# Dashboard design

Made with the `frontend-design` skill (vendored in `.claude/skills/frontend-design`, from
github.com/anthropics/skills, Apache-2.0) and checked against a data-visualisation method whose
palette validator computes colour-blind separation and contrast instead of guessing them. These
notes are the plan and a record of what was tried. This is the third version of the interface.

## Brief

- **Subject:** one person's investing bot for Indian ETFs. It wakes once a day at 15:10 IST, checks
  a rule, and on a handful of days a year trades. Intraday research is a side room.
- **Audience:** its owner, who is not a designer or a trader by profession, on a laptop at home and
  on a phone around the market close.
- **Primary job:** answer three questions without reading a manual: what do I hold and what is it
  worth, is the bot awake and when does it act next, and what should I do now (usually nothing).
  Secondary: choose and test a plan, and see what happened.
- **The ask for this pass:** market-standard, easy to understand and operate, with the craft of the
  sites that win Awwwards: confident type, one strong idea per screen, generous space, motion that
  means something. Inspiration is by principle; no site's layout, art or copy was reproduced.

## Tokens

The name is Thunderbot, so the identity is a monsoon sky: one storm-blue slab against rain-washed
paper. The slab is the only saturated surface in the product.

| Role | Light | Dark |
|---|---|---|
| Paper (page) | `#EEF2F5` rain | `#0A1C28` night rain |
| Raised (forms, menus) | `#FFFFFF` | `#102737` |
| Storm (the hero slab) | `#0E2A3B` | `#14364B` |
| Ink | `#0E2A3B` | `#E6EEF4` |
| Ink, soft | `#566878` | `#93A6B6` |
| Rule | `#D5DEE6` | `#1E3B4F` |
| Bolt (logo, "now" marks) | `#F2B01E` | `#F2B01E` |
| Gain | `#0A7D57` | `#3FD0A0` |
| Loss | `#C92F3D` | `#F47F88` |
| Running / caution (status only) | `#0CA30C` / `#F2B01E` | same |

Green for a gain and red for a loss is what every Indian broker app uses, so it is used here; every
figure also carries its sign, and status never relies on colour alone.

**What you hold has a colour, and keeps it everywhere** (mix bar, tables, charts, plan cards):

| Holding | On paper | On storm and in dark mode |
|---|---|---|
| Nifty 50 | `#2F6FED` | `#3F7FEA` |
| Next 50 | `#0E9E8E` | `#13A794` |
| Gold | `#B87900` | `#C4850F` |
| Midcap | `#7C4DDB` | `#8E6BE8` |
| Parked (liquid ETF, cash) | neutral track, not a series colour | same |

Both sets pass the validator on their own surface (lightness band, chroma floor, adjacent
colour-blind ΔE ≥ 12, normal-vision ΔE ≥ 19, contrast ≥ 3:1). Parked money is drawn as the neutral
remainder of the bar because it is the absence of a position, and a grey would fail the chroma floor
as a series anyway.

**Type:** Bricolage Grotesque, one variable family for everything. Its width axis gives narrow,
heavy figures for money (width 75-80, weight 700-800, large optical size) and an easy text face at
15/24 (width 100, weight 400). Tabular figures in every column. The rupee sign lives in the
`latin-ext` subset, which the previous version never loaded, so ₹ used to fall back to a system font.
Scale: 13 · 15 · 17 · 21 · 28 · 40 · 64 · 72-128 (hero).

**Layout:** a top bar that never leaves: wordmark, five plain words, what the bot is doing, and the
one control that matters (Start, or hold to stop). Content sits in one centred column up to 1200px,
left-aligned inside it. On phones the words move to a bottom bar with icons.

```
┌───────────────────────────────────────────────────────────────────────────────┐
│ ϟ Thunderbot    Home  Plans  Results  Activity  Settings   ● Investing  [Stop]│
├───────────────────────────────────────────────────────────────────────────────┤
│ ╔═══════════════════════════ storm slab ═══════════════════════════════════╗ │
│ ║ ₹4,99,337                                         Next check              ║ │
│ ║ −₹663 since you started with ₹5,00,000            Today, 15:10 IST        ║ │
│ ║                                                    in 2 h 14 min          ║ │
│ ║ ▇▇▇▇▇▇ 33% ▇▇▇▇▇▇▇▇ 33% ▇▇▇▇▇▇▇▇ 33% ░░ parked                             ║ │
│ ║ ■ Nifty 50   ■ Next 50   ■ Gold                                           ║ │
│ ╚════════════════════════════════════════════════════════════════════════════╝ │
│  What you hold (table)                    │  What happens next (three lines)   │
│  Orders to copy into Groww                │  Activity                          │
└───────────────────────────────────────────────────────────────────────────────┘
```

## Principles

1. **One slab, one idea.** Home opens on the storm slab: what the portfolio is worth, how it is
   split, and when the bot acts next. Nothing else on any screen is that loud.
2. **Say what to do.** Every screen leads with a sentence in the owner's words, and a first visit
   shows the three steps to a running bot (wake it, pick a plan, start) instead of an empty dashboard.
   Orders appear as a list to copy into the Groww app, sells first.
3. **Plans, not parameters.** The Lab is a sequence: choose a plan, test it on 15 years, use it. The
   sliders are behind "Fine-tune". Every result is shown next to doing less.
4. **Open sections, few boxes.** Sections are separated by space and one rule. Boxes are for things
   you edit and things you choose between. Radius by role: 8px controls, 16px surfaces, 28px the slab.
5. **Motion for meaning.** One load moment (the figure settles, the mix bar fills left to right), the
   nav marker slides, the stop button fills while held. Nothing loops except the running dot.

## Review against the generic default

A "fintech dashboard" prompt lands on white, an indigo primary, a sidebar of icons, a grid of rounded
KPI cards with soft shadows, a donut chart and Inter. Changes made after checking the first draft of
this plan against that:

- Dropped an indigo-on-white first draft: it was the SaaS kit with a different logo. The storm slab
  on rain paper comes from the product's own name.
- No KPI card grid and no drop shadows on content. The hero is one slab; the rest is open type.
- The allocation is a labelled bar at the chart method's 28px, not a donut: three parts of one
  whole read faster in a line, and the bar sits under the figure it explains.
- A second display typeface was dropped. One family, used with intent, also keeps the big figure
  in the same voice as the rest.
- Lime-on-black "terminal" styling was never on the table: it is the other cliché, and the owner
  asked for something easy to read.

## Notes for next time

- v1 (Oct 2026) was the SaaS card kit. v2 was a quiet left rail with Archivo and a blue/red pair,
  built around the intraday session. v3 (this one) is built around daily investing.
- If a new holding is added, give it the next validated colour; do not reuse a status colour.
- If adding a page, start from the sentence that answers the page's question, then the detail.
