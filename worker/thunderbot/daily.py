"""Daily-bar portfolio strategies for delivery (CNC) investing, with an honest backtester.

Why this exists: intraday strategies lost money in our tests, and SEBI's studies say most intraday
traders lose. Slow, rules-based delivery strategies have long public track records instead
(trend filters on the index, cross-sectional momentum in the style of NSE's Nifty200 Momentum 30).

The backtester:
- decides on day t's close and trades at day t+1's close (no look-ahead),
- charges Indian delivery costs per order (brokerage, STT, exchange, SEBI, stamp, GST, DP),
- optionally charges capital-gains tax on every sale (STCG within 12 months, LTCG after, with the
  yearly LTCG exemption), so results are after tax, not just after costs,
- reports CAGR, volatility, max drawdown, yearly returns and a buy-and-hold benchmark.

Prices come from Yahoo Finance (split- and dividend-adjusted closes). Known bias: a stock universe
built from today's index members ignores companies that dropped out (survivorship bias), which
flatters stock-picking strategies. The index-trend strategy has no such bias.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

# Prices: {symbol: {date: adjusted close}} on a shared trading calendar.
Prices = dict[str, dict[date, float]]

BENCHMARK = "NIFTYBEES"  # Nifty 50 ETF; its adjusted price approximates the Nifty 50 total return
INDEX = "^NSEI"  # Nifty 50 index (price), used for the market trend filter
CASH = "CASH"


# Costs and taxes


@dataclass
class DeliveryCosts:
    """Groww delivery (CNC) charges per order on NSE, as of October 2026.

    Brokerage min(Rs 20, 0.1%), floored at min(Rs 5, 2.5%); STT 0.1% on each side for stocks but
    0.001% on the sell side only for equity ETFs; NSE charges 0.00307%; SEBI 0.0001%; stamp duty
    0.015% on buys; GST 18% on brokerage, exchange, SEBI and DP charges; DP Rs 23.60 per scrip
    sold per day. Sources: docs research notes (costs_and_taxes.md).
    """

    exchange_pct: float = 0.0000307
    sebi_pct: float = 0.000001
    stamp_buy_pct: float = 0.00015
    gst_pct: float = 0.18
    dp_per_sell: float = 23.60
    stock_stt_pct: float = 0.001
    etf_sell_stt_pct: float = 0.00001
    slippage_pct: float = 0.0005  # per side: spread and impact; ~0.02-0.05% on Nifty 50 names
    etfs: frozenset[str] = frozenset({"NIFTYBEES", "JUNIORBEES", "BANKBEES", "LIQUIDBEES", "GOLDBEES", "SETFNIF50"})

    @staticmethod
    def brokerage(value: float) -> float:
        b = min(20.0, 0.001 * value)
        return b if b >= 5.0 else min(5.0, 0.025 * value)

    def order(self, value: float, buy: bool, symbol: str = "") -> float:
        if value <= 0:
            return 0.0
        b = self.brokerage(value)
        fees = value * (self.exchange_pct + self.sebi_pct)
        etf = symbol in self.etfs
        stt = (0.0 if buy else value * self.etf_sell_stt_pct) if etf else value * self.stock_stt_pct
        cost = b + fees + stt + value * self.slippage_pct
        if buy:
            cost += value * self.stamp_buy_pct + self.gst_pct * (b + fees)
        else:
            cost += self.dp_per_sell + self.gst_pct * (b + fees)  # DP already includes its GST
        return cost


@dataclass
class CapitalGainsTax:
    """Listed equity, Budget 2024 rates (sales on or after 23 July 2024)."""

    stcg_rate: float = 0.20  # held 12 months or less
    ltcg_rate: float = 0.125  # held more than 12 months ...
    ltcg_exempt: float = 125_000.0  # ... on gains above Rs 1.25 lakh per financial year
    cess: float = 0.04  # health and education cess on the tax

    def year_tax(self, stcg: float, ltcg: float) -> float:
        """Tax for one financial year. Losses offset gains (STCL against both, LTCL against LTCG only)."""
        if stcg < 0:
            ltcg += stcg
            stcg = 0.0
        tax = max(stcg, 0.0) * self.stcg_rate + max(ltcg - self.ltcg_exempt, 0.0) * self.ltcg_rate
        return tax * (1 + self.cess)


def financial_year(d: date) -> int:
    return d.year if d.month >= 4 else d.year - 1


# Data


def load_prices(symbols: list[str], start: date, end: date, cache_dir: Path | None = None,
                downloader: Callable[..., Any] | None = None) -> Prices:
    """Daily adjusted closes from Yahoo Finance. Index symbols start with ^; others get the .NS suffix."""
    import pandas as pd

    def ticker(s: str) -> str:
        return s if s.startswith("^") or "." in s else f"{s}.NS"

    cache = cache_dir / f"daily_{start}_{end}.pkl" if cache_dir else None
    frame = None
    if cache and cache.exists():
        frame = pd.read_pickle(cache)
        if not all(ticker(s) in frame.columns.get_level_values(0) for s in symbols):
            frame = None
    if frame is None:
        if downloader is None:
            import yfinance as yf

            def downloader(**kw):
                return yf.download(progress=False, auto_adjust=True, threads=True, **kw)
        frame = downloader(tickers=[ticker(s) for s in symbols], start=start.isoformat(),
                           end=(end + timedelta(days=1)).isoformat(), interval="1d", group_by="ticker",
                           multi_level_index=True)
        if cache:
            cache.parent.mkdir(parents=True, exist_ok=True)
            frame.to_pickle(cache)
    out: Prices = {}
    for s in symbols:
        try:
            closes = frame[ticker(s)]["Close"].dropna()
        except KeyError:
            continue
        series = {ts.date(): float(v) for ts, v in closes.items() if v > 0}
        if series:
            out[s], _ = clean_series(series)
    return out


SPLIT_RATIOS = (2, 3, 4, 5, 10, 1 / 2, 1 / 3, 1 / 4, 1 / 5, 1 / 10, 3 / 2, 2 / 3)


def clean_series(series: dict[date, float], spike: float = 0.30, window: int = 4) -> tuple[dict[date, float], list[str]]:
    """Repair the two Yahoo errors we see on NSE data.

    1. Short spikes: a few days far from the surrounding prices that then revert (bad ticks, a split
       applied late). A day more than `spike` away from the median of its 2*window neighbours is dropped.
    2. Persistent split-sized jumps: an unadjusted split or bonus. History before it is rescaled.
    """
    days = sorted(series)
    vals = [series[d] for d in days]
    notes: list[str] = []
    keep = []
    for i, v in enumerate(vals):
        nb = sorted(vals[max(0, i - window):i] + vals[i + 1:i + 1 + window])
        med = nb[len(nb) // 2] if nb else v
        if med > 0 and abs(v / med - 1) > spike:
            notes.append(f"dropped spike {days[i]} ({v:.2f} vs {med:.2f})")
            continue
        keep.append(i)
    days = [days[i] for i in keep]
    vals = [vals[i] for i in keep]
    for i in range(len(vals) - 1, 0, -1):
        r = vals[i] / vals[i - 1]
        if abs(math.log(r)) < math.log(1.4):
            continue
        ratio = next((k for k in SPLIT_RATIOS if abs(r / k - 1) < 0.04), None)
        if ratio is not None:
            vals[:i] = [x * ratio for x in vals[:i]]
            notes.append(f"back-adjusted {days[i]} by {ratio:.3f}")
    return dict(zip(days, vals, strict=True)), notes


def calendar(prices: Prices, anchor: str) -> list[date]:
    if anchor not in prices:
        raise ValueError(f"no price data for {anchor}")
    return sorted(prices[anchor])


# Signals


def sma(values: list[float], n: int) -> float | None:
    return sum(values[-n:]) / n if len(values) >= n else None


def momentum_scores(history: dict[str, list[float]], lookbacks: tuple[int, ...] = (126, 252),
                    vol_window: int = 252) -> dict[str, float]:
    """NSE-style normalized momentum: each lookback's return divided by annualized volatility,
    z-scored across stocks, then averaged. Needs a full year of history per stock."""
    need = max(*lookbacks, vol_window) + 1
    raw: dict[int, dict[str, float]] = {lb: {} for lb in lookbacks}
    for sym, px in history.items():
        if len(px) < need or px[-1] <= 0:
            continue
        rets = [math.log(px[i] / px[i - 1]) for i in range(len(px) - vol_window, len(px)) if px[i - 1] > 0]
        if len(rets) < vol_window * 0.9:
            continue
        mean = sum(rets) / len(rets)
        vol = math.sqrt(sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)) * math.sqrt(252)
        if vol <= 0:
            continue
        for lb in lookbacks:
            raw[lb][sym] = (px[-1] / px[-1 - lb] - 1) / vol
    common = set.intersection(*(set(v) for v in raw.values())) if raw else set()
    scores: dict[str, float] = {s: 0.0 for s in common}
    for lb, vals in raw.items():
        xs = [vals[s] for s in common]
        if len(xs) < 2:
            continue
        mu = sum(xs) / len(xs)
        sd = math.sqrt(sum((x - mu) ** 2 for x in xs) / (len(xs) - 1)) or 1.0
        for s in common:
            scores[s] += (vals[s] - mu) / sd / len(raw)
    return scores


# Strategies: each returns target weights for the next session, given history up to today.

RebalanceRule = Callable[[date, date | None], bool]


def month_end(d: date, nxt: date | None) -> bool:
    return nxt is None or nxt.month != d.month


def quarter_end(d: date, nxt: date | None) -> bool:
    return month_end(d, nxt) and d.month in (3, 6, 9, 12)


def half_year_end(d: date, nxt: date | None) -> bool:
    return month_end(d, nxt) and d.month in (6, 12)


def week_end(d: date, nxt: date | None) -> bool:
    return nxt is None or nxt.isocalendar()[1] != d.isocalendar()[1]


REBALANCE: dict[str, RebalanceRule] = {"weekly": week_end, "monthly": month_end, "quarterly": quarter_end,
                                       "semiannual": half_year_end}


@dataclass
class IndexTrend:
    """Hold the Nifty 50 ETF while Nifty is above its N-day average; hold cash otherwise.
    Checked at each rebalance date. A buffer avoids flipping on every touch of the average."""

    sma_days: int = 200
    buffer_pct: float = 1.0
    rebalance: str = "monthly"  # month-end checks: fewer whipsaws than weekly or daily checks
    asset: str = BENCHMARK
    name: str = "index_trend"

    def universe(self) -> list[str]:
        return [INDEX, self.asset]

    def target(self, d: date, hist: dict[str, list[float]], current: dict[str, float]) -> dict[str, float] | None:
        idx = hist.get(INDEX, [])
        avg = sma(idx, self.sma_days)
        if avg is None or self.asset not in hist:
            return None
        invested = current.get(self.asset, 0) > 0
        up = idx[-1] > avg * (1 + self.buffer_pct / 100)
        down = idx[-1] < avg * (1 - self.buffer_pct / 100)
        if up or (invested and not down):
            return {self.asset: 1.0}
        return {}


@dataclass
class MomentumRotation:
    """Hold the top-N stocks by normalized 6- and 12-month momentum, equal weight.
    Optional market filter: no new buys, and move to cash, while Nifty is below its N-day average.
    Hysteresis: a holding is kept while it ranks within the top `keep_rank`, to cut turnover."""

    symbols: list[str] = field(default_factory=list)
    top_n: int = 15
    keep_rank: int = 25
    rebalance: str = "monthly"  # how often the market filter is checked
    rank_every: str = "quarterly"  # how often stocks are re-ranked: monthly | quarterly | semiannual
    trend_filter: bool = True
    trend_sma_days: int = 200
    name: str = "momentum"

    def universe(self) -> list[str]:
        return [INDEX, *self.symbols]

    def target(self, d: date, hist: dict[str, list[float]], current: dict[str, float]) -> dict[str, float] | None:
        if self.trend_filter:
            idx = hist.get(INDEX, [])
            avg = sma(idx, self.trend_sma_days)
            if avg is None:
                return None
            if idx[-1] < avg:
                return {}
        held = {s: w for s, w in current.items() if w > 0}
        ranking_day = self.rank_every == "monthly" or (
            self.rank_every == "quarterly" and d.month in (3, 6, 9, 12)) or (
            self.rank_every == "semiannual" and d.month in (6, 12))
        if held and not ranking_day:
            return None  # keep the holdings until the next ranking date
        scores = momentum_scores({s: hist[s] for s in self.symbols if s in hist})
        if len(scores) < self.top_n:
            return None
        ranked = sorted(scores, key=scores.get, reverse=True)
        keep = [s for s in ranked[: self.keep_rank] if current.get(s, 0) > 0][: self.top_n]
        picks = keep + [s for s in ranked if s not in keep][: self.top_n - len(keep)]
        return {s: 1.0 / len(picks) for s in picks}


# Backtest


@dataclass
class Lot:
    qty: float
    cost: float  # total cost basis incl. buy charges
    since: date


@dataclass
class DailyResult:
    strategy: str
    start: date
    end: date
    equity: list[tuple[date, float]]
    benchmark: list[tuple[date, float]]
    trades: int
    costs: float
    taxes: float
    turnover: float
    exposure: float
    rebalances: int

    def metrics(self) -> dict[str, Any]:
        return {**_stats(self.equity), "trades": self.trades, "costs": round(self.costs, 2),
                "taxes": round(self.taxes, 2), "turnover_per_year": round(self.turnover, 2),
                "time_invested_pct": round(self.exposure * 100, 1), "rebalances": self.rebalances,
                "benchmark": _stats(self.benchmark)}

    def yearly(self) -> list[dict[str, Any]]:
        def by_year(series):
            out, last = {}, None
            for d, v in series:
                if last is not None and d.year != last[0].year:
                    out[last[0].year] = last[1]
                last = (d, v)
            if last:
                out[last[0].year] = last[1]
            return out
        eq, bm = by_year(self.equity), by_year(self.benchmark)
        rows, prev_e, prev_b = [], self.equity[0][1], self.benchmark[0][1]
        for y in sorted(eq):
            rows.append({"year": y, "strategy_pct": round((eq[y] / prev_e - 1) * 100, 1),
                         "benchmark_pct": round((bm[y] / prev_b - 1) * 100, 1) if y in bm else None})
            prev_e, prev_b = eq[y], bm.get(y, prev_b)
        return rows


def _stats(series: list[tuple[date, float]]) -> dict[str, Any]:
    if len(series) < 2:
        return {}
    (d0, v0), (d1, v1) = series[0], series[-1]
    years = max((d1 - d0).days / 365.25, 1e-9)
    rets = [series[i][1] / series[i - 1][1] - 1 for i in range(1, len(series))]
    mean = sum(rets) / len(rets)
    sd = math.sqrt(sum((r - mean) ** 2 for r in rets) / max(len(rets) - 1, 1))
    peak, mdd, peak_d, longest = v0, 0.0, d0, 0
    for d, v in series:
        if v >= peak:
            longest = max(longest, (d - peak_d).days)
            peak, peak_d = v, d
        mdd = min(mdd, v / peak - 1)
    longest = max(longest, (d1 - peak_d).days)
    cagr = (v1 / v0) ** (1 / years) - 1
    return {"cagr_pct": round(cagr * 100, 2), "total_return_pct": round((v1 / v0 - 1) * 100, 1),
            "volatility_pct": round(sd * math.sqrt(252) * 100, 2),
            "sharpe": round(mean / sd * math.sqrt(252), 2) if sd else None,
            "max_drawdown_pct": round(mdd * 100, 2), "longest_underwater_days": longest,
            "final_value": round(v1, 2), "years": round(years, 2)}


def backtest(strategy: Any, prices: Prices, start: date, end: date, capital: float = 500_000.0,
             costs: DeliveryCosts | None = None, tax: CapitalGainsTax | None = None,
             cash_yield_pct: float = 0.0, min_trade: float = 1_000.0) -> DailyResult:
    """Simulate the strategy day by day. Decisions use closes up to day t; trades fill at t+1's close."""
    costs = costs or DeliveryCosts()
    days = [d for d in calendar(prices, INDEX if INDEX in prices else BENCHMARK)]
    hist: dict[str, list[float]] = {s: [] for s in prices}
    last_px: dict[str, float] = {}
    lots: dict[str, Lot] = {}
    cash = capital
    pending: dict[str, float] | None = None
    equity, bench = [], []
    trades = 0
    total_costs = total_tax = traded = 0.0
    invested_days = 0
    rebalances = 0
    gains: dict[int, list[float]] = {}  # fy -> [stcg, ltcg]
    rule = REBALANCE[strategy.rebalance]
    daily_cash = (1 + cash_yield_pct / 100) ** (1 / 252) - 1
    bench_units = None
    started = False

    def value() -> float:
        return cash + sum(lot.qty * last_px.get(s, 0) for s, lot in lots.items())

    def settle_tax(fy: int) -> None:
        nonlocal cash, total_tax
        if tax and fy in gains:
            t = tax.year_tax(*gains.pop(fy))
            cash -= t
            total_tax += t

    for i, d in enumerate(days):
        for s, series in prices.items():
            px = series.get(d)
            if px is not None:
                hist[s].append(px)
                last_px[s] = px
        if d > end:
            break
        if d < start:
            continue
        if not started:
            started = True
            bench_units = capital / last_px[BENCHMARK] if BENCHMARK in last_px else None
        # Pay last financial year's tax at the first trading day of a new one.
        if tax and i > 0 and financial_year(d) != financial_year(days[i - 1]):
            settle_tax(financial_year(days[i - 1]))
        cash *= 1 + daily_cash
        # Execute yesterday's decision at today's close.
        if pending is not None:
            total = value()
            want = {s: w * total for s, w in pending.items() if s in last_px}
            for s in list(lots):  # sells first, to free cash
                lot = lots[s]
                target_val = want.get(s, 0.0)
                cur_val = lot.qty * last_px[s]
                if cur_val - target_val > min_trade or (target_val == 0 and cur_val > 0):
                    sell_val = cur_val - target_val
                    frac = sell_val / cur_val
                    c = costs.order(sell_val, buy=False, symbol=s)
                    basis = lot.cost * frac
                    gain = sell_val - c - basis
                    fy = financial_year(d)
                    g = gains.setdefault(fy, [0.0, 0.0])
                    g[0 if (d - lot.since).days <= 365 else 1] += gain
                    cash += sell_val - c
                    total_costs += c
                    traded += sell_val
                    trades += 1
                    lot.qty -= lot.qty * frac
                    lot.cost -= basis
                    if lot.qty * last_px[s] < 1:
                        del lots[s]
            for s, target_val in want.items():  # then buys
                cur_val = lots[s].qty * last_px[s] if s in lots else 0.0
                buy_val = min(target_val - cur_val, cash / (1 + 0.004))
                if buy_val > min_trade:
                    c = costs.order(buy_val, buy=True, symbol=s)
                    qty = buy_val / last_px[s]
                    if s in lots:
                        lots[s].qty += qty
                        lots[s].cost += buy_val + c
                    else:
                        lots[s] = Lot(qty, buy_val + c, d)
                    cash -= buy_val + c
                    total_costs += c
                    traded += buy_val
                    trades += 1
            pending = None
        v = value()
        equity.append((d, v))
        bench.append((d, bench_units * last_px[BENCHMARK] if bench_units else capital))
        if lots:
            invested_days += 1
        nxt = days[i + 1] if i + 1 < len(days) else None
        if rule(d, nxt) and nxt is not None:
            current = {s: lot.qty * last_px[s] / v for s, lot in lots.items()}
            tgt = strategy.target(d, hist, current)
            if tgt is not None:
                pending = tgt
                rebalances += 1
    if tax and equity:
        # Tax on gains realized in the final, unfinished year.
        settle_tax(financial_year(equity[-1][0]))
        equity[-1] = (equity[-1][0], value())
    years = max((equity[-1][0] - equity[0][0]).days / 365.25, 1e-9) if equity else 1
    avg_val = sum(v for _, v in equity) / len(equity) if equity else capital
    return DailyResult(strategy.name, start, end, equity, bench, trades, total_costs, total_tax,
                       traded / avg_val / years / 2, invested_days / max(len(equity), 1), rebalances)


UNIVERSE_DIR = Path(__file__).parent / "universes"


def universe(name: str = "nifty100") -> list[str]:
    return read_symbols(UNIVERSE_DIR / f"{name}.txt")


# What the dashboard's Lab shows for the daily (invest) strategies.
DAILY_CATALOG = [
    {"name": "index_trend", "label": "Nifty trend (ETF or cash)",
     "description": "Holds the Nifty 50 ETF (NIFTYBEES) while the Nifty is above its 200-day average, and cash below it. "
                    "One instrument, no stock picking, about 4 trades a year. Aims to cut deep crashes, not to beat the index.",
     "params": [
         {"name": "sma_days", "label": "Average length (days)", "type": "int", "min": 50, "max": 300, "step": 10, "default": 200},
         {"name": "buffer_pct", "label": "Buffer around the average %", "type": "float", "min": 0, "max": 5, "step": 0.5, "default": 1.0},
     ]},
    {"name": "momentum", "label": "Momentum top stocks",
     "description": "Every quarter, picks the Nifty 100 stocks with the strongest 6- and 12-month risk-adjusted returns "
                    "(the method behind NSE's Nifty200 Momentum 30), equal weight. Checks the market every month and "
                    "goes to cash while the Nifty is below its 200-day average.",
     "params": [
         {"name": "top_n", "label": "Stocks held", "type": "int", "min": 5, "max": 30, "step": 1, "default": 15},
         {"name": "keep_rank", "label": "Keep while ranked in top", "type": "int", "min": 5, "max": 50, "step": 1, "default": 25},
         {"name": "rank_months", "label": "Re-rank every N months (1, 3 or 6)", "type": "int", "min": 1, "max": 6, "step": 1, "default": 3},
         {"name": "trend_filter", "label": "Market filter (1 = on)", "type": "int", "min": 0, "max": 1, "step": 1, "default": 1},
     ]},
]


def build_daily(name: str, params: dict[str, Any] | None = None, symbols: list[str] | None = None) -> Any:
    spec = next((c for c in DAILY_CATALOG if c["name"] == name), None)
    if spec is None:
        raise ValueError(f"unknown daily strategy {name!r}")
    p = {x["name"]: x["default"] for x in spec["params"]}
    for x in spec["params"]:
        if params and x["name"] in params and params[x["name"]] is not None:
            v = min(max(float(params[x["name"]]), x["min"]), x["max"])
            p[x["name"]] = int(round(v)) if x["type"] == "int" else v
    if name == "index_trend":
        return IndexTrend(sma_days=p["sma_days"], buffer_pct=p["buffer_pct"])
    rank_every = "monthly" if p["rank_months"] < 2 else "quarterly" if p["rank_months"] < 5 else "semiannual"
    return MomentumRotation(symbols=symbols or universe(), top_n=p["top_n"], keep_rank=max(p["keep_rank"], p["top_n"]),
                            trend_filter=bool(p["trend_filter"]), rank_every=rank_every)


def result_payload(r: DailyResult, max_points: int = 400) -> dict[str, Any]:
    step = max(1, len(r.equity) // max_points)
    pts = list(range(0, len(r.equity), step)) + ([len(r.equity) - 1] if (len(r.equity) - 1) % step else [])
    return {"metrics": r.metrics(), "yearly": r.yearly(),
            "equity": [{"date": r.equity[i][0].isoformat(), "value": round(r.equity[i][1], 2),
                        "benchmark": round(r.benchmark[i][1], 2)} for i in pts]}


def read_symbols(path: str | Path) -> list[str]:
    """Symbols from an NSE index constituents CSV (column 'Symbol') or one symbol per line."""
    lines = Path(path).read_text().splitlines()
    if lines and "Symbol" in lines[0]:
        import csv

        return [r["Symbol"].strip() for r in csv.DictReader(lines) if r.get("Symbol")]
    return [ln.strip().upper() for ln in lines if ln.strip() and not ln.startswith("#")]


def today() -> date:
    return datetime.now().date()
