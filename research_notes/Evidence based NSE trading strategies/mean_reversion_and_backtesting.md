# Short-term mean reversion on Indian indices/ETFs, and backtesting Indian equities with free data

Research date: 23 Oct 2026. Every source is labelled with its publication date where known. Overall evidence quality: **weak for India-specific index-level mean reversion**. No peer-reviewed or code-published RSI(2)/IBS/N-down-days backtest on Nifty 50, Bank Nifty or NIFTYBEES turned up. Most quantified evidence is from US SPY data or from Indian cross-sectional (stock-ranking) studies.

## 1. Does simple short-term mean reversion (RSI(2), N down days, IBS, buy-the-dip above 200DMA) work on Nifty / Bank Nifty / NIFTYBEES after Indian costs?

### Takeaway
I found no credible, methodology-disclosed backtest of Connors RSI(2), IBS or "buy after N down days" on Nifty 50, Bank Nifty or NIFTYBEES. The best-documented recent replication is on US SPY (Oct 2026). On SPY the rule still has an edge per trade (~77% win rate, +0.63% average trade, ~11% time in market), but the edge per trade has shrunk since publication (2009 onward) and the rule badly lags buy-and-hold CAGR. Indian evidence on short-term reversal exists but is cross-sectional (ranking stocks) and is fragile to delivery costs. Any Nifty result has to be produced and validated in-house.

### Cited Findings
**US benchmark evidence (best documented, not India):**
- Empirica Lab (11 Oct 2026) rebuilt the Connors RSI(2) rule on SPY. Rules: buy at the close when RSI(2) < 10 and close > 200-day SMA; sell at the close when close > 5-day SMA; no stop. Data: Yahoo dividend-adjusted, 29 Jan 1993 to 30 Sep 2026, 2 bps per side. Results vs buy-and-hold:
  - 265 trades, 204 winners (~77%), average trade +0.63%, holding period a little over 3 days.
  - Exposure 893 of 8,475 days (~11%).
  - CAGR 5.0% vs 10.8%; Sharpe 0.81 vs 0.65; max drawdown 14.8% vs 55.2%.
  - Last three years: 8.8% vs 22.3% annualised.
  - Worst trade -10.2% (Jul to Aug 2011). Longest stretch without a new equity high: 693 trading days.
  — [Empirica Lab, "Connors' RSI(2) had a Sharpe of 0.97 before the book. Since then: 0.68."](https://empiricalab.substack.com/p/connors-rsi2-spy)
- Decay after publication (same source, split at 1 Jan 2009):

  | Period | Trades | Win rate | Avg trade | Sharpe (rule vs B&H) | Max DD |
  |---|---|---|---|---|---|
  | Pre-2009 | 116 | 81% | +0.79% | 0.97 vs 0.42 | 7.0% |
  | Post-2009 | 149 | 74% | +0.51% | 0.68 vs 0.87 | 14.8% |

  Since 2009 SPY returned 14.9%/yr and the rule 4.3%/yr. — [Empirica Lab](https://empiricalab.substack.com/p/connors-rsi2-spy)
- Cost sensitivity on SPY (same source): annualised return 5.3% at zero cost, 4.4% at 6 bps/side, 3.7% at 10 bps/side. — [Empirica Lab](https://empiricalab.substack.com/p/connors-rsi2-spy)
- Robustness (same source):
  - All 15 parameter variants (RSI length 2 to 4, thresholds 5 to 25) were positive, with Sharpe 0.13 to 0.92. A threshold of 5 returned only 2.7%/yr.
  - Five other US equity ETFs returned 2.1 to 4.3%/yr (Sharpe 0.38 to 0.53).
  - Deflated Sharpe 99%; probability of backtest overfitting 4%.
  - The author flags that closing-price fills assume an RSI that is only final at the close.
  — [Empirica Lab](https://empiricalab.substack.com/p/connors-rsi2-spy)
- Other RSI(2) reports are vendor/blog quality and not India:
  - "75-79% win rate" claims. — [toptradingstrategy.com](https://toptradingstrategy.com/strategy/rsi-2-mean-reversion); [QuantifiedStrategies RSI-2](https://www.quantifiedstrategies.com/rsi-2-strategy/)
  - A Substack variant (2000 to 2025): CAGR 4.88%, max DD 13.64%, win rate 73.94%, 11 trades/yr. — [Algomatic Trading](https://algomatictrading.substack.com/p/strategy-6-my-take-on-larry-connors)
  - A forum user reports 1965 to 1995 results with a 66% win rate but a net loss, which points to regime dependence. — [Trade2Win thread](https://www.trade2win.com/threads/backtest-results-for-connors-rsi2-strategy.242688/)
- IBS: QuantifiedStrategies claims IBS strategies worked over three decades on SPY/QQQ. This is vendor-quality, US-only evidence. — [QuantifiedStrategies IBS](https://www.quantifiedstrategies.com/internal-bar-strength-ibs-indicator-strategy/)
- IBS: Alvarez Quant Trading notes that IBS captures only one-day mean reversion and he did not get it working as a standalone strategy. — [Alvarez Quant Trading, IBS](https://alvarezquanttrading.com/blog/internal-bar-strength-for-mean-reversion/)

**India-specific evidence (all weak or indirect):**
- Marketcalls (3 Nov 2008) "2 period RSI trading systems for Nifty" proposes Nifty rules:
  - Long the next day when RSI(2) < 5, adding each day it stays below 5; exit when RSI > 50. Mirror rule for shorts above 95.
  - The only numbers it gives are Connors' **US stock** statistics (1995 to mid-2006). For example, after RSI(2) < 2 the average excess return was +0.22% (1 day), +0.51% (2 days) and +0.87% (1 week).
  - **No Nifty win rate, trade count, cost or drawdown is reported.**
  — [Marketcalls 2008](https://www.marketcalls.in/nifty-technicals/2-period-rsi-trading-systems-for-nifty.html)
- Delphic Alpha Substack (28 Jun 2026, paywalled, partially visible) tested **cross-sectional** reversal on Nifty 50 stocks over ~11 years (2015 to 2026):
  - Setup: long recent losers, short recent winners, open-to-close returns, 192 configurations, results gross of costs.
  - Best gross Sharpe 1.03 (2-day lookback, 2-day rebalance). Annual Sharpe was positive in most years 2015 to 2024 and **negative in 2025 and 2026 YTD**.
  - Highest gross return per trade was 29 bps (5-day lookback, 4-weekly rebalance). That is below the author's ~25 to 30+ bps round-trip estimate for cash delivery, yet the author says "only longest-horizon configurations survive" at 30 bps.
  - The data source is not named and point-in-time constituents are not stated, so survivorship bias is likely.
  — [Delphic Alpha](https://delphicalpha.substack.com/p/does-mean-reversion-work-on-the-nifty)
- Same source, Indian round-trip cost estimates:
  - Cash delivery: ~22 bps statutory, 25 to 30+ bps all-in.
  - Cash intraday: ~4 bps.
  - Single-stock futures: ~7 bps, with futures STT on sell raised to 0.05% from Apr 2026.
  — [Delphic Alpha](https://delphicalpha.substack.com/p/does-mean-reversion-work-on-the-nifty)
- Academic: Chui, Ranganathan, Rohit & Veeraraghavan (2023, *Pacific-Basin Finance Journal*) studied 3,956 BSE stocks from 2000 to 2021. They found short- and intermediate-term reversals concentrated in the **most illiquid** portfolios, which are the opposite of large-cap index constituents. — [IDEAS/RePEc listing](https://ideas.repec.org/a/eee/pacfin/v82y2023ics0927538x23002640.html)
- Academic: Parthasarathy & Sendilvelu (2022, *Economic Thought Journal*) report significant reversals after large price moves in large, liquid Indian stocks, at horizons up to six months. This is event-study evidence, not a tradable daily rule. — [ETJ article](https://ethj.iki.bas.bg/etj/article/view/1235)
- Academic: Tripathi & Aggarwal (2015, *IJFM*) document intraday reversal within minutes of extreme moves. — [Publishing India](https://publishingindia.com/archive/ijfm/prior-return-effect-in-indian-stock-market-an-intra-day-analysis)
- Academic: an NSE research paper describes overreaction-led short-run momentum and long-run contrarian profits. Author and date were not visible in the snippet. — [NSE research paper](https://nsearchives.nseindia.com/content/research/res_paperfinal223.pdf)
- Zerodha's "In The Money" (episode referenced 16 Jan 2026) backtested a long-only Bollinger-Band mean reversion on Nifty and Gold. **The results were not visible on the page reviewed.** — [Zerodha Aftermarket Report](https://aftermarketreport.zerodha.com/p/nifty-lacks-follow-through-broader)
- Marketcalls ran an hourly Nifty-futures RSI **momentum** test (2011 to 2018): buy when RSI crosses above 65, exit below 40, 0.03% costs. It reported ~16.25% CAGR, 120 trades and Sharpe 1.38. This is a momentum rule, not mean reversion, and comes from a vendor/educator. — [Marketcalls RSI momentum](https://www.marketcalls.in/amibroker/rsi-momentum-trading-strategy-do-simple-trading-strategies-really-work-part3.html)

### Inferences
- The best available prior for an RSI(2)-style rule on Nifty/NIFTYBEES is roughly 8 to 12 trades/yr, ~70 to 80% win rate, +0.4 to 0.8% average trade gross, 10 to 30% exposure, and CAGR well below buy-and-hold with much lower drawdown. Treat this as a hypothesis to test, not a finding: it is extrapolated from SPY, and Nifty volatility and trend structure differ.
- Low exposure (~11%) is the main reason CAGR lags. The fair comparison is risk-adjusted return, or the rule plus interest on idle cash (e.g., a liquid ETF), not raw CAGR.
- **Cost viability by instrument (my computation from the Groww tariffs in section 2; verify before use):**
  - **NIFTYBEES on Groww, ₹1,00,000 delivery round trip:**
    - Brokerage ₹20+₹20, plus 18% GST ≈ ₹47.
    - STT 0.001% on sell ≈ ₹1.
    - Stamp 0.015% on buy ≈ ₹15.
    - Exchange charges ~0.003% × 2 ≈ ₹6, plus GST.
    - DP ₹16.5 + ₹3.5, plus GST ≈ ₹23.6.
    - Total ≈ ₹93 ≈ **~0.09% round trip, plus bid-ask spread**.
  - **A Nifty stock, same size:** STT 0.1% on each side adds ₹200, so ≈ **~0.29% round trip**.
  - On a +0.5% average trade, the ETF keeps ~80% of the gross edge. A single-stock version keeps only ~40%, and less once spread and slippage are added.
  - Fixed charges (₹20 brokerage, ~₹23.6 DP) bite hard at small sizes. At ₹10,000 per trade the ETF round trip rises to roughly 0.6 to 0.7%, which would erase a typical RSI(2) edge.
- The Delphic Alpha annual Sharpe turning negative in 2025 and 2026 YTD hints at decay in the cross-sectional effect. That matches the US post-publication decay. One source is not enough to confirm it.
- Buy-the-dip with a 200-DMA filter will sit out long Indian bear phases (2008, 2020). That limits drawdown but also cuts trade count, which makes statistical significance harder to reach (see section 5).

### Gaps
- No published Nifty 50, Bank Nifty or NIFTYBEES backtest of RSI(2), IBS, N-down-days or 200-DMA buy-the-dip with stated methodology and costs was found. Searched Marketcalls, Capitalmind, Zerodha and Quantpedia-type sources. Capitalmind had nothing indexed on this.
- No India-specific evidence on post-2010 decay of index-level short-term reversal.
- Bank Nifty: no evidence at all, neither ETF (e.g., BANKBEES) nor index.
- Indian short-term capital gains tax (STCG, believed 20% since Jul 2024 for listed equity/equity ETFs) materially reduces the net return of high-turnover strategies. It was not verified with a primary source in this session.

## 2. Index ETF practicalities on NSE (NIFTYBEES and peers): expense ratio, tracking error, liquidity, and Groww charges

### Takeaway
NIFTYBEES has a ~0.04% expense ratio (secondary sources, 2026). NAV-based tracking error is small, but price-based tracking error can be much larger. The key cost advantage for a swing trader is STT: on Groww, delivery/BTST sales of equity ETFs pay **0.001% STT on the sell side only**, against **0.1% on both sides** for equity shares. Brokerage, stamp, DP and exchange charges are the same as for stocks.

### Cited Findings
- NIFTYBEES total expense ratio is 0.04%, per a 2026-dated overview citing 11 Sep 2026 and a March 2026 snapshot. Both are secondary; the AMC factsheet was not retrieved. — [Multibagg (2026)](https://www.multibagg.ai/feeds/what-is-nifty-bees-cmu2ie23200000agm5z2ukhpw); [OneTradeJournal](https://onetradejournal.com/learn/what-is-nifty-bees)
- Tickertape lists NIFTYBEES tracking error at ~0.02% (garbled labels, period not stated). Another snapshot says "<0.05%". — [Tickertape](https://tickertape.in/etfs/nippon-india-nifty-50-bees-etf-NBES)
- Freefincal (2020) found NAV-based tracking error of 0.16% for May 2019 to Apr 2020, but **5.6% using traded price**. Investors transact with other unitholders, not at NAV. — [Freefincal](https://freefincal.com/nippon-india-etf-nifty-bees-vs-uti-nifty-index-fund-which-is-better/)
- Groww STT for ETFs (Groww help page; Gold, Liquid, Gilt and some international ETFs are exempt):
  - Delivery and BTST: 0.001% on sell orders only.
  - Intraday: 0.025% on sell orders only.
  - For comparison, equity delivery STT is 0.1% on both buy and sell.
  — [Groww help: What is STT](https://groww.in/help/stocks,-f&o,-ipo-&-mtf/sx-pricing/what-is-stt)
- Groww STT blog (11 Feb 2026): STT on sale of equity-oriented fund units in delivery is 0.001% (seller), with no STT on purchase. The Budget 2026 changes (effective 1 Apr 2026) affected only derivatives (futures 0.02%→0.05%, options 0.1%→0.15%). — [Groww blog: STT](https://groww.in/blog/what-is-stt)
- Other Groww charges:
  - Delivery brokerage: lower of ₹20 or 0.1% per executed order.
  - DP charges: ₹16.5 per sell transaction plus ₹3.5 depository fee (₹3.25 for women).
  - Stamp duty: 0.015% on buys.
  - NSE exchange charges: 0.00297% (help page) vs 0.00345% (pricing page/third parties), so the sources conflict.
  - GST: 18% on brokerage, DP and exchange charges.
  — [Groww help: charges in report](https://groww.in/help/stocks,-f&o,-ipo-&-mtf/discoverable/what-are-the-different-charges-mentioned-in-the-report); [Groww pricing](https://groww.in/pricing/stocks); [StockCalc Groww calculator](https://stockcalc.in/calculator/groww-brokerage)
- One third-party calculator lists 0.05% brokerage, which conflicts with Groww's 0.1%/₹20 cap. Use Groww's own page. — [StockCalc](https://stockcalc.in/calculator/brokerage/groww)
- ETF premiums can detach from NAV when creation is blocked. A blog cites an NSE release (25 Sep 2026) warning about international ETFs trading at large premiums after overseas limits were exhausted. This affects international ETFs, not Nifty ETFs. — [Belong blog](https://getbelong.com/blog/us-stocks-etfs/why-etfs-trade-at-premium-or-discount/)

### Inferences
- For a daily-bar Nifty mean-reversion rule, NIFTYBEES (or another liquid Nifty 50 ETF) is far cheaper to trade than a basket of stocks because of the 100x lower STT. ETF trading is the cost-viable implementation for a Groww retail account.
- Price-based tracking error (Freefincal's 5.6%) means a backtest on the ^NSEI index can differ materially from actually trading NIFTYBEES. The backtest should use NIFTYBEES.NS prices directly, or at least validate against them. Note also that NIFTYBEES had a unit split/consolidation history, which needs checking in the Yahoo series.
- Other Nifty 50 ETFs (SBI, UTI, ICICI, HDFC, etc.) exist with similarly low TERs. NIFTYBEES is typically cited as the most traded, but I did not obtain comparative volume or spread data.

### Gaps
- No current (Oct 2026) AMC factsheet values for NIFTYBEES TER and tracking error were retrieved, nor for competing Nifty 50 ETFs.
- No quantitative bid-ask spread, impact cost or iNAV premium/discount data for NIFTYBEES or other Nifty ETFs was found.
- SEBI market-maker obligations for Indian ETFs were not retrieved.

## 3. Survivorship bias in Indian stock backtests: size, historical constituents, effect on momentum

### Takeaway
Survivorship bias in India is material. The only quantified recent estimate (Mar 2026, a non-peer-reviewed arXiv paper, small caps) finds survivor-only backtests overstate annual returns by ~4.9 percentage points. Free point-in-time constituent data for Nifty indices is patchy:
- NSE's inclusion/exclusion file (reportedly to Jul 2020).
- niftyindices monthly constituent zips (Apr 2013 to Mar 2022).
- Index change announcements and monthly weight reports after that.

Reconstruction is possible but laborious, and the burden falls on the backtester.

### Cited Findings
- Ranse, "Survivorship Bias in Emerging Market Small-Cap Indices: Evidence from India's NIFTY Smallcap 250" (arXiv:2603.19380, 19 Mar 2026, single author, not peer-reviewed):
  - Data: 1,437 stocks, 2016 to 2025.
  - Survivor-only equal-weight backtests overstate annual return by **4.94 pp (23.3% relative)** and Sharpe by **0.097 (9.1%)**.
  - Index turnover was 82.5% over the period: 16.1% delisted, 33.1% graduated, 33.2% demoted.
  - Membership was reconstructed from bhavcopy data that includes delisted securities. Accuracy: 100% for current constituents, ~85 to 90% historically.
  — [arXiv 2603.19380](https://arxiv.org/abs/2603.19380)
- Marketcalls (30 Aug 2026) gives a method for building point-in-time Nifty 50 history:
  - Start from the current list and walk back through NSE Indices addition/deletion announcements.
  - Attach monthly "Market Capitalisation, Weightage and Beta for NIFTY 50 & NIFTY Next 50" reports.
  - Align effective dates.
  - Validate constituent counts, weight sums, and ISIN continuity across ticker changes (e.g., Zomato→Eternal).
  - Handle ad-hoc changes outside the March/September reviews.
  - Former members it lists include Yes Bank, Zee, Cairn India, Idea, Vedanta, PNB and HDFC Ltd.
  - It does **not** quantify the bias, and it warns that using current weights with historical membership still leaks future information.
  — [Marketcalls](https://www.marketcalls.in/llm-models/how-to-build-survivorship-bias-free-nifty-50-historical-data-using-grokbot.html)
- Free sources (TradingQnA thread, 2016 to Oct 2026):
  - NSE `IndexInclExcl.xls` (archives.nseindia.com/content/indices/IndexInclExcl.xls): inclusion/exclusion dates. Reportedly runs only to 31 Jul 2020 and gives company names rather than symbols, though one poster disagrees.
  - niftyindices monthly constituent zips (`indices_dataMar2022.zip` style URLs): Apr 2013 to Mar 2022.
  - After Apr 2022, reportedly only F&O-index constituents (e.g., Nifty 50) are available.
  - niftyindices historical-data reports: monthly market-cap archives.
  - Commercial vendors (e.g., Accelpix) were suggested.
  — [TradingQnA: historical composition of Nifty indices](https://tradingqna.com/t/where-can-i-find-historical-composition-of-nifty-indices/7163)
- One summary estimates the Nifty 50 membership "half-life" at ~5 to 6 years. That came from a search-result summary, and I could not trace the primary source. — [share.market backtesting article](https://www.share.market/buzz/futures-and-options/backtesting-trading-strategies-in-india/) (unverified attribution)

### Inferences
- For a **single-index ETF strategy** (NIFTYBEES/^NSEI), constituent survivorship bias does not apply, because the index itself contains its historical members. That is a strong argument for testing index-level mean reversion on the ETF or index first.
- For a **momentum strategy on today's Nifty 50/100/200**, the bias is plausibly upward and possibly large:
  - Today's members are disproportionately past winners (e.g., Trent, Eternal, Jio Financial joined after big runs).
  - Today's list leaves out laggards that were dropped (Yes Bank, Vedanta, Zee).
  - Momentum picks recent winners, so a current-constituent universe effectively pre-selects stocks that went on to keep winning.
  - Ranse's ~5 pp/yr small-cap figure is likely an upper bound for Nifty 50. For Nifty 100/200 the effect is probably smaller than small caps but not negligible. No direct large-cap India estimate was found.
- Mergers and demergers (HDFC Ltd into HDFC Bank, Jul 2023) create both survivorship and price-adjustment problems at once.

### Gaps
- No quantified survivorship-bias estimate for Nifty 50/100/200 or for a momentum strategy specifically.
- I did not verify whether niftyindices.com currently publishes complete historical constituent files for Nifty 100/200 after Mar 2022, nor whether the NSE IndexInclExcl.xls URL is still live.

## 4. Yahoo Finance (yfinance) data quality for NSE ".NS" tickers, and alternatives

### Takeaway
yfinance is usable for a first pass on index/ETF data but unreliable for Indian single-stock corporate actions:
- Known complaints cover demergers (HDFC Bank), bonus issues, splits and dividend values that don't match NSE.
- Delisted tickers are generally unavailable.
- Defaults changed: `auto_adjust=True` now returns adjusted prices in the "Close" column.

Alternatives (NSE bhavcopy via jugaad-data, nsepython, EOD2) scrape NSE endpoints that change and rate-limit without notice. NSE's terms of use for bulk or commercial reuse were not confirmed.

### Cited Findings
- yfinance `download()` docs:
  - `auto_adjust` defaults to `True` (adjusts all OHLC).
  - `repair=False` by default; when on, it fixes 100x currency-unit mix-ups.
  - `actions=False` by default (dividends and splits are not returned unless requested).
  - `back_adjust` exists but is undocumented on that page.
  — [yfinance download reference](https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html)
- yfinance switched to returning adjusted prices by default, labelled "Close" rather than "Adj Close". `auto_adjust=False` returns both raw and adjusted columns. — [Kerry Back, "Online Data"](https://kerryback.substack.com/p/02-online-data)
- TradingQnA (4 Apr 2026): an algo trader reports that yfinance mishandled the **HDFCBANK demerger**, producing "completely wrong returns" over ~2 years of backtest. Splits, bonuses and rights issues were also named as problem events. The thread found no free source with reliable corporate-action adjustment. — [TradingQnA](https://tradingqna.com/t/has-anyone-found-wrong-adjusted-prices-in-nse-historical-data-for-backtesting/192938)
- Quantra forum: yfinance dividend values for Reliance on some dates did not match NSE announcements. A reply says yfinance Indian data can be "missing, outdated, or adjusted" inconsistently with NSE, and recommends checking corporate actions against NSE. — [Quantra community](https://quantra.quantinsti.com/community/t/corporate-actions/26346)
- yfinance issue #2621 reports missing price history for 5 Nov 2025 across many tickers. It appears to be Yahoo server-side, also visible on Yahoo's website. — [yfinance #2621](https://github.com/ranaroussi/yfinance/issues/2621)
- Ticker suffix: append `.NS` for NSE and `.BO` for BSE. Wrapper libraries "may not always function as expected". — [Quantra NSEpy thread](https://quantra.quantinsti.com/community/t/nsepy-library/26341)
- Broker data is often split/bonus-adjusted but **not dividend-adjusted**. For example, Zerodha Kite historical data adjusts only for splits and bonuses. — [Kite forum](https://kite.trade/forum/discussion/comment/21017)
- EOD2 (open-source, BennyThadikaran) stores NSE EOD CSVs adjusted for splits and bonuses. It notes data before 2005 may not be fully adjusted because NSE provides no adjustment data before 2005. — [EOD2 GitHub](https://github.com/BennyThadikaran/eod2)
- jugaad-data downloads historical/live data from NSE's website with caching "to play nice with NSE". It warns that libraries built on the old NSE site may stop working. — [jugaad-data PyPI](https://pypi.org/project/jugaad-data)
- nsefin notes NSE may cap history responses (~70 rows) and that public endpoints change without notice. bhavkit warns of rate-limiting and recommends sleeps and incremental updates. — [nsefin PyPI](https://pypi.org/project/nsefin/); [bhavkit PyPI](https://pypi.org/project/bhavkit/)
- Historical Nifty index data has been available from 1995 via data aggregators (e.g., the former Quandl NSE/CNX_NIFTY dataset). — [TradingQnA thread](https://tradingqna.com/t/where-can-i-find-historical-composition-of-nifty-indices/7163)

### Inferences
- **Practical recipe:**
  - Pull `auto_adjust=False, actions=True` so raw and adjusted columns plus the action log are all available.
  - Compute signals on adjusted series; compute position sizing and fills on raw prices.
  - Cross-check every split, bonus and demerger against NSE corporate-action records or bhavcopy price jumps. Flag any daily return beyond ±20% for an index/ETF, or beyond the circuit limit for a stock.
  - Diff against NSE bhavcopy for a sample of dates.
- For NIFTYBEES and ^NSEI, corporate-action risk is lower than for stocks. Still check NIFTYBEES unit splits and dividend history, since the ETF paid dividends in earlier years.
- **Benchmark:** Yahoo's ^NSEI is the price index, not the Total Return Index. The Nifty 50 TRI should come from niftyindices.com historical data. Comparing a strategy to the price index understates buy-and-hold by roughly the dividend yield (~1.2 to 1.5%/yr, approximate, not verified here).
- Delisted or renamed tickers (e.g., ZOMATO→ETERNAL) can break yfinance histories. Key all data on ISIN, not symbol.

### Gaps
- How far back daily `.NS` data goes on Yahoo (commonly said to be ~1996 to 2002 for large caps and ~2007 for ^NSEI) was not verified.
- No authoritative statement of NSE's terms of use or licensing for bhavcopy, nsepython or jugaad-data scraped data was found. Commercial redistribution likely needs an NSE data licence (unverified).
- No direct GitHub issue documenting systematic `.NS` adjustment bugs was found. The evidence is forum anecdotes.

## 5. Best practices: walk-forward/out-of-sample testing, look-ahead (close vs next open), minimum trades, Nifty 50 TRI benchmark

### Takeaway
Credible daily-bar testing for this use case means:
- Signals computed on the close and executed at the **next open**, or at the same close only if the signal can be computed before the close.
- Explicit Indian costs per trade (section 2).
- Point-in-time universes for stock strategies.
- Parameters chosen on in-sample data and evaluated walk-forward.
- Overfitting checks (deflated Sharpe, PBO, random-entry tests).
- A Nifty 50 TRI benchmark with cash interest on idle capital.

Sparse mean-reversion rules produce few trades (~8 to 12/yr), so statistical confidence is limited even over 15+ years.

### Cited Findings
- The Empirica Lab RSI(2) note shows a credible validation stack:
  - Parameter grid around the published values (15 variants).
  - Deflated Sharpe ratio and probability of backtest overfitting.
  - 2,000 random-entry runs (none matched).
  - Bootstrap 95% intervals: win rate 72 to 82%, Sharpe 0.53 to 1.11.
  - A pre/post-publication split as an out-of-sample test.
  - Cross-instrument check on five other ETFs.
  - A scorecard that fails the strategy on Sharpe, drawdown and worst day despite the 77% win rate.
  — [Empirica Lab](https://empiricalab.substack.com/p/connors-rsi2-spy)
- Same source: closing-price fills are optimistic because RSI(2) is only final at the close, and cash was assumed to earn nothing. The 265-trade count fell just short of its own 300-trade adequacy criterion. — [Empirica Lab](https://empiricalab.substack.com/p/connors-rsi2-spy)
- Look-ahead in universe construction: membership changes must not appear before their effective dates, and current index weights must not be applied historically. — [Marketcalls (Aug 2026)](https://www.marketcalls.in/llm-models/how-to-build-survivorship-bias-free-nifty-50-historical-data-using-grokbot.html)
- The Delphic Alpha test used open-to-close returns and reported per-year Sharpe, which exposed 2025 and 2026 deterioration that an aggregate Sharpe would hide. It reported only gross results, which is a known weakness. — [Delphic Alpha](https://delphicalpha.substack.com/p/does-mean-reversion-work-on-the-nifty)
- Marketcalls' hourly Nifty RSI test included 0.03% commissions plus slippage. This is an example of Indian practitioners stating cost assumptions explicitly. — [Marketcalls](https://www.marketcalls.in/amibroker/rsi-momentum-trading-strategy-do-simple-trading-strategies-really-work-part3.html)

### Inferences
- **Execution timing:** with daily Yahoo bars, the safe default is "signal on close t, fill at open t+1". A same-close fill is defensible only if the signal is computed from a 15:25 price and an order is placed in the closing session. Run both and report the gap; for mean reversion the overnight gap often carries much of the edge.
- **Trade count:** at ~10 trades/yr, a 2007 to 2026 Nifty sample gives ~150 to 200 trades. That is enough to estimate win rate (±~6 to 7 pp at 95%) but weak for average trade or Sharpe. Report bootstrap confidence intervals, not point estimates.
- **Walk-forward:** pick RSI length and threshold and the exit rule on, say, 2007 to 2016, then freeze them and test 2017 to 2026. Better, use rolling 5-year train / 1-year test windows. Prefer parameter plateaus over peaks, as in Empirica's grid where all variants were positive.
- **Benchmark:** compare against Nifty 50 TRI buy-and-hold, and against "rule + liquid-fund/overnight rate on idle cash". Report CAGR, Sharpe, max drawdown, exposure and return per unit of exposure, as Empirica does. Include taxes (STCG on every winning round trip vs LTCG on buy-and-hold) for an after-tax view, because that comparison can flip the conclusion for Indian retail.
- **Data sanity:** run the same rules on ^NSEI (index) and NIFTYBEES.NS (tradable) and reconcile the differences. Treat any result that holds only on the index as untradable.

### Gaps
- No India-specific academic or practitioner guidance on minimum trade counts or walk-forward window lengths was found. The recommendations above are general practice, not India-sourced.
- No source quantified the close-vs-next-open fill difference for Nifty mean-reversion rules.
