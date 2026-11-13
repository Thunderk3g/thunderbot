"use client";

import { ChevronDown } from "lucide-react";
import { useState } from "react";
import { dayTime } from "@/lib/format";
import type { HarnessFile, HarnessState } from "@/lib/harness";
import { usePoll } from "@/lib/usePoll";
import { Empty } from "./ui";

const KIND: Record<HarnessFile["kind"], string> = { policy: "Policy", plan: "Plan", role: "Role", prompt: "Prompt", gates: "Gates" };
const MAY: Record<string, string> = { veto: "say no", shrink: "say no, or less", postpone: "hold it a day" };

/** The harness: everything that shapes a decision and is not the engine, as files you can read. */
export default function HarnessView({ go }: { go: (to: string) => void }) {
  const h = usePoll<HarnessState>("/api/harness", 30000);
  const [open, setOpen] = useState<string | null>(null);
  if (!h.data) {
    return (
      <div className="page">
        <div><h1>Harness</h1><p className="lede">Everything that shapes a decision and is not the engine: your limits, the plan, each model role and its prompt, and the tests a role must pass.</p></div>
        <Empty title={h.error ? "The harness has not been published yet." : "Loading."}>{h.error ? `The worker publishes it on its next pass. (${h.error})` : ""}</Empty>
      </div>
    );
  }
  const d = h.data;
  return (
    <div className="page">
      <div>
        <h1>Harness</h1>
        <p className="lede">
          Everything that shapes a decision and is not the engine. Change a file and the harness gets a new id, so the journal can tell which rules made which decision.
          Editing the harness changes what is proposed. It cannot change what the engine allows.
        </p>
      </div>

      {!d.valid && (
        <div className="notice stop" style={{ alignItems: "flex-start" }}>
          <span className="grow">This harness did not pass its checks, so the built-in one is in use: {d.problems.join("; ")}.</span>
        </div>
      )}

      <dl className="reads">
        <div><dt>In use</dt><dd className="tnum">{d.id}<small>{d.source === "directory" ? d.path : "the built-in harness"}</small></dd></div>
        <div><dt>Loaded</dt><dd>{d.loaded_at ? dayTime(d.loaded_at) : "–"}<small>{d.valid ? "passed every check" : "failed its checks"}</small></dd></div>
        <div><dt>Model memory</dt><dd>{d.memory_mode === "inject" ? "Fed back in" : "Written down only"}
          <small>{d.memory_mode === "inject" ? "yesterday's lessons go into today's prompt" : "lessons are kept for you to read, not shown to the model"}</small></dd></div>
        <div><dt>Earlier versions</dt><dd>{d.previous_ids.length}<small>{d.previous_ids.length ? `last ${d.previous_ids[0].id.slice(0, 7)}, ${d.previous_ids[0].decisions} decisions` : "this is the first"}</small></dd></div>
      </dl>

      <section className="section">
        <div className="section-head"><h2>Model roles</h2><p>What each one is for, the most it can do, and whether it has earned the right to do it</p></div>
        <div className="table-wrap"><table>
          <thead><tr><th>Role</th><th>The most it can do</th><th>If it fails</th><th>Standing</th></tr></thead>
          <tbody>{d.roles.map((r) => (
            <tr key={r.name}>
              <td style={{ whiteSpace: "normal", minWidth: 220 }}><b>{r.label}</b><span className="soft small" style={{ display: "block", maxWidth: "46ch" }}>{r.purpose}</span></td>
              <td>{MAY[r.may] ?? r.may}</td>
              <td style={{ whiteSpace: "normal", maxWidth: 220 }}>{r.on_failure}</td>
              <td>{r.stage === "active" ? <span className="tag use">Has authority</span> : <span className="tag">Watching only</span>}
                {!r.scored && <span className="soft small" style={{ display: "block" }}>not scored in R</span>}</td>
            </tr>
          ))}</tbody>
        </table></div>
        <p className="small" style={{ marginTop: 12 }}><a href="/lab" onClick={(e) => { e.preventDefault(); go("/lab"); }}>See how each role is doing in the Lab</a></p>
      </section>

      <section className="section">
        <div className="section-head"><h2>The files</h2><p>{d.source === "directory" ? `Edit them in ${d.path}` : "Copy them out and set TB_HARNESS_DIR to edit them"}</p></div>
        <div className="files">
          {d.files.map((f) => (
            <div key={f.path} className={`file ${open === f.path ? "open" : ""}`}>
              <button type="button" aria-expanded={open === f.path} onClick={() => setOpen(open === f.path ? null : f.path)}>
                <span className="tag">{KIND[f.kind]}</span><code>{f.path}</code><span className="soft small tnum">{f.digest.slice(0, 7)}</span><ChevronDown size={16} className="chev" aria-hidden />
              </button>
              {open === f.path && <pre>{f.text}</pre>}
            </div>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="section-head"><h2>Ceilings no file can raise</h2><p>Set in the engine&apos;s code</p></div>
        <dl className="facts">
          {Object.entries(d.ceilings).map(([k, v]) => [<dt key={`${k}t`}>{k.replaceAll("_", " ")}</dt>, <dd key={`${k}d`} className="tnum">{String(v)}</dd>])}
        </dl>
      </section>
    </div>
  );
}
