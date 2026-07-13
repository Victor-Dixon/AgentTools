#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


PACKET_PATH = Path("data/reports/trading/daily_tsla_trade_packet.json")
OUT_PATH = Path("data/reports/discord/trading/daily_tsla_trade_packet_discord_demo.json")


def main() -> int:
    packet = json.loads(PACKET_PATH.read_text(encoding="utf-8"))

    payload = {
        "username": "Dream.OS Trading Cortex",
        "embeds": [
            {
                "title": "TSLA Daily Trade Packet",
                "description": (
                    f"**Regime:** {packet['market_context']['futures_regime']}\n"
                    f"**Trend:** {packet['tsla_structure']['trend']}\n"
                    f"**VWAP:** {packet['tsla_structure']['vwap_relation']}\n"
                    f"**Momentum:** {packet['tsla_structure']['momentum_state']}"
                ),
                "fields": [
                    {
                        "name": "Support",
                        "value": ", ".join(map(str, packet["tsla_structure"]["key_levels"]["support"])),
                        "inline": False,
                    },
                    {
                        "name": "Resistance",
                        "value": ", ".join(map(str, packet["tsla_structure"]["key_levels"]["resistance"])),
                        "inline": False,
                    },
                    {
                        "name": "Bull Scenario",
                        "value": packet["trade_scenarios"]["bull"],
                        "inline": False,
                    },
                    {
                        "name": "Bear Scenario",
                        "value": packet["trade_scenarios"]["bear"],
                        "inline": False,
                    },
                    {
                        "name": "No-Trade Condition",
                        "value": packet["trade_scenarios"]["no_trade"],
                        "inline": False,
                    },
                    {
                        "name": "Risk Mode",
                        "value": packet["risk_state"]["mode"],
                        "inline": False,
                    },
                ],
                "footer": {
                    "text": "Decision support only. Manual execution. Robot YAML not enabled."
                },
            }
        ],
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(payload, indent=2))
    print("DAILY_TSLA_PACKET_DISCORD_DEMO=PASS")
    print(f"PAYLOAD={OUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
