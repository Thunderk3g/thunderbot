# Dashboard design

Made with the `frontend-design` skill (vendored in `.claude/skills/frontend-design`, from
github.com/anthropics/skills, Apache-2.0). These notes are the plan and a record of what was tried.
This is the fifth version of the interface: "the line", corrected after a measured critique of the fourth.

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
rule to an order, through gates. The rule of the picture is: **if an order passes, the conductor never
breaks.**

```
 rule ●━━━━━━●━●━━━━━━●━●━━━━━━●━●━━━━━━▶ order       every contact closed: taken whole
 rule ●━━━━━━●━●══════●═●══════●═●══════▷ order ×0.5  the LLM asked for half: the core narrows inside
                                                       a channel that stays full width
 rule ●━━━━━━●━●━━━━━━┄[ ]┄━━━━━●━●━━━━━━▶ order       no LLM fitted: the line runs straight through
                                                       an empty dashed socket
 plan ●━━━━━━●━●━━━━━━●━●━━━━━━[❙❙]░░░░░░○ held        the LLM held a rebalance for a session
 rule ●━━━━━━●╱ ○░░░░░░○ ○░░░░░░○ ○░░░░░░○ not traded  the score opened its switch: the only state
                                                       with an air gap
```

- **A faint channel of constant width runs the whole way and stands for full size.** The filled core
  inside it is the share that is left, with a `×0.5` badge beside the gate that narrowed it. Stroke
  thickness alone, in open space, reads as styling; a core inside a fixed channel reads as a proportion.
- **An unfitted optional gate is a dashed socket the line passes through**, unbroken. The fourth version
  drew this as two walls with a gap, which is the electrical sign for an open circuit and said the
  opposite of what it meant.
- **A hold is an amber latch.** A rebalance check can postpone by a session; that is not a stop.
- **A lifted arm is a stop**, and the channel after it stays empty: those gates were never asked.
- **A rebalance is several orders at once**, so its end fans into one chip per order. A single stroke
  width has no meaning for a basket.
- **Settled traces are calm; a trace that is still open is lit.** In the dark theme only a live trace is
  yellow. The fourth version painted every row yellow, which glared and spent the one accent everywhere.
- **On a phone the large trace turns** and runs down the left margin, so every gate gets a full line of
  words. The small trace on each Desk row stays horizontal; it fits.

`dashboard/components/DecisionTrace.tsx` is the whole of it, and it is used only for the causal,
time-ordered gates of one decision: each setup on the Desk, the daily check on Portfolio, a decision's
own page in the Journal, and the Guide.

### What is connected is a different shape

The scheduler, market data, an LLM, a broker and the order mode are not a chain: the broker is not
downstream of an optional LLM. The fourth version drew them with the same line, so an unfitted LLM looked
like a break before the broker. They are now taps off one bus (`SystemBus.tsx`): a solid tap is
connected, a dashed tap is an optional part that is not fitted, a red tap is fitted and failing.

## Tokens

The name is Thunderbot, so the palette is a storm: violet sky, yellow lightning. They are also the
colours of the ₹100 and ₹200 notes, which is the other thing this product is about.

Every pair below was measured (WCAG 2.1 relative luminance). Text is at least 4.5:1; anything a person
must see to use a control is at least 3:1.

| Role | Light | on paper | Dark | on paper |
|---|---|---|---|---|
| Paper (page) | `#ECE9F2` | | `#140D22` | |
| Ink | `#1C1230` | 14.9 | `#EEE9F7` | 15.5 |
| Ink, soft | `#625878` | 5.5 | `#A79DC0` | 7.3 |
| Hairline (dividers only) | `#D3CCE1` | 1.3 | `#32264E` | 1.4 |
| Control border (inputs, switches, sockets) | `#7A6E94` | 3.9 | `#7B6B9E` | 4.0 |
| Full-size channel in a trace | `#BDB4D2` | | `#4A3B6E` | |
| Trace, settled | ink | | `#CFC8E2` | 11.7 |
| Trace, live | ink | | `#F7BC1F` | 11.0 |
| Bolt (the mark, live nodes, "go") | `#F5B301` | 1.5, so it always carries an ink edge | `#F7BC1F` | 11.0 |
| Amber as text | `#7A5200` | 5.8 | `#F7BC1F` | 11.0 |
| Gain | `#08704B` | 5.1 | `#4AD6A5` | 10.3 |
| Loss | `#C4283C` | 4.7 | `#FF8793` | 8.2 |
| Storm (the hero slab) | `#2A1A4A` | | `#2B1B52` | |

Two findings from measuring the fourth version drove this table. The yellow bolt on pale paper is 1.5:1,
so it is never used alone there: every yellow dot has a 1.5px ink ring, and amber words use the darker
amber. And the hairline was doing duty as the border of inputs at 1.3:1; a hairline may only divide, so
controls have their own border colour.

Holdings keep one hue each and change lightness by surface, so each passes as text and as a fill:

| Holding | Light | Dark and on the slab |
|---|---|---|
| Nifty 50 | `#1D56C9` (5.4) | `#6EA1FF` (7.4, 6.1 on the slab) |
| Next 50 | `#086D62` (5.2) | `#3ED1C0` (10.0, 8.2) |
| Gold | `#8A5A00` (4.9), drawn as a diamond | `#F0B429` (10.2, 8.4) |
| Stocks | `#A12872` (5.7) | `#F47CC4` (7.7, 6.3) |

Gold's swatch is a diamond, so it is never told from a loss by colour alone. Parked money is the neutral
remainder of the bar, because it is the absence of a position. No gradients as decoration and no drop
shadows except under things that float. Green for a gain and red for a loss is what every Indian broker
app uses; every figure also carries its sign, with a true minus (U+2212) so columns line up.

## Type

**Anek Latin**, by Ek Type in Mumbai, one variable family with a width axis, used three ways:

- narrow and heavy (width 78 to 86, weight 700 to 750) for money and tickers, like a price board;
- normal (width 100, weight 400) for reading, at 15.5/24;
- wide (width 112 to 122, weight 600) for titles.

**Literata** is the second face and has exactly one job: words an LLM wrote. A line or two is set in
italic. A longer passage (a day's review, a full rationale) is set upright in a margin callout with a
dashed edge and chips naming the model and "non-binding", because a block of italic reads slowly. If it
is in this serif, a model said it; everything else was written by rules.

Tabular figures in every column. A monospace face appears only inside key inputs and `code`.

## Layout

Five places, in the order of how much they matter to someone's money. The intraday desk is a room
inside the Lab, not a peer of the portfolio, and five fit a phone's tab bar.

| Place | Address | What is there |
|---|---|---|
| **Portfolio** | `/`, `/portfolio/plan` | Value and split; the daily decision as a trace; a drift corridor per holding; the orders to place; adding money; the tax year; choosing and testing a plan |
| **Lab** (paper only) | `/lab`, `/lab/desk`, `/lab/sweeps`, `/lab/results` | Whether each model role has earned authority; the intraday desk; parameter sweeps marked down for every setting tried; results |
| **Journal** | `/journal`, `/journal/log`, `/journal/<id>` | Every setup and what the gates did; what the gates were worth; one page per decision |
| **Harness** | `/harness` | The files that shape a decision, each role's standing, the ceilings no file can raise |
| **Setup** | `/setup`, `/guide` | What is connected; keys; holdings; how orders are placed; limits; how it works |

A rail on the left that never leaves: the wordmark, the five words, the system bus, one control.
That control **pauses**. It never sells: leaving a position is done on the page that holds it, behind a
statement of what it books. Content is one left-aligned column up to 1240px. On phones the rail becomes
a top bar with the pause control and a five-tab bar.

Every page has a real address, so a decision can be bookmarked and sent to someone.

Sections are separated by space and one 2px ink rule under the heading. Boxes are used only around
things you edit or choose between. Radius by role: 7px on controls, 12px on panels, 22px on the slab.
Buttons are squared, not pills. The one filled yellow button on a screen is the thing that starts
something.

### Other pictures, each used once

- **Drift corridor** (Portfolio): one bullet graph per holding on a shared axis. The shaded band is how
  far it may drift, the tick is its target, the bar is where it is, and a marker shows which holding the
  next deposit goes to.
- **Gate strip** (Lab): for each model role, the range its true effect per setup is in, drawn across a
  line that means "no model". Whole bar right of the line: it has earned authority.
- **Tax-year meter** (Portfolio): how much of the year's tax-free allowance is used, and how much could
  still be booked.

## Principles

1. **One picture for one kind of thing.** The trace explains a decision, so it is the signature. It is not stretched over things that are not decisions.
2. **Sentences over tiles.** The Desk opens with "The desk is trading on paper. +₹450 after costs today,
   from 3 trades and 7 setups." instead of a row of stat boxes.
3. **The model's voice is marked.** Its own serif, and nowhere else.
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
  blue slab and Bricolage Grotesque, good on Home, generic on the Desk. Fourth: the line, with one
  component doing five jobs, a "not fitted" glyph that read as a break, a yellow that vanished on pale
  paper and flooded the dark theme, and seven peers in the rail. Do not drift back.
- Measure a colour before using it. `docs/design.md` records the ratio for every pair; add the number
  when you add a colour.
- A new page starts from a sentence that answers the page's question. If the page shows a decision,
  draw it with `DecisionTrace`. If it shows what is connected, use `SystemBus`. Do not invent a third.
- Anything an LLM wrote goes in `.voice` (short) or `.voice-block` (long). Nothing else does.
- The rail's control pauses and never sells. Do not add a second meaning to it.
