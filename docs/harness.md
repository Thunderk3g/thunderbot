# The harness

The harness is everything that shapes a decision and is not the engine. It is a directory of plain
files. You can open one, change it, and the worker uses the new version on its next pass. The engine
underneath (sizing, limits, orders, exits, the kill switch) is not in the harness and cannot be changed
from it.

```
harness/
  policy.toml               what you want: limits, memory mode, what your LLM costs
  gates.toml                how an LLM role earns authority, and how it loses it
  plans/investing.toml      which daily plan, until one is chosen on the dashboard
  plans/desk.toml           the intraday desk's settings
  roles/trader.toml         what the role is for, what it may do, what it reads
  roles/trader.md           the prompt it is given
  roles/signal_reviewer.*   the same pair for each role
  roles/rebalance_reviewer.*
  roles/day_reviewer.*
```

The copy that ships with the code is in `worker/thunderbot/harness/default/`. It reproduces the prompts
and settings the code used before they were moved into files.

## Editing it

There are two ways.

- **In the repository.** Edit the files under `worker/thunderbot/harness/default/` and deploy. This is
  the way to do it on Vercel, where the worker has no disk of its own.
- **In a directory of your own.** Copy the built-in harness out, edit the copy, and point the worker at it:

  ```bash
  python -m thunderbot.harness export ~/thunderbot-harness
  ```

  ```bash
  python -m thunderbot.harness check ~/thunderbot-harness
  ```

  Then set `TB_HARNESS_DIR=~/thunderbot-harness` where the worker runs. The directory must be a complete
  copy; a missing file is an error, not a fallback to the default for that file.

The worker re-reads the harness when a file changes. There is no restart.

## Every edit is checked

When the harness is loaded, every value is checked. A harness that fails any check is **not used**: the
built-in one runs in its place, and the problem is written to the log, shown on the dashboard's Harness
page, and recorded as an event. A bad edit can stop your change from taking effect. It cannot stop
trading, and it cannot widen what a model may do.

The checks name the file and the key, for example:

```
policy.toml [risk] risk_per_trade_pct: 5.0 is outside 0.05 to 2.0 (the ceiling is fixed in the code)
roles/rebalance_reviewer.toml may: this role may at most 'postpone' (postpone), got 'shrink'
gates.toml [defaults] n_min: 5 is outside 30 to 100000 (at least 30 scored setups)
```

### Ceilings no file can pass

| Limit | Ceiling |
|---|---|
| Risk per trade | 2% of capital |
| Daily loss limit | 10% of capital |
| Intraday leverage | 5 times |
| Orders | 9 a second |

They are constants in `worker/thunderbot/config.py`. `policy.toml` can ask for less. It cannot ask for
more, and it has no key for live trading, the static IP or credentials at all.

### What a role may do

| Role | May at most | In its file you can |
|---|---|---|
| `trader` (the desk) | take or skip, and shrink | restrict it to `veto` (take or skip only) |
| `signal_reviewer` (the long-running engine) | approve or reject, and shrink | restrict it to `veto` |
| `rebalance_reviewer` (daily investing) | postpone a rebalance by one session, twice at most | nothing more |
| `day_reviewer` | write a review and lessons; it affects no trade | nothing more |

No role can enlarge a trade, set a price or create an order, whatever its prompt says. The shape of each
role's reply is fixed in `worker/thunderbot/llm/adapter.py`: a reply that does not fit is a failed call.
For the two trade roles a failed call skips the trade. For the rebalance role a failed call lets the rule
go ahead, because the rule is the system and the check is an extra.

## The files

**`policy.toml`**

- `[memory] mode`: `journal_only` (the default) or `inject`. See [Memory](#memory).
- `[risk]`: limits you want, all optional: `capital`, `risk_per_trade_pct`, `max_daily_loss_pct`,
  `max_open_positions`, `max_trades_per_day`, `max_leverage`, `max_position_notional_pct`,
  `max_stop_distance_pct`. A value here is applied first; a value changed on the dashboard's Setup page
  is applied on top. Today the intraday desk and its training job read these. The daily investing runner
  and the long-running engine still take their limits from the environment and the Setup page.
- `[instruments] desk_symbols`: the stocks the desk watches. Empty means the built-in list.
- `[llm_cost]`: your provider's price per million tokens, in and out, and a rupee rate. With these set,
  every decision records what its call cost, and a role has to earn that back. No price is assumed for
  any provider: left at zero, the cost is recorded as zero.

**`plans/investing.toml`** names the daily plan and its parameters. It is used until a plan is chosen on
the dashboard's Plans page; after that the dashboard's choice stands.

**`plans/desk.toml`** holds the desk's own settings (`strict`, `min_stop_pct`, `min_prob`). A change made
on the Desk page is applied on top.

**`roles/<name>.toml`** says what the role is for (`label`, `purpose`), the most it may do (`may`), what
it is shown (`reads`), what happens when its call fails (`on_failure`) and which prompt file it uses
(`prompt`). `reads` and `on_failure` describe the role for whoever opens the file; the behaviour itself
is in the code.

**`roles/<name>.md`** is the prompt, word for word. This is the file most worth editing.

**`gates.toml`** is described under [How a role earns authority](#how-a-role-earns-authority).

## The harness id

Every harness has an id: twelve characters digested from every file in it. Change one word of one prompt
and the id changes.

The id is written on every decision the desk makes: on the signal, on the LLM's answer, and on the
outcome the setup went on to have. That is what lets two harnesses be compared on the same forward days,
and it is why an edited harness starts with a clean record: nothing earned under the old words is
credited to the new ones.

The dashboard's Harness page shows the id in use, each file as it was loaded, and the ids that came
before it with the number of decisions scored under each.

## Memory

After each close the end-of-day reviewer writes a short review and up to four lessons. They are kept and
shown on the Desk page in either mode.

- **`journal_only`** (the default): the lessons are never put into the trader's prompt. One day is two to
  six setups, which is noise, and a prompt that changes itself overnight is a different harness that has
  not been scored.
- **`inject`**: the newest eight lessons are shown to the trader before each decision. Turning this on is
  an edit to `policy.toml`, so it changes the harness id and the trader starts again in shadow. To study
  whether memory helps, run a harness with it and one without and compare their records.

## How a role earns authority

A scored role is in one of two stages.

- **Shadow.** It is asked. Its answer, prompt and cost are written down. The engine then carries on as if
  it had said "take at full size".
- **Active.** Its answer is applied.

The trader and the signal reviewer start in shadow. The rebalance reviewer starts active: it can only
postpone, and it is not scored in R.

### What is measured

Every setup a role was asked about is followed to its stop, target or the close, whether or not it was
traded. So for each one the role's worth can be computed exactly, against leaving the setup alone:

```
delta = (w - 1) x R - c
```

- `w` is the share of normal size the role asked for: 1 to leave it alone, 0 for a veto, in between for a
  shrink. An approval below the confidence the engine requires counts as 0, and so does a failed call
  that skips the trade.
- `R` is what the setup went on to make in units of risk, **after charges and slippage**, at the size the
  risk limits would have given it.
- `c` is what the call cost, in the same units.

| The role... | delta |
|---|---|
| vetoed a setup that lost 1R | +1R |
| vetoed a setup that made 2R | −2R |
| halved a setup that lost 1R | +0.5R |
| left a setup alone | −c: it has to earn back its own fee |

Comparing the average of approved setups with the average of vetoed ones does not measure this. A role
that approves setups making +0.35R and vetoes ones making +0.15R looks good on that comparison, and
every one of its vetoes gave up +0.15R.

Before scoring, R is clipped to the range in `gates.toml` (−2 to 4 by default) and a call's cost is
capped (0.5R by default), so one freak trade cannot decide the result.

### Looking as often as you like

The average of `delta` is the role's worth per setup. It is shown with a 95% range that is valid at
every look: a confidence sequence, not an ordinary confidence interval. Checking an ordinary interval
every day and acting when it looks good makes it wrong far more than 5% of the time. A confidence
sequence is built so that the truth lies inside every one of its ranges at once with 95% probability,
however often you look and whenever you stop. It is wider than an ordinary interval for that reason.

The one used is the predictable plug-in empirical-Bernstein confidence sequence of Waudby-Smith and
Ramdas (2024), in `worker/thunderbot/stats/confseq.py`, about sixty lines of plain Python.

### Moving between stages

| Move | When |
|---|---|
| Shadow to active | at least `n_min` scored setups (100 by default, never fewer than 30) **and** the lower bound is above zero |
| Active to shadow | the upper bound is below zero, **or** the running total is below `demote_cum_r` (−5R by default) |

The desk checks after every close. The Lab page can ask for a check at any time. Each move is recorded
as an event with the numbers behind it.

Only forward decisions on paper or live prices are scored. Replays of history and backtests never are,
because a model has read the past.

At about ten scored setups a day, 100 takes two weeks. With the default settings the range at 100 setups
is roughly ±0.5R wide, so only a large effect is proven that early; a role worth 0.15R a setup needs
several hundred.

## Sweeps in the Lab

Trying many settings on the same history and keeping the best is the commonest way to fool yourself, so
a parameter sweep reports two corrections (`worker/thunderbot/stats/overfit.py`).

- **Trials are counted across sweeps.** Every setting ever tried on a strategy, set of stocks and data
  source adds to one running count. Ten sweeps of six rows are sixty trials. Each row's Sharpe ratio is
  then **deflated** for that count (Bailey and López de Prado, 2014): the result is the probability that
  the row is better than the best of that many skill-less settings would look by luck. At least 0.95 is
  needed.
- **Probability of backtest overfitting** (Bailey, Borwein, López de Prado and Zhu). The days are cut
  into eight blocks. For each of the 70 ways of calling four of them "in sample", the best setting is
  picked there and ranked on the other four. The probability is the share of splits in which that winner
  landed in the bottom half. 20% or less is needed.

A row "clears the bar" only when both hold. Clearing it earns paper trading and nothing more. The sweep's
verdict says the count in words, for example: "No setting clears the bar once 60 trials are counted."

This replaces the old single 70/30 split and its "robust" flag. The in-sample and out-of-sample columns
are still shown.

## What reads the harness today

| Part | Reads from the harness |
|---|---|
| The intraday desk (`ai/runner.py`) | prompts, stages, memory mode, `[risk]`, `desk_symbols`, `plans/desk.toml`, cost prices; stamps the id on every row |
| The rebalance reviewer (`llm/rebalance.py`) | its prompt and cost prices |
| The end-of-day reviewer (`ai/reflect.py`) | its prompt |
| The long-running engine (`engine.py`) | the signal reviewer's or trader's prompt. It does not yet honour stages or stamp the id: a reviewer there is applied as before |
| Daily investing (`invest.py`) | `plans/investing.toml`, until a plan is chosen on the dashboard |
