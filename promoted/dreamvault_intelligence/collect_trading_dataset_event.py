#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

DATASET_DIR = Path("runtime/trading/datasets")
EVENTS = DATASET_DIR / "events.jsonl"
FEATURES = DATASET_DIR / "features.jsonl"

REGIME = Path("data/reports/trading/market_regime_daily_context.json")
TSLA_STATS = Path("data/reports/trading/tsla_momentum_curl_daily_stats.json")
DAY_PLAN = Path("data/reports/trading/intraday_trading_day_plan.json")
ACCOUNT_PLAN = Path("data/reports/trading/account_aware_day_plan.json")
RISK_PROFILE = Path("data/reports/trading/account_risk_profile.json")
PAPER_REPORT = Path("data/reports/trading/paper_trade_simulation_report.json")
POSITION_DECISIONS = Path("data/reports/trading/position_decisions.json")
TSLA_CSV = Path("runtime/trading/data/real/tsla_intraday_latest.csv")
OUT_MD = Path("data/reports/trading/trading_dataset_event_report.md")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def count_csv_rows(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        with path.open(newline="", encoding="utf-8") as f:
            return max(0, sum(1 for _ in csv.DictReader(f)))
    except Exception:
        return 0


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def main() -> int:
    event_id = str(uuid4())

    regime = load_json(REGIME)
    tsla = load_json(TSLA_STATS)
    day_plan = load_json(DAY_PLAN)
    account_plan = load_json(ACCOUNT_PLAN)
    risk_profile = load_json(RISK_PROFILE)
    paper = load_json(PAPER_REPORT)
    position_decisions = load_json(POSITION_DECISIONS)

    market_context = account_plan.get("market_context") or day_plan.get("market_context") or {}
    execution_plan = account_plan.get("execution_plan") or {}
    paper_decision = paper.get("decision") or {}

    event = {
        "event_id": event_id,
        "generated_at": now(),
        "event_type": "trading_loop_snapshot",
        "symbol": "TSLA",
        "paper_only": True,
        "real_execution_enabled": False,
    }

    features = {
        "event_id": event_id,
        "generated_at": event["generated_at"],
        "symbol": "TSLA",
        "candles_available": count_csv_rows(TSLA_CSV),
        "day_type": market_context.get("day_type") or regime.get("day_type"),
        "market_regime": market_context.get("market_regime") or regime.get("market_regime"),
        "risk_score": market_context.get("risk_score") or regime.get("risk_score"),
        "bias": market_context.get("bias"),
        "trade_permission": execution_plan.get("trade_permission"),
        "max_new_position_pct": execution_plan.get("max_new_position_pct"),
        "max_risk_dollars": paper_decision.get("max_risk_dollars")
            or risk_profile.get("derived_limits", {}).get("max_risk_per_trade_dollars"),
        "signal_count": len(tsla.get("signals") or []),
        "paper_action": paper_decision.get("action"),
        "decision_class": paper_decision.get("decision_class"),
        "decision_reason": paper_decision.get("reason"),
        "position_decisions_count": position_decisions.get("positions", 0),
        "risk_profile_mode": risk_profile.get("mode"),
        "account_size_used": risk_profile.get("account_size"),
    }

    append_jsonl(EVENTS, event)
    append_jsonl(FEATURES, features)

    OUT_MD.write_text(
        "\n".join([
            "# Trading Dataset Event Report",
            "",
            f"- Generated: {event['generated_at']}",
            f"- Event ID: {event_id}",
            f"- Symbol: TSLA",
            f"- Candles: {features['candles_available']}",
            f"- Day Type: {features['day_type']}",
            f"- Market Regime: {features['market_regime']}",
            f"- Risk Score: {features['risk_score']}",
            f"- Paper Action: {features['paper_action']}",
            f"- Decision Class: {features['decision_class']}",
            f"- Max Risk Dollars: {features['max_risk_dollars']}",
            "",
        ]),
        encoding="utf-8",
    )

    print(f"EVENTS={EVENTS}")
    print(f"FEATURES={FEATURES}")
    print(f"REPORT={OUT_MD}")
    print("TRADING_DATASET_EVENT_COLLECTOR=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
