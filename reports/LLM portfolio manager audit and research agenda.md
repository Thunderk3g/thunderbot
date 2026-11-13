# Sound engine, no edge yet: an audit of Thunderbot and what to study next

Thunderbot is better built than most open-source LLM trading projects and it has not found a way to make money that beats holding three ETFs. Both halves of that sentence come from evidence in this repository. The engine keeps the LLM in the one position the 2026 literature supports (it can veto or shrink, code places orders, hard limits run last), it journals what happened to every trade it did not take, and its backtests are after Indian charges and tax beside a lazy benchmark. Almost no open-source framework or retail product does all three. Against that, its own tests say the intraday desk loses about a quarter of its risk on every trade, no timing rule beat a fixed ETF mix after tax, and a check run for this report found the Nifty trend plan behind the index in **every one of 13 rolling five-year windows**. The gap between this bot and an LLM-powered portfolio manager is therefore not more strategies. It is five things the project does not have yet: a view of what the owner actually holds, goals and a risk profile, a test for overfitting that accounts for how many settings were tried, an LLM role that does what LLMs are evidenced to do (read text), and a harness that an owner can edit without touching Python. On "anyone can bring their keys": a shared website that holds users' Groww credentials is ruled out by Groww's terms and by the exchange's static-IP rule, so the workable form is one clean install per person. The study order that follows from all this is backtest-overfitting statistics first, then LLM memorisation and forward evaluation, then robust portfolio construction, then Indian factor and multi-asset evidence, then the personal-finance and regulatory layers.

**How to read the sourcing.** Three web-research passes ran for this report on 13 November 2026. Many Indian broker, law-firm and news hosts refused page fetches, so claims are tagged: no tag means the page or paper was read; *(snippet)* means a search extract of a page that could not be opened; *(own computation)* means a figure calculated for this report with the code in this repository on Yahoo Finance prices. The earlier reports in this folder already cover SEBI's retail-loss studies, Indian momentum evidence, costs and tax, ETF rotation and serverless hosting; they are cited, not repeated.

## Is the bot any good?

### The engineering is careful, and three checks confirm it

The code was read end to end along both decision paths, the test suite was run, and the daily plans were re-run on fresh data.

- **Tests.** 175 tests pass on `main`. CI, however, had been red for the last three pushes: the lint step failed on five small errors, so the test step never ran. That is fixed in the commit that accompanies this report.
- **The LLM cannot move money up.** `RiskManager.evaluate` (`worker/thunderbot/risk.py`) clamps the LLM's size multiplier to between 0 and 1, rejects on a veto or low confidence, and only then sizes the trade from capital and the stop distance. No path lets a reply change entry, stop or target. A failed call skips the trade.
- **Counterfactuals are kept.** Every setup, taken or not, is followed to its stop, target or the close and stored with the LLM's verdict (`ai/runner.py`, `signal_outcomes`). This is what lets the project ask whether the LLM helps.
- **Backtests are conservative where it matters.** Entry at the next bar's open, the stop assumed to hit before the target inside one bar, gaps filled at the open, charges on both legs, capital-gains tax by asset class, first-in first-out lots, and a "same ETFs, no timing" twin next to every rotation result (`backtest.py`, `daily.py`).
- **Re-run results match the repository's reports** *(own computation, 14 Nov 2011 to 13 Nov 2026, ₹5 lakh, after charges and tax)*:

| Plan | CAGR | Worst fall | Sharpe | Trades |
|---|---|---|---|---|
| Steady mix (Nifty 50, Next 50, gold; rebalanced each March) | 13.4% | −23.2% | 1.18 | 66 |
| Trend rotation (same ETFs, 200-day rule, liquid fund when out) | 9.1% | −15.5% | 1.02 | 256 |
| Holding NIFTYBEES | 12.0% | −36.3% | 0.86 | 1 |

### The Nifty trend rule costs return in every window tested

One new robustness check was run for this report, on the Nifty trend plan, because a single 15-year figure hides how much depends on the start date and on the chosen settings *(own computation, 1 Jan 2009 to 12 Nov 2026, after tax; the benchmark is NIFTYBEES before exit tax, which flatters the benchmark by up to about a point a year)*.

- **Thirty settings** (average length 100 to 300 days, buffer 0 to 2%, weekly or month-end checks) returned between **7.6% and 10.5% a year**; holding NIFTYBEES returned **13.4%**. The default setting ranked 9th of 30, so it was not cherry-picked, and no setting came close to the index.
- **Thirteen rolling five-year windows** with the default setting: the rule beat the index's return in **0 of 13** and had the shallower worst fall in **13 of 13**.
- **Sharpe** ranged from 0.60 to 0.83 against the index's 0.81, and only one of the 30 settings was above it. The rule buys a smaller fall and, in all but that one case, pays for it more than proportionally.

This agrees with the earlier reports: timing rules in India since 2009 have been a way to hold less risk, not a way to earn more. The dashboard already says so in words. The table above is the stronger statement and belongs next to the plan.

### What is weak, ranked by harm

| # | Weakness | Where | Why it matters | Smallest fix |
|---|---|---|---|---|
| 1 | Parameter sweeps split history once (70/30) and flag a row "robust" with no correction for how many settings were tried | `jobs.py`, `sweep` | With up to 60 settings on 60 days of bars, some will pass by luck; "robust" then invites paper trading of noise | Report a deflated Sharpe ratio and the number of trials; require a second untouched period before "robust" |
| 2 | The LLM's value has no pass or fail rule set in advance | AI desk, Results page | Vetoed-versus-approved average R is shown, but with no minimum sample or threshold any result can be read as encouraging | Pre-register the gate: metric, sample size, and what happens on a fail |
| 3 | Intraday model trains on about 60 days of 5-minute Yahoo bars | `ai/train.py` | Too little data to learn from or to reject on; the walk-forward report is honest but the sample cannot support a model | Record bars daily from now; treat the desk as a data collector until there is a year |
| 4 | The LLM writes "lessons" from one day and reads them the next, unscored | `ai/reflect.py` | One day is noise; a lesson can change behaviour without ever being tested, and the literature flags memory as a leak and an attack surface | Stamp each decision with the lessons shown; score lessons like any other role, or keep them out of the prompt |
| 5 | Stock plans use today's index members | `daily.py`, momentum | Already disclosed: about 10 points a year of the momentum result is survivorship | Rebuild membership from NSE bhavcopy and index change notices (see research area 1) |
| 6 | In daily investing, "stop" sells everything | `invest.py` | Realises tax and exits the market on a button press | Make stop mean "no new trades"; keep a separate, confirmed "sell all" |
| 7 | Live delivery orders: a partial fill is treated as not filled; the reference id takes characters from the symbol | `invest.py`, `_live_fill` | The stored portfolio can drift from the broker's; a symbol such as `M&M` may produce an id the broker rejects (unverified on a live account) | Record the filled quantity; build the id from letters and digits only |
| 8 | The long-running intraday engine keeps positions and the day's loss in memory | `engine.py` | A restart mid-session forgets open positions (broker stops still protect them) and resets the daily loss limit | Persist state as the serverless desk already does |
| 9 | Two LLM stacks | `llm/filter.py`, `llm/rebalance.py` use the Anthropic SDK; `llm/trader.py` an OpenAI-compatible client | The rebalance reviewer works with one provider only; "bring any key" is half true | One provider interface for every role |
| 10 | Paper fills assume the last price is tradable | `ai/runner.py` | Flatters results in thin names and fast moves | Fill at the next bar's open, as the training labels do, so paper and labels agree |
| 11 | `invest-backtest --years 18` shows a flat benchmark | `daily.py` | NIFTYBEES has no Yahoo history before January 2009 and the benchmark is bought only on day one; the dashboard caps at 17 years so this is latent | Buy the benchmark on its first available price, or refuse the window |
| 12 | Two cost models with slightly different rates | `costs.py`, `daily.py` | Intraday and delivery charges can drift apart | One schedule, two views |

None of these lets an LLM enlarge a trade or bypass a limit. Items 6 to 8 matter only once real orders are placed, which has not happened.

### Verdict

- **As engineering:** good. The design choices are the ones a careful practitioner would make, and they are tested.
- **As a money-maker:** not shown. The best plan is a fixed mix that needs no bot, and the intraday desk reports no edge. The project says this itself, which is its most unusual quality.
- **As a product someone else could use:** not yet. It assumes one user, environment variables and a reader of the source.

## How it compares with the market

### Open-source frameworks give the LLM far more authority

| Project | What the LLM decides | Backtest | Live broker |
|---|---|---|---|
| [TradingAgents](https://github.com/TauricResearch/TradingAgents) (122k stars) | Everything: analysts, bull and bear debate, trader, risk team, an LLM portfolio manager approves | Yes | No |
| [ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) (65k) | Investor-persona agents; places no trades | Yes | No |
| [AI-Trader](https://github.com/HKUDS/AI-Trader) (23k) | Agents publish and copy signals | Paper | Names several |
| [FinRobot](https://github.com/AI4Finance-Foundation/FinRobot) (8k) | Narrative only; code computes the numbers | Notebook | No |
| [RD-Agent](https://github.com/microsoft/RD-Agent) (15k) | Proposes factors and models; code backtests them | Yes | No |
| [NautilusTrader](https://github.com/nautechsystems/nautilus_trader) (32k), [freqtrade](https://github.com/freqtrade/freqtrade) (57k) | Nothing; no LLM | Yes, same code live | Crypto, IBKR |
| [OpenAlgo](https://github.com/marketcalls/openalgo) (3k, India) | Via MCP an assistant can place orders | Limited | 38 Indian brokers incl. Groww |
| **Thunderbot** | Veto, shrink or postpone only | Yes, after tax | Groww (unused) |

Thunderbot sits at the conservative end with FinRobot and RD-Agent, where code computes and judges and the LLM proposes or narrates. Two ideas are worth borrowing: OpenAlgo's **semi-auto mode**, in which each order waits for a human tap, and TradingAgents' practice of settling past decisions against realised returns and feeding that back, provided the feedback is scored (weakness 4).

### Forward evidence: general LLMs do not beat buy-and-hold

The earlier notes in `research_notes/` cover this; the additions from this pass are below.

- **FINSABER** ([arXiv 2505.07078](https://arxiv.org/html/2505.07078v4)) re-ran published LLM agents over 2004 to 2024 with delisted stocks included. Buy-and-hold had the highest Sharpe in every setup; the agents showed no significant alpha, and were too cautious in rising markets and too aggressive in falling ones.
- **StockBench** ([arXiv 2510.02209](https://arxiv.org/html/2510.02209v2)): 13 models on 20 Dow stocks after their training cutoffs returned between +2.5% and −2.8% against +0.4% for buy-and-hold.
- **Agent Market Arena** ([arXiv 2510.11695](https://arxiv.org/html/2510.11695v2)) and **LiveTradeBench** ([arXiv 2511.03628](https://arxiv.org/abs/2511.03628)): the agent's design matters more than which model is inside it, and general benchmark scores do not predict trading results.
- **Alpha Arena**: four of six models lost money in season one, and in the follow-up on US stocks only 6 of 32 result sets were positive *(snippet)*.
- **Memorisation**: models recall exact pre-cutoff prices, and telling them to ignore the future does not work ([Lopez-Lira, Tang and Zhu](https://arxiv.org/html/2504.14765v2)); almost every published agent fails against a random baseline once past its cutoff ([Profit Mirage, arXiv 2510.07920](https://arxiv.org/abs/2510.07920)).
- **Field quality**: a 2026 survey of 80 empirical studies found only 62.5% used time-consistent splits, 58.8% modelled transaction costs, and none shipped a full reproduction package ([arXiv 2605.19337](https://arxiv.org/html/2605.19337)).

**The veto design itself is untested in the literature.** No robust study of an LLM veto over rule-based signals was found. Its classical cousin is meta-labelling, where a second model filters and sizes the first model's bets ([Hudson & Thames](https://hudsonthames.org/does-meta-labeling-add-to-signal-efficacy/)). One practitioner's pre-registered test of a frozen GPT veto failed: it cut trades but removed winners ([QuantConnect forum](https://www.quantconnect.com/forum/discussion/21370/a-frozen-llm-veto-failed-its-added-value-gate-then-the-mechanical-control-failed-locked-final/), one self-reported case). Thunderbot's shadow journal is exactly the instrument needed to answer this, and a clean forward answer on Indian data would be new.

### Where LLMs do add value

- **Reading news.** The best out-of-sample result is [Lopez-Lira and Tang](https://arxiv.org/pdf/2304.07619v6): on 4,123 US stocks after the model's cutoff, a GPT-4 long-short sentiment portfolio had a Sharpe of about 3 before costs. Two warnings come with it. The effect is strongest in small stocks and needs very low costs, and it is decaying fast: Sharpe 6.5 in late 2021, 3.7 in 2022, 2.3 in 2023, 1.2 in early 2024.
- **Proposing factors for code to test.** [RD-Agent(Q)](https://arxiv.org/html/2505.15155v2) and [AlphaAgent](https://arxiv.org/abs/2502.16789) report gains on Chinese A-shares (authors' own figures). The LLM writes hypotheses and code; a deterministic backtester judges.
- **Explaining, extracting, compiling policy.** Universal in products, with no return evidence, and the safest place to start.

### What retail products treat as standard

Products checked: Composer, QuantConnect, Robinhood's agentic trading beta, Public, TradingView, and in India Streak, AlgoTest, Groww's GR-1 and Dhan's Fuzz (vendor pages; details in the research pass). Indian brokers are deliberately keeping their assistants away from automated stock picks *(snippet, [niftytrader](https://www.niftytrader.in/markets/indian-brokerages-turn-to-ai-for-smarter-portfolio-analysis-avoid-automated-stock-picks/))*.

| What a credible platform has in 2026 | Thunderbot |
|---|---|
| 1. Deterministic execution and hard limits outside the model | Yes |
| 2. LLM roles judged forward only, never on pre-cutoff backtests | Yes by design (LLM off in backtests); no stated cutoff check |
| 3. The LLM's marginal value measured against the no-LLM control, with a gate set in advance | Measured; **no gate** |
| 4. Walk-forward backtests with costs, a survivorship-free universe and a benchmark | Costs and benchmark yes; **one split; survivor universe for stocks** |
| 5. Kill switch, staged authority, an explicit rule for LLM outages | Yes; stages are written down, not enforced |
| 6. Append-only journal: inputs, prompt version, model version, output, action, outcome | Yes, except **prompt and harness version** |
| 7. Schema-checked outputs; free text never reaches orders | Yes |
| 8. Paper mode identical to live; human approval for anything that widens risk | Paper yes (fills differ slightly); **no per-order approval mode** |
| 9. Protection against poisoned inputs and leaking memory | Low exposure today (no news); **unscored lessons** |
| 10. Regulatory fit, pinned model versions, cost budget per decision | Static IP, throttle, limit orders yes; **model not pinned, no cost budget** |
| No-code or plain-language strategy definition (table stakes in products) | **No** |
| Plain-language explanation of each decision | Partly |

## Bring your own keys: one install per person

### A shared site holding broker keys is ruled out three ways

- **Groww's terms** (section XI, read): "You shall use the algo only for yourself or your family"; passwords must not be "revealed to any third party"; one static IP is mapped to the API keys ([terms](https://groww.in/terms-and-conditions/)).
- **The exchange framework.** A static IP at the client's end is required for a person using the API for their own algo, and that person must "host the Algo using a static IP at their end where Algo logic resides" ([NSE FAQ, 3 Nov 2025](https://nsearchives.nseindia.com/web/sites/default/files/inline-files/FAQ_Retail_Algo_03112025_NSE.pdf), Q3, Q5, Q6). Anyone providing algos to others must be empanelled with the exchange, host on the broker's servers, and register as a Research Analyst if the logic is a black box (same FAQ, Q4 and Q5; [SEBI circular of 30 Sep 2025](https://www.sebi.gov.in/sebi_data/attachdocs/sep-2025/1759232056254.pdf) for the dates, full application from 1 April 2026). API market orders are not permitted (Q11), which the engine already respects.
- **Security.** Groww's TOTP flow is unattended by design, so a stored key and TOTP secret are standing authority to trade. The IP whitelist is what makes a stolen pair useless; on a shared server the thief is on the whitelisted address already.

| | Shared site holding broker keys | Shared research, order agent on the owner's machine | One install per person |
|---|---|---|---|
| Rules | Needs exchange empanelment and broker hosting; users breach Groww's terms | Unsettled: fine only if all trading logic runs on the owner's side | The route the rules describe for a person's own algo; what OpenAlgo does |
| Security | Worst: every user's keys on one whitelisted server | Medium | Each person's risk is their own machine |
| Work | Very large | Large | Modest |
| Friction for the user | Lowest | Medium | Highest: a static IP and a setup step |

**One point is unsettled and needs a professional view before the project is promoted to others:** no circular defines "algo provider" for someone who only distributes free, open-source software that each user runs and edits. The self-hosted position is the strongest available but is untested.

### What the setup should do

1. A first-run screen: pick an LLM provider, paste a key, press "check". The check lists the provider's models and makes one tiny call.
2. A second step for Groww: paste the TOTP key and secret on the machine that will place orders; the existing `login-check` and `check-ip` commands become buttons.
3. Keys are stored encrypted inside that install (AES-GCM with a master key kept outside the database), shown back only as a masked hint, and never logged.
4. Backtests fetch prices under the user's own entitlement. Yahoo's interface is described as for personal use ([yfinance](https://pypi.org/project/yfinance)) and NSE data needs a licence to redistribute *(snippet)*, so a public site should demo on synthetic data only.

### One LLM interface for every role

Use two official clients behind one small adapter: the OpenAI-compatible protocol with a base URL for xAI Grok (`https://api.x.ai/v1`), Groq (`https://api.groq.com/openai/v1`), OpenAI, Gemini and OpenRouter, and the Anthropic client for Claude. Reasons and cautions:

- Strict JSON-schema output is uneven: Groq guarantees it on two models only and Gemini's compatible layer is reported to ignore schemas at times *(snippet)*. Keep the current approach of asking for JSON and validating every field, and treat a bad reply as a failed call.
- Do not hardcode model names or prices; they change monthly. List them from the provider at setup.
- Avoid a catch-all routing library in a process that holds broker credentials. LiteLLM's PyPI releases 1.82.7 and 1.82.8 carried a credential stealer for about 40 minutes on 24 March 2026 ([InfoQ](https://infoq.com/news/2026/03/litellm-supply-chain-attack/)). Pin dependencies by hash.
- Record the exact model id returned with every decision, so a provider silently changing a model under a fixed name shows up in the journal.

## Strategies: fewer than you would like

The honest list of things worth adding is short, because the evidence keeps saying that the fixed mix is hard to beat.

| Idea | Evidence | Worth building? |
|---|---|---|
| **Drift bands** in place of a fixed March rebalance | Vanguard's simulations favour annual rebalancing for investors who do not harvest tax ([Vanguard 2022](https://corporate.vanguard.com/content/dam/corp/research/pdf/rational_rebalancing_analytical_approach_to_multiasset_portfolio_rebalancing.pdf)); Daryanani's 20% bands beat calendar rules on 1992 to 2004 data, with mixed replications | Yes: cheap, and in India every sale is taxed, so trading only when far off target matters more |
| **Cash-flow rebalancing** (new money goes to whatever is under target) | Follows from the tax point; no sale, no tax | Yes |
| **Tax-harvest step** each March (use the ₹1.25 lakh exemption; realise losses) | India has no statutory wash-sale rule *(snippet)*; general anti-avoidance exists; a same-day sell and rebuy is netted as intraday | Yes, as a suggestion the owner confirms; get a chartered accountant's view |
| **Low-volatility sleeve** | Found on NSE in three studies over 2001 to 2020 with one contrary; an independent 2006 to 2025 test puts it near 14% a year with a −43% fall; NSE's own backtests show 18 to 19% but recent live five-year figures are far lower *(snippet, unverified)* | Test it; as an ETF, not a stock picker |
| **Volatility cap** (hold less when recent volatility is high) | Thins the left tail for equities ([Harvey et al.](https://quantpedia.com/the-impact-of-volatility-targeting-on-equities-bonds-commodities-and-currencies)); real-time versions disappoint and costs eat it ([Cederburg et al.](https://econpapers.repec.org/RePEc:eee:jfinec:v:138:y:2020:i:1:p:95-117)) | Test it honestly; expect a smaller fall, not more return |
| **Volatility-scaled momentum** | Doubled momentum's Sharpe in US data ([Barroso and Santa-Clara](https://econpapers.repec.org/RePEc:eee:jfinec:v:116:y:2015:i:1:p:111-120)); no peer-reviewed Indian test was found | A research project, and a publishable one |
| **Optimised weights** (mean-variance, risk parity, HRP) | With few assets, equal weight is hard to beat out of sample ([DeMiguel, Garlappi and Uppal](https://ideas.repec.org/a/oup/rfinst/v22y2009i5p1915-1953.html)); Indian HRP evidence is thin and mixed | Only as a tested option beside equal weight |
| **LLM views into Black-Litterman** | One workshop paper, nine months of data, results driven by each model's fixed style ([Lee et al.](https://arxiv.org/abs/2504.14345v1)) | Later, forward-tested, with tiny tilts |
| **News or filings as a signal** | Real but decaying, strongest where costs are highest | First as dated facts in the journal, not as a trading rule |
| More intraday rule sets | The desk's own report and SEBI's loss studies | No |

Two changes to the market itself help daily plans: NSE's **closing auction** for F&O stocks went live on 3 August 2026 and sets the official close, so a rule that decides on the close can now trade at it; and new ETF price-band and pre-open rules took effect in September 2026 *(both snippet; verify before relying on them)*. ETF orders should be limit orders checked against iNAV.

## What to research, in order

For a solo researcher-builder, ranked by how much each changes what the system can honestly claim.

1. **Backtest overfitting statistics.** The deflated Sharpe ratio ([Bailey and López de Prado](https://papers.ssrn.com/abstract=2460551)), the probability of backtest overfitting ([Bailey et al.](https://papers.ssrn.com/abstract=2326253)), combinatorial purged cross-validation (López de Prado, *Advances in Financial Machine Learning*, chapters 7 and 11 to 14), and the t above 3 hurdle ([Harvey, Liu and Zhu](https://papers.ssrn.com/abstract=2513152)). Trying about 45 settings on five years of data almost guarantees a backtest Sharpe of 1 with nothing behind it. Then survivorship-free Indian data: NSE's daily bhavcopy files include delisted stocks, and a 2026 paper rebuilt Smallcap 250 membership from them and found 16% delisted ([arXiv 2603.19380](https://arxiv.org/abs/2603.19380)). *Fixes weaknesses 1 and 5. Highest return on study time.*
2. **Evaluating an LLM that has read the past.** Memorisation and cutoff-aware testing ([Lopez-Lira, Tang and Zhu](https://arxiv.org/html/2504.14765v2); [FINSABER](https://arxiv.org/html/2505.07078v4); [StockBench](https://arxiv.org/abs/2510.02209v1); the counterpoint that the bias is modest for news with a downstream regression, [arXiv 2502.21206](https://arxiv.org/abs/2502.21206)). Then experiment design for the veto: pre-registration, sample size, sequential testing, meta-labelling. *This is where the project can produce an original result.*
3. **Robust portfolio construction for small accounts.** Why equal weight is hard to beat, shrinkage ([Ledoit and Wolf](https://econ-papers.upf.edu/papers/691.pdf)), HRP ([López de Prado](https://papers.ssrn.com/abstract=2708678)), volatility targeting and its critics, rebalancing bands, fractional Kelly. Libraries to learn with: [skfolio](https://pypi.org/project/skfolio/) (BSD, ships walk-forward and combinatorial purged cross-validation) and [PyPortfolioOpt](https://pypi.org/project/pyportfolioopt/) (MIT, whole-share allocation).
4. **Indian factor and multi-asset evidence.** Low volatility, quality and multi-factor indices, kept strictly apart as pre-launch backtest and live record; gold as the diversifier; a properly costed Indian version of Faber's tactical allocation. *No peer-reviewed Indian dual-momentum or tactical-allocation study was found, so this is open ground.*
5. **Agent harness design.** Separating advice from execution, staged authority, memory with an "outcome embargo", prompt-injection through news and tools ([TradeTrap, arXiv 2512.02261](https://arxiv.org/abs/2512.02261)), journals that carry prompt and model versions ([survey, arXiv 2605.19337](https://arxiv.org/html/2605.19337)).
6. **Goals and risk profiling.** Goal-based portfolios ([Das, Markowitz, Scheid and Statman](https://www.cambridge.org/core/product/4B23CFB326982C52014A1BA447FA9244)); why questionnaires are unreliable and capacity matters more than stated tolerance ([CFA Institute Research Foundation](https://rpc.cfainstitute.org/research/foundation/2017/new-vistas-in-risk-profiling)). LLM advice studies show home bias and risk inflation ([PLOS ONE 2025](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0325459)), so capacity should be computed and the LLM used to ask and explain.
7. **Indian tax mechanics and holdings import.** Set-off rules, the annual exemption, the Income-tax Act 2025 renumbering; [casparser](https://pypi.org/project/casparser/) reads CAMS, KFintech, NSDL and CDSL statements. The Account Aggregator network is closed to anyone who is not a regulated entity, so statements and the broker's holdings API are the realistic route.
8. **The regulatory perimeter.** The retail algo framework, the Investment Adviser and Research Analyst rules as amended in December 2024 (advisers must disclose AI use), and the ₹50 lakh portfolio-management threshold. A one-time study followed by a lawyer, before anything is offered to other people.
9. **Execution at retail size.** Impact cost, iNAV, the closing auction. Small for monthly ETF trades; study when real orders start.

## The harness, concretely

What "a well-written harness that people can edit" would consist of, each as a versioned file with a schema, and the whole set stamped with one id on every decision:

- **`policy`**: goals with amounts and dates, capital, what may be held, risk limits, tax situation.
- **`plan`**: target weights or a rule, rebalance trigger (date or band), cash asset.
- **`roles/`**: one file per LLM role with its purpose, its prompt, the data it may read, the exact shape of its reply, what it is allowed to affect (nothing, postpone, veto, shrink, a bounded tilt), and what happens when it fails.
- **`gates`**: for each plan and role, the metric, the sample size and the threshold that must be met before it gains authority, and the rule for losing it.
- **`tools/`**: read-only data sources, each with the time its data was known.

The engine reads these and nothing else. Changing a prompt creates a new harness version, its decisions are scored separately, and two versions can be compared on the same forward days. That last property is what would make this a research instrument and not just a bot.

## Build order

1. **Legibility.** `docs/how-it-works.md` now exists; bring it into the dashboard with a page per decision.
2. **Keys and setup.** One LLM interface; a setup screen with live checks; encrypted storage per install.
3. **Honest sweeps and real gates.** Deflated Sharpe and trial counts in the Lab; a pre-registered gate for the LLM, enforced.
4. **Harness as files.** Prompts out of the source; version id on every decision.
5. **Portfolio layer.** Holdings import, goals, drift bands, cash-flow rebalancing, a tax-harvest suggestion.
6. **A reading role.** Dated facts from filings and results, journalled and scored before any rule uses them.
7. **Live fixes** (weaknesses 6 to 8) before the first real order.

## What this report did not verify

- No real order has been placed, so every statement about live behaviour comes from reading code.
- The SEBI and NSE points rest on the NSE FAQ and one SEBI circular that were read, plus broker and law-firm summaries that were mostly seen as search extracts. The NSE implementation circulars themselves could not be opened.
- NSE factor-index live figures, the September 2026 ETF rule date, the general anti-avoidance threshold and the same-day netting treatment are unverified.
- Provider model names, prices and structured-output behaviour were not tested against live APIs.
- Yahoo prices carry known errors that `daily.py` repairs; a second data source was not used to cross-check the re-run figures.
