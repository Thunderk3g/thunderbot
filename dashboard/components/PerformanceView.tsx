"use client";

import { motion } from "motion/react";
import { Bot, ChartLine, Layers } from "lucide-react";
import { useMemo, useState } from "react";
import { inr, num, pct, signedInr } from "@/lib/format";
import { dailySeries, groupBy, reviewerStats, tradeStats } from "@/lib/stats";
import type { Outcome, Trade } from "@/lib/types";
import { usePoll } from "@/lib/usePoll";
import { PnlBars, PnlCurve } from "./charts";
import { Badge, Card, Empty, Segmented, Skeleton, Stat } from "./ui";

type Perf = { mode: string; days: number; trades: Trade[]; outcomes: Outcome[]; anchor: string | null };
type Mode = "paper" | "live" | "replay";

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
    <div className="grid">
      <div style={{ display: "flex", flexWrap: "wrap", gap: 10, alignItems: "center", justifyContent: "space-between" }}>
        <Segmented<Mode> value={mode} onChange={setMode} options={[
          { value: "paper", label: "Paper" }, { value: "live", label: "Live" }, { value: "replay", label: "Replay" },
        ]} />
        <Segmented value={days} onChange={setDays} options={[
          { value: "30", label: "30d" }, { value: "90", label: "90d" }, { value: "365", label: "1y" }, { value: "3650", label: "All" },
        ]} />
      </div>

      {error && <div className="banner bad">{error}</div>}
      {!data ? <div className="card"><Skeleton height={260} /></div> : !data.trades.length ? (
        <div className="card"><Empty icon={<ChartLine size={28} />} title={`No ${mode} trades yet`}
          hint={mode === "live" ? "Live results appear after the engine trades real money." : "Run the engine (or a replay) and results build up here."} /></div>
      ) : (
        <>
          <div className="stats">
            <Stat label="Net P&L" value={stats.net} format={signedInr} tone="auto" foot={`after ${inr(stats.costs)} costs`} />
            <Stat label="Trades" value={stats.trades} format={(n) => num(n, 0)} foot={`${daily.length} days`} />
            <Stat label="Win rate" value={stats.winRate} format={(n) => pct(n)} />
            <Stat label="Profit factor" value={stats.profitFactor} format={(n) => num(n)} foot="gross wins / gross losses" />
            <Stat label="Expectancy" value={stats.expectancy} format={signedInr} tone="auto" foot="per trade" />
            <Stat label="Max drawdown" value={stats.maxDrawdown ? -stats.maxDrawdown : 0} format={signedInr} tone="auto" />
          </div>

          <Card title="Cumulative P&L" icon={<ChartLine size={15} />}
            action={<span className="subtle">{data.anchor ? `through ${data.anchor.slice(0, 10)}` : ""}</span>}>
            <PnlCurve points={daily.map((d) => ({ time: d.day, value: d.equity }))} height={260} label="cumulative" />
          </Card>

          <div className="grid cols-2">
            <Card title="Daily P&L" icon={<ChartLine size={15} />}
              action={<div className="legend"><span><i style={{ background: "var(--series-up)" }} />gain</span><span><i style={{ background: "var(--series-down)" }} />loss</span></div>}>
              <PnlBars points={daily.map((d) => ({ time: d.day, value: d.pnl }))} height={200} />
            </Card>
            <ReviewerCard stats={reviewer} />
          </div>

          <div className="grid cols-2">
            <Breakdown title="By strategy" rows={byStrategy} />
            <Breakdown title="By symbol" rows={bySymbol} />
          </div>
        </>
      )}
    </div>
  );
}

function ReviewerCard({ stats }: { stats: ReturnType<typeof reviewerStats> }) {
  const approve = stats.find((s) => s.decision === "approve");
  const reject = stats.find((s) => s.decision === "reject");
  const enough = (approve?.n ?? 0) >= 30 && (reject?.n ?? 0) >= 15;
  const helping = approve && reject && approve.avgR > reject.avgR;
  const maxAbs = Math.max(0.5, ...stats.map((s) => Math.abs(s.avgR)));
  return (
    <Card title="Is the reviewer earning its keep?" icon={<Bot size={15} />}>
      {!stats.length ? <Empty title="No reviewed signals yet" hint="Every signal is tracked to its stop or target, traded or not, so vetoes can be scored." /> : (
        <>
          <div className="list">
            {stats.map((s, i) => (
              <div key={s.decision} className="row" style={{ display: "grid", gridTemplateColumns: "92px 1fr 70px", gap: 10 }}>
                <span style={{ fontWeight: 600 }}>{s.decision === "none" ? "unreviewed" : s.decision === "approve" ? "approved" : "vetoed"}</span>
                <div style={{ position: "relative", height: 14 }}>
                  <div style={{ position: "absolute", left: "50%", top: 0, bottom: 0, width: 1, background: "var(--axis)" }} />
                  <motion.div initial={{ width: 0 }} animate={{ width: `${(Math.abs(s.avgR) / maxAbs) * 50}%` }} transition={{ delay: i * 0.08, type: "spring", stiffness: 120, damping: 18 }}
                    style={{ position: "absolute", top: 2, height: 10, borderRadius: s.avgR >= 0 ? "0 4px 4px 0" : "4px 0 0 4px",
                      left: s.avgR >= 0 ? "50%" : undefined, right: s.avgR < 0 ? "50%" : undefined,
                      background: s.avgR >= 0 ? "var(--series-up)" : "var(--series-down)" }} />
                </div>
                <span className={s.avgR >= 0 ? "up" : "down"} style={{ textAlign: "right", fontWeight: 600 }}>{s.avgR >= 0 ? "+" : ""}{s.avgR.toFixed(2)}R</span>
                <span className="subtle" style={{ gridColumn: "1 / -1" }}>{s.n} signals · {s.hitRate.toFixed(0)}% ended positive</span>
              </div>
            ))}
          </div>
          <div className="note" style={{ marginTop: 12 }}>
            {!enough ? "Not enough reviewed signals to judge yet (want 30+ approved and 15+ vetoed)."
              : helping ? <>Vetoed signals averaged {reject!.avgR.toFixed(2)}R vs {approve!.avgR.toFixed(2)}R for approved ones, so the reviewer is filtering out worse trades. <Badge tone="good">helping</Badge></>
              : <>Vetoed signals did as well as or better than approved ones. The reviewer isn&apos;t adding value; consider turning it off. <Badge tone="bad">not helping</Badge></>}
          </div>
        </>
      )}
    </Card>
  );
}

function Breakdown({ title, rows }: { title: string; rows: ReturnType<typeof groupBy> }) {
  return (
    <Card title={title} icon={<Layers size={15} />}>
      <div className="table-wrap">
        <table>
          <thead><tr><th>{title.replace("By ", "")}</th><th className="num">Trades</th><th className="num">Win rate</th><th className="num">Net</th></tr></thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.key}><td>{r.key}</td><td className="num">{r.trades}</td><td className="num">{pct(r.winRate, 0)}</td>
                <td className={`num ${r.net >= 0 ? "up" : "down"}`}>{signedInr(r.net)}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}
