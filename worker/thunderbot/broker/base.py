from __future__ import annotations

from typing import Protocol

from ..models import BrokerPosition, Order, OrderRequest


class BrokerError(RuntimeError):
    pass


class Broker(Protocol):
    name: str

    def place_order(self, req: OrderRequest) -> Order: ...

    def cancel_order(self, order_id: str) -> Order: ...

    def order_status(self, order_id: str) -> Order: ...

    def positions(self) -> list[BrokerPosition]: ...

    def ltp(self, symbols: list[str]) -> dict[str, float]: ...

    def available_cash(self) -> float | None: ...
