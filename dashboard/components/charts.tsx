"use client";

import {
  BaselineSeries, ColorType, HistogramSeries, LineSeries, createChart,
  type IChartApi, type ISeriesApi, type MouseEventParams, type Time, type UTCTimestamp,
} from "lightweight-charts";
import { useEffect, useRef, useState } from "react";
import { signedInr } from "@/lib/format";

export type Point = { time: string; value: number };

const IST_OFFSET = 19_800; // lightweight-charts renders UTC; shift so the axis reads in exchange time

function compactInr(p: number) {
  const a = Math.abs(p);
  const body = a >= 1e7 ? `${(a / 1e7).toFixed(1)}Cr` : a >= 1e5 ? `${(a / 1e5).toFixed(1)}L` : a >= 1e3 ? `${(a / 1e3).toFixed(a >= 1e4 ? 0 : 1)}k` : a.toFixed(0);
  return `${p < 0 ? "−" : ""}₹${body}`;
}

function cssVar(name: string) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function withAlpha(hex: string, alpha: number) {
  const h = hex.replace("#", "");
  const n = parseInt(h.length === 3 ? h.split("").map((c) => c + c).join("") : h, 16);
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${alpha})`;
}

function toTime(t: string, intraday: boolean): Time {
  return intraday ? ((Math.floor(Date.parse(t) / 1000) + IST_OFFSET) as UTCTimestamp) : (t.slice(0, 10) as Time);
}

function dedupe<T extends { time: Time }>(rows: T[]): T[] {
  const m = new Map<string, T>();
  for (const r of rows) m.set(String(r.time), r);
  return [...m.values()].sort((a, b) => (String(a.time) < String(b.time) ? -1 : 1));
}

function formatTime(time: Time, intraday: boolean) {
  if (typeof time === "number") {
    const d = new Date((time - IST_OFFSET) * 1000);
    return new Intl.DateTimeFormat("en-IN", { timeZone: "Asia/Kolkata", day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit", hour12: false }).format(d);
  }
  return intraday ? String(time) : new Date(`${String(time)}T00:00:00`).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "2-digit" });
}

function useThemeVersion() {
  const [v, setV] = useState(0);
  useEffect(() => {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    const bump = () => setV((x) => x + 1);
    mq.addEventListener("change", bump);
    const mo = new MutationObserver(bump);
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    return () => { mq.removeEventListener("change", bump); mo.disconnect(); };
  }, []);
  return v;
}

function baseOptions(intraday: boolean) {
  return {
    autoSize: true,
    layout: {
      background: { type: ColorType.Solid, color: "transparent" },
      textColor: cssVar("--ink-soft"),
      fontFamily: getComputedStyle(document.body).fontFamily,
      fontSize: 12,
      attributionLogo: false, // attribution is in the page footer instead
    },
    grid: { vertLines: { visible: false }, horzLines: { color: cssVar("--rule") } },
    rightPriceScale: { borderVisible: false, scaleMargins: { top: 0.15, bottom: 0.1 } },
    timeScale: { borderVisible: false, timeVisible: intraday, secondsVisible: false, fixLeftEdge: true, fixRightEdge: true },
    crosshair: {
      vertLine: { color: cssVar("--rule-strong"), width: 1 as const, style: 0, labelVisible: false },
      horzLine: { color: cssVar("--rule-strong"), width: 1 as const, style: 0, labelVisible: false },
    },
    localization: { priceFormatter: (p: number) => compactInr(p) },
    handleScroll: false,
    handleScale: false,
  };
}

function useTooltip(intraday: boolean, label: string) {
  const [tip, setTip] = useState<{ x: number; y: number; time: string; value: number } | null>(null);
  const handler = (series: ISeriesApi<"Baseline" | "Histogram">, el: HTMLElement) => (p: MouseEventParams) => {
    const d = p.seriesData.get(series) as { value?: number } | undefined;
    if (!p.point || !p.time || d?.value === undefined) return setTip(null);
    const x = Math.min(Math.max(p.point.x + 12, 0), el.clientWidth - 150);
    setTip({ x, y: Math.max(p.point.y - 44, 0), time: formatTime(p.time, intraday), value: d.value });
  };
  const node = tip && (
    <div className="chart-tip" style={{ left: tip.x, top: tip.y }}>
      <div className="t">{tip.time}</div>
      <div><strong>{signedInr(tip.value)}</strong> <span className="t">{label}</span></div>
    </div>
  );
  return { handler, node };
}

/** Cumulative P&L around a zero baseline: blue above, red below. */
export function PnlCurve({ points, intraday = false, height = 220, label = "P&L" }: {
  points: Point[]; intraday?: boolean; height?: number; label?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Baseline"> | null>(null);
  const theme = useThemeVersion();
  const { handler, node } = useTooltip(intraday, label);

  useEffect(() => {
    if (!ref.current) return;
    const up = cssVar("--gain"), down = cssVar("--loss");
    const chart = createChart(ref.current, baseOptions(intraday));
    const series = chart.addSeries(BaselineSeries, {
      baseValue: { type: "price", price: 0 },
      topLineColor: up, topFillColor1: withAlpha(up, 0.18), topFillColor2: withAlpha(up, 0.02),
      bottomLineColor: down, bottomFillColor1: withAlpha(down, 0.02), bottomFillColor2: withAlpha(down, 0.18),
      lineWidth: 2, priceLineVisible: false, lastValueVisible: false, crosshairMarkerRadius: 4,
      crosshairMarkerBorderColor: cssVar("--paper"), crosshairMarkerBorderWidth: 2,
    });
    const onMove = handler(series, ref.current);
    chart.subscribeCrosshairMove(onMove);
    chartRef.current = chart;
    seriesRef.current = series;
    return () => { chart.unsubscribeCrosshairMove(onMove); chart.remove(); chartRef.current = null; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [intraday, theme]);

  useEffect(() => {
    if (!seriesRef.current) return;
    seriesRef.current.setData(dedupe(points.map((p) => ({ time: toTime(p.time, intraday), value: p.value }))));
    chartRef.current?.timeScale().fitContent();
  }, [points, intraday, theme]);

  return <div className="chart" style={{ height }} ref={ref}>{node}</div>;
}

/** Portfolio value against a benchmark, both from the same starting capital. */
export function GrowthChart({ points, height = 260, label = "Strategy", benchLabel = "Nifty ETF" }: {
  points: { time: string; value: number; benchmark: number }[]; height?: number; label?: string; benchLabel?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const theme = useThemeVersion();
  const [tip, setTip] = useState<{ x: number; y: number; time: string; a: number; b: number } | null>(null);

  useEffect(() => {
    if (!ref.current) return;
    const el = ref.current;
    const opts = baseOptions(false);
    const chart = createChart(el, { ...opts, localization: { priceFormatter: (p: number) => compactInr(p).replace("−", "-") } });
    const main = chart.addSeries(LineSeries, { color: cssVar("--gain"), lineWidth: 2, priceLineVisible: false, lastValueVisible: false });
    const bench = chart.addSeries(LineSeries, { color: cssVar("--ink-soft"), lineWidth: 1, lineStyle: 2, priceLineVisible: false, lastValueVisible: false });
    main.setData(dedupe(points.map((p) => ({ time: toTime(p.time, false), value: p.value }))));
    bench.setData(dedupe(points.map((p) => ({ time: toTime(p.time, false), value: p.benchmark }))));
    chart.timeScale().fitContent();
    const onMove = (p: MouseEventParams) => {
      const a = p.seriesData.get(main) as { value?: number } | undefined;
      const b = p.seriesData.get(bench) as { value?: number } | undefined;
      if (!p.point || !p.time || a?.value === undefined || b?.value === undefined) return setTip(null);
      setTip({ x: Math.min(Math.max(p.point.x + 12, 0), el.clientWidth - 170), y: Math.max(p.point.y - 56, 0),
        time: formatTime(p.time, false), a: a.value, b: b.value });
    };
    chart.subscribeCrosshairMove(onMove);
    return () => { chart.unsubscribeCrosshairMove(onMove); chart.remove(); };
  }, [points, theme]);

  return (
    <div className="chart" style={{ height }} ref={ref}>
      {tip && (
        <div className="chart-tip" style={{ left: tip.x, top: tip.y }}>
          <div>{tip.time}</div>
          <div><strong>{inrFull(tip.a)}</strong> {label}</div>
          <div>{inrFull(tip.b)} {benchLabel}</div>
        </div>
      )}
    </div>
  );
}

function inrFull(n: number) {
  return `₹${Math.round(n).toLocaleString("en-IN")}`;
}

/** Daily P&L bars, colored by sign (diverging blue/red). */
export function PnlBars({ points, height = 160 }: { points: Point[]; height?: number }) {
  const ref = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);
  const theme = useThemeVersion();
  const { handler, node } = useTooltip(false, "day");

  useEffect(() => {
    if (!ref.current) return;
    const opts = baseOptions(false);
    // Thin bars (≤ ~24px) even when there are only a few days to show.
    const chart = createChart(ref.current, { ...opts, timeScale: { ...opts.timeScale, maxBarSpacing: 30 } });
    const series = chart.addSeries(HistogramSeries, { priceLineVisible: false, lastValueVisible: false, base: 0 });
    const onMove = handler(series, ref.current);
    chart.subscribeCrosshairMove(onMove);
    chartRef.current = chart;
    seriesRef.current = series;
    return () => { chart.unsubscribeCrosshairMove(onMove); chart.remove(); chartRef.current = null; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [theme]);

  useEffect(() => {
    if (!seriesRef.current) return;
    const up = cssVar("--gain"), down = cssVar("--loss");
    seriesRef.current.setData(dedupe(points.map((p) => ({ time: toTime(p.time, false), value: p.value, color: p.value >= 0 ? up : down }))));
    chartRef.current?.timeScale().fitContent();
  }, [points, theme]);

  return <div className="chart" style={{ height }} ref={ref}>{node}</div>;
}
