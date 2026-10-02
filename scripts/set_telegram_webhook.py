from __future__ import annotations

import os
import urllib.parse
import urllib.request


def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    webhook_url = os.environ.get("TELEGRAM_WEBHOOK_URL", "").strip()
    secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "").strip()
    if not token or not webhook_url or not secret:
        raise SystemExit(
            "TELEGRAM_BOT_TOKEN, TELEGRAM_WEBHOOK_URL and TELEGRAM_WEBHOOK_SECRET are required"
        )
    if not webhook_url.startswith("https://"):
        raise SystemExit("TELEGRAM_WEBHOOK_URL must use https://")

    payload = urllib.parse.urlencode(
        {"url": webhook_url, "secret_token": secret, "allowed_updates": '["message","callback_query"]'}
    ).encode("utf-8")
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/setWebhook",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
    print(body)


if __name__ == "__main__":
    main()
