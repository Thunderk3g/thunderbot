"use client";

import { useState } from "react";
import { Line, type Gate, type LineEnd } from "./Line";

type Go = (page: "today" | "desk" | "lab" | "results" | "log" | "settings") => void;

/** The same setup under four outcomes, to show what each gate can and cannot do. */
const CASES: { id: string; button: string; gates: Gate[]; end: LineEnd; says: string }[] = [
  {
    id: "whole", button: "Taken whole",
    gates: [
      { key: "model", label: "Model", state: "pass", value: "scored 46%" },
      { key: "llm", label: "LLM", state: "pass", value: "said take" },
      { key: "limits", label: "Limits", state: "pass", value: "38 shares" },
    ],
    end: { label: "Order", value: "38 shares, with a stop" },
    says: "Every gate stays closed. The rule set the entry, stop and target; the limits set the size from the money you allow it to risk. Nobody else touched a number.",
  },
  {
    id: "thin", button: "Shrunk by the LLM",
    gates: [
      { key: "model", label: "Model", state: "pass", value: "scored 44%" },
      { key: "llm", label: "LLM", state: "thin", size: 0.5, value: "cut to 50%" },
      { key: "limits", label: "Limits", state: "pass", value: "19 shares" },
    ],
    end: { label: "Order", value: "19 shares, with a stop" },
    says: "The LLM liked the setup but named a concern, so it asked for half size. The line carries on thinner. It could have asked for less; it cannot ask for more than normal size.",
  },
  {
    id: "model", button: "Stopped by the model",
    gates: [
      { key: "model", label: "Model", state: "cut", value: "28%, too low" },
      { key: "llm", label: "LLM", state: "pass", value: "not asked" },
      { key: "limits", label: "Limits", state: "pass" },
    ],
    end: { label: "Not traded", value: "followed anyway" },
    says: "The model scored the setup below its floor, so the line breaks there and the LLM is never asked. The setup is still followed on paper to its stop, target or the close, so you can see what skipping it was worth.",
  },
  {
    id: "limit", button: "Stopped by a limit",
    gates: [
      { key: "model", label: "Model", state: "pass", value: "scored 51%" },
      { key: "llm", label: "LLM", state: "pass", value: "said take" },
      { key: "limits", label: "Limits", state: "cut", value: "daily loss limit" },
    ],
    end: { label: "Not traded", value: "followed anyway" },
    says: "Everyone upstream said yes, and the desk had already lost its limit for the day. Limits run last and always win, which is why no model or prompt can talk the bot into a bigger loss than you set.",
  },
];

const WORDS: [string, string][] = [
  ["R", "The amount risked on a trade: the distance from entry to stop, times the shares. A trade that made +2R made twice what it risked; −1R hit its stop."],
  ["After costs", "After brokerage, STT, exchange and SEBI fees, stamp duty, GST and slippage. On the desk that is about 0.2% of a position per round trip."],
  ["Win rate", "The share of trades that made money. Useless alone: 37% wins at 2R each can still lose after costs."],
  ["Profit factor", "Rupees won divided by rupees lost. Below 1 loses money."],
  ["Worst fall", "The largest drop from a peak to the next low. Also called maximum drawdown."],
  ["Sharpe", "Return per unit of bumpiness. Above 1 is good for a portfolio that only buys."],
  ["Out of sample", "Judged on days the rule or model was not fitted on. The only kind of result that counts."],
  ["Ranking score (AUC)", "How well the model puts good setups above bad ones. 0.50 is a coin toss. The desk's first model scored 0.49."],
  ["VWAP", "The day's average price, weighted by volume."],
  ["Volume, 1.5×", "This bar's volume against the usual volume at this time of day."],
  ["Followed setup", "A setup tracked on paper to its stop, target or the close even though it was not traded."],
  ["Learning and Strict", "Learning trades the best-scored 30% of setups to build a record. Strict trades only what the model expects to profit, which so far is nothing."],
  ["No-timing twin", "The same ETFs held in equal parts with no rule. If a rule cannot beat it, the rule is adding nothing."],
  ["Paper", "Orders that are simulated at live prices with real charges taken off. No money moves."],
];

export default function GuideView({ go }: { go?: Go }) {
  const [which, setWhich] = useState("whole");
  const c = CASES.find((x) => x.id === which) ?? CASES[0];
  const link = (page: Parameters<Go>[0], text: string) => (
    <button type="button" onClick={() => go?.(page)} style={{ border: 0, background: "none", padding: 0, cursor: "pointer", textDecoration: "underline", color: "inherit", font: "inherit" }}>{text}</button>
  );
  return (
    <div className="guide">
      <div>
        <h1>How Thunderbot works</h1>
        <p className="lede">For someone who trades a little and wants to know what this thing does with a rupee, without reading the code.</p>
      </div>

      <section>
        <h2>One picture explains most of it</h2>
        <div className="prose">
          <p>Every decision is a line that runs from a rule to an order. On the way it passes through gates. A gate can leave the line whole, thin it, or open and break it. No gate can make it thicker, move a price or invent a trade.</p>
        </div>
        <div className="providers" role="group" aria-label="Show an outcome" style={{ marginTop: 18 }}>
          {CASES.map((x) => <button key={x.id} type="button" aria-pressed={x.id === which} onClick={() => setWhich(x.id)}>{x.button}</button>)}
        </div>
        <div className="stage">
          <Line size="lg" source={{ label: "Rule", value: "Opening-range breakout" }} gates={c.gates} end={c.end} label={`Example: ${c.button}`} />
        </div>
        <p className="lede" style={{ fontSize: 16.5, marginTop: 6 }} aria-live="polite">{c.says}</p>
      </section>

      <section>
        <h2>Two bots share this dashboard</h2>
        <div className="twobots">
          <div>
            <h3>The investing bot</h3>
            <p className="soft">This is the part meant to hold money. It lives on {link("today", "Home")} and {link("lab", "Plans")}.</p>
            <dl>
              <dt>Trades</dt><dd>A few ETFs: Nifty 50, Next 50, gold, a liquid fund</dd>
              <dt>Decides</dt><dd>Once a day at 15:10; trades a few times a year</dd>
              <dt>Who decides</dt><dd>A fixed rule you choose, called a plan</dd>
              <dt>Evidence</dt><dd>The plain fixed mix beat every timing rule after tax</dd>
            </dl>
          </div>
          <div>
            <h3>The desk</h3>
            <p className="soft">This exists to keep testing, on paper, whether an edge ever appears. It lives on {link("desk", "Desk")}.</p>
            <dl>
              <dt>Trades</dt><dd>24 liquid Nifty 50 stocks, intraday only</dd>
              <dt>Decides</dt><dd>Every five minutes, 09:30 to 14:30; flat by 15:05</dd>
              <dt>Who decides</dt><dd>Four rule sets propose, a small model scores, an LLM takes or skips</dd>
              <dt>Evidence</dt><dd>No edge found; it loses about a quarter of its risk a trade</dd>
            </dl>
          </div>
        </div>
      </section>

      <section>
        <h2>The daily check, step by step</h2>
        <ol className="walk">
          <li><div><b>15:10 on every trading day, it wakes.</b><p>Nothing runs all day. A timer calls a small function, which loads prices, adds today&apos;s live price, does one pass and exits.</p></div></li>
          <li><div><b>It asks whether today is a decision day.</b><p>Most plans decide only at month-end, or once a year. On other days it records what the portfolio is worth and stops.</p></div></li>
          <li><div><b>The plan gives target shares.</b><p>For example a third each in three ETFs, or &quot;hold each ETF only while it is above its 200-day average&quot;.</p></div></li>
          <li><div><b>The prices are checked.</b><p>A price that is missing, stale or has jumped oddly stops the run for the day.</p></div></li>
          <li><div><b>An LLM may look the orders over.</b><p>It can postpone by one day if something looks broken, such as a 90% one-day fall that is really a unit split. It cannot change an order, it is told not to forecast, and after two postponements the rule runs anyway.</p></div></li>
          <li><div><b>Orders go out.</b><p>Sells first, then buys, in whole shares. On paper they fill at the live price with charges taken off, and Home lists them so you can place the same ones by hand in Groww.</p></div></li>
          <li><div><b>Everything is written down.</b><p>Orders, the plan and the portfolio&apos;s value go to the {link("log", "Journal")}.</p></div></li>
        </ol>
      </section>

      <section>
        <h2>A desk trade, step by step</h2>
        <ol className="walk">
          <li><div><b>Four rule sets look for a setup.</b><p>Opening-range breakout, VWAP reversion, EMA pullback, momentum burst. Each fixes the entry, stop and target, and fires at most once per stock per day.</p></div></li>
          <li><div><b>The stop is widened to at least 0.8%.</b><p>Charges cost about 0.2% a round trip, so a 0.3% stop loses most of its risk to costs before the trade starts.</p></div></li>
          <li><div><b>A small model scores it.</b><p>Sixty shallow decision trees look at 32 facts about that bar and estimate the chance of a profit after costs. Low scores are skipped but still followed.</p></div></li>
          <li><div><b>The LLM takes or skips.</b><p>It sees the setup, the score, the market so far today and the account&apos;s day. It answers take or skip and a size from 0 to 1. If the call fails, the trade is skipped.</p></div></li>
          <li><div><b>The limits have the last word.</b><p>Size comes from risking a fixed share of capital on the distance to the stop. Then the caps: positions open, trades per day, the daily loss limit, the entry window.</p></div></li>
          <li><div><b>It is filled and managed on paper.</b><p>Stop first if a bar touched both stop and target. Everything is closed from 15:05.</p></div></li>
          <li><div><b>After the close it reviews the day.</b><p>The LLM writes a short review and a few lessons, and the model is retrained overnight on the latest 60 days.</p></div></li>
        </ol>
        <p className="small soft" style={{ marginTop: 12, maxWidth: "66ch" }}>Anything you see in italic serif on the Desk was written by the LLM. Everything else was written by rules.</p>
      </section>

      <section>
        <h2>What the words mean</h2>
        <dl className="glossary">
          {WORDS.map(([w, d]) => [<dt key={`${w}-t`}>{w}</dt>, <dd key={`${w}-d`}>{d}</dd>])}
        </dl>
      </section>

      <section>
        <h2>What it can and cannot do</h2>
        <div className="prose">
          <p><b>It cannot place a real order from this dashboard.</b> Brokers accept API orders only from a static IP registered to your account. Real orders are switched on by you, on your own machine. {link("settings", "Setup")} shows what that takes.</p>
          <p><b>It cannot raise its own limits.</b> Each limit has a ceiling in the code that no setting can exceed: 2% risk a trade, 10% daily loss, five times leverage, nine orders a second.</p>
          <p><b>It can show paper results that real trading would not match.</b> Paper fills assume you can always trade at the last price, and free prices can lag.</p>
          <p><b>It can lose money even when everything works.</b> The research behind it found no timing rule that beat holding the ETFs, and no evidence for a profitable retail intraday bot. It is built to show such results plainly before money is at risk.</p>
        </div>
      </section>
    </div>
  );
}
