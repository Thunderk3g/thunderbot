# Momentum, Low-Volatility, Quality Factor Strategies and Trend-Following Filters in Indian Equities (NSE)

Compiled 23 Oct 2026. All figures are labelled with their as-of dates.

**Back-test vs live.** Every NSE factor index has a base date of 1 Apr 2005 (Alpha 50: 31 Dec 2003), but each launched much later. Figures before the launch date are NSE back-tests:
- Nifty200 Momentum 30: launched 25 Aug 2020
- Nifty Midcap150 Momentum 50: launched 16 Aug 2022
- Nifty200 Quality 30: launched 17 Apr 2018
- Nifty Alpha Low-Volatility 30: launched 10 Jul 2017
- Nifty Alpha 50: launched 19 Nov 2012
- Nifty100 Low Volatility 30: launch date not confirmed (see Gaps)

**Own computations.** Two sets of numbers marked **[own computation]** were calculated for these notes from public data (scripts in the session scratchpad):
- Momentum factor statistics, from the IIM Ahmedabad factor data library CSVs.
- 200-DMA / absolute-momentum filter tests, from Yahoo Finance ^NSEI daily closes.

They are not published results.

---

## Q1. NSE factor indices: exact methodology and long-run performance (Momentum 30, Midcap150 Momentum 50, Alpha 50, Low Vol 30, Quality 30, Alpha Low-Vol 30)

### Takeaway
Nifty200 Momentum 30 is a fully specified, replicable rule. Inputs are 6- and 12-month price returns (ending one month before the rebalance month), each divided by 1-year annualised volatility of daily log returns. These are cross-sectionally z-scored, averaged 50/50 and mapped to a "normalised score". The index holds the top 30 F&O-eligible Nifty 200 stocks, weighted by score × free-float market cap and capped at min(5%, 5× the market-cap weight). It rebalances in June and December with a 15/45 rank buffer.

Performance (TRI):
- Apr 2005 – Jun 2026: 18.8% CAGR, against 13.9% for Nifty 200 TRI and 13.6% for Nifty 50 TRI.
- Maximum drawdown: about -68% (Oct 2008).
- Calendar years: momentum lost heavily in 2008 (-60%), lagged badly in 2009 and 2025, and was flat-to-negative in 2018 and 2022.
- The live period since Aug 2020 confirms the premium, but it has been lumpy. The 5-year TR CAGR to 30 Sep 2026 is 9.28%, against 6.37% for Nifty 50 TRI.

Low volatility and quality give lower drawdowns and roughly 2–3 points of excess return over the long run, but have lagged in strong bull runs.

### Cited Findings

**Nifty200 Momentum 30: methodology (NSE methodology document, Sept 2026 edition)**
- **Universe:** stocks forming, or about to form, part of the Nifty 200 at review. Each stock needs at least 1 year of listing history and must be available for trading in the F&O segment on the effective date. — [NSE Indices Methodology Document, Sept 2026, pp.187-190](https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf)
- **Momentum ratios:**
  - MR12 = 12-month price return / σp, where 12-month return = [Price(M-1)/Price(M-13)] − 1.
  - MR6 = 6-month price return / σp, where 6-month return = [Price(M-1)/Price(M-7)] − 1.
  - M is the rebalance month and prices are as of the last trading day of the stated months, so the most recent month (the rebalance month) is excluded.
  - σp is the annualised standard deviation of daily lognormal returns over 1 year.
  - Source: [NSE Methodology Document](https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf)
- **Z-scores:** Z12 = (MR12 − mean MR12)/sd MR12 across the eligible universe, and likewise for Z6. Weighted Average Z = 0.5·Z12 + 0.5·Z6. — [NSE Methodology Document](https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf)
- **Normalised Momentum Score:** (1 + Z) if Z ≥ 0, and (1 − Z)^-1 if Z < 0. The top 30 by score are selected. — [NSE Methodology Document](https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf)
- **Weights:** weight ∝ free-float market cap × score. Each stock is capped at the lower of 5% or 5× its pure free-float market-cap weight. Capping is applied semi-annually at rebalance. — [NSE Methodology Document](https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf)
- **Reconstitution and buffer:** semi-annual, in June and December.
  - The top 15 ranked stocks are compulsorily included.
  - Existing constituents ranked beyond 45 are compulsorily excluded.
  - Stocks leaving the Nifty 200 exit at review.
  - Ad-hoc changes are made for corporate actions or suspensions, plus a quarterly check against SEBI concentration norms.
  - Source: [NSE Methodology Document](https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf)
- **Index facts:** base date 1 Apr 2005, base value 1000, launched 25 Aug 2020. — [NSE Factsheet Nifty200 Momentum 30, 30 Sep 2026](https://www.niftyindices.com/Factsheet/Factsheet_Nifty200_Momentum30.pdf)
- **Worked example from HDFC AMC.** A stock with 6-month return 30%, 12-month return 60% and 17% volatility has MR6 = 1.8 and MR12 = 3.5. That illustrates how volatility scaling penalises a stock with a similar return but higher volatility. — [HDFC NIFTY200 Momentum 30 Index Fund presentation, July 2026](https://files.hdfcfund.com/s3fs-public/Others/2026-07/HDFC%20NIFTY200%20Momentum%2030%20Index%20Fund_PPT%20%28July%202026%29.pdf)

**Nifty Midcap150 Momentum 50: methodology differences**
- **Universe and eligibility:** Nifty Midcap 150, with 1-year listing history. Non-F&O stocks are ineligible if they hit the upper or lower circuit on at least 20% of trading days in the past 6 months.
- **Selection and weights:** same score as Momentum 30. The top 50 are selected, with the same weighting and the same 5%/5× cap.
- **Rebalance and buffer:** semi-annual in June and December, using data to the last trading day of May and November.
  - Existing constituents ranked within the top 75 are retained.
  - The top 25 non-members are compulsorily included.
  - Constituents ranked beyond 75 are excluded.
- Source: [NSE Methodology Document, pp.191-192](https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf); [NSE Factsheet Midcap150 Momentum 50, 30 Sep 2026](https://www.niftyindices.com/Factsheet/Factsheet_NiftyMidcap150Momentum50.pdf)
- **Nifty500 Momentum 50 eligibility** adds further exclusions: promoter pledge above 20%, the bottom 10% by 6-month average turnover, and the bottom 10% by turnover ratio. — [NSE whitepaper "The Science of Momentum", Apr 2026, Exhibit 1](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf)

**Nifty100 Low Volatility 30: methodology**
- **Universe:** Nifty 100, F&O-available stocks only, with 1-year listing; DVRs are excluded.
- **Selection:** volatility = standard deviation of daily log price returns over the last 1 year. The 30 lowest-volatility stocks are selected.
- **Weights:** proportional to 1/volatility. Stocks with 6-month average turnover below the lowest in the Nifty 50 are capped at 3%.
- **Rebalance and buffer:** reconstituted quarterly using data to the end of February, May, August and November. Existing constituents within the top 60 are retained.
- Source: [NSE Methodology Document, pp.184-186](https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf)

**Nifty200 Quality 30: methodology**
- **Universe:** Nifty 200, F&O-available stocks only.
- **Score:** z-scores of ROE (latest fiscal year), D/E (latest fiscal year) and EPS growth variability (5 years, using 6 years of adjusted EPS).
  - Weighted Z = 0.33·Z(ROE) − 0.33·Z(D/E) − 0.33·Z(EPS variability).
  - For financials: 0.5·Z(ROE) − 0.5·Z(EPS variability).
  - Stocks with negative EPS in any of the previous 6 years are excluded.
  - The score uses the same (1+Z) / (1−Z)^-1 mapping as momentum.
- **Selection and weights:** top 30. Weight ∝ √(free-float market cap) × quality score, capped at min(5%, 5× market-cap weight).
- **Rebalance and buffer:** semi-annual in June and December. The top 10 are compulsorily included and constituents ranked beyond 50 are excluded.
- Source: [NSE Methodology Document, pp.222-224](https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf)

**Nifty Alpha 50: methodology**
- **Universe:** the top 300 companies by average free-float market cap and average daily turnover over 6 months, with 1-year listing and 100% trading frequency.
- **Selection:** Jensen's alpha computed from 1-year trailing prices; the top 50 by alpha are selected.
- **Weights:** proportional to alpha. Negative-alpha stocks are not selected.
- **Rebalance and buffer:** quarterly, using data to the end of February, May, August and November. Existing constituents within the top 100 are retained (100% buffer).
- Source: [NSE Methodology Document, p.173](https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf)

**Nifty Alpha Low-Volatility 30: methodology**
- **Universe:** Nifty 100 plus Nifty Midcap 50, F&O-available stocks only.
- **Score:** 50% alpha (Jensen's alpha over the previous year) and 50% low-volatility (inverse standard deviation of daily returns) factor z-scores.
- **Selection and weights:** top 30, factor-score weighted, with a 5% cap.
- Source: [NSE Methodology Document, pp.233-236](https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf); [NSE Factsheet Alpha Low-Vol 30, 30 Sep 2026](https://www.niftyindices.com/Factsheet/Factsheet_NIFTY_Alpha_Low-Volatility_30.pdf)

**Long-run performance: Nifty200 Momentum 30 vs Nifty 200 / Nifty 50 (TRI)**
- **CAGR as of 30 Jun 2026:**

  | Index | Since 1 Apr 2005 | 15y | 10y | 7y | 5y | 3y | 1y |
  |---|---|---|---|---|---|---|---|
  | Nifty200 Momentum 30 TRI | 18.8% | 18.1% | 17.8% | 16.6% | 12.6% | 14.1% | -2.5% |
  | Nifty 200 TRI | 13.9% | 12.3% | 13.5% | 13.6% | 11.8% | 12.1% | -2.2% |
  | Nifty 50 TRI | 13.6% | 11.4% | 12.5% | 11.9% | 10.0% | 8.8% | -5.4% |

  Source: [HDFC AMC presentation, July 2026 (source NSE Indices)](https://files.hdfcfund.com/s3fs-public/Others/2026-07/HDFC%20NIFTY200%20Momentum%2030%20Index%20Fund_PPT%20%28July%202026%29.pdf)
- **Average daily-rolling returns, Apr 2005 – Jun 2026 (Momentum 30 / Nifty 200 / Nifty 50 TRI):**

  | Horizon | Momentum 30 | Nifty 200 | Nifty 50 |
  |---|---|---|---|
  | 1y average (sd) | 22.3% (28.6%) | 16.4% (24.8%) | 15.9% (22.8%) |
  | 3y average | 18.2% | 12.8% | 12.5% |
  | 5y average | 18.6% | 12.9% | 12.6% |
  | 10y average | 19.1% | 12.6% | 12.2% |

  Source: [HDFC AMC presentation, July 2026](https://files.hdfcfund.com/s3fs-public/Others/2026-07/HDFC%20NIFTY200%20Momentum%2030%20Index%20Fund_PPT%20%28July%202026%29.pdf)
- **Financial-year returns (Momentum 30 / Nifty 200 / Nifty 50 TRI):**

  | FY | Momentum 30 | Nifty 200 | Nifty 50 |
  |---|---|---|---|
  | FY09 | -34.9% | -38.5% | -35.4% |
  | FY10 | 62.9% | 86.4% | 75.3% |
  | FY19 | 11.6% | 11.9% | 16.4% |
  | FY20 | -16.4% | -26.1% | -25.0% |
  | FY21 | 62.4% | 74.6% | 72.5% |
  | FY22 | 37.7% | 21.4% | 20.3% |
  | FY23 | -9.2% | -1.1% | 0.6% |
  | FY24 | 70.0% | 38.3% | 30.1% |
  | FY25 | -7.6% | 6.4% | 6.7% |
  | FY26 | -3.4% | -2.8% | -4.0% |
  | FY27 to date (to 30 Jun 2026) | 14.4% | 10.9% | 7.4% |

  Momentum 30 beat Nifty 200 TRI in 14 of 21 FYs and Nifty 50 TRI in 15 of 21. — [HDFC AMC presentation, July 2026](https://files.hdfcfund.com/s3fs-public/Others/2026-07/HDFC%20NIFTY200%20Momentum%2030%20Index%20Fund_PPT%20%28July%202026%29.pdf)
- **NSE whitepaper, annualised TR as of 27 Feb 2026.**
  - Since inception (Apr 2005):
    - Nifty200 Momentum 30: 19.19%, vs 15.08% for Nifty 200.
    - Midcap150 Momentum 50: 23.00%, vs 17.24% for Midcap 150.
    - Nifty500 Momentum 50: 21.94%, vs 18.85% for Nifty 500.
  - Momentum 30 over other periods: 10y 20.16% (Nifty 200 15.74%), 5y 18.15% (14.42%), 3y 21.50% (17.53%).
  - Since-inception Sharpe ratios (MIBOR risk-free): Momentum 30 0.50, Midcap150 Momentum 50 0.71, Nifty500 Momentum 50 0.63.
  - Source: [NSE whitepaper, Apr 2026, Exhibits 3-4b](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf)
- **Calendar-year returns of Nifty200 Momentum 30, with excess over Nifty 200.** The whitepaper does not state whether the table is PR or TR; other exhibits in the paper use TR.

  | Year | Momentum 30 | Excess over Nifty 200 | Nifty 200 (implied) |
  |---|---|---|---|
  | 2006 | 44.17% | +7.44 | |
  | 2007 | 100.84% | +35.28 | |
  | 2008 | -60.04% | -3.95 | ≈ -56.1% |
  | 2009 | 69.34% | -19.47 | |
  | 2010 | 19.75% | +4.13 | |
  | 2011 | -16.07% | +10.00 | |
  | 2012 | 38.80% | +5.17 | |
  | 2013 | 12.89% | +6.99 | |
  | 2014 | 49.56% | +12.25 | |
  | 2015 | 10.85% | +11.60 | |
  | 2016 | 9.56% | +4.48 | |
  | 2017 | 57.46% | +22.25 | |
  | 2018 | -1.66% | -1.98 | ≈ +0.3% |
  | 2019 | 10.55% | +0.52 | |
  | 2020 | 19.95% | +3.13 | |
  | 2021 | 53.81% | +24.93 | |
  | 2022 | -5.45% | -10.36 | |
  | 2023 | 41.71% | +17.05 | |
  | 2024 | 21.33% | +6.58 | |
  | 2025 | -4.57% | -14.13 | ≈ +9.6% |

  Momentum 30 beat Nifty 200 in 15 of 20 calendar years. — [NSE whitepaper, Apr 2026, Exhibit 7](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf)
- **Calendar-year returns of Midcap150 Momentum 50 (excess over Midcap 150):** 2008 -65.08% (-0.13); 2018 -16.98% (-4.36); 2019 5.61% (+4.99); 2020 26.86% (+1.30); 2023 52.48% (+7.87); 2024 32.30% (+7.83); 2025 -3.46% (-9.45). It beat its parent in 14 of 20 years. — [NSE whitepaper, Apr 2026, Exhibit 7](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf)
- **Maximum drawdown since Apr 2005** (all on 27 Oct 2008 except Midcap, 9 Mar 2009):
  - Momentum 30: -67.7%, vs -63.7% for Nifty 200.
  - Nifty500 Momentum 50: -70.2%, vs -63.7% for Nifty 500.
  - Midcap150 Momentum 50: -72.5%, vs -72.9% for Midcap 150.
  - Source: [NSE whitepaper, Apr 2026, Exhibit 6](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf)

**Latest factsheet snapshot, 30 Sep 2026** (TR returns; 5y and since-inception are CAGR; volatility is annualised from daily data on the PR index)

| Index | 1y TR | 5y TR CAGR | Since inception TR | SD since inception | Beta vs Nifty 50 (since inception) |
|---|---|---|---|---|---|
| Nifty200 Momentum 30 | -0.47% | 9.28% | 18.30% | 22.31% | 0.95 |
| Nifty Midcap150 Momentum 50 | 4.08% | 15.13% | 22.22% | 21.11% | 0.82 |
| Nifty200 Quality 30 | -5.42% | 6.40% | 16.64% | 17.87% | 0.79 |
| Nifty Alpha Low-Volatility 30 | -1.91% | 8.57% | 17.71% | 17.20% | 0.74 |
| Nifty Alpha 50 (base Dec 2003) | 11.44% | 12.03% | 20.21% | 24.74% | 0.97 |
| Nifty 50 TRI (comparator) | -7.09% | 6.37% | — | — | — |

- Momentum 30's YTD 2026 TR at 30 Sep 2026 was -4.65%.
- Sources: [Momentum 30 factsheet](https://www.niftyindices.com/Factsheet/Factsheet_Nifty200_Momentum30.pdf); [Midcap150 Momentum 50 factsheet](https://www.niftyindices.com/Factsheet/Factsheet_NiftyMidcap150Momentum50.pdf); [Quality 30 factsheet](https://www.niftyindices.com/Factsheet/Factsheet_NIFTY200_Quality30.pdf); [Alpha Low-Vol 30 factsheet](https://www.niftyindices.com/Factsheet/Factsheet_NIFTY_Alpha_Low-Volatility_30.pdf); [Alpha 50 factsheet](https://www.niftyindices.com/Factsheet/Factsheet_Nifty_Alpha50.pdf); Nifty 50 TRI comparator from [ICICI Pru Nifty 100 Low Vol 30 ETF factsheet, 30 Sep 2026](https://www.icicipruamc.com/blob/knowledgecentre/factsheet-schemes/Passive%20Schemes/ETFs%20Schemes/ICICI%20Prudential%20Nifty%20100%20Low%20Volatility%2030%20ETF.pdf)

**Nifty100 Low Volatility 30**
- **Live-ish data (TRI to 30 Sep 2026):** 1y -4.68%, 3y 8.97%, 5y 8.12%. Over the ETF's life, 12.38% CAGR, vs 11.03% for Nifty 50 TRI. Inception date not shown in the extracted text; the 2.94× growth implies roughly 9.2 years. — [ICICI Pru Nifty 100 Low Vol 30 ETF factsheet, Sep 2026](https://www.icicipruamc.com/blob/knowledgecentre/factsheet-schemes/Passive%20Schemes/ETFs%20Schemes/ICICI%20Prudential%20Nifty%20100%20Low%20Volatility%2030%20ETF.pdf)
- **NSE 2018 white paper (price return, mostly back-tested), to 31 May 2018:**
  - CAGR since Apr 2005: 17.66%, vs 13.66% for Nifty 100.
  - Volatility: 18.18% vs 22.62%.
  - Return/risk: 0.97 vs 0.60.
  - Calendar years: 2008 -43.3% vs -53.7%; 2009 +89.8% vs +82.7%; 2011 -13.3% vs -25.8%; 2017 +28.2% vs +31.0%.
  - Worst drawdown: -49.5% (2 Jan to 27 Oct 2008), vs -61.5% for Nifty 100.
  - Outperformed Nifty 100 in 100% of rolling 5, 7 and 10-year windows.
  - Source: [NSE NIFTY100 Low Vol 30 white paper, Jun 2018](https://archives.nseindia.com/content/indices/NIFTY100_Low_Vol30_White_paper_Jun2018.pdf)
- **Third-party back-test, 2006–2025:** a low-volatility portfolio had Sharpe 0.87 and max drawdown -42.80% (low-turnover bucket). — [Freefincal](https://freefincal.com/?p=348456)

### Inferences
- **Live premium.** Over the live period (Sep 2021 – Sep 2026, 5y), Momentum 30 still beat Nifty 50 TRI by about 2.9 points a year (9.28% vs 6.37%). That is smaller than the 4–5 point back-tested premium, and it came with a beta of about 1.18 over that window.
- **Momentum's worst calendar years:** 2008 (crash), 2009 (sharp rebound led by beaten-down stocks), 2022 and 2025 (leadership reversals). These are exactly the "momentum crash" regimes the literature describes: rebounds after bear markets, and abrupt rotations.
- **Midcap momentum.** Midcap150 Momentum 50 had the highest long-run CAGR (about 22–23%) with a since-inception beta of only 0.82. Its max drawdown roughly matched its parent's (-72.5%), so the extra return did not come with extra crash depth.
- **Low-vol and quality** have about 18% volatility vs about 22% for momentum, and roughly 10 points shallower 2008 drawdowns. A 50/50 momentum + low-vol (or quality) blend is the natural diversified candidate. Note that Nifty Alpha Low-Vol 30 already embeds this idea (17.71% since 2005 at 17.2% SD).
- **Methodology drift.** The F&O-eligibility requirement now appears in the Momentum 30, Low Vol 30, Quality 30 and multi-factor methodologies. Historical back-tests may have been computed under earlier rules. Replicators should apply the current rules to point-in-time data.

### Gaps
- No calendar-year Nifty 50 TRI series was found to sit alongside the whitepaper's calendar-year table. Nifty 200 values are implied only from the excess returns.
- Couldn't retrieve the official NSE factsheet for Nifty100 Low Volatility 30 (the URL could not be found), so its official launch date, since-inception CAGR and SD are unconfirmed.
- Couldn't open the Business Standard article (Dec 2025, "Nifty200 Momentum30: a flip of index switch jolts ₹16K cr") because it returned 403. Exactly what rule changed in Dec 2025, and when the F&O requirement began, are therefore unconfirmed.
- No official max-drawdown figures were found for Quality 30, Alpha 50 or Alpha Low-Vol 30.

---

## Q2. Academic evidence on cross-sectional momentum in India (size of premium, crash risk, transaction costs)

### Takeaway
Momentum is the most robust equity anomaly in Indian academic data.

- **IIMA library, 1993–2025** [own computation]: the survivorship-adjusted WML (winners-minus-losers) factor averages about 1.1% a month (t ≈ 3.1), roughly 13% a year arithmetic.
- **Volatility and crashes:** annual volatility is 19–25%. There were severe crashes: -53% (2000) and -52% (Nov 2008 – Aug 2009, the post-crisis rebound).
- **Long-only side:** big-cap winners compounded about 2.3 points a year faster than the market (2005–2025).
- **Transaction costs:** studies find long-only momentum survives costs. Third-party replications suggest much of the premium sits in less liquid names.

### Cited Findings
- **IIM Ahmedabad (Agarwalla, Jacob, Varma) data library.** Fama-French plus momentum factors for India, from CMIE Prowess data.
  - Methodology: firms traded on fewer than 50 days in the prior 12 months are excluded, and the factors are corrected for survivorship bias.
  - Momentum signal: the 11-month return from t-12 to t-1 (so the latest month is skipped). Winners are the top 30%, losers the bottom 30%.
  - Portfolios are cross-sorted with size. WML = average of (WS − LS) and (WB − LB).
  - The data are updated (latest file 2025-12).
  - Source: [Agarwalla, Jacob & Varma, "Four factor model in Indian equities market", IIMA WP 2013-09-05 (revised)](https://faculty.iima.ac.in/~iffm/Indian-Fama-French-Momentum/four-factors-India-90s-onwards-IIM-WP-Version.pdf); [IIMA data library](https://faculty.iima.ac.in/iffm/Indian-Fama-French-Momentum/); [Prof. Varma page](https://www.jrvarma.in/fama-french.html)
- **Paper abstract:** momentum factor average annual return 21.9% (Jan 1994 – Dec 2014 per the abstract), HML 15.3%, SMB about 0%, and market excess return 11.5%. Another summary flags that these abstract figures are internally inconsistent, so they need checking against the paper's tables. — [IIMA WP](https://faculty.iima.ac.in/~iffm/Indian-Fama-French-Momentum/four-factors-India-90s-onwards-IIM-WP-Version.pdf)
- **[own computation] WML statistics** from the [IIMA monthly survivorship-adjusted CSV (2025-12 release)](https://faculty.iima.ac.in/iffm/Indian-Fama-French-Momentum/DATA/2025-12_FourFactors_and_Market_Returns_Monthly_SurvivorshipBiasAdjusted.csv):

  | Period | Mean/month | CAGR | Annual vol | t-stat | Max drawdown | Positive months |
  |---|---|---|---|---|---|---|
  | Nov 1993 – Dec 2025 | 1.11% | 10.9% | 24.5% | 3.08 | -53.5% (Feb–Nov 2000) | 59% |
  | Apr 2005 – Dec 2025 | 1.11% | 12.1% | 19.2% | 3.16 | -52.4% (Nov 2008 – Aug 2009) | — |
  | 2010 – 2025 | — | 14.3% | 16.5% | 3.58 | -33.3% (Jul 2013 – May 2014) | — |
  | 2016 – 2025 | — | 11.5% | 14.3% | — | -25.7% (Mar 2020 – Jan 2021) | — |

  - **Worst months:** Nov 2001 -27.6%, May 2009 -25.0%, Apr 2000 -21.1%, Dec 2008 -20.3%, Apr 2009 -18.3%, Jan 2012 -18.0%, Apr 2020 -13.5%.
  - **Worst rolling 12 months:** -44.2% (to Nov 2009).
- **[own computation] Annual WML** (IIMA yearly file):

  | Year | WML | Year | WML |
  |---|---|---|---|
  | 1998 | -31.9% | 2018 | +22.8% |
  | 2000 | -36.0% | 2019 | +29.6% |
  | 2008 | -9.6% | 2020 | -3.8% |
  | 2009 | -30.5% | 2021 | +31.3% |
  | 2011 | +52.1% | 2022 | -0.1% |
  | 2012 | -2.9% | 2023 | +12.8% |
  | | | 2024 | +20.6% |
  | | | 2025 | -5.5% |

  Monthly: 2020 had WML +10.9% in Feb and +13.8% in Mar (crash), then -13.5% in Apr (rebound). 2025: Jan -6.3%, May -6.1%. — [IIMA yearly CSV](https://faculty.iima.ac.in/iffm/Indian-Fama-French-Momentum/DATA/2025-12_FourFactors_and_Market_Returns_Yearly_SurvivorshipBiasAdjusted.csv)
- **[own computation] Long-only side, Apr 2005 – Dec 2025** (IIMA size-momentum portfolios, survivorship-adjusted):

  | Portfolio | CAGR | Vol | Max drawdown |
  |---|---|---|---|
  | Big-cap winners (WB) | 17.2% | 23.1% | -59.8% |
  | Market (MF+RF) | 14.9% | 21.6% | -61.9% |
  | Big-cap losers | 9.4% | 34.1% | -63.3% |

  Over Nov 1993 – Dec 2025: WB 19.5% vs market 13.0%. — [IIMA size-momentum CSV](https://faculty.iima.ac.in/iffm/Indian-Fama-French-Momentum/DATA/2025-12_Size_Momentum_Portfolio_Returns_Monthly_SurvivorshipBiasAdjusted.csv)
- **Jacob, Pradeep & Varma (SSRN, Nov 2022), Apr 1995 – Mar 2021:**
  - Momentum factor averaged 1.62% a month (vol 7.16%), vs 1.69% for quality-minus-junk (vol 6.71%) and 1.33% for the market. Value was marginally negative.
  - Average drawdowns: momentum 12.13% long-short and 14.52% long-only; QMJ 9.76%; long-only quality 7.99%.
  - INR 100 grew to INR 6,988 in momentum and INR 9,345 in QMJ.
  - QMJ four-factor alpha: 0.92% a month.
  - Source: [Quantpedia summary](https://quantpedia.com/performance-of-factor-strategies-in-india/); [SSRN 4284686](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4284686)
- **Sehgal & Jain (2011):** momentum profits exist in India and are stronger for 6-6 than 12-12 strategies. Sector momentum also exists, and part of stock momentum is captured by the sector factor. — [Journal of Advances in Management Research (Emerald)](https://www.emerald.com/insight/content/doi/10.1108/09727981111129327/full/html)
- **Ansari & Khan (2012), 1995–2006:** strong momentum profits that CAPM and Fama-French cannot explain. Buying the 3- and 6-month winners was profitable, which the authors read as support for behavioural explanations. — [Managerial Finance 38(2) (Emerald)](https://emerald.com/insight/content/doi/10.1108/03074351211193730/full/html)
- **Aggarwal & Gupta (2017):** long-only momentum stays profitable after transaction costs and exchange restrictions, but only for short formation and holding periods. Medium and long-term momentum were not rewarded in their sample. — [Journal of Commerce and Accounting Research](https://www.publishingindia.com/archive/jcar/can-small-investors-gain-from-momentum-trading-in-india-an-empirical-investigation)
- **Maheshwari & Dhankar (2016), NSE 1997–2013:** momentum is profitable, with no January or April seasonality. — summarised in search results for [JCAR seasonality paper](https://www.publishingindia.com/archive/jcar/seasonality-in-momentum-profits-evidence-from-the-indian-stock-market)
- **Liquidity and costs (third-party replication, EODHD data, Dec 2006 – Jun 2025):**
  - Set-up: top 200 by market cap with PE > 0, 12-month return / 12-month volatility, 30 stocks equal-weighted, rebalanced in June and December. Costs of 0.11% plus 0.05% slippage per trade, and Indian LTCG/STCG taxes.
  - Gross CAGR 15.23% and net 14.01%, vs 10.42% for Nifty 50.
  - Net max drawdown -70.53% with a 65-month recovery; net Sharpe 0.35.
  - Illiquid-stock momentum returned 19.43% CAGR, while liquid-stock momentum returned 8.51%, below Nifty 50. The author argues most of the premium sits in illiquid names.
  - Source: [BacktestIndia](https://backtestindia.com/blog/momentum-investing-india-backtest); see also [Freefincal, "Is Indian Momentum Investing Just a Liquidity Illusion?"](https://freefincal.com/is-indian-momentum-investing-just-a-liquidity-illusion/) (low-liquidity sub-portfolio max drawdown -66.41%)
- **Global benchmark:** momentum is significantly profitable only for round-trip costs below about 1.5% (Grundy & Martin, as cited in an NSE research paper). — [NSE Research Paper RP 2, Feb 2012](https://nsearchives.nseindia.com/research/content/RP_2_Feb2012.pdf)

### Inferences
- **Size of the premium.** Robust estimates of the long-short premium are 10–14% a year (IIMA), though the long-short form is not implementable for retail because short-selling is restricted. The relevant figure is the long-only winners' edge over the market: about 2–5 points a year, depending on universe and weighting. Big-cap winners beat the market by 2.3 points (IIMA, 2005–2025), and Nifty200 Momentum 30 beat Nifty 200 by about 4.9 points (NSE, 2005–2026).
- **Crash risk** is concentrated in post-crash rebounds (2009 and Apr 2020) and in sharp leadership reversals (2000, Nov 2001, Jan 2012, Jan 2025). The long-only form loses less because its losses are not amplified by a short leg.
- **Costs.** With Indian round-trip costs for liquid large or midcaps around 0.2–0.5%, plus STCG at 20%, semi-annual momentum keeps most of its edge (net-of-tax drag of about 1.2 points a year in one replication). The liquidity finding means a Nifty 200 or F&O-only universe is safer but may earn less than small-cap back-tests suggest.

### Gaps
- Couldn't locate a "Raju & Chandrasekaran" Indian momentum paper; the name may be misremembered.
- IIM paper tables (t-stats by sub-period, transaction-cost analysis) could not be read beyond the methodology section.
- No peer-reviewed Indian study was found that quantifies momentum crash risk conditional on market state, in the manner of Daniel & Moskowitz.

---

## Q3. Time-series momentum / trend filters in India (Nifty above 200-DMA, absolute momentum, dual momentum)

### Takeaway
On Nifty 50, a 200-day moving-average filter roughly halves maximum drawdown and cuts volatility by about a third. How much return it gives up depends heavily on how often the signal is checked:
- **Daily-checked** filters whipsaw about 8 times a year and lose about 2 points of CAGR.
- **Month-end-checked** filters switch about 2 times a year and roughly matched buy-and-hold CAGR from mid-2008 to Oct 2026, though they lagged after 2015.

Published Indian evidence is mostly blog back-tests without costs or taxes; no rigorous peer-reviewed study was found.

### Cited Findings
- **[own computation] Nifty 50 price index (^NSEI from Yahoo Finance), 8 Jul 2008 – 14 Oct 2026 (18.3 years).**
  - Assumptions: cash earns 6.5% a year when out of the market; 0.10% cost per switch; no taxes. The signal at day t's close is applied to the next day's return.
  - The price index excludes dividends (about 1.2–1.5% a year), which understates buy-and-hold relative to the cash-earning strategies.
  - The test starts after the Jan 2008 peak, so the full 2008 drawdown is not captured.

  | Rule | CAGR | Vol | Max drawdown | Switches | Time in market |
  |---|---|---|---|---|---|
  | Buy-and-hold | 10.0% | 19.5% | -45.4% | — | 100% |
  | Daily close > SMA200 | 7.8% | 12.9% | -20.9% | 144 (7.9/yr) | 71% |
  | SMA200 ±2% band | 7.7% | 13.0% | -25.0% | 38 (2.1/yr) | — |
  | Month-end close > SMA200 | 10.1% | 13.5% | -24.2% | 35 (1.9/yr) | 71% |
  | SMA50 > SMA200 crossover | 6.9% | 12.7% | -38.8% | 24 (1.3/yr) | — |
  | Month-end 12m return > 6.5% cash (absolute momentum) | 4.4% | 12.0% | -22.7% | 33 (1.8/yr) | 63% |

  - **2015 – Oct 2026 sub-period:** buy-and-hold 8.8% CAGR, max drawdown -38.4%. Daily SMA200: 5.3%, -20.9%, 8.9 switches a year. Month-end SMA200: 7.3%, -16.6%.
  - Script output from [Yahoo Finance ^NSEI chart data](https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI?period1=0&period2=1792000000&interval=1d).
- **Momentum Lab, NIFTYBEES, 10 years:** a 200-day EMA absolute-momentum rule had max drawdown -20.19%, vs -36.34% for buy-and-hold. — [Momentum Lab (Substack)](https://momentumlab.substack.com/p/backtesting-dual-momentum-strategy) (as summarised in search results)
- **Momentum Lab dual momentum, Nifty vs Gold vs fixed deposit, 2014–2024:**
  - Rule: hold whichever of Nifty or gold has the higher 200-day return, provided it also beats the FD return; otherwise hold the FD.
  - CAGR 18.79% vs Nifty 12.13% and gold 10.86%. Max drawdown -11.42% vs Nifty -34.00%.
  - No costs, taxes, rebalance frequency or switch counts are reported.
  - Source: [Momentum Lab](https://momentumlab.substack.com/p/backtesting-dual-momentum-strategy)
- **Quantinuous, Nifty LargeMidcap 250 momentum back-test:** a Nifty 50 EMA100 exit rule reportedly cut max drawdown from 48.6% to 19.14%, at about 30% CAGR over 20 years. Self-reported. — [Quantinuous (Substack)](https://quantinuous.substack.com/p/weekly-momentum-portfolio-protection)
- **Paperswithbacktest, Nifty 1990–2026:** trend-following rules based on 80-day EMAs had a worst drawdown of -31.1%. — [Paperswithbacktest](https://paperswithbacktest.com/strategies/trend-following-algorithms-on-india-s-nifty-index) (from search snippet; not verified in full)
- **Capitalmind** discusses adding a trend layer ("Capitalmind Chase") to long-only portfolios to cut drawdowns, but publishes no figures publicly. — [Capitalmind podcast 31](https://premium.capitalmind.in/2020/08/podcast-31-how-trend-following-can-make-buy-and-hold-better/)
- **Current regime context:** in Oct 2026 Business Standard reported only 10 of the 50 Nifty stocks (20%) above their 200-DMA. Another outlet reported a 160-day streak of Nifty below its 200-DMA. — [Business Standard, Oct 2026](https://www.business-standard.com/markets/news/nifty-s-200-day-moving-average-sounds-alarm-as-market-breadth-thins-126101401265_1.html); [Whalesbook](https://www.whalesbook.com/news/English/sebiexchange/Nifty-50-Marks-160-Day-Streak-Below-200-DMA-What-It-Means/6adabe3379a16deaeafae99c)

### Inferences
- **Check the filter monthly, not daily.** Daily checking roughly quadruples switches (about 8 vs 2 a year) and costs about 2 points of CAGR in whipsaws. A ±2% band cuts switches to about 2 a year, but it did not recover the CAGR in this sample.
- **Expect lower drawdowns, not higher returns.** A 200-DMA filter on Nifty should be expected to cut max drawdown from about 40–55% to about 17–25%, at roughly equal-or-lower CAGR. Return parity in 2008–2026 depended on the 2008 bear market (partly in sample) and the 6.5% cash yield.
- **Taxes.** Each exit triggers STCG (20%) or LTCG (12.5%) in a taxable account, which the figures above ignore. This favours applying the filter inside tax-efficient wrappers, or using it to toggle new allocations rather than liquidate.
- **Absolute momentum** (12-month return above cash) did poorly in India over 2008–2026 (4.4% CAGR). The fast V-shaped recoveries of 2009 and 2020 punish slow 12-month signals. The 200-DMA rule reacted faster.
- **As a filter on a momentum portfolio,** trend overlays mainly target the 2008-type crash (-60% to -70%). They do not help in 2009-type rebounds or in 2025-type rotations when the broad market is above its 200-DMA.

### Gaps
- No peer-reviewed or NSE-published study was found of 200-DMA, time-series momentum or dual momentum on Nifty or Nifty sector indices with costs and taxes.
- No Indian sector-rotation dual-momentum study with reliable numbers was found.
- The own computation uses the price index, not TRI, and starts July 2008. A TRI-based test from 1999 or 2005 would be more definitive.
- Couldn't access Momo India's "reducing momentum drawdowns" back-test (404), so the stock-level 200-DMA overlay results are unknown.

---

## Q4. Momentum drawdowns and regime risk in India (2008, 2009, 2020, 2022, 2024-25)

### Takeaway
Momentum 30's worst drawdown was about -68% in 2008 (vs -64% for Nifty 200), with a recovery of about 5 years in replications. Its worst drawdown since 2011 is only about -34% (COVID 2020), comparable to the market. Its main modern risk is relative: sharp underperformance when leadership rotates.

- **FY23:** -9.2% vs -1.1% for Nifty 200.
- **FY25:** -7.6% vs +6.4%.
- **CY2025:** -4.57% vs about +9.6%.
- **Peak to trough:** a roughly 27–29% fall from the Sep 2024 peak, vs about 12–15% for broad indices.

### Cited Findings
- **2008:** max drawdown -67.7% (to 27 Oct 2008), vs -63.7% for Nifty 200. The 2008 calendar-year return was -60.04%. — [NSE whitepaper, Apr 2026](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf)
  - A blog cites -67.9% for Momentum 30 vs -64.6% for Nifty 50 (2008). — [Curious Investing Insights](https://curiousinvestinginsights.substack.com/p/momentum-or-mayhem-unpacking-the)
  - The replication shows net -70.53% (Oct 2007 – Dec 2008), with recovery only in May 2014 (65 months), vs a 60-month recovery for Nifty 50. — [BacktestIndia](https://backtestindia.com/blog/momentum-investing-india-backtest)
- **2009 rebound:** Momentum 30 returned +69.34% vs about +88.8% for Nifty 200 (excess -19.47). FY10 was +62.9% vs +86.4%. — [NSE whitepaper](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf); [HDFC AMC](https://files.hdfcfund.com/s3fs-public/Others/2026-07/HDFC%20NIFTY200%20Momentum%2030%20Index%20Fund_PPT%20%28July%202026%29.pdf)
- **COVID 2020:** Momentum 30 drawdown -34.2% vs -39.6% for Nifty 50 (blog figure). — [Curious Investing Insights](https://curiousinvestinginsights.substack.com/p/momentum-or-mayhem-unpacking-the)
  - Mirae Asset reports a max drawdown of -34.0% for Momentum 30 over Jan 2011 – Jun 2026, with a 13.9-month max recovery period. That compares with -38.3% for Nifty 50 (12.6 months) and -41.7% for Nifty500 Multicap 50:25:25 (12.6 months). — [Mirae Asset Nifty200 Momentum 30 + G-Sec 50:50 ETF presentation (data to Jun 2026)](https://www.miraeassetmf.co.in/docs/default-source/product-presentations/mirae-asset-nifty200-momentum-30-plus-8-13-yr-g-sec-5050-etf-presentation.pdf)
  - FY20 was -16.4% vs -26.1% for Nifty 200 TRI. Calendar 2020 was +19.95%. — [HDFC AMC](https://files.hdfcfund.com/s3fs-public/Others/2026-07/HDFC%20NIFTY200%20Momentum%2030%20Index%20Fund_PPT%20%28July%202026%29.pdf); [NSE whitepaper](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf)
- **2022–23:** drawdown -14.8% vs -13.2% for Nifty 50 (blog). CY2022 return -5.45% (excess -10.36). FY23 -9.2% vs -1.1% for Nifty 200 TRI. — [Curious Investing Insights](https://curiousinvestinginsights.substack.com/p/momentum-or-mayhem-unpacking-the); [NSE whitepaper](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf); [HDFC AMC](https://files.hdfcfund.com/s3fs-public/Others/2026-07/HDFC%20NIFTY200%20Momentum%2030%20Index%20Fund_PPT%20%28July%202026%29.pdf)
- **2024–25 slump:**
  - About -27% in the 6 months to around Mar 2025, vs -12% for Nifty 50 and -15% for Nifty 200. — [Curious Investing Insights](https://curiousinvestinginsights.substack.com/p/momentum-or-mayhem-unpacking-the)
  - As of 24 Oct 2025, the 52-week range was 25,133.95 – 35,490.75 (≈ -29% high to low) and the 1-year return was -9.53%. — [Kotak Securities index page](https://www.kotaksecurities.com/indices/nifty200-momentum-30)
  - NSE notes that momentum indices underperformed in the Jul 2024 – Oct 2025 "downward market phase" after leading in Aug 2023 – Aug 2025. — [NSE whitepaper, Exhibit 5](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf)
  - In the replication, Jan 2025 alone was -11.1% vs -0.9% for low-vol. — [BacktestIndia](https://backtestindia.com/blog/momentum-investing-india-backtest)
- **2026 status:** YTD TR -4.65% and 1y TR -0.47% at 30 Sep 2026. The portfolio was concentrated in Capital Goods (24.1%), Financial Services (21.2%), Metals & Mining (18.7%) and Power (14.2%), with zero IT, FMCG or Oil & Gas versus the Nifty 200 (Jun 2026 comparison). — [NSE factsheet, Sep 2026](https://www.niftyindices.com/Factsheet/Factsheet_Nifty200_Momentum30.pdf); [HDFC AMC, Jun 2026 sector table](https://files.hdfcfund.com/s3fs-public/Others/2026-07/HDFC%20NIFTY200%20Momentum%2030%20Index%20Fund_PPT%20%28July%202026%29.pdf)
- **[own computation] Factor-level crashes (IIMA WML):** Apr–May 2009 -18.3% and -25.0%; Apr 2020 -13.5%; worst rolling 12 months -44.2% (to Nov 2009). — [IIMA data library](https://faculty.iima.ac.in/iffm/Indian-Fama-French-Momentum/)
- **Diversifier evidence:** in 2008, Low Vol 30 fell -43.3% vs -53.7% for Nifty 100 (price return). In 2011 it fell -13.3% vs -25.8%. — [NSE Low Vol white paper, 2018](https://archives.nseindia.com/content/indices/NIFTY100_Low_Vol30_White_paper_Jun2018.pdf)
  - In one replication, the correlation of monthly returns between momentum and low-vol was 0.87. A sequential low-vol-then-momentum filter had a -16.5% drawdown in COVID 2020. — [BacktestIndia](https://backtestindia.com/blog/momentum-investing-india-backtest)
- **Momentum + bond 50:50:** Nifty200 Momentum 30 + 8–13y G-Sec 50:50 index (back-test, Jan 2011 – Jun 2026): 12.7% CAGR, COVID drawdown -17.6%, volatility 9.7%, Sharpe 0.63, Calmar 0.72. Nifty 50 over the same period: 10.5% CAGR, -38.3% drawdown, 16.5% volatility. — [Mirae Asset presentation](https://www.miraeassetmf.co.in/docs/default-source/product-presentations/mirae-asset-nifty200-momentum-30-plus-8-13-yr-g-sec-5050-etf-presentation.pdf)

### Inferences
- **Size positions for the 2008 case.** A realistic planning assumption for a long-only Nifty 200 momentum book is a -35% drawdown in a normal bear market, with a -65% to -70% tail in a 2008-style crash. Relative underperformance of 10–20 points can last 6–18 months (2009, 2022, Sep 2024 – 2025).
- **Momentum underperformed broad indices in both crashes and rebounds** (2008/2009, 2020 April) and in rotations (2022, 2025), but beat them in the 2020 crash month itself. Blending with low-vol, quality or bonds is the best-documented way to reduce this.

### Gaps
- No official NSE figure was found for the exact Momentum 30 peak-to-trough drawdown from Sep 2024 (date and level). The 27–29% figures are a blog estimate and an inference from the Kotak range.
- No drawdown-duration statistics were found for the official index (only the replication's 65 months and Mirae's 13.9 months for post-2011).

---

## Q5. Practical: turnover, number of holdings, rebalance frequency

### Takeaway
NSE's own study finds semi-annual rebalancing beat quarterly for Nifty200 Momentum 30 (19.19% vs 17.12% since 2005), with 20–50% less churn. Quarterly helped only in midcaps.

One-way churn per year for the semi-annual Momentum 30 is about 100–135%. The rank buffer (top 15 always in, out only beyond rank 45 for 30 names) is the main turnover control.

Typical index holdings: 30 names (large/mid), 50 names (midcap). Market-cap tilt plus a 5% cap keeps it investable. Index fund tracking errors are 0.17–0.52%.

### Cited Findings
- **Quarterly vs semi-annual since Apr 2005 (to 27 Feb 2026):**

  | Index | Quarterly | Semi-annual |
  |---|---|---|
  | Nifty200 Momentum 30 | 17.12% | 19.19% |
  | Midcap150 Momentum 50 | 23.26% | 23.00% |
  | Nifty500 Momentum 50 | 21.16% | 21.94% |

  - Semi-annual Momentum 30 beat quarterly in 100% of 10-year and 7-year rolling windows, and 70% of 1-year windows.
  - Quarterly beat semi-annual in only 6 of 20 calendar years for Momentum 30, 12 of 20 for Midcap150 Momentum 50, and 9 of 20 for Nifty500 Momentum 50.
  - Source: [NSE whitepaper, Exhibits 8-10](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf)
- **Annual churn, % of index weight replaced (quarterly vs semi-annual):**

  | Index | FY22 | FY23 | FY24 | FY25 | FY26 to 27 Feb |
  |---|---|---|---|---|---|
  | Momentum 30 | 148 vs 101 | 146 vs 112 | 147 vs 115 | 167 vs 110 | 123 vs 134 |
  | Midcap150 Momentum 50 | — | — | — | 129 vs 96 | — |
  | Nifty500 Momentum 50 | — | — | — | 218 vs 139 | — |

  Quarterly adds about 20–70% extra annual churn. — [NSE whitepaper, Exhibit 11](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf)
- **Buffers by index:**
  - Momentum 30: top 15 in, out beyond 45.
  - Midcap Momentum 50: retain within 75, top 25 in.
  - Quality 30: top 10 in, out beyond 50.
  - Low Vol 30: retain within top 60.
  - Alpha 50: retain within top 100.
  - Source: [NSE Methodology Document](https://www.niftyindices.com/Methodology/Method_NIFTY_Equity_Indices.pdf)
- **Implementation (as of 27 Feb 2026):**
  - 24 passive funds track the momentum indices, with AUM of about ₹17,667 cr. Of these, 13 Nifty200 Momentum 30 funds hold about ₹12,523 cr; UTI's index fund alone is ₹8,712 cr.
  - 1-year tracking errors run from 0.17% (UTI, HDFC ETF) to 0.52% (Motilal index fund).
  - Source: [NSE whitepaper, Exhibit 12](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf)
- **Concentration:** Momentum 30's top 10 weights summed to 49.29%, and large caps were about 52% of weight vs about 48% midcaps (Jun 2026). — [HDFC AMC presentation](https://files.hdfcfund.com/s3fs-public/Others/2026-07/HDFC%20NIFTY200%20Momentum%2030%20Index%20Fund_PPT%20%28July%202026%29.pdf)
- **Taxes and costs in replication:** about 80% of semi-annual momentum gains would be taxed as STCG. Semi-annual rebalancing doubles turnover versus annual. The gross-to-net gap was 1.22 points a year, with 0.11% trade cost plus 0.05% slippage. — [BacktestIndia](https://backtestindia.com/blog/momentum-investing-india-backtest)
- **Monthly rebalancing:** an equal-weighted, long-only, monthly-rebalanced winner portfolio from the top 200 Indian stocks delivered alpha, though "not all implementations of factor strategies are the same." — [Factor Investor report, Jan 2022](https://factorinvestor.substack.com/p/factor-investor-report-jan-2022) (from search snippet)
- **Lookback evidence from academia:** 6-6 momentum was stronger than 12-12 (Sehgal & Jain), and short horizons were more robust after costs (Aggarwal & Gupta). — [Emerald](https://www.emerald.com/insight/content/doi/10.1108/09727981111129327/full/html); [JCAR](https://www.publishingindia.com/archive/jcar/can-small-investors-gain-from-momentum-trading-in-india-an-empirical-investigation)

### Inferences
- **Recommended replicable baseline.** Nifty 200 F&O universe, 6m+12m volatility-scaled scores that skip the latest month, about 30 holdings, rebalanced semi-annually (or quarterly with a strong buffer), using a rank buffer of roughly top 15 in / out beyond 45. Expect about 100–130% one-way annual turnover. At about 0.3% round-trip cost that is roughly 0.3–0.4 points a year in costs, before STCG.
- **Rebalance frequency.** Monthly or quarterly rebalancing is not supported for large/midcap momentum by NSE's own test. Any edge appears only in midcaps and comes with higher churn and tax drag.
- **Weighting.** Equal weight (as in the replication) vs score × market-cap tilt (as in the index) changes the liquidity profile. The liquidity findings in Q2 suggest equal weight earns more from smaller, less liquid names but with more slippage.

### Gaps
- No NSE or academic study was found comparing monthly vs semi-annual rebalance for Indian large/midcap momentum on a net-of-tax basis. Nor was turnover data found for Low Vol 30 or Quality 30.
- No published comparison was found of 20 vs 30 vs 50 holdings for Indian momentum.
