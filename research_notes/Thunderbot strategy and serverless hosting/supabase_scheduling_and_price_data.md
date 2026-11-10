# Supabase free-plan scheduling (pg_cron, pg_net, Vault, Edge Functions, pausing) and NSE end-of-day price sources (Yahoo and alternatives)

As-of date: 10 November 2026. Read this box before using anything below.

**How these notes were sourced, and what could not be done**

- The research session's network allowed only GitHub (`github.com`, `raw.githubusercontent.com`) and PyPI. `supabase.com`, `twelvedata.com`, `kite.trade` and `upstox.com` did not resolve, and every market-data host was refused by the session's egress proxy.
- Supabase documentation was therefore read from its official source files in the `supabase/supabase` GitHub repository, `master` branch, on 10 Nov 2026 (`apps/docs/content/...`). Those files are what supabase.com/docs is built from. SQL below is copied from those files. Each citation gives the public docs URL and the source file.
- Web search was available for one query only; the shared search budget for the turn then ran out. Reddit, Stack Overflow, Vercel community and provider pricing pages were not searched.
- **No live test of Yahoo, NSE, AMFI, mfapi.in, Stooq, Twelve Data or Upstox was possible.** `curl` from this machine to `query1/query2.finance.yahoo.com`, `fc.yahoo.com`, `nsearchives.nseindia.com`, `www.nseindia.com`, `www.niftyindices.com`, `www.amfiindia.com`, `api.mfapi.in`, `stooq.com`, `api.twelvedata.com` and `api.upstox.com` all failed with `CONNECT tunnel failed, response 403` from the session's own proxy (16:31-16:40 UTC, 10 Nov 2026). That is a sandbox policy denial. It says nothing about whether those services block cloud IPs.
- Items I could not source today are in the **Gaps** sections, marked "UNVERIFIED RECOLLECTION" where I give what I remember from before this session (knowledge to about mid-2026). Treat those as leads to check, not facts.

---

## A1. Is pg_cron (Supabase Cron) usable on the Free plan, and what are its schedule rules and limits?

### Takeaway
Supabase Cron is pg_cron inside the project's Postgres; the docs put no plan restriction on it, schedules run in GMT/UTC, the minimum is one second (`'N seconds'`) or one minute in cron syntax, and `*/5 3-10 * * 1-5` and `40 9 * * 1-5` are valid schedules for the Thunderbot windows. Supabase recommends at most 8 concurrent jobs of at most 10 minutes each, and `cron.job_run_details` must be purged by a job you schedule yourself.

### Cited Findings
- "Supabase Cron is a Postgres Module that simplifies scheduling recurring Jobs with cron syntax and monitoring Job runs inside Postgres." Jobs "can be created via SQL or the Integrations -> Cron interface inside the Dashboard, and can run anywhere from every second to once a year". — [Supabase docs: Cron](https://supabase.com/docs/guides/cron) ([source file](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/cron.mdx))
- "For best performance, we recommend no more than 8 Jobs run concurrently. Each Job should run no more than 10 minutes." — [Supabase docs: Cron](https://supabase.com/docs/guides/cron)
- "Under the hood, Supabase Cron uses the `pg_cron` Postgres database extension... all Jobs are stored on the `cron.job` table. Every Job's run and its status is recorded on the `cron.job_run_details` table." — [Supabase docs: Cron](https://supabase.com/docs/guides/cron)
- Every Job "can run SQL snippets or database functions with zero network latency or make an HTTP request, such as invoking a Supabase Edge Function". — [Supabase docs: Cron](https://supabase.com/docs/guides/cron)
- Install SQL, copied exactly: — [Supabase docs: Cron install](https://supabase.com/docs/guides/cron/install) ([source file](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/cron/install.mdx))
  ```sql
  create extension pg_cron with schema pg_catalog;

  grant usage on schema cron to postgres;
  grant all privileges on all tables in schema cron to postgres;
  ```
  Dashboard route: "Go to the Cron Postgres Module under Integrations in the Dashboard. Enable the `pg_cron` extension." Uninstall is `drop extension if exists pg_cron;` and "Disabling the `pg_cron` extension will permanently delete all Jobs."
- Cron syntax as documented by Supabase (5 fields: min 0-59, hour 0-23, day of month 1-31, month 1-12, day of week 0-6 where "0 to 6 are Sunday to Saturday, or use names; 7 is also Sunday"). "You can use [1-59] seconds (e.g. `30 seconds`) as the cron syntax to schedule sub-minute Jobs." "You can input seconds for your Job schedule interval as long as you're on Postgres version 15.1.1.61 or later." — [Supabase docs: Cron quickstart](https://supabase.com/docs/guides/cron/quickstart) ([source file](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/cron/quickstart.mdx))
- Schedule, edit, pause, delete and inspect, copied exactly from the quickstart: — [Supabase docs: Cron quickstart](https://supabase.com/docs/guides/cron/quickstart)
  ```sql
  -- Cron Job name cannot be edited
  select cron.schedule('permanent-cron-job-name', '30 seconds', 'CALL do_something()');
  ```
  ```sql
  select cron.alter_job(
    job_id := (select jobid from cron.job where jobname = 'permanent-cron-job-name'),
    schedule := '*/5 * * * *'
  );
  ```
  ```sql
  -- Activate Job
  select cron.alter_job(
    job_id := (select jobid from cron.job where jobname = 'permanent-cron-job-name'),
    active := true
  );

  -- Deactivate Job
  select cron.alter_job(
    job_id := (select jobid from cron.job where jobname = 'permanent-cron-job-name'),
    active := false
  );
  ```
  ```sql
  select cron.unschedule('permanent-cron-job-name');
  ```
  ```sql
  select
    *
  from cron.job_run_details
  where jobid = (select jobid from cron.job where jobname = 'permanent-cron-job-name')
  order by start_time desc
  limit 10;
  ```
- "Job names are case sensitive and cannot be edited once created. Attempting to create a second Job with the same name (and case) will overwrite the first Job." Also: "It is also possible to modify a job by using the `cron.schedule()` function by inputting the same job name. This will replace the existing job via upsert." — [Supabase docs: Cron quickstart](https://supabase.com/docs/guides/cron/quickstart)
- "Unscheduling a Job will permanently delete the Job from `cron.job` table but its run history remain in `cron.job_run_details` table." — [Supabase docs: Cron quickstart](https://supabase.com/docs/guides/cron/quickstart)
- "The records in the `cron.job_run_details` table are not cleaned up automatically. They are also not removed when jobs are unscheduled, which will take up disk space in your database." Official cleanup job, copied exactly: — [Supabase docs: Cron quickstart](https://supabase.com/docs/guides/cron/quickstart)
  ```sql
  select cron.schedule(
    'job-run-details-cleanup', -- name of the cron job
    '0 0 * * *', -- daily at midnight (GMT)
    $$ delete from cron.job_run_details where end_time < now() - interval '7 days' $$
  );
  ```
- Supabase's own examples label times as GMT, e.g. `'30 3 * * 6', -- Saturday at 3:30AM (GMT)`. — [Supabase docs: Cron quickstart](https://supabase.com/docs/guides/cron/quickstart)
- pg_cron upstream: `cron.timezone` defaults to `GMT` ("Timezone in which the pg_cron background worker should run"); "Previously pg_cron could only use GMT time, but now you can adapt your time by setting `cron.timezone` in postgresql.conf." `cron.max_running_jobs` defaults to `32`. `cron.log_run` defaults to `on` ("Log all run details in the `cron.job_run_details` table"). — [pg_cron README](https://github.com/citusdata/pg_cron/blob/main/README.md)
- pg_cron upstream syntax notes: `$` means last day of the month; "`[1-59] seconds` to schedule a job based on an interval. Note, you cannot use seconds with the other time units." Example given: `0 0 * * 1-5   # 12AM every weekday`. The parser "comes directly from the cron source code by Paul Vixie, hence the same options are supported." — [pg_cron README](https://github.com/citusdata/pg_cron/blob/main/README.md)
- "pg_cron can run multiple jobs in parallel, but only one instance of each specific job at a time. If a second instance is triggered before the first finishes, it's queued and starts as soon as the first one completes." — [pg_cron README](https://github.com/citusdata/pg_cron/blob/main/README.md)
- A web search summary of Supabase's pg_cron debugging guide reported that pg_cron "supports up to 32 concurrent jobs, each using a database connection" and that the 8-job figure is a recommendation, not an enforced cap. I could not open the guide itself. — [Supabase troubleshooting: pg_cron debugging guide](https://supabase.com/docs/guides/troubleshooting/pgcron-debugging-guide-n1KTaz) (search-result summary only)
- The same search surfaced a third-party tutorial saying pg_cron is available on all Supabase plans including the free tier. Not an official source. — [RapidDev tutorial](https://www.rapidevelopers.com/md/supabase-tutorial/how-to-schedule-cron-jobs-with-supabase) (search-result summary only)
- Free-plan compute is "Nano": shared CPU, "Up to 0.5 GB" memory, 60 max database connections, 200 pooler clients. — [Supabase docs: Compute and disk](https://supabase.com/docs/guides/platform/compute-and-disk) ([source file](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/compute-and-disk.mdx))

### Inferences
- No Cron, pg_cron, pricing or plan file I read restricts pg_cron to paid plans, and the shared pricing data (`packages/shared-data/pricing.ts`) has no Cron line item. Free-plan availability is therefore very likely, but the official docs never say "available on Free" in the files read.
- ADAPTED schedules for Thunderbot (not from the docs; built from the documented 5-field syntax and the GMT rule). 09:15-15:30 IST is 03:45-10:00 UTC; 15:10 IST is 09:40 UTC:
  - Simple, over-wide: `*/5 3-10 * * 1-5` fires every 5 minutes 03:00-10:55 UTC (08:30-16:25 IST) Monday-Friday. The worker must itself ignore ticks outside 09:15-15:30 IST.
  - Exact window with three jobs: `45-59/5 3 * * 1-5`, `*/5 4-9 * * 1-5`, `0 10 * * 1-5`.
  - Single daily decision run: `40 9 * * 1-5` (09:40 UTC = 15:10 IST).
  - pg_cron knows nothing about NSE holidays, so the worker needs its own holiday check.
- An HTTP job issued through pg_net returns in milliseconds because pg_net only queues the request (see A2). The "8 concurrent, 10 minutes" recommendation is therefore not a constraint for a job that just calls `net.http_post`.
- One tick every 5 minutes for 6.25 hours on about 250 trading days adds about 19,000 rows a year to `cron.job_run_details`. The official 7-day cleanup job keeps this negligible against the 500 MB limit.

### Gaps
- No official sentence stating "pg_cron is available on the Free plan" was found in the files read. Confirm by enabling it under Integrations -> Cron in a Free project.
- The pg_cron version on current Supabase Postgres images was not checked. The "N seconds" requirement is quoted as "Postgres version 15.1.1.61 or later" from the docs; the pg_cron 1.5 link in the task brief is not confirmed here.
- I could not open Supabase's pg_cron debugging guide (the file path in the repo was not found), so the "32 concurrent jobs" wording comes from a search summary plus the upstream default.

---

## A2. Can pg_net call an external URL from pg_cron and from an insert trigger, and how does it behave?

### Takeaway
Yes to both: pg_net queues an HTTP request that a background worker sends after the transaction commits, and Database Webhooks are an official wrapper over the same mechanism. It is fire-and-forget: no automatic retries, an unlogged queue, a short default timeout that the Supabase docs give as 2,000 ms and upstream gives as 5,000 ms, and responses kept 6 hours. Design the worker call to return quickly and record status in Postgres.

### Cited Findings
- "pg_net enables Postgres to make asynchronous HTTP/HTTPS requests in SQL... it is asynchronous by default. This makes it useful in blocking functions (like triggers)." "The pg_net API is in beta. Functions signatures may change." — [Supabase docs: pg_net](https://supabase.com/docs/guides/database/extensions/pg_net) ([source file](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/extensions/pg_net.mdx))
- Enable SQL, copied exactly: — [Supabase docs: pg_net](https://supabase.com/docs/guides/database/extensions/pg_net)
  ```sql
  -- Example: enable the "pg_net" extension.
  create extension pg_net with schema "extensions";
  -- Note: The extension creates its own schema/namespace named "net" to avoid naming conflicts. Registering it in the extensions schema avoids exposing it in public and satisfies the Security Advisor check.

  -- Example: disable the "pg_net" extension
  drop extension if exists pg_net;
  drop schema net;
  ```
- `net.http_post` signature as shown in the Supabase docs, copied exactly. "HTTP requests are not started until the transaction is committed." — [Supabase docs: pg_net](https://supabase.com/docs/guides/database/extensions/pg_net)
  ```sql
  net.http_post(
      -- url for the request
      url text,
      -- body of the POST request
      body jsonb default '{}'::jsonb,
      -- key/value pairs to be url encoded and appended to the `url`
      params jsonb default '{}'::jsonb,
      -- key/values to be included in request headers
      headers jsonb default '{"Content-Type": "application/json"}'::jsonb,
      -- the maximum number of milliseconds the request may take before being canceled
      timeout_milliseconds int default 2000
  )
      -- request_id reference
      returns bigint

      volatile
      parallel safe
      language plpgsql
  ```
  `net.http_get` and `net.http_delete` have the same `timeout_milliseconds int default 2000` in the Supabase docs.
- CONFLICT on the default timeout: the upstream pg_net README on `master` shows `timeout_milliseconds int default 5000` for GET, POST and DELETE, and documents a setting "pg_net.max_timeout_ms (default: 600000): An integer that bounds the `timeout_milliseconds` of a request. A request with a timeout outside `1..pg_net.max_timeout_ms` is not sent and gets an `ERROR` response saying so". — [pg_net README](https://github.com/supabase/pg_net/blob/master/README.md); Supabase docs say 2000 ms — [Supabase docs: pg_net](https://supabase.com/docs/guides/database/extensions/pg_net)
- Official cron + HTTP example with an explicit timeout, copied exactly: — [Supabase docs: Cron quickstart](https://supabase.com/docs/guides/cron/quickstart)
  ```sql
  select
    cron.schedule(
      'invoke-function-every-half-minute',
      '30 seconds',
      $$
      select
        net.http_post(
            url:='https://project-ref.supabase.co/functions/v1/function-name',
            headers:=jsonb_build_object('Content-Type','application/json', 'apikey', 'YOUR_PUBLISHABLE_KEY'),
            body:=jsonb_build_object('time', now() ),
            timeout_milliseconds:=5000
        ) as request_id;
      $$
    );
  ```
  "This requires the `pg_net` extension to be enabled."
- Official "call an endpoint every minute" example from the pg_net page, copied exactly: — [Supabase docs: pg_net](https://supabase.com/docs/guides/database/extensions/pg_net)
  ```sql
  select cron.schedule(
  	'cron-job-name',
  	'* * * * *', -- Executes every minute (cron syntax)
  	$$
  	    -- SQL query
  	    select "net"."http_post"(
              -- URL of Edge function
              url:='https://project-ref.supabase.co/functions/v1/function-name',
              headers:='{"apikey": "<SUPABASE_PUBLISHABLE_KEY>"}'::jsonb,
              body:='{"name": "pg_net"}'::jsonb
  	    ) as "request_id";
  	$$
  );
  ```
- Official trigger example ("Make a call to an external endpoint when a trigger event occurs"), copied exactly. Note it is `after update`; the docs have no `after insert` version on this page: — [Supabase docs: pg_net](https://supabase.com/docs/guides/database/extensions/pg_net)
  ```sql
  -- function called by trigger
  create or replace function <function_name>()
      returns trigger
      language plpgSQL
  as $$
  begin
      -- calls pg_net function net.http_post
      -- sends request to postman API
      perform "net"."http_post"(
        'https://postman-echo.com/post'::text,
        jsonb_build_object(
          'old_row', to_jsonb(old.*),
          'new_row', to_jsonb(new.*)
        ),
        headers:='{"Content-Type": "application/json"}'::jsonb
      ) as request_id;
      return new;
  END $$;

  -- trigger for table update
  create trigger <trigger_name>
      after update on <table_name>
      for each row
      execute function <function_name>();
  ```
- Database Webhooks: "Database Webhooks are a convenience wrapper around triggers using the pg_net extension. This extension is asynchronous, and therefore will not block your database changes for long-running network requests." "You can hook into three table events: `INSERT`, `UPDATE`, and `DELETE`. All events are fired _after_ a database row is changed." "We currently support HTTP webhooks. These can be sent as `POST` or `GET` requests with a JSON payload." — [Supabase docs: Database Webhooks](https://supabase.com/docs/guides/database/webhooks) ([source file](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/webhooks.mdx))
- Official webhook-as-SQL definition, copied exactly: — [Supabase docs: Database Webhooks](https://supabase.com/docs/guides/database/webhooks)
  ```sql
  create trigger "my_webhook" after insert
  on "public"."my_table" for each row
  execute function "supabase_functions"."http_request"(
    'http://host.docker.internal:3000',
    'POST',
    '{"Content-Type":"application/json"}',
    '{}',
    '1000'
  );
  ```
- Official `after insert` trigger that reads its URL and key from Vault and calls `net.http_post`, copied exactly (this is the closest official template for "run a backtest when a row is inserted"): — [Supabase docs: Database Webhooks, "From a migration"](https://supabase.com/docs/guides/database/webhooks)
  ```sql
  create function public.call_function_name()
  returns trigger
  language plpgsql
  security definer
  set search_path = ''
  as $$
  begin
    perform net.http_post(
      url := (select decrypted_secret from vault.decrypted_secrets where name = 'project_url') || '/functions/v1/function-name',
      headers := jsonb_build_object(
        'Content-Type', 'application/json',
        'apikey', (select decrypted_secret from vault.decrypted_secrets where name = 'secret_key')
      ),
      body := jsonb_build_object(
        'type', tg_op,
        'table', tg_table_name,
        'schema', tg_table_schema,
        'record', to_jsonb(new),
        'old_record', null
      )
    );
    return new;
  end;
  $$;

  create trigger call_function_name
  after insert on public.my_table
  for each row execute function public.call_function_name();
  ```
  "The trigger function is `security definer` because the roles that insert rows, such as `authenticated`, can't read Vault. Without it, their inserts fail with a permission error."
- A dashboard-created webhook "saves the key in its trigger definition, so the key appears anywhere the trigger's SQL does, such as a database dump." — [Supabase docs: Database Webhooks](https://supabase.com/docs/guides/database/webhooks)
- Webhook payload for an insert is `{ type: 'INSERT', table, schema, record, old_record: null }`. "Logging history of webhook calls is available under the `net` schema of your database." — [Supabase docs: Database Webhooks](https://supabase.com/docs/guides/database/webhooks)
- Queue and response storage: "Waiting requests are stored in the `net.http_request_queue` table. Upon execution, they are deleted." "Once a response is returned, by default, it is stored for 6 hours in the `net._http_response` table." That table has columns `id, status_code, content_type, headers, content, timed_out, error_msg, created`. — [Supabase docs: pg_net](https://supabase.com/docs/guides/database/extensions/pg_net)
- Official query for failures, copied exactly: — [Supabase docs: pg_net](https://supabase.com/docs/guides/database/extensions/pg_net)
  ```sql
  select
    *
  from net._http_response
  where "status_code" >= 400 or "error_msg" is not null
  order by "created" desc;
  ```
- Limitations listed by Supabase: requests and responses live in unlogged tables "which are not preserved during a crash or unclean shutdown"; "By default, response data is saved for only 6 hours"; "Can only make POST requests with JSON data. No other data formats are supported"; "Intended to handle at most 200 requests per second. Increasing the rate can introduce instability"; "Does not have support for PATCH/PUT requests"; "Can only work with one database at a time. It defaults to the `postgres` database." — [Supabase docs: pg_net](https://supabase.com/docs/guides/database/extensions/pg_net)
- Upstream confirms three request types only: async GET, async POST "with a *JSON* payload", async DELETE. Settings: `pg_net.batch_size` default 200, `pg_net.ttl` default 6 hours. — [pg_net README](https://github.com/supabase/pg_net/blob/master/README.md)
- No built-in retry: the upstream README has a "Retrying failed requests" section that says `net._http_response` "doesn't store all the necessary information to retry failed requests" and tells you to build your own request-tracking table and wrapper function. — [pg_net README](https://github.com/supabase/pg_net/blob/master/README.md)
- Changing pg_net settings on Supabase "requires superuser privileges. Contact Support to have the required permission granted", and needs pg_net v0.12.0 or later. — [Supabase docs: pg_net](https://supabase.com/docs/guides/database/extensions/pg_net)
- Secret exposure while queued: "Any role that can log in to your database can read the secret key while the request waits. `pg_net` writes the decrypted key to `net.http_request_queue` until it sends the request." — [Supabase docs: Scheduling Edge Functions](https://supabase.com/docs/guides/functions/schedule-functions) ([partial source](https://github.com/supabase/supabase/blob/master/apps/docs/content/_partials/pg_net_queued_key.mdx))
- Local development only: `localhost` in a webhook URL "will refer to the container itself, not your host machine"; use `host.docker.internal`. — [Supabase docs: Database Webhooks](https://supabase.com/docs/guides/database/webhooks)
- Thunderbot already has a suitable target table: `public.jobs` (`kind` in `backtest`/`sweep`, `status` in `queued`/`running`/`done`/`error`, `progress`, `result`, `error`, `started_at`, `finished_at`), with "RLS on, no policies, service-role access only". — local file `/home/user/thunderbot/supabase/migrations/20261016120000_platform.sql`

### Inferences
- Because the two official sources disagree on the default timeout (2,000 ms vs 5,000 ms), always pass `timeout_milliseconds` explicitly, as the official cron example does.
- The fifth argument `'1000'` in the official `supabase_functions.http_request` example is the timeout in milliseconds. The docs page does not label the arguments; this reading comes from the order (URL, method, headers, params, timeout).
- If the called endpoint takes 60-120 s and the pg_net timeout is 5 s, pg_net records a row with `timed_out` true (or an `error_msg`) and does not retry. Whether the function behind the URL keeps running after the caller disconnects depends on the host (Vercel), not on Supabase. The safe design is: the endpoint authenticates, writes or claims a status row, returns HTTP 202 inside a second or two, and does the long work in the platform's background facility; or else set `timeout_milliseconds` above the worst-case run time (upstream allows up to 600,000 ms by default).
- pg_net has no retries and its queue is unlogged, so a missed trigger call must be recoverable. With Thunderbot's `jobs.status = 'queued'` column, the periodic cron tick can double as a sweeper: every tick, the worker also picks up any job still `queued`. Then the insert trigger is only a latency optimisation.
- ADAPTED SQL for Thunderbot (not from the docs; assembled from the official examples above; names `worker_url`, `cron_secret`, `thunderbot-tick` and the `/api/...` paths are placeholders):
  ```sql
  -- ADAPTED. Run once in the SQL editor, outside migrations.
  select vault.create_secret('https://<your-app>.vercel.app/api/tick', 'worker_url', 'Thunderbot worker tick endpoint');
  select vault.create_secret('https://<your-app>.vercel.app/api/jobs/run', 'jobs_url', 'Thunderbot on-demand job endpoint');
  select vault.create_secret('<long random string>', 'cron_secret', 'Bearer secret the worker checks');

  -- ADAPTED. Every 5 minutes, 03:00-10:55 UTC, Monday-Friday. The worker ignores ticks outside 09:15-15:30 IST and on NSE holidays.
  select cron.schedule(
    'thunderbot-tick',
    '*/5 3-10 * * 1-5',
    $$
    select net.http_post(
        url := (select decrypted_secret from vault.decrypted_secrets where name = 'worker_url'),
        headers := jsonb_build_object(
          'Content-Type', 'application/json',
          'Authorization', 'Bearer ' || (select decrypted_secret from vault.decrypted_secrets where name = 'cron_secret')
        ),
        body := jsonb_build_object('source', 'pg_cron', 'time', now()),
        timeout_milliseconds := 5000
    ) as request_id;
    $$
  );

  -- ADAPTED. Fire the worker when the dashboard inserts a research job.
  create function public.notify_job_inserted()
  returns trigger
  language plpgsql
  security definer
  set search_path = ''
  as $$
  begin
    perform net.http_post(
      url := (select decrypted_secret from vault.decrypted_secrets where name = 'jobs_url'),
      headers := jsonb_build_object(
        'Content-Type', 'application/json',
        'Authorization', 'Bearer ' || (select decrypted_secret from vault.decrypted_secrets where name = 'cron_secret')
      ),
      body := jsonb_build_object('type', tg_op, 'table', tg_table_name, 'job_id', new.id, 'kind', new.kind),
      timeout_milliseconds := 5000
    );
    return new;
  end;
  $$;

  create trigger jobs_notify_worker
  after insert on public.jobs
  for each row execute function public.notify_job_inserted();

  -- To remove: select cron.unschedule('thunderbot-tick');
  ```
- The cron job text stored in `cron.job` holds only the Vault lookup, not the secret. The decrypted value still appears briefly in `net.http_request_queue`, as the docs warn.

### Gaps
- Vercel behaviour when the HTTP client (pg_net) times out and disconnects was not verified today (Vercel docs not reachable). UNVERIFIED RECOLLECTION: Vercel functions normally run to completion or to `maxDuration` after a client disconnect unless request cancellation is opted into; check Vercel's current docs and test it.
- Which pg_net version, default timeout and `max_timeout_ms` a new Supabase project runs in November 2026 was not checked. Run `select name, setting from pg_settings where name like 'pg_net%';` and `select extversion from pg_extension where extname = 'pg_net';` in the project.
- I found no official statement that pg_net "cannot call localhost" on the hosted platform; the only localhost note is about local Docker development.
- Supabase's "Webhook debugging guide" (`/kb/troubleshooting/webhook-debugging-guide-M8sk47`) could not be opened.

---

## A3. How do you store the call's secret in Supabase Vault, and is Vault on Free?

### Takeaway
`vault.create_secret(value, name, description)` stores an encrypted secret and `vault.decrypted_secrets` returns it at query time; the official "Scheduling Edge Functions" example uses exactly this for the project URL and secret key. The docs show no plan restriction on Vault. Legacy `anon`/`service_role` keys are being deprecated "by the end of 2026" in favour of `sb_publishable_...` / `sb_secret_...`.

### Cited Findings
- Create and read secrets, copied exactly: — [Supabase docs: Vault](https://supabase.com/docs/guides/database/vault) ([source file](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/vault.mdx))
  ```sql
  select vault.create_secret('my_s3kre3t');
  ```
  ```sql
  select vault.create_secret('another_s3kre3t', 'unique_name', 'This is the description');
  ```
  ```sql
  select * 
  from vault.decrypted_secrets 
  order by created_at desc 
  limit 3;
  ```
  "The function returns the UUID of the new secret." "Secrets can also have an optional _unique_ name and an optional description."
- Update and delete, copied exactly: — [Supabase docs: Vault](https://supabase.com/docs/guides/database/vault)
  ```sql
  select
    vault.update_secret(
      '7095d222-efe5-4cd5-b5c6-5755b451e223',
      'n3w_upd@ted_s3kret',
      'updated_unique_name',
      'This is the updated description'
    );
  ```
  ```sql
  delete from vault.secrets
  where id = '7095d222-efe5-4cd5-b5c6-5755b451e223'
  returning id, name;
  ```
- Official "Scheduling Edge Functions" example, copied exactly: — [Supabase docs: Scheduling Edge Functions](https://supabase.com/docs/guides/functions/schedule-functions) ([source file](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/schedule-functions.mdx))
  ```sql
  select vault.create_secret('https://project-ref.supabase.co', 'project_url');
  select vault.create_secret('YOUR_SUPABASE_SECRET_KEY', 'secret_key');
  ```
  ```sql
  select
    cron.schedule(
      'invoke-function-every-minute',
      '* * * * *', -- every minute
      $$
      select
        net.http_post(
            url:= (select decrypted_secret from vault.decrypted_secrets where name = 'project_url') || '/functions/v1/function-name',
            headers:=jsonb_build_object(
              'Content-type', 'application/json',
              'apikey', (select decrypted_secret from vault.decrypted_secrets where name = 'secret_key')
            ),
            body:=concat('{"time": "', now(), '"}')::jsonb
        ) as request_id;
      $$
    );
  ```
  The page now says: "Call the function with your secret key. Don't use your publishable key, because it's public and anyone who has it can call a function that accepts it." and "To access the auth token securely for your Edge Function call, we recommend storing them in Supabase Vault."
- How Vault protects data: secrets are "stored using Authenticated Encryption on disk" and "available in decrypted form through a Postgres view"; "Views are not stored on disk, they are only run at query time, so the secret remains encrypted on disk, and in any backup dumps or replication streams." "The encryption key is never stored in the database alongside the encrypted data." "Supabase creates and manages a unique encryption key for each project in our secured backend systems." — [Supabase docs: Vault](https://supabase.com/docs/guides/database/vault)
- "You should ensure that you protect access to this view with the appropriate SQL privilege settings at all times, as anyone that has access to the view has access to decrypted secrets." — [Supabase docs: Vault](https://supabase.com/docs/guides/database/vault)
- Pausing does not break Vault: "Same-project operations - pausing and restoring, and Point-in-Time or in-place restores - keep the same key, so your secrets stay readable automatically." A manual `pg_dump`/`pg_restore` into a new project "cannot decrypt secrets copied from the old project" until the root key is copied. — [Supabase docs: Vault](https://supabase.com/docs/guides/database/vault)
- API keys: "Supabase is deprecating the `anon` and `service_role` keys by the end of 2026. Use the publishable (`sb_publishable_xxx`) and secret (`sb_secret_xxx`) keys instead." — [Supabase docs: API keys](https://supabase.com/docs/guides/getting-started/api-keys) ([partial source](https://github.com/supabase/supabase/blob/master/apps/docs/content/_partials/api_keys_deprecation.mdx))
- "Publishable and secret keys are short strings, not JWTs. If a tool, tutorial, or AI assistant tells you to copy a long key that begins with `eyJ`, it was written for the legacy keys." "Creating publishable and secret keys doesn't revoke your legacy keys. Both key systems work at the same time." Secret keys "provide full access to your project's data, bypassing Row Level Security." — [Supabase docs: API keys](https://supabase.com/docs/guides/getting-started/api-keys)
- Deprecation timeline from the announcement (as summarised by the fetch tool, not quoted verbatim): June 2025 early preview; July 2025 full launch; November 2025 monthly reminders begin, "Projects restored from 1 November 2025 will no longer be restored with legacy keys", and new projects no longer get `anon`/`service_role`; "Late 2026 (TBC)" legacy keys deleted. — [Supabase GitHub discussion #29260](https://github.com/orgs/supabase/discussions/29260)
- Thunderbot already supports the new keys: commit `ba5dce1` "Support new Supabase sb_secret keys in dashboard and worker". — local repo `/home/user/thunderbot` (`git log`)

### Inferences
- Neither the Vault page nor the pricing data mentions a plan restriction, so Vault is very likely available on Free; the docs do not state it in so many words.
- For a call to a Vercel endpoint (not an Edge Function), the Supabase secret key is not needed in the request at all. Store only a random shared secret in Vault and have the worker check it, as in the adapted SQL in A2. That limits the damage if the header leaks through `net.http_request_queue`.
- A Free project that gets paused and then restored comes back without legacy keys (per the announcement's November 2025 rule). Thunderbot's `sb_secret` support means this should not break it, provided the deployed env vars use the new keys.

### Gaps
- The docs give "by the end of 2026" and the announcement says "Late 2026 (TBC)" for legacy-key removal. I found no exact removal date as of 10 Nov 2026, and the announcement text was read through a summarising tool.
- No explicit "Vault is available on the Free plan" statement was found.

---

## A4. Does a Free project still get paused after 7 days, what counts as activity, and what are the Free quotas?

### Takeaway
Yes: as of November 2026 the docs say Free projects with too little "user database activity" over a week are paused, "a few user requests to the database each day" is typically enough, and only a paid plan guarantees no pausing. Supabase has not published whether pg_cron activity counts, and community reports conflict (one user received a pause warning in November 2026 despite 87 successful keep-alive API calls), so do not rely on pg_cron or a trivial ping to keep a Free project alive.

### Cited Findings
- "Supabase pauses Free Plan projects that show low activity over a 7-day period to save server resources." — [Supabase docs: Project Pausing](https://supabase.com/docs/guides/platform/free-project-pausing) ([source file](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/free-project-pausing.mdx))
- "A Free plan project is considered inactive if it does not receive sufficient user database activity over the past week. Projects with too few user queries during that window are the clearest candidates for pausing. While you may be actively using the project, it's possible that usage is not enough to exclude it from automatic pausing. Typically a few user requests to the database each day over the previous week is enough to keep the project from being paused." — [Supabase docs: Project Pausing](https://supabase.com/docs/guides/platform/free-project-pausing)
- Emails: "A warning email roughly one week before the pause takes effect" and "A confirmation email once the project has been paused." After the warning, the pause can be prevented by visiting the project in the Dashboard "to generate activity" or by "making API calls to your project or sending requests via your connected application." — [Supabase docs: Project Pausing](https://supabase.com/docs/guides/platform/free-project-pausing)
- Restore window is now one year, not 90 days: "You can restore a paused project for up to 1 year after it was paused". "Once the project is paused, there is a 1-year window to restore the project on the platform from within Supabase Studio." The section's anchor is still `#90-day-window-to-restore`, which indicates the earlier limit was 90 days. — [Supabase docs: Project Pausing](https://supabase.com/docs/guides/platform/free-project-pausing)
- "Projects under a paid plan cannot be paused and are not subject to automatic pausing for inactivity." "To prevent future automatic pausing, upgrade to the Pro Plan". — [Supabase docs: Project Pausing](https://supabase.com/docs/guides/platform/free-project-pausing)
- Production checklist: "We may pause applications on the Free Plan that exhibit low activity in a 7-day period to save on server resources." "Database backups are not available for download for Free Plan projects." — [Supabase docs: Production checklist](https://supabase.com/docs/guides/deployment/going-into-prod) ([source file](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/deployment/going-into-prod.mdx))
- Pricing data: Free plan footer "Free projects are paused after 1 week of inactivity. Limit of 2 active projects."; pausing row: Free "After 1 week of inactivity", Pro/Team/Enterprise "Never". — [Supabase pricing data, plans.ts](https://github.com/supabase/supabase/blob/master/packages/shared-data/plans.ts) and [pricing.ts](https://github.com/supabase/supabase/blob/master/packages/shared-data/pricing.ts) (the data behind [supabase.com/pricing](https://supabase.com/pricing))
- "You are granted two free projects. The project limit applies across all organizations where you are an Owner or Administrator... Paused projects do not count towards your free project limit." — [Supabase docs: Billing](https://supabase.com/docs/guides/platform/billing-on-supabase) ([source file](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/billing-on-supabase.mdx))
- Free quotas (per organisation unless stated): Egress 5 GB; Database size 500 MB per project; 50,000 monthly active users; Storage 1 GB; Edge Function invocations 500,000; Realtime messages 2 million; Realtime peak connections 200. Pro: 250 GB egress, 8 GB disk per project, 100,000 MAU, 100 GB storage, 2 million invocations. — [Supabase docs: Billing](https://supabase.com/docs/guides/platform/billing-on-supabase)
- Egress quota "Free: 5 GB / 5 GB" (uncached / cached). — [Supabase docs: Manage egress usage](https://supabase.com/docs/guides/platform/manage-your-usage/egress) ([source file](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/manage-your-usage/egress.mdx))
- Free plan features: "Unlimited API requests", "50,000 monthly active users", "500 MB database size", "Shared CPU • 500 MB RAM", "5 GB egress", "5 GB cached egress", "1 GB file storage", "Community support". Pro is `priceMonthly: 25` ("From" $25/month, "Includes one project running on Micro compute"), with "Daily backups stored for 7 days" and "7-day log retention". — [Supabase pricing data, plans.ts](https://github.com/supabase/supabase/blob/master/packages/shared-data/plans.ts)
- Backups: Automatic backups Free `false`, Pro "7 days"; Point-in-time recovery Free `false`, Pro "$100 per month per 7 days retention". — [Supabase pricing data, pricing.ts](https://github.com/supabase/supabase/blob/master/packages/shared-data/pricing.ts)
- "We recommend that free tier plan projects regularly export their data using the Supabase CLI `db dump` command and maintain off-site backups." — [Supabase docs: Backups](https://supabase.com/docs/guides/platform/backups) ([source file](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/backups.mdx))
- Connections: direct connection `db.[PROJECT-REF].supabase.co:5432` is IPv6 on Free and Pro, IPv4 only with the IPv4 add-on; shared pooler (Supavisor) session mode `:5432` and transaction mode `:6543` are IPv4 on every plan. "The shared pooler is IPv4-only on every plan." The IPv4 add-on "is available on the Pro Plan and above." — [Supabase docs: Connecting to Postgres](https://supabase.com/docs/guides/database/connecting-to-postgres) ([source file](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/database/connecting-to-postgres.mdx))
- Community, November 2026: a Free-plan user reported a pause warning email on 5 Nov 2026 although a GitHub Actions workflow had made 87 keep-alive calls (2-4 a day, 9 Oct to 5 Nov 2026), each `POST /rest/v1/rpc/keepalive` returning HTTP 200. The RPC returned a constant and touched no table. Six replies, none identified as Supabase staff; the thread is unanswered. — [Supabase GitHub discussion #53090](https://github.com/orgs/supabase/discussions/53090) (read via a summarising tool)
- Community, October 2026: accepted (non-staff, as far as the page shows) answer restates the docs: activity means "user database activity over the past week", API reads and writes count because they reach the database, a few requests a day is typically enough but "not a guarantee", email is the only warning signal, restore deadline one year. It does not mention pg_cron. — [Supabase GitHub discussion #51126](https://github.com/orgs/supabase/discussions/51126) (read via a summarising tool)
- Community, 2023-2026: a user's project was paused despite a daily external job that only connected to the database; a GitHub "Collaborator" (GaryAustin1) said "I would think an external API request is the for sure way as it would tick both boxes" and that internal activity alone is not the test because "there are all kinds of Postgres things running in the background". The original poster later reported that a daily INSERT/UPDATE/DELETE transaction had kept the project active since March 2024 and that "just establishing a connection is not sufficient." No Supabase staff answer. — [Supabase GitHub discussion #13121](https://github.com/orgs/supabase/discussions/13121) (read via a summarising tool)
- Community keep-alive pattern: a popular repo describes "Creating a cron job (scheduled task) that makes a simple database call" from outside (Vercel cron) to stop pausing. — [travisvn/supabase-pause-prevention README](https://github.com/travisvn/supabase-pause-prevention)
- Other 2026 threads show pause/restore problems on Free: restore failing and reverting to INACTIVE (#51807, Oct 2026), project stuck "Restoring" (#50003, Sep 2026), "Table data lost after project restore from paused state (Free Tier)" (#39271, Oct 2025). Titles only; bodies not read. — [Supabase GitHub discussions search "paused inactivity"](https://github.com/orgs/supabase/discussions?discussions_q=paused+inactivity)

### Inferences
- The official wording changed from "inactivity" to "sufficient user database activity" and "user queries". That wording, plus the collaborator's remark about background Postgres activity, suggests internal jobs such as pg_cron may not count, but nothing official says so either way. Treat "pg_cron keeps the project awake" as unproven.
- The conflicting evidence is consistent with one reading: requests that reach the database and touch real tables through the API count; bare connections and constant-returning calls may not. This is a hypothesis from three user reports, not a rule.
- Thunderbot's design helps here: every worker tick makes real reads and writes to Supabase tables from outside (Vercel), on about 250 trading days a year. Weekends and holiday runs are the weak spot, so add a daily tick (including weekends) in which the worker reads and writes a real row. Even then, Free gives no guarantee.
- If the project is paused, pg_cron stops with it, so the scheduler fails silently at exactly the moment nothing is watching. A trading bot on Free needs an external dead-man check (for example, the dashboard or a second scheduler alerting when the last heartbeat row is older than a day) and the owner must watch for the warning email.
- For a bot that places real orders, Pro at $25/month removes pausing and adds daily backups; that is the only officially guaranteed route.
- Storage is not a constraint: daily bars for 10 symbols over 20 years are about 50,000 rows.

### Gaps
- No official statement on whether pg_cron jobs, pooler connections, or Dashboard visits count as activity, or on any numeric threshold. Discussion #53090 (Nov 2026) asks exactly this and had no staff reply when read.
- Reddit and other forums were not searched (search budget exhausted), so the wider body of "keep-alive via GitHub Actions/pg_cron" reports is not represented.
- The exact date the restore window changed from 90 days to 1 year was not found.
- Community threads were read through a summarising tool; staff status of repliers is as shown on the page and may be incomplete.

---

## A5. What are the Edge Functions limits on Free vs Pro, can they run Python or run in Mumbai, and are Queues useful?

### Takeaway
Edge Functions are TypeScript on a Deno-compatible runtime (no Python), with 256 MB memory, 2 s CPU time per request, a 150 s request idle timeout, and a worker wall-clock limit of 150 s on Free and 400 s on paid plans; Free includes 500,000 invocations a month and Mumbai (`ap-south-1`) is a supported execution region. They could act as a dispatcher or do light TypeScript work, but the Python strategy cannot run there. Supabase Queues (pgmq) exist and are pull-based.

### Cited Findings
- Runtime limits, quoted: "Maximum Memory: 256MB"; "Maximum Duration (Wall clock limit): This is the duration an Edge Function worker will stay active. During this period, a worker can serve multiple requests or process background tasks. Free plan: 150s. Paid plans: 400s"; "Maximum CPU Time: 2s (Amount of actual time spent on the CPU per request - does not include async I/O.)"; "Request idle timeout: 150s (If an Edge Function doesn't send a response before the timeout, 504 Gateway Timeout will be returned)". — [Supabase docs: Edge Functions limits](https://supabase.com/docs/guides/functions/limits) ([source file](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/limits.mdx))
- Platform limits: "Maximum Function Size: 20MB (bundled locally via the CLI) or 5MB (bundled server-side, e.g. via the Management API or Dashboard)"; functions per project Free 100, Pro 1000, Team 2000; "Outgoing connections to ports `25` and `587` are not allowed"; "Web Worker API (or Node `vm` API) are not available"; up to 100 secrets per project. — [Supabase docs: Edge Functions limits](https://supabase.com/docs/guides/functions/limits)
- Invocations: Free 500,000; Pro and Team 2 million then $2 per million. "You are charged for the number of times your functions get invoked, regardless of the response status code. Preflight (OPTIONS) requests are not billed." — [Supabase docs: Edge Function invocations usage](https://supabase.com/docs/guides/platform/manage-your-usage/edge-function-invocations) ([pricing partial](https://github.com/supabase/supabase/blob/master/apps/docs/content/_partials/billing/pricing/pricing_edge_functions.mdx))
- Language: "Edge Functions are server-side TypeScript functions, distributed globally at the edge", "developed using Deno", "TypeScript first and supports WASM". "Runtime: Supabase Edge Runtime (Deno compatible runtime with TypeScript first). Functions are `.ts` files that export a handler." — [Supabase docs: Edge Functions](https://supabase.com/docs/guides/functions) ([source file](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions.mdx))
- Background tasks: "You can use `EdgeRuntime.waitUntil(promise)` to explicitly mark background tasks. The Function instance continues to run until the promise provided to `waitUntil` completes." "You can respond to the request immediately and leave the task running in the background." A `beforeunload` event warns before shutdown. — [Supabase docs: Background tasks](https://supabase.com/docs/guides/functions/background-tasks) ([source file](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/background-tasks.mdx))
- Regions: "Edge Functions automatically execute in the region closest to the user making the request." Supported regions include `ap-south-1` (Mumbai) and `ap-southeast-1` (Singapore). "You can specify the region programmatically using the Supabase Client library, or using the `x-region` HTTP header"; where a header cannot be added, "you can use `forceFunctionRegion` query parameter." The response header `x-sb-edge-region` shows where it ran. "When you explicitly specify a region via the `x-region` header, requests will NOT be automatically re-routed to another region." — [Supabase docs: Regional invocations](https://supabase.com/docs/guides/functions/regional-invocation) ([source file](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/functions/regional-invocation.mdx))
- Calling a function from pg_cron or a webhook: "The function receives the secret key on the `apikey` header. To accept it, disable `verify_jwt` and use `auth: 'secret'`." — [Supabase docs: Scheduling Edge Functions](https://supabase.com/docs/guides/functions/schedule-functions)
- Queues: "Supabase Queues is a Postgres-native durable Message Queue system with guaranteed delivery built on the pgmq database extension." "A Message is delivered exactly once to a consumer within a customizable visibility window." — [Supabase docs: Queues](https://supabase.com/docs/guides/queues) ([source file](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/queues.mdx))
- "Supabase Queues is a pull-based Message Queue". The official consumer example is an Edge Function that reads 5 messages, processes them and deletes each. — [Supabase docs: Consuming queue messages with Edge Functions](https://supabase.com/docs/guides/queues/consuming-messages-with-edge-functions) ([source file](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/queues/consuming-messages-with-edge-functions.mdx))

### Inferences
- Because pg_cron reaches a function through pg_net from the database's region, adding `x-region: ap-south-1` (or `forceFunctionRegion`) to the `net.http_post` headers would pin an Edge Function to Mumbai. This matters only if an Indian data source prefers Indian IPs; there is no evidence here that Supabase's Mumbai edge IPs are accepted by any broker or by NSE.
- The 2 s CPU limit excludes async I/O, so an Edge Function that only fetches a few quotes and writes rows fits easily; a pandas-style backtest does not, and Python is not available anyway.
- 500,000 free invocations a month dwarfs Thunderbot's need: a 5-minute tick across the trading day is about 75 calls a day, roughly 1,650 a month.
- Queues add little for a single-worker personal bot. They are pull-based, so something still has to wake a consumer; the existing `public.jobs` table with a `status` column already gives a durable queue, and pg_cron provides the wake-up.
- An Edge Function could replace Vercel as the "thin dispatcher" only if the strategy were rewritten in TypeScript. Otherwise pg_net calling the Vercel Python function directly is one hop shorter.

### Gaps
- Whether Queues carry any plan restriction was not checked (the quickstart was downloaded but not reviewed in detail).
- The exact semantics of "soft/hard" CPU limits are in a troubleshooting article (`/kb/troubleshooting/edge-function-cpu-limits`) that could not be opened; only the 2 s figure is confirmed.

---

## A6. Does Supabase offer a static egress IP that could be whitelisted with a broker?

### Takeaway
No, as far as the official docs go: the paid IPv4 add-on gives a static address for inbound database connections only, and the docs state that outbound connections from the database have no guaranteed static IP. I found no official static-egress option for Edge Functions. Treat Supabase as unable to satisfy a broker's static-IP whitelist.

### Cited Findings
- "IPv4 addresses are guaranteed to be static for ingress traffic. If your database is making outbound connections, the outbound IP address is not static and cannot be guaranteed." — [Supabase docs: Dedicated IPv4 address for ingress](https://supabase.com/docs/guides/platform/ipv4-address) ([source file](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/ipv4-address.mdx))
- The add-on is titled "Dedicated IPv4 Address for Ingress" and is listed as "IPv4 add-on (Pro Plan and above)". "While the IPv4 address generally remains the same, actions like pausing/unpausing the project or enabling/disabling the add-on can lead to a new IPv4 address." — [Supabase docs: Dedicated IPv4 address for ingress](https://supabase.com/docs/guides/platform/ipv4-address)
- Price: "$0.0055 per hour ($4 per month)"; "IPv4 Hours are **not** covered by the Spend Cap." — [Supabase docs: Manage IPv4 usage](https://supabase.com/docs/guides/platform/manage-your-usage/ipv4) ([source file](https://github.com/supabase/supabase/blob/master/apps/docs/content/guides/platform/manage-your-usage/ipv4.mdx))
- Edge Functions run "in the region closest to the user making the request" through a "Global API Gateway" that routes to the nearest edge location. — [Supabase docs: Regional invocations](https://supabase.com/docs/guides/functions/regional-invocation) and [Edge Functions architecture](https://supabase.com/docs/guides/functions/architecture)
- SEBI's static-IP rule applies to API orders: "Static IP is mandatory for every API order, whatever the frequency. You can whitelist a primary and a backup." — local file `/home/user/thunderbot/docs/research-report.md` (the project's earlier research; cites the 4 Feb 2025 SEBI circular, fully mandatory from 1 Apr 2026)

### Inferences
- pg_net requests leave from the database host, so the docs' statement about database outbound connections applies to pg_net calls too. A pg_net source IP must not be whitelisted anywhere.
- In the Thunderbot design this does not matter for scheduling: pg_net only needs to reach a public HTTPS endpoint that authenticates with a shared secret. It matters only if any part of the stack must place live orders, which needs a static IP that neither Supabase nor (by default) Vercel provides.

### Gaps
- No official page explicitly saying "Edge Functions have no static outbound IP" was found in the files read; the conclusion rests on the absence of any such feature in the limits, architecture, regional and network-restriction pages.
- Whether a Free project's pg_net egress IP is stable in practice is unknown and unsupported; no official statement exists beyond the quote above.

---

## B1. Does Yahoo Finance's chart endpoint still work from cloud servers, and how good is it for NSE?

### Takeaway
Not tested today (the research sandbox blocked Yahoo), so this rests on yfinance's code and issue tracker: the v8 chart endpoint is still what yfinance 1.8.0 (3 Nov 2026) uses, Yahoo has returned HTTP 429 to single, low-volume requests in waves since November 2024, and from spring 2025 it appears to fingerprint clients, which is why yfinance moved to `curl_cffi` browser impersonation. Evidence that Yahoo blocks cloud IP ranges specifically is anecdotal (one AWS Lambda report in April 2025), and yfinance still has NSE-specific data-quality issues, so Yahoo is usable but must not be the only source for a job that has to run at 15:10 IST.

### Cited Findings
- LIVE TEST NOT POSSIBLE: on 10 Nov 2026 at 16:31 UTC, `curl` with a Chrome User-Agent from this cloud machine to `https://query1.finance.yahoo.com/v8/finance/chart/NIFTYBEES.NS?range=5d&interval=1d`, the same on `query2`, and `/v7/finance/quote?symbols=NIFTYBEES.NS` each failed with `curl: (56) CONNECT tunnel failed, response 403`. The proxy status endpoint recorded "gateway answered 403 to CONNECT (policy denial or other refusal)". This is the research sandbox refusing the destination, not a response from Yahoo. — test run in this session; proxy log at `$HTTPS_PROXY/__agentproxy/status`
- yfinance still builds price history from the v8 chart endpoint on `query2`: `_BASE_URL_ = 'https://query2.finance.yahoo.com'` and `url = f"{_BASE_URL_}/v8/finance/chart/{self.ticker}"`. — [yfinance const.py](https://github.com/ranaroussi/yfinance/blob/main/yfinance/const.py), [yfinance scrapers/history.py](https://github.com/ranaroussi/yfinance/blob/main/yfinance/scrapers/history.py)
- yfinance's request layer fetches a cookie from `https://fc.yahoo.com` and a crumb from `https://query1.finance.yahoo.com/v1/test/getcrumb` (fallback: a consent/CSRF flow and `query2.../v1/test/getcrumb`), adds the crumb to request parameters, and raises `YFRateLimitError` on HTTP 429 or when the crumb response contains "Too Many Requests". A code comment states: "fc.yahoo.com is non-critical: chart API works without its cookie." — [yfinance data.py](https://github.com/ranaroussi/yfinance/blob/main/yfinance/data.py)
- Release history: 0.2.54 on 18 Feb 2025 ("Hotfix user-agent #2277"); 0.2.58 on 2 May 2025 ("Fix false rate-limit problem #2430"); 0.2.59 on 7 May 2025 ("Fix the fix for rate-limit #2452"); 0.2.60 ("Fix cookie reuse, and handle DNS blocking fc.yahoo.com #2483"); 0.2.62 ("detect rate-limit during crumb fetch #2491", "replace requests.HTTPError with curl_cffi"); 1.0 on 22 Dec 2025 ("Add optional retry mechanism for transient network errors #2627", "Block curl_cffi version 0.14"); 1.4.0 on 23 May 2026 ("Make curl_cffi optional with fallback to requests"); 1.5.2 on 23 Jul 2026 ("Fix yfinance breaking with curl_cffi>=0.16"); 1.8.0 on 3 Nov 2026 (latest). — [yfinance CHANGELOG](https://github.com/ranaroussi/yfinance/blob/main/CHANGELOG.rst); dates from [PyPI yfinance](https://pypi.org/project/yfinance/)
- yfinance 1.8.0 declares `curl_cffi>=0.17` among its requirements on PyPI. — [PyPI yfinance](https://pypi.org/project/yfinance/)
- November 2024 wave: issue "Getting 429 error (rate-limit) when in loop" opened 14 Nov 2024 for `v10/finance/quoteSummary`; the crumb endpoint also returned "Too Many Requests"; a user reported it "even when using a VPN"; the maintainer noted "yfinance sends cookie-crumb with requests so Yahoo could track you despite VPN hopping"; fixed in 0.2.54 by rotating user-agent headers. — [yfinance issue #2125](https://github.com/ranaroussi/yfinance/issues/2125) (read via a summarising tool)
- The chart endpoint was hit too: issue "New rate-limiting" (15 Nov 2024) shows `response code=429` and a crumb of "Edge: Too Many Requests" on `query2.finance.yahoo.com/v8/finance/chart/{ticker}` after about 950 tickers. — [yfinance issue #2128](https://github.com/ranaroussi/yfinance/issues/2128) (read via a summarising tool)
- April-May 2025 wave: `yf.download('^GSPC')` returned `YFRateLimitError('Too Many Requests. Rate limited. Try after a while.')` from 29 Apr 2025; a user got HTTP 429 calling the chart endpoint directly with `requests`; the reporter "tried several IP addresses without success"; a user suspected TLS fingerprinting and others confirmed that `curl_cffi` with browser impersonation worked; one user reported being rate-limited on AWS Lambda (Python 3.13, yfinance 0.2.57) while the same script worked locally; another reported it "works fine on google colab". Closed 9 May 2025 with no root cause given. — [yfinance issue #2422](https://github.com/ranaroussi/yfinance/issues/2422) (read via a summarising tool)
- Not fully solved by the fix: "[0.2.61] Still 429 Error: Too Many Requests after trying previous fixes" (opened 27 May 2025, closed "not planned" 19 Jan 2026). The reporter "only sent 1 request and it didn't work"; a commenter wrote "finance.yahoo.com will return a 429 Too Many Requests under certain circumstances regardless of the number of requests"; the maintainer said "yfinance latest release works for the vast majority of users. Most of the exceptions are proven to have old versions"; a user reported it "Still not solved" on 0.2.65 in July 2025. No cloud provider is named in that thread. — [yfinance issue #2518](https://github.com/ranaroussi/yfinance/issues/2518) (read via a summarising tool)
- Later reports: a direct `curl` to the chart endpoint returning 429 after "change ip" (Dec 2025, though the test URL used an invalid interval) — [yfinance issue #2658](https://github.com/ranaroussi/yfinance/issues/2658); "DX-Y.NYB returns HTTP 500/429 while other tickers work" closed Mar 2026 — [yfinance issue #2721](https://github.com/ranaroussi/yfinance/issues/2721) (title only); a March 2026 discussion "How to handle YFRateLimitError gracefully when fetching multiple tickers?" — [yfinance discussion #2727](https://github.com/ranaroussi/yfinance/discussions/2727) (title only)
- Terms: yfinance "is intended for research and educational purposes"; "You should refer to Yahoo!'s terms of use... for details on your rights to use the actual data downloaded. Remember - the Yahoo! finance API is intended for personal use only." — [yfinance README](https://github.com/ranaroussi/yfinance/blob/main/README.md)
- NSE data-quality reports in the yfinance tracker (titles and dates; bodies not read except #2612): "Incorrect historical data for RAYMOND.NS: Abrupt drop from ₹1564 to ₹551 on 14-May-2025 with no corporate action" (#2519, May 2025); "Inaccurate price data, NSE" (#2055, Sep 2024); "Incorrect market data for NSE segment" (#2022, Aug 2024); "Unable to get history of ASIANPAINT.NS on May 4, 2022" (#2044); "Indian ETFs quoteType marked incorrectly" (#2626, Nov 2025); "HTTP 404 when fetching ZOMATO.NS" (#2545, Jun 2025). — [yfinance issue search for NSE/.NS](https://github.com/ranaroussi/yfinance/issues?q=is%3Aissue+NSE+OR+%22.NS%22+OR+NIFTYBEES+OR+BSE+OR+India+sort%3Acreated-desc)
- "'No price data found' for valid NSE/BSE symbol" (ITC.NS and RELIANCE.NS, opened 21 Oct 2025, self-resolved by 8 Nov 2025; the maintainer could not reproduce it and no cause was confirmed). — [yfinance issue #2612](https://github.com/ranaroussi/yfinance/issues/2612) (read via a summarising tool)
- yfinance 1.0 includes "Correct 30m interval alignment and filtering for NSE/early-open markets #2642", and 1.8.0 adds "Price repair: fix split-like level shift that has no matching split". — [yfinance CHANGELOG](https://github.com/ranaroussi/yfinance/blob/main/CHANGELOG.rst)
- Thunderbot's own experience with Yahoo NSE data: bad ticks had to be repaired, "e.g. NIFTYBEES 6 Oct 2010 and the unadjusted Dec 2019 1:10 split". — local file `/home/user/thunderbot/research_notes/Evidence based NSE trading strategies/thunderbot_backtests.md`
- Thunderbot's code documents further Yahoo defects: "Yahoo shows zero volume for the 09:15 bar on most days and skips a few bars"; `clean_series` exists to "Repair the two Yahoo errors we see on NSE data": short spikes and "Persistent split-sized jumps: an unadjusted split or bonus." — local files `/home/user/thunderbot/worker/thunderbot/jobs.py` and `/home/user/thunderbot/worker/thunderbot/daily.py`
- How Thunderbot fetches today: `yf.download(...)` through the `yfinance` library (`yfinance>=0.2.54` optional extra); daily history with `auto_adjust=True`, `interval="1d"`, `threads=True`; last traded price from `period="1d", interval="1m"` bars, cached 10 s; `.NS` suffix for NSE, `^` symbols passed through. — local files `/home/user/thunderbot/worker/thunderbot/yahoo.py`, `daily.py`, `worker/pyproject.toml`

### Inferences
- The pattern across 2024-2026 (429 on the first request, IP changes not helping, browser impersonation helping) points to client fingerprinting and cookie/crumb tracking more than to plain per-IP rate limits. Cloud IP ranges may be scored more harshly, but the tracker gives only one named cloud case (AWS Lambda, April 2025) against one counter-example (Colab), so "Yahoo blocks cloud IPs" is not established by what I could read.
- Thunderbot's floor of `yfinance>=0.2.54` predates the `curl_cffi` change (0.2.58/0.2.59, May 2025). A serverless deploy should pin a current release (1.8.0 as of 3 Nov 2026) and expect `curl_cffi`, a compiled dependency, in the bundle.
- yfinance makes extra calls (cookie, crumb) on a cold start before the chart call. In a serverless function every invocation is a cold start for Yahoo's purposes unless the cookie is persisted, which multiplies exposure to the crumb endpoint's 429s. A direct GET of the v8 chart URL with a browser User-Agent avoids those extra calls; yfinance's own comment says the chart API works without the cookie. Whether a plain GET succeeds from Vercel in November 2026 must be tested from Vercel.
- The correct handling is: bounded retries with backoff, a fallback source, and a "no fresh price, do nothing" rule, with the outcome written to a status row.
- `threads=True` in `daily.load_prices` fires parallel requests; for 10 symbols a sequential fetch is gentler and still fast.

### Gaps
- No live HTTP status from Yahoo could be obtained (sandbox policy). Run this from the actual Vercel function and from a laptop and compare: `curl -s -o /dev/null -w "%{http_code}\n" -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36" "https://query1.finance.yahoo.com/v8/finance/chart/NIFTYBEES.NS?range=5d&interval=1d"`.
- Stack Overflow, Reddit r/algotrading and Vercel community posts on datacentre blocking were not searched (search budget exhausted). The yfinance issue search for "github actions / lambda / vercel / ec2" returned no rate-limit issue naming those platforms in its title, which is weak evidence either way.
- Whether v7 quote and v10 quoteSummary still require a crumb while v8 chart does not: UNVERIFIED RECOLLECTION says yes (crumb required for v7/v10 since 2023; chart works without). The yfinance code comment supports the chart half only.
- Yahoo's quote delay for NSE: not verified. UNVERIFIED RECOLLECTION: Yahoo's exchange-delay help page has listed NSE as real-time and BSE as 15-minute delayed, but timestamps should be checked in the response (`meta.regularMarketTime`) on every run rather than assumed. The repo itself warns that Yahoo "can lag".
- `^NSEI` having zero volume before 2013 and Yahoo's dividend handling in adjusted close for Indian ETFs: not verified today.
- Yahoo's actual terms-of-use text was not read; only yfinance's summary of it ("personal use only") is cited.

---

## B2. What reliable free or cheap alternatives exist for NSE end-of-day prices?

### Takeaway
The only alternative I could verify today is the structure of NSE's own archive files (UDiFF bhavcopy since 8 July 2024, full bhavcopy with delivery data, index close files) as coded in two maintained open-source libraries, together with evidence that NSE's website rejects some non-browser clients from cloud servers. Pricing, coverage and cloud-reachability for Twelve Data, EODHD, Alpha Vantage, Stooq, AMFI/mfapi.in and the rest could not be checked from this session and are listed as unverified leads.

### Cited Findings
- NSE archive URL patterns used by jugaad-data (base `https://nsearchives.nseindia.com/`): UDiFF bhavcopy `/content/cm/BhavCopy_NSE_CM_0_0_0_{ymd}_F_0000.csv.zip`; full bhavcopy `/products/content/sec_bhavdata_full_{dd}{mm}{yyyy}.csv`; legacy `/content/historical/EQUITIES/{yyyy}/{MMM}/cm{dd}{MMM}{yyyy}bhav.csv.zip`. Code comment: "Date when NSE switched to UDiff format (Unified Distilled File Format)", `udiff_start_date = date(2024, 7, 8)`. — [jugaad-data archives.py](https://github.com/jugaad-py/jugaad-data/blob/master/jugaad_data/nse/archives.py)
- The same library sends a Chrome User-Agent and `Sec-CH-UA` headers to the archive host, and fetches index closes from `https://www.niftyindices.com` at `/Daily_Snapshot/ind_close_all_{dd}{mm}{yyyy}.csv` with `Referer: https://www.nseindia.com` and `X-Requested-With: XMLHttpRequest`. — [jugaad-data archives.py](https://github.com/jugaad-py/jugaad-data/blob/master/jugaad_data/nse/archives.py)
- NseIndiaApi (v5.1.1, 30 Oct 2026) uses the same files: "Before 8th July 2024, the legacy bhavcopy format is downloaded, e.g. `cm02JAN2023bhav.csv`. On or after 8th July 2024, the UDIFF bhavcopy format is used, e.g. `BhavCopy_NSE_CM_0_0_0_20250102_F_0000.csv`"; delivery report at `{archive_url}/products/content/sec_bhavdata_full_{date}.csv`; index report at `{archive_url}/content/indices/ind_close_all_{date:%d%m%Y}.csv`, with `archive_url = https://nsearchives.nseindia.com`. — [NseIndiaApi NSE.py](https://github.com/BennyThadikaran/NseIndiaApi/blob/main/src/nse/NSE.py); version date from [PyPI nse](https://pypi.org/project/nse/)
- NSE needs browser-like sessions and throttling: NseIndiaApi "sends browser-like headers on every request, loads and persists cookies", rate-limits to "3 requests/second" by default, retries on `429`, `502`, `503`, `504`, and warns that 12 requests/second from multiple workers "can quickly trigger rate limiting or temporary blocks". — [NseIndiaApi README](https://github.com/BennyThadikaran/NseIndiaApi/blob/main/README.md) and [usage docs](https://github.com/BennyThadikaran/NseIndiaApi/blob/main/docs/source/usage.rst)
- jugaad-data advertises a "Built-in caching mechanism to play nice with NSE. Avoid making un-necessary requests to NSE's website and getting blocked". — [jugaad-data README](https://github.com/jugaad-py/jugaad-data/blob/master/README.md)
- Cloud-server evidence for NSE: issue "Connection timeout issue when connecting to NSE from server environments" (27 Mar - 5 Apr 2025). From AWS EC2, Python requests to `www.nseindia.com` timed out while the same code worked locally; `curl` with HTTP/2 worked from the same server and `--http1.1` got no response. The reporter concluded "Since curl works on server, we can eliminate the possibility of NSE range-blocking my server"; the maintainer guessed NSE is "blocking requests with specific headers" rather than by IP range. Fixed by a change adding "support for the library to support connections from server environments". — [NseIndiaApi issue #9](https://github.com/BennyThadikaran/NseIndiaApi/issues/9) (read via a summarising tool)
- Another library ships a separate "Server Edition" described as "designed for server environments, seamlessly functioning on AWS, Google Colab, and DigitalOcean", distinct from its local edition. — [nsepython README](https://github.com/aeron7/nsepython/blob/master/README.md)
- A 403 on NSE's `equityQuote` endpoint was reported in May 2026 (closed as duplicate; cause not shown). — [NseIndiaApi issue #28](https://github.com/BennyThadikaran/NseIndiaApi/issues/28) (title and status only)
- LIVE TEST NOT POSSIBLE: `curl` from this machine to `https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_20261109_F_0000.csv.zip`, `https://www.nseindia.com/`, `https://www.niftyindices.com/`, `https://www.amfiindia.com/spages/NAVAll.txt`, `https://api.mfapi.in/mf/120716/latest` and `https://stooq.com/q/d/l/?s=^nsei&i=d` all failed at the research sandbox's proxy ("gateway answered 403 to CONNECT (policy denial or other refusal)"), 10 Nov 2026. Not evidence about those sites. — test run in this session
- ICICI Breeze historical data is unadjusted: "The historical data provided does not account for corporate adjusted data." — [PyPI breeze-connect](https://pypi.org/project/breeze-connect/) (v1.0.69, 14 Apr 2026)
- EODHD: "To access our APIs, you need to register on our site (it's free) and obtain an API key. Access to some data requires a subscription to one of our paid plans." — [PyPI eodhd](https://pypi.org/project/eodhd/)

### Inferences
- Bhavcopy files are raw exchange closes with no corporate-action adjustment (they are daily settlement records), so a backtest built on them must apply splits and bonuses itself. For ETFs the events are rare and known (for example NIFTYBEES 1:10 in December 2019, already handled in `daily.clean_series`).
- Bhavcopy is published after the close, so it cannot feed a 15:10 IST decision. Its role is nightly reconciliation: compare yesterday's stored close against the exchange file and flag differences from the intraday source.
- The EC2 case suggests NSE's edge filters on protocol and headers (HTTP/2, browser-like fingerprint) at least as much as on IP range. A serverless function may therefore reach the archive host with the right client, but this is unproven for Vercel and should be treated as best-effort.
- A NAV-based series (AMFI) is not a substitute for traded prices: it is a per-unit value published in the evening, it has the same discontinuity as the market price when units are split, and an ETF trades at a premium or discount to it. It is useful as an independent cross-check of an ETF's level and of split dates.

### Gaps
All of the following were requested but could not be verified on 10 Nov 2026 (hosts unreachable from the session, search budget exhausted). Statements marked UNVERIFIED RECOLLECTION are from memory to about mid-2026 and may be wrong or out of date.
- NSE bhavcopy publication time, licence terms, and whether `nsearchives.nseindia.com` serves cloud or foreign IPs without cookies. UNVERIFIED RECOLLECTION: files appear in the early evening IST; the archive host has been more permissive than `www.nseindia.com/api`, with a browser User-Agent sufficient in most reports.
- niftyindices.com historical and Total Return Index endpoints: only the daily snapshot path above is confirmed (from library code). The POST endpoints for TRI history were not checked.
- AMFI `NAVAll.txt` and NAV history, and mfapi.in. UNVERIFIED RECOLLECTION: both free with no key; NAVAll.txt is a semicolon-separated daily file updated late evening IST; mfapi.in serves full NAV history as JSON per scheme code.
- Stooq. UNVERIFIED RECOLLECTION: carries some Indian indices but little or no NSE equity/ETF coverage; whether CSV download now needs a captcha or key is unknown to me.
- Twelve Data. UNVERIFIED RECOLLECTION: free tier 800 credits/day and 8/minute; NSE India not in the free tier and placed on a paid plan. Exact plan and price not confirmed.
- EODHD. UNVERIFIED RECOLLECTION: free 20 calls/day with limited history; "EOD Historical Data - All World" about $19.99/month; NSE symbols use the `.NSE` suffix.
- Alpha Vantage. UNVERIFIED RECOLLECTION: 25 requests/day free; Indian equities mainly through `.BSE` symbols.
- Financial Modeling Prep, Marketstack, Tiingo, Polygon, Finnhub: coverage and pricing for NSE not checked. UNVERIFIED RECOLLECTION: Tiingo and Polygon have no Indian equities; Finnhub's international data is paid.
- Google Finance via Sheets `GOOGLEFINANCE("NSE:NIFTYBEES")`: not checked. UNVERIFIED RECOLLECTION: free, delayed, closes only, and usable from code only through a published-sheet CSV, which is fragile.
- TradingView (no public data API) and investing.com (scrape-blocked): not checked.
- History depth, adjustment policy and licence for every provider above.

---

## B3. Which broker data APIs give NSE history or a live price from a serverless function without a static IP?

### Takeaway
Verified today: Upstox's historical-candle endpoints are documented as needing no authorisation while its live quotes need an OAuth token; ICICI Breeze states its static-IP rule in terms of orders; Dhan exposes static-IP management in its SDK; Groww's data needs its paid plan. Everything else about broker pricing and whether data calls are exempt from static-IP checks is unverified today.

### Cited Findings
- Upstox historical candles need no token per the SDK docs: `GET /v3/historical-candle/{instrumentKey}/{unit}/{interval}/{to_date}`, `GET /v3/historical-candle/{instrumentKey}/{unit}/{interval}/{to_date}/{from_date}` and `GET /v3/historical-candle/intraday/{instrumentKey}/{unit}/{interval}` each state "### Authorization: No authorization required". — [upstox-python docs/HistoryV3Api.md](https://github.com/upstox/upstox-python/blob/master/docs/HistoryV3Api.md)
- Upstox live market quotes do need a token: the Market Quote V3 methods state "Authorization: OAUTH2". — [upstox-python docs/MarketQuoteV3Api.md](https://github.com/upstox/upstox-python/blob/master/docs/MarketQuoteV3Api.md)
- Upstox SDK is actively maintained: `upstox-python-sdk` 2.30.0 released 7 Sep 2026. — [PyPI upstox-python-sdk](https://pypi.org/project/upstox-python-sdk/)
- ICICI Breeze words the static-IP rule around orders: "Orders must be placed only from the static IP address registered with ICICI Direct while procuring API key." and "Primary or secondary static IP provided by the client can be updated only once per week." Its historical data "does not account for corporate adjusted data." — [PyPI breeze-connect](https://pypi.org/project/breeze-connect/)
- Dhan's SDK offers "Historical Data... both multiple minute timeframe OHLC and Daily OHLC" (`dhan.historical_daily_data(security_id, exchange_segment, instrument_type, from_date, to_date)`) and static-IP management: "You can manage your Static IP (whitelisting) using `set_ip`, `modify_ip`, and `get_ip`." `dhanhq` 2.3.0 released 8 Oct 2026. — [DhanHQ-py README](https://github.com/dhan-oss/DhanHQ-py/blob/main/README.md); [PyPI dhanhq](https://pypi.org/project/dhanhq/)
- Dhan pricing as recorded in the project's earlier research: "Trading API free; Data API ₹499 + taxes/month". Upstox: "No subscription; per-order fee on API orders". — local file `/home/user/thunderbot/docs/research-report.md` (earlier project research, not re-verified today)
- Groww as recorded in the project's earlier research: the Trade API "costs ₹499 + GST a month (₹4,999 a year, or a ₹0 trial with no live or historical data)"; access tokens "expire daily at 6:00 AM"; static IPs are added on the API Keys page. — local file `/home/user/thunderbot/docs/research-report.md` (not re-verified today)
- Groww's SDK exposes a live feed and LTP (`groww_feed.subscribe_live_data(...)`, `groww_feed.get_stocks_ltp("SWIGGY", timeout=3)`); `growwapi` 1.5.0 released 6 Dec 2025. — [PyPI growwapi](https://pypi.org/project/growwapi/)
- Other broker SDKs are current on PyPI: `kiteconnect` 5.2.2 (15 Sep 2026), `fyers-apiv3` 3.2.1 (30 Oct 2026, with "Historical Data" methods), `breeze-connect` 1.0.69 (14 Apr 2026), `smartapi-python` 1.5.5 (7 Feb 2025). — [PyPI kiteconnect](https://pypi.org/project/kiteconnect/), [PyPI fyers-apiv3](https://pypi.org/project/fyers-apiv3/), [PyPI smartapi-python](https://pypi.org/project/smartapi-python/)

### Inferences
- Upstox historical candles are the one broker source documented as callable with no account token, which makes them the natural no-secret fallback for daily bars. Whether the intraday candle endpoint is fresh enough to serve as a 15:10 IST price, and whether Upstox adjusts for corporate actions, must be tested.
- Any broker's live LTP needs a daily login token (TOTP or OAuth). A serverless function can hold that in Supabase, but the daily login flow is the operational cost, not the static IP.
- ICICI's wording and the SEBI rule as summarised in the project's earlier research ("mandatory for every API order") both tie the static IP to orders. That supports, but does not prove, the general claim that data calls are exempt at each broker.

### Gaps
- Which brokers enforce the static-IP check on data calls as well as orders: not verified for any broker. UNVERIFIED RECOLLECTION: the requirement applies to order placement and modification; market-data and historical endpoints generally work from any IP.
- Zerodha Kite Connect pricing and tiers. UNVERIFIED RECOLLECTION: about Rs 500/month including historical data since 2025, plus a free personal tier without market data.
- Fyers, Angel One SmartAPI, Shoonya/Finvasia and 5paisa pricing, rate limits and data terms: not checked. UNVERIFIED RECOLLECTION: Fyers, Angel One and Shoonya APIs are free with an account.
- Dhan "Data API free with trades" condition: not checked.
- Upstox rate limits, history depth, adjustment policy, and whether the no-auth candle endpoints are reachable from Vercel IPs: not tested (host blocked from this session; upstox.com docs not reachable).
- Whether Groww's quote endpoints are included in the ₹499 plan and callable without a whitelisted IP: see the sibling note `/home/user/thunderbot/research_notes/Thunderbot strategy and serverless hosting/groww_api_and_static_ip.md`; not re-checked here.

---

## B4. What synthesis facts matter for a robust, low-request price design?

### Takeaway
A daily ETF strategy on at most 10 symbols needs roughly 10-20 HTTP requests a day if history is cached in Supabase and each run fetches only the latest bar, so rate limits are not the binding risk; first-request blocking and silent bad data are. The sourced facts support a primary + fallback + nightly reconciliation layout with every outcome written to Postgres.

### Cited Findings
- Thunderbot currently re-downloads full history through `yf.download` for a date range and caches only to a local pickle file (`cache_dir / f"daily_{start}_{end}.pkl"`), which a serverless function cannot keep between runs. — local file `/home/user/thunderbot/worker/thunderbot/daily.py`
- Yahoo has returned 429 to a single request with no prior volume. — [yfinance issue #2518](https://github.com/ranaroussi/yfinance/issues/2518)
- One user reported about 950 chart requests succeeding before 429s began in November 2024. — [yfinance issue #2128](https://github.com/ranaroussi/yfinance/issues/2128)
- pg_net does not retry and its queue is unlogged. — [Supabase docs: pg_net](https://supabase.com/docs/guides/database/extensions/pg_net); [pg_net README](https://github.com/supabase/pg_net/blob/master/README.md)
- Free database size is 500 MB per project. — [Supabase docs: Billing](https://supabase.com/docs/guides/platform/billing-on-supabase)
- Exchange files exist for after-the-fact checking (UDiFF bhavcopy, full bhavcopy, index closes). — [jugaad-data archives.py](https://github.com/jugaad-py/jugaad-data/blob/master/jugaad_data/nse/archives.py)
- Upstox documents no-auth historical candle endpoints. — [upstox-python docs/HistoryV3Api.md](https://github.com/upstox/upstox-python/blob/master/docs/HistoryV3Api.md)

### Inferences
- Request budget for the daily strategy: 10 symbols × 1 chart call each (a `range=5d&interval=1d` call returns the latest bar plus a few days for overlap checks) = 10 calls at 15:10 IST; a single benchmark index adds 1. With a second pass for retries or a fallback source, that is at most about 20-25 calls a day, around 6,000 a year. Even a 25-request/day free tier would cover the fallback role for a handful of symbols.
- If the 5-minute tick also fetched prices, it would be about 75 ticks × 10 symbols = 750 calls a day, still small, but each tick is another chance to hit a first-request 429. For a strategy that decides once at 15:10 IST, the 5-minute ticks should do housekeeping (job sweeping, heartbeats) and only the decision tick should fetch prices.
- Storage: a `prices_daily(symbol, date, open, high, low, close, volume, source, fetched_at)` table for 10 symbols over 20 years is about 50,000 rows, a few MB.
- Suggested layering, each element tied to a sourced weakness: (1) cache all history in Supabase and fetch only the newest bars, because serverless has no local cache and every extra Yahoo call is exposure; (2) on each run, compare the overlapping days against stored values and refuse to trade on a split-sized jump, because unadjusted splits and bad ticks are documented; (3) fall back to a second source when the primary fails or the last bar's timestamp is stale; (4) reconcile nightly against exchange files where reachable; (5) write a status row per run so a dead scheduler or a blocked fetch is visible, because pg_net will not retry and a paused Free project stops pg_cron.
- "Adjusted" history from one source and raw closes from another must not be mixed in one series. Store raw closes plus an explicit corporate-action factor, or store one source's adjusted series and use others only as cross-checks.

### Gaps
- No source or endpoint was live-tested from any cloud IP in this session, so the choice of primary and fallback cannot be ranked on evidence yet. The decisive test is a small script run from the real Vercel deployment (and ideally from the Mumbai region) hitting Yahoo v8 chart, Upstox historical candles and the NSE archive host for a week, logging HTTP status and bar timestamps at 15:10 IST.
- Whether any free source provides a trustworthy live price for NSE ETFs at 15:10 IST without an account remains unconfirmed.
