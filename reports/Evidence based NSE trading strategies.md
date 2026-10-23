# Trade less: momentum and trend beat intraday

The only simple, rules-based approaches with credible evidence of positive returns after costs and taxes for a Groww retail account are low-turnover delivery strategies on daily bars. The two that stand out are **cross-sectional momentum on large and mid caps (the Nifty200 Momentum 30 rule)** and a **monthly-checked 200-day trend filter on a Nifty 50 ETF**. Intraday and F&O trading have the opposite evidence. SEBI finds that **71% of individual intraday cash traders lost money in FY23**, and **87.7% to 93% of individual F&O traders lost money in every year studied from FY22 to FY26**. Thunderbot's own intraday ORB, VWAP-reversion and EMA-pullback results (profit factors 0.18 to 0.40) are what that base rate predicts. The unbiased evidence for momentum is NSE's Nifty200 Momentum 30 TRI: **18.8% CAGR against 13.9% for the Nifty 200 TRI from 2005 to 2026**, but most of that history is a back-test, and the live five years show **9.28% against 6.37% for the Nifty 50 TRI**. Thunderbot's 21% after-tax momentum backtest is not achievable, because about **10 points a year of it is survivorship bias** from testing on today's Nifty 100. Thunderbot should retire its intraday strategies and adopt two daily-bar strategies, with exact rules given below. The first is a NIFTYBEES/Nifty 200-DMA trend sleeve (realistic **6.5–8.5% after tax with a -15% to -25% maximum drawdown**). The second is a Momentum 30 replication with a monthly market filter (realistic **8–13% after tax and costs, with -20% to -35% drawdowns in ordinary bear markets and worse in a 2008-style crash**). Neither strategy guarantees a profit. Both can lose money for years, and the momentum sleeve can trail the index badly for 6–18 months at a time.

## Nine in ten F&O traders and seven in ten intraday traders lose money

SEBI's outcome studies give a clear ranking of retail trading styles in India, and the higher-turnover styles do worse. The July 2024 intraday cash study found that **71% of individual intraday traders made net losses in FY23, up from 65% in FY19** ([SEBI press release](https://www.sebi.gov.in/media-and-notifications/press-releases/jul-2024/sebi-study-finds-that-7-out-of-10-individual-intraday-traders-in-equity-cash-segment-make-losses_84948.html); [Taxscan](https://www.taxscan.in/7-out-of-10-individual-intraday-traders-in-equity-cash-segment-make-losses-says-sebi/422657)). Friction drives much of the damage: loss-makers paid trading costs equal to a **further 57% of their trading losses**, and the loss-maker share rose to **80% among traders with more than 500 trades a year** ([Taxscan](https://www.taxscan.in/7-out-of-10-individual-intraday-traders-in-equity-cash-segment-make-losses-says-sebi/422657); [Outlook Money](https://www.outlookmoney.com/invest/most-intra-day-traders-incur-losses-half-of-traders-under-30-years-herere-detailed-findings-from-sebi-report)).

F&O is worse. The August 2026 SEBI study covers the top 15 brokers, about 90% of individual traders. It finds **87.7% of individuals lost money in FY26, after 90.9% in FY25 and 91.1% in FY24**. Individuals lost about **₹3.85 lakh crore net over FY22–FY26** and paid about **₹1 lakh crore in transaction costs** ([SEBI FY25–FY26 study](https://www.sebi.gov.in/sebi_data/attachdocs/aug-2026/1787233506209.pdf)). Options account for **92% of individual losses**, and those losses occurred in almost every quarter whether Nifty rose or fell. That pattern points to structural losses (premium decay, spreads and costs) rather than bad market calls. Experience does not lower the chance of losing: new and regular traders lost at nearly identical rates (87.8% and 87.7%). Regular traders simply lost more per head because they traded 45.7 times their portfolio value ([SEBI FY25–FY26 study](https://www.sebi.gov.in/sebi_data/attachdocs/aug-2026/1787233506209.pdf)).

Automation does not change this for retail traders. Over FY25–FY26, **99% of FPI and proprietary-desk gross profits came from algorithmic entities**, and the top 10 prop traders took 74.5% of all prop profit. Individuals tagged as "algo" users still lost **₹51,728 crore gross** over the same two years ([SEBI FY25–FY26 study](https://www.sebi.gov.in/sebi_data/attachdocs/aug-2026/1787233506209.pdf)). The edge sits with co-located, member-cost-structure desks. A Python engine on a retail API has none of their advantages at intraday horizons.

Thunderbot's own intraday test fits this picture. Over 39 trading days of real 5-minute bars (21 Aug–16 Oct 2026, ₹1 lakh, five Nifty stocks), the three strategies lost money after costs, with profit factors far below 1:

| Strategy | Net P&L | Profit factor |
|---|---|---|
| Opening-range breakout | -₹10,817 | 0.40 |
| VWAP reversion | -₹9,890 | 0.18 |
| EMA pullback | -₹13,293 | 0.30 |

Source: [Thunderbot backtests](../research_notes/Evidence%20based%20NSE%20trading%20strategies/thunderbot_backtests.md). Thirty-nine days is too short to prove these rules have negative expectancy. But nothing in the evidence suggests they have a positive one, and the SEBI base rate says the default outcome for frequent intraday trading is a loss. Continuing to optimise them would mostly fit noise.

## Costs and taxes set a hurdle of about 0.3% per delivery round trip

Groww charges the same brokerage for delivery and intraday: **₹20 or 0.1% of order value, whichever is lower, per executed order**, with a ₹5 floor rule for tiny orders. Delivery sells also pay a **DP charge of ₹23.60 per scrip per sell day** (₹16.5 Groww plus ₹3.5 CDSL, plus 18% GST) ([Groww Pricing](https://groww.in/pricing); [Groww Help](https://groww.in/help/stocks,-f&o,-ipo-&-mtf/discoverable/what-are-the-different-charges-mentioned-in-the-report)). The biggest delivery cost is STT, which is unchanged by Budgets 2024–2026: **0.1% on both the buy and sell legs for delivery, 0.025% on the sell leg only for intraday** ([Groww Pricing](https://groww.in/pricing); [Zerodha Charges](https://zerodha.com/charges)). The Budget 2026 STT hike applied only to F&O, raising futures from 0.02% to 0.05% and options premium from 0.10% to 0.15% ([Upstox News](https://upstox.com/news/personal-finance/tax/explained-how-the-stt-hike-on-equity-futures-and-options-affects-traders-and-investors/article-189260/)).

The other charges are small:

- NSE exchange charges: about 0.00307% per side.
- SEBI fee: 0.0001% per side.
- Stamp duty on buys: 0.015% for delivery, 0.003% for intraday.
- GST: 18% on brokerage, exchange charges, the SEBI fee and DP charges.

Sources: [Groww Pricing](https://groww.in/pricing); [Zerodha Support](https://support.zerodha.com/category/account-opening/resident-individual/ri-charges/articles/exchange-transaction-charges).

Equity ETFs are the exception that matters most for strategy design. **Delivery sales of equity ETFs pay STT of only 0.001%, on the sell side only** ([Groww help: STT](https://groww.in/help/stocks,-f&o,-ipo-&-mtf/sx-pricing/what-is-stt)).

| Round trip on Groww (explicit costs, before slippage and tax) | ₹10,000 | ₹1,00,000 | ₹10,00,000 |
|---|---|---|---|
| Stock, delivery (CNC) | ₹69 (0.69%) | ₹293 (0.29%) | ₹2,296 (0.23%) |
| Stock, intraday (MIS) | ₹27 (0.27%) | ₹83 (0.08%) | ₹402 (0.04%) |
| Nifty 50 ETF, delivery | — | ≈₹94 (0.09%) | — |

The figures above are computed from the [Groww Pricing](https://groww.in/pricing) schedule. Slippage comes on top. NSE puts the Nifty 50 basket impact cost at **0.02% for ₹50 lakh** ([NSE Nifty 50 page](https://www.nseindia.com/products-services/indices-nifty50-index)). Individual midcaps are several times wider, so a reasonable assumption is 0.03–0.05% per side for Nifty 50 names and 0.08–0.15% for the midcap part of the Nifty 200.

Position size matters because brokerage and DP charges are fixed amounts. Take a 30-stock portfolio on ₹5 lakh, about ₹16,700 per position. Applying the same schedule, each position costs about **₹100 per round trip, or 0.6%**, before slippage. The same trade in NIFTYBEES costs under 0.1%.

Tax widens the gap between delivery and trading income. Listed equity gains on which STT was paid are taxed as follows (since 23 July 2024, and unchanged in Budget 2026):

- **STCG at 20%** on holdings of 12 months or less.
- **LTCG at 12.5%** above ₹1.25 lakh per financial year.

Sources: [Quicko](https://learn.quicko.com/ltcg-equity-shares-equity-mutual-funds); [Bajaj Finserv](https://www.bajajfinserv.in/what-is-ltcg-tax-rate). The 4% cess applies on top. Intraday profits are speculative business income taxed at slab rates, which means about 31% or more at the top slab. Speculative losses can be set off only against speculative income ([Sahi](https://www.sahi.com/blogs/income-tax-on-intraday-trading-india); [1 Finance](https://1finance.co.in/blog/itr-for-fo-and-intraday-traders-ay-2026-27/)). So intraday faces a higher tax rate on any wins, and its losses are partly trapped.

Two fixed overheads apply to an automated account:

- **API fee.** The Groww Trade API costs **₹499 a month or ₹4,999 a year, plus GST**. That is about 1.2% a year of drag on ₹5 lakh and 0.3% on ₹20 lakh. The free tier still allows placing orders and reading holdings; it lacks live data and historical candles ([Groww Blog](https://groww.in/blog/api-trading-on-groww)). A daily-bar strategy that gets its data elsewhere may therefore avoid the fee, but Groww calls the free tier a trial, so its permanence is uncertain.
- **SEBI retail-algo framework (mandatory from 1 April 2026).** It requires a whitelisted static IP for order APIs and daily authentication. Exchange registration is needed only above **10 orders per second** ([Fyers support](https://support.fyers.in/portal/en/kb/articles/what-are-the-new-sebi-rules-for-retail-algo-trading-from-april-01-2026); [Zerodha Daily Brief](https://thedailybrief.zerodha.com/p/sebis-latest-algo-trading-rules)). A daily rebalancer never comes near that limit.

## Momentum is India's most robust anomaly, but its live premium is about half the back-test

Nifty200 Momentum 30 is a fully specified rule that anyone can replicate:

- **Universe:** F&O-eligible Nifty 200 stocks with at least one year of listing.
- **Score:** 6-month and 12-month price returns, ending one month before the rebalance month, each divided by one-year annualised volatility of daily log returns. Each ratio is z-scored across the universe and the two are averaged 50/50.
- **Holdings:** the top 30, weighted by score × free-float market cap, with each stock capped at the lower of 5% or 5× its market-cap weight.
- **Rebalance:** every June and December, with a buffer. The top 15 are always included, and existing holdings stay until they rank below 45.

Source: [NSE Methodology Document, Sept 2026](https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf).

Over 1 April 2005 to 30 June 2026 the TRI compounded at **18.8%, against 13.9% for the Nifty 200 TRI and 13.6% for the Nifty 50 TRI**. It beat the Nifty 200 in 14 of 21 financial years ([HDFC AMC presentation, July 2026](https://files.hdfcfund.com/s3fs-public/Others/2026-07/HDFC%20NIFTY200%20Momentum%2030%20Index%20Fund_PPT%20%28July%202026%29.pdf)). The index launched only on 25 August 2020, so the 2005–2020 record is a back-test. The live record is weaker: the five-year TR CAGR to 30 September 2026 was **9.28% against 6.37% for the Nifty 50 TRI**, and the one-year return was -0.47% ([NSE factsheet](https://www.niftyindices.com/Factsheet/Factsheet_Nifty200_Momentum30.pdf); [ICICI Pru factsheet](https://www.icicipruamc.com/blob/knowledgecentre/factsheet-schemes/Passive%20Schemes/ETFs%20Schemes/ICICI%20Prudential%20Nifty%20100%20Low%20Volatility%2030%20ETF.pdf)). The premium survived going live at roughly 3 points a year, not the back-tested 5.

Academic data supports the factor itself. In the survivorship-adjusted IIM Ahmedabad factor library, the winners-minus-losers factor averages **about 1.1% a month (t ≈ 3.1) from 1993 to 2025**. Over 2005–2025, the implementable long-only leg, big-cap winners, compounded at **17.2% against 14.9% for the market**. These statistics were computed for this research from the [IIMA data library](https://faculty.iima.ac.in/iffm/Indian-Fama-French-Momentum/) and follow [Agarwalla, Jacob & Varma](https://faculty.iima.ac.in/~iffm/Indian-Fama-French-Momentum/four-factors-India-90s-onwards-IIM-WP-Version.pdf). [Aggarwal & Gupta (2017)](https://www.publishingindia.com/archive/jcar/can-small-investors-gain-from-momentum-trading-in-india-an-empirical-investigation) find long-only momentum remains profitable after Indian transaction costs.

The strongest caution comes from an independent replication covering December 2006 to June 2025. It used 30 equal-weighted stocks with semi-annual rebalancing and included costs and Indian capital-gains taxes. It earned **14.01% net against 10.42% for the Nifty 50**, but its maximum drawdown was **-70.5% with a 65-month recovery**. Its liquid-stock subset returned only **8.51%**, which suggests much of the premium sits in less liquid names ([BacktestIndia](https://backtestindia.com/blog/momentum-investing-india-backtest); [Freefincal](https://freefincal.com/is-indian-momentum-investing-just-a-liquidity-illusion/)).

Momentum's risks are large, and they arrive in clusters:

- **Crashes.** The index lost **60% in 2008**, with a maximum drawdown of -67.7% against -63.7% for the Nifty 200.
- **Post-crash rebounds.** It lagged the 2009 rebound by 19 points.
- **Leadership rotations.** It fell about **27–29% from its September 2024 peak** while broad indices fell 12–15%, and it ended CY2025 down 4.57% against roughly +9.6% for the Nifty 200 ([NSE whitepaper, Apr 2026](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf); [Curious Investing Insights](https://curiousinvestinginsights.substack.com/p/momentum-or-mayhem-unpacking-the)).
- **Sector concentration.** In mid-2026 the portfolio held capital goods, financials, metals and power, with no IT, FMCG or oil and gas ([HDFC AMC](https://files.hdfcfund.com/s3fs-public/Others/2026-07/HDFC%20NIFTY200%20Momentum%2030%20Index%20Fund_PPT%20%28July%202026%29.pdf)).

Rebalancing frequency is the one design choice NSE has tested directly. **Semi-annual rebalancing beat quarterly for Momentum 30 (19.19% against 17.12% since 2005)**, won in every 7- and 10-year rolling window, and produced 20–50% less churn. Semi-annual one-way churn still runs at about **100–135% a year** ([NSE whitepaper, Exhibits 8–11](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf)). About 24 passive funds with roughly ₹17,700 crore of AUM now track momentum indices, with one-year tracking errors of 0.17–0.52%. That makes them a cheap benchmark, and a fallback, for any DIY replication.

Low volatility and quality are the main diversifiers, offering **similar long-run returns with shallower drawdowns**:

- **Nifty100 Low Volatility 30:** fell 43.3% in 2008 against 53.7% for the Nifty 100 ([NSE Low Vol white paper](https://archives.nseindia.com/content/indices/NIFTY100_Low_Vol30_White_paper_Jun2018.pdf)), and returned 12.38% a year over its ETF's life against 11.03% for the Nifty 50 TRI ([ICICI Pru factsheet](https://www.icicipruamc.com/blob/knowledgecentre/factsheet-schemes/Passive%20Schemes/ETFs%20Schemes/ICICI%20Prudential%20Nifty%20100%20Low%20Volatility%2030%20ETF.pdf)).
- **Alpha Low-Volatility 30:** 17.71% since 2005 at 17.2% volatility.
- **Quality 30:** 16.64% since 2005 at 17.9% volatility ([NSE factsheets](https://www.niftyindices.com/Factsheet/Factsheet_NIFTY_Alpha_Low-Volatility_30.pdf)).
- **Academic support for quality:** over 1995–2021, quality-minus-junk matched momentum's average return with smaller drawdowns ([Jacob, Pradeep & Varma via Quantpedia](https://quantpedia.com/performance-of-factor-strategies-in-india/)).

Quality needs point-in-time fundamentals (ROE, D/E and EPS variability) that free daily-bar data does not provide. Low volatility needs only prices, but its five-year live return of 8.12% shows it lags in bull runs. Both factors also lagged in 2026: one-year returns to 30 September were -4.68% for Low Vol 30 and -5.42% for Quality 30.

## A monthly 200-day filter roughly halves drawdowns and costs 1–1.5 points a year

On the Nifty 50, a 200-day moving-average rule mainly cuts drawdowns; it does not raise returns, and how often it is checked matters a great deal. A test on Yahoo ^NSEI daily data from July 2008 to October 2026 assumed 6.5% interest on cash and 0.1% per switch, and ignored tax:

| Rule | CAGR | Max drawdown | Switches per year |
|---|---|---|---|
| Buy and hold | 10.0% | -45.4% | — |
| Daily check | 7.8% | -20.9% | 7.9 |
| Month-end check | 10.1% | -24.2% | 1.9 |

The month-end rule lagged after 2015, at 7.3% against 8.8% for buy and hold. A 12-month absolute-momentum rule earned only 4.4%, because India's V-shaped recoveries in 2009 and 2020 punish slow signals. These are calculations done for this research from [Yahoo ^NSEI data](https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI?period1=0&period2=1792000000&interval=1d), not published results, and no peer-reviewed Indian study of the filter with costs and taxes was found.

Thunderbot's own after-tax test points the same way. It used NIFTYBEES from 2011 to 2026 with full Groww costs, slippage and capital-gains tax ([Thunderbot backtests](../research_notes/Evidence%20based%20NSE%20trading%20strategies/thunderbot_backtests.md)):

| Variant | After-tax CAGR | Max drawdown | Trades |
|---|---|---|---|
| Month-end check, 1% buffer | 8.07% | -15% to -17% | 30 |
| Weekly check, no buffer | 6.33% | -23.9% | 94 |
| NIFTYBEES buy and hold (pre-tax benchmark) | 9.47% | -36.3% | — |

The filter gave up about 1–1.5 points a year in a mostly rising market in exchange for less than half the drawdown. The true after-tax gap is a little smaller, because the buy-and-hold benchmark is shown before its own LTCG.

Applied to a momentum portfolio, the filter targets the 2008-type crash. It cannot help in 2009-type rebounds or 2025-type rotations that happen while the broad market sits above its 200-day average ([NSE whitepaper, Apr 2026](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf)). Thunderbot's tests found one implementation detail that matters: the filter protected the momentum book only when it was **checked monthly**. Quarterly and semi-annual checks let the 2020 crash through, with drawdowns of about -36%.

The current regime is relevant here. In October 2026 only 10 of the 50 Nifty stocks were above their 200-day averages, and the index had spent a long streak below its own ([Business Standard, Oct 2026](https://www.business-standard.com/markets/news/nifty-s-200-day-moving-average-sounds-alarm-as-market-breadth-thins-126101401265_1.html); [Whalesbook](https://www.whalesbook.com/news/English/sebiexchange/Nifty-50-Marks-160-Day-Streak-Below-200-DMA-What-It-Means/6adabe3379a16deaeafae99c)). If those conditions still hold, both recommended strategies would start in cash.

## Short-term mean reversion lacks any credible Indian evidence

No backtest of RSI(2), internal bar strength or "buy after N down days" on the Nifty 50, Bank Nifty or NIFTYBEES with a disclosed method was found. The best-documented replication is on US data. A rebuild of Connors' RSI(2) rule on SPY from 1993 to 2026 won about **77% of trades with a +0.63% average trade**. But it compounded at only **5.0% against 10.8% for buy and hold**, and its Sharpe ratio fell from 0.97 before publication to 0.68 after. Since 2009 it has returned **4.3% a year against 14.9%** for the index ([Empirica Lab](https://empiricalab.substack.com/p/connors-rsi2-spy)).

The Indian evidence is cross-sectional and fragile. One study of reversal among Nifty 50 stocks found a gross Sharpe of 1.03, but per-trade edges were at or below the 25–30 bps delivery round-trip cost, annual Sharpe turned **negative in 2025 and 2026**, and point-in-time constituents were not stated ([Delphic Alpha](https://delphicalpha.substack.com/p/does-mean-reversion-work-on-the-nifty)). Academic work finds Indian reversals concentrated in the **most illiquid** stocks ([Chui et al. 2023](https://ideas.repec.org/a/eee/pacfin/v82y2023ics0927538x23002640.html)), which are the opposite of an index ETF.

On cost alone, NIFTYBEES at about 0.09% per round trip could keep most of a 0.5% per-trade edge. But the edge itself is unproven in India. A strategy in the market about 11% of the time also produces too few trades to establish significance. Mean reversion belongs in Thunderbot's research queue, tested walk-forward on NIFTYBEES prices. It is not a candidate for live capital.

## Survivorship bias inflates Thunderbot's momentum backtest by about 10 points a year

Thunderbot's momentum rotation used NSE-style scores on **today's Nifty 100 list**. The best variant (monthly rebalance, top 15, keep within rank 25, market filter on) showed **21.36% after tax with a -19.4% maximum drawdown** from 2011 to 2026. Thunderbot's own control exposes the problem: simply equal-weighting the same 100 current members and holding them returned **19.56% after tax**, against 9.47% for NIFTYBEES ([Thunderbot backtests](../research_notes/Evidence%20based%20NSE%20trading%20strategies/thunderbot_backtests.md)). Picking from stocks known to have survived to 2026 explains most of the headline. Part of the 10-point gap may also be an equal-weight size tilt.

Momentum's edge over that control was a more believable 5.6 to 7.6 points. Even that figure is probably inflated, because momentum concentrates in exactly the past winners that a current-constituent list over-represents. The only quantified Indian estimate, for small caps, finds survivor-only backtests overstate returns by **4.94 points a year** ([Ranse, arXiv 2603.19380](https://arxiv.org/abs/2603.19380)). That study did not test momentum.

Thunderbot's backtest also favoured monthly rebalancing, which contradicts NSE's unbiased finding that semi-annual beats quarterly. A biased sample rewards turnover, because extra trades simply chase stocks already known to survive. The single-ETF trend test, by contrast, has **no survivorship problem**, because the index carries its own historical members.

Fixing this requires point-in-time membership. The free sources are:

- NSE's `IndexInclExcl.xls`, reportedly covering changes to July 2020.
- niftyindices monthly constituent archives for April 2013 to March 2022.
- Index-change announcements after that.

Sources: [TradingQnA](https://tradingqna.com/t/where-can-i-find-historical-composition-of-nifty-indices/7163); [Marketcalls](https://www.marketcalls.in/llm-models/how-to-build-survivorship-bias-free-nifty-50-historical-data-using-grokbot.html).

Yahoo data needs auditing for Indian corporate actions. One trader reported "completely wrong returns" around the HDFC Bank merger ([TradingQnA](https://tradingqna.com/t/has-anyone-found-wrong-adjusted-prices-in-nse-historical-data-for-backtesting/192938)), and delisted tickers are generally missing. NSE bhavcopy tools (jugaad-data, EOD2) are the cross-check, though NSE endpoints change and rate-limit without notice ([jugaad-data](https://pypi.org/project/jugaad-data); [EOD2](https://github.com/BennyThadikaran/eod2)).

A credible test also needs:

- Signals on the close of day t, filled at the next open or the next close.
- Parameters frozen on one period and tested on a later one.
- Comparison against the Nifty 50 TRI from niftyindices, not the ^NSEI price index.

## Recommendation: two daily-bar strategies with fixed rules

Thunderbot should **retire ORB, VWAP reversion and EMA pullback from live trading** and rebuild around two delivery strategies, split roughly 50/50. Both run once a day after the close and place a few orders a month at most, so the SEBI algo framework and Groww rate limits are not binding. Both should park idle money in a liquid ETF or liquid fund, since the backtests assumed about 6% interest on cash.

**Strategy 1: Nifty 200-day trend on NIFTYBEES.** This is the low-cost core, with no survivorship bias.

| Element | Rule |
|---|---|
| Data | Daily closes of the Nifty 50 index and NIFTYBEES |
| Signal | 200-day simple moving average (SMA200) of the Nifty 50 close |
| Check day | Last trading day of each month only; ignore all intra-month moves |
| Entry | If in cash and close > SMA200 × 1.01, buy NIFTYBEES with the whole sleeve the next trading day |
| Exit | If invested and close < SMA200 × 0.99, sell all NIFTYBEES the next trading day and move to a liquid ETF or fund |
| Orders | One order per leg, using a limit or market-price-protection order |
| Expected | About 1 round trip a year; about 0.04% explicit cost per round trip on ₹5 lakh |

Confirm that this symmetric 1% band matches the buffer definition in `worker/thunderbot/daily.py` before treating the backtest as validation.

**Strategy 2: Momentum 30 replication with a monthly market filter.** This is the return engine.

| Element | Rule |
|---|---|
| Universe | Current Nifty 200 members that are F&O-eligible with at least 252 trading days of history. Backtests must use point-in-time membership |
| Score | MR12 = (P[end of month M−1] / P[end of month M−13] − 1) / σ<br>MR6 = (P[M−1] / P[M−7] − 1) / σ<br>σ = annualised standard deviation of the last 252 daily log returns<br>Z-score MR12 and MR6 across the universe; score = 0.5·Z12 + 0.5·Z6 |
| Rebalance | Score on the last trading day of May and November; trade on the first trading days of June and December |
| Selection | Hold 30 stocks. Ranks 1–15 are always held. Existing holdings ranked 16–45 are kept. Sell holdings ranked below 45 or that have left the Nifty 200. Fill empty slots from the best-ranked non-holdings |
| Weighting | Equal weight, 1/30 of sleeve equity for each new buy. Leave retained positions untouched to save orders |
| Market filter | On every month-end, if Nifty 50 close < SMA200 × 0.99, sell everything the next day and hold a liquid ETF. Re-enter when a month-end close is > SMA200 × 1.01, buying the current top 30 by fresh scores |
| Capital | ₹10 lakh or more preferred, which keeps positions above about ₹33,000 and the API fee below 0.6% a year. Below that, execute the sleeve through a Nifty200 Momentum 30 ETF or fund, timed by the same filter, which avoids 0.1% stock STT on each leg |

Combining semi-annual ranking with a monthly filter follows two separate findings: NSE's rebalancing study and Thunderbot's finding that the filter only protects when checked monthly. The combination itself has not been tested, so Thunderbot must test it on point-in-time data before going live.

**Realistic expectations.** These ranges are anchored on unbiased evidence, not on Thunderbot's survivorship-biased momentum backtest.

| | Long-run CAGR, after costs and tax | Max drawdown | Main anchors |
|---|---|---|---|
| Strategy 1: NIFTYBEES trend | 6.5–8.5% (lags buy and hold by 1–2 points in bull markets) | -15% to -25% | Thunderbot after-tax 8.07%; ^NSEI month-end test 10.1% pre-tax (7.3% since 2015) |
| Strategy 2: Momentum 30 with filter | 8–13% (market plus about 1–3 points net); live 5-year anchor 9.3% pre-tax | -20% to -35% in ordinary bears; -50% or worse if a crash gaps through a month-end check | NSE TRI 18.8% vs 13.9% (mostly back-test); live 9.28% vs 6.37%; replication 14.0% net with -70.5% drawdown unfiltered |
| 50/50 blend | About 7.5–11% | About -20% to -30% | Combination of the two rows above |

The momentum range takes the live and replication premiums of roughly 2–4 points over the market. It then deducts about 1–2 points for 20% STCG (roughly 80% of momentum gains are short-term), the 0.6–0.8% round-trip cost on a churn of 100–135% a year, and the filter's own round trips ([BacktestIndia](https://backtestindia.com/blog/momentum-investing-india-backtest)). The API fee adds about 1.2% a year at ₹5 lakh if the paid tier is used.

**Main risks.**

- **Losing years are certain to happen.** Neither strategy guarantees profit, and both will have losing years.
- **Momentum's bad regimes.** Momentum will at times trail the market by 10–20 points for 6–18 months, as in 2009, FY23 and 2024–25. Momentum has also delivered less in liquid stocks than in illiquid ones, and growing passive AUM could crowd the premium further.
- **Whipsaw and lag.** The trend filter whipsaws in sideways markets, lags V-shaped recoveries, and realises STCG on every exit.
- **Unproven combinations.** Thunderbot's best filtered results have not been reproduced on point-in-time data. Yahoo corporate-action errors can silently corrupt stock-level backtests.
- **Operational risk.** This covers static-IP and daily-authentication failures, the Groww free API tier's uncertain permanence, and order rejections at rebalance.
- **Behavioural risk.** Abandoning the system after a drawdown is the most common way rules-based investors turn a positive-expectancy strategy into a realised loss.

Before committing capital, Thunderbot should:

1. Rebuild the momentum backtest on point-in-time constituents.
2. Benchmark both sleeves against the Nifty 50 TRI and a Momentum 30 index fund.
3. Paper-trade for one to two rebalance cycles.
4. Set a written kill rule: if the DIY sleeve trails the Momentum 30 fund by more than its cost advantage over a full cycle, buy the fund.

## Conclusion

The evidence changes what Thunderbot's job should be. Its edge will not come from out-trading algorithmic desks on 5-minute bars, where SEBI data shows retail participants fund institutional profits. It can come from exploiting a slow, documented anomaly cheaply and keeping drawdowns small enough that the owner sticks with it. Because it is cheap to run, the trend sleeve can be held at full size. The momentum sleeve earns its place only if it beats a ₹0-effort index fund after Groww's per-order costs, STCG and the API fee.

The most useful finding from Thunderbot's own work is its survivorship control, not its headline return. Any future strategy should be required to beat that kind of control, as well as the Nifty 50 TRI, before it reaches live capital. That discipline protects capital more reliably than any single rule.
