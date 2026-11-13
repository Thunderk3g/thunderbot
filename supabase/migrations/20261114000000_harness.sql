-- The harness and its gates (docs/harness.md).
--
-- Every decision now carries the id of the harness it was made under, so two harnesses can be compared
-- on the same forward days, and every setup an LLM role was asked about carries what is needed to score
-- that role against doing nothing: the size it asked for, what the call cost, and what the setup went
-- on to make after charges and slippage.
--
-- All new columns are nullable; rows written before this migration simply have none of them and are
-- not scored. A worker newer than the database leaves these columns out and says so in its log, so the
-- order in which this migration and a deployment are applied does not matter.

alter table public.signals add column if not exists harness_id text;

alter table public.llm_decisions add column if not exists harness_id text;
alter table public.llm_decisions add column if not exists role text;        -- trader | signal_reviewer | rebalance_reviewer
alter table public.llm_decisions add column if not exists stage text;       -- shadow | active, when the role was asked
alter table public.llm_decisions add column if not exists cost_inr numeric; -- from the prices in the harness's policy.toml

alter table public.signal_outcomes add column if not exists harness_id text;
alter table public.signal_outcomes add column if not exists llm_role text;
alter table public.signal_outcomes add column if not exists llm_stage text;
alter table public.signal_outcomes add column if not exists llm_model text;      -- the model id the provider answered with
alter table public.signal_outcomes add column if not exists llm_w numeric;       -- share of normal size the role asked for, 0 to 1
alter table public.signal_outcomes add column if not exists llm_cost_inr numeric;
alter table public.signal_outcomes add column if not exists net_r numeric;       -- outcome in R after charges and slippage, at full size
alter table public.signal_outcomes add column if not exists risk_inr numeric;    -- rupees risked at full size

create index if not exists signal_outcomes_role_idx on public.signal_outcomes (llm_role, harness_id, created_at);

-- Scoring the roles on demand is a job like any other.
alter table public.jobs drop constraint if exists jobs_kind_check;
alter table public.jobs add constraint jobs_kind_check
  check (kind in ('backtest', 'sweep', 'invest', 'train', 'groww_check', 'gates'));
