"use client";

import { AnimatePresence, motion } from "motion/react";
import { useEffect, useMemo, useState } from "react";
import { dayTime, hhmm, inr, num, signedInr } from "@/lib/format";
import { workerAlive, type EventRow, type LiveState, type Plan, type Position, type SignalCard } from "@/lib/types";
import { asset, slices } from "@/lib/assets";
import { wakeWorker } from "@/lib/usePoll";
import DayStrip from "./DayStrip";
import { AnimatedNumber, Button, Empty, MixBar, Section, Skeleton, spring } from "./ui";

const ALERT_KINDS = new Set(["error", "exit_failed", "stop_failed", "halt", "kill_switch", "order_rejected", "unmanaged_position"]);
const tone = (n: number) => (n > 0 ? "gain" : n < 0 ? "loss" : "");
const plural = (n: number, w: string) => `${n} ${w}${n === 1 ? "" : "s"}`;

type Go = (page: "today" | "lab" | "results" | "log" | "settings") => void;

export default function LiveView({ state, act, refresh, go }: { state: LiveState | null; act: (a: string) => Promise<void>; refresh?: () => void; go?: Go }) {
  if (!state) return <Loading />;
  const { control, tradesToday, equityToday, signals, events, sessionDay } = state;
  const hb = control.heartbeat;
  const eff = control.effective_settings;
  const realized = hb?.realized_pnl ?? tradesToday.reduce((a, t) => a + Number(t.net_pnl), 0);
  const unrealized = hb?.unrealized_pnl ?? 0;
  const total = realized + unrealized;
  const positions = hb?.positions ?? [];
  const closed = tradesToday.length;
  const alive = workerAlive(hb);
  const todayIst = new Date().toLocaleDateString("en-CA", { timeZone: "Asia/Kolkata" });
  const needLogin = hb?.mode === "live" && eff?.env_only.require_login_confirmation && control.login_confirmed_for !== todayIst;
  const trading = !control.kill_switch && !!control.trading_enabled;
  const feedDown = hb?.feed && !hb.feed.ok ? hb.feed.message : null;
  const notStarted = hb && alive && hb.mode !== "replay" && !trading;

  if (!hb) return <GetStarted control={control} refresh={refresh} go={go} act={act} />;
  if (hb.style === "invest" && hb.portfolio) {
    return <InvestToday state={state} act={act} alive={alive} feedDown={feedDown} notStarted={!!notStarted} trading={trading} refresh={refresh} go={go} />;
  }

  const summary = !closed && !positions.length
    ? "Nothing traded yet today."
    : <>after costs, from {plural(closed, "closed trade")}.{" "}
      {positions.length
        ? <><strong>{plural(positions.length, "position")} open</strong>, {signedInr(unrealized)} of it not yet banked.</>
        : "Nothing open."}</>;

  return (
    <div className="page">
      <div className="notices">
        <AnimatePresence initial={false}>
          {feedDown && (
            <Notice key="feed" kind="stop">
              {hb?.feed?.source === "yahoo" ? "Yahoo prices aren't coming through" : "Groww isn't connected"}, so nothing can trade. {feedDown}
            </Notice>
          )}
          {notStarted && (
            <Notice key="start" kind="info" action={<Button size="sm" variant="primary" onClick={() => act("start")}>Start {hb.mode === "live" ? "live" : "paper"} trading</Button>}>
              {control.kill_switch ? "Trading was stopped and everything is flat." : "Not trading."}{" "}
              {hb.mode === "live" ? "Live mode places real orders on Groww." : `Paper trading uses live ${hb.feed?.source === "yahoo" ? "Yahoo Finance" : "Groww"} prices; the orders are simulated.`}
            </Notice>
          )}
          {trading && hb?.market_open === false && !feedDown && (
            <Notice key="closed" kind="info">Started. The market is closed now, so the first trades can happen from 09:30 IST on the next trading day.</Notice>
          )}
          {hb?.halted && <Notice key="halt" kind="stop">Halted for the day: {hb.halt_reason ?? "daily loss limit reached"}. It resumes tomorrow.</Notice>}
          {control.paused && !control.kill_switch && (
            <Notice key="pause" kind="caution" action={<Button size="sm" onClick={() => act("resume")}>Resume new trades</Button>}>
              New trades are paused. Open positions are still managed.
            </Notice>
          )}
          {needLogin && (
            <Notice key="login" kind="caution" action={<Button size="sm" variant="primary" onClick={() => act("confirm_login")}>Confirm login</Button>}>
              Confirm today&apos;s Groww login to allow new trades. Exchange rules require a daily sign-in.
            </Notice>
          )}
          {hb && !alive && <Notice key="off" kind="caution">The worker hasn&apos;t reported since {dayTime(hb.wall_at ?? hb.at)}. Stop orders at Groww still protect open positions.</Notice>}
        </AnimatePresence>
      </div>

      <section aria-label="Today">
        <div className={`hero-figure ${tone(total)}`}>
          <AnimatedNumber value={total} format={(n) => signedInr(n)} />
        </div>
        <p className="hero-line">{summary}</p>
        <DayStrip
          points={equityToday.map((e) => ({ at: e.at, value: Number(e.realized_pnl) + Number(e.unrealized_pnl) }))}
          trades={tradesToday.map((t) => ({ at: t.closed_at, net: Number(t.net_pnl), symbol: t.symbol }))}
          now={hb?.at} marketOpen={hb?.market_open}
          entryStart={eff?.editable.entry_start ?? "09:30"} entryEnd={eff?.editable.entry_end ?? "14:30"} flattenAt={eff?.editable.flatten_at ?? "15:05"}
        />
        <p className="small soft" style={{ marginTop: 6 }}>
          {new Date(`${sessionDay}T12:00:00+05:30`).toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long", timeZone: "Asia/Kolkata" })}.
          Dots are closed trades; hover the line for the P&amp;L at any time.
        </p>
      </section>

      <div className="split">
        <div className="page" style={{ gap: 40 }}>
          <Section title="Open positions" aside={<p>{positions.length} of {eff?.editable.max_open_positions ?? "–"} allowed</p>}>
            <Positions positions={positions} />
          </Section>
          <Section title="How it's set up" aside={control.paused
            ? <Button size="sm" variant="quiet" onClick={() => act("resume")}>Resume new trades</Button>
            : <Button size="sm" variant="quiet" onClick={() => act("pause")}>Pause new trades</Button>}>
            <dl className="facts">
              <dt>Strategy</dt><dd>{control.strategy_catalog?.find((s) => s.name === eff?.editable.strategy)?.label ?? hb?.strategy ?? "–"}</dd>
              <dt>Prices</dt><dd>{hb?.mode === "replay" ? "Replayed history" : !hb?.feed ? "–" : `${hb.feed.source === "yahoo" ? "Yahoo Finance (free)" : "Groww"}${hb.feed.ok ? "" : ", not connected"}`}</dd>
              <dt>Orders</dt><dd className={hb?.mode === "live" ? "loss" : ""}>{hb?.mode === "live" ? "Real, on Groww" : hb ? "Simulated (paper)" : "–"}</dd>
              <dt>Reviewer</dt><dd>{!hb?.reviewer || hb.reviewer === "none" ? "Off" : hb.reviewer === "heuristic" ? "Rule-based baseline" : `${hb.reviewer}, ${eff?.editable.llm_effort} effort`}</dd>
              <dt>Risk per trade</dt><dd>{eff ? `${inr((eff.editable.capital * eff.editable.risk_per_trade_pct) / 100)} (${eff.editable.risk_per_trade_pct}% of ${inr(eff.editable.capital)})` : "–"}</dd>
              <dt>Daily loss limit</dt><dd>{eff ? <LossUsed used={Math.max(0, -total)} limit={(eff.editable.capital * eff.editable.max_daily_loss_pct) / 100} /> : "–"}</dd>
              <dt>Trades today</dt><dd>{hb?.trades_today ?? closed} of {eff?.editable.max_trades_per_day ?? "–"}</dd>
              <dt>Schedule</dt><dd>New trades {eff?.editable.entry_start}–{eff?.editable.entry_end}, flat by {eff?.editable.flatten_at}</dd>
            </dl>
          </Section>
        </div>
        <div className="page" style={{ gap: 40 }}>
          <Section title="Signals" aside={<p>Every idea the strategy had, and what happened to it</p>}>
            <SignalFeed signals={signals} sessionDay={sessionDay} />
          </Section>
          <Section title="Engine log">
            <EngineLog events={events} />
          </Section>
        </div>
      </div>
    </div>
  );
}

const STRATEGY_NAME: Record<string, string> = {
  core_mix: "Steady mix", etf_trend: "Trend rotation", etf_rank: "Strongest ETFs", index_trend: "Nifty trend", momentum: "Momentum stocks",
};
const ORDER = ["nifty", "next50", "gold", "mid", "parked"];
const TRADES_WHEN: Record<string, string> = {
  core_mix: "It trades once a year, at the end of March, to bring the three ETFs back to their shares.",
  etf_trend: "It trades at month-end, and only when an ETF crosses its 200-day average or a share drifts 10 points.",
  etf_rank: "It trades at month-end, and only when the strongest ETFs change or a share drifts 10 points.",
  index_trend: "It trades at month-end, and only when the Nifty crosses its 200-day average.",
  momentum: "It re-ranks the stocks each quarter and checks the market filter at month-end.",
};

/** One pass of the serverless worker on demand: first-time setup, or catching up after a missed run. */
function WakeButton({ refresh, label, variant = "quiet", size = "sm" }: { refresh?: () => void; label: string; variant?: "" | "primary" | "quiet"; size?: "" | "sm" | "lg" }) {
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState<string | null>(null);
  const go = async () => {
    setBusy(true);
    setNote(null);
    try {
      const r = await wakeWorker();
      setNote(r.did ? `Done: ${r.did}.` : "Done.");
      refresh?.();
    } catch (e) {
      setNote(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
      <Button size={size} variant={variant} onClick={go} disabled={busy}>{busy ? "Checking…" : label}</Button>
      {note && <span className="small soft" role="status">{note}</span>}
    </span>
  );
}

/** First visit: nothing has reported in yet. Three steps to a running bot, in order. */
function GetStarted({ control, refresh, go, act }: { control: LiveState["control"]; refresh?: () => void; go?: Go; act: (a: string) => Promise<void> }) {
  const picked = !!control.invest_settings?.strategy;
  return (
    <div className="page">
      <section className="slab" aria-label="Get started">
        <div>
          <h1 style={{ maxWidth: "18ch" }}>Three steps and your bot is running.</h1>
          <p className="hero-line">
            Thunderbot holds a few index and gold ETFs for you and checks them once a day at 15:10 IST. It starts in paper mode:
            live prices, pretend money.
          </p>
        </div>
        <div className="steps">
          <div className="step now">
            <h3>Wake the worker</h3>
            <p>Nothing has reported in yet. Wake it once; after that the scheduler calls it by itself.</p>
            <WakeButton refresh={refresh} label="Wake the worker" variant="primary" size="" />
          </div>
          <div className={`step ${picked ? "done" : ""}`}>
            <h3>Choose a plan</h3>
            <p>Test each plan on 15 years of real prices, after costs and tax, and pick the one you can live with.</p>
            <Button onClick={() => go?.("lab")}>See the plans</Button>
          </div>
          <div className="step">
            <h3>Start paper investing</h3>
            <p>The first check runs at the next 15:10 IST on a trading day. You can stop it at any time.</p>
            <Button onClick={() => act("start")} disabled>Start</Button>
          </div>
        </div>
      </section>
      <p className="small soft" style={{ maxWidth: "70ch" }}>
        If waking fails on your own computer, the worker isn&apos;t running there: start <code>thunderbot serve</code> and then <code>thunderbot tick</code>.
        On Vercel, check that the deployment built the worker function. The setup guide is in <code>docs/no-server.md</code>.
      </p>
    </div>
  );
}

/** "Today, 15:10 IST" and how long until then, from the visitor's clock but in exchange time. */
function useNextCheck(runAt: string, lastRun: string | null) {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 30_000);
    return () => clearInterval(id);
  }, []);
  const ist = new Date(now + 19_800_000); // read with getUTC*: exchange wall-clock time
  const [h, m] = runAt.split(":").map(Number);
  const target = new Date(Date.UTC(ist.getUTCFullYear(), ist.getUTCMonth(), ist.getUTCDate(), h, m));
  const today = ist.toISOString().slice(0, 10);
  const weekday = (d: Date) => d.getUTCDay() >= 1 && d.getUTCDay() <= 5;
  if (!weekday(target) || ist.getTime() >= target.getTime() || lastRun === today) {
    do target.setUTCDate(target.getUTCDate() + 1); while (!weekday(target));
  }
  const mins = Math.max(0, Math.round((target.getTime() - ist.getTime()) / 60_000));
  const isToday = target.toISOString().slice(0, 10) === today;
  const tomorrow = new Date(ist); tomorrow.setUTCDate(ist.getUTCDate() + 1);
  const day = isToday ? "Today" : target.toISOString().slice(0, 10) === tomorrow.toISOString().slice(0, 10) ? "Tomorrow"
    : target.toLocaleDateString("en-IN", { weekday: "long", timeZone: "UTC" });
  const wait = mins < 60 ? `in ${mins} min` : mins < 48 * 60 ? `in ${Math.floor(mins / 60)} h ${mins % 60} min` : `in ${Math.round(mins / 1440)} days`;
  return { day, wait };
}

function Tickets({ plan, mode }: { plan: Plan; mode: string }) {
  const when = dayTime(plan.at);
  if (!plan.orders.length) return <p className="soft">The last check on {when} needed no trades.</p>;
  const sorted = [...plan.orders].sort((a, b) => (a.side === b.side ? 0 : a.side === "SELL" ? -1 : 1));
  return (
    <>
      <div className="tickets">
        {sorted.map((o) => (
          <div className="ticket" key={`${o.side}-${o.symbol}`}>
            <span className={`side ${o.side === "BUY" ? "gain" : "loss"}`}>{o.side === "BUY" ? "Buy" : "Sell"}</span>
            <span className="what"><b>{o.qty} × {o.symbol}</b> <span className="soft">{asset(o.symbol).known ? `${asset(o.symbol).name}, ` : ""}near ₹{num(o.price)}</span></span>
            <span className="amount">{inr(o.value)}</span>
          </div>
        ))}
      </div>
      <p className="small soft" style={{ marginTop: 12, maxWidth: "68ch" }}>
        {mode === "live" ? `Placed on Groww on ${when}.` : `Simulated on ${when}${plan.late ? ", after the close, on closing prices" : ""}.`}{" "}
        {mode !== "live" && "To follow this with real money, place the same orders in the Groww app as limit orders near these prices, sells first."}
      </p>
    </>
  );
}

function InvestToday({ state, act, alive, feedDown, notStarted, trading, refresh, go }: {
  state: LiveState; act: (a: string) => Promise<void>; alive: boolean; feedDown: string | null; notStarted: boolean; trading: boolean;
  refresh?: () => void; go?: Go;
}) {
  const { control, events } = state;
  const hb = control.heartbeat!;
  const p = hb.portfolio!;
  const gain = p.value - p.capital;
  const serverless = hb.scheduler === "serverless";
  const empty = !p.holdings.length;
  const next = useNextCheck(p.run_at, p.last_run);
  const strategyName = STRATEGY_NAME[hb.strategy ?? ""] ?? hb.strategy ?? "your plan";
  const held = Object.fromEntries(p.holdings.map((h) => [h.symbol, h.weight]));
  const target = p.target ? Object.fromEntries(Object.entries(p.target).map(([k, v]) => [k, v * 100])) : null;
  const nextRebalance = new Date(`${p.next_rebalance}T12:00:00+05:30`).toLocaleDateString("en-IN", { weekday: "short", day: "numeric", month: "short", timeZone: "Asia/Kolkata" });
  const signals = Object.entries(p.signals ?? {});
  const timed = hb.strategy === "etf_trend" || hb.strategy === "index_trend";
  return (
    <div className="page">
      <div className="notices">
        <AnimatePresence initial={false}>
          {feedDown && <Notice key="feed" kind="stop">No prices from {hb.feed?.source === "yahoo" ? "Yahoo" : "Groww"}, so nothing can trade. {feedDown}</Notice>}
          {control.paused && trading && (
            <Notice key="pause" kind="caution" action={<Button size="sm" onClick={() => act("resume")}>Resume</Button>}>Paused: the holdings stay, and no trades happen.</Notice>
          )}
          {p.pending && trading && (
            <Notice key="pending" kind="caution">A rebalance is waiting{p.missed ? ` (the ${p.missed} run started too late to trade)` : ""}. It will be decided again on fresh prices at {p.run_at} IST on the next trading day. Activity says why.</Notice>
          )}
          {!alive && (
            <Notice key="off" kind="caution" action={serverless ? <WakeButton refresh={refresh} label="Check now" variant="" /> : undefined}>
              {serverless ? `The scheduler hasn't called the worker since ${dayTime(hb.wall_at ?? hb.at)}.` : `The worker hasn't reported since ${dayTime(hb.wall_at ?? hb.at)}.`}
            </Notice>
          )}
        </AnimatePresence>
      </div>

      <section className="slab" aria-label="Your portfolio">
        <div className="slab-top">
          <div>
            <div className="hero-figure"><AnimatedNumber value={p.value} format={(n) => inr(n)} /></div>
            <p className="hero-line">
              {empty && notStarted
                ? <>Paper money, waiting. Press Start and <strong>{strategyName}</strong> makes its first check at {p.run_at} IST.</>
                : <><strong className={tone(gain)}>{signedInr(gain)}</strong> ({gain >= 0 ? "+" : ""}{((gain / p.capital) * 100).toFixed(1)}%) since you started with {inr(p.capital)}{hb.mode === "live" ? "" : " of paper money"}.</>}
            </p>
          </div>
          <dl className="next" style={{ margin: 0 }}>
            <dt>{notStarted ? "Not running" : "Next check"}</dt>
            <dd>{notStarted ? "Press Start" : `${next.day}, ${p.run_at}`}</dd>
            <p>{notStarted ? `It then checks every trading day at ${p.run_at} IST.` : `${next.wait}, exchange time.`}</p>
            {notStarted && <div style={{ marginTop: 14 }}><Button variant="primary" size="lg" onClick={() => act("start")}>Start {hb.mode === "live" ? "live" : "paper"} investing</Button></div>}
          </dl>
        </div>
        {empty
          ? target && <MixBar slices={slices(target)} caption={`${strategyName} will hold`} />
          : <MixBar slices={slices(held)} caption="How it is split" />}
      </section>

      <div className="split">
        <div className="page" style={{ gap: 44 }}>
          <Section title="What you hold" aside={<p>{empty ? "nothing yet" : `${p.holdings.length} ${p.holdings.length === 1 ? "holding" : "holdings"}, ${inr(p.cash)} in cash`}</p>}>
            {empty ? <Empty title="All cash for now.">Holdings appear after the first check at {p.run_at} IST on a trading day.</Empty> : (
              <div className="table-wrap"><table>
                <thead><tr><th>Holding</th><th className="num hide-sm">Units</th><th className="num hide-sm">Price</th><th className="num">Value</th><th className="num hide-sm">Share</th><th className="num">Gain</th></tr></thead>
                <tbody>{[...p.holdings].sort((x, y) => ORDER.indexOf(asset(x.symbol).kind) - ORDER.indexOf(asset(y.symbol).kind)).map((h) => {
                  const a = asset(h.symbol);
                  const want = target?.[h.symbol];
                  return (
                    <tr key={h.symbol}>
                      <td><span className={`swatch ${a.kind}`} />{a.known ? <>{a.name} <span className="soft small hide-sm">{h.symbol}</span></> : <span className="ticker">{h.symbol}</span>}</td>
                      <td className="num hide-sm">{num(h.qty, 0)}</td><td className="num hide-sm">{num(h.ltp)}</td><td className="num">{inr(h.value)}</td>
                      <td className="num hide-sm">{h.weight.toFixed(1)}%{want !== undefined && <span className="soft small"> of {want.toFixed(0)}</span>}</td>
                      <td className={`num ${tone(h.pnl)}`}>{signedInr(h.pnl)}</td>
                    </tr>
                  );
                })}</tbody>
              </table></div>
            )}
          </Section>
          {p.last_plan && (
            <Section title={hb.mode === "live" ? "Latest orders" : "Orders to copy into Groww"}>
              <Tickets plan={p.last_plan} mode={hb.mode} />
            </Section>
          )}
        </div>

        <div className="page" style={{ gap: 44 }}>
          <Section title="What happens next" aside={control.paused
            ? <Button size="sm" variant="quiet" onClick={() => act("resume")}>Resume</Button>
            : trading ? <Button size="sm" variant="quiet" onClick={() => act("pause")}>Pause</Button> : undefined}>
            <dl className="upnext">
              <div>
                <span className={`pip ${trading && alive ? "now" : ""}`} />
                <div><dt>{strategyName}: month-end review on {nextRebalance}</dt><dd>{TRADES_WHEN[hb.strategy ?? ""] ?? "It trades only on rebalance days."}{" "}
                  <button type="button" onClick={() => go?.("lab")} style={{ border: 0, background: "none", padding: 0, cursor: "pointer", textDecoration: "underline", color: "inherit" }}>Change plan</button></dd></div>
              </div>
              {timed && signals.map(([sym, sig]) => (
                <div key={sym}>
                  <span className="pip" style={{ background: `var(--a-${asset(sym).kind === "next50" ? "next" : asset(sym).kind})` }} />
                  <div><dt>{asset(sym).name} is {sig.above ? "above" : "below"} its 200-day average</dt>
                    <dd>{num(sig.price)} against {num(sig.avg)}, so it is {sig.above ? "held" : `parked in ${p.liquid_symbol ?? "the liquid ETF"}`} at the next month-end check.</dd></div>
                </div>
              ))}
              <div>
                <span className={`pip ${alive ? "ok" : "bad"}`} />
                <div><dt>{serverless ? "The scheduler" : "The worker"} {alive ? "is calling in" : "has gone quiet"}</dt>
                  <dd>Last heard {dayTime(hb.wall_at ?? hb.at)}. {serverless ? "It wakes every few minutes in market hours; nothing stays running." : "It runs all the time on your machine or server."}{" "}
                    {serverless && <WakeButton refresh={refresh} label="Check now" />}</dd></div>
              </div>
              <div>
                <span className="pip" />
                <div><dt>{hb.mode === "live" ? "Real orders on Groww" : "Paper orders"}</dt>
                  <dd>{hb.mode === "live" ? "Delivery limit orders, placed from the registered static IP." : "Fills are simulated at live Yahoo prices with Groww's charges. Real orders need the Trade API and a static IP of your own."}</dd></div>
              </div>
            </dl>
          </Section>
          <Section title="Activity" aside={<Button size="sm" variant="quiet" onClick={() => go?.("log")}>See all</Button>}>
            <EngineLog events={events} />
          </Section>
        </div>
      </div>
    </div>
  );
}

function Notice({ kind, children, action }: { kind: "stop" | "caution" | "info"; children: React.ReactNode; action?: React.ReactNode }) {
  return (
    <motion.div className={`notice ${kind}`} initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} transition={{ duration: 0.2 }}>
      <span className="grow">{children}</span>{action}
    </motion.div>
  );
}

function LossUsed({ used, limit }: { used: number; limit: number }) {
  const frac = limit > 0 ? Math.min(used / limit, 1) : 0;
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 10 }}>
      <span style={{ width: 80, height: 4, borderRadius: 4, background: "var(--rule)", overflow: "hidden", display: "inline-block" }}>
        <motion.span style={{ display: "block", height: "100%", background: frac > 0.6 ? "var(--loss)" : "var(--ink-soft)" }} animate={{ width: `${frac * 100}%` }} transition={spring} />
      </span>
      <span className="tnum">{inr(used)} used of {inr(limit)}</span>
    </span>
  );
}

function Positions({ positions }: { positions: Position[] }) {
  if (!positions.length) return <Empty title="Flat.">New positions appear here with a gauge showing where the price sits between stop and target.</Empty>;
  return (
    <div className="rows">
      {positions.map((p) => {
        const long = p.side === "BUY";
        const span = long ? p.target - p.stop : p.stop - p.target;
        const at = (v: number) => Math.min(100, Math.max(0, ((long ? v - p.stop : p.stop - v) / span) * 100));
        return (
          <div key={p.symbol} style={{ padding: "12px 2px" }}>
            <div style={{ display: "flex", alignItems: "baseline", gap: 12 }}>
              <span className="ticker" style={{ fontSize: 18 }}>{p.symbol}</span>
              <span className="soft small">{long ? "Long" : "Short"} {p.qty} at {num(p.entry)}, now {num(p.ltp)}</span>
              <span style={{ marginLeft: "auto", fontWeight: 650 }} className={`tnum ${tone(p.unrealized)}`}>
                <AnimatedNumber value={p.unrealized} format={(n) => signedInr(n)} />
              </span>
            </div>
            <div className="gauge" aria-label={`Price between stop ${p.stop} and target ${p.target}`}>
              <span className="track" />
              <span className="entry" style={{ left: `${at(p.entry)}%` }} />
              <motion.span className="now" initial={false} animate={{ left: `${at(p.ltp)}%` }} transition={{ type: "spring", stiffness: 150, damping: 22 }} />
            </div>
            <div className="gauge-labels"><span>Stop {num(p.stop)}</span><span>Opened {hhmm(p.opened_at)}</span><span>Target {num(p.target)}</span></div>
          </div>
        );
      })}
    </div>
  );
}

function verdict(s: SignalCard): { text: string; cls: string } {
  const d = s.decision;
  if (!d) return { text: "not reviewed", cls: "none" };
  if (d.error) return { text: "review failed", cls: "none" };
  if (!d.approve) return { text: "vetoed", cls: "reject" };
  return { text: d.size_multiplier < 1 ? `approved at ${Math.round(d.size_multiplier * 100)}%` : "approved", cls: "approve" };
}

function SignalFeed({ signals, sessionDay }: { signals: SignalCard[]; sessionDay: string }) {
  const [open, setOpen] = useState<string | null>(null);
  if (!signals.length) return <Empty title="No signals yet.">Each strategy idea shows up here with the reviewer&apos;s decision, and later, how it would have played out.</Empty>;
  return (
    <div className="rows" style={{ maxHeight: 560, overflowY: "auto" }}>
      <AnimatePresence initial={false}>
        {signals.map((s) => {
          const v = verdict(s);
          const o = s.outcome;
          const isOpen = open === s.id;
          return (
            <motion.div key={s.id} layout="position" initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={spring}>
              <button type="button" className="row-button" aria-expanded={isOpen} onClick={() => setOpen(isOpen ? null : s.id)}>
                <div className="row">
                  <span className="time">{s.signal_ts.slice(0, 10) === sessionDay ? hhmm(s.signal_ts) : dayTime(s.signal_ts)}</span>
                  <span className="ticker">{s.symbol}</span>
                  <span className="soft small">{s.side === "BUY" ? "buy" : "sell"}</span>
                  <span className="grow" />
                  {o && <span className={`small tnum ${tone(Number(o.r_multiple))}`} title="How the idea played out, in multiples of the risk taken">
                    {Number(o.r_multiple) > 0 ? "+" : ""}{Number(o.r_multiple).toFixed(1)}R
                  </span>}
                  <span className={`verdict ${v.cls}`}>{v.text}</span>
                </div>
              </button>
              <AnimatePresence initial={false}>
                {isOpen && (
                  <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} style={{ overflow: "hidden" }}>
                    <div className="detail">
                      <p>Entry {num(s.entry)}, stop {num(s.stop)}, target {num(s.target)}. {s.reason}.</p>
                      {s.decision && <p><strong style={{ color: "var(--ink)" }}>Reviewer ({s.decision.model}):</strong> {s.decision.rationale}</p>}
                      {s.decision?.risk_flags?.length ? <p>Concerns: {s.decision.risk_flags.map((f) => f.replaceAll("_", " ")).join(", ")}.</p> : null}
                      {o && <p>It hit its {o.outcome === "eod" ? "end-of-day exit" : o.outcome} at {hhmm(o.closed_at)}{o.risk_approved ? "" : ", though it wasn't traded"}.</p>}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}

function EngineLog({ events }: { events: EventRow[] }) {
  const rows = useMemo(() => events.filter((e) => e.kind !== "risk_verdict").slice(0, 12), [events]);
  if (!rows.length) return <Empty title="Nothing yet.">Checks, orders and warnings show up here.</Empty>;
  return (
    <div className="rows">
      {rows.map((e) => (
        <div key={e.id} className="row small">
          <span className="time">{hhmm(e.created_at)}</span>
          <span className={`grow trunc ${ALERT_KINDS.has(e.kind) ? "loss" : ""}`} title={e.message}>{e.message}</span>
        </div>
      ))}
    </div>
  );
}

function Loading() {
  return (
    <div className="page">
      <Skeleton height={80} width={260} />
      <Skeleton height={168} />
      <div className="split"><Skeleton height={200} /><Skeleton height={200} /></div>
    </div>
  );
}
