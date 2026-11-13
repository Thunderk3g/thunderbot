import type { CSSProperties, ReactNode } from "react";

/** The product's one picture: a decision as a conductor running through gates (docs/design.md).
 *  A gate can leave the line whole, thin it, or open and break it. Nothing downstream can make it thicker,
 *  which is also what the engine guarantees. Thickness is the share of normal size that is left. */

export type GateState = "pass" | "thin" | "cut" | "wait" | "absent";
export type Tone = "" | "gain" | "loss" | "ghost";
export type Gate = {
  key: string;
  label: string;
  state: GateState;
  /** Second caption line: a score, a reason, a size. */
  value?: ReactNode;
  tone?: Tone;
  /** Share of normal size left after this gate, 0 to 1. Only read on "thin". */
  size?: number;
};
export type LineEnd = { label: string; value?: ReactNode; tone?: Tone };

const FULL = { sm: 5, lg: 8 } as const;
const THIN = 1.2;

function Switch({ state, big }: { state: GateState | "dead"; big: boolean }) {
  const k = big ? 1.5 : 1;
  if (state === "absent") {
    // No gate fitted here: the line runs straight through an empty holder.
    return (
      <svg className="sw" width={20 * k} height={18 * k} viewBox="0 0 20 18" aria-hidden>
        <line className="lead" x1="0" y1="9" x2="20" y2="9" strokeWidth={`calc(var(--w) / ${k})`} strokeLinecap="butt" />
        <line className="lead" x1="5" y1="3.5" x2="5" y2="14.5" strokeWidth="1.6" />
        <line className="lead" x1="15" y1="3.5" x2="15" y2="14.5" strokeWidth="1.6" />
      </svg>
    );
  }
  const open = state === "cut";
  const live = state === "pass" || state === "thin";
  return (
    <svg className="sw" width={32 * k} height={18 * k} viewBox="0 0 32 18" aria-hidden>
      {live && <line className="arm" x1="5" y1="9" x2="27" y2="9" strokeWidth="2.6" />}
      {open && <line className="arm" x1="5" y1="9" x2="23" y2="1.6" strokeWidth="2.6" />}
      <circle cx="5" cy="9" r="3.6" />
      <circle cx="27" cy="9" r="3.6" style={open ? { fill: "var(--hole, var(--paper))" } : undefined} />
    </svg>
  );
}

export function Line({ source, gates, end, size = "sm", label }: {
  source: { label: string; value?: ReactNode };
  gates: Gate[];
  end: LineEnd;
  size?: "sm" | "lg";
  label?: string;
}) {
  const full = FULL[size];
  const k = size === "lg" ? 1.5 : 1;
  let share = 1;
  let broken = false;
  const items = gates.map((g) => {
    const widthIn = THIN + share * (full - THIN);
    const dead = broken;
    if (!dead) {
      if (g.state === "cut") broken = true;
      if (g.state === "thin") share = Math.max(0, Math.min(1, g.size ?? share));
    }
    return { g, widthIn, dead };
  });
  const endWidth = THIN + share * (full - THIN);
  const waiting = !broken && gates.some((g) => g.state === "wait");
  return (
    <ol className={`ln ${size === "lg" ? "lg" : ""}`} aria-label={label}>
      <li className="gate src" style={{ "--w": `${full}px` } as CSSProperties}>
        <div className="track">
          <svg className="sw" width={12 * k} height={18 * k} viewBox="0 0 12 18" aria-hidden><circle cx="6" cy="9" r="4.6" /></svg>
          <span className="wire" />
        </div>
        <div className="cap"><b>{source.label}</b>{source.value !== undefined && <em>{source.value}</em>}</div>
      </li>
      {items.map(({ g, widthIn, dead }) => {
        const state = dead ? "dead" : g.state;
        return (
          <li key={g.key} className={`gate ${state}`} style={{ "--w": `${widthIn}px` } as CSSProperties}>
            <div className="track"><span className="wire" /><Switch big={size === "lg"} state={dead || g.state === "wait" ? "dead" : g.state} /></div>
            <div className="cap"><b>{g.label}</b>{g.value !== undefined && <em className={dead ? "" : g.tone ?? ""}>{g.value}</em>}</div>
          </li>
        );
      })}
      <li className={`gate end ${broken ? "dead" : waiting ? "wait" : "pass"}`} style={{ "--w": `${endWidth}px` } as CSSProperties}>
        <div className="track">
          <span className="wire" />
          {broken || waiting
            ? <svg className="sw" width={12 * k} height={18 * k} viewBox="0 0 12 18" aria-hidden><circle cx="6" cy="9" r="4" /></svg>
            : <svg className="sw" width={14 * k} height={18 * k} viewBox="0 0 14 18" aria-hidden><path d="M0 1.5 13 9 0 16.5z" /></svg>}
        </div>
        <div className="cap"><b>{end.label}</b>{end.value !== undefined && <em className={end.tone ?? ""}>{end.value}</em>}</div>
      </li>
    </ol>
  );
}

/** One continuous line wound into a rosette, the way the fine lines on a banknote are drawn.
 *  Three hypotrochoids; each is a single closed path so it can be drawn in one stroke on load. */
export function Guilloche() {
  const curve = (R: number, r: number, d: number, turns: number, scale: number) => {
    const steps = 720;
    let path = "";
    for (let i = 0; i <= steps; i++) {
      const t = (i / steps) * Math.PI * 2 * turns;
      const x = ((R - r) * Math.cos(t) + d * Math.cos(((R - r) / r) * t)) * scale;
      const y = ((R - r) * Math.sin(t) - d * Math.sin(((R - r) / r) * t)) * scale;
      path += `${i ? "L" : "M"}${x.toFixed(1)} ${y.toFixed(1)}`;
    }
    return path + "Z";
  };
  return (
    <svg className="guilloche" viewBox="-310 -310 620 620" aria-hidden>
      <path pathLength={1} d={curve(96, 36, 58, 3, 2.35)} />
      <path pathLength={1} d={curve(105, 30, 34, 2, 2.6)} />
      <path pathLength={1} d={curve(84, 49, 70, 7, 2.3)} />
    </svg>
  );
}
