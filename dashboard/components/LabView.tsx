"use client";

import { AnimatePresence, motion } from "motion/react";
import { LoaderCircle } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { dayTime, inr, num, pct, signedInr } from "@/lib/format";
import type { BacktestResult, Control, InvestResult, Job, ParamSpec, StrategyInfo, SweepResult, SweepRow } from "@/lib/types";
import { post, usePoll, startJob } from "@/lib/usePoll";
import { PnlCurve } from "./charts";
import InvestLab, { InvestResultView, ModeSwitch, NoResult, planName } from "./InvestLab";
import { Button, ChipsInput, Empty, Figures, Panel, Progress, Section, Segmented, SliderField, spring } from "./ui";

type Kind = "backtest" | "sweep";
type Source = "yahoo" | "demo" | "csv" | "groww";
const SOURCE_NAME: Record<string, string> = { yahoo: "Yahoo Finance", demo: "practice data", csv: "saved candles", groww: "Groww history" };
const tone = (n: number | null | undefined) => (!n ? "" : n > 0 ? "gain" : "loss") as "" | "gain" | "loss";

function isoDaysAgo(days: number): string {
  return new Date(Date.now() - days * 86_400_000).toLocaleDateString("en-CA", { timeZone: "Asia/Kolkata" });
}

function defaultsFor(s?: StrategyInfo): Record<string, number> {
  return Object.fromEntries((s?.params ?? []).map((p) => [p.name, p.default]));
}

function sweepValues(p: ParamSpec, center: number): string {
  const step = p.type === "int" ? Math.max(1, Math.round((p.max - p.min) / 10)) : Math.max(p.step, Number(((p.max - p.min) / 10).toFixed(2)));
  const vals = [center - step, center, center + step].map((v) => Math.min(p.max, Math.max(p.min, Number(v.toFixed(2)))));
  return [...new Set(vals)].join(", ");
}

export default function LabView({ control, onApplied, onUsed, only }: { control?: Control; onApplied: () => void; onUsed?: () => void; only?: "invest" | "intraday" }) {
  const [picked, setMode] = useState<"invest" | "intraday">("invest");
  const mode = only ?? picked;
  const [investJob, setInvestJob] = useState<string | null>(null);
  const [stage, setStage] = useState<"choose" | "test" | "use">("choose");
  if (mode === "invest") {
    const inUse = control?.invest_settings ? JSON.stringify([control.invest_settings.strategy, control.invest_settings.params]) : undefined;
    const useStrategy = async (r: InvestResult) => {
      await post("/api/control", { action: "invest_settings", strategy: r.strategy, params: r.strategy_params });
      onUsed?.();
    };
    return (
      <div className="page">
        <LabHeader mode={mode} setMode={setMode} only={only} />
        <ol className="trail" aria-label="Steps">
          <li className={stage !== "choose" ? "done" : ""} aria-current={stage === "choose" ? "step" : undefined}>Choose a plan</li>
          <li className={stage === "use" ? "done" : ""} aria-current={stage === "test" ? "step" : undefined}>Test it on past years</li>
          <li aria-current={stage === "use" ? "step" : undefined}>Use it</li>
        </ol>
        <div className="split form">
          <div>
            <InvestLab control={control} onJob={(id) => { setInvestJob(id); setStage("test"); }} />
            <div style={{ marginTop: 32 }}><History selected={investJob} onSelect={(id) => { setInvestJob(id); setStage("test"); }} kinds={["invest"]} /></div>
          </div>
          <div>{investJob
            ? <JobView id={investJob} onApply={async () => {}} onUseInvest={useStrategy} inUse={inUse} onDone={() => setStage("use")} />
            : <NoResult />}</div>
        </div>
      </div>
    );
  }
  return <IntradayLab control={control} onApplied={onApplied} mode={mode} setMode={setMode} only={only} />;
}

function LabHeader({ mode, setMode, only }: { mode: "invest" | "intraday"; setMode: (m: "invest" | "intraday") => void; only?: "invest" | "intraday" }) {
  if (only === "intraday") {
    return <p className="lede" style={{ marginTop: 0 }}>Test an intraday rule on past prices with the same code that trades. Every result is marked down for how many settings have been tried.</p>;
  }
  return (
    <div className="page-head">
      <div>
        <h1>{mode === "invest" ? "Choose a plan you can live with." : "Intraday research."}</h1>
        <p className="lede">
          {mode === "invest"
            ? "Each plan is a fixed rule. Test it on up to 17 years of real NSE prices, after Groww's charges and capital-gains tax, before you trust it with anything."
            : "Test an intraday strategy on past prices with the same code that trades. These strategies lost money in our tests; this room is for research, not income."}
        </p>
      </div>
      {!only && <ModeSwitch value={mode} onChange={setMode} />}
    </div>
  );
}

function IntradayLab({ control, onApplied, mode, setMode, only }: { control?: Control; onApplied: () => void; mode: "invest" | "intraday"; setMode: (m: "invest" | "intraday") => void; only?: "invest" | "intraday" }) {
  const catalog = control?.strategy_catalog ?? [];
  const eff = control?.effective_settings;
  const [kind, setKind] = useState<Kind>("backtest");
  const [strategy, setStrategy] = useState<string>("");
  const [params, setParams] = useState<Record<string, number>>({});
  const [symbols, setSymbols] = useState<string[]>([]);
  const [source, setSource] = useState<Source>("yahoo");
  // Yahoo keeps 5-minute bars for about 60 days, so default to the last 8 weeks.
  const [start, setStart] = useState(() => isoDaysAgo(56));
  const [end, setEnd] = useState(() => isoDaysAgo(0));
  const [grid, setGrid] = useState<Record<string, string>>({});
  const [jobId, setJobId] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const info = catalog.find((s) => s.name === strategy);

  useEffect(() => {
    if (!strategy && eff && catalog.length) {
      setStrategy(eff.editable.strategy);
      setParams({ ...defaultsFor(catalog.find((s) => s.name === eff.editable.strategy)), ...eff.editable.strategy_params });
      setSymbols(eff.editable.symbols);
    }
  }, [eff, catalog, strategy]);

  const pickStrategy = (name: string) => {
    setStrategy(name);
    setParams(defaultsFor(catalog.find((s) => s.name === name)));
    setGrid({});
  };
  const combos = useMemo(() => Object.values(grid).reduce((n, v) => n * Math.max(1, v.split(",").filter((x) => x.trim()).length), 1), [grid]);

  const submit = async () => {
    setSubmitError(null);
    setSubmitting(true);
    try {
      const gridValues = Object.fromEntries(Object.entries(grid).map(([k, v]) => [k, v.split(",").map((x) => Number(x.trim())).filter((x) => Number.isFinite(x))]));
      setJobId(await startJob(kind, { strategy, strategy_params: params, symbols, data: source, start, end, ...(kind === "sweep" ? { grid: gridValues } : {}) }));
    } catch (e) {
      setSubmitError(e instanceof Error ? e.message : String(e));
    } finally {
      setSubmitting(false);
    }
  };

  const apply = async (sp: Record<string, number>) => {
    const current = (control?.settings_overrides ?? {}) as Record<string, unknown>;
    await post("/api/settings", { overrides: { ...current, strategy, strategy_params: sp } });
    onApplied();
  };

  if (!catalog.length) {
    return (
      <div className="page">
        <LabHeader mode={mode} setMode={setMode} only={only} />
        <Empty title="The strategy list hasn't loaded.">It's published by the worker. Start <code>thunderbot serve</code> locally, or <code>thunderbot jobs</code> on the server.</Empty>
      </div>
    );
  }

  return (
    <div className="page">
      <LabHeader mode={mode} setMode={setMode} only={only} />
      <div className="split form">
        <div>
          <Panel>
            <div className="form">
              <Segmented<Kind> label="Experiment type" value={kind} onChange={setKind} options={[{ value: "backtest", label: "Backtest" }, { value: "sweep", label: "Sweep" }]} />
              <div className="field">
                <label htmlFor="lab-strategy">Strategy</label>
                <select id="lab-strategy" className="input" value={strategy} onChange={(e) => pickStrategy(e.target.value)}>
                  {catalog.map((s) => <option key={s.name} value={s.name}>{s.label}</option>)}
                </select>
                {info && <span className="hint">{info.description}</span>}
              </div>
              {info?.params.map((p) => (
                <div key={p.name}>
                  <SliderField label={p.label} value={params[p.name] ?? p.default} min={p.min} max={p.max} step={p.step} onChange={(v) => setParams({ ...params, [p.name]: v })} />
                  <AnimatePresence initial={false}>
                    {kind === "sweep" && (
                      <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} style={{ overflow: "hidden" }}>
                        <div className="toggle-row" style={{ marginTop: 6 }}>
                          <label className="hint" style={{ display: "flex", gap: 6, alignItems: "center" }}>
                            <input type="checkbox" checked={p.name in grid} onChange={(e) => {
                              const g = { ...grid };
                              if (e.target.checked) g[p.name] = sweepValues(p, params[p.name] ?? p.default);
                              else delete g[p.name];
                              setGrid(g);
                            }} />Try several values
                          </label>
                          {p.name in grid && <input className="input tnum" style={{ maxWidth: 170 }} aria-label={`${p.label} values`} value={grid[p.name]} onChange={(e) => setGrid({ ...grid, [p.name]: e.target.value })} />}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              ))}
              <div className="field"><label>Stocks</label><ChipsInput values={symbols} onChange={setSymbols} placeholder="Add" /></div>
              <div className="field">
                <label>Prices</label>
                <Segmented<Source> label="Price data" value={source} onChange={setSource} options={[
                  { value: "yahoo", label: "Yahoo (free)" }, { value: "demo", label: "Practice" }, { value: "csv", label: "Saved" },
                  ...(eff?.env_only.groww_configured ? [{ value: "groww" as Source, label: "Groww" }] : []),
                ]} />
                <span className="hint">{source === "yahoo" ? "Real NSE prices from Yahoo Finance, free. 5-minute bars go back about 60 days." : source === "demo" ? "Random prices for learning the tools. No strategy can have an edge on them." : source === "csv" ? "Candles saved on the server with thunderbot fetch-history." : "Downloaded from Groww for the dates below."}</span>
              </div>
              <div className="time-grid">
                <div className="field"><label htmlFor="lab-from">From</label><input id="lab-from" type="date" className="input" value={start} onChange={(e) => setStart(e.target.value)} /></div>
                <div className="field"><label htmlFor="lab-to">To</label><input id="lab-to" type="date" className="input" value={end} onChange={(e) => setEnd(e.target.value)} /></div>
              </div>
              {kind === "sweep" && (
                <p className={`hint ${combos > 60 ? "loss" : ""}`}>
                  {Object.keys(grid).length ? `${combos} combinations to test (up to 60).` : "Pick one to three settings to try several values of."}
                </p>
              )}
              {submitError && <div className="notice stop"><span className="grow">{submitError}</span></div>}
              <Button variant="primary" block onClick={submit} disabled={submitting || !symbols.length || (kind === "sweep" && (!Object.keys(grid).length || combos > 60))}>
                {submitting && <LoaderCircle size={15} className="spin" />}{kind === "sweep" ? "Run sweep" : "Run backtest"}
              </Button>
            </div>
          </Panel>
          <div style={{ marginTop: 28 }}><History selected={jobId} onSelect={setJobId} kinds={["backtest", "sweep"]} /></div>
        </div>
        <div>{jobId ? <JobView id={jobId} onApply={apply} /> : <Empty title="Results appear here.">Pick a strategy and run a backtest on real prices from Yahoo. Practice data is only for learning the tools.</Empty>}</div>
      </div>
    </div>
  );
}

function History({ selected, onSelect, kinds }: { selected: string | null; onSelect: (id: string) => void; kinds: Job["kind"][] }) {
  const { data: all } = usePoll<Job[]>("/api/jobs", 4000);
  const data = all?.filter((j) => kinds.includes(j.kind));
  if (!data?.length) return null;
  const status = (j: Job) => j.status === "running" ? `${Math.round(Number(j.progress) * 100)}%` : j.status === "done" ? "done" : j.status === "error" ? "failed" : "waiting";
  return (
    <Section title="Earlier runs" className="" >
      <div className="rows" style={{ marginTop: 4 }}>
        {data.map((j) => (
          <button key={j.id} type="button" className="row-button" onClick={() => onSelect(j.id)} aria-current={selected === j.id}>
            <div className="row small" style={selected === j.id ? { background: "var(--wash-strong)" } : undefined}>
              <span className="grow trunc">{j.kind === "invest"
                ? <><strong>{planName(String(j.params.strategy))}</strong> over {String(j.params.years ?? 15)} years</>
                : <><strong>{String(j.params.strategy ?? "")}</strong> {j.kind} on {SOURCE_NAME[String(j.params.data)] ?? String(j.params.data)}</>}</span>
              <span className="time">{dayTime(j.created_at)}</span>
              <span className={j.status === "error" ? "loss" : "soft"} style={{ width: 52, textAlign: "right" }}>{status(j)}</span>
            </div>
          </button>
        ))}
      </div>
    </Section>
  );
}

function JobView({ id, onApply, onUseInvest, inUse, onDone }: {
  id: string; onApply: (sp: Record<string, number>) => Promise<void>; onUseInvest?: (r: InvestResult) => Promise<void>; inUse?: string; onDone?: () => void;
}) {
  const [interval, setIntervalMs] = useState(1000);
  const { data: job } = usePoll<Job>(`/api/jobs?id=${id}`, interval);
  const finished = !!job && (job.status === "done" || job.status === "error");
  useEffect(() => setIntervalMs(finished ? 60_000 : 1000), [finished]);
  useEffect(() => { if (job?.status === "done") onDone?.(); }, [job?.status, id]); // eslint-disable-line react-hooks/exhaustive-deps
  if (!job || job.status === "queued" || job.status === "running") {
    return (
      <div>
        <h2>{!job || job.status === "queued" ? "Waiting for the worker" : job.kind === "sweep" ? "Running the sweep" : job.kind === "invest" ? "Testing over the years" : "Running the backtest"}</h2>
        <div style={{ margin: "14px 0 10px" }}><Progress value={Number(job?.progress) || 0.03} /></div>
        <p className="small soft">{job?.status === "queued" ? "Experiments run on the worker. If this doesn't start within a minute, the worker function isn't deployed (or, on your own machine, thunderbot serve isn't running)." : "Same code as live trading, replayed over past prices."}</p>
      </div>
    );
  }
  if (job.status === "error") return <div className="notice stop"><span className="grow">The experiment failed: {job.error}</span></div>;
  if (job.kind === "invest") {
    const r = job.result as InvestResult;
    return <InvestResultView r={r} onUse={onUseInvest ? () => onUseInvest(r) : undefined} inUse={inUse === JSON.stringify([r.strategy, r.strategy_params])} />;
  }
  return job.kind === "sweep" ? <SweepView r={job.result as SweepResult} onApply={onApply} /> : <BacktestView r={job.result as BacktestResult} onApply={onApply} />;
}

function BacktestView({ r, onApply }: { r: BacktestResult; onApply: (sp: Record<string, number>) => Promise<void> }) {
  const m = r.metrics;
  let cum = 0;
  const curve = r.equity.map((e) => ({ time: e.date, value: (cum += e.pnl) }));
  return (
    <motion.div className="page" style={{ gap: 36 }} initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div>
        <p className="hero-line" style={{ marginTop: 0, fontSize: 21, color: "var(--ink)" }}>
          It would have {m.net_pnl >= 0 ? "made" : "lost"} <strong className={tone(m.net_pnl)}>{inr(Math.abs(m.net_pnl))}</strong> from {m.trades} trades
          over {String(m.days)} days, after {inr(m.total_costs as number)} in costs.
        </p>
        <p className="small soft" style={{ marginTop: 6 }}>{r.data_note}</p>
        <div style={{ marginTop: 20 }}>
          <Figures items={[
            { label: "Won", value: pct(m.win_rate_pct as number, 0) },
            { label: "Profit factor", value: num(m.profit_factor as number | null) },
            { label: "Worst drawdown", value: pct(-(m.max_drawdown_pct as number)), tone: "loss" },
            { label: "Sharpe ratio", value: num(m.sharpe_daily_annualized as number | null) },
          ]} />
        </div>
      </div>
      <Section title="Running total" aside={<Button size="sm" onClick={() => onApply(r.strategy_params)}>Use these settings</Button>}>
        <PnlCurve points={curve} height={240} label="total" />
      </Section>
      <div className="split even">
        <Section title="By stock">
          <div className="table-wrap"><table>
            <thead><tr><th>Stock</th><th className="num">Trades</th><th className="num">Won</th><th className="num">Net</th></tr></thead>
            <tbody>{Object.entries(r.per_symbol).sort(([, a], [, b]) => b.net_pnl - a.net_pnl).map(([s, v]) => (
              <tr key={s}><td className="ticker">{s}</td><td className="num">{v.trades}</td><td className="num">{pct((v.wins / v.trades) * 100, 0)}</td><td className={`num ${tone(v.net_pnl)}`}>{signedInr(v.net_pnl)}</td></tr>
            ))}</tbody>
          </table></div>
        </Section>
        <Section title="How trades ended">
          <dl className="facts">
            {Object.entries((m.exit_reasons ?? {}) as Record<string, number>).map(([k, v]) => (
              <div key={k} style={{ display: "contents" }}><dt>{({ stop: "Stop loss", target: "Target", eod_flatten: "End of day", stop_gap: "Gapped past stop", target_gap: "Gapped past target", daily_loss_halt: "Daily loss limit" } as Record<string, string>)[k] ?? k}</dt><dd className="tnum">{v}</dd></div>
            ))}
          </dl>
        </Section>
      </div>
      <Section title={`Last ${Math.min(r.trades.length, 60)} trades`}>
        <div className="table-wrap" style={{ maxHeight: 360, overflowY: "auto" }}><table>
          <thead><tr><th>Closed</th><th>Stock</th><th>Side</th><th className="num">Qty</th><th className="num">Entry</th><th className="num">Exit</th><th>Ended by</th><th className="num">Net</th></tr></thead>
          <tbody>{r.trades.slice(-60).reverse().map((t, i) => (
            <tr key={i}><td className="tnum">{dayTime(t.closed_at)}</td><td className="ticker">{t.symbol}</td><td>{t.side === "BUY" ? "Long" : "Short"}</td><td className="num">{t.qty}</td>
              <td className="num">{num(t.entry)}</td><td className="num">{num(t.exit)}</td><td>{t.reason.replaceAll("_", " ")}</td><td className={`num ${tone(t.net_pnl)}`}>{signedInr(t.net_pnl)}</td></tr>
          ))}</tbody>
        </table></div>
      </Section>
    </motion.div>
  );
}

/** A setting clears the bar only if its Sharpe is still likely above zero after every setting ever tried
 *  on this data is counted (deflated Sharpe of 0.95 or more). Older results fall back to their own flag. */
const clears = (row: SweepRow) => (row.dsr !== undefined && row.dsr !== null ? row.dsr >= 0.95 : !!row.robust);

function SweepView({ r, onApply }: { r: SweepResult; onApply: (sp: Record<string, number>) => Promise<void> }) {
  const [applied, setApplied] = useState<number | null>(null);
  const [confirming, setConfirming] = useState<number | null>(null);
  const names = r.axes.map((a) => a.name);
  const deflated = r.rows.some((row) => row.dsr !== undefined && row.dsr !== null);
  const passed = r.rows.filter(clears).length;
  const choose = async (i: number, row: SweepRow) => {
    // A setting that only won on the history it was picked from is usually overfit: make that a deliberate choice.
    if (!clears(row) && confirming !== i) return setConfirming(i);
    await onApply(row.params);
    setApplied(i);
    setConfirming(null);
  };
  return (
    <motion.div className="page" style={{ gap: 28 }} initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div>
        <p className="hero-line" style={{ marginTop: 0, fontSize: 21, color: "var(--ink)" }}>
          {r.verdict ?? (passed
            ? `${passed} of ${r.rows.length} settings held up on prices they hadn't seen.`
            : `None of the ${r.rows.length} settings held up on prices they hadn't seen.`)}
        </p>
        <p className="small soft" style={{ marginTop: 6, maxWidth: "74ch" }}>
          {deflated
            ? <>Try enough settings and one will look good by luck. {r.trials ? <><b>{r.trials} settings</b> have now been tried on this data, across every sweep, and each result below is marked down for all of them. </> : null}
              &ldquo;Deflated&rdquo; is the chance a setting&apos;s Sharpe is really above zero after that; 95% is the bar.
              {r.pbo !== undefined && r.pbo !== null ? <> Across {r.blocks ?? "the"} blocks of days, the setting that looked best on one half finished in the bottom half on the other <b>{Math.round(r.pbo * 100)}%</b> of the time; near 50% means the ranking is noise.</> : null}</>
            : <>Ranked by results before {r.split_date}; the &ldquo;after&rdquo; columns are the honest test.</>} {r.data_note}
        </p>
      </div>
      <div className="table-wrap"><table>
        <thead><tr>
          {names.map((n) => <th key={n} className="num">{n.replaceAll("_", " ")}</th>)}
          <th className="num">Before</th><th className="num">Trades</th><th className="num">After</th><th className="num">Trades</th>
          {deflated && <><th className="num">Sharpe</th><th className="num">Deflated</th></>}<th></th><th></th>
        </tr></thead>
        <tbody>
          {r.rows.map((row, i) => (
            <motion.tr key={i} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: Math.min(i * 0.02, 0.5), ...spring }} className={clears(row) ? "top" : ""}>
              {names.map((n) => <td key={n} className="num">{num(row.params[n])}</td>)}
              <td className={`num ${tone(Number(row.in_sample.net_pnl))}`}>{signedInr(row.in_sample.net_pnl)}</td>
              <td className="num">{row.in_sample.trades}</td>
              <td className={`num ${tone(Number(row.out_of_sample.net_pnl))}`}>{signedInr(row.out_of_sample.net_pnl)}</td>
              <td className="num">{row.out_of_sample.trades}</td>
              {deflated && <><td className="num">{row.sharpe === null || row.sharpe === undefined ? "–" : num(row.sharpe)}</td>
                <td className="num">{row.dsr === null || row.dsr === undefined ? "–" : `${Math.round(row.dsr * 100)}%`}</td></>}
              <td className="gain small">{clears(row) ? "clears the bar" : ""}</td>
              <td style={{ textAlign: "right" }}>
                <Button size="sm" variant={applied === i ? "primary" : confirming === i ? "stop" : ""} onClick={() => choose(i, row)}
                  title={clears(row) ? "Trade with these settings" : "These settings did not clear the bar"}>
                  {applied === i ? "In use" : confirming === i ? "Below the bar. Use anyway?" : "Use"}
                </Button>
              </td>
            </motion.tr>
          ))}
        </tbody>
      </table></div>
    </motion.div>
  );
}
