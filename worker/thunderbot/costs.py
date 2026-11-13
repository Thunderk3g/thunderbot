"""Indian equity transaction charges: one schedule, read by every cost model in the package.

``GROWW`` holds Groww's equity charges and the statutory levies as of November 2026 (sources:
research_notes/ETF rotation and serverless hosting/etf_tax_and_charges.md). ``CostModel`` prices an
intraday or delivery leg for the trading engine and the intraday backtester; ``daily.DeliveryCosts``
prices a delivery order for the daily plans, with the STT rules that differ by kind of ETF. Both take
their default rates from ``GROWW``, so a rate is changed in one place.

They are **estimates**. Reconcile them against your own contract notes before trusting any backtest.
Rates are fractions of turnover, not %.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import Product, Side


@dataclass(frozen=True)
class ChargeSchedule:
    brokerage_flat: float = 20.0  # Rs per executed order, or ...
    brokerage_pct: float = 0.001  # ... 0.1% of order value, whichever is lower
    brokerage_min: float = 5.0  # floor for small orders, itself capped at ...
    brokerage_min_pct: float = 0.025  # ... 2.5% of order value
    stt_intraday_sell: float = 0.00025  # 0.025% on the sell side
    stt_delivery: float = 0.001  # 0.1% on buy and sell (stocks)
    stt_equity_etf_sell: float = 0.00001  # 0.001% on the sell side (equity ETFs); other ETFs pay none
    exchange_txn: float = 0.0000307  # NSE cash, IPFT included
    sebi_fee: float = 0.000001  # Rs 10 per crore
    stamp_intraday_buy: float = 0.00003
    stamp_delivery_buy: float = 0.00015
    gst: float = 0.18  # on brokerage, exchange and SEBI charges
    dp_charge_per_sell: float = 23.60  # delivery sell, per scrip per day: Rs 20 plus GST
    mtf_interest_per_day: float = 0.00041  # 0.041%/day on the funded amount (Groww MTF page)

    def brokerage(self, value: float, flat: float | None = None, pct: float | None = None, floor: float | None = None) -> float:
        """min(Rs 20, 0.1%), floored at min(Rs 5, 2.5% of the order)."""
        flat = self.brokerage_flat if flat is None else flat
        pct = self.brokerage_pct if pct is None else pct
        floor = self.brokerage_min if floor is None else floor
        b = min(flat, pct * value)
        return b if b >= floor else min(floor, self.brokerage_min_pct * value)


GROWW = ChargeSchedule()


@dataclass
class CostModel:
    brokerage_flat: float = GROWW.brokerage_flat
    brokerage_pct: float = GROWW.brokerage_pct
    brokerage_min: float = GROWW.brokerage_min
    stt_intraday_sell: float = GROWW.stt_intraday_sell
    stt_delivery: float = GROWW.stt_delivery
    exchange_txn: float = GROWW.exchange_txn
    sebi_fee: float = GROWW.sebi_fee
    stamp_intraday_buy: float = GROWW.stamp_intraday_buy
    stamp_delivery_buy: float = GROWW.stamp_delivery_buy
    gst: float = GROWW.gst
    dp_charge_per_sell: float = GROWW.dp_charge_per_sell
    mtf_interest_per_day: float = GROWW.mtf_interest_per_day

    def leg(self, side: Side, qty: int, price: float, product: Product) -> float:
        """Total charges for one executed order (one leg)."""
        value = qty * price
        if value <= 0:
            return 0.0
        brokerage = GROWW.brokerage(value, self.brokerage_flat, self.brokerage_pct, self.brokerage_min)
        intraday = product is Product.MIS
        if intraday:
            stt = value * self.stt_intraday_sell if side is Side.SELL else 0.0
            stamp = value * self.stamp_intraday_buy if side is Side.BUY else 0.0
            dp = 0.0
        else:
            stt = value * self.stt_delivery
            stamp = value * self.stamp_delivery_buy if side is Side.BUY else 0.0
            dp = self.dp_charge_per_sell if side is Side.SELL else 0.0
        exch = value * self.exchange_txn
        sebi = value * self.sebi_fee
        gst = (brokerage + exch + sebi) * self.gst
        return round(brokerage + stt + exch + sebi + stamp + gst + dp, 2)

    def round_trip(self, entry_side: Side, qty: int, entry: float, exit_: float, product: Product) -> float:
        return round(
            self.leg(entry_side, qty, entry, product) + self.leg(entry_side.opposite(), qty, exit_, product),
            2,
        )

    def mtf_interest(self, funded_amount: float, days: int) -> float:
        return round(funded_amount * self.mtf_interest_per_day * max(days, 0), 2)
