-- Thunderbot schema: audit trail mirrored from the worker's local SQLite journal,
-- plus a small control table the dashboard writes (kill switch, pause, login confirmation).
--
-- Security model: RLS is enabled on every table with NO policies, so the anon and
-- authenticated roles can read or write nothing. Only the service-role key
-- (held by the worker on the VPS and by the dashboard's server-side code) can
-- access these tables. Never expose the service-role key to a browser.

create table if not exists public.events (
  id uuid primary key,
  created_at timestamptz not null default now(),
  kind text not null,
  message text not null,
  data jsonb not null default '{}'::jsonb
);
create index if not exists events_created_at_idx on public.events (created_at desc);
create index if not exists events_kind_idx on public.events (kind, created_at desc);

create table if not exists public.signals (
  id uuid primary key,
  created_at timestamptz not null default now(),
  symbol text not null,
  side text not null check (side in ('BUY', 'SELL')),
  product text not null check (product in ('CNC', 'MIS', 'MTF')),
  strategy text not null,
  signal_ts timestamptz not null,
  entry numeric(14, 2) not null,
  stop numeric(14, 2) not null,
  target numeric(14, 2) not null,
  reason text,
  features jsonb not null default '{}'::jsonb,
  mode text not null check (mode in ('paper', 'live'))
);
create index if not exists signals_created_at_idx on public.signals (created_at desc);

-- One row per LLM review, including the full prompt, for audit and offline evaluation.
create table if not exists public.llm_decisions (
  id uuid primary key,
  created_at timestamptz not null default now(),
  signal_id uuid,
  symbol text not null,
  approve boolean not null,
  size_multiplier numeric(6, 4) not null,
  confidence numeric(6, 4) not null,
  rationale text not null,
  risk_flags jsonb not null default '[]'::jsonb,
  model text not null,
  latency_ms integer not null default 0,
  input_tokens integer not null default 0,
  output_tokens integer not null default 0,
  error text,
  request_id text,
  prompt text
);
create index if not exists llm_decisions_signal_idx on public.llm_decisions (signal_id);
create index if not exists llm_decisions_created_at_idx on public.llm_decisions (created_at desc);

-- Append-only order state history: a new row each time the worker observes an order.
create table if not exists public.orders (
  id uuid primary key,
  created_at timestamptz not null default now(),
  order_id text not null,
  reference_id text,
  signal_id uuid,
  purpose text not null,
  symbol text not null,
  side text not null,
  product text not null,
  order_type text not null,
  qty integer not null,
  price numeric(14, 2),
  trigger_price numeric(14, 2),
  status text not null,
  filled_qty integer not null default 0,
  avg_price numeric(14, 2),
  message text,
  broker text not null,
  mode text not null
);
create index if not exists orders_order_id_idx on public.orders (order_id, created_at desc);
create index if not exists orders_created_at_idx on public.orders (created_at desc);

create table if not exists public.trades (
  id uuid primary key,
  created_at timestamptz not null default now(),
  signal_id uuid,
  symbol text not null,
  side text not null,
  product text not null,
  qty integer not null,
  entry_price numeric(14, 2) not null,
  exit_price numeric(14, 2) not null,
  opened_at timestamptz not null,
  closed_at timestamptz not null,
  exit_reason text not null,
  gross_pnl numeric(14, 2) not null,
  costs numeric(14, 2) not null,
  net_pnl numeric(14, 2) not null,
  strategy text not null,
  mode text not null
);
create index if not exists trades_closed_at_idx on public.trades (closed_at desc);

create table if not exists public.control (
  key text primary key,
  value jsonb not null,
  updated_at timestamptz not null default now()
);
insert into public.control (key, value) values
  ('kill_switch', 'false'::jsonb),
  ('paused', 'false'::jsonb)
on conflict (key) do nothing;

create or replace view public.daily_pnl
with (security_invoker = true) as
select
  (closed_at at time zone 'Asia/Kolkata')::date as trade_date,
  mode,
  count(*) as trades,
  sum(net_pnl) as net_pnl,
  sum(costs) as costs,
  sum(case when net_pnl > 0 then 1 else 0 end) as winners
from public.trades
group by 1, 2;

alter table public.events enable row level security;
alter table public.signals enable row level security;
alter table public.llm_decisions enable row level security;
alter table public.orders enable row level security;
alter table public.trades enable row level security;
alter table public.control enable row level security;
