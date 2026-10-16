"""Groww Trade API adapter (``growwapi`` >= 1.5.0).

Notes verified against the growwapi 1.5.0 source:
- ``GrowwAPI.get_access_token(api_key, totp=...)`` / ``(api_key, secret=...)`` returns the token string.
- ``place_order`` takes validity, exchange, order_type, product, quantity, segment,
  trading_symbol, transaction_type, order_reference_id, price, trigger_price.
- The SDK defines ``PRODUCT_MTF = "MTF"``, but Groww's public docs list only
  CNC/MIS/NRML, so whether the server accepts MTF orders is unverified.
  MTF stays blocked unless ``TB_ALLOW_MTF_API=true``.

Response field names come from Groww's REST docs. The parsers below accept a few
spellings and fail loudly on anything else, never silently.
"""

from __future__ import annotations

import base64
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from ..clock import now_ist, to_ist, token_is_stale
from ..models import (
    BrokerPosition,
    Order,
    OrderRequest,
    OrderStatus,
    OrderType,
    Product,
)
from ..throttle import OrderThrottle
from .base import BrokerError

log = logging.getLogger(__name__)

SEGMENT_CASH = "CASH"
VALIDITY_DAY = "DAY"

_FILLED = {"EXECUTED", "COMPLETED", "DELIVERY_AWAITED"}
_REJECTED = {"REJECTED", "FAILED"}
_CANCELLED = {"CANCELLED"}


def map_status(raw_status: str | None, filled_qty: int, qty: int) -> OrderStatus:
    st = (raw_status or "").upper()
    if st in _REJECTED:
        return OrderStatus.REJECTED
    if st in _CANCELLED:
        return OrderStatus.PARTIAL if 0 < filled_qty < qty else OrderStatus.CANCELLED
    if st in _FILLED and filled_qty >= qty:
        return OrderStatus.FILLED
    if filled_qty > 0:
        return OrderStatus.PARTIAL if filled_qty < qty else OrderStatus.FILLED
    return OrderStatus.PENDING


def _first(d: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return default


def key_role(api_key: str) -> str | None:
    """The key type embedded in a Groww API key (a JWT): ``auth-totp`` or an approval-type role.

    Decoded locally without verifying the signature, only to give clear setup errors.
    """
    try:
        payload = api_key.split(".")[1]
        claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        sub = claims.get("sub")
        sub = json.loads(sub) if isinstance(sub, str) else (sub or {})
        return sub.get("role")
    except Exception:
        return None


def is_base32(secret: str) -> bool:
    return bool(re.fullmatch(r"[A-Z2-7]+=*", secret.replace(" ", "").upper()))


class GrowwSession:
    """Obtains and caches the daily Groww access token.

    Tokens expire at 6:00 AM IST and the token endpoint allows only 150 requests
    per day, so the token is cached on disk and reused until it goes stale.
    """

    def __init__(
        self,
        api_key: str,
        totp_secret: str | None = None,
        api_secret: str | None = None,
        cache_path: Path | None = None,
    ) -> None:
        if not api_key:
            raise BrokerError("GROWW_API_KEY is required")
        if not (totp_secret or api_secret):
            raise BrokerError("set GROWW_TOTP_SECRET (TOTP flow) or GROWW_API_SECRET (daily-approval flow)")
        role = key_role(api_key)
        if role == "auth-totp":
            if not totp_secret:
                raise BrokerError(
                    "GROWW_API_KEY is a TOTP-type key, so GROWW_TOTP_SECRET is required "
                    "(the base32 secret shown with the QR code when the key was created)")
            if not is_base32(totp_secret):
                raise BrokerError(
                    "GROWW_TOTP_SECRET is not a valid TOTP secret: TOTP secrets are base32 (letters A-Z and "
                    "digits 2-7, like the text under the QR code). The value set looks like an API secret; "
                    "regenerate the TOTP key on groww.in/trade-api/api-keys and copy the TOTP secret")
            api_secret = None  # TOTP keys log in with codes only
        self.api_key = api_key
        self.totp_secret = totp_secret
        self.api_secret = api_secret
        self.cache_path = cache_path

    def _load_cached(self, now: datetime) -> str | None:
        if not self.cache_path or not self.cache_path.exists():
            return None
        try:
            data = json.loads(self.cache_path.read_text())
            issued = datetime.fromisoformat(data["issued_at"])
            if not token_is_stale(issued, now):
                return data["token"]
        except (KeyError, ValueError, json.JSONDecodeError):
            log.warning("ignoring unreadable Groww token cache")
        return None

    def token(self, force_refresh: bool = False) -> tuple[str, bool]:
        """Return (token, freshly_issued)."""
        now = now_ist()
        if not force_refresh:
            cached = self._load_cached(now)
            if cached:
                return cached, False
        from growwapi import GrowwAPI

        if self.totp_secret:
            import pyotp

            code = pyotp.TOTP(self.totp_secret.replace(" ", "").upper()).now()
            token = GrowwAPI.get_access_token(api_key=self.api_key, totp=code)
        else:
            token = GrowwAPI.get_access_token(api_key=self.api_key, secret=self.api_secret)
        if self.cache_path:
            self.cache_path.parent.mkdir(parents=True, exist_ok=True)
            self.cache_path.write_text(json.dumps({"token": token, "issued_at": now.isoformat()}))
            self.cache_path.chmod(0o600)
        return token, True


class GrowwBroker:
    name = "groww"

    def __init__(self, client: Any, throttle: OrderThrottle, allow_mtf: bool = False, exchange: str = "NSE") -> None:
        self.client = client
        self.throttle = throttle
        self.allow_mtf = allow_mtf
        self.exchange = exchange
        self._requests: dict[str, OrderRequest] = {}

    @classmethod
    def connect(cls, session: GrowwSession, throttle: OrderThrottle, allow_mtf: bool = False, exchange: str = "NSE"):
        from growwapi import GrowwAPI

        token, _ = session.token()
        return cls(GrowwAPI(token), throttle, allow_mtf=allow_mtf, exchange=exchange)

    # Orders

    def place_order(self, req: OrderRequest) -> Order:
        if req.product is Product.MTF and not self.allow_mtf:
            raise BrokerError("MTF orders via API are disabled (TB_ALLOW_MTF_API=false)")
        if req.order_type in (OrderType.LIMIT, OrderType.SL) and not req.price:
            raise BrokerError(f"{req.order_type.value} order needs a price")
        if req.order_type in (OrderType.SL, OrderType.SL_M) and not req.trigger_price:
            raise BrokerError(f"{req.order_type.value} order needs a trigger price")
        self.throttle.acquire()
        try:
            resp = self.client.place_order(
                validity=VALIDITY_DAY,
                exchange=req.exchange,
                order_type=req.order_type.value,
                product=req.product.value,
                quantity=int(req.qty),
                segment=SEGMENT_CASH,
                trading_symbol=req.symbol,
                transaction_type=req.side.value,
                order_reference_id=req.reference_id,
                price=round(req.price, 2) if req.price else 0.0,
                trigger_price=round(req.trigger_price, 2) if req.trigger_price else None,
            )
        except Exception as e:
            raise BrokerError(f"place_order failed for {req.symbol}: {e}") from e
        order_id = _first(resp or {}, "groww_order_id", "order_id")
        if not order_id:
            raise BrokerError(f"place_order returned no order id: {resp!r}")
        self._requests[order_id] = req
        status = map_status(_first(resp, "order_status"), 0, req.qty)
        return Order(order_id=order_id, request=req, status=status, message=str(_first(resp, "remark", default="")), raw=resp)

    def cancel_order(self, order_id: str) -> Order:
        self.throttle.acquire()
        try:
            self.client.cancel_order(groww_order_id=order_id, segment=SEGMENT_CASH)
        except Exception as e:
            raise BrokerError(f"cancel_order failed for {order_id}: {e}") from e
        return self.order_status(order_id)

    def order_status(self, order_id: str) -> Order:
        try:
            d = self.client.get_order_detail(segment=SEGMENT_CASH, groww_order_id=order_id)
        except Exception as e:
            raise BrokerError(f"get_order_detail failed for {order_id}: {e}") from e
        return self._parse_order(order_id, d or {})

    def _parse_order(self, order_id: str, d: dict[str, Any]) -> Order:
        req = self._requests.get(order_id)
        qty = int(_first(d, "quantity", default=req.qty if req else 0) or 0)
        filled = int(_first(d, "filled_quantity", default=0) or 0)
        avg = _first(d, "average_fill_price", "avg_fill_price", "average_price")
        if req is None:
            from ..models import Side

            req = OrderRequest(
                symbol=str(_first(d, "trading_symbol", default="?")),
                side=Side(str(_first(d, "transaction_type", default="BUY")).upper()),
                qty=qty,
                product=Product(str(_first(d, "product", default="MIS")).upper()),
                order_type=OrderType(str(_first(d, "order_type", default="LIMIT")).upper()),
                price=_first(d, "price"),
                trigger_price=_first(d, "trigger_price"),
            )
        return Order(
            order_id=order_id,
            request=req,
            status=map_status(_first(d, "order_status"), filled, qty or req.qty),
            filled_qty=filled,
            avg_price=float(avg) if avg not in (None, 0, "0") else None,
            message=str(_first(d, "remark", default="")),
            raw=d,
        )

    # Portfolio and data

    def positions(self) -> list[BrokerPosition]:
        try:
            resp = self.client.get_positions_for_user(segment=SEGMENT_CASH)
        except Exception as e:
            raise BrokerError(f"get_positions_for_user failed: {e}") from e
        out = []
        for p in (resp or {}).get("positions", []):
            qty = int(_first(p, "quantity", "net_quantity", default=0) or 0)
            if qty == 0:
                continue
            try:
                product = Product(str(_first(p, "product", default="MIS")).upper())
            except ValueError:
                log.warning("skipping position with unsupported product: %s", p)
                continue
            out.append(
                BrokerPosition(
                    symbol=str(_first(p, "trading_symbol", default="?")),
                    product=product,
                    qty=qty,
                    avg_price=float(_first(p, "net_price", "average_price", default=0.0) or 0.0),
                    exchange=str(_first(p, "exchange", default=self.exchange)),
                )
            )
        return out

    def ltp(self, symbols: list[str]) -> dict[str, float]:
        if not symbols:
            return {}
        out: dict[str, float] = {}
        # Groww allows up to 50 instruments per LTP call.
        for i in range(0, len(symbols), 50):
            chunk = symbols[i : i + 50]
            keys = tuple(f"{self.exchange}_{s}" for s in chunk)
            try:
                resp = self.client.get_ltp(exchange_trading_symbols=keys, segment=SEGMENT_CASH)
            except Exception as e:
                raise BrokerError(f"get_ltp failed: {e}") from e
            for s, k in zip(chunk, keys, strict=True):
                v = (resp or {}).get(k)
                if v is not None:
                    out[s] = float(v)
        return out

    def available_cash(self) -> float | None:
        try:
            m = self.client.get_available_margin_details() or {}
        except Exception as e:
            log.warning("margin lookup failed: %s", e)
            return None
        eq = m.get("equity_margin_details") or {}
        v = _first(eq, "mis_balance_available", "cnc_balance_available")
        if v is None:
            v = _first(m, "clear_cash")
        return float(v) if v is not None else None


def last_login(cache_path: Path) -> datetime | None:
    try:
        return to_ist(datetime.fromisoformat(json.loads(cache_path.read_text())["issued_at"]))
    except Exception:
        return None
