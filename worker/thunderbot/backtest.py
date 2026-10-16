"""Bar-by-bar backtester sharing the live engine's strategy, risk and cost code.

Simulation rules (conservative by design):
- A signal generated on bar *t*'s close is filled at bar *t+1*'s open plus slippage.
- If a single bar touches both stop and target, the stop is assumed to hit first.
- A gap through the stop exits at the open, not at the stop price.
- Positions are flattened at the first bar starting at or after ``flatten_at``.
- Costs come from ``CostModel`` on both legs.

The LLM filter is off by default here. LLMs have seen historical prices in
training, so an LLM-filtered backtest suffers look-ahead bias. Use
paper trading to evaluate the LLM layer instead.
"""

from __future__ import annotations

import math
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any

from .clock import MarketClock
from .config import Settings
from .costs import CostModel
from .data import group_by_day
from .llm.filter import PassThroughFilter, SignalFilter
from .llm.types import ReviewContext
from .models import Candle, ClosedTrade, ManagedPosition, Side, Signal
from .risk import RiskManager
from .strategy.base import Strategy


@dataclass
class _Pending:
    signal: Signal
    qty: int


@dataclass
class BacktestResult:
    trades: list[ClosedTrade]
    daily_pnl: dict[date, float]
    capital: float
    signals: int = 0
    rejected: dict[str, int] = field(default_factory=dict)

    def metrics(self) -> dict[str, Any]:
        trades = self.trades
        net = [t.net_pnl for t in trades]
        wins = [x for x in net if x > 0]
        losses = [x for x in net if x <= 0]
        equity, peak, max_dd = self.capital, self.capital, 0.0
        for d in sorted(self.daily_pnl):
            equity += self.daily_pnl[d]
            peak = max(peak, equity)
            max_dd = max(max_dd, peak - equity)
        daily_returns = [self.daily_pnl[d] / self.capital for d in sorted(self.daily_pnl)]
        sharpe = None
        if len(daily_returns) > 1 and statistics.pstdev(daily_returns) > 0:
            sharpe = statistics.mean(daily_returns) / statistics.pstdev(daily_returns) * math.sqrt(252)
        gross_loss = -sum(losses)
        return {
            "days": len(self.daily_pnl),
            "signals": self.signals,
            "trades": len(trades),
            "net_pnl": round(sum(net), 2),
            "gross_pnl": round(sum(t.gross_pnl for t in trades), 2),
            "total_costs": round(sum(t.costs for t in trades), 2),
            "return_pct": round(sum(net) / self.capital * 100, 2),
            "win_rate_pct": round(len(wins) / len(trades) * 100, 1) if trades else 0.0,
            "profit_factor": round(sum(wins) / gross_loss, 2) if gross_loss > 0 else None,
            "avg_trade": round(sum(net) / len(trades), 2) if trades else 0.0,
            "max_drawdown": round(max_dd, 2),
            "max_drawdown_pct": round(max_dd / self.capital * 100, 2),
            "sharpe_daily_annualized": round(sharpe, 2) if sharpe is not None else None,
            "losing_days_pct": round(
                sum(1 for v in self.daily_pnl.values() if v < 0) / len(self.daily_pnl) * 100, 1
            ) if self.daily_pnl else 0.0,
            "exit_reasons": dict(_count(t.exit_reason for t in trades)),
            "rejections": dict(sorted(self.rejected.items(), key=lambda kv: -kv[1])),
        }


def _count(items) -> dict[str, int]:
    out: dict[str, int] = defaultdict(int)
    for i in items:
        out[i] += 1
    return out


def _rejection_key(reason: str) -> str:
    return reason.split(":")[0].split("(")[0].strip()


PRIOR_BARS = 400  # ~5 sessions of 5-minute bars, for ATR and time-of-day volume baselines


class Backtester:
    def __init__(
        self,
        settings: Settings,
        strategy: Strategy,
        costs: CostModel | None = None,
        signal_filter: SignalFilter | None = None,
        clock: MarketClock | None = None,
    ) -> None:
        self.s = settings
        self.strategy = strategy
        self.costs = costs or CostModel()
        self.filter = signal_filter or PassThroughFilter()
        self.clock = clock or settings.clock()
        self.slip = settings.slippage_bps / 10_000.0

    def run(self, data: dict[str, list[Candle]]) -> BacktestResult:
        by_symbol_day = {sym: group_by_day(bars) for sym, bars in data.items()}
        all_days = sorted({d for days in by_symbol_day.values() for d in days})
        risk = RiskManager(self.s, self.clock)
        trades: list[ClosedTrade] = []
        daily: dict[date, float] = {}
        rejected: dict[str, int] = defaultdict(int)
        n_signals = 0
        prior: dict[str, list[Candle]] = {sym: [] for sym in data}
        interval = timedelta(minutes=self.s.interval_minutes)

        for day in all_days:
            if not self.clock.is_trading_day(day):
                continue
            self.strategy.reset_day()
            sessions = {sym: days.get(day, []) for sym, days in by_symbol_day.items()}
            first_ts = min((b[0].ts for b in sessions.values() if b), default=None)
            if first_ts is None:
                continue
            risk.roll_day(first_ts)
            open_pos: dict[str, ManagedPosition] = {}
            pending: dict[str, _Pending] = {}
            day_trades: list[ClosedTrade] = []
            index = {sym: {b.ts: i for i, b in enumerate(bars)} for sym, bars in sessions.items()}
            timeline = sorted({b.ts for bars in sessions.values() for b in bars})

            def close(sym: str, price: float, ts: datetime, reason: str,
                      open_pos=open_pos, day_trades=day_trades) -> None:
                pos = open_pos.pop(sym)
                cost = self.costs.round_trip(pos.side, pos.qty, pos.entry_price, price, pos.product)
                t = ClosedTrade(pos.symbol, pos.side, pos.product, pos.qty, pos.entry_price, round(price, 2),
                                pos.opened_at, ts, reason, cost, self.strategy.name)
                day_trades.append(t)
                risk.record_close(t.net_pnl)

            for ts in timeline:
                flatten_bar = self.clock.should_flatten(ts)
                for sym, bars in sessions.items():
                    i = index[sym].get(ts)
                    if i is None:
                        continue
                    bar = bars[i]

                    # 1) fill pending entry at this bar's open
                    if sym in pending:
                        p = pending.pop(sym)
                        sig = p.signal
                        fill = bar.open * (1 + self.slip * sig.side.sign)
                        invalid = (
                            flatten_bar
                            or (sig.side is Side.BUY and not (sig.stop < fill < sig.target))
                            or (sig.side is Side.SELL and not (sig.target < fill < sig.stop))
                        )
                        if invalid:
                            rejected["gapped past stop/target before fill"] += 1
                        else:
                            open_pos[sym] = ManagedPosition(sym, sig.side, sig.product, p.qty, round(fill, 2),
                                                            sig.stop, sig.target, ts, entry_order_id="bt")
                            risk.record_open()

                    # 2) manage open position on this bar
                    if sym in open_pos:
                        # A position entered at this bar's open is checked against the same bar's range.
                        pos = open_pos[sym]
                        long = pos.side is Side.BUY
                        slip = -self.slip if long else self.slip

                        def adverse(px: float, slip: float = slip) -> float:
                            return px * (1 + slip)

                        if flatten_bar:
                            close(sym, adverse(bar.open), ts, "eod_flatten")
                        elif (long and bar.open <= pos.stop) or (not long and bar.open >= pos.stop):
                            close(sym, adverse(bar.open), ts, "stop_gap")
                        elif (long and bar.low <= pos.stop) or (not long and bar.high >= pos.stop):
                            close(sym, adverse(pos.stop), ts, "stop")
                        elif (long and bar.open >= pos.target) or (not long and bar.open <= pos.target):
                            close(sym, bar.open, ts, "target_gap")
                        elif (long and bar.high >= pos.target) or (not long and bar.low <= pos.target):
                            close(sym, pos.target, ts, "target")

                # 3) daily loss check at bar close
                unreal = 0.0
                for sym, pos in open_pos.items():
                    i = index[sym].get(ts)
                    if i is not None:
                        unreal += pos.unrealized(sessions[sym][i].close)
                if risk.check_daily_loss(unreal) and open_pos:
                    for sym in list(open_pos):
                        i = index[sym].get(ts)
                        px = sessions[sym][i].close if i is not None else open_pos[sym].entry_price
                        close(sym, px, ts, "daily_loss_halt")
                    pending.clear()

                # 4) new signals on this bar's close
                close_time = ts + interval
                for sym, bars in sessions.items():
                    i = index[sym].get(ts)
                    if i is None or sym in open_pos or sym in pending:
                        continue
                    sig = self.strategy.on_bar(sym, bars[: i + 1], prior[sym])
                    if sig is None:
                        continue
                    n_signals += 1
                    decision = None
                    if self.filter.enabled:
                        decision = self.filter.review(ReviewContext(sig, bars[max(0, i - 11): i + 1],
                                                                    day_realized_pnl=risk.state.realized_pnl,
                                                                    trades_today=risk.state.trades_opened))
                    book = {**open_pos, **{k: _as_placeholder(v) for k, v in pending.items()}}
                    verdict = risk.evaluate(sig, decision, book, close_time)
                    if verdict.approved:
                        pending[sym] = _Pending(sig, verdict.qty)
                    else:
                        rejected[_rejection_key(verdict.reasons[-1])] += 1

            # safety: close anything still open at the last bar of the day
            for sym in list(open_pos):
                bars = sessions[sym]
                if bars:
                    close(sym, bars[-1].close, bars[-1].ts, "session_end")

            daily[day] = round(sum(t.net_pnl for t in day_trades), 2)
            trades.extend(day_trades)
            for sym, bars in sessions.items():
                prior[sym] = (prior[sym] + bars)[-PRIOR_BARS:]

        return BacktestResult(trades, daily, self.s.capital, n_signals, dict(rejected))


def _as_placeholder(p: _Pending) -> ManagedPosition:
    s = p.signal
    return ManagedPosition(s.symbol, s.side, s.product, p.qty, s.entry, s.stop, s.target, s.ts, entry_order_id="pending")


def format_report(metrics: dict[str, Any]) -> str:
    lines = ["Backtest results", "=" * 40]
    for k, v in metrics.items():
        if isinstance(v, dict):
            lines.append(f"{k}:")
            for kk, vv in v.items():
                lines.append(f"    {kk}: {vv}")
        else:
            lines.append(f"{k:>26}: {v}")
    return "\n".join(lines)
