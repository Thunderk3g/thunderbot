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
  // The AI desk (intraday paper trading) has its own switch; the kill switch stops both.
  ai_start: async () => {
    const updated_at = new Date().toISOString();
    await upsert("control", [
      { key: "kill_switch", value: false, updated_at },
      { key: "intraday_enabled", value: true, updated_at },
    ]);
    await logEvent("dashboard", "AI desk started from dashboard");
  },
  ai_stop: () => setControl("intraday_enabled", false, "AI desk stopped from dashboard; open paper positions are closed on the next bar"),
  confirm_login: () => setControl("login_confirmed_for", istToday(), `operator confirmed broker login for ${istToday()}`),
};

const INVEST_STRATEGIES = new Set(["core_mix", "etf_trend", "etf_rank", "index_trend", "momentum"]);

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
    if (!body.strategy || !INVEST_STRATEGIES.has(body.strategy)) return fail(`strategy must be one of ${[...INVEST_STRATEGIES].join(", ")}`, 400);
    const params = Object.fromEntries(Object.entries(body.params ?? {}).filter(([, v]) => typeof v === "number" && Number.isFinite(v)));
    return guard(async () => {
      await setControl("invest_settings", { strategy: body.strategy, params }, `investing strategy set to ${body.strategy}`);
      return { ok: true };
    });
  }
  if (action === "ai_params") {
    // strict: 0 = paper learning (trade the best-scored setups), 1 = only when the model expects a profit.
    const p = body.params ?? {};
    const clean: Record<string, number> = {};
    if (p.strict === 0 || p.strict === 1) clean.strict = p.strict;
    if (typeof p.min_stop_pct === "number" && p.min_stop_pct >= 0 && p.min_stop_pct <= 3) clean.min_stop_pct = p.min_stop_pct;
    if (typeof p.min_prob === "number" && p.min_prob >= 0 && p.min_prob <= 0.9) clean.min_prob = p.min_prob;
    return guard(async () => {
      await setControl("ai_params", clean, `AI desk settings changed: ${JSON.stringify(clean)}`);
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
