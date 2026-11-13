"""Runtime settings loaded from environment variables.

Some limits have *hard ceilings* that configuration cannot raise. They encode
regulatory or broker limits (SEBI's 10 orders/second threshold for unregistered
retail algos, Groww's 250 orders/minute, the roughly 5x intraday leverage that
peak-margin rules allow). The engine clamps to them silently and records a
warning.
"""

from __future__ import annotations

import dataclasses
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .clock import MarketClock, load_holidays, parse_hhmm

# Hard ceilings, which configuration cannot raise.
HARD_MAX_ORDERS_PER_SECOND = 9  # stay strictly below SEBI's 10 OPS registration threshold
HARD_MAX_ORDERS_PER_MINUTE = 250  # Groww order rate limit
HARD_MAX_LEVERAGE = 5.0  # ~20% upfront margin for MIS under peak-margin rules
HARD_MAX_RISK_PER_TRADE_PCT = 2.0
HARD_MAX_DAILY_LOSS_PCT = 10.0
LATEST_FLATTEN = "15:15"  # Groww auto-squares MIS at 15:20

LLM_EFFORTS = ("low", "medium", "high", "xhigh", "max")
# Liquid Nifty 50 names: tight spreads, and Yahoo serves 5-minute bars for all of them.
AI_UNIVERSE = ("RELIANCE", "HDFCBANK", "ICICIBANK", "INFY", "TCS", "SBIN", "AXISBANK", "KOTAKBANK", "LT", "ITC",
               "BHARTIARTL", "BAJFINANCE", "MARUTI", "SUNPHARMA", "TATASTEEL", "NTPC", "ADANIENT", "ADANIPORTS",
               "TITAN", "HCLTECH", "JSWSTEEL", "HINDALCO", "COALINDIA", "ONGC")
DEFAULT_HOLIDAYS = Path(__file__).parent / "universes" / "nse_holidays.txt"  # used when TB_HOLIDAYS_FILE is unset

# Keys the dashboard may change at runtime, with (type, min, max) bounds.
# Live trading, MTF, the static IP, credentials and login policy are deliberately absent:
# they can only be changed in the worker's environment on the VPS.
OVERRIDABLE: dict[str, tuple[str, float | None, float | None]] = {
    "capital": ("float", 1_000, 100_000_000),
    "risk_per_trade_pct": ("float", 0.05, HARD_MAX_RISK_PER_TRADE_PCT),
    "max_daily_loss_pct": ("float", 0.1, HARD_MAX_DAILY_LOSS_PCT),
    "max_open_positions": ("int", 1, 20),
    "max_trades_per_day": ("int", 1, 50),
    "max_leverage": ("float", 0.1, HARD_MAX_LEVERAGE),
    "max_position_notional_pct": ("float", 1, 100),
    "max_stop_distance_pct": ("float", 0.1, 10),
    "allow_short": ("bool", None, None),
    "symbols": ("symbols", None, None),
    "entry_start": ("hhmm", None, None),
    "entry_end": ("hhmm", None, None),
    "flatten_at": ("hhmm", None, None),
    "price_protection_pct": ("float", 0.05, 3),
    "llm_enabled": ("bool", None, None),
    "llm_effort": ("enum", None, None),
    "llm_fail_mode": ("enum", None, None),
    "llm_min_confidence": ("float", 0, 1),
    "strategy": ("strategy", None, None),
    "strategy_params": ("params", None, None),
}


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
    # Strategy
    strategy: str = "orb"
    strategy_params: dict[str, Any] = field(default_factory=dict)

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
    # An OpenAI-compatible endpoint for the AI desk's trader (xAI Grok, Groq, OpenAI, OpenRouter, ...).
    llm_api_key: str | None = field(default=None, repr=False)
    llm_base_url: str | None = None
    llm_chat_model: str | None = None
    # Anthropic's own API. Set from ANTHROPIC_API_KEY or from a key saved in the dashboard; when unset the
    # SDK still looks for its usual credentials.
    anthropic_api_key: str | None = field(default=None, repr=False)
    llm_source: str | None = None  # "dashboard" | "environment" | None: where the LLM key came from
    llm_preset: str | None = None  # the setup screen's provider id, when the key was saved there

    # AI desk (intraday, ML-scored setups decided by the LLM). Paper only on a serverless worker.
    ai_symbols: list[str] = field(default_factory=lambda: list(AI_UNIVERSE))

    # Groww credentials and compliance
    groww_api_key: str | None = field(default=None, repr=False)
    groww_totp_secret: str | None = field(default=None, repr=False)
    groww_api_secret: str | None = field(default=None, repr=False)
    groww_source: str | None = None  # "dashboard" | "environment" | None
    expected_static_ip: str | None = None
    invest_strategy: str = "core_mix"  # daily strategy: core_mix | etf_trend | etf_rank | index_trend | momentum
    invest_at: str = "15:10"  # IST time of the daily decision (prices then stand in for the close)
    invest_cutoff: str = "15:25"  # a live run that starts after this does not trade; it tries again next session
    liquid_symbol: str = "LIQUIDCASE"  # the growth-type liquid ETF that idle money is parked in
    slab_rate_pct: float = 30.0  # your marginal income-tax rate, for liquid and short-term gold ETF gains
    # Drift corridor: a holding is out when it is this many points from its target, or this share of its
    # own target away, whichever comes first. Shown on the dashboard; used by the plan's band option.
    band_abs_pct: float = 5.0
    band_rel_pct: float = 20.0
    harvest_via: str = "t_plus_1"  # how a tax harvest buys back: t_plus_1 (next session) | twin (a twin fund, same day)
    tick_minutes: float = 15.0  # the longest gap between scheduler calls in market hours (Vercel's free tier)
    cron_secret: str | None = None  # shared secret the schedulers send to the serverless worker
    telegram_token: str | None = field(default=None, repr=False)
    telegram_chat_id: str | None = None
    ntfy_topic: str | None = None
    feed: str = "yahoo"  # price source for paper trading: groww (official, paid plan) | yahoo (free, can lag)
    live_trading_enabled: bool = False
    allow_mtf_api: bool = False
    require_login_confirmation: bool = True

    # Persistence
    data_dir: str = "var"
    backtest_data_dir: str = "data/groww"
    supabase_url: str | None = None
    supabase_service_key: str | None = field(default=None, repr=False)

    # The environment's own credential values, kept so keys saved in the dashboard can be re-applied or
    # dropped on a later pass (see credentials.apply_credentials). Never shown.
    env_credentials: dict[str, Any] | None = field(default=None, repr=False)

    warnings: list[str] = field(default_factory=list)

    @classmethod
    def from_env(cls) -> "Settings":
        s = cls(
            strategy=_env("TB_STRATEGY", cls.strategy) or cls.strategy,
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
            # With a chat endpoint configured the LLM is on unless TB_LLM_ENABLED says otherwise.
            llm_enabled=_env_bool("TB_LLM_ENABLED", bool(_env("LLM_API_KEY") and _env("LLM_BASE_URL") and _env("LLM_MODEL"))),
            llm_api_key=_env("LLM_API_KEY"),
            anthropic_api_key=_env("ANTHROPIC_API_KEY"),
            llm_base_url=_env("LLM_BASE_URL"),
            llm_chat_model=_env("LLM_MODEL"),
            ai_symbols=_env_list("TB_AI_SYMBOLS", list(AI_UNIVERSE)),
            llm_model=_env("TB_LLM_MODEL", cls.llm_model) or cls.llm_model,
            llm_effort=_env("TB_LLM_EFFORT", cls.llm_effort) or cls.llm_effort,
            llm_fail_mode=(_env("TB_LLM_FAIL_MODE", cls.llm_fail_mode) or cls.llm_fail_mode).lower(),
            llm_timeout_seconds=_env_float("TB_LLM_TIMEOUT_SECONDS", cls.llm_timeout_seconds),
            llm_min_confidence=_env_float("TB_LLM_MIN_CONFIDENCE", cls.llm_min_confidence),
            groww_api_key=_env("GROWW_API_KEY"),
            groww_source="environment" if _env("GROWW_API_KEY") else None,
            groww_totp_secret=_env("GROWW_TOTP_SECRET"),
            groww_api_secret=_env("GROWW_API_SECRET"),
            expected_static_ip=_env("TB_EXPECTED_STATIC_IP"),
            live_trading_enabled=_env_bool("TB_LIVE_TRADING_ENABLED", False),
            allow_mtf_api=_env_bool("TB_ALLOW_MTF_API", False),
            require_login_confirmation=_env_bool("TB_REQUIRE_LOGIN_CONFIRMATION", True),
            feed=(_env("TB_FEED", cls.feed) or cls.feed).strip().lower(),
            invest_strategy=(_env("TB_INVEST_STRATEGY", cls.invest_strategy) or cls.invest_strategy).strip().lower(),
            invest_at=_env("TB_INVEST_AT", cls.invest_at) or cls.invest_at,
            invest_cutoff=_env("TB_INVEST_CUTOFF", cls.invest_cutoff) or cls.invest_cutoff,
            liquid_symbol=(_env("TB_LIQUID_SYMBOL", cls.liquid_symbol) or cls.liquid_symbol).strip().upper(),
            slab_rate_pct=_env_float("TB_SLAB_RATE_PCT", cls.slab_rate_pct),
            band_abs_pct=min(max(_env_float("TB_BAND_ABS_PCT", cls.band_abs_pct), 0.5), 25.0),
            band_rel_pct=min(max(_env_float("TB_BAND_REL_PCT", cls.band_rel_pct), 1.0), 100.0),
            harvest_via=(_env("TB_HARVEST_VIA", cls.harvest_via) or cls.harvest_via).strip().lower(),
            tick_minutes=_env_float("TB_TICK_MINUTES", cls.tick_minutes),
            cron_secret=_env("CRON_SECRET"),
            telegram_token=_env("TB_TELEGRAM_TOKEN"),
            telegram_chat_id=_env("TB_TELEGRAM_CHAT_ID"),
            ntfy_topic=_env("TB_NTFY_TOPIC"),
            data_dir=_env("TB_DATA_DIR", cls.data_dir) or cls.data_dir,
            backtest_data_dir=_env("TB_BACKTEST_DATA_DIR", cls.backtest_data_dir) or cls.backtest_data_dir,
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
        if self.feed not in ("groww", "yahoo"):
            self.warnings.append(f"TB_FEED={self.feed!r} is not groww or yahoo; using yahoo")
            self.feed = "yahoo"
        self.slab_rate_pct = min(max(self.slab_rate_pct, 0.0), 45.0)
        if self.llm_fail_mode not in ("reject", "pass"):
            self.warnings.append(f"llm_fail_mode={self.llm_fail_mode!r} invalid; using 'reject'")
            self.llm_fail_mode = "reject"

    def with_overrides(self, overrides: dict[str, Any] | None) -> tuple["Settings", dict[str, str]]:
        """Return a copy with dashboard overrides applied, plus {key: reason} for rejected keys.

        Always derive from the env-loaded base settings so overrides never accumulate.
        """
        from .strategy import STRATEGIES, coerce_params

        new = dataclasses.replace(self, warnings=[], symbols=list(self.symbols), strategy_params=dict(self.strategy_params),
                                  ai_symbols=list(self.ai_symbols))
        rejected: dict[str, str] = {}
        for key, value in (overrides or {}).items():
            spec = OVERRIDABLE.get(key)
            if spec is None:
                rejected[key] = "not editable from the dashboard"
                continue
            kind, lo, hi = spec
            try:
                if kind in ("float", "int"):
                    v = float(value)
                    if lo is not None and v < lo or hi is not None and v > hi:
                        rejected[key] = f"must be between {lo} and {hi}"
                        continue
                    setattr(new, key, int(v) if kind == "int" else v)
                elif kind == "bool":
                    setattr(new, key, bool(value))
                elif kind == "symbols":
                    syms = [str(x).strip().upper() for x in value if str(x).strip()]
                    if not syms or not all(x.replace("-", "").replace("&", "").isalnum() for x in syms):
                        rejected[key] = "symbols must be non-empty NSE trading symbols"
                        continue
                    new.symbols = syms[:50]
                elif kind == "hhmm":
                    parse_hhmm(str(value))
                    if key == "flatten_at" and str(value) > LATEST_FLATTEN:
                        rejected[key] = f"must be at or before {LATEST_FLATTEN} (Groww squares off MIS at 15:20)"
                        continue
                    setattr(new, key, str(value))
                elif kind == "enum":
                    allowed = LLM_EFFORTS if key == "llm_effort" else ("reject", "pass")
                    if value not in allowed:
                        rejected[key] = f"must be one of {allowed}"
                        continue
                    setattr(new, key, value)
                elif kind == "strategy":
                    if value not in STRATEGIES:
                        rejected[key] = f"unknown strategy; choose from {sorted(STRATEGIES)}"
                        continue
                    new.strategy = value
                elif kind == "params":
                    if not isinstance(value, dict):
                        rejected[key] = "must be an object"
                        continue
                    new.strategy_params = dict(value)
            except (TypeError, ValueError) as e:
                rejected[key] = f"invalid value: {e}"
        if parse_hhmm(new.entry_start) >= parse_hhmm(new.entry_end):
            rejected["entry_window"] = "entry_start must be before entry_end; window left unchanged"
            new.entry_start, new.entry_end = self.entry_start, self.entry_end
        new.strategy_params = coerce_params(new.strategy, new.strategy_params)
        new.apply_hard_limits()
        return new, rejected

    def public_view(self) -> dict[str, Any]:
        """Effective settings for the dashboard. Never includes credentials."""
        editable = {k: getattr(self, k) for k in OVERRIDABLE}
        return {
            "editable": editable,
            "bounds": {k: {"type": t, "min": lo, "max": hi} for k, (t, lo, hi) in OVERRIDABLE.items()},
            "env_only": {
                "live_trading_enabled": self.live_trading_enabled,
                "allow_mtf_api": self.allow_mtf_api,
                "require_login_confirmation": self.require_login_confirmation,
                "static_ip_configured": bool(self.expected_static_ip),
                "expected_static_ip": self.expected_static_ip,
                "groww_configured": bool(self.groww_api_key),
                "groww_source": self.groww_source_view,
                "groww_auth": self.groww_auth,
                "feed": self.feed,
                "liquid_symbol": self.liquid_symbol,
                "slab_rate_pct": self.slab_rate_pct,
                "band_abs_pct": self.band_abs_pct,
                "band_rel_pct": self.band_rel_pct,
                "harvest_via": self.harvest_via,
                "notifications": bool((self.telegram_token and self.telegram_chat_id) or self.ntfy_topic),
                "llm_model": self.llm_chat_model if self.chat_llm else self.llm_model,
                "llm_provider": self.llm_provider,
                "llm_configured": self.chat_llm or self.has_anthropic_key,
                "llm_source": self.llm_source_view,
                "llm_preset": self.llm_preset,
                "ai_symbols": list(self.ai_symbols),
                "orders_per_second": self.orders_per_second,
            },
            "hard_ceilings": {
                "orders_per_second": HARD_MAX_ORDERS_PER_SECOND,
                "orders_per_minute": HARD_MAX_ORDERS_PER_MINUTE,
                "max_leverage": HARD_MAX_LEVERAGE,
                "risk_per_trade_pct": HARD_MAX_RISK_PER_TRADE_PCT,
                "max_daily_loss_pct": HARD_MAX_DAILY_LOSS_PCT,
                "latest_flatten": LATEST_FLATTEN,
            },
            "llm_efforts": list(LLM_EFFORTS),
        }

    @property
    def chat_llm(self) -> bool:
        """True when an OpenAI-compatible endpoint is fully configured."""
        return bool(self.llm_api_key and self.llm_base_url and self.llm_chat_model)

    @property
    def llm_provider(self) -> str:
        if self.chat_llm:
            from .llm.trader import provider_of

            return provider_of(self.llm_base_url)
        return "Anthropic" if self.has_anthropic_key else "none"

    @property
    def has_anthropic_key(self) -> bool:
        return bool(self.anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY"))

    @property
    def llm_source_view(self) -> str | None:
        """Where the LLM key in use came from: the dashboard's setup screen, the environment, or nowhere."""
        if self.llm_source:
            return self.llm_source
        return "environment" if self.chat_llm or self.has_anthropic_key else None

    @property
    def groww_source_view(self) -> str | None:
        if not self.groww_api_key:
            return None
        return self.groww_source or "environment"

    @property
    def groww_auth(self) -> str | None:
        """"totp" for a TOTP-type key (unattended login), "approval" for one that needs daily approval on Groww."""
        if not self.groww_api_key:
            return None
        from .broker.groww import key_role

        if key_role(self.groww_api_key) == "auth-totp" or (self.groww_totp_secret and not self.groww_api_secret):
            return "totp"
        return "approval"

    def clock(self) -> MarketClock:
        return MarketClock(
            entry_start=parse_hhmm(self.entry_start),
            entry_end=parse_hhmm(self.entry_end),
            flatten_at=parse_hhmm(self.flatten_at),
            holidays=load_holidays(self.holidays_file or DEFAULT_HOLIDAYS),
        )

    @property
    def data_path(self) -> Path:
        p = Path(self.data_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p
