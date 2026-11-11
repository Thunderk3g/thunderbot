# Indian liquid/overnight ETFs on NSE and the historical return on cash (2008 to Nov 2026)

Research date: 11 Nov 2026. Market data below is "as of" 9-11 Nov 2026 unless stated.

**How to read the sourcing in this file**

- "AMFI NAV" = daily NAV history of the scheme published by AMFI, pulled through the public mirror `api.mfapi.in/mf/<scheme code>`. All yields and calendar-year fund returns were computed by me from those NAVs (simple point-to-point; face-value rebasings of x10/x100 adjusted). They are computed figures, not AMC-published figures.
- "Groww ETF page" = the data block embedded in each ETF's page on groww.in (TER, AUM, launch date, average volume). Groww is an aggregator, not the AMC; treat TER/AUM as indicative.
- "Groww candles" = NSE daily/1-minute OHLCV served by Groww's charting endpoint for the symbol (1 year to 11 Nov 2026).
- Access limits in this session: AMC sites (nipponindiaim, zerodhafundhouse, growwmf, dspim, kotakmf, hdfcfund, sbimf, miraeassetmf, bajajamc), nseindia.com, rbi.org.in, CRISIL, Value Research, Morningstar, tradingqna and most news sites were blocked by the network policy, and the web-search budget ran out part-way. No AMC factsheet or SID was opened. Items that rest only on a search-result snippet are marked "(search snippet, page not opened)".

---

## 1. The two kinds of liquid ETF, and every liquid/overnight ETF found on NSE

### Takeaway
There are 20 live liquid/overnight ETFs on NSE: 6 daily-dividend (IDCW) ones whose price is pinned near Rs 1,000, and 14 growth ones whose NAV rises every day. For a bot, Zerodha's LIQUIDCASE is the only growth ETF that combines very large volume (median about Rs 231 crore a day) with no off-NAV prints in the past year; it is the default choice, with Kotak LIQUID1, DSP LIQUIDADD and Mirae LIQUIDPLUS as cheaper-TER but thinner alternatives. Net yield in early Nov 2026 is about 5.0-5.3% annualised, below the 5.5-6.5% assumed in the brief.

### Cited Findings

**Common structure**

- All but three track the Nifty 1D Rate Index, which "uses the overnight rate provided through Triparty Repo Dealing System (TREPS)"; the CCIL weighted average rate is divided by 365 and added daily; base date 3 Jan 2011, base value 1000, launched 23 Jun 2016 — [NSE Indices factsheet, 30 Oct 2026](https://www.niftyindices.com/Factsheet/Factsheet_Nifty_1D_Rate.pdf)
- Exceptions: DSP LIQUIDADD and ICICI LIQUIDIETF/CASHIETF track the BSE Liquid Rate Index; ABSLLIQUID tracks the CRISIL Liquid Overnight Index — Groww ETF pages for [LIQUIDADD](https://groww.in/etfs/dsp-sp-bse-liquid-rate-etf), [CASHIETF](https://groww.in/etfs/icici-prudential-bse-liquid-rate-etf-growth), [ABSLLIQUID](https://groww.in/etfs/aditya-birla-sun-life-amc-ltd-abslliquid) (as of 9 Nov 2026)
- TREPS is described as backed by government securities — [Groww blog, 3 Mar 2025](https://groww.in/blog/what-is-treps-in-mutual-funds)

**Kind 1: daily-dividend (IDCW) ETFs, price pinned at about Rs 1,000**

- LIQUIDBEES "declares daily Dividend and the same is compulsorily reinvested in the Scheme on daily basis. The Units arising out of Dividend reinvestment results into fractional Units"; Nippon runs a buyback/redemption route for fractional units — [Nippon fractional-redemption procedure hosted by Sushil Finance](https://www.sushilfinance.com/upload/downloadfiles/Fraction-Redemption-procedure.pdf) (search snippet, page not opened)
- Crediting frequency: dividends are "calculated daily and reinvested as additional units, which are credited to your demat account every 30 days" — [Groww "Liquid ETF" page, undated, read 11 Nov 2026](https://groww.in/p/liquid-etf). A forum thread says "credited on monthly basis" — [TradingQnA](https://tradingqna.com/t/what-is-the-earning-of-liquid-bees/155082) (search snippet, page not opened). I could not confirm "weekly" anywhere.
- AMFI NAV for the IDCW ETFs is exactly Rs 1,000.00 every day (LIQUIDBEES from 6 Nov 2016 to 10 Nov 2026; DSP LIQUIDETF from 19 Mar 2018; ICICI LIQUIDIETF from 25 Sep 2018; ABSLLIQUID, Mirae LIQUID, LIQUIDSBI likewise), so the whole return arrives as units — AMFI NAV: [LIQUIDBEES 140086](https://api.mfapi.in/mf/140086), [DSP 142589](https://api.mfapi.in/mf/142589), [ICICI 144947](https://api.mfapi.in/mf/144947), [ABSL 151533](https://api.mfapi.in/mf/151533), [Mirae 151908](https://api.mfapi.in/mf/151908), [SBI 152168](https://api.mfapi.in/mf/152168)
- NSE closing price of every IDCW ETF stayed between Rs 999.99 and Rs 1,000.01 on all but a handful of sessions in the past year (LIQUIDBEES 249/249 sessions; ICICI LIQUIDIETF 243/249; LIQUIDSBI 247/249) — Groww candles: [LIQUIDBEES](https://groww.in/v1/api/charting_service/v2/chart/exchange/NSE/segment/CASH/LIQUIDBEES/1y?intervalInDays=1&minimal=false), [LIQUIDIETF](https://groww.in/v1/api/charting_service/v2/chart/exchange/NSE/segment/CASH/LIQUIDIETF/1y?intervalInDays=1&minimal=false), [LIQUIDSBI](https://groww.in/v1/api/charting_service/v2/chart/exchange/NSE/segment/CASH/LIQUIDSBI/1y?intervalInDays=1&minimal=false)
- Tax on the dividend units: "The value of the dividend units allotted to you is treated as dividend income and is taxable under the head Income from Other Sources at your applicable income tax slab rate"; that value becomes the cost of those units; TDS "may be deducted before the dividend units are credited" once the dividend "exceeds the prescribed threshold during the financial year" — [Zerodha support](https://support.zerodha.com/category/console/reports/taxation/articles/dividends-on-liquid-etfs-and-liquid-bees) (read 11 Nov 2026)
- The TDS threshold on mutual fund income (Section 194K, 10%) is Rs 10,000 per financial year from 1 Apr 2025, up from Rs 5,000 — [India Briefing TDS guide FY 2025-26](https://india-briefing.com/news/a-guide-to-indias-tds-rates-for-fy-2025-26-36999.html) (search snippet, page not opened)

**Kind 2: growth ETFs, NAV and price rise daily, no dividend**

- NAVs of all 14 growth ETFs rise every calendar day (weekends included, as AMFI publishes Sunday NAVs). LIQUIDCASE, LIQUIDADD and GROWWLIQID have had zero down-days in NAV since launch — AMFI NAV: [LIQUIDCASE 152327](https://api.mfapi.in/mf/152327), [LIQUIDADD 152555](https://api.mfapi.in/mf/152555), [GROWWLIQID 152891](https://api.mfapi.in/mf/152891)
- Groww describes its own ETF as a "Growth NAV Option" in which overnight interest is added to the fund's value, with "No Securities Transaction Tax (STT)" and "No Exit Load" — [Groww blog, 20 Nov 2025](https://groww.in/blog/groww-mutual-fund-has-introduced-nifty-1d-rate-liquid-etf)
- LIQUIDCASE is on Zerodha's approved list for pledging — [Zerodha support](https://support.zerodha.com/category/trading-and-markets/trading-faqs/trading-categories-and-groups/articles/liquidcase-etf-for-pledging)

**Ticker identifications asked for in the brief**

- LIQUIDADD is DSP Mutual Fund's "DSP BSE Liquid Rate ETF" (formerly DSP S&P BSE Liquid Rate ETF), ISIN INF740KA1UM0, BSE 544159, growth, tracks BSE Liquid Rate Index (not Nifty 1D Rate) — [Groww ETF page](https://groww.in/etfs/dsp-sp-bse-liquid-rate-etf); listing announced 3 Apr 2024 — [FintechBizNews](https://fintechbiznews.com/finserv-mf-amcs/dsp-sp-bse-liquid-rate-etf-listed-) (search snippet, page not opened)
- Groww's own ETF is GROWWLIQID (Groww Nifty 1D Rate Liquid ETF, ISIN INF666M01IP5, BSE 590159), unit price about Rs 111.6 — [Groww ETF page](https://groww.in/etfs/groww-nifty-rate-liquid-etf)
- LIQUIDPLUS is Mirae Asset's growth ETF (ISIN INF769K01MY5), not HDFC's. HDFC's symbol is HDFCLIQUID — [Groww LIQUIDPLUS](https://groww.in/etfs/mirae-asset-nifty-d-rate-liquid-etfgrowth), [Groww HDFCLIQUID](https://groww.in/etfs/hdfc-nifty-d-rate-liquid-etf)
- LIQGRWBEES exists: Nippon India Nifty 1D Rate Liquid ETF - Growth, first NAV 24 Jul 2025 — [Groww ETF page](https://groww.in/etfs/nippon-india-nifty-1d-rate-liquid-etf-growth-ltd), [AMFI NAV 153725](https://api.mfapi.in/mf/153725)
- HDFCLIQUID was an IDCW ETF and became growth-only from 28 Feb 2025 — [Angel One](https://www.angelone.in/news/mutual-funds/hdfc-nifty-one-d-rate-liquid-etf-switches-to-growth-option) (search snippet, page not opened); consistent with AMFI data, where the old code ends at NAV 1000 on 28 Feb 2025 and the growth code starts 2 Mar 2025 — [AMFI 152049](https://api.mfapi.in/mf/152049), [AMFI 153403](https://api.mfapi.in/mf/153403)
- Kotak LIQUID1: AMFI NAV was flat at 1000.00 until 28 Jul 2024 and has accumulated since 29 Jul 2024 (1000.1681), reaching 1131.2545 on 10 Nov 2026 — [AMFI NAV 151358](https://api.mfapi.in/mf/151358)

**Full table (as of 9-11 Nov 2026)**

Columns: launch = Groww "foundation date"; TER and AUM = Groww ETF page (9 Nov 2026); traded value = median and minimum daily NSE traded value over the last 60 sessions to 11 Nov 2026 from Groww candles (volume x close); 7d/30d yield = simple annualised change in AMFI NAV to 10 Nov 2026; 1Y = AMFI NAV change 30 Oct 2025 to 30 Oct 2026 (index over the same window: 5.23%); "drag" = 5.23% minus that 1Y figure.

| NSE symbol | AMC / scheme | Kind | Index | Launch | TER % | AUM Rs cr | Traded value Rs cr/day, median (min) | NAV 10 Nov 2026 | 7d / 30d yield % | 1Y % (drag) |
|---|---|---|---|---|---|---|---|---|---|---|
| LIQUIDBEES | Nippon India ETF Nifty 1D Rate Liquid BeES | IDCW daily | Nifty 1D Rate | 8 Jul 2003 | 0.71 | 10,033 | 384.5 (95.6) | 1000.00 | not computable from NAV | see gap |
| LIQUIDETF | DSP Nifty 1D Rate Liquid ETF | IDCW daily | Nifty 1D Rate | 14 Mar 2018 | 0.32 | 540 | 12.6 (3.0) | 1000.00 | n/c | n/c |
| LIQUIDIETF | ICICI Pru BSE Liquid Rate ETF - IDCW | IDCW daily | BSE Liquid Rate | 25 Sep 2018 | 0.36 | 974 | 41.6 (12.9) | 1000.00 | n/c | n/c |
| ABSLLIQUID | ABSL CRISIL Liquid Overnight ETF | IDCW daily | CRISIL Liquid Overnight | 13 Mar 2023 | 0.44 | 43 | 0.38 (0.03) | 1000.00 | n/c | n/c |
| LIQUID | Mirae Asset Nifty 1D Rate Liquid ETF - IDCW | IDCW daily | Nifty 1D Rate | 27 Jul 2023 | 0.36 | 468 | 14.5 (1.8) | 1000.00 | n/c | n/c |
| LIQUIDSBI | SBI Nifty 1D Rate Liquid ETF - IDCW | IDCW daily | Nifty 1D Rate | 27 Oct 2023 | 0.36 | 46 | 0.44 (0.06) | 1000.00 | n/c | n/c |
| LIQUID1 | Kotak Nifty 1D Rate Liquid ETF | Growth (since 29 Jul 2024) | Nifty 1D Rate | 24 Jan 2023 | 0.24 | 2,617 | 96.5 (18.8) | 1131.25 | 5.21 / 5.23 | 5.02 (0.21) |
| LIQUIDCASE | Zerodha Nifty 1D Rate Liquid ETF | Growth | Nifty 1D Rate | 17 Jan 2024 | 0.28 | 11,179 | 231.4 (110.0) | 116.83 | 5.20 / 5.33 | 4.96 (0.27) |
| LIQUIDADD | DSP BSE Liquid Rate ETF | Growth | BSE Liquid Rate | 27 Mar 2024 | 0.31 | 1,962 | 53.8 (4.7) | 1153.67 | 5.27 / 5.31 | 4.93 (0.30) |
| LIQUIDBETF | Bajaj Finserv Nifty 1D Rate Liquid ETF | Growth | Nifty 1D Rate | 28 May 2024 | 0.21 | 582 | 28.2 (10.2) | 1107.16 | 5.30 / 5.12 | 4.84 (0.39) |
| LIQUIDSHRI | Shriram Nifty 1D Rate Liquid ETF | Growth | Nifty 1D Rate | 5 Jul 2024 | 0.52 | 34 | 0.82 (0.03) | 1129.86 | 5.05 / 5.10 | 4.74 (0.49) |
| GROWWLIQID | Groww Nifty 1D Rate Liquid ETF | Growth | Nifty 1D Rate | 24 Sep 2024 | 0.38 | 87 | 3.4 (0.84) | 111.58 | 5.00 / 5.07 | 4.72 (0.51) |
| LIQUIDPLUS | Mirae Asset Nifty 1D Rate Liquid ETF - Growth | Growth | Nifty 1D Rate | 7 Nov 2024 | 0.21 | 904 | 42.6 (2.7) | 1111.98 | 5.30 / 5.38 | 5.01 (0.22) |
| HDFCLIQUID | HDFC Nifty 1D Rate Liquid ETF - Growth | Growth (IDCW until 28 Feb 2025) | Nifty 1D Rate | 24 Aug 2023 | 0.25 | 177 | 2.9 (0.28) | 1086.45 | 5.30 / 5.39 | 4.91 (0.32) |
| CASHIETF | ICICI Pru BSE Liquid Rate ETF - Growth | Growth | BSE Liquid Rate | 12 Mar 2025 | 0.26 | 988 | 21.1 (0.94) | 1088.07 | 5.33 / 5.37 | 5.00 (0.23) |
| AONELIQUID | Angel One Nifty 1D Rate Liquid ETF | Growth | Nifty 1D Rate | 25 Mar 2025 | 0.34 | 243 | 2.1 (0.45) | 1085.42 (11 Nov) | 5.23 / 5.24 | 4.99 (0.24) |
| LIQGRWBEES | Nippon India Nifty 1D Rate Liquid ETF - Growth | Growth | Nifty 1D Rate | 24 Jul 2025 | 0.25 | 307 | 8.0 (1.0) | 1063.63 | 5.30 / 5.32 | 4.73 (0.50) |
| SBILIQETF | SBI Nifty 1D Rate Liquid ETF - Growth | Growth | Nifty 1D Rate | 8 Aug 2025 | 0.29 | 154 | 13.1 (0.62) | 1064.25 | 5.27 / 5.32 | 4.99 (0.24) |
| ELIQUID | Edelweiss Nifty 1D Rate Liquid ETF | Growth | Nifty 1D Rate | 6 Oct 2025 | 0.22 | 77 | 2.9 (0.07) | 1056.72 | 5.32 / n.a. | 5.08 (0.15) |
| LIQUIDBETA | UTI Nifty 1D Rate Liquid ETF - Growth | Growth | Nifty 1D Rate | 16 Jul 2026 | 0.23 | 31 | 0.009 (0.0001) | 1016.03 | 5.32 / 5.40 | too new |

Sources for the table: Groww ETF pages — [LIQUIDBEES](https://groww.in/etfs/reliance-etf-liquid-bees), [LIQUIDETF](https://groww.in/etfs/dsp-blackrock-investment-managers-pvt-ltd-liquidetf), [LIQUIDIETF](https://groww.in/etfs/icici-prudential-asset-management-company-ltd-iciciliq), [ABSLLIQUID](https://groww.in/etfs/aditya-birla-sun-life-amc-ltd-abslliquid), [LIQUID](https://groww.in/etfs/mirae-asset-nifty-d-rate-liquid-etf), [LIQUIDSBI](https://groww.in/etfs/sbi-noftuy-d-rate-etf), [LIQUID1](https://groww.in/etfs/kotak-nifty-d-rate-liquid-etf), [LIQUIDCASE](https://groww.in/etfs/zerodha-nifty-d-rate-liquid-etf), [LIQUIDADD](https://groww.in/etfs/dsp-sp-bse-liquid-rate-etf), [LIQUIDBETF](https://groww.in/etfs/bajaj-finserv-nifty-d-rate-liquid-etf), [LIQUIDSHRI](https://groww.in/etfs/shriram-nifty-d-rate-liquid-etf), [GROWWLIQID](https://groww.in/etfs/groww-nifty-rate-liquid-etf), [LIQUIDPLUS](https://groww.in/etfs/mirae-asset-nifty-d-rate-liquid-etfgrowth), [HDFCLIQUID](https://groww.in/etfs/hdfc-nifty-d-rate-liquid-etf), [CASHIETF](https://groww.in/etfs/icici-prudential-bse-liquid-rate-etf-growth), [AONELIQUID](https://groww.in/etfs/angle-one-liquid-1d-ltd), [LIQGRWBEES](https://groww.in/etfs/nippon-india-nifty-1d-rate-liquid-etf-growth-ltd), [SBILIQETF](https://groww.in/etfs/sbi-nifty-d-rate-liquid-etf), [ELIQUID](https://groww.in/etfs/edelweiss-nifty-1d-rate-liquid-etf), [LIQUIDBETA](https://groww.in/etfs/units-of-uti-nifty-d-rate-liquid-etf-growth). AMFI NAVs — scheme codes 151358, 152327, 152555, 152638, 152741, 152891, 153045, 153403, 153378, 153451, 153725, 153796, 153920, 154466 at `https://api.mfapi.in/mf/<code>`, e.g. [152327](https://api.mfapi.in/mf/152327). Volumes — Groww candles, e.g. [LIQUIDCASE](https://groww.in/v1/api/charting_service/v2/chart/exchange/NSE/segment/CASH/LIQUIDCASE/1y?intervalInDays=1&minimal=false) (replace the symbol for others). Index 1Y of 5.23% — [NSE Indices factsheet, 30 Oct 2026](https://www.niftyindices.com/Factsheet/Factsheet_Nifty_1D_Rate.pdf).

**Bid-ask spread (proxy)**

- No order-book snapshot was available (market closed when checked). Proxy: high minus low of each 1-minute bar on 11 Nov 2026. LIQUIDCASE: 287 of 375 bars had a range of Rs 0.01 and 85 had Rs 0.02; the whole day traded Rs 116.84-116.86. LIQUIDBEES: 281 of 375 bars Rs 0.01; day range Rs 999.99-1000.01. GROWWLIQID: 170 of 194 bars had zero range, 24 had Rs 0.01; day range Rs 111.59-111.60. Rs 1,000-type growth ETFs (LIQUIDADD, LIQUIDPLUS, LIQUIDBETF, LIQGRWBEES, AONELIQUID, HDFCLIQUID): day range Rs 0.02 — Groww 1-minute candles, e.g. [LIQUIDCASE](https://groww.in/v1/api/charting_service/v2/chart/exchange/NSE/segment/CASH/LIQUIDCASE/daily?intervalInMinutes=1&minimal=false), [GROWWLIQID](https://groww.in/v1/api/charting_service/v2/chart/exchange/NSE/segment/CASH/GROWWLIQID/daily?intervalInMinutes=1&minimal=false), [LIQUIDBEES](https://groww.in/v1/api/charting_service/v2/chart/exchange/NSE/segment/CASH/LIQUIDBEES/daily?intervalInMinutes=1&minimal=false)

**Current yield versus the brief's assumption**

- Nifty 1D Rate Index: YTD 4.31%, 1 year 5.23%, 5 years 5.80% CAGR, since inception 6.27% CAGR, as of 30 Oct 2026 — [NSE Indices factsheet](https://www.niftyindices.com/Factsheet/Factsheet_Nifty_1D_Rate.pdf)
- Index yield shown as 5.74% on 31 Oct 2026 (a month-end reading) — [NSE Indices fixed income dashboard, Oct 2026](https://www.niftyindices.com/Index_Dashboard_Fixed_Income/Index_Dashboard_FixedIncome_OCT2026.pdf)
- HDFC Overnight Fund Direct-Growth annualised by month in 2026: Jan 5.23, Feb 4.75, Mar 5.19, Apr 5.03, May 5.07, Jun 5.16, Jul 5.14, Aug 5.01, Sep 4.82, Oct 5.38, Nov (to 10th) 5.52 — computed from [AMFI NAV 119110](https://api.mfapi.in/mf/119110)
- RBI repo rate was 5.25% after a 25 bp cut on 5 Dec 2025, and was held at 5.25% (SDF 5.00%, MSF 5.50%, neutral stance) on 6 Feb 2026 and 5 Jun 2026 — Groww blog [5 Dec 2025](https://groww.in/blog/rbi-repo-rate-cut), [6 Feb 2026](https://groww.in/blog/rbi-repo-rate-remains-unchanged), [5 Jun 2026](https://groww.in/blog/rbi-keeps-repo-rate-unchanged-maintains-neutral-stance-amidst-global-uncertainty)

### Inferences
- The realised "drag" column is more useful than the headline TER. Kotak, Mirae, ICICI growth, SBI growth and Angel One delivered within 0.21-0.24% of the index over the last year; Zerodha 0.27%; Nippon growth, Groww and Shriram lost about 0.5%. Nippon LIQGRWBEES shows a 0.25% TER on Groww but a 0.50% realised drag, so its TER was probably higher earlier in the year or the Groww figure is stale.
- Yield differences between the good ETFs are about 0.05-0.3% a year, i.e. Rs 50-300 a year per Rs 1 lakh. Execution quality (tight book, no freak prints) matters far more for a bot than TER. On that test LIQUIDCASE is clearly best, followed by LIQUIDBEES for depth only.
- LIQUIDBEES at TER 0.71% should yield roughly index minus 0.7%, about 4.5% over the last year, i.e. about 0.45% a year less than LIQUIDCASE, before the dividend/fractional-unit hassle.
- A Rs 1,000-type unit leaves up to Rs 1,100 unparked per purchase; a Rs 100-type unit (LIQUIDCASE, GROWWLIQID) leaves at most about Rs 117. Trivial either way.
- Using Groww's own GROWWLIQID has no visible advantage at the Groww broker: highest drag (0.51%), AUM only Rs 87 crore, median traded value Rs 3.4 crore a day.

### Gaps
- No AMC factsheet could be opened, so TER and AUM are Groww's figures (9 Nov 2026), not the AMC's. Verify TER on the AMC site before committing.
- LIQUIDBEES 7-day/30-day yield and its exact dividend-credit schedule (30 days per Groww; "weekly" not confirmed) could not be taken from Nippon's own documents.
- Groww's displayed returns for IDCW ETFs look unreliable (LIQUIDBEES 1Y 4.24%, 5Y 4.53%; DSP LIQUIDETF 1Y 7.51%), so they are not used — [Groww LIQUIDBEES](https://groww.in/etfs/reliance-etf-liquid-bees), [Groww LIQUIDETF](https://groww.in/etfs/dsp-blackrock-investment-managers-pvt-ltd-liquidetf)
- UTI's NSE symbol is shown as LIQUIDBETA by Groww; not cross-checked on nseindia.com (blocked).
- Actual bid/ask quotes and depth were not observed; the spread is inferred from 1-minute trade ranges on one day.
- RBI decisions at the Aug and Oct 2026 MPC meetings were not found. Overnight fund yields of 4.8-5.5% through Nov 2026 give no sign of a large move away from 5.25%.

---

## 2. Why the growth kind is simpler, round-trip cost at Groww, and breakeven days

### Takeaway
A round trip at Groww costs about Rs 94 on Rs 1 lakh and about Rs 298 on Rs 10 lakh before spread, of which Rs 70.80 is fixed (two Rs 20 brokerages, the Rs 20 DP charge, and GST). At today's roughly 5.2% net yield that is about 7 days of interest on Rs 1 lakh and 2-3 days on Rs 10 lakh; below about Rs 50,000 parking rarely pays unless cash sits for weeks.

### Cited Findings
- Groww equity delivery brokerage: "Rs 20 or 0.1% of trade value per order, whichever is lower", minimum Rs 5; STT 0.1% on stocks; stamp duty 0.015% on buy only; NSE exchange transaction charge 0.00307% (pricing page) or 0.00297% (help page) each side; SEBI turnover fee 0.0001%; IPFT 0.0001% (NSE); DP charge on sell: Groww Rs 16.5 (Rs 0 if debit value under Rs 100) plus depository Rs 3.5 (Rs 3.25 for women); GST 18% on brokerage, DP, exchange, SEBI and IPFT charges — [Groww pricing](https://groww.in/pricing/stocks), [Groww help: charges](https://groww.in/help/brokerage-and-taxes/charges-for-delivery/what-are-the-different-charges-mentioned-in-the-report) (read 11 Nov 2026)
- Neither Groww page has any ETF-specific or liquid-ETF-specific line — same two pages
- STT: liquid ETFs are exempt. Zerodha: STT "does not apply to GOLD ETFs, LIQUID and Gilt ETFs, and some international ETFs" — [Zerodha support: STT on ETFs](https://support.zerodha.com/category/account-opening/resident-individual/ri-charges/articles/stt-etfs). Zerodha: liquid ETF charges are "the same as those of equity trades, except that STT is not charged" — [Zerodha support: Liquid BeES charges](https://support.zerodha.com/category/account-opening/charges-at-zerodha/articles/what-are-the-charges-for-trading-in-liquidbees). Groww: liquid ETF trading does not incur STT — [Groww Liquid ETF page](https://groww.in/p/liquid-etf), [Groww blog, 10 Jul 2025](https://groww.in/blog/difference-between-liquid-funds-and-liquid-etfs)
- Stamp duty still applies to liquid ETFs ("Uniform stamp duty based on the value of the transaction") and so does a DP charge on sale: at Zerodha Rs 9.50 + GST for Liquid BeES and Rs 13 + GST for other liquid ETFs — [Zerodha support: Liquid BeES charges](https://support.zerodha.com/category/account-opening/charges-at-zerodha/articles/what-are-the-charges-for-trading-in-liquidbees)
- No entry or exit load, because the ETF trades on the secondary market — same Zerodha page
- Growth option: "many liquid ETFs do not issue dividends", so tax applies only on sale — [Groww blog, 20 Nov 2025](https://groww.in/blog/groww-mutual-fund-has-introduced-nifty-1d-rate-liquid-etf)
- IDCW option: each dividend allotment is slab-rate income with possible TDS, and creates its own cost lot — [Zerodha support](https://support.zerodha.com/category/console/reports/taxation/articles/dividends-on-liquid-etfs-and-liquid-bees)

### Inferences

**Round-trip cost model for Groww (my arithmetic from the rates above; assumes Groww applies its standard delivery schedule to liquid ETFs with STT nil)**

Cost = Rs 70.80 fixed + 0.0227% of the amount + spread.

- Fixed: brokerage Rs 20 buy + Rs 20 sell + DP Rs 20 on sell = Rs 60, plus 18% GST = Rs 70.80. (Brokerage reaches the Rs 20 cap at Rs 20,000 order size. Below that it is 0.1% a side, minimum Rs 5.)
- Proportional: stamp duty 0.015% (buy) + exchange 0.00307% x 2 + SEBI and IPFT 0.0002% x 2, with GST on the last two groups = about 0.0227%.
- Spread: one tick. Rs 0.01 on a Rs 116.85 unit (LIQUIDCASE) = 0.86 bp = Rs 8.6 per Rs 1 lakh. Rs 0.01 on a Rs 1,000-1,150 unit = about 0.09-0.1 bp = Rs 1 per Rs 1 lakh.

| Amount | Buy side Rs | Sell side Rs | Round trip Rs (before spread) | + spread, Rs 1,000-type unit | + spread, LIQUIDCASE/GROWWLIQID |
|---|---|---|---|---|---|
| Rs 20,000 | 27.4 | 48.0 | 75.3 | 75.5 | 77.0 |
| Rs 1,00,000 | 42.5 | 51.1 | 93.5 | 94.4 | 102.1 |
| Rs 10,00,000 | 212.2 | 85.8 | 298.0 | 307 | 384 |

**Breakeven calendar days of accrual (cost divided by daily interest)**

| Net yield | Rs 1 lakh, Rs 1,000-type | Rs 1 lakh, LIQUIDCASE | Rs 10 lakh, Rs 1,000-type | Rs 10 lakh, LIQUIDCASE |
|---|---|---|---|---|
| 5.2% (actual, Nov 2026) | 6.6 | 7.2 | 2.2 | 2.7 |
| 5.5% | 6.3 | 6.8 | 2.0 | 2.5 |
| 6.0% | 5.7 | 6.2 | 1.9 | 2.3 |
| 6.5% | 5.3 | 5.7 | 1.7 | 2.2 |

- For Rs 20,000 at 5.2% the breakeven is about 26 days (Rs 75 cost, Rs 2.85 a day). Parking small sums is not worth it.
- Even at very large size the proportional cost (2.3 bp plus spread) equals 1.6-2.2 days of yield, so parking for one or two nights never pays.
- Net gain examples at 5.2%: Rs 1 lakh parked 30 days earns about Rs 427 gross, Rs 325-333 after costs, about Rs 225-230 after 31.2% slab tax (costs reduce the taxable gain). Rs 10 lakh for 30 days: about Rs 4,274 gross, Rs 3,890-3,967 after costs.
- A single Rs 0.01 tick on LIQUIDCASE equals about 0.6 days of yield; daily accrual (about Rs 0.0166 per unit at 5.2%) is larger than one tick, so the price normally rises 1-2 ticks a day. On a Rs 1,000-type unit a tick is about 0.07 days of yield.
- Why growth is simpler for a bot: one holding with integer units, no periodic dividend-unit credits to reconcile, no fractional units stranded in demat, no TDS entries, and one capital-gain line per sale. With IDCW the bot's holdings quantity changes without a trade, and the fractional remainder cannot be sold on the exchange.
- Tax amount is broadly the same either way (slab rate on dividend or on gain), but growth defers it to the sale and avoids TDS cash drag above Rs 10,000 of dividends a year.
- Splitting a sale over several days repeats the Rs 23.60 DP charge each day; sell the whole position in one day where possible.

### Gaps
- Not confirmed from a Groww source: whether Groww charges its Rs 16.5 + Rs 3.5 DP fee on liquid ETF sales (Zerodha does charge, at a reduced rate), and whether Groww's order window shows STT nil for these symbols. A Rs 100-200 test trade and its contract note would settle both.
- Groww's two pages disagree on the NSE transaction charge (0.00307% vs 0.00297%); the difference is under Rs 1 per Rs 10 lakh round trip.
- Stamp duty of 0.015% on a debt-ETF purchase is taken from Groww's general delivery schedule; no liquid-ETF-specific statement was found.

---

## 3. Settlement mechanics that matter

### Takeaway
Groww says 100% of delivery sale proceeds are usable for new trades within 30 minutes, so a liquid ETF sold from demat can fund a same-day stock/ETF buy; the exception is a buy-today-sell-tomorrow (BTST) sale, whose proceeds are blocked for that whole day. In practice the market price already carries weekend and holiday accrual on the last trading day before the break, so interest runs settlement-date to settlement-date.

### Cited Findings
- Groww: "100% of the sell amount will be available within 30 minutes for further trading in Stocks & FnO"; previously "only 80% was available on the same day"; withdrawal of the full amount "after 10 AM on the next trading day (T+1 day)" — [Groww help](https://groww.in/help/stocks/searchable/how-long-before-i-get-money-in-my-groww-balance-after-selling-shares) (undated; refers to "the new NSE circular"; read 11 Nov 2026)
- Groww, same page: for BTST trades "the full sell amount will be blocked for the entire day and can only be used or withdrawn the next trading day"
- Older Groww pages still describe the 80% rule (20% blocked till end of day) — [Groww blog: margin on selling stocks](https://groww.in/blog/margin-on-selling-stocks) (search snippet, page not opened)
- Groww: shares bought today can be sold immediately (treated as intraday); trade-to-trade categories can be sold only after T+1 delivery — [Groww help](https://groww.in/help/stocks/order/when-can-i-sell-the-shares-which-i-have-purchased-today-1)
- BTST: selling on T+1 before the units reach demat relies on the original seller delivering; a short delivery can lead to an auction penalty "up to 20% of the value of stock short delivered" — [Zerodha support: BTST risk](https://support.zerodha.com/category/trading-and-markets/trading-faqs/general/articles/btst-risk); "proceeds from the sale of BTST shares are often not available for new trades on the same day" — [Groww blog, 17 Jun 2026](https://groww.in/blog/btst-trading)
- Returns on a liquid ETF begin "as soon as the trade settlement is completed" — [Groww blog, 10 Jul 2025](https://groww.in/blog/difference-between-liquid-funds-and-liquid-etfs)
- Weekend/holiday accrual is priced in advance. Over the year to 11 Nov 2026 the NSE close was within about 0.1 bp of same-day NAV on Mondays to Thursdays (median), but on Fridays the median close was 2.58 bp (LIQUIDCASE), 2.60 bp (LIQUIDADD) and 2.73 bp (LIQUIDPLUS) above Friday's NAV, and about 3.0-4.3 bp above on the day before a three-day break (23 Jan, 2 Apr, 30 Apr, 25 Jun, 11 Sep, 1 Oct 2026) — computed from Groww candles ([LIQUIDCASE](https://groww.in/v1/api/charting_service/v2/chart/exchange/NSE/segment/CASH/LIQUIDCASE/1y?intervalInDays=1&minimal=false), [LIQUIDADD](https://groww.in/v1/api/charting_service/v2/chart/exchange/NSE/segment/CASH/LIQUIDADD/1y?intervalInDays=1&minimal=false), [LIQUIDPLUS](https://groww.in/v1/api/charting_service/v2/chart/exchange/NSE/segment/CASH/LIQUIDPLUS/1y?intervalInDays=1&minimal=false)) against AMFI NAVs ([152327](https://api.mfapi.in/mf/152327), [152555](https://api.mfapi.in/mf/152555), [153045](https://api.mfapi.in/mf/153045))
- Liquid ETFs can be pledged for margin; LIQUIDCASE is on Zerodha's approved list — [Zerodha support](https://support.zerodha.com/category/trading-and-markets/trading-faqs/trading-categories-and-groups/articles/liquidcase-etf-for-pledging); Groww notes brokers "often accept these units as margin" — [Groww Liquid ETF page](https://groww.in/p/liquid-etf)
- ETF price bands: the base was the T-2 NAV, which can put the lower circuit above the last traded price — [Zerodha support: circuit limits for ETFs](https://support.zerodha.com/category/trading-and-markets/trading-faqs/general/articles/circuit-limits-for-etfs); SEBI moved the base to the previous day's NAV with category-specific dynamic bands from 1 Sep 2026 — [Groww blog, 16 Jun 2026](https://groww.in/blog/sebi-revises-etf-trading-framework-to-keep-prices-closer-to-underlying-asset-values)

### Inferences
- Workable bot sequence at Groww: sell the liquid ETF first (limit order at the bid), wait for the fill and for buying power to refresh (Groww says up to 30 minutes), then buy the target ETF. Budget for that delay rather than assuming instant credit.
- To keep same-day redeployment, do not sell liquid ETF units bought the previous trading day: that is BTST and Groww blocks the proceeds for the day. Units bought on day T are safely sellable with usable proceeds from T+2. This sets a practical minimum parking period of two trading days, which is also roughly the cost breakeven at Rs 10 lakh.
- Because Friday's price includes Saturday and Sunday accrual, buying on Friday and selling on Monday earns about one day, not three. The backtest should accrue cash interest on calendar days between settlement dates (T+1 to T+1), which over long holds equals calendar days held.
- Buying a liquid ETF with same-day stock-sale proceeds should work under the same 100% rule, but the stock sale itself must not be a BTST sale.

### Gaps
- The date and circular number behind Groww's switch from 80% to 100% were not found; Groww's own pages are inconsistent. Confirm with a small live test.
- Zerodha's page on proceeds from T1 holdings says credit is usable only after early pay-in, from the next trading day — [Zerodha support](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-holdings/articles/t1-holdings-proceeds); broker practice differs, so Groww behaviour should not be inferred from Zerodha.
- Whether Groww's API exposes updated buying power immediately after a sell fill was not researched.
- The new SEBI price-band percentages for liquid/overnight ETFs (from 1 Sep 2026) were not found.

---

## 4. Tax after 1 April 2023 (one paragraph; a separate researcher covers tax)

### Takeaway
Liquid ETFs are "specified mutual funds" under Section 50AA: any gain on units bought on or after 1 Apr 2023 is short-term and taxed at slab rate whatever the holding period, and IDCW dividends are slab-rate income with TDS above the annual threshold; no change for this category was found in the 2026 Budget summary.

### Cited Findings
- "Liquid ETFs and Liquid BeES are classified as specified mutual funds under Section 50AA of the Income-tax Act"; for units acquired on or after 1 Apr 2023 gains are deemed short-term "irrespective of your holding period" and taxed at slab rate; dividend units are "Income from Other Sources" at slab rate, with TDS above "the prescribed threshold" — [Zerodha support](https://support.zerodha.com/category/console/reports/taxation/articles/dividends-on-liquid-etfs-and-liquid-bees)
- Budget 2024 (July): debt-oriented units acquired before 1 Apr 2023 and sold on or after 23 Jul 2024 get 12.5% LTCG after 24 months; units acquired on or after 1 Apr 2023 remain at slab rate with no holding-period benefit; a fund must hold no more than 65% in debt and money market instruments to qualify for the 12.5% treatment — [Zerodha support: MF taxation](https://support.zerodha.com/category/mutual-funds/understanding-mutual-funds/about-mutual-funds/articles/how-does-taxation-work-for-mutual-fund-investments)
- TDS threshold on mutual fund income rose from Rs 5,000 to Rs 10,000 from 1 Apr 2025 — [India Briefing](https://india-briefing.com/news/a-guide-to-indias-tds-rates-for-fy-2025-26-36999.html) (search snippet, page not opened)
- Budget 2026 highlights list buybacks taxed as capital gains and STT on futures raised to 0.05%; nothing on debt fund taxation — [Groww blog, 2 Feb 2026](https://groww.in/blog/union-budget-2026-key-highlights)
- Conflict: Groww's own explainer pages say liquid ETF tax "is similar to stocks", with 12.5% LTCG after one year and a Rs 1.25 lakh exemption — [Groww Liquid ETF page](https://groww.in/p/liquid-etf), [Groww blog, 10 Jul 2025](https://groww.in/blog/difference-between-liquid-funds-and-liquid-etfs); this contradicts the Section 50AA treatment described by Zerodha.

### Inferences
- The Zerodha/Section 50AA reading is the one consistent with the law for a fund that is 100% in overnight debt; the Groww explainer appears to be wrong and should not be relied on.
- For the backtest, tax the cash leg's entire return at the investor's slab rate in the year of sale (growth ETF) or year of accrual (IDCW).

### Gaps
- Section numbers under the new Income-tax Act 2025 (in force from 1 Apr 2026) and any 2025-2026 change to the specified-mutual-fund definition were not verified; left to the tax researcher.

---

## 5. Year-by-year return on cash in India, 2008 to 2026 YTD

### Takeaway
Overnight cash returned between 3.1% (2021) and 8.2% (2012-2014) a year and averaged about 6.3% since 2011; liquid funds earned about 1 percentage point more in most years (range 0.2 in 2021-2022 to 2.1 in 2009). Official Nifty 1D Rate calendar-year figures were obtainable only for 2022-2025; earlier years are filled with actual overnight-fund returns and clearly marked estimates.

### Cited Findings

**Calendar-year table (percent)**

| Year | (a) Nifty 1D Rate Index | (a2) HDFC Overnight Fund Reg-Growth, actual | (b) Nifty Liquid Index | (b2) Mean of 4 large liquid funds, Reg-Growth, actual | (c) Avg repo rate | (d) LIQUIDBEES, estimate |
|---|---|---|---|---|---|---|
| 2008 | index starts 2011 | 7.54 | n/a | 9.16 | 8.01 | ~6.9 est. |
| 2009 | - | 3.34 | n/a | 5.46 | 4.92 | ~2.7 est. |
| 2010 | - | 4.73 | n/a | 5.35 | 5.47 | ~4.1 est. |
| 2011 | ~7.6 est. | 7.46 | n/a | 8.92 | ~7.5 unverified | ~6.9 est. |
| 2012 | ~8.3 est. | 8.24 | n/a | 9.68 | ~8.15 unverified | ~7.6 est. |
| 2013 | ~8.3 est. | 8.21 | n/a | 9.28 | ~7.5 unverified | ~7.6 est. |
| 2014 | ~8.3 est. | 8.16 | n/a | 9.13 | 7.98 | ~7.6 est. |
| 2015 | ~7.4 est. | 7.29 | 8.16 derived | 8.35 | 7.28 | ~6.7 est. |
| 2016 | ~6.5 est. | 6.41 | 7.42 derived | 7.65 | 6.50 | ~5.8 est. |
| 2017 | ~6.0 est. | 5.90 | 6.43 derived | 6.64 | 6.15 | ~5.3 est. |
| 2018 | 6.15 derived | 6.12 | 7.35 derived | 7.37 | 6.25 | ~5.5 est. |
| 2019 | 5.77 derived | 5.55 | 6.50 | 6.63 | 5.74 | ~5.1 est. |
| 2020 | 3.41 derived | 3.24 | 4.23 | 4.23 | 4.33 | ~2.7 est. |
| 2021 | 3.28 derived | 3.07 | 3.49 | 3.23 | 4.00 | ~2.6 est. |
| 2022 | 4.78 | 4.54 | 5.06 | 4.76 | 4.90 | ~4.1 est. |
| 2023 | 6.76 | 6.56 | 7.18 | 7.01 | 6.50 | ~6.1 est. |
| 2024 | 6.75 | 6.59 | 7.45 | 7.34 | 6.50 | ~6.0 est. |
| 2025 | 5.81 | 5.68 | 6.61 | 6.50 | 5.79 | ~5.1 est. |
| 2026 YTD | 4.31 (to 30 Oct) | 4.39 (to 10 Nov) | n/a | 5.55 (to 10 Nov) | 5.25 (see note) | ~3.7 est. (to 30 Oct) |

Sources and method, column by column:

- (a) 2022-2025: one-year return of "NIFTY 1D Rate Index" in the December fixed income dashboards — [Dec 2022](https://www.niftyindices.com/Index_Dashboard_Fixed_Income/Index_Dashboard_FixedIncome_DEC2022.pdf) (1Y 4.78, 3Y 3.82, 5Y 4.67), [Dec 2023](https://www.niftyindices.com/Index_Dashboard_Fixed_Income/Index_Dashboard_FixedIncome_DEC2023.pdf) (6.76, 4.93, 4.79), [Dec 2024](https://www.niftyindices.com/Index_Dashboard_Fixed_Income/Index_Dashboard_FixedIncome_DEC2024.pdf) (6.75, 6.09, 4.98), [Dec 2025](https://www.niftyindices.com/Index_Dashboard_Fixed_Income/Index_Dashboard_FixedIncome_DEC2025.pdf) (5.81, 6.44, 5.46). 2026 YTD 4.31% to 30 Oct 2026 — [factsheet](https://www.niftyindices.com/Factsheet/Factsheet_Nifty_1D_Rate.pdf). One-year return to 31 Oct 2026: 5.25% — [Oct 2026 dashboard](https://www.niftyindices.com/Index_Dashboard_Fixed_Income/Index_Dashboard_FixedIncome_OCT2026.pdf)
- (a) 2018-2021 "derived": backed out by me from the 3-year and 5-year CAGRs in those same four dashboards. Cross-checks reproduce the published 5Y to Dec 2024 (4.98) and Dec 2025 (5.46). Rounding error about +/-0.1.
- (a) 2011-2017 "est.": HDFC Overnight Reg-Growth plus 0.10. Basis: the index's since-inception CAGR of 6.27% (3 Jan 2011 to 30 Oct 2026) implies about 7.48% a year for 2011-2017 once 2018-2026 are removed, against 7.38% for the fund. Error about +/-0.15 in any single year.
- (a2) Computed from AMFI NAV of HDFC Overnight Fund Regular-Growth (scheme earlier named HDFC Cash Management Fund - Call Plan), 31 Dec to 31 Dec, face-value change of 30 Aug 2015 adjusted — [AMFI NAV 101996](https://api.mfapi.in/mf/101996). Direct plan from 2013: 8.27, 8.21, 7.37, 6.48, 5.96, 6.19, 5.66, 3.35, 3.17, 4.64, 6.67, 6.66, 5.76, and 4.47 for 2026 to 10 Nov — [AMFI NAV 119110](https://api.mfapi.in/mf/119110). This fund has had no negative daily NAV change since 2007.
- (b) 2019-2025: one-year return of "NIFTY Liquid Index" in December dashboards — [Dec 2019](https://www.niftyindices.com/Index_Dashboard_Fixed_Income/Index_Dashboard_FixedIncome_DEC2019.pdf) (1Y 6.50, 3Y 6.76, 5Y 7.17), [Dec 2020](https://www.niftyindices.com/Index_Dashboard_Fixed_Income/Index_Dashboard_FixedIncome_DEC2020.pdf) (4.23, 6.02, 6.38), [Dec 2021](https://www.niftyindices.com/Index_Dashboard_Fixed_Income/Index_Dashboard_FixedIncome_DEC2021.pdf) (3.49, 4.73, 5.59), and the 2022-2025 dashboards above (5.06, 7.18, 7.45, 6.61). 2015-2018 derived by me from the 3Y/5Y CAGRs. Nifty Liquid Index A-I: 4.95 (2022), 7.16 (2023), 7.39 (2024), 6.50 (2025).
- (b2) Mean of calendar-year returns of four large liquid funds, Regular-Growth, computed from AMFI NAVs with face-value changes adjusted: [Nippon India Liquid 100851](https://api.mfapi.in/mf/100851), [HDFC Liquid 100868](https://api.mfapi.in/mf/100868), [ICICI Pru Liquid 103340](https://api.mfapi.in/mf/103340), [ABSL Liquid 100047](https://api.mfapi.in/mf/100047). The four funds are within 0.2 of each other in every year since 2011. Survivorship caveat: these are large survivors, not the category average.
- (c) Time-weighted average of the repo rate from the dated table at [Freefincal "RBI repo rate history", updated 20 Sep 2026](https://freefincal.com/rbi-repo-rate-history/) for 2008-2010 and 2014-2025, plus the 5 Dec 2025 cut to 5.25% from [Groww](https://groww.in/blog/rbi-repo-rate-cut). That table has no entries between 17 Mar 2011 (6.75%) and 3 May 2013 (7.25%), so it omits the 2011-2012 hikes and cuts; the 2011-2013 values shown are from my background knowledge and are unverified. The table also dates the move to 6.50% as 08-01-2023 (most likely 8 Feb 2023), which would make 2023 about 6.47. 2026: 5.25% confirmed to 5 Jun 2026 ([Groww](https://groww.in/blog/rbi-keeps-repo-rate-unchanged-maintains-neutral-stance-amidst-global-uncertainty)); later meetings not verified.
- (d) No sourced LIQUIDBEES total-return series was found. The estimate is column (a) (or a2 plus 0.1 before 2011) minus a 0.7% expense ratio, the current TER being 0.71% — [Groww LIQUIDBEES page, 9 Nov 2026](https://groww.in/etfs/reliance-etf-liquid-bees). It is pre-tax and ignores the dividend distribution tax that applied to LIQUIDBEES dividends before April 2020 (29.12% per [Freefincal, 15 Sep 2018](https://freefincal.com/liquid-funds-with-low-credit-risk/)).

**Growth liquid ETFs, actual NAV returns (percent)** — computed from AMFI NAVs listed in section 1

| ETF | CY2025 | 2026 YTD to 10 Nov |
|---|---|---|
| LIQUID1 (Kotak) | 5.61 | 4.29 |
| LIQUIDPLUS (Mirae) | 5.60 | 4.29 |
| LIQUIDCASE (Zerodha) | 5.52 | 4.24 |
| LIQUIDADD (DSP) | 5.49 | 4.22 |
| LIQUIDBETF (Bajaj) | 5.45 | 4.15 |
| LIQUIDSHRI (Shriram) | 5.37 | 4.05 |
| GROWWLIQID (Groww) | 5.37 | 4.03 |
| Index (Nifty 1D Rate) | 5.81 | 4.31 to 30 Oct |

**Financial-year figures (April to March, percent)** — computed from the same AMFI NAVs

| FY | HDFC Overnight Reg-Growth | Mean of 4 liquid funds Reg-Growth |
|---|---|---|
| 2007-08 | 6.95 | 8.28 |
| 2008-09 | 6.91 | 8.84 |
| 2009-10 | 3.11 | 4.63 |
| 2010-11 | 5.53 | 6.44 |
| 2011-12 | 8.03 | 9.34 |
| 2012-13 | 7.95 | 9.28 |
| 2013-14 | 8.39 | 9.51 |
| 2014-15 | 8.03 | 8.99 |
| 2015-16 | 7.09 | 8.23 |
| 2016-17 | 6.15 | 7.27 |
| 2017-18 | 5.90 | 6.73 |
| 2018-19 | 6.21 | 7.43 |
| 2019-20 | 5.09 | 6.20 |
| 2020-21 | 2.89 | 3.58 |
| 2021-22 | 3.15 | 3.35 |
| 2022-23 | 5.31 | 5.62 |
| 2023-24 | 6.67 | 7.17 |
| 2024-25 | 6.49 | 7.30 |
| 2025-26 | 5.35 | 6.12 |

### Inferences
- For the backtest's cash leg use column (a) where official or derived (2018 onward) and (a2) plus 0.1 before that, then subtract the chosen ETF's drag: about 0.25-0.30% for LIQUIDCASE-type ETFs, 0.7% for LIQUIDBEES. Before January 2024 no growth liquid ETF existed (Kotak's turned growth in July 2024), so a realistic pre-2024 cash leg is LIQUIDBEES at index minus 0.7%, with dividend tax.
- The overnight return tracks the average repo rate within about +/-0.5% in normal years. It ran well below repo in 2009 and 2020-2021 (surplus liquidity, overnight near reverse repo) and above it in 2013 (liquidity squeeze).
- Liquid funds beat overnight by about 1-1.5% a year in 2008-2019 (2.1% in 2009, 0.6-0.7% in 2010 and 2017), by almost nothing in 2021-2022, and by 0.7-1.1% in 2024-2026. An overnight-only ETF therefore gives up real yield versus a liquid mutual fund in exchange for same-day tradability and no credit risk.
- 2026 full-year overnight return is on course for about 5.1-5.2%, the lowest since 2022.

### Gaps
- CRISIL Liquid Fund Index / CRISIL Liquid Debt A-I Index year-by-year returns: not obtained (crisil.com blocked). Nifty Liquid Index and four-fund averages are used instead.
- Official Nifty 1D Rate calendar-year values for 2011-2021: the index's historical-data service on niftyindices.com returned errors and December dashboards before 2022 do not list the index. Values are derived or estimated as described.
- Overnight call / MIBOR / TREPS annual averages from RBI DBIE: not obtained (rbi.org.in blocked).
- 2011-2013 average repo rate needs a clean source; the Freefincal table is incomplete for that span.
- A sourced LIQUIDBEES total-return series (Nippon factsheet "dividend reinvested" returns) was not obtained.

---

## 6. Risks and traps

### Takeaway
The underlying overnight/TREPS portfolio has been essentially loss-free, so the real risks are execution risks: off-NAV prints from market orders in thin books, small new ETFs with a few lakh rupees of daily volume, and paying costs for parking periods that are too short. Liquid mutual funds, unlike overnight ETFs, did take credit and mark-to-market hits in 2017-2020.

### Cited Findings

**Off-NAV prints (the main trap)**

- On 11 Nov 2026 ICICI CASHIETF opened with a trade at Rs 1,109.85 against a NAV of about Rs 1,088.1 (a 2% overpayment, roughly five months of yield) before trading at Rs 1,088.23-1,088.24 — [Groww 1-minute candles CASHIETF](https://groww.in/v1/api/charting_service/v2/chart/exchange/NSE/segment/CASH/CASHIETF/daily?intervalInMinutes=1&minimal=false), [AMFI NAV 153378](https://api.mfapi.in/mf/153378)
- Sessions in the past year (about 249) with a trade more than 0.25% above / below that day's close: LIQUIDBEES 8 / 21 (extremes +2.5% / -3.0%), LIQUID1 32 / 25 (+3.0% / -2.0%), GROWWLIQID 27 / 23 (+2.0% / -2.0%), AONELIQUID 18 / 7, LIQGRWBEES 17 / 12, HDFCLIQUID 14 / 16, SBILIQETF 14 / 15 (+5.0% / -2.5%), CASHIETF 14 / 8, LIQUIDPLUS 11 / 11, LIQUIDBETF 7 / 5 (+4.9% / -5.1%), LIQUIDADD 5 / 1, LIQUIDIETF 2 / 12 (+4.1% / -4.4%). LIQUIDCASE: 0 / 0 in 197 sessions, with no trade more than 0.02% from the close; LIQUIDSHRI 0 / 0 but on negligible volume — Groww daily candles, e.g. [LIQUIDCASE](https://groww.in/v1/api/charting_service/v2/chart/exchange/NSE/segment/CASH/LIQUIDCASE/1y?intervalInDays=1&minimal=false), [LIQUIDBEES](https://groww.in/v1/api/charting_service/v2/chart/exchange/NSE/segment/CASH/LIQUIDBEES/1y?intervalInDays=1&minimal=false), [LIQUID1](https://groww.in/v1/api/charting_service/v2/chart/exchange/NSE/segment/CASH/LIQUID1/1y?intervalInDays=1&minimal=false), [GROWWLIQID](https://groww.in/v1/api/charting_service/v2/chart/exchange/NSE/segment/CASH/GROWWLIQID/1y?intervalInDays=1&minimal=false)
- LIQUIDBEES traded as low as Rs 969.99 and as high as Rs 1,025 in the past year while closing at Rs 999.99-1,000.00 every day — [Groww candles LIQUIDBEES](https://groww.in/v1/api/charting_service/v2/chart/exchange/NSE/segment/CASH/LIQUIDBEES/1y?intervalInDays=1&minimal=false)
- Zerodha blocks market and SL-M orders in a list of ETFs from 9:15 to 9:17 AM "due to a lack of liquidity" — [Zerodha support](https://support.zerodha.com/category/trading-and-markets/alerts-and-nudges/kite-error-messages/articles/market-orders-for-etf-for-first-two-minutes)

**Premium/discount at the close, and days the price does not move**

- Closing price versus same-day NAV over the past year stayed within 5 bp on every session for LIQUIDCASE (range -1.3 to +4.3 bp), LIQUIDADD, LIQUIDPLUS, LIQUIDBETF, GROWWLIQID, CASHIETF, AONELIQUID, LIQGRWBEES and LIQUID1; the positive extremes are the pre-weekend/pre-holiday accrual described in section 3. Exceptions: SBILIQETF closed 50.5 bp above NAV on 1 Feb 2026, HDFCLIQUID 6.6 bp above on 8 Nov 2026 — computed from Groww candles and AMFI NAVs as in section 3
- LIQUIDCASE's close was unchanged from the previous close on 17 of 196 sessions and never lower; GROWWLIQID unchanged on 7 of 248. Among Rs 1,000-type ETFs the close fell on a few sessions (ELIQUID 4, LIQUIDSHRI 4, HDFCLIQUID 4, SBILIQETF 3) — same data
- Thin ETFs: median daily traded value over the last 60 sessions was Rs 0.009 crore (about Rs 93,000) for LIQUIDBETA, Rs 0.38 crore for ABSLLIQUID, Rs 0.44 crore for LIQUIDSBI, Rs 0.82 crore for LIQUIDSHRI; minimum-day value Rs 0.07 crore for ELIQUID and Rs 0.28 crore for HDFCLIQUID — Groww candles (section 1 table)

**Credit and mark-to-market events hit liquid funds, not overnight funds**

- 22 Feb 2017: Taurus Liquid Fund NAV fell 7.22% in a day — computed from [AMFI NAV 104241](https://api.mfapi.in/mf/104241); Freefincal links this to the Ballarpur bond downgrade — [Freefincal, 15 Sep 2018](https://freefincal.com/liquid-funds-with-low-credit-risk/)
- September 2018 (IL&FS): Principal Cash Management Fund NAV fell 2.31% (9 Sep), 1.60% (17 Sep) and 5.72% (24 Sep) — computed from [AMFI NAV 100898](https://api.mfapi.in/mf/100898); the NBFC crisis began in September 2018 "after IL&FS group companies defaulted on payments" — [Groww blog, 28 Nov 2019](https://groww.in/blog/sebi-regulations-stricter-rules-to-make-liquid-funds-safer-for-investors)
- March 2020: liquid fund category average fell 0.05% in a day and the worst fund (HSBC Cash) 0.14%; money market funds fell 0.37% on average in a day; "Only overnight funds have so far been spared", with the Nifty 1D Rate Index up 0.01% / 0.04% / 0.09% over 1 day / 3 days / 1 week — [Freefincal, 20 Mar 2020](https://freefincal.com/why-liquid-funds-and-money-market-funds-also-fell-in-the-last-few-days/)
- Large liquid funds' worst days since 2007: 16 Jul 2013 (Nippon -0.24%, HDFC -0.16%, ICICI -0.16%), 23 Mar 2020 (-0.07% to -0.11%), 19 Mar 2020 (-0.07% to -0.09%), 4 May 2022 (-0.03% to -0.04%, the day of the off-cycle repo hike to 4.40%) — computed from AMFI NAVs [100851](https://api.mfapi.in/mf/100851), [100868](https://api.mfapi.in/mf/100868), [103340](https://api.mfapi.in/mf/103340); hike date from [Freefincal repo table](https://freefincal.com/rbi-repo-rate-history/)
- HDFC Overnight Fund (since 2007) and Nippon India Overnight Fund (since Dec 2018) have had no negative daily NAV change — computed from AMFI NAVs [101996](https://api.mfapi.in/mf/101996), [145810](https://api.mfapi.in/mf/145810)
- The six Franklin Templeton schemes wound up in April 2020 were low duration, ultra short, short term, credit risk, dynamic accrual and income opportunities funds; no liquid or overnight fund was among them — [Freefincal, 23 Apr 2020](https://freefincal.com/franklin-wind-up-six-debt-mfs/)
- After 2018-19 SEBI required liquid funds to hold at least 20% in cash equivalents, cut single-sector exposure to 20%, moved valuation to mark-to-market, and added an exit load for exits within 7 days — [Groww blog, 28 Nov 2019](https://groww.in/blog/sebi-regulations-stricter-rules-to-make-liquid-funds-safer-for-investors)
- To minimise all kinds of risk, "stick to overnight mutual funds" — [Freefincal, 15 Sep 2018](https://freefincal.com/liquid-funds-with-low-credit-risk/)

**TER differences**

- LIQUIDBEES 0.71% versus 0.21% (Mirae LIQUIDPLUS, Bajaj LIQUIDBETF), 0.22% (Edelweiss), 0.24% (Kotak), 0.25% (HDFC, Nippon growth), 0.26% (ICICI growth), 0.28% (Zerodha), 0.31% (DSP LIQUIDADD), 0.38% (Groww), 0.52% (Shriram) — Groww ETF pages, 9 Nov 2026 (links in section 1)

### Inferences
- Bot rules that follow from the data: limit orders only, never market orders; price the limit at the last close plus or minus one or two ticks (or the current best bid/ask) and never more than about 5 bp from the previous NAV; avoid the first two minutes after 9:15; skip any ETF whose median traded value is below about 50 times the order size.
- LIQUIDCASE's clean record probably reflects deep two-sided quotes at a Rs 0.01 tick on a Rs 117 unit, where one tick is 0.86 bp and market-maker quoting is profitable. The cost is that one tick is 9 times larger in bp than on a Rs 1,000 unit; on Rs 10 lakh that is about Rs 86 versus Rs 9 per round trip, small against the risk of a 2% freak fill elsewhere.
- LIQUIDBEES combines the highest TER, daily dividend income, fractional units and frequent low prints (21 sessions with trades more than 0.25% below the close). It is the weakest fit for an automated delivery bot despite its depth.
- An overnight ETF carries no meaningful credit or duration risk; the residual risks are operational (exchange or broker outage on the day cash is needed, a settlement holiday delaying credit) and regulatory (tax or price-band rule changes).
- Sceptical bottom line: at 5.2% and Groww's charges, parking Rs 1 lakh for under a week loses money, and a month earns about Rs 330 before tax. The benefit only becomes material for balances of several lakh held for weeks, which is roughly Rs 400-430 a month per Rs 1 lakh before costs and tax.

### Gaps
- The causes of the Taurus (2017) and Principal (2018) NAV drops are attributed from Freefincal/Groww context; the specific issuer exposures were not verified from fund disclosures. A -37% move in the Principal series on 24 Mar 2013 looks like a data/plan artefact and was ignored.
- DHFL (June 2019) effects on specific liquid funds were not researched.
- Intraday indicative NAV (iNAV) availability for these ETFs through Groww was not checked.
- Whether any growth liquid ETF has ever closed materially below NAV for more than a day before November 2025 was not tested (only one year of price history was pulled).
