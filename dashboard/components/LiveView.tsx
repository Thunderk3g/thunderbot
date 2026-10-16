"use client";

import { AnimatePresence, motion } from "motion/react";
import { Bot, ChevronDown, CircleAlert, Clock, Lock, OctagonX, Pause, Play, ShieldCheck, Sparkles, Wallet } from "lucide-react";
import { useMemo, useState } from "react";
import { ago, dayTime, hhmm, inr, num, pnlClass, signedInr } from "@/lib/format";
import type { EventRow, LiveState, Position, SignalCard } from "@/lib/types";
import { PnlCurve } from "./charts";
import { AnimatedNumber, Badge, Button, Card, Empty, Skeleton, fadeUp, spring } from "./ui";

const ALERT_KINDS = new Set(["error", "exit_failed", "stop_failed", "halt", "kill_switch", "order_rejected", "unmanaged_position"]);

export default function LiveView({ state, act }: { state: LiveState | null; act: (a: string) => Promise<void> }) {
  if (!state) return <LoadingLive />;
  const { control, tradesToday, equityToday, signals, events, sessionDay } = state;
  const hb = control.heartbeat;
  const realized = hb?.realized_pnl ?? tradesToday.reduce((a, t) => a + Number(t.net_pnl), 0);
  const unrealized = hb?.unrealized_pnl ?? 0;
  const wins = tradesToday.filter((t) => Number(t.net_pnl) > 0).length;
  const eff = control.effective_settings;
  const alive = !!hb?.wall_at && Date.now() - new Date(hb.wall_at).getTime() < 45_000;
  const needLogin = hb?.mode === "live" && eff?.env_only.require_login_confirmation && control.login_confirmed_for !== new Date().toLocaleDateString("en-CA", { timeZone: "Asia/Kolkata" });

  const curve = equityToday.map((e) => ({ time: e.at, value: Number(e.realized_pnl) + Number(e.unrealized_pnl) }));

  return (
    <div className="grid">
      <AnimatePresence initial={false}>
        {control.kill_switch && <Banner key="kill" tone="bad" icon={<OctagonX size={16} />} text="Kill switch engaged: all positions flattened, no new entries." />}
        {hb?.halted && <Banner key="halt" tone="bad" icon={<CircleAlert size={16} />} text={`Trading halted for the day: ${hb.halt_reason ?? "daily loss limit"}`} />}
        {control.paused && !control.kill_switch && (
          <Banner key="pause" tone="warn" icon={<Pause size={16} />} text="New entries paused. Open positions are still managed."
            action={<Button size="sm" onClick={() => act("resume")}><Play size={14} />Resume</Button>} />
        )}
        {needLogin && (
          <Banner key="login" tone="warn" icon={<Lock size={16} />} text="Confirm today's broker login to allow new entries (daily 2FA policy)."
            action={<Button size="sm" variant="primary" onClick={() => act("confirm_login")}><ShieldCheck size={14} />Confirm login</Button>} />
        )}
        {hb && !alive && <Banner key="offline" tone="warn" icon={<CircleAlert size={16} />} text={`Worker hasn't reported since ${ago(hb.wall_at ?? hb.at)}. Broker-side stops still protect open positions.`} />}
        {!hb && <Banner key="nohb" tone="info" icon={<Sparkles size={16} />} text="No worker yet. Start one: `thunderbot replay --speed 0.3` to watch a simulated session, or `thunderbot paper`." />}
      </AnimatePresence>

      <Card>
        <div className="hero">
          <div>
            <div className="subtle" style={{ display: "flex", gap: 8, alignItems: "center" }}>
              <Clock size={13} /> Session {sessionDay}{hb?.market_open === false ? " · market closed" : ""}
            </div>
            <div className={`hero-value ${pnlClass(realized + unrealized)}`}>
              <AnimatedNumber value={realized + unrealized} format={(n) => signedInr(n)} />
            </div>
            <div className="hero-sub">
              <KV k="Realized" v={<AnimatedNumber value={realized} format={(n) => signedInr(n)} className={pnlClass(realized)} />} />
              <KV k="Open P&L" v={<AnimatedNumber value={unrealized} format={(n) => signedInr(n)} className={pnlClass(unrealized)} />} />
              <KV k="Trades" v={`${hb?.trades_today ?? tradesToday.length}${eff ? ` / ${eff.editable.max_trades_per_day}` : ""}`} />
              <KV k="Win rate" v={tradesToday.length ? `${Math.round((wins / tradesToday.length) * 100)}%` : "–"} />
            </div>
          </div>
          <div>
            {curve.length > 1 ? <PnlCurve points={curve} intraday height={170} label="session P&L" />
              : <Empty title="No intraday curve yet" hint="It fills in as the session runs." />}
          </div>
        </div>
      </Card>

      <div className="grid cols-2">
        <Card title="Open positions" icon={<Wallet size={15} />} delay={0.05}
          action={<span className="subtle">{hb?.open_positions ?? 0}{eff ? ` / ${eff.editable.max_open_positions}` : ""}</span>}>
          <Positions positions={hb?.positions ?? []} />
        </Card>
        <Card title="Session" icon={<Bot size={15} />} delay={0.1}
          action={control.paused
            ? <Button size="sm" onClick={() => act("resume")}><Play size={14} />Resume entries</Button>
            : <Button size="sm" onClick={() => act("pause")}><Pause size={14} />Pause entries</Button>}>
          <div className="list">
            <Line k="Strategy" v={eff ? labelFor(control, eff.editable.strategy) : hb?.strategy ?? "–"} />
            <Line k="Signal reviewer" v={!hb?.reviewer || hb.reviewer === "none" ? <Badge>off</Badge>
              : hb.reviewer === "heuristic" ? <Badge>rule-based baseline</Badge>
              : <Badge tone="blue">{hb.reviewer} · {eff?.editable.llm_effort}</Badge>} />
            <Line k="Capital" v={inr(eff?.editable.capital ?? hb?.capital)} />
            <Line k="Risk per trade" v={eff ? `${eff.editable.risk_per_trade_pct}% (${inr((eff.editable.capital * eff.editable.risk_per_trade_pct) / 100)})` : "–"} />
            <Line k="Daily loss limit" v={eff ? <LossMeter used={Math.max(0, -(realized + unrealized))} limit={(eff.editable.capital * eff.editable.max_daily_loss_pct) / 100} /> : "–"} />
            <Line k="Entry window" v={eff ? `${eff.editable.entry_start}–${eff.editable.entry_end}, flat by ${eff.editable.flatten_at}` : "–"} />
          </div>
        </Card>
      </div>

      <div className="grid cols-2">
        <Card title="Signals" icon={<Sparkles size={15} />} delay={0.15} action={<span className="subtle">click to expand</span>}>
          <SignalFeed signals={signals} sessionDay={sessionDay} />
        </Card>
        <Card title="Activity" icon={<Clock size={15} />} delay={0.2}>
          <Activity events={events} />
        </Card>
      </div>
    </div>
  );
}

function labelFor(control: LiveState["control"], name: string) {
  return control.strategy_catalog?.find((s) => s.name === name)?.label ?? name;
}

function Banner({ tone, icon, text, action }: { tone: "bad" | "warn" | "info"; icon: React.ReactNode; text: string; action?: React.ReactNode }) {
  return (
    <motion.div className={`banner ${tone}`} initial={{ opacity: 0, height: 0, marginBottom: 0 }} animate={{ opacity: 1, height: "auto", marginBottom: 0 }}
      exit={{ opacity: 0, height: 0 }} transition={{ duration: 0.25 }}>
      {icon}<span className="grow">{text}</span>{action}
    </motion.div>
  );
}

function KV({ k, v }: { k: string; v: React.ReactNode }) {
  return <div className="kv"><div className="k">{k}</div><div className="v">{v}</div></div>;
}

function Line({ k, v }: { k: string; v: React.ReactNode }) {
  return <div className="row" style={{ justifyContent: "space-between" }}><span className="ink2">{k}</span><span style={{ fontWeight: 550, textAlign: "right" }}>{v}</span></div>;
}

function LossMeter({ used, limit }: { used: number; limit: number }) {
  const frac = limit > 0 ? Math.min(used / limit, 1) : 0;
  const color = frac > 0.75 ? "var(--critical)" : frac > 0.4 ? "var(--warning)" : "var(--accent)";
  return (
    <span style={{ display: "inline-flex", alignItems: "center", gap: 8 }}>
      <span style={{ width: 90, height: 6, borderRadius: 99, background: "var(--grid)", overflow: "hidden", display: "inline-block" }}>
        <motion.span style={{ display: "block", height: "100%", background: color, borderRadius: 99 }} animate={{ width: `${frac * 100}%` }} transition={spring} />
      </span>
      <span className="subtle">{inr(used)} / {inr(limit)}</span>
    </span>
  );
}

function Positions({ positions }: { positions: Position[] }) {
  if (!positions.length) return <Empty title="Flat" hint="No open positions. Entries appear here with a live stop-to-target gauge." />;
  return (
    <div className="list">
      <AnimatePresence initial={false}>
        {positions.map((p) => {
          const long = p.side === "BUY";
          const span = long ? p.target - p.stop : p.stop - p.target;
          const at = (x: number) => Math.min(100, Math.max(0, ((long ? x - p.stop : p.stop - x) / span) * 100));
          return (
            <motion.div key={p.symbol} layout {...fadeUp} className="row" style={{ display: "block" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span className="sym">{p.symbol}</span>
                <Badge tone={long ? "blue" : "bad"}>{long ? "LONG" : "SHORT"} {p.qty}</Badge>
                <span className="subtle">{num(p.entry)} → {num(p.ltp)}</span>
                <span style={{ marginLeft: "auto", fontWeight: 650 }}>
                  <AnimatedNumber value={p.unrealized} format={(n) => signedInr(n)} className={pnlClass(p.unrealized)} />
                </span>
              </div>
              <div className="range" title="stop ← entry · price → target">
                <span className="entry" style={{ left: `${at(p.entry)}%` }} />
                <motion.span className="ltp" initial={false} animate={{ left: `${at(p.ltp)}%` }} transition={{ type: "spring", stiffness: 160, damping: 22 }} />
              </div>
              <div className="range-labels"><span>stop {num(p.stop)}</span><span>since {hhmm(p.opened_at)}</span><span>target {num(p.target)}</span></div>
            </motion.div>
          );
        })}
      </AnimatePresence>
    </div>
  );
}

function verdict(s: SignalCard) {
  const d = s.decision;
  if (!d) return <Badge>no review</Badge>;
  if (d.error) return <Badge tone="warn" title={d.error}>review failed</Badge>;
  return d.approve ? <Badge tone="good">approved {Math.round(d.size_multiplier * 100)}%</Badge> : <Badge tone="bad">vetoed</Badge>;
}

function SignalFeed({ signals, sessionDay }: { signals: SignalCard[]; sessionDay: string }) {
  const [open, setOpen] = useState<string | null>(null);
  if (!signals.length) return <Empty title="No signals yet" hint="Each strategy signal shows up here with the reviewer's verdict and, later, how it played out." />;
  return (
    <div className="list" style={{ maxHeight: 520, overflowY: "auto" }}>
      <AnimatePresence initial={false}>
        {signals.map((s) => {
          const o = s.outcome;
          const isOpen = open === s.id;
          return (
            <motion.div key={s.id} layout className="signal" initial={{ opacity: 0, y: -10, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={spring} onClick={() => setOpen(isOpen ? null : s.id)}>
              <div className="signal-top">
                <span className="subtle mono">{s.signal_ts.slice(0, 10) === sessionDay ? hhmm(s.signal_ts) : dayTime(s.signal_ts)}</span>
                <span className="sym">{s.symbol}</span>
                <Badge tone={s.side === "BUY" ? "blue" : "bad"}>{s.side}</Badge>
                {verdict(s)}
                {o && <Badge tone={Number(o.r_multiple) > 0 ? "good" : "bad"} title={`virtual outcome: ${o.outcome}`}>{Number(o.r_multiple) > 0 ? "+" : ""}{Number(o.r_multiple).toFixed(2)}R</Badge>}
                <motion.span style={{ marginLeft: "auto", display: "inline-flex" }} animate={{ rotate: isOpen ? 180 : 0 }}><ChevronDown size={15} className="ink2" /></motion.span>
              </div>
              <AnimatePresence initial={false}>
                {isOpen && (
                  <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} style={{ overflow: "hidden" }}>
                    <div className="signal-body">
                      <div>Entry {num(s.entry)} · stop {num(s.stop)} · target {num(s.target)} · {s.strategy}</div>
                      <div style={{ marginTop: 6 }}>{s.reason}</div>
                      {s.decision && <div style={{ marginTop: 6 }}><strong>{s.decision.model}:</strong> {s.decision.rationale} <span className="subtle">(confidence {Number(s.decision.confidence).toFixed(2)})</span></div>}
                      {o && <div style={{ marginTop: 6 }} className="subtle">Played out: hit {o.outcome} at {hhmm(o.closed_at)}{o.risk_approved ? "" : " (not traded)"}</div>}
                    </div>
                    {s.decision?.risk_flags?.length ? <div className="flags">{s.decision.risk_flags.map((f) => <Badge key={f} tone="warn">{f.replaceAll("_", " ")}</Badge>)}</div> : null}
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

function Activity({ events }: { events: EventRow[] }) {
  const rows = useMemo(() => events.filter((e) => e.kind !== "risk_verdict").slice(0, 25), [events]);
  if (!rows.length) return <Empty title="Quiet" hint="Engine events show up here." />;
  return (
    <div className="list" style={{ maxHeight: 520, overflowY: "auto" }}>
      <AnimatePresence initial={false}>
        {rows.map((e) => (
          <motion.div key={e.id} layout {...fadeUp} className="row">
            <span className="subtle mono" style={{ flex: "none" }}>{hhmm(e.created_at)}</span>
            <span className="grow trunc" title={e.message}>{e.message}</span>
            <Badge tone={ALERT_KINDS.has(e.kind) ? "bad" : ""}>{e.kind.replaceAll("_", " ")}</Badge>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}

function LoadingLive() {
  return (
    <div className="grid">
      <div className="card"><Skeleton height={20} width={160} /><div style={{ height: 14 }} /><Skeleton height={52} width={260} /><div style={{ height: 14 }} /><Skeleton height={120} /></div>
      <div className="grid cols-2"><div className="card"><Skeleton height={140} /></div><div className="card"><Skeleton height={140} /></div></div>
    </div>
  );
}
