"""The worker as a function that is woken up, does one pass, and exits.

There is no process to keep alive: a scheduler (Supabase pg_cron, Vercel Cron, GitHub Actions, or a
laptop's task scheduler) calls ``handle`` every few minutes during market hours, and the dashboard
calls it to run a backtest. Everything it knows between calls is in Supabase.

Operations:
- ``tick``: one pass of the daily investing runner (heartbeat, the 15:10 decision when due), one bar of
  the AI intraday desk (paper), then any research or training jobs still queued.
- ``job``: run one queued research job now (``id`` selects it), within the function's time limit.
- ``health``: configuration check that touches nothing.

Live orders are refused here unless a fixed outbound address is configured: brokers accept API orders
only from the static IP registered to the account, and a serverless function has no address of its own.
"""

from __future__ import annotations

import base64
import hmac
import logging
import os
import time
from typing import Any

from .clock import now_ist, parse_hhmm
from .config import Settings

log = logging.getLogger(__name__)

OPS = ("tick", "job", "health")


def authorized(headers: dict[str, str], env: dict[str, str] | None = None) -> bool:
    """A scheduler's bearer secret, or the dashboard's own Basic credentials. Fails closed."""
    env = os.environ if env is None else env
    auth = next((v for k, v in headers.items() if k.lower() == "authorization"), "") or ""
    secret = env.get("CRON_SECRET") or ""
    if secret and auth.startswith("Bearer ") and hmac.compare_digest(auth[7:].encode(), secret.encode()):
        return True
    user, password = env.get("DASHBOARD_USER") or "", env.get("DASHBOARD_PASSWORD") or ""
    if user and password and auth.startswith("Basic "):
        try:
            got_user, _, got_pass = base64.b64decode(auth[6:]).decode().partition(":")
        except Exception:
            return False
        return hmac.compare_digest(got_user.encode(), user.encode()) and hmac.compare_digest(got_pass.encode(), password.encode())
    return False


def build_runner(settings: Settings, store: Any, scheduler: str = "serverless"):
    """The paper investing runner on free Yahoo prices, with state in ``store``."""
    from .chart import ChartQuotes
    from .invest import InvestRunner
    from .llm.rebalance import build_rebalance_reviewer
    from .notify import build_notifier

    quotes = ChartQuotes()
    return InvestRunner(
        store, quotes, settings.clock(), settings.capital, mode="paper", strategy=settings.invest_strategy,
        run_at=parse_hhmm(settings.invest_at), cutoff=parse_hhmm(settings.invest_cutoff), feed_status=quotes.status,
        liquid_symbol=settings.liquid_symbol, reviewer=build_rebalance_reviewer(settings),
        notify=build_notifier(settings.telegram_token, settings.telegram_chat_id, settings.ntfy_topic),
        scheduler=scheduler, tick_minutes=settings.tick_minutes,
    )


def run_intraday(settings: Settings, store: Any) -> dict[str, Any]:
    """One bar of the AI desk. Its failure is journalled and must not take the investing tick down with it."""
    from .ai.runner import IntradayRunner

    try:
        return IntradayRunner(settings, store).tick()
    except Exception as e:
        log.exception("AI desk tick failed")
        try:
            store.event("error", f"AI desk tick failed: {type(e).__name__}: {e}")
        except Exception:
            pass
        return {"intraday": f"error: {type(e).__name__}: {e}"}


def run_jobs(settings: Settings, store: Any, deadline: float, job_id: str | None = None) -> list[str]:
    """Run queued research jobs until none are left or the time budget is nearly spent."""
    from .jobs import JobRunner

    runner = JobRunner(store, settings)
    done: list[str] = []
    while time.monotonic() < deadline:
        ran = runner.run_once(job_id)
        if not ran:
            break
        done.append(ran)
        if job_id:
            break
    return done


def handle(op: str, params: dict[str, str] | None = None, settings: Settings | None = None, store: Any = None,
           budget_seconds: float = 240.0) -> tuple[int, dict[str, Any]]:
    """Run one operation. Returns (HTTP status, JSON body). Never raises: errors come back as a 500 body."""
    from .credentials import apply_credentials
    from .store import build_remote_store

    params = params or {}
    if op not in OPS:
        return 400, {"error": f"op must be one of {OPS}"}
    started = time.monotonic()
    try:
        settings = settings or Settings.from_env()
        if op == "health":
            return 200, {"ok": True, "at": now_ist().isoformat(), "supabase": bool(settings.supabase_url and settings.supabase_service_key),
                         "strategy": settings.invest_strategy, "run_at": settings.invest_at, "liquid_symbol": settings.liquid_symbol,
                         "reviewer": settings.llm_enabled, "llm": settings.llm_provider, "mode": "paper"}
        store = store or build_remote_store(settings.supabase_url, settings.supabase_service_key)
        # Keys saved from the dashboard's setup screen win over the environment's. They cover the LLM and
        # the Groww login; nothing saved there can enable real orders.
        settings = apply_credentials(settings, store)
        deadline = started + budget_seconds
        if op == "job":
            ran = run_jobs(settings, store, deadline, params.get("id") or None)
            return 200, {"ok": True, "jobs": ran, "seconds": round(time.monotonic() - started, 1)}
        publish_catalog(settings, store)
        summary = build_runner(settings, store).tick()
        desk = run_intraday(settings, store)
        ran = run_jobs(settings, store, deadline)
        return 200, {"ok": True, **summary, **desk, "jobs": ran, "seconds": round(time.monotonic() - started, 1)}
    except Exception as e:
        log.exception("serverless %s failed", op)
        try:
            if store is not None:
                store.event("error", f"worker {op} failed: {type(e).__name__}: {e}")
        except Exception:
            pass
        return 500, {"error": f"{type(e).__name__}: {e}"}


def publish_catalog(settings: Settings, store: Any) -> None:
    """Keep the dashboard's strategy lists and effective settings current (cheap, idempotent)."""
    from .daily import DAILY_CATALOG
    from .strategy import catalog

    control = store.get_control()
    if control.get("daily_catalog") != DAILY_CATALOG:
        store.set_control("daily_catalog", DAILY_CATALOG)
    if control.get("strategy_catalog") != catalog():
        store.set_control("strategy_catalog", catalog())
    new, rejected = settings.with_overrides(control.get("settings_overrides") or {})
    view = {**new.public_view(), "rejected": rejected}
    if control.get("effective_settings") != view:
        store.set_control("effective_settings", view)
