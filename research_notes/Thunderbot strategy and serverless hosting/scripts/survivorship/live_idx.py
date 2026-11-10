import pandas as pd, numpy as np
W='/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/work/'
I=pd.read_pickle(W+'idx.pkl')
# sanity: fill stitched names
def ser(k): return I[k].dropna()
def stats(s):
    yrs=(s.index[-1]-s.index[0]).days/365.25; cagr=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1
    r=np.log(s).diff().dropna(); vol=r.std()*np.sqrt(252)
    dd=s/s.cummax()-1; t=dd.idxmin(); p=s[:t].idxmax()
    rec=s[t:][s[t:]>=s[p]]; rec=rec.index[0].date() if len(rec) else None
    return cagr,vol,dd.min(),p.date(),t.date(),rec
def rel_under(s,b):
    """longest stretch (calendar days) the ratio s/b stayed below a prior high; and whether still underwater"""
    x=(s/b).dropna(); peak=x.cummax(); under=x<peak*0.999999
    best=(0,None,None); start=None
    for d,u in under.items():
        if u and start is None: start=prev
        if (not u) and start is not None:
            L=(d-start).days
            if L>best[0]: best=(L,start,d)
            start=None
        prev=d
    ongoing=None
    if start is not None:
        L=(x.index[-1]-start).days; ongoing=(L,start)
        if L>best[0]: best=(L,start,None)
    rdd=(x/peak-1); return best, ongoing, rdd.min(), rdd.idxmin().date(), x.iloc[-1]/x.iloc[0]
pairs=[('nifty200_momentum_30','nifty_200'),('nifty_alpha_50','nifty_500'),('nifty_alpha_50','nifty_50'),('nifty_low_volatility_50','nifty_500'),('nifty100_low_volatility_30','nifty_100'),
       ('nifty100_quality_30','nifty_100'),('nifty200_quality_30','nifty_200'),('nifty50_value_20','nifty_50'),('nifty500_value_50','nifty_500'),
       ('nifty_alpha_low_volatility_30','nifty_200'),('nifty_alpha_quality_low_volatility_30','nifty_200'),('nifty_quality_low_volatility_30','nifty_200'),('nifty_alpha_quality_value_low_volatility_30','nifty_200'),
       ('nifty_midcap150_momentum_50','nifty_midcap_150'),('nifty200_alpha_30','nifty_200')]
# stitch quality 30
q=pd.concat([I['nse_quality_30'].dropna(), I['nifty_quality_30'].dropna(), I['nifty100_quality_30'].dropna()]); q=q[~q.index.duplicated()].sort_index(); I['nifty100_quality_30']=q
print("PRICE-RETURN indices, live since launch; end", I.index.max().date())
print(f"{'index':44s} {'start':10s} | CAGR   vol   maxDD (peak->trough, recovered) || bench CAGR vol maxDD || excess | longest rel. underwater (days, from->to) | max rel DD (date)")
for a,bn in pairs:
    if a not in I or bn not in I: print(a,bn,'missing'); continue
    s=ser(a); b=I[bn].dropna(); idx=s.index.intersection(b.index); s=s[idx]; b=b[idx]
    c,v,d,p,t,rec=stats(s); cb,vb,db,pb,tb,recb=stats(b)
    best,ong,rdd,rddt,relw=rel_under(s,b)
    print(f"{a:44s} {s.index[0].date()} | {c*100:5.1f} {v*100:5.1f} {d*100:6.1f} ({p}->{t}, rec {rec}) || {bn:10s} {cb*100:5.1f} {vb*100:5.1f} {db*100:6.1f} ({pb}->{tb}) || {100*(c-cb):+5.1f} | {best[0]/365.25:4.1f}y {best[1].date() if best[1] is not None else None}->{best[2].date() if best[2] is not None else 'ONGOING'} ; ongoing {round(ong[0]/365.25,1) if ong else 0}y | {rdd*100:5.1f}% ({rddt})")
# COVID drawdowns Jan-Mar 2020 and Sep2024-2025
print("\nDrawdown windows (price index):")
for k in ['nifty_50','nifty_100','nifty_200','nifty_500','nifty_alpha_50','nifty100_low_volatility_30','nifty200_quality_30','nifty50_value_20','nifty500_value_50','nifty_alpha_low_volatility_30','nifty200_momentum_30','nifty_low_volatility_50']:
    s=ser(k); out=[]
    for a,b in [('2020-01-01','2020-04-30'),('2021-10-01','2022-07-31'),('2024-06-01','2025-06-30'),('2025-07-01','2026-10-26')]:
        w=s[a:b]
        if len(w)<20: out.append('   n/a'); continue
        dd=(w/w.cummax()-1); out.append(f"{dd.min()*100:6.1f}% ({w[:dd.idxmin()].idxmax().date()}->{dd.idxmin().date()})")
    print(f"{k:32s} covid {out[0]} | 2021-22 {out[1]} | 2024-25 {out[2]} | 2025-26 {out[3]}")
# calendar-year PR returns
yr=I[['nifty_50','nifty_200','nifty_500','nifty200_momentum_30','nifty_alpha_50','nifty100_low_volatility_30','nifty200_quality_30','nifty500_value_50','nifty_alpha_low_volatility_30']].resample('YE').last().pct_change()*100
print(yr.round(1).to_string())
print("YTD 2026 to", I.index.max().date())
