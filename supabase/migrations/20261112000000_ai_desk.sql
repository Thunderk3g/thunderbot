-- The AI desk: a table for trained models, and a job kind for training them.
-- Same security model as before: RLS on, no policies, service-role access only.

-- Training runs are queued like backtests (the dashboard's Retrain button, or the desk itself after the close).
alter table public.jobs drop constraint if exists jobs_kind_check;
alter table public.jobs add constraint jobs_kind_check check (kind in ('backtest', 'sweep', 'invest', 'train'));

-- One row per trained model. The newest row for a name is the one in use; older rows are the history.
-- "model" is the whole model as JSON (a few tens of kilobytes); "report" is its out-of-sample report.
create table if not exists public.models (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz not null default now(),
  name text not null,
  report jsonb not null default '{}'::jsonb,
  model jsonb not null
);
create index if not exists models_name_created_idx on public.models (name, created_at desc);

alter table public.models enable row level security;
