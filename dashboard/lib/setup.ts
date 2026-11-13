// Shapes shared by the setup API (app/api/setup) and the setup screen. No secrets and no server code here.

export type ProviderFamily = "anthropic" | "openai_compatible";

export type ProviderInfo = {
  id: string;
  label: string;
  family: ProviderFamily;
  /** Empty for "custom": the owner types it. */
  baseUrl: string;
  /** Where to create a key. Empty for "custom". */
  keyUrl: string;
  /** What a key from this provider looks like, e.g. "sk-ant-…". */
  keyHint: string;
  note?: string;
};

// Base URLs are mirrored in worker/thunderbot/llm/provider.py. Model names are never listed here:
// the screen asks the provider for them.
export const PROVIDERS: ProviderInfo[] = [
  { id: "anthropic", label: "Anthropic (Claude)", family: "anthropic", baseUrl: "https://api.anthropic.com",
    keyUrl: "https://console.anthropic.com/settings/keys", keyHint: "sk-ant-…" },
  { id: "xai", label: "xAI (Grok)", family: "openai_compatible", baseUrl: "https://api.x.ai/v1",
    keyUrl: "https://console.x.ai", keyHint: "xai-…" },
  { id: "groq", label: "Groq", family: "openai_compatible", baseUrl: "https://api.groq.com/openai/v1",
    keyUrl: "https://console.groq.com/keys", keyHint: "gsk_…",
    note: "Fast, with a free tier. Most of its models return JSON on a best-effort basis; a reply that cannot be read counts as a failed call and the trade is skipped." },
  { id: "openai", label: "OpenAI", family: "openai_compatible", baseUrl: "https://api.openai.com/v1",
    keyUrl: "https://platform.openai.com/api-keys", keyHint: "sk-…" },
  { id: "gemini", label: "Google Gemini", family: "openai_compatible",
    baseUrl: "https://generativelanguage.googleapis.com/v1beta/openai",
    keyUrl: "https://aistudio.google.com/apikey", keyHint: "AIza…" },
  { id: "openrouter", label: "OpenRouter", family: "openai_compatible", baseUrl: "https://openrouter.ai/api/v1",
    keyUrl: "https://openrouter.ai/keys", keyHint: "sk-or-…",
    note: "One key for many providers' models." },
  { id: "custom", label: "Other (OpenAI-compatible)", family: "openai_compatible", baseUrl: "", keyUrl: "", keyHint: "",
    note: "Any server that speaks the chat-completions protocol. http:// is accepted only for localhost." },
];

export type GrowwCheck = {
  ok: boolean;
  at: string;
  steps: { name: string; ok: boolean; detail: string }[];
  ip: { observed: string | null; expected: string | null; ok: boolean } | null;
};

export type SetupState = {
  store: { ready: boolean; keySource: "TB_SECRET_KEY" | "service_key" | null; problem?: string };
  providers: ProviderInfo[];
  llm: {
    configured: boolean;
    source: "dashboard" | "environment" | null;
    preset: string | null;
    provider: string | null;
    baseUrl: string | null;
    model: string | null;
    hint: string | null;
    updatedAt: string | null;
    enabled: boolean;
  };
  groww: {
    configured: boolean;
    source: "dashboard" | "environment" | null;
    auth: "totp" | "approval" | null;
    hint: string | null;
    updatedAt: string | null;
    lastCheck: GrowwCheck | null;
  };
  /** Read from the worker's published settings; display only. Real orders are switched on where the worker runs. */
  live: { enabled: boolean; staticIp: string | null };
};

// POST /api/setup bodies, by `action`.
export type SetupAction =
  | { action: "check_llm"; preset: string; baseUrl?: string; apiKey?: string }
  | { action: "save_llm"; preset: string; baseUrl?: string; apiKey?: string; model: string }
  | { action: "clear_llm" }
  | { action: "save_groww"; apiKey: string; totpSecret?: string; apiSecret?: string }
  | { action: "check_groww" }
  | { action: "clear_groww" };

export type CheckLlmResult = { ok: boolean; models: string[]; message: string };
export type SaveLlmResult = { ok: boolean; reply: string; latencyMs: number; message: string };
/** `jobId` is a `groww_check` job: poll GET /api/jobs?id=…; its `result` is a GrowwCheck. */
export type GrowwJobResult = { ok: boolean; jobId: string };
export type ClearResult = { ok: boolean };
