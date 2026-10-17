export type Side = "BUY" | "SELL";

export type Position = {
  symbol: string; side: Side; qty: number; entry: number; stop: number; target: number; ltp: number;
  unrealized: number; opened_at: string; product: string;
};

export type Heartbeat = {
  at: string; wall_at?: string; mode: "paper" | "live" | "replay"; strategy?: string; open_positions: number;
  positions?: Position[]; realized_pnl: number; unrealized_pnl?: number; trades_today?: number; halted: boolean;
  halt_reason?: string; market_open?: boolean; capital?: number; llm_enabled?: boolean; reviewer?: string;
  trading?: "running" | "stopped"; feed?: { source: string; ok: boolean; message: string } | null;
};

export type ParamSpec = { name: string; label: string; type: "int" | "float"; min: number; max: number; step: number; default: number };
export type StrategyInfo = { name: string; label: string; description: string; params: ParamSpec[] };

export type EffectiveSettings = {
  editable: Record<string, unknown> & {
    strategy: string; strategy_params: Record<string, number>; symbols: string[]; capital: number;
    risk_per_trade_pct: number; max_daily_loss_pct: number; max_open_positions: number; max_trades_per_day: number;
    max_leverage: number; max_position_notional_pct: number; max_stop_distance_pct: number; allow_short: boolean;
    entry_start: string; entry_end: string; flatten_at: string; price_protection_pct: number; llm_enabled: boolean;
    llm_effort: string; llm_fail_mode: string; llm_min_confidence: number;
  };
  bounds: Record<string, { type: string; min: number | null; max: number | null }>;
  env_only: {
    live_trading_enabled: boolean; allow_mtf_api: boolean; require_login_confirmation: boolean;
    static_ip_configured: boolean; groww_configured: boolean; llm_model: string; orders_per_second: number;
  };
  hard_ceilings: Record<string, number | string>;
  llm_efforts: string[];
  rejected: Record<string, string>;
};

export type Control = {
  kill_switch?: boolean; paused?: boolean; trading_enabled?: boolean; login_confirmed_for?: string; heartbeat?: Heartbeat;
  effective_settings?: EffectiveSettings; settings_overrides?: Record<string, unknown>; strategy_catalog?: StrategyInfo[];
};

export type Signal = {
  id: string; created_at: string; symbol: string; side: Side; strategy: string; signal_ts: string; entry: number;
  stop: number; target: number; reason: string; mode: string;
};
export type Decision = {
  signal_id: string; approve: boolean; size_multiplier: number; confidence: number; rationale: string;
  risk_flags: string[]; model: string; latency_ms: number; error: string | null;
};
export type Outcome = {
  signal_id: string; symbol: string; strategy: string; side: Side; llm_decision: "approve" | "reject" | "none";
  risk_approved: boolean; outcome: "stop" | "target" | "eod"; r_multiple: number; closed_at: string; mode: string;
};
export type Trade = {
  id: string; symbol: string; side: Side; qty: number; entry_price: number; exit_price: number; opened_at: string;
  closed_at: string; exit_reason: string; gross_pnl: number; net_pnl: number; costs: number; strategy: string; mode: string;
};
export type EventRow = { id: string; created_at: string; kind: string; message: string };
export type EquityPoint = { at: string; realized_pnl: number; unrealized_pnl: number; mode: string };
export type OrderRow = {
  id: string; created_at: string; order_id: string; purpose: string; symbol: string; side: Side; order_type: string;
  qty: number; price: number | null; trigger_price: number | null; status: string; avg_price: number | null; mode: string;
};

export type SignalCard = Signal & { decision?: Decision; outcome?: Outcome };

export type LiveState = {
  control: Control; sessionDay: string; signals: SignalCard[]; events: EventRow[]; tradesToday: Trade[];
  equityToday: EquityPoint[]; serverTime: string;
};

export type Metrics = Record<string, number | null | Record<string, number>>;
export type BacktestResult = {
  metrics: Metrics & { net_pnl: number; trades: number };
  equity: { date: string; equity: number; pnl: number }[];
  per_symbol: Record<string, { trades: number; net_pnl: number; wins: number }>;
  trades: { symbol: string; side: Side; qty: number; entry: number; exit: number; opened_at: string; closed_at: string; reason: string; costs: number; net_pnl: number }[];
  strategy: string; strategy_params: Record<string, number>; data_note: string;
};
export type SweepRow = {
  params: Record<string, number>; robust: boolean;
  in_sample: Record<string, number | null>; out_of_sample: Record<string, number | null>;
};
export type SweepResult = {
  strategy: string; axes: { name: string; values: number[] }[]; rows: SweepRow[]; split_date: string;
  in_sample_fraction: number; data_note: string; robust_count: number;
};
export type Job = {
  id: string; created_at: string; kind: "backtest" | "sweep"; params: Record<string, unknown>;
  status: "queued" | "running" | "done" | "error"; progress: number; result?: BacktestResult | SweepResult | null; error?: string | null;
};
