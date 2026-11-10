import pandas as pd, numpy as np, ast, re
W='/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/work/'
Rp='/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/dl/NegativeZone_nsepit/repo/src/nsepit/'
C=pd.read_pickle(W+'close.pkl').astype('float64'); I=pd.read_pickle(W+'idx.pkl'); M=pd.read_pickle(W+'master.pkl')
tree=ast.parse(open(Rp+'membership.py').read()); AL={}; N2S={}
for n in tree.body:
    if isinstance(n,ast.Assign):
        nm=getattr(n.targets[0],'id','')
        if nm=='ALIASES': AL=ast.literal_eval(n.value)
        if nm=='NAME2SYM': N2S=ast.literal_eval(n.value)
norm=lambda s: AL.get(re.sub(r'\[.*?\]','',str(s)).strip(), re.sub(r'\[.*?\]','',str(s)).strip())
cons=pd.read_csv(Rp+'data/nifty50_constituents.csv'); chg=pd.read_csv(Rp+'data/nifty50_changes.csv'); chg['date']=pd.to_datetime(chg['date'],dayfirst=True)
for c in cons.itertuples(): N2S.setdefault(norm(c.Company), c.Symbol)
alias={}
for _,r in M.iterrows():
    alias[r.symbol]=r.key
    for p in str(r.previous_symbols or '').replace(';',',').replace('|',',').split(','):
        if p.strip(): alias.setdefault(p.strip(), r.key)
cur=set(cons.Company.map(norm))
def at(d):
    s=set(cur)
    for _,r in chg[chg.date>d].sort_values('date',ascending=False).iterrows():
        s.discard(norm(r.included)); s.add(norm(r.excluded))
    return s
def keys(names):
    out=[];miss=[]
    for n in names:
        s=N2S.get(n); k=alias.get(s,s) if s else None
        if k in C.columns: out.append(k)
        else: miss.append((n,s))
    return out,miss
allmiss=set()
dates=C.index; Cf=C.ffill(); R=Cf.pct_change(); R=R.mask(R>0.6,0.0).fillna(0.0)
logr=np.log(C/C.shift(1)); logr=logr.mask(logr.abs()>0.6); vol=logr.rolling(252,min_periods=200).std()*np.sqrt(252)
qe=[d for i,d in enumerate(dates[:-1]) if d.month in (3,6,9,12) and dates[i+1].month!=d.month]
curk,_=keys(cur)
def uni_pit(t):
    k,m=keys(at(t)); allmiss.update(m); return [x for x in k if pd.notna(C.loc[:t,x].iloc[-60:]).any()]
def uni_cur(t): return [x for x in curk if pd.notna(Cf.loc[t,x]) and pd.notna(vol.loc[t,x])]
def score(t,u):
    i=dates.get_loc(t); u=[x for x in u if pd.notna(vol.loc[t,x]) and pd.notna(Cf.iloc[i-252][x])]
    p0=Cf.iloc[i][u]; v=vol.loc[t][u]; m6=(p0/Cf.iloc[i-126][u]-1)/v; m12=(p0/Cf.iloc[i-252][u]-1)/v; z=lambda x:(x-x.mean())/x.std()
    return (z(m6)+z(m12)).dropna().sort_values(ascending=False)
def run(uf,mode='mom',k=10,keep=None,start='2006-03-31'):
    rb=[d for d in qe if d>=pd.Timestamp(start)]; ret=pd.Series(0.0,index=dates); hold=[]; tos=[]; w=pd.Series(dtype=float); nu=[]
    for j,t in enumerate(rb):
        u=uf(t); nu.append(len(u))
        if mode=='ew': new=u
        else:
            sc=score(t,u); rank={s:i+1 for i,s in enumerate(sc.index)}
            if keep: kept=[s for s in hold if rank.get(s,999)<=keep]; new=kept+[s for s in sc.index if s not in kept][:max(0,k-len(kept))]
            else: new=list(sc.index[:k])
        i0=dates.get_loc(t)+1; i1=(dates.get_loc(rb[j+1])+1) if j+1<len(rb) else len(dates)-1
        if i0>=len(dates)-1: break
        g=(1+R.iloc[i0+1:i1+1][new]).cumprod(); pv=g.mean(axis=1); pr=pv.pct_change(); pr.iloc[0]=pv.iloc[0]-1; ret.iloc[i0+1:i1+1]=pr.values
        wn=pd.Series(1/len(new),index=new)
        if len(w): a=wn.index.union(w.index); tos.append(0.5*(wn.reindex(a,fill_value=0)-w.reindex(a,fill_value=0)).abs().sum())
        w=g.iloc[-1]/g.iloc[-1].sum(); hold=new
    return ret, (np.mean(tos)*4 if tos else np.nan), np.mean(nu)
def st(r,a,b):
    x=r[a:b]; eq=(1+x).cumprod(); yrs=(x.index[-1]-x.index[0]).days/365.25; dd=eq/eq.cummax()-1
    return (eq.iloc[-1]**(1/yrs)-1)*100, x.std()*np.sqrt(252)*100, dd.min()*100
out={}
print(f"{'universe':30s} {'strategy':18s} | 2011-01..2026-10 CAGR vol MDD | 2006-04..2026-10 CAGR vol MDD | 2017-04..2026-10 CAGR | turn/yr | avg n")
for un,uf in [('PIT Nifty 50 (reconstructed)',uni_pit),("Today's Nifty 50 backwards",uni_cur)]:
    for sn,kw in [('EW all',dict(mode='ew')),('Mom top10',dict(k=10)),('Mom top10 keep17',dict(k=10,keep=17)),('Mom top15 keep25',dict(k=15,keep=25))]:
        r,to,n=run(uf,**kw); out[(un,sn)]=r
        a=st(r,'2011-01-01','2026-10-26'); b=st(r,'2006-04-03','2026-10-26'); c=st(r,'2017-04-13','2026-10-26')
        print(f"{un:30s} {sn:18s} | {a[0]:5.1f} {a[1]:5.1f} {a[2]:6.1f} | {b[0]:5.1f} {b[1]:5.1f} {b[2]:6.1f} | {c[0]:5.1f} | {to*100:4.0f}% | {n:4.0f}")
print("unmapped PIT names (excluded from PIT universe):", sorted(allmiss))
for k,a in [('nifty_50','2012-03-01'),('nifty50_equal_weight','2017-04-13'),('nifty_100','2012-03-01'),('nifty100_equal_weight','2013-06-10')]:
    s=I[k].dropna()[a:]; yrs=(s.index[-1]-s.index[0]).days/365.25; print(f"official {k} PR CAGR from {s.index[0].date()}: {((s.iloc[-1]/s.iloc[0])**(1/yrs)-1)*100:.1f}%")
print("PIT N50 EW 2012-03..: %.1f ; today's-list EW 2012-03..: %.1f"%(st(out[('PIT Nifty 50 (reconstructed)','EW all')],'2012-03-01','2026-10-26')[0], st(out[("Today's Nifty 50 backwards",'EW all')],'2012-03-01','2026-10-26')[0]))
# Nifty 100: today's list EW vs official EW index, same window
B=pd.read_pickle(W+'bt_returns.pkl')
for a in ['2013-06-10','2012-03-01','2011-01-03']:
    x=B['Current Nifty 100 list applied backwards|EW universe'][a:'2026-10-26']; yrs=(x.index[-1]-x.index[0]).days/365.25
    print(f"today's Nifty100 list EW (price-only, qtrly rebalanced) from {a}: {(((1+x).prod())**(1/yrs)-1)*100:.1f}%")
pd.DataFrame({f"{a}|{b}":v for (a,b),v in out.items()}).to_pickle(W+'n50_returns.pkl')
