import type { CSSProperties, ReactNode } from "react";

/** One decision as a conductor running through gates, in the order they were asked (docs/design.md).
 *
 *  The rule of the picture: if an order passes, the conductor never breaks. A faint channel of constant
 *  width runs the whole way and stands for full size; the filled core inside it is the share of full size
 *  that is left. A gate can leave the core whole, narrow it, hold it for a day, or open and break it.
 *  Nothing downstream can widen it, which is also what the engine guarantees.
 *
 *  Use this only for causal, time-ordered gates of a single decision. What is connected to what is a
 *  different shape and has its own component (SystemBus). */

export type GateState =
  | "pass"     // closed: the core runs through unchanged
  | "thin"     // closed, and the core is narrower after it (see `size`)
  | "defer"    // held for now: nothing passes today, the decision is taken again later
  | "cut"      // open: the only state with a broken conductor
  | "absent"   // an optional gate that is not fitted: the core runs straight through an empty socket
  | "wait";    // not reached yet
export type Tone = "" | "gain" | "loss" | "ghost";
export type Gate = {
  key: string;
  label: string;
  state: GateState;
  /** Second caption line: a score, a reason, a size. */
  value?: ReactNode;
  tone?: Tone;
  /** Share of full size left after this gate, 0 to 1. Read on "thin"; shown as a ×0.5 badge. */
  size?: number;
};
export type Leg = { side: "BUY" | "SELL"; text: string };
export type TraceEnd = {
  label: string; value?: ReactNode; tone?: Tone;
  /** A rebalance has several orders at once, so its end fans into one chip per order. */
  legs?: Leg[];
};

function GateGlyph({ state, share }: { state: GateState | "dead"; share: number }) {
  // Drawn in a 34 x 18 box whose centre line is the conductor. `--H` is the channel's width.
  const core = `calc(var(--H) * ${share})`;
  if (state === "absent") {
    return (
      <svg className="glyph" viewBox="0 0 34 18" aria-hidden>
        <line className="ghost" x1="0" y1="9" x2="34" y2="9" />
        <line className="core" x1="0" y1="9" x2="34" y2="9" style={{ strokeWidth: core }} />
        <rect className="socket" x="5" y="1.5" width="24" height="15" rx="4" />
      </svg>
    );
  }
  if (state === "defer") {
    return (
      <svg className="glyph" viewBox="0 0 34 18" aria-hidden>
        <line className="ghost" x1="0" y1="9" x2="34" y2="9" />
        <line className="core" x1="0" y1="9" x2="9" y2="9" style={{ strokeWidth: core }} />
        <rect className="latch" x="8" y="0.75" width="18" height="16.5" rx="4" />
        <line className="latch-bar" x1="14" y1="5" x2="14" y2="13" />
        <line className="latch-bar" x1="20" y1="5" x2="20" y2="13" />
      </svg>
    );
  }
  const live = state === "pass" || state === "thin";
  const open = state === "cut";
  return (
    <svg className="glyph" viewBox="0 0 34 18" aria-hidden>
      <line className="ghost" x1="0" y1="9" x2="34" y2="9" />
      {live && <line className="core" x1="0" y1="9" x2="34" y2="9" style={{ strokeWidth: core }} />}
      {open && <line className="core" x1="0" y1="9" x2="6" y2="9" style={{ strokeWidth: core }} />}
      {open && <line className="arm" x1="6" y1="9" x2="23" y2="0.6" />}
      <circle className={live || open ? "term on" : "term"} cx="6" cy="9" r="5.2" />
      <circle className={live ? "term on" : "term"} cx="28" cy="9" r="5.2" />
    </svg>
  );
}

export function DecisionTrace({ source, gates, end, size = "sm", live = false, label }: {
  source: { label: string; value?: ReactNode };
  gates: Gate[];
  end: TraceEnd;
  size?: "sm" | "lg";
  /** True while the decision is still open (a position on, a check running). Settled traces stay calm. */
  live?: boolean;
  label?: string;
}) {
  let share = 1;
  let stopped: "cut" | "defer" | null = null;
  const items = gates.map((g) => {
    const shareIn = stopped ? 0 : share;
    const dead = stopped !== null;
    if (!dead) {
      if (g.state === "cut") stopped = "cut";
      else if (g.state === "defer") stopped = "defer";
      else if (g.state === "thin") share = Math.max(0, Math.min(1, g.size ?? share));
    }
    return { g, shareIn, shareOut: stopped ? 0 : share, dead };
  });
  const waiting = !stopped && gates.some((g) => g.state === "wait");
  const endShare = stopped || waiting ? 0 : share;
  const endState = stopped === "cut" ? "dead" : stopped === "defer" ? "held" : waiting ? "wait" : "pass";
  const vars = (s: number) => ({ "--share": s } as CSSProperties);
  return (
    <ol className={`trace ${size === "lg" ? "lg" : ""} ${live ? "live" : ""}`} aria-label={label}>
      <li className="tg src">
        <div className="track">
          <svg className="glyph node" viewBox="0 0 14 18" aria-hidden><circle className="term on" cx="7" cy="9" r="6" /></svg>
          <span className="chan" style={vars(1)} />
        </div>
        <div className="cap"><b>{source.label}</b>{source.value !== undefined && <em>{source.value}</em>}</div>
      </li>
      {items.map(({ g, shareIn, shareOut, dead }) => {
        const state = dead || g.state === "wait" ? (dead ? "dead" : "wait") : g.state;
        return (
          <li key={g.key} className={`tg ${state}`}>
            <div className="track">
              <span className="chan" style={vars(shareIn)} />
              <GateGlyph state={state === "wait" ? "dead" : state} share={g.state === "thin" && !dead ? shareOut : shareIn} />
            </div>
            <div className="cap">
              <b>{g.label}</b>
              {g.state === "thin" && !dead && g.size !== undefined && <span className="mult">×{Number(g.size.toFixed(2))}</span>}
              {g.value !== undefined && <em className={dead ? "" : g.tone ?? ""}>{g.value}</em>}
            </div>
          </li>
        );
      })}
      <li className={`tg end ${endState} ${end.legs?.length ? "fan" : ""}`}>
        <div className="track">
          <span className="chan" style={vars(endShare)} />
          {endState === "pass"
            ? <svg className="glyph head" viewBox="0 0 14 18" aria-hidden><path d="M0 2 13 9 0 16z" /></svg>
            : <svg className="glyph node" viewBox="0 0 14 18" aria-hidden><circle className="term" cx="7" cy="9" r="4.2" /></svg>}
        </div>
        <div className="cap">
          <b>{end.label}</b>
          {end.value !== undefined && <em className={end.tone ?? ""}>{end.value}</em>}
          {end.legs?.length ? (
            <ul className="legs">
              {end.legs.map((l, i) => <li key={i} className={l.side === "BUY" ? "buy" : "sell"}><span>{l.side === "BUY" ? "Buy" : "Sell"}</span>{l.text}</li>)}
            </ul>
          ) : null}
        </div>
      </li>
    </ol>
  );
}
