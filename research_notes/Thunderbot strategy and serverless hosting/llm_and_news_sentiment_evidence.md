# Do LLMs or news-sentiment signals add investment return for a small retail trader? Evidence 2023 to November 2026

*Research conditions (read before using these notes): written 10 November 2026. Page fetching was blocked in this session (arxiv.org, sebi.gov.in, alphaxiv.org and traderank.ai all failed to resolve), and the shared web-search budget ran out before the last batch of queries. Every cited finding below therefore rests on search-result summaries of the linked pages, not on a full read of the page. Numbers should be re-checked against the primary PDF before being quoted as exact. Topics that could not be searched at all are listed under Gaps and are marked UNVERIFIED where I give a recollection without a source.*

## 1. The headline positive papers and their caveats

### Takeaway
The best-known positive results are backtests of daily, high-turnover long-short portfolios on US stocks, and their own authors report that the edge is concentrated in small stocks and bad news, shrinks sharply after trading costs, and has declined as LLM use spread. None of these papers tests anything resembling a once-a-day, long-only, monthly-rebalanced retail strategy in India.

### Cited Findings

**Lopez-Lira & Tang, "Can ChatGPT Forecast Stock Price Movements?" (first version April 2023, v6 October 2025) — backtest**
- The latest version (v6, October 2025) states that strategy returns decline as LLM adoption rises, which the authors read as improved price efficiency, and ties this to a model with information-capacity constraints, underreaction and limits to arbitrage — [arXiv 2304.07619 v6](https://arxiv.org/pdf/2304.07619v6)
- The v6 abstract reports that GPT-4 captures the initial market reaction to headlines with about 90% portfolio-day hit rates, but that this initial reaction is not tradable — [arXiv 2304.07619](https://arxiv.org/abs/2304.07619)
- Before costs, the best model's long-short Sharpe ratio is reported as 3.28 in a later version (1.79 for GPT-3.5, 1.61 for DistilBart-MNLI); an earlier version reported 3.8 for GPT-4 and 3.1 for GPT-3.5, so the figures move between versions — [arXiv 2304.07619 v5](https://arxiv.org/pdf/2304.07619v5.pdf); [arXiv 2304.07619 v4](https://arxiv.org/pdf/2304.07619v4.pdf)
- After costs: assuming 10 bps per trade the long-short strategy's cumulative return falls to about 350% over the sample, and at 25 bps per trade to about 50% — [arXiv 2304.07619 v4](https://arxiv.org/pdf/2304.07619v4.pdf)
- The later version says underreaction is particularly pronounced for smaller stocks and after negative news, and that exploiting it is feasible only for participants whose transaction costs are sufficiently low, such as market makers — [arXiv 2304.07619 v5](https://arxiv.org/pdf/2304.07619v5.pdf)
- Forecasting ability generally rises with model size — [arXiv 2304.07619](https://arxiv.org/abs/2304.07619)
- A third-party blog summary reports the Sharpe ratio falling to 1.22 by early 2024 and about 190% daily turnover. Not verified against the paper — [Pulse blog](https://www.pulse.bot/ai/blogs/can-chatgpt-forecast-stock-price-movements-680b3dee-231f-4644-b717-0fb80e1ea03a/)

**Chen, Kelly & Xiu, "Expected Returns and Large Language Models" — backtest**
- The paper extracts contextualised embeddings of news text from LLMs (ChatGPT, LLaMA, plus BERT/RoBERTa comparisons) to predict the cross-section of returns; LLM-embedding predictions improve significantly over technical signals such as past returns and over simpler NLP methods — [Oxford NLP-in-finance seminar listing](https://nlpecofin.web.ox.ac.uk/node/3041271); [AEA 2025 programme](https://www.aeaweb.org/conference/2025/program/1861)
- A conference discussion of the paper lists as a main finding that returns respond slowly to news — [Sophia Zhengzi Li discussion slides, Wharton Jacobs Levy Center](https://jacobslevycenter.wharton.upenn.edu/wp-content/uploads/2024/09/ExpectedReturnAndLLM_Discussion_SophiaZhengziLi_NoPause.pdf)
- The paper's keywords include trading strategies, Sharpe ratios and limits to arbitrage — [AEA 2025 programme](https://www.aeaweb.org/conference/2025/program/1861)

**Kim, Muhn & Nikolaev, "Financial Statement Analysis with Large Language Models" (Chicago Booth, May 2024; arXiv v3 20 February 2025) — backtest**
- GPT-4 with a chain-of-thought prompt predicted the direction of future earnings with about 60.4% accuracy from anonymised, standardised statements, against roughly 53 to 57% for the median analyst; a simple prompt scored about 52% — [AI and Finance substack summary](https://aiandfinance.substack.com/p/financial-statement-analysis-with); [arXiv 2407.17866 v3](https://arxiv.org/abs/2407.17866v3)
- Statements were stripped of company names and years were replaced by labels (t, t-1); the authors report that GPT-4's ability to guess the firm or fiscal year from the anonymised data is negligible. Sample: 150,678 firm-year observations from 15,401 companies in Compustat — [AI and Finance substack summary](https://aiandfinance.substack.com/p/financial-statement-analysis-with)
- Critique: Bradford Levy's "Caution Ahead: Numerical Reasoning and Look-ahead Bias in AI Models" (Chicago Booth, December 2024 / 2025) examines why AI models do well on accounting and finance tasks and finds that LLMs reason poorly with numbers and that commercial LLMs show significant look-ahead bias that may account for much of their apparent predictive power — [Chicago Booth working paper page](https://www.chicagobooth.edu/research/fama-miller/finance-research/working-papers/2025/caution-ahead); [CXO Advisory summary](https://www.cxoadvisory.com/investing-expertise/innumeracy-and-look-ahead-bias-in-llms)

**Pelster & Val, "Can ChatGPT assist in picking stocks?" (Finance Research Letters 59, 2024) — a live experiment, not a backtest**
- ChatGPT-4 ratings correlate positively with future earnings announcements and stock returns, and the model adjusts ratings in a timely way after earnings surprises and news — [RePEc listing](https://ideas.repec.org/a/eee/finlet/v59y2024ics1544612323011583.html)
- The authors frame LLMs as cost-effective "assistants" in stock selection, not as the final judge — [Alpha Architect summary](https://alphaarchitect.com/chatgpt/)
- A 2026 arXiv paper characterises the same study as showing that ChatGPT's stock recommendations lack consistency and are sensitive to prompt design — [arXiv 2603.19944 v2](https://arxiv.org/pdf/2603.19944v2)

**LLM trading-agent papers (FinMem, FinAgent, TradingAgents, FinCON, QuantAgent) — backtests**
- The FINSABER authors note that most LLM-investing studies assess performance over short periods and few stock symbols and often release no code — [FINSABER, arXiv 2505.07078](https://arxiv.org/html/2505.07078v3)
- Re-tested with GPT-4o, FinMem, FinAgent, QuantAgent, FinCON and TradingAgents all show a significant performance drop once evaluated beyond the model's training window (details in section 2) — [Profit Mirage, arXiv 2510.07920](https://arxiv.org/abs/2510.07920)

### Inferences
- The positive literature measures something a daily end-of-day retail bot cannot capture: a next-day (or intraday) reaction to fresh headlines, harvested with roughly full daily portfolio turnover in both long and short legs. A delivery-only NSE account cannot short overnight, and the bot's core signals rebalance monthly.
- The authors' own cost sensitivity (cumulative return falling from very large to about 50% at 25 bps per trade) implies the strategy is marginal for anyone paying retail-level impact and statutory costs. Indian delivery trades carry securities transaction tax and stamp duty on top of spreads, so the hurdle is higher than the 10 to 25 bps tested.
- Kim et al. is evidence that LLMs can do useful financial-statement reasoning as an assistant; it is not evidence of tradable alpha for a retail account, and the look-ahead critique means even the accuracy figure needs post-cutoff confirmation.

### Gaps
- Jha, Qian, Weber & Yang, "ChatGPT and Corporate Policies": not searched (search budget exhausted). UNVERIFIED recollection: the paper builds a ChatGPT "investment score" from earnings-call transcripts that predicts firms' future capital expenditure and is associated with negative future abnormal returns for high-score firms; it is a corporate-finance result, not a trading strategy test. Check before citing.
- MarketSenseAI, FinGPT, FinMem, TradingAgents, FinAgent: the original papers' own headline numbers and test windows were not retrieved. Only the third-party re-evaluations (FINSABER, Profit Mirage) were found.
- Chen, Kelly & Xiu: no source found for their transaction-cost treatment, sample period or Sharpe ratios.
- Lopez-Lira & Tang: the exact post-adoption Sharpe figures and how overnight versus open-to-close returns are handled were not confirmed from the PDF.
- I could not confirm from a primary source whether Levy's paper re-runs the Kim, Muhn & Nikolaev test specifically. UNVERIFIED recollection: it does, and reports that the result weakens outside the training window.

## 2. Look-ahead, memorisation and data-leakage critiques, and what forward (post-cutoff) benchmarks found

### Takeaway
The dominant finding of 2024 to 2026 is that any LLM "backtest" over dates inside the model's training window is not interpretable as forecasting skill, and that when agents are tested after the cutoff or live, most fail to beat buy-and-hold. One nuance cuts the other way: for narrow news-sentiment tasks, purpose-built leak-free models achieve similar results, so look-ahead bias there appears modest.

### Cited Findings

**Memorisation and look-ahead tests**
- Lopez-Lira, Tang & Zhu, "The Memorization Problem" (arXiv April 2025, v2 15 December 2025; SSRN revision 2 April 2026): LLMs can recall exact numerical values of key economic variables from before their cutoff; pre-cutoff forecasting tests cannot separate skill from memorisation (forecast ability is non-identified under black-box access); explicit instructions to respect a date boundary do not prevent recall-level accuracy; masking fails because models reconstruct entities and dates from minimal context; LLMs cannot recall post-cutoff data, so post-cutoff evaluation is required — [arXiv 2504.14765 v2](https://arxiv.org/html/2504.14765v2); [SSRN 5217505](https://papers.ssrn.com/abstract=5217505); [Quantpedia summary](https://quantpedia.com/the-memorization-problem-can-we-trust-llms-forecasts/)
- Glasserman & Lin (September 2023): using GPT-3.5 sentiment, anonymised ("replaced") headlines produced higher in-sample long-short returns than the originals, which the authors attribute to a "distraction effect" from company knowledge outweighing look-ahead bias. In-sample is January 2015 to September 2021; out-of-sample is October 2021 to December 2022, where the difference loses statistical significance (borderline evidence for larger companies) — [arXiv 2309.17322](https://arxiv.org/abs/2309.17322)
- Sarkar & Vafa, "Lookahead Bias in Pretrained Language Models" (Harvard, first version March 2024): propose statistical tests for leakage and find evidence of it in predicting risk factors from earnings calls and election winners from biographies; remedy is to use models whose pretraining data stops before the analysis period — [ICML 2025 listing](https://icml.cc/virtual/2025/48685); [NBER conference PDF](https://conference.nber.org/conf_papers/f205530/f205530.pdf)
- Levy, "Caution Ahead": commercial LLMs show significant look-ahead bias and weak numerical reasoning — [Chicago Booth](https://www.chicagobooth.edu/research/center-for-applied-artificial-intelligence/research/our-faculty-research/2025/caution-ahead-numerical-reasoning-and-look-ahead-bias-in-ai-models)
- Look-Ahead-Bench (Benhenda, 2026) reports significant look-ahead bias in standard commercial LLMs on stock selection, measured as alpha decay, while point-in-time models do not show the pattern — [arXiv 2601.13770](https://arxiv.org/pdf/2601.13770)
- Somoza, Didisheim & Fraschini prompt LLMs to retrieve historical stock returns without context and find that smaller models and finer data granularity show negligible bias (URL-to-paper mapping inferred from the search listing) — [ESSEC research page](https://faculty.essec.edu/research/16148-ais-predictable-memory-in-financial-analysis)
- Gao, Jiang & Yan introduced a "Look Ahead Prediction" metric and showed that substantial memorisation can amplify apparent predictive power, as described secondhand by a 2026 preprint — [arXiv 2603.26797](https://arxiv.org/pdf/2603.26797.pdf)

**Point-in-time models (the mixed evidence)**
- He, Lv, Manela & Wu, "Chronologically Consistent Large Language Models" (arXiv 2502.21206): ChronoBERT and ChronoGPT are trained per year from 1999 so they never see future text. Predicting next-day returns from news, their real-time outputs achieve Sharpe ratios comparable to a much larger Llama model, which the authors read as look-ahead bias being modest in that application. The authors add that bias is application-specific — [arXiv 2502.21206 v2](https://arxiv.org/pdf/2502.21206v2); [alphaXiv listing](https://alphaxiv.org/abs/2502.21206)

**Agent backtests re-examined**
- "Profit Mirage" (Li, Zeng, Xing, Xu & Xu, 9 October 2025): FinMem, FinAgent, QuantAgent, FinCON and TradingAgents on GPT-4o all drop significantly in the post-cutoff generalisation setting; the authors attribute backtest gains to memorised history, not trading skill. A third-party review gives Sharpe-ratio decay of 51.48% to 62.23% (secondhand figure). The authors' proposed fix (FactFin) uses the LLM as a strategy generator, not a direct decision-maker — [arXiv 2510.07920](https://arxiv.org/abs/2510.07920); [Moonlight review](https://www.themoonlight.io/review/profit-mirage-revisiting-information-leakage-in-llm-based-financial-agents)
- FINSABER (Li, Kim, Cucuringu & Ma, arXiv May 2025, v3): over 2000 to 2024 with rolling windows and broader universes, the reported advantages of LLM strategies often vanish and they generally underperform traditional strategies. LLM strategies are too conservative in bull markets and take disproportionate losses in bear markets. The authors recommend prioritising trend detection and regime-aware risk controls over architectural complexity. Stated limitations include untuned traditional baselines and residual look-ahead bias from pretrained LLMs — [arXiv 2505.07078 v3](https://arxiv.org/html/2505.07078v3); [Moonlight review](https://www.themoonlight.io/review/can-llm-based-financial-investing-strategies-outperform-the-market-in-long-run)

**Forward or contamination-free benchmarks**
- StockBench (Chen et al., October 2025): agents make daily decisions on 20 Dow stocks over March to July 2025 (after model cutoffs; a simulation, not real money). Most agents, including GPT-5 and Claude-4, fail to beat equal-weight buy-and-hold on return and risk-adjusted return. Baseline 0.4% return with a 15.2% maximum drawdown; Kimi-K2 1.9%; Qwen3-235B 2.4%. Agents lagged in the downturn and led in the upturn — [arXiv 2510.02209](https://arxiv.org/abs/2510.02209v1); [Moonlight review](https://www.themoonlight.io/review/stockbench-can-llm-agents-trade-stocks-profitably-in-real-world-markets)
- DeepFund, "Time Travel is Cheating" (NeurIPS 2025): tested live on data after each model's cutoff, nine leading LLMs including DeepSeek-V3 and Claude-3.7-Sonnet incur net trading losses; in one 24-day window only Grok 3 mini Beta was positive — [arXiv 2505.11065](https://arxiv.org/abs/2505.11065); [NeurIPS 2025 poster](https://neurips.cc/virtual/2025/poster/121642)
- LiveTradeBench (November 2025): 50-day live evaluation of 21 LLMs; high general-benchmark (LMArena) scores do not imply better trading outcomes — [arXiv 2511.03628](https://arxiv.org/html/2511.03628v1)
- Agent Market Arena, "When Agents Trade" (October 2025): live daily decisions on TSLA, BMRN, BTC and ETH; agent framework matters more than the model backbone. Summaries conflict on the buy-and-hold comparison: some say agents often outperform it, another says most struggle to — [arXiv 2510.11695](https://arxiv.org/abs/2510.11695); [Moonlight review](https://www.themoonlight.io/review/when-agents-trade-live-multi-market-trading-benchmark-for-llm-agents)

### Inferences
- For this bot, any LLM-review prompt "validated" on historical NSE dates inside the model's training window proves nothing. Only decisions logged after the model's cutoff count, and each model upgrade resets that clock.
- The ChronoBERT result and the Glasserman-Lin result suggest look-ahead bias is not the whole story for narrow headline-sentiment scoring. The larger problem for a retail trader is the short horizon and cost of that signal (section 4), not that it is entirely an artefact.
- The forward benchmarks are short (24 to roughly 100 trading days) and cover a handful of US large caps or crypto. They show absence of demonstrated edge, not proof of harm. They do show two consistent behaviours relevant to a veto role: over-conservatism in rising markets and bullish bias in general.
- FINSABER's recommendation (trend detection and regime-aware risk control beat architectural complexity) points toward the bot's existing mechanical trend rules, not toward adding LLM judgement.

### Gaps
- Ludwig, Mullainathan & Rambachan, "Large Language Models: An Applied Econometric Framework": not searched. UNVERIFIED recollection: the paper argues that using an LLM for a prediction problem is valid only under "no training leakage" between the LLM's training data and the researcher's sample, which generally requires open models with documented training data and published cutoffs.
- Time Machine GPT, StoriesLM, DatedGPT: not searched; no sourced findings.
- FinBen and InvestorBench: not searched; no sourced findings.
- Exact numbers for LiveTradeBench and Agent Market Arena versus buy-and-hold were not retrieved.
- An "AI-Trader" live benchmark (arXiv 2512.10971) surfaced by title only.

## 3. Live results (real or paper money in real time), not backtests

### Takeaway
Live records are mostly unflattering: four of six frontier models lost between roughly 31% and 63% of real capital in 17 days in Alpha Arena Season 1, and the longest-running AI and sentiment ETFs have trailed the S&P 500 over their lives. The profitable live examples (Bridgewater AIA Labs, Minotaur, one Alpha Arena winner per season) are either institutional systems with heavy human infrastructure or short samples that cannot distinguish skill from luck.

### Cited Findings

**Nof1 Alpha Arena**
- Season 1 ran from 18 October to 3 November 2025 (some sources say 4 November): six models each traded USD 10,000 of real money in crypto perpetuals on Hyperliquid with no human intervention — [ForkLog](https://forklog.com/en/four-out-of-six-ai-models-suffer-losses-in-trading-tournament/); [GNcrypto](https://www.gncrypto.news/news/qwen-wins-alpha-arena-season-1-with-22-percent-returns/)
- Season 1 final returns as reported: Qwen 3 Max about +22.3%, DeepSeek about +4.9%, Claude Sonnet 4.5 about -30.8%, Grok 4 about -45.3%, Gemini 2.5 Pro about -56.7%, GPT-5 about -62.7%. Only two of six were profitable. Ending balances differ slightly between outlets — [ForkLog](https://forklog.com/en/four-out-of-six-ai-models-suffer-losses-in-trading-tournament/); [Benzinga](https://benzinga.com/crypto/cryptocurrency/25/11/48651974/chatgpt-lost-63-trying-to-trade-crypto-but-one-china-ai-made-a-healthy-profit); [iWeaver](https://iweaver.ai/blog/alpha-arena-ai-trader-showdown)
- Coverage reports Nof1 itself cautioning that success in Alpha Arena is very difficult and that early wins could reflect luck (attribution taken from a search summary; exact page not confirmed) — [Bitcoin.com News](https://news.bitcoin.com/alpha-arena-ai-trading-experiment-sees-china-outperform-western-models-so-far)
- Season 1.5 launched 19 November 2025 on US stocks with USD 10,000 per model. As of 8 December 2025 only Grok 4.2 remained profitable while the other models were recording losses — [ForkLog](https://forklog.com/en/ai-model-grok-4-2-triumphs-in-trading-tournament/)
- Season 1.5 winner: a "mystery model" later revealed as xAI's Grok 4.20, ending near USD 11,060 from USD 10,000 (about 10 to 12%). The figure traces to a social-media post and secondary coverage, not an official Nof1 table that I could open — [Yahoo Finance / Benzinga](https://finance.yahoo.com/news/elon-musks-grok-4-20-123855766.html); [Briefs](https://www.briefs.co/news/xai-s-grok-4-20-wins-live-trading-showdown-edging-out-openai/)
- A third-party tracker says Nof1's site still showed Season 1.5 as of August 2026 with a banner saying the models are no longer running — [TradeRank](https://www.traderank.ai/alpha-arena-leaderboard)

**Retail "ChatGPT portfolio" experiments**
- Finder (UK) ran a theoretical, no-money portfolio of 38 ChatGPT-picked stocks from 6 March 2023. By March 2025 it was up about 42% against about 27.6% for the average of the 10 most popular UK funds; the lead peaked near 23 points on 23 January 2025 — [European Business Magazine](https://europeanbusinessmagazine.com/finders-chatgpt-investment-fund-is-still-outperforming-the-uks-10-most-popular-funds/); [Finder](https://www.finder.com/uk/ai-investing)
- Caveats: it is not a real fund; the comparison group is the 10 most popular funds on Interactive Investor; the US-dollar portfolio is converted to sterling; ChatGPT's training data ended September 2021 at the time of selection; Finder itself said consumers should not take stock tips from AI — [KSL / CNN](https://www.ksl.com/article/news/business/chatgpt-can-pick-stocks-better-than-your-fund-manager/50638128); [Finder](https://www.finder.com/uk/ai-investing)
- Reuters (September 2025) reported that stock picking with ChatGPT requires financial knowledge and that adopters describe a high risk of getting it wrong — [Reuters via Tiger Brokers](https://www.itiger.com/news/2570057854)

**AI and sentiment ETFs**
- AIEQ (Amplify, formerly EquBot, AI Powered Equity ETF; launched October 2017): has lagged the S&P 500 since inception with higher volatility, per an October 2025 Motley Fool piece summarised by M1 — [M1](https://pages.m1.com/invest/stocks/AIEQ)
- AIEQ annualised alpha versus the S&P 500 of about -4.99% (measured since January 2024); maximum drawdown since inception -38.97% versus -33.99% for VOO — [PortfoliosLab AIEQ](https://portfolioslab.com/symbol/AIEQ); [PortfoliosLab AIEQ vs VOO](https://portfolioslab.com/tools/stock-comparison/AIEQ/VOO)
- AIEQ in 2026 was roughly level with the index: +14.2% year to date versus +13.9% for SPY as of 14 August 2026 — [Equibles](https://equibles.com/stocks/aieq)
- A Seeking Alpha review is titled "AIEQ: The AI ETF That Thinks, But Doesn't Outperform Yet" — [Seeking Alpha](https://seekingalpha.com/article/4797167-aieq-the-ai-etf-that-thinks-but-doesnt-outperform-yet)
- BUZZ (VanEck Social Sentiment ETF; inception 2 March 2021; 0.76% expense ratio; about USD 103 million in assets in September 2026): since-inception annualised return about 8.26% at NAV versus about 14.61% for the S&P 500 on the issuer's performance page seen in late October 2026 (as-of date not shown in the summary) — [VanEck BUZZ performance](https://www.vaneck.com/us/en/investments/social-sentiment-etf-buzz/performance/)
- LIVR (Intelligent Livermore ETF; launched about 18 September 2024; 0.69% net expense ratio): NAV return 7.52% versus 11.26% for the S&P 500 from inception to 30 June 2025, per the fund's annual report — [LIVR annual shareholder report](https://etfarchitect.com/wp-content/uploads/compliance/etf/TSR/LIVR_TSR-AR.pdf)
- LIVR later figures of 12.46% year to date and 10.18% since inception appear on a comparison page with no as-of date and no benchmark — [StockAnalysis](https://stockanalysis.com/etf/compare/livr)

**Hedge funds**
- Eurekahedge AI Hedge Fund Index: 9.8% annualised from December 2009 through July of the year of the report versus 13.7% for the S&P 500 total return, in a Wall Street Journal piece titled "Some hedge funds thought AI would help them beat the market. Then things got real." The index has beaten the average hedge fund but not the S&P 500 — [FN London / WSJ](https://fnlondon-spa-stg.sc.onservo.com/articles/some-hedge-funds-thought-ai-would-help-them-beat-the-market-then-things-got-real-d45be29e?mod=home); [HedgeCo](https://www.hedgeco.net/news/?p=58736)
- Bridgewater AIA Labs fund (machine learning as the primary basis of decisions; more than USD 5 billion raised): up about 11% in 2025 (one outlet says 11.9%) — [Fortune, 2 January 2026](https://fortune.com/2026/01/02/top-hedge-fund-performers-2025-bridgewater-de-shaw-citadel-millennium/?rand=8593); [Institutional Investor](https://www.institutionalinvestor.com/index%2Ephp/article/behind-bridgewaters-surge)
- A Reuters report of 2 July 2026 gives the AIA fund an annualised return of 11.3% since launch and about USD 4.5 billion in assets. The same report's 8.1% first-half 2026 gain is attributed in the headline to Bridgewater's flagship macro fund; the search summary attached it to AIA, so treat the 8.1% as unresolved — [The Star / Reuters](https://www.thestar.com.my/tech/tech-news/2026/07/02/bridgewater039s-flagship-macro-fund-gains-81-in-first-half-amid-market-volatility-sources-say)
- Minotaur Capital (Australia; "Taurient" system reads about 5,000 articles a day through LLMs): 13.7% in its first six months to January versus 6.7% for MSCI ACWI. The search summary dated this January 2026, but the companion Bloomberg piece is dated 14 February 2025, so the period is most likely August 2024 to January 2025 — [Hedgeweek](https://www.hedgeweek.com/ai-powered-hedge-fund-outperforms-market/); [Advisor Perspectives / Bloomberg](https://www.advisorperspectives.com/articles/2025/02/14/hedge-fund-startup-replaced-analysts-ai-beats-market)
- Minotaur later figures: 42.4% net of fees since inception "18 months ago" (undated article); 21.7% annualised since inception and 16.3% for the quarter to 30 June 2026, driven mainly by SK hynix and Micron, followed by a sharp memory-stock fall in July 2026. These come from a third-party aggregator, not a fund letter — [Finance News Network](https://www.finnewsnetwork.com.au/archives/finance_news_network3202230.html); [Buy Side Digest](https://www.buysidedigest.com/funds/minotaur-global-opportunities-fund)

### Inferences
- Equal-weighting the six reported Season 1 results gives an average of about -28% in 17 days (22.3 + 4.9 - 30.8 - 45.3 - 56.7 - 62.7, divided by 6), so the six accounts together turned USD 60,000 into roughly USD 43,000. This is my arithmetic from the reported figures, not an official total.
- Alpha Arena is leveraged crypto perps with intraday decisions. It says little directly about a monthly, unleveraged, delivery-only ETF bot. What transfers is the dispersion: the same market, the same prompt and data, and outcomes from +22% to -63%, which is what unvalidated discretionary decision-making looks like.
- Season winners changed between seasons (Qwen in Season 1, Grok 4.20 in Season 1.5), and each season is one sample of a few weeks. This is too short to attribute to skill.
- AIEQ (nine years), BUZZ (five and a half years) and LIVR (two years) are the longest audited live records of AI or sentiment stock selection available to a retail investor. All three trail a cheap index over their lives, and fees of 0.69 to 0.80% account for only part of the gap.
- Bridgewater and Minotaur show that institutions with proprietary data, research staff and risk systems can run ML- or LLM-centred funds profitably over one to two years. Minotaur's results are concentrated in a few semiconductor holdings in a strong market, so they do not isolate LLM skill. Neither result is evidence about a retail prompt reviewing trades.
- The Finder portfolio is a single static draw of large US quality stocks during a strong US bull market, measured against UK retail favourites. It is closer to a style-and-currency bet than a test of LLM stock picking.

### Gaps
- No official Nof1 final table for either season could be opened. Season 1.5's full per-model results, trade counts and fees, and whether any Season 2 ran in 2026, are unconfirmed. Sources also conflict on when Season 1.5 ended (December 2025 in one, a "launch" article dated November 2026 in another).
- Autopilot and similar "ChatGPT portfolio" copy-trading products: not searched.
- QRFT, Korean "ChatGPT-managed" ETFs, and the list of liquidated sentiment ETFs: not searched. UNVERIFIED recollection: several earlier sentiment ETFs closed (for example the first BUZZ-indexed fund from Sprott/ALPS in 2019), and Qraft's AI ETFs have a mixed record; check before citing.
- Man Group and Two Sigma: no fund-level performance attributable to LLMs was found; only Man's process description (section 6).
- Current since-inception figures for AIEQ and LIVR against the S&P 500 as of late 2026 were not found on an issuer page. The LIVR comparison is confirmed only to 30 June 2025.
- The Eurekahedge figure's end year is not stated in the summary and the index's current values were not retrieved; the URL found is a staging mirror of the FN London article.

## 4. News-sentiment evidence more broadly, including India

### Takeaway
Text-based return predictability is real in the academic record but is a short-horizon, high-turnover, small-stock effect that the positive LLM papers themselves say is exploitable only by very low-cost traders. India-specific studies exist but the ones found are small, index-level or correlational, without cost-aware out-of-sample trading tests.

### Cited Findings
- Ke, Kelly & Xiu, "Predicting Returns with Text Data" (NBER Working Paper 26186, 2019): introduces SESTM, a supervised sentiment score built for return prediction, estimated on Dow Jones Newswires — [NBER w26186](https://www.nber.org/papers/w26186)
- Chen, Kelly & Xiu's discussant summarises a main finding as returns responding slowly to news — [Wharton discussion slides](https://jacobslevycenter.wharton.upenn.edu/wp-content/uploads/2024/09/ExpectedReturnAndLLM_Discussion_SophiaZhengziLi_NoPause.pdf)
- Lopez-Lira & Tang: the initial reaction to headlines is captured by GPT-4 but is not tradable; the remaining drift is concentrated in smaller stocks and negative news; exploitation is feasible only for participants with sufficiently low transaction costs such as market makers; returns have declined as LLM adoption rose — [arXiv 2304.07619 v6](https://arxiv.org/pdf/2304.07619v6); [arXiv 2304.07619 v5](https://arxiv.org/pdf/2304.07619v5.pdf)
- A 2025 study in the Journal of Risk and Financial Management using about 1.86 million headlines finds that neither FinBERT news sentiment, historical returns nor implied volatility offers a consistently exploitable edge over market efficiency, with uneven benefit across models and sectors — [MDPI JRFM 18(8) 412](https://mdpi.com/1911-8074/18/8/412)

**India-specific**
- A 2025 study applies FinBERT to long news articles on non-financial Nifty 50 stocks to build a portfolio that it reports outperformed the market; the authors note that some strong performers were missed because news was the only selection input (URL-to-study mapping inferred from the search listing) — [Int. J. Indian Culture and Business Management 34(3), 2025](https://ideas.repec.org/a/ids/ijicbm/v34y2025i3p389-407.html)
- A study scraping Economic Times articles from January 2021 to February 2024 and scoring headlines with DistilBERT reports that news sentiment, especially on market conditions and political events, significantly affected Nifty 50 index movement — [Moonlight review of the Nifty 50 study](https://www.themoonlight.io/review/understanding-the-impact-of-news-articles-on-the-movement-of-market-index-a-case-on-nifty-50)
- A 2023 Indian-equities study using FinBERT and transfer entropy finds negative news influences prices more than positive news (URL mapping inferred) — [NITK repository](https://idr.nitk.ac.in/items/0a613590-601d-4a3b-a972-d0a9592ef292/full)
- An event study around Operation Sindoor (2025) aggregates FinBERT and other model scores from Google News RSS and tweets and aligns them with daily returns; it is a short-window correlation study — [IIETA](https://iieta.org/node/21504)
- An arXiv paper on Indian financial news questions whether common sentiment-quantification approaches are sound and introduces a tool tailored to Indian news (SENTInews) — [arXiv 2312.14978](https://arxiv.org/abs/2312.14978v1)

### Inferences
- A bot that runs once a day after the close, on free and delayed headlines, acts many hours after the news. The papers that find an edge trade at the next open or close after timestamped newswire items and rely on the portion of drift that survives the first reaction, mostly in small, illiquid stocks. That is the opposite of an ETF and large-cap delivery universe.
- The India studies found are of low evidential quality for a trading decision: index-level or Nifty 50 only, short samples (2021 to 2024), in-sample or correlational designs, general-purpose English models, and no reported transaction-cost or post-cutoff tests. None establishes that sentiment from Economic Times or Moneycontrol headlines improves a monthly momentum rule on NSE.
- Monthly trend and momentum rules already absorb slow-moving news through price. Adding a daily sentiment overlay would raise turnover on a strategy whose design advantage is low turnover.

### Gaps
- Tetlock (2007), "Giving Content to Investor Sentiment": not searched. UNVERIFIED recollection: high media pessimism in a Wall Street Journal column predicts downward pressure on the Dow followed by reversal within about a week, with effects too small to trade profitably after costs.
- Ke, Kelly & Xiu's results on speed of assimilation were not retrieved. UNVERIFIED recollection: most of the predictability arrives within one to two days, and it is slower and stronger for small and volatile stocks.
- Post-earnings-announcement drift speed, Heston & Sinha on news horizons, and any evidence on drift speed in India: not searched.
- No peer-reviewed study was found that combines NSE stock returns, Economic Times or Moneycontrol headlines, an LLM or FinBERT, and a cost-aware out-of-sample trading test. No study of Indian-language (Hindi or regional) financial news sentiment was found.

## 5. Retail-relevant cautions: SEBI, non-determinism, hallucination, prompt injection, cost, auditability

### Takeaway
SEBI's retail algo framework (circular of 4 February 2025, mandatory at brokers from 1 April 2026) distinguishes disclosed-logic "white box" algos from undisclosed "black box" algos, with research-analyst registration attached to black-box providers. Whether a personal bot whose orders depend on an LLM's judgement counts as black box is not addressed in anything found, and keeping the LLM out of order decisions avoids the question.

### Cited Findings

**SEBI retail algo framework**
- SEBI's circular "Safer participation of retail investors in algorithmic trading" is dated 4 February 2025 and followed a December 2024 consultation — [QuantInsti](https://blog.quantinsti.com/sebi-algo-trading-guidelines-retail-investors); [Business Today, 13 December 2024](https://www.businesstoday.in/markets/top-story/story/sebi-proposes-to-open-up-algo-trading-for-retail-investors-to-improve-market-integrity-457242-2024-12-13)
- White box (execution) algos have disclosed and replicable logic and may be registered on a fast-track basis. Black box algos have undisclosed logic: the provider must register as a Research Analyst, keep a research report for each algo, and re-register when the logic changes — [QuantInsti](https://blog.quantinsti.com/sebi-algo-trading-guidelines-retail-investors); [India Law](https://www.indialaw.in/md/blog/civil/sebi-retail-investors-algorithmic-trading/)
- The framework became mandatory for brokers on 1 April 2026 — [Fyers support](https://support.fyers.in/portal/en/kb/articles/what-are-the-new-sebi-rules-for-retail-algo-trading-from-april-01-2026); [Tradejini](https://www.tradejini.com/blogs/what-sebis-new-algo-trading-rules-mean-for-you)
- Broker guidance puts the registration threshold at 10 orders per second per exchange; below it no separate exchange registration of the strategy is needed. Brokers reject bursts above it — [Fyers blog](https://fyers.in/blog/sebi-algo-trading-rules-and-regulations-in-india/); [5paisa community](https://tradebetter.5paisa.com/t/important-update-sebi-algo-compliance-effective-1st-april/761)
- Broker guidance says API orders must come from a registered app tied to a whitelisted static IP regardless of order rate, with daily two-factor login; some retail guides say static IP applies only in some cases — [Upstox community guide](https://community.upstox.com/t/a-guide-for-our-api-algo-partners-and-clients/11826); [Kite Connect forum](https://kite.trade/forum/discussion/15865/sebi-regn-required-or-not)
- One broker-side blog says individuals running transparent (white box) logic for personal use below the threshold are treated as regular API users; another says a provider that cannot explain its strategy may need Research Analyst registration — [Liquide](https://blog.liquide.life/sebi-algo-trading-regulations-2026/); [Tradejini](https://www.tradejini.com/blogs/what-sebis-new-algo-trading-rules-mean-for-you)
- A legal commentary argues the circular does not clearly delineate registration requirements between black box and white box algos and calls black-box regulation "unfinished business" — [IRCCL](https://www.irccl.in/post/retail-algo-trading-under-sebi-s-lens-the-unfinished-business-of-black-box-regulation)

**SEBI on AI/ML**
- SEBI's consultation paper of 13 November 2024 proposed amending the Intermediaries, SECC and Depositories regulations to make regulated entities solely responsible for the consequences of AI tools they use, including outsourced ones — [SEBI board memorandum, December 2024](https://www.sebi.gov.in/sebi_data/meetingfiles/dec-2024/1735042007618_1.pdf); [Taxmann](https://www.taxmann.com/post/blog/sebi-proposes-ai-ml-governance-framework-for-securities-markets)
- On 20 June 2025 SEBI released a consultation paper with guiding principles for responsible AI/ML use in securities markets (comments to 11 July 2025), proposing a lighter regime for internal-only AI than for client-facing AI — [Business Today, 20 June 2025](https://www.businesstoday.in/markets/story/sebi-releases-draft-guidelines-for-responsible-ai-use-in-markets-seeks-public-input-by-july-481229-2025-06-20)
- Status conflict: one source says no final amendments had been gazetted as of September 2025, while another describes the June 2025 guidelines as notified — [Taxmann](https://www.taxmann.com/post/blog/sebi-proposes-ai-ml-governance-framework-for-securities-markets); contradicted by [Mondaq, Tech Law Bytes June 2025](https://www.mondaq.com/india/new-technology/1649892/tech-law-bytes-june-2025)

**Prompt injection, hallucination, consistency**
- TradeTrap (December 2025, simulated trading): injecting prompts that reverse directional cues cut one tool-calling agent's total return from 7.81% to 0.89% and its Sharpe ratio from 5.72 to 0.29 while trades rose from 47 to 391. Falsified news and social text, with prices left intact, pushed adaptive agents into narrative-driven overexposure — [arXiv 2512.02261](https://arxiv.org/pdf/2512.02261)
- An ICLR 2026 submission on multi-agent trading systems finds vulnerabilities in every agent role, with prompt attacks propagating through the pipeline — [ICLR 2026 listing](https://iclr.cc/virtual/2026/10016542)
- A separate August 2026 paper notes that putting a single LLM agent in a terminal safety role creates a single point of failure that can bypass all upstream deliberation — [alphaXiv 2608.24069](https://www.alphaxiv.org/abs/2608.24069)
- A Columbia study finds off-the-shelf LLMs show serious hallucination on financial tasks — [arXiv 2311.15548](https://arxiv.org/pdf/2311.15548)
- Man Group states its internal agent may misinterpret research concepts during code generation or create inconsistencies between stated method and actual execution — [Man Group](https://www.man.com/insights/what-ai-can-do-for-alpha)
- ChatGPT stock recommendations are described as lacking consistency and being prompt-sensitive — [arXiv 2603.19944 v2](https://arxiv.org/pdf/2603.19944v2)

### Inferences
- The SEBI black-box obligations found are written for algo providers who offer algos to clients. Nothing found says a self-coded personal bot below 10 orders per second needs Research Analyst registration, and a once-a-day bot is far below that threshold. This is my reading of broker summaries, not of the circular text, and is not legal advice.
- A pure mechanical rule set is "disclosed and replicable" in the plain sense. An LLM that can alter or block orders is not replicable (the same input can yield a different output, and the vendor can change the model). If the user were ever asked by a broker or exchange to describe the algo, a design where the LLM only annotates and logs, or at most triggers a deterministic "hold and alert the human" path, is easier to describe as white box than one where the LLM chooses orders.
- The August 2026 single-point-of-failure warning applies directly to a veto design: a terminal LLM veto fed raw news text can be steered by that text. Mitigations that follow from the findings: give the veto structured data (exchange corporate-action feeds, price ratios) before free text; treat headlines as untrusted input; make the veto one-directional (it can only block or defer a trade, never create or enlarge one); and cap how long a veto can stand without human confirmation.
- A one-directional veto bounds the damage from hallucination or injection to missed trades. For a trend system, missed entries during a rising market are the documented failure mode (over-conservatism in FINSABER and StockBench).

### Gaps
- The SEBI circular itself and NSE/BSE implementation circulars could not be opened (sebi.gov.in blocked). The definitions of white box and black box, and the treatment of self-developed algos used for self and family, are taken from broker blogs and law-firm notes.
- No SEBI, exchange or broker statement was found on whether LLM involvement in order decisions makes a personal algo "black box".
- Whether the November 2024 AI-responsibility amendments were finally notified is unresolved. UNVERIFIED recollection: amendments to the Intermediaries Regulations on responsibility for AI tools were notified in early 2025; this conflicts with one source above and needs checking on SEBI's site.
- LLM non-determinism studies (same prompt, different buy/sell answer) and current API cost per daily run: not searched; no sourced figures.

## 6. Which roles have reasonable support for a small trader

### Takeaway
Practitioner evidence supports LLMs as supervised research and engineering assistants (idea generation, code, summarisation, explanation) whose output passes the same tests as human work, and offers nothing found that supports an LLM as an unsupervised discretionary trade approver. A data-anomaly "circuit breaker" role is consistent with that pattern but I found no direct study of it.

### Cited Findings
- Man Group's AlphaGPT is an agentic research system (idea generation, coding, evaluation). Its evaluator applies the same statistical, risk and economic-rationale criteria as human research; signals go through an investment committee; developers inspect generated code line by line; Man says "we can't leave it unsupervised just yet". Several dozen signals have been approved for live trading — [Man Group, "What AI can do for alpha"](https://www.man.com/insights/what-ai-can-do-for-alpha); [Hedgeweek](https://hedgeweek.com/news/man-group-deploys-agentic-ai-for-quant-signal-discovery)
- CFA Institute's Enterprising Investor (5 February 2026) argues that firms deploying AI without validation, grounding and control frameworks risk embedding latent fragilities in the investment process, and cites a large study of production AI agents finding that successful deployments are simple, tightly constrained and continuously supervised — [CFA Institute, "Where AI ends and investment judgment begins"](https://rpc.cfainstitute.org/blogs/enterprising-investor/2026/where-ai-ends-and-investment-judgment-begins)
- CFA Institute's 2023 post lists hallucination and inaccuracy as core LLM risks and recommends governance focused on use and safety standards — [CFA Institute, 2023](https://rpc.cfainstitute.org/blogs/enterprising-investor/2023/chatgpt-and-large-language-models-their-risks-and-limitations)
- A February 2024 CFA Institute survey of 200 investment-firm representatives found mixed feelings and slow adoption of generative AI — [InvestmentNews](https://www.investmentnews.com/fintech/news/generative-ai-still-too-hot-to-touch-say-investment-firms-256862)
- AQR: Cliff Asness, previously sceptical, said the firm has "surrendered more to the machines", uses machine learning to size trades and sometimes acts on patterns researchers cannot fully explain. This concerns machine learning on large proprietary datasets in a USD 100 billion-plus firm, not LLM review of trades — [Bloomberg, 23 April 2025](https://www.bloomberg.com/news/articles/2025-04-23/aqr-bets-on-machine-learning-as-cliff-asness-becomes-ai-believer); [HedgeCo](https://www.hedgeco.net/news/?p=90739)
- Quant pioneer Martin Lueck (Aspect Capital) warned against handing trading over to AI while seeing opportunity in LLMs assisting quantitative researchers — [Financial Times (FT Chinese mirror)](https://d2uvt19t67bxij.cloudfront.net/interactive/263073/en)
- Pelster & Val conclude LLMs are useful as assistants in stock selection, not as the decision-maker — [Alpha Architect](https://alphaarchitect.com/chatgpt/)
- Profit Mirage's proposed remedy uses the LLM as a strategy generator whose output is then tested, not as the direct decision-maker — [arXiv 2510.07920](https://arxiv.org/abs/2510.07920)
- FINSABER recommends trend detection and regime-aware risk controls over more complex LLM architectures — [arXiv 2505.07078 v3](https://arxiv.org/html/2505.07078v3)

### Inferences
- Role (a), no LLM in signal generation for the mechanical monthly rules: supported. Every re-evaluation found (FINSABER, Profit Mirage, StockBench, DeepFund) fails to show a durable edge from LLM decision-making, and the positive papers concern a horizon and cost structure the bot cannot access.
- Role (b), veto-only circuit breaker on data anomalies (split or bonus not adjusted, ETF unit split, bad tick, suspension, merger or delisting): plausible and consistent with "simple, tightly constrained, supervised", but not evidenced. Most of these anomalies can be caught more reliably by deterministic checks (price change beyond a threshold versus index, exchange corporate-action file, zero volume, symbol missing from the bhavcopy). The LLM adds value only for the unstructured residue (reading an announcement), and should come after the deterministic checks, not replace them.
- Role (c), summarising and logging rationale in plain language: supported by the assistant framing in Man Group, CFA Institute and Pelster & Val, and carries no order risk if the text cannot influence orders. Hallucination risk remains, so explanations should be generated from the bot's own computed numbers passed in the prompt.
- Role (d), code and backtest review: supported by Man Group's use (with line-by-line human inspection). This is offline, has no latency or injection exposure, and probably has the best benefit-to-risk ratio of the four.
- A forecasting-style "LLM approves each trade on its merits" step is the role with the least support: it reintroduces the over-conservatism and bullish-bias behaviours seen in the benchmarks and cannot be validated at monthly frequency (section 7).

### Gaps
- No study or practitioner write-up was found that tests an LLM as a data-anomaly or corporate-action detector for a trading system, for India or anywhere.
- AQR's paper "Can Machines Time Markets?", Alpha Architect commentary beyond the Pelster & Val summary, Marcos López de Prado's work on backtest overfitting, and BIS, IMF and FSB reports on AI in finance (2024 to 2025): not searched. UNVERIFIED recollection: the FSB (November 2024) and IMF (October 2024 GFSR) reports focus on systemic issues such as third-party concentration, herding and model risk and do not assess retail alpha.
- No CFA Institute Research Foundation report from 2025 specifically on LLMs in investment management was confirmed; a practitioner guide by Firoozye, Mihov & Treleaven surfaced but its publisher was not confirmed.

## 7. If an LLM veto is kept, how to evaluate it honestly

### Takeaway
The literature's own standard is post-cutoff, forward-only evaluation against the un-intervened baseline; applied to a monthly bot, a veto fires so rarely that a statistically meaningful verdict on return impact would take decades, so the veto should be justified and judged as an error-catching control, not as a source of return.

### Cited Findings
- Pre-cutoff tests cannot identify forecasting ability; instructions to "ignore later data" and masking do not work; only post-cutoff evaluation is clean — [Lopez-Lira, Tang & Zhu, arXiv 2504.14765 v2](https://arxiv.org/html/2504.14765v2)
- Live benchmarks were created because backtests let LLMs use future knowledge ("time travel is cheating") — [DeepFund, arXiv 2505.11065](https://arxiv.org/abs/2505.11065)
- Agent performance drops substantially once tested past the cutoff — [Profit Mirage, arXiv 2510.07920](https://arxiv.org/abs/2510.07920)
- Benchmarks judge agents against a passive buy-and-hold baseline on both return and risk-adjusted return — [StockBench, arXiv 2510.02209](https://arxiv.org/abs/2510.02209v1)
- Short live windows are dominated by luck: Nof1 is reported to have warned that early wins could reflect luck, and winners differed between seasons — [Bitcoin.com News](https://news.bitcoin.com/alpha-arena-ai-trading-experiment-sees-china-outperform-western-models-so-far); [ForkLog](https://forklog.com/en/ai-model-grok-4-2-triumphs-in-trading-tournament/)
- General-capability rankings do not predict trading outcomes, so a newer model cannot be assumed to be a better reviewer — [LiveTradeBench, arXiv 2511.03628](https://arxiv.org/html/2511.03628v1)
- Results are sensitive to prompt design and can be degraded by manipulated text — [arXiv 2603.19944 v2](https://arxiv.org/pdf/2603.19944v2); [TradeTrap, arXiv 2512.02261](https://arxiv.org/pdf/2512.02261)

### Inferences
- Shadow book: run the un-vetoed mechanical portfolio in parallel on paper from day one, with identical prices and costs, and report both equity curves. The veto's contribution is the difference, and it must carry the cost of missed trades.
- Log for every review, not only vetoes: timestamp, model name and version, full prompt, inputs, raw output, decision, and the stated reason category (data anomaly, corporate action, suspension, "judgement"). Freeze the prompt; any change to prompt or model starts a new evaluation series.
- Count only decisions made after the model's training cutoff, which is automatically true for live logging but rules out "replaying" the veto over history to build a sample.
- Illustrative sample-size arithmetic (my assumptions, not sourced): if a veto fires 3 times a year and the one-month return difference between vetoed and un-vetoed outcomes has a standard deviation of 8%, detecting an average benefit of 2% per veto at roughly two standard errors needs about (2 x 8 / 2) squared = 64 vetoes, or about 21 years. With a 1% average benefit it needs about 256 vetoes. Return-based validation is therefore out of reach.
- A feasible alternative metric is precision on verifiable facts. For each veto, record afterwards whether the claimed anomaly was real (did the split, suspension or bad tick exist in exchange records?). True and false positives can be scored objectively within days, and a handful of false vetoes is enough to justify removing or narrowing the step.
- Pre-commit a removal rule, for example: drop the veto if false positives exceed true positives after the first 10 vetoes, or if any veto traces to instructions embedded in news text. Without a pre-committed rule, a rare lucky veto will be remembered and the missed trades will not.
- Splitting the log by reason category will show whether deterministic checks would have caught the same events. If they would, replace the LLM with the rule.

### Gaps
- No published methodology was found for evaluating a low-frequency LLM veto or overlay specifically; the approach above is assembled from the look-ahead and benchmark literature.
- Formal tools for short track records (Bailey & López de Prado's minimum track record length and deflated Sharpe ratio) were not searched and are not sourced here.
- The veto frequency (a few per year) is the task brief's assumption; no empirical base rate for corporate-action or data-error events in a monthly NSE ETF and large-cap rotation was found.
