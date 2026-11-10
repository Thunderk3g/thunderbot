# Fallback schedulers (free hosted options) and running Thunderbot on the owner's laptop

> As-of date for everything below: **10 November 2026**.
> Workload assumed: Python worker (pandas/numpy), 10-120 s per run, target 15:10 IST = 09:40 UTC Mon-Fri, state in Supabase Postgres.
>
> **Source-access caveat (read first).** In this research session `docs.github.com`, `github.blog` and `docs.oracle.com` could not be fetched at all (blocked by the session network policy), and `cloud.google.com` pricing pages came back truncated. Facts for those vendors therefore come from web-search extracts of the official pages and from secondary write-ups; each is labelled. Items tagged **[PRIOR]** are from the researcher's background knowledge (training cut-off mid-2026) and were *not* re-verified against a live page today - treat them as "check before relying on". All command/config blocks are **templates assembled from documented options; none were executed in this session.**

---

## 1. GitHub Actions scheduled workflows as a fallback scheduler

### Takeaway
Free and fully capable of running a 2-minute pandas job (public repo: free; private repo: about 2,000 included min/month on the Free plan), and since late March 2026 it reportedly accepts an IANA `timezone:` next to each `cron:` entry - but GitHub itself documents that scheduled runs can be delayed or even dropped under load, there is no fixed outbound IP on the free tier, and public-repo schedules are auto-disabled after 60 days of inactivity. Use it only with "fire early + wait in-job + idempotent catch-up cron + dead-man alert", never as the sole trigger for a time-critical order.

**COST:** $0 (public repo, standard runners) / $0 within about 2,000 min/month (private, Free plan).
**FIXED OUTBOUND IP:** No on free/standard runners. Static IP ranges exist only for paid *larger runners*, and current docs say that feature requires GitHub Enterprise Cloud.
**RELIABILITY / TIMING:** Poor precision - officially "can be delayed", jobs "may be dropped"; not suitable alone for a 15-minute pre-close window.

### Cited Findings
- **Timezone support added (2026).** GitHub's "GitHub Actions: Late March 2026 updates" changelog lists timezone support for scheduled workflows; secondary guides describe a per-entry `timezone:` field taking an IANA zone name beside each `cron:` line, defaulting to UTC when omitted. actionlint v1.7.12 (2026-03-30) added validation of the IANA timezone string. *Caveat: the official changelog/docs could not be opened here; secondary guides cite two different changelog dates (2026-03-19 and 2026-03-26), so syntax details are from third-party summaries.* - [GitHub changelog (URL as surfaced by search)](https://github.blog/changelog/2026-03-26-github-actions-late-march-2026-updates); [itime.day guide](https://itime.day/articles/github-actions-cron-timezone); [issoh.co.jp guide](https://www.issoh.co.jp/tech/details/16925/); [cronuru GitHub Actions cron dialect](https://cronuru.com/dialects/github-actions)
- **Documented delays and drops.** Official docs wording (seen via a GitHub Enterprise Server docs page / docs-repo mirror): "The schedule event can be delayed during periods of high loads of GitHub Actions workflow runs. High load times include the start of every hour. If the load is sufficiently high enough, some queued jobs may be dropped." The docs suggest scheduling at a minute other than :00. - [GitHub docs, events that trigger workflows (canonical page, not directly opened)](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows); [runhooks.app write-up](https://runhooks.app/blog/github-actions-scheduled-workflows-unreliable/); [HackerNoon: "Your GitHub Actions cron job can disappear without failing"](https://hackernoon.com/your-github-actions-cron-job-can-disappear-without-failing)
- **Minimum interval 5 minutes; no `@daily`-style macros.** - [cronuru dialect page](https://cronuru.com/dialects/github-actions); [cronuru guide](https://cronuru.com/guides/github-actions-scheduled-workflows)
- **Schedules run only from the default branch.** - [GitHub community discussion 201738 citing the docs](https://github.com/orgs/community/discussions/201738)
- **60-day auto-disable.** Secondary sources state GitHub disables scheduled workflows *in public repositories* after 60 days without repository activity (commits, issues, PRs, etc.). - [cronuru guide](https://cronuru.com/guides/github-actions-scheduled-workflows); [issoh.co.jp guide](https://www.issoh.co.jp/tech/details/16925/); [cronsignal troubleshooting](https://cronsignal.pages.dev/troubleshoot/github-actions-cron-not-running)
- **2026 pricing changes.** From 1 Jan 2026 GitHub cut GitHub-hosted runner prices by up to about 39% and introduced a $0.002/min "Actions cloud platform charge" that is already included in the reduced hosted-runner meter price; "runner usage in public repositories will remain free". The planned $0.002/min charge for *self-hosted* runners from 1 Mar 2026 was **postponed** with no new date. - [GitHub changelog 2025-12-16](https://github.blog/changelog/2025-12-16-coming-soon-simpler-pricing-and-a-better-experience-for-github-actions/); [GitHub resources: 2026 pricing changes](https://resources.github.com/actions/2026-pricing-changes-for-github-actions/); [DevClass](https://devclass.com/2025/12/17/github-to-charge-for-self-hosted-runners-from-march-2026/)
- **Included minutes.** Third-party 2026 pricing trackers still list 2,000 min/month + 500 MB artifact storage for private repos on GitHub Free (Linux 1x; Windows 2x; macOS 10x multipliers); standard runners on public repos free. - [cicdcalculator.com](https://cicdcalculator.com/github-actions-free-tier); [toolradar](https://toolradar.com/tools/github-actions/pricing)
- **Static IPs only on larger runners.** Static IP ranges are an opt-in feature of GitHub-hosted *larger* runners; current docs say the organisation must be on GitHub Enterprise Cloud (older blog posts mention Team + Enterprise); default cap of 10 larger runners with static ranges; two ranges assigned per runner. - [GitHub docs: manage larger runners](https://docs.github.com/en/actions/how-tos/manage-runners/larger-runners/manage-larger-runners); [GitHub changelog 2023-09-06](https://github.blog/changelog/2023-09-06-dual-static-ip-ranges-for-github-hosted-larger-runners)
- **Yahoo Finance from shared IPs.** yfinance users report HTTP 429 / `YFRateLimitError` even at the cookie/crumb step before any data request; Yahoo publishes no limits. - [yfinance issue 2480](https://github.com/ranaroussi/yfinance/issues/2480); [yfinance issue 2128](https://github.com/ranaroussi/yfinance/issues/2128); [yfinance discussion 2431](https://github.com/ranaroussi/yfinance/discussions/2431)

### Inferences
- **Budget check:** a 2-min job on 22 weekdays is about 44 min/month; even the "fire early and sleep about 28 min" pattern below costs about 22 x 30 = 660 min/month - inside 2,000 private minutes, and free in a public repo (but a public repo exposes strategy code and is subject to the 60-day disable rule).
- Because India has no DST, the UTC form `40 9 * * 1-5` is permanently correct; using the new `timezone:` key is optional. Prefer the UTC form for the fallback because it does not depend on a feature whose exact syntax could not be verified against GitHub's own page today.
- Timezone support changes *what time is requested*, not *how punctually GitHub starts the run*; the delay/drop caveat is unchanged.
- **Mitigation design:** (1) primary cron about 28 min early at an off-peak minute, job sleeps until 09:40 UTC; (2) second cron at 09:42 UTC as catch-up, which becomes a no-op thanks to the `runs` idempotency row (section 10); (3) the worker inspects the IST clock: before 15:25 IST trade normally, after that switch to AMO/next-day mode; (4) healthchecks.io dead-man alert.
- GitHub runner IPs are shared cloud addresses, so Yahoo/NSE throttling is plausible; no source found that confirms a blanket block of GitHub runner ranges. Design for retries and a secondary price source (broker API).
- **[PRIOR, unverified today]** job limit 6 h on GitHub-hosted runners; runners live in Azure with weekly-published dynamic IP ranges (`GET /meta`); secrets are encrypted repo/environment secrets exposed as `${{ secrets.X }}` and masked in logs; `workflow_dispatch` is triggered by `POST /repos/{owner}/{repo}/actions/workflows/{file}/dispatches` with body `{"ref":"main","inputs":{...}}` (204 response) and `repository_dispatch` by `POST /repos/{owner}/{repo}/dispatches` with `{"event_type":"backtest","client_payload":{...}}`; a fine-grained PAT needs Actions: write (workflow dispatch) or Contents: write (repository dispatch).

**Example workflow (template, untested; action major versions should be checked):**

```yaml
# .github/workflows/thunderbot.yml  (must be on the default branch)
name: thunderbot

on:
  schedule:
    # All UTC. IST has no DST, so 15:10 IST == 09:40 UTC all year.
    - cron: '12 9 * * 1-5'   # primary: fires ~14:42 IST, job then waits until 15:10 IST
    - cron: '42 9 * * 1-5'   # catch-up: ~15:12 IST; no-op if today's run row already exists
    # Reported 2026 alternative (verify syntax in GitHub docs before use):
    # - cron: '10 15 * * 1-5'
    #   timezone: 'Asia/Kolkata'
  workflow_dispatch:           # manual / dashboard-triggered runs and backtests
    inputs:
      mode:
        description: 'live | dry-run | backtest'
        type: choice
        options: [dry-run, live, backtest]
        default: dry-run
      params:
        description: 'JSON parameters for a backtest'
        required: false
        default: '{}'
  repository_dispatch:
    types: [backtest]

# One live run at a time; the catch-up cron queues behind the primary instead of racing it.
concurrency:
  group: thunderbot-${{ github.event_name == 'schedule' && 'live' || github.run_id }}
  cancel-in-progress: false

permissions:
  contents: read

jobs:
  run:
    runs-on: ubuntu-latest
    timeout-minutes: 45
    env:
      SUPABASE_DB_URL: ${{ secrets.SUPABASE_DB_URL }}
      BROKER_API_KEY: ${{ secrets.BROKER_API_KEY }}
      HC_PING_URL: ${{ secrets.HC_PING_URL }}
      RUN_SOURCE: gha
      MODE: ${{ github.event_name == 'schedule' && 'live' || inputs.mode || 'backtest' }}
      PARAMS: ${{ inputs.params || toJSON(github.event.client_payload) }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: pip                      # caches wheels keyed on requirements*.txt
      - run: pip install -r requirements.txt
      - name: Wait until 09:40 UTC (15:10 IST) if started early
        if: github.event_name == 'schedule'
        run: |
          target=$(date -u -d 'today 09:40' +%s); now=$(date -u +%s)
          if [ "$now" -lt "$target" ]; then sleep $(( target - now )); fi
      - name: Run worker (idempotent on strategy + trade_date)
        run: python -m thunderbot.worker --mode "$MODE" --params "$PARAMS"
      - name: Dead-man ping
        if: success() && github.event_name == 'schedule'
        run: curl -fsS -m 10 --retry 3 "$HC_PING_URL" > /dev/null
```

Dashboard trigger (template): `curl -X POST -H "Authorization: Bearer $GH_PAT" -H "Accept: application/vnd.github+json" https://api.github.com/repos/OWNER/REPO/actions/workflows/thunderbot.yml/dispatches -d '{"ref":"main","inputs":{"mode":"backtest","params":"{\"start\":\"2015-01-01\"}"}}'`

### Gaps
- Could not open docs.github.com / github.blog: exact official `timezone:` syntax, the exact 60-day wording (the public-repo-only scope comes from secondary sources; one GHES mirror states the rule without the "public" qualifier), the 6-hour job limit, current included-minutes table and the `/meta` IP guidance are not confirmed against live official pages today.
- No quantitative, authoritative statistics on real-world schedule delay (the commonly quoted "5-30+ minutes, occasionally skipped" is anecdotal; GitHub publishes no SLA for `schedule`).
- No source confirming or refuting that Yahoo Finance or nseindia.com block GitHub-hosted runner IP ranges specifically.

---

## 2. Google Cloud Run (jobs) + Cloud Scheduler

### Takeaway
The most precise free hosted option: Cloud Scheduler takes a native `--time-zone="Asia/Kolkata"` and calls the Cloud Run Jobs `:run` API; a 2-minute daily job uses about 1-2% of the monthly free allowance and 1 of 3 free Scheduler jobs. It needs a billing account with a card, and a fixed egress IP is *not* free (Cloud NAT is about $32/month before data).

**COST:** $0 in practice within the free tier (billing account + card required).
**FIXED OUTBOUND IP:** No by default (dynamic pool); yes via Direct VPC egress + Cloud NAT + reserved static IP, about $32/month for the NAT gateway plus about $0.045/GB plus the IP charge (third-party figures).
**RELIABILITY / TIMING:** High; a purpose-built cron service with configurable retries. No timing SLA figure was verified today.

### Cited Findings
- **Free tier numbers.** Cloud Run free usage per month: first 180,000 vCPU-seconds, first 360,000 GiB-seconds, 2 million requests (request-based services). Some Google pricing-page variants show 240,000 vCPU-seconds and 450,000 GiB-seconds for instance-based billing/jobs, "based on us-central1 pricing". The free tier is aggregated across projects by billing account, resets monthly, and is applied as a spending-based discount at Tier 1 pricing. *Extracted via search snippets of the official page; the page itself returned truncated.* - [Cloud Run pricing](https://cloud.google.com/run/pricing); [cloudchipr summary](https://cloudchipr.com/blog/cloud-run-pricing); [agentdeals GCP free tier 2026](https://agentdeals.dev/gcp-free-tier-2026)
- **Cloud Scheduler: 3 free jobs per billing account.** - [agentdeals GCP free tier 2026](https://agentdeals.dev/gcp-free-tier-2026); [Cloud Scheduler pricing (official, returned truncated)](https://cloud.google.com/scheduler/pricing)
- **Official scheduling pattern for jobs.** Create the Cloud Run job first, then `gcloud scheduler jobs create http SCHEDULER_JOB_NAME --location ... --schedule ... --uri` pointing at the Cloud Run Admin API `.../jobs/JOB-NAME:run`, authenticated with an OAuth service account; third-party guides add `--time-zone` and `--oauth-token-scope=https://www.googleapis.com/auth/cloud-platform`, and grant the scheduler's service account `roles/run.invoker` (or `roles/run.jobsExecutorWithOverrides`). Test with `gcloud run jobs execute` and `gcloud scheduler jobs run`. - [Cloud Run docs: execute jobs on a schedule](https://docs.cloud.google.com/run/docs/execute/jobs-on-schedule); [OneUptime guide, Feb 2026](https://oneuptime.com/blog/post/2026-02-17-how-to-configure-cloud-scheduler-to-trigger-cloud-run-jobs-on-a-schedule/view); [Cloud Run docs: running services on a schedule](https://docs.cloud.google.com/run/docs/triggering/using-scheduler)
- **Static egress.** Cloud Run uses a dynamic IP pool by default; for a fixed IP route all egress (`--vpc-egress=all-traffic`) through a VPC with a Cloud NAT gateway using a reserved static address; Google recommends Direct VPC egress over a connector; create the NAT *before* switching egress or the workload loses internet; subnet at least /26. - [Cloud Run docs: static outbound IP](https://docs.cloud.google.com/run/docs/configuring/static-outbound-ip); [OneUptime Direct VPC egress guide](https://oneuptime.com/blog/post/2026-02-17-how-to-configure-cloud-run-direct-vpc-egress-to-avoid-vpc-connector-throughput-limits/view)
- **NAT cost (third-party figure).** Cloud NAT about $0.044/hour (about $32/month) per gateway plus $0.045/GB processed. - [QuotaGuard: static IPs for Cloud Functions and Cloud Run](https://quotaguard.com/blog/google-cloud-functions-cloud-run-static-ip)

### Inferences
- **Usage maths:** 120 s x 1 vCPU x 22 runs = 2,640 vCPU-s/month (about 1.5% of 180,000) and, at 1 GiB, 2,640 GiB-s (under 1% of 360,000). Even if Mumbai is billed at Tier 2 rates and the free tier is credited at Tier 1 value, the overage is effectively zero at this scale.
- **[PRIOR, unverified today]** `asia-south1` (Mumbai) is a Tier 2 Cloud Run region; Cloud Scheduler beyond the free 3 jobs is $0.10/job/month; Cloud Run job task timeout default 10 min, max 24 h (longer for some configurations), services max 60 min per request; Artifact Registry has 0.5 GB free storage; Scheduler calling a Cloud Run *service* uses `--oidc-service-account-email` + `--oidc-token-audience`, whereas the *jobs* `:run` endpoint is a Google API and uses `--oauth-service-account-email`.
- Cheaper static-IP alternatives than NAT: (a) proxy only the broker calls through a free Oracle VM with a reserved IP (section 3); (b) place the order from the laptop on a home static IP (section 11); (c) a small always-on VM instead of serverless.

**Commands (template, untested):**

```bash
PROJECT_ID=your-project; REGION=asia-south1
gcloud services enable run.googleapis.com cloudscheduler.googleapis.com \
  artifactregistry.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com

# Secret (never bake into the image)
printf '%s' "$SUPABASE_DB_URL" | gcloud secrets create supabase-db-url --data-file=-

# Build from source and create the job (needs a Dockerfile or buildpack-compatible repo)
gcloud run jobs deploy thunderbot-job --source . --region "$REGION" \
  --cpu 1 --memory 1Gi --task-timeout 10m --max-retries 1 \
  --set-env-vars RUN_SOURCE=cloudrun,MODE=live \
  --set-secrets SUPABASE_DB_URL=supabase-db-url:latest

gcloud run jobs execute thunderbot-job --region "$REGION" --wait     # manual test

# Identity for the scheduler, allowed to run the job
gcloud iam service-accounts create thunderbot-scheduler
gcloud run jobs add-iam-policy-binding thunderbot-job --region "$REGION" \
  --member "serviceAccount:thunderbot-scheduler@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role roles/run.invoker

# 15:10 IST Mon-Fri, native timezone, with retries
gcloud scheduler jobs create http thunderbot-1510 --location "$REGION" \
  --schedule "10 15 * * 1-5" --time-zone "Asia/Kolkata" \
  --uri "https://run.googleapis.com/v2/projects/${PROJECT_ID}/locations/${REGION}/jobs/thunderbot-job:run" \
  --http-method POST \
  --oauth-service-account-email "thunderbot-scheduler@${PROJECT_ID}.iam.gserviceaccount.com" \
  --oauth-token-scope "https://www.googleapis.com/auth/cloud-platform" \
  --max-retry-attempts 3 --min-backoff 30s --max-backoff 120s --attempt-deadline 60s

gcloud scheduler jobs run thunderbot-1510 --location "$REGION"       # fire now to test
```

Static-IP add-on (only if required; about $32+/month): reserve an address (`gcloud compute addresses create thunderbot-ip --region $REGION`), create a router and NAT (`gcloud compute routers create ...`, `gcloud compute routers nats create ... --nat-external-ip-pool=thunderbot-ip --nat-all-subnet-ip-ranges`), then redeploy the job with `--network default --subnet default --vpc-egress all-traffic`.

### Gaps
- cloud.google.com pricing pages returned truncated: could not confirm today (a) whether the 180k/360k or 240k/450k allowance applies to *jobs*, (b) the Tier assignment of asia-south1, (c) Scheduler's per-job price and the exact free-tier wording, (d) Cloud NAT and static-IP prices from Google's own page.
- No verified figure for Cloud Scheduler firing precision (commonly "within seconds"; not sourced today).
- Cloud Scheduler region availability in asia-south1 not verified today.

---

## 3. Oracle Cloud Always Free VM

### Takeaway
The only free option found that plausibly gives a **free static public IPv4** (reserved public IP on an Always Free VM), which makes it attractive as a static-IP proxy for broker API calls - but it is an always-on server (which the owner wanted to avoid), needs a credit card, A1 capacity is often unavailable, and idle Always Free instances can be reclaimed.

**COST:** $0 (card required at sign-up).
**FIXED OUTBOUND IP:** Yes, free - reserved public IPv4 (community sources indicate a small reserved-IP limit on free tenancies).
**RELIABILITY / TIMING:** cron/systemd on a VM is second-accurate; the platform risks are provisioning ("out of host capacity") and idle reclamation.

### Cited Findings
- **Shapes.** Oracle's Always Free resource page still describes the Arm A1 allowance as 3,000 OCPU-hours and 18,000 GB-hours per month (equal to 4 OCPU / 24 GB running continuously). - [Oracle docs: Always Free Resources](https://docs.oracle.com/en-us/iaas/Content/FreeTier/resourceref.htm); [oracommit blog, Feb 2026](https://oracommit.blogspot.com/2026/02/understanding-oci-always-free-compute.html)
- **Conflicting claim of a 2026 cut.** One blog claims the A1 allowance was reduced to about 2 OCPU / 12 GB in 2026; this conflicts with Oracle's own resource page as surfaced by search and comes from a single low-authority source. - [braindetox.kr](https://braindetox.kr/en/posts/oracle_always_free_tier_reduced_2026.html); contradicted by [Oracle docs](https://docs.oracle.com/en-us/iaas/Content/FreeTier/resourceref.htm)
- **Idle reclamation.** Oracle evaluates Always Free compute over a 7-day period; an instance may be deemed idle when 95th-percentile CPU, network and (for A1) memory utilisation are all below 20%. One Korean-language source says 15%; a terms page mentions a 10-20% range. - [Oracle docs: Always Free Resources](https://docs.oracle.com/en-us/iaas/Content/FreeTier/resourceref.htm); [oracommit blog](https://oracommit.blogspot.com/2026/02/understanding-oci-always-free-compute.html)
- **"Out of host capacity".** Oracle's guidance is to try another availability domain or retry later; community users script repeated attempts. - [Oracle docs: Always Free Resources](https://docs.oracle.com/en-us/iaas/Content/FreeTier/resourceref.htm); [space-node 2026 limits article](https://space-node.net/blog/oracle-cloud-always-free-limits-2026)
- **Reserved public IPs.** A community answer says free tenancies can reserve 2 public IPs (plus use non-reserved ephemeral ones), quoting an Oracle doc line that tenancies get six public IPv4 addresses for Always Free compute; another user reported hitting a `reserved-public-ip-count` limit when reserving a second IP. - [Oracle community thread](https://community.oracle.com/CustomerConnect/discussion/592763/how-many-reserved-public-ip-can-i-make-in-the-free-tier); [Oracle docs: public IP addresses](https://docs.oracle.com/iaas/Content/Network/Tasks/managingpublicIPs.htm)

### Inferences
- A lightly used cron box (2 minutes of work a day) is exactly the profile the idle-reclamation rule targets. **[PRIOR]** The rule is generally understood to apply to tenancies that never upgraded to Pay-As-You-Go; upgrading to PAYG (still $0 if you stay inside Always Free) is the usual mitigation and also improves A1 capacity odds. Verify on Oracle's page.
- As a static-IP proxy: run a small authenticated forward proxy (or WireGuard/`ssh -D`) on the VM and route *only* broker API calls through it from Cloud Run / GitHub Actions / the laptop. This yields a fixed source IP for the broker allow-list at $0 but adds a single point of failure and a credential to protect.
- **[PRIOR, unverified today]** x86 allowance is 2 x VM.Standard.E2.1.Micro (1/8 OCPU, 1 GB each); India regions are Mumbai (`ap-mumbai-1`) and Hyderabad (`ap-hyderabad-1`); Always Free compute must be created in the tenancy's *home region*, which is chosen at sign-up and cannot be changed; a credit/debit card is required for verification; there are recurring community reports of accounts terminated without explanation.

**Scheduling on the VM (template):** prefer a systemd timer with `OnCalendar=Mon..Fri *-*-* 15:10:00 Asia/Kolkata` (full units in section 9). cron alternative:

```cron
# crontab -e   (CRON_TZ is a cronie feature: Oracle Linux/RHEL/Fedora. On Ubuntu/Debian verify
# support, or run `sudo timedatectl set-timezone Asia/Kolkata` and drop the CRON_TZ line.)
CRON_TZ=Asia/Kolkata
10 15 * * 1-5 /home/opc/thunderbot/.venv/bin/python -m thunderbot.worker --mode live >> /home/opc/thunderbot/cron.log 2>&1
```

### Gaps
- docs.oracle.com could not be opened: E2.1.Micro count, exact reclamation wording (including the PAYG exemption), India-region availability of Always Free shapes, the reserved-IP limit and outbound data allowance are not confirmed against the live page today.
- The claimed 2026 reduction of the A1 allowance is unresolved (one blog versus Oracle's page as indexed).
- Account-termination "horror stories" are anecdotal; no reliable frequency data found.

---

## 4. Cloudflare Workers with Python (Pyodide)

### Takeaway
Not feasible for a pandas job on the free plan: Workers Free allows only **10 ms CPU** per invocation, including each Cron Trigger run. On the $5/month paid plan CPU can be raised up to 5 minutes, so it becomes technically possible, but Python Workers are still described as open beta, run on Pyodide/WebAssembly with package and socket constraints, and offer no fixed egress IP - poor fit versus Cloud Run or Modal.

**COST:** Free plan unusable for this job; Workers Paid ($5/month **[PRIOR]**) would work.
**FIXED OUTBOUND IP:** No (egress from Cloudflare's shared ranges) **[PRIOR]**.
**RELIABILITY / TIMING:** Cron Triggers are reliable to about the minute (UTC), but the 10 ms CPU cap kills the run on Free.

### Cited Findings
- **CPU limits.** CPU time is 10 ms on Workers Free versus up to 5 min on Workers Paid; the 10 ms cap applies per HTTP request *and per Cron Trigger* on Free. Paid users can raise `cpu_ms` up to 300,000 ms (5 minutes) (default 30 s). - [Cloudflare Workers limits](https://developers.cloudflare.com/workers/platform/limits/); [Cloudflare changelog 2025-03-25: higher CPU limits](https://developers.cloudflare.com/changelog/post/2025-03-25-higher-cpu-limits/)
- **Other Free limits.** 100,000 requests/day; 50 subrequests per request; 5 Cron Triggers per account (250 on paid). - [Cloudflare Workers limits](https://developers.cloudflare.com/workers/platform/limits/); [Cloudflare Workers pricing](https://developers.cloudflare.com/workers/platform/pricing/)
- **Python status.** Cloudflare's Python Workers docs (seen via a docs preview mirror) still say the `python_workers` compatibility flag is required "while Python Workers are in open beta", and that `pywrangler` is the CLI for local runs, package installation and deployment. - [Cloudflare Python Workers docs](https://developers.cloudflare.com/workers/languages/python/); [docs preview mirror as surfaced](https://8818b16c.previews.developers.cloudflare.com/workers/languages/python/index.md)
- **Packages and cold start (secondary).** Third-party guides say pure-Python PyPI packages and Pyodide-built packages are supported (packages with unsupported C extensions fail), that pywrangler shipped 8 Dec 2025, and that cold starts are about 1 s with Wasm memory snapshots. - [skills.sh Cloudflare Python Workers summary](https://www.skills.sh/jezweb/claude-skills/cloudflare-python-workers); [agentpedia summary](https://agentpedia.codes/agent-skills/python/cloudflare-python-workers)

### Inferences
- numpy and pandas are Pyodide-built packages, so they should load, but merely importing pandas costs far more than 10 ms of CPU; a pandas cron on the Free plan would be terminated for exceeding CPU time. Verdict: **free plan no; paid plan possible but awkward**.
- **[PRIOR, unverified today]** 128 MB memory per isolate; no raw TCP sockets from Python (HTTP via the fetch shim, e.g. httpx/requests adapters; Postgres via Hyperdrive or the Supabase REST API rather than psycopg); Cron Triggers are UTC with 1-minute minimum granularity; Cloudflare Workflows exists for long multi-step tasks.

### Gaps
- No primary Cloudflare page confirming GA versus beta as of November 2026 beyond the docs-preview wording; no primary confirmation that pandas is on the supported package list today.
- Memory limit, socket constraints and the $5 price were not re-verified today.

---

## 5. Other free / near-free schedulers and hosts, and external "pingers"

### Takeaway
Best Python-native fallback is **Modal** ($30/month free credits, `modal.Cron`); the cheapest way to get precise, frequent triggering of an existing Vercel function is an external pinger - **cron-job.org** (free, 1-minute granularity, but about 30 s request timeout) or **Upstash QStash** (free tier 1,000 messages/day, 10 schedules, up to 15-minute response wait, retries, signed requests). None provides a free fixed outbound IP; Fly.io sells one for about $3.60/month.

### Cited Findings
- **Modal.** Starter plan is $0 with $30/month free compute credits, 3 seats, 100 containers, 1-day log retention; cron support is included but sources disagree on a cap (one blog: "5 cron jobs and 8 web endpoints"; another: "limited"). Static IP ("Proxy", up to 5 static IPs each) is for Team plan (1 proxy; Team is $250/month + compute) and Enterprise (3). - [Modal docs: proxy IPs](https://modal.com/docs/guide/proxy-ips); [costbench Modal free plan](https://www.costbench.com/software/ai-gpu-cloud/modal/free-plan/); [activepieces Modal pricing 2026](https://www.activepieces.com/blog/modal-labs-pricing-2026-gpu-rates-plans-and-credits)
- **AWS Lambda + EventBridge Scheduler.** Lambda always-free allowance: 1M requests and 400,000 GB-seconds per month, described as permanent; EventBridge Scheduler: 14,000,000 free invocations/month, then $1.00 per million; Scheduler supports time zones. (One blog claims the Scheduler free tier is 12-month only; AWS's page is authoritative and was not opened.) - [AWS EventBridge pricing](https://aws.amazon.com/eventbridge/pricing/); [AWS EventBridge Scheduler](https://aws.amazon.com/eventbridge/scheduler); [Wiz: Lambda cost breakdown 2026](https://www.wiz.io/academy/cloud-cost/aws-lambda-cost-breakdown)
- **Fly.io.** Static (app-scoped) egress IPs became billable from 1 Jan 2026 at about $0.005/hour, about $3.60/month per IPv4, allocated per region, up to 64 machines per IP; one review says there is no free plan for new accounts. - [Fly community: billing for app-scoped egress IPs](https://community.fly.io/t/billing-for-app-scoped-egress-ips-starts-jan-1-2026/26686); [QuotaGuard: Fly.io static outbound IP](https://www.quotaguard.com/blog/fly-io-static-outbound-ip); [toolpick Fly.io review](https://www.toolpick.dev/reviews/fly-io)
- **Render.** Cron jobs are billed per second of running time with "a minimum monthly charge of $1 per cron job service". - [Render docs: cron jobs](https://render.com/docs/cronjobs)
- **PythonAnywhere.** From January 2026 (US cut-over 15 Jan, EU 8 Jan) new free accounts lose scheduled tasks (moved to the paid Developer tier); the $5 Hacker plan was dropped and the base paid plan is $10/month; one pricing snippet still shows "1 daily task" on free, apparently for accounts created before the cut-over. - [PythonAnywhere blog: changes to free accounts](https://blog.pythonanywhere.com/221/); [PythonAnywhere blog: new plans](https://blog.pythonanywhere.com/222/); [PythonAnywhere pricing](https://www.pythonanywhere.com/pricing/)
- **cron-job.org.** Official FAQ: the service is entirely free; it calls your URL at the configured times and waits for it to finish. Third-party trackers: 1-minute minimum interval (up to 60 executions/hour per job), about 30-second request timeout, last 50 executions kept per job, unlimited jobs under fair use. - [cron-job.org FAQ](https://cron-job.org/faq/); [agentdeals cron-job.org](https://agentdeals.dev/vendor/cron-job-org); [freetier.co cron-job.org](https://freetier.co/directory/products/cron-joborg); [cron-job.org blog: timeout errors](https://blog.cron-job.org/service/2021/12/01/errors-explained-timeout.html)
- **Upstash QStash.** Free plan: $0, 1,000 messages/day (raised from 500), 1 MB max message size, **10 active schedules**, **max HTTP response duration 15 minutes**; QStash aborts a delivery attempt that exceeds the plan's max response duration and retries per its retry policy; pay-as-you-go is $1 per 100k messages. A third-party comparison says `CRON_TZ` is supported on the free tier. - [Upstash QStash pricing](https://upstash.com/pricing/qstash.md); [QStash retry docs](https://upstash.com/docs/qstash/features/retry); [Upstash blog Q&A](https://upstash.com/blog/qstash-qa); [merginit free cron comparison, June 2026](https://merginit.com/blog/26062026-free-cron-job-scheduler-comparison)
- **healthchecks.io (monitoring, not a scheduler).** Free Hobbyist tier: 20 checks, 100 log entries per check; Business $20/month (100 checks). - [toolradar healthchecks.io pricing](https://toolradar.com/tools/healthchecks-io/pricing); [Capterra healthchecks.io pricing](https://www.capterra.com/p/249957/Healthchecksio/pricing/)

### Inferences
- **Modal fit:** a 2-min CPU-only run 22 times a month costs cents, far inside $30 of credits. Template **[PRIOR syntax, verify]**:
  ```python
  import modal
  app = modal.App("thunderbot")
  image = modal.Image.debian_slim().pip_install("pandas", "numpy", "psycopg[binary]", "requests")

  @app.function(image=image, schedule=modal.Cron("40 9 * * 1-5"),   # UTC = 15:10 IST
                secrets=[modal.Secret.from_name("thunderbot")], timeout=600, retries=2)
  def daily():
      from thunderbot.worker import main
      main(mode="live", source="modal")
  # deploy: modal deploy thunderbot_modal.py
  ```
- **Pinger pattern for Vercel Hobby:** have cron-job.org or QStash call `https://<app>.vercel.app/api/run?...` at `10 15 * * 1-5` Asia/Kolkata with a shared-secret header (cron-job.org) or verify the `Upstash-Signature` header (QStash). cron-job.org's roughly 30 s timeout means a 10-120 s job must either return 202 immediately and continue in the background or be split into steps; QStash's 15-minute allowance comfortably covers the Vercel function's own max duration. Idempotency (section 10) makes retries safe.
- With QStash's 1,000 messages/day, an every-minute ping across the whole 09:15-15:30 IST session (375 messages) fits; every minute around the clock (1,440) does not.
- **[PRIOR, unverified today - one-liners requested by the brief]**
  - *Azure Functions (Consumption) timer trigger:* COST free grant of 1M executions + 400k GB-s/month; IP no (static needs NAT gateway on a paid plan); TIMING good, NCRONTAB, timezone via `WEBSITE_TIME_ZONE` (historically Windows plans only).
  - *AWS Lambda detail:* 15-min max run; pandas via layer or container image; static IP needs VPC + NAT gateway (roughly $32+/month); EventBridge Scheduler parameter is `ScheduleExpressionTimezone`.
  - *Fly.io detail:* machines can stop/scale to zero (pay per second, a few dollars a month at most for this job); Mumbai region `bom`; "scheduled machines" only offer coarse hourly/daily/weekly/monthly schedules without an exact time, so use an external trigger or an in-app scheduler.
  - *Railway:* cron supported; trial credit then $5/month Hobby; no static IP on Hobby.
  - *Koyeb:* small free instance exists; no native precise cron on free; no static IP.
  - *Deno Deploy (`Deno.cron`), Supabase `pg_cron` + Edge Functions, Val Town:* JS/TS runtimes only - fine as *triggers* that call a Python endpoint, not as hosts for pandas. `pg_cron` schedules are in UTC.
  - *EasyCron:* free tier is restrictive (few jobs, low frequency, short timeout); cron-job.org is the better free pinger.

### Gaps
- Modal's exact cron cap on Starter and whether `modal.Cron(..., timezone=...)` is available were not verified on modal.com.
- cron-job.org's timezone feature and exact timeout were not confirmed from its own FAQ text (30 s appears in several third-party sources and an older official blog post on timeouts).
- QStash `CRON_TZ` syntax not confirmed in official docs; a different Upstash page shows 500 messages/day (older figure).
- Azure Functions, Railway, Koyeb, Deno Deploy, Val Town, Supabase pg_cron, EasyCron: not researched this session (prior knowledge only).
- AWS NAT gateway price and the permanence of the EventBridge Scheduler free tier not verified on AWS's own page.
- healthchecks.io free-tier numbers are from aggregators, not its pricing page.

---

## 6. Compact comparison table

### Takeaway
For a free hosted fallback with accurate timing, Cloud Run Jobs + Cloud Scheduler is the strongest; Modal is the simplest for Python; GitHub Actions is the easiest but least punctual; only Oracle offers a free static IP and it is an always-on VM.

### Cited Findings
(Each cell summarises findings and sources given in sections 1-5; "[PRIOR]" = not verified today.)

| Option | Cost for this job | Fixed outbound IP | Timing precision / reliability | Key limits |
|---|---|---|---|---|
| **GitHub Actions `schedule`** | $0 (public) / within about 2,000 min/mo (private Free) | No (static ranges only on larger runners, Enterprise Cloud) | Weak: documented delays, possible dropped runs | 5-min minimum; default branch only; public-repo schedules disabled after 60 days inactivity; UTC by default (`timezone:` reported since Mar 2026) |
| **Cloud Run Jobs + Cloud Scheduler** | $0 within free tier; card required | No by default; about $32+/mo via Cloud NAT + reserved IP | Strong: dedicated scheduler, native `Asia/Kolkata`, retries | 180k vCPU-s + 360k GiB-s/mo free; 3 free Scheduler jobs per billing account |
| **Oracle Always Free VM** | $0; card required | **Yes, free reserved IPv4** | Strong (cron/systemd on a VM) but platform risk | Always-on server; A1 "out of host capacity"; idle reclamation (7 days under 20%); home-region lock [PRIOR] |
| **Cloudflare Python Workers** | Free plan unusable; $5/mo paid [PRIOR] | No [PRIOR] | Cron fine; job is killed by CPU cap on Free | 10 ms CPU on Free (5 min max on Paid); 5 cron triggers/account on Free; Pyodide; open beta |
| **Modal** | $0 within $30/mo credits | No on Starter (Proxy on Team, $250/mo) | Good [PRIOR]; Python-native `modal.Cron` | Cron cap on Starter unclear (possibly 5); 1-day logs |
| **AWS Lambda + EventBridge Scheduler** | $0 within always-free tier | No; VPC + NAT about $32+/mo [PRIOR] | Strong; timezone-aware schedules | 1M req + 400k GB-s/mo; 14M scheduler invocations/mo; 15-min max [PRIOR] |
| **Azure Functions timer** [PRIOR] | $0 within grant | No | Good | Consumption plan timeouts; timezone setting OS-dependent |
| **Fly.io** | No free tier for new accounts; a few $/mo | **Yes, about $3.60/mo** per egress IPv4 | Good with external trigger; built-in schedule is coarse [PRIOR] | `bom` region [PRIOR]; egress IP per region |
| **Render cron job** | From $1/mo minimum per cron service | No (not researched) | Good | Per-second billing with $1 minimum |
| **Railway / Koyeb** [PRIOR] | Trial or $5/mo / small free instance | No | Fair | Not researched today |
| **PythonAnywhere** | New free accounts: no scheduled tasks; paid from $10/mo | No | Daily task at a fixed time on paid | Hacker $5 plan discontinued (Jan 2026) |
| **cron-job.org -> Vercel function** | $0 | n/a (the Vercel function's IP applies; not fixed) | Good: 1-min granularity | About 30 s request timeout; 60 executions/hour per job |
| **Upstash QStash -> Vercel function** | $0 up to 1,000 msgs/day | n/a (as above) | Good: cron schedules, retries, signatures | 10 active schedules; 15-min max response; 1 MB message |
| **Deno Deploy / Supabase pg_cron / Val Town** [PRIOR] | $0 | No | Good as triggers | JS/TS only - cannot host pandas |
| **Own laptop (sections 7-9)** | $0 | Home ISP IP (static only if the ISP plan provides it) | Exact when awake; fails silently when asleep/off | Sleep/wake behaviour is the dominant risk |

### Inferences
- If a fixed IP is mandatory for order placement, the realistic low-cost choices are: Oracle free VM (as host or proxy), Fly.io egress IP (about $3.60/month plus compute), or the laptop on a home static IP; serverless NAT-based options cost roughly ten times more than Fly.io.
- If a fixed IP is *not* needed for the fallback's job (e.g. it only computes the signal and notifies), Cloud Run + Scheduler or Modal are the cleanest free choices.

### Gaps
- Table rows marked [PRIOR] were not verified today; Render's static-IP position was not researched.

---

## 7. Laptop: Windows 10/11 Task Scheduler

### Takeaway
Task Scheduler can run the job at 15:10 local time on weekdays, catch up after a missed start, retry on failure and attempt to wake the PC - but on Modern Standby (S0) laptops, wake timers are widely reported as unreliable (especially lid-closed or on battery), and nothing wakes a fully shut-down machine without a BIOS RTC alarm. Treat "wake to run" as best-effort and rely on catch-up plus the cloud dead-man check.

### Cited Findings
- A Microsoft Q&A answer states Modern Standby does not support waking from sleep via wake timers in the way S3 does; users are told to check sleep states with `powercfg /a`. - [Microsoft Q&A: waking from sleep on a Modern Standby PC](https://learn.microsoft.com/en-us/answers/questions/1660115/regarding-waking-up-from-sleep-on-a-modern-standby)
- Dell Latitude 5520 owners report wake timers and scheduled tasks not triggering in S0, and not from hibernate without AC power; schedules were reliable only on AC. - [Dell community thread](https://www.dell.com/community/Latitude/Wake-Timers-and-Task-Schedules-do-not-trigger-in-S0-Power-State/m-p/8310145)
- HP users report scheduled tasks not waking laptops reliably. - [HP community thread](https://h30434.www3.hp.com/t5/Notebook-Operating-System-and-Recovery/Scheduled-task-does-not-wake-laptop-reliably/m-p/9562014)
- Microsoft Tech Community thread "Scheduled Tasks in Modern Standby" documents the same class of problem; an Elevenforum user reports that once the *sleep* timeout (not just display-off) elapses, Modern Standby enters a phase where Task Scheduler cannot run user tasks (another user reports the opposite). - [Tech Community thread](https://techcommunity.microsoft.com/t5/windows-insider-program/scheduled-tasks-in-modern-standby/m-p/4202950); [Elevenforum thread](https://www.elevenforum.com/t/modern-standby-scheduled-tasks.16749/post-323401)
- A Veeam forum user obtained Modern Standby wakes by editing the task XML to add automatic-maintenance settings, confirmed with `powercfg /sleepstudy`. - [Veeam forum post](https://forums.veeam.com/viewtopic.php?p=506901)
- Guidance to confirm "Allow wake timers" is enabled for both battery and plugged-in states and to test with a trivial wake task first. - [GeekChamp guide](https://geekchamp.com/?p=227770)

### Inferences
- Practical reliability ranking on Windows: (1) laptop awake, on AC, lid open at 15:10 - reliable; (2) S3 sleep on AC with wake timers enabled - usually works; (3) Modern Standby, lid closed or on battery - unreliable; (4) hibernate / shut down - will not wake (except vendor BIOS "RTC wake/auto power-on", which is model-specific).
- Simplest robust habit: on trading days keep the laptop on AC with sleep disabled between about 15:00 and 15:30 (`powercfg /change standby-timeout-ac 0`), and let `StartWhenAvailable` plus the catch-up logic handle misses.
- `RunOnlyIfNetworkAvailable` can cause a start to be skipped when Wi-Fi has not reconnected right after wake; it is safer to omit it and let the script wait/retry for the network (section 10).
- **[PRIOR, unverified today]** all cmdlet/switch names below (ScheduledTasks module), the `RTCWAKE` powercfg alias, and that `schtasks /Create` has no switches for wake/catch-up (those need XML import).

**PowerShell (template, untested; run in an elevated PowerShell):**

```powershell
# Assumes the Windows clock/time zone is India Standard Time (check: Get-TimeZone).
$root    = "C:\thunderbot"
$action  = New-ScheduledTaskAction -Execute "$root\.venv\Scripts\python.exe" `
             -Argument "-m thunderbot.worker --mode live --source laptop" -WorkingDirectory $root
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 3:10PM
$settings = New-ScheduledTaskSettingsSet `
             -WakeToRun `                              # "Wake the computer to run this task"
             -StartWhenAvailable `                     # run ASAP after a missed start
             -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries `
             -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 2) `   # retry on failure
             -ExecutionTimeLimit (New-TimeSpan -Minutes 15) `               # stop if it hangs
             -MultipleInstances IgnoreNew
             # optional: -RunOnlyIfNetworkAvailable   (see caveat above)
# "Run whether user is logged on or not" without storing a password:
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType S4U -RunLevel Limited
Register-ScheduledTask -TaskName "Thunderbot-1510" -Action $action -Trigger $trigger `
                       -Settings $settings -Principal $principal -Force

Start-ScheduledTask -TaskName "Thunderbot-1510"          # test now
Get-ScheduledTaskInfo -TaskName "Thunderbot-1510"         # LastRunTime, LastTaskResult, NextRunTime
```

**Power settings and diagnostics (template):**

```bat
powercfg /a                         :: which sleep states exist: "Standby (S3)" vs "Standby (S0 Low Power Idle)"
:: Enable "Allow wake timers" on AC and on battery (0=disable, 1=enable, 2=important only)
powercfg /SETACVALUEINDEX SCHEME_CURRENT SUB_SLEEP RTCWAKE 1
powercfg /SETDCVALUEINDEX SCHEME_CURRENT SUB_SLEEP RTCWAKE 1
powercfg /SETACTIVE SCHEME_CURRENT
powercfg /waketimers                :: lists armed wake timers (the task should appear after sleep is requested)
powercfg -devicequery wake_armed    :: devices allowed to wake the PC
powercfg /lastwake                  :: what woke it last time
powercfg /sleepstudy                :: Modern Standby session report (HTML)
```

**schtasks equivalent:** basic creation is `schtasks /Create /TN "Thunderbot-1510" /TR "C:\thunderbot\run.cmd" /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 15:10 /F`, but wake/catch-up/retry are not exposed as switches; export the task (`schtasks /Query /TN "Thunderbot-1510" /XML > task.xml`), set the following inside `<Settings>`, and re-import with `schtasks /Create /TN "Thunderbot-1510" /XML task.xml /F`:

```xml
<WakeToRun>true</WakeToRun>
<StartWhenAvailable>true</StartWhenAvailable>
<DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
<StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
<ExecutionTimeLimit>PT15M</ExecutionTimeLimit>
<RestartOnFailure><Interval>PT2M</Interval><Count>3</Count></RestartOnFailure>
<MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
```

- **If the laptop is not on IST:** Task Scheduler triggers use local time. Either compute the local equivalent of 09:40 UTC (and remember it shifts in DST zones), or tick "Synchronize across time zones" on the trigger (XML `StartBoundary` with a `Z` suffix, e.g. `2026-11-11T09:40:00Z`) so the trigger is pinned to UTC. **[PRIOR]**
- **WSL:** a cron or systemd timer *inside* WSL2 only runs while the WSL VM is running, and the VM is stopped when idle and suspended with Windows. Schedule from Windows instead: action `wsl.exe` with arguments `-d Ubuntu -u YOU -- bash -lc "cd ~/thunderbot && .venv/bin/python -m thunderbot.worker --mode live"`. **[PRIOR]**

### Gaps
- No official Microsoft Learn documentation page (as opposed to Q&A/community threads) was retrieved for wake-timer behaviour under Modern Standby, for `New-ScheduledTaskSettingsSet`, `schtasks` or `powercfg`; the command syntax above is from prior knowledge and must be tested on the actual machine.
- No authoritative statement found on whether `StartWhenAvailable` reliably fires after resume from Modern Standby on battery.

---

## 8. Laptop: macOS (Sonoma / Sequoia / Tahoe 26) launchd

### Takeaway
Use a LaunchAgent with `StartCalendarInterval` (five weekday dicts): Apple documents that a calendar job missed while the Mac was *asleep* runs on wake (not if it was powered off), and `sudo pmset repeat wakeorpoweron MTWRF 15:08:00` can wake it beforehand - but developer reports say a lid-closed MacBook will not actually run the job until the lid is opened, and launchd gives no guarantee about power state. Wrap the command in `caffeinate` and keep the catch-up/dead-man logic.

### Cited Findings
- Apple's launchd guide: "If you schedule a launchd job by setting the StartCalendarInterval key and the computer is asleep when the job should have run, your job will run when the computer wakes up." (If the machine is off, the job is not run until the next scheduled time.) - [Apple: Scheduling Timed Jobs](https://developer.apple.com/library/mac/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/ScheduledJobs.html)
- 2026 Apple Developer Forums thread "launchd StartCalendarInterval behavior changed": with the lid open during sleep launchd runs the job (it may be suspended until full wake); with the lid closed the job does not run until the lid is opened; macOS 12 and earlier reportedly slept through the interval whereas macOS 15 and 26 dark-wake at it; a launchd engineer states launchd "doesn't guarantee anything about the power state of the system" when starting a `StartCalendarInterval` job. (Anecdotal; Apple silicon not specifically addressed.) - [Apple Developer Forums thread 815034](https://developer.apple.com/forums/thread/815034)
- `pmset` man page: `schedule` sets one-time power events, `repeat` sets daily/weekly events; "you may only have one pair of repeating events scheduled - a 'power on' event and a 'power off' event"; a new `pmset repeat` overwrites the previous one. Working example from Apple Communities: `sudo pmset repeat shutdown MTWRFSU 18:00:00 wakeorpoweron MTWRFSU 08:00:00`. - [pmset(1) man page](https://keith.github.io/xcode-man-pages/pmset.1.html); [Apple Communities thread](https://discussions.apple.com/thread/254870819)
- Write-ups on why cron misfires on a sleeping Mac and why launchd is preferred. - [dev.to: cron not working on Mac, the macOS sleep trap](https://dev.to/arjun_adhikari_4ac4ca1052/cron-not-working-on-mac-how-to-fix-the-macos-sleep-trap-with-launchd-3l4g); [josephspurrier.com: macOS sleep and cron](https://www.josephspurrier.com/macos-sleep-cron)

### Inferences
- Reliability ranking on a MacBook: awake or lid-open on AC - reliable; asleep with lid open - runs at/after a (dark) wake; lid closed, especially on battery - assume it will *not* run until opened; powered off - not run (only `pmset ... wakeorpoweron` on AC can start it, and Apple silicon laptops do not truly "power on" on schedule when shut down and lid-closed - unverified).
- `launchd` uses the system's local time zone and has no per-job timezone key, so the Mac's zone must be Asia/Kolkata or the Hour/Minute must be converted. **[PRIOR]**
- **[PRIOR, unverified today]** LaunchAgents run only while the user is logged in (use a LaunchDaemon in `/Library/LaunchDaemons` with `UserName` for no-login operation); files under `~/Documents`, `~/Desktop`, `~/Downloads` are TCC-protected, so keep the project and venv elsewhere (e.g. `~/thunderbot`) or grant Full Disk Access to the Python binary; launchd does not load the shell profile, so use absolute paths to the venv's `python` and set `PATH`/env vars in the plist; on recent macOS the user must also allow the item under System Settings > General > Login Items & Extensions; cron additionally needs Full Disk Access for `/usr/sbin/cron` and never catches up on missed runs.

**`~/Library/LaunchAgents/com.thunderbot.daily.plist` (template, untested):**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>com.thunderbot.daily</string>

  <!-- caffeinate -i keeps the Mac from idle-sleeping for the lifetime of the wrapped command -->
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/caffeinate</string><string>-i</string>
    <string>/Users/YOU/thunderbot/.venv/bin/python</string>
    <string>-m</string><string>thunderbot.worker</string>
    <string>--mode</string><string>live</string>
    <string>--source</string><string>laptop</string>
  </array>
  <key>WorkingDirectory</key><string>/Users/YOU/thunderbot</string>

  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key><string>/Users/YOU/thunderbot/.venv/bin:/usr/bin:/bin</string>
    <key>TZ</key><string>Asia/Kolkata</string>
  </dict>

  <!-- 15:10 local time, Monday(1)..Friday(5); system time zone must be Asia/Kolkata -->
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>10</integer></dict>
    <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>10</integer></dict>
    <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>10</integer></dict>
    <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>10</integer></dict>
    <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>10</integer></dict>
  </array>

  <key>StandardOutPath</key><string>/Users/YOU/Library/Logs/thunderbot/out.log</string>
  <key>StandardErrorPath</key><string>/Users/YOU/Library/Logs/thunderbot/err.log</string>
</dict>
</plist>
```

```bash
mkdir -p ~/Library/Logs/thunderbot
plutil -lint ~/Library/LaunchAgents/com.thunderbot.daily.plist
launchctl bootstrap gui/$UID ~/Library/LaunchAgents/com.thunderbot.daily.plist   # load
launchctl kickstart -k gui/$UID/com.thunderbot.daily                              # run once now (test)
launchctl print gui/$UID/com.thunderbot.daily | head -40                          # state, last exit code
launchctl bootout gui/$UID/com.thunderbot.daily                                   # unload (before editing)

# Wake (or power on) two minutes early on weekdays; needs sudo; only one repeat pair exists system-wide
sudo pmset repeat wakeorpoweron MTWRF 15:08:00
pmset -g sched            # show scheduled/repeating power events
sudo pmset repeat cancel  # remove
pmset -g log | grep -i -E "wake|darkwake" | tail   # what actually happened
```

### Gaps
- No Apple documentation found that states how `pmset repeat wakeorpoweron` behaves on a lid-closed, on-battery Apple silicon MacBook; behaviour described is from a developer-forum anecdote and inference. Power Nap behaviour was not researched.
- TCC/Full Disk Access and Login Items details are prior knowledge, not sourced today.
- The Apple launchd guide cited is an archived document; `man launchd.plist` on the target macOS should be checked for the same sentence.

---

## 9. Laptop: Linux systemd timer (and cron/anacron)

### Takeaway
A system-level systemd timer with `OnCalendar=Mon..Fri *-*-* 15:10:00 Asia/Kolkata`, `Persistent=true`, `WakeSystem=true` and `AccuracySec=1s` is the most capable laptop scheduler of the three OSes: IANA timezones are supported in calendar expressions, missed runs are caught up at next boot/activation, and the timer can wake the machine from suspend (not from power-off). The worker must still check the clock, because a "persistent" catch-up may fire hours late.

### Cited Findings
- `systemd.time(7)`: calendar events accept a timezone suffix - the literal `UTC`, the local timezone, or an IANA name such as `Asia/Tokyo` (list via `timedatectl list-timezones`); if omitted the local timezone is used. - [systemd.time man page (freedesktop.org, latest)](https://www.freedesktop.org/software/systemd/man/latest/systemd.time.html); [man7 mirror](https://man7.org/linux/man-pages/man7/systemd.time.7.html)
- `systemd.timer(5)`: `AccuracySec=` defaults to 1min and `RandomizedDelaySec=` to 0; `Persistent=` (default false) stores the last trigger time on disk and, when the timer is activated, triggers the service immediately if it would have been triggered at least once while the timer was inactive; `WakeSystem=` (boolean) makes an elapsing timer resume the system from suspend if the system supports it, using a clock that keeps advancing during suspend. - [systemd.timer man page (Debian)](https://manpages.debian.org/systemd.timer)
- `WakeSystem=` needs privileges: the systemd author noted WakeSystem timers require privileges, so a plain per-user timer does not wake the machine; the kernel rejects alarm timerfds without `CAP_WAKE_ALARM` (EPERM). Since systemd v254 user sessions are intended to receive `CAP_WAKE_ALARM`, but bugs show it missing for some UID ranges / directory-managed accounts. - [joeyh.name: a programmable alarm clock using systemd](https://joeyh.name/blog/entry/a_programmable_alarm_clock_using_systemd/); [KDE bug 506052](https://bugs.kde.org/show_bug.cgi?id=506052); [kernel commit: reject ALARM timerfds without CAP_WAKE_ALARM](https://lab.nexedi.com/kirr/linux/-/commit/2895a5e5b3ae78d9923a91fce405d4a2f32c4309)

### Inferences
- Install the units as **system** units (in `/etc/systemd/system`, with `User=` in the service) so `WakeSystem=true` has `CAP_WAKE_ALARM` regardless of distro/session quirks.
- `Persistent=true` fires the missed job as soon as the timer is next activated - that can be 20:00 the same day or Saturday morning. The worker must therefore decide by current IST time and trade date: before 15:25 IST on a trading day, trade; otherwise AMO/next-day/skip (section 10).
- `WakeSystem` wakes from suspend-to-RAM/s2idle if the RTC alarm works on the hardware; it cannot power on a machine that is shut down. For that, use firmware RTC wake set by `rtcwake` before powering off, e.g. `sudo rtcwake -m off -l -t "$(date -d 'tomorrow 15:05' +%s)"` (hardware/BIOS dependent). **[PRIOR]**
- **[PRIOR, unverified today]** `Restart=on-failure` is permitted for `Type=oneshot` services since systemd 244; `systemd-analyze calendar "<expr>"` validates the expression and prints the next elapse in local time and UTC; anacron only guarantees "once per day/week/month at some point after boot" with no time-of-day control, so it suits a post-close catch-up but not a 15:10 run; `CRON_TZ` is honoured by cronie (Fedora/RHEL/Arch) - check `man 5 crontab` on Debian/Ubuntu.

**`/etc/systemd/system/thunderbot.service` (template, untested):**

```ini
[Unit]
Description=Thunderbot daily run
Wants=network-online.target
After=network-online.target
StartLimitIntervalSec=900
StartLimitBurst=4

[Service]
Type=oneshot
User=YOU
WorkingDirectory=/home/YOU/thunderbot
EnvironmentFile=/home/YOU/thunderbot/.env
# After resume, network-online.target is already "reached"; wait explicitly for DNS/route (up to ~60 s)
ExecStartPre=/bin/sh -c 'for i in $(seq 1 30); do getent hosts api.supabase.com >/dev/null && exit 0; sleep 2; done; exit 1'
ExecStart=/home/YOU/thunderbot/.venv/bin/python -m thunderbot.worker --mode live --source laptop
TimeoutStartSec=900
Restart=on-failure
RestartSec=60
```

**`/etc/systemd/system/thunderbot.timer`:**

```ini
[Unit]
Description=Thunderbot at 15:10 IST Mon-Fri

[Timer]
OnCalendar=Mon..Fri *-*-* 15:10:00 Asia/Kolkata
Persistent=true
WakeSystem=true
AccuracySec=1s
RandomizedDelaySec=0
Unit=thunderbot.service

[Install]
WantedBy=timers.target
```

```bash
systemd-analyze calendar "Mon..Fri *-*-* 15:10:00 Asia/Kolkata"   # validate; shows next elapse + UTC
sudo systemctl daemon-reload
sudo systemctl enable --now thunderbot.timer
systemctl list-timers thunderbot.timer        # NEXT / LEFT / LAST
sudo systemctl start thunderbot.service       # manual test run
journalctl -u thunderbot.service -n 100 --no-pager
cat /sys/class/rtc/rtc0/wakealarm             # non-empty while a wake alarm is armed (during suspend prep)
```

**cron alternative:** `CRON_TZ=Asia/Kolkata` then `10 15 * * 1-5 /home/YOU/thunderbot/.venv/bin/python -m thunderbot.worker --mode live >> /home/YOU/thunderbot/cron.log 2>&1` - no wake, no catch-up, so strictly worse than the timer on a laptop.

### Gaps
- The freedesktop.org pages were surfaced through search, not opened; the timezone-suffix rule and `Persistent`/`WakeSystem` semantics are from search extracts of the man pages (some from older systemd versions on Debian mirrors).
- No source checked for `Restart=` with `Type=oneshot`, `rtcwake`, or `CRON_TZ` support by distro.
- Wake-from-suspend reliability on specific laptop hardware (s2idle versus S3) not researched.

---

## 10. Handling a missed run for this strategy (idempotency, alerts, holidays, clocks)

### Takeaway
Because the strategy decides monthly on daily prices and trades delivery, an occasional missed 15:10 run is recoverable: catch up before about 15:25 IST the same day, otherwise place an after-market order or act next session - the published evidence on "rebalance timing luck" says date shifts add noise (not expected loss), which is material only when persistent. What must be bullet-proof is *not double-trading*: a `(strategy, trade_date)` unique row in Postgres claimed before any order, plus a dead-man alert at 15:20 IST.

### Cited Findings
- **Rebalance timing luck (RTL).** RTL is the performance dispersion between otherwise identical strategies rebalanced on different schedules; in Hoffstein, Faber and Braun's 2020 work, constructed index strategies often showed RTL above 100 bp annualised, with one replicated value index showing calendar-year differentials above 40% from schedule choice alone; the effect is not mean-reverting, is larger with higher turnover / less frequent rebalancing / fewer constraints, and is diluted by 1/N when N staggered tranches are used. - [Newfound Research: the luck of the rebalance timing](https://blog.thinknewfound.com/2013/08/the-luck-of-the-rebalance-timing/); [CXO Advisory summary](https://www.cxoadvisory.com/?p=32143); [Nitin Gupta replication: luck in rebalance timing](https://nitingupta2.github.io/investing/luck-in-rebalance-timing)
- **NSE holiday data.** Community libraries call the unofficial endpoint `https://www.nseindia.com/api/holiday-master?type=trading` (also `type=clearing`) and read the list by segment key from the JSON; wrappers exist: `nse` package `holidays(type='trading'|'clearing')`, NseKit `nse_trading_holidays()`, nselib `trading_holiday_calendar`. These are scraped endpoints that need browser-like headers/cookies and can change without notice. Angel One's SmartAPI forum states the broker API does not provide market holidays. - [NseIndiaApi docs](https://bennythadikaran.github.io/NseIndiaApi/api.html); [nselib on PyPI](https://pypi.org/project/nselib); [NseKit on PyPI](https://pypi.org/project/NseKit/); [SmartAPI forum](https://smartapi.angelone.in/smartapi/forum/post/14721)
- **Dead-man monitoring.** healthchecks.io's free Hobbyist tier covers 20 checks with period/grace-time controls and a cron-expression editor. - [toolradar healthchecks.io pricing](https://toolradar.com/tools/healthchecks-io/pricing); [Capterra healthchecks.io](https://www.capterra.com/p/249957/Healthchecksio/pricing/)

### Inferences
- **(a) Same-day catch-up:** any trigger (laptop wake, GitHub catch-up cron, manual `workflow_dispatch`, phone-opened dashboard button) arriving before about 15:25 IST should run normally; the idempotency row makes it safe for all of them to fire.
- **(b) Missed entirely:** run after the close on final daily prices and either place an AMO for the next open or simply act at about 15:10 next session. This shifts execution by one trading day on a monthly signal. The RTL literature implies the *expected* cost is about zero while adding dispersion; a rare one-day slip is a far smaller perturbation than permanently choosing a different rebalance day (the case the 100 bp+/year figures describe). No study quantifying a one-day delay for a monthly Indian-equity momentum strategy was found. Log the slip (`intended_date`, `executed_date`) so tracking difference can be measured. **[PRIOR]** AMO windows and rules are broker-specific and should be confirmed with the chosen broker.
- **(c) Idempotency (template SQL):**
  ```sql
  create table if not exists runs (
    strategy     text        not null,
    trade_date   date        not null,           -- IST trading date
    status       text        not null default 'started',  -- started|succeeded|failed|skipped_holiday|amo_placed
    source       text        not null,           -- laptop|gha|cloudrun|modal|manual
    started_at   timestamptz not null default now(),
    finished_at  timestamptz,
    detail       jsonb,
    primary key (strategy, trade_date)
  );

  -- Step 1: claim. Exactly one caller gets a row back.
  insert into runs (strategy, trade_date, source)
  values ('thunderbot', (now() at time zone 'Asia/Kolkata')::date, $1)
  on conflict (strategy, trade_date) do nothing
  returning *;

  -- Step 2 (only if step 1 returned nothing): take over a failed or stale claim
  update runs set source = $1, status = 'started', started_at = now()
  where strategy = 'thunderbot'
    and trade_date = (now() at time zone 'Asia/Kolkata')::date
    and (status = 'failed' or (status = 'started' and started_at < now() - interval '10 minutes'))
  returning *;
  -- No row from either statement => another trigger owns today's run: exit 0.
  ```
  Add a second guard at the broker: a deterministic order tag / client order id such as `TB-YYYYMMDD-SYMBOL`, and check the broker's order book for that tag before placing. If using advisory locks through Supabase's transaction-mode pooler, use `pg_try_advisory_xact_lock(hashtext('thunderbot:' || trade_date))` inside one transaction rather than session-level locks **[PRIOR]**.
- **(d) Dead-man switch:** create a healthchecks.io check with schedule `10 15 * * 1-5`, timezone `Asia/Kolkata`, grace 10 minutes, so an alert (email/Telegram) fires at about 15:20 IST if no success ping arrived; the worker pings `https://hc-ping.com/<uuid>/start` at start, the bare URL on success and `/fail` on error **[PRIOR ping URL format]**. Holidays would raise false alarms unless the worker also pings "success (skipped_holiday)" - so let every trigger ping even when it no-ops. A second, independent check: a Supabase `pg_cron` job or GitHub cron at 09:50 UTC that queries `runs` and notifies if today's row is missing.
- **(e) Holidays:** load the year's NSE trading-holiday list into a Supabase table once a year (from the NSE circular / `holiday-master` endpoint via laptop, since nseindia.com is hostile to data-centre IPs), and have the worker check `is_trading_day(today)` first. Hand-maintain exceptions: special Saturday live sessions, Muhurat trading (evening session on Diwali) and ad-hoc closures are announced by circular and are *not* derivable from a weekday rule **[PRIOR]**. Month-end detection should use "last trading day of the month per the holiday table", not the calendar.
- **Network readiness on wake:** retry DNS + a cheap HTTPS call (e.g. Supabase health) with exponential backoff for about 60-90 s before failing; set explicit timeouts on every HTTP call; exit non-zero on failure so the OS scheduler's retry (Task Scheduler `RestartCount`, systemd `Restart=on-failure`) engages.
- **Clock/timezone pitfalls:** India has no DST, so 15:10 IST = 09:40 UTC year-round and UTC crons never drift; compute `trade_date` in `Asia/Kolkata` explicitly (never from server-local or UTC date); after long sleep make sure the OS has resynced time (NTP) before trusting "is it before 15:25?" - compare against the DB server's `now()` as the single source of truth for time.

### Gaps
- No direct empirical study found on the cost of a one-day execution delay for a monthly-rebalanced Indian equity strategy; the RTL sources concern US indices and tactical models.
- AMO timings/rules, special-session and Muhurat handling were not researched this session (prior knowledge only).
- Whether `pandas_market_calendars` / `exchange_calendars` carry an up-to-date NSE calendar was not verified.
- healthchecks.io cron/timezone/Telegram features and ping URL format were not confirmed on its own docs today.

---

## 11. The hybrid pattern: laptop + cloud

### Takeaway
Two workable hybrids: (A) **laptop primary, cloud watchdog** - the laptop (home IP, possibly static) runs and trades at 15:10, a free cloud job checks the `runs` table a few minutes later and alerts or takes over; (B) **cloud primary for signal + notification, human or laptop for execution** - Cloud Run/Modal/GitHub computes the signal on time and notifies, while the order is placed from the laptop or manually, so the cloud never needs a fixed IP. Both rest on the shared Postgres `runs` row for exactly-once behaviour.

### Cited Findings
- Hosted schedulers differ sharply in punctuality (GitHub documents delays/drops; Cloud Scheduler is a dedicated cron service with native timezone and retries). - [GitHub docs, schedule event](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows); [Cloud Run docs: execute jobs on a schedule](https://docs.cloud.google.com/run/docs/execute/jobs-on-schedule)
- Free fixed egress IP is available only via an Oracle Always Free VM; paid minimum found is Fly.io at about $3.60/month; serverless NAT is about $32/month. - [Oracle docs: public IP addresses](https://docs.oracle.com/iaas/Content/Network/Tasks/managingpublicIPs.htm); [Fly community: egress IP billing](https://community.fly.io/t/billing-for-app-scoped-egress-ips-starts-jan-1-2026/26686); [QuotaGuard: Cloud Run static IP cost](https://quotaguard.com/blog/google-cloud-functions-cloud-run-static-ip)
- Laptop wake-to-run is unreliable on Modern Standby Windows laptops and lid-closed MacBooks. - [Dell community thread](https://www.dell.com/community/Latitude/Wake-Timers-and-Task-Schedules-do-not-trigger-in-S0-Power-State/m-p/8310145); [Apple Developer Forums thread 815034](https://developer.apple.com/forums/thread/815034)

### Inferences
- **Pattern A (laptop primary):** laptop task at 15:10 IST -> claims `runs` row -> trades from the home IP. Cloud watchdog at 15:15 IST (Cloud Scheduler job, or QStash/cron-job.org hitting a Vercel function): if today's row is missing or stale, either (i) notify the owner by Telegram/email to act manually before 15:25, or (ii) run the worker itself in "signal-only" or full mode. On non-rebalance days (most days of the month) a miss costs nothing, so the watchdog only needs to be loud near month-end.
- **Pattern B (cloud primary):** cloud job computes the month-end signal at 15:10 IST and writes target orders to Postgres plus a push notification; execution is done by the laptop agent polling Postgres when awake, or by the human in the broker app. This avoids any fixed-IP requirement in the cloud and keeps broker credentials off third-party runners.
- Since the decision is monthly, the scheduler only truly matters on about 12 days a year; a calendar reminder on the last trading day of each month plus the dead-man alert may deliver more reliability than any wake-timer tuning.
- Layering for defence in depth: laptop (primary) + Cloud Scheduler (precise watchdog) + GitHub Actions cron (free tertiary catch-up) + healthchecks.io (alert). All idempotent via the same `runs` key, so adding triggers only reduces risk.

### Gaps
- Whether the broker's API terms and the applicable static-IP rule permit order placement from more than one registered IP (home + cloud proxy) was outside this scope and not researched here.
- Whether the owner's home broadband has a static IP (or CGNAT) is unknown; a dynamic home IP would undercut the "laptop on home static IP" variant.
