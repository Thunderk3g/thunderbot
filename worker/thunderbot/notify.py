"""Short alerts to a phone: a rebalance was made, a run was missed, prices looked wrong.

Two free channels, both optional. Telegram needs a bot token and a chat id (TB_TELEGRAM_TOKEN,
TB_TELEGRAM_CHAT_ID); ntfy.sh needs only a topic name that is hard to guess (TB_NTFY_TOPIC).
A failed alert is logged and never stops the run.
"""

from __future__ import annotations

import logging
from collections.abc import Callable

log = logging.getLogger(__name__)


def build_notifier(telegram_token: str | None = None, telegram_chat: str | None = None,
                   ntfy_topic: str | None = None, post: Callable[..., object] | None = None) -> Callable[[str], None] | None:
    if not (telegram_token and telegram_chat) and not ntfy_topic:
        return None

    def send(text: str) -> None:
        import requests

        do = post or requests.post
        if telegram_token and telegram_chat:
            do(f"https://api.telegram.org/bot{telegram_token}/sendMessage",
               json={"chat_id": telegram_chat, "text": text[:3900]}, timeout=10)
        if ntfy_topic:
            do(f"https://ntfy.sh/{ntfy_topic}", data=text[:3900].encode(), timeout=10)

    return send
