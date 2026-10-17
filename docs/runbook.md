# Runbook

Build in four stages and don't skip any. Each stage has an exit criterion.

## Stage 0 - Learn the cockpit (local, no accounts)

Follow "Run it on one machine" in the README: `thunderbot serve`, `thunderbot replay --speed 0.3`,
and the dashboard. Try the kill switch, pause, a settings change and a Lab sweep. Watch the
engine apply each change. Everything runs on synthetic data, so nothing here measures an edge.

## Connect your Groww account

1. On groww.in/trade-api/api-keys create a **TOTP** key. You get two things: the **API key** (a long
   `eyJ...` token) and a **TOTP secret** (base32: capital letters A-Z and digits 2-7, the text
   under the QR code). Thunderbot needs both.
2. Put them in `worker/.env` locally (gitignored, loaded automatically) or `/etc/thunderbot.env`
   on the VPS (`chmod 600`). Never commit them or paste them into chats or tickets.
   ```
   GROWW_API_KEY=eyJ...
   GROWW_TOTP_SECRET=ABCDEFGHIJKLMNOP
   ```
3. Run `thunderbot login-check`. It logs in, fetches your profile, and probes the live-data plan.
   It never places orders and prints neither the token nor account details. It tells you plainly
   if the secret isn't a TOTP secret or the key type doesn't match.
4. For orders, also whitelist the VPS's static IP on the same page and set `TB_EXPECTED_STATIC_IP`.

If a key or secret is ever exposed, delete it on the API keys page and create a new one. TOTP
keys don't expire on their own.

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
6. Fill `worker/deploy/nse_holidays.txt` with this year's NSE holidays.
7. Optional: set `TB_LLM_ENABLED=true` and `ANTHROPIC_API_KEY` to start collecting LLM decisions.

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

## Starting and stopping

The worker service runs all the time but trades only after you press **Start paper trading** on
the dashboard (or run `thunderbot start`). **Hold to stop** (or `thunderbot stop`) closes every
open position and takes no new trades; the worker keeps running and waits for the next Start.
Start and stop survive restarts, since they live in the control table.

Paper trading uses live prices and simulates only the orders. `TB_FEED` picks the prices:
`yahoo` (default) is free Yahoo Finance data through the open-source `yfinance` library, with no
account needed, but it is unofficial and can lag the exchange; `groww` is Groww's official feed
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
| Something looks wrong | Dashboard **Hold to stop** (or `thunderbot stop`, or `thunderbot kill`): flattens all managed positions, blocks entries. |
| Want to stop new trades but keep exits running | Dashboard **Pause new entries** (or `thunderbot pause`). |
| `exit_failed` event | The engine could not close a position after 3 attempts. **Close it manually in the Groww app now.** |
| `stop_failed` event | Protective stop rejected; the engine tried to exit immediately. Check the position in the app. |
| `unmanaged_position` event | A position exists that the engine didn't open (manual trade or a restart mid-trade). The engine never touches it, so handle it yourself. |
| Worker crashed mid-trade | Broker-side SL orders still protect open positions. On restart the engine reports unmanaged positions. Close them manually or let Groww's 3:20 PM MIS square-off handle it. |
| IP changed | Live mode refuses to start. Fix the VPS IP or update the whitelist (some brokers allow changes only weekly). |
| Repeated errors | After 5 consecutive failed ticks, the engine engages the kill switch itself and tries to flatten. |

To trade again after a stop or a kill: **Start** on the dashboard or `thunderbot start` (this also clears the kill switch and pause).
