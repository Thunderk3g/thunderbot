import { getControl, logEvent, upsert } from "@/lib/db";
import { guard } from "@/lib/api";
import { EMPTY_GATES, type GatesState } from "@/lib/harness";

export const dynamic = "force-dynamic";

/** Each scored LLM role's record against doing nothing, as the worker last published it. */
export async function GET() {
  return guard(async (): Promise<GatesState> => {
    const control = await getControl();
    return { ...EMPTY_GATES, ...((control.gates as Partial<GatesState> | undefined) ?? {}) };
  });
}

/** Score the roles now instead of waiting for the next close. Queues a job; the worker does the sums. */
export async function POST() {
  return guard(async () => {
    const id = crypto.randomUUID();
    await upsert("jobs", { id, created_at: new Date().toISOString(), kind: "gates", params: {}, status: "queued", progress: 0 });
    await logEvent("dashboard", "asked the worker to score the LLM roles now");
    return { ok: true, jobId: id };
  });
}
