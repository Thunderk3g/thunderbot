# Free and cheap NSE end-of-day and delayed-quote data sources that work from cloud/serverless hosts (state as of 11 Nov 2026)

Reading guide:
- **"Direct test"** = an HTTP request I made on 11 Nov 2026 at about 22:40 IST (17:10 UTC) from this research sandbox, a cloud container behind an egress proxy. Its public IP, provider and country could not be determined (the IP-lookup host was blocked). One cloud IP on one evening shows an endpoint is not blanket-blocked; it does not show it is reliable. The market was closed, so intraday quote delay was not measured.
- **"(snippet)"** = the fact comes from a search-result extract; the page itself could not be opened because the host is outside this session's network allow-list (twelvedata.com, eodhd.com, upstox.com, dhan.co, help.yahoo.com, support.fyers.in, kotakneo.com, onetradejournal.com, stooq.com, portal.amfiindia.com, bseindia.com, google.com were all unreachable). Treat these as needing a second look.
- This note extends section 4 of `Evidence based NSE trading strategies/mean_reversion_and_backtesting.md` (yfinance defaults, HDFCBANK demerger, dividend mismatches, issue #2621). Those points are not repeated.

## 1. Yahoo Finance from cloud servers in 2025-2026 (v8 chart endpoint, 429s, IP blocking, terms, delay, data quality)

### Takeaway
The v8 chart endpoint still answered unauthenticated from a cloud host on 11 Nov 2026 with nothing but a User-Agent header, and no cookie or crumb. The "429 Too Many Requests" that people report is, in my tests, mostly a client-fingerprint rejection (it fires on the first request for `curl`, `python-requests`, `Deno/x` and a missing User-Agent), not a counted rate limit. Yahoo publishes no limit and gives no assurance of access, its terms prohibit automated collection, and its NIFTYBEES.NS history contains a 10x split error and no dividend adjustment, so it should be a convenience source backed by a cache and an independent check.

### Cited Findings

**Does v8 chart still work without cookies/crumb? (direct tests, 11 Nov 2026)**
- `GET /v8/finance/chart/NIFTYBEES.NS?range=5d&interval=1d` with a Chrome User-Agent and no cookies returned HTTP 200 JSON (`regularMarketPrice` 286.54, exchange `NSI`). `^NSEI` on `query2` also returned 200. — [query1 v8 chart, NIFTYBEES.NS](https://query1.finance.yahoo.com/v8/finance/chart/NIFTYBEES.NS?range=5d&interval=1d)
- The same URL returned **HTTP 429 with body `Edge: Too Many Requests` on the very first request** when the User-Agent was curl's default, `python-requests/2.32`, `Deno/2.1.4`, or absent. It returned 200 for `Mozilla/5.0`, the full Chrome string, `node`, `undici`, `axios/1.7.2` and `okhttp/4.12.0`. — [query1 v8 chart, NIFTYBEES.NS](https://query1.finance.yahoo.com/v8/finance/chart/NIFTYBEES.NS?range=5d&interval=1d)
- The v7 quote endpoint without a crumb returned HTTP 401 `"Unauthorized ... User is unable to access this feature"`. So v7 still needs cookie + crumb; v8 chart does not. — [query1 v7 quote](https://query1.finance.yahoo.com/v7/finance/quote?symbols=NIFTYBEES.NS)
- Twelve sequential v8 calls for 12 different `.NS` ETFs in about 5 seconds all returned 200 (0.15 to 0.85 s each). — [query1 v8 chart, NIFTYBEES.NS](https://query1.finance.yahoo.com/v8/finance/chart/NIFTYBEES.NS?range=1mo&interval=1d)
- `range=max&interval=1d` silently returned **monthly** bars (`dataGranularity: 1mo`, 216 rows). `period1=0&period2=<now>&interval=1d` returned true daily bars (4,411 rows, 454 KB). — [query1 v8 chart, period1/period2 form](https://query1.finance.yahoo.com/v8/finance/chart/NIFTYBEES.NS?period1=0&period2=1794500000&interval=1d&events=div%2Csplits)
- `range=1d&interval=1m` returned 376 one-minute bars covering 09:15 to 15:30 IST, and `meta.regularMarketTime` was 15:30:01 IST. The chart response therefore carries its own timestamp for a staleness check. — [query1 v8 chart, 1m](https://query1.finance.yahoo.com/v8/finance/chart/NIFTYBEES.NS?range=1d&interval=1m)

**The 2025-2026 record of 429s and blocking (user reports unless marked maintainer)**
- 20 Feb 2025, issue #2297 "Edge: Too Many Requests, response code = 429": `yf.download` failed with the crumb request returning `Edge: Too Many Requests`, and the reporter still failed after upgrading to 0.2.54. Maintainer ValueRaider (22 Feb 2025) suggested "Try manually changing user-agent" and closed it as a duplicate of #2284. No maintainer stated a root cause; one user guessed "they have deployed new safeguards against scraping". — [yfinance #2297](https://github.com/ranaroussi/yfinance/issues/2297)
- 30 Apr 2025, issue #2422 "[0.2.57] YFRateLimitError('Too Many Requests')": a user found the request worked in a browser and with curl but returned 429 from Python `requests`, and suspected TLS fingerprinting. The workaround that worked was passing a `curl_cffi` session with `impersonate="chrome"`. Another user said the following release "resolves the rate-limit by implementing curl_cffi". Closed 9 May 2025 (linked PR #2434). One Linux user still failed on 0.2.59. — [yfinance #2422](https://github.com/ranaroussi/yfinance/issues/2422)
- Cloud-specific report in #2422: a user hit the error on **AWS Lambda** (Python 3.13, yfinance 0.2.57) while the same script worked locally. The original reporter said changing IP addresses did not help. — [yfinance #2422](https://github.com/ranaroussi/yfinance/issues/2422)
- Issue #2480 reports the error persisting across 0.2.57, 0.2.58 and 0.2.59 (snippet). — [yfinance #2480](https://github.com/ranaroussi/yfinance/issues/2480)
- Discussion #2431 (opened 1 May 2025, answered 21 Jan 2026):
  - One user measured "about 100 requests", then a 30-second wait, before later being unable to make any requests.
  - One user was blocked for over 24 hours; another (21 Jan 2026) was rate-limited on the first request with yfinance 1.0 and 0.2.66, and it cleared "after another hour".
  - Maintainer ValueRaider on a VPN user: "Sounds like Yahoo blocking your VPN." His advice on 21 Jan 2026: "Stop spamming Yahoo, fetch smarter", pointing to the yfinance-cache project.
  — [yfinance discussion #2431](https://github.com/ranaroussi/yfinance/discussions/2431)
- Hosted-platform anecdotes (snippets, not opened): a Reddit r/CodingHelp post about a model that "works locally but fails on" Streamlit Cloud/Render, and PythonAnywhere forum threads about yfinance calls failing there. — [Reddit mirror](https://redlib.hyperreal.coffee/r/CodingHelp/comments/1ki88le/financial_model_works_locally_but_fails_on); [PythonAnywhere forum](https://www.pythonanywhere.com/forums/topic/35201/)

**Terms of use**
- Yahoo's Terms of Service prohibit collecting data through "robots, spiders, scrapers, data mining tools" and accessing services "through automated means ... without our permission" (snippet of the Ireland and international versions; the current US text was not retrieved). — [Yahoo ToS, IE previous version 9 Jun 2025](https://legal.yahoo.com/ie/en/yahoo/terms/otos/previousversion-2025-06-09/index.html); [Yahoo ToS, international](https://legal.yahoo.com/xw/en/yahoo/terms/otos/index.html)
- yfinance's own notice: it is "not affiliated, endorsed, or vetted by Yahoo", uses Yahoo's publicly available APIs, and is "intended for research and educational purposes"; users are pointed to Yahoo's terms for their rights to the downloaded data (snippet). — [yfinance README](https://cdn.jsdelivr.net/gh/ranaroussi/yfinance@main/README.md)

**Quote delay for `.NS`**
- Yahoo's exchange table lists "India | National Stock Exchange of India | .NS | Real-time | ICE Data Services", and Bombay Stock Exchange `.BO` at 15 minutes (snippet). — [Yahoo help SLN2310](https://help.yahoo.com/kb/finance/SLN2310.html)
- The Singapore edition of the same page marks NSE "Real-time**" with the footnote that NSE quotes are real-time "for all users who have signed in" (snippet). — [Yahoo help SG SLN2310](https://sg.help.yahoo.com/kb/SLN2310.html)

**Data quality found in the direct pull (extends the earlier note)**
- History depth: NIFTYBEES.NS and GOLDBEES.NS daily bars start 2 Jan 2009 (`firstTradeDate` 1 Jan 2009); `^NSEI` starts 17 Sep 2007 (4,729 rows). NSE's ETF list gives NIFTYBEES's listing date as 8 Jan 2002, so Yahoo is missing its first seven years. — [query1 v8 chart, period1/period2 form](https://query1.finance.yahoo.com/v8/finance/chart/NIFTYBEES.NS?period1=0&period2=1794500000&interval=1d&events=div%2Csplits); [NSE eq_etfseclist.csv](https://nsearchives.nseindia.com/content/equities/eq_etfseclist.csv)
- **Split error:** NIFTYBEES.NS closes read 129.25 (18 Dec 2019), **13.02 (19 Dec), 13.03 (20 Dec)**, 129.93 (23 Dec). NSE records a face-value split from Rs 10 to Rs 1 with ex-date 19 Dec 2019. Yahoo returned an empty `splits` list for the ticker. — [query1 v8 chart, period1/period2 form](https://query1.finance.yahoo.com/v8/finance/chart/NIFTYBEES.NS?period1=0&period2=1794500000&interval=1d&events=div%2Csplits); [NSE corporate actions API, NIFTYBEES](https://www.nseindia.com/api/corporates-corporateActions?index=equities&symbol=NIFTYBEES)
- **No dividend adjustment:** `adjclose` equals `close` on every one of the 4,411 rows and zero dividend events were returned, while NSE lists NIFTYBEES dividends of Rs 8 (ex 18 Feb 2015), Rs 7 (10 Mar 2014), Rs 7.5 (13 Mar 2013) and one on 9 Mar 2012. — same two sources as above
- Other defects in NIFTYBEES.NS: 10 null closes (most recent 24 Oct 2025), 185 zero or missing volume days (165 of them in 2012-2013), and a one-day print of 52.50 on 6 Oct 2010 between 62.10 and 61.62. `^NSEI` has 31 null closes and 1,365 zero-volume rows. — [query1 v8 chart, period1/period2 form](https://query1.finance.yahoo.com/v8/finance/chart/NIFTYBEES.NS?period1=0&period2=1794500000&interval=1d&events=div%2Csplits)

### Inferences
- A **Supabase Edge Function (Deno) will get 429 from Yahoo on its first call unless it sets a User-Agent explicitly**, because the default `Deno/x` string was rejected. Node's default (`node`/`undici`) passed, so a Vercel Node function may work by accident. Set a browser User-Agent everywhere rather than rely on that.
- The Feb to May 2025 "rate limit" wave was largely fingerprint-based rejection (User-Agent, then TLS), which is why yfinance moved to `curl_cffi` impersonation. A raw `fetch` to v8 with a browser User-Agent is a simpler dependency than yfinance for a serverless function, but it lacks the TLS impersonation and could be the first thing to break if Yahoo tightens again.
- The bot's own volume (about 11 symbols, a few calls per day) is far below the roughly 100-requests-per-burst pattern users describe. The realistic risk is not the bot's own rate; it is a shared datacenter IP that other tenants have already burned, which the bot cannot control. Hence the need for a fallback that does not depend on Yahoo.
- Always request with `period1`/`period2`, never `range=max`, or the backtest silently runs on monthly bars.
- For signal purposes the 19-20 Dec 2019 error is fatal if unpatched (a false -90% and +900% move). Any Yahoo backfill must be reconciled against NSE bhavcopy before use.

### Gaps
- Intraday delay of the unauthenticated v8 endpoint for `.NS` during market hours was not measured (market closed at test time). Yahoo's help page says real-time, possibly only for signed-in users. To settle it, log `meta.regularMarketTime` against wall-clock time at 15:10 IST for a week.
- No official Yahoo statement of a per-IP limit, and no confirmed report that AWS, GCP, Azure, Vercel or GitHub Actions ranges are blocked wholesale. The evidence is one Lambda report plus hosted-platform anecdotes.
- No 2026-dated GitHub issue specific to GitHub Actions or Vercel was found.
- The current US Yahoo Terms of Service text was not retrieved.
- The yfinance release that first shipped `curl_cffi` by default was not confirmed from the changelog (the brief says 0.2.54+; issue #2422 suggests it landed after 0.2.57).

## 2. NSE's own files: bhavcopy (UDiFF), sec_bhavdata_full, index close file, publication times, cloud access, adjustment, terms, libraries

### Takeaway
The static files on `nsearchives.nseindia.com` downloaded from a cloud host on 11 Nov 2026 with a browser-like User-Agent and no cookies, and the day's UDiFF bhavcopy was already timestamped 16:33 IST. They are unadjusted, include ETFs in series EQ, and one 200 KB zip covers every listed security. `www.nseindia.com` is a different matter: the homepage and the quote API returned Akamai 403s, and NSE's terms prohibit automated collection.

### Cited Findings

**Files, formats and what is in them (direct tests, 11 Nov 2026)**
- New UDiFF CM bhavcopy `BhavCopy_NSE_CM_0_0_0_YYYYMMDD_F_0000.csv.zip`: HTTP 200, 212 KB, 3,775 rows for 11 Nov 2026. Columns include `TradDt, ISIN, TckrSymb, SctySrs, OpnPric, HghPric, LwPric, ClsPric, LastPric, PrvsClsgPric, TtlTradgVol, TtlTrfVal`. — [UDiFF bhavcopy 11 Nov 2026](https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_20261111_F_0000.csv.zip)
- **ETFs are in the CM bhavcopy as series EQ**: NIFTYBEES (ISIN INF204KB14I2, close 286.54), GOLDBEES and JUNIORBEES all appear with `SctySrs = EQ`. — [UDiFF bhavcopy 11 Nov 2026](https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_20261111_F_0000.csv.zip)
- `sec_bhavdata_full_DDMMYYYY.csv` (plain CSV with delivery quantity): HTTP 200, 407 KB, and available back to at least 1 Jan 2020. — [sec_bhavdata_full 11 Nov 2026](https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_11112026.csv)
- `ind_close_all_DDMMYYYY.csv`: HTTP 200, about 147 index rows with open, high, low, close, P/E, P/B and dividend yield (Nifty 50 close 25,255.05, P/E 20.59, yield 1.35% on 11 Nov 2026). It is a price-index file, not total return. Available back to at least 1 Jan 2015. — [ind_close_all 11 Nov 2026](https://nsearchives.nseindia.com/content/indices/ind_close_all_11112026.csv)
- History reach of each URL pattern: UDiFF exists for 8 Jul 2024 but returned 404 for 2 Jan 2023. The old `cm<DD><MON><YYYY>bhav.csv.zip` returned 200 for 1 Jan 2020 and 404 for 11 Nov 2026. A long backfill therefore needs both patterns (or `sec_bhavdata_full`). — [UDiFF 8 Jul 2024](https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_20240708_F_0000.csv.zip); [old format 1 Jan 2020](https://nsearchives.nseindia.com/content/historical/EQUITIES/2020/JAN/cm01JAN2020bhav.csv.zip)
- The UDiFF cutover date was Monday 8 Jul 2024: BSE's UDiFF page says the old trade and bhavcopy files "shall be discontinued from Monday 08th July 2024", and a TradingQnA post from that date gives the new NSE URL (snippets). — [BSE UDiFF page](https://bseindia.com/static/members/udiff.aspx); [TradingQnA](https://tradingqna.com/t/has-nse-changed-bhavcopy-location/169551)

**Publication time (from `Last-Modified` headers, direct tests)**
- UDiFF bhavcopy: 16:45 IST on 9 Nov 2026 and 16:33 IST on 11 Nov 2026 (11:15 and 11:03 GMT). — [UDiFF bhavcopy 9 Nov 2026](https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_20261109_F_0000.csv.zip)
- `ind_close_all`: 23:20 IST on 9 Nov and 19:55 IST on 11 Nov. — [ind_close_all 9 Nov 2026](https://nsearchives.nseindia.com/content/indices/ind_close_all_09112026.csv)
- `sec_bhavdata_full`: 23:55 IST on 9 Nov and 22:25 IST on 11 Nov. — [sec_bhavdata_full 9 Nov 2026](https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_09112026.csv)
- NSE itself describes "the bhavcopy report uploaded on the website immediately after market close" (circular dated 18 Jun 2026). — [NSE/MSD/74764](https://nsearchives.nseindia.com/content/circulars/MSD74764.pdf)
- **Holiday trap:** for 10 Nov 2026 the UDiFF file returned 404, but `sec_bhavdata_full_10112026.csv` returned 200 with the 9 Nov rows inside (`DATE1 = 09-Nov-2026`). — [sec_bhavdata_full 10 Nov 2026](https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_10112026.csv)

**Cloud access and blocking**
- `nsearchives` filters on User-Agent, not (in this test) on IP: `Mozilla/5.0`, `node` and `undici` returned 200; `python-requests`, `Deno/2.1.4`, `axios`, `okhttp` and no User-Agent had the HTTP/2 stream reset with no response. — [ind_close_all 11 Nov 2026](https://nsearchives.nseindia.com/content/indices/ind_close_all_11112026.csv)
- `www.nseindia.com` from the same host: the homepage and `/api/quote-equity?symbol=NIFTYBEES` returned Akamai "Access Denied" 403 (with and without a cookie warm-up attempt, which itself got 403). — [NSE quote API](https://www.nseindia.com/api/quote-equity?symbol=NIFTYBEES)
- Yet several JSON endpoints on the same host returned 200 with no cookies: `/api/etf` (all ETFs with last price, volume and NAV; NIFTYBEES `ltP` 286.75), `/api/allIndices`, `/api/marketStatus`, `/api/corporates-corporateActions`, and `/api/historicalOR/generateSecurityWiseHistoricalData`. `/api/historical/cm/equity` returned an HTML page instead of data. — [NSE ETF API](https://www.nseindia.com/api/etf); [NSE allIndices API](https://www.nseindia.com/api/allIndices)
- User reports of datacenter blocking (older, undated in the extracts): the nsepython maintainer says the library "does not work with AWS, Google Cloud and web servers" and that Indian servers are needed; a Kite forum reply says "AWS IP range is blocked by NSE"; users report timeouts on AWS Lambda (snippets). — [Unofficed forum](https://forum.unofficed.com/t/update-nsepython-not-working-in-aws-google-cloud-and-webservers/670); [Kite forum](https://kite.trade/forum/discussion/comment/49373)
- A third-party package claims `nsearchives.nseindia.com` has "no Cloudflare, works from any IP" and documents AWS Lambda use (snippet; the PyPI page could not be opened). — [nse-archives on PyPI](https://pypi.org/project/nse-archives/)

**Unadjusted prices and where corporate actions come from**
- Bhavcopy carries raw traded prices with a `PrvsClsgPric` column and no adjustment factor. — [UDiFF bhavcopy 11 Nov 2026](https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_20261111_F_0000.csv.zip)
- NSE's corporate-actions JSON returned 200 from the cloud host for a single symbol (NIFTYBEES: the 19 Dec 2019 split and 2012-2015 dividends, as free-text `subject` strings) and for a date range across all equities. — [NSE corporate actions API](https://www.nseindia.com/api/corporates-corporateActions?index=equities&symbol=NIFTYBEES)
- `eq_etfseclist.csv` lists every ETF with symbol, underlying, listing date, ISIN and face value. — [NSE eq_etfseclist.csv](https://nsearchives.nseindia.com/content/equities/eq_etfseclist.csv)

**Terms and 2026 circulars**
- NSE's Terms of Use: the user "is prohibited to conduct any systematic or automated data collection activities (including scraping, data mining, data extraction and data harvesting) on or in relation to our Website / Mobile Application" (snippet). — [NSE Terms of Use](https://www.nseindia.com/nse-terms-of-use)
- `www.nseindia.com/robots.txt` currently reads `User-agent: * / Allow: / / Disallow: /market-data-test` (direct test). This contradicts the nsepython maintainer's older claim that robots.txt blocks all web servers. — [NSE robots.txt](https://www.nseindia.com/robots.txt)
- NSE has a separate Data Sharing & Usage Policy governing redistribution of market data (snippet; clauses not read). — [NSE Data Sharing & Usage Policy](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/NSE_Data_Sharing%26Usage_Policy.pdf)
- 2026 "Streamlining EOD information dissemination related to Bhavcopy" circulars (18 Jun, 14 Oct and 30 Oct 2026) concern **member** channels: the `.DAT` bhavcopy moving to the Extranet, closing prices broadcast over trading APIs, and Extranet `.md/.ms` bhavcopy reports being discontinued on 9 Jan 2027 (revised from 7 Dec 2026). They do not mention the public UDiFF CSV, which was still being published on 11 Nov 2026. — [NSE/MSD/74764](https://nsearchives.nseindia.com/content/circulars/MSD74764.pdf); [NSE/MSD/76877](https://nsearchives.nseindia.com/content/circulars/MSD76877.pdf); [NSE/MSD/77208](https://nsearchives.nseindia.com/content/circulars/MSD77208.pdf)

### Inferences
- The UDiFF bhavcopy is the best free **authoritative** daily source for this bot: one request per day returns all 10 ETFs and any 100 stocks, keyed by ISIN, by about 16:45 IST. It cannot serve the 15:10 IST price, since the day's file does not exist yet.
- Prefer UDiFF over `sec_bhavdata_full` for the daily job. It is published five to seven hours earlier and returns 404 on holidays instead of a stale copy. If `sec_bhavdata_full` is used, compare the `DATE1` column with the requested date.
- For ETFs the adjustment burden is small: unit splits are rare and current growth-option ETFs pay no dividends, so a hand-maintained table of split dates (seeded from the corporate-actions API) is enough. For 100 stocks it is real work (bonuses, splits, demergers, rights), which is the case for paying a vendor or broker that adjusts.
- A long backfill from bhavcopy means roughly 250 files per year, about 5,000 requests for 20 years. That is a one-time job to run slowly from a laptop, not from a serverless function.
- The unofficial `www.nseindia.com/api/etf` endpoint is a possible free last-resort live quote for ETFs, but it sits behind Akamai, has no stability promise, and automated use conflicts with NSE's terms.
- The public-file change risk is real: NSE reorganised bhavcopy channels three times in 2026. Watch for a 404 on the UDiFF URL and alert rather than fail silently.

### Gaps
- Whether `nsearchives` blocks specific cloud ranges (AWS Mumbai vs US regions, GitHub Actions/Azure, Vercel) was not tested beyond this one host. The "works from any IP" claim is a package author's, unverified.
- `Last-Modified` shows the last write, which may be a re-upload; first-publication times could be earlier than listed, and two days is a small sample.
- Current working status of jugaad-data, nsepython and nselib in 2026 was not established; no 2026-dated issue was found. The earlier note's caution stands (they wrap `www.nseindia.com` endpoints that change and block).
- The NSE circular that formally retired the old `cm...bhav.csv.zip` file was not found.
- Whether personal, non-redistributed downloading of the public bhavcopy files is expressly permitted was not confirmed; only the general prohibition on automated collection was seen.

## 3. NSE index history and Total Return Index (niftyindices.com); BSE equivalents

### Takeaway
The widely copied niftyindices.com `Backpage.aspx` POST endpoints for price and total-return history did not work from the cloud host on 11 Nov 2026 (302 redirect to a login page). Price-index closes are reliably available from `ind_close_all`, but no cloud-friendly free TRI source was confirmed.

### Cited Findings
- Direct test: `POST https://www.niftyindices.com/Backpage.aspx/getHistoricaldatatabletoString` with the usual `cinfo` JSON body, JSON content type and the `reports/historical-data` Referer returned **HTTP 302 to `/Sitefinity/Login?ReturnUrl=...`** with body `{"Message":"There was an error processing the request."}`. `getTotalReturnIndexString` behaved identically. Loading the historical-data page first (HTTP 200) and replaying its cookies did not change the result. — [niftyindices historical data page](https://www.niftyindices.com/reports/historical-data)
- Community reports of the same endpoints failing: nsepython's `index_history` raising `KeyError: 'd'` (blank response), a server-side "Object reference not set to an instance of an object" error from `getHistoricaldatatabletoString`, and a note that it worked from Google Colab but not from the user's machine (snippet, dates not shown). — [Unofficed forum](https://forum.unofficed.com/t/index-history-is-not-working/1363)
- Nifty 50 price-index daily OHLC is in NSE's `ind_close_all` file, available from the cloud host and back to at least 2015. — [ind_close_all 1 Jan 2015](https://nsearchives.nseindia.com/content/indices/ind_close_all_01012015.csv)
- NSE's `/api/allIndices` returned 200 from the cloud host with the Nifty 50 last value (25,255.05, timestamp 11 Nov 2026 15:30). — [NSE allIndices API](https://www.nseindia.com/api/allIndices)
- niftyindices.com has its own Terms of Use, separate from NSE's (snippet; not read). — [niftyindices Terms of Use](https://niftyindices.com/terms-of-use)
- BSE publishes UDiFF-format bhavcopy files as well (snippet); the BSE download host was not reachable from this session. — [BSE UDiFF page](https://bseindia.com/static/members/udiff.aspx)

### Inferences
- Do not make the bot depend on niftyindices.com at run time. If a Nifty 50 TRI benchmark is needed for backtest reporting, download it manually once from the website in a browser and store it in Postgres.
- A practical TRI proxy that is cloud-friendly: the NAV history of a direct-plan growth Nifty 50 index fund from mfapi.in (section 9), which reinvests dividends and trails the TRI by its expense ratio and tracking difference.
- For signals (as opposed to benchmarking), the price index from `ind_close_all` or Yahoo `^NSEI` is sufficient.

### Gaps
- Whether the niftyindices failure is IP-based, a changed request contract, or a site change is unknown. It was one test from one host.
- BSE bhavcopy and index-history URLs could not be tested (host blocked in this session).
- No source was found for a free machine-readable Nifty 50 TRI series other than niftyindices.com.

## 4. Stooq

### Takeaway
Stooq stopped being a keyless source in March 2026: CSV downloads now need an API key obtained on the site, which breaks `pandas-datareader`. Its coverage of Indian instruments could not be confirmed, so it is not a candidate for this bot.

### Cited Findings
- pandas-datareader issue #1012 (opened 13 Apr 2026, still open): "as of March 2026" Stooq "requires an API key for data downloads"; `DataReader(..., 'stooq', ...)` now raises `ParserError` because Stooq returns an HTML page with instructions instead of CSV. The key is requested at `https://stooq.com/q/d/?s=spy.us&get_apikey`. — [pandas-datareader #1012](https://github.com/pydata/pandas-datareader/issues/1012)
- The CSV endpoint form is `https://stooq.com/q/d/l/?s=<symbol>&i=d`. — [pandas-datareader #1012](https://github.com/pydata/pandas-datareader/issues/1012)
- A third-party guide says the key is obtained through a CAPTCHA on the site and that a daily quota applies, with an "Exceeded the daily hits limit" message when passed (snippet, vendor blog). — [QVeris guide](https://qveris.ai/guides/free-stock-api-without-key)

### Inferences
- A CAPTCHA-gated key with an unpublished daily quota is a poor fit for an unattended serverless job, even if the Nifty index is carried.

### Gaps
- Whether Stooq carries `^NSEI` or any individual NSE stocks or ETFs was not confirmed. A search found nothing, and stooq.com was unreachable from this session.
- The exact `apikey` URL parameter and the daily hit limit were not found in a primary source.

## 5. Twelve Data

### Takeaway
Twelve Data lists NSE and BSE instruments, but the available evidence says the free Basic plan covers US equities, forex and crypto only and that Indian data needs a paid tier. The plan name and price could not be confirmed because twelvedata.com was unreachable from this session.

### Cited Findings
- Free Basic plan: 8 API calls per minute and 800 per day, covering US equities, forex and crypto (third-party listing, snippet). — [NexusFi listing](https://nexusfi.com/d/data-providers/twelve-data)
- A conflicting third-party page dated May 2026 gives a daily request limit of 250 (snippet). — [apispine](https://apispine.com/twelve-data)
- Twelve Data's support site describes a paid tier as the one that unlocks "all markets, including complete data coverage for India" (snippet). — [Twelve Data support, trial article](https://support.twelvedata.com/en/articles/5335783-trial)
- Twelve Data has an "Indian exchanges overview" support article that lists NSE as real-time (snippet). — [Twelve Data support, Indian exchanges](https://support.twelvedata.com/en/articles/5768291-indian-exchanges-overview)
- Twelve Data's site has quote pages for NSE and BSE stocks and lists Nifty 50 under indices (snippet). — [Twelve Data indices](https://twelvedata.com/indices)

### Inferences
- Without a free NSE tier, Twelve Data competes with EODHD and the broker APIs on price, and nothing found suggests it is cheaper than either for India.

### Gaps
- Which plan first includes NSE, its monthly price, whether NSE data on that plan is real-time, delayed or EOD, and whether closes are split- and dividend-adjusted. Check twelvedata.com/pricing directly.
- The free plan's true daily credit limit (800 vs 250 in conflicting third-party pages).

## 6. EODHD (EOD Historical Data)

### Takeaway
EODHD is the most credible paid EOD vendor found for NSE: a USD 19.99 per month plan with long global history, an `.NSE` exchange code, splits and dividends, and a documented way to list delisted tickers. The free tier (20 calls per day, one year of history) is only enough to evaluate it. Indian data quality and delisted completeness were not verified.

### Cited Findings
- Free plan: "20 API calls per day; 1 year of history for end-of-day prices, splits and dividends; limited features" (snippet). — [EODHD plans help](https://eodhd.com/help/plans)
- "EOD Historical Data — All World": USD 19.99 per month or USD 199 per year, 100,000 API calls per day (snippet). — [EODHD pricing](https://eodhd.com/pricing)
- The help page says the All World plan includes delisted tickers; delisted data is also a listed feature on the pricing comparison (snippet). — [EODHD plans help](https://eodhd.com/help/plans)
- NSE instruments use the `.NSE` suffix and are quoted in INR, including ETFs (for example `NV20IETF.NSE`, `TNIDETF.NSE`) and stocks (`TCS.NSE`) (snippets). — [EODHD NV20IETF.NSE](https://eodhd.com/financial-summary/NV20IETF.NSE); [EODHD TCS.NSE](https://eodhd.com/financial-summary/TCS.NSE)
- Delisted names per exchange can be listed by adding `delisted=1` to the exchange-symbol-list endpoint (snippet). — [EODHD exchanges API](https://eodhd.com/financial-apis/exchanges-api-list-of-tickers-and-trading-hours)
- Third-party description of the USD 19.99 tier: global coverage of 60+ exchanges and 30+ years for major markets (snippet). — [FitGap listing](https://us.fitgap.com/products/eodhd-financial-data-apis)

### Inferences
- As an API-key service with no IP fingerprinting issue, EODHD is cloud-neutral: it should behave the same on Vercel, Supabase or GitHub Actions. That makes it the simplest paid fallback for EOD.
- At about USD 20 per month (roughly Rs 1,700 to 1,800) it costs three times a broker data subscription. It earns that only if the 100-stock, survivorship-aware backtest is actually built. For 10 ETFs plus the Nifty it is overkill.
- A cheap route: subscribe for one month, download full history including delisted names into Postgres, then cancel and maintain forward from bhavcopy. Check the licence terms before doing this.

### Gaps
- History depth for NSE specifically, how complete the NSE delisted set is, and the accuracy of Indian split, bonus and demerger adjustments. No independent review was found.
- Whether the USD 19.99 plan includes any delayed live quotes for NSE (that appears to be a separate, dearer plan; not confirmed).
- Personal vs commercial licence terms were not read.

## 7. Other vendors and hacks (Alpha Vantage, FMP, Marketstack, Tiingo, Polygon, Finnhub, Google Finance/Sheets, investing.com, Moneycontrol/Tickertape)

### Takeaway
None of these was confirmed as a usable free NSE source. The evidence found is thin and mostly from comparison blogs, so this group should be treated as "not shown to work" rather than "shown not to work".

### Cited Findings
- Alpha Vantage free tier: 25 requests per day and 5 per minute, delayed data (comparison-blog snippet). — [QVeris comparison](https://qveris.ai/guides/stock-api-free-comparison/)
- Alpha Vantage's non-US coverage is described as "very patchy" by one comparison, and a forum comment says it discontinued real-time intraday for NSE and BSE (snippets, unverified). — [multiples.vc comparison](https://multiples.vc/compare/alpha-vantage-api-alternatives); [Marketcalls](https://www.marketcalls.in/database/alphavantage-alternative-yahoo-finance-finance-api.html)
- Financial Modeling Prep free tier: 250 requests per day, limited EOD, non-commercial only (comparison-blog snippet). No statement on `.NS` coverage was found. — [QVeris comparison](https://qveris.ai/guides/stock-api-free-comparison/)
- Marketstack free tier: 100 requests per month, EOD data, one year of history (vendor-affiliated blog snippet). No confirmation that XNSE is on the free plan. — [APILayer blog](https://blog.apilayer.com/analyzing-the-top-free-apis-for-stock-data/)
- Finnhub free tier: 60 calls per minute with limited real-time quotes (comparison-blog snippet). No India coverage detail found. — [QVeris comparison](https://qveris.ai/guides/stock-api-free-comparison/)
- Google's finance data disclaimer lists NSE as "Realtime", while several third-party guides say `GOOGLEFINANCE` prices for NSE are delayed by up to 20 minutes; Sheets exposes a `datadelay` attribute to check (snippets). — [Google Finance disclaimer](https://www.google.com/googlefinance/disclaimer?hl=en); [Sheetaki guide](https://sheetaki.com/get-nse-and-bse-real-time-prices-google-sheets/)
- NSE sells licensed 15-minute delayed and real-time feeds to vendors through NSE Data & Analytics, with a published tariff (snippet). — [NSE real-time data subscription](https://www.nseindia.com/market-data/real-time-data-subscription)

### Inferences
- `GOOGLEFINANCE("NSE:NIFTYBEES")` in a published Google Sheet read as CSV is a workable zero-cost third fallback for a last price, since Google's servers do the fetching and cloud IP blocking does not apply. It is undocumented, has no uptime promise, and Google's terms restrict use of the data outside Sheets.
- With 25 requests per day, Alpha Vantage could not cover 11 symbols twice a day even if its NSE coverage were good.

### Gaps
- Tiingo and Polygon India coverage: nothing found either way (the brief's assumption that neither covers NSE is unconfirmed here).
- Alpha Vantage `.BSE` symbol support and whether NSE symbols exist; FMP and Marketstack NSE coverage on free plans; Finnhub's India plan and price.
- investing.com, Moneycontrol and Tickertape unofficial endpoints and their terms were not researched.

## 8. Broker data APIs for Indian retail: cost, history depth, login, serverless fit, and the April 2026 static-IP rule

### Takeaway
The static-IP requirement that took effect on 1 April 2026 applies to API order placement, not market data: Zerodha says so on its support page, and Fyers and Kotak Neo say the same in snippets. For a serverless data source the standout is Upstox's free Analytics Token (read-only, one-year validity, covers quotes and historical records). Groww (Rs 499 per month plus GST) and Zerodha Connect (Rs 500 per month) bundle live and historical data but need a daily token refresh, which TOTP-based login can automate.

### Cited Findings

**Static-IP rule and market data**
- Zerodha (official support page): "effective 1 April 2026, you must have a static IP for API-based order placement"; the WebSocket stream and other APIs such as orderbook and positions "can continue to be accessed from any IP address". Up to two IPs can be registered, and exchange rules allow one modification per calendar week. The page does not name historical data explicitly and cites no circular number. — [Zerodha support, static IP](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/static-ip)
- Fyers community reply: "you can fetch the data without static IP address" (snippet). — [Fyers community](https://fyers.in/community/t/sebis-new-algo-trading-rules-kick-in-on-april-1-here-is-what-changes-for-you/12267)
- Kotak Neo: Report APIs, Portfolio APIs, Data APIs and WebSocket streams continue to work regardless of IP (snippet). — [Kotak Neo static IP page](https://www.kotakneo.com/platform/kotak-neo-trade-api/static-ip-details/)
- Upstox: a registered static IP and algo registration are required for API trading (official community post, snippet). Separately, for the Analytics Token, "account-specific APIs require Static IP to be enabled" (snippet). — [Upstox community announcement](https://community.upstox.com/t/important-update-regulatory-changes-for-api-and-algo-trading-are-now-live/14874); [Upstox Analytics Token announcement](https://upstox.com/developer/api-documentation/announcements/analytics-token)
- Groww: static IPs are added under the API Keys section (primary plus optional secondary); a third-party comparison lists Groww's IP requirement against order placement (snippets). — [Groww blog, static IP setup](https://groww.in/blog/static-ip-api-trading-setup)

**Groww Trade API**
- Price: Rs 499 per month plus taxes for all trading APIs including live and historical data; the annual plan is Rs 4,999 (about Rs 417 per month) plus taxes. A Rs 0 free trial exists but excludes live quotes, LTP, OHLC and historical candles (snippets). — [Groww pricing](https://915.groww.in/pricing); [Groww blog, API trading](https://groww.in/blog/api-trading-on-groww)
- Historical candles (official docs, fetched): daily (1,440-minute) candles have "Full history" with a maximum of 1,080 days per request; weekly has full history with no per-request limit; intraday intervals reach back only 3 months. — [Groww historical data docs](https://groww.in/trade-api/docs/curl/historical-data)
- That `/v1/historical/candle/range` endpoint is marked deprecated ("will NOT work in the future"); the replacement is "Get Historical Candle Data" in the Backtesting section. The page does not say whether prices are adjusted. — [Groww historical data docs](https://groww.in/trade-api/docs/curl/historical-data); [Groww backtesting docs](https://groww.in/trade-api/docs/curl/backtesting)
- Login: an access token generated on the dashboard expires daily at 06:00 IST; alternatively an API key plus TOTP secret (no expiry on the key) lets code mint a token with `GrowwAPI.get_access_token(api_key, totp)` (snippet of official docs). — [Groww Python SDK docs](https://groww.in/trade-api/docs/python-sdk)

**Zerodha Kite Connect**
- Personal plan (free): orders, GTT, alerts, margins and portfolio, with "no historical or real-time data included". Connect plan: Rs 500 per month per API key, adding live WebSocket data and historical candles at no extra cost (snippets of official help pages). — [Zerodha support, Kite API charges](https://support.zerodha.com/category/trading-and-markets/kite-web-and-mobile/kite-api/articles/what-are-the-charges-for-kite-apis)
- The Rs 2,000 to Rs 500 price cut for the data (real-time plus historical) APIs took effect on 6 May 2025 (official forum post, snippet). — [Kite forum announcement](https://kite.trade/forum/discussion/15015/revising-kite-connect-fees-from-2000-to-500-per-month)
- As of Nov 2026, paid users who generate Rs 500 or more of brokerage in a calendar month receive 500 Developer Credits that can renew the subscription for the next month (snippet of official help page). — [Zerodha support, Kite API charges](https://support.zerodha.com/category/trading-and-markets/kite-web-and-mobile/kite-api/articles/what-are-the-charges-for-kite-apis)

**Upstox**
- "Our APIs and websockets are free"; Historical Candle Data V3 is available on all plans, while expired-instrument endpoints need the Plus plan (snippets). — [Upstox community, API pricing](https://community.upstox.com/t/developer-api-pricing/3796); [Upstox backtesting docs](https://upstox.com/developer/api-documentation/backtesting)
- Historical Candle Data V3: daily data from January 2000, intraday from January 2022 (official docs, snippet). One user got nothing before January 2008 for a BSE stock. — [Upstox historical candle V3 docs](https://upstox.com/developer/api-documentation/v3/get-historical-candle-data); [Upstox community](https://community.upstox.com/t/historical-data-older-than-jan-1-2008/11822)
- Standard access tokens expire daily at 03:30 IST (community moderator, snippet). — [Upstox community, token](https://community.upstox.com/t/upstox-api-access-token/8942)
- **Analytics Token**: a long-lived, read-only token with one-year validity, GET endpoints only, covering full market quotes, OHLC quotes V3 and "historical records"; it cannot place, modify or cancel orders; one token per account, and generating a new one revokes the old (official announcement, snippet). — [Upstox Analytics Token announcement](https://upstox.com/developer/api-documentation/announcements/analytics-token)

**Dhan**
- Dhan's FAQ: the offer making the Data API free after a set number of trades "has been discontinued"; the Data API costs Rs 499 plus taxes per month (snippet). — [Dhan support FAQ](https://dhan.co/support/platforms/dhanhq-api/is-the-dhanhq-data-api-subscription-free-if-i-execute-a-minimum-number-of-trades-every-month/)
- Dhan's historical-data docs say daily data is available back to a scrip's inception (v1 docs, snippet). — [DhanHQ historical data docs](https://dhanhq.co/docs/v2/historical-data/)

**Angel One SmartAPI, Fyers, ICICI Breeze**
- Angel One: historical data is "completely free of cost", covers NSE, BSE and derivative segments, up to 8,000 candles per request; login uses a TOTP secret, and a forum thread reports TOTP login "sometimes working and sometimes failing" (snippets). — [Angel One SmartAPI article](https://www.angelone.in/news/angel-one-smartapi-the-secret-to-easy-automated-algo-trading); [SmartAPI forum](https://smartapi.angelone.in/smartapi/forum/post/11333)
- Fyers: the Standard plan is free with usage limits; from 16 Oct 2026 the data-API limit is 5 requests per second on Standard and 10 on Prime (official notice, snippet). — [Fyers plans and limits](https://fyers.in/api-docs/v3/getting-started/plans-and-limits/); [Fyers notice board](https://fyers.in/notice-board/changes-to-fyers-api-rate-limits-and-usage)
- ICICI Breeze: free, with 3 years of historical data and 1-second or 1-minute granularity; limits of 100 calls per minute and 5,000 per day (snippets). A TradingQnA user reported incorrect and duplicate historical data and switched to a paid vendor. — [ICICI Direct Breeze article](https://www.icicidirect.com/ilearn/stocks/articles/how-to-download-historical-data-using-breeze-api-python-sdk); [Chittorgarh review](https://www.chittorgarh.com/broker/icicidirect/api-for-algo-trading-review/1/); [TradingQnA](https://tradingqna.com/t/is-icici-breeze-api-stable/150332)

**Adjustment caveat (from the earlier note, still relevant)**
- Zerodha historical candles are adjusted for splits and bonuses only, not dividends. — [Kite forum](https://kite.trade/forum/discussion/comment/21017)

### Inferences

Summary table (cells marked "?" were not confirmed):

| Broker | Data cost | Daily history depth | Login for data | Serverless fit |
|---|---|---|---|---|
| Upstox | Free | From Jan 2000 (documented) | Analytics Token, valid 1 year | Best: one secret, no daily login |
| Groww | Rs 499/month + 18% GST (about Rs 589) | "Full history", 1,080 days per call | Daily token (06:00 IST) or API key + TOTP in code | Good if already paying for order API |
| Zerodha Connect | Rs 500/month (GST treatment unconfirmed) | ? | Daily login with TOTP | Workable; daily token is the friction |
| Dhan | Rs 499/month + taxes | To inception | ? | ? |
| Angel One | Free | ? | TOTP in code | Workable; TOTP flakiness reported |
| Fyers | Free (Standard) | ? | ? | ? |
| ICICI Breeze | Free | 3 years | ? | Weak: short history, quality complaint |
| Shoonya, 5paisa | ? | ? | ? | Not researched |

- The bot can keep fetching prices from a serverless function with a changing IP after April 2026. Only the order-placing call needs to leave from a registered static IP.
- If the bot already places orders through Groww's paid API, Groww's live quote is the natural 15:10 IST primary (same vendor, same token, exchange-sourced). If it does not, the Upstox Analytics Token is the cheapest robust live-price source: free, no daily login, and the account need not be funded or traded.
- Broker daily candles are probably split-adjusted but not dividend-adjusted (confirmed only for Zerodha). For growth ETFs this is acceptable; for stocks it understates total return.

### Gaps
- The SEBI circular number and date behind the static-IP rule were not read in primary form (commonly cited as SEBI's February 2025 retail algo framework; the search tool named NSE circular NSE/INVG/67858, unverified).
- Groww's own statement on whether market-data calls need a whitelisted IP was not found.
- Whether Upstox's Analytics Token explicitly covers the Historical Candle V3 endpoint, and whether Upstox data endpoints are IP-restricted, could not be confirmed (upstox.com unreachable).
- Daily-candle depth for Zerodha, Angel One and Fyers; whether Groww, Upstox and Dhan candles are adjusted; token and login details for Dhan, Fyers and Breeze; everything about Shoonya/Finvasia and 5paisa.
- Whether Zerodha's Rs 500 and Dhan's Rs 499 include GST.

## 9. AMFI NAV history and mfapi.in as an alternative EOD source

### Takeaway
mfapi.in answered from the cloud host with no key and returned the full NAV history of the NIFTYBEES scheme as JSON, so it is a zero-friction independent check on ETF prices. Two limits matter: the NIFTYBEES history starts only in November 2016, and NAVs are unadjusted for the 2019 unit split and arrive a day late.

### Cited Findings (direct tests, 11 Nov 2026)
- `GET https://api.mfapi.in/mf/140084` returned HTTP 200, 100 KB JSON: "Nippon India ETF Nifty 50 BeES - Direct Plan", ISIN INF204KB14I2, 2,471 NAV rows from 7 Nov 2016 to 9 Nov 2026. — [mfapi.in scheme 140084](https://api.mfapi.in/mf/140084)
- The first NAV is 867.7194 (7 Nov 2016) and the latest 285.8134 (9 Nov 2026), so the series is **not adjusted** for the 10-for-1 unit split of Dec 2019. — [mfapi.in scheme 140084](https://api.mfapi.in/mf/140084)
- At 22:40 IST on 11 Nov the latest NAV available was dated 9 Nov (10 Nov had no trading), so the same-day NAV was not yet published. — [mfapi.in latest, scheme 120716](https://api.mfapi.in/mf/120716/latest)
- An index-fund alternative with longer history: "UTI Nifty 50 Index Fund - Direct Plan - Growth" (scheme 120716) has 3,409 NAV rows from 2 Jan 2013. — [mfapi.in scheme 120716](https://api.mfapi.in/mf/120716)
- Search endpoint works: `/mf/search?q=nifty 50 bees` returned scheme codes for Nifty BeES (140084) and Junior BeES (140085). — [mfapi.in search](https://api.mfapi.in/mf/search?q=nifty%2050%20bees)
- NAV vs traded price, one observation: NIFTYBEES NAV was 285.8134 against an NSE close of 285.01 on 9 Nov 2026, a gap of about 0.28%. — [mfapi.in scheme 140084](https://api.mfapi.in/mf/140084); [UDiFF bhavcopy 9 Nov 2026](https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_20261109_F_0000.csv.zip)
- NSE's `/api/etf` also carries each ETF's NAV next to its last traded price (`nav` 285.8134, `navDate` 10-Nov-2026). — [NSE ETF API](https://www.nseindia.com/api/etf)
- AMFI's `https://www.amfiindia.com/spages/NAVAll.txt` now 302-redirects to `https://portal.amfiindia.com/spages/NAVAll.txt`. — [AMFI NAVAll.txt](https://www.amfiindia.com/spages/NAVAll.txt)
- mfapi.in is described as a free API aggregating AMFI data with no authentication, updated once daily; no rate limit is published (third-party descriptions, snippets). — [publicapi.dev listing](https://publicapi.dev/indian-mutual-fund-api)

### Inferences
- For a monthly rotation signal built on 3 to 12 month returns, a 0.2 to 0.3% premium or discount to NAV is small next to the return differences between asset classes, so NAV-based signals should rank ETFs the same way as price-based ones in nearly all months. This holds for liquid domestic equity and gold ETFs. It should not be assumed for ETFs that can trade at persistent premiums (for example overseas-index ETFs under subscription limits), where price and NAV can diverge by several percent.
- NAV cannot supply the 15:10 IST price and should not be used to size or price orders.
- mfapi.in is a single volunteer-style service with no SLA. Use it as a cross-check and third fallback, not as the primary.

### Gaps
- AMFI's own files (`NAVAll.txt` and the historical NAV download on portal.amfiindia.com) could not be fetched: the portal host is outside this session's allow-list, so their cloud-friendliness and publication time are untested.
- Why the NIFTYBEES scheme history on mfapi.in begins only in Nov 2016, and whether AMFI holds earlier NAVs under another scheme code.
- mfapi.in's operator, rate limits and uptime record.
- No source was gathered on the size of NAV premiums for overseas ETFs; that caution is from general knowledge, not from a cited source.

## 10. Recommendation matrix: long history, a 15:10 IST price, and a fallback when Yahoo blocks a cloud IP

### Takeaway
Cache daily closes in the bot's own Postgres and treat every external source as a feed for that cache: backfill once from Yahoo (patched against NSE bhavcopy), append each evening from the NSE UDiFF bhavcopy, and take the 15:10 IST price from a broker quote with Yahoo's chart endpoint as the free alternative. With the cache in place, a Yahoo outage costs at most one live quote, not the whole run.

### Cited Findings
- Yahoo v8 chart returned full daily history (4,411 rows for NIFTYBEES.NS from 2009) and a timestamped last price from a cloud host with only a User-Agent header on 11 Nov 2026, but rejected `Deno`, `python-requests` and curl User-Agents with 429. — [query1 v8 chart, period1/period2 form](https://query1.finance.yahoo.com/v8/finance/chart/NIFTYBEES.NS?period1=0&period2=1794500000&interval=1d&events=div%2Csplits)
- NSE's UDiFF bhavcopy for the day was available by 16:33 to 16:45 IST, includes ETFs in series EQ, and downloaded from the cloud host. — [UDiFF bhavcopy 11 Nov 2026](https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_20261111_F_0000.csv.zip)
- Market-data API calls are outside the static-IP requirement at Zerodha (official). — [Zerodha support, static IP](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/static-ip)
- Upstox offers a free, read-only, one-year Analytics Token for quotes and historical records (snippet). — [Upstox Analytics Token announcement](https://upstox.com/developer/api-documentation/announcements/analytics-token)
- Groww's paid API (Rs 499 per month plus taxes) includes live quotes and daily candles with full history (snippet and official docs). — [Groww pricing](https://915.groww.in/pricing); [Groww historical data docs](https://groww.in/trade-api/docs/curl/historical-data)
- EODHD's USD 19.99 per month plan includes delisted tickers and uses the `.NSE` code (snippets). — [EODHD plans help](https://eodhd.com/help/plans)
- yfinance's maintainer advises caching rather than refetching: "Stop spamming Yahoo, fetch smarter" (21 Jan 2026). — [yfinance discussion #2431](https://github.com/ranaroussi/yfinance/discussions/2431)

### Inferences

**Matrix (all rows are my assessment from the findings above)**

| Need | Best fit | Cost | Main caveat | Runner-up |
|---|---|---|---|---|
| (1) Long daily history, 10 ETFs + Nifty 50 | Yahoo v8 chart with `period1`/`period2`, loaded once into Postgres and patched against NSE bhavcopy | Free | Starts 2009 for NIFTYBEES; 10x error on 19-20 Dec 2019; no dividend adjustment; terms prohibit automated access | Broker daily candles (Upstox free from 2000, Groww full history) |
| (1b) Long history, ~100 stocks, survivorship-aware | EODHD All World for one or more months | USD 19.99/month | Indian adjustment quality and delisted completeness unverified | Self-built from bhavcopy plus NSE corporate actions (free, heavy work) |
| (2) Near-live price at 15:10 IST | Broker quote: Groww if already subscribed, otherwise Upstox Analytics Token | Rs 499/month + GST, or free | Groww token expires daily (automate with TOTP); Upstox token scope for candles not confirmed | Yahoo v8 `meta.regularMarketPrice` with a staleness check on `regularMarketTime` (free; delay unmeasured) |
| (3) Fallback when Yahoo blocks the cloud IP | EOD: NSE UDiFF bhavcopy. Live: the broker quote not used as primary | Free | Bhavcopy is unadjusted and not available until about 16:45 IST; User-Agent filtered | mfapi.in NAV (T+1, ETFs only); `GOOGLEFINANCE` via a published Sheet; NSE `/api/etf` (unofficial) |

**Why the Postgres cache changes the picture**
- Each run then needs only the last few days plus one live quote. A 12-month momentum signal for 11 instruments reads about 2,800 cached rows and fetches 11 prices.
- Suggested table: `(isin, trade_date, close_raw, adj_factor, source, fetched_at)`, keyed on ISIN and date, with adjusted close computed as `close_raw * adj_factor`. Keep a small `corporate_actions` table of split dates and ratios.
- Evening job (GitHub Actions cron at about 17:30 IST, or Supabase cron): download the day's UDiFF zip, upsert the tracked ISINs, and compare with Yahoo's close for the same day. Alert on a difference above about 0.5% or on a one-day move above 20%.
- 15:10 IST run: read history to T-1 from Postgres, fetch the live price from source A, fall back to source B if A fails or its timestamp is more than a few minutes old, and refuse to trade if both fail or disagree by more than about 1%.
- If the evening job has missed days, the run can still proceed from Yahoo or broker candles for the gap, so no single source is a hard dependency.

**Choice of primary and fallback for this bot (10 ETFs, monthly signals)**
- Primary for history and daily updates: NSE UDiFF bhavcopy into Postgres, seeded by a one-time Yahoo backfill that has been reconciled against bhavcopy for the full overlap.
- Primary for the 15:10 IST price: the broker the bot already trades through. Fallback: Yahoo v8 chart with an explicit browser User-Agent.
- Paid vendors (EODHD, Twelve Data) are not needed for the ETF-only version.

### Gaps
- The delay of Yahoo's unauthenticated `.NS` quote at 15:10 IST is unmeasured, so its ranking as a live fallback is provisional.
- None of the sources was tested from the actual target hosts (Vercel, Supabase Edge, GitHub Actions). Results from this one sandbox may not carry over, particularly for NSE's Akamai-fronted hosts.
- Broker details that drive the live-price choice (Groww IP rules for data, Upstox Analytics Token scope) rest on snippets and need a check against the official docs.
- Licensing: both Yahoo and NSE prohibit automated collection in their website terms. No source was found that expressly permits personal automated use of either, so the free routes carry a terms risk that only a broker API or a paid vendor removes.
