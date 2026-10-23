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

/** What the operator asked for. The heartbeat says what the worker is actually doing. */
export function tradingOn(control?: Control): boolean {
  return !!control && !control.kill_switch && !!control.trading_enabled;
}

function workerState(control?: Control): { on: boolean; title: string; detail: string } {
  const hb: Heartbeat | undefined = control?.heartbeat;
  if (!hb) return { on: false, title: "No worker yet", detail: "Start the worker on the server to trade from here." };
  const alive = !!hb.wall_at && Date.now() - new Date(hb.wall_at).getTime() < 45_000;
  if (!alive) return { on: false, title: "Worker offline", detail: `Last heard from ${ago(hb.wall_at ?? hb.at)}.` };
  if (hb.mode === "replay") return { on: true, title: "Running a replay", detail: `Updated ${ago(hb.wall_at)}.` };
  if (control?.kill_switch) return { on: false, title: "Stopped", detail: "Everything is flat. Press Start to trade again." };
  if (!control?.trading_enabled) return { on: false, title: "Not trading", detail: `Press Start to begin ${MODE_WORD[hb.mode] ?? hb.mode}.` };
  if (hb.feed && !hb.feed.ok) return { on: false, title: hb.feed.source === "yahoo" ? "No prices from Yahoo" : "Groww not connected", detail: "See the notice on Today." };
  if (hb.halted) return { on: false, title: "Halted for the day", detail: hb.halt_reason ?? "Daily loss limit reached." };
  if (control?.paused) return { on: true, title: "Paused", detail: "Managing open trades, taking no new ones." };
  if (hb.market_open === false && hb.style !== "invest") return { on: true, title: "Waiting for the market", detail: "Trades 09:15–15:30 IST, Monday to Friday." };
  if (hb.style === "invest") return { on: true, title: `Investing (${hb.mode})`, detail: `Acts daily at ${hb.portfolio?.run_at ?? "15:10"}. Updated ${ago(hb.wall_at)}.` };
  return { on: true, title: `Running ${MODE_WORD[hb.mode] ?? hb.mode}`, detail: `Updated ${ago(hb.wall_at)}.` };
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
    if (action === "start" && control?.heartbeat?.mode === "live"
      && !window.confirm("The worker is in LIVE mode. Start trading with real money?")) return;
    await post("/api/control", { action });
    live.refresh();
  };

  const mode = control?.heartbeat?.mode === "live" ? "live" : "paper";
  const tradeButton = (compact: boolean) => tradingOn(control)
    ? <HoldButton block onConfirm={() => act("stop")}><OctagonX size={15} />{compact ? "Hold to stop" : "Hold to stop trading"}</HoldButton>
    : <Button variant="primary" block onClick={() => act("start")}><Play size={15} />{compact ? "Start" : `Start ${mode} trading`}</Button>;

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
            <StatusDot on={state.on} />
            <div><strong className={control?.heartbeat?.mode === "live" ? "loss" : ""}>{state.title}</strong><span className="soft">{state.detail}</span></div>
          </div>
          {tradeButton(false)}
          <ThemeToggle />
        </div>
      </aside>

      <header className="mobile-bar">
        <div className="state">
          <StatusDot on={state.on} />
          <div><strong>{state.title}</strong></div>
        </div>
        <div style={{ width: 132 }}>{tradeButton(true)}</div>
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
