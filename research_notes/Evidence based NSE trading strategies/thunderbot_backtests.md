# Thunderbot's own backtests (computed 23 Oct 2026, worker/thunderbot/daily.py)

Method: daily Yahoo Finance adjusted closes (split/dividend adjusted; bad ticks repaired, e.g. NIFTYBEES 6 Oct 2010 and the unadjusted Dec 2019 1:10 split). Decide on day t close, trade at day t+1 close. Groww delivery costs per order (brokerage min(20, 0.1%) floored at min(5, 2.5%), STT 0.1% each side for stocks and 0.001% sell-only for ETFs, NSE 0.00307%, SEBI 0.0001%, stamp 0.015% buy, GST 18%, DP Rs 23.60 per sell) plus 0.05% slippage per side. After-tax runs charge STCG 20% / LTCG 12.5% above Rs 1.25 lakh per FY, 4% cess, losses offset. Idle cash earns 6%/yr (liquid fund proxy). Capital Rs 5 lakh. Period 1 Jan 2011 to 22 Oct 2026 unless stated. Benchmark: NIFTYBEES buy-and-hold, pre-tax (9.47% CAGR, -36.3% max drawdown over this period).

## Strategy A: Nifty trend (NIFTYBEES while Nifty 50 > 200-day SMA, else cash)

| Variant | Pre-tax CAGR | After-tax CAGR | Max DD | Trades |
|---|---|---|---|---|
| 200DMA, 0% buffer, weekly check | 6.68% | 6.33% | -23.9% | 94 |
| 200DMA, 0% buffer, month-end check | 8.04% | 7.61% | -15.8% | 47 |
| 200DMA, 1% buffer, weekly check | 7.04% | 6.69% | -19.0% | 57 |
| 200DMA, 1% buffer, month-end check | 8.55% | 8.07% | -15.3% / -17.4% | 30 |

Sub-periods (1% buffer, weekly, after tax): 2011-2018 4.63% vs B&H 7.84%; 2019-2026 9.25% vs 11.25%. Max DD about -19% vs -25%/-36%.
Takeaway: gives up ~1-1.5 pts/yr of return in this bull-market sample for roughly half the drawdown. No survivorship bias (single ETF).

## Strategy B: Momentum rotation on today's Nifty 100 list (SURVIVORSHIP-BIASED)

Score = NSE-style: 6m and 12m return / 1y annualized vol, z-scored, averaged. Equal weight, hold top N, keep a holding while it ranks within keep_rank. Market filter: all cash when Nifty < 200DMA (checked at rebalance).

| Variant | Pre-tax CAGR | After-tax CAGR | Max DD (after tax) | Trades |
|---|---|---|---|---|
| monthly top15 keep25, filter on | 24.79% | 21.36% | -19.4% | ~2,270 |
| monthly top15 keep25, filter off | 28.11% | 25.15% | -36.7% | ~2,910 |
| quarterly top15 keep25, filter on | 18.53% | 16.12% | -37.5% | ~950 |
| semiannual top15 keep25, filter on | 20.24% | 18.38% | -35.6% | ~540 |
| monthly top30 keep45, filter on | 21.28% | 18.70% | -14.6% | ~3,960 |
| semiannual top30 keep45, filter on | 17.27% | 15.89% | -36.2% | ~965 |

Survivorship control: equal-weight buy-and-hold of the same 100 current members (quarterly rebalanced) returned 19.56% after tax 2011-2026 (vs 9.47% for NIFTYBEES), i.e. roughly 10 pts/yr of the result is survivorship bias, not skill. Momentum's edge over that equal-weight control: +5.6 pts/yr unfiltered, +7.6 pts vs the filtered equal-weight (13.79%). Sub-periods after tax, momentum monthly+filter vs equal-weight survivors: 2011-18 17.46% vs 15.67%; 2019-26 25.11% vs 23.75%.
Takeaway: the momentum ranking adds value, but the absolute numbers are not achievable; anchor expectations on NSE's unbiased Nifty200 Momentum 30 TRI (18.8% vs 13.9% Nifty 200, 2005-2026, mostly back-test; live 5y 9.3% vs 6.4%).
The market filter only protects when checked monthly (quarterly/semiannual checks let the 2020 crash through: about -36% DD).

## Earlier intraday result (for context)
Opening-range breakout, VWAP reversion and EMA pullback on 5 Nifty stocks, 5-minute Yahoo bars, 39 trading days (21 Aug - 16 Oct 2026), Rs 1 lakh: net -10,817 / -9,890 / -13,293 after costs; profit factors 0.40 / 0.18 / 0.30.
