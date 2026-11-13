"""Read-only check of Groww credentials: log in, read the profile, probe live data, compare the IP.

It never places, changes or cancels an order. The command ``thunderbot login-check`` prints its result,
and the dashboard's setup screen queues it as a ``groww_check`` job and shows the same steps.

Result shape (also stored in the control row ``groww_check``)::

    {"ok": bool, "at": iso time, "steps": [{"name", "ok", "detail"}],
     "ip": {"observed", "expected", "ok"} | None}

``ok`` means the key is well formed, the SDK is present, the login worked and the profile was read.
Live data and the static IP are reported but do not decide ``ok``: paper trading needs neither.
"""

from __future__ import annotations

import importlib.util
from collections.abc import Callable
from pathlib import Path
from typing import Any

from ..clock import now_ist
from .base import BrokerError
from .groww import GrowwSession, key_role

PACKAGES = ("growwapi", "pyotp")


def missing_packages() -> list[str]:
    return [name for name in PACKAGES if importlib.util.find_spec(name) is None]


def _scrub(text: str, secrets: list[str | None]) -> str:
    """Remove credential values from a message before it is shown or stored."""
    for s in secrets:
        if s and len(s) >= 6:
            text = text.replace(s, "[hidden]")
    return text[:400]


def _default_client(token: str) -> Any:
    from growwapi import GrowwAPI

    return GrowwAPI(token)


def login_check(
    api_key: str | None,
    totp_secret: str | None = None,
    api_secret: str | None = None,
    *,
    cache_path: Path | None = None,
    fresh: bool = False,
    expected_ip: str | None = None,
    session_factory: Callable[..., Any] = GrowwSession,
    client_factory: Callable[[str], Any] = _default_client,
    missing: Callable[[], list[str]] = missing_packages,
    public_ip: Callable[[], str | None] | None = None,
) -> dict[str, Any]:
    secrets = [api_key, totp_secret, api_secret]
    steps: list[dict[str, Any]] = []

    def step(name: str, ok: bool, detail: str) -> bool:
        steps.append({"name": name, "ok": ok, "detail": _scrub(detail, secrets)})
        return ok

    def done(ok: bool, token: str | None = None) -> dict[str, Any]:
        for s in steps:
            s["detail"] = _scrub(s["detail"], [token])
        return {"ok": ok, "at": now_ist().isoformat(), "steps": steps, "ip": _ip_check(expected_ip, public_ip)}

    if not api_key:
        step("Key", False, "No Groww API key is saved in Setup or set as GROWW_API_KEY.")
        return done(False)
    role = key_role(api_key)
    try:
        session = session_factory(api_key, totp_secret, api_secret, cache_path=cache_path)
    except BrokerError as e:
        step("Key", False, str(e))
        return done(False)
    if role == "auth-totp":
        step("Key", True, "TOTP key: the worker can log in by itself each morning")
    elif role:
        step("Key", True, "approval key: it must be approved on Groww's API Keys page each day")
    else:
        step("Key", True, "key type not recognised; the login below shows whether it works")

    absent = missing()
    if absent:
        step("SDK", False, f"{' and '.join(absent)} {'is' if len(absent) == 1 else 'are'} not installed where this check ran. "
                           "A serverless worker does not carry the Groww SDK because it cannot place orders. Run "
                           "'thunderbot login-check' on the machine that has your static IP.")
        return done(False)
    step("SDK", True, "Groww SDK installed")

    try:
        token, new = session.token(force_refresh=fresh)
    except BrokerError as e:
        step("Login", False, str(e))
        return done(False)
    except Exception as e:
        # A network failure is not a refusal: say which, so the owner fixes the right thing.
        network = any(w in type(e).__name__ for w in ("Connection", "Proxy", "Timeout", "SSL"))
        why = "Could not reach Groww from where the worker runs" if network else "Groww refused the login"
        step("Login", False, f"{why} ({type(e).__name__}: {e})")
        return done(False)
    step("Login", True, "new access token issued" if new else "the access token issued earlier today still works")

    ok = True
    try:
        client = client_factory(token)
        client.get_user_profile()
        step("Profile", True, "account profile read")
    except Exception as e:
        ok = step("Profile", False, f"could not read the profile ({type(e).__name__}: {e})")
        return done(ok, token)
    try:
        ltp = client.get_ltp(exchange_trading_symbols=("NSE_RELIANCE",), segment="CASH")
        step("Live data", True, f"RELIANCE last traded at {ltp.get('NSE_RELIANCE')}")
    except Exception as e:
        step("Live data", False, f"not available ({type(e).__name__}: {e}). Live prices need a paid Trade API plan; "
                                 "paper trading on free prices works without it.")
    return done(ok, token)


def _ip_check(expected: str | None, public_ip: Callable[[], str | None] | None) -> dict[str, Any] | None:
    """This machine's public address against the one registered for orders. None when neither is known."""
    from ..compliance import check_static_ip
    from ..compliance import public_ip as lookup

    try:
        observed = (public_ip or lookup)()
    except Exception:
        observed = None
    if not expected and not observed:
        return None
    ok = bool(expected and observed) and check_static_ip(expected, observed).ok
    return {"observed": observed, "expected": expected or None, "ok": ok}
