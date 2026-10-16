# Dashboard design

Made with the `frontend-design` skill (vendored in `.claude/skills/frontend-design`, from
github.com/anthropics/skills, Apache-2.0). These notes are the plan and a record of what was tried.

## Brief

- **Subject:** the control room of one person's NSE intraday trading bot.
- **Audience:** its owner, on a laptop at home and on a phone during market hours.
- **Primary job:** answer "is it making money right now, is it healthy?" in one glance, and stop it
  in one gesture. Secondary: research strategies (Lab) and change limits (Settings).

## Tokens

| Role | Light | Dark |
|---|---|---|
| Paper (page) | `#F3F5F7` slate paper | `#101B26` harbour |
| Raised (forms, popovers) | `#FBFCFD` | `#162433` |
| Ink | `#17232F` | `#E4EBF1` |
| Ink, soft | `#556372` | `#93A3B3` |
| Rule | `#D5DCE3` | `#22313F` |
| Gain | `#2A6FC9` | `#4A90E8` |
| Loss | `#D6453D` | `#E66259` |
| Running (status only) | `#0CA30C` | `#0CA30C` |
| Caution (status only) | `#FAB219` | `#FAB219` |

Gain and loss pass the data-viz palette validator (CVD ΔE ≥ 20, contrast ≥ 3:1) on both papers.
Blue/red rather than green/red so the pair survives red-green colour blindness; every P&L value
also carries its sign.

**Type:** Archivo, one variable family with a width axis. Condensed width (~70) and weight 700 for
the money and tickers, like an exchange price board: long NSE symbols (HDFCBANK, ICICIBANK) stay
compact and numbers read as instruments. Normal width, weight 400 for prose at 15/24. Scale:
13 · 15 · 18 · 24 · 40 · 88. Tabular figures only in columns.

**Layout:** a quiet left rail with five plain words (Today, Results, Lab, Settings, Log), the
running state and the stop control. Content is left-aligned in one column up to 1120px; numbers
right-aligned in tables. On phones the rail becomes a top status bar and a bottom tab bar.

```
┌────────┬──────────────────────────────────────────────────────┐
│Thunder │ −₹332                                                 │
│bot     │ after costs, from 1 trade. Nothing open.              │
│        │ ┌ 09:15 ──────────────────────────┬now──────── 15:30 ┐│
│Today   │ │ opening │   entries open        │ managing │ flat   ││
│Results │ │  ───────╲___________/‾‾‾‾‾‾‾‾‾‾‾ (P&L through day)   ││
│Lab     │ └──────────────────────────────────────────────────────┘│
│Settings│ Positions              │ Signals                       │
│Log     │ RELIANCE  Long 42 −₹120│ 10:45 RELIANCE sell  approved │
│        │ stop ─────●──── target │ 11:25 ITC sell       vetoed   │
│● Paper │                        │                               │
│[Hold to│                        │                               │
│  stop] │                        │                               │
└────────┴──────────────────────────────────────────────────────┘
```

## Principles

1. **The trading day organises everything.** Today hangs off one ribbon from 09:15 to 15:30,
   showing the bot's own schedule (opening range, entries open, managing only, flat), the P&L line
   through the day, each closed trade, and a "now" cursor. That ribbon is the one bold element.
2. **Quiet everywhere else.** No drop shadows. Boxes only around things you edit (forms) or that
   float (toasts, save bar). Sections are separated by space and alignment. Radius by role: 6px on
   controls, 10px on panels, none on page sections.
3. **Sentences over tiles.** Summaries are written out ("Down ₹332 after costs, from 1 trade")
   instead of rows of stat boxes; key figures sit in a plain definition grid.
4. **Motion for meaning.** One load-in moment (the day's line draws itself) and motion that answers
   an action: holding the stop, expanding a signal, saving settings. A new signal arriving slides in
   because it's news. Nothing else animates on its own.

## Review against the generic default

A generic "trading dashboard" prompt lands on: near-black with neon green/red, a grid of identical
rounded KPI cards, Inter, a big number with a row of stat tiles, and monospace labels. Changes made
after checking the first draft of this plan against that:

- Dropped a navy-and-brass "private bank" palette: a finance cliché, not specific to this bot.
- Dropped a serif display face (cluster #1 in the skill's calibration list).
- Replaced the KPI tile row in the hero with one written sentence, and made the session ribbon,
  which only this product has, carry the visual weight.
- Removed every middle-dot meta string, all-caps label, monospace label and per-card entrance
  animation from the first version of the UI.

## Notes for next time

- The first version (Oct 2026) used the SaaS card kit; screenshots in `docs/screenshots/` before
  this pass show it. Don't drift back.
- If adding a page, start from a sentence that answers the page's question, then the detail.
