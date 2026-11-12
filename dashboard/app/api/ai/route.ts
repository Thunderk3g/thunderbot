import { q, select } from "@/lib/db";
import { guard } from "@/lib/api";
import type { Job, ModelReport } from "@/lib/types";

export const dynamic = "force-dynamic";

/** The AI desk's current model report and its latest training job. The model itself stays on the server. */
export async function GET() {
  return guard(async () => {
    const [models, jobs] = await Promise.all([
      select<{ id: string; created_at: string; report: ModelReport }>("models", q({
        select: "id,created_at,report", name: "eq.intraday_setups", order: "created_at.desc", limit: 1 })),
      select<Job>("jobs", q({ select: "id,created_at,kind,status,progress,error", kind: "eq.train", order: "created_at.desc", limit: 1 })),
    ]);
    return { model: models[0] ?? null, job: jobs[0] ?? null };
  });
}
