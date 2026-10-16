"use client";

import { AnimatePresence, motion } from "motion/react";
import { Bot, Check, CircleAlert, Clock, Gauge, Lock, LoaderCircle, RotateCcw, ShieldCheck, Sparkles } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import type { Control, EffectiveSettings } from "@/lib/types";
import { post } from "@/lib/usePoll";
import { Badge, Button, Card, ChipsInput, Empty, Segmented, SliderField, Switch, fadeUp } from "./ui";

type Editable = EffectiveSettings["editable"];

export default function SettingsView({ control, refresh }: { control?: Control; refresh: () => void }) {
  const eff = control?.effective_settings;
  const catalog = control?.strategy_catalog ?? [];
  const [draft, setDraft] = useState<Editable | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [savedAt, setSavedAt] = useState<number | null>(null);

  const baseline = useMemo(() => (eff ? { ...eff.editable } : null), [eff]);
  useEffect(() => {
    if (baseline && !draft) setDraft(baseline);
  }, [baseline, draft]);

  if (!eff || !draft || !baseline) {
    return <div className="card"><Empty icon={<Gauge size={28} />} title="Settings not available yet" hint="The worker publishes its effective settings when it starts." /></div>;
  }

  const dirty = JSON.stringify(draft) !== JSON.stringify(baseline);
  const set = <K extends keyof Editable>(k: K, v: Editable[K]) => setDraft({ ...draft, [k]: v });
  const b = (k: string) => eff.bounds[k] ?? { min: 0, max: 100 };
  const info = catalog.find((s) => s.name === draft.strategy);

  const overrides = (control?.settings_overrides ?? {}) as Record<string, unknown>;
  const pending = Object.entries(overrides).some(([k, v]) => !(k in eff.rejected) && JSON.stringify(v) !== JSON.stringify((eff.editable as Record<string, unknown>)[k]));

  const save = async () => {
    setSaving(true);
    setError(null);
    try {
      await post("/api/settings", { overrides: draft });
      setSavedAt(Date.now());
      refresh();
      setDraft(null); // re-sync from the worker's effective settings
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setSaving(false);
    }
  };

  const reset = async () => {
    await post("/api/settings", { overrides: {} });
    refresh();
    setDraft(null);
  };

  return (
    <div className="grid">
      <AnimatePresence initial={false}>
        {pending && <motion.div key="pending" {...fadeUp} className="banner info"><LoaderCircle size={15} className="spin" /><span className="grow">Saved. Waiting for the worker to apply on its next tick…</span></motion.div>}
        {!pending && savedAt && Date.now() - savedAt < 15_000 && <motion.div key="ok" {...fadeUp} className="banner info"><Check size={15} /><span className="grow">Applied by the worker.</span></motion.div>}
        {Object.keys(eff.rejected).length > 0 && (
          <motion.div key="rej" {...fadeUp} className="banner warn"><CircleAlert size={15} />
            <span className="grow">Worker rejected: {Object.entries(eff.rejected).map(([k, v]) => `${k} (${v})`).join("; ")}</span>
          </motion.div>
        )}
        {error && <motion.div key="err" {...fadeUp} className="banner bad"><CircleAlert size={15} /><span className="grow">{error}</span></motion.div>}
      </AnimatePresence>

      <div className="grid cols-2">
        <Card title="Strategy" icon={<Sparkles size={15} />}>
          <div className="form">
            <div className="field">
              <label>Active strategy</label>
              <select className="input" value={draft.strategy} onChange={(e) => {
                const next = catalog.find((s) => s.name === e.target.value);
                setDraft({ ...draft, strategy: e.target.value, strategy_params: Object.fromEntries((next?.params ?? []).map((p) => [p.name, p.default])) });
              }}>
                {catalog.map((s) => <option key={s.name} value={s.name}>{s.label}</option>)}
              </select>
              {info && <span className="subtle">{info.description}</span>}
            </div>
            {info?.params.map((p) => (
              <SliderField key={p.name} label={p.label} min={p.min} max={p.max} step={p.step}
                value={draft.strategy_params[p.name] ?? p.default}
                onChange={(v) => set("strategy_params", { ...draft.strategy_params, [p.name]: v })} />
            ))}
          </div>
        </Card>

        <Card title="Capital & risk" icon={<ShieldCheck size={15} />} delay={0.05}>
          <div className="form">
            <div className="field">
              <label>Capital (₹)</label>
              <input className="input" inputMode="numeric" value={draft.capital} onChange={(e) => set("capital", Number(e.target.value.replace(/[^\d.]/g, "")) || 0)} />
            </div>
            <SliderField label="Risk per trade" suffix="%" min={b("risk_per_trade_pct").min ?? 0.05} max={b("risk_per_trade_pct").max ?? 2} step={0.05}
              value={draft.risk_per_trade_pct} onChange={(v) => set("risk_per_trade_pct", v)}
              hint={`≈ ₹${Math.round((draft.capital * draft.risk_per_trade_pct) / 100).toLocaleString("en-IN")} per trade`} />
            <SliderField label="Daily loss limit" suffix="%" min={b("max_daily_loss_pct").min ?? 0.1} max={b("max_daily_loss_pct").max ?? 10} step={0.1}
              value={draft.max_daily_loss_pct} onChange={(v) => set("max_daily_loss_pct", v)} hint="halts and flattens for the day" />
            <SliderField label="Max open positions" min={1} max={20} step={1} value={draft.max_open_positions} onChange={(v) => set("max_open_positions", v)} />
            <SliderField label="Max trades per day" min={1} max={50} step={1} value={draft.max_trades_per_day} onChange={(v) => set("max_trades_per_day", v)} />
            <SliderField label="Intraday leverage" suffix="x" min={b("max_leverage").min ?? 0.1} max={b("max_leverage").max ?? 5} step={0.1}
              value={draft.max_leverage} onChange={(v) => set("max_leverage", v)} hint={`hard cap ${eff.hard_ceilings.max_leverage}x`} />
            <SliderField label="Max size per position" suffix="%" min={1} max={100} step={1} value={draft.max_position_notional_pct} onChange={(v) => set("max_position_notional_pct", v)} />
            <SliderField label="Widest allowed stop" suffix="%" min={0.1} max={10} step={0.1} value={draft.max_stop_distance_pct} onChange={(v) => set("max_stop_distance_pct", v)} />
            <div className="toggle-row"><span className="field-label">Allow intraday shorts</span><Switch checked={draft.allow_short} onChange={(v) => set("allow_short", v)} label="Allow shorts" /></div>
          </div>
        </Card>

        <Card title="Universe & timing" icon={<Clock size={15} />} delay={0.1}>
          <div className="form">
            <div className="field"><label>Symbols (NSE)</label><ChipsInput values={draft.symbols} onChange={(v) => set("symbols", v)} placeholder="add symbol" /></div>
            <div className="time-grid">
              <div className="field"><label>Entries from</label><input type="time" className="input" value={draft.entry_start} onChange={(e) => set("entry_start", e.target.value)} /></div>
              <div className="field"><label>Entries until</label><input type="time" className="input" value={draft.entry_end} onChange={(e) => set("entry_end", e.target.value)} /></div>
              <div className="field"><label>Flatten at</label><input type="time" className="input" max={String(eff.hard_ceilings.latest_flatten)} value={draft.flatten_at} onChange={(e) => set("flatten_at", e.target.value)} /></div>
            </div>
            <SliderField label="Price protection band" suffix="%" min={0.05} max={3} step={0.05} value={draft.price_protection_pct}
              onChange={(v) => set("price_protection_pct", v)} hint="limit price offset instead of market orders" />
          </div>
        </Card>

        <Card title="Signal reviewer" icon={<Bot size={15} />} delay={0.15}>
          <div className="form">
            <div className="toggle-row">
              <div><div className="field-label">Claude review</div><div className="subtle">{eff.env_only.llm_model}. Can veto or shrink a signal, never enlarge it.</div></div>
              <Switch checked={draft.llm_enabled} onChange={(v) => set("llm_enabled", v)} label="Claude review" />
            </div>
            <AnimatePresence initial={false}>
              {draft.llm_enabled && (
                <motion.div className="form" initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} style={{ overflow: "hidden" }}>
                  <div className="field"><label>Effort</label>
                    <Segmented value={draft.llm_effort} onChange={(v) => set("llm_effort", v)} options={eff.llm_efforts.map((e) => ({ value: e, label: e }))} />
                  </div>
                  <div className="field"><label>If the review fails</label>
                    <Segmented value={draft.llm_fail_mode} onChange={(v) => set("llm_fail_mode", v)} options={[{ value: "reject", label: "Skip the trade" }, { value: "pass", label: "Trade anyway" }]} />
                  </div>
                  <SliderField label="Minimum confidence to approve" min={0} max={1} step={0.05} value={draft.llm_min_confidence} onChange={(v) => set("llm_min_confidence", v)} />
                </motion.div>
              )}
            </AnimatePresence>
            <div className="note">Judge the reviewer on the Performance tab. Every signal&apos;s outcome is tracked, so you can see whether vetoed trades really did worse.</div>
          </div>
        </Card>
      </div>

      <Card title="Locked on the worker" icon={<Lock size={15} />} delay={0.2}
        action={<Button size="sm" variant="ghost" onClick={reset}><RotateCcw size={14} />Reset to worker defaults</Button>}>
        <div className="grid cols-3">
          <Locked label="Live trading" on={eff.env_only.live_trading_enabled} />
          <Locked label="MTF orders via API" on={eff.env_only.allow_mtf_api} />
          <Locked label="Daily login confirmation" on={eff.env_only.require_login_confirmation} />
          <Locked label="Static IP check configured" on={eff.env_only.static_ip_configured} />
          <Locked label="Groww credentials" on={eff.env_only.groww_configured} />
          <div className="locked"><span>Order rate</span><Badge>{eff.env_only.orders_per_second}/s · cap {eff.hard_ceilings.orders_per_second}</Badge></div>
        </div>
        <p className="subtle" style={{ marginTop: 12 }}>These can only be changed in the worker&apos;s environment on the VPS, so the dashboard can never switch on live trading by itself.</p>
      </Card>

      <AnimatePresence>
        {dirty && (
          <motion.div className="save-bar" initial={{ y: 80, opacity: 0, x: "-50%" }} animate={{ y: 0, opacity: 1, x: "-50%" }} exit={{ y: 80, opacity: 0, x: "-50%" }}
            transition={{ type: "spring", stiffness: 380, damping: 30 }}>
            <span>Unsaved changes</span>
            <Button size="sm" variant="ghost" onClick={() => setDraft(baseline)}>Discard</Button>
            <Button size="sm" onClick={save} disabled={saving}>{saving ? <LoaderCircle size={14} className="spin" /> : <Check size={14} />}Save &amp; apply</Button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function Locked({ label, on }: { label: string; on: boolean }) {
  return <div className="locked"><span>{label}</span>{on ? <Badge tone="good"><Check size={12} />on</Badge> : <Badge><Lock size={11} />off</Badge>}</div>;
}
