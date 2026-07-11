#!/usr/bin/env python3
"""DEPRECATED: use start_message_bus_processor.py (DreamVault unified bus SSOT).

Legacy JSON queue at data/message_queue.json is no longer drained by hidden workers.
"""

from __future__ import annotations

import sys

if __name__ == "__main__":
    print(
        "DEPRECATED: start_message_queue_processor.py — use start_message_bus_processor.py",
        file=sys.stderr,
    )
    from start_message_bus_processor import main

    raise SystemExit(main())
