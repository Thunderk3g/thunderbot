-- Serverless worker support: a run lock, and room for the daily-strategy backtests.
-- Same security model as before: RLS on, no policies, service-role access only.

-- The Lab's daily-strategy backtests are queued as kind = 'invest'; the original check left them out.
alter table public.jobs drop constraint if exists jobs_kind_check;
alter table public.jobs add constraint jobs_kind_check check (kind in ('backtest', 'sweep', 'invest'));

-- One row per (kind, day) that a worker has claimed. Two schedulers can wake the worker at the same
-- moment (Supabase Cron and Vercel Cron, or a retry); the unique key lets exactly one of them act.
create table if not exists public.daily_runs (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  kind text not null,
  day date not null,
  status text not null default 'running' check (status in ('running', 'done', 'error')),
  detail jsonb not null default '{}'::jsonb,
  unique (kind, day)
);
create index if not exists daily_runs_created_at_idx on public.daily_runs (created_at desc);

alter table public.daily_runs enable row level security;
