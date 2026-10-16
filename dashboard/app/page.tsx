import { confirmLogin, engageKillSwitch, pauseEntries, releaseKillSwitch, resumeEntries } from "./actions";
import { getControl, istToday, select } from "@/lib/db";

export const dynamic = "force-dynamic";

type Signal = {
  id: string; created_at: string; symbol: string; side: string; entry: number; stop: number; target: number;
  reason: string; mode: string;
};
type Decision = {
  signal_id: string; approve: boolean; size_multiplier: number; confidence: number; rationale: string;
  risk_flags: string[]; model: string; latency_ms: number; error: string | null;
};
type Trade = {
  id: string; symbol: string; side: string; qty: number; entry_price: number; exit_price: number;
  closed_at: string; exit_reason: string; net_pnl: number; costs: number; mode: string;
};
type DailyPnl = { trade_date: string; mode: string; trades: number; net_pnl: number; costs: number; winners: number };
type Event = { id: string; created_at: string; kind: string; message: string };

const ALERT_KINDS = new Set(["error", "exit_failed", "stop_failed", "halt", "kill_switch", "order_rejected", "unmanaged_position"]);

function inr(n: number | null | undefined) {
  if (n === null || n === undefined) return "-";
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(Number(n));
}

function time(iso: string) {
  return new Intl.DateTimeFormat("en-IN", {
    timeZone: "Asia/Kolkata", day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit",
  }).format(new Date(iso));
}

export default async function Page() {
  const [control, signals, decisions, trades, daily, events] = await Promise.all([
    getControl(),
    select<Signal>("signals", "select=*&order=created_at.desc&limit=25"),
    select<Decision>("llm_decisions", "select=*&order=created_at.desc&limit=50"),
    select<Trade>("trades", "select=*&order=closed_at.desc&limit=25"),
    select<DailyPnl>("daily_pnl", "select=*&order=trade_date.desc&limit=20"),
    select<Event>("events", "select=id,created_at,kind,message&order=created_at.desc&limit=40"),
  ]);

  const today = istToday();
  const hb = control.heartbeat;
  const hbAgeSec = hb ? Math.round((Date.now() - new Date(hb.at).getTime()) / 1000) : null;
  const alive = hbAgeSec !== null && hbAgeSec < 90;
  const decisionBySignal = new Map(decisions.map((d) => [d.signal_id, d]));
  const todayRows = daily.filter((d) => d.trade_date === today);
  const todayPnl = todayRows.reduce((s, d) => s + Number(d.net_pnl), 0);
  const todayTrades = todayRows.reduce((s, d) => s + Number(d.trades), 0);

  return (
    <main>
      <div className="header">
        <div>
          <h1>Thunderbot</h1>
          <div className="muted small">
            {hb ? `${hb.mode} mode · heartbeat ${hbAgeSec}s ago` : "no heartbeat yet"}{" "}
            <span className={`pill ${alive ? "good" : "bad"}`}>{alive ? "worker alive" : "worker down"}</span>
          </div>
        </div>
        <div className="controls">
          {control.kill_switch ? (
            <form action={releaseKillSwitch}><button type="submit">Release kill switch</button></form>
          ) : (
            <form action={engageKillSwitch}><button type="submit" className="danger">Kill switch: flatten all</button></form>
          )}
          {control.paused ? (
            <form action={resumeEntries}><button type="submit">Resume entries</button></form>
          ) : (
            <form action={pauseEntries}><button type="submit">Pause new entries</button></form>
          )}
          {control.login_confirmed_for !== today && (
            <form action={confirmLogin}><button type="submit">Confirm today&apos;s broker login</button></form>
          )}
        </div>
      </div>

      <div className="grid">
        <div className="panel stat"><div className="label">Today net P&amp;L</div>
          <div className={`value ${todayPnl >= 0 ? "good" : "bad"}`}>{inr(todayPnl)}</div></div>
        <div className="panel stat"><div className="label">Trades today</div><div className="value">{todayTrades}</div></div>
        <div className="panel stat"><div className="label">Open positions</div><div className="value">{hb?.open_positions ?? "-"}</div></div>
        <div className="panel stat"><div className="label">Status</div>
          <div className="value">
            {control.kill_switch ? <span className="bad">Killed</span>
              : hb?.halted ? <span className="bad">Halted</span>
              : control.paused ? <span className="warn">Paused</span>
              : <span className="good">Active</span>}
          </div></div>
        <div className="panel stat"><div className="label">Login confirmed</div>
          <div className="value">{control.login_confirmed_for === today ? <span className="good">Yes</span> : <span className="warn">No</span>}</div></div>
      </div>

      <section className="panel">
        <h2>Signals and LLM review</h2>
        <table>
          <thead><tr><th>Time</th><th>Symbol</th><th>Side</th><th className="num">Entry</th><th className="num">Stop</th>
            <th className="num">Target</th><th>LLM</th><th className="num">Size</th><th className="num">Conf.</th><th>Rationale</th></tr></thead>
          <tbody>
            {signals.map((s) => {
              const d = decisionBySignal.get(s.id);
              return (
                <tr key={s.id}>
                  <td>{time(s.created_at)}</td><td>{s.symbol}</td><td>{s.side}</td>
                  <td className="num">{s.entry}</td><td className="num">{s.stop}</td><td className="num">{s.target}</td>
                  <td>{d ? <span className={d.approve ? "good" : "bad"}>{d.error ? "error" : d.approve ? "approve" : "reject"}</span> : <span className="muted">off</span>}</td>
                  <td className="num">{d ? `${Math.round(Number(d.size_multiplier) * 100)}%` : "-"}</td>
                  <td className="num">{d ? Number(d.confidence).toFixed(2) : "-"}</td>
                  <td className="small">{d ? d.rationale : s.reason}
                    {d && d.risk_flags?.length > 0 && <div className="muted">{d.risk_flags.join(", ")}</div>}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </section>

      <section className="panel">
        <h2>Closed trades</h2>
        <table>
          <thead><tr><th>Closed</th><th>Symbol</th><th>Side</th><th className="num">Qty</th><th className="num">Entry</th>
            <th className="num">Exit</th><th>Reason</th><th className="num">Costs</th><th className="num">Net</th><th>Mode</th></tr></thead>
          <tbody>
            {trades.map((t) => (
              <tr key={t.id}>
                <td>{time(t.closed_at)}</td><td>{t.symbol}</td><td>{t.side}</td><td className="num">{t.qty}</td>
                <td className="num">{t.entry_price}</td><td className="num">{t.exit_price}</td><td>{t.exit_reason}</td>
                <td className="num">{inr(t.costs)}</td>
                <td className={`num ${Number(t.net_pnl) >= 0 ? "good" : "bad"}`}>{inr(t.net_pnl)}</td><td>{t.mode}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="panel">
        <h2>Daily P&amp;L</h2>
        <table>
          <thead><tr><th>Date</th><th>Mode</th><th className="num">Trades</th><th className="num">Win rate</th>
            <th className="num">Costs</th><th className="num">Net</th></tr></thead>
          <tbody>
            {daily.map((d) => (
              <tr key={`${d.trade_date}-${d.mode}`}>
                <td>{d.trade_date}</td><td>{d.mode}</td><td className="num">{d.trades}</td>
                <td className="num">{d.trades ? `${Math.round((Number(d.winners) / Number(d.trades)) * 100)}%` : "-"}</td>
                <td className="num">{inr(d.costs)}</td>
                <td className={`num ${Number(d.net_pnl) >= 0 ? "good" : "bad"}`}>{inr(d.net_pnl)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="panel">
        <h2>Event log</h2>
        <table>
          <tbody>
            {events.map((e) => (
              <tr key={e.id}>
                <td className="small" style={{ whiteSpace: "nowrap" }}>{time(e.created_at)}</td>
                <td className={ALERT_KINDS.has(e.kind) ? "bad" : "muted"}>{e.kind}</td>
                <td>{e.message}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </main>
  );
}
