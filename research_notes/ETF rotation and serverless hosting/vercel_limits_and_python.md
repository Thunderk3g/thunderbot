# Vercel platform limits and behaviour for a scheduled Python worker next to a Next.js App Router dashboard (state as of November 2026)

All Vercel pages below were read on **2026-11-11**. Where a page exposes a `last_updated` field it is given in brackets as `[upd YYYY-MM-DD]`. Quotes are verbatim from the page unless marked as a summary. "Source code" links point at the `main` branch of `vercel/vercel` on GitHub as read on 2026-11-11 (behaviour inferred from code is labelled as such and is not a documented guarantee).

Important context changes versus what most 2024-2025 material says:

- Cron Jobs are now labelled a **legacy feature** that "will be migrated to Schedules in the future"; Schedules is in public beta.
- Fluid compute is the default; current docs publish **only** Fluid limits (Hobby 300 s).
- Python is **GA** (15 Oct 2026); the `/api` directory model is documented as being for "existing projects"; the recommended way to combine Next.js + Python is **Services** (beta, all plans).
- Python bundle limit is **500 MB** (since 24 Feb 2026).
- Cron limit is **100 per project on every plan** (since 20 Jan 2026), but Hobby is still **once per day**.

---

## 1. Cron Jobs: limits on Hobby vs Pro vs Enterprise, configuration, invocation, security, reliability

### Takeaway
As of Nov 2026 every plan gets 100 cron jobs per project, but Hobby crons may only fire **once per day** and anywhere inside the scheduled hour (±59 min); Pro/Enterprise can fire every minute with per-minute precision. Crons are a plain HTTP GET (UA `vercel-cron/1.0`, optional `Authorization: Bearer <CRON_SECRET>`) to the production deployment only, in UTC, with **no retries**, best-effort delivery, and possible duplicates. Vercel now calls Cron Jobs "legacy" and offers **Schedules (beta)**, which on Hobby allows every 15 minutes (with a 15-minute jitter window and a 5,000-runs-per-period cap).

### Cited Findings

**Limits table (current)**
- Table verbatim: Hobby "100 cron jobs" / "Once per day" / "Per-hour (±59 min)"; Pro "100 cron jobs" / "Once per minute" / "Per-minute"; Enterprise "100 cron jobs" / "Once per minute" / "Per-minute". Column headers: "Number of cron jobs per project", "Minimum interval", "Scheduling precision". [upd 2026-07-15] — [Usage & Pricing for Cron Jobs](https://vercel.com/docs/cron-jobs/usage-and-pricing)
- "Hobby accounts are limited to cron jobs that run **once per day**. Cron expressions that would run more frequently will fail during deployment." Deploy error text: "*Hobby accounts are limited to daily cron jobs. This cron expression would run more than once per day.*" — [Usage & Pricing for Cron Jobs](https://vercel.com/docs/cron-jobs/usage-and-pricing)
- Hobby timing: "Vercel cannot assure a timely cron job invocation. For example, a cron job configured as `0 1 * * *` (every day at 1 am) will trigger anywhere between 1:00 am and 1:59 am." — [Usage & Pricing for Cron Jobs](https://vercel.com/docs/cron-jobs/usage-and-pricing)
- Pro/Enterprise timing: "For all other teams, cron jobs will be invoked within the minute specified. For instance, the expression `5 8 * * *` would trigger an invocation between `08:05:00` and `08:05:59`." [upd 2026-08-11] — [Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs)
- General limits table also lists "Cron Jobs (per project)": Hobby 100*, Pro 100, Enterprise 100. [upd 2026-09-16] — [Limits](https://vercel.com/docs/limits)
- "Disabled cron jobs will still be listed and will count towards your cron jobs limits". — [Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs)

**2026 change (confirming the "100 per project" question)**
- Changelog published **20 January 2026** (summary, not verbatim): per-team cron limits were removed and the per-project limit raised to 100 on all plans; previously every plan was capped at 20 cron jobs per project with per-team caps of 2 (Hobby), 40 (Pro), 100 (Enterprise). — [Cron jobs now support 100 per project on every plan](https://vercel.com/changelog/cron-jobs-now-support-100-per-project-on-every-plan)
- Historical baseline: at GA on 15 Nov 2023, limits were per account: Hobby 2, Pro 40, Enterprise 100. The same post says "We also added support for Deployment Protection and Instant Rollback." — [Vercel Cron Jobs are now generally available](https://vercel.com/changelog/vercel-cron-jobs-are-now-generally-available)
- The 2026 change did **not** relax the Hobby once-per-day rule (current table above still says "Once per day"). — [Usage & Pricing for Cron Jobs](https://vercel.com/docs/cron-jobs/usage-and-pricing)

**Configuration**
- Configured in `vercel.json` under `crons` (array of `{ "path", "schedule" }`) or via the Build Output API. `crons` is "Used to configure cron jobs for the production deployment of a project." Limits: "A maximum of string length of 512 for the `path` value" and "256 for the `schedule` value"; `path` "Must start with `/`". [upd 2026-08-14] — [vercel.json reference: crons](https://vercel.com/docs/project-configuration/vercel-json#crons)
- Cron expression: 5 fields (minute, hour, day-of-month, month, day-of-week 0-6 Sun-Sat). Limitations verbatim: "Cron jobs on Vercel do not support alternative expressions like `MON`, `SUN`, `JAN`, or `DEC`"; "You cannot configure both day of the month and day of the week at the same time. When one has a value, the other must be `*`"; "The timezone is always UTC". [upd 2026-09-16] — [Cron Jobs](https://vercel.com/docs/cron-jobs)
- Updating/deleting a cron requires editing `vercel.json` and redeploying; a project-level "Disable Cron Jobs" button exists and persists across promotions and rollbacks. — [Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs)

**How a cron invokes the function**
- "To trigger a cron job, Vercel makes an HTTP GET request to your project's production deployment URL, using the `path` provided in your project's `vercel.json` file. For example, Vercel might request the following endpoint to trigger a cron job: `https://*.vercel.app/api/cron`." — [Cron Jobs](https://vercel.com/docs/cron-jobs)
- "Vercel Functions triggered by a cron job on Vercel will always contain `vercel-cron/1.0` as the user agent. Each request also includes an `x-vercel-cron-schedule` header containing the cron expression that triggered the invocation". — [Cron Jobs](https://vercel.com/docs/cron-jobs)
- Production only: "Cron jobs run only on production deployments." (troubleshooting table); "Vercel invokes cron jobs on the production deployment serving your production domain". — [Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs)
- No local emulation: "There is currently no support for `vercel dev`, `next dev`, or other framework-native local development servers." Test by requesting the endpoint directly. — [Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs)
- Redirects are not followed: "Cron jobs do not follow redirects. When a cron-triggered endpoint returns a 3xx redirect status code, the job completes without further requests." Next.js `trailingSlash` is named as a common cause; fix by putting the trailing slash in `path`. — [Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs)
- Nonexistent path: "it generates a 404 error. However, Vercel still executes your cron job." — [Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs)
- "when cron jobs respond with a redirect or a cached response, they will not be shown in the logs." For Next.js route handlers the docs suggest `export const dynamic = 'force-dynamic';`. — [Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs)
- A WAF custom rule can block a cron before it reaches the function ("Review your firewall rules and exclude the cron job's path from rules that deny or challenge traffic"). — [Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs)

**Securing**
- "It is possible to secure your cron job invocations by adding an environment variable called `CRON_SECRET` to your Vercel project. We recommend using a random string of at least 16 characters". "The value of the variable will be automatically sent as an `Authorization` header when Vercel invokes your cron job." "The `authorization` header will have the `Bearer` prefix for the value." — [Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs)
- Use header-safe characters only (letters/numbers; no line breaks or leading/trailing spaces), otherwise "your endpoint returns `401` for every invocation." — [Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs)
- The secret is captured per deployment at build time: "Editing `CRON_SECRET` in project settings changes nothing until your next deployment." Rollback restores the target deployment's copy. — [Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs)
- The cron path is otherwise a public URL: "A Cron Job path is a public URL, so anyone can call it unless you check `CRON_SECRET`." [upd 2026-10-09] — [Migrating from Cron Jobs to Schedules](https://vercel.com/docs/schedules/migrate-from-cron-jobs)

**Reliability: retries, duplicates, concurrency**
- "Vercel will not retry an invocation if a cron job fails." — [Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs)
- "Cron job delivery is best effort. Most invocations run as scheduled, but occasional transient network errors can prevent a request from reaching your function. In those cases, your function does not execute, and no runtime log is created for that scheduled run." — [Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs)
- "Cron delivery can also occasionally invoke the same scheduled run more than once. Because of this, cron jobs should be resilient to both missed runs and duplicate runs." Recommended: idempotent, reconciliation-based operations; unique IDs; "Query and process all work since the last successful run". — [Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs)
- Overlap: "If your cron job runs longer than the interval between invocations, Vercel can trigger a second instance while the first is still running." Docs recommend a lock (Redis distributed lock given as example). — [Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs)
- During promotion/rollback "A run scheduled inside that gap can still reach the deployment you just moved away from, or it can be skipped." — [Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs)
- "Creating a new deployment will not interrupt your running cron jobs; they will continue until they finish." — [Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs)

**Usage accounting**
- "Cron jobs invoke Vercel Functions. This means the same usage and pricing limits will apply." and "Cron jobs are included in **all plans**. You use a function to invoke a cron job, and therefore usage and pricing limits for these functions apply to all cron job executions". — [Usage & Pricing for Cron Jobs](https://vercel.com/docs/cron-jobs/usage-and-pricing)
- "The duration limits for Cron jobs are identical to those of Vercel Functions." — [Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs)

**Schedules (successor, public beta) - materially changes what Hobby can do**
- Banner on every cron page: "Cron Jobs are a legacy feature and will be migrated to Schedules in the future. Schedules include timezones, private function and queue targets. You can also create schedules at runtime." — [Cron Jobs](https://vercel.com/docs/cron-jobs)
- "Schedules are in beta, and these limits may change before general availability." Limits by plan: Schedules per team 1,000 (Hobby) / 10,000 (Pro) / 100,000 (Enterprise); Jitter window "Always 15 minutes" (Hobby) vs "1 to 15 minutes. Defaults to 1 minute." (Pro/Ent); Most frequent cron schedule "Every 15 minutes" (Hobby) vs "Every minute, with a 1-minute jitter window"; payload 16 KB. (This page's `last_updated` metadata reads 2018-10-20, which is obviously wrong; content is current beta docs.) — [Schedules Limits](https://vercel.com/docs/schedules/limits)
- Hobby caps: "A deployment can declare up to 100 static schedules in `vercel.json`"; "Each billing period, a team can create up to 500 dynamic schedules and run its schedules up to 5,000 times. Scheduled and manual runs both count toward the run limit." Over the limit, scheduled runs are skipped until the next period. — [Schedules Limits](https://vercel.com/docs/schedules/limits)
- Timing comparison table: Hobby Cron Jobs "At most once per day, at any time within the scheduled hour" vs Hobby Schedules "At most once every 15 minutes, within a 15-minute jitter window"; Pro/Ent Cron Jobs "At the scheduled minute" vs Schedules "Within the jitter window, which defaults to 1 minute and can be set from 1 to 15 minutes". — [Migrating from Cron Jobs to Schedules](https://vercel.com/docs/schedules/migrate-from-cron-jobs)
- Path-target schedules call the route like a cron: UA `vercel-cron/1.0`, `x-vercel-cron-schedule` header, and "If you set `CRON_SECRET`, the `Authorization` header contains `Bearer <CRON_SECRET>`". But "Path schedules send a `POST` request by default, but Cron Jobs send `GET`. Set `requestMethod` to `GET` when you migrate". If both `crons` and `schedules` entries are kept "your route runs twice for each occurrence." — [Migrating from Cron Jobs to Schedules](https://vercel.com/docs/schedules/migrate-from-cron-jobs)
- Schedule syntax: `"schedules": { "<name>": { "schedule": "0 9 * * *", "path": "/api/daily-report", "requestMethod": "GET", "timezone": "America/New_York", "jitter": 5 } }`; `timezone` is an IANA name defaulting to UTC; exactly one target of `function` / `path` / `topic`; `service` may name the Service owning a `function`. Example `0 9 * * 1-5` (weekdays) is valid; named days/months are not. — [Schedules Configuration Reference](https://vercel.com/docs/schedules/configuration)
- Schedules can also "Run schedules in Preview branches and custom environments", be enabled/disabled/run without redeploying, and show execution history. — [Migrating from Cron Jobs to Schedules](https://vercel.com/docs/schedules/migrate-from-cron-jobs)
- Private "function" targets require wrapping the handler with `handleSchedule` from the `@vercel/schedules` (JS) package and a `schedule/v1beta` trigger; such a function "has no public URL, and only Vercel's scheduler can invoke" it. — [Migrating from Cron Jobs to Schedules](https://vercel.com/docs/schedules/migrate-from-cron-jobs); [Schedules Configuration Reference](https://vercel.com/docs/schedules/configuration)

### Inferences
- On Hobby, legacy `crons` cannot express an intraday trading cadence (e.g. "every 15 min during NSE hours" or even "09:20 and 15:20 IST" as two entries is allowed only if each expression fires once per day - two separate once-daily cron entries for the same path are permitted by the 100-per-project limit, and the `x-vercel-cron-schedule` header tells them apart; but each still lands anywhere in its hour). Precise or frequent runs need Pro crons, Schedules beta (15-minute granularity + 15-minute jitter on Hobby), or an external scheduler hitting the function over HTTPS.
- Because Hobby timing is "anywhere within the hour" and delivery is best-effort with possible duplicates and no retries, the worker must be idempotent and decide what to do from wall-clock/market state plus a "last successful run" marker in Supabase, not from the fact that it was invoked.
- UTC only (for `crons`): an IST schedule must be converted (IST = UTC+5:30, no DST), e.g. 15:20 IST = `50 9 * * 1-5`. Schedules beta would allow `"timezone": "Asia/Kolkata"`.
- 5,000 Hobby schedule runs per billing period is ample for one worker even at every 15 minutes around the clock (~2,900/month).

### Gaps
- Whether Vercel's own cron requests bypass **Deployment Protection** (Vercel Authentication) is not documented in the current cron or protection docs. The only statement found is the 2023 GA changelog line "We also added support for Deployment Protection". Under the default Standard Protection, production domains are not protected, so this only matters if "All Deployments" protection is switched on. Needs a live test.
- No doc states a retry or "late run" policy for Schedules in the pages read (the `concepts` page was not fetched); whether a Python function can be a private `function` target (the documented wrapper is the JS `@vercel/schedules` SDK) was not confirmed. Path targets work with any runtime.
- No date is published for when legacy Cron Jobs will be migrated/retired ("in the future").

---

## 2. Functions: duration, memory, bundle size, body size, Hobby quotas/fair use, region pinning

### Takeaway
With Fluid compute (default for all projects created since 23 Apr 2025), Hobby functions get **300 s default and max**, **2 GB / 1 vCPU**, and Pro gets 300 s default / **800 s** max (1800 s beta) and up to 4 GB / 2 vCPU. Python bundles may be **500 MB** uncompressed (250 MB for other runtimes; 5 GB "large functions" beta), request/response bodies 4.5 MB. Hobby includes 4 Active-CPU hours, 360 GB-hours of provisioned memory and 1M invocations a month, is non-commercial only, and can pin functions to **one** region of your choice (so `bom1` is allowed).

### Cited Findings

**Maximum duration**
- Summary row: "Hobby: 300s default and maximum. Pro and Enterprise: 300s default, 800s maximum, and 1800s extended maximum Beta." Table for "Node.js, Bun, and Python runtimes": Hobby 300s/300s/-; Pro 300s/800s/1800s (Beta); Enterprise 300s/800s/1800s (Beta). [upd 2026-08-24] — [Vercel Functions Limits](https://vercel.com/docs/functions/limitations)
- On timeout "a 504 error code (`FUNCTION_INVOCATION_TIMEOUT`) is returned." — [Vercel Functions Limits](https://vercel.com/docs/functions/limitations)
- "As of April 23, 2025, fluid compute is enabled by default for new projects." Can be toggled per project in Settings > Functions, or per deployment with `"fluid": true` in `vercel.json`. Fluid supports Node.js, Python, Edge, Bun, Rust. [upd 2026-08-24] — [Fluid compute](https://vercel.com/docs/fluid-compute)
- History: changelog of **25 June 2025** (summary) raised Fluid defaults to 300 s on all plans; Hobby was previously 60 s default/max, Pro/Enterprise previously 90 s default; Standard instance became 1 vCPU / 2 GB (was 1.7 GB), Performance 2 vCPU / 4 GB; "Basic" CPU removed and Hobby moved to Standard. — [Higher defaults and limits for Vercel Functions running Fluid compute](https://vercel.com/changelog/higher-defaults-and-limits-for-vercel-functions-running-fluid-compute)
- 1800 s extended maximum is beta, Pro/Enterprise only, per-function configuration only, and supported for `python3.12`, `python3.13`, `python3.14` (plus Node 22/24/26, Bun 1.x). [upd 2026-08-24] — [Configuring Maximum Duration](https://vercel.com/docs/functions/configuring-functions/duration)
- For unlimited-duration work Vercel points to Workflows ("pause, resume, and maintain state for minutes to months"). — [Vercel Functions Limits](https://vercel.com/docs/functions/limitations)

**How `maxDuration` is configured**
- Next.js App Router route handler: `export const maxDuration = 5;` in `app/api/.../route.ts`. — [Configuring Maximum Duration](https://vercel.com/docs/functions/configuring-functions/duration)
- "Other Frameworks and runtimes, Next.js versions older than 13.5, Rust, Go, Python, or Ruby": "configure the `maxDuration` property of the `functions` object in your `vercel.json` file", keyed by a glob such as `"api/*.js"`; extended example uses `"api/long-task.py": { "maxDuration": 1800 }`. "The order in which you specify file patterns is important." — [Configuring Maximum Duration](https://vercel.com/docs/functions/configuring-functions/duration)
- `maxDuration`: "Set an integer number of seconds between `1` and your plan's maximum limit... `\"max\"` is also accepted and resolves to your plan's maximum at deploy time". — [vercel.json reference: functions](https://vercel.com/docs/project-configuration/vercel-json#functions)
- Precedence: function code > `vercel.json` > dashboard > Fluid defaults. A project default can also be set in Settings > Functions > Function Max Duration. — [Fluid compute](https://vercel.com/docs/fluid-compute); [Configuring Maximum Duration](https://vercel.com/docs/functions/configuring-functions/duration)

**Memory / CPU**
- Table: Hobby default "2 GB / 1 vCPU", maximum "2 GB / 1 vCPU"; Pro/Enterprise default "2 GB / 1 vCPU", maximum "4 GB / 2 vCPU". Pro/Enterprise can change the default in the dashboard. — [Vercel Functions Limits](https://vercel.com/docs/functions/limitations)
- "`memory`: Memory cannot be set in `vercel.json` with Fluid compute enabled. Instead set it in the **Functions** section in your project dashboard". — [vercel.json reference: functions](https://vercel.com/docs/project-configuration/vercel-json#functions)

**Bundle size**
- "For Vercel Functions, the maximum uncompressed size is **250 MB** including layers... For Python functions, the maximum uncompressed size is **500 MB**." — [Vercel Functions Limits](https://vercel.com/docs/functions/limitations)
- "The standard Python bundle size limit is **500 MB** uncompressed. Large Functions support Python bundles up to **5 GB** on Fluid compute when enabled (public beta)." [upd 2026-08-12] — [Python runtime](https://vercel.com/docs/functions/runtimes/python)
- Changelog published **24 February 2026** (summary): Python Vercel Functions bundle limit raised from 250 MB to 500 MB uncompressed; the page does not state any plan restriction. — [Python Vercel Functions bundle size limit increased to 500MB](https://vercel.com/changelog/python-vercel-functions-bundle-size-limit-increased-to-500mb)
- Large functions (beta): up to 5 GB, Node.js/Bun/Python, "require fluid compute with Active CPU enabled"; "New projects are eligible for large functions by default. For existing projects, opt in by setting the `VERCEL_SUPPORT_LARGE_FUNCTIONS` environment variable" (`1` on, `0` off). "Vercel only uses the large functions beta for Functions that exceed the standard bundle size limit." — [Vercel Functions Limits](https://vercel.com/docs/functions/limitations)
- Debugging size: set env `VERCEL_ANALYZE_BUILD_OUTPUT=1` and redeploy; build logs list each function's uncompressed size and largest files. — [Vercel Functions Limits](https://vercel.com/docs/functions/limitations)

**Request/response body and other runtime limits**
- "The maximum payload size for the request body or the response body of a Vercel Function is **4.5 MB**. The response body limit doesn't apply to streamed responses." Over-limit returns 413 `FUNCTION_PAYLOAD_TOO_LARGE`. — [Vercel Functions Limits](https://vercel.com/docs/functions/limitations)
- File descriptors: "1,024 shared across concurrent executions (including runtime usage)". — [Vercel Functions Limits](https://vercel.com/docs/functions/limitations)
- Filesystem: "Read-only filesystem with writable `/tmp` scratch space up to 500 MB". [upd 2026-08-12] — [Runtimes](https://vercel.com/docs/functions/runtimes)
- Archiving: functions not invoked are archived "Within 2 weeks for Production Deployments" / "Within 3 days for Preview Deployments"; unarchiving "can make the initial cold start time at least 1 second longer than usual." — [Runtimes](https://vercel.com/docs/functions/runtimes)
- `SIGTERM` is delivered before termination on the Python runtime; "Your code can run for up to 500 milliseconds... after receiving a `SIGTERM` signal." [upd 2026-08-11] — [Functions API Reference](https://vercel.com/docs/functions/functions-api-reference)
- Environment variables: total 64 KB per deployment for Python and other runtimes; max 1000 per environment. — [Limits](https://vercel.com/docs/limits)
- Hobby function count: with Next.js, dynamic code is bundled into few functions; "When using other frameworks, or Vercel Functions directly without a framework, every API maps directly to one Vercel Function. For example, having five files inside `api/` would create five Vercel Functions. For Hobby, this approach is limited to 12 Vercel Functions per deployment." — [Runtimes](https://vercel.com/docs/functions/runtimes)

**Hobby included usage, fair use, non-commercial restriction**
- Hobby included per month: Active CPU "4 CPU-hrs"; Provisioned Memory "360 GB-hrs"; Function Invocations "First 1,000,000"; Fast Data Transfer first 100 GB; Fast Origin Transfer first 10 GB; CDN Requests first 1,000,000. [upd 2026-09-14] — [Vercel Hobby Plan](https://vercel.com/docs/plans/hobby)
- Active CPU = "CPU time your code actively consumes"; "You are only billed during actual code execution and not during I/O operations". Provisioned Memory = memory x instance lifetime, "Continues billing while handling requests, even during I/O operations". Invocations count "regardless of request success or failure". [upd 2026-06-16] — [Fluid compute pricing](https://vercel.com/docs/functions/usage-and-pricing)
- Exceeding Hobby limits: "In most cases, if you exceed your usage limits on the Hobby plan, you will have to wait until 30 days have passed before you can use the feature again." — [Vercel Hobby Plan](https://vercel.com/docs/plans/hobby). Also: "On the Hobby plan you **will not pay for any additional usage**. However, your account may be paused if you do exceed the limits." — [Legacy Usage & Pricing for Functions](https://vercel.com/docs/functions/usage-and-pricing/legacy-pricing)
- Commercial restriction verbatim: "**Hobby teams** are restricted to non-commercial personal use only. All commercial usage of the platform requires either a Pro or Enterprise plan. Commercial usage is defined as any Deployment that is used for the purpose of financial gain of **anyone** involved in **any part of the production** of the project, including a paid employee or consultant writing the code." Listed examples: requesting/processing payment from visitors, advertising the sale of a product or service, receiving payment to create/update/host the site, affiliate linking as primary purpose, advertisements. "Asking for Donations **does not** fall under commercial usage." "If you are unsure... contact the Vercel Support team". [upd 2026-09-14] — [Fair Use Guidelines](https://vercel.com/docs/limits/fair-use-guidelines)
- "Circumventing or otherwise misusing Vercel's limits or usage guidelines is a violation of our fair use guidelines." — [Fair Use Guidelines](https://vercel.com/docs/limits/fair-use-guidelines)
- Pro pricing: $20/month with "a $20 included credit to use across resources"; developer seat $20/month. Pro on-demand rates in Mumbai: Active CPU $0.140/hour, Provisioned Memory $0.0116/GB-hr; invocations $0.60 per million. — [Vercel Pricing](https://vercel.com/pricing); [Fluid compute pricing](https://vercel.com/docs/functions/usage-and-pricing); [Mumbai (bom1) pricing](https://vercel.com/docs/pricing/regional-pricing/bom1)

**Regions / pinning to Mumbai (bom1)**
- `bom1` = `ap-south-1`, "Mumbai, India" is one of 19 compute-capable regions. [upd 2026-08-11] — [Global network and regions](https://vercel.com/docs/regions)
- "By default, Vercel Functions execute in *Washington, D.C., USA* (`iad1`) **for all new projects**... You can set a new default region through your project's settings". Ways to set: dashboard (Settings > Functions > Function Regions), `vercel.json` `"regions": ["sfo1"]`, CLI `vercel --regions sfo1`, or per-function `functions["api/x"].regions`. [upd 2026-08-11] — [Configuring regions for Vercel Functions](https://vercel.com/docs/functions/configuring-functions/region)
- Plan limits table: Hobby "Single region"; Pro "5 regions"; Enterprise "All regions". "Deploying to more regions than your plan allows causes the deployment to fail before the build step." — [Configuring regions for Vercel Functions](https://vercel.com/docs/functions/configuring-functions/region)
- Conflict: the Fluid compute page's table says multi-region functions on Pro are "Up to 3" (and a changelog is titled "Pro customers can now configure up to 3 regions"), whereas the region page says "5 regions". — [Fluid compute](https://vercel.com/docs/fluid-compute); contradicted by [Configuring regions](https://vercel.com/docs/functions/configuring-functions/region)
- Middleware is not pinned: "Vercel deploys Routing Middleware to all regions by default, regardless of your region settings. On the Hobby plan, Routing Middleware runs in fewer regions." — [Configuring regions for Vercel Functions](https://vercel.com/docs/functions/configuring-functions/region)
- Region failover: "In the event of regional downtime, application traffic is automatically rerouted to the next closest region"; configurable function failover regions are Enterprise only. — [Global network and regions](https://vercel.com/docs/regions)

### Inferences
- A once- or few-times-daily worker that mostly waits on HTTPS (broker API, Supabase) uses almost no Active CPU; the binding Hobby quota is Provisioned Memory: 2 GB x wall-clock. A 60-second run costs 2 GB x 60 s = 0.033 GB-hr; 360 GB-hrs/month allows roughly 10,800 such minute-long runs, i.e. far more than any plausible schedule. The dashboard's own traffic shares the same quotas.
- A single region on Hobby can be `bom1`: the limit is on the *number* of regions, not which one. Put `"regions": ["bom1"]` in `dashboard/vercel.json` (or set it in the dashboard) so both the Next.js functions and the Python function run in Mumbai.
- The literal Hobby wording ("used for the purpose of financial gain of anyone involved in any part of the production of the project") can be read to cover a personal trading bot even though every listed example concerns websites taking money from visitors. Vercel's docs do not address personal trading/automation explicitly; treat Hobby eligibility as ambiguous and either ask Vercel Support or budget for Pro ($20/month) if the bot trades real money.
- The 12-functions-per-deployment Hobby cap applies to files under `api/` (one function per `.py` file); keep the Python worker to one or a few entrypoint files and put shared code in importable modules.

### Gaps
- **Non-Fluid (legacy) limits could not be confirmed from any current Vercel page.** The figures in the brief (Hobby 10 s default / 60 s max; Pro 15 s default / 300 s max; Hobby 1024 MB) do not appear in today's docs: the limits, duration, legacy-pricing and pricing pages only publish Fluid numbers, and the June 2025 changelog only gives the previous *Fluid* defaults (Hobby 60 s, Pro 90 s). The Wayback Machine was not reachable from the research environment. Since Fluid is on by default for any project created after 23 Apr 2025, the practical design number is 300 s on Hobby; if someone disables Fluid, expect much lower legacy limits (not verified here).
- Vercel does not publish the legacy "100 GB-hours" Hobby allowance any more; the current Hobby allowance is expressed only as 4 CPU-hrs / 360 GB-hrs / 1M invocations.
- CPU architecture of the Python function runtime (x86_64 vs arm64) is not stated on the pages read.
- Whether the Pro multi-region cap is 3 or 5 is inconsistent across docs (irrelevant for a single-region `bom1` design).

---

## 3. Python runtime alongside Next.js in one project

### Takeaway
Yes: Python functions can live in the same Vercel project as a Next.js App Router app. There are two supported shapes in Nov 2026: (a) the classic zero-config **`api/*.py` directory at the project root** (i.e. `dashboard/api/worker.py` when Root Directory = `dashboard`), served at `/api/worker`, which Vercel now documents as supported "for existing projects"; and (b) **Vercel Services** (beta, all plans), the officially recommended way to pair a Next.js frontend with a Python backend, configured with `services` + service-targeted `rewrites` in `vercel.json`. Precedence when a Next.js route and a Python file claim the same `/api/...` path is **not documented** - avoid the collision.

### Cited Findings

**Status of Python and the `/api` directory**
- Python on Vercel went GA on **15 October 2026** (summary): FastAPI, Flask and Django are auto-detected; `uv` and `pyproject.toml` supported; Vercel Services deploys "a frontend and backends together in one project". — [Python on Vercel is now generally available](https://vercel.com/changelog/python-on-vercel-is-now-generally-available)
- "Vercel supports existing projects that define file-based Python functions in an `/api` directory." "For new Python applications, use a framework preset for FastAPI, Flask, or Django. To run a Python backend alongside another framework, use Services." [upd 2026-08-12] — [Python Functions in the /api Directory](https://vercel.com/docs/functions/runtimes/python/api-directory)
- Routing: "Without a detected Python framework preset, each `.py` file inside `/api` becomes a separate Vercel Function. Vercel serves each function at its file path. For example, `api/index.py` serves `/api`, and `api/users.py` serves `/api/users`." — [Python Functions in the /api Directory](https://vercel.com/docs/functions/runtimes/python/api-directory)
- "A Python framework preset takes precedence over file-based functions. When Vercel detects a framework preset, the framework application handles all requests, and files under `/api` don't become separate Vercel Functions." — [Python Functions in the /api Directory](https://vercel.com/docs/functions/runtimes/python/api-directory)
- `vercel.json` reference: "For all officially supported runtimes, the only requirement is to create an `api` directory at the root of your project directory, placing your Vercel functions inside." — [vercel.json reference: functions](https://vercel.com/docs/project-configuration/vercel-json#functions)

**Coexistence with Next.js (from Vercel's builder source, not prose docs)**
- Vercel's zero-config builder detection emits this warning when a Next.js project also has JS files in `api/`: "When using Next.js, it is recommended to place JavaScript Functions inside of the `pages/api` (provided by Next.js) directory instead of `api` (provided by Vercel). Other languages (Python, Go, etc) should still go in the `api` directory." — [vercel/vercel `packages/fs-detectors/src/detect-builders.ts`](https://github.com/vercel/vercel/blob/main/packages/fs-detectors/src/detect-builders.ts)
- Same file: for Next.js projects the generic `^/api(/.*)?$` 404 catch-all is skipped, with the comment "Skip for Next.js: it serves /api (Pages + App Router) and 404s unmatched paths". And `functions` keys in `vercel.json` are validated: with the Next.js builder, keys starting with `pages/`, `src/pages`, `app/`, `src/app/`, `middleware` are accepted for Next.js, other keys must match a file handled by an `api/` builder or the build fails with `unused_function`. — [vercel/vercel `detect-builders.ts`](https://github.com/vercel/vercel/blob/main/packages/fs-detectors/src/detect-builders.ts)
- A widely used community starter demonstrates the pattern in production: Next.js `app/` plus `api/index.py` (FastAPI) and `requirements.txt` at the repo root, with `next.config.js` rewrites sending `/api/py/:path*` to `http://127.0.0.1:8000/api/py/:path*` in development and to `/api/` in production (so one FastAPI function at `api/index.py` handles every `/api/py/*` path). It has no `vercel.json`. Repo pins `next ^14.2.13`, `fastapi==0.115.0`. — [digitros/nextjs-fastapi `next.config.js`](https://github.com/digitros/nextjs-fastapi/blob/main/next.config.js)

**Official hybrid template today (Services)**
- The current official "Next.js FastAPI Starter" lives at `vercel/examples/python/nextjs-fastapi` with layout `frontend/`, `backend/`, `vercel.json`, and this config: `"services": { "frontend": { "root": "frontend/", "framework": "nextjs" }, "backend": { "root": "backend/", "entrypoint": "main:app" } }`, `"rewrites": [ { "source": "/svc/api/:path*", "destination": { "service": "backend" } }, { "source": "/(.*)", "destination": { "service": "frontend" } } ]`. Local dev: `vercel dev`. — [Next.js FastAPI Starter template](https://vercel.com/templates/fast-api/next-js-fastapi-starter); [vercel/examples python/nextjs-fastapi](https://github.com/vercel/examples/tree/main/python/nextjs-fastapi)
- "Services are available in Beta on all plans". "A service is internal by default and will not be routable from the Internet unless you expose it. To route a service publicly, include a top-level rewrite rule that targets the service as `destination`". [upd 2026-08-10] — [Services](https://vercel.com/docs/services)
- In services mode, "`functions`, `installCommand`, `buildCommand`, `devCommand`, `ignoreCommand`, `outputDirectory` and `framework` keys should be moved into the relevant service." Public routing (rewrites, redirects, firewall, Deployment Protection) stays top-level and applies across services. — [Services](https://vercel.com/docs/services)
- Routing semantics: top-level rewrites are evaluated in order, first match wins; "The service receives the original request path. `GET /api/users` reaches `my_backend` as `/api/users`, not `/users`." "Routing into a service is final. If no route matches inside the service, Vercel does not fall back to your other top-level rewrites." [upd 2026-06-30] — [Services routing](https://vercel.com/docs/services/routing)
- A service can stay private and be called from Next.js server code via a binding (Vercel injects the URL as an env var, e.g. `BACKEND_URL`); the Oct 2026 KB guide uses exactly this (Next.js Route Handler `/api/backend/*` forwards to a private FastAPI service; only rewrite is `/(.*)` to the frontend). — [How to deploy a Python backend with Vercel Services](https://vercel.com/kb/guide/python-backend-on-vercel); [Services](https://vercel.com/docs/services)
- Services billing: "Each service runs on Vercel's compute and is billed the same as Vercel Functions"; binding calls are "Service Requests" (Hobby: first 1,000,000 included); "The same function limits apply to each service". [upd 2026-08-31] — [Services Pricing and Limits](https://vercel.com/docs/services/pricing)
- A schedule can target a function inside a service (`"service": "worker", "function": "index"`), though "`vercel dev` doesn't run schedules that target a function in a service yet." — [Schedules Configuration Reference](https://vercel.com/docs/schedules/configuration)

**Python versions, dependencies, handler shapes**
- "The available versions are: **3.12** (default), **3.13**, **3.14**". Set with `pyproject.toml`, `.python-version`, or `Pipfile.lock`; unsupported/undefined falls back to the default. — [Python runtime](https://vercel.com/docs/functions/runtimes/python)
- "Define dependencies in `pyproject.toml` (with or without a `uv.lock`), `requirements.txt`, or a `Pipfile` with a corresponding `Pipfile.lock`." — [Python runtime](https://vercel.com/docs/functions/runtimes/python)
- `/api` file handlers: "Each `.py` file must define one of these top-level names: `app` for an ASGI or WSGI application; `application` for a WSGI application; `handler` for a class that inherits from `BaseHTTPRequestHandler`", with the canonical `class handler(BaseHTTPRequestHandler): def do_GET(self): ...` example. — [Python Functions in the /api Directory](https://vercel.com/docs/functions/runtimes/python/api-directory)
- Framework-preset entrypoints (when the project itself is a Python app or a Service): `app.py`, `index.py`, `server.py`, `main.py`, `wsgi.py`, or `asgi.py` (also inside `src/` or `app/`), or `[tool.vercel] entrypoint = "my_package.api:app"` in `pyproject.toml`; the file must expose `app` (or `application`). Framework is detected from a matching dependency in `requirements.txt`, `pyproject.toml`, or `Pipfile`. — [Python runtime](https://vercel.com/docs/functions/runtimes/python)
- Streaming responses are supported on the Python runtime. — [Python runtime](https://vercel.com/docs/functions/runtimes/python)
- Build image is Amazon Linux 2023 with Python 3.14, 3.13, 3.12 preinstalled. [upd 2026-08-11] — [Build image overview](https://vercel.com/docs/builds/build-image)

**What gets bundled; including shared local Python code**
- "By default, Python Vercel Functions include all files from your project that are reachable at build time. There is no automatic tree-shaking for Python." Bytecode (`.pyc`) is precompiled into the bundle "when space allows". — [Python runtime](https://vercel.com/docs/functions/runtimes/python)
- Builder source confirms the default: it globs `**` from the work path and excludes only a fixed list: `.git/**`, `.gitignore`, `.vercel/**`, `.pnpm-store/**`, `**/node_modules/**`, `**/.next/**`, `**/.nuxt/**`, `**/.venv/**`, `**/venv/**`, `**/__pycache__/**`, `**/.mypy_cache/**`, `**/.ruff_cache/**`, `**/public/**`, and JS lockfiles, plus any `excludeFiles`; `includeFiles` globs are resolved relative to the same work path. — [vercel/vercel `packages/python/src/index.ts`](https://github.com/vercel/vercel/blob/main/packages/python/src/index.ts)
- `includeFiles` / `excludeFiles` are per-function glob options under `functions` in `vercel.json` ("Not supported in Next.js, instead use `outputFileTracingIncludes`" - that caveat is about Next.js-built functions). The glob is "relative to your project root". Example: `"functions": { "api/**/*.py": { "excludeFiles": "{tests/**,...}" } }`. — [vercel.json reference: functions](https://vercel.com/docs/project-configuration/vercel-json#functions); [Python Functions in the /api Directory](https://vercel.com/docs/functions/runtimes/python/api-directory)
- "Python uses the current working directory when you pass a relative path to `open()`. The working directory is the base of your project, not the directory containing the file." — [Python runtime](https://vercel.com/docs/functions/runtimes/python)

**Root Directory and sibling directories**
- Root Directory: "By default, your build can access files outside of that directory, and your commands can use `..` to move up a level. If you turn off **Include files outside the root directory in the Build Step** in the **Root Directory** settings, your build cannot access files outside of that directory". [upd 2026-08-28] — [Configuring a Build](https://vercel.com/docs/builds/configure-a-build)
- Install Command note: "If you're using Vercel functions defined in the natively supported `api` directory, a different Install Command will be used depending on the language of the Vercel Function... You cannot customize the Install Command for other runtimes" (only Node.js functions accept a per-function `installCommand`). — [Configuring a Build](https://vercel.com/docs/builds/configure-a-build)
- Hobby cannot connect a project to a Git repository owned by a Git organization. — [Limits](https://vercel.com/docs/limits)

### Inferences
- With Root Directory = `dashboard`, "the root of your project directory" is `dashboard/`, so the classic layout is `dashboard/api/worker.py`, `dashboard/requirements.txt` (or `dashboard/pyproject.toml`), and `dashboard/vercel.json` holding `crons`, `regions` and `functions["api/worker.py"].maxDuration`. The function URL is `/api/worker`. No `rewrites` are needed for one-file-per-endpoint functions; rewrites are only needed for the "one ASGI app handles a whole prefix" pattern (as in the community starter) or for Services.
- Because the Python builder bundles every non-excluded file under the project root, a strategy package placed at e.g. `dashboard/thunderbot/` is included automatically and importable from `api/worker.py` without `includeFiles`. The flip side is that the Python function also bundles the dashboard's source tree (minus `node_modules`, `.next`, `public`); use `excludeFiles` to keep it lean.
- Sharing Python code from a sibling directory **outside** the Root Directory (this repo has `worker/` beside `dashboard/`) is the weak point of the `api/` approach: the build container can read `../worker` by default, but the Python function bundle is assembled from the project root (work path) and `includeFiles` globs resolve against it, so `../worker/**` is not something the docs say will work. Practical options, in order of how well-supported they look: (1) use **Services** with the project Root Directory at the repo root, `frontend.root = "dashboard/"` and a Python service whose `root = "worker/"` - this is exactly the polyglot-monorepo case Services was built for; (2) keep `api/` and copy or vendor the package into `dashboard/` during the build; (3) declare the sibling as a path dependency in `dashboard/requirements.txt`/`pyproject.toml` so it is installed into the bundle like any package (plausible, untested).
- Precedence on a path collision (`dashboard/app/api/worker/route.ts` vs `dashboard/api/worker.py`) is undocumented; the detector only reports conflicts among `api/` files. Do not define the same path in both. A distinct prefix (e.g. Python at `/api/py-worker` or under a Services prefix like `/svc/...`) removes the ambiguity. Next.js's own handling of unmatched `/api/*` (it 404s them) is another reason to verify the Python route on a preview deployment early.
- If `dashboard/requirements.txt` lists `fastapi`/`flask`/`django`, the "framework preset precedence" rule is worded for Python-preset projects; in a project whose Framework Preset is Next.js the `api/` files should remain per-file functions, but that interaction is not spelled out. Using a plain `BaseHTTPRequestHandler` `handler` class with only `requests` as a dependency sidesteps it and keeps the bundle to a few MB.
- Services is beta: expect config churn (there is already a superseded `experimentalServices` model). For a small single-developer bot the `api/worker.py` shape is simpler and long-established; Services is the forward-looking choice if the sibling `worker/` layout must be kept.

### Gaps
- No current Vercel prose doc explicitly says "Python files in `api/` work in a Next.js project" - the evidence is the builder source/warning text and the long-standing community starter. The docs page now steers such projects to Services.
- Precedence between `app/api/**/route.ts` and `api/*.py` for the same path: not documented; not determined.
- Whether `includeFiles` (or a relative path dependency) can pull files from outside the Root Directory into a Python function: not documented; needs a test deployment.
- How a Services project interacts with a dashboard-configured Root Directory other than the repo root is not described in the pages read.

---

## 4. Does Next.js `middleware.ts` run in front of Python functions under `/api/*`?

### Takeaway
Almost certainly yes: on Vercel, Next.js middleware is compiled into the deployment's routing table as a route that runs before filesystem/function resolution for every path its `matcher` covers, irrespective of which runtime built the target. Vercel's docs say middleware runs on every request unless a matcher narrows it, but they never mention Python functions specifically, so treat it as "expected, verify on a preview". Consequence: Vercel cron (and any external scheduler) calling `/api/worker` will hit the Basic Auth middleware and get a 401 unless the matcher excludes that path or the middleware accepts the `Authorization: Bearer <CRON_SECRET>` header.

### Cited Findings
- "Routing Middleware **executes code *before* a request is processed on a site**"; "Because it runs globally before the cache..."; "Without a matcher, your Routing Middleware runs on **every** request, including requests for static files." [upd 2026-08-14] — [Routing Middleware](https://vercel.com/docs/routing-middleware)
- Next.js builds its own routing middleware: "You can't use `proxy` with frameworks that build their own routing middleware, such as Next.js and Astro. In Next.js 16 and later, add a `proxy.ts` file at your project root instead, or a `middleware.ts` file in earlier versions." — [Routing Middleware](https://vercel.com/docs/routing-middleware)
- The docs' own matcher example exists precisely to keep middleware off API routes: "To match all request paths except for the ones starting with: `api` (API routes), `_next/static` (static files), `favicon.ico`" use `["/((?!api|_next/static|favicon.ico).*)"]`. — [Routing Middleware](https://vercel.com/docs/routing-middleware)
- Request lifecycle: the proxy "determines... **Middleware**: Does Routing Middleware need to run first for tasks like authentication or A/B testing?" before the cache and compute layers. [upd 2026-08-28] — [How requests flow through Vercel](https://vercel.com/docs/fundamentals/infrastructure)
- Source: the `@vercel/next` builder emits middleware as routes with `continue: true`, `src: matcher.regexp`, `middlewarePath`, and `override: true`, and places them with the comment "middleware comes directly after redirects but before beforeFiles rewrites as middleware is not a \"file\" route" - i.e. ahead of `{ handle: 'filesystem' }`, which is where functions and static files are resolved. — [vercel/vercel `packages/next/src/server-build.ts`](https://github.com/vercel/vercel/blob/main/packages/next/src/server-build.ts); [vercel/vercel `packages/next/src/utils.ts`](https://github.com/vercel/vercel/blob/main/packages/next/src/utils.ts)
- Cron requests carry `Authorization: Bearer <CRON_SECRET>` (when the env var is set) and user agent `vercel-cron/1.0`. — [Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs); [Cron Jobs](https://vercel.com/docs/cron-jobs)
- Middleware limits: max URL length 14 KB, request body 4 MB, 64 request headers, 32 KB header length; billed on the Fluid model; runs on Node.js by default. — [Routing Middleware](https://vercel.com/docs/routing-middleware)
- "Deployment Protection requires authentication for all requests, including those to Routing Middleware." [upd 2026-09-15] — [Deployment Protection](https://vercel.com/docs/deployment-protection)
- For Services projects, "Firewall, Deployment Protection, redirects are configured once at the top level and apply across all services" (middleware is not mentioned in that sentence). — [Services](https://vercel.com/docs/services)

### Inferences
- HTTP Basic Auth and Vercel's cron secret both use the single `Authorization` header (`Basic ...` vs `Bearer ...`), so a request cannot carry both. Two workable designs: (1) exclude the worker path in the middleware `matcher` (e.g. `/((?!api/worker|_next/static|_next/image|favicon.ico).*)`) and let the Python function itself verify `Authorization: Bearer $CRON_SECRET`; or (2) keep the matcher broad and have the middleware pass requests whose `Authorization` equals `Bearer ${process.env.CRON_SECRET}`, with the Python function re-checking. Option 1 is simpler and keeps the auth decision next to the code that trades.
- Do not rely on the `vercel-cron/1.0` user agent for auth; it is trivially spoofable. The secret header is the only documented authenticity mechanism for path-based crons.
- Next.js 15 uses `middleware.ts`; the docs flag a rename to `proxy.ts` from Next.js 16, relevant if the dashboard is upgraded.
- With Services, whether the Next.js service's middleware sees requests that a top-level rewrite sends to a different (Python) service is undocumented; by the "each service handles its own routes" model it probably does **not**, meaning a publicly exposed Python service would need its own auth (the Oct 2026 KB guide says as much: exposing Python publicly "requires your app to handle its own authentication").

### Gaps
- No Vercel doc or reliable community thread was found that explicitly states "Next.js middleware runs before non-Next.js (Python) functions in `api/`". The conclusion rests on generic docs plus the builder's route ordering. Verify with a preview deployment: request `/api/worker` with and without credentials and inspect whether the Basic Auth challenge appears.
- Behaviour of Next.js middleware across Services boundaries is not documented.

---

## 5. Do heavy packages fit? (pandas/numpy, yfinance + curl_cffi/lxml, scipy/scikit-learn)

### Takeaway
Everything fits under the 500 MB Python limit, even all at once (about 418 MB unzipped for requests + pandas + numpy + yfinance + scikit-learn with current wheels), but only pandas/numpy-class stacks would have fit under the old 250 MB limit, and the full stack leaves under 100 MB of headroom before Vercel adds bytecode and your own files. A `requests`-only worker is about 4 MB. No reliable report of `curl_cffi` wheels failing on Vercel's Amazon Linux 2023 runtime was found; the wheel is a standard `manylinux_2_17_x86_64` abi3 binary.

### Cited Findings
- Limits being measured against: 500 MB uncompressed for Python, 250 MB otherwise, 5 GB large-functions beta. — [Vercel Functions Limits](https://vercel.com/docs/functions/limitations)
- "There is no automatic tree-shaking for Python"; `.pyc` bytecode is added "when space allows"; "Make sure your `pyproject.toml` or `requirements.txt` only lists packages necessary at runtime." — [Python runtime](https://vercel.com/docs/functions/runtimes/python)
- Vercel's own troubleshooting names "machine learning libraries" and packages that "ship binaries" as common causes of oversize functions and recommends `VERCEL_ANALYZE_BUILD_OUTPUT=1` to list the largest files. — [Vercel Functions Limits](https://vercel.com/docs/functions/limitations)
- **Primary measurement by this researcher (2026-11-11; no URL)**: `pip install --only-binary=:all: --python-version 3.12 --platform manylinux2014_x86_64/manylinux_2_28_x86_64 --target <dir>`, then `du -sm` (unzipped, before any `.pyc`). Versions resolved from PyPI that day. Results:
  - `requests` 2.34.2 with deps (certifi, urllib3, idna, charset-normalizer): **4 MB** — [requests on PyPI](https://pypi.org/project/requests/)
  - `pandas` 3.1.1 + `numpy` 2.5.4 (+ tzdata, python-dateutil): **153 MB** (pandas 80, numpy 43, numpy.libs 27); 59 MB of that is `tests/` directories — [pandas on PyPI](https://pypi.org/project/pandas/); [numpy on PyPI](https://pypi.org/project/numpy/)
  - `yfinance` 1.8.0 with all deps: **224 MB** (pandas 80, numpy 43 + numpy.libs 27, **curl_cffi 0.17.0: 41 MB**, lxml 6.1.3: 12 MB, plus protobuf, peewee, websockets, beautifulsoup4, pytz, tzdata, etc.); 59 MB is `tests/` — [yfinance on PyPI](https://pypi.org/project/yfinance/)
  - `scipy` 1.18.1 + numpy: **208 MB** (scipy 109, scipy.libs 30, numpy 70); 48 MB `tests/` — [scipy on PyPI](https://pypi.org/project/scipy/)
  - `scikit-learn` 1.9.1 with deps (scipy, numpy, joblib, threadpoolctl, narwhals): **264 MB** (sklearn 48 on top of scipy/numpy); 62 MB `tests/` — [scikit-learn on PyPI](https://pypi.org/project/scikit-learn/)
  - All of `requests pandas numpy yfinance scikit-learn` together: **418 MB**; 105 MB of that is `tests/` directories.
- `curl_cffi` 0.17.0's Linux wheel is tagged `cp310-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64` and consists essentially of one 41 MB shared object (`_wrapper.abi3.so`). — [curl_cffi on PyPI](https://pypi.org/project/curl-cffi/) (tags read from the installed wheel's `WHEEL` file on 2026-11-11)
- Vercel builds on Amazon Linux 2023. — [Build image overview](https://vercel.com/docs/builds/build-image)
- yfinance depends on curl_cffi for Yahoo access: a yfinance issue notes "request_cache sessions don't work with curl_cffi, which is necessary now for Yahoo API" and that users should not pass their own session. — [ranaroussi/yfinance issue #2456](https://github.com/ranaroussi/yfinance/issues/2456)
- Cold-start mitigations Vercel documents: automatic bytecode precompilation for Python bundles and (Fluid) "function pre-warming on production deployments"; archived functions add "at least 1 second". — [Python runtime](https://vercel.com/docs/functions/runtimes/python); [Fluid compute](https://vercel.com/docs/fluid-compute); [Runtimes](https://vercel.com/docs/functions/runtimes)

### Inferences
- Amazon Linux 2023 ships glibc 2.34, which satisfies `manylinux_2_17` and `manylinux_2_28` wheels, so numpy/pandas/scipy/lxml/curl_cffi binary wheels should install without compilation on x86_64. Nothing found suggests a Vercel-specific curl_cffi incompatibility.
- Roughly a quarter of each scientific stack is test suites. An `excludeFiles` glob such as `**/tests/**` would save 50-100 MB; note `excludeFiles` is documented for project files and it is not confirmed that it also prunes installed dependencies (Vercel's example shows vendored paths like `_vendor/tensorflow/...` in the analyzer output, suggesting dependencies live under a `_vendor/` directory inside the bundle).
- For the worker itself, importing pandas/numpy on a cold start costs noticeable time (hundreds of ms to a couple of seconds is typical for these libraries generally), which is harmless for a cron job with a 300 s budget but argues for keeping the request-path worker `requests`-only and treating pandas/yfinance as optional. The bigger operational risk with yfinance on any serverless host is Yahoo throttling/blocking datacenter IP ranges rather than packaging.
- Adding scipy/scikit-learn on top of pandas + yfinance leaves little headroom under 500 MB once `.pyc` files and project files are added; the large-functions beta (5 GB, default-eligible for new projects) is the escape hatch but is beta.

### Gaps
- No measured cold-start times for these stacks on Vercel were found in official sources.
- No authoritative statement on the runtime CPU architecture; sizes above are for x86_64 wheels (aarch64 wheels differ slightly).
- Could not find a reliable public report either confirming or refuting curl_cffi/yfinance working inside Vercel Python functions; one Vercel community thread about outbound TCP timeouts from functions surfaced in search but was not verified and is not specific to curl_cffi. Test on a preview deployment.
- Whether `excludeFiles` can strip `tests/` folders from installed third-party packages is not documented.

---

## 6. Outbound static IP options

### Takeaway
Ordinary Vercel function egress uses dynamic addresses and Vercel publishes no range to allowlist. A fixed egress IP requires **Static IPs** (Pro or Enterprise add-on, launched 2 Oct 2025): **$100/month per project** plus Private Data Transfer (about $0.187/GB in Mumbai), giving a **shared** pair of **two static IPs per configured region** (up to three regions). Dedicated IPs need **Secure Compute**, which is Enterprise-only with custom pricing. Nothing is available on Hobby.

### Cited Findings
- "Without Static IPs, outbound traffic from your deployments uses dynamic IP addresses, and Vercel doesn't publish a fixed range for you to allowlist. To get fixed outbound addresses, use Static IPs on Pro or Enterprise, or Secure Compute on Enterprise." [upd 2026-06-30] — [Static IPs](https://vercel.com/docs/networking/static-ips)
- "Static IPs are available on Enterprise and Pro plans". "With Static IPs (shared pool), you can access backend services that require IP allowlisting through static egress IPs." — [Static IPs](https://vercel.com/docs/networking/static-ips)
- Pricing: "Static IPs are priced at $100/month per project for Pro plus Private Data Transfer priced regionally". Comparison table: Static IPs "$100/month per project, plus Private Data Transfer at regional rates"; Secure Compute "Custom pricing". — [Static IPs](https://vercel.com/docs/networking/static-ips)
- Pricing page: Static IPs (shared pool) on Pro "$100 / project / month; Starting at $0.15 per GB"; Hobby "Not available". Secure Compute: Pro "Not available", Enterprise "Custom". — [Vercel Pricing](https://vercel.com/pricing)
- Mumbai rate: "Private Data Transfer $0.187 per 1 GB" (bom1). [upd 2026-09-14] — [Mumbai (bom1) pricing](https://vercel.com/docs/pricing/regional-pricing/bom1)
- How many IPs / sharing: "Each configured region provides two static IP addresses from a shared pool, and a small group of customers in the same region shares them. Keep your backend's authentication in place, because other customers' traffic can come from the same addresses." "Each configured region has its own static IP pair". — [Static IPs](https://vercel.com/docs/networking/static-ips)
- Regions: "Select up to three regions close to your backend"; "Pick a **region** close to your backend services... You can pick up to 3 regions". [upd 2026-05-12] — [Getting Started with Static IPs](https://vercel.com/docs/networking/static-ips/getting-started)
- Scope: applies to Vercel Functions in every environment of the project ("You cannot isolate static IPs to specific deployment environments"); builds only if "Use for builds" is turned on; "Routing Middleware never uses static IPs"; egress only, no fixed inbound IP; a redeploy is needed after enabling. — [Static IPs](https://vercel.com/docs/networking/static-ips); [Getting Started with Static IPs](https://vercel.com/docs/networking/static-ips/getting-started)
- Launch: changelog dated **2 October 2025**, "Pro and Enterprise teams"; "Traffic from builds and functions routes through consistent, shared static IPs." — [Static IPs are now available for more secure connectivity](https://vercel.com/changelog/static-ips-are-now-available-for-more-secure-connectivity)
- Secure Compute: "available for purchase on Enterprise plans"; "Secure Compute is available as an Enterprise feature. Contact your Vercel account team for pricing."; each network gets "A pair of dedicated IP addresses"; "Each private network has its own dedicated IP pair and is isolated from others, ensuring no sharing across teams"; Private Data Transfer "$0.15/GB only for traffic that leaves the private network via the public internet"; up to 100 projects per network; supports Python runtime; does not apply to Routing Middleware or Edge runtime; region is chosen when the network is created. [upd 2026-09-23] — [Secure Compute](https://vercel.com/docs/networking/secure-compute)
- If both are enabled on a project, Secure Compute wins and "Static IPs will be ignored." — [Static IPs](https://vercel.com/docs/networking/static-ips)
- Vercel's suggested alternatives to IP allowlisting: OIDC federation for AWS/GCP/Azure backends, and AWS PrivateLink for AWS-hosted services. — [Static IPs](https://vercel.com/docs/networking/static-ips)
- Pro plan base price $20/month (includes $20 usage credit). — [Vercel Pricing](https://vercel.com/pricing)

### Inferences
- Minimum cost of a fixed egress IP on Vercel is therefore Pro ($20/month) + Static IPs ($100/month per project) = about **$120/month** plus per-GB transfer (negligible for a trading worker's JSON traffic).
- The IPs are shared with "a small group of customers", so an Indian broker API that requires a registered static IP (the usual reason for this question) would see an address that other Vercel tenants can also originate from; broker-side API keys/TOTP remain the real authentication. Whether a broker accepts a shared NAT address as the registered IP is a broker-policy question, not a Vercel one.
- Two addresses per region means **both** must be registered/allowlisted with the counterparty; if a broker allows only one registered IP, Static IPs' pair may not fit that constraint.
- `bom1` has its own published "Private Data Transfer" rate that links to the Static IPs doc, which strongly suggests Static IPs can be configured in Mumbai, but no doc page enumerates the supported regions.
- Supabase over HTTPS (PostgREST with an API key) does not need a static IP at all; only direct Postgres connections behind Supabase network restrictions, or broker allowlists, would.

### Gaps
- No official list of which regions support Static IPs; `bom1` availability is inferred, not confirmed. Check the project's Settings > Networking > Static IPs > Configure Regions.
- Secure Compute's price is no longer published (the docs and pricing page say custom/contact sales); any older figure from blogs should be treated as stale.
- Whether the two IPs of a region are used round-robin or active/standby is not documented.

---

## 7. Other relevant limits: deployments, builds, logs, background work, external schedulers and Deployment Protection

### Takeaway
Hobby allows 100 deployments/day, 45-minute builds, one concurrent build, and keeps runtime logs for only **1 hour** (Pro: 1 day), so the worker must persist its own run log (e.g. to Supabase). An external scheduler can invoke the function over plain HTTPS on the production domain, which Standard Protection leaves public; protected URLs need the `x-vercel-protection-bypass` secret. `waitUntil` background work is documented for Node.js/Edge, not for Python.

### Cited Findings

**Deployments and builds**
- General limits table: Deployments Created per Day - Hobby 100, Pro 6000; Build Time per Deployment 45 min (all plans); Concurrent Deployments - Hobby 1; Projects - Hobby 200; Vercel Projects per Git repository - Hobby 25; Routes per deployment 2048; CLI static file upload 100 MB (Hobby); Deploy Hooks per project 5. [upd 2026-09-16] — [Limits](https://vercel.com/docs/limits)
- Hobby rate limits: "You are able to build `100` Deployments every `3600` seconds (1 hour)"; "You are able to deploy `100` times every `86400` seconds (1 day)". "Each Vercel Function is also classed as a build." — [Limits](https://vercel.com/docs/limits)
- Hobby build machine: 2 vCPUs, 8 GB memory, 64 GB disk. — [Vercel Hobby Plan](https://vercel.com/docs/plans/hobby)
- Builds shallow-clone the repo (`git clone --depth=10`). — [Configuring a Build](https://vercel.com/docs/builds/configure-a-build)
- Monorepo: a "Skip deployment" switch under Root Directory skips deployments for commits that do not affect the project. — [Configuring a Build](https://vercel.com/docs/builds/configure-a-build)
- "Proxied Request Timeout" for rewrites to external origins: 120 seconds. — [Limits](https://vercel.com/docs/limits)

**Logs**
- "Runtime logs are stored for **1 hour** on Hobby, **1 day** on Pro, and for **3 days** on Enterprise accounts." Build logs are stored indefinitely per deployment. — [Limits](https://vercel.com/docs/limits)
- Pricing page: Pro and Enterprise can extend to 30 days with Observability Plus. Log Drains are not available on Hobby. — [Vercel Pricing](https://vercel.com/pricing); [Vercel Hobby Plan](https://vercel.com/docs/plans/hobby)
- Cron invocations appear as function invocations in runtime logs (filter `requestPath:/api/my-cron-job`), via "View Logs" on the Cron Jobs tab. — [Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs)

**Background work after the response**
- Fluid compute: "After fulfilling user requests, you can continue executing background tasks using `waitUntil`." — [Fluid compute](https://vercel.com/docs/fluid-compute)
- "Node.js and Edge runtime streaming functions support the `waitUntil` method". The Python SDK reference (`pip install vercel`, `vercel.functions`) documents `get_env`, `geolocation`, `ip_address`, `RuntimeCache`/`AsyncRuntimeCache` only. [upd 2026-08-11] — [Runtimes](https://vercel.com/docs/functions/runtimes); [vercel.functions API Reference (Python)](https://vercel.com/docs/functions/functions-api-reference/vercel-sdk-python)
- Vercel's Nov 2026 comparison of background options (summary): `waitUntil` and Cron Jobs are bounded by the function max duration (300 s Hobby); Queues and Daemons are public beta; Workflows GA since April 2026 with no run-duration limit (Hobby includes 50,000 events/month); Daemons are always-on workers, production only, Hobby 1-2 GiB / 1 vCPU with 5 Active CPU-hours and 420 GB-hours per month. For scheduled jobs it recommends cron + `CRON_SECRET`, assuming runs can be missed or duplicated. Published 2 Nov 2026, updated 7 Nov 2026. — [Running background workers on Vercel](https://vercel.com/kb/guide/background-workers-on-vercel)

**External schedulers and Deployment Protection**
- Functions are ordinary HTTPS endpoints; a cron path "is a public URL, so anyone can call it unless you check `CRON_SECRET`." — [Migrating from Cron Jobs to Schedules](https://vercel.com/docs/schedules/migrate-from-cron-jobs)
- Protection scopes: "**Standard Protection**: Protects all deployments **except** production domains"; "**All Deployments**: Protects **all** URLs, including production domains". Under Standard Protection "the production generated deployment URL becomes restricted". Standard Protection and All Deployments are available on all plans. [upd 2026-09-15] — [Deployment Protection](https://vercel.com/docs/deployment-protection)
- Hobby gets "Vercel Authentication for preview and production deployments, Deployment Protection Exceptions, and Shareable Links"; Password Protection is "Not available on Hobby" and costs "$20 per month per protected project" on Pro; Trusted IPs is Enterprise. — [Vercel Hobby Plan](https://vercel.com/docs/plans/hobby); [Deployment Protection](https://vercel.com/docs/deployment-protection)
- "Protection Bypass for Automation is available on all plans". "you can authenticate using either an HTTP header or a query parameter named `x-vercel-protection-bypass` with the value of the generated secret for the project." Vercel sets one secret as the `VERCEL_AUTOMATION_BYPASS_SECRET` system env var; multiple secrets per project are supported; regenerating a secret requires a redeploy. It bypasses Vercel Authentication, Password Protection and Trusted IPs, but not active DDoS mitigations. Optional `x-vercel-set-bypass-cookie: true`. [upd 2026-09-16] — [Protection Bypass for Automation](https://vercel.com/docs/deployment-protection/methods-to-bypass-deployment-protection/protection-bypass-automation)
- Hobby WAF: up to 3 custom rules and 10 IP blocks. — [Vercel Hobby Plan](https://vercel.com/docs/plans/hobby)

### Inferences
- Design for an external scheduler (GitHub Actions cron, Supabase `pg_cron` + `pg_net`, cron-job.org, etc.): call `https://<production-domain>/api/worker` with a shared secret header verified by the Python function; exclude that path from the Basic Auth middleware matcher. No protection-bypass token is needed for the production domain under Standard Protection; it is needed only for preview/generated URLs or if "All Deployments" protection is enabled.
- Because Hobby runtime logs vanish after one hour and missed cron runs leave no log at all, the worker should write a heartbeat/run record (start, end, outcome, schedule header) to Supabase on every invocation and the dashboard should alert on staleness.
- The app-level Basic Auth in `middleware.ts` is a reasonable substitute for Vercel Password Protection, which Hobby lacks; Vercel Authentication (Vercel-account login) is the free platform alternative for protecting the production domain, but it would also sit in front of external scheduler calls (requiring the bypass header) and possibly Vercel cron (see Gap in section 1).
- Python work that must outlive the HTTP response should not rely on `waitUntil`; simply do the work before responding (cron callers do not care about latency) within the 300 s budget, or hand off to Workflows/Queues if it grows.

### Gaps
- No "build minutes" quota appears in the current limits, Hobby or pricing pages read; only per-build duration (45 min), concurrency (1 on Hobby) and deployment-count limits are published.
- A Python equivalent of `waitUntil` is not documented in the Python SDK reference; whether one exists in the `vercel` package was not confirmed.
- Deployment Protection's interaction with Vercel-originated cron requests remains undocumented (see section 1 Gaps).
