# Live record of Indian momentum and factor ETFs / index funds vs their index back-tests, and DIY momentum vs holding a fund

Compiled 11 Nov 2026. Fund NAV data run to 9 Nov 2026.

**How to read the labels**
- **LIVE** = a real fund's NAV (after costs) or an index after its public launch date.
- **BACKTEST** = index history before the index's launch date (all NSE factor indices have a 1 Apr 2005 base, Alpha 50 Dec 2003, but launched years later; launch dates are in the earlier note).
- **[own computation]** = calculated for these notes from public NAV history ([mfapi.in](https://api.mfapi.in/mf/148703), which mirrors AMFI NAVs) and fund data pages on [Groww](https://groww.in/mutual-funds/uti-nifty200-momentum-30-index-fund-direct-growth). ETF returns use NAV, not traded price, and are adjusted for unit splits. These are not published results.

**What is already established elsewhere and not repeated here:** index methodology, long-run index numbers, academic momentum evidence and drawdowns are in `Evidence based NSE trading strategies/momentum_factor_evidence.md`; survivorship bias and data hygiene are in `mean_reversion_and_backtesting.md` (section 3); Groww costs and tax rates are in `costs_and_taxes.md`.

**Access limits in this session.** niftyindices.com timed out and could not be re-read, so index-level figures (NSE whitepaper Apr 2026, factsheets 30 Sep 2026) are carried over from the earlier note. Capitalmind, PrimeInvestor, Value Research, Morningstar, Weekend Investing, AMC sites, SSRN, NBER, Kaggle, Substack and BacktestIndia were unreachable, and the web-search quota ran out part-way. Nifty 50 TRI and Nifty 200 TRI daily series were not available, so **live index funds are used as proxies**:
- Nifty 50 TRI → UTI Nifty 50 Index Fund, direct ([mfapi 120716](https://api.mfapi.in/mf/120716)); it trailed the TRI by about 0.2 points a year (5y to 30 Sep 2026: 6.14% vs 6.37%).
- Broad market → Motilal Oswal Nifty 500 Index Fund, direct ([mfapi 147625](https://api.mfapi.in/mf/147625)).
- Nifty 200 → calendar-year values implied by NSE's whitepaper, plus an **own proxy** of 85% Axis Nifty 100 Index Fund + 15% Motilal Oswal Nifty Midcap 150 Index Fund. The proxy returned 16.4% against 16.3% for the Groww Nifty 200 ETF over 27 Feb 2025 – 9 Nov 2026, and is within about 0.5 points of the implied Nifty 200 calendar-year figures for 2021–2025.

---

## Q1. Instruments: tickers, AMC, launch date, cost, AUM, tracking difference

### Takeaway
Two tickers in the brief were wrong: **MOMENTUM is Aditya Birla Sun Life's ETF, and MOM30IETF is ICICI Prudential's** (Mirae has no plain Nifty200 Momentum 30 ETF). No "MIDMOMENTUM" ticker exists; the midcap momentum ETFs are MOMIDMTM (Motilal Oswal) and SBIMIDMOM (SBI). The only large, long-lived momentum product is the UTI index fund (₹7,962 cr, live since March 2021). Every momentum ETF is small (₹38–513 cr) and thinly traded. Funds have trailed their index total return by roughly 0.3–0.9 points a year (momentum), 0.5–0.9 (midcap momentum, more in 2023) and about 1.4 (Alpha 50).

### Cited Findings

**Cost figures need care.** Groww now shows two numbers for index funds, "expense ratio" and "base expense ratio" (for example 0.78% and 0.38% for the UTI momentum fund on 9 Nov 2026), and one number for ETFs. — [Groww: UTI Nifty200 Momentum 30](https://groww.in/mutual-funds/uti-nifty200-momentum-30-index-fund-direct-growth). A Kotak factsheet (July 2026) describes its 0.26% figure for the Kotak momentum ETF as a "Base Expense Ratio" excluding brokerage and transaction costs, with a separate total expense ratio published. — [Kotak factsheet, July 2026 (via search summary)](https://www.kotakmf.com/factsheet/July_2026/kotak/Kotak-Nifty200-Momentum-ETF.html)

**Tables.** All rows are LIVE. AUM, expense, turnover, ETF tracking error and launch date are from Groww fund/ETF pages read 11 Nov 2026 (NAV date 9 Nov 2026). The last two columns are [own computation] from mfapi NAVs: (a) fund return minus index total return for the year to 30 Sep 2026, using the index figures from NSE factsheets recorded in the earlier note; (b) CAGR from first NAV to 9 Nov 2026 next to the Nifty 50 and Nifty 500 index funds over identical dates. Sources: [Groww ETF page pattern, e.g. MOM30IETF](https://groww.in/etfs/icici-prudential-nifty-momentum-etf); [Groww fund page pattern](https://groww.in/mutual-funds/hdfc-nifty200-momentum-30-index-fund-direct-growth); [mfapi scheme list](https://api.mfapi.in/mf); index 1-year returns from the [NSE Momentum 30 factsheet](https://www.niftyindices.com/Factsheet/Factsheet_Nifty200_Momentum30.pdf) and sister factsheets as cited in the earlier note.

*Nifty200 Momentum 30*

| Fund | Type / NSE ticker | Launch | AUM ₹ cr | Expense: total / base % | Turnover % | ETF tracking error % | 1y to 30 Sep 2026, fund − index (pp) | CAGR since first NAV: fund / Nifty 50 fund / Nifty 500 fund |
|---|---|---|---|---|---|---|---|---|
| UTI Nifty200 Momentum 30 Index Fund | Index fund, direct | 10 Mar 2021 | 7,961.7 | 0.78 / 0.38 | 62 | — | −0.53 | 14.1 / 10.5 / 12.5 |
| Motilal Oswal Nifty 200 Momentum 30 ETF | ETF **MOMOMENTUM** | 10 Feb 2022 | 111.3 | 0.84 | — | 0.44 | −0.82 | 9.8 / 9.2 / 11.1 |
| Motilal Oswal Nifty 200 Momentum 30 Index Fund | Index fund, direct | 10 Feb 2022 | 881.6 | 0.71 / 0.28 | 36 | — | −0.93 | 9.8 / 9.2 / 11.1 |
| ICICI Prudential Nifty 200 Momentum 30 ETF | ETF **MOM30IETF** | 4 Aug 2022 | 512.7 | 0.70 | — | 0.25 | −0.59 | 13.0 / 9.9 / 12.1 |
| ICICI Prudential Nifty 200 Momentum 30 Index Fund | Index fund, direct | 5 Aug 2022 | 488.9 | 0.67 / 0.27 | 150 | — | −0.65 | 12.2 / 9.7 / 11.9 |
| Aditya Birla Sun Life Nifty 200 Momentum 30 ETF | ETF **MOMENTUM** | 12 Aug 2022 | 37.9 | 0.67 | — | 0.26 | −0.62 | 12.2 / 9.4 / 11.6 |
| Bandhan Nifty200 Momentum 30 Index Fund | Index fund, direct | 2 Sep 2022 | 115.5 | 0.77 / 0.34 | 144 | — | −0.82 | 10.9 / 9.7 / 11.6 |
| HDFC NIFTY200 Momentum 30 ETF | ETF **HDFCMOMENT** | 11 Oct 2022 | 100.0 | 0.30 | — | 0.22 | −0.52 | 12.3 / 11.0 / 13.0 |
| Kotak Nifty 200 Momentum 30 Index Fund | Index fund, direct | 15 Jun 2023 | 562.1 | 0.62 / 0.17 | 169 | — | −0.55 | 11.2 / 9.8 / 12.5 |
| HDFC NIFTY200 Momentum 30 Index Fund | Index fund, direct | 28 Feb 2024 | 568.2 | 0.70 / 0.31 | 144 | — | −0.77 | 0.6 / 6.0 / 7.0 |
| Baroda BNP Paribas Nifty200 Momentum 30 Index Fund | Index fund, direct | 15 Oct 2024 | 20.7 | 0.97 / 0.36 | 206 | — | −1.11 | −10.0 / 1.1 / 0.7 |
| SBI Nifty200 Momentum 30 Index Fund | Index fund, direct | 9 Jul 2025 | 111.3 | 0.80 / 0.34 | 166 | — | −0.81 | −2.1 / 0.5 / 1.3 |
| Kotak Nifty 200 Momentum 30 ETF | ETF **MOMENTUM30** | 10 Oct 2025 | 91.7 | 0.68 | — | 0.27 | n/a | −4.2 / −1.1 / 0.8 |

*Nifty Midcap150 Momentum 50*

| Fund | Type / NSE ticker | Launch | AUM ₹ cr | Expense: total / base % | Turnover % | ETF tracking error % | 1y to 30 Sep 2026, fund − index (pp) | CAGR since first NAV: fund / Nifty 50 fund / Nifty 500 fund |
|---|---|---|---|---|---|---|---|---|
| Tata Nifty Midcap 150 Momentum 50 Index Fund | Index fund, direct | 20 Oct 2022 | 1,205.6 | 0.73 / 0.38 | 106 | — | −0.91 | 15.7 / 9.5 / 11.9 |
| Edelweiss Nifty Midcap150 Momentum 50 Index Fund | Index fund, direct | first NAV 2 Dec 2022 | not retrieved | not retrieved | — | — | −0.53 | 16.4 / 8.7 / 11.2 |
| Kotak Nifty Midcap 150 Momentum 50 Index Fund | Index fund, direct | 8 Oct 2024 | 446.5 | 0.61 / 0.24 | 121 | — | −0.54 | −3.2 / 1.1 / 0.8 |
| Motilal Oswal Nifty Midcap150 Momentum 50 ETF | ETF **MOMIDMTM** | 30 Jun 2025 | 45.3 | 1.02 | — | 0.27 | −0.90 | −1.3 / −0.1 / 1.0 |
| SBI Nifty Midcap 150 Momentum 50 ETF | ETF **SBIMIDMOM** | 2 Mar 2026 | 134.0 | 0.47 | — | n/a | n/a | n/a |

Mirae's **MOMMIDCAP** (16 Jul 2026, ₹105.6 cr, 1.89%) tracks a different index, BSE Midcap 150 Momentum 30. — [Groww](https://groww.in/etfs/mirae-asset-bse-midcap-momentum-etf)

*Nifty500 Momentum 50*

| Fund | Type / NSE ticker | Launch | AUM ₹ cr | Expense: total / base % | Turnover % | ETF tracking error % | Return since first NAV: fund / Nifty 50 fund / Nifty 500 fund |
|---|---|---|---|---|---|---|---|
| Motilal Oswal Nifty 500 Momentum 50 ETF | ETF **MOMENTUM50** | 24 Sep 2024 | 392.6 | 0.88 | — | 0.42 | −8.4 / −0.5 / −0.5 (CAGR) |
| Motilal Oswal Nifty 500 Momentum 50 Index Fund | Index fund, direct | 24 Sep 2024 | 784.8 | 0.74 / 0.36 | 53 | — | −8.2 / −0.5 / −0.5 (CAGR) |
| Nippon India Nifty 500 Momentum 50 Index Fund | Index fund, direct | 30 Sep 2024 | 1,253.6 | 0.60 / 0.21 | 145 | — | −8.1 / −0.5 / −0.6 (CAGR) |
| Bandhan Nifty 500 Momentum 50 Index Fund | Index fund, direct | 29 Oct 2024 | 41.6 | 0.77 / 0.31 | 162 | — | −5.2 / 2.4 / 2.6 (CAGR) |
| Axis Nifty500 Momentum 50 Index Fund | Index fund, direct | 13 Feb 2025 | 171.6 | 0.53 / 0.15 | — | — | 8.2 / 6.2 / 9.0 (CAGR) |
| Groww Nifty 500 Momentum 50 ETF | ETF **GROWWMOM50** | 23 Apr 2025 | 29.4 | 0.81 | — | 0.27 | 3.9 / 3.0 / 4.8 (CAGR) |
| Kotak Nifty500 Momentum 50 Index Fund | Index fund, direct | 11 Dec 2025 | 26.5 | 0.62 / 0.16 | 152 | — | 2.1 / −2.2 / 1.1 (absolute) |

*Nifty Alpha 50 and Nifty Alpha Low-Volatility 30*

| Fund | Type / NSE ticker | Launch | AUM ₹ cr | Expense: total / base % | Turnover % | ETF tracking error % | 1y to 30 Sep 2026, fund − index (pp) | CAGR since first NAV: fund / Nifty 50 fund / Nifty 500 fund |
|---|---|---|---|---|---|---|---|---|
| Kotak Nifty Alpha 50 ETF | ETF **ALPHA** | 22 Dec 2021 | 880.6 | 0.71 | — | 0.80 | −1.46 | 8.3 / 9.1 / 10.7 |
| Bandhan Nifty Alpha 50 Index Fund | Index fund, direct | 9 Nov 2023 | 598.0 | 0.72 / 0.31 | 152 | — | −1.38 | 11.2 / 9.9 / 11.7 |
| Motilal Oswal Nifty Alpha 50 ETF | ETF **MOALPHA50** | 7 Jul 2025 | 3.3 | 1.03 | — | 0.62 | −1.63 | −0.8 / 0.0 / 1.2 |
| Kotak Nifty Alpha 50 Index Fund | Index fund, direct | 19 Aug 2025 | 55.4 | 1.01 / 0.30 | 158 | — | −1.92 | 1.5 / 1.4 / 2.8 |
| ICICI Prudential Nifty Alpha Low-Volatility 30 ETF | ETF **ALPL30IETF** | 12 Aug 2020 | 1,448.6 | 0.57 | — | 0.14 | −0.58 | 14.6 / 14.7 / 16.7 |
| Nippon India Nifty Alpha Low Volatility 30 Index Fund | Index fund, direct | 19 Aug 2022 | 1,169.3 | 0.56 / 0.30 | 80 | — | −0.59 | 12.1 / 9.8 / 12.0 |
| Edelweiss Nifty Alpha Low Volatility 30 Index Fund | Index fund, direct | 17 May 2024 | 79.9 | 0.54 / 0.28 | 72 | — | −0.68 | −0.3 / 5.4 / 5.3 |
| UTI Nifty Alpha Low-Volatility 30 Index Fund | Index fund, direct | 28 Nov 2024 | 63.4 | 0.76 / 0.51 | 86 | — | −0.77 | −2.7 / 2.2 / 2.1 |
| Bandhan Nifty Alpha Low Volatility 30 Index Fund | Index fund, direct | 23 Jan 2025 | 9.2 | 0.51 / 0.24 | 144 | — | −0.59 | 1.6 / 5.7 / 6.7 |
| Kotak Nifty Alpha Low Volatility 30 Index Fund | Index fund, direct | 17 Jun 2026 | 7.2 | 0.84 / 0.20 | 31 | — | n/a | n/a |

Related: Mirae Asset Nifty 200 Alpha 30 ETF **ALPHAETF** (20 Oct 2023, ₹388.4 cr, 0.78%, tracking error 0.40%); Tata Nifty200 Alpha 30 Index Fund (5 Sep 2024, ₹199.0 cr, 0.78 / 0.39, turnover 168%). — [Groww ALPHAETF](https://groww.in/etfs/mirae-asset-nifty-alpha-etf)

*Low volatility and quality (comparison)*

| Fund | Type / NSE ticker | Launch | AUM ₹ cr | Expense: total / base % | Turnover % | ETF tracking error % | 1y to 30 Sep 2026, fund − index (pp) | CAGR since first NAV: fund / Nifty 50 fund / Nifty 500 fund |
|---|---|---|---|---|---|---|---|---|
| ICICI Prudential Nifty 100 Low Volatility 30 ETF | ETF **LOWVOLIETF** | 4 Jul 2017 | 3,111.3 | 0.52 | — | 0.15 | −0.52 | 12.3 / 11.8 / n/a (NAV history from 3 Jul 2018) |
| Kotak Nifty 100 Low Volatility 30 ETF | ETF **LOWVOL1** | 23 Mar 2022 | 252.9 | 0.25 | — | 0.07 | −0.03 | 12.2 / 9.4 / 11.5 |
| Bandhan Nifty100 Low Volatility 30 Index Fund | Index fund, direct | 6 Oct 2022 | 1,444.3 | 0.49 / 0.30 | 45 | — | −0.48 | 12.2 / 10.4 / 12.4 |
| HDFC NIFTY100 Low Volatility 30 ETF | ETF **HDFCLOWVOL** | 11 Oct 2022 | 12.0 | 0.35 | — | 0.04 | −0.35 | 13.1 / 11.0 / 13.0 |
| Mirae Asset Nifty 100 Low Volatility 30 ETF | ETF **LOWVOL** | 24 Mar 2023 | 40.7 | 0.48 | — | 0.07 | −0.39 | 14.4 / 12.4 / 15.7 |
| Kotak / HDFC / SBI Nifty100 Low Volatility 30 Index Funds | Index funds, direct | Jun 2024 / Jul 2024 / Jul 2025 | 102.2 / 198.8 / 51.9 | 0.39/0.17, 0.52/0.34, 0.51/0.33 | 71 / 32 / 35 | — | n/a | n/a |
| SBI Nifty 200 Quality 30 ETF | ETF **SBIQUALITY** | 10 Dec 2018 | 77.5 | 0.33 | — | 0.05 | n/a | NAV history not on mfapi |
| Aditya Birla Sun Life Nifty 200 Quality 30 ETF | ETF **NIFTYQLITY** | 12 Aug 2022 | 22.5 | 0.33 | — | 0.07 | −0.24 | 8.5 / 9.4 / 11.6 |
| ICICI Prudential Nifty 200 Quality 30 ETF | ETF **QUAL30IETF** | 7 Aug 2023 | 129.3 | 0.34 | — | 0.04 | −0.31 | 8.1 / 8.9 / 11.4 |
| UTI Nifty200 Quality 30 Index Fund | Index fund, direct | 20 Sep 2024 | 500.1 | 0.65 / 0.48 | 28 | — | −0.47 | −6.3 / −0.7 / −0.8 |
| Kotak Nifty200 Quality 30 ETF | ETF **QUALITY30** | 14 Jul 2025 | 3.0 | 0.31 | — | 0.09 | n/a | n/a |
| SBI / ICICI / Bandhan / Kotak Nifty200 Quality 30 Index Funds | Index funds, direct | Jun 2025 / Jun 2025 / Dec 2024 / Jul 2025 | 306.8 / 24.9 / 16.1 / 16.4 | 0.42/0.29, 0.47/0.33, 0.53/0.31, 0.33/0.18 | 32 / 30 / 40 / 31 | — | n/a | n/a |

*Value and multi-factor (comparison)*

| Fund | Type / NSE ticker | Launch | AUM ₹ cr | Expense: total / base % | CAGR since first NAV: fund / Nifty 50 fund / Nifty 500 fund |
|---|---|---|---|---|---|
| Kotak Nifty 50 Value 20 ETF | ETF **NV20** | 8 Dec 2015 | 75.2 | 0.35 | 14.0 / 12.5 / n/a |
| ICICI Prudential Nifty50 Value 20 ETF | ETF **NV20IETF** | 20 Jun 2016 | 172.1 | 0.44 | n/a |
| Nippon India Nifty 50 Value 20 Index Fund | Index fund, direct | 19 Feb 2021 | 707.9 | 0.52 / 0.21 | 11.5 / 10.8 / 12.9 |
| UTI Nifty 500 Value 50 Index Fund | Index fund, direct | 10 May 2023 | 838.0 | 0.71 / 0.49 | 25.3 / 10.5 / 13.7 |
| ICICI Prudential Nifty200 Value 30 ETF | ETF **VAL30IETF** | 17 Oct 2024 | 45.7 | 0.38 | 4.7 / 1.3 / 1.1 |
| Edelweiss Nifty500 Multicap Momentum Quality 50 ETF / Index Fund | ETF **EMULTIMQ** / index fund | 31 Oct 2024 | 29.8 / 602.2 | 0.73 ; 0.68 / 0.34 | −5.7 / 2.7 / 2.8 (ETF) |
| Mirae Asset Nifty Smallcap 250 Momentum Quality 100 ETF | ETF **SMALLCAP** | 23 Feb 2024 | 932.4 | 0.73 | n/a |
| Mirae Asset Nifty MidSmallcap400 Momentum Quality 100 ETF | ETF **MIDSMALL** | 22 May 2024 | 464.0 | 0.64 | n/a |
| Mirae Asset Nifty200 Momentum 30 Plus 8-13 yr G-Sec 50:50 ETF | ETF **HYBRIDETF** | 27 Jul 2026 | 15.0 | 0.54 | too new |

Also listed on Groww: Axis Nifty500 Value 50 ETF (VALUEAXIS), Mirae Nifty 500 Value 50 ETF (VALUE), SBI Nifty200 Value 30 ETF (SBIVALETF), HDFC NIFTY50 Value 20 ETF (HDFCVALUE), HDFC NIFTY100 Quality 30 ETF (HDFCQUAL), Groww Nifty 500 Low Volatility 50 ETF (GROWWLOVOL), Angel One Nifty Total Market Momentum Quality 50 ETF (AONETMMQ50), Groww Nifty 200 ETF (GROWWN200, the only plain Nifty 200 fund, 27 Feb 2025, ₹15.7 cr). — [Groww search API results](https://groww.in/etfs/groww-nifty-etf)

**ETF liquidity (LIVE, one-session snapshot around 10–11 Nov 2026; NSE volume × NAV, possibly a partial session).** MOM30IETF ≈ ₹3.8 cr; MOMENTUM50 ≈ ₹2.9 cr; HDFCMOMENT ≈ ₹1.6 cr; MOMENTUM30 ≈ ₹1.2 cr; MOMOMENTUM ≈ ₹0.4 cr; MOMENTUM (ABSL) ≈ ₹0.24 cr; SBIMIDMOM ≈ ₹0.45 cr; MOMIDMTM ≈ ₹0.18 cr; ALPHA ≈ ₹7.7 cr; ALPL30IETF ≈ ₹0.85 cr; LOWVOLIETF ≈ ₹9.9 cr; every quality ETF under ₹0.15 cr. [own computation] from [Groww ETF pages](https://groww.in/etfs/hdfc-nifty-momentum-etf)

**Calendar-year tracking difference vs index (LIVE fund minus index; [own computation]).** Index calendar-year returns are from NSE whitepaper Exhibit 7 as recorded in the earlier note; the exhibit does not say whether it is price or total return, so treat these as approximate.

| Fund | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|
| UTI Momentum 30 index fund | −0.02 | −0.34 | −0.03 | −0.52 |
| Motilal Oswal Momentum 30 index fund / ETF | — | −0.55 / −0.52 | −0.48 / −0.52 | −0.89 / −0.87 |
| ICICI Momentum 30 index fund / ETF | — | −1.53 / −0.87 | −0.88 / −0.77 | −0.71 / −0.51 |
| ABSL Momentum 30 ETF | — | −0.46 | −0.65 | −0.60 |
| Bandhan Momentum 30 index fund | — | −1.53 | −1.04 | −0.83 |
| HDFC Momentum 30 ETF | — | −0.86 | −0.69 | −0.42 |
| Kotak Momentum 30 index fund | — | — | −0.29 | −0.18 |
| Tata Midcap150 Momentum 50 index fund | — | −2.64 | −1.41 | −0.74 |
| Edelweiss Midcap150 Momentum 50 index fund | — | −2.15 | −0.31 | −0.77 |

Sources: fund NAVs from [mfapi](https://api.mfapi.in/mf/150738); index years from the [NSE whitepaper, Apr 2026, Exhibit 7](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf).

- UTI's fund returned 8.98% a year over the 5 years to 30 Sep 2026 against 9.28% for the index total return: a tracking difference of −0.30 points a year. ICICI's Alpha Low-Vol 30 ETF returned 7.95% against 8.57% (−0.62). ICICI's Low Vol 30 ETF returned 7.59% against 8.12% (−0.53). [own computation] — [mfapi 148703](https://api.mfapi.in/mf/148703); [mfapi 148456](https://api.mfapi.in/mf/148456); [mfapi 141596](https://api.mfapi.in/mf/141596); index figures from the [NSE factsheets, 30 Sep 2026](https://www.niftyindices.com/Factsheet/Factsheet_Nifty200_Momentum30.pdf)
- NSE reported 1-year tracking errors of 0.17% (UTI, HDFC ETF) to 0.52% (Motilal index fund) for Momentum 30 funds as of 27 Feb 2026. — [NSE whitepaper, Exhibit 12](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf) (from the earlier note)
- A third-party page listed lower ETF expense ratios in the first half of 2026: Kotak 0.24%, ABSL 0.29%, Motilal 0.30–0.32%, HDFC 0.30%, ICICI 0.30%. — [Choice India](https://choiceindia.com/mutual-funds/kotak-nifty-200-momentum-30-etf-growth-140519562-2066); [Tickertape](https://www.tickertape.in/etfs/aditya-birla-sun-life-nifty-200-momentum-30-etf-MOME); [Business Today](https://www.businesstoday.in/mutual-funds/motilal-oswal-nifty-200-momentum-30-etf-detail-page-5891) (search summaries)

### Inferences
- Groww's larger "expense ratio" number probably adds brokerage and statutory levies to the base ratio under the 2026 disclosure format. That fits the observed tracking differences (0.3–0.9 points) better than the old 0.3–0.5% headline TERs do. Not confirmed against an AMC document.
- For someone buying and holding ₹1–20 lakh, a direct-plan index fund (UTI, Kotak, ICICI, HDFC for Momentum 30) avoids the two ETF frictions: thin order books (₹0.2–4 cr a day) and brokerage plus DP charges. HDFCMOMENT shows the lowest listed ETF cost (0.30%); MOM30IETF is the most traded.
- Reported fund turnover varies from 36% to 206% for the same index. AMCs compute it differently and flows distort it, so it is not a clean measure of index churn.
- Alpha 50 funds lose noticeably more to implementation (about 1.4–1.9 points in the last year) than Momentum 30 funds, consistent with quarterly rebalancing in a 300-stock universe.

### Gaps
- Tracking difference **since each fund's launch** could not be computed because index TRI history was unreachable. Only calendar-year and trailing-period comparisons are given.
- TER figures were not confirmed on AMC factsheets or AMFI. The split between base and total expense is an inference.
- Edelweiss Midcap150 Momentum 50 fund AUM and cost, and ETF premium/discount to NAV and bid-ask spreads, were not retrieved.
- No Bandhan or Zerodha momentum ETF and no Nippon Alpha Low-Vol 30 ETF were found on Groww; absence from one platform's search is not proof they do not exist.

---

## Q2. Calendar-year returns and since-launch CAGR of the oldest live fund in each family

### Takeaway
The oldest momentum fund (UTI, March 2021) has returned 14.1% a year against 10.5% for a Nifty 50 index fund and about 12.0–12.5% for the broad market, but all of that lead was earned before September 2024 and three of its last five calendar periods lagged the Nifty 200. A plain Nifty Next 50 fund (14.5%) matched it and a plain Midcap 150 fund (17.6%) beat it over the same dates, and over the latest five years the momentum fund (7.9%) is level with the Nifty 50 fund (7.8%). Alpha 50, Alpha Low-Vol 30 and Quality 30 funds have **not** beaten a broad index fund since they launched.

### Cited Findings

**LIVE fund NAV returns (%), [own computation] from mfapi NAVs; 2026 is year-to-date to 9 Nov 2026.**

| Fund (first NAV) | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 YTD | CAGR since first NAV | Nifty 50 fund, same dates | Nifty 500 fund, same dates |
|---|---|---|---|---|---|---|---|---|---|
| UTI Nifty200 Momentum 30 Index Fund (12 Mar 2021) | 40.8 from 12 Mar | −5.5 | 41.4 | 21.3 | −5.1 | −2.4 | 14.14 | 10.50 | 12.46 |
| Tata Nifty Midcap150 Momentum 50 Index Fund (31 Oct 2022) | — | −5.2 from 31 Oct | 49.8 | 30.9 | −4.2 | 1.0 | 15.72 | 9.52 | 11.85 |
| Motilal Oswal Nifty 500 Momentum 50 Index Fund (30 Sep 2024) | — | — | — | −10.5 from 30 Sep | −8.4 | 1.8 | −8.20 | −0.48 | −0.50 |
| Kotak Nifty Alpha 50 ETF (29 Dec 2021) | — | −16.6 | 41.8 | 32.4 | −10.8 | 4.4 | 8.31 | 9.06 | 10.73 |
| ICICI Pru Nifty Alpha Low-Vol 30 ETF (13 Aug 2020) | 30.2 | −3.6 | 38.2 | 17.0 | −0.3 | −1.5 | 14.55 | 14.68 | 16.73 |
| ICICI Pru Nifty 100 Low Vol 30 ETF (NAV from 3 Jul 2018) | 23.6 | 1.5 | 31.2 | 11.8 | 10.9 | −3.6 | 12.27 | 11.76 | n/a |
| ABSL Nifty 200 Quality 30 ETF (19 Aug 2022) | — | −3.6 from 19 Aug | 31.0 | 14.2 | 4.4 | −6.1 | 8.53 | 9.43 | 11.59 |
| Nippon India ETF Nifty 50 Value 20 (19 Jun 2015) | 36.5 | 1.3 | 29.2 | 17.4 | 0.7 | −6.6 | 12.65 | 11.33 | n/a |
| UTI Nifty 500 Value 50 Index Fund (12 May 2023) | — | — | 55.5 from 12 May | 19.9 | 16.3 | 1.4 | 25.28 | 10.49 | 13.65 |
| Mirae Nifty 200 Alpha 30 ETF (23 Oct 2023) | — | — | 25.1 from 23 Oct | 26.7 | −5.5 | 5.4 | 16.18 | 10.00 | 12.35 |
| **Benchmarks** | | | | | | | | | |
| UTI Nifty 50 Index Fund (Nifty 50 TRI proxy) | 25.3 | 5.4 | 21.0 | 9.8 | 11.7 | −3.3 | — | — | — |
| Nifty 200, implied by NSE whitepaper (index, not a fund) | 28.9 | 4.9 | 24.7 | 14.8 | 9.6 | −1.4 (Groww Nifty 200 ETF) | — | — | — |
| Motilal Oswal Nifty 500 Index Fund | 30.6 | 3.8 | 26.5 | 15.6 | 7.7 | −0.5 | — | — | — |
| UTI Nifty Next 50 Index Fund | 30.3 | 0.6 | 26.8 | 27.9 | 2.6 | 5.6 | — | — | — |
| Motilal Oswal Nifty Midcap 150 Index Fund | 46.9 | 3.6 | 44.3 | 24.2 | 5.8 | 1.1 | — | — | — |

Sources: NAV histories at [mfapi 148703](https://api.mfapi.in/mf/148703), [150738](https://api.mfapi.in/mf/150738), [152875](https://api.mfapi.in/mf/152875), [149397](https://api.mfapi.in/mf/149397), [148456](https://api.mfapi.in/mf/148456), [141596](https://api.mfapi.in/mf/141596), [150497](https://api.mfapi.in/mf/150497), [134782](https://api.mfapi.in/mf/134782), [151739](https://api.mfapi.in/mf/151739), [152134](https://api.mfapi.in/mf/152134), [120716](https://api.mfapi.in/mf/120716), [147625](https://api.mfapi.in/mf/147625), [143341](https://api.mfapi.in/mf/143341), [147622](https://api.mfapi.in/mf/147622), [153329](https://api.mfapi.in/mf/153329); Nifty 200 implied from the [NSE whitepaper, Exhibit 7](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf).

- **UTI momentum fund against other plain funds over identical dates (12 Mar 2021 – 9 Nov 2026, LIVE, [own computation]):** momentum 14.14%; Nifty 50 fund 10.50%; Nifty 200 proxy 12.01%; Nifty 500 fund 12.46%; Nifty Next 50 fund 14.47%; Midcap 150 fund 17.64%. A daily-rebalanced blend of 52% Nifty 100 fund and 48% Midcap 150 fund, matching the index's size mix, returned 14.23%. — [mfapi 148703](https://api.mfapi.in/mf/148703); [147666](https://api.mfapi.in/mf/147666); [147622](https://api.mfapi.in/mf/147622); size mix from [HDFC AMC presentation, July 2026](https://files.hdfcfund.com/s3fs-public/Others/2026-07/HDFC%20NIFTY200%20Momentum%2030%20Index%20Fund_PPT%20%28July%202026%29.pdf)
- **Split at the September 2024 peak (LIVE, [own computation]):**

  | Period | UTI Momentum 30 | Nifty 50 fund | Nifty 500 fund | Next 50 fund | Midcap 150 fund |
  |---|---|---|---|---|---|
  | 12 Mar 2021 – 27 Sep 2024 | 31.5% a year | 18.1% | 21.3% | 26.0% | 29.2% |
  | 27 Sep 2024 – 9 Nov 2026 | −10.0% a year | −1.1% | −1.0% | −2.5% | +0.5% |

  — [mfapi 148703](https://api.mfapi.in/mf/148703)
- **Midcap momentum against its own parent (LIVE, [own computation]):** Tata Nifty Midcap150 Momentum 50 Index Fund returned 15.72% a year from 31 Oct 2022 to 9 Nov 2026; the plain Motilal Oswal Nifty Midcap 150 Index Fund returned 17.59% over the same dates. By year (momentum vs parent): 2023 49.8 vs 44.3; 2024 30.9 vs 24.2; 2025 −4.2 vs +5.8; 2026 YTD 1.0 vs 1.1. — [mfapi 150738](https://api.mfapi.in/mf/150738); [mfapi 147622](https://api.mfapi.in/mf/147622)
- **Trailing returns to 9 Nov 2026 (LIVE, [own computation], cross-checked with Groww's displayed figures):**

  | Period | UTI Momentum 30 | Nifty 50 fund | Nifty 500 fund | Next 50 fund | Midcap 150 fund |
  |---|---|---|---|---|---|
  | 3 years | 9.38% | 9.90% | 11.80% | 17.41% | 14.43% |
  | 5 years | 7.89% | 7.79% | 9.45% | 11.26% | 13.82% |

  Groww shows the same fund at 1-year −3.43%, 3-year 9.37%, 5-year 7.88%, since launch 14.01%, standard deviation 20.13, beta 1.19; and UTI Nifty 50 at 1-year −0.92%, 3-year 9.9%, 5-year 7.79%. — [Groww](https://groww.in/mutual-funds/uti-nifty200-momentum-30-index-fund-direct-growth); [mfapi 148703](https://api.mfapi.in/mf/148703)
- Live fund-life volatility and maximum drawdown (LIVE, [own computation]): UTI Momentum 30 19.2% and −31.5% (7 Apr 2025); Kotak Alpha 50 ETF 21.7% and −33.5% (27 Feb 2023); Tata Midcap150 Momentum 50 18.2% and −25.9%; ICICI Alpha Low-Vol 30 ETF 13.5% and −25.0%; ICICI Low Vol 30 ETF 14.3% and −30.5% (23 Mar 2020); ABSL Quality 30 ETF 12.7% and −22.5%; UTI Nifty 50 fund 16.0% and −38.4% (since 2013). — [mfapi](https://api.mfapi.in/mf/149397)

### Inferences
- Since launch, the UTI momentum fund's 14.1% is almost exactly what a size-matched blend of plain large-cap and midcap index funds earned (14.2%). On live data to date, the momentum fund's lead over the Nifty 50 is explained by its midcap tilt, not by stock selection.
- The live "since launch" number is very sensitive to the end date. To 27 Sep 2024 the fund led the Nifty 50 fund by 13 points a year; since then it has lagged by 9 points a year. Over the latest 5 years the momentum fund and the Nifty 50 fund are level (7.9% vs 7.8%) and over 3 years momentum is behind; the 14.1% since-launch figure owes most of its lead to the fund's first nine months (+40.8% from 12 Mar to 31 Dec 2021, against +16.4% for the Nifty 50 fund).
- The earlier note recorded a 5-year lead of about 2.9 points a year over the Nifty 50 TRI at 30 Sep 2026 (9.28% vs 6.37%); the fund data agree for that date (8.98% vs 6.14%). Six weeks later, at 9 Nov 2026, the 5-year lead is about 0.1 points. Two things changed: the window's start moved past 30 Sep – 9 Nov 2021, when the momentum fund gained 8.0% against 2.5% for the Nifty 50 fund, and its end took in 30 Sep – 9 Nov 2026, when the Nifty 50 fund gained 10.8% against 2.7% for momentum ([own computation]). Trailing-period comparisons of this fund should not be read without checking neighbouring dates.
- Nifty500 Momentum 50 funds launched within days of the September 2024 peak and are still about 16–17% below their starting NAV after two years: a clear case of product launches following back-tested and recent performance.

### Gaps
- No true Nifty 50 TRI or Nifty 200 TRI daily series; fund proxies understate the index by the fund's cost (about 0.2 points a year for the Nifty 50 fund).
- SBI Nifty 200 Quality 30 ETF (December 2018), the oldest quality-30 fund, has no NAV history on mfapi, so quality's live record here starts August 2022.
- 2021 returns for funds that did not exist for the full year are partial and not comparable across rows.

---

## Q3. The 2024–25 momentum slump: depth, duration, recovery

### Takeaway
Measured on live fund NAVs, Momentum 30 peaked on 27 Sep 2024, bottomed on 7 Apr 2025 at −31.5%, and on 9 Nov 2026 was still 20% below its peak, 773 days later. The Nifty 50 fund fell 15.5% and regained its high in October 2025. The worst rolling one-year lag against the broad market was about −19 to −21 points (late May 2025), and the fund's relative performance has been below its June 2024 high for about 29 months and counting.

### Cited Findings

**Peak-to-trough on LIVE fund NAVs ([own computation]; peak = highest NAV between June and December 2024).**

| Fund | Peak | Trough | Drawdown | Days to trough | Recovered prior high? | Level on 9 Nov 2026 vs peak |
|---|---|---|---|---|---|---|
| UTI Nifty200 Momentum 30 | 27 Sep 2024 | 7 Apr 2025 | −31.5% | 192 | Not yet (773 days) | −20.0% |
| Tata Midcap150 Momentum 50 | 24 Sep 2024 | 13 Mar 2025 | −25.9% | 170 | Not yet (776 days) | −9.1% |
| Kotak Alpha 50 ETF | 24 Sep 2024 | 3 Mar 2025 | −31.5% | 160 | Not yet | −15.1% |
| Mirae Nifty 200 Alpha 30 ETF | 30 Aug 2024 | 28 Feb 2025 | −30.0% | 182 | Not yet | −10.8% |
| ICICI Alpha Low-Vol 30 ETF | 27 Sep 2024 | 28 Feb 2025 | −25.0% | 154 | Not yet | −15.1% |
| ABSL Nifty 200 Quality 30 ETF | 27 Sep 2024 | 4 Mar 2025 | −22.5% | 158 | Not yet | −13.0% |
| ICICI Low Vol 30 ETF | 27 Sep 2024 | 4 Mar 2025 | −18.2% | 158 | Not yet | −5.3% |
| Nippon Nifty 50 Value 20 ETF | 26 Sep 2024 | 8 Oct 2026 | −22.6% | 742 | Not yet | −13.2% |
| UTI Nifty 500 Value 50 | 31 Jul 2024 | 28 Feb 2025 | −22.6% | 212 | Yes, 31 Dec 2025 (518 days) | −7.4% vs Feb 2026 high |
| UTI Nifty 50 fund | 26 Sep 2024 | 4 Mar 2025 | −15.5% | 159 | Yes, 27 Oct 2025 (396 days) | −4.1% vs Jan 2026 high |
| Nifty 200 proxy (85% Nifty 100 + 15% Midcap 150 funds) | 26 Sep 2024 | 28 Feb 2025 | −17.7% | 155 | Yes, 2 Jan 2026 | −2.2% |
| Motilal Oswal Nifty 500 fund | 26 Sep 2024 | 28 Feb 2025 | −18.6% | 155 | Not yet | −2.1% |
| Motilal Oswal Midcap 150 fund | 24 Sep 2024 | 28 Feb 2025 | −21.0% | 157 | Yes, 17 Nov 2025 | +0.5% |
| UTI Nifty Next 50 fund | 27 Sep 2024 | 28 Feb 2025 | −26.5% | 154 | Not yet | −5.2% |

Sources: [mfapi 148703](https://api.mfapi.in/mf/148703), [150738](https://api.mfapi.in/mf/150738), [149397](https://api.mfapi.in/mf/149397), [148456](https://api.mfapi.in/mf/148456), [141596](https://api.mfapi.in/mf/141596), [120716](https://api.mfapi.in/mf/120716), [147625](https://api.mfapi.in/mf/147625), [147622](https://api.mfapi.in/mf/147622), [143341](https://api.mfapi.in/mf/143341).

- **Same-window comparison (LIVE, [own computation]):** from 27 Sep 2024 to 7 Apr 2025 the UTI momentum fund fell 31.5%, the Nifty 50 fund 15.1% and the Nifty 500 fund 17.6%. From 27 Sep 2024 to 9 Nov 2026: momentum −20.0%, Nifty 50 fund −2.4%, Nifty 500 fund −2.0%, Midcap150 Momentum 50 −8.0%. — [mfapi 148703](https://api.mfapi.in/mf/148703)
- **Rolling one-year excess return (LIVE, 365-day windows, [own computation]):**

  | Fund vs benchmark | Worst (date) | Best (date) | Latest, 9 Nov 2026 | Share of windows negative | Longest negative run |
  |---|---|---|---|---|---|
  | UTI Momentum 30 vs Nifty 50 fund | −21.5 pp (21 May 2025) | +49.5 pp (21 May 2024) | −2.5 pp | 47% | 21 Jan 2025 – 24 Feb 2026 (399 days) |
  | UTI Momentum 30 vs Nifty 200 proxy | −19.6 pp (29 May 2025) | +39.1 pp (21 May 2024) | −4.0 pp | 54% | 17 Jan 2025 – 9 Mar 2026 (416 days); earlier 2 May 2022 – 15 May 2023 (378 days) |
  | UTI Momentum 30 vs Nifty 500 fund | −19.3 pp (29 May 2025) | +36.3 pp | −4.4 pp | 58% | 17 Jan 2025 – 9 Mar 2026 (416 days) |
  | Tata Midcap150 Momentum 50 vs Midcap 150 fund | −10.8 pp (17 Dec 2025) | +19.4 pp (3 Jun 2024) | −2.1 pp | 62% | 21 Jan 2025 – 9 Nov 2026, ongoing (657 days) |
  | Tata Midcap150 Momentum 50 vs Nifty 50 fund | −17.2 pp (17 Dec 2025) | +53.6 pp | +1.1 pp | 34% | 20 Mar 2025 – 10 Feb 2026 (327 days) |
  | Kotak Alpha 50 ETF vs Nifty 50 fund | −31.2 pp (11 Apr 2023) | +60.9 pp | +3.1 pp | 44% | 24 Jan 2025 – 16 Feb 2026 (388 days) |

  — [mfapi 148703](https://api.mfapi.in/mf/148703); [150738](https://api.mfapi.in/mf/150738); [149397](https://api.mfapi.in/mf/149397)
- **Relative-strength drawdown (fund ÷ benchmark, LIVE, [own computation]):** the UTI momentum fund's ratio to the Nifty 200 proxy peaked on 14 Jun 2024 and on 9 Nov 2026 stood 21.9% below that high (low point −22.5% on 6 Nov 2026). Against the Nifty 50 fund the low was −24.0% (9 Apr 2025) and it is now −22.5%. Tata Midcap150 Momentum 50 against the Midcap 150 fund peaked 3 Jun 2024 and is 12.6% below (low −15.5%, 7 Jul 2026). — [mfapi 148703](https://api.mfapi.in/mf/148703); [150738](https://api.mfapi.in/mf/150738)
- Index-level context from the earlier note: Momentum 30's calendar 2025 return was −4.57% against about +9.6% for the Nifty 200 (excess −14.13 points), and its 1-year total return at 30 Sep 2026 was −0.47%. — [NSE whitepaper, Exhibit 7](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf); [NSE factsheet](https://www.niftyindices.com/Factsheet/Factsheet_Nifty200_Momentum30.pdf)

### Inferences
- The live drawdown (−31.5%) confirms the earlier note's 27–29% blog and price-range estimates and gives exact dates. The trough came on 7 Apr 2025, about five weeks after the broad market's low (28 Feb – 4 Mar 2025): momentum kept falling while the market was already turning.
- The absolute loss was about twice the market's. The more durable damage is relative: the broad market regained its highs within 13–15 months, while momentum has not participated in the recovery and is still roughly 22% behind in relative terms.
- This is the live fund's worst episode, but not unusual against the back-test: the back-tested index spent about six years (end-2007 to end-2013) behind the Nifty 200 on a cumulative basis (see Q5).
- Every factor fund fell further than the Nifty 50 in this episode, including low volatility (−18.2%) and quality (−22.5%). Neither acted as a cushion.

### Gaps
- Peak and trough dates are for fund NAVs. The index TRI dates should match within a day, but index values were not available to confirm.
- Rolling excess against the true Nifty 200 TRI is approximated by a proxy.
- Press coverage of the slump (ET, Mint, Moneycontrol, Business Standard) could not be opened in this session.

---

## Q4. Live vs back-test for each index

### Takeaway
For Nifty200 Momentum 30 the back-tested lead over the Nifty 200 was about 5.6 points a year (calendar 2006–2019); the live lead is about 2.8 points for 2021–2025, about 2.1 points including 2026 to date, and **negative** (−1.6 points a year) if the single year 2021 is excluded. Midcap150 Momentum 50 and Alpha 50 funds have lagged plain alternatives since their funds launched, and Alpha Low-Vol 30 has merely matched the Nifty 50 over six years. Live results have been consistently weaker than the back-tests, though none of the live periods is long enough to be conclusive.

### Cited Findings

**Nifty200 Momentum 30 (index launched 25 Aug 2020) — [own computation] from NSE's calendar-year table.**

| Period | Label | Momentum 30 CAGR | Nifty 200 CAGR | Gap (pp a year) | Years ahead |
|---|---|---|---|---|---|
| 2006–2019 | BACKTEST | 17.53% | 11.94% | +5.59 | 11 of 14 |
| 2010–2019 | BACKTEST | 17.22% | 9.96% | +7.25 | 9 of 10 |
| 2020 | launch year, mixed | 19.95% | 16.82% | +3.13 | — |
| 2021–2025 | LIVE | 19.00% | 16.21% | +2.79 | 3 of 5 |
| 2022–2025 | LIVE | 11.60% | 13.24% | −1.63 | 2 of 4 |
| 1 Jan 2021 – 9 Nov 2026 (index years + UTI fund and Groww Nifty 200 ETF for 2026) | LIVE | 15.5% | 13.4% | +2.1 | 3 of 6 |

Inputs: [NSE whitepaper, Apr 2026, Exhibit 7](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf) (as recorded in the earlier note); 2026 from [mfapi 148703](https://api.mfapi.in/mf/148703) and [153329](https://api.mfapi.in/mf/153329).

- Live years: 2021 +24.9 points, 2022 −10.4, 2023 +17.1, 2024 +6.6, 2025 −14.1 against the Nifty 200. — [NSE whitepaper, Exhibit 7](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf)
- LIVE fund check: UTI's fund returned 14.14% a year against 12.01% for the Nifty 200 proxy from 12 Mar 2021 to 9 Nov 2026, a lead of about 2.1 points. [own computation] — [mfapi 148703](https://api.mfapi.in/mf/148703)
- NSE's own since-inception figure (to 27 Feb 2026) is 19.19% against 15.08% for the Nifty 200, and it blends 15 back-tested years with about 5.5 live years. — [NSE whitepaper, Exhibits 3–4b](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf)

**Nifty Midcap150 Momentum 50 (index launched 16 Aug 2022).**
- BACKTEST: 23.00% a year since April 2005 against 17.24% for the Nifty Midcap 150 (to 27 Feb 2026), a gap of about 5.8 points. — [NSE whitepaper](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf)
- LIVE: the oldest fund (Tata, 31 Oct 2022 – 9 Nov 2026) returned 15.72% against 17.59% for a plain Midcap 150 index fund, a gap of −1.9 points a year. Index excess in the live calendar years: 2023 +7.87, 2024 +7.83, 2025 −9.45. [own computation] — [mfapi 150738](https://api.mfapi.in/mf/150738); [147622](https://api.mfapi.in/mf/147622); [NSE whitepaper, Exhibit 7](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf)
- Freefincal's launch review (October 2022) recommended against the Tata fund, noting the index "has no trading history" and "will underperform the Nifty Midcap 150 index for several months from time to time", which "can persist even over 5Y". — [Freefincal](https://freefincal.com/tata-nifty-midcap-150-momentum-50-index-fund-review/)

**Nifty Alpha Low-Volatility 30 (index launched 10 Jul 2017).**
- BACKTEST-dominated: 17.71% a year since April 2005 (to 30 Sep 2026). — [NSE factsheet](https://www.niftyindices.com/Factsheet/Factsheet_NIFTY_Alpha_Low-Volatility_30.pdf)
- LIVE: ICICI's ETF NAV returned 14.55% a year from 13 Aug 2020 to 9 Nov 2026, against 14.68% for the Nifty 50 fund and 16.73% for the Nifty 500 fund. Up to 27 Sep 2024 it led the Nifty 50 fund (27.8% vs 23.8% a year); since then it has returned −7.5% a year against −1.1%. [own computation] — [mfapi 148456](https://api.mfapi.in/mf/148456)
- Freefincal on this ETF at launch: "much of the data below is a backtest. So returns are are a backtest of a backtest!" and "We need more history." — [Freefincal](https://freefincal.com/icici-prudential-alpha-low-vol-30-etf-review-what-you-need-to-know/)

**Nifty Alpha 50 (index launched 19 Nov 2012).**
- Index since Dec 2003: 20.21% a year with 24.74% volatility (to 30 Sep 2026). — [NSE factsheet](https://www.niftyindices.com/Factsheet/Factsheet_Nifty_Alpha50.pdf)
- LIVE: Kotak's ETF returned 8.31% a year from 29 Dec 2021 to 9 Nov 2026, against 9.06% for the Nifty 50 fund and 10.73% for the Nifty 500 fund; its calendar years were −16.6, +41.8, +32.4, −10.8 and +4.4 (YTD). [own computation] — [mfapi 149397](https://api.mfapi.in/mf/149397)

**Low volatility and quality.**
- LIVE: ICICI Low Vol 30 ETF 12.27% a year against 11.76% for the Nifty 50 fund (3 Jul 2018 – 9 Nov 2026), a lead of about 0.5 points; the back-tested lead over the Nifty 100 to May 2018 was about 4 points (17.66% vs 13.66%, price return). [own computation] — [mfapi 141596](https://api.mfapi.in/mf/141596); [NSE Low Vol 30 white paper, 2018](https://archives.nseindia.com/content/indices/NIFTY100_Low_Vol30_White_paper_Jun2018.pdf)
- LIVE: ABSL Nifty 200 Quality 30 ETF 8.53% a year against 9.43% (Nifty 50 fund) and 11.59% (Nifty 500 fund) from 19 Aug 2022. [own computation] — [mfapi 150497](https://api.mfapi.in/mf/150497)

**Independent commentary (Freefincal; other outlets unreachable).**
- On the UTI momentum fund at launch (February 2021): "Almost the entire outperformance came from Jan 2012 to Jan 2018"; the back-tested index failed to beat the Nifty for about 3.5 years around the 2008 crash and for about three years from 2017–18; the fund is "just another fancy thematic index fund that is likely to disappoint investors". — [Freefincal](https://freefincal.com/uti-nifty200-momentum-30-index-fund/)
- On factor indices generally (November 2023): index definitions and baskets are "cherry-picked to produce good results with past data"; for Nifty Midcap150 Quality 50, "The ten-year outperformance from Oct 2011 to Oct 2021 has been erased by poor performance over the last two years." — [Freefincal](https://freefincal.com/why-nifty-midcap150-quality-50-index-performance-is-a-warning-for-factor-investing-fans/)
- On Nifty500 Momentum 50 (September 2024, just before launch of the funds): "Our recommendation is to avoid momentum-based passive (or active) funds"; "too volatile (than a small cap index) to be the mainstay of a portfolio." — [Freefincal](https://freefincal.com/should-you-invest-in-the-nifty-500-momentum-50-index/)
- On low volatility (October 2025): "Much of the low volatility index history is backtested and not seen in actual trading." — [Freefincal](https://freefincal.com/is-there-a-factor-index-that-is-consistently-less-risky-than-broad-based-indices/)

### Inferences
- The live shortfall against the back-test has three plausible causes that cannot be separated with this data: ordinary bad luck over a short window (five to six years, one bad regime); selection of index rules that fitted the pre-launch period; and crowding or capacity once about ₹17,700 cr tracks these indices (figure from the earlier note).
- A fair summary for planning: assume a momentum index fund beats the Nifty 200 by 0–3 points a year before tax, not the 5–6 points in the back-test, and expect multi-year stretches where it is behind.
- Funds launch after strong back-tests and strong recent runs (Midcap150 Momentum 50 in late 2022 after 2020–21; Nifty500 Momentum 50 in September 2024 at the peak). The investor's realised experience is therefore worse than even the live index record.

### Gaps
- No index TRI series from exact launch dates, so "live" uses calendar years and fund NAVs. The Alpha 50 index's live period since November 2012 and Alpha Low-Vol 30's from July 2017 to August 2020 are not covered.
- Capitalmind, PrimeInvestor, Morningstar India, ET and Mint analyses of back-test versus live could not be reached. Only Freefincal and NSE material was read.
- No statistical test of the live-vs-back-test gap was possible with five annual observations.

---

## Q5. Long-run factor numbers, longest lags, and multi-factor combinations

### Takeaway
Long-run index figures are in the earlier note and are mostly back-tested. The new evidence here is on lag length: back-tested Momentum 30 spent about six years (end-2007 to end-2013) behind the Nifty 200 cumulatively, and every live factor fund is currently in a relative drawdown of 5–22% that has lasted two years or more; ICICI's low-volatility ETF has not made a new relative high against the Nifty 50 since April 2020. No multi-factor combination has a live record that beats a plain broad index fund.

### Cited Findings
- **Long-run index returns (mostly BACKTEST; total return since 1 Apr 2005 to 30 Sep 2026, volatility on price index):** Momentum 30 18.30% / 22.31%; Midcap150 Momentum 50 22.22% / 21.11%; Quality 30 16.64% / 17.87%; Alpha Low-Vol 30 17.71% / 17.20%; Alpha 50 (since Dec 2003) 20.21% / 24.74%. Nifty 200 TRI 13.9% and Nifty 50 TRI 13.6% (to 30 Jun 2026). — [NSE factsheets as cited in the earlier note](https://www.niftyindices.com/Factsheet/Factsheet_Nifty200_Momentum30.pdf); [HDFC AMC presentation, July 2026](https://files.hdfcfund.com/s3fs-public/Others/2026-07/HDFC%20NIFTY200%20Momentum%2030%20Index%20Fund_PPT%20%28July%202026%29.pdf)
- **Momentum 30 vs Nifty 200, cumulative relative performance at year-ends ([own computation], BACKTEST to 2019, LIVE from 2021):**

  | Stretch behind the prior relative high | Label | Deepest shortfall | Length |
  |---|---|---|---|
  | End-2007 → regained end-2013 | BACKTEST | −18.4% (end-2009) | about 6 years |
  | End-2017 → regained end-2020 | BACKTEST | −2.0% (end-2018) | about 3 years |
  | End-2021 → regained end-2023 | LIVE | −9.9% (end-2022) | about 2 years |
  | End-2024 → ongoing at 9 Nov 2026 | LIVE | −13.8% (year-end basis; −22% on daily fund data from the June 2024 high) | about 2 years so far |

  Rolling 3-year gaps turned negative for windows ending 2009 (−0.4 points a year) and 2010 (−5.4); the 5-year gap was about zero for the window ending 2012 (−0.1) and +2.8 for the window ending 2025. — [NSE whitepaper, Exhibit 7](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf)
- **Longest relative lag on LIVE fund data (fund ÷ benchmark below its previous high; [own computation]):**

  | Fund | vs Nifty 50 fund | vs Nifty 500 fund |
  |---|---|---|
  | UTI Momentum 30 (since Mar 2021) | 14 Jun 2024 → ongoing, 878 days; now −22.5% | 3 Jun 2024 → ongoing, 889 days; now −22.2% |
  | Tata Midcap150 Momentum 50 (since Oct 2022) | 19 Dec 2024 → ongoing, 690 days; now −12.9% | same start; now −11.9% |
  | Kotak Alpha 50 ETF (since Dec 2021) | 11 Jul 2024 → ongoing, 851 days; now −16.4% (worst ever −33.0%, Feb 2023) | now −15.7% |
  | ICICI Alpha Low-Vol 30 ETF (since Aug 2020) | 25 Sep 2020 → 3 Jan 2024, 1,195 days; now −13.8% | 25 Sep 2020 → 11 Mar 2024, 1,263 days; now −14.1% |
  | ICICI Low Vol 30 ETF (NAV since Jul 2018) | 15 Apr 2020 → ongoing, 2,399 days (about 6.6 years); now −5.0%, worst −14.2% (Apr 2022) | now −14.7% |
  | ABSL Quality 30 ETF (since Aug 2022) | 11 Sep 2024 → ongoing, 789 days; now −13.6% | now −13.1% |
  | Nippon Nifty 50 Value 20 ETF (since Jun 2015) | 26 Nov 2024 → ongoing, 713 days; now −13.6% | 23 Feb 2023 → ongoing, 1,355 days; now −16.9% |

  — [mfapi 148703](https://api.mfapi.in/mf/148703); [150738](https://api.mfapi.in/mf/150738); [149397](https://api.mfapi.in/mf/149397); [148456](https://api.mfapi.in/mf/148456); [141596](https://api.mfapi.in/mf/141596); [150497](https://api.mfapi.in/mf/150497); [134782](https://api.mfapi.in/mf/134782)
- Freefincal (December 2021, updated August 2022) on low volatility: "For the first time, the 5Y return of the low volatility index is lower than that of the Nifty 50", and "No strategy outperforms forever." — [Freefincal](https://freefincal.com/nifty-100-low-volatility-30-vs-nifty-50-return-difference-at-an-all-time-low/)
- Freefincal (October 2025): Low Vol 30 had a lower Ulcer index than the Nifty 100 in only 50–82% of 2- to 10-year windows, while a 65:35 equity-bond hybrid index did so in 100%; "low volatility does not guarantee a low drawdown." — [Freefincal](https://freefincal.com/is-there-a-factor-index-that-is-consistently-less-risky-than-broad-based-indices/)
- Freefincal (August 2024): "It is incorrect to assume that low-volatility investing will always fare better than investing in the Nifty or Nifty Next 50." — [Freefincal](https://freefincal.com/can-i-switch-from-nifty-nifty-next-50-to-nifty-100-low-volatility-30-index-fund/)
- **Third-party factor back-test with delisted stocks included (BACKTEST, Dec 2006 – Dec 2025, Nifty 500, top 50 by factor split into low- and high-liquidity halves, annual rebalance, net of costs and Indian taxes; Nifty 50 net 10.41%):**

  | Factor | Low-turnover half: net CAGR / max drawdown | High-turnover half: net CAGR / max drawdown |
  |---|---|---|
  | Momentum | 15.04% / −75.73% (68-month recovery) | 11.89% / −77.70% (70 months) |
  | Quality (ROE) | 15.45% / −65.04% | 8.16% / −72.02% |
  | Value | 13.74% / −54.03% | 12.23% / −64.35% |
  | Low volatility | 14.11% / −42.80% | 14.03% / −45.79% |

  The authors conclude low volatility is "the sole factor that appears completely turnover-agnostic". — [Freefincal / BacktestIndia, April 2026](https://freefincal.com/does-factor-investing-outperformance-fail-for-high-turnover-stocks/)
- **Multi-factor, LIVE:** ICICI Alpha Low-Vol 30 ETF 14.55% vs 16.73% for the Nifty 500 fund since August 2020; Edelweiss Nifty500 Multicap Momentum Quality 50 ETF −5.7% a year vs +2.8% for the Nifty 500 fund since November 2024 (2025: −8.4%); Mirae Nifty 200 Alpha 30 ETF 16.18% vs 12.35% since October 2023. [own computation] — [mfapi 148456](https://api.mfapi.in/mf/148456); [152981](https://api.mfapi.in/mf/152981); [152134](https://api.mfapi.in/mf/152134)
- **Multi-factor, BACKTEST:** a 50:50 Momentum 30 + 8–13 year G-Sec index returned 12.7% a year with a −17.6% worst drawdown over Jan 2011 – Jun 2026 (Nifty 50: 10.5%, −38.3%); a fund on it (HYBRIDETF) launched only on 27 Jul 2026. — [Mirae Asset presentation](https://www.miraeassetmf.co.in/docs/default-source/product-presentations/mirae-asset-nifty200-momentum-30-plus-8-13-yr-g-sec-5050-etf-presentation.pdf); [Groww](https://groww.in/etfs/mirae-asset-nifty200-momentum-30-plus-544841)

### Inferences
- The longest live lag belongs to low volatility, not momentum: about 6.6 years without a new relative high against the Nifty 50. An investor choosing low volatility for "smoother outperformance" has received lower volatility (14.3% against 17.1% for the Nifty 50 fund since July 2018) but almost no extra return (+0.5 points a year).
- Combining alpha with low volatility has not avoided long lags live (about 3.3 years, 2020–2024) and it fell 25% in 2024–25, more than the Nifty 50.
- The best-evidenced diversifier for momentum is not another equity factor but bonds or cash: the equity factors all fell together in 2024–25, while the momentum-plus-G-Sec back-test halves drawdown. That combination has no live record yet.
- Value was the one factor that did well in the momentum slump (UTI Nifty 500 Value 50: +16.3% in 2025; ICICI Nifty200 Value 30 ETF: +20.0% in 2025), which suggests momentum-plus-value is a better offset than momentum-plus-quality or low-vol. This rests on one episode.

### Gaps
- No long-run (since 2005) CAGR, volatility or maximum drawdown was retrieved for Nifty 50 Value 20, Nifty200 Value 30, Nifty500 Value 50, Nifty100 Low Volatility 30 (official factsheet), Nifty Alpha Quality Low-Vol 30, Nifty Alpha Quality Value Low-Vol 30 or Nifty500 Multifactor MQVLv 50. niftyindices.com was unreachable and NSE's multi-factor whitepaper could not be opened.
- No fund tracking Nifty Alpha Quality Low-Vol 30 or MQVLv 50 was found on Groww or mfapi, so those indices have no live fund record in these notes.
- Longest-lag figures for the back-tested period are at calendar-year resolution only, and only for Momentum 30.

---

## Q6. Data for an honest hobbyist back-test, and the size of survivorship bias

### Takeaway
Free building blocks now exist: several 2026 GitHub projects rebuild point-in-time NSE index membership from exchange circulars, Wikipedia or Internet Archive snapshots, and keep delisted stocks by working from daily bhavcopies. None is a turnkey, validated Nifty 200 history with prices. Practitioner estimates put survivorship inflation at about 5 points of annual return (small caps) or +0.4 to +0.9 of Sharpe ratio for momentum, enough to erase most of a typical hobby back-test's apparent edge.

### Cited Findings
- **BKKB20/nse-index-history** (GitHub, last pushed March 2026): reconstructs constituents of 28 NSE indices "from 2004 to 2026" from "~100 NSE PDF and HTM circulars", by walking back from current members; outputs a SQLite database and Excel workbook; membership only, no prices. Stated limits: three 2018–19 circulars are scanned images and unprocessed; "Pre-2010 accuracy limited by company-name-to-ticker mapping completeness". The README names Nifty 50, Next 50, Bank, IT and Midcap 50 and "23 more"; Nifty 200 and 500 are not confirmed. — [GitHub](https://github.com/BKKB20/nse-index-history)
- **NegativeZone/nsepit** (MIT licence, July 2026): point-in-time **Nifty 50** membership rebuilt from Wikipedia's replacement history, plus survivorship-free liquidity universes (top N by 63-day median traded value, delisted names included) from NSE bhavcopies "since 2009" (about 4,300 files). It includes a harness that runs a strategy on point-in-time and current-member universes and reports the difference. Price-only (no dividends), no automatic rename splicing. It notes NSE's terms "restrict reproduction and redistribution of its data". — [GitHub](https://github.com/NegativeZone/nsepit)
- **abhij1306/NSE-noodles** (October 2026): a method, not data. Scripts keep "every equity security that ever appeared in a daily bhavcopy since 22 Jun 2011", key data by ISIN, and accept corporate-action factors "only when the ex-date price gap confirms it". Does not cover index membership. A full pull takes about 4–5 hours at one request every 2 seconds. — [GitHub](https://github.com/abhij1306/NSE-noodles)
- **ReaperOAK/survivorship-free-backtester** (July 2026, PolyForm Noncommercial licence): uses NSE bhavcopy, yfinance, mfapi NAVs, Internet Archive snapshots for point-in-time Nifty 100/200/500 lists, and Kaggle Nifty 50 weights; "~2,800 NSE stocks × 26 years". Its headline finding: "Survivorship inflates momentum by roughly +0.4 to +0.9 Sharpe depending on universe"; raw momentum "Sharpe ~1.5" becomes "~1.0 corrected". Also: after tax, high-turnover strategies "barely out-earn buy-and-hold". No date ranges are given and the author says all figures are back-tests "on a strong market era". — [GitHub](https://github.com/ReaperOAK/survivorship-free-backtester)
- **vishalvx/nifty-indices-datasets** (June 2026) advertises historical constituents for Nifty 50, Midcap 50, Smallcap 50 and momentum indices; **ranadheergudipathi02-oss/india-index-tracker** (July 2026) tracks NSE and BSE constituent changes going forward. Neither README was read. — [GitHub repository search](https://api.github.com/search/repositories?q=nifty+historical+constituents)
- **BacktestIndia** is described by Freefincal as "a free NSE backtesting platform covering 19 years of data, including delisted stocks"; its Momentum-30-style replication (Dec 2006 – Jun 2025, net of costs and tax) gives 14.60% CAGR and a −70.61% maximum drawdown against 10.41% and −55.12% for the Nifty 50. — [Freefincal, March 2026](https://freefincal.com/is-indian-momentum-investing-just-a-liquidity-illusion/); [Freefincal, April 2026](https://freefincal.com/does-factor-investing-outperformance-fail-for-high-turnover-stocks/)
- **Size of the bias, academic-style estimate:** survivor-only equal-weight back-tests of the Nifty Smallcap 250 overstate annual return by 4.94 points and Sharpe by 0.097 (2016–2025, 1,437 stocks, membership rebuilt from bhavcopies with 85–90% historical accuracy; single author, not peer-reviewed). — [arXiv 2603.19380](https://arxiv.org/abs/2603.19380)
- A forum request for point-in-time Nifty 500 membership including delisted names has no answer in the indexed thread, and Kite Connect cannot return history for delisted instruments. — [Unofficed forum](https://forum.unofficed.com/t/get-historical-nifty-500-constituent/1375); [Kite forum](https://kite.trade/forum/discussion/comment/50548/) (search summaries)
- Official and semi-official membership sources (NSE inclusion/exclusion file, niftyindices monthly constituent zips for Apr 2013 – Mar 2022, index-change press releases, monthly weight reports) are described in the earlier note. — [TradingQnA thread](https://tradingqna.com/t/where-can-i-find-historical-composition-of-nifty-indices/7163)

### Inferences
- A practical free route for a Nifty 200 momentum test: (1) build the price panel from bhavcopies keyed by ISIN (NSE-noodles method), which keeps dead stocks; (2) use a liquidity-ranked universe (top 200 by traded value at each rebalance date) instead of true index membership, which avoids the membership problem entirely and is what nsepit does; (3) validate against BKKB20's or ReaperOAK's reconstructed membership where available.
- Bias size for a large/mid-cap momentum test is probably smaller than the 5 points measured in small caps, but the ReaperOAK estimate (a third of the Sharpe ratio) suggests it is not small. A 15-stock back-test on today's constituents should be treated as unusable, as the brief already assumes.
- A cheaper sanity check than building any of this: compare the hobby back-test's 2021–2026 result with the live UTI fund's 14.1% CAGR and −31.5% drawdown. If the back-test shows much better numbers on a similar universe over those dates, the difference is bias or luck, not skill.
- All these repositories are new (2026), have one to seven stars and no independent validation. Their outputs need spot checks against NSE circulars before being trusted.

### Gaps
- Kaggle, EODHD, Samco, CMIE Prowess, ACE Equity and Refinitiv pricing and coverage were not checked (hosts unreachable or search quota exhausted). The IIM Ahmedabad factor library, which publishes survivorship-adjusted series, was also unreachable, so a direct adjusted-versus-unadjusted momentum comparison was not computed.
- No peer-reviewed estimate of survivorship bias for Indian **large/mid-cap momentum** was found.
- Whether BKKB20's 28 indices include the Nifty 200 was not confirmed.

---

## Q7. DIY 15-stock momentum vs holding a momentum ETF or index fund, after costs and tax

### Takeaway
Even granting the DIY portfolio the same gross return as the index, it should be expected to finish about 1.0–2.5 points a year behind a momentum index fund after tax for ₹1–20 lakh, almost entirely because the investor pays 20% short-term gains tax on each rebalance while the fund pays none on its own trades. Trading costs are roughly a wash with the fund's cost at ₹5 lakh and above; fixed per-order charges fall below about 0.25% a year above roughly ₹4.5–5 lakh and to about 0.1% at ₹10 lakh.

### Cited Findings
- **Index turnover:** NSE reports annual churn for the semi-annual Momentum 30 of 101% (FY22), 112% (FY23), 115% (FY24), 110% (FY25) and 134% (FY26 to 27 Feb 2026); Midcap150 Momentum 50 96% and Nifty500 Momentum 50 139% in FY25. — [NSE whitepaper, Exhibit 11](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf) (from the earlier note)
- **Fund-reported portfolio turnover** (Groww, November 2026) for Momentum 30 funds ranges from 36% (Motilal) and 62% (UTI) to 144–206% (HDFC, Bandhan, ICICI, SBI, Kotak, Baroda); Midcap150 Momentum 50 funds 106–121%; Nifty500 Momentum 50 funds 53–162%; Alpha 50 funds 152–158%. — [Groww fund pages](https://groww.in/mutual-funds/kotak-nifty-200-momentum-30-index-fund-direct-growth)
- **Churn by name count:** for Nifty500 Momentum 50, 39 of 50 stocks (78%) were replaced in December 2024 and 34 of 50 (68%) in June 2025; 47 of the original 50 were gone within a year. — [Freefincal, August 2025](https://freefincal.com/an-index-with-a-portfolio-turnover-higher-than-active-funds/)
- **Groww charges and tax rates** used below (brokerage min(₹20, 0.1%) per order; DP ₹23.60 per sell; STT 0.1% each side; stamp 0.015% on buys; exchange and SEBI about 0.0032% per side; STCG 20% and LTCG 12.5% above ₹1.25 lakh a year, before 4% cess) are sourced in `costs_and_taxes.md`. — [Groww pricing](https://groww.in/pricing)
- **DIY annual trading cost, [own computation].** Assumptions: 15 equal positions; 8 names replaced at each of two rebalances a year (one-way turnover about 107%, matching the index); one order per trade; slippage 0.10% a side.

  | Capital | Position size | Fixed charges (brokerage, DP, GST) | Fixed, % a year | Variable (STT, stamp, exchange, slippage), % a year | Total, % a year |
  |---|---|---|---|---|---|
  | ₹1 lakh | ₹6,667 | ₹629 | 0.63 | 0.45 | 1.08 |
  | ₹2 lakh | ₹13,333 | ₹881 | 0.44 | 0.45 | 0.89 |
  | ₹3 lakh | ₹20,000 | ₹1,133 | 0.38 | 0.45 | 0.83 |
  | ₹5 lakh | ₹33,333 | ₹1,133 | 0.23 | 0.45 | 0.68 |
  | ₹7.5 lakh | ₹50,000 | ₹1,133 | 0.15 | 0.45 | 0.60 |
  | ₹10 lakh | ₹66,667 | ₹1,133 | 0.11 | 0.45 | 0.56 |
  | ₹20 lakh | ₹1,33,333 | ₹1,133 | 0.06 | 0.45 | 0.51 |

  With zero slippage the ₹5 lakh total is 0.46%. Inputs: [Groww pricing](https://groww.in/pricing).
- **Fund-side cost actually observed (LIVE):** momentum index funds trailed the index total return by about 0.3 points a year over five years (UTI) and 0.5–0.9 points in the year to 30 Sep 2026 across funds. [own computation] — [mfapi 148703](https://api.mfapi.in/mf/148703); [NSE factsheet](https://www.niftyindices.com/Factsheet/Factsheet_Nifty200_Momentum30.pdf)
- **Ten-year after-tax comparison, [own computation].** Both sides earn the same gross index return. DIY pays the trading costs above and tax every year on realised gains (all of each year's gain treated as realised, 80% or 50% of it short-term at 20.8% including cess, the rest long-term at 13% above ₹1.25 lakh; losses carried forward). The fund trails the index by 0.5% a year and pays 13% on gains above ₹1.25 lakh once, at redemption.

  | Gross path | Capital | DIY, 80% short-term | DIY, 50% short-term | Fund, hold and redeem | Fund with yearly ₹1.25 lakh gain harvesting | DIY shortfall vs fund (80% / 50% short-term) |
  |---|---|---|---|---|---|---|
  | Flat 15% a year | ₹1 lakh | 11.60% | 12.47% | 13.86% | 14.50% | 2.26 / 1.39 pp |
  | Flat 15% | ₹5 lakh | 11.93% | 12.83% | 13.45% | 14.34% | 1.52 / 0.62 pp |
  | Flat 15% | ₹20 lakh | 12.02% | 12.50% | 13.37% | 13.63% | 1.35 / 0.87 pp |
  | Flat 10% | ₹5 lakh | 7.77% | 8.36% | 8.77% | 9.50% | 1.00 / 0.42 pp |
  | Flat 10% | ₹20 lakh | 7.88% | 8.40% | 8.66% | 9.04% | 0.77 / 0.26 pp |
  | Flat 20% | ₹5 lakh | 16.09% | 17.20% | 18.21% | 18.90% | 2.12 / 1.01 pp |
  | Momentum 30 index years 2016–2025 (18.3% gross) | ₹1 lakh | 14.45% | 15.51% | 16.90% | 17.79% | 2.45 / 1.39 pp |
  | Same path | ₹5 lakh | 14.78% | 15.52% | 16.58% | 17.32% | 1.80 / 1.06 pp |
  | Same path | ₹20 lakh | 14.66% | 15.13% | 16.52% | 16.72% | 1.86 / 1.39 pp |

  Tax alone, with no costs on either side (₹20 lakh, 15% a year): 1.97 points a year if all gains are short-term, 1.36 at 80%, 0.89 at 50%, 0.31 if all are long-term. Index path from the [NSE whitepaper, Exhibit 7](https://www.niftyindices.com/docs/default-source/indices/nifty200-momentum-30/momentum-strategy-whitepaper_2026.pdf).
- **Share of gains that is short-term:** a third-party replication estimates about 80% of semi-annual momentum gains are taxed as short-term, and that moving to annual rebalancing would save about 0.44% a year in tax. — [BacktestIndia](https://backtestindia.com/blog/momentum-investing-india-backtest) (figures from the earlier note and a search summary; page not reachable in this session)
- **Practitioner view for the wrapper:** Freefincal's review of the UTI fund says existing DIY momentum investors "could consider it as a satellite" for tax and effort savings, and recommends that momentum PMS or smallcase holders switch to the fund, mainly for tax reasons (paraphrase of the fetched page). — [Freefincal](https://freefincal.com/uti-nifty200-momentum-30-index-fund/)
- **Illustration from a newsletter (promotional, not a back-test):** ₹10 lakh over 10 years grows to about ₹30.7 lakh after tax in a direct momentum approach against about ₹36.6 lakh in a momentum mutual fund, which works out to roughly 11.9% against 13.9% a year, a gap of about 2 points. — [Curious Investing Insights](https://curiousinvestinginsights.substack.com/p/why-momentum-in-a-mutual-fund-is) (search summary only; page not reachable)
- **Counter-argument for DIY:** the momentum premium in one delisting-inclusive back-test sits in less liquid stocks (19.43% net for the low-turnover half against 8.51% for the liquid half, 2006–2025), and "Large momentum funds, forced to concentrate in liquid stocks as AUM grows, may lose the alpha. Smaller individual portfolios may keep a structural advantage" (paraphrase). — [Freefincal / BacktestIndia, March 2026](https://freefincal.com/is-indian-momentum-investing-just-a-liquidity-illusion/)
- **Counter-evidence on high-turnover strategies generally:** one open-source Indian back-tester reports that after tax, high-turnover strategies "barely out-earn buy-and-hold". — [GitHub: ReaperOAK](https://github.com/ReaperOAK/survivorship-free-backtester)

### Inferences
- **Central estimate of DIY after-tax drag relative to the fund: about 1.5 points a year (range 1.0–2.5) at 10–18% gross returns** for ₹1–20 lakh, if most gains are realised within 12 months. It falls to 0.3–1.0 points if the investor can push half or more of the gains past 12 months (for example a 12-month hold rule with a buffer), at the price of slower signals. This is a model, not a measured result.
- To beat the fund, a DIY 15-stock picker therefore needs to out-select the index by about 1.5 points a year net, every year, with half as many names and with a back-test that is known to be biased. The live record in Q2 shows the index's own selection added nothing over a size-matched blend in 5.7 years, which makes that hurdle look high.
- **Capital threshold:** fixed charges are about 0.6% a year at ₹1 lakh, 0.4% at ₹2–3 lakh, under 0.25% from about ₹4.5–5 lakh, and about 0.1% at ₹10 lakh. Below roughly ₹3 lakh, DIY is clearly handicapped on costs alone; above ₹5 lakh costs stop being the deciding factor and tax dominates.
- For small accounts the wrapper advantage is larger than the headline: at ₹1–5 lakh, yearly gains are usually under the ₹1.25 lakh long-term exemption, so a fund holder who books and re-buys once a year can hold momentum almost tax-free, while the DIY investor still pays 20% on short-term gains from the first rupee.
- Points in DIY's favour that the model ignores: realised losses can offset other gains (a fund's internal losses cannot be passed through); the investor controls timing; and a small portfolio can hold less liquid names. Points against: 15 names track the index loosely, so results will scatter widely around it in both directions.
- Within the wrapper, index fund versus ETF: the tax treatment is the same; the ETF adds brokerage, DP charge on sale and spread in thinly traded counters, and the index fund adds nothing. For buy-and-hold on Groww the direct index fund is the simpler choice.

### Gaps
- Capitalmind, Zerodha/Rainmatter and Weekend Investing pieces on the wrapper tax advantage and the counter-arguments could not be read. Only Freefincal and two search summaries inform the practitioner view.
- The model assumes all gains are realised each year and that DIY matches the index gross return; neither was tested on stock-level data. Real tax outcomes depend on the path of gains and losses and on other income.
- Whether costs embedded in funds will change under the 2026 expense-disclosure rules was not checked.
- Tax treatment of the 50:50 momentum-plus-G-Sec ETF (it may not qualify as an equity-oriented fund) was not verified.

---

## Q8. Does a trend filter on a momentum ETF or index help or hurt?

### Takeaway
There is no reliable Indian evidence that a 200-day filter improves a momentum fund, and the live record since 2022 shows the result depends almost entirely on which rule is picked: checking the fund against its own 200-day average monthly cut returns roughly in half without reducing the drawdown, while a 100-day rule or a Nifty-50-based rule happened to work well. Each exit from an equity fund is taxable, which cost a further 1.2–1.7 points a year in these tests.

### Cited Findings
- **LIVE test on the UTI momentum fund's NAV, 31 Jan 2022 – 9 Nov 2026 (4.8 years), [own computation].** Rule: hold the fund when the signal is above its moving average, otherwise cash at 6.5%; signal acted on the next day; no trading costs. "After tax" deducts 20.8% (held 12 months or less) or 13% of the gain at each exit, ignoring the ₹1.25 lakh exemption.

  | Rule | CAGR | CAGR after tax | Max drawdown (before / after tax) | Switches | Time invested |
  |---|---|---|---|---|---|
  | Buy and hold the momentum fund | 9.89% | — | −31.5% | 0 | 100% |
  | Buy and hold the Nifty 50 fund | 9.07% | — | −15.5% | 0 | 100% |
  | Fund vs own 200-day average, month-end check | 5.23% | 3.99% | −31.8% / −35.5% | 18 | 60% |
  | Fund vs own 200-day average, daily check | 6.50% | 5.14% | −23.8% / −28.3% | 58 | 60% |
  | Fund vs own 100-day average, month-end check | 12.90% | 11.49% | −12.4% / −17.5% | 14 | 58% |
  | Nifty 50 fund vs its 200-day average, month-end check | 14.36% | 12.68% | −14.4% / −18.3% | 10 | 68% |

  The own-200-day monthly rule stayed invested through the first three months of the fall (signal "in" at each month-end from September to November 2024), exited at end-December 2024, then flipped in and out about 10 times between June 2025 and October 2026. — [mfapi 148703](https://api.mfapi.in/mf/148703); [mfapi 120716](https://api.mfapi.in/mf/120716)
- **Same test on other LIVE funds, own 200-day average, month-end check, [own computation]:**

  | Fund and period | Buy and hold: CAGR / max drawdown | Filtered: CAGR / max drawdown | Filtered after tax: CAGR |
  |---|---|---|---|
  | Tata Midcap150 Momentum 50, Oct 2023 – Nov 2026 | 14.46% / −25.9% | 8.31% / −23.7% | 7.01% |
  | UTI Nifty 50 fund, Jan 2014 – Nov 2026 | 12.75% / −38.4% | 10.93% / −17.1% | 9.57% |
  | UTI Nifty Next 50 fund, Jun 2019 – Nov 2026 | 14.83% / −36.3% | 9.63% / −21.6% | 8.20% |
  | ICICI Low Vol 30 ETF NAV, Jun 2019 – Nov 2026 | 13.24% / −30.5% | 8.43% / −20.7% | 7.26% |
  | Motilal Oswal Midcap 150 fund, Sep 2020 – Nov 2026 | 22.92% / −21.2% | 16.75% / −20.7% | 14.69% |

  Using the Nifty 50 fund's 200-day average as the switch for the Tata midcap momentum fund gave 20.69% and −10.7% over its three years. — [mfapi 150738](https://api.mfapi.in/mf/150738); [120716](https://api.mfapi.in/mf/120716); [143341](https://api.mfapi.in/mf/143341); [141596](https://api.mfapi.in/mf/141596); [147622](https://api.mfapi.in/mf/147622)
- **Freefincal, October 2022 (BACKTEST, Nifty Midcap150 Momentum 50 TRI, rolling 5-, 7- and 10-year windows):** a 6-month vs 12-month moving-average switch between the momentum index and debt at 6% looked "promising", but "has a higher risk than systematic investing", "may not always provide a higher reward for the higher risk taken", and "the model fails for sharp price changes" such as March 2020. Taxes and exit loads were not included. — [Freefincal](https://freefincal.com/momentum-index-fund-will-tactical-entry-exit-give-better-results/)
- **Freefincal, 10-month moving average on the Sensex (BACKTEST, 338 ten-year windows):** to allow for tax and exit loads the author cut the tactical portfolio's final value by 20%, against 4% for a systematic 50:50 portfolio, because it averaged about five round trips per decade; a steady systematic portfolio was "typically better" on drawdown. — [Freefincal](https://freefincal.com/market-timing-with-ten-month-moving-average-tactical-asset-allocation-backtest-part-2/)
- **Freefincal's moving-average tool page (updated August 2026):** back-tests "do not factor in future market movements, human emotions, taxation and exit loads"; the model "works reasonably well with 50% equity or lower" and "not so well for higher equity allocations". — [Freefincal](https://freefincal.com/tool-for-tactical-buying-and-selling-using-moving-averages/)
- **Open-source Indian back-tester (BACKTEST, dates not given):** an ensemble with a regime-to-cash switch "roughly halves drawdown (−38% → ~−18%)", described by its author as "insurance, not free alpha". — [GitHub: ReaperOAK](https://github.com/ReaperOAK/survivorship-free-backtester)
- **Momo India (September 2024, BACKTEST):** a 30-stock equal-weight momentum portfolio that goes to cash when its own NAV is below the 200-day average on the monthly rebalance day; the plain version went to cash only in 2008 and during Covid. The result figures were not visible. — [Momo India](https://momoindia.substack.com/p/backtest-reducing-momentum-drawdowns) (search summary; page not reachable)
- **Tax and cost of the switch itself:** units of an equity fund sold within 12 months are taxed at 20%, later at 12.5% above ₹1.25 lakh a year (rates in `costs_and_taxes.md`); several momentum index funds also carry exit loads (Motilal Oswal Momentum 30 and Nifty 500 Momentum 50: 1% within 15 days; Tata Midcap150 Momentum 50: 0.50% for an initial period; SBI Momentum 30 and Bandhan Nifty 500 Momentum 50: 0.25% for a short initial period; UTI, ICICI, HDFC, Kotak and Bandhan Momentum 30: nil). — [Groww fund pages](https://groww.in/mutual-funds/motilal-oswal-nifty-200-momentum-30-index-fund-direct-growth)

### Inferences
- A trend filter addresses market-wide crashes (2008, March 2020). The 2024–25 damage to momentum was a rotation: the broad market recovered within about a year while momentum stayed down. A filter on the fund's own trend then whipsaws; a filter on the Nifty 50 exits and re-enters on the market's schedule, not the factor's. Neither is designed for this kind of loss.
- The spread between neighbouring rules over the same 4.8 years (5.2% for the 200-day rule, 12.9% for the 100-day rule, 14.4% for the Nifty-based rule) is a warning sign of noise, not evidence that the better two "work". Choosing among them after the fact would be curve-fitting.
- On the longer live samples (Nifty 50 since 2014, Next 50 and low-vol since 2019), the filter did what the earlier note found for the Nifty: it roughly halved the drawdown and cost about 2–5 points a year of return before tax, and a further 1.2–2 points after tax.
- If a filter is wanted on a momentum holding, the less costly forms are: apply it to new money only (pause purchases, do not sell), or hold a fixed bond or cash share alongside (as the 50:50 momentum-plus-G-Sec index does) so no taxable switching is needed.
- Because the fund wrapper's main advantage is tax deferral (Q7), a rule that sells the fund once or twice a year gives much of that advantage back.

### Gaps
- No test on the Nifty200 Momentum 30 TRI from 2005 was possible (index history unreachable), so the filter's effect in the 2008 and 2020 crashes on the actual index is unmeasured here. That is the case where it would be expected to help most.
- Capitalmind, Weekend Investing and Alphaquest trend-filter back-tests could not be reached.
- The momentum-crash literature (Daniel & Moskowitz; Barroso & Santa-Clara on volatility scaling) could not be re-read in this session (NBER and SSRN unreachable). From memory only, and unverified here: both find momentum crashes cluster in rebounds after market declines and that scaling exposure by recent momentum volatility improved risk-adjusted returns in long-short US data. Neither is an Indian, long-only, after-tax result.
- The own tests ignore trading costs, the LTCG exemption, exit loads and the delay between NAV-based signals and execution, and cover at most 4.8 years for momentum funds.
