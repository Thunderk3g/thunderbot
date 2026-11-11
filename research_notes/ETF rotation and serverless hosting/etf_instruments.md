# NSE-listed ETFs for a monthly rotation bot (Groww delivery, Yahoo `.NS` prices): instrument reference as of 11 Nov 2026

**Read this first: how these notes were built and what that limits.**
- The shared web-search budget ran out after six searches, and most Indian AMC, news and data hosts were unreachable from the research session (valueresearchonline.com, businesstoday.in, business-standard.com, trendlyne.com, tradingqna.com, pocketful.in, tickertape.in, all AMC sites, nseindia.com HTML, amfiindia NAV file, rbi.org.in). SEBI/RBI circular texts and AMC factsheets were **not** read.
- Two primary sources were reachable and carry most of the numbers below:
  - **Yahoo Finance chart API**, pulled directly on 11 Nov 2026 for about 130 `.NS` symbols. This is the same data `yfinance` returns. URL pattern: `https://query1.finance.yahoo.com/v8/finance/chart/{SYMBOL}.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits`. Turnover figures marked "Yahoo" are close x volume from this feed (NSE only).
  - **Groww ETF pages** (`groww.in/etfs/...`), read on 11 Nov 2026. Groww shows TER, AUM, tracking error, NAV and 1-month average volume but **prints no as-of date** for any of them. Launch is given as a year only.
- Figures taken only from search-result summaries (pages not opened) are marked **[snippet]**.
- Rs 1 crore = Rs 10 million. "Rs cr/day" = average daily traded value on NSE.

---

## 1. For each asset class, which NSE ETFs are most liquid, and which is best for a Rs 1-20 lakh order?

### Takeaway
One ETF per class is far more liquid than its peers, and it is almost always the Nippon "BeES" product: NIFTYBEES, JUNIORBEES, MID150BEES, GOLDBEES, SILVERBEES, LTGILTBEES. AUM is a poor guide to tradability (SBI and UTI Nifty ETFs are huge but thinly traded). Gilt ETFs are thin enough that a Rs 20 lakh order is 4-13% of a typical day's turnover, and the three US-index ETFs are trading 18-53% above NAV, so neither class is a clean rotation leg today.

### Cited Findings

**Sources for all tables in this section.** TER, AUM, tracking error (TE) and 1-month average volume: [Groww ETF list](https://groww.in/etfs) and the individual Groww pages linked in each row, read 11 Nov 2026, no as-of date shown. "Yahoo median" = median daily traded value over the last 250 sessions (Nov 2025 to 11 Nov 2026) from the Yahoo chart API. "Groww 1M" = Groww 1-month average volume x last price.

#### 1.1 Nifty 50

| NSE symbol | AMC | Launch | TER | AUM (Rs cr) | TE | Turnover (Rs cr/day) | Notes |
|---|---|---|---|---|---|---|---|
| **NIFTYBEES** | Nippon India | 2001 (Groww "Founded") | 0.05% | 68,029 | 0.02% | ~278 (Groww 1M: 97,14,243 units); 192 (Yahoo median) | [Groww](https://groww.in/etfs/reliance-etf-nifty-bees); [Yahoo](https://query1.finance.yahoo.com/v8/finance/chart/NIFTYBEES.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits) |
| SBINIFTY50 (was SETFNIF50) | SBI | 22 Jul 2015 | 0.05% | 2,07,251 | 0.02% | ~33 (Groww 1M: 12,16,351 units) | [Groww](https://groww.in/etfs/sbietf-nifty). Largest AUM, about 1/8 of NIFTYBEES turnover |
| NIFTYIETF | ICICI Prudential | 2013 | 0.04% | 44,568 | 0.02% | ~30 (Groww 1M: 10,37,166 units) | [Groww](https://groww.in/etfs/icici-prudential-nifty-etf). Yahoo history broken (section 3) |
| NIFTYBETA (was UTINIFTETF) | UTI | not retrieved | 0.06% | 71,671 | 0.02% | ~1.9 (Groww 1M: 67,655 units); 1.7 (Yahoo median) | Rs 71,671 cr AUM but under Rs 2 cr/day traded |
| HDFCNIFTY | HDFC | not retrieved | not retrieved | not retrieved | - | 3.8 (Yahoo median) | [Yahoo](https://query1.finance.yahoo.com/v8/finance/chart/HDFCNIFTY.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits) |
| NIFTY1 | Kotak | Yahoo data from Feb 2010 | not retrieved | not retrieved | - | 4.9 (Yahoo median) | Yahoo names it "Kotak Nifty 50 ETF" |
| NIFTYETF | Mirae Asset | Yahoo data from Nov 2018 | not retrieved | not retrieved | - | 5.4 (Yahoo median) | |
| BSLNIFTY | Aditya Birla SL | Yahoo data from Jul 2011 | 0.06% | 3,291 | 0.05% | 2.5-3.8 (Yahoo 60-day) | Yahoo history corrupted in 2013 (section 4) |
| NIFTYCASE | Zerodha | Yahoo data from 30 Jul 2026 | 0.06% | 71 | 0.16% | ~1 | New, tiny |

- Groww also lists a Groww Nifty 50 ETF (TER 0.20%, AUM Rs 42 cr), Angel One Nifty 50 ETF (0.18%, Rs 20 cr) and JioBlackRock Nifty 50 ETF (shown at 1.09%, Rs 78 cr, a figure that looks wrong and should be checked). — [Groww ETF list](https://groww.in/etfs)
- Other sources disagree slightly on TER: NIFTYBEES 0.04%, SBI 0.04% (Tickertape, as of 12 May 2026), NIFTYIETF 0.02-0.03%, UTI 0.05% **[snippet]**. NIFTYBEES AUM was Rs 57,033 cr on 31 Mar 2026 **[snippet]**. — [Tickertape SBI Nifty 50 ETF](https://www.tickertape.in/etfs/sbi-nifty-50-etf-SBFP); [Sharpely comparison](https://sharpely.in/etfs/compare/icici-prudential-nifty-50-etf-vs-nippon-india-nifty-bees); [1 Finance NIFTYBEES](https://1finance.co.in/product-scoring/mutual-funds/equity/nippon-india-etf-nifty-50-bees)
- **Pick: NIFTYBEES.** Rs 20 lakh is about 0.1% of its median daily turnover. It also has the only intact long Yahoo history in the class (from 2 Jan 2009).

#### 1.2 Nifty Next 50

| NSE symbol | AMC | Launch | TER | AUM (Rs cr) | TE | Turnover (Rs cr/day) | Notes |
|---|---|---|---|---|---|---|---|
| **JUNIORBEES** | Nippon India | 2003 | 0.26% | 8,537 | 0.07% | ~29 (Groww 1M: 3,69,912 units); 29 (Yahoo median) | [Groww](https://groww.in/etfs/reliance-etf-junior-bees); [Yahoo](https://query1.finance.yahoo.com/v8/finance/chart/JUNIORBEES.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits) |
| NEXT50IETF | ICICI Prudential | not retrieved | 0.19% | 2,577 | 0.14% | 5.6 (Yahoo median) | Yahoo history only from 12 Dec 2023 |
| SBINEXT50 (was SETFNN50) | SBI | not retrieved | not retrieved | not retrieved | - | ~2 (Yahoo, 8 sessions) | Yahoo history lost at rename |
| NEXT50BETA | UTI (inferred from the "BETA" naming) | Yahoo data from 15 Dec 2025 | not retrieved | not retrieved | - | 0.8-1.2 (Yahoo 60-day) | |
| HDFCNEXT50 | HDFC | Yahoo data from Aug 2022 | not retrieved | not retrieved | - | 0.7-0.9 | Unadjusted 10x break in Yahoo data |
| ABSLNN50ET | Aditya Birla SL | Yahoo data from Dec 2018 | not retrieved | not retrieved | - | ~0.1 | Effectively untradable |

- **Pick: JUNIORBEES.** Rs 20 lakh is about 0.7% of median daily turnover. Its 0.26% TER (Groww) is the highest in the class, but no rival has even a fifth of its volume.

#### 1.3 Nifty Midcap 150 (and what each "midcap" ticker really tracks)

| NSE symbol | AMC | Index tracked | TER | AUM (Rs cr) | TE | Turnover (Rs cr/day) | Notes |
|---|---|---|---|---|---|---|---|
| **MID150BEES** | Nippon India | **Nifty Midcap 150** (Groww benchmark: "Nifty Midcap 150 TRI") | 0.28% | 3,834 | 0.15% | ~20 (Groww 1M: 8,62,828 units) | [Groww](https://groww.in/etfs/reliance-nippon-life-asset-management-ltd-retfmid). Founded 2019. **Yahoo returns only 15 daily rows** (section 3) |
| MIDCAPETF | Mirae Asset | **Nifty Midcap 150** | 0.17% | 1,817 | 0.09% | 5.9 (Yahoo median) | Yahoo history from 19 Jun 2024 only |
| MIDCAPIETF | ICICI Prudential | **Nifty Midcap 150** | 0.22% | 727 | 0.14% | 2.5 (Yahoo median) | Yahoo history from 28 Jan 2020, 10:1 split recorded |
| MID150CASE | Zerodha | **Nifty Midcap 150** | 0.25% | 265 | 0.08% | 1.3-1.5 | Yahoo from Jun 2024 |
| HDFCMID150 | HDFC | **Nifty Midcap 150** | 0.25% | 152 | 0.04% | ~1 | Yahoo from Mar 2025 |
| MID150 | Kotak | **Nifty Midcap 150** | 0.18% | 13 | 0.06% | 0.1-0.25 | Groww shows a garbage price for it (Rs 16,669) |
| SBIMID150 | SBI (name inferred) | presumably Nifty Midcap 150 | - | - | - | ~0.05 | 8 Yahoo rows |
| MOM100 | Motilal Oswal | **Nifty Midcap 100** (not 150) | 0.34% | 810 | 0.05% | 2.7 (Yahoo median) | Yahoo history from 31 Jan 2011, the longest midcap series |
| MIDCAP | Kotak | **Nifty Midcap 50** (not 150) | 0.35% | 198 | 0.05% | 0.7-0.8 | 74 zero-volume days in the last 250 on Yahoo |
| MIDSELIETF | ICICI Prudential | a "Midcap Select" index per the ticker (name not confirmed) | - | - | - | ~0.4 | Not Midcap 150 |

- Sources: [Groww ETF list](https://groww.in/etfs); [Yahoo MIDCAPIETF.NS](https://query1.finance.yahoo.com/v8/finance/chart/MIDCAPIETF.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits); [Yahoo MOM100.NS](https://query1.finance.yahoo.com/v8/finance/chart/MOM100.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits)
- **Pick: MID150BEES for trading.** Rs 20 lakh is about 1% of daily turnover. Mirae's MIDCAPETF is cheaper (0.17% vs 0.28%) but trades under a third as much.

#### 1.4 Gold

| NSE symbol | AMC | Launch | TER | AUM (Rs cr) | TE | Turnover (Rs cr/day) | Notes |
|---|---|---|---|---|---|---|---|
| **GOLDBEES** | Nippon India | 2007 | **0.81%** | 55,053 | 0.41% | ~320 (Groww 1M: 2,77,32,587 units); 345 (Yahoo median) | [Groww](https://groww.in/etfs/reliance-etf-gold-bees). Highest TER in class |
| GOLDIETF | ICICI Prudential | not retrieved | 0.49% | 26,904 | 0.45% | 73 (Yahoo median) | Yahoo from 12 Dec 2023 |
| SBIGOLD (was SETFGOLD) | SBI | not retrieved | 0.65% | 25,710 | 0.44% | 45-60 (Yahoo 60-day) | Yahoo history lost at rename |
| HDFCGOLD | HDFC | not retrieved | 0.59% | 22,836 | 0.39% | 56 (Yahoo median) | Yahoo from 8 Jun 2023 |
| GOLD1 | Kotak | Yahoo data from Apr 2008 | 0.52% | 13,799 | 0.38% | 28 (Yahoo median) | Yahoo history 18+ years, splits recorded |
| TATAGOLD | Tata | Yahoo data from Jan 2024 | 0.39% | 5,921 | 0.66% | 78 (Yahoo median) | Unit price Rs 13.56 |
| GOLDETF | Mirae Asset | Yahoo data from Sep 2023 | 0.35% | 3,469 | 0.58% | 17-21 | |
| GOLDCASE | Zerodha | Yahoo data from Mar 2024 | 0.35% | 2,522 | 0.58% | 23 (Yahoo median) | |
| GOLDBETA | UTI (inferred from naming) | Yahoo data from May 2018 | not retrieved | not retrieved | - | ~8 | |

- Also on Groww: DSP Gold ETF (0.45%, Rs 2,841 cr) and Groww Gold ETF (0.71%, Rs 457 cr). — [Groww ETF list](https://groww.in/etfs)
- **AXISGOLD returned "symbol may be delisted" on Yahoo** and was not in Groww's 100-row list, so nothing is confirmed for it. — [Yahoo AXISGOLD.NS](https://query1.finance.yahoo.com/v8/finance/chart/AXISGOLD.NS?period1=0&period2=1900000000&interval=1d)
- **Pick: GOLDBEES for liquidity and history; GOLDIETF or HDFCGOLD if the 0.2-0.3%/yr TER saving matters more.** All three absorb Rs 20 lakh easily (under 0.1% of GOLDBEES turnover, under 0.4% of the others).

#### 1.5 Silver

| NSE symbol | AMC | Launch | TER | AUM (Rs cr) | TE | Turnover (Rs cr/day) | Notes |
|---|---|---|---|---|---|---|---|
| **SILVERBEES** | Nippon India | 2022 (Yahoo data from 4 Feb 2022) | 0.58% | 26,991 | 0.79% | ~441 (Groww 1M: 2,49,25,292 units); 640 (Yahoo median) | [Groww](https://groww.in/etfs/nippon-life-india-asset-management-ltd-nippon-india-silver-etf) |
| SILVERIETF | ICICI Prudential | not retrieved | 0.40% | 11,932 | 0.53% | 96 (Yahoo median) | Yahoo from 3 Feb 2025 only |
| HDFCSILVER | HDFC | not retrieved | 0.50% | 6,755 | 0.94% | 85 (Yahoo median) | Yahoo from 3 Mar 2025 only |
| TATSILV | Tata | Yahoo data from Jan 2024 | 0.46% | 4,478 | 1.35% | 126 (Yahoo median) | Yahoo series has unexplained jumps |
| SBISILVER | SBI | Yahoo data from Jul 2024 | 0.41% | 4,913 | 0.95% | 20-24 | |
| SILVER1 | Kotak | Yahoo data from Dec 2022 | 0.35% | 3,120 | 0.60% | 14-19 | Unadjusted 10x break Feb 2026 |
| SILVER | Aditya Birla SL | Yahoo data from 31 Jan 2022 | not retrieved | not retrieved | - | 18-21 | |
| SILVERADD | DSP (matched to Groww's DSP Silver ETF by price) | Yahoo data from Aug 2022 | 0.40% | 1,365 | 0.64% | 7-9 | 10:1 split 28 Aug 2026 recorded on Yahoo |
| SILVERCASE | Zerodha | Yahoo data from Mar 2025 | 0.39% | 1,138 | 1.34% | 16-18 | |

- Silver ETF tracking errors (0.5-1.6%) are 25-80 times those of Nifty ETFs (0.02%). — [Groww ETF list](https://groww.in/etfs)
- **Pick: SILVERBEES.** It is the most traded ETF in this whole note. No silver ETF has more than about 4.8 years of history.

#### 1.6 US / international

| NSE symbol | AMC | Index | Launch | TER | AUM (Rs cr) | Turnover (Rs cr/day) | Price / NAV on 11 Nov 2026 |
|---|---|---|---|---|---|---|---|
| MON100 (was N100) | Motilal Oswal | Nasdaq 100 | 2011 (Yahoo from 29 Mar 2011) | 0.60% | 13,276 | ~32 (Groww 1M); 21 (Yahoo median) | Rs 303.49 vs NAV 256.11 = **+18.5%** |
| MAFANG | Mirae Asset | NYSE FANG+ | 2021 (Yahoo from 14 May 2021) | 0.66% | 4,448 | ~25 (Groww 1M); 4.8 (Yahoo median) | Rs 239.72 vs NAV 159.53 = **+50.3%** |
| MASPTOP50 | Mirae Asset | S&P 500 Top 50 (not the S&P 500) | 2021 (Yahoo from 24 Sep 2021) | 0.65% | 1,154 | ~6.7 (Groww 1M); 1.5 (Yahoo median) | Rs 98.40 vs NAV 64.15 = **+53.4%** |
| HNGSNGBEES | Nippon India | Hang Seng | 2010 (Yahoo from 9 Mar 2010) | 0.98% | 991 | ~3.4 (Groww 1M); 5.8 (Yahoo median) | Rs 451.11 vs NAV 436.57 = +3.3% |
| MAHKTECH | Mirae Asset | Hang Seng TECH | Yahoo from Dec 2021 | 0.65% | 339 | ~1.2 | NAV not captured |
| MONQ50 | Motilal Oswal | Nasdaq Q-50 | Yahoo from Dec 2021 | 0.57% | 172 | 11-22, erratic | See section 2 |

- Sources: [Groww MON100](https://groww.in/etfs/motilal-oswal-mutual-fundmotilal-oswal-most-shares-nasdaq-etf); [Groww MAFANG](https://groww.in/etfs/mirae-asset-nyse-fang-etf); [Groww MASPTOP50](https://groww.in/etfs/mirae-asset-sp-top-etf-masptop); [Groww HNGSNGBEES](https://groww.in/etfs/reliance-etf-hang-seng-bees). The premium column is my arithmetic on Groww's displayed price and NAV. Groww does not date the NAV; for overseas funds it is at least one US session stale, so allow about +/-2 points.
- No plain S&P 500 ETF was found on NSE. Yahoo's symbol lookup for "Motilal Oswal S&P 500" returns only index-fund plans (`0P0001JMZC.BO`), not an exchange-traded symbol. — [Yahoo lookup](https://query1.finance.yahoo.com/v1/finance/search?q=Motilal%20Oswal%20S%26P%20500)
- **Pick: none is suitable as-is.** MON100 is the least bad (deepest volume, longest history, smallest premium). See section 2.

#### 1.7 Gilt / government bond

| NSE symbol | AMC | Index | Launch | TER | AUM (Rs cr) | Turnover (Rs cr/day) | Notes |
|---|---|---|---|---|---|---|---|
| **LTGILTBEES** | Nippon India | Nifty 8-13 yr G-Sec | 2016 (Yahoo from 11 May 2018) | 0.11% | 2,326 | ~4.5 (Groww 1M: 15,21,428 units); 4.6 (Yahoo median) | [Groww](https://groww.in/etfs/reliance-etf-long-term-gilt). Worst day in last 250: Rs 1.0 cr |
| GILT5YBEES | Nippon India | Nifty 5 yr Benchmark G-Sec | 2021 (Yahoo from 7 Apr 2021) | 0.10% | 258 | ~2.3 (Groww 1M); 1.5 (Yahoo median) | [Groww](https://groww.in/etfs/nippon-life-india-asset-management-ltd-netfgilty) |
| LTGILTCASE | Zerodha | Nifty 8-13 yr G-Sec | Yahoo from 30 Jul 2026 | not retrieved | not retrieved | 0.65-0.76 | Too new |
| SBI10YGILT (was SETF10GILT) | SBI | Nifty 10 yr Benchmark G-Sec | not retrieved | not retrieved | not retrieved | 0.1-0.2 | |
| MOGSEC | Motilal Oswal | Nifty 5 yr Benchmark G-Sec | not retrieved | not retrieved | not retrieved | median 0.05 | |
| GSEC10IETF / GSEC5IETF | ICICI Prudential | Nifty 10 yr / 5 yr Benchmark G-Sec | not retrieved | not retrieved | not retrieved | ~0.1 each | GSEC10IETF had 23 zero-volume days in the last 250 |
| LICNETFGSC | LIC MF | Nifty 8-13 yr G-Sec | Yahoo from Dec 2014 | not retrieved | not retrieved | 0.07-0.16 | Longest history, almost no volume |
| GSEC10YEAR | Mirae Asset | Nifty 8-13 yr G-Sec | Yahoo from Sep 2023 | not retrieved | not retrieved | ~0.01 | |
| EBBETF0430 | Edelweiss | Bharat Bond Apr 2030 (AAA PSU bonds, **not gilts**) | Yahoo from 30 Dec 2019 | 0.02% | 23,998 | ~4.0 (Groww 1M); 2.0 (Yahoo median) | Target-maturity: the fund ends in Apr 2030 |
| EBBETF0431 | Edelweiss | Bharat Bond Apr 2031 | Yahoo from 29 Jul 2020 | 0.02% | 12,890 | ~0.9 | |
| BBETF0432 | Edelweiss | Bharat Bond Apr 2032 | Yahoo from 17 Dec 2021 | 0.02% | 10,181 | 0.23 (Yahoo median) | Note the symbol has no leading "E" |
| EBBETF0433 | Edelweiss | Bharat Bond Apr 2033 | Yahoo from 3 Mar 2025 (truncated) | not retrieved | not retrieved | 0.4-0.55 | |

- Index names for the non-Nippon gilt ETFs come from Yahoo's instrument long names. — [Yahoo LTGILTBEES.NS](https://query1.finance.yahoo.com/v8/finance/chart/LTGILTBEES.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits); [Yahoo GILT5YBEES.NS](https://query1.finance.yahoo.com/v8/finance/chart/GILT5YBEES.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits); [Yahoo EBBETF0430.NS](https://query1.finance.yahoo.com/v8/finance/chart/EBBETF0430.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits)
- Groww labels the Bharat Bond "tracking error" as 1.34-1.84%, far above any other fund here; the basis is not explained. — [Groww GILT5YBEES peer table](https://groww.in/etfs/nippon-life-india-asset-management-ltd-netfgilty)
- Matured Bharat Bond and SDL ETFs leave one-row stubs on Yahoo (EBBETF0425 last row 8 Apr 2025; SDL26BEES last row 27 Apr 2026). — [Yahoo EBBETF0425.NS](https://query1.finance.yahoo.com/v8/finance/chart/EBBETF0425.NS?period1=0&period2=1900000000&interval=1d)
- **Pick: LTGILTBEES**, with GILT5YBEES as the shorter-duration option. Rs 20 lakh is about 4% of LTGILTBEES's median daily turnover and about 13% of GILT5YBEES's.
- Liquid ETFs (covered by another researcher), for scale only: LIQUIDBEES Rs 323 cr/day and LIQUIDCASE Rs 206 cr/day (Yahoo medians). — [Groww ETF list](https://groww.in/etfs)

### Inferences
- **Order size as a share of a typical day** (Rs 20 lakh / Yahoo median daily value): GOLDBEES 0.06%, SILVERBEES 0.03%, NIFTYBEES 0.10%, JUNIORBEES 0.7%, MID150BEES ~1%, MON100 ~1%, LTGILTBEES ~4%, MAFANG ~4%, EBBETF0430 ~10%, GILT5YBEES ~13%, MASPTOP50 ~13%. At Rs 1-5 lakh all the "pick" tickers are comfortable; at Rs 20 lakh the gilt leg needs a patient limit order or splitting.
- AUM does not predict tradability. SBI's and UTI's Nifty ETFs hold Rs 2.07 lakh cr and Rs 0.72 lakh cr but trade Rs 33 cr and Rs 2 cr a day, against Rs 190-280 cr for NIFTYBEES at a third of SBI's AUM. Their assets are plausibly institutional buy-and-hold money (commonly said to be EPFO; not verified here).
- TER differences inside equity classes (0.04-0.06% for Nifty 50) are smaller than one bad fill. Liquidity and data quality should decide. Gold is the exception: GOLDBEES at 0.81% costs 0.2-0.3%/yr more than GOLDIETF, HDFCGOLD or GOLD1, and about 0.45%/yr more than the cheapest small funds (Mirae, Zerodha at 0.35%).
- A "gilt" sleeve built on Bharat Bond ETFs is a different exposure (PSU credit, fixed maturity date) and forces a ticker change at maturity. LTGILTBEES is the only constant-duration government-bond ETF with usable volume.
- Groww's TER figures for JUNIORBEES (0.26%), MID150BEES (0.28%) and GOLDBEES (0.81%) are higher than I expected. They are reported as shown; confirm against Nippon's factsheet before quoting them.

### Gaps
- **No AMC factsheet was read**, so TER, AUM and tracking error rest on Groww's undated display. Exact launch/listing dates are missing for most funds. From memory only (unverified): NIFTYBEES Dec 2001, JUNIORBEES Feb 2003, GOLDBEES Mar 2007, MON100 Mar 2011, LTGILTBEES Jul 2016, MID150BEES Jan 2019, GILT5YBEES Apr 2021, MAFANG May 2021, MASPTOP50 Sep 2021, SILVERBEES Feb 2022.
- **No bid-ask spread or impact-cost data was found for any ETF.** NSE publishes impact cost but nseindia.com was unreachable. Daily bars cannot give a spread.
- Not retrieved: TER/AUM for HDFC, Kotak, Mirae and UTI Nifty 50 ETFs; all non-Nippon gilt ETFs; the AMC behind `NEXT50.NS`; anything on AXISGOLD or UTI/Axis silver ETFs.
- Tracking **difference** (return gap vs index) was not found for any fund; Groww shows only tracking error.

---

## 2. Overseas investment limits and the premium-to-NAV problem on international ETFs

### Takeaway
India-listed overseas ETFs cannot create new units while the industry's overseas limits are exhausted, so price is set by demand alone. On 11 Nov 2026 MON100 traded about 18% above NAV and MAFANG and MASPTOP50 about 50% above. Premiums have swung by 15-25 points within weeks, and one small ETF (MONQ50) rose 179% and then hit three straight 20% lower circuits in September 2026. I found no evidence that limits have reopened.

### Cited Findings
- **The limits [snippet].** The industry-wide cap is USD 7 billion for overseas investments by mutual funds, plus a separate USD 1 billion for investments in overseas ETFs. Sources disagree on whether a USD 1 billion ceiling also applies per fund house. When a cap is hit, fund houses cannot create fresh units, demand outstrips supply and prices rise above NAV. — [Business Today, 26 Apr 2026](https://www.businesstoday.in/mutual-funds/story/global-etfs-mafang-sp-500-top-50-trade-at-20-premiums-whats-driving-the-surge-527464-2026-04-26); [1 Finance](https://1finance.co.in/blog/why-are-international-etfs-trading-at-a-premium-understand-the-concept-of-inav/); [Paasa](https://paasa.com/blog/why-indian-international-etfs-trade-at-premium)
- **Status in 2026 [snippet].** No source found says limits were raised or reopened. Reports say the industry is close to the USD 7 billion ceiling; Axis MF paused lump-sum and fresh SIP inflows into some overseas schemes from 6 May 2026; Value Research headlines read "Only one international fund remains open [for] fresh SIPs" and "Global mutual fund SIPs stopped". — [Value Research 229022](https://www.valueresearchonline.com/stories/229022/only-one-international-fund-remains-open-fresh-sips/); [Value Research 229288](https://www.valueresearchonline.com/stories/229288/global-mutual-fund-sips-stopped-what-investors-can-do-now/); [Multibagg](https://www.multibagg.ai/market-pulse/articles/international-sip-halts-etf-premiums-cmsdi5bfy03dg0zoykviv7m0w)
- **Published premium figures [snippet]:**
  - MON100: 9.7% (30 Mar 2026); 19.22% (Apr 2026); 17.4% on 5 Aug 2026 with a 52-week average of 9.3%.
  - MAFANG: 27.7% (Mar 2026); 22.53% (Apr 2026).
  - Headline, 26 Apr 2026: "Global ETFs MAFANG, S&P 500 Top 50 trade at 20% premiums".
  - A Business Standard piece dated 26 Dec 2024 is titled "Wait for NAV and price on exchange to converge before investing".
  — [Business Today, 26 Apr 2026](https://www.businesstoday.in/mutual-funds/story/global-etfs-mafang-sp-500-top-50-trade-at-20-premiums-whats-driving-the-surge-527464-2026-04-26); [Value Research "The premium that never leaves you alone"](https://www.valueresearchonline.com/stories/228263/the-premium-that-never-leaves-you-alone/); [Value Research "The ETF blind spot"](https://www.valueresearchonline.com/stories/227955/the-etf-blind-spot/); [Business Standard, 26 Dec 2024](https://business-standard.com/amp/finance/personal-finance/wait-for-nav-and-price-on-exchange-to-converge-before-investing-124122600876_1.html)
- **Premiums on 11 Nov 2026 (Groww price vs Groww NAV, my arithmetic):** MON100 +18.5%, MAFANG +50.3%, MASPTOP50 +53.4%, HNGSNGBEES +3.3%. — [Groww MON100](https://groww.in/etfs/motilal-oswal-mutual-fundmotilal-oswal-most-shares-nasdaq-etf); [Groww MAFANG](https://groww.in/etfs/mirae-asset-nyse-fang-etf); [Groww MASPTOP50](https://groww.in/etfs/mirae-asset-sp-top-etf-masptop); [Groww HNGSNGBEES](https://groww.in/etfs/reliance-etf-hang-seng-bees)
- **Premium history, estimated (own calculation).** Method: ETF close divided by (previous US index close x USD/INR), scaled so the pre-limit period is zero (MON100: 2019-2021; MAFANG: Jun-Dec 2021). It ignores TER and dividends, so treat it as +/-3 points. It gives +18.4% for MON100 and +47.1% for MAFANG on 11 Nov 2026, matching Groww's NAV-based 18.5% and 50.3%.

  | Year | MON100 median | MON100 range (dates) | MAFANG median | MAFANG range (dates) |
  |---|---|---|---|---|
  | 2022 | +0.4% | -2.6% to +12.9% (13 May 2022) | -0.1% | -3.3% to +4.1% |
  | 2023 | -1.4% | -3.8% to +1.1% | -1.4% | -3.4% to +3.7% |
  | 2024 | -0.9% | -4.8% to +19.4% (31 Dec 2024) | +1.3% | -5.6% to +22.9% (22 Apr 2024) |
  | 2025 | +4.0% | -2.9% to +19.5% (1 Jan 2025) | +16.5% | +7.9% to +24.4% (3 Jan 2025) |
  | 2026 to 11 Nov | +15.8% | -3.9% (5 Mar) to +25.2% (8 Sep) | +17.4% | +11.2% (16 Apr) to +56.1% (12 Oct) |

  — data: [Yahoo MON100.NS](https://query1.finance.yahoo.com/v8/finance/chart/MON100.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits); [Yahoo MAFANG.NS](https://query1.finance.yahoo.com/v8/finance/chart/MAFANG.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits); [Yahoo ^NDX](https://query1.finance.yahoo.com/v8/finance/chart/%5ENDX?period1=0&period2=1900000000&interval=1d); [Yahoo ^NYFANG](https://query1.finance.yahoo.com/v8/finance/chart/%5ENYFANG?period1=0&period2=1900000000&interval=1d); [Yahoo USDINR=X](https://query1.finance.yahoo.com/v8/finance/chart/USDINR=X?period1=0&period2=1900000000&interval=1d)
- **MONQ50, September 2026 (Yahoo closes).** Rs 141.93 on 4 Sep, Rs 396.30 on 18 Sep (+179% in nine sessions, the last three each about +20%), then Rs 317.04, 253.64 and 202.92 on 21-23 Sep (three consecutive -20% days). The fund has only Rs 172 cr of AUM. INDmoney covered it as "The curtain falls on Motilal Oswal Nasdaq Q50 ETF's absurd rally: what happens when an ETF premium unwinds". — [Yahoo MONQ50.NS](https://query1.finance.yahoo.com/v8/finance/chart/MONQ50.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits); [INDmoney](https://www.indmoney.com/blog/mutual-funds/why-motilal-oswal-nasdaq-q50-etf-premium-is-unwinding); [Groww ETF list](https://groww.in/etfs)
- **Price-band rule change [snippet].** A rule effective 7 Sep 2026 links the ETF price band to the previous closing price, so an overseas ETF already at a premium can move further from NAV. MONQ50's run began on 7 Sep 2026. — [Multibagg](https://www.multibagg.ai/market-pulse/articles/international-sip-halts-etf-premiums-cmsdi5bfy03dg0zoykviv7m0w)
- An NSE release dated 25 Sep 2026 warned about international ETFs trading at large premiums after overseas limits were exhausted (per a blog, already cited in the earlier note); Cafemutual reports Mirae Asset itself warning investors about overseas ETFs. — [Belong blog](https://getbelong.com/blog/us-stocks-etfs/why-etfs-trade-at-premium-or-discount/); [Cafemutual](https://cafemutual.com/news/industry/38774-mirae-asset-warns-investors-about-overseas-etfs)
- MAFANG's daily high equals its daily low on more than half of the last 250 sessions in Yahoo's data (median range 0.00%; MASPTOP50 0.56%). — [Yahoo MAFANG.NS](https://query1.finance.yahoo.com/v8/finance/chart/MAFANG.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits)
- **LRS proposal [snippet].** Reports in October 2026 say the RBI proposed removing investment remittances from the automatic LRS route; no circular or effective date exists yet. — [Multibagg](https://www.multibagg.ai/market-pulse/articles/international-sip-halts-etf-premiums-cmsdi5bfy03dg0zoykviv7m0w)

### Inferences
- **A momentum signal on these tickers measures premium as much as the index.** MON100's premium moved from about -4% (March 2026) to +25% (September 2026). A rotation rule ranking on trailing return would have read that as US outperformance and bought near the premium peak.
- A buyer at an 18-50% premium loses that amount if limits are raised and creation resumes, regardless of what the Nasdaq does. The loss can arrive in days and through lower circuits, as MONQ50 showed, so a stop-loss will not execute.
- Backtests over 2011-2023 on MON100 look clean because the premium was near zero (median within +/-1.5% in 2022-2024). That history says little about the instrument as it trades now.
- Practical options for the bot: (a) exclude the international sleeve; (b) allow MON100 only when price is within a small band (say 2-3%) of the previous NAV, which in 2026 would have kept it out almost all year; (c) get US exposure outside the ETF wrapper (not researched here). The MAFANG flat-range observation may mean it often sits locked at its price band, which would make it hard to enter or exit on a chosen day; it could also be a Yahoo data fault.
- HNGSNGBEES shows only a ~3% premium on Groww's NAV. My index-ratio method overstates its premium (about +13%) because the fund tracks a total-return index while Yahoo's `^HSI` excludes Hang Seng's 3-4% dividend yield, so that estimate is discarded.

### Gaps
- **The regulatory timeline was not sourced.** From memory, unverified: SEBI told AMCs to stop fresh overseas subscriptions from about 2 Feb 2022 when the USD 7 billion cap neared; partial reopening followed in mid-2022 up to the headroom as of 1 Feb 2022; and the USD 1 billion overseas-ETF cap led to a stop on fresh subscriptions in schemes investing in overseas ETFs from 1 Apr 2024. Confirm each against SEBI/AMFI letters.
- Which specific ETFs currently accept creation by market makers, and since when each stopped, was not found.
- No iNAV history was available; the premium series above is an estimate. MASPTOP50 has no free benchmark on Yahoo, so only the single 11 Nov 2026 reading exists.
- The text and number of the NSE price-band circular (effective 7 Sep 2026) and the 25 Sep 2026 NSE release were not retrieved.

---

## 3. Launch dates, usable price history on Yahoo, and ticker renames

### Takeaway
Yahoo's history often starts at the last symbol rename, not at launch, and for two otherwise attractive tickers (MID150BEES and NIFTYIETF) it currently returns only a few weeks of data. NIFTYBEES, JUNIORBEES and GOLDBEES have about 17.9 years on Yahoo; MON100 15.6; SILVERBEES 4.8; GILT5YBEES 5.6; LTGILTBEES 8.5. SBI's ETFs were renamed around 30 Oct 2026 and their Yahoo history is gone.

### Cited Findings
- **Yahoo daily history for the recommended tickers (first row to 11 Nov 2026):**

  | Ticker | First Yahoo row | Rows | Years | Fund founded (Groww) |
  |---|---|---|---|---|
  | NIFTYBEES.NS | 2 Jan 2009 | 4,401 | 17.9 | 2001 |
  | JUNIORBEES.NS | 2 Jan 2009 | 4,401 | 17.9 | 2003 |
  | GOLDBEES.NS | 2 Jan 2009 | 4,400 | 17.9 | 2007 |
  | LIQUIDBEES.NS | 2 Jan 2009 | 4,401 | 17.9 | - |
  | MON100.NS | 29 Mar 2011 | 3,850 | 15.6 | 2011 |
  | HNGSNGBEES.NS | 9 Mar 2010 | 4,111 | 16.7 | 2010 |
  | MOM100.NS (Midcap 100) | 31 Jan 2011 | 3,887 | 15.8 | - |
  | LTGILTBEES.NS | 11 May 2018 | 1,839 | 8.5 | 2016 |
  | GILT5YBEES.NS | 7 Apr 2021 | 1,376 | 5.6 | 2021 |
  | SILVERBEES.NS | 4 Feb 2022 | 1,176 | 4.8 | 2022 |
  | MAFANG.NS | 14 May 2021 | 1,357 | 5.5 | 2021 |
  | MASPTOP50.NS | 24 Sep 2021 | 1,265 | 5.1 | 2021 |
  | MIDCAPIETF.NS (Midcap 150) | 28 Jan 2020 | 1,676 | 6.8 | - |
  | **MID150BEES.NS** | **22 Sep 2026** | **15** | **0.1** | 2019 |

  — [Yahoo NIFTYBEES.NS](https://query1.finance.yahoo.com/v8/finance/chart/NIFTYBEES.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits); [Yahoo MID150BEES.NS](https://query1.finance.yahoo.com/v8/finance/chart/MID150BEES.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits); same URL pattern for the rest; founding years from [Groww](https://groww.in/etfs)
- **MID150BEES.NS and NIFTYIETF.NS are effectively empty on Yahoo.** MID150BEES returned 15 daily rows (22 Sep to 11 Nov 2026) on two pulls and with `range=10y`. NIFTYIETF returned 7 rows from 2 Nov 2026 with `period1=0` and 15 rows from 22 Sep 2026 in a calendar-year request, although Yahoo's metadata gives its first trade date as March 2013. The `.BO` versions return one row. — [Yahoo MID150BEES.NS range=10y](https://query1.finance.yahoo.com/v8/finance/chart/MID150BEES.NS?range=10y&interval=1d); [Yahoo NIFTYIETF.NS](https://query1.finance.yahoo.com/v8/finance/chart/NIFTYIETF.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits)
- **SBI rename, about 30 Oct 2026.** Groww lists the SBI Nifty 50 ETF with NSE code `SBINIFTY50` while its short name is still "SETFNIFTY". On Yahoo the new symbols start on 30 Oct 2026 (8 rows) and the old ones stop on 4 Nov 2026 and themselves begin only on 17 Jul 2026:
  - SETFNIF50 -> SBINIFTY50
  - SETFGOLD -> SBIGOLD
  - SETFNN50 -> SBINEXT50
  - SETF10GILT -> SBI10YGILT
  — [Groww SBI Nifty 50 ETF](https://groww.in/etfs/sbietf-nifty); [Yahoo SBINIFTY50.NS](https://query1.finance.yahoo.com/v8/finance/chart/SBINIFTY50.NS?period1=0&period2=1900000000&interval=1d); [Yahoo SETFNIF50.NS](https://query1.finance.yahoo.com/v8/finance/chart/SETFNIF50.NS?period1=0&period2=1900000000&interval=1d); [Yahoo lookup for SBI 10 yr G-Sec ETF](https://query1.finance.yahoo.com/v1/finance/search?q=SBI%20Nifty%2010%20yr%20Benchmark%20G-Sec%20ETF)
- **UTI rename.** The UTI Nifty 50 ETF trades as `NIFTYBETA` (Groww slug `uti-mutual-fund-uti-nifty-etf`; Trendlyne files its split history under NIFTYBETA). `UTINIFTETF.NS` and `UTINEXT50.NS` return "symbol may be delisted". Yahoo history for NIFTYBETA and NEXT50BETA starts 15 Dec 2025; GOLDBETA goes back to May 2018; Groww also shows SENSEXBETA. — [Groww NIFTYBEES peer table](https://groww.in/etfs/reliance-etf-nifty-bees); [Trendlyne](https://trendlyne.com/equity/Split/NIFTYBETA/1772/uti-nifty-50-etf-split); [Yahoo NIFTYBETA.NS](https://query1.finance.yahoo.com/v8/finance/chart/NIFTYBETA.NS?period1=0&period2=1900000000&interval=1d)
- **Other old symbols now dead on Yahoo** ("No data found, symbol may be delisted"): N100, KOTAKGOLD, KOTAKNIFTY, ICICIGOLD, HDFCMFGETF, ICICISILVE, KOTAKSILVE. Their successors' Yahoo histories start late: HDFCGOLD and HDFCNIFTY on 8 Jun 2023; GOLDIETF and NEXT50IETF on 12 Dec 2023; SILVERIETF and GSEC10IETF on 3 Feb 2025; HDFCSILVER, HDFCMID150 and MOGSEC on 3 Mar 2025. — [Yahoo N100.NS](https://query1.finance.yahoo.com/v8/finance/chart/N100.NS?period1=0&period2=1900000000&interval=1d); [Yahoo HDFCGOLD.NS](https://query1.finance.yahoo.com/v8/finance/chart/HDFCGOLD.NS?period1=0&period2=1900000000&interval=1d); [Yahoo GOLDIETF.NS](https://query1.finance.yahoo.com/v8/finance/chart/GOLDIETF.NS?period1=0&period2=1900000000&interval=1d)
- **Nippon / Reliance / Goldman Sachs lineage.** The BeES symbols themselves did not change. The December 2019 NSE Clearing circular names the AMC as "Reliance Nippon Life Asset Management Limited" and the funds as "Nippon India ETF ...". The ISINs did change at the split: NIFTYBEES went from INF732E01011 to INF204KB14I2 and GOLDBEES from INF732E01102 to INF204KB17I5. Groww's URL slugs still read `reliance-etf-nifty-bees`, `reliance-etf-gold-bees`, `reliance-etf-junior-bees`. — [NSE Clearing circular NCL/CMPT/42889](https://nsearchives.nseindia.com/content/circulars/CMPT42889.pdf); [Groww NIFTYBEES](https://groww.in/etfs/reliance-etf-nifty-bees)
- Groww's page for GILT5YBEES labels it "NETFGILT5Y" in one place, and its slugs for MID150BEES and MOM100 end in `retfmid` and `most-shares-m-etf`. — [Groww GILT5YBEES](https://groww.in/etfs/nippon-life-india-asset-management-ltd-netfgilty); [Groww ETF list](https://groww.in/etfs)

### Inferences
- Those Groww fragments suggest earlier symbols NETFGILT5Y -> GILT5YBEES, RETFMID150 -> MID150BEES and M100 -> MOM100 (and N100 -> MON100, KOTAKGOLD -> GOLD1, KOTAKNIFTY -> NIFTY1, HDFCMFGETF -> HDFCGOLD, ICICIGOLD -> GOLDIETF). The pairings are inferred from slugs, dead symbols and matching fund names; none was confirmed against an NSE symbol-change circular.
- The start dates of 8 Jun 2023 (HDFC) and 12 Dec 2023 (ICICI) look like rename dates; the 3 Feb 2025 and 3 Mar 2025 starts look like Yahoo truncation, since those funds are older.
- **Backtest design consequence.** Only NIFTYBEES, JUNIORBEES, GOLDBEES, MON100 and LIQUIDBEES give 15+ years on Yahoo. A common window that includes SILVERBEES starts in February 2022, about 57 monthly observations, which is too few to validate a monthly rotation rule. Longer tests need index data (niftyindices.com TRI, MCX or LBMA silver) spliced before the ETF's start.
- For midcap, Yahoo offers MOM100 (Midcap 100, from 2011) or MIDCAPIETF (Midcap 150, from 2020) as signal proxies while trading MID150BEES. NSE bhavcopy is the fix for MID150BEES itself.
- **Key instruments on ISIN, and re-check symbols before each run.** A rename (SBI in Oct 2026, UTI in Dec 2025) silently breaks a Yahoo download; the old symbol goes stale or "delisted" and the new one starts empty.

### Gaps
- No NSE circular was retrieved for the SBI, UTI, HDFC, ICICI, Kotak or Motilal symbol changes, so the exact effective dates are unknown.
- Whether the MID150BEES / NIFTYIETF gap on Yahoo is temporary is unknown. In my recollection these tickers had full Yahoo history in earlier years.
- Exact inception and listing dates were not confirmed from any AMC document (see section 1 gaps).

---

## 4. Unit splits and face-value changes: what happened, and does Yahoo handle them?

### Takeaway
The December 2019 Nippon splits are confirmed from the NSE Clearing circular: NIFTYBEES 1:10 and GOLDBEES 1:100, ex-date 19 Dec 2019, record date 20 Dec 2019. JUNIORBEES and LIQUIDBEES were not split. Yahoo's NIFTYBEES and GOLDBEES series are back-adjusted but each contains **two corrupt days (19 and 20 Dec 2019)** that are 10x or 100x too low, and Yahoo records no split event for either. Several other ETFs have splits Yahoo did not adjust at all.

### Cited Findings
- **NSE Clearing circular NCL/CMPT/42889 (Circular 368/2019), dated 12 Dec 2019.** Record date 20 Dec 2019; ex-date 19 Dec 2019 (settlement N 2019238); new ISINs issued.

  | Symbol | Face value change | Ratio |
  |---|---|---|
  | NIFTYBEES | Rs 10 -> Re 1 | 1 old unit = 10 new |
  | BANKBEES | Rs 10 -> Re 1 | 1:10 |
  | PSUBNKBEES | Rs 10 -> Re 1 | 1:10 |
  | NETFNV20 | Rs 10 -> Re 1 | 1:10 |
  | HNGSNGBEES | Rs 10 -> Re 1 | 1:10 |
  | GOLDBEES | Rs 100 -> Re 1 | 1 old unit = 100 new |

  JUNIORBEES and LIQUIDBEES are not in the circular. — [NSE Clearing circular](https://nsearchives.nseindia.com/content/circulars/CMPT42889.pdf)
- Trendlyne lists the NIFTYBEES and GOLDBEES ex-date as 19 Dec 2019, and JUNIORBEES's last split as Rs 10 -> Rs 1.25 in 2004 **[snippet]**. Business Standard carried the GOLDBEES Rs 100 -> Re 1 record-date announcement **[snippet]**. — [Trendlyne NIFTYBEES](https://trendlyne.com/equity/Split/NIFTYBEES/1588/nippon-india-etf-nifty-50-bees-split); [Trendlyne GOLDBEES](https://trendlyne.com/equity/Split/GOLDBEES/1582/nippon-india-etf-gold-bees-split); [Trendlyne JUNIORBEES](https://trendlyne.com/equity/Split/JUNIORBEES/1584/nippon-india-etf-nifty-next-50-junior-bees-split); [Business Standard](https://business-standard.com/markets/nippon-india-etf-gold-bees-share-price-28235/announcements/bse-exchange-26630571)
- **Yahoo around the split (raw closes; adjusted close is identical):**

  | Date | NIFTYBEES.NS | GOLDBEES.NS |
  |---|---|---|
  | 18 Dec 2019 | 129.25 | 33.596 |
  | **19 Dec 2019** | **13.02** | **0.336** |
  | **20 Dec 2019** | **13.03** | **0.336** |
  | 23 Dec 2019 | 129.93 | 33.65 |

  The `events` block is empty for both tickers (no splits, no dividends). BANKBEES (328.7 -> 32.95 -> 330.71) and HNGSNGBEES (321.9 -> 36.61 -> 351.39) show the same two-day fault. — [Yahoo NIFTYBEES.NS](https://query1.finance.yahoo.com/v8/finance/chart/NIFTYBEES.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits); [Yahoo GOLDBEES.NS](https://query1.finance.yahoo.com/v8/finance/chart/GOLDBEES.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits); [Yahoo BANKBEES.NS](https://query1.finance.yahoo.com/v8/finance/chart/BANKBEES.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits)
- **MON100.NS has the same pattern in June 2021:** 101.56 (16 Jun) -> 10.09 (17 Jun) -> 10.42 (18 Jun) -> 103.41 (21 Jun), with no split event recorded. — [Yahoo MON100.NS](https://query1.finance.yahoo.com/v8/finance/chart/MON100.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits)
- **Splits Yahoo records as events** (series adjusted, no discontinuity found):
  - MIDCAPIETF 10:1 and MIDSELIETF 10:1, both 10 May 2024.
  - GOLD1 10:1 on 22 Jul 2021 (plus a meaningless "10:10" on 13 Apr 2015).
  - GOLDBETA 100:1 on 25 Mar 2021.
  - SILVERADD 10:1 on 28 Aug 2026.
  — [Yahoo MIDCAPIETF.NS](https://query1.finance.yahoo.com/v8/finance/chart/MIDCAPIETF.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits); [Yahoo GOLD1.NS](https://query1.finance.yahoo.com/v8/finance/chart/GOLD1.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits)
- **10x / 100x breaks Yahoo left unadjusted** (no split event; everything before the date is on the old scale):

  | Ticker | Date | Close before -> after |
  |---|---|---|
  | HDFCNEXT50 | 20 Oct 2023 | 452.70 -> 44.85 |
  | BSLGOLDETF | 25 Nov 2021 | 4,348.65 -> 43.65 |
  | LICMFGOLD | 9 Mar 2026 | 14,401.80 -> 142.00 |
  | GROWWGOLD | 2 Feb 2026 | 157.42 -> 14.06 |
  | MIDCAP (Kotak Midcap 50) | 27 Feb 2026 | 173.63 -> 17.22 |
  | SILVER1 (Kotak Silver) | 27 Feb 2026 | 249.55 -> 25.75 |

  — [Yahoo HDFCNEXT50.NS](https://query1.finance.yahoo.com/v8/finance/chart/HDFCNEXT50.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits); [Yahoo SILVER1.NS](https://query1.finance.yahoo.com/v8/finance/chart/SILVER1.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits); [Yahoo LICMFGOLD.NS](https://query1.finance.yahoo.com/v8/finance/chart/LICMFGOLD.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits)
- A BSE circular dated 20 Feb 2026 covers "split of units / change in face value of Kotak Nifty Bank ETF", consistent with a Kotak-wide split a week before the 27 Feb 2026 breaks **[snippet, title only]**. — [BSE circular index](https://rhnvrm.github.io/stock-market-circulars/circulars/bse/2026/bse-2026-02-20-b2e7b041b165002f-split-of-units-change-in-face-value-of-kotak-nifty-bank-etf-scheme)
- Other splits known only from titles **[snippet]**: UTI Nifty 50 ETF face-value split (Value Research); Quantum Nifty 50 ETF split in 2026 (TradingQnA). — [Value Research](https://www.valueresearchonline.com/stories/53218/uti-nifty-50-etf-splits-its-face-value-will-it-affect-you/); [TradingQnA](https://tradingqna.com/t/everything-you-need-to-know-about-the-quantum-nifty-50-etf-stock-split-2026/191403)
- **Other bad Yahoo data seen:**
  - BSLNIFTY.NS flips between about Rs 5.5 and Rs 60 on 195 days in 2013.
  - QGOLDHALF.NS has a two-day 50x drop on 16-20 Dec 2021.
  - ABSLNN50ET.NS has a two-day 10x drop on 25-29 Nov 2021.
  - TATSILV.NS has +33% and +55% one-day jumps on 4 Nov 2024 and 10 Nov 2025 that no other silver ETF shows.
  - Most tickers have one or two zero-volume rows a year.
  — [Yahoo BSLNIFTY.NS](https://query1.finance.yahoo.com/v8/finance/chart/BSLNIFTY.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits); [Yahoo TATSILV.NS](https://query1.finance.yahoo.com/v8/finance/chart/TATSILV.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits)
- **No 10x-type break** was found in JUNIORBEES, LIQUIDBEES, SILVERBEES, MAFANG, MASPTOP50, LTGILTBEES, GILT5YBEES, the Bharat Bond ETFs, NIFTYETF, HDFCNIFTY, HDFCGOLD or GOLDIETF over the history Yahoo holds. — [Yahoo JUNIORBEES.NS](https://query1.finance.yahoo.com/v8/finance/chart/JUNIORBEES.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits)
- **Real moves that look like splits but are not.** Every silver ETF on Yahoo fell about 19% on 30 Jan 2026 and about 23% on 2 Feb 2026 (SILVERBEES 351.91 -> 286.48 -> 219.94). Groww's 52-week high for SILVERBEES is Rs 360.00, consistent with the pre-crash level. — [Yahoo SILVERBEES.NS](https://query1.finance.yahoo.com/v8/finance/chart/SILVERBEES.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits); [Groww SILVERBEES](https://groww.in/etfs/nippon-life-india-asset-management-ltd-nippon-india-silver-etf)

### Inferences
- **Yahoo's adjusted close does not handle these correctly, and it fails in two different ways.** For the BeES funds and MON100 the long history is right but two post-split days are double-divided. For HDFCNEXT50, BSLGOLDETF, LICMFGOLD, GROWWGOLD and the Kotak pair, the split is not applied at all. Because no split event is recorded, `yfinance`'s `actions` output cannot be used to detect either case.
- Effect on a monthly rotation backtest: the two bad December 2019 days create a fake -90% / +900% daily return pair for NIFTYBEES and -99% / +9,900% for GOLDBEES. They fall mid-month, so month-end momentum is unaffected, but any daily volatility, drawdown, moving-average or stop calculation is wrecked. MON100's bad days are 17-18 Jun 2021.
- **Recommended data hygiene.** Hard-code repairs for 19-20 Dec 2019 (multiply NIFTYBEES, BANKBEES, HNGSNGBEES by 10 and GOLDBEES by 100) and 17-18 Jun 2021 (MON100 x10). Then run a generic guard: flag any daily ratio outside 0.83-1.2, classify ratios near 0.1/10 or 0.01/100 as split artefacts, and treat the rest (silver in Jan-Feb 2026, MONQ50 in Sep 2026) as real. `yfinance`'s `repair=True` targets 100x errors and may catch GOLDBEES; whether it catches the 10x cases was not tested.
- The MON100 pattern implies a 1:10 unit split with an ex-date around 17 Jun 2021, but no circular was retrieved.
- The SILVERBEES crash shows a filter that simply deletes moves over 20% would erase a genuine 37% two-day loss.

### Gaps
- No circular was retrieved for any split other than the December 2019 Nippon one. Ratios and dates for MON100 (2021), UTI, HDFC, Aditya Birla (2021), LIC, Groww, Kotak (Feb 2026) and DSP (Aug 2026) are inferred from price breaks or Yahoo events only.
- Whether MID150BEES, NIFTYIETF or the SBI ETFs have ever split could not be checked because Yahoo holds almost no history for them. Indirect evidence against an SBI Nifty 50 ETF split: Groww shows its all-time low as Rs 68.4 on 29 Feb 2016, about 1/100 of the Nifty then, the same ratio as today. — [Groww SBI Nifty 50 ETF](https://groww.in/etfs/sbietf-nifty)
- No GitHub issue or forum report specifically about these `.NS` ETF glitches was found (searches ran out). The evidence is the direct pull.
- No news source was retrieved for the Jan-Feb 2026 silver crash; it is corroborated only by eight ETFs moving together and Groww's 52-week range.

---

## 5. Practical traps: price vs NAV/iNAV, market makers, the Rs 25 crore rule, thin volume, tracking error vs tracking difference

### Takeaway
You trade with other investors at the market price, not with the fund at NAV, and SEBI's rules push every order under Rs 25 crore onto the exchange. Even the largest ETFs have closed several percent away from fair value in stress (NIFTYBEES in March 2020; silver ETFs 5-12% rich in October 2025). The defence is a limit order near iNAV on a liquid ticker, placed away from the open and close, plus a check that price is near NAV before buying.

### Cited Findings
- **SEBI circular of 23 May 2022, "Development of passive funds" [snippet]:**
  - Direct subscription or redemption with the AMC only for amounts above Rs 25 crore; smaller investors must use the exchange. The threshold does not apply to market makers.
  - Implementation was deferred from 1 Jul 2022 to 1 Nov 2022 and then to 1 May 2023, when the exchange route became compulsory for deals under Rs 25 crore.
  - AMCs must appoint at least two market makers per ETF.
  — [Business Standard, May 2023](https://www.business-standard.com/india-news/after-two-deferments-exchange-route-compulsory-for-sub-rs-25-cr-etf-deals-123050100756_1.html); [Taxmann](https://taxmann.com/post/blog/etfs-units-direct-transaction-with-amcs-shall-be-facilitated-only-for-transactions-above-rs-25-cr-sebi); [Morningstar India](https://www.morningstar.in/posts/68444/sebi-issues-new-norms-for-passive-funds.aspx); [Business Standard, May 2022](https://business-standard.com/amp/article/markets/passive-funds-set-for-boost-as-sebi-eases-market-making-nfo-and-etf-rules-122052401459_1.html)
- **Tracking error vs tracking difference under that circular [snippet]:**
  - Tracking error = annualised standard deviation of the daily return difference between the index and the fund's **NAV**, on one-year rolling data. It must stay within 2% for equity ETFs and index funds and be disclosed daily on AMC and exchange websites.
  - Tracking difference = the annualised return gap. It must be disclosed monthly; for debt ETFs and index funds the one-year average must not exceed 1.25%.
  — [Moneylife](https://moneylife.in/article/sebi-tracking-error-of-equity-etfs-and-index-funds-cannot-exceed-2-percentage/67279.html); [Business Standard](https://www.business-standard.com/amp/article/markets/sebi-issues-new-norms-for-constitution-disclosure-of-passive-funds-122052301663_1.html)
- **Displayed tracking errors (Groww, undated):** Nifty 50 ETFs 0.02%; JUNIORBEES 0.07%; MID150BEES 0.15%; gold 0.38-0.66%; silver 0.53-1.57%; LTGILTBEES 0.18%; MON100 0.20%; MAFANG 0.04% and MASPTOP50 0.07% (while trading about 50% above NAV). — [Groww ETF list](https://groww.in/etfs)
- **NAV-based vs price-based tracking.** Freefincal measured NIFTYBEES tracking error for May 2019 to Apr 2020 at 0.16% on NAV but 5.6% on traded price. — [Freefincal](https://freefincal.com/nippon-india-etf-nifty-bees-vs-uti-nifty-index-fund-which-is-better/)
- **March 2020, NIFTYBEES (own calculation).** NIFTYBEES close divided by Nifty 50 close, relative to 28 Feb 2020: +4.5% on 16 Mar, +3.9% on 17 Mar, **+6.5% on 18 Mar**, +1.7% on 19 Mar, -0.2% on 20 Mar, +3.1% on 23 Mar, -1.1% on 27 Mar, -1.3% on 7 Apr 2020. In the first half of March the gap stayed within +/-0.3%. — data: [Yahoo NIFTYBEES.NS](https://query1.finance.yahoo.com/v8/finance/chart/NIFTYBEES.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits); [Yahoo ^NSEI](https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI?period1=0&period2=1900000000&interval=1d)
- **Silver, October 2025:**
  - On Thursday 9 Oct 2025 Nippon's silver ETF closed at Rs 156 against an iNAV of Rs 148.3, about 5.5% above (Yahoo shows the same close, 156.16).
  - Silver ETFs from HDFC, Tata and UTI were at premiums of 10% or more.
  - Business Standard put the range at 5-12% and attributed it to a physical silver shortage in India.
  - Kotak MF stopped lump-sum and switch-in subscriptions to its silver ETF fund-of-funds.
  - A forum post on 16 Oct 2025 reported another silver ETF about 6% **below** iNAV.
  — [Business Standard, 9 Oct 2025](https://www.business-standard.com/markets/news/silver-etfs-trade-at-steep-premiums-amid-global-supply-squeeze-125100901276_1.html); [Business Standard, 13 Oct 2025](https://www.business-standard.com/finance/personal-finance/paying-too-much-silver-etfs-look-shiny-but-mind-the-5-12-premium-risk-125101300184_1.html); [Business Today, 9 Oct 2025](https://www.businesstoday.in/mutual-funds/story/your-silver-etf-is-not-tracking-silver-wealth-manager-warns-investors-as-premiums-skyrocket-amid-record-rally-497595-2025-10-09); [TradingQnA](https://tradingqna.com/t/why-are-some-gold-and-silver-etfs-trading-below-i-nav/187720)
- **Cross-ETF dispersion in the same episode (own calculation).** These funds hold the same metal, so differences in their returns are premium changes. Relative to SILVERBEES since 15 Sep 2025: SBISILVER was 3.7% behind and SILVERADD 3.2% behind on 14 Oct 2025; ESILVER was 3.5% ahead on 15 Oct 2025. SILVERBEES itself went 143.82 (7 Oct) -> 174.31 (14 Oct) -> 141.94 (23 Oct). Gold ETFs over 10-23 Oct 2025 stayed within about +/-0.6% of GOLDBEES, with one TATAGOLD reading of +1.3% on 21 Oct. — data: [Yahoo SILVERBEES.NS](https://query1.finance.yahoo.com/v8/finance/chart/SILVERBEES.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits); [Yahoo SBISILVER.NS](https://query1.finance.yahoo.com/v8/finance/chart/SBISILVER.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits); [Yahoo GOLDBEES.NS](https://query1.finance.yahoo.com/v8/finance/chart/GOLDBEES.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits)
- **Silver crash, 30 Jan and 2 Feb 2026 (own calculation).** On 30 Jan 2026 HDFCSILVER and TATSILV closed 3.1% and 4.4% rich to SILVERBEES while SBISILVER closed 3.1% cheap; on 2 Feb the HDFC gap reversed to -2.8%. — data: [Yahoo HDFCSILVER.NS](https://query1.finance.yahoo.com/v8/finance/chart/HDFCSILVER.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits)
- **Thin trading.** Zero-volume sessions in the last 250: Kotak Midcap 50 ETF 74, Zerodha Silver ETF 41, ICICI 10-yr G-Sec ETF 23, ABSL 10-yr gilt ETF 77. Median daily value is under Rs 0.25 cr for BBETF0432, GSEC10IETF, GSEC5IETF, LICNETFGSC, MOGSEC and GSEC10YEAR. — [Yahoo GSEC10IETF.NS](https://query1.finance.yahoo.com/v8/finance/chart/GSEC10IETF.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits); [Yahoo MIDCAP.NS](https://query1.finance.yahoo.com/v8/finance/chart/MIDCAP.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits)
- **Where iNAV shows up.** Zerodha's Kite displays a "nudge" comparing price with iNAV for ETFs such as MON100 **[snippet, thread title]**. Groww's ETF page shows the previous NAV beside the live price, which is enough for a premium check but is not a live iNAV. — [TradingQnA](https://tradingqna.com/t/kite-nudge-for-mon100-etf-inav/130815); [Groww MON100](https://groww.in/etfs/motilal-oswal-mutual-fundmotilal-oswal-most-shares-nasdaq-etf)

### Inferences
- **The published tracking error is the wrong number for a trader.** It compares NAV with the index. MAFANG's 0.04% sits beside a 50% premium. What the bot earns is the price return, so the check that matters is price vs NAV or iNAV at the moment of trading.
- For commodity ETFs the creation mechanism depends on physical metal. When silver was scarce in October 2025, market makers could not create units and premiums of 5-12% appeared even on the largest fund. A rotation rule that buys silver after a strong month is most likely to trade exactly then.
- The March 2020 gaps are close-to-close and could partly reflect closing-auction timing, but several-percent readings on five separate days agree with Freefincal's price-based 5.6% tracking error for that year.
- **Execution rules that follow:**
  - Use limit orders, never market orders. Reference the live iNAV where available, otherwise the last NAV adjusted by the index move.
  - Trade between roughly 10:00 and 15:00, avoiding the open and close.
  - Skip or defer the trade if price is more than about 0.5% from iNAV for Nifty, Next 50 or gold; allow about 1% for midcap, silver and gilt.
  - Apply a hard premium cap to anything international.
  - On gilt ETFs, split a Rs 20 lakh order or leave a resting limit.
- A monthly bot can afford patience. Missing a day costs little; paying a 2% premium costs more than a year of TER on every fund here.

### Gaps
- **The SEBI circular text was not read** (the guessed SEBI URL returned 404). Not confirmed: the iNAV disclosure frequency, market-maker spread and quote obligations, incentives, and whether the Rs 25 crore threshold has been revised since 2023. From memory, unverified: iNAV must be published on the exchange with at most a 15-second lag for equity ETFs and at least four times a day for debt ETFs.
- No live iNAV feed URL was verified. NSE's ETF pages and AMC sites are the usual places, but both were unreachable. Whether Groww's app shows live iNAV was not confirmed.
- No measured bid-ask spreads or impact costs.
- No news account of ETF dislocations in March 2020 was retrieved; the evidence is my price-ratio calculation and Freefincal's annual figure.
- No article was found on gold ETF premiums in 2025-2026; the Yahoo cross-section suggests gold stayed tight in October 2025.

---

## 6. Dividend treatment: does Yahoo adjusted close equal total return?

### Takeaway
The equity, gold, silver, gilt and international ETFs recommended here have paid no dividends in Yahoo's records and their adjusted close equals their close, which is consistent with growth-style funds that reinvest index dividends in NAV. Price return is therefore the investor's total return for those tickers. LIQUIDBEES is the exception: its price is pinned near Rs 1,000 and the return arrives as dividends.

### Cited Findings
- **No dividend events and adjusted close identical to close across full history** for NIFTYBEES, JUNIORBEES, GOLDBEES, SILVERBEES, MON100, MAFANG, MASPTOP50, HNGSNGBEES, LTGILTBEES, GILT5YBEES, MOM100, MIDCAPIETF and the Bharat Bond ETFs. — [Yahoo NIFTYBEES.NS](https://query1.finance.yahoo.com/v8/finance/chart/NIFTYBEES.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits); [Yahoo JUNIORBEES.NS](https://query1.finance.yahoo.com/v8/finance/chart/JUNIORBEES.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits); [Yahoo LTGILTBEES.NS](https://query1.finance.yahoo.com/v8/finance/chart/LTGILTBEES.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits)
- **LIQUIDBEES.NS:** 153 dividend events on Yahoo (for example 3.54 on 30 Apr 2025, 3.59 on 30 May 2025, 3.08 on 30 Sep 2025); last close Rs 999.99; adjusted close differs from close by up to 41% over the history. LIQUIDCASE (Zerodha) has no dividends and a rising price (Rs 116.85). — [Yahoo LIQUIDBEES.NS](https://query1.finance.yahoo.com/v8/finance/chart/LIQUIDBEES.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits); [Yahoo LIQUIDCASE.NS](https://query1.finance.yahoo.com/v8/finance/chart/LIQUIDCASE.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits)
- **Isolated dividends elsewhere:** Kotak's NIFTY1 shows 1.10 (7 May 2013) and 0.95 (24 Nov 2014); ICICI's NIFTYIETF shows one 2.20 dividend dated April 2016. — [Yahoo NIFTY1.NS](https://query1.finance.yahoo.com/v8/finance/chart/NIFTY1.NS?period1=0&period2=1900000000&interval=1d&events=div%2Csplits); [Yahoo NIFTYIETF.NS](https://query1.finance.yahoo.com/v8/finance/chart/NIFTYIETF.NS?range=max&interval=1d&events=div%2Csplits)
- Groww lists the benchmarks as total-return indices: "Nifty 50 TRI" (NIFTYBEES, SBINIFTY50, NIFTYIETF), "Nifty Next 50 TRI" (JUNIORBEES), "Nifty Midcap 150 TRI" (MID150BEES), "NASDAQ-100 TRI" (MON100), "NYSE FANG+ TRI" (MAFANG), "Hang Seng TRI" (HNGSNGBEES). — [Groww NIFTYBEES](https://groww.in/etfs/reliance-etf-nifty-bees); [Groww MON100](https://groww.in/etfs/motilal-oswal-mutual-fundmotilal-oswal-most-shares-nasdaq-etf)
- SBI's gold ETF is named "SBI Gold Exchange Traded Scheme - Growth Option" on Groww. — [Groww GOLDBEES peer table](https://groww.in/etfs/reliance-etf-gold-bees)
- Yahoo's `^NSEI` is the price index, not the total-return index (from the earlier note, section 4). — [yfinance download reference](https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html)

### Inferences
- For the recommended tickers Yahoo's `Close` and `Adj Close` are interchangeable, and both already include reinvested dividends because the fund keeps them in NAV. Compare the strategy with Nifty TRI, not `^NSEI`, or NIFTYBEES will look about a dividend yield per year better than "the index".
- The earlier note's concern that NIFTYBEES "paid dividends in earlier years" is not visible in Yahoo's data from 2009 onward: no dividend events are recorded. Yahoo's event data is demonstrably incomplete (it missed the 2019 split), so this is absence of evidence only.
- If LIQUIDBEES is the cash leg, use adjusted close for returns and expect periodic small dividend credits rather than price gains. LIQUIDCASE accrues in price and is simpler for a bot. Detail belongs to the liquid-ETF researcher.
- The premium problem dominates everything in this section for international ETFs: price return and NAV return differ by tens of points.

### Gaps
- No scheme information document was read to confirm that each ETF is growth-only with no IDCW option. The conclusion rests on Yahoo's missing dividend events and Groww's benchmark and plan labels.
- Tax treatment by class (equity vs non-equity for gold, silver, international and gilt ETFs after the 2023-2024 changes) was not researched and matters for a monthly-turnover strategy.
