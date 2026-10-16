"use client";

import { AnimatePresence, animate, motion, useMotionValue, useReducedMotion, useSpring, useTransform } from "motion/react";
import { X } from "lucide-react";
import { useEffect, useId, useRef, useState, type ReactNode } from "react";

export const spring = { type: "spring" as const, stiffness: 420, damping: 36, mass: 0.8 };

/** A number that springs to its new value when data changes. */
export function AnimatedNumber({ value, format, className }: { value: number; format: (n: number) => string; className?: string }) {
  const reduce = useReducedMotion();
  const mv = useSpring(value, { stiffness: 140, damping: 26, mass: 0.6 });
  const text = useTransform(mv, (v) => format(v));
  useEffect(() => {
    if (reduce) mv.jump(value);
    else mv.set(value);
  }, [value, mv, reduce]);
  return <motion.span className={className}>{text}</motion.span>;
}

/** A page section: a heading line and content, separated from neighbours by space, not a box. */
export function Section({ title, aside, children, className = "" }: { title?: ReactNode; aside?: ReactNode; children: ReactNode; className?: string }) {
  return (
    <section className={`section ${className}`}>
      {(title || aside) && (
        <div className="section-head">
          {title && <h2>{title}</h2>}
          {aside}
        </div>
      )}
      {children}
    </section>
  );
}

/** A raised panel, used only around forms. */
export function Panel({ title, aside, children }: { title?: ReactNode; aside?: ReactNode; children: ReactNode }) {
  return (
    <div className="panel">
      {(title || aside) && (
        <div className="section-head" style={{ marginBottom: 14 }}>
          {title && <h2 style={{ margin: 0 }}>{title}</h2>}
          {aside}
        </div>
      )}
      {children}
    </div>
  );
}

export function Figures({ items }: { items: { label: string; value: ReactNode; tone?: "gain" | "loss" | "" }[] }) {
  return (
    <dl className="figures">
      {items.map((i) => (
        <div className="figure" key={i.label}>
          <dt>{i.label}</dt>
          <dd className={i.tone ?? ""}>{i.value}</dd>
        </div>
      ))}
    </dl>
  );
}

export function StatusDot({ on }: { on: boolean }) {
  const reduce = useReducedMotion();
  return (
    <span className={`dot ${on ? "on" : "off"}`} aria-hidden>
      {on && !reduce && (
        <motion.span style={{ position: "absolute", inset: 0, borderRadius: "50%", background: "var(--running)" }}
          animate={{ scale: [1, 2.2], opacity: [0.5, 0] }} transition={{ duration: 2, repeat: Infinity, ease: "easeOut" }} />
      )}
    </span>
  );
}

export function Button({ children, variant = "", size = "", onClick, disabled, type = "button", title, block }: {
  children: ReactNode; variant?: "" | "primary" | "stop" | "quiet"; size?: "" | "sm"; onClick?: () => void;
  disabled?: boolean; type?: "button" | "submit"; title?: string; block?: boolean;
}) {
  return (
    <motion.button type={type} className={`btn ${variant} ${size} ${block ? "block" : ""}`} onClick={onClick} disabled={disabled} title={title}
      whileTap={disabled ? undefined : { scale: 0.97 }} transition={spring}>
      {children}
    </motion.button>
  );
}

/** Press and hold to confirm, so the stop can't be hit by accident. */
export function HoldButton({ children, onConfirm, duration = 1.1, block }: { children: ReactNode; onConfirm: () => void; duration?: number; block?: boolean }) {
  const progress = useMotionValue(0);
  const ctrl = useRef<ReturnType<typeof animate> | null>(null);
  const start = () => {
    ctrl.current?.stop();
    ctrl.current = animate(progress, 1, {
      duration: duration * (1 - progress.get()), ease: "linear",
      onComplete: () => { onConfirm(); progress.set(0); },
    });
  };
  const cancel = () => {
    ctrl.current?.stop();
    ctrl.current = animate(progress, 0, { duration: 0.2 });
  };
  return (
    <button type="button" className={`btn stop hold ${block ? "block" : ""}`} onPointerDown={start} onPointerUp={cancel} onPointerLeave={cancel}
      onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); if (!e.repeat) start(); } }}
      onKeyUp={(e) => { if (e.key === "Enter" || e.key === " ") cancel(); }}
      aria-label="Stop trading: press and hold">
      <motion.div className="hold-fill" style={{ scaleX: progress }} />
      <span>{children}</span>
    </button>
  );
}

export function Segmented<T extends string>({ options, value, onChange, label }: {
  options: { value: T; label: ReactNode }[]; value: T; onChange: (v: T) => void; label?: string;
}) {
  const id = useId();
  return (
    <div className="seg" role="group" aria-label={label}>
      {options.map((o) => (
        <button key={o.value} type="button" aria-pressed={o.value === value} onClick={() => onChange(o.value)}>
          {o.value === value && <motion.div layoutId={`seg-${id}`} className="seg-pill" transition={spring} />}
          <span>{o.label}</span>
        </button>
      ))}
    </div>
  );
}

export function Switch({ checked, onChange, label }: { checked: boolean; onChange: (v: boolean) => void; label: string }) {
  return (
    <button type="button" role="switch" aria-checked={checked} aria-label={label} className="switch" onClick={() => onChange(!checked)}>
      <motion.span className="knob" animate={{ x: checked ? 16 : 0 }} transition={spring} />
    </button>
  );
}

export function SliderField({ label, value, min, max, step, onChange, suffix, hint }: {
  label: string; value: number; min: number; max: number; step: number; onChange: (v: number) => void; suffix?: string; hint?: string;
}) {
  const [text, setText] = useState(String(value));
  useEffect(() => setText(String(value)), [value]);
  const commit = (raw: string) => {
    const v = Number(raw);
    if (Number.isFinite(v)) onChange(Math.min(max, Math.max(min, v)));
    else setText(String(value));
  };
  return (
    <div className="field">
      <label><span>{label}</span>{hint && <span className="hint">{hint}</span>}</label>
      <div className="slider-row">
        <input type="range" min={min} max={max} step={step} value={value} aria-label={label} onChange={(e) => onChange(Number(e.target.value))} />
        <div style={{ position: "relative" }}>
          <input className="input tnum" inputMode="decimal" value={text} aria-label={`${label} value`}
            onChange={(e) => setText(e.target.value)} onBlur={(e) => commit(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") commit((e.target as HTMLInputElement).value); }} />
          {suffix && <span className="hint" style={{ position: "absolute", right: 9, top: 8 }}>{suffix}</span>}
        </div>
      </div>
    </div>
  );
}

export function ChipsInput({ values, onChange, placeholder }: { values: string[]; onChange: (v: string[]) => void; placeholder?: string }) {
  const [draft, setDraft] = useState("");
  const add = (raw: string) => {
    const items = raw.split(/[\s,]+/).map((s) => s.trim().toUpperCase()).filter(Boolean);
    if (items.length) onChange([...new Set([...values, ...items])]);
    setDraft("");
  };
  return (
    <div className="chips">
      <AnimatePresence initial={false}>
        {values.map((v) => (
          <motion.span key={v} className="chip ticker" layout initial={{ opacity: 0, scale: 0.85 }} animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.85 }} transition={spring}>
            {v}
            <button type="button" aria-label={`Remove ${v}`} onClick={() => onChange(values.filter((x) => x !== v))}><X size={13} /></button>
          </motion.span>
        ))}
      </AnimatePresence>
      <input value={draft} placeholder={placeholder} aria-label="Add symbol" onChange={(e) => setDraft(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === "," || e.key === " ") { e.preventDefault(); add(draft); }
          if (e.key === "Backspace" && !draft && values.length) onChange(values.slice(0, -1));
        }}
        onBlur={() => draft && add(draft)} />
    </div>
  );
}

export function Progress({ value }: { value: number }) {
  return (
    <div className="progress" role="progressbar" aria-valuenow={Math.round(value * 100)} aria-valuemin={0} aria-valuemax={100}>
      <motion.div initial={{ width: 0 }} animate={{ width: `${Math.max(3, value * 100)}%` }} transition={{ type: "spring", stiffness: 120, damping: 22 }} />
    </div>
  );
}

export function Empty({ title, children }: { title: string; children?: ReactNode }) {
  return <div className="empty"><strong>{title}</strong>{children}</div>;
}

export function Skeleton({ height = 16, width = "100%" }: { height?: number; width?: number | string }) {
  return <div className="shimmer" style={{ height, width }} />;
}
