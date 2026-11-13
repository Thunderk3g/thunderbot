"use client";

import { LoaderCircle } from "lucide-react";
import { useState } from "react";
import { asset } from "@/lib/assets";
import { dayTime, inr, num, signedInr } from "@/lib/format";
import type { Basket, DriftRow, ExecMode, NextDeposit, PortfolioExtras, TaxYear } from "@/lib/portfolio";
import type { Holding } from "@/lib/types";
import { Button, Empty } from "./ui";

type Act = (action: string, extra?: Record<string, unknown>) => Promise<void>;
const ORDER = ["nifty", "next50", "gold", "mid", "parked"];
const varOf = (symbol: string) => `var(--a-${asset(symbol).kind === "next50" ? "next" : asset(symbol).kind})`;

/** The corridor each sleeve may drift in before anything is sold: 5 points, or a fifth of its target if
 *  that is tighter. Used only when the worker has not published its own table. */
export function driftFrom(holdings: Holding[], target: Record<string, number> | null, band = { abs_pct: 5, rel_pct: 20 }): DriftRow[] {
  if (!target) return [];
  const have = new Map(holdings.map((h) => [h.symbol, h]));
  return Object.entries(target).filter(([, t]) => t > 0).map(([symbol, t]) => {
    const h = have.get(symbol);
    const half = Math.min(band.abs_pct, (band.rel_pct / 100) * t);
    const weight = h?.weight ?? 0;
    return { symbol, weight, target: t, lo: Math.max(0, t - half), hi: t + half, out: Math.abs(weight - t) >= half, value: h?.value ?? 0 };
  });
}

/** Bullet graphs on one shared axis: the band a sleeve may sit in, its target, and where it is now. */
export function DriftCorridor({ rows, next }: { rows: DriftRow[]; next?: NextDeposit }) {
  if (!rows.length) return <Empty title="No targets yet.">Choose a plan and the corridor for each holding appears here.</Empty>;
  const sorted = [...rows].sort((a, b) => ORDER.indexOf(asset(a.symbol).kind) - ORDER.indexOf(asset(b.symbol).kind));
  const max = Math.max(60, Math.ceil(Math.max(...rows.map((r) => Math.max(r.hi, r.weight))) / 10) * 10);
  const x = (v: number) => `${(Math.min(v, max) / max) * 100}%`;
  const ticks = Array.from({ length: max / 10 + 1 }, (_, i) => i * 10);
  return (
    <div className="corridor" role="table" aria-label="Each holding against its target and the band it may drift in">
      {sorted.map((r) => {
        const a = asset(r.symbol);
        const gets = next?.symbol === r.symbol;
        return (
          <div className={`corridor-row ${r.out ? "out" : ""}`} role="row" key={r.symbol}>
            <div className="who" role="cell"><i className={`swatch ${a.kind}`} />{a.known ? a.name : r.symbol}</div>
            <div className="bar" role="cell" aria-label={`${r.weight.toFixed(1)}% now, target ${r.target.toFixed(0)}%, band ${r.lo.toFixed(0)} to ${r.hi.toFixed(0)}%`}>
              <span className="band" style={{ left: x(r.lo), width: `calc(${x(r.hi)} - ${x(r.lo)})` }} />
              <span className="fill" style={{ width: x(r.weight), background: varOf(r.symbol) }} />
              <span className="tick" style={{ left: x(r.target) }} />
              {gets && <span className="gets" style={{ left: x(r.weight) }} title="The next deposit goes here">▲</span>}
            </div>
            <div className="num" role="cell"><b>{r.weight.toFixed(1)}%</b><span> of {r.target.toFixed(0)}</span></div>
            <div className="state" role="cell">{r.out ? (r.weight > r.target ? "above its band" : "below its band") : gets ? "next deposit" : "in band"}</div>
          </div>
        );
      })}
      <div className="corridor-axis" aria-hidden>{ticks.map((t) => <span key={t} style={{ left: x(t) }}>{t}%</span>)}</div>
      <p className="small soft">The shaded band is how far a holding may drift before anything is sold; the tick is its target. New money goes to the holding furthest below its target, so most months nothing needs selling.</p>
    </div>
  );
}

/** Add money without selling anything: it is routed to whatever is furthest below target. */
export function CashFlowRouter({ next, pending, act }: { next?: NextDeposit; pending?: number; act: Act }) {
  const [amount, setAmount] = useState("");
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState<string | null>(null);
  const value = Number(amount.replace(/[^\d.]/g, ""));
  const add = async () => {
    setBusy(true);
    setNote(null);
    try { await act("deposit", { amount: value }); setAmount(""); setNote(`${inr(value)} added. It is invested at the next daily check.`); }
    catch (e) { setNote(e instanceof Error ? e.message : String(e)); }
    setBusy(false);
  };
  return (
    <div className="form">
      <p>
        {next
          ? <>The next rupee goes to <b>{asset(next.symbol).known ? asset(next.symbol).name : next.symbol}</b>, which is {inr(next.short_inr)} ({num(next.short_pct, 1)} points) short of its target.</>
          : "Every holding is at or above its target, so a deposit is split across them in their target shares."}
        {pending ? <> {inr(pending)} is waiting for the next check.</> : null}
      </p>
      <div className="field">
        <label htmlFor="deposit">Money you are adding</label>
        <div className="key-row">
          <input id="deposit" className="input tnum" inputMode="numeric" placeholder="₹ 10,000" value={amount} onChange={(e) => setAmount(e.target.value)} />
          <Button variant="primary" onClick={add} disabled={busy || !(value > 0)}>{busy && <LoaderCircle size={14} className="spin" />}Add deposit</Button>
        </div>
        <span className="hint">Deposits only ever buy. Nothing is sold, so no tax is realised.</span>
      </div>
      {note && <p className="small soft" role="status">{note}</p>}
    </div>
  );
}

/** How much of this year's tax-free allowance on long-term equity gains is used, and what could still use it. */
export function TaxHarvestMeter({ tax, act }: { tax: TaxYear; act: Act }) {
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState<string | null>(null);
  const used = Math.max(0, Math.min(tax.realized_ltcg, tax.exempt));
  const canUse = Math.max(0, Math.min(tax.harvestable_gain, tax.remaining));
  const pctOf = (v: number) => `${(v / tax.exempt) * 100}%`;
  const go = async () => {
    setBusy(true);
    try { await act("harvest", { confirm: true }); setNote("Queued. The sale happens at the next check and the rebuy on the session after."); setConfirming(false); }
    catch (e) { setNote(e instanceof Error ? e.message : String(e)); }
    setBusy(false);
  };
  return (
    <div className="form">
      <p>
        <b>{inr(used)}</b> of this year&apos;s {inr(tax.exempt)} tax-free allowance on long-term equity gains is used.{" "}
        {canUse > 0
          ? <>You hold <b>{inr(tax.harvestable_gain)}</b> of unrealised long-term gains; booking {inr(canUse)} of it before 31 March would cost no tax and raise your cost base.</>
          : tax.remaining <= 0 ? "The allowance is used up for this year." : "Nothing you hold has a long-term gain to book yet."}
      </p>
      <div className="meter" role="img" aria-label={`${inr(used)} used, ${inr(canUse)} could be used, of ${inr(tax.exempt)}`}>
        <span className="used" style={{ width: pctOf(used) }} />
        <span className="can" style={{ width: pctOf(canUse) }} />
      </div>
      <div className="meter-key"><span><i className="used" />Used {inr(used)}</span><span><i className="can" />Could book {inr(canUse)}</span><span>{tax.days_left} days left in {tax.fy}</span></div>
      {tax.lots.length > 0 && (
        <div className="table-wrap"><table className="dense">
          <thead><tr><th>Holding</th><th className="num">Units</th><th className="num">Gain</th><th className="num">Held</th><th className="gap">How</th></tr></thead>
          <tbody>{tax.lots.map((l, i) => (
            <tr key={i}><td>{asset(l.symbol).known ? asset(l.symbol).name : l.symbol}</td><td className="num">{num(l.qty, 0)}</td><td className="num gain">{signedInr(l.gain)}</td>
              <td className="num">{l.held_days} days</td><td className="gap">{l.via === "twin" ? `swap into ${l.twin} the same day` : "sell, then rebuy the next session"}</td></tr>
          ))}</tbody>
        </table></div>
      )}
      {canUse > 0 && !confirming && <div className="btn-row"><Button onClick={() => setConfirming(true)}>Plan this harvest</Button></div>}
      {confirming && (
        <div className="notice caution" style={{ alignItems: "flex-start", flexWrap: "wrap" }}>
          <span className="grow">This sells and rebuys to book about {inr(canUse)} of gains. A sale and rebuy of the same fund on one day counts as intraday and books nothing, so the rebuy waits a session; the money is out of the market overnight. Confirm with a chartered accountant before doing this with real money.</span>
          <span className="btn-row"><Button size="sm" variant="primary" onClick={go} disabled={busy}>{busy && <LoaderCircle size={14} className="spin" />}Queue it</Button><Button size="sm" variant="quiet" onClick={() => setConfirming(false)}>Cancel</Button></span>
        </div>
      )}
      {note && <p className="small soft" role="status">{note}</p>}
      <p className="small soft">{tax.note}</p>
    </div>
  );
}

const BASKET_WHY: Record<string, string> = {
  rebalance: "The plan rebalanced", deposit: "Your deposit is being invested", sell_all: "You asked to sell everything",
  harvest: "This books gains inside the year's tax-free allowance", harvest_rebuy: "This buys back what was sold to book gains",
};

/** Guided basket: the orders to place by hand, as a checklist, and a way to say they are done. */
export function BasketTicket({ basket, act }: { basket: Basket; act: Act }) {
  const [done, setDone] = useState<Set<number>>(new Set());
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);
  const orders = [...basket.orders].sort((a, b) => (a.side === b.side ? 0 : a.side === "SELL" ? -1 : 1));
  const text = orders.map((o) => `${o.side === "BUY" ? "Buy" : "Sell"} ${o.qty} ${o.symbol} limit ${o.limit}`).join("\n");
  const copy = async () => { try { await navigator.clipboard.writeText(text); setCopied(true); setTimeout(() => setCopied(false), 1800); } catch { /* clipboard unavailable */ } };
  const finish = async () => { setBusy(true); try { await act("basket_done", { id: basket.id }); } finally { setBusy(false); } };
  const toggle = (i: number) => setDone((d) => { const n = new Set(d); if (n.has(i)) n.delete(i); else n.add(i); return n; });
  if (basket.status !== "open") {
    return (
      <p className="soft">
        The basket of {dayTime(basket.at)} is {basket.status === "reconciled" ? "reconciled: your holdings match it" : "closed"}.
        {basket.mismatch?.length ? ` Differences: ${basket.mismatch.join("; ")}.` : ""}
      </p>
    );
  }
  return (
    <>
      <p style={{ marginBottom: 10 }}>{BASKET_WHY[basket.reason] ?? basket.reason}. Place these in the Groww app as limit orders, sells first, then tick them off.</p>
      <ul className="basket">
        {orders.map((o, i) => (
          <li key={`${o.side}-${o.symbol}`} className={done.has(i) ? "done" : ""}>
            <label>
              <input type="checkbox" checked={done.has(i)} onChange={() => toggle(i)} />
              <span className={`side ${o.side === "BUY" ? "gain" : "loss"}`}>{o.side === "BUY" ? "Buy" : "Sell"}</span>
              <span className="what"><b>{o.qty} × {o.symbol}</b> <span className="soft">limit ₹{num(o.limit)}</span><span className="why soft">{o.why}</span></span>
              <span className="amount">{inr(o.value)}</span>
            </label>
          </li>
        ))}
      </ul>
      <div className="btn-row" style={{ marginTop: 14 }}>
        <Button onClick={copy}>{copied ? "Copied" : "Copy the list"}</Button>
        <Button variant="primary" onClick={finish} disabled={busy || done.size < orders.length}>{busy && <LoaderCircle size={14} className="spin" />}I have placed these</Button>
      </div>
      <p className="small soft" style={{ marginTop: 10, maxWidth: "66ch" }}>
        Nothing is sent to your broker from here. When your holdings are next read, the basket is checked against what you actually hold and any difference is shown.
      </p>
    </>
  );
}

const MODES: { id: ExecMode; name: string; line: string }[] = [
  { id: "paper", name: "Paper", line: "Pretend money at live prices. The place to start." },
  { id: "guided", name: "Guided basket", line: "Real money, placed by you. The bot works out the orders; you place them in Groww. Needs no fixed IP." },
  { id: "auto", name: "Automated", line: "The bot places the orders. Works only where the worker runs on your registered static IP with the live switch set there." },
];

export function ModePicker({ extras, act }: { extras: PortfolioExtras; act: Act }) {
  const mode = extras.exec_mode ?? "paper";
  const [busy, setBusy] = useState<ExecMode | null>(null);
  const pick = async (m: ExecMode) => { if (m === mode) return; setBusy(m); try { await act("set_mode", { mode: m }); } finally { setBusy(null); } };
  return (
    <div className="plans" role="radiogroup" aria-label="How orders are placed">
      {MODES.map((m) => (
        <button key={m.id} type="button" role="radio" aria-checked={m.id === mode} className="plan" onClick={() => pick(m.id)} disabled={busy !== null}>
          <span className="plan-name">{m.name}<span className="radio" /></span>
          <p>{m.line}</p>
        </button>
      ))}
      {extras.exec_note && <p className="small soft">{extras.exec_note}</p>}
    </div>
  );
}
