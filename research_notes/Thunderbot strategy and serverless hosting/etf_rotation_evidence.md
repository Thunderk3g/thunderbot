# Tactical ETF rotation / trend-following asset allocation: global and Indian evidence (as of 10 Nov 2026)

> **Read this first: research limits in this session.**
> - Only about 23 web searches ran before the session-wide search budget was exhausted. The last planned searches (Zakamulin, McLean & Pontiff, Weekend Investing, PrimeInvestor, Indian multi-asset funds, gold-by-year, tax on gold/liquid ETFs) never ran.
> - Direct page fetches were blocked by the session's network policy for every site tried (freefincal.com, concretumgroup.com, momentumlab.substack.com, ramakrishnavadlamudi.blogspot.com; niftyindices.com and amfiindia.com were already being refused with 403). So **no primary page was read in full**. Every "Cited Finding" below comes from a search-result summary of the linked page, not from reading the page. Treat exact figures as "as reported in search summary".
> - Where a number is only my recollection and was not retrieved this session, it sits under **Gaps** and is labelled **UNVERIFIED RECALL**. Do not publish those as sourced facts.
> - Baseline the reader already has (from this repo, not re-researched): month-end 200-DMA rule with 1% buffer on NIFTYBEES, 2011-2026, about 8.1% after-tax / 8.5% pre-tax CAGR, worst fall 15-17%, vs 9.5% and -36% for buy-and-hold — [Thunderbot backtests](../Evidence%20based%20NSE%20trading%20strategies/thunderbot_backtests.md).

---

## 1. Faber's "A Quantitative Approach to Tactical Asset Allocation" / GTAA: original backtest vs out-of-sample and live funds

### Takeaway
Out of sample, Faber's rule has kept its drawdown-cutting property but its return roughly halved: about 6% a year for 2006-Mar 2025 (one vendor's replication) against about 10.5-11.7% in the pre-publication backtest. The live funds that tried to run it for real did worse than the paper: the original Cambria-run GTAA ETF lost its sub-advisor in 2014 and was liquidated in 2017, and Cambria's successor trend/momentum fund (GMOM) has compounded at roughly 3.5-5.7% a year since 2014 with a 25% drawdown.

### Cited Findings

**A. Pre-publication backtest (in-sample; no tax; hypothetical)**

| Item | Return | Worst drawdown | Period | Costs / tax | Type | Source |
|---|---|---|---|---|---|---|
| GTAA 5-asset timing (10-month SMA; US stocks, foreign stocks, bonds, REITs, commodities) | CAGR 11.7%, Sharpe 0.81 | 9.5% (monthly observations, so true intra-month drawdown was deeper) | 1972-2005 | Not stated in summary; tax not included | Backtest (as summarised by a vendor) | [Concretum Group](https://concretumgroup.com/global-tactical-asset-allocation/) |
| GTAA5, 2013 paper update | CAGR 10.5% vs 9.0% buy-and-hold; vol 7.0% vs 10.0%; Sharpe 0.79 vs 0.45 | -12% vs -45% | 1973-2012 | Not stated; tax not included | Backtest (third-party summary; figures differ slightly from other summaries) | [EdgeTools GTAA5 page](https://edgetools.pages.dev/portfolio-models/gtaa5-live) |
| Same update, different summary | Volatility cut to single digits | Buy-and-hold drawdown of about 46% cut to under 10% | 1973-2012 | Not stated | Backtest | [Transvaal-Titian blog summary of the 2013 update](https://transvaal-titian.blogspot.com/2013/06/qtaa-update-global-tactical-510-mebane.html) |
| GTAA yearly record in paper | Exactly one negative year, -0.59% in 2008 | — | 1973-2012 | — | Backtest | [MoneySense, "The failed promise of market timing"](https://www.moneysense.ca/columns/the-failed-promise-of-market-timing) |
| S&P 500 alone with 10-month SMA | Sharpe rises from 0.32 to 0.55; in market about 70% of the time | 1930s drawdown cut from 83.7% to 42.2% | 1901-2012 | Not stated | Backtest | [Transvaal-Titian blog](https://transvaal-titian.blogspot.com/2013/06/qtaa-update-global-tactical-510-mebane.html) |

- The original paper itself says the timing system underperformed the index in roughly half of all years since 1900; the edge comes from avoiding a few big bear markets, not from winning most years. — [Faber paper copy (SSRN id 962461 on Scribd)](https://www.scribd.com/doc/116881446/SSRN-id962461)
- The search summaries disagree on the buy-and-hold comparator (9.0% vs figures nearer 9.9%) and on the timing drawdown (-9.5% vs -12%). I could not open the paper to settle it. — [EdgeTools](https://edgetools.pages.dev/portfolio-models/gtaa5-live); [Concretum](https://concretumgroup.com/global-tactical-asset-allocation/)

**B. Post-publication, out-of-sample replications (still simulated, not live money)**

| Item | Return | Worst drawdown | Period | Costs / tax | Type | Source |
|---|---|---|---|---|---|---|
| Same rule, same five assets, 200-day SMA, month-end rebalancing, "no parameter tuning" | CAGR 6.05%, Sharpe 0.68 | 11.7% | Jan 2006 - Mar 2025 | Not confirmed in summary; no tax | Out-of-sample simulation by a vendor that sells implementation tools | [Concretum Group](https://concretumgroup.com/global-tactical-asset-allocation/); [Concretum Substack](https://concretumgroup.substack.com/p/global-tactical-asset-allocation) |
| Faber's own 2013 update | "Similar results" in 2006-2012 to the long history | under 10% (long-run) | 2006-2012 out-of-sample portion | Not stated | Author's own out-of-sample check | [Transvaal-Titian blog](https://transvaal-titian.blogspot.com/2013/06/qtaa-update-global-tactical-510-mebane.html) |
| Faber's 10-year revisit (2017 paper, discussed on his podcast ep. 86) | Abstract claims the model "performed well in real-time", with "equity-like returns with bond-like volatility and drawdowns"; numbers not retrieved | Not retrieved | 11 years after the original data cutoff | Not retrieved | Author's own review | [Meb Faber Show ep. 86](https://mebfaber.libsyn.com/ep86-meb-faber) |
| Hobbyist replication | CAGR 4.5%, Sharpe 0.66 | 8.1% | roughly a decade (exact dates not in summary) | Unknown | Forum backtest, low reliability | [QuantConnect forum](https://www.quantconnect.com/forum/discussion/8285/a-quantitative-approach-to-tactical-asset-allocation-gtaa-5-with-simplemovingaverage/) |

- Concretum itself notes that out-of-sample returns came in below the in-sample period "which is expected". — [Concretum Group](https://concretumgroup.com/global-tactical-asset-allocation/)
- The out-of-sample 6.05% is for a five-asset global portfolio in USD. The search did not return the matching buy-and-hold five-asset figure or the S&P 500 figure for 2006-2025, so "beat or lagged buy-and-hold" cannot be stated from what was retrieved. — [Concretum Group](https://concretumgroup.com/global-tactical-asset-allocation/)
- An independent analysis surfaced in search argues the original backtest "may have oversold the strategy's results in terms of what we can expect going forward" because the sample period was unusually favourable (attribution from search summary; most likely this piece). — [Capital Spectator, "Have You Stress-Tested Your Portfolio Strategy?"](https://capitalspectator.com/?p=7974)
- Academics (Marmi, Pacati, Renò, Risso) examined whether Faber's result is a counterexample to market efficiency; their conclusion was not retrieved. — [CORE copy of the paper](https://core.ac.uk/download/18510012.pdf)

**C. Live funds (real money, after fees)**

| Fund | Return | Worst drawdown | Period | Costs / tax | Type | Source |
|---|---|---|---|---|---|---|
| AdvisorShares Cambria Global Tactical ETF (ticker GTAA), Cambria as sub-advisor | Not retrieved | Not retrieved | Launched 2010; Cambria and AdvisorShares parted ways June 2014; Morgan Creek (Mark Yusko) took over | Net of fund fees | Live | [ETF Trends, June 2014](https://www.etftrends.com/2014/06/advisorshares-cambria-part-ways-on-tactical-etf/) |
| Same fund after the change | Liquidated; last trading day 12 May 2017. AdvisorShares' CEO referred to "the challenge of assuming its prior track record" | — | 2014-2017 | Net | Live; fund closed | [ETF Trends, May 2017](https://www.etftrends.com/2017/05/advisorshares-to-close-active-etfs-give-gtaa/); [StreetInsider press release](https://www.streetinsider.com/Press+Releases/AdvisorShares+Announces+ETF+Closures/12840304.html) |
| Cambria Global Momentum ETF (GMOM), Faber's successor trend/momentum fund | 5.69% a year since inception (88.05% cumulative) at NAV | 25.02% (trough 19 Mar 2020) | 4 Nov 2014 - 31 Mar 2026 | Net of fees; before investor tax | Live | [Cambria GMOM fact sheet](https://www.cambriafunds.com/assets/docs/GMOM-FactSheet.pdf); drawdown from [PortfoliosLab GMOM](https://portfolioslab.com/symbol/GMOM) |
| GMOM, earlier end date | 3.45% a year | about 25.0% | 4 Nov 2014 - 15 Apr 2025 | Net | Live | [MyPlanIQ GMOM](https://myplaniq.com/invest/quote/GMOM) |
| GMOM vs S&P 500, 10 years | 3.52% a year vs 11.24% for the S&P 500 | GMOM -25.03% vs -34.24% for Vanguard Total World (VT) | 10 years to about late 2025 | Net | Live | [PortfoliosLab GMOM](https://portfolioslab.com/symbol/GMOM); [PortfoliosLab GMOM vs VT](https://portfolioslab.com/tools/stock-comparison/GMOM/VT) |

- Conflict: another GMOM page shows a 10-year annualised NAV return of 0.50% with no clear date; it clashes with the 3.52% figure and should be ignored unless verified. — [PortfoliosLab GMOM](https://portfolioslab.com/symbol/GMOM)
- The 5.69% (to Mar 2026) vs 3.45% (to Apr 2025) gap shows how much one good year (2025-26, when gold and non-US assets trended) moves a "since inception" number for a trend fund. — [Cambria GMOM fact sheet](https://www.cambriafunds.com/assets/docs/GMOM-FactSheet.pdf); [MyPlanIQ GMOM](https://myplaniq.com/invest/quote/GMOM)
- Wider evidence on real tactical funds: a study of actual tactical allocation mutual funds over 1994-2016 found they underperformed all benchmarks and had negative alpha. — ["Is Tactical Allocation a Winning Strategy?" (practical applications summary)](https://aquila.usm.edu/fac_pubs/20187)
- A thesis testing tactical allocation "in a real-life setting" found performance poorer than in the back-test (attribution from search summary; one of these two documents). — [Erasmus University repository](https://repub.eur.nl/pub/85973); [CORE document](https://core.ac.uk/download/225890416.pdf)
- Positive counterpoint, vendor's own claim: Allocate Smartly says the tactical strategies it tracks outperformed 60/40 through 2025 and into early 2026. This is a model-tracking service's statement about simulated strategy tracking, not audited fund results. — [Allocate Smartly blog via Pulse aggregator](https://www.pulse.bot/publishers/allocate-smartly-blog/)

### Inferences
- The honest summary of Faber's rule after 20 years: **drawdown control held (about 12% vs the paper's 10%), return did not (about 6% vs 10-12%)**. Part of the return fall is the asset mix (commodities, foreign stocks and bonds earned little in 2009-2021), not the timing rule itself.
- Live results are worse than replications. GMOM's 25% drawdown is more than double the paper's worst case, and its 10-year return was about a third of the S&P 500's. The original GTAA ETF did not survive. A retail investor should plan on the live numbers, not the paper's.
- The comparison that matters to the reader is the same one already seen on Nifty: trend rules have been a **risk-reduction tool that costs return in long bull markets**, not a return enhancer.

### Gaps
- Exact tables from Faber's 2007 paper, 2013 update and 2017 revisit were not opened. **UNVERIFIED RECALL** (do not publish as sourced): the 2013 update's headline table is, to my memory, buy-and-hold 9.92% CAGR / -46.0% max drawdown vs GTAA 10.48% / -9.54% for 1973-2012. A search with those figures confirmed only "46% to less than 10%".
- Live return of the AdvisorShares Cambria GTAA ETF for 2010-2014 was not found. **UNVERIFIED RECALL**: it was roughly flat to low-single-digit a year while global equities rose strongly, which is the subject of the [Canadian Couch Potato article "The failed promise of market timing" (Dec 2013)](https://canadiancouchpotato.com/2013/12/30/the-failed-promise-of-market-timing/); that article's live numbers were not retrieved.
- Buy-and-hold comparators for Concretum's 2006-2025 window were not retrieved.
- Allocate Smartly's own out-of-sample-vs-backtest study and Cambria Trinity (TRTY) live record were not retrieved.

---

## 2. Antonacci's dual momentum (GEM): original backtest vs performance since the 2014 book

### Takeaway
The book's backtest showed about 17.4% a year with a 17-23% worst drawdown for 1974-2013; after publication, the only quantified test retrieved says returns fell to about a third of the pre-publication level through March 2023, with a drawdown as deep as the S&P 500's. Independent reviewers also found the published 12-month lookback was a lucky pick among more than a thousand equally reasonable variants.

### Cited Findings

**A. Pre-publication backtest (hypothetical, gross)**

| Item | Return | Worst drawdown | Period | Costs / tax | Type | Source |
|---|---|---|---|---|---|---|
| GEM (12-month relative momentum between US and non-US stocks; absolute momentum vs T-bills; else aggregate bonds; monthly) | 17.43% average annual vs 9.55% for MSCI ACWI; SD 12.64%; Sharpe 0.87 | 22.7% | 1974-2013 | **Gross returns**, monthly rebalancing; no tax | Backtest by the author | [CXO Advisory notes on the book](https://cxoadvisory.com/momentum-investing/a-few-notes-on-dual-momentum-investing); [A Wealth of Common Sense review](https://awealthofcommonsense.com/?p=9726) |
| GEM, extended window | 17.36% average annual; Sharpe 0.89 | -17.84% | Jan 1974 - Oct 2015 | Gross | Backtest by the author | [Seeking Alpha, "Bring More Data"](https://seekingalpha.com/article/3708296-bring-more-data) |
| GEM extended backwards | About 440 bps a year over the S&P 500 | Not retrieved | 1950-2018 | Gross | Backtest by the author | [Antonacci, "Extended Backtest of Global Equities Momentum"](https://www.hvst.com/posts/extended-backtest-of-global-equities-momentum-X34TPYzQ) |

- Conflict: the 1974-2013 drawdown is given as 22.7% and the 1974-2015 drawdown as 17.84%; a longer window cannot have a smaller maximum drawdown unless the method or data changed. Unresolved. — [CXO Advisory](https://cxoadvisory.com/momentum-investing/a-few-notes-on-dual-momentum-investing); [Seeking Alpha](https://seekingalpha.com/article/3708296-bring-more-data)
- Antonacci himself says the gains come mainly from avoiding bear-market losses, that outperformance in bull markets is much smaller, and that the model "will have periods of underperformance". — [CXO Advisory](https://cxoadvisory.com/momentum-investing/a-few-notes-on-dual-momentum-investing); [Antonacci, "Why Does Dual Momentum Outperform?"](https://seekingalpha.com/article/3768586-why-does-dual-momentum-outperform)

**B. Post-publication / out-of-sample**

| Item | Return | Worst drawdown | Period | Costs / tax | Type | Source |
|---|---|---|---|---|---|---|
| Dual momentum, pre-publication reference window | CAGR 7.2%, Sharpe 0.43 (SPY: 6.4%, 0.26) | -26.1% (SPY -51.9%) | Jan 2008 - Dec 2013 | Not stated | Backtest by a critic | [Price Action Lab](https://priceactionlab.com/Blog/?p=68274) |
| Dual momentum, post-publication | Annualised return "about a third" of the pre-publication figure (so roughly 2-3% a year by that author's numbers) | "Matched that of the SPY ETF" | 4 Jan 2014 - 9 Mar 2023 | Not stated | Out-of-sample simulation by a critic (vendor blog) | [Price Action Lab](https://priceactionlab.com/Blog/?p=68274) |
| ReSolve "Craftsman's Perspective": original spec vs 1,226 alternative specifications | Original spec "regressed to the median" out of sample; the family as a whole stayed attractive | Large dispersion in calendar-year returns across specifications | Out-of-sample windows 1950-1973 and 2012-2018 | Hypothetical, simulated | Out-of-sample study by a vendor | [Advisor Perspectives / ReSolve, May 2019](https://www.advisorperspectives.com/articles/2019/05/06/global-equity-momentum-a-craftsmans-perspective) |
| ETF-only implementation (different variant) | CAGR 7.6% | Not retrieved | 2000-2020 | Unknown | Backtest | [wikifolio](https://www.wikifolio.com/de/de/w/wf02020mms) |

- Price Action Lab's conclusion: the wide gap between pre- and post-publication performance "is an indication that the strategy was the outcome of data mining and selection bias", with regime change as a second cause. — [Price Action Lab](https://priceactionlab.com/Blog/?p=68274)
- Newfound Research: GEM is fragile to specification. A 9-month and a 10-month lookback, conceptually near-identical, produced very different cumulative returns over the same period (one returned just 43.1%); a 10-month version whipsawed in 2011. "Trend following strategies will always incur some sort of whipsaw risk." — [Newfound Research, GEM posts](https://blog.thinknewfound.com/tag/gem/)
- TuringTrader's review of the strategy: it "provided only little benefits in late 2018 or spring 2020" and missed the quick rebounds. — [TuringTrader](https://turingtrader-com.web.app/portfolios/antonacci-dual-momentum)
- March 2020 mechanics: the market fell 34% in 5 weeks and regained its peak in 5 months; classic GEM was out for 3-4 months and re-entered only after the absolute-momentum signal turned, after much of the rebound. — [Freenance (Polish-language explainer)](https://freenance.io/strategie/dual-momentum-gary-antonacci-2026-pl-strategia-momentum-relative-absolute-implementacja-przyklad/)
- One practitioner matched the published allocations in all but 3 of 540 months (1971-2015) and found the "official" rules move to bonds earlier but whipsaw slightly more than the simplified rule. — [Index Swing Trader blog](https://indexswingtrader.blogspot.sg/2016/10/prospecting-dual-momentum-with-gem.html)

### Inferences
- GEM is the closest global analogue to the reader's proposed rotation (pick the stronger of a few assets, fall back to a safe asset). Its history is a warning: **a backtest of 17% a year became low single digits after publication in the one quantified test found**, mainly through whipsaws around fast falls and fast recoveries (2015-16, late 2018, March 2020) and a bond "safe" leg that also fell in 2022.
- The ReSolve finding matters most for design: if the result depends on choosing 12 months rather than 9 or 10, the true expected edge is the average across reasonable lookbacks, not the best one.

### Gaps
- No year-by-year GEM returns for 2014-2025 were retrieved (optimalmomentum.com, Allocate Smartly, Dual Momentum Systems and Portfolio Charts were not reached). The Price Action Lab figure stops in March 2023 and is one critic's simulation; no independent replication of it was found.
- Alpha Architect's critique of GEM was not retrieved (only its 2014 book review URL surfaced: [Alpha Architect](https://alphaarchitect.com/?p=14414)).
- **UNVERIFIED RECALL**: GEM moved to bonds in 2022, when aggregate bonds also lost money, so the "safe" leg did not protect. Not confirmed this session.

---

## 3. AQR-style trend following: long-run evidence, the weak 2010s, live fund records, and negative academic evidence

### Takeaway
The long-run simulated evidence for trend following is strong (about 11% a year net over 1880-2013 in AQR's study), but that is a diversified long/short futures strategy across 60+ markets, not a long-only rotation among four Indian ETFs. The live record is lumpy: the main industry index has earned about 4.9% a year since 2000, with a poor 2011-2019, a 27% gain in 2022, its worst-ever 12-month loss (-18.7%) to April 2025, and a strong 2026 so far.

### Cited Findings

**A. Long-run research (simulated)**

| Item | Return | Worst drawdown | Period | Costs / tax | Type | Source |
|---|---|---|---|---|---|---|
| AQR, "A Century of Evidence on Trend-Following Investing" (time-series momentum, long/short, 67 markets) | 14.9% gross, 11.2% net a year; vol 9.7%; net Sharpe 0.77; near-zero correlation to stocks and bonds; positive in every decade | Not retrieved | Jan 1880 - Dec 2013 | Net of simulated transaction costs and hypothetical 2-and-20 fees; no tax | Backtest | [AQR](https://www.aqr.com/Insights/Research/Journal-Article/A-Century-of-Evidence-on-Trend-Following-Investing); [Alpha Architect / Swedroe](https://alphaarchitect.com/trend-following-is-everywhere/) |

- Sources disagree on the weakest decade in that study (5.7% net for the period starting 1910 vs 4.1% for the period starting 1919). — [ETF.com / Swedroe](https://www.etf.com/sections/index-investor-corner/swedroe-trend-following-works); [Alpha Architect](https://alphaarchitect.com/trend-following-is-everywhere/)
- AQR's explanation for the weak 2010s ("You Can't Always Trend When You Want"): the main cause was a lack of large risk-adjusted market moves, not a failure of trend rules to capture moves, and not reduced diversification. — [The Idea Farm summary](https://theideafarm.com/alternative-investment/you-cant-always-trend-when-you-want/); [Rivershedge blog quoting the paper](https://rivershedge.blogspot.com/2019/05/aqr-on-trend-not-being-dead-yet.html)

**B. Negative / mixed academic evidence**

- Huang, Li, Wang & Zhou, "Time series momentum: Is it there?" (Journal of Financial Economics, 2020), 55 futures, 1985-2015: asset-by-asset regressions show little time-series momentum in or out of sample; the pooled t-statistic fails bootstrap tests; the strategy is profitable, but "virtually the same" as a strategy based on the historical mean return that needs no predictability. "Overall, the evidence on TSM is weak." — [WUSTL publication page](https://profiles.wustl.edu/en/publications/time-series-momentum-is-it-there/); [CXO Advisory summary](https://www.cxoadvisory.com/momentum-investing/intrinsic-time-series-momentum-does-not-really-exist/)
- Alpha Architect's reading of that paper: the authors do not say there is no predictability, only that it is not as simple as a constant 12-month rule. — [Alpha Architect](https://alphaarchitect.com/are-trend-following-and-time-series-momentum-research-results-robust/)

**C. Live record of trend funds (real money, net of fees)**

| Item | Return | Worst drawdown | Period | Type | Source |
|---|---|---|---|---|---|
| SG Trend Index (10 largest trend CTAs) | 4.9% a year | — | Jan 2000 - May 2025 | Live index of funds | [Man Group, "Trend Following and Drawdowns: Is This Time Different?"](https://www.man.com/insights/is-this-time-different) (attribution from search summary) |
| SG Trend Index | +27% | — | 2022 | Live | [Man Group](https://www.man.com/insights/is-this-time-different) |
| SG Trend Index | About -18.7% over 12 months, the worst in the index's 25-year history | -18.7% (12-month) | 12 months to 30 Apr 2025 | Live | [Virtus AlphaSimplex via AdvisorAnalyst](https://advisoranalyst.com/?p=167192) |
| SG Trend Index | +2.39% | — | Calendar 2025 | Live | [Top Traders Unplugged, Dec 2025 report](https://www.toptradersunplugged.com/trend-following-performance-report-december-2025/) |
| SG Trend Index | +15.80% year to date | — | Jan - Sep 2026 | Live | [Top Traders Unplugged, Sep 2026 report](https://www.toptradersunplugged.com/trend-following-performance-report-september-2026/) |
| Trend index, 2014 | +19.7%, the last double-digit year before 2022 (index label ambiguous in the article) | — | 2014 | Live | [The Full FX](https://thefullfx.com/year-end-drop-fails-to-dampen-stellar-2022-for-trend-followers/) |
| SG CTA Index (broader) | +20.1%, best year since inception in 2000 | — | 2022 | Live | [Hedgeweek](https://www.hedgeweek.com/trend-followers-turn-leaders-ctas-deliver-record-returns-2022/) |
| AQR Managed Futures (AQMIX), launched 5 Jan 2010 | 2022: 16.95%; 2023: 2.08%; 2024: 8.13%; 2025: 14.62%; 2026 YTD: 9.72% | — | Calendar years | Live; **may be price-only, see conflict note** | [PortfoliosLab](https://portfolioslab.com/tools/stock-comparison/QNZIX/AQMIX); launch date from [AQR fund page](https://funds.aqr.com/funds/aqr-managed-futures-strategy-fund) |
| AQMIX trailing | 23.0% (1 yr), 11.7% a year (3 yr), 14.5% a year (5 yr) | — | To 31 Aug 2026 | Live | [AAII](https://www.aaii.com/fund/ticker/AQMIX) |

- Managed futures failed to hedge equities in 2011 and 2018; in 2011 and 2018 whipsawing markets left most SG Trend constituents negative for the year. — [Price Action Lab](https://priceactionlab.com/Blog/?p=79304); [Top Traders Unplugged](https://www.toptradersunplugged.com/trend-following-performance-report-december-2025/)
- Dispersion between trend managers is huge: the gap between the best and worst SG Trend constituent averages 26% a year. — [Meketa, "Trend Following Strategies", Dec 2025](https://meketa.com/wp-content/uploads/2025/12/MEKETA_Trend-Following.pdf)
- Conflict: AQMIX's 2022 figure of 16.95% looks too low against the SG Trend Index's +27% and may exclude the fund's large distributions. Verify against AQR's annual report before use. — [PortfoliosLab](https://portfolioslab.com/tools/stock-comparison/QNZIX/AQMIX)
- A Top Traders Unplugged report (April 2023) says the SG Trend Index has had "only 4" negative calendar years; this was not reconciled with the weak 2011-2018 stretch and should not be quoted without checking. — [Top Traders Unplugged](https://www.toptradersunplugged.com/trend-following-performance-report-april-2023/)

### Inferences
- AQR's century result does **not** transfer to the reader's plan. It needs dozens of markets, both long and short, with leverage and volatility targeting. A long-only switch among Nifty 50, Next 50, midcap and gold has two effective bets (Indian equity, gold), so it has far less diversification and no ability to profit from falls.
- Even professionals with 60+ markets had a lost decade (2011-2019) and a record drawdown in 2024-25. An Indian retail rotation should expect multi-year stretches of lagging buy-and-hold.
- The Huang et al. result is the strongest academic caution: much of the measured "trend" profit could be earned by simply holding assets with positive long-run returns. For a long-only rotation, that means most of the return will come from being invested in rising assets (beta), not from timing skill.

### Gaps
- Not searched (budget ran out): McLean & Pontiff, Zakamulin, Moskowitz-Ooi-Pedersen headline numbers, AQR "Trend Following: Why Now?" and AQR drawdown papers. **UNVERIFIED RECALL** (well-known results, but no URL retrieved this session): McLean & Pontiff (Journal of Finance, 2016) found anomaly returns about 26% lower out of sample and about 58% lower after publication across 97 predictors; Zakamulin's work on moving-average timing argues reported performance is overstated by data-mining and that out-of-sample gains are uneven and concentrated in a few bear markets.
- A full SG Trend calendar-year series for 2010-2024 was not retrieved (the Meketa PDF reportedly has the table). **UNVERIFIED RECALL**, approximate: 2011 -8%, 2012 -4%, 2013 +3%, 2014 +20%, 2015 0%, 2016 -6%, 2017 +2%, 2018 -8%, 2019 +9%, 2020 +6%, 2021 +6%, 2022 +27%, 2023 -4%, 2024 +3%.
- AQMIX calendar-year total returns for 2010-2021 were not retrieved.

---

## 4. Indian evidence and practitioner backtests

### Takeaway
Published Indian evidence for Nifty/gold rotation is thin and low-quality: a handful of blog and forum backtests showing 16-19% CAGR with 11-24% drawdowns over 2011-2024 windows, none with costs or tax, none live, and all covering a period that includes gold's strongest run. The more careful Indian voices retrieved (Freefincal; one 22-year 200-DMA test) say timing mainly reduces risk and does not reliably add return, and that backtests ignore tax and behaviour.

### Cited Findings

| Source / rule | Return | Worst drawdown | Period | Costs / tax | Type | Link |
|---|---|---|---|---|---|---|
| Momentum Lab: hold whichever of Nifty or gold has the higher 200-day return if it beats a fixed-deposit return, else FD | CAGR 18.79% (382.33% total) vs Nifty 12.13% (184.65%) and gold 10.86% (156.50%) | -11.42% vs Nifty -34.00% | 2014-2024 | No costs or tax reported; switch count not reported | Backtest (blog) | [Momentum Lab](https://momentumlab.substack.com/p/backtesting-dual-momentum-strategy) |
| Momentum Lab: 200-day EMA absolute momentum on NIFTYBEES alone | Not retrieved | -20.19% vs -36.34% buy-and-hold | 10 years | Not reported | Backtest (blog) | [Momentum Lab](https://momentumlab.substack.com/p/backtesting-dual-momentum-strategy) |
| Forum: dual momentum, NIFTYBEES vs GOLDBEES (ChatGPT-assisted) | CAGR 16.06% | -23.51% (quoted in a related post; may not be the same run) | about 14 years | Not reported | Backtest (forum, unaudited) | [MadeForTrade](https://madefortrade.in/t/dual-momentum-strategy-with-niftybees-goldbees/33205); [TradingQnA](https://tradingqna.com/t/dual-momentum-strategy-with-niftybees-goldbees/174470) |
| Shared Nifty-gold regime backtest: buy-and-hold legs only | Nifty about 214% absolute; gold about 161% absolute | Nifty about -38%; gold about -21% | about 2015-26 | Not reported | Backtest summary (aggregator) | [Multibagg](https://www.multibagg.ai/market-pulse/articles/nifty-gold-regime-backtest-buyhold-cmox4nfw9a1vymn0jn71nlb34) |
| Independent 22-year test: Nifty 50 above 200-DMA, else liquid fund | "Market timing using 200 DMA doesn't improve returns meaningfully, but it adds complexity and costs" (numbers not in summary) | Not retrieved | 22 years | Not confirmed | Backtest | [Free Float, "Tactical allocation"](https://freefloat.substack.com/p/tactical-allocation) or [MoneyWorks4Me](https://www.moneyworks4me.com/blog/time-the-market-or-asset-allocation) (attribution not confirmed) |
| Freefincal: 200-DMA rule on Nifty, tested while analysing IDFC Dynamic Equity Fund | "Seems to have comfortably beaten the Nifty" (numbers not in summary) | Not retrieved | Not retrieved | Freefincal's stated caveat: backtests "do not factor in future market movements, human emotions, taxation and exit loads" | Backtest | [Freefincal](https://freefincal.com/investment-strategy-analysis-idfc-dynamic-equity-fund/) |
| Freefincal: tactical buy/sell of gold vs cash using moving averages | Tactical gave a better return from the early 2000s on in rolling tests; "will not work all the time" | Not retrieved | Aug 1997 - May 2020 | Tax not included | Backtest | [Freefincal](https://freefincal.com/is-this-a-good-time-to-buy-gold/) |
| This repo's own test: month-end close above 200-DMA, Nifty 50 price index, 6.5% on cash, 0.1% per switch | 10.1% vs 10.0% buy-and-hold; 2015-Oct 2026: 7.3% vs 8.8% | -24.2% vs -45.4% | Jul 2008 - Oct 2026 | Costs yes, tax no | Own backtest | [Prior notes](../Evidence%20based%20NSE%20trading%20strategies/momentum_factor_evidence.md) |
| This repo's own test: 12-month absolute momentum on Nifty (the GEM-style signal) | 4.4% | -22.7% | Jul 2008 - Oct 2026 | Costs yes, tax no | Own backtest | [Prior notes](../Evidence%20based%20NSE%20trading%20strategies/momentum_factor_evidence.md) |

- Freefincal has a multi-part series and related posts that exist but could not be opened: "Tactical Asset Allocation Backtest Part 3: Short-Term Vs Long-Term", "Nifty Momentum Timing: Can it produce higher returns?", "Momentum index fund: Will tactical entry/exit give better results?". — [Part 3](https://freefincal.com/tactical-asset-allocation-backtest-part-3-short-term-vs-long-term/); [Nifty Momentum Timing](https://freefincal.com/?p=29305); [Momentum index tactical entry/exit](https://freefincal.com/momentum-index-fund-will-tactical-entry-exit-give-better-results/)
- Capitalmind: no public gold/Nifty rotation backtest with CAGR and drawdown was found. Its public material is stock-momentum factsheets; one (2021) reported a smallcase CAGR of about 60% while saying actual investor returns were likely nearer 46%, a useful example of the gap between model and realised returns. Capitalmind also has a 2024 gold/silver allocation article that was not opened. — [Capitalmind momentum factsheet, May 2021](https://premium.capitalmind.in/2021/06/cm-momentum-monthly-fact-sheet-may-2021/); [Capitalmind gold-silver allocation analysis 2024](https://www.capitalmind.in/insights/gold-silver-portfolio-allocation-analysis-2024)
- Other Indian items that surfaced by title only (not opened, no numbers): a ValuePickr thread "Momentum based ETF rotation - Amazing backtested results - Need Reviews"; a ValuePickr thread on volatility-adjusted momentum with a gold regime filter (2018-2026); "Indian Edition of the Dual Momentum Strategy with Nifty/Gold"; "The 200-DMA golden cross on Nifty: confirmed too late to matter". — [ValuePickr ETF rotation](https://forum.valuepickr.com/t/momentum-based-etf-rotation-amazing-backtested-results-need-reviews/2226); [ValuePickr gold regime filter](https://forum.valuepickr.com/t/backtesting-volatility-adjusted-momentum-with-a-gold-regime-filter-2018-2026/218153); [Samasthiti](https://samasthiti.substack.com/p/indian-edition-of-the-dual-momentum); [TFfinance](https://finance-platform-fawn-ten.vercel.app/projects/the-200-dma-golden-cross-on-nifty-confirmed-too-late-to-matter)
- Conflict: the Multibagg summary's gold return of about 161% for 2015-26 looks far too low for a window that includes 2025 and is close to Momentum Lab's 156.5% for 2014-2024; the window is probably mislabelled. Do not use it. — [Multibagg](https://www.multibagg.ai/market-pulse/articles/nifty-gold-regime-backtest-buyhold-cmox4nfw9a1vymn0jn71nlb34); [Momentum Lab](https://momentumlab.substack.com/p/backtesting-dual-momentum-strategy)

### Inferences
- **No Indian rotation result retrieved is live, audited, net of costs, or net of tax.** The 16-19% CAGR figures are upper bounds from favourable windows. On the reader's own cost and tax model, the plain 200-DMA rule lost about 0.4-1.4 points a year to costs and tax; a rotation with more switches and a gold leg taxed differently would lose more.
- The Momentum Lab result (18.8% vs 12.1%) relies on gold being a strong alternative whenever Nifty was weak in 2014-2024. Gold alone made only 10.9% a year in that window, so the excess came from switching at good moments in one decade: about 10 years, perhaps 15-25 switches. That is too few independent decisions to distinguish skill from luck.
- The repo's own finding that a 12-month absolute-momentum signal earned only 4.4% on Nifty (vs 10% buy-and-hold) shows slow GEM-style signals have failed on Indian equity specifically, because of the V-shaped 2009 and 2020 recoveries.

### Gaps
- **Not researched at all (search budget ran out, sites blocked):** Weekend Investing (Mi EverGreen, Mi ALLCAP GOLD, Mi India Top 10, HNI Wealth Builder, NNF10), PrimeInvestor, Stockopedia India, Zerodha Varsity, Marketfeed, ET Money Genius, smallcase "All Weather", and the live records of DSP, Edelweiss, ICICI Prudential and Quantum dynamic / multi-asset funds. No statement about any of these should be made from these notes.
- Freefincal's actual numbers (double moving average on Sensex, Nifty, Next 50, gold) were not retrieved. **UNVERIFIED RECALL**: Pattabiraman's recurring conclusion is that tactical allocation lowers risk and sometimes, not always, raises return, and that his backtests assume tax-free, load-free switches so real results would be worse.
- The independent 22-year 200-DMA test's source and numbers need confirming.
- Rule details (lookback, rebalance day, trade timing, use of ETF vs index data) for the forum backtests were not retrieved.

---

## 5. How much of any Indian rotation result is just gold's 2019-2026 bull run?

### Takeaway
I could not retrieve a sourced gold-by-year series, so this cannot be answered with cited figures. The sourced fragments point one way: over 2014-2024 gold on its own (10.9% a year) lagged Nifty (12.1%), so any rotation that beat both did so by switching into gold at the right times in 2019-2020, 2022 and 2024, and a backtest extended through 2025-26 will be flattered further by gold's very large recent gain.

### Cited Findings
- Over 2014-2024, buy-and-hold gold returned 156.50% (10.86% a year) and Nifty 184.65% (12.13% a year); the Nifty/gold dual-momentum rule returned 382.33% (18.79% a year). No costs or tax. — [Momentum Lab](https://momentumlab.substack.com/p/backtesting-dual-momentum-strategy)
- Gold on MCX was reported up about 49% over one year in a social-media-derived summary with no clear date window (unverified). — [Multibagg index-returns summary](https://www.multibagg.ai/market-pulse/articles/nifty-indices-one-year-returns-cmrl5lgvd01rkqt0jigwke0zs)
- In 2025 the Nifty 50 price index rose about 10.5% (23,645 to 26,130) and the Nifty Next 50 TRI returned +2.09%. — [Angel One, Nifty 50 vs Nifty Next 50 returns 2025](https://www.angelone.in/news/market-updates/nifty-50-vs-nifty-next-50-returns-2025-where-did-investors-make-more-money-malayalam)
- The same aggregator shows a later window (to June 2026) with Nifty 50 at -7.7%, consistent with the repo's note that Nifty spent a long streak below its 200-DMA in 2026. — [Multibagg](https://www.multibagg.ai/market-pulse/articles/nifty-indices-one-year-returns-cmrl5lgvd01rkqt0jigwke0zs); [prior notes](../Evidence%20based%20NSE%20trading%20strategies/momentum_factor_evidence.md)
- Trend funds globally had their weakest stretch through April 2025 and then recovered (+15.8% to Sep 2026), which coincides with the period when gold trended hard; live trend results everywhere are currently flattered by the same move. — [Top Traders Unplugged, Sep 2026](https://www.toptradersunplugged.com/trend-following-performance-report-september-2026/); [AdvisorAnalyst](https://advisoranalyst.com/?p=167192)
- A Freefincal-style table of "Nifty 50 TRI | Gilt fund | Gold" and a BasuNivesh "Nifty 50 vs Gold" comparison exist but could not be opened. — [Datawrapper table](https://datawrapper.dwcdn.net/WygcF/1); [BasuNivesh](https://www.basunivesh.com/nifty-50-vs-gold-which-is-the-best-investment/)

### Inferences
- A four-equity-plus-gold rotation has really two return engines: Indian equity beta (Nifty 50, Next 50 and midcap rise and fall together) and gold. When Indian equities are below trend, the only thing the rule can rotate into besides cash is gold. So **the rule's edge over the plain 200-DMA rule is, almost by construction, gold's return during Indian equity downtrends.**
- Any backtest whose window starts after about 2012 and ends in 2025-26 is dominated by one gold bull market. A fair test must show the result separately for a period when gold fell or went sideways in rupees (roughly 2012/13 to 2018). If the rotation only matches or lags the plain rule there, the "edge" is a gold bet.
- Test to ask of any published Indian rotation result: (a) what was the result with gold removed, (b) what was the result for 2013-2018 alone, (c) how many switches produced the excess.

### Gaps
- **The year-by-year arithmetic could not be sourced.** See the unverified table in section 6. Using that unverified table purely as an illustration: gold in rupees compounds to roughly +2% a year for 2012-2018 and roughly +22% a year for 2019-2025, against roughly 14-15% a year for Nifty 50 TRI in both halves. If those approximate figures are confirmed, essentially all of gold's contribution to any 2011-2026 rotation backtest comes from the second half. **This arithmetic rests on recalled numbers and must be re-done with verified data before publication.**
- World Gold Council INR return tables and Gold BeES NAV history were not reached.

---

## 6. Year-by-year calendar returns 2008-2025 (+2026 YTD): gold in INR, Nifty 50 TRI, Nifty Next 50 TRI, Nifty Midcap 150 TRI

### Takeaway
This table could not be built from sources in this session: niftyindices.com, AMFI and the one blog that publishes the exact table were unreachable, and searches returned only two 2025 data points. A recalled, approximate table is given under Gaps and is explicitly unverified.

### Cited Findings
- **2025, Nifty 50: about +10.5% (price return, not total return)**, from 23,645 to 26,130. — [Angel One](https://www.angelone.in/news/market-updates/nifty-50-vs-nifty-next-50-returns-2025-where-did-investors-make-more-money-malayalam)
- **2025, Nifty Next 50 TRI: +2.09% (total return).** — [Angel One](https://www.angelone.in/news/market-updates/nifty-50-vs-nifty-next-50-returns-2025-where-did-investors-make-more-money-malayalam)
- A blog post dated 7 Jan 2026 compiles NSE index calendar-year returns for 2006-2025 (as of 31 Dec 2025), including Nifty 50 TRI and Nifty Next 50 TRI and a Nifty 50 vs gold comparison. It is the best single source for this table but its host was blocked here. — [Rama Krishna Vadlamudi blog](https://ramakrishnavadlamudi.blogspot.com/2026/01/nse-indices-calendar-year-returns-2006.html)
- Other pages likely to hold the series, not opened: Bajaj AMC "Nifty 50 historical returns"; BasuNivesh "Nifty Next 50 vs Nifty Midcap 150"; FundsIndia monthly insights. — [Bajaj AMC](https://www.bajajamc.com/knowledge-centre/nifty-50-historical-returns); [BasuNivesh](https://www.basunivesh.com/nifty-next-50-vs-nifty-midcap-150/); [FundsIndia Insights](https://www.fundsindia.com/blog/wp-content/uploads/2021/11/202111-FundsIndia-Insights.pdf)
- Nifty 50 fell sharply in 2008 and rebounded sharply in 2009 (no percentages in the retrieved summary). — [Bajaj AMC](https://www.bajajamc.com/knowledge-centre/nifty-50-historical-returns)

### Inferences
- None that can be supported from sourced data.

### Gaps
- **Sourced table: not available.** Sites that must be allowed (or data pasted in) to build it: niftyindices.com (historical TRI values), amfiindia.com or mfapi.in (Gold BeES NAV), gold.org (INR gold returns), ramakrishnavadlamudi.blogspot.com.
- **2026 year-to-date: nothing reliable retrieved** for any of the four series. Fragments only: Nifty 50 about -7.7% in a window ending June 2026 ([Multibagg](https://www.multibagg.ai/market-pulse/articles/nifty-indices-one-year-returns-cmrl5lgvd01rkqt0jigwke0zs)), window definition unclear.
- **UNVERIFIED RECALL TABLE — not sourced, rounded, from the researcher's memory. Equity figures are probably within about ±2 points; gold within about ±5 points and depends on the series (domestic/MCX/ETF vs LBMA converted to INR). Do not publish as fact; verify every cell.**

| Year | Gold, INR (domestic price, approx.) | Nifty 50 TRI | Nifty Next 50 TRI | Nifty Midcap 150 TRI |
|---|---|---|---|---|
| 2008 | +26 | -51 | -63 | -65 |
| 2009 | +24 | +78 | +130 | +114 |
| 2010 | +23 | +19 | +19 | +20 |
| 2011 | +32 | -24 | -31 | -31 |
| 2012 | +12 | +29 | +50 | +47 |
| 2013 | -5 | +8 | +6 | -1 |
| 2014 | -6 (domestic; LBMA-in-INR was about flat to +2) | +33 | +46 | +63 |
| 2015 | -7 | -3 | +8 | +10 |
| 2016 | +11 | +4 | +8 | +7 |
| 2017 | +5 | +30 | +48 | +56 |
| 2018 | +8 | +5 | -8 | -13 |
| 2019 | +24 | +14 | +2 | +1 |
| 2020 | +28 | +16 | +16 | +26 |
| 2021 | -4 | +26 | +31 | +48 |
| 2022 | +14 | +6 | +1 | +4 |
| 2023 | +15 | +21 | +27 | +45 |
| 2024 | +21 (domestic, after the July 2024 import-duty cut; LBMA-in-INR was nearer +30) | +10 | +28 | +24 |
| 2025 | very roughly +65 to +75 | about +12 (price +10.5 is sourced) | +2.09 (sourced) | about +6 |
| 2026 YTD | not known | not known | not known | not known |

- Points of definition to settle when verifying: (a) TRI vs price index (TRI adds roughly 1.2-1.5 points a year for Nifty 50); (b) gold series: Gold BeES NAV includes about 0.8% expense and tracks domestic landed price including import duty, so 2013-14 (duty rises, premiums) and 2024 (duty cut from 15% to 6%) differ from LBMA-converted figures by several points.

---

## 7. Known failure modes of asset-class trend rotation

### Takeaway
The documented failure modes are whipsaw in sideways markets, late re-entry after V-shaped recoveries, sensitivity to the lookback chosen, and sensitivity to the rebalance day ("timing luck"), which alone has moved a single-asset trend rule's worst drawdown from about 19% to about 30%. In India, tax adds a further drag that none of the retrieved backtests include.

### Cited Findings
- **Rebalance-date luck, Faber's rule on SPY:** running the 10-month SMA rule with 21 different one-day offsets moved max drawdown from about 19% to about 30% and annual return by about 0.8 points. — [Newfound Research, "The Luck of the Rebalance Timing"](https://blog.thinknewfound.com/2013/08/the-luck-of-the-rebalance-timing/); replication at [Nitin Gupta's notes](https://nitingupta2.github.io/investing/luck-in-rebalance-timing)
- **Rebalance-date luck, GTAA 2006-2025:** 21 otherwise identical versions differing only in rebalance day (last trading day through the 20th) showed a large spread of outcomes; rebalancing one day late slightly improved results. Suggested fixes are checking more often or splitting the portfolio into tranches rebalanced on different days. — [Concretum Group](https://concretumgroup.com/global-tactical-asset-allocation/); [Piinghel write-up](https://piinghel.github.io/quants/2025/05/10/rebalancing-luck.html)
- **Tranching is not free for small accounts:** three tranches gave similar return with less risk, not more return; Concretum's "Tranching Dilemma" paper warns that for smaller investors trading costs may outweigh the benefit. — [Piinghel write-up](https://piinghel.github.io/quants/2025/05/10/rebalancing-luck.html); [Concretum papers](https://concretumgroup.com/papers/)
- **Size of timing luck generally:** Newfound's "Rebalance Timing Luck" paper reports dispersion "often exceeding 100 basis points annualized"; it is larger for faster signals such as momentum and for less constrained universes, and smaller when rebalancing is more frequent. — [Newfound Research via AdvisorAnalyst](https://advisoranalyst.com/?p=128230); [Newfound Research](https://blog.thinknewfound.com/2013/08/the-luck-of-the-rebalance-timing/)
- **Lookback sensitivity:** Hoffstein: "nothing magical" about 200 days; the signal is to some extent arbitrary. For GEM, 9-month vs 10-month lookbacks gave very different results, and the published 12-month spec regressed to the median of 1,226 variants out of sample. — [Newfound Research](https://blog.thinknewfound.com/2013/08/the-luck-of-the-rebalance-timing/); [Newfound GEM posts](https://blog.thinknewfound.com/tag/gem/); [ReSolve via Advisor Perspectives](https://www.advisorperspectives.com/articles/2019/05/06/global-equity-momentum-a-craftsmans-perspective)
- **Whipsaw:** "Trend following strategies will always incur some sort of whipsaw risk" (10-month GEM whipsawed in 2011); most trend CTAs lost money in 2011 and 2018 in choppy markets. — [Newfound GEM posts](https://blog.thinknewfound.com/tag/gem/); [Top Traders Unplugged](https://www.toptradersunplugged.com/trend-following-performance-report-december-2025/)
- **V-shaped recoveries and lag:** March 2020 fell 34% in 5 weeks and recovered in 5 months; GEM was out 3-4 months and re-entered late. TuringTrader: little benefit in late 2018 or spring 2020. GMOM's worst drawdown (25%) bottomed on 19 March 2020, i.e. the trend fund took most of the fall anyway. — [Freenance](https://freenance.io/strategie/dual-momentum-gary-antonacci-2026-pl-strategia-momentum-relative-absolute-implementacja-przyklad/); [TuringTrader](https://turingtrader-com.web.app/portfolios/antonacci-dual-momentum); [PortfoliosLab GMOM](https://portfolioslab.com/symbol/GMOM)
- **India-specific, from this repo's own tests:** checking the Nifty 200-DMA daily instead of monthly raised switches from about 2 to about 8 a year and cut CAGR from 10.1% to 7.8%; a 12-month absolute-momentum signal earned 4.4% because of the 2009 and 2020 V-shapes; quarterly or half-yearly checks let the 2020 crash through (about -36%). — [Prior notes](../Evidence%20based%20NSE%20trading%20strategies/momentum_factor_evidence.md); [prior report](../../reports/Evidence%20based%20NSE%20trading%20strategies.md)
- **Underperforming in most years is normal:** Faber's own paper says the timing rule lagged the index in about half of all years. — [Faber paper copy](https://www.scribd.com/doc/116881446/SSRN-id962461)
- **Post-publication decay:** dual momentum's return fell to about a third after 2013 in one test; GTAA's fell from about 11% to about 6%. — [Price Action Lab](https://priceactionlab.com/Blog/?p=68274); [Concretum Group](https://concretumgroup.com/global-tactical-asset-allocation/)
- **Tax (equity ETFs):** short-term gains on listed equity (12 months or less) are taxed at 20% and long-term at 12.5% above Rs 1.25 lakh a year, since 23 July 2024. — [Quicko](https://learn.quicko.com/ltcg-equity-shares-equity-mutual-funds), as cited in the [prior report](../../reports/Evidence%20based%20NSE%20trading%20strategies.md)
- **Tax drag measured on the reader's own rule:** the month-end 200-DMA rule on NIFTYBEES fell to 8.07% after costs and tax over 2011-2026 with 30 trades. — [Thunderbot backtests](../Evidence%20based%20NSE%20trading%20strategies/thunderbot_backtests.md)

### Inferences
- A monthly rotation among four risky ETFs will trade more than the single-asset 200-DMA rule (which made 30 trades in 15 years). Almost every exit will be inside 12 months, so nearly all realised gains are short-term. More switches mean more gains pulled forward into the 20% bracket (or the slab rate for non-equity ETFs) instead of compounding untaxed.
- With only one decision date a month, the reader's result will depend noticeably on which day is used. A 19%-vs-30% drawdown spread from day-of-month alone is larger than the difference between most competing rules. A backtest that reports only the month-end version overstates confidence; it should be re-run on other days of the month and the range reported.
- Next 50 and midcap fall harder than Nifty 50 in crashes and tend to be the top-ranked "trending" assets just before a fall, so a rotation that favours the strongest equity ETF will usually enter a crash holding the most volatile one. The plain Nifty 50 rule does not have this problem.
- Net judgement from the evidence retrieved: there is **no sourced, live, after-tax evidence that a multi-ETF rotation beats the reader's existing month-end 200-DMA rule in India.** The claim that it does rests on blog backtests over a gold bull market. Global live evidence (GMOM, GEM post-2014, SG Trend 2011-2019) says to expect lower returns than backtests, with drawdowns of 20-25% rather than 10-12%.

### Gaps
- **Tax treatment of the non-equity legs was not researched this session.** **UNVERIFIED RECALL**, to be checked by whoever covers tax: gains on gold ETFs held 12 months or less are taxed at the investor's slab rate (not 20%), with 12.5% long-term after 12 months; gains on a liquid/debt ETF are taxed at slab rate regardless of holding period; Liquid BeES credits daily dividends that are taxable income. If right, a monthly rotation into gold is taxed more heavily than the equity legs for anyone in the 30% slab.
- No published study was found that measures tax drag on a multi-asset monthly rotation in India.
- No Indian study of rebalance-day sensitivity was found; the repo's own backtester could produce this.
- Newfound's specific papers on trend-following timing luck were not opened; the figures above come from search summaries.
