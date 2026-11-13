import { getControl, logEvent, setControl, upsert } from "@/lib/db";
import { fail, guard } from "@/lib/api";
import { deleteSecret, getSecret, listSecretRows, maskKey, putSecret, secretStoreStatus } from "@/lib/secrets";
import { PROVIDERS } from "@/lib/setup";
import type { CheckLlmResult, GrowwCheck, GrowwJobResult, ProviderInfo, SaveLlmResult, SetupState } from "@/lib/setup";

export const dynamic = "force-dynamic";

// The setup screen: bring your own LLM key and your own Groww credentials.
// Keys are checked against the provider from here (server side), encrypted, and stored for the worker.
// Nothing saved here can switch on real orders: live trading, the static IP and MTF are read from the
// environment of the machine the worker runs on.

const LIST_TIMEOUT_MS = 10_000;
const TEST_TIMEOUT_MS = 25_000;
const TEST_TOKENS = 64; // room for a model that thinks before it answers; the reply itself is one word
const NOT_CHAT = /embed|whisper|tts|speech|transcrib|dall-e|image|imagen|veo|video|moderation|rerank|guard|audio|realtime/i;

type Env = {
  llm_configured?: boolean; llm_provider?: string; llm_model?: string; llm_source?: string | null;
  groww_configured?: boolean; groww_source?: string | null; groww_auth?: "totp" | "approval" | null;
  live_trading_enabled?: boolean; expected_static_ip?: string | null;
};
type Effective = { env_only?: Env; editable?: { llm_enabled?: boolean } };

export async function GET() {
  return guard(async (): Promise<SetupState> => {
    const store = await secretStoreStatus();
    const [control, rows] = await Promise.all([getControl(), store.ready ? listSecretRows() : Promise.resolve([])]);
    const eff = (control.effective_settings ?? {}) as Effective;
    const env = eff.env_only ?? {};
    const text = (v: unknown) => (typeof v === "string" && v ? v : null);

    const llmRow = rows.find((r) => r.name === "llm");
    // A worker that has not run since a key was cleared may still report "dashboard"; the table is the truth.
    const llmEnv = !llmRow && !!env.llm_configured && env.llm_source !== "dashboard";
    const llm: SetupState["llm"] = llmRow
      ? {
          configured: true, source: "dashboard", preset: text(llmRow.meta.preset), provider: text(llmRow.meta.provider),
          baseUrl: text(llmRow.meta.base_url), model: text(llmRow.meta.model), hint: llmRow.hint || null,
          updatedAt: llmRow.updated_at ?? null, enabled: eff.editable?.llm_enabled ?? true,
        }
      : {
          configured: llmEnv, source: llmEnv ? "environment" : null, preset: null,
          provider: llmEnv && env.llm_provider !== "none" ? text(env.llm_provider) : null, baseUrl: null,
          model: llmEnv ? text(env.llm_model) : null, hint: null, updatedAt: null,
          enabled: llmEnv && (eff.editable?.llm_enabled ?? false),
        };

    const growwRow = rows.find((r) => r.name === "groww");
    const growwEnv = !growwRow && !!env.groww_configured && env.groww_source !== "dashboard";
    const check = control.groww_check as GrowwCheck | null | undefined;
    const groww: SetupState["groww"] = {
      configured: !!growwRow || growwEnv,
      source: growwRow ? "dashboard" : growwEnv ? "environment" : null,
      auth: growwRow ? (growwRow.meta.auth === "totp" ? "totp" : "approval") : growwEnv ? env.groww_auth ?? null : null,
      hint: growwRow ? growwRow.hint || null : null,
      updatedAt: growwRow?.updated_at ?? null,
      lastCheck: check && Array.isArray(check.steps) ? check : null,
    };

    return {
      store, providers: PROVIDERS, llm, groww,
      live: { enabled: !!env.live_trading_enabled, staticIp: text(env.expected_static_ip) },
    };
  });
}

export async function POST(req: Request) {
  let body: Record<string, unknown>;
  try {
    body = (await req.json()) as Record<string, unknown>;
  } catch {
    return fail("invalid JSON", 400);
  }
  if (!body || typeof body !== "object") return fail("invalid JSON", 400);
  const action = typeof body.action === "string" ? body.action : "";
  const handler = ACTIONS[action];
  if (!handler) return fail(`unknown action; use one of ${Object.keys(ACTIONS).join(", ")}`, 400);
  try {
    return guard(await handler(body));
  } catch (e) {
    return fail(e, e instanceof BadRequest ? 400 : 500);
  }
}

class BadRequest extends Error {}

// Each handler validates first (throwing BadRequest) and returns the work to run under guard().
const ACTIONS: Record<string, (body: Record<string, unknown>) => Promise<() => Promise<unknown>>> = {
  check_llm: async (body) => {
    const target = await llmTarget(body);
    return () => listModels(target);
  },

  save_llm: async (body) => {
    const model = str(body.model);
    if (!model || model.length > 200) throw new BadRequest("choose a model");
    await requireStore();
    const target = await llmTarget(body);
    return async (): Promise<SaveLlmResult> => {
      const test = await testModel(target, model);
      if (!test.ok) return test;
      await putSecret(
        "llm",
        { provider: target.provider.family, preset: target.provider.id, base_url: target.baseUrl, api_key: target.key, model },
        maskKey(target.key),
        { preset: target.provider.id, provider: target.provider.label, family: target.provider.family, base_url: target.baseUrl, model },
      );
      await logEvent("dashboard", `LLM key saved (${target.provider.label}, ${model})`);
      return test;
    };
  },

  clear_llm: async () => async () => {
    await deleteSecret("llm");
    await logEvent("dashboard", "LLM key removed");
    return { ok: true };
  },

  save_groww: async (body) => {
    const apiKey = str(body.apiKey);
    const totpSecret = str(body.totpSecret).replace(/\s+/g, "").toUpperCase();
    const apiSecret = str(body.apiSecret);
    const auth = validateGroww(apiKey, totpSecret, apiSecret);
    await requireStore();
    return async (): Promise<GrowwJobResult> => {
      const secret: Record<string, unknown> = { api_key: apiKey };
      if (auth === "totp") secret.totp_secret = totpSecret;
      else secret.api_secret = apiSecret;
      await putSecret("groww", secret, maskKey(apiKey), { auth });
      await logEvent("dashboard", `Groww credentials saved (${auth === "totp" ? "TOTP key" : "approval key"})`);
      // A token issued for the previous key must not be reused for the new one.
      return { ok: true, jobId: await queueGrowwCheck(true) };
    };
  },

  check_groww: async () => async (): Promise<GrowwJobResult> => ({ ok: true, jobId: await queueGrowwCheck(false) }),

  clear_groww: async () => async () => {
    await deleteSecret("groww");
    await setControl("groww_check", null, "Groww credentials removed");
    return { ok: true };
  },
};

function str(v: unknown): string {
  return typeof v === "string" ? v.trim() : "";
}

async function requireStore() {
  const status = await secretStoreStatus();
  if (!status.ready) throw new BadRequest(status.problem ?? "Keys cannot be saved yet: set TB_SECRET_KEY.");
}

// LLM

type Target = { provider: ProviderInfo; baseUrl: string; key: string };

function baseUrlFor(provider: ProviderInfo, given: string): string {
  if (provider.id !== "custom") return provider.baseUrl;
  let url: URL;
  try {
    url = new URL(given);
  } catch {
    throw new BadRequest("enter the server's base URL, for example https://host/v1");
  }
  const local = ["localhost", "127.0.0.1", "[::1]"].includes(url.hostname);
  if (url.protocol !== "https:" && !(url.protocol === "http:" && local)) {
    throw new BadRequest("the base URL must use https (http is accepted only for localhost)");
  }
  if (url.username || url.password) throw new BadRequest("put the key in the key field, not in the URL");
  return `${url.origin}${url.pathname}`.replace(/\/+$/, "").replace(/\/chat\/completions$/, "");
}

/** The provider, base URL and key a request is about. With no key in the request the saved one is used,
 *  and only for the provider and address it was saved for: a saved key is never sent anywhere else. */
async function llmTarget(body: Record<string, unknown>): Promise<Target> {
  const provider = PROVIDERS.find((p) => p.id === str(body.preset));
  if (!provider) throw new BadRequest(`preset must be one of ${PROVIDERS.map((p) => p.id).join(", ")}`);
  const baseUrl = baseUrlFor(provider, str(body.baseUrl));
  let key = str(body.apiKey);
  if (key.length > 4000) throw new BadRequest("that key is too long");
  if (!key) {
    const saved = await getSecret("llm").catch(() => null);
    if (!saved || saved.preset !== provider.id || saved.base_url !== baseUrl || typeof saved.api_key !== "string") {
      throw new BadRequest(`paste your ${provider.label} key`);
    }
    key = saved.api_key;
  }
  return { provider, baseUrl, key };
}

function authHeaders(t: Target): Record<string, string> {
  return t.provider.family === "anthropic"
    ? { "x-api-key": t.key, "anthropic-version": "2023-06-01", "content-type": "application/json" }
    : { Authorization: `Bearer ${t.key}`, "Content-Type": "application/json" };
}

/** The provider's own words about a failure, with the key removed in case it was echoed. */
function providerMessage(status: number, payload: unknown, key: string): string {
  const p = payload as { error?: { message?: string } | string; message?: string } | string | null;
  let said = "";
  if (typeof p === "string") said = p;
  else if (p && typeof p.error === "string") said = p.error;
  else if (p && p.error && typeof p.error === "object" && typeof p.error.message === "string") said = p.error.message;
  else if (p && typeof p.message === "string") said = p.message;
  said = said.split(key).join("[key]").replace(/\s+/g, " ").trim().slice(0, 300);
  const lead = status === 401 || status === 403 ? "The key was refused" : status === 404 ? "Not found at that address" :
    status === 429 ? "The provider is rate-limiting this key" : `The provider answered HTTP ${status}`;
  return said ? `${lead}: ${said}` : `${lead}.`;
}

async function send(url: string, init: RequestInit, timeoutMs: number): Promise<{ status: number; payload: unknown }> {
  const res = await fetch(url, { ...init, cache: "no-store", signal: AbortSignal.timeout(timeoutMs) });
  const raw = await res.text();
  try {
    return { status: res.status, payload: JSON.parse(raw) };
  } catch {
    return { status: res.status, payload: raw.slice(0, 300) };
  }
}

function unreachable(e: unknown, t: Target): string {
  const timedOut = e instanceof Error && (e.name === "TimeoutError" || e.name === "AbortError");
  return timedOut ? `${t.provider.label} did not answer in time. Try again.` : `Could not reach ${t.provider.label} at ${t.baseUrl}.`;
}

async function listModels(t: Target): Promise<CheckLlmResult> {
  const url = t.provider.family === "anthropic" ? `${t.baseUrl}/v1/models?limit=1000` : `${t.baseUrl}/models`;
  let status: number, payload: unknown;
  try {
    ({ status, payload } = await send(url, { method: "GET", headers: authHeaders(t) }, LIST_TIMEOUT_MS));
  } catch (e) {
    return { ok: false, models: [], message: unreachable(e, t) };
  }
  if (status !== 200) return { ok: false, models: [], message: providerMessage(status, payload, t.key) };
  const p = payload as { data?: unknown; models?: unknown } | unknown[];
  const list = Array.isArray(p) ? p : Array.isArray(p?.data) ? p.data : Array.isArray(p?.models) ? p.models : [];
  const ids = new Set<string>();
  for (const item of list as unknown[]) {
    const m = item as { id?: unknown; name?: unknown } | string;
    const id = typeof m === "string" ? m : typeof m?.id === "string" ? m.id : typeof m?.name === "string" ? m.name : "";
    if (id) ids.add(id.replace(/^models\//, ""));
  }
  const all = [...ids].sort((a, b) => a.localeCompare(b));
  const chat = all.filter((id) => !NOT_CHAT.test(id));
  const models = chat.length ? chat : all;
  if (!models.length) return { ok: true, models, message: "The key works, but the provider listed no models. Type the model's id." };
  return { ok: true, models, message: `The key works. ${models.length} model${models.length === 1 ? "" : "s"} available.` };
}

async function testModel(t: Target, model: string): Promise<SaveLlmResult> {
  const messages = [{ role: "user", content: "Reply with the word ok." }];
  const started = Date.now();
  const failed = (message: string): SaveLlmResult => ({ ok: false, reply: "", latencyMs: Date.now() - started, message });
  try {
    let status: number, payload: unknown;
    if (t.provider.family === "anthropic") {
      ({ status, payload } = await send(`${t.baseUrl}/v1/messages`, {
        method: "POST", headers: authHeaders(t), body: JSON.stringify({ model, max_tokens: TEST_TOKENS, messages }),
      }, TEST_TIMEOUT_MS));
    } else {
      const post = (limit: Record<string, number>) => send(`${t.baseUrl}/chat/completions`, {
        method: "POST", headers: authHeaders(t), body: JSON.stringify({ model, messages, ...limit }),
      }, TEST_TIMEOUT_MS);
      ({ status, payload } = await post({ max_tokens: TEST_TOKENS }));
      // Newer OpenAI models renamed the limit; the worker's client makes the same switch.
      if (status === 400 && /max_tokens|max_completion_tokens/i.test(JSON.stringify(payload))) {
        ({ status, payload } = await post({ max_completion_tokens: TEST_TOKENS }));
      }
    }
    if (status !== 200) return failed(providerMessage(status, payload, t.key));
    const latencyMs = Date.now() - started;
    const reply = replyText(payload).slice(0, 200);
    return { ok: true, reply, latencyMs, message: `${t.provider.label} answered with ${model} in ${(latencyMs / 1000).toFixed(1)} s. Saved.` };
  } catch (e) {
    return failed(unreachable(e, t));
  }
}

function replyText(payload: unknown): string {
  const p = payload as {
    content?: { type?: string; text?: string }[];
    choices?: { message?: { content?: unknown } }[];
  } | null;
  if (Array.isArray(p?.content)) return p.content.filter((b) => b?.type === "text").map((b) => b.text ?? "").join("").trim();
  const c = p?.choices?.[0]?.message?.content;
  return typeof c === "string" ? c.trim() : "";
}

// Groww

/** The key type inside a Groww API key (a JWT), read without verifying it. Same rule as broker/groww.py. */
function growwKeyRole(apiKey: string): string | null {
  try {
    const claims = JSON.parse(Buffer.from(apiKey.split(".")[1] ?? "", "base64url").toString("utf8")) as { sub?: unknown };
    const sub = typeof claims.sub === "string" ? JSON.parse(claims.sub) : claims.sub;
    const role = (sub as { role?: unknown } | null)?.role;
    return typeof role === "string" ? role : null;
  } catch {
    return null;
  }
}

function validateGroww(apiKey: string, totpSecret: string, apiSecret: string): "totp" | "approval" {
  if (!apiKey) throw new BadRequest("paste the API key from groww.in/trade-api/api-keys");
  if (apiKey.length > 4000 || totpSecret.length > 200 || apiSecret.length > 4000) throw new BadRequest("that value is too long");
  if (!totpSecret && !apiSecret) throw new BadRequest("add the TOTP secret (TOTP key) or the API secret (approval key)");
  const base32 = /^[A-Z2-7]+=*$/.test(totpSecret);
  if (growwKeyRole(apiKey) === "auth-totp") {
    if (!totpSecret) throw new BadRequest("this is a TOTP key, so the TOTP secret shown with its QR code is required");
    if (!base32) {
      throw new BadRequest("that is not a TOTP secret: TOTP secrets use only the letters A-Z and the digits 2-7. " +
        "It looks like an API secret; copy the text under the QR code instead.");
    }
    return "totp";
  }
  if (totpSecret && !apiSecret) {
    if (!base32) throw new BadRequest("that is not a TOTP secret: TOTP secrets use only the letters A-Z and the digits 2-7");
    return "totp";
  }
  return "approval";
}

async function queueGrowwCheck(fresh: boolean): Promise<string> {
  const id = crypto.randomUUID();
  await upsert("jobs", { id, created_at: new Date().toISOString(), kind: "groww_check", params: { fresh }, status: "queued", progress: 0 });
  return id;
}
