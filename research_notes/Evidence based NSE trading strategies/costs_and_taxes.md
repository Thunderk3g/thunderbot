# Costs and Taxes for NSE Equity Trading via Groww (Delivery/CNC and Intraday/MIS), as of October 2026

## 1. STT on equity delivery and intraday (after Budget 2024 and later changes)

### Takeaway
STT on NSE equity cash has not changed in Budget 2024, 2025 or 2026. Delivery (CNC) pays 0.1% on both the buy and the sell leg. Intraday (MIS) pays 0.025% on the sell leg only. The Budget 2026 STT hike, effective 1 April 2026, applies only to F&O: futures went from 0.02% to 0.05%, and options from 0.10% to 0.15% on premium and 0.125% to 0.15% on exercise.

### Cited Findings
- Groww pricing: STT for intraday is 0.025% on sell orders; for delivery it is 0.1% on both buy and sell. — [Groww Pricing](https://groww.in/pricing)
- Zerodha cross-check gives the same rates: equity delivery 0.1% on buy and sell, intraday 0.025% on the sell side. — [Zerodha Charges](https://zerodha.com/charges)
- Budget 2026 changed STT from 1 April 2026 as follows: futures 0.02% to 0.05%, options premium 0.10% to 0.15%, options exercise 0.125% to 0.15%. Equity delivery (0.1%) and intraday (0.025%) are unchanged. — [Upstox News](https://upstox.com/news/personal-finance/tax/explained-how-the-stt-hike-on-equity-futures-and-options-affects-traders-and-investors/article-189260/); [Finnovate](https://www.finnovate.in/learn/blog/budget-2026-stt-hike-fno-trades-explained)
- One worked example in the Upstox article labels the old futures rate as 0.025%, which conflicts with its own rate table (0.02%). The table value of 0.02% agrees with other sources. — [Upstox News](https://upstox.com/news/personal-finance/tax/explained-how-the-stt-hike-on-equity-futures-and-options-affects-traders-and-investors/article-189260/)

### Inferences
- Backtester formulas:
  - `STT_CNC = 0.001 × buy_value + 0.001 × sell_value`
  - `STT_MIS = 0.00025 × sell_value`
- Contract notes conventionally round STT to the nearest rupee. For small trades this rounding creates a few paise to ₹1 of noise. Exact rounding rules were not verified, so treat this as a convention.
- If a strategy uses F&O, its STT inputs must switch to the new rates for trades from 1 April 2026.

### Gaps
- I did not read the primary Finance Act 2026 or CBDT notification text. The F&O STT figures come from broker and financial-media explainers, which agree with one another.

## 2. Exchange transaction charges, SEBI fee, stamp duty, GST, IPFT

### Takeaway
All-in NSE cash exchange cost is about 0.00307% per side (₹3.07 per lakh). Brokers show it in two ways, and the totals are the same:
- Groww: transaction charge 0.00297% + IPFT 0.0001%
- Zerodha: a single 0.00307% figure that includes IPFT

Other per-side charges:
- SEBI turnover fee: 0.0001% (₹10 per crore) on each side.
- Stamp duty, buy side only: 0.015% for delivery, 0.003% for intraday.
- GST: 18% on brokerage + exchange charges + IPFT + SEBI fee + DP charges. GST is not charged on STT or stamp duty.

### Cited Findings
- Groww lists NSE transaction charges at 0.00297% and BSE at 0.00375%, the same for intraday and delivery. Its BSE table also shows 0.00345% for most groups. It lists the SEBI turnover charge at 0.0001% on buy and sell, and the NSE IPFT charge at 0.0001% on buy and sell. — [Groww Pricing](https://groww.in/pricing); [Groww Help: charges in report](https://groww.in/help/stocks,-f&o,-ipo-&-mtf/discoverable/what-are-the-different-charges-mentioned-in-the-report)
- Groww stamp duty is 0.003% on intraday buys and 0.015% on delivery buys. — [Groww Pricing](https://groww.in/pricing)
- Groww applies 18% GST to brokerage, DP charges, exchange transaction charges, IPFT, the SEBI turnover charge, auto square-off charges, API charges and some other fees. — [Groww Pricing](https://groww.in/pricing)
- Zerodha lists the NSE transaction charge at 0.00307%. Its support page gives the same rate as ₹3.07 per lakh and says "NSE IPFT charges are included in the exchange transaction fees." Zerodha also lists SEBI charges at ₹10/crore and stamp duty at 0.015% (₹1500/crore) for delivery buys and 0.003% (₹300/crore) for intraday buys. Its GST base is brokerage + SEBI + transaction charges. — [Zerodha Charges](https://zerodha.com/charges); [Zerodha Support](https://support.zerodha.com/category/account-opening/resident-individual/ri-charges/articles/exchange-transaction-charges)
- History of the NSE rate:
  - **Effective 1 October 2024 (SEBI "true-to-label" uniform charges):** cash market ₹2.97 per lakh per side, replacing the earlier slab-based ₹3.22–3.25 per lakh. — [search summary of NSE circular, via Geojit and other broker notices](https://notifications.geojit.com/exchange-circulars/cash-segment); [Business Standard (older 0.00325% context)](https://www.business-standard.com/markets/news/nse-to-cut-cash-derivatives-transaction-charges-by-1-from-april-1-124031200766_1.html)
  - **Effective 1 March 2026 (circular NSE/FA/73061, dated 27 February 2026):** NSE rolled the trading-member IPFT contribution back to pre-April 2023 levels, ₹0.01 per crore each side. It raised transaction charges by a matching amount, so the overall outflow is unchanged for cash, equity futures and equity options. — [TeamLease RegTech](https://www.teamleaseregtech.com/updates/article/53156/nse-issued-a-circular-regarding-the-revision-in-transaction-charges/); [NSE circular PDF](https://nsearchives.nseindia.com/content/circulars/FA73061.pdf) (the fetch returned 503, so the content was taken from search excerpts)
- **Conflict:** IndMoney's pricing page shows 0.00322% for NSE, which appears to be the pre-October 2024 slab rate and out of date. — [IndMoney Pricing](https://www.indmoney.com/pricing)

### Inferences
- Groww still shows 0.00297% + 0.0001% IPFT, which reflects the pre-March 2026 split. The sum is 0.00307%, the same as Zerodha's post-March 2026 combined figure. For a backtester, model a single combined rate of **0.00307% per side** of turnover, with GST on top.
- Per-side regulatory formulas (V = traded value for that leg):
  - `exch = 0.0000307 × V` (each side; the IPFT component is included)
  - `sebi = 0.000001 × V` (each side)
  - `stamp_CNC = 0.00015 × V_buy`; `stamp_MIS = 0.00003 × V_buy`
  - `GST = 0.18 × (brokerage + exch + sebi + DP)`
- There is a small presentation difference: Zerodha's footnote states IPFT as "₹0.01 per crore," while Groww shows 0.0001% (₹10 per crore). Either way the totals reconcile to ₹3.07 per lakh, and the effect is immaterial for backtesting.

### Gaps
- I could not open the text of NSE circular FA73061 (HTTP 503), so the exact post-March 2026 split between transaction charge and IPFT is not confirmed. The ₹0.01/crore IPFT figure and the "unchanged outflow" statement come from TeamLease and search excerpts.
- The exact rounding conventions for stamp duty and exchange charges on contract notes were not verified.

## 3. Groww brokerage, DP charges, AMC, MTF interest, auto square-off

### Takeaway
Groww brokerage is the same for delivery and intraday: ₹20 or 0.1% of order value per executed order, whichever is lower. If that comes to less than ₹5, the charge is the lower of ₹5 or 2.5% of trade value. DP charges for a delivery sell are ₹16.5 (Groww) + ₹3.5 (CDSL) = ₹20, plus 18% GST = **₹23.60 per scrip per sell day**. Women pay ₹3.25 CDSL, so ₹23.31. Intraday has no DP charge. Other charges: AMC ₹0, MTF interest 14.95% p.a., auto square-off ₹50 + GST per position.

### Cited Findings
- Groww brokerage on stocks is "₹20 or 0.1% of the executed order value, whichever is lower," with a ₹5 minimum. — [Groww Pricing](https://groww.in/pricing)
- Groww Help adds the minimum rule: "if the brokerage per trade is less than ₹5, then the minimum charge will be the lower of ₹5 or 2.5% of your trade value." The same formula applies to delivery and intraday. — [Groww Help](https://groww.in/help/stocks,-f&o,-ipo-&-mtf/discoverable/what-are-the-different-charges-mentioned-in-the-report)
- DP charges on delivery sells are ₹16.5 (Groww) plus the depository fee (₹3.5 for male, ₹3.25 for female clients), with 18% GST on the total. The ₹16.5 component is waived when the debit or sell value is under ₹100. Intraday DP is ₹0. — [Groww Help](https://groww.in/help/stocks,-f&o,-ipo-&-mtf/discoverable/what-are-the-different-charges-mentioned-in-the-report); [Groww Pricing](https://groww.in/pricing)
- Account maintenance charge is ₹0. MTF interest is 14.95% p.a. on the funded amount, and MTF brokerage is 0.1% of order value per order. Auto square-off is ₹50 per open intraday position squared off by the system, plus GST. Pledge or unpledge is ₹20 per ISIN plus GST. — [Groww Pricing](https://groww.in/pricing)
- Earlier Groww terms were a ₹2 minimum brokerage and ₹18.5 DP per ISIN. According to a search summary of a Finology article, these changed around June 2025. The article could not be fetched (403), so the exact effective date is unverified. — [Finology (search summary)](https://select.finology.in/articles/broker/groww-latest-fees-update-2025)
- For comparison, Zerodha charges ₹0 brokerage on delivery, 0.03% or ₹20 (whichever is lower) on intraday, and DP of ₹15.34 per scrip including GST. — [Zerodha Charges](https://zerodha.com/charges)

### Inferences
- Brokerage formula per executed order:
  `b = min(20, 0.001·V); if b < 5: b = min(5, 0.025·V)`
  The cap of ₹20 binds from V ≥ ₹20,000. The ₹5 floor applies when V < ₹5,000.
- DP formula: `DP = 23.60` per scrip per day with a delivery sell. It is charged once per scrip per day regardless of quantity or number of orders, the same way Zerodha describes its DP charge. Use `DP = 20 × 1.18` if GST is computed separately.
- Each executed order attracts brokerage. If an order fills in parts on the same day, brokerage is generally charged once per order, but this was not verified for Groww. Splitting a position into several orders multiplies the brokerage.
- Groww's ₹20 cap is per order, not a flat fee. For small delivery trades (under ₹20k) Groww is noticeably more expensive than Zerodha's zero-brokerage delivery.

### Gaps
- No dated 2026 Groww notice was found. All figures come from the live Groww pricing and help pages as fetched on 23 October 2026.
- MTF interest may be tiered or have changed during the year. Only the 14.95% flat figure was found.
- No call & trade charge was listed on the Groww page.

## 4. Capital gains tax and business-income treatment

### Takeaway
Listed equity on which STT was paid is taxed as follows (Budget 2024, effective for transfers on or after 23 July 2024; unchanged in Budget 2025 and Budget 2026):
- **STCG** (held 12 months or less): 20%, under Section 111A
- **LTCG** (held more than 12 months): 12.5% on gains above ₹1.25 lakh per financial year, under Section 112A
- Before 23 July 2024 the rates were 15% STCG and 10% LTCG above ₹1 lakh.

Intraday equity profits are speculative business income, taxed at slab rates. F&O income is non-speculative business income, also taxed at slab rates. From 1 April 2026 the Income Tax Act 2025 renumbers these sections but does not change the rates.

### Cited Findings
- From 23 July 2024: STCG under Section 111A rose from 15% to 20%; LTCG under Section 112A went to 12.5% (from 10%), and the exemption rose from ₹1 lakh to ₹1.25 lakh. The concessional rates require STT to have been paid. — [Quicko](https://learn.quicko.com/ltcg-equity-shares-equity-mutual-funds); [IndMoney Budget 2024](https://indmoney.com/articles/budget-2024-tax-updates); [Business Today](https://www.businesstoday.in/amp/personal-finance/tax/story/tax-calculation-what-ltcg-exemptions-are-available-under-new-tax-regime-check-details-460044-2025-01-08)
- Budget 2026 left the following unchanged for FY 2026-27: LTCG at 12.5%, the ₹1.25 lakh exemption, STCG at 20% and the 12-month holding period. AMFI's request for a ₹2 lakh exemption was not accepted. Related Budget 2026 changes: buyback proceeds move from dividend taxation to capital gains taxation, and the F&O STT hike. — [Bajaj Finserv](https://www.bajajfinserv.in/what-is-ltcg-tax-rate); [Angel One News](https://oga-prod.angelone.in/news/taxation/union-budget-2026-ltcg-tax-unchanged-at-12-5-stt-on-commodity-futures-hiked); [Sahi](https://www.sahi.com/blogs/ltcg-tax-mutual-funds-stocks-budget-2026)
- The Income Tax Act 2025 reorganises the capital-gains sections into a schedule from 1 April 2026. This is a change of form, not of rates. — [Patron Accounting](https://www.patronaccounting.com/blog/itr-capital-gains-notifications-2026-what-changed); [Sahi](https://www.sahi.com/blogs/ltcg-tax-mutual-funds-stocks-budget-2026)
- Business-income treatment:
  - Intraday equity is speculative business income under Section 43(5) of the 1961 Act, which becomes Section 66 of the 2025 Act from 1 April 2026.
  - Exchange-traded F&O is non-speculative business income.
  - Speculative losses can be set off only against speculative income and carried forward 4 years.
  - Non-speculative F&O losses can be set off against other income except salary and carried forward 8 years, if the return is filed on time.
  - Both are reported in ITR-3. Section 44AD presumptive taxation is not available for speculative income.
  - Tax-audit threshold under Section 44AB is turnover of ₹10 crore, where turnover is the sum of absolute per-trade P&L.
  — [1 Finance](https://1finance.co.in/blog/itr-for-fo-and-intraday-traders-ay-2026-27/); [Sahi – intraday tax](https://www.sahi.com/blogs/income-tax-on-intraday-trading-india); [Richify calculator](https://www.richify.ai/in/tools/intraday-trading-tax-calculator)

### Inferences
- Backtester tax model:
  - CNC sold within 12 months or less: `tax = 0.20 × max(0, net STCG)`
  - CNC held more than 12 months: `tax = 0.125 × max(0, net LTCG − 125000)` per financial year
  - MIS: `tax = slab_rate × net speculative profit`. At the 30% top slab, the effective rate including cess (4%) and surcharge is about 31.2% or more.
- Cess is not included in the 20% and 12.5% headline rates. The 4% Health & Education cess applies on top, giving 20.8% and 13% effective, before any surcharge. Surcharge on 111A and 112A gains is capped at 15%. These figures are general knowledge and were not re-verified in this session.
- Transaction costs other than STT, such as brokerage, exchange charges, stamp duty and DP, are deductible from capital gains as costs of transfer or acquisition. STT itself is not deductible against capital gains. For business income (intraday, F&O), expenses are deductible, and STT is generally treated as a deductible expense. This is general knowledge and was not verified in this session.

### Gaps
- No primary incometax.gov.in or Finance Act text was fetched. The rates are confirmed by several consistent secondary sources.
- The cess and surcharge details and the treatment of STT and costs as deductions come from general knowledge and were not sourced in this session.
- Sources disagree on the exact audit-turnover basis for intraday (speculative) trading.

## 5. Groww Trade API pricing and rate limits (2026)

### Takeaway
The Groww Trade API costs **₹499/month + 18% GST**, or **₹4,999/year + GST** (about ₹417/month). A free tier allows order placement, modification and cancellation, smart orders (GTT/OCO), positions, holdings and margins, but it does **not** include live data (quotes, LTP, OHLC, option chain, Greeks) or historical candles for backtesting. The documentation gives these rate limits: orders 10/sec and 250/min; live data 10/sec and 300/min; non-trading 20/sec and 500/min; authentication 5/sec and 30/min. The live feed allows up to 1,000 subscriptions according to the documentation, while the blog says 3,000.

### Cited Findings
- The Groww blog (published 30 September 2026) lists these plans: Free Trial ₹0 (all APIs except Live Data and Backtesting), Monthly ₹499/month + taxes, Yearly ₹4,999/year (₹417/month) + taxes. Plans auto-renew from the Groww balance, and GST is shown at 18%. The blog says the difference between free and paid is "data access, not order placement." — [Groww Blog: API Trading on Groww](https://groww.in/blog/api-trading-on-groww)
- The same blog lists 250 order requests/min, 300 market-data requests/min, 300 OHLC requests/min, **3,000 real-time subscriptions per user**, 25 modifications per order, 5 sessions per user and an average response time of about 65 ms. — [Groww Blog](https://groww.in/blog/api-trading-on-groww)
- The Python SDK documentation gives limits by type, shared by every API of that type:

  | Type | Per second | Per minute |
  |---|---|---|
  | Authentication | 5 | 30 |
  | Orders | 10 | 250 |
  | Live Data | 10 | 300 |
  | Non-Trading | 20 | 500 |

  The access-token endpoint is also limited to 150 requests per 24 hours. The documentation gives the live feed as "up to **1000** subscriptions." Two authentication flows exist: API key + secret, which "requires daily approval," and TOTP, labelled "No Expiry." — [Groww Trade API Python SDK docs](https://groww.in/trade-api/docs/python-sdk)
- Marketcalls reports the price as ₹499 flat, down from ₹2,000 earlier, with all modules included. — [Marketcalls](https://www.marketcalls.in/fintech/groww-enters-the-algo-arena-with-powerful-trading-apis.html)
- Groww's pricing page lists "API charges" among the items that attract 18% GST. — [Groww Pricing](https://groww.in/pricing)

### Inferences
- The yearly cost with GST is ₹4,999 × 1.18 ≈ ₹5,899. On a ₹5 lakh account that is about 1.2% a year of fixed drag, and on ₹20 lakh about 0.3%. A backtester should model it as a fixed annual cost, not a per-trade cost.
- The live-feed subscription limit conflicts between sources: 1,000 in the SDK docs and 3,000 in the blog. Design to 1,000 to be safe. A Nifty 200 universe fits within either limit.
- Use the TOTP flow for unattended bots, because the key + secret flow needs a manual approval every day.

### Gaps
- No per-order API surcharge was found. The blog and a third-party review (Chittorgarh) say there is none, but Groww's separate "Pricing" page for the API was not fetched.
- Static-IP requirements (part of SEBI's retail algo framework) are not mentioned in the Groww documentation I read.

## 6. Bid-ask spread and slippage (NSE impact cost)

### Takeaway
NSE reports the Nifty 50 index impact cost at **0.02% for a ₹50 lakh basket**, for both March 2025 and March 2026. The Nifty Next 50's last published figure found was 0.04% (March 2019, ₹25 lakh basket). No Nifty 200 figure was found. Stocks are eligible for index inclusion only if their impact cost is 0.50% or less for a ₹10 crore basket in 90% of observations.

### Cited Findings
- Nifty 50 impact cost is 0.02% for a ₹50 lakh portfolio, as of March 2025 and March 2026. — [NSE Nifty 50 index page (search snippet)](https://www.nseindia.com/products-services/indices-nifty50-index) (the direct fetch returned 403)
- Nifty Next 50 impact cost was 0.04% for March 2019, at a ₹25 lakh basket. — [NSE Nifty Next 50 page](https://nseindia.com/products/content/equities/indices/nifty_next_50.htm)
- Eligibility criterion: average impact cost of 0.50% or less for 90% of observations over six months, for a ₹10 crore basket. — [Nifty 50 methodology whitepaper 2025](https://niftyindices.com/docs/default-source/indices/nifty-50/nifty-50-whitepaper_2025.pdf)
- Freefincal analysis notes that even some large-cap stocks have materially higher impact cost than the index basket figure suggests. — [Freefincal](https://freefincal.com/impact-cost/)

### Inferences
- Index-level impact cost is a weighted basket figure. Individual Nifty 50 names are mostly about 0.01–0.05%. Midcaps in the Nifty 200 (Midcap 100 part) are typically several times wider. This is a reasoned estimate, not a sourced number.
- Suggested per-side slippage assumptions for the backtester (conservative, my inference):
  - Nifty 50: 0.03–0.05%
  - Rest of Nifty 100: about 0.05–0.08%
  - Midcap 100 part of the Nifty 200: about 0.08–0.15%
  - Add more at the open, at the close, and for market orders around news.
  - Calibrate these against Groww fill data when it is available.
- At these slippage levels, round-trip slippage (0.06–0.3%) is comparable to or larger than the explicit intraday costs for trades of ₹1 lakh or more.

### Gaps
- No Nifty 200 or per-stock impact cost figures were retrieved. NSE publishes per-security impact cost in its monthly index reports and the niftyindices factsheets, but those files were not accessed.
- The NSE pages returned 403 to direct fetches, so the 0.02% figure comes from search snippets.

## 7. Worked examples: round-trip cost as % of trade value (Groww, NSE)

### Takeaway
At Groww's current schedule, explicit round-trip costs, excluding slippage and income tax, are:

| Trade size (each leg) | Delivery (CNC) | Intraday (MIS) |
|---|---|---|
| ₹10,000 | ₹69.45 (0.69%) | ₹27.15 (0.27%) |
| ₹1,00,000 | ₹293.28 (0.29%) | ₹82.68 (0.08%) |
| ₹10,00,000 | ₹2,295.61 (0.23%) | ₹402.01 (0.04%) |

STT dominates delivery costs at larger sizes, with a floor of about 0.2% plus 0.015% stamp duty. For small trades, fixed brokerage and DP charges dominate.

### Cited Findings
- Inputs are from the sections above: Groww brokerage, DP, STT, stamp duty, exchange, IPFT and SEBI charges, and GST, from [Groww Pricing](https://groww.in/pricing) and [Groww Help](https://groww.in/help/stocks,-f&o,-ipo-&-mtf/discoverable/what-are-the-different-charges-mentioned-in-the-report). The NSE combined rate of 0.00307% per side is cross-checked against [Zerodha Charges](https://zerodha.com/charges).

### Inferences
**Formulas** (buy value Vb, sell value Vs; one order per leg):
```
brok(V)  = min(20, 0.001·V);  if brok < 5: brok = min(5, 0.025·V)
B        = brok(Vb) + brok(Vs)
EXCH     = 0.0000307 · (Vb + Vs)          # NSE txn 0.00297% + IPFT 0.0001%
SEBI     = 0.000001  · (Vb + Vs)
STT      = CNC: 0.001·(Vb + Vs)   | MIS: 0.00025·Vs
STAMP    = CNC: 0.00015·Vb        | MIS: 0.00003·Vb
DP       = CNC: 20 per scrip per sell-day (pre-GST) | MIS: 0
GST      = 0.18 · (B + EXCH + SEBI + DP)
TOTAL    = B + EXCH + SEBI + STT + STAMP + DP + GST
(+ ₹50×1.18 = ₹59 if an MIS position is auto-squared-off by Groww)
```

**Breakdown** (Vb = Vs = V; in ₹):

| Mode | V | Brokerage | STT | Exch+IPFT | SEBI | Stamp | DP | GST | Total | % of V |
|---|---|---|---|---|---|---|---|---|---|---|
| CNC | 10,000 | 20.00 | 20.00 | 0.61 | 0.02 | 1.50 | 20.00 | 7.31 | 69.45 | 0.69% |
| CNC | 1,00,000 | 40.00 | 200.00 | 6.14 | 0.20 | 15.00 | 20.00 | 11.94 | 293.28 | 0.29% |
| CNC | 10,00,000 | 40.00 | 2,000.00 | 61.40 | 2.00 | 150.00 | 20.00 | 22.21 | 2,295.61 | 0.23% |
| MIS | 10,000 | 20.00 | 2.50 | 0.61 | 0.02 | 0.30 | 0 | 3.71 | 27.15 | 0.27% |
| MIS | 1,00,000 | 40.00 | 25.00 | 6.14 | 0.20 | 3.00 | 0 | 8.34 | 82.68 | 0.08% |
| MIS | 10,00,000 | 40.00 | 250.00 | 61.40 | 2.00 | 30.00 | 0 | 18.61 | 402.01 | 0.04% |

- How the rows work out:
  - At ₹10,000, brokerage is 0.1% = ₹10 per leg, because the ₹20 cap does not bind.
  - From ₹20,000 per leg upward, the cap binds and brokerage is ₹40 per round trip.
- Combined with section 6, adding about 0.03–0.05% slippage per side for Nifty 50 names gives realistic all-in round-trip costs of about:
  - CNC: 0.75% at ₹10k, 0.35% at ₹1L, 0.30% at ₹10L
  - MIS: 0.33% at ₹10k, 0.15% at ₹1L, 0.12% at ₹10L
- Implication for strategy design: on Groww, a delivery swing trade needs an average gross edge well above about 0.3% per round trip at sizes of ₹1 lakh or more, and about 0.7% at ₹10k sizes, before tax. Intraday needs about 0.1–0.15% at ₹1L or more, but its profits are taxed at slab rates (up to about 31–39%), compared with 20% STCG for delivery.
- Groww's ₹20 cap is per order, so scaling in or out over several orders adds ₹23.60 (₹20 + GST) per extra order. The DP charge is per scrip per day, so selling one scrip in several orders on the same day still pays DP once.

### Gaps
- Exact contract-note rounding (STT to the nearest rupee, stamp duty rounding) is not modelled. It changes the small-trade figures by up to about ₹1–2.
- The examples assume the buy and sell prices are equal. With real P&L, Vs differs from Vb, and the sell-side charges scale with Vs.
