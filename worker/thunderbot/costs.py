"""Indian equity transaction cost model.

Defaults approximate Groww equity charges and statutory levies as of late 2026.
They are **configurable estimates**. Reconcile them against your own contract
notes before trusting any backtest. Rates are fractions of turnover, not %.
"""

from __future__ import annotations

from dataclasses import dataclass

from .models import Product, Side


@dataclass
class CostModel:
    brokerage_flat: float = 20.0  # Rs per executed order cap
    brokerage_pct: float = 0.001  # 0.1% of order value, whichever is lower
    brokerage_min: float = 5.0
    stt_intraday_sell: float = 0.00025  # 0.025% on sell side
    stt_delivery: float = 0.001  # 0.1% on buy and sell
    exchange_txn: float = 0.0000297  # NSE cash
    sebi_fee: float = 0.000001  # Rs 10 per crore
    stamp_intraday_buy: float = 0.00003
    stamp_delivery_buy: float = 0.00015
    gst: float = 0.18  # on brokerage + exchange txn + SEBI fee
    dp_charge_per_sell: float = 16.0  # delivery/MTF sell, per scrip per day (approx. incl. GST)
    mtf_interest_per_day: float = 0.00041  # 0.041%/day on the funded amount (Groww MTF page)

    def leg(self, side: Side, qty: int, price: float, product: Product) -> float:
        """Total charges for one executed order (one leg)."""
        value = qty * price
        if value <= 0:
            return 0.0
        brokerage = max(min(self.brokerage_flat, value * self.brokerage_pct), self.brokerage_min)
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
