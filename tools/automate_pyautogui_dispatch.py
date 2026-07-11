#!/usr/bin/env python3
"""Automate PyAutoGUI dispatch through the Agent Cellphone "main system".

This script automates the governed workstation controls exposed by the inbox
and messaging helpers:

- Cursor focus via Agent Cellphone coordinates (`runtime/DREAMVAULT_TIGHT/coords.json`)
- Optional outbox preface via `tools/messaging_outbox_helper.py prepare_outbox`
- Clipboard write + paste + Enter via PyAutoGUI

It does not replace production bus/agent modes — it drives the current
message bus and legacy inbox transport mechanics.

Examples:
    python tools/automate_pyautogui_dispatch.py \
      --repo D:/DreamVault \
      --target Agent-4 \
      --message "[A2A] Captain handoff ping" \
      --dry-run

    python tools/automate_pyautogui_dispatch.py \
      --repo D:/DreamVault \
      --plan-file data/handoff_plan.json \
      --live

    python tools/automate_pyautogui_dispatch.py \
      --repo D:/DreamVault \
      --targets Agent-2,Agent-3 \
      --message "Resume overnight recovery lane" \
      --live
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import pyautogui
import pyperclip


DEFAULT_COORDS = Path(r"D:\DreamVault\runtime\DREAMVAULT_TIGHT\coords.json")
DEFAULT_AGENT_PROFILE = Path.home() / ".config" / "cursor" / "agents.local.json"


@dataclass
class DispatchTarget:
    agent_id: str
    kind: str = "input_box"
    click_position: tuple[int, int] | None = None


@dataclass
class DispatchStep:
    target: DispatchTarget
    message: str
    pause_before_paste: float = 0.3
    pause_after_paste: float = 0.5
    outbox_step: str | None = None


@dataclass
class DispatchReport:
    repo: str
    live: bool
    results: list[dict[str, Any]] = field(default_factory=list)

    def append(self, **row: Any) -> None:
        self.results.append(row)


def _ensure_utf8() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def _parse_agent_id(value: str) -> str:
    value = str(value or "").strip()
    if not value:
        raise ValueError("empty agent id")
    if value.lower().startswith("agent-"):
        return f"Agent-{value.split('-', 1)[1]}"
    if value.lower().startswith("agent"):
        return f"Agent-{value[5:]}"
    return f"Agent-{value}"


def _resolve_repo(args: argparse.Namespace) -> Path:
    raw = (
        args.repo
        or os.environ.get("DREAMVAULT_ROOT")
        or os.environ.get("REPO_ROOT")
        or Path.cwd()
    )
    return Path(raw).resolve()


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(str(path))
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    return data if isinstance(data, dict) else {}


def _coords_candidate_paths(repo: Path, explicit: Path | None) -> list[Path]:
    candidates: list[Path] = []
    if explicit is not None:
        candidates.append(explicit.expanduser().resolve())
    candidates.extend(
        [
            repo / "runtime" / "DREAMVAULT_TIGHT" / "coords.json",
            repo / "agent_workspaces" / "coord_map.json",
            DEFAULT_COORDS,
            Path(r"D:\agent-tools") / "runtime" / "DREAMVAULT_TIGHT" / "coords.json",
        ]
    )
    deduped: list[Path] = []
    seen: set[str] = set()
    for path in candidates:
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(path)
    return deduped


def _candidate_coord_keys(agent_id: str, kind: str) -> list[str]:
    n = agent_id.replace("Agent-", "")
    keys = [
        f"agent_{n}_{kind}",
        f"agent{n}_{kind}",
        f"{agent_id}_{kind}",
    ]
    if kind == "input_box":
        keys.extend([f"agent_{n}_input", f"agent{n}_input", f"{agent_id}_input"])
    return keys


def _resolve_target(
    *,
    repo: Path,
    coords_path: Path | None,
    target: DispatchTarget,
) -> tuple[DispatchTarget, Path]:
    if target.click_position is not None:
        return target, Path("explicit")

    for candidate_path in _coords_candidate_paths(repo, coords_path):
        if not candidate_path.is_file():
            continue
        data = _load_json(candidate_path)
        agents = data.get("agents")
        if not isinstance(agents, dict):
            continue
        agent_entry = agents.get(target.agent_id)
        if not isinstance(agent_entry, dict):
            raise KeyError(f"Agent {target.agent_id!r} not found in {candidate_path}")
        for key in _candidate_coord_keys(target.agent_id, target.kind):
            value = agent_entry.get(key)
            if isinstance(value, (list, tuple)) and len(value) >= 2:
                x, y = int(value[0]), int(value[1])
                return (
                    DispatchTarget(
                        agent_id=target.agent_id,
                        kind=target.kind,
                        click_position=(x, y),
                    ),
                    candidate_path,
                )
        raise KeyError(
            f"No coordinate key for {target.agent_id} kind={target.kind} in {candidate_path}"
        )

    searched = ", ".join(str(path) for path in _coords_candidate_paths(repo, coords_path))
    raise FileNotFoundError(f"coords file not found; searched: {searched}")


def _profile_matches_target(target: DispatchTarget, profile: dict[str, Any]) -> bool:
    name = str(profile.get("name") or "")
    if name == target.agent_id:
        return True
    n = target.agent_id.replace("Agent-", "")
    return name in {f"Agent-{n}", f"Agent-{n} Workspace", target.agent_id}


def _resolve_devtools_click(
    *,
    devtools_profiles: Path,
    target: DispatchTarget,
) -> tuple[int, int] | None:
    if not devtools_profiles.is_file():
        return None

    data = _load_json(devtools_profiles)
    profiles = data.get("profiles")
    if not isinstance(profiles, list):
        return None

    for profile in profiles:
        if not isinstance(profile, dict):
            continue
        if not _profile_matches_target(target, profile):
            continue
        position = profile.get("position")
        size = profile.get("size")
        if not (
            isinstance(position, (list, tuple))
            and len(position) >= 2
            and isinstance(size, (list, tuple))
            and len(size) >= 2
        ):
            continue
        x = int(position[0]) + max(16, int(size[0]) // 2)
        y = int(position[1]) + max(12, min(48, int(size[1]) // 6))
        return (x, y)
    return None


def _focus_target(
    *,
    target: DispatchTarget,
    hover_before_click: float,
    devtools_profiles: Path,
) -> tuple[int, int]:
    if target.click_position is None:
        raise ValueError(f"target {target.agent_id} has no click_position")

    coord_x, coord_y = target.click_position
    x, y = coord_x, coord_y

    devtools = _resolve_devtools_click(devtools_profiles=devtools_profiles, target=target)
    if devtools is not None and target.kind == "input_box":
        x, y = devtools

    pyautogui.moveTo(x, y, duration=max(0.0, hover_before_click))
    pyautogui.click(x, y)
    return (x, y)


def _run_outbox_helper(repo: Path, sender: str, step: str) -> dict[str, Any]:
    helper = repo / "tools" / "messaging_outbox_helper.py"
    if not helper.is_file():
        raise FileNotFoundError(str(helper))

    cmd = [
        sys.executable,
        str(helper),
        "prepare_outbox",
        "--agent",
        sender,
        "--step",
        step,
    ]
    proc = subprocess.run(
        cmd,
        cwd=str(repo),
        capture_output=True,
        text=True,
        check=False,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip()
        raise RuntimeError(f"prepare_outbox failed ({proc.returncode}): {detail}")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"prepare_outbox returned non-JSON output: {proc.stdout[:300]}") from exc


def _dispatch_packet(
    *,
    repo: Path,
    coords_path: Path | None,
    step: DispatchStep,
    dry_run: bool,
    hover_before_click: float,
    devtools_profiles: Path,
) -> dict[str, Any]:
    resolved, resolved_coords_path = _resolve_target(
        repo=repo,
        coords_path=coords_path,
        target=step.target,
    )
    row: dict[str, Any] = {
        "agent": resolved.agent_id,
        "kind": resolved.kind,
        "coords": list(resolved.click_position or []),
        "coords_path": str(resolved_coords_path),
        "message_chars": len(step.message),
        "dry_run": dry_run,
    }

    if dry_run:
        row["status"] = "DRY_RUN"
        row["would_paste"] = step.message[:180]
        return row

    clicked = _focus_target(
        target=resolved,
        hover_before_click=hover_before_click,
        devtools_profiles=devtools_profiles,
    )
    row["clicked"] = list(clicked)

    if step.outbox_step:
        row["outbox"] = _run_outbox_helper(repo, resolved.agent_id, step.outbox_step)

    time.sleep(max(0.0, step.pause_before_paste))
    pyperclip.copy(step.message)
    time.sleep(0.15)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(max(0.0, step.pause_after_paste))
    pyautogui.press("enter")

    row["status"] = "SENT"
    row["message_preview"] = step.message[:180]
    return row


def _parse_plan(path: Path) -> list[DispatchStep]:
    data = _load_json(path)
    steps_raw = data.get("steps")
    if not isinstance(steps_raw, list) or not steps_raw:
        raise ValueError(f"plan file has no steps: {path}")

    out: list[DispatchStep] = []
    for item in steps_raw:
        if not isinstance(item, dict):
            continue
        agent = _parse_agent_id(str(item.get("agent") or item.get("target") or ""))
        message = str(item.get("message") or item.get("body") or "").strip()
        if not message:
            raise ValueError(f"plan step for {agent} missing message")
        coords = item.get("coords")
        click_position = None
        if isinstance(coords, (list, tuple)) and len(coords) >= 2:
            click_position = (int(coords[0]), int(coords[1]))
        target = DispatchTarget(
            agent_id=agent,
            kind=str(item.get("kind") or "input_box"),
            click_position=click_position,
        )
        out.append(
            DispatchStep(
                target=target,
                message=message,
                pause_before_paste=float(item.get("pause_before_paste", 0.3)),
                pause_after_paste=float(item.get("pause_after_paste", 0.5)),
                outbox_step=(str(item["outbox_step"]) if item.get("outbox_step") else None),
            )
        )
    if not out:
        raise ValueError(f"plan file had no valid steps: {path}")
    return out


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=None, help="DreamVault / messaging repo root")
    parser.add_argument("--coords", type=Path, default=None, help="Coordinate map JSON")
    parser.add_argument("--targets", default="", help="Comma-separated agent ids")
    parser.add_argument("--target", default="", help="Single agent id")
    parser.add_argument("--message", default="", help="Packet body to paste/send")
    parser.add_argument("--plan-file", type=Path, default=None, help="JSON plan with steps[]")
    parser.add_argument("--outbox-step", default=None, help="Optional prepare_outbox step name")
    parser.add_argument(
        "--kind",
        default="input_box",
        help="Coordinate kind from coords.json (default: input_box)",
    )
    parser.add_argument("--pause-before-paste", type=float, default=0.3)
    parser.add_argument("--pause-after-paste", type=float, default=0.5)
    parser.add_argument("--hover-before-click", type=float, default=0.08)
    parser.add_argument(
        "--devtools-profiles",
        type=Path,
        default=DEFAULT_AGENT_PROFILE,
        help="Cursor agents.local.json for devtools click center",
    )
    parser.add_argument("--dry-run", action="store_true", help="Resolve coords only")
    parser.add_argument("--live", action="store_true", help="Click, paste, and Enter")
    parser.add_argument("--failsafe", action="store_true", help="Enable PyAutoGUI FAILSAFE")
    parser.add_argument("--report-json", type=Path, default=None, help="Write dispatch report JSON")
    return parser.parse_args()


def _build_steps(args: argparse.Namespace) -> list[DispatchStep]:
    if args.plan_file:
        return _parse_plan(args.plan_file.resolve())

    message = str(args.message or "").strip()
    if not message:
        raise ValueError("--message is required when --plan-file is not used")

    raw_targets: list[str] = []
    if args.target:
        raw_targets.append(args.target)
    if args.targets:
        raw_targets.extend(part.strip() for part in str(args.targets).split(",") if part.strip())
    if not raw_targets:
        raise ValueError("provide --target or --targets or --plan-file")

    return [
        DispatchStep(
            target=DispatchTarget(agent_id=_parse_agent_id(target), kind=args.kind),
            message=message,
            pause_before_paste=float(args.pause_before_paste),
            pause_after_paste=float(args.pause_after_paste),
            outbox_step=(str(args.outbox_step) if args.outbox_step else None),
        )
        for target in raw_targets
    ]


def main() -> int:
    _ensure_utf8()
    args = _parse_args()
    repo = _resolve_repo(args)
    dry_run = bool(args.dry_run or not args.live)

    pyautogui.FAILSAFE = bool(args.failsafe)
    pyautogui.PAUSE = 0.05

    report = DispatchReport(repo=str(repo), live=not dry_run)

    try:
        steps = _build_steps(args)
    except Exception as exc:
        print(f"DISPATCH_PREPARE=FAIL reason={exc}")
        return 1

    for index, step in enumerate(steps, start=1):
        try:
            row = _dispatch_packet(
                repo=repo,
                coords_path=args.coords,
                step=step,
                dry_run=dry_run,
                hover_before_click=float(args.hover_before_click),
                devtools_profiles=args.devtools_profiles.expanduser().resolve(),
            )
            row["index"] = index
            report.append(**row)
            print(
                f"[{index}/{len(steps)}] {row.get('agent', step.target.agent_id)}: "
                f"{row.get('status', 'UNKNOWN')} coords={row.get('coords')}"
            )
        except Exception as exc:
            report.append(index=index, agent=step.target.agent_id, status="FAIL", error=str(exc))
            print(f"[{index}/{len(steps)}] {step.target.agent_id}: FAIL {exc}", file=sys.stderr)
            if args.report_json:
                args.report_json.parent.mkdir(parents=True, exist_ok=True)
                args.report_json.write_text(
                    json.dumps(asdict(report), indent=2) + "\n",
                    encoding="utf-8",
                )
            return 1

    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(json.dumps(asdict(report), indent=2) + "\n", encoding="utf-8")
        print(f"report_json={args.report_json}")

    mode = "DRY_RUN" if dry_run else "LIVE"
    print(f"DISPATCH_COMPLETE mode={mode} sent={len(steps)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
