#!/usr/bin/env python3
"""Start message queue processor via PyAutoGUI adapter boundary.

Adapted from Agent_Cellphone_V2_Repository/tools/start_message_queue_processor.py
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def main() -> int:
    from agent_tools.discord_commander.queue_bridge import load_queue_processor

    logger.info("Starting message queue processor (PyAutoGUI adapter boundary)")
    processor = load_queue_processor()
    try:
        processor.process_queue(max_messages=None, batch_size=1, interval=5.0)
    except KeyboardInterrupt:
        logger.info("Queue processor stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
