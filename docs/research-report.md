# LLM-Powered Trading Platform on Groww (Intraday + MTF): Research Report and Build Blueprint (October 2026)

> Source document for this repository. The text is as provided, minus the inline source-link
> badges, which were dropped for readability. The original paste was cut off partway through
> Section 3 (the research lineage), so it ends there.
>
> **Corrections found while building (October 16, 2026):**
> 1. **MTF constant.** The report says no `PRODUCT_MTF` constant exists in the Python SDK. In fact
>    `growwapi` 1.5.0 defines `GrowwAPI.PRODUCT_MTF = "MTF"` (`growwapi/groww/client.py`), and the
>    order-update protobufs include an `MTF` product. The public Annexures still list only CNC/MIS/NRML,
>    so whether the **server** accepts MTF orders is unverified. The code keeps MTF behind
>    `TB_ALLOW_MTF_API=false` until it is confirmed on a live account. See `docs/architecture.md`.
> 2. **More SDK constants than documented.** The SDK also defines validities `EOS/IOC/GTC/GTD` and
>    products `ARB/BO/CO`. Only what the docs promise (DAY validity; CNC/MIS) is used here.

**Bottom line: you can build this on Groww's official Trade API for intraday (MIS) and delivery (CNC) today, but you should not count on automating MTF through it. Groww's marketing page says the API handles MTF, yet its official SDK and REST docs list only CNC, MIS and NRML product types, and none of its changelog entries adds MTF.** The right design is a deterministic quant engine that generates signals, with the LLM acting as a filter, ranker and explainer that cannot override hard risk limits. That engine runs on an always-on worker with a static IP, which SEBI has required for every retail API order since April 1, 2026. Vercel only hosts the dashboard. Treat the LLM layer as unproven alpha: the best published evidence is short backtests and small live tournaments, and look-ahead bias inflates most LLM backtests.

## TL;DR
- **Groww API works for intraday and delivery, but MTF is unconfirmed.** It costs ₹499 + GST a month (₹4,999 a year, or a ₹0 trial with no live or historical data). It uses a Python SDK (`growwapi`) and TOTP login, and access tokens expire daily at 6:00 AM. It supports LIMIT, MARKET, SL and SL_M orders plus GTT/OCO smart orders, and allows 10 orders a second. Treat MTF via API as unsupported until you verify it on a live account. If programmatic MTF is a must-have, check Zerodha Kite Connect or Dhan, which list MTF as an order product (unverified here).
- **For compliance, a personal algo needs a whitelisted static IP, daily 2FA login, and fewer than 10 orders/second.** Market orders get price protection (MPP), and API sessions log out every day. Staying under 10 orders a second avoids exchange algo registration, and nothing else is needed for personal use under the February 4, 2025 SEBI circular, which became fully mandatory on April 1, 2026.
- **The architecture is three parts, built in stages.** A Next.js dashboard on Vercel, Supabase Postgres for state and LLM reasoning traces, and a Python worker on a Mumbai VPS with a static IP that holds the broker credentials and runs the strategy loop. Build in four stages: backtest, then paper trade for at least 4–8 weeks, then live with tiny size, then scale. Expect most intraday variants to fail after costs: SEBI's July 2024 study of clients at the top 10 brokers found 71% of individual intraday cash traders lost money in FY23.

## Key Findings

### 1. Groww Trade API: what it actually offers (verified against official docs)

**Availability and pricing**
- Groww's September 30, 2026 guide lists three plans:
  - **Free Trial** (₹0): orders, smart orders, positions, holdings and margin, but no Live Data or Backtesting APIs.
  - **Monthly**: ₹499 + tax.
  - **Yearly**: ₹4,999 + tax, about ₹417 a month.
- Subscriptions are bought at groww.in/trade-api, auto-renew, and are deducted from your Groww balance.
- Groww also has **"Groww Cloud" Strategies**, a hosted script editor with "Run now" and "Save & deploy" buttons. It is one way to satisfy the "hosted within broker infrastructure" model, though you give up control of your stack.

**Authentication**
There are two official flows:
1. **API key + secret**: needs daily approval on the Groww Cloud API Keys page.
2. **TOTP flow**: the TOTP token and secret don't expire. You generate a 6-digit code with `pyotp` and exchange it for an access token with `GrowwAPI.get_access_token(api_key=..., totp=...)`.

Other rules:
- Access tokens **expire daily at 6:00 AM**, per Groww's cURL docs. Tradetron says 8 AM, but I'd trust Groww's own docs.
- The token endpoint is limited to **150 requests per 24 hours**.
- The TOTP flow makes an unattended daily login technically possible. Under SEBI's daily-2FA rule, keep a human-confirmed or at least logged login step (see Compliance).

**SDK**
- Install with `pip install growwapi`. Python 3.9+.
- The latest release is 1.5.0 (December 2025).
- Changelog milestones:
  - Historical/backtesting data: October 3, 2025
  - Smart Orders (GTT/OCO): October 29, 2025
  - Option chain: November 24, 2025
  - `realised_pnl` in positions: November 2025
  - User profile: December 2025

**Supported operations (from the official Annexures)**
| Area | What's supported |
|---|---|
| Products | **CNC** (delivery), **MIS** (intraday), **NRML** (F&O carry). **No MTF value documented.** |
| Order types | LIMIT, MARKET, SL, SL_M |
| Smart orders | GTT and OCO; **CASH-segment OCO supports only MIS** |
| Validity | DAY only |
| Segments / exchanges | CASH, FNO; NSE, BSE. The intro mentions MCX, but the changelog notes MCX is not supported in parts of the API. |
| Portfolio | Holdings, positions (incl. realised P&L), margin, order list/status, trade list |
| Live data | LTP / OHLC (up to 50 instruments per call), quote with depth, option chain + Greeks, WebSocket feed for market data and order/position updates |
| Historical | Candles of 1, 2, 3, 5, 10, 15 and 30 min; 1 h, 4 h; 1 day, 1 week, 1 month. Equities, indices and F&O "available from 2020". |

**Historical request windows**
- 30 days per request for 1–5 min candles.
- 90 days for 10–30 min.
- 180 days for 1 hour and above.
- Pagination is needed for multi-year pulls.
- **Conflict:** a third-party review (oidata.in) says intraday candles go back only three months. The official Backtesting page says "from 2020". Verify on your account before you design the data pipeline, and record your own minute bars from day one either way.

**Rate limits (official)**
| Type | Per second | Per minute |
|---|---|---|
| Orders (create/modify/cancel) | 10 | 250 |
| Live data | 10 | 300 |
| Non-trading (status, positions, holdings, margin) | 20 | 500 |
| Authentication | 5 | 30 |

- Limits apply per type, shared by all endpoints in that type.
- The feed allows up to 1,000 subscriptions per the SDK docs. Groww's blog says 3,000, so plan for 1,000.
- Other limits: 25 modifications per order, 5 sessions per user.

**MTF: the critical gap**
- groww.in/trade-api says you can "place orders in Stocks, F&O, and MTF".
- On the same page, the pricing FAQ mentions only "stocks and F&O".
- No `PRODUCT_MTF` constant appears in the Python SDK Annexures or the cURL Annexures, and no changelog entry through v1.5.0 adds one.
- Community wrappers (groww-mcp-server, growwapi-go) also list only CNC/MIS/NRML.
- **Conclusion:** treat MTF via the Groww API as unsupported or undocumented.

What you can do about it:
- (a) Have the system *recommend* MTF swing trades and place them manually in the app. Groww now allows MTF AMOs and MTF-to-delivery conversion.
- (b) Raise a Groww support ticket asking whether `product="MTF"` is accepted.
- (c) Use a second broker for the MTF sleeve.

**Static IP on Groww**
- Add a primary and secondary static IP on the API Keys page (groww.in/trade-api/api-keys).
- Orders from non-whitelisted IPs are rejected.

**Community code worth reading**
- OpenAlgo (marketcalls/openalgo): AGPL, Flask + React. It has 36 broker plugins including Groww and an "Analyzer Mode" sandbox with ₹1 crore of virtual capital at real prices.
- Groww MCP servers that expose the API to LLM agents:
  - developerJai/groww-mcp, which handles automated TOTP auth, GTT/OCO and the option chain
  - arkapravasinha/groww-mcp-server
  - venkatakaushikvemani/groww-mcp
- rctrj/growwapi-go, a Go wrapper.
- Third-party platforms supporting Groww: AlgoTest, Tradetron, Stocksdeveloper.

**Alternatives if Groww is limiting**
| Broker | API cost (2026) | Notes |
|---|---|---|
| Zerodha Kite Connect | Personal: free (orders, no data). Connect: ₹500/month with live and historical data. Per Zerodha support, from October 2026 paid Connect users who generate ₹2,000 or more in brokerage in a calendar month get 500 Developer Credits (₹500) to cover the next month's renewal. | Most mature SDK and docs. Lists MTF as a product (verify). |
| Dhan (DhanHQ) | Trading API free; Data API ₹499 + taxes/month | Lists MTF as a product type (verify) |
| Upstox | No subscription; per-order fee on API orders | From April 1, 2026: one active API app per user, MPP default |
| Fyers / Angel One SmartAPI | Free | Fyers: daily 2FA, 10 OPS, MPP conversion from April 1, 2026 |

### 2. Regulation: what your personal algo must do (late 2026)

**Framework chain**
- SEBI circular SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/0000013 (February 4, 2025).
- NSE implementation standards (NSE/INVG/67858, May 5, 2025).
- SEBI glide-path extension (September 30, 2025).
- Broker milestones in October–November 2025. Non-compliant brokers were barred from onboarding new API clients from January 5, 2026.
- **Full enforcement from April 1, 2026.**

**What applies to you as a self-coding retail trader**
- **Fewer than 10 orders per second per exchange: no algo registration needed.** Orders carry a generic algo tag. Above 10 OPS the strategy must be registered through the broker with a unique algo ID. Your design (a handful of orders a day) is far below this, but add a client-side throttle anyway.
- **Static IP is mandatory for every API order,** whatever the frequency. You can whitelist a primary and a backup. You may share a static IP only with immediate family. Some brokers allow changing it only once per calendar week.
- **Daily 2FA / OAuth login.** All API sessions are force-logged-out before the next trading day. Long-lived refresh tokens are gone.
- **Market orders become Market Price Protection (MPP) orders.** They fill only within a band and otherwise rest as limits. Brokers including Fyers say AMOs are not permitted for algo orders.
- **Third-party platforms must be empanelled** and hosted in the broker's infrastructure. A self-built, self-hosted script for your own account is the "tech-savvy retail investor" case and doesn't need empanelment. Don't sell or share your strategy.
- **Audit trail:** orders are traceable client → algo ID → static IP → API key. Keep your own logs too.

**MTF rules**
- Only **Group I securities and equity ETFs** are eligible.
- The client puts up at least **25%**, so the broker funds at most 75%. Groww advertises "up to 4x".
- Funded shares are **pledged** to the broker in the depository system.
- When cash collateral funds the purchase and the funded stock counts as maintenance margin, margin is **VaR + 5×ELM**.
- **Groww terms (per Groww's MTF page, groww.in/stocks/mtf):**
  - Interest of **0.041% a day (14.95% p.a.)**, charged only on the funded amount
  - **0.1% brokerage per order**
  - **₹20 per pledge/unpledge**
  - Shortfalls are shown in the Positions tab; unmet margin calls lead to liquidation.
- SEBI has floated a consultation on an MTF overhaul (₹5 crore broker net worth, ledger fungibility, keeping VaR + 5×ELM). These are **proposals, not final rules**.

**Intraday rules**
- Peak-margin rules mean at least about 20% upfront margin (about 5x maximum leverage). Some older third-party pages still quote "8x" for Groww; ignore them.
- **Auto square-off conflict:** Groww's help pages say MIS positions are auto-squared at **3:20 PM** with a **₹50 + GST per position** charge. Several third-party sites say 3:10 PM or 3:15 PM. Program your flatten-all at **3:05 PM** so the discrepancy doesn't matter.
- NSE introduced a Closing Auction Session in the cash segment during 2026. MPP doesn't apply in CAS, so avoid exiting into the close.

### 3. LLMs for trading: evidence, not hype

**What the research shows**
- **TradingAgents** (Xiao et al., arXiv 2412.20138) uses fundamental, sentiment, news and technical analysts, bull/bear researchers, a trader and a risk team, and debates each decision.
  - It reported a **26.62% cumulative return on AAPL** and beat rule-based baselines on Sharpe for AAPL, GOOGL and AMZN.
  - But the test covered **only three months**, because each decision took **11 LLM calls and 20+ tool calls**, and there was **no live trading**.
  - Useful as an architecture template, weak as proof of alpha.
- **The research lineage:**
  - FinMem (layered memory)
  - FinCon (multi-agent with verbal reinforcement)

*(The provided report ends here.)*
