# Architecture

This document maps the blueprint in [`research-report.md`](research-report.md) onto the code.

```
  ┌────────────────────────── Mumbai VPS (static IP, whitelisted on Groww) ──────────────────────────┐
  │                                                                                                   │
  │  thunderbot worker (Python, systemd)                                                              │
  │                                                                                                   │
  │   GrowwMarketData ──► Strategy (ORB) ──► Signal ──► LLM review ──► RiskManager ──► TradingEngine  │
  │   (5-min candles)     deterministic        │        veto / shrink   hard limits     orders, stops │
  │                                            │        only (Claude)   final say            │        │
  │                                            ▼                                             ▼        │
  │                                   SQLite journal (source of truth) ◄────────── GrowwBroker /      │
  │                                            │                                   PaperBroker        │
  └────────────────────────────────────────────┼──────────────────────────────────────────────────────┘
                                               │ best-effort mirror (service-role key)
                                               ▼
                                      Supabase Postgres  ◄──── control: kill switch, pause, login confirm
                                               ▲
                                               │ server-side only (service-role key)
                                      Next.js dashboard on Vercel (Basic Auth)
```

## Platform: the dashboard as the control surface

The dashboard never talks to the worker directly. Everything goes through the database (Supabase in
production, `thunderbot serve` over SQLite locally), so the trading VPS needs no inbound ports:

| Flow | Mechanism |
|---|---|
| Live state | The engine writes a `heartbeat` control row every tick: positions with LTP and unrealized P&L, realized P&L, halt state, active strategy, reviewer. It also writes `equity` snapshots every minute. The dashboard polls `/api/state` every 2 s. |
| Controls | Dashboard writes `kill_switch`, `paused`, `login_confirmed_for` control rows; the engine reads them each tick. Kill is hold-to-confirm. |
| Settings | Dashboard writes `settings_overrides`. The engine applies them on its next tick via `Settings.with_overrides`: an **allowlist** of keys (`config.OVERRIDABLE`), each type-checked and bounded, always applied on top of the env-loaded base so overrides never accumulate. Live trading, MTF, static IP, credentials and login policy are not on the list. The result, including rejected keys, is published as `effective_settings`. |
| Research | Dashboard inserts a `jobs` row; `JobRunner` (`thunderbot jobs`, or inside `thunderbot serve`) claims it and runs a backtest or walk-forward sweep with the live strategy, risk and cost code, then writes progress and results back. Data sources: synthetic, CSV from `TB_BACKTEST_DATA_DIR` (never a client-supplied path), or Groww. |
| Reviewer value | Every signal, traded or not, is tracked virtually to its stop, target or end of day and written to `signal_outcomes` with an R-multiple and the reviewer's decision. The Performance tab compares average R of vetoed and approved signals. That is the evidence for keeping or dropping the LLM. |
| Replay | `thunderbot replay` drives `TradingEngine.tick` with a simulated clock and intra-bar prices (open, low/high, high/low, close) over historical candles. It journals exactly like paper trading (`mode = replay`), so the whole cockpit can be exercised and watched without a broker. |

The dashboard's API routes run server-side with the service-role key; the browser never sees it.
The whole app is behind HTTP Basic Auth that fails closed when unconfigured.

## Design principles

1. **The quant engine decides what to trade. The LLM can only say "less" or "no".**
   `Strategy.on_bar` produces every signal with a fixed entry, stop and target. The LLM
   (`thunderbot/llm/filter.py`) returns `approve | reject`, a `size_multiplier`, a confidence and a
   rationale. `RiskManager.evaluate` (`thunderbot/risk.py`) clamps the multiplier to [0, 1], rejects
   low-confidence approvals, and then applies its own limits. No LLM output can enlarge a position,
   change prices, or bypass a limit. A test (`test_llm_cannot_increase_size`) pins this.
2. **Fail closed.** When the LLM call errors, times out or is refused, the default
   (`TB_LLM_FAIL_MODE=reject`) skips the trade. Live trading needs three explicit opt-ins:
   `TB_LIVE_TRADING_ENABLED=true`, the `--i-understand-the-risks` flag, and a static-IP check that
   passes. MTF is off unless `TB_ALLOW_MTF_API=true`.
3. **Exits never wait on an LLM.** Stops, targets, the daily-loss halt, the kill switch and the
   3:05 PM flatten are all deterministic.
4. **Positions stay protected if the worker dies.** Right after an entry fills, a broker-side `SL`
   order is placed at the signal's stop. If that order cannot be placed, the position is closed
   immediately. The engine also keeps a software stop in case an SL-limit order is skipped on a gap.
5. **One code path for backtest and live.** The backtester reuses `Strategy`, `RiskManager` and
   `CostModel`, so a limit enforced live is also enforced in research.
6. **Everything is journaled.** Signals, the full LLM prompt and response metadata, every observed
   order state, closed trades and compliance events go to a local SQLite journal first, then to
   Supabase. A Supabase outage never blocks trading or loses the record.

## Module map

| Module | Responsibility |
|---|---|
| `config.py` | Env-driven settings. **Hard ceilings** config cannot raise: 9 orders/s (below SEBI's 10 OPS), 250 orders/min, 5x leverage, 2% risk per trade, 10% daily loss. |
| `clock.py` | IST session times, entry window (09:30-14:30), flatten at 15:05, holidays, 6:00 AM token expiry. |
| `strategy/__init__.py` | Strategy registry with UI parameter schemas (`catalog()`), `coerce_params` (known keys, typed, clamped) and `build_strategy`. |
| `strategy/vwap_reversion.py` | Fades a move stretched N ATRs from VWAP at an RSI extreme with a reversal bar; targets VWAP; skips trades whose target doesn't cover the stop. |
| `strategy/ema_pullback.py` | Joins an established fast/slow EMA trend on a pullback to the slow EMA that closes back beyond the fast EMA, on the right side of VWAP. |
| `strategy/orb.py` | Opening Range Breakout: 15-min range, close beyond range and VWAP, relative-volume surge vs. same time slot on prior days, stop at the far side of the range (tightened by ATR), 2R target, one signal per symbol per day. |
| `llm/filter.py` | Claude review via `client.beta.messages.parse` with a Pydantic schema; `fallbacks="default"` reroutes safety declines to Anthropic's recommended fallback model. |
| `risk.py` | Kill switch, halt, entry window, universe, one position per symbol, max positions and trades, product rules (no CNC shorts, MTF gated), signal geometry, max stop distance, fixed-fractional sizing, notional and cash caps, daily-loss halt. |
| `throttle.py` | Sliding-window order throttle that wraps every order-mutating Groww call. |
| `costs.py` | Brokerage, STT, exchange, SEBI, stamp duty, GST, DP charge, MTF interest. These are configurable estimates, so reconcile them with your contract notes. |
| `broker/groww.py` | `GrowwSession` (TOTP or approval flow, on-disk token cache, 6 AM expiry) and `GrowwBroker` (orders, status, positions, LTP in batches of 50, margin). |
| `broker/paper.py` | Pessimistic paper fills at live prices; stops fill past their limit on a gap. |
| `engine.py` | The polling loop: controls, heartbeat, prices, position management, halts, flatten, and bar-close signal scan. Orders are marketable LIMITs inside a price-protection band, never naked MARKET (MPP-friendly). |
| `backtest.py` | Next-bar-open fills, stop-before-target when a bar touches both, gap-through-stop exits at the open, 15:05 flatten, costs on both legs. |
| `compliance.py` | Static-IP check against `TB_EXPECTED_STATIC_IP` (primary[,secondary]) and unique 13-char order reference ids. |
| `store.py` | SQLite journal plus Supabase PostgREST mirror; control reads prefer Supabase (where the dashboard writes). `select`/`update` back the job queue. |
| `jobs.py` | Research job runner: backtests and walk-forward sweeps (max 60 combinations, in-sample/out-of-sample split, "robust" flag). |
| `replay.py` | Replays candles through the real engine and paper broker with a simulated clock. |
| `server.py` | `thunderbot serve`: PostgREST-compatible subset (select/order/limit/eq..in filters, upsert, patch) over the SQLite journal, bound to localhost, key-protected; validates settings overrides on write. |
| `llm/filter.py` `HeuristicFilter` | Free rule-based reviewer with the same veto/shrink contract, labelled `model="heuristic"`. It is the baseline Claude has to beat. |

## Compliance mapping (SEBI retail algo framework, in force April 1, 2026)

| Requirement | Where it is handled |
|---|---|
| Static IP for every API order | `compliance.check_static_ip` runs before `thunderbot live` starts; the worker runs on a VPS whose IP is whitelisted on the Groww API Keys page. |
| < 10 orders/second to avoid algo registration | `OrderThrottle`, default 5/s, hard-capped at 9/s. |
| Daily 2FA / forced logout | Token cached until 6:00 AM IST; with `TB_REQUIRE_LOGIN_CONFIRMATION=true`, live trading waits each day until a human confirms the login (dashboard button or `thunderbot confirm-login`). Each token issue is journaled. |
| Market orders become MPP | The engine uses marketable LIMIT orders within `TB_PRICE_PROTECTION_PCT`, retrying with a wider band on exits. |
| No AMOs for algo orders | The engine trades only during market hours. |
| Audit trail | Every order carries a unique `order_reference_id` and is journaled with its signal id and LLM decision. |
| Don't share or sell the strategy | Single-user design; the dashboard is behind Basic Auth. |

## MTF

The report concludes MTF via the Groww API is undocumented. Inspecting `growwapi` 1.5.0 shows the
SDK *does* define `PRODUCT_MTF = "MTF"`, but the public docs don't list it and the server's behavior
is unverified. So:

- `Product.MTF` exists in the domain model and `CostModel.mtf_interest` models the 0.041%/day charge.
- `GrowwBroker.place_order` and `RiskManager.evaluate` both refuse MTF unless `TB_ALLOW_MTF_API=true`.
- **Before enabling it:** raise a Groww support ticket, or place one tiny MTF order manually through
  the API on a live account and confirm it shows as MTF in the app. Until then, treat MTF ideas as
  recommendations to place by hand.

## LLM layer: why it is off by default

Published LLM-trading results are mostly short backtests, and LLMs have seen historical prices in
training, which inflates backtests through look-ahead bias. So:

- `thunderbot backtest` runs without the LLM unless you pass `--llm`, which logs a warning.
- Evaluate the LLM layer in **paper trading**: compare approved and vetoed signals (both are journaled
  with outcomes you can join on `signal_id`) over several weeks before trusting it with size.
- Model: `claude-opus-5-5` at `effort=medium`, one call per signal (a handful per day), with server-side
  refusal fallback enabled. Change it with `TB_LLM_MODEL` / `TB_LLM_EFFORT`.

## Known limitations and next steps

- Candle polling via the historical API: a WebSocket feed (`GrowwFeed`) would cut latency, but
  5-minute bars don't need it.
- One strategy ships (ORB). Add others by subclassing `Strategy` and registering them in
  `strategy/__init__.py`.
- The paper broker does not model partial fills, queue position, or the closing auction.
- Cost defaults are estimates. Reconcile them with your first contract notes.
- Response field names for Groww order and position endpoints follow the REST docs. Parsers accept
  common variants, but verify them against a live response in paper mode first.
