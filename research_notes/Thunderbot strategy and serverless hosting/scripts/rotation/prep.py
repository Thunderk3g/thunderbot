"""Build the analysis panel used by every other script in this folder. Reads only the earlier researcher's pickles."""
import pandas as pd, numpy as np, json
S='/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/'
W=S+'work/'; OUT=S+'rotation/'
C=pd.read_pickle(W+'close.pkl'); T=pd.read_pickle(W+'turn.pkl'); I=pd.read_pickle(W+'idx.pkl'); M=pd.read_pickle(W+'master.pkl')
days=C.index
# ---- Nifty 50 index (price): Yahoo-style file before 2012-02-21, NSE daily index file after
y=pd.read_csv(S+'dl/rishabhjain0295-web_nifty500-momentum-backtest/repo/data/index/NIFTY50.csv')
y=pd.Series(pd.to_numeric(y['Close'],errors='coerce').values,index=pd.to_datetime(y['Date'])).dropna(); y=y[~y.index.duplicated()].sort_index()
n50i=pd.concat([y[:'2012-02-20'], I['nifty_50'].dropna()]); n50i_full=pd.concat([n50i, y['2026-10-27':]])
n50i_full.to_pickle(OUT+'n50_index_to_nov.pkl')
n50i=n50i.reindex(days).ffill()
def chain(parts):
    """parts: list of (series, start) ordered; chain-link daily returns into one level series ending at last series' level"""
    r=pd.Series(np.nan,index=days)
    for k,(s,a) in enumerate(parts):
        s=s.reindex(days).ffill(); rr=s.pct_change(fill_method=None)
        z=parts[k+1][1] if k+1<len(parts) else None
        m=(days>pd.Timestamp(a)) if z is None else ((days>pd.Timestamp(a))&(days<=pd.Timestamp(z)))
        r[m]=rr[m]
    first=r.first_valid_index(); lv=(1+r.fillna(0)).cumprod(); lv[days<first]=np.nan
    i0=days.get_loc(first)-1; lv.iloc[i0]=1.0
    return lv
nn_i=I['nifty_next_50'].dropna(); mid100=pd.concat([I['cnx_midcap'].dropna(),I['nifty_free_float_midcap_100'].dropna(),I['nifty_midcap_100'].dropna()]); mid100=mid100[~mid100.index.duplicated()].sort_index()
mid150=I['nifty_midcap_150'].dropna()
# synthetic midcap proxy (only used before 2011-02-04): ranks 101-250 by 126-day median turnover, sqrt-turnover weights, monthly reconstitution
eq=[k for k in M[M['isin'].fillna('').str.startswith('INE')].key if k in C.columns]
Ce=C[eq]; R=Ce.pct_change(fill_method=None); R=R.where(R.abs()<0.6,0.0)
med=T[eq].rolling(126,min_periods=60).median()
me=days.to_series().groupby([days.year,days.month]).last().values
wd=pd.DataFrame(0.0,index=me,columns=eq)
for d in me:
    if d>pd.Timestamp('2012-06-30'): break
    r=med.loc[d].dropna().sort_values(ascending=False); sel=r.index[100:250]
    if len(sel): x=np.sqrt(r[sel]); wd.loc[d,sel]=(x/x.sum()).values
syn_r=(wd.reindex(days).ffill().shift(1).fillna(0)*R.fillna(0)).sum(axis=1); syn=(1+syn_r).cumprod()
P=pd.DataFrame(index=days)
P['N50']=C['NIFTYBEES'].ffill(); P['NN50']=C['JUNIORBEES'].ffill(); P['GOLD']=C['GOLDBEES'].ffill()
# midcap traded leg: synthetic -> MOM100 ETF (4 Feb 2011) -> Midcap 100 index PR (21 Feb 2012) -> Midcap 150 index PR (1 Apr 2016)
P['MID']=chain([(syn,'2005-06-30'),(C['MOM100'],'2011-02-04'),(mid100,'2012-02-21'),(mid150,'2016-04-01')])
P['MID_ETF']=chain([(syn,'2005-06-30'),(C['MOM100'],'2011-02-04'),(mid100,'2012-02-21'),(mid150,'2016-04-01'),(C['MID150BEES'],'2019-02-04')])
SG=pd.DataFrame(index=days)   # signal series
SG['N50']=n50i; SG['NN50']=chain([(C['JUNIORBEES'],'2005-01-03'),(nn_i,'2012-02-21')]); SG['MID']=P['MID']; SG['GOLD']=P['GOLD']
# cash legs
cal=np.array([(d-days[0]).days for d in days])
cash0=pd.Series(1.0,index=days); cash6=pd.Series(1.06**(cal/365.0),index=days)
r1d=I['nifty_1d_rate_index'].dropna().reindex(days).ffill(); a=r1d.first_valid_index()
rr=cash6.pct_change().fillna(0); rr[days>a]=r1d.pct_change(fill_method=None)[days>a]; cashA=(1+rr).cumprod()
CASH=pd.DataFrame({'c0':cash0,'c6':cash6,'cA':cashA})
RAW=pd.DataFrame({'n50_idx':n50i,'nn50_idx':nn_i.reindex(days).ffill(),'mid100_idx':mid100.reindex(days).ffill(),'mid150_idx':mid150.reindex(days).ffill(),
                  'mom30_idx':I['nifty200_momentum_30'].reindex(days).ffill(),'n200_idx':I['nifty_200'].reindex(days).ffill(),'rate1d_idx':I['nifty_1d_rate_index'].reindex(days).ffill(),'syn_mid':syn})
pd.to_pickle({'P':P,'SG':SG,'CASH':CASH,'RAW':RAW},OUT+'panel.pkl')
print(P.dropna().index[0], P.index[-1]); print(P.loc[['2007-12-31','2011-02-04','2012-02-21','2016-04-01','2019-02-04','2026-10-26']])
print('1D rate index first date', a, 'CAGR since', (r1d.iloc[-1]/r1d.dropna().iloc[0])**(365.25/(days[-1]-a).days)-1)
