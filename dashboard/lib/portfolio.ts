// What the investing worker publishes about the portfolio beyond its holdings, inside the heartbeat's
// `portfolio` object (worker/thunderbot/invest.py). Every field is optional: a worker from before these
// existed still renders. Shared by the control API and the screens; no server code here.

/** How orders are carried out. `paper`: simulated. `guided`: listed for the owner to place by hand.
 *  `auto`: sent to the broker, and only on a worker whose own environment allows real orders. */
export type ExecMode = "paper" | "guided" | "auto";

/** One target holding against its drift corridor. Weights are in % of the portfolio. */
export type DriftRow = { symbol: string; weight: number; target: number; lo: number; hi: number; out: boolean; value: number };

/** Where the next deposited rupee would go: the holding furthest below its target. */
export type NextDeposit = { symbol: string; short_inr: number; short_pct: number } | null;

/** One proposed sale that books long-term equity gain inside the year's tax-free allowance.
 *  `via` says how the money gets back in: the next session, or a twin fund on the same day. */
export type HarvestLot = { symbol: string; qty: number; gain: number; held_days: number; via: "t_plus_1" | "twin"; twin?: string };

export type TaxYear = {
  /** Financial year, e.g. "2026-27". */
  fy: string;
  exempt: number;
  realized_ltcg: number;
  realized_other: number;
  /** What is left of the exemption. */
  remaining: number;
  /** Unrealized long-term equity gain that could be booked, before the cap. */
  harvestable_gain: number;
  /** The proposal, capped at `remaining`. */
  lots: HarvestLot[];
  days_left: number;
  note: string;
};

export type BasketOrder = { symbol: string; side: "BUY" | "SELL"; qty: number; limit: number; value: number; why: string };

/** Orders worked out by the plan for the owner to place by hand. `reason` is one of rebalance, deposit,
 *  sell_all, harvest, harvest_rebuy. */
export type Basket = {
  id: string; at: string; reason: string; orders: BasketOrder[]; status: "open" | "reconciled" | "expired";
  reconciled_at?: string; mismatch?: string[];
};

export type ExternalHolding = { symbol: string; qty: number; avg_price: number; ltp: number | null; value: number | null; kind: string; in_plan: boolean };

export type PortfolioExtras = {
  exec_mode?: ExecMode;
  /** Why the mode in use differs from the one asked for, e.g. automatic orders are not allowed on this worker. */
  exec_note?: string;
  band?: { abs_pct: number; rel_pct: number };
  drift?: DriftRow[];
  next_deposit?: NextDeposit;
  tax_year?: TaxYear;
  basket?: Basket | null;
  actual?: { source: "groww" | "manual" | null; synced_at: string | null; holdings: ExternalHolding[]; outside_plan_value: number };
  pending_deposit?: number;
};

export const EXEC_MODES: ExecMode[] = ["paper", "guided", "auto"];

/** A holdings row as the owner types it in. `since` (YYYY-MM-DD) is optional; without it the tax-year
 *  planner cannot tell whether a holding is long-term and leaves it out. */
export type HoldingRow = { symbol: string; qty: number; avg_price: number; since?: string };

// POST /api/control bodies added for the portfolio, by `action`. Commands marked "queued" are carried out
// by the worker on its next pass; the others take effect as soon as the worker next reads its controls.
export type PortfolioAction =
  | { action: "stop" } // no new trades; holdings stay
  | { action: "sell_all" } // queued; also stops new trades
  | { action: "set_mode"; mode: ExecMode }
  | { action: "deposit"; amount: number } // queued
  | { action: "harvest"; confirm: true } // queued
  | { action: "import_holdings"; rows: HoldingRow[] } // queued
  | { action: "clear_holdings" } // queued
  | { action: "basket_done"; id: string } // queued
  | { action: "sync_holdings" }; // queued
