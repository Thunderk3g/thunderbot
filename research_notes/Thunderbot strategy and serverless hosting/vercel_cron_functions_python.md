# Vercel cron, functions and Python runtime for the Thunderbot worker (status: 10 Nov 2026)

**Read this first: how these notes were sourced, and what that means for confidence.**

- `vercel.com` (and `nextjs.org`, `community.vercel.com`, `github.com`) could **not be fetched** from this research session: the session's network policy refused the connection. I therefore could not open any Vercel docs page, and could **not read the "last updated" date** on the pages. Two dates surfaced through the search tool's page metadata and are given where they apply; every other page date is a gap.
- Web search worked for 12 queries and then the shared search budget for the whole research run was exhausted. The search tool returns short summaries and snippets of the pages it found, not full pages. Findings marked **[search snippet]** are what the search tool reported an official Vercel page as saying. They are probably right but were not read in context by me. Wording inside quotation marks on those lines is the tool's quotation of the page.
- Findings marked **[source code]** were read directly and in full from Vercel's public GitHub repositories on `raw.githubusercontent.com` (`vercel/vercel` `main` branch, `vercel/next.js` `canary` and `v15.5.0`, `digitros/nextjs-fastapi`, `vercel/examples`), as they stood on 10 Nov 2026. These are primary and exact, but source code shows what the tooling accepts, not what each plan is allowed (plan limits are enforced server-side).
- Findings marked **[measured]** are measurements I ran in this session (installing the real wheels from PyPI).
- Anything I could only recall from pre-2026 knowledge of the docs is kept out of "Cited Findings" and listed under "Gaps" as *recalled, not re-verified*.
- To close the gaps, someone needs to open the listed doc URLs in a browser (or allow `vercel.com` in this environment's network settings).

**Repo facts used throughout (inspected locally, commit `da6bd27`):**

- No `vercel.json` exists anywhere in the repo. The runbook says to import `dashboard/` as the Vercel project with Root Directory `dashboard` (`docs/runbook.md` step 5).
- Dashboard: `next` 15.5.27, `react` 19.2.8, App Router. Existing route handlers: `/api/jobs`, `/api/journal`, `/api/performance`, `/api/settings`, `/api/control`, `/api/state` (`dashboard/app/api/*/route.ts`). None set `runtime`, `maxDuration` or `preferredRegion`.
- `dashboard/middleware.ts` enforces HTTP Basic Auth on everything matched by `matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"]`. That matcher **includes every `/api/...` path**. It returns 401 (not a redirect) when the `Authorization` header is not valid `Basic` credentials, and 503 when `DASHBOARD_USER`/`DASHBOARD_PASSWORD` are unset.
- Worker (`worker/pyproject.toml`): `requires-python = ">=3.10"`, setuptools build, core dependency only `requests>=2.31`; extras `yahoo = ["yfinance>=0.2.54"]`, `groww`, `llm`, `all`. `pandas` is not declared directly; it arrives through `yfinance` and is imported lazily in `worker/thunderbot/daily.py`. `numpy` is not imported directly by the worker.
- Worker entry points are long-running loops, not request handlers: `thunderbot.cli:main` with subcommands `invest`, `jobs`, `paper`, `live`, `serve` and others; `InvestRunner.run_forever()` calls `tick()` in a sleep loop and trades once a day at `TB_INVEST_AT` (default 15:10 IST); `JobRunner.run_forever()` polls the Supabase `jobs` table and `JobRunner.run_once()` claims and executes one job (`worker/thunderbot/invest.py`, `worker/thunderbot/jobs.py`). `tick()` and `run_once()` are the natural single-shot units for a serverless function.
- State is **not** purely in Supabase today: `worker/thunderbot/store.py` builds a `CompositeStore` whose source of truth is a local SQLite file (`<TB_DATA_DIR>/journal.sqlite3`, default `var/`) with Supabase as a "best-effort mirror" (`docs/architecture.md`). On Vercel the filesystem is ephemeral, so this needs a Supabase-only store before the worker can run there.
- Live trading requires a whitelisted static IP (`compliance.check_static_ip`, `TB_EXPECTED_STATIC_IP`); paper trading on Yahoo data does not.

## 1. Vercel Cron Jobs: per-plan limits and mechanics

### Takeaway
On Hobby a cron can run at most once per day and only with hour-level precision, so Hobby cannot wake the worker every few minutes and cannot guarantee "about 15:10 IST"; Pro allows per-minute schedules with per-minute precision and 100 cron jobs per project. Cron Jobs are now labelled a legacy feature being migrated to "Vercel Schedules" (public beta on all plans), which adds timezones and Python script targets, but I could not confirm the Schedules frequency limits for Hobby.

### Cited Findings

**Limits per plan**
- [search snippet] The current usage page lists **Hobby: 100 cron jobs, once per day, precision "Per-hour (±59 min)"**; **Pro and Enterprise: 100 cron jobs, once per minute, per-minute precision**. — [Vercel docs: Cron Jobs usage and pricing](https://vercel.com/docs/cron-jobs/usage-and-pricing) (also served at [/docs/schedules/cron-jobs/usage-and-pricing](https://vercel.com/docs/schedules/cron-jobs/usage-and-pricing)); page date not seen.
- [search snippet] The limit of 100 per project applies to every plan. — [Vercel changelog: Cron jobs now support 100 per project on every plan](https://vercel.com/changelog/cron-jobs-now-support-100-per-project-on-every-plan). A third-party blog dates this to January 2026; I could not confirm the date. The older figures (2 on Hobby, 40 on Pro) still appear on third-party pages and are outdated.
- [search snippet] "Hobby accounts are limited to daily cron jobs" and "Cron expressions that would run more frequently will fail during deployment." — [Vercel docs: Cron Jobs usage and pricing](https://vercel.com/docs/cron-jobs/usage-and-pricing).
- [search snippet] An older version of the same page (seen on a legacy mirror, and which still listed 2 cron jobs for Hobby) explained the Hobby window as: "a cron job configured as `0 1 * * *` will trigger anywhere between 1:00 am and 1:59 am." The current page expresses this as "Per-hour (±59 min)". — [legacy mirror of the usage page](https://zeit.co/docs/cron-jobs/usage-and-pricing); current wording at [Vercel docs](https://vercel.com/docs/cron-jobs/usage-and-pricing).

**How a cron is invoked**
- [search snippet] Triggers are "sent as an HTTP GET request to your project's production deployment URL, using the `path` provided in your project's `vercel.json` file." — [Vercel docs: Cron Jobs](https://vercel.com/docs/cron-jobs).
- [search snippet] Functions triggered by a cron job carry the user agent `vercel-cron/1.0`. — [Vercel docs: Cron Jobs](https://vercel.com/docs/cron-jobs).
- [search snippet] Vercel invokes cron jobs only for production deployments, not preview deployments. — [Vercel docs: Cron Jobs](https://vercel.com/docs/cron-jobs).
- [search snippet] Cron invocations do not follow redirects; with `trailingSlash` enabled the trailing slash must be written explicitly in the path. — [Vercel KB: Troubleshooting Vercel Cron Jobs](https://vercel.com/kb/guide/troubleshooting-vercel-cron-jobs).
- [search snippet] Cron duration limits are the same as Vercel Functions duration limits. — [Vercel docs: Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs).

**Expression syntax**
- [search snippet] "Cron jobs on Vercel do not support alternative expressions like `MON`, `SUN`, `JAN`, or `DEC`." The timezone is always UTC. Day of month and day of week cannot both be set in one expression. — [Vercel docs: Cron Jobs](https://vercel.com/docs/cron-jobs).
- [source code] The `crons` entry shape is `{ "path": string, "schedule": string }`. — [vercel/vercel `packages/build-utils/src/types.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/build-utils/src/types.ts)
- [source code] Vercel's own example `vercel.json` uses `"crons": [{ "path": "/api/cron/1m", "schedule": "* * * * *" }, { "path": "/api/cron/10m", "schedule": "*/10 * * * *" }, { "path": "/api/cron/1d", "schedule": "0 0 * * *" }, { "path": "/api/cron/1w", "schedule": "0 0 * * 0" }]`. — [vercel/examples `solutions/cron/vercel.json`](https://raw.githubusercontent.com/vercel/examples/main/solutions/cron/vercel.json)

**Authentication**
- [search snippet] Adding a `CRON_SECRET` environment variable secures cron invocations; the handler checks the request's `Authorization` header against it. Vercel sends the production deployment's copy of the secret, and a changed secret only reaches deployments created after the change, so a redeploy is needed. — [Vercel docs: Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs)
- A third-party guide says Vercel recommends a secret of at least 16 random characters; not confirmed on the official page. — [cronuru.com guide](https://cronuru.com/guides/vercel-cron)

**Vercel Schedules (the successor)**
- [search snippet] Cron Jobs are described in the docs as "a legacy feature and will be migrated to Schedules". Schedules is in **public beta on all plans**; existing Cron Jobs continue to work; the migration guide says route code does not need to change. — [Vercel docs: Schedules](https://vercel.com/docs/schedules), [Migrate from Cron Jobs](https://vercel.com/docs/schedules/migrate-from-cron-jobs), [changelog: Vercel Schedules is now in public beta](https://vercel.com/changelog/vercel-schedules-is-now-in-public-beta)
- [search snippet] Schedules add timezones, private targets, one-time runs, execution history, and pausing or running a schedule without redeploying. — [Vercel docs: Schedules](https://vercel.com/docs/schedules)
- [search snippet] Schedules limits "may change before general availability". On Hobby a deployment can declare up to 100 static schedules, and "deployments don't recreate a deleted static schedule until you update it in vercel.json to meet the Hobby limits" (so Hobby-specific limits on schedules do exist). — [Vercel docs: Schedules limits](https://vercel.com/docs/schedules/limits)
- [source code] A schedule definition is `schedule` (cron expression, required), optional `timezone` ("IANA timezone for cron evaluation, e.g. "America/New_York". Defaults to UTC."), optional `jitter` ("Maximum random delay applied to each firing, from 1 to 15 whole minutes"), plus exactly one target: `path` (with `requestMethod` `GET` or `POST`, "Defaults to `POST`"), or `function` (optionally with `service`), or `topic` (a queue topic). — [vercel/vercel `packages/build-utils/src/types.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/build-utils/src/types.ts)
- [source code] `vercel.json` syntax: "`schedules` in `vercel.json` can now be an object keyed by schedule name, like `"schedules": { "nightly": { "schedule": "0 0 * * *", "path": "/api/cron" } }`"; the older array format has since been removed (CLI 65.4.0). Entries use "`schedule` plus exactly one of `path`, `function`, `topic`, or `entrypoint`, with optional `name`, `timezone`, and `jitter`". — [vercel/vercel `packages/cli/CHANGELOG.md`](https://raw.githubusercontent.com/vercel/vercel/main/packages/cli/CHANGELOG.md)
- [source code] Python scripts can be schedule targets without an HTTP route: "A `.py` entrypoint such as `jobs/nightly.py` runs as a script once per firing in a private function under `_vercel/schedules/`." — [vercel/vercel `packages/python/CHANGELOG.md`](https://raw.githubusercontent.com/vercel/vercel/main/packages/python/CHANGELOG.md)
- [source code] The CLI has `vercel schedules create | update | enable | disable | invoke | delete | list | executions list`. — [vercel/vercel `packages/cli/CHANGELOG.md`](https://raw.githubusercontent.com/vercel/vercel/main/packages/cli/CHANGELOG.md)

**Hobby "personal, non-commercial" clause**
- [search snippet] "Hobby teams are restricted to non-commercial personal use only" and "all commercial usage of the platform requires either a Pro or Enterprise plan." Page metadata reported by the search tool: last updated 2026-09-14. — [Vercel docs: Fair use guidelines](https://vercel.com/docs/limits/fair-use-guidelines)
- A third-party guide paraphrases Vercel's definition of commercial use as any deployment made for the financial gain of anyone involved, including a paid consultant who wrote the code. — [livemy.app: Vercel pricing explained](https://livemy.app/blog/vercel-pricing)

### Inferences
- **Hobby cannot run the intraday loop.** "Every few minutes during 03:45-10:00 UTC" needs sub-daily schedules, which fail at deployment on Hobby. This is a hard no on Hobby with Vercel's own scheduler.
- **Hobby cannot promise 15:10 IST.** With per-hour precision, a daily cron for 09:40 UTC is not guaranteed to run near 09:40. The only worked example in the docs is for minute 0 ("`0 1 * * *` ... between 1:00 am and 1:59 am"); the current "±59 min" wording does not say whether a `40 9` expression fires within 09:00-09:59 or up to 59 minutes either side of 09:40. NSE closes at 10:00 UTC, so a run that slips past 10:00 UTC would miss the session. The conservative Hobby expression is `0 9 * * 1-5`, which under the documented example fires somewhere in 09:00-09:59 UTC (14:30-15:29 IST): inside market hours, but up to 40 minutes before or 19 minutes after the intended 15:10 decision time. Whether that is acceptable is a strategy question, not a platform one.
- **Pro expressions for market hours** (UTC only on legacy crons; weekdays must be numeric): `45-59/5 3 * * 1-5`, `*/5 4-9 * * 1-5` and `0 10 * * 1-5` cover 09:15-15:30 IST at 5-minute steps; `40 9 * * 1-5` is 15:10 IST. Indian market holidays are not expressible in cron, so the handler must check `worker/deploy/nse_holidays.txt` (the worker's `MarketClock` already does this).
- **Schedules would fit Thunderbot better than legacy crons** if its plan limits allow it: `"timezone": "Asia/Kolkata"` removes the UTC arithmetic, and a Python script target runs in a private function with no public route, which sidesteps the dashboard's Basic Auth middleware altogether. It is beta, so its limits and syntax may still change (the CLI changelog shows three breaking format changes during the beta).
- **Note the method difference:** legacy crons send GET; a Schedules `path` target defaults to POST. A handler should accept the method its scheduler uses.
- **The Basic Auth middleware will block cron calls today.** A cron request carries `Authorization: Bearer <CRON_SECRET>` (see Gaps for the exact format), not Basic credentials, so `dashboard/middleware.ts` would answer 401 for any cron path under the current matcher. See section 4 for the fix.
- **Fair use is a grey area for a personal trading bot.** The bot sells nothing, has no visitors and no customers, which points to "personal". But it exists to make money for its owner, and the (third-party-reported) definition turns on "financial gain of anyone involved". I found no Vercel statement that settles it. Pro removes the question.

### Gaps
- **Exact text of the docs on retries, duplicates and overlap was not retrieved.** The search tool confirmed only that the Managing Cron Jobs page has sections on duration, error handling and concurrency control. *Recalled, not re-verified* from the pre-2026 page: Vercel does not retry a failed cron invocation; the same cron event can occasionally be delivered more than once, so handlers should be idempotent; and if a run is still in progress when the next one fires, a second instance starts concurrently unless the handler takes its own lock. Thunderbot should assume all three (for example a per-trading-day row in Supabase as the idempotency key and lock). Verify at [Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs).
- **Exact `CRON_SECRET` header format and the official example code were not retrieved.** *Recalled, not re-verified*: Vercel sends `Authorization: Bearer <CRON_SECRET>` and the docs' Next.js example compares `request.headers.get('authorization')` with `` `Bearer ${process.env.CRON_SECRET}` `` and returns 401 otherwise.
- **Exact deployment error text for a sub-daily cron on Hobby** not retrieved. Third-party guides quote it as starting "Hobby accounts are limited to daily Cron Jobs" followed by the offending expression.
- **Which way the Hobby hour window falls for a non-zero minute** (within the named hour, or ±59 minutes around the named minute) is not stated in anything I could read.
- **Schedules limits per plan** (minimum interval and precision on Hobby vs Pro, pricing) not retrieved: [Schedules limits](https://vercel.com/docs/schedules/limits).
- Whether one `path` may appear in several `crons` entries with different schedules, and whether range-with-step (`45-59/5`) is accepted, were not verified.
- "Last updated" dates of the cron pages were not visible.

## 2. Vercel Functions limits per plan

### Takeaway
With Fluid compute (default for projects created since 23 April 2025), functions on Hobby get 300 s default and maximum duration, and Pro gets 300 s default configurable to 800 s, so both the 15:10 run and 10-120 s backtests fit on either plan. Hobby is limited to one function region, 2 GB memory and fixed monthly allowances with no paid overage.

### Cited Findings

**Duration**
- [search snippet] With Fluid compute: "Hobby: 300s (default and maximum)"; "Pro and Ent: 300s (default) - configurable up to 800s". — [Vercel docs: Functions limitations](https://vercel.com/docs/functions/limitations); [changelog: Higher defaults and limits for Vercel Functions running Fluid compute](https://vercel.com/changelog/higher-defaults-and-limits-for-vercel-functions-running-fluid-compute)
- [search snippet] A beta "extended max duration" supports up to 1800 s; a third-party write-up says it is for Pro and Enterprise, needs Fluid compute, and is set per function in `vercel.json`. — [Vercel docs: Functions limitations](https://vercel.com/docs/functions/limitations); [createwith.com summary](https://www.createwith.com/tool/vercel/updates/vercel-bun-runtime-adds-large-functions-and-extended-max-duration)
- [search snippet] Without Fluid compute (legacy figures, seen on an older cached Vercel page): Hobby 10 s default / 60 s maximum; Pro 15 s default / 300 s maximum. — [Vercel docs: Configuring maximum duration](https://vercel.com/docs/functions/configuring-functions/duration)
- [source code] In `vercel.json`, `maxDuration` is an integer from 1 or the string `"max"`; the CLI only applies a coarse client-side ceiling of 3600 and "the authoritative limit is enforced by server-side validation at deploy time." — [vercel/vercel `packages/build-utils/src/max-duration.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/build-utils/src/max-duration.ts)

**Fluid compute default**
- [search snippet] "As of April 23, 2025, fluid compute is enabled by default for new projects." — [changelog: Fluid compute is now the default for new projects](https://vercel.com/changelog/fluid-compute-is-now-the-default-for-new-projects); [Vercel docs: Fluid compute](https://vercel.com/docs/fluid-compute)

**Memory and CPU**
- [search snippet] Maximum memory: "Hobby: 2 GB, Pro and Ent: 4 GB". — [Vercel docs: Functions limitations](https://vercel.com/docs/functions/limitations)
- [search snippet] "If you are on the Hobby plan, and have enabled fluid compute, the memory size will be managed by Vercel with a minimum of 1 vCPU." — [Vercel docs: Configuring memory and CPU](https://vercel.com/docs/functions/configuring-functions/memory)
- [source code] Client-side schema bounds in `vercel.json` `functions`: `memory` 128-10240, `maxConcurrency` 1-8192, `architecture` `x86_64` or `arm64`, at most 50 patterns. These are tooling bounds, not plan entitlements. — [vercel/vercel `packages/build-utils/src/schemas.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/build-utils/src/schemas.ts)

**Bundle size and disk**
- [search snippet] "The maximum uncompressed size is 500 MB for Python functions." — [Vercel docs: Python runtime](https://vercel.com/docs/functions/runtimes/python); [changelog: Python Vercel Functions bundle size limit increased to 500MB](https://vercel.com/changelog/python-vercel-functions-bundle-size-limit-increased-to-500mb) (from 250 MB). An older snapshot of the Python page still says 250 MB.
- [search snippet] "Vercel Functions now support Node.js and Python deployments with package sizes up to 5GB on Fluid compute through the Large Functions public beta." — [Vercel docs: Functions limitations](https://vercel.com/docs/functions/limitations)
- [source code] How the Python builder actually handles size: bundles up to **225 MB** ship as an ordinary zip ("AWS Lambda uncompressed size limit is 250MB, but we use 225MB to leave room for the Lambda layers"). Above that, with a `uv.lock`, public packages are **deferred to a `uv sync` into `/tmp` at cold start** (budget 500 MB: "AWS Lambda ephemeral storage (/tmp) is 512MB. Use 500MB to leave a buffer"). Beyond that, "large functions (beta)" bundle everything, up to 5 GiB. A custom `installCommand` disables the deferred install and fails the build over 225 MB. — [vercel/vercel `packages/python/src/dependency-externalizer.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/python/src/dependency-externalizer.ts), [`packages/python/src/index.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/python/src/index.ts)

**Included usage and overage on Hobby**
- [search snippet] Hobby includes 4 hours/month of Fluid Active CPU, 360 GB-hrs/month of Fluid Provisioned Memory and 1M function invocations/month. — [Vercel pricing](https://vercel.com/pricing)
- Hobby has no paid overage; limits are hard caps and "you usually wait for limits to reset" (third-party summaries). — [stork.ai: Vercel pricing 2026](https://www.stork.ai/blog/vercel-pricing-2026), [benchlm.ai cost worksheet](https://benchlm.ai/vercel/pricing)

**Regions**
- [search snippet] "The default Function region is Washington, D.C. (`iad1`) for all new projects." — [Vercel docs: Configuring function regions](https://vercel.com/docs/functions/configuring-functions/region)
- [search snippet] Regions per plan: **Hobby a single region, Pro 5 regions, Enterprise all regions**; deploying to more regions than the plan allows fails before the build step. Page metadata reported by the search tool: updated 2026-07-15. — [Vercel docs: Configuring function regions](https://vercel.com/docs/functions/configuring-functions/region); contradicted on the Pro figure by the older [changelog: Pro customers can now configure up to 3 regions](https://vercel.com/changelog/pro-customers-can-now-configure-up-to-3-regions-for-vercel-functions)
- [search snippet] Regions are set with a `regions` array in `vercel.json` (example from the changelog: `"regions": ["sfo1", "lhr1", "sin1"]`) followed by a redeploy. — [changelog: Pro regions](https://vercel.com/changelog/pro-customers-can-now-configure-up-to-3-regions-for-vercel-functions)
- [source code] `regions` and `functionFailoverRegions` are also accepted per function pattern inside `functions`. — [vercel/vercel `packages/build-utils/src/schemas.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/build-utils/src/schemas.ts)

### Inferences
- **Duration is not the constraint on either plan.** A 10-120 s backtest and a once-a-day rebalance both fit in 300 s on Hobby and Pro, provided Fluid compute is on for the project. If the Thunderbot Vercel project predates 23 April 2025 or has Fluid switched off, the Hobby ceiling would be the legacy 60 s and a 120 s backtest would be killed.
- **Hobby can keep functions in Mumbai.** "A single region" on Hobby, with a selectable `regions` setting, is consistent with the brief's statement that the dashboard already runs in `bom1`; the Python function would follow the project's region setting. I did not see a doc line naming `bom1` explicitly.
- **Usage would be tiny against the Hobby allowance if scheduling were allowed.** Rough arithmetic for a Pro-style 5-minute cadence: about 76 wakes per trading day × about 21 days ≈ 1,600 invocations/month against 1M included; at an assumed 3 s of CPU each that is about 1.3 Active CPU hours against 4 included. The daily-only pattern Hobby permits is about 21 invocations/month. (The 3 s figure is my assumption, not a measurement.)
- **The 225 MB internal threshold matters more than the headline 500 MB.** Staying under 225 MB keeps every dependency in the zip. Between 225 MB and 500 MB the function still deploys, but pays for a dependency install into `/tmp` on every cold start, which is the wrong trade for a job that cold-starts on nearly every run.

### Gaps
- **Request/response body limit (historically 4.5 MB)** not re-verified today. *Recalled, not re-verified.* Large backtest results should be written to Supabase rather than returned in the response, which is what `JobRunner` already does.
- **vCPU per plan** (historically Standard 2 GB / 1 vCPU, Performance 4 GB / 2 vCPU on Pro) not re-verified beyond the Hobby quote above.
- **Whether Fluid compute must be switched on manually for older projects**, and where, not re-verified. *Recalled*: Project Settings, Functions, or `"fluid": true` in `vercel.json`.
- **What exactly happens when Hobby exceeds its allowance** (pause until reset, and for how long) not confirmed on an official page: [Hobby plan](https://vercel.com/docs/plans/hobby).
- **Concurrency limits per plan** not retrieved.
- Whether Pro is 5 regions (newer docs page) or 3 (older changelog) is unresolved; irrelevant for a single-region `bom1` deployment.
- "Last updated" dates of the limits, duration and memory pages were not visible.

## 3. Python runtime on Vercel

### Takeaway
Python on Vercel was announced as generally available in mid-October 2026, supports 3.12 (default), 3.13 and 3.14, installs with uv from `pyproject.toml`/`uv.lock`/`requirements.txt`, and the worker's real dependency set (yfinance + pandas + numpy and transitive packages) measures 168 MB unpacked, which fits under the 225 MB standard threshold and far under the 500 MB limit. No cold-start measurement for this stack on Vercel was found.

### Cited Findings

**Status and versions**
- [search snippet] "Python on Vercel is now generally available." Third-party sources date the post to about 15 October 2026; the changelog's own date was not seen. The same announcement marks the AI SDK for Python, Workflow SDK for Python and Queues as beta. — [Vercel changelog: Python on Vercel is now generally available](https://vercel.com/changelog/python-on-vercel-is-now-generally-available), [Vercel blog](https://vercel.com/blog/python-on-vercel-is-now-generally-available), [Vercel community weekly, 19 Oct 2026](https://community.vercel.com/t/vercel-weekly-october-19-2026/51009)
- [search snippet] Supported versions: 3.12 (default), 3.13 and 3.14; "If the project doesn't specify a supported version, the default version will be used." — [Vercel docs: Python version](https://vercel.com/docs/functions/runtimes/python/python-version)
- [source code] The builder's version table is 3.14, 3.13, 3.12, 3.11, 3.10, 3.9 (3.6 discontinued), default 3.12. The version is read from `.python-version`, `pyproject.toml` (`requires-python`) or `Pipfile.lock`; otherwise it logs "No Python version specified in .python-version, pyproject.toml, or Pipfile.lock. Using python version: 3.12". — [vercel/vercel `packages/python/src/version.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/python/src/version.ts). Note the docs list only 3.12-3.14 as supported while the builder table still contains 3.9-3.11; treat 3.12+ as the supported set.
- [source code] Builder package is `@vercel/python` 29.0.0 and pins uv 0.13.5. — [vercel/vercel `packages/python/package.json`](https://raw.githubusercontent.com/vercel/vercel/main/packages/python/package.json), [`packages/python/CHANGELOG.md`](https://raw.githubusercontent.com/vercel/vercel/main/packages/python/CHANGELOG.md)

**Dependencies**
- [search snippet] Dependencies "can be defined in a pyproject.toml with or without a corresponding uv.lock, requirements.txt, or a Pipfile with corresponding Pipfile.lock." — [Vercel docs: Python runtime](https://vercel.com/docs/functions/runtimes/python)
- [source code] The default install path uses uv "to normalize manifests into a uv.lock". — [vercel/vercel `packages/python/src/index.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/python/src/index.ts)
- A third-party handbook says Vercel installs Python dependencies with uv by default and reads `uv.lock` natively. — [pydevtools.com: How to deploy a uv project to Vercel](https://pydevtools.com/handbook/how-to/how-to-deploy-a-uv-project-to-vercel/)

**Entrypoints and handler conventions**
- [source code] Zero-config `api/` directory: every `api/**/*.py` file is built with `@vercel/python`, but only if the file is a valid entrypoint (it must define an app or handler; other `.py` files in `api/` are treated as helpers, not routes). — [vercel/vercel `packages/fs-detectors/src/detect-builders.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/fs-detectors/src/detect-builders.ts), [`packages/fs-detectors/src/python.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/fs-detectors/src/python.ts)
- [source code] A valid entrypoint exports a top-level `app`, `application` or `handler` (error text: "does not export a top-level "app", "application", or "handler" variable"). — [vercel/vercel `packages/python/src/entrypoint.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/python/src/entrypoint.ts)
- [source code] For a standalone Python app (FastAPI, Flask and similar, zero-config), the builder looks for `app`, `index`, `server`, `main`, `wsgi` or `asgi` `.py` files in the root, `src/`, `app/` or `api/`; or follows `[project.scripts] app = "module:attr"` or `[tool.vercel] entrypoint` in `pyproject.toml`. — [vercel/vercel `packages/python/src/entrypoint.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/python/src/entrypoint.ts)
- [source code] The runtime "provides an ASGI/WSGI server implementation" and vendors uvicorn and werkzeug. — [vercel/vercel `python/vercel-runtime/README.md`](https://raw.githubusercontent.com/vercel/vercel/main/python/vercel-runtime/README.md)
- [source code] Vercel's FastAPI starter is a plain `pyproject.toml` project (`requires-python = "==3.12.*"`, `fastapi`, `uvicorn`) deployed "with zero configuration". — [vercel/vercel `examples/fastapi`](https://raw.githubusercontent.com/vercel/vercel/main/examples/fastapi/README.md)

**Function configuration**
- [source code] Per-pattern keys accepted under `functions` in `vercel.json`: `runtime`, `memory`, `maxDuration`, `maxConcurrency`, `regions`, `functionFailoverRegions`, `includeFiles`, `excludeFiles`, `installCommand`, `architecture`, `supportsCancellation`, `experimentalTriggers`. The Python builder applies both project-level and per-function `excludeFiles`. — [vercel/vercel `packages/build-utils/src/schemas.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/build-utils/src/schemas.ts), [`packages/python/src/index.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/python/src/index.ts)
- [source code] The builder precompiles Python bytecode into whatever room is left under a 220 MB ceiling to speed up cold starts, ranking "by cold-start value instead of size", and since a recent release leaves `pip` out of the bundle ("saves about 5 MB per function"). — [vercel/vercel `packages/python/CHANGELOG.md`](https://raw.githubusercontent.com/vercel/vercel/main/packages/python/CHANGELOG.md)

**Does pandas + numpy + yfinance fit? Measured today**
- [measured] `pip install --target` of `yfinance pandas numpy requests` using CPython 3.12 manylinux x86_64 wheels (no bytecode) comes to **168 MB unpacked**: pandas 45 MB, curl_cffi 40 MB, numpy 30 MB plus `numpy.libs` 27 MB, lxml 12 MB, tzdata 3 MB, pytz 3 MB, protobuf 2 MB, everything else about 1 MB each or less. Zipped: 49 MB. With every `.pyc` compiled: 224 MB. Bundled test directories account for about 26 MB of the 168 MB. Versions resolved: yfinance 1.8.0, pandas 3.1.1, numpy 2.5.4, curl_cffi 0.17.0, lxml 6.1.3, peewee 4.5.3, protobuf 7.36.2, websockets 17.4, beautifulsoup4 4.15.0, requests 2.34.2. — [PyPI: yfinance](https://pypi.org/project/yfinance/), [PyPI: pandas](https://pypi.org/project/pandas/), [PyPI: numpy](https://pypi.org/project/numpy/), [PyPI: curl_cffi](https://pypi.org/project/curl-cffi/)
- [measured] yfinance 1.8.0 declares these required dependencies: `beautifulsoup4>=4.11.1`, `curl_cffi>=0.17`, `lxml>=4.9.0`, `numpy>=1.16.5`, `pandas>=1.3.0`, `peewee>=3.16.2`, `platformdirs>=2.0.0`, `protobuf>=3.19.0`, `pytz>=2022.5`, `requests>=2.31`, `websockets>=13.0`. `frozendict` and `multitasking` are no longer in the list. — [PyPI JSON for yfinance](https://pypi.org/pypi/yfinance/json)
- [measured] Binary wheels exist for the Lambda-style target: pandas 3.1.1 `cp312 manylinux_2_28_x86_64` (12.0 MB download, requires Python >=3.11), numpy 2.5.4 `cp312 manylinux_2_28_x86_64` (16.7 MB, requires Python >=3.12), curl_cffi 0.17.0 `abi3 manylinux2014_x86_64` (14.1 MB), lxml 6.1.3 `cp312 manylinux` (5.1 MB). — [PyPI JSON for pandas](https://pypi.org/pypi/pandas/json), [numpy](https://pypi.org/pypi/numpy/json), [curl_cffi](https://pypi.org/pypi/curl_cffi/json), [lxml](https://pypi.org/pypi/lxml/json)

**Real-world reports**
- Vercel community threads about Python functions exceeding the old 250 MB limit exist (titles only seen; contents not read): "Python deploy error: exceeded the unzipped maximum size of 250 MB", "NextJS + Flask API: a serverless function exceeding 250mb limit", "Python serverless functions: reducing size of dependencies". — [community thread 26649](https://community.vercel.com/t/python-deploy-error-exceeded-the-unzipped-maximum-size-of-250-mb/26649), [thread 15625](https://community.vercel.com/t/nextjs-flask-api-a-serverless-function-exceeding-250mb-limit/15625), [thread 1765](https://community.vercel.com/t/python-serverless-functions-reducing-size-of-dependencies/1765); Vercel's own guide: [Troubleshooting the function 250 MB limit](https://vercel.com/kb/guide/troubleshooting-function-250mb-limit)

### Inferences
- **The yahoo-only worker fits comfortably.** 168 MB of dependencies plus the worker's own code (a few hundred kB) is under the builder's 225 MB "standard" threshold, so all dependencies ship in the zip and none are installed at cold start. Headroom is about 55 MB. Excluding bundled test suites via `excludeFiles` would recover up to about 26 MB more.
- **Adding the other extras erodes the headroom.** `anthropic` + `pydantic` (the `llm` extra) and `growwapi` + `pyotp` (the `groww` extra) were not measured. My attempt to resolve `growwapi` together with the rest for a binary-only cp312 manylinux target failed with a dependency conflict, so the `all` extra needs its own test before assuming it deploys. If the total crosses 225 MB the function still deploys (up to 500 MB) but takes the slower cold-start install path.
- **`requires-python = ">=3.10"` will resolve to Vercel's default 3.12**, which satisfies numpy 2.5 (needs >=3.12) and pandas 3.1 (needs >=3.11). Adding a `.python-version` file makes this explicit.
- **Two handler styles are available.** A `handler(BaseHTTPRequestHandler)` class, or a WSGI/ASGI `app` (FastAPI/Flask). For two or three endpoints (tick, daily, backtest) a single small FastAPI or Flask `app` in one file gives one bundle and one cold start profile; separate files each get their own copy of the 168 MB bundle.
- **The worker needs a thin serverless wrapper, not a rewrite**: one handler calling `InvestRunner.tick()` once, and one calling `JobRunner.run_once()`, with the SQLite-backed store replaced by a Supabase-only store.

### Gaps
- **Cold-start time for a pandas + yfinance function on Vercel**: no measurement found. The brief's 2-5 s guess is unverified. It can only be settled by deploying and reading the function logs.
- **Whether Yahoo Finance serves Vercel's `bom1` egress IPs reliably** (rate limits or blocks on cloud IP ranges): no source found in this session. This is a real operational risk for a once-a-day job with no automatic retry and should be tested from a deployed function before relying on it.
- **Reports of people running yfinance specifically on Vercel in 2025-2026**: none found before the search budget ran out.
- **Python streaming responses and a Python `waitUntil` equivalent**: not verified.
- Whether the Python runtime docs page still carries any plan restriction, and its "last updated" date, were not visible.
- The official docs' own example of `functions` config for `api/**/*.py` was not retrieved; the example in section 4 is assembled from the schema.

## 4. Running the Python function in the same Vercel project as the Next.js App Router dashboard

### Takeaway
A Python `api/` directory next to a Next.js app in one Vercel project is supported by Vercel's own build tooling, and with Root Directory `dashboard` that folder has to be `dashboard/api/`; the newer `services` configuration is the designed way to host a Next.js frontend and a Python backend from separate folders. The dashboard's Basic Auth middleware matches all `/api/` paths and will reject scheduler calls unless its matcher is changed.

### Cited Findings

**`api/*.py` beside Next.js**
- [source code] Vercel's builder detection explicitly expects non-JavaScript functions in `api/` alongside Next.js. Its warning text reads: "When using Next.js, it is recommended to place JavaScript Functions inside of the `pages/api` (provided by Next.js) directory instead of `api` (provided by Vercel). Other languages (Python, Go, etc) should still go in the `api` directory." — [vercel/vercel `packages/fs-detectors/src/detect-builders.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/fs-detectors/src/detect-builders.ts)
- [source code] For Next.js projects Vercel does not add its usual catch-all 404 for unmatched `/api` paths, because "it serves /api (Pages + App Router) and 404s unmatched paths". Both sets of routes therefore share the `/api` prefix. — [vercel/vercel `packages/fs-detectors/src/detect-builders.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/fs-detectors/src/detect-builders.ts)
- [source code] A `functions` pattern in `vercel.json` that matches nothing fails the build with "The pattern "..." defined in `functions` doesn't match any Serverless Functions." — [vercel/vercel `packages/fs-detectors/src/detect-builders.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/fs-detectors/src/detect-builders.ts)
- [source code] The `api/**` scan is relative to the project root being built, so with Root Directory `dashboard` the folder is `dashboard/api/`. — [vercel/vercel `packages/fs-detectors/src/detect-builders.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/fs-detectors/src/detect-builders.ts)

**The Next.js + FastAPI starter template**
- [source code] The template keeps FastAPI in a root `api/index.py` next to the Next.js `app/` directory, with routes declared under `/api/py/...` (`@app.get("/api/py/helloFastApi")`, `FastAPI(docs_url="/api/py/docs", openapi_url="/api/py/openapi.json")`). — [digitros/nextjs-fastapi `api/index.py`](https://raw.githubusercontent.com/digitros/nextjs-fastapi/main/api/index.py)
- [source code] Routing is done with `next.config.js` rewrites: `source: "/api/py/:path*"` goes to `http://127.0.0.1:8000/api/py/:path*` in development and to `"/api/"` in production (the Python function built from `api/index.py`). — [digitros/nextjs-fastapi `next.config.js`](https://raw.githubusercontent.com/digitros/nextjs-fastapi/main/next.config.js)
- [source code] The README states: "The Python/FastAPI server is mapped into to Next.js app under `/api/`", "the app/api routes are available on the same domain, so you can use NextJs Route Handlers and make requests to `/api/...`", and "In production, the FastAPI server is hosted as Python serverless functions on Vercel." The template has no `vercel.json` and is on Next.js 14. — [digitros/nextjs-fastapi `README.md`](https://raw.githubusercontent.com/digitros/nextjs-fastapi/main/README.md)
- [search snippet] Vercel also lists a Next.js + Flask starter. — [Vercel templates: nextjs-flask-starter](https://vercel.com/templates/next.js/nextjs-flask-starter)

**Vercel Services (multi-service projects)**
- [search snippet] "To deploy a project that uses multiple services, your project framework setting must be set to Services and `experimentalServices` must be present in `vercel.json`." The documented example mounts a Next.js frontend at `/` and a FastAPI backend at `/svc/api`. Newer pages use a `services` key with `root` and `framework` fields plus rewrites. — [Vercel docs: Services (experimental)](https://vercel.com/docs/services/experimental), [Vercel KB: The complete guide to Vercel Services](https://vercel.com/kb/guide/vercel-services), [Vercel blog: Vercel Services](https://vercel.com/blog/vercel-services-run-full-stack-on-vercel), [Vercel KB: Python backend on Vercel](https://vercel.com/kb/guide/python-backend-on-vercel)
- [search snippet] Sources conflict on whether the route prefix is stripped before the request reaches the backend; the experimental docs table shows the application receiving the full path, for example `/svc/api/users`. — [Vercel docs: Services (experimental)](https://vercel.com/docs/services/experimental)
- [source code] Three config keys are recognised: `experimentalServices` (legacy), `services` (current), and `experimentalServicesV2` (a deprecated alias of `services`). The CLI ships "a migration assistant for `experimentalServices` which converts a legacy `experimentalServices` config into `services` with top-level service rewrites." — [vercel/vercel `packages/fs-detectors/src/services/types.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/fs-detectors/src/services/types.ts), [`packages/cli/CHANGELOG.md`](https://raw.githubusercontent.com/vercel/vercel/main/packages/cli/CHANGELOG.md)
- [source code] Current `services` entry fields: `root` (required, "Path to the service root, relative to `vercel.json`"), `framework`, `runtime`, `entrypoint` ("a file path or a module specification (for Python)"), `command`, `installCommand`, `buildCommand`, `devCommand`, `ignoreCommand`, `outputDirectory`, `bindings` (`{ service, format: "url", env }` to inject another service's URL), `functions`, and a per-service `headers`/`redirects`/`rewrites`/`routes` table "applied only after top-level routing". — [vercel/vercel `packages/build-utils/src/types.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/build-utils/src/types.ts)
- [source code] Legacy `experimentalServices` entry fields: `type` (`web`, `cron`, `worker`, `job`), `trigger` (`queue`, `schedule`, `workflow`), `root`, `entrypoint` (examples: "apps/web", "services/fastapi/main.py"), `framework`, `builder`, `runtime` (for example `python3.14`), `memory`, `maxDuration`, `includeFiles`, `excludeFiles`, `mount` or `routePrefix` ("deprecated, use mount instead") or `subdomain`, `schedule` ("Cron schedule expression(s)"), `topics`, `env`. Marked "@experimental This feature is experimental and may change." — [vercel/vercel `packages/build-utils/src/types.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/build-utils/src/types.ts)
- [source code] Scheduled Python services are routed internally at `/_svc/{serviceName}/crons/{entry}/{handler}`, and a Python cron service may define its schedules in code ("Support dynamically specifying crons from a python service"). — [vercel/vercel `packages/fs-detectors/src/services/types.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/fs-detectors/src/services/types.ts), [`packages/python/src/crons.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/python/src/crons.ts)

**Middleware in front of Python routes**
- [source code] Next.js docs: "Proxy will be invoked for **every route in your project**. Given this, it's crucial to use matchers to precisely target or exclude specific routes." Execution order: (1) `headers` from `next.config.js`, (2) `redirects`, (3) Proxy, (4) `beforeFiles` rewrites, (5) filesystem routes (`public/`, `_next/static/`, `pages/`, `app/`), (6) `afterFiles` rewrites, (7) dynamic routes, (8) `fallback` rewrites. The 15.5 docs say the same with the word "Middleware". — [vercel/next.js `proxy.mdx` (canary)](https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/proxy.mdx), [`middleware.mdx` (v15.5.0)](https://raw.githubusercontent.com/vercel/next.js/v15.5.0/docs/01-app/03-api-reference/03-file-conventions/middleware.mdx)
- [source code] "Without a `matcher`, Proxy runs on **every request**, including static files (`_next/static`), image optimizations (`_next/image`), and assets in the `public/` folder." The documented exclusion pattern is a negative lookahead such as `'/((?!api|_next/static|_next/image|favicon.ico|sitemap.xml|robots.txt).*)'`. Matcher values must be constants. — [vercel/next.js `proxy.mdx` (canary)](https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/proxy.mdx)
- [source code] "The `middleware.js` file convention has been **deprecated** in Next.js 16 and renamed to `proxy.js`. All functionality remains the same — only the file and export names have changed." Proxy defaults to the Node.js runtime; in 15.5 "Middleware defaults to using the Edge runtime" with Node.js runtime available as stable. — [vercel/next.js `middleware.mdx` (canary)](https://raw.githubusercontent.com/vercel/next.js/canary/docs/01-app/03-api-reference/03-file-conventions/middleware.mdx), [`middleware.mdx` (v15.5.0)](https://raw.githubusercontent.com/vercel/next.js/v15.5.0/docs/01-app/03-api-reference/03-file-conventions/middleware.mdx)
- [source code] On Vercel, a Next.js project's root middleware file is built by the Next.js builder itself ("Exclude the middleware builder for Next.js apps since @vercel/next will build middlewares"), and the separate `proxy` property in `vercel.json` "cannot be used with Next.js because the framework builds its own routing middleware." — [vercel/vercel `packages/fs-detectors/src/detect-builders.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/fs-detectors/src/detect-builders.ts)

### Inferences
- **Simplest layout for Thunderbot today (Root Directory stays `dashboard`):** add `dashboard/api/py/worker.py` (or a single `dashboard/api/index.py` behind a rewrite, as the template does), a `dashboard/requirements.txt` or `dashboard/pyproject.toml`, and `dashboard/vercel.json`. Use a path prefix that none of the six existing route handlers use; `/api/py/...` is the template's convention and does not collide with `/api/jobs`, `/api/journal`, `/api/performance`, `/api/settings`, `/api/control`, `/api/state`.
- **Getting `worker/thunderbot` into the function is the awkward part**, because `worker/` is a sibling of the Root Directory. Options, none verified end to end: (a) declare the worker as a path dependency of the Python project in `dashboard/` (uv supports local path sources, and the Python builder has a code path for local-source packages); this depends on files outside the Root Directory being present in the build; (b) copy or vendor `worker/thunderbot` into `dashboard/` during the build command; (c) move the Vercel project to the repo root and use `services` with `{"root": "dashboard"}` and `{"root": "worker"}`, which is the layout Services is designed for and avoids the outside-root question. Option (c) is cleanest but relies on a feature whose legacy form is explicitly experimental and whose current status I could not confirm.
- **The Basic Auth middleware will reject scheduler calls unless changed.** Under the current matcher every `/api/...` request reaches `middleware.ts`; a cron or schedule request has no Basic credentials, so it gets 401. For a Next.js route handler target this is certain. For an `api/*.py` function it is very likely too, since Next.js documents middleware as running for "every route in your project" ahead of filesystem routes and Vercel builds it into the project's routing; I did not find an official sentence saying so for non-Next functions, so test it. Either way the fix is the same: exclude the scheduler path in the matcher, for example `matcher: ["/((?!api/py/|_next/static|_next/image|favicon.ico).*)"]`, and have the Python handler itself verify `CRON_SECRET`. An excluded path is public, so the handler-level check is not optional. A Schedules `entrypoint`/`function` target, which runs in a private function with no public URL, would avoid the problem entirely.
- **Do not rely on precedence for clashing paths.** If `dashboard/api/jobs.py` and `dashboard/app/api/jobs/route.ts` both existed, both would claim `/api/jobs`. I could not establish which wins; keep the Python paths under their own prefix.
- **Dashboard-triggered backtests:** the existing flow (dashboard inserts a `jobs` row; a runner claims it) maps onto Vercel as "POST `/api/jobs` inserts the row, then calls the Python function, which runs `JobRunner.run_once()`". The browser call to the Python route would pass through middleware with the user's Basic credentials if the path is not excluded, so the on-demand backtest route and the scheduler route may want different paths (one behind Basic Auth, one excluded and protected by `CRON_SECRET`).
- **Illustrative `dashboard/vercel.json`** (assembled by me from the schema and the cron rules above; not copied from Vercel docs and not deployed; the `crons` block as written needs Pro):

```json
{
  "regions": ["bom1"],
  "functions": {
    "api/py/*.py": { "maxDuration": 300, "excludeFiles": "**/tests/**" }
  },
  "crons": [
    { "path": "/api/py/daily", "schedule": "40 9 * * 1-5" }
  ]
}
```

  On Pro, add `"memory"` if more than the default is wanted and intraday entries such as `{ "path": "/api/py/tick", "schedule": "*/5 4-9 * * 1-5" }`. On Hobby the only deployable schedule is once per day (for example `"0 9 * * 1-5"`), with hour-level precision. The Schedules (beta) equivalent with IST would be `"schedules": { "daily": { "schedule": "10 15 * * 1-5", "timezone": "Asia/Kolkata", "path": "/api/py/daily", "requestMethod": "GET" } }`, subject to the unknown plan limits.
- **Next.js version note:** the dashboard is on 15.5.27, so the file stays `middleware.ts` (Edge runtime by default; `atob` and the hand-written constant-time compare already suit Edge). On upgrading to Next.js 16 it becomes `proxy.ts` with the same matcher syntax.

### Gaps
- **The "Include files outside the Root Directory in the Build Step" project setting** and how it interacts with the Python builder was not verified today. *Recalled, not re-verified*: it exists in Project Settings and is on by default for newer projects. A CLI changelog line about daemons ("a daemon `root` can now point above the project root directory ... when the files are in the build. Paths outside the repository are still rejected") suggests above-root files can be part of a build, but that is about a different feature.
- **Current status of `services`** (GA, beta or experimental), its plan availability, and the exact syntax of top-level rewrites that target a service were not retrieved. I have deliberately not written a `services` example because I could only reconstruct it from type definitions. See [Vercel KB: Vercel Services](https://vercel.com/kb/guide/vercel-services).
- **An official statement on whether Next.js middleware runs for non-Next `api/` functions on Vercel**, and Vercel's Routing Middleware docs page, were not retrieved.
- **Path-conflict precedence** between `api/*.py` and `app/api/**/route.ts` not established.
- Whether Vercel's Deployment Protection settings could also intercept scheduler calls on production was not checked.

## 5. Alternatives within Vercel for longer or recurring jobs

### Takeaway
Thunderbot does not need a durable-execution product for 10-120 s backtests because they fit inside one 300 s function invocation on both plans. Vercel Workflows is GA for TypeScript with its Python SDK in beta, Queues and Schedules are in public beta, and none of them lifts the Hobby restriction on how often a schedule may fire as far as I could confirm.

### Cited Findings
- [search snippet] Vercel Workflows is generally available (announced April 2026; "over 100 million runs and over 500 million steps across more than 1,500 customers"). The Python SDK is separate: "workflow support in the Python SDK is currently in beta", with steps marked by a `@wf.step` decorator. — [Vercel docs: Workflows](https://vercel.com/docs/workflows), [Vercel docs: Workflows for Python](https://vercel.com/docs/workflows/python), [Dutch IT Channel, 23 April 2026](https://www.dutchitchannel.nl/news/730354/vercel-workflows-nu-officieel-beschikbaar)
- [search snippet] Vercel Queues is in public beta for all teams (a third-party page dates the public beta to 27 February 2026); the Python Queues SDK entered beta on 19 August 2026. No GA date found. — [Vercel changelog: Queues now in public beta](https://vercel.com/changelog/vercel-queues-now-in-public-beta), [Vercel changelog: Python Queues SDK in beta](https://vercel.com/changelog/vercel-python-queues-sdk-is-now-available-in-beta), [Vercel docs: Queues](https://vercel.com/docs/queues)
- [source code] The Python builder discovers queue subscribers declared in `pyproject.toml` and can adapt Celery, Dramatiq and APScheduler workers; `functions` entries accept `experimentalTriggers` of type `queue/v1beta`, `queue/v2beta` and `schedule/v1beta` with `maxDeliveries`, `retryAfterSeconds`, `initialDelaySeconds` and `maxConcurrency`. — [vercel/vercel `packages/python/CHANGELOG.md`](https://raw.githubusercontent.com/vercel/vercel/main/packages/python/CHANGELOG.md), [`packages/build-utils/src/schemas.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/build-utils/src/schemas.ts)
- [search snippet] Vercel Sandbox on Hobby includes 5 hours/month of Active CPU; "once you exceed your included limit on Hobby, sandbox creation is paused until the next billing cycle"; Pro is billed at $0.128/hour of Active CPU. Its beta/GA status is reported inconsistently. — [Vercel docs: Sandbox pricing](https://vercel.com/docs/vercel-sandbox/pricing)
- [source code] `vercel.json` now accepts a top-level `daemons` field (Dockerfile entrypoints, `instances`, `livenessProbe`, `terminationGracePeriodSeconds`), with a `vercel daemons` command to list, inspect, scale and restart them, and services can use `runtime: "container"`. — [vercel/vercel `packages/cli/CHANGELOG.md`](https://raw.githubusercontent.com/vercel/vercel/main/packages/cli/CHANGELOG.md), [`packages/build-utils/src/types.ts`](https://raw.githubusercontent.com/vercel/vercel/main/packages/build-utils/src/types.ts)
- A third-party article describes Vercel as now running backends with "Python GA, Containers, Daemons". — [buildmvpfast.com](https://www.buildmvpfast.com/blog/vercel-python-backend-containers-daemons-2026)
- [search snippet] Vercel publishes a guide on background workers. — [Vercel KB: Background workers on Vercel](https://vercel.com/kb/guide/background-workers-on-vercel)

### Inferences
- **Backtests: use a plain function.** A 10-120 s job inside a 300 s limit needs no workflow engine. The existing `jobs` table already gives progress reporting and a durable result, so the browser does not have to hold the HTTP request open.
- **Sweeps are the case to watch.** `jobs.py` allows walk-forward sweeps of up to 60 combinations; if one sweep can exceed 300 s it must either be split into one invocation per combination or moved to Pro (800 s) or a queue. I did not measure sweep run time.
- **Queues would give retries that crons lack** (`maxDeliveries`, `retryAfterSeconds`), which matters for a once-a-day order run, but it is beta in both the platform and the Python SDK.
- **Daemons are the only Vercel feature that resembles the worker's current always-on loop**, and would in principle remove the need for a scheduler at all. I could not establish their plan availability, pricing or maturity, so they cannot be planned around from these notes.

### Gaps
- Daemons and container services: status, plans, price and whether they are available in `bom1` not retrieved.
- A Python equivalent of `waitUntil` and background-task behaviour after the response is sent were not verified.
- Workflows and Queues pricing and Hobby allowances not retrieved.
- The content of the background-workers guide was not read.

## 6. Static outbound IP on Vercel

### Takeaway
A fixed egress IP is not available on Hobby; on Pro it is a paid add-on reported at $100 per project per month plus data transfer, using IPs in a shared VPC, and dedicated IPs require Enterprise Secure Compute. This only matters for live Groww orders, not for paper trading or Yahoo data.

### Cited Findings
- [search snippet] Static IPs cost "$100.00/month per project, plus Private Data Transfer at regional rates" and are for Pro and Enterprise teams. — [Vercel docs: Static IPs](https://vercel.com/docs/networking/static-ips) (the page has moved from `/docs/connectivity/static-ips`)
- [search snippet] The pricing page shows Static IPs data transfer "starting at $0.15 per GB"; regional rates are in the regional pricing docs. — [Vercel pricing](https://vercel.com/pricing)
- [search snippet] Static IPs use a shared Virtual Private Cloud; each configured region has its own static IP pair; build traffic can also be routed through them and then counts as Private Data Transfer. — [Vercel docs: Static IPs](https://vercel.com/docs/networking/static-ips)
- [search snippet] Dedicated IPs come only through Secure Compute, which is Enterprise-only with custom pricing; "if a project uses Secure Compute, Static IPs will be ignored." — [Vercel docs: Static IPs](https://vercel.com/docs/networking/static-ips)
- Hobby users cannot buy Static IPs (third-party write-up). — [QuotaGuard blog](https://www.quotaguard.com/blog/vercel-static-outbound-ip-github-allowlisting)
- Repo requirement: live trading refuses to start unless the host's public IP matches `TB_EXPECTED_STATIC_IP`, and the architecture document maps this to the SEBI rule "Static IP for every API order". — `worker/thunderbot/compliance.py`, `docs/architecture.md` in this repo

### Inferences
- **Live trading from Vercel means Pro plus the add-on: about $120/month before usage** ($20 platform fee + $100 Static IPs), against the small Mumbai VPS the runbook currently prescribes. For paper trading and backtests the add-on is unnecessary.
- **"Shared VPC" needs a compliance check before use for orders.** If the static IP pair is shared with other Vercel customers in the region, whitelisting it at the broker means other tenants' traffic comes from the same address. Whether that satisfies the broker's and SEBI's static-IP expectation is outside what I could establish here.
- Because each region has its own pair, a `bom1`-only project would have one pair (primary and secondary), which matches Groww's "primary[,secondary]" whitelist shape used by `TB_EXPECTED_STATIC_IP`.

### Gaps
- **Availability of Static IPs in `bom1`** and the `bom1` Private Data Transfer rate were not found.
- Whether the IPs are shared across customers or reserved per project inside the shared VPC was not clarified by the snippets.
- The Secure Compute price (the brief's "about $6.5k/yr") was not confirmed; the docs snippet says only "custom pricing".
- An official sentence stating that Hobby deployments use dynamic IPs was not retrieved.
- The Static IPs page date and launch date were not visible.

## 7. Pro plan price in 2026

### Takeaway
Pro is reported as a $20/month platform fee that includes one deploying seat and $20 of monthly usage credit, with usage beyond the credit billed on demand; I could confirm this only through third-party summaries, not Vercel's pricing page text.

### Cited Findings
- Pro is described as a $20 monthly platform fee including one deploying seat and $20 in monthly infrastructure credit; additional deploying seats are $20 each per month and viewer seats are free; usage beyond the credit is billed on demand. — [makerkit.dev: Vercel cost in 2026](https://makerkit.dev/blog/tutorials/vercel-cost), [massivegrid.com: Vercel pricing explained 2026](https://massivegrid.com/blog/vercel-pricing-explained-2026/), [livemy.app: Vercel pricing explained](https://livemy.app/blog/vercel-pricing)
- [search snippet] Pro supports a hard spend limit that pauses projects at 100%. — [Vercel docs: Pro plan](https://vercel.com/docs/plans/pro-plan)
- [search snippet] Hobby includes 4 hours Active CPU, 360 GB-hrs provisioned memory and 1M invocations per month at no charge. — [Vercel pricing](https://vercel.com/pricing)

### Inferences
- **For Thunderbot the Pro bill would very likely be the flat $20/month**: at roughly 1,600 short invocations a month the function usage is far below what $20 of credit covers. This rests on the usage arithmetic in section 2 and on unit prices I did not retrieve, so treat it as an expectation, not a quote.
- **What Pro buys for this project**: per-minute cron schedules with per-minute precision (the one capability Hobby lacks that the intraday design needs), 800 s maximum duration, 4 GB memory, eligibility for Static IPs, and no fair-use ambiguity.
- **What Hobby can do**: host the dashboard and the Python function in `bom1`, run on-demand backtests up to 300 s, and fire one scheduled run per day at an imprecise time within an hour window.

### Gaps
- The official pricing page text, unit prices for Active CPU, provisioned memory and invocations beyond the included amounts, and any regional price difference for `bom1` were not retrieved: [Vercel pricing](https://vercel.com/pricing), [Vercel docs: Pro plan](https://vercel.com/docs/plans/pro-plan).
- Whether the $20 credit model described by third parties is unchanged as of November 2026 was not confirmed on a Vercel page.
