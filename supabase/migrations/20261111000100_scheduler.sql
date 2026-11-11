-- Supabase as the scheduler: pg_cron wakes the worker function over HTTPS (pg_net) every five minutes
-- during NSE hours. Nothing else has to stay running.
--
-- Before the jobs do anything, store two secrets in Vault (SQL editor, once per project; never in git):
--
--   select vault.create_secret('https://YOUR-APP.vercel.app', 'thunderbot_worker_url', 'Base URL of the dashboard deployment');
--   select vault.create_secret('THE-SAME-VALUE-AS-CRON_SECRET-ON-VERCEL', 'thunderbot_cron_secret', 'Bearer token the worker function checks');
--
-- Optional, for a phone alert when the worker goes quiet during market hours (https://ntfy.sh, free):
--
--   select vault.create_secret('a-long-topic-name-nobody-can-guess', 'thunderbot_ntfy_topic', 'ntfy.sh topic for alerts');
--
-- Until the first two exist, thunderbot_wake() does nothing. To change one later:
--   select vault.update_secret((select id from vault.secrets where name = 'thunderbot_worker_url'), 'https://new-url');
--
-- Check that it works:  select public.thunderbot_wake('manual');
--                       select status_code, content, error_msg, created from net._http_response order by created desc limit 5;
--                       select j.jobname, d.status, d.return_message, d.start_time from cron.job_run_details d
--                         join cron.job j using (jobid) order by d.start_time desc limit 10;

create extension if not exists pg_cron with schema pg_catalog;
create extension if not exists pg_net with schema extensions;

-- Queue one GET to the worker function. pg_net sends it after this transaction commits and does not
-- wait for the answer, so the caller returns in milliseconds however long the function runs. The
-- timeout is the function's own limit: a request cut short might otherwise cancel a running backtest.
create or replace function public.thunderbot_wake(reason text default 'cron')
returns bigint
language plpgsql
security definer
set search_path = ''
as $$
declare
  worker_url text;
  secret text;
  request_id bigint;
begin
  select decrypted_secret into worker_url from vault.decrypted_secrets where name = 'thunderbot_worker_url';
  select decrypted_secret into secret from vault.decrypted_secrets where name = 'thunderbot_cron_secret';
  if worker_url is null or secret is null then
    raise notice 'thunderbot_wake: store the Vault secrets thunderbot_worker_url and thunderbot_cron_secret first';
    return null;
  end if;
  select net.http_get(
    url := rtrim(worker_url, '/') || '/api/worker',
    params := jsonb_build_object('op', 'tick', 'by', reason),
    headers := jsonb_build_object('Authorization', 'Bearer ' || secret),
    timeout_milliseconds := 290000
  ) into request_id;
  return request_id;
end;
$$;

-- An alert that does not depend on the worker: if the heartbeat is stale while the market is open,
-- the chain (pg_cron -> pg_net -> Vercel -> Supabase) is broken somewhere. Silent unless a topic is set.
create or replace function public.thunderbot_watchdog()
returns bigint
language plpgsql
security definer
set search_path = ''
as $$
declare
  topic text;
  last_seen timestamptz;
  wanted boolean;
begin
  select decrypted_secret into topic from vault.decrypted_secrets where name = 'thunderbot_ntfy_topic';
  if topic is null then
    return null;
  end if;
  select (value ->> 'wall_at')::timestamptz into last_seen from public.control where key = 'heartbeat';
  select value = 'true'::jsonb into wanted from public.control where key = 'trading_enabled';
  if not coalesce(wanted, false) or (last_seen is not null and last_seen > now() - interval '20 minutes') then
    return null;
  end if;
  return net.http_post(
    url := 'https://ntfy.sh',
    body := jsonb_build_object(
      'topic', topic,
      'title', 'Thunderbot is not running',
      'message', 'No heartbeat since ' || coalesce(to_char(last_seen at time zone 'Asia/Kolkata', 'DD Mon HH24:MI'), 'ever')
                 || ' IST. Today''s 15:10 check may be missed. Open the dashboard and press "Check now".',
      'priority', 4
    ),
    timeout_milliseconds := 10000
  );
end;
$$;

revoke all on function public.thunderbot_wake(text) from public, anon, authenticated;
revoke all on function public.thunderbot_watchdog() from public, anon, authenticated;

-- pg_cron runs in UTC. 09:15-15:30 IST is 03:45-10:00 UTC, which no single cron expression covers, so the
-- job fires every five minutes from 03:00 to 10:55 UTC on weekdays and sends only inside the window.
-- 15:35 keeps one tick after the close, for a paper run that could not happen in time.
select cron.schedule(
  'thunderbot-market-tick',
  '*/5 3-10 * * 1-5',
  $$
  select public.thunderbot_wake('market')
  where (now() at time zone 'Asia/Kolkata')::time between time '09:15' and time '15:35';
  $$
);

-- Evening catch-up: late paper runs, queued backtests, and a fresh heartbeat for the dashboard.
select cron.schedule('thunderbot-evening-tick', '30 11 * * 1-5', $$ select public.thunderbot_wake('evening'); $$);

-- Weekends: one call a day, so the project sees real API requests and the dashboard stays current.
select cron.schedule('thunderbot-weekend-tick', '30 6 * * 0,6', $$ select public.thunderbot_wake('weekend'); $$);

-- 15:05 and 15:20 IST on weekdays: is the worker alive in time for the 15:10 check?
select cron.schedule('thunderbot-watchdog', '35,50 9 * * 1-5', $$ select public.thunderbot_watchdog(); $$);

-- pg_cron never prunes its own history.
select cron.schedule(
  'thunderbot-prune-cron-history',
  '15 20 * * *',
  $$ delete from cron.job_run_details where end_time < now() - interval '7 days'; $$
);
