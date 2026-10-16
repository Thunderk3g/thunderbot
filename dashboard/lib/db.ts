import "server-only";

// Minimal PostgREST client. Server-side only: uses the service-role key.
// Works against Supabase in production and against `thunderbot serve` locally.

type Row = Record<string, unknown>;

function config() {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) throw new Error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set");
  return { base: `${url.replace(/\/$/, "")}/rest/v1`, key };
}

function headers(key: string, extra: Record<string, string> = {}): Record<string, string> {
  const h: Record<string, string> = { apikey: key, "Content-Type": "application/json", ...extra };
  // Legacy service_role keys are JWTs and also go in Authorization; new sb_secret_ keys must not.
  if (key.startsWith("eyJ")) h.Authorization = `Bearer ${key}`;
  return h;
}

/** Build a PostgREST query string; values are URL-encoded (ISO timestamps contain '+'). */
export function q(params: Record<string, string | number | undefined>): string {
  return Object.entries(params)
    .filter(([, v]) => v !== undefined && v !== "")
    .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
    .join("&");
}

export async function select<T = Row>(table: string, query: string): Promise<T[]> {
  const { base, key } = config();
  const res = await fetch(`${base}/${table}?${query}`, { headers: headers(key), cache: "no-store" });
  if (!res.ok) throw new Error(`select ${table} failed: ${res.status} ${await res.text()}`);
  return (await res.json()) as T[];
}

export async function upsert(table: string, row: Row | Row[]): Promise<void> {
  const { base, key } = config();
  const res = await fetch(`${base}/${table}`, {
    method: "POST",
    headers: headers(key, { Prefer: "return=minimal,resolution=merge-duplicates" }),
    body: JSON.stringify(row),
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`upsert ${table} failed: ${res.status} ${await res.text()}`);
}

export async function getControl(): Promise<Record<string, unknown>> {
  const rows = await select<{ key: string; value: unknown }>("control", "select=key,value");
  return Object.fromEntries(rows.map((r) => [r.key, r.value]));
}

export async function setControl(key: string, value: unknown, message: string) {
  const now = new Date().toISOString();
  await upsert("control", { key, value, updated_at: now });
  await logEvent("dashboard", message, { key, value });
}

export async function logEvent(kind: string, message: string, data: Row = {}) {
  await upsert("events", { id: crypto.randomUUID(), created_at: new Date().toISOString(), kind, message, data });
}

export function istToday(): string {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Kolkata" }).format(new Date());
}

export function istDayStart(day: string): string {
  return `${day}T00:00:00+05:30`;
}
