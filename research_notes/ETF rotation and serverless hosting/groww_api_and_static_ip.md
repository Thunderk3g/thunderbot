# Groww Trade API and SEBI's static-IP rule for retail API orders (state as of 11 November 2026), and ways to get a fixed outbound IP without an always-on app server

Reading notes for the report writer:

- **How each source was read.** "Read in full" means I downloaded and read the primary document on 11 Nov 2026. "Search snippet" means the page's host was blocked in this session and the fact comes from a search-engine summary of that page. Blocked hosts included quotaguard.com, dhan.co, kite.trade, upstox.com, fyers.in, tradingqna.com, usefixie.com, aws.amazon.com, vultr.com, digitalocean.com, fly.io, render.com, railway.com and marketcalls.in. Treat snippet-only facts as lower confidence.
- **Source classes** are marked as REGULATOR (SEBI/NSE text), BROKER (official broker page), VENDOR (a company selling static IPs or proxies), and USER (forum or blog).
- **INR conversions** use an assumed round rate of ₹90 per USD. I did not source this rate; re-convert at the current rate.
- This note extends section 5 of `/home/user/thunderbot/research_notes/Evidence based NSE trading strategies/costs_and_taxes.md` (Groww API pricing and rate limits as of October 2026) and does not repeat its detail.

## 1. Groww Trade API as of late 2026: pricing, coverage, SDK, base URL

### Takeaway
Nothing material has changed since the October 2026 note: ₹499/month + 18% GST or ₹4,999/year + GST, with a ₹0 "Free Trial" tier that can place, modify and cancel orders and read holdings, positions and margins, but has no live data or historical/backtesting data. The REST base is `https://api.groww.in/v1`, and the official Python SDK `growwapi` is still at 1.5.0 (December 2025), with no release in the 11 months since.

### Cited Findings
- BROKER (Groww blog, published 30 Sep 2026, read 11 Nov 2026): Free Trial is "₹0 per month" with "access to Groww Cloud and all APIs except Live data and Backtesting APIs". Monthly is "₹499 per month plus taxes, billed at ₹6,000 per year". Yearly is "₹417 per month plus taxes, billed at ₹4,999 per year". Paid plans auto-renew from the Groww balance. The Free Trial lets you "place, modify and cancel orders, create smart orders" and check positions, holdings and margin. Live quotes, LTP, OHLC, option chain, Greeks and historical candles are "covered in paid plans". — [Groww Blog: API Trading on Groww](https://groww.in/blog/api-trading-on-groww)
- BROKER (Groww landing page, read 11 Nov 2026): still shows an "Early Bird" flat price of ₹499/month + taxes (struck through ₹2,000) covering Orders API, full Live Data API (LTP, Quote, OHLC), Margin API and Historical Data, with historical data described as available for up to 3 months. The landing page does not mention the free tier or the annual plan. Its FAQ says anyone with a Groww account can use the APIs, for Stocks, F&O and MTF on NSE and BSE. — [groww.in/trade-api](https://groww.in/trade-api)
- BROKER (Groww cURL docs, read in full 11 Nov 2026): prerequisites are a Groww account and "an active Trading API Subscription", bought from groww.in/user/profile/trading-apis. "Groww Trading APIs currently support equity (CASH) and derivatives (FNO) trading only. Commodities trading (MCX segment) is not available at this time." — [Groww Trade API cURL docs](https://groww.in/trade-api/docs/curl)
- BROKER: REST endpoints sit under `https://api.groww.in/v1` (for example `POST https://api.groww.in/v1/order/create`). Mandatory headers are `Authorization: Bearer {ACCESS_TOKEN}`, `Accept: application/json` and `X-API-VERSION: 1.0`. Documented error codes are GA000 (internal error), GA001 (bad request), GA003 (unable to serve), GA004 (entity does not exist), GA005 ("User not authorised to perform this operation"), GA006 (cannot process) and GA007 (duplicate order reference id). — [Groww Trade API cURL docs](https://groww.in/trade-api/docs/curl)
- BROKER: documentation sections are Instruments, Orders, Smart Orders (GTT/OCO), Portfolio (holdings, positions), Margin, Live Data, Historical Data, Backtesting, User, Annexures and Changelog. — [Groww Trade API cURL docs](https://groww.in/trade-api/docs/curl)
- BROKER: the instruments master is a downloadable CSV at `https://growwapi-assets.groww.in/instruments/instrument.csv`. — [Groww docs: Instruments](https://groww.in/trade-api/docs/python-sdk/instruments)
- BROKER: the order API examples use `PRODUCT_CNC`, `SEGMENT_CASH`, `EXCHANGE_NSE` and order types `ORDER_TYPE_LIMIT`, `ORDER_TYPE_MARKET`, `ORDER_TYPE_STOP_LOSS` and `ORDER_TYPE_STOP_LOSS_MARKET`. — [Groww docs: Orders](https://groww.in/trade-api/docs/python-sdk/orders)
- SDK version (PyPI JSON, fetched 11 Nov 2026): latest `growwapi` is **1.5.0**, uploaded 6 Dec 2025, requires Python >=3.9,<4.0. Earlier uploads: 1.3.0 (26 Nov 2025), 1.2.0 (10 Nov 2025), 1.1.0 (8 Oct 2025), 1.0.0 (3 Oct 2025). — [PyPI growwapi](https://pypi.org/project/growwapi/)
- BROKER (SDK changelog, read 11 Nov 2026): 1.5.0 is dated 3 Dec 2025 ("Smart order doc enhancements"); 1.4.0 (2 Dec 2025) added `get_user_profile`; 1.3.0 added the option chain API; 1.2.0 added Smart Orders; 1.0.0 added historical data; 0.0.9 (4 Sep 2025) added checksum-based token generation; 0.0.8 (11 Jun 2025) added TOTP support. The changelog has no entry about static IPs. — [Groww SDK changelog](https://groww.in/trade-api/docs/python-sdk/changelog)

### Inferences
- A handful of delivery orders a month can be placed on the ₹0 tier, as far as Groww's blog states. The paid tier is needed only if the bot wants Groww's own quotes or candles. The static-IP requirement (sections 4 and 5) applies whichever tier is used.
- The landing page and the blog disagree in presentation (flat ₹499 "Early Bird" versus three tiers). The blog is newer and more detailed, so the three-tier description is the better guide, but the purchase page should be checked at subscription time.

### Gaps
- I could not open the logged-in subscription page (groww.in/user/profile/trading-apis), so I could not confirm that the ₹0 tier is still offered at checkout in November 2026 or how long a "trial" lasts.
- No per-order API fee was found. Normal brokerage still applies (see the costs note).
- Whether market data is ever billed separately from the ₹499 plan: no source says so. The blog treats data as part of the paid plan.

## 2. Login and authentication: daily-approval key+secret flow versus TOTP flow, token lifetime, token limits

### Takeaway
Groww documents three routes to an access token: a token generated by hand on the website, an API key + secret flow that needs a daily manual approval, and a TOTP flow intended for unattended use. Access tokens expire daily at 06:00, and the token endpoint is capped at 150 requests per 24 hours. Groww's own two documentation pages contradict each other on whether the TOTP flow also needs daily approval, so that must be tested on the live account before relying on it.

### Cited Findings
- BROKER (cURL docs, raw page text checked 11 Nov 2026): "1st Approach: Access Token (Expires daily at 6:00 AM)", generated by hand from the Trading APIs settings page. "2nd Approach: API Key and Secret Flow (Uses API Key and Secret — Requires daily approval on Groww Cloud Api Keys Page)", which posts `key_type: "approval"` with a checksum and timestamp. "3rd Approach: TOTP Flow (Uses API Key and Totp code — Requires daily approval on Groww Cloud Api keys page)", which posts `key_type: "totp"`. — [Groww Trade API cURL docs](https://groww.in/trade-api/docs/curl)
- BROKER (Python SDK docs, raw page text checked 11 Nov 2026): "1st Approach: API Key and Secret Flow (Uses API Key and Secret — Requires daily approval on Groww Cloud Api Keys Page)" and "2nd Approach: TOTP Flow (Uses TOTP token and TOTP QR code — No Expiry)". The TOTP flow uses `GrowwAPI.get_access_token(api_key=..., totp=...)` and needs `pip install pyotp`. — [Groww Trade API Python SDK docs](https://groww.in/trade-api/docs/python-sdk)
- **Conflict:** the same TOTP flow is labelled "No Expiry" in the Python SDK page and "Requires daily approval" in the cURL page. Both labels were present in the raw HTML on 11 Nov 2026. — [Python SDK docs](https://groww.in/trade-api/docs/python-sdk); contradicted by [cURL docs](https://groww.in/trade-api/docs/curl)
- BROKER: the token endpoint is `POST https://api.groww.in/v1/token/api/access` with `Authorization: Bearer <USER_API_KEY>`. The token response carries an `expiry` field (ISO date-time) and an `isActive` flag. The checksum timestamp is valid for 10 minutes. — [Groww Trade API cURL docs](https://groww.in/trade-api/docs/curl)
- BROKER: rate limits on authentication are 5 per second and 30 per minute, and "The /v1/token/api/access endpoint is also subject to a limit of 150 requests per 24 hours". — [Groww Trade API Python SDK docs](https://groww.in/trade-api/docs/python-sdk)
- BROKER: the Groww blog lists "5 sessions per user" and describes OAuth 2.0 as a key feature. — [Groww Blog: API Trading on Groww](https://groww.in/blog/api-trading-on-groww)
- REGULATOR: "All API sessions shall be compulsorily logged out every day before the start of the next trading day." — [NSE circular NSE/INVG/67858, 5 May 2025, Annexure A.8](https://nsearchives.nseindia.com/content/circulars/INVG67858.pdf)
- REGULATOR: brokers must "have OAuth (Open Authentication) based authentication only and all other authentication mechanisms shall be discontinued" and "authenticate access to API through two factor authentication". — [SEBI circular SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/0000013, 4 Feb 2025, para 5.I.d](https://www.sebi.gov.in/sebi_data/attachdocs/feb-2025/1738665456458.pdf)
- REGULATOR: the NSE operational modalities soften this to "OAuth (Open Authentication) / SEBI mandated 2FA based authentication only or any authentication mechanism allowed / communicated by the Exchange / SEBI from time to time". — [NSE circular NSE/INVG/69255, 22 Jul 2025, Annexure I para 10.9](https://nsearchives.nseindia.com/content/circulars/INVG69255.zip)

### Inferences
- The most plausible reading is that "No Expiry" describes the TOTP key (it does not need re-approval each morning), while every access token it produces still dies at 06:00, because NSE requires all API sessions to be logged out daily. A bot that trades at 15:10 IST would therefore generate a fresh token each trading day shortly before use. One token request a day is far inside the 150-per-24-hours cap.
- The TOTP secret lets code generate the second factor, which is how Groww's flow satisfies the two-factor rule without a human. It also means the API key plus TOTP secret together are full order-placing credentials and must be stored as secrets.
- If the cURL page is the correct one and TOTP also needs daily approval, a fully unattended bot is not possible on Groww, and the fallback is one tap of approval each trading morning.

### Gaps
- Groww does not say whether token generation is restricted to the whitelisted IP. Zerodha and Upstox restrict only order endpoints (section 5), but for Groww this is unverified.
- I found no user reports confirming how the TOTP flow behaves day to day in 2026.

## 3. Rate limits and the 10 orders-per-second threshold

### Takeaway
Groww's limits (10 orders/second, 250/minute) sit at the regulatory ceiling. Below 10 orders per second per exchange a client-written algo needs no registration, but every API order is still treated and tagged as an algo order. A bot that places a few orders a month is nowhere near any limit.

### Cited Findings
- BROKER: Groww limits by type are Orders 10/sec and 250/min; Live Data 10/sec and 300/min; Non-Trading (order status, order list, trade list, positions, holdings, margin) 20/sec and 500/min; Authentication 5/sec and 30/min. Limits apply per type, not per endpoint. Live feed allows up to 1,000 subscriptions. — [Groww Trade API Python SDK docs](https://groww.in/trade-api/docs/python-sdk)
- BROKER: the Groww blog gives 250 order requests/minute, 300 market-data requests/minute, 3,000 real-time subscriptions and 25 modifications per order (the subscription figure conflicts with the docs' 1,000, as the October note recorded). — [Groww Blog: API Trading on Groww](https://groww.in/blog/api-trading-on-groww)
- REGULATOR: "The Threshold Order Per Second (TOPS) is initially set at not exceeding 10 orders per second ... If the flow of algo orders from the client to the broker via API is below the defined Threshold Order Per Second (TOPS) i.e. 10 OPS per exchange, the client will not be required to register for algorithmic trading from the broker's system. The threshold will be applied basis the calendar clock second of the broker server." — [NSE/INVG/67858, Annexure B.2](https://nsearchives.nseindia.com/content/circulars/INVG67858.pdf)
- REGULATOR: orders above the threshold must be rejected by the broker unless the algo is registered: "the broker shall reject/ not accept/not process any orders exceeding the OPS limit". A client wanting more than 10 OPS "must register their algorithm with each Exchange". The broker may set a lower client-level limit. — [NSE/INVG/67858, Annexure B.5, C.1, F](https://nsearchives.nseindia.com/content/circulars/INVG67858.pdf)
- REGULATOR: "All algo orders (Below and above the threshold) shall be tagged with a unique identifier provided by the Exchange in order to establish audit trail." Orders below the threshold get "a generic algo ID ... provided by the Exchange". — [NSE/INVG/67858, Annexure B.3, G](https://nsearchives.nseindia.com/content/circulars/INVG67858.pdf)
- REGULATOR: for unregistered client algos within 10 OPS, the broker sends Algo ID "99999" and sets the 13th digit of the NNF ID to "0"; the client-direct-API channel is identified by the 12 digits "444444444444". — [NSE/INVG/69255, Annexure I paras 2.1 and 8.2.4](https://nsearchives.nseindia.com/content/circulars/INVG69255.zip); [NSE FAQ dated 3 Nov 2025, Q7](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FAQ_Retail_Algo_03112025_NSE.pdf)
- REGULATOR: "all orders received via API from clients are considered Algo orders and require appropriate tagging including standardised tagging for cases where the OPS is within the threshold of 10 OPS." — [NSE FAQ dated 3 Nov 2025, Q8](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FAQ_Retail_Algo_03112025_NSE.pdf)
- REGULATOR: SEBI's circular says algos written by tech-savvy retail investors must be registered "only if they cross the specified order per second threshold", and a registered algo may be used for the investor's family, defined as "self, spouse, dependent children and dependent parents". — [SEBI circular 4 Feb 2025, para 5.I.c](https://www.sebi.gov.in/sebi_data/attachdocs/feb-2025/1738665456458.pdf)
- REGULATOR: "Algo orders with order type as Market Order are not permitted" (quoting NSE/MSD/67753 point 8.1.1.12). The operational modalities add that members must adhere to the market price protection check "by not placing any algorithmic orders on the Exchange as a market order". — [NSE FAQ dated 3 Nov 2025, Q11](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FAQ_Retail_Algo_03112025_NSE.pdf); [NSE/INVG/69255, Annexure I audit table item 5](https://nsearchives.nseindia.com/content/circulars/INVG69255.zip)

### Inferences
- The algo-ID tagging is done by the broker. The owner of a sub-10-OPS personal bot does not apply to the exchange for anything; the broker tags the orders with the generic ID.
- Because every API order counts as an algo order and algo orders may not reach the exchange as market orders, the bot should send **limit** orders (for example a marketable limit a little through the touch at 15:10). Groww's SDK still lists `ORDER_TYPE_MARKET`; how Groww treats an API market order (reject, or convert to a protected limit) is not documented in what I read and should be tested with a one-share order.

### Gaps
- Groww's handling of API market orders after 1 April 2026 is unverified.
- Some lines of the NSE/INVG/67858 PDF did not extract (parts of clauses A.1, B.3, C.3, C.4 and I.h), so quotes above are limited to text that extracted cleanly.

## 4. The static-IP rule: what the regulator text says, and the timeline

### Takeaway
SEBI's 4 February 2025 circular bans "open APIs" and allows API access "only through a unique vendor client specific API key and static IP whitelisted by the broker". NSE's implementation standards (5 May 2025) add the working detail: one primary IP plus an optional secondary, changes at most once per calendar week, and **"A static IP can only be mapped to one client at a time"** except within a family. After two extensions the whole framework became applicable to all brokers on 1 April 2026, and there is no order-count threshold below which the static IP is waived.

### Cited Findings
- REGULATOR (read in full): brokers shall "not permit open APIs and allow access only through a unique vendor client specific API key and static IP whitelisted by the broker to ensure identification and traceability of the algo provider and the end user (i.e. investor)". Original effective date: "The provisions of this circular shall be applicable with effect from August 01, 2025." — [SEBI circular SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/0000013, 4 Feb 2025](https://www.sebi.gov.in/sebi_data/attachdocs/feb-2025/1738665456458.pdf)
- REGULATOR (read in full): SEBI's 30 Sep 2025 circular records that the date was first extended to 1 Oct 2025 "vide circular dated July 29, 2025". It then let ready brokers go live from 1 Oct 2025 and set a glide path for the rest: Milestone 1, apply to register API-based retail algo products and at least one strategy by 31 Oct 2025; Milestone 2, complete registration by 30 Nov 2025; Milestone 3, take part in at least one mock session by 3 Jan 2026. Brokers missing the milestones "shall be barred from onboarding new retail clients for API based algo trading framework w.e.f. January 05, 2026". Finally: "W.e.f. April 01, 2026, algo framework specified in circular dated February 04, 2025 along with implementation standards and detailed operational modalities (issued by exchanges) will be applicable for all stock brokers." — [SEBI circular SEBI/HO/MIRSD/MIRSD-PoD/P/CIR/2025/132, 30 Sep 2025](https://www.sebi.gov.in/sebi_data/attachdocs/sep-2025/1759232056254.pdf)
- REGULATOR (read in full, NSE implementation standards, Annexure section A):
  - A.1: "To gain access, clients must mandatorily provide the stockbroker with a static IP address(es)".
  - A.2: "The client may give only one static IP address (primary), or provide additional Static IP address (secondary) for the purpose of connectivity redundancy".
  - A.3: multiple API keys may map to the same primary/secondary IPs "of that client only", or have separate IPs per key.
  - A.5: "The need for static IP is mandatory for API access for client generated algos ... In case of client generated algos, the static IP shall be that of the client".
  - A.6: "Clients will have the ability to update their mapped static IP addresses as needed, but not more than once a calendar week. Clients may reach out to the broker in extraordinary cases".
  - A.7: "A static IP can only be mapped to one client at a time. However, static IPs can be shared between clients provided such clients belong to one family as defined in SEBI circular SEBI/HO/MIRSD/MIRSD-PoD1/P/CIR/2024/169 dated 3 December 2024. The client shall provide a written request / email from registered email / request using 2FA validation to the broker for sharing the static IP to such family."
  — [NSE circular NSE/INVG/67858, 5 May 2025](https://nsearchives.nseindia.com/content/circulars/INVG67858.pdf)
- REGULATOR: section I.e of the same annexure repeats that "open APIs are not permitted, and access is being provided only through a unique vendor client specific API key and static IP whitelisted by the broker for retail users". Section I.f makes the broker "fully responsible and liable for all orders emanating through their ... Client API" systems. — [NSE/INVG/67858](https://nsearchives.nseindia.com/content/circulars/INVG67858.pdf)
- REGULATOR: the NSE FAQ confirms scope: "Client static IP is required only in case of Tech savvy Investor using API" and "Tech Savvy client is required to host the Algo using a static IP at their end where Algo logic resides instead of hosting the Algo on Trading Member's cloud server". Clients who trade through a broker-hosted or vendor algo platform use the broker's server IP instead. — [NSE FAQ dated 3 Nov 2025, Q3, Q5, Q6, Q10](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FAQ_Retail_Algo_03112025_NSE.pdf)
- REGULATOR: for the "Tech savvy client category" the broker must disclose the client's PAN and UCC to the exchange, and the client is given a terms-and-conditions document (Annexure 9). The broker's order-routing server must be located in India. — [NSE/INVG/69255, 22 Jul 2025, Annexure I paras 2.5, 10.2, 10.14](https://nsearchives.nseindia.com/content/circulars/INVG69255.zip)
- No later relaxation found: an extended search on 11 Nov 2026 for any SEBI or exchange change after 1 April 2026 returned only explainers describing the requirement as in force. — [Fyers support: new SEBI rules from April 01, 2026 (search snippet)](https://support.fyers.in/portal/en/kb/articles/what-are-the-new-sebi-rules-for-retail-algo-trading-from-april-01-2026); [Zerodha "In the Money": SEBI algo trading changes April 2026 (search snippet)](https://inthemoneybyzerodha.substack.com/p/sebi-algo-trading-changes-april-2026)

### Inferences
- **All API orders, no threshold.** The 10-OPS line decides only whether the algo must be registered. The static IP is a condition of API access itself (A.1, A.5), so even one API order a month needs a whitelisted IP.
- **Orders versus read-only calls.** The regulator text gates "API access" as a whole and does not carve out read-only calls. The carve-out seen in practice (section 5) is a broker implementation choice: brokers enforce the IP check on order placement, modification and cancellation only. It could be tightened without a new SEBI circular.
- **IPv4 or IPv6.** The SEBI and NSE texts I read say nothing about IP version. Acceptance of IPv6 is broker-specific (section 5).
- **Rejection.** The regulator text does not spell out the consequence of a mismatched IP; brokers implement it as an order rejection (section 5).
- **What a personal bot owner is, in the rulebook's terms:** a "tech savvy retail investor (within OPS threshold)", running an unregistered algo through a client direct API, tagged by the broker with generic algo ID 99999.

### Gaps
- I did not open SEBI's 29 July 2025 extension circular or the BSE equivalents; the 29 July date comes from SEBI's own 30 Sep 2025 circular.
- The family definition in SEBI circular 2024/169 (3 Dec 2024) was not read; SEBI's Feb 2025 circular defines family as self, spouse, dependent children and dependent parents.
- I could not check SEBI's and NSE's circular listings exhaustively for 2026 changes; "no relaxation found" rests on searches.

## 5. How Groww and other brokers implement the rule

### Takeaway
Groww whitelists a primary and an optional secondary IP at groww.in/trade-api/api-keys and applies the check to order placement; it does not publish its change frequency, IPv6 stance, family process or error text. Zerodha, Upstox, Dhan, Fyers and Tradejini all describe the same shape: two IP slots, one change per week, family sharing only by declaration, enforcement on order endpoints only, and rejection of orders from any other IP.

### Cited Findings
**Groww**
- BROKER (Groww blog, published 2 Sep 2026, read 11 Nov 2026): "order placement must originate from a static IP". Steps: open the API Keys section at https://groww.in/trade-api/api-keys, click "Add static IP", enter the Primary Static IP, "Add a Secondary Static IP as backup", click Update; the IP is then whitelisted for order placement and Groww suggests a small test order. Ways to get one: an ISP add-on (Airtel, Jio, ACT) at "₹300 – ₹1,000/month", or a cloud server with a static public IP (AWS, GCP, DigitalOcean, Azure) at "$5 – $50/month". The post says nothing on change frequency, family sharing, IPv4/IPv6, VPNs, proxies, shared IPs or error messages. — [Groww Blog: Static IP for API Trading: Setup Guide](https://groww.in/blog/static-ip-api-trading-setup)
- BROKER (Groww's X account, posted 31 Mar 2026 per the post ID; search snippet): "As of April 1st, new SEBI rules kick in for algo traders using APIs. Order placement must now come from a static, whitelisted IP ... If your orders come from a dynamic or unregistered IP, they'll be rejected by broker APIs." — [Trading with Groww on X](https://x.com/TradeWithGroww_/status/2038996435870621738)
- Groww's API documentation pages (cURL intro, Python SDK intro, changelog) contain no mention of static IPs or whitelisting as of 11 Nov 2026. — [Groww cURL docs](https://groww.in/trade-api/docs/curl); [Groww SDK changelog](https://groww.in/trade-api/docs/python-sdk/changelog)
- USER/VENDOR conflict: one static-IP vendor page says Groww allows "up to 3 static IPs"; Groww's own blog describes two slots (primary and secondary). — [staticip.in Groww page (search snippet)](https://staticip.in/brokers/groww); contradicted by [Groww Blog](https://groww.in/blog/static-ip-api-trading-setup)
- USER: a third-party comparison checked 13 Oct 2026 notes that Groww's page speaks only of order placement, lists primary and secondary slots, and does not state a lock period or change frequency. — [onetradejournal (search snippet)](https://onetradejournal.com/trading-apis/static-ip-for-algo-trading)

**Zerodha (Kite Connect)**
- BROKER (support article, read in full 11 Nov 2026): "effective 1 April 2026, you must have a static IP for API-based order placement. This requirement applies to all API-based order placement". "The WebSocket market data stream and other APIs, such as orderbook and positions, can continue to be accessed from any IP address." "You typically obtain a static IP from internet service providers (ISPs), cloud, or Virtual Private Server (VPS) providers." "Exchange rules allow just one modification per calendar week." "You must add at least one primary IP. You can add up to two IPs". Family accounts (spouse, dependent children, dependent parents) can share an IP through one developer account, with the declaration "I confirm that the above static IPs will be used exclusively by me and/or my immediate family." — [Zerodha Support: What is a static IP](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/static-ip)
- BROKER/USER (Kite forum, search snippets): staff replies say the requirement is "applicable only to order-related endpoints (placement, modification, and cancellation)"; that an EC2 instance's public IP can be used if made static; that sharing is allowed only with regulation-permitted family members ("HUF and members can share IP. Partners cannot"); and that surveillance "may also suspend API access if such accounts are sharing static IPs among unrelated people". A user's question "Is placing orders via a proxy IP allowed?" had no staff answer in the results. — [Kite Connect forum](https://kite.trade/forum/discussion/comment/50533); [Kite Connect forum](https://kite.trade/forum/discussion/comment/50587/)

**Upstox**
- BROKER (developer docs, search snippets): each app supports "one Primary and one Secondary Static IP"; the IPs may be "IPv4 or IPv6, standard notation"; "other standard APIs (holdings, positions, funds, historical candles etc.) are not restricted by Static IP"; a mismatched IP gets HTTP 403 with error UDAPI1154 (static IP restriction); a successful IP update invalidates the existing access token. — [Upstox: algo trading circular announcement](https://upstox.com/developer/api-documentation/announcements/algo-trading-circular); [Upstox: Update App Static IPs](https://upstox.com/developer/api-documentation/update-app-static-ips/); [Upstox community: UDAPI1154](https://community.upstox.com/t/i-am-getting-error-udapi1154-while-placing-orders-via-api/14900)

**Dhan**
- BROKER (support pages, search snippets): a whitelisted IP "can only be changed after 7 days, as per the exchange regulations"; the dashboard lets you update a "whitelisted IPv4 / IPv6 address"; a mismatch gives "DH-905 invalid IP"; a Get-Static-IP call returns primary IP, secondary IP, detected IP and orders-allowed status; family accounts "can be mapped to a single Static IP ... subject to the required verification and approval process"; Dhan's guidance says it wants to ensure "no two users are using the same IP address at the same time in our system". — [Dhan: why can't I modify my IP](https://dhan.co/support/platforms/dhanhq-api/why-i-am-unable-to-modify-my-ip-address/); [Dhan: DH-905](https://dhan.co/support/platforms/dhanhq-api/i-have-added-my-static-ip-s-on-dhan-web-but-my-orders-are-getting-rejected-stating-dh-905-invalid-ip-while-placing-them-through-the-api-what-should-i-do/); [Dhan: family accounts](https://dhan.co/support/platforms/dhanhq-api/can-multiple-family-member-accounts-use-the-same-static-ip-for-api-trading/)

**Fyers**
- BROKER (support and community, search snippets): "Each user must have a unique static IP, and it cannot be shared across multiple users", with a declaration-form route for a common IP among family members. A Fyers community reply says "you can fetch the data without static IP address"; the requirement applies to placing orders. — [Fyers support: new SEBI rules from April 01, 2026](https://support.fyers.in/portal/en/kb/articles/what-are-the-new-sebi-rules-for-retail-algo-trading-from-april-01-2026); [Fyers support: common static IP for family](https://support.fyers.in/portal/en/kb/articles/how-to-enable-a-common-static-ip-address-for-family-members-retail-algo-regulations); [Fyers community: static IP for data-only apps](https://fyers.in/community/t/is-a-static-ip-required-for-data-only-applications-historical-market-depth-tbt-under-the-new-sebi-guidelines/22865)

**Others**
- BROKER (Tradejini, search snippets): from 1 April 2026 "all API-based order requests must originate from a registered static IP address"; IP changes are "allowed once per calendar week as per NSE circular"; multiple API keys can map to the same IP; it has a knowledge-base article titled "I use the API only to fetch data and check positions, not to place orders. Do I need a static IP?" — [Tradejini blog](https://www.tradejini.com/blogs/how-to-register-your-static-ip-on-the-tradejini-developer-portal); [Tradejini KB](https://www.tradejini.com/support/knowledge-base/api/static-ip/practical-and-setup/my-algo-is-hosted-on-my-office-server-what-if-the-office-ip-changes)
- BROKER (Rupeezy, search snippet): takes a primary static IP and an optional secondary, "IPv4 or IPv6". — [Rupeezy support](https://support.rupeezy.in/support/solutions/articles/21000004280-how-does-static-ip-work-in-api-trading-)

### Inferences
- Triangulated rule, as brokers apply it in 2026: (a) order place/modify/cancel calls must come from a registered IP, everything else works from anywhere; (b) two slots, primary and secondary; (c) one change per calendar week (Dhan phrases it as a 7-day lock); (d) one IP maps to one client, family excepted by declaration; (e) mismatches are rejected with a broker-specific error.
- For Groww, (a) and (b) are confirmed by Groww's own blog. Points (c) and (d) are not stated by Groww but follow from the NSE standard that binds every broker, so the owner should assume one change per calendar week and get the IP right the first time.
- Groww's error for a wrong IP is undocumented. GA005 ("User not authorised to perform this operation") is a plausible candidate, but that is a guess.
- Because read-only calls are not IP-checked, a successful holdings or quote call proves nothing about whether orders will pass. Only a real order (for example one share, or a far-from-market limit order that is then cancelled) tests the whitelist.

### Gaps
- Groww: IPv6 acceptance, change frequency, family process, exact rejection message, and whether read-only calls are officially exempt (the blog only implies it) all need confirmation from the API Keys page or Groww support.
- Angel One and Kotak Neo pages were found but not read.

## 6. Are datacenter/VPS IPs acceptable, and are shared static IPs acceptable?

### Takeaway
Cloud and VPS static IPs are explicitly accepted (Zerodha's and Groww's own pages name cloud providers as a source). A static IP that other, unrelated broker clients also egress from conflicts with NSE's rule that "A static IP can only be mapped to one client at a time", and brokers repeat that the IP must be unique to the client or the client's family.

### Cited Findings
- BROKER: Zerodha: "You typically obtain a static IP from internet service providers (ISPs), cloud, or Virtual Private Server (VPS) providers." — [Zerodha Support](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/static-ip)
- BROKER: Groww lists hosting "on a cloud server with a static public IP" (AWS, Google Cloud, DigitalOcean, Azure) as one of two ways to comply. — [Groww Blog](https://groww.in/blog/static-ip-api-trading-setup)
- REGULATOR: "A static IP can only be mapped to one client at a time", with sharing only among family on written or 2FA-validated request; and for client-generated algos "the static IP shall be that of the client". — [NSE/INVG/67858, Annexure A.5 and A.7](https://nsearchives.nseindia.com/content/circulars/INVG67858.pdf)
- BROKER: Fyers: "Each user must have a unique static IP, and it cannot be shared across multiple users." — [Fyers support (search snippet)](https://support.fyers.in/portal/en/kb/articles/what-are-the-new-sebi-rules-for-retail-algo-trading-from-april-01-2026)
- BROKER: Zerodha's declaration: "I confirm that the above static IPs will be used exclusively by me and/or my immediate family." — [Zerodha Support](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/static-ip)
- BROKER: Dhan wants to ensure "no two users are using the same IP address at the same time in our system". — [Dhan support (search snippet)](https://dhan.co/support/platforms/dhanhq-api/can-multiple-family-member-accounts-use-the-same-static-ip-for-api-trading/)
- VENDOR: QuotaGuard itself warns that on its lower tiers the static IPs "may be shared across customers", that a shared IP can be rejected if another customer has already registered it with the same broker, and that "SEBI's requirement is traceability: the IP must map to you specifically". — [QuotaGuard blog: SEBI's static IP mandate (search snippet)](https://quotaguard.com/blog/sebis-static-ip-mandate-is-live-fix-your-cloud-trading-bot-now); [QuotaGuard blog: Dhan API static IP (search snippet)](https://quotaguard.com/blog/dhan-api-static-ip)
- USER: a MadeForTrade forum post says a VPN, tunnel or static-IP proxy can be used "only if the broker allows it and the outgoing IP is a dedicated static IP mapped to the client/API key. Shared VPN/proxy IPs should be avoided." — [MadeForTrade forum (search snippet)](https://madefortrade.in/t/static-ip-dhan-cloud-is-not-working/91100)

### Inferences
- A dedicated IPv4 on a VPS or cloud NAT that only the owner uses meets both the letter (one client per IP) and the purpose (traceability) of the rule.
- A shared-pool IP fails the one-client-per-IP rule the moment a second Groww client registers the same address. The broker may reject the registration, or accept it and later flag two unrelated clients on one IP. The owner cannot know or control who else uses the pool.
- I found no rule requiring the client's IP to be located in India (the India-location rule in NSE/INVG/69255 para 10.2 is about the broker's routing server). I also found no Groww statement on foreign IPs.

### Gaps
- No broker FAQ or regulator text that I could read addresses proxies by name. The conclusion on shared proxies is derived from the one-client-per-IP rule, not from an explicit "no proxies" sentence.
- Whether Groww technically checks for duplicate IP registrations across clients is unknown.

## 7. Options for a fixed outbound IP without an always-on app server

### Takeaway
The cheapest compliant route is a dedicated IPv4 the owner alone controls: a home-broadband static IP for a laptop (roughly ₹2,000–7,000 a year), or a small VPS in India (about US$4–6, roughly ₹360–540, a month) used either to run the bot or as a private forward proxy for Vercel. Vercel's own Static IPs cost US$100 a month per project and are shared between customers, and most low-priced proxy plans are shared too, which collides with the one-client-per-IP rule.

### Cited Findings
**Option 1: Vercel Static IPs and Secure Compute**
- VENDOR (Vercel docs, last updated 30 Jun 2026, read in full): Static IPs are available on Pro and Enterprise. "Static IPs are priced at $100/month per project for Pro plus Private Data Transfer". "Each configured region provides two static IP addresses from a shared pool, and a small group of customers in the same region shares them." "Keep your backend's authentication in place, because other customers' traffic can come from the same addresses. If you need IP addresses that only your team uses, use Secure Compute". Up to three regions can be selected; Routing Middleware never uses the static IPs. — [Vercel docs: Static IPs](https://vercel.com/docs/networking/static-ips)
- VENDOR: Static IPs launched 2 Oct 2025 for Pro and Enterprise. — [Vercel changelog](https://vercel.com/changelog/static-ips-are-now-available-for-more-secure-connectivity)
- VENDOR: Secure Compute is Enterprise only with custom pricing; each network gets "a pair of dedicated IP addresses" in a dedicated VPC. — [Vercel docs: Secure Compute](https://vercel.com/docs/networking/secure-compute)
- VENDOR: Mumbai (bom1) is a Vercel region with a published Private Data Transfer price of $0.187 per GB. — [Vercel regional pricing: bom1](https://vercel.com/docs/pricing/regional-pricing/bom1)
- VENDOR: Vercel cron jobs on the Hobby plan may run only once per day with per-hour precision (±59 minutes); Pro allows per-minute scheduling. — [Vercel docs: Cron usage and pricing](https://vercel.com/docs/cron-jobs/usage-and-pricing)

**Option 2: static-IP HTTP proxy services**
- VENDOR (QuotaGuard pricing page, search snippets): QuotaGuard Static is Starter $19/month, Production $49, Business $89, Enterprise $219. "Starter, Production, and Business use shared static IP pairs"; only Enterprise has "dedicated IPs and proxy resources reserved for your account". Shield Enterprise is listed at $259/month (another QuotaGuard page says $269). All plans give a load-balanced pair of IPs. — [QuotaGuard pricing](https://www.quotaguard.com/pricing)
- VENDOR: QuotaGuard says its Static outbound product uses "a blind CONNECT tunnel and does not decrypt payloads". A QuotaGuard post on Angel One's SmartAPI recommends a Mumbai-region proxy host (hostname containing `ap-south-shield-01`). — [QuotaGuard pricing (search snippet)](https://www.quotaguard.com/pricing); [QuotaGuard blog: SmartAPI static IP (search snippet)](https://www.quotaguard.com/blog/smartapi-static-ip-sebi-compliance)
- VENDOR (Fixie, Heroku add-on listing, search snippet): a free plan with 500 requests a month exists; listed regions are US and EU (Virginia, Oregon, Dublin, Frankfurt), and Mumbai is not marked available; each subscriber "is assigned a set of static IPs". — [Heroku add-on: Fixie](https://elements.heroku.com/addons/fixie)

**Option 3: a tiny VPS with its own static IPv4, used to run the bot or as a private forward proxy**
- USER/aggregator: AWS Lightsail's entry Linux bundles are $5/month with a public IPv4 and $3.50/month IPv6-only (figures quoted for US regions; Mumbai price not confirmed). A Lightsail static IP is free while attached to a running instance and about $0.005/hour when not. — [AWS Compute Blog: IPv6 bundles and pricing update (search snippet)](https://aws.amazon.com/blogs/compute/announcing-ipv6-instance-bundles-and-pricing-update-on-amazon-lightsail); [issoh.co.jp Lightsail guide (search snippet)](https://issoh.co.jp/?p=3383)
- USER/aggregator: DigitalOcean's Basic 512 MB droplet is listed at $4/month in Bangalore (aggregator, prices checked 3 Nov 2026). — [valebyte India VPS listing (search snippet)](https://valebyte.com/en/vps/india/)
- USER: Vultr's cheapest plan is $2.50/month IPv6-only; $3.50 is the cheapest with IPv4; a forum comment puts the Mumbai entry plan at $6/month. — [LowEndTalk thread (search snippet)](https://lowendtalk.com/discussion/comment/3412678/)
- VENDOR/USER: Oracle Cloud's Always Free tier continues after the 30-day trial. Idle Always Free instances can be reclaimed: a 2026 blog says Oracle evaluates a 7-day window and treats an instance as idle when CPU (95th percentile), network and, for A1 shapes, memory all stay under 20%; older notices gave 10% and 15%. Oracle's docs describe "out of host capacity" errors for Always Free shapes. A user reports that converting to Pay As You Go prevents idle reclamation. — [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/); [oracommit blog, Feb 2026 (search snippet)](https://oracommit.blogspot.com/2026/02/understanding-oci-always-free-compute.html); [Oracle docs: Always Free resources (search snippet)](https://docs.oracle.com/en-us/iaas/Content/FreeTier/resourceref.htm)
- VENDOR: Google Cloud's free e2-micro VM is limited to us-west1, us-central1 and us-east1. An in-use external IPv4 on a standard VM is priced at $0.005/hour (about $3.65/month); the pricing page also says VM external IPs "are offered with a free tier". — [Google Cloud free tier (search snippet)](https://cloud.google.com/free/docs/compute-getting-started); [Google Cloud network pricing](https://cloud.google.com/vpc/network-pricing)
- USER: OpenAlgo's static-IP FAQ notes that VPS providers such as DigitalOcean, Vultr and OVH come with a static IP by default. — [OpenAlgo docs (search snippet)](https://docs.openalgo.in/static-ip)

**Option 4: static IP on Indian home broadband**
- BROKER: Groww's estimate for an ISP static-IP add-on is "₹300 – ₹1,000/month (depending on speed and provider)". — [Groww Blog](https://groww.in/blog/static-ip-api-trading-setup)
- USER (third-party blogs, search snippets; no ISP price list was read): Airtel about ₹299 + GST/month for retail or ₹300–600/month; JioFiber "inconsistent", ₹200–500 add-on or business plans only, and "Jio's static IP is CGNAT in some areas"; ACT Fibernet ₹250/month in one source and ₹500–1,000/month with a business-plan migration in another; BSNL the cheapest, with an older published schedule of one static IP at ₹2,000 a year for plans from ₹999 to under ₹1,500 a month and free for plans of ₹2,799 and above. — [Sarathi Fiber: static IP in India 2026](https://sarathifiber.com/static-ip-in-india-jiofiber-airtel-2026/); [Marketcalls: how to get a static IP in India](https://www.marketcalls.in/market-regulations/how-to-get-a-static-ip-in-india-for-algo-trading-compliance.html); [99-networks: BSNL static IP charges](https://99-networks.com/bsnl-static-ip-address-plans-charges/)

**Option 5: cloud NAT with a reserved IP, and other platforms**
- USER: AWS NAT Gateway in Mumbai is quoted at $0.056/hour ($40.32 for a 30-day month) plus $0.056 per GB processed; $0.045/hour is the US-region rate. — [CloudKeeper blog (search snippet)](https://www.cloudkeeper.com/insights/blog/aws-cloud-cost-optimization-nat-gateway)
- VENDOR (Google Cloud pricing page, read 11 Nov 2026): Cloud NAT costs $0.0014/hour per assigned VM instance for up to 32 instances, $0.045 per GiB processed, and $0.005/hour for each external IP the gateway uses. — [Google Cloud network pricing](https://cloud.google.com/vpc/network-pricing)
- USER: Fly.io static egress IPv4 is about $3.60/month per address per region (secondary sources; a Fly community thread gives $0.005/hour for a machine-scoped version). — [Fly.io docs: egress IPs (search snippet)](https://fly.io/docs/networking/egress-ips/); [Fly community thread (search snippet)](https://community.fly.io/t/static-egress-ips-for-machines/22004)
- VENDOR: Railway offers static outbound IPv4 on the Pro plan ($20/month per Railway's support bot) and not on Hobby; a Railway community post says the IP "may be shared with other customers". — [Railway docs: static outbound IPs (search snippet)](https://docs.railway.com/networking/static-outbound-ips); [Railway station thread (search snippet)](https://station.railway.com/feedback/support-dedicated-outbound-static-i-ps-fo-741d24d1)
- VENDOR: Render's default outbound IP ranges "are shared across all services in the same region". Since 19 May 2026, Pro workspaces and above can buy dedicated IP sets at $100/month per set, each set giving three static IPv4 addresses in one region. — [Render docs: outbound IPs (search snippet)](https://render.com/docs/outbound-ip-addresses); [Render changelog (search snippet)](https://render.com/changelog/add-dedicated-outbound-ips-to-your-workspace)
- VENDOR: Cloudflare's dedicated egress (formerly Aegis, now "Dedicated CDN Egress IPs") is for Enterprise customers; Worker `fetch()` calls to the customer's own origin use them, `connect()` calls do not. — [Cloudflare docs (search snippet)](https://developers.cloudflare.com/smart-shield/configuration/dedicated-egress-ips/)
- VENDOR (GitHub docs, read 11 Nov 2026): static IPs exist only on larger runners, and "Larger runners are only available for organizations and enterprises using the GitHub Team or GitHub Enterprise Cloud plans". The limits page gives 10 static IPs for Team and 50 for Enterprise. — [GitHub docs: larger runners](https://docs.github.com/en/actions/using-github-hosted-runners/using-larger-runners/about-larger-runners); [GitHub docs: Actions limits (search snippet)](https://docs.github.com/en/actions/reference/limits)

### Inferences
Comparison (monthly cost; INR at the assumed ₹90/USD; "dedicated" means only the owner egresses from the IP):

| Option | Approx. monthly cost | Dedicated to you? | Setup effort | Main caveat |
|---|---|---|---|---|
| Home broadband static IP + laptop | ₹170–1,000 (BSNL annual plan to private-ISP add-on) | Yes, if truly public | Call the ISP; register the IP | Must be a public IPv4, not CGNAT; laptop must be on that network at 15:10 |
| Small India VPS running the bot itself | $4–6 (₹360–540) | Yes | Low: cron + Python | It is a server, though a tiny one |
| Vercel function + private forward proxy on that VPS | $4–6 (₹360–540) plus Vercel | Yes | Medium: tinyproxy/Squid with auth, or a tunnel | Two moving parts instead of one |
| Oracle Always Free VM | $0 | Yes | Medium | Capacity errors and idle reclamation |
| GCP Cloud Run/Functions + Cloud NAT + reserved IP | roughly $5 (₹450) | Yes | Medium to high | Networking setup; cost estimate is mine |
| Fly.io machine + static egress IP | about $3.60 (₹325) plus machine time | Yes (per app) | Medium | Price from secondary sources |
| Railway Pro static outbound IP | $20 (₹1,800) | Possibly shared | Low | Sharing status unclear |
| QuotaGuard Static Starter/Production/Business | $19–89 (₹1,710–8,010) | **No, shared** | Low | Conflicts with one-client-per-IP |
| QuotaGuard Enterprise (dedicated) | $219 (₹19,710) | Yes | Low | Price |
| Vercel Static IPs (Pro) | $100 (₹9,000) + Pro plan | **No, shared pool** | Lowest | Shared, and expensive |
| Render dedicated IP set | $100 (₹9,000) | Yes | Low | Three IPs, but brokers offer two slots |
| AWS Lambda + NAT Gateway + Elastic IP (Mumbai) | about $40–44 (₹3,600–3,960) | Yes | High | Costly for a few orders a month |
| Vercel Secure Compute, Cloudflare dedicated egress, GitHub larger runners | Enterprise/Team pricing | Varies | High | Not aimed at individuals |

- **Vercel alone cannot satisfy the rule cheaply.** Without the add-on, Vercel egress IPs are dynamic. With the add-on they are static but shared with other Vercel customers, which Vercel itself states. Two IPs per region does fit the broker's two slots, but the sharing problem remains.
- **A Vercel function can still be the brain.** It can compute signals and call Groww's order endpoint through an authenticated HTTPS proxy running on the owner's own VPS, so that Groww sees the VPS's dedicated IP. At that point the VPS could simply run the whole bot from cron, which is simpler; the proxy design only makes sense if the owner wants to keep code and scheduling on Vercel.
- **Scheduling on Vercel needs Pro anyway.** Hobby cron cannot hit 15:10 IST reliably (±59 minutes), so a Vercel-scheduled order at a fixed time implies the Pro plan or an external scheduler such as Supabase's.
- **Laptop on a home static IP:** the router's public address is what Groww sees, so the laptop needs no special setup beyond being on that network. Three checks before registering: (1) confirm the address shown by an external "what is my IP" service equals the ISP-assigned static IP (if not, the line is behind CGNAT); (2) confirm the route to `api.groww.in` uses the registered address family, because a dual-stack line may send traffic over IPv6 from a different address, in which case force IPv4; (3) never place orders while tethered to a phone or on another network. Registering the home IP as primary and a VPS IP as secondary uses both slots for redundancy.
- **GCP estimate:** Cloud NAT at $0.0014/hour is about $1/month, plus a reserved IP at $0.005/hour, about $3.65/month, plus negligible data. This assumes one small instance counts toward the NAT charge and ignores any VPC connector cost, which I did not price.
- **AWS estimate:** $40.32 for the gateway plus about $3.65 for a public IPv4 at $0.005/hour (the IPv4 rate is my recollection of AWS's public pricing, not sourced here). The US$33 figure sometimes quoted is the US-region rate.

### Gaps
- Official price pages for AWS Lightsail (Mumbai), Vultr, DigitalOcean, Linode/Akamai, Hetzner, E2E Networks, Hostinger, Fly.io, Railway and Fixie could not be opened. Linode/Akamai (Mumbai, Chennai), Hetzner (no India region), E2E Networks and Hostinger India VPS have **no sourced price** in these notes.
- Noble IP: no information found.
- Fixie: paid tier prices and whether any plan gives a dedicated IP were not found.
- Whether Vercel Static IPs can be configured specifically in bom1 is not stated on the pages read; bom1 is a function region with Private Data Transfer pricing, which suggests it can.
- Indian ISP prices are all from third-party blogs, with wide disagreement; none is from an ISP's own tariff page, and none is dated precisely. Excitel and Tata Play Fiber were not covered by any source found.
- Oracle Always Free availability in Mumbai/Hyderabad and current ARM capacity there were not confirmed.

## 8. Is routing broker order traffic through a third-party proxy acceptable and safe?

### Takeaway
Verdict: use an IP that only you egress from. A dedicated IP on your own VPS (or a dedicated-IP proxy plan) is consistent with the rules and with what brokers accept; a shared proxy pool (Vercel Static IPs, QuotaGuard's non-Enterprise tiers, Render's default ranges, possibly Railway) is not consistent with NSE's one-client-per-IP rule and is the wrong tool here, even though it would often work technically.

### Cited Findings
- REGULATOR: "A static IP can only be mapped to one client at a time" and, for client-generated algos, "the static IP shall be that of the client". The stated purpose of the key-plus-IP control is "identification and traceability of ... the end user i.e. investor". — [NSE/INVG/67858, Annexure A.5, A.7, I.e](https://nsearchives.nseindia.com/content/circulars/INVG67858.pdf)
- BROKER: Zerodha's users must declare that the IPs "will be used exclusively by me and/or my immediate family"; forum staff say surveillance may suspend API access where unrelated accounts share static IPs. — [Zerodha Support](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/static-ip); [Kite Connect forum (search snippet)](https://kite.trade/forum/discussion/comment/50587/)
- BROKER: Zerodha and Groww both name cloud or VPS providers as legitimate sources of a static IP. — [Zerodha Support](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/static-ip); [Groww Blog](https://groww.in/blog/static-ip-api-trading-setup)
- VENDOR: Vercel on its shared pool: "An IP allowlist confirms where a request came from, but not who sent it" and "other customers' traffic can come from the same addresses". — [Vercel docs: Static IPs](https://vercel.com/docs/networking/static-ips)
- VENDOR: QuotaGuard says its outbound Static proxy is a blind CONNECT tunnel that does not decrypt payloads, that only its Enterprise plan gives a dedicated IP, and that a shared IP may be rejected if another of its customers has registered it with the same broker. — [QuotaGuard pricing (search snippet)](https://www.quotaguard.com/pricing); [QuotaGuard blog (search snippet)](https://quotaguard.com/blog/dhan-api-static-ip)
- USER: a Kite forum user asked "Is placing orders via a proxy IP allowed?" and no staff answer appeared in the results; a staff reply elsewhere notes that with a VPN "your requests will automatically go out through the gateway IP". — [Kite Connect forum (search snippet)](https://kite.trade/forum/discussion/comment/50533)

### Inferences
(a) Regulatory
- The rule does not ban proxies or tunnels as such. What matters is which public IP the broker sees and whether that IP is mapped to one client. A proxy on a VPS the owner rents, with an IPv4 assigned only to that VPS, passes; the owner is the only client behind that IP and can show the hosting invoice if asked.
- A shared pool fails the one-client-per-IP test in principle, and the owner has no way to know who else is behind it. If another Groww API user registers the same address, either registration may be refused or both accounts may be flagged. Because the broker is "fully responsible and liable" for API orders, expect brokers to resolve doubts by suspending API access.

(b) Security (technical reasoning, not from a cited source)
- With an HTTPS `CONNECT` tunnel the TLS session runs end to end between the bot and `api.groww.in`. The proxy sees the destination host, timing and data volume, but not the access token or the order contents.
- The proxy operator can still block, delay or drop requests, so availability depends on it.
- If the client were configured to trust a proxy-supplied certificate (TLS interception), the proxy could read and alter everything. Keep normal certificate verification on and never install a proxy's CA.
- The proxy username and password become a second secret. Anyone holding them can egress from "your" whitelisted IP, though they still cannot place orders without the Groww token.
- On a shared pool, other customers already egress from the whitelisted address, so the IP check adds almost nothing as a security control; all protection rests on the API key, TOTP secret and token.

(c) Reliability and latency
- For one limit order a day at 15:10 IST, an extra hop of tens of milliseconds within India, or a few hundred via a US or EU proxy, does not matter. What matters is that the hop is up at that minute. A self-run proxy on one small VPS is a single point of failure, so register a secondary IP (for example the home line) and alert on failure with time to place the order by hand before 15:30.

(d) Broker terms
- No Groww term addressing proxies or VPNs was found. Groww's only published requirement is that orders originate from the registered static IP.

Overall: a dedicated IP on infrastructure you rent is acceptable with the caveats above; a shared proxy IP is not advisable, on regulatory rather than cryptographic grounds.

### Gaps
- No regulator or broker text explicitly rules on third-party proxies; the verdict is an inference from the one-client-per-IP rule and broker declarations.
- Groww's API terms and conditions (the NSE "Annexure 9" client terms) were not read.

## 9. What stays impossible without a static IP, and what remains possible

### Takeaway
Without a registered static IP, placing, modifying or cancelling orders through the Groww API is not possible; such orders are rejected. Everything short of the order call remains possible: backtests, paper trading, signal generation, notifications, and (by broker practice) reading holdings, positions and data. The clean no-static-IP workflow is "the bot computes and alerts, the owner taps the order in the Groww app".

### Cited Findings
- BROKER: Groww: "Order placement must now come from a static, whitelisted IP ... If your orders come from a dynamic or unregistered IP, they'll be rejected by broker APIs." — [Trading with Groww on X, 31 Mar 2026 (search snippet)](https://x.com/TradeWithGroww_/status/2038996435870621738)
- BROKER: Groww's setup guide ties whitelisting to order placement only ("order placement must originate from a static IP"). — [Groww Blog](https://groww.in/blog/static-ip-api-trading-setup)
- BROKER: Zerodha: the market-data WebSocket "and other APIs, such as orderbook and positions, can continue to be accessed from any IP address". — [Zerodha Support](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/static-ip)
- BROKER: Upstox: holdings, positions, funds and historical candles "are not restricted by Static IP". — [Upstox developer announcement (search snippet)](https://upstox.com/developer/api-documentation/announcements/algo-trading-circular)
- BROKER: Fyers community reply: data can be fetched without a static IP. — [Fyers community (search snippet)](https://fyers.in/community/t/is-a-static-ip-required-for-data-only-applications-historical-market-depth-tbt-under-the-new-sebi-guidelines/22865)
- REGULATOR: manual order entry through the broker's own web or mobile front end is a separate, non-algo channel (IBT "111111111111" and STWT "333333333333", where the front end "captures only manual order entry of all order attributes"), not subject to the client-API static-IP rule. — [NSE/INVG/69255, Annexure I para 2.1](https://nsearchives.nseindia.com/content/circulars/INVG69255.zip)
- BROKER: on Groww's ₹0 tier, live data and historical/backtesting APIs are not available, while orders, positions, holdings and margins are. — [Groww Blog: API Trading on Groww](https://groww.in/blog/api-trading-on-groww)

### Inferences
- **Impossible without a static IP:** API order placement, modification and cancellation on Groww, including Smart Orders (GTT/OCO) created through the API, since those are order-creating calls. Whether Groww checks the IP on Smart Order endpoints specifically is not documented, so assume it does.
- **Possible without a static IP:**
  - Backtests and paper trading (no broker call is involved).
  - Signal generation on Vercel + Supabase from any data source.
  - Notifications such as "sell X, buy Y, place it in the Groww app before 15:20". A human then enters the order in the app, which is a manual order and outside the API rules entirely.
  - Reading holdings, positions, margins and order status through the API from any IP, by the practice Zerodha, Upstox and Fyers state openly and Groww's wording implies. Groww has not said this in so many words, so verify it with one call from a non-whitelisted IP.
  - Manual execution in the Groww app or website.
- **Minimum checklist to place live API orders on Groww in November 2026:** (1) Groww account with a Trading API subscription (₹0 tier suffices for orders, per Groww's blog); (2) API key with the TOTP flow set up, secrets stored safely; (3) a static public IP that only the owner uses, registered as primary at groww.in/trade-api/api-keys, ideally with a secondary; (4) a fresh access token each trading day; (5) limit orders, not market orders; (6) a one-share live test from the registered IP, since data calls do not prove the whitelist works; (7) no IP change more than once per calendar week.
- For a handful of orders a month, the alert-and-tap workflow costs nothing and avoids all of the above. The static IP buys only the removal of that one manual tap.

### Gaps
- Groww has no published statement that read-only API calls are exempt from the IP check; this is inferred from its order-placement wording and from other brokers.
- Whether a human-triggered order sent through the API (for example a button in the owner's own app) counts as an algo order: by NSE FAQ Q8, all orders received via API are treated as algo orders, so it would still need the static IP.
