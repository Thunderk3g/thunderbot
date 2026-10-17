import { istToday, logEvent, setControl, upsert } from "@/lib/db";
import { fail, guard } from "@/lib/api";

export const dynamic = "force-dynamic";

const ACTIONS: Record<string, () => Promise<void>> = {
  // Start clears every stop condition at once; the worker then trades from the next bar.
  start: async () => {
    const updated_at = new Date().toISOString();
    await upsert("control", [
      { key: "kill_switch", value: false, updated_at },
      { key: "paused", value: false, updated_at },
      { key: "trading_enabled", value: true, updated_at },
    ]);
    await logEvent("dashboard", "trading started from dashboard");
  },
  stop: () => setControl("trading_enabled", false, "trading stopped from dashboard; closing open positions"),
  kill: () => setControl("kill_switch", true, "kill switch engaged from dashboard"),
  release: () => setControl("kill_switch", false, "kill switch released from dashboard"),
  pause: () => setControl("paused", true, "new entries paused from dashboard"),
  resume: () => setControl("paused", false, "new entries resumed from dashboard"),
  confirm_login: () => setControl("login_confirmed_for", istToday(), `operator confirmed broker login for ${istToday()}`),
};

export async function POST(req: Request) {
  let action: string | undefined;
  try {
    action = (await req.json()).action;
  } catch {
    return fail("invalid JSON", 400);
  }
  const fn = action ? ACTIONS[action] : undefined;
  if (!fn) return fail(`unknown action; use one of ${Object.keys(ACTIONS).join(", ")}`, 400);
  return guard(async () => {
    await fn();
    return { ok: true };
  });
}
