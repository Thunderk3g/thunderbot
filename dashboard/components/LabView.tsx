"use client";

import { AnimatePresence, motion } from "motion/react";
import { Check, CircleAlert, FlaskConical, History, LoaderCircle, Play, ShieldCheck, Sparkles } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { dayTime, inr, num, pct, signedInr } from "@/lib/format";
import type { BacktestResult, Control, Job, ParamSpec, StrategyInfo, SweepResult, SweepRow } from "@/lib/types";
import { post, usePoll } from "@/lib/usePoll";
import { PnlCurve } from "./charts";
import { Badge, Button, Card, ChipsInput, Empty, Progress, Segmented, SliderField, Stat, fadeUp, spring } from "./ui";

type Kind = "backtest" | "sweep";
type Source = "demo" | "csv" | "groww";

function defaultsFor(s?: StrategyInfo): Record<string, number> {
  return Object.fromEntries((s?.params ?? []).map((p) => [p.name, p.default]));
}

function sweepValues(p: ParamSpec, center: number): string {
  const step = p.type === "int" ? Math.max(1, Math.round((p.max - p.min) / 10)) : Math.max(p.step, Number(((p.max - p.min) / 10).toFixed(2)));
  const vals = [center - step, center, center + step].map((v) => Math.min(p.max, Math.max(p.min, Number(v.toFixed(2)))));
  return [...new Set(vals)].join(", ");
}

export default function LabView({ control, onApplied }: { control?: Control; onApplied: () => void }) {
  const catalog = control?.strategy_catalog ?? [];
  const eff = control?.effective_settings;
  const [kind, setKind] = useState<Kind>("backtest");
  const [strategy, setStrategy] = useState<string>("");
  const [params, setParams] = useState<Record<string, number>>({});
  const [symbols, setSymbols] = useState<string[]>([]);
  const [source, setSource] = useState<Source>("demo");
  const [start, setStart] = useState("2026-01-05");
  const [end, setEnd] = useState("2026-06-30");
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
      const { id } = await post<{ id: string }>("/api/jobs", {
        kind, params: { strategy, strategy_params: params, symbols, data: source, start, end, ...(kind === "sweep" ? { grid: gridValues } : {}) },
      });
      setJobId(id);
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

  if (!catalog.length) return <div className="card"><Empty icon={<FlaskConical size={28} />} title="Strategy catalog not loaded" hint="Start the worker (`thunderbot serve` locally, or `thunderbot jobs` next to Supabase) to publish it." /></div>;

  return (
    <div className="lab">
        <div className="grid">
          <Card title="Experiment" icon={<FlaskConical size={15} />}>
            <div className="form">
              <Segmented<Kind> value={kind} onChange={setKind} options={[{ value: "backtest", label: "Backtest" }, { value: "sweep", label: "Walk-forward sweep" }]} />
              <div className="field">
                <label>Strategy</label>
                <select className="input" value={strategy} onChange={(e) => pickStrategy(e.target.value)}>
                  {catalog.map((s) => <option key={s.name} value={s.name}>{s.label}</option>)}
                </select>
                {info && <span className="subtle">{info.description}</span>}
              </div>
              {info?.params.map((p) => (
                <div key={p.name}>
                  <SliderField label={p.label} value={params[p.name] ?? p.default} min={p.min} max={p.max} step={p.step}
                    onChange={(v) => setParams({ ...params, [p.name]: v })} />
                  <AnimatePresence initial={false}>
                    {kind === "sweep" && (
                      <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} style={{ overflow: "hidden" }}>
                        <div className="toggle-row" style={{ marginTop: 6 }}>
                          <label className="subtle" style={{ display: "flex", gap: 6, alignItems: "center" }}>
                            <input type="checkbox" checked={p.name in grid} onChange={(e) => {
                              const g = { ...grid };
                              if (e.target.checked) g[p.name] = sweepValues(p, params[p.name] ?? p.default);
                              else delete g[p.name];
                              setGrid(g);
                            }} />sweep
                          </label>
                          {p.name in grid && <input className="input" style={{ maxWidth: 190 }} value={grid[p.name]} onChange={(e) => setGrid({ ...grid, [p.name]: e.target.value })} />}
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              ))}
              <div className="field"><label>Symbols</label><ChipsInput values={symbols} onChange={setSymbols} placeholder="add symbol" /></div>
              <div className="field">
                <label>Data</label>
                <Segmented<Source> value={source} onChange={setSource} options={[
                  { value: "demo", label: "Synthetic" }, { value: "csv", label: "CSV" },
                  ...(eff?.env_only.groww_configured ? [{ value: "groww" as Source, label: "Groww" }] : []),
                ]} />
                {source === "demo" && <span className="subtle">Random walk: good for learning the tools, useless for judging an edge.</span>}
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                <div className="field"><label>From</label><input type="date" className="input" value={start} onChange={(e) => setStart(e.target.value)} /></div>
                <div className="field"><label>To</label><input type="date" className="input" value={end} onChange={(e) => setEnd(e.target.value)} /></div>
              </div>
              {kind === "sweep" && (
                <div className={`note ${combos > 60 ? "down" : ""}`}>
                  {Object.keys(grid).length ? `${combos} combinations (max 60).` : "Tick 'sweep' on 1–3 parameters."} The first 70% of days pick the winner;
                  the last 30% (never seen during selection) show whether it holds up.
                </div>
              )}
              <AnimatePresence>{submitError && <motion.div {...fadeUp} className="banner bad"><CircleAlert size={15} />{submitError}</motion.div>}</AnimatePresence>
              <Button variant="primary" onClick={submit} disabled={submitting || !symbols.length || (kind === "sweep" && (!Object.keys(grid).length || combos > 60))}>
                {submitting ? <LoaderCircle size={15} className="spin" /> : <Play size={15} />}Run {kind === "sweep" ? "sweep" : "backtest"}
              </Button>
            </div>
          </Card>
          <JobHistory selected={jobId} onSelect={setJobId} />
        </div>
        <div className="grid">
          {jobId ? <JobView id={jobId} onApply={apply} /> : (
            <div className="card"><Empty icon={<Sparkles size={28} />} title="Run an experiment"
              hint="Backtests use the exact strategy, risk and cost code the live engine runs. Sweeps test parameter ranges with an out-of-sample check." /></div>
          )}
        </div>
    </div>
  );
}

function JobHistory({ selected, onSelect }: { selected: string | null; onSelect: (id: string) => void }) {
  const { data } = usePoll<Job[]>("/api/jobs", 4000);
  if (!data?.length) return null;
  return (
    <Card title="Recent experiments" icon={<History size={15} />}>
      <div className="list">
        <AnimatePresence initial={false}>
          {data.map((j) => (
            <motion.div key={j.id} layout {...fadeUp} className="row clickable" onClick={() => onSelect(j.id)}
              style={{ boxShadow: selected === j.id ? "inset 0 0 0 1.5px var(--accent)" : "inset 0 0 0 0px transparent" }}>
              <div className="grow">
                <div style={{ fontWeight: 600 }}>{String(j.params.strategy ?? "")} <span className="subtle">{j.kind}</span></div>
                <div className="subtle">{dayTime(j.created_at)} · {String(j.params.data ?? "")}</div>
              </div>
              <StatusBadge job={j} />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </Card>
  );
}

function StatusBadge({ job }: { job: Job }) {
  if (job.status === "done") return <Badge tone="good"><Check size={12} />done</Badge>;
  if (job.status === "error") return <Badge tone="bad">error</Badge>;
  if (job.status === "running") return <Badge tone="blue"><LoaderCircle size={12} className="spin" />{Math.round(Number(job.progress) * 100)}%</Badge>;
  return <Badge>queued</Badge>;
}

function JobView({ id, onApply }: { id: string; onApply: (sp: Record<string, number>) => Promise<void> }) {
  const [interval, setIntervalMs] = useState(1000);
  const { data: job } = usePoll<Job>(`/api/jobs?id=${id}`, interval);
  useEffect(() => setIntervalMs(job && (job.status === "done" || job.status === "error") ? 60_000 : 1000), [job]);
  if (!job) return <div className="card"><Progress value={0.05} /></div>;
  if (job.status === "queued" || job.status === "running") {
    return (
      <Card title={job.status === "queued" ? "Waiting for the worker…" : `Running ${job.kind}…`} icon={<LoaderCircle size={15} className="spin" />}>
        <Progress value={Number(job.progress) || 0.03} />
        <p className="subtle" style={{ marginTop: 10 }}>{job.status === "queued" ? "Jobs run on the worker (`thunderbot serve` or `thunderbot jobs`). If nothing happens, check it's running." : "Same engine code as live trading, on historical bars."}</p>
      </Card>
    );
  }
  if (job.status === "error") return <div className="banner bad"><CircleAlert size={16} /><span className="grow">{job.error}</span></div>;
  return job.kind === "sweep"
    ? <SweepView r={job.result as SweepResult} onApply={onApply} />
    : <BacktestView r={job.result as BacktestResult} onApply={onApply} />;
}

function BacktestView({ r, onApply }: { r: BacktestResult; onApply: (sp: Record<string, number>) => Promise<void> }) {
  const m = r.metrics;
  let cum = 0;
  const curve = r.equity.map((e) => ({ time: e.date, value: (cum += e.pnl) }));
  return (
    <motion.div className="grid" {...fadeUp}>
      {r.data_note && <div className="note">{r.data_note}</div>}
      <div className="stats">
        <Stat label="Net P&L" value={m.net_pnl} format={signedInr} tone="auto" foot={`${inr(m.total_costs as number)} costs`} />
        <Stat label="Trades" value={m.trades} format={(n) => num(n, 0)} foot={`${m.days} days`} />
        <Stat label="Win rate" value={m.win_rate_pct as number} format={(n) => pct(n)} />
        <Stat label="Profit factor" value={m.profit_factor as number | null} format={(n) => num(n)} />
        <Stat label="Max drawdown" value={-(m.max_drawdown_pct as number)} format={(n) => pct(n)} tone="auto" />
        <Stat label="Sharpe" value={m.sharpe_daily_annualized as number | null} format={(n) => num(n)} foot="daily, annualized" />
      </div>
      <Card title="Cumulative P&L" action={<Button size="sm" onClick={() => onApply(r.strategy_params)}><ShieldCheck size={14} />Use these settings</Button>}>
        <PnlCurve points={curve} height={240} label="cumulative" />
      </Card>
      <div className="grid cols-2">
        <Card title="By symbol">
          <div className="table-wrap"><table>
            <thead><tr><th>Symbol</th><th className="num">Trades</th><th className="num">Win rate</th><th className="num">Net</th></tr></thead>
            <tbody>{Object.entries(r.per_symbol).sort(([, a], [, b]) => b.net_pnl - a.net_pnl).map(([s, v]) => (
              <tr key={s}><td>{s}</td><td className="num">{v.trades}</td><td className="num">{pct((v.wins / v.trades) * 100, 0)}</td><td className={`num ${v.net_pnl >= 0 ? "up" : "down"}`}>{signedInr(v.net_pnl)}</td></tr>
            ))}</tbody>
          </table></div>
        </Card>
        <Card title="Exit reasons">
          <div className="list">{Object.entries((m.exit_reasons ?? {}) as Record<string, number>).map(([k, v]) => (
            <div key={k} className="row" style={{ justifyContent: "space-between" }}><span>{k.replaceAll("_", " ")}</span><strong>{v}</strong></div>
          ))}</div>
        </Card>
      </div>
      <Card title={`Last ${Math.min(r.trades.length, 60)} trades`}>
        <div className="table-wrap" style={{ maxHeight: 360, overflowY: "auto" }}><table>
          <thead><tr><th>Closed</th><th>Symbol</th><th>Side</th><th className="num">Qty</th><th className="num">Entry</th><th className="num">Exit</th><th>Reason</th><th className="num">Net</th></tr></thead>
          <tbody>{r.trades.slice(-60).reverse().map((t, i) => (
            <tr key={i}><td>{dayTime(t.closed_at)}</td><td>{t.symbol}</td><td>{t.side}</td><td className="num">{t.qty}</td><td className="num">{num(t.entry)}</td>
              <td className="num">{num(t.exit)}</td><td>{t.reason.replaceAll("_", " ")}</td><td className={`num ${t.net_pnl >= 0 ? "up" : "down"}`}>{signedInr(t.net_pnl)}</td></tr>
          ))}</tbody>
        </table></div>
      </Card>
    </motion.div>
  );
}

function SweepView({ r, onApply }: { r: SweepResult; onApply: (sp: Record<string, number>) => Promise<void> }) {
  const [applied, setApplied] = useState<number | null>(null);
  const [confirming, setConfirming] = useState<number | null>(null);
  const choose = async (i: number, row: SweepRow) => {
    // A configuration that only won in-sample is usually overfit: make that a deliberate choice.
    if (!row.robust && confirming !== i) return setConfirming(i);
    await onApply(row.params);
    setApplied(i);
    setConfirming(null);
  };
  const names = r.axes.map((a) => a.name);
  return (
    <motion.div className="grid" {...fadeUp}>
      <div className="note">
        {r.data_note} Ranked by in-sample net P&L (days before {r.split_date}). Out-of-sample columns are the honest test.{" "}
        {r.robust_count ? <Badge tone="good">{r.robust_count} robust</Badge> : <Badge tone="bad">nothing held up out-of-sample</Badge>}
      </div>
      <Card title="Walk-forward results">
        <div className="table-wrap"><table>
          <thead><tr>
            {names.map((n) => <th key={n} className="num">{n}</th>)}
            <th className="num">In-sample net</th><th className="num">PF</th><th className="num">Trades</th><th className="num">Out-of-sample net</th><th className="num">PF</th><th className="num">Trades</th><th></th><th></th>
          </tr></thead>
          <tbody>
            {r.rows.map((row: SweepRow, i) => (
              <motion.tr key={i} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: Math.min(i * 0.025, 0.6), ...spring }} className={i === 0 ? "best" : ""}>
                {names.map((n) => <td key={n} className="num">{num(row.params[n])}</td>)}
                <td className={`num ${Number(row.in_sample.net_pnl) >= 0 ? "up" : "down"}`}>{signedInr(row.in_sample.net_pnl)}</td>
                <td className="num">{num(row.in_sample.profit_factor)}</td>
                <td className="num">{row.in_sample.trades}</td>
                <td className={`num ${Number(row.out_of_sample.net_pnl) >= 0 ? "up" : "down"}`}>{signedInr(row.out_of_sample.net_pnl)}</td>
                <td className="num">{num(row.out_of_sample.profit_factor)}</td>
                <td className="num">{row.out_of_sample.trades}</td>
                <td>{row.robust ? <Badge tone="good">robust</Badge> : null}</td>
                <td>
                  <Button size="sm" variant={applied === i ? "primary" : confirming === i ? "danger" : ""}
                    title={row.robust ? "Apply to the engine" : "Didn't hold up out-of-sample"} onClick={() => choose(i, row)}>
                    {applied === i ? <><Check size={13} />Applied</> : confirming === i ? "Overfit? Confirm" : "Use"}
                  </Button>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table></div>
      </Card>
    </motion.div>
  );
}
