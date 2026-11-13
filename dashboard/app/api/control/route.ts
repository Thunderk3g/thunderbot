import { getControl, istToday, logEvent, setControl, upsert } from "@/lib/db";
import { fail, guard } from "@/lib/api";
import { EXEC_MODES, type ExecMode, type HoldingRow } from "@/lib/portfolio";

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
  // Stop means no new trades. Investments stay where they are; only intraday positions, which cannot be
  // carried overnight, are closed. Selling the portfolio is a separate, explicit action (sell_all).
  stop: () => setControl("trading_enabled", false, "stopped from dashboard: no new trades; holdings stay"),
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

// Commands the investing worker carries out on its next pass. They are appended to one control row, each
// with a rising number; the worker remembers the last number it handled, so nothing runs twice and the row
// never has to be cleared (worker/thunderbot/invest.py, _drain_commands). None of them, and nothing else
// this route writes, can switch on real orders: that takes switches in the worker's own environment.
const COMMANDS_KEY = "invest_commands";
type Command = { id: number; at: string; cmd: string } & Record<string, unknown>;

async function queue(cmd: string, fields: Record<string, unknown>, message: string): Promise<number> {
  const control = await getControl();
  const items = ((control[COMMANDS_KEY] as { items?: Command[] } | undefined)?.items ?? []).filter((c) => c && typeof c.id === "number");
  const id = Math.max(Date.now(), ...items.map((c) => c.id + 1));
  const now = new Date().toISOString();
  await upsert("control", { key: COMMANDS_KEY, value: { items: [...items, { id, at: now, cmd, ...fields }].slice(-20) }, updated_at: now });
  await logEvent("dashboard", message, { command: cmd });
  return id;
}

const SYMBOL = /^[A-Z0-9][A-Z0-9&_.-]{0,23}$/;
const DAY = /^\d{4}-\d{2}-\d{2}$/;

function cleanRows(rows: unknown): HoldingRow[] | string {
  if (!Array.isArray(rows)) return "rows must be a list of {symbol, qty, avg_price}";
  if (rows.length > 200) return "at most 200 holdings";
  const out: HoldingRow[] = [];
  for (const r of rows as Record<string, unknown>[]) {
    const symbol = String(r?.symbol ?? "").trim().toUpperCase();
    const qty = Number(r?.qty), avg = Number(r?.avg_price);
    if (!SYMBOL.test(symbol)) return `"${symbol.slice(0, 24)}" is not an NSE symbol`;
    if (!Number.isFinite(qty) || qty <= 0 || qty > 1e9) return `${symbol}: quantity must be more than zero`;
    if (!Number.isFinite(avg) || avg < 0 || avg > 1e7) return `${symbol}: average price must be zero or more`;
    const row: HoldingRow = { symbol, qty, avg_price: avg };
    if (r?.since !== undefined && r.since !== null && r.since !== "") {
      if (typeof r.since !== "string" || !DAY.test(r.since)) return `${symbol}: the purchase date must look like 2025-04-30`;
      row.since = r.since;
    }
    out.push(row);
  }
  return out;
}

export async function POST(req: Request) {
  let action: string | undefined;
  let body: { action?: string; strategy?: string; params?: Record<string, number>; mode?: string; amount?: number; confirm?: boolean;
    rows?: unknown; id?: string };
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
  // The portfolio: how orders are carried out, deposits, holdings, the tax year.
  if (action === "set_mode") {
    if (!EXEC_MODES.includes(body.mode as ExecMode)) return fail(`mode must be one of ${EXEC_MODES.join(", ")}`, 400);
    // "auto" here is a request. The worker honours it only if its own environment allows real orders;
    // anywhere else it lists the orders to place by hand and says why.
    return guard(async () => {
      await setControl("invest_mode", body.mode, `orders are now ${body.mode === "paper" ? "simulated" : body.mode === "guided" ? "listed for you to place by hand" : "requested as automatic"}`);
      return { ok: true };
    });
  }
  if (action === "sell_all") {
    return guard(async () => {
      await setControl("trading_enabled", false, "stopped from dashboard before selling everything");
      return { ok: true, command: await queue("sell_all", {}, "you asked to sell every holding the plan manages") };
    });
  }
  if (action === "deposit") {
    const amount = Number(body.amount);
    if (!Number.isFinite(amount) || amount < 1 || amount > 1e9) return fail("amount must be between 1 and 1,00,00,00,000 rupees", 400);
    return guard(async () => ({ ok: true, command: await queue("deposit", { amount: Math.round(amount * 100) / 100 }, `deposit of ₹${Math.round(amount).toLocaleString("en-IN")} recorded`) }));
  }
  if (action === "harvest") {
    if (body.confirm !== true) return fail("a harvest needs confirm: true", 400);
    return guard(async () => ({ ok: true, command: await queue("harvest", { confirm: true }, "you confirmed the tax-year harvest") }));
  }
  if (action === "import_holdings") {
    const rows = cleanRows(body.rows);
    if (typeof rows === "string") return fail(rows, 400);
    if (!rows.length) return fail("add at least one holding, or use clear_holdings", 400);
    return guard(async () => ({ ok: true, command: await queue("import_holdings", { rows }, `${rows.length} holdings entered by hand`) }));
  }
  if (action === "clear_holdings") {
    return guard(async () => ({ ok: true, command: await queue("clear_holdings", {}, "the list of holdings was cleared") }));
  }
  if (action === "sync_holdings") {
    return guard(async () => ({ ok: true, command: await queue("sync_holdings", {}, "asked the worker to read holdings from Groww") }));
  }
  if (action === "basket_done") {
    if (typeof body.id !== "string" || !/^[A-Za-z0-9-]{1,40}$/.test(body.id)) return fail("id must be the basket's id", 400);
    return guard(async () => ({ ok: true, command: await queue("basket_done", { basket: body.id }, "you marked the basket as placed") }));
  }
  const fn = action ? ACTIONS[action] : undefined;
  if (!fn) return fail(`unknown action; use one of ${[...Object.keys(ACTIONS), "invest_settings", "ai_params", "set_mode", "sell_all", "deposit", "harvest", "import_holdings", "clear_holdings", "sync_holdings", "basket_done"].join(", ")}`, 400);
  return guard(async () => {
    await fn();
    return { ok: true };
  });
}
