import pandas as pd, numpy as np
W='/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/work/'
C=pd.read_pickle(W+'close.pkl'); T=pd.read_pickle(W+'turn.pkl'); I=pd.read_pickle(W+'idx.pkl'); M=pd.read_pickle(W+'master.pkl')
eq=M[M['isin'].fillna('').str.startswith('INE')].key
eq=[k for k in eq if k in C.columns]
Ce=C[eq]; Te=T[eq]
R=Ce.pct_change(fill_method=None); R=R.where(R.abs()<0.6, 0.0)
med=Te.rolling(126,min_periods=60).median()
me=Ce.index.to_series().groupby([Ce.index.year,Ce.index.month]).last().values
def build(lo,hi,weight):
    out=pd.Series(0.0,index=Ce.index); w=None
    med_me=med.loc[me]
    wd=pd.DataFrame(0.0,index=me,columns=eq)
    for d in me:
        r=med_me.loc[d].dropna().sort_values(ascending=False)
        sel=r.index[lo:hi]
        if len(sel)==0: continue
        if weight=='ew': wd.loc[d,sel]=1/len(sel)
        else:
            x=np.sqrt(r[sel]); wd.loc[d,sel]=(x/x.sum()).values
    wdaily=wd.reindex(Ce.index).ffill().shift(1).fillna(0)
    return (wdaily*R.fillna(0)).sum(axis=1)
mid=pd.concat([I['cnx_midcap'].dropna(), I['nifty_free_float_midcap_100'].dropna(), I['nifty_midcap_100'].dropna()]); mid=mid[~mid.index.duplicated()].sort_index()
print('mid100 stitched', mid.index.min(), mid.index.max(), len(mid), 'max abs daily', mid.pct_change().abs().max())
m150=I['nifty_midcap_150'].dropna()
jb=C['JUNIORBEES'].ffill(); nn=I['nifty_next_50'].dropna()
def cmp(p, b, a, z, name):
    pr=p[a:z]; br=b.pct_change()[a:z].dropna(); pr=pr.reindex(br.index)
    yrs=(br.index[-1]-br.index[0]).days/365.25
    cp=((1+pr).prod())**(1/yrs)-1; cb=((1+br).prod())**(1/yrs)-1
    mp=(1+pr).resample('ME').prod()-1; mb=(1+br).resample('ME').prod()-1
    te=(pr-br).std()*np.sqrt(252)
    print(f"{name:34s} {a}..{z} proxy CAGR {cp*100:5.1f} bench {cb*100:5.1f} | daily corr {pr.corr(br):.3f} monthly corr {mp.corr(mb):.3f} TE {te*100:.1f}% | vol {pr.std()*np.sqrt(252)*100:.1f} vs {br.std()*np.sqrt(252)*100:.1f}")
for lo,hi,w in [(100,250,'ew'),(100,250,'sq'),(80,200,'sq'),(50,200,'sq'),(100,200,'sq'),(50,150,'sq')]:
    p=build(lo,hi,w)
    cmp(p,mid,'2012-03-01','2016-03-31',f'turn-rank {lo}-{hi} {w} vs Mid100')
    cmp(p,mid,'2016-04-01','2026-10-26',f'turn-rank {lo}-{hi} {w} vs Mid100')
    cmp(p,m150,'2016-04-04','2026-10-26',f'turn-rank {lo}-{hi} {w} vs Mid150')
# Next50 (JUNIORBEES) as midcap proxy?
cmp(jb.pct_change(),mid,'2012-03-01','2016-03-31','JUNIORBEES vs Mid100')
cmp(jb.pct_change(),m150,'2016-04-04','2026-10-26','JUNIORBEES vs Mid150')
cmp(C['MOM100'].ffill().pct_change(),mid,'2012-03-01','2016-03-31','MOM100 ETF vs Mid100')
cmp(C['MOM100'].ffill().pct_change(),mid,'2016-04-01','2026-10-26','MOM100 ETF vs Mid100')
cmp(C['MID150BEES'].ffill().pct_change(),m150,'2019-03-01','2026-10-26','MID150BEES vs Mid150')
for y in range(2019,2027):
    cmp(C['MID150BEES'].ffill().pct_change(),m150,f'{y}-01-01' if y>2019 else '2019-02-05',f'{y}-12-31',f'MID150BEES vs Mid150 {y}')
cmp(mid.pct_change(),m150,'2016-04-04','2026-10-26','Mid100 vs Mid150')
cmp(jb.pct_change(),nn,'2012-03-01','2026-10-26','JUNIORBEES vs Next50 idx')
cmp(C['NIFTYBEES'].ffill().pct_change(),I['nifty_50'].dropna(),'2012-03-01','2026-10-26','NIFTYBEES vs Nifty50 idx')
print('missing days JUNIORBEES by year', C['JUNIORBEES'].isna().groupby(C.index.year).sum().to_dict())
print('missing days GOLDBEES by year', C['GOLDBEES']['2007-03-19':].isna().groupby(C['2007-03-19':].index.year).sum().to_dict())
print('missing days MID150BEES by year', C['MID150BEES']['2019-02-04':].isna().groupby(C['2019-02-04':].index.year).sum().to_dict())
print('missing NIFTYBEES', C['NIFTYBEES'].isna().sum())
