import type { Outcome, Trade } from "./types";
import { istDay } from "./format";

export type TradeStats = {
  trades: number; net: number; gross: number; costs: number; winRate: number | null; profitFactor: number | null;
  expectancy: number | null; maxDrawdown: number; avgWin: number | null; avgLoss: number | null;
};

export function tradeStats(trades: Trade[]): TradeStats {
  const nets = trades.map((t) => Number(t.net_pnl));
  const wins = nets.filter((x) => x > 0);
  const losses = nets.filter((x) => x <= 0);
  const net = nets.reduce((a, b) => a + b, 0);
  const grossLoss = -losses.reduce((a, b) => a + b, 0);
  let peak = 0, eq = 0, dd = 0;
  for (const t of [...trades].sort((a, b) => a.closed_at.localeCompare(b.closed_at))) {
    eq += Number(t.net_pnl);
    peak = Math.max(peak, eq);
    dd = Math.max(dd, peak - eq);
  }
  return {
    trades: trades.length,
    net,
    gross: trades.reduce((a, t) => a + Number(t.gross_pnl ?? 0), 0),
    costs: trades.reduce((a, t) => a + Number(t.costs ?? 0), 0),
    winRate: trades.length ? (wins.length / trades.length) * 100 : null,
    profitFactor: grossLoss > 0 ? wins.reduce((a, b) => a + b, 0) / grossLoss : null,
    expectancy: trades.length ? net / trades.length : null,
    maxDrawdown: dd,
    avgWin: wins.length ? wins.reduce((a, b) => a + b, 0) / wins.length : null,
    avgLoss: losses.length ? losses.reduce((a, b) => a + b, 0) / losses.length : null,
  };
}

export function dailySeries(trades: Trade[]): { day: string; pnl: number; equity: number }[] {
  const byDay = new Map<string, number>();
  for (const t of trades) {
    const d = istDay(t.closed_at);
    byDay.set(d, (byDay.get(d) ?? 0) + Number(t.net_pnl));
  }
  let eq = 0;
  return [...byDay.entries()].sort(([a], [b]) => a.localeCompare(b)).map(([day, pnl]) => {
    eq += pnl;
    return { day, pnl: Math.round(pnl * 100) / 100, equity: Math.round(eq * 100) / 100 };
  });
}

export type GroupStat = { key: string; trades: number; net: number; winRate: number };

export function groupBy(trades: Trade[], key: "strategy" | "symbol"): GroupStat[] {
  const m = new Map<string, Trade[]>();
  for (const t of trades) m.set(t[key], [...(m.get(t[key]) ?? []), t]);
  return [...m.entries()]
    .map(([k, ts]) => ({
      key: k, trades: ts.length, net: ts.reduce((a, t) => a + Number(t.net_pnl), 0),
      winRate: (ts.filter((t) => Number(t.net_pnl) > 0).length / ts.length) * 100,
    }))
    .sort((a, b) => b.net - a.net);
}

export type ReviewerStat = { decision: string; n: number; avgR: number; hitRate: number };

/** Average R-multiple of every signal's virtual outcome, split by the reviewer's decision. */
export function reviewerStats(outcomes: Outcome[]): ReviewerStat[] {
  const order = ["approve", "reject", "none"];
  return order
    .map((decision) => {
      const xs = outcomes.filter((o) => o.llm_decision === decision);
      return {
        decision,
        n: xs.length,
        avgR: xs.length ? xs.reduce((a, o) => a + Number(o.r_multiple), 0) / xs.length : 0,
        hitRate: xs.length ? (xs.filter((o) => Number(o.r_multiple) > 0).length / xs.length) * 100 : 0,
      };
    })
    .filter((s) => s.n > 0);
}
