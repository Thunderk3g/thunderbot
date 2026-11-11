# What was built in this repository and how it was checked (11 November 2026)

First-hand notes from the engineer who implemented the no-server design in the `thunderbot` repository
alongside this research. Everything below was run on a development machine on 11 Nov 2026. Nothing was
deployed to a real Vercel or Supabase project, because no credentials for either were available; items that
could only be confirmed on a real deployment are listed at the end.

## The design that was implemented

```
Supabase (free plan)                               Vercel (Hobby plan, region bom1)
  Postgres: journal, control, jobs, daily_runs  <--  Next.js dashboard (app/api/* route handlers)
  pg_cron: every 5 min, 09:15-15:35 IST       --->  /api/worker  (Python function, dashboard/api/worker.py)
           + 17:00 IST, + weekends, + watchdog        imports the `thunderbot` package from ../worker
  pg_net:  GET /api/worker, Bearer secret            one pass, then exits; all state is in Supabase
  Vault:   worker URL + cron secret                 Vercel Schedules `*/15 9-15 * * 1-5` Asia/Kolkata (beta)
                                                     + legacy Vercel Cron `40 9 * * 1-5` as a stand-in
```

- **One Python function, `dashboard/api/worker.py`, served at `/api/worker`.** `GET` or `POST` with
  `op=tick` (default) runs one pass of the daily investing worker; `POST ?op=job&id=...` runs a queued
  backtest; `op=health` checks configuration. Limit `maxDuration: 300`, region `bom1`, set in
  `dashboard/vercel.json`.
- **Dependencies:** `dashboard/pyproject.toml` declares `thunderbot[llm]` with a uv path source
  (`[tool.uv.sources] thunderbot = { path = "../worker" }`). The worker package needs only `requests`;
  daily prices come from Yahoo's v8 chart endpoint called directly (no pandas, numpy or yfinance).
- **Authentication:** the Next.js middleware (HTTP Basic Auth on every path) lets a request through to
  `/api/worker` when it carries `Authorization: Bearer $CRON_SECRET`; the Python function checks the
  bearer secret or the dashboard's Basic credentials again itself and returns 401 otherwise.
- **Scheduling:** a Supabase migration creates `public.thunderbot_wake()`, which reads the worker URL and
  secret from Vault and queues `net.http_get(... timeout_milliseconds := 290000)`, and five pg_cron jobs:
  `*/5 3-10 * * 1-5` gated in SQL to 09:15-15:35 IST, `30 11 * * 1-5` (17:00 IST catch-up),
  `30 6 * * 0,6` (weekends, so the project sees real API requests), a watchdog at 15:05 and 15:20 IST that
  posts to ntfy.sh if the heartbeat is more than 20 minutes old, and a nightly prune of
  `cron.job_run_details`.
- **Idempotency:** a `daily_runs` table with `unique (kind, day)`. The worker inserts a row before the daily
  decision; a duplicate insert returns HTTP 409 from PostgREST and that invocation does nothing. A run that
  fails releases the lock; one that died can be taken over after 15 minutes. Queued jobs are claimed with a
  conditional `PATCH ...?status=eq.queued` with `Prefer: return=representation`.
- **Timing rules in the worker:** the daily decision is due from 15:10 IST. A paper run that starts late
  (even after the close) still runs that evening on closing prices and is flagged as late. A live run that
  starts after 15:25 IST does not trade; it is marked missed, an alert is sent, and the decision is made
  afresh on the next trading day. Backtests show a one- or two-day delay costs these monthly rules little.
- **Guards before any trade:** a live price missing, a price history ending more than 7 days ago, or a live
  price more than 15% from the last close (the signature of an unadjusted unit split) postpones the
  rebalance and raises an alert. If the Nifty ETF has not traded today the day is treated as a holiday.
- **LLM role as implemented:** an optional reviewer (Claude, off by default) is shown the planned orders and
  the price facts behind them. It may approve or postpone the whole rebalance by one session, at most twice
  in a row; it cannot change, add or enlarge an order; a reviewer error approves. Every verdict is stored
  with its prompt in `llm_decisions`.
- **Live orders are not placed by the serverless function.** It runs paper trading and shows the exact
  orders; the user can copy them into the Groww app by hand. Live API orders stay on the long-running
  worker (`thunderbot invest --live`) or `thunderbot tick --live` on a machine whose public IP is the one
  registered with Groww, behind three explicit opt-ins.
- **Fallback runners that share the same state:** `thunderbot tick` (one pass, then exit) for Windows Task
  Scheduler, macOS launchd, Linux systemd timers or a GitHub Actions schedule.

## Checks that were actually run

1. **Vercel build, locally, with Vercel CLI 65.14.0** (`vercel build` from the repository root with a
   project file setting `rootDirectory: dashboard`, framework Next.js). Result: build completed
   successfully. The Next.js app built first; then the Python builder reported "Using Python 3.12 from
   dashboard/pyproject.toml", used uv 0.11.32, and produced `functions/api/worker.func` next to the
   Next.js route functions. A later build that added a `schedules` block (Vercel Schedules, beta) beside the
   legacy `crons` entry also succeeded, and both appear in the output `config.json`. The bundle's file map contains `_vendor/thunderbot/...` (including its data
   files) and `_vendor/requests/...`: 375 files in total. `config.json` carries the cron entry and a
   middleware route whose pattern matches every path, which confirms the middleware sits in front of
   `/api/worker`.
   - A first attempt with `requirements.txt` containing `../worker` FAILED: the builder resolved the
     relative path to `dashboard/worker` ("Distribution not found"). The `pyproject.toml` path source worked.
   - The builder writes `dashboard/uv.lock` and `dashboard/.python-version` during the build; both are
     git-ignored.
2. **The built function, run locally** on the virtual environment the Vercel builder created (Python
   3.12.3), against the repository's local PostgREST stand-in: no credentials returned 401; `op=health`
   returned 200; a tick before "Start" did nothing; a tick after "Start" bought the three-ETF mix on live
   Yahoo prices in 2.0 seconds; a second tick the same day did nothing; a queued 15-year backtest ran
   through `op=job`. A 15-year backtest of the trend rotation takes under one second of compute once prices
   are loaded; loading 5-8 symbols from Yahoo takes 1-3 seconds.
3. **Yahoo's chart endpoint from this cloud sandbox** (not a Vercel or AWS address): HTTP 200 with a browser
   User-Agent for every symbol tried, 17 years of daily bars per request. Symbols that returned almost no
   history: MID150BEES.NS, NIFTYIETF.NS (15 rows), SETFNIF50.NS and SETFGOLD.NS (76 rows, ended 4 Nov 2026).
4. **The SQL migrations, on PostgreSQL 16.15 locally**, with stand-in `cron`, `net` and `vault` schemas that
   copy the documented function signatures: all four migrations applied; `thunderbot_wake()` returned NULL
   with a notice when the Vault secrets were missing and otherwise queued
   `GET https://.../api/worker?op=tick&by=...` with the bearer header and a 290000 ms timeout; the
   market-hours gate was true at 09:15, 15:10 and 15:35 IST and false at 09:10 and 15:40; the watchdog
   alerted only with a topic set, trading enabled and a stale heartbeat; `daily_runs` rejected a second
   claim for the same day; the `anon` role cannot execute `thunderbot_wake`.
5. **Tests:** the worker's test suite passes (137 tests), including the run lock, late and missed runs, the
   bad-price guard, the reviewer's limits, tax by asset class and the serverless handler. The dashboard
   type-checks and builds.
6. **A bug found on the way:** the existing `jobs` table had `check (kind in ('backtest', 'sweep'))`, so the
   daily-strategy backtests (`kind = 'invest'`) could never have been queued on a real Supabase project.
   The new migration widens the check.

## Not verified (needs a real deployment)

- That Vercel's hosted builder resolves the `../worker` path source the way the local CLI did. It depends on
  the project setting "Include source files outside of the Root Directory in the Build Step" (on by
  default). If it fails, the fallback is to copy `worker/thunderbot` into `dashboard/` in the build command.
- That Yahoo answers requests from Vercel's Mumbai egress addresses at 15:10 IST without rate limiting.
- That pg_cron, pg_net and Vault behave on the hosted free plan exactly as their documentation says,
  including whether pg_net's request to a Vercel function that outlives a shorter timeout cancels it (the
  timeout was set to the function's full limit to avoid depending on that).
- That scheduled activity keeps a free Supabase project from pausing; the weekend tick is there to make
  real Data API requests every day, which is what the documentation asks for.
- Any live order on Groww. No broker credentials were used at any point.
