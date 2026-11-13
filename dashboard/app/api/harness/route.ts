import { getControl } from "@/lib/db";
import { guard } from "@/lib/api";
import { EMPTY_HARNESS, type HarnessState } from "@/lib/harness";

export const dynamic = "force-dynamic";

/** The harness the worker is running, as the worker last published it. Read-only: the harness is edited as files. */
export async function GET() {
  return guard(async (): Promise<HarnessState> => {
    const control = await getControl();
    return { ...EMPTY_HARNESS, ...((control.harness as Partial<HarnessState> | undefined) ?? {}) };
  });
}
