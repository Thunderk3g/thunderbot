# Rotate ETFs, rent momentum, drop the server

Thunderbot's best realistic upgrade is modest. Replace the single Nifty 200-day switch with a four-sleeve month-end trend rotation (NIFTYBEES, JUNIORBEES, MID150BEES and GOLDBEES, each held only while above its own 200-day average, idle sleeves parked in the growth-type liquid ETF LIQUIDCASE), and hold momentum through a Nifty200 Momentum 30 fund instead of picking 15 stocks. In this session's own single-run backtest the rotation returned **9.3% a year after Groww costs and FY 2026-27 tax over 2011–2026 with an 18% worst fall**, against 6.6–7.4% for the reader's rule on the same engine and 8.8% for simply holding NIFTYBEES. That lead is fragile: **about half of it since 2011, and all of it since 2019, came from gold**, and a plain equal-weight mix of the same four ETFs rebalanced once a year returned more (11.7%) with a deeper fall (27.5%, and 49% in 2008). Rotation buys smaller drawdowns, not higher returns, and the published global record says the same while showing returns roughly halving after publication. Real momentum funds have earned about half their pre-launch premium (+2.8 points a year over the Nifty 200 in 2021–2025 against +5.6 in the 2006–2019 backtest), fell 31.8% in 2024–25 and had not recovered two years later; a self-run 15-stock book needs 1–3.5 points of extra gross return a year just to tie a fund after tax, and honest point-in-time tests show 0–2. The bot can run with no server: Supabase's pg_cron and pg_net can wake a Python function that lives in the same Vercel project as the dashboard, which matters because Vercel Hobby's own cron fires only once a day inside a ±59-minute window. What stays impossible without a broker-registered static IP is placing, changing or cancelling Groww orders by API; with two to four orders a month, the bot should decide and notify and the owner should tap the order in the Groww app. Evidence quality is uneven throughout: this session's network blocked almost every website, so most figures are search-result summaries or single-run computations and are labelled as such.

## Most figures are search summaries or single-run computations, and four of the reader's assumptions need correcting

This research ran under a network policy that refused almost every site except GitHub and PyPI, and the shared web-search budget ran out part-way. No Vercel, Groww, SEBI, NSE, niftyindices, AMFI, Yahoo or AMC page was opened in full on 10 November 2026. The report therefore carries four evidence levels, and every section states which one its figures rest on.

| Label used below | What it means | Typical examples |
|---|---|---|
| **[doc]** | Read directly and in full from source code or the source files of official documentation on GitHub or PyPI, or from this repo | Supabase docs source, Vercel's builder code, the `growwapi` 1.5.0 wheel, yfinance code, Next.js docs source |
| **[summary]** | A search-result summary of the linked page; the page itself was not read | Vercel plan limits, tax rates, Groww pricing, SEBI and NSE rules, fund TERs and AUM, all global strategy literature |
| **[computed]** | This session's own single-run, unreviewed calculation on public GitHub price data (NSE bhavcopy snapshot to 26 Oct 2026) | Rotation backtests, year-by-year returns, liquidity, survivorship measurements, trend-filter tests |
| **[recalled]** | Unverified recollection from before this session; a lead to check, not a fact | Pre-2016 overnight returns, most launch dates, VPS and data-vendor prices |

The computations use adjusted NSE closes from the [NSEDATA4ME snapshot of 26 Oct 2026](https://github.com/ancap97/NSEDATA4ME); the scripts are saved under [research_notes/…/scripts](../research_notes/Thunderbot%20strategy%20and%20serverless%20hosting/scripts/). They are one run on one history with no independent review. Figures carried forward from the 23 October 2026 session, when primary pages could still be read, are marked "earlier session".

Four of the reader's own assumptions do not survive checking. First, the 8.5% result for the 200-day rule **already assumes idle cash earns 6% a year**: the project's backtest note says so and the job runner defaults `cash_yield_pct` to 6.0 ([Thunderbot backtests](../research_notes/Evidence%20based%20NSE%20trading%20strategies/thunderbot_backtests.md); `worker/thunderbot/jobs.py`). Re-run with cash at 0%, the same rule returns **5.3–6.4% after costs, not 8.5%** [computed] ([rotation notes](../research_notes/Thunderbot%20strategy%20and%20serverless%20hosting/computed_rotation_backtests.md)). A liquid ETF therefore does not add two points on top of 8.5%; it is what makes the backtested figure reachable. Second, **equity ETF units pay STT of 0.001% on the sell side only**, and gold and liquid ETFs pay none ([Zerodha Support](https://support.zerodha.com/category/account-opening/resident-individual/ri-charges/articles/stt-etfs)) [summary]. The daily backtester already models this (`etf_sell_stt_pct` in `worker/thunderbot/daily.py`), but the general cost module (`worker/thunderbot/costs.py`) and the earlier cost note apply the share rate of 0.1% on both legs, which is 200 times too high for ETF units. Third, the worker does not keep all its state in Supabase: `worker/thunderbot/store.py` treats a local SQLite file as the source of truth and Supabase as a best-effort mirror, which cannot work on an ephemeral serverless filesystem. Fourth, the momentum ETF tickers differ from the brief: `MOMENTUM` is Aditya Birla Sun Life's ETF, ICICI's is `MOM30IETF` and Kotak's is `MOMENTUM30` ([ABSL AMC](https://mutualfund.adityabirlacapital.com/empower/Passive-ETFs/Nifty-200-Momentum-30-ETF.html); [TradingView](https://in.tradingview.com/symbols/NSE-MOM30IETF/analysis); [Kotak factsheet](https://www.kotakmf.com/factsheet/sept_2026/kotak/Download_pdf/Kotak%20Nifty200%20Momentum%2030%20ETF_Factsheet%20One%20Pager.pdf)) [summary].

## A four-ETF trend rotation beat the 200-day rule by two points after tax, and gold supplied half of it

### Published rules kept their drawdown control and lost about half their return

All figures in this subsection are [summary]. Faber's tactical allocation paper showed about **10.5% a year against 9.0% for buy-and-hold over 1973–2012, with a worst fall of 12% against 45%**, before tax ([EdgeTools](https://edgetools.pages.dev/portfolio-models/gtaa5-live)). A vendor's replication of the same five-asset rule over January 2006 to March 2025, the period after publication, found **6.05% a year with an 11.7% worst fall** ([Concretum Group](https://concretumgroup.com/global-tactical-asset-allocation/)). Real money did worse than the replication. The ETF Cambria ran on the strategy lost its sub-advisor in 2014 and was liquidated in May 2017 ([ETF Trends](https://www.etftrends.com/2017/05/advisorshares-to-close-active-etfs-give-gtaa/)), and Cambria's successor trend fund GMOM has compounded at **5.69% a year from November 2014 to March 2026 with a 25% worst fall**, against a 10-year figure of 3.52% a year beside 11.24% for the S&P 500 ([Cambria fact sheet](https://www.cambriafunds.com/assets/docs/GMOM-FactSheet.pdf); [PortfoliosLab](https://portfolioslab.com/symbol/GMOM)).

Antonacci's dual momentum followed the same path. The book's gross backtest showed **17.4% a year against 9.6% for world equities over 1974–2013** with a worst fall near 23% ([CXO Advisory](https://cxoadvisory.com/momentum-investing/a-few-notes-on-dual-momentum-investing)). The one quantified post-publication test found returns at **about a third of the pre-publication level from 2014 to March 2023, with a drawdown as deep as the S&P 500's** ([Price Action Lab](https://priceactionlab.com/Blog/?p=68274)). ReSolve found the published 12-month look-back "regressed to the median" of 1,226 equally reasonable variants out of sample ([Advisor Perspectives](https://www.advisorperspectives.com/articles/2019/05/06/global-equity-momentum-a-craftsmans-perspective)). That critic's test is a single vendor simulation with no independent replication, so treat its size as indicative.

AQR's century study is the strongest positive evidence, at **11.2% a year net over 1880–2013**, but it describes a leveraged long-short futures strategy across 67 markets ([AQR](https://www.aqr.com/Insights/Research/Journal-Article/A-Century-of-Evidence-on-Trend-Following-Investing)). A long-only switch among Indian equity ETFs and gold has two effective bets and cannot profit from falls. The live record of professional trend funds is lumpy: the SG Trend Index earned **4.9% a year from 2000 to May 2025**, gained 27% in 2022, then posted its worst-ever 12-month loss of 18.7% to April 2025 ([Man Group](https://www.man.com/insights/is-this-time-different); [AdvisorAnalyst](https://advisoranalyst.com/?p=167192)). The sharpest academic caution is Huang, Li, Wang and Zhou, who find that time-series momentum profits are "virtually the same" as a strategy that simply holds assets with positive long-run returns ([WUSTL](https://profiles.wustl.edu/en/publications/time-series-momentum-is-it-there/)). A study of real tactical allocation mutual funds over 1994–2016 found they underperformed every benchmark ([USM repository](https://aquila.usm.edu/fac_pubs/20187)).

### Indian published evidence is thin, gross of tax and drawn from a gold bull market

The Indian results found are blog and forum backtests, all [summary], none live, none after costs or tax. The best known shows a Nifty-or-gold dual momentum rule earning **18.8% a year against 12.1% for the Nifty and 10.9% for gold over 2014–2024**, with an 11.4% worst fall ([Momentum Lab](https://momentumlab.substack.com/p/backtesting-dual-momentum-strategy)). A forum version on NIFTYBEES and GOLDBEES shows 16.1% over about 14 years ([TradingQnA](https://tradingqna.com/t/dual-momentum-strategy-with-niftybees-goldbees/174470)). Freefincal's own caveat on its timing backtests is that they "do not factor in future market movements, human emotions, taxation and exit loads" ([Freefincal](https://freefincal.com/investment-strategy-analysis-idfc-dynamic-equity-fund/)). No public Capitalmind rotation backtest with returns and drawdowns was found, and Weekend Investing and PrimeInvestor could not be researched at all, so this report says nothing about them. The project's earlier test adds one India-specific warning: a 12-month absolute-momentum signal on the Nifty earned only **4.4% a year from July 2008 to October 2026**, because the V-shaped recoveries of 2009 and 2020 punish slow signals ([earlier notes](../research_notes/Evidence%20based%20NSE%20trading%20strategies/momentum_factor_evidence.md)).

### Own backtest: the rotation beats the rule, and a passive mix beats the rotation

Because nothing published is usable, the rotation was tested directly. Everything in this subsection is [computed] from [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME) prices ([rotation notes](../research_notes/Thunderbot%20strategy%20and%20serverless%20hosting/computed_rotation_backtests.md)). The "four sleeves" rule puts 25% in each of NIFTYBEES, JUNIORBEES, a midcap leg and GOLDBEES when that sleeve's signal closes above its 200-day average at month-end, and holds the sleeve in a liquid ETF otherwise. "Dual momentum" holds the two strongest of the four by average 6- and 12-month return, each only if above its 200-day average. Costs follow Groww's schedule with ETF STT at 0.001%, slippage of 5–10 basis points a side, and tax at 20.8% short-term and 13% long-term on equity ETFs, slab rate (31.2%) on short-term gold and on the liquid ETF. Cash earns a flat 6%. The midcap leg is synthetic before February 2011 and a price index after, so 2008–2010 midcap results are approximate.

| Variant | Before costs, 2011–26 | After tax, 2011–26 | Worst fall after tax, 2011–26 | After tax, 2008–18 | After tax, 2019–26 | Worst fall 2008–26, before costs |
|---|---|---|---|---|---|---|
| Buy and hold NIFTYBEES | 9.5% | 8.8% | −36.3% | 5.2% | 10.3% | −59.7% |
| Reader's rule, Nifty index signal, liquid ETF | 7.6% | 6.6% | −19.0% | 6.4% | 9.3% | −27.8% |
| Reader's rule, NIFTYBEES signal, liquid ETF | 8.4% | 7.4% | −16.0% | 6.8% | 10.2% | −27.8% |
| Reader's rule, idle cash at 0% | 5.5% | 5.0% | −23.6% | 4.7% | 7.8% | not reported |
| **Four sleeves** | **10.4%** | **9.3%** | **−18.0%** | **8.7%** | **11.8%** | **−21.5%** |
| Dual momentum, top two | 13.3% | 11.5% | −25.7% | 9.6% | 13.4% | −36.8% |
| Three equity sleeves, no gold | 8.9% | 8.0% | −30.1% | 8.2% | 8.9% | −32.4% |
| Nifty 50, Next 50 and gold sleeves (all real ETF data) | 10.4% | 9.2% | −13.2% | 9.3% | 12.2% | −16.9% |
| Equal weight of the four, rebalanced each December | 12.4% | 11.7% | −27.5% | 9.1% | 14.4% | −49.0% |
| 75% NIFTYBEES, 25% GOLDBEES, annual | 10.6% | 9.9% | −27.2% | 7.4% | 12.7% | −43.9% |

After-tax figures are at ₹5 lakh with everything sold at the end. The closest reproduction of the reader's own rule gave 7.8–8.3% after costs against the reader's 8.55%, and 7.4–7.7% after tax against 8.07%; the remaining gap is unexplained and probably reflects Yahoo data differences.

Three results matter. The four-sleeve rotation beat the reader's rule after costs and tax by **1.6 to 2.7 points a year in every sub-period**, with a similar or shallower worst fall. The dual-momentum version added more return but fell 25–37%, deeper than the reader's rule in every period. And **the passive equal-weight mix out-returned both rotations in most periods**; the rotation's contribution was cutting the worst fall from 27.5% to 18% since 2011 and from 49% to about 21% in 2008. The reader's rule also needs restating. The earlier comparison set the rule's after-tax 8.1% against a pre-tax 9.5% for buy-and-hold; the fair benchmark is NIFTYBEES after tax at 8.8%, and the rule still trailed it in all 30 specifications tested over 2011–2026.

Account size barely matters for ETFs. Costs took about 0.6 points a year from the rotation at ₹1 lakh, 0.4 at ₹5 lakh and 0.3 at ₹20 lakh, while tax drag ran the other way (0.3, 0.7 and 1.1 points) because the ₹1.25 lakh exemption covers less of a larger account's gains.

### Gold explains half the edge since 2011 and all of it since 2019

The year-by-year record shows why. All figures are [computed] ETF price returns, which track total return closely for these funds: NIFTYBEES returned −7.41% against −7.43% for the Nifty 50 total-return index over May 2025 to October 2026.

| Year | Gold (GOLDBEES) | Nifty 50 (NIFTYBEES) | Next 50 (JUNIORBEES) | Midcap 100 ETF (MOM100) | Overnight index (Nifty 1D Rate) |
|---|---|---|---|---|---|
| 2008 | 24.5 | −52.1 | −63.7 | — | — |
| 2009 | 24.9 | 75.6 | 123.9 | — | — |
| 2010 | 21.7 | 18.6 | 18.0 | — | — |
| 2011 | 29.9 | −24.0 | −31.7 | — | — |
| 2012 | 11.2 | 26.5 | 47.2 | 40.2 | — |
| 2013 | −6.4 | 7.2 | 5.7 | −2.2 | — |
| 2014 | −9.3 | 31.6 | 43.7 | 55.6 | — |
| 2015 | −7.5 | −4.3 | 7.9 | 7.6 | — |
| 2016 | 12.5 | 4.0 | 7.5 | 7.2 | — |
| 2017 | 2.4 | 29.9 | 45.4 | 46.2 | 6.0 |
| 2018 | 6.7 | 4.8 | −7.5 | −15.0 | 6.2 |
| 2019 | 22.9 | 13.6 | 1.0 | −2.7 | 5.8 |
| 2020 | 27.0 | 15.4 | 15.8 | 21.7 | 3.4 |
| 2021 | −5.2 | 26.0 | 30.4 | 45.5 | 3.3 |
| 2022 | 12.8 | 5.5 | 0.8 | 4.9 | 4.7 |
| 2023 | 14.7 | 21.0 | 26.9 | 47.2 | 6.8 |
| 2024 | 19.4 | 10.4 | 28.1 | 24.5 | 6.8 |
| 2025 | 71.8 | 11.7 | 2.5 | 6.4 | 5.8 |
| 2026 to 26 Oct | 5.5 | −12.2 | −3.6 | −6.6 | 4.3 |

Source: [rotation notes](../research_notes/Thunderbot%20strategy%20and%20serverless%20hosting/computed_rotation_backtests.md), data [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME). Gold compounded at **13.6% a year over 2008–2026 against 7.9% for NIFTYBEES and 9.6% for JUNIORBEES**, but the split is stark: **9.2% a year in 2008–2018 and 19.9% in 2019–2026**, with 2025 alone at +71.8%. Gold also spent 6.6 years under water after November 2012.

Removing gold from the rotation cut its after-tax lead over the reader's rule from +2.7 to +1.4 points over 2011–2026, and from +2.5 to −0.4 points over 2019–2026. A gentler test, which "de-trends" gold from 2019 to its 2008–2018 growth rate while keeping its path, removed less than half as much (13.2% to 11.0% before costs, against 10.0% with no gold). The remainder is timing: gold rose when Indian equities fell in 2020, 2022 and 2025–26. That pattern is a property of one stretch of history, and the data cannot say whether it will repeat. In 2008–2018 the no-gold rotation still led the rule by about two points, but that period leans on the synthetic midcap series and on JUNIORBEES's 124% rebound in 2009.

### The day of the month moved the reader's rule more than the choice of rule did

Timing luck is the largest single source of dispersion [computed]. Moving the reader's decision from month-end to the 15th trading day cut its 2011–2026 return from **7.6% to 3.9% and deepened its worst fall from 18% to 43%**, because a mid-month check sat through most of March 2020. Across 30 near-equivalent specifications (five decision days, three look-backs, two buffers) the rule's after-tax return ranged from 3.0% to 8.4% with a median of 6.0%; the reader's month-end, 200-day, 1% buffer choice sits near the top. The four-sleeve rotation was steadier, at **7.3% to 9.8% with a median of 8.9%**, because four signals rarely flip on the same day, though its worst fall still reached 31% with a mid-month decision. The rotation beat the rule in all 30 matched specifications in every period; the no-gold rotation won in only 19 of 30 over 2019–2026. This matches the global finding that shifting Faber's rule by a few days moved its worst fall from about 19% to about 30% ([Newfound Research](https://blog.thinknewfound.com/2013/08/the-luck-of-the-rebalance-timing/)) [summary].

Two smaller findings shape implementation. Trading at the next day's close instead of the decision day's close cost 0.3–1.4 points a year, so a 15:10 decision executed before 15:30 is worth keeping. And the 1% buffer had no consistent sign: it helped the rule in 2008–2018 and hurt it in 2019–2026.

At the end of the data every trend variant was fully in cash from 30 September 2026. The Nifty then rose about 10% between 26 October and 9 November, taken from a third-party file not cross-checked against NSE, while the month-end rule stayed out. That is the rule working as designed, and it is what lagging a V-shaped recovery feels like.

## Five ETFs are liquid enough to trade; momentum, gilt and overseas ETFs are not

### The instrument list

"First trade" is the first date each ticker appears in NSE bhavcopy data and median traded value is NSE-only for the 12 months to 26 October 2026, both [computed] from [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME). Expense ratios and fund sizes are [summary]. Bid-ask spreads, tracking difference and premium or discount to NAV were not sourced for any of these ETFs.

| Role | NSE ticker | First trade in NSE data | Expense ratio | Fund size | Median daily traded value | Verdict |
|---|---|---|---|---|---|---|
| Nifty 50 | NIFTYBEES | before 2005 | 0.04% | ₹57,033 cr (31 Mar 2026) | ₹188.5 cr | Use |
| Nifty 50 (alternative) | SETFNIF50 | not checked | 0.04% | about ₹2.1 lakh cr | not measured | Institutional size; NIFTYBEES has the retail volume |
| Nifty Next 50 | JUNIORBEES | before 2005 | not confirmed | not confirmed | ₹29.1 cr | Use |
| Nifty Midcap 150 | MID150BEES | 4 Feb 2019 | not confirmed | not confirmed | ₹17.7 cr | Use; backtest on the index before 2019 |
| Nifty Midcap 100 | MOM100 | 4 Feb 2011 | not confirmed | not confirmed | ₹2.7 cr | Backtest proxy only |
| Gold | GOLDBEES | 19 Mar 2007 | not confirmed | not confirmed | ₹345 cr | Use |
| Silver | SILVERBEES | 7 Feb 2022 | not confirmed | not confirmed | ₹645 cr | Avoid |
| Liquid, growth type | LIQUIDCASE | 24 Jan 2024 | 0.23–0.28% | ₹11,179–11,836 cr (Nov 2026) | ₹199.6 cr | Use as the cash leg |
| Liquid, growth type | LIQUIDADD | 3 Apr 2024 | about 0.31% (undated) | about ₹1,900 cr (undated) | ₹51.7 cr | Backup cash leg |
| Liquid, growth type | GROWWLIQID | 26 Sep 2024 | not confirmed | not confirmed | ₹2.5 cr | Too thin |
| Liquid, daily dividend | LIQUIDBEES | before 2005 | 0.59–0.71% | ₹11,614 cr (5 Nov 2026) | ₹316.8 cr | Avoid for a bot |
| Nasdaq 100 | MON100 | 31 Mar 2011 | not confirmed | not confirmed | ₹20.7 cr | Avoid: premium to NAV |
| US mega-cap | MAFANG, MASPTOP50 | 14 May 2021, 24 Sep 2021 | not confirmed | not confirmed | ₹4.5 cr, ₹1.5 cr | Avoid: premium to NAV |
| Long gilt | LTGILTBEES | 14 Jul 2016 | not confirmed | not confirmed | ₹4.6 cr | Marginal |
| 5-year and 10-year gilt | GILT5YBEES, SETF10GILT | 8 Apr 2021, 23 Jun 2016 | not confirmed | not confirmed | ₹1.5 cr, ₹0.21 cr | Too thin |

Sources for the [summary] columns: [1 Finance](https://1finance.co.in/product-scoring/mutual-funds/equity/nippon-india-etf-nifty-50-bees), [sharpely](https://sharpely.in/etfs/tata-nifty-50-exchange-traded-fundgrowth/38578/similar-funds), [Zerodha Fund House](https://www.zerodhafundhouse.com/etfs/zerodha-nifty-1d-rate-liquid-etf-ZLIQD), [mStock](https://www.mstock.com/mutual-fund-investments/zerodha-nifty-1d-rate-liquid-etf/mf7454), [INDmoney](https://www.indmoney.com/etfs/liquid), [Upstox](https://upstox.com/etfs/nip-ind-etf-liquid-bees-share-price/INF732E01037/). The mapping of LIQUIDADD to DSP's BSE Liquid Rate ETF is [recalled], as are the usual launch dates for the pre-2005 funds (NIFTYBEES December 2001, JUNIORBEES February 2003, LIQUIDBEES July 2003).

The five instruments a four-sleeve rotation uses all trade well over ₹15 crore on a median day, so the largest single order in a ₹20 lakh account is about 0.6% of a day's volume. Traded value says nothing about the premium at the moment of the order, so limit orders still apply.

### Liquid ETFs: use the growth kind

LIQUIDBEES declares a dividend every day so that its NAV falls back to ₹1,000, and credits the income as new units ([Capitalmind](https://premium.capitalmind.in/2016/04/premium-understanding-liquid-bees-an-etf-for-safe-parking-of-funds-and-to-optimize-margins/)) [summary]. Its price stayed between ₹969.64 and ₹1,006.53 across the whole data set [computed], so a price-only backtest shows zero return and a live holding drifts as units arrive. Fractional units cannot be sold on the exchange and must be redeemed off-market ([Zerodha Support](https://support.zerodha.com/category/mutual-funds/understanding-mutual-funds/articles/redeeming-fractional-units)), each dividend is taxable income with 10% TDS above ₹10,000 a year ([Quicko](https://learn.quicko.com/section-194k-tds-dividend-mutual-funds)), and brokers have struggled to report it correctly ([TradingQnA](https://tradingqna.com/t/inaccurate-capital-gains-for-liquidbees-in-zerodha-tax-p-l/169419)) [summary].

LIQUIDCASE and the other growth-type ETFs pay no dividend: the price itself climbs a paisa or two a day, the unit count never changes, and nothing is taxed until sale ([TradingQnA](https://tradingqna.com/t/liquidcase-vs-liquidbees/159606)) [summary]. LIQUIDCASE's NAV stood at about ₹116.73 on 4 November 2026 from a ₹100 base ([mStock](https://www.mstock.com/mutual-fund-investments/zerodha-nifty-1d-rate-liquid-etf/mf7454)). Realised yields are a little below the overnight rate [computed]: **LIQUIDCASE 5.64% a year since January 2024 against 5.94% for the Nifty 1D Rate index**, LIQUIDADD 5.54% against 5.88% since April 2024, and GROWWLIQID 5.24% against 5.69% since September 2024. LIQUIDCASE returned 5.5% in 2025 and 4.0% in 2026 to 26 October, about 4.9% annualised. None of the three had a down day larger than 0.01%. LIQUIDBEES's higher expense ratio shows in its 5-year return of 4.81% a year to July 2026 ([sharpely](https://sharpely.in/etfs/nippon-india-etf-nifty-1d-rate-liquid-beesidcw-daily/1787/performance)) [summary]. Current 7-day yields were not sourced.

A flat 6% for the cash leg is therefore slightly generous for recent years. The overnight index can be computed only from mid-2016; earlier years are [recalled] and must be replaced with real data before use.

| Year | Overnight return | Status |
|---|---|---|
| 2008 | about 7–8% | [recalled] |
| 2009 | about 3.3% | [recalled] |
| 2010 | about 5% | [recalled] |
| 2011 | about 7.8% | [recalled] |
| 2012 | about 8.2% | [recalled] |
| 2013 | about 8.3% | [recalled] |
| 2014 | about 8.2% | [recalled] |
| 2015 | about 7.2% | [recalled] |
| 2016 | about 6.4% | [recalled] |
| 2017 | 6.0% | [computed], Nifty 1D Rate index |
| 2018 | 6.2% | [computed] |
| 2019 | 5.8% | [computed] |
| 2020 | 3.4% | [computed] |
| 2021 | 3.3% | [computed] |
| 2022 | 4.7% | [computed] |
| 2023 | 6.8% | [computed] |
| 2024 | 6.8% | [computed] |
| 2025 | 5.8% | [computed] |
| 2026 to 26 Oct | 4.3% | [computed] |

Liquid funds historically earned somewhat more than the overnight rate [recalled], and the three growth-type liquid ETFs have earned about 0.3–0.45 points less than the overnight index [computed]. The free way to build the real 2008–2016 series is an old overnight fund's NAV history from AMFI, which this session could not reach.

### Overseas ETFs are unusable while the investment cap binds

All [summary]. SEBI's June 2021 circular caps overseas investment at USD 1 billion per fund house within an industry limit of USD 7 billion, with a separate USD 1 billion industry limit for overseas ETFs ([SCC Online](https://www.scconline.com/blog/post/2021/06/05/sebi-issues-circular-for-the-enhancement-of-overseas-investment-limits-on-mutual-funds/)). Subscriptions were halted in early 2022 and again for overseas-ETF schemes in March 2024 ([Business Standard](https://www.business-standard.com/amp/markets/news/sebi-directs-mutual-funds-to-stop-inflows-into-etf-based-overseas-schemes-124032101060_1.html)), and the cap was still binding on **18 July 2026**, the latest date confirmed ([Business Today](https://www.businesstoday.in/mutual-funds/story/why-are-mutual-funds-stopping-international-sips-heres-how-sebis-overseas-investment-cap-works-543752-2026-07-18)). With unit creation frozen, prices detach from NAV. NSE warned investors on 25 September 2026 ([NSE press release](https://nsearchives.nseindia.com//web/pressrelease/2026-09/PR_cc_25092026_20260925122830.pdf)). Motilal Oswal's Nasdaq Q50 ETF went from ₹142 to ₹396.30 in ten sessions against a NAV of ₹118.14, a premium near **235%** ([inkl](https://www.inkl.com/news/bse-cautions-investors-as-international-etfs-trade-at-steep-premiums-to-nav-what-should-investors-do)); MASPTOP50 averaged a 49% premium and peaked at 83% ([TradingView News](https://www.tradingview.com/news/moodys:e962a48496436:0-overseas-etfs-nearly-30-of-turnover-at-inflated-prices/)); MON100 closed 17% above NAV in mid-June 2026 ([Finvezto](https://finvezto.com/reports/global-etf-premium-to-nav)). The premium can collapse overnight if limits rise, or when the price-band base moves to NAV, planned for 1 April 2027. A backtest on these prices also overstates returns, because the price history contains the premium.

### Practical traps

Three traps deserve code. First, unit splits: Nippon split NIFTYBEES 10-for-1 and GOLDBEES 100-for-1 with a record date of 20 December 2019 and ex-date of 19 December ([NSE circular CML42888](https://nsearchives.nseindia.com/content/circulars/CML42888.pdf); [Trendlyne](https://trendlyne.com/equity/Split/GOLDBEES/1582/nippon-india-etf-gold-bees-split)) [summary]. The bhavcopy-derived series used here is correctly adjusted across those dates [computed]. Yahoo could not be tested this session, but the project's own notes record that its NIFTYBEES split was unadjusted and had to be repaired, so any one-day move beyond −50% with no matching index move should block trading. Second, ETF closes misprice on panic days [computed]: JUNIORBEES fell 1.3% on 4 June 2024 when its index fell 9.3%, and MID150BEES rose 15.8% on 19 March 2020 when its index fell 4.0%. Signals computed on ETF prices inherit that noise. Third, premiums: silver ETFs traded 5.7% to 15% above fair value in October 2025 during a physical shortage ([Asianet Newsable](https://newsable.asianetnews.com/markets/silver-etf-prices-hit-record-kotak-mutual-fund-puts-fresh-investments-on-hold-articleshow-c4rbhio); [Business Standard](https://www.business-standard.com/amp/finance/personal-finance/why-mfs-are-freezing-silver-etf-investments-and-what-it-means-for-you-125101400231_1.html)) [summary], and SILVERBEES then fell 23.2% in a day on 2 February 2026 [computed, not cross-checked]. A rule that buys what rose last month buys silver exactly when its premium is widest.

SEBI's ETF price-band framework also changed in 2026 [summary]. The band is now anchored to the ETF's own previous close, defined as the last 30 minutes' volume-weighted price, with an initial band of ±10%, in place of ±20% around NAV ([Taxmann](https://www.taxmann.com/post/blog/sebi-revises-etf-price-band-and-pre-open-auction-framework/); [NSE circular CMTR76101](https://nsearchives.nseindia.com/content/circulars/CMTR76101.pdf)). It was reported effective 1 September 2026, though one extract mentions a late-August extension, so the operative date is unresolved. Nothing mechanical now stops a premium compounding at 10% a day, so the bot should refuse any buy more than a set margin above indicative NAV.

## Equity ETFs pay 20.8% on short-term gains; gold and liquid ETFs pay slab rate

Everything in this section is [summary]; no Finance Act or Income-tax Act 2025 text was read, and the section numbers come from secondary guides and AMC tax reckoners that agree with each other. Budget 2026 changed nothing for these instruments: its STT increase applied to derivatives only ([ClearTax](https://cleartax.in/s/budget-2026-highlights)).

| ETF category, units bought now and sold in FY 2026-27 | Long-term after | Short-term rate | Long-term rate | ₹1.25 lakh exemption | STT on delivery sale |
|---|---|---|---|---|---|
| Equity (Nifty 50, Next 50, Midcap 150, momentum) | more than 12 months | 20% (20.8% with cess) | 12.5% (13.0%) | Yes, one limit shared across all listed equity and equity funds | 0.001% |
| Gold and silver | more than 12 months | Slab rate (31.2% at the top slab) | 12.5% (13.0%), no indexation | No | Nil |
| India-listed international | more than 12 months (some sources say 24) | Slab rate | 12.5% (13.0%) | No | Nil on those named, such as the Nasdaq 100 ETF |
| Liquid, gilt, debt, Bharat Bond | never | Slab rate, always | not applicable | No | Nil |

Sources: [CBDT FAQs, July 2024](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2036604&reg=48&lang=2); [ICICI Prudential Tax Reckoner 2026-27](https://www.icicipruamc.com/blob/knowledgecentre/tax_reckoner/Tax%20Reckoner%202026-27.pdf); [Outlook Money](https://www.outlookmoney.com/invest/tax-reckoner-2026-27-how-mutual-fund-investments-will-be-taxed-after-budget); [Zerodha Support](https://support.zerodha.com/category/account-opening/resident-individual/ri-charges/articles/stt-etfs). Under the Income-tax Act 2025 the equity provisions are sections 196 and 198, the general long-term provision is 197 and the debt-fund rule is section 76 ([ebizfiling](https://ebizfiling.com/blog/section-196-and-198-short-term-and-long-term-capital-gains/)).

Four consequences follow for a monthly rotation. Nearly every exit is short-term, so the asset class sets the rate: a ₹10,000 gain costs ₹2,080 in an equity ETF and ₹3,120 in GOLDBEES at the top slab, and the backtester must apply the rate by instrument. The ₹1.25 lakh exemption applies only to long-term equity gains, so a rotation almost never uses it. The section 87A rebate cannot be used against the 20% and 12.5% rates since FY 2025-26 ([TaxGuru](https://taxguru.in/income-tax/section-87a-rebate-stcg-111a-tax-planning-fy-2025-26.html)); it plausibly still shelters slab-rate gains from gold and liquid ETFs for a resident with total income within ₹12 lakh, but that is an inference no source stated. And a 6% liquid yield nets about 4.1% at the 30% slab, 4.75% at 20% and 5.7% at 5%.

Short-term losses offset any capital gain, long-term losses offset only long-term gains, and unused losses carry forward eight years if the return is filed on time ([ClearTax](https://cleartax.in/glossary/capital-loss-carryover)). One conflict is moot here: sources disagree on gold ETF units bought between April 2023 and March 2025, but units bought now are outside it on every reading. One residual risk is not moot: CBDT Circular 6/2016 protects capital-gains treatment only for holdings over 12 months ([circular text](https://finodha.in/wp-content/uploads/2024/05/CBDT-Circular-No.-62016.pdf)), so a monthly rotator relies on facts and consistency, not a safe harbour. The reclassification risk for a few delivery ETF trades a month with own money looks low but is not zero.

Groww bills ETFs like shares apart from STT. Brokerage is the lower of ₹20 or 0.1% per order with a ₹5 minimum, and the DP charge has been ₹20 plus GST (₹23.60) per ETF per sell day since 21 June 2025 ([Groww Pricing](https://groww.in/pricing); [Business Standard](https://www.business-standard.com/amp/companies/news/groww-to-raise-minimum-brokerage-dp-and-mtf-charges-from-june-21-125052200669_1.html)). Stamp duty is 0.015% on buys, exchange and investor-protection charges total 0.00307% a side, the SEBI fee is 0.0001% and GST is 18% on the non-statutory items. Groww's schedule was read directly on 23 October 2026 and only re-confirmed through search summaries today. No Groww source confirmed or denied a brokerage or DP waiver on liquid ETFs.

| Order value | Equity ETF round trip | Liquid ETF round trip | A share, for comparison | Days of a 6% yield to recover the liquid round trip |
|---|---|---|---|---|
| ₹10,000 | ₹49.55 (0.50%) | ₹49.45 (0.49%) | ₹69.45 (0.69%) | about 30 |
| ₹1,00,000 | ₹94.28 (0.094%) | ₹93.28 (0.093%) | ₹293.28 (0.29%) | about 6 |
| ₹5,00,000 | ₹188.21 (0.038%) | ₹183.21 (0.037%) | ₹1,183.21 (0.24%) | about 2 |

These are arithmetic on the schedule above ([tax and cost notes](../research_notes/Thunderbot%20strategy%20and%20serverless%20hosting/etf_tax_and_groww_costs.md)). The fixed DP charge dominates small trades: by the same arithmetic a ₹25,000 sleeve pays about ₹76 for the round trip, so parking it for less than about three weeks costs more than it earns.

## Live momentum has earned about half its backtested premium, and the fund beats a 15-stock book

### The products: one index fund holds the money, and the ETFs are thin

Product facts are [summary]; first-trade dates and traded values are [computed].

| Product | NSE ticker | First trade | Expense ratio | Fund size | Median daily traded value, 12 months | Tracking |
|---|---|---|---|---|---|---|
| ICICI Pru Nifty 200 Momentum 30 ETF | MOM30IETF | 10 Aug 2022 | 0.30% | ₹552–557 cr (undated) | ₹2.4 cr | Tracking difference −0.63% since inception; error 0.25% (31 Aug 2026) |
| Motilal Oswal Nifty 200 Momentum 30 ETF | MOMOMENTUM | 17 Feb 2022 | 0.30–0.36% | ₹125–154 cr | ₹0.43 cr | not found |
| HDFC NIFTY200 Momentum 30 ETF | HDFCMOMENT | 17 Oct 2022 | 0.30% | ₹87–102 cr | ₹0.49 cr | Error 0.17% (Feb 2026) |
| Aditya Birla SL Nifty 200 Momentum 30 ETF | MOMENTUM | 19 Aug 2022 | 0.17% (AMC page) | ₹38–48 cr | ₹0.18 cr | not found |
| Kotak Nifty200 Momentum 30 ETF | MOMENTUM30 | 17 Oct 2025 | 0.26% | ₹33–36 cr | ₹0.10 cr | Error 0.27% (30 Sep 2026) |
| UTI Nifty200 Momentum 30 Index Fund | not listed (mutual fund) | launched 10 Mar 2021 | unresolved, 0.43–0.78% direct | ₹7,962 cr (30 Sep 2026) | not applicable | Difference −0.56% 1-year, −0.37% 5-year, direct; error 0.15% |
| ICICI Pru Nifty 100 Low Vol 30 ETF | LOWVOLIETF | 11 Jul 2017 | not confirmed | not confirmed | ₹3.1 cr | not found |
| ICICI Pru Alpha Low Vol 30 ETF | ALPL30IETF | 18 Aug 2020 | not confirmed | not confirmed | ₹1.5 cr | not found |

Sources: [ICICI Pru factsheet](https://www.icicipruamc.com/blob/knowledgecentre/factsheet-schemes/Passive%20Schemes/ETFs%20Schemes/ICICI%20Prudential%20Nifty%20200%20Momentum%2030%20ETF.pdf); [Upstox](https://upstox.com/etfs/motilalamc-momomentum-share-price/INF247L01BK2/); [Groww](https://groww.in/etfs/hdfc-nifty-momentum-etf); [AdvisorKhoj](https://www.advisorkhoj.com/mutual-funds-research/UTI-Nifty-200-Momentum-30-Index-Fund-Regular-Plan-Growth-Option); UTI tracking from an AMFI-data compilation as of 1 July 2026 ([nse-strategy-indices-visualised](https://github.com/patel-26meet/nse-strategy-indices-visualised)). UTI's fund holds roughly two-thirds of the category. The issuers shown for LOWVOLIETF and ALPL30IETF come from the brief and were not re-verified. Tickers, costs and sizes for Midcap150 Momentum 50, Nifty500 Momentum 50 and Alpha 50 funds could not be researched; only their index records appear below.

No momentum ETF trades more than ₹2.5 crore on a median day. A ₹5 lakh order is about 2% of MOM30IETF's median day and a ₹20 lakh order about 8%; in the other four a ₹20 lakh order would be 40% to 200% of a day's trading. Momentum funds are also three to four times harder to run than a Nifty 50 fund: the median Nifty 50 index fund trails its index by 0.18% a year in the direct plan, while momentum ETFs trail by 0.5–0.85% and direct-plan momentum index funds by a median of 0.80%, on AMFI data as of 1 July 2026 ([nse-strategy-indices-visualised](https://github.com/patel-26meet/nse-strategy-indices-visualised)).

### Calendar years and the 2024–25 slump

Total-return index figures below come from a third-party compilation of NSE's daily feed, read directly, whose momentum figures match NSE's own whitepaper to two decimals ([nse-strategy-indices-visualised](https://github.com/patel-26meet/nse-strategy-indices-visualised)). The UTI column is the regular plan [summary] ([ProfitGuru](https://www.profitguruonline.com/mutual-funds/scheme/uti-nifty-200-momentum-30-index-fund-regular-plan-growth-option-148704)).

| Year | Nifty 50 | Nifty 200 | Momentum 30 index | UTI Momentum 30 fund (regular) | Alpha 50 | Low Vol 30 | Quality 30 | Alpha Low-Vol 30 | Value 50 |
|---|---|---|---|---|---|---|---|---|---|
| 2021 | 25.6 | 28.9 | 53.8 | part year | 75.4 | 24.2 | 26.2 | 30.9 | 56.4 |
| 2022 | 5.7 | 4.9 | −5.5 | −5.95 | −13.5 | 2.0 | −4.4 | −3.1 | 23.2 |
| 2023 | 21.3 | 24.7 | 41.7 | 40.59 | 43.6 | 31.9 | 31.7 | 39.0 | 62.6 |
| 2024 | 10.1 | 14.8 | 21.3 | 20.36 | 33.9 | 12.4 | 14.4 | 17.8 | 20.2 |
| 2025 | 11.9 | 9.6 | −4.6 | −5.78 | −10.2 | 11.5 | 4.7 | 0.3 | 16.9 |
| 2026 to 2 Sep | −7.6 | −3.5 | −0.8 | not found | 12.6 | −4.3 | −3.6 | −0.2 | 3.8 |

Nifty Midcap150 Momentum 50 returned 52.5%, 32.3% and −3.5% in 2023, 2024 and 2025 against 44.6%, 24.5% and 6.0% for the Midcap 150 ([NSE whitepaper, April 2026](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf), earlier session).

The slump was twice as deep as the market's and far longer. The Momentum 30 index fell **31.8% from 27 September 2024 to 7 April 2025** [computed], which matches the live Motilal ETF's 31.7% fall ([ProfitGuru](https://www.profitguruonline.com/mutual-funds/scheme/motilal-oswal-nifty-200-momentum-30-etf-149801)), against about 15–16% for the Nifty 50 over the same dates. It had **not regained its peak by 26 October 2026**, more than two years on, and has trailed the Nifty 200 since 14 June 2024 [computed]. The June 2025 rebalance replaced 20 of 30 stocks after the fall ([Value Research](https://www.valueresearchonline.com/stories/225617/two-thirds-momentum-index-changes-just-one-day/)) [summary]. An actively managed momentum fund did not escape: Samco's drew down 23% from January 2025 and had not recovered by August 2026 ([Arthgyaan](https://arthgyaan.com/fund/samco-active-momentum-fund-direct-growth-option/151753)) [summary]. No evidence was found that NSE changed its rebalancing rules in response.

### Live results beside the pre-launch backtest

The index launched on 25 August 2020, so 71% of its quoted history is back-calculated. Splitting NSE's own calendar-year table at the launch date gives the cleanest comparison [computed from the [NSE whitepaper](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf)].

| Period | Status | Momentum 30 | Nifty 200 | Excess | Years ahead |
|---|---|---|---|---|---|
| 2006–2019 | Backtest, all pre-launch | 17.5% | 11.9% | +5.6 | 11 of 14 |
| 2021–2025 | Live index | 19.0% | 16.2% | +2.8 | 3 of 5 |
| 2022–2025 | Live index and first full fund years | 11.6% | 13.2% | −1.6 | 2 of 4 |

Other live windows give smaller numbers: +1.0 point a year from launch to 26 October 2026 on price indices, with a third more volatility (19.4% against 14.7%) [computed], and +0.4 over the five years to 2 September 2026 on total return. All of the lead was earned by March 2024; from April 2024 to June 2026 momentum gained 2.1% in total against 14.7% for the Nifty 200 [computed from the [HDFC AMC deck](https://files.hdfcfund.com/s3fs-public/Others/2026-07/HDFC%20NIFTY200%20Momentum%2030%20Index%20Fund_PPT%20%28July%202026%29.pdf)]. UTI's fund has compounded at roughly 14.5–14.75% a year in the direct plan and about 13% in the regular plan since March 2021 ([Sharpely](https://sharpely.in/mutual-funds/uti-nifty200-momentum-30-index-fund-directgrowth/41312/performance); [Dezerv](https://www.dezerv.in/mutual-funds/uti-nifty200-momentum-30-index-fund-regular-growth-inf789f1aus7/)) [summary, undated]. Five live years with two slumps is too short to call the premium gone, and the survivorship-adjusted IIM Ahmedabad data still show one. But the planning number is half the backtest or less, which is also what US research found: smart-beta indices beat the market by 2.77% a year before listing and trailed by 0.44% after ([InvestmentNews on "The Smart Beta Mirage"](https://www.investmentnews.com/industry-news/news/smart-beta-funds-dont-live-up-backtesting-196778)) [summary].

### Since 2005, every factor has had a multi-year drought

Since-2005 figures are mostly backtest (earlier session, from NSE factsheets): Momentum 30 at 18.3–18.8% a year against 13.9% for the Nifty 200, with a 67.7% fall in 2008; Alpha Low-Volatility 30 at 17.7%; Quality 30 at 16.6%; Alpha 50 at 20.2% from a 2003 base ([NSE factsheet](https://www.niftyindices.com/Factsheet/Factsheet_Nifty200_Momentum30.pdf); [HDFC AMC deck](https://files.hdfcfund.com/s3fs-public/Others/2026-07/HDFC%20NIFTY200%20Momentum%2030%20Index%20Fund_PPT%20%28July%202026%29.pdf)). Low Volatility 30 has a since-2005 figure only to May 2018, and no since-2005 figure for value could be retrieved. The live record since each index's launch is the honest test [computed, price indices to 26 October 2026; [factor notes](../research_notes/Thunderbot%20strategy%20and%20serverless%20hosting/factor_indices_survivorship_diy_vs_etf.md)].

| Index | Live from | Live return | Benchmark return | Excess | Worst fall | Longest stretch behind its benchmark |
|---|---|---|---|---|---|---|
| Nifty200 Momentum 30 | Aug 2020 | 14.5% | 13.5% (Nifty 200) | +1.0 | −31.8% | 2.4 years, from June 2024, ongoing |
| Nifty Alpha 50 | Nov 2012 | 19.5% | 12.2% (Nifty 500) | +7.3 | −40.7% | 2.4 years, 2018–2020 |
| Nifty100 Low Volatility 30 | Jul 2016 | 10.4% | 10.3% (Nifty 100) | +0.1 | −31.0% | 6.5 years, from April 2020, ongoing |
| Nifty200 Quality 30 | Apr 2018 | 8.6% | 10.1% (Nifty 200) | −1.4 | −29.5% | 6.5 years, ongoing |
| Nifty Alpha Low-Volatility 30 | Jul 2017 | 10.5% | 10.0% (Nifty 200) | +0.5 | −31.3% | 6.6 years, ongoing |
| Nifty500 Value 50 | Oct 2018 | 17.2% | 12.3% (Nifty 500) | +5.0 | −54.5% | 4.7 years, 2018–2023 |
| Nifty Midcap150 Momentum 50 | Aug 2022 | 14.2% | 14.4% (Midcap 150) | −0.2 | −25.6% | 2.4 years, ongoing |

The low-volatility and quality droughts are measured from a relative high set at the bottom of the COVID crash, which overstates them; on calendar years Low Vol 30 beat the Nifty 100 in three of six years from 2020. Momentum's longest drought is in the backtest: it made no net progress against the Nifty 200 across the five calendar years 2008–2012, about six years from peak to recovery. Value lost 7.5 points a year for five years before its recent run. Only Alpha 50 and Value 50 have kept a large live edge, and both carry the deepest falls.

Combinations have delivered a smoother ride, not a premium. Alpha Low-Volatility 30 and Alpha Quality Low-Volatility 30 are each about +0.5 points a year over the Nifty 200 since July 2017, Quality Low-Volatility 30 is −1.6, and the one blend with a clear live edge, the four-factor Alpha Quality Value Low-Volatility 30 at +2.4, has no fund tracking it [computed]. A simple 50:50 of the Momentum 30 and Low Vol 30 calendar-year returns for 2021–2025 gives about 17.7% a year against 16.2% for the Nifty 200 and 19.0% for momentum alone, with a worst year of −1.7% against −5.5% [computed]. That blend is buyable with two cheap funds and is the most defensible combination on live data.

### An honest backtest is now free, and it shows survivorship adds 8–10 points a year

A hobbyist can rebuild point-in-time data in about a day plus a weekend, from pieces inspected directly this session ([factor notes](../research_notes/Thunderbot%20strategy%20and%20serverless%20hosting/factor_indices_survivorship_diy_vs_etf.md)). NSE's own inclusion and exclusion workbook, `IndexInclExcl.xls`, lists every change to the Nifty 50 from 1996, Nifty 100 from 2003, Nifty 200 from November 2011 and Nifty 500 from 1998, up to July–September 2020, by company name ([copy in a public repo](https://github.com/rishabhjain0295-web/nifty500-momentum-backtest)). After 2020 the changes come from archived constituent lists and the half-yearly press releases. The project [nsepit](https://github.com/NegativeZone/nsepit) offers validated point-in-time Nifty 50 membership from 2005; an equal-weight portfolio built from it tracked NSE's official equal-weight index within 0.5 points a year. For prices, [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME) publishes a split- and bonus-adjusted bhavcopy database from 2005 with **4,583 securities, of which 1,037 are delisted or inactive**, including DHFL, Ranbaxy, HDFC Ltd and Satyam. It does not adjust for dividends, rights or small demergers, and 409 implausible one-day jumps had to be neutralised. Yahoo and broker APIs do not carry delisted names. One reconstruction, [BKKB20/nse-index-history](https://github.com/BKKB20/nse-index-history), is unusable: its "2004" Nifty 100 contains companies that listed a decade later.

Measured directly on that data [computed], using today's list instead of point-in-time membership added **7.7 points a year to an equal-weight Nifty 50 portfolio over 2011–2026** (16.4% against 8.7%) and **9.1 points to an equal-weight Nifty 100 since June 2013** (21.2% against 12.1% for NSE's official equal-weight index). For momentum the inflation was larger: a top-15 quarterly rule returned 20.4% on today's Nifty 50 list and **10.3% on point-in-time membership**. On honest membership the same rule beat simple equal weighting by −0.4 to +1.9 points a year, not the 5–7 points the reader's control suggested. The cause is index churn: 24 of the 50 Nifty members of January 2011 have since left, and those 24 had a median return of −0.1% a year. Published estimates are far smaller, at 4.94 points for Indian small caps ([Ranse, arXiv](https://arxiv.org/abs/2603.19380)), and the commonly quoted US fund figure of about 1 point is [recalled]. The momentum test used point-in-time Nifty 50 membership, not Nifty 100, which remains to be built.

### No account size from ₹1 lakh to ₹20 lakh makes 15 stocks beat the fund

At the same gross return, a momentum fund beats a self-run 15-stock book by roughly **2–4 points a year at ₹1 lakh, 1.5–3 at ₹5 lakh and 0.5–2.5 at ₹20 lakh** [computed from the Groww tariff and tax rules]. Fixed charges explain the small-account gap: quarterly turnover of 120–170% costs 1.1–1.6% a year at ₹1 lakh on Groww, 0.6–0.9% at ₹5 lakh and 0.45–0.65% at ₹20 lakh, and the ₹5,899 annual API fee adds 5.9%, 1.2% and 0.3%. Tax explains the rest and does not shrink with size. A fund rebalances its 100–135% annual churn without tax and the holder pays 12.5% only on exit, often nothing inside the ₹1.25 lakh exemption; the DIY investor pays 20.8% on most gains every year. The reader's own backtests showed that drag at 1.9–3.4 points a year.

So the question "at what capital does DIY win" has no answer in rupees. Fixed costs stop mattering by ₹10–20 lakh, but the DIY book then still needs **+1 to +3.5 points a year of gross return over the Momentum 30 index** to tie, and the evidence for that is absent: the index's own live edge over the Nifty 200 is +0.4 to +2.8, NSE found quarterly rebalancing worse than half-yearly (17.1% against 19.2% since 2005, backtested; [NSE whitepaper](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf)), and the point-in-time test shows 0–2 points. The fund's weaknesses are real, namely 0.5–1.0% a year of tracking difference and about ₹8,000 crore of one-way trading forced onto pre-announced dates ([Business Standard](https://www.business-standard.com/markets/news/nifty200-momentum30-a-flip-of-index-switch-jolts-16k-cr-across-the-grid-125121400388_1.html)) [summary]. It is the better vehicle for the same strategy, not a promise of the backtested return.

### A trend filter on momentum helps only if it follows the market, and tax eats part of it

New tests [computed, price indices, month-end check, cash at 6.5%] give a mixed answer. Switching the live Momentum 30 index to cash whenever the **Nifty 50** closed below its 200-day average raised the 2020–2026 return from 14.5% to 19.5% and cut the worst fall from 31.8% to 18.1%; after tax it was 16.8% against 13.0%. That is six years and nine switches, and the same rule **cost Alpha 50 about three points a year after tax over thirteen years** and cost a point-in-time momentum portfolio 1.6 points a year after tax over 2011–2026 while cutting its worst fall from 38.8% to 16.2%. Filtering on the momentum index's **own** 200-day average was worse in every test: 6.0% against 8.7% on Momentum 30 since July 2021, with a deeper drawdown. Tax adds 0.6–1.2 points a year to the cost of filtering, because each exit crystallises short-term gains and resets the holding clock. The filter's return benefit comes almost entirely from 2008, when it lifted the point-in-time portfolio from 11.3% to 20.4% a year over 2006–2010. It is insurance against a 60% fall, with a real premium.

## No live evidence shows an LLM adding return at this trading frequency

All findings here are [summary]. The positive academic results describe something Thunderbot cannot trade. Lopez-Lira and Tang's ChatGPT headline strategy shows a pre-cost Sharpe ratio above 3, but it is a daily long-short portfolio with roughly full turnover; at 25 basis points a trade its cumulative return collapses, the authors say it is feasible only for participants with very low costs "such as market makers", and returns have declined as LLM use spread ([arXiv 2304.07619](https://arxiv.org/abs/2304.07619)). Backtests over dates inside a model's training window prove nothing: models recall exact past values, and instructions to ignore later data do not prevent it ([Lopez-Lira, Tang and Zhu](https://arxiv.org/html/2504.14765v2)). When five well-known LLM trading agents were re-tested past the model cutoff, all dropped significantly ([Profit Mirage](https://arxiv.org/abs/2510.07920)), and a 2000–2024 re-evaluation found the reported advantages "often vanish" ([FINSABER](https://arxiv.org/html/2505.07078v3)).

Forward and live results are mostly unflattering. In StockBench, covering March to July 2025, most agents including GPT-5 failed to beat equal-weight buy-and-hold ([arXiv 2510.02209](https://arxiv.org/abs/2510.02209v1)); DeepFund found nine leading models made net losses on post-cutoff data ([arXiv 2505.11065](https://arxiv.org/abs/2505.11065)). In Alpha Arena's first season, **four of six frontier models lost between 31% and 63% of real money in 17 days** ([ForkLog](https://forklog.com/en/four-out-of-six-ai-models-suffer-losses-in-trading-tournament/)). The longest audited records trail a cheap index: the AI-run AIEQ ETF has lagged the S&P 500 since 2017 ([M1](https://pages.m1.com/invest/stocks/AIEQ)), the sentiment ETF BUZZ returned about 8.3% a year since March 2021 against 14.6% ([VanEck](https://www.vaneck.com/us/en/investments/social-sentiment-etf-buzz/performance/)), and the Eurekahedge AI hedge fund index earned 9.8% against 13.7% for the S&P 500 ([HedgeCo](https://www.hedgeco.net/news/?p=58736)). The positive exceptions are institutions with proprietary data and staff, such as Bridgewater's AIA fund at about 11% in 2025 ([Fortune](https://fortune.com/2026/01/02/top-hedge-fund-performers-2025-bridgewater-de-shaw-citadel-millennium/?rand=8593)), or short samples concentrated in a few stocks. The nuance on the other side is that purpose-built leak-free models achieve similar news-sentiment results, so look-ahead is not the whole story ([He et al.](https://arxiv.org/pdf/2502.21206v2)); the binding problem for retail is horizon and cost. The Indian sentiment studies found are small, correlational and untested after costs.

The LLM should therefore have no role in generating or approving signals. Three roles have reasonable support: offline review of code and backtests, which is how Man Group uses its research agent under line-by-line human inspection ([Man Group](https://www.man.com/insights/what-ai-can-do-for-alpha)); writing a plain-language log of each decision from the bot's own computed numbers; and, at most, a one-directional veto that can only defer a trade and alert the owner, placed after deterministic checks for splits, bad ticks and suspensions. Even that veto carries risk: injected text cut one simulated agent's return from 7.8% to 0.9% ([TradeTrap](https://arxiv.org/pdf/2512.02261)), and benchmarks show LLM agents are too conservative in rising markets, which is the failure mode of a veto on a trend system. A veto that fires three times a year cannot be validated on returns within a lifetime; by illustrative arithmetic it would take about 64 vetoes to detect a 2% average benefit. Judge it on verifiable precision instead, by recording whether each claimed anomaly was real, and pre-commit to removing it if false alarms exceed true ones after the first ten. Keeping the LLM out of order decisions also keeps the bot plainly "white box" under SEBI's retail algo framework, a point no source addressed directly.

## Supabase's free scheduler can wake a Python function inside the Vercel project

### Vercel's limits: Hobby runs the job but cannot schedule it

Plan limits are [summary] of Vercel's docs, which could not be opened; configuration shapes are [doc] from Vercel's public build tooling.

| Limit | Hobby | Pro |
|---|---|---|
| Cron jobs per project | 100 | 100 |
| Most frequent schedule | Once per day; a more frequent expression fails at deployment | Once per minute |
| Timing precision | Per-hour (±59 minutes) | Per-minute |
| Cron timezone and syntax | UTC only; numeric weekdays only | Same |
| Maximum function duration with Fluid compute | 300 s | 300 s default, configurable to 800 s |
| Maximum duration without Fluid compute (older projects) | 60 s | 300 s |
| Memory | 2 GB | 4 GB |
| Function regions | One | Several |
| Static outbound IP | Not available | $100 a month per project add-on, on shared addresses |
| Price | Free; "non-commercial personal use only" | $20 a month including $20 of usage credit (third-party summaries) |

Sources: [Cron usage and pricing](https://vercel.com/docs/cron-jobs/usage-and-pricing); [Functions limitations](https://vercel.com/docs/functions/limitations); [Configuring regions](https://vercel.com/docs/functions/configuring-functions/region); [Static IPs](https://vercel.com/docs/networking/static-ips); [Fair use guidelines](https://vercel.com/docs/limits/fair-use-guidelines). Fluid compute has been the default for projects created since 23 April 2025 ([changelog](https://vercel.com/changelog/fluid-compute-is-now-the-default-for-new-projects)).

Duration is not the constraint: a 10–120 second backtest fits in 300 seconds on either plan, provided Fluid compute is on. Scheduling is. **Hobby cannot wake the worker every few minutes and cannot promise 15:10**: a daily cron may fire up to 59 minutes off, and NSE closes at 10:00 UTC. Cron invocations are HTTP GET requests to the production deployment with the user agent `vercel-cron/1.0`, and are secured by a `CRON_SECRET` environment variable checked against the `Authorization` header ([Managing Cron Jobs](https://vercel.com/docs/cron-jobs/manage-cron-jobs)); the exact `Bearer` format, and the docs' statements that failed crons are not retried and may occasionally fire twice, are [recalled]. Vercel now calls Cron Jobs a legacy feature being migrated to "Schedules", in public beta, which adds an IANA `timezone` field and Python script targets that run in a private function ([Schedules](https://vercel.com/docs/schedules); [build-utils types](https://raw.githubusercontent.com/vercel/vercel/main/packages/build-utils/src/types.ts)); its Hobby frequency limits could not be confirmed. Hobby permits one function region, and a selectable region is consistent with the dashboard already running in Mumbai, though no doc line naming `bom1` for Hobby was seen. Whether a personal trading bot counts as "non-commercial" is a grey area Vercel has not settled.

### A Python function can sit beside the Next.js app, behind the same middleware

Vercel's builder explicitly expects this layout: its own warning text says JavaScript functions belong in Next.js, while "other languages (Python, Go, etc) should still go in the `api` directory" ([detect-builders.ts](https://raw.githubusercontent.com/vercel/vercel/main/packages/fs-detectors/src/detect-builders.ts)) [doc]. With the project's Root Directory set to `dashboard`, that folder is `dashboard/api/`. Both sets of routes share the `/api` prefix, and precedence for clashing paths could not be established, so the Python routes need their own prefix. Vercel's Next.js-plus-FastAPI template uses `/api/py/...` ([nextjs-fastapi](https://raw.githubusercontent.com/digitros/nextjs-fastapi/main/api/index.py)), which collides with none of the dashboard's six existing handlers. A valid Python entrypoint exports a top-level `app` or `handler`; Python 3.12 is the default and dependencies install from `requirements.txt` or `pyproject.toml` ([entrypoint.ts](https://raw.githubusercontent.com/vercel/vercel/main/packages/python/src/entrypoint.ts); [version.ts](https://raw.githubusercontent.com/vercel/vercel/main/packages/python/src/version.ts)). Python on Vercel was announced as generally available around mid-October 2026 ([changelog](https://vercel.com/changelog/python-on-vercel-is-now-generally-available)) [summary].

The dependencies fit. Installing the real wheels for yfinance, pandas, numpy and requests measured **168 MB unpacked** this session, with pandas at 45 MB, curl_cffi at 40 MB and numpy at 57 MB including its libraries. Vercel documents a 500 MB limit for Python functions, but its builder ships bundles up to **225 MB** as an ordinary zip and above that defers installing packages to every cold start ([dependency-externalizer.ts](https://raw.githubusercontent.com/vercel/vercel/main/packages/python/src/dependency-externalizer.ts)) [doc]. The Yahoo-only worker has about 55 MB of headroom; the `groww` and `llm` extras were not measured, and one attempt to resolve `growwapi` with the rest failed. Cold-start time for this stack was not measured anywhere.

The dashboard's middleware will block the scheduler as written. Its matcher covers every `/api/...` path and answers 401 to anything without Basic credentials (`dashboard/middleware.ts`). Next.js documents that middleware runs for "every route in your project" ahead of filesystem routes ([Next.js docs source](https://raw.githubusercontent.com/vercel/next.js/v15.5.0/docs/01-app/03-api-reference/03-file-conventions/middleware.mdx)) [doc]; that it also fronts non-Next `api/*.py` functions on Vercel is very likely but was not confirmed, so test it. The fix is the same either way: exclude the scheduler path from the matcher and make the Python handler verify a shared secret itself. An illustrative configuration, assembled from the schema and not deployed, is below; the `crons` block needs Pro and is unnecessary if Supabase does the scheduling.

```json
{
  "regions": ["bom1"],
  "functions": {
    "api/py/*.py": { "maxDuration": 300, "excludeFiles": "**/tests/**" }
  },
  "crons": [
    { "path": "/api/py/daily", "schedule": "40 9 * * 1-5" }
  ]
}
```

```ts
// dashboard/middleware.ts: exclude the scheduler path; the Python handler must check its own secret
export const config = {
  matcher: ["/((?!api/py/|_next/static|_next/image|favicon.ico).*)"],
};
```

Two pieces of real work remain. The worker lives in `worker/`, a sibling of the Root Directory, so it must reach the function as a path dependency, a build-time copy, or by moving the project to the repo root under Vercel's `services` configuration; none was verified end to end. And the worker's entry points are loops: the serverless wrapper should call `InvestRunner.tick()` once and `JobRunner.run_once()` once, against a Supabase-only store.

### Supabase: pg_cron, pg_net and Vault, with the official SQL

Everything here is [doc], read from the source files of Supabase's documentation on 10 November 2026. Supabase Cron is pg_cron inside the project's Postgres; jobs "can run anywhere from every second to once a year", schedules are in GMT, and Supabase recommends at most 8 concurrent jobs of at most 10 minutes each ([Cron](https://supabase.com/docs/guides/cron)). No file read restricts pg_cron, pg_net or Vault to paid plans and the pricing data has no line for them, so free-plan availability is very likely, but **no official sentence says "available on Free"**. Enable the extensions:

```sql
create extension pg_cron with schema pg_catalog;

grant usage on schema cron to postgres;
grant all privileges on all tables in schema cron to postgres;
```

```sql
create extension pg_net with schema "extensions";
```

pg_net queues an asynchronous HTTP request that is sent after the transaction commits ([pg_net](https://supabase.com/docs/guides/database/extensions/pg_net)). The official pattern for a scheduled call with its secret in Vault is ([Scheduling Edge Functions](https://supabase.com/docs/guides/functions/schedule-functions)):

```sql
select vault.create_secret('https://project-ref.supabase.co', 'project_url');
select vault.create_secret('YOUR_SUPABASE_SECRET_KEY', 'secret_key');
```

```sql
select
  cron.schedule(
    'invoke-function-every-minute',
    '* * * * *', -- every minute
    $$
    select
      net.http_post(
          url:= (select decrypted_secret from vault.decrypted_secrets where name = 'project_url') || '/functions/v1/function-name',
          headers:=jsonb_build_object(
            'Content-type', 'application/json',
            'apikey', (select decrypted_secret from vault.decrypted_secrets where name = 'secret_key')
          ),
          body:=concat('{"time": "', now(), '"}')::jsonb
      ) as request_id;
    $$
  );
```

The official template for calling out when a row is inserted, with the URL and key read from Vault, is ([Database Webhooks](https://supabase.com/docs/guides/database/webhooks)):

```sql
create function public.call_function_name()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  perform net.http_post(
    url := (select decrypted_secret from vault.decrypted_secrets where name = 'project_url') || '/functions/v1/function-name',
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'apikey', (select decrypted_secret from vault.decrypted_secrets where name = 'secret_key')
    ),
    body := jsonb_build_object(
      'type', tg_op,
      'table', tg_table_name,
      'schema', tg_table_schema,
      'record', to_jsonb(new),
      'old_record', null
    )
  );
  return new;
end;
$$;

create trigger call_function_name
after insert on public.my_table
for each row execute function public.call_function_name();
```

Run history is not cleaned automatically; the official cleanup job is:

```sql
select cron.schedule(
  'job-run-details-cleanup', -- name of the cron job
  '0 0 * * *', -- daily at midnight (GMT)
  $$ delete from cron.job_run_details where end_time < now() - interval '7 days' $$
);
```

For Thunderbot the adaptation is small and is **not from the docs**: store the Vercel endpoint URL and a long random bearer secret in Vault (the Supabase secret key is not needed for a call to Vercel), point `net.http_post` at them, and use UTC schedules. `40 9 * * 1-5` is 15:10 IST on weekdays; `*/5 3-10 * * 1-5` ticks every five minutes from 08:30 to 16:25 IST, with the worker ignoring ticks outside market hours and on NSE holidays, which cron cannot express. The existing `public.jobs` table is the natural target for the insert trigger.

Four behaviours shape the design. pg_net **does not retry**, and its queue lives in unlogged tables that do not survive a crash ([pg_net README](https://github.com/supabase/pg_net/blob/master/README.md)). Its default timeout is 2,000 ms in Supabase's docs and 5,000 ms upstream, so always pass `timeout_milliseconds` explicitly; upstream allows up to 600,000 ms. Responses are kept for six hours in `net._http_response`. And the decrypted secret sits briefly in `net.http_request_queue`, readable by any role that can log in to the database. Whether a Vercel function keeps running after pg_net times out and disconnects is [recalled] (it normally does) and must be tested. The safe pattern is to treat the insert trigger as a latency optimisation and let every periodic tick also sweep for jobs still marked `queued`.

### The free project still pauses, and scheduled activity may not prevent it

The docs are plain that "Supabase pauses Free Plan projects that show low activity over a 7-day period", that the test is "sufficient user database activity", and that "a few user requests to the database each day" is typically enough; paid projects are never paused ([Project Pausing](https://supabase.com/docs/guides/platform/free-project-pausing)) [doc]. A paused project can be restored for up to one year. **Supabase has not said whether pg_cron activity counts.** In a community thread summarised this session, a free-plan user received a pause warning on 5 November 2026 despite 87 successful keep-alive API calls that touched no table ([discussion #53090](https://github.com/orgs/supabase/discussions/53090)); an older thread reports that a daily insert, update and delete kept a project alive where a bare connection did not ([discussion #13121](https://github.com/orgs/supabase/discussions/13121)). Thunderbot's worker makes real reads and writes from outside on every tick, which is the pattern most likely to count, but weekends and holidays are the weak spot and the free plan gives no guarantee. If the project pauses, pg_cron stops with it, silently. The free plan also has no downloadable backups. For real money, Supabase Pro at $25 a month is the only guaranteed route ([plans data](https://github.com/supabase/supabase/blob/master/packages/shared-data/plans.ts)).

Edge Functions cannot host the strategy. They are TypeScript on a Deno-compatible runtime with 256 MB of memory, 2 seconds of CPU per request and a wall-clock limit of 150 seconds on Free and 400 seconds on paid plans; Free includes 500,000 invocations a month and Mumbai is a supported region ([Edge Functions limits](https://supabase.com/docs/guides/functions/limits)) [doc]. Supabase offers no static outbound address either: its IPv4 add-on is for inbound connections, and "the outbound IP address is not static and cannot be guaranteed" ([IPv4 address](https://supabase.com/docs/guides/platform/ipv4-address)).

## Yahoo from cloud addresses is unproven either way, so prices need a cache and a fallback

No live test of Yahoo, NSE or any vendor was possible: the research sandbox refused every market-data host, which says nothing about whether those services block cloud addresses. What follows rests on yfinance's code [doc] and its issue tracker, read through a summarising tool.

The v8 chart endpoint is still what yfinance 1.8.0, released 3 November 2026, uses for price history, and a comment in its code states the "chart API works without its cookie" ([history.py](https://github.com/ranaroussi/yfinance/blob/main/yfinance/scrapers/history.py); [data.py](https://github.com/ranaroussi/yfinance/blob/main/yfinance/data.py)). But "just a browser User-Agent" is no longer the whole story. Yahoo has returned HTTP 429 in waves since November 2024, sometimes to a single request with no prior volume; changing IP address did not help several users; and from spring 2025 browser impersonation through `curl_cffi` did, which points to client fingerprinting more than per-IP limits ([issue #2422](https://github.com/ranaroussi/yfinance/issues/2422); [issue #2518](https://github.com/ranaroussi/yfinance/issues/2518)). The evidence on cloud ranges specifically is one AWS Lambda report against one Google Colab counter-example. **Whether Vercel's Mumbai addresses are served reliably can only be settled by testing from the deployed function.** The repo's dependency floor of `yfinance>=0.2.54` predates the fingerprinting fix and should be pinned to a current release. Yahoo's NSE data also has documented defects, from the unadjusted 2019 NIFTYBEES split to an abrupt wrong price for Raymond in May 2025 ([yfinance issues](https://github.com/ranaroussi/yfinance/issues?q=is%3Aissue+NSE+OR+%22.NS%22+OR+NIFTYBEES+OR+BSE+OR+India+sort%3Acreated-desc)).

| Source | What is established | Cost | Status |
|---|---|---|---|
| NSE bhavcopy archive | Daily raw closes for every traded security; new file format since 8 July 2024; needs browser-like headers and throttling | Free | [doc] from library code; published after the close, so reconciliation only; cloud reachability untested |
| Upstox historical candles | Daily and intraday candle endpoints documented as "No authorization required" | Free | [doc] from the SDK docs; freshness, adjustment and reachability from Vercel untested |
| Groww data API | Live price, quotes and candles | ₹499 a month plus taxes | [summary] |
| Dhan data API | Daily and intraday history | ₹499 a month plus taxes | Earlier project research, not re-verified |
| Twelve Data | NSE not in the free tier | Paid plan, price not confirmed | [recalled] |
| EODHD | NSE symbols with `.NSE` suffix | About $19.99 a month | [recalled] |
| Alpha Vantage | 25 requests a day; Indian equities mainly as BSE symbols | Free tier | [recalled] |
| Stooq | Some Indian indices, little or no NSE ETF coverage | Free | [recalled] |

Sources: [jugaad-data archives.py](https://github.com/jugaad-py/jugaad-data/blob/master/jugaad_data/nse/archives.py); [upstox-python HistoryV3Api](https://github.com/upstox/upstox-python/blob/master/docs/HistoryV3Api.md). One cloud report suggests NSE filters on protocol and headers more than IP range: Python requests from AWS timed out while HTTP/2 `curl` from the same server worked ([NseIndiaApi issue #9](https://github.com/BennyThadikaran/NseIndiaApi/issues/9)).

The workload is tiny, which is the saving grace. Ten symbols need 10–25 requests a day if history is cached in a Supabase table and each run fetches only the latest bars; today the worker re-downloads full history into a local pickle a serverless function cannot keep. The robust layout is a primary source, a second source when the primary fails or its last bar is stale, a refusal to trade on any split-sized jump against stored history, nightly reconciliation against the exchange file where reachable, and a status row per run. Adjusted history from one source must never be mixed with raw closes from another.

## API orders need a broker-registered static IP; reads, signals and alerts do not

### The Groww Trade API today

The API costs **₹499 plus taxes a month, or ₹4,999 a year**, and normal per-order brokerage still applies ([Groww Trade API](https://groww.in/trade-api); [Chittorgarh, September 2026](https://www.chittorgarh.com/broker/groww/api-for-algo-trading-review/173/)) [summary]. Groww's blog also describes a ₹0 trial plan without live or historical data; whether it allows order placement was not confirmed ([Groww blog](https://groww.in/blog/api-trading-on-groww)). The Python SDK `growwapi` has been at version 1.5.0 since 6 December 2025 ([PyPI](https://pypi.org/project/growwapi/)) [doc].

Login has three flavours [summary of Groww's docs]: a token generated by hand, an API key plus secret that "requires daily approval" on Groww's site, and an API key plus TOTP. Reading the SDK settles the mechanics [doc]: every flow is one HTTPS POST to `/v1/token/api/access`, with either a six-digit TOTP code or a checksum of the secret and a timestamp, and the "checksum" flow is the daily-approval flow, not a third unattended option. **TOTP is the only unattended login**, and it is stateless, so a serverless function can mint the day's token itself. Access tokens expire at 06:00 IST daily ([Groww docs](https://groww.in/trade-api/docs/curl)). Documented rate limits are 10 a second and 250 a minute for orders and 20 a second and 500 a minute for other calls ([Groww docs](https://groww.in/trade-api/docs/python-sdk)) [summary]. The SDK has no sandbox host and no after-market-order flag, so the only end-to-end test is a very small real order and orders must be sent during market hours. The repo's assumed cap of 150 token requests a day appears only in a code comment.

### What SEBI's static-IP rule requires

All [summary]; the circular and NSE's FAQ could not be opened. The framework stems from SEBI's circular of 4 February 2025 and has applied to all brokers since **1 April 2026** ([SEBI circular, September 2025](https://www.sebi.gov.in/sebi_data/attachdocs/sep-2025/1759232056254.pdf); [Fyers](https://support.fyers.in/portal/en/kb/articles/what-are-the-new-sebi-rules-for-retail-algo-trading-from-april-01-2026)). No source found says it was relaxed afterwards. A client using the API must furnish a static IP "which may be changed no more than once per calendar week" ([NSE FAQ](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FAQ_Retail%20Algo_03112025_NSE.pdf)). Brokers offer **one primary and one optional secondary address**; Zerodha, Upstox and Dhan all document the weekly change limit ([Zerodha](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/static-ip); [Upstox](https://upstox.com/developer/api-documentation/announcements/static-ip-apis/); [Dhan](https://dhanhq.co/docs/v2/authentication/)). A self-built algo for one's own account needs exchange registration only above 10 orders a second, but Zerodha is explicit that the static IP is required "regardless of your order rate" ([Zerodha FAQs](https://support.zerodha.com/category/trading-and-markets/general-kite/kite-api/articles/kite-connect-api-faqs)). An address may be shared only with immediate family.

On Groww the addresses are entered on the API Keys page as a primary and a backup ([Groww guide](https://groww.in/blog/static-ip-api-trading-setup)), and orders from any other address "will be rejected by broker APIs" ([Groww on X](https://x.com/TradeWithGroww_/status/2038996435870621738)). Groww's own change-frequency limit was not found, so assume once a week. Third-party guides consistently report that the check applies to order endpoints while login, prices, holdings and order status work from any address ([brokerkit-groww](https://pypi.org/project/brokerkit-groww/); [FnOTrader](https://www.fnotrader.com/blog/static-ip-for-api-trading)); no exchange text confirming that was found.

### Fixed outgoing addresses without a server

| Option | Monthly cost | Is the address yours alone? | Evidence | Assessment |
|---|---|---|---|---|
| Owner places the order in the Groww app | Nil | Not needed | Rule applies to API orders only [summary] | Lowest risk; a few minutes a month |
| Groww Cloud (broker-hosted runtime) | Unknown | Not needed, per Groww's marketing | Marketing claim only | The most valuable thing to verify next |
| Home broadband static IP | Roughly ₹100 to ₹1,000+ | Yes | Weak vendor blogs | A device must be on; confirm with the ISP that it is not behind carrier NAT |
| Scale-to-zero container with its own egress IP (Fly.io) | About $3.60 for the IP plus cents of compute | Appears so; not confirmed | [summary] | Closest to "no server"; Mumbai region availability unverified |
| Tiny VPS as a forward proxy | About $4–5 | Yes | [recalled] prices | It is a server, though a stateless one |
| Oracle Always Free VM | Nil | Yes, reserved IPv4 | [summary] and [recalled] | Always-on, capacity shortages, idle reclamation |
| Static-IP proxy service (QuotaGuard) | From $19; dedicated address only at about $219+ | Shared below the top tier | [summary], vendor's own pages | Shared address may be refused |
| Vercel Static IPs | $100 per project plus data transfer | No, shared across a small group of customers | [summary] | Poor value and wrong shape |

Sources: [Fly.io egress IPs](https://fly.io/docs/networking/egress-ips/); [QuotaGuard pricing](https://www.quotaguard.com/products/pricing); [Vercel networking](https://vercel.com/docs/networking); [Oracle Always Free](https://docs.oracle.com/en-us/iaas/Content/FreeTier/resourceref.htm). Indian resellers advertising "static IP for algo trading" from about ₹100 a month exist, on vendor claims only ([staticip.in](https://staticip.in/brokers/groww)).

Routing orders through a third-party address is acceptable in principle and unsafe in one specific form. Zerodha's FAQ says a static IP may come from "an ISP, a cloud provider (such as AWS or GCP), or a VPN/VPC service", so a proxy is not prohibited as such. The problem is sharing: the framework ties an address to one client or family, sharing outside the family "may lead to suspension", and a proxy vendor itself concedes that a shared address "can be rejected if another QuotaGuard customer has already registered it with the same broker" ([QuotaGuard](https://www.quotaguard.com/blog/kotak-neo-api-static-ip)). On security, a standard HTTPS forward proxy sees only the destination and timing, because TLS runs end to end with Groww; that protection vanishes with any product that asks for its own certificate to be installed or terminates TLS itself. On a shared address the IP check adds nothing against the service's other users, so security rests entirely on the API key and TOTP secret. Only a dedicated address should be registered, with a second address from a different provider in the backup slot, because a failed proxy cannot be swapped for a week. Groww's API terms were not read.

## Cloud Scheduler is the most punctual free fallback and a sleeping laptop the least

Vendor facts here are [summary] unless marked; pricing pages for GitHub, Google and Oracle could not be opened.

| Option | Cost for a 2-minute daily job | Fixed outgoing IP | Timing and reliability |
|---|---|---|---|
| GitHub Actions schedule | Free on public repos; about 44 of 2,000 included minutes on a private repo | No | Weak: officially "can be delayed" and jobs "may be dropped" under load; public-repo schedules disabled after 60 days of inactivity |
| Cloud Run job plus Cloud Scheduler | Free within the allowance; card required | No; about $32 a month through Cloud NAT | Strong: native `Asia/Kolkata` schedules with retries; 3 free scheduler jobs |
| Oracle Always Free VM | Free; card required | Yes | Exact, but an always-on server with reclamation risk |
| Cloudflare Python Workers | Free plan unusable: 10 ms CPU per run; paid plan about $5 [recalled] | No [recalled] | Cron is fine; pandas is not on the free plan |
| Modal | Free within $30 a month of credits | No on the free plan | Good; Python-native cron |
| cron-job.org or Upstash QStash calling the Vercel function | Free | Not applicable | Good: one-minute granularity; cron-job.org times out near 30 s, QStash waits up to 15 minutes and retries |

Sources: [GitHub docs](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows); [Cloud Run scheduling](https://docs.cloud.google.com/run/docs/execute/jobs-on-schedule); [Cloudflare limits](https://developers.cloudflare.com/workers/platform/limits/); [Modal](https://modal.com/docs/guide/proxy-ips); [QStash pricing](https://upstash.com/pricing/qstash.md); [cron-job.org FAQ](https://cron-job.org/faq/). For a watchdog, healthchecks.io's free tier alerts when an expected ping does not arrive ([toolradar](https://toolradar.com/tools/healthchecks-io/pricing)).

On a laptop, the scheduler is easy and the wake is not. The templates below were assembled from documented options and **not executed**. Linux is the most capable: a system-level systemd timer accepts an IANA timezone, catches up missed runs and can wake from suspend, though not from power-off ([systemd.time](https://www.freedesktop.org/software/systemd/man/latest/systemd.time.html); [systemd.timer](https://manpages.debian.org/systemd.timer)).

```ini
# /etc/systemd/system/thunderbot.timer (system unit, so WakeSystem has the needed privilege)
[Timer]
OnCalendar=Mon..Fri *-*-* 15:10:00 Asia/Kolkata
Persistent=true
WakeSystem=true
AccuracySec=1s
```

On macOS, a LaunchAgent with `StartCalendarInterval` runs a job missed during sleep when the Mac wakes ([Apple](https://developer.apple.com/library/mac/documentation/MacOSX/Conceptual/BPSystemStartup/Chapters/ScheduledJobs.html)), and `pmset` can schedule the wake, but a 2026 developer-forum report says a lid-closed MacBook will not run the job until opened ([Apple Developer Forums](https://developer.apple.com/forums/thread/815034)).

```bash
sudo pmset repeat wakeorpoweron MTWRF 15:08:00   # wake two minutes early on weekdays
# LaunchAgent: StartCalendarInterval with Weekday 1-5, Hour 15, Minute 10; wrap the command in /usr/bin/caffeinate -i
```

On Windows, Task Scheduler can wake, catch up and retry, but wake timers are widely reported as unreliable on Modern Standby laptops, especially lid-closed or on battery ([Microsoft Q&A](https://learn.microsoft.com/en-us/answers/questions/1660115/regarding-waking-up-from-sleep-on-a-modern-standby); [Dell community](https://www.dell.com/community/Latitude/Wake-Timers-and-Task-Schedules-do-not-trigger-in-S0-Power-State/m-p/8310145)). The cmdlet syntax is [recalled].

```powershell
$trigger  = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday,Tuesday,Wednesday,Thursday,Friday -At 3:10PM
$settings = New-ScheduledTaskSettingsSet -WakeToRun -StartWhenAvailable -AllowStartIfOnBatteries `
            -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 2) -MultipleInstances IgnoreNew
```

A missed run is recoverable for this strategy because it decides monthly; what must be bullet-proof is not trading twice. Every trigger, whichever it is, should first claim a row keyed on strategy and IST trade date in Postgres and exit if another trigger already holds it. A run arriving before about 15:25 IST proceeds normally; a later one acts at the next session and logs the slip. Since the decision matters on about twelve days a year, a calendar reminder on the last trading day of each month plus a dead-man alert buys more reliability than any wake-timer tuning. India has no daylight saving, so 09:40 UTC is 15:10 IST all year.

## Recommendation: one rotation, one fund, one free scheduler, and a human finger on the order

### Strategy 1, the core: a four-sleeve trend rotation with a liquid-ETF cash leg

| Element | Rule |
|---|---|
| Instruments | NIFTYBEES, JUNIORBEES, MID150BEES, GOLDBEES; cash leg LIQUIDCASE (backup LIQUIDADD) |
| Target weights | 25% per sleeve |
| Signal | For each sleeve, the 200-day simple average of daily closes, including the decision day |
| Signal series | As backtested: Nifty 50 index, Nifty Next 50 index, the midcap index and the GOLDBEES price. Using each ETF's own split-adjusted close is simpler; choose one and freeze it before testing |
| Decision | Last trading day of each month, at 15:10 IST, from an NSE holiday table and not the calendar |
| Hold or park | A sleeve holds its ETF if its signal series is above its 200-day average; otherwise that 25% sits in LIQUIDCASE |
| Trading | Trade only when a sleeve switches, and once at the December month-end; touch an asset only if it is opened, closed, or more than 5 percentage points from target |
| Execution | Limit orders between 15:10 and 15:30 the same day; skip a buy priced more than about 0.5% above indicative NAV; refuse to act on a split-sized price jump |
| Activity | About 15–17 orders a year including the liquid ETF; in cash about 28% of the time |

This can be backtested from 2008 on free ETF prices for three sleeves and from 2011–2012 for midcaps. **Realistic range: about 6–9.5% a year after costs and tax, with a worst fall of 15–30%.** The upper end is the backtest itself (9.3% at month-end; 7.3–9.8% across 30 specifications). The lower end assumes gold stops helping (5.4–9.1% across specifications without gold), that the liquid ETF earns 5–5.5% and not 6%, and some of the decay every published trend rule has shown. The range is derived from one history and is not a promise.

The main risks are specific. Half or more of the edge is a gold bet that may not repeat. The Nifty signal was still out of the market on 30 October 2026 while the index rebounded about 10% into early November, and the rule will lag every V-shaped recovery in the same way. A different decision day produced a 31% fall in the backtest. Gold and liquid gains are taxed at slab rate. And a passive equal-weight mix of the same four ETFs, rebalanced each December, returned 11.7% after tax since 2011: an owner who can sit through a 27% fall, or the 49% of 2008, should hold that instead and needs no bot. The bot should paper-track that mix as its benchmark and the three-sleeve Nifty 50, Next 50 and gold variant as a cross-check built wholly on real ETF data.

### Strategy 2, the optional satellite: momentum through a fund

| Element | Rule |
|---|---|
| Instrument | A Nifty200 Momentum 30 fund. Inside the bot: MOM30IETF with limit orders, for orders up to about ₹5 lakh. Outside the bot: UTI's index fund, direct plan, which is larger and tracks more tightly |
| Base rule | Buy and hold; no stock picking and no quarterly re-ranking by the owner |
| Optional filter | At month-end, if the Nifty 50 closes below its own 200-day average, move the sleeve to LIQUIDCASE; return when it closes above. Never use the momentum index's own average |
| Size | A minority of capital, and only for money that can sit through a 30% fall and two to six years of lagging the market |
| Retire | The 15-stock rotation, unless a rebuild on point-in-time Nifty 100 membership shows it beating the Momentum 30 index by 1–3.5 points a year before costs |

**Realistic range without the filter: about 8–13% a year after costs and tax over a long holding period, with falls of about 30% in an ordinary correction and 65–70% in a 2008-type crash.** That is the market's return plus the live premium of roughly 0–2.5 points, less 0.5–1.0 points of fund cost and exit tax; the fund's five-year return to mid-September 2026 was 8.7% a year ([Univest](https://univest.in/blogs/uti-nifty200-momentum-30-index-fund-direct-growth-review-2026)) [summary]. With the Nifty 50 filter, expect a worst fall nearer 16–34% and give up roughly 0–2 points a year before tax and a further 0.6–1.2 in tax outside a crash. The combination of the two strategies was not tested.

### The no-server setup

Run the dashboard and a Python function in one Vercel project, with the function under `dashboard/api/py/`, the middleware matcher excluding that prefix, and the handler checking a bearer secret. Let Supabase do the scheduling: pg_cron fires `40 9 * * 1-5` for the decision, a five-minute tick sweeps queued backtests, and an insert trigger on `public.jobs` makes dashboard backtests start promptly, all through pg_net with the secret in Vault and an explicit timeout. Replace the SQLite-first store with a Supabase-only one, cache prices in a Supabase table, claim an idempotency row before acting, and ping an external dead-man check on every run including no-ops. On a rebalance day the bot sends the exact sells and buys with limit prices at about 15:05; the owner places them in the Groww app; after 15:30 the bot mints a TOTP token, reads holdings and the order book, and confirms the portfolio matches.

The limits that shape it are few. Vercel Hobby's own cron is useless for this job, which is why Supabase or a free external pinger schedules it. Functions get 300 seconds only with Fluid compute. The Python bundle must stay under 225 MB to avoid slow cold starts. pg_net does not retry, so the periodic tick must double as a sweeper. A free Supabase project can pause after a quiet week and takes pg_cron down with it, so paper trading can run free but real money justifies Supabase Pro at $25 a month, and Vercel Pro at $20 removes the fair-use question. Keep one fallback scheduler outside both vendors: Cloud Scheduler if punctuality matters, GitHub Actions if not.

**What stays impossible without a registered static IP:** placing, modifying or cancelling Groww orders through the API, and by assumption API-created GTT and OCO orders, from Vercel on any plan without the add-on, from Supabase, from GitHub runners, or from a home connection with a changing address. Everything else works: signals, paper trading, price fetching, token minting, reading holdings and order status as third parties report, writing to Supabase and sending alerts. If full automation is wanted later, the order of preference is Groww Cloud if it proves real, then a home static IP, then a dedicated egress address on a scale-to-zero container or small VPS, with a second address registered as backup. Never a shared address.

## What could not be confirmed

| Item | Status on 10 November 2026 |
|---|---|
| Whether Yahoo serves Vercel's Mumbai addresses reliably | Untested; no market-data host was reachable. Test from the deployed function |
| Whether Yahoo's NIFTYBEES and GOLDBEES history is split-adjusted | Untested; the project's own notes say NIFTYBEES was not |
| Vercel plan limits, cron retry and duplicate behaviour, `CRON_SECRET` header format, Schedules limits, `bom1` on Hobby | Docs not opened; limits are search summaries, the rest recalled |
| Whether Next.js middleware fronts `api/*.py` functions; how `worker/` outside the Root Directory reaches the build | Very likely and unverified respectively; test both |
| An official statement that pg_cron, pg_net and Vault are available on Supabase Free; whether pg_cron activity prevents pausing | Not stated in the docs read; Supabase has not answered |
| Groww: order placement on the ₹0 plan, IP change frequency, token-request cap, reference-id idempotency, IPv6 whitelisting, what Groww Cloud is | Not found; groww.in was unreachable |
| SEBI circular and NSE FAQ wording; any circular after April 2026; that reads are exempt from the IP check | Not opened; broker and third-party summaries only |
| Tax section numbers under the Income-tax Act 2025; rebate against slab-rate fund gains | Secondary sources and inference; Act not read |
| Groww charges | Read directly on 23 October 2026; search summaries only today |
| Expense ratio, fund size, spread and tracking difference for JUNIORBEES, MID150BEES, GOLDBEES, SILVERBEES, gilt and overseas ETFs | Not sourced |
| Launch dates before 2005, and the LIQUIDADD-to-DSP mapping | Recalled |
| Overnight and liquid returns for 2008–2016; Next 50 and midcap index returns before 2012; long total-return index history | Recalled or unavailable |
| Operative date of SEBI's ETF price-band framework | Reported as 1 September 2026 with a possible extension |
| Overseas investment cap status | Confirmed binding to 18 July 2026 only |
| Fund TERs for UTI's momentum fund; tickers, costs and sizes for Midcap150 Momentum 50, Nifty500 Momentum 50 and Alpha 50 funds | Unresolved or not researched |
| Factor index data after 2 September 2026 (total return) and 26 October 2026 (price) | Not available |
| Weekend Investing, PrimeInvestor and Capitalmind rotation results; any live, after-tax Indian rotation record | Not researched or not found |
| Momentum on point-in-time Nifty 100 membership | Not run; the bias estimate rests on Nifty 50 membership |
| VPS, NAT gateway, data-vendor and home-broadband static-IP prices; Fly.io Mumbai region | Recalled or weak vendor blogs |
| Every laptop command and every adapted SQL or JSON snippet | Templates, not executed |
| All own backtests | Single runs on one history, unreviewed; synthetic midcap data before February 2011 |

## Conclusion

The research inverted the reader's starting questions. The idle-cash problem was already solved inside the backtest and only needed solving in the account; the search for a better timing rule ended at a passive four-ETF mix that beat every rule on return; and the momentum question turned out to be about tax wrappers, not stock selection. What a bot adds for this investor is therefore narrow and real: drawdown control, executed without emotion, at ETF costs low enough that the control is nearly free. Whether that is worth having depends on one honest answer from the owner about sitting through a 30–50% fall.

The hosting answer has the same shape. The always-on server was only ever needed for two things, a punctual clock and a fixed address, and a database cron supplies the first for free. The second is needed for about a dozen order days a year, which is too little to justify renting an address or trusting a shared one. The first engineering task is not a scheduler at all: it is to point the deployed function at Yahoo for a week and log what comes back, because that untested dependency, not any plan limit, is what would stop the 15:10 run.
