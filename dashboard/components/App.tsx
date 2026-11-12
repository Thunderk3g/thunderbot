"use client";

import { AnimatePresence, motion } from "motion/react";
import { BrainCircuit, ChartLine, House, Layers, Moon, OctagonX, Play, ScrollText, Settings, Sun } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { ago } from "@/lib/format";
import { workerAlive, type Control, type EventRow, type Heartbeat, type LiveState } from "@/lib/types";
import { post, usePoll } from "@/lib/usePoll";
import { Button, HoldButton, StatusDot, spring } from "./ui";
import DeskView from "./DeskView";
import LiveView from "./LiveView";
import PerformanceView from "./PerformanceView";
import LabView from "./LabView";
import SettingsView from "./SettingsView";
import JournalView from "./JournalView";

const PAGES = [
  { id: "desk", label: "AI desk", icon: BrainCircuit },
  { id: "today", label: "Investing", icon: House },
  { id: "lab", label: "Plans", icon: Layers },
  { id: "results", label: "Results", icon: ChartLine },
  { id: "log", label: "Activity", icon: ScrollText },
  { id: "settings", label: "Settings", icon: Settings },
] as const;
type PageId = (typeof PAGES)[number]["id"];

const ALERT_KINDS = new Set(["error", "exit_failed", "stop_failed", "halt", "kill_switch", "order_rejected", "unmanaged_position"]);
const MODE_WORD: Record<string, string> = { paper: "paper trading", live: "live trading", replay: "a replay" };

/** What the operator asked for. The heartbeat says what the worker is actually doing. */
export function tradingOn(control?: Control): boolean {
  return !!control && !control.kill_switch && !!control.trading_enabled;
}

type Tone = "on" | "off" | "idle";

function workerState(control?: Control): { tone: Tone; title: string; detail: string } {
  const hb: Heartbeat | undefined = control?.heartbeat;
  if (!hb) return { tone: "idle", title: "Not set up yet", detail: "Wake the worker from Home." };
  const serverless = hb.scheduler === "serverless";
  const invest = hb.style === "invest";
  if (!workerAlive(hb)) {
    return serverless
      ? { tone: "off", title: "Scheduler is silent", detail: `Last check ${ago(hb.wall_at ?? hb.at)}.` }
      : { tone: "off", title: "Worker offline", detail: `Last heard from ${ago(hb.wall_at ?? hb.at)}.` };
  }
  if (hb.mode === "replay") return { tone: "on", title: "Running a replay", detail: `Updated ${ago(hb.wall_at)}.` };
  if (control?.kill_switch) return { tone: "idle", title: "Stopped", detail: "Everything is sold. Press Start to go again." };
  if (!control?.trading_enabled) return { tone: "idle", title: invest ? "Not investing yet" : "Not trading", detail: `Press Start to begin ${invest ? (hb.mode === "live" ? "live investing" : "paper investing") : MODE_WORD[hb.mode] ?? hb.mode}.` };
  if (hb.feed && !hb.feed.ok) return { tone: "off", title: hb.feed.source === "yahoo" ? "No prices from Yahoo" : "Groww not connected", detail: "See the notice on Home." };
  if (hb.halted) return { tone: "off", title: "Halted for the day", detail: hb.halt_reason ?? "Daily loss limit reached." };
  if (control?.paused) return { tone: "idle", title: "Paused", detail: invest ? "Holdings stay; no trades happen." : "Managing open trades, taking no new ones." };
  if (hb.market_open === false && !invest) return { tone: "on", title: "Waiting for the market", detail: "Trades 09:15–15:30 IST, Monday to Friday." };
  if (invest) return { tone: "on", title: `Investing (${hb.mode})`, detail: `Checks daily at ${hb.portfolio?.run_at ?? "15:10"} IST. Last heard ${ago(hb.wall_at)}.` };
  return { tone: "on", title: `Running ${MODE_WORD[hb.mode] ?? hb.mode}`, detail: `Updated ${ago(hb.wall_at)}.` };
}

export default function App() {
  const [page, setPage] = useState<PageId>("desk");
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

  const tradeButton = tradingOn(control)
    ? <HoldButton onConfirm={() => act("stop")}><OctagonX size={15} />Hold to stop</HoldButton>
    : <Button variant="primary" onClick={() => act("start")}><Play size={15} />Start</Button>;

  return (
    <div className="frame">
      <header className="topbar">
        <button type="button" className="wordmark" onClick={() => go("desk")} style={{ border: 0, background: "none", cursor: "pointer", padding: 0, color: "inherit" }} aria-label="Thunderbot, go to the AI desk">
          <Bolt />Thunderbot
        </button>
        <nav className="nav" aria-label="Pages">
          {PAGES.map((p) => (
            <button key={p.id} aria-current={page === p.id ? "page" : undefined} onClick={() => go(p.id)}>
              {page === p.id && <motion.span layoutId="nav-mark" className="nav-mark" transition={spring} />}
              <span>{p.label}</span>
            </button>
          ))}
        </nav>
        <div className="bar-end">
          <div className="state" title={state.detail} hidden={page === "desk"}>
            <StatusDot tone={state.tone} />
            <div><strong className={control?.heartbeat?.mode === "live" ? "loss" : ""}>{state.title}</strong><span className="soft">{state.detail}</span></div>
          </div>
          {control?.heartbeat && page !== "desk" && tradeButton}
          <ThemeToggle />
        </div>
      </header>

      <main className="content">
        {live.error && !live.data && (
          <div className="notice stop" style={{ marginBottom: 24 }}>
            <span className="grow">The dashboard can&apos;t reach its database: {live.error}. Check SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in the deployment&apos;s settings.</span>
          </div>
        )}
        <AnimatePresence mode="wait">
          <motion.div key={page} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.16 }}>
            {page === "desk" && <DeskView state={live.data} refresh={live.refresh} />}
            {page === "today" && <LiveView state={live.data} act={act} refresh={live.refresh} go={go} />}
            {page === "results" && <PerformanceView defaultMode={control?.heartbeat?.mode ?? "paper"} />}
            {page === "lab" && <LabView control={control} onApplied={() => { live.refresh(); go("settings"); }} onUsed={() => { live.refresh(); go("today"); }} />}
            {page === "settings" && <SettingsView control={control} refresh={live.refresh} go={go} />}
            {page === "log" && <JournalView />}
          </motion.div>
        </AnimatePresence>
        <p className="foot">
          Thunderbot follows rules; it can&apos;t promise profit. A backtest shows what a rule did, not what it will do, and most
          intraday strategies lose money after costs. Charts use <a href="https://www.tradingview.com/" target="_blank" rel="noreferrer">TradingView</a> Lightweight Charts.
        </p>
      </main>

      <nav className="tabbar" aria-label="Pages">
        {PAGES.map((p) => (
          <button key={p.id} aria-current={page === p.id ? "page" : undefined} onClick={() => go(p.id)}>
            <p.icon size={19} aria-hidden />{p.label}
          </button>
        ))}
      </nav>

      <Toasts events={live.data?.events ?? []} />
    </div>
  );
}

/** The mark: a bolt, in the one accent the brand owns. */
function Bolt() {
  return (
    <svg width="18" height="22" viewBox="0 0 18 22" aria-hidden>
      <path d="M11 0 0 13h7l-2 9 13-14h-8z" fill="var(--bolt)" />
    </svg>
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
    <button type="button" className="icon-btn" onClick={flip} aria-label={dark ? "Switch to light theme" : "Switch to dark theme"} title={dark ? "Light theme" : "Dark theme"}>
      {dark ? <Sun size={17} /> : <Moon size={17} />}
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
