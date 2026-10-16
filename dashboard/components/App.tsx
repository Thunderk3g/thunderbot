"use client";

import { AnimatePresence, motion } from "motion/react";
import { Activity, ChartLine, CircleAlert, FlaskConical, Moon, OctagonX, Play, ScrollText, SlidersHorizontal, Sun, Zap } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { ago } from "@/lib/format";
import type { EventRow, LiveState } from "@/lib/types";
import { post, usePoll } from "@/lib/usePoll";
import { Badge, Button, HoldButton, Pulse, spring } from "./ui";
import LiveView from "./LiveView";
import PerformanceView from "./PerformanceView";
import LabView from "./LabView";
import SettingsView from "./SettingsView";
import JournalView from "./JournalView";

const TABS = [
  { id: "live", label: "Live", icon: Activity },
  { id: "performance", label: "Performance", icon: ChartLine },
  { id: "lab", label: "Strategy lab", icon: FlaskConical },
  { id: "settings", label: "Settings", icon: SlidersHorizontal },
  { id: "journal", label: "Journal", icon: ScrollText },
] as const;
type TabId = (typeof TABS)[number]["id"];

const ALERT_KINDS = new Set(["error", "exit_failed", "stop_failed", "halt", "kill_switch", "order_rejected", "unmanaged_position"]);

export default function App() {
  const [tab, setTab] = useState<TabId>("live");
  const live = usePoll<LiveState>("/api/state", 2000);
  const control = live.data?.control;
  const hb = control?.heartbeat;
  const alive = !!hb?.wall_at && Date.now() - new Date(hb.wall_at).getTime() < 45_000;

  useEffect(() => {
    try {
      const saved = localStorage.getItem("tb-tab") as TabId | null;
      if (saved && TABS.some((t) => t.id === saved)) setTab(saved);
    } catch { /* storage unavailable */ }
  }, []);
  const choose = (t: TabId) => {
    setTab(t);
    try { localStorage.setItem("tb-tab", t); } catch { /* storage unavailable */ }
  };

  const act = async (action: string) => {
    await post("/api/control", { action });
    live.refresh();
  };

  return (
    <div className="shell">
      <header className="topbar">
        <div style={{ display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap" }}>
          <div className="brand"><span className="brand-mark"><Zap size={15} /></span>Thunderbot</div>
          <div className="status-line">
            <Pulse on={alive} />
            <span>{hb ? (alive ? `Worker live · ${ago(hb.wall_at)}` : `Worker offline · last seen ${ago(hb.wall_at ?? hb.at)}`) : "Waiting for worker"}</span>
            {hb && <ModeBadge mode={hb.mode} />}
            {hb?.strategy && <Badge>{hb.strategy}</Badge>}
          </div>
        </div>
        <div className="top-actions">
          <ThemeToggle />
          <AnimatePresence mode="popLayout" initial={false}>
            {control?.kill_switch ? (
              <motion.div key="release" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.9 }}>
                <Button variant="primary" onClick={() => act("release")}><Play size={15} />Release kill switch</Button>
              </motion.div>
            ) : (
              <motion.div key="kill" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.9 }}>
                <HoldButton onConfirm={() => act("kill")}><OctagonX size={15} />Hold to kill</HoldButton>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </header>

      <nav className="tabs" role="tablist">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button key={id} role="tab" aria-selected={tab === id} className="tab" onClick={() => choose(id)}>
            {tab === id && <motion.div layoutId="tab-pill" className="tab-pill" transition={spring} />}
            <span><Icon size={15} />{label}</span>
          </button>
        ))}
      </nav>

      {live.error && !live.data && (
        <div className="banner bad"><CircleAlert size={16} /><span className="grow">Can&apos;t reach the data API: {live.error}</span></div>
      )}

      <AnimatePresence mode="wait">
        <motion.main key={tab} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}>
          {tab === "live" && <LiveView state={live.data} act={act} />}
          {tab === "performance" && <PerformanceView defaultMode={hb?.mode ?? "paper"} />}
          {tab === "lab" && <LabView control={control} onApplied={() => { live.refresh(); choose("settings"); }} />}
          {tab === "settings" && <SettingsView control={control} refresh={live.refresh} />}
          {tab === "journal" && <JournalView />}
        </motion.main>
      </AnimatePresence>

      <footer className="subtle" style={{ marginTop: 40, textAlign: "center" }}>
        Charts by <a href="https://www.tradingview.com/" target="_blank" rel="noreferrer" style={{ color: "inherit" }}>TradingView</a> Lightweight Charts™.
        Thunderbot is a tool, not a guarantee: most intraday strategies lose money after costs.
      </footer>

      <Toasts events={live.data?.events ?? []} />
    </div>
  );
}

function ModeBadge({ mode }: { mode: string }) {
  if (mode === "live") return <Badge tone="live">LIVE</Badge>;
  if (mode === "replay") return <Badge tone="blue">REPLAY</Badge>;
  return <Badge tone="good">PAPER</Badge>;
}

function ThemeToggle() {
  const [dark, setDark] = useState<boolean | null>(null);
  useEffect(() => {
    const t = document.documentElement.dataset.theme;
    setDark(t ? t === "dark" : window.matchMedia("(prefers-color-scheme: dark)").matches);
  }, []);
  const flip = () => {
    const next = dark ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem("tb-theme", next); } catch { /* storage unavailable */ }
    setDark(!dark);
  };
  return (
    <Button variant="ghost" size="sm" onClick={flip} title="Toggle theme">
      <motion.span key={String(dark)} initial={{ rotate: -90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} style={{ display: "inline-flex" }}>
        {dark ? <Sun size={16} /> : <Moon size={16} />}
      </motion.span>
    </Button>
  );
}

function Toasts({ events }: { events: EventRow[] }) {
  const seen = useRef<Set<string> | null>(null);
  const [toasts, setToasts] = useState<EventRow[]>([]);
  useEffect(() => {
    if (!events.length) return;
    if (seen.current === null) {
      seen.current = new Set(events.map((e) => e.id)); // don't toast history on first load
      return;
    }
    const fresh = events.filter((e) => !seen.current!.has(e.id) && ALERT_KINDS.has(e.kind));
    events.forEach((e) => seen.current!.add(e.id));
    if (fresh.length) setToasts((t) => [...fresh.slice(0, 3), ...t].slice(0, 4));
  }, [events]);
  useEffect(() => {
    if (!toasts.length) return;
    const id = setTimeout(() => setToasts((t) => t.slice(0, -1)), 7000);
    return () => clearTimeout(id);
  }, [toasts]);
  return (
    <div className="toasts" aria-live="polite">
      <AnimatePresence>
        {toasts.map((t) => (
          <motion.div key={t.id} className="toast bad" layout initial={{ opacity: 0, x: 40, scale: 0.96 }}
            animate={{ opacity: 1, x: 0, scale: 1 }} exit={{ opacity: 0, x: 40 }} transition={spring}
            onClick={() => setToasts((all) => all.filter((x) => x.id !== t.id))}>
            <CircleAlert size={16} color="var(--critical)" style={{ flex: "none", marginTop: 2 }} />
            <div><div style={{ fontWeight: 600 }}>{t.kind.replaceAll("_", " ")}</div><div className="ink2" style={{ fontSize: 13 }}>{t.message}</div></div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
