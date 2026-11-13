// Shapes shared by the harness and gates APIs (app/api/harness, app/api/gates) and the screens that
// show them. The worker publishes both as control rows; nothing here is computed in the dashboard.

/** One file of the harness, as it was loaded. */
export type HarnessFile = { path: string; kind: "policy" | "plan" | "role" | "prompt" | "gates"; digest: string; text: string };

/** A role that can affect a trade. Roles that only write notes (the end-of-day reviewer) appear under `files`. */
export type HarnessRole = {
  name: string; label: string; purpose: string; may: "veto" | "shrink" | "postpone"; reads: string[]; on_failure: string;
  stage: "shadow" | "active"; scored: boolean; prompt_path: string;
};

export type HarnessState = {
  /** 12-character digest of every file in the bundle; stamped on each decision. */
  id: string;
  source: "built-in" | "directory";
  path: string | null;
  loaded_at: string | null;
  /** False when TB_HARNESS_DIR pointed at a harness that failed a check; the built-in one is then in use. */
  valid: boolean;
  problems: string[];
  memory_mode: "journal_only" | "inject";
  files: HarnessFile[];
  roles: HarnessRole[];
  /** Limits fixed in the code that no harness can exceed. */
  ceilings: Record<string, number>;
  previous_ids: { id: string; first_seen: string; last_seen: string; decisions: number }[];
};

/** The running average of a role's marginal value per setup, in R, with its confidence sequence. */
export type GatePoint = { n: number; mean: number; lower: number; upper: number };

export type GateRole = {
  role: string; label: string; harness_id: string; stage: "shadow" | "active"; n: number; n_min: number; alpha: number;
  mean: number | null; lower: number | null; upper: number | null;
  /** Running total of the role's marginal value, in R. */
  cum: number;
  /** What its calls have cost in total, in R. */
  cost_r: number;
  vetoes: number; shrinks: number;
  verdict: "proven" | "inconclusive" | "drag" | "too_few"; verdict_text: string;
  /** Scored setups still needed before a promotion is possible, or null once there are enough. */
  needs: number | null;
  series: GatePoint[];
  last_change: { at: string; from: string; to: string; why: string } | null;
};

export type GatesState = { updated_at: string | null; roles: GateRole[]; note: string };

export const EMPTY_HARNESS: HarnessState = {
  id: "", source: "built-in", path: null, loaded_at: null, valid: true, problems: [], memory_mode: "journal_only",
  files: [], roles: [], ceilings: {}, previous_ids: [],
};
export const EMPTY_GATES: GatesState = { updated_at: null, roles: [], note: "" };
