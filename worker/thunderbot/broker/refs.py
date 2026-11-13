"""Order reference ids for delivery orders.

Groww accepts 8 to 20 characters, letters and digits only. An id built from the ticker fails on both
counts: ``M&M`` and ``BAJAJ-AUTO`` carry punctuation, and a short ticker can leave the id under eight
characters. So nothing from the symbol goes in. The id is ``tb`` + the date + a digest of what the order
is, which makes it the same every time the same order is described and different for every other one.
"""

from __future__ import annotations

import hashlib
from datetime import date

_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyz"


def _base36(n: int, width: int) -> str:
    out = ""
    while n:
        n, r = divmod(n, 36)
        out = _ALPHABET[r] + out
    return out.rjust(width, "0")[-width:]


def delivery_ref(day: date, decision_id: str, symbol: str, side: str, attempt: int = 0) -> str:
    """An 18-character id: ``tb`` + yymmdd + 10 base-36 characters of a SHA-256 digest of
    (decision id, symbol, side, attempt). ``attempt`` separates a retry from the order it repeats."""
    digest = hashlib.sha256(f"{decision_id}|{symbol}|{side.upper()}|{attempt}".encode()).digest()
    return f"tb{day:%y%m%d}{_base36(int.from_bytes(digest[:8], 'big'), 10)}"
