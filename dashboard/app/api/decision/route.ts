import { q, select } from "@/lib/db";
import { fail, guard } from "@/lib/api";

export const dynamic = "force-dynamic";

/** Everything recorded about one decision, by the id of the setup that started it. */
export async function GET(req: Request) {
  const id = new URL(req.url).searchParams.get("id") ?? "";
  if (!/^[A-Za-z0-9_-]{6,64}$/.test(id)) return fail("that is not a decision id", 400);
  return guard(async () => {
    const eq = `eq.${id}`;
    const [signals, decisions, outcomes, orders, trades] = await Promise.all([
      select("signals", q({ select: "*", id: eq, limit: 1 })),
      select("llm_decisions", q({ select: "*", signal_id: eq, order: "created_at.asc", limit: 5 })),
      select("signal_outcomes", q({ select: "*", signal_id: eq, limit: 1 })),
      select("orders", q({ select: "*", signal_id: eq, order: "created_at.asc", limit: 20 })),
      select("trades", q({ select: "*", signal_id: eq, order: "closed_at.asc", limit: 5 })),
    ]);
    if (!signals.length) throw new Error("no decision with that id");
    return { signal: signals[0], decision: decisions[decisions.length - 1] ?? null, outcome: outcomes[0] ?? null, orders, trades };
  });
}
