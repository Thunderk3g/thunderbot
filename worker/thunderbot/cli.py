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
    client = _groww_client(s)
    md = GrowwMarketData(client, exchange=s.exchange)
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
    md = CSVMarketData(args.data)
    symbols = s.symbols if not args.all_files else md.symbols()
    s.symbols = symbols
    start = datetime.fromisoformat(args.start).replace(tzinfo=IST) if args.start else datetime(2000, 1, 1, tzinfo=IST)
    end = datetime.fromisoformat(args.end).replace(tzinfo=IST) if args.end else datetime(2100, 1, 1, tzinfo=IST)
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
    from .broker.groww import GrowwBroker
    from .broker.paper import PaperBroker
    from .engine import TradingEngine
    from .llm.filter import build_filter
    from .throttle import OrderThrottle

    store = build_store(s.data_path, s.supabase_url, s.supabase_service_key)
    session = _groww_session(s)
    client = _groww_client(s)

    def refresh_token(now: datetime) -> None:
        # Groww tokens expire at 6:00 AM IST; the session reuses its cached token until then.
        token, fresh = session.token()
        if token != client.token:
            client.token = token
            store.event("login", "Groww access token refreshed", at=now.isoformat(), fresh=fresh)

    throttle = OrderThrottle(s.orders_per_second, s.orders_per_minute)
    groww = GrowwBroker(client, throttle, allow_mtf=s.allow_mtf_api, exchange=s.exchange)
    broker = groww if mode == "live" else PaperBroker(s.capital, s.slippage_bps)
    engine = TradingEngine(
        settings=s, broker=broker, quotes=groww, data=GrowwMarketData(client, exchange=s.exchange),
        strategy=_strategy(s), signal_filter=build_filter(s), store=store, mode=mode,
        before_market_tick=refresh_token, filter_factory=build_filter,
        require_login_confirmation=(mode == "live" and s.require_login_confirmation),
    )
    engine.run_forever()
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
        print(f"TB_LOCAL_API_KEY not set; generated one for this session:\n  {key}")
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
    JobRunner(store, s, _groww_factory(s)).run_forever()
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
    if args.command == "kill":
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
    from .broker.base import BrokerError
    from .broker.groww import key_role

    if not s.groww_api_key:
        print("GROWW_API_KEY is not set (put it in worker/.env or /etc/thunderbot.env).", file=sys.stderr)
        return 2
    print(f"API key type: {key_role(s.groww_api_key) or 'unknown'}")
    try:
        session = _groww_session(s)
        token, fresh = session.token(force_refresh=args.fresh)
    except BrokerError as e:
        print(f"Setup problem: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Login failed: {type(e).__name__}: {e}", file=sys.stderr)
        return 1
    print(f"Login OK ({'new token' if fresh else 'cached token'}; token not shown).")
    from growwapi import GrowwAPI

    client = GrowwAPI(token)
    try:
        client.get_user_profile()
        print("Profile: OK")
    except Exception as e:
        print(f"Profile: failed ({type(e).__name__}: {e})")
    try:
        ltp = client.get_ltp(exchange_trading_symbols=("NSE_RELIANCE",), segment="CASH")
        print(f"Live data: OK (RELIANCE LTP {ltp.get('NSE_RELIANCE')})")
    except Exception as e:
        print(f"Live data: unavailable ({type(e).__name__}: {e}). The Live Data API needs a paid Trade API plan.")
    print("No orders were placed. Orders additionally require this host's IP to be whitelisted on Groww.")
    return 0


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

    f = sub.add_parser("fetch-history", help="download candles from Groww into CSV (paid plan required)")
    f.add_argument("--out", default="data/groww")
    f.add_argument("--days", type=int, default=90)
    f.add_argument("--end", help="YYYY-MM-DD (default: now)")
    f.add_argument("--interval", type=int, default=5)
    f.set_defaults(func=cmd_fetch_history)

    b = sub.add_parser("backtest", help="run the strategy over CSV data")
    b.add_argument("--data", required=True, help="directory of <SYMBOL>.csv files")
    b.add_argument("--start")
    b.add_argument("--end")
    b.add_argument("--all-files", action="store_true", help="use every CSV in --data instead of TB_SYMBOLS")
    b.add_argument("--llm", action="store_true", help="enable the LLM filter (look-ahead biased; costs money)")
    b.add_argument("--trades-csv")
    b.add_argument("--json", action="store_true")
    b.set_defaults(func=cmd_backtest)

    sub.add_parser("paper", help="paper trade against live Groww prices").set_defaults(func=cmd_paper)

    sv = sub.add_parser("serve", help="local API for the dashboard (stands in for Supabase) + job runner")
    sv.add_argument("--host", default="127.0.0.1")
    sv.add_argument("--port", type=int, default=8787)
    sv.add_argument("--no-jobs", action="store_true")
    sv.set_defaults(func=cmd_serve)

    sub.add_parser("jobs", help="run dashboard research jobs (backtests, sweeps)").set_defaults(func=cmd_jobs)

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
    lv = sub.add_parser("live", help="trade live on Groww (requires static IP + explicit opt-in)")
    lv.add_argument("--i-understand-the-risks", action="store_true")
    lv.set_defaults(func=cmd_live)

    for name, help_ in (("kill", "engage kill switch: flatten and stop new entries"),
                        ("resume", "release kill switch and pause"),
                        ("pause", "stop new entries, keep managing open positions"),
                        ("confirm-login", "confirm today's broker login (daily 2FA policy)")):
        sub.add_parser(name, help=help_).set_defaults(func=cmd_control)
    sub.add_parser("check-ip", help="verify this host's public IP is the whitelisted static IP").set_defaults(func=cmd_check_ip)
    lc = sub.add_parser("login-check", help="read-only Groww credential check (login, profile, data plan); never trades")
    lc.add_argument("--fresh", action="store_true", help="ignore the cached token (uses 1 of 150 daily token requests)")
    lc.set_defaults(func=cmd_login_check)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    load_dotenv()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    return args.func(args, _settings())


if __name__ == "__main__":
    raise SystemExit(main())
