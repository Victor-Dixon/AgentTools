"""Bilateral SENT proof — DISPATCH success is not partner visibility.

Captain session 2026-08-24 M1: never claim SENT from bus/GUI DISPATCH alone.
SENT requires an inbox file plus a trusted verification mode or partner REPLY.
clipboard_proxy and NONCE_VERIFY_FAILED are fail.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

SENT_OK_MODES = frozenset({"uia", "injected_verify_fn"})
NOT_SENT_MODES = frozenset({"clipboard_proxy", "nonce_verify_failed", "dispatch_only"})

STATUS_SENT = "SENT"
STATUS_DISPATCH_UNCONFIRMED = "DISPATCH_UNCONFIRMED"
STATUS_NOT_SENT = "NOT_SENT"


def extract_verification_mode(detail: str | None) -> str:
    """Parse transport detail into a verification mode token."""
    text = (detail or "").strip().lower()
    if not text:
        return "dispatch_only"
    if "clipboard_proxy" in text:
        return "clipboard_proxy"
    if "nonce_verify_failed" in text:
        return "nonce_verify_failed"
    if "injected_verify_fn" in text:
        return "injected_verify_fn"
    if "verification_mode=uia" in text or "verify=uia" in text or " uia" in f" {text}":
        return "uia"
    return "dispatch_only"


def classify_bilateral_sent(
    *,
    dispatch_success: bool = False,
    verification_mode: str | None = None,
    inbox_path: str | Path | None = None,
    partner_reply: bool = False,
) -> dict[str, Any]:
    """Return SENT only when inbox exists and verify mode is trusted (or partner replied)."""
    mode = (verification_mode or "dispatch_only").strip().lower() or "dispatch_only"
    inbox_file = Path(inbox_path) if inbox_path else None
    inbox_exists = bool(inbox_file and inbox_file.is_file())

    if mode in {"clipboard_proxy", "nonce_verify_failed"}:
        return {
            "status": STATUS_NOT_SENT,
            "reason": f"verification_mode={mode}",
            "dispatch_success": dispatch_success,
            "inbox_exists": inbox_exists,
            "verification_mode": mode,
            "partner_reply": partner_reply,
        }

    trusted = mode in SENT_OK_MODES or partner_reply
    if dispatch_success and inbox_exists and trusted:
        return {
            "status": STATUS_SENT,
            "reason": "inbox_and_trusted_verify",
            "dispatch_success": True,
            "inbox_exists": True,
            "verification_mode": mode,
            "partner_reply": partner_reply,
        }

    if dispatch_success:
        return {
            "status": STATUS_DISPATCH_UNCONFIRMED,
            "reason": "dispatch_success_without_inbox_or_trusted_verify",
            "dispatch_success": True,
            "inbox_exists": inbox_exists,
            "verification_mode": mode,
            "partner_reply": partner_reply,
        }

    return {
        "status": STATUS_NOT_SENT,
        "reason": "no_dispatch",
        "dispatch_success": False,
        "inbox_exists": inbox_exists,
        "verification_mode": mode,
        "partner_reply": partner_reply,
    }


def is_bilateral_sent(proof: dict[str, Any]) -> bool:
    return str(proof.get("status") or "") == STATUS_SENT
