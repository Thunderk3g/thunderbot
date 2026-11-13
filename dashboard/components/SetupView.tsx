"use client";

import { ChevronDown, LoaderCircle } from "lucide-react";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { dayTime } from "@/lib/format";
import type { GrowwCheck, SetupState } from "@/lib/setup";
import type { Control } from "@/lib/types";
import { post, wakeWorker } from "@/lib/usePoll";
import type { SysNode } from "./App";
import { Line, type Gate } from "./Line";
import SettingsView from "./SettingsView";
import { Button } from "./ui";

type Go = (page: "lab" | "today" | "guide") => void;
type StationId = "worker" | "prices" | "llm" | "groww" | "orders";

const STATUS_WORD: Record<SysNode["tone"], string> = { on: "Connected", off: "Not connected", bad: "Needs attention" };

export default function SetupView({ control, setup, setupError, nodes, refresh, go }: {
  control?: Control; setup: SetupState | null; setupError: string | null; nodes: SysNode[]; refresh: () => void; go?: Go;
}) {
  const [open, setOpen] = useState<StationId | null>(null);
  const decided = useRef(false);
  // Open the first thing that still needs the owner, once, when the state first loads. After that the
  // owner is in charge of what is open, so saving a key never closes the panel they are reading.
  useEffect(() => {
    if (decided.current || !setup) return;
    decided.current = true;
    setOpen(!setup.llm.configured ? "llm" : !setup.groww.configured ? "groww" : null);
  }, [setup]);
  const toggle = (id: StationId) => { decided.current = true; setOpen(open === id ? null : id); };
  const byKey = Object.fromEntries(nodes.map((n) => [n.key, n])) as Record<StationId, SysNode>;

  const gates: Gate[] = (["prices", "llm", "groww"] as const).map((k) => ({
    key: k, label: byKey[k].name, value: byKey[k].note,
    state: byKey[k].tone === "on" ? "pass" : byKey[k].tone === "bad" ? "cut" : "absent",
  }));
  const hb = control?.heartbeat;

  return (
    <div className="page">
      <div className="page-head">
        <div>
          <h1>Setup</h1>
          <p className="lede">Bring your own keys. Everything here belongs to this copy of Thunderbot and nobody else&apos;s: your scheduler, your LLM, your Groww account.</p>
        </div>
      </div>

      <section aria-label="What is connected">
        <div className="stage" style={{ paddingTop: 0 }}>
          <Line size="lg" label="What is connected, in order"
            source={{ label: byKey.worker.name, value: byKey.worker.note }} gates={gates}
            end={{ label: byKey.orders.name, value: byKey.orders.note }} />
        </div>
        <p className="small soft" style={{ maxWidth: "70ch", marginTop: 10 }}>
          Read it left to right: something wakes the worker, it fetches prices, an LLM may weigh in, a broker may be connected, and orders come out the end.
          An empty holder means that part is optional and not fitted. A broken switch means it is fitted and failing.
        </p>
      </section>

      {setupError && !setup && (
        <div className="notice stop"><span className="grow">The setup screen couldn&apos;t load its state: {setupError}.</span></div>
      )}
      {setup && !setup.store.ready && (
        <div className="notice caution"><span className="grow">Keys can&apos;t be saved from this screen yet: {setup.store.problem ?? "no secret key is configured"}. Keys set in the worker&apos;s environment still work.</span></div>
      )}

      <div className="stations">
        <Station id="worker" node={byKey.worker} open={open} toggle={toggle} blurb="Wakes the worker every few minutes in market hours">
          <p>{hb?.scheduler === "serverless"
            ? "Nothing runs all day. A timer in your database calls a small function, which does one pass and exits. If a call is missed, the next one catches up."
            : hb ? "A long-running worker on your own machine reports in every few seconds." : "Nothing has reported in yet. Wake the worker once; after that the scheduler calls it by itself."}</p>
          <WakeNow refresh={refresh} />
          <p className="small soft">Setting up the timer is covered in <code>docs/no-server.md</code>.</p>
        </Station>

        <Station id="prices" node={byKey.prices} open={open} toggle={toggle} blurb="Where the bot reads prices from">
          <p>{hb?.feed?.source === "groww"
            ? "Prices come from Groww's own feed, using your key."
            : "Prices come from Yahoo Finance, which is free and can lag the exchange by a few minutes. That is fine for a decision made once a day; it flatters intraday paper results."}</p>
          {hb?.feed && !hb.feed.ok && <div className="notice stop"><span className="grow">{hb.feed.message}</span></div>}
          <p className="small soft">With a Groww key connected below, set <code>TB_FEED=groww</code> where the worker runs to use Groww&apos;s prices and history instead.</p>
        </Station>

        <Station id="llm" node={byKey.llm} open={open} toggle={toggle} blurb="Optional. It can skip, shrink or postpone a trade; it can never make one">
          {setup ? <LlmForm setup={setup} refresh={refresh} /> : <p className="soft">Loading.</p>}
        </Station>

        <Station id="groww" node={byKey.groww} open={open} toggle={toggle} blurb="Optional. Needed for Groww's prices and, one day, real orders">
          {setup ? <GrowwForm setup={setup} refresh={refresh} /> : <p className="soft">Loading.</p>}
        </Station>

        <Station id="orders" node={byKey.orders} open={open} toggle={toggle} blurb="On paper until you decide otherwise, on your own machine">
          <p>Orders are simulated at live prices with Groww&apos;s charges taken off. Real orders are switched on in one place only: the machine whose static IP is registered with Groww. Nothing on this screen can do it, so a stolen dashboard password cannot trade your account.</p>
          <ul className="steps-list">
            <li className={setup?.groww.lastCheck?.ok ? "ok" : ""}><span><b>A Groww key that passes its check.</b> <span>{setup?.groww.lastCheck?.ok ? "Done." : "Connect it above."}</span></span></li>
            <li className={setup?.groww.lastCheck?.ip?.ok ? "ok" : ""}><span><b>That machine&apos;s IP registered with Groww.</b> <span>{setup?.live.staticIp ? `Expected ${setup.live.staticIp}.` : "Set TB_EXPECTED_STATIC_IP there."}</span></span></li>
            <li className={setup?.live.enabled ? "ok" : ""}><span><b>The live switch, set there.</b> <span><code>TB_LIVE_TRADING_ENABLED=true</code> in that machine&apos;s environment.</span></span></li>
            <li><span><b>The command, typed by you.</b> <span><code>thunderbot invest --live --i-understand-the-risks</code></span></span></li>
          </ul>
          <p className="small soft">Before any of that: the plan should have earned it on paper. The Guide explains what to look for.{" "}
            <button type="button" onClick={() => go?.("guide")} style={{ border: 0, background: "none", padding: 0, cursor: "pointer", textDecoration: "underline", color: "inherit", font: "inherit" }}>Open the Guide</button></p>
        </Station>
      </div>

      <SettingsView control={control} refresh={refresh} go={go} />
    </div>
  );
}

function Station({ id, node, open, toggle, blurb, children }: {
  id: StationId; node: SysNode; open: StationId | null; toggle: (id: StationId) => void; blurb: string; children: ReactNode;
}) {
  const isOpen = open === id;
  return (
    <section className={`station ${node.tone} ${isOpen ? "open" : ""}`}>
      <button type="button" aria-expanded={isOpen} onClick={() => toggle(id)}>
        <i className="node" aria-hidden />
        <span className="name"><b>{node.name}</b><span>{blurb}</span></span>
        <span className="status">{node.tone === "on" ? node.note : STATUS_WORD[node.tone]}</span>
        <ChevronDown size={16} className="chev" aria-hidden />
      </button>
      {isOpen && <div className="station-body">{children}</div>}
    </section>
  );
}

function WakeNow({ refresh }: { refresh: () => void }) {
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState<string | null>(null);
  const go = async () => {
    setBusy(true);
    setNote(null);
    try { const r = await wakeWorker(); setNote(r.did ? `Done: ${r.did}.` : "Done."); refresh(); }
    catch (e) { setNote(e instanceof Error ? e.message : String(e)); }
    setBusy(false);
  };
  return (
    <div className="btn-row">
      <Button onClick={go} disabled={busy}>{busy && <LoaderCircle size={14} className="spin" />}Wake the worker now</Button>
      {note && <span className="small soft" role="status">{note}</span>}
    </div>
  );
}

type Result = { kind: "good" | "stop" | "info"; text: string } | null;

function LlmForm({ setup, refresh }: { setup: SetupState; refresh: () => void }) {
  const llm = setup.llm;
  const [preset, setPreset] = useState(llm.preset ?? "groq");
  const info = setup.providers.find((p) => p.id === preset) ?? setup.providers[0];
  const [baseUrl, setBaseUrl] = useState(llm.preset === "custom" ? llm.baseUrl ?? "" : "");
  const [apiKey, setApiKey] = useState("");
  const [models, setModels] = useState<string[]>([]);
  const [model, setModel] = useState(llm.model ?? "");
  const [busy, setBusy] = useState<"check" | "save" | "clear" | null>(null);
  const [result, setResult] = useState<Result>(null);
  const samePreset = llm.configured && llm.source === "dashboard" && llm.preset === preset;
  const canUseStored = samePreset && !apiKey;
  const ready = setup.store.ready;

  const choose = (id: string) => { setPreset(id); setModels([]); setResult(null); if (id !== llm.preset) setModel(""); };
  const body = () => ({ preset, ...(preset === "custom" ? { baseUrl } : {}), ...(apiKey ? { apiKey } : {}) });
  const check = async () => {
    setBusy("check");
    setResult(null);
    try {
      const r = await post<{ ok: boolean; models: string[]; message: string }>("/api/setup", { action: "check_llm", ...body() });
      if (!r.ok) throw new Error(r.message);
      setModels(r.models);
      if (!model || !r.models.includes(model)) setModel(r.models.includes(llm.model ?? "") ? llm.model! : r.models[0] ?? "");
      setResult({ kind: "good", text: `The key works. ${r.models.length} models are available; pick one.` });
    } catch (e) { setResult({ kind: "stop", text: e instanceof Error ? e.message : String(e) }); }
    setBusy(null);
  };
  const save = async () => {
    setBusy("save");
    setResult(null);
    try {
      const r = await post<{ ok: boolean; reply?: string; latencyMs?: number; message: string }>("/api/setup", { action: "save_llm", ...body(), model });
      if (!r.ok) throw new Error(r.message);
      setApiKey("");
      setResult({ kind: "good", text: `Saved. ${model} answered in ${r.latencyMs ?? "?"} ms. The worker uses it from its next pass.` });
      refresh();
    } catch (e) { setResult({ kind: "stop", text: e instanceof Error ? e.message : String(e) }); }
    setBusy(null);
  };
  const clear = async () => {
    setBusy("clear");
    try { await post("/api/setup", { action: "clear_llm" }); setModels([]); setModel(""); setResult({ kind: "info", text: "Removed. The rules now run by themselves." }); refresh(); }
    catch (e) { setResult({ kind: "stop", text: e instanceof Error ? e.message : String(e) }); }
    setBusy(null);
  };

  return (
    <>
      {llm.configured && (
        <p>
          Connected to <b>{llm.provider}</b> with <b>{llm.model}</b>
          {llm.source === "dashboard" ? <>, key {llm.hint}, saved {llm.updatedAt ? dayTime(llm.updatedAt) : "earlier"}.</> : <>, from the worker&apos;s environment. A key saved here takes its place.</>}
          {!llm.enabled && " It is switched off in the limits below."}
        </p>
      )}
      <div className="field">
        <span className="field-label">Provider</span>
        <div className="providers" role="group" aria-label="LLM provider">
          {setup.providers.map((p) => <button key={p.id} type="button" aria-pressed={p.id === preset} onClick={() => choose(p.id)}>{p.label}</button>)}
        </div>
        {info.note && <span className="hint">{info.note}</span>}
      </div>
      {preset === "custom" && (
        <div className="field">
          <label htmlFor="llm-base">Base URL</label>
          <input id="llm-base" className="input key" placeholder="https://your-server/v1" value={baseUrl} onChange={(e) => setBaseUrl(e.target.value)} spellCheck={false} autoComplete="off" />
        </div>
      )}
      <div className="field">
        <label htmlFor="llm-key"><span>API key</span>
          {info.keyUrl && <a className="hint" href={info.keyUrl} target="_blank" rel="noreferrer">Get one from {info.label.replace(/ \(.*/, "")}</a>}</label>
        <div className="key-row">
          <input id="llm-key" className="input key" type="password" placeholder={canUseStored ? `Saved (${llm.hint}). Paste a new key to replace it` : info.keyHint || "Paste the key"}
            value={apiKey} onChange={(e) => setApiKey(e.target.value.trim())} spellCheck={false} autoComplete="off" disabled={!ready} />
          <Button onClick={check} disabled={busy !== null || !ready || (!apiKey && !canUseStored) || (preset === "custom" && !baseUrl)}>
            {busy === "check" && <LoaderCircle size={14} className="spin" />}Check key
          </Button>
        </div>
        <span className="hint">Checked against the provider, then stored encrypted in your own database. It is never shown again and never sent anywhere else.</span>
      </div>
      {(models.length > 0 || model) && (
        <div className="field">
          <label htmlFor="llm-model">Model</label>
          {models.length > 0
            ? <select id="llm-model" className="input" value={model} onChange={(e) => setModel(e.target.value)}>{models.map((m) => <option key={m} value={m}>{m}</option>)}</select>
            : <input id="llm-model" className="input" value={model} onChange={(e) => setModel(e.target.value)} spellCheck={false} />}
          <span className="hint">The list comes from the provider. Whatever model answers is recorded with every decision it makes.</span>
        </div>
      )}
      {result && <div className={`notice ${result.kind}`} role="status"><span className="grow">{result.text}</span></div>}
      <div className="btn-row">
        <Button variant="primary" onClick={save} disabled={busy !== null || !ready || !model || (!apiKey && !canUseStored)}>
          {busy === "save" && <LoaderCircle size={14} className="spin" />}Save and test
        </Button>
        {llm.source === "dashboard" && <Button variant="quiet" onClick={clear} disabled={busy !== null}>Remove this key</Button>}
      </div>
    </>
  );
}

function GrowwForm({ setup, refresh }: { setup: SetupState; refresh: () => void }) {
  const g = setup.groww;
  const [apiKey, setApiKey] = useState("");
  const [totp, setTotp] = useState("");
  const [secret, setSecret] = useState("");
  const [approval, setApproval] = useState(g.auth === "approval");
  const [busy, setBusy] = useState<"save" | "check" | "clear" | null>(null);
  const [result, setResult] = useState<Result>(null);
  const [fresh, setFresh] = useState<GrowwCheck | null>(null);
  const ready = setup.store.ready;
  const last = fresh ?? g.lastCheck;

  const follow = async (jobId: string) => {
    void fetch(`/api/worker?op=job&id=${encodeURIComponent(jobId)}`, { method: "POST" }).catch(() => undefined);
    for (let i = 0; i < 45; i++) {
      await new Promise((r) => setTimeout(r, 1500));
      const res = await fetch(`/api/jobs?id=${encodeURIComponent(jobId)}`, { cache: "no-store" });
      const job = (await res.json()) as { status: string; result?: GrowwCheck | null; error?: string | null };
      if (job.status === "done" && job.result) return job.result;
      if (job.status === "error") throw new Error(job.error ?? "the check failed");
    }
    throw new Error("the worker has not picked the check up yet. Wake it from Scheduler above, then check again");
  };
  const run = async (which: "save" | "check") => {
    setBusy(which);
    setResult(null);
    try {
      const r = await post<{ ok: boolean; jobId: string; message?: string }>("/api/setup",
        which === "save" ? { action: "save_groww", apiKey, ...(approval ? { apiSecret: secret } : { totpSecret: totp }) } : { action: "check_groww" });
      if (which === "save") { setApiKey(""); setTotp(""); setSecret(""); refresh(); }
      setResult({ kind: "info", text: which === "save" ? "Saved. Checking the login now; this takes a few seconds." : "Checking the login now." });
      const check = await follow(r.jobId);
      setFresh(check);
      setResult(check.ok ? { kind: "good", text: "Groww accepted the login." } : { kind: "stop", text: "The check did not pass. See the steps below." });
      refresh();
    } catch (e) { setResult({ kind: "stop", text: e instanceof Error ? e.message : String(e) }); }
    setBusy(null);
  };
  const clear = async () => {
    setBusy("clear");
    try { await post("/api/setup", { action: "clear_groww" }); setFresh(null); setResult({ kind: "info", text: "Removed." }); refresh(); }
    catch (e) { setResult({ kind: "stop", text: e instanceof Error ? e.message : String(e) }); }
    setBusy(null);
  };

  return (
    <>
      <p>
        {g.configured
          ? <>Connected{g.source === "dashboard" ? <>, key {g.hint}, saved {g.updatedAt ? dayTime(g.updatedAt) : "earlier"}</> : " from the worker's environment"}. </>
          : "Create an API key on Groww's Trade API page and paste it here. "}
        It is used to read prices and history and to check that the login works. It cannot place a real order from here: see Paper orders below.
      </p>
      <div className="field">
        <label htmlFor="gw-key"><span>API key</span><a className="hint" href="https://groww.in/trade-api/api-keys" target="_blank" rel="noreferrer">Create one on Groww</a></label>
        <input id="gw-key" className="input key" type="password" placeholder={g.configured && g.source === "dashboard" ? `Saved (${g.hint}). Paste a new key to replace it` : "Starts with eyJ…"}
          value={apiKey} onChange={(e) => setApiKey(e.target.value.trim())} spellCheck={false} autoComplete="off" disabled={!ready} />
      </div>
      {approval ? (
        <div className="field">
          <label htmlFor="gw-secret">API secret</label>
          <input id="gw-secret" className="input key" type="password" value={secret} onChange={(e) => setSecret(e.target.value.trim())} spellCheck={false} autoComplete="off" disabled={!ready} />
          <span className="hint">This kind of key has to be approved on Groww&apos;s site each morning before it works.</span>
        </div>
      ) : (
        <div className="field">
          <label htmlFor="gw-totp">TOTP secret</label>
          <input id="gw-totp" className="input key" type="password" placeholder="The long code shown once when you create a TOTP key" value={totp}
            onChange={(e) => setTotp(e.target.value.replace(/\s/g, ""))} spellCheck={false} autoComplete="off" disabled={!ready} />
          <span className="hint">The secret behind the six-digit codes, not a code itself. With it the bot can log in each morning without you.</span>
        </div>
      )}
      <label className="small" style={{ display: "inline-flex", gap: 8, alignItems: "center", cursor: "pointer" }}>
        <input type="checkbox" checked={approval} onChange={(e) => setApproval(e.target.checked)} />My key uses daily approval, not TOTP
      </label>
      {result && <div className={`notice ${result.kind}`} role="status"><span className="grow">{busy && <LoaderCircle size={14} className="spin" style={{ verticalAlign: -2, marginRight: 8 }} />}{result.text}</span></div>}
      {last && (
        <div>
          <p className="small soft" style={{ marginBottom: 4 }}>Last check, {dayTime(last.at)}</p>
          <ul className="steps-list">
            {last.steps.map((s) => <li key={s.name} className={s.ok ? "ok" : "bad"}><span><b>{s.name}.</b> <span>{s.detail}</span></span></li>)}
            {last.ip && <li className={last.ip.ok ? "ok" : ""}><span><b>Static IP.</b> <span>{last.ip.expected ? `This worker's address is ${last.ip.observed ?? "unknown"}; ${last.ip.ok ? "it matches" : `the registered one is ${last.ip.expected}`}.` : `This worker's address is ${last.ip.observed ?? "unknown"}. No registered address is set, which only matters for real orders.`}</span></span></li>}
          </ul>
        </div>
      )}
      <div className="btn-row">
        <Button variant="primary" onClick={() => run("save")} disabled={busy !== null || !ready || !apiKey || (approval ? !secret : !totp)}>
          {busy === "save" && <LoaderCircle size={14} className="spin" />}Save and check
        </Button>
        {g.configured && <Button onClick={() => run("check")} disabled={busy !== null}>{busy === "check" && <LoaderCircle size={14} className="spin" />}Check again</Button>}
        {g.source === "dashboard" && <Button variant="quiet" onClick={clear} disabled={busy !== null}>Remove this key</Button>}
      </div>
      <p className="small soft">Stored encrypted in your own database. A stored key and TOTP secret together can log in to your account, so keep this dashboard&apos;s password strong and private.</p>
    </>
  );
}
