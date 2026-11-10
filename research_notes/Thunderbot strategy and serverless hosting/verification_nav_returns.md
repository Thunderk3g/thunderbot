# Verification of the report's return tables from mutual-fund NAV history (mfapi.in), as of 10 November 2026

> **What this is.** A verification and gap-filling pass on `reports/Thunderbot strategy and serverless hosting.md`, using daily NAV history from the free public API `api.mfapi.in` (which republishes AMFI NAVs). Every number below is **[own computation]** from cached NAV files unless marked otherwise. These are historical figures, not forecasts. Single run, unreviewed.
>
> **Data access.** 35 requests in total, all HTTP 200, one at a time with a one-second pause, fetched 10 Nov 2026 19:21–19:24 UTC: one scheme list (`https://api.mfapi.in/mf`) and 34 NAV histories (`https://api.mfapi.in/mf/<schemeCode>`). No request was refused. Latest NAV in the files: **9 Nov 2026** for equity, gold and silver schemes, **10 Nov 2026** for liquid and overnight schemes. Exchange closing prices used for the price-versus-NAV comparisons are the earlier session's [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME) snapshot (to 26 Oct 2026). Ticker-to-ISIN mapping comes from the Dhan scrip master in [Jainu-s/nse_indices_historical_data](https://github.com/Jainu-s/nse_indices_historical_data) (`data/dhan_scrip_master.csv`, repo snapshot 11 Jun 2026) and NSEDATA4ME's `isin_symbol_map.json`; mfapi's ISIN field links the two.
>
> **Files.** Scripts: `/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/verify_nav/scripts/` (`fetch.sh`, `navlib.py`, `core.py`, `q1.py` liquid, `q2.py` asset classes, `q3.py` factor funds, `q5.py` price versus NAV, `q6.py` residual checks; run with `python3 -I`). Cache: `/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/verify_nav/data/` (`mf_<code>.json`, `_requests.log`).
>
> **Method.** Calendar-year return = last NAV on or before 31 Dec of year Y divided by last NAV on or before 31 Dec of Y−1. Power-of-ten NAV steps (unit splits, face-value changes) are detected and back-adjusted to today's unit basis; each one is listed. Old BeES history sits under earlier scheme codes (Benchmark, then Goldman Sachs, then Nippon) and is joined end to end; one trading day is missing at each join (19 Aug 2011 and 4 Nov 2016) and the NAVs either side are continuous. Drawdowns use daily NAVs. "2008–2026" means 31 Dec 2007 to the stated end date.

## (a) Summary: what holds and what changes

**Holds up**
1. **Liquid ETF yields are confirmed to two decimals.** LIQUIDCASE 5.64% a year from 24 Jan 2024 to 26 Oct 2026, LIQUIDADD 5.54% from 3 Apr 2024, GROWWLIQID 5.24% from 26 Sep 2024; LIQUIDCASE 5.52% in 2025 and 4.02% in 2026 to 26 Oct; NAV ₹116.7309 on 4 Nov 2026. None of the three has had a single down day in NAV.
2. **The recalled 2008–2016 overnight returns hold within 0.35 points every year** against HDFC Overnight Fund's NAV (7.54, 3.34, 4.73, 7.46, 8.24, 8.21, 8.16, 7.29, 6.41). The computed 2017–2026 overnight index rows are also confirmed: overnight funds earned 0.05–0.21 points less than the index each year.
3. **LIQUIDADD is DSP BSE Liquid Rate ETF** (ISIN INF740KA1UM0, scheme 152555, base ₹1,000). LOWVOLIETF and ALPL30IETF are ICICI Prudential ETFs, as the brief said.
4. **The year-by-year NIFTYBEES, JUNIORBEES and MID150BEES returns match NAV within 1 point** in every year except three cells (NIFTYBEES 2009; JUNIORBEES 2009 and 2012), and period CAGRs match within 0.1–0.2 points.
5. **The momentum slump is confirmed on the fund itself:** UTI Nifty200 Momentum 30 direct plan fell 31.50% from 27 Sep 2024 to 7 Apr 2025 (same dates as the index's 31.8%), has not regained its peak, and stood 26.4% below it on 26 Oct 2026 and 20.0% below on 9 Nov 2026. The UTI regular plan's calendar years (−5.95, 40.67, 20.72, −5.54) match the report within 0.4 points. The 1-, 3- and 5-year figures to mid-September 2026 (−3.39, 9.47, 8.73) match the report's.
6. **The Nifty's rebound after the data ended is confirmed:** NIFTYBEES NAV rose 10.10% from 26 Oct to 9 Nov 2026 (JUNIORBEES 9.51%, MID150BEES 7.70%).

**Needs correcting or qualifying**
1. **Gold in 2013 and 2014.** NAV returns were **−14.1% and +0.8%**, not −6.4% and −9.3%. The report's figures are exchange closing prices, and GOLDBEES closed 8.9% above NAV on 31 Dec 2013 (monthly median premium +10.6% in December 2013). Both pairs compound to nearly the same two-year result. The price figures are what a seller on the exchange got, so the backtest is not wrong, but the table should say it is price-based and that a premium of that size sat in the data. Smaller gold differences in 2008, 2009, 2016, 2022 and 2023 have the same cause.
2. **"ETF price returns track total return closely" is not true for NIFTYBEES before 2016.** The NAV fell 0.9–1.9% against a Nifty 50 index fund on six single days (15 Sep 2008, 9 Jul 2009, 12 Mar 2012, 14 Mar 2013, 11 Mar 2014, 20 Feb 2015), the pattern of cash distributions; JUNIORBEES shows one (11 Mar 2014). Adding them back lifts NIFTYBEES buy-and-hold from **5.6% to 6.4% a year for 2008–2018**, from 9.5% to 9.8% for 2011–26 Oct 2026 and from 7.9% to 8.3% for 2008–26 Oct 2026. The distributions are inferred from NAV behaviour, not confirmed from an AMC notice.
3. **Worst falls measured on closing prices are too shallow by about 2 points.** On NAV, NIFTYBEES fell **38.4%** in 2020 (report: 36.3%), because the ETF closed 3.45% above NAV on 23 Mar 2020. JUNIORBEES: 40.5% against 38.7% (2011–26) and 36.2% against 34.5% (2019–26). Gold's worst NAV fall is 29.5% (28 Aug 2013 to 31 Jul 2015) against 27.1% on price.
4. **The flat 6% cash assumption is fair for 2011–2026 as a whole and about 1.1 points too high for 2019–2026.** Overnight funds returned 6.1% a year over 2011–2026 and 5.0–5.1% over 2019–2026; growth liquid ETFs have earned about 0.2–0.35 points less than those funds. Trailing 1-year liquid ETF returns are now 4.7–5.0% and 7-day annualised yields 5.0–5.3%.
5. **UTI fund since-launch figures are date-sensitive and the regular/direct pair in the notes was mislabelled.** As of 9 Nov 2026: **direct 14.1% a year, regular 13.6%** from the first NAV (12 Mar 2021). The "NAV 19.84 on 30 Oct 2026" in the notes is the direct plan (regular was 19.30). The report's "14.5–14.75% direct, about 13% regular" mixes dates; the true gap between plans is 0.56 points a year, not 1.5.
6. **Factor products have trailed their indices by more than the report implies.** Kotak Nifty Alpha 50 ETF returned 8.3% a year since its first NAV (29 Dec 2021) against 9.1% for a Nifty 50 index fund and 10.7% for a Nifty 500 index fund, and trailed its own index by 0.6–3.1 points in each calendar year. Tata Nifty Midcap150 Momentum 50 Index Fund trailed its index by 2.7, 1.4 and 0.7 points in 2023–2025 and trailed MID150BEES by 1.9 points a year since 31 Oct 2022.
7. **All "to 26 Oct 2026" figures are stale by one sharp fortnight.** To 9 Nov 2026 the 2026 year-to-date NIFTYBEES return is −3.2% (not −12.2%), and NIFTYBEES 2019–2026 is 12.5% a year (not 11.1%).

## (b) Verification table

Source column: scheme code = `https://api.mfapi.in/mf/<code>`. As-of: data fetched 10 Nov 2026; latest NAV 9 Nov 2026 (equity, gold) or 10 Nov 2026 (liquid).

| # | Report claim (section) | Status | Evidence [own computation] | Source | As-of |
|---|---|---|---|---|---|
| 1 | "LIQUIDCASE 5.64% a year since January 2024" (Liquid ETFs: use the growth kind) | CONFIRMED | NAV 24 Jan 2024 → 26 Oct 2026: 5.64% a year; to 10 Nov 2026 from first NAV (23 Jan 2024): 5.64% | [152327](https://api.mfapi.in/mf/152327) | 10 Nov 2026 |
| 2 | "LIQUIDADD 5.54% … since April 2024" | CONFIRMED | 3 Apr 2024 → 26 Oct 2026: 5.54%; from first NAV 27 Mar 2024 → 10 Nov 2026: 5.55% | [152555](https://api.mfapi.in/mf/152555) | 10 Nov 2026 |
| 3 | "GROWWLIQID 5.24% … since September 2024" | CONFIRMED | 26 Sep 2024 → 26 Oct 2026: 5.24% | [152891](https://api.mfapi.in/mf/152891) | 10 Nov 2026 |
| 4 | "LIQUIDCASE returned 5.5% in 2025 and 4.0% in 2026 to 26 October, about 4.9% annualised" | CONFIRMED | 5.52% and 4.02%; 2026 to 10 Nov 4.24% (4.95% annualised) | [152327](https://api.mfapi.in/mf/152327) | 10 Nov 2026 |
| 5 | "LIQUIDCASE's NAV stood at about ₹116.73 on 4 November 2026 from a ₹100 base" | CONFIRMED | NAV 116.7309 on 4 Nov 2026; first NAV 100.1995 on 23 Jan 2024 | [152327](https://api.mfapi.in/mf/152327) | 10 Nov 2026 |
| 6 | "None of the three had a down day larger than 0.01%" | CONFIRMED (stronger) | Smallest daily NAV change is positive for all three (no down day in NAV) | 152327, 152555, 152891 | 10 Nov 2026 |
| 7 | "Current 7-day yields were not sourced" | GAP FILLED | 7-day annualised to 10 Nov 2026: LIQUIDCASE 5.20%, LIQUIDADD 5.27%, GROWWLIQID 5.00%; 30-day 5.33 / 5.31 / 5.07; 1-year 4.96 / 4.94 / 4.73 | 152327, 152555, 152891 | 10 Nov 2026 |
| 8 | "The mapping of LIQUIDADD to DSP's BSE Liquid Rate ETF is [recalled]" (instrument list; What could not be confirmed) | CONFIRMED | mfapi scheme 152555 "DSP BSE Liquid Rate ETF", ISIN INF740KA1UM0; Dhan scrip master lists NSE symbol LIQUIDADD with the same ISIN | [152555](https://api.mfapi.in/mf/152555); [Dhan scrip master copy](https://github.com/Jainu-s/nse_indices_historical_data) | 10 Nov 2026 |
| 9 | Overnight return 2008 "about 7–8%" … 2016 "about 6.4%" [recalled] (table in Liquid ETFs section) | CONFIRMED within 0.35 points | HDFC Overnight Reg-G: 7.54, 3.34, 4.73, 7.46, 8.24, 8.21, 8.16, 7.29, 6.41 for 2008–2016. Largest gaps: 2011 (7.46 against 7.8) and 2010 (4.73 against 5) | [101996](https://api.mfapi.in/mf/101996) | 10 Nov 2026 |
| 10 | Overnight index 2017–2025: 6.0, 6.2, 5.8, 3.4, 3.3, 4.7, 6.8, 6.8, 5.8; 2026 to 26 Oct 4.3 [computed] | CONFIRMED | HDFC Overnight: 5.90, 6.12, 5.55, 3.24, 3.07, 4.54, 6.56, 6.59, 5.68; 4.15. SBI Overnight: 5.76, 6.19, 5.61, 3.30, 3.11, 4.58, 6.59, 6.60, 5.72; 4.19. Funds trail the index by 0.05–0.21 | [101996](https://api.mfapi.in/mf/101996); [101206](https://api.mfapi.in/mf/101206) | 10 Nov 2026 |
| 11 | "Liquid funds historically earned somewhat more than the overnight rate [recalled]" | CONFIRMED | Liquid funds minus HDFC Overnight: +1.2 points a year over 2008–2016 (8.0% against 6.8%), +0.7 over 2019–2026 (5.7% against 5.0%) | 100868, 103340, 105280, 101996 | 10 Nov 2026 |
| 12 | "A flat 6% for the cash leg is therefore slightly generous for recent years" | CONFIRMED and quantified | Overnight funds 2019 → 10 Nov 2026: 5.03–5.07% a year; liquid ETFs run 0.2–0.35 below overnight funds, so about 4.8% for an ETF. 2011 → 10 Nov 2026: HDFC Overnight 6.13% | 101996, 101206 | 10 Nov 2026 |
| 13 | "the liquid ETF earns 5–5.5% and not 6%" (Strategy 1 range) | PARTLY: lower end | Trailing 1-year 4.7–5.0%; current 7-day 5.0–5.3% | 152327, 152555, 152891 | 10 Nov 2026 |
| 14 | "Overnight and liquid returns for 2008–2016 … Recalled or unavailable" (What could not be confirmed) | GAP FILLED | Full table in section (c) Q1 | 100868, 103340, 105280, 101206, 101996 | 10 Nov 2026 |
| 15 | Gold 2013 "−6.4", 2014 "−9.3" (year table, "Gold explains half the edge") | CORRECTED → NAV −14.1 and +0.8; price figures stand as price returns | GOLDBEES close was 8.9% above NAV on 31 Dec 2013 and 2.1% below on 31 Dec 2014 | 105085, 115744, [140088](https://api.mfapi.in/mf/140088); closes from [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME) | 9 Nov 2026 |
| 16 | Gold other years (2008 24.5, 2009 24.9, 2016 12.5, 2022 12.8, 2023 14.7) | CORRECTED on NAV → 25.6, 22.7, 10.7, 14.0, 12.7 | Year-end close-to-NAV gaps: −1.7% (2008), −1.7% (2015), −1.5% (2022). Remaining 12 gold cells within 1 point | same | 9 Nov 2026 |
| 17 | "Gold compounded at 13.6% a year over 2008–2026 … 9.2% a year in 2008–2018 and 19.9% in 2019–2026" | CONFIRMED | NAV: 13.5%, 9.2%, 19.8% (to 26 Oct 2026 and to 9 Nov 2026 alike); 2011–2026 11.7% | same | 9 Nov 2026 |
| 18 | "2025 alone at +71.8%" (gold) | CONFIRMED | NAV +72.0% | [140088](https://api.mfapi.in/mf/140088) | 9 Nov 2026 |
| 19 | "Gold also spent 6.6 years under water after November 2012" | QUALIFIED | On NAV the peak is 28 Aug 2013 and recovery 5 Aug 2019: 5.9 years. The November 2012 peak is a closing-price peak | 105085, 115744, 140088 | 9 Nov 2026 |
| 20 | NIFTYBEES yearly column (−52.1 … −12.2) | CONFIRMED except 2009 (NAV 74.6 against 75.6) | 18 of 19 cells within 1 point of raw NAV | 101325, 115728, [140084](https://api.mfapi.in/mf/140084) | 9 Nov 2026 |
| 21 | "ETF price returns, which track total return closely for these funds" | CORRECTED for 2008–2015 | Six one-day NAV shortfalls against UTI Nifty 50 Index Fund of 1.14, 1.09, 1.85, 1.25, 1.05 and 0.90% (dates in summary). With them added back: 2009 76.5, 2012 29.4, 2013 8.0, 2014 32.6, 2015 −3.2 | 101325, 115728, 140084, [100822](https://api.mfapi.in/mf/100822) | 9 Nov 2026 |
| 22 | "NIFTYBEES returned −7.41% … over May 2025 to October 2026" | CONFIRMED | NAV 15 May 2025 → 26 Oct 2026: −7.47% | [140084](https://api.mfapi.in/mf/140084) | 26 Oct 2026 |
| 23 | NIFTYBEES 7.9% a year 2008–2026; buy and hold 9.5% for 2011–26; 5.7% (notes) for 2008–18; 11.1% for 2019–26 | CONFIRMED on raw NAV to 26 Oct 2026 (7.9, 9.5, 5.6, 11.1); CORRECTED with distributions added back → 8.3, 9.8, 6.4, 11.1 | To 9 Nov 2026: 8.4, 10.1, 5.6, 12.5 raw | 101325, 115728, 140084 | 9 Nov 2026 |
| 24 | Buy and hold NIFTYBEES worst fall "−36.3%" (2011–26) and "−59.7%" (2008–26) | CORRECTED → −38.4% (14 Jan → 23 Mar 2020) on NAV; −59.9% (8 Jan → 27 Oct 2008) | NIFTYBEES closed 3.45% above NAV on 23 Mar 2020 | same; closes from NSEDATA4ME | 9 Nov 2026 |
| 25 | JUNIORBEES yearly column | CONFIRMED except 2009 (NAV 122.7 against 123.9) and 2012 (48.8 against 47.2) | Year-end close-to-NAV gap −1.2% at end 2012, −0.8% at end 2008 | 101621, 115729, [140085](https://api.mfapi.in/mf/140085) | 9 Nov 2026 |
| 26 | JUNIORBEES 9.6% a year 2008–2026; "124% rebound in 2009" | CONFIRMED | NAV 9.7% to 26 Oct 2026 (10.2% to 9 Nov); 2009 +122.7% | same | 9 Nov 2026 |
| 27 | "Next 50 and midcap index returns before 2012 … Recalled or unavailable" | PARTLY FILLED | ICICI Pru Nifty Next 50 Index Fund Reg-G gives 2011 −30.8, 2012 44.9 as a second series. No midcap fund NAV exists before 2019 | [112957](https://api.mfapi.in/mf/112957) | 9 Nov 2026 |
| 28 | MID150BEES yearly (notes: 25.6, 47.3, 3.7, 44.1, 24.2, 5.7, −6.1) and 18.0% a year from 4 Feb 2019 | CONFIRMED | NAV: 25.3, 47.6, 3.6, 44.3, 24.1, 5.8, −6.2; 17.9% a year 4 Feb 2019 → 26 Oct 2026; worst fall −38.3% | [146271](https://api.mfapi.in/mf/146271) | 9 Nov 2026 |
| 29 | "The Nifty then rose about 10% between 26 October and 9 November … not cross-checked" | CONFIRMED | NIFTYBEES NAV +10.10%; UTI Nifty 50 Direct +10.10%; JUNIORBEES +9.51%; MID150BEES +7.70% | 140084, [120716](https://api.mfapi.in/mf/120716), 140085, 146271 | 9 Nov 2026 |
| 30 | NIFTYBEES 10-for-1 and GOLDBEES 100-for-1 unit splits, ex-date 19 Dec 2019 (Practical traps) | CONFIRMED, with a date nuance | Raw NAV: NIFTYBEES 1,300.3137 (20 Dec 2019) → 129.9356 (23 Dec); GOLDBEES 3,358.6429 → 33.7313. The NAV series changes basis on 23 Dec, two trading days after the exchange ex-date | 140084, 140088 | 9 Nov 2026 |
| 31 | "SILVERBEES then fell 23.2% in a day on 2 February 2026 [computed, not cross-checked]" | CONFIRMED as a real fall | NAV 359.32 (29 Jan) → 315.61 (30 Jan) → 317.06 (1 Feb) → 237.86 (2 Feb): −25.0% on the day, −33.8% over three sessions. Close was 9.2% below NAV on 30 Jan | [149758](https://api.mfapi.in/mf/149758) | 9 Nov 2026 |
| 32 | "silver ETFs traded 5.7% to 15% above fair value in October 2025" [summary] | NOT REPRODUCED for SILVERBEES on a close-to-NAV basis | SILVERBEES close minus same-day NAV peaked at +3.0% (9 Oct 2025) in October 2025; its largest closing premium was +5.4% on 26 Dec 2025. The news figures may refer to other funds, intraday prices or an international fair value | 149758; closes from NSEDATA4ME | 26 Oct 2026 |
| 33 | "A backtest on these prices also overstates returns" (overseas ETFs); "MON100 closed 17% above NAV in mid-June 2026" | CONFIRMED | MON100 2024: NAV +28.6% against +56.8% on price. Closing premium to NAV in the 12 months to 26 Oct 2026: median 12.7%, maximum 27.7% (5 Jun 2026), 5.3% on 26 Oct 2026 | [114984](https://api.mfapi.in/mf/114984) | 26 Oct 2026 |
| 34 | "premium or discount to NAV were not sourced for any of these ETFs" | GAP FILLED (closing basis) | Table in section (c) Q4 | several | 26 Oct 2026 |
| 35 | UTI Nifty200 Momentum 30 Index Fund "launched 10 Mar 2021" | CONSISTENT | First NAV 12 Mar 2021 at 9.9454 (direct) and 9.9450 (regular) | [148703](https://api.mfapi.in/mf/148703); [148704](https://api.mfapi.in/mf/148704) | 9 Nov 2026 |
| 36 | "UTI's fund has compounded at roughly 14.5–14.75% a year in the direct plan and about 13% in the regular plan since March 2021 [undated]" | CORRECTED → direct 14.14%, regular 13.58% (12 Mar 2021 → 9 Nov 2026) | Date-sensitive: direct 15.57% at 30 Jun 2026, 12.56% at 26 Oct 2026, 13.04% at 30 Oct 2026. +114.36% (the notes' Paytm figure) matches a NAV near 21.44, seen in late June to August 2026 | 148703, 148704 | 9 Nov 2026 |
| 37 | Notes: "NAV 19.84 on 30 Oct 2026" described as regular plan; 1.5-point direct/regular gap | CORRECTED | 19.8433 is the **direct** NAV on 30 Oct 2026; regular was 19.3036. Gap between plans is 0.56 points a year | 148703, 148704 | 30 Oct 2026 |
| 38 | UTI regular plan calendar years "−5.95, 40.59, 20.36, −5.78" (Calendar years table) | CONFIRMED within 0.4 points | NAV: −5.95, 40.67, 20.72, −5.54 | [148704](https://api.mfapi.in/mf/148704) | 9 Nov 2026 |
| 39 | UTI **direct** plan calendar years: "not found" (notes) | GAP FILLED | −5.47 (2022), 41.37 (2023), 21.30 (2024), −5.09 (2025); 2026 to 2 Sep −1.07, to 26 Oct −10.19, to 9 Nov −2.39. Trails the total-return index by 0.0–0.5 points a year | [148703](https://api.mfapi.in/mf/148703) | 9 Nov 2026 |
| 40 | "Momentum 30 index fell 31.8% from 27 September 2024 to 7 April 2025 … against about 15–16% for the Nifty 50 over the same dates" | CONFIRMED on funds | UTI direct −31.50%, regular −31.68%, ICICI ETF NAV −31.9%, same peak and trough dates; UTI Nifty 50 Direct −15.10% over those dates | 148703, 148704, [150455](https://api.mfapi.in/mf/150455), 120716 | 9 Nov 2026 |
| 41 | "had not regained its peak by 26 October 2026" | CONFIRMED, still true on 9 Nov 2026 | Direct NAV 26.2739 at peak; highest since is 26.0116 (1 Oct 2024); −26.35% on 26 Oct 2026, −19.96% on 9 Nov 2026 | 148703 | 9 Nov 2026 |
| 42 | "the fund's five-year return to mid-September 2026 was 8.7% a year" (Strategy 2); notes: 1y −3.39, 3y 9.46 | CONFIRMED | Direct, to 15 Sep 2026: 1y −3.39%, 3y 9.47%, 5y 8.73%. To 9 Nov 2026: 1y −3.43%, 3y 9.38%, 5y 7.89% | 148703 | 9 Nov 2026 |
| 43 | "2022–2025 … Momentum 30 11.6%, Nifty 200 13.2%, excess −1.6" (Live results table) | CONFIRMED on funds | UTI direct 11.37% a year over 31 Dec 2021 → 31 Dec 2025 against 13.08% for Motilal Oswal Nifty 500 Index Direct (−1.7) and 11.84% for UTI Nifty 50 Direct (−0.5) | 148703, [147625](https://api.mfapi.in/mf/147625), 120716 | 31 Dec 2025 |
| 44 | "from April 2024 to June 2026 momentum gained 2.1% in total against 14.7% for the Nifty 200" | CONFIRMED on funds | 28 Mar 2024 → 30 Jun 2026: UTI direct +1.42%; Nifty 500 fund +15.46%; Nifty 50 fund +9.44% | 148703, 147625, 120716 | 30 Jun 2026 |
| 45 | Nifty 50 total-return years "25.6, 5.7, 21.3, 10.1, 11.9; 2026 to 2 Sep −7.6" | CONFIRMED | UTI Nifty 50 Direct: 25.30, 5.44, 21.04, 9.80, 11.68; −7.75 (fund trails by 0.15–0.3) | [120716](https://api.mfapi.in/mf/120716) | 9 Nov 2026 |
| 46 | Like-for-like fund comparison since UTI launch: "No like-for-like figure" (notes) | GAP FILLED | 12 Mar 2021 → 9 Nov 2026: momentum direct 14.14%, Nifty 500 fund 12.46% (+1.7), Nifty 50 fund 10.50% (+3.6). To 26 Oct 2026: 12.56, 10.82, 8.70 | 148703, 147625, 120716 | 9 Nov 2026 |
| 47 | Nifty Midcap150 Momentum 50 "52.5%, 32.3% and −3.5% in 2023, 2024 and 2025"; worst fall −25.6%; "−0.2" against Midcap 150 since Aug 2022 | Index figures not testable; FUND TRAILS | Tata index fund direct: 49.8, 30.9, −4.2 (2.7, 1.4, 0.7 below the index); worst fall −25.9% (24 Sep 2024 → 13 Mar 2025), 9.1% below peak on 9 Nov 2026; 15.72% a year since 31 Oct 2022 against 17.57% for MID150BEES NAV (−1.9) | [150738](https://api.mfapi.in/mf/150738); 146271 | 9 Nov 2026 |
| 48 | "Only Alpha 50 and Value 50 have kept a large live edge" (factor table: Alpha 50 +7.3 since Nov 2012) | QUALIFIED: not true of the investable fund over its own life | Kotak Nifty Alpha 50 ETF NAV, 29 Dec 2021 → 9 Nov 2026: 8.31% a year against 9.06% (Nifty 50 fund) and 10.73% (Nifty 500 fund). Calendar years −16.6, 41.8, 32.4, −10.8 against the index's −13.5, 43.6, 33.9, −10.2 | [149397](https://api.mfapi.in/mf/149397) | 9 Nov 2026 |
| 49 | Alpha Low-Vol 30 years "30.9, −3.1, 39.0, 17.8, 0.3" | CONFIRMED (fund 0.5–0.8 lower) | ICICI ETF NAV: 30.2, −3.6, 38.2, 17.0, −0.3 | [148456](https://api.mfapi.in/mf/148456) | 9 Nov 2026 |
| 50 | Low Vol 30 years "24.2, 2.0, 31.9, 12.4, 11.5"; worst fall −31.0% | CONFIRMED (fund 0.5–0.7 lower) | ICICI ETF NAV: 23.6, 1.5, 31.2, 11.8, 10.9; worst fall −30.5% (17 Jan → 23 Mar 2020) | [141596](https://api.mfapi.in/mf/141596) | 9 Nov 2026 |
| 51 | Quality 30 years "26.2, −4.4, 31.7, 14.4, 4.7"; worst fall −29.5%; excess −1.4 | CONFIRMED (fund 0.4–0.8 lower) | SBI ETF NAV: 25.5, −5.0, 30.9, 13.7, 4.3; worst fall −29.1%; 10.95% a year since 14 Dec 2018 against 12.27% for the Nifty 50 fund (−1.3) | [145648](https://api.mfapi.in/mf/145648) | 9 Nov 2026 |
| 52 | MOM30IETF "Tracking difference −0.63% since inception" | CONSISTENT | ETF NAV years 40.8, 20.6, −5.1 against index 41.7, 21.3, −4.6: 0.5–0.9 below | [150455](https://api.mfapi.in/mf/150455) | 9 Nov 2026 |
| 53 | "The issuers shown for LOWVOLIETF and ALPL30IETF come from the brief and were not re-verified" | CONFIRMED | Both ICICI Prudential (ISINs INF109KC19U5 and INF109KC17V7 match scheme names and NSE symbols) | 141596, 148456; Dhan scrip master copy | 10 Nov 2026 |
| 54 | First-trade dates: MID150BEES 4 Feb 2019, GOLDBEES 19 Mar 2007, SILVERBEES 7 Feb 2022, MON100 31 Mar 2011, MOM30IETF 10 Aug 2022, ALPL30IETF 18 Aug 2020, LIQUIDCASE 24 Jan 2024, LIQUIDADD 3 Apr 2024, GROWWLIQID 26 Sep 2024 | CONSISTENT | First NAVs fall 1–7 days earlier in each of these nine cases (table in section (c) Q4) | several | 10 Nov 2026 |
| 55 | "Launch dates before 2005" (NIFTYBEES December 2001, JUNIORBEES February 2003, LIQUIDBEES July 2003) | STILL UNCONFIRMED | mfapi history starts 19 Jun 2006 for Nifty BeES and Junior BeES and 6 Nov 2016 for the current Liquid BeES code; older Liquid BeES codes not fetched | 101325, 101621, 140086 | 10 Nov 2026 |
| 56 | LOWVOLIETF first trade 11 Jul 2017 | STILL UNCONFIRMED from NAV | mfapi NAV history for the scheme starts 3 Jul 2018, a year after the first exchange trade | [141596](https://api.mfapi.in/mf/141596) | 10 Nov 2026 |
| 57 | "LIQUIDBEES's … 5-year return of 4.81% a year to July 2026" | STILL UNCONFIRMED | NAV is 1,000.0000 on every date, so NAV history cannot give a return | [140086](https://api.mfapi.in/mf/140086) | 10 Nov 2026 |

## (c) New tables

### Q1. Liquid and overnight returns by calendar year

#### Takeaway
Liquid funds returned about 7.0% a year over 2011–2026 and 5.7% over 2019–2026; a true overnight fund returned 6.1% and 5.0%. The three growth liquid ETFs have earned 0.2–0.35 points less than regular-plan overnight funds since launch, and their trailing 1-year return is now 4.7–5.0%.

#### Cited findings

**Series used**

| Series | Scheme code | First NAV in mfapi | Last NAV | Unit change found in raw NAV (back-adjusted) |
|---|---|---|---|---|
| HDFC Liquid Fund, Regular, Growth | [100868](https://api.mfapi.in/mf/100868) | 2 Apr 2006 | 10 Nov 2026 (5,564.2280) | ×100 between 28 and 30 Aug 2015 |
| ICICI Prudential Liquid Fund, Regular, Growth | [103340](https://api.mfapi.in/mf/103340) | 2 Apr 2006 | 10 Nov 2026 (419.7031) | ×10 between 30 Oct and 2 Nov 2009 |
| SBI Liquid Fund, Regular, Growth | [105280](https://api.mfapi.in/mf/105280) | 26 Mar 2007 (two gaps in mid-2007; 65 zero-NAV rows dropped) | 10 Nov 2026 (4,431.9836) | ×100 between 12 and 13 Jan 2012 |
| SBI Overnight Fund, Regular, Growth | [101206](https://api.mfapi.in/mf/101206) | 1 Apr 2006 | 10 Nov 2026 (4,457.0990) | ×100 between 12 and 13 Jan 2012 |
| HDFC Overnight Fund, Regular, Growth | [101996](https://api.mfapi.in/mf/101996) | 2 Apr 2006 | 10 Nov 2026 (4,074.9827) | ×100 between 28 and 30 Aug 2015 |
| Zerodha CASE Nifty 1D Rate Liquid ETF, Growth (LIQUIDCASE, ISIN INF0R8F01034) | [152327](https://api.mfapi.in/mf/152327) | **23 Jan 2024** (100.1995) | 10 Nov 2026 (116.8306) | none |
| DSP BSE Liquid Rate ETF (LIQUIDADD, ISIN INF740KA1UM0) | [152555](https://api.mfapi.in/mf/152555) | **27 Mar 2024** (1,001.2681) | 10 Nov 2026 (1,153.6655) | none |
| Groww Nifty 1D Rate Liquid ETF (GROWWLIQID, ISIN INF666M01IP5) | [152891](https://api.mfapi.in/mf/152891) | **25 Sep 2024** (100.0974) | 10 Nov 2026 (111.5775) | none |

All five open-ended funds are regular plans; direct plans (from 2013) would be roughly 0.1 point higher.

**Calendar-year returns, % [own computation]** — sources: the scheme codes above

| Year | HDFC Liquid | ICICI Pru Liquid | SBI Liquid | SBI Overnight | HDFC Overnight | LIQUIDCASE | LIQUIDADD | GROWWLIQID | Report's overnight figure |
|---|---|---|---|---|---|---|---|---|---|
| 2008 | 8.90 | 9.32 | 8.74 | 8.72 | 7.54 | — | — | — | about 7–8 [recalled] |
| 2009 | 5.29 | 5.56 | 4.85 | 5.22 | 3.34 | — | — | — | about 3.3 [recalled] |
| 2010 | 5.15 | 5.50 | 5.48 | 5.65 | 4.73 | — | — | — | about 5 [recalled] |
| 2011 | 8.80 | 8.95 | 8.97 | 8.90 | 7.46 | — | — | — | about 7.8 [recalled] |
| 2012 | 9.56 | 9.70 | 9.63 | 9.30 | 8.24 | — | — | — | about 8.2 [recalled] |
| 2013 | 9.28 | 9.28 | 9.22 | 8.87 | 8.21 | — | — | — | about 8.3 [recalled] |
| 2014 | 9.10 | 9.12 | 9.04 | 8.74 | 8.16 | — | — | — | about 8.2 [recalled] |
| 2015 | 8.35 | 8.33 | 8.28 | 7.78 | 7.29 | — | — | — | about 7.2 [recalled] |
| 2016 | 7.59 | 7.66 | 7.59 | 6.78 | 6.41 | — | — | — | about 6.4 [recalled] |
| 2017 | 6.53 | 6.64 | 6.55 | 5.76 | 5.90 | — | — | — | 6.0 (index) |
| 2018 | 7.23 | 7.40 | 7.31 | 6.19 | 6.12 | — | — | — | 6.2 |
| 2019 | 6.52 | 6.60 | 6.51 | 5.61 | 5.55 | — | — | — | 5.8 |
| 2020 | 4.11 | 4.27 | 4.18 | 3.30 | 3.24 | — | — | — | 3.4 |
| 2021 | 3.21 | 3.23 | 3.27 | 3.11 | 3.07 | — | — | — | 3.3 |
| 2022 | 4.75 | 4.74 | 4.75 | 4.58 | 4.54 | — | — | — | 4.7 |
| 2023 | 6.97 | 7.00 | 6.96 | 6.59 | 6.56 | — | — | — | 6.8 |
| 2024 | 7.33 | 7.36 | 7.26 | 6.60 | 6.59 | 6.00 from 23 Jan (6.39 annualised) | 4.80 from 27 Mar (6.28 annualised) | 1.69 from 25 Sep (6.36 annualised) | 6.8 |
| 2025 | 6.50 | 6.48 | 6.43 | 5.72 | 5.68 | 5.52 | 5.49 | 5.37 | 5.8 |
| 2026 to 26 Oct | 5.21 | 5.19 | 5.23 | 4.19 | 4.15 | 4.02 | 4.00 | 3.81 | 4.3 |
| 2026 to 10 Nov | 5.54 | 5.52 | 5.55 | 4.42 | 4.39 | 4.24 | 4.22 | 4.03 | — |
| 2026 to 10 Nov, annualised | 6.48 | 6.45 | 6.49 | 5.16 | 5.12 | 4.95 | 4.93 | 4.70 | — |

**Period averages, % a year (compound, 31 Dec start → end date) [own computation]**

| Period | HDFC Liquid | ICICI Pru Liquid | SBI Liquid | SBI Overnight | HDFC Overnight |
|---|---|---|---|---|---|
| 2008–2016 (to 31 Dec 2016) | 7.99 | 8.15 | 7.96 | 7.76 | 6.81 |
| 2008–2026 (to 10 Nov 2026) | 6.92 | 7.02 | 6.91 | 6.45 | 5.98 |
| **2011–2026** (to 10 Nov 2026) | **7.01** | **7.07** | **7.02** | 6.43 | **6.13** |
| 2017–2026 | 5.95 | 6.00 | 5.96 | 5.26 | 5.23 |
| **2019–2026** | **5.71** | **5.74** | **5.71** | **5.07** | **5.03** |
| 2021–2026 | 5.85 | 5.85 | 5.84 | 5.29 | 5.26 |
| 2024–2026 | 6.78 | 6.77 | 6.74 | 5.86 | 5.82 |

Ending on 26 Oct 2026 instead of 10 Nov 2026 changes no figure by more than 0.02. Over 31 Dec 2007 → 31 Dec 2018 the same calculation gives HDFC Overnight 6.66%, SBI Overnight 7.44% and HDFC Liquid 7.79% a year.

**Liquid ETFs since first NAV, and trailing returns as of 10 Nov 2026 [own computation]** (annualised simply: return × 365 ÷ days; the 365-day figure is the plain return)

| ETF | Since first NAV → 10 Nov 2026 | SBI / HDFC Overnight, same dates | HDFC Liquid, same dates | 7-day | 30-day | 91-day | 365-day |
|---|---|---|---|---|---|---|---|
| LIQUIDCASE (152327) | 5.64% | 5.84% / 5.80% | 6.76% | 5.20% | 5.33% | 4.92% | 4.96% |
| LIQUIDADD (152555) | 5.55% | 5.78% / 5.74% | 6.72% | 5.27% | 5.31% | 4.90% | 4.94% |
| GROWWLIQID (152891) | 5.24% | 5.60% / 5.55% | 6.57% | 5.00% | 5.07% | 4.68% | 4.73% |
| SBI Overnight (101206), for scale | — | — | — | 5.52% | 5.55% | 5.14% | 5.18% |
| HDFC Liquid (100868), for scale | — | — | — | 8.11% | 5.51% | 5.94% | 6.41% |

**NAV dips in the long series.** Liquid funds had one-day NAV falls larger than 0.02% on 16 Jul 2013 (−0.16 to −0.17%), 24 Jul 2013, 19–24 Mar 2020 (three days of −0.05 to −0.08%), 4 May 2022 and 28 Mar 2023 (−0.02 to −0.03%); HDFC Liquid has 28 down days of any size since December 2007. HDFC Overnight has no down day at all since December 2007; SBI Overnight has six, two of them larger than 0.02% (15 Apr 2008 −0.07%, 16 Jul 2013 −0.11%). — [100868](https://api.mfapi.in/mf/100868), [101996](https://api.mfapi.in/mf/101996), [101206](https://api.mfapi.in/mf/101206)

#### Inferences
- **Against the flat 6%.** A growth liquid ETF would have earned roughly an overnight fund's return less 0.2–0.35 points. That gives about 5.8–5.9% a year for 2011–2026 (flat 6% is right to within 0.2), about 4.7–4.85% for 2019–2026 (flat 6% is about 1.1–1.3 too high), and about 6.3–6.5% for 2008–2018 (flat 6% is about 0.3–0.5 too low; HDFC Overnight's 6.66% a year less the ETF gap). The report's sub-period comparison therefore flatters cash-heavy rules in 2019–2026 and slightly handicaps them in 2008–2018.
- **Against the recalled 2008–2016 figures.** All nine recalled overnight figures are within 0.35 points of HDFC Overnight's NAV return. The notes' recalled liquid-fund column (8.4, 4.9, 5.1, 8.2, 8.5, 9.0, 9.2, 8.2, 7.5) is within about 0.6 points of HDFC Liquid except 2012 (9.56 against 8.5).
- **SBI Overnight is not a clean overnight series before 2018–19.** Its 2008–2016 returns (7.8% a year) sit close to the liquid funds and 1 point above HDFC Overnight; from 2019 the two overnight funds agree within 0.06 points a year. The likely reason is that the scheme ran under an earlier, wider mandate before SEBI's 2018 recategorisation [recalled: formerly a "liquid floater" plan; HDFC's was a "call" plan]. Use HDFC Overnight (101996) as the pre-2019 overnight proxy.
- The 8.1% 7-day figure for HDFC Liquid (and 8.0–8.1% for ICICI and SBI) in early November 2026 is far above the 30-day figure; daily accruals ran at 6–12% annualised from 27 Oct to 9 Nov 2026. That looks like mark-to-market gains on short paper, but no source was checked for the cause.

#### Gaps
- LIQUIDBEES cannot be measured from NAV (pinned at ₹1,000.0000).
- Direct-plan liquid and overnight funds, and the liquid ETFs of Kotak, HDFC, Mirae, Bajaj, Nippon (growth), SBI and UTI, were not fetched.
- The earlier names and mandates of the two overnight funds are recollection, not sourced.

### Q2. Gold, Nifty 50, Next 50 and Midcap 150 by calendar year, from NAVs

#### Takeaway
On NAV, the report's equity ETF columns hold within 1 point in all but three cells, but gold differs by 7.7 and 10.1 points in 2013 and 2014 because GOLDBEES traded about 9% above NAV at the end of 2013. NIFTYBEES returns before 2016 are understated by about 1–2 points in six years unless distributions are added back.

#### Cited findings

**What the raw NAVs show around the December 2019 unit splits** — [140084](https://api.mfapi.in/mf/140084), [140088](https://api.mfapi.in/mf/140088), [140085](https://api.mfapi.in/mf/140085)

| NAV date | NIFTYBEES | GOLDBEES | JUNIORBEES |
|---|---|---|---|
| 18 Dec 2019 | 1,294.9366 | 3,361.4836 | 291.9998 |
| 19 Dec 2019 | 1,299.0255 | 3,353.2295 | 293.1111 |
| 20 Dec 2019 | 1,300.3137 | 3,358.6429 | 294.7800 |
| 23 Dec 2019 | **129.9356** (ratio 0.0999) | **33.7313** (ratio 0.0100) | 294.6746 |

The 10-for-1 and 100-for-1 changes are both in the raw NAV and are not adjusted by mfapi. The NAV changes basis between 20 and 23 Dec 2019, after the exchange ex-date of 19 Dec, so raw price and raw NAV disagree by 10× or 100× on 19 and 20 Dec. After back-adjustment the NAV and the NSEDATA4ME adjusted closes agree within 0.3% on every day from 17 to 23 Dec 2019. JUNIORBEES has no unit change in its history.

**Other unit changes found in raw NAVs:** ICICI Pru Nifty 100 Low Vol 30 ETF 196.3630 → 19.7146 (1 → 4 Mar 2024); ICICI Pru Nifty Alpha Low-Vol 30 ETF 269.3560 → 27.1022 (10 → 13 May 2024); ICICI Pru Nifty 200 Momentum 30 ETF 186.1575 → 18.8604 (10 → 12 Aug 2022, in its first week); Motilal Oswal Nasdaq 100 ETF 1,025.4998 → 101.5224 (18 → 21 Jun 2021). — [141596](https://api.mfapi.in/mf/141596), [148456](https://api.mfapi.in/mf/148456), [150455](https://api.mfapi.in/mf/150455), [114984](https://api.mfapi.in/mf/114984)

**Scheme-code history.** GOLDBEES: 105085 (16 Mar 2007 → 18 Aug 2011), 115744 (22 Aug 2011 → 3 Nov 2016), 140088 (7 Nov 2016 → 9 Nov 2026). NIFTYBEES: 101325 (19 Jun 2006 → 18 Aug 2011), 115728, 140084. JUNIORBEES: 101621 (19 Jun 2006 → 18 Aug 2011), 115729, 140085. MID150BEES: 146271 (1 Feb 2019 → 9 Nov 2026). Cross-check funds: UTI Nifty 50 Index Fund Regular Growth 100822 (from 3 Apr 2006), ICICI Prudential Nifty Next 50 Index Fund Regular Growth 112957 (from 29 Jun 2010).

**Days on which NIFTYBEES NAV fell against UTI Nifty 50 Index Fund by more than 0.4% with no reversal [own computation]** — 101325, 115728, [100822](https://api.mfapi.in/mf/100822)

| Date | NIFTYBEES NAV change | UTI fund change | Shortfall | Implied amount per pre-split unit |
|---|---|---|---|---|
| 15 Sep 2008 | −4.78% | −3.69% | 1.14% | about ₹4.9 |
| 9 Jul 2009 | −1.03% | +0.07% | 1.09% | about ₹4.5 |
| 12 Mar 2012 | −1.35% | +0.51% | 1.85% | about ₹10.1 |
| 14 Mar 2013 | −0.28% | +0.98% | 1.25% | about ₹7.4 |
| 11 Mar 2014 | −1.43% | −0.38% | 1.05% | about ₹7.0 |
| 20 Feb 2015 | −1.58% | −0.69% | 0.90% | about ₹8.1 |

JUNIORBEES shows one such day against the ICICI Next 50 fund: 11 Mar 2014 (−1.64% against −0.86%, shortfall 0.78%, about ₹1.0 a unit). None after 2015 in either ETF. A further NIFTYBEES shortfall of 1.94% on 8 Jan 2007 is outside the window.

**Calendar-year returns from NAV, % [own computation]**

| Year | GOLDBEES | NIFTYBEES, raw NAV | NIFTYBEES, shortfalls added back | UTI Nifty 50 Index Reg-G | JUNIORBEES, raw NAV | ICICI Pru Next 50 Index Reg-G | MID150BEES |
|---|---|---|---|---|---|---|---|
| 2008 | 25.6 | −51.9 | −51.3 | −52.0 | −63.3 | — | — |
| 2009 | 22.7 | 74.6 | 76.5 | 73.8 | 122.7 | — | — |
| 2010 | 21.7 | 18.8 | 18.8 | 17.7 | 17.8 | — | — |
| 2011 | 30.3 | −23.9 | −23.9 | −24.8 | −31.6 | −30.8 | — |
| 2012 | 10.9 | 27.0 | 29.4 | 28.3 | 48.8 | 44.9 | — |
| 2013 | −14.1 | 6.6 | 8.0 | 6.9 | 5.1 | 5.4 | — |
| 2014 | 0.8 | 31.2 | 32.6 | 31.8 | 43.5 (44.7 with the March 2014 shortfall added back) | 43.6 | — |
| 2015 | −7.8 | −4.1 | −3.2 | −3.3 | 7.1 | 6.2 | — |
| 2016 | 10.7 | 3.9 | 3.9 | 4.0 | 7.2 | 7.6 | — |
| 2017 | 2.9 | 30.0 | 30.0 | 29.7 | 46.3 | 45.7 | — |
| 2018 | 6.9 | 4.6 | 4.6 | 4.3 | −8.0 | −8.8 | — |
| 2019 | 22.9 | 13.5 | 13.5 | 13.2 | 1.3 | 0.6 | part year from 1 Feb |
| 2020 | 26.2 | 15.8 | 15.8 | 15.5 | 15.5 | 14.3 | 25.3 |
| 2021 | −4.8 | 25.5 | 25.5 | 25.2 | 30.5 | 29.5 | 47.6 |
| 2022 | 14.0 | 5.6 | 5.6 | 5.3 | 0.7 | 0.1 | 3.6 |
| 2023 | 12.7 | 21.3 | 21.3 | 20.9 | 27.1 | 26.3 | 44.3 |
| 2024 | 19.4 | 10.0 | 10.0 | 9.6 | 28.1 | 27.2 | 24.1 |
| 2025 | 72.0 | 11.8 | 11.8 | 11.6 | 2.8 | 2.1 | 5.8 |
| 2026 to 26 Oct | 5.7 | −12.1 | −12.1 | −12.3 | −3.4 | −4.0 | −6.2 |
| 2026 to 9 Nov | 6.1 | −3.2 | −3.2 | −3.4 | 5.7 | 5.0 | 1.1 |

Also from NAV: SILVERBEES (149758) +2.7% (2023), +16.4% (2024), +160.5% (2025), −15.4% (2026 to 26 Oct), −19.0% (to 9 Nov); the notes' price figures were +7.4, +16.0, +157.3 and −14.4. MON100 (114984) NAV +17.4% (2012), −25.8% (2022), +28.6% (2024), +26.0% (2025), +23.0% (2026 to 26 Oct); the notes' price figure for 2024 was +56.8%.

**CAGR and maximum drawdown from daily NAV [own computation]** (drawdown dates are peak → trough)

| Period | Series | CAGR to 9 Nov 2026 | CAGR to 26 Oct 2026 | Report / notes CAGR (to 26 Oct, price) | Max drawdown on NAV | Report / notes drawdown (price) |
|---|---|---|---|---|---|---|
| 2008–2026 | GOLDBEES | 13.5% | 13.5% | 13.6% | −29.5% (28 Aug 2013 → 31 Jul 2015) | −27.1% (27 Nov 2012 → 6 Aug 2015) |
| | NIFTYBEES raw | 8.4% | 7.9% | 7.9% | −59.9% (8 Jan → 27 Oct 2008) | −59.7% |
| | NIFTYBEES, shortfalls added back | 8.9% | 8.3% | — | −59.5% | — |
| | UTI Nifty 50 Index Reg-G | 8.3% | 7.7% | — | −59.7% | — |
| | JUNIORBEES raw | 10.2% | 9.7% | 9.6% | −72.2% (4 Jan 2008 → 9 Mar 2009) | −72.3% |
| 2011–2026 | GOLDBEES | 11.7% | 11.7% | 11.7% | −29.5% | −27.1% |
| | NIFTYBEES raw | 10.1% | 9.5% | 9.5% | **−38.4%** (14 Jan → 23 Mar 2020) | −36.3% (17 Jan → 23 Mar 2020) |
| | NIFTYBEES, shortfalls added back | 10.5% | 9.8% | — | −38.4% | — |
| | JUNIORBEES raw | 12.5% | 11.9% | 11.9% | **−40.5%** (8 Jan 2018 → 23 Mar 2020) | −38.7% (8 Jan 2018 → 24 Mar 2020) |
| | ICICI Pru Next 50 Index Reg-G | 11.9% | 11.3% | — | −41.6% | — |
| 2008–2018 (to 31 Dec 2018) | GOLDBEES | 9.2% | 9.2% | 9.2% | −29.5% | −27.1% |
| | NIFTYBEES raw | 5.6% | 5.6% | 5.7% | −59.9% | −59.7% |
| | NIFTYBEES, shortfalls added back | **6.4%** | 6.4% | — | −59.5% | — |
| | JUNIORBEES raw | 7.8% | 7.8% | 7.8% | −72.2% | −72.3% |
| 2019–2026 | GOLDBEES | 19.8% | 19.8% | 19.9% | −22.3% (29 Jan → 23 Mar 2026) | −24.4% (same dates) |
| | NIFTYBEES raw | 12.5% | 11.1% | 11.1% | −38.4% | −36.3% |
| | JUNIORBEES raw | 13.6% | 12.3% | 12.3% | −36.2% (24 Jan → 23 Mar 2020) | −34.5% (24 Jan → 24 Mar 2020) |
| From 1 Feb 2019 | MID150BEES | 18.8% | 17.8% (17.9% from 4 Feb 2019) | 18.0% from 4 Feb 2019 | −38.3% (7 Feb → 23 Mar 2020) | −38.4% |

**Cells that differ by more than 1 point from the table in `computed_rotation_backtests.md` (NAV minus exchange close) [own computation]**

| Series | Year | NAV | Notes (close) | Difference | Close-to-NAV gap at the relevant year-ends |
|---|---|---|---|---|---|
| GOLDBEES | 2008 | 25.6 | 24.5 | +1.1 | −0.8% end 2007, −1.7% end 2008 |
| GOLDBEES | 2009 | 22.7 | 24.9 | −2.2 | −1.7% end 2008, 0.0% end 2009 |
| GOLDBEES | 2013 | −14.1 | −6.4 | **−7.7** | 0.0% end 2012, **+8.9% end 2013** |
| GOLDBEES | 2014 | 0.8 | −9.3 | **+10.1** | +8.9% end 2013, −2.1% end 2014 |
| GOLDBEES | 2016 | 10.7 | 12.5 | −1.8 | −1.7% end 2015, −0.1% end 2016 |
| GOLDBEES | 2022 | 14.0 | 12.8 | +1.2 | −0.5% end 2021, −1.5% end 2022 |
| GOLDBEES | 2023 | 12.7 | 14.7 | −2.0 | −1.5% end 2022, +0.2% end 2023 |
| NIFTYBEES (raw NAV) | 2009 | 74.6 | 75.6 | −1.0 | −0.6% end 2008, 0.0% end 2009 |
| JUNIORBEES (raw NAV) | 2009 | 122.7 | 123.9 | −1.2 | −0.8% end 2008, −0.2% end 2009 |
| JUNIORBEES (raw NAV) | 2012 | 48.8 | 47.2 | +1.6 | −0.2% end 2011, −1.2% end 2012 |
| NIFTYBEES (shortfalls added back) | 2012 | 29.4 | 26.5 | +2.9 | distribution-like fall on 12 Mar 2012 |
| NIFTYBEES (shortfalls added back) | 2014 | 32.6 | 31.6 | +1.0 | 11 Mar 2014 |
| NIFTYBEES (shortfalls added back) | 2015 | −3.2 | −4.3 | +1.1 | 20 Feb 2015 |

Every other cell compared is within 1.0 point: 12 of 19 for GOLDBEES, 18 of 19 for raw NIFTYBEES, 17 of 19 for raw JUNIORBEES, 7 of 7 for MID150BEES, 2 of 2 for LIQUIDCASE (5.52 against 5.5; 4.02 against 4.0), and all ten Nifty 1D Rate rows against overnight funds (within 0.21). The report's "Midcap 100 ETF (MOM100)" column tracks a different index and has no NAV counterpart here.

GOLDBEES monthly median close-to-NAV premium: +5.9% (Oct 2013), +8.0% (Nov), +10.6% (Dec), +7.8% (Jan 2014), +4.8% (Feb), +2.3% (Mar), +4.3% (Apr), +5.7% (May), then −0.1% in June 2014; highest single close +12.6% on 4 Dec 2013. — NAV 105085, 115744, 140088; closes from [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME)

#### Inferences
- The gold table in the report should be labelled "exchange closing price". Either basis is defensible, and for a rule that trades on the exchange the price basis is the right one, but the 2013–14 premium means the backtest's gold signal and gold returns in those months reflect an Indian import-curb premium that NAV did not carry (the cause is recollection, not sourced here).
- The six NIFTYBEES one-day shortfalls have near-round rupee sizes (about ₹10, ₹7.4, ₹7, ₹8 per old unit in 2012–2015), which fits cash distributions. Exchange prices fall on such days as well and the price data are not dividend-adjusted, so every NIFTYBEES buy-and-hold and "in the market" figure in the report for 2008–2015 is understated by the same amount. The effect on the rotation-versus-buy-and-hold comparison is small (0.3 points a year over 2011–2026, 0.8 over 2008–2018) and works in favour of buy-and-hold.
- Closing-price drawdowns understate real falls on panic days. On 23 Mar 2020 closes stood above NAV by 3.45% (NIFTYBEES), 3.79% (JUNIORBEES), 1.48% (MID150BEES), 10.2% (LOWVOLIETF) and 9.3% (SBIETFQLTY).
- Ending the tables on 26 Oct 2026 caught a local low. Thirteen days later NIFTYBEES's since-2019 CAGR is 1.4 points higher.

#### Gaps
- No Midcap 150 fund or ETF NAV exists before 1 Feb 2019; the pre-2019 midcap leg stays unverified.
- Next 50 before June 2010 rests on JUNIORBEES alone; any distribution it paid before then cannot be detected without a second series.
- The NIFTYBEES and JUNIORBEES distributions are inferred from NAV behaviour against a reference fund that itself had tracking error of up to 1 point a year before 2012; amounts and dates are not confirmed from AMC notices.
- UTI Nifty 50 Index Fund is a regular plan with a higher expense ratio, so its yearly figures are not a clean total-return benchmark.

### Q3. Momentum and factor funds from NAV history

#### Takeaway
UTI's momentum fund has returned 14.1% a year in the direct plan since its first NAV on 12 Mar 2021, 3.6 points ahead of a Nifty 50 index fund and 1.7 ahead of a Nifty 500 index fund over identical dates, but it fell 31.5% in 2024–25 and is still 20% below its peak. Every factor fund checked is below its September 2024 peak, and the Alpha 50 and midcap-momentum funds trail their indices by 1–3 points a year.

#### Cited findings

**UTI Nifty200 Momentum 30 Index Fund [own computation]** — direct [148703](https://api.mfapi.in/mf/148703), regular [148704](https://api.mfapi.in/mf/148704); comparators UTI Nifty 50 Index Fund Direct Growth [120716](https://api.mfapi.in/mf/120716) and Motilal Oswal Nifty 500 Index Fund Direct Growth [147625](https://api.mfapi.in/mf/147625). No Nifty 200 index fund with enough history exists in the scheme list (Groww Nifty 200 ETF, 153329, was not fetched and its scheme code places it in 2025), so Nifty 500 stands in.

| Measure | Direct | Regular | UTI Nifty 50 Direct | Nifty 500 Index Direct | Report says |
|---|---|---|---|---|---|
| First NAV | 12 Mar 2021, 9.9454 | 12 Mar 2021, 9.9450 | — | — | launched 10 Mar 2021 |
| Latest NAV | 9 Nov 2026, 21.0307 | 9 Nov 2026, 20.4561 | 176.4383 | 27.5784 | — |
| CAGR, first NAV → 9 Nov 2026 | **14.14%** | **13.58%** | 10.50% | 12.46% | 14.5–14.75% direct, about 13% regular (undated) |
| CAGR from ₹10 on 10 Mar 2021 → 9 Nov 2026 | 14.02% | 13.46% | — | — | — |
| CAGR, first NAV → 26 Oct 2026 | 12.56% | 12.02% | 8.70% | 10.82% | — |
| CAGR, first NAV → 30 Jun 2026 | 15.57% | 15.00% | 10.18% | 12.77% | index 15.9% from 1 Apr 2021 |
| 2021 from first NAV | +40.81% | +40.24% | — | — | part year |
| 2022 | −5.47% | −5.95% | 5.44% | 3.79% | −5.95 (regular); index −5.5 |
| 2023 | 41.37% | 40.67% | 21.04% | 26.54% | 40.59; index 41.7 |
| 2024 | 21.30% | 20.72% | 9.80% | 15.64% | 20.36; index 21.3 |
| 2025 | −5.09% | −5.54% | 11.68% | 7.67% | −5.78; index −4.6 |
| 2026 to 2 Sep | −1.07% | −1.38% | −7.75% | −2.04% | index −0.8; Nifty 50 −7.6 |
| 2026 to 26 Oct | −10.19% | −10.54% | — | — | index (price) −10.5 |
| 2026 to 9 Nov | −2.39% | −2.78% | −3.35% | −0.51% | — |
| 2022–2025 compound | 11.37% | — | 11.84% | 13.08% | index 11.6 against Nifty 200 13.2 |
| Peak NAV | 27 Sep 2024, 26.2739 | 27 Sep 2024, 25.8148 | 26 Sep 2024 | 26 Sep 2024 | 27 Sep 2024 |
| Trough | 7 Apr 2025, 17.9980 | 7 Apr 2025, 17.6373 | 4 Mar 2025 | 28 Feb 2025 | 7 Apr 2025 |
| Depth | **−31.50%** | −31.68% | −15.51% | −18.62% | −31.8% (index) |
| Same dates, 27 Sep 2024 → 7 Apr 2025 | −31.50% | −31.68% | −15.10% | −17.64% | Nifty 50 about 15–16% |
| Against peak on 26 Oct 2026 | −26.35% | −27.08% | −11.49% | — | not regained |
| Against peak on 9 Nov 2026 | **−19.96%** | −20.76% | −2.55% | −2.07% | — |
| Recovered? | No (highest since: 26.0116 on 1 Oct 2024) | No | Yes, 27 Oct 2025, then fell again | No | No |
| Trailing to 15 Sep 2026: 1y / 3y / 5y | −3.39 / 9.47 / 8.73 | −3.84 / 8.95 / 8.20 | −6.95 / 5.61 / 6.72 | −2.40 / 9.12 / 9.16 | −3.39 / 9.46 / 8.72 |
| Trailing to 9 Nov 2026: 1y / 3y / 5y | −3.43 / 9.38 / 7.89 | −3.88 / 8.86 / 7.36 | −0.93 / 9.90 / 7.79 | 0.98 / 11.80 / 9.45 | — |

**Other factor funds [own computation]** — CAGR from each fund's first NAV in mfapi to 9 Nov 2026, against UTI Nifty 50 Index Fund Direct (120716) over identical dates; "2024 peak" is the highest NAV between June and December 2024.

| Index tracked | Fund (scheme code, NSE symbol where listed) | First NAV | Fund CAGR | Nifty 50 fund, same dates | Excess | 2024 peak → trough | Depth | Against peak on 9 Nov 2026 | Worst fall since first NAV | Report's figure for the index |
|---|---|---|---|---|---|---|---|---|---|---|
| Nifty200 Momentum 30 | ICICI Pru ETF ([150455](https://api.mfapi.in/mf/150455), MOM30IETF) | 5 Aug 2022 | 13.00% | 9.91% | +3.1 | 27 Sep 2024 → 7 Apr 2025 | −31.9% | −20.5%, not recovered | −31.9% | −31.8% |
| Nifty Midcap150 Momentum 50 | Tata Index Fund Direct ([150738](https://api.mfapi.in/mf/150738)) | 31 Oct 2022 | 15.72% | 9.52% | +6.2 (but −1.9 against MID150BEES NAV, 17.57%) | 24 Sep 2024 → 13 Mar 2025 | −25.9% | −9.1%, not recovered | −25.9% | worst fall −25.6%; −0.2 against Midcap 150 |
| Nifty500 Momentum 50 | Motilal Oswal Index Fund Direct ([152875](https://api.mfapi.in/mf/152875)) | 30 Sep 2024 | −8.20% | −0.48% | −7.7 | 15 Oct 2024 → 7 Apr 2025 | −31.6% | −17.2%, not recovered | −31.6% | not in report |
| Nifty Alpha 50 | Kotak ETF ([149397](https://api.mfapi.in/mf/149397), ALPHA) | 29 Dec 2021 | 8.31% | 9.06% | **−0.75** (−2.4 against Nifty 500 fund, 10.73%) | 24 Sep 2024 → 3 Mar 2025 | −31.5% | −15.1%, not recovered | −33.5% (6 Apr 2022 → 27 Feb 2023) | +7.3 since Nov 2012; worst fall −40.7% |
| Nifty Alpha Low-Volatility 30 | ICICI Pru ETF ([148456](https://api.mfapi.in/mf/148456), ALPL30IETF) | 13 Aug 2020 | 14.55% | 14.68% | −0.1 (−2.2 against Nifty 500 fund, 16.73%) | 27 Sep 2024 → 28 Feb 2025 | −25.0% | −15.1%, not recovered | −25.0% | +0.5 since Jul 2017; worst fall −31.3% |
| Nifty100 Low Volatility 30 | ICICI Pru ETF ([141596](https://api.mfapi.in/mf/141596), LOWVOLIETF) | 3 Jul 2018 (truncated; first trade 11 Jul 2017) | 12.27% | 11.76% | +0.5 | 27 Sep 2024 → 4 Mar 2025 | −18.2% | −5.3%, not recovered | −30.5% (17 Jan → 23 Mar 2020) | +0.1 since Jul 2016; worst fall −31.0% |
| Nifty200 Quality 30 | SBI ETF ([145648](https://api.mfapi.in/mf/145648), SBIETFQLTY) | 14 Dec 2018 | 10.95% | 12.27% | −1.3 | 27 Sep 2024 → 4 Mar 2025 | −22.5% | −13.3%, not recovered | −29.1% (31 Oct 2019 → 23 Mar 2020) | −1.4 since Apr 2018; worst fall −29.5% |
| Nifty Midcap 150, for scale | MID150BEES ([146271](https://api.mfapi.in/mf/146271)) | 1 Feb 2019 | 18.84% | 12.36% | +6.5 | 24 Sep 2024 → 28 Feb 2025 | −21.0% | +0.4%; recovered 17 Nov 2025 | −38.3% | — |

**Fund calendar years against the report's index figures, % [own computation]**

| Fund | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 to 9 Nov | Report's index: 2022 / 2023 / 2024 / 2025 |
|---|---|---|---|---|---|---|---|
| Tata Midcap150 Momentum 50 Index Direct | — | — | 49.8 | 30.9 | −4.2 | 1.0 | — / 52.5 / 32.3 / −3.5 |
| Motilal Oswal Nifty 500 Momentum 50 Index Direct | — | — | — | — | −8.4 | 1.8 | not in report |
| Kotak Nifty Alpha 50 ETF | — | −16.6 | 41.8 | 32.4 | −10.8 | 4.4 | −13.5 / 43.6 / 33.9 / −10.2 |
| ICICI Pru Alpha Low-Vol 30 ETF | 30.2 | −3.6 | 38.2 | 17.0 | −0.3 | −1.5 | −3.1 / 39.0 / 17.8 / 0.3 |
| ICICI Pru Nifty 100 Low Vol 30 ETF | 23.6 | 1.5 | 31.2 | 11.8 | 10.9 | −3.6 | 2.0 / 31.9 / 12.4 / 11.5 |
| SBI Nifty 200 Quality 30 ETF | 25.5 | −5.0 | 30.9 | 13.7 | 4.3 | −6.2 | −4.4 / 31.7 / 14.4 / 4.7 |
| ICICI Pru Nifty 200 Momentum 30 ETF | — | — | 40.8 | 20.6 | −5.1 | −2.5 | −5.5 / 41.7 / 21.3 / −4.6 |

Low Vol 30 and Quality 30 ETFs also give 2019 (4.9, 5.0) and 2020 (23.7, 25.6).

#### Inferences
- The report's index-based conclusions survive on fund data: a small positive since-launch edge for Momentum 30 (+1.7 against a Nifty 500 fund), negative over 2022–2025 (−1.7), a 31–32% fall, and no recovery in more than two years.
- Tracking cost is the new information. Yearly shortfall against the index is 0.0–0.5 points for UTI's direct plan, 0.5–0.9 for the ICICI momentum ETF, 0.4–0.8 for the low-vol, quality and alpha-low-vol ETFs, 0.7–2.7 for the Tata midcap-momentum fund and 0.6–3.1 for the Kotak Alpha 50 ETF. The index figures compared are the report's (a third-party compilation and the NSE whitepaper), not re-fetched.
- The Alpha 50 index's "+7.3 since 2012" has not been available to investors: the first product's NAV starts on 29 Dec 2021 and has trailed both broad index funds since.
- The Motilal Nifty 500 Momentum 50 fund opened three days after the market peak, so its own 31.6% fall understates the index's fall from 27 Sep 2024, and its since-launch figure (−8.2% a year) is the worst-case entry.
- The notes flagged a claim that the Nifty 50 stood 23.6% below its September 2024 high on 4 Sep 2026 as unreliable; the Nifty 50 fund was 7.0% below on that date.

#### Gaps
- No Nifty 200 index fund with history; the Nifty 500 fund is the stand-in.
- Other products on the same indices (Motilal, HDFC, Kotak, Bandhan, SBI momentum funds; Bandhan Alpha 50; Nippon and UTI alpha-low-vol; Edelweiss and Kotak midcap momentum) were not fetched, so each row rests on one fund.
- Nifty500 Value 50 was not checked (UTI fund code 151738 exists).
- Expense ratios and fund sizes are not in mfapi and remain as in the report.

### Q4. First NAV dates as launch-date proxies, and closing premium to NAV

#### Takeaway
First NAVs fall zero to seven days before the first exchange trade for every ETF launched since 2007, which supports the report's first-trade dates. For the three oldest BeES funds mfapi's history is truncated and says nothing about launch.

#### Cited findings

| NSE symbol | Scheme (codes) | First NAV in mfapi | First NAV value | Report's first trade | Reading |
|---|---|---|---|---|---|
| NIFTYBEES | Nippon India ETF Nifty 50 BeES (101325 → 115728 → [140084](https://api.mfapi.in/mf/140084)) | 19 Jun 2006 | 296.1205 (pre-split) | before 2005 | **Truncated.** Not a launch date |
| JUNIORBEES | Nippon India ETF Nifty Next 50 Junior BeES (101621 → 115729 → [140085](https://api.mfapi.in/mf/140085)) | 19 Jun 2006 | 52.3549 | before 2005 | **Truncated** |
| LIQUIDBEES | Nippon India ETF Nifty 1D Rate Liquid BeES ([140086](https://api.mfapi.in/mf/140086); older codes 101884 and 115730 not fetched) | 6 Nov 2016 | 1,000.0000 | before 2005 | **Truncated** |
| GOLDBEES | Nippon India ETF Gold BeES (105085 → 115744 → [140088](https://api.mfapi.in/mf/140088)) | 16 Mar 2007 | 942.8777 (pre-split) | 19 Mar 2007 | Consistent |
| MID150BEES | Nippon India ETF Nifty Midcap 150 ([146271](https://api.mfapi.in/mf/146271)) | 1 Feb 2019 | 60.6696 | 4 Feb 2019 | Consistent |
| SILVERBEES | Nippon India Silver ETF ([149758](https://api.mfapi.in/mf/149758)) | 4 Feb 2022 | 60.9596 | 7 Feb 2022 | Consistent |
| MOM30IETF | ICICI Prudential Nifty 200 Momentum 30 ETF ([150455](https://api.mfapi.in/mf/150455)) | 5 Aug 2022 | 183.3181 (pre-split) | 10 Aug 2022 | Consistent |
| MON100 | Motilal Oswal Nasdaq 100 ETF ([114984](https://api.mfapi.in/mf/114984)) | 30 Mar 2011 | 104.2030 (pre-split) | 31 Mar 2011 | Consistent |
| LIQUIDCASE | Zerodha CASE Nifty 1D Rate Liquid ETF ([152327](https://api.mfapi.in/mf/152327)) | 23 Jan 2024 | 100.1995 | 24 Jan 2024 | Consistent |
| LIQUIDADD | DSP BSE Liquid Rate ETF ([152555](https://api.mfapi.in/mf/152555)) | 27 Mar 2024 | 1,001.2681 | 3 Apr 2024 | Consistent |
| GROWWLIQID | Groww Nifty 1D Rate Liquid ETF ([152891](https://api.mfapi.in/mf/152891)) | 25 Sep 2024 | 100.0974 | 26 Sep 2024 | Consistent |
| ALPL30IETF | ICICI Prudential Nifty Alpha Low-Volatility 30 ETF ([148456](https://api.mfapi.in/mf/148456)) | 13 Aug 2020 | 117.80 (pre-split) | 18 Aug 2020 | Consistent |
| LOWVOLIETF | ICICI Prudential Nifty 100 Low Volatility 30 ETF ([141596](https://api.mfapi.in/mf/141596)) | 3 Jul 2018 | 85.03 (pre-split) | 11 Jul 2017 | **Truncated** by about a year |
| ALPHA | Kotak Nifty Alpha 50 ETF ([149397](https://api.mfapi.in/mf/149397)) | 29 Dec 2021 | 34.1096 | not in report (first close in NSEDATA4ME: 29 Dec 2021) | Consistent |
| SBIETFQLTY | SBI Nifty 200 Quality 30 ETF ([145648](https://api.mfapi.in/mf/145648)) | 14 Dec 2018 | 95.5983 | not in report (first close: 17 Dec 2018) | Consistent |
| (not listed) | UTI Nifty200 Momentum 30 Index Fund ([148703](https://api.mfapi.in/mf/148703)) | 12 Mar 2021 | 9.9454 | launched 10 Mar 2021 | Consistent |

Symbol-to-scheme links are by ISIN: the mfapi scheme list gives each scheme's ISIN and the Dhan scrip master gives the NSE symbol for the same ISIN. — [Jainu-s/nse_indices_historical_data](https://github.com/Jainu-s/nse_indices_historical_data); [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME)

**Closing price against same-day NAV, 27 Oct 2025 → 26 Oct 2026 [own computation]** — NAV from the scheme codes above; closes from [NSEDATA4ME](https://github.com/ancap97/NSEDATA4ME)

| Symbol | Median | 5th percentile | 95th percentile | Lowest | Highest |
|---|---|---|---|---|---|
| NIFTYBEES | +0.06% | −0.17% | +0.28% | −0.89% | +0.72% (19 Mar 2026) |
| JUNIORBEES | +0.11% | −0.16% | +0.25% | −0.62% | +1.34% (29 Sep 2026) |
| MID150BEES | +0.14% | −0.16% | +0.28% | −0.56% | +1.16% (1 Apr 2026) |
| GOLDBEES | +0.11% | −0.34% | +0.71% | −3.40% | +6.26% (21 Jan 2026) |
| SILVERBEES | −0.17% | −1.65% | +0.74% | −9.23% (30 Jan 2026) | +5.37% (26 Dec 2025) |
| LIQUIDCASE | 0.00% | −0.01% | +0.03% | −0.01% | +0.04% |
| LIQUIDADD | 0.00% | 0.00% | +0.03% | 0.00% | +0.04% |
| GROWWLIQID | 0.00% | −0.01% | +0.03% | −0.01% | +0.04% |
| MOM30IETF | −0.07% | −0.38% | +0.23% | −1.19% | +1.87% (29 Jun 2026) |
| MON100 | **+12.70%** | +0.38% | +22.48% | −3.02% | **+27.67%** (5 Jun 2026) |

Largest closing premiums in each ETF's whole history: GOLDBEES +12.6% (4 Dec 2013); NIFTYBEES +7.1% (18 Mar 2020); JUNIORBEES +15.9% (21 Jan 2008); MID150BEES +21.8% (19 Mar 2020); LOWVOLIETF +21.2% (16 Mar 2020); SBIETFQLTY +18.7% (18 Mar 2020); ALPHA +6.9% and ALPL30IETF +3.8% (both 4 Jun 2024).

#### Inferences
- The liquid ETFs close within 0.04% of NAV, so the price is a clean total-return series, as the report assumed.
- A buy limit of "0.5% above indicative NAV" (the report's execution rule) would have been breached at the close on fewer than 5% of days for the three equity ETFs and on more than 5% of days for GOLDBEES.
- Gold, silver and Nasdaq NAVs are struck from prices at a different time of day from the NSE close, so single-day gaps for those three include timing noise; medians and month-long gaps (December 2013, MON100 in 2026) do not.

#### Gaps
- True launch or allotment dates for NIFTYBEES, JUNIORBEES, LIQUIDBEES and LOWVOLIETF are not in mfapi.
- Intraday premiums and bid-ask spreads remain unsourced; these are closing figures only.

## (d) Failures and remaining gaps

**Failures.** None on the network side: 35 of 35 requests returned HTTP 200 and no endpoint refused. One local slip: a helper script named `inspect.py` shadowed Python's standard module and broke a pandas import; it was renamed `inspect_nav.py` and nothing was affected.

**Limits of the source**
- mfapi carries no expense ratios, fund sizes, traded volumes, index values or corporate-action records. Unit splits and distributions were inferred from NAV steps.
- History before April–June 2006 is absent for every scheme, and some schemes start later than their launch (NIFTYBEES, JUNIORBEES, LIQUIDBEES, LOWVOLIETF).
- Old BeES history is spread over three scheme codes each; one trading day is missing at each join.
- ETF "plan" labels in mfapi are unreliable ("Direct Plan", "IDCW" on schemes that have neither feature in practice); schemes were identified by ISIN and NAV behaviour.

**Still unconfirmed after this pass**
- Launch dates for the pre-2005 ETFs; LIQUIDBEES's realised return.
- Midcap returns before February 2019 from an investable product; Next 50 before June 2010 from a second series.
- Whether the six NIFTYBEES NAV shortfalls (and JUNIORBEES's one) were declared distributions, and their exact amounts.
- Index-level figures in the report (NSE whitepaper years, total-return compilation, live-since-launch index table, Nifty 200 comparisons) were not re-fetched; only the funds were measured.
- The "5.7% to 15%" silver premium of October 2025 was not reproduced for SILVERBEES on a close-to-NAV basis (maximum +3.0%).
- The rotation backtests themselves were not re-run. The findings above imply three adjustments if they are: use year-specific overnight returns less about 0.2–0.3 points in place of the flat 6%; add back NIFTYBEES and JUNIORBEES distributions before 2016; and measure drawdowns on NAV or index levels, or state that they are closing-price figures.
- Everything here is one unreviewed run.
