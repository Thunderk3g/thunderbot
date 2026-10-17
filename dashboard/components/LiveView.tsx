"use client";

import { AnimatePresence, motion } from "motion/react";
import { useMemo, useState } from "react";
import { dayTime, hhmm, inr, num, signedInr } from "@/lib/format";
import type { EventRow, LiveState, Position, SignalCard } from "@/lib/types";
import DayStrip from "./DayStrip";
import { AnimatedNumber, Button, Empty, Section, Skeleton, spring } from "./ui";

const ALERT_KINDS = new Set(["error", "exit_failed", "stop_failed", "halt", "kill_switch", "order_rejected", "unmanaged_position"]);
const tone = (n: number) => (n > 0 ? "gain" : n < 0 ? "loss" : "");
const plural = (n: number, w: string) => `${n} ${w}${n === 1 ? "" : "s"}`;

export default function LiveView({ state, act }: { state: LiveState | null; act: (a: string) => Promise<void> }) {
  if (!state) return <Loading />;
  const { control, tradesToday, equityToday, signals, events, sessionDay } = state;
  const hb = control.heartbeat;
  const eff = control.effective_settings;
  const realized = hb?.realized_pnl ?? tradesToday.reduce((a, t) => a + Number(t.net_pnl), 0);
  const unrealized = hb?.unrealized_pnl ?? 0;
  const total = realized + unrealized;
  const positions = hb?.positions ?? [];
  const closed = tradesToday.length;
  const alive = !!hb?.wall_at && Date.now() - new Date(hb.wall_at).getTime() < 45_000;
  const todayIst = new Date().toLocaleDateString("en-CA", { timeZone: "Asia/Kolkata" });
  const needLogin = hb?.mode === "live" && eff?.env_only.require_login_confirmation && control.login_confirmed_for !== todayIst;
  const trading = !control.kill_switch && !!control.trading_enabled;
  const feedDown = hb?.feed && !hb.feed.ok ? hb.feed.message : null;
  const notStarted = hb && alive && hb.mode !== "replay" && !trading;

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
              Groww isn&apos;t connected, so there are no live prices and nothing can trade. {feedDown}
            </Notice>
          )}
          {notStarted && (
            <Notice key="start" kind="info" action={<Button size="sm" variant="primary" onClick={() => act("start")}>Start {hb.mode === "live" ? "live" : "paper"} trading</Button>}>
              {control.kill_switch ? "Trading was stopped and everything is flat." : "Not trading."}{" "}
              {hb.mode === "live" ? "Live mode places real orders on Groww." : "Paper trading uses live Groww prices; the orders are simulated."}
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
          {!hb && <Notice key="none" kind="info">No worker has connected yet. Run <code>thunderbot replay --speed 0.3</code> to watch a simulated session, or start paper trading on the server.</Notice>}
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
              <dt>Prices</dt><dd>{hb?.mode === "replay" ? "Replayed history" : !hb?.feed ? "–" : hb.feed.ok ? "Live from Groww" : "Groww, not connected"}</dd>
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
  if (!rows.length) return <Empty title="Quiet.">Engine events show up here.</Empty>;
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
