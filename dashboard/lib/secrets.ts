import "server-only";
import { createCipheriv, createDecipheriv, createHash, randomBytes } from "node:crypto";

// Keys saved from the setup screen, encrypted before they reach the database.
//
// Format, shared with worker/thunderbot/secrets.py:
//   key     SHA-256 of "thunderbot-secrets-v1:" + master
//   master  TB_SECRET_KEY, or the database key both sides already hold (SUPABASE_SERVICE_ROLE_KEY)
//   stored  "v1:" + base64(iv(12) || ciphertext || tag(16)), AES-256-GCM, plaintext one JSON object
//
// The table holds ciphertext, a masked hint and non-secret metadata. Nothing in this file logs a secret
// or puts one in an error message.

const KDF_PREFIX = "thunderbot-secrets-v1:";
const VERSION = "v1";
const TABLE = "secrets";

export type KeySource = "TB_SECRET_KEY" | "service_key";
export type SecretRow = { name: string; hint: string; meta: Record<string, unknown>; updated_at: string };

export function masterKey(): { value: string; source: KeySource } | null {
  const own = (process.env.TB_SECRET_KEY ?? "").trim();
  if (own) return { value: own, source: "TB_SECRET_KEY" };
  const service = (process.env.SUPABASE_SERVICE_ROLE_KEY ?? "").trim();
  if (service) return { value: service, source: "service_key" };
  return null;
}

function aesKey(master: string): Buffer {
  return createHash("sha256").update(KDF_PREFIX + master, "utf8").digest();
}

export function encryptSecret(obj: Record<string, unknown>, master: string, iv: Buffer = randomBytes(12)): string {
  const cipher = createCipheriv("aes-256-gcm", aesKey(master), iv);
  const body = Buffer.concat([cipher.update(JSON.stringify(obj), "utf8"), cipher.final()]);
  return `${VERSION}:${Buffer.concat([iv, body, cipher.getAuthTag()]).toString("base64")}`;
}

export function decryptSecret(blob: string, master: string): Record<string, unknown> {
  const [version, payload] = [blob.slice(0, blob.indexOf(":")), blob.slice(blob.indexOf(":") + 1)];
  if (version !== VERSION || !payload) throw new Error("unknown secret format");
  const raw = Buffer.from(payload, "base64");
  if (raw.length < 12 + 16) throw new Error("stored secret is too short");
  const decipher = createDecipheriv("aes-256-gcm", aesKey(master), raw.subarray(0, 12));
  decipher.setAuthTag(raw.subarray(raw.length - 16));
  let plain: string;
  try {
    plain = Buffer.concat([decipher.update(raw.subarray(12, raw.length - 16)), decipher.final()]).toString("utf8");
  } catch {
    throw new Error("the saved key cannot be decrypted with the current TB_SECRET_KEY; save it again");
  }
  const out: unknown = JSON.parse(plain);
  if (!out || typeof out !== "object" || Array.isArray(out)) throw new Error("stored secret is not an object");
  return out as Record<string, unknown>;
}

/** "sk-ant-…a1b2": a recognisable prefix and never more than the last four characters. */
export function maskKey(secret: string): string {
  const s = secret.trim();
  if (s.length < 12) return "…";
  const head = s.slice(0, 7);
  const cut = Math.max(head.lastIndexOf("-"), head.lastIndexOf("_"));
  const prefix = cut >= 0 ? head.slice(0, cut + 1) : s.slice(0, 3);
  return `${prefix}…${s.slice(-4)}`;
}

// PostgREST plumbing (Supabase in production, `thunderbot serve` locally).

function rest() {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) throw new Error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set");
  const headers: Record<string, string> = { apikey: key, "Content-Type": "application/json" };
  // Legacy service_role keys are JWTs and also go in Authorization; new sb_secret_ keys must not.
  if (key.startsWith("eyJ")) headers.Authorization = `Bearer ${key}`;
  return { base: `${url.replace(/\/$/, "")}/rest/v1/${TABLE}`, headers };
}

async function call(method: string, query: string, body?: unknown, prefer?: string): Promise<Response> {
  const { base, headers } = rest();
  const res = await fetch(`${base}${query}`, {
    method, cache: "no-store", headers: prefer ? { ...headers, Prefer: prefer } : headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  // The response to a failed write could echo the row, so only the status is reported.
  if (!res.ok) throw new Error(`secrets ${method} failed with HTTP ${res.status}`);
  return res;
}

/** Names, hints and metadata of what is saved. Never the ciphertext. */
export async function listSecretRows(): Promise<SecretRow[]> {
  const res = await call("GET", "?select=name,hint,meta,updated_at");
  return (await res.json()) as SecretRow[];
}

export async function secretStoreStatus(): Promise<{ ready: boolean; keySource: KeySource | null; problem?: string }> {
  const master = masterKey();
  if (!master) {
    return { ready: false, keySource: null, problem: "Set TB_SECRET_KEY (or SUPABASE_SERVICE_ROLE_KEY) on the dashboard to save keys here." };
  }
  try {
    await call("GET", "?select=name&limit=1");
  } catch {
    return {
      ready: false, keySource: master.source,
      problem: "The secrets table is missing. Apply supabase/migrations/20261113000000_secrets.sql, or restart `thunderbot serve` on the current version.",
    };
  }
  return { ready: true, keySource: master.source };
}

function requireMaster(): string {
  const master = masterKey();
  if (!master) throw new Error("Keys cannot be saved yet: set TB_SECRET_KEY on the dashboard and on the worker.");
  return master.value;
}

export async function putSecret(name: string, obj: Record<string, unknown>, hint: string, meta: Record<string, unknown>): Promise<void> {
  const row = { name, ciphertext: encryptSecret(obj, requireMaster()), hint, meta, updated_at: new Date().toISOString() };
  await call("POST", "", row, "return=minimal,resolution=merge-duplicates");
}

export async function getSecret(name: string): Promise<Record<string, unknown> | null> {
  const res = await call("GET", `?select=ciphertext&name=eq.${encodeURIComponent(name)}&limit=1`);
  const rows = (await res.json()) as { ciphertext?: string }[];
  if (!rows.length || !rows[0].ciphertext) return null;
  return decryptSecret(rows[0].ciphertext, requireMaster());
}

export async function deleteSecret(name: string): Promise<void> {
  await call("DELETE", `?name=eq.${encodeURIComponent(name)}`);
}
