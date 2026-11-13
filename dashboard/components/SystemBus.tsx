import type { ReactNode } from "react";

/** What is connected, as taps off one bus (docs/design.md).
 *
 *  These services are parallel, not a chain: the broker does not sit downstream of an optional LLM, and
 *  an unfitted optional part must never look like a break before something else. So each service hangs
 *  off the same vertical bar on its own tap. A solid tap is connected, a dashed tap is an optional part
 *  that is not fitted, a red tap is fitted and failing. */
export type TapTone = "on" | "optional" | "bad" | "off";
export type Tap = { key: string; name: string; note: string; tone: TapTone };

export function SystemBus({ taps, onPick, compact = false }: { taps: Tap[]; onPick?: (key: string) => void; compact?: boolean }) {
  return (
    <ul className={`bus ${compact ? "compact" : ""}`}>
      {taps.map((t) => (
        <li key={t.key} className={t.tone}>
          <span className="tap" aria-hidden><i /></span>
          {onPick
            ? <button type="button" onClick={() => onPick(t.key)}><b>{t.name}</b><span>{t.note}</span></button>
            : <span className="what"><b>{t.name}</b><span>{t.note}</span></span>}
        </li>
      ))}
    </ul>
  );
}

/** A tap that opens: the Setup page's stations hang off the same bus. */
export function BusStation({ tap, open, onToggle, blurb, status, children }: {
  tap: Tap; open: boolean; onToggle: () => void; blurb: string; status: string; children: ReactNode;
}) {
  return (
    <li className={`station ${tap.tone} ${open ? "open" : ""}`}>
      <span className="tap" aria-hidden><i /></span>
      <div className="station-main">
        <button type="button" aria-expanded={open} onClick={onToggle}>
          <span className="name"><b>{tap.name}</b><span>{blurb}</span></span>
          <span className="status">{status}</span>
          <svg className="chev" width="16" height="16" viewBox="0 0 16 16" aria-hidden><path d="M3.5 6 8 10.5 12.5 6" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" /></svg>
        </button>
        {open && <div className="station-body">{children}</div>}
      </div>
    </li>
  );
}
