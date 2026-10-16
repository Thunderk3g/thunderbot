"""Checks tied to the SEBI retail-algo framework (fully in force from April 1, 2026).

- Static IP: every API order must come from an IP whitelisted on the Groww API
  Keys page. ``check_static_ip`` refuses to start live trading from any other IP,
  so orders are not silently rejected (or sent from the wrong host).
- Daily 2FA: sessions are force-logged-out daily. The engine asks a human to
  confirm each day's login before trading when TB_REQUIRE_LOGIN_CONFIRMATION=true.
- Order rate: see ``thunderbot.throttle`` (hard-capped below 10 orders/second).
- Audit trail: every order carries a unique reference id that is journaled
  together with the signal and LLM decision that produced it.
"""

from __future__ import annotations

import itertools
import secrets
from dataclasses import dataclass
from datetime import datetime

from .clock import to_ist

IP_ECHO_URLS = ("https://api.ipify.org", "https://ifconfig.me/ip", "https://checkip.amazonaws.com")


@dataclass
class IPCheck:
    ok: bool
    observed: str | None
    expected: str | None
    message: str


def public_ip(timeout: float = 5.0) -> str | None:
    import requests

    for url in IP_ECHO_URLS:
        try:
            resp = requests.get(url, timeout=timeout)
            if resp.ok and resp.text.strip():
                return resp.text.strip()
        except requests.RequestException:
            continue
    return None


def check_static_ip(expected: str | None, observed: str | None = None) -> IPCheck:
    if not expected:
        return IPCheck(False, observed, expected, "TB_EXPECTED_STATIC_IP is not set; live trading requires a whitelisted static IP")
    observed = observed if observed is not None else public_ip()
    if observed is None:
        return IPCheck(False, None, expected, "could not determine public IP")
    allowed = {ip.strip() for ip in expected.split(",") if ip.strip()}  # primary[,secondary]
    if observed not in allowed:
        return IPCheck(False, observed, expected, f"public IP {observed} is not in the whitelist {sorted(allowed)}")
    return IPCheck(True, observed, expected, f"public IP {observed} matches whitelist")


class OrderRefGenerator:
    """Unique, alphanumeric order reference ids (13 chars), e.g. ``TB261016001A3``.

    Groww accepts 8-20 alphanumeric characters. The date prefix keeps ids unique
    across days, and a random suffix guards against clashes after a restart.
    """

    def __init__(self, prefix: str = "TB") -> None:
        self.prefix = prefix
        self._counter = itertools.count(1)
        self._salt = secrets.token_hex(1).upper()

    def next(self, ts: datetime) -> str:
        ts = to_ist(ts)
        n = next(self._counter) % 1000
        return f"{self.prefix}{ts:%y%m%d}{n:03d}{self._salt}"[:20]
