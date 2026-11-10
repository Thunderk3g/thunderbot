import numpy as np
def groww(V,side):
    b=min(20,0.001*V); 
    if b<5: b=min(5,0.025*V)
    exch=0.0000307*V; sebi=0.000001*V; stt=0.001*V; stamp=0.00015*V if side=='buy' else 0; dp=20 if side=='sell' else 0
    return b+exch+sebi+stt+stamp+dp+0.18*(b+exch+sebi+dp)
def zerodha(V,side):
    exch=0.0000307*V; sebi=0.000001*V; stt=0.001*V; stamp=0.00015*V if side=='buy' else 0; dp=13 if side=='sell' else 0  # Zerodha DP 15.34 incl GST
    return exch+sebi+stt+stamp+dp+0.18*(exch+sebi+dp)
SLIP=0.0005
print("Per-trade cost at position size = capital/15")
for cap in (100000,500000,2000000):
    V=cap/15
    for nm,f in (('Groww',groww),('Zerodha',zerodha)):
        rt=f(V,'buy')+f(V,'sell'); print(f" cap {cap:>9,} pos {V:>9,.0f} {nm:8s} buy {f(V,'buy'):6.1f} sell {f(V,'sell'):6.1f} round-trip {rt:7.1f} = {rt/V*100:.2f}% (+{2*SLIP*100:.2f}% slippage) ; fixed part (brokerage+DP+GST) = {(rt-0.0021*V-0.0000636*V*1.18)/V*100:.2f}%")
print("\nAnnual explicit-cost drag (% of capital), 15 stocks, quarterly; name-replacement turnover TO (one-way); option: also re-equalise the ~survivors each quarter (extra small orders of ~10% of position, half buys half sells)")
for TO in (1.2,1.7):
    for cap in (100000,500000,2000000):
        V=cap/15; nrep=TO*15  # positions replaced per year
        for nm,f in (('Groww',groww),('Zerodha',zerodha)):
            c_rep=nrep*(f(V,'buy')+f(V,'sell'))
            nsurv=(15-nrep/4)*4; v=0.10*V
            c_reb=nsurv*(0.5*f(v,'buy')+0.5*f(v,'sell'))
            slip=2*SLIP*TO*cap
            print(f" TO {TO*100:.0f}% cap {cap:>9,} {nm:8s}: replacements {c_rep/cap*100:.2f}% + slippage {slip/cap*100:.2f}% = {100*(c_rep+slip)/cap:.2f}% ; with quarterly re-equalising +{c_reb/cap*100:.2f}% -> {100*(c_rep+slip+c_reb)/cap:.2f}% ; + Groww API Rs 5,899/yr = {5899/cap*100:.2f}%")
print("\nTax-deferral example")
def etf_after(g,ter,N,exempt_frac=0.0,rate=0.13):
    w=(1+g-ter)**N; gain=w-1; tax=gain*(1-exempt_frac)*rate; return ((w-tax)**(1/N)-1)*100
def diy_after(g,c,frac_st=1.0,frac_lt=0.0):
    # every year realise all gains: frac_st at 20.8%, frac_lt at 13% (no exemption), rest deferred ignored
    rate=frac_st*0.208+frac_lt*0.13
    return ((g-c)*(1-rate))*100
for g in (0.12,0.15,0.18):
    print(f" gross index return {g*100:.0f}%:")
    for N in (5,10):
        print(f"   ETF/index fund, cost+tracking 0.8%/yr, held {N}y, 13% LTCG on full gain at exit: {etf_after(g,0.008,N):.2f}% ; if gains fully inside Rs1.25L/yr exemption via annual harvesting: {(g-0.008)*100:.2f}%")
    for c in (0.005,0.010,0.015):
        a=diy_after(g,c,1.0,0.0); b=diy_after(g,c,0.7,0.3)
        print(f"   DIY same gross, costs {c*100:.1f}%: all STCG {a:.2f}% ; 70% STCG/30% LTCG {b:.2f}%")
    for N in (10,):
        tgt=etf_after(g,0.008,N)/100
        for c in (0.005,0.010,0.015):
            need=tgt/(1-0.208)+c; need2=tgt/(1-(0.7*0.208+0.3*0.13))+c
            print(f"   break-even DIY gross return to match ETF 10y after-tax ({tgt*100:.2f}%), costs {c*100:.1f}%: {need*100:.2f}% (alpha {100*(need-g):+.2f} pts) all-STCG ; {need2*100:.2f}% (alpha {100*(need2-g):+.2f}) 70/30 mix")
        tgt=(g-0.008)
        need=tgt/(1-0.208)+0.010; print(f"   vs ETF with gains harvested tax-free (small accounts): DIY needs {need*100:.2f}% gross at 1.0% cost (alpha {100*(need-g):+.2f} pts)")
print("\nMax corpus for tax-free harvesting: gain <= 1.25L/yr -> corpus <= 1.25L/return:", {r: round(125000/r) for r in (0.10,0.12,0.15,0.18)})
