# Deploy reference: Supabase and Vercel

For an agent (or person) with access to both accounts. Do the steps in this order: the Vault step
needs the Vercel URL, and the Vercel deploy needs the Supabase keys. Never commit a secret.
Longer explanation and a troubleshooting table: [`docs/no-server.md`](docs/no-server.md).

## 1. Supabase

1. **Project:** use the existing Thunderbot project, or create one in Mumbai (`ap-south-1`). Free plan is enough.
2. **Apply the six migrations, in filename order** (`supabase db push`, or run each file in the SQL editor):
   ```
   supabase/migrations/20261016000000_init.sql
   supabase/migrations/20261016120000_platform.sql
   supabase/migrations/20261111000000_serverless.sql     -- daily_runs lock; allows job kind 'invest'
   supabase/migrations/20261111000100_scheduler.sql      -- pg_cron + pg_net jobs, wake() and watchdog()
   supabase/migrations/20261112000000_ai_desk.sql        -- models table; allows job kind 'train'
   supabase/migrations/20261113000000_secrets.sql        -- encrypted keys from the Setup screen; job kind 'groww_check'
   ```
   If the last one fails on `create extension pg_cron`, enable **Cron** under Integrations first, then rerun it.
   Do not add RLS policies: every table has RLS on with no policies, and only the secret key may read or write.
3. **Collect two values** for Vercel (Settings > API keys): the project URL, and a secret key
   (`sb_secret_...`, or the legacy `service_role` key).
4. **After step 2.4 below gives you the URL**, store the scheduler's secrets in Vault (SQL editor, once):
   ```sql
   select vault.create_secret('https://<PRODUCTION-DOMAIN>', 'thunderbot_worker_url', 'Base URL of the dashboard deployment');
   select vault.create_secret('<SAME VALUE AS CRON_SECRET ON VERCEL>', 'thunderbot_cron_secret', 'Bearer token the worker function checks');
   -- optional phone alert if the worker goes quiet in market hours (https://ntfy.sh):
   select vault.create_secret('<a-long-unguessable-topic>', 'thunderbot_ntfy_topic', 'ntfy.sh topic for alerts');
   ```
   To change one later: `select vault.update_secret((select id from vault.secrets where name = 'thunderbot_worker_url'), '<new value>');`

## 2. Vercel

1. **Project:** repository `Thunderk3g/thunderbot`, production branch `main`, framework Next.js,
   **Root Directory `dashboard`**. Keep "Include source files outside of the Root Directory in the Build
   Step" **on** (the Python function installs the worker package from `../worker`). Keep Fluid compute on.
2. **Environment variables** (Production; none with a `NEXT_PUBLIC_` prefix):

   | Name | Value |
   |---|---|
   | `SUPABASE_URL` | the Supabase project URL |
   | `SUPABASE_SERVICE_ROLE_KEY` | the Supabase secret key |
   | `DASHBOARD_USER` | the owner's chosen login name |
   | `DASHBOARD_PASSWORD` | a strong password, chosen by the owner |
   | `CRON_SECRET` | a new random string, e.g. `openssl rand -hex 32` |
   | `TB_SECRET_KEY` | another new random string; encrypts the keys saved on the Setup screen. Use the same value on any other machine that runs the worker |
   | `TB_CAPITAL` | paper capital in rupees, e.g. `500000` |

   Optional: `TB_INVEST_STRATEGY` (default `core_mix`), `TB_LIQUID_SYMBOL` (`LIQUIDCASE`), `TB_SLAB_RATE_PCT` (`30`),
   `TB_NTFY_TOPIC` or `TB_TELEGRAM_TOKEN` + `TB_TELEGRAM_CHAT_ID` (alerts). The LLM key is entered by the owner on the
   dashboard's Setup screen after the deploy, not here (`TB_LLM_ENABLED=true` + `ANTHROPIC_API_KEY` still works as
   the environment route). **Do not set** `TB_LIVE_TRADING_ENABLED`, `GROWW_*` or `TB_EXPECTED_STATIC_IP` here: live
   orders cannot run from Vercel (no static IP).
3. **Deploy `main`.** Nothing else to configure: `dashboard/vercel.json` already sets region `bom1`, a 300-second
   limit for `api/worker.py`, a 15-minute weekday schedule (Vercel Schedules, beta) and a daily cron.
   - The build log must show a Python step ("Using Python 3.12 from dashboard/pyproject.toml").
   - If the deploy fails with an error about `schedules`, delete the `schedules` block from
     `dashboard/vercel.json` and redeploy; Supabase's scheduler then keeps time alone.
   - If it fails resolving `../worker`, the "outside the Root Directory" setting in step 1 is off.
4. **Note the production domain** and go back to Supabase step 1.4. The production domain must be reachable
   without Vercel login (Standard Protection is fine; do not put Vercel Authentication on production), or
   Supabase's calls will get a 401 from Vercel instead of reaching the app.

## 3. Check it works

```bash
# 401 without credentials, 200 with the secret:
curl -s -o /dev/null -w "%{http_code}\n" https://<DOMAIN>/api/worker
curl -s -H "Authorization: Bearer <CRON_SECRET>" "https://<DOMAIN>/api/worker?op=health"   # {"ok": true, "supabase": true, ...}
curl -s -H "Authorization: Bearer <CRON_SECRET>" "https://<DOMAIN>/api/worker?op=tick"     # {"ok": true, "did": "stopped", ...}
```

```sql
select public.thunderbot_wake('manual');                                   -- returns a request id
select status_code, left(content, 160), error_msg from net._http_response order by created desc limit 3;  -- expect 200
select jobname, schedule from cron.job order by jobname;                   -- five thunderbot-* jobs
select key from public.control order by key;                               -- includes heartbeat after the first tick
```

| Result | Meaning |
|---|---|
| `health` says `"supabase": false`, or `tick` returns 500 "SUPABASE_URL ... must be set" | Vercel env vars missing for Production |
| `tick` returns 500 mentioning a missing table or `daily_runs` | migrations not applied |
| `/api/worker` returns 404 | the Python function was not built (Root Directory or build setting) |
| `net._http_response` shows 401 | Vault's `thunderbot_cron_secret` differs from Vercel's `CRON_SECRET` |
| `net._http_response` shows a timeout or DNS error | Vault's `thunderbot_worker_url` is wrong |

## 4. Hand back to the owner

Open `https://<DOMAIN>`, log in with `DASHBOARD_USER` / `DASHBOARD_PASSWORD`, choose a plan under **Plans**,
then press **Start**. It paper-trades: the first check runs at the next 15:10 IST on a trading day. Tell the
owner the domain and where the login was stored; do not put either secret in the repository or in chat.
