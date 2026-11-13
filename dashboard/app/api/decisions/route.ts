import { q, select } from "@/lib/db";
import { guard } from "@/lib/api";

export const dynamic = "force-dynamic";

type SignalRow = { id: string; created_at: string; symbol: string; side: string; strategy: string; signal_ts: string; mode: string; harness_id?: string | null };
type DecisionRow = { signal_id: string; approve: boolean; size_multiplier: number; model: string; error: string | null };
type OutcomeRow = { signal_id: string; llm_decision: string; risk_approved: boolean; outcome: string; r_multiple: number };

/** The ledger: every setup the rules proposed, what the gates did with it, and what it went on to do. */
export async function GET() {
  return guard(async () => {
    // `harness_id` arrives with a later migration; ask for it, and fall back if the column is not there yet.
    const signals = await select<SignalRow>("signals", q({ select: "id,created_at,symbol,side,strategy,signal_ts,mode,harness_id", order: "created_at.desc", limit: 200 }))
      .catch(() => select<SignalRow>("signals", q({ select: "id,created_at,symbol,side,strategy,signal_ts,mode", order: "created_at.desc", limit: 200 })));
    const [decisions, outcomes] = await Promise.all([
      select<DecisionRow>("llm_decisions", q({ select: "signal_id,approve,size_multiplier,model,error", order: "created_at.desc", limit: 400 })),
      select<OutcomeRow>("signal_outcomes", q({ select: "signal_id,llm_decision,risk_approved,outcome,r_multiple", order: "created_at.desc", limit: 400 })),
    ]);
    const dec = new Map(decisions.map((d) => [d.signal_id, d]));
    const out = new Map(outcomes.map((o) => [o.signal_id, o]));
    const rows = signals.map((s) => {
      const d = dec.get(s.id), o = out.get(s.id);
      return {
        id: s.id, at: s.signal_ts ?? s.created_at, symbol: s.symbol, side: s.side, strategy: s.strategy, mode: s.mode, harness_id: s.harness_id ?? null,
        asked: !!d, llm: d ? (d.error ? "failed" : d.approve ? (d.size_multiplier < 1 ? "shrunk" : "take") : "skip") : "none",
        size: d?.size_multiplier ?? null, model: d?.model ?? null,
        taken: o ? o.risk_approved : null, outcome: o?.outcome ?? null, r: o ? Number(o.r_multiple) : null,
      };
    });
    // What the gates were worth, in units of risk, before charges: every setup followed blind against the ones taken.
    const settled = rows.filter((r) => r.r !== null && r.taken !== null);
    const allR = settled.reduce((a, r) => a + (r.r as number), 0);
    const takenR = settled.filter((r) => r.taken).reduce((a, r) => a + (r.r as number), 0);
    return {
      rows,
      attribution: { n: settled.length, taken: settled.filter((r) => r.taken).length, all_r: allR, gates_r: takenR - allR, taken_r: takenR },
    };
  });
}
