"use client";

import { BrainCircuit, ChevronDown, LoaderCircle, OctagonX, Play, RefreshCw, Zap } from "lucide-react";
import { Fragment, useMemo, useState } from "react";
import { ago, inr, num, signedInr } from "@/lib/format";
import type { AIDesk, DeskDecision, DeskPosition, GroupStats, Job, LiveState, ModelReport } from "@/lib/types";
import { post, startJob, usePoll, wakeWorker } from "@/lib/usePoll";
import { PnlBars, PnlCurve } from "./charts";
import { Button, HoldButton, Segmented, StatusDot } from "./ui";

const STATUS: Record<AIDesk["status"], { tone: "on" | "off" | "idle"; text: string }> = {
  running: { tone: "on", text: "Trading (paper)" },
  closing: { tone: "idle", text: "Stopped; closing open trades" },
  paused: { tone: "idle", text: "Paused: managing open trades only" },
  halted: { tone: "off", text: "Halted: daily loss limit hit" },
  off: { tone: "idle", text: "Off" },
  waiting: { tone: "idle", text: "Waiting for the open (09:15 IST)" },
  closed: { tone: "idle", text: "Market closed" },
  no_prices: { tone: "off", text: "No prices from Yahoo" },
};
const REGIME: Record<string, string> = {
  trend_up: "Trending up", trend_down: "Trending down", quiet_range: "Quiet range", choppy: "Choppy", unknown: "No read yet",
};
const SETUP: Record<string, string> = {
  orb: "Opening-range breakout", vwap_reversion: "VWAP reversion", ema_pullback: "EMA pullback", momentum: "Momentum burst",
};
const FEATURE: Record<string, string> = {
  mins: "Time of day", dow: "Day of week", ret_1: "Last bar's move", ret_3: "15-minute move", ret_6: "30-minute move",
  ret_12: "60-minute move", ret_open: "Move since the open", gap: "Opening gap", vwap_dist_atr: "Distance from VWAP",
  atr_pct: "Volatility (ATR)", range_pos: "Place in the day's range", bar_range_atr: "Size of the signal bar", bar_body: "Signal bar's body",
  rvol: "Volume vs usual (bar)", cum_rvol: "Volume vs usual (day)", rsi: "RSI", ema_spread_atr: "EMA 9 vs 21", or_pos: "Place vs opening range",
  trend_bars: "Bars going the trade's way", pd_ext_dist_atr: "Beyond yesterday's extreme", pd_opp_dist_atr: "Room from yesterday's other extreme",
  idx_ret_open: "Nifty since the open", idx_ret_6: "Nifty, last 30 minutes", idx_range_pos: "Nifty's place in its range",
  rel_strength: "Strength vs Nifty", stop_pct: "Stop distance", reward_risk: "Reward to risk", side: "Long or short",
  gen_orb: "Is a breakout", gen_vwap_reversion: "Is a reversion", gen_ema_pullback: "Is a pullback", gen_momentum: "Is a momentum burst",
};
const VERDICT: Record<string, { tag: string; cls: string }> = {
  edge_supported: { tag: "Edge found", cls: "use" }, weak_positive: { tag: "Unproven", cls: "warn" },
  no_edge: { tag: "No edge yet", cls: "bad" }, too_few: { tag: "Too little data", cls: "warn" },
};

const sign = (n: number | null | undefined, d = 2) => (n === null || n === undefined ? "–" : `${n > 0 ? "+" : ""}${n.toFixed(d)}`);
const tone = (n: number | null | undefined) => (!n ? "" : n > 0 ? "gain" : "loss");

export default function DeskView({ state, refresh }: { state: LiveState | null; refresh: () => void }) {
  const control = state?.control;
  const desk = control?.ai_desk;
  const summary = control?.ai_model ?? null;
  const ai = usePoll<{ model: { id: string; created_at: string; report: ModelReport } | null; job: Job | null }>("/api/ai", 8000);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const run = async (name: string, fn: () => Promise<unknown>) => {
    setBusy(name);
    setError(null);
    try { await fn(); } catch (e) { setError(e instanceof Error ? e.message : String(e)); }
    setBusy(null);
    refresh();
    ai.refresh();
  };
  const start = () => run("start", async () => { await post("/api/control", { action: "ai_start" }); await wakeWorker(); });
  const stop = () => run("stop", async () => { await post("/api/control", { action: "ai_stop" }); await wakeWorker().catch(() => undefined); });
  const wake = () => run("wake", () => wakeWorker());
  const retrain = () => run("train", () => startJob("train", {}));
  const setStrict = (v: "0" | "1") => run("mode", () => post("/api/control", { action: "ai_params", params: { ...(desk?.params ?? {}), strict: Number(v) } }));

  const enabled = !!control?.intraday_enabled && !control?.kill_switch;
  const status = desk ? STATUS[desk.status] ?? STATUS.off : { tone: "idle" as const, text: "Not started yet" };
  const stats = desk?.stats;
  const dayPnl = (stats?.realized ?? 0) + (stats?.unrealized ?? 0);
  const curve = useMemo(() => (desk?.curve ?? []).map(([t, v]) => ({ time: `${desk!.day}T${t}:00+05:30`, value: v })), [desk]);
  const training = ai.data?.job && (ai.data.job.status === "queued" || ai.data.job.status === "running") ? ai.data.job : null;
  const report = ai.data?.model?.report ?? null;
  const market = desk?.market ?? {};
  const strict = String(desk?.params?.strict ?? 0) as "0" | "1";

  return (
    <div className="desk">
      <section className="slab desk-head">
        <div className="desk-title">
          <div>
            <p className="eyebrow"><BrainCircuit size={14} aria-hidden /> AI desk · intraday · NSE cash</p>
            <h1 className="desk-state"><StatusDot tone={status.tone} />{status.text}</h1>
            <p className="soft small">
              {desk ? <>Last bar {desk.bar ?? "–"} · updated {ago(desk.at)} · {desk.universe} stocks watched · {desk.limits.entry_window} entries, flat by {desk.limits.flatten_at}</>
                : "The worker has not reported on the desk yet. Press Start, or Run a bar now."}
            </p>
          </div>
          <div className="desk-actions">
            {enabled
              ? <HoldButton onConfirm={stop}><OctagonX size={15} />Hold to stop</HoldButton>
              : <Button variant="primary" onClick={start} disabled={busy !== null}>{busy === "start" ? <LoaderCircle size={15} className="spin" /> : <Play size={15} />}Start paper trading</Button>}
            <Button onClick={wake} disabled={busy !== null} title="Run the worker once now instead of waiting for the next 5-minute call">
              {busy === "wake" ? <LoaderCircle size={15} className="spin" /> : <RefreshCw size={15} />}Run a bar now
            </Button>
          </div>
        </div>

        <dl className="desk-kpis">
          <div className="kpi main"><dt>Today, after costs</dt><dd className={tone(dayPnl)}>{signedInr(dayPnl)}</dd></div>
          <div className="kpi"><dt>Closed</dt><dd className={tone(stats?.realized)}>{signedInr(stats?.realized ?? 0)}</dd></div>
          <div className="kpi"><dt>Open</dt><dd className={tone(stats?.unrealized)}>{signedInr(stats?.unrealized ?? 0)}</dd></div>
          <div className="kpi"><dt>Trades</dt><dd>{stats?.trades ?? 0}<small> / {desk?.limits.max_trades_per_day ?? "–"}</small></dd></div>
          <div className="kpi"><dt>Won · lost</dt><dd>{stats?.wins ?? 0} · {stats?.losses ?? 0}</dd></div>
          <div className="kpi"><dt>Setups seen</dt><dd>{stats?.setups ?? 0}</dd></div>
          <div className="kpi"><dt>Charges</dt><dd>{inr(stats?.costs ?? 0)}</dd></div>
        </dl>

        <div className="desk-chips">
          <span className="pill"><b>Market</b>{REGIME[market.label ?? "unknown"] ?? market.label}
            {market.index_ret_open_pct !== undefined && <em className={tone(market.index_ret_open_pct)}>Nifty {sign(market.index_ret_open_pct)}%</em>}
            {market.breadth_up_pct !== undefined && <em>{market.breadth_up_pct}% of stocks up</em>}
          </span>
          <span className="pill"><b>Model</b>{summary ? <>{VERDICT[summary.verdict]?.tag ?? summary.verdict}<em>AUC {summary.auc?.toFixed(2) ?? "–"}</em><em>trained {ago(summary.trained_at)}</em></>
            : training ? "Training now" : "Not trained yet"}</span>
          <span className="pill"><b>Trader</b>{desk?.llm.on ? <>{desk.llm.provider}<em>{desk.llm.model}</em></> : <>No LLM connected<em>the model decides alone</em></>}</span>
          <span className="pill"><b>Risk</b>{desk ? <>{desk.limits.risk_per_trade_pct}% a trade<em>stop at −{desk.limits.max_daily_loss_pct}% a day</em><em>max {desk.limits.max_open_positions} open</em></> : "–"}</span>
        </div>
      </section>

      {error && <div className="notice stop"><span className="grow">{error}</span></div>}
      {desk?.feed_error && <div className="notice stop"><span className="grow">{desk.feed_error}</span></div>}
      {stats?.halted && <div className="notice stop"><span className="grow">{stats.halt_reason || "Trading is halted for the day."}</span></div>}
      {desk && !desk.llm.on && (
        <div className="notice caution"><span className="grow">
          No LLM is connected, so setups that pass the model are taken without a second opinion. Add <code>LLM_API_KEY</code>, <code>LLM_BASE_URL</code> and <code>LLM_MODEL</code> to
          the Vercel project (the same three your GrokBot uses) and redeploy.
        </span></div>
      )}

      <div className="desk-grid">
        <div className="desk-main">
          <Block title="Open positions" aside={desk?.positions.length ? `${desk.positions.length} open` : undefined}>
            {desk?.positions.length ? <Positions rows={desk.positions} /> : <p className="quiet">Nothing open.{desk?.pending.length ? ` ${desk.pending.length} entry waiting for the next bar.` : ""}</p>}
          </Block>

          <Block title="Decision tape" aside="Every setup today: what the model scored, what the trader decided, how it ended">
            {desk?.decisions.length ? <Tape rows={desk.decisions} /> : (
              <p className="quiet">{enabled ? "No setups yet today. The desk checks every 5 minutes between " + (desk?.limits.entry_window ?? "09:30-14:30") + " IST." : "The desk is off. Start it to see setups here."}</p>
            )}
          </Block>
          <Block title="The model" aside={
            <span className="aside-actions">
              <Segmented label="How strict" value={strict} onChange={setStrict}
                options={[{ value: "0", label: "Learning" }, { value: "1", label: "Strict" }]} />
              <Button size="sm" onClick={retrain} disabled={busy !== null || !!training}>
                {training ? <LoaderCircle size={14} className="spin" /> : <Zap size={14} />}{training ? `Training ${Math.round((training.progress ?? 0) * 100)}%` : "Retrain"}
              </Button>
            </span>}>
            <ModelCard report={report} summary={summary} strict={strict === "1"} jobError={ai.data?.job?.status === "error" ? ai.data.job.error ?? "training failed" : null} />
          </Block>
        </div>

        <aside className="desk-side">
          <Block title="Today's P&L">
            {curve.length > 1 ? <PnlCurve points={curve} intraday height={170} label="P&L" /> : <p className="quiet">The line starts with the first bar the desk trades.</p>}
          </Block>
          <Block title="Watchlist" aside={desk?.watch.length ? "by move today" : undefined}>
            {desk?.watch.length ? <Watch desk={desk} /> : <p className="quiet">Prices appear once the desk has run a bar in market hours.</p>}
          </Block>
          <Block title="Desk notes" aside={control?.ai_memory?.last_review ? control.ai_memory.last_review.day : undefined}>
            <Notes control={control} />
          </Block>
          <Block title="Paper record">
            <Record control={control} />
          </Block>
          <Block title="Before real money">
            <Readiness control={control} />
          </Block>
        </aside>
      </div>
    </div>
  );
}

function Block({ title, aside, children }: { title: string; aside?: React.ReactNode; children: React.ReactNode }) {
  return (
    <section className="block">
      <header><h2>{title}</h2>{aside && <div className="block-aside">{aside}</div>}</header>
      {children}
    </section>
  );
}

function Positions({ rows }: { rows: DeskPosition[] }) {
  return (
    <div className="table-wrap">
      <table className="dense">
        <thead><tr><th>Stock</th><th>Side</th><th className="num">Qty</th><th className="num">Entry</th><th className="num">Now</th><th className="gap">Stop → target</th><th className="num">P&L</th></tr></thead>
        <tbody>
          {rows.map((p) => {
            const lo = Math.min(p.stop, p.target), hi = Math.max(p.stop, p.target);
            const at = Math.min(100, Math.max(0, ((p.ltp - lo) / (hi - lo)) * 100));
            const entryAt = ((p.entry - lo) / (hi - lo)) * 100;
            const flip = p.side === "SELL";
            return (
              <tr key={p.symbol}>
                <td><strong>{p.symbol}</strong><span className="sub">{SETUP[p.generator ?? ""] ?? p.generator}</span></td>
                <td><span className={`side ${p.side === "BUY" ? "buy" : "sell"}`}>{p.side === "BUY" ? "Long" : "Short"}</span></td>
                <td className="num">{p.qty}</td><td className="num">{num(p.entry)}</td><td className="num">{num(p.ltp)}</td>
                <td className="gap">
                  <div className="range" title={`Stop ${p.stop} · entry ${p.entry} · target ${p.target}`}>
                    <span className="range-entry" style={{ left: `${flip ? 100 - entryAt : entryAt}%` }} />
                    <span className={`range-now ${tone(p.unrealized)}`} style={{ left: `${flip ? 100 - at : at}%` }} />
                  </div>
                  <span className="sub">{num(p.stop)} → {num(p.target)}</span>
                </td>
                <td className={`num ${tone(p.unrealized)}`}>{signedInr(p.unrealized)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function outcomeOf(d: DeskDecision): { text: string; cls: string } {
  if (d.verdict === "take") {
    if (d.status === "closed") return { text: `${signedInr(d.pnl ?? 0)} · ${(d.exit ?? "").replaceAll("_", " ")}`, cls: tone(d.pnl) };
    if (d.status === "open") return { text: "open", cls: "" };
    return { text: d.status ?? "–", cls: "" };
  }
  if (d.r !== undefined) return { text: `would have made ${sign(d.r)}R`, cls: d.r > 0 ? "missed" : "dodged" };
  return { text: "watching", cls: "soft" };
}

function Tape({ rows }: { rows: DeskDecision[] }) {
  const [open, setOpen] = useState<string | null>(null);
  const ordered = useMemo(() => [...rows].reverse(), [rows]);
  return (
    <div className="table-wrap">
      <table className="dense tape">
        <thead><tr><th>Time</th><th>Stock</th><th>Setup</th><th className="num">Model</th><th className="gap">Decision</th><th>By</th><th>Result</th><th /></tr></thead>
        <tbody>
          {ordered.map((d) => {
            const out = outcomeOf(d);
            const isOpen = open === d.id;
            return (
              <Fragment key={d.id}>
                <tr className={`${d.verdict} ${isOpen ? "open" : ""}`} onClick={() => setOpen(isOpen ? null : d.id)}>
                  <td className="tnum">{d.t}</td>
                  <td><strong>{d.symbol}</strong> <span className={`side ${d.side === "BUY" ? "buy" : "sell"}`}>{d.side === "BUY" ? "Long" : "Short"}</span></td>
                  <td>{SETUP[d.kind] ?? d.kind}</td>
                  <td className="num">{d.prob === null ? "–" : (
                    <span className="score" title={d.expected_r !== null ? `Expected ${sign(d.expected_r)}R after costs` : undefined}>
                      <i style={{ width: `${Math.round(d.prob * 100)}%` }} />{Math.round(d.prob * 100)}%
                    </span>)}
                  </td>
                  <td className="gap"><span className={`call ${d.verdict}`}>{d.verdict === "take" ? "Take" : "Skip"}</span>{d.size !== undefined && d.verdict === "take" && d.size < 1 && <span className="sub"> at {Math.round(d.size * 100)}% size</span>}</td>
                  <td className="by">{d.by || "–"}</td>
                  <td className={out.cls}>{out.text}</td>
                  <td className="chev"><ChevronDown size={14} aria-label={isOpen ? "Hide reasoning" : "Show reasoning"} /></td>
                </tr>
                {isOpen && (
                  <tr className="why">
                    <td colSpan={8}>
                      <div className="why-grid">
                        <div><b>Setup</b><p>{d.why}</p><p className="soft">Entry {num(d.entry)} · stop {num(d.stop)} · target {num(d.target)}{d.qty ? ` · ${d.qty} shares` : ""}</p></div>
                        <div><b>{d.verdict === "take" ? "Why it was taken" : "Why it was skipped"}</b>
                          <p>{d.note || "No note."}</p>
                          {d.flags?.length > 0 && <p className="flags">{d.flags.map((f) => <span key={f}>{f.replaceAll("_", " ")}</span>)}</p>}
                          {d.error && <p className="loss">LLM error: {d.error}</p>}
                        </div>
                        <div><b>Model</b><p>{d.prob === null ? "No model yet: passed through unscored." : `${Math.round(d.prob * 100)}% chance of a profit after costs${d.expected_r !== null ? `; expects ${sign(d.expected_r)}R` : ""}.`}</p>
                          {d.r !== undefined && <p className="soft">Followed mechanically it made {sign(d.r)}R ({d.outcome === "eod" ? "held to the close" : `hit its ${d.outcome}`}), before costs.</p>}
                        </div>
                      </div>
                    </td>
                  </tr>
                )}
              </Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function Watch({ desk }: { desk: AIDesk }) {
  const rows = useMemo(() => [...desk.watch].sort((a, b) => Math.abs(b.chg_pct) - Math.abs(a.chg_pct)), [desk.watch]);
  const held = new Set(desk.positions.map((p) => p.symbol));
  return (
    <div className="table-wrap watch">
      <table className="dense">
        <thead><tr><th>Stock</th><th className="num">Price</th><th className="num">Day</th><th className="num">vs VWAP</th><th className="num">Vol ×</th></tr></thead>
        <tbody>
          {rows.map((w) => (
            <tr key={w.symbol}>
              <td>{held.has(w.symbol) && <i className="held" title="Position open" />}{w.symbol}</td>
              <td className="num">{num(w.ltp)}</td>
              <td className={`num ${tone(w.chg_pct)}`}>{sign(w.chg_pct)}%</td>
              <td className={`num ${tone(w.vs_vwap_pct)}`}>{sign(w.vs_vwap_pct)}%</td>
              <td className={`num ${w.rvol !== null && w.rvol >= 1.5 ? "hot" : "soft"}`}>{w.rvol === null ? "–" : w.rvol.toFixed(1)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function StatRow({ label, g, mark }: { label: string; g?: GroupStats; mark?: boolean }) {
  if (!g) return null;
  return (
    <tr className={mark ? "top" : ""}>
      <td>{label}</td><td className="num">{g.n}</td><td className="num">{g.win_pct === null ? "–" : `${g.win_pct}%`}</td>
      <td className={`num ${tone(g.avg_r)}`}>{sign(g.avg_r)}R</td><td className={`num ${tone(g.total_r)}`}>{sign(g.total_r, 0)}R</td>
      <td className="num soft">{g.t === null ? "–" : g.t.toFixed(1)}</td>
    </tr>
  );
}

function ModelCard({ report, summary, strict, jobError }: { report: ModelReport | null; summary: LiveState["control"]["ai_model"]; strict: boolean; jobError: string | null }) {
  if (!report) {
    return (
      <>
        {jobError && <div className="notice stop" style={{ marginBottom: 12 }}><span className="grow">Training failed: {jobError}</span></div>}
        <p className="quiet">{summary ? "Loading the report." : "No model yet. The desk trains one from the last 60 days of 5-minute bars the first time it runs (about a minute), or press Retrain."}</p>
      </>
    );
  }
  const v = VERDICT[report.verdict] ?? { tag: report.verdict, cls: "" };
  const o = report.oos;
  const maxImp = Math.max(...report.importance.map(([, x]) => x), 0.0001);
  return (
    <div className="model">
      {jobError && <div className="notice stop" style={{ marginBottom: 12 }}><span className="grow">The last training run failed: {jobError}</span></div>}
      <p className="model-verdict"><span className={`tag ${v.cls}`}>{v.tag}</span>{report.verdict_text}</p>
      <p className="small soft">
        Trained on {report.setups.toLocaleString("en-IN")} setups from {report.symbols} stocks, {report.first_day} to {report.last_day}. Every figure below is from days the model
        had not seen (from {o.from}), after Groww&apos;s charges and slippage. 1R is the amount risked on a trade.
        {strict ? (report.policy.strict === null ? " Strict mode is on and no score level has been profitable, so the desk will not trade until that changes."
          : ` Strict mode is on: only setups scored ${Math.round(report.policy.strict * 100)}% or higher are traded.`)
          : ` Learning mode is on: the desk trades the best-scored 30% (scores of ${Math.round(report.policy.learn * 100)}% or more) to build a record, whatever the verdict.`}
      </p>
      <div className="model-grid">
        <div>
          <h3>By score</h3>
          <table className="dense">
            <thead><tr><th>Group</th><th className="num">Trades</th><th className="num">Won</th><th className="num">Each</th><th className="num">Total</th><th className="num">t</th></tr></thead>
            <tbody>
              <StatRow label="Every setup" g={o.by_share["100"]} />
              <StatRow label="Best-scored half" g={o.by_share["50"]} />
              <StatRow label="Best 30% (traded)" g={o.by_share["30"]} mark />
              <StatRow label="Best 20%" g={o.by_share["20"]} />
              <StatRow label="Best 10%" g={o.by_share["10"]} />
            </tbody>
          </table>
          <h3>By setup</h3>
          <table className="dense">
            <thead><tr><th>Setup</th><th className="num">Trades</th><th className="num">Won</th><th className="num">Each</th><th className="num">Total</th><th className="num">t</th></tr></thead>
            <tbody>{Object.entries(o.by_generator).map(([g, s]) => <StatRow key={g} label={SETUP[g] ?? g} g={s} />)}</tbody>
          </table>
          <p className="small soft">Ranking skill (AUC): {o.auc?.toFixed(2) ?? "–"}, where 0.50 is a coin toss. {o.base_win_pct}% of all setups made money.</p>
        </div>
        <div>
          <h3>What the model looks at most</h3>
          <ul className="bars">
            {report.importance.slice(0, 9).map(([name, x]) => (
              <li key={name}><span>{FEATURE[name] ?? name}</span><i><b style={{ width: `${(x / maxImp) * 100}%` }} /></i><em>{Math.round(x * 100)}%</em></li>
            ))}
          </ul>
          <h3>Best 30%, running total (R)</h3>
          {o.curve.length > 1 ? <Spark rows={o.curve} /> : <p className="quiet">Not enough days yet.</p>}
          {report.note && <p className="small soft">{report.note}</p>}
        </div>
      </div>
    </div>
  );
}

/** Running total in R for the traded group (solid) against taking every setup (faint). */
function Spark({ rows }: { rows: [string, number, number][] }) {
  const W = 420, H = 120, pad = 4;
  const vals = rows.flatMap(([, m, a]) => [m, a]).concat(0);
  const lo = Math.min(...vals), hi = Math.max(...vals), span = hi - lo || 1;
  const x = (i: number) => pad + (i / (rows.length - 1)) * (W - 2 * pad);
  const y = (v: number) => pad + (1 - (v - lo) / span) * (H - 2 * pad);
  const path = (k: 1 | 2) => rows.map((r, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(r[k]).toFixed(1)}`).join(" ");
  const last = rows[rows.length - 1];
  return (
    <figure className="spark">
      <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`Running total: ${last[1]}R for the best-scored 30%, ${last[2]}R for every setup`}>
        <line x1={pad} x2={W - pad} y1={y(0)} y2={y(0)} className="zero" />
        <path d={path(2)} className="all" />
        <path d={path(1)} className={last[1] >= 0 ? "model up" : "model down"} />
      </svg>
      <figcaption><span><i className={last[1] >= 0 ? "k up" : "k down"} />Best 30%: {sign(last[1], 0)}R</span><span><i className="k all" />Every setup: {sign(last[2], 0)}R</span>
        <span className="soft">{rows[0][0].slice(5)} to {last[0].slice(5)}</span></figcaption>
    </figure>
  );
}

function Notes({ control }: { control?: LiveState["control"] }) {
  const mem = control?.ai_memory;
  const review = mem?.last_review;
  if (!review && !mem?.lessons?.length) return <p className="quiet">After each close the desk writes up its day here. With an LLM connected it also keeps a few lessons and reads them before every decision.</p>;
  return (
    <div className="notes">
      {review && (
        <p>{review.summary || `${review.numbers.trades} trade${review.numbers.trades === 1 ? "" : "s"}, net ${signedInr(review.numbers.net_pnl)}.`}
          {review.numbers.skipped_avg_r !== null && <span className="soft"> Skipped setups averaged {sign(review.numbers.skipped_avg_r)}R; taken ones {sign(review.numbers.taken_avg_r)}R.</span>}</p>
      )}
      {mem?.lessons?.length ? <ul>{[...mem.lessons].reverse().map((l, i) => <li key={i}><span className="soft">{l.day.slice(5)}</span>{l.text}</li>)}</ul> : null}
    </div>
  );
}

function Record({ control }: { control?: LiveState["control"] }) {
  const days = control?.ai_history ?? [];
  if (!days.length) return <p className="quiet">Each trading day is added here after the close.</p>;
  const net = days.reduce((a, d) => a + d.net, 0), trades = days.reduce((a, d) => a + d.trades, 0), wins = days.reduce((a, d) => a + d.wins, 0);
  return (
    <>
      <dl className="mini">
        <div><dt>Net, after costs</dt><dd className={tone(net)}>{signedInr(net)}</dd></div>
        <div><dt>Trades</dt><dd>{trades}</dd></div>
        <div><dt>Won</dt><dd>{trades ? `${Math.round((wins / trades) * 100)}%` : "–"}</dd></div>
        <div><dt>Days</dt><dd>{days.length}</dd></div>
      </dl>
      {days.length > 1 && <PnlBars points={days.map((d) => ({ time: d.day, value: d.net }))} height={110} />}
    </>
  );
}

function Readiness({ control }: { control?: LiveState["control"] }) {
  const env = control?.effective_settings?.env_only;
  const days = control?.ai_history ?? [];
  const trades = days.reduce((a, d) => a + d.trades, 0), net = days.reduce((a, d) => a + d.net, 0);
  const verdict = control?.ai_model?.verdict;
  const items: { ok: boolean; text: string; detail: string }[] = [
    { ok: verdict === "edge_supported", text: "The model shows an edge out of sample", detail: verdict ? VERDICT[verdict]?.tag ?? verdict : "not trained" },
    { ok: trades >= 100 && net > 0, text: "100 paper trades with a profit after costs", detail: `${trades} so far, ${signedInr(net)}` },
    { ok: !!env?.groww_configured, text: "Groww Trade API key on the trading machine", detail: env?.groww_configured ? "set" : "not set here" },
    { ok: !!env?.static_ip_configured, text: "A static IP registered with Groww", detail: env?.static_ip_configured ? "set" : "Vercel has none" },
  ];
  return (
    <>
      <ul className="checks">
        {items.map((i) => <li key={i.text} className={i.ok ? "ok" : ""}><span>{i.text}</span><em>{i.detail}</em></li>)}
      </ul>
      <p className="small soft">
        This desk trades on paper. Brokers accept API orders only from a static IP registered to your account, which Vercel cannot provide, so real orders need a small
        always-on machine running <code>thunderbot live</code> with <code>TB_STRATEGY=ai</code>. It uses this same model, LLM and risk limits. See docs/ai-desk.md.
      </p>
    </>
  );
}
