from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
env = os.environ.copy()
env["TELEGRAM_EPISODE"] = "2"
env["TELEGRAM_LIBRARY_PATH"] = "library/telegram/thai-spiritual-world.json"

raise SystemExit(
    subprocess.run(
        [sys.executable, "scripts/publish_telegram_library.py"],
        cwd=ROOT,
        env=env,
        check=False,
    ).returncode
)
