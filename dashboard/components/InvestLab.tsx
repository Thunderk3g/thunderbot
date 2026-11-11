"use client";

import { motion } from "motion/react";
import { LoaderCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { asset, type AssetKind } from "@/lib/assets";
import { inr, num, pct } from "@/lib/format";
import type { Control, DailyStrategy, InvestResult } from "@/lib/types";
import { startJob } from "@/lib/usePoll";
import { GrowthChart } from "./charts";
import { Button, Empty, Figures, Section, Segmented, SliderField, Switch } from "./ui";

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

/** How each plan is introduced: a short name, one line, what it holds, how often it trades. */
const PLAN: Record<string, { name: string; line: string; holds: AssetKind[]; trades: string; caution?: string }> = {
  core_mix: { name: "Steady mix", line: "Hold three ETFs in fixed shares. Rebalance once a year. No timing.", holds: ["nifty", "next50", "gold"], trades: "about 4 trades a year" },
  etf_trend: { name: "Trend rotation", line: "Hold each ETF only while it is rising; park the rest in a liquid ETF.", holds: ["nifty", "next50", "gold", "parked"], trades: "about 17 trades a year" },
  etf_rank: { name: "Strongest ETFs", line: "Hold the two ETFs with the best recent returns, if they beat cash.", holds: ["nifty", "next50", "gold", "parked"], trades: "about 14 trades a year" },
  index_trend: { name: "Nifty trend", line: "Hold the Nifty 50 ETF while the Nifty is rising; a liquid ETF otherwise.", holds: ["nifty", "parked"], trades: "about 4 trades a year" },
  momentum: { name: "Momentum stocks", line: "Pick the 15 strongest Nifty 100 stocks each quarter.", holds: ["mid", "parked"], trades: "dozens of trades a year", caution: "Biased test" },
};
export const planName = (name: string) => PLAN[name]?.name ?? name;

const tone = (n: number) => (n > 0 ? "gain" : n < 0 ? "loss" : "") as "" | "gain" | "loss";

export function defaultsOf(s?: DailyStrategy): Record<string, number> {
  return Object.fromEntries((s?.params ?? []).map((p) => [p.name, p.default]));
}

export default function InvestLab({ control, onJob }: { control?: Control; onJob: (id: string) => void }) {
  const catalog = control?.daily_catalog?.length ? control.daily_catalog : FALLBACK_DAILY;
  const inUse = control?.invest_settings?.strategy ?? control?.heartbeat?.strategy;
  const [name, setName] = useState(control?.invest_settings?.strategy ?? catalog[0].name);
  const info = catalog.find((s) => s.name === name) ?? catalog[0];
  const [params, setParams] = useState<Record<string, number>>(() => ({ ...defaultsOf(info), ...(control?.invest_settings?.params ?? {}) }));
  const [years, setYears] = useState(15);
  const [capital, setCapital] = useState(control?.heartbeat?.capital ?? 500_000);
  const [tax, setTax] = useState(true);
  const [slab, setSlab] = useState(control?.effective_settings?.env_only.slab_rate_pct ?? 30);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => setParams((p) => ({ ...defaultsOf(info), ...p })), [info]);

  const pick = (n: string) => {
    setName(n);
    setParams(defaultsOf(catalog.find((s) => s.name === n)));
  };
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
    <div className="form">
      <div className="plans" role="radiogroup" aria-label="Plan">
        {catalog.map((s) => {
          const meta = PLAN[s.name];
          const on = s.name === name;
          return (
            <button key={s.name} type="button" role="radio" aria-checked={on} className="plan" onClick={() => pick(s.name)}>
              <span className="plan-name">
                <span>{meta?.name ?? s.label}</span>
                <span style={{ display: "inline-flex", gap: 8, alignItems: "center" }}>
                  {inUse === s.name && <span className="tag use">In use</span>}
                  {meta?.caution && <span className="tag warn">{meta.caution}</span>}
                  <span className="radio" aria-hidden />
                </span>
              </span>
              <p>{on ? s.description : meta?.line ?? s.description}</p>
              {meta && (
                <span className="plan-meta">
                  <span className="swatches" aria-hidden>{meta.holds.map((k) => <i key={k} className={`swatch ${k}`} />)}</span>
                  <span>{meta.trades}</span>
                </span>
              )}
            </button>
          );
        })}
      </div>

      <details className="fine">
        <summary>Fine-tune {PLAN[name]?.name ?? "the plan"} and the test</summary>
        <div className="form">
          {info?.params.map((p) => (
            <SliderField key={p.name} label={p.label} min={p.min} max={p.max} step={p.step} value={params[p.name] ?? p.default}
              onChange={(v) => setParams({ ...params, [p.name]: v })} />
          ))}
          <SliderField label="Years of history" min={3} max={17} step={1} value={years} onChange={setYears} hint="The ETFs' prices start in 2009" />
          <div className="field">
            <label htmlFor="inv-cap">Starting money</label>
            <input id="inv-cap" className="input tnum" inputMode="numeric" value={capital} onChange={(e) => setCapital(Number(e.target.value.replace(/[^\d]/g, "")) || 0)} />
          </div>
          <div className="toggle-row"><span className="field-label">Subtract capital-gains tax</span><Switch checked={tax} onChange={setTax} label="Subtract tax" /></div>
          {tax && <SliderField label="Your income-tax slab %" min={0} max={40} step={5} value={slab} onChange={setSlab} hint="For liquid ETF gains and gold sold within a year" />}
        </div>
      </details>

      {error && <div className="notice stop"><span className="grow">{error}</span></div>}
      <Button variant="primary" size="lg" block onClick={run} disabled={busy || capital < 10_000}>
        {busy && <LoaderCircle size={16} className="spin" />}Test {PLAN[name]?.name ?? "it"} on {years} years
      </Button>
    </div>
  );
}

export function InvestResultView({ r, onUse, inUse }: { r: InvestResult; onUse?: () => Promise<void>; inUse?: boolean }) {
  const m = r.metrics;
  const b = m.benchmark;
  const [used, setUsed] = useState(false);
  const label = planName(r.strategy);
  const taxed = m.taxes > 0 || (m.exit_tax ?? 0) > 0;
  const rows = [
    { label, cagr: m.cagr_pct, exit: m.cagr_after_exit_tax_pct, fall: m.max_drawdown_pct, value: m.final_value, own: true },
    ...(r.comparators ?? []).map((c) => ({ label: c.label, cagr: c.cagr_pct, exit: c.cagr_after_exit_tax_pct, fall: c.max_drawdown_pct, value: c.final_value, own: false })),
    { label: "Nifty 50 ETF, bought and held", cagr: b.cagr_pct, exit: b.cagr_after_exit_tax_pct, fall: b.max_drawdown_pct, value: b.final_value, own: false },
  ];
  const rate = (x: (typeof rows)[number]) => x.exit ?? x.cagr;
  const best = Math.max(...rows.map(rate), 1);
  const beaten = rows.slice(1).filter((x) => rate(x) > rate(rows[0]));
  const deepest = Math.min(...beaten.map((x) => x.fall), 0);
  return (
    <motion.div className="page" style={{ gap: 40 }} initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div>
        <h2 style={{ fontSize: "clamp(24px, 3vw, 34px)", lineHeight: 1.15, letterSpacing: "-0.025em", fontVariationSettings: '"wdth" 88, "opsz" 48', maxWidth: "24ch" }}>
          {inr(r.capital)} would have become <span className={tone(m.final_value - r.capital)}>{inr(m.final_value)}</span> in {num(m.years, 0)} years.
        </h2>
        <p className="lede">
          That is {pct(m.cagr_pct)} a year{taxed ? " after costs and tax" : " after costs"}, with a worst fall of {pct(Math.abs(m.max_drawdown_pct))} along the way.
        </p>
        {beaten.length > 0 && (
          <div className="notice caution" style={{ marginTop: 16 }}>
            <span className="grow">
              {label} earned less than {beaten.map((x) => `“${x.label}”`).join(" and ")}.{" "}
              {m.max_drawdown_pct > deepest
                ? <>What it gave in return was a smaller worst fall: {pct(Math.abs(m.max_drawdown_pct))} against {pct(Math.abs(deepest))}.</>
                : <>Its worst fall was no smaller either.</>}
            </span>
          </div>
        )}
        {onUse && (
          <div style={{ marginTop: 20, display: "flex", gap: 12, alignItems: "center", flexWrap: "wrap" }}>
            <Button variant="primary" size="lg" disabled={used || inUse} onClick={async () => { await onUse(); setUsed(true); }}>
              {used || inUse ? `${label} is in use` : `Use ${label}`}
            </Button>
            <span className="small soft">The bot switches at its next daily check. Nothing trades before then.</span>
          </div>
        )}
      </div>

      <Section title="Against doing less" aside={<p>A year, if sold and taxed today</p>}>
        <div className="versus">
          {rows.map((x) => (
            <div key={x.label} className={`versus-row ${x.own ? "own" : ""}`}>
              <div className="who"><b>{x.label}</b><span>{pct(rate(x))} a year, ends at {inr(x.value)}</span></div>
              <div className="versus-track"><motion.div initial={{ width: 0 }} animate={{ width: `${Math.max(2, (rate(x) / best) * 100)}%` }} transition={{ type: "spring", stiffness: 120, damping: 22 }} /></div>
              <div className="versus-fall">Worst fall {pct(Math.abs(x.fall))}</div>
            </div>
          ))}
        </div>
        {r.allocation && Object.keys(r.allocation).length > 0 && (
          <p className="small soft" style={{ marginTop: 16 }}>
            On average the money sat in: {Object.entries(r.allocation).map(([s, w]) => `${asset(s).name} ${w.toFixed(0)}%`).join(", ")}.
          </p>
        )}
      </Section>

      <Section title="How it grew" aside={<div className="legend"><span><i style={{ background: "var(--ink)" }} />{label}</span><span><i style={{ background: "var(--ink-soft)", opacity: 0.6 }} />Nifty 50 ETF (dashed)</span></div>}>
        <GrowthChart points={r.equity.map((e) => ({ time: e.date, value: e.value, benchmark: e.benchmark }))} label={label} />
      </Section>

      <Section title="The details">
        <Figures items={[
          { label: "Longest wait for a new high", value: `${num(m.longest_underwater_days / 365, 1)} yrs` },
          { label: "Trades", value: num(m.trades, 0) },
          { label: "Costs paid", value: inr(m.costs) },
          { label: "Tax paid", value: inr(m.taxes) },
          { label: "Worst fall, Nifty ETF", value: pct(Math.abs(b.max_drawdown_pct)) },
        ]} />
        <p className="small soft" style={{ marginTop: 16, maxWidth: "78ch" }}>{r.data_note}</p>
      </Section>

      <Section title="Each year">
        <div className="table-wrap"><table>
          <thead><tr><th>Year</th><th className="num">{label}</th><th className="num">Nifty 50 ETF</th><th className="num">Difference</th></tr></thead>
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
  return <Segmented<"invest" | "intraday"> label="What to test" value={value} onChange={onChange}
    options={[{ value: "invest", label: "Investing plans" }, { value: "intraday", label: "Intraday research" }]} />;
}

export function NoResult() {
  return (
    <Empty title="Pick a plan and test it.">
      You will see what your money would have become over the years, after costs and tax, next to simply holding the Nifty 50 ETF and
      next to holding the same ETFs with no timing at all.
    </Empty>
  );
}
