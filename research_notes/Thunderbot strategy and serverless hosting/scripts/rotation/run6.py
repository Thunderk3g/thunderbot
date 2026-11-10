"""Q6 robustness: decision day, lookback, buffer, execution lag, rebalance band. Pre-cost with cash at 6%; plus post-tax (Rs 5 lakh, 31.2% slab, liquidated)."""
import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/rotation')
from engine import *
A4=['N50','NN50','MID','GOLD']; A3=['N50','NN50','MID']
P=P0[A4]; SG=SG0[A4]; SGe=SG.copy(); SGe['N50']=P['N50']; PX=px_with_cash(P,'c6')
def build(name,mode='ME',n=200,buf=None):
    dd=decision_dates(mode)
    if name=='b':  return tgt_trend(SG,['N50'],dd,n,1.01 if buf is None else buf)
    if name=="b'": return tgt_trend(SGe,['N50'],dd,n,1.01 if buf is None else buf)
    if name=='c':  return tgt_trend(SG,A4,dd,n,1.00 if buf is None else buf)
    if name=='d':  return tgt_dual(SG,A4,dd,2,'sma',n,1.00 if buf is None else buf)
    if name=='e-c':return tgt_trend(SG,A3,dd,n,1.00 if buf is None else buf)
    if name=='e-d':return tgt_dual(SG,A3,dd,2,'sma',n,1.00 if buf is None else buf)
def run(T,per,lag=0,band=0.05,post=True):
    a,z=PERIODS[per]; e,s=simulate(PX,T,a,z,lag=lag,band=band); pf=perf(e); out=[pf['cagr'],pf['mdd']]
    if post:
        e2,s2=simulate(PX,T,a,z,capital=5e5,costs=True,tax=True,lag=lag,band=band); out.append(((s2['liq_value']/5e5)**(1/pf['years'])-1)*100)
    return out
rows=[]
names=['b',"b'",'c','d','e-c','e-d']
for nm in names:
    for per in PERIODS:
        for mode in [5,10,15,20,'ME']:
            for lag in [0,1]:
                r=run(build(nm,mode),per,lag=lag); rows.append(dict(test='day',strategy=nm,period=per,setting=f"{mode}",lag=lag,cagr=r[0],mdd=r[1],post=r[2]))
        for n in [150,200,250,'10m']:
            r=run(build(nm,'ME',n),per); rows.append(dict(test='lookback',strategy=nm,period=per,setting=str(n),lag=0,cagr=r[0],mdd=r[1],post=r[2]))
        for buf in [1.00,1.01,1.02]:
            r=run(build(nm,'ME',200,buf),per); rows.append(dict(test='buffer',strategy=nm,period=per,setting=f"{buf:.2f}",lag=0,cagr=r[0],mdd=r[1],post=r[2]))
        if nm in ('c','d','e-c','e-d'):
            for band in [0.0,0.025,0.05,0.10]:
                r=run(build(nm),per,band=band); rows.append(dict(test='band',strategy=nm,period=per,setting=f"{band}",lag=0,cagr=r[0],mdd=r[1],post=r[2]))
# full grid for dispersion: day x lookback x buffer (lag 0), pre-cost only
grid=[]
for nm in names:
    for mode in [5,10,15,20,'ME']:
        for n in [150,200,250]:
            for buf in [1.00,1.01]:
                T=build(nm,mode,n,buf)
                for per in PERIODS:
                    r=run(T,per,post=True); grid.append(dict(strategy=nm,period=per,mode=str(mode),n=n,buf=buf,cagr=r[0],mdd=r[1],post=r[2]))
R=pd.DataFrame(rows); G=pd.DataFrame(grid); pd.to_pickle({'R':R,'G':G},OUT+'res6.pkl')
pd.set_option('display.width',300); pd.set_option('display.max_rows',1000)
for test in ['day','lookback','buffer','band']:
    X=R[R.test==test]
    for val,lab in [('cagr','pre-cost CAGR'),('mdd','max DD'),('post','post-tax liquidated CAGR (5L)')]:
        if test=='day':
            for lag in [0,1]:
                print(f"\n--- {test} lag {lag}: {lab}"); print(X[X.lag==lag].pivot_table(index=['period','strategy'],columns='setting',values=val,sort=False)[['5','10','15','20','ME']].round(1).to_string())
        else:
            print(f"\n--- {test}: {lab}"); print(X.pivot_table(index=['period','strategy'],columns='setting',values=val,sort=False).round(1).to_string())
print("\n--- GRID (5 decision days x 3 lookbacks x 2 buffers = 30 specs per strategy): min / median / max")
for val in ['cagr','post','mdd']:
    g=G.groupby(['period','strategy'],sort=False)[val].agg(['min','median','max']).round(1); print(val); print(g.to_string())
# how often does c / d beat b / b' across the 30 specs (same spec for both)?
M=G.pivot_table(index=['period','mode','n','buf'],columns='strategy',values='post')
for x in ['c','d','e-c','e-d']:
    for y in ['b',"b'"]:
        d=(M[x]-M[y]); print(f"post-tax {x} minus {y} over 30 matched specs: " + '; '.join(f"{per}: min {d.loc[per].min():+.1f} med {d.loc[per].median():+.1f} max {d.loc[per].max():+.1f} wins {int((d.loc[per]>0).sum())}/30" for per in PERIODS))
M2=G.pivot_table(index=['period','mode','n','buf'],columns='strategy',values='mdd')
for x in ['c','d','e-c','e-d']:
    d=(M2[x]-M2["b"]); print(f"maxDD {x} minus b (positive = shallower) : " + '; '.join(f"{per}: min {d.loc[per].min():+.1f} med {d.loc[per].median():+.1f} max {d.loc[per].max():+.1f}" for per in PERIODS))
