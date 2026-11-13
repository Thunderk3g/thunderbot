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
| Honest backtesting | Daily plans after Groww charges and asset-class tax, with a benchmark and a no-timing twin; sweeps count every setting ever tried on the data, report a deflated Sharpe and the probability the winner was picked by luck | Stock plans use today's index members (survivorship bias) |
| Paper trading | Daily investing and the intraday desk both run from a scheduled function, state in Postgres | Fills are simulated from 5-minute Yahoo bars, so they are optimistic about liquidity |
| Portfolio management | Reads actual holdings (from Groww or a typed list); a drift corridor per holding; deposits routed to the furthest-below-target holding with no sales; a tax-year harvest plan that avoids a same-day round trip; guided baskets the owner places by hand | No goals or risk profile; no statement (PDF) import; no construction beyond fixed weights; no iNAV check on ETF orders (no data source) |
| LLM roles | Four roles behind one adapter, any provider; each can only veto, shrink or postpone; prompts and replies journalled with the model id and the cost of the call | No role yet does the thing LLMs are best evidenced for (reading filings and results) |
| Measuring the LLM | Each answer scored against the same setup with the model left out, after charges and call cost, inside a confidence sequence that stays valid under daily peeking; a role is obeyed only after it clears the gate and is demoted automatically if it turns into a drag | The intraday desk produces the only scored decisions, on too little data to settle anything soon |
| Editable harness | Policy, plans, roles, prompts and gates are files, validated against the engine's ceilings; a content id is stamped on every decision; model memory is written down, not fed back, unless the harness says otherwise | Files are edited on disk, not in the dashboard; no goals in the policy |
| Bring your own keys | A Setup page: paste an LLM key and a Groww key, each is checked live and stored encrypted in the install's own database; nothing stored there can enable real orders | No one-command install; the scheduler is still set up by hand; long-running workers read saved keys only at start |
| Explaining itself | Every decision is drawn as a trace through its gates and has its own page; words an LLM wrote are set in their own typeface; a Guide explains each step and term | No account of why the portfolio is what it is |
| Live trading | Paper, guided basket and automated modes; engine with broker-side stops, static-IP check, order throttle, daily login confirmation; engine state survives a restart; partial fills are booked | Not yet run with real money |

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

1. **Make it legible.** Done: a Guide, every decision drawn as a trace, and one page per decision.
2. **Make it one person's in ten minutes.** Mostly done: a Setup page for the LLM and Groww keys with
   live checks, and one adapter for every LLM role. Still to do: a one-command install.
3. **Make the harness a thing.** Done: policy, plans, roles and gates as versioned files, prompts out of
   the source, an id stamped on every decision. Still to do: editing from the dashboard.
4. **Make the gates real.** Done: each role is scored against its own absence with an anytime-valid
   confidence sequence, and promoted or demoted by rule. Sweeps are deflated for every trial.
5. **Make it a portfolio manager.** Partly done: actual holdings, drift corridors, deposit routing, a
   tax-year plan, guided baskets. Still to do: goals and a risk profile, statement import, a monthly
   letter that explains the portfolio.
6. **Give the LLM its evidenced job.** Not started: reading exchange filings, results and corporate
   actions into structured, dated facts that rules can use and the journal can score. This would also be
   the testbed with enough forward events to settle whether a model role helps.

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

- The Setup page stores keys encrypted with a key derived from `TB_SECRET_KEY`, or from the database's
  service key when that is unset. With the fallback, anyone holding the service key can decrypt them; a
  database dump alone cannot. Set `TB_SECRET_KEY` for real separation.
- The tax-year planner assumes a same-day sale and rebuy of one ticker is netted as intraday and books
  nothing, and offers a next-session rebuy or a swap into a twin ETF. That treatment, and how
  anti-avoidance rules apply to deliberate harvesting, were not checked against primary sources.
- There is no iNAV check before an ETF order: the Groww SDK exposes no iNAV and no free source was
  verified, so none was faked.
- The confidence sequence clips each setup's result to fixed bounds in R before scoring. A fat-tailed
  winner beyond the bound is under-counted.
- Guided baskets are reconciled against holdings the owner types in or Groww reports; nothing checks
  the price the owner actually got.
- The intraday model trains on about 60 days of 5-minute bars, the most Yahoo serves. Its own report
  says it has found no edge.
- Stock plans (momentum) use today's index members, so their backtests carry survivorship bias.
- No real order has ever been placed, and no call to a real LLM provider or to Groww has succeeded from
  the development environment.
