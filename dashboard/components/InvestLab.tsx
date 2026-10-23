"use client";

import { motion } from "motion/react";
import { LoaderCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { inr, num, pct } from "@/lib/format";
import type { Control, DailyStrategy, InvestResult } from "@/lib/types";
import { post } from "@/lib/usePoll";
import { GrowthChart } from "./charts";
import { Button, Empty, Figures, Panel, Section, Segmented, SliderField, Switch } from "./ui";

// Shown until the worker publishes its own catalog (the worker clamps every value anyway).
export const FALLBACK_DAILY: DailyStrategy[] = [
  { name: "index_trend", label: "Nifty trend (ETF or cash)", description: "Holds the Nifty 50 ETF while the Nifty is above its 200-day average, cash below it.",
    params: [
      { name: "sma_days", label: "Average length (days)", type: "int", min: 50, max: 300, step: 10, default: 200 },
      { name: "buffer_pct", label: "Buffer around the average %", type: "float", min: 0, max: 5, step: 0.5, default: 1 },
    ] },
  { name: "momentum", label: "Momentum top stocks", description: "Every quarter, picks the Nifty 100 stocks with the strongest 6- and 12-month risk-adjusted returns; checks the market monthly.",
    params: [
      { name: "top_n", label: "Stocks held", type: "int", min: 5, max: 30, step: 1, default: 15 },
      { name: "keep_rank", label: "Keep while ranked in top", type: "int", min: 5, max: 50, step: 1, default: 25 },
      { name: "rank_months", label: "Re-rank every N months (1, 3 or 6)", type: "int", min: 1, max: 6, step: 1, default: 3 },
      { name: "trend_filter", label: "Market filter (1 = on)", type: "int", min: 0, max: 1, step: 1, default: 1 },
    ] },
];

const tone = (n: number) => (n > 0 ? "gain" : n < 0 ? "loss" : "") as "" | "gain" | "loss";

export function defaultsOf(s?: DailyStrategy): Record<string, number> {
  return Object.fromEntries((s?.params ?? []).map((p) => [p.name, p.default]));
}

export default function InvestLab({ control, onJob }: { control?: Control; onJob: (id: string) => void }) {
  const catalog = control?.daily_catalog?.length ? control.daily_catalog : FALLBACK_DAILY;
  const [name, setName] = useState(control?.invest_settings?.strategy ?? "index_trend");
  const info = catalog.find((s) => s.name === name) ?? catalog[0];
  const [params, setParams] = useState<Record<string, number>>(() => ({ ...defaultsOf(info), ...(control?.invest_settings?.params ?? {}) }));
  const [years, setYears] = useState(15);
  const [capital, setCapital] = useState(500_000);
  const [tax, setTax] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => setParams((p) => ({ ...defaultsOf(info), ...p })), [info]);

  const run = async () => {
    setBusy(true);
    setError(null);
    try {
      const { id } = await post<{ id: string }>("/api/jobs", { kind: "invest", params: { strategy: name, strategy_params: params, years, capital, tax } });
      onJob(id);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <Panel>
      <div className="form">
        <div className="field">
          <label htmlFor="inv-strategy">Strategy</label>
          <select id="inv-strategy" className="input" value={name} onChange={(e) => { setName(e.target.value); setParams(defaultsOf(catalog.find((s) => s.name === e.target.value))); }}>
            {catalog.map((s) => <option key={s.name} value={s.name}>{s.label}</option>)}
          </select>
          <span className="hint">{info?.description}</span>
        </div>
        {info?.params.map((p) => (
          <SliderField key={p.name} label={p.label} min={p.min} max={p.max} step={p.step} value={params[p.name] ?? p.default}
            onChange={(v) => setParams({ ...params, [p.name]: v })} />
        ))}
        <SliderField label="Years of history" min={3} max={18} step={1} value={years} onChange={setYears} hint="Daily prices from Yahoo Finance" />
        <div className="field">
          <label htmlFor="inv-cap">Starting money</label>
          <input id="inv-cap" className="input tnum" inputMode="numeric" value={capital} onChange={(e) => setCapital(Number(e.target.value.replace(/[^\d]/g, "")) || 0)} />
        </div>
        <div className="toggle-row"><span className="field-label">Subtract capital-gains tax</span><Switch checked={tax} onChange={setTax} label="Subtract tax" /></div>
        {error && <div className="notice stop"><span className="grow">{error}</span></div>}
        <Button variant="primary" block onClick={run} disabled={busy || capital < 10_000}>
          {busy && <LoaderCircle size={15} className="spin" />}Test {years} years
        </Button>
      </div>
    </Panel>
  );
}

export function InvestResultView({ r, onUse }: { r: InvestResult; onUse?: () => Promise<void> }) {
  const m = r.metrics;
  const b = m.benchmark;
  const [used, setUsed] = useState(false);
  const label = (FALLBACK_DAILY.find((s) => s.name === r.strategy)?.label ?? r.strategy).split(" (")[0];
  return (
    <motion.div className="page" style={{ gap: 32 }} initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div>
        <p className="hero-line" style={{ marginTop: 0, fontSize: 21, color: "var(--ink)" }}>
          {inr(r.capital)} would have become <strong className={tone(m.final_value - r.capital)}>{inr(m.final_value)}</strong> in {num(m.years, 1)} years
          ({pct(m.cagr_pct)} a year{m.taxes > 0 ? " after costs and tax" : " after costs"}). Holding the Nifty ETF: {inr(b.final_value)} ({pct(b.cagr_pct)} a year, before tax).
        </p>
        <p className="small soft" style={{ marginTop: 6, maxWidth: "75ch" }}>{r.data_note}</p>
        <div style={{ marginTop: 20 }}>
          <Figures items={[
            { label: "Worst fall", value: pct(m.max_drawdown_pct), tone: "loss" },
            { label: "Worst fall, Nifty ETF", value: pct(b.max_drawdown_pct), tone: "loss" },
            { label: "Time invested", value: pct(m.time_invested_pct, 0) },
            { label: "Trades", value: num(m.trades, 0) },
            { label: "Costs + tax", value: inr(m.costs + m.taxes) },
          ]} />
        </div>
      </div>
      <Section title="Growth" aside={<div className="legend"><span><i style={{ background: "var(--gain)" }} />{label}</span><span><i style={{ background: "var(--ink-soft)" }} />Nifty ETF</span></div>}>
        <GrowthChart points={r.equity.map((e) => ({ time: e.date, value: e.value, benchmark: e.benchmark }))} label={label} />
      </Section>
      <Section title="Each year" aside={onUse ? <Button size="sm" variant={used ? "primary" : ""} onClick={async () => { await onUse(); setUsed(true); }}>{used ? "In use" : "Use this strategy"}</Button> : undefined}>
        <div className="table-wrap"><table>
          <thead><tr><th>Year</th><th className="num">{label}</th><th className="num">Nifty ETF</th><th className="num">Difference</th></tr></thead>
          <tbody>{[...r.yearly].reverse().map((y) => (
            <tr key={y.year}><td className="tnum">{y.year}</td>
              <td className={`num ${tone(y.strategy_pct)}`}>{pct(y.strategy_pct)}</td>
              <td className={`num ${tone(y.benchmark_pct ?? 0)}`}>{y.benchmark_pct === null ? "–" : pct(y.benchmark_pct)}</td>
              <td className={`num ${tone(y.strategy_pct - (y.benchmark_pct ?? 0))}`}>{y.benchmark_pct === null ? "–" : `${y.strategy_pct - y.benchmark_pct > 0 ? "+" : ""}${(y.strategy_pct - y.benchmark_pct).toFixed(1)}`}</td></tr>
          ))}</tbody>
        </table></div>
      </Section>
    </motion.div>
  );
}

export function ModeSwitch({ value, onChange }: { value: "invest" | "intraday"; onChange: (v: "invest" | "intraday") => void }) {
  return <Segmented<"invest" | "intraday"> label="Strategy type" value={value} onChange={onChange}
    options={[{ value: "invest", label: "Invest (daily)" }, { value: "intraday", label: "Intraday" }]} />;
}

export function NoResult() {
  return <Empty title="Results appear here.">Test a daily strategy over many years of real NSE prices. The result shows what your money would have become after costs and tax, next to simply holding the Nifty ETF.</Empty>;
}
