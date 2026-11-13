-- Keys saved from the dashboard's setup screen: the LLM provider key and the Groww login credentials.
-- Same security model as every other table: RLS on, no policies, service-role access only.
--
-- The dashboard encrypts each secret before it is written (AES-256-GCM under TB_SECRET_KEY, or the
-- service-role key when that is unset) and the worker decrypts it when it starts a pass, so this
-- table holds ciphertext, a masked hint such as "sk-…a1b2", and non-secret metadata (provider,
-- model, key type). One install holds one person's keys.
create table if not exists public.secrets (
  name text primary key,
  ciphertext text not null,
  hint text not null default '',
  meta jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

alter table public.secrets enable row level security;

-- The setup screen's "Check" button queues a read-only Groww login check like any other job.
alter table public.jobs drop constraint if exists jobs_kind_check;
alter table public.jobs add constraint jobs_kind_check
  check (kind in ('backtest', 'sweep', 'invest', 'train', 'groww_check'));

-- Belt and braces: even if a policy is added by mistake later, the browser roles hold no privilege here.
revoke all on table public.secrets from anon, authenticated;
