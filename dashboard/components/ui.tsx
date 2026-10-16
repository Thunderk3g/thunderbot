"use client";

import { AnimatePresence, animate, motion, useMotionValue, useReducedMotion, useSpring, useTransform } from "motion/react";
import { X } from "lucide-react";
import { useEffect, useId, useRef, useState, type ReactNode } from "react";

export const spring = { type: "spring" as const, stiffness: 420, damping: 34, mass: 0.8 };
export const fadeUp = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -6 },
  transition: { duration: 0.22, ease: [0.22, 1, 0.36, 1] as const },
};

/** A number that springs to its new value. */
export function AnimatedNumber({ value, format, className }: { value: number; format: (n: number) => string; className?: string }) {
  const reduce = useReducedMotion();
  const mv = useSpring(value, { stiffness: 140, damping: 24, mass: 0.6 });
  const text = useTransform(mv, (v) => format(v));
  useEffect(() => {
    if (reduce) mv.jump(value);
    else mv.set(value);
  }, [value, mv, reduce]);
  return <motion.span className={className}>{text}</motion.span>;
}

export function Card({ title, icon, action, children, className = "", delay = 0 }: {
  title?: ReactNode; icon?: ReactNode; action?: ReactNode; children: ReactNode; className?: string; delay?: number;
}) {
  return (
    <motion.section className={`card ${className}`} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay, ease: [0.22, 1, 0.36, 1] }}>
      {(title || action) && (
        <div className="card-head">
          <h2 className="card-title">{icon}{title}</h2>
          {action}
        </div>
      )}
      {children}
    </motion.section>
  );
}

export function Stat({ label, value, format, tone, foot }: {
  label: string; value: number | null | undefined; format: (n: number) => string; tone?: "auto" | "none"; foot?: ReactNode;
}) {
  const cls = tone === "auto" && value ? (value > 0 ? "up" : "down") : "";
  return (
    <motion.div className="stat" layout initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }}>
      <div className="label">{label}</div>
      <div className={`value ${cls}`}>
        {value === null || value === undefined ? "–" : <AnimatedNumber value={value} format={format} />}
      </div>
      {foot && <div className="foot">{foot}</div>}
    </motion.div>
  );
}

export function Badge({ tone = "", children, title }: { tone?: "" | "blue" | "good" | "bad" | "warn" | "live"; children: ReactNode; title?: string }) {
  return <span className={`badge ${tone}`} title={title}>{children}</span>;
}

export function Pulse({ on }: { on: boolean }) {
  return (
    <span className={`dot ${on ? "on" : "off"}`} aria-label={on ? "online" : "offline"}>
      {on && (
        <motion.span style={{ position: "absolute", inset: 0, borderRadius: "50%", background: "var(--good)" }}
          animate={{ scale: [1, 2.4], opacity: [0.6, 0] }} transition={{ duration: 1.6, repeat: Infinity, ease: "easeOut" }} />
      )}
    </span>
  );
}

export function Button({ children, variant = "", size = "", onClick, disabled, type = "button", title }: {
  children: ReactNode; variant?: "" | "primary" | "danger" | "ghost"; size?: "" | "sm"; onClick?: () => void;
  disabled?: boolean; type?: "button" | "submit"; title?: string;
}) {
  return (
    <motion.button type={type} className={`btn ${variant} ${size}`} onClick={onClick} disabled={disabled} title={title}
      whileTap={disabled ? undefined : { scale: 0.96 }} whileHover={disabled ? undefined : { y: -1 }} transition={spring}>
      {children}
    </motion.button>
  );
}

/** Press and hold to confirm. Used for the kill switch so it can't be hit by accident. */
export function HoldButton({ children, onConfirm, duration = 1.1, variant = "danger" }: {
  children: ReactNode; onConfirm: () => void; duration?: number; variant?: "danger" | "primary";
}) {
  const progress = useMotionValue(0);
  const ctrl = useRef<ReturnType<typeof animate> | null>(null);
  const start = () => {
    ctrl.current?.stop();
    ctrl.current = animate(progress, 1, { duration: duration * (1 - progress.get()), ease: "linear", onComplete: () => {
      onConfirm();
      progress.set(0);
    } });
  };
  const cancel = () => {
    ctrl.current?.stop();
    ctrl.current = animate(progress, 0, { duration: 0.25 });
  };
  return (
    <motion.button type="button" className={`btn ${variant} hold`} onPointerDown={start} onPointerUp={cancel} onPointerLeave={cancel}
      onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); if (!e.repeat) start(); } }}
      onKeyUp={(e) => { if (e.key === "Enter" || e.key === " ") cancel(); }}
      whileTap={{ scale: 0.97 }} title="Press and hold to confirm">
      <motion.div className="hold-fill" style={{ scaleX: progress }} />
      <span>{children}</span>
    </motion.button>
  );
}

export function Segmented<T extends string>({ options, value, onChange }: {
  options: { value: T; label: ReactNode }[]; value: T; onChange: (v: T) => void;
}) {
  const id = useId();
  return (
    <div className="seg" role="group">
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
      <label><span>{label}</span>{hint && <span className="subtle">{hint}</span>}</label>
      <div className="slider-row">
        <input type="range" min={min} max={max} step={step} value={value} aria-label={label}
          onChange={(e) => onChange(Number(e.target.value))} />
        <div style={{ position: "relative" }}>
          <input className="input" inputMode="decimal" value={text} aria-label={`${label} value`}
            onChange={(e) => setText(e.target.value)} onBlur={(e) => commit(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") commit((e.target as HTMLInputElement).value); }} />
          {suffix && <span className="subtle" style={{ position: "absolute", right: 10, top: 9 }}>{suffix}</span>}
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
          <motion.span key={v} className="chip" layout initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }} transition={spring}>
            {v}
            <button type="button" aria-label={`remove ${v}`} onClick={() => onChange(values.filter((x) => x !== v))}><X size={13} /></button>
          </motion.span>
        ))}
      </AnimatePresence>
      <input value={draft} placeholder={placeholder} onChange={(e) => setDraft(e.target.value)}
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
      <motion.div initial={{ width: 0 }} animate={{ width: `${Math.max(4, value * 100)}%` }} transition={{ type: "spring", stiffness: 120, damping: 20 }} />
    </div>
  );
}

export function Empty({ title, hint, icon }: { title: string; hint?: ReactNode; icon?: ReactNode }) {
  return (
    <motion.div className="empty" {...fadeUp}>
      {icon && <div style={{ marginBottom: 8, opacity: 0.6 }}>{icon}</div>}
      <div className="title">{title}</div>
      {hint && <div>{hint}</div>}
    </motion.div>
  );
}

export function Skeleton({ height = 16, width = "100%" }: { height?: number; width?: number | string }) {
  return <div className="shimmer" style={{ height, width }} />;
}
