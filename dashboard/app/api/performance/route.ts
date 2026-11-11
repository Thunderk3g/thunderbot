import { q, select } from "@/lib/db";
import { guard } from "@/lib/api";
import type { EquityPoint, Outcome, Trade } from "@/lib/types";

export const dynamic = "force-dynamic";

const MODES = new Set(["paper", "live", "replay"]);

export async function GET(req: Request) {
  return guard(async () => {
    const url = new URL(req.url);
    const mode = MODES.has(url.searchParams.get("mode") ?? "") ? url.searchParams.get("mode")! : "paper";
    const days = Math.min(Math.max(Number(url.searchParams.get("days") ?? 90) || 90, 1), 3650);
    // Anchor the window on the latest activity for this mode, so replays of old dates still show up.
    const [latestTrade, latestEquity] = await Promise.all([
      select<Trade>("trades", q({ select: "closed_at", mode: `eq.${mode}`, order: "closed_at.desc", limit: 1 })),
      select<EquityPoint>("equity", q({ select: "at", mode: `eq.${mode}`, order: "at.desc", limit: 1 })),
    ]);
    const stamps = [latestTrade[0]?.closed_at, latestEquity[0]?.at].filter(Boolean) as string[];
    if (!stamps.length) return { mode, days, trades: [], outcomes: [], value: [], anchor: null };
    const anchorIso = stamps.sort().at(-1)!;
    const since = new Date(new Date(anchorIso).getTime() - days * 86_400_000).toISOString();
    const [trades, outcomes, equity] = await Promise.all([
      select<Trade>("trades", q({ select: "*", mode: `eq.${mode}`, closed_at: `gte.${since}`, order: "closed_at.asc", limit: 5000 })),
      select<Outcome>("signal_outcomes", q({
        select: "signal_id,symbol,strategy,side,llm_decision,risk_approved,outcome,r_multiple,closed_at,mode",
        mode: `eq.${mode}`, closed_at: `gte.${since}`, order: "closed_at.asc", limit: 5000,
      })),
      select<EquityPoint>("equity", q({ select: "at,realized_pnl,unrealized_pnl", mode: `eq.${mode}`, at: `gte.${since}`, order: "at.desc", limit: 5000 })),
    ]);
    // One point per exchange day: the day's last reading of gain since the start.
    const byDay = new Map<string, number>();
    for (const e of equity) {
      const day = new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Kolkata" }).format(new Date(e.at));
      if (!byDay.has(day)) byDay.set(day, Number(e.realized_pnl) + Number(e.unrealized_pnl));
    }
    const value = [...byDay.entries()].sort(([x], [y]) => (x < y ? -1 : 1)).map(([day, gain]) => ({ day, gain }));
    return { mode, days, trades, outcomes, value, anchor: anchorIso };
  });
}
