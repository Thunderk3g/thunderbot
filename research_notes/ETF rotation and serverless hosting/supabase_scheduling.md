# Supabase (free plan) as the scheduler for a serverless worker: pg_cron, pg_net, Vault, webhooks/triggers, pausing, Edge Function limits (state as of 2026-11-11)

Method note for the report writer: all Supabase documentation text and SQL below was copied on 2026-11-11 from the documentation source files in `supabase/supabase` (`apps/docs/content/...`, `master` branch), which are what `supabase.com/docs` renders; the links point at the rendered pages. SQL blocks labelled **official (verbatim)** are unmodified. Blocks labelled **ADAPTED** are my own adaptation of an official pattern and have NOT been executed against a live project. Several Supabase doc pages (and one Vercel page) contain an embedded note addressed to AI agents asking them to file a documentation feedback report; that is page content, not part of this task, and was ignored.

---

## 1. pg_cron on Supabase (availability, enabling, intervals, timezone, limits, run history, syntax)

### Takeaway
Supabase Cron is the `pg_cron` extension plus a Dashboard UI (Integrations > Cron); the docs put no plan restriction on it, schedules are 5-field cron in GMT/UTC or `'N seconds'` (1-59), and Supabase recommends at most 8 concurrent jobs, each under 10 minutes. Run history in `cron.job_run_details` is never pruned automatically, so a cleanup job is required.

### Cited Findings

**What it is / where it lives**
- "Supabase Cron is a Postgres Module that simplifies scheduling recurring Jobs with cron syntax and monitoring Job runs inside Postgres." Jobs "can be created via SQL or the Integrations -> Cron interface inside the Dashboard, and can run anywhere from every second to once a year." — [Supabase Cron overview](https://supabase.com/docs/guides/cron)
- "Every Job can run SQL snippets or database functions with zero network latency or make an HTTP request, such as invoking a Supabase Edge Function, with ease." — [Supabase Cron overview](https://supabase.com/docs/guides/cron)
- "For best performance, we recommend no more than 8 Jobs run concurrently. Each Job should run no more than 10 minutes." — [Supabase Cron overview](https://supabase.com/docs/guides/cron)
- Under the hood it uses `pg_cron`; "The extension creates a `cron` schema in your database and all Jobs are stored on the `cron.job` table. Every Job's run and its status is recorded on the `cron.job_run_details` table." — [Supabase Cron overview](https://supabase.com/docs/guides/cron)
- The old extension page now only says "See the Supabase Cron docs." — [pg_cron extension page](https://supabase.com/docs/guides/database/extensions/pg_cron)

**Enabling** — Dashboard: "Go to the Cron Postgres Module under Integrations in the Dashboard. Enable the `pg_cron` extension." SQL, official (verbatim) — [Cron install](https://supabase.com/docs/guides/cron/install):

```sql
create extension pg_cron with schema pg_catalog;

grant usage on schema cron to postgres;
grant all privileges on all tables in schema cron to postgres;
```

Uninstall (official, verbatim; "Disabling the `pg_cron` extension will permanently delete all Jobs."):

```sql
drop extension if exists pg_cron;
```

**Schedule syntax** — official cron-syntax chart, identical in the Supabase quickstart and the pg_cron README — [Cron quickstart](https://supabase.com/docs/guides/cron/quickstart), [pg_cron README](https://github.com/citusdata/pg_cron):

```
┌───────────── min (0 - 59)
│ ┌────────────── hour (0 - 23)
│ │ ┌─────────────── day of month (1 - 31)
│ │ │ ┌──────────────── month (1 - 12)
│ │ │ │ ┌───────────────── day of week (0 - 6) (0 to 6 are Sunday to
│ │ │ │ │                  Saturday, or use names; 7 is also Sunday)
│ │ │ │ │
│ │ │ │ │
* * * * *
```

- Day-of-week numbering confirmed: 0-6 = Sunday-Saturday, 7 is also Sunday, names allowed; so `1-5` = Monday-Friday. The pg_cron README gives `0 0 * * 1-5   # 12AM every weekday` as an example. — [pg_cron README](https://github.com/citusdata/pg_cron)
- Sub-minute: "You can use [1-59] seconds (e.g. `30 seconds`) as the cron syntax to schedule sub-minute Jobs." and "You can input seconds for your Job schedule interval as long as you're on Postgres version 15.1.1.61 or later." — [Cron quickstart](https://supabase.com/docs/guides/cron/quickstart)
- pg_cron README: "to use `[1-59] seconds` to schedule a job based on an interval. Note, you cannot use seconds with the other time units." It also supports `$` for last day of month. — [pg_cron README](https://github.com/citusdata/pg_cron)
- Smallest standard cron interval is one minute (`* * * * *     # every minute`). — [pg_cron README](https://github.com/citusdata/pg_cron)
- Timezone: every Supabase example annotates times as GMT (e.g. `'30 3 * * 6', -- Saturday at 3:30AM (GMT)`). pg_cron's `cron.timezone` setting defaults to `GMT` ("Timezone in which the pg_cron background worker should run") and is a postmaster-level setting that needs a server restart. — [Cron quickstart](https://supabase.com/docs/guides/cron/quickstart), [pg_cron README](https://github.com/citusdata/pg_cron)

**Job naming** — "Job names are case sensitive and cannot be edited once created. Attempting to create a second Job with the same name (and case) will overwrite the first Job." — [Cron quickstart](https://supabase.com/docs/guides/cron/quickstart)

**Official SQL (verbatim)** — all from [Cron quickstart](https://supabase.com/docs/guides/cron/quickstart):

Schedule:
```sql
-- Cron Job name cannot be edited
select cron.schedule('permanent-cron-job-name', '30 seconds', 'CALL do_something()');
```

Edit:
```sql
select cron.alter_job(
  job_id := (select jobid from cron.job where jobname = 'permanent-cron-job-name'),
  schedule := '*/5 * * * *'
);
```

Full `cron.alter_job` options ("It is also possible to modify a job by using the `cron.schedule()` function by inputting the same job name. This will replace the existing job via upsert."):
```sql
cron.alter_job(
  job_id bigint,
  schedule text default null,
  command text default null,
  database text default null,
  username text default null,
  active boolean default null
)
```

Activate / deactivate:
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

Unschedule ("Unscheduling a Job will permanently delete the Job from `cron.job` table but its run history remain in `cron.job_run_details` table."):
```sql
select cron.unschedule('permanent-cron-job-name');
```

Inspect runs:
```sql
select
  *
from cron.job_run_details
where jobid = (select jobid from cron.job where jobname = 'permanent-cron-job-name')
order by start_time desc
limit 10;
```

Prune run history ("`cron.job_run_details` grows with every Job run and is never cleaned up automatically, even after a Job is unscheduled. Schedule a Job to delete old records, keeping only the last 7 days"):
```sql
select cron.schedule(
  'job-run-details-cleanup', -- name of the cron job
  '0 0 * * *', -- daily at midnight (GMT)
  $$ delete from cron.job_run_details where end_time < now() - interval '7 days' $$
);
```

Call a database function every 5 minutes:
```sql
select cron.schedule('call-db-function', '*/5 * * * *', 'SELECT hello_world()');
```

Invoke an HTTP endpoint (Edge Function) every 30 seconds, with an explicit pg_net timeout ("This requires the `pg_net` extension to be enabled."):
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

**Official SQL (verbatim): scheduled HTTP call with secrets pulled from Vault** — [Scheduling Edge Functions](https://supabase.com/docs/guides/functions/schedule-functions). Page text: "Call the function with your secret key. Don't use your publishable key, because it's public and anyone who has it can call a function that accepts it. Store your project URL and secret key in Supabase Vault":

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

**Dashboard path** — "Go to the Jobs section ... Click on `Create job` ... Choose a schedule for your Job by inputting cron syntax ... or natural language. Input SQL snippet or select a Database function, HTTP request, or Supabase Edge Function." — [Cron quickstart](https://supabase.com/docs/guides/cron/quickstart)

**Concurrency / overlap** — "pg_cron can run multiple jobs in parallel, but only one instance of each specific job at a time. If a second instance is triggered before the first finishes, it's queued and starts as soon as the first one completes." Upstream default `cron.max_running_jobs` is `32`. — [pg_cron README](https://github.com/citusdata/pg_cron). Supabase's debugging guide says pg_cron "supports up to 32 concurrent jobs" and that each concurrent job uses a database connection. — [pg_cron debugging guide](https://supabase.com/docs/guides/troubleshooting/pgcron-debugging-guide-n1KTaz)

**Debugging jobs that do not run** — official SQL (as returned by the fetch tool from the troubleshooting page; re-check formatting on the page before pasting) — [pg_cron debugging guide](https://supabase.com/docs/guides/troubleshooting/pgcron-debugging-guide-n1KTaz):
```sql
SELECT
  pid as process_id,
  usename as database_user,
  application_name,
  backend_start as when_process_began,
  wait_event_type,
  state,
  query,
  backend_type
FROM pg_stat_activity where application_name ilike 'pg_cron scheduler';
```
If this returns no row, "the worker has died"; fix is a fast reboot from General Settings. Postgres v15.6.1.122+ carries pg_cron v1.6.4 with fixes and auto-revive. Failed runs:
```sql
SELECT *
FROM cron.job_run_details
WHERE
    (status <> 'succeeded' AND status <> 'running')
        AND
     start_time > NOW() - INTERVAL '5 days'
ORDER BY start_time DESC
LIMIT 10;
```

### Inferences
- No Supabase doc page fetched gates pg_cron, pg_net or Vault by plan (the plan-gated items the docs do call out are things like PITR, IPv4 add-on, SSO, image transforms). The install pages simply say to enable the extension. So all three should be usable on the Free plan; this is inference from absence of a restriction, not an explicit "available on Free" statement.
- Because a `net.http_post` call returns immediately, the cron job itself finishes in milliseconds, so the "10 minutes per job / 8 concurrent" recommendation is not a practical constraint for an HTTP-dispatch job; the long-running work happens in Vercel.
- A `cron.schedule` command that reads the token via a `vault.decrypted_secrets` sub-select stores only the SQL text (not the token) in `cron.job.command`.
- On the free tier's 500 MB database, a 5-minute job adds roughly 80 rows/trading day to `cron.job_run_details`; small, but the pruning job should still be scheduled.

### Gaps
- The claim "seconds schedules arrived in pg_cron 1.5" was not verified in this session; the Supabase doc states the requirement as Postgres image version 15.1.1.61+, and the pg_cron README states the feature without a version.
- I found no Supabase doc that explicitly states `cron.timezone` on the hosted platform or whether it can be changed; only the GMT annotations in the examples and the upstream default.
- No explicit official sentence "pg_cron is available on the Free plan" was found.

---

## 2. pg_net (availability, signatures, async model, timeouts, responses, limits, debugging)

### Takeaway
`net.http_get/http_post/http_delete` only enqueue a request and return a `bigint` request id; a background worker sends it after the transaction commits, and the response is stored in `net._http_response` for 6 hours. `timeout_milliseconds` is "the maximum number of milliseconds the request may take before being canceled", so pg_net does drop the connection at the timeout; whether the Vercel function keeps running is decided on the Vercel side (cancellation on client disconnect is opt-in there).

### Cited Findings

**Status and enabling**
- "The pg_net API is in beta. Functions signatures may change." — [pg_net docs](https://supabase.com/docs/guides/database/extensions/pg_net)
- "pg_net enables Postgres to make asynchronous HTTP/HTTPS requests in SQL. It differs from the `http` extension in that it is asynchronous by default. This makes it useful in blocking functions (like triggers)." — [pg_net docs](https://supabase.com/docs/guides/database/extensions/pg_net)
- Dashboard: Database > Extensions > search "pg_net" and enable. SQL, official (verbatim):
```sql
-- Example: enable the "pg_net" extension.
create extension pg_net with schema "extensions";
-- Note: The extension creates its own schema/namespace named "net" to avoid naming conflicts. Registering it in the extensions schema avoids exposing it in public and satisfies the Security Advisor check.

-- Example: disable the "pg_net" extension
drop extension if exists pg_net;
drop schema net;
```
— [pg_net docs](https://supabase.com/docs/guides/database/extensions/pg_net)

**Signatures, official (verbatim) from the Supabase docs** — [pg_net docs](https://supabase.com/docs/guides/database/extensions/pg_net). Each is described as "returning the request's ID. HTTP requests are not started until the transaction is committed." and each is a `SECURITY DEFINER` function.

```sql
net.http_get(
    -- url for the request
    url text,
    -- key/value pairs to be url encoded and appended to the `url`
    params jsonb default '{}'::jsonb,
    -- key/values to be included in request headers
    headers jsonb default '{}'::jsonb,
    -- the maximum number of milliseconds the request may take before being canceled
    timeout_milliseconds int default 2000
)
    -- request_id reference
    returns bigint

    strict
    volatile
    parallel safe
    language plpgsql
```

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

```sql
net.http_delete(
    -- url for the request
    url text,
    -- key/value pairs to be url encoded and appended to the `url`
    params jsonb default '{}'::jsonb,
    -- key/values to be included in request headers
    headers jsonb default '{}'::jsonb,
    -- the maximum number of milliseconds the request may take before being canceled
    timeout_milliseconds int default 2000
)
    -- request_id reference
    returns bigint

    strict
    volatile
    parallel safe
    language plpgsql
    security definer
```

- **CONFLICT on the default timeout:** the Supabase docs page shows `timeout_milliseconds int default 2000` for all three functions — [pg_net docs](https://supabase.com/docs/guides/database/extensions/pg_net); the pg_net repository README (master, fetched 2026-11-11) shows `timeout_milliseconds int default 5000` for all three — [pg_net README](https://github.com/supabase/pg_net). The default therefore depends on the pg_net version installed in the project. Database Webhooks default to 1000 ms (see section 4). Always pass `timeout_milliseconds` explicitly.
- Upper bound: "**pg_net.max_timeout_ms** (default: 600000): An integer that bounds the `timeout_milliseconds` of a request. A request with a timeout outside `1..pg_net.max_timeout_ms` is not sent and gets an `ERROR` response saying so, so every request has a finite lifetime and a single request can't block the others. Only superusers can change it." — [pg_net README](https://github.com/supabase/pg_net) (master README; may not exist in older installed versions)

**Async model**
- "When any of the three request functions (`http_get`, `http_post`, `http_delete`) are invoked, they create an entry in the `net.http_request_queue` table." "Once a response is received, it gets stored in the `_http_response` table." The extension uses libcurl "within a PostgreSQL background worker"; "This background worker sleeps until it receives a signal from the request functions, which awakes it and prompts it to read the `net.http_request_queue` table and execute the requests on it." — [pg_net README](https://github.com/supabase/pg_net)
- "Waiting requests are stored in the `net.http_request_queue` table. Upon execution, they are deleted." Table definitions, official (verbatim) — [pg_net docs](https://supabase.com/docs/guides/database/extensions/pg_net):
```sql
CREATE UNLOGGED TABLE
    net.http_request_queue (
        id bigint NOT NULL DEFAULT nextval('net.http_request_queue_id_seq'::regclass),
        method text NOT NULL,
        url text NOT NULL,
        headers jsonb NOT NULL,
        body bytea NULL,
        timeout_milliseconds integer NOT NULL
    )
```
```sql
CREATE UNLOGGED TABLE
    net._http_response (
        id bigint NULL,
        status_code integer NULL,
        content_type text NULL,
        headers jsonb NULL,
        content text NULL,
        timed_out boolean NULL,
        error_msg text NULL,
        created timestamp with time zone NOT NULL DEFAULT now()
    )
```
- "Once a response is returned, by default, it is stored for 6 hours in the `net._http_response` table." — [pg_net docs](https://supabase.com/docs/guides/database/extensions/pg_net)
- "The extension is configured to reliably execute up to 200 requests per second. The response messages are stored for only 6 hours to prevent needless buildup." — [pg_net docs](https://supabase.com/docs/guides/database/extensions/pg_net)
- README config: `pg_net.batch_size` (default 200) "limits the max number of rows that the extension will process from `net.http_request_queue` during each read"; `pg_net.ttl` (default 6 hours); "the deletion won't happen exactly after the TTL has passed. The worker will perform this deletion while its processing requests." — [pg_net README](https://github.com/supabase/pg_net)
- Changing settings on Supabase needs pg_net v0.12.0+ and Support to grant the privilege (`grant alter system on parameter pg_net.ttl to postgres;`), then:
```sql
alter system set pg_net.ttl to '24 hours';
select net.worker_restart();
```
— [pg_net docs](https://supabase.com/docs/guides/database/extensions/pg_net)

**Limitations, official (verbatim list)** — [pg_net docs](https://supabase.com/docs/guides/database/extensions/pg_net):
- "To improve speed and performance, the requests and responses are stored in unlogged tables, which are not preserved during a crash or unclean shutdown."
- "By default, response data is saved for only 6 hours"
- "Can only make POST requests with JSON data. No other data formats are supported"
- "Intended to handle at most 200 requests per second. Increasing the rate can introduce instability"
- "Does not have support for PATCH/PUT requests"
- "Can only work with one database at a time. It defaults to the `postgres` database."
- README phrasing: "it only supports three types of asynchronous requests: async http GET requests; async http POST requests with a *JSON* payload; async http DELETE requests". — [pg_net README](https://github.com/supabase/pg_net)

**Debugging, official (verbatim)** — [pg_net docs](https://supabase.com/docs/guides/database/extensions/pg_net):
```sql
select * from net._http_response;
```
```sql
select
  *
from net._http_response
where "status_code" >= 400 or "error_msg" is not null
order by "created" desc;
```
```sql
select
    net.http_post(
        url := 'https://postman-echo.com/post',
        body := '{"key1": "value", "key2": 5}'::jsonb
    ) as request_id;
```
```sql
select
  "name",
  "setting"
from pg_settings
where "name" like 'pg_net%';
```
- Webhook debugging guide: `net._http_response` "saves all the response messages from the past 6 hours"; a timed-out request shows as a row where "every column contains NULL values, except for the `id`, `error_msg`, and `created` columns"; a timeout bug "has been patched in `pg_net` v0.11", "available in Postgres 15.6.1.135 and above"; when requests time out en masse, "increase your webhook's timeout". Check the worker with `select pid from pg_stat_activity where backend_type ilike '%pg_net%';` and restart with `select net.worker_restart();` (pg_net 0.8+). Do not add triggers to `net._http_response` or `net.http_request_queue` ("can lead to an infinite loop"). — [Webhook debugging guide](https://supabase.com/docs/guides/troubleshooting/webhook-debugging-guide-M8sk47)
- Retries are not built in: "While the net._http_response table logs each request, it doesn't store all the necessary information to retry failed requests", so the README shows a user-built `request_tracker` table and `request_wrapper` function. — [pg_net README](https://github.com/supabase/pg_net)

**Security note on headers** — "Any role that can log in to your database can read the secret key while the request waits. `pg_net` writes the decrypted key to `net.http_request_queue` until it sends the request." — [Scheduling Edge Functions](https://supabase.com/docs/guides/functions/schedule-functions) / [Database Webhooks](https://supabase.com/docs/guides/database/webhooks). Also: "By default, the `net` schema grants `USAGE` to `PUBLIC`", but `net` is not exposed through the Data API and `anon`/`authenticated` are `NOLOGIN` roles. — [pg_net docs](https://supabase.com/docs/guides/database/extensions/pg_net)

**Does the timeout cancel a Vercel function?** (target-side behaviour, from Vercel docs last updated 2026-08-11)
- "Cancellation is opt-in. In your `vercel.json`, add `"supportsCancellation": true` to the specific paths you want to enable it for." "This feature is only available in the Node.js runtime." "When cancellation is enabled ... When the client disconnects, the signal fires and the function is terminated." "Termination on disconnect applies to every function matching the glob, whether or not your code listens for the abort signal. Any work not wrapped in `waitUntil` or `after` will be lost on cancellation. This is why cancellation is opt-in." — [Vercel Functions API reference](https://vercel.com/docs/functions/functions-api-reference)

### Inferences
- The SQL statement that calls `net.http_post` never waits for the HTTP response, so a 120-second endpoint does not block the cron job, the trigger, or the inserting transaction.
- pg_net itself abandons the HTTP request at `timeout_milliseconds` (the docs' word is "canceled"). With the default (2000 or 5000 ms) a 120-second endpoint will always be recorded as timed out in `net._http_response` even if the work succeeds. Two workable designs: (a) pass `timeout_milliseconds := 150000` or similar (within the 600000 ms bound documented in the README) so the real status code is recorded; or (b) have the Vercel endpoint acknowledge quickly (e.g. 202) and continue with `waitUntil`, and write its own result row back to Supabase.
- If the caller disconnects early, a Vercel function is terminated only when `supportsCancellation` is enabled for that path (Node.js only). With the default configuration, and for the Python runtime (which the cancellation feature does not cover), the function should keep running to completion or to its own `maxDuration`. This is inferred from the opt-in wording; Vercel does not state an explicit guarantee for non-Node runtimes on that page.
- A timed-out row is indistinguishable from a genuine network failure, so success should be tracked by the worker writing back to a table, not by `net._http_response`.
- Because the queue and response tables are unlogged, a database crash/unclean restart can silently drop queued requests; combined with no built-in retry, the target must tolerate missed and duplicated calls.

### Gaps
- Which pg_net version (and therefore which default timeout and whether `pg_net.max_timeout_ms` exists) a new free-plan project gets in November 2026 was not determined; check with `select extversion from pg_extension where extname = 'pg_net';` and the `pg_settings` query above.
- No official statement on outbound concurrency limits or connection reuse beyond "200 requests per second".
- Not tested empirically: whether a Vercel Python function really continues after pg_net's timeout.

---

## 3. Supabase Vault (store, read, update, security model, use inside pg_cron + pg_net)

### Takeaway
Vault stores secrets encrypted (AEAD via libsodium) in `vault.secrets` and exposes plaintext through the `vault.decrypted_secrets` view at query time; the encryption key is held outside the database by Supabase. The official pattern is a sub-select on `vault.decrypted_secrets` inside the `net.http_post` call, with the caveat that pg_net then holds the decrypted header in `net.http_request_queue` until it is sent.

### Cited Findings
- "Vault is a Postgres extension and accompanying Supabase UI that makes it safe and easy to store encrypted secrets and other data in your database." Secrets are "stored using Authenticated Encryption on disk" and "available in decrypted form through a Postgres view"; "any backups or replication streams also preserve this encryption". — [Vault docs](https://supabase.com/docs/guides/database/vault)
- "You can use Vault to store secrets - everything from Environment Variables to API Keys. You can then use these secrets anywhere in your database: Postgres Functions, Triggers, and Webhooks." — [Vault docs](https://supabase.com/docs/guides/database/vault)

Official SQL (verbatim) — [Vault docs](https://supabase.com/docs/guides/database/vault):

Create (returns the new secret's UUID; name must be unique, name and description optional):
```sql
select vault.create_secret('my_s3kre3t');
```
```sql
select vault.create_secret('another_s3kre3t', 'unique_name', 'This is the description');
```

Read:
```sql
select * 
from vault.decrypted_secrets 
order by created_at desc 
limit 3;
```

Update (UUID first, then new secret, name, description):
```sql
select
  vault.update_secret(
    '7095d222-efe5-4cd5-b5c6-5755b451e223',
    'n3w_upd@ted_s3kret',
    'updated_unique_name',
    'This is the updated description'
  );
```

Delete:
```sql
delete from vault.secrets
where id = '7095d222-efe5-4cd5-b5c6-5755b451e223'
returning id, name;
```

- "Views are not stored on disk, they are only run at query time, so the secret remains encrypted on disk, and in any backup dumps or replication streams." "You should ensure that you protect access to this view with the appropriate SQL privilege settings at all times, as anyone that has access to the view has access to decrypted secrets." — [Vault docs](https://supabase.com/docs/guides/database/vault)
- "the encryption key is never stored in the database alongside the encrypted data"; "Supabase creates and manages a unique encryption key for each project in our secured backend systems"; the Management API returns the project's 64-character hex root key. — [Vault docs](https://supabase.com/docs/guides/database/vault)
- "Same-project operations - pausing and restoring, and Point-in-Time or in-place restores - keep the same key, so your secrets stay readable automatically." A manual `pg_dump`/`pg_restore` into a new project cannot decrypt old secrets unless the root key is copied, and the `pgsodium` Management API endpoint "is only available for active (not paused or removed) projects". — [Vault docs](https://supabase.com/docs/guides/database/vault)
- Official pattern for reading the secret by name inside a pg_net call (verbatim) — [Migrating to new API keys](https://supabase.com/docs/guides/getting-started/migrating-to-new-api-keys): "Don't hardcode a secret key in SQL or a webhook configuration, where it's stored in plain text. Store it in Vault and read it at call time:"
```sql
headers := jsonb_build_object(
  'Content-Type', 'application/json',
  'apikey', (select decrypted_secret from vault.decrypted_secrets where name = 'secret_key')
)
```
- The complete official `cron.schedule` + `net.http_post` + Vault example is in section 1 (from [Scheduling Edge Functions](https://supabase.com/docs/guides/functions/schedule-functions)).
- Trigger functions that read Vault must be `security definer`: "because the roles that insert rows, such as `authenticated`, can't read Vault. Without it, their inserts fail with a permission error." — [Database Webhooks](https://supabase.com/docs/guides/database/webhooks)

**ADAPTED (not official, not executed): Vault secrets + pg_cron + `net.http_post` to a Vercel endpoint with an `Authorization: Bearer` header.** The current official examples send a Supabase secret key on the `apikey` header; for a non-Supabase target with its own shared token, the same sub-select is concatenated into a Bearer header:

```sql
-- ADAPTED from https://supabase.com/docs/guides/functions/schedule-functions
-- run once in the SQL editor, outside migrations
select vault.create_secret('https://YOUR-APP.vercel.app', 'worker_url', 'Base URL of the Vercel worker');
select vault.create_secret('LONG_RANDOM_TOKEN', 'worker_token', 'Shared bearer token checked by the Vercel worker');

select
  cron.schedule(
    'market-tick',
    '*/5 3-10 * * 1-5', -- every 5 min, 03:00-10:55 UTC, Mon-Fri (see section 5)
    $$
    select
      net.http_post(
          url := (select decrypted_secret from vault.decrypted_secrets where name = 'worker_url') || '/api/tick',
          headers := jsonb_build_object(
            'Content-Type', 'application/json',
            'Authorization', 'Bearer ' || (select decrypted_secret from vault.decrypted_secrets where name = 'worker_token')
          ),
          body := jsonb_build_object('source', 'pg_cron', 'scheduled_at', now()),
          timeout_milliseconds := 10000
      ) as request_id;
    $$
  );
```

### Inferences
- Rotating the token is `vault.update_secret(<uuid>, <new value>)`; because the cron job reads the secret at run time, no job needs to be rescheduled.
- No doc fetched restricts Vault to paid plans; treat Free-plan availability as likely but not explicitly confirmed (see Gaps).
- The Vault protects the token at rest and in dumps; it does not hide it from database login roles at send time (queue-table caveat in section 2).

### Gaps
- The current Vault page does not show a `where name = '...'` example on its own; that form appears in the schedule-functions, webhooks and API-key migration pages (cited above).
- No explicit plan-availability statement for Vault was found. No explicit doc statement on whether statement logging could capture `vault.create_secret('...')` literals; that concern is not addressed on the current Vault page.

---

## 4. Firing an HTTPS call when a row is inserted (Database Webhooks vs own trigger + `net.http_post`)

### Takeaway
A Database Webhook is just an `after insert/update/delete ... for each row` trigger that executes `supabase_functions.http_request(url, method, headers, params, timeout_ms)`, which in turn calls pg_net; you can equally write your own trigger function calling `net.http_post`, which is the officially recommended route when the secret must come from Vault. In both cases the HTTP request is only sent after the inserting transaction commits.

### Cited Findings
- "You can hook into three table events: `INSERT`, `UPDATE`, and `DELETE`. All events are fired *after* a database row is changed." — [Database Webhooks](https://supabase.com/docs/guides/database/webhooks)
- "Database Webhooks are very similar to triggers, and that's because Database Webhooks are a convenience wrapper around triggers using the pg_net extension. This extension is asynchronous, and therefore will not block your database changes for long-running network requests." — [Database Webhooks](https://supabase.com/docs/guides/database/webhooks)
- "We currently support HTTP webhooks. These can be sent as `POST` or `GET` requests with a JSON payload." — [Database Webhooks](https://supabase.com/docs/guides/database/webhooks)
- Dashboard: Integrations > Webhooks; name it, pick the table, pick events. — [Database Webhooks](https://supabase.com/docs/guides/database/webhooks)

**Option A, official (verbatim): webhook created from SQL** — [Database Webhooks](https://supabase.com/docs/guides/database/webhooks):
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
- Argument order and defaults, from the function source shipped in the Supabase repo: `TG_ARGV[0]` = url, `[1]` = method, `[2]` = headers JSON (default `{"Content-Type": "application/json"}`), `[3]` = params JSON (default `{}`), `[4]` = timeout in ms (default `1000`). Only `GET` and `POST` are accepted (`method argument % is invalid` otherwise). For POST it builds the payload with `jsonb_build_object('old_record', OLD, 'record', NEW, 'type', TG_OP, 'table', TG_TABLE_NAME, 'schema', TG_TABLE_SCHEMA)`, calls `net.http_post(url, payload, params, headers, timeout_ms)` and records `(hook_table_id, hook_name, request_id)` in `supabase_functions.hooks`. — [supabase/supabase docker/volumes/db/webhooks.sql](https://github.com/supabase/supabase/blob/master/docker/volumes/db/webhooks.sql) (this is the self-hosting copy of the function; the hosted platform's copy may differ in detail)
- Secrets caveat: "The webhook saves the key in its trigger definition, so the key appears anywhere the trigger's SQL does, such as a database dump." — [Database Webhooks](https://supabase.com/docs/guides/database/webhooks)

**Payload format, official (verbatim)** — [Database Webhooks](https://supabase.com/docs/guides/database/webhooks):
```typescript
type InsertPayload = {
  type: 'INSERT'
  table: string
  schema: string
  record: TableRecord<T>
  old_record: null
}
type UpdatePayload = {
  type: 'UPDATE'
  table: string
  schema: string
  record: TableRecord<T>
  old_record: TableRecord<T>
}
type DeletePayload = {
  type: 'DELETE'
  table: string
  schema: string
  record: null
  old_record: TableRecord<T>
}
```

**Option B, official (verbatim): own trigger function reading Vault and calling `net.http_post`** — [Database Webhooks, "From a migration"](https://supabase.com/docs/guides/database/webhooks). First, once per project, outside migrations:
```sql
select vault.create_secret('https://project-ref.supabase.co', 'project_url');
select vault.create_secret('YOUR_SUPABASE_SECRET_KEY', 'secret_key');
```
Then in a migration:
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

**Option B variant, official (verbatim): generic pg_net-in-trigger example** — [pg_net docs](https://supabase.com/docs/guides/database/extensions/pg_net):
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

- After-commit semantics: "HTTP requests are not started until the transaction is committed." — [pg_net docs](https://supabase.com/docs/guides/database/extensions/pg_net)
- Monitoring: "Logging history of webhook calls is available under the `net` schema of your database." — [Database Webhooks](https://supabase.com/docs/guides/database/webhooks)

**ADAPTED (not official, not executed): `jobs` insert -> Vercel endpoint with Bearer token from Vault**
```sql
-- ADAPTED from the official "From a migration" trigger at
-- https://supabase.com/docs/guides/database/webhooks
create function public.notify_worker_job_inserted()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  perform net.http_post(
    url := (select decrypted_secret from vault.decrypted_secrets where name = 'worker_url') || '/api/run-job',
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'Authorization', 'Bearer ' || (select decrypted_secret from vault.decrypted_secrets where name = 'worker_token')
    ),
    body := jsonb_build_object(
      'type', tg_op,
      'table', tg_table_name,
      'schema', tg_table_schema,
      'record', to_jsonb(new),
      'old_record', null
    ),
    timeout_milliseconds := 10000
  );
  return new;
end;
$$;

create trigger notify_worker_job_inserted
after insert on public.jobs
for each row execute function public.notify_worker_job_inserted();
```

### Inferences
- For a Vercel target protected by a shared token, Option B is preferable: Option A would embed the token in the trigger definition (visible in dumps and `pg_trigger`), while Option B keeps it in Vault and uses the same payload shape as a Database Webhook.
- Since the request is queued inside the inserting transaction and sent only after commit, a rolled-back insert sends nothing, and the worker can safely read the row by id when the call arrives.
- With the webhook default timeout of 1000 ms (and pg_net's 2000/5000 ms), any long backtest launched from a trigger will be logged as timed out unless the timeout is raised or the endpoint acknowledges fast (see section 2).
- Delivery is at-most-once from pg_net's side (no retry, unlogged queue), so pair the trigger with a cron "sweeper" that re-dispatches `jobs` rows still in `pending` state; this makes the trigger a latency optimisation rather than the only delivery path.

### Gaps
- The hosted platform's exact `supabase_functions.http_request` definition was not inspected (only the self-hosting SQL in the public repo). Verify with `select pg_get_functiondef('supabase_functions.http_request'::regproc);` in the project.
- Whether the `supabase_functions` schema exists before the first webhook is created in the Dashboard on a brand-new project was not confirmed.

---

## 5. Cron expressions for Indian market hours (09:15-15:30 IST = 03:45-10:00 UTC, Mon-Fri)

### Takeaway
One 5-field cron line cannot express 03:45-10:00 UTC exactly; either use three jobs for an exact window or one broader job (`*/5 3-10 * * 1-5`) with the time check done in SQL or in the endpoint. IST has no daylight saving and the whole session falls on the same UTC calendar day, so `1-5` in UTC is the same Monday-Friday as in IST.

### Cited Findings
- Day of week is `0 - 6` with "0 to 6 are Sunday to Saturday, or use names; 7 is also Sunday"; README example `0 0 * * 1-5   # 12AM every weekday`. — [pg_cron README](https://github.com/citusdata/pg_cron), [Cron quickstart](https://supabase.com/docs/guides/cron/quickstart)
- pg_cron's parser "comes directly from the cron source code by Paul Vixie, hence the same options are supported" (ranges, lists, steps). — [pg_cron README](https://github.com/citusdata/pg_cron)
- Schedules are evaluated in GMT by default (`cron.timezone` default `GMT`). — [pg_cron README](https://github.com/citusdata/pg_cron)
- Reusing a job name overwrites the job, so each schedule needs its own name. — [Cron quickstart](https://supabase.com/docs/guides/cron/quickstart)

### Inferences
All SQL in this subsection is **ADAPTED / my own construction, not executed**.

Exact window, every 5 minutes, three jobs (fires 03:45, 03:50, 03:55, then 04:00-09:55, then 10:00 UTC):
```sql
-- ADAPTED: replace <DISPATCH_SQL> with the net.http_post statement from section 3
select cron.schedule('market-tick-open',  '45-59/5 3 * * 1-5', $$ <DISPATCH_SQL> $$);  -- 03:45, 03:50, 03:55 UTC
select cron.schedule('market-tick-mid',   '*/5 4-9 * * 1-5',   $$ <DISPATCH_SQL> $$);  -- 04:00 ... 09:55 UTC
select cron.schedule('market-tick-close', '0 10 * * 1-5',      $$ <DISPATCH_SQL> $$);  -- 10:00 UTC = 15:30 IST
```

Simpler: one job over 03:00-10:55 UTC with the window enforced in SQL so no request is sent outside market hours (a `select ... where` with no `from` is valid Postgres):
```sql
-- ADAPTED
select
  cron.schedule(
    'market-tick',
    '*/5 3-10 * * 1-5',
    $$
    select
      net.http_post(
          url := (select decrypted_secret from vault.decrypted_secrets where name = 'worker_url') || '/api/tick',
          headers := jsonb_build_object(
            'Content-Type', 'application/json',
            'Authorization', 'Bearer ' || (select decrypted_secret from vault.decrypted_secrets where name = 'worker_token')
          ),
          body := jsonb_build_object('source', 'pg_cron', 'scheduled_at', now()),
          timeout_milliseconds := 10000
      ) as request_id
    where (now() at time zone 'Asia/Kolkata')::time between time '09:15' and time '15:30';
    $$
  );
```

- Simplest: schedule `*/5 3-10 * * 1-5` unconditionally and let the Vercel endpoint decide (it has to check NSE trading holidays anyway, which no cron expression can encode). That costs about 15 wasted calls per day (03:00-03:40 and 10:05-10:55 UTC).
- Call volume: 03:45-10:00 UTC at 5-minute spacing is 76 calls per trading day; the broad variant is 96 per day. Both are trivial against pg_net's 200 requests/second design limit.
- A request scheduled for 10:00:00 UTC is exactly 15:30 IST; if a post-close run is wanted (e.g. 15:35 IST), add `5 10 * * 1-5`.

### Gaps
- None of the adapted expressions was run on a live Supabase project; verify with `select jobname, schedule from cron.job;` and by watching `cron.job_run_details` for one session.

---

## 6. Free-plan project pausing (7-day inactivity, what counts, restore window, emails, project count)

### Takeaway
Yes, as of November 2026 Free-plan projects are still paused after about a week of low activity, and the official definition is "sufficient user database activity" (user queries/requests), with a warning email about a week before. Supabase does not say officially whether pg_cron jobs running inside the database count; community evidence is mixed and non-authoritative, so the safe design is for the external worker to make real database requests through the API every trading day.

### Cited Findings
- "Supabase pauses Free Plan projects that show low activity over a 7-day period to save server resources." — [Project Pausing](https://supabase.com/docs/guides/platform/free-project-pausing)
- "A Free plan project is considered inactive if it does not receive sufficient user database activity over the past week. Projects with too few user queries during that window are the clearest candidates for pausing. While you may be actively using the project, it's possible that usage is not enough to exclude it from automatic pausing. Typically a few user requests to the database each day over the previous week is enough to keep the project from being paused." — [Project Pausing](https://supabase.com/docs/guides/platform/free-project-pausing)
- Emails: "Supabase sends two emails to the project owner regarding project pausing: 1. A warning email roughly one week before the pause takes effect. 2. A confirmation email once the project has been paused." — [Project Pausing](https://supabase.com/docs/guides/platform/free-project-pausing)
- After the warning, pausing can be prevented by: "Visit the project from the Supabase Dashboard to generate activity" or "Generate a sufficient amount of activity by making API calls to your project or sending requests via your connected application." — [Project Pausing](https://supabase.com/docs/guides/platform/free-project-pausing)
- FAQ: "Only on the Free plan. If a Free project gets too little database activity over a week, Supabase pauses it." "Opening the project in the dashboard or sending real requests from your app both count as activity. A few requests a day is usually enough to keep a project running, though that isn't a guarantee." "A paused project keeps all of its data and settings." — [Supabase KB FAQ: Do Supabase projects pause when they're inactive?](https://supabase.com/kb/faqs/platform/free-project-pausing)
- Pricing page wording: "Free projects are paused after 1 week of inactivity." (as extracted by the fetch tool on 2026-11-11) — [Supabase pricing](https://supabase.com/pricing)
- Production checklist: "We may pause applications on the Free Plan that exhibit low activity in a 7-day period to save on server resources." "Upgrade to Pro to guarantee that we won't pause your project for inactivity." — [Production checklist](https://supabase.com/docs/guides/deployment/going-into-prod)
- "Paid projects cannot be paused and are not subject to pausing for inactivity." — [Project Pausing](https://supabase.com/docs/guides/platform/free-project-pausing)
- **Restore window (CONFLICT with older figure):** the current official page says "You can restore a paused project for up to 1 year after it was paused" and "there is a 1-year window to restore the project on the platform from within Supabase Studio"; the upgrading guide says the same ("users have a 1-year window to restore the project"), although its screenshot is still captioned "Project Paused: 90 Days Remaining". — [Project Pausing](https://supabase.com/docs/guides/platform/free-project-pausing), [Upgrading](https://supabase.com/docs/guides/platform/upgrading). The 90-day figure in the assignment and in many third-party posts appears to be the older policy; a search-engine summary on 2026-11-11 still attributed "90 days" to the official doc, so the change is recent or cached copies persist.
- After the restore window: "you can download your project's backup file, and Storage objects from the project dashboard" and restore to a new project or locally. — [Upgrading](https://supabase.com/docs/guides/platform/upgrading)
- Number of free projects: "You are granted two free projects. The project limit applies across all organizations where you are an Owner or Administrator. ... Paused projects do not count towards your free project limit." — [About billing on Supabase](https://supabase.com/docs/guides/platform/billing-on-supabase)
- Side effects of pause/restore: "Free projects will move to the latest minor version when their paused project is restored." — [Upgrading](https://supabase.com/docs/guides/platform/upgrading). Vault secrets stay readable across pause/restore. — [Vault docs](https://supabase.com/docs/guides/database/vault). Projects restored from 1 November 2025 onward do not get legacy `anon`/`service_role` keys back. — [API keys announcement, GitHub discussion #29260](https://github.com/orgs/supabase/discussions/29260)

**Community statements on what counts (none is from Supabase staff; treat as anecdote)** — all from [GitHub discussion #13121](https://github.com/orgs/supabase/discussions/13121):
- GaryAustin1 ("Collaborator" badge, a community contributor, not staff), 2023-03-23, opinion on in-database jobs: "It can't just be something running in the database as there are all kinds of Postgres things running in the background."
- Original poster ricemountainer, 2023-03-30: got the inactivity alert despite an external job connecting daily; concluded that just connecting "does not meet the requirements". 2025-06-28: reports a daily application transaction (INSERT/UPDATE/DELETE) has kept the project from being paused since March 2024; "just establishing a connection is not sufficient."
- Rubenburdin (no badge; the reply promotes a commercial product), 2026-02-20: claims detection "looks at actual database activity (queries, transactions) not just connections" and that pg_cron inside Supabase "also counts as database activity". Unverified.
- Third-party blogs disagree with each other (some say database activity, some say incoming API requests); community keep-alive tools generally ping the REST API from outside (e.g. GitHub Actions or an external cron). — [travisvn/supabase-pause-prevention](https://github.com/travisvn/supabase-pause-prevention), [runhooks.app blog](https://runhooks.app/blog/preventing-supabase-free-tier-pausing/)

### Inferences
- The official wording ("user database activity", "user queries", "user requests to the database", "API calls to your project") points at externally originated requests. pg_cron-only activity is not confirmed to count and one experienced community member argues it cannot. Do not rely on pg_cron alone to keep the project alive.
- In the proposed design the Vercel worker is called 76+ times per trading day and will read/write Supabase through the Data API on each call, which is well above "a few user requests to the database each day". The risk window is market closures: the 7-day look-back spans a weekend plus holidays, so a long holiday stretch with no worker traffic could reduce activity. A weekend/holiday keep-alive that makes a real query from outside (the worker itself on a daily schedule, or a GitHub Actions job) removes that risk.
- While paused, the database is offline, so pg_cron jobs and triggers do not run at all, and nothing inside Supabase can un-pause it; the warning email (about a week ahead) is the only signal.

### Gaps
- No Supabase staff statement or official doc was found that says whether pg_cron/pg_net activity counts toward the inactivity check. This remains genuinely unknown as of 2026-11-11.
- The exact threshold ("sufficient", "a few requests a day ... isn't a guarantee") is deliberately unspecified by Supabase.
- I could not date the change from a 90-day to a 1-year restore window.
- Reddit/Discord threads were not retrieved directly; only GitHub discussions, the official docs and blog posts surfaced by search.

---

## 7. Free-plan quotas relevant to this design

### Takeaway
The headline Free numbers are unchanged: 500 MB database per project, 5 GB egress plus a separate 5 GB cached-egress quota, 500,000 Edge Function invocations, 2 active projects, shared CPU with 0.5 GB RAM (Nano), 1-day log retention and no downloadable backups or PITR. Quotas are per organization, not per project, except database size.

### Cited Findings
- Quota table (Free column): Egress 5 GB; Database Size 500 MB per project; Monthly Active Users 50,000; Storage Size 1 GB; Edge Function Invocations 500,000; Realtime Message Count 2 million; Realtime Peak Connections 200. — [About billing on Supabase](https://supabase.com/docs/guides/platform/billing-on-supabase)
- "The quota is applied to your entire organization, independent of how many projects you launch within that organization." — [About billing on Supabase](https://supabase.com/docs/guides/platform/billing-on-supabase)
- Egress: "Cached and uncached egress have independent quotas and independent pricing." Free plan quota "5 GB / 5 GB" (uncached / cached), no over-usage pricing on Free. — [Manage Egress usage](https://supabase.com/docs/guides/platform/manage-your-usage/egress)
- Pricing page Free plan (as extracted by the fetch tool, 2026-11-11): 500 MB database per project; 5 GB egress; 5 GB cached egress; 50,000 MAU; 1 GB file storage; 50 MB max upload; 500,000 Edge Function invocations per month; shared CPU with 500 MB RAM; up to 2 active projects; log retention 1 day; no automatic backups; no PITR, branching, log drains, custom domains; community support only. — [Supabase pricing](https://supabase.com/pricing)
- Compute: "Nano (free plan) and Micro (paid plans)"; Nano = $0, Shared CPU, "Up to 0.5 GB" memory, 500 MB database size; footnote "Compute resources on the Free plan are subject to change." — [Compute and Disk](https://supabase.com/docs/guides/platform/compute-and-disk)
- Connections on Nano (free): Database Max Connections 60; Connection Pooler Max Clients 200; Default Pool Size 15; Max Replication Slots 5; Max WAL Senders 5. — [Compute and Disk](https://supabase.com/docs/guides/platform/compute-and-disk)
- Backups: "Database backups are not available for download for Free Plan projects." — [Production checklist](https://supabase.com/docs/guides/deployment/going-into-prod). Daily backups are described for Pro (7 days), Team (14 days), Enterprise (up to 30 days); free projects are advised to export their own data with the CLI. — [Database Backups](https://supabase.com/docs/guides/platform/backups)
- Edge Function invocations are counted "regardless of the response status code. Preflight (OPTIONS) requests are not billed." — [Manage Edge Function Invocations usage](https://supabase.com/docs/guides/platform/manage-your-usage/edge-function-invocations)
- IPv4 add-on is "Pro Plan and above"; the shared pooler (Supavisor) connection strings are IPv4-compatible; direct connections are IPv6 by default, and Vercel is listed among platforms that only accept IPv4 connections. — [Dedicated IPv4 Address for Ingress](https://supabase.com/docs/guides/platform/ipv4-address)

### Inferences
- Calls made by pg_net go straight to Vercel and do not consume the Edge Function invocation quota; only calls to `/functions/v1/...` do.
- A Vercel function connecting to Postgres directly must use the shared pooler (IPv4) string, or avoid Postgres connections entirely by using the Data API (PostgREST) over HTTPS; with 60 direct connections and a pool size of 15, the HTTPS Data API is the safer choice for bursty serverless workers.
- At 96 calls/day the request and cron-history volume is negligible against 500 MB, provided `cron.job_run_details` is pruned; `net._http_response` self-expires after 6 hours.

### Gaps
- The pricing page was read through a summarizing fetch tool, not copied verbatim; numbers that also appear in the docs tables (above) are the firmer citations. Log retention (1 day) and "no automatic backups" on Free come only from that pricing-page extraction.
- What happens on exceeding a Free quota (grace period, restrictions) was not researched in this pass.

---

## 8. Edge Functions limits and capabilities (late 2026)

### Takeaway
Edge Functions run on a Deno-based runtime with 256 MB memory, 2 s CPU time per request, a 150 s wall-clock limit on Free (400 s paid), a 150 s request idle timeout, a 20 MB bundle limit and 100 functions per project on Free. They can be pinned to `ap-south-1` (Mumbai) with the `x-region` header or `forceFunctionRegion` query parameter, can be invoked directly from Supabase Cron, and have no static egress IPs.

### Cited Findings
Runtime limits, verbatim — [Edge Functions limits](https://supabase.com/docs/guides/functions/limits):
- "Maximum Memory: 256MB"
- "Maximum Duration (Wall clock limit): This is the duration an Edge Function worker will stay active. During this period, a worker can serve multiple requests or process background tasks. Free plan: 150s; Paid plans: 400s"
- "Maximum CPU Time: 2s (Amount of actual time spent on the CPU per request - does not include async I/O.)"
- "Request idle timeout: 150s (If an Edge Function doesn't send a response before the timeout, 504 Gateway Timeout will be returned)"

Platform limits, verbatim — [Edge Functions limits](https://supabase.com/docs/guides/functions/limits):
- "Maximum Function Size: 20MB (bundled locally via the CLI) or 5MB (bundled server-side, e.g. via the Management API or Dashboard)"
- "Maximum no. of Functions per project: Free: 100; Pro: 1000; Team: 2000; Enterprise: Unlimited"
- "Maximum log message length: 10,000 characters"; "Log event threshold: 100 events per 10 seconds"
- "Recursive/Nested Function Calling: 30 requests per trace, within a 60-second window"
- Secrets: max 100 per project; names up to 256 characters; max secret size 48 KiB; names must not start with `SUPABASE_`.
- Other restrictions: "Outgoing connections to ports `25` and `587` are not allowed."; "Web Worker API (or Node `vm` API) are not available."; "Node Libraries that require multithreading are not supported."; HTML is only served with custom domains.

Background work: "You can use `EdgeRuntime.waitUntil(promise)` to explicitly mark background tasks. The Function instance continues to run until the promise provided to `waitUntil` completes." "The maximum duration is capped based on the wall-clock, CPU, and memory limits." — [Background Tasks](https://supabase.com/docs/guides/functions/background-tasks)

Regional invocation — [Regional Invocations](https://supabase.com/docs/guides/functions/regional-invocation):
- "Edge Functions automatically execute in the region closest to the user making the request."
- Supported regions include "`ap-south-1` (Mumbai)" (also `ap-southeast-1` Singapore, `ap-northeast-1` Tokyo, etc.).
- "You can specify the region programmatically using the Supabase Client library, or using the `x-region` HTTP header." "In case you cannot add the `x-region` header to the request (e.g.: CORS requests, Webhooks), you can use `forceFunctionRegion` query parameter."
- "You can verify the execution region by looking at the `x-sb-edge-region` HTTP header in the response."
- "When you explicitly specify a region via the `x-region` header, requests will NOT be automatically re-routed to another region."

Cron -> Edge Function: the Cron job form lets you "select a Database function, HTTP request, or Supabase Edge Function" — [Cron quickstart](https://supabase.com/docs/guides/cron/quickstart); "Every Job can ... make an HTTP request, such as invoking a Supabase Edge Function" — [Supabase Cron overview](https://supabase.com/docs/guides/cron). SQL examples are in section 1.

Auth for cron/pg_net callers: "Cron jobs, workers, `pg_net`, and other Edge Functions make calls with a secret key on the `apikey` header rather than a user JWT." Set `verify_jwt = false` for the function and use `withSupabase({ auth: 'secret' }, ...)` from `npm:@supabase/server@1`. — [Securing Edge Functions](https://supabase.com/docs/guides/functions/auth)

Static egress: "Due to their serverless and globally distributed nature, Supabase Edge Functions do not originate from a single static IP address or a small, stable range of IPs." The article describes Edge Functions as "powered by Deno Deploy" and as offering "the Deno developer experience". — [Why Supabase Edge Functions cannot provide static egress IPs](https://supabase.com/docs/guides/troubleshooting/why-supabase-edge-functions-cannot-provide-static-egress-ips-for-whitelisting-3d78b0)

### Inferences
- The 2 s CPU limit and 256 MB memory make Edge Functions unsuitable for a pandas-style backtest; they are suitable as a thin dispatcher only. The CPU limit counts CPU time, not waiting on I/O, so an Edge Function could wait on a slow upstream within the 150 s wall-clock/idle limits.
- An Edge Function can be pinned to Mumbai from a pg_net call by adding `'x-region', 'ap-south-1'` to the headers object or `?forceFunctionRegion=ap-south-1` to the URL (adaptation of the documented cURL example; not tested from pg_net).
- Pinning the region does not give a fixed IP, so it does not help with broker IP allow-lists.

### Gaps
- "TypeScript/JavaScript only, no Python" is not stated as such on the pages fetched; the docs describe a Deno-based runtime and all examples are TypeScript. Treat "no Python runtime" as well-established but not quoted here.
- Whether the Free-plan 150 s wall-clock applies to background tasks after the response is sent in exactly the same way was not checked beyond the sentence quoted above.

---

## 9. API keys: `sb_publishable_...` / `sb_secret_...` vs legacy `anon` / `service_role`

### Takeaway
Legacy JWT `anon`/`service_role` keys are being deprecated "by the end of 2026"; new projects (and projects restored after 1 November 2025) only have `sb_publishable_...` and `sb_secret_...` keys. New keys are not JWTs and must be sent on the `apikey` header, not as `Authorization: Bearer`, which matters directly for pg_net and Database Webhook calls.

### Cited Findings
- "Supabase is deprecating the `anon` and `service_role` keys by the end of 2026. Use the publishable (`sb_publishable_xxx`) and secret (`sb_secret_xxx`) keys instead." — [API keys docs (deprecation notice)](https://supabase.com/docs/guides/getting-started/api-keys)
- Timeline from the announcement: June 2025 early preview (opt-in on existing projects); July 2025 full feature launch; November 2025 monthly migration reminders begin, new projects no longer get `anon`/`service_role`, and projects restored from 1 November 2025 no longer get legacy keys; "Late 2026 (TBC)" legacy keys deleted and removed from docs and dashboard, and apps still using them will break. — [GitHub discussion #29260](https://github.com/orgs/supabase/discussions/29260)
- Key types: publishable `sb_publishable_...` (low privilege, safe to expose), secret `sb_secret_...` (elevated, backend only, maps to the `service_role` Postgres role with `BYPASSRLS`), `anon` = "Legacy version of publishable keys", `service_role` = "Legacy version of secret keys". "Publishable and secret keys are short strings, not JWTs. If a tool, tutorial, or AI assistant tells you to copy a long key that begins with `eyJ`, it was written for the legacy keys." — [API keys docs](https://supabase.com/docs/guides/getting-started/api-keys)
- Coexistence: "Creating publishable and secret keys doesn't revoke your legacy keys. Both key systems work at the same time." Legacy keys "stay valid until you disable them in the Settings > API Keys section of the Dashboard". — [API keys docs](https://supabase.com/docs/guides/getting-started/api-keys)
- Header rule: "Send publishable and secret keys on the `apikey` header, not on `Authorization: Bearer`. Because the keys aren't JWTs, anything that tries to verify one as a JWT fails. For migration compatibility the `verify_jwt` platform check accepts them on either header, but passing that check doesn't authenticate the caller." — [API keys docs, Known limitations](https://supabase.com/docs/guides/getting-started/api-keys)
- "Send publishable and secret keys on the `apikey` header only. If you also pass the key on the `Authorization: Bearer` header, which many Supabase clients do by default, the platform tries to parse it as a JWT and rejects the request with `Invalid JWT`." (stated in the Edge Functions migration step) — [Migrating to new API keys](https://supabase.com/docs/guides/getting-started/migrating-to-new-api-keys)
- Announcement nuance: the `Authorization` header should carry a user JWT or be left empty; a value that exactly matches the `apikey` value is tolerated for backward compatibility. — [GitHub discussion #29260](https://github.com/orgs/supabase/discussions/29260)
- Secret keys are blocked in browsers: "Supabase matches on the `User-Agent` header and returns HTTP 401 Unauthorized." — [API keys docs](https://supabase.com/docs/guides/getting-started/api-keys)
- pg_net / webhooks migration, official (verbatim) — [Migrating to new API keys](https://supabase.com/docs/guides/getting-started/migrating-to-new-api-keys): "Calls made from Postgres with `pg_net`, including Database Webhooks, usually send the `service_role` key on the `Authorization: Bearer` header. The new secret keys aren't JWTs, so they're rejected there. Send the secret key on the `apikey` header instead."
```sql
-- before
select net.http_post(
  url := 'https://your-project.supabase.co/functions/v1/your-function',
  headers := jsonb_build_object(
    'Content-Type', 'application/json',
    'Authorization', 'Bearer <service_role key>'
  ),
  body := jsonb_build_object('event', 'ping')
);

-- after
select net.http_post(
  url := 'https://your-project.supabase.co/functions/v1/your-function',
  headers := jsonb_build_object(
    'Content-Type', 'application/json',
    'apikey', 'sb_secret_...'
  ),
  body := jsonb_build_object('event', 'ping')
);
```
- Inside Edge Functions, `SUPABASE_SECRET_KEYS` is injected as a JSON dictionary keyed by key name; `SUPABASE_ANON_KEY`/`SUPABASE_SERVICE_ROLE_KEY` "still exist in the runtime, but they carry the legacy keys". — [API keys docs](https://supabase.com/docs/guides/getting-started/api-keys)
- Server-side usage from a backend such as Vercel: `createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_SECRET_KEY!)`. — [API keys docs](https://supabase.com/docs/guides/getting-started/api-keys)

### Inferences
- A project created in November 2026 will have only `sb_publishable_`/`sb_secret_` keys; any tutorial that passes a `service_role` JWT as `Authorization: Bearer` (the pre-2025 pattern for pg_cron -> Edge Function) will not work as written.
- For raw REST calls from the Vercel worker to PostgREST, send the secret key in `apikey` and do not duplicate it into `Authorization` unless it is byte-identical to the `apikey` value (tolerated for compatibility per the announcement); the supabase-js client handles this.
- The Vercel endpoint's own shared token is unrelated to Supabase keys, so the `Authorization: Bearer <worker_token>` header in the adapted SQL is fine for a non-Supabase target.

### Gaps
- The exact removal date for legacy keys is still stated only as "by the end of 2026" / "Late 2026 (TBC)"; no confirmed day was found, and I did not find a November 2026 changelog entry confirming whether removal has already happened.
- The docs URL for the API keys page: the source file lives at `guides/getting-started/api-keys`; the older `/docs/guides/api/api-keys` path may redirect (not checked).

---

## 10. Network: static egress IPs for pg_net / Edge Functions

### Takeaway
Supabase offers no static outbound IP for either the database (pg_net) or Edge Functions; the paid dedicated IPv4 add-on is for ingress to the database only. A broker's IP allow-list therefore cannot be satisfied from Supabase directly.

### Cited Findings
- The add-on page is titled "Dedicated IPv4 Address for Ingress" and states: "IPv4 addresses are guaranteed to be static for ingress traffic. If your database is making outbound connections, the outbound IP address is not static and cannot be guaranteed." — [Dedicated IPv4 Address for Ingress](https://supabase.com/docs/guides/platform/ipv4-address)
- The add-on is "Pro Plan and above"; "actions like pausing/unpausing the project or enabling/disabling the add-on can lead to a new IPv4 address." — [Dedicated IPv4 Address for Ingress](https://supabase.com/docs/guides/platform/ipv4-address)
- "Because Supabase Edge Functions lack static or stable egress IP addresses, standard outbound calls from an Edge Function to a service that requires IP whitelisting ... will likely be blocked." Recommended: "Solution 1: Use an Outbound Proxy (Recommended)" (a small VM with a fixed egress IP), "Solution 2: Header-Based Authentication (Best for Servers You Control)", "Solution 3: Self-Hosting the Edge Runtime". — [Why Supabase Edge Functions cannot provide static egress IPs](https://supabase.com/docs/guides/troubleshooting/why-supabase-edge-functions-cannot-provide-static-egress-ips-for-whitelisting-3d78b0)

### Inferences
- pg_net requests originate from the database host, whose outbound IP "is not static and cannot be guaranteed"; this is fine for calling a Vercel endpoint authenticated by a header token (Supabase's own "Solution 2" pattern), but broker API calls that need a whitelisted IP must be made from somewhere with a fixed egress IP, not from Supabase.
- Supabase's role in this architecture is therefore scheduler/queue/state store only; the IP-whitelisted hop has to live elsewhere.

### Gaps
- pg_net has no documented proxy setting on the pages reviewed; I did not find any official way to route pg_net through an outbound proxy.

---

## 11. Reliability notes (missed runs, restarts, pausing, idempotency)

### Takeaway
Neither pg_cron nor pg_net gives delivery guarantees: jobs do not run while the database is down or paused, pg_net's queue is unlogged and has no retries, and overlapping runs of the same job are queued rather than run in parallel. The target endpoint should be idempotent and the system should carry its own state so a later tick can repair a missed one.

### Cited Findings
- pg_net "requests and responses are stored in unlogged tables, which are not preserved during a crash or unclean shutdown." — [pg_net docs](https://supabase.com/docs/guides/database/extensions/pg_net)
- pg_net has no built-in retry; the README shows a hand-built tracking table and wrapper to retry failed requests. — [pg_net README](https://github.com/supabase/pg_net)
- "pg_cron can run multiple jobs in parallel, but only one instance of each specific job at a time. If a second instance is triggered before the first finishes, it's queued and starts as soon as the first one completes." — [pg_cron README](https://github.com/citusdata/pg_cron)
- The README's sample `cron.job_run_details` output shows a run with status `failed` and return message `server restarted`, i.e. a run in flight during a restart is recorded as failed. — [pg_cron README](https://github.com/citusdata/pg_cron)
- "pg_cron does not run any jobs as a long a server is in hot standby mode, but it automatically starts when the server is promoted." — [pg_cron README](https://github.com/citusdata/pg_cron)
- The pg_cron scheduler worker can die; before Postgres v15.6.1.122 (pg_cron v1.6.4) there is no auto-revive and a fast reboot is needed. Other listed failure causes: too many concurrent jobs exhausting connections, and database resource strain (CPU, memory, disk IO). — [pg_cron debugging guide](https://supabase.com/docs/guides/troubleshooting/pgcron-debugging-guide-n1KTaz)
- The pg_net worker can also fail; check `pg_stat_activity` and call `net.worker_restart()`. Requests can time out en masse under load. — [Webhook debugging guide](https://supabase.com/docs/guides/troubleshooting/webhook-debugging-guide-M8sk47)
- Free-plan compute is shared CPU with up to 0.5 GB RAM and "subject to change"; Free projects can be paused and are moved to the latest minor Postgres version when restored. — [Compute and Disk](https://supabase.com/docs/guides/platform/compute-and-disk), [Upgrading](https://supabase.com/docs/guides/platform/upgrading)
- Pro-plan guarantee wording: "Upgrade to Pro to guarantee that we won't pause your project for inactivity." — [Production checklist](https://supabase.com/docs/guides/deployment/going-into-prod)
- Supabase cautions against maintenance jobs such as scheduled `pg_terminate_backend(pid)`, which "can disrupt critical background processes". — [Cron quickstart](https://supabase.com/docs/guides/cron/quickstart)

### Inferences
- pg_cron evaluates schedules as time passes; a tick that falls while Postgres is restarting, being upgraded, or paused is simply not run, and there is no documented catch-up/backfill mechanism. Design each tick so the next one can do the missed work (e.g. the endpoint computes "what should be done as of now" from stored state rather than "do one increment").
- Duplicate delivery is also possible in practice (manual re-dispatch, a sweeper job plus a trigger both firing for the same `jobs` row, or a request recorded as timed out that actually ran). Make the worker idempotent: claim the job with a conditional update such as `update jobs set status = 'running' where id = $1 and status = 'pending' returning id` and exit if no row is returned (pattern is my recommendation, not from Supabase docs).
- Monitoring should combine three sources: `cron.job_run_details` (did the tick fire), `net._http_response` (did the HTTP call return within the timeout; only 6 hours of history), and an application-level heartbeat row written by the worker (did the work complete). With 1-day log retention on Free, the heartbeat table is the only durable record.
- For a trading workflow, a Free project that may pause, has no downloadable backups, and sends from a non-static IP is acceptable as a best-effort scheduler but should not be the only safeguard for time-critical order placement.

### Gaps
- No official Supabase or pg_cron statement was found that says in so many words "missed runs are not caught up"; this is inferred from the scheduler design and the absence of any backfill feature in the README and docs.
- No published uptime/SLA figures for Free-plan projects or for the frequency of maintenance restarts were found in this pass.
- No measured data on pg_cron timing jitter on Nano compute (how late after the minute boundary a job fires) was found.
