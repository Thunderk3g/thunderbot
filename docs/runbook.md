# Runbook

For the daily strategies with no server, start at [`no-server.md`](no-server.md) and come back here for
live trading. The stages below describe the long-running worker; build in order and don't skip any.

## Stage 0 - Learn the cockpit (local, no accounts)

Follow "Run it on one machine" in the README: `thunderbot serve`, `thunderbot replay --speed 0.3`,
and the dashboard. Try the kill switch, pause, a settings change and a Lab sweep. Watch the
engine apply each change. Everything runs on synthetic data, so nothing here measures an edge.

## Connect your Groww account

1. On groww.in/trade-api/api-keys create a **TOTP** key. You get two things: the **API key** (a long
   `eyJ...` token) and a **TOTP secret** (base32: capital letters A-Z and digits 2-7, the text
   under the QR code). Thunderbot needs both.
2. Give them to Thunderbot one of two ways. Never commit them or paste them into chats or tickets.
   - **The dashboard's Setup screen.** Paste both and press Save. They are encrypted before they are
     stored (see "Keys saved from the dashboard" below) and the worker reads them on its next pass.
   - **The worker's environment.** Put them in `worker/.env` locally (gitignored, loaded automatically)
     or `/etc/thunderbot.env` on the VPS (`chmod 600`):
     ```
     GROWW_API_KEY=eyJ...
     GROWW_TOTP_SECRET=ABCDEFGHIJKLMNOP
     ```
   A key saved in the dashboard wins over one in the environment.
3. Check them. Setup's **Check** button and `thunderbot login-check` run the same read-only steps: the
   key's type, the login, your profile, the live-data plan, and this machine's public IP against
   `TB_EXPECTED_STATIC_IP`. Nothing is ordered, and neither the token nor account details are shown.
   It tells you plainly if the secret isn't a TOTP secret or the key type doesn't match. The check
   runs where the worker runs: on a serverless worker it stops at "SDK not installed", because that
   worker cannot place orders and does not carry the Groww SDK. Run it on the static-IP machine.
4. For orders, also whitelist the VPS's static IP on the same page and set `TB_EXPECTED_STATIC_IP`.
   This, `TB_LIVE_TRADING_ENABLED` and `TB_ALLOW_MTF_API` are read from the worker's environment
   only. Nothing saved in the dashboard can switch on real orders.

If a key or secret is ever exposed, delete it on the API keys page and create a new one. TOTP
keys don't expire on their own.

## Keys saved from the dashboard

The Setup screen takes two things: an LLM key (Anthropic, xAI Grok, Groq, OpenAI, Gemini, OpenRouter,
or any OpenAI-compatible server) and the Groww credentials. Each is checked before it is saved: the
LLM key by listing the provider's models and making one tiny call with the model you pick, the Groww
key by the read-only check above.

- **Where they live.** In the `secrets` table, encrypted with AES-256-GCM. The table holds
  ciphertext, a masked hint such as `sk-…a1b2`, and the provider and model names. The dashboard never
  sends a saved key back to the browser.
- **The encryption key.** Set the same `TB_SECRET_KEY` on the dashboard and on every worker (any long
  random string). When it is unset, both sides use the database key they already share, which works
  until that key is rotated; after a rotation, save the keys again.
- **What the worker needs.** The `cryptography` package (`pip install -e "worker[all]"` includes it;
  the Vercel function gets it from `dashboard/pyproject.toml`). Without it, saved keys are ignored
  with one warning and environment keys keep working.
- **Precedence.** A saved key wins over the environment. `TB_LLM_ENABLED=false` in the worker's
  environment switches every LLM role off whichever key is present. A long-running worker
  (`thunderbot paper`, `live`, `invest`) reads saved keys when it starts; the serverless worker and
  the AI desk read them on every pass.
- **One install, one person.** The table has one row per key name. This is not a way to hold other
  people's broker credentials.

## Stage 1 - Backtest (local)

```bash
cd worker
python -m venv .venv && . .venv/bin/activate
pip install -e ".[all,dev]"
pytest

# Plumbing check on synthetic data (expect it to LOSE about its costs: random walks have no edge)
thunderbot demo-data --out data/demo --days 120
thunderbot backtest --data data/demo

# Real data (needs the paid Trade API plan for the Backtesting API)
export GROWW_API_KEY=... GROWW_TOTP_SECRET=...
thunderbot fetch-history --out data/groww --days 365 --interval 5
thunderbot backtest --data data/groww --trades-csv trades.csv
```

In the dashboard's **Strategy lab**, run walk-forward sweeps on real data (CSV or Groww). Only
promote a configuration marked **robust**: profitable in-sample *and* on the unseen
out-of-sample days, with at least 20 out-of-sample trades and a profit factor of 1.1 or more.

Exit criterion: positive net P&L **after costs** across at least a year, profit factor > 1.2,
max drawdown you can stomach, and no single month carrying the result. Most intraday variants fail
here; that is the expected outcome, not a bug. Start recording your own minute bars now, since
Groww's intraday history depth is disputed (3 months vs. "from 2020").

## Stage 2 - Paper trading (4-8 weeks minimum)

1. **VPS:** a small Linux VM in Mumbai (`ap-south-1` or equivalent) with a **static/elastic IP**.
2. **Whitelist** that IP (and an optional backup) on groww.in/trade-api/api-keys.
3. **Supabase:** create a project, then apply both migrations in `supabase/migrations/`
   (`supabase db push`, or paste them into the SQL editor in order).
4. **Worker install:**
   ```bash
   sudo useradd --system --home /opt/thunderbot thunderbot
   sudo git clone <this repo> /opt/thunderbot && cd /opt/thunderbot
   sudo python3 -m venv venv && sudo venv/bin/pip install -e "worker[all]"
   sudo cp worker/.env.example /etc/thunderbot.env && sudo chmod 600 /etc/thunderbot.env  # fill it in
   sudo cp worker/deploy/thunderbot.service worker/deploy/thunderbot-jobs.service /etc/systemd/system/
   sudo systemctl daemon-reload && sudo systemctl enable --now thunderbot thunderbot-jobs
   journalctl -u thunderbot -f
   ```
5. **Dashboard:** import `dashboard/` as a Vercel project (root directory `dashboard`) and set
   `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `DASHBOARD_USER` and `DASHBOARD_PASSWORD`. Never
   use a `NEXT_PUBLIC_` prefix for the service key.
6. Check the NSE holiday list (`worker/thunderbot/universes/nse_holidays.txt`, also copied to `worker/deploy/`) each December and add the new year.
7. Optional: connect an LLM on the dashboard's Setup screen (or set `TB_LLM_ENABLED=true` and
   `ANTHROPIC_API_KEY`, or the three `LLM_*` variables) to start collecting LLM decisions.

Exit criterion: paper results within reasonable distance of the backtest, no `exit_failed`,
`stop_failed` or repeated `error` events, the kill switch tested at least once, and (if the LLM
is on) evidence from the journal that vetoed signals did worse than approved ones.

## Stage 3 - Live, tiny size

Set `TB_CAPITAL` to the smallest amount that still buys 1 share of your most expensive symbol at
your risk settings. Then:

```bash
thunderbot check-ip                 # must print "matches whitelist"
# in /etc/thunderbot.env: TB_LIVE_TRADING_ENABLED=true
# in the unit file: ExecStart=/opt/thunderbot/venv/bin/thunderbot live --i-understand-the-risks
sudo systemctl daemon-reload && sudo systemctl restart thunderbot
```

Each trading morning: open the dashboard and click **Confirm today's broker login** (or run
`thunderbot confirm-login` on the VPS). Until then the worker opens no new positions (exits,
stops and the 15:05 flatten keep running). The Groww token is refreshed automatically after its
6:00 AM expiry, and each refresh is journaled as a `login` event.

Exit criterion: 4+ weeks of live fills matching paper behavior, with costs matching your
contract notes.

## Stage 4 - Scale

Raise `TB_CAPITAL` gradually. Keep `TB_MAX_LEVERAGE=1` until you have a long live record.

## Daily investing (the default)

Our research found no support for intraday trading by retail traders, and no support for an LLM or a
machine-learning model picking trades for a small account (`reports/`). What the evidence does support is
holding a few broad ETFs cheaply and rebalancing rarely. The worker therefore runs a slow, daily delivery
(CNC) strategy, chosen in **Lab -> Invest (daily)** or with `TB_INVEST_STRATEGY`:

| Strategy | Rule | Our backtest, 2011-2026, Rs 5 lakh, after costs and tax |
|---|---|---|
| `core_mix` (default) | NIFTYBEES, JUNIORBEES and GOLDBEES, a third each; rebalance at the end of March | about 12.5% a year, worst fall 23% |
| `etf_trend` | the same three ETFs in equal parts, each held only while above its own 200-day average at month-end; a part that is out waits in the liquid ETF | about 8.8% a year, worst fall 15% |
| `etf_rank` | the two ETFs with the best average 3-, 6- and 12-month return that also beat the liquid ETF | about 8.9% a year, worst fall 21% |
| `index_trend` | NIFTYBEES while the Nifty is more than 1% above its 200-day average at month-end, else the liquid ETF | about 7.1% a year, worst fall 22% |
| `momentum` | the top 15 Nifty 100 stocks by momentum, quarterly | not trustworthy: the stock list is today's index |

Holding NIFTYBEES alone made about 10.1% a year before tax (9.4% if sold and taxed at the end) with a
worst fall of 36%. Read those numbers with three cautions. They are backtests of sixteen years, not
promises. Gold rose about 19% a year from 2019 to 2026 and every result that holds gold is flattered by
it. And no timing rule beat simply holding the same ETFs: the trend rules trade about 3 to 4 points a year
of return for a shallower worst fall. Plan for less than the backtests: see the ranges in the report.

The worker checks once a day at `TB_INVEST_AT` (15:10 IST). `core_mix` trades once a year; the trend rules
trade at month-end, and only when a holding changes. Idle money is parked in `TB_LIQUID_SYMBOL`
(LIQUIDCASE, a growth-type liquid ETF). Test from the command line with
`thunderbot invest-backtest --strategy etf_trend --years 15`.

Two ways to run it:

- **No server (recommended to start):** [`docs/no-server.md`](no-server.md). Supabase's scheduler wakes a
  function on Vercel every five minutes in market hours. Paper trading, backtests and alerts; you place
  the few real orders by hand in the Groww app.
- **A machine with a static IP (needed for live API orders):** `thunderbot invest` as a service on a small
  VPS (the stages above), or `thunderbot tick` from a laptop scheduler (`worker/deploy/laptop/`).

### How orders are carried out

Three modes, chosen on the dashboard or with `thunderbot mode paper|guided|auto`:

| Mode | What happens at a decision | Needs |
|---|---|---|
| `paper` (default) | Fills are simulated at the live price with Groww's charges taken off. | Nothing. |
| `guided` | The whole-share limit orders are worked out and listed as a basket. You place them in the Groww app. Nothing is sent to the broker. | Nothing. This is the first real-money step. |
| `auto` | The orders go to Groww. | A worker started with `thunderbot invest --live`, which takes `TB_LIVE_TRADING_ENABLED=true`, a matching `TB_EXPECTED_STATIC_IP` and the `--i-understand-the-risks` flag on that machine. |

Asking for `auto` on any other worker (the Vercel function, a laptop without the switches) does not place
orders. It behaves as `guided` and the dashboard says why. Nothing written from the dashboard can change that.

A basket stays open until the holdings show it was placed. With a Groww key connected the worker reads
your holdings and closes the basket itself; if they do not match after you mark it placed, it lists what is
missing. With holdings typed in by hand, marking the basket placed updates the list. A rebalance basket
that is still open the next day is re-priced, and one basket is open at a time.

### What you really hold

In `guided` mode the plan works on your actual holdings, not a simulated account. They come from Groww
(read-only, `get_holdings_for_user`, a few times a day and whenever you ask) or from a list you type in:
symbol, quantity, average price and, if you know it, the purchase date. Anything the plan does not target
is shown as outside the plan and is never sold by the bot. Reading holdings needs the Groww SDK, so it
works on a laptop or server worker and not on the Vercel function; there, type the list in.

### Deposits and drift

`thunderbot deposit 25000` (or the dashboard) records new money. At the next daily check it is spent, in
whole shares, on whatever is furthest below its target, and nothing is sold, so no tax is realised. The
dashboard always shows where the next rupee would go.

Each holding has a corridor around its target: 5 percentage points, or a fifth of the target if that is
narrower (`TB_BAND_ABS_PCT`, `TB_BAND_REL_PCT`). A 33% holding may sit between 28% and 38%; a 10% one between
8% and 12%. The corridors are shown every pass. `core_mix` still rebalances each March by default. Its
`band` option rebalances only when a holding leaves its corridor, and its test-only options add a monthly
deposit and stop the plan selling at all, so you can compare the three in the Lab before choosing.

### The tax year

For the current financial year the dashboard shows how much long-term equity gain has been realised, how
much of the Rs 1.25 lakh exemption is left, and which holdings bought more than a year ago could be sold to
use it. It is a proposal. Nothing happens unless you confirm it.

A sale and repurchase of the same ticker on one day is netted by the broker as an intraday trade and books
no gain. So a harvest sells on one day and buys back on the next session (`TB_HARVEST_VIA=t_plus_1`, the
default, with a night out of the market for that amount), or swaps into a twin fund on the same index on the
same day (`TB_HARVEST_VIA=twin`; the twin map is `HARVEST_TWINS` in `worker/thunderbot/daily.py`). On a day a
harvest trades, the daily check is moved to the next session so the two cannot collide. In `guided` and
`auto` modes a harvest is always a basket for you to place.

This has not been checked against primary tax sources, including the same-day netting and how the
anti-avoidance rules treat a sale made only to step up cost. Confirm it with a chartered accountant first.
Holdings read from Groww carry no purchase dates, so they are left out of the proposal and any sale of them
is counted as short-term.

## Taxes the backtests assume (financial year 2026-27)

| Instrument | Up to 12 months | After 12 months |
|---|---|---|
| Equity ETFs (NIFTYBEES, JUNIORBEES) | 20% | 12.5% on gains above Rs 1.25 lakh a year |
| Gold and silver ETFs | your income-tax slab rate | 12.5%, no exemption |
| Liquid and other debt ETFs | your slab rate | your slab rate (never long-term) |

Plus 4% cess. Set your slab with `TB_SLAB_RATE_PCT` (default 30) or the slider in the Lab. This is the
model's reading of the rules, not tax advice; check your own position before filing.

## Starting and stopping

The worker service runs all the time but trades only after you press **Start** on the dashboard (or run
`thunderbot start`). Stopping (`thunderbot stop`) means no new trades. What it does to what is held
depends on what is held:

- **Investments stay.** The daily plan keeps every holding. Stop and the kill switch never sell them.
- **Intraday positions are closed**, because they cannot be carried overnight.

Selling the investments is a separate command, `thunderbot sell-all` (or its button, behind a confirmation
that shows the charges and tax). It also stops new trades. Start, stop and commands survive restarts, since
they live in the control table.

Paper trading uses live prices and simulates only the orders. `TB_FEED` picks the prices:
`yahoo` (default) is free Yahoo Finance data, with no account needed, but it is unofficial and can lag
the exchange (the daily strategies call Yahoo's chart endpoint directly; intraday paper trading uses the
open-source `yfinance` library for quotes); `groww` is Groww's official feed
(LTP every few seconds, 5-minute candles), which needs a working Groww login and the paid
Live Data plan. Live trading always uses Groww.

Backtests can use the same free data: **Lab → Prices → Yahoo (free)**, or
`thunderbot backtest --yahoo`. Yahoo keeps 5-minute bars for about 60 days only. If the login fails, the worker stays up and the dashboard shows why
("Groww not connected"). It retries at most every 5 minutes, because Groww allows only 150
token requests a day. Fix the credentials in `/etc/thunderbot.env` and restart the service.

## Daily operations

| Time (IST) | What happens |
|---|---|
| before 9:15 | Worker idle. Old token expired at 6:00 AM; a new one is issued on first use (journaled as `login`). |
| 9:15-9:30 | Opening range forms; no entries. |
| 9:30-14:30 | Entry window. Signals → LLM review → risk → entry + broker-side stop. |
| 14:30-15:05 | Positions managed (targets/stops), no new entries. |
| 15:05 | Flatten everything (Groww auto-squares MIS at 3:20 PM for ₹50 + GST per position). |

## Emergency procedures

| Situation | Action |
|---|---|
| Something looks wrong | Stop from the dashboard (or `thunderbot stop`, or `thunderbot kill`): closes intraday positions and blocks new trades. Investments are not sold. |
| Want to stop new trades but keep exits running | Dashboard **Pause new entries** (or `thunderbot pause`). |
| `partial_fill` event | A live delivery order filled in part. The rest was cancelled and only the filled shares are booked; the next check trades the difference. |
| `exit_failed` event | The engine could not close a position after 3 attempts. **Close it manually in the Groww app now.** |
| `stop_failed` event | Protective stop rejected; the engine tried to exit immediately. Check the position in the app. |
| `unmanaged_position` event | A position exists that the engine didn't open (manual trade or a restart mid-trade). The engine never touches it, so handle it yourself. |
| Worker crashed mid-trade | Broker-side SL orders still protect open positions. On a restart the same day the engine takes its positions back, with the day's result, trade count and any halt, from the `engine_state` control row, and carries on managing them. Anything it cannot account for is reported as unmanaged: close that manually or let Groww's 3:20 PM MIS square-off handle it. |
| IP changed | Live mode refuses to start. Fix the VPS IP or update the whitelist (some brokers allow changes only weekly). |
| Repeated errors | After 5 consecutive failed ticks, the engine engages the kill switch itself and tries to flatten. |

To trade again after a stop or a kill: **Start** on the dashboard or `thunderbot start` (this also clears the kill switch and pause).
