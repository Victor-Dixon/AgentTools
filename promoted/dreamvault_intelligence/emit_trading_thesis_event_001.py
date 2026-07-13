#!/usr/bin/env python3
"""
@file Emit structured trading thesis cognition packet.
@summary Convert trading conversations into runtime artifacts.
@registry runtime/tasks/trading_thesis_event_pipeline_001.yaml
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path.cwd()

event_dir = ROOT / "runtime/events/trading"
report_dir = ROOT / "data/reports/trading"

event_dir.mkdir(parents=True, exist_ok=True)
report_dir.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now(UTC).isoformat()

packet = {
    "event_type": "trading_thesis",
    "symbol": "TSLA",
    "timestamp": timestamp,
    "position": "TSLA 480C 2026-05-29",
    "bias": "cautiously_bullish",
    "thesis": {
        "core": (
            "Trade depends more on perceived upside expansion "
            "than literal strike touch."
        ),
        "trigger_levels": [
            "420 hold",
            "426 reclaim",
            "4h MACD expansion",
        ],
        "invalidation": [
            "Repeated 420 rejection",
            "Loss of VWAP",
            "Momentum stall",
        ],
    },
    "operator_notes": [
        "Theta becomes primary risk next week.",
        "Need expectation expansion not necessarily strike hit.",
    ],
    "confidence": {
        "short_term": "medium",
        "theta_risk": "elevated",
    },
}

json_path = event_dir / "latest_tsla_thesis.json"

with open(json_path, "w", encoding="utf-8") as handle:
    json.dump(packet, handle, indent=2)

markdown = f"""# TSLA Trading Thesis

## Position
TSLA 480C 2026-05-29

## Bias
Cautiously bullish

## Core Thesis
Trade depends more on perceived upside expansion
than literal strike touch.

## Trigger Levels
- 420 hold
- 426 reclaim
- 4h MACD expansion

## Invalidation
- Repeated 420 rejection
- Loss of VWAP
- Momentum stall

## Operator Notes
- Theta becomes primary risk next week.
- Need expectation expansion not necessarily strike hit.

## Confidence
- Short-term: medium
- Theta risk: elevated
"""

md_path = report_dir / "latest_tsla_thesis.md"

with open(md_path, "w", encoding="utf-8") as handle:
    handle.write(markdown)

discord_payload = {
    "channel": "trading-thesis",
    "title": "TSLA Thesis Update",
    "body": (
        "Bias: cautiously bullish | "
        "Key level: 420 | "
        "Need expectation expansion."
    ),
}

discord_path = event_dir / "latest_tsla_discord_payload.json"

with open(discord_path, "w", encoding="utf-8") as handle:
    json.dump(discord_payload, handle, indent=2)

print("TRADING_THESIS_EVENT=PASS")
print(f"JSON={json_path}")
print(f"MARKDOWN={md_path}")
print(f"DISCORD={discord_path}")
