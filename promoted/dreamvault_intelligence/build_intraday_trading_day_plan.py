#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REGIME_JSON = Path("data/reports/trading/market_regime_daily_context.json")
TSLA_JSON = Path("data/reports/trading/tsla_momentum_curl_daily_stats.json")
OUT_JSON = Path("data/reports/trading/intraday_trading_day_plan.json")
OUT_MD = Path("data/reports/trading/intraday_trading_day_plan.md")


DAY_PLAYBOOKS = {
    "trend_down_risk_off": {
        "bias": "bearish",
        "sizing": "normal_to_reduced",
        "preferred_setups": [
            "TSLA failed VWAP reclaim into bearish continuation",
            "MACD bearish curl after lower high",
            "Put continuation after weak bounce rejection",
        ],
        "avoid": [
            "late chase after extended downside candle",
            "puts directly into prior low without consolidation",
            "calls unless broad regime flips",
        ],
        "confirmation": [
            "SPY/QQQ remain below VWAP",
            "TSLA rejects EMA9 or VWAP",
            "MACD histogram weakens after bounce",
        ],
        "invalidation": [
            "SPY and QQQ reclaim VWAP together",
            "TSLA forms higher low above VWAP",
            "risk score improves to neutral or positive",
        ],
    },
    "volatility_expansion": {
        "bias": "directional_but_fast",
        "sizing": "reduced",
        "preferred_setups": [
            "wait for pullback then continuation",
            "trade with regime direction only",
            "use smaller size because candles are expanded",
        ],
        "avoid": [
            "entering after 2-3 large same-direction candles",
            "oversized dailies",
            "holding through violent reclaim against position",
        ],
        "confirmation": [
            "market direction remains aligned",
            "TSLA confirms structure break or failed reclaim",
            "volume supports move",
        ],
        "invalidation": [
            "range collapses into chop",
            "SPY/QQQ diverge sharply",
            "TSLA reclaims VWAP and holds",
        ],
    },
    "trend_up_risk_on": {
        "bias": "bullish",
        "sizing": "normal_to_reduced",
        "preferred_setups": [
            "TSLA VWAP reclaim and hold",
            "MACD bullish curl after higher low",
            "call continuation after shallow pullback",
        ],
        "avoid": [
            "countertrend puts without failed reclaim",
            "shorting strong tech-led breadth",
            "chasing calls into upper extension",
        ],
        "confirmation": [
            "SPY/QQQ remain above VWAP",
            "TSLA holds EMA9/VWAP",
            "NQ confirms risk-on behavior",
        ],
        "invalidation": [
            "SPY and QQQ lose VWAP together",
            "TSLA breaks prior higher low",
            "risk score flips negative",
        ],
    },
    "mixed_chop": {
        "bias": "neutral",
        "sizing": "small_or_no_trade",
        "preferred_setups": [
            "only high-quality failed reclaim/rejection trades",
            "mean reversion near clear range edges",
            "wait for range break before momentum entries",
        ],
        "avoid": [
            "anticipation entries",
            "midrange trades",
            "oversized dailies",
        ],
        "confirmation": [
            "clear reclaim or rejection",
            "defined range edge",
            "market confirms same direction for multiple candles",
        ],
        "invalidation": [
            "price returns to range middle",
            "SPY/QQQ disagree",
            "signals alternate rapidly",
        ],
    },
    "range_day": {
        "bias": "mean_reversion",
        "sizing": "small",
        "preferred_setups": [
            "fade range extremes only",
            "avoid momentum unless range breaks",
            "take profits faster",
        ],
        "avoid": [
            "breakout chasing before confirmation",
            "holding dailies too long",
            "entries near range middle",
        ],
        "confirmation": [
            "range high/low respected",
            "VWAP acts as magnet",
            "no broad risk expansion",
        ],
        "invalidation": [
            "range expansion above/below day boundary",
            "risk score expands strongly",
            "volume confirms breakout",
        ],
    },
    "gap_and_go": {
        "bias": "with_gap_direction",
        "sizing": "reduced_until_pullback",
        "preferred_setups": [
            "first pullback continuation",
            "VWAP hold in gap direction",
            "MACD curl with trend",
        ],
        "avoid": [
            "fading gap without failed continuation",
            "late chase after extended move",
            "countertrend dailies",
        ],
        "confirmation": [
            "gap direction holds VWAP",
            "market breadth confirms",
            "pullbacks are shallow",
        ],
        "invalidation": [
            "VWAP loss against gap",
            "gap fill accelerates",
            "SPY/QQQ reverse together",
        ],
    },
    "gap_fade": {
        "bias": "fade_opening_move",
        "sizing": "small_to_normal_after_confirmation",
        "preferred_setups": [
            "failed opening direction continuation",
            "VWAP rejection after gap fade starts",
            "trade toward prior balance/range",
        ],
        "avoid": [
            "assuming gap fade before confirmation",
            "holding after full gap fill",
            "entering during first candle noise",
        ],
        "confirmation": [
            "opening direction fails",
            "VWAP flips against gap",
            "SPY/QQQ confirm reversal",
        ],
        "invalidation": [
            "gap direction reclaims and holds",
            "new high/low in gap direction",
            "risk score expands with original gap",
        ],
    },
    "rotation_day": {
        "bias": "selective",
        "sizing": "small",
        "preferred_setups": [
            "trade strongest/weakest asset only",
            "avoid assuming SPY confirms QQQ",
            "TSLA only if it follows QQQ/NQ cleanly",
        ],
        "avoid": [
            "broad-market assumptions",
            "oversized index-correlated trades",
            "forcing TSLA if it decouples",
        ],
        "confirmation": [
            "TSLA aligns with QQQ/NQ",
            "relative strength/weakness is clear",
            "SPY/QQQ divergence is stable",
        ],
        "invalidation": [
            "rotation resolves into broad trend",
            "TSLA loses relative signal",
            "SPY/QQQ correlation snaps back suddenly",
        ],
    },
    "tech_led_risk_off": {
        "bias": "bearish_tech",
        "sizing": "normal_to_reduced",
        "preferred_setups": [
            "TSLA puts after QQQ/NQ weakness confirms",
            "failed VWAP reclaim",
            "lower-high continuation",
        ],
        "avoid": [
            "calls on TSLA without QQQ reclaim",
            "shorting defensive strength as proxy",
            "late puts after large downside extension",
        ],
        "confirmation": [
            "QQQ and NQ remain weak",
            "TSLA underperforms SPY",
            "MACD curl aligns bearish",
        ],
        "invalidation": [
            "QQQ/NQ reclaim VWAP",
            "TSLA shows relative strength",
            "risk score improves",
        ],
    },
    "tech_led_risk_on": {
        "bias": "bullish_tech",
        "sizing": "normal_to_reduced",
        "preferred_setups": [
            "TSLA calls after QQQ/NQ strength confirms",
            "VWAP reclaim and hold",
            "higher-low continuation",
        ],
        "avoid": [
            "puts without failed reclaim",
            "shorting tech leadership",
            "late chase into extended candle",
        ],
        "confirmation": [
            "QQQ and NQ remain strong",
            "TSLA holds above VWAP",
            "MACD bullish curl confirms",
        ],
        "invalidation": [
            "QQQ/NQ lose VWAP",
            "TSLA fails reclaim",
            "risk score flips negative",
        ],
    },
}


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def pick_playbook(day_type: str, market_regime: str) -> tuple[str, dict]:
    if day_type in DAY_PLAYBOOKS:
        return day_type, DAY_PLAYBOOKS[day_type]
    if market_regime in {"broad_risk_off", "mild_risk_off"}:
        return "trend_down_risk_off", DAY_PLAYBOOKS["trend_down_risk_off"]
    if market_regime in {"broad_risk_on", "mild_risk_on"}:
        return "trend_up_risk_on", DAY_PLAYBOOKS["trend_up_risk_on"]
    return "mixed_chop", DAY_PLAYBOOKS["mixed_chop"]


def build_plan() -> dict:
    regime = load_json(REGIME_JSON)
    tsla = load_json(TSLA_JSON)

    agg = regime.get("aggregate", {})
    day_type = agg.get("day_type", "unknown")
    market_regime = agg.get("market_regime", "unknown")
    risk_score = agg.get("risk_score", 0)
    phase = agg.get("phase", "intraday")
    confidence = agg.get("confidence", "low")

    playbook_key, playbook = pick_playbook(day_type, market_regime)

    signal_count = tsla.get("signal_count", 0)
    tsla_status = tsla.get("data_status", "ok")
    candles = tsla.get("candles", 0)

    posture = playbook["sizing"]
    if phase == "intraday" and confidence != "high":
        posture = f"{posture}_until_confirmation"
    if tsla_status in {"missing_or_insufficient_data", "partial_intraday"}:
        posture = f"{posture}_partial_data"

    trade_permission = "allowed_selectively"
    if playbook_key in {"mixed_chop", "range_day", "rotation_day"}:
        trade_permission = "restricted"
    if tsla_status == "missing_or_insufficient_data":
        trade_permission = "observe_only"

    plan = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase": phase,
        "day_type": day_type,
        "market_regime": market_regime,
        "risk_score": risk_score,
        "confidence": confidence,
        "selected_playbook": playbook_key,
        "bias": playbook["bias"],
        "sizing_posture": posture,
        "trade_permission": trade_permission,
        "preferred_setups": playbook["preferred_setups"],
        "avoid": playbook["avoid"],
        "confirmation_required": playbook["confirmation"],
        "invalidation_triggers": playbook["invalidation"],
        "tsla_strategy": {
            "candles": candles,
            "data_status": tsla_status,
            "signal_count": signal_count,
            "put_signals": tsla.get("put_signals", 0),
            "call_signals": tsla.get("call_signals", 0),
            "last_close": tsla.get("last_close"),
        },
        "operator_rules": [
            "No trade before setup confirmation.",
            "No oversized dailies during partial-data or volatility-expansion conditions.",
            "If invalidation triggers fire, stop and rebuild plan.",
            "Journal screenshot, entry reason, exit reason, MAE, MFE, and emotion state.",
        ],
    }
    return plan


def write_plan(plan: dict) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(plan, indent=2), encoding="utf-8")

    lines = [
        "# Intraday Trading Day Plan",
        "",
        f"- Generated: {plan['generated_at']}",
        f"- Phase: {plan['phase']}",
        f"- Day Type: {plan['day_type']}",
        f"- Market Regime: {plan['market_regime']}",
        f"- Risk Score: {plan['risk_score']}",
        f"- Confidence: {plan['confidence']}",
        f"- Selected Playbook: {plan['selected_playbook']}",
        f"- Bias: {plan['bias']}",
        f"- Sizing: {plan['sizing_posture']}",
        f"- Trade Permission: {plan['trade_permission']}",
        "",
        "## Preferred Setups",
        "",
    ]
    lines += [f"- {x}" for x in plan["preferred_setups"]]
    lines += ["", "## Avoid", ""]
    lines += [f"- {x}" for x in plan["avoid"]]
    lines += ["", "## Confirmation Required", ""]
    lines += [f"- {x}" for x in plan["confirmation_required"]]
    lines += ["", "## Invalidation Triggers", ""]
    lines += [f"- {x}" for x in plan["invalidation_triggers"]]
    lines += [
        "",
        "## TSLA Strategy Context",
        "",
        f"- Candles: {plan['tsla_strategy']['candles']}",
        f"- Data Status: {plan['tsla_strategy']['data_status']}",
        f"- Signals: {plan['tsla_strategy']['signal_count']}",
        f"- PUT Signals: {plan['tsla_strategy']['put_signals']}",
        f"- CALL Signals: {plan['tsla_strategy']['call_signals']}",
        f"- Last Close: {plan['tsla_strategy']['last_close']}",
        "",
        "## Operator Rules",
        "",
    ]
    lines += [f"- {x}" for x in plan["operator_rules"]]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    plan = build_plan()
    write_plan(plan)

    print(f"DAY_PLAN_JSON={OUT_JSON}")
    print(f"DAY_PLAN_MD={OUT_MD}")
    print(f"DAY_TYPE={plan['day_type']}")
    print(f"BIAS={plan['bias']}")
    print(f"TRADE_PERMISSION={plan['trade_permission']}")
    print(f"SIZING={plan['sizing_posture']}")
    print("INTRADAY_TRADING_DAY_PLAN=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
