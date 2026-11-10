import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/verify_nav/scripts')
from core import *
import pandas as pd, numpy as np
C=pd.read_pickle('/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/work/close.pkl')
X={'GOLDBEES':[105085,115744,140088],'NIFTYBEES':[101325,115728,140084],'JUNIORBEES':[101621,115729,140085],'MID150BEES':[146271],'SILVERBEES':[149758],'LIQUIDCASE':[152327],'LIQUIDADD':[152555],'GROWWLIQID':[152891],'MON100':[114984],'MOM30IETF':[150455],'ALPHA':[149397],'ALPL30IETF':[148456],'LOWVOLIETF':[141596],'SBIETFQLTY':[145648]}
print('close columns present:',[k for k in X if k in C.columns],'missing',[k for k in X if k not in C.columns])
PR={}
for k,codes in X.items():
    if k not in C.columns: continue
    s=S(codes,k); nav=pd.Series(s.v,index=pd.to_datetime(s.d)); px=C[k].dropna()
    df=pd.concat([px.rename('px'),nav.rename('nav')],axis=1).dropna(); df['prem']=df.px/df.nav-1
    PR[k]=df
    l=df['2025-10-27':'2026-10-26'].prem
    print('%-11s first px %s | all-time: n=%d median %.2f%% p5 %.2f%% p95 %.2f%% min %.2f%% (%s) max %.2f%% (%s) | last 12m: median %.2f%% p5 %.2f%% p95 %.2f%% min %.2f%% max %.2f%% (%s)'%(k,px.index[0].date(),len(df),100*df.prem.median(),100*df.prem.quantile(.05),100*df.prem.quantile(.95),100*df.prem.min(),df.prem.idxmin().date(),100*df.prem.max(),df.prem.idxmax().date(),100*l.median(),100*l.quantile(.05),100*l.quantile(.95),100*l.min(),100*l.max(),l.idxmax().date()))
print('\nYear-end close/NAV premium % (last common day of year)')
for k in ('GOLDBEES','NIFTYBEES','JUNIORBEES','MID150BEES'):
    df=PR[k]; ye=df.groupby(df.index.year).tail(1)
    print(k,' '.join('%d:%+.1f'%(d.year,100*p) for d,p in ye.prem.items()))
g=PR['GOLDBEES']; print('GOLDBEES premium monthly medians 2013-2014:',' '.join('%s:%+.1f'%(str(d)[:7],100*p) for d,p in g['2013-01':'2015-03'].prem.resample('ME').median().items()))
for d in ('2019-12-17','2019-12-18','2019-12-19','2019-12-20','2019-12-23'):
    print(d,'NIFTYBEES px/nav',PR['NIFTYBEES'].loc[d,['px','nav']].round(3).tolist() if d in PR['NIFTYBEES'].index else None,'GOLDBEES',PR['GOLDBEES'].loc[d,['px','nav']].round(4).tolist() if d in PR['GOLDBEES'].index else None)
for d in ('2020-03-23','2026-10-26'):
    print(d,{k:round(100*PR[k].prem.get(pd.Timestamp(d),np.nan),2) for k in PR})
# overnight index vs funds
P=pd.read_pickle('/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/rotation/panel.pkl'); r=P['RAW']['rate1d_idx'].dropna()
H=S([101996],'HDFC ON'); SB=S([101206],'SBI ON')
print('\n1D rate index yearly vs HDFC/SBI overnight Reg-G')
for y in range(2017,2026):
    a=r[:'%d-12-31'%(y-1)].iloc[-1]; b=r[:'%d-12-31'%y].iloc[-1]
    print(y,'index %.2f HDFC %.2f SBI %.2f'%(100*(b/a-1),100*H.yr(y),100*SB.yr(y)))
a=r[:'2025-12-31'].iloc[-1]; b=r[:'2026-10-26'].iloc[-1]; print('2026 to 26 Oct index %.2f'%(100*(b/a-1)), 'HDFC',pct(H.ret(D(2025,12,31),D(2026,10,26)),2))
