# Job runners (free cloud schedulers) and laptop scheduling for a once-a-day trading job — state as of 11 November 2026

Target job: Python (`requests`, Supabase Postgres REST), 5-60 s runtime, must run once at ~15:10 IST (= 09:40 UTC; IST is UTC+5:30, no DST) on weekdays; ideally also every few minutes 09:15-15:30 IST (= 03:45-10:00 UTC).

**How to read the evidence labels in these notes**

- **[fetched]** = I opened the primary page in this session and the wording comes from it (only `docs.github.com` pages were fetchable).
- **[snippet]** = the fact comes from a web-search result summary of the linked page; I could not open the page itself. Treat numbers as "very likely right, re-check before relying on them".
- **[composed]** = a command/config I wrote from documented syntax; it was NOT executed in this session. The link is the reference page for the syntax.
- Research-environment limitation: direct fetches of `docs.oracle.com`, `developers.cloudflare.com`, `aws.amazon.com`, `modal.com`, `pythonanywhere.com`, `upstash.com`, `healthchecks.io`, `cron-job.org`, `learn.microsoft.com`, `freedesktop.org`, `github.blog`, `simonwillison.net`, `infoq.com` all failed (hosts not allowed from the research sandbox). `cloud.google.com` pricing pages returned truncated content. Those topics rely on search snippets.

---

## A1. GitHub Actions `schedule` (cron) workflows

### Takeaway
Free and Python-friendly, and since March 2026 it accepts an IANA `timezone` (so `Asia/Kolkata` works), but GitHub itself documents that scheduled runs can be delayed and even dropped under load; it is fine as a fallback or for a "sometime around 15:10" run, and NOT safe as the only trigger for a job with a hard 15:25 cutoff. The reliable pattern is an external precise scheduler calling `workflow_dispatch` through the REST API; there is no fixed outbound IP on standard runners.

### Cited Findings
- **Delay/drop wording (verbatim):** "The `schedule` event can be delayed during periods of high loads of GitHub Actions workflow runs." "High load times include the start of every hour." "If the load is sufficiently high enough, some queued jobs may be dropped." "To decrease the chance of delay, schedule your workflow to run at a different time of the hour." [fetched] — [GitHub Docs: Events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
- **Minimum interval:** "The shortest interval you can run scheduled workflows is once every 5 minutes." [fetched] — [GitHub Docs: Events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
- **Default branch only:** "Scheduled workflows will only run on the default branch." / "Scheduled workflows run on the latest commit on the default branch." [fetched] — [GitHub Docs: Events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
- **60-day auto-disable:** "In a public repository, scheduled workflows are automatically disabled when no repository activity has occurred in 60 days." (The docs state this for public repositories only.) [fetched] — [GitHub Docs: Events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
- **Time zones — CHANGED in 2026 (no longer UTC-only):** the docs now say "You can optionally specify a timezone using an IANA timezone string for timezone-aware scheduling", with an example using `timezone: "America/New_York"`; "By default, scheduled workflows run in UTC."; for DST, "scheduled workflows in skipped hours advance to the next valid time." [fetched] — [GitHub Docs: Events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows). The feature was announced in the changelog "GitHub Actions: Late March 2026 updates" (19 March 2026) as "Timezone support for scheduled workflows". [snippet] — [GitHub Changelog 2026-03-19](https://github.blog/changelog/2026-03-19-github-actions-late-march-2026-updates/)
- **Notifications:** "Notifications for scheduled workflows are sent to the user who last modified the cron syntax in the workflow file." [fetched] — [GitHub Docs: Events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
- **Community measurements of lateness (anecdotal, small samples):** a 2026 scheduler bake-off reported GitHub's best scheduled run was >17 minutes late, the median ~26 minutes late, and one run >10 hours late. [snippet] — [josephhall.org "small bake-off"](https://josephhall.org/blog/small-bake-off/). A GitHub community discussion reports a workflow "consistently delayed 8-14 hours, one day dropped entirely" even after changing the cron minute. [snippet] — [GitHub community discussion #201738](https://github.com/orgs/community/discussions/201738); see also [discussion #185355 "Github actions doesn't run scheduled workflow"](https://github.com/orgs/community/discussions/185355). Third-party write-ups characterise typical top-of-hour delay as 5-30 minutes. [snippet] — [crontap: GitHub Actions cron drift problem](https://crontap.com/blog/github-actions-cron-drift-problem). GitHub publishes no lateness statistic of its own.
- **Free allowance (now expressed in dollars, not minutes):** GitHub Free includes **$12/month** of Actions compute (GitHub Pro $18), 500 MB artifact storage (Pro 1 GB), 10 GB cache per repo; per-minute rates: Linux 1-core x64 $0.002, Linux 2-core x64 $0.006, Linux 2-core arm64 $0.005, Windows 2-core $0.010, macOS $0.062. Standard GitHub-hosted runners in **public repositories remain free** and do not consume the included amount; self-hosted runners are listed as free. [fetched] — [GitHub Docs: GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
- **2025-2026 pricing changes:** GitHub announced on 16 Dec 2025 a price cut for hosted runners (up to 39%, effective 1 Jan 2026) and a new $0.002/min "cloud platform" charge for self-hosted runners from 1 Mar 2026; the self-hosted charge was then **postponed** ("to take time to re-evaluate"). Free quotas were stated to remain the same; public-repo usage stays free. [snippet] — [GitHub Changelog 2025-12-16](https://github.blog/changelog/2025-12-16-coming-soon-simpler-pricing-and-a-better-experience-for-github-actions/); [GitHub resources: Pricing changes for GitHub Actions](https://resources.github.com/actions/2026-pricing-changes-for-github-actions/). The billing page fetched today still lists self-hosted runners as free. [fetched] — [GitHub Docs: GitHub Actions billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
- **Limits:** "Each job in a workflow can run for up to 6 hours of execution time."; a workflow run is cancelled after 35 days; Free plan: 20 concurrent jobs; trigger limits 1,500 events per 10 s per repo; REST API 5,000 requests/hour for a personal access token. [fetched] — [GitHub Docs: Actions limits](https://docs.github.com/en/actions/reference/limits)
- **Runner IPs are NOT fixed, and no longer only Azure:** IP ranges come from the `actions` key of `GET /meta`, the list "is updated once a week", and "we do not recommend that you use these as allowlists for your internal resources". Linux runners now use a multi-cloud pool, so their outbound IPs are "not limited to Azure datacenter ranges". For fixed addresses the docs recommend "larger runners with a static IP address range, or self-hosted runners" (larger runners are paid, also in public repos). [fetched] — [GitHub Docs: GitHub-hosted runners reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners); [GitHub Docs: billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
- **Runner sizes:** public repos get 4 CPU/16 GB Linux runners; private repos 2 CPU/8 GB; a 1-CPU `ubuntu-slim` runner (5 GB RAM) exists. [fetched] — [GitHub Docs: GitHub-hosted runners reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)
- **External trigger endpoint:** `POST /repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches`, body `ref` (required, branch or tag) and optional `inputs` (max 25 keys); classic PATs need the `repo` scope; the documented response is now `200` "Response including the workflow run ID and URLs". [fetched] — [GitHub Docs: REST API, workflows](https://docs.github.com/en/rest/actions/workflows)
- `workflow_dispatch` and `repository_dispatch` both require the workflow file to exist on the default branch; `repository_dispatch` always runs the last commit on the default branch. [fetched] — [GitHub Docs: Events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
- **Workflow file [composed]** — syntax per [GitHub Docs: Events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows). Secondary sources confirm `timezone:` sits next to each `cron:` entry ([cronuru GitHub Actions cron guide](https://cronuru.com/guides/github-actions-scheduled-workflows)):

  ```yaml
  # .github/workflows/thunderbot.yml  (must be on the default branch)
  name: thunderbot
  on:
    schedule:
      - cron: '10 15 * * 1-5'        # 15:10 Mon-Fri in the zone below
        timezone: 'Asia/Kolkata'     # added by GitHub in March 2026; without it use '40 9 * * 1-5' (UTC)
      - cron: '20 15 * * 1-5'        # second attempt; the script must be idempotent
        timezone: 'Asia/Kolkata'
    workflow_dispatch: {}            # lets an external scheduler (or you) start it on time
  concurrency:
    group: thunderbot
    cancel-in-progress: false
  jobs:
    run:
      runs-on: ubuntu-latest
      timeout-minutes: 5
      steps:
        - uses: actions/checkout@v4          # use the current major version
        - uses: actions/setup-python@v5
          with:
            python-version: '3.12'
            cache: pip
        - run: pip install -r requirements.txt
        - run: python bot.py
          env:
            SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
            SUPABASE_SERVICE_KEY: ${{ secrets.SUPABASE_SERVICE_KEY }}
  ```
- **External precise trigger from Supabase [composed]** — pg_cron schedules SQL and pg_net's `net.http_post` makes the HTTP call; pg_net is fire-and-forget (responses land in `net._http_response`, kept ~6 hours; a 5xx is neither retried nor alerted). [snippet] — [Supabase Docs: pg_net](https://supabase.com/docs/guides/database/extensions/pg_net); [Supabase Docs: pg_cron](https://supabase.com/docs/guides/database/extensions/pgcron); endpoint per [GitHub REST docs](https://docs.github.com/en/rest/actions/workflows):

  ```sql
  -- store a fine-grained PAT (Actions: read & write on the one repo) in Supabase Vault first
  select cron.schedule(
    'thunderbot-1510-ist',
    '40 9 * * 1-5',                              -- pg_cron on Supabase is UTC: 09:40 UTC = 15:10 IST
    $$
    select net.http_post(
      url     := 'https://api.github.com/repos/OWNER/REPO/actions/workflows/thunderbot.yml/dispatches',
      headers := jsonb_build_object(
                   'Accept',        'application/vnd.github+json',
                   'Authorization', 'Bearer ' || (select decrypted_secret from vault.decrypted_secrets where name = 'github_pat'),
                   'User-Agent',    'supabase-pg-net'),
      body    := jsonb_build_object('ref', 'main')
    );
    $$
  );
  ```

### Inferences
- $12 / $0.006 = 2,000 Linux 2-core minutes, i.e. the familiar "2,000 minutes/month on Free" is unchanged in effect; on the 1-core `ubuntu-slim` runner ($0.002/min) the same $12 would buy ~6,000 minutes (computed from the fetched rates; the billing page did not state the minute equivalents itself).
- Budget check for a private repo: one run per weekday ≈ 22 runs/month ≈ 22-44 billed minutes (negligible). Every 5 minutes for 03:45-10:00 UTC ≈ 75 runs/day ≈ 1,650 runs/month; if each job is billed as at least one whole minute that is ~1,650 of the ~2,000 minutes, i.e. feasible but tight; a public repo has no such limit.
- 09:40 UTC is not the top of the hour, so the documented worst congestion window is avoided, but nothing guarantees start by 15:25 IST. A scheduled run that arrives late must be stopped by the script's own cutoff check (see B4).
- `workflow_dispatch` runs are queued immediately on API call, so "external precise scheduler -> dispatch API" replaces the unreliable part (the schedule event) while keeping free compute; remaining latency is runner pickup plus `checkout`/`setup-python`/`pip install`.
- If the repo is public and the workflow contains a `schedule:` trigger, 60 days without repo activity disables it; a private repo, or a dispatch-only workflow in a public repo, avoids relying on the scheduled-workflow keepalive (docs only describe auto-disable for scheduled workflows in public repos).
- Secrets: repository "Actions secrets" are exposed only via `${{ secrets.NAME }}` and masked in logs; never put the Supabase service key in a public repo's code. (Standard behaviour; the secrets doc page was not re-fetched in this session.)

### Gaps
- No official or measured figure for job start latency (the brief's "~10-40 s") was found in this session; treat it as unverified.
- Whether partial minutes are still rounded up per job is not stated on the current billing page (it was historically).
- The exact `timezone` YAML placement was confirmed from the docs page summary and secondary guides, not from the changelog text itself (github.blog was unreachable).
- Final status of the self-hosted runner charge after the postponement is not confirmed beyond "postponed, still listed as free on the billing page today".

---

## A2. Google Cloud Run (jobs or services) + Cloud Scheduler

### Takeaway
The most precise fully-managed free option: Cloud Scheduler supports tz-database zones (`Asia/Kolkata`), retries, and 3 free jobs per billing account, and a 60-second Python job is far inside Cloud Run's free tier; it needs a billing account, and a fixed outbound IP costs extra (Cloud NAT + reserved IP).

### Cited Findings
- **Cloud Run free tier:** request-based services: first 180,000 vCPU-seconds, 360,000 GiB-seconds and 2 million requests per month free (Tier 1 pricing basis); instance-based billing/jobs figures quoted as 240,000 vCPU-seconds and 450,000 GiB-seconds; Tier 2 regions show lower equivalents (e.g. 128,571 vCPU-s / 257,142 GiB-s request-based; 200,000 vCPU-s / 375,000 GiB-s for jobs). "The free tier usage is aggregated across projects by billing account and resets every month." [snippet] — [Cloud Run pricing](https://cloud.google.com/run/pricing)
- **Cloud Scheduler price:** 3 free jobs per month per billing account (counted at billing-account level, not per project); then $0.10 per job per 31 days; "a job is not billed for individual executions". [snippet] — [Cloud Scheduler pricing](https://cloud.google.com/scheduler/pricing)
- **Time zone:** the job's `timeZone` "must be a time zone name from the tz database. If a time zone is not specified, the default will be in UTC". [snippet] — [Cloud Scheduler REST reference: projects.locations.jobs](https://docs.cloud.google.com/scheduler/docs/reference/rest/v1beta1/projects.locations.jobs)
- **Retries:** "The default value of retry_count is zero. If retry_count is zero, a job attempt will not be retried if it fails." With `retry_count > 0` the job "will be tried a total of retry_count times, with exponential backoff, until the next scheduled start time." Attempt deadline for HTTP targets: 15 seconds to 30 minutes; a timeout is marked `DEADLINE_EXCEEDED`. [snippet] — [Cloud Scheduler REST reference](https://docs.cloud.google.com/scheduler/docs/reference/rest/v1beta1/projects.locations.jobs)
- **Scheduling a Cloud Run job:** Google's "Execute jobs on a schedule" page uses `gcloud scheduler jobs create http` posting to the Cloud Run v2 API `.../jobs/JOB-NAME:run` with `--oauth-service-account-email`; roles needed include Cloud Scheduler Admin and Cloud Run Invoker. [snippet] — [Cloud Run docs: Execute jobs on a schedule](https://docs.cloud.google.com/run/docs/execute/jobs-on-schedule)
- **Commands [composed]** — syntax per [Execute jobs on a schedule](https://docs.cloud.google.com/run/docs/execute/jobs-on-schedule) and [Manage cron jobs](https://docs.cloud.google.com/scheduler/docs/creating):

  ```bash
  # 1) deploy the code as a Cloud Run job (buildpacks pick up requirements.txt + a Procfile/entrypoint)
  gcloud run jobs deploy thunderbot --source . --region asia-south1 \
    --task-timeout 300s --max-retries 0 \
    --set-secrets SUPABASE_SERVICE_KEY=supabase-service-key:latest \
    --set-env-vars SUPABASE_URL=https://YOURPROJECT.supabase.co

  # 2) trigger it at 15:10 IST Mon-Fri
  gcloud scheduler jobs create http thunderbot-1510 \
    --location asia-south1 \
    --schedule "10 15 * * 1-5" --time-zone "Asia/Kolkata" \
    --uri "https://run.googleapis.com/v2/projects/PROJECT_ID/locations/asia-south1/jobs/thunderbot:run" \
    --http-method POST \
    --oauth-service-account-email PROJECT_NUMBER-compute@developer.gserviceaccount.com \
    --max-retry-attempts 2 --attempt-deadline 180s

  # 3) optional intraday job (uses the 2nd of 3 free scheduler jobs); the script gates 09:15-15:30 itself
  gcloud scheduler jobs create http thunderbot-intraday \
    --location asia-south1 \
    --schedule "*/5 9-15 * * 1-5" --time-zone "Asia/Kolkata" \
    --uri "https://run.googleapis.com/v2/projects/PROJECT_ID/locations/asia-south1/jobs/thunderbot:run" \
    --http-method POST \
    --oauth-service-account-email PROJECT_NUMBER-compute@developer.gserviceaccount.com
  ```
- **Static egress IP:** only by routing egress through a VPC (Direct VPC egress or a Serverless VPC Access connector) plus Cloud NAT with a reserved IP. Cloud NAT is usage-priced: an hourly gateway charge ($0.0014 per VM-instance-hour, capped at $0.044/hour above 32 instances), $0.005/hour per external IP, and $0.045/GiB processed. [snippet, table partly garbled in the result] — [Cloud NAT pricing](https://cloud.google.com/nat/pricing). A static-IP vendor's blog estimates "$40-50/month for a simple setup" (about $32/month per gateway plus data); this is a secondary estimate from a company selling an alternative. [snippet] — [QuotaGuard blog](https://quotaguard.com/blog/google-cloud-functions-cloud-run-static-ip)

### Inferences
- Usage estimate: 1 vCPU/512 MiB x 60 s x ~22 runs = ~1,320 vCPU-s/month; even every 5 minutes through market hours (~1,650 runs) is ~99,000 vCPU-s and ~50,000 GiB-s, inside the free tier in either pricing tier.
- With Direct VPC egress (no always-on connector VMs) the static-IP cost for this workload is probably dominated by the reserved IP (~$0.005/h ≈ $3.65/month) plus a small gateway charge, i.e. single-digit dollars/month, well below the vendor's $40-50 estimate, which appears to assume the gateway at its capped rate and/or a connector. Not verified against a real bill.
- Cloud Scheduler has no documented top-of-hour congestion problem like GitHub; expect start within seconds of the cron time, then Cloud Run job start latency (container pull/start) on top.
- Three free Scheduler jobs are enough for: the 15:10 run, a 15:20 retry, and one intraday `*/5` job.

### Gaps
- I could not confirm from a fetched page whether `asia-south1` (Mumbai) is Tier 1 or Tier 2 for Cloud Run (my recollection is that Mumbai is Tier 1 and Delhi `asia-south2` is Tier 2 — unverified). Either way the free allowance covers this job.
- No official Cloud Scheduler timing-precision SLA/number was found.
- Billing-account/credit-card requirement: Google Cloud requires an active billing account to enable Cloud Run and Cloud Scheduler APIs (standard behaviour; not re-verified on a fetched page in this session).
- Cloud Scheduler availability in `asia-south1` was not re-verified (if unavailable, any other location can call the Mumbai Cloud Run job).

---

## A3. AWS Lambda + EventBridge Scheduler

### Takeaway
Technically excellent (IANA time zones, retries, per-minute cron, Mumbai region) and effectively free at this volume on a paid-plan account, but accounts created after 15 July 2025 start on a credit-based Free plan that ends after 6 months, and a fixed outbound IP requires a VPC + NAT Gateway + Elastic IP at roughly USD 45/month in Mumbai.

### Cited Findings
- **Lambda free tier:** one million requests and 400,000 GB-seconds of compute per month, aggregated across x86 and Graviton functions. [snippet] — [AWS Lambda pricing](https://aws.amazon.com/lambda/pricing/)
- **EventBridge Scheduler free tier:** 14,000,000 invocations per month free, then $1.00 per million — reported by third-party/AWS-community pages; not seen on an official AWS page in this session. [snippet] — [AWS Builder Center: Free AWS cron jobs](https://builder.aws.com/content/3KlUsGddUtlTJTEihmtO40vu6MG/free-aws-cron-jobs-eventbridge-scheduler-and-step-functions); [freetier.co AWS guide](https://freetier.co/aws-free-tier)
- **Free-tier change for new accounts:** accounts opened after 15 July 2025 choose a Free plan or Paid plan; both start with $100 in credits and can earn up to $100 more (total $200); the Free plan lasts 6 months (credit-based). Accounts created before 15 July 2025 stay on the legacy Free Tier (12-month trials plus Always Free). [snippet] — [AWS News Blog: AWS Free Tier update](https://aws.amazon.com/blogs/aws/aws-free-tier-update-new-customers-can-get-started-and-explore-aws-with-up-to-200-in-credits/); [InfoQ, July 2025](https://www.infoq.com/news/2025/07/aws-risk-free-account-credits)
- **Time zones:** EventBridge Scheduler evaluates cron expressions in a chosen IANA time zone (including DST), unlike EventBridge Rules, which are UTC-only. [snippet] — [Picking a Scheduler on AWS](https://barkingiguana.com/writing/picking-a-scheduler-on-aws/); official overview at [EventBridge Scheduler user guide](https://docs.aws.amazon.com/eventbridge/latest/userguide/using-eventbridge-scheduler.html)
- **Flexible window:** "When you configure your schedule with a flexible time window, EventBridge Scheduler invokes the target within the time window you set. This is useful in cases that do not require precise scheduled invocation of targets." (So set it OFF for this job.) [snippet] — [EventBridge Scheduler: flexible time windows](https://docs.aws.eu/scheduler/latest/UserGuide/managing-schedule-flexible-time-windows.html)
- **Retries/DLQ:** the retry policy sets the number of retries and the maximum age of an unprocessed event (max 24 hours); after exhaustion the event can go to an SQS dead-letter queue. [snippet] — [EventBridge Scheduler user guide](https://docs.aws.amazon.com/eventbridge/latest/userguide/using-eventbridge-scheduler.html)
- **Command [composed]** — syntax per [EventBridge Scheduler user guide](https://docs.aws.amazon.com/eventbridge/latest/userguide/using-eventbridge-scheduler.html):

  ```bash
  aws scheduler create-schedule --region ap-south-1 --name thunderbot-1510 \
    --schedule-expression "cron(10 15 ? * MON-FRI *)" \
    --schedule-expression-timezone "Asia/Kolkata" \
    --flexible-time-window '{"Mode":"OFF"}' \
    --target '{"Arn":"arn:aws:lambda:ap-south-1:ACCOUNT_ID:function:thunderbot",
               "RoleArn":"arn:aws:iam::ACCOUNT_ID:role/scheduler-invoke-thunderbot",
               "RetryPolicy":{"MaximumRetryAttempts":2,"MaximumEventAgeInSeconds":600}}'
  ```
- **Static IP cost:** NAT Gateway is charged per hour available plus per GB processed. [snippet] — [AWS docs: Pricing for NAT gateways](https://docs.aws.amazon.com/vpc/latest/userguide/nat-gateway-pricing.html). Mumbai rate reported by third parties as $0.056/hour and $0.056/GB (US regions $0.045); every public IPv4 address costs $0.005/hour (~$3.65/month). [snippet, third-party] — [cloudprice.net ap-south-1](https://cloudprice.net/aws/region/ap-south-1); [CloudBurn NAT Gateway pricing](https://cloudburn.io/blog/aws-nat-gateway-pricing)

### Inferences
- $0.056 x 730 h ≈ $40.9/month + $3.65 Elastic IP ≈ **$44.5/month** before data, slightly above the brief's $33-40 estimate (which matches US-region rates).
- At ~22-1,650 invocations/month x 60 s x 256-512 MB, Lambda usage is 1-10% of the monthly free allowance.
- `requests` is not in the Lambda Python runtime by default as a supported dependency; package it in the deployment zip or a layer (standard practice, not re-verified here).
- For a brand-new AWS account in late 2026, "free" means: 6 months on the Free plan, then upgrade to the Paid plan (where the always-free Lambda allowance keeps the bill at ~$0 for this job) or the account closes.

### Gaps
- EventBridge Scheduler's precision ("within 60 seconds of the scheduled time") could not be confirmed from an official page in this session.
- Official ap-south-1 NAT Gateway rate table was not reachable; the $0.056 figures are third-party.
- Whether Always Free Lambda limits continue unchanged on post-July-2025 Paid plans was only seen in secondary sources.

---

## A4. Oracle Cloud Always Free VM

### Takeaway
Still the only zero-cost option that is a real always-on Linux server (cron/systemd timers, minute-level precision) with its own public IPv4 — valuable for broker IP whitelisting — but in mid-2026 Oracle halved the Arm allowance (now 2 OCPU/12 GB), idle instances on non-upgraded accounts can be reclaimed, capacity for new Arm instances is unreliable, and account-termination anecdotes are common.

### Cited Findings
- **Arm allowance halved in 2026:** Oracle cut the Always Free Ampere A1 allowance from 4 OCPUs/24 GB to **2 OCPUs/12 GB**; the docs reportedly now list 1,500 OCPU-hours and 9,000 GB-hours per month for VM.Standard.A1.Flex (previously 3,000/18,000). Sources disagree on the effective date: 15 June 2026 (InfoQ) vs. limits applying from 18 August 2026 (Oracle community notice, other blogs). Either way it is in force by November 2026. There was no prominent public announcement ("quietly"). [snippet] — [InfoQ: Oracle Cloud free tier limits (July 2026)](https://infoq.com/news/2026/07/oracle-cloud-free-tier-limits/); [Linuxiac: Oracle Quietly Cuts Free Tier Ampere A1 Resources in Half](https://linuxiac.com/oracle-quietly-cuts-free-tier-ampere-a1-resources-in-half/); [Oracle community thread](https://community.oracle.com/customerconnect/discussion/972539/cannot-change-ampere-a1-compute-resource-allocation)
- A secondhand (Reddit-sourced) report says Oracle Support confirmed the new A1 limits also apply to Pay-As-You-Go accounts, so usage above 2 OCPU/12 GB may be billed. [snippet, unverified] — [terminalbytes: Oracle Cloud free tier changes 2026](https://terminalbytes.com/oracle-cloud-free-tier-changes-2026)
- **Idle reclamation:** Oracle may reclaim an Always Free compute instance deemed idle over a 7-day period: CPU utilisation (95th percentile) below 20%, network utilisation below 20%, and memory utilisation below 20% (memory criterion applies to A1 shapes only). The threshold has moved over time (10% early 2023 -> 15% April 2023 -> 20%). [snippet] — [Oracle Docs: Always Free Resources](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm); [oracommit blog, Feb 2026](https://oracommit.blogspot.com/2026/02/understanding-oci-always-free-compute.html); [51sec.org history](https://51sec.org/2023/02/24/oracle-cloud-cleaning-up-idle-compute-instances-how-to-keep-it)
- **Avoiding reclamation:** converting the account to Pay As You Go exempts instances from idle reclamation (free resources stay free). [snippet] — [51sec.org](https://51sec.org/2023/02/24/oracle-cloud-cleaning-up-idle-compute-instances-how-to-keep-it)
- **Public IP:** a reserved public IP stays with the account and can be moved to a new VM, whereas an ephemeral IP lasts only as long as the instance; free-tier users report hitting a `reserved-public-ip-count` service limit when creating reserved IPs. [snippet, forum] — [Oracle community: Cannot create reserved IP](https://community.oracle.com/CustomerConnect/discussion/621840/cannot-create-reserved-ip-it-says-limits-were-exceeded)
- **Termination anecdotes:** forum posts describe free-tier instances/accounts removed with little explanation (e.g. a 2019 cleanup bug that wrongly flagged free-tier instances; "removed by an internal system without notice"). [snippet, anecdotal] — [LowEndTalk thread](https://lowendtalk.com/discussion/comment/3614918/)
- **Capacity:** an Oracle community user reports being unable to create a new A1 instance in their region. [snippet] — [Oracle community thread](https://community.oracle.com/customerconnect/discussion/972539/cannot-change-ampere-a1-compute-resource-allocation)

### Inferences
- A cron/systemd timer on an always-on VM fires within about a second of the wall-clock time; this is the best timing precision of any free option, and the job can loop every minute through market hours at no cost.
- A trading job that runs for 60 seconds a day leaves the VM far below the 20% thresholds, so a non-upgraded account's instance is a reclamation candidate; upgrading to PAYG (card required, stays $0 within limits) is the practical mitigation rather than running CPU-burner scripts.
- Because Always Free resources must be created in the home region chosen at sign-up, choose Mumbai (ap-mumbai-1) or Hyderabad (ap-hyderabad-1) at account creation if a low-latency Indian IP is wanted (home-region rule is long-standing Oracle policy; not re-fetched).
- Given the 2026 cut and termination stories, treat Oracle free as "good primary if monitored, never the only path": keep the dead-man alert (B4) and a second runner.

### Gaps
- I could not open Oracle's Always Free page to confirm, as of November 2026: the AMD micro allowance (historically 2 x VM.Standard.E2.1.Micro, 1/8 OCPU + 1 GB each), the exact number of free reserved public IPv4 addresses, the home-region rule wording, and the "out of host capacity" note. The brief's "A1 4 OCPU/24 GB" is outdated per the findings above.
- No Mumbai/Hyderabad-specific capacity data for 2026 was found.

---

## A5. Cloudflare Workers (Cron Triggers, Python Workers)

### Takeaway
Cron Triggers exist on the free plan (5 per account, UTC), and Python Workers reportedly reached GA in September 2026, but the free plan's 10 ms CPU limit, the Pyodide runtime (async HTTP only; `requests` support disputed) and the lack of a fixed egress IP make it a poor fit for porting an existing `requests`-based job; it is better used as a tiny precise "pinger" that calls another endpoint.

### Cited Findings
- **Limits (Free vs Paid):** CPU time per HTTP request 10 ms (Free) vs up to 5 min (Paid); CPU per Cron Trigger 10 ms (Free) vs 30 s for schedules under 1 hour and 15 min for schedules of 1 hour or more (Paid); Cron Triggers per account 5 (Free) vs 250 (Paid); subrequests 50 per request (Free) vs 10,000 (Paid); Cron Triggers have a 15-minute wall-clock duration limit. [snippet] — [Cloudflare Workers limits](https://developers.cloudflare.com/workers/platform/limits/)
- **Cron Triggers are UTC with no per-Worker time-zone option** (third-party guide). [snippet] — [cronuru: Cloudflare Workers cron triggers](https://cronuru.com/guides/cloudflare-workers-cron-triggers)
- **Python Workers status:** reported as generally available on 21 September 2026 after ~2 years in beta; local CLI `pywrangler` (PyPI package `workers-py`), uv-first workflow; ASGI/WSGI connectors let FastAPI/Django/Flask run. [snippet — primary pages unreachable] — [Simon Willison, 21 Sep 2026](https://simonwillison.net/2026/Sep/21/cloudflare-python-worker/); [InfoQ: Cloudflare Python Workers GA](https://infoq.com/news/2026/09/cloudflare-python-workers-ga)
- **Scheduled handler in Python:** `class Default(WorkerEntrypoint): async def scheduled(self, controller, env, ctx)`; Cron Triggers for Python Workers were announced 22 April 2025. [snippet] — [Cloudflare changelog 2025-04-22](https://developers.cloudflare.com/changelog/2025-04-22-python-worker-cron-triggers)
- **Packages:** Python Workers support packages included in Pyodide plus pure-Python packages/PyEmscripten wheels; the packages page says only HTTP libraries that can make requests asynchronously are supported (aiohttp, httpx), and JavaScript `fetch()` is callable via the FFI. [snippet] — [Cloudflare docs: Python packages](https://developers.cloudflare.com/workers/languages/python/packages)
- **Conflict on `requests`:** Cloudflare's packages page (as indexed) says synchronous `requests` is unsupported, while InfoQ's GA coverage says `requests` and `httpx` now route through the JavaScript fetch API. Unresolved. [snippet] — [Cloudflare docs: Python packages](https://developers.cloudflare.com/workers/languages/python/packages); contradicted by [InfoQ](https://infoq.com/news/2026/09/cloudflare-python-workers-ga)
- **Cold start:** Cloudflare's December 2025 benchmark (httpx + FastAPI + pydantic) reported a mean cold start of ~1.03 s using deploy-time memory snapshots. [snippet] — [Cloudflare changelog 2025-12-08](https://developers.cloudflare.com/changelog/2025-12-08-python-cold-start-improvements/); [Cloudflare blog: Python Workers advancements](https://blog.cloudflare.com/python-workers-advancements)
- **Yahoo Finance from cloud IPs:** Yahoo rate-limits by IP and session crumb; datacenter/shared cloud IPs are reported to hit 429s or blocks quickly, and apps that work locally fail on shared hosts. Sources are scraping vendors and forums, not Yahoo. No source specifically tested Cloudflare Workers egress. [snippet, low-quality sources] — [Scrapfly: guide to Yahoo Finance API](https://scrapfly.io/blog/posts/guide-to-yahoo-finance-api); [Portfolio Performance forum](https://forum.portfolio-performance.info/t/yahoo-finance-too-many-requests-getting-errors-on-updates-desktop-only/32780)

### Inferences
- A job that does several HTTPS calls and JSON parsing in CPython-on-WebAssembly is unlikely to fit in 10 ms of CPU on the free plan; realistically this needs Workers Paid, which removes the "free" attraction.
- Network wait does not count as CPU time, so a JavaScript/TypeScript Worker whose only job is "at the cron minute, `fetch()` a Cloud Run/Vercel/Lambda URL or the GitHub dispatch API" does fit the free plan and gives near-exact timing; the 5 free cron triggers and UTC-only schedule (`40 9 * * 1-5`) are enough.
- Workers share Cloudflare's egress ranges; there is no per-account fixed outbound IP on Free/Paid plans, so Workers cannot satisfy a broker's static-IP whitelist by themselves (dedicated egress is an Enterprise add-on — from prior knowledge, not re-verified).
- The Yahoo-blocking risk applies to every shared cloud egress (GitHub runners, Lambda, Cloud Run, Workers), not just Cloudflare; a home IP or a private VM IP is the safer place to fetch Yahoo data.

### Gaps
- Could not confirm from Cloudflare's own pages: whether Python Workers (with packages) deploy on the Free plan in 2026, their CPU limits there, the Workers Paid price ($5/month historically), daily request limits, and Cron Trigger timing precision.
- GA status rests on search snippets of pages I could not open; the `requests` question needs a 5-minute hands-on test.

---

## A6. Other options (one line each)

### Takeaway
For precise timing at zero cost, the useful extras are external HTTP schedulers (cron-job.org, QStash, Cloud Scheduler) pinging a serverless endpoint, and Modal for Python-native cron; several formerly free options (PythonAnywhere free scheduled tasks, Deta) are no longer available to new users.

### Cited Findings
- **Vercel Cron:** Hobby = cron jobs limited to once per day with per-hour precision (a 01:00 job fires anywhere 01:00-01:59; ±59 min); more frequent expressions fail at deploy; Pro ($20/user/month) = once-per-minute with per-minute precision; job-count limit now reported as 100 per project. (Covered in depth by another researcher.) [snippet] — [Vercel docs: Cron jobs usage and pricing](https://vercel.com/docs/cron-jobs/usage-and-pricing)
- **Supabase pg_cron + pg_net / Edge Functions:** pg_cron schedules SQL inside the existing database and `net.http_post` can call any HTTPS URL (fire-and-forget, no retry on 5xx; sub-minute schedules need pg_cron 1.5+); Edge Functions can be scheduled the same way but are TypeScript/Deno. [snippet] — [Supabase docs: Scheduling Edge Functions](https://supabase.com/docs/guides/functions/schedule-functions); [Supabase docs: pg_net](https://supabase.com/docs/guides/database/extensions/pg_net)
- **Render cron jobs:** paid; prorated by the second of running time with "a minimum monthly charge of $1 per cron job service"; at most one active run per cron job. [snippet] — [Render docs: Cron Jobs](https://render.com/docs/cronjobs)
- **Railway cron:** services can start on a crontab schedule and you pay only while running; third-party sources say minimum cadence is 5 minutes and best-effort; trial credit then paid plans (figures inconsistent across sources). [snippet] — [Railway docs: compare to Render](https://docs.railway.com/platform/compare-to-render); [crontap on Railway cron](https://crontap.com/blog/railway-http-cron-external)
- **Fly.io:** Machines have a "scheduled" mode but community guidance is that it suits coarse intervals; the cost-effective pattern for precise jobs is an external cron starting a Machine through the API. [snippet] — [Fly community: Cron jobs/scheduler on Fly.io?](https://community.fly.io/t/cron-jobs-scheduler-on-fly-io/7791)
- **Modal:** Starter plan $0 + compute with **$30/month free credits**, **5 deployed crons** (unlimited on higher tiers), 3 seats, 100 containers; Team is $250/month; one tracker reports network egress billing ($0.04/GiB) from 1 Oct 2026. Python-native (`@app.function(schedule=modal.Cron(...))`). [snippet] — [Modal pricing](https://modal.com/pricing); [costbench Modal free plan](https://www.costbench.com/software/ai-gpu-cloud/modal/free-plan/)
- **PythonAnywhere:** since January 2026 **new free accounts no longer get scheduled tasks** (moved to the Developer tier at $10/month, which has 20 hourly/daily tasks); accounts created earlier keep 1 daily task; the old $5 Hacker plan was dropped; free accounts still have outbound access restricted to an allowlist over HTTP(S). [snippet] — [PythonAnywhere blog: Changes on Free Accounts](https://blog.pythonanywhere.com/221/); [PythonAnywhere blog: New Plans](https://blog.pythonanywhere.com/222/); [PythonAnywhere pricing](https://www.pythonanywhere.com/pricing/)
- **cron-job.org:** free external HTTP scheduler, up to once per minute; request must finish within 30 seconds (then timed out; reads up to 64 KB of output); jobs are auto-disabled after repeated consecutive failures (15 per one source, 25 per another). [snippet] — [cron-job.org FAQ](https://cron-job.org/en/faq/); [DEV: cron-job.org](https://dev.to/arxeiss/cron-job-org-free-cron-service-2ge)
- **Upstash QStash:** free plan now listed as 1,000 messages/day (older pages/third parties say 500), 10 schedules on free, automatic retries; pay-as-you-go $1 per 100K messages. Sources conflict on whether retries count as messages. [snippet] — [Upstash QStash pricing](https://upstash.com/pricing/qstash)
- **EasyCron:** free tier limits are inconsistent across sources (200 executions/day with 20-minute minimum interval vs. other figures) and free plans must be renewed manually; EasyCron may stop free service at any time. [snippet] — [EasyCron terms](https://easycron.com/terms); [FastCron list of free cron services](https://www.fastcron.com/blog/free-cron-job-services)
- **UptimeRobot:** free plan 50 monitors at 5-minute intervals (a monitor, not a cron: fixed interval, no weekday/time-of-day schedule); commercial-use terms changed in 2026 and sources conflict. [snippet] — [DEV: UptimeRobot free plan in 2026](https://dev.to/r0tten0x/uptimerobot-free-plan-in-2026-the-limits-thatll-actually-bite-you-445g)
- **Google Apps Script time-driven triggers:** free; a `nearMinute()` trigger "runs at the specified minute, within plus or minus 15 minutes"; consumer accounts get ~90 minutes of total trigger runtime per day (6 h on Workspace), 6-minute max per execution, 20 triggers per user per script. Can call an HTTPS endpoint with `UrlFetchApp`. [snippet] — [Apps Script reference: ClockTriggerBuilder](https://developers.google.com/apps-script/reference/script/clock-trigger-builder)

### Inferences
- cron-job.org's 30-second timeout is shorter than the job's worst case (60 s): the endpoint it pings should acknowledge immediately and do the work asynchronously (or the ping should be the GitHub dispatch call, which returns at once).
- Modal is the lowest-friction "free + Python-native + precise cron" option: 22-1,650 runs x 60 s of a fractional CPU costs cents against $30/month credit; it has no fixed outbound IP on the free plan (static-IP proxies are a paid-plan feature — from prior knowledge, unverified in this session).
- Apps Script's ±15 minutes makes it unsuitable for a 15:10 run with a 15:25 cutoff except as a late "did it run?" checker.
- Home-server alternatives: a Raspberry Pi (or any always-on mini PC) running the same systemd timer as in B3 gives exact timing on the home IP for the cost of ~3-5 W of electricity, but shares the home connection's dynamic IP and power/ISP outages; an old Android phone with Termux + cron works in principle but Android battery optimisation (Doze) routinely suspends background processes, so it needs a wake-lock and "unrestricted battery" settings and is the least dependable of these. (No sources retrieved for these; engineering judgement.)

### Gaps
- Deta: no source retrieved in this session. From prior knowledge Deta Space announced its sunset in 2024 (shutdown in October 2024); treat as unavailable but unverified here.
- Railway and Fly.io current pricing/free allowances and exact schedule granularity were not confirmed from their own docs.
- cron-job.org outbound IP list, per-job time-zone support and exact auto-disable threshold were not confirmed; healthchecks-style details for QStash schedule limits conflict between sources.

---

## A7. Comparison table

### Takeaway
No free serverless option gives a fixed outbound IP; only an always-on VM (Oracle free, or any paid VPS) or a paid NAT does. For timing, Cloud Scheduler/EventBridge/Modal/cron-job.org/a VM are precise; GitHub `schedule`, Vercel Hobby and Apps Script are not.

### Cited Findings
Sources for each row are the cited findings in A1-A6 above (same links); cells marked * are my inference or unverified.

| Option | Monthly cost | Fixed outbound IP | Timing precision | Max runtime | Python support | Main caveat |
|---|---|---|---|---|---|---|
| GitHub Actions `schedule` ([docs](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows), [billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)) | $0 (public: unlimited standard runners; private: $12 included ≈ 2,000 Linux min*) | No (paid larger runners only) | Poor: documented delays and drops; anecdotes of 17-26 min typical, hours worst case | 6 h per job | Native (any pip package) | Late/dropped runs; 60-day auto-disable in public repos; min interval 5 min |
| GitHub Actions via `workflow_dispatch` from an external scheduler ([REST docs](https://docs.github.com/en/rest/actions/workflows)) | $0 | No | Good*: starts when API is called, plus runner pickup and setup time (unmeasured) | 6 h per job | Native | Needs a PAT stored in the scheduler; two moving parts |
| Cloud Run job + Cloud Scheduler ([Run pricing](https://cloud.google.com/run/pricing), [Scheduler pricing](https://cloud.google.com/scheduler/pricing)) | $0 within free tier (3 scheduler jobs free) | Paid (Cloud NAT + reserved IP; ~single-digit $* to $40-50 per vendor estimate) | Good*: tz-aware cron (`Asia/Kolkata`), retries configurable | Scheduler attempt deadline up to 30 min; Cloud Run job tasks far longer | Native (container/buildpack) | Billing account required; retries default to 0 |
| AWS Lambda + EventBridge Scheduler ([Lambda pricing](https://aws.amazon.com/lambda/pricing/)) | $0 within always-free allowance (new accounts: 6-month credit Free plan, then must upgrade) | Paid (VPC + NAT Gateway + EIP ≈ $45/month in Mumbai*) | Good*: tz-aware cron, retry policy + DLQ | 15 min* (Lambda limit, not re-verified) | Native (package `requests` in zip/layer) | New-account free-plan expiry; static IP is expensive |
| Oracle Always Free VM ([Always Free docs](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm)) | $0 | **Yes** (VM public IPv4; reserved IP) | Excellent*: local cron/systemd timer | Unlimited (always-on) | Native (full Linux) | Idle reclamation unless PAYG; Arm quota halved in 2026; capacity and termination anecdotes |
| Cloudflare Workers Cron Triggers ([limits](https://developers.cloudflare.com/workers/platform/limits/)) | $0 (5 cron triggers) / paid for real CPU | No | Good* (UTC only) | Free: 10 ms CPU; Paid: 30 s-15 min CPU, 15 min wall | Pyodide Python Workers (GA Sep 2026 per press); `requests` support disputed | 10 ms CPU on free; best as a JS pinger |
| Vercel Cron Hobby ([docs](https://vercel.com/docs/cron-jobs/usage-and-pricing)) | $0 | No | Poor: once/day, ±59 min | Function limits (see Vercel researcher) | Python functions supported | Cannot hit 15:10 reliably; Pro $20/user/month for per-minute |
| Modal ([pricing](https://modal.com/pricing)) | $0 ($30/month credits; 5 deployed crons) | No* (paid feature) | Good* (cron) | Long (configurable timeouts)* | Python-native | Credits/limits are a vendor promotion that can change |
| Supabase pg_cron + pg_net ([docs](https://supabase.com/docs/guides/database/extensions/pg_net)) | $0 (already in the stack) | No | Good (pg_cron, down to seconds) | n/a (SQL / HTTP trigger only) | No (SQL; Edge Functions are TypeScript) | Fire-and-forget HTTP, no retry/alert on failure |
| cron-job.org -> any HTTPS endpoint ([FAQ](https://cron-job.org/en/faq/)) | $0 | n/a (it is only the trigger) | Good: up to 1/min | 30 s HTTP timeout | n/a | Auto-disables after repeated failures; volunteer-run service |
| Upstash QStash ([pricing](https://upstash.com/pricing/qstash)) | $0 (1,000 msgs/day, 10 schedules) | n/a (trigger) | Good* (cron schedules, retries) | Endpoint-dependent | n/a | Free limits changed over time; verify |
| PythonAnywhere ([pricing](https://www.pythonanywhere.com/pricing/)) | $10/month for scheduled tasks (new free accounts: none) | No* | Daily/hourly tasks at a set minute* | CPU-seconds quota | Native | No longer free for scheduling; outbound allowlist on free |
| Render cron job ([docs](https://render.com/docs/cronjobs)) | From $1/month minimum per cron service | No* (paid add-ons) | Good* | Long | Native | Not free |
| Google Apps Script trigger ([docs](https://developers.google.com/apps-script/reference/script/clock-trigger-builder)) | $0 | No | Poor: ±15 min | 6 min/run, ~90 min/day | No (JavaScript; can call HTTPS) | Imprecise |
| Laptop (Task Scheduler / launchd / systemd) (see B1-B3) | $0 | No (home ISP IP, usually dynamic) | Excellent when awake; unreliable when asleep/lid closed | Unlimited | Native | Sleep, Wi-Fi, power, reboots |

### Inferences
- Recommended layering for this bot: (1) primary = a machine with a stable IP if live orders need it (Oracle free VM on PAYG, or a small paid VPS), else Cloud Run + Cloud Scheduler or Modal; (2) secondary = laptop task or GitHub `workflow_dispatch` fired by Supabase pg_cron a few minutes later; (3) the idempotency marker in Supabase makes double-firing harmless; (4) a dead-man alert at 15:20 IST catches total failure.

### Gaps
- Rows marked * need verification before being presented as fact; several runtime limits (Lambda 15 min, Modal timeouts) come from prior knowledge rather than a page opened in this session.

---

## B1. Windows 10/11 — Task Scheduler

### Takeaway
Use `Register-ScheduledTask` (not plain `schtasks`) so that wake, catch-up and battery options can be set; even then, laptops using Modern Standby (S0) frequently ignore wake timers on battery or with the lid closed, so the task is only dependable if the laptop is awake and plugged in around 15:10 — pair it with "start when available", a second trigger, and the script-side cutoff.

### Cited Findings
- `schtasks /create` syntax: `/sc weekly` with `/d MON,TUE,WED,THU,FRI` (valid values MON-SUN; `/d` is valid only with weekly or monthly schedules), `/st` start time in 24-hour `HH:MM`, `/tn` name, `/tr` command, `/ru` run-as account. [snippet] — [Microsoft Learn: schtasks create](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-create)
- **Command [composed]** — per [schtasks create](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-create):

  ```bat
  schtasks /Create /TN "ThunderBot\Daily1510" /TR "C:\thunderbot\run_bot.cmd" ^
    /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 15:10 /F
  ```
- `New-ScheduledTaskSettingsSet` exposes `-WakeToRun` (Task Scheduler wakes the computer before running the task), `-StartWhenAvailable` (the task can run at any time after its scheduled time has passed), `-AllowStartIfOnBatteries` (start even on battery power) and `-DontStopIfGoingOnBatteries`. [snippet; fuller wording from older versions of the page] — [Microsoft Learn: New-ScheduledTaskSettingsSet](https://learn.microsoft.com/en-us/powershell/module/scheduledtasks/new-scheduledtasksettingsset)
- With `StartWhenAvailable`, a missed task is queued and started after a delay; "the default delay is 10 minutes" per the TaskSettings documentation as summarised. [snippet] — [Microsoft Learn: TaskSettings.StartWhenAvailable](https://learn.microsoft.com/en-us/windows/win32/TaskSchd/tasksettings-startwhenavailable)
- **PowerShell [composed]** — per [New-ScheduledTaskSettingsSet](https://learn.microsoft.com/en-us/powershell/module/scheduledtasks/new-scheduledtasksettingsset) and [New-ScheduledTask](https://learn.microsoft.com/en-us/powershell/module/scheduledtasks/new-scheduledtask):

  ```powershell
  # C:\thunderbot\run_bot.cmd  (wrapper: venv python + log file)
  #   @echo off
  #   cd /d C:\thunderbot
  #   ".venv\Scripts\python.exe" -u bot.py >> "logs\bot.log" 2>&1

  $days    = 'Monday','Tuesday','Wednesday','Thursday','Friday'
  $action  = New-ScheduledTaskAction -Execute 'C:\thunderbot\run_bot.cmd' -WorkingDirectory 'C:\thunderbot'
  $t1      = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $days -At '15:10'
  $t2      = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $days -At '15:20'   # second attempt
  $set     = New-ScheduledTaskSettingsSet -WakeToRun -StartWhenAvailable `
               -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
               -MultipleInstances IgnoreNew `
               -ExecutionTimeLimit (New-TimeSpan -Minutes 10) `
               -RestartCount 2 -RestartInterval (New-TimeSpan -Minutes 1)

  # (a) simplest: runs only while you are logged on
  Register-ScheduledTask -TaskName 'Daily1510' -TaskPath '\ThunderBot\' `
    -Action $action -Trigger $t1,$t2 -Settings $set

  # (b) "Run whether user is logged on or not" without storing a password (run from an elevated prompt)
  $prin = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType S4U -RunLevel Limited
  Register-ScheduledTask -TaskName 'Daily1510' -TaskPath '\ThunderBot\' `
    -Action $action -Trigger $t1,$t2 -Settings $set -Principal $prin -Force

  # test and inspect
  Start-ScheduledTask -TaskPath '\ThunderBot\' -TaskName 'Daily1510'
  Get-ScheduledTaskInfo -TaskPath '\ThunderBot\' -TaskName 'Daily1510'   # LastRunTime, LastTaskResult, NextRunTime
  ```
- **Wake timers must be allowed in the power plan:** Microsoft's guidance for the "Wake the computer to run this task" option: Power Options -> Sleep -> "Allow wake timers" -> Enable. [snippet] — [Microsoft Support KB 973454](https://support.microsoft.com/help/973454). Equivalent commands [composed]:

  ```bat
  powercfg /setacvalueindex SCHEME_CURRENT SUB_SLEEP RTCWAKE 1
  powercfg /setdcvalueindex SCHEME_CURRENT SUB_SLEEP RTCWAKE 1
  powercfg /setactive SCHEME_CURRENT
  powercfg /a            & rem shows whether the laptop uses "Standby (S0 Low Power Idle)" = Modern Standby
  powercfg /waketimers   & rem lists armed wake timers (run as administrator)
  ```
- **Modern Standby unreliability (candid):** a Microsoft Q&A user reports that Modern Standby does not wake from sleep via the wake timer (while the Windows 11 Clock app alarm can wake the same PC); a Dell Latitude thread reports tasks and wake timers failing to trigger from S0 Modern Standby and from hibernate without AC, but working reliably on AC power; HP threads report "Scheduled task does not wake laptop reliably". Workarounds reported: set "Sleep after" to Never (let only the display turn off), keep the machine on AC, and rely on "Run task as soon as possible after a scheduled start is missed". No official Microsoft statement that wake timers are unsupported in Modern Standby was found. [snippet, forum evidence] — [Microsoft Q&A: waking a Modern Standby PC](https://learn.microsoft.com/en-us/answers/questions/1660115/regarding-waking-up-from-sleep-on-a-modern-standby); [Dell community: Wake Timers and Task Schedules do not trigger in S0](https://www.dell.com/community/Latitude/Wake-Timers-and-Task-Schedules-do-not-trigger-in-S0-Power-State/m-p/8310145); [HP community](https://h30434.www3.hp.com/t5/Notebook-Operating-System-and-Recovery/Scheduled-task-does-not-wake-laptop-reliably/m-p/9564506); [ElevenForum: Modern Standby - Scheduled Tasks](https://www.elevenforum.com/t/modern-standby-scheduled-tasks.16749/post-323260)

### Inferences
- Plain `schtasks /Create` has no switches for wake-to-run, start-when-available or battery behaviour, and tasks it creates default to "start only on AC power / stop if switching to battery"; that default alone silently skips a laptop on battery. Hence the PowerShell route (or exporting/importing task XML). (Long-standing behaviour; not re-verified on a fetched page.)
- `-StartWhenAvailable` means that opening the lid at 19:00 will run the 15:10 task at 19:00: the script MUST refuse to trade outside its window (B4).
- Task times are local wall-clock time: set Windows to India time (`tzutil /s "India Standard Time"`; check with `tzutil /g`) or convert 15:10 IST to the local zone; if the laptop travels, the task follows the new local time unless the trigger is created with "Synchronize across time zones".
- `-LogonType S4U` runs without an interactive session and without a stored password; it has no Windows network credentials, which does not matter for outbound HTTPS to Supabase/broker APIs.
- I deliberately left out `-RunOnlyIfNetworkAvailable`: right after wake the network is often not yet up and the task would be skipped; a retry loop in the script is more robust.
- WSL caveats: cron inside WSL2 only runs while the WSL VM is running (it shuts down when idle and is not started at boot by default), and WSL2's clock can drift after host sleep; schedule from Windows Task Scheduler instead, with the action `wsl.exe -d Ubuntu -- /home/USER/thunderbot/run.sh` if the code lives in WSL.
- On Windows, Python's `zoneinfo` needs `pip install tzdata` for `ZoneInfo("Asia/Kolkata")` to work.

### Gaps
- Exact current wording of each `New-ScheduledTaskSettingsSet` switch could not be quoted (learn.microsoft.com unreachable); `-DontStopIfGoingOnBatteries` in particular had no description in the search results.
- No authoritative Microsoft document on Task Scheduler wake behaviour under Modern Standby (DC power, lid closed) was found; evidence is forum reports. Must be tested on the actual laptop: schedule a test task 10 minutes ahead, sleep/close the lid on battery, check `Get-ScheduledTaskInfo`.

---

## B2. macOS (Sonoma / Sequoia / Tahoe) — launchd

### Takeaway
A per-user LaunchAgent with `StartCalendarInterval` is the right tool: unlike cron it runs a missed job once on wake (but not if the Mac was powered off), and `pmset repeat wakeorpoweron` can wake the Mac shortly before; scheduled wake on a closed-lid, on-battery laptop is not dependable and I found no solid Apple Silicon confirmation.

### Cited Findings
- **Sleep behaviour (man page):** "Unlike cron which skips job invocations when the computer is asleep, launchd will start the job the next time the computer wakes up. If multiple intervals transpire before the computer is woken, those events will be coalesced into one event upon wake from sleep." [snippet of the man page text] — [launchd.plist(5), Apple open source](https://opensource.apple.com/source/launchd/launchd-258.1/launchd/src/launchd.plist.5.auto.html)
- **Powered off is different:** if the computer is turned off at the `StartCalendarInterval` time, the job is not run after power-on (unless e.g. `RunAtLoad` is set); Apple's guide makes the same point about a machine that is always off at the scheduled time. [snippet] — [Apple Developer Forums thread 52369](https://developer.apple.com/forums/thread/52369); [Apple: Scheduling Timed Jobs](https://developer.apple.com/library/mac/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/ScheduledJobs.html)
- **Plist [composed]** — keys per [launchd.plist(5)](https://opensource.apple.com/source/launchd/launchd-258.1/launchd/src/launchd.plist.5.auto.html) (Weekday 1-5 = Mon-Fri; times are system local time). Save as `~/Library/LaunchAgents/com.thunderbot.daily.plist`:

  ```xml
  <?xml version="1.0" encoding="UTF-8"?>
  <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
  <plist version="1.0">
  <dict>
    <key>Label</key>
    <string>com.thunderbot.daily</string>

    <key>ProgramArguments</key>
    <array>
      <string>/usr/bin/caffeinate</string>
      <string>-i</string>
      <string>/Users/USERNAME/thunderbot/.venv/bin/python</string>
      <string>-u</string>
      <string>/Users/USERNAME/thunderbot/bot.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/Users/USERNAME/thunderbot</string>

    <key>StartCalendarInterval</key>
    <array>
      <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>10</integer></dict>
      <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>10</integer></dict>
      <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>10</integer></dict>
      <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>10</integer></dict>
      <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>10</integer></dict>
      <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>20</integer></dict>
      <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>20</integer></dict>
      <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>20</integer></dict>
      <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>20</integer></dict>
      <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>20</integer></dict>
    </array>

    <key>StandardOutPath</key>
    <string>/Users/USERNAME/thunderbot/logs/bot.out.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/USERNAME/thunderbot/logs/bot.err.log</string>
  </dict>
  </plist>
  ```
- **Load/test commands [composed]** (modern `launchctl` subcommands; `$UID` works in zsh and bash):

  ```bash
  mkdir -p ~/thunderbot/logs
  plutil -lint ~/Library/LaunchAgents/com.thunderbot.daily.plist
  launchctl bootstrap gui/$UID ~/Library/LaunchAgents/com.thunderbot.daily.plist
  launchctl enable gui/$UID/com.thunderbot.daily
  launchctl kickstart -k gui/$UID/com.thunderbot.daily     # run once now to test
  launchctl print gui/$UID/com.thunderbot.daily            # state, last exit code
  launchctl bootout gui/$UID/com.thunderbot.daily          # unload (do this before editing, then bootstrap again)
  ```
- **Scheduled wake:** `pmset repeat` takes a type (`sleep`, `wake`, `poweron`, `shutdown`, `wakeorpoweron`), weekdays as a subset of `MTWRFSU`, and a time `hh:mm:ss`; only one pair of repeating events (one "power on" type and one "power off" type) can exist; `pmset -g sched` shows the schedule and `sudo pmset repeat cancel` removes it. [snippet] — [pmset(1) man page mirror](https://keith.github.io/xcode-man-pages/pmset.1.html); [Apple Support: Schedule your Mac to turn on or off in Terminal](https://support.apple.com/guide/mac-help/mchl40376151/mac)

  ```bash
  sudo pmset repeat wakeorpoweron MTWRF 15:05:00
  pmset -g sched
  pmset -g log | grep -i -E "wake|sleep" | tail -20      # afterwards: verify that it really woke
  ```
- **Reliability report (candid):** on macOS Sequoia 15.6, a user on battery found a scheduled `wakeorpoweron` fired after a ~15 s sleep but failed after sleeps of 1-3 minutes (machine stuck in a "Deep Idle" state); that machine was an Intel MacBook Pro 2020, cause unresolved. [snippet, single anecdote] — [Apple Community (Japan) thread 256125968](https://discussionsjapan.apple.com/thread/256125968)

### Inferences
- The LaunchAgent lives in the `gui/$UID` domain, so it only runs while that user is logged in (screen may be locked). After a reboot nobody has logged in yet -> no run; enable automatic login or accept this failure mode.
- Wrapping the command in `caffeinate -i` prevents idle sleep while the job runs, which matters after a scheduled wake because macOS goes back to sleep quickly when idle.
- Sequence on a sleeping Mac: 15:05 `pmset` wake -> launchd fires the 15:10 entry on time; if the wake fails, launchd runs the coalesced missed job whenever the lid is next opened, which may be hours later -> the script's cutoff check is mandatory.
- Why not cron: no run-on-wake, and since Catalina `cron` jobs touching protected folders need Full Disk Access granted to `/usr/sbin/cron`. For the LaunchAgent, keep the project outside `~/Documents`, `~/Desktop`, `~/Downloads` (privacy-protected folders) to avoid silent permission failures. (Prior knowledge; not sourced in this session.)
- `StartCalendarInterval` is evaluated in the system's local time zone; keep the Mac on India time or convert (prior knowledge; Apple docs not fetched).

### Gaps
- No reliable source confirms how `pmset repeat wakeorpoweron` behaves on Apple Silicon MacBooks with the lid closed and on battery under Sequoia/Tahoe, whether AC power is required, or how Power Nap interacts. Must be tested on the actual machine (schedule a wake 5 minutes ahead, close the lid, then read `pmset -g log`).
- The quoted man-page text is from an older open-source launchd release; the current `man launchd.plist` on the user's macOS version should be checked (wording has changed across versions).

---

## B3. Linux — systemd timers

### Takeaway
A systemd timer with `OnCalendar=... Asia/Kolkata`, `Persistent=true` and `AccuracySec=1s` is exact and catches up after downtime; waking a suspended laptop needs `WakeSystem=true` in a system-level (not user) timer and working RTC hardware, and bug reports show it does not always fire.

### Cited Findings
- **Time zone in `OnCalendar`:** "You can also specify a timezone at the end of the directive (use `timedatectl list-timezones` to list accepted values)", example `OnCalendar=*-*-* 02:00:00 Europe/Paris`; expressions can be validated with `systemd-analyze calendar`. [snippet] — [ArchWiki: systemd/Timers](https://wiki.archlinux.org/title/Systemd/Timers). An `Asia/Kolkata` example ("every Monday at 10:00 AM in the Asia/Kolkata timezone") is on the NixOS wiki. [snippet] — [NixOS Wiki: Systemd/timers](https://wiki.nixos.org/wiki/Systemd/timers)
- **`Persistent=`:** "Takes a boolean argument. If true, the time when the service unit was last triggered is stored on disk." A missed run (e.g. machine powered off) is triggered immediately when the timer is next activated; default is false. [snippet] — [systemd.timer(5), Debian manpages](https://manpages.debian.org/systemd.timer); [ArchWiki: systemd/Timers](https://wiki.archlinux.org/title/Systemd/Timers)
- **`WakeSystem=`:** a calendar event elapsing while suspended "will cause the system to wake up, provided the hardware supports it"; it works only for the system manager (privileged), not per-user units. [snippet] — [systemd.timer(5), Debian manpages](https://manpages.debian.org/systemd.timer); [Fedora discussion: systemd timers don't run when the system goes to sleep](https://discussion.fedoraproject.org/t/systemd-timers-cronjob-replacement-dont-run-when-the-system-goes-to-sleep/111773)
- **Known problems (candid):** Red Hat bug: "timer with WakeSystem=true does not count down in suspend"; Debian bug #811473: "timer with WakeSystem=yes doesn't always start the service it's supposed to trigger"; a Fedora user reports no wake at the specified time. [snippet] — [Red Hat Bugzilla 2240171](https://bugzilla.redhat.com/show_bug.cgi?id=2240171); [Debian bug #811473](https://lists.alioth.debian.org/pipermail/pkg-systemd-maintainers/2016-January/028962.html)
- **User timer [composed]** — directives per [systemd.timer(5)](https://manpages.debian.org/systemd.timer) and [ArchWiki](https://wiki.archlinux.org/title/Systemd/Timers):

  ```ini
  # ~/.config/systemd/user/thunderbot.service
  [Unit]
  Description=ThunderBot daily trading job

  [Service]
  Type=oneshot
  WorkingDirectory=%h/thunderbot
  ExecStart=%h/thunderbot/.venv/bin/python -u bot.py
  TimeoutStartSec=300
  ```

  ```ini
  # ~/.config/systemd/user/thunderbot.timer
  [Unit]
  Description=ThunderBot at 15:10 and 15:20 IST, Mon-Fri

  [Timer]
  OnCalendar=Mon..Fri *-*-* 15:10:00 Asia/Kolkata
  OnCalendar=Mon..Fri *-*-* 15:20:00 Asia/Kolkata
  Persistent=true
  AccuracySec=1s

  [Install]
  WantedBy=timers.target
  ```

  ```bash
  systemd-analyze calendar "Mon..Fri *-*-* 15:10:00 Asia/Kolkata"   # prints next elapse in local time and UTC
  systemctl --user daemon-reload
  systemctl --user enable --now thunderbot.timer
  systemctl --user list-timers thunderbot.timer
  systemctl --user start thunderbot.service                          # test run now
  journalctl --user -u thunderbot.service -n 50                      # output/logs
  sudo loginctl enable-linger "$USER"                                # run without an open login session
  ```
- **System-level variant that can wake from suspend [composed]** — place in `/etc/systemd/system/`, add `User=YOURUSER` and absolute paths to the service (plus `Wants=network-online.target` / `After=network-online.target`), and add to the timer:

  ```ini
  [Timer]
  OnCalendar=Mon..Fri *-*-* 15:08:00 Asia/Kolkata
  WakeSystem=true
  Persistent=true
  AccuracySec=1s
  ```
  then `sudo systemctl daemon-reload && sudo systemctl enable --now thunderbot.timer`.
- **cron vs anacron:** the ArchWiki comparison notes timers can catch up missed runs with `Persistent=true`, which plain cron cannot. [snippet] — [ArchWiki: systemd/Timers](https://wiki.archlinux.org/title/Systemd/cron_functionality)

### Inferences
- `AccuracySec` defaults to 1 minute, so without `AccuracySec=1s` the job may start up to a minute late (default per the man page from prior knowledge; not quoted from a fetched page).
- A calendar timer that elapsed during suspend fires on resume even without `Persistent=` (the real-time clock has jumped past the deadline); `Persistent=true` additionally covers power-off/reboot. Both produce late runs -> script cutoff required.
- User units cannot depend on system targets such as `network-online.target`; in the user variant the script should wait/retry for network itself.
- `loginctl enable-linger` keeps the user manager (and its timers) running without a login session, which matters on a headless or auto-booting machine.
- cron skips anything scheduled while the machine was asleep/off; anacron only guarantees "once per day/week" at no specific time, so neither can express "15:10, or catch up, but never after 15:25".
- `rtcwake` alternative when `WakeSystem=` misbehaves: arm the RTC explicitly before suspending, e.g. `sudo rtcwake -m no -l -t "$(date -d 'today 15:05' +%s)"` (sets the alarm only) or `sudo rtcwake -m mem -l -t "$(date -d 'tomorrow 15:05' +%s)"` (suspend now, wake then). Whether a closed-lid laptop stays awake depends on logind's lid-switch handling. (Command from prior knowledge of util-linux `rtcwake(8)`; no page retrieved.)

### Gaps
- freedesktop.org man pages could not be fetched; `systemd.time(7)` wording on time-zone suffixes and the `AccuracySec`/`WakeSystem` text are from mirrors' snippets and prior knowledge.
- No data on how reliably RTC wake works on the user's specific laptop/firmware; needs a test.

---

## B4. General reliability practices for a once-a-day trading job on a laptop

### Takeaway
Assume the scheduler will sometimes fire late, twice or not at all: make the job claim "today" atomically in Supabase, refuse to act outside a hard time window, schedule a second attempt, and have something that is not the laptop raise an alert by 15:20 IST if no run was recorded. Since 1 April 2026 SEBI's retail-algo framework makes a broker-whitelisted static IP a prerequisite for API orders, which a home connection or any free serverless platform usually cannot provide.

### Cited Findings
- **All three laptop schedulers produce late catch-up runs by design:** Windows `StartWhenAvailable` runs "at any time after its scheduled time has passed" ([Microsoft Learn](https://learn.microsoft.com/en-us/powershell/module/scheduledtasks/new-scheduledtasksettingsset)); launchd "will start the job the next time the computer wakes up" ([launchd.plist(5)](https://opensource.apple.com/source/launchd/launchd-258.1/launchd/src/launchd.plist.5.auto.html)); systemd `Persistent=true` triggers a missed run when the timer is next activated ([ArchWiki](https://wiki.archlinux.org/title/Systemd/Timers)). [snippets]
- **GitHub's own advice on timing:** "To decrease the chance of delay, schedule your workflow to run at a different time of the hour." [fetched] — [GitHub Docs](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
- **healthchecks.io (dead-man switch):** free Hobbyist plan covers 20 checks, 3 team members, 100 log entries per check; Supporter $5/month has the same limits; Business $20/month (100 checks). Checks can use a simple period or a cron expression with a time zone and grace time; integrations listed include email, Slack, Discord, Telegram and webhooks (not confirmed which are on the free plan). [snippet] — [healthchecks.io pricing](https://healthchecks.io/pricing); [Healthchecks docs: Configuring checks (self-hosted mirror)](https://healthchecks.sre.cfainstitute.org/docs/configuring_checks/)
- **pg_net is fire-and-forget:** responses land in `net._http_response` (kept ~6 hours) and failures are not retried, so a Supabase-side watchdog must itself be simple and checked. [snippet] — [Supabase docs: pg_net](https://supabase.com/docs/guides/database/extensions/pg_net)
- **Static IP for live orders (India):** SEBI's February 2025 circular on retail participation in algorithmic trading (cited as SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/0000013 — verify the number against the PDF) requires retail API users to register static IP address(es) with their broker; after two delays it became mandatory on 1 April 2026. Kotak Neo: order APIs "will accept requests only from whitelisted static IPs with a valid session created from the same IP". FYERS: applies to users running automated strategies via the API; below 10 orders per second no algo registration is needed but the static IP must still be whitelisted. 5paisa: restriction enforced from 1 April 2026. [snippet] — [Kotak Neo: Static IP whitelisting](https://www.kotakneo.com/platform/kotak-neo-trade-api/static-ip-details/); [FYERS notice](https://fyers.in/notice-board/new-sebi-framework-for-retail-algo-trading-from-april-01-2026/); [FYERS support article](https://support.fyers.in/portal/en/kb/articles/what-are-the-new-sebi-rules-for-retail-algo-trading-from-april-01-2026); [5paisa community](https://tradebetter.5paisa.com/t/important-update-sebi-algo-compliance-effective-1st-april/761); [Upstox community: Static IP setup guide](https://community.upstox.com/t/static-ip-setup-guide-for-api-traders/14683)
- **Yahoo Finance from shared IPs:** rate limiting is per IP and crumb; shared cloud hosts see 429s more often than home connections. [snippet, low-quality sources] — [Scrapfly guide](https://scrapfly.io/blog/posts/guide-to-yahoo-finance-api)

### Inferences
(Engineering recommendations derived from the findings above; the code is [composed] and untested.)

- **Idempotency via an atomic claim.** Create `job_runs(run_date date, job text, status text, started_at timestamptz default now(), primary key (run_date, job))`. The job's first action is an INSERT through PostgREST; a unique-violation (HTTP 409) means another runner already claimed today and this run exits. This makes "laptop + cloud fallback + second trigger" safe.
- **Hard window.** Never trade outside e.g. 15:05-15:25 IST regardless of why the process started (catch-up after wake, delayed GitHub run, manual click). On a late start: record `skipped_late` and alert.
- **Skeleton:**

  ```python
  import os, sys, time, requests
  from datetime import datetime, time as dtime
  from zoneinfo import ZoneInfo           # on Windows also: pip install tzdata

  IST = ZoneInfo("Asia/Kolkata")
  URL, KEY = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"]
  HDR = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
  HC  = os.environ.get("HC_PING_URL")     # e.g. https://hc-ping.com/<uuid>

  def alert(msg):                          # ntfy.sh topic or Telegram bot sendMessage
      try: requests.post("https://ntfy.sh/YOUR-SECRET-TOPIC", data=msg.encode(), timeout=10)
      except requests.RequestException: pass

  def wait_for_network(deadline_s=120):
      t0 = time.time()
      while time.time() - t0 < deadline_s:
          try:
              requests.get(f"{URL}/rest/v1/", headers=HDR, timeout=5); return True
          except requests.RequestException:
              time.sleep(5)
      return False

  now = datetime.now(IST)
  if now.weekday() >= 5:
      sys.exit(0)
  if not (dtime(15, 5) <= now.time() <= dtime(15, 25)):
      alert(f"thunderbot started outside window at {now:%H:%M} IST - NOT trading"); sys.exit(0)
  if not wait_for_network():
      alert("thunderbot: no network by deadline"); sys.exit(1)

  r = requests.post(f"{URL}/rest/v1/job_runs", headers=HDR, timeout=10,
                    json={"run_date": now.date().isoformat(), "job": "rotate", "status": "started"})
  if r.status_code == 409:                 # unique violation -> already claimed today
      sys.exit(0)
  r.raise_for_status()

  if HC: requests.get(HC + "/start", timeout=10)
  try:
      ...                                  # holiday check, signals, orders
      requests.patch(f"{URL}/rest/v1/job_runs?run_date=eq.{now.date()}&job=eq.rotate",
                     headers=HDR, json={"status": "done"}, timeout=10)
      if HC: requests.get(HC, timeout=10)
  except Exception as e:
      if HC: requests.get(HC + "/fail", timeout=10)
      alert(f"thunderbot FAILED: {e!r}"); raise
  ```
- **Second attempt.** Triggers at 15:10 and 15:20 (as in every config above) cost nothing once the claim row exists; additionally a login/wake-time trigger is harmless because of the window check.
- **Dead-man alert that does not depend on the laptop.** Option 1: a healthchecks.io check with cron schedule `10 15 * * 1-5`, time zone `Asia/Kolkata`, grace 10 minutes -> it alerts at ~15:20 if no success ping arrived. Option 2 (no new vendor) — Supabase watchdog:

  ```sql
  select cron.schedule('thunderbot-watchdog', '50 9 * * 1-5', $$   -- 09:50 UTC = 15:20 IST
    select net.http_post(
      url  := 'https://ntfy.sh/YOUR-SECRET-TOPIC',
      body := jsonb_build_object('alert', 'thunderbot has NOT completed today'))
    where not exists (
      select 1 from job_runs
      where run_date = (now() at time zone 'Asia/Kolkata')::date and job = 'rotate' and status = 'done');
  $$);
  ```
  (For Telegram use `https://api.telegram.org/bot<TOKEN>/sendMessage` with `jsonb_build_object('chat_id', <id>, 'text', '...')`.) Because pg_net does not retry, option 1 and option 2 together are stronger than either alone.
- **Escalation instead of only alerting:** the 15:20 watchdog can call the GitHub `workflow_dispatch` endpoint (A1) or a Cloud Run URL so the cloud fallback runs the job itself while there are still ~5 minutes before the cutoff; the claim row prevents a double trade if the laptop wakes at the same moment. Note the fallback then trades from a non-whitelisted IP unless it runs on the static-IP machine.
- **Clock sync:** a wrong laptop clock defeats both the trigger and the window check; keep automatic time on (Windows: `w32tm /resync`, `w32tm /query /status`; macOS: "Set time and date automatically"; Linux: `timedatectl set-ntp true`, `timedatectl status`). The Supabase-side date check (`now() at time zone 'Asia/Kolkata'`) gives an independent clock for the marker.
- **Holidays:** schedulers only know weekdays. Keep an NSE trading-holiday table in Supabase (refreshed yearly from the exchange circular) and have both the job and the watchdog skip those dates; otherwise the watchdog alerts on every holiday and the job may act on stale prices. Also handle special sessions (e.g. Muhurat trading, rare Saturday sessions) explicitly.
- **Network on wake:** Wi-Fi often reconnects 5-30 s after wake; the retry loop above (2 minutes) is safer than a scheduler-level "only if network available" condition, which simply skips the run.
- **Home IP implications:** a typical home broadband IP is dynamic (often behind carrier-grade NAT), so it cannot be whitelisted reliably for order APIs; options are an ISP static-IP add-on, or sending order calls through a machine with a fixed public IP (Oracle free VM, a cheap VPS, or a paid NAT/proxy). Data-only jobs (fetch prices, write signals to Supabase) do not need this.
- **Candid bottom line on laptops:** timing is exact only while the laptop is awake, on power and online; closed-lid/battery wake is unreliable on Windows Modern Standby, unproven on Apple Silicon and firmware-dependent on Linux. A laptop is a good secondary runner or a fine primary only for someone at the desk at 15:10; unattended daily trading needs an always-on machine or a managed scheduler plus the alert.

### Gaps
- Per-broker specifics (how many IPs, change frequency, whether the user's broker enforces IP checks on all order endpoints) were not confirmed for Zerodha, Dhan or Upstox from their own documentation; third-party posts conflict.
- healthchecks.io free-plan integration list (Telegram on free?) and ping URL format were not verified on the live site (host unreachable); the `hc-ping.com/<uuid>` with `/start` and `/fail` suffixes is from prior knowledge.
- ntfy.sh and Telegram Bot API usage shown above is from prior knowledge; no pages retrieved.
- No NSE holiday-calendar source was researched here.
