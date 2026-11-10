"""Reproduction check of the reader's rule b (their file: cash 6%, decide t, trade t+1 close, Rs 5 lakh, costs, 1 Jan 2011 - 22 Oct 2026)."""
import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/rotation')
from engine import *
P=P0[['N50']]; dd=decision_dates('ME')
SGi=SG0[['N50']]; SGe=P0[['N50']]
print("signal | buffer | lag | cash | costs  -> CAGR, MDD (peak->trough), orders, switches;   period 2010-12-31..end")
for end in ['2026-10-22','2026-10-26']:
  for sgn,SGx in [('index',SGi),('NIFTYBEES',SGe)]:
    for buf in [1.01,1.00]:
        T=tgt_trend(SGx,['N50'],dd,200,buf)
        for lag in [0,1]:
            for cm in ['c0','c6']:
                for costs in [False,True]:
                    eq,st=simulate(px_with_cash(P,cm),T,'2010-12-31',end,capital=500000,costs=costs,liq_etf=False,lag=lag); pf=perf(eq)
                    eq2,st2=simulate(px_with_cash(P,cm),T,'2010-12-31',end,capital=500000,costs=True,tax=True,liq_etf=False,lag=lag,slab=0.312)
                    y=pf['years']
                    print(f"end {end} {sgn:9s} buf {buf:.2f} lag {lag} {cm} costs {int(costs)} -> {pf['cagr']:5.2f}%  MDD {pf['mdd']:6.1f} ({pf['peak']}->{pf['trough']}) orders {st['orders']} | after tax+costs (cash interest untaxed here) {((eq2.iloc[-1]/5e5)**(1/y)-1)*100:5.2f}% liquidated {((st2['liq_value']/5e5)**(1/y)-1)*100:5.2f}%")
T=tgt_trend(SGi,['N50'],dd,200,1.01)
on=T['N50']['2010-12-01':]; ch=on[on.diff()!=0]; print('switch dates (month-end decisions), 1=in:', [(d.date().isoformat(),int(v)) for d,v in ch.items()])
eq,st=simulate(px_with_cash(P,'c6'),T,'2010-12-31','2026-10-26'); ye=eq.groupby(eq.index.year).last().pct_change(); ye.iloc[0]=eq.groupby(eq.index.year).last().iloc[0]/1-1
bh=P['N50']['2010-12-31':]; yb=bh.groupby(bh.index.year).last().pct_change()
print(pd.DataFrame({'rule b (6% cash)':ye*100,'NIFTYBEES':yb*100}).round(1).T.to_string())
