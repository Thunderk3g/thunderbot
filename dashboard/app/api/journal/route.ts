import { q, select } from "@/lib/db";
import { guard } from "@/lib/api";
import type { EventRow, OrderRow } from "@/lib/types";

export const dynamic = "force-dynamic";

export async function GET() {
  return guard(async () => {
    const [events, orders] = await Promise.all([
      select<EventRow>("events", q({ select: "id,created_at,kind,message", order: "created_at.desc", limit: 300 })),
      select<OrderRow>("orders", q({
        select: "id,created_at,order_id,purpose,symbol,side,order_type,qty,price,trigger_price,status,avg_price,mode",
        order: "created_at.desc", limit: 200,
      })),
    ]);
    return { events, orders };
  });
}
