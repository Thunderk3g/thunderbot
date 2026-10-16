import { setControl } from "@/lib/db";
import { fail, guard } from "@/lib/api";

export const dynamic = "force-dynamic";

// The worker validates and clamps every key (and rejects env-only ones such as live trading);
// this route only checks the shape.
export async function POST(req: Request) {
  let overrides: unknown;
  try {
    overrides = (await req.json()).overrides;
  } catch {
    return fail("invalid JSON", 400);
  }
  if (!overrides || typeof overrides !== "object" || Array.isArray(overrides)) return fail("overrides must be an object", 400);
  if (JSON.stringify(overrides).length > 20_000) return fail("overrides too large", 400);
  return guard(async () => {
    await setControl("settings_overrides", overrides, "settings updated from dashboard");
    return { ok: true };
  });
}
