"""Core domain types shared by the strategy, risk, broker, backtest and engine layers."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


class Side(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

    @property
    def sign(self) -> int:
        return 1 if self is Side.BUY else -1

    def opposite(self) -> "Side":
        return Side.SELL if self is Side.BUY else Side.BUY


class Product(str, enum.Enum):
    CNC = "CNC"  # delivery
    MIS = "MIS"  # intraday, auto squared-off by the broker
    MTF = "MTF"  # margin trading facility; API support unverified, gated by config


class OrderType(str, enum.Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    SL = "SL"
    SL_M = "SL_M"


class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"  # accepted, not yet filled (includes trigger-pending stops)
    FILLED = "FILLED"
    PARTIAL = "PARTIAL"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

    @property
    def is_terminal(self) -> bool:
        return self in (OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED)


@dataclass(frozen=True)
class Candle:
    ts: datetime  # bar start time, timezone-aware IST
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class Signal:
    """A trade idea from the deterministic strategy. Entry/stop/target are fixed here."""

    symbol: str
    side: Side
    product: Product
    entry: float
    stop: float
    target: float
    strategy: str
    ts: datetime
    reason: str = ""
    features: dict[str, Any] = field(default_factory=dict)

    @property
    def risk_per_share(self) -> float:
        return abs(self.entry - self.stop)

    @property
    def reward_risk(self) -> float:
        r = self.risk_per_share
        return abs(self.target - self.entry) / r if r > 0 else 0.0


@dataclass
class OrderRequest:
    symbol: str
    side: Side
    qty: int
    product: Product
    order_type: OrderType
    price: float | None = None
    trigger_price: float | None = None
    reference_id: str | None = None
    exchange: str = "NSE"


@dataclass
class Order:
    order_id: str
    request: OrderRequest
    status: OrderStatus
    filled_qty: int = 0
    avg_price: float | None = None
    message: str = ""
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class BrokerPosition:
    """A position as reported by the broker (net quantity, signed)."""

    symbol: str
    product: Product
    qty: int
    avg_price: float
    exchange: str = "NSE"


@dataclass
class ManagedPosition:
    """A position the engine opened and is responsible for exiting."""

    symbol: str
    side: Side
    product: Product
    qty: int
    entry_price: float
    stop: float
    target: float
    opened_at: datetime
    entry_order_id: str
    stop_order_id: str | None = None
    signal_id: str | None = None
    entry_costs: float = 0.0

    def unrealized(self, ltp: float) -> float:
        return (ltp - self.entry_price) * self.qty * self.side.sign


@dataclass
class ClosedTrade:
    symbol: str
    side: Side
    product: Product
    qty: int
    entry_price: float
    exit_price: float
    opened_at: datetime
    closed_at: datetime
    exit_reason: str
    costs: float
    strategy: str = ""
    signal_id: str | None = None

    @property
    def gross_pnl(self) -> float:
        return (self.exit_price - self.entry_price) * self.qty * self.side.sign

    @property
    def net_pnl(self) -> float:
        return self.gross_pnl - self.costs
