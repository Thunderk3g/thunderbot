"use client";

import { AnimatePresence, motion } from "motion/react";
import { BookOpen, ChartLine, House, Layers, Moon, OctagonX, Play, ScrollText, Sun, Unplug, Zap } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { ago } from "@/lib/format";
import type { SetupState } from "@/lib/setup";
import { workerAlive, type Control, type EventRow, type Heartbeat, type LiveState } from "@/lib/types";
import { post, usePoll } from "@/lib/usePoll";
import { Button, HoldButton, spring } from "./ui";
import DeskView from "./DeskView";
import GuideView from "./GuideView";
import JournalView from "./JournalView";
import LabView from "./LabView";
import LiveView from "./LiveView";
import PerformanceView from "./PerformanceView";
import SetupView from "./SetupView";

const PAGES = [
  { id: "today", label: "Home", icon: House },
  { id: "desk", label: "Desk", icon: Zap },
  { id: "lab", label: "Plans", icon: Layers },
  { id: "results", label: "Results", icon: ChartLine },
  { id: "log", label: "Journal", icon: ScrollText },
  { id: "guide", label: "Guide", icon: BookOpen },
  { id: "settings", label: "Setup", icon: Unplug },
] as const;
export type PageId = (typeof PAGES)[number]["id"];

const ALERT_KINDS = new Set(["error", "exit_failed", "stop_failed", "halt", "kill_switch", "order_rejected", "unmanaged_position"]);

/** What the operator asked for. The heartbeat says what the worker is actually doing. */
export function tradingOn(control?: Control): boolean {
  return !!control && !control.kill_switch && !!control.trading_enabled;
}

type NodeTone = "on" | "off" | "bad";
export type SysNode = { key: string; name: string; note: string; tone: NodeTone };

/** The chain everything depends on, in order: something wakes the worker, it gets prices, an LLM may weigh in,
 *  a broker may be connected, and orders come out the end, on paper or for real. */
export function systemLine(control: Control | undefined, setup: SetupState | null): SysNode[] {
  const hb: Heartbeat | undefined = control?.heartbeat;
  const desk = control?.ai_desk;
  const env = control?.effective_settings?.env_only;
  const alive = workerAlive(hb);
  const serverless = hb?.scheduler === "serverless";
  const feedBad = (hb?.feed && !hb.feed.ok) || !!desk?.feed_error;
  const llmOn = setup ? setup.llm.configured && setup.llm.enabled : !!env?.llm_configured;
  const llmName = setup?.llm.model ?? (env?.llm_configured ? env.llm_model : null);
  const growwOn = setup ? setup.groww.configured : !!env?.groww_configured;
  const growwBad = growwOn && !!setup?.groww.lastCheck && !setup.groww.lastCheck.ok;
  const live = hb?.mode === "live";
  const running = tradingOn(control) || (!!control?.intraday_enabled && !control?.kill_switch);
  return [
    { key: "worker", name: serverless ? "Scheduler" : "Worker", tone: !hb ? "off" : alive ? "on" : "bad",
      note: !hb ? "never called" : alive ? `called ${ago(hb.wall_at ?? hb.at)}` : `silent since ${ago(hb.wall_at ?? hb.at)}` },
    { key: "prices", name: "Prices", tone: !hb ? "off" : feedBad ? "bad" : "on",
      note: !hb ? "waiting for the worker" : feedBad ? "not coming through" : hb.feed?.source === "groww" ? "from Groww" : "from Yahoo, free" },
    { key: "llm", name: "LLM", tone: llmOn ? "on" : "off", note: llmOn ? llmName ?? "connected" : "not connected" },
    { key: "groww", name: "Groww", tone: growwBad ? "bad" : growwOn ? "on" : "off",
      note: growwBad ? "last check failed" : growwOn ? (setup?.groww.lastCheck?.ok ? "key checked" : "key saved") : "not connected" },
    { key: "orders", name: live ? "Real orders" : "Paper orders", tone: running ? "on" : "off", note: running ? (live ? "live on Groww" : "running") : "stopped" },
  ];
}

export default function App() {
  const [page, setPage] = useState<PageId>("today");
  const live = usePoll<LiveState>("/api/state", 2000);
  const setup = usePoll<SetupState>("/api/setup", 15000);
  const control = live.data?.control;
  const hb = control?.heartbeat;
  const nodes = systemLine(control, setup.data);

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
    if (action === "start" && hb?.mode === "live" && !window.confirm("The worker is in LIVE mode. Start trading with real money?")) return;
    await post("/api/control", { action });
    live.refresh();
  };

  const investing = tradingOn(control);
  const deskOn = !!control?.intraday_enabled && !control?.kill_switch;
  const stopAll = async () => {
    if (investing) await post("/api/control", { action: "stop" });
    if (deskOn) await post("/api/control", { action: "ai_stop" });
    live.refresh();
  };
  const power = investing || deskOn
    ? <HoldButton block onConfirm={stopAll}><OctagonX size={15} />Hold to stop</HoldButton>
    : hb ? <Button variant="go" block onClick={() => act("start")}><Play size={15} />Start investing</Button> : null;
  const openTrades = (control?.ai_desk?.positions.length ?? 0) + (hb?.style !== "invest" ? hb?.open_positions ?? 0 : 0);

  return (
    <div className="frame">
      <aside className="rail">
        <button type="button" className="wordmark" onClick={() => go("today")} aria-label="Thunderbot, go to Home"><Bolt />Thunderbot</button>
        <nav className="nav" aria-label="Pages">
          {PAGES.map((p) => (
            <button key={p.id} aria-current={page === p.id ? "page" : undefined} onClick={() => go(p.id)}>
              {page === p.id && <motion.span layoutId="nav-mark" className="nav-mark" transition={spring} />}
              <span>{p.label}</span>
              {p.id === "desk" && openTrades > 0 && <span className="nav-note">{openTrades} open</span>}
            </button>
          ))}
        </nav>
        <div className="rail-end">
          <div>
            <p className="sys-title">What is connected</p>
            <ol className="sys">
              {nodes.map((n) => (
                <li key={n.key} className={n.tone}>
                  <i className="node" aria-hidden />
                  <button type="button" onClick={() => go("settings")} title="Open Setup"><b>{n.name}</b><span>{n.note}</span></button>
                </li>
              ))}
            </ol>
          </div>
          {power}
          <div className="rail-row">
            <span className="small soft">{hb?.mode === "live" ? "Real money" : "Paper money"}</span>
            <ThemeToggle />
          </div>
        </div>
      </aside>

      <header className="topbar">
        <button type="button" className="wordmark" onClick={() => go("today")} aria-label="Thunderbot, go to Home"><Bolt />Thunderbot</button>
        <div className="bar-end">
          {investing || deskOn
            ? <HoldButton onConfirm={stopAll}><OctagonX size={15} />Hold to stop</HoldButton>
            : hb ? <Button variant="go" size="sm" onClick={() => act("start")}><Play size={14} />Start</Button> : null}
          <ThemeToggle />
        </div>
      </header>

      <main className="content">
        {live.error && !live.data && (
          <div className="notice stop" style={{ marginBottom: 24 }}>
            <span className="grow">The dashboard can&apos;t reach its database: {live.error}. Check SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY where the dashboard runs.</span>
          </div>
        )}
        <AnimatePresence mode="wait">
          <motion.div key={page} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.14 }}>
            {page === "today" && <LiveView state={live.data} act={act} refresh={live.refresh} go={go} />}
            {page === "desk" && <DeskView state={live.data} refresh={live.refresh} setup={setup.data} go={go} />}
            {page === "results" && <PerformanceView defaultMode={hb?.mode ?? "paper"} />}
            {page === "lab" && <LabView control={control} onApplied={() => { live.refresh(); go("settings"); }} onUsed={() => { live.refresh(); go("today"); }} />}
            {page === "log" && <JournalView />}
            {page === "guide" && <GuideView go={go} />}
            {page === "settings" && <SetupView control={control} setup={setup.data} setupError={setup.error} nodes={nodes} refresh={() => { live.refresh(); setup.refresh(); }} go={go} />}
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
    <svg width="17" height="21" viewBox="0 0 18 22" aria-hidden>
      <path d="M11 0 0 13h7l-2 9 13-14h-8z" fill="var(--bolt)" stroke="var(--ink)" strokeWidth="1.2" strokeLinejoin="round" />
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
