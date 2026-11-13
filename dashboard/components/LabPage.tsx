"use client";

import type { GateRole, GatesState } from "@/lib/harness";
import { signed } from "@/lib/format";
import type { SetupState } from "@/lib/setup";
import type { LiveState } from "@/lib/types";
import { usePoll } from "@/lib/usePoll";
import DeskView from "./DeskView";
import LabView from "./LabView";
import PerformanceView from "./PerformanceView";
import { Empty, Tabs } from "./ui";

const TABS = [
  { href: "/lab", label: "Gates" },
  { href: "/lab/desk", label: "Intraday desk" },
  { href: "/lab/sweeps", label: "Sweeps" },
  { href: "/lab/results", label: "Results" },
];

/** The research room. Nothing in it moves money; it exists to find out, on forward data, whether a
 *  part of the machine has earned any authority. */
export default function LabPage({ state, setup, refresh, go, tab }: {
  state: LiveState | null; setup: SetupState | null; refresh: () => void; go: (to: string) => void; tab?: string;
}) {
  const current = tab && TABS.some((t) => t.href === `/lab/${tab}`) ? `/lab/${tab}` : "/lab";
  return (
    <div>
      <div className="page-head" style={{ marginBottom: 22 }}>
        <div>
          <h1>Lab<span className="badge-paper">paper only</span></h1>
          <p className="lede">Nothing in this room moves money. It is where each part of the machine has to show, on days it has not seen, that it earns its place.</p>
        </div>
      </div>
      <Tabs items={TABS} current={current} go={go} />
      {current === "/lab" && <Gates go={go} />}
      {current === "/lab/desk" && <DeskView state={state} refresh={refresh} setup={setup} go={go} />}
      {current === "/lab/sweeps" && <LabView only="intraday" control={state?.control} onApplied={() => { refresh(); go("/setup"); }} />}
      {current === "/lab/results" && <PerformanceView defaultMode={state?.control.heartbeat?.mode ?? "paper"} />}
    </div>
  );
}

const VERDICT_WORD: Record<GateRole["verdict"], string> = {
  proven: "Proven to help", inconclusive: "Not settled yet", drag: "A net drag", too_few: "Too few checks",
};

function Gates({ go }: { go: (to: string) => void }) {
  const gates = usePoll<GatesState>("/api/gates", 20000);
  const roles = gates.data?.roles ?? [];
  if (gates.error && !gates.data) {
    return <Empty title="No gate results yet.">The worker publishes them after its next pass. ({gates.error})</Empty>;
  }
  if (!roles.length) {
    return (
      <Empty title="No model role has been scored yet.">
        Once an LLM is connected, every answer it gives is scored against the same setup with the model left out. The result appears here after the first few setups have run their course.
      </Empty>
    );
  }
  const span = Math.max(0.25, ...roles.flatMap((r) => [Math.abs(r.lower ?? 0), Math.abs(r.upper ?? 0), Math.abs(r.mean ?? 0)])) * 1.15;
  return (
    <div className="page" style={{ gap: 36 }}>
      <section className="section">
        <div className="section-head"><h2>Does each model role earn its place?</h2><p>Each answer against the same setup with the model left out, after charges and the cost of the call</p></div>
        <div className="gatestrip">
          {roles.map((r) => <GateRow key={`${r.role}-${r.harness_id}`} r={r} span={span} />)}
          <div className="gate-axis" aria-hidden><span style={{ left: "0%" }}>{signed(-span, 2)}R</span><span style={{ left: "50%" }}>no model</span><span style={{ left: "100%" }}>{signed(span, 2)}R</span></div>
        </div>
        <p className="small soft" style={{ maxWidth: "74ch", marginTop: 14 }}>
          The bar is the range the true effect per setup is in, 95% of the time, and it stays valid however often you look. A role gets authority only when the whole bar is right of the line
          and it has been checked enough times. If the whole bar falls left of the line, it goes back to watching. While a role is watching, it is asked and its answer is recorded, but nothing it says is applied.
          {gates.data?.note ? ` ${gates.data.note}` : ""}
        </p>
        <p className="small" style={{ marginTop: 10 }}>
          <a href="/harness" onClick={(e) => { e.preventDefault(); go("/harness"); }}>See each role&apos;s prompt and rules in the Harness</a>
        </p>
      </section>
    </div>
  );
}

function GateRow({ r, span }: { r: GateRole; span: number }) {
  const x = (v: number) => `${((Math.max(-span, Math.min(span, v)) + span) / (2 * span)) * 100}%`;
  const has = r.lower !== null && r.upper !== null && r.mean !== null;
  return (
    <div className={`gate-row ${r.verdict}`}>
      <div className="who">
        <b>{r.label}</b>
        <span>{r.stage === "active" ? "Has authority" : "Watching only"}, {r.n} of {r.n_min} checks{r.harness_id ? `, harness ${r.harness_id.slice(0, 7)}` : ""}</span>
      </div>
      <div className="plot" role="img" aria-label={has ? `Effect per setup between ${signed(r.lower, 2)}R and ${signed(r.upper, 2)}R, best estimate ${signed(r.mean, 2)}R` : "No estimate yet"}>
        <span className="zero" />
        {has && <span className="ci" style={{ left: x(r.lower!), width: `calc(${x(r.upper!)} - ${x(r.lower!)})` }} />}
        {has && <span className="pt" style={{ left: x(r.mean!) }} />}
      </div>
      <div className="says">
        <b>{VERDICT_WORD[r.verdict]}</b>
        <span>{r.verdict_text}</span>
      </div>
    </div>
  );
}
