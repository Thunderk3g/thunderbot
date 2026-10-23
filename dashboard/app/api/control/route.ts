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

const INVEST_STRATEGIES = new Set(["index_trend", "momentum"]);

export async function POST(req: Request) {
  let action: string | undefined;
  let body: { action?: string; strategy?: string; params?: Record<string, number> };
  try {
    body = await req.json();
    action = body.action;
  } catch {
    return fail("invalid JSON", 400);
  }
  if (action === "invest_settings") {
    // The worker clamps every parameter to its allowed range; this only checks the shape.
    if (!body.strategy || !INVEST_STRATEGIES.has(body.strategy)) return fail("strategy must be index_trend or momentum", 400);
    const params = Object.fromEntries(Object.entries(body.params ?? {}).filter(([, v]) => typeof v === "number" && Number.isFinite(v)));
    return guard(async () => {
      await setControl("invest_settings", { strategy: body.strategy, params }, `investing strategy set to ${body.strategy}`);
      return { ok: true };
    });
  }
  const fn = action ? ACTIONS[action] : undefined;
  if (!fn) return fail(`unknown action; use one of ${Object.keys(ACTIONS).join(", ")}`, 400);
  return guard(async () => {
    await fn();
    return { ok: true };
  });
}
