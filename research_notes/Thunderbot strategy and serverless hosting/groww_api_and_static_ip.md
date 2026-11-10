# Groww Trade API, SEBI's static-IP rule for retail API orders, and ways to get a fixed outgoing IP without an always-on server (as of 10 Nov 2026)

> **How these notes were made, and their limits (read first).**
> - This session's network policy blocked direct page fetches for every site except package registries (PyPI, npm). groww.in, sebi.gov.in, nsearchives.nseindia.com, zerodha.com, vercel.com, quotaguard.com, support.fyers.in and others could not be opened. The shared web-search budget also ran out part-way through, so about half the planned searches (VPS prices, AWS/GCP NAT prices, Fixie, Railway/Render, Cloudflare, Indian ISPs, Groww Cloud details, the NSE FAQ text) never ran.
> - Therefore: (a) facts marked **[SDK]** were read directly from the `growwapi` 1.5.0 wheel downloaded from PyPI today (primary, strong); (b) facts marked **[search summary]** come from search-result summaries of the linked page, not from reading the page in full (medium; wording may be paraphrased); (c) anything I know only from memory is kept out of "Cited Findings" and listed under "Gaps" as **unverified background** with the official page to check.
> - Dates: the newest evidence found for most rules is from Sep to Oct 2026 (Groww blog revision, Chittorgarh review, PyPI releases). I found no source saying the static-IP rule was relaxed after 1 Apr 2026, but I also could not open SEBI/NSE sites to check for a late-2026 circular.

## 0. What Thunderbot currently does and assumes (repo inspection)

### Takeaway
The worker already uses Groww's TOTP login, caches the daily token on disk, tags every order with a unique reference id and refuses live trading unless the machine's public IP equals a configured whitelisted IP. All of this assumes a Mumbai VPS with a static IP; nothing in the code routes broker calls through a proxy yet.

### Cited Findings
- Login: `GrowwSession.token()` builds a 6-digit code with `pyotp.TOTP(secret).now()` and calls `GrowwAPI.get_access_token(api_key=..., totp=code)`; if only `GROWW_API_SECRET` is set it uses the approval flow `get_access_token(api_key=..., secret=...)`. The token is cached in a file (mode 0600) and reused until stale. — `/home/user/thunderbot/worker/thunderbot/broker/groww.py`
- The code comments assume "Tokens expire at 6:00 AM IST and the token endpoint allows only 150 requests per day"; a failed login is retried at most every 300 s for that reason. — `/home/user/thunderbot/worker/thunderbot/broker/groww.py`
- Static IP guard: `check_static_ip` compares the public IP (from api.ipify.org / ifconfig.me / checkip.amazonaws.com) with `TB_EXPECTED_STATIC_IP` ("primary[,secondary]") and blocks `thunderbot live` on a mismatch. — `/home/user/thunderbot/worker/thunderbot/compliance.py`
- Order reference ids are 13 alphanumeric characters (`TB` + yymmdd + counter + salt); the comment says "Groww accepts 8-20 alphanumeric characters". — `/home/user/thunderbot/worker/thunderbot/compliance.py`
- The runbook tells the owner to create a TOTP key on groww.in/trade-api/api-keys, whitelist the VPS's static IP "on the same page", and notes "some brokers allow changes only weekly". It also says Groww's live-data feed "needs ... the paid Live Data plan" and "Groww's intraday history depth is disputed (3 months vs. 'from 2020')". — `/home/user/thunderbot/docs/runbook.md`
- Dependencies pin `growwapi>=1.5.0`, `pyotp>=2.9`. — `/home/user/thunderbot/worker/pyproject.toml`
- The architecture puts the worker on a "Mumbai VPS (static IP, whitelisted on Groww)" with the Next.js dashboard on Vercel and state in Supabase; the dashboard never calls the broker. — `/home/user/thunderbot/docs/architecture.md`, `/home/user/thunderbot/README.md`

### Inferences
- If the worker moves to serverless and orders go through a proxy, `check_static_ip` must test the IP **as seen through the proxy** (make the ipify call through the same proxy), otherwise it will either block a valid setup or pass an invalid one.
- The on-disk token cache does not survive a serverless run; a serverless design would mint a token per run (see section 1) or store it in Supabase.

### Gaps
- The "150 token requests per day" and "8-20 alphanumeric characters" limits appear only in repo comments. I could not open Groww's docs to confirm them.

## 1. Groww Trade API today: price, docs, SDK, login flows, limits, features

### Takeaway
The Trade API is still sold at Rs 499 + taxes per month (labelled an early-bird price against a struck-through Rs 2,000), normal per-order brokerage still applies, and the Python SDK `growwapi` has been at 1.5.0 since 6 Dec 2025. The TOTP flow is fully automatable and stateless (one HTTPS POST per run), so a serverless function can mint the day's token itself; the "checksum" flow exists but is just the API-key-plus-secret flow and needs a human approval every day.

### Cited Findings
**Price and plans**
- Groww's own page lists the API at Rs 499 + taxes per month, covering live data (LTP, quote, OHLC), orders, margin and historical data, with a struck-through Rs 2,000 and an "early bird" label; it mentions "historical data (up to 3 months)". [search summary] — [groww.in/trade-api](https://groww.in/trade-api)
- A broker-review site states the fee is Rs 499 + taxes a month "as of September 2026". [search summary] — [Chittorgarh, Groww API review](https://www.chittorgarh.com/broker/groww/api-for-algo-trading-review/173/)
- A Groww page lists a Monthly plan at Rs 499/month + taxes and a Yearly plan at Rs 417/month + taxes billed Rs 4,999 per year; Groww's blog also describes a **Free Trial plan at Rs 0** that gives access to "Groww Cloud" but excludes live quotes/LTP/OHLC, option chain and Greeks, and historical candles. The search summary says the free/paid difference is data access, not order placement. [search summary; exact plan table not read] — [Groww blog: API trading on Groww](https://groww.in/blog/api-trading-on-groww)
- Per-order brokerage is not waived for API orders: Groww's pricing lists Rs 20 or 0.1% per executed order (whichever is lower) for equity delivery and intraday, Rs 20 per F&O order. [search summary] — [Groww 915 pricing](https://915.groww.in/pricing)
- A third-party wrapper's README (v1.0.4, 4 Sep 2026) says the Rs 499/month subscription "is required for quotes, LTP, OHLC, historical candles, and streaming"; without it those calls raise "Access forbidden". — [brokerkit-groww on PyPI](https://pypi.org/project/brokerkit-groww/)

**SDK and docs**
- `growwapi` latest version is **1.5.0, uploaded 6 Dec 2025**; earlier releases 1.3.0 (26 Nov 2025), 1.2.0 (10 Nov 2025), 1.1.0 (8 Oct 2025), 1.0.0 (3 Oct 2025). No newer release exists as of 10 Nov 2026 (checked via the PyPI JSON API today). Requires Python >=3.9,<4.0. — [PyPI growwapi](https://pypi.org/project/growwapi/)
- Official docs live at groww.in/trade-api/docs (Python SDK and cURL variants, plus a Smart Orders page). — [Groww docs, Python SDK](https://groww.in/trade-api/docs/python-sdk), [Groww docs, cURL](https://groww.in/trade-api/docs/curl), [Groww docs, Smart Orders](https://groww.in/trade-api/docs/python-sdk/smart-orders)

**Login flows**
- Groww's docs describe three ways to get a token: (1) an **Access Token** generated by hand on the API keys page, which expires daily at 6:00 AM; (2) **API key + secret**, which "requires daily approval" on the API keys page; (3) **API key + TOTP**, where the code comes from an authenticator secret. The docs label the TOTP option "No Expiry" (this refers to the TOTP credential; access tokens still expire daily at 06:00 IST). [search summary] — [Groww docs, cURL introduction](https://groww.in/trade-api/docs/curl), [Groww docs, Python SDK](https://groww.in/trade-api/docs/python-sdk)
- [SDK] The token call is one unauthenticated-state HTTPS request: `POST https://api.groww.in/v1/token/api/access` with the API key as the Bearer header and a JSON body of either `{"key_type": "totp", "totp": "<6 digits>"}` or `{"key_type": "approval", "checksum": sha256(secret + timestamp), "timestamp": <unix seconds>}`; it returns `token`. So the **checksum flow is the approval (key + secret) flow**, not a third unattended option. — [PyPI growwapi 1.5.0, `groww/client.py` `get_access_token` / `_build_request_data` / `_generate_checksum`](https://pypi.org/project/growwapi/)
- A third-party wrapper states "Access tokens expire daily at 6 AM IST" and that a TOTP code is valid for 30 seconds and used once to obtain the token. — [brokerkit-groww on PyPI](https://pypi.org/project/brokerkit-groww/)

**Rate limits**
- Groww's docs list **Orders (create, modify, cancel): 10 per second and 250 per minute; Non-trading: 20 per second and 500 per minute**, and say that if the limit for one API in a type is exhausted, all APIs of that type are limited until the window resets. [search summary] — [Groww docs, Python SDK](https://groww.in/trade-api/docs/python-sdk)
- A third-party MCP server README lists live data (quote, LTP, OHLC) at 10 per second / 300 per minute, but also lists orders at 15 per second, which conflicts with the official 10/s figure above. Treat the live-data row as unverified. [search summary] — [developerJai/groww-mcp](https://github.com/developerJai/groww-mcp)
- `get_ltp` and `get_ohlc` accept up to 50 symbols per call, one segment at a time. — [brokerkit-groww on PyPI](https://pypi.org/project/brokerkit-groww/)
- [SDK] HTTP 429 maps to `GrowwAPIRateLimitException`; 401 to "API token has either expired or is invalid"; 403 to "Your API token does not have the required permissions". — [PyPI growwapi 1.5.0, `groww/exceptions.py`](https://pypi.org/project/growwapi/)

**Orders, products, segments, data** (all [SDK], from constants and method signatures in `groww/client.py` of [growwapi 1.5.0](https://pypi.org/project/growwapi/))
- Order types: `LIMIT`, `MARKET`, `SL`, `SL_M`. Validity constants: `DAY`, `EOS`, `IOC`, `GTC`, `GTD`.
- Product constants: `CNC`, `MIS`, `NRML`, `MTF`, `BO`, `CO`, `ARB`. (The repo notes Groww's public docs list only CNC/MIS/NRML, so the others may not be accepted server-side.)
- Segments: `CASH`, `FNO`, `COMMODITY`, `CURRENCY`. Exchange constants: `NSE`, `BSE`, `MCX`, `MCXSX`, `NCDEX`, `US`.
- `place_order(validity, exchange, order_type, product, quantity, segment, trading_symbol, transaction_type, order_reference_id=None, price=0.0, trigger_price=None)` posts to `/v1/order/create`. If `order_reference_id` is omitted the SDK sends a random 8-digit number. There is **no AMO / after-market flag** in the signature.
- `get_order_status_by_reference(order_reference_id)` (`/order/status/reference/{id}`) exists, so a caller can look an order up by its own id after a timeout before retrying. The SDK does not state that Groww rejects duplicate reference ids.
- **Smart orders**: `create_smart_order` / `modify_smart_order` / `cancel_smart_order` / `get_smart_order` / `get_smart_order_list` at `/order-advance/*`, types `GTT` and `OCO`, with `trigger_price`, `trigger_direction` (UP/DOWN), `duration` and product type (CNC, MIS).
- Account endpoints: holdings (`/holdings/user`), positions (`/positions/user`, by symbol), available margin (`/margins/detail/user`), per-order margin requirement (`/margins/detail/orders`), order list/detail/status, trades per order, user profile.
- Data endpoints: quote, LTP, OHLC, option chain, Greeks, historical candles (`/historical/candles`; intervals from 1 minute to 1 month), expiries and contracts, instruments CSV.
- Live feed: `GrowwFeed` connects to `wss://socket-api.groww.in` (NATS over WebSocket; the SDK depends on `nats-py`) after creating a socket token; it carries LTP, order updates and position updates (protobuf messages for stocks, stock orders and positions).
- The SDK has a single production base URL (`https://api.groww.in/v1`); there is **no sandbox or paper-trading host or flag** anywhere in the package.

### Inferences
- Minting the token from a serverless function on each run is technically straightforward with the TOTP flow: it needs only the API key, the base32 TOTP secret and one HTTPS POST, with no browser, callback URL or stored session. At 1 to 4 order days a month plus a daily check, the bot would make far fewer token requests than the 150/day cap the repo assumes.
- The token mint itself is probably not IP-restricted (several sources say only order endpoints are IP-checked, see section 3), but I found no official Groww statement on that.
- The daily 06:00 IST expiry is how Groww meets the "sessions logged out before the next trading day" requirement; the TOTP flow meets the two-factor requirement without a human, which is the same approach other brokers accept.
- Because there is no sandbox, the only safe end-to-end test of the order path is Groww's own advice: a very small real order.
- Since the SDK has no AMO flag, a "queue it the night before" design is not available through the API as far as the SDK shows; orders must be sent during market hours (the bot's 15:10 IST slot is fine).

### Gaps
- Could not open groww.in to read the pricing table, the docs' rate-limit table (live-data row), the token-request cap, the reference-id format rule, or any changelog. **groww.in must be allowed in the session's network settings** to confirm these.
- Whether the Rs 0 "Free Trial" plan really allows order placement without the Rs 499 subscription (which would make a data-free, orders-only bot free apart from brokerage) is unconfirmed; the search summary suggests it but the plan table was not read.
- Whether AMO orders are accepted through the API, whether Groww enforces idempotency on `order_reference_id`, and how deep historical data goes (3 months per the product page vs. other claims) remain unverified.
- No search on reliability complaints ran before the budget ended. I found no reliable sources either way on Groww API outages or order-rejection problems in 2026.
- Market-order handling under the new rules: forum thread titles from Zerodha and Dhan ("Regarding Market Protection and Static IP", "Static IP, MPP & Rate Limits", "Preparing to comply ... (Static IP, ratelimits, order types)") show that API market orders are subject to market-price-protection changes at other brokers; I could not read the details or find Groww's handling. Using LIMIT orders avoids the question. — [Kite forum 15873](https://kite.trade/forum/discussion/15873/regarding-market-protection-and-static-ip), [Dhan community 61689](https://madefortrade.in/t/dhanhq-update-safer-participation-of-retail-investors-in-algo-trading-static-ip-mpp-rate-limits/61689)

## 2. SEBI's retail-algo framework and exactly what the static-IP rule requires

### Takeaway
The framework has applied to all brokers since 1 April 2026 and every source found treats it as in force; a self-built bot for one's own account needs no exchange registration below 10 orders per second, but it does need a broker-registered static IP for API orders. The IP may be changed at most once per calendar week, brokers offer one primary plus one optional backup, and sharing is limited to immediate family.

### Cited Findings
**Circulars and timeline**
- Base circular: SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/0000013 dated 4 February 2025, "Safer participation of retail investors in Algorithmic trading". [search summary] — [Groww blog on the static-IP setup](https://groww.in/blog/static-ip-api-trading-setup), [QuotaGuard blog (vendor)](https://www.quotaguard.com/blog/sebis-static-ip-mandate-is-live-fix-your-cloud-trading-bot-now)
- First extension: SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/108 dated 29 July 2025 moved the start from 1 August 2025 to 1 October 2025. [search summary] — [TaxGuru summary](https://taxguru.in/sebi/sebi-extends-algo-trading-implementation-timeline-april-2026.html)
- Second extension with a glide path: **SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/132 dated 30 September 2025**. Milestones: by 31 Oct 2025 brokers apply to register at least one retail algo product and strategy; by 30 Nov 2025 complete registration; mock session 3 Jan 2026; brokers missing the milestones barred from onboarding new retail API-algo clients from 5 Jan 2026; the framework and exchange standards "applicable to all the stock brokers with effect from April 01, 2026". [search summary] — [SEBI circular PDF](https://www.sebi.gov.in/sebi_data/attachdocs/sep-2025/1759232056254.pdf), [Outlook Business](https://www.outlookbusiness.com/markets/sebi-extends-deadline-to-implement-retail-algo-trading-by-april-2026)
- Exchange standards: NSE circular NSE/INVG/67858 (5 May 2025) and NSE/INVG/69255 (22 July 2025), plus an NSE FAQ whose file name is dated 3 Nov 2025. [search summary] — [NSE FAQ PDF](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FAQ_Retail%20Algo_03112025_NSE.pdf)
- In force after 1 April 2026: Fyers published "new SEBI rules for retail algo trading from April 01, 2026"; Groww's own account posted that "as of April 1st, new SEBI rules kick in" and that orders from a dynamic or unregistered IP "will be rejected by broker APIs". Groww's static-IP guide was revised about 69 days before today (roughly early September 2026) and still describes the requirement. [search summaries] — [Fyers support article](https://support.fyers.in/portal/en/kb/articles/what-are-the-new-sebi-rules-for-retail-algo-trading-from-april-01-2026), [Groww post on X](https://x.com/TradeWithGroww_/status/2038996435870621738), [Groww blog](https://groww.in/blog/static-ip-api-trading-setup)

**What the rule says**
- Each client seeking API access must furnish a static IP, "which may be changed no more than once per calendar week"; summaries add a route through the broker for extraordinary circumstances. [search summary] — [NSE FAQ PDF](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FAQ_Retail%20Algo_03112025_NSE.pdf), [MarketCalls summary](https://www.marketcalls.in/market-regulations/new-nse-rules-for-retail-algo-trading-what-retail-traders-algo-platforms-and-brokers-must-now-do.html)
- "Client static IP is required only in case of Tech savvy Investor using API"; when access is through an algo provider, "the static IP shall be that of the vendor or the client". [search summary] — [NSE FAQ PDF](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FAQ_Retail%20Algo_03112025_NSE.pdf)
- Brokers must allow API access only through unique API keys mapped to whitelisted static IPs; open APIs are not permitted for order flow. [search summary] — [Groww blog](https://groww.in/blog/static-ip-api-trading-setup), [QuotaGuard blog (vendor)](https://www.quotaguard.com/blog/sebis-static-ip-mandate-is-live-fix-your-cloud-trading-bot-now)
- Number of IPs: summaries of the May 2025 NSE circular say one primary and one optional secondary static IP. [search summary] — [NSE circular summary on Medium](https://medium.com/@social_62250/nse-circular-summary-safer-participation-of-retail-investors-in-algorithmic-trading-may-2025-63c9238f68b8)
- Order-rate threshold: an individual's own algo needs exchange registration only if orders to the broker exceed **10 per second** (per exchange/segment); all orders received via API are treated as algo orders; non-registered algos run only on designated API keys. [search summary] — [NSE FAQ PDF](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FAQ_Retail%20Algo_03112025_NSE.pdf), [Zerodha Z-Connect overview](https://zerodha.com/z-connect/general/a-comprehensive-overview-of-nses-circular-on-the-new-retail-algo-trading-framework)
- Zerodha's FAQ states a static IP is required "regardless of your order rate" (the 10 OPS threshold exempts from registration, not from the IP rule). [search summary] — [Zerodha Kite Connect FAQs](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/kite-connect-api-faqs)
- Family sharing: one static IP may be shared only with immediate family (spouse, dependent children, dependent parents); sharing outside the family "may lead to suspension of your Kite Connect account and all associated API keys". Other summaries add written consent and 2FA conditions. [search summary] — [Zerodha Kite Connect FAQs](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/kite-connect-api-faqs), [MarketCalls summary](https://www.marketcalls.in/market-regulations/new-nse-rules-for-retail-algo-trading-what-retail-traders-algo-platforms-and-brokers-must-now-do.html)
- Scope: third-party guides consistently report that brokers enforce the whitelist on order endpoints while login, market data and reads of orders/positions work from any address. [search summary; no exchange text found] — [FnOTrader blog](https://www.fnotrader.com/blog/static-ip-for-api-trading), [brokerkit-groww on PyPI](https://pypi.org/project/brokerkit-groww/)

### Inferences
- For Thunderbot (a self-written algo, own account, a handful of orders a month): no algo registration, no empanelment and no strategy approval are needed; the binding requirements are the static IP on order calls, two-factor login, the daily token reset and staying under 10 orders per second. The throttle in the repo already covers the last point by a wide margin.
- "Once per calendar week" plus "primary and backup" means a home ISP or VPS whose IP changes unexpectedly can leave the bot unable to trade for up to a week unless the backup slot holds a second working IP.

### Gaps
- I could not open the SEBI circular or the NSE FAQ, so the following are **unverified background** (from memory of the Feb 2025 circular and May 2025 NSE standards, to be checked against the PDFs above): all API/algo orders carry an exchange-provided unique identifier, with a generic algo ID for unregistered sub-threshold client algos; brokers must use OAuth-based authentication and two-factor login and discontinue other mechanisms; API sessions are logged out before the next trading day's pre-open.
- No authoritative text found on whether the rule is technology-neutral about IPv4 vs IPv6, or on whether exchanges themselves reject an IP already mapped to an unrelated client (QuotaGuard claims brokers do; see section 5).
- No authoritative statement found that data-only calls are exempt; the evidence is broker practice reported by third parties.
- **sebi.gov.in and nsearchives.nseindia.com must be allowed** to confirm exact wording and to check for any circular issued between April and November 2026.

## 3. How Groww implements it, and how other brokers document the same rule

### Takeaway
On Groww the IP is registered on the Trade API "API Keys" page with a primary and an optional secondary address, and orders from any other IP are rejected while reads keep working. Groww's published change-frequency limit was not found, so assume the exchange's once-per-calendar-week limit that Zerodha, Upstox and Dhan all enforce.

### Cited Findings
**Groww**
- Steps in Groww's guide: go to the API Keys section, click "Add static IP", enter the primary static IP, add a secondary static IP as backup, click Update; then place a small test order to confirm. "Once added, your IP will be whitelisted for order placement." [search summary] — [Groww blog: Static IP for API Trading: Setup Guide](https://groww.in/blog/static-ip-api-trading-setup)
- Groww's wording of the rule: order placement must come from a static, whitelisted IP; orders from a dynamic or unregistered IP "will be rejected by broker APIs". [search summary] — [Groww post on X](https://x.com/TradeWithGroww_/status/2038996435870621738)
- Third-party integration docs describe an "Add/Update Static IP" control next to the API key on Groww's API keys page. [search summary] — [OpenAlgo docs, Groww](https://docs.openalgo.in/connect-brokers/brokers/groww)
- Without a registered IP "order placement fails with an IP-rejection error, while reads still work". — [brokerkit-groww on PyPI](https://pypi.org/project/brokerkit-groww/)
- A third-party comparison found "no stated limits" on how often Groww's IP can be changed; another third-party page says Groww allows up to 3 IPs, conflicting with Groww's own primary + secondary description. [search summaries; unreliable] — [onetradejournal comparison](https://onetradejournal.com/trading-apis/static-ip-for-algo-trading), [TradeSteady guide](https://www.tradesteadyalgo.com/pages/blog-how-to-whitelist-ip-broker.html)
- **Groww Cloud**: the title of Groww's guide (as syndicated) is "Static IP for API Trading: Setup Guide (or Skip It with Groww Cloud)", and Groww's X post says "with Groww Cloud, you can skip all of that — deploy your strategies without worrying about static IPs or compliance, and go live in minutes". Groww's blog says even the Rs 0 Free Trial plan gives access to Groww Cloud. [search summaries; marketing claims, mechanics not verified] — [Dailyhunt copy of the Groww guide](https://m.dailyhunt.in/news/india/english/groww-epaper-groww/static+ip+for+api+trading+setup+guide+or+skip+it+with+groww+cloud-newsid-n705632971), [Groww post on X](https://x.com/TradeWithGroww_/status/2038996435870621738), [Groww blog: API trading on Groww](https://groww.in/blog/api-trading-on-groww)

**Other brokers (cross-check)**
- Zerodha: at least one primary IP is mandatory, a secondary is optional; "exchange rules allow just one modification per calendar week"; the setting is at developer-account level for all apps; an order "may be rejected if the whitelisted IP does not exactly match the public IP from which your requests reach Zerodha". [search summary] — [Zerodha: What is a static IP and how to add one](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/static-ip), [Zerodha Kite Connect FAQs](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/kite-connect-api-faqs)
- Zerodha on where the IP may come from: "an ISP (internet service provider), a cloud provider (such as AWS or GCP), or a VPN/VPC service". [search summary] — [Zerodha Kite Connect FAQs](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/kite-connect-api-faqs)
- Zerodha IPv6: a third-party guide says Zerodha's static IP page accepts both IPv4 and IPv6 (not confirmed on Zerodha's page). [search summary] — [trueip.in guide (vendor)](https://www.trueip.in/brokers/zerodha-kite-connect-static-ip/)
- Dhan: "Static IP whitelisting is mandatory as per the new SEBI and exchange guidelines. You can set up a primary and a secondary IP ... Once an IP is setup, you cannot modify the same for the next 7 days"; APIs exist to set, modify and read the IPs. Dhan's support also says "Dhan Cloud deployments are not subject to the Static IP requirement applicable to external API order placement environments". [search summary] — [DhanHQ v2 docs, Authentication](https://dhanhq.co/docs/v2/authentication/), [Dhan support: Is a static IP required for Dhan Cloud?](https://dhan.co/support/platforms/dhanhq-api/is-a-static-ip-required-for-dhan-cloud/)
- Upstox: "Each user is permitted one Primary and one Secondary Static IP for backup and failover"; IPv4 or IPv6 notation accepted; error "Static IP can only be updated once per week"; updating invalidates the existing access token; orders "may be rejected unless traffic originates from a registered IP". [search summary] — [Upstox: Static IP Management APIs](https://upstox.com/developer/api-documentation/announcements/static-ip-apis/), [Upstox: Update Static IPs API](https://upstox.com/developer/api-documentation/update-app-static-ips/)

### Inferences
- Groww follows the same pattern as the three brokers with clear docs: IP bound at the account/API-keys level, two slots, order endpoints only. Plan for a weekly change limit on Groww even though Groww's page was not seen stating it.
- "Groww Cloud" and "Dhan Cloud" show a pattern: a broker-hosted runtime is exempt because orders originate inside the broker's own network. If Groww Cloud can run a small scheduled Python job, it may be the only route that needs neither a server nor a static IP. This is the single most valuable thing to verify next.
- Register a secondary IP from a different provider from day one (for example proxy as primary, home/VPS as backup) so that a provider failure does not cost a week.

### Gaps
- Groww specifics not confirmed from Groww's own pages: change frequency / cool-off, exact error code and message for a non-whitelisted IP, whether the IP is bound per API key or per account, whether IPv6 is accepted, whether smart-order (GTT/OCO) API calls are also IP-checked (they are order instructions, so assume yes).
- What Groww Cloud actually is (hosted notebook/strategy runner? scheduler? supported libraries, outbound internet access to Supabase, pricing, limits) is unknown; the search on it did not run.
- Fyers and Angel One documentation was not reached (support.fyers.in blocked; no search ran for Angel One).

## 4. Options for a fixed outgoing IP without running an always-on server

### Takeaway
Among options with evidence gathered this session, the realistic choices are (a) a paid static-IP proxy whose address is dedicated to you, (b) a scale-to-zero container with its own static egress IP (Fly.io at about $3.60/month for the IP), or (c) a tiny VPS used only as a forward proxy; Vercel's own Static IPs add-on costs $100/month per project and the addresses are shared with other customers. Cheap proxy tiers (QuotaGuard below Enterprise) also use shared IPs, which the vendor itself admits can be refused by Indian brokers.

### Cited Findings
**Vercel**
- Static IPs is an add-on for Pro and Enterprise at **$100/month per project plus Private Data Transfer** (from $0.15/GB per a third-party pricing site); not available on Hobby. [search summary] — [Vercel docs: Static IPs](https://vercel.com/docs/networking/static-ips)
- The addresses come from a shared VPC with subnet-level isolation: "the static IP addresses are shared across a small group of customers in the same region". Dedicated IPs require Secure Compute, which is Enterprise-only with custom pricing. [search summary] — [Vercel docs: Networking](https://vercel.com/docs/networking)

**QuotaGuard (static-IP proxy SaaS)**
- Direct pricing starts at **$19/month for QuotaGuard Static and $29/month for Shield**; Static tiers are $19, $49, $89 and $219 (Enterprise). AP-South-1 (Mumbai) is listed as a region. Every plan gets a pair of static IPs. [search summary] — [QuotaGuard pricing](https://www.quotaguard.com/products/pricing)
- "Dedicated IPs are only available on Enterprise, and lower tiers share IPs with other customers"; the AWS Marketplace listing shows Shield Enterprise at $249/month with dedicated IPs. [search summary] — [QuotaGuard blog: dedicated IPs per tenant](https://www.quotaguard.com/blog/dedicated-static-ip-per-tenant-trading-platform), [AWS Marketplace: QuotaGuard Shield](https://aws.amazon.com/marketplace/pp/prodview-yutsjvgt75g6q)
- QuotaGuard's own Kotak Neo post: "Because brokers require each IP to be uniquely tied to one trader, a shared static IP can be rejected if another QuotaGuard customer has already registered it with the same broker", a risk that grows as more customers onboard. [search summary; vendor source, no independent report found] — [QuotaGuard blog: Kotak Neo static IP](https://www.quotaguard.com/blog/kotak-neo-api-static-ip)
- The Starter plan includes 10 GB per month with no per-GB overage fees. [search summary] — [QuotaGuard blog](https://www.quotaguard.com/blog/saas-static-inbound-ip-enterprise-firewall)

**Fly.io (scale-to-zero machine with its own egress IP)**
- A static egress IP costs **$0.005/hour, about $3.60/month**, and one allocation gives both an IPv4 and an IPv6 address. App-scoped static egress IPs are per region (one for each region where the app has machines); the older machine-scoped type is released when the machine is destroyed. [search summary] — [Fly.io docs: Egress IP addresses](https://fly.io/docs/networking/egress-ips/), [Fly.io pricing](https://docs.fly.io/about/pricing)
- The IP is billed per hour whether or not traffic is sent; stopped machines stop CPU/RAM billing but root filesystem and volumes still bill. [search summary; third-party] — [bex.co analysis, 21 Aug 2026](https://bex.co/blog/2026/08/21/flyio-hidden-billing-lines-nat-gateways-metrics)

**Fixie**
- Fixie's standard product is HTTP/HTTPS only and SOCKS5 is a separate product (Fixie Socks); Fixie "operates in the same data centers as Heroku's US and EU regions". [search summary; the first claim is from a competitor's June 2026 comparison] — [QuotaGuard vs Fixie](https://www.quotaguard.com/blog/quotaguard-vs-fixie-comparison), [Heroku add-on: Fixie](https://elements.heroku.com/addons/fixie)

**Indian "static IP for algo trading" resellers (a category that appeared after the rule)**
- A reseller advertises Rs 100/month for one IPv6 static IP with a free backup address, aimed at Groww users; an aggregator quotes static IPs "from Rs 250/month + GST". [search summaries; vendor claims, unverified] — [staticip.in, Groww page](https://staticip.in/brokers/groww), [Quantsapp, Groww API](https://www.quantsapp.com/brokers/groww/api)

**Home broadband static IP (India)**
- Vendor blogs give inconsistent prices: ACT said to need a business-plan migration or roughly Rs 1,000+/month in select cities; Airtel roughly Rs 300-600/month (another says Rs 200-1,500 and business plans only); JioFiber Rs 200-500/month "when approved", rarely on residential plans; BSNL from about Rs 100 to Rs 200-350/month plus a one-time fee of about Rs 750; a general figure of "Rs 200-500 a month per connection". [search summaries; low reliability, mostly from sellers of alternatives] — [Sarathi Fiber guide 2026](https://sarathifiber.com/static-ip-in-india-jiofiber-airtel-2026/), [MyAlgoMate guide](https://myalgomate.com/blog/static-ip-for-algo-trading-india), [NetSpace India guide](https://www.netspaceindia.com/blog/static-ip-address-in-india/)
- MTNL Mumbai publishes a static-IP tariff for broadband. [page not read] — [MTNL Mumbai static IP tariff](https://mtnlmumbai.in/index.php/broadband/unlimited-plan/static-ip-ip-pool)

### Inferences
- **Latency is irrelevant** for one or two delivery orders at about 15:10 IST; a proxy hop through Singapore or the US would add tens to hundreds of milliseconds, which does not matter. Region matters only for reliability and for any geo-restrictions Groww may apply (unknown).
- Vercel Static IPs is poor value here: about Rs 8,500/month for an IP that is shared with other Vercel customers, against a need of 2 to 4 orders a month.
- A scale-to-zero container with a dedicated egress IP (the Fly.io pattern) is closest to "no server": nothing runs between orders, there is no OS to patch, and the address is allocated to your app rather than shared. Total cost should be about $3.60/month plus cents of compute, if Fly's Mumbai region is used and the IP is confirmed as app-exclusive.
- A VPS forward proxy **is a server**, just a stateless one. It needs: a firewall that accepts connections only from known sources or, since Vercel/Supabase egress IPs are not fixed, strong proxy authentication over TLS (or a WireGuard/SSH tunnel); the proxy restricted to `api.groww.in:443` as its only allowed destination; unattended security upgrades; and a monthly health check, because a silently dead proxy is discovered only at order time.
- A home static IP removes third parties from the path but reintroduces a device that must be on (laptop, router or Raspberry Pi), and depends on the ISP not using carrier-grade NAT.

### Gaps
The searches for the following never ran, so these are **unverified background** from memory (mid-2026 or earlier). Check the linked official page before relying on any number.
- AWS: a NAT Gateway in ap-south-1 costs roughly $0.056/hour (about $40/month) plus per-GB processing, and every public IPv4 address costs $0.005/hour (about $3.60/month); a Lambda in a VPC needs the NAT gateway to have a fixed egress IP. Check [AWS VPC pricing](https://aws.amazon.com/vpc/pricing/).
- AWS Lightsail Mumbai: about $5/month for the smallest IPv4 bundle ($3.50 for IPv6-only), static IP free while attached. Check [Lightsail pricing](https://aws.amazon.com/lightsail/pricing/).
- DigitalOcean Bangalore from $4/month; Vultr (Mumbai, Delhi NCR, Bangalore) $5/month regular, cheaper IPv6-only plans in limited regions; Akamai/Linode (Mumbai, Chennai) $5/month; Hetzner has no India region (Singapore is the nearest). Check each provider's pricing page.
- Oracle Cloud Always Free: free micro VMs with a reserved public IP in Mumbai or Hyderabad home regions, with known capacity shortages and reclamation of idle Always Free instances. Check [Oracle Free Tier](https://www.oracle.com/cloud/free/).
- Google Cloud: the free e2-micro is limited to US regions; Cloud Run needs VPC egress plus Cloud NAT with a reserved IP (NAT gateway hourly fee plus IP fee). Check [Cloud NAT pricing](https://cloud.google.com/nat/pricing).
- Cloudflare Workers have no fixed egress IP unless dedicated egress IPs are bought (Enterprise Zero Trust); Supabase Edge Functions have none; GitHub-hosted runners have none (static-IP larger runners are a paid Team/Enterprise feature); Railway offers static outbound IPs on Pro and Render publishes shared regional outbound ranges, neither with an India region. All unverified this session.
- Fixie's free "Tricycle" tier, current prices and regions; Noble IP; IPRoyal, Bright Data and Proxy-Cheap static ISP/residential proxies and their terms on financial use; Tailscale exit nodes; Azure NAT gateway. Nothing gathered.
- Whether Fly.io still offers the Mumbai (`bom`) region in November 2026, whether an app-scoped egress IP is exclusive to one app, and whether the hourly IP charge continues while machines are stopped (it appears to).
- Whether Vercel Static IPs is offered in bom1.
- Indian ISP facts (current static-IP prices on residential plans, which ISPs use CGNAT, IPv6 static prefixes) rest on weak vendor blogs; confirm with the ISP directly.
- Whether Groww accepts an IPv6 address in the whitelist field (Upstox does; a reseller's Groww offer implies Groww does, but that is a vendor claim).

## 5. Is routing broker orders through a third-party proxy acceptable and safe?

### Takeaway
Using an IP obtained from a cloud, VPN or VPC provider is explicitly accepted by at least one major broker, so a proxy is not prohibited as such; the real problems are shared addresses and trust. A proxy IP that other customers also use breaks the "IP tied to one client or family" premise and may be refused or cause a compliance problem, so only a dedicated address should be registered.

### Cited Findings
- Zerodha's FAQ says a static IP can be acquired from "an ISP, a cloud provider (such as AWS or GCP), or a VPN/VPC service". [search summary] — [Zerodha Kite Connect FAQs](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/kite-connect-api-faqs)
- Sharing an IP outside the immediate family "may lead to suspension of your Kite Connect account and all associated API keys". [search summary] — [Zerodha Kite Connect FAQs](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/kite-connect-api-faqs)
- A proxy vendor concedes that brokers "require each IP to be uniquely tied to one trader" and that a shared proxy IP "can be rejected if another QuotaGuard customer has already registered it with the same broker". [search summary; vendor] — [QuotaGuard blog: Kotak Neo](https://www.quotaguard.com/blog/kotak-neo-api-static-ip)
- Vercel's Static IPs are "shared across a small group of customers in the same region". [search summary] — [Vercel docs: Networking](https://vercel.com/docs/networking)
- The broker checks the public IP "from which your requests reach" it, and rejects on any mismatch. [search summary] — [Zerodha: static IP article](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/static-ip)
- The NSE FAQ allows the static IP to be "that of the vendor or the client" when access is through an algo provider, which shows the framework contemplates orders leaving from infrastructure the client does not own. [search summary] — [NSE FAQ PDF](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FAQ_Retail%20Algo_03112025_NSE.pdf)

### Inferences
**Regulatory and contractual**
- Nothing found prohibits a proxy, VPN or VPS address. What is restricted is sharing one address across unrelated clients. A dedicated proxy or VPS IP is therefore on the same footing as the "cloud provider" case brokers already accept; a shared SaaS or Vercel IP is not.
- Responsibility stays with the client: the account holder registers the IP and is answerable for every order from it. Groww's API terms were not read, so whether Groww adds any restriction is unknown.

**Security (general networking facts, not broker-specific)**
- With a standard HTTPS forward proxy the client sends `CONNECT api.groww.in:443` and then runs TLS end to end with Groww. The proxy operator can see the destination host, timing and byte counts but cannot read the API key, token or order details, provided the client verifies Groww's certificate normally.
- That protection disappears if the service asks you to install its CA certificate, disable certificate verification, or send requests to its own HTTPS endpoint which it then forwards (TLS termination). Avoid any product that works that way for broker traffic.
- The static IP is a second factor on top of the token. Whoever controls the registered address (the proxy operator, or any other customer on a shared IP) already satisfies that factor, so on a shared IP the control adds nothing against other users of the same service; security then rests entirely on the TOTP secret and API key.
- Availability: if the proxy is down at 15:10 on rebalance day, the order cannot be sent, and the IP cannot be swapped quickly because of the weekly change limit. A registered secondary IP from a different provider and a "place it manually" alert cover this.
- Proxy credentials become one more secret to protect; restrict them and rotate them like the broker keys.

**Risk ranking for this bot, lowest risk first**
1. Bot decides, human taps in the Groww app (no API order, no static IP, no third party in the order path).
2. A broker-hosted runtime (Groww Cloud), if it can run the job: no static IP and no third party, but unverified.
3. Own static IP at home (ISP-issued, not CGNAT) with the laptop or a small device placing the order: no third party, but a device must be on and the ISP must keep the address stable.
4. Dedicated egress IP on infrastructure you control: a tiny VPS forward proxy, or a scale-to-zero container with its own egress IP. One provider to trust, end-to-end TLS, address exclusive to you.
5. Proxy SaaS with a dedicated IP (for example QuotaGuard Enterprise at $219+/month): technically fine, but expensive for 2 to 4 orders a month and adds an operator who could originate traffic from your registered IP.
6. Shared-IP products (QuotaGuard Starter-class plans, Vercel Static IPs, Render-style shared ranges): may be refused at registration, conflicts with the one-client-per-IP premise, and gives no real IP protection.
7. Residential/ISP "static" proxy marketplaces: unknown operators, addresses often resold or shared, terms frequently exclude financial transactions. Not suitable.

### Gaps
- Groww's API terms of use and any Groww statement on VPN, proxy or cloud IPs were not found (groww.in blocked).
- No independent report (forum, Reddit, TradingQnA) was found of a broker rejecting an IP because another client had registered it; the only source is QuotaGuard's own blog.
- Proxy providers' terms on financial transactions were not checked.
- Whether exchanges cross-check one IP across clients of **different** brokers is unknown.

## 6. What stays impossible without a static IP, what is still possible, and the semi-automatic design

### Takeaway
Without a registered static IP, API order placement on Groww does not work from Vercel (Hobby, or Pro without the add-on), Supabase Edge Functions, GitHub Actions or a laptop on a dynamic connection; everything else the bot does still works. Because a monthly ETF rotation needs only about 2 to 4 orders a month (one sell and one buy per switch, and no orders in months with no switch), "bot decides, human places the order" is a workable design.

### Cited Findings
- Orders from a dynamic or unregistered IP "will be rejected by broker APIs". [search summary] — [Groww post on X](https://x.com/TradeWithGroww_/status/2038996435870621738)
- Without a whitelisted IP, "order placement fails with an IP-rejection error, while reads still work"; guides describe the usual symptom as an "IP not whitelisted" or HTTP 403 response while login, prices and positions keep working. — [brokerkit-groww on PyPI](https://pypi.org/project/brokerkit-groww/), [FnOTrader blog](https://www.fnotrader.com/blog/static-ip-for-api-trading)
- "Reading orders, positions and order updates needs no static IP." [search summary; third-party] — [FnOTrader blog](https://www.fnotrader.com/blog/static-ip-for-api-trading)
- The static-IP requirement attaches to clients using the API; the NSE FAQ frames it as required "in case of Tech savvy Investor using API". Orders placed by hand in the broker's app are not API orders. [search summary] — [NSE FAQ PDF](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FAQ_Retail%20Algo_03112025_NSE.pdf)
- Groww markets Groww Cloud as a way to deploy strategies "without worrying about static IPs". [search summary; marketing claim] — [Groww post on X](https://x.com/TradeWithGroww_/status/2038996435870621738)
- [SDK] GTT and OCO smart orders can be created through the API (`/order-advance/create`). — [PyPI growwapi 1.5.0](https://pypi.org/project/growwapi/)

### Inferences
- **Impossible today without a registered static IP:** placing, modifying or cancelling Groww orders by API from any platform with rotating or shared egress (Vercel Hobby, Vercel Pro without the Static IPs add-on, Supabase Edge Functions, GitHub-hosted runners, a home connection with a dynamic or CGNAT address). API smart orders (GTT/OCO) are order instructions and should be assumed to fall under the same check.
- **Still possible from serverless without a static IP:** computing signals, paper trading, fetching prices and history (from Groww with the paid plan, or free sources), reading Groww holdings, positions, margins and order status, minting the daily token, writing to Supabase, and sending notifications.
- **Semi-automatic design:** on a rebalance day the bot sends a message at about 15:05 IST stating exactly what to sell and buy, with quantities and limit prices; the owner places the 1 to 2 orders in the Groww app in under a minute; after 15:30 the bot reads the order book and holdings through the (non-order) API and confirms that the portfolio matches, alerting if not. The read-back step keeps the audit trail and catches missed or mistyped orders.
- At 2 to 4 orders a month the manual effort is a few minutes a month, against a cost of roughly Rs 300 to Rs 8,500 a month and added failure modes for the fully automatic routes. Full automation is a convenience here, not a necessity.
- If the Rs 499/month API subscription is only needed for data (section 1), a semi-automatic bot that takes prices from a free source and only reads holdings from Groww might not need the subscription at all; this depends on which endpoints the free plan allows.

### Gaps
- Not researched (budget ended): whether the Groww app supports deep links to a pre-filled order ticket, basket orders for delivery equity, stock/ETF SIPs, or in-app GTT for CNC, and whether any of these could mechanise a monthly switch without the API. From memory, Groww offers stock SIPs and GTT in the app, but neither performs a conditional "sell ETF A, buy ETF B" rotation; treat as unverified.
- Whether read endpoints (holdings, order list) are available on the Rs 0 plan.
- Whether Groww Cloud can host a once-a-day scheduled job with outbound access to Supabase; if yes, full automation would need no static IP and no server.
