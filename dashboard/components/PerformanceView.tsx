"use client";

import { motion } from "motion/react";
import { useMemo, useState } from "react";
import { inr, num, pct, signedInr } from "@/lib/format";
import { dailySeries, groupBy, reviewerStats, tradeStats } from "@/lib/stats";
import type { Outcome, Trade } from "@/lib/types";
import { usePoll } from "@/lib/usePoll";
import { PnlBars, PnlCurve } from "./charts";
import { Empty, Figures, Section, Segmented, Skeleton } from "./ui";

type Perf = { mode: string; days: number; trades: Trade[]; outcomes: Outcome[]; anchor: string | null };
type Mode = "paper" | "live" | "replay";
const MODE_NOUN: Record<Mode, string> = { paper: "Paper trading", live: "Live trading", replay: "Replays" };
const tone = (n: number | null | undefined) => (!n ? "" : n > 0 ? "gain" : "loss") as "" | "gain" | "loss";

export default function PerformanceView({ defaultMode }: { defaultMode: Mode }) {
  const [mode, setMode] = useState<Mode>(defaultMode);
  const [days, setDays] = useState("90");
  const { data, error } = usePoll<Perf>(`/api/performance?mode=${mode}&days=${days}`, 10_000);

  const stats = useMemo(() => tradeStats(data?.trades ?? []), [data]);
  const daily = useMemo(() => dailySeries(data?.trades ?? []), [data]);
  const reviewer = useMemo(() => reviewerStats(data?.outcomes ?? []), [data]);
  const byStrategy = useMemo(() => groupBy(data?.trades ?? [], "strategy"), [data]);
  const bySymbol = useMemo(() => groupBy(data?.trades ?? [], "symbol"), [data]);

  return (
    <div className="page">
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12, alignItems: "center", justifyContent: "space-between" }}>
        <h1>Results</h1>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <Segmented<Mode> label="Trading mode" value={mode} onChange={setMode} options={[
            { value: "paper", label: "Paper" }, { value: "live", label: "Live" }, { value: "replay", label: "Replay" },
          ]} />
          <Segmented label="Period" value={days} onChange={setDays} options={[
            { value: "30", label: "30 days" }, { value: "90", label: "90 days" }, { value: "365", label: "1 year" }, { value: "3650", label: "All" },
          ]} />
        </div>
      </div>

      {error && <div className="notice stop"><span className="grow">{error}</span></div>}
      {!data ? <Skeleton height={300} /> : !data.trades.length ? (
        <Empty title={`No ${mode} trades yet.`}>
          {mode === "live" ? "Live results appear once the engine trades real money." : "Run the engine or a replay and results build up here."}
        </Empty>
      ) : (
        <>
          <section>
            <p className="hero-line" style={{ marginTop: 0, fontSize: 22, color: "var(--ink)", maxWidth: "48ch" }}>
              {MODE_NOUN[mode]} {stats.net >= 0 ? "made" : "lost"} <strong className={tone(stats.net)}>{inr(Math.abs(stats.net))}</strong> over{" "}
              {daily.length} trading {daily.length === 1 ? "day" : "days"}, after {inr(stats.costs)} in costs.
            </p>
            <div style={{ marginTop: 24 }}>
              <Figures items={[
                { label: "Trades", value: num(stats.trades, 0) },
                { label: "Won", value: pct(stats.winRate, 0) },
                { label: "Profit factor", value: num(stats.profitFactor) },
                { label: "Average trade", value: signedInr(stats.expectancy), tone: tone(stats.expectancy) },
                { label: "Worst drawdown", value: stats.maxDrawdown ? signedInr(-stats.maxDrawdown) : "none", tone: stats.maxDrawdown ? "loss" : "" },
              ]} />
            </div>
          </section>

          <Section title="Running total" aside={<p>Net P&amp;L by day{data.anchor ? `, through ${data.anchor.slice(0, 10)}` : ""}</p>}>
            <PnlCurve points={daily.map((d) => ({ time: d.day, value: d.equity }))} height={260} label="total" />
          </Section>

          <div className="split even">
            <Section title="Each day" aside={<div className="legend"><span><i style={{ background: "var(--gain)" }} />gain</span><span><i style={{ background: "var(--loss)" }} />loss</span></div>}>
              <PnlBars points={daily.map((d) => ({ time: d.day, value: d.pnl }))} height={200} />
            </Section>
            <ReviewerSection stats={reviewer} />
          </div>

          <div className="split even">
            <Breakdown title="By strategy" rows={byStrategy} />
            <Breakdown title="By stock" rows={bySymbol} ticker />
          </div>
        </>
      )}
    </div>
  );
}

function ReviewerSection({ stats }: { stats: ReturnType<typeof reviewerStats> }) {
  const approve = stats.find((s) => s.decision === "approve");
  const reject = stats.find((s) => s.decision === "reject");
  const enough = (approve?.n ?? 0) >= 30 && (reject?.n ?? 0) >= 15;
  const helping = !!approve && !!reject && approve.avgR > reject.avgR;
  const maxAbs = Math.max(0.5, ...stats.map((s) => Math.abs(s.avgR)));
  const name: Record<string, string> = { approve: "Approved", reject: "Vetoed", none: "Not reviewed" };
  return (
    <Section title="Is the reviewer worth it?" aside={<p>Average result per idea, in multiples of risk</p>}>
      {!stats.length ? <Empty title="Nothing to compare yet.">Every signal is followed to its stop or target, traded or not, so vetoes can be judged.</Empty> : (
        <>
          <div className="compare">
            {stats.map((s, i) => (
              <div key={s.decision} style={{ display: "contents" }}>
                <span>{name[s.decision]}</span>
                <span className="bar">
                  <span className="axis" />
                  <motion.span initial={{ width: 0 }} animate={{ width: `${(Math.abs(s.avgR) / maxAbs) * 50}%` }} transition={{ delay: i * 0.06, type: "spring", stiffness: 120, damping: 20 }}
                    style={{ position: "absolute", top: 0, height: 10, left: s.avgR >= 0 ? "50%" : undefined, right: s.avgR < 0 ? "50%" : undefined,
                      borderRadius: s.avgR >= 0 ? "0 3px 3px 0" : "3px 0 0 3px", background: s.avgR >= 0 ? "var(--gain)" : "var(--loss)" }} />
                </span>
                <span className={`tnum ${s.avgR >= 0 ? "gain" : "loss"}`} style={{ textAlign: "right", fontWeight: 600 }}>{Math.abs(s.avgR) < 0.005 ? "0.00" : `${s.avgR > 0 ? "+" : ""}${s.avgR.toFixed(2)}`}R</span>
                <span className="soft small" style={{ gridColumn: "2 / -1", marginTop: -4, marginBottom: 6 }}>{s.n} ideas, {s.hitRate.toFixed(0)}% ended in profit</span>
              </div>
            ))}
          </div>
          <p className="small" style={{ marginTop: 12, maxWidth: "60ch" }}>
            {!enough ? "Too few reviewed ideas to judge yet. Wait for 30 approved and 15 vetoed."
              : helping ? `Yes, so far. Vetoed ideas averaged ${reject!.avgR.toFixed(2)}R against ${approve!.avgR.toFixed(2)}R for approved ones.`
              : "No. Vetoed ideas did as well as approved ones, so the reviewer is costing money without filtering anything. Consider turning it off in Settings."}
          </p>
        </>
      )}
    </Section>
  );
}

function Breakdown({ title, rows, ticker }: { title: string; rows: ReturnType<typeof groupBy>; ticker?: boolean }) {
  return (
    <Section title={title}>
      <div className="table-wrap">
        <table>
          <thead><tr><th>{ticker ? "Stock" : "Strategy"}</th><th className="num">Trades</th><th className="num">Won</th><th className="num">Net</th></tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.key}><td className={ticker ? "ticker" : ""}>{r.key}</td><td className="num">{r.trades}</td><td className="num">{pct(r.winRate, 0)}</td>
                <td className={`num ${r.net >= 0 ? "gain" : "loss"}`}>{signedInr(r.net)}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </Section>
  );
}
