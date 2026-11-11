# Running Thunderbot with no server

Thunderbot's daily strategies make one decision a day, so nothing needs to stay running. A scheduler
wakes a function, the function does one pass and exits, and everything it knows lives in Supabase.

```
Supabase (free plan)                               Vercel (Hobby plan, Mumbai)
  Postgres: journal, control, jobs, daily_runs  <--  dashboard (Next.js)
  Cron: every 5 min, 09:15-15:35 IST  ---------->  /api/worker (Python function)
        17:00 IST catch-up, weekends, watchdog       one pass of `thunderbot`, then it exits
  Vault: worker URL + shared secret                Vercel Schedules: every 15 min in market hours
```

Two clocks wake the same function, and a lock in the database lets only one of them act on a given day.
Vercel's own scheduler works as soon as the project is deployed. Supabase's is more punctual (to the
minute, against a 15-minute window on Vercel's free plan) and adds the watchdog; connect it in step 3.

**What this setup does:** paper trading of the daily strategies on live Yahoo prices, backtests from the
Lab, alerts, and a list of the exact orders after each rebalance. **What it does not do:** place real
orders. See [What needs a static IP](#what-needs-a-static-ip).

The reasoning and sources behind each choice are in
[`reports/ETF rotation and serverless hosting.md`](../reports/ETF%20rotation%20and%20serverless%20hosting.md).

## Set it up (about 20 minutes)

### 1. Supabase

1. Create a project (the free plan is enough; pick the Mumbai region).
2. Apply the four files in `supabase/migrations/` in order: `supabase db push`, or paste each into the
   SQL editor. The last one enables `pg_cron` and `pg_net` and creates the schedules. They do nothing
   until step 3.
3. Note the project URL and a secret key (Settings > API keys: an `sb_secret_...` key, or the legacy
   `service_role` key).

### 2. Vercel

1. Import the repository as a project and set **Root Directory** to `dashboard`. Leave "Include source
   files outside of the Root Directory in the Build Step" on (the default): the Python function installs
   the worker package from `../worker`.
2. Set these environment variables for Production (none with a `NEXT_PUBLIC_` prefix):

   | Variable | Value |
   |---|---|
   | `SUPABASE_URL` | the project URL |
   | `SUPABASE_SERVICE_ROLE_KEY` | the secret key |
   | `DASHBOARD_USER`, `DASHBOARD_PASSWORD` | your dashboard login |
   | `CRON_SECRET` | a long random string, for example from `openssl rand -hex 32` |
   | `TB_CAPITAL` | paper capital in rupees, for example `500000` |

   Optional: `TB_INVEST_STRATEGY` (`core_mix` by default), `TB_LIQUID_SYMBOL` (`LIQUIDCASE`),
   `TB_SLAB_RATE_PCT` (`30`), `TB_NTFY_TOPIC` or `TB_TELEGRAM_TOKEN` + `TB_TELEGRAM_CHAT_ID` for alerts,
   and `TB_LLM_ENABLED=true` + `ANTHROPIC_API_KEY` for the rebalance reviewer.
3. Deploy. `dashboard/vercel.json` already pins the function to Mumbai (`bom1`), gives it 300 seconds, and
   registers two schedules: a 15-minute tick from 09:00 to 15:45 IST on weekdays (Vercel Schedules, a
   public beta since 4 November 2026) and the older once-a-day cron as a stand-in, set to fire in the hour
   after the close (15:30-16:29 IST) so that a missed day is at least made up on closing prices. If a deployment ever
   fails with an error about `schedules`, delete that block from `vercel.json`; Supabase's scheduler in
   step 3 then does the job by itself.
4. Open the site, log in, and press **Wake the worker** on Today. A heartbeat appears within a few seconds.

### 3. Connect the scheduler

In the Supabase SQL editor, once (these values never go in git):

```sql
select vault.create_secret('https://YOUR-APP.vercel.app', 'thunderbot_worker_url', 'Base URL of the dashboard deployment');
select vault.create_secret('THE-SAME-VALUE-AS-CRON_SECRET', 'thunderbot_cron_secret', 'Bearer token the worker function checks');
-- optional: a phone alert through https://ntfy.sh if the worker goes quiet in market hours
select vault.create_secret('a-long-topic-name-nobody-can-guess', 'thunderbot_ntfy_topic', 'ntfy.sh topic for alerts');
```

Then check the chain end to end:

```sql
select public.thunderbot_wake('manual');
select status_code, left(content, 200), error_msg, created from net._http_response order by created desc limit 3;
```

A `200` with `"ok": true` means Supabase reached the function. A `401` means the two secrets differ. A
timeout or DNS error means the URL is wrong.

### 4. Start

In the dashboard, test strategies in the **Lab**, press **Use this strategy** on the one you want, then
**Start paper investing**. The first check runs at the next 15:10 IST on a trading day (or press
**Check now**).

## How it behaves

- **Every five minutes in market hours** Supabase calls the function, and Vercel calls it about every
  fifteen. Most calls only write a heartbeat. At the first call from 15:10 IST the function makes the
  day's decision. On most days that is "not a rebalance day".
- **Only one run acts per day.** The function claims the day in the `daily_runs` table before it decides.
  A second scheduler calling at the same moment finds the day taken and stops.
- **A late paper run still runs.** If nothing called the function before the close, the 15:35 or 17:00 IST
  call (or Vercel's backup cron, or **Check now**) runs the decision on closing prices and labels it late.
- **Bad prices stop a rebalance.** A missing price, a history that ends more than a week ago, or a price
  more than 15% from the last close postpones the trade to the next session and logs the reason. An ETF
  unit split that the data feed has not adjusted looks exactly like that.
- **Backtests** run in the same function when you press Test in the Lab. A 15-year test takes a few seconds.
- **The watchdog** is a separate Supabase job. At 15:05 and 15:20 IST it checks the heartbeat and, if you
  stored an ntfy topic, alerts your phone when the worker has been silent for 20 minutes.

## Limits that shape this design

Figures as documented by Vercel and Supabase in November 2026; check them if something stops working.

| Limit | Hobby / free plan | Consequence |
|---|---|---|
| Vercel Schedules (beta) | every 15 minutes at most, each run landing somewhere in a 15-minute window; 5,000 runs a month | good enough to act between 15:10 and 15:30; Supabase Cron is the punctual clock |
| Vercel Cron (legacy) | once a day, firing anywhere within its named hour | a stand-in only: set to the hour after the close |
| Vercel function time | 300 seconds | a tick takes 1-3 seconds; a backtest a few seconds |
| Vercel Python bundle | 500 MB in the docs | the worker and its dependencies come to about 23 MB |
| Vercel runtime logs | kept 1 hour | the worker journals to Supabase instead |
| Vercel Hobby terms | non-commercial use only | fine for a personal bot; your call to make |
| Supabase pg_cron | once a minute at most, UTC | schedules are written in UTC and gated to IST in SQL |
| Supabase pg_net | asynchronous, no retries | the function is safe to call twice; nothing depends on a retry |
| Supabase free project | pauses after about a week without requests | the weekend tick makes real API requests every day |
| Outbound IP address | changes; none can be registered | no live broker orders from here |

## What needs a static IP

Since 1 April 2026 Indian brokers accept **API orders only from a static IP address registered to your
account** (one primary and one backup, changeable about once a week), and an address may be mapped to one
client only. That rules out this setup for live orders: Vercel's functions have no fixed address, its paid
static IPs (about $100 a month on top of Pro) are shared between customers, and Supabase offers no fixed
outbound address at all.

What stays possible here: signals, paper trading, backtests, alerts, and reading the orders off the Today
page to place them yourself in the Groww app. For the two recommended strategies that is a handful of
orders a year.

To place live orders automatically you need one machine with an address of your own:

| Option | Rough cost | Notes |
|---|---|---|
| Your laptop on home broadband with a static IP | roughly Rs 300-1,000 a month for the IP; quotes vary by provider | No server. Use `worker/deploy/laptop/`. The laptop must be awake at 15:10 IST. |
| A small Mumbai VPS | about $4-6 a month | Run `thunderbot invest --live` there (`worker/deploy/bootstrap.sh`). It is a server, but a tiny one. |
| Oracle Cloud's free VM | free | Comes with a public IP you can reserve (check the current terms); free instances can be reclaimed when idle. |

Either way the dashboard stays on Vercel and the state stays in Supabase. Live trading needs three explicit
opt-ins on that machine: `TB_LIVE_TRADING_ENABLED=true`, a `TB_EXPECTED_STATIC_IP` that matches its public
address, and the `--live --i-understand-the-risks` flags. Sending orders through a shared proxy service
instead is not advisable: the address would not be yours alone, which is what the rule requires.

## Other ways to wake the worker

All of these run the same code against the same Supabase state, so they can be combined; the run lock
keeps them from acting twice.

- **A laptop:** `thunderbot tick` from Task Scheduler, launchd or a systemd timer. Files and commands are
  in [`worker/deploy/laptop/`](../worker/deploy/laptop/README.md).
- **GitHub Actions:** `.github/workflows/tick.yml`, off until you set the repository variable
  `TB_ACTIONS_TICK=on`. GitHub starts scheduled runs late when busy, so it is a backup only.
- **Any HTTP scheduler** (cron-job.org, Upstash QStash, Cloud Scheduler): `GET https://YOUR-APP/api/worker`
  with the header `Authorization: Bearer <CRON_SECRET>`.

## If something is wrong

| Symptom | Likely cause |
|---|---|
| Today says "No worker yet" | The function has never run. Press **Wake the worker**; if that fails the message says why. |
| "Scheduler is silent" in the side rail | Supabase is not calling the function: Vault secrets missing or wrong, or the project is paused. Run the two check queries above. |
| `/api/worker` returns 404 | The Python function was not built. Check the deployment's build log for the Python step and the Root Directory setting. |
| `/api/worker` returns 500 "SUPABASE_URL ... must be set" | Environment variables are missing on Vercel for that environment. |
| A backtest fails with "Yahoo Finance returned no prices" | Yahoo refused the function's address or the symbol. Try again; if it persists, run backtests from your own machine with `thunderbot serve`. |
| "rebalance postponed, prices look wrong" in the Log | The bad-price guard fired. Compare the price shown with the NSE; if the feed is wrong the rule will try again next session. |
