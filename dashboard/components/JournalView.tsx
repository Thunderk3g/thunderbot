"use client";

import { useMemo, useState } from "react";
import { dayTime, num } from "@/lib/format";
import type { EventRow, OrderRow } from "@/lib/types";
import { usePoll } from "@/lib/usePoll";
import { Empty, Segmented, Skeleton } from "./ui";

const ALERT_KINDS = new Set(["error", "exit_failed", "stop_failed", "halt", "kill_switch", "order_rejected", "unmanaged_position"]);
const TRADING = new Set(["position_opened", "position_closed", "entry_skipped", "entry_unfilled", "exit_retry", "risk_verdict"]);
const CONTROL = new Set(["dashboard", "settings_applied", "login", "login_confirmed", "login_confirmation_required", "pause", "resume", "engine_start", "engine_stop", "static_ip_check"]);
type Filter = "all" | "problems" | "trades" | "controls";
const STATUS: Record<string, string> = { FILLED: "filled", PENDING: "waiting", PARTIAL: "part filled", CANCELLED: "cancelled", REJECTED: "rejected" };

export default function JournalView() {
  const { data } = usePoll<{ events: EventRow[]; orders: OrderRow[] }>("/api/journal", 5000);
  const [view, setView] = useState<"events" | "orders">("events");
  const [filter, setFilter] = useState<Filter>("all");
  const events = useMemo(() => (data?.events ?? []).filter((e) =>
    filter === "all" ? true : filter === "problems" ? ALERT_KINDS.has(e.kind) : filter === "trades" ? TRADING.has(e.kind) : CONTROL.has(e.kind)), [data, filter]);

  return (
    <div className="page">
      <div style={{ display: "flex", flexWrap: "wrap", gap: 12, justifyContent: "space-between", alignItems: "center" }}>
        <h1>Log</h1>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <Segmented label="Show" value={view} onChange={setView} options={[{ value: "events", label: "What happened" }, { value: "orders", label: "Orders" }]} />
          {view === "events" && (
            <Segmented<Filter> label="Filter" value={filter} onChange={setFilter} options={[
              { value: "all", label: "All" }, { value: "problems", label: "Problems" }, { value: "trades", label: "Trades" }, { value: "controls", label: "Controls" },
            ]} />
          )}
        </div>
      </div>
      {!data ? <Skeleton height={300} /> : view === "events" ? (
        !events.length ? <Empty title="Nothing here." /> : (
          <div className="rows">
            {events.map((e) => (
              <div key={e.id} className="row small">
                <span className="time" style={{ width: 104 }}>{dayTime(e.created_at)}</span>
                <span className={`grow ${ALERT_KINDS.has(e.kind) ? "loss" : ""}`} style={{ wordBreak: "break-word" }}>{e.message}</span>
              </div>
            ))}
          </div>
        )
      ) : !data.orders.length ? <Empty title="No orders yet." /> : (
        <div className="table-wrap"><table>
          <thead><tr><th>Time</th><th>For</th><th>Stock</th><th>Side</th><th>Type</th><th className="num">Qty</th><th className="num">Limit</th><th className="num">Trigger</th><th>Status</th><th className="num">Filled at</th><th>Mode</th></tr></thead>
          <tbody>{data.orders.map((o) => (
            <tr key={o.id}>
              <td className="tnum">{dayTime(o.created_at)}</td><td>{o.purpose.replace("exit:", "exit, ").replaceAll("_", " ")}</td><td className="ticker">{o.symbol}</td>
              <td>{o.side === "BUY" ? "Buy" : "Sell"}</td><td>{o.order_type === "SL" ? "Stop" : o.order_type.toLowerCase()}</td>
              <td className="num">{o.qty}</td><td className="num">{num(o.price)}</td><td className="num">{num(o.trigger_price)}</td>
              <td className={o.status === "REJECTED" ? "loss" : ""}>{STATUS[o.status] ?? o.status.toLowerCase()}</td>
              <td className="num">{num(o.avg_price)}</td><td>{o.mode}</td>
            </tr>
          ))}</tbody>
        </table></div>
      )}
    </div>
  );
}
