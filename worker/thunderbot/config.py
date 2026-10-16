"""Runtime settings loaded from environment variables.

Some limits have *hard ceilings* that configuration cannot raise. They encode
regulatory or broker limits (SEBI's 10 orders/second threshold for unregistered
retail algos, Groww's 250 orders/minute, the roughly 5x intraday leverage that
peak-margin rules allow). The engine clamps to them silently and records a
warning.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from .clock import MarketClock, load_holidays, parse_hhmm

# Hard ceilings, which configuration cannot raise.
HARD_MAX_ORDERS_PER_SECOND = 9  # stay strictly below SEBI's 10 OPS registration threshold
HARD_MAX_ORDERS_PER_MINUTE = 250  # Groww order rate limit
HARD_MAX_LEVERAGE = 5.0  # ~20% upfront margin for MIS under peak-margin rules
HARD_MAX_RISK_PER_TRADE_PCT = 2.0
HARD_MAX_DAILY_LOSS_PCT = 10.0


def _env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name)
    return value if value not in (None, "") else default


def _env_bool(name: str, default: bool) -> bool:
    value = _env(name)
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def _env_float(name: str, default: float) -> float:
    value = _env(name)
    return float(value) if value is not None else default


def _env_int(name: str, default: int) -> int:
    value = _env(name)
    return int(value) if value is not None else default


def _env_list(name: str, default: list[str]) -> list[str]:
    value = _env(name)
    if value is None:
        return list(default)
    return [s.strip().upper() for s in value.split(",") if s.strip()]


@dataclass
class Settings:
    # Capital and risk
    capital: float = 100_000.0
    risk_per_trade_pct: float = 0.5
    max_daily_loss_pct: float = 2.0
    max_open_positions: int = 3
    max_trades_per_day: int = 6
    max_leverage: float = 1.0
    max_position_notional_pct: float = 50.0  # of capital * leverage, per position
    max_stop_distance_pct: float = 3.0  # reject signals whose stop is further than this
    allow_short: bool = True  # intraday (MIS) shorts only

    # Universe and timing
    symbols: list[str] = field(default_factory=lambda: ["RELIANCE", "HDFCBANK", "INFY", "ICICIBANK", "TCS"])
    exchange: str = "NSE"
    interval_minutes: int = 5
    entry_start: str = "09:30"
    entry_end: str = "14:30"
    flatten_at: str = "15:05"
    holidays_file: str | None = None
    poll_seconds: float = 10.0

    # Execution
    orders_per_second: int = 5
    orders_per_minute: int = 200
    slippage_bps: float = 5.0
    price_protection_pct: float = 0.5  # marketable-limit band instead of MARKET (MPP-friendly)
    stop_limit_buffer_pct: float = 0.5  # SL limit price beyond trigger
    fill_timeout_seconds: float = 20.0

    # LLM review layer
    llm_enabled: bool = False
    llm_model: str = "claude-opus-5-5"
    llm_effort: str = "medium"
    llm_fail_mode: str = "reject"  # reject | pass, i.e. what to do when the LLM call fails
    llm_timeout_seconds: float = 60.0
    llm_min_confidence: float = 0.5

    # Groww credentials and compliance
    groww_api_key: str | None = None
    groww_totp_secret: str | None = None
    groww_api_secret: str | None = None
    expected_static_ip: str | None = None
    live_trading_enabled: bool = False
    allow_mtf_api: bool = False
    require_login_confirmation: bool = True

    # Persistence
    data_dir: str = "var"
    supabase_url: str | None = None
    supabase_service_key: str | None = None

    warnings: list[str] = field(default_factory=list)

    @classmethod
    def from_env(cls) -> "Settings":
        s = cls(
            capital=_env_float("TB_CAPITAL", cls.capital),
            risk_per_trade_pct=_env_float("TB_RISK_PER_TRADE_PCT", cls.risk_per_trade_pct),
            max_daily_loss_pct=_env_float("TB_MAX_DAILY_LOSS_PCT", cls.max_daily_loss_pct),
            max_open_positions=_env_int("TB_MAX_OPEN_POSITIONS", cls.max_open_positions),
            max_trades_per_day=_env_int("TB_MAX_TRADES_PER_DAY", cls.max_trades_per_day),
            max_leverage=_env_float("TB_MAX_LEVERAGE", cls.max_leverage),
            max_position_notional_pct=_env_float("TB_MAX_POSITION_NOTIONAL_PCT", cls.max_position_notional_pct),
            max_stop_distance_pct=_env_float("TB_MAX_STOP_DISTANCE_PCT", cls.max_stop_distance_pct),
            allow_short=_env_bool("TB_ALLOW_SHORT", cls.allow_short),
            symbols=_env_list("TB_SYMBOLS", cls().symbols),
            exchange=_env("TB_EXCHANGE", cls.exchange) or cls.exchange,
            interval_minutes=_env_int("TB_INTERVAL_MINUTES", cls.interval_minutes),
            entry_start=_env("TB_ENTRY_START", cls.entry_start) or cls.entry_start,
            entry_end=_env("TB_ENTRY_END", cls.entry_end) or cls.entry_end,
            flatten_at=_env("TB_FLATTEN_AT", cls.flatten_at) or cls.flatten_at,
            holidays_file=_env("TB_HOLIDAYS_FILE"),
            poll_seconds=_env_float("TB_POLL_SECONDS", cls.poll_seconds),
            orders_per_second=_env_int("TB_ORDERS_PER_SECOND", cls.orders_per_second),
            orders_per_minute=_env_int("TB_ORDERS_PER_MINUTE", cls.orders_per_minute),
            slippage_bps=_env_float("TB_SLIPPAGE_BPS", cls.slippage_bps),
            price_protection_pct=_env_float("TB_PRICE_PROTECTION_PCT", cls.price_protection_pct),
            stop_limit_buffer_pct=_env_float("TB_STOP_LIMIT_BUFFER_PCT", cls.stop_limit_buffer_pct),
            fill_timeout_seconds=_env_float("TB_FILL_TIMEOUT_SECONDS", cls.fill_timeout_seconds),
            llm_enabled=_env_bool("TB_LLM_ENABLED", cls.llm_enabled),
            llm_model=_env("TB_LLM_MODEL", cls.llm_model) or cls.llm_model,
            llm_effort=_env("TB_LLM_EFFORT", cls.llm_effort) or cls.llm_effort,
            llm_fail_mode=(_env("TB_LLM_FAIL_MODE", cls.llm_fail_mode) or cls.llm_fail_mode).lower(),
            llm_timeout_seconds=_env_float("TB_LLM_TIMEOUT_SECONDS", cls.llm_timeout_seconds),
            llm_min_confidence=_env_float("TB_LLM_MIN_CONFIDENCE", cls.llm_min_confidence),
            groww_api_key=_env("GROWW_API_KEY"),
            groww_totp_secret=_env("GROWW_TOTP_SECRET"),
            groww_api_secret=_env("GROWW_API_SECRET"),
            expected_static_ip=_env("TB_EXPECTED_STATIC_IP"),
            live_trading_enabled=_env_bool("TB_LIVE_TRADING_ENABLED", False),
            allow_mtf_api=_env_bool("TB_ALLOW_MTF_API", False),
            require_login_confirmation=_env_bool("TB_REQUIRE_LOGIN_CONFIRMATION", True),
            data_dir=_env("TB_DATA_DIR", cls.data_dir) or cls.data_dir,
            supabase_url=_env("SUPABASE_URL"),
            supabase_service_key=_env("SUPABASE_SERVICE_ROLE_KEY"),
        )
        s.apply_hard_limits()
        return s

    def apply_hard_limits(self) -> None:
        def clamp(name: str, ceiling: float) -> None:
            value = getattr(self, name)
            if value > ceiling:
                self.warnings.append(f"{name}={value} exceeds hard ceiling {ceiling}; clamped")
                setattr(self, name, type(value)(ceiling))

        clamp("orders_per_second", HARD_MAX_ORDERS_PER_SECOND)
        clamp("orders_per_minute", HARD_MAX_ORDERS_PER_MINUTE)
        clamp("max_leverage", HARD_MAX_LEVERAGE)
        clamp("risk_per_trade_pct", HARD_MAX_RISK_PER_TRADE_PCT)
        clamp("max_daily_loss_pct", HARD_MAX_DAILY_LOSS_PCT)
        if self.llm_fail_mode not in ("reject", "pass"):
            self.warnings.append(f"llm_fail_mode={self.llm_fail_mode!r} invalid; using 'reject'")
            self.llm_fail_mode = "reject"

    def clock(self) -> MarketClock:
        return MarketClock(
            entry_start=parse_hhmm(self.entry_start),
            entry_end=parse_hhmm(self.entry_end),
            flatten_at=parse_hhmm(self.flatten_at),
            holidays=load_holidays(self.holidays_file),
        )

    @property
    def data_path(self) -> Path:
        p = Path(self.data_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p
