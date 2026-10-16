"use client";

import { AnimatePresence, motion } from "motion/react";
import { LoaderCircle } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { inr } from "@/lib/format";
import type { Control, EffectiveSettings } from "@/lib/types";
import { post } from "@/lib/usePoll";
import { Button, ChipsInput, Empty, Panel, Segmented, SliderField, Switch } from "./ui";

type Editable = EffectiveSettings["editable"];

const NAMES: Record<string, string> = {
  capital: "capital", risk_per_trade_pct: "risk per trade", max_daily_loss_pct: "daily loss limit", max_open_positions: "open positions",
  max_trades_per_day: "trades per day", max_leverage: "leverage", max_position_notional_pct: "position size", max_stop_distance_pct: "widest stop",
  flatten_at: "flat-by time", entry_window: "trading hours", symbols: "stocks", live_trading_enabled: "live trading",
};

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
    return <Empty title="Settings haven't loaded.">The worker publishes them when it starts.</Empty>;
  }

  const dirty = JSON.stringify(draft) !== JSON.stringify(baseline);
  const set = <K extends keyof Editable>(k: K, v: Editable[K]) => setDraft({ ...draft, [k]: v });
  const b = (k: string, lo: number, hi: number) => ({ min: eff.bounds[k]?.min ?? lo, max: eff.bounds[k]?.max ?? hi });
  const info = catalog.find((s) => s.name === draft.strategy);
  const overrides = (control?.settings_overrides ?? {}) as Record<string, unknown>;
  const pending = Object.entries(overrides).some(([k, v]) => !(k in eff.rejected) && JSON.stringify(v) !== JSON.stringify((eff.editable as Record<string, unknown>)[k]));
  const rejected = Object.entries(eff.rejected);

  const save = async () => {
    setSaving(true);
    setError(null);
    try {
      await post("/api/settings", { overrides: draft });
      setSavedAt(Date.now());
      refresh();
      setDraft(null); // re-sync from what the worker actually applied
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
    <div className="page">
      <div>
        <h1>Settings</h1>
        <p className="soft" style={{ marginTop: 6, maxWidth: "64ch" }}>Changes apply on the worker within a few seconds. It checks every value against its own limits first.</p>
      </div>

      <div className="notices">
        <AnimatePresence initial={false}>
          {pending && <Notice key="p" kind="info"><LoaderCircle size={14} className="spin" style={{ verticalAlign: -2, marginRight: 8 }} />Saved. Waiting for the worker to apply it.</Notice>}
          {!pending && savedAt && Date.now() - savedAt < 15_000 && <Notice key="ok" kind="info">Applied.</Notice>}
          {rejected.length > 0 && <Notice key="r" kind="caution">The worker kept its own value for {rejected.map(([k, v]) => `${NAMES[k] ?? k} (${v})`).join("; ")}.</Notice>}
          {error && <Notice key="e" kind="stop">Couldn&apos;t save: {error}</Notice>}
        </AnimatePresence>
      </div>

      <div className="split even" style={{ alignItems: "start" }}>
        <div>
          <Panel title="Strategy">
            <div className="form">
              <div className="field">
                <label htmlFor="set-strategy">Trades with</label>
                <select id="set-strategy" className="input" value={draft.strategy} onChange={(e) => {
                  const next = catalog.find((s) => s.name === e.target.value);
                  setDraft({ ...draft, strategy: e.target.value, strategy_params: Object.fromEntries((next?.params ?? []).map((p) => [p.name, p.default])) });
                }}>
                  {catalog.map((s) => <option key={s.name} value={s.name}>{s.label}</option>)}
                </select>
                {info && <span className="hint">{info.description}</span>}
              </div>
              {info?.params.map((p) => (
                <SliderField key={p.name} label={p.label} min={p.min} max={p.max} step={p.step}
                  value={draft.strategy_params[p.name] ?? p.default} onChange={(v) => set("strategy_params", { ...draft.strategy_params, [p.name]: v })} />
              ))}
            </div>
          </Panel>
          <Panel title="Stocks and hours">
            <div className="form">
              <div className="field"><label>Stocks to watch</label><ChipsInput values={draft.symbols} onChange={(v) => set("symbols", v)} placeholder="Add NSE symbol" /></div>
              <div className="time-grid">
                <div className="field"><label htmlFor="t1">New trades from</label><input id="t1" type="time" className="input" value={draft.entry_start} onChange={(e) => set("entry_start", e.target.value)} /></div>
                <div className="field"><label htmlFor="t2">until</label><input id="t2" type="time" className="input" value={draft.entry_end} onChange={(e) => set("entry_end", e.target.value)} /></div>
                <div className="field"><label htmlFor="t3">Flat by</label><input id="t3" type="time" className="input" max={String(eff.hard_ceilings.latest_flatten)} value={draft.flatten_at} onChange={(e) => set("flatten_at", e.target.value)} /></div>
              </div>
              <SliderField label="Limit price offset" suffix="%" min={0.05} max={3} step={0.05} value={draft.price_protection_pct}
                onChange={(v) => set("price_protection_pct", v)} hint="Orders are limit orders this far through the price, never plain market orders" />
            </div>
          </Panel>
        </div>

        <div>
          <Panel title="Money and risk">
            <div className="form">
              <div className="field">
                <label htmlFor="cap">Capital</label>
                <input id="cap" className="input tnum" inputMode="numeric" value={draft.capital} onChange={(e) => set("capital", Number(e.target.value.replace(/[^\d.]/g, "")) || 0)} />
              </div>
              <SliderField label="Risk per trade" suffix="%" {...b("risk_per_trade_pct", 0.05, 2)} step={0.05} value={draft.risk_per_trade_pct}
                onChange={(v) => set("risk_per_trade_pct", v)} hint={`${inr((draft.capital * draft.risk_per_trade_pct) / 100)} lost if a stop is hit`} />
              <SliderField label="Daily loss limit" suffix="%" {...b("max_daily_loss_pct", 0.1, 10)} step={0.1} value={draft.max_daily_loss_pct}
                onChange={(v) => set("max_daily_loss_pct", v)} hint={`Stops for the day at ${inr((draft.capital * draft.max_daily_loss_pct) / 100)} down`} />
              <SliderField label="Open positions at once" min={1} max={20} step={1} value={draft.max_open_positions} onChange={(v) => set("max_open_positions", v)} />
              <SliderField label="Trades per day" min={1} max={50} step={1} value={draft.max_trades_per_day} onChange={(v) => set("max_trades_per_day", v)} />
              <SliderField label="Intraday leverage" suffix="x" {...b("max_leverage", 0.1, 5)} step={0.1} value={draft.max_leverage}
                onChange={(v) => set("max_leverage", v)} hint={`Up to ${eff.hard_ceilings.max_leverage}x`} />
              <SliderField label="Largest position" suffix="%" min={1} max={100} step={1} value={draft.max_position_notional_pct} onChange={(v) => set("max_position_notional_pct", v)} hint="Of buying power" />
              <SliderField label="Widest stop allowed" suffix="%" min={0.1} max={10} step={0.1} value={draft.max_stop_distance_pct} onChange={(v) => set("max_stop_distance_pct", v)} />
              <div className="toggle-row"><span className="field-label">Allow intraday short selling</span><Switch checked={draft.allow_short} onChange={(v) => set("allow_short", v)} label="Allow short selling" /></div>
            </div>
          </Panel>
          <Panel title="Reviewer">
            <div className="form">
              <div className="toggle-row">
                <div><div className="field-label">Ask Claude about each signal</div><p className="hint">{eff.env_only.llm_model} can skip a trade or shrink it, never make it bigger.</p></div>
                <Switch checked={draft.llm_enabled} onChange={(v) => set("llm_enabled", v)} label="Claude reviewer" />
              </div>
              <AnimatePresence initial={false}>
                {draft.llm_enabled && (
                  <motion.div className="form" initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} style={{ overflow: "hidden" }}>
                    <div className="field"><label>How hard it thinks</label>
                      <Segmented label="Effort" value={draft.llm_effort} onChange={(v) => set("llm_effort", v)} options={eff.llm_efforts.map((e) => ({ value: e, label: e }))} />
                    </div>
                    <div className="field"><label>If it can&apos;t answer</label>
                      <Segmented label="Failure behaviour" value={draft.llm_fail_mode} onChange={(v) => set("llm_fail_mode", v)} options={[{ value: "reject", label: "Skip the trade" }, { value: "pass", label: "Trade anyway" }]} />
                    </div>
                    <SliderField label="Confidence needed to approve" min={0} max={1} step={0.05} value={draft.llm_min_confidence} onChange={(v) => set("llm_min_confidence", v)} />
                  </motion.div>
                )}
              </AnimatePresence>
              <p className="hint">Results shows whether the trades it skips really do worse.</p>
            </div>
          </Panel>
        </div>
      </div>

      <section>
        <div className="section-head">
          <h2>Set on the server only</h2>
          <Button size="sm" variant="quiet" onClick={reset}>Reset everything above to the server defaults</Button>
        </div>
        <p className="soft small" style={{ marginBottom: 14, maxWidth: "64ch" }}>
          The dashboard can&apos;t change these, so a stolen password can&apos;t turn on live trading. Edit <code>/etc/thunderbot.env</code> on the server.
        </p>
        <dl className="locked">
          <dt>Live trading</dt><dd className={eff.env_only.live_trading_enabled ? "loss" : ""}>{eff.env_only.live_trading_enabled ? "Allowed" : "Off"}</dd>
          <dt>Margin trading (MTF)</dt><dd>{eff.env_only.allow_mtf_api ? "Allowed" : "Off"}</dd>
          <dt>Daily login confirmation</dt><dd>{eff.env_only.require_login_confirmation ? "Required" : "Not required"}</dd>
          <dt>Static IP check</dt><dd>{eff.env_only.static_ip_configured ? "Configured" : "Not configured yet"}</dd>
          <dt>Groww account</dt><dd>{eff.env_only.groww_configured ? "Connected" : "Not connected yet"}</dd>
          <dt>Order rate</dt><dd className="tnum">{eff.env_only.orders_per_second} a second (exchange limit 10)</dd>
        </dl>
      </section>

      <AnimatePresence>
        {dirty && (
          <motion.div className="save-bar" initial={{ y: 80, opacity: 0, x: "-50%" }} animate={{ y: 0, opacity: 1, x: "-50%" }} exit={{ y: 80, opacity: 0, x: "-50%" }}
            transition={{ type: "spring", stiffness: 380, damping: 32 }}>
            <span>You have unsaved changes</span>
            <Button size="sm" variant="quiet" onClick={() => setDraft(baseline)}>Discard</Button>
            <Button size="sm" onClick={save} disabled={saving}>{saving && <LoaderCircle size={14} className="spin" />}Save changes</Button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function Notice({ kind, children }: { kind: "stop" | "caution" | "info"; children: React.ReactNode }) {
  return (
    <motion.div className={`notice ${kind}`} initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} transition={{ duration: 0.2 }}>
      <span className="grow">{children}</span>
    </motion.div>
  );
}
