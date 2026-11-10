import pandas as pd, numpy as np, glob, os
b='/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/dl/ancap97_NSEDATA4ME_data/repo/data/'
out='/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/work/'
sm=pd.read_parquet(b+'symbol_master.parquet')
main=sm[~sm.is_sme]
cl={}; tv={}; raw={}
for _,r in main.iterrows():
    f=b+'store/'+r.key.lower()+'.parquet'
    if not os.path.exists(f): continue
    d=pd.read_parquet(f, columns=['date','series','close','turnover','adj_factor'])
    d=d[d.series.isin(['EQ','BE','BZ'])].drop_duplicates('date').set_index('date')
    if len(d)<60: continue
    cl[r.key]=(d.close/d.adj_factor).astype('float32'); tv[r.key]=d.turnover.astype('float32')
C=pd.DataFrame(cl).sort_index(); T=pd.DataFrame(tv).sort_index()
print(C.shape, C.index.min(), C.index.max())
C.to_pickle(out+'close.pkl'); T.to_pickle(out+'turn.pkl'); main.to_pickle(out+'master.pkl')
# indices
idx={}
for f in glob.glob(b+'indices/*.parquet'):
    d=pd.read_parquet(f, columns=['date','close']).drop_duplicates('date').set_index('date').close
    idx[os.path.basename(f)[:-8]]=d
I=pd.DataFrame(idx).sort_index(); I.to_pickle(out+'idx.pkl'); print(I.shape, I.index.min(), I.index.max())
for k in ['cnx_nifty','s_p_cnx_nifty','nifty_50','cnx_100','nifty_100','cnx_200','nifty_200','cnx_500','s_p_cnx_500','nifty_500','cnx_alpha_index','nifty_alpha_50','cnx_low_volatility','nifty_low_volatility_50','nse_quality_30','nifty_quality_30','nifty100_quality_30','nifty100_low_volatility_30','nifty200_momentum_30','nifty200_quality_30','nifty50_value_20','nifty500_value_50','nifty_alpha_low_volatility_30','nifty_alpha_quality_low_volatility_30','nifty_quality_low_volatility_30','nifty_alpha_quality_value_low_volatility_30','nifty_midcap150_momentum_50','nifty200_alpha_30','nifty500_momentum_50','nifty500_multicap_momentum_quality_50']:
    if k in I: s=I[k].dropna(); print(f"{k:45s} {s.index.min().date()} -> {s.index.max().date()} n={len(s)}")
    else: print(k,'MISSING')
