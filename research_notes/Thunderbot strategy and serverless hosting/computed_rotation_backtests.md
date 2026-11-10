# Computed year-by-year returns of Indian asset classes since 2008, and monthly ETF trend rotation versus a Nifty 200-day-average rule

> Status of everything below: **single-run, unreviewed back-tests computed in this session on 10 Nov 2026**. Every number is **[own computation]** unless a different source is linked. Nothing here is a forecast or a promise.
>
> **Data.** Adjusted daily closes and traded value from the [ancap97/NSEDATA4ME `data` branch, snapshot 26 Oct 2026](https://github.com/ancap97/NSEDATA4ME) (NSE bhavcopy, split/bonus-adjusted, 3 Jan 2005 → 26 Oct 2026; NSE daily index closes from 21 Feb 2012). Nifty 50 index before 21 Feb 2012 from the Yahoo-style file in [rishabhjain0295-web/nifty500-momentum-backtest](https://github.com/rishabhjain0295-web/nifty500-momentum-backtest). An 18-month total-return check series from [Indranil-Mondal/nifty-market-digest-bot](https://github.com/Indranil-Mondal/nifty-market-digest-bot). **Last date in the main data: 26 Oct 2026.**
>
> **Scripts (all in `/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/rotation/`):** `prep.py` (builds `panel.pkl`), `q123.py` (inventory, yearly returns, liquidity), `engine.py` (simulator, cost and tax model), `run4.py` (main back-tests → `out4.txt`), `repro.py` (reproduction of the reader's rule), `run5.py` (costs and tax → `out5.txt`), `run6.py` (robustness → `out6.txt`), `extras.py` (yearly strategy returns, holdings, gold decomposition), `proxy_test.py` and `chk.py` (data checks). Run order: `prep.py`, then any other, with `python3 -I`.
>
> **Labels.** "PR" = price-return index (no dividends). "ETF" = traded ETF closing price, which for a growth ETF approximates index total return minus costs. Periods: "2008–2026" = 31 Dec 2007 close → 26 Oct 2026; "2011–2026" = 31 Dec 2010 → 26 Oct 2026; "2008–2018" = 31 Dec 2007 → 31 Dec 2018; "2019–2026" = 31 Dec 2018 → 26 Oct 2026.

## 1. Data inventory and sanity checks

### Takeaway
Nifty 50, Next 50 and gold have clean ETF price histories for the whole 2008–2026 window; the midcap leg does not (index from 21 Feb 2012, ETF from 4 Feb 2019), so 2008–Feb 2011 midcap figures rest on a synthetic proxy that is known to be biased low. The December 2019 NIFTYBEES and GOLDBEES unit splits are correctly adjusted, and no total-return index history longer than 18 months was found.

### Cited Findings

**What exists and from when [own inspection]** — [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME)

| Series | Type | First date in files | Note |
|---|---|---|---|
| Nifty 50 | index PR | 21 Feb 2012 (NSE file); 1995 in the Yahoo-style file | The two files match on the overlap (earlier note); the Yahoo-style file runs to 6 Nov 2026 |
| Nifty Next 50 | index PR | 21 Feb 2012 | No earlier index data found |
| Nifty Midcap 100 | index PR | 21 Feb 2012 | Stitched from three successive names (CNX Midcap → Free Float Midcap 100 → Midcap 100) |
| Nifty Midcap 150 | index PR | 1 Apr 2016 | |
| Nifty 200 | index PR | 21 Feb 2012 | |
| Nifty200 Momentum 30 | index PR | 25 Aug 2020 | Live history only |
| Nifty 1D Rate Index | overnight-rate index | 23 Jun 2016 | The only usable cash series |
| G-sec indices (10-yr benchmark, composite, 4–8 yr) | index | Oct–Nov 2015 | Not used |
| Total-return (TRI) variants | — | **none** in the main files | Only 15 May 2025 → 9 Nov 2026 in the digest-bot repo |
| NIFTYBEES, JUNIORBEES | ETF | 3 Jan 2005 | JUNIORBEES has 52 missing days in 2005 and 23 in 2006, almost none after |
| GOLDBEES | ETF | 19 Mar 2007 | No missing days |
| MOM100 (formerly M100, Midcap 100 ETF) | ETF | 4 Feb 2011 | |
| MID150BEES | ETF | 4 Feb 2019 | |
| MON100 | ETF | 31 Mar 2011 | |
| LIQUIDBEES | ETF | 3 Jan 2005 | Price pinned near ₹1,000 (range 969.64–1,006.53); income is paid as units, so the price series **cannot** give a return |
| LIQUIDCASE | ETF (growth) | 24 Jan 2024 | |
| LIQUIDADD | ETF (growth) | 3 Apr 2024 | |
| GROWWLIQID | ETF (growth) | 26 Sep 2024 | |
| SETF10GILT, LTGILTBEES | ETF | 23 Jun 2016, 14 Jul 2016 | |
| LOWVOLIETF | ETF | 11 Jul 2017 | |
| ALPL30IETF | ETF | 18 Aug 2020 | |
| GILT5YBEES | ETF | 8 Apr 2021 | |
| MAFANG, MASPTOP50 | ETF | 14 May 2021, 24 Sep 2021 | |
| SILVERBEES, MOMOMENTUM | ETF | 7 Feb 2022, 17 Feb 2022 | |
| MOM30IETF, MOMENTUM, HDFCMOMENT | ETF | 10 Aug 2022, 19 Aug 2022, 17 Oct 2022 | |
| MOMENTUM30 | ETF | 17 Oct 2025 | |

**Split check [own computation].** Adjusted NIFTYBEES closes run 129.25 → 130.20 → 130.34 across 18–20 Dec 2019 and GOLDBEES 33.60 → 33.55 → 33.65; there is no −90% or −99% step. — [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME)

**One-day moves beyond ±20% [own computation]** — [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME)
- NIFTYBEES, JUNIORBEES, GOLDBEES, MID150BEES, LIQUIDCASE, LIQUIDADD, GROWWLIQID, MON100, MOM100 and every momentum, low-vol and gilt ETF except the two below: **none**.
- SILVERBEES: −23.2% on 2 Feb 2026 (also −18.6% on 30 Jan 2026 and +12.5% on 3 Feb 2026; looks like a real crash, not a data fault, but not verified against another source).
- SETF10GILT: −21.7% on 4 Aug 2016 and +27.0% on 8 Sep 2016, plus 22 further moves of 10–20% in its first months. These are bad prints in a barely traded ETF; the series is unusable before 2017.
- Moves of 10–20% in ETFs used below: NIFTYBEES −10.1% (24 Oct 2008), +14.6% (18 May 2009), −10.2% (23 Mar 2020); JUNIORBEES −17.5% (22 Jan 2008), +17.0% (28 Oct 2008), +19.7% (19 May 2009) and a +18.4% / −12.3% pair on 26–28 Nov 2005 (before the test window); GOLDBEES −10.5% (30 Jan 2026); MID150BEES +15.8%, −12.7%, −13.3%, +12.4% on 19, 20, 23 and 26 Mar 2020.

**ETF closes are noisy on crisis days [own computation].** MID150BEES differed from its index by more than 4 points on 13 days (for example +15.8% against −4.0% on 19 Mar 2020; +0.2% against −7.1% on 4 Jun 2024). JUNIORBEES fell 1.3% on 4 Jun 2024 when the Next 50 index fell 9.3%, and gave it back the next day. NIFTYBEES differed by more than 3 points on 3 days (16 and 19 Mar 2020, 5 Jun 2024). Calendar-year returns still match closely: MID150BEES beat the Midcap 150 price index by 0.3–1.2 points in each year 2020–2026. — [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME)

**Does the ETF price track total return? [own computation]** 15 May 2025 → 26 Oct 2026: Nifty 50 TRI −7.43%, NIFTYBEES −7.41%, Nifty 50 price index −9.21%. Next 50 TRI +1.89%, JUNIORBEES +1.42%, price index +0.38%. Midcap 150 TRI +1.13%, MID150BEES +1.02%, price index +0.15%. — TRI from [nifty-market-digest-bot](https://github.com/Indranil-Mondal/nifty-market-digest-bot); prices from [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME)

**Longer-run gap, ETF minus price index, 1 Mar 2012 → 26 Oct 2026 [own computation]:** NIFTYBEES 11.3% a year against 10.3% for the Nifty 50 price index; JUNIORBEES 14.0% against 13.5% for the Next 50 price index. — [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME)

**Synthetic midcap proxy test [own computation].** A basket of the stocks ranked 101–250 by 126-day median traded value (square-root-of-turnover weights, monthly) had a monthly correlation of 0.97–0.98 with the midcap indices but returned 6.1% a year against 13.1% for the Midcap 100 index over Mar 2012 – Mar 2016, and 14.3% against 16.3% for the Midcap 150 over Apr 2016 – Oct 2026. It is used below **only** for 31 Dec 2007 → 4 Feb 2011. — [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME)

**After the data ends.** The Nifty 50 closed at 22,753.20 on 26 Oct 2026 and at 25,030.35 on 6 Nov 2026 in the Yahoo-style file; the digest-bot file shows 25,044.65 on 9 Nov 2026 (+10.1% from 26 Oct), Next 50 72,789.45 (+9.5%), Midcap 150 22,408.55 (+7.7%). — [rishabhjain0295-web repo](https://github.com/rishabhjain0295-web/nifty500-momentum-backtest); [nifty-market-digest-bot](https://github.com/Indranil-Mondal/nifty-market-digest-bot). Not cross-checked against NSE.

### Inferences
- NIFTYBEES, JUNIORBEES and GOLDBEES prices are usable total-return proxies for 2008–2026. Daily drawdown and volatility figures built on ETF closes carry some noise from crisis-day mispricing, mainly for MID150BEES; for that reason the midcap leg in the back-tests uses the **price index** from Feb 2012 onward, which understates what an ETF holder received by roughly 0.3–1.2 points a year.
- The 2008–2011 midcap history is the weakest part of the data. Results that depend on it (four-asset rotation in 2008–2010, midcap buy-and-hold in 2008–2018) should be read as approximate and probably too low for midcaps.

### Gaps
- No Next 50 or midcap **index** data before 21 Feb 2012, and no long TRI history, could be found on GitHub in the time allowed (four repository searches; four candidate repos cloned, none had daily index history before 2012).
- No liquid or overnight series before 23 Jun 2016.
- No rupee gold price before 19 Mar 2007, so gold's 200-day average is only available from late Dec 2007 (computed on 190+ days for the first few weeks).

## 2. Year-by-year calendar returns, 2008 → 26 Oct 2026

### Takeaway
Gold in rupees had four losing calendar years in nineteen (2013, 2014, 2015 and 2021) and returned 13.6% a year over 2008–2026 against 7.9% for NIFTYBEES, but the split is stark: 9.2% a year in 2008–2018 and 19.9% in 2019–2026, with 2025 alone at +71.8%. The cash leg can be computed from data only from mid-2016.

### Cited Findings

**Calendar-year returns, % [own computation]** — prices from [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME); Nifty 50 index 2008–2011 from [rishabhjain0295-web repo](https://github.com/rishabhjain0295-web/nifty500-momentum-backtest). 2026 is 31 Dec 2025 → 26 Oct 2026. "—" = no full-year data.

| Year | Gold: GOLDBEES (ETF) | Nifty 50 index (PR) | NIFTYBEES (ETF) | Next 50 index (PR) | JUNIORBEES (ETF) | Midcap 100 index (PR) | Midcap 150 index (PR) | MOM100 Midcap 100 ETF | MID150BEES (ETF) | Nifty200 Momentum 30 (PR) | Nifty 1D Rate index | LIQUIDCASE (ETF) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2008 | 24.5 | −51.8 | −52.1 | — | −63.7 | — | — | — | — | — | — | — |
| 2009 | 24.9 | 75.8 | 75.6 | — | 123.9 | — | — | — | — | — | — | — |
| 2010 | 21.7 | 17.9 | 18.6 | — | 18.0 | — | — | — | — | — | — | — |
| 2011 | 29.9 | −24.6 | −24.0 | — | −31.7 | — | — | — | — | — | — | — |
| 2012 | 11.2 | 27.7 | 26.5 | — | 47.2 | — | — | 40.2 | — | — | — | — |
| 2013 | −6.4 | 6.8 | 7.2 | 4.8 | 5.7 | −5.1 | — | −2.2 | — | — | — | — |
| 2014 | −9.3 | 31.4 | 31.6 | 44.4 | 43.7 | 55.9 | — | 55.6 | — | — | — | — |
| 2015 | −7.5 | −4.1 | −4.3 | 7.0 | 7.9 | 6.5 | — | 7.6 | — | — | — | — |
| 2016 | 12.5 | 3.0 | 4.0 | 7.1 | 7.5 | 7.1 | — | 7.2 | — | — | — | — |
| 2017 | 2.4 | 28.6 | 29.9 | 44.8 | 45.4 | 47.3 | 54.3 | 46.2 | — | — | 6.0 | — |
| 2018 | 6.7 | 3.2 | 4.8 | −9.0 | −7.5 | −15.4 | −13.3 | −15.0 | — | — | 6.2 | — |
| 2019 | 22.9 | 12.0 | 13.6 | 0.5 | 1.0 | −4.3 | −0.3 | −2.7 | — | — | 5.8 | — |
| 2020 | 27.0 | 14.9 | 15.4 | 14.8 | 15.8 | 21.9 | 24.4 | 21.7 | 25.6 | — | 3.4 | — |
| 2021 | −5.2 | 24.1 | 26.0 | 29.9 | 30.4 | 46.1 | 46.8 | 45.5 | 47.3 | 52.1 | 3.3 | — |
| 2022 | 12.8 | 4.3 | 5.5 | −0.1 | 0.8 | 3.5 | 3.0 | 4.9 | 3.7 | −6.4 | 4.7 | — |
| 2023 | 14.7 | 20.0 | 21.0 | 26.4 | 26.9 | 46.6 | 43.7 | 47.2 | 44.1 | 40.7 | 6.8 | — |
| 2024 | 19.4 | 8.8 | 10.4 | 27.5 | 28.1 | 23.9 | 23.8 | 24.5 | 24.2 | 20.0 | 6.8 | — |
| 2025 | 71.8 | 10.5 | 11.7 | 2.0 | 2.5 | 5.7 | 5.4 | 6.4 | 5.7 | −5.1 | 5.8 | 5.5 |
| 2026 to 26 Oct | 5.5 | −12.9 | −12.2 | −4.2 | −3.6 | −6.6 | −6.6 | −6.6 | −6.1 | −10.5 | 4.3 | 4.0 |

Also in the files: SILVERBEES +7.4% (2023), +16.0% (2024), +157.3% (2025), −14.4% (2026 to 26 Oct); MON100 from +17.3% (2012) to +56.8% (2024), −26.2% in 2022, +23.8% in 2026 to 26 Oct.

**Period statistics [own computation]** (CAGR / annualised daily volatility / maximum drawdown on daily closes with peak → trough / best and worst calendar year) — [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME)

| Period | Series | CAGR | Vol | Max drawdown | Best year | Worst year |
|---|---|---|---|---|---|---|
| 2008–2026 | GOLDBEES (ETF) | 13.6% | 16.4% | −27.1% (27 Nov 2012 → 6 Aug 2015) | 2025 +71.8% | 2014 −9.3% |
| | Nifty 50 index (PR) | 7.2% | 20.2% | −59.9% (8 Jan → 27 Oct 2008) | 2009 +75.8% | 2008 −51.8% |
| | NIFTYBEES (ETF) | 7.9% | 18.9% | −59.7% (9 Jan → 27 Oct 2008) | 2009 +75.6% | 2008 −52.1% |
| | JUNIORBEES (ETF) | 9.6% | 22.5% | −72.3% (4 Jan 2008 → 9 Mar 2009) | 2009 +123.9% | 2008 −63.7% |
| 2011–2026 | GOLDBEES (ETF) | 11.7% | 15.5% | −27.1% (27 Nov 2012 → 6 Aug 2015) | 2025 +71.8% | 2014 −9.3% |
| | Nifty 50 index (PR) | 8.6% | 16.4% | −38.4% (14 Jan → 23 Mar 2020) | 2014 +31.4% | 2011 −24.6% |
| | NIFTYBEES (ETF) | 9.5% | 15.1% | −36.3% (17 Jan → 23 Mar 2020) | 2014 +31.6% | 2011 −24.0% |
| | JUNIORBEES (ETF) | 11.9% | 17.8% | −38.7% (8 Jan 2018 → 24 Mar 2020) | 2012 +47.2% | 2011 −31.7% |
| 2008–2018 | GOLDBEES (ETF) | 9.2% | 15.5% | −27.1% (27 Nov 2012 → 6 Aug 2015) | 2011 +29.9% | 2014 −9.3% |
| | Nifty 50 index (PR) | 5.3% | 22.0% | −59.9% | 2009 +75.8% | 2008 −51.8% |
| | NIFTYBEES (ETF) | 5.7% | 21.0% | −59.7% | 2009 +75.6% | 2008 −52.1% |
| | JUNIORBEES (ETF) | 7.8% | 25.5% | −72.3% | 2009 +123.9% | 2008 −63.7% |
| 2019–2026 | GOLDBEES (ETF) | 19.9% | 17.5% | −24.4% (29 Jan → 23 Mar 2026) | 2025 +71.8% | 2021 −5.2% |
| | Nifty 50 index (PR) | 9.9% | 17.3% | −38.4% (14 Jan → 23 Mar 2020) | 2021 +24.1% | 2026 −12.9% |
| | NIFTYBEES (ETF) | 11.1% | 15.5% | −36.3% (17 Jan → 23 Mar 2020) | 2021 +26.0% | 2026 −12.2% |
| | Next 50 index (PR) | 11.6% | 18.8% | −36.5% (24 Jan → 23 Mar 2020) | 2021 +29.9% | 2026 −4.2% |
| | JUNIORBEES (ETF) | 12.3% | 17.4% | −34.5% (24 Jan → 24 Mar 2020) | 2021 +30.4% | 2026 −3.6% |
| | Midcap 100 index (PR) | 15.8% | 19.5% | −40.2% (7 Feb → 23 Mar 2020) | 2023 +46.6% | 2026 −6.6% |
| | Midcap 150 index (PR) | 16.4% | 18.3% | −38.7% (7 Feb → 23 Mar 2020) | 2021 +46.8% | 2026 −6.6% |
| | Nifty 1D Rate index | 5.2% | 0.3% | none | 2024 +6.8% | 2021 +3.3% |

Short series, from their own first date to 26 Oct 2026: Midcap 100 index PR from 21 Feb 2012: 14.3% a year, drawdown −49.4% (23 Jan 2018 → 23 Mar 2020). Midcap 150 index PR from 1 Apr 2016: 16.3%, −44.2% (8 Jan 2018 → 23 Mar 2020). MID150BEES from 4 Feb 2019: 18.0%, −38.4%. MOM100 ETF from 4 Feb 2011: 14.0%, −48.4%. Nifty200 Momentum 30 PR from 25 Aug 2020: 14.5%, −31.8% (27 Sep 2024 → 7 Apr 2025). Nifty 1D Rate index from 23 Jun 2016: 5.43% a year. — [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME)

**Liquid ETFs against the overnight index [own computation]:** LIQUIDCASE 5.64% a year since 24 Jan 2024 against 5.94% for the Nifty 1D Rate index over the same days; LIQUIDADD 5.54% against 5.88% since 3 Apr 2024; GROWWLIQID 5.24% against 5.69% since 26 Sep 2024. None of the three had a down day larger than 0.01%. — [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME)

### Inferences
- Liquid ETFs have delivered about 0.3–0.45 points a year less than the overnight index; a flat 6.0% for the cash leg is therefore slightly generous for 2019–2026 (overnight index 5.2% a year) and unverifiable before mid-2016.
- NIFTYBEES buy-and-hold over 2011–2026 comes out at 9.5% a year with a −36.3% worst fall, matching the reader's own benchmark figures (9.5%, −36%).

### Gaps
- **The cash leg cannot be computed from data before 23 Jun 2016.** No Next 50 or midcap calendar-year index returns before 2013 (ETF only for Next 50; nothing reliable for midcap 2008–2011). Nifty200 Momentum 30 only from 2021 (live history); its earlier back-filled history is not in these files.

## 3. Liquidity: average and median daily traded value

### Takeaway
On the NSE alone, NIFTYBEES, GOLDBEES, LIQUIDCASE, LIQUIDBEES, JUNIORBEES, MID150BEES and LIQUIDADD all trade well over ₹15 crore on a median day, so a ₹20 lakh order is a small fraction of a day's volume. Most momentum ETFs and SETF10GILT trade under ₹1 crore on a median day and fail the test.

### Cited Findings

**Daily traded value on NSE, ₹ crore [own computation]** from the turnover panel. 3-month window: 27 Jul → 26 Oct 2026 (63 trading days). 12-month window: 27 Oct 2025 → 26 Oct 2026 (246 days). Every ETF traded on all 246 days. — [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME)

| ETF | 3-month average | 3-month median | 12-month average | 12-month median | ₹20 lakh as share of 12-month median day | Flag |
|---|---|---|---|---|---|---|
| NIFTYBEES | 175.0 | 156.5 | 216.9 | 188.5 | 0.1% | |
| GOLDBEES | 294.1 | 260.4 | 535.4 | 345.0 | 0.06% | |
| SILVERBEES | 453.3 | 384.6 | 1,215.9 | 645.3 | 0.03% | |
| LIQUIDBEES | 407.2 | 339.9 | 377.6 | 316.8 | 0.06% | |
| LIQUIDCASE | 234.1 | 205.3 | 217.6 | 199.6 | 0.1% | |
| LIQUIDADD | 63.0 | 49.2 | 60.5 | 51.7 | 0.4% | |
| JUNIORBEES | 29.4 | 24.8 | 33.2 | 29.1 | 0.7% | |
| MID150BEES | 19.3 | 15.0 | 22.1 | 17.7 | 1.1% | |
| MON100 | 21.6 | 19.6 | 23.7 | 20.7 | 1.0% | |
| MAFANG | 17.2 | 13.7 | 8.6 | 4.5 | 4% | |
| LTGILTBEES | 4.5 | 3.4 | 5.6 | 4.6 | 4% | |
| LOWVOLIETF | 5.0 | 3.3 | 4.8 | 3.1 | 6% | |
| GROWWLIQID | 3.9 | 3.0 | 4.0 | 2.5 | 8% | thin |
| MOM100 | 2.3 | 1.9 | 3.3 | 2.7 | 7% | thin |
| MOM30IETF | 2.1 | 1.7 | 4.9 | 2.4 | 8% | thin |
| MASPTOP50 | 9.7 | 5.2 | 3.7 | 1.5 | 13% | thin; four moves of 12–20% in a day in 2024–2026 |
| GILT5YBEES | 1.4 | 1.2 | 2.0 | 1.5 | 13% | thin |
| ALPL30IETF | 1.6 | 0.76 | 3.0 | 1.5 | 14% | **below ₹1 crore on 3-month median** |
| HDFCMOMENT | 0.58 | 0.46 | 0.58 | 0.49 | 41% | **below ₹1 crore** |
| MOMOMENTUM | 0.43 | 0.36 | 0.78 | 0.43 | 47% | **below ₹1 crore** |
| MOMENTUM | 0.24 | 0.18 | 0.29 | 0.18 | 111% | **below ₹1 crore** |
| MOMENTUM30 | 1.09 | 0.20 | 0.52 | 0.10 | 200% | **below ₹1 crore** |
| SETF10GILT | 0.11 | 0.06 | 0.46 | 0.21 | 95% | **below ₹1 crore** |

### Inferences
- The five instruments a four-sleeve rotation would use (NIFTYBEES, JUNIORBEES, MID150BEES, GOLDBEES, LIQUIDCASE) all clear the ₹1 crore bar by a wide margin. The largest single order in a ₹20 lakh account (₹10 lakh in MID150BEES under the dual-momentum variant) is about 0.6% of a median day.
- No Nifty200 Momentum 30 ETF clears ₹2.5 crore on a median day; a ₹20 lakh order would be 8% to 200% of a median day's trading in them.

### Gaps
- NSE cash-market turnover only; BSE volume, bid-ask spreads and intraday depth at 15:10 are not in the data. Traded value says nothing about the premium or discount to NAV at the moment of the order.

## 4. Back-tests: buy-and-hold, the reader's rule, sleeve rotation, dual momentum, no-gold variants and passive mixes

### Takeaway
Before costs and tax, with cash at a flat 6%, the four-sleeve trend rotation returned 10.4% a year over 2011–2026 with a −16.6% worst fall, against 7.6% and −18.3% for the reader's rule on the same engine; the dual-momentum version returned 13.3% but fell 24.7% (and 36.8% in early 2008). Remove gold and both rotations drop to 8.9% with falls of 29–35%; a plain equal-weight mix of the four assets rebalanced once a year returned more than either rotation (12.4%) but fell 27.5% in 2020 and 49% in 2008.

### Cited Findings

**Exact rule definitions (all month-end decisions use the last trading day's close; `engine.py`, `run4.py`).** Data for all rows: [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME).
- **Traded prices:** N50 = NIFTYBEES; NN50 = JUNIORBEES; GOLD = GOLDBEES; MID = chained daily returns of the synthetic proxy (to 4 Feb 2011), MOM100 ETF (to 21 Feb 2012), Nifty Midcap 100 price index (to 1 Apr 2016), Nifty Midcap 150 price index (after). LIQ = cash leg.
- **Signal series:** N50 = Nifty 50 price index; NN50 = JUNIORBEES returns chained into the Next 50 price index from 21 Feb 2012; MID and GOLD = their traded series. 200-DMA = simple mean of the last 200 closes including the decision day.
- **a** Buy-and-hold NIFTYBEES.
- **b** Reader's rule: 100% NIFTYBEES if Nifty 50 index close > 1.01 × its 200-DMA at month-end, else 100% cash. **b′** = same with the signal computed on the NIFTYBEES price instead of the index. **b0** = 1.00× buffer.
- **c** Four sleeves of 25% (N50, NN50, MID, GOLD); a sleeve is held if its signal series > 1.00 × its 200-DMA, otherwise that 25% sits in cash. **c1** = 1.01× buffer.
- **d** Dual momentum: score = average of 126-day and 252-day return; hold the top 2 of the four at 50% each, but only those above their own 200-DMA; a failing slot sits in cash. **d2** = absolute filter is "252-day return > 6%" instead of the 200-DMA.
- **e-c / e-d** Same as c / d with gold removed (three equity sleeves of 33.3%; top 2 of 3).
- **u-c / u-d** Same as c / d on N50, NN50 and GOLD only (three sleeves of 33.3%; top 2 of 3). Every input is a real ETF price for the whole period, so this is the cross-check on the synthetic midcap years.
- **g-…** Gold "de-trended": from 1 Jan 2019 a constant is subtracted from gold's daily log return so that its 2019–2026 CAGR equals its 2008–2018 CAGR (9.22% instead of 19.94%); the path shape is kept and the signals are recomputed on the altered series.
- **f1** Equal weight of the four, full rebalance at the December month-end. **f2** 75% NIFTYBEES / 25% GOLDBEES, same rebalance. **f3, f4, f5** buy-and-hold JUNIORBEES, MID, GOLDBEES.
- **Trading rule for b–e:** trade only when the target weights change, and at the December month-end; an asset is traded only if it is opened, closed, or more than 5 percentage points of the portfolio away from target; cash is the residual.
- **Cash:** "6%" = flat 6.0% a year; "0%" = idle; "actual" = Nifty 1D Rate index from 23 Jun 2016 and flat 6% before (so it differs from the 6% column only after mid-2016).
- **Timing:** signal and trade on the same close. This slightly flatters a 15:10 decision. The "next day's close" check is in section 6.

**Reproduction of the reader's rule [own computation].** The reader's own file gives, for "200DMA, 1% buffer, month-end check", 8.55% pre-tax, 8.07% after tax, worst fall −15.3% / −17.4%, 30 trades, over 1 Jan 2011 → 22 Oct 2026, with **idle cash earning 6% a year**, decision on day t and trade at day t+1 close, ₹5 lakh and Groww costs — [thunderbot_backtests.md](../Evidence%20based%20NSE%20trading%20strategies/thunderbot_backtests.md). The brief for this note described the rule as cash "earning nothing"; the reader's file does not.

| Specification, 31 Dec 2010 → 22 Oct 2026, ₹5 lakh | CAGR before costs | CAGR after costs | Max drawdown | Switches |
|---|---|---|---|---|
| Reader's file | — | 8.55% | −15.3% / −17.4% | 30 trades |
| Signal on NIFTYBEES price, 6% cash, same-day close | 8.42% | 8.26% | −15.4% | 35 |
| Signal on NIFTYBEES price, 6% cash, next-day close | 7.98% | 7.82% | −15.3% | 35 |
| Signal on Nifty 50 index, 6% cash, same-day close | 7.56% | 7.38% | −18.3% | 39 |
| Signal on Nifty 50 index, 6% cash, next-day close | 7.01% | 6.84% | −21.0% | 39 |
| Signal on NIFTYBEES price, **0% cash**, same-day close | 6.38% | 6.22% | −19.2% | 35 |
| Signal on Nifty 50 index, **0% cash**, same-day close | 5.47% | 5.29% | −23.3% | 39 |
| Signal on Nifty 50 index, 0% cash, next-day close | 4.94% | 4.76% | −25.8% | 39 |

Closest match: 7.8–8.3% after costs and −15.3% to −15.7% against the reader's 8.55% and −15.3%; the remaining 0.3–0.7 points and the different switch count (35 switches here against 30 trades in the reader's file) are unexplained and probably come from the reader's Yahoo data (repaired ticks, dividend-adjusted closes). With cash at 0% the rule returns 5.3–6.4%, not 8.5%.

**Main table, before costs and tax [own computation].** CAGR shown for the three cash treatments; volatility, drawdown, worst year, time under water, orders and cash share are for the 6% case. "Orders a year" counts every buy or sell including those in the liquid ETF. Midcap leg is synthetic before 4 Feb 2011.

*2011–2026 (31 Dec 2010 → 26 Oct 2026)*

| Variant | CAGR, cash 6% | CAGR, cash 0% | CAGR, actual cash | Vol | Max drawdown (peak → trough) | Worst calendar year | Longest under water | Orders a year | Time in cash |
|---|---|---|---|---|---|---|---|---|---|
| a Buy-and-hold NIFTYBEES | 9.5% | 9.5% | 9.5% | 15.1% | −36.3% (17 Jan → 23 Mar 2020) | 2011 −24.0% | 2.8 y | 0 | 0% |
| b Reader's rule (index signal) | 7.6% | 5.5% | 7.4% | 10.4% | −18.3% (3 Jan 2011 → 26 Jul 2012) | 2011 −6.7% | 3.3 y | 5.0 | 34% |
| b′ Reader's rule (NIFTYBEES signal) | 8.4% | 6.4% | 8.3% | 10.4% | −15.4% (29 Jan → 26 Aug 2015) | 2011 −6.7% | 2.2 y | 4.5 | 32% |
| b0 same as b, no buffer | 8.0% | 6.2% | 7.9% | 10.8% | −17.6% | 2011 −9.8% | 3.2 y | 4.5 | 29% |
| c Four sleeves, 1.00× | 10.4% | 8.7% | 10.3% | 9.7% | −16.6% (23 Jan 2018 → 23 Mar 2020) | 2018 −10.2% | 2.8 y | 17.2 | 28% |
| c1 Four sleeves, 1.01× | 10.0% | 7.9% | 9.9% | 9.3% | −18.4% (23 Jan 2018 → 23 Mar 2020) | 2018 −13.0% | 2.8 y | 17.5 | 33% |
| d Dual momentum, 200-DMA filter | 13.3% | 12.4% | 13.2% | 13.8% | −24.7% (8 Jan 2018 → 23 Mar 2020) | 2018 −16.1% | 2.9 y | 12.7 | 13% |
| d2 Dual momentum, 12-month > 6% filter | 11.9% | 10.8% | 11.8% | 13.9% | −25.6% | 2018 −14.1% | 3.0 y | 11.8 | 16% |
| e-c No gold, three equity sleeves | 8.9% | 7.1% | 8.8% | 11.6% | −28.7% (23 Jan 2018 → 23 Mar 2020) | 2018 −12.8% | 3.2 y | 12.4 | 29% |
| e-d No gold, top 2 of 3 equity | 8.9% | 7.4% | 8.8% | 13.2% | −35.1% (8 Jan 2018 → 23 Mar 2020) | 2026 −13.2% | 3.4 y | 10.1 | 24% |
| u-c N50 + NN50 + gold sleeves | 10.4% | 8.7% | 10.5% | 9.1% | −12.3% (29 Jan → 23 Mar 2026) | 2018 −7.4% | 2.0 y | 13.3 | 28% |
| u-d Top 2 of N50, NN50, gold | 12.2% | 11.1% | 12.1% | 11.9% | −19.2% (29 Jan → 23 Mar 2026) | 2018 −14.6% | 2.2 y | 11.6 | 16% |
| g-c Four sleeves, gold de-trended | 9.3% | 7.5% | 9.2% | 9.7% | −21.0% | 2018 −10.2% | 2.9 y | 17.5 | 30% |
| g-d Dual momentum, gold de-trended | 12.7% | 11.7% | 12.6% | 13.9% | −31.8% | 2018 −16.1% | 3.0 y | 11.8 | 14% |
| f1 Equal weight of four, annual | 12.4% | — | — | 12.2% | −27.5% (20 Feb → 23 Mar 2020) | 2011 −14.6% | 1.2 y | 4.5 | 0% |
| f2 75% Nifty / 25% gold, annual | 10.6% | — | — | 11.7% | −27.2% (17 Jan → 23 Mar 2020) | 2011 −10.6% | 1.5 y | 2.6 | 0% |
| f3 Buy-and-hold JUNIORBEES | 11.9% | — | — | 17.8% | −38.7% (8 Jan 2018 → 24 Mar 2020) | 2011 −31.7% | 2.9 y | 0 | 0% |
| f4 Buy-and-hold midcap (index PR chain) | 13.0% | — | — | 18.1% | −44.2% (8 Jan 2018 → 23 Mar 2020) | 2011 −32.5% | 3.4 y | 0 | 0% |
| f5 Buy-and-hold GOLDBEES | 11.7% | — | — | 15.5% | −27.1% (27 Nov 2012 → 6 Aug 2015) | 2014 −9.3% | 6.6 y | 0 | 0% |

*Full period, 2008–2026 (31 Dec 2007 → 26 Oct 2026)*

| Variant | CAGR, cash 6% | CAGR, cash 0% | CAGR, actual cash | Vol | Max drawdown (peak → trough) | Worst calendar year | Longest under water | Orders a year | Time in cash |
|---|---|---|---|---|---|---|---|---|---|
| a | 7.9% | 7.9% | 7.9% | 18.9% | −59.7% (9 Jan → 27 Oct 2008) | 2008 −52.1% | 3.0 y | 0 | 0% |
| b | 8.5% | 6.4% | 8.4% | 12.8% | −27.8% (9 Jan → 17 Mar 2008) | 2008 −18.8% | 3.5 y | 4.4 | 34% |
| b′ | 9.2% | 7.2% | 9.1% | 12.9% | −27.8% (9 Jan → 17 Mar 2008) | 2008 −18.8% | 2.2 y | 4.0 | 33% |
| c | 11.1% | 9.4% | 11.0% | 11.1% | −21.5% (4 Jan → 24 Mar 2008) | 2008 −15.9% | 2.8 y | 15.7 | 28% |
| c1 | 10.3% | 8.2% | 10.2% | 10.7% | −21.5% | 2008 −14.9% | 2.8 y | 15.9 | 32% |
| d | 12.7% | 11.8% | 12.7% | 15.9% | −36.8% (4 Jan → 24 Mar 2008) | 2008 −30.7% | 2.9 y | 11.7 | 14% |
| d2 | 10.5% | 9.4% | 10.4% | 15.4% | −39.0% (4 Jan → 11 Sep 2008) | 2008 −30.4% | 3.0 y | 10.6 | 17% |
| e-c | 9.4% | 7.5% | 9.3% | 13.6% | −32.4% (4 Jan → 24 Mar 2008) | 2008 −26.2% | 3.5 y | 11.4 | 30% |
| e-d | 9.6% | 8.0% | 9.6% | 15.6% | −39.4% (4 Jan → 24 Mar 2008) | 2008 −32.9% | 3.5 y | 9.5 | 25% |
| u-c | 11.8% | 10.2% | 11.9% | 10.4% | −16.9% (14 Jan → 22 Jan 2008) | 2008 −9.0% | 2.0 y | 12.3 | 28% |
| u-d | 11.8% | 10.7% | 11.8% | 13.6% | −27.7% (4 Jan → 11 Sep 2008) | 2008 −21.8% | 2.2 y | 11.6 | 17% |
| g-c | 10.2% | 8.3% | 10.1% | 11.1% | −21.5% | 2008 −15.9% | 2.9 y | 16.0 | 30% |
| g-d | 12.2% | 11.1% | 12.1% | 15.9% | −36.8% | 2008 −30.7% | 3.0 y | 11.2 | 15% |
| f1 | 12.2% | — | — | 14.4% | −49.0% (4 Jan → 27 Oct 2008) | 2008 −39.2% | 1.9 y | 4.8 | 0% |
| f2 | 10.4% | — | — | 14.0% | −43.9% (9 Jan → 27 Oct 2008) | 2008 −33.0% | 1.7 y | 2.7 | 0% |
| f3 | 9.6% | — | — | 22.5% | −72.3% (4 Jan 2008 → 9 Mar 2009) | 2008 −63.7% | 3.4 y | 0 | 0% |
| f4 (synthetic to Feb 2011) | 10.5% | — | — | 21.8% | −73.8% (4 Jan 2008 → 9 Mar 2009) | 2008 −65.4% | 3.6 y | 0 | 0% |
| f5 | 13.6% | — | — | 16.4% | −27.1% (27 Nov 2012 → 6 Aug 2015) | 2014 −9.3% | 6.6 y | 0 | 0% |

*2008–2018 (31 Dec 2007 → 31 Dec 2018)*

| Variant | CAGR, cash 6% | CAGR, cash 0% | Vol | Max drawdown | Worst calendar year | Longest under water | Orders a year | Time in cash |
|---|---|---|---|---|---|---|---|---|
| a | 5.7% | 5.7% | 21.0% | −59.7% | 2008 −52.1% | 3.0 y | 0 | 0% |
| b | 7.1% | 5.0% | 14.4% | −27.8% | 2008 −18.8% | 3.5 y | 4.6 | 35% |
| b′ | 7.7% | 5.4% | 14.3% | −27.8% | 2008 −18.8% | 2.2 y | 4.1 | 35% |
| c | 9.6% | 7.7% | 11.8% | −21.5% | 2008 −15.9% | 2.1 y | 15.2 | 31% |
| c1 | 8.2% | 5.9% | 11.3% | −21.5% | 2008 −14.9% | 2.1 y | 15.5 | 36% |
| d | 10.9% | 9.8% | 16.8% | −36.8% | 2008 −30.7% | 1.7 y | 10.1 | 15% |
| d2 | 8.0% | 6.9% | 16.1% | −39.0% | 2008 −30.4% | 2.6 y | 8.1 | 17% |
| e-c | 9.1% | 7.0% | 14.8% | −32.4% | 2008 −26.2% | 3.5 y | 10.8 | 32% |
| e-d | 10.3% | 8.6% | 17.0% | −39.4% | 2008 −32.9% | 3.5 y | 8.4 | 28% |
| u-c | 10.6% | 8.5% | 11.0% | −16.9% | 2008 −9.0% | 1.4 y | 12.5 | 30% |
| u-d | 9.8% | 8.6% | 14.3% | −27.7% | 2008 −21.8% | 1.6 y | 11.5 | 19% |
| f1 | 9.9% | — | 15.4% | −49.0% | 2008 −39.2% | 1.9 y | 5.1 | 0% |
| f2 | 8.1% | — | 15.1% | −43.9% | 2008 −33.0% | 1.7 y | 2.9 | 0% |
| f3 | 7.8% | — | 25.5% | −72.3% | 2008 −63.7% | 3.4 y | 0 | 0% |
| f4 (synthetic to Feb 2011) | 6.5% | — | 23.9% | −73.8% | 2008 −65.4% | 3.6 y | 0 | 0% |
| f5 | 9.2% | — | 15.5% | −27.1% | 2014 −9.3% | 6.1 y, not recovered by end 2018 | 0 | 0% |

*2019–2026 (31 Dec 2018 → 26 Oct 2026; every input is real index or ETF data)*

| Variant | CAGR, cash 6% | CAGR, cash 0% | CAGR, actual cash | Vol | Max drawdown (peak → trough) | Worst calendar year | Longest under water | Orders a year | Time in cash |
|---|---|---|---|---|---|---|---|---|---|
| a | 11.1% | 11.1% | 11.1% | 15.5% | −36.3% (17 Jan → 23 Mar 2020) | 2026 −12.2% | 1.1 y | 0 | 0% |
| b | 10.5% | 8.4% | 10.2% | 10.2% | −13.9% (18 Oct 2021 → 28 Feb 2023) | 2022 −4.8% | 2.1 y | 4.2 | 32% |
| b′ | 11.5% | 9.6% | 11.2% | 10.5% | −10.7% (18 Oct 2021 → 19 Apr 2022) | 2026 +1.4% | 1.1 y | 4.0 | 29% |
| c | 13.2% | 11.7% | 13.0% | 10.1% | −13.5% (18 Oct 2021 → 13 May 2022) | 2026 −4.5% | 1.8 y | 16.4 | 24% |
| c1 | 13.3% | 11.6% | 13.0% | 9.8% | −12.6% (24 Feb → 23 Mar 2020) | 2022 −3.7% | 1.9 y | 16.9 | 27% |
| d | 15.3% | 14.6% | 15.2% | 14.4% | −22.6% (24 Feb → 23 Mar 2020) | 2022 −10.4% | 2.1 y | 14.5 | 12% |
| d2 | 14.1% | 13.0% | 14.0% | 14.4% | −22.6% | 2022 −11.2% | 2.1 y | 14.5 | 16% |
| e-c | 10.0% | 8.2% | 9.7% | 11.6% | −18.4% (24 Jan → 23 Mar 2020) | 2026 −8.1% | 2.1 y, from 27 Sep 2024, not recovered | 12.5 | 28% |
| e-d | 8.7% | 7.3% | 8.5% | 13.3% | −25.2% (3 Jun 2019 → 23 Mar 2020) | 2026 −13.2% | 2.1 y, from 27 Sep 2024, not recovered | 11.3 | 21% |
| u-c | 13.6% | 12.5% | 13.8% | 9.6% | −12.3% (29 Jan → 23 Mar 2026) | 2026 −1.4% | 1.7 y | 12.4 | 24% |
| u-d | 14.7% | 13.8% | 14.6% | 12.5% | −19.2% (29 Jan → 23 Mar 2026) | 2022 −10.1% | 2.2 y | 11.6 | 13% |
| g-c gold de-trended | 11.0% | 9.2% | 10.7% | 10.1% | −13.8% | 2026 −6.0% | 1.9 y | 17.6 | 28% |
| g-d gold de-trended | 14.0% | 13.1% | 13.8% | 14.6% | −22.5% | 2022 −8.9% | 1.9 y | 12.7 | 14% |
| f1 | 15.6% | — | — | 13.0% | −27.5% (20 Feb → 23 Mar 2020) | 2026 −4.2% | 0.8 y | 4.9 | 0% |
| f1 gold de-trended | 12.9% | — | — | 13.0% | −27.8% | 2026 −6.1% | 1.1 y | 4.9 | 0% |
| f2 | 13.7% | — | — | 12.4% | −27.2% (17 Jan → 23 Mar 2020) | 2026 −7.8% | 0.7 y, from 29 Jan 2026, not recovered | 2.0 | 0% |
| f2 gold de-trended | 11.0% | — | — | 12.5% | −27.7% | 2026 −9.7% | 1.1 y | 2.8 | 0% |
| f3 | 12.3% | — | — | 17.4% | −34.5% (24 Jan → 24 Mar 2020) | 2026 −3.6% | 2.1 y, not recovered | 0 | 0% |
| f4 | 16.4% | — | — | 18.3% | −38.7% (7 Feb → 23 Mar 2020) | 2026 −6.6% | 1.3 y | 0 | 0% |
| f5 | 19.9% | — | — | 17.5% | −24.4% (29 Jan → 23 Mar 2026) | 2021 −5.2% | 2.5 y | 0 | 0% |

*Cross-check on real midcap data only, 31 Dec 2012 → 26 Oct 2026, cash 6%:* a 11.2% / −36.3%; b 9.1% / −16.1%; c 11.4% / −16.6%; c1 11.0% / −18.4%; d 13.5% / −24.7%; e-c 10.5% / −28.7%; e-d 10.3% / −35.1%; f1 13.5% / −27.5%; f2 11.5% / −27.2%; f3 13.6% / −38.7%; f4 15.6% / −44.2%; f5 10.6% / −25.5%.

*Using MID150BEES prices instead of the midcap index from 4 Feb 2019 (2019–2026):* c 13.5% / −13.4% (index: 13.2% / −13.5%); d 15.6% / −21.9% (15.3% / −22.6%); f1 15.8% / −27.2% (15.6% / −27.5%).

**Calendar-year returns of the main variants, before costs, cash 6% [own computation]**

| Year | a | b | b′ | c | d | e-c | e-d | f1 | f2 |
|---|---|---|---|---|---|---|---|---|---|
| 2008 | −52.1 | −18.8 | −18.8 | −15.9 | −30.7 | −26.2 | −32.9 | −39.2 | −33.0 |
| 2009 | 75.6 | 52.6 | 52.6 | 53.5 | 63.1 | 62.8 | 86.9 | 90.9 | 62.9 |
| 2010 | 18.6 | 18.6 | 18.6 | 18.1 | 16.5 | 17.2 | 16.6 | 18.3 | 19.4 |
| 2011 | −24.0 | −6.7 | −6.7 | 0.5 | 9.2 | −7.6 | −7.5 | −14.6 | −10.6 |
| 2012 | 26.5 | 2.2 | 8.1 | 7.5 | 14.3 | 5.4 | 7.6 | 30.4 | 22.7 |
| 2013 | 7.2 | −1.6 | −1.6 | −0.8 | −4.8 | 0.3 | −3.5 | 0.4 | 3.8 |
| 2014 | 31.6 | 31.6 | 31.6 | 34.4 | 48.5 | 44.0 | 48.5 | 30.5 | 21.3 |
| 2015 | −4.3 | −5.8 | −5.0 | 0.2 | 6.2 | 2.7 | 6.2 | 0.6 | −5.1 |
| 2016 | 4.0 | 4.5 | 3.5 | 4.9 | 0.6 | 3.2 | 1.8 | 7.9 | 6.1 |
| 2017 | 29.9 | 25.0 | 25.0 | 32.8 | 49.9 | 42.0 | 49.9 | 33.0 | 23.0 |
| 2018 | 4.8 | −4.5 | −4.5 | −10.2 | −16.1 | −12.8 | −12.6 | −2.3 | 5.3 |
| 2019 | 13.6 | 4.8 | 4.1 | 5.4 | 13.3 | −0.5 | −2.1 | 9.3 | 15.9 |
| 2020 | 15.4 | 19.6 | 19.6 | 20.2 | 9.4 | 12.0 | 3.4 | 20.7 | 18.3 |
| 2021 | 26.0 | 26.0 | 26.0 | 28.1 | 36.7 | 34.7 | 36.5 | 24.5 | 18.2 |
| 2022 | 5.5 | −4.8 | 2.9 | −2.0 | −10.4 | −3.9 | −8.9 | 5.5 | 7.3 |
| 2023 | 21.0 | 17.5 | 17.5 | 21.5 | 25.3 | 25.6 | 31.8 | 26.6 | 19.4 |
| 2024 | 10.4 | 10.4 | 10.4 | 20.5 | 25.9 | 21.1 | 25.9 | 20.4 | 12.6 |
| 2025 | 11.7 | 10.7 | 10.7 | 18.9 | 34.7 | 4.1 | 5.6 | 22.8 | 26.7 |
| 2026 to 26 Oct | −12.2 | 1.4 | 1.4 | −4.5 | −5.8 | −8.1 | −13.2 | −4.2 | −7.8 |

**Gold's contribution, before costs, cash 6% [own computation]**

| Version | 2008–2026 | 2011–2026 | 2008–2018 | 2019–2026 |
|---|---|---|---|---|
| c as specified | 11.1% | 10.4% | 9.6% | 13.2% |
| c, gold de-trended to 9.2% a year from 2019 | 10.2% | 9.3% | 9.6% | 11.0% |
| c, gold sleeve always in cash | 9.0% | 8.5% | 8.6% | 9.4% |
| e-c, three equity sleeves | 9.4% | 8.9% | 9.1% | 10.0% |
| d as specified | 12.7% | 13.3% | 10.9% | 15.3% |
| d, gold de-trended | 12.2% | 12.7% | 10.9% | 14.0% |
| d, gold slot always in cash | 9.4% | 9.3% | 9.4% | 9.3% |
| e-d, top 2 of 3 equity | 9.6% | 8.9% | 10.3% | 8.7% |
| b reader's rule (index signal) / b′ | 8.5% / 9.2% | 7.6% / 8.4% | 7.1% / 7.7% | 10.5% / 11.5% |

Average target weight in gold: c 17% in 2008–2018 and 21% in 2019–2026; d 18% and 28%. Average weight in midcap under d: 27% and 31%.

**State at the end of the data [own computation].** At the 30 Sep 2026 decision all four signal series were below their 200-DMA (Nifty 50 at 0.928 of it, Next 50 0.996, midcap 0.984, gold 0.989), so b, c, d, e-c and e-d were all 100% in cash. On 30 Oct 2026 the Nifty 50 closed at 23,053.10, 4.1% below its 200-DMA, so rule b stayed in cash; by 6 Nov the index was at 25,030.35, 4.3% above it. — [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME); [rishabhjain0295-web repo](https://github.com/rishabhjain0295-web/nifty500-momentum-backtest)

### Inferences
- On this engine the reader's rule earns about 2 points a year less with idle cash than with a 6% liquid ETF (5.5% against 7.6% over 2011–2026). Whether the cash actually sits in a liquid ETF matters more than the choice between the rule and most of its close variants.
- Rotation c's advantage before costs is about 2.5–2.9 points a year over rule b and 1.7–2.0 over b′ in every period, with a similar or shallower worst fall. Rotation d adds a further 1.2–2.9 points but with drawdowns of 23–37%, deeper than rule b in every period.
- In 2019–2026, taking gold out turns c's +2.7-point lead over b into a 0.5-point deficit (10.0% against 10.5%), and d's +4.8-point lead into a 1.8-point deficit. In 2008–2018 the no-gold versions still lead b by 2.0–3.2 points, but that sub-period leans on the synthetic midcap series and on JUNIORBEES's +124% in 2009.
- "De-trending" gold removes less than half of what removing gold does (c: 13.2% → 11.0% → 10.0%; d: 15.3% → 14.0% → 8.7%). The remainder is timing: gold rose when equities fell (2020, 2022, 2025–26), and that pattern is kept by the de-trended series. It is a property of this one stretch of history, not a guarantee.
- A passive equal-weight mix (f1) out-returned both rotations in every period before costs; what the rotations bought was a smaller worst fall (−17% to −25% against −27% in 2020 and −49% in 2008), not extra return.

### Gaps
- Four-asset results before 4 Feb 2011 use a synthetic midcap series that under-returned the real index by 2–7 points a year where it could be checked; u-c and u-d are the versions with real data throughout.
- Drawdowns are on daily closes of ETFs, which misprice on panic days; true intraday falls were larger.
- No dividends on the midcap index leg. No tracking error, premium/discount or expense drag for a liquid ETF beyond using a flat 6% or the overnight index.

## 5. Costs and tax at ₹1 lakh, ₹5 lakh and ₹20 lakh

### Takeaway
After Groww costs and FY 2026-27 tax rules, on a liquidated basis at ₹5 lakh, rotation c returned 9.3% a year over 2011–2026 against 6.6% for rule b (7.4% with the NIFTYBEES signal) and 8.8% for buy-and-hold NIFTYBEES; d returned 11.5% and the equal-weight passive mix 11.7%. Costs and tax together took about 1.1 points a year from c, 1.8 from d, 0.9 from b and 0.7–0.8 from the passive mixes; account size moved results by only 0.2–0.5 points.

### Cited Findings

**Model (`engine.py`).** Per order: brokerage 0.1% of value, minimum ₹5, maximum ₹20; exchange charge 0.00297%; SEBI 0.0001%; 18% GST on those three; stamp duty 0.015% on buys; STT 0.001% on sells of N50, NN50 and MID only; DP ₹23.60 per sell order; slippage 5 bps a side (10 bps for MID), also charged on the liquid ETF. Tax: equity ETF gains on units held ≤365 days 20.8%, longer 13% above ₹1.25 lakh per April–March year; gold ≤365 days at slab, longer 13% with no exemption; liquid ETF always slab; FIFO lots; short-term losses set against the highest-taxed gains first, long-term losses only against long-term gains, unused losses carried forward without expiry; tax paid on the last trading day of March by reducing the liquid holding first, then all holdings pro rata. Slab 31.2% unless stated. "Held" = value at the end with unrealised gains untaxed. "Liquidated" = everything sold on the end date and that year's tax paid. Each period is a fresh simulation starting with the stated capital. Cash leg = liquid ETF at a flat 6%. Data: [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME).

**2011–2026, CAGR % [own computation]**

| Variant | Before costs | After costs ₹1L / ₹5L / ₹20L | After tax, held ₹1L / ₹5L / ₹20L | After tax, liquidated ₹1L / ₹5L / ₹20L | Orders a year | Max drawdown after tax (₹5L) |
|---|---|---|---|---|---|---|
| a Buy-and-hold NIFTYBEES | 9.48 | 9.48 / 9.48 / 9.48 | 9.48 / 9.48 / 9.48 | 9.04 / 8.81 / 8.77 | 0.1 | −36.3% |
| b Reader's rule, liquid ETF 6% | 7.56 | 7.08 / 7.20 / 7.22 | 6.86 / 6.70 / 6.42 | 6.77 / 6.61 / 6.33 | 5.0 | −19.0% |
| b, idle cash 0% | 5.47 | 5.22 / 5.28 / 5.30 | 5.13 / 5.01 / 4.75 | 5.13 / 5.01 / 4.75 | 2.5 | −23.6% |
| b′ NIFTYBEES signal, liquid ETF 6% | 8.42 | 7.99 / 8.10 / 8.11 | 7.76 / 7.51 / 7.19 | 7.66 / 7.42 / 7.10 | 4.5 | −16.0% |
| b′, idle cash 0% | 6.38 | 6.16 / 6.21 / 6.22 | 6.07 / 5.87 / 5.60 | 6.07 / 5.87 / 5.60 | 2.3 | −19.6% |
| c Four sleeves 1.00× | 10.44 | 9.81 / 10.07 / 10.12 | 9.67 / 9.47 / 9.19 | 9.54 / 9.34 / 9.06 | 15.2 | −18.0% |
| c1 Four sleeves 1.01× | 10.02 | 9.33 / 9.65 / 9.69 | 9.12 / 9.04 / 8.74 | 8.98 / 8.90 / 8.61 | 15.7 | −20.0% |
| d Dual momentum | 13.30 | 12.68 / 12.84 / 12.87 | 12.05 / 11.73 / 11.48 | 11.85 / 11.53 / 11.29 | 11.4 | −25.7% |
| e-c No gold sleeves | 8.93 | 8.32 / 8.54 / 8.58 | 8.28 / 8.01 / 7.69 | 8.27 / 8.01 / 7.68 | 11.3 | −30.1% |
| e-d No gold dual momentum | 8.92 | 8.28 / 8.47 / 8.50 | 8.23 / 7.97 / 7.60 | 8.22 / 7.97 / 7.60 | 9.6 | −36.2% |
| u-c N50 + NN50 + gold sleeves | 10.40 | 9.82 / 10.03 / 10.07 | 9.50 / 9.38 / 9.09 | 9.33 / 9.21 / 8.92 | 11.8 | −13.2% |
| u-d Top 2 of N50, NN50, gold | 12.16 | 11.62 / 11.77 / 11.80 | 11.19 / 10.84 / 10.59 | 11.00 / 10.65 / 10.40 | 10.8 | −20.9% |
| f1 Equal weight, annual | 12.44 | 12.38 / 12.41 / 12.42 | 12.21 / 12.24 / 12.20 | 11.77 / 11.65 / 11.58 | 4.1 | −27.5% |
| f2 75 / 25, annual | 10.61 | 10.58 / 10.60 / 10.60 | 10.42 / 10.44 / 10.43 | 10.05 / 9.87 / 9.82 | 2.0 | −27.2% |
| f3 Buy-and-hold JUNIORBEES | 11.85 | 11.84 / 11.85 / 11.85 | 11.84 / 11.85 / 11.85 | 11.25 / 11.08 / 11.05 | 0.1 | −38.7% |
| f4 Buy-and-hold midcap (PR chain) | 12.95 | 12.94 / 12.94 / 12.94 | 12.94 / 12.94 / 12.94 | 12.28 / 12.14 / 12.11 | 0.1 | −44.2% |
| f5 Buy-and-hold GOLDBEES | 11.73 | 11.72 / 11.72 / 11.72 | 11.72 / 11.72 / 11.72 | 10.92 / 10.92 / 10.92 | 0.1 | −27.1% |

**Other periods, after tax, liquidated, CAGR % at ₹1L / ₹5L / ₹20L (before-cost figure in brackets) [own computation]**

| Variant | 2008–2026 | 2008–2018 | 2019–2026 |
|---|---|---|---|
| a | 7.53 / 7.34 / 7.31 (7.90) | 5.64 / 5.24 / 5.11 (5.65) | 11.08 / 10.25 / 10.09 (11.13) |
| b, liquid ETF 6% | 7.79 / 7.50 / 7.17 (8.51) | 6.40 / 6.37 / 5.94 (7.11) | 9.64 / 9.30 / 8.90 (10.51) |
| b, idle cash 0% | 6.10 / 5.92 / 5.58 (6.38) | 4.71 / 4.73 / 4.34 (4.95) | 8.08 / 7.81 / 7.39 (8.42) |
| b′, liquid ETF 6% | 8.48 / 8.11 / 7.78 (9.24) | 6.91 / 6.81 / 6.39 (7.65) | 10.64 / 10.18 / 9.79 (11.52) |
| c | 10.19 / 9.89 / 9.64 (11.12) | 8.70 / 8.70 / 8.37 (9.65) | 12.14 / 11.82 / 11.48 (13.23) |
| c1 | 9.29 / 9.07 / 8.83 (10.27) | 7.06 / 7.10 / 6.81 (8.16) | 12.19 / 11.94 / 11.60 (13.31) |
| d | 11.33 / 11.05 / 10.79 (12.70) | 9.67 / 9.56 / 9.20 (10.89) | 13.64 / 13.44 / 13.10 (15.30) |
| e-c | 8.73 / 8.41 / 8.09 (9.43) | 8.30 / 8.22 / 7.80 (9.06) | 9.22 / 8.91 / 8.53 (9.95) |
| e-d | 8.87 / 8.52 / 8.19 (9.64) | 9.61 / 9.36 / 8.90 (10.34) | 7.78 / 7.64 / 7.24 (8.65) |
| u-c | 10.80 / 10.45 / 10.21 (11.83) | 9.50 / 9.34 / 9.02 (10.56) | 12.39 / 12.23 / 11.86 (13.65) |
| u-d | 10.72 / 10.39 / 10.12 (11.82) | 8.77 / 8.58 / 8.22 (9.83) | 13.16 / 13.02 / 12.71 (14.69) |
| f1 | 11.55 / 11.49 / 11.41 (12.23) | 9.55 / 9.11 / 9.01 (9.90) | 14.94 / 14.42 / 14.31 (15.60) |
| f2 | 9.80 / 9.69 / 9.65 (10.39) | 7.79 / 7.41 / 7.31 (8.08) | 13.12 / 12.66 / 12.53 (13.73) |
| f3 | 9.14 / 8.99 / 8.96 (9.62) | 7.75 / 7.18 / 7.07 (7.78) | 12.07 / 11.29 / 11.14 (12.26) |
| f4 | 9.96 / 9.83 / 9.81 (10.49) | 6.44 / 5.97 / 5.84 (6.47) | 15.76 / 15.14 / 15.03 (16.42) |
| f5 | 12.79 at all sizes (13.55) | 8.37 (9.22) | 18.34 (19.94) |

**Slab-rate sensitivity, ₹5 lakh, after tax, liquidated, CAGR % [own computation]**

| Period | Variant | Slab 5.2% | Slab 20.8% | Slab 31.2% |
|---|---|---|---|---|
| 2011–2026 | b | 6.79 | 6.68 | 6.61 |
| | b′ | 7.62 | 7.50 | 7.42 |
| | c | 9.44 | 9.37 | 9.34 |
| | d | 11.68 | 11.58 | 11.53 |
| | f1 | 11.69 | 11.66 | 11.65 |
| 2008–2018 | b / c / d | 6.59 / 8.88 / 9.78 | 6.45 / 8.77 / 9.64 | 6.37 / 8.70 / 9.56 |
| 2019–2026 | b / c / d | 9.56 / 11.91 / 13.50 | 9.40 / 11.84 / 13.45 | 9.30 / 11.82 / 13.44 |
| 2008–2026 | b / c / d | 7.72 / 10.02 / 11.20 | 7.58 / 9.94 / 11.10 | 7.50 / 9.89 / 11.05 |

**Rotation minus the reader's rule, after costs and tax, liquidated, ₹5 lakh, points a year [own computation]**

| Comparison | 2008–2026 | 2011–2026 | 2008–2018 | 2019–2026 |
|---|---|---|---|---|
| c − b (index signal) | +2.4 | +2.7 | +2.3 | +2.5 |
| c − b′ (NIFTYBEES signal) | +1.8 | +1.9 | +1.9 | +1.6 |
| d − b | +3.6 | +4.9 | +3.2 | +4.1 |
| d − b′ | +2.9 | +4.1 | +2.8 | +3.3 |
| e-c (no gold) − b | +0.9 | +1.4 | +1.9 | −0.4 |
| e-c (no gold) − b′ | +0.3 | +0.6 | +1.4 | −1.3 |
| e-d (no gold) − b | +1.0 | +1.4 | +3.0 | −1.7 |
| e-d (no gold) − b′ | +0.4 | +0.6 | +2.6 | −2.5 |
| c − a (buy-and-hold NIFTYBEES) | +2.6 | +0.5 | +3.5 | +1.6 |
| c − f1 (equal-weight passive) | −1.6 | −2.3 | −0.4 | −2.6 |
| d − f1 | −0.4 | −0.1 | +0.5 | −1.0 |

### Inferences
- Costs: at ₹1 lakh the fixed charges (₹5 minimum brokerage, ₹23.60 DP per sell) cost rotation c about 0.6 points a year against 0.4 at ₹5 lakh and 0.3 at ₹20 lakh. Slippage and stamp duty, which scale with size, are most of the cost above ₹5 lakh.
- Tax: the ₹1.25 lakh exemption works against larger accounts — c's tax drag over 2011–2026 is about 0.3 points at ₹1 lakh, 0.7 at ₹5 lakh and 1.1 at ₹20 lakh (liquidated basis). The slab rate barely matters (0.1–0.3 points between 5.2% and 31.2%) because most gains are equity short-term or long-term gains taxed at fixed rates and the liquid ETF's gains are small.
- Rule b after tax (6.6–7.4%) was below buy-and-hold NIFTYBEES after tax (8.8%) over 2011–2026 on this engine; rotation c (9.3%) was slightly above it; neither beat a passive equal-weight mix of the same four assets (11.7%).
- Every rotation's after-tax edge over the passive mix is negative or near zero; the case for rotation rests on the smaller drawdown, and that case is weaker for d (−25.7%) than for c (−18.0%) against f1's −27.5% in 2011–2026.

### Gaps
- **Simplifications:** FY 2026-27 rates and the ₹1.25 lakh exemption are applied to the whole history and not inflation-adjusted; no surcharge; no rebate or basic-exemption effects at low slabs; loss carry-forward has no 8-year limit; tax is paid without triggering further sales tax or trading cost; Groww's "lower of ₹5 or 2.5%" floor for tiny orders is ignored; the 12-month test is 365 days; grandfathering and the old indexation rules for gold are ignored; the liquid ETF is treated as a growth ETF taxed on sale (a daily-dividend ETF such as LIQUIDBEES is taxed differently); the Groww API subscription fee is not included; no dividends on the midcap index leg.
- The reader's own after-tax figure (8.07%) could not be reproduced exactly; the closest here is 7.4–7.7% (b′ at ₹5 lakh, held or liquidated).

## 6. Robustness: decision day, look-back, buffer, execution lag, rebalance band

### Takeaway
The reader's rule is far more sensitive to the day of the month than either rotation: over 2011–2026, moving the decision from month-end to the 15th trading day cuts its return from 7.6% to 3.9% and deepens its worst fall from −18% to −43%, because a mid-month check sat through most of the March 2020 crash. Month-end is close to the luckiest choice in this sample. The ranking c > b held in all 30 day × look-back × buffer combinations after tax in every period (29 of 30 against b′ in 2008–2018); the no-gold rotation's lead over b did not hold in 2019–2026.

### Cited Findings

All from `run6.py` / `out6.txt`, cash 6%, data [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME). "After tax" = ₹5 lakh, 31.2% slab, liquidated.

**(i) Decision day of the month, same-day close, 2011–2026 [own computation]**

| Variant | Metric | 5th trading day | 10th | 15th | 20th | Month-end |
|---|---|---|---|---|---|---|
| b | CAGR before costs | 6.3% | 7.2% | 3.9% | 7.8% | 7.6% |
| | Max drawdown | −20.1% | −23.5% | −42.6% | −17.1% | −18.3% |
| | CAGR after tax | 5.6% | 6.4% | 3.3% | 6.9% | 6.6% |
| b′ | CAGR before costs | 6.3% | 5.7% | 3.9% | 8.0% | 8.4% |
| | Max drawdown | −20.1% | −23.5% | −42.6% | −18.9% | −15.4% |
| | CAGR after tax | 5.6% | 5.1% | 3.4% | 7.1% | 7.4% |
| c | CAGR before costs | 10.8% | 9.9% | 8.3% | 9.2% | 10.4% |
| | Max drawdown | −15.2% | −17.7% | −30.9% | −18.4% | −16.6% |
| | CAGR after tax | 9.7% | 8.9% | 7.4% | 8.1% | 9.3% |
| d | CAGR before costs | 13.5% | 13.5% | 11.6% | 11.8% | 13.3% |
| | Max drawdown | −24.0% | −21.1% | −31.3% | −28.5% | −24.7% |
| | CAGR after tax | 11.7% | 11.8% | 10.0% | 10.2% | 11.5% |
| e-c | CAGR before costs | 9.1% | 8.0% | 6.1% | 7.5% | 8.9% |
| | Max drawdown | −25.1% | −25.8% | −44.2% | −30.6% | −28.7% |
| e-d | CAGR before costs | 9.7% | 8.9% | 6.5% | 7.4% | 8.9% |
| | Max drawdown | −26.8% | −26.1% | −48.1% | −37.9% | −35.1% |

Other periods, CAGR before costs across the five decision days (range): 2008–2026 — b 5.2–8.5%, b′ 5.1–9.2%, c 9.4–11.4%, d 11.5–12.7%; 2008–2018 — b 4.6–7.5%, c 8.6–10.3%, d 8.6–10.9%, e-c 7.9–10.4%, e-d 9.1–10.8%; 2019–2026 — b 5.9–10.5%, b′ 3.9–11.5%, c 9.7–13.3%, d 14.0–16.4%, e-c 5.3–10.0%, e-d 5.2–9.7%. Max drawdown range 2019–2026: b −13.9% to −38.4%; c −13.5% to −26.6%; d −21.1% to −24.0%.

**Trade at the next day's close instead of the decision day's close (month-end decisions), CAGR before costs [own computation]**

| Variant | 2008–2026 same day → next day | 2011–2026 | 2008–2018 | 2019–2026 |
|---|---|---|---|---|
| b | 8.5 → 7.7 | 7.6 → 7.0 | 7.1 → 6.1 | 10.5 → 10.1 |
| b′ | 9.2 → 8.6 | 8.4 → 8.0 | 7.7 → 6.7 | 11.5 → 11.2 |
| c | 11.1 → 10.5 | 10.4 → 10.1 | 9.6 → 8.8 | 13.2 → 12.9 |
| d | 12.7 → 11.5 | 13.3 → 12.6 | 10.9 → 9.6 | 15.3 → 14.3 |
| e-c | 9.4 → 8.4 | 8.9 → 8.4 | 9.1 → 7.7 | 10.0 → 9.5 |
| e-d | 9.6 → 8.7 | 8.9 → 8.5 | 10.3 → 9.1 | 8.7 → 8.1 |

Max drawdown with next-day execution, 2011–2026: b −21.0%, b′ −15.3%, c −16.8%, d −25.8%. For the 5th-trading-day decision the next-day version was not worse (b 6.4%, c 10.9%, d 13.6% over 2011–2026).

**(ii) Look-back, month-end decisions, 2011–2026 [own computation]**

| Variant | Metric | 150-day | 200-day | 250-day | 10-month |
|---|---|---|---|---|---|
| b | CAGR before costs / max drawdown | 9.0% / −15.4% | 7.6% / −18.3% | 8.3% / −16.1% | 8.4% / −18.3% |
| b′ | | 8.9% / −17.7% | 8.4% / −15.4% | 7.9% / −16.1% | 8.6% / −14.8% |
| c | | 10.1% / −18.2% | 10.4% / −16.6% | 10.2% / −14.7% | 10.0% / −18.3% |
| d (filter look-back only) | | 13.2% / −26.0% | 13.3% / −24.7% | 14.1% / −21.5% | 12.5% / −27.2% |
| e-c | | 8.7% / −30.9% | 8.9% / −28.7% | 8.6% / −26.4% | 8.6% / −30.1% |
| e-d | | 8.5% / −37.1% | 8.9% / −35.1% | 9.1% / −32.3% | 8.1% / −37.2% |

In 2008–2018 the 250-day look-back was the weak one: b 5.4%, c 7.1%, e-c 6.3%, e-d 7.2% (against 7.1%, 9.6%, 9.1%, 10.3% at 200 days). In 2019–2026 b ranged 10.2–11.0%, b′ 8.8–12.7%, c 13.0–13.8%, d 14.9–16.8%.

**(iii) Buffer, month-end, 200-day, CAGR before costs [own computation]**

| Variant | 2011–2026: 1.00× / 1.01× / 1.02× | 2008–2018 | 2019–2026 |
|---|---|---|---|
| b | 8.0 / 7.6 / 7.6 | 6.6 / 7.1 / 7.8 | 11.4 / 10.5 / 9.0 |
| b′ | 8.9 / 8.4 / 8.6 | 8.0 / 7.7 / 8.4 | 12.1 / 11.5 / 10.3 |
| c | 10.4 / 10.0 / 10.0 | 9.6 / 8.2 / 8.0 | 13.2 / 13.3 / 13.2 |
| d | 13.3 / 13.1 / 13.9 | 10.9 / 9.8 / 9.5 | 15.3 / 16.5 / 18.7 |
| e-c | 8.9 / 8.3 / 8.8 | 9.1 / 7.2 / 7.3 | 10.0 / 10.2 / 10.9 |
| e-d | 8.9 / 8.3 / 9.0 | 10.3 / 7.6 / 7.7 | 8.7 / 9.7 / 10.9 |

The 1% buffer helped rule b in 2008–2018 (+0.5 points) and hurt it in 2019–2026 (−0.9 points); over 2011–2026 it cost 0.4 points. No consistent sign.

**Rebalance band (0, 2.5, 5, 10 points), 2011–2026, CAGR before costs:** c 10.0 / 10.2 / 10.4 / 10.7%; d 13.3 / 13.3 / 13.3 / 13.6%; e-c 8.9 / 9.0 / 8.9 / 8.9%. Wider bands let winning sleeves run; the effect is about 0.7 points for c and nil for the no-gold version.

**Grid of 30 specifications per variant (5 decision days × 150/200/250-day × 1.00/1.01 buffer), same-day close [own computation]**

| Variant | Period | CAGR after tax: min / median / max | Max drawdown: worst / median / best |
|---|---|---|---|
| b | 2011–2026 | 3.0 / 6.0 / 8.4 | −42.6 / −23.1 / −14.1 |
| b′ | 2011–2026 | 2.9 / 5.9 / 8.1 | −42.6 / −20.5 / −14.4 |
| c | 2011–2026 | 7.3 / 8.9 / 9.8 | −30.9 / −17.6 / −14.4 |
| d | 2011–2026 | 9.0 / 11.2 / 12.2 | −31.7 / −24.4 / −21.1 |
| e-c | 2011–2026 | 5.4 / 7.3 / 9.1 | −44.2 / −29.3 / −22.4 |
| e-d | 2011–2026 | 5.2 / 7.4 / 8.9 | −48.1 / −34.4 / −24.1 |
| b | 2008–2018 | 2.8 / 5.4 / 8.1 | −36.5 / −27.8 / −22.0 |
| c | 2008–2018 | 5.2 / 8.4 / 10.1 | −34.9 / −21.6 / −19.9 |
| d | 2008–2018 | 6.0 / 8.2 / 9.6 | −51.6 / −36.4 / −28.9 |
| e-c | 2008–2018 | 3.9 / 8.0 / 10.4 | −42.5 / −32.3 / −26.6 |
| e-d | 2008–2018 | 4.1 / 8.5 / 10.2 | −49.3 / −37.6 / −28.9 |
| b | 2019–2026 | 3.6 / 8.3 / 10.7 | −38.4 / −20.1 / −10.6 |
| c | 2019–2026 | 8.7 / 11.0 / 12.9 | −26.9 / −14.9 / −11.5 |
| d | 2019–2026 | 11.4 / 13.8 / 15.5 | −24.1 / −22.5 / −20.6 |
| e-c | 2019–2026 | 4.5 / 8.1 / 10.9 | −36.1 / −22.5 / −14.0 |
| e-d | 2019–2026 | 4.2 / 7.4 / 9.8 | −39.2 / −24.6 / −18.3 |

**Matched comparison (same day, look-back and buffer for both), after-tax CAGR difference in points [own computation]**

| Comparison | 2008–2026 min / median / max; wins | 2011–2026 | 2008–2018 | 2019–2026 |
|---|---|---|---|---|
| c − b | +1.1 / +3.0 / +5.0; 30 of 30 | +1.0 / +2.9 / +4.8; 30 of 30 | +0.2 / +2.6 / +4.7; 30 of 30 | +1.6 / +3.3 / +5.6; 30 of 30 |
| c − b′ | +0.9 / +2.7 / +5.0; 30 | +1.1 / +3.1 / +4.9; 30 | −0.2 / +2.1 / +4.8; 29 | +1.1 / +3.7 / +5.9; 30 |
| d − b | +1.5 / +4.1 / +6.1; 30 | +2.9 / +5.0 / +7.6; 30 | 0.0 / +2.3 / +4.8; 30 | +3.4 / +5.7 / +9.7; 30 |
| e-c − b | −0.5 / +1.4 / +3.5; 28 | −0.1 / +1.5 / +3.3; 29 | −0.8 / +2.2 / +4.8; 28 | −1.2 / +0.4 / +2.4; 19 |
| e-c − b′ | −0.7 / +1.4 / +3.6; 26 | −0.4 / +1.5 / +3.4; 27 | −1.2 / +1.6 / +4.9; 28 | −1.8 / +0.6 / +2.8; 23 |
| e-d − b | −0.5 / +1.4 / +3.9; 26 | −0.5 / +1.5 / +3.8; 28 | 0.0 / +2.5 / +4.9; 30 | −2.6 / −0.2 / +2.5; 14 |
| e-d − b′ | −0.7 / +1.5 / +4.0; 27 | −0.5 / +1.5 / +4.0; 27 | −0.4 / +2.2 / +5.0; 28 | −3.0 / +0.2 / +2.8; 16 |

Max drawdown difference against b on matched specifications (positive = shallower than b), median: c +4.4 (2008–2026), +6.5 (2011–2026), +2.9 (2008–2018), +4.2 (2019–2026); d −7.3, +0.1, −8.6, −4.0; e-c −5.2, −5.2, −5.1, −1.8; e-d −9.6, −7.9, −10.5, −3.6.

### Inferences
- **Timing luck is the largest single source of dispersion for rule b**: 3.9–7.8% before costs and −17% to −43% worst fall over 2011–2026 from the decision day alone. The reader's month-end, 200-day, 1%-buffer, NIFTYBEES-signal specification sits in the upper part of the 30-specification range for 2011–2026 (7.4% after tax, against a median of 5.9% and a maximum of 8.1%).
- The four-sleeve rotation is less exposed to timing luck (after-tax range 7.3–9.8% over 2011–2026) because four signals rarely flip on the same day, but its worst fall still reached −31% with a mid-month decision.
- The "winner" between c and b does not change with these choices in any period. The "winner" between the **no-gold** rotations and b does change: in 2019–2026 e-c wins in 19 of 30 specifications and e-d in 14 of 30.
- Between c and d the higher return of d is consistent (median across specifications 11.2% against 8.9% after tax, 2011–2026), and so is its deeper drawdown (median −24.4% against −17.6%).
- Trading at the next day's close costs 0.3–1.4 points a year for month-end decisions in this sample; a 15:10 decision executed before the close would sit somewhere between the two.

### Gaps
- No test of weekly or staggered ("tranched") decisions, of momentum look-backs other than 6 and 12 months, or of a top-1 version of d.
- Thirty specifications from one 19-year history are not independent samples; the ranges describe sensitivity, not a confidence interval.

## 7. Verdict from the numbers

### Takeaway
On this data, rotation c beat the reader's rule after costs and tax in every sub-period by about 1.6–2.7 points a year with a similar or smaller worst fall, and rotation d by 2.8–4.9 points with a deeper one; but in 2019–2026 the whole of that edge came from gold, and a passive annual-rebalanced mix of the same four assets returned more than either rotation in most periods. These are back-test results from one history, not expected returns.

### Cited Findings
All figures are [own computation] from the tables above; data [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME).

- **Does c or d beat b after costs and tax, by sub-period (₹5 lakh, 31.2% slab, liquidated)?** 2008–2018: b 6.4% (b′ 6.8%), c 8.7%, d 9.6%. 2019–2026: b 9.3% (b′ 10.2%), c 11.8%, d 13.4%. 2011–2026: b 6.6% (b′ 7.4%), c 9.3%, d 11.5%. Yes in each, by +1.6 to +2.7 points for c and +2.8 to +4.9 for d.
- **At what risk?** Worst fall before costs, 2011–2026: b −18.3% (b′ −15.4%), c −16.6%, d −24.7%. Full period: b −27.8%, c −21.5%, d −36.8% (early 2008, partly on synthetic midcap data; the all-real-data version u-d fell 27.7%).
- **How much disappears without gold?** After tax at ₹5 lakh: c's lead over b falls from +2.7 to +1.4 points over 2011–2026 (about half) and from +2.5 to −0.4 over 2019–2026 (all of it). d's lead falls from +4.9 to +1.4 over 2011–2026 (about 70%) and from +4.1 to −1.7 over 2019–2026. In 2008–2018 the no-gold versions keep most of the lead (+1.9 and +3.0 against b), on weaker data.
- **How much disappears outside 2019–2026?** c's lead over b is about the same size in 2008–2018 (+2.3) as in 2019–2026 (+2.5); d's is smaller (+3.2 against +4.1). The lead is not confined to 2019–2026, but its source differs: midcaps and Next 50 in 2009–2017, gold in 2019–2026.
- **Against doing nothing clever:** buy-and-hold NIFTYBEES after tax returned 8.8% over 2011–2026 (worst fall −36.3%); 75/25 Nifty/gold 9.9% (−27.2%); equal weight of the four 11.7% (−27.5%). Rule b was below all three on return; c was above buy-and-hold by 0.5 points and below the equal-weight mix by 2.3.
- **Dispersion across near-equivalent specifications, after tax, 2011–2026:** b 3.0–8.4% (median 6.0%); c 7.3–9.8% (8.9%); d 9.0–12.2% (11.2%); no-gold c 5.4–9.1% (7.3%); no-gold d 5.2–8.9% (7.4%).
- **Right now:** every trend variant was fully in cash from 30 Sep 2026, and rule b still was on 30 Oct 2026, while the Nifty 50 rose about 10% between 26 Oct and 9 Nov 2026 (section 1). — [nifty-market-digest-bot](https://github.com/Indranil-Mondal/nifty-market-digest-bot)

### Inferences
- A defensible way to state the forward question, without forecasting: if gold's next decade resembles 2008–2018 rather than 2019–2026 and its tendency to rise when Indian equities fall is not repeated, the evidence here supports an after-tax edge for the sleeve rotation over the reader's rule somewhere between roughly −1 and +3 points a year (matched no-gold comparisons: −1.2 to +2.4, median +0.4, in 2019–2026; −0.1 to +3.3, median +1.5, in 2011–2026), with a **deeper** worst fall than the rule (median about 2–5 points deeper). If gold keeps diversifying as it did, the range seen was +1 to +5.6 points with a worst fall about 3–6 points shallower at the median. The data cannot say which will hold.
- The choice of decision day moved rule b's result by more (about 4 points a year and 25 points of drawdown) than the choice between rule b and rotation c did at month-end (about 2–3 points). Whatever is adopted, a single month-end check carries this timing risk; the rotation carries less of it.
- The most robust findings are negative ones: (1) rule b's after-tax return was below buy-and-hold NIFTYBEES (8.8%) in all 30 specifications over 2011–2026 (maximum 8.4%) and at the median in 2019–2026 (8.3% against 10.3%), though above it at the median in 2008–2018 (5.4% against 5.2%); (2) rotation c did not beat a passive equal-weight mix of the same assets on after-tax return in any period, and d did so only in 2008–2018 (+0.5 points); (3) the dual-momentum variant's worst fall was only about 2.5 points shallower than a passive 75/25 mix in 2011–2026 (−24.7% against −27.2%), and in 2008 it fell 36.8% against 27.8% for rule b and 43.9% for 75/25.
- Parking the "out" money in a liquid ETF rather than idle cash was worth about 2 points a year to rule b; that is as large as the rotation's edge and carries far less model risk.

### Gaps
- One history, one run, no independent review; no out-of-sample period; 2008–Feb 2011 midcap data are synthetic; midcap leg is price-return from 2012; cash is a flat 6% (overnight index only from mid-2016); FY 2026-27 tax rules applied to all years.
- The reader's own 8.55% / 8.07% could only be approximated (7.8–8.4% / 7.4–7.7%); differences in data source are the likely cause but were not resolved.
- Not tested: tranching across several decision days, a volatility-scaled or risk-parity sleeve sizing, silver or international ETFs as extra sleeves, and what happens if the liquid ETF trades at a discount on the day of a switch.
