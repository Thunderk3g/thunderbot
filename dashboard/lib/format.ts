const inrFmt = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 });
const inrFmt2 = new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 2 });

export function inr(n: number | null | undefined, decimals = 0): string {
  if (n === null || n === undefined || Number.isNaN(Number(n))) return "–";
  return (decimals ? inrFmt2 : inrFmt).format(Number(n));
}

export function signedInr(n: number | null | undefined): string {
  if (n === null || n === undefined) return "–";
  const v = Number(n);
  return `${v > 0 ? "+" : ""}${inr(v)}`;
}

export function num(n: number | null | undefined, d = 2): string {
  if (n === null || n === undefined || Number.isNaN(Number(n))) return "–";
  return Number(n).toLocaleString("en-IN", { maximumFractionDigits: d, minimumFractionDigits: 0 });
}

export function pct(n: number | null | undefined, d = 1): string {
  if (n === null || n === undefined) return "–";
  return `${Number(n).toFixed(d)}%`;
}

export function hhmm(iso: string): string {
  // Journal timestamps carry the +05:30 offset; show exchange time regardless of viewer timezone.
  return new Intl.DateTimeFormat("en-IN", { timeZone: "Asia/Kolkata", hour: "2-digit", minute: "2-digit", hour12: false }).format(new Date(iso));
}

export function dayTime(iso: string): string {
  return new Intl.DateTimeFormat("en-IN", {
    timeZone: "Asia/Kolkata", day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit", hour12: false,
  }).format(new Date(iso));
}

export function ago(iso?: string): string {
  if (!iso) return "never";
  const s = Math.max(0, Math.round((Date.now() - new Date(iso).getTime()) / 1000));
  if (s < 60) return `${s}s ago`;
  if (s < 3600) return `${Math.round(s / 60)}m ago`;
  return `${Math.round(s / 3600)}h ago`;
}

export function pnlClass(n: number | null | undefined): string {
  if (!n) return "";
  return Number(n) > 0 ? "up" : "down";
}

export function istDay(iso: string): string {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Kolkata" }).format(new Date(iso));
}
