"""Q5: costs and tax at Rs 1 lakh / 5 lakh / 20 lakh; four periods; slab sensitivity."""
import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/rotation')
from engine import *
from run4 import strategies, A4
P=P0[A4]; SG=SG0[A4]; S=strategies(P,SG); dd=decision_dates('ME')
SGe=SG.copy(); SGe['N50']=P['N50']
S["b' same, signal on NIFTYBEES price"]=(tgt_trend(SGe,['N50'],dd,200,1.01),{})
keys=['a  B&H Nifty 50 (NIFTYBEES)','b  Nifty>1.01x200DMA else cash',"b' same, signal on NIFTYBEES price",'c  4 sleeves trend 1.00x','c1 4 sleeves trend 1.01x','d  dual mom top2 of 4, 200DMA filter',
      'e-c no gold: 3 equity sleeves 1.00x','e-d no gold: top2 of 3 equity','u-c N50+NN50+GOLD sleeves 1.00x','u-d top2 of N50,NN50,GOLD','f1 EW 4 assets, annual rebal','f2 75% N50 / 25% gold, annual','f3 B&H Next 50 (JUNIORBEES)','f4 B&H Midcap (index PR chain)','f5 B&H Gold (GOLDBEES)']
PX=px_with_cash(P,'c6'); PX0=px_with_cash(P,'c0')
rows=[]
def one(nm,T,kw,per,cap,slab,px=PX,liq_etf=True,tag='liquid ETF 6%'):
    a,z=PERIODS[per]
    e0,s0=simulate(px,T,a,z,capital=cap,liq_etf=liq_etf,**kw); y=perf(e0)['years']
    e1,s1=simulate(px,T,a,z,capital=cap,costs=True,liq_etf=liq_etf,**kw)
    e2,s2=simulate(px,T,a,z,capital=cap,costs=True,tax=True,slab=slab,liq_etf=liq_etf,**kw)
    cg=lambda v:((v/cap)**(1/y)-1)*100
    rows.append(dict(period=per,strategy=nm,cash=tag,capital=cap,slab=slab,pre=cg(e0.iloc[-1]),post_cost=cg(e1.iloc[-1]),post_tax_held=cg(e2.iloc[-1]),post_tax_liquidated=cg(s2['liq_value']),
                     cost_pa_pct=s1['cost']/y/((cap+e1.iloc[-1])/2)*100, orders_yr=s1['orders']/y, tax_paid_total=s2['tax'], mdd_post_tax=perf(e2)['mdd'], end_value=s2['liq_value']))
for per in PERIODS:
    for nm in keys:
        T,kw=S[nm]
        for cap in [1e5,5e5,2e6]:
            one(nm,T,kw,per,cap,0.312)
        if nm[:2] in ('b ',"b'",'c ','d ','f1','a ','f2'):
            for slab in [0.052,0.208]: one(nm,T,kw,per,5e5,slab)
    for nm in ['b  Nifty>1.01x200DMA else cash',"b' same, signal on NIFTYBEES price"]:
        T,kw=S[nm]
        for cap in [1e5,5e5,2e6]: one(nm,T,kw,per,cap,0.312,px=PX0,liq_etf=False,tag='idle cash 0%')
R=pd.DataFrame(rows); R.to_pickle(OUT+'res5.pkl')
pd.set_option('display.width',400); pd.set_option('display.max_columns',40); pd.set_option('display.max_rows',2000)
print("BASE slab 31.2%: pre / post-cost / post-tax held / post-tax liquidated, by capital")
B=R[(R.slab==0.312)]
for per in PERIODS:
    print('\n=====',per)
    x=B[B.period==per].pivot_table(index=['strategy','cash'],columns='capital',values=['pre','post_cost','post_tax_held','post_tax_liquidated','orders_yr','mdd_post_tax'],sort=False)
    x=x[[('pre',5e5),('post_cost',1e5),('post_cost',5e5),('post_cost',2e6),('post_tax_held',1e5),('post_tax_held',5e5),('post_tax_held',2e6),('post_tax_liquidated',1e5),('post_tax_liquidated',5e5),('post_tax_liquidated',2e6),('orders_yr',5e5),('mdd_post_tax',5e5)]]
    print(x.round(2).to_string())
print("\nSLAB sensitivity at Rs 5 lakh: post-tax liquidated CAGR")
x=R[(R.capital==5e5)&(R.cash=='liquid ETF 6%')].pivot_table(index=['period','strategy'],columns='slab',values='post_tax_liquidated',sort=False).dropna()
print(x.round(2).to_string())
