"use client";

import { motion } from "motion/react";
import { LoaderCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { inr, num, pct } from "@/lib/format";
import type { Control, DailyStrategy, InvestResult } from "@/lib/types";
import { startJob } from "@/lib/usePoll";
import { GrowthChart } from "./charts";
import { Button, Empty, Figures, Panel, Section, Segmented, SliderField, Switch } from "./ui";

// Shown until the worker publishes its own catalog (the worker clamps every value anyway).
const onOff = { type: "int" as const, min: 0, max: 1, step: 1 };
export const FALLBACK_DAILY: DailyStrategy[] = [
  { name: "core_mix", label: "Steady mix (Nifty 50, Next 50, gold)", description: "Holds NIFTYBEES, JUNIORBEES and GOLDBEES in fixed shares and rebalances once a year. No market timing.",
    params: [
      { name: "gold_pct", label: "Gold share %", type: "int", min: 0, max: 50, step: 1, default: 33 },
      { name: "next50_pct", label: "Next 50 share of the equity part %", type: "int", min: 0, max: 100, step: 10, default: 50 },
    ] },
  { name: "etf_trend", label: "Trend rotation (ETFs or liquid fund)", description: "Holds each ETF only while its price is above its 200-day average; a share that is out waits in a liquid ETF.",
    params: [
      { name: "sma_days", label: "Average length (days)", type: "int", min: 100, max: 300, step: 10, default: 200 },
      { name: "gold", label: "Include gold (1 = yes)", ...onOff, default: 1 },
      { name: "midcap", label: "Include midcaps (1 = yes)", ...onOff, default: 0 },
    ] },
  { name: "etf_rank", label: "Strongest ETFs (dual momentum)", description: "Holds the ETFs with the best 3-, 6- and 12-month returns that also beat the liquid ETF.",
    params: [
      { name: "top_n", label: "ETFs held", type: "int", min: 1, max: 3, step: 1, default: 2 },
      { name: "gold", label: "Include gold (1 = yes)", ...onOff, default: 1 },
      { name: "midcap", label: "Include midcaps (1 = yes)", ...onOff, default: 0 },
    ] },
  { name: "index_trend", label: "Nifty trend (ETF or liquid fund)", description: "Holds the Nifty 50 ETF while the Nifty is above its 200-day average, a liquid ETF below it.",
    params: [
      { name: "sma_days", label: "Average length (days)", type: "int", min: 50, max: 300, step: 10, default: 200 },
      { name: "buffer_pct", label: "Buffer around the average %", type: "float", min: 0, max: 5, step: 0.5, default: 1 },
      { name: "liquid", label: "Park in a liquid ETF (1 = yes)", ...onOff, default: 1 },
    ] },
  { name: "momentum", label: "Momentum top stocks (biased backtest)", description: "Every quarter, picks the Nifty 100 stocks with the strongest 6- and 12-month risk-adjusted returns. Its backtest is inflated by survivorship bias.",
    params: [
      { name: "top_n", label: "Stocks held", type: "int", min: 5, max: 30, step: 1, default: 15 },
      { name: "keep_rank", label: "Keep while ranked in top", type: "int", min: 5, max: 50, step: 1, default: 25 },
      { name: "rank_months", label: "Re-rank every N months (1, 3 or 6)", type: "int", min: 1, max: 6, step: 1, default: 3 },
      { name: "trend_filter", label: "Market filter (1 = on)", ...onOff, default: 1 },
    ] },
];

const ASSET_NAME: Record<string, string> = {
  NIFTYBEES: "Nifty 50 ETF", JUNIORBEES: "Next 50 ETF", GOLDBEES: "Gold ETF", MOM100: "Midcap 100 ETF", LIQUID: "Liquid ETF", CASH: "Cash",
};

const tone = (n: number) => (n > 0 ? "gain" : n < 0 ? "loss" : "") as "" | "gain" | "loss";

export function defaultsOf(s?: DailyStrategy): Record<string, number> {
  return Object.fromEntries((s?.params ?? []).map((p) => [p.name, p.default]));
}

export default function InvestLab({ control, onJob }: { control?: Control; onJob: (id: string) => void }) {
  const catalog = control?.daily_catalog?.length ? control.daily_catalog : FALLBACK_DAILY;
  const [name, setName] = useState(control?.invest_settings?.strategy ?? catalog[0].name);
  const info = catalog.find((s) => s.name === name) ?? catalog[0];
  const [params, setParams] = useState<Record<string, number>>(() => ({ ...defaultsOf(info), ...(control?.invest_settings?.params ?? {}) }));
  const [years, setYears] = useState(15);
  const [capital, setCapital] = useState(500_000);
  const [tax, setTax] = useState(true);
  const [slab, setSlab] = useState(control?.effective_settings?.env_only.slab_rate_pct ?? 30);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => setParams((p) => ({ ...defaultsOf(info), ...p })), [info]);

  const run = async () => {
    setBusy(true);
    setError(null);
    try {
      onJob(await startJob("invest", { strategy: name, strategy_params: params, years, capital, tax, slab_rate_pct: slab }));
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
        <SliderField label="Years of history" min={3} max={17} step={1} value={years} onChange={setYears} hint="Daily prices from Yahoo Finance; the ETFs' history starts in 2009" />
        <div className="field">
          <label htmlFor="inv-cap">Starting money</label>
          <input id="inv-cap" className="input tnum" inputMode="numeric" value={capital} onChange={(e) => setCapital(Number(e.target.value.replace(/[^\d]/g, "")) || 0)} />
        </div>
        <div className="toggle-row"><span className="field-label">Subtract capital-gains tax</span><Switch checked={tax} onChange={setTax} label="Subtract tax" /></div>
        {tax && <SliderField label="Your income-tax slab %" min={0} max={40} step={5} value={slab} onChange={setSlab} hint="Applies to liquid ETF gains and to gold ETFs sold within 12 months" />}
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
  const taxed = m.taxes > 0 || (m.exit_tax ?? 0) > 0;
  const rows = [
    { label, cagr: m.cagr_pct, exit: m.cagr_after_exit_tax_pct, fall: m.max_drawdown_pct, value: m.final_value, own: true },
    ...(r.comparators ?? []).map((c) => ({ label: c.label, cagr: c.cagr_pct, exit: c.cagr_after_exit_tax_pct, fall: c.max_drawdown_pct, value: c.final_value, own: false })),
    { label: "Nifty 50 ETF, bought and held", cagr: b.cagr_pct, exit: b.cagr_after_exit_tax_pct, fall: b.max_drawdown_pct, value: b.final_value, own: false },
  ];
  const beaten = rows.slice(1).filter((x) => (x.exit ?? x.cagr) > (m.cagr_after_exit_tax_pct ?? m.cagr_pct));
  const deepest = Math.min(...beaten.map((x) => x.fall), 0);
  return (
    <motion.div className="page" style={{ gap: 32 }} initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div>
        <p className="hero-line" style={{ marginTop: 0, fontSize: 21, color: "var(--ink)" }}>
          {inr(r.capital)} would have become <strong className={tone(m.final_value - r.capital)}>{inr(m.final_value)}</strong> in {num(m.years, 1)} years
          ({pct(m.cagr_pct)} a year{taxed ? " after costs and tax" : " after costs"}). Holding the Nifty ETF: {inr(b.final_value)} ({pct(b.cagr_pct)} a year, before tax).
        </p>
        {beaten.length > 0 && (
          <div className="notice caution" style={{ marginTop: 14 }}>
            <span className="grow">
              Over these years this rule earned less than {beaten.map((x) => `“${x.label}”`).join(" and ")}.{" "}
              {m.max_drawdown_pct > deepest
                ? <>What it gave in return was a smaller worst fall: {pct(m.max_drawdown_pct)} against {pct(deepest)}.</>
                : <>Its worst fall was no smaller either.</>}
            </span>
          </div>
        )}
        <p className="small soft" style={{ marginTop: 10, maxWidth: "75ch" }}>{r.data_note}</p>
        <div style={{ marginTop: 20 }}>
          <Figures items={[
            { label: "Worst fall", value: pct(m.max_drawdown_pct), tone: "loss" },
            { label: "Worst fall, Nifty ETF", value: pct(b.max_drawdown_pct), tone: "loss" },
            { label: "Longest wait for a new high", value: `${num(m.longest_underwater_days / 365, 1)} yrs` },
            { label: "Trades", value: num(m.trades, 0) },
            { label: "Costs + tax", value: inr(m.costs + m.taxes) },
          ]} />
        </div>
      </div>
      <Section title="Against doing less">
        <div className="table-wrap"><table>
          <thead><tr><th>What you held</th><th className="num">A year</th><th className="num">If sold and taxed today</th><th className="num">Worst fall</th><th className="num">Ends at</th></tr></thead>
          <tbody>{rows.map((x) => (
            <tr key={x.label} style={x.own ? { fontWeight: 600 } : undefined}><td>{x.label}</td>
              <td className={`num ${tone(x.cagr)}`}>{pct(x.cagr)}</td>
              <td className={`num ${tone(x.exit ?? 0)}`}>{x.exit == null ? "–" : pct(x.exit)}</td>
              <td className="num loss">{pct(x.fall)}</td><td className="num">{inr(x.value)}</td></tr>
          ))}</tbody>
        </table></div>
        {r.allocation && Object.keys(r.allocation).length > 0 && (
          <p className="small soft" style={{ marginTop: 12 }}>
            Money was held, on average: {Object.entries(r.allocation).map(([s, w]) => `${ASSET_NAME[s] ?? s} ${w.toFixed(0)}%`).join(", ")}.
          </p>
        )}
      </Section>
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
  return <Empty title="Results appear here.">Test a daily strategy over many years of real NSE prices. The result shows what your money would have become after costs and tax, next to simply holding the Nifty ETF and next to holding the same ETFs without any timing.</Empty>;
}
