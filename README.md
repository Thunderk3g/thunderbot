# Thunderbot

A personal trading system for NSE cash equities on **Groww's Trade API**, built from the blueprint in
[`docs/research-report.md`](docs/research-report.md):

- A **deterministic quant engine** generates every signal (Opening Range Breakout on 5-minute bars).
- A **Claude review layer** can veto a signal or shrink its size. It can never create a trade, enlarge
  one, or move its prices.
- **Hard risk limits** run last and always win: daily loss halt, position and trade caps,
  fixed-fractional sizing, leverage ceiling, kill switch, 3:05 PM flatten.
- **SEBI retail-algo compliance** (April 2026 framework): static-IP check, order throttle hard-capped
  below 10 orders/second, daily login confirmation, MPP-friendly marketable-limit orders, and a full
  audit journal.

> **Read this first.** SEBI found that 71% of individual intraday cash traders lost money in FY23.
> This code is a framework, not an edge. Backtest, then paper trade for at least 4-8 weeks, before
> risking real money, and start tiny. The LLM layer is unproven: evaluate it in paper trading, not
> in backtests, which LLM look-ahead bias inflates.

## Layout

```
worker/      Python trading worker (runs on a Mumbai VPS with a static IP)
  thunderbot/  strategy, LLM filter, risk, brokers (Groww + paper), engine, backtester, CLI
  tests/       68 tests covering risk rules, fills, engine lifecycle, Groww mapping, LLM clamping
  deploy/      systemd unit, NSE holiday file
dashboard/   Next.js monitor + kill switch for Vercel (Basic Auth, server-side Supabase access)
supabase/    Postgres schema (RLS on, service-role access only)
docs/        research report, architecture, runbook
```

## Quick start

```bash
cd worker
python -m venv .venv && . .venv/bin/activate
pip install -e ".[all,dev]"
pytest

thunderbot demo-data --out data/demo --days 120   # synthetic data, plumbing only
thunderbot backtest --data data/demo
```

With a paid Groww Trade API plan:

```bash
export GROWW_API_KEY=... GROWW_TOTP_SECRET=...
thunderbot fetch-history --out data/groww --days 365
thunderbot backtest --data data/groww --trades-csv trades.csv
thunderbot paper                     # paper trade against live Groww prices
```

Live trading needs three explicit opt-ins: `TB_LIVE_TRADING_ENABLED=true`, a whitelisted
`TB_EXPECTED_STATIC_IP` that matches the host's public IP, and
`thunderbot live --i-understand-the-risks`. See [`docs/runbook.md`](docs/runbook.md).

## Commands

| Command | Purpose |
|---|---|
| `thunderbot backtest --data DIR` | Run the strategy over CSV candles (costs, slippage, conservative fills) |
| `thunderbot fetch-history` | Download candles from Groww, paginated per Groww's window limits |
| `thunderbot demo-data` | Write synthetic CSVs for plumbing tests |
| `thunderbot paper` / `live` | Run the trading engine |
| `thunderbot kill` / `pause` / `resume` | Control plane (also on the dashboard) |
| `thunderbot confirm-login` | Confirm today's broker login (daily 2FA policy) |
| `thunderbot check-ip` | Verify the public IP is the whitelisted static IP |

All settings are environment variables; see [`worker/.env.example`](worker/.env.example).

## Key decisions

- **MTF is off.** `growwapi` 1.5.0 defines `PRODUCT_MTF`, but Groww's docs don't list it and server
  support is unverified. Keep `TB_ALLOW_MTF_API=false` until confirmed on a live account.
- **No naked MARKET orders.** Entries and exits are marketable LIMITs inside a price-protection band.
  Exits retry with a wider band, and a broker-side SL order protects every open position.
- **The LLM is off by default** (`TB_LLM_ENABLED=false`). When on, it uses `claude-opus-5-5` once per
  signal with structured output, fails closed on errors, and every prompt and decision is journaled.
- **SQLite is the source of truth on the VPS**; Supabase is a best-effort mirror for the dashboard.

More detail in [`docs/architecture.md`](docs/architecture.md).
