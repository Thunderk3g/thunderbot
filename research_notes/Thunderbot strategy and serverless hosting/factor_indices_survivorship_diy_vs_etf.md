# Indian factor indices since 2005, survivorship-free data, and DIY 15-stock momentum vs a momentum ETF (as of 10 Nov 2026)

Compiled 10 Nov 2026. Read with the earlier notes `Evidence based NSE trading strategies/momentum_factor_evidence.md` and `.../mean_reversion_and_backtesting.md` (23 Oct 2026); figures already established there are only summarised here.

**How these notes were built, and their limits.**
- **Network.** In this session `niftyindices.com`, `nseindia.com`, `freefincal.com`, SSRN, Yahoo Finance, AMFI and the Wayback Machine were all unreachable (blocked by the session's network policy), and the shared web-search budget ran out after 13 searches. Only GitHub and PyPI were reachable. So none of the Capitalmind, Freefincal, DSP, Motilal, Weekend Investing, Rajan Raju, S&P BSE or broker-pricing pages could be opened; where they appear below it is from a search-result summary and is marked **[search summary]**.
- **Own computations.** Because of that, most new numbers are marked **[own computation]**. They were calculated in this session from public data sets cloned from GitHub (each named with its URL). Scripts are in the session scratchpad, `/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/work/`. They are not published results and nobody has reviewed them.
- **Recalled literature.** Academic papers marked **[recalled]** are cited from the researcher's memory of the published paper; the link is the paper's DOI or SSRN page but it was not re-opened in this session. Check any such number before quoting it.
- **Back-test vs live.** Every NSE factor index has a back-calculated history from its base date (usually 1 Apr 2005). Only the period after the launch date is live. Launch dates are in section 3.
- **PR vs TR.** "TR/TRI" includes dividends; "PR" is the price index, which is about 1.2–1.5 points a year lower. All own computations on stock portfolios are price-only, before costs and tax.

---

## 1. Long-run record of the NSE factor indices (1 Apr 2005 → 2026): return, risk, drawdown and the longest stretches of underperformance

### Takeaway
Since 2005 (mostly back-test) momentum, alpha, low-volatility and quality indices all show 3–6 points a year over the Nifty 50/200, but the live record is far weaker: since launch, Momentum 30 is +1.0 point a year over the Nifty 200 (price index, 25 Aug 2020 – 26 Oct 2026) with a third more volatility, Low Vol 30 is +0.1, Quality 30 is −1.4 and only Alpha 50 (+7) and Value 50 (+5) have kept a large edge. Every factor has had multi-year droughts: momentum made no net progress against the Nifty 200 from the end of 2007 until 2013 and has been behind again since June 2024; quality has lagged since 2016–2020; low-volatility since April 2020; value lost 7.5 points a year for five years (2016–2021) before its recent run.

### Cited Findings

**Since-2005 figures (TRI unless stated; mostly back-test)**

| Index | Since-inception CAGR | Annualised SD | Max drawdown | Comparator | As of / source |
|---|---|---|---|---|---|
| Nifty200 Momentum 30 | 18.30% (to 30 Sep 2026); 18.8% (to 30 Jun 2026) | 22.31% | −67.7% (to 27 Oct 2008) | Nifty 200 TRI 13.9%, Nifty 50 TRI 13.6% (to Jun 2026); Nifty 200 drawdown −63.7% | Earlier notes, from [NSE factsheet](https://www.niftyindices.com/Factsheet/Factsheet_Nifty200_Momentum30.pdf), [HDFC AMC deck Jul 2026](https://files.hdfcfund.com/s3fs-public/Others/2026-07/HDFC%20NIFTY200%20Momentum%2030%20Index%20Fund_PPT%20%28July%202026%29.pdf), [NSE whitepaper Apr 2026](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf) |
| Nifty200 Quality 30 | 16.64% (to 30 Sep 2026) | 17.87% | not found | — | Earlier notes, from [NSE factsheet](https://www.niftyindices.com/Factsheet/Factsheet_NIFTY200_Quality30.pdf) |
| Nifty Alpha Low-Volatility 30 | 17.71% (to 30 Sep 2026); 19.0% (to 30 Sep 2020) | 17.20%; 18.5% vs 22.6% for Nifty 100 (to Sep 2020) | not found | — | Earlier notes, [NSE factsheet](https://www.niftyindices.com/Factsheet/Factsheet_NIFTY_Alpha_Low-Volatility_30.pdf); [NSE whitepaper Oct 2020](https://www.niftyindices.com/docs/default-source/indices/nifty-alpha-low-volatility-30/nifty-alpha-low-volatility-30-whitepaper_2020.pdf) **[search summary]** |
| Nifty Alpha 50 (base 31 Dec 2003) | 20.21% (to 30 Sep 2026) | 24.74% | not found | — | Earlier notes, [NSE factsheet](https://www.niftyindices.com/Factsheet/Factsheet_Nifty_Alpha50.pdf) |
| Nifty100 Low Volatility 30 | 17.66% **price return**, Apr 2005 – May 2018 only | 18.18% | −49.5% (2 Jan – 27 Oct 2008) | Nifty 100 PR 13.66%, SD 22.62%, drawdown −61.5% | Earlier notes, [NSE white paper Jun 2018](https://archives.nseindia.com/content/indices/NIFTY100_Low_Vol30_White_paper_Jun2018.pdf) |

- No since-2005 CAGR, SD or drawdown to 2026 could be retrieved for Nifty100 Low Volatility 30, Nifty 100/500 TRI, Nifty50 Value 20 (base 1 Jan 2009) or Nifty500 Value 50 — see Gaps.
- Nifty50 Value 20 and Nifty100 Quality 30 do not go back to 2005: their base dates are 1 Jan 2009 and 1 Oct 2009. — [index_launch_dates.json in patel-26meet/nse-strategy-indices-visualised (from NSE factsheets, 31 Aug 2026)](https://github.com/patel-26meet/nse-strategy-indices-visualised)

**10-, 5-, 3- and 1-year TRI returns, as of 2 Sep 2026.** Source: a third-party compilation of NSE Indices' daily TRI feed. Its Momentum 30 calendar-year figures match NSE's own whitepaper to the second decimal, which supports its accuracy. "Vol 5y" and "Max DD 5y" cover 2 Sep 2021 – 2 Sep 2026. — [patel-26meet/nse-strategy-indices-visualised, data/index_returns_*.json](https://github.com/patel-26meet/nse-strategy-indices-visualised) ([site](https://patel-26meet.github.io/nse-strategy-indices-visualised/))

| Index (TRI) | 1y | 3y | 5y | 10y | Vol 5y | Max DD 5y |
|---|---|---|---|---|---|---|
| Nifty 50 | −1.6% | 8.4% | 8.1% | 11.9% | 13.8% | −16.4% |
| Nifty 100 | 0.4% | 10.1% | 8.6% | 12.1% | 14.1% | −17.2% |
| Nifty 200 | 2.4% | 11.4% | 10.0% | 12.8% | 14.3% | −17.8% |
| Nifty 500 | 3.1% | 11.9% | 10.7% | 13.2% | 14.4% | −18.6% |
| Nifty200 Momentum 30 | 2.9% | 12.1% | 10.4% | 16.4% | 19.5% | −31.6% |
| Nifty Alpha 50 | 12.7% | 17.9% | 13.7% | 20.6% | 21.8% | −32.8% |
| Nifty100 Low Volatility 30 | −0.9% | 11.8% | 10.0% | 12.9% | 11.9% | −18.1% |
| Nifty200 Quality 30 | −0.4% | 10.2% | 8.3% | 12.2% | 13.5% | −22.4% |
| Nifty100 Quality 30 | 0.9% | 10.6% | 9.0% | 11.3% | 13.0% | −21.0% |
| Nifty Alpha Low-Volatility 30 | 2.9% | 12.8% | 9.9% | 13.4% | 13.3% | −24.7% |
| Nifty50 Value 20 | −5.2% | 7.1% | 8.1% | 14.4% | 13.9% | −19.0% |
| Nifty500 Value 50 | 16.7% | 24.8% | 25.7% | 16.6% | 20.3% | −22.2% |
| Nifty Midcap150 Momentum 50 | 6.0% | 16.9% | 17.2% | 20.5% | 19.1% | −25.5% |

**Calendar-year TRI returns 2020 – 2026 YTD (to 2 Sep 2026).** — [same source](https://github.com/patel-26meet/nse-strategy-indices-visualised)

| Index | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 YTD |
|---|---|---|---|---|---|---|---|
| Nifty 50 | 16.1 | 25.6 | 5.7 | 21.3 | 10.1 | 11.9 | −7.6 |
| Nifty 200 | 16.8 | 28.9 | 4.9 | 24.7 | 14.8 | 9.6 | −3.5 |
| Nifty200 Momentum 30 | 20.0 | 53.8 | −5.5 | 41.7 | 21.3 | −4.6 | −0.8 |
| Nifty Alpha 50 | 52.7 | 75.4 | −13.5 | 43.6 | 33.9 | −10.2 | 12.6 |
| Nifty100 Low Volatility 30 | 24.3 | 24.2 | 2.0 | 31.9 | 12.4 | 11.5 | −4.3 |
| Nifty200 Quality 30 | 26.3 | 26.2 | −4.4 | 31.7 | 14.4 | 4.7 | −3.6 |
| Nifty Alpha Low-Volatility 30 | 15.7 | 30.9 | −3.1 | 39.0 | 17.8 | 0.3 | −0.2 |
| Nifty50 Value 20 | 28.5 | 37.3 | 1.7 | 29.8 | 17.9 | 0.9 | −10.2 |
| Nifty500 Value 50 | 8.5 | 56.4 | 23.2 | 62.6 | 20.2 | 16.9 | 3.8 |

- **Conflict.** Wright Research lists −8.23% for Nifty200 Quality 30 in 2025; the TRI compilation shows +4.68% and this session's price-index calculation +2.9%. Treat the Wright figure as unreliable. — [Wright Research](https://www.wrightresearch.in/track/index/nifty-200-quality-30/) **[search summary]**; contradicted by [patel-26meet compilation](https://github.com/patel-26meet/nse-strategy-indices-visualised)

**Live record since each index's launch [own computation].** Daily **price-index** closes from NSE's daily index file (`ind_close_all`), which only lists an index once it has launched, so every row is live history. End date 26 Oct 2026. "Relative underwater" is the time the index/benchmark ratio spent below its earlier high. Data: [ancap97/NSEDATA4ME `data` branch (snapshot 26 Oct 2026)](https://github.com/ancap97/NSEDATA4ME).

| Index (PR) | Live from | CAGR | Vol | Max drawdown (peak → trough) | Benchmark CAGR / vol / max DD | Excess | Longest relative underwater | Max relative drawdown |
|---|---|---|---|---|---|---|---|---|
| Nifty200 Momentum 30 | 25 Aug 2020 | 14.5% | 19.4% | −31.8% (27 Sep 2024 → 7 Apr 2025; not recovered by 26 Oct 2026) | Nifty 200: 13.5% / 14.7% / −18.1% | +1.0 | 2.4 y, 14 Jun 2024 → ongoing | −22.1% (9 Apr 2025) |
| Nifty Alpha 50 (from 1 Mar 2013; see note) | 19 Nov 2012 | 19.5% | 20.9% | −40.7% (to 23 Mar 2020) | Nifty 500: 12.2% | +7.3 | 2.4 y, Jan 2018 → Jun 2020 | −29.7% |
| Nifty100 Low Volatility 30 | 11 Jul 2016 | 10.4% | 13.8% | −31.0% (17 Jan → 23 Mar 2020) | Nifty 100: 10.3% / 16.2% / −38.1% | +0.1 | 6.5 y, 15 Apr 2020 → ongoing | −14.2% (4 Apr 2022) |
| Nifty Low Volatility 50 | 19 Nov 2012 | 12.7% | 13.2% | −29.3% (Feb → Mar 2020) | Nifty 500: 12.0% / 16.1% / −38.3% | +0.7 | 6.4 y, 26 May 2020 → ongoing | −21.0% (Apr 2022) |
| Nifty200 Quality 30 | 18 Apr 2018 | 8.6% | 15.4% | −29.5% (Oct 2019 → 23 Mar 2020) | Nifty 200: 10.1% / 17.1% / −38.2% | −1.4 | 6.5 y, 15 Apr 2020 → ongoing | −23.7% (24 Feb 2026) |
| Nifty100 Quality 30 | 19 Mar 2015 | 7.8% | 14.8% | −34.1% (Aug 2018 → Mar 2020) | Nifty 100: 9.0% / 16.2% / −38.1% | −1.2 | 10.7 y, 25 Feb 2016 → ongoing | −21.7% (Jan 2023) |
| Nifty50 Value 20 (data from 9 Nov 2015) | 28 Mar 2014 | 11.2% | 15.6% | −31.2% (Apr 2019 → Mar 2020) | Nifty 50: 10.1% / 16.2% / −38.4% | +1.0 | 2.3 y, Mar 2016 → Aug 2018 | −14.8% (25 Aug 2026) |
| Nifty500 Value 50 | 24 Oct 2018 | 17.2% | 23.1% | −54.5% (16 Apr 2019 → 24 Mar 2020) | Nifty 500: 12.3% / 17.2% / −38.3% | +5.0 | 4.7 y, Nov 2018 → Jul 2023 | −38.8% (14 Oct 2020) |
| Nifty Alpha Low-Volatility 30 | 13 Jul 2017 | 10.5% | 15.1% | −31.3% (Feb → Mar 2020) | Nifty 200: 10.0% / 16.7% / −38.2% | +0.5 | 6.6 y, 31 Mar 2020 → ongoing | −19.6% (Feb 2021) |
| Nifty Midcap150 Momentum 50 | 17 Aug 2022 | 14.2% | 18.4% | −25.6% (24 Sep 2024 → 13 Mar 2025; not recovered) | Midcap 150: 14.4% / 16.1% / −21.1% | −0.2 | 2.4 y, 3 Jun 2024 → ongoing | −14.0% (Jul 2026) |

- Note on Alpha 50: the source file has a one-off 67% fall and 199% rise on 8 and 11 Feb 2013 (a data artefact); the series was used from 1 Mar 2013 with those two days neutralised.
- The "underwater since April 2020" results for low-volatility and quality are measured from a relative high set at the bottom of the COVID crash, when defensive indices were far ahead. On calendar-year TRI data Low Vol 30 beat the Nifty 100 in 3 of 6 years 2020–2025 (+8.2, −2.2, −3.0, +10.6, −0.6, +1.2 points) and Quality 30 beat the Nifty 200 in 2 of 6 (+9.5, −2.7, −9.3, +7.0, −0.3, −4.9). **[own computation]** from [patel-26meet compilation](https://github.com/patel-26meet/nse-strategy-indices-visualised)

**Drawdowns in specific episodes [own computation], price indices, same data.**

| Index | COVID (Jan–Mar 2020) | Oct 2021 – Jun 2022 | Sep 2024 – Apr 2025 | 2026 (from Jan high) |
|---|---|---|---|---|
| Nifty 50 | −38.4% | −17.2% | −15.8% | −15.6% (to 8 Oct 2026) |
| Nifty 200 | −38.2% | −18.1% | −18.1% | −14.9% |
| Nifty200 Momentum 30 | not live | −28.4% | −31.8% | −16.0% |
| Nifty Alpha 50 | −38.4% | −32.7% | −31.5% | −17.0% |
| Nifty100 Low Volatility 30 | −31.0% | −16.5% | −18.4% | −14.3% |
| Nifty200 Quality 30 | −29.5% | −18.7% | −23.0% | −16.0% |
| Nifty Alpha Low-Volatility 30 | −31.3% | −20.0% | −24.9% | −13.4% |
| Nifty500 Value 50 | −43.8% (−54.5% from Apr 2019) | −23.0% | −23.1% | −14.9% |

- 2026 price returns to 26 Oct 2026: Nifty 50 −12.9%, Nifty 200 −10.6%, Momentum 30 −10.5%, Low Vol 30 −11.6%, Quality 30 −12.2%, Alpha Low-Vol 30 −9.2%, Value 50 −6.1%, Alpha 50 +1.7%. **[own computation]**, [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME)
- The 2008–09 momentum drawdown (−67.7%, Jan → 27 Oct 2008) and the 2009 rebound lag (+69.3% vs about +88.8% for Nifty 200) are in the earlier notes. — [NSE whitepaper Apr 2026](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf)

**Longest stretches of underperformance for Momentum 30 (back-test + live) [own computation]** from the calendar-year table in NSE's April 2026 whitepaper (Momentum 30 return and excess over Nifty 200, 2006–2025). — [NSE whitepaper, Exhibit 7](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf)
- Momentum 30 / Nifty 200 relative wealth peaked at the end of 2007, fell through 2008 (−4 points) and 2009 (−19.5 points), was still fractionally below its end-2007 level at the end of 2012 (1.275 vs 1.279) and only passed it during 2013: **five full calendar years (2008–2012) with no net outperformance, about six from peak to recovery**.
- Over 2008–2010 Momentum 30 trailed by 5.4 points a year; over the five years 2008–2012 it trailed by 0.1 point a year. Those are the only losing 3-year (2 of 18) and 5-year (1 of 16) calendar windows in 2006–2025.
- End 2017 → end 2019: flat-to-down relative to the Nifty 200 (2018 −2.0, 2019 +0.5 points), recovered in 2020. 2022 (−10.4 points) was recovered in 2023.
- From the end of 2024 to the end of 2025 relative wealth fell 13% (2025 excess −14.1 points). On daily data the relative peak was 14 Jun 2024 and it had not been regained by 26 Oct 2026.
- Calendar-year arithmetic over 2006–2025: Momentum 30 18.0% a year vs 13.2% for the implied Nifty 200.

**Published rolling-return statistics (index providers and fund houses; all include back-test years)**
- Momentum 30 beat the Nifty 200 in 78.7% of daily rolling 5-year windows (NSE whitepaper at launch, Sep 2020). — [NSE whitepaper Sep 2020](https://archives.nseindia.com/content/indices/Nifty200_Momentum_30_Index_Whitepaper_Sep_20.pdf) **[search summary]**
- A Motilal Oswal deck reports "odds of outperformance" against Nifty 200 TRI of 88.2% (3-year) and 98.8% (5-year) for momentum, 87.6% for quality, 96.0% for low volatility and only 34.5% for value over 5 years; the column labels were hard to parse in the summary. — [Motilal Oswal AMC presentation](https://www.motilaloswalmf.com/CMS/assets/uploads/Documents/f03de-presentation-motilal-oswal-nifty-200-momentum-30-etf-index-fund-rd.pdf) **[search summary]**
- Nifty200 Quality 30 beat its parent in more than 80% of rolling 3-, 5-, 7- and 10-year periods over 2005–2018 (all back-test; the index launched in April 2018). — [NSE Quality 30 whitepaper](https://archives.nseindia.com/content/indices/NIFTY200_Quality30_Whitepaper_Final.pdf) **[search summary]**
- Nifty500 Value 50 and Nifty50 Value 20 beat their benchmarks 46% and 81% of the time respectively. — [Mint, 19 Apr 2024](https://www.pressreader.com/india/mint-kolkata/20240419/282316800086985) **[search summary]**
- Capitalmind (Sep 2021): most NSE factor indices improve their odds of beating the Nifty over longer horizons, except Nifty500 Value 50 and Nifty High Beta 50, which were among the weakest against buy-and-hold Nifty. — [Capitalmind Premium](https://premium.capitalmind.in/2021/09/best-nifty-factor-index-value-quality-alpha-momentum-lowvolatility-compared/) **[search summary]**
- Freefincal: Nifty50 Value 20 beat the Nifty 50 over seven years or more, but underperformance over five years or less "can be frustrating"; the 10-year outperformance margin of Low Vol 30 over the Nifty 50 was "at an all-time low". — [Freefincal, Value 20 review](https://freefincal.com/nippon-india-nifty-50-value-20-index-fund-review/); [Freefincal, Low Vol 30 vs Nifty 50](https://freefincal.com/nifty-100-low-volatility-30-vs-nifty-50-return-difference-at-an-all-time-low/) **[search summaries]**
- Value Research: factor funds trailed their parent indices in the recent downturn; five-year rolling returns favour factor indices but returns are lumpy, with long lagging stretches. — [Value Research](https://www.valueresearchonline.com/stories/224244/factor-funds-performance-review-market-downturn/) **[search summary]**
- A smallcase post states the Nifty200 Quality 30 returned "0.6% a year" and Momentum 30 "0.8%" over an unclear recent window, and that a quality portfolio trailed the Nifty LargeMidcap 250 every year since 2021. — [smallcase blog](https://www.smallcase.com/blog/quality-bluechips-smallcase-returns-gold-allocation/) **[search summary; window not verified]**

**Academic evidence (from the earlier notes)**
- IIM Ahmedabad survivorship-adjusted data: big-cap winners 17.2% vs market 14.9% (Apr 2005 – Dec 2025), an edge of 2.3 points; the long-short momentum factor fell 52% between Nov 2008 and Aug 2009. — [IIMA data library](https://faculty.iima.ac.in/iffm/Indian-Fama-French-Momentum/)
- Raju and Teli: long-only momentum, low-volatility and quality portfolios from India's top 200 stocks beat the broad index over their sample, but "there is not one factor-style that is a consistent winner". — [Factor Investor report, Jan 2022](https://factorinvestor.substack.com/p/factor-investor-report-jan-2022) **[search summary]**

### Inferences
- The back-tested 4–5 point momentum premium should not be the planning number. On live data the edge of Momentum 30 over the Nifty 200 is +0.4 points (5 years to 2 Sep 2026, TRI), +1.0 (since launch to 26 Oct 2026, PR) or +2.8 (calendar 2021–2025, TRI), with volatility of about 19.5% against 14.5% and drawdowns 10–14 points deeper in 2022 and 2024–25.
- A momentum investor must be able to sit through at least two to three years, and historically five to six, of zero or negative relative return, plus an absolute drawdown of about −30% in an ordinary correction and −65% to −70% in a 2008-type crash.
- Low-volatility and quality have delivered what they are meant to deliver in live trading (drawdowns 7–9 points shallower in March 2020, volatility about 2 points lower) but not extra return: +0.1 and −1.4 points a year.
- Value is the most regime-dependent factor: −7.5 points a year in Sep 2016 – Sep 2021, +15 points a year in Sep 2021 – Sep 2026, and a −54.5% absolute drawdown in 2019–20.
- Factor leadership rotates on a 3–6 year cycle (quality/low-vol led to early 2020, momentum/alpha 2020–mid 2024, value 2021–2026). Choosing the factor with the best trailing 5-year return is likely to buy it near the end of its run.

### Gaps
- NSE's own site was unreachable, so the latest (31 Oct 2026) factsheets were not opened. Missing as a result: since-2005 TRI CAGR, SD and maximum drawdown to 2026 for Nifty100 Low Volatility 30, Nifty500 Value 50, Nifty 100 TRI and Nifty 500 TRI; official maximum-drawdown figures (with dates) for Quality 30, Alpha 50 and Alpha Low-Vol 30 over the full history.
- No daily TRI series from 2005 was available, so true daily rolling 3- and 5-year underperformance statistics from 2005 could not be computed. The Momentum 30 stretches above are at calendar-year resolution; those for the other factors cover only their live period.
- Not opened: Capitalmind, Freefincal, DSP ("Netra"/factor reports), Motilal Oswal, ICICI Prudential, UTI and Mirae factor decks, S&P BSE factor index data (Momentum, Low Volatility, Quality, Enhanced Value) and SPIVA India. No BSE factor numbers are in these notes.
- Rajan Raju's SSRN papers were identified by title only ("Shades of Momentum", SSRN 4977717; a 52-week-high momentum paper, SSRN 4587697; "'Long' Factors, not 'Short' Change" with Anish Teli) and not read. No paper by him on factor timing or trend-following in India was found. — [Quantpedia listing](https://vvv.quantpedia.com/?p=38194); [Scribd copy of SSRN 4587697](https://www.scribd.com/document/694152012/SSRN-id4587697) **[search summaries]**

---

## 2. Which factor combinations have held up best in India

### Takeaway
On live data to 26 Oct 2026 the simple two-factor blends have not earned a premium: Alpha Low-Volatility 30 and Alpha-Quality-Low-Vol 30 are each about +0.5 point a year over the Nifty 200 since July 2017, Quality-Low-Vol 30 is −1.6, and the newer momentum-quality indices are flat-to-negative since launch. The one multi-factor index with a clear live edge is the four-factor Alpha-Quality-Value-Low-Vol 30 (+2.4 points a year, helped by the value run), and no fund tracks it. What the blends do deliver is a lower-volatility ride than pure momentum.

### Cited Findings
- **Construction.** NSE's 2017 multi-factor family draws from the Nifty 100 plus Nifty Midcap 50 and weights factor scores equally: Alpha Low-Vol 30 (50/50), Quality Low-Vol 30 (50/50), Alpha Quality Low-Vol 30 (one-third each), Alpha Quality Value Low-Vol 30 (one quarter each). Base date 1 Apr 2005, launched July 2017. — [NSE press release, 13 Jul 2017](https://niftyindices.com/Press_Release/ind_prs13072017.pdf); [NSE multi-factor whitepaper](https://archives.nseindia.com/content/indices/NIFTY_Multi-Factor_Indices_whitepaper.pdf) **[search summaries]**; launch dates from [patel-26meet compilation](https://github.com/patel-26meet/nse-strategy-indices-visualised)
- **Live record since 13 Jul 2017, price index, to 26 Oct 2026 [own computation]** (Nifty 200 over the same period: 10.0% CAGR, 16.7% vol, −38.2% drawdown). Data: [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME)

  | Index | CAGR | Vol | Max DD | Excess over Nifty 200 | Relative underwater |
  |---|---|---|---|---|---|
  | Alpha Low-Volatility 30 | 10.5% | 15.1% | −31.3% | +0.5 | since 31 Mar 2020 (6.6 y, ongoing) |
  | Alpha Quality Low-Volatility 30 | 10.6% | 14.8% | −29.9% | +0.5 | since 15 Apr 2020 (6.5 y, ongoing) |
  | Quality Low-Volatility 30 | 8.4% | 14.1% | −30.0% | −1.6 | since 15 Apr 2020; max relative DD −26.6% (22 Jun 2026) |
  | Alpha Quality Value Low-Volatility 30 | 12.4% | 14.8% | −29.0% | +2.4 | 3.6 y (Apr 2020 → Nov 2023); behind again for 2.2 y |

- **TRI, as of 2 Sep 2026** (Nifty 200: 5y 10.0%, 10y 12.8%; Nifty 500: 5y 10.7%, 10y 13.2%). — [patel-26meet compilation](https://github.com/patel-26meet/nse-strategy-indices-visualised)

  | Index | Launched | 1y | 3y | 5y | 10y | Vol 5y | Max DD 5y |
  |---|---|---|---|---|---|---|---|
  | Alpha Low-Volatility 30 | 10 Jul 2017 | 2.9% | 12.8% | 9.9% | 13.4% | 13.3% | −24.7% |
  | Alpha Quality Low-Volatility 30 | 10 Jul 2017 | 1.7% | 14.2% | 10.7% | 13.4% | 13.2% | −24.1% |
  | Quality Low-Volatility 30 | 10 Jul 2017 | −3.6% | 7.9% | 7.1% | 10.6% | 12.1% | −21.0% |
  | Alpha Quality Value Low-Vol 30 | 3 Jul 2017 | −3.0% | 15.4% | 14.4% | 15.7% | 13.7% | −20.9% |
  | Nifty200 Alpha 30 | 21 Jul 2022 | 7.7% | 17.5% | 14.8% | 18.9% | 21.3% | −31.1% |
  | Nifty500 Multicap Momentum Quality 50 | 4 Sep 2024 | 2.3% | 13.1% | 11.0% | 17.0% | 17.9% | −30.0% |
  | Nifty Total Market Momentum Quality 50 | 6 Aug 2025 | 4.7% | 13.6% | 11.9% | 17.9% | 18.7% | −29.5% |
  | Nifty500 Multifactor MQVLv 50 | 6 Feb 2025 | 0.3% | 15.0% | 13.8% | 15.2% | 15.5% | −22.9% |
  | Nifty500 Momentum 50 | 4 Jun 2024 | 8.0% | 13.8% | 13.9% | 18.8% | 20.9% | −31.6% |
  | Nifty500 Low Volatility 50 | 20 Dec 2024 | 1.5% | 14.7% | 12.8% | 14.6% | 12.4% | −15.2% |

- **Nifty500 Multicap Momentum Quality 50.** Launched 4 Sep 2024 with a reported 32.49% 5-year CAGR (back-calculated). It holds 10 large, 15 mid and 25 small caps and rebalances in June and December. — [Business Standard, 5 Sep 2024](https://www.business-standard.com/amp/markets/capital-market-news/nse-launches-new-multicap-momentum-quality-50-index-124090500335_1.html) **[search summary]**. Since launch: 2025 −7.8% against +7.8% for the Nifty 500; 2026 YTD (to 2 Sep) +1.5% against −2.0%. An Edelweiss fund tracking it drew down −26.6% from 13 Dec 2024 to 28 Feb 2025. — [patel-26meet compilation](https://github.com/patel-26meet/nse-strategy-indices-visualised); [arthgyaan fund page](https://arthgyaan.com/fund/edelweiss-nifty500-multicap-momentum-quality-50-index-fund-direct-growth/152985) **[search summary]**
- **Nifty200 Alpha 30** (launched 21 Jul 2022) is +8.7 points a year over the Nifty 200 on live price data to 26 Oct 2026 (18.2% vs 9.5%), with 20.1% volatility and a −29.9% drawdown (Aug 2024 → Feb 2025); it has been behind its relative high since 11 Jul 2024. **[own computation]**, [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME)
- **No fund tracks Alpha Quality Value Low-Volatility 30**; funds that appear in searches track the two-factor Alpha Low-Volatility 30. "Multi Factor" passive fund-of-funds are benchmarked to plain Nifty 500 TRI. — [patel-26meet compilation, funds data from AMFI](https://github.com/patel-26meet/nse-strategy-indices-visualised)
- **Momentum + low-vol correlation.** In one replication, monthly returns of momentum and low-volatility portfolios had a correlation of 0.87; a sequential low-vol-then-momentum filter had a −16.5% drawdown in March 2020 (earlier notes). — [BacktestIndia](https://backtestindia.com/blog/momentum-investing-india-backtest)
- **Momentum + bonds.** Nifty200 Momentum 30 Plus 8–13 yr G-Sec 50:50 (back-test, Jan 2011 – Jun 2026): 12.7% CAGR, 9.7% volatility, −17.6% COVID drawdown, against 10.5% / 16.5% / −38.3% for the Nifty 50 (earlier notes). — [Mirae Asset presentation](https://www.miraeassetmf.co.in/docs/default-source/product-presentations/mirae-asset-nifty200-momentum-30-plus-8-13-yr-g-sec-5050-etf-presentation.pdf)
- **Fund-house material** shows higher average rolling returns and return/risk ratios for both Momentum 30 and Low Vol 30 than the Nifty 50/100/200 over 1, 3, 5 and 10 years; this is marketing material that includes the back-test. — [HDFC AMC "Smart Beta Investing (Momentum & Low Vol)" leaflet, Jun 2026](https://files.hdfcfund.com/s3fs-public/Others/2026-06/Leaflet%20-%20Smart%20Beta%20Investing%20%28Momentum%20%26%20Low%20Vol%29%20%28June%202026%29.pdf) **[search summary]**
- **Practitioner positioning.** Capitalmind's AIF combines momentum, low volatility and quality on the stated ground that single factors run in cycles. — [Capitalmind](https://capitalmind.in/alternative-investment-fund) **[search summary]**
- **Mechanical 50:50 blend of the two live indices [own computation].** Averaging the calendar-year TRI returns of Momentum 30 and Low Vol 30 for 2021–2025 (rebalanced back to 50:50 each January) gives 39.0%, −1.7%, 36.8%, 16.9%, 3.4%, or about 17.7% a year against 16.2% for the Nifty 200 and 19.0% for Momentum 30 alone. The blend's worst year was −1.7% against −5.5% for momentum. From [patel-26meet compilation](https://github.com/patel-26meet/nse-strategy-indices-visualised)

### Inferences
- Pairing momentum (or alpha) with low volatility has, live, produced roughly market return with about 10% less volatility than the Nifty 200 and a third less than pure momentum. It has not produced the 3–4 point premium that the 2005–2017 back-test showed.
- Quality-heavy blends have been the weakest since 2017 (Quality Low-Vol 30 −1.6 points a year).
- A do-it-yourself 50:50 holding of a Momentum 30 fund and a Low Vol 30 fund is a defensible "combination" because both exist as cheap funds and its components have 6–10 years of live history. The four-factor index that looks best cannot be bought.
- All 2024–2026 launches (Multicap Momentum Quality 50, Total Market Momentum Quality 50, Multifactor MQVLv 50, Nifty500 Momentum/Low Vol/Quality 50) are almost entirely back-test; their 10-year numbers are in-sample by construction.

### Gaps
- No Freefincal or Capitalmind back-test of a 50:50 Momentum 30 + Low Vol 30 fund blend was found in the one search run on it; their articles could not be opened. The blend arithmetic above uses calendar-year returns only (no daily volatility or drawdown).
- No since-2005 performance table for the multi-factor indices was retrieved; the NSE multi-factor whitepaper could not be opened.
- No live data for Nifty Alpha Quality Low-Vol 30 against the Nifty 100 + Midcap 50 universe it draws from; Nifty 200 is used as the nearest benchmark.

---

## 3. How much of each index history is back-test, and does performance decay after launch?

### Takeaway
Between half and four-fifths of each NSE factor index's quoted history is a back-test written after the fact (71% for Momentum 30). US evidence is that smart-beta indices lose essentially all of their back-tested outperformance once a product is listed, and the Indian live records point the same way: the back-tested premium has shrunk by roughly half to nine-tenths for Momentum 30, Low Vol 30, Quality 30, Alpha Low-Vol 30 and Midcap150 Momentum 50. Alpha 50 is the main exception.

### Cited Findings

**Launch dates and the share of history that is back-test** (to 26 Oct 2026). Dates from NSE factsheets as compiled in [patel-26meet/nse-strategy-indices-visualised](https://github.com/patel-26meet/nse-strategy-indices-visualised); shares are **[own computation]**.

| Index | Base date | Launch date | Back-test years | Live years | Back-test share |
|---|---|---|---|---|---|
| Nifty Alpha 50 | 31 Dec 2003 | 19 Nov 2012 | 8.9 | 13.9 | 39% |
| Nifty Low Volatility 50 / High Beta 50 | 31 Dec 2003 | 19 Nov 2012 | 8.9 | 13.9 | 39% |
| Nifty50 Value 20 | 1 Jan 2009 | 28 Mar 2014 | 5.2 | 12.6 | 29% |
| Nifty100 Quality 30 | 1 Oct 2009 | 19 Mar 2015 | 5.5 | 11.6 | 32% |
| Nifty100 Low Volatility 30 | 1 Apr 2005 | 8 Jul 2016 | 11.3 | 10.3 | 52% |
| Alpha Low-Vol 30, Alpha Quality Low-Vol 30, Quality Low-Vol 30, AQVLV 30 | 1 Apr 2005 | 3–10 Jul 2017 | 12.3 | 9.3 | 57% |
| Nifty200 Quality 30 | 1 Apr 2005 | 17 Apr 2018 | 13.0 | 8.5 | 60% |
| Nifty500 Value 50 | 1 Apr 2005 | 24 Oct 2018 | 13.6 | 8.0 | 63% |
| Nifty200 Momentum 30 | 1 Apr 2005 | 25 Aug 2020 | 15.4 | 6.2 | 71% |
| Nifty200 Alpha 30 | 1 Apr 2005 | 21 Jul 2022 | 17.3 | 4.3 | 80% |
| Nifty Midcap150 Momentum 50 | 1 Apr 2005 | 16 Aug 2022 | 17.4 | 4.2 | 81% |
| Nifty500 Momentum 50 | 1 Apr 2005 | 4 Jun 2024 | 19.2 | 2.4 | 89% |
| Nifty500 Multicap Momentum Quality 50 | 1 Apr 2005 | 4 Sep 2024 | 19.4 | 2.1 | 90% |

- Of 37 NSE strategy indices with a return series, 24 use the 1 Apr 2005 base date, only 9 existed ten years ago, and 14 were launched in 2024 or later. Nifty500 Growth 50 showed a 21.4% three-year return on the day it was launched (26 Aug 2026). — [patel-26meet/nse-strategy-indices-visualised README, data as of 2 Sep 2026](https://github.com/patel-26meet/nse-strategy-indices-visualised)

**Global evidence on decay**
- Huang, Song and Xiang, "The Smart Beta Mirage" (*Journal of Financial and Quantitative Analysis* 59(6), 2024): for US equity smart-beta ETFs listed 2000–2018, the indices' market-adjusted return falls from about 3% a year in the back-test to about −0.5% to −1% after the ETF lists. Variation in factor premia, strategic timing and diminishing returns to scale do not explain the fall; the authors attribute it to data mining in index construction, and show investors chase back-tests. — [Cambridge University Press](https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/smart-beta-mirage/35CA1CEA091A485DDA960BB2D9930BC9); [RePEc](https://ideas.repec.org/a/cup/jfinqa/v59y2024i6p2515-2546_2.html) **[search summaries]**
- The press summary gives 2.77% a year above market before listing and −0.44% after fees over an average six years after listing. — [InvestmentNews](https://www.investmentnews.com/industry-news/news/smart-beta-funds-dont-live-up-backtesting-196778) **[search summary]**
- Suhonen, Lennkh and Perez (2017): across 215 bank "alternative beta" strategies, the median Sharpe ratio fell by 73% from back-test to live. — [Journal of Portfolio Management 43(2)](https://doi.org/10.3905/jpm.2017.43.2.090) **[recalled]**
- McLean and Pontiff (2016): across 97 published return predictors, returns were 26% lower out of sample and 58% lower after publication. — [Journal of Finance 71(1)](https://doi.org/10.1111/jofi.12365) **[recalled]**
- Harvey, Liu and Zhu (2016): with over 300 published factors, a new factor should clear a t-statistic of about 3.0, not 2.0, to allow for data mining. — [Review of Financial Studies 29(1)](https://doi.org/10.1093/rfs/hhv059) **[recalled]**
- Arnott, Beck, Kalesnik and West (2016): much of the past outperformance of popular smart-beta factors came from the factor becoming more expensive, which cannot repeat and can reverse. — [Research Affiliates, "How Can 'Smart Beta' Go Horribly Wrong?"](https://www.researchaffiliates.com/publications/articles/442-how-can-smart-beta-go-horribly-wrong) **[recalled]**

**India: back-tested vs live excess return [own computation]**

| Index | Back-tested premium (source) | Live premium | Rough shrinkage |
|---|---|---|---|
| Nifty200 Momentum 30 vs Nifty 200 | About +5.0 points a year in the 14 pre-launch calendar years 2006–2019 (relative wealth ×1.98); +7.2 in Sep 2016 – Sep 2021 | +2.8 (calendar 2021–2025, TRI); +1.0 (launch → 26 Oct 2026, PR); +0.4 (5 years to 2 Sep 2026, TRI) | 45–90% |
| Nifty100 Low Volatility 30 vs Nifty 100 | +4.0 (PR, Apr 2005 – May 2018, of which 11 years back-test) | +0.1 (PR, Jul 2016 → Oct 2026); +0.8 (10-year TRI to Sep 2026) | 80–95% |
| Nifty200 Quality 30 vs Nifty 200 | About +2.7 (16.64% since inception vs about 13.9%) | −1.4 (PR, Apr 2018 → Oct 2026); −1.7 (5-year TRI) | more than 100% |
| Nifty Alpha Low-Vol 30 vs Nifty 200 | About +3.8 (17.71% since inception vs about 13.9%) | +0.5 (PR, Jul 2017 → Oct 2026); −0.1 (5-year TRI) | 85–100% |
| Nifty Midcap150 Momentum 50 vs Midcap 150 | +5.8 (23.00% vs 17.24%, Apr 2005 – Feb 2026) | −0.2 (PR, Aug 2022 → Oct 2026); +0.1 (5-year TRI) | about 100% |
| Nifty Alpha 50 vs Nifty 500 | not established | +7.3 (PR, Mar 2013 → Oct 2026); +3.0 (5-year TRI) | none visible |
| Nifty500 Value 50 vs Nifty 500 | not established | +5.0 (PR, Oct 2018 → Oct 2026) after a 4.7-year relative drought | n/a |

Sources: back-tested figures from the earlier notes ([NSE factsheets](https://www.niftyindices.com/Factsheet/Factsheet_Nifty200_Momentum30.pdf), [NSE whitepaper Apr 2026](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf), [NSE Low Vol white paper 2018](https://archives.nseindia.com/content/indices/NIFTY100_Low_Vol30_White_paper_Jun2018.pdf)); live figures computed from [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME) and [patel-26meet compilation](https://github.com/patel-26meet/nse-strategy-indices-visualised).

- The same compilation notes that Nifty Midcap150 Momentum 50 returned 17.18% over five years against 17.08% for the plain Nifty Midcap 150, "0.1pp a year and 2.2pp of volatility", and that Nifty High Beta 50 (fully live) beat the Nifty 500 by 7.5 points a year over 5 years but trailed it by 1.9 over 10. — [patel-26meet README](https://github.com/patel-26meet/nse-strategy-indices-visualised)
- Momentum 30's methodology has itself changed after launch: the F&O-eligibility rule now appears in the methodology and a December 2025 change was reported as having "jolted" ₹16,000 crore of tracking assets (earlier notes; article not opened). — [NSE methodology document](https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf); [Business Standard, Dec 2025 (403)](https://www.business-standard.com/)
- Indian blog commentary questioning NSE's back-testing claims for "child" indices exists but was not opened. — [Rama Krishna Vadlamudi blog, 9 Dec 2025](https://ramakrishnavadlamudi.blogspot.com/2025/12/nses-backtesting-claims-child-indices.html); [same blog, 24 Nov 2025](https://ramakrishnavadlamudi.blogspot.com/2025/11/factor-investing-in-india-do-smart-beta.html) **[titles only]**

### Inferences
- A sensible haircut for planning is to assume half or less of any back-tested Indian factor premium. For Momentum 30 that means +1 to +2.5 points a year over the Nifty 200 before fund costs, not +5.
- Six years of live data is a short sample that contains two momentum drawdowns (2022, 2024–25) and one strong run (2023–mid 2024), so the live premium is itself uncertain; it is not proof that momentum has stopped working. The IIM-A factor data (survivorship-adjusted, 1993–2025) still show a significant premium.
- The live shortfall cannot be blamed on index methodology alone: assets tracking momentum indices grew from zero in 2020 to about ₹17,700 crore by Feb 2026 (earlier notes), and crowding into the same 30 names on the same rebalance dates is a plausible second cause. This is a hypothesis, not a finding.
- The reader's own back-test is subject to the same problem twice over: it is both survivorship-biased and fitted (lookbacks, buffer, filter) on the same 2011–2026 data.

### Gaps
- No peer-reviewed Indian study of post-launch decay of NSE or BSE factor indices was found.
- The pre-launch back-tested premium for Alpha 50, Value 50 and the multi-factor indices was not established (no pre-launch daily data), so decay for those cannot be measured.
- The Research Affiliates, Suhonen et al., McLean–Pontiff and Harvey–Liu–Zhu numbers are from memory and were not re-checked.

---

## 4. Free or cheap sources of historical index membership (Nifty 50 / 100 / 200 / 500)

### Takeaway
A hobbyist can now rebuild point-in-time membership for free, but in pieces: NSE's own inclusion/exclusion workbook covers Nifty 50 (from 1996), Nifty 100 (2003), Nifty 200 (Nov 2011) and Nifty 500 (Aug 1998) up to July–September 2020, by company name; monthly constituent files cover April 2013 – March 2022; after that it is Wayback snapshots of the constituent CSVs and NSE press releases. Several 2026 GitHub projects automate parts of this; quality varies from validated (Nifty 50) to unusable.

### Cited Findings

**Primary (NSE) sources**
- **`IndexInclExcl.xls`** (NSE archives). Checked from a copy in a public repo **[own inspection]**: 37 sheets, one per index, each with Index Name / Event Date / Scrip Name / "Inclusion into Index" or "Exclusion from Index". Coverage: Nifty 50 from 18 Sep 1996 (196 events), Nifty Next 50 from 12 Jan 2000 (382), Nifty 100 from 19 Mar 2003 (336), Nifty 200 from 22 Nov 2011 (466), Nifty 500 from 1 Aug 1998 (2,495). The last events are dated 31 Jul 2020 (14 Sep 2020 for Nifty 500). It gives company names, not symbols, and no starting constituent list. — [copy in rishabhjain0295-web/nifty500-momentum-backtest, data/IndexInclExcl.xls](https://github.com/rishabhjain0295-web/nifty500-momentum-backtest); original URL per earlier notes: [NSE archives](https://archives.nseindia.com/content/indices/IndexInclExcl.xls)
- That repo's author describes the file as "authoritative from 1998 to 2020-09-14, after which NSE stopped updating this particular file". — [rishabhjain0295-web README](https://github.com/rishabhjain0295-web/nifty500-momentum-backtest)
- **Monthly constituent archives, April 2013 – March/April 2022.** A second project reports that "exact official Nifty 500 membership begins 2013-04-30" and official sector history runs 30 Apr 2013 – 29 Apr 2022, matching the niftyindices monthly zip files described in the earlier notes. — [manan0308/india-nifty-momentum-backtest, KNOWN_LIMITATIONS.md](https://github.com/manan0308/india-nifty-momentum-backtest); [TradingQnA thread](https://tradingqna.com/t/where-can-i-find-historical-composition-of-nifty-indices/7163)
- **Current lists only:** `ind_nifty50list.csv`, `ind_nifty100list.csv`, `ind_nifty500list.csv` on NSE archives hold today's members; history must come from Wayback Machine snapshots of those URLs. — [rishabhjain0295-web README](https://github.com/rishabhjain0295-web/nifty500-momentum-backtest); [ReaperOAK/survivorship-free-backtester README](https://github.com/ReaperOAK/survivorship-free-backtester)
- **Press releases** on each semi-annual reconstitution are on niftyindices.com and are the source used by reconstruction projects. — [vishalvx/nifty-indices-datasets README](https://github.com/vishalvx/nifty-indices-datasets)
- **NSE name-change and symbol-change files** (`namechange.csv`, `symbolchange.csv`) are needed to map old scrip names to tickers; the copies in one repo have 2,317 and 1,051 rows. — [rishabhjain0295-web data folder](https://github.com/rishabhjain0295-web/nifty500-momentum-backtest); URLs listed in [NSE-noodles method.md](https://github.com/abhij1306/NSE-noodles)

**Community reconstructions (GitHub), with quality assessed in this session**

| Project | What it offers | Coverage | Assessment |
|---|---|---|---|
| [NegativeZone/nsepit](https://github.com/NegativeZone/nsepit) (Jul 2026) | Point-in-time **Nifty 50** membership rebuilt from Wikipedia's change table (69 changes, 25 Feb 2005 – 30 Sep 2025), with an alias table for renames/mergers and a name-to-symbol map; build refuses to run unless there are exactly 50 members at every month-end and 20 spot checks pass. Also a "bias harness" that runs a strategy on point-in-time vs current members. | Nifty 50 only, 2005 → mid-2026 | **Good.** An equal-weight portfolio built from it in this session tracked NSE's official Nifty50 Equal Weight index within 0.5 point a year (section 6). |
| [rishabhjain0295-web/nifty500-momentum-backtest](https://github.com/rishabhjain0295-web/nifty500-momentum-backtest) (updated 7 Nov 2026) | **Nifty 500** membership calendar: 1,427 (symbol, start, end) intervals for 1,115 symbols from Aug 1998, built from `IndexInclExcl.xls` to Sep 2020 and six Wayback snapshots (Jul 2020 – May 2026) after that; raw NSE files included. | Nifty 500, 1998 → 2026 | **Usable with care.** 318 historical names (about 25%) could not be mapped to a live ticker and are simply missing, so the universe averages about 424 names a month, and 2020–2026 changes are dated only to the nearest snapshot. Prices are from Yahoo, which lacks delisted stocks. |
| [manan0308/india-nifty-momentum-backtest](https://github.com/manan0308/india-nifty-momentum-backtest) (Sep 2026) | Official Nifty 500 membership from 30 Apr 2013, plus point-in-time **liquidity-ranked** Top 500 (from May 1995), Top 750 (Jul 2004) and Top 1,000 (Jan 2007) universes built from bhavcopies, 3 Nov 1994 – 7 Aug 2026, 11.05 million daily rows. | 1994 → Aug 2026 | Careful documentation and hashes, but the data archive is distributed outside Git and the author warns redistribution may need NSE permission. Not downloaded here. |
| [ReaperOAK/survivorship-free-backtester](https://github.com/ReaperOAK/survivorship-free-backtester) (Jul 2026, non-commercial licence) | Scripts that rebuild point-in-time Nifty 100/200/500 membership from the Internet Archive and recover delisted prices from bhavcopies. | Depends on Wayback coverage | Code only; results not verified here. |
| [vishalvx/nifty-indices-datasets](https://github.com/vishalvx/nifty-indices-datasets) (Jun 2026) | Monthly binary membership CSVs from press releases: Nifty 50 (2008 →), Midcap 50 and Smallcap 50 (2019 →), Nifty500 Momentum 50 (Jun 2024 →). | No Nifty 100/200/500 | Narrow; not verified. |
| [BKKB20/nse-index-history](https://github.com/BKKB20/nse-index-history) (Mar 2026) | Claims 28 indices, 2004–2026, rebuilt from about 100 NSE circulars. | — | **Not usable [own inspection].** The Nifty 50 has a member count other than 50 (between 46 and 58) in 40 of its 45 snapshots; the Nifty 100 has 13 snapshots, none between May 2009 and March 2026, and every pre-2009 "Nifty 100" snapshot contains all 100 of today's members (for example DMart and LIC appear in 2004); the Nifty 500 has 4 snapshots. |

- nsepit's README points to two further membership sources: **niftyhistory.in** (per-rebalance CSVs) and an academic data set on **figshare**. Neither was opened. — [nsepit README](https://github.com/NegativeZone/nsepit); [niftyhistory.in](https://niftyhistory.in/); [figshare](https://doi.org/10.6084/m9.figshare.30217915)
- Marketcalls (Aug 2026) describes walking back from the current list through NSE announcements and the monthly "Market Capitalisation, Weightage and Beta" reports for Nifty 50 and Next 50 (earlier notes). — [Marketcalls](https://www.marketcalls.in/llm-models/how-to-build-survivorship-bias-free-nifty-50-historical-data-using-grokbot.html)
- Forum threads asking for historical Nifty 500 constituents (2011–2012, pre-2013) mostly end without a free answer and suggest paying an authorised vendor. — [TradingQnA: which stocks made up Nifty 500 in the past](https://tradingqna.com/t/how-to-find-out-which-stocks-made-up-nifty-500-in-the-past/187020); [TradingQnA: historical constituents of various NSE indices](https://tradingqna.com/t/historical-constituents-of-various-nse-indices/176515); [Unofficed forum](https://forum.unofficed.com/t/get-historical-nifty-500-constituent/1375) **[search summaries]**
- **Commercial.** Optuma sells survivorship-bias-free symbol lists including a Nifty 500 list, reliable from 14 Feb 2008. — [Optuma knowledge base](https://www.optuma.com/kb/data/end-of-day-data-options/survivorship-bias-free-data) **[search summary]**
- **Not what they seem.** The `index-constitution` PyPI package covers CSI 300, S&P 500 and Nasdaq-100 (no Nifty coverage confirmed); a Hugging Face "Nifty500 companies 5 years" set holds the current 500 tickers over June 2021 – June 2026, which is survivorship-biased by construction. — [PyPI index-constitution](https://pypi.org/project/index-constitution/); [Hugging Face IITKGP/Nifty500_companies_5_years_data](https://huggingface.co/datasets/IITKGP/Nifty500_companies_5_years_data) **[search summaries]**
- **Research standard.** The IIM Ahmedabad factor library is built from CMIE Prowess and is survivorship-adjusted (earlier notes). — [IIMA data library](https://faculty.iima.ac.in/iffm/Indian-Fama-French-Momentum/)

**A membership-free alternative**
- Two of the projects avoid index membership altogether and define the universe causally as "the top N stocks by trailing traded value on each date", computed from bhavcopies, which is survivorship-free by construction. — [nsepit README](https://github.com/NegativeZone/nsepit); [manan0308 README](https://github.com/manan0308/india-nifty-momentum-backtest)
- Caution **[own computation]**: a top-100-by-6-month-median-turnover universe is not a good stand-in for the Nifty 100. Equal-weighted, it returned 6.9% a year (price only, Jan 2011 – Oct 2026) against roughly 10.8% for the official Nifty 100 price index (from Mar 2012) and 12.1% for Nifty100 Equal Weight (from Jun 2013), and at the end date only 68 of its 100 names were in the actual Nifty 100. Turnover ranking pulls in heavily traded speculative names. Data: [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME)

### Inferences
- For the reader's Nifty 100 back-test the cheapest honest route is: (a) take `IndexInclExcl.xls` for "Nifty 100" events from 2011 to July 2020; (b) patch August 2020 – 2026 from Wayback snapshots of `ind_nifty100list.csv` or the semi-annual press releases (roughly 12 reconstitutions, 5–10 names each); (c) walk backwards from today's list; (d) hand-map roughly 180–200 company names to symbols using `namechange.csv`/`symbolchange.csv`; (e) check that the count is exactly 100 at every date. This is a weekend of work, not a month.
- Any reconstruction should be validated the way nsepit does it: member count at every date, no duplicate identities across renames, and an equal-weight portfolio that tracks the official equal-weight index (Nifty50 Equal Weight from April 2017; Nifty100 Equal Weight from June 2013).
- A zero-effort check is available without any membership data: compare the equal-weight return of "today's list" against the official Nifty100 Equal Weight index over the same dates. The gap is the survivorship bias of the universe (section 6).

### Gaps
- NSE Data & Analytics' paid "historical index constituents" product and its price could not be checked (site unreachable).
- Not checked: CMIE Prowess, ACE Equity, Capitaline and Bloomberg pricing; Tijori, Screener, Trendlyne, StockEdge and Chartink (no evidence found that any offers point-in-time index membership); Kaggle data sets (Kaggle unreachable; one "Kaggle historical Nifty-50 weights" set is cited by [ReaperOAK](https://github.com/ReaperOAK/survivorship-free-backtester) but not identified); "Samasthiti", "Stocko" and "SigFig" (nothing found).
- Whether the Wayback Machine has enough snapshots of `ind_nifty100list.csv` for every half-year since 2020 was not verified (archive.org unreachable); one project found six usable Nifty 500 snapshots between July 2020 and May 2026.
- Whether niftyindices.com still serves the April 2013 – March 2022 monthly constituent zips, and whether Nifty 100/200 are included, was not re-verified.

---

## 5. Free prices for delisted, merged and renamed NSE stocks

### Takeaway
NSE's daily bhavcopy is the one free source that contains every security that traded on a given day, so it is survivorship-free by construction; the cost is that prices are unadjusted and the user must apply splits, bonuses, demergers and symbol/ISIN changes. In 2026 at least three open-source projects do this end to end, and one publishes a ready-made adjusted database (2005 → present, 4,583 securities of which 1,037 are delisted or inactive) that worked out of the box in this session. Broker APIs and Yahoo do not carry delisted names.

### Cited Findings

**The source files and URL patterns** — from [abhij1306/NSE-noodles, docs/method.md](https://github.com/abhij1306/NSE-noodles) and [ancap97/NSEDATA4ME README](https://github.com/ancap97/NSEDATA4ME):

| File | Period | URL pattern / name |
|---|---|---|
| Cash-market bhavcopy, old format | to 5 Jul 2024 | `nsearchives.nseindia.com/content/historical/EQUITIES/YYYY/MON/cmDDMONYYYYbhav.csv.zip` |
| Cash-market bhavcopy, UDiFF format | from 8 Jul 2024 | `nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_YYYYMMDD_F_0000.csv.zip` |
| Full bhavcopy with delivery data | from 2019 | `sec_bhavdata_full_DDMMYYYY.csv` (before 2019: `MTO_DDMMYYYY.DAT`) |
| Daily index file (all NSE indices, OHLC, P/E, P/B, yield) | from 21 Feb 2012 in these projects | `nsearchives.nseindia.com/content/indices/ind_close_all_DDMMYYYY.csv` |
| Corporate actions | — | `PRDDMMYY.zip` daily files; `www.nseindia.com/api/corporates-corporateActions` (undocumented API) |
| Symbol and name changes | — | `nsearchives.nseindia.com/content/equities/symbolchange.csv`, `namechange.csv` |

- **How far back.** One project starts on 22 Jun 2011, the first bhavcopy with an ISIN column. — [NSE-noodles method.md](https://github.com/abhij1306/NSE-noodles). Another has price history from 3 Jan 2005. — [NSEDATA4ME README](https://github.com/ancap97/NSEDATA4ME). A third has rows from 3 Nov 1994. — [manan0308 README](https://github.com/manan0308/india-nifty-momentum-backtest). EOD2 advertises "daily EOD data for over 2000 NSE stocks since 1995", adjusted for splits and bonuses. — [BennyThadikaran/eod2 README](https://github.com/BennyThadikaran/eod2)
- **Delisted names are kept.** "Every equity security that ever appeared in a daily bhavcopy" stays in the history, so "delisted, suspended and merged-away companies stay". — [NSE-noodles README](https://github.com/abhij1306/NSE-noodles). NSEDATA4ME's 26 Oct 2026 snapshot has 4,583 securities (3,975 main board, 608 SME), of which 1,037 are delisted or inactive. — [NSEDATA4ME README](https://github.com/ancap97/NSEDATA4ME). Confirmed in this session: the snapshot contains DHFL (to 11 Jun 2021), Ranbaxy (to 1 Apr 2015), HDFC Ltd (to 12 Jul 2023), Satyam (to 3 Jul 2013), Unitech and Reliance Communications. **[own inspection]**
- **Free vendors drop them.** One author recovered from bhavcopies six companies that "a free data vendor had simply erased", matching at 0.997+ return correlation on overlapping dates. — [NegativeZone blog, 28 Jul 2026](https://negativezone.github.io/2026/07/28/market_heuristics.html). Another, relying on Yahoo, found "no free tradable price series" for 318 former Nifty 500 names and lists 154 symbols Yahoo could not serve. — [rishabhjain0295-web README](https://github.com/rishabhjain0295-web/nifty500-momentum-backtest)
- **Yahoo's old Indian data is dirty.** 110 of about 1,089 symbols had an implausible more-than-3× one-day jump in 1998–2007, "almost certainly unadjusted splits/mergers/symbol reuse" (for example Kansai Nerolac, about 40× between May 2004 and June 2005). — [rishabhjain0295-web README](https://github.com/rishabhjain0295-web/nifty500-momentum-backtest)

**The work involved**
- **Download.** About 3,900 bhavcopy files and as many index files for 2011 → 2026; 4 to 5 hours at one request every 2 seconds, resumable; corporate actions about 15 minutes; "a few gigabytes" of disk. — [NSE-noodles docs/getting-started.md](https://github.com/abhij1306/NSE-noodles). Another tool estimates about 4,300 files from 2009. — [nsepit README](https://github.com/NegativeZone/nsepit)
- **Rate limits and blocking.** Projects wait 1.2–2 seconds between requests, never run two pulls at once, and refresh cookies after an HTTP 401 or 403; "NSE can block automated requests for some time". The `www.nseindia.com/api` endpoints "are not a documented public API and can change or block". — [NSEDATA4ME README](https://github.com/ancap97/NSEDATA4ME); [NSE-noodles README](https://github.com/abhij1306/NSE-noodles). niftyindices.com silently stalls on non-browser User-Agent strings and uses Akamai bot detection. — [satwikbasu/indian-market-data-endpoints](https://github.com/satwikbasu/indian-market-data-endpoints)
- **Adjustment is the hard part.** A 1:1 bonus looks like a 50% crash in raw data. NSE's feed carries no demerger ratio; rights issues and demergers need manual research; ISIN changes must be chained on evidence; each factor should be checked against the ex-date price gap, with anything unconfirmed sent to a review list. — [NSE-noodles README and method.md](https://github.com/abhij1306/NSE-noodles)
- **Known holes in the ready-made database.** NSEDATA4ME adjusts for splits and bonuses but not dividends or rights; demergers with a price gap under 2% are not applied; index history starts 21 Feb 2012. Its corporate-action table has 27,324 rows and 16 manual overrides. — [NSEDATA4ME README, "Limits"](https://github.com/ancap97/NSEDATA4ME); row counts **[own inspection]**
- **Residual errors [own computation].** In NSEDATA4ME's adjusted panel (3,709 main-board series, 5,407 trading days from 3 Jan 2005) there were 409 one-day adjusted returns above +60%, most likely unhandled corporate actions; these were set to zero in the calculations in section 6. Data: [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME)
- **Ready-made snapshot.** NSEDATA4ME publishes its processed data (about 430 MB of Parquet, one file per security with an adjustment factor) on a `data` branch, refreshed every week or two; `sync.py` then tops up from NSE daily. Cloning that branch took under a minute in this session. — [NSEDATA4ME README](https://github.com/ancap97/NSEDATA4ME)
- **Licensing.** NSE's terms restrict reproduction and redistribution of its data; projects either ship code only or warn users not to republish. — [nsepit README](https://github.com/NegativeZone/nsepit); [manan0308 KNOWN_LIMITATIONS.md](https://github.com/manan0308/india-nifty-momentum-backtest); [NSE terms of use](https://www.nseindia.com/static/nse-terms-of-use)
- **Downloaders.** Plain bhavcopy downloaders remain available and maintained. — [BennyThadikaran/NseIndiaApi](https://github.com/BennyThadikaran/NseIndiaApi); [tilak999/NSE-Data-bank](https://github.com/tilak999/NSE-Data-bank); [girishg4t/nse-bse-bhavcopy](https://github.com/girishg4t/nse-bse-bhavcopy) (NSE and BSE); jugaad-data, nsepython and bhavkit were covered in the earlier notes.
- **Broker data.** One project refreshes daily prices for all current NSE symbols and index histories from 2013 through the Dhan API. — [manan0308 docs/provenance/SOURCES.md](https://github.com/manan0308/india-nifty-momentum-backtest). Zerodha's historical data is adjusted for splits and bonuses but not dividends (earlier notes). — [Kite forum](https://kite.trade/forum/discussion/comment/21017)
- **Total-return index data is free too.** niftyindices.com serves daily TRI for every Nifty index from inception in one POST call (`/Backpage.aspx/getTotalReturnIndexString`), provided a browser-like User-Agent is sent. — [satwikbasu/indian-market-data-endpoints, endpoints/niftyindices-tri-api.md](https://github.com/satwikbasu/indian-market-data-endpoints)

### Inferences
- Realistic effort for a hobbyist in late 2026: **about a day** to get a survivorship-free, split/bonus-adjusted daily price panel by cloning NSEDATA4ME (or running NSE-noodles for 2011 onward), plus **a weekend** to rebuild Nifty 100 membership (section 4). Building the adjustment pipeline from scratch is weeks of work and not worth repeating.
- What remains imperfect whatever route is taken: dividends (ignore them and compare against price indices, or add about 1.2–1.5% a year), demergers, the final value of delisted shares, and a few hundred bad ticks that need a filter.
- The right way to treat a delisting in a back-test matters little for momentum (a stock heading for insolvency rarely has top-decile momentum) but matters for equal-weight and value screens. Freezing at the last traded price, as done here, is optimistic for insolvencies such as DHFL, where shareholders received nothing.
- The reader's bot should fetch from a home or residential connection on a schedule; whether NSE serves these files to cloud or serverless IP ranges was not established here.

### Gaps
- No evidence was gathered on NSE blocking cloud or data-centre IP addresses specifically (the sites were unreachable from this session for a different reason, the session's own network policy).
- BSE bhavcopy URL patterns and coverage were not checked.
- Unverified in this session (from memory; check before relying on them): Zerodha Kite Connect is believed to cost ₹500 a month since early 2025 with historical data included; Upstox, Fyers, Angel One and Dhan are believed to offer free historical candles to account holders; broker APIs key history to the current instrument list and therefore do not serve delisted symbols; EODHD lists NSE tickers and sells delisted-ticker access mainly for US markets; Norgate has no Indian data; TrueData and Global Datafeeds are paid authorised vendors. None of these pricing pages could be opened.
- The EOD2 claim of history "since 1995" and its handling of delisted stocks was not tested.

---

## 6. How big is survivorship bias, globally and in India, and why "today's Nifty 100" inflates momentum most

### Takeaway
Measured directly in this session, using today's list instead of point-in-time membership adds about **8–9 points a year** to an equal-weight Nifty 50 or Nifty 100 portfolio over 2011–2026 and about **9–10 points a year** to a 10–15 stock quarterly momentum portfolio. On true point-in-time Nifty 50 membership the same momentum rule returned about 8–11% a year (price only, before costs and tax), within 0–2 points of simply equal-weighting the index. That is far larger than the 1–4 points usually quoted from US fund studies, because roughly half of a large-cap Indian index is replaced each decade and the replaced half earned about zero.

### Cited Findings

**Global literature**
- Brown, Goetzmann, Ibbotson and Ross (1992) showed that conditioning on survival creates apparent performance persistence that is not real. — [Review of Financial Studies 5(4)](https://doi.org/10.1093/rfs/5.4.553) **[recalled]**
- Elton, Gruber and Blake (1996) put survivorship bias in US mutual-fund returns at about 0.9% a year. — [Review of Financial Studies 9(4)](https://doi.org/10.1093/rfs/9.4.1097) **[recalled]**
- Shumway (1997) found that stocks delisted for performance reasons lose about 30% on delisting on average, a return missing from the standard database, so strategies that hold such stocks are flattered. — [Journal of Finance 52(1)](https://doi.org/10.1111/j.1540-6261.1997.tb03818.x) **[recalled]**

**India-specific published estimates**
- Ranse (arXiv, Mar 2026): survivor-only equal-weight back-tests of the Nifty Smallcap 250 universe overstate annual return by 4.94 points (2016–2025); index turnover was 82.5% over the period, with 16.1% of names delisted (earlier notes). — [arXiv 2603.19380](https://arxiv.org/abs/2603.19380)
- A hobby project reports that correcting for survivorship cut a momentum strategy's Sharpe ratio from about 1.5 to about 1.0, an inflation of "+0.4 to +0.9 Sharpe depending on universe", and that after correction the broad Nifty 500 universe held up best. Self-reported, not verified. — [ReaperOAK/survivorship-free-backtester README](https://github.com/ReaperOAK/survivorship-free-backtester)
- Another author states that the bias "is not a constant you can subtract. It varies several-fold across strategy families, and it's worst for exactly the families that concentrate in names heading for trouble"; no numbers are published. — [NegativeZone blog](https://negativezone.github.io/2026/07/28/market_heuristics.html)
- The IIM-A factor returns are survivorship-adjusted and still show momentum (earlier notes), so the factor is real; it is the size of a retail back-test that is in doubt. — [IIMA data library](https://faculty.iima.ac.in/iffm/Indian-Fama-French-Momentum/)
- The reader's own control: an equal-weight portfolio of today's Nifty 100 members returned 19.56% a year after tax (2011–2026) against 9.47% for NIFTYBEES. — earlier notes, `thunderbot_backtests.md`

**Index churn [own computation]** from NSE's `IndexInclExcl.xls` (copy in [rishabhjain0295-web repo](https://github.com/rishabhjain0295-web/nifty500-momentum-backtest)) and the Wikipedia-derived Nifty 50 change table in [nsepit](https://github.com/NegativeZone/nsepit):

| Index | Exclusions recorded | Typical exclusions per year | Members on 1 Jan 2011 gone by Jul–Sep 2020 | Members on 1 Apr 2005 gone by 2020 |
|---|---|---|---|---|
| Nifty 50 | 98 (Sep 1996 – Jul 2020) | 2–7 (about 7% of the index) | 20 of 50 (40%) — the same count from both sources | 24 of 50 (48%) |
| Nifty 100 | 168 (Mar 2003 – Jul 2020) | 5–16 (about 9%) | about 49 of 100 | about 59 of 100 |
| Nifty 200 | 233 (Nov 2011 – Jul 2020) | 18–45 (about 13%) | — | — |
| Nifty 500 | 997 (Aug 1998 – Sep 2020) | 26–105 (9–13%) | about 47% | about 58% |

- The Nifty 100/500 cohort counts are inferred from event sequences by company name and may be slightly overstated where a company was renamed between its inclusion and exclusion.
- **Nifty 50 to the present:** of the 50 members on 1 Jan 2011, 26 were still members after the September 2025 review and 24 had gone; of the 1 Apr 2005 members, 23 remain. Of the July 2020 members, 11 have since left. — computed from [nsepit data](https://github.com/NegativeZone/nsepit)
- **What happened to the ones that left [own computation].** Price-only return from 3 Jan 2011 to 26 Oct 2026 (delisted names frozen at their last traded price): the 26 that stayed had a median return of +9.9% a year; the 24 that left had a median of −0.1% a year and a mean of −2.4%. Twelve of the 24 lost money in absolute terms and 7 no longer trade. Worst: Reliance Communications −28.1% a year, Reliance Capital −22.4%, JP Associates −21.4%, Reliance Infrastructure −16.6%, Reliance Power −13.3%. For the 1 Jan 2016 cohort: 32 stayed (median +10.5% a year), 18 left (median +6.0%, mean +2.0%); worst Idea Cellular −20.1%, Yes Bank −18.3%, Zee −16.0% a year. Prices: [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME)
- **Named casualties and their index exits** (NSE file): Jaiprakash Associates entered the Nifty 50 on 22 Oct 2009, left it on 28 Mar 2014, left the Nifty 200 on 1 Apr 2016 and the Nifty 500 on 27 Sep 2019; DHFL left the Nifty 200 on 27 Sep 2019 and the Nifty 500 on 26 Jun 2020; Indiabulls Housing entered the Nifty 50 on 31 Mar 2017, left on 27 Sep 2019 and left the Nifty 100 on 26 Jun 2020; Idea Cellular left the Nifty 50 on 31 Mar 2017; Jet Airways, Lanco Infratech, IVRCL, Gitanjali Gems, Educomp, Deccan Chronicle, Amtek Auto, Bhushan Steel, Cox & Kings, PC Jeweller and Punj Lloyd all left the Nifty 500 between 2013 and 2020. — [IndexInclExcl.xls copy](https://github.com/rishabhjain0295-web/nifty500-momentum-backtest)
- **Liquid-universe view [own computation].** Of the 100 most heavily traded NSE stocks on 31 Mar 2006, 34 no longer trade; of those on 31 Dec 2010, 21; on 31 Dec 2015, 8; on 31 Dec 2020, 3. Only 43 of the 100 most-traded stocks at the end of 2010 are in today's Nifty 100. Across the whole exchange, 1,037 of 4,583 securities (23%) in the database are delisted or inactive. Data: [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME)

**Direct measurement of the bias [own computation]**
Method: adjusted closes from [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME) (split/bonus-adjusted, price only); point-in-time Nifty 50 membership from [nsepit](https://github.com/NegativeZone/nsepit); today's Nifty 100 list from [rishabhjain0295-web](https://github.com/rishabhjain0295-web/nifty500-momentum-backtest). Quarter-end re-rank, trade one day later, equal weight. Momentum score = z-score of 6-month return ÷ 1-year volatility plus z-score of 12-month return ÷ 1-year volatility. "Keep" = hold an existing position while it ranks inside that number. No costs, no tax, no dividends, no market filter.

*Check on the data:* the rebuilt point-in-time Nifty 50, equal-weighted, returned 10.5% a year from April 2017 against 11.0% for NSE's official Nifty50 Equal Weight price index, and 10.2% from March 2012 against 10.4% for the Nifty 50 price index.

| Universe | Strategy | CAGR Jan 2011 – Oct 2026 | Max DD | CAGR Apr 2006 – Oct 2026 | Max DD | One-way turnover / yr |
|---|---|---|---|---|---|---|
| **Point-in-time Nifty 50** | Equal weight, all members | 8.7% | −41.5% | 9.6% | −58.3% | 27% |
| | Momentum top 10 | 8.3% | −37.6% | 8.8% | −59.5% | 177% |
| | Momentum top 10, keep 17 | 10.6% | −37.7% | 11.1% | −63.3% | 119% |
| | Momentum top 15, keep 25 | 10.3% | −38.8% | 10.6% | −61.5% | 91% |
| **Today's Nifty 50 applied backwards** | Equal weight | 16.4% | −38.0% | 17.7% | −56.2% | 22% |
| | Momentum top 10 | 18.5% | −37.9% | 17.8% | −60.9% | 170% |
| | Momentum top 10, keep 17 | 19.8% | −40.9% | 17.7% | −62.7% | 117% |
| | Momentum top 15, keep 25 | 20.4% | −40.2% | 18.8% | −62.4% | 78% |
| **Today's Nifty 100 applied backwards** (the reader's set-up) | Equal weight | 18.2% | −37.6% | 19.4% | −55.2% | 24% |
| | Momentum top 15 | 25.1% | −39.3% | 24.5% | −61.5% | 178% |
| | Momentum top 15, keep 25 | 25.3% | −38.8% | 24.3% | −61.2% | 124% |
| | Momentum top 30, keep 45 | 22.0% | −37.5% | 22.0% | −57.5% | 82% |

- **Bias in the Nifty 50 universe, 2011–2026:** equal weight +7.7 points a year (16.4% vs 8.7%); momentum top 10 +10.2; top 10 keep 17 +9.2; top 15 keep 25 +10.1. Over 2006–2026: +8.1, +9.0, +6.6 and +8.2.
- **Bias in the Nifty 100 universe, equal weight:** today's list returned 21.2% a year from 10 Jun 2013 against 12.1% for NSE's official Nifty100 Equal Weight price index over the same dates: **+9.1 points a year**. From March 2012 it returned 20.0% against 10.8% for the cap-weighted Nifty 100 price index.
- **Momentum's edge over equal weight is itself inflated.** In today's-list Nifty 50 the three momentum variants beat equal weight by +2.1, +3.4 and +4.0 points a year (2011–2026). On point-in-time membership the same variants scored −0.4, +1.9 and +1.6.
- **The reader's numbers are reproduced.** Today's-list Nifty 100 momentum top 15 gives 25% a year gross here, in line with the reader's 18.5–28% pre-tax range.
- **Sensitivity with a liquidity-ranked universe** (top 100 or 200 by 6-month median traded value at each date; a poor proxy for the index, see section 4):

  | Universe | Equal weight | Momentum top 15 | Top 15 keep 25 | Top 30 keep 45 |
  |---|---|---|---|---|
  | Point-in-time liquid 100, 2011–2026 | 6.9% | 11.7% (DD −47.9%) | 11.7% | 11.5% |
  | End-date liquid 100 applied backwards | 20.1% | 31.0% | 34.0% | 24.9% |
  | Point-in-time liquid 200, 2011–2026 | 8.2% | 20.5% (DD −47.2%) | 21.3% | 18.8% |
  | Point-in-time liquid 200, 2006–2026 | 8.7% | 15.1% (DD −80.3%) | 15.5% | 15.6% |
  | Point-in-time liquid 200, Apr 2006 – Dec 2010 | 10.4% | −1.3% | −1.9% | 5.5% |
  | End-date liquid 200 applied backwards, 2011–2026 | 19.1% | 35.9% | 37.7% | 30.2% |

  Turnover of the point-in-time liquid-universe momentum portfolios was 125–250% a year.

### Inferences
- **Why momentum is hit hardest.** Today's list is, by construction, the set of stocks whose prices rose enough to get in and never fell enough to be thrown out. A momentum rule ranks on past price rises, so inside that set almost every "winner" it buys is known in advance to have kept winning, and the stocks that had strong momentum just before collapsing (Reliance Communications in 2007, JP Associates in 2009–10, Yes Bank and Indiabulls Housing in 2017, Zee, DHFL) are not there to be bought. Equal weighting only gains from the absence of losers; momentum gains from that and from look-ahead in selection.
- **Honest expectation for the reader's strategy.** Take the official Nifty100 Equal Weight or Nifty 100 price return (about 11–12% a year since 2012–13), add 0 to 2 points for large-cap quarterly momentum, add about 1.3 points of dividends: roughly 12–15.5% gross. After 0.5–1.5 points of costs and 1.5–2.5 points of tax (section 7) that is roughly **9–13% a year**, against the 21% the biased back-test shows and against 9.5% for NIFTYBEES over the reader's window. These base figures end in a falling market (the Nifty 50 was down 12.9% in 2026 to 26 Oct).
- The reader's rule of thumb ("almost all of it is survivorship") is confirmed for large caps. On the Nifty 50 over 2011–2026, today's-list momentum (20.4% a year, top 15 keep 25) beat the point-in-time equal-weight index (8.7%) by 11.7 points: 7.7 came from the universe alone, about 2.4 from look-ahead inflating the momentum edge, and 1.6 from momentum itself.
- Momentum looked materially stronger in a broader liquid universe (top 200) over 2011–2026 even point-in-time, which fits the earlier finding that the Indian premium sits in mid-caps and less liquid names. But that portfolio lost 80% in 2008–09, made nothing for the first five years, and rests on a proxy universe and partly unadjusted data; treat it as a lead to test properly, not as a result.
- Global rules of thumb (1–4 points) understate the problem for Indian index-based back-tests, because Indian index turnover is high (7–13% of names a year) and the stocks that left the Nifty 50 after 2011 had a median return of about zero.

### Gaps
- The Nifty 100 momentum strategy itself was not run on true point-in-time Nifty 100 membership (only the equal-weight comparison uses official data); the momentum bias figure rests on the Nifty 50 reconstruction and the liquidity proxy.
- Results are price-only and gross of costs and tax, use last-traded price for delisted shares, and depend on one third-party adjusted data set with known gaps (dividends, rights, small demergers, 409 neutralised outliers). They are single runs with no robustness testing of lookbacks or rebalance dates.
- No published, peer-reviewed estimate of survivorship bias for the Nifty 50/100/200 or for Indian momentum was found.
- "Wealth creation study" churn statistics from Motilal Oswal, Marcellus or Capitalmind were not retrieved.
- Videocon, Unitech, Suzlon, Reliance Capital and Yes Bank exit dates from the Nifty 100/200/500 were not extracted individually (the Nifty 50 exits are in the nsepit change table).

---

## 7. DIY 15 stocks versus a momentum ETF or index fund: turnover, costs, tax and the break-even

### Takeaway
At the same gross return, a momentum index fund beats a self-run 15-stock portfolio by roughly 1–4 points a year after costs and tax for a ₹1–20 lakh investor (most at ₹1 lakh, least at ₹20 lakh), because the fund rebalances tax-free inside the wrapper and the investor pays 12.5% only on exit (and can often pay nothing by using the ₹1.25 lakh annual exemption), whereas the DIY investor pays 20% on most realised gains every year plus 0.4–2% in trading frictions. The DIY portfolio therefore needs about 1–3.5 points a year of gross alpha over the Nifty200 Momentum 30 index just to tie, and the honest evidence in section 6 is that a 15-stock large-cap momentum rule has delivered about 0–2.

### Cited Findings

**Turnover**
- Official Nifty200 Momentum 30 (semi-annual, 30 stocks, rank buffer): 101–134% of index weight replaced a year in FY22–FY26; a quarterly variant would be 123–167% (earlier notes). — [NSE whitepaper Apr 2026, Exhibit 11](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf)
- Quarterly 15-stock momentum **[own computation, section 6]**: 165–220% a year one-way with a strict top-15 rule; 113–167% with a "keep while in the top 25" buffer; 78–125% for 30 stocks with a top-45 buffer. On true Nifty 50 membership: 177% (top 10), 119% (top 10 keep 17), 91% (top 15 keep 25).
- NSE's own test found semi-annual rebalancing beat quarterly for Momentum 30 (19.19% vs 17.12% since 2005) (earlier notes). — [NSE whitepaper, Exhibits 8–10](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf)

**Cost per trade and annual drag [own computation]** from the Groww and Zerodha tariffs in the earlier notes (`costs_and_taxes.md`: Groww brokerage min(₹20, 0.1%) with a ₹5 floor, DP ₹20 + GST per sell; Zerodha zero delivery brokerage, DP ₹15.34 per sell; STT 0.1% each side; stamp 0.015% on buys; exchange 0.00307%; GST 18%). — [Groww pricing](https://groww.in/pricing); [Zerodha charges](https://zerodha.com/charges)

| Capital | Position (÷15) | Groww round trip | of which fixed (brokerage + DP + GST) | Zerodha round trip | of which fixed |
|---|---|---|---|---|---|
| ₹1 lakh | ₹6,667 | ₹54 = 0.81% | 0.59% | ₹30 = 0.45% | 0.24% |
| ₹5 lakh | ₹33,333 | ₹145 = 0.43% | 0.22% | ₹90 = 0.27% | 0.05% |
| ₹20 lakh | ₹1,33,333 | ₹367 = 0.28% | 0.06% | ₹312 = 0.23% | 0.02% |

Annual drag as a percentage of capital, including 0.05% slippage per side:

| One-way turnover | Capital | Groww | Zerodha | If every surviving position is also re-equalised each quarter (Groww / Zerodha) |
|---|---|---|---|---|
| 120% | ₹1 lakh | 1.09% | 0.66% | 1.87% / 1.02% |
| 120% | ₹5 lakh | 0.64% | 0.44% | 0.82% / 0.54% |
| 120% | ₹20 lakh | 0.45% | 0.40% | 0.54% / 0.45% |
| 170% | ₹1 lakh | 1.55% | 0.94% | 2.19% / 1.23% |
| 170% | ₹5 lakh | 0.91% | 0.63% | 1.06% / 0.70% |
| 170% | ₹20 lakh | 0.64% | 0.57% | 0.71% / 0.61% |

- The irreducible part (STT both sides, stamp duty, slippage) is about 0.32% of turnover, or about 0.4% a year at 120% turnover, whatever the account size.
- If the portfolio is run through Groww's paid API (₹4,999 + GST = ₹5,899 a year, earlier notes), that adds 5.9% a year at ₹1 lakh, 1.2% at ₹5 lakh and 0.3% at ₹20 lakh. — [Groww blog: API trading](https://groww.in/blog/api-trading-on-groww)

**What the fund costs** — AMFI tracking data as compiled in [patel-26meet/nse-strategy-indices-visualised, data/funds_tracking_amfi.json](https://github.com/patel-26meet/nse-strategy-indices-visualised) (tracking difference as of 1 Jul 2026, tracking error as of 28 Aug 2026; negative = fund behind its TRI):

| Nifty200 Momentum 30 product | Tracking error | 1-year tracking difference | 3-year | Since launch |
|---|---|---|---|---|
| ETFs (HDFC, ICICI Pru, ABSL, Motilal, Kotak) | 0.22–0.44% | −0.53% to −0.84% | −0.56% to −0.66% | −0.47% to −0.85% |
| Index funds, direct plans (UTI, Kotak, ICICI Pru, HDFC, SBI, Bandhan, Motilal, Baroda BNP) | 0.15–0.47% | −0.56% to −1.15% (median −0.80%) | −0.35% to −1.03% | −0.49% to −1.06% |
| Index funds, regular plans | similar | −1.02% to −1.80% | −0.88% to −1.73% | −1.06% to −1.75% |
| UTI Nifty200 Momentum 30 Index Fund (oldest) | 0.15% | −0.56% direct | −0.35% direct | 5-year −0.37% direct; −0.92% regular |

- For comparison, the median Nifty 50 index fund's 1-year tracking difference is −0.18% (direct) and −0.34% (regular), and funds on Low Vol 30 and Quality 30 have median tracking error of 0.07–0.10%. Momentum funds are 3–4 times harder to run. — [same source](https://github.com/patel-26meet/nse-strategy-indices-visualised)
- Midcap and Nifty 500 momentum funds are costlier: median 1-year tracking difference −0.82% direct, with Tata's and Edelweiss's Midcap150 Momentum 50 funds at −1.30% and −1.03% a year over 3 years. — [same source](https://github.com/patel-26meet/nse-strategy-indices-visualised)
- Fund houses tracking an identical basket differ by up to 0.51 points a year in what they deliver. — [patel-26meet README](https://github.com/patel-26meet/nse-strategy-indices-visualised)
- An ETF additionally needs a demat account, pays brokerage and DP charges on sale, and trades at a spread; STT on ETF sales is 0.001% (earlier notes). An index fund's direct plan has no transaction cost beyond 0.005% stamp duty on purchases. — [Groww help: STT](https://groww.in/help/stocks,-f&o,-ipo-&-mtf/sx-pricing/what-is-stt)

**Tax**
- Listed shares and equity fund units: short-term gains (held 12 months or less) 20%, long-term 12.5% above ₹1.25 lakh a financial year, unchanged in Budget 2026; with 4% cess, 20.8% and 13% (earlier notes). — [Quicko](https://learn.quicko.com/ltcg-equity-shares-equity-mutual-funds); [Bajaj Finserv](https://www.bajajfinserv.in/what-is-ltcg-tax-rate)
- A SEBI-registered mutual fund pays no tax on gains it realises when it rebalances (section 10(23D) of the Income-tax Act 1961; renumbered under the Income-tax Act 2025); the unit-holder is taxed only on redemption. — [Income Tax Department, Income-tax Act](https://incometaxindia.gov.in/Pages/acts/income-tax-act.aspx) **[recalled; section text not opened]**
- In the reader's own back-tests the tax drag was 2.4 points a year on an 18.5% pre-tax return for the quarterly 15-stock variant (13% of the return), 3.4 points on 24.8% for monthly, and 1.9 points on 20.2% for semi-annual, at ₹5 lakh capital with loss offsets and the ₹1.25 lakh exemption. — earlier notes, `thunderbot_backtests.md`
- An independent semi-annual replication found about 80% of gains taxed as short-term and a gross-to-net gap (costs plus tax) of 1.22 points on 15.2% (earlier notes). — [BacktestIndia](https://backtestindia.com/blog/momentum-investing-india-backtest)
- Israel and Moskowitz, "How Tax Efficient Are Equity Styles?" (2012): in US data momentum, despite much higher turnover than value, carried a similar or lower tax burden because it tends to realise losses short-term and gains long-term, while value is taxed on dividends. — [SSRN 2089459](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2089459) **[recalled]**
- Frazzini, Israel and Moskowitz, "Trading Costs of Asset Pricing Anomalies": using about a trillion dollars of live institutional trades, actual trading costs were far below earlier academic estimates and momentum survived them at large scale. — [SSRN 2294498](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2294498) **[recalled]**

**Worked example [own computation]** — same gross return for the index and the DIY portfolio; fund lags its index by 0.8% a year; fund held, then redeemed with 13% tax on the whole gain; DIY taxed each year.

| Gross return | Fund, held 5 y | Fund, held 10 y | Fund if gains stay within the ₹1.25 lakh exemption | DIY, all gains short-term (20.8%), costs 0.5% / 1.0% / 1.5% | DIY at the reader's observed 13% effective rate, costs 1.0% |
|---|---|---|---|---|---|
| 12% | 9.98% | 10.22% | 11.20% | 9.11% / 8.71% / 8.32% | 9.57% |
| 15% | 12.72% | 13.06% | 14.20% | 11.48% / 11.09% / 10.69% | 12.18% |
| 18% | 15.48% | 15.93% | 17.20% | 13.86% / 13.46% / 13.07% | 14.79% |

**Break-even gross alpha the DIY portfolio needs over the index** to match the fund held 10 years:

| Gross index return | Costs 0.5% (≈ ₹20 lakh) | Costs 1.0% (≈ ₹5 lakh) | Costs 1.5% (≈ ₹1 lakh) | If the fund's gains are harvested tax-free, costs 1.0% |
|---|---|---|---|---|
| 12% | +1.4 (all short-term) / +1.0 (70% short, 30% long) | +1.9 / +1.5 | +2.4 / +2.0 | +3.1 |
| 15% | +2.0 / +1.5 | +2.5 / +2.0 | +3.0 / +2.5 | +3.9 |
| 18% | +2.6 / +2.0 | +3.1 / +2.5 | +3.6 / +3.0 | +4.7 |

- At the reader's observed 13% effective tax rate and 1.0% costs, the break-even alpha is about +0.7 points at 12% gross, +1.0 at 15% and +1.3 at 18%.
- **The ₹1.25 lakh exemption.** A fund holder whose yearly gain is under ₹1.25 lakh can sell and rebuy after a year and pay no tax at all; at 12–18% returns that covers a corpus of roughly ₹7–10 lakh (₹1.25 lakh ÷ 0.18 = ₹6.9 lakh; ÷ 0.12 = ₹10.4 lakh). Short-term gains in a DIY account get no such exemption.

**Concentration [own computation, section 6]**
- On point-in-time Nifty 50 membership (2011–2026), three near-identical momentum variants returned 8.3% (top 10), 10.6% (top 10 keep 17) and 10.3% (top 15 keep 25): about 2 points a year of pure implementation noise.
- Volatility was 18.0% for 10 stocks against 17.1% for 15; in the liquid-100 universe, 22.3% for 15 stocks against 20.3% for 30, with maximum drawdown −47.9% against −39.2%.
- Momentum 30's own top-10 weights sum to 49% (Jun 2026, earlier notes). — [HDFC AMC deck](https://files.hdfcfund.com/s3fs-public/Others/2026-07/HDFC%20NIFTY200%20Momentum%2030%20Index%20Fund_PPT%20%28July%202026%29.pdf)

**Practitioner views**
- Freefincal on the UTI momentum fund at launch: about five times the cost of a Nifty index fund, which shrinks any outperformance; "periods of momentum outperformance will be followed by underperformance". — [Freefincal](https://freefincal.com/nifty200-momentum-30-index-a-new-strategy-index-from-the-nse/) **[search summary]**
- A hobbyist's after-tax simulator "shows tax is the great equalizer between active strategies and buy-and-hold"; "after Indian tax, high-turnover strategies barely out-earn buy-and-hold; the win is a smoother ride". Self-reported. — [ReaperOAK/survivorship-free-backtester README](https://github.com/ReaperOAK/survivorship-free-backtester)

### Inferences
- **Where fixed costs stop mattering.** At a zero-brokerage broker the fixed part of a round trip falls to 0.05% by ₹5 lakh; at Groww it is 0.22% at ₹5 lakh and 0.06% at ₹20 lakh. So fixed charges are a real handicap at ₹1 lakh (0.6–1.5% a year), minor by ₹5 lakh and negligible at ₹10–20 lakh. Tax, not brokerage, is the durable disadvantage, and it does not shrink with size; it grows, because the ₹1.25 lakh exemption covers less of the gain.
- **By account size, at equal gross return:**
  - **₹1 lakh:** the fund wins by about 2–4 points a year (DIY costs 1.1–2.2%, tax about 2–3%, against a fund costing 0.6–0.8% with no tax in practice). DIY is not rational on returns.
  - **₹5 lakh:** the fund wins by about 1.5–3 points (DIY costs 0.6–1.1%, tax about 2–3%; a 15% gain is ₹75,000 a year, still inside the exemption).
  - **₹20 lakh:** the fund wins by about 0.5–2.5 points (DIY costs 0.45–0.7%, tax about 2–3%; the fund holder pays about 13% on the part of the gain above the exemption, sooner or later).
- **Verdict on alpha.** DIY needs roughly +1 to +3.5 points a year over the Nifty200 Momentum 30 index to tie. Evidence that a 15-stock quarterly Nifty-100 rule can deliver that: none. The official index's own live edge over the Nifty 200 is +0.4 to +2.8; NSE's test says quarterly is worse than semi-annual; the point-in-time large-cap test shows a 0–2 point edge over equal weight.
- Things DIY can do that a fund cannot: skip a rebalance to turn a short-term gain into a long-term one, harvest losses against other gains, apply a market filter to new purchases only, and avoid the index's pre-announced rebalance dates. None of these has been shown to be worth 1–3 points a year.
- **Behavioural risk** points the same way: 15 positions, 60–100 orders a year, and the temptation to override the rule after a −30% stretch such as September 2024 – April 2025. The cost of one skipped or discretionary rebalance is not measurable in a back-test.
- The fund's own weaknesses should be stated: 0.5–1.0% a year of tracking difference, a rule set NSE can change, crowded rebalances, and the live-performance shortfall of section 3. It is the better vehicle for the same strategy, not a promise of the back-tested return.

### Gaps
- No Capitalmind, Freefincal, Weekend Investing or Alpha Architect article comparing DIY momentum with a momentum index fund after Indian costs and tax was opened; whether such a published comparison exists is unknown.
- Current TERs of the Momentum 30 funds were not collected (another researcher is covering the funds); the AMFI tracking-difference data are as of 1 Jul 2026.
- The worked example assumes equal gross returns, a flat tax rate each year, and no surcharge; it ignores dividends (taxed at slab in a DIY account, reinvested untaxed inside a growth-plan fund, which favours the fund a little more).
- ETF bid-ask spreads and premium/discount to NAV for momentum ETFs were not measured.
- The Income-tax Act 2025 section that replaces section 10(23D) was not confirmed.

---

## 8. Does a trend filter (200-DMA or 10-month average) on a momentum index or portfolio help or hurt, before and after tax?

### Takeaway
The evidence is mixed and period-dependent. A month-end "Nifty 50 above its 200-day average" switch roughly halved the drawdown of a momentum portfolio in every period tested and added a great deal in 2008, but over 2011–2026 it cost 0.7 points a year before tax and 1.6 after; on the Nifty 50, Nifty 200, Low Vol 30 and Alpha 50 it cost 2–3 points a year after tax. On the live Momentum 30 index (2020–2026) the same switch helped by about 4 points a year after tax, yet a switch based on the momentum index's own 200-day average hurt by about 4 points and did not reduce the drawdown. Tax adds roughly 0.6–1.2 points a year to the cost of filtering.

### Cited Findings

**Literature**
- Daniel and Moskowitz (2016), "Momentum crashes": momentum's worst losses come in rebounds after market declines, when volatility is high; the long-short strategy's crashes (1932, 2009) are driven by the loser leg rallying; a dynamic strategy that scales exposure by forecast return and variance roughly doubles the Sharpe ratio. — [Journal of Financial Economics 122(2)](https://doi.org/10.1016/j.jfineco.2015.12.002) **[recalled]**
- Barroso and Santa-Clara (2015), "Momentum has its moments": scaling long-short momentum to constant volatility raised its Sharpe ratio from about 0.53 to about 0.97 and removed most of the crash risk. — [Journal of Financial Economics 116(1)](https://doi.org/10.1016/j.jfineco.2014.11.010) **[recalled]**
- Faber (2007): a 10-month moving-average rule on broad asset classes gave returns similar to buy-and-hold with much lower volatility and drawdown. — [SSRN 962461](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=962461) **[recalled]**
- Antonacci (2012): "absolute momentum" (hold only when the trailing 12-month return beats cash) as an overlay on relative momentum. — [SSRN 2042750](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2042750) **[recalled]**
- Indian factor data: the long-short momentum factor's worst months were April–May 2009 (−18.3%, −25.0%) and April 2020 (−13.5%), all in rebounds (earlier notes). — [IIMA data library](https://faculty.iima.ac.in/iffm/Indian-Fama-French-Momentum/)
- An IIM-A webinar on a systematic long-only momentum strategy in India (Rajan Raju presenting, March 2023) summarises that momentum "suffers bad times in the short (momentum crash) or even medium term". — [IIM Ahmedabad](https://iima.ac.in/eventswebinar-systematic-long-only-momentum-strategy-financial-markets-evidence-india) **[search summary]**

**Indian back-tests already on file (earlier notes)**
- Nifty 50 price index, Jul 2008 – Oct 2026: month-end 200-DMA rule 10.1% vs 10.0% buy-and-hold, drawdown −24% vs −45%; daily checking cost 2 points; 12-month absolute momentum returned only 4.4%. — own computation in `momentum_factor_evidence.md` from [Yahoo ^NSEI](https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI?period1=0&period2=1792000000&interval=1d)
- NIFTYBEES, 2011–2026, after tax and costs: 6.3–8.1% for four filter variants against 9.5% buy-and-hold (pre-tax), with drawdown −15% to −24% against −36%. — `thunderbot_backtests.md`
- In the reader's (survivorship-biased) momentum back-test the filter cut drawdown from −36.7% to −19.4% only when checked monthly; quarterly or semi-annual checks let the 2020 crash through. — `thunderbot_backtests.md`
- A hobby project's survivorship-corrected tournament picked "ensemble + regime-cash" (go to cash below the 200-day trend) as its winner, saying it "roughly halves drawdown (−38% → about −18%) — insurance, not free alpha". Self-reported. — [ReaperOAK/survivorship-free-backtester README](https://github.com/ReaperOAK/survivorship-free-backtester)
- Self-reported blog results (dual momentum 18.8% vs 12.1%; EMA-100 exit cutting drawdown from 48.6% to 19.1%) report no costs or tax (earlier notes). — [Momentum Lab](https://momentumlab.substack.com/p/backtesting-dual-momentum-strategy); [Quantinuous](https://quantinuous.substack.com/p/weekly-momentum-portfolio-protection)

**New tests [own computation]**
Rule: at each month-end, hold the asset next month if the signal series closed above its 200-day simple average, otherwise hold cash at 6.5% a year; 0.15% cost per switch. After-tax version: on every exit the gain since entry is taxed at 20.8% if held 365 days or less, otherwise 13%; losses are carried forward; cash interest is taxed at 31.2%; buy-and-hold pays 13% on the whole gain at the end; the ₹1.25 lakh exemption is ignored. Price indices only. Data: [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME); Nifty 50 before 2012 from the index file in [rishabhjain0295-web repo](https://github.com/rishabhjain0295-web/nifty500-momentum-backtest) (it matches the NSE file exactly on 3,591 overlapping days). "PIT momentum" is the point-in-time Nifty 50 top-15-keep-25 portfolio from section 6.

*Signal: Nifty 50 against its own 200-DMA*

| Asset | Period | Buy-and-hold CAGR / max DD | Filtered CAGR / max DD | Switches a year; time invested | After tax: buy-and-hold vs filtered |
|---|---|---|---|---|---|
| Nifty 50 | Apr 2006 – Oct 2026 | 9.7% / −59.9% | 9.8% / −29.9% | 1.8; 73% | 9.1% vs 8.2% |
| Nifty 50 | Jan 2011 – Oct 2026 | 8.6% / −38.4% | 6.7% / −22.8% | 2.1; 72% | 8.0% vs 5.5% |
| PIT momentum | Apr 2006 – Oct 2026 | 10.6% / −61.5% | 12.0% / −31.3% | 1.9; 73% | 9.9% vs 10.1% |
| PIT momentum | Apr 2006 – Dec 2010 | 11.3% / −61.5% | 20.4% / −31.3% | 0.8; 80% | 10.1% vs 17.7% |
| PIT momentum | Jan 2011 – Oct 2026 | 10.3% / −38.8% | 9.6% / −16.2% | 2.2; 71% | 9.6% vs 8.0% |
| Nifty200 Momentum 30 (live) | 25 Aug 2020 – Oct 2026 | 14.5% / −31.8% | 19.5% / −18.1% | 1.5; 76% | 13.0% vs 16.8% |
| Nifty Alpha 50 (live) | Mar 2013 – Oct 2026 | 19.5% / −40.7% | 17.6% / −34.0% | 2.0; 74% | 18.4% vs 15.2% |
| Nifty 200 | Mar 2012 – Oct 2026 | 11.2% / −38.2% | 9.1% / −22.0% | 2.0; 75% | 10.4% vs 7.7% |
| Nifty100 Low Vol 30 (live) | Jul 2016 – Oct 2026 | 10.4% / −31.0% | 8.4% / −18.9% | 2.0; 76% | 9.5% vs 7.0% |

*Signal: the asset's own 200-DMA*

| Asset | Period | Buy-and-hold CAGR / max DD | Filtered CAGR / max DD | Switches a year | After tax: buy-and-hold vs filtered |
|---|---|---|---|---|---|
| PIT momentum | Apr 2007 – Oct 2026 | 11.0% / −61.5% | 9.9% / −39.9% | 1.5 | 10.4% vs 8.2% |
| Nifty200 Momentum 30 (live) | Jul 2021 – Oct 2026 | 8.7% / −31.8% | 6.0% / −33.1% | 3.2 | 7.8% vs 4.0% |
| Nifty Alpha 50 (live) | Jan 2014 – Oct 2026 | 20.0% / −40.7% | 13.9% / −51.3% | 1.9 | 18.9% vs 11.7% |

- **Tax effect.** The filter's cost relative to buy-and-hold widened after tax by 0.6 points a year for the Nifty 50 (2011–2026: −1.9 before, −2.5 after), 0.9 points for point-in-time momentum (2011–2026: −0.7 before, −1.6 after) and 1.2 points for point-in-time momentum over 2006–2026 (+1.4 before, +0.2 after).
- **Current regime.** In October 2026 only 10 of 50 Nifty stocks were above their 200-DMA and the Nifty had spent a 160-day stretch below its own (earlier notes); the Nifty 50 price index was −12.9% for 2026 to 26 Oct and −15.6% from its January high at the 8 Oct low. — [Business Standard](https://www.business-standard.com/markets/news/nifty-s-200-day-moving-average-sounds-alarm-as-market-breadth-thins-126101401265_1.html); own computation from [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME)

### Inferences
- **What the filter reliably buys:** a maximum drawdown of roughly −16% to −34% instead of −31% to −62%, and about a quarter less volatility, when the signal is the broad market (Nifty 50) checked monthly. **What it costs:** about 2 switches a year, 25–30% of the time in cash, about 0–2 points a year of pre-tax return in markets without a 2008-style collapse, and a further 0.6–1.2 points in tax.
- **Its return benefit comes almost entirely from one episode.** Remove 2008 and the filter subtracted return on every series except the 6-year live Momentum 30 sample. The 2020 crash was too fast for a monthly 200-DMA rule to help much, and it then missed part of the rebound.
- **Use the market's trend, not the momentum index's own.** Filtering on the momentum index's own average did worse in all three tests and made the drawdown deeper in two of them, because momentum indices fall and rebound faster than the signal can react.
- **When the tax drag is worth paying.** Each exit crystallises gains at 20.8% if the units are under a year old and resets the holding clock, so an investor who would otherwise have paid nothing (inside the ₹1.25 lakh exemption) or 13% at the very end gives up 0.6–1.2 points a year. That is a reasonable price only if a −60% drawdown would cause the investor to abandon the plan, or if the money has a fixed date. For an investor adding monthly and able to hold through a deep loss, the filter has a negative expected return after tax on this evidence.
- **Cheaper ways to get most of the protection:** apply the filter to new money only (redirect SIPs to a liquid or arbitrage fund while the Nifty is below its 200-DMA, without selling); hold a fixed share in debt or low-volatility (the Momentum 30 + G-Sec 50:50 index had a −17.6% COVID drawdown with no trading by the investor); or exit only units that are already long-term.
- The live Momentum 30 result (+4 points after tax with a Nifty-50 filter) should not be extrapolated: it is six years, nine switches, and the same rule lost 3 points a year on Alpha 50 over thirteen.
- Volatility scaling, which the academic literature favours over on/off timing for momentum, was not tested here.

### Gaps
- No Freefincal, Capitalmind or Weekend Investing back-test of a trend filter on a momentum index was opened; one search for Freefincal's momentum-with-200-DMA articles found only its general fund reviews.
- No test on the official Momentum 30 index before August 2020 (no daily data), so the index's own 2008 behaviour under a filter is unknown; the 2006–2010 result uses this session's point-in-time Nifty 50 momentum portfolio as a stand-in.
- Tests are price-only, single-specification (200-day SMA, month-end check, 6.5% cash), ignore the ₹1.25 lakh exemption and surcharge, and model tax losses in one pool. A 10-month average, bands, and volatility scaling were not tried.
- No peer-reviewed Indian study of trend filters on momentum portfolios with costs and tax was found (unchanged from the earlier notes). The Daniel–Moskowitz, Barroso–Santa-Clara, Faber and Antonacci numbers are from memory.
