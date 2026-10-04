from __future__ import annotations

import os
import sys

os.environ["TELEGRAM_EPISODE"] = "1"
os.environ["TELEGRAM_LIBRARY_PATH"] = "library/telegram/thai-spiritual-world.json"

from scripts.publish_telegram_library import main


if __name__ == "__main__":
    raise SystemExit(main())
