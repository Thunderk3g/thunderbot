# Live (since-launch) performance of Indian momentum and factor ETFs / index funds vs Nifty 50 and Nifty 200 (as of 10 Nov 2026)

> **Read this first: evidence quality and access limits.**
> - This session could not open any web page. Direct fetches failed (`www.niftyindices.com` and `api.mfapi.in` are outside the session's allowed network domains; `curl` got 403 from the proxy for AMFI, Yahoo and AMC hosts). The shared web-search budget (200 calls per turn across all agents) ran out after 19 searches.
> - So every figure tagged **[snippet]** below comes from a search-result summary, not a page I read. Treat these as leads to verify, especially where aggregator sites disagree.
> - Figures tagged **[prior notes]** were read from the primary source in the 23 Oct 2026 session and are carried forward from `research_notes/Evidence based NSE trading strategies/momentum_factor_evidence.md`.
> - Figures tagged **[own computation]** are arithmetic on those sourced numbers. No NAV history could be downloaded, so nothing here is computed from raw NAVs.
> - Roughly half the brief (all non-momentum factor products, most ETF liquidity and tracking data, PMS/smallcase records, Nifty 50 TRI calendar years) could not be researched. Those items are listed under Gaps, not filled in.
> - Label convention: **BACKTEST** = index history before the index's launch date; **LIVE INDEX** = index TRI after launch; **LIVE FUND** = actual scheme NAV.

---

## Q1. Nifty200 Momentum 30 products: tickers, launch dates, TER, AUM, liquidity, tracking

### Takeaway
Five ETFs and at least eight index funds track Nifty200 Momentum 30, but the money is in one product: UTI's index fund (about ₹7,962 cr at 30 Sep 2026) holds roughly two-thirds of the category. The ETFs are small (about ₹33 cr to ₹155 cr, ICICI about ₹550 cr on an undated figure), and two tickers in the brief were wrong: `MOMENTUM` is Aditya Birla Sun Life's ETF, ICICI's is `MOM30IETF`, and Kotak's is `MOMENTUM30`. Disclosed tracking error is 0.17–0.52% a year; the one tracking-difference figure found (ICICI ETF) is −0.63% since inception.

### Cited Findings

**ETF tickers (verified against multiple listings) [snippet]**

| ETF | NSE symbol | Launch | TER | AUM | Tracking |
|---|---|---|---|---|---|
| Motilal Oswal Nifty 200 Momentum 30 ETF | `MOMOMENTUM` | Feb 2022 (per brief; not re-verified) | 0.30–0.36% | ₹125–154 cr (₹154.33 cr at 24 Aug 2026) | not found |
| ICICI Prudential Nifty 200 Momentum 30 ETF | `MOM30IETF` (ISIN INF109KC17C7) | 4 Aug 2022 | 0.30% | ₹552–557 cr (undated; ₹233 cr at 30 Jun 2024) | TD −0.63% since inception, −0.47% 1y; TE 0.25% (1y), 0.26% (3y), at 31 Aug 2026 |
| Aditya Birla SL Nifty 200 Momentum 30 ETF | `MOMENTUM` (BSE 543575) | not found | 0.17% (AMC page); 0.22% (TradingView) | ₹38–47.5 cr | not found |
| HDFC NIFTY200 Momentum 30 ETF | `HDFCMOMENT` | Oct 2022 (per brief; not re-verified) | 0.30% | ₹87–102 cr | 1y TE 0.17% at 27 Feb 2026 [prior notes] |
| Kotak Nifty200 Momentum 30 ETF | `MOMENTUM30` | not found | 0.26% (factsheets Jul and Sep 2026) | ₹33–36 cr | TE 0.27% at 30 Sep 2026; 0.32% in Jun 2026 |

- Symbols: Motilal `MOMOMENTUM`, ICICI `MOM30IETF`, ABSL `MOMENTUM`, HDFC `HDFCMOMENT`, Kotak `MOMENTUM30`. — [Groww Motilal](https://groww.in/etfs/motilal-oswal-nifty-momemtum-etf-a-scheme-under-motilal-oswal-mutual-fund); [TradingView MOM30IETF](https://in.tradingview.com/symbols/NSE-MOM30IETF/analysis); [ABSL AMC page](https://mutualfund.adityabirlacapital.com/empower/Passive-ETFs/Nifty-200-Momentum-30-ETF.html); [Groww HDFC](https://groww.in/etfs/hdfc-nifty-momentum-etf); [Kotak factsheet, Sep 2026](https://www.kotakmf.com/factsheet/sept_2026/kotak/Download_pdf/Kotak%20Nifty200%20Momentum%2030%20ETF_Factsheet%20One%20Pager.pdf)
- ICICI ETF: launch 4 Aug 2022; AUM about ₹552.39 cr (undated); its own description cites ₹233.13 cr at 30 Jun 2024. — [Upstox ICICI ETF page](https://upstox.com/etfs/icicipramc-icicimom30-share-price/INF109KC17C7/). Choice lists ₹557 cr and a 0.86% expense ratio; the 0.86% conflicts with every other source and looks wrong. — [Choice](https://choiceindia.com/mutual-funds/icici-prudential-nifty-200-momentum-30-etf-growth)
- ICICI ETF tracking difference −0.63% since inception and −0.47% over 1 year; tracking error 0.25% (1y) and 0.26% (3y), as of 31 Aug 2026. — [ICICI Pru AMC factsheet](https://www.icicipruamc.com/blob/knowledgecentre/factsheet-schemes/Passive%20Schemes/ETFs%20Schemes/ICICI%20Prudential%20Nifty%20200%20Momentum%2030%20ETF.pdf)
- Kotak ETF: TE 0.27% and TER 0.26% at 30 Sep 2026; TE 0.32% in the June 2026 factsheet. — [Kotak, Sep 2026](https://www.kotakmf.com/factsheet/sept_2026/kotak/Download_pdf/Kotak%20Nifty200%20Momentum%2030%20ETF_Factsheet%20One%20Pager.pdf); [Kotak, Jun 2026](https://www.kotakmf.com/factsheet/June_2026/kotak/Download_pdf/KOTAK%20NIFTY200%20MOMENTUM%2030%20ETF.pdf)
- Motilal ETF: AUM ₹154.33 cr at 24 Aug 2026; other pages ₹125.50–134 cr; TER 0.31–0.36%; NAV ₹62.38 at 3 Aug 2026. One page shows 1.28% TER, an outlier. — [Upstox Motilal](https://upstox.com/etfs/motilalamc-momomentum-share-price/INF247L01BK2/); [Value Research](https://www.valueresearchonline.com/funds/42039/motilal-oswal-nifty-200-momentum-30-etf/); [Choice](https://choiceindia.com/mutual-funds/motilal-oswal-nifty-200-momentum-30-etf-growth)
- HDFC ETF AUM ₹87–102 cr, TER 0.3%. — [Groww](https://groww.in/stocks/hdfc-nifty-momentum-etf); [Choice](https://choiceindia.com/mutual-funds/hdfc-nifty200-momentum-30-etf-growth)
- ABSL ETF: AMC page shows 0.17% and ₹47.50 cr; Groww shows 0.67% and ₹38 cr (conflict; AMC page preferred). — [ABSL AMC](https://mutualfund.adityabirlacapital.com/empower/Passive-ETFs/Nifty-200-Momentum-30-ETF.html); [Groww ABSL](https://groww.in/stocks/aditya-birla-sun-life-nifty-momentum-etf)
- Kotak ETF AUM ₹33–36 cr. — [Groww Kotak](https://groww.in/stocks/kotak-nifty-200-momentum-30-etf-ltd); [Choice Kotak](https://choiceindia.com/mutual-funds/kotak-nifty-200-momentum-30-etf-growth-140519562-2066)

**Index funds [snippet unless marked]**
- **UTI Nifty200 Momentum 30 Index Fund** (the first product): launched 10 Mar 2021 (one site says 11 Mar); AUM ₹7,961.68 cr at 30 Sep 2026 (AMFI, via AdvisorKhoj). — [AdvisorKhoj](https://www.advisorkhoj.com/mutual-funds-research/UTI-Nifty-200-Momentum-30-Index-Fund-Regular-Plan-Growth-Option); launch reported in [Business Standard, Feb 2021](https://www.business-standard.com/article/markets/uti-amc-launches-nifty-200-index-based-passively-managed-fund-121021901141_1.html)
  - AUM was ₹8,712 cr at 27 Feb 2026, so it fell about 9% in seven months. — [NSE whitepaper, Apr 2026, Exhibit 12](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf) [prior notes]
  - **TER is unresolved.** Aggregators show 0.43–0.45% (direct) up to 0.89%; UTI's own page was summarised as "Direct: 0.78, Regular: 1.25"; AdvisorKhoj shows 1.36% for regular. — [UTI MF page](https://www.utimf.com/mutual-funds/uti-nifty200-momentum-30-index-fund); [AdvisorKhoj](https://www.advisorkhoj.com/mutual-funds-research/UTI-Nifty-200-Momentum-30-Index-Fund-Regular-Plan-Growth-Option)
  - 1-year tracking error 0.17% at 27 Feb 2026. — [NSE whitepaper](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf) [prior notes]
- **Kotak Nifty 200 Momentum 30 Index Fund:** TE 0.20% in both the July and September 2026 factsheets. — [Kotak, Sep 2026](https://www.kotakmf.com/factsheet/sept_2026/kotak/NIFTY-200-MOMENTUM-30-INDEX-FUND.html)
- **Baroda BNP Paribas Nifty200 Momentum 30 Index Fund:** TE 0.48 for both plans (June 2026). Its NFO was in late September 2024, at the momentum peak. — [BBNPP factsheet, Jun 2026](https://www.barodabnpparibasmf.in/efactsheet/Jun2026/Innerpages/Nifty200-Momentum-30-Index-Fund.html); [Business Today, 24 Sep 2024](https://www.businesstoday.in/amp/personal-finance/investment/story/nfo-alert-baroda-bnp-paribas-nifty-200-momentum-30-index-fund-groww-nifty-india-defence-etf-details-here-447219-2024-09-24)
- **Motilal Oswal index fund:** highest 1-year TE in the category, 0.52% at 27 Feb 2026. — [NSE whitepaper](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf) [prior notes]
- **Others confirmed to exist:** Bandhan (launched as IDFC, NFO closed 26 Aug 2022), SBI, HDFC and ICICI index funds. — [Outlook Money](https://www.outlookmoney.com/news/idfc-mutual-fund-announces-new-nfo-issue-closes-on-august-26-news-217189); [5paisa SBI NFO](https://www.5paisa.com/news/sbi-nifty200-momentum-30-index-fund-nfo-launch-dates-investment-details-key-highlights); [HDFC leaflet, Jun 2026](https://files.hdfcfund.com/s3fs-public/Others/2026-06/Leaflet%20-HDFC%20NIFTY200%20Momentum%2030%20Index%20Fund%20%28June%202026%29.pdf); [PersonalFN ICICI index fund](https://www.personalfn.com/mutual-funds/best-funds/factsheet/icici-pru-nifty-200-momentum-30-index-fund-idcw-direct-plan)
- **Category size at 27 Feb 2026:** 13 Nifty200 Momentum 30 funds with about ₹12,523 cr; 24 passive funds on all NSE momentum indices with about ₹17,667 cr. — [NSE whitepaper, Exhibit 12](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf) [prior notes]

### Inferences
- UTI holds about 70% of Nifty200 Momentum 30 assets (₹8,712 cr of ₹12,523 cr at Feb 2026). For a retail investor the index fund, not an ETF, is the liquid route: four of the five ETFs have under ₹160 cr.
- The ICICI ETF's −0.63% since-inception tracking difference (assumed annualised, as AMC factsheets normally report it) against a roughly 0.30% TER implies about 0.3 points a year of cost beyond the fee (transaction costs, cash drag). That is the only hard number found for "all-in" slippage of a live momentum product.
- The regular-plan UTI fund trailed the index by 0.5–1.2 points in each calendar year 2022–2025 (see Q3), consistent with a regular TER near 1%.

### Gaps
- **Average traded value for any ETF: not found.** No bid-ask spread or iNAV premium/discount data either.
- Tracking difference (1y, 3y, since inception) for UTI, Motilal, HDFC, Kotak, ABSL, Bandhan, SBI, Baroda: not found. Only ICICI ETF's TD was retrieved.
- Direct-plan TERs for index funds: not reliably established for any fund. UTI's is contradictory (0.43% to 0.78%).
- Launch dates for the ABSL and Kotak ETFs and the Kotak, SBI, HDFC and ICICI index funds were not retrieved. From memory (unverified): ABSL ETF Aug 2022, Kotak index fund mid-2023, HDFC index fund early 2024.
- Whether Mirae (Nifty200 Alpha 30, `ALPHAETF`), Nippon, Zerodha, Tata, Groww or Edelweiss run Nifty200 Momentum 30 products: not researched.

---

## Q2. Other factor products (midcap/500 momentum, alpha, low-vol, quality, value, multi-factor, active momentum funds, PMS and smallcases)

### Takeaway
Almost nothing new could be retrieved here, so this question is largely unanswered. The one product with fresh data is the actively managed Samco Active Momentum Fund (launched July 2023): it trails its category, and its drawdown that began on 3 Jan 2025 reached −23% in April 2026 and had not recovered by August 2026.

### Cited Findings
- **Samco Active Momentum Fund** (LIVE FUND; benchmark Nifty 500 TRI; launched around July 2023) [snippet]:
  - Trails its Equity: Thematic category peers as on 20 Aug 2026; rated 2.41/5 by one analysis site.
  - Maximum drawdown −23.06%, peak 3 Jan 2025 to trough 3 Apr 2026, not yet recovered.
  - Worst 1-year rolling return −18.67%; 52.9% of 701 one-year rolling periods were negative.
  - Source: [Arthgyaan](https://arthgyaan.com/fund/samco-active-momentum-fund-direct-growth-option/151753) (most likely source of these statistics among the results; not opened)
  - Since-inception CAGR is reported inconsistently: 16.43% (direct), 12.52% (regular), and 9.45% (regular, as of Feb 2026). Direct-plan 1-year return −1.11% (undated). — [Sharpely](https://sharpely.in/mutual-funds/samco-active-momentum-fund-directgrowth/43515/performance); [Choice](https://choiceindia.com/mutual-funds/samco-active-momentum-fund-growth)
- **Capitalmind:** its Momentum PMS has been live since 2019. The company reported a post-fee CAGR of 29.14% for the five years ending 31 Jul 2024. That is self-reported and ends before the slump; no 2025–26 figures were found. — [Capitalmind blog](https://www.capitalmind.in/blog/best-pms-capitalmind-pms-strategies-performance) [snippet]
- **Factor index snapshot at 30 Sep 2026** (LIVE INDEX for the 1y and 5y columns, all TRI) [prior notes]:

  | Index | 1y TR | 5y TR CAGR | Index launch |
  |---|---|---|---|
  | Nifty200 Momentum 30 | −0.47% | 9.28% | 25 Aug 2020 |
  | Nifty Midcap150 Momentum 50 | 4.08% | 15.13% | 16 Aug 2022 (so ~1 year of the 5y is back-test) |
  | Nifty Alpha 50 | 11.44% | 12.03% | 19 Nov 2012 |
  | Nifty Alpha Low-Volatility 30 | −1.91% | 8.57% | 10 Jul 2017 |
  | Nifty200 Quality 30 | −5.42% | 6.40% | 17 Apr 2018 |
  | Nifty100 Low Volatility 30 | −4.68% | 8.12% | not confirmed |
  | Nifty 50 TRI | −7.09% | 6.37% | — |

  Sources: NSE factsheets for each index, e.g. [Momentum 30](https://www.niftyindices.com/Factsheet/Factsheet_Nifty200_Momentum30.pdf), [Midcap150 Momentum 50](https://www.niftyindices.com/Factsheet/Factsheet_NiftyMidcap150Momentum50.pdf), [Alpha 50](https://www.niftyindices.com/Factsheet/Factsheet_Nifty_Alpha50.pdf), [Alpha Low-Vol 30](https://www.niftyindices.com/Factsheet/Factsheet_NIFTY_Alpha_Low-Volatility_30.pdf), [Quality 30](https://www.niftyindices.com/Factsheet/Factsheet_NIFTY200_Quality30.pdf); Low Vol 30 and Nifty 50 TRI from the [ICICI Pru Nifty 100 Low Vol 30 ETF factsheet, Sep 2026](https://www.icicipruamc.com/blob/knowledgecentre/factsheet-schemes/Passive%20Schemes/ETFs%20Schemes/ICICI%20Prudential%20Nifty%20100%20Low%20Volatility%2030%20ETF.pdf)
- **ICICI Pru Nifty 100 Low Vol 30 ETF** (oldest low-vol product): over the ETF's life to 30 Sep 2026, 12.38% CAGR vs 11.03% for Nifty 50 TRI. The earlier notes did not record whether 12.38% is the scheme or its benchmark, nor the inception date (implied about 9.2 years). — [ICICI factsheet, Sep 2026](https://www.icicipruamc.com/blob/knowledgecentre/factsheet-schemes/Passive%20Schemes/ETFs%20Schemes/ICICI%20Prudential%20Nifty%20100%20Low%20Volatility%2030%20ETF.pdf) [prior notes]
- **Value and low-vol led in 2025:** a Mint article of 10 Nov 2025 reported value and low volatility as the standout factors of 2025. — [Mint via Magzter](https://www.magzter.com/de/stories/newspaper/Mint-Chennai/SMARTBETA-FUNDS-AIM-FOR-SMARTER-RETURNS-BUT-DO-THEY-REALLY-DELIVER) [snippet]
- **Midcap momentum marketing claim:** Nifty Midcap150 Momentum 50 beat midcap active funds in 100% of 7-year windows (Business Today, Jul 2025). This is a mostly back-tested index compared against live funds, so it is not live evidence. — [Business Today](https://www.businesstoday.in/mutual-funds/story/smart-beta-trumps-active-funds-over-all-7-year-cycles-in-mid-small-cap-segments-expert-explains-485695-2025-07-22) [snippet]

### Inferences
- Over the five years to 30 Sep 2026 every NSE factor index above beat Nifty 50 TRI (6.37%), but by widely different margins: midcap momentum +8.8 points, Alpha 50 +5.7, Momentum 30 +2.9, Alpha Low-Vol +2.2, Low Vol +1.8, Quality roughly nil. These are index TRIs; funds earn less after costs.
- An active momentum fund did not avoid the slump. Samco's drawdown started later (Jan 2025) and was still open 19 months on, so "active" was no protection in the one live case found.

### Gaps
- **Not researched at all (search budget exhausted):** tickers, launch dates, TER, AUM and returns for Nifty Midcap150 Momentum 50 funds (Tata index fund, Kotak/Edelweiss/Mirae ETFs), Nifty500 Momentum 50 (Motilal `MOMENTUM50`, Bandhan, Edelweiss), Nifty Smallcap250 Momentum Quality 100, Nifty Alpha 50 (Kotak `ALPHA`, Bandhan, Nippon), Alpha Low-Vol 30 (ICICI `ALPL30IETF`, Nippon, Kotak, UTI), Low Vol 30 (`LOWVOLIETF`, Kotak, UTI), Quality 30 (`SBIETFQLTY`, ICICI), Nifty 50 Value 20 (`NV20IETF`, `NV20BEES`), Nifty500 Value 50 (`MOVALUE`, UTI), and the multi-factor indices. The tickers in this bullet come from the brief and are unverified.
- Quant Momentum Fund: no data retrieved.
- Weekend Investing (Mi25/Mi50), Wright Momentum smallcase, Capitalmind Momentum PMS 2025–26: no audited live results found. Wright Research publishes monthly performance posts through July 2026 that were not opened. — [Wright Research blog index](https://www.wrightresearch.in/blog/quant/)
- Since-launch CAGR of the oldest Alpha Low-Vol 30 and Alpha 50 products vs Nifty 50: not found.

---

## Q3. Calendar-year returns 2021–2026 YTD: momentum index and UTI fund vs broad indices

### Takeaway
Nifty200 Momentum 30 had three winning and two losing calendar years against Nifty 200 since 2021 (+24.9, −10.4, +17.1, +6.6, −14.1 points), and the UTI fund tracked that pattern about 0.5–1.2 points lower in its regular plan. The table below is incomplete: Nifty 50, Nifty 500 and all non-momentum factor indices could not be sourced year by year.

### Cited Findings

**Calendar-year returns (%)**

| Year | Nifty200 Momentum 30 (index; LIVE INDEX; NSE whitepaper, PR/TR not stated, appears TR) | UTI Nifty200 Momentum 30 Index Fund (LIVE FUND; **regular** plan NAV) | Nifty 200 (index; implied = momentum − stated excess) | Nifty Midcap150 Momentum 50 (index; BACKTEST until 16 Aug 2022) | Nifty Midcap 150 (implied) |
|---|---|---|---|---|---|
| 2021 | 53.81 | launched 10 Mar 2021, no full year | 28.88 | not captured | not captured |
| 2022 | −5.45 | −5.95 | 4.91 | not captured | not captured |
| 2023 | 41.71 | 40.59 | 24.66 | 52.48 | 44.61 |
| 2024 | 21.33 | 20.36 | 14.75 | 32.30 | 24.47 |
| 2025 | −4.57 | −5.78 | 9.56 | −3.46 | 5.99 |
| 2026 YTD to 30 Sep | −4.65 (TR, NSE factsheet) | not found | not found | not found | not found |

- Index columns: [NSE whitepaper "The Science of Momentum", Apr 2026, Exhibit 7](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf) [prior notes]. 2026 YTD: [NSE factsheet, 30 Sep 2026](https://www.niftyindices.com/Factsheet/Factsheet_Nifty200_Momentum30.pdf) [prior notes].
- UTI fund column: 2022 −5.95% (category average +1.07%), 2023 +40.59%, 2024 +20.36%, 2025 −5.78%. The page is for the regular plan. — [ProfitGuru, UTI regular plan](https://www.profitguruonline.com/mutual-funds/scheme/uti-nifty-200-momentum-30-index-fund-regular-plan-growth-option-148704) [snippet]
- Motilal Oswal Nifty 200 Momentum 30 ETF (LIVE FUND) returned −5.69% in calendar 2025. — [ProfitGuru, Motilal ETF](https://www.profitguruonline.com/mutual-funds/scheme/motilal-oswal-nifty-200-momentum-30-etf-149801) [snippet]
- **Conflict:** Wright Research's index tracker shows 62.09% for 2021 and −12.09% for 2025, against the whitepaper's 53.81% and −4.57%. The funds' 2025 results (−5.7% to −5.8%) match the whitepaper, not Wright. — [Wright Research tracker](https://www.wrightresearch.in/track/index/nifty-200-momentum-30/) [snippet]

**Financial-year returns, TRI (LIVE INDEX from FY22)** [prior notes]

| FY | Nifty200 Momentum 30 TRI | Nifty 200 TRI | Nifty 50 TRI |
|---|---|---|---|
| FY22 | 37.7 | 21.4 | 20.3 |
| FY23 | −9.2 | −1.1 | 0.6 |
| FY24 | 70.0 | 38.3 | 30.1 |
| FY25 | −7.6 | 6.4 | 6.7 |
| FY26 | −3.4 | −2.8 | −4.0 |
| FY27 to 30 Jun 2026 | 14.4 | 10.9 | 7.4 |

Source: [HDFC AMC presentation, July 2026 (source NSE Indices)](https://files.hdfcfund.com/s3fs-public/Others/2026-07/HDFC%20NIFTY200%20Momentum%2030%20Index%20Fund_PPT%20%28July%202026%29.pdf)

### Inferences
- The whitepaper's calendar-year table is almost certainly total return: the regular-plan fund trails it by 0.50, 1.12, 0.97 and 1.21 points in 2022–2025, which fits a TRI less a regular-plan expense ratio [own computation].
- 2021–2025 compounded [own computation]: momentum index 19.0% a year vs 16.2% for Nifty 200 (+2.8 points). Drop 2021 and the picture reverses: 2022–2025 momentum 11.6% vs Nifty 200 13.2% (−1.6 points). An investor who bought after the first year has lagged a plain Nifty 200 fund for four calendar years.
- FY data has Nifty 50 alongside and is the only like-for-like three-way comparison available: momentum beat Nifty 50 in 3 of 5 completed FYs since launch of the first fund.

### Gaps
- **Nifty 50 TRI, Nifty 500 TRI and Nifty Midcap 150 TRI calendar-year returns: not sourced.** From memory and unverified: Nifty 50 TRI was about 25.6% (2021), 5.7% (2022), 21.3% (2023), 10.1% (2024). Verify before use.
- Calendar-year returns for Nifty500 Momentum 50, Alpha 50, Alpha Low-Vol 30, Low Vol 30 and Quality 30: not found.
- UTI **direct** plan calendar-year returns: not found (only regular).
- Nothing later than 30 Sep 2026 for index YTD. October 2026 factsheets were not accessible.

---

## Q4. Since-launch CAGR of the UTI fund vs Nifty 50 / Nifty 200 over the same period; 1y / 3y / 5y

### Takeaway
The UTI fund has compounded at roughly 14.5–15% a year in the direct plan and about 13% in the regular plan since March 2021. Over nearly the same window (Apr 2021–Jun 2026) the momentum TRI did 15.9% against 13.1% for Nifty 200 TRI and 11.0% for Nifty 50 TRI. All of that lead was earned by March 2024; since then the fund has lagged both.

### Cited Findings
- **Since inception (LIVE FUND)** [snippet; aggregator figures, dates differ]:
  - Direct plan: 14.75% CAGR since 11 Mar 2021 (undated). — [Sharpely](https://sharpely.in/mutual-funds/uti-nifty200-momentum-30-index-fund-directgrowth/41312/performance)
  - Direct plan: +114.36% absolute since launch, 1-year 1.92% (undated, around late Oct 2026). — [Paytm Money](https://www.paytmmoney.com/mutual-funds/scheme/uti-nifty200-momentum-30-index-fund-direct-g/inf789f1aut5)
  - Regular plan: 13.05% CAGR since inception; NAV ₹19.86. — [Dezerv](https://www.dezerv.in/mutual-funds/uti-nifty200-momentum-30-index-fund-regular-growth-inf789f1aus7/)
  - An unidentified aggregator page shows since-launch 15.10%, 3y 12.90% and 5y 10.69% as of 30 Jun 2026; another shows NAV 19.84 on 30 Oct 2026 with 3y CAGR 9.10%. The search tool did not say which page. Candidates: [5paisa](https://5paisa.com/mutual-funds/uti-nifty200-momentum-30-index-fund-direct-growth), [ClearTax](https://cleartax.in/mutual-funds/uti-mutual-fund/uti-nifty200-momentum-30-index-fund-direct/INF789F1AUT5), [INDmoney](https://indmoney.com/mutual-funds/fund/uti-nifty200-momentum-30-index-fund-direct-growth/1006372)
- **Trailing returns (LIVE FUND, direct)** as of mid-September 2026: 1y −3.39%, 3y 9.46%, 5y 8.72%. — [Univest](https://univest.in/blogs/uti-nifty200-momentum-30-index-fund-direct-growth-review-2026) [snippet]
- **Index trailing returns (LIVE INDEX, TRI)** [prior notes]:

  | As of | Period | Momentum 30 TRI | Nifty 200 TRI | Nifty 50 TRI |
  |---|---|---|---|---|
  | 30 Jun 2026 | 1y | −2.5% | −2.2% | −5.4% |
  | 30 Jun 2026 | 3y | 14.1% | 12.1% | 8.8% |
  | 30 Jun 2026 | 5y | 12.6% | 11.8% | 10.0% |
  | 30 Sep 2026 | 1y | −0.47% | not found | −7.09% |
  | 30 Sep 2026 | 5y | 9.28% | not found | 6.37% |

  Sources: [HDFC AMC presentation, July 2026](https://files.hdfcfund.com/s3fs-public/Others/2026-07/HDFC%20NIFTY200%20Momentum%2030%20Index%20Fund_PPT%20%28July%202026%29.pdf); [NSE factsheet, 30 Sep 2026](https://www.niftyindices.com/Factsheet/Factsheet_Nifty200_Momentum30.pdf)

### Inferences
- **Own computation from the FY table (TRI, 1 Apr 2021 – 30 Jun 2026, 5.25 years):** momentum 15.9% a year (₹1 → ₹2.17), Nifty 200 13.1% (₹1.90), Nifty 50 11.0% (₹1.73). This starts three weeks after the UTI fund's launch, so it is a close proxy for "since launch", before fund costs.
- **Split the period [own computation]:**
  - Apr 2021 – Mar 2024: momentum 28.6% a year vs 18.4% (Nifty 200) and 16.3% (Nifty 50).
  - Apr 2024 – Jun 2026: momentum +2.1% in total vs +14.7% (Nifty 200) and +10.0% (Nifty 50).
- **Cross-check of the fund figures [own computation]:** a regular NAV of 19.84 on 30 Oct 2026 from ₹10 on 10 Mar 2021 is 12.9% a year; +114.36% in the direct plan is 14.5% a year. Both agree with the aggregator CAGRs. The 1.5-point direct/regular gap is wider than the TER gap alone would give, so one of the two inputs is probably off-date.
- The fund's five-year numbers are sensitive to the start date: 5y to Jun 2026 was 12.6% (index), 5y to Sep 2026 only 9.28%, because the strong mid-2021 months dropped out of the window.

### Gaps
- No like-for-like figure for a Nifty 50 or Nifty 200 **index fund** over 10 Mar 2021 to date; the comparison above uses TRIs and so flatters neither side by fund costs.
- No verified direct-plan NAV series. `api.mfapi.in` and AMFI were unreachable, so the since-launch CAGR could not be computed from NAV history as planned.
- Since-launch CAGR for the oldest Alpha Low-Vol 30 and Alpha 50 products: not found. Low Vol 30: see Q2 (12.38% vs 11.03%, with caveats).
- Rolling-return statistics for the live period: not found.

---

## Q5. The 2024–25 momentum slump: depth, duration, relative lag, causes, methodology changes

### Takeaway
Nifty200 Momentum 30 fell 31.8% from 27 Sep 2024 to 7 Apr 2025, about twice the Nifty 50's 15.4% fall over the same dates, and it had still not regained its peak about two years later: it stood roughly 19% below on 4 Sep 2026. No evidence was found that NSE changed the rebalancing rules; its April 2026 study argued for keeping semi-annual rebalancing.

### Cited Findings
- **Peak and trough (LIVE INDEX):** drawdown began 27 Sep 2024 and troughed 7 Apr 2025 at −31.79%, 192 days peak to trough; still unrecovered as of August 2025. — [Wright Research](https://www.wrightresearch.in/blog/momentum-strategies-underperforming-2025-data-insights) [snippet]
- **Nifty 50 over the same dates:** −15.35%, against −31.79% for Nifty200 Momentum 30. — [DSIJ](https://insights.dsij.in/appmindshare/active-momentum-funds-timing-the-market-or-tapping-the-trend-51070) [snippet; the exact DSIJ article was not identified by the search tool]
- **Live fund confirmation:** Motilal Oswal Nifty 200 Momentum 30 ETF maximum drawdown −31.69%, Sep 2024 to Apr 2025. — [ProfitGuru](https://www.profitguruonline.com/mutual-funds/scheme/motilal-oswal-nifty-200-momentum-30-etf-149801) [snippet]
- **Early leg:** Nifty 200 Momentum 30 TRI fell 12.1% between 26 Sep and 14 Nov 2024. — [Value Research](https://www.valueresearchonline.com/stories/222422/why-momentum-funds-are-seeing-sharper-declines-amid-market-corrections/) [snippet]
- **Peak level and status two years on:** all-time high 38,115.25 on 27 Sep 2024 (CEIC data); 30,718.25 on 4 Sep 2026, about 19% below. — [Dealplexus, 28 Sep 2026](https://www.dealplexus.com/blog/momentum-funds-india) [snippet; secondary blog]
- **52-week range at 24 Oct 2025:** 25,133.95 – 35,490.75. — [Kotak Securities](https://www.kotaksecurities.com/indices/nifty200-momentum-30) [prior notes]
- **Relative lag:**
  - Calendar 2025: −4.57% vs about +9.6% for Nifty 200 (excess −14.13 points). — [NSE whitepaper, Exhibit 7](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf) [prior notes]
  - FY25: −7.6% vs +6.4% (Nifty 200 TRI) and +6.7% (Nifty 50 TRI). — [HDFC AMC, July 2026](https://files.hdfcfund.com/s3fs-public/Others/2026-07/HDFC%20NIFTY200%20Momentum%2030%20Index%20Fund_PPT%20%28July%202026%29.pdf) [prior notes]
  - Midcap150 Momentum 50 in 2025: −3.46% vs about +6.0% for Midcap 150 (excess −9.45). — [NSE whitepaper](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf) [prior notes]
- **Partial rebound in 2026:** 1 year to 30 Sep 2026, momentum −0.47% vs −7.09% for Nifty 50 TRI; FY27 to 30 Jun 2026, +14.4% vs +7.4%. — [NSE factsheet](https://www.niftyindices.com/Factsheet/Factsheet_Nifty200_Momentum30.pdf); [HDFC AMC](https://files.hdfcfund.com/s3fs-public/Others/2026-07/HDFC%20NIFTY200%20Momentum%2030%20Index%20Fund_PPT%20%28July%202026%29.pdf) [prior notes]
- **Other indices:**
  - Midcap150 Momentum 50 "down 24%" with simple momentum strategies "down around 30%" (undated, apparently early 2025). — [StockViz](https://stockviz.substack.com/p/costriskreturns-tradeoffs) [snippet]
  - Nifty Alpha 50 peak-to-trough fall of 17.7% over 2024–2026 vs 5.4% for Low Vol 30. — [Groww Digest](https://digest.groww.in/p/what-if-we-compare-the-calmest-stocks) [snippet]. The basis (daily or month-end, which dates) is unknown and 17.7% looks too small for a daily series.
- **Causes, as far as sourced:**
  - NSE itself places momentum's underperformance in the Jul 2024 – Oct 2025 "downward market phase". — [NSE whitepaper, Exhibit 5](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf) [prior notes]
  - Industry comment: momentum "struggled in the last two quarters as markets came off after hitting a peak in September 2024". — [Upstox](https://upstox.com/news/personal-finance/mutual-funds/smart-beta-funds-in-volatile-markets-how-11-schemes-with-over-500-crore-aum-stack-up/article-195604/) [snippet; attribution to this article is probable, not confirmed]
  - The June 2025 reconstitution replaced 20 of 30 stocks, a 67% churn by count, after the leadership change. — [Value Research](https://www.valueresearchonline.com/stories/225617/two-thirds-momentum-index-changes-just-one-day/) [snippet]
  - The December 2025 rebalance replaced another 19. — [Whalesbook](https://www.whalesbook.com/news/English/energy/Metas-Bold-India-Play-Whos-Now-Guiding-Public-Policy-in-This-Crucial-Market/693ef98fa3d7cdf72fb893c2) [snippet]
- **Methodology:**
  - The Business Standard piece of 14 Dec 2025 ("a flip of index switch jolts ₹16K cr") is about the routine half-yearly rebalance, not a rule change. — [Business Standard](https://www.business-standard.com/markets/news/nifty200-momentum30-a-flip-of-index-switch-jolts-16k-cr-across-the-grid-125121400388_1.html) [snippet]
  - NSE's April 2026 whitepaper tested quarterly against semi-annual rebalancing and found semi-annual better for Nifty200 Momentum 30 (19.19% vs 17.12% since 2005, back-tested). The September 2026 methodology document still specifies June and December. — [NSE whitepaper, Exhibits 8-10](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf); [NSE methodology document](https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf) [prior notes]

### Inferences
- **Recovery arithmetic [own computation]:** from 30,718 on 4 Sep 2026 the index needs +24% to regain 38,115. At 4 Sep 2026 the drawdown was 23 months old, which makes it the longest of the live era. Mirae's presentation (data to Jun 2026, prior notes) gives a "maximum recovery period" of 13.9 months for 2011–2026; that cannot include this still-open drawdown, so Mirae's figure presumably counts completed recoveries only.
- **Intraday vs close [own computation]:** a −31.79% close-to-close fall implies a trough near 25,998, while the 52-week low of 25,133.95 is −34.1% from the peak. The gap is probably the intraday low on 7 Apr 2025.
- **Cumulative lag since the slump began [own computation, TRI]:** Apr 2024 – Jun 2026 momentum +2.1% vs Nifty 200 +14.7% and Nifty 50 +10.0%, a shortfall of about 12.6 and 7.9 points.
- **Why it fell twice as far (reasoned, not sourced):** the index held its September 2024 leaders through the December 2024 review on six- and twelve-month scores that were still high, then turned over two-thirds of the book in June 2025 after the fall. Selling the fallen names and buying the new leaders after their move is the whipsaw cost of a semi-annual schedule. No source quantifies it, and NSE's own back-test says a quarterly schedule would have done worse over the long run.
- Momentum beat Nifty 50 over the year to Sep 2026 while both were negative, so the relative slump ended before the absolute one.

### Gaps
- Exact drawdown and dates for Midcap150 Momentum 50, Nifty500 Momentum 50 and Alpha 50 from the Sep 2024 peak: not found.
- Nifty 50 and Nifty 200 levels from 27 Sep 2024 to today: not sourced. One site (Chartrow) says Nifty 50 was 23.6% below its Sep 2024 high on 4 Sep 2026, which is hard to square with a −7.09% one-year TRI return to 30 Sep 2026; treat as unreliable. — [Chartrow](https://chartrow.com/nifty-50/drawdown)
- Sector attribution of the fall (PSU, defence, capital goods weights at Sep 2024): not retrieved. The Value Research article on sharper declines and Wright's "What's hurting momentum in 2025?" section were not readable.
- Whether NSE issued any consultation on quarterly rebalancing in 2025–26: searched once, nothing found, then the budget ran out. Absence here is weak evidence.
- Status after 30 Sep 2026 (October–November 2026): not available.

---

## Q6. Live vs back-test gap

### Takeaway
The live premium is real but about half the back-tested one. Nifty200 Momentum 30 beat Nifty 200 by about 5.6 points a year in the pre-launch back-test (2006–2019) and by about 2.8 points a year in the five full calendar years after launch (2021–2025), with all of it coming from 2021 and 2023. Indian commentators warned of this at launch, and international studies find the same decay.

### Cited Findings
- **Index dates:** base date 1 Apr 2005; launched 25 Aug 2020. — [NSE press release, 25 Aug 2020](https://niftyindices.com/Press_Release/ind_prs25082020.pdf); [NSE factsheet](https://www.niftyindices.com/Factsheet/Factsheet_Nifty200_Momentum30.pdf) [prior notes]
- **BACKTEST claim at launch:** NSE's September 2020 whitepaper said the index beat Nifty 200 in 13 of the last 16 calendar years. — [NSE whitepaper, Sep 2020](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/nifty200_momentum_30_index_whitepaper_sep_20.pdf) [snippet]
- **Blended record still marketed:** 18.8% CAGR vs 13.9% for Nifty 200 TRI, Apr 2005 – Jun 2026, about 15 of those 21 years being back-test. — [HDFC leaflet, Jun 2026](https://files.hdfcfund.com/s3fs-public/Others/2026-06/Leaflet%20-HDFC%20NIFTY200%20Momentum%2030%20Index%20Fund%20%28June%202026%29.pdf) [snippet]; [HDFC presentation](https://files.hdfcfund.com/s3fs-public/Others/2026-07/HDFC%20NIFTY200%20Momentum%2030%20Index%20Fund_PPT%20%28July%202026%29.pdf) [prior notes]
- **Year-by-year excess over Nifty 200** (source for the computation below): [NSE whitepaper, Apr 2026, Exhibit 7](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf) [prior notes]
- **Indian commentary:**
  - Freefincal's review of the UTI fund (Feb 2021, updated Aug 2025): the strategy may underperform the Nifty/Sensex over the long term, back-tested outperformance would likely be smaller in practice, and an investor starting with Nifty plus Nifty Next 50 does not need it. — [Freefincal](https://freefincal.com/uti-nifty200-momentum-30-index-fund/) [snippet]
  - PrimeInvestor's NFO review: hold it alongside Nifty 50 or Nifty 100, not in place of them. — [PrimeInvestor](https://primeinvestor.in/reports/is-uti-nifty-momentum-30-index-fund-nfo-worth-it/) [snippet]
  - Business Standard (Nov 2024): new factor index funds arrive with strong back-tested data, and any factor will underperform at times. — [Business Standard](https://business-standard.com/amp/finance/personal-finance/choice-of-momentum-factor-index-should-depend-on-performance-in-downturns-124110701113_1.html) [snippet]
  - Capitalmind (Sep 2021): "index performance is not investment performance", and index providers have an incentive to publish more indices. — [Capitalmind](https://premium.capitalmind.in/2021/09/best-nifty-factor-index-value-quality-alpha-momentum-lowvolatility-compared/) [snippet]
  - One analysis notes momentum and low-volatility funds "stumbled" in their first real market correction in India. — source not identified among [these results](https://www.icicidirect.com/research/equity/finace/all-you-need-to-know-about-how-factor-or-smart-beta-investing-works) [snippet; weak attribution]
- **International evidence on post-launch decay** [snippet]:
  - Morningstar: new indices beat their benchmarks by 1.4% a year in the five years before a fund tracks them, and by 0.39% a year afterwards. — [ETF Stream](https://www.etfstream.com/articles/index-outperformance-ends-when-funds-launch)
  - "The Smart Beta Mirage" (Journal of Financial and Quantitative Analysis): smart-beta indexes show a CAPM alpha of −0.44% a year over an average six-year post-listing period. — [Cambridge Core PDF](https://core-prod.cambridgecore.org/core/services/aop-cambridge-core/content/view/35CA1CEA091A485DDA960BB2D9930BC9/S0022109023000674a.pdf/smart_beta_mirage.pdf)

### Inferences
**Own computation from the whitepaper's calendar-year table (index returns; Nifty 200 implied from the stated excess):**

| Period | Status | Momentum 30 CAGR | Nifty 200 CAGR | Excess (geometric) | Average annual excess | Years ahead |
|---|---|---|---|---|---|---|
| 2006–2019 | BACKTEST (all pre-launch) | 17.5% | 11.9% | +5.6 | +6.8 | 11 of 14 |
| 2021–2025 | LIVE INDEX (full years after launch) | 19.0% | 16.2% | +2.8 | +4.8 | 3 of 5 |
| 2022–2025 | LIVE INDEX and first full fund years | 11.6% | 13.2% | −1.6 | −0.2 | 2 of 4 |

- The live excess is about half the back-tested one on a compounded basis (2.8 vs 5.6 points). Five years is far too short to call the premium gone or confirmed; two bad years out of five is within the back-test's own range (3 losing years in 14).
- Post-fund-launch (TRI, Apr 2021 – Jun 2026): +2.8 points a year over Nifty 200 and +4.9 over Nifty 50, before fund costs of roughly 0.5–0.7 points (TER plus tracking difference).
- The live hit rate (3 of 5) is below the launch claim (13 of 16).
- The live period was also a high-return period for everything (Nifty 200 at 16.2% vs 11.9% in the back-test window), so the absolute live CAGR of 19% flatters momentum; the excess is the honest measure.

### Gaps
- Since-launch (Aug 2020) point-to-point CAGR for the index vs Nifty 200 from an official source: not retrieved.
- The same live-vs-back-test split for Alpha 50 (launched Nov 2012), Alpha Low-Vol 30 (Jul 2017), Midcap150 Momentum 50 (Aug 2022) and Nifty500 Momentum 50 (2024): not done; calendar-year data was not available.
- No Indian study was found that systematically measures factor-index performance before and after launch. The search for a Freefincal article on that exact theme returned only international research. DSP Netra, Morningstar India and Value Research pieces on the topic were not found.
- A pre-existing inconsistency remains unresolved: the NSE whitepaper gives Nifty 200 a since-2005 return of 15.08% (to Feb 2026) while HDFC gives 13.9% (to Jun 2026).

---

## Q7. Impact cost and capacity: turnover, rebalance front-running, AUM

### Takeaway
The index replaces about 100–135% of its weight a year, and each half-yearly rebalance now forces roughly ₹8,000 cr of one-way trading by tracking funds on a date announced three weeks ahead. Nobody has published the resulting impact cost in basis points. Fund tracking differences will not show it, because the index itself absorbs the price pressure.

### Cited Findings
- **Index churn, semi-annual schedule (% of index weight replaced per year):** FY22 101, FY23 112, FY24 115, FY25 110, FY26 to 27 Feb 134. — [NSE whitepaper, Exhibit 11](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf) [prior notes]
- **Fund-level turnover:** portfolio turnover ratio of Nifty 200 Momentum 30 funds was 124.24% a year as of 31 May 2025. — [Value Research](https://www.valueresearchonline.com/stories/225617/two-thirds-momentum-index-changes-just-one-day/) [snippet]
- **June 2024 rebalance:** one-way turnover 42.3%, one-way trade about ₹3,200 cr (INR 32bn); the preview had estimated 49% and US$850m. — [Smartkarma review](https://smartkarma.com/insights/nifty200-momentum30-index-rebalance-13-changes-42-turnover-momentum-recovers-after-selloff); [Smartkarma preview](https://smartkarma.com/insights/nifty200-momentum30-index-rebalance-preview-49-turnover-us-850m-trade-election-results-coming) [snippet]
- **June 2025 rebalance:** about 20 changes; one-way turnover 68.4% including capping; round-trip trade about ₹16,000 cr (US$1.9bn). Announced 6 June, effective at the close on 27 June. — [Business Standard, Jun 2025](https://www.business-standard.com/markets/stock-market-news/nifty200-momentum-30-index-to-see-20-stock-changes-on-june-27-125062600872_1.html) [snippet]
- **December 2025 rebalance:** 19 constituents replaced, effective 30 December; round-trip ₹16,130 cr (US$1.8bn) per Brian Freitas of Periscope Analytics. Outflows of ₹103–647 cr per exiting stock and inflows of ₹159–628 cr per entrant. — [Business Standard, 14 Dec 2025](https://www.business-standard.com/markets/news/nifty200-momentum30-a-flip-of-index-switch-jolts-16k-cr-across-the-grid-125121400388_1.html); [Whalesbook](https://www.whalesbook.com/news/English/energy/Metas-Bold-India-Play-Whos-Now-Guiding-Public-Policy-in-This-Crucial-Market/693ef98fa3d7cdf72fb893c2) [snippet]
- **Reference point for costs:** Nifty 50 basket impact cost is 0.02% for ₹50 lakh; index eligibility requires impact cost of 0.50% or less for a ₹10 crore basket. — carried from `costs_and_taxes.md`: [NSE Nifty 50 page](https://www.nseindia.com/products-services/indices-nifty50-index); [Nifty 50 methodology whitepaper](https://niftyindices.com/docs/default-source/indices/nifty-50/nifty-50-whitepaper_2025.pdf)
- **Liquidity and the premium:** a third-party replication found liquid-stock momentum returned 8.51% (below Nifty 50) while illiquid-stock momentum returned 19.43%. — [BacktestIndia](https://backtestindia.com/blog/momentum-investing-india-backtest); [Freefincal](https://freefincal.com/is-indian-momentum-investing-just-a-liquidity-illusion/) [prior notes]

### Inferences
- **Implied tracked assets [own computation]:** ₹16,000 cr round trip at 68.4% one-way turnover means about ₹11,700 cr tracking the index in June 2025, matching the ₹12,523 cr NSE reported for February 2026. The trade estimates are therefore credible.
- **Trade size has grown about 2.5 times in a year:** one-way ₹3,200 cr in June 2024 to about ₹8,000 cr in June and December 2025, from both more assets and higher turnover (42% to 68%).
- **Front-running is structurally easy:** the changes are public about three weeks before the effective date, the formula is published so analysts predict them earlier still, and all tracking funds trade at the same close. Per-stock flows of ₹100–650 cr are large for midcap names. This is reasoning from the mechanics; no source measured the price effect.
- **Tracking difference understates the true cost.** A fund that trades at the rebalance close matches the index exactly even if that close was pushed 1–2% against it. The loss sits inside the index return, so it shows up as a live return below the back-test, not as tracking error.
- **For the "ETF vs 15 stocks" decision:** a self-run 15-stock book trading ₹5–50 lakh has negligible impact and can trade a few days away from the index dates, which a ₹8,000 cr fund cannot. Against that it pays higher percentage brokerage and STT, loses the fund's tax deferral (the fund pays no capital gains tax on its 100%+ turnover; the individual pays 20% STCG on each short-held winner), and carries more stock-specific risk with 15 names than 30.

### Gaps
- No published estimate of rebalance-day impact cost or front-running loss in basis points for any Indian momentum index.
- Turnover for Midcap150 Momentum 50 and Nifty500 Momentum 50 beyond FY25 (96% and 139%, prior notes): not updated. Nothing for Alpha 50's quarterly turnover.
- No data on how much of the tracked AUM trades on the effective date versus spreading trades.
- Capacity estimates (AUM at which the premium is competed away): none found.
