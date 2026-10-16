"""In-process paper broker that fills against live (or replayed) prices.

Fill rules are deliberately pessimistic:
- Marketable LIMIT orders fill at the worse of LTP plus slippage and the limit; a
  limit that is not marketable stays pending until price reaches it.
- Stop orders (SL / SL_M) trigger when LTP crosses the trigger and fill at LTP
  minus slippage, even past the limit price. A real SL-limit order might not fill
  at all on a gap, which would be worse, so the engine also checks stops itself.
"""

from __future__ import annotations

import itertools
import threading
from dataclasses import replace

from ..models import BrokerPosition, Order, OrderRequest, OrderStatus, OrderType, Side
from .base import BrokerError


class PaperBroker:
    name = "paper"

    def __init__(self, starting_cash: float, slippage_bps: float = 5.0) -> None:
        self.cash = starting_cash
        self.slip = slippage_bps / 10_000.0
        self._prices: dict[str, float] = {}
        self._orders: dict[str, Order] = {}
        self._positions: dict[tuple[str, str], BrokerPosition] = {}
        self._ids = itertools.count(1)
        self._lock = threading.Lock()

    # Price feed

    def update_price(self, symbol: str, price: float) -> list[Order]:
        """Feed a new LTP. Returns orders that filled as a result."""
        with self._lock:
            self._prices[symbol] = price
            filled = []
            for order in list(self._orders.values()):
                if order.status is OrderStatus.PENDING and order.request.symbol == symbol:
                    if self._try_fill(order, price):
                        filled.append(order)
            return filled

    # Broker protocol

    def place_order(self, req: OrderRequest) -> Order:
        if req.qty <= 0:
            raise BrokerError("quantity must be positive")
        with self._lock:
            order = Order(order_id=f"PAPER{next(self._ids):06d}", request=req, status=OrderStatus.PENDING)
            self._orders[order.order_id] = order
            price = self._prices.get(req.symbol)
            if price is not None:
                self._try_fill(order, price)
            return replace(order)

    def cancel_order(self, order_id: str) -> Order:
        with self._lock:
            order = self._get(order_id)
            if not order.status.is_terminal:
                order.status = OrderStatus.CANCELLED
            return replace(order)

    def order_status(self, order_id: str) -> Order:
        with self._lock:
            return replace(self._get(order_id))

    def positions(self) -> list[BrokerPosition]:
        with self._lock:
            return [replace(p) for p in self._positions.values() if p.qty != 0]

    def ltp(self, symbols: list[str]) -> dict[str, float]:
        with self._lock:
            return {s: self._prices[s] for s in symbols if s in self._prices}

    def available_cash(self) -> float | None:
        # Paper mode does not model broker margin; RiskManager falls back to capital-based limits.
        return None

    # Internals

    def _get(self, order_id: str) -> Order:
        try:
            return self._orders[order_id]
        except KeyError:
            raise BrokerError(f"unknown order {order_id}") from None

    def _try_fill(self, order: Order, ltp: float) -> bool:
        req = order.request
        buy = req.side is Side.BUY
        fill: float | None = None
        if req.order_type is OrderType.MARKET:
            fill = ltp * (1 + self.slip) if buy else ltp * (1 - self.slip)
        elif req.order_type is OrderType.LIMIT:
            assert req.price is not None
            if (buy and ltp <= req.price) or (not buy and ltp >= req.price):
                fill = min(ltp * (1 + self.slip), req.price) if buy else max(ltp * (1 - self.slip), req.price)
        else:  # SL / SL_M
            assert req.trigger_price is not None
            if (buy and ltp >= req.trigger_price) or (not buy and ltp <= req.trigger_price):
                fill = ltp * (1 + self.slip) if buy else ltp * (1 - self.slip)
        if fill is None:
            return False
        fill = round(fill, 2)
        order.status = OrderStatus.FILLED
        order.filled_qty = req.qty
        order.avg_price = fill
        self._apply_fill(req, fill)
        return True

    def _apply_fill(self, req: OrderRequest, price: float) -> None:
        key = (req.symbol, req.product.value)
        pos = self._positions.get(key) or BrokerPosition(req.symbol, req.product, 0, 0.0, req.exchange)
        signed = req.qty * req.side.sign
        new_qty = pos.qty + signed
        if pos.qty == 0 or (pos.qty > 0) == (signed > 0):
            # opening or adding
            total = abs(pos.qty) + req.qty
            pos.avg_price = (pos.avg_price * abs(pos.qty) + price * req.qty) / total
        elif new_qty != 0 and (new_qty > 0) != (pos.qty > 0):
            # flipped through zero
            pos.avg_price = price
        pos.qty = new_qty
        if new_qty == 0:
            pos.avg_price = 0.0
        self.cash -= signed * price
        self._positions[key] = pos
