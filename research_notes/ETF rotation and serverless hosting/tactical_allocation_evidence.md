# Tactical ETF Rotation / Trend-Following Asset Allocation: Evidence for an Indian Retail Investor (Nifty 50, Next 50, Midcap, Gold, Liquid)

Researcher notes, compiled 11 Nov 2026. Read these labels before using any number:

- **(fetched)** = page opened and read this session.
- **(search excerpt)** = taken from a search-result summary; page not opened.
- **[own computation]** = calculated this session from AMFI NAV data (via mfapi.in) or Yahoo Finance monthly prices. These are back-tests, not live results, unless the row is a live fund's NAV.
- **(recalled, not re-verified)** = a figure from the primary paper that I know from training but could not re-open, because the host was blocked in this session. Treat as needing a check.
- **BACKTEST** and **LIVE** are kept in separate bullets or tables throughout.

Session limits that shaped these notes: the shared web-search budget ran out part-way through, and most hosts were blocked for page fetches (aqr.com, ssrn.com, cambriafunds.com, optimalmomentum.com, thinknewfound.com, weekendinvesting.com, smallcase.com, niftyindices API). Freefincal, Capitalmind, mfapi.in and Yahoo Finance were reachable. Where published sources could not be reached, I replaced them with own computations on primary price data and say so.

---

## Q1. Meb Faber's GTAA (10-month SMA): rule, backtest, and out-of-sample record 2007-2026

### Takeaway
The rule did what it promised on drawdown and failed on return. Out of sample (2007 to Nov 2026) a replication on the five original asset classes made about 5.4% a year with an 11% worst drawdown, against 7.7% for a 60/40 fund and 10.8% for the S&P 500. It lagged 60/40 in 14 of 19 calendar years, including nine in a row (2009-2017).

### Cited Findings
**The rule**
- Five asset classes at 20% each: US stocks, foreign developed stocks, US 10-year bonds, commodities, REITs. At each month-end, hold an asset if its price is above its 10-month simple moving average; otherwise hold that 20% slice in T-bills. Signals are checked only on the last day of the month. — [Faber, SSRN 962461](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=962461) (recalled, not re-verified); consistent with the five-asset, month-end description in [Concretum](https://concretumgroup.com/global-tactical-asset-allocation/) (search excerpt)

**BACKTEST (in-sample)**
- Original in-sample period 1972-2005: 11.7% CAGR, Sharpe 0.81. — [Concretum](https://concretumgroup.com/global-tactical-asset-allocation/) (search excerpt)
- Faber's 2013 update, 1973-2012: timing portfolio 10.48% a year, volatility 6.99%, worst drawdown -9.54%; buy-and-hold of the same five assets 9.92%, volatility 10.28%, worst drawdown -46.0%. — [Faber, SSRN 962461](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=962461) (recalled, not re-verified)
- A study by Zakamulin concluded that the reported performance of these market-timing strategies contains a substantial data-mining bias. — [Swedroe, ETF.com](https://www.etf.com/sections/index-investor-corner/swedroe-why-financial-trends-persist) (search excerpt)

**OUT OF SAMPLE (post-publication)**
- Faber's own 2013 review covered 2006-2012 out of sample and showed the timing strategy underperforming buy-and-hold in 2009 and 2010. — [Ritholtz, 2012](https://ritholtz.com/2012/01/revisiting-quant-approach-to-tactical-asset-allocation); [The 7 Circles](https://the7circles.uk/?p=35413) (search excerpts)
- Concretum, Jan 2006 - Mar 2025, same five assets, 200-day SMA checked at month-end, no re-tuning: CAGR 6.05%, Sharpe 0.68, max drawdown 11.7%. Returns "came in below the in-sample period". — [Concretum](https://concretumgroup.com/global-tactical-asset-allocation/) (search excerpt)
- **[own computation] Replication, Dec 2006 - Nov 2026**, ETFs SPY / EFA / IEF / VNQ / DBC, 10-month SMA at month-end, cash = BIL (SHY before May 2007), Yahoo adjusted monthly closes, no costs or tax:

  | Portfolio | CAGR 2007-Nov 2026 | Max drawdown (monthly) | CAGR 2007-2013 | CAGR 2014-Nov 2026 |
  |---|---|---|---|---|
  | Faber GTAA-5, 10-month SMA | 5.4% | -11.2% | 4.8% | 5.7% |
  | Same 5 assets, buy-and-hold | 6.0% | -43.5% | 4.4% | 6.8% |
  | 60/40 (Vanguard Balanced Index, VBINX) | 7.7% | -32.6% | 6.3% | 8.5% |
  | S&P 500 (SPY) | 10.8% | -50.8% | 6.1% | 13.4% |

  Source data: [Yahoo Finance chart API, SPY](https://query2.finance.yahoo.com/v8/finance/chart/SPY?period1=1100000000&period2=1794500000&interval=1mo) and the same endpoint for the other tickers.
- **[own computation] Calendar years, GTAA-5 vs 60/40 (VBINX):** 2008 -2.7% vs -22.2%; 2009 14.6 vs 20.1; 2010 3.9 vs 13.1; 2011 -0.1 vs 4.1; 2012 1.7 vs 11.3; 2013 7.8 vs 18.0; 2014 7.5 vs 9.8; 2015 -2.4 vs 0.4; 2016 3.6 vs 8.6; 2017 9.1 vs 13.8; 2018 -1.5 vs -3.0; 2019 8.4 vs 21.7; 2020 3.9 vs 16.3; 2021 22.1 vs 14.1; 2022 -4.9 vs -17.0; 2023 4.4 vs 17.4; 2024 6.4 vs 14.5; 2025 9.1 vs 13.5; 2026 YTD 10.3 vs 6.4. The rule beat 60/40 in 2007, 2008, 2018, 2021 and 2022 only.

**LIVE funds run by Faber / Cambria**
- Cambria Global Tactical ETF (ticker GTAA) launched in 2010 with a 1.41% expense ratio. — [ETF Trends, 2011](https://www.etftrends.com/2011/07/etf-spotlight-cambria-global-tactical-etf-gtaa/2/) (search excerpt)
- In 2011 the ETF lost 7.29% while the five-fund GTAA model returned +2.49%. The live fund diverged from the paper model in its first full year. — [Mutual Fund Observer, 2013](https://www.mutualfundobserver.com/?p=4056) (search excerpt)
- Since inception to October 2011 the ETF was down 4.87%. — [ETF Trends, Oct 2011](https://www.etftrends.com/2011/10/etf-chart-of-the-day-absolute-returns/) (search excerpt)
- Cambria Global Momentum ETF (GMOM, trend plus momentum, inception 4 Nov 2014): annualised since inception 5.69% and cumulative 88.05% to 31 Mar 2026; 10-year 7.16%, 5-year 7.75%. The search tool flagged that it read the column order from the table layout. — [Cambria GMOM fact sheet](https://www.cambriafunds.com/assets/docs/GMOM-FactSheet.pdf) (search excerpt)
- **[own computation] GMOM, Dec 2018 - Nov 2026 (Yahoo adjusted prices; Yahoo history starts Dec 2018):** CAGR 7.9%, max drawdown -15.6%, vs SPY 16.8% / -23.9% and VBINX 10.3% / -20.8%. Calendar years: 2019 8.2%, 2020 2.4%, 2021 19.1%, 2022 -2.8%, 2023 0.7%, 2024 6.7%, 2025 20.6%, 2026 YTD 9.6%. — [Yahoo Finance, GMOM](https://query2.finance.yahoo.com/v8/finance/chart/GMOM?period1=1100000000&period2=1794500000&interval=1mo)

### Inferences
- The out-of-sample result is roughly "half the return of equities with a fifth of the drawdown". The in-sample claim of equity-like returns did not survive.
- Most of the shortfall versus 60/40 came from a US-equity-led bull market with V-shaped recoveries (2009, 2019, 2020, 2023), where a slow filter re-enters late. That pattern is also the Indian experience in 2009 and 2020.
- A live fund with real costs and discretion did worse than the paper model from year one. Expect a personal bot to sit below its own backtest too.

### Gaps
- Could not open Faber's paper or Cambria's site, so the 1973-2012 table and what happened to the GTAA ticker after 2014 are unverified. (My recollection is that Cambria stopped sub-advising it in 2014 and the fund was later closed; not sourced.)
- No Allocate Smartly tracker figures were retrieved; searches returned none and the budget ran out.
- The own replication ignores trading costs and uses ETFs rather than the indices in the paper.

---

## Q2. Antonacci's dual momentum (GEM): rule, backtest, live record 2014-2026, fragility

### Takeaway
GEM's backtest (about 17% a year, 1974-2013) has not repeated. Three independent post-publication checks and my own replication agree it has trailed the S&P 500 by about 5 points a year since 2014, with no meaningful drawdown advantage in that period. The result is also highly sensitive to the lookback month.

### Cited Findings
**The rule**
- Each month-end: if the S&P 500's 12-month return beats T-bills, hold whichever of the S&P 500 or ACWI ex-US has the higher 12-month return; otherwise hold aggregate bonds. One holding at a time. — [Antonacci, SSRN 2042750](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2042750) (recalled, not re-verified); rule consistent with [Newfound](https://blog.thinknewfound.com/tag/gem/) (search excerpt)

**BACKTEST**
- 1974-2013: GEM 17.43% a year, volatility 12.64%, Sharpe 0.87, worst drawdown -22.72%, vs ACWI 8.85% and -60.21%. — [Optimal Momentum, GEM performance](https://www.optimalmomentum.com/gem-performance/) (recalled, not re-verified; host blocked)
- Antonacci's extended backtest reports GEM up 20% across 1973-74 while the S&P 500 fell over 40%, and attributes the cost of absolute momentum to "occasional whipsaws and lags". — [Antonacci, Oct 2018](https://www.optimalmomentum.com/extended-backtest-of-global-equities-momentum/) (search excerpt)
- ReSolve's replication (1950-2018, hypothetical): GEM looked attractive in and out of sample, but the original specification's out-of-sample performance "regressed to the median" of 1,225 alternative parameter choices, and they could not reject that all variants share the same expected return and Sharpe. — [ReSolve / Advisor Perspectives, 2019](https://files.advisorperspectives.com/articles/2019/05/06/global-equity-momentum-a-craftsmans-perspective) (search excerpt)

**OUT OF SAMPLE (post-publication, all hypothetical trackers, not audited accounts)**
- 1997-2013 GEM beat the S&P 500 by 5.1 points a year; 2014-2026 it trailed by 5.4 points a year. Full 1997-2026: GEM 10.25% vs S&P 500 9.85%. GEM's worst year was -17.3% (2022). — [AlgoStrategyLab, GitHub](https://github.com/AlgoStrategyLab/dual-momentum) (search excerpt)
- Since the book, GEM "lagged even a plain SPY by five points a year while giving up its drawdown edge". — [Quant for Free](https://quant4free.com/analysis/dual-momentum/) (search excerpt)
- A 2026 replication paper (1971-2026): GEM has underperformed a passive index by 4.8 points a year since 2010, and its deepest drawdown in 55 years came in 2021-2023 "while it was holding its defensive asset" (bonds). — [Petit, SSRN 7427878](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7427878) (search excerpt)
- Another summary: 2014-2022 GEM underperformed buy-and-hold S&P 500, and it offers "no protection in fast crashes (2020, 2025)". — [reblnc](https://reblnc.com/insights/dual-momentum); [dualmomentumsystems](https://dualmomentumsystems.com/strategies/global-equities-momentum) (search excerpts)
- **[own computation] Replication, Dec 2006 - Nov 2026** (SPY; ex-US = VEU, EFA before Mar 2007; bonds AGG; T-bills BIL/SHY; Yahoo adjusted monthly closes; no costs):

  | | CAGR 2007-Nov 2026 | Max DD | CAGR 2007-2013 | CAGR 2014-Nov 2026 | Max DD 2014-2026 |
  |---|---|---|---|---|---|
  | GEM, 12-month lookback | 8.7% | -19.5% | 9.4% | 8.2% | -19.5% |
  | GEM, 10-month | 8.5% | -19.4% | 8.5% | 8.5% | -19.4% |
  | GEM, 9-month | 6.8% | -20.1% | 4.2% | 8.2% | -20.1% |
  | GEM, 6-month | 7.6% | -24.9% | 10.5% | 6.0% | -24.9% |
  | SPY | 10.8% | -50.8% | 6.1% | 13.4% | -23.9% |
  | 60/40 (VBINX) | 7.7% | -32.6% | 6.3% | 8.5% | -20.8% |

- **[own computation] Whipsaw years, GEM 12-month vs SPY:** 2015 -6.6% vs +1.2%; 2016 6.9 vs 12.0; 2018 -8.0 vs -4.6; 2019 18.6 vs 31.2; 2020 2.6 vs 18.3; 2022 -16.9 vs -18.2; 2023 9.6 vs 26.2; 2025 13.6 vs 17.7. Within 2014-2026 it kept pace with SPY only in 2014, 2017, 2022, 2024 and 2026 YTD.

**Fragility (Newfound)**
- Newfound built GEM variants with 6- to 12-month lookbacks: "the yearly spread between these strategies can be hundreds-to-thousands of basis points", citing 2010 for a 10-month versus 9-month lookback. Their line: "the simplicity of GEM belies its inherent fragility". A 2019 follow-up says the 10-month version whipsawed in 2011 when few others did: "more specification whipsaw than style whipsaw". — [Newfound Research, GEM tag](https://blog.thinknewfound.com/tag/gem/) (search excerpt)
- **[own computation] confirms the size:** in 2010 the 10-month variant made +11.2% and the 9-month variant -8.3% (a 19.5-point gap from a one-month change). In 2018: 10-month +0.5%, 12-month -8.0%.
- Alpha Architect's 2015 comparison found a simpler "robust asset allocation" approach matched or arguably beat dual momentum with stronger drawdown protection. — [Alpha Architect, 2015](https://alphaarchitect.com/2015/02/asset-allocation-horserace-robust-asset-allocation-raa-vs-dual-momentum/) (search excerpt)

### Inferences
- A single-holding, single-lookback rule is a concentrated bet on one parameter. The spread between adjacent lookbacks in a single year is larger than the long-run edge being sought.
- Since 2014 GEM delivered roughly 60/40's return with roughly 60/40's drawdown. That is the honest prior for a top-1 rotation rule after publication.
- The 2022 failure matters for India: the "safe" asset (bonds) fell with equities. A rotation whose defensive leg is a liquid ETF avoids that specific failure, but earns only overnight rates.

### Gaps
- No audited live account or fund tracking GEM was found. All post-2014 numbers are trackers or replications.
- Could not open optimalmomentum.com, Newfound's article, quant4free or the SSRN paper to read full tables.

---

## Q3. AQR / managed-futures trend following: long-run evidence, the 2010s drought, 2022 and after

### Takeaway
Century-long simulations show trend following positive in every decade, but the live record since 2010 is a decade of roughly nothing, one spectacular year (2022), and then the index's second-worst drawdown (2024-25). AQR's own managed-futures fund compounded at about 4.3% a year from 2010 to Nov 2026.

### Cited Findings
**Long-run BACKTESTS**
- AQR "A Century of Evidence on Trend-Following Investing" (Hurst, Ooi, Pedersen): 1903 to mid-2012, positive net returns in every decade, full-sample annualised return 14.3% after simulated fees. Examples from the decade table: 13.4% net and Sharpe 0.84 in 1903-1912; 30.3% net and Sharpe 1.89 in 1973-1982 (column alignment in the extracted copy was garbled). The 2017 JPM version extends to 2016. — [eCapital copy of the AQR paper](http://www.ecapital.ch/downloads/AQR_A%20Century_of_Evidence_on_Trend-Following.pdf); [AQR JPM 2017 version](https://www.aqr.com/-/media/AQR/Documents/Insights/Journal-Article/AQR-JPM-Fall-2017.pdf) (search excerpts)
- Moskowitz, Ooi and Pedersen (2012), "Time Series Momentum": a 12-month own-return signal across 58 liquid futures and forwards, 1985-2009, with significant returns that were strongest in extreme markets. — [SSRN 2089463](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2089463) (recalled, not re-verified)
- "Trend Following: Equity and Bond Crisis Alpha" is a Man AHL paper (Hamill, Rattray, Van Hemert, 2016), not AQR. It reports trend following did well in the worst equity and bond environments back to 1960. — [SSRN 2831926](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2831926) (recalled, not re-verified)
- AQR's "You Can't Always Trend When You Want" (2020) attributes the weak 2010s to smaller market moves rather than crowding or a broken signal. — [AQR](https://www.aqr.com/Insights/Research/Journal-Article/You-Cant-Always-Trend-When-You-Want) (recalled, not re-verified)

**LIVE results**
- **[own computation] AQR Managed Futures Strategy Fund (AQMIX), Jan 2010 - Nov 2026:** CAGR 4.3%, max drawdown -24.4% (monthly). Over the same span SPY made 14.3% and VBINX 9.4%. — [Yahoo Finance, AQMIX](https://query2.finance.yahoo.com/v8/finance/chart/AQMIX?period1=1100000000&period2=1794500000&interval=1mo)
- AQMIX calendar years: 2011 -6.4%, 2012 +3.0, 2013 +9.4, 2014 +9.7, 2015 +2.0, 2016 -8.4, 2017 -1.0, 2018 -8.9, 2019 +1.9, 2020 -0.4, 2021 -1.0, 2022 +35.5, 2023 +2.1, 2024 +8.1, 2025 +14.6, 2026 YTD +11.0. Own computation; the 2011-2024 values match [Yahoo Finance performance page](https://finance.yahoo.com/quote/AQMIX/performance/) and [AAII](https://www.aaii.com/fund/ticker/AQMIX) (search excerpts).
- [own computation] Six calendar years 2016-2021 compounded to about -17% for AQMIX, before the +35.5% of 2022.
- [own computation] iMGP DBi Managed Futures ETF (DBMF), May 2019 - Nov 2026: CAGR 9.2%, max drawdown -17.3%; 2022 +21.6%, 2023 -8.9%. — [Yahoo Finance, DBMF](https://query2.finance.yahoo.com/v8/finance/chart/DBMF?period1=1100000000&period2=1794500000&interval=1mo)
- SG CTA Index posted a record +20.13% in 2022; the trend index returned above 20%. — [The Full FX](https://thefullfx.com/?p=3378) (search excerpt)
- SG Trend Index fell 20.4% from May 2024 through May 2025, its second-largest drawdown since inception in 2000. — [Cambridge Associates](https://publishedresearch.cambridgeassociates.com/?p=19140) (search excerpt)
- Trend-following hedge funds were down double digits in the first half of 2025. — [Alternatives Watch, Jul 2025](https://www.alternativeswatch.com/2025/07/01/trend-following-hedge-funds-loss-h1-societe-generale-index/) (search excerpt)
- SG Trend Index: equal-weighted, ten programs, starts 1 Jan 2000, rebalanced each January. — [BarclayHedge](https://www.barclayhedge.com/sg-prime-services-indices/sg-trend-index/) (search excerpt)

### Inferences
- This evidence is about diversified long/short futures across 50-plus markets. A long-only rotation among three Indian equity indices, gold and cash has far fewer independent bets and cannot short. The century-long Sharpe ratios do not transfer.
- The live lesson that does transfer: trend strategies can go 6-10 years with nothing to show and then pay in one year. A retail investor judging a bot on 2-3 years of results will almost certainly quit or over-trust at the wrong time.

### Gaps
- Year-by-year SG Trend Index returns were not retrieved. My unverified recollection is roughly +20% in 2014, about +27% in 2022, and a flat-to-negative 2011-2013 and 2015-2018; check against SG Prime Services before quoting.
- Could not open AQR's site to confirm decade tables or the drought paper's numbers.

---

## Q4. Indian evidence: published and practitioner backtests of rotation, dual momentum and moving-average timing

### Takeaway
Indian published evidence is thin, blog-level and mostly ignores costs and tax. The consistent finding is that moving-average timing lowers drawdown and does not reliably raise return. My own NAV-based test of the exact five-asset universe says the same, and adds that a plain static mix rebalanced once a year beat both the Faber rule and 12-month dual momentum in both samples. Shorter lookbacks did better, which is itself a warning about parameter luck.

### Cited Findings
**Freefincal (M. Pattabiraman) - BACKTESTS, sceptical**
- 10-month moving average on Sensex vs a 50/50 equity/fixed-income portfolio rebalanced yearly, 338 rolling ten-year windows. Rule: above the 10-month average, all in equity; below, all in fixed income (assumed 6% post-tax). Tax and exit load approximated by cutting the tactical final value by 20% and the systematic by 4%. Findings in text: both timing models beat systematic in some periods; the systematic portfolio was "typically better" than the 10-month rule on months underwater; timing had steeper falls than the 50/50 portfolio; no-equity stretches lasted about 10-20 months. Conclusion: "The backtest says yes but keep in mind the assumptions made, real-life limitations, the fact that in the recent past results are not that good and that it is only a back-test." Numeric returns are only in charts. — [Freefincal, Part 2](https://freefincal.com/market-timing-with-ten-month-moving-average-tactical-asset-allocation-backtest-part-2/) (fetched)
- Part 3 (196 five-year and 136 ten-year windows): "The 10MMA model appears to be riskier than the PE-model"; "if you simply held lower (30%) equity, you could have got the job done instead of timing!"; "Time the market because you desire lower risk and not because you desire a higher return." — [Freefincal, Part 3](https://freefincal.com/tactical-asset-allocation-backtest-part-3-short-term-vs-long-term/) (fetched)
- Double moving average (6-month vs 12-month) on Sensex from 1979, Nifty Next 50 TRI, Nifty Midcap 150 TRI, Smallcap 250 TRI (27 May 2022). On Sensex over 15 years with 50% equity the tactical strategy "fails badly", with sharp underperformance after March 2020: the crash was too short for the averages to cross back in time, so the tactical investor missed much of the recovery. Next 50 and Midcap 150 showed similar patterns. Taxes and exit loads not included. Conclusion: "just another method sometimes superior to other methods and sometimes inferior"; "nothing works all the time in all markets." — [Freefincal, May 2022](https://freefincal.com/a-risk-in-market-timing-that-122-years-of-backtesting-failed-to-reveal/) (fetched)
- Gold 6-month vs 12-month moving-average timing, 1979/1997 to May 2020, 155-367 ten-year windows, taxes excluded: reduces risk "pretty much every time" but higher returns need "a clear trend"; "Returns might be a nice perk if lucky." — [Freefincal, May 2020](https://freefincal.com/is-this-a-good-time-to-buy-gold/) (fetched)
- Freefincal also has posts on timing the Nifty Midcap150 Momentum 50 fund and gilt funds with the same method. — [Freefincal tactical category](https://freefincal.com/category/tactical-asset-allocation) (fetched; titles only)

**Capitalmind - BACKTEST**
- Nifty-vs-Gold dual momentum (16 Jun 2022): hold whichever of Nifty or Gold BeES had the higher trailing one-year return, reviewed monthly, 23 trades in about 17 years from 2005. Rs 1 lakh grew to Rs 8.4 lakh vs Rs 7.7 lakh for buy-and-hold Nifty: "comparable returns to the Nifty with lower volatility". Costs and taxes not mentioned. — [Capitalmind, Jun 2022](https://www.capitalmind.in/insights/should-gold-be-in-your-long-term-portfolio) (fetched)
- Same article: gold trailed the Nifty by about 2.1% a year over 1999-2022; gold beat the Nifty in about 34% of 5-year and 39% of 10-year rolling windows; gold declined for seven years after 2012 and only regained its 2012 price in the pandemic. — [Capitalmind, Jun 2022](https://www.capitalmind.in/insights/should-gold-be-in-your-long-term-portfolio) (fetched)
- Static mix study (25 Oct 2024, data 2000 - Oct 2024): the best return-for-volatility mix was 32% gold / 68% Nifty; starting in 2010 instead shifts the answer toward more Nifty; the "optimal" portfolios trail the Nifty on 3- and 5-year rolling returns nearly 60% of the time; Nifty led 56% of rolling 3-year windows, gold 21%. The article supports a strategic allocation and does not test timing. — [Capitalmind, Oct 2024](https://www.capitalmind.in/insights/gold-silver-portfolio-allocation-analysis-2024) (fetched)
- Capitalmind's trend overlay ("Chase") is discussed without public numbers. — [earlier note, Q3](https://premium.capitalmind.in/2020/08/podcast-31-how-trend-following-can-make-buy-and-hold-better/)

**Other practitioner BACKTESTS**
- Momentum Lab, Nifty/gold/FD dual momentum on 200-day returns, 2014-2024: CAGR 18.79% vs Nifty 12.13%, max drawdown -11.42% vs -34.00%. No costs, taxes or switch counts. — [Momentum Lab](https://momentumlab.substack.com/p/backtesting-dual-momentum-strategy) (search excerpt; also in the earlier note)
- Weekend Investing "Mi EverGreen": 20 momentum stocks from the CNX 200 plus a gold ETF at 75/25, rebalanced monthly; the manager's blog claims 21.1% CAGR with 18.6% max drawdown over 6.75 years vs 14.3% and 38.2% for the CNX 200. That period is mostly pre-launch (launch 26 Dec 2021), promotional, and it is stock rotation with a gold sleeve, not ETF rotation. — [smallcase blog](https://www.smallcase.com/blog/mi-evergreen-your-affordable-companion-for-financial-independence/); [Tickertape listing](https://tickertape.in/smallcase/mi-evergreen-WKIMO_0019) (search excerpts)
- Earlier note's own test on Nifty 50 (Jul 2008 - Oct 2026, price index, 6.5% cash, 0.10% per switch, no tax): month-end 200-DMA rule 10.1% CAGR / -24.2% max drawdown vs buy-and-hold 10.0% / -45.4%; daily-checked version 7.8%; 12-month absolute momentum 4.4%. — [momentum_factor_evidence.md, Q3](https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI?period1=0&period2=1792000000&interval=1d)

**[own computation] BACKTEST of the reader's exact universe, month-end signals, NAV data**

Method and limits:
- Monthly: signal from month-end NAVs, traded at that month-end, held one month. Cost 0.2% of traded value on each leg. No tax in the first tables.
- Nifty 50 = UTI Nifty 50 Index Fund (regular, growth). Next 50 = Junior BeES NAV. Gold = Gold BeES NAV (split-adjusted). Liquid = HDFC Liquid Fund (regular, growth), which yields more than a liquid ETF. Midcap = Motilal Oswal Nifty Midcap 100 ETF NAV from Feb 2011, spliced to the Nifty Midcap 50 price index before that; it is a proxy, not Midcap 150.
- Data: [mfapi.in / AMFI NAVs, e.g. scheme 100822](https://api.mfapi.in/mf/100822), 101621 / 115729 / 140085 (Junior BeES), 105085 / 115744 / 140088 (Gold BeES), 114456, 100868; [Yahoo Finance ^NSEMDCP50](https://query2.finance.yahoo.com/v8/finance/chart/%5ENSEMDCP50?period1=1100000000&period2=1794500000&interval=1mo).
- NAVs are not traded prices. Premiums, discounts and thin liquidity in midcap ETFs are not modelled.
- Rules were chosen before looking at results, but this is one path of history and 19 years is about three market cycles.

Sample A - Nifty 50, Next 50, Gold, Liquid (no midcap), Dec 2007 - Nov 2026, includes all of 2008:

| Strategy | CAGR | Vol | Max DD (monthly) | CAGR Dec 2007 - Dec 2018 | CAGR Dec 2018 - Nov 2026 | One-way turnover / yr |
|---|---|---|---|---|---|---|
| Buy-and-hold Nifty 50 | 8.2% | 20.1% | -55.3% | 5.5% | 12.1% | 0 |
| Buy-and-hold Next 50 | 10.1% | 25.0% | -68.9% | 7.8% | 13.5% | 0 |
| Buy-and-hold Gold BeES | 13.4% | 17.2% | -26.6% | 9.2% | 19.6% | 0 |
| Liquid fund | 6.9% | 0.5% | 0% | 7.8% | 5.7% | 0 |
| Static 1/3 each Nifty / Next 50 / Gold, annual rebalance | 12.3% | 14.4% | -37.0% | 10.0% | 15.6% | 0.1x |
| Static 25% each incl. liquid, annual rebalance | 11.3% | 10.7% | -25.9% | 10.0% | 13.2% | 0.1x |
| Static 75 Nifty / 25 Gold, annual rebalance | 10.6% | 14.7% | -38.0% | 8.0% | 14.3% | 0.1x |
| Faber 10-month SMA, 3 assets incl. gold | 10.5% | 10.6% | -13.7% | 9.3% | 12.2% | 1.9x |
| Faber 10-month SMA, equity only (Nifty + Next 50) | 9.9% | 14.7% | -22.9% | 10.2% | 9.4% | 1.9x |
| Faber 10-month SMA, Nifty 50 only | 8.2% | 13.7% | -23.3% | 6.8% | 10.2% | 1.9x |
| Dual momentum top-1, 12-month, incl. gold | 8.1% | 17.2% | -46.9% | 5.0% | 12.5% | 2.6x |
| Dual momentum top-1, 12-month, no gold | 2.1% | 14.4% | -45.9% | 2.6% | 1.3% | 2.9x |
| Dual momentum top-1, 9-month, incl. gold | 14.8% | 17.3% | -30.5% | 11.9% | 18.9% | 2.0x |
| Dual momentum top-1, 6-month, incl. gold | 14.7% | 17.4% | -31.2% | 10.8% | 20.4% | 2.9x |
| Dual momentum top-1, 3-month, incl. gold | 11.1% | 19.2% | -39.2% | 5.3% | 19.7% | 5.0x |
| Top-2 by blended 3/6/12-month momentum, incl. gold | 9.2% | 12.5% | -25.3% | 7.1% | 12.2% | 2.3x |
| Top-2 blended, no gold | 6.5% | 12.3% | -30.0% | 6.1% | 7.1% | 2.1x |

Sample B - adds the midcap proxy, Sep 2008 - Nov 2026. It starts after most of the 2008 fall, which flatters every buy-and-hold row:

| Strategy | CAGR | Max DD (monthly) | CAGR Sep 2008 - Dec 2018 | CAGR Dec 2018 - Nov 2026 |
|---|---|---|---|---|
| Buy-and-hold Nifty 50 | 11.3% | -29.9% | 10.7% | 12.1% |
| Buy-and-hold Next 50 | 15.0% | -36.2% | 16.3% | 13.5% |
| Buy-and-hold midcap proxy | 14.4% | -43.6% | 12.1% | 17.4% |
| Buy-and-hold Gold BeES | 12.5% | -26.6% | 7.4% | 19.6% |
| Static 25% each of 4 risky assets, annual rebalance | 14.3% | -26.3% | 12.8% | 16.3% |
| Static 20% each of 5 incl. liquid, annual rebalance | 13.1% | -20.8% | 12.2% | 14.2% |
| Faber 10-month SMA, 4 assets incl. gold | 11.3% | -16.3% | 10.7% | 12.2% |
| Faber 10-month SMA, 3 equity indices, no gold | 11.3% | -24.5% | 12.0% | 10.3% |
| Dual momentum top-1, 12-month, incl. gold | 13.6% | -23.3% | 10.1% | 18.3% |
| Dual momentum top-1, 12-month, no gold | 7.4% | -33.5% | 8.8% | 5.6% |
| Dual momentum top-1, 9-month / 6-month / 3-month, incl. gold | 17.1% / 15.8% / 14.3% | -15.4% / -33.8% / -25.5% | 14.5% / 13.4% / 8.4% | 20.5% / 18.9% / 22.4% |
| Top-2 blended 3/6/12, incl. gold | 12.3% | -21.8% | 10.4% | 14.8% |
| Top-2 blended, no gold | 10.1% | -23.6% | 11.3% | 8.6% |

### Inferences
- **The robust effect is drawdown, not return.** The Faber-style rule with gold cut the worst drawdown to about -14% to -16% in both samples, at a return between buy-and-hold Nifty and the static mix.
- **A static mix is the benchmark to beat, and mostly it was not beaten.** One-third each of Nifty, Next 50 and gold, rebalanced once a year, made 12.3% in Sample A against 10.5% for the Faber rule and 8.1% for 12-month dual momentum, with one trade a year.
- **Top-1 rotation is fragile in India too.** Changing only the lookback from 12 to 9 months moved Sample A's CAGR from 8.1% to 14.8% and the worst drawdown from -47% to -31%. Any single choice here is curve-fitting risk.
- **The 12-month rule failed in 2008 in this universe.** It entered 2008 holding Next 50 (highest trailing return) and lost 38% that year. Slow absolute momentum does not guarantee crash protection.
- Published Indian backtests (Capitalmind, Freefincal) are consistent with these numbers: comparable return, lower volatility, no free lunch.

### Gaps
- No peer-reviewed study of time-series momentum or asset-class rotation across Indian equity indices, gold and debt was found (also a gap in the earlier note). The search budget ended before a dedicated academic search could be run.
- PrimeInvestor, Weekend Investing ETF-only smallcases ("Mi AllCap GOLD", "Mi ST ATH" and similar) and "Capitalmind Adaptive Momentum": no usable figures retrieved. Their sites were blocked or gated.
- Freefincal's numeric results sit in chart images and could not be extracted.
- Own backtest: proxy midcap series, regular-plan index fund for Nifty, liquid fund rather than liquid ETF, NAV rather than traded price, month-end same-day execution.

---

## Q5. LIVE Indian track records: funds and smallcases running equity / gold / debt dynamic allocation

### Takeaway
No live, rule-based Indian ETF-rotation product with a verifiable public record was found. The nearest live evidence is multi-asset and dynamic-allocation mutual funds: the two best beat a Nifty 50 index fund by about 4 points a year since 2013, the median roughly matched it with smaller drawdowns, and results are far better after 2019 than before.

### Cited Findings
- **[own computation] LIVE fund NAVs, direct plans, to 9 Nov 2026**, compared with UTI Nifty 50 Index Fund (direct) over the identical window. NAV returns are after fund costs and before the investor's exit tax. Max drawdown is from daily NAVs. Source: [mfapi.in / AMFI NAV history, e.g. scheme 120334](https://api.mfapi.in/mf/120334); codes 120821, 119843, 120760, 148053, 148454, 148457, 149441, 151745, 152056, 152064, 118615, 118968, 120377, 126393, 120716.

  | Fund | Window start | CAGR | Max DD | Nifty 50 index fund, same window: CAGR / Max DD |
  |---|---|---|---|---|
  | ICICI Prudential Multi Asset Allocation | 2 Jan 2013 | 15.9% | -30.6% | 11.9% / -38.4% |
  | Quant Multi Asset Allocation | 7 Jan 2013 | 15.6% | -44.8% | 11.9% / -38.4% |
  | SBI Multi Asset Allocation | 19 Mar 2013 | 12.1% | -17.6% | 12.4% / -38.4% |
  | UTI Multi Asset Allocation | 2 Jan 2013 | 10.0% | -25.0% | 11.9% / -38.4% |
  | Edelweiss Balanced Advantage | 22 Jan 2013 | 12.3% | -16.2% | 11.8% / -38.4% |
  | HDFC Balanced Advantage | 2 Jan 2013 | 13.9% | -34.2% | 11.9% / -38.4% |
  | ICICI Prudential Balanced Advantage | 2 Jan 2013 | 12.6% | -27.0% | 11.9% / -38.4% |
  | DSP Dynamic Asset Allocation | 7 Feb 2014 | 10.2% | -19.3% | 12.8% / -38.4% |
  | Tata Multi Asset Allocation | 12 Mar 2020 | 17.5% | -13.5% | 16.6% / -23.6% |
  | Nippon India Multi Asset Allocation | 31 Aug 2020 | 17.5% | -10.8% | 14.7% / -16.6% |
  | Motilal Oswal Multi Asset | 10 Aug 2020 | 5.5% | -22.3% | 14.7% / -16.6% |
  | ICICI Prudential Passive Multi-Asset FoF | 17 Jan 2022 | 11.9% | -7.4% | 7.8% / -15.9% |
  | WhiteOak Capital Multi Asset Allocation | 22 May 2023 | 16.0% | -6.1% | 10.5% / -15.5% |
  | DSP Multi Asset Allocation | 29 Sep 2023 | 18.1% | -9.7% | 9.1% / -15.5% |
  | Kotak Multi Asset Allocation | 3 Oct 2023 | 17.0% | -13.8% | 9.4% / -15.5% |

- **[own computation] The same long-running funds split by period (CAGR):**

  | Fund | 2 Jan 2013 - 31 Dec 2018 | 1 Jan 2019 - 9 Nov 2026 |
  |---|---|---|
  | ICICI Pru Multi Asset | 14.9% | 16.5% |
  | Quant Multi Asset | 6.7% | 22.9% |
  | SBI Multi Asset | 10.3% | 13.5% |
  | UTI Multi Asset | 6.7% | 12.5% |
  | Edelweiss Balanced Advantage | 11.2% | 13.2% |
  | HDFC Balanced Advantage | 12.7% | 14.8% |
  | ICICI Pru Balanced Advantage | 13.3% | 12.1% |
  | UTI Nifty 50 Index Fund | 11.3% | 12.2% |

- [own computation] Calendar 2025: the multi-asset funds with gold made 17-25% (ICICI 19, Quant 18, SBI 20, Tata 17, Nippon 21, DSP 25, Kotak 24) against 12% for the Nifty 50 index fund, a year in which Gold BeES NAV rose 72%.
- Weekend Investing Mi EverGreen went live on 26 Dec 2021; an Aug 2024 weekly review reported +8.7% for FY25 to date. Current since-launch returns sit behind a login. — [Tickertape / smallcase listing](https://tickertape.in/smallcase/mi-evergreen-WKIMO_0019); [Weekend Investing weekly review, 30 Aug 2024](https://weekendinvesting.beehiiv.com/p/good-bad-ugly-weekly-review-30-aug-2024) (search excerpts)

### Inferences
- These funds are discretionary or valuation-driven, not mechanical trend rules, so they are indirect evidence only. They show what professionally run equity/gold/debt switching delivered after costs.
- The table has survivorship bias: it lists funds that exist today, and several were recategorised in 2018 (their pre-2018 mandates differed).
- Funds switch internally without triggering the investor's capital-gains tax. A DIY bot pays tax on every switch, so matching a fund's pre-tax NAV return with the same skill leaves the DIY investor behind.
- Dispersion is wide: Motilal Oswal Multi Asset made 5.5% a year against 14.7% for the index over the same window. "Dynamic allocation" is not a reliable source of excess return.
- Windows that start in 2020-2023 look strong mainly because they sit inside gold's run and avoid any long gold bear market.

### Gaps
- No verified since-launch numbers for Weekend Investing ETF smallcases, "Windmill" / "All Weather" smallcases, or Capitalmind PMS strategies. smallcase and Weekend Investing pages were blocked or gated. This is the largest unanswered item.
- Fund mandates (which ones are trend-based, such as Edelweiss Balanced Advantage's pro-cyclical model, versus valuation-based) were not re-sourced this session.
- Comparison is against a Nifty 50 index fund, not each scheme's own blended benchmark.

---

## Q6. How much of any Indian rotation result is simply gold's 2019-2026 run?

### Takeaway
Most of it. In my backtest the 12-month top-1 rotation made 18.3% a year in 2019-2026 with gold in the universe and 5.6% without it. Gold supplied roughly half to three-quarters of the rule's total log growth, and backtests that end before 2023 show rotation merely matching the Nifty.

### Cited Findings
- **[own computation] Gold itself:** Gold BeES NAV compounded at 19.6% a year from Dec 2018 to Nov 2026, against 9.2% from Dec 2007 to Dec 2018. Calendar 2025 alone was +72.0% (NAV) / +71.8% (market price). Over the seven calendar years 2019-2025 gold multiplied about 3.9x; the Nifty 50 index fund about 2.5x. — [AMFI NAV via mfapi, scheme 140088](https://api.mfapi.in/mf/140088); [Yahoo Finance GOLDBEES.NS](https://query1.finance.yahoo.com/v8/finance/chart/GOLDBEES.NS?period1=1167600000&period2=1794000000&interval=1mo)
- **[own computation] Gold's flat stretch:** over the six calendar years 2013-2018 Gold BeES returned about -3% in total (NAV basis; about -3.5% on market price).
- **[own computation] Same rules with and without gold in the universe (Sample B, with midcap proxy):**

  | Rule | Full period CAGR | Sep 2008 - Dec 2018 | Dec 2018 - Nov 2026 |
  |---|---|---|---|
  | Dual momentum top-1, 12-month: with gold | 13.6% | 10.1% | 18.3% |
  | Dual momentum top-1, 12-month: no gold | 7.4% | 8.8% | 5.6% |
  | Top-2 blended: with gold | 12.3% | 10.4% | 14.8% |
  | Top-2 blended: no gold | 10.1% | 11.3% | 8.6% |
  | Faber 10-month SMA: with gold | 11.3% | 10.7% | 12.2% |
  | Faber 10-month SMA: no gold | 11.3% | 12.0% | 10.3% |
  | Buy-and-hold Nifty 50 | 11.3% | 10.7% | 12.1% |

- **[own computation] Attribution for the 12-month top-1 rule:** in Sample B it held gold in 42 of 123 months to Dec 2018 and in 51 of 95 months after. Gross growth while holding gold was 3.29x out of a total 12.2x, about 48% of log growth. In Sample A (no midcap) gold was 3.26x of 5.3x, about 71% of log growth, and the rule held gold in 56 of 95 months after 2018.
- **[own computation] Calendar 2025 and 2026 YTD for the 12-month top-1 rule:** +47.9% and +6.1% with gold; -9.0% and -17.0% without gold (Sample B). The Nifty 50 index fund made +11.6% and -3.4%.
- Capitalmind's Nifty-gold dual momentum, ending mid-2022 before the largest part of gold's run, beat buy-and-hold Nifty only marginally (Rs 8.4 lakh vs Rs 7.7 lakh from Rs 1 lakh over about 17 years). — [Capitalmind, Jun 2022](https://www.capitalmind.in/insights/should-gold-be-in-your-long-term-portfolio) (fetched)
- Momentum Lab's 18.79% CAGR for Nifty/gold dual momentum uses a 2014-2024 window, which starts near gold's 2013-2015 low. — [Momentum Lab](https://momentumlab.substack.com/p/backtesting-dual-momentum-strategy) (search excerpt)
- Capitalmind's static optimisation is window-dependent in the same way: 32% gold is "optimal" from 2000, but starting in 2010 the optimum holds more Nifty and less gold. — [Capitalmind, Oct 2024](https://www.capitalmind.in/insights/gold-silver-portfolio-allocation-analysis-2024) (fetched)

### Inferences
- An equity-only rotation among Nifty 50, Next 50 and midcap added nothing over buy-and-hold in 2019-2026 and lost to it under the top-1 rule. The three equity indices are too correlated for rotation among them to matter; the result is a gold-or-not-gold switch.
- The rotation rule did not "find" gold by skill. Any rule that owned gold from mid-2019 looks good. A static 25% gold holding captured much of the same benefit with one trade a year.
- The sceptical forward view: after a 3.9x move in seven years, a momentum rule will be holding gold at whatever point the trend ends. Gold's last comparable peak (2012) was followed by six flat years. A backtest ending Nov 2026 contains the run and none of the aftermath.

### Gaps
- No published Indian source isolating gold's contribution to a rotation strategy was found; the attribution above is entirely own computation.
- Gold BeES NAV and traded price diverged in 2013-2014 (see Q7), so gold's contribution in those years depends on which series is used.

---

## Q7. Year-by-year calendar returns since 2008: gold in INR, Nifty 50, Nifty Next 50, Midcap

### Takeaway
The table below is built from investable series (fund and ETF NAVs) plus Yahoo price indices, because the official NSE total-return index download failed in this session. Fund-NAV columns are total-return by construction, net of fund costs; the "PR" columns are price return and exclude dividends of roughly 1-1.5% a year.

### Cited Findings
- **[own computation] Calendar-year returns, %.** 2026 YTD is to 9 Nov 2026 for NAV columns and 11 Nov 2026 for Yahoo columns.

  | Year | Gold BeES NAV | Gold BeES market price | Nifty 50 fund NAV (UTI index fund, regular) | Nifty 50 PR | Next 50 ETF NAV (Junior BeES) | Next 50 PR | Midcap 150 TRI (published) / ETF NAV | Liquid fund NAV |
  |---|---|---|---|---|---|---|---|---|
  | 2008 | 25.6 | n/a | -52.0 | -51.8 | -63.3 | -63.5 | -65 | 8.9 |
  | 2009 | 22.7 | n/a | 73.8 | 75.8 | 122.7 | 127.9 | 114 | 5.3 |
  | 2010 | 21.7 | 21.7 | 17.7 | 17.9 | 17.8 | 17.8 | 20 | 5.1 |
  | 2011 | 30.3 | 29.9 | -24.8 | -24.6 | -31.6 | -31.9 | -31 | 8.8 |
  | 2012 | 10.9 | 11.3 | 28.3 | 27.7 | 48.8 | 48.1 | 47 | 9.6 |
  | 2013 | -14.1 | -6.4 | 6.9 | 6.8 | 5.1 | 4.8 | -1 | 9.3 |
  | 2014 | 0.8 | -9.3 | 31.8 | 31.4 | 43.5 | 44.4 | 63 | 9.1 |
  | 2015 | -7.8 | -7.5 | -3.3 | -4.1 | 7.1 | 7.0 | 10 | 8.3 |
  | 2016 | 10.7 | 12.5 | 4.0 | 3.0 | 7.2 | 7.1 | 7 | 7.6 |
  | 2017 | 2.9 | 2.4 | 29.7 | 28.6 | 46.3 | 44.8 | 56 | 6.5 |
  | 2018 | 6.9 | 6.7 | 4.3 | 3.2 | -8.0 | -9.0 | -13 | 7.2 |
  | 2019 | 22.3 | 22.9 | 13.2 | 12.0 | 1.3 | 0.5 | not found (Midcap 100 ETF NAV: -3.5) | 6.5 |
  | 2020 | 26.2 | 27.0 | 15.5 | 14.9 | 15.5 | 14.8 | 25.3 | 4.1 |
  | 2021 | -4.8 | -5.2 | 25.2 | 24.1 | 30.5 | 29.9 | 47.6 | 3.2 |
  | 2022 | 14.0 | 12.8 | 5.3 | 4.3 | 0.7 | -0.1 | 3.6 | 4.8 |
  | 2023 | 12.7 | 14.7 | 20.9 | 20.0 | 27.1 | 26.4 | 44.3 | 7.0 |
  | 2024 | 19.4 | 19.4 | 9.6 | 8.8 | 28.1 | 27.5 | 24.1 | 7.3 |
  | 2025 | 72.0 | 71.8 | 11.6 | 10.5 | 2.8 | 2.0 | 5.8 | 6.5 |
  | 2026 YTD | 6.1 | 4.7 | -3.4 | -3.3 | 5.7 | 5.9 | 1.1 | 5.5 |

- **Column sources and basis:**
  - Gold BeES NAV: AMFI NAV history, split-adjusted for the Dec 2019 1:100 unit split; rupee return of an India-listed gold ETF, includes import duty effects, net of expense ratio. — [mfapi 105085](https://api.mfapi.in/mf/105085), [115744](https://api.mfapi.in/mf/115744), [140088](https://api.mfapi.in/mf/140088)
  - Gold BeES market price: NSE traded close, price return. — [Yahoo Finance GOLDBEES.NS](https://query1.finance.yahoo.com/v8/finance/chart/GOLDBEES.NS?period1=1167600000&period2=1794000000&interval=1mo)
  - Nifty 50 fund NAV: UTI Nifty 50 Index Fund, regular plan, growth option. Dividends reinvested inside the fund, so it is a total-return proxy net of costs. It tracked poorly in 2008-2009 (below even the price index) and from 2015 runs about 1 point above price return. — [mfapi 100822](https://api.mfapi.in/mf/100822)
  - Nifty 50 PR and Next 50 PR: Yahoo `^NSEI` and `^NSMIDCP` month-end closes, price return, no dividends. — [Yahoo ^NSEI](https://query2.finance.yahoo.com/v8/finance/chart/%5ENSEI?period1=1100000000&period2=1794500000&interval=1mo); [Yahoo ^NSMIDCP](https://query2.finance.yahoo.com/v8/finance/chart/%5ENSMIDCP?period1=1100000000&period2=1794500000&interval=1mo)
  - Next 50 ETF NAV: Junior BeES NAV (Benchmark, then Goldman Sachs, then Nippon). The ETF paid occasional dividends in early years that this series does not add back (2009 shows 122.7% against a price index of 127.9%). — [mfapi 101621](https://api.mfapi.in/mf/101621), [115729](https://api.mfapi.in/mf/115729), [140085](https://api.mfapi.in/mf/140085)
  - Midcap 150, 2008-2018: Nifty Midcap 150 TRI calendar-year returns from a DSP fund presentation, rounded to whole numbers. — [DSP Nifty Midcap 150 Quality 50 presentation](https://www.slideshare.net/slideshow/dsp-nifty-midcap-150-quality-50-indexpdf/266596229) (search excerpt). Cross-check from ICRA / Bloomberg data: 2008 -64.6, 2009 112.5, 2010 19.9, 2011 -30.8. — [Cafemutual](https://cafemutual.com/news/industry/35282-how-have-various-market-caps-performed-over-the-last-20-calendar-years) (search excerpt)
  - Midcap 150, 2020 onward: Nippon India ETF Nifty Midcap 150 NAV (launched Feb 2019), total-return proxy net of costs. — [mfapi 146271](https://api.mfapi.in/mf/146271). Yahoo's Nifty Midcap 150 price index gives 24.4, 46.8, 3.0, 43.7, 23.8, 5.4 for 2020-2025 and 1.4 YTD.
  - Liquid fund: HDFC Liquid Fund, regular, growth. — [mfapi 100868](https://api.mfapi.in/mf/100868)
- **Official Nifty 50 TRI where found:** 2008 -51.3%, 2009 +77.6%, 2010 +19.2%, 2011 -23.8%. — [Bajaj AMC](https://www.bajajamc.com/knowledge-centre/nifty-50-historical-returns) (search excerpt)
- **Gold 2008 cross-check:** Rs 100 in gold at end-2007 became Rs 126.94 at end-2008, while Rs 100 in the Nifty 50 became Rs 48.21. — [Angel One](https://angelone.in/news/nifty-50-vs-gold) (search excerpt). International gold in rupees (COMEX futures x USD/INR, own computation) gives +29.6% for 2008.
- A blog compiling NSE index calendar-year returns for 2006-2025 exists and likely has the full TRI table, but could not be opened. — [Rama Krishna Vadlamudi, Jan 2026](https://ramakrishnavadlamudi.blogspot.com/2026/01/nse-indices-calendar-year-returns-2006.html) (search result title only)

### Inferences
- **Gold 2013-2014 depends on the series.** NAV says -14.1% then +0.8%; traded price says -6.4% then -9.3%. Both compound to about the same two-year result (-13% to -15%). The likely cause is ETF units trading at a premium to NAV at end-2013 during import curbs; that explanation is my inference, not sourced. A bot trading on exchange experiences the price series.
- Gold was the best of the four risky assets in 2008, 2010, 2011, 2016, 2018, 2019, 2020, 2022 and 2025, and the worst in 2009, 2012, 2013, 2014, 2015, 2017, 2021 and 2023 (NAV basis). That alternation is why a gold sleeve helps a static mix as much as it helps a rotation.
- Nifty 50, Next 50 and midcap fell together in every bad year (2008, 2011, and the flat-to-down 2018-2019 stretch for the latter two). Rotating among them offers no shelter.
- 2026 so far (to early November) is a mild whipsaw year: Nifty 50 about -3%, Next 50 about +6%, midcap about +1%, gold about +5-6% after its 2025 surge.

### Gaps
- Official NSE TRI series for Nifty 50, Next 50 and Midcap 150 could not be downloaded (niftyindices.com API returned an error; its data host was blocked). Only four Nifty 50 TRI years and the 2008-2018 Midcap 150 TRI years are from published TRI tables.
- Nifty Midcap 150 TRI for 2019 was not found. Nifty Next 50 TRI by year was not found; the ETF NAV and price index bracket it.
- World Gold Council and IBJA / MCX rupee gold series were not retrieved; the gold columns are ETF-based.

---

## Q8. Negative and mixed evidence: long lags, whipsaw years and tax drag

### Takeaway
Trend and rotation rules lag buy-and-hold for long stretches as a matter of course: nine straight years for Faber's rule against 60/40, twelve years and counting for GEM against the S&P 500, six negative-sum years for AQR's fund. In India the whipsaw years were 2013, 2016, 2018-19, 2022 and 2026 YTD, and Indian tax takes roughly 1-2 points a year from a switching strategy, against under 1 point for buy-and-hold.

### Cited Findings
**Long lags (global)**
- [own computation] Faber GTAA-5 trailed a 60/40 fund in every calendar year from 2009 to 2017, and in 14 of the 19 full years 2007-2025. See Q1.
- [own computation] GEM trailed the S&P 500 by 5.2 points a year from 2014 to Nov 2026 (8.2% vs 13.4%), corroborated at 5.4, 5 and 4.8 points by [AlgoStrategyLab](https://github.com/AlgoStrategyLab/dual-momentum), [Quant for Free](https://quant4free.com/analysis/dual-momentum/) and [Petit, SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7427878) (search excerpts).
- [own computation] AQR Managed Futures lost about 17% over 2016-2021. SG Trend fell 20.4% from May 2024 to May 2025. — [Cambridge Associates](https://publishedresearch.cambridgeassociates.com/?p=19140) (search excerpt)

**India: lag after 2015 on Nifty alone**
- Earlier note's own test: from 2015 to Oct 2026 a month-end 200-DMA rule on Nifty made 7.3% a year against 8.8% for buy-and-hold (price index, before tax); a daily-checked version made 5.3% with 8.9 switches a year. — [earlier note, Q3; Yahoo ^NSEI data](https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI?period1=0&period2=1792000000&interval=1d)
- Freefincal: the 6/12-month moving-average rule "fails badly" on Sensex over 15 years because of March 2020, and Next 50 and Midcap 150 behaved similarly. — [Freefincal, May 2022](https://freefincal.com/a-risk-in-market-timing-that-122-years-of-backtesting-failed-to-reveal/) (fetched)
- In Oct 2026 the Nifty had spent a reported 160 days below its 200-DMA with only 20% of constituents above theirs. — [Business Standard, Oct 2026](https://www.business-standard.com/markets/news/nifty-s-200-day-moving-average-sounds-alarm-as-market-breadth-thins-126101401265_1.html); [Whalesbook](https://www.whalesbook.com/news/English/sebiexchange/Nifty-50-Marks-160-Day-Streak-Below-200-DMA-What-It-Means/6adabe3379a16deaeafae99c) (from the earlier note)

**[own computation] India: calendar-year results of the backtested rules (Sample A: Nifty 50, Next 50, Gold, Liquid; before tax, after 0.2% costs)**

| Year | Buy-and-hold Nifty 50 | Static 1/3 each, annual rebalance | Faber 10m SMA, with gold | Faber 10m SMA, equity only | Dual momentum top-1 12m, with gold | Dual momentum top-1 12m, no gold |
|---|---|---|---|---|---|---|
| 2008 | -52.1 | -30.0 | -12.0 | -17.9 | -38.2 | -43.7 |
| 2009 | 73.8 | 72.9 | 55.8 | 72.6 | 30.6 | 34.4 |
| 2010 | 17.7 | 19.0 | 19.7 | 17.9 | 17.8 | 17.8 |
| 2011 | -24.8 | -8.7 | 4.5 | -7.0 | 29.8 | -5.0 |
| 2012 | 28.3 | 29.3 | 9.6 | 8.5 | 19.5 | 10.1 |
| 2013 | 6.9 | -0.7 | -3.8 | 0.4 | -18.1 | -18.1 |
| 2014 | 31.8 | 25.4 | 24.8 | 37.6 | 39.8 | 39.8 |
| 2015 | -3.3 | -1.4 | -2.7 | 0.1 | 5.4 | 5.4 |
| 2016 | 4.0 | 7.3 | 8.1 | 5.2 | -17.1 | -0.7 |
| 2017 | 29.7 | 26.3 | 23.6 | 34.7 | 38.6 | 34.2 |
| 2018 | 4.3 | 1.0 | -9.5 | -12.0 | -16.4 | -11.3 |
| 2019 | 13.2 | 12.3 | 8.6 | 2.0 | 8.2 | 0.1 |
| 2020 | 15.5 | 19.1 | 20.2 | 16.4 | 26.2 | 1.5 |
| 2021 | 25.2 | 17.0 | 14.2 | 27.8 | 8.3 | 21.2 |
| 2022 | 5.3 | 6.6 | 0.9 | -3.0 | -14.2 | -15.2 |
| 2023 | 20.9 | 20.2 | 14.4 | 18.2 | -0.2 | 15.9 |
| 2024 | 9.6 | 19.0 | 19.3 | 18.6 | 27.6 | 28.1 |
| 2025 | 11.6 | 28.8 | 25.5 | 6.8 | 47.9 | -11.6 |
| 2026 YTD | -3.4 | 2.8 | -3.8 | -7.3 | 6.1 | -18.9 |

Reading the whipsaw windows named in the brief:
- **2010-2013:** the Faber rule with gold did fine in total (it sidestepped 2011) but gave back 18.7 points to the Nifty in 2012 and lost money in 2013. The top-1 rule lost 18.1% in 2013 while the Nifty gained 6.9%.
- **2015-16:** roughly a draw for the Faber rule; the top-1 rule lost 17.1% in 2016 (Nifty +4.0%).
- **2018-19:** the worst stretch. Faber with gold made about -1.7% over the two years and the equity-only version about -10%, against +18% for the Nifty. The top-1 rule lost 16.4% in 2018.
- **2022:** Faber +0.9%, equity-only -3.0%, top-1 -14.2%, against Nifty +5.3%.
- **Sep 2024-2025 and 2026 YTD:** equity-only timing made 6.8% in 2025 (Nifty 11.6%) and -7.3% in 2026 YTD (Nifty -3.4%). The with-gold versions were rescued entirely by gold in 2025.
- The 12-month top-1 rule had four calendar years worse than -14% (2013, 2016, 2018, 2022) in which the Nifty was positive every time.

**Tax drag in India**
- Rates for FY 2026-27 (see the sibling note `etf_tax_and_charges.md` for full sourcing): equity ETFs 20% short-term under 12 months, 12.5% long-term with a Rs 1.25 lakh annual exemption; gold ETFs 12.5% after 12 months and slab rate before, with no exemption; liquid/debt ETFs at slab rate always. — [ICICI Prudential Tax Reckoner 2026-27](https://www.icicipruamc.com/blob/knowledgecentre/tax_reckoner/Tax%20Reckoner%202026-27.pdf); [Zerodha Varsity](https://zerodha.com/varsity/chapter/taxation-for-investors/) (search excerpts, via sibling note)
- Freefincal's rule of thumb in its backtests: cut the tactical portfolio's final value by 20% for tax and exit loads, against 4% for a buy-and-rebalance portfolio. — [Freefincal, Part 2](https://freefincal.com/market-timing-with-ten-month-moving-average-tactical-asset-allocation-backtest-part-2/) (fetched)
- **[own computation] After-tax CAGR**, applying today's rates to the whole history, tax paid at each sale, simple loss carry-forward, full liquidation at the end, no Rs 1.25 lakh exemption, no cess. First figure assumes a 30% slab, second a 10% slab:

  | Strategy | Sample A pre-tax | Sample A after tax | Sample B pre-tax | Sample B after tax |
  |---|---|---|---|---|
  | Buy-and-hold Nifty 50 | 8.2% | 7.6% | 11.3% | 10.6% |
  | Static equal-weight risky assets, annual rebalance | 12.3% | 11.4% | 14.3% | 13.3% |
  | Static 75 Nifty / 25 gold | 10.6% | 9.8% | 12.2% | 11.4% |
  | Faber 10m SMA, with gold | 10.5% | 9.0% / 9.3% | 11.3% | 9.7% / 10.1% |
  | Faber 10m SMA, Nifty only | 8.2% | 7.0% / 7.4% | 9.9% | 8.4% / 8.8% |
  | Dual momentum top-1 12m, with gold | 8.1% | 7.2% / 7.1% | 13.6% | 11.5% / 11.6% |
  | Dual momentum top-1 12m, no gold | 2.1% | 1.4% / 1.8% | 7.4% | 5.7% / 6.1% |
  | Top-2 blended, with gold | 9.2% | 7.8% / 8.2% | 12.3% | 10.5% / 10.8% |

- [own computation] Trading costs at 0.2% per leg with 2-3x one-way turnover cost the rotation rules about 0.8-1.2% a year, already inside the pre-tax figures.

### Inferences
- Tax drag for a switching rule is about 0.7-2.1 points a year (most rows 1.2-1.8); for buy-and-hold or annual rebalancing it is 0.6-1.0 points. The gap of roughly 0.5-1 point a year is the hurdle a rotation rule must clear just to tie, before any skill.
- At Rs 1-5 lakh of capital the Rs 1.25 lakh equity LTCG exemption would shelter most long-term equity gains for the static investor but none of the rotation rule's short-term gains, so the true tax gap for a small account is wider than the table shows.
- After tax, the Faber rule with gold lands above buy-and-hold Nifty in Sample A (9.0-9.3% vs 7.6%, the sample containing all of 2008) and below it in Sample B (9.7-10.1% vs 10.6%). In both it is 2-3 points below the static equal-weight mix. Its only durable advantage is the smaller drawdown.
- The pattern across every strategy family is identical: one or two crisis years (2008, 2011, 2022 globally; 2008 and 2011 in India) pay for many years of small losses. An investor who starts just after a crisis year can wait a decade for the next payoff.
- A month-end bot does not avoid whipsaw; it reduces it. The earlier note measured about 2 switches a year at month-end versus 8 with daily checks.

### Gaps
- The after-tax model applies FY 2026-27 rates to the entire history and ignores the exemption, cess, surcharge and the 87A rebate interaction. It is indicative only.
- No published Indian study quantifying tax drag on a rotation strategy was found beyond Freefincal's flat 20% haircut.
- No evidence was gathered on execution slippage for small orders in Indian midcap or Next 50 ETFs at month-end.
