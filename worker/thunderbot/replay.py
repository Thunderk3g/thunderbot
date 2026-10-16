"""Replay historical candles through the *real* trading engine and paper broker.

Unlike the backtester (a fast bar-level simulation), replay drives
``TradingEngine.tick`` with a simulated clock and intra-bar prices
(open -> low/high -> high/low -> close), so every journal row, heartbeat,
dashboard update, kill switch and settings change behaves exactly as in paper
trading, only faster. Use ``speed`` to watch it unfold on the dashboard.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from datetime import date, datetime, timedelta
from datetime import time as dtime

from .broker.paper import PaperBroker
from .clock import IST, MARKET_CLOSE, MARKET_OPEN
from .config import Settings
from .costs import CostModel
from .data import group_by_day
from .engine import TradingEngine
from .llm.filter import SignalFilter
from .models import Candle
from .store import CompositeStore
from .strategy import build_strategy

log = logging.getLogger(__name__)


class DictMarketData:
    def __init__(self, data: dict[str, list[Candle]]) -> None:
        self.data = data

    def candles(self, symbol: str, interval_minutes: int, start: datetime, end: datetime) -> list[Candle]:
        return [c for c in self.data.get(symbol, []) if start <= c.ts < end]


class ReplayQuotes:
    def __init__(self) -> None:
        self.prices: dict[str, float] = {}

    def ltp(self, symbols: list[str]) -> dict[str, float]:
        return {s: self.prices[s] for s in symbols if s in self.prices}


def _intrabar_path(c: Candle) -> list[float]:
    # Up bars are assumed to dip first, down bars to pop first: the usual conservative ordering.
    return [c.open, c.low, c.high, c.close] if c.close >= c.open else [c.open, c.high, c.low, c.close]


def run_replay(
    settings: Settings,
    data: dict[str, list[Candle]],
    store: CompositeStore,
    signal_filter: SignalFilter,
    speed: float = 0.0,
    filter_factory: Callable[[Settings], SignalFilter] | None = None,
    on_day: Callable[[date], None] | None = None,
    should_stop: Callable[[], bool] = lambda: False,
) -> TradingEngine:
    quotes = ReplayQuotes()
    clock_now = [datetime.now(IST)]
    engine = TradingEngine(
        settings=settings, broker=PaperBroker(settings.capital, settings.slippage_bps), quotes=quotes,
        data=DictMarketData(data), strategy=build_strategy(settings.strategy, settings.strategy_params, settings.allow_short),
        signal_filter=signal_filter, store=store, mode="replay", costs=CostModel(),
        now_fn=lambda: clock_now[0], sleep_fn=lambda _: None, filter_factory=filter_factory,
        equity_interval_seconds=60 * settings.interval_minutes,
    )
    engine.publish_static()
    store.event("engine_start", "replay started", symbols=settings.symbols, speed=speed)
    by_day: dict[date, dict[str, list[Candle]]] = {}
    for sym, bars in data.items():
        for d, day_bars in group_by_day(bars).items():
            by_day.setdefault(d, {})[sym] = day_bars
    step = timedelta(minutes=settings.interval_minutes)

    for d in sorted(by_day):
        if should_stop():
            break
        if on_day:
            on_day(d)
        sessions = by_day[d]
        clock_now[0] = datetime.combine(d, dtime(9, 0), tzinfo=IST)
        engine.tick()  # roll the day before the open
        timeline = sorted({c.ts for bars in sessions.values() for c in bars})
        index = {sym: {c.ts: c for c in bars} for sym, bars in sessions.items()}
        for t in timeline:
            if should_stop():
                break
            paths = {sym: _intrabar_path(idx[t]) for sym, idx in index.items() if t in idx}
            # three intra-bar ticks inside the bar, then one just after it closes
            offsets = [step * 0.2, step * 0.4, step * 0.6, step + timedelta(seconds=5)]
            for k, off in enumerate(offsets):
                clock_now[0] = t + off
                for sym, path in paths.items():
                    quotes.prices[sym] = path[k]
                engine.tick()
            if speed > 0:
                time.sleep(speed)
        clock_now[0] = datetime.combine(d, MARKET_CLOSE, tzinfo=IST) + timedelta(minutes=1)
        engine.tick()
    store.event("engine_stop", "replay finished")
    return engine


__all__ = ["run_replay", "DictMarketData", "ReplayQuotes", "MARKET_OPEN"]
