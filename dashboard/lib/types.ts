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
  style?: "intraday" | "invest"; portfolio?: Portfolio;
  scheduler?: "worker" | "serverless"; next_tick_by?: string;
};

/** Is the worker (or its scheduler) still reporting? A serverless worker says when to expect it next. */
export function workerAlive(hb?: Heartbeat): boolean {
  if (!hb?.wall_at) return false;
  if (hb.next_tick_by) return Date.now() < new Date(hb.next_tick_by).getTime() + 180_000;
  return Date.now() - new Date(hb.wall_at).getTime() < 45_000;
}

export type Holding = { symbol: string; qty: number; avg_price: number; ltp: number; value: number; weight: number; pnl: number; since: string };
export type Portfolio = {
  value: number; cash: number; capital: number; invested_pct: number; holdings: Holding[]; next_rebalance: string;
  last_run: string | null; run_at: string; rebalance: string; realized: number;
  filter: { index: number | null; sma: number | null; above: boolean } | null;
  pending?: boolean; missed?: string | null; liquid_symbol?: string; last_plan?: Plan | null;
  target?: Record<string, number> | null; signals?: Record<string, { price: number; avg: number; above: boolean }> | null;
};
export type PlanOrder = { symbol: string; side: Side; qty: number; price: number; value: number };
export type Plan = { at: string; late: boolean; strategy: string; target: Record<string, number>; orders: PlanOrder[] };
export type DailyStrategy = { name: string; label: string; description: string; params: ParamSpec[] };

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
    static_ip_configured: boolean; groww_configured: boolean; llm_model: string; orders_per_second: number; feed?: string;
    llm_provider?: string; llm_configured?: boolean; ai_symbols?: string[];
    liquid_symbol?: string; slab_rate_pct?: number; notifications?: boolean;
  };
  hard_ceilings: Record<string, number | string>;
  llm_efforts: string[];
  rejected: Record<string, string>;
};

// The AI desk (intraday, paper): what the worker publishes after each 5-minute bar.
export type DeskDecision = {
  id: string; t: string; symbol: string; side: Side; kind: string; entry: number; stop: number; target: number;
  prob: number | null; expected_r: number | null; why: string; verdict: "take" | "skip" | ""; by: string; note: string;
  flags: string[]; confidence?: number; size?: number; qty?: number; status?: string; fill?: number; exit?: string;
  exit_price?: number; pnl?: number; r?: number; outcome?: "stop" | "target" | "eod"; error?: string;
  /** While a role is only watching, `said` and `asked_size` are what it answered and `size` is what was applied (1). */
  stage?: "shadow" | "active"; said?: "take" | "skip"; asked_size?: number;
};
export type DeskPosition = {
  symbol: string; side: Side; qty: number; entry: number; stop: number; target: number; opened_at: string;
  generator: string | null; ml_prob: number | null; ltp: number; unrealized: number;
};
export type DeskWatch = { symbol: string; ltp: number; chg_pct: number; vs_vwap_pct: number; rvol: number | null; m30_pct: number };
export type DeskMarket = {
  label?: string; breadth_up_pct?: number; above_vwap_pct?: number; stocks?: number; index_ret_open_pct?: number;
  index_ret_30m_pct?: number; index_range_pct?: number; index_range_pos?: number; index_last?: number;
};
export type AIDesk = {
  at: string; day: string; status: "running" | "off" | "paused" | "halted" | "closed" | "waiting" | "closing" | "no_prices";
  enabled: boolean; mode: string; bar: string | null; market: DeskMarket; watch: DeskWatch[]; positions: DeskPosition[];
  pending: { symbol: string; side: Side; qty: number; stop: number; target: number }[]; decisions: DeskDecision[];
  stats: { realized: number; unrealized: number; trades: number; wins: number; losses: number; costs: number; halted: boolean; halt_reason: string; setups: number };
  curve: [string, number][]; llm: { on: boolean; provider: string; model: string | null };
  limits: { capital: number; risk_per_trade_pct: number; max_daily_loss_pct: number; max_open_positions: number; max_trades_per_day: number; entry_window: string; flatten_at: string };
  params: { strict?: number; min_prob?: number; min_stop_pct?: number }; universe: number; feed_error: string | null;
  harness_id?: string; memory_mode?: "journal_only" | "inject"; stage?: "shadow" | "active";
};
export type GroupStats = { n: number; win_pct: number | null; avg_r: number | null; total_r: number; t: number | null; floor?: number };
export type ModelSummary = {
  id: string; trained_at: string; days: number; setups: number; symbols: number; min_stop_pct: number; verdict: string; verdict_text: string;
  auc: number | null; best: GroupStats; all: GroupStats; policy: { learn: number; strict: number | null; ev: [number, number] };
};
export type ModelReport = {
  trained_at: string; days: number; first_day: string; last_day: string; setups: number; symbols: number; min_stop_pct: number;
  policy: { learn: number; strict: number | null; ev: [number, number] }; verdict: string; verdict_text: string;
  importance: [string, number][]; note?: string;
  oos: {
    from: string; setups: number; auc: number | null; brier: number; brier_base: number; base_win_pct: number; all: GroupStats;
    by_share: Record<string, GroupStats>; by_generator: Record<string, GroupStats>;
    buckets: { p: number; win_pct: number; avg_r: number; n: number }[]; curve: [string, number, number][];
  };
};
export type AIMemory = {
  lessons?: { day: string; text: string }[];
  last_review?: { day: string; summary: string; by: string; numbers: { net_pnl: number; trades: number; wins: number; setups: number; taken_avg_r: number | null; skipped_avg_r: number | null } };
};
export type AIDay = { day: string; net: number; trades: number; wins: number; costs: number; setups: number };

export type Control = {
  ai_desk?: AIDesk; ai_model?: ModelSummary | null; ai_memory?: AIMemory; ai_history?: AIDay[]; intraday_enabled?: boolean;
  kill_switch?: boolean; paused?: boolean; trading_enabled?: boolean; login_confirmed_for?: string; heartbeat?: Heartbeat;
  effective_settings?: EffectiveSettings; settings_overrides?: Record<string, unknown>; strategy_catalog?: StrategyInfo[];
  daily_catalog?: DailyStrategy[]; invest_settings?: { strategy: string; params: Record<string, number> };
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
  params: Record<string, number>;
  in_sample: Record<string, number | null>; out_of_sample: Record<string, number | null>;
  /** Annualised Sharpe of the daily returns, and its deflated value: the chance it is above zero once
   *  every setting ever tried on this data is counted. Older results carry `robust` instead. */
  sharpe?: number | null; dsr?: number | null; robust?: boolean;
};
export type SweepResult = {
  strategy: string; axes: { name: string; values: number[] }[]; rows: SweepRow[]; split_date: string;
  in_sample_fraction: number; data_note: string; robust_count?: number;
  /** Settings tried on this data so far, across every sweep; the probability the winner was picked by luck; a verdict in words. */
  trials?: number; pbo?: number | null; blocks?: number; verdict?: string;
};
export type InvestMetrics = {
  cagr_pct: number; total_return_pct: number; volatility_pct: number; sharpe: number | null; max_drawdown_pct: number;
  longest_underwater_days: number; final_value: number; years: number;
};
export type InvestResult = {
  metrics: InvestMetrics & { trades: number; costs: number; taxes: number; turnover_per_year: number; time_invested_pct: number;
      rebalances: number; exit_tax?: number; cagr_after_exit_tax_pct?: number | null;
    benchmark: InvestMetrics & { exit_tax?: number; cagr_after_exit_tax_pct?: number | null } };
  yearly: { year: number; strategy_pct: number; benchmark_pct: number | null }[];
  equity: { date: string; value: number; benchmark: number }[];
  strategy: string; strategy_params: Record<string, number>; data_note: string; years: number; capital: number;
  slab_rate_pct?: number; allocation?: Record<string, number>;
  comparators?: { label: string; cagr_pct: number; cagr_after_exit_tax_pct: number | null; max_drawdown_pct: number; final_value: number; trades: number }[];
};
export type Job = {
  id: string; created_at: string; kind: "backtest" | "sweep" | "invest" | "train"; params: Record<string, unknown>;
  status: "queued" | "running" | "done" | "error"; progress: number; result?: BacktestResult | SweepResult | InvestResult | null; error?: string | null;
};
