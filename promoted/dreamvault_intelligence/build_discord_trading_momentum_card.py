#!/usr/bin/env python3
from pathlib import Path
from dreamvault.discord.trading_momentum_card import write_outputs

if __name__ == "__main__":
    result = write_outputs(Path("data/reports/discord/trading"))
    print("DISCORD_TRADING_MOMENTUM_CARD=PASS")
    print(f"JSON={result['json']}")
    print(f"MARKDOWN={result['markdown']}")
