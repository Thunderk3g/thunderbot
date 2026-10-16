# Runbook

Build in four stages and don't skip any. Each stage has an exit criterion.

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

Exit criterion: positive net P&L **after costs** across at least a year, profit factor > 1.2,
max drawdown you can stomach, and no single month carrying the result. Most intraday variants fail
here; that is the expected outcome, not a bug. Start recording your own minute bars now, since
Groww's intraday history depth is disputed (3 months vs. "from 2020").

## Stage 2 - Paper trading (4-8 weeks minimum)

1. **VPS:** a small Linux VM in Mumbai (`ap-south-1` or equivalent) with a **static/elastic IP**.
2. **Whitelist** that IP (and an optional backup) on groww.in/trade-api/api-keys.
3. **Supabase:** create a project, then apply `supabase/migrations/20261016000000_init.sql`
   (`supabase db push` or paste it into the SQL editor).
4. **Worker install:**
   ```bash
   sudo useradd --system --home /opt/thunderbot thunderbot
   sudo git clone <this repo> /opt/thunderbot && cd /opt/thunderbot
   sudo python3 -m venv venv && sudo venv/bin/pip install -e "worker[all]"
   sudo cp worker/.env.example /etc/thunderbot.env && sudo chmod 600 /etc/thunderbot.env  # fill it in
   sudo cp worker/deploy/thunderbot.service /etc/systemd/system/
   sudo systemctl daemon-reload && sudo systemctl enable --now thunderbot
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
| Something looks wrong | Dashboard **Kill switch** (or `thunderbot kill`): flattens all managed positions, blocks entries. |
| Want to stop new trades but keep exits running | Dashboard **Pause new entries** (or `thunderbot pause`). |
| `exit_failed` event | The engine could not close a position after 3 attempts. **Close it manually in the Groww app now.** |
| `stop_failed` event | Protective stop rejected; the engine tried to exit immediately. Check the position in the app. |
| `unmanaged_position` event | A position exists that the engine didn't open (manual trade or a restart mid-trade). The engine never touches it, so handle it yourself. |
| Worker crashed mid-trade | Broker-side SL orders still protect open positions. On restart the engine reports unmanaged positions. Close them manually or let Groww's 3:20 PM MIS square-off handle it. |
| IP changed | Live mode refuses to start. Fix the VPS IP or update the whitelist (some brokers allow changes only weekly). |
| Repeated errors | After 5 consecutive failed ticks, the engine engages the kill switch itself and tries to flatten. |

To resume after a kill: `thunderbot resume` or **Release kill switch** on the dashboard.
