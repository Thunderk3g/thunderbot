// What each holding is called and which colour it keeps everywhere (docs/design.md).

export type AssetKind = "nifty" | "next50" | "gold" | "mid" | "parked";

const KNOWN: Record<string, { name: string; kind: AssetKind }> = {
  NIFTYBEES: { name: "Nifty 50", kind: "nifty" },
  JUNIORBEES: { name: "Next 50", kind: "next50" },
  GOLDBEES: { name: "Gold", kind: "gold" },
  MOM100: { name: "Midcap", kind: "mid" },
  LIQUID: { name: "Liquid ETF", kind: "parked" },
  LIQUIDCASE: { name: "Liquid ETF", kind: "parked" },
  LIQUIDBEES: { name: "Liquid ETF", kind: "parked" },
  LIQUIDADD: { name: "Liquid ETF", kind: "parked" },
  CASH: { name: "Cash", kind: "parked" },
};

/** Stocks from the momentum plan share one colour: they are one sleeve, not fifteen series. */
export function asset(symbol: string): { name: string; kind: AssetKind; known: boolean } {
  const a = KNOWN[symbol];
  return a ? { ...a, known: true } : { name: symbol, kind: "mid", known: false };
}

export type Slice = { key: string; name: string; kind: AssetKind; pct: number };

/** Weights (in %) grouped into the bar's segments, in a fixed order; whatever is missing from 100 is parked cash. */
export function slices(weights: Record<string, number>): Slice[] {
  const order: AssetKind[] = ["nifty", "next50", "gold", "mid", "parked"];
  const by = new Map<AssetKind, Slice>();
  let total = 0;
  for (const [symbol, pct] of Object.entries(weights)) {
    if (!(pct > 0)) continue;
    const a = asset(symbol);
    total += pct;
    const name = a.known ? a.name : "Stocks";
    const cur = by.get(a.kind);
    by.set(a.kind, cur ? { ...cur, pct: cur.pct + pct, name: cur.name === name ? name : a.kind === "parked" ? "Parked" : cur.name }
      : { key: a.kind, name, kind: a.kind, pct });
  }
  const spare = 100 - total;
  if (spare > 0.5) {
    const cur = by.get("parked");
    by.set("parked", cur ? { ...cur, pct: cur.pct + spare, name: "Parked" } : { key: "parked", name: "Cash", kind: "parked", pct: spare });
  }
  return order.map((k) => by.get(k)).filter((x): x is Slice => !!x);
}
