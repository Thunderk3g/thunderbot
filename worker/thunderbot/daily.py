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
from datetime import date, datetime
from pathlib import Path
from typing import Any

from .costs import GROWW

# Prices: {symbol: {date: adjusted close}} on a shared trading calendar.
Prices = dict[str, dict[date, float]]

BENCHMARK = "NIFTYBEES"  # Nifty 50 ETF; its adjusted price approximates the Nifty 50 total return
INDEX = "^NSEI"  # Nifty 50 index (price), used for the market trend filter
CASH = "CASH"
LIQUID = "LIQUID"  # a growth-type liquid ETF; in backtests its price is built from CASH_YIELDS

# What each instrument is, for charges and tax. Anything not listed is treated as a stock.
EQUITY_ETFS = frozenset({
    "NIFTYBEES", "JUNIORBEES", "BANKBEES", "SETFNIF50", "NIFTYIETF", "HDFCNIFTY", "NEXT50IETF", "MOM100",
    "MID150BEES", "MIDCAPETF", "MIDCAPIETF", "MID150CASE", "MOMENTUM", "MOM30IETF", "HDFCMOMENT", "MOMOMENTUM",
    "ALPHA", "ALPL30IETF", "LOWVOLIETF",
})
COMMODITY_ETFS = frozenset({"GOLDBEES", "SETFGOLD", "HDFCGOLD", "GOLDIETF", "SILVERBEES"})
OVERSEAS_ETFS = frozenset({"MON100", "MAFANG", "MASPTOP50", "HNGSNGBEES"})
DEBT_ETFS = frozenset({LIQUID, "LIQUIDCASE", "LIQUIDBEES", "LIQUIDADD", "GROWWLIQID", "LIQUIDIETF", "LIQUID1",
                       "LTGILTBEES", "GILT5YBEES"})


def asset_class(symbol: str) -> str:
    """equity_etf | commodity_etf | overseas_etf | debt_etf | stock"""
    if symbol in EQUITY_ETFS:
        return "equity_etf"
    if symbol in COMMODITY_ETFS:
        return "commodity_etf"
    if symbol in OVERSEAS_ETFS:
        return "overseas_etf"
    if symbol in DEBT_ETFS:
        return "debt_etf"
    return "stock"


# Return on overnight money in India by calendar year, %: the Nifty 1D Rate index, before fund costs.
# 2022-2025 are NSE's published figures; 2018-2021 are derived from its multi-year returns; 2008-2017
# are HDFC Overnight Fund's actual return plus 0.10; 2026 is the year to 30 October, annualised.
# Source table: research_notes/ETF rotation and serverless hosting/liquid_etfs_and_cash_returns.md
CASH_YIELDS: dict[int, float] = {
    2008: 7.6, 2009: 3.4, 2010: 4.8, 2011: 7.6, 2012: 8.3, 2013: 8.3, 2014: 8.3, 2015: 7.4, 2016: 6.5,
    2017: 6.0, 2018: 6.15, 2019: 5.77, 2020: 3.41, 2021: 3.28, 2022: 4.78, 2023: 6.76, 2024: 6.75, 2025: 5.81,
    2026: 5.2,
}
LIQUID_ETF_COST_PCT = 0.30  # expense ratio plus tracking shortfall of a growth-type liquid ETF, % a year


def liquid_series(days: list[date], yields: dict[int, float] | None = None, cost_pct: float = LIQUID_ETF_COST_PCT,
                  start_price: float = 100.0) -> dict[date, float]:
    """A liquid ETF's price on the given days, compounding each calendar year's overnight rate less costs."""
    yields = yields or CASH_YIELDS
    latest = yields[max(yields)]
    out: dict[date, float] = {}
    px, prev = start_price, None
    for d in days:
        if prev is not None:
            rate = max(yields.get(d.year, latest) - cost_pct, 0.0) / 100
            px *= (1 + rate) ** ((d - prev).days / 365.0)
        out[d] = px
        prev = d
    return out


# Costs and taxes


@dataclass
class DeliveryCosts:
    """Groww delivery (CNC) charges per order on NSE, as of November 2026.

    Brokerage min(Rs 20, 0.1%), floored at min(Rs 5, 2.5%); NSE charges 0.00307%; SEBI 0.0001%; stamp
    duty 0.015% on buys; GST 18% on brokerage, exchange, SEBI and DP charges; DP Rs 23.60 per scrip sold
    per day. STT depends on the instrument: 0.1% on each side for stocks, 0.001% on the sell side for
    equity ETFs, and none for gold, silver, overseas and debt ETFs (they are not equity-oriented funds).
    Slippage is half the bid-ask spread plus impact: about 0.05% for liquid ETFs and large stocks, and one
    tick (0.01%) for a liquid ETF priced near Rs 100. Sources: research_notes (etf_tax_and_charges.md).
    """

    # Rates come from the one schedule in costs.py, which the intraday cost model reads too.
    exchange_pct: float = GROWW.exchange_txn
    sebi_pct: float = GROWW.sebi_fee
    stamp_buy_pct: float = GROWW.stamp_delivery_buy
    gst_pct: float = GROWW.gst
    dp_per_sell: float = GROWW.dp_charge_per_sell
    stock_stt_pct: float = GROWW.stt_delivery
    etf_sell_stt_pct: float = GROWW.stt_equity_etf_sell
    slippage_pct: float = 0.0005  # per side
    liquid_slippage_pct: float = 0.0001

    @staticmethod
    def brokerage(value: float) -> float:
        return GROWW.brokerage(value)

    def order(self, value: float, buy: bool, symbol: str = "") -> float:
        if value <= 0:
            return 0.0
        b = self.brokerage(value)
        fees = value * (self.exchange_pct + self.sebi_pct)
        kind = asset_class(symbol)
        if kind == "stock":
            stt = value * self.stock_stt_pct
        elif kind == "equity_etf":
            stt = 0.0 if buy else value * self.etf_sell_stt_pct
        else:
            stt = 0.0
        slip = self.liquid_slippage_pct if kind == "debt_etf" else self.slippage_pct
        cost = b + fees + stt + value * slip
        if buy:
            cost += value * self.stamp_buy_pct + self.gst_pct * (b + fees)
        else:
            cost += self.dp_per_sell + self.gst_pct * (b + fees)  # DP already includes its GST
        return cost


@dataclass
class CapitalGainsTax:
    """Capital-gains tax for a resident individual, financial year 2026-27.

    Four kinds of gain, by instrument and holding period (see ``tax_bucket``):
    - ``stcg``: stocks and equity ETFs held 12 months or less. 20%.
    - ``ltcg``: stocks and equity ETFs held longer. 12.5% above Rs 1.25 lakh a year.
    - ``other_ltcg``: gold, silver and overseas ETFs held more than 12 months. 12.5%, no exemption.
    - ``slab``: those ETFs held 12 months or less, and liquid or debt ETFs for any period. Taxed as
      income at the investor's marginal rate (``slab_rate``).
    Short-term losses offset any gain; long-term losses offset long-term gains only; unused losses
    carry forward (pass a ``carry`` dict to keep them between years).
    """

    stcg_rate: float = 0.20
    ltcg_rate: float = 0.125
    ltcg_exempt: float = 125_000.0
    cess: float = 0.04  # health and education cess on the tax
    other_ltcg_rate: float = 0.125
    slab_rate: float = 0.30

    def year_tax(self, stcg: float, ltcg: float, other_ltcg: float = 0.0, slab: float = 0.0,
                 carry: dict[str, float] | None = None) -> float:
        st_loss = max(-stcg, 0.0) + max(-slab, 0.0) + (carry or {}).get("st", 0.0)
        lt_loss = max(-ltcg, 0.0) + max(-other_ltcg, 0.0) + (carry or {}).get("lt", 0.0)
        gains = {"slab": max(slab, 0.0), "stcg": max(stcg, 0.0), "other": max(other_ltcg, 0.0), "ltcg": max(ltcg, 0.0)}
        # Use short-term losses where the tax rate is highest; equity LTCG last (part of it is exempt).
        order = ["slab", "stcg"] if self.slab_rate >= self.stcg_rate else ["stcg", "slab"]
        for k in [*order, "other", "ltcg"]:
            used = min(st_loss, gains[k])
            gains[k] -= used
            st_loss -= used
        for k in ("other", "ltcg"):
            used = min(lt_loss, gains[k])
            gains[k] -= used
            lt_loss -= used
        if carry is not None:
            carry["st"], carry["lt"] = st_loss, lt_loss
        tax = (gains["slab"] * self.slab_rate + gains["stcg"] * self.stcg_rate + gains["other"] * self.other_ltcg_rate
               + max(gains["ltcg"] - self.ltcg_exempt, 0.0) * self.ltcg_rate)
        return tax * (1 + self.cess)


TAX_BUCKETS = ("stcg", "ltcg", "other_ltcg", "slab")


def tax_bucket(symbol: str, held_days: int) -> str:
    """Which of CapitalGainsTax's four kinds of gain a sale falls under."""
    kind = asset_class(symbol)
    long_term = held_days > 365
    if kind in ("stock", "equity_etf"):
        return "ltcg" if long_term else "stcg"
    if kind == "debt_etf":
        return "slab"
    return "other_ltcg" if long_term else "slab"


def financial_year(d: date) -> int:
    return d.year if d.month >= 4 else d.year - 1


# Data


Fetcher = Callable[[list[str], date, date], tuple[Prices, dict[str, str]]]


def load_prices(symbols: list[str], start: date, end: date, cache_dir: Path | None = None,
                fetch: Fetcher | None = None, errors: dict[str, str] | None = None) -> Prices:
    """Daily adjusted closes from Yahoo Finance's chart endpoint, cleaned of known bad ticks.

    Index symbols start with ^; others get the .NS suffix. ``LIQUID`` is not downloaded: it is built from
    the yearly overnight-rate table on the calendar of the first symbol that has data. Symbols Yahoo
    could not serve are left out and, if ``errors`` is given, explained there.
    """
    import json

    real = [s for s in dict.fromkeys(symbols) if s != LIQUID]
    raw: Prices = {}
    cache = cache_dir / f"daily_{start}_{end}.json" if cache_dir else None
    if cache and cache.exists():
        try:
            raw = {s: {date.fromisoformat(d): v for d, v in series.items()}
                   for s, series in json.loads(cache.read_text()).items()}
        except (ValueError, OSError):
            raw = {}
    missing = [s for s in real if s not in raw]
    if missing:
        if fetch is None:
            from .chart import fetch_many as fetch
        got, errs = fetch(missing, start, end)
        raw.update(got)
        if errors is not None:
            errors.update(errs)
        if cache and got:
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps({s: {d.isoformat(): v for d, v in series.items()} for s, series in raw.items()}))
    out: Prices = {}
    for s in real:
        series = {d: v for d, v in raw.get(s, {}).items() if v > 0 and start <= d <= end}
        if series:
            out[s], _ = clean_series(series)
    if LIQUID in symbols and out:
        anchor = INDEX if INDEX in out else next(iter(out))
        out[LIQUID] = liquid_series(sorted(out[anchor]))
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
    for vals in raw.values():
        xs = [vals[s] for s in common]
        if len(xs) < 2:
            continue
        mu = sum(xs) / len(xs)
        sd = math.sqrt(sum((x - mu) ** 2 for x in xs) / (len(xs) - 1)) or 1.0
        for s in common:
            scores[s] += (vals[s] - mu) / sd / len(raw)
    return scores


# Drift corridors and cash routing: plain arithmetic shared by the backtester and the live runner.

BAND_ABS_PCT = 5.0  # a holding is out of its corridor when it is this many points from target ...
BAND_REL_PCT = 20.0  # ... or this share of its own target away, whichever comes first


def corridor(target: float, abs_pct: float = BAND_ABS_PCT, rel_pct: float = BAND_REL_PCT) -> tuple[float, float]:
    """The (low, high) weights a holding may sit between, as fractions. ``target`` is a fraction too.
    A 33% holding may drift to 28.3-38.3% (the 5-point rule binds); a 10% one to 8-12% (the 20% rule)."""
    half = min(abs_pct / 100.0, rel_pct / 100.0 * target)
    return max(target - half, 0.0), min(target + half, 1.0)


def out_of_band(current: dict[str, float], target: dict[str, float], abs_pct: float = BAND_ABS_PCT,
                rel_pct: float = BAND_REL_PCT) -> list[str]:
    """Target holdings whose weight has reached the edge of their corridor."""
    out = []
    for s, t in target.items():
        lo, hi = corridor(t, abs_pct, rel_pct)
        w = current.get(s, 0.0)
        if w <= lo + 1e-9 or w >= hi - 1e-9:
            out.append(s)
    return out


def shortfalls(values: dict[str, float], target: dict[str, float], total: float) -> dict[str, float]:
    """Rupees each target holding is below its share of ``total`` (negative when above)."""
    return {s: t * total - values.get(s, 0.0) for s, t in target.items()}


def route_cash(cash: float, values: dict[str, float], target: dict[str, float], prices: dict[str, float], total: float,
               min_order: float = 500.0, buffer: float = 0.004) -> list[tuple[str, int]]:
    """Spend ``cash`` on whole shares with no sells: the holding furthest below target first, then the
    next, until the cash is used or nothing is a whole share short. ``total`` is the portfolio's value
    including the cash. Returns (symbol, quantity) buys in the order to place them."""
    usable = cash / (1 + buffer)
    values = dict(values)
    orders: dict[str, int] = {}
    while True:
        short = shortfalls(values, target, total)
        pick = None
        for s in sorted(short, key=short.get, reverse=True):
            px = prices.get(s)
            if not px:
                continue
            qty = math.floor(min(short[s], usable) / px)
            if qty >= 1 and (qty * px >= min_order or s in orders):
                pick = (s, qty, px)
                break
        if pick is None:
            break
        s, qty, px = pick
        orders[s] = orders.get(s, 0) + qty
        values[s] = values.get(s, 0.0) + qty * px
        usable -= qty * px
    return list(orders.items())


# Tax-gain harvesting. Selling and rebuying the same ticker on one day is netted by the broker as an
# intraday trade and realises nothing, so a harvest either rebuys on the next session or swaps into a
# twin: another fund on the same index. Edit this map to suit what your broker lists. (Not verified
# against primary tax sources: confirm with a chartered accountant before acting on a harvest.)
HARVEST_TWINS: dict[str, str] = {
    "NIFTYBEES": "SETFNIF50", "SETFNIF50": "NIFTYBEES",
    "JUNIORBEES": "NEXT50IETF", "NEXT50IETF": "JUNIORBEES",
}


def xirr(flows: list[tuple[date, float]]) -> float | None:
    """Money-weighted yearly return, in %, of dated cash flows (money in is negative). None when the
    flows never change sign or no rate between -99% and +1000% balances them."""
    if not flows or not (any(v < 0 for _, v in flows) and any(v > 0 for _, v in flows)):
        return None
    d0 = min(d for d, _ in flows)

    def npv(rate: float) -> float:
        return sum(v / (1 + rate) ** ((d - d0).days / 365.25) for d, v in flows)

    lo, hi = -0.99, 10.0
    if npv(lo) * npv(hi) > 0:
        return None
    for _ in range(100):
        mid = (lo + hi) / 2
        if npv(lo) * npv(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return round((lo + hi) / 2 * 100, 2)


# Strategies: each returns target weights for the next session, given history up to today.

RebalanceRule = Callable[[date, date | None], bool]
KEEP = "keep"  # a strategy returns this to say "the holdings are fine, do not trade"
Target = dict[str, float] | str | None  # weights, KEEP, or None when there is not enough history


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
    """Hold an equity ETF while the Nifty is above its N-day average; otherwise hold the cash asset
    (a liquid ETF), or plain cash if none is given. Checked at each rebalance date. A buffer avoids
    flipping on every touch of the average."""

    sma_days: int = 200
    buffer_pct: float = 1.0
    rebalance: str = "monthly"  # month-end checks: fewer whipsaws than weekly or daily checks
    asset: str = BENCHMARK
    cash_asset: str | None = None
    name: str = "index_trend"

    def universe(self) -> list[str]:
        return [INDEX, self.asset, *([self.cash_asset] if self.cash_asset else [])]

    def target(self, d: date, hist: dict[str, list[float]], current: dict[str, float]) -> Target:
        idx = hist.get(INDEX, [])
        avg = sma(idx, self.sma_days)
        if avg is None or self.asset not in hist:
            return None
        invested = current.get(self.asset, 0) > 0
        up = idx[-1] > avg * (1 + self.buffer_pct / 100)
        down = idx[-1] < avg * (1 - self.buffer_pct / 100)
        if up or (invested and not down):
            return {self.asset: 1.0}
        return {self.cash_asset: 1.0} if self.cash_asset and self.cash_asset in hist else {}


def blended_return(px: list[float], lookbacks: tuple[int, ...]) -> float | None:
    """Average of the returns over each lookback (in trading days). None without enough history."""
    if len(px) <= max(lookbacks) or px[-1] <= 0:
        return None
    return sum(px[-1] / px[-1 - lb] - 1 for lb in lookbacks) / len(lookbacks)


@dataclass
class EtfRotation:
    """Rotate between a few ETFs on their own trends, parking the rest in a liquid ETF.

    Two modes, both checked at month-end:
    - ``rank`` (dual momentum): score each ETF by its average 3-, 6- and 12-month return. Hold the top
      ``top_n`` in equal parts, but only those whose score beats the liquid ETF's over the same
      periods; any slot that fails goes to the liquid ETF.
    - ``trend`` (Faber): give every ETF an equal share and hold it only while its price is above its
      ``sma_days`` average; a share that is out goes to the liquid ETF.
    To keep turnover and tax low it trades only when the holdings change, or when a weight has
    drifted more than ``band_pct`` points from its target.
    """

    assets: list[str] = field(default_factory=lambda: ["NIFTYBEES", "JUNIORBEES", "GOLDBEES"])
    cash_asset: str | None = LIQUID
    mode: str = "rank"
    top_n: int = 2
    lookbacks: tuple[int, ...] = (63, 126, 252)
    sma_days: int = 200
    band_pct: float = 10.0
    cash_yield_pct: float = 6.0  # used for the absolute test only when the cash asset has no history
    rebalance: str = "monthly"
    name: str = "etf_rotation"

    def universe(self) -> list[str]:
        return [INDEX, *self.assets, *([self.cash_asset] if self.cash_asset else [])]

    def scores(self, hist: dict[str, list[float]]) -> dict[str, float]:
        out = {}
        for a in self.assets:
            r = blended_return(hist.get(a, []), self.lookbacks)
            if r is not None:
                out[a] = r
        return out

    def cash_score(self, hist: dict[str, list[float]]) -> float:
        r = blended_return(hist.get(self.cash_asset or "", []), self.lookbacks)
        if r is not None:
            return r
        return sum((1 + self.cash_yield_pct / 100) ** (lb / 252) - 1 for lb in self.lookbacks) / len(self.lookbacks)

    def wanted(self, hist: dict[str, list[float]]) -> dict[str, float] | None:
        """Target weights before the no-trade band. None when no ETF has enough history yet."""
        weights: dict[str, float] = {}
        if self.mode == "trend":
            ready = [a for a in self.assets if len(hist.get(a, [])) >= self.sma_days]
            if not ready:
                return None
            for a in ready:
                if hist[a][-1] > sma(hist[a], self.sma_days):
                    weights[a] = 1.0 / len(ready)
        else:
            scores = self.scores(hist)
            if not scores:
                return None
            hurdle = self.cash_score(hist)
            n = min(self.top_n, len(scores))
            for a in sorted(scores, key=scores.get, reverse=True)[:n]:
                if scores[a] > hurdle:
                    weights[a] = 1.0 / n
        spare = 1.0 - sum(weights.values())
        if spare > 1e-9 and self.cash_asset and self.cash_asset in hist:
            weights[self.cash_asset] = spare
        return weights

    def target(self, d: date, hist: dict[str, list[float]], current: dict[str, float]) -> Target:
        want = self.wanted(hist)
        if want is None:
            return None
        held = {s for s, w in current.items() if w > 0.005}
        if held == set(want) and all(abs(current.get(s, 0) - w) * 100 <= self.band_pct for s, w in want.items()):
            return KEEP  # same holdings, weights close enough
        return want


@dataclass
class StaticMix:
    """Hold fixed weights and rebalance once a year. A no-timing yardstick: it shows what the same
    ETFs earned without any rotation, so the rotation rule cannot take credit for the asset mix."""

    weights: dict[str, float] = field(default_factory=dict)
    rebalance: str = "monthly"  # looked at every month-end, traded only in ``month``
    month: int = 3  # rebalance at the end of March, the last month of the tax year
    name: str = "static_mix"
    # ``band``: ignore the calendar and rebalance only when a holding has left its drift corridor.
    band: bool = False
    band_abs_pct: float = BAND_ABS_PCT
    band_rel_pct: float = BAND_REL_PCT
    # Backtest only: add this much on the first session of every month, bought into whatever is furthest
    # below target. With ``deposits_only`` the plan never sells, so new money does all the rebalancing.
    monthly_deposit: float = 0.0
    deposits_only: bool = False

    def universe(self) -> list[str]:
        return [INDEX, *self.weights]

    def target(self, d: date, hist: dict[str, list[float]], current: dict[str, float]) -> Target:
        ready = {s: w for s, w in self.weights.items() if hist.get(s)}
        if not ready:
            return None
        total = sum(ready.values())
        want = {s: w / total for s, w in ready.items()}
        held = {s for s, w in current.items() if w > 0.005}
        if self.band:
            if held == set(ready) and not out_of_band(current, want, self.band_abs_pct, self.band_rel_pct):
                return KEEP
            return want
        if held and d.month != self.month and held == set(ready):
            return KEEP
        return want


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

    def target(self, d: date, hist: dict[str, list[float]], current: dict[str, float]) -> Target:
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
            return KEEP  # keep the holdings until the next ranking date
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
    exit_tax: float = 0.0  # tax still owed on unrealized gains if everything were sold on the last day
    benchmark_exit_tax: float = 0.0
    weights: list[tuple[date, dict[str, float]]] = field(default_factory=list)  # after each rebalance
    # With monthly deposits, ``equity`` and ``benchmark`` are time-weighted indices (what one rupee held
    # throughout became, scaled to the starting capital), so CAGR and drawdown stay comparable. What the
    # account actually held, and its money-weighted return, are in ``deposits``.
    deposits: dict[str, Any] | None = None

    def metrics(self) -> dict[str, Any]:
        m = {**_stats(self.equity), "trades": self.trades, "costs": round(self.costs, 2),
             "taxes": round(self.taxes, 2), "turnover_per_year": round(self.turnover, 2),
             "time_invested_pct": round(self.exposure * 100, 1), "rebalances": self.rebalances,
             "benchmark": _stats(self.benchmark)}
        # Exit tax is in rupees of the real account; scale it to the index when deposits were made.
        dep = self.deposits or {}
        scale = self.equity[-1][1] / dep["final_value"] if dep.get("final_value") else 1.0
        bscale = self.benchmark[-1][1] / dep["benchmark_final_value"] if dep.get("benchmark_final_value") else 1.0
        m["exit_tax"] = round(self.exit_tax, 2)
        m["cagr_after_exit_tax_pct"] = _cagr_after(self.equity, self.exit_tax * scale)
        m["benchmark"]["exit_tax"] = round(self.benchmark_exit_tax, 2)
        m["benchmark"]["cagr_after_exit_tax_pct"] = _cagr_after(self.benchmark, self.benchmark_exit_tax * bscale)
        if self.deposits:
            m["deposits"] = self.deposits
        return m

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


def _cagr_after(series: list[tuple[date, float]], deduct: float) -> float | None:
    if len(series) < 2:
        return None
    (d0, v0), (d1, v1) = series[0], series[-1]
    years = max((d1 - d0).days / 365.25, 1e-9)
    return round(((max(v1 - deduct, 1e-9) / v0) ** (1 / years) - 1) * 100, 2)


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
             cash_yield_pct: float = 0.0, min_trade: float = 1_000.0, trade_lag: int = 1,
             monthly_deposit: float | None = None, deposits_only: bool | None = None) -> DailyResult:
    """Simulate the strategy day by day.

    Decisions use closes up to day t and fill at the close ``trade_lag`` sessions later (1 by default,
    so there is no look-ahead; 0 approximates deciding and trading in the last minutes of day t).
    Shares are sold first-in first-out, as Indian demat accounts are taxed. Tax for a financial year is
    paid on the first session of the next one, by selling the cash asset first if cash is short.

    ``monthly_deposit`` adds that many rupees on the first session of each later month and buys whatever
    is furthest below its target with it, selling nothing. The benchmark receives the same deposits.
    ``deposits_only`` stops the plan from ever selling to rebalance, so the deposits do all of it. Both
    default to the strategy's own ``monthly_deposit`` / ``deposits_only`` attributes when it has them.
    """
    costs = costs or DeliveryCosts()
    monthly_deposit = float(getattr(strategy, "monthly_deposit", 0.0) if monthly_deposit is None else monthly_deposit)
    deposits_only = bool(getattr(strategy, "deposits_only", False) if deposits_only is None else deposits_only)
    days = [d for d in calendar(prices, INDEX if INDEX in prices else BENCHMARK)]
    hist: dict[str, list[float]] = {s: [] for s in prices}
    last_px: dict[str, float] = {}
    lots: dict[str, list[Lot]] = {}
    cash = capital
    queue: list[tuple[int, dict[str, float]]] = []  # (index of the fill day, target weights)
    equity, bench = [], []
    weights_log: list[tuple[date, dict[str, float]]] = []
    trades = 0
    total_costs = total_tax = traded = 0.0
    invested_days = 0
    rebalances = 0
    gains: dict[int, dict[str, float]] = {}  # fy -> gain by tax bucket
    carry: dict[str, float] = {}
    rule = REBALANCE[strategy.rebalance]
    daily_cash = (1 + cash_yield_pct / 100) ** (1 / 252) - 1
    cash_asset = getattr(strategy, "cash_asset", None)
    bench_units = None
    bench_cost = capital
    started = decided = False
    # Deposits: units of a time-weighted index for the account and for the benchmark, and the dated flows.
    units = bench_idx_units = capital
    flows: list[tuple[date, float]] = []
    last_target: dict[str, float] = {}
    contributed = capital

    def held(s: str) -> float:
        return sum(lot.qty for lot in lots.get(s, []))

    def value() -> float:
        return cash + sum(held(s) * last_px.get(s, 0) for s in lots)

    def sell(s: str, sell_val: float, d: date) -> None:
        nonlocal cash, total_costs, traded, trades
        px = last_px[s]
        qty = min(sell_val / px, held(s))
        if qty <= 0:
            return
        c = costs.order(qty * px, buy=False, symbol=s)
        left, fy = qty, financial_year(d)
        g = gains.setdefault(fy, dict.fromkeys(TAX_BUCKETS, 0.0))
        for lot in list(lots[s]):
            take = min(lot.qty, left)
            if take <= 0:
                break
            basis = lot.cost * take / lot.qty
            share = take / qty
            g[tax_bucket(s, (d - lot.since).days)] += take * px - c * share - basis
            lot.qty -= take
            lot.cost -= basis
            left -= take
            if lot.qty * px < 0.01:
                lots[s].remove(lot)
        if not lots[s]:
            del lots[s]
        cash += qty * px - c
        total_costs += c
        traded += qty * px
        trades += 1

    def buy(s: str, buy_val: float, d: date) -> None:
        nonlocal cash, total_costs, traded, trades
        c = costs.order(buy_val, buy=True, symbol=s)
        lots.setdefault(s, []).append(Lot(buy_val / last_px[s], buy_val + c, d))
        cash -= buy_val + c
        total_costs += c
        traded += buy_val
        trades += 1

    def execute(pending: dict[str, float], d: date) -> None:
        nonlocal last_target
        last_target = dict(pending)
        total = value()
        want = {s: w * total for s, w in pending.items() if s in last_px}
        if not deposits_only:
            for s in list(lots):  # sells first, to free cash
                target_val = want.get(s, 0.0)
                cur_val = held(s) * last_px[s]
                if cur_val - target_val > min_trade or (target_val == 0 and cur_val > 0):
                    sell(s, cur_val - target_val, d)
        # Buys, the holding furthest below target first, so a no-sell plan spends its cash where it counts.
        for s, target_val in sorted(want.items(), key=lambda kv: kv[1] - held(kv[0]) * last_px[kv[0]], reverse=True):
            buy_val = min(target_val - held(s) * last_px[s], cash / (1 + 0.004))
            if buy_val > min_trade:
                buy(s, buy_val, d)
        v = value()
        weights_log.append((d, {s: round(held(s) * last_px[s] / v, 4) for s in lots} if v else {}))

    def deposit(d: date) -> None:
        """Add the month's money and buy what is furthest below target with it. Nothing is sold."""
        nonlocal cash, units, bench_units, bench_cost, bench_idx_units, contributed
        v = value()
        units += monthly_deposit / (v / units) if v > 0 else monthly_deposit
        cash += monthly_deposit
        contributed += monthly_deposit
        flows.append((d, -monthly_deposit))
        if bench_units and BENCHMARK in last_px:
            bench_val = bench_units * last_px[BENCHMARK]
            bench_idx_units += monthly_deposit / (bench_val / bench_idx_units)
            c = costs.order(monthly_deposit, buy=True, symbol=BENCHMARK)
            bench_units += (monthly_deposit - c) / last_px[BENCHMARK]
            bench_cost += monthly_deposit - c
        target = {s: w for s, w in last_target.items() if s in last_px}
        if not target:
            return  # nothing decided yet: the first decision spends it
        total = value()
        short = shortfalls({s: held(s) * last_px[s] for s in target}, target, total)
        for s in sorted(short, key=short.get, reverse=True):
            buy_val = min(short[s], cash / (1 + 0.004))
            if buy_val > min(min_trade, 500.0):
                buy(s, buy_val, d)

    def settle_tax(fy: int, d: date) -> None:
        nonlocal cash, total_tax
        if not tax or fy not in gains:
            return
        g = gains.pop(fy)
        t = tax.year_tax(g["stcg"], g["ltcg"], g["other_ltcg"], g["slab"], carry=carry)
        if t > cash:  # raise the money: the cash asset first, then everything pro rata
            short = (t - cash) * 1.002 + 50
            if cash_asset in lots:
                sell(cash_asset, min(short, held(cash_asset) * last_px[cash_asset]), d)
            short = t - cash
            invested = sum(held(s) * last_px[s] for s in lots)
            if short > 0 and invested > 0:
                frac = min(1.0, (short * 1.002 + 50 * len(lots)) / invested)
                for s in list(lots):
                    sell(s, held(s) * last_px[s] * frac, d)
        cash -= t
        total_tax += t

    def unrealized_tax(d: date) -> float:
        """Tax owed if everything were sold today, on top of gains already realized this year."""
        if not tax:
            return 0.0
        g = dict(gains.get(financial_year(d), dict.fromkeys(TAX_BUCKETS, 0.0)))
        base = tax.year_tax(g["stcg"], g["ltcg"], g["other_ltcg"], g["slab"], carry=dict(carry))
        for s, ls in lots.items():
            for lot in ls:
                g[tax_bucket(s, (d - lot.since).days)] += lot.qty * last_px[s] - lot.cost
        return max(tax.year_tax(g["stcg"], g["ltcg"], g["other_ltcg"], g["slab"], carry=dict(carry)) - base, 0.0)

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
            flows.append((d, -capital))
            if BENCHMARK in last_px:
                bench_cost = capital - costs.order(capital, buy=True, symbol=BENCHMARK)
                bench_units = bench_cost / last_px[BENCHMARK]
        elif monthly_deposit > 0 and i > 0 and d.month != days[i - 1].month:
            deposit(d)
        # Pay last financial year's tax at the first trading day of a new one.
        if tax and i > 0 and financial_year(d) != financial_year(days[i - 1]):
            settle_tax(financial_year(days[i - 1]), d)
        if cash > 0:
            cash *= 1 + daily_cash
        # Execute the decision that is due today, at today's close.
        while queue and queue[0][0] <= i:
            execute(queue.pop(0)[1], d)
        v = value()
        equity.append((d, v * (capital / units)))  # capital / units is exactly 1 until a deposit is made
        bench.append((d, bench_units * last_px[BENCHMARK] * (capital / bench_idx_units) if bench_units else capital))
        if any(asset_class(s) != "debt_etf" for s in lots):
            invested_days += 1
        nxt = days[i + 1] if i + 1 < len(days) else None
        # Decide on rebalance days, and on the first day too (a new account does not wait for month-end).
        if (rule(d, nxt) or not decided) and nxt is not None:
            current = {s: held(s) * last_px[s] / v for s in lots}
            tgt = strategy.target(d, hist, current)
            decided = decided or tgt is not None
            if isinstance(tgt, dict):
                rebalances += 1
                if trade_lag <= 0:
                    execute(tgt, d)
                    equity[-1] = (d, value() * (capital / units))
                else:
                    queue.append((i + trade_lag, tgt))
    exit_tax = bench_exit_tax = 0.0
    if tax and equity:
        last_day = equity[-1][0]
        exit_tax = unrealized_tax(last_day)
        # Tax on gains realized in the final, unfinished year.
        settle_tax(financial_year(last_day), last_day)
        equity[-1] = (last_day, value() * (capital / units))
        if bench_units:
            bench_exit_tax = CapitalGainsTax(**{k: getattr(tax, k) for k in tax.__dataclass_fields__}).year_tax(
                0.0, bench_units * last_px[BENCHMARK] - bench_cost)
    years = max((equity[-1][0] - equity[0][0]).days / 365.25, 1e-9) if equity else 1
    avg_val = sum(v for _, v in equity) / len(equity) if equity else capital
    deposits = None
    if monthly_deposit > 0 and equity:
        last_day, final = equity[-1][0], value()
        bench_final = bench_units * last_px[BENCHMARK] if bench_units else None
        deposits = {
            "monthly": monthly_deposit, "no_sells": deposits_only, "contributed": round(contributed, 2),
            "final_value": round(final, 2), "xirr_pct": xirr([*flows, (last_day, final)]),
            "xirr_after_exit_tax_pct": xirr([*flows, (last_day, final - exit_tax)]),
            "benchmark_final_value": round(bench_final, 2) if bench_final else None,
            "benchmark_xirr_pct": xirr([*flows, (last_day, bench_final)]) if bench_final else None,
            "benchmark_xirr_after_exit_tax_pct": xirr([*flows, (last_day, bench_final - bench_exit_tax)]) if bench_final else None,
        }
    return DailyResult(strategy.name, start, end, equity, bench, trades, total_costs, total_tax,
                       traded / avg_val / years / 2, invested_days / max(len(equity), 1), rebalances,
                       exit_tax=exit_tax, benchmark_exit_tax=bench_exit_tax, weights=weights_log, deposits=deposits)


UNIVERSE_DIR = Path(__file__).parent / "universes"


def universe(name: str = "nifty100") -> list[str]:
    return read_symbols(UNIVERSE_DIR / f"{name}.txt")


# What the dashboard's Lab shows for the daily (invest) strategies. The first entry is the default.
N50, NEXT50, GOLD, MIDCAP = "NIFTYBEES", "JUNIORBEES", "GOLDBEES", "MOM100"
_ON_OFF = {"type": "int", "min": 0, "max": 1, "step": 1}
DAILY_CATALOG = [
    {"name": "core_mix", "label": "Steady mix (Nifty 50, Next 50, gold)",
     "description": "Holds NIFTYBEES, JUNIORBEES and GOLDBEES in fixed shares and rebalances once a year, at the end of "
                    "March. No market timing, about six trades a year, very little tax. In our tests no rotation rule beat "
                    "it after tax; its falls are deeper than the trend strategies', and gold's 2019-2026 run flatters it.",
     "params": [
         {"name": "gold_pct", "label": "Gold share %", "type": "int", "min": 0, "max": 50, "step": 1, "default": 33},
         {"name": "next50_pct", "label": "Next 50 share of the equity part %", "type": "int", "min": 0, "max": 100, "step": 10, "default": 50},
         {"name": "band", "label": "Rebalance only when a share leaves its band, not every March (1 = yes)", **_ON_OFF, "default": 0},
         {"name": "monthly_deposit", "label": "Test only: add this much every month, Rs", "type": "int", "min": 0, "max": 1_000_000, "step": 1_000, "default": 0},
         {"name": "no_sells", "label": "Never sell to rebalance; let new money do it (1 = yes)", **_ON_OFF, "default": 0},
     ]},
    {"name": "etf_trend", "label": "Trend rotation (ETFs or liquid fund)",
     "description": "Splits the money equally between the ETFs and holds each one only while its price is above its "
                    "200-day average; a share that is out waits in a liquid ETF. Checked at month-end. It has fallen far less "
                    "than the market in crashes and earned less than simply holding the same ETFs.",
     "params": [
         {"name": "sma_days", "label": "Average length (days)", "type": "int", "min": 100, "max": 300, "step": 10, "default": 200},
         {"name": "gold", "label": "Include gold (1 = yes)", **_ON_OFF, "default": 1},
         {"name": "midcap", "label": "Include midcaps (1 = yes)", **_ON_OFF, "default": 0},
     ]},
    {"name": "etf_rank", "label": "Strongest ETFs (dual momentum)",
     "description": "Ranks the ETFs by their average 3-, 6- and 12-month return and holds the strongest ones, but only "
                    "those beating the liquid ETF; the rest waits in the liquid ETF. Checked at month-end. More trades and "
                    "more short-term tax than the other strategies, for no extra return in our tests.",
     "params": [
         {"name": "top_n", "label": "ETFs held", "type": "int", "min": 1, "max": 3, "step": 1, "default": 2},
         {"name": "gold", "label": "Include gold (1 = yes)", **_ON_OFF, "default": 1},
         {"name": "midcap", "label": "Include midcaps (1 = yes)", **_ON_OFF, "default": 0},
     ]},
    {"name": "index_trend", "label": "Nifty trend (ETF or liquid fund)",
     "description": "Holds the Nifty 50 ETF (NIFTYBEES) while the Nifty is above its 200-day average, and a liquid ETF "
                    "below it. One instrument, about 4 trades a year. Aims to cut deep crashes, not to beat the index.",
     "params": [
         {"name": "sma_days", "label": "Average length (days)", "type": "int", "min": 50, "max": 300, "step": 10, "default": 200},
         {"name": "buffer_pct", "label": "Buffer around the average %", "type": "float", "min": 0, "max": 5, "step": 0.5, "default": 1.0},
         {"name": "liquid", "label": "Park in a liquid ETF (1 = yes)", **_ON_OFF, "default": 1},
     ]},
    {"name": "momentum", "label": "Momentum top stocks (biased backtest)",
     "description": "Every quarter, picks the Nifty 100 stocks with the strongest 6- and 12-month risk-adjusted returns "
                    "(the method behind NSE's Nifty200 Momentum 30), equal weight. Checks the market every month and "
                    "goes to cash while the Nifty is below its 200-day average. Its backtest uses today's index members, "
                    "so it is inflated by survivorship bias; a momentum ETF is the cleaner way to hold this.",
     "params": [
         {"name": "top_n", "label": "Stocks held", "type": "int", "min": 5, "max": 30, "step": 1, "default": 15},
         {"name": "keep_rank", "label": "Keep while ranked in top", "type": "int", "min": 5, "max": 50, "step": 1, "default": 25},
         {"name": "rank_months", "label": "Re-rank every N months (1, 3 or 6)", "type": "int", "min": 1, "max": 6, "step": 1, "default": 3},
         {"name": "trend_filter", "label": "Market filter (1 = on)", **_ON_OFF, "default": 1},
     ]},
]
DAILY_NAMES = tuple(c["name"] for c in DAILY_CATALOG)
PLAN_NAMES = {"core_mix": "Steady mix", "etf_trend": "Trend rotation", "etf_rank": "Strongest ETFs",
              "index_trend": "Nifty trend", "momentum": "Momentum stocks"}  # what the dashboard calls each plan


def daily_params(name: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """The strategy's parameters, each clamped to its allowed range; unknown keys are dropped."""
    spec = next((c for c in DAILY_CATALOG if c["name"] == name), None)
    if spec is None:
        raise ValueError(f"unknown daily strategy {name!r}")
    p = {x["name"]: x["default"] for x in spec["params"]}
    for x in spec["params"]:
        if params and x["name"] in params and params[x["name"]] is not None:
            v = min(max(float(params[x["name"]]), x["min"]), x["max"])
            p[x["name"]] = int(round(v)) if x["type"] == "int" else v
    return p


def build_daily(name: str, params: dict[str, Any] | None = None, symbols: list[str] | None = None,
                cash_asset: str = LIQUID) -> Any:
    """Build a strategy by its catalog name. ``cash_asset`` is the liquid ETF to park in: the synthetic
    ``LIQUID`` in backtests, the real ticker (for example LIQUIDCASE) when trading."""
    p = daily_params(name, params)
    if name == "core_mix":
        equity = 1 - p["gold_pct"] / 100
        weights = {N50: equity * (1 - p["next50_pct"] / 100), NEXT50: equity * p["next50_pct"] / 100, GOLD: p["gold_pct"] / 100}
        return StaticMix({s: w for s, w in weights.items() if w > 0}, name="core_mix", band=bool(p["band"]),
                         monthly_deposit=float(p["monthly_deposit"]), deposits_only=bool(p["no_sells"]))
    if name in ("etf_trend", "etf_rank"):
        assets = [N50, NEXT50, *([MIDCAP] if p["midcap"] else []), *([GOLD] if p["gold"] else [])]
        if name == "etf_trend":
            return EtfRotation(assets=assets, cash_asset=cash_asset, mode="trend", sma_days=p["sma_days"], name=name)
        return EtfRotation(assets=assets, cash_asset=cash_asset, mode="rank", top_n=min(p["top_n"], len(assets)), name=name)
    if name == "index_trend":
        return IndexTrend(sma_days=p["sma_days"], buffer_pct=p["buffer_pct"], cash_asset=cash_asset if p["liquid"] else None)
    rank_every = "monthly" if p["rank_months"] < 2 else "quarterly" if p["rank_months"] < 5 else "semiannual"
    return MomentumRotation(symbols=symbols or universe(), top_n=p["top_n"], keep_rank=max(p["keep_rank"], p["top_n"]),
                            trend_filter=bool(p["trend_filter"]), rank_every=rank_every)


def no_timing_twin(strategy: Any) -> StaticMix | None:
    """The same ETFs held in equal parts with a yearly rebalance: what the strategy's timing has to beat."""
    if isinstance(strategy, EtfRotation):
        return StaticMix({a: 1 / len(strategy.assets) for a in strategy.assets})
    if isinstance(strategy, IndexTrend):
        return None  # the Nifty ETF benchmark already is its no-timing twin
    return None


def result_payload(r: DailyResult, max_points: int = 400) -> dict[str, Any]:
    step = max(1, len(r.equity) // max_points)
    pts = list(range(0, len(r.equity), step)) + ([len(r.equity) - 1] if (len(r.equity) - 1) % step else [])
    spans: dict[str, float] = {}
    for (d0, w), (d1, _) in zip(r.weights, [*r.weights[1:], (r.end, {})], strict=True):
        for s, x in w.items():
            spans[s] = spans.get(s, 0.0) + x * (d1 - d0).days
        spans[CASH] = spans.get(CASH, 0.0) + max(1 - sum(w.values()), 0.0) * (d1 - d0).days
    total = sum(spans.values()) or 1.0
    return {"metrics": r.metrics(), "yearly": r.yearly(),
            "allocation": {s: round(v / total * 100, 1) for s, v in sorted(spans.items(), key=lambda kv: -kv[1]) if v / total >= 0.005},
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
