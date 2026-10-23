"""Research jobs queued from the dashboard: backtests and walk-forward parameter sweeps.

The dashboard inserts a row into ``jobs`` with ``status="queued"``; ``JobRunner``
picks it up, runs it with the same strategy/risk/cost code as live trading, and
writes the result back to the row. Jobs never place orders.

Walk-forward sweeps rank every parameter combination on the first part of the
history (in-sample) and report how the same combination did on the later,
unseen part (out-of-sample). Only configurations that hold up out-of-sample
deserve paper trading; the best in-sample row is usually overfit.
"""

from __future__ import annotations

import itertools
import logging
import time
import traceback
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any

from .backtest import Backtester, BacktestResult
from .clock import IST, now_ist
from .config import Settings
from .costs import CostModel
from .data import CSVMarketData, GrowwMarketData, synthetic_history, write_csv
from .models import Candle
from .store import CompositeStore
from .strategy import STRATEGIES, build_strategy, coerce_params

log = logging.getLogger(__name__)

MAX_SWEEP_COMBOS = 60
MAX_TRADES_IN_RESULT = 300
DATA_SOURCES = ("demo", "yahoo", "csv", "groww")


class JobError(ValueError):
    pass


def _parse_date(value: Any, default: date) -> date:
    if not value:
        return default
    return date.fromisoformat(str(value)[:10])


def _trading_days(start: date, end: date) -> int:
    n, d = 0, start
    while d <= end:
        n += d.weekday() < 5
        d += timedelta(days=1)
    return n


class DataLoader:
    def __init__(self, settings: Settings, groww_client_factory=None) -> None:
        self.s = settings
        self.groww_client_factory = groww_client_factory

    def load(self, source: str, symbols: list[str], start: date, end: date) -> tuple[dict[str, list[Candle]], str]:
        if source not in DATA_SOURCES:
            raise JobError(f"data source must be one of {DATA_SOURCES}")
        interval = self.s.interval_minutes
        if source == "demo":
            days = max(_trading_days(start, end), 5)
            data = synthetic_history(symbols, start, min(days, 500), interval, seed=7)
            return data, "Synthetic random-walk data: no strategy can have a real edge here. Use it to learn the tools."
        start_dt = datetime.combine(start, datetime.min.time(), tzinfo=IST)
        end_dt = datetime.combine(end + timedelta(days=1), datetime.min.time(), tzinfo=IST)
        if source == "yahoo":
            from .yahoo import YahooMarketData

            md = YahooMarketData(exchange=self.s.exchange)
            floor = md.earliest(interval)
            data = {}
            for sym in symbols:
                data[sym] = md.candles(sym, interval, start_dt, end_dt)
                time.sleep(0.2)  # be gentle with a free service
            if not any(data.values()):
                raise JobError(f"Yahoo returned no {interval}-minute candles for these dates. Yahoo keeps "
                               f"{interval}-minute bars only since {floor:%d %b %Y}." if floor else
                               "Yahoo returned no candles for these dates and symbols.")
            clipped = f" Yahoo keeps {interval}-minute bars only since {floor:%d %b %Y}." if floor and start_dt < floor else ""
            return data, ("Free Yahoo Finance candles (real NSE prices, unofficial source)." + clipped +
                          " Yahoo shows zero volume for the 09:15 bar on most days and skips a few bars.")
        if source == "csv":
            md = CSVMarketData(self.s.backtest_data_dir)
            try:
                data = {sym: md.candles(sym, interval, start_dt, end_dt) for sym in symbols}
            except FileNotFoundError as e:
                raise JobError(f"{e}. Run `thunderbot fetch-history --out {self.s.backtest_data_dir}` first.") from e
            return data, f"CSV candles from {self.s.backtest_data_dir}"
        if self.groww_client_factory is None:
            raise JobError("Groww credentials are not configured on the worker")
        md = GrowwMarketData(self.groww_client_factory(), exchange=self.s.exchange)
        data = {}
        for sym in symbols:
            data[sym] = md.candles(sym, interval, start_dt, end_dt)
            write_csv(self.s.data_path / "cache" / "groww" / f"{sym}.csv", data[sym])
            time.sleep(0.2)
        return data, "Groww historical candles"


def _summary(m: dict[str, Any]) -> dict[str, Any]:
    keys = ("trades", "net_pnl", "return_pct", "win_rate_pct", "profit_factor", "max_drawdown_pct",
            "sharpe_daily_annualized", "avg_trade", "total_costs")
    return {k: m.get(k) for k in keys}


def _result_payload(res: BacktestResult) -> dict[str, Any]:
    metrics = res.metrics()
    equity, running = [], res.capital
    for d in sorted(res.daily_pnl):
        running += res.daily_pnl[d]
        equity.append({"date": d.isoformat(), "equity": round(running, 2), "pnl": res.daily_pnl[d]})
    per_symbol: dict[str, dict[str, float]] = defaultdict(lambda: {"trades": 0, "net_pnl": 0.0, "wins": 0})
    for t in res.trades:
        ps = per_symbol[t.symbol]
        ps["trades"] += 1
        ps["net_pnl"] = round(ps["net_pnl"] + t.net_pnl, 2)
        ps["wins"] += t.net_pnl > 0
    trades = [
        {"symbol": t.symbol, "side": t.side.value, "qty": t.qty, "entry": t.entry_price, "exit": t.exit_price,
         "opened_at": t.opened_at.isoformat(), "closed_at": t.closed_at.isoformat(), "reason": t.exit_reason,
         "costs": t.costs, "net_pnl": round(t.net_pnl, 2)}
        for t in res.trades[-MAX_TRADES_IN_RESULT:]
    ]
    return {"metrics": metrics, "equity": equity, "per_symbol": dict(per_symbol), "trades": trades}


def _split_days(data: dict[str, list[Candle]], fraction: float) -> tuple[dict, dict, date | None]:
    days = sorted({c.ts.date() for bars in data.values() for c in bars})
    if len(days) < 10:
        raise JobError("need at least 10 trading days for a walk-forward split")
    cut = days[int(len(days) * fraction)]
    ins = {s: [c for c in bars if c.ts.date() < cut] for s, bars in data.items()}
    oos = {s: [c for c in bars if c.ts.date() >= cut] for s, bars in data.items()}
    return ins, oos, cut


class JobRunner:
    def __init__(self, store: CompositeStore, base_settings: Settings, groww_client_factory=None,
                 poll_seconds: float = 2.0) -> None:
        self.store = store
        self.base = base_settings
        self.loader = DataLoader(base_settings, groww_client_factory)
        self.poll = poll_seconds

    def publish_catalog(self) -> None:
        """Let the dashboard's Lab render even when only the job runner is up."""
        from .strategy import catalog

        from .daily import DAILY_CATALOG

        self.store.set_control("strategy_catalog", catalog())
        self.store.set_control("daily_catalog", DAILY_CATALOG)
        control = self.store.get_control()
        if "effective_settings" not in control:
            new, rejected = self.base.with_overrides(control.get("settings_overrides") or {})
            self.store.set_control("effective_settings", {**new.public_view(), "rejected": rejected})

    def run_forever(self) -> None:
        log.info("job runner started")
        try:
            self.publish_catalog()
        except Exception:
            log.exception("could not publish strategy catalog")
        while True:
            try:
                if not self.run_once():
                    time.sleep(self.poll)
            except Exception:
                log.exception("job loop error")
                time.sleep(self.poll)

    def run_once(self) -> bool:
        queued = self.store.select("jobs", {"status": "queued"}, order="created_at", desc=False, limit=1)
        if not queued:
            return False
        job = queued[0]
        self.store.update("jobs", job["id"], {"status": "running", "started_at": now_ist().isoformat(), "progress": 0.0})
        try:
            result = self.execute(job["kind"], job.get("params") or {},
                                  progress=lambda p: self.store.update("jobs", job["id"], {"progress": round(p, 3)}))
            self.store.update("jobs", job["id"], {"status": "done", "progress": 1.0, "result": result,
                                                  "finished_at": now_ist().isoformat()})
        except JobError as e:
            self.store.update("jobs", job["id"], {"status": "error", "error": str(e), "finished_at": now_ist().isoformat()})
        except Exception as e:
            log.exception("job %s failed", job["id"])
            self.store.update("jobs", job["id"], {"status": "error", "error": f"{type(e).__name__}: {e}",
                                                  "trace": traceback.format_exc()[-2000:],
                                                  "finished_at": now_ist().isoformat()})
        return True

    # Job kinds

    def _settings_for(self, params: dict[str, Any]) -> Settings:
        overrides = dict(params.get("settings") or {})
        overrides["strategy"] = params.get("strategy", self.base.strategy)
        if params.get("symbols"):
            overrides["symbols"] = params["symbols"]
        s, rejected = self.base.with_overrides(overrides)
        if rejected:
            raise JobError(f"invalid settings: {rejected}")
        return s

    def _common(self, params: dict[str, Any]):
        strategy = params.get("strategy", self.base.strategy)
        if strategy not in STRATEGIES:
            raise JobError(f"unknown strategy {strategy!r}")
        s = self._settings_for(params)
        today = now_ist().date()
        end = _parse_date(params.get("end"), today)
        start = _parse_date(params.get("start"), end - timedelta(days=180))
        if start >= end:
            raise JobError("start must be before end")
        data, note = self.loader.load(params.get("data", "demo"), s.symbols, start, end)
        if not any(data.values()):
            raise JobError("no candles in the selected range")
        return strategy, s, data, note

    def execute(self, kind: str, params: dict[str, Any], progress=lambda p: None) -> dict[str, Any]:
        if kind == "backtest":
            return self.backtest(params, progress)
        if kind == "sweep":
            return self.sweep(params, progress)
        if kind == "invest":
            return self.invest(params, progress)
        raise JobError(f"unknown job kind {kind!r}")

    def invest(self, params: dict[str, Any], progress) -> dict[str, Any]:
        """Daily-bar delivery strategy over many years, after Indian costs and capital-gains tax."""
        from . import daily

        name = params.get("strategy", "index_trend")
        try:
            strat = daily.build_daily(name, params.get("strategy_params"))
        except ValueError as e:
            raise JobError(str(e)) from e
        years = min(max(int(params.get("years") or 15), 3), 18)
        capital = min(max(float(params.get("capital") or 500_000), 10_000), 1e9)
        end = now_ist().date()
        start = end - timedelta(days=int(years * 365.25))
        progress(0.1)
        symbols = list(dict.fromkeys([daily.INDEX, daily.BENCHMARK, *getattr(strat, "symbols", []),
                                      getattr(strat, "asset", daily.BENCHMARK)]))
        prices = daily.load_prices(symbols, start - timedelta(days=420), end,
                                   cache_dir=self.base.data_path / "cache" / "daily")
        progress(0.6)
        res = daily.backtest(strat, prices, start, end, capital=capital,
                             tax=daily.CapitalGainsTax() if params.get("tax", True) else None,
                             cash_yield_pct=float(params.get("cash_yield_pct", 6.0)))
        note = ("Daily Yahoo Finance prices, split- and dividend-adjusted, with known bad ticks repaired. "
                "Costs: Groww delivery charges, STT, stamp duty, GST, DP and 0.05% slippage per side. "
                "Tax: 20% on gains held up to 12 months, 12.5% above Rs 1.25 lakh a year after that. "
                "Idle cash earns 6% a year (a liquid fund). The benchmark is NIFTYBEES held throughout, before tax.")
        if name == "momentum":
            note += (" WARNING: the stock list is today's Nifty 100, so stocks that fell out of the index are missing. "
                     "That survivorship bias inflates the result by several points a year.")
        return {**daily.result_payload(res), "strategy": name, "strategy_params": params.get("strategy_params") or {},
                "data_note": note, "years": years, "capital": capital}

    def backtest(self, params: dict[str, Any], progress) -> dict[str, Any]:
        strategy, s, data, note = self._common(params)
        sp = coerce_params(strategy, params.get("strategy_params"))
        progress(0.2)
        res = Backtester(s, build_strategy(strategy, sp, s.allow_short), CostModel()).run(data)
        return {**_result_payload(res), "strategy": strategy, "strategy_params": sp, "data_note": note}

    def sweep(self, params: dict[str, Any], progress) -> dict[str, Any]:
        strategy, s, data, note = self._common(params)
        base_params = coerce_params(strategy, params.get("strategy_params"))
        grid = params.get("grid") or {}
        specs = {p["name"] for p in STRATEGIES[strategy].param_specs}
        axes = []
        for name, values in grid.items():
            if name not in specs:
                raise JobError(f"{name} is not a parameter of {strategy}")
            vals = sorted({coerce_params(strategy, {name: v})[name] for v in values})
            if vals:
                axes.append((name, vals))
        if not axes:
            raise JobError("pick at least one parameter with values to sweep")
        combos = list(itertools.product(*[vals for _, vals in axes]))
        if len(combos) > MAX_SWEEP_COMBOS:
            raise JobError(f"{len(combos)} combinations; the limit is {MAX_SWEEP_COMBOS}")
        fraction = min(max(float(params.get("in_sample_fraction", 0.7)), 0.5), 0.9)
        ins, oos, cut = _split_days(data, fraction)

        rows = []
        for i, combo in enumerate(combos):
            sp = {**base_params, **dict(zip([n for n, _ in axes], combo, strict=True))}
            r_in = Backtester(s, build_strategy(strategy, sp, s.allow_short), CostModel()).run(ins).metrics()
            r_out = Backtester(s, build_strategy(strategy, sp, s.allow_short), CostModel()).run(oos).metrics()
            robust = (r_out["net_pnl"] > 0 and (r_out["profit_factor"] or 0) >= 1.1 and r_out["trades"] >= 20
                      and r_in["net_pnl"] > 0)
            rows.append({"params": sp, "in_sample": _summary(r_in), "out_of_sample": _summary(r_out), "robust": robust})
            progress((i + 1) / len(combos))
        rows.sort(key=lambda r: r["in_sample"]["net_pnl"], reverse=True)
        return {
            "strategy": strategy, "axes": [{"name": n, "values": v} for n, v in axes], "rows": rows,
            "split_date": cut.isoformat() if cut else None, "in_sample_fraction": fraction, "data_note": note,
            "robust_count": sum(r["robust"] for r in rows),
        }
