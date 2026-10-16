import { q, select, upsert } from "@/lib/db";
import { fail, guard } from "@/lib/api";
import type { Job } from "@/lib/types";

export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  return guard(async () => {
    const id = new URL(req.url).searchParams.get("id");
    if (id) {
      const rows = await select<Job>("jobs", q({ select: "*", id: `eq.${id}`, limit: 1 }));
      if (!rows.length) throw new Error("job not found");
      return rows[0];
    }
    return select<Job>("jobs", q({ select: "id,created_at,kind,params,status,progress,error", order: "created_at.desc", limit: 15 }));
  });
}

export async function POST(req: Request) {
  let body: { kind?: string; params?: Record<string, unknown> };
  try {
    body = await req.json();
  } catch {
    return fail("invalid JSON", 400);
  }
  if (body.kind !== "backtest" && body.kind !== "sweep") return fail("kind must be backtest or sweep", 400);
  if (!body.params || typeof body.params !== "object") return fail("params required", 400);
  return guard(async () => {
    const id = crypto.randomUUID();
    await upsert("jobs", {
      id, created_at: new Date().toISOString(), kind: body.kind!, params: body.params!, status: "queued", progress: 0,
    });
    return { id };
  });
}
