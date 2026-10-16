"use client";

import { AnimatePresence, motion } from "motion/react";
import { ListOrdered, ScrollText } from "lucide-react";
import { useMemo, useState } from "react";
import { dayTime, num } from "@/lib/format";
import type { EventRow, OrderRow } from "@/lib/types";
import { usePoll } from "@/lib/usePoll";
import { Badge, Card, Empty, Segmented, Skeleton, fadeUp } from "./ui";

const ALERT_KINDS = new Set(["error", "exit_failed", "stop_failed", "halt", "kill_switch", "order_rejected", "unmanaged_position"]);
type Filter = "all" | "alerts" | "trading" | "control";
const TRADING = new Set(["position_opened", "position_closed", "entry_skipped", "entry_unfilled", "exit_retry", "risk_verdict"]);
const CONTROL = new Set(["dashboard", "settings_applied", "login", "login_confirmed", "login_confirmation_required", "pause", "resume", "engine_start", "engine_stop", "static_ip_check"]);

export default function JournalView() {
  const { data } = usePoll<{ events: EventRow[]; orders: OrderRow[] }>("/api/journal", 5000);
  const [filter, setFilter] = useState<Filter>("all");
  const [view, setView] = useState<"events" | "orders">("events");
  const events = useMemo(() => (data?.events ?? []).filter((e) =>
    filter === "all" ? true : filter === "alerts" ? ALERT_KINDS.has(e.kind) : filter === "trading" ? TRADING.has(e.kind) : CONTROL.has(e.kind)), [data, filter]);

  return (
    <div className="grid">
      <div style={{ display: "flex", flexWrap: "wrap", gap: 10, justifyContent: "space-between" }}>
        <Segmented value={view} onChange={setView} options={[{ value: "events", label: "Events" }, { value: "orders", label: "Orders" }]} />
        {view === "events" && (
          <Segmented<Filter> value={filter} onChange={setFilter} options={[
            { value: "all", label: "All" }, { value: "alerts", label: "Alerts" }, { value: "trading", label: "Trading" }, { value: "control", label: "Control" },
          ]} />
        )}
      </div>
      {!data ? <div className="card"><Skeleton height={300} /></div> : view === "events" ? (
        <Card title={`${events.length} events`} icon={<ScrollText size={15} />}>
          {!events.length ? <Empty title="Nothing here" /> : (
            <div className="list">
              <AnimatePresence initial={false}>
                {events.map((e) => (
                  <motion.div key={e.id} layout {...fadeUp} className="row">
                    <span className="subtle mono" style={{ flex: "none", width: 110 }}>{dayTime(e.created_at)}</span>
                    <Badge tone={ALERT_KINDS.has(e.kind) ? "bad" : ""}>{e.kind.replaceAll("_", " ")}</Badge>
                    <span className="grow" style={{ wordBreak: "break-word" }}>{e.message}</span>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}
        </Card>
      ) : (
        <Card title="Order history" icon={<ListOrdered size={15} />}>
          {!data.orders.length ? <Empty title="No orders yet" /> : (
            <div className="table-wrap"><table>
              <thead><tr><th>Time</th><th>Purpose</th><th>Symbol</th><th>Side</th><th>Type</th><th className="num">Qty</th><th className="num">Price</th><th className="num">Trigger</th><th>Status</th><th className="num">Fill</th><th>Mode</th></tr></thead>
              <tbody>{data.orders.map((o) => (
                <tr key={o.id}>
                  <td>{dayTime(o.created_at)}</td><td>{o.purpose}</td><td>{o.symbol}</td><td>{o.side}</td><td>{o.order_type}</td>
                  <td className="num">{o.qty}</td><td className="num">{num(o.price)}</td><td className="num">{num(o.trigger_price)}</td>
                  <td><Badge tone={o.status === "FILLED" ? "good" : o.status === "REJECTED" ? "bad" : o.status === "CANCELLED" ? "" : "blue"}>{o.status.toLowerCase()}</Badge></td>
                  <td className="num">{num(o.avg_price)}</td><td>{o.mode}</td>
                </tr>
              ))}</tbody>
            </table></div>
          )}
        </Card>
      )}
    </div>
  );
}
