"use client";

import type { LiveState } from "@/lib/types";
import LabView from "./LabView";
import LiveView from "./LiveView";
import { Tabs } from "./ui";

/** The portfolio and the plan that runs it are one place: what you hold, and the rule that decides it. */
export default function PortfolioView({ state, act, refresh, go, tab, llmOn }: {
  state: LiveState | null; act: (action: string, extra?: Record<string, unknown>) => Promise<void>; refresh: () => void;
  go: (to: string) => void; tab: "holdings" | "plan"; llmOn: boolean;
}) {
  const invest = state?.control.heartbeat?.style === "invest";
  return (
    <div>
      {(invest || tab === "plan") && (
        <Tabs go={go} current={tab === "plan" ? "/portfolio/plan" : "/"} items={[{ href: "/", label: "Holdings" }, { href: "/portfolio/plan", label: "Plan" }]} />
      )}
      {tab === "plan"
        ? <LabView only="invest" control={state?.control} onApplied={() => { refresh(); go("/setup"); }} onUsed={() => { refresh(); go("/"); }} />
        : <LiveView state={state} act={act} refresh={refresh} go={go} llmOn={llmOn} />}
    </div>
  );
}
