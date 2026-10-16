"use client";

import { motion, useReducedMotion } from "motion/react";
import { useEffect, useId, useMemo, useRef, useState } from "react";
import { signedInr } from "@/lib/format";

const OPEN = 9 * 60 + 15;
const CLOSE = 15 * 60 + 30;

type Pt = { at: string; value: number };
type TradeMark = { at: string; net: number; symbol: string };

function istMinutes(iso: string): number {
  const parts = new Intl.DateTimeFormat("en-GB", { timeZone: "Asia/Kolkata", hour: "2-digit", minute: "2-digit", hour12: false })
    .formatToParts(new Date(iso));
  const h = Number(parts.find((p) => p.type === "hour")?.value ?? 0);
  const m = Number(parts.find((p) => p.type === "minute")?.value ?? 0);
  return h * 60 + m + new Date(iso).getSeconds() / 60;
}

function hhmmFromMinutes(m: number): string {
  const h = Math.floor(m / 60), mm = Math.floor(m % 60);
  return `${String(h).padStart(2, "0")}:${String(mm).padStart(2, "0")}`;
}

function parseHHMM(s: string): number {
  const [h, m] = s.split(":").map(Number);
  return h * 60 + m;
}

/**
 * The trading day as one ribbon: the bot's schedule, the P&L line through the session,
 * each closed trade, and where "now" is. This is the page's one bold element (docs/design.md).
 */
export default function DayStrip({ points, trades, now, entryStart, entryEnd, flattenAt, marketOpen }: {
  points: Pt[]; trades: TradeMark[]; now?: string; entryStart: string; entryEnd: string; flattenAt: string; marketOpen?: boolean;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [w, setW] = useState(900);
  const [hover, setHover] = useState<{ x: number; y: number; t: number; v: number } | null>(null);
  const reduce = useReducedMotion();
  const uid = useId().replace(/:/g, "");

  useEffect(() => {
    if (!ref.current) return;
    const ro = new ResizeObserver(([e]) => setW(Math.max(320, e.contentRect.width)));
    ro.observe(ref.current);
    return () => ro.disconnect();
  }, []);

  const H = 168, plotTop = 18, plotH = 118, axisY = plotTop + plotH;
  const x = (m: number) => ((Math.min(Math.max(m, OPEN), CLOSE) - OPEN) / (CLOSE - OPEN)) * w;

  const series = useMemo(() => points.map((p) => ({ t: istMinutes(p.at), v: p.value })).sort((a, b) => a.t - b.t), [points]);
  const [lo, hi] = useMemo(() => {
    const vs = series.map((s) => s.v);
    let a = Math.min(0, ...vs), b = Math.max(0, ...vs);
    if (a === b) { a = -1; b = 1; }
    const pad = (b - a) * 0.12;
    return [a - pad, b + pad];
  }, [series]);
  const y = (v: number) => plotTop + ((hi - v) / (hi - lo)) * plotH;
  const y0 = y(0);

  const line = series.length ? series.map((s, i) => `${i ? "L" : "M"}${x(s.t).toFixed(1)},${y(s.v).toFixed(1)}`).join(" ") : "";
  const area = series.length ? `${line} L${x(series[series.length - 1].t).toFixed(1)},${y0} L${x(series[0].t).toFixed(1)},${y0} Z` : "";

  const zones = [
    { from: OPEN, to: parseHHMM(entryStart), label: "Opening range", shade: "var(--wash)" },
    { from: parseHHMM(entryStart), to: parseHHMM(entryEnd), label: "Entries open", shade: "transparent" },
    { from: parseHHMM(entryEnd), to: parseHHMM(flattenAt), label: "Managing only", shade: "var(--wash)" },
    { from: parseHHMM(flattenAt), to: CLOSE, label: "Flat", shade: "var(--wash-strong)" },
  ].filter((z) => z.to > z.from);
  const hours = (w < 640 ? [11, 13] : [10, 11, 12, 13, 14, 15]).map((h) => h * 60);
  const nowM = now ? istMinutes(now) : null;
  const showNow = nowM !== null && nowM >= OPEN && nowM <= CLOSE;

  const valueAt = (t: number) => {
    let best = series[0];
    for (const s of series) if (Math.abs(s.t - t) < Math.abs(best.t - t)) best = s;
    return best;
  };

  const onMove = (e: React.PointerEvent<SVGSVGElement>) => {
    if (!series.length) return;
    const r = e.currentTarget.getBoundingClientRect();
    const t = OPEN + ((e.clientX - r.left) / r.width) * (CLOSE - OPEN);
    const s = valueAt(t);
    setHover({ x: x(s.t), y: y(s.v), t: s.t, v: s.v });
  };

  return (
    <div className="daystrip" ref={ref}>
      <svg viewBox={`0 0 ${w} ${H}`} height={H} role="img" aria-label="Today's P&L through the trading session"
        onPointerMove={onMove} onPointerLeave={() => setHover(null)}>
        <defs>
          {/* Gain/loss colour only away from zero, so a flat ₹0 line reads as neutral, not as a gain. */}
          <clipPath id={`above-${uid}`}><rect x={0} y={0} width={w} height={Math.max(0, y0 - 1.5)} /></clipPath>
          <clipPath id={`below-${uid}`}><rect x={0} y={y0 + 1.5} width={w} height={H} /></clipPath>
        </defs>

        {zones.map((z) => (
          <g key={z.label}>
            <rect x={x(z.from)} y={plotTop} width={x(z.to) - x(z.from)} height={plotH} fill={z.shade} />
            {x(z.to) - x(z.from) > 70 && (
              <text x={x(z.from) + 6} y={axisY + 30} fontSize={12} fill="var(--ink-soft)">{z.label}</text>
            )}
          </g>
        ))}
        {hours.map((m) => (
          <g key={m}>
            <line x1={x(m)} x2={x(m)} y1={plotTop} y2={axisY} stroke="var(--rule)" strokeWidth={1} />
            <text x={x(m)} y={axisY + 14} fontSize={11} fill="var(--ink-soft)" textAnchor="middle" className="tnum">{hhmmFromMinutes(m)}</text>
          </g>
        ))}
        <text x={2} y={axisY + 14} fontSize={11} fill="var(--ink-soft)" className="tnum">09:15</text>
        <text x={w - 2} y={axisY + 14} fontSize={11} fill="var(--ink-soft)" textAnchor="end" className="tnum">15:30</text>
        <line x1={0} x2={w} y1={y0} y2={y0} stroke="var(--rule-strong)" strokeWidth={1} />

        {series.length > 0 && (
          <>
            <path d={line} fill="none" stroke="var(--ink-soft)" strokeWidth={2} strokeLinejoin="round" />
            <path d={area} fill="var(--gain)" opacity={0.12} clipPath={`url(#above-${uid})`} />
            <path d={area} fill="var(--loss)" opacity={0.12} clipPath={`url(#below-${uid})`} />
            {(["above", "below"] as const).map((side) => (
              <motion.path key={side} d={line} fill="none" stroke={side === "above" ? "var(--gain)" : "var(--loss)"} strokeWidth={2}
                strokeLinejoin="round" strokeLinecap="round" clipPath={`url(#${side}-${uid})`}
                initial={reduce ? false : { pathLength: 0 }} animate={{ pathLength: 1 }} transition={{ duration: 1.1, ease: [0.3, 0, 0.2, 1] }} />
            ))}
          </>
        )}

        {series.length > 0 && trades.map((tr, i) => {
          const t = istMinutes(tr.at);
          const s = valueAt(t);
          return (
            <circle key={i} cx={x(t)} cy={y(s.v)} r={4.5} fill={tr.net >= 0 ? "var(--gain)" : "var(--loss)"} stroke="var(--paper)" strokeWidth={2}>
              <title>{`${tr.symbol} closed ${hhmmFromMinutes(t)}: ${signedInr(tr.net)}`}</title>
            </circle>
          );
        })}

        {showNow && (
          <g>
            <rect x={x(nowM!)} y={plotTop} width={Math.max(0, w - x(nowM!))} height={plotH} fill="var(--paper)" opacity={0.55} />
            <line x1={x(nowM!)} x2={x(nowM!)} y1={plotTop - 6} y2={axisY} stroke="var(--ink)" strokeWidth={1.5} />
            <text x={x(nowM!)} y={plotTop - 9} fontSize={12} fontWeight={600} fill="var(--ink)" textAnchor={x(nowM!) > w - 40 ? "end" : "middle"} className="tnum">
              {hhmmFromMinutes(nowM!)}
            </text>
          </g>
        )}

        {hover && (
          <g pointerEvents="none">
            <line x1={hover.x} x2={hover.x} y1={plotTop} y2={axisY} stroke="var(--ink-soft)" strokeWidth={1} />
            <circle cx={hover.x} cy={hover.y} r={4.5} fill={hover.v >= 0 ? "var(--gain)" : "var(--loss)"} stroke="var(--paper)" strokeWidth={2} />
          </g>
        )}

        {!series.length && (
          <text x={w / 2} y={plotTop + plotH / 2 + 5} fontSize={14} fill="var(--ink-soft)" textAnchor="middle">
            {marketOpen === false ? "Market is closed. The line starts at 09:15." : "No P&L yet today."}
          </text>
        )}
      </svg>
      {hover && (
        <div className="strip-tip" style={{ left: hover.x, top: hover.y - 10 }}>
          {hhmmFromMinutes(hover.t)}  {signedInr(hover.v)}
        </div>
      )}
    </div>
  );
}
