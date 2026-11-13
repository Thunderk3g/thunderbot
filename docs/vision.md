# The grand idea

Thunderbot today is one person's paper-trading bot for NSE on Groww. This page says what it is meant
to become, how far it is from that, and how to judge it. It is written for two readers: the owner,
and a reviewer (human or agent) asked to find what is wrong with the project.

## In one paragraph

**An open, self-hosted portfolio manager for Indian investors, run by rules, assisted by an LLM, and
defined by a harness its owner can read and edit.** You bring your own broker key and your own LLM key.
You state your goals and limits in plain files. The system proposes what to hold, shows what each choice
would have earned after costs and tax, trades on paper until its own record justifies real money, and
keeps a journal that can show whether every part of it, the LLM included, earned its place. Nothing in
it is taken on trust: a feature that cannot be measured against doing nothing does not ship as a default.

## Who it is for

- **The owner-operator.** A part-time investor or trader who can follow a setup guide, wants to
  understand what the machine is doing with their money, and wants to change how it behaves without
  reading the engine's source.
- **The researcher.** Someone studying LLMs in portfolio management who needs a harness where a new
  prompt, model or strategy can be dropped in and scored on forward data with the same rules as
  everything else.

It is not for someone who wants a signal service, a guaranteed return, or a hosted account that trades
for them.

## What "harness" means here

The harness is everything that shapes a decision and is not the engine. The aim is that each part is a
file a person can open, edit, version and test:

| Part | What it holds | State today |
|---|---|---|
| **Policy** | Goals, horizon, capital, risk limits, allowed instruments, tax situation | Risk limits only, as settings; no goals or profile |
| **Plans** | The rules that decide what to hold (`worker/thunderbot/daily.py`, `strategy/`) | Five daily plans and four intraday generators, in Python |
| **Roles** | What each LLM call is for, its prompt, what it may return | Three roles, prompts as string constants in `llm/` |
| **Tools** | The data a role may read: prices, holdings, filings, news | Prices and the account's own state only |
| **Gates** | The tests a plan, model or role must pass before it gets more authority | A written checklist on the AI desk; nothing enforces it |
| **Journal** | Every input, prompt, reply, order and outcome, including for trades not taken | Built, and the strongest part of the system |

The engine underneath stays fixed and deterministic: sizing, limits, order placement, exits, the kill
switch. Editing the harness can change what is proposed. It cannot change what is allowed.

## Rules the design does not bend

1. **The LLM never has the last word on money.** It can veto, shrink, postpone, explain or propose a
   view. Code turns views into orders and hard limits run after it. No LLM output can enlarge a
   position, set a price or lift a limit.
2. **Every LLM role is scored forward, against its own absence.** A model has read the past, so a
   backtest of an LLM over dates before its training cutoff proves nothing. Roles are judged on paper
   and live decisions only, against the same decisions with the role switched off.
3. **Results are after costs and tax, next to the lazy alternative.** Every backtest is shown beside
   holding the index ETF and beside holding the same instruments with no timing.
4. **Authority is earned in stages.** Backtest, then paper, then small real money, then size. The
   project's own research found that most ideas fail the first two stages. That is the tool working.
5. **Fail closed, stay protected.** A failed LLM call skips the trade. A live position always has a
   stop at the broker. Live trading needs explicit switches set where the worker runs.
6. **One person, one instance, their own keys.** Broker credentials never leave a machine the owner
   controls. See [Bring your own keys](#bring-your-own-keys).
7. **Say what was found, including when it is "no edge".** Reports state the verdict in words.

## Where it stands against the idea

| Pillar | Today | Gap to the idea |
|---|---|---|
| Honest backtesting | Daily plans after Groww charges and asset-class tax, with a benchmark and a no-timing twin; walk-forward ML report with a worded verdict | Parameter sweeps use one train/test split with no correction for trying many settings; stock plans use today's index members (survivorship bias) |
| Paper trading | Daily investing and the intraday AI desk both run from a scheduled function, state in Postgres | Works; fills are simulated from 5-minute Yahoo bars, so they are optimistic about liquidity |
| Portfolio management | Fixed-mix and trend plans over three or four ETFs | No view of what the owner already holds, no goals, no risk profile, no portfolio construction beyond equal or fixed weights, no tax-aware rebalancing, no drift bands |
| LLM roles | Signal reviewer, intraday trader, rebalance checker; all veto or shrink only; prompts and replies journalled | Two separate client stacks (Anthropic SDK and an OpenAI-compatible client); the rebalance checker works with one provider only; no role yet does the thing LLMs are best evidenced for (reading text) |
| Measuring the LLM | Every setup is followed to its outcome whether taken or not; vetoed and approved signals compared by average R | No pass or fail gate decided in advance; no minimum sample; no control for the model changing under a fixed name |
| Editable harness | Strategy parameters and risk limits editable in the dashboard | Prompts, roles, plans and gates are source code; no versioning of a harness as a unit; no way to compare two harnesses on the same forward data |
| Bring your own keys | LLM by three environment variables; Groww by environment variables on the worker | No setup screen, no key check, no per-user storage; the whole system assumes one user |
| Explaining itself | Rationale stored with each decision; a setup tape on the AI desk | No plain-language account of how a trade happens, what each number means, or why the portfolio is what it is |
| Live trading | Engine with broker-side stops, static-IP check, order throttle, daily login confirmation | Not yet run with real money; the long-running engine keeps positions in memory only; delivery orders do not handle partial fills |

## Bring your own keys

"Anyone can come and use it" means **anyone can run their own copy**, with a setup flow that takes
their LLM key and their broker key, checks both, and starts them on paper. It does not mean one shared
website that holds everyone's broker credentials and places orders for them. Three reasons:

- **Groww's terms.** The API terms say the algo is for "yourself or your family" and that credentials
  must not be revealed to a third party. A site that holds users' keys puts every user in breach.
- **The exchange rules.** Since 1 April 2026 a person automating their own account must run the logic
  on their own static IP, one address per client. Anyone running logic and placing orders for unrelated
  people is an algo provider, which means exchange empanelment and hosting on the broker's servers.
- **Security.** A stored broker key plus a stored TOTP secret is standing authority to trade someone's
  account. The static-IP whitelist is the control that makes a stolen key useless; on a shared server
  the thief is already on the whitelisted address.

So the target is a copy that installs cleanly for one person: a first-run screen for the LLM provider
and key, the Groww credentials and the static-IP check; secrets encrypted inside that instance; data
fetched under that person's own entitlement. A public site can carry the documentation and a demo on
synthetic prices. A shared research site with an order agent on the owner's machine is a possible later
step, and only after a written view from the broker or a securities lawyer, because it is not settled
whether distributing software makes its author a provider. Sources are in
[`reports/LLM portfolio manager audit and research agenda.md`](../reports/LLM%20portfolio%20manager%20audit%20and%20research%20agenda.md).

## Stages

1. **Make it legible.** A "how it works" page; every number on the dashboard explained where it is
   shown; one page per decision showing rule, model, LLM, limits and outcome.
2. **Make it one person's in ten minutes.** Setup screen for the LLM key (any provider) and the Groww
   key, with a live check of each; one provider interface for every LLM role.
3. **Make the harness a thing.** Policy, roles and gates as versioned files; prompts out of the source;
   a harness has an id that is stamped on every decision it makes.
4. **Make the gates real.** Pre-registered pass or fail rules for plans and for each LLM role, enforced
   by the engine before authority widens.
5. **Make it a portfolio manager.** Import what the owner holds; goals and a risk profile; construction
   methods that beat equal weight out of sample or are not used; drift bands; tax-aware rebalancing;
   a monthly letter that explains the portfolio.
6. **Give the LLM its evidenced job.** Reading filings, results and news into structured, dated facts
   that rules can use and the journal can score.

## Brief for a reviewer

You are asked to find where this project falls short of the idea above, and where the idea itself is
wrong. Useful findings are specific, reproducible and ranked.

**Start here**

- `README.md`, then this page, then `docs/architecture.md` and `docs/ai-desk.md`.
- The path of an intraday decision: `worker/thunderbot/strategy/ai.py` → `ai/gbm.py` →
  `llm/trader.py` → `risk.py` → `ai/runner.py`.
- The path of a daily decision: `worker/thunderbot/daily.py` → `invest.py` → `llm/rebalance.py`.
- The research the design rests on: `reports/`.

**Run it**

```bash
cd worker && python -m venv .venv && . .venv/bin/activate && pip install -e ".[all,dev]"
pytest -q
thunderbot invest-backtest --strategy core_mix --years 15
thunderbot invest-backtest --strategy etf_trend --years 15
```

**Questions worth answering**

1. *Correctness.* Can any path let an LLM reply, a dashboard setting or a malformed row enlarge a
   position, move a price or skip a limit? Is there look-ahead anywhere in a backtest, a label or a
   feature? Do paper fills, training labels and the backtester agree on how a trade is filled?
2. *Honesty of the numbers.* Which reported figures would not survive a stricter test (more settings
   tried than disclosed, a lucky start date, survivorship, a benchmark that flatters)? What is the
   smallest change that would make each figure trustworthy?
3. *Live readiness.* What happens on a restart mid-session, a partial fill, a rejected stop order, a
   stale price, two schedulers firing at once, a broker token expiring mid-order?
4. *Security.* Where do secrets live, who can read them, what can someone do with the dashboard
   password alone, and what would change if a second user were added?
5. *The harness.* Which behaviours can an owner change without editing Python? Which should they be
   able to and cannot? Is any role's prompt doing a job that code should do, or the reverse?
6. *Fit to the idea.* Which pillar in the table above is furthest from its target for the least work?
   Which part of the idea is not supported by the evidence in `reports/`, and should be dropped?
7. *Legibility.* Could a part-time trader say, after ten minutes with the dashboard, why the last trade
   happened and what the bot will do next? If not, what is missing?

**Report format**

For each finding: what is wrong, where (`file:line`), how to reproduce it, why it matters to someone's
money or to the idea, and the smallest fix. Rank by harm. Separate what you verified by running it from
what you inferred by reading.

**Already known (verify, do not rediscover)**

- Parameter sweeps (`jobs.py`, `sweep`) split history once, 70/30, and flag a row "robust" with no
  correction for the number of settings tried.
- `thunderbot invest-backtest --years 18` shows a flat benchmark, because NIFTYBEES has no Yahoo history
  before January 2009 and the benchmark is only bought on the first day. The dashboard caps at 17 years.
- In daily investing, "stop" sells every holding (`invest.py`), which realises tax; for a portfolio
  the safer meaning is "stop trading and keep what is held".
- Live delivery orders build a reference id from the first six characters of the symbol
  (`invest.py`, `_live_fill`); symbols such as `M&M` put a character in it that the broker's format
  may reject. Unverified against a live account.
- A live delivery order that fills in part is treated as not filled, so the stored portfolio can drift
  from the broker's.
- The long-running intraday engine (`engine.py`) holds positions and the day's loss in memory; a
  restart mid-session forgets both. The serverless desk (`ai/runner.py`) keeps its state in the database
  and does not have this problem.
- The intraday model trains on about 60 days of 5-minute bars, the most Yahoo serves. Its own report
  says it has found no edge.
