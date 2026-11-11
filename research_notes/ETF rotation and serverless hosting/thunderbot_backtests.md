# Thunderbot's own backtests of ETF rotation, 2010-2026 (run 11 November 2026)

These are first-hand results from this repository's backtester (`worker/thunderbot/daily.py`), not
published research. They are backtests: they show what each rule did on past prices, not what it will do.

## Method

- **Prices:** Yahoo Finance chart endpoint, adjusted daily closes, to 11 Nov 2026. NIFTYBEES, JUNIORBEES
  and GOLDBEES start 2 Jan 2009; MOM100 (Nifty Midcap 100 ETF) 31 Jan 2011; MON100 (Nasdaq 100 ETF)
  29 Mar 2011; `^NSEI` 17 Sep 2007. Known bad ticks are repaired (`clean_series`): the two days after the
  19 Dec 2019 unit splits (NIFTYBEES, BANKBEES 1:10, GOLDBEES 1:100) appear at one-tenth or one-hundredth
  of the right price and are dropped; MON100 has the same fault on 17-18 Jun 2021; NIFTYBEES has a bad
  tick on 6 Oct 2010. MID150BEES and NIFTYIETF return only 15 rows on Yahoo, so they cannot be tested.
- **Execution:** the rule decides on day t's close and fills at day t+1's close (no look-ahead). Sensitivity
  to filling the same day or two days later is shown below.
- **Costs:** Groww delivery schedule per order: brokerage min(Rs 20, 0.1%), NSE 0.00307%, SEBI 0.0001%,
  stamp duty 0.015% on buys, GST 18%, DP Rs 23.60 per sell, STT 0.001% on equity-ETF sells and nil on gold
  and liquid ETFs, plus 0.05% slippage per side (0.01% for the liquid ETF).
- **Tax (FY 2026-27 rules applied to the whole history):** equity ETFs 20% up to 12 months and 12.5% above
  Rs 1.25 lakh a year after; gold ETFs at a 30% slab rate up to 12 months and 12.5% after with no exemption;
  the liquid ETF always at the 30% slab rate; 4% cess; first-in-first-out lots; short-term losses set off
  against any gain, long-term losses against long-term gains, unused losses carried forward. Tax is paid
  on the first session of each financial year. "exit" is the CAGR if everything were also sold and taxed
  on the last day.
- **Liquid ETF:** a synthetic growth-type liquid ETF priced from the Nifty 1D Rate return of each calendar
  year (table in `liquid_etfs_and_cash_returns.md`) less 0.30% a year in costs.
- **Capital:** Rs 5 lakh unless stated. **Benchmark:** NIFTYBEES bought on day one and held (pre-tax, and
  "exit" after 12.5% LTCG on the final gain).
- **Rules tested:**
  - *Nifty trend*: NIFTYBEES while the Nifty is more than 1% above its 200-day average at month-end, out when
    more than 1% below; out means idle cash (0%) or the liquid ETF.
  - *static*: fixed weights, rebalanced each March. No timing.
  - *trend [..]* (Faber-style): equal share per ETF, each held only while above its own 200-day average at
    month-end, otherwise that share sits in the liquid ETF. Trades only when holdings change or a weight
    drifts more than 10 points.
  - *rank topN [..]* (dual momentum): rank by the average of 3-, 6- and 12-month returns, hold the top N in
    equal parts if they beat the liquid ETF's return over the same periods, otherwise the liquid ETF.
  - N = NIFTYBEES, NN = JUNIORBEES (Next 50), Mid = MOM100, G = GOLDBEES, Nasdaq = MON100.
- Columns: `cagr` % a year after costs and tax; `exit` as above; `mdd` worst peak-to-trough fall %; `vol`
  annualised volatility; `sh` Sharpe (no risk-free deduction); `uw` longest time below a previous high in
  days; `trd` trades; `cost` and `tax` in rupees; `inv` % of days holding anything other than the liquid ETF.

## 1. All variants, 3 Jan 2011 to 11 Nov 2026

```
== 2011-01-03 to 2026-11-11, Rs 5 lakh, after costs and tax (slab 30%), trade next close
Nifty trend, idle cash 0%                    cagr   5.86 exit   5.86 mdd  -27.34 vol  11.5 sh 0.57 uw  1278d trd   36 cost     9984 tax     62915 inv  76.8%
BENCH NIFTYBEES buy&hold (pre-tax)           cagr  10.12 exit   9.43 mdd  -36.34 vol  15.1 sh 0.73 uw  1019d
Nifty trend, idle cash 0%, PRE-TAX           cagr   6.25 exit   6.25 mdd  -27.34 vol  11.5 sh 0.60 uw  1278d trd   32 cost     9977 tax         0 inv  76.8%
Nifty trend + liquid ETF                     cagr   7.07 exit   7.07 mdd  -22.07 vol  11.5 sh 0.67 uw  1227d trd   71 cost    15544 tax    100939 inv  76.8%
Nifty trend + liquid ETF, PRE-TAX            cagr   7.66 exit   7.66 mdd  -22.07 vol  11.5 sh 0.72 uw  1227d trd   61 cost    15599 tax         0 inv  76.8%
Nifty trend + liquid, slab 20%               cagr   7.12 exit   7.12 mdd  -22.07 vol  11.5 sh 0.67 uw  1227d trd   70 cost    15560 tax     94940 inv  76.8%
-- static mixes (annual rebalance)
static N50                                   cagr  10.16 exit   9.47 mdd  -36.34 vol  15.1 sh 0.73 uw   864d trd    2 cost      373 tax         0 inv 100.0%
static N50/NN50                              cagr  11.44 exit  10.77 mdd  -34.94 vol  15.4 sh 0.80 uw   775d trd   30 cost     1585 tax         0 inv 100.0%
static N50/NN50/Gold                         cagr  12.48 exit  11.92 mdd  -23.16 vol  11.6 sh 1.10 uw   504d trd   69 cost     3982 tax     64479 inv 100.0%
static N50/NN50/Mid/Gold                     cagr  12.64 exit  12.04 mdd  -25.60 vol  12.2 sh 1.06 uw   706d trd   95 cost     4660 tax     54256 inv 100.0%
static 3 equity (N,NN,Mid)                   cagr  11.67 exit  10.98 mdd  -38.05 vol  15.4 sh 0.81 uw  1192d trd   53 cost     2531 tax         0 inv 100.0%
static Gold                                  cagr  11.63 exit  10.83 mdd  -27.40 vol  15.8 sh 0.80 uw  2425d trd    2 cost      373 tax         0 inv 100.0%
static NN50                                  cagr  12.51 exit  11.73 mdd  -38.68 vol  17.6 sh 0.78 uw  1060d trd    2 cost      373 tax         0 inv 100.0%
static Mid100                                cagr  12.66 exit  11.87 mdd  -48.42 vol  20.5 sh 0.70 uw  1204d trd    2 cost      373 tax         0 inv  99.5%
static 75 equity/25 gold                     cagr  12.32 exit  11.74 mdd  -25.32 vol  12.2 sh 1.04 uw   442d trd   65 cost     3648 tax     54378 inv 100.0%
static N50/Gold/Liquid thirds                cagr   9.98 exit   9.34 mdd  -14.37 vol   7.6 sh 1.33 uw   445d trd   86 cost     3642 tax     47879 inv 100.0%
static Nasdaq                                cagr  23.69 exit  22.65 mdd  -36.55 vol  23.1 sh 1.06 uw   561d trd    2 cost      373 tax         0 inv  98.5%
-- rotation, rank mode (3/6/12m blend, absolute filter vs liquid)
rank top1 [N,NN,G]                           cagr  11.95 exit  11.95 mdd  -37.65 vol  17.6 sh 0.75 uw   990d trd  105 cost    62937 tax    410465 inv  95.6%
rank top2 [N,NN,G]                           cagr   8.86 exit   8.86 mdd  -20.81 vol  12.1 sh 0.78 uw   910d trd  222 cost    47449 tax    168856 inv  95.6%
rank top3 [N,NN,G]                           cagr   8.37 exit   8.36 mdd  -14.29 vol   8.9 sh 0.97 uw   814d trd  219 cost    30353 tax    134539 inv  95.6%
rank top1 [N,NN,Mid,G]                       cagr  14.44 exit  14.44 mdd  -32.12 vol  18.6 sh 0.84 uw   911d trd  109 cost    66642 tax    665413 inv  95.6%
rank top2 [N,NN,Mid,G]                       cagr   9.41 exit   9.41 mdd  -32.17 vol  13.7 sh 0.74 uw  1077d trd  264 cost    67292 tax    231599 inv  95.6%
rank top3 [N,NN,Mid,G]                       cagr   8.45 exit   8.45 mdd  -25.19 vol  11.5 sh 0.78 uw  1077d trd  312 cost    47512 tax    134401 inv  95.6%
rank top1 [N,NN,Mid (no gold)]               cagr   3.72 exit   3.72 mdd  -50.41 vol  15.6 sh 0.32 uw  1352d trd  135 cost    51322 tax    119740 inv  73.4%
rank top2 [N,NN,Mid (no gold)]               cagr   5.87 exit   5.87 mdd  -38.03 vol  13.0 sh 0.52 uw  1231d trd  212 cost    44898 tax    113153 inv  73.4%
rank top3 [N,NN,Mid (no gold)]               cagr   6.81 exit   6.81 mdd  -27.65 vol  11.0 sh 0.67 uw  1114d trd  220 cost    32250 tax     92119 inv  73.4%
rank top1 [N,NN (no gold)]                   cagr   4.64 exit   4.64 mdd  -30.94 vol  13.6 sh 0.41 uw  1099d trd  119 cost    45541 tax    112418 inv  72.9%
rank top2 [N,NN (no gold)]                   cagr   6.61 exit   6.61 mdd  -20.29 vol  10.8 sh 0.66 uw  1043d trd  147 cost    27760 tax     86807 inv  72.9%
rank top1 [N,G]                              cagr  11.01 exit  11.01 mdd  -28.65 vol  15.7 sh 0.76 uw  1281d trd   85 cost    51457 tax    268226 inv  90.9%
rank top2 [N,G]                              cagr   8.89 exit   8.85 mdd  -15.81 vol   8.9 sh 1.02 uw   669d trd  146 cost    26270 tax    158725 inv  90.9%
rank top1 [N,NN,Mid,G,Nasdaq]                cagr  13.96 exit  13.96 mdd  -30.97 vol  21.3 sh 0.74 uw   845d trd  104 cost    99705 tax   1118735 inv  98.8%
rank top2 [N,NN,Mid,G,Nasdaq]                cagr  12.09 exit  12.09 mdd  -28.86 vol  15.3 sh 0.84 uw   815d trd  260 cost    66318 tax    488792 inv  98.8%
rank top3 [N,NN,Mid,G,Nasdaq]                cagr  10.28 exit  10.28 mdd  -27.45 vol  12.5 sh 0.87 uw  1011d trd  429 cost    69474 tax    271933 inv  98.8%
-- rotation, trend mode (each above own 200d avg)
trend [N,NN,G]                               cagr   8.82 exit   8.82 mdd  -15.47 vol   9.2 sh 0.99 uw   749d trd  268 cost    32338 tax    159470 inv  98.7%
trend [N,NN,Mid,G]                           cagr   9.02 exit   9.01 mdd  -16.37 vol   9.6 sh 0.97 uw  1035d trd  363 cost    36181 tax    158288 inv  99.3%
trend [N,NN,Mid (no gold)]                   cagr   7.98 exit   7.98 mdd  -26.45 vol  11.5 sh 0.75 uw  1183d trd  213 cost    30707 tax    128517 inv  82.7%
trend [N,G]                                  cagr   8.63 exit   8.61 mdd  -16.74 vol   9.2 sh 0.97 uw   587d trd  171 cost    26677 tax    175168 inv  94.5%
trend [N,NN,Mid,G,Nasdaq]                    cagr  10.78 exit  10.77 mdd  -16.36 vol   9.4 sh 1.16 uw   751d trd  481 cost    41895 tax    249645 inv  99.8%
```

Note on the first block: strategies begin with a decision on the first day, so "static N50" differs from
the benchmark only by the benchmark's same-day fill. An earlier run that began at the end of January 2011
(after a 10% fall that month) gave every rule about 0.8 points a year more; start-date luck is that large.

## 2. Sub-periods, parameter sensitivity, fill delay, capital, pre-tax

```
== 2010-03-01 to 2026-11-11
Nifty trend, idle cash                       cagr   6.64 exit   6.64 mdd  -30.53 vol  13.1 sh 0.57 uw  1393d trd   37 cost    11655 tax     91227 inv  78.0%
  NIFTYBEES buy&hold (pre-tax | after exit tax) cagr  10.97 exit  10.26 mdd  -36.34 vol  16.2 sh 0.74
Nifty trend + liquid                         cagr   7.76 exit   7.76 mdd  -25.89 vol  13.1 sh 0.65 uw  1304d trd   74 cost    18111 tax    138722 inv  78.0%
static N50/NN50/Gold                         cagr  12.97 exit  12.43 mdd  -23.16 vol  11.6 sh 1.13 uw   504d trd   84 cost     4770 tax     85189 inv 100.0%
static N50/NN50                              cagr  11.96 exit  11.30 mdd  -34.94 vol  15.6 sh 0.82 uw  1234d trd   36 cost     1848 tax       992 inv 100.0%
static Gold                                  cagr  12.23 exit  11.45 mdd  -27.40 vol  15.6 sh 0.84 uw  2425d trd    2 cost      373 tax         0 inv 100.0%
rank top1 [N,NN,G]                           cagr  12.02 exit  12.02 mdd  -37.64 vol  17.7 sh 0.75 uw   990d trd  111 cost    71147 tax    470892 inv  95.8%
rank top2 [N,NN,G]                           cagr   8.60 exit   8.59 mdd  -20.84 vol  12.5 sh 0.74 uw   910d trd  239 cost    50889 tax    180210 inv  95.8%
trend [N,NN,G]                               cagr   9.30 exit   9.29 mdd  -15.46 vol   9.5 sh 1.01 uw   749d trd  276 cost    36321 tax    206763 inv  98.8%
trend [N,NN] no gold                         cagr   8.28 exit   8.28 mdd  -25.85 vol  11.9 sh 0.75 uw  1280d trd  145 cost    32062 tax    165372 inv  81.4%
rank top2 [N,NN] no gold                     cagr   7.06 exit   7.06 mdd  -20.44 vol  11.4 sh 0.67 uw  1286d trd  151 cost    30971 tax    128156 inv  74.3%
== 2011-01-03 to 2026-11-11
Nifty trend, idle cash                       cagr   5.86 exit   5.86 mdd  -27.34 vol  11.5 sh 0.57 uw  1278d trd   36 cost     9984 tax     62915 inv  76.8%
  NIFTYBEES buy&hold (pre-tax | after exit tax) cagr  10.12 exit   9.43 mdd  -36.34 vol  15.1 sh 0.73
Nifty trend + liquid                         cagr   7.07 exit   7.07 mdd  -22.07 vol  11.5 sh 0.67 uw  1227d trd   71 cost    15544 tax    100939 inv  76.8%
static N50/NN50/Gold                         cagr  12.48 exit  11.92 mdd  -23.16 vol  11.6 sh 1.10 uw   504d trd   69 cost     3982 tax     64479 inv 100.0%
static N50/NN50                              cagr  11.44 exit  10.77 mdd  -34.94 vol  15.4 sh 0.80 uw   775d trd   30 cost     1585 tax         0 inv 100.0%
static Gold                                  cagr  11.63 exit  10.83 mdd  -27.40 vol  15.8 sh 0.80 uw  2425d trd    2 cost      373 tax         0 inv 100.0%
rank top1 [N,NN,G]                           cagr  11.95 exit  11.95 mdd  -37.65 vol  17.6 sh 0.75 uw   990d trd  105 cost    62937 tax    410465 inv  95.6%
rank top2 [N,NN,G]                           cagr   8.86 exit   8.86 mdd  -20.81 vol  12.1 sh 0.78 uw   910d trd  222 cost    47449 tax    168856 inv  95.6%
trend [N,NN,G]                               cagr   8.82 exit   8.82 mdd  -15.47 vol   9.2 sh 0.99 uw   749d trd  268 cost    32338 tax    159470 inv  98.7%
trend [N,NN] no gold                         cagr   7.83 exit   7.83 mdd  -18.90 vol  11.3 sh 0.74 uw   825d trd  142 cost    28466 tax    121980 inv  80.4%
rank top2 [N,NN] no gold                     cagr   6.61 exit   6.61 mdd  -20.29 vol  10.8 sh 0.66 uw  1043d trd  147 cost    27760 tax     86807 inv  72.9%
== 2010-03-01 to 2018-12-31
Nifty trend, idle cash                       cagr   5.17 exit   5.17 mdd  -30.53 vol  14.4 sh 0.43 uw  1393d trd   22 cost     5078 tax     15262 inv  76.6%
  NIFTYBEES buy&hold (pre-tax | after exit tax) cagr   9.65 exit   8.91 mdd  -27.27 vol  16.9 sh 0.65
Nifty trend + liquid                         cagr   6.58 exit   6.58 mdd  -25.89 vol  14.4 sh 0.53 uw  1304d trd   42 cost     7551 tax     32861 inv  76.6%
static N50/NN50/Gold                         cagr   9.74 exit   9.14 mdd  -14.31 vol  10.9 sh 0.93 uw   504d trd   45 cost     1986 tax      4345 inv 100.0%
static N50/NN50                              cagr  10.78 exit  10.00 mdd  -32.85 vol  15.6 sh 0.76 uw  1234d trd   18 cost      932 tax         5 inv 100.0%
static Gold                                  cagr   6.09 exit   5.44 mdd  -27.40 vol  13.7 sh 0.51 uw  2225d trd    2 cost      373 tax         0 inv 100.0%
rank top1 [N,NN,G]                           cagr   8.18 exit   8.18 mdd  -32.33 vol  16.4 sh 0.57 uw   667d trd   60 cost    25280 tax    121372 inv  92.4%
rank top2 [N,NN,G]                           cagr   6.37 exit   6.37 mdd  -18.60 vol  12.2 sh 0.58 uw   637d trd  128 cost    20897 tax     29253 inv  92.4%
trend [N,NN,G]                               cagr   7.01 exit   7.01 mdd  -12.76 vol   9.1 sh 0.81 uw   483d trd  141 cost    14238 tax     41176 inv  98.0%
trend [N,NN] no gold                         cagr   7.91 exit   7.91 mdd  -25.85 vol  12.6 sh 0.69 uw  1280d trd   78 cost    12152 tax     43622 inv  80.2%
rank top2 [N,NN] no gold                     cagr   6.68 exit   6.68 mdd  -17.78 vol  11.9 sh 0.62 uw  1286d trd   85 cost    13048 tax     42308 inv  70.9%
== 2019-01-01 to 2026-11-11
Nifty trend, idle cash                       cagr   7.54 exit   7.54 mdd  -17.87 vol  11.4 sh 0.71 uw   775d trd   16 cost     4440 tax     27792 inv  76.6%
  NIFTYBEES buy&hold (pre-tax | after exit tax) cagr  12.57 exit  11.60 mdd  -36.34 vol  15.5 sh 0.86
Nifty trend + liquid                         cagr   8.52 exit   8.52 mdd  -16.86 vol  11.4 sh 0.79 uw   775d trd   35 cost     6690 tax     36453 inv  76.6%
static N50/NN50/Gold                         cagr  16.85 exit  15.88 mdd  -23.16 vol  12.4 sh 1.34 uw   286d trd   42 cost     2216 tax     28855 inv  99.9%
static N50/NN50                              cagr  13.41 exit  12.45 mdd  -34.95 vol  15.7 sh 0.90 uw   775d trd   22 cost     1017 tax       146 inv  99.9%
static Gold                                  cagr  19.47 exit  17.92 mdd  -24.44 vol  17.6 sh 1.12 uw   908d trd    2 cost      373 tax         0 inv  99.9%
rank top1 [N,NN,G]                           cagr  16.33 exit  16.33 mdd  -37.70 vol  19.0 sh 0.91 uw   990d trd   48 cost    23273 tax    173501 inv  99.6%
rank top2 [N,NN,G]                           cagr  11.25 exit  11.25 mdd  -20.69 vol  12.8 sh 0.92 uw   851d trd  110 cost    18910 tax     76955 inv  99.6%
trend [N,NN,G]                               cagr  12.17 exit  12.15 mdd  -15.48 vol   9.8 sh 1.24 uw   746d trd  130 cost    14104 tax     77025 inv  99.6%
trend [N,NN] no gold                         cagr   9.01 exit   9.01 mdd  -17.49 vol  11.1 sh 0.85 uw   784d trd   68 cost    11669 tax     47194 inv  82.8%
rank top2 [N,NN] no gold                     cagr   7.73 exit   7.73 mdd  -19.84 vol  10.8 sh 0.76 uw   808d trd   67 cost    11325 tax     33878 inv  78.0%
== 2011-01-03 to 2015-12-31
Nifty trend, idle cash                       cagr   0.33 exit   0.33 mdd  -27.34 vol  12.2 sh 0.09 uw  1278d trd   16 cost     3087 tax         0 inv  68.2%
  NIFTYBEES buy&hold (pre-tax | after exit tax) cagr   5.26 exit   5.17 mdd  -25.38 vol  16.2 sh 0.41
Nifty trend + liquid                         cagr   2.61 exit   2.61 mdd  -22.07 vol  12.2 sh 0.28 uw  1227d trd   29 cost     4434 tax         0 inv  68.2%
static N50/NN50/Gold                         cagr   6.86 exit   6.62 mdd  -11.52 vol  11.6 sh 0.65 uw   415d trd   21 cost     1099 tax      1535 inv  99.9%
static N50/NN50                              cagr   7.78 exit   7.39 mdd  -28.26 vol  16.0 sh 0.56 uw   730d trd    8 cost      574 tax         0 inv  99.9%
static Gold                                  cagr   2.73 exit   2.39 mdd  -27.40 vol  15.4 sh 0.26 uw  1129d trd    2 cost      373 tax         0 inv  99.9%
rank top1 [N,NN,G]                           cagr  11.92 exit  11.91 mdd  -32.12 vol  17.1 sh 0.77 uw   667d trd   31 cost    10456 tax     38606 inv  91.6%
rank top2 [N,NN,G]                           cagr   8.80 exit   8.76 mdd  -18.55 vol  12.0 sh 0.79 uw   492d trd   58 cost     8874 tax     18768 inv  91.6%
trend [N,NN,G]                               cagr   5.71 exit   5.71 mdd   -9.27 vol   9.2 sh 0.68 uw   482d trd   91 cost     8200 tax      6988 inv  96.5%
trend [N,NN] no gold                         cagr   6.42 exit   6.38 mdd  -18.90 vol  12.0 sh 0.60 uw   731d trd   44 cost     6172 tax      7041 inv  73.0%
rank top2 [N,NN] no gold                     cagr   5.64 exit   5.60 mdd  -14.25 vol  11.0 sh 0.57 uw   696d trd   51 cost     7095 tax      3448 inv  59.9%
== 2016-01-01 to 2020-12-31
Nifty trend, idle cash                       cagr  10.56 exit   9.57 mdd  -14.25 vol  10.7 sh 1.02 uw   805d trd   12 cost     3042 tax      3825 inv  80.3%
  NIFTYBEES buy&hold (pre-tax | after exit tax) cagr  13.56 exit  12.54 mdd  -36.34 vol  16.4 sh 0.88
Nifty trend + liquid                         cagr  11.35 exit  10.29 mdd  -14.05 vol  10.7 sh 1.08 uw   804d trd   25 cost     4552 tax      9389 inv  80.3%
static N50/NN50/Gold                         cagr  14.20 exit  13.17 mdd  -23.16 vol  11.1 sh 1.28 uw   298d trd   24 cost     1222 tax      5402 inv  99.9%
static N50/NN50                              cagr  12.53 exit  11.67 mdd  -34.95 vol  16.3 sh 0.83 uw   500d trd   12 cost      719 tax         0 inv  99.9%
static Gold                                  cagr  13.56 exit  12.14 mdd  -14.56 vol  13.5 sh 1.03 uw   907d trd    2 cost      373 tax         0 inv  99.9%
rank top1 [N,NN,G]                           cagr  11.04 exit  10.47 mdd  -25.57 vol  15.3 sh 0.78 uw   826d trd   31 cost     9388 tax     41144 inv  94.9%
rank top2 [N,NN,G]                           cagr   7.98 exit   7.42 mdd  -17.05 vol  10.0 sh 0.84 uw   910d trd   76 cost    10251 tax     14699 inv  94.9%
trend [N,NN,G]                               cagr   9.90 exit   8.94 mdd  -10.33 vol   7.8 sh 1.27 uw   710d trd   79 cost     7058 tax      7154 inv  99.9%
trend [N,NN] no gold                         cagr   8.84 exit   8.05 mdd  -16.53 vol  10.4 sh 0.89 uw   823d trd   49 cost     7138 tax      1142 inv  81.8%
rank top2 [N,NN] no gold                     cagr   7.73 exit   6.87 mdd  -17.34 vol   9.7 sh 0.83 uw  1043d trd   43 cost     6118 tax      4300 inv  72.3%
== 2021-01-01 to 2026-11-11
Nifty trend, idle cash                       cagr   7.33 exit   7.33 mdd  -17.63 vol  11.5 sh 0.68 uw   775d trd    9 cost     2717 tax     11973 inv  81.1%
  NIFTYBEES buy&hold (pre-tax | after exit tax) cagr  11.74 exit  10.86 mdd  -16.11 vol  12.9 sh 0.94
Nifty trend + liquid                         cagr   8.15 exit   8.15 mdd  -16.58 vol  11.5 sh 0.75 uw   775d trd   20 cost     3848 tax     17354 inv  81.1%
static N50/NN50/Gold                         cagr  15.61 exit  14.63 mdd  -16.97 vol  11.9 sh 1.30 uw   286d trd   33 cost     1616 tax     13685 inv  99.9%
static N50/NN50                              cagr  13.49 exit  12.52 mdd  -20.58 vol  13.9 sh 1.00 uw   775d trd   10 cost      681 tax         0 inv  99.9%
static Gold                                  cagr  17.63 exit  15.97 mdd  -24.44 vol  17.7 sh 1.03 uw   425d trd    2 cost      373 tax         0 inv  99.9%
rank top1 [N,NN,G]                           cagr  13.56 exit  13.56 mdd  -35.53 vol  19.5 sh 0.77 uw   959d trd   41 cost    13957 tax     74416 inv  99.4%
rank top2 [N,NN,G]                           cagr   9.85 exit   9.85 mdd  -20.69 vol  13.6 sh 0.77 uw   851d trd   85 cost    12638 tax     40519 inv  99.4%
trend [N,NN,G]                               cagr  11.21 exit  11.19 mdd  -15.48 vol  10.2 sh 1.11 uw   744d trd   97 cost     9351 tax     39233 inv  99.4%
trend [N,NN] no gold                         cagr   8.88 exit   8.88 mdd  -15.87 vol  11.3 sh 0.83 uw   778d trd   45 cost     7563 tax     24640 inv  85.4%
rank top2 [N,NN] no gold                     cagr   6.88 exit   6.88 mdd  -19.87 vol  11.4 sh 0.65 uw   802d trd   51 cost     8020 tax     21432 inv  84.1%
== sensitivity 2011-2026: trend mode [N,NN,G] by average length
trend sma 100                                cagr   7.96 exit   7.95 mdd  -17.46 vol   8.7 sh 0.94 uw   710d trd  372 cost    46990 tax    228019 inv  93.0%
trend sma 150                                cagr   8.49 exit   8.48 mdd  -18.20 vol   9.0 sh 0.98 uw   912d trd  311 cost    38680 tax    163310 inv  96.0%
trend sma 200                                cagr   8.82 exit   8.82 mdd  -15.47 vol   9.2 sh 0.99 uw   749d trd  268 cost    32338 tax    159470 inv  98.7%
trend sma 250                                cagr   9.30 exit   9.29 mdd  -16.92 vol   9.5 sh 1.01 uw   580d trd  210 cost    25795 tax    167688 inv  99.8%
== sensitivity: rank top2 [N,NN,G] by lookback
rank top2 lb (21,)                           cagr   9.11 exit   9.11 mdd  -22.02 vol  11.4 sh 0.84 uw   741d trd  458 cost   102419 tax    545628 inv  82.6%
rank top2 lb (63,)                           cagr   9.33 exit   9.33 mdd  -19.08 vol  11.4 sh 0.86 uw   930d trd  274 cost    60504 tax    315378 inv  89.2%
rank top2 lb (126,)                          cagr   9.70 exit   9.70 mdd  -24.19 vol  11.9 sh 0.86 uw  1035d trd  215 cost    51857 tax    216292 inv  93.0%
rank top2 lb (252,)                          cagr   8.43 exit   8.30 mdd  -21.86 vol  12.3 sh 0.74 uw   842d trd  171 cost    36582 tax    139292 inv  94.2%
rank top2 lb (126, 252)                      cagr   8.94 exit   8.94 mdd  -21.61 vol  12.2 sh 0.78 uw  1049d trd  194 cost    44685 tax    174652 inv  94.1%
rank top2 lb (63, 126, 252)                  cagr   8.86 exit   8.86 mdd  -20.81 vol  12.1 sh 0.78 uw   910d trd  222 cost    47449 tax    168856 inv  95.6%
rank top2 lb (21, 63, 126, 252)              cagr   9.98 exit   9.97 mdd  -20.62 vol  12.0 sh 0.88 uw   911d trd  238 cost    55391 tax    215351 inv  94.0%
== sensitivity: IndexTrend+liquid by sma / buffer
index trend sma 100 buf 0                    cagr   6.87 exit   6.87 mdd  -26.72 vol  10.5 sh 0.70 uw  1253d trd  136 cost    33935 tax    185319 inv  65.7%
index trend sma 100 buf 1                    cagr   6.43 exit   6.43 mdd  -26.72 vol  10.5 sh 0.66 uw  1276d trd  126 cost    29974 tax    167994 inv  66.3%
index trend sma 100 buf 2                    cagr   7.25 exit   7.25 mdd  -18.00 vol  10.1 sh 0.76 uw   805d trd   86 cost    22906 tax    133673 inv  63.2%
index trend sma 150 buf 0                    cagr   7.14 exit   7.07 mdd  -19.49 vol  10.7 sh 0.71 uw  1225d trd  111 cost    25222 tax    102667 inv  68.2%
index trend sma 150 buf 1                    cagr   7.63 exit   7.56 mdd  -17.99 vol  10.4 sh 0.78 uw   828d trd   86 cost    20720 tax    117802 inv  66.4%
index trend sma 150 buf 2                    cagr   6.92 exit   6.92 mdd  -19.62 vol  10.7 sh 0.70 uw   833d trd   77 cost    18255 tax     98081 inv  67.4%
index trend sma 200 buf 0                    cagr   6.61 exit   6.54 mdd  -22.07 vol  10.9 sh 0.66 uw  1227d trd  100 cost    22520 tax     81702 inv  71.2%
index trend sma 200 buf 1                    cagr   7.07 exit   7.07 mdd  -22.07 vol  11.5 sh 0.67 uw  1227d trd   71 cost    15544 tax    100939 inv  76.8%
index trend sma 200 buf 2                    cagr   6.49 exit   6.49 mdd  -20.82 vol  11.7 sh 0.61 uw  1232d trd   67 cost    13694 tax     89126 inv  75.2%
index trend sma 250 buf 0                    cagr   6.83 exit   6.83 mdd  -22.07 vol  11.4 sh 0.65 uw  1227d trd   76 cost    17541 tax     93359 inv  76.3%
index trend sma 250 buf 1                    cagr   6.56 exit   6.56 mdd  -21.64 vol  11.8 sh 0.61 uw  1232d trd   70 cost    15126 tax     84724 inv  78.4%
index trend sma 250 buf 2                    cagr   6.26 exit   6.26 mdd  -21.60 vol  11.8 sh 0.59 uw  1232d trd   66 cost    13510 tax     74878 inv  76.3%
== trade lag 0 vs 1 vs 2 (2011-2026)
trend [N,NN,G] lag 0                         cagr   9.14 exit   9.14 mdd  -15.59 vol   9.2 sh 1.02 uw   703d trd  268 cost    33031 tax    166585 inv  98.7%
index trend+liquid lag 0                     cagr   7.21 exit   7.21 mdd  -21.20 vol  11.5 sh 0.68 uw  1225d trd   72 cost    16037 tax    102229 inv  76.8%
trend [N,NN,G] lag 1                         cagr   8.82 exit   8.82 mdd  -15.47 vol   9.2 sh 0.99 uw   749d trd  268 cost    32338 tax    159470 inv  98.7%
index trend+liquid lag 1                     cagr   7.07 exit   7.07 mdd  -22.07 vol  11.5 sh 0.67 uw  1227d trd   71 cost    15544 tax    100939 inv  76.8%
trend [N,NN,G] lag 2                         cagr   8.59 exit   8.58 mdd  -15.46 vol   9.2 sh 0.96 uw   787d trd  261 cost    31679 tax    149158 inv  98.7%
index trend+liquid lag 2                     cagr   7.08 exit   7.08 mdd  -22.33 vol  11.5 sh 0.67 uw  1225d trd   71 cost    15650 tax    107079 inv  76.8%
== capital sensitivity (static & trend) 2011-2026
static N/NN/G cap 100000                     cagr  12.46 exit  12.05 mdd  -23.16 vol  11.6 sh 1.10 uw   504d trd   60 cost     1862 tax     12822 inv 100.0%
trend [N,NN,G] cap 100000                    cagr   8.84 exit   8.83 mdd  -15.54 vol   9.2 sh 0.99 uw   745d trd  235 cost    12211 tax     20578 inv  98.7%
index trend+liq cap 100000                   cagr   7.43 exit   7.43 mdd  -22.38 vol  11.4 sh 0.70 uw  1229d trd   51 cost     4401 tax      3871 inv  76.8%
static N/NN/G cap 500000                     cagr  12.48 exit  11.92 mdd  -23.16 vol  11.6 sh 1.10 uw   504d trd   69 cost     3982 tax     64479 inv 100.0%
trend [N,NN,G] cap 500000                    cagr   8.82 exit   8.82 mdd  -15.47 vol   9.2 sh 0.99 uw   749d trd  268 cost    32338 tax    159470 inv  98.7%
index trend+liq cap 500000                   cagr   7.07 exit   7.07 mdd  -22.07 vol  11.5 sh 0.67 uw  1227d trd   71 cost    15544 tax    100939 inv  76.8%
static N/NN/G cap 2000000                    cagr  12.42 exit  11.83 mdd  -23.16 vol  11.6 sh 1.10 uw   504d trd   78 cost    10346 tax    339859 inv 100.0%
trend [N,NN,G] cap 2000000                   cagr   8.57 exit   8.56 mdd  -15.45 vol   9.2 sh 0.96 uw   749d trd  272 cost   102114 tax    794674 inv  98.7%
index trend+liq cap 2000000                  cagr   6.81 exit   6.81 mdd  -22.00 vol  11.6 sh 0.64 uw  1226d trd   70 cost    55677 tax    552839 inv  76.8%
== pre-tax versions 2011-2026
Nifty trend, idle cash PRE-TAX               cagr   6.25 exit   6.25 mdd  -27.34 vol  11.5 sh 0.60 uw  1278d trd   32 cost     9977 tax         0 inv  76.8%
Nifty trend + liquid PRE-TAX                 cagr   7.66 exit   7.66 mdd  -22.07 vol  11.5 sh 0.72 uw  1227d trd   61 cost    15599 tax         0 inv  76.8%
static N50/NN50/Gold PRE-TAX                 cagr  12.68 exit  12.68 mdd  -23.16 vol  11.6 sh 1.12 uw   504d trd   51 cost     3407 tax         0 inv 100.0%
static N50/NN50 PRE-TAX                      cagr  11.44 exit  11.44 mdd  -34.94 vol  15.4 sh 0.80 uw   775d trd   30 cost     1585 tax         0 inv 100.0%
static Gold PRE-TAX                          cagr  11.63 exit  11.63 mdd  -27.40 vol  15.8 sh 0.80 uw  2425d trd    2 cost      373 tax         0 inv 100.0%
rank top1 [N,NN,G] PRE-TAX                   cagr  13.75 exit  13.75 mdd  -33.98 vol  17.4 sh 0.85 uw   948d trd   97 cost    70673 tax         0 inv  95.6%
rank top2 [N,NN,G] PRE-TAX                   cagr   9.71 exit   9.71 mdd  -20.50 vol  12.1 sh 0.85 uw   910d trd  206 cost    48976 tax         0 inv  95.6%
trend [N,NN,G] PRE-TAX                       cagr   9.62 exit   9.62 mdd  -13.97 vol   9.2 sh 1.07 uw   744d trd  256 cost    32977 tax         0 inv  98.7%
trend [N,NN] no gold PRE-TAX                 cagr   8.46 exit   8.46 mdd  -18.90 vol  11.3 sh 0.80 uw   823d trd  133 cost    29017 tax         0 inv  80.4%
rank top2 [N,NN] no gold PRE-TAX             cagr   7.13 exit   7.13 mdd  -19.81 vol  10.8 sh 0.71 uw  1043d trd  137 cost    28075 tax         0 inv  72.9%
```

## 3. Calendar years, drawdown episodes, rolling three-year returns

```
calendar-year % returns from Yahoo adjusted closes (ETF prices are after expenses; index is price-only)
year    Nifty50 idx      NIFTYBEES     JUNIORBEES       GOLDBEES         MOM100         MON100  Liquid(model)
2010           17.9           18.6           18.5           21.7              -              -            4.5
2011          -24.6          -24.0          -31.7           29.9              -              -            7.3
2012           27.7           27.4           49.0           11.3           40.2           17.3            8.0
2013            6.8            6.5            4.4           -6.4           -2.2           59.5            8.0
2014           31.4           31.6           43.7           -9.3           55.6           18.8            8.0
2015           -4.1           -4.3            7.9           -7.5            7.6           13.6            7.1
2016            3.0            4.0            7.5           12.5            7.2           17.6            6.2
2017           28.6           29.9           45.4            2.4           46.2           36.9            5.7
2018            3.2            4.8           -7.5            6.7          -15.0           -9.8            5.9
2019           12.0           13.6            1.0           22.9           -2.7           40.6            5.5
2020           14.9           15.4           15.8           27.0           21.7           50.4            3.1
2021           24.1           26.0           30.4           -5.2           45.5           30.1            3.0
2022            4.3            5.5            0.8           12.8            4.9          -26.2            4.5
2023           20.0           21.0           26.9           14.7           47.2           53.6            6.4
2024            8.8           10.4           28.1           19.4           24.5           56.8            6.5
2025           10.5           11.7            2.5           71.8            6.4            8.1            5.5
2026           -3.3           -3.0            6.4            4.7            1.5           31.0            4.2

after costs and tax, by calendar year, Rs 5 lakh from 2011-01-03
year      Nifty trend+liquid       Mix N/NN/G thirds   Trend rotation N/NN/G        Rank top2 N/NN/G    NIFTYBEES hold
2011                   -11.3                    -9.6                     3.0                    11.2             -24.4
2012                     2.8                    26.5                     9.3                    14.2              27.4
2013                    -1.7                     1.2                    -1.9                   -11.5               6.5
2014                    31.6                    21.7                    19.9                    34.9              31.6
2015                    -3.7                    -0.9                    -0.4                     1.3              -4.3
2016                     3.2                     8.2                     5.0                    -1.8               4.0
2017                    28.2                    25.6                    20.6                    26.9              29.9
2018                     0.3                     0.9                    -5.8                   -12.6               4.8
2019                     7.1                    12.7                     8.8                     8.3              13.6
2020                    18.9                    25.7                    22.6                    25.1              15.4
2021                    25.9                    17.2                    17.2                    25.8              26.0
2022                    -0.3                     6.1                    -5.0                   -14.2               5.5
2023                    16.8                    22.1                    15.6                    17.0              21.0
2024                    10.4                    19.3                    19.5                    13.7              10.4
2025                     6.3                    26.9                    25.1                    28.5              11.7
2026                   -10.7                     3.6                    -5.3                    -8.0              -3.0
Nifty trend+liquid drawdowns >8%: [('2011-01-03', '2012-07-26', '2014-05-14', -22.1), ('2015-01-29', '2015-09-01', '2016-09-06', -12.4), ('2016-09-08', '2016-12-26', '2017-03-01', -11.5), ('2018-01-29', '2018-03-23', '2018-07-20', -9.6), ('2018-08-28', '2018-10-26', '2020-11-09', -14.1), ('2021-10-18', '2022-05-13', '2023-07-20', -13.8), ('2024-09-27', '2026-03-30', 'None', -17.3)]
Mix N/NN/G thirds drawdowns >8%: [('2011-01-03', '2011-02-09', '2011-09-21', -11.2), ('2011-09-21', '2011-10-05', '2011-11-08', -8.1), ('2011-11-08', '2011-12-29', '2012-02-09', -11.1), ('2012-02-21', '2012-05-16', '2012-08-23', -8.5), ('2013-01-15', '2013-06-26', '2014-03-06', -11.5), ('2015-01-28', '2016-01-21', '2016-06-15', -10.9), ('2016-09-08', '2016-12-26', '2017-02-22', -11.9), ('2018-08-31', '2018-10-26', '2019-06-25', -9.6), ('2020-02-24', '2020-03-23', '2020-07-01', -23.2), ('2022-04-11', '2022-06-20', '2022-08-18', -11.8), ('2024-09-27', '2025-02-28', '2025-04-21', -10.5), ('2026-01-29', '2026-03-23', 'None', -17.0)]
Trend rotation N/NN/G drawdowns >8%: [('2011-01-03', '2011-02-03', '2011-08-11', -9.3), ('2013-01-15', '2013-04-09', '2014-05-12', -8.9), ('2015-08-06', '2016-01-21', '2016-07-01', -8.8), ('2016-09-08', '2016-12-26', '2017-04-25', -10.3), ('2018-01-23', '2018-12-10', '2020-01-03', -10.1), ('2021-11-15', '2022-05-13', '2023-12-04', -12.9), ('2024-09-27', '2024-11-14', '2025-04-21', -9.0), ('2026-01-29', '2026-10-23', 'None', -15.5)]
Rank top2 N/NN/G drawdowns >8%: [('2013-01-15', '2014-02-03', '2014-05-22', -18.5), ('2015-04-13', '2015-05-07', '2015-08-05', -9.2), ('2015-08-06', '2016-01-21', '2016-09-08', -12.2), ('2016-09-08', '2016-12-26', '2017-05-04', -11.0), ('2018-01-23', '2019-05-13', '2020-07-21', -17.0), ('2020-08-07', '2020-09-24', '2020-11-09', -8.9), ('2021-10-18', '2022-12-23', '2024-02-16', -20.8), ('2024-09-27', '2025-01-13', '2025-09-03', -14.2), ('2026-01-29', '2026-11-11', 'None', -20.7)]
Nifty trend+liquid       rolling 3y CAGR: min -4.1 median 10.3 max 20.4  share<5%/yr 10%
Mix N/NN/G thirds        rolling 3y CAGR: min 0.9 median 13.2 max 28.2  share<5%/yr 1%
Trend rotation N/NN/G    rolling 3y CAGR: min 2.6 median 9.1 max 25.5  share<5%/yr 7%
Rank top2 N/NN/G         rolling 3y CAGR: min 1.0 median 8.9 max 25.5  share<5%/yr 17%
NIFTYBEES hold           rolling 3y CAGR: min -3.5 median 13.2 max 31.0  share<5%/yr 5%
trend rotation rebalances: 74 avg liquid weight 0.37
```

## What the numbers say

1. **No timing rule beat holding the same ETFs.** From 2011 to 2026 the static one-third mix of NIFTYBEES,
   JUNIORBEES and GOLDBEES made 12.5% a year after tax (11.9% after exit tax) with a worst fall of 23%.
   The best rotation rules on the same three ETFs made 8.8-8.9%. The static mix also beat every rotation
   variant in each long sub-period tested (2010-2018 and 2019-2026), and in 2016-2020 and 2021-2026. The
   only window where a rotation rule won was 2011-2015, where rank top-1 and top-2 beat the mix.
2. **What timing bought was a shallower worst fall, at a price of 3 to 4 points a year.** Trend rotation's
   worst fall was 15% against 23% for the static mix and 36% for NIFTYBEES. Its worst rolling three-year
   return was +2.6% a year against +0.9% for the mix and -3.5% for NIFTYBEES.
3. **Tax and costs take about a point a year from the rotation rules** (trend [N,NN,G]: 9.62% pre-tax,
   8.82% after; rank top-1: 13.75% pre-tax, 11.96% after), and almost nothing from the static mix (12.68%
   to 12.48%). Rank top-1 paid Rs 4.1 lakh in tax on Rs 5 lakh of starting capital.
4. **Gold explains the rotation results that look good.** Without gold, rotation made 3.7-8.7% a year
   depending on the variant, below simply holding NIFTYBEES (10.1%). With gold, trend rotation made 7.0% in 2010-2018 (gold hurt:
   the no-gold version made 7.9%) and 12.2% in 2019-2026 (no-gold: 9.0%). GOLDBEES made 6.1% a year in
   2010-2018 and 19.5% a year in 2019-2026, including +72% in calendar 2025.
5. **Parking idle money in a liquid ETF is worth about 1.2 points a year to the Nifty trend rule**
   (5.86% to 7.07% after tax, 2011-2026) because it is out of the market about 23% of the time. The rule
   still trailed buy-and-hold NIFTYBEES by 2.4 to 3 points a year, with a worst fall of 22% against 36%.
6. **Fragile parameters.** Rank top-2 ranged from 8.4% to 10.0% across seven lookback choices, and top-1 on
   different ETF lists from 3.7% to 14.4%. The Nifty trend rule ranged from 6.3% to 7.6% across twelve
   average-length and buffer choices, with worst falls from 18% to 27%. No setting is reliably best.
7. **A day's delay matters little.** Filling the same day, the next day or two days later changed trend
   rotation's result from 9.1% to 8.8% to 8.6%, and the Nifty trend rule's from 7.2% to 7.1%. A missed 15:10 run
   that trades the next session is therefore tolerable for these monthly rules.
8. **Capital hardly matters between Rs 1 lakh and Rs 20 lakh** (static mix 12.46% / 12.48% / 12.42%; trend
   rotation 8.84% / 8.82% / 8.57%): fixed charges fall with size while the Rs 1.25 lakh exemption covers
   less of a larger account's gains.
9. **Adding the Nasdaq 100 ETF raised every backtest** (it made 23.6% a year), but the ETF now trades 18%
   or more above its NAV because fund houses cannot create units, so the backtest cannot be reproduced.

## Limits of these backtests

- Sixteen years, one country, one gold bull market and no multi-year equity bear market after 2011. The
  2008 crash, where trend rules did their best work elsewhere, predates the ETF price data.
- FY 2026-27 tax rules are applied to every year; the real rules differed before 2018 and before 2024.
- Yahoo prices are closes of thinly traded ETFs in the early years and can sit away from NAV.
- The liquid ETF is modelled, not traded; real liquid ETFs earned about 0.2-0.5% a year less than the index.
- Whole-share rounding, partial fills and ETF premiums at the moment of trading are not modelled.

## 4. A machine-learning market filter, tested walk-forward (run 11 November 2026)

The question: can a machine-learning model decide better than the 200-day rule when to hold the Nifty and
when to sit in the liquid ETF? This is the most favourable honest setup for ML that free data allows.

- **Data:** 216 month-ends of the Nifty 50 index (`^NSEI`, price only), Oct 2008 to Sep 2026.
- **Target:** did the Nifty beat the liquid ETF over the following month? (Yes in 53% of months.)
- **Features, all known at the month-end:** 1-, 3-, 6- and 12-month returns; distance from the 200- and 50-day
  averages; 20- and 60-day volatility; fall from the one-year high; short-term over long-term volatility.
- **Models:** logistic regression, gradient boosting, random forest (scikit-learn, small and regularised).
- **Walk-forward:** the model is refitted every month on all earlier months only (at least 60), then predicts
  the next month. Out-of-sample decisions: 156, Oct 2013 to Sep 2026. Invested when the predicted
  probability is above 0.5 (or above the base rate so far), otherwise in the liquid ETF.
- Monthly returns, 0.10% cost per switch, before tax unless stated.

```
months 216 from 2008-10-31 to 2026-09-30; months where the Nifty beat cash: 53%
out-of-sample: 2013-10-31 to 2026-09-30 (156 monthly decisions)
always hold the Nifty                10.5% a year   worst fall  -29.3%   in market  100%   right   54%   switches 0
200-day rule (above average)          9.1% a year   worst fall  -15.6%   in market   74%   right   52%   switches 25
12-month return beats cash            3.5% a year   worst fall  -36.3%   in market   66%   right   47%   switches 25
ML: logistic regression, p>0.5        8.4% a year   worst fall  -10.3%   in market   53%   right   46%   switches 57
ML: gradient boosting, p>0.5         11.5% a year   worst fall  -10.7%   in market   48%   right   54%   switches 75
ML: random forest, p>0.5             12.2% a year   worst fall  -10.8%   in market   51%   right   52%   switches 82
ML: logistic regression, p>base rate    9.7% a year   worst fall   -7.5%   in market   39%   right   53%   switches 65
ML: gradient boosting, p>base rate   12.4% a year   worst fall   -6.7%   in market   39%   right   55%   switches 77
ML: random forest, p>base rate       12.8% a year   worst fall   -6.2%   in market   40%   right   54%   switches 71
random 80%-invested signals: median 9.5% a year, 5th-95th percentile 6.5% to 12.7%

1. Seeds (p > 0.5), full out-of-sample 2013-10..2026-09:  CAGR / worst fall / time in market
   gradient boosting  CAGR min 11.1 median 12.3 max 13.7;  worst fall -13.3 to -6.6
   random forest      CAGR min 10.3 median 11.5 max 12.3;  worst fall -10.8 to -7.8
2. Sub-periods (split at 2020-04-30): first half | second half, CAGR
   always hold                                            7.1 |  14.0   full  10.5  fall  -29.3  in market 100%
   200-day rule                                           5.5 |  12.7   full   9.1  fall  -15.6  in market  74%
   ML gradient boosting                                  13.4 |   9.7   full  11.5  fall  -10.7  in market  48%
   ML random forest                                      11.0 |  13.5   full  12.2  fall  -10.8  in market  51%
   ML logistic                                            8.6 |   8.2   full   8.4  fall  -10.3  in market  53%
   plain rule: 20-day volatility below its 3-year median  10.2 |   7.3   full   8.7  fall   -7.8  in market  58%
   plain rule: 20-day volatility below 18%                6.9 |  11.2   full   9.0  fall  -20.3  in market  84%
3. Random signals with the same time in market and the same number of switches (block-shuffled), 5000 draws
   ML gradient boosting   actual 11.5%; shuffled median 7.6%, 95th pct 11.5%; share of shuffles that did as well: 4.8%
   ML random forest       actual 12.2%; shuffled median 7.8%, 95th pct 11.7%; share of shuffles that did as well: 3.1%
4. After costs and tax, through thunderbot's backtester (NIFTYBEES or the liquid ETF, Rs 5 lakh, 30% slab)
   always hold                                          pre-tax  11.4  after tax  11.4  if sold and taxed  10.6  worst fall  -36.3  trades   2  tax paid        0
   200-day rule                                         pre-tax   9.7  after tax   9.0  if sold and taxed   8.9  worst fall  -15.9  trades  76  tax paid    94631
   ML gradient boosting                                 pre-tax  12.2  after tax   9.4  if sold and taxed   9.4  worst fall  -15.0  trades 188  tax paid   345373
   ML random forest                                     pre-tax  12.6  after tax   9.7  if sold and taxed   9.7  worst fall  -15.0  trades 208  tax paid   369435
   plain rule: 20-day volatility below its 3-year median pre-tax   8.9  after tax   7.8  if sold and taxed   7.8  worst fall  -11.0  trades 106  tax paid   135736
```

What this shows:

1. **Before tax, the tree models looked better than everything else:** 11.5% to 12.8% a year against 10.5%
   for always holding the Nifty and 9.1% for the 200-day rule, with worst falls of 6% to 11% against 29%.
   They were right about the next month's direction 52-55% of the time, no better than always guessing
   "up" (54%); the gain came from being out during a few very bad months, mostly when volatility was high.
2. **The edge is not statistically distinguishable from luck.** Signals with the same time in the market and
   the same number of switches, shuffled in time, did as well in 3.1% (random forest) and 4.8% (gradient
   boosting) of 5,000 draws. Six model-and-threshold variants were tried, so one result at that level is
   expected by chance. Changing only the random seed moved the result between 10.3% and 13.7% a year.
   Gradient boosting made 13.4% a year in the first half and 9.7% in the second, when holding made 14.0%.
3. **After tax the edge is gone.** Run through Thunderbot's backtester (NIFTYBEES or the liquid ETF, Rs 5
   lakh, next-day fills, FY 2026-27 tax at a 30% slab) the two tree models made 12.2% and 12.6% a year
   before tax but 9.4% and 9.7% after it, against 11.4% for holding NIFTYBEES (10.6% if sold and taxed at
   the end). They traded 188 and 208 times and paid Rs 3.5-3.7 lakh in tax. The 200-day rule made 9.0%
   after tax with 76 trades. The ML models did keep the worst fall to 15% against 36%.
4. **Logistic regression lost to buy-and-hold even before tax** (8.4%). A plain volatility rule (hold while
   20-day volatility is below its three-year median) made 8.7% before tax and 7.8% after.
5. **Decision:** not adopted. It is a market-timing rule with more trades, more tax and less evidence than the
   200-day rule, and it would add a 260 MB dependency to a function that otherwise needs 4 MB.

Intraday ML was not testable here at all: free 5-minute data covers 60 days, which is a few thousand bars
per symbol and one market regime. The published evidence on intraday ML for non-HFT traders is in
`llm_and_ml_trading_evidence.md`.
