-- Platform tables for the interactive dashboard: research jobs, intraday equity, signal outcomes.
-- Same security model as the init migration: RLS on, no policies, service-role access only.

-- Replay mode journals like paper trading, tagged mode = 'replay'.
alter table public.signals drop constraint if exists signals_mode_check;
alter table public.signals add constraint signals_mode_check check (mode in ('paper', 'live', 'replay'));

-- Research jobs queued by the dashboard and executed by `thunderbot jobs`.
create table if not exists public.jobs (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  kind text not null check (kind in ('backtest', 'sweep')),
  params jsonb not null default '{}'::jsonb,
  status text not null default 'queued' check (status in ('queued', 'running', 'done', 'error')),
  progress numeric(5, 3) not null default 0,
  result jsonb,
  error text,
  trace text,
  started_at timestamptz,
  finished_at timestamptz
);
create index if not exists jobs_status_idx on public.jobs (status, created_at);
create index if not exists jobs_created_at_idx on public.jobs (created_at desc);

-- Intraday equity snapshots (realized + unrealized), one per minute while the market is open.
create table if not exists public.equity (
  id uuid primary key,
  created_at timestamptz not null default now(),
  at timestamptz not null,
  mode text not null,
  realized_pnl numeric(14, 2) not null,
  unrealized_pnl numeric(14, 2) not null,
  open_positions integer not null default 0
);
create index if not exists equity_at_idx on public.equity (at desc);

-- Every signal tracked to its stop / target / end of day, whether or not it was traded.
-- Comparing r_multiple by llm_decision shows whether the reviewer's vetoes avoid losers.
create table if not exists public.signal_outcomes (
  id uuid primary key,
  created_at timestamptz not null default now(),
  signal_id uuid not null,
  symbol text not null,
  strategy text not null,
  side text not null,
  entry numeric(14, 2) not null,
  stop numeric(14, 2) not null,
  target numeric(14, 2) not null,
  signal_ts timestamptz not null,
  llm_decision text not null check (llm_decision in ('approve', 'reject', 'none')),
  llm_size_multiplier numeric(6, 4),
  risk_approved boolean not null,
  exit_price numeric(14, 2) not null,
  outcome text not null check (outcome in ('stop', 'target', 'eod')),
  closed_at timestamptz not null,
  r_multiple numeric(10, 3) not null,
  mode text not null
);
create index if not exists signal_outcomes_closed_idx on public.signal_outcomes (closed_at desc);

alter table public.jobs enable row level security;
alter table public.equity enable row level security;
alter table public.signal_outcomes enable row level security;
