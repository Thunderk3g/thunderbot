"use client";

import { useCallback, useEffect, useRef, useState } from "react";

/** Poll a JSON endpoint; pauses while the tab is hidden and keeps the last good data on errors. */
export function usePoll<T>(url: string | null, intervalMs: number) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const alive = useRef(true);

  const load = useCallback(async () => {
    if (!url) return;
    try {
      const res = await fetch(url, { cache: "no-store" });
      const json = await res.json();
      if (!res.ok) throw new Error(json.error ?? res.statusText);
      if (alive.current) { setData(json as T); setError(null); }
    } catch (e) {
      if (alive.current) setError(e instanceof Error ? e.message : String(e));
    }
  }, [url]);

  useEffect(() => {
    alive.current = true;
    let stopped = false;
    const loop = async () => {
      if (stopped) return;
      if (document.visibilityState === "visible") await load();
      timer.current = setTimeout(loop, intervalMs);
    };
    loop();
    const onVis = () => { if (document.visibilityState === "visible") load(); };
    document.addEventListener("visibilitychange", onVis);
    return () => {
      stopped = true;
      alive.current = false;
      if (timer.current) clearTimeout(timer.current);
      document.removeEventListener("visibilitychange", onVis);
    };
  }, [load, intervalMs]);

  return { data, error, refresh: load };
}

export async function post<T = unknown>(url: string, body: unknown): Promise<T> {
  const res = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const json = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(json.error ?? res.statusText);
  return json as T;
}


/** Queue a research job, then wake the serverless worker to run it now. Where no such function exists
 *  (local `thunderbot serve`, a long-running worker) the wake-up fails quietly and the worker's own
 *  job loop picks the job up. */
export async function startJob(kind: "backtest" | "sweep" | "invest", params: Record<string, unknown>): Promise<string> {
  const { id } = await post<{ id: string }>("/api/jobs", { kind, params });
  void fetch(`/api/worker?op=job&id=${encodeURIComponent(id)}`, { method: "POST" }).catch(() => undefined);
  return id;
}

/** One pass of the serverless worker, on demand. Throws if the function is not deployed or fails. */
export async function wakeWorker(): Promise<{ did?: string }> {
  const res = await fetch("/api/worker?op=tick", { method: "POST" });
  const json = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(json.error ?? (res.status === 404 ? "there is no worker function on this deployment" : res.statusText));
  return json;
}
