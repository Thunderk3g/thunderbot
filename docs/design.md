# Dashboard design

Made with the `frontend-design` skill (vendored in `.claude/skills/frontend-design`, from
github.com/anthropics/skills, Apache-2.0). These notes are the plan and a record of what was tried.
This is the fourth version of the interface, called "the line".

## Brief

- **Subject:** a portfolio manager one person runs for themselves. Rules decide; an LLM can only say
  no, less or later; a journal shows whether each part earned its place.
- **Audience:** a part-time investor or trader who does not yet understand how the machine works, on
  a laptop at home and on a phone around the market close.
- **Primary job:** make the machine legible. What do I hold, what will it do next, and for any decision,
  where exactly in the chain was it taken, shrunk or stopped.
- **The ask for this pass:** free rein, and not the generic generated dashboard.

## The one idea: the line

Thunder plus harness is a conductor. Every decision is drawn as a line that runs left to right from a
rule to an order, through gates. A gate is drawn as a switch:

```
 rule ●━━━━━━●━●━━━━━━●━●━━━━━━●━●━━━━━━▶ order     every switch closed: taken whole
 rule ●━━━━━━●━●━━━━━━●─●──────●─●──────▷ order     the LLM asked for half: the line runs on thinner
 rule ●━━━━━━●╱○┈┈┈┈┈┈○ ○┈┈┈┈┈┈○ ○┈┈┈┈┈┈○ not traded  the model opened its switch: the line stops there
 rule ●━━━━━━●━●━━━━━━┤ ├━━━━━━●━●━━━━━━▶ order     an empty holder: no LLM fitted, the line runs through
```

- **Thickness is the share of normal size that is left.** It can only stay the same or get thinner,
  because that is what the engine guarantees.
- **A lifted arm is a break.** Everything after it is dotted: those gates were never asked.
- **An empty holder** means an optional part is not fitted (no LLM connected). It is not a fault.

The same picture is used in five places, so it is learned once:

| Where | What the line is |
|---|---|
| Desk, every setup | Rule → model → LLM → limits → order |
| Home | The last daily check: plan → decision day → price check → LLM check → orders |
| Setup | What is connected: scheduler → prices → LLM → Groww → orders |
| The rail | The same connections, drawn top to bottom, always on screen |
| Guide | One setup under four outcomes, with buttons to switch between them |

`dashboard/components/Line.tsx` is the whole of it.

## Tokens

The name is Thunderbot, so the palette is a storm: violet sky, yellow lightning. They are also the
colours of the ₹100 and ₹200 notes, which is the other thing this product is about.

| Role | Light | Dark |
|---|---|---|
| Paper (page) | `#ECE9F2` washed lavender | `#140D22` night violet |
| Raised (forms) | `#F8F6FB` | `#1D1431` |
| Ink | `#1C1230` | `#EEE9F7` |
| Ink, soft | `#625878` | `#A79DC0` |
| Rule | `#D3CCE1` | `#32264E` |
| Storm (the hero slab) | `#2A1A4A` | `#2B1B52` |
| Bolt (the mark, live nodes, "go") | `#F5B301` | `#F7BC1F` |
| The line | ink | bolt: in the dark the line is lightning |
| Gain | `#08704B` | `#4AD6A5` |
| Loss | `#C4283C` | `#FF8793` |

No gradients as decoration and no drop shadows except under things that float. Green for a gain and
red for a loss is what every Indian broker app uses, so it is used here; every figure also carries its
sign.

Holdings keep one colour each everywhere: Nifty 50 `#2F6FED`, Next 50 `#0E9E8E`, gold `#B87900`,
stocks `#C2408F`. Parked money is the neutral remainder of the bar, because it is the absence of a
position.

## Type

**Anek Latin**, by Ek Type in Mumbai, one variable family with a width axis, used three ways:

- narrow and heavy (width 78 to 86, weight 700 to 750) for money and tickers, like a price board;
- normal (width 100, weight 400) for reading, at 15.5/24;
- wide (width 112 to 122, weight 600) for titles.

**Literata italic** is the second face and has exactly one job: words an LLM wrote. A rationale, a
day's review, a lesson. If it is in italic serif, a model said it; everything else was written by rules.
That makes the typeface carry information the owner needs, and it is the only place a serif appears.

Tabular figures in every column. A monospace face appears only inside key inputs and `code`.

## Layout

A rail on the left that never leaves: the wordmark, seven plain words, the system line, the stop
control. Content is one left-aligned column up to 1240px. On phones the rail becomes a top bar with
the stop control and a bottom tab bar.

```
┌──────────────┬──────────────────────────────────────────────────────────┐
│ ⚡ Thunderbot │  ┌──────────────── storm slab ─────────────────────────┐ │
│              │  │ ₹5,07,958                          Next check        │ │
│ Home         │  │ +₹7,958 since you started…         Monday, 15:10     │ │
│ Desk         │  │ [ Nifty 50 ][ Next 50 ][ Gold ]        (engraving)   │ │
│ Plans        │  └──────────────────────────────────────────────────────┘ │
│ Results      │  The last decision                                        │
│ Journal      │  ●━━━━━━━●━●━━━━━━━●━●━━━━━━━┤ ├━━━━━━━▶                  │
│ Guide        │  Plan     Decision day  Price check  LLM check  3 orders  │
│ Setup        │                                                           │
│              │  What you hold                 │ What happens next        │
│ ● Scheduler  │                                                           │
│ ┃            │                                                           │
│ ● Prices     │                                                           │
│ ┊            │                                                           │
│ ○ LLM        │                                                           │
│ ┊            │                                                           │
│ ○ Groww      │                                                           │
│ ● Paper      │                                                           │
│ [Hold to stop]                                                           │
└──────────────┴──────────────────────────────────────────────────────────┘
```

Sections are separated by space and one 2px ink rule under the heading. Boxes are used only around
things you edit or choose between. Radius by role: 7px on controls, 12px on panels, 22px on the slab.
Buttons are squared, not pills. The one filled yellow button on a screen is the thing that starts
something.

## Principles

1. **One picture, used everywhere.** The line explains the product, so it is the only signature.
2. **Sentences over tiles.** The Desk opens with "The desk is trading on paper. +₹450 after costs today,
   from 3 trades and 7 setups." instead of a row of stat boxes.
3. **The model's voice is marked.** Italic serif, and nowhere else.
4. **One decoration, in one place.** The Home slab carries an engraving: three closed curves, each one
   continuous line, drawn once on load the way the fine lines on a banknote are. It is the line again,
   wound up.
5. **Motion answers an action.** Expanding a setup, holding the stop, switching the Guide's example.
   The engraving is the only thing that moves by itself, once.

## Review against the generic default

A "trading dashboard" prompt lands on near-black with a neon accent, a grid of identical rounded KPI
cards, tracked-out capital labels over every block, and a monospace face for small data. The third
version's Desk had drifted there. Changes made against that:

- Removed every all-capitals label, every middle-dot meta string and the KPI tile row.
- Replaced the Desk's table of decisions with the line, so a row shows its reasoning instead of naming it.
- Replaced the card grid with ruled sections.
- Dropped the navy-and-brass and the cream-and-serif directions without building them: both are what
  any finance brief gets.
- Checked the lavender against the "purple gradient" cliché: it is flat, greyed, and paired with an
  ink that is nearly black; there is no gradient anywhere in the product.

## Notes for next time

- First version (Oct 2026): the SaaS card kit. Second: slate paper and a session ribbon. Third: storm
  blue slab and Bricolage Grotesque, good on Home, generic on the Desk. Do not drift back.
- A new page starts from a sentence that answers the page's question. If the page shows a decision,
  draw it with `Line`; do not invent a second diagram.
- Anything an LLM wrote goes in `.voice`. Nothing else does.
- The large line (`size="lg"`) scrolls sideways on tablets and shrinks on phones; captions must stay
  short enough to wrap in about 70px.
