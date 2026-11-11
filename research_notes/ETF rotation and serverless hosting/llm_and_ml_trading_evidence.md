# LLM, news-sentiment and ML price-prediction evidence for a small Indian retail bot (2023 to Nov 2026)

Research date: 11 Nov 2026. Perspective: Rs 1-20 lakh, NSE cash equities via Groww API, personal bot.

**One-paragraph verdict (for the report writer):** The evidence does not support "a profitable intraday LLM-powered, ML-powered trading application" at retail scale. Every strong LLM/ML return number found is a pre-cost or low-cost backtest; the authors of the best-known LLM paper themselves say the effect is only exploitable by participants with market-maker-level costs, and its Sharpe fell every year of the sample. Live LLM trading tests (2025-26) are short, mostly paper-traded, mostly cost-free, and show no reliable edge over buy-and-hold; the one real-money contest saw four of six frontier models lose money. No credible India-specific evidence of retail-scale intraday ML or news-sentiment profit after costs was found. The only India-specific test of "ML ranker vs plain 12-1 momentum" found (unreviewed, single author) says the ML ranker does not win after costs. The defensible role for an LLM is a logged, veto-only reviewer/explainer on a once-a-day rules-based rebalance, where API cost is a few US cents per decision.

**Evidence labels used below:** [BACKTEST] = historical simulation; [LIVE-PAPER] = live prices, simulated fills; [LIVE-REAL] = real money; [FUND] = audited fund/index track record.

**Source-access caveat:** In this session these hosts could not be fetched directly, so claims from them rest on search-result snippets only and are flagged "(snippet only)": papers.ssrn.com, www.nber.org, forklog.com, briefs.co, traderank.ai, iweaver.ai, aurpay.net, marketscreener.com, ar5iv.labs.arxiv.org. Figures extracted from long arXiv HTML pages were read by an automated summariser over the first ~100k characters; verify exact table values against the PDFs before quoting to the decimal.

---

## 1. LLM stock-return prediction papers: what survives look-ahead/memorisation controls and costs?

### Takeaway
The headline paper (Lopez-Lira & Tang) is a genuine post-training-cutoff result, but it is a daily long-short US backtest whose Sharpe decays from 6.54 (2021Q4) to 1.22 (Jan-May 2024), is concentrated in small caps and negative news, turns unprofitable at 20 bps round-trip cost, and which the authors say is only feasible for market-maker-cost participants. The look-ahead/memorisation literature (Glasserman-Lin, Sarkar-Vafa, Levy, Lopez-Lira-Tang-Zhu) shows any LLM "forecast" on dates before the model's knowledge cutoff is uninterpretable, and that prompts and name-masking do not fix it.

### Cited Findings

**Lopez-Lira & Tang, "Can ChatGPT Forecast Stock Price Movements?" (arXiv 2304.07619; v6 dated Oct 2025) [BACKTEST, post-cutoff]**
- Sample is October 2021 to May 2024; the paper states the model's training data "stops in September 2021", so the test is out-of-sample with respect to the model's knowledge. — [arXiv v6 HTML](https://arxiv.org/html/2304.07619v6)
- Long-short "drift" strategy annualised Sharpe: GPT-4 2.97 (overnight-news entry) and 2.63 (intraday entry); GPT-3.5 1.66; DistilBART-MNLI 1.26; BART-large 1.05; Llama2-70b 0.97; basic models (GPT-1, GPT-2, BERT) negative. All before costs. — [arXiv v6 HTML](https://arxiv.org/html/2304.07619v6)
- Earlier versions quoted higher numbers on a shorter sample (Sharpe 3.8 for GPT-4, 3.1 for GPT-3.5; cumulative return 350% at 10 bps and 50% at 25 bps per trade). The numbers moved down as the sample lengthened; cite the version. — [arXiv v5 PDF](https://arxiv.org/pdf/2304.07619v5.pdf)
- Decay over time (v6): annualised Sharpe 6.54 in 2021Q4, 3.68 in 2022, 2.33 in 2023, 1.22 in January-May 2024. The abstract says "Strategy returns decline as LLM adoption rises, consistent with improved price efficiency"; the introduction calls this "suggestive evidence", not a causal finding. — [arXiv v6 HTML](https://arxiv.org/html/2304.07619v6)
- Costs (v6): at 5 bps round-trip cumulative return stays above 300%; at 10 bps above 100% (Sharpe about 1.29 with full daily rebalancing, 1.34 with 25% partial rebalancing); at 20 bps the strategy is unprofitable. — [arXiv v6 HTML](https://arxiv.org/html/2304.07619v6)
- Size: predictability is "more pronounced among smaller stocks" and for negative news; small-firm interaction coefficient 0.404 (t=4.75) against a base coefficient of 0.087 (t=4.09). Excluding stocks at or below $5 and below the 20th NYSE size percentile still leaves >300% cumulative pre-cost return. — [arXiv v6 HTML](https://arxiv.org/html/2304.07619v6)
- Who can exploit it: the paper says exploiting these patterns is "only feasible for market participants whose transaction costs are sufficiently low", naming market makers. — [arXiv v6 HTML](https://arxiv.org/html/2304.07619v6)
- Intraday detail: returns in the first 1-15 minutes after an intraday news release are statistically insignificant for the signal; from 15 minutes post-release to the close the coefficient is 0.189 (t=5.12), described as about a 30 bps return for entering 15 minutes post-release (pre-cost, US stocks). — [arXiv v6 HTML](https://arxiv.org/html/2304.07619v6)

**Chen, Kelly & Xiu, "Expected Returns and Large Language Models" (SSRN 4416687, first posted Nov 2022) [BACKTEST]**
- Uses LLM embeddings of news text (not chat prompts) to predict returns; covers 16 international equity markets and news in 13 languages; finds LLM representations beat word-count sentiment models and that "returns respond slowly to news". — [Oxford NLP-EcoFin listing](https://nlpecofin.web.ox.ac.uk/node/3041271); [Wharton Jacobs Levy discussion slides, Sept 2024](https://jacobslevycenter.wharton.upenn.edu/wp-content/uploads/2024/09/ExpectedReturnAndLLM_Discussion_SophiaZhengziLi_NoPause.pdf)

**Glasserman & Lin, "Assessing Look-Ahead Bias in Stock Return Predictions Generated By GPT Sentiment Analysis" (arXiv 2309.17322, Sept 2023) [BACKTEST]**
- In-sample period Jan 2015-Sep 2021 (inside GPT-3.5's training window), out-of-sample Oct 2021-Dec 2022. Anonymising company names in headlines gave higher in-sample returns than original headlines, which the authors attribute to a "distraction effect" (the model's general knowledge of a company hurts) outweighing look-ahead bias; the effect is strongest for large companies. Out-of-sample the difference loses statistical significance. — [arXiv 2309.17322](https://arxiv.org/abs/2309.17322)

**Sarkar & Vafa, "Lookahead Bias in Pretrained Language Models" (NBER conference paper June 2024; ICML 2025)**
- Build statistical tests showing lookahead bias in two applications (predicting risk factors from earnings calls; predicting election winners from biographies); argue prompting-based fixes are limited and only models trained solely on pre-period data avoid the problem. — [NBER conference PDF](https://conference.nber.org/conf_papers/f205530/f205530.pdf); [ICML 2025 page](https://icml.cc/virtual/2025/48685)

**Levy, "Caution Ahead: Numerical Reasoning and Look-ahead Bias in AI Models" (Chicago Booth working paper, Dec 2024/2025 listing)**
- Two findings: LLMs show weak numerical reasoning, and commercial LLMs carry significant look-ahead bias that "may account for a large share" of apparent predictive power in accounting/finance tasks. — [Chicago Booth Fama-Miller working paper page](https://www.chicagobooth.edu/research/fama-miller/finance-research/working-papers/2025/caution-ahead)

**Lopez-Lira, Tang & Zhu, "The Memorization Problem: Can We Trust LLMs' Economic Forecasts?" (arXiv 2504.14765; v2 Dec 2025)**
- GPT-4o recalls pre-cutoff daily S&P 500 levels with mean absolute percent error 0.61% (DJIA 0.53%, Nasdaq 1.80%) and ~80.6% directional accuracy; monthly S&P direction 82.8% correct. After the cutoff (Oct 2023 onward) S&P error rises to 16.87% and directional accuracy falls to 45.7%. — [arXiv 2504.14765v2](https://arxiv.org/html/2504.14765v2)
- Telling the model to pretend its knowledge stops earlier does not work ("prompts cannot change what information is encoded in the model's parameters"); masking firm names does not work either: GPT-4o identified the company in 100% of masked Apple/Meta/Microsoft earnings calls and >85% for all Magnificent 7, and the correct quarter for Apple 93.2% of the time. — [arXiv 2504.14765v2](https://arxiv.org/html/2504.14765v2)
- Authors' rule: only testing on periods the model has not been exposed to separates forecasting from memorisation; they caution their own post-cutoff samples are small. — [arXiv 2504.14765v2](https://arxiv.org/html/2504.14765v2)

**2025-26 follow-ups on decay / pricing-in**
- "Buy the Rumor, Sell the News: When Is News Priced In?" (arXiv 2608.14014, Aug 2026; 4.57 million articles, ~3,000 US stocks, 2023-2026; ICAIF 2026 workshop): by the close of publication day the cumulative move in the news direction is 2.8 times its value twenty days later; fundamental news (earnings, guidance, dividends, analyst actions) keeps drifting for weeks relative to comparable stocks, while soft story-driven news gives its move back. The paper presents no trading strategy or cost analysis. — [arXiv 2608.14014](https://arxiv.org/abs/2608.14014)
- "ChatGPT as a Time Capsule: The Limits of Price Discovery" (arXiv 2604.21433, 2026) argues predictability from pre-cutoff text may reflect information the LLM absorbed from the later record rather than a market inefficiency (snippet-level reading only). — [arXiv 2604.21433](https://arxiv.org/html/2604.21433v1)
- "Detecting Lookahead Bias in LLM Forecasts" (arXiv 2512.23847, Dec 2025) is a further methods paper on the same problem (not read in full). — [arXiv 2512.23847](https://arxiv.org/pdf/2512.23847)

### Inferences
- What survives look-ahead controls: a modest, decaying, post-cutoff, small-cap-heavy US overnight/next-day drift after firm news, measured before realistic costs. What survives costs for a retail account: by the authors' own table, nothing at 20 bps round-trip. The existing Thunderbot report puts an Indian delivery round trip at about 0.3% (30 bps) before impact, i.e. above the level at which the US strategy is already dead.
- The 1.22 Sharpe for Jan-May 2024 is the last data point found; there is no published evidence in this search that the effect persisted, at any Sharpe, into 2025-2026.
- Any backtest the owner runs by asking a 2026 LLM about 2020-2025 Indian news is contaminated by construction (Memorization Problem); only forward, live, logged tests are informative.
- A long-short daily strategy on small caps is not implementable in NSE cash equities by a retail account anyway (no overnight shorting in cash; small-cap impact costs), so even the gross result does not map onto the owner's setting.

### Gaps
- Chen-Kelly-Xiu Sharpe ratios, cost treatment and whether India is among the 16 markets: SSRN page could not be fetched; not verified.
- No peer-reviewed paper found that tests LLM news-sentiment alpha specifically on 2025-2026 data after costs. The "decay with adoption" claim rests on Lopez-Lira & Tang's own year-by-year Sharpe (suggestive, not causal).
- Levy's exact quantitative results (how much predictive power disappears) were not extracted.

---

## 2. LIVE (not backtest) evidence 2024-2026: Alpha Arena, benchmarks, AI funds

### Takeaway
Live evidence is thin, short-horizon and unflattering: in the only widely reported real-money contest, four of six frontier LLMs lost money in 17 days (two lost more than half), and its equities follow-up reportedly saw only 6 of 32 result sets finish positive. Academic "live" benchmarks run 50-82 trading days, ignore transaction costs, and still show LLM agents roughly indistinguishable from buy-and-hold; over 20 years with a bias-controlled universe (FINSABER), LLM agents significantly underperform buy-and-hold. AI-run funds with real track records (AIEQ, Eurekahedge AI index, NBER hedge-fund study) lag the S&P 500 or show an edge that faded after 2017.

### Cited Findings

**Alpha Arena (nof1.ai) Season 1 [LIVE-REAL, crypto perpetuals, 17 days]**
- Ran about 17/18 October to 3 November 2025; six models each given US$10,000 of real money: Qwen3 Max, DeepSeek Chat V3.1, GPT-5, Gemini 2.5 Pro, Grok 4, Claude Sonnet 4.5. — [ForkLog](https://forklog.com/en/four-out-of-six-ai-models-suffer-losses-in-trading-tournament/) (snippet only)
- Final results reported: Qwen3 Max +22.32% (winner), DeepSeek V3.1 about +4.89%, Gemini 2.5 Pro about -56.71%, GPT-5 about -62.66%; four of six models finished with losses. — [ForkLog](https://forklog.com/en/four-out-of-six-ai-models-suffer-losses-in-trading-tournament/); [Aurpay summary table](https://aurpay.net/?p=23782) (both snippet only)
- nof1 itself described the season as exploratory: short duration, modest capital and no statistical controls mean the figures are not a definitive ranking of trading ability. — [ForkLog](https://forklog.com/en/four-out-of-six-ai-models-suffer-losses-in-trading-tournament/) (snippet only)
- Mid-season coverage had Grok, DeepSeek and Claude "posting serious gains" before the final losses for Grok and Claude, illustrating how unstable the ranking was within a fortnight. — [Decrypt via Yahoo Finance](https://finance.yahoo.com/news/ai-crypto-trading-showdown-deepseek-202512124.html)

**Alpha Arena Season 1.5 [LIVE-REAL, US equities, 2 weeks]**
- Ran 19 November to 3 December 2025 on US equities with eight models across four parallel competition modes, US$10,000 each. Winner was a "Mystery Model" later identified as Grok 4.20, with a 12.11% aggregate return (other outlets report different figures for the same result). — [ForkLog](https://forklog.com/en/ai-model-grok-4-2-triumphs-in-trading-tournament/); [Traderank leaderboard recap](https://www.traderank.ai/alpha-arena-leaderboard) (snippet only)
- One report states that across the eight models and four two-week contests the overall portfolio fell about one third and only 6 of 32 result sets finished positive. — [Briefs.co](https://briefs.co/news/public-ai-trading-contests-largely-lose-money-and-raise-new) (snippet only; secondary source, not verified against nof1)
- As of a check dated August 2026, nof1.ai still showed Season 1.5 with models no longer running and no Season 2 roster or leaderboard published. — [Traderank leaderboard recap](https://www.traderank.ai/alpha-arena-leaderboard) (snippet only; confirmed only as of Aug 2026)

**FINSABER (Li, Kim, Cucuringu, Ma; arXiv 2505.07078, v4 Nov 2025) [BACKTEST, 20 years, bias-controlled]**
- Re-tests published LLM trading agents (FinMem, FinAgent) on 2004-2024 with historical S&P 500 constituents including delisted names. Quote: "previously reported LLM advantages deteriorate significantly under broader cross-section and over a longer-term evaluation." — [arXiv 2505.07078v4](https://arxiv.org/html/2505.07078v4)
- Composite setup, Sharpe (annualised return): Random-Five selection: buy-and-hold 0.315 (6.7%), FinMem -0.253 (-0.1%), FinAgent 0.094 (4.5%). Momentum selection: buy-and-hold 0.384 (9.9%), FinMem 0.025 (3.6%), FinAgent 0.104 (14.0%). Paired t-tests: buy-and-hold beats FinMem (p = 3.0e-6) and FinAgent (p = 7.7e-4) under Random-Five. Neither agent has statistically significant alpha (p > 0.34). — [arXiv 2505.07078v4](https://arxiv.org/html/2505.07078v4)
- Regime result: FinAgent Sharpe 0.12 in bull years and -0.38 in bear years; FinMem -0.19 and -0.97; buy-and-hold 0.61 bull / -0.28 bear. "Both are too cautious when risk is rewarded and too aggressive when it is penalised." — [arXiv 2505.07078v4](https://arxiv.org/html/2505.07078v4)
- Costs modelled are US retail commissions only (US$0.0049/share, min US$0.99); no slippage. The paper notes its LLM results are not adjusted for data leakage (which would flatter the LLMs), and that large-scale LLM backtesting is "financially intensive". — [arXiv 2505.07078v4](https://arxiv.org/html/2505.07078v4)

**StockBench (arXiv 2510.02209, Oct 2025) [LIVE-PAPER style, post-cutoff, 82 trading days]**
- 3 March to 30 June 2025, top-20 DJIA stocks, US$100,000 start. Equal-weight buy-and-hold: +0.4% return, -15.2% max drawdown. Model returns ranged from -2.8% (GPT-OSS-20B) to +2.5% (Qwen3-235B-Think); GPT-5 +0.3%, Claude-4-Sonnet +2.2%, DeepSeek-V3.1 +1.1%. Transaction costs are not modelled. — [arXiv 2510.02209v1](https://arxiv.org/html/2510.02209v1)
- The paper is internally inconsistent: its table shows 8 of 13 models above the baseline, while the abstract says "most LLM agents struggle to outperform the simple buy-and-hold baseline". In a separate downturn window "all the LLM agents failed to outperform the passive baseline". Performance fell for almost all agents when the universe grew from 5 to 30 stocks. — [arXiv 2510.02209v1](https://arxiv.org/html/2510.02209v1); [arXiv abstract](https://arxiv.org/abs/2510.02209)

**LiveTradeBench (Yu, Li, You; arXiv 2511.03628, Nov 2025) [LIVE-PAPER, 50 trading days]**
- 18 August to 24 October 2025; 21 LLMs; 15 US stocks/ETFs plus cash, and 10 Polymarket markets. US-stock cumulative returns ranged from 1.78% (Qwen3-235B-Thinking, Sharpe 0.60) to 6.25% (GPT-4.1, Sharpe 2.64). Spearman correlation between LMArena score and US-stock return: 0.054 (Polymarket: -0.38), i.e. general model quality does not predict trading results. — [arXiv 2511.03628v1](https://arxiv.org/html/2511.03628v1)
- The evaluation does "not account for transaction fees, bid-ask spreads, liquidity constraints"; portfolios are simulated on live prices. No buy-and-hold baseline was found in the portion read. — [arXiv 2511.03628v1](https://arxiv.org/html/2511.03628v1)

**AI-Trader (HKU; arXiv 2512.10971, Dec 2025) [LIVE-PAPER]**
- Six mainstream LLMs across US stocks, A-shares and crypto at several frequencies. Abstract: "general intelligence does not automatically translate to effective trading capability"; most agents show poor returns and weak risk management. — [arXiv 2512.10971](https://arxiv.org/abs/2512.10971)

**AI-run funds with real track records [FUND]**
- AIEQ (AI Powered Equity ETF, launched Oct 2017): Amplify's own pages show since-inception NAV return of roughly 9.4-10.1% annualised (undated snapshots). — [Amplify AIEQ page](https://amplifyetfs.com/aieq/)
- An October 2025 Motley Fool review (reproduced by M1) concluded AIEQ "fails to deliver superior returns or lower risk" versus an S&P 500 ETF, has lagged the S&P 500 since inception with higher volatility, a high fee and extremely high turnover. — [M1 AIEQ page](https://pages.m1.com/invest/stocks/AIEQ)
- Since January 2024 AIEQ captured 110.97% of S&P 500 downside but only 94.13% of upside. — [PortfoliosLab AIEQ](https://portfolioslab.com/symbol/AIEQ)
- Eurekahedge AI Hedge Fund Index (10 equally weighted funds): 9.8% annualised from December 2009 through July (year not confirmed in the excerpt) versus 13.7% for the S&P 500 total return. — [WSJ-sourced chart "Can AI Beat the Market?"](https://datawrapper.dwcdn.net/B7xvB/5)
- Chen, Sialm & Xu, "The Growth and Performance of Artificial Intelligence in Asset Management" (NBER WP 35273, 2026; 7,896 US hedge funds): AI hedge funds beat non-AI funds by about 50 bps/month before 2017, but the advantage was statistically indistinguishable from zero in later years (decline of about 6 bps per year in the monthly advantage); AI funds held about US$12 billion in 2024. — [NBER Digest, Sept 2026](https://www.nber.org/digest/202609/artificial-intelligence-and-hedge-fund-investing); [NBER WP 35273](https://www.nber.org/papers/w35273) (snippet only)
- Man Group's internal "AlphaGPT" proposes signals, codes and backtests them, but a Man Numeric senior PM says models cannot yet replace the market judgment research requires; the firm describes controls for look-ahead bias and data mining. This is an LLM as research assistant, not as a trader. — [AI Street interview](https://aistreet.beehiiv.com/p/inside-man-group-s-alphagpt)

**Retail "ChatGPT portfolio" products**
- A MarketScreener piece compared Autopilot's GPT and Grok portfolios from 12 Feb 2025 to 17 Feb 2026, a period in which the S&P 500 returned 12%. — [MarketScreener](https://www.marketscreener.com/news/can-chatgpt-and-grok-beat-the-market-ce7e5cdfd081fe24) (snippet only; the portfolios' own returns were not retrievable)

### Inferences
- A 17-day or 50-day window cannot distinguish skill from luck: with daily Sharpe-1 noise, a two-week ranking is essentially random. The spread from +22% to -63% in Alpha Arena S1 on leveraged crypto perps is evidence about leverage and variance, not about which model "can trade".
- The benchmarks that look mildly positive (StockBench, LiveTradeBench) omit all costs and run in a rising market on mega-cap US names; the one benchmark that controls for survivorship and runs 20 years (FINSABER) is clearly negative. That ordering (the more careful the test, the worse the result) is the classic signature of an effect that is not there.
- LiveTradeBench's 0.054 rank correlation means "use the best frontier model" is not a trading edge.
- No disclosed hedge-fund result attributes audited alpha to an LLM making trade decisions; institutional use that is documented is research acceleration.

### Gaps
- Claude Sonnet 4.5 and Grok 4 exact final Season 1 figures were not verifiable (ForkLog/Aurpay unreachable); only "four of six lost" plus four models' numbers were confirmed via snippets. nof1.ai was not fetched directly.
- No Alpha Arena Season 2 or any later nof1 season results found; status confirmed only as of Aug 2026.
- Autopilot GPT/Grok portfolio returns not retrieved. AIEQ vs S&P 500 exact since-inception gap to Nov 2026 not retrieved (Amplify gives ~9.4-10.1% annualised without a matched benchmark figure).
- No LIVE LLM-trading evidence of any kind on Indian equities was found.
- TradingAgents-specific critique not separately sourced (FINSABER tests FinMem/FinAgent; FinCon was not open source and was only used as a selector).

---

## 3. News sentiment for a retail trader: half-life, who captures it, and India

### Takeaway
Scheduled and headline news is priced in milliseconds to minutes by co-located algorithmic traders; what remains for a slow trader is a multi-day drift after fundamental news that is small, concentrated in small/illiquid names and negative news, and in the US evidence is already eliminated by a 20 bps round-trip cost. India-specific sentiment studies are few, low-powered, mostly ignore costs, and give mixed results; none found shows a retail-implementable news-sentiment profit on NSE after costs.

### Cited Findings
- Speed for scheduled macro news: the fastest traders act within a few milliseconds of US macro announcements, and event-trading profitability drops sharply with delay even for a trader who gets direction right 80% of the time. — [Scholtus, van Dijk & Frijns, Tinbergen DP](https://papers.tinbergen.nl/12121.pdf)
- Chordia, Green & Kottimukkalur find prices in S&P 500 ETF/futures incorporate macro surprises so quickly that buying two-second-early access to Consumer Sentiment data earned no excess profit. — [ABFER conference paper](https://www.abfer.org/media/abfer-events-2016/annual-conference/investment-finance/38-do-high-frequency-traders-need-to-be-regulated-evidence-from-algorithmic-trading-on-macroeconomic-news.pdf)
- HFTs react faster than other trader groups to publicly disclosed corporate announcements. — ["How HFTs Price Information", AUT working paper](https://acfr.aut.ac.nz/__data/assets/pdf_file/0005/925286/How_HFTs_Price_Information.pdf)
- For LLM-scored US firm news, the first 1-15 minutes after an intraday release show no significant signal return; a drift from 15 minutes to the close (about 30 bps, pre-cost) and overnight/next-day drift exist, concentrated in small stocks and negative news, and the strategy is unprofitable at 20 bps round-trip. — [Lopez-Lira & Tang v6](https://arxiv.org/html/2304.07619v6)
- Across 1.68 million US stock-day news events (2023-2026), the cumulative move by the close of publication day is 2.8 times its value 20 days later: on average more of the move has happened (and partly reversed) than remains. Only fundamental news drifts on for weeks; soft news reverses. — [arXiv 2608.14014](https://arxiv.org/abs/2608.14014)
- India market structure: NSE opened co-location in January 2010 and within 15 months 60% of incoming orders came from co-located servers. — [ABFER/NSE low-latency paper](https://www.abfer.org/media/abfer-events-2014/annual-conference/investment-finance/low-latency-trading-and-comovement-of-order-flow-andprices.pdf)
- NSE announced an architecture upgrade from 11 April 2026 to cut response latency to the nanosecond range (announced plan, Feb 2026). — [Business Today, 22 Feb 2026](https://www.businesstoday.in/markets/stocks/story/nse-to-slash-trading-latency-to-nanoseconds-from-apr-11-targets-100-mn-transactions-per-second-517444-2026-02-22)
- An NSE-NYU study of trading around unscheduled corporate announcements finds retail traders are the least informed trading group. — [NSE-NYU working paper](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/Trading%20around%20Unscheduled%20announcements_FINALTONYU.pdf)
- Retail API ceiling: under SEBI's retail-algo framework (mandatory from 1 April 2026) exchange registration is required above 10 orders per second. — [Zerodha Daily Brief](https://thedailybrief.zerodha.com/p/sebis-latest-algo-trading-rules) (as already cited in the Thunderbot report)

**India-specific sentiment studies (all [BACKTEST] or event studies)**
- FinBERT on long news articles for non-financial Nifty 50 stocks to build a portfolio: "found to outperform the market", but the authors note it missed strong performers because news was the only selection input; no cost treatment visible in the abstract. — [IJICBM 2025, Vol. 34 No. 3](https://www.inderscience.com/info/inarticle.php?artid=144909)
- "News Sentiment and Stock Market Dynamics: A Machine Learning Investigation" (JRFM 2025) reports weak correlations among its sentiment measures; cites earlier Indian work finding aggregate news sentiment predicts short-term NIFTY fluctuations. — [JRFM 18(8):412](https://doi.org/10.3390/jrfm18080412)
- A FinBERT sentiment index built from Times of India business articles shows a significant positive association with Nifty 500 and sectoral indices (association, not a traded strategy). — ["Mind over market", ResearchGate](https://www.researchgate.net/publication/394935778_Mind_over_market_Impact_of_investor_sentiment_on_the_Indian_stock_market)
- A 2018-2024 study links Moneycontrol forum, Twitter/X and Reddit sentiment (VADER, FinBERT, custom lexicon) to Nifty 50/Sensex returns, volatility and volume (results not extracted; non-journal deposit). — [Zenodo record](https://zenodo.org/records/18770670)
- An event study of NSE corporate announcements by Indian financial institutions during the IL&FS crisis found the FinBERT sentiment coefficient not statistically significant. — [GitHub: nse-announcements-finbert-event-study](https://github.com/SankarGanesh01/nse-announcements-finbert-event-study)
- An instruction-tuned-LLM + RAG + reinforcement-learning sentiment system for NIFTY 50 exists as a preprint (results not read). — [arXiv 2512.20082](https://arxiv.org/pdf/2512.20082)

**India post-earnings drift (older evidence only)**
- 100 NSE firms, 2014-2018: market "tends to be efficient with respect to earnings announcements and therefore does not produce excessive returns", with heterogeneity by liquidity. — [Gupta & Dhusia, Trends Economics and Management](https://journals.vutbr.cz/index.php/trends/article/view/541)
- Earlier work finds drift: negative drift for over a week after bad earnings news — [University of Nottingham dissertation, 2013](https://eprints.nottingham.ac.uk/26569); drift over 120 days plus pre-announcement price movement — [IIM Bangalore repository](https://repository.iimb.ac.in/handle/2074/17935)

### Inferences
- A Groww-API bot with delayed/Yahoo data, seconds of LLM latency and no colocation cannot compete for the first minutes after news; the fast part of news alpha is structurally unavailable.
- The slow part (multi-day drift after earnings/guidance) is the only piece a daily bot could even attempt. It is a known anomaly (PEAD), not an LLM invention; an LLM merely classifies the news. Indian evidence on PEAD is old and mixed, and the pre-announcement run-up finding suggests information leaks before publication, further shrinking what is left for a headline reader.
- Because news moves partly reverse on average (2.8x ratio), a naive "buy positive headlines" rule is more likely to buy the top of the move than to capture drift.
- Indian sentiment papers showing "outperformance" generally lack costs, survivorship control and out-of-sample periods beyond a model's training cutoff; they should be read as hypotheses.

### Gaps
- No study found measuring how many seconds/minutes NSE prices take to absorb corporate announcements or news headlines, nor one quantifying retail-API latency versus co-located participants.
- No 2023-2026 India PEAD or overnight-drift-after-news study found; no India news-sentiment study with explicit transaction costs found.
- Groww's specific API rate limit was not re-verified here (the 10 orders/sec figure is the SEBI registration threshold from the existing report).

---

## 4. ML for intraday price prediction (boosting / LSTM / transformers; 1-5 minute bars; order book)

### Takeaway
Academic intraday/LOB deep-learning results are prediction-accuracy results, not profit results: independent benchmarks find the models lose much of their accuracy on new data and that high accuracy "does not necessarily correspond to actionable trading signals", while the classic daily ML stat-arb papers report profitability "fluctuating around zero after transaction costs" since 2010. No credible evidence of retail-scale intraday ML profitability in India was found.

### Cited Findings
- Gu, Kelly & Xiu's "Empirical Asset Pricing via Machine Learning" is a monthly-horizon study (neural-net long-short decile Sharpe 1.35 value-weighted; S&P 500 timing Sharpe 0.77), not intraday; how much of it survives trading costs is the subject of Avramov et al. (Section 5). — [AQR-hosted paper](https://www.aqr.com/-/media/AQR/Documents/Journal-Articles/Empirical-Asset-Pricing-in-Machine-Learning.pdf?sc_lang=en); [NBER w25398](https://www.nber.org/papers/w25398.pdf)
- LOBCAST benchmark (Prata et al., arXiv 2308.01915; Artificial Intelligence Review 2024): 15 state-of-the-art deep-learning LOB models re-tested; "all models exhibit a significant performance drop when exposed to new data, thereby raising questions about their real-world market applicability". — [arXiv 2308.01915](https://arxiv.org/abs/2308.01915)
- Briola, Bartolucci & Aste, "Deep Limit Order Book Forecasting: a microstructural guide" (Quantitative Finance 2025; 15 NASDAQ stocks, DeepLOB): high forecasting power "does not necessarily correspond to actionable trading signals"; probability of a correct complete transaction is only about 0.07-0.12 at the 10-update horizon even for the most predictable large-tick stocks and 0.01-0.06 for small-tick stocks at longer horizons; most 10-update horizons elapse in under one second; the authors list live-data infrastructure, guaranteed fills, zero impact and zero transaction costs as assumptions that ruin "any attempt to produce a reliable backtest". — [arXiv 2403.09267v4](https://arxiv.org/html/2403.09267v4); [LSE Research Online](https://researchonline.lse.ac.uk/id/eprint/128950)
- Fischer & Krauss (LSTM on S&P 500 constituents, EJOR 2018): daily returns 0.46% and Sharpe 5.8 before costs, but "as of 2010, excess returns seem to have been arbitraged away with LSTM profitability fluctuating around zero after transaction costs". — [EconPapers / EJOR 270(2)](https://econpapers.repec.org/RePEc:eee:ejores:v:270:y:2018:i:2:p:654-669)
- Krauss, Do & Huck (deep nets, gradient-boosted trees, random forests; S&P 500 stat-arb): 0.45%/day pre-cost for the ensemble, with "deteriorating returns" in later years, "indicating that markets have become more efficient in respect to standard machine learning statistical arbitrage". — [FAU discussion paper](https://www.iwf.rw.fau.de/files/2016/03/03-2016.pdf)
- Multiple-testing hurdle: Harvey, Liu & Zhu argue a new factor needs a t-statistic above 3.0 and that most claimed findings in financial economics are likely false. — [NBER w20592 / RFS 2016](https://nber.org/papers/w20592)
- Bailey & Lopez de Prado's Deflated Sharpe Ratio corrects a backtest Sharpe for selection bias under multiple testing and non-normal returns. — [SSRN 2460551](https://papers.ssrn.com/abstract=2460551)
- Bailey, Borwein, Lopez de Prado & Zhu's Probability of Backtest Overfitting estimates, via combinatorially symmetric cross-validation, the chance the best in-sample configuration underperforms the median out-of-sample. — [SSRN 2326253](https://papers.ssrn.com/abstract=2326253)
- Arnott, Harvey & Markowitz, "A Backtesting Protocol in the Era of Machine Learning" (2018): a research protocol intended for both statistical and ML methods to curb overfitting. — [paper copy (SSRN 3275654)](https://www.smallake.kr/wp-content/uploads/2023/04/SSRN-id3275654.pdf)
- Pointer only (already documented in the Thunderbot report): SEBI's Aug 2026 F&O study shows individuals tagged as algo users still lost Rs 51,728 crore gross over FY25-FY26, and the July 2024 study shows 71% of intraday cash traders lost in FY23. — [SEBI FY25-FY26 study](https://www.sebi.gov.in/sebi_data/attachdocs/aug-2026/1787233506209.pdf)
- Indian "ML beats momentum" claims located were in low-tier outlets and on options, e.g. an IJFMR 2025 paper claiming an ML options strategy outperforms basic momentum on Nifty 50 options. — [IJFMR 2025](https://www.ijfmr.com/papers/2025/4/50375.pdf)

### Inferences
- The LOB literature's horizons (sub-second to seconds) are unreachable from a retail API; a 1-5 minute-bar model sees none of the queue/latency edge and must overcome the bid-ask spread plus brokerage and statutory charges on every round trip with a directional accuracy barely above 50%. Nothing in the peer-reviewed record shows that is achievable out-of-sample at retail scale.
- Thunderbot's own intraday rule results (profit factors 0.18-0.40 in the existing report) are consistent with this; swapping hand rules for XGBoost/LSTM on the same bars adds degrees of freedom (overfitting risk) without adding information.
- Any intraday ML backtest the owner builds will have been selected from many trials; applying the deflated-Sharpe/PBO logic, a backtest Sharpe of 1-2 from dozens of tried configurations is the expected outcome of zero true skill.

### Gaps
- No primary source was retrieved quantifying DeepLOB's net profit after costs/latency; the "vanishes after costs" statement is supported here by Briola et al. and LOBCAST (accuracy fails to generalise or to translate into executable trades), not by a DeepLOB P&L table.
- LOBCAST's own profit-analysis numbers and exact F1 drops were not extracted (ar5iv unreachable).
- No peer-reviewed, cost-inclusive, out-of-sample study of intraday ML on NSE stocks at retail scale was found, positive or negative. Absence of evidence, not proof of impossibility.
- The seven-point Arnott-Harvey-Markowitz protocol text was not extracted.

---

## 5. ML for monthly / cross-sectional prediction, and ML ranker vs plain 12-1 momentum in India

### Takeaway
Monthly ML return prediction is real in US academic data but much of it lives in microcaps, distressed stocks and high-turnover portfolios; it shrinks by roughly 60% when microcaps are excluded, shrinks again in real-time designs and after publication, and no study found shows it beating simple momentum for 100-500 Indian stocks after costs. The single direct Indian test found (unreviewed) concludes gradient boosting does not beat 12-1 momentum on the Nifty 500 after costs and needs 1.8x the turnover to match it.

### Cited Findings
- Gu, Kelly & Xiu (RFS 2020): neural-net long-short decile portfolio annualised out-of-sample Sharpe 1.35 (value-weighted), pre-cost, US stocks, monthly. — [NBER w25398](https://www.nber.org/papers/w25398.pdf)
- Avramov, Cheng & Metzker, "Machine Learning vs. Economic Restrictions" (Management Science 2023): ML profitability is "considerably attenuated" when microcaps, distressed stocks or high-volatility episodes are excluded, and "further deteriorates in the presence of reasonable trading costs because of high turnover and extreme positions"; deep-learning signals remain profitable in long positions and recent years. — [SSRN 3450322](https://papers.ssrn.com/abstract=3450322); [EconPapers, Mgmt Sci 69(5)](https://econpapers.repec.org/RePEc:inm:ormnsc:v:69:y:2023:i:5:p:2587-2619)
- CUHK's summary of the same paper: excluding microcaps cuts the payoff by 62%; co-author Cheng says an average investor would struggle to achieve alpha after transaction costs, though this is not a case against ML in quant investing as such. — [CUHK Business School](https://cbk.bschool.cuhk.edu.hk/the-limitations-of-using-ai-to-pick-stocks/)
- Li, Rossi, Yan & Zheng (JFE 2025, "Machine learning from a 'Universe' of signals: The role of feature engineering"; earlier title "Real-time Machine Learning in the Cross-Section of Stock Returns"): building ML strategies from 18,000+ fundamental signals an investor could actually have known in real time gives out-of-sample performance that is significant but "considerably weaker" than studies using curated published anomalies, and especially weak (insignificant in the working paper) among large stocks. — [JFE 2025 PDF](https://www.lehigh.edu/~xuy219/research/JFE_2025.pdf); [working paper](https://cfet.frankfurt-school.de/wp-content/uploads/2024/09/Real_Time_ML.pdf)
- McLean & Pontiff: anomaly long-short returns are about 58% lower post-publication (0.58% to 0.26% monthly across 97 predictors in the commonly quoted version; other drafts give 56% on 95 predictors). — [CXO Advisory summary](https://www.cxoadvisory.com/big-ideas/effects-of-market-adaptation); replication caveat that the US is the only country with a reliable post-publication decline — [Jacobs & Mueller](https://www.wiwi.hu-berlin.de/en/Professorships/bwl/finance/seminars/papers-fin-acc-res-seminars/17s/jacobs.pdf)
- Harvey, Sancetta & Zhao (NBER, 2026) reaffirm a t-statistic cutoff of at least 3.0 for new factors. — [NBER w34898](https://www.nber.org/system/files/working_papers/w34898/w34898.pdf)

**India**
- Sharma, "Empirical Asset Pricing via Machine Learning: Evidence from Indian Equity Markets" (SSRN 7339440): applies the Gu-Kelly-Xiu framework to 375 NSE stocks over 2000-2024 with ten price-based characteristics and 14 models in an expanding-window out-of-sample design. — [SSRN 7339440](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7339440) (snippet only; results not retrieved)
- An earlier study on NIFTY 100 constituents with 35 characteristics reports ML models outperform OLS (gross of costs as far as the abstract shows). — ["The cross-section of Indian stock returns: evidence using machine learning", ResearchGate](https://www.researchgate.net/publication/354819735_The_cross-section_of_Indian_stock_returns_evidence_using_machine_learning)
- "Empirical Asset Pricing via Machine Learning: The Global Edition" is hosted by IIM Bangalore (India coverage not confirmed). — [IIMB PDF](https://www.iimb.ac.in/sites/default/files/inline-files/Empirical%20Asset-Pricing-Machine-Learning.pdf)
- "When Gradient Boosting Does Not Beat Momentum" (H. Pandhe, SSRN 7137361, 2026; independent researcher, not peer reviewed): XGBoost cross-sectional ranker vs plain 12-1 momentum on the Nifty 500, walk-forward with transaction costs, Stationary Block Bootstrap and Jobson-Korkie-Memmel tests: the ML model does not beat the baseline once significance and costs are applied; a learning-to-rank variant that matches the baseline Sharpe needs 1.8x the turnover. — [author's GitHub listing](https://github.com/harsh-pandhe/harsh-pandhe); [SSRN 7137361](https://papers.ssrn.com/abstract=7137361) (SSRN not fetched; details as self-reported by the author)
- Same author, "Hysteresis Rebalancing in Cross-Sectional Momentum" (SSRN 7389238): a rank buffer band cut average monthly liquidations from 9.57 to 4.62 names and annualised cost drag from 163 to 78 bps; the Sharpe gain is not statistically significant (p = 0.167) and the author calls the results sample-specific. — [author's GitHub listing](https://github.com/harsh-pandhe/harsh-pandhe)

### Inferences
- For a 100-500 stock Indian large/mid-cap universe (no microcaps, long-only, monthly), the conditions under which ML's edge is largest (microcaps, shorting, high turnover) are exactly the ones excluded. The realistic prior is that an ML ranker is at best a noisier, higher-turnover re-expression of momentum/volatility, which is what the Pandhe result says.
- With only ~20 years x 12 months of Indian data and a few hundred names, a boosted model has far fewer independent observations than the US CRSP panels where ML gains were measured; overfitting risk is higher, not lower.
- The absolute CAGRs in the Pandhe papers (33-45%) look inflated in the same way the existing Thunderbot report flags (current-constituent survivorship), so only the relative ML-vs-momentum comparison should be used, and with caution.
- Evidence-compatible position: keep the plain 12-1 (or NSE Momentum 30-style) sort; if ML is used at all, treat it as a research side-project that must beat the plain sort net of costs in a pre-registered forward test.

### Gaps
- Sharma (SSRN 7339440) quantitative results (out-of-sample R2, long-short Sharpe, any cost analysis) not retrieved; SSRN unreachable.
- Chen & Zimmermann's Open Source Asset Pricing post-publication decay estimates were not retrieved in this session.
- No peer-reviewed Indian study comparing an ML ranker with 12-1 momentum net of costs was found; the only direct test is a single-author SSRN preprint known here via the author's own summary.
- Post-2018 US out-of-sample updates of the Gu-Kelly-Xiu portfolios were not located.

---

## 6. Sensible, evidence-compatible roles for an LLM in a small rules-based bot

### Takeaway
There is no benchmark showing LLMs are reliable at corporate-action detection or price-feed anomaly diagnosis, and the adjacent evidence says LLMs catch only "trivial" time-series anomalies, are weak at numerical reasoning, are not fully deterministic, and can be steered into large drawdowns by fake or injected news. That supports the proposed guardrail design (veto/shrink only, never create or enlarge; deterministic checks first; every veto logged and scored) and argues against giving the LLM any authority to originate trades.

### Cited Findings
- Time-series anomalies: "LLMs can understand trivial time series anomalies"; there is "no evidence that they can understand more subtle real-world anomalies". — ["Can LLMs Understand Time Series Anomalies?", arXiv 2410.05440](https://arxiv.org/pdf/2410.05440)
- A 2025 paper reports LLMs can help filter false alarms from a conventional anomaly detector by combining plots with a text description of the data-generating process, i.e. LLM as second-stage reviewer rather than primary detector. — [arXiv 2503.21833](https://arxiv.org/abs/2503.21833v1)
- Numerical reasoning is a documented LLM weakness in finance/accounting tasks. — [Levy, Chicago Booth](https://www.chicagobooth.edu/research/fama-miller/finance-research/working-papers/2025/caution-ahead)
- Filing Q&A, 2023-era models: on FinanceBench (10,231 questions on public-company filings), Claude 2 with long context answered about 75% correctly, 21% wrongly and refused 3%; other tested configurations failed or refused far more often (68-81% in one secondary report). These are 2023 models and should be treated as dated. — [Patronus AI release](https://prnewswire.com/news-releases/patronus-ai-launches-industry-first-llm-benchmark-for-finance-to-address-hallucinations-301990858.html); [FinanceBench, arXiv 2311.11944](https://www.alphaxiv.org/abs/2311.11944v1)
- Filing-QA hallucination detection, 2026: on 755 annotated SEC 10-K Q&A examples, the best LLM-judge and embedding detectors reach F1 0.82-0.86 under clean conditions, meaning hallucination checking is itself imperfect. — [arXiv 2603.20252](https://arxiv.org/abs/2603.20252)
- Fake-news / prompt-injection: TradeTrap (arXiv 2512.02261, Dec 2025) shows small perturbations at one component (fake news injected into feeds, prompt injection, memory poisoning, tool tampering) propagate through LLM trading agents to "extreme concentration, runaway exposure, and large portfolio drawdowns"; an adaptive agent over-reacted to scripted fake crises and failed to recover. — [arXiv 2512.02261](https://arxiv.org/abs/2512.02261v1)
- Further 2026 work on the same threat exists: "Poisoning Agentic Alpha: Adversarial Vulnerabilities Across Roles and Architectures in Multi-Agent Trading Systems" — [arXiv 2608.24069](https://arxiv.org/pdf/2608.24069) (findings not read); "Adversarial News and Lost Profits: Manipulating Headlines in LLM-Driven Algorithmic Trading" (Rizvani, Apruzzese, Laskov 2026) is cited there (title only).
- Non-determinism: in a cross-provider study of financial workflows at temperature 0, small 7-20B models reached 100% output consistency while a 120B model reached only 12.5%; one cited test produced 80 unique completions from 1,000 identical temperature-0 runs of a 235B model. — ["LLM Output Drift", arXiv 2511.07585](https://arxiv.org/html/2511.07585)
- In agentic settings drift compounds along the trajectory even when final decisions match. — ["Replayable Financial Agents", arXiv 2601.15322](https://arxiv.org/html/2601.15322v2)
- Sentiment labels for the same sentence vary across runs of the same model (GPT-3.5/LLaMA-era test). — ["Benchmarking Large Language Model Volatility", arXiv 2311.15180](https://arxiv.org/pdf/2311.15180.pdf)
- Stale knowledge: LLM recall of market facts collapses after the training cutoff (S&P 500 level error 0.61% pre-cutoff vs 16.87% post-cutoff), and the model cannot be prompted into a different knowledge state. — [arXiv 2504.14765v2](https://arxiv.org/html/2504.14765v2)
- LLM agents' temperament when given discretion: over 20 years they were "too cautious when risk is rewarded and too aggressive when it is penalised". — [FINSABER](https://arxiv.org/html/2505.07078v4)
- Institutional precedent for the "assistant, not decider" role: Man Group uses an LLM system to propose and code research ideas under human review. — [AI Street](https://aistreet.beehiiv.com/p/inside-man-group-s-alphagpt)

### Inferences
- Role (a), pre-trade sanity / event-risk veto: an unadjusted split or bonus (a one-day -50%/-80% price gap with no index move) is a "trivial" anomaly in the sense of arXiv 2410.05440, so an LLM would probably flag it, but a two-line deterministic rule (abs(overnight return) > X% and no matching entry in the exchange corporate-action file) flags it more reliably and for free. Sensible ordering: deterministic checks from NSE corporate-action/results calendars and price-continuity rules first; LLM only as a second reader that explains flagged cases and may add a veto, never as the sole detector.
- The LLM must be given the facts (corporate-action file, results calendar, today's exchange announcements) in the prompt. Asking it from memory whether a company has results or a split "this week" will produce stale or invented answers, per the post-cutoff recall collapse.
- Veto-only is the right asymmetry: FINSABER and TradeTrap show the damage comes when the LLM can originate or enlarge positions. A veto can cost at most the forgone return of one skipped rebalance leg. But vetoes are not free: FINSABER's "too cautious in bull markets" finding predicts an LLM reviewer will over-veto, so each veto should be logged with the counterfactual (what the vetoed trade would have earned over the next rebalance period) and the LLM's veto right withdrawn if, after a pre-set number of vetoes, the vetoed trades have outperformed the kept ones.
- Prompt-injection hygiene follows from TradeTrap: pass news text as quoted data, strip instructions, restrict the output to a fixed schema (APPROVE / VETO / SHRINK plus reason code), and enforce in code that the output can only reduce order size. Treat an unparseable or contradictory answer as "no opinion" (rules proceed), not as approval of something new.
- Non-determinism means the same rebalance can get different verdicts on re-run; store the exact prompt, model ID and response for each decision, and never re-roll until the answer is the desired one. Temperature 0 is not a guarantee of identical output (arXiv 2511.07585), and Anthropic's API reference bundled with this research tool (cached 3 Nov 2026; not re-checked on the live docs) says current Claude models reject sampling parameters such as temperature altogether, so reproducibility has to come from logging, not from temperature settings.
- Roles (b) plain-language rebalance explanations and (c) filing summaries are low-risk because they do not touch orders, but summaries inherit a non-trivial error rate; they should quote the source passage and be labelled as unaudited.

### Gaps
- No benchmark or paper found that measures LLM accuracy at corporate-action detection, unadjusted-split detection in price feeds, results-day identification, or trading-halt detection. Reliability for these specific tasks is untested in the literature located; it would need the owner's own evaluation set (e.g. replaying past NSE splits/bonuses and scoring hits and false alarms).
- No published study found that scores an LLM veto layer on a rules-based equity strategy (hit rate, cost of false vetoes). The design is evidence-compatible, not evidence-proven.
- FinanceBench-style accuracy for 2026 frontier models on Indian filings (BSE/NSE PDFs, often scanned) was not found.

---

## 7. Cost side: API cost per decision in 2026

### Takeaway
At November 2026 list prices one daily trade-review call costs roughly US$0.001 to US$0.08 depending on model, i.e. about US$0.25 to US$20 a year, which is negligible; calling a frontier model on every 1-minute bar for a 50-stock watchlist would cost on the order of US$28,000-56,000 a year, more than the whole account, and would also be too slow.

### Cited Findings
- Anthropic list prices per million tokens (input / output), fetched 11 Nov 2026: Claude Fable 5.2 $8 / $40; Claude Opus 5.5 $4 / $20; Claude Sonnet 5.5 $2 / $10; Claude Haiku 5.5 $0.10 / $0.50 (prompts up to 100k tokens); Claude Haiku 4.5 $1 / $5. — [Anthropic pricing docs](https://platform.claude.com/docs/en/about-claude/pricing)
- The Batch API gives a 50 percent discount on input and output tokens for asynchronous processing (e.g. Opus 5.5 batch $2 / $10), and can be combined with prompt-caching discounts; cache hits cost $0.20/MTok on Opus 5.5 and $0.10/MTok on Sonnet 5.5. — [Anthropic pricing docs](https://platform.claude.com/docs/en/about-claude/pricing)
- Research-scale LLM backtesting is described by FINSABER's authors as "financially intensive", which is one reason published LLM-agent tests use few symbols and short windows. — [FINSABER](https://arxiv.org/html/2505.07078v4)
- Models are not interchangeable for trading by price or leaderboard rank: LMArena score vs live trading return rank correlation was 0.054. — [LiveTradeBench](https://arxiv.org/html/2511.03628v1)

### Inferences
(Arithmetic by the researcher from the list prices above; token counts are assumptions, not measurements. On models where thinking is always on, thinking tokens bill as output, so real output usage may be higher than assumed.)
- One daily review call, assumed 6,000 input tokens (proposed orders, holdings, corporate-action/results calendar extract, a few announcements) and 800 output tokens: Fable 5.2 about $0.080; Opus 5.5 about $0.040; Sonnet 5.5 about $0.020; Haiku 5.5 about $0.001. Over ~250 trading days: about $20, $10, $5 and $0.25 a year. A monthly rebalance needs only ~12 substantive calls a year.
- Scale check: on Rs 1 lakh, a 0.3% delivery round trip costs about Rs 300; a year of daily Opus 5.5 reviews (about $10) is worth only a few such round trips at that account size (assuming USD/INR in the high 80s, not looked up) and is immaterial at Rs 20 lakh. API cost is not the constraint for one decision a day; the question is only whether the review adds value.
- Per-bar intraday use, assumed 2,000 input and 200 output tokens per call, 50 symbols, NSE's 375-minute session: 1-minute bars = 18,750 calls/day. Opus 5.5 about $0.012/call = $225/day = about $56,000/year; Sonnet 5.5 about $112/day = about $28,000/year; Haiku 5.5 about $5.6/day = about $1,400/year. On 5-minute bars (3,750 calls/day): Opus 5.5 about $45/day = about $11,000/year; Haiku 5.5 about $1.1/day = about $280/year.
- Even the cheapest per-bar configuration (about $280-1,400/year) is a 1-10%+ annual drag on a Rs 1-20 lakh account before any trading cost, for a signal with no demonstrated edge (Sections 1-4). Batch discounts do not apply to real-time decisions.
- Latency compounds the cost problem: a reasoning model takes seconds per call, so a per-bar LLM loop acts on stale prices, and the news-reaction window that matters is over within minutes (Section 3).

### Gaps
- No measured token counts for an actual Thunderbot review prompt; the per-decision figures are order-of-magnitude estimates.
- Prices for non-Anthropic frontier models (OpenAI, Google, DeepSeek, Qwen) in Nov 2026 were not checked; the conclusion (cents per daily decision, thousands of dollars per year for per-bar use of a frontier model) is unlikely to change but is unverified for them.
- USD/INR was not looked up; rupee equivalents are deliberately omitted.
