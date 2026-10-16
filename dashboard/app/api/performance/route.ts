import { q, select } from "@/lib/db";
import { guard } from "@/lib/api";
import type { Outcome, Trade } from "@/lib/types";

export const dynamic = "force-dynamic";

const MODES = new Set(["paper", "live", "replay"]);

export async function GET(req: Request) {
  return guard(async () => {
    const url = new URL(req.url);
    const mode = MODES.has(url.searchParams.get("mode") ?? "") ? url.searchParams.get("mode")! : "paper";
    const days = Math.min(Math.max(Number(url.searchParams.get("days") ?? 90) || 90, 1), 3650);
    // Anchor the window on the latest trade for this mode, so replays of old dates still show up.
    const latest = await select<Trade>("trades", q({ select: "closed_at", mode: `eq.${mode}`, order: "closed_at.desc", limit: 1 }));
    if (!latest.length) return { mode, days, trades: [], outcomes: [], anchor: null };
    const anchor = new Date(latest[0].closed_at);
    const since = new Date(anchor.getTime() - days * 86_400_000).toISOString();
    const [trades, outcomes] = await Promise.all([
      select<Trade>("trades", q({ select: "*", mode: `eq.${mode}`, closed_at: `gte.${since}`, order: "closed_at.asc", limit: 5000 })),
      select<Outcome>("signal_outcomes", q({
        select: "signal_id,symbol,strategy,side,llm_decision,risk_approved,outcome,r_multiple,closed_at,mode",
        mode: `eq.${mode}`, closed_at: `gte.${since}`, order: "closed_at.asc", limit: 5000,
      })),
    ]);
    return { mode, days, trades, outcomes, anchor: latest[0].closed_at };
  });
}
