#!/usr/bin/env python3
import json
from pathlib import Path

ACCOUNT = Path("runtime/trading/ledger/paper_account.json")
EVENTS = Path("runtime/trading/events/options_paper_events.jsonl")
OUT = Path("runtime/trading/discord/latest_paper_trade_payload.json")
SUMMARY = Path("data/reports/trading/latest_discord_paper_trade_summary.md")

def load_latest_event():
    if not EVENTS.exists():
        return {}
    lines = [line for line in EVENTS.read_text().splitlines() if line.strip()]
    if not lines:
        return {}
    return json.loads(lines[-1])

def main():
    account = json.loads(ACCOUNT.read_text())
    event = load_latest_event()
    stats = account.get("stats", {})

    action = event.get("action", "STATUS")
    contract = event.get("contract_symbol", "N/A")
    strategy = event.get("strategy_id", "manual")
    pnl = float(event.get("pnl", 0.0))

    day_pnl = 0.0
    if event.get("closed_at"):
        day = event["closed_at"][:10]
        for trade in account.get("closed_trades", []):
            if str(trade.get("closed_at", "")).startswith(day):
                day_pnl += float(trade.get("pnl", 0.0))

    made_lost = "MADE" if day_pnl >= 0 else "LOST"

    payload = {
        "username": "Dream.OS Paper Trader",
        "content": f"Dream.OS paper options update: {action} {contract}",
        "embeds": [
            {
                "title": "Dream.OS Paper Options Trade",
                "description": f"Strategy: `{strategy}`",
                "fields": [
                    {"name": "Action", "value": f"`{action}`", "inline": True},
                    {"name": "Contract", "value": f"`{contract}`", "inline": True},
                    {"name": "Mode", "value": "`paper_only`", "inline": True},
                    {"name": "Starting Equity", "value": f"${account['starting_equity']:.2f}", "inline": True},
                    {"name": "Current Equity", "value": f"${account['current_equity']:.2f}", "inline": True},
                    {"name": "Realized PnL", "value": f"${account['realized_pnl']:.2f}", "inline": True},
                    {"name": f"Today Would Have {made_lost}", "value": f"${abs(day_pnl):.2f}", "inline": True},
                    {"name": "Trades", "value": str(stats.get("total_trades", 0)), "inline": True},
                    {"name": "Win Rate", "value": f"{float(stats.get('win_rate', 0.0)) * 100:.2f}%", "inline": True},
                    {"name": "Wins / Losses", "value": f"{stats.get('wins', 0)} / {stats.get('losses', 0)}", "inline": True},
                    {"name": "Profit Factor", "value": str(stats.get("profit_factor", 0.0)), "inline": True}
                ]
            }
        ]
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n")

    print(f"DISCORD_PAYLOAD={OUT}")
    print(f"ACTION={action}")
    print(f"CONTRACT={contract}")
    print(f"CURRENT_EQUITY={account['current_equity']:.2f}")
    print(f"REALIZED_PNL={account['realized_pnl']:.2f}")
    print(f"TODAY_WOULD_HAVE_{made_lost}={abs(day_pnl):.2f}")

    if SUMMARY.exists():
        print(f"SUMMARY={SUMMARY}")

if __name__ == "__main__":
    main()
