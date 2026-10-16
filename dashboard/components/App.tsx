"use client";

import { AnimatePresence, motion } from "motion/react";
import { Moon, OctagonX, Play, Sun } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { ago } from "@/lib/format";
import type { Control, EventRow, Heartbeat, LiveState } from "@/lib/types";
import { post, usePoll } from "@/lib/usePoll";
import { Button, HoldButton, StatusDot, spring } from "./ui";
import LiveView from "./LiveView";
import PerformanceView from "./PerformanceView";
import LabView from "./LabView";
import SettingsView from "./SettingsView";
import JournalView from "./JournalView";

const PAGES = [
  { id: "today", label: "Today" },
  { id: "results", label: "Results" },
  { id: "lab", label: "Lab" },
  { id: "settings", label: "Settings" },
  { id: "log", label: "Log" },
] as const;
type PageId = (typeof PAGES)[number]["id"];

const ALERT_KINDS = new Set(["error", "exit_failed", "stop_failed", "halt", "kill_switch", "order_rejected", "unmanaged_position"]);
const MODE_WORD: Record<string, string> = { paper: "paper trading", live: "live trading", replay: "a replay" };

function workerState(control?: Control): { alive: boolean; title: string; detail: string } {
  const hb: Heartbeat | undefined = control?.heartbeat;
  if (!hb) return { alive: false, title: "No worker yet", detail: "Start one on the server to see trading here." };
  const alive = !!hb.wall_at && Date.now() - new Date(hb.wall_at).getTime() < 45_000;
  if (!alive) return { alive, title: "Worker offline", detail: `Last heard from ${ago(hb.wall_at ?? hb.at)}.` };
  if (control?.kill_switch) return { alive, title: "Stopped", detail: "Everything is flat. No new trades." };
  if (hb.halted) return { alive, title: "Halted for the day", detail: hb.halt_reason ?? "Daily loss limit reached." };
  if (control?.paused) return { alive, title: "Paused", detail: "Managing open trades, taking no new ones." };
  return { alive, title: `Running ${MODE_WORD[hb.mode] ?? hb.mode}`, detail: `Updated ${ago(hb.wall_at)}.` };
}

export default function App() {
  const [page, setPage] = useState<PageId>("today");
  const live = usePoll<LiveState>("/api/state", 2000);
  const control = live.data?.control;
  const state = workerState(control);

  useEffect(() => {
    try {
      const saved = localStorage.getItem("tb-page") as PageId | null;
      if (saved && PAGES.some((p) => p.id === saved)) setPage(saved);
    } catch { /* storage unavailable */ }
  }, []);
  const go = (p: PageId) => {
    setPage(p);
    try { localStorage.setItem("tb-page", p); } catch { /* storage unavailable */ }
    window.scrollTo({ top: 0 });
  };
  const act = async (action: string) => {
    await post("/api/control", { action });
    live.refresh();
  };

  const stopControl = control?.kill_switch
    ? <Button variant="primary" block onClick={() => act("release")}><Play size={15} />Resume trading</Button>
    : <HoldButton block onConfirm={() => act("kill")}><OctagonX size={15} />Hold to stop</HoldButton>;

  return (
    <div className="frame">
      <aside className="rail">
        <div className="wordmark">Thunder<span>bot</span></div>
        <nav className="nav" aria-label="Pages">
          {PAGES.map((p) => (
            <button key={p.id} aria-current={page === p.id ? "page" : undefined} onClick={() => go(p.id)}>
              {page === p.id && <motion.span layoutId="nav-mark" className="nav-mark" transition={spring} />}
              {p.label}
            </button>
          ))}
        </nav>
        <div className="rail-foot">
          <div className="state">
            <StatusDot on={state.alive && !control?.kill_switch && !control?.heartbeat?.halted} />
            <div><strong className={control?.heartbeat?.mode === "live" ? "loss" : ""}>{state.title}</strong><span className="soft">{state.detail}</span></div>
          </div>
          {stopControl}
          <ThemeToggle />
        </div>
      </aside>

      <header className="mobile-bar">
        <div className="state">
          <StatusDot on={state.alive && !control?.kill_switch && !control?.heartbeat?.halted} />
          <div><strong>{state.title}</strong></div>
        </div>
        <div style={{ width: 150 }}>{stopControl}</div>
      </header>

      <main className="content">
        {live.error && !live.data && (
          <div className="notice stop" style={{ marginBottom: 24 }}>
            <span className="grow">The dashboard can&apos;t reach its database: {live.error}. Check SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.</span>
          </div>
        )}
        <AnimatePresence mode="wait">
          <motion.div key={page} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.12 }}>
            {page === "today" && <LiveView state={live.data} act={act} />}
            {page === "results" && <PerformanceView defaultMode={control?.heartbeat?.mode ?? "paper"} />}
            {page === "lab" && <LabView control={control} onApplied={() => { live.refresh(); go("settings"); }} />}
            {page === "settings" && <SettingsView control={control} refresh={live.refresh} />}
            {page === "log" && <JournalView />}
          </motion.div>
        </AnimatePresence>
        <p className="foot">
          Thunderbot can veto, size and stop trades; it can&apos;t promise profit. Most intraday strategies lose money after costs,
          so judge every change on the Results page. Charts use <a href="https://www.tradingview.com/" target="_blank" rel="noreferrer">TradingView</a> Lightweight Charts.
        </p>
      </main>

      <nav className="tabbar" aria-label="Pages">
        {PAGES.map((p) => (
          <button key={p.id} aria-current={page === p.id ? "page" : undefined} onClick={() => go(p.id)}>{p.label}</button>
        ))}
      </nav>

      <Toasts events={live.data?.events ?? []} />
    </div>
  );
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
    <button type="button" className="btn quiet sm" onClick={flip} style={{ alignSelf: "flex-start" }}>
      {dark ? <Sun size={14} /> : <Moon size={14} />}{dark ? "Light theme" : "Dark theme"}
    </button>
  );
}

function Toasts({ events }: { events: EventRow[] }) {
  const seen = useRef<Set<string> | null>(null);
  const [toasts, setToasts] = useState<EventRow[]>([]);
  useEffect(() => {
    if (!events.length) return;
    if (seen.current === null) {
      seen.current = new Set(events.map((e) => e.id)); // don't replay history on first load
      return;
    }
    const fresh = events.filter((e) => !seen.current!.has(e.id) && ALERT_KINDS.has(e.kind));
    events.forEach((e) => seen.current!.add(e.id));
    if (fresh.length) setToasts((t) => [...fresh.slice(0, 3), ...t].slice(0, 4));
  }, [events]);
  useEffect(() => {
    if (!toasts.length) return;
    const id = setTimeout(() => setToasts((t) => t.slice(0, -1)), 8000);
    return () => clearTimeout(id);
  }, [toasts]);
  return (
    <div className="toasts" aria-live="assertive">
      <AnimatePresence>
        {toasts.map((t) => (
          <motion.div key={t.id} className="toast" layout initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }} transition={spring} onClick={() => setToasts((all) => all.filter((x) => x.id !== t.id))}>
            <strong>{t.kind.replaceAll("_", " ").replace(/^./, (c) => c.toUpperCase())}</strong>
            {t.message}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
