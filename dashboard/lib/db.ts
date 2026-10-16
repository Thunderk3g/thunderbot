import "server-only";

// Minimal PostgREST client. Server-side only: uses the service-role key.

type Row = Record<string, unknown>;

function config() {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) throw new Error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set");
  return { base: `${url.replace(/\/$/, "")}/rest/v1`, key };
}

function headers(key: string, extra: Record<string, string> = {}) {
  return { apikey: key, Authorization: `Bearer ${key}`, "Content-Type": "application/json", ...extra };
}

export async function select<T extends Row = Row>(table: string, query: string): Promise<T[]> {
  const { base, key } = config();
  const res = await fetch(`${base}/${table}?${query}`, { headers: headers(key), cache: "no-store" });
  if (!res.ok) throw new Error(`select ${table} failed: ${res.status} ${await res.text()}`);
  return (await res.json()) as T[];
}

export async function upsert(table: string, row: Row): Promise<void> {
  const { base, key } = config();
  const res = await fetch(`${base}/${table}`, {
    method: "POST",
    headers: headers(key, { Prefer: "return=minimal,resolution=merge-duplicates" }),
    body: JSON.stringify(row),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`upsert ${table} failed: ${res.status} ${await res.text()}`);
}

export type Control = Record<string, unknown> & {
  kill_switch?: boolean;
  paused?: boolean;
  login_confirmed_for?: string;
  heartbeat?: { at: string; mode: string; open_positions: number; realized_pnl: number; halted: boolean };
};

export async function getControl(): Promise<Control> {
  const rows = await select<{ key: string; value: unknown }>("control", "select=key,value");
  return Object.fromEntries(rows.map((r) => [r.key, r.value])) as Control;
}

export function istToday(): string {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Kolkata" }).format(new Date());
}
