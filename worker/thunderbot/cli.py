"""Command-line entry point: ``thunderbot <command>``."""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

from .backtest import Backtester, format_report
from .clock import IST, now_ist
from .config import Settings
from .costs import CostModel
from .data import CSVMarketData, GrowwMarketData, synthetic_history, write_csv
from .store import build_store
from .strategy import Strategy, build_strategy

log = logging.getLogger("thunderbot")


def load_dotenv(path: str | Path = ".env") -> list[str]:
    """Load KEY=VALUE lines from a local .env (gitignored) without overriding the real environment."""
    import os

    p = Path(path)
    if not p.is_file():
        return []
    loaded = []
    for raw in p.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.removeprefix("export ").strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value
            loaded.append(key)
    return loaded


def _settings() -> Settings:
    s = Settings.from_env()
    for w in s.warnings:
        log.warning(w)
    return s


def _stored(s: Settings, store=None) -> Settings:
    """Settings with the keys saved from the dashboard's setup screen applied on top of the environment.

    Saved keys cover the LLM and the Groww login only. Live trading, the static IP and MTF stay with
    the environment and the command line.
    """
    from .credentials import apply_credentials

    return apply_credentials(s, store or build_store(s.data_path, s.supabase_url, s.supabase_service_key))


def _strategy(s: Settings) -> Strategy:
    return build_strategy(s.strategy, s.strategy_params, s.allow_short)


def _groww_session(s: Settings):
    from .broker.groww import GrowwSession

    return GrowwSession(s.groww_api_key or "", s.groww_totp_secret, s.groww_api_secret,
                        cache_path=s.data_path / "groww_token.json")


def _groww_client(s: Settings):
    from growwapi import GrowwAPI

    token, fresh = _groww_session(s).token()
    if fresh:
        build_store(s.data_path, s.supabase_url, s.supabase_service_key).event(
            "login", "new Groww access token issued", at=now_ist().isoformat())
    return GrowwAPI(token)


# Commands

def cmd_demo_data(args, s: Settings) -> int:
    start = date.fromisoformat(args.start)
    data = synthetic_history(s.symbols, start, args.days, s.interval_minutes, seed=args.seed)
    out = Path(args.out)
    for sym, bars in data.items():
        write_csv(out / f"{sym}.csv", bars)
    print(f"wrote {len(data)} synthetic files to {out} ({args.days} sessions each). Synthetic data is for plumbing tests only.")
    return 0


def cmd_fetch_history(args, s: Settings) -> int:
    if args.source == "yahoo":
        from .yahoo import YahooMarketData

        md = YahooMarketData(exchange=s.exchange)
    else:
        md = GrowwMarketData(_groww_client(_stored(s)), exchange=s.exchange)
    end = datetime.combine(date.fromisoformat(args.end), datetime.min.time(), tzinfo=IST) if args.end else now_ist()
    start = end - timedelta(days=args.days)
    out = Path(args.out)
    for sym in s.symbols:
        bars = md.candles(sym, args.interval, start, end)
        write_csv(out / f"{sym}.csv", bars)
        print(f"{sym}: {len(bars)} bars")
        time.sleep(0.2)  # stay well inside the live-data rate limit
    return 0


def cmd_backtest(args, s: Settings) -> int:
    if args.yahoo:
        from .yahoo import YahooMarketData

        md = YahooMarketData(exchange=s.exchange)
        symbols = s.symbols
        print("Using free Yahoo Finance candles (real NSE prices; 5-minute bars cover the last 60 days only).")
    elif args.data:
        md = CSVMarketData(args.data)
        symbols = s.symbols if not args.all_files else md.symbols()
    else:
        print("Give --data <dir of CSVs> or --yahoo.", file=sys.stderr)
        return 2
    s.symbols = symbols
    start = datetime.fromisoformat(args.start).replace(tzinfo=IST) if args.start else datetime(2000, 1, 1, tzinfo=IST)
    end = datetime.fromisoformat(args.end).replace(tzinfo=IST) if args.end else now_ist() + timedelta(days=1)
    data = {sym: md.candles(sym, s.interval_minutes, start, end) for sym in symbols}
    signal_filter = None
    if args.llm:
        from .llm.filter import ClaudeSignalFilter

        log.warning("LLM-filtered backtests suffer look-ahead bias (the model has seen this history). Treat results as plumbing tests.")
        signal_filter = ClaudeSignalFilter(s)
    result = Backtester(s, _strategy(s), CostModel(), signal_filter).run(data)
    metrics = result.metrics()
    print(format_report(metrics))
    if args.trades_csv:
        import csv

        with open(args.trades_csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["symbol", "side", "qty", "entry", "exit", "opened_at", "closed_at", "reason", "gross", "costs", "net"])
            for t in result.trades:
                w.writerow([t.symbol, t.side.value, t.qty, t.entry_price, t.exit_price, t.opened_at.isoformat(),
                            t.closed_at.isoformat(), t.exit_reason, round(t.gross_pnl, 2), t.costs, round(t.net_pnl, 2)])
    if args.json:
        print(json.dumps(metrics, indent=2, default=str))
    return 0


def _run_engine(s: Settings, mode: str) -> int:
    from .broker.groww import GrowwBroker, GrowwLink
    from .broker.paper import PaperBroker
    from .engine import TradingEngine
    from .llm.filter import build_filter
    from .throttle import OrderThrottle

    store = build_store(s.data_path, s.supabase_url, s.supabase_service_key)
    s = _stored(s, store)
    if mode == "paper" and s.feed == "yahoo":
        return _run_paper_on_yahoo(s, store)
    # The worker stays up even if the Groww login fails, and shows the reason on the dashboard.
    # Paper mode still uses Groww for live prices and candles; only the orders are simulated.
    link = GrowwLink(lambda: _groww_session(s),
                     on_fresh_token=lambda: store.event("login", "new Groww access token issued"))
    if problem := link.ensure():
        store.event("feed_error", problem)

    throttle = OrderThrottle(s.orders_per_second, s.orders_per_minute)
    groww = GrowwBroker(link, throttle, allow_mtf=s.allow_mtf_api, exchange=s.exchange)
    broker = groww if mode == "live" else PaperBroker(s.capital, s.slippage_bps)
    engine = TradingEngine(
        settings=s, broker=broker, quotes=groww, data=GrowwMarketData(link, exchange=s.exchange),
        strategy=_strategy(s), signal_filter=build_filter(s), store=store, mode=mode,
        before_market_tick=lambda now: link.ensure(), filter_factory=build_filter,
        require_login_confirmation=(mode == "live" and s.require_login_confirmation),
        require_start=True, feed_status=link.status,
    )
    engine.run_forever()
    return 0


def _run_paper_on_yahoo(s: Settings, store) -> int:
    """Paper trading on free Yahoo Finance prices: no Groww account or data plan needed."""
    from .broker.paper import PaperBroker
    from .engine import TradingEngine
    from .llm.filter import build_filter
    from .yahoo import YahooFeed

    feed = YahooFeed(exchange=s.exchange)
    if problem := feed.ensure():
        store.event("feed_error", problem)
    engine = TradingEngine(
        settings=s, broker=PaperBroker(s.capital, s.slippage_bps), quotes=feed.quotes, data=feed.data,
        strategy=_strategy(s), signal_filter=build_filter(s), store=store, mode="paper",
        before_market_tick=lambda now: feed.ensure(), filter_factory=build_filter,
        require_start=True, feed_status=feed.status,
    )
    engine.run_forever()
    return 0


def _invest_runner(s: Settings, mode: str, store, scheduler: str = "worker"):
    """Daily delivery investing (see thunderbot/invest.py). Paper uses TB_FEED prices; live uses Groww."""
    from .clock import parse_hhmm
    from .invest import InvestRunner
    from .llm.rebalance import build_rebalance_reviewer
    from .notify import build_notifier

    s = _stored(s, store)
    broker = None
    if mode == "live" or s.feed == "groww":
        from .broker.groww import GrowwBroker, GrowwLink
        from .throttle import OrderThrottle

        link = GrowwLink(lambda: _groww_session(s),
                         on_fresh_token=lambda: store.event("login", "new Groww access token issued"))
        if problem := link.ensure():
            store.event("feed_error", problem)
        groww = GrowwBroker(link, OrderThrottle(s.orders_per_second, s.orders_per_minute), exchange=s.exchange)
        quotes, status = groww, link.status
        broker = groww if mode == "live" else None
    else:
        from .chart import ChartQuotes

        quotes = ChartQuotes()
        status = quotes.status
    from .broker.groww import holdings_reader
    from .daily import CapitalGainsTax

    return InvestRunner(store, quotes, s.clock(), s.capital, mode=mode, broker=broker, strategy=s.invest_strategy,
                        run_at=parse_hhmm(s.invest_at), cutoff=parse_hhmm(s.invest_cutoff), feed_status=status,
                        liquid_symbol=s.liquid_symbol, reviewer=build_rebalance_reviewer(s),
                        notify=build_notifier(s.telegram_token, s.telegram_chat_id, s.ntfy_topic),
                        scheduler=scheduler, tick_minutes=s.tick_minutes,
                        holdings_source=holdings_reader(s.groww_api_key, s.groww_totp_secret, s.groww_api_secret,
                                                        cache_path=s.data_path / "groww_token.json"),
                        band_abs_pct=s.band_abs_pct, band_rel_pct=s.band_rel_pct, harvest_via=s.harvest_via,
                        tax=CapitalGainsTax(slab_rate=s.slab_rate_pct / 100))


def _run_invest(s: Settings, mode: str) -> int:
    from .daily import DAILY_CATALOG

    store = build_store(s.data_path, s.supabase_url, s.supabase_service_key)
    runner = _invest_runner(s, mode, store)
    store.set_control("daily_catalog", DAILY_CATALOG)
    runner.run_forever()
    return 0


def _live_guard(args, s: Settings) -> str | None:
    """Why live investing must not start, or None when every opt-in is in place."""
    from .compliance import check_static_ip

    if not args.i_understand_the_risks or not s.live_trading_enabled:
        return "needs --i-understand-the-risks and TB_LIVE_TRADING_ENABLED=true."
    ip = check_static_ip(s.expected_static_ip)
    return None if ip.ok else ip.message


def cmd_tick(args, s: Settings) -> int:
    """One pass of the daily investing worker, then exit. For schedulers: cron, Task Scheduler, launchd,
    GitHub Actions. State lives in Supabase when it is configured, so the dashboard sees the same account."""
    from .serverless import publish_catalog, run_jobs
    from .store import build_remote_store

    mode = "live" if args.live else "paper"
    if args.live and (problem := _live_guard(args, s)):
        print(f"Refusing to invest live: {problem}", file=sys.stderr)
        return 2
    remote = bool(s.supabase_url and s.supabase_service_key)
    store = build_remote_store(s.supabase_url, s.supabase_service_key) if remote else build_store(s.data_path, None, None)
    try:
        s = _stored(s, store)
        publish_catalog(s, store)
        summary = _invest_runner(s, mode, store, scheduler="serverless").tick()
        if not args.no_jobs:
            summary["jobs"] = run_jobs(s, store, time.monotonic() + args.job_seconds)
    except Exception as e:
        log.exception("tick failed")
        store.event("error", f"tick failed: {type(e).__name__}: {e}")
        return 1
    print(json.dumps(summary, indent=2, default=str))
    return 0


def cmd_invest(args, s: Settings) -> int:
    if args.live:
        if problem := _live_guard(args, s):
            print(f"Refusing to invest live: {problem}", file=sys.stderr)
            return 2
        return _run_invest(s, "live")
    return _run_invest(s, "paper")


def cmd_invest_backtest(args, s: Settings) -> int:
    from . import daily

    strat = daily.build_daily(args.strategy, {})
    end = date.fromisoformat(args.end) if args.end else now_ist().date()
    start = end - timedelta(days=int(args.years * 365.25))
    twin = daily.no_timing_twin(strat)
    symbols = list(dict.fromkeys([daily.INDEX, daily.BENCHMARK, *strat.universe(), *(twin.universe() if twin else [])]))
    errors: dict[str, str] = {}
    prices = daily.load_prices(symbols, start - timedelta(days=460), end, cache_dir=s.data_path / "cache" / "daily", errors=errors)
    for sym, why in errors.items():
        print(f"no data for {sym}: {why}", file=sys.stderr)
    tax = None if args.no_tax else daily.CapitalGainsTax(slab_rate=s.slab_rate_pct / 100)
    res = daily.backtest(strat, prices, start, end, capital=s.capital, tax=tax)
    m = res.metrics()
    bench = m.pop("benchmark")
    print(f"{args.strategy}: {start} to {end}, capital {s.capital:,.0f}, {'pre-tax' if args.no_tax else 'after tax'}")
    for k, v in m.items():
        print(f"  {k:>26}: {v}")
    keys = ("cagr_pct", "cagr_after_exit_tax_pct", "max_drawdown_pct", "sharpe")
    print("  benchmark (NIFTYBEES held):", {k: bench.get(k) for k in keys})
    if twin is not None:
        t = daily.backtest(twin, prices, start, end, capital=s.capital, tax=tax).metrics()
        print("  same ETFs, equal parts, no timing:", {k: t.get(k) for k in keys})
    print("  year  strategy  benchmark")
    for y in res.yearly():
        print(f"  {y['year']}  {y['strategy_pct']:>7}%  {y['benchmark_pct']:>8}%")
    if args.strategy == "momentum":
        print("Note: today's Nifty 100 list is used, so survivorship bias inflates this result.")
    return 0


def _groww_factory(s: Settings):
    if not s.groww_api_key:
        return None
    return lambda: _groww_client(s)


def cmd_serve(args, s: Settings) -> int:
    import os
    import secrets as _secrets

    from .server import serve

    key = os.environ.get("TB_LOCAL_API_KEY") or _secrets.token_urlsafe(24)
    if "TB_LOCAL_API_KEY" not in os.environ:
        print(f"TB_LOCAL_API_KEY not set; generated one for this session:\n  {key}\n"
              "Keys saved in the dashboard's Setup are encrypted under it, so set TB_LOCAL_API_KEY (or TB_SECRET_KEY)\n"
              "to a fixed value if you want them to survive a restart.")
        os.environ["TB_LOCAL_API_KEY"] = key  # the job runner in this process decrypts saved keys with it
    httpd = serve(s, args.host, args.port, key, run_jobs=not args.no_jobs, groww_client_factory=_groww_factory(s))
    print(f"Local API on http://{args.host}:{args.port}. Dashboard env:\n"
          f"  SUPABASE_URL=http://{args.host}:{args.port}\n  SUPABASE_SERVICE_ROLE_KEY={key}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


def cmd_jobs(args, s: Settings) -> int:
    from .jobs import JobRunner

    store = build_store(s.data_path, s.supabase_url, s.supabase_service_key)
    runner = JobRunner(store, s, _groww_factory(s))
    if args.once:
        runner.publish_catalog()
        while runner.run_once():
            pass
        return 0
    runner.run_forever()
    return 0


def cmd_replay(args, s: Settings) -> int:
    from .llm.filter import build_filter
    from .replay import run_replay

    if args.data:
        md = CSVMarketData(args.data)
        if args.all_files:
            s.symbols = md.symbols()
        far = datetime(2000, 1, 1, tzinfo=IST), datetime(2100, 1, 1, tzinfo=IST)
        data = {sym: md.candles(sym, s.interval_minutes, *far) for sym in s.symbols}
    else:
        data = synthetic_history(s.symbols, date.fromisoformat(args.start), args.days, s.interval_minutes, seed=args.seed)
        print("Replaying SYNTHETIC data (random walk). Results say nothing about real markets.")
    if args.days and args.data:
        days = sorted({c.ts.date() for bars in data.values() for c in bars})[-args.days:]
        keep = set(days)
        data = {sym: [c for c in bars if c.ts.date() in keep] for sym, bars in data.items()}
    store = build_store(s.data_path, s.supabase_url, s.supabase_service_key)
    s = _stored(s, store)
    reviewer = args.reviewer
    if reviewer == "claude":
        s.llm_enabled = True
        reviewer = "auto"
    engine = run_replay(
        s, data, store, build_filter(s, reviewer), speed=args.speed,
        filter_factory=lambda st: build_filter(st, reviewer),
        on_day=lambda d: print(f"replaying {d}"),
    )
    print(f"done. realized P&L on the last day: {engine.risk.state.realized_pnl:.2f}")
    return 0


def cmd_paper(args, s: Settings) -> int:
    return _run_engine(s, "paper")


def cmd_live(args, s: Settings) -> int:
    from .compliance import check_static_ip

    if not args.i_understand_the_risks:
        print("Refusing to trade live without --i-understand-the-risks.", file=sys.stderr)
        return 2
    if not s.live_trading_enabled:
        print("Refusing to trade live: set TB_LIVE_TRADING_ENABLED=true.", file=sys.stderr)
        return 2
    ip = check_static_ip(s.expected_static_ip)
    store = build_store(s.data_path, s.supabase_url, s.supabase_service_key)
    store.event("static_ip_check", ip.message, ok=ip.ok, observed=ip.observed, expected=ip.expected)
    if not ip.ok:
        print(f"Refusing to trade live: {ip.message}", file=sys.stderr)
        return 2
    return _run_engine(s, "live")


def cmd_control(args, s: Settings) -> int:
    store = build_store(s.data_path, s.supabase_url, s.supabase_service_key)
    if args.command == "start":
        store.set_control("kill_switch", False)
        store.set_control("paused", False)
        store.set_control("trading_enabled", True)
        store.event("trading_started", "trading started from CLI")
    elif args.command == "stop":
        store.set_control("trading_enabled", False)
        store.event("trading_stopped", "stopped from CLI: no new trades; investments stay, intraday positions are closed")
    elif args.command == "sell-all":
        from .invest import queue_command

        store.set_control("trading_enabled", False)
        queue_command(store, "sell_all")
        store.event("sell_all", "sell-all requested from CLI")
    elif args.command == "deposit":
        from .invest import queue_command

        if not args.amount > 0:
            print("The amount must be more than zero.", file=sys.stderr)
            return 2
        queue_command(store, "deposit", amount=float(args.amount))
        store.event("deposit", f"deposit of Rs {args.amount:,.0f} recorded from CLI")
    elif args.command == "mode":
        from .invest import MODE_KEY

        store.set_control(MODE_KEY, args.mode)
        store.event("invest_mode", f"orders are now {args.mode} (set from CLI)")
    elif args.command == "kill":
        store.set_control("kill_switch", True)
        store.event("kill_switch", "engaged from CLI")
    elif args.command == "resume":
        store.set_control("kill_switch", False)
        store.set_control("paused", False)
        store.event("resume", "kill switch released from CLI")
    elif args.command == "pause":
        store.set_control("paused", True)
        store.event("pause", "new entries paused from CLI")
    elif args.command == "confirm-login":
        today = now_ist().date().isoformat()
        store.set_control("login_confirmed_for", today)
        store.event("login_confirmed", f"login confirmed for {today} from CLI")
    print(json.dumps(store.get_control(), indent=2, default=str))
    return 0


def cmd_login_check(args, s: Settings) -> int:
    """Read-only Groww check: log in, fetch the profile, and probe the live-data plan. Never places orders."""
    from .broker.check import login_check

    s = _stored(s)
    result = login_check(s.groww_api_key, s.groww_totp_secret, s.groww_api_secret,
                         cache_path=s.data_path / "groww_token.json", fresh=args.fresh, expected_ip=s.expected_static_ip)
    for step in result["steps"]:
        print(f"{step['name']}: {'OK' if step['ok'] else 'FAILED'} ({step['detail']})")
    ip = result["ip"]
    if ip:
        if ip["expected"]:
            print(f"Static IP: {'matches' if ip['ok'] else 'does NOT match'} (this machine {ip['observed']}, registered {ip['expected']})")
        else:
            print(f"Static IP: this machine is {ip['observed']}; TB_EXPECTED_STATIC_IP is not set")
    print("No orders were placed. Orders additionally require this host's IP to be whitelisted on Groww.")
    if result["ok"]:
        return 0
    failed = next((x["name"] for x in result["steps"] if not x["ok"]), "")
    return 2 if failed in ("Key", "SDK") else 1


def cmd_check_ip(args, s: Settings) -> int:
    from .compliance import check_static_ip

    r = check_static_ip(s.expected_static_ip)
    print(r.message)
    return 0 if r.ok else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="thunderbot", description=__doc__)
    p.add_argument("-v", "--verbose", action="store_true")
    sub = p.add_subparsers(dest="command", required=True)

    d = sub.add_parser("demo-data", help="write synthetic 5-minute CSVs for plumbing tests")
    d.add_argument("--out", default="data/demo")
    d.add_argument("--start", default="2026-01-05")
    d.add_argument("--days", type=int, default=60)
    d.add_argument("--seed", type=int, default=7)
    d.set_defaults(func=cmd_demo_data)

    f = sub.add_parser("fetch-history", help="download candles into CSV from Groww (paid plan) or Yahoo (free)")
    f.add_argument("--source", choices=("groww", "yahoo"), default="groww")
    f.add_argument("--out", default="data/groww")
    f.add_argument("--days", type=int, default=90)
    f.add_argument("--end", help="YYYY-MM-DD (default: now)")
    f.add_argument("--interval", type=int, default=5)
    f.set_defaults(func=cmd_fetch_history)

    b = sub.add_parser("backtest", help="run the strategy over CSV data")
    b.add_argument("--data", help="directory of <SYMBOL>.csv files")
    b.add_argument("--yahoo", action="store_true", help="download free Yahoo Finance candles instead of reading CSVs")
    b.add_argument("--start")
    b.add_argument("--end")
    b.add_argument("--all-files", action="store_true", help="use every CSV in --data instead of TB_SYMBOLS")
    b.add_argument("--llm", action="store_true", help="enable the LLM filter (look-ahead biased; costs money)")
    b.add_argument("--trades-csv")
    b.add_argument("--json", action="store_true")
    b.set_defaults(func=cmd_backtest)

    sub.add_parser("paper", help="paper trade on live prices (TB_FEED=groww or yahoo); orders are simulated").set_defaults(func=cmd_paper)

    sv = sub.add_parser("serve", help="local API for the dashboard (stands in for Supabase) + job runner")
    sv.add_argument("--host", default="127.0.0.1")
    sv.add_argument("--port", type=int, default=8787)
    sv.add_argument("--no-jobs", action="store_true")
    sv.set_defaults(func=cmd_serve)

    jb = sub.add_parser("jobs", help="run dashboard research jobs (backtests, sweeps)")
    jb.add_argument("--once", action="store_true", help="run what is queued, then exit")
    jb.set_defaults(func=cmd_jobs)

    rp = sub.add_parser("replay", help="replay history through the real engine + paper broker (watch it on the dashboard)")
    rp.add_argument("--data", help="directory of <SYMBOL>.csv files (default: synthetic data)")
    rp.add_argument("--all-files", action="store_true")
    rp.add_argument("--days", type=int, default=20, help="number of sessions (last N for --data)")
    rp.add_argument("--start", default="2026-01-05", help="synthetic data start date")
    rp.add_argument("--seed", type=int, default=7)
    rp.add_argument("--speed", type=float, default=0.0, help="real seconds to wait per bar (0 = as fast as possible)")
    rp.add_argument("--reviewer", choices=("none", "heuristic", "claude", "auto"), default="auto",
                    help="signal reviewer: claude costs money; heuristic is a free rule-based baseline")
    rp.set_defaults(func=cmd_replay)
    tk = sub.add_parser("tick", help="one pass of daily investing, then exit (for cron, Task Scheduler, launchd, CI)")
    tk.add_argument("--live", action="store_true")
    tk.add_argument("--i-understand-the-risks", action="store_true")
    tk.add_argument("--no-jobs", action="store_true", help="do not run queued research jobs afterwards")
    tk.add_argument("--job-seconds", type=float, default=240, help="time budget for queued research jobs")
    tk.set_defaults(func=cmd_tick)
    iv = sub.add_parser("invest", help="daily delivery investing as a long-running worker; paper unless --live")
    iv.add_argument("--live", action="store_true")
    iv.add_argument("--i-understand-the-risks", action="store_true")
    iv.set_defaults(func=cmd_invest)
    ib = sub.add_parser("invest-backtest", help="backtest a daily delivery strategy over many years, after costs and tax")
    ib.add_argument("--strategy", choices=("core_mix", "etf_trend", "etf_rank", "index_trend", "momentum"), default="core_mix")
    ib.add_argument("--years", type=float, default=15)
    ib.add_argument("--end", help="YYYY-MM-DD (default: today)")
    ib.add_argument("--no-tax", action="store_true")
    ib.set_defaults(func=cmd_invest_backtest)
    lv = sub.add_parser("live", help="trade live on Groww (requires static IP + explicit opt-in)")
    lv.add_argument("--i-understand-the-risks", action="store_true")
    lv.set_defaults(func=cmd_live)

    for name, help_ in (("start", "start trading (the paper/live worker waits for this)"),
                        ("stop", "no new trades: investments stay as they are; intraday positions are closed"),
                        ("sell-all", "daily investing: sell every holding the plan manages (stop never does this)"),
                        ("kill", "engage kill switch: flatten and stop new entries"),
                        ("resume", "release kill switch and pause"),
                        ("pause", "stop new entries, keep managing open positions"),
                        ("confirm-login", "confirm today's broker login (daily 2FA policy)")):
        sub.add_parser(name, help=help_).set_defaults(func=cmd_control)
    dp = sub.add_parser("deposit", help="daily investing: record new money; it buys what is furthest below target, selling nothing")
    dp.add_argument("amount", type=float, help="rupees")
    dp.set_defaults(func=cmd_control)
    md = sub.add_parser("mode", help="daily investing: how orders are carried out")
    md.add_argument("mode", choices=("paper", "guided", "auto"),
                    help="paper: simulated. guided: listed for you to place by hand. auto: sent to the broker, "
                         "and only by a worker started with `invest --live`")
    md.set_defaults(func=cmd_control)
    sub.add_parser("check-ip", help="verify this host's public IP is the whitelisted static IP").set_defaults(func=cmd_check_ip)
    lc = sub.add_parser("login-check", help="read-only Groww credential check (login, profile, data plan); never trades")
    lc.add_argument("--fresh", action="store_true", help="ignore the cached token (uses 1 of 150 daily token requests)")
    lc.set_defaults(func=cmd_login_check)
    return p


def main(argv: list[str] | None = None) -> int:
    import os

    args = build_parser().parse_args(argv)
    load_dotenv(os.environ.get("TB_ENV_FILE", ".env"))
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    return args.func(args, _settings())


if __name__ == "__main__":
    raise SystemExit(main())
