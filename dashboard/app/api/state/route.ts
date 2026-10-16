import { getControl, istDayStart, istToday, q, select } from "@/lib/db";
import { guard } from "@/lib/api";
import type { Control, Decision, EquityPoint, EventRow, Outcome, Signal, SignalCard, Trade } from "@/lib/types";

export const dynamic = "force-dynamic";

export async function GET() {
  return guard(async () => {
    const control = (await getControl()) as Control;
    const hb = control.heartbeat;
    // The session day follows the worker's clock, so replays of past dates read like a live session.
    const sessionDay = hb?.at ? hb.at.slice(0, 10) : istToday();
    const since = istDayStart(sessionDay);
    const mode = hb?.mode ? `eq.${hb.mode}` : undefined;
    const [signals, decisions, outcomes, events, tradesToday, equityToday] = await Promise.all([
      select<Signal>("signals", q({ select: "*", order: "created_at.desc", limit: 30 })),
      select<Decision>("llm_decisions", q({
        select: "signal_id,approve,size_multiplier,confidence,rationale,risk_flags,model,latency_ms,error",
        order: "created_at.desc", limit: 60,
      })),
      select<Outcome>("signal_outcomes", q({
        select: "signal_id,symbol,strategy,side,llm_decision,risk_approved,outcome,r_multiple,closed_at,mode",
        order: "created_at.desc", limit: 60,
      })),
      select<EventRow>("events", q({ select: "id,created_at,kind,message", order: "created_at.desc", limit: 40 })),
      select<Trade>("trades", q({ select: "*", closed_at: `gte.${since}`, mode, order: "closed_at.desc", limit: 300 })),
      select<EquityPoint>("equity", q({ select: "at,realized_pnl,unrealized_pnl,mode", at: `gte.${since}`, mode, order: "at.asc", limit: 2000 })),
    ]);
    const dec = new Map(decisions.map((d) => [d.signal_id, d]));
    const out = new Map(outcomes.map((o) => [o.signal_id, o]));
    const cards: SignalCard[] = signals.map((s) => ({ ...s, decision: dec.get(s.id), outcome: out.get(s.id) }));
    return { control, sessionDay, signals: cards, events, tradesToday, equityToday, serverTime: new Date().toISOString() };
  });
}
