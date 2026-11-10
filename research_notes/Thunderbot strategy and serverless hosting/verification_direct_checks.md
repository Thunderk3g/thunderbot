# Direct checks of price-data sources from this cloud session

All requests below were made on 10 November 2026 between about 19:15 and 19:30 UTC from a single
cloud container (one datacentre IP address, behind the session's HTTPS proxy). This is ONE data point
from ONE address on ONE evening; it does not show how Vercel's Mumbai addresses are treated, and it
does not rule out rate-limit waves. Roughly 25 requests were made to Yahoo in total, spaced about one
second apart. 9 November 2026 was the latest trading session in every source (10 November appears to
have been a market holiday; an 8 November Sunday session, presumably Muhurat trading, shows in Upstox).

## Yahoo Finance chart endpoint (`query1.finance.yahoo.com/v8/finance/chart/...`)

| Check | Result |
|---|---|
| With a desktop Chrome User-Agent header, no cookie, no crumb | HTTP 200 on every request (about 25), for NIFTYBEES.NS, JUNIORBEES.NS, MID150BEES.NS, GOLDBEES.NS, LIQUIDCASE.NS, LIQUIDBEES.NS, MOM30IETF.NS and ^NSEI |
| Same URL with curl's default User-Agent | HTTP 429 (one request). The User-Agent header is what decides it |
| `query2` host | HTTP 200 for LIQUIDCASE.NS (one request) |
| Freshness | `regularMarketTime` = 2026-11-09 10:00 UTC (15:30 IST) for all symbols; `exchangeDataDelayedBy` not present in `meta` |
| NIFTYBEES.NS around the December 2019 unit split | History is back-adjusted (closes of 125.8–129.3 on 10–18 Dec 2019, 129.9 on 23 Dec), but the bars for **19 and 20 Dec 2019 are wrong: 13.02 and 13.03**, ten times too low. No split event is returned with `events=div,splits`. `adjclose` equals `close` |
| GOLDBEES.NS around the December 2019 unit split | Same pattern: 33.2–33.6 before, 33.65 after, but **19 and 20 Dec 2019 show 0.336**, a hundred times too low. No split event returned |
| First bar available with `range=max` | NIFTYBEES.NS, JUNIORBEES.NS, GOLDBEES.NS, LIQUIDBEES.NS: 1 Jan 2009 (so Yahoo cannot supply 2008). ^NSEI: September 2007. LIQUIDCASE.NS: 17 Jan 2024 |
| LIQUIDBEES.NS | Price is 1000.0; it carries no return information, as expected for the daily-dividend type |
| LIQUIDCASE.NS | Present, price 116.83 on 9 Nov 2026; usable as a rising-price cash series from January 2024 |
| **MID150BEES.NS** | **History is truncated: only 32 daily bars, starting 22 Sep 2026**, although `meta.firstTradeDate` says 31 Jan 2019. Yahoo cannot currently supply a backtest history for this ETF |
| **MOM30IETF.NS** | History starts 24 Jun 2024 (590 daily bars), not the August 2022 listing |

Consequences for the bot: a two-bar corruption at each 2019 split would create a false 90% or 99%
"crash" and rebound in any 200-day average or drawdown calculation unless those two bars are repaired
or dropped; and two of the symbols a rotation would use (MID150BEES, MOM30IETF) have histories on
Yahoo too short to backtest, so their history must come from NSE bhavcopy, AMFI NAVs or the index.

## Upstox public historical candles

`GET https://api.upstox.com/v2/historical-candle/NSE_EQ%7CINF204KB14I2/day/2026-11-09/2026-11-01`
(instrument key = `NSE_EQ|` + the ISIN of NIFTYBEES) returned HTTP 200 with **no authorisation header**
and seven daily candles, the latest dated 2026-11-09 with close 285.01, matching Yahoo's 285.01.
This confirms a working, no-login fallback for daily candles from a cloud address (single test).
Whether the candles are adjusted for corporate actions was not checked.

## NSE archive files (`nsearchives.nseindia.com`)

| File for 9 Nov 2026 | Status with a browser User-Agent | `Last-Modified` header |
|---|---|---|
| `content/cm/BhavCopy_NSE_CM_0_0_0_20261109_F_0000.csv.zip` (UDiFF bhavcopy) | 200, 207 KB | 11:15 GMT = 16:45 IST |
| `products/content/sec_bhavdata_full_09112026.csv` (full bhavcopy with delivery data) | 200 | 18:25 GMT = 23:55 IST |
| `content/indices/ind_close_all_09112026.csv` (all index closes) | 200, 17.5 KB | 17:50 GMT = 23:20 IST |
| `content/indices/ind_nifty100list.csv` (current Nifty 100 constituents) | 200 | not recorded |

The same index file requested with curl's default User-Agent failed (HTTP/2 stream error, no
response). `www.nseindia.com` itself returned 403 to a plain request and was not pursued. The archive
files are published after the close, so they suit reconciliation and backtests, not a 15:10 decision.

## Other reachability observed (one request each)

`api.mfapi.in` 200; `www.niftyindices.com` 200 (home page); `groww.in/pricing` 200;
`supabase.com/docs/guides/cron` 200; `vercel.com/docs/...` 308 redirect (follow redirects);
`www.sebi.gov.in` 200; `support.zerodha.com` 200; `docs.github.com` 200; `cloud.google.com` 200;
`www.incometaxindia.gov.in` 403; `www.amfiindia.com/spages/NAVAll.txt` 302.
