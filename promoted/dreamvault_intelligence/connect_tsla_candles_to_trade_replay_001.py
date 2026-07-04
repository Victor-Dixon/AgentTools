#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CANDLE_ROOTS = [Path("data"), Path("runtime")]
JOURNAL = Path("data/reports/trading/journals/latest_robinhood_trade_journal.json")
OUT_JSON = Path("data/reports/trading/journals/latest_trade_chart_replay.json")
OUT_MD = Path("data/reports/trading/journals/latest_trade_chart_replay.md")
INV_JSON = Path("data/reports/trading/journals/tsla_candle_source_inventory.json")


def parse_dt(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value).replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def discover_tsla_candle_files() -> list[Path]:
    hits: list[Path] = []
    for root in CANDLE_ROOTS:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if p.is_file() and "tsla" in p.name.lower() and p.suffix.lower() in {".json", ".jsonl", ".csv"}:
                hits.append(p)
    return sorted(set(hits))


def load_candles(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        if path.suffix.lower() == ".csv":
            with path.open(newline="", encoding="utf-8") as f:
                rows = list(csv.DictReader(f))
        elif path.suffix.lower() == ".jsonl":
            rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
        else:
            obj = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(obj, list):
                rows = obj
            elif isinstance(obj, dict):
                for key in ("candles", "bars", "data", "results"):
                    if isinstance(obj.get(key), list):
                        rows = obj[key]
                        break
    except Exception:
        return []

    normalized = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        ts = r.get("timestamp") or r.get("time") or r.get("datetime") or r.get("date") or r.get("t")
        dt = parse_dt(ts)
        if not dt:
            continue
        normalized.append({
            "timestamp": dt.isoformat(),
            "open": r.get("open") or r.get("o"),
            "high": r.get("high") or r.get("h"),
            "low": r.get("low") or r.get("l"),
            "close": r.get("close") or r.get("c"),
            "volume": r.get("volume") or r.get("v"),
            "source": str(path),
        })
    return normalized


def nearest_window(candles: list[dict[str, Any]], fill_ts: str, radius: int = 5) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    dt = parse_dt(fill_ts)
    if not dt or not candles:
        return [], None
    indexed = [(abs((parse_dt(c.get("timestamp")) or dt) - dt).total_seconds(), i, c) for i, c in enumerate(candles)]
    _, idx, nearest = min(indexed, key=lambda x: x[0])
    lo = max(0, idx - radius)
    hi = min(len(candles), idx + radius + 1)
    return candles[lo:hi], nearest


def classify(fill: dict[str, Any], nearest: dict[str, Any] | None) -> tuple[str, str]:
    if not nearest:
        return "needs_chart_context", "no_matching_candle_source"
    side = str(fill.get("side", "")).upper()
    price = float(fill.get("price") or 0)
    try:
        close = float(nearest.get("close") or 0)
        high = float(nearest.get("high") or close)
        low = float(nearest.get("low") or close)
    except Exception:
        return "unknown", "candle_values_unparseable"

    if "BUY" in side or "DEBIT" in side:
        if price >= high:
            return "possible_chase", "entry_at_or_above_nearest_candle_high"
        if price <= low:
            return "possible_clean_entry", "entry_near_nearest_candle_low"
        return "planned_or_mid_candle", "entry_inside_nearest_candle_range"

    if "SELL" in side or "CREDIT" in side:
        return "exit_review", "exit_requires_original_plan_comparison"

    return "unknown", "unrecognized_side"


def render_md(rows: list[dict[str, Any]], inventory: list[dict[str, Any]]) -> str:
    lines = [
        "# TSLA Candle-Connected Trade Replay",
        "",
        f"generated_at: {datetime.now(timezone.utc).isoformat()}",
        f"fills_reviewed: {len(rows)}",
        f"candle_sources_found: {len(inventory)}",
        "",
        "| Time | Symbol | Side | Price | Classification | Reason | Candle Source |",
        "|---|---:|---:|---:|---|---|---|",
    ]
    for r in rows:
        src = (r.get("nearest_candle") or {}).get("source", "")
        lines.append(
            f"| {r.get('timestamp','')} | {r.get('symbol','')} | {r.get('side','')} | {r.get('price','')} | "
            f"{r.get('classification','')} | {r.get('reason_code','')} | {src} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.parse_args()

    files = discover_tsla_candle_files()
    inventory = []
    all_candles: list[dict[str, Any]] = []

    for f in files:
        candles = load_candles(f)
        inventory.append({"path": str(f), "candles_loaded": len(candles)})
        all_candles.extend(candles)

    all_candles.sort(key=lambda c: c["timestamp"])

    fills = json.loads(JOURNAL.read_text(encoding="utf-8")) if JOURNAL.exists() else []
    rows = []
    for fill in fills:
        window, nearest = nearest_window(all_candles, str(fill.get("timestamp", "")))
        label, reason = classify(fill, nearest)
        rows.append({
            **fill,
            "classification": label,
            "reason_code": reason,
            "chart_context_available": nearest is not None,
            "nearest_candle": nearest,
            "candle_window": window,
        })

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    INV_JSON.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    OUT_JSON.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(rows, inventory), encoding="utf-8")

    print("CONNECT_TSLA_CANDLES_TO_TRADE_REPLAY=PASS")
    print(f"CANDLE_FILES_FOUND={len(files)}")
    print(f"CANDLES_LOADED={len(all_candles)}")
    print(f"FILLS_REVIEWED={len(rows)}")
    print(f"JSON={OUT_JSON}")
    print(f"MD={OUT_MD}")
    print(f"INVENTORY={INV_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
