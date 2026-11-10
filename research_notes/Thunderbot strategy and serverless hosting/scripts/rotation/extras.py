"""Extras: yearly returns per strategy, average weights, holdings at last decision, MID150BEES check, b' row for Q4 table."""
import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/rotation')
from engine import *
from run4 import strategies, A4, A3
pd.set_option('display.width',300); pd.set_option('display.max_columns',40)
P=P0[A4]; SG=SG0[A4]; S=strategies(P,SG); dd=decision_dates('ME'); SGe=SG.copy(); SGe['N50']=P['N50']
S["b' same, signal on NIFTYBEES price"]=(tgt_trend(SGe,['N50'],dd,200,1.01),{})
PX=px_with_cash(P,'c6')
keys={'a':'a  B&H Nifty 50 (NIFTYBEES)','b':'b  Nifty>1.01x200DMA else cash',"b'":"b' same, signal on NIFTYBEES price",'c':'c  4 sleeves trend 1.00x','d':'d  dual mom top2 of 4, 200DMA filter','e-c':'e-c no gold: 3 equity sleeves 1.00x','e-d':'e-d no gold: top2 of 3 equity','f1':'f1 EW 4 assets, annual rebal','f2':'f2 75% N50 / 25% gold, annual'}
Y={}
for k,nm in keys.items():
    T,kw=S[nm]; e,s=simulate(PX,T,'2007-12-31','2026-10-26',**kw); Y[k]=e.groupby(e.index.year).last().pct_change().iloc[1:]*100
print("Calendar-year returns, pre-cost, cash at 6% (single run from 31 Dec 2007):"); print(pd.DataFrame(Y).round(1).to_string())
# b' rows for the Q4 table
for per,(a,z) in PERIODS.items():
    T,kw=S[keys["b'"]]; out=[]
    for cm in ['c6','c0','cA']:
        e,s=simulate(px_with_cash(P,cm),T,a,z); pf=perf(e); out.append((pf,s))
    pf,s=out[0]; print(f"b' {per}: CAGR6 {pf['cagr']:.1f} vol {pf['vol']:.1f} MDD {pf['mdd']:.1f} ({pf['peak']}->{pf['trough']}) worst {pf['worst_y']} {pf['worst']:+.1f} UW {pf['uw_years']:.1f}y {pf['uw']} orders/yr {s['orders']/pf['years']:.1f} cash {s['cash_share']*100:.0f}% | CAGR0 {out[1][0]['cagr']:.1f} MDD0 {out[1][0]['mdd']:.1f} CAGRA {out[2][0]['cagr']:.1f}")
# average target weights by period for c and d
for k in ['c','d']:
    T=S[keys[k]][0].reindex(days).ffill()
    for per,(a,z) in PERIODS.items(): print(k,per,'avg target weight %:',(T[a:z].mean()*100).round(0).to_dict())
print('targets at last decisions:'); 
for k in ['b',"b'",'c','d','e-c','e-d']: print(k, S[keys[k]][0].tail(3).round(2).to_dict('index'))
r=sma_ratio(SG,200); print('price / 200-DMA at 30 Sep and 26 Oct 2026:'); print(r.loc[['2026-09-30','2026-10-26']].round(3).to_string())
B=SG.bfill(); print('6m/12m returns at 30 Sep 2026:', ((SG/B.shift(126)-1).loc['2026-09-30']*100).round(1).to_dict(), ((SG/B.shift(252)-1).loc['2026-09-30']*100).round(1).to_dict())
# MID150BEES instead of the index for the midcap leg, 2019-2026 (start 2019-02-04 listing; use from 2019-12-31 to avoid thin first year)
P2=P.copy(); P2['MID']=P0['MID_ETF']; PX2=px_with_cash(P2,'c6')
for k in ['c','d','f1']:
    T,kw=S[keys[k]]
    for a in ['2018-12-31']:
        e1,_=simulate(PX,T,a,'2026-10-26',**kw); e2,_=simulate(PX2,T,a,'2026-10-26',**kw); p1=perf(e1); p2=perf(e2)
        print(f"{k} 2019-2026 midcap leg index PR: CAGR {p1['cagr']:.1f} MDD {p1['mdd']:.1f} | MID150BEES prices from 4 Feb 2019: CAGR {p2['cagr']:.1f} MDD {p2['mdd']:.1f}")
# contribution: c and d with gold sleeve forced to cash (gold never held) but still 4 slots -> isolates gold's return contribution
Tc=S[keys['c']][0].copy(); Tc['LIQ']+=Tc['GOLD']; Tc['GOLD']=0
Td=S[keys['d']][0].copy(); Td['LIQ']+=Td['GOLD']; Td['GOLD']=0
for nm,T in [('c, gold sleeve replaced by cash',Tc),('d, gold slot replaced by cash',Td)]:
    print(nm, {per: round(perf(simulate(PX,T,a,z)[0])['cagr'],1) for per,(a,z) in PERIODS.items()}, {per: round(perf(simulate(PX,T,a,z)[0])['mdd'],1) for per,(a,z) in PERIODS.items()})
# round trips for b
T=S[keys['b']][0]['N50']; x=T['2010-12-31':]; print('b switches 2011-2026:', int((x.diff().abs()>0).sum()), ' b\' switches:', int((S[keys["b'"]][0]['N50']['2010-12-31':].diff().abs()>0).sum()))
