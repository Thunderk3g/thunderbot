# How Thunderbot works, in plain words

Written for someone who trades a little and wants to know what this thing does with a rupee, without
reading the code. File names are given so you can check each claim.

## Two bots share one dashboard

| | The investing bot | The AI desk |
|---|---|---|
| What it trades | A few ETFs: Nifty 50, Next 50, gold, a liquid fund | 24 liquid Nifty 50 stocks, intraday only |
| How often it decides | Once a day at 15:10 IST; trades a few times a year | Every 5 minutes, 09:30 to 14:30; flat by 15:05 |
| Who decides | A fixed rule (a "plan") | Four rule sets propose, a small model scores, an LLM takes or skips |
| What the evidence says | The plain fixed mix beat every timing rule after tax | No edge found; it loses about a quarter of its risk per trade |
| Why it exists | This is the part meant to hold money | To keep testing, on paper, whether an edge ever appears |

Both are **paper trading** unless you set up a machine with a registered static IP and turn on three
separate switches. Nothing on the dashboard can turn on real orders.

## What wakes it

There is no program running all day. A timer in the database (Supabase) calls a small function (on
Vercel) every five minutes in market hours. The function wakes, reads what it knew last time from the
database, does one pass, writes everything back and exits. If a call is missed, the next one catches up.
(`worker/thunderbot/serverless.py`)

## The investing bot, step by step

1. **15:10 IST, every trading day.** It loads daily prices and adds today's live price as today's bar.
2. **Is today a decision day?** Most plans only decide at month-end, or once a year. On other days it
   records the portfolio's value and stops.
3. **The plan gives target weights.** For example "a third each in NIFTYBEES, JUNIORBEES and GOLDBEES",
   or "hold each ETF only while it is above its 200-day average, otherwise a liquid fund".
4. **Price check.** A price that is missing, stale or has jumped oddly stops the run for the day.
5. **Optional LLM check.** A reviewer reads the order list and the prices behind it and may **postpone
   by one day** if something looks broken (a 90% one-day fall is a unit split, not a crash). It cannot
   change an order, and after two postponements the rule runs anyway. It is told not to forecast.
6. **Orders.** Sell what is over target, then buy what is under, in whole shares. On paper these fill at
   the live price with slippage and Groww's charges taken off. The dashboard lists them so you can
   place the same orders by hand in the Groww app.
7. **Journal.** Orders, trades, the plan and the portfolio's value are written to the database.

(`worker/thunderbot/invest.py`, plans in `daily.py`, reviewer in `llm/rebalance.py`)

### The plans

| Plan | Rule | 15 years to Nov 2026, after costs and tax | Worst fall |
|---|---|---|---|
| **Steady mix** | Nifty 50, Next 50 and gold in fixed shares; rebalance each March | 13.4% a year | −23% |
| **Trend rotation** | Each ETF held only above its 200-day average, else liquid fund | 9.1% a year | −15% |
| **Nifty trend** | Nifty ETF above the 200-day average, else liquid fund | less than holding the ETF in all 13 five-year windows since 2009 | shallower in all 13 |
| **Strongest ETFs** | Hold the top-ranked ETFs by 3, 6 and 12-month return | no extra return for more tax | |
| **Momentum stocks** | Top Nifty 100 stocks by risk-adjusted momentum | looks like 22% but uses today's index members, so it is inflated | |
| *Holding NIFTYBEES* | *the yardstick* | *12.0% a year* | *−36%* |

Read that table the way the project's own research does: timing rules give a smaller fall and a smaller
return. Gold's run since 2019 flatters the mix. None of it is a promise.

## The AI desk, step by step

Every five minutes, for each stock:

1. **Four rule sets look for a setup.** Each one fixes the entry, stop and target, and fires at most
   once per stock per day.
   - *Opening-range breakout*: first close beyond the first 15 minutes' range, on the right side of
     VWAP, on a volume surge.
   - *VWAP reversion*: price stretched far from VWAP at an RSI extreme with a reversal bar; target VWAP.
   - *EMA pullback*: an established trend pulls back to the slow average and closes back through the fast one.
   - *Momentum burst*: first close at a new high or low for the day after 10:00, on at least 1.5 times
     the usual volume and on the right side of VWAP.
2. **The stop is widened to at least 0.8%.** Charges and slippage cost about 0.2% per round trip, so a
   0.3% stop loses most of its risk to costs before the trade starts.
3. **A small model scores the setup.** Sixty shallow decision trees look at 32 facts about that bar
   (recent returns, distance from VWAP, volume against the same time on earlier days, RSI, the Nifty's
   move, time of day) and estimate the chance the trade ends in profit after costs. Low scores are
   skipped but still followed.
4. **The LLM takes or skips.** It sees the setup, the score, how setups scored like this did before,
   the market so far today, the last hour of bars, the account's day, and a few "lessons" it wrote
   after earlier sessions. It answers take or skip and a size from 0 to 1. It cannot set a price, raise
   the size above normal, or create a trade. If the call fails, the trade is skipped.
5. **Risk limits have the last word.** Size comes from risking a fixed share of capital (0.5% by
   default) on the distance to the stop. Then the caps: positions open, trades per day, position size,
   the daily loss limit, the entry window.
6. **Paper fill and exit.** Entry at the last price plus slippage. On every later bar: stop first if a
   bar touched both stop and target; everything closed from 15:05.
7. **Every setup is followed to the end**, taken or not. That is how the desk can say what each skip
   was worth and whether the LLM's vetoes were right.
8. **After the close** the day is recorded, the LLM writes a short review and up to four lessons, and
   the model is retrained overnight on the latest 60 days.

(`worker/thunderbot/ai/runner.py`, `strategy/ai.py`, `ai/gbm.py`, `llm/trader.py`, `risk.py`)

### Where the limits sit

```
rule set ──► model score ──► LLM: take / skip / smaller ──► risk limits ──► paper order
 fixes the     can only          can only say                final say:       stop and target
 prices        drop a setup      no, or less                 size and caps    checked every bar
```

Each stage can only remove or shrink. Nothing downstream of the rule set can move a price, and nothing
downstream of the risk limits exists.

## What the words on the dashboard mean

| Word | Meaning |
|---|---|
| **R** | The amount risked on a trade: entry to stop, times shares. "+2R" made twice what it risked; "−1R" hit its stop. |
| **After costs** | After brokerage, STT, exchange and SEBI fees, stamp duty, GST and slippage. |
| **Win rate** | Share of trades that made money. Useless alone: 37% wins at 2R each can still lose after costs. |
| **Profit factor** | Rupees won divided by rupees lost. Below 1 loses money. |
| **Max drawdown / worst fall** | The largest drop from a peak to the next low. |
| **Sharpe** | Return per unit of bumpiness. Above 1 is good for a long-only portfolio. |
| **Out of sample** | Judged on days the rule or model was not fitted on. The only kind of result that counts. |
| **AUC** | How well the model ranks good setups above bad. 0.50 is a coin toss; the desk's first model scored 0.49. |
| **VWAP** | The day's average price weighted by volume. |
| **RVOL** | This bar's volume against the usual volume at this time of day. |
| **Shadow / followed setup** | A setup tracked on paper to its stop, target or the close even though it was not traded. |
| **Vetoed** | The LLM said no. Compare vetoed and approved setups by average R to see if it is helping. |
| **Learning / Strict** | Learning trades the best-scored 30% to build a record. Strict trades only what the model expects to profit, which so far is nothing. |
| **No-timing twin** | The same ETFs held in equal parts with no rule. If the rule cannot beat it, the rule is not adding anything. |

## What can and cannot go wrong

- **It cannot** place a real order from Vercel: brokers accept API orders only from a registered
  static IP, and the function has none.
- **It cannot** raise its own limits. Limits have ceilings in the code that settings cannot exceed
  (2% risk per trade, 10% daily loss, 5× leverage, 9 orders a second).
- **It can** show paper results that real trading would not match: paper fills assume you can always
  trade at the last price, and prices come from Yahoo, which can lag.
- **It can** lose money on real orders even when everything works. The research in `reports/` found
  no timing rule that beat holding the ETFs, and no evidence for a profitable retail intraday bot.

## Where to look when you want to change something

| To change | Go to |
|---|---|
| Which plan runs, its parameters | Dashboard → Plans |
| Risk per trade, daily loss limit, position caps | Dashboard → Setup → Desk limits |
| Which LLM is used | Dashboard → Setup → LLM (or `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL` where the worker runs) |
| The Groww key | Dashboard → Setup → Groww (real orders still need the switches on your own machine) |
| What the LLM is told | `TRADER_PROMPT` in `llm/trader.py`, `SYSTEM_PROMPT` in `llm/rebalance.py` |
| A new intraday rule set | A class in `worker/thunderbot/strategy/`, added to `make_generators` in `strategy/ai.py` |
| A new daily plan | A class in `daily.py` with a `target()` method, added to `DAILY_CATALOG` |
