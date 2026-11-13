"use client";

import { AnimatePresence, motion } from "motion/react";
import { FlaskConical, Moon, PauseCircle, Play, ScrollText, SlidersHorizontal, Sun, Unplug, Wallet } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import { ago } from "@/lib/format";
import type { PortfolioExtras } from "@/lib/portfolio";
import type { SetupState } from "@/lib/setup";
import { workerAlive, type Control, type EventRow, type Heartbeat, type LiveState } from "@/lib/types";
import { post, usePoll } from "@/lib/usePoll";
import { Button, HoldButton, spring } from "./ui";
import GuideView from "./GuideView";
import HarnessView from "./HarnessView";
import JournalPage from "./JournalPage";
import LabPage from "./LabPage";
import PortfolioView from "./PortfolioView";
import SetupView from "./SetupView";
import { SystemBus, type Tap } from "./SystemBus";

/** Five places, in the order of how much they matter to someone's money. The intraday desk is a room
 *  inside the Lab, not a peer of the portfolio. */
const NAV = [
  { href: "/", root: "portfolio", label: "Portfolio", icon: Wallet },
  { href: "/lab", root: "lab", label: "Lab", icon: FlaskConical },
  { href: "/journal", root: "journal", label: "Journal", icon: ScrollText },
  { href: "/harness", root: "harness", label: "Harness", icon: SlidersHorizontal },
  { href: "/setup", root: "setup", label: "Setup", icon: Unplug },
] as const;

/** Older page ids still used by the views, mapped to addresses. */
const LEGACY: Record<string, string> = {
  today: "/", lab: "/portfolio/plan", desk: "/lab/desk", results: "/lab/results", log: "/journal/log", settings: "/setup", guide: "/guide",
};
export type Go = (to: string) => void;

const ALERT_KINDS = new Set(["error", "exit_failed", "stop_failed", "halt", "kill_switch", "order_rejected", "unmanaged_position"]);
const MODE_NAME: Record<string, string> = { paper: "Paper", guided: "Guided basket", auto: "Automated" };

/** What the operator asked for. The heartbeat says what the worker is actually doing. */
export function tradingOn(control?: Control): boolean {
  return !!control && !control.kill_switch && !!control.trading_enabled;
}

/** The services everything depends on. They are parallel, so they are drawn as taps off one bus. */
export function systemTaps(control: Control | undefined, setup: SetupState | null): Tap[] {
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
  const extras = (hb?.portfolio ?? {}) as PortfolioExtras;
  const mode = extras.exec_mode ?? (hb?.mode === "live" ? "auto" : "paper");
  return [
    { key: "worker", name: serverless ? "Scheduler" : "Worker", tone: !hb ? "off" : alive ? "on" : "bad",
      note: !hb ? "never called" : alive ? `called ${ago(hb.wall_at ?? hb.at)}` : `silent since ${ago(hb.wall_at ?? hb.at)}` },
    { key: "prices", name: "Market data", tone: !hb ? "off" : feedBad ? "bad" : "on",
      note: !hb ? "waiting for the worker" : feedBad ? "not coming through" : hb.feed?.source === "groww" ? "from Groww" : "from Yahoo, free" },
    { key: "llm", name: "Model", tone: llmOn ? "on" : "optional", note: llmOn ? llmName ?? "connected" : "optional, not fitted" },
    { key: "groww", name: "Broker", tone: growwBad ? "bad" : growwOn ? "on" : "optional",
      note: growwBad ? "last check failed" : growwOn ? (setup?.groww.lastCheck?.ok ? "Groww, key checked" : "Groww, key saved") : "optional, not fitted" },
    { key: "orders", name: "Orders", tone: "on", note: MODE_NAME[mode] ?? mode },
  ];
}

function parse(path: string[]): { root: string; rest: string[] } {
  const [first, ...rest] = path;
  if (!first || first === "portfolio") return { root: "portfolio", rest };
  return { root: first, rest };
}

export default function App({ initialPath }: { initialPath: string[] }) {
  const [path, setPath] = useState<string[]>(initialPath);
  const live = usePoll<LiveState>("/api/state", 2000);
  const setup = usePoll<SetupState>("/api/setup", 15000);
  const control = live.data?.control;
  const hb = control?.heartbeat;
  const taps = systemTaps(control, setup.data);
  const { root, rest } = parse(path);

  useEffect(() => {
    const onPop = () => setPath(window.location.pathname.split("/").filter(Boolean));
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);
  const go: Go = useCallback((to: string) => {
    const href = to.startsWith("/") ? to : LEGACY[to] ?? "/";
    if (href !== window.location.pathname) window.history.pushState(null, "", href);
    setPath(href.split("/").filter(Boolean));
    window.scrollTo({ top: 0 });
  }, []);
  const act = async (action: string, extra: Record<string, unknown> = {}) => {
    if (action === "start" && hb?.mode === "live" && !window.confirm("The worker is in LIVE mode. Start trading with real money?")) return;
    await post("/api/control", { action, ...extra });
    live.refresh();
  };
  const refreshAll = () => { live.refresh(); setup.refresh(); };

  const running = tradingOn(control) || (!!control?.intraday_enabled && !control?.kill_switch);
  const paused = !!control?.paused;
  // The rail's one control pauses; it never sells. Leaving a position is done on the page that holds it.
  const pause = paused
    ? <Button variant="go" block onClick={() => act("resume")}><Play size={15} />Resume</Button>
    : running ? <HoldButton block tone="pause" label="Pause everything: press and hold" onConfirm={() => act("pause")}><PauseCircle size={15} />Hold to pause</HoldButton> : null;
  const openTrades = control?.ai_desk?.positions.length ?? 0;

  return (
    <div className="frame">
      <aside className="rail">
        <button type="button" className="wordmark" onClick={() => go("/")} aria-label="Thunderbot, go to your portfolio"><Bolt />Thunderbot</button>
        <nav className="nav" aria-label="Pages">
          {NAV.map((p) => (
            <a key={p.root} href={p.href} aria-current={root === p.root ? "page" : undefined} onClick={(e) => { if (!e.metaKey && !e.ctrlKey) { e.preventDefault(); go(p.href); } }}>
              {root === p.root && <motion.span layoutId="nav-mark" className="nav-mark" transition={spring} />}
              <span>{p.label}</span>
              {p.root === "lab" && <span className="nav-note">{openTrades > 0 ? `${openTrades} open, paper` : "paper"}</span>}
            </a>
          ))}
        </nav>
        <div className="rail-end">
          <div>
            <p className="sys-title">What is connected</p>
            <SystemBus compact taps={taps} onPick={() => go("/setup")} />
          </div>
          {pause && (
            <div>
              {pause}
              <p className="small soft" style={{ marginTop: 6 }}>{paused ? "Paused. Nothing new is traded." : "Pausing sells nothing. Holdings and stops stay as they are."}</p>
            </div>
          )}
          <div className="rail-row">
            <a className="small" href="/guide" onClick={(e) => { e.preventDefault(); go("/guide"); }}>How it works</a>
            <ThemeToggle />
          </div>
        </div>
      </aside>

      <header className="topbar">
        <button type="button" className="wordmark" onClick={() => go("/")} aria-label="Thunderbot, go to your portfolio"><Bolt />Thunderbot</button>
        <div className="bar-end">
          {paused
            ? <Button variant="go" size="sm" onClick={() => act("resume")}><Play size={14} />Resume</Button>
            : running ? <HoldButton tone="pause" label="Pause everything: press and hold" onConfirm={() => act("pause")}><PauseCircle size={15} />Hold to pause</HoldButton> : null}
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
          <motion.div key={root} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.14 }}>
            {root === "portfolio" && <PortfolioView state={live.data} act={act} refresh={live.refresh} go={go} tab={rest[0] === "plan" ? "plan" : "holdings"} llmOn={taps[2].tone === "on"} />}
            {root === "lab" && <LabPage state={live.data} setup={setup.data} refresh={live.refresh} go={go} tab={rest[0]} />}
            {root === "journal" && <JournalPage go={go} sub={rest[0]} />}
            {root === "harness" && <HarnessView go={go} />}
            {root === "guide" && <GuideView go={go} />}
            {root === "setup" && <SetupView control={control} setup={setup.data} setupError={setup.error} taps={taps} act={act} refresh={refreshAll} go={go} />}
            {!["portfolio", "lab", "journal", "harness", "guide", "setup"].includes(root) && (
              <div className="empty"><strong>There is no page at this address.</strong>Go back to your <a href="/" onClick={(e) => { e.preventDefault(); go("/"); }}>portfolio</a>.</div>
            )}
          </motion.div>
        </AnimatePresence>
        <p className="foot">
          Thunderbot follows rules; it can&apos;t promise profit. A backtest shows what a rule did, not what it will do, and most
          intraday strategies lose money after costs. Charts use <a href="https://www.tradingview.com/" target="_blank" rel="noreferrer">TradingView</a> Lightweight Charts.
        </p>
      </main>

      <nav className="tabbar" aria-label="Pages">
        {NAV.map((p) => (
          <a key={p.root} href={p.href} aria-current={root === p.root ? "page" : undefined} onClick={(e) => { e.preventDefault(); go(p.href); }}>
            <p.icon size={19} aria-hidden />{p.label}
          </a>
        ))}
      </nav>

      <Toasts events={live.data?.events ?? []} />
    </div>
  );
}

/** The mark: a bolt, in the one accent the brand owns, with an ink edge so it holds on pale paper. */
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
