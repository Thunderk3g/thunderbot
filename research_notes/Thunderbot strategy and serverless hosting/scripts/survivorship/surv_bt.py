import pandas as pd, numpy as np, sys
W='/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/work/'
C=pd.read_pickle(W+'close.pkl').astype('float64'); T=pd.read_pickle(W+'turn.pkl').astype('float64'); I=pd.read_pickle(W+'idx.pkl')
dates=C.index
last_valid=C.apply(lambda s: s.last_valid_index()); first_valid=C.apply(lambda s: s.first_valid_index())
Cf=C.ffill()                      # after delisting: frozen at last price (0 return)
R=Cf.pct_change()
big=(R>0.60); print("daily adj returns > +60% set to 0:", int(big.sum().sum())); R=R.mask(big,0.0)
R=R.fillna(0.0)
logr=np.log(C/C.shift(1)); logr=logr.mask(logr.abs()>0.6)
vol=logr.rolling(252,min_periods=200).std()*np.sqrt(252)
cnt=C.rolling(280,min_periods=1).count()
medturn=T.rolling(126,min_periods=100).median()
cur100=pd.read_csv('/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/dl/rishabhjain0295-web_nifty500-momentum-backtest/repo/data/universes/nifty100.csv')
print("current nifty100 file cols", cur100.columns.tolist(), len(cur100))
symcol=[c for c in cur100.columns if 'symbol' in c.lower()][0]
M=pd.read_pickle(W+'master.pkl'); alias={}
for _,r in M.iterrows():
    alias[r.symbol]=r.key
    for p in str(r.previous_symbols or '').replace(';',',').split(','):
        if p.strip(): alias.setdefault(p.strip(), r.key)
cur_keys=[alias.get(s,s) for s in cur100[symcol]]; miss=[k for k in cur_keys if k not in C.columns]; print("current N100 not in data:", miss)
cur_keys=[k for k in cur_keys if k in C.columns]
qe=[d for i,d in enumerate(dates[:-1]) if d.month in (3,6,9,12) and dates[i+1].month!=d.month]
def elig(t):
    ok=(cnt.loc[t]>=250)&C.loc[t].notna()&vol.loc[t].notna()
    return ok
def uni_pit(t,n):
    ok=elig(t); mt=medturn.loc[t][ok].dropna(); return list(mt.nlargest(n).index)
end_uni={n:uni_pit(dates[-1],n) for n in (100,200)}
def uni_end(t,n): 
    ok=elig(t); return [k for k in end_uni[n] if ok.get(k,False)]
def uni_cur(t,n):
    ok=elig(t); return [k for k in cur_keys if ok.get(k,False)]
def score(t,u,skip=0):
    i=dates.get_loc(t); p0=Cf.iloc[i-skip][u]; r6=p0/Cf.iloc[i-126][u]-1; r12=p0/Cf.iloc[i-252][u]-1; v=vol.loc[t][u]
    m6=r6/v; m12=r12/v; z=lambda x:(x-x.mean())/x.std()
    return (z(m6)+z(m12)).dropna().sort_values(ascending=False)
def run(unif,n,k=15,keep=None,mode='mom',start='2006-03-31',lag=1,skip=0):
    rb=[d for d in qe if d>=pd.Timestamp(start)]
    ret=pd.Series(0.0,index=dates); hold=[]; tos=[]; nuni=[]
    w=pd.Series(dtype=float)
    for j,t in enumerate(rb):
        u=unif(t,n); nuni.append(len(u))
        if mode=='ew': new=u
        else:
            sc=score(t,u,skip); rank={s:i+1 for i,s in enumerate(sc.index)}
            if keep:
                kept=[s for s in hold if rank.get(s,9999)<=keep]; new=kept+[s for s in sc.index if s not in kept][:max(0,k-len(kept))]
            else: new=list(sc.index[:k])
        i0=dates.get_loc(t)+lag; i1=(dates.get_loc(rb[j+1])+lag) if j+1<len(rb) else len(dates)-1
        if i0>=len(dates)-1: break
        seg=R.iloc[i0+1:i1+1][new]; g=(1+seg).cumprod()
        pv=g.mean(axis=1); pr=pv.pct_change(); pr.iloc[0]=pv.iloc[0]-1
        ret.iloc[i0+1:i1+1]=pr.values
        wn=pd.Series(1/len(new),index=new)
        if len(w): 
            allk=wn.index.union(w.index); tos.append(0.5*(wn.reindex(allk,fill_value=0)-w.reindex(allk,fill_value=0)).abs().sum())
        w=(g.iloc[-1]/g.iloc[-1].sum()); hold=new
    return ret, np.mean(tos)*4 if tos else np.nan, np.mean(nuni)
def st(r,a,b):
    x=r[a:b]; eq=(1+x).cumprod(); yrs=(x.index[-1]-x.index[0]).days/365.25
    dd=eq/eq.cummax()-1
    return (eq.iloc[-1]**(1/yrs)-1)*100, x.std()*np.sqrt(252)*100, dd.min()*100, dd.idxmin().date()
res={}
cfg=[('PIT liquid-100',uni_pit,100),('End-date liquid-100 applied backwards',uni_end,100),('Current Nifty 100 list applied backwards',uni_cur,100),('PIT liquid-200',uni_pit,200),('End-date liquid-200 applied backwards',uni_end,200)]
print(f"\n{'universe':42s} {'strategy':18s} | 2011-01..2026-10: CAGR vol maxDD | 2006-04..2026-10: CAGR vol maxDD | 2006-04..2010-12 CAGR | turnover/yr | avg universe n")
for name,uf,n in cfg:
    for sname,kw in [('EW universe',dict(mode='ew')),('Mom top15',dict(k=15)),('Mom top15 keep25',dict(k=15,keep=25)),('Mom top30 keep45',dict(k=30,keep=45))]:
        r,to,nu=run(uf,n,**kw); res[(name,sname)]=r
        a=st(r,'2011-01-01','2026-10-26'); b=st(r,'2006-04-03','2026-10-26'); c=st(r,'2006-04-03','2010-12-31')
        print(f"{name:42s} {sname:18s} | {a[0]:5.1f} {a[1]:5.1f} {a[2]:6.1f} ({a[3]}) | {b[0]:5.1f} {b[1]:5.1f} {b[2]:6.1f} ({b[3]}) | {c[0]:5.1f} | {to*100:5.0f}% | {nu:5.0f}")
pd.DataFrame({f"{a}|{b}":v for (a,b),v in res.items()}).to_pickle(W+'bt_returns.pkl')
# validation vs official indices (price) 2012-03..2026-10
for k in ['nifty_100','nifty100_equal_weight','nifty_200','nifty_50']:
    if k in I:
        s=I[k].dropna()['2012-03-01':]; yrs=(s.index[-1]-s.index[0]).days/365.25; print(f"official {k}: PR CAGR {((s.iloc[-1]/s.iloc[0])**(1/yrs)-1)*100:.1f}% from {s.index[0].date()}")
for key in [('PIT liquid-100','EW universe'),('Current Nifty 100 list applied backwards','EW universe'),('End-date liquid-100 applied backwards','EW universe')]:
    print(key, "CAGR 2012-03..2026-10: %.1f%%"%st(res[key],'2012-03-01','2026-10-26')[0])
# what PIT universe overlap with current list at various dates
for d in ['2006-03-31','2010-12-31','2015-12-31','2020-12-31','2026-09-30']:
    t=[x for x in qe if x<=pd.Timestamp(d)][-1]; u=set(uni_pit(t,100)); print(t.date(), "PIT liquid-100 ∩ current Nifty100 list:", len(u&set(cur_keys)), "| ∩ end-date liquid-100:", len(u&set(end_uni[100])), "| inactive later:", sum(M.set_index('key').status.reindex(list(u))=='inactive'))
