"use client";

import { ArrowLeft } from "lucide-react";
import { dayTime, inr, num, signed, signedInr } from "@/lib/format";
import { usePoll } from "@/lib/usePoll";
import { DecisionTrace, type Gate, type TraceEnd } from "./DecisionTrace";
import JournalView from "./JournalView";
import { Empty, Tabs } from "./ui";

type Row = {
  id: string; at: string; symbol: string; side: string; strategy: string; mode: string; harness_id: string | null;
  asked: boolean; llm: "take" | "shrunk" | "skip" | "failed" | "none"; size: number | null; model: string | null;
  taken: boolean | null; outcome: string | null; r: number | null;
};
type Ledger = { rows: Row[]; attribution: { n: number; taken: number; all_r: number; gates_r: number; taken_r: number } };
type Rec = Record<string, unknown>;
type One = { signal: Rec; decision: Rec | null; outcome: Rec | null; orders: Rec[]; trades: Rec[] };

const SETUP: Record<string, string> = { orb: "Opening-range breakout", vwap_reversion: "VWAP reversion", ema_pullback: "EMA pullback", momentum: "Momentum burst", ai: "Desk setup" };
const LLM_WORD: Record<Row["llm"], string> = { take: "said take", shrunk: "cut the size", skip: "said skip", failed: "call failed", none: "not asked" };
const str = (v: unknown) => (v === null || v === undefined ? "" : String(v));
const numOf = (v: unknown) => (v === null || v === undefined || v === "" ? null : Number(v));

export default function JournalPage({ go, sub }: { go: (to: string) => void; sub?: string }) {
  if (sub && sub !== "log") return <DecisionPage id={sub} go={go} />;
  const current = sub === "log" ? "/journal/log" : "/journal";
  return (
    <div>
      <div className="page-head" style={{ marginBottom: 22 }}>
        <div>
          <h1>Journal</h1>
          <p className="lede">Everything the machine decided and did, including the trades it did not take and what they went on to do.</p>
        </div>
      </div>
      <Tabs go={go} current={current} items={[{ href: "/journal", label: "Decisions" }, { href: "/journal/log", label: "Events and orders" }]} />
      {current === "/journal" ? <Decisions go={go} /> : <JournalView />}
    </div>
  );
}

function Decisions({ go }: { go: (to: string) => void }) {
  const ledger = usePoll<Ledger>("/api/decisions", 15000);
  const rows = ledger.data?.rows ?? [];
  const a = ledger.data?.attribution;
  if (!ledger.data) return <Empty title={ledger.error ? "The ledger could not be read." : "Loading."}>{ledger.error ?? ""}</Empty>;
  if (!rows.length) return <Empty title="No decisions yet.">Every setup the rules propose is written here, with what each gate did and what the setup went on to do.</Empty>;
  const span = a ? Math.max(1, Math.abs(a.all_r), Math.abs(a.taken_r), Math.abs(a.gates_r)) : 1;
  const bar = (v: number) => ({ left: v >= 0 ? "50%" : `${50 - (Math.abs(v) / span) * 50}%`, width: `${(Math.abs(v) / span) * 50}%` });
  return (
    <div className="page" style={{ gap: 40 }}>
      {a && a.n > 0 && (
        <section className="section">
          <div className="section-head"><h2>What the gates were worth</h2><p>{a.n} settled setups, in units of risk, before charges</p></div>
          <div className="waterfall">
            <div className="wf-row"><span>Every setup, taken blind</span><span className="track"><i className={a.all_r >= 0 ? "gain" : "loss"} style={bar(a.all_r)} /><span className="mid" /></span><span className="v">{signed(a.all_r, 1)}R</span></div>
            <div className="wf-row"><span>What the gates changed</span><span className="track"><i className={a.gates_r >= 0 ? "gain" : "loss"} style={bar(a.gates_r)} /><span className="mid" /></span><span className="v">{signed(a.gates_r, 1)}R</span></div>
            <div className="wf-row"><span>The {a.taken} that were taken</span><span className="track"><i className={a.taken_r >= 0 ? "gain" : "loss"} style={bar(a.taken_r)} /><span className="mid" /></span><span className="v">{signed(a.taken_r, 1)}R</span></div>
          </div>
          <p className="small soft" style={{ marginTop: 12, maxWidth: "70ch" }}>
            If skipping setups helped, the middle bar points right. Charges come off the last bar; the Lab scores each model role after charges and the cost of its own calls.
          </p>
        </section>
      )}
      <section className="section">
        <div className="section-head"><h2>Every setup</h2><p>Open one to see what it knew, who decided, and how it ended</p></div>
        <div className="table-wrap"><table className="ledger">
          <thead><tr><th>When</th><th>Setup</th><th>Rule</th><th>Model said</th><th>Taken</th><th className="num">It went on to make</th><th>Harness</th></tr></thead>
          <tbody>{rows.map((r) => (
            <tr key={r.id}>
              <td className="tnum">{dayTime(r.at)}</td>
              <td><a href={`/journal/${r.id}`} onClick={(e) => { if (!e.metaKey && !e.ctrlKey) { e.preventDefault(); go(`/journal/${r.id}`); } }}><span className="ticker">{r.symbol}</span></a>{" "}
                <span className={`dir ${r.side === "BUY" ? "buy" : "sell"}`}>{r.side === "BUY" ? "long" : "short"}</span></td>
              <td>{SETUP[r.strategy] ?? r.strategy}</td>
              <td>{LLM_WORD[r.llm]}{r.llm === "shrunk" && r.size !== null ? ` to ${Math.round(r.size * 100)}%` : ""}</td>
              <td>{r.taken === null ? "still open" : r.taken ? "yes" : "no"}</td>
              <td className={`num ${r.r === null ? "" : r.r > 0 ? "gain" : r.r < 0 ? "loss" : ""}`}>{r.r === null ? "–" : `${signed(r.r, 2)}R`}</td>
              <td className="tnum soft">{r.harness_id ? r.harness_id.slice(0, 7) : "–"}</td>
            </tr>
          ))}</tbody>
        </table></div>
      </section>
    </div>
  );
}

/** One decision, on its own page: what was proposed, what each gate did, what was known, and how it ended. */
function DecisionPage({ id, go }: { id: string; go: (to: string) => void }) {
  const one = usePoll<One>(`/api/decision?id=${encodeURIComponent(id)}`, 30000);
  const back = <a className="back" href="/journal" onClick={(e) => { e.preventDefault(); go("/journal"); }}><ArrowLeft size={15} />All decisions</a>;
  if (!one.data) {
    return <div className="decision">{back}<Empty title={one.error ? "This decision could not be found." : "Loading."}>{one.error ?? ""}</Empty></div>;
  }
  const { signal: s, decision: d, outcome: o, trades, orders } = one.data;
  const features = (s.features ?? {}) as Rec;
  const prob = numOf(features.ml_prob);
  const long = s.side === "BUY";
  const taken = o ? !!o.risk_approved : trades.length > 0 || orders.length > 0;
  const size = d ? numOf(d.size_multiplier) : null;
  const approve = d ? !!d.approve : null;
  const r = o ? numOf(o.r_multiple) : null;
  const trade = trades[0];
  const net = trade ? numOf(trade.net_pnl) : null;
  const setupName = SETUP[str(features.generator)] ?? SETUP[str(s.strategy)] ?? str(s.strategy);
  const stoppedBy = taken ? null : d ? (d.error ? "the model call failing" : approve === false ? "the model" : "a limit") : prob !== null ? "its score" : "a limit";

  const gates: Gate[] = [];
  if (prob !== null) gates.push({ key: "model", label: "Score", state: !d && !taken ? "cut" : "pass", value: `${Math.round(prob * 100)}%${!d && !taken ? ", too low" : ""}` });
  gates.push(!d ? { key: "llm", label: "Model", state: "absent", value: "not asked" }
    : d.error ? { key: "llm", label: "Model", state: "cut", value: "call failed" }
    : approve === false ? { key: "llm", label: "Model", state: "cut", value: "said skip" }
    : size !== null && size < 1 ? { key: "llm", label: "Model", state: "thin", size, value: "asked for less" }
    : { key: "llm", label: "Model", state: "pass", value: "said take" });
  gates.push(taken ? { key: "limits", label: "Limits", state: "pass", value: trade ? `${str(trade.qty)} shares` : "within limits" }
    : { key: "limits", label: "Limits", state: d && approve !== false && !d.error ? "cut" : "pass", value: d && approve !== false && !d.error ? "over a limit" : undefined });
  const end: TraceEnd = taken
    ? net !== null ? { label: str(trade.exit_reason).replaceAll("_", " ").replace(/^./, (c) => c.toUpperCase()), value: signedInr(net), tone: net > 0 ? "gain" : net < 0 ? "loss" : "" }
      : { label: "Open", value: "position on" }
    : r !== null ? { label: "Not traded", value: r > 0 ? `${signed(r, 1)}R missed` : `${signed(r, 1)}R avoided`, tone: r > 0 ? "ghost" : "gain" }
      : { label: "Not traded", value: "still following" };

  return (
    <div className="decision">
      <div>
        {back}
        <p className="verdict-line">
          <b>{str(s.symbol)}</b>, {long ? "long" : "short"}, was {taken ? "taken" : <>skipped because of <b>{stoppedBy}</b></>}
          {net !== null ? <> and closed <b className={net >= 0 ? "gain" : "loss"}>{signedInr(net)}</b> after costs.</>
            : taken ? " and is still open."
            : r !== null ? <>. Followed anyway, it made <b className={r >= 0 ? "gain" : "loss"}>{signed(r, 2)}R</b>.</> : ". It is still being followed."}
        </p>
        <p className="meta">
          <span>{dayTime(str(s.signal_ts ?? s.created_at))}</span><span>{setupName}</span><span>{str(s.mode)}</span>
          {s.harness_id ? <span>harness {str(s.harness_id).slice(0, 12)}</span> : null}{d?.model ? <span>{str(d.model)}</span> : null}
        </p>
      </div>

      <section className="section">
        <div className="section-head"><h2>How it was decided</h2><p>Left to right, in the order the gates were asked</p></div>
        <div className="stage"><DecisionTrace size="lg" live={taken && net === null} source={{ label: "Rule", value: setupName }} gates={gates} end={end} label="This decision" /></div>
      </section>

      <section className="section">
        <div className="section-head"><h2>What the rule proposed</h2></div>
        <p style={{ maxWidth: "66ch" }}>{str(s.reason)}.</p>
        <dl className="facts" style={{ marginTop: 14 }}>
          <dt>Entry</dt><dd className="tnum">{num(numOf(s.entry))}</dd>
          <dt>Stop</dt><dd className="tnum">{num(numOf(s.stop))}</dd>
          <dt>Target</dt><dd className="tnum">{num(numOf(s.target))}</dd>
        </dl>
      </section>

      {d && (
        <section className="section">
          <div className="section-head"><h2>What the model said</h2><p>Its answer binds nothing beyond no, or less</p></div>
          <div className="voice-block">
            <div className="who"><span className="tag">{str(d.model)}</span><span className="tag">non-binding</span>
              {numOf(d.confidence) !== null && <span>{Math.round((numOf(d.confidence) ?? 0) * 100)}% sure</span>}
              {numOf(d.latency_ms) ? <span>{num((numOf(d.latency_ms) ?? 0) / 1000, 1)} s</span> : null}
              {numOf(d.input_tokens) ? <span>{num(numOf(d.input_tokens), 0)} tokens in, {num(numOf(d.output_tokens), 0)} out</span> : null}
              {numOf(d.cost_inr) ? <span>cost {inr(numOf(d.cost_inr), 2)}</span> : null}</div>
            <p>{str(d.rationale) || "No reason was given."}</p>
            {d.error ? <p className="loss" style={{ fontFamily: "var(--font)" }}>The call failed: {str(d.error)}. A failed call skips the trade.</p> : null}
          </div>
          {str(d.prompt) && (
            <details className="fine" style={{ marginTop: 18 }}>
              <summary>Everything the model was shown</summary>
              <pre>{str(d.prompt)}</pre>
            </details>
          )}
        </section>
      )}

      <section className="section">
        <div className="section-head"><h2>What was known at the time</h2><p>Only bars that had already closed</p></div>
        <pre>{JSON.stringify(features, null, 1)}</pre>
      </section>

      <section className="section">
        <div className="section-head"><h2>How it ended</h2></div>
        <dl className="facts">
          <dt>Followed on paper</dt><dd>{r === null || (taken && net === null) ? "still running" : <>{signed(r, 2)}R, {str(o?.outcome) === "eod" ? "held to the close" : `hit its ${str(o?.outcome)}`}, before charges</>}</dd>
          <dt>Actually traded</dt><dd>{trade ? <>{str(trade.qty)} shares, in at {num(numOf(trade.entry_price))}, out at {num(numOf(trade.exit_price))}, {signedInr(net)} after {inr(numOf(trade.costs))} of charges</> : taken ? "position still open" : "no"}</dd>
          <dt>Orders</dt><dd>{orders.length ? orders.map((x) => `${str(x.purpose)} ${str(x.status).toLowerCase()}`).join(", ") : "none"}</dd>
        </dl>
      </section>
    </div>
  );
}
