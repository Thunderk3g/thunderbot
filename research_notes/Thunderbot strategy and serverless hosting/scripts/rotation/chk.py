import pandas as pd, numpy as np, json
W='/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/work/'
C=pd.read_pickle(W+'close.pkl'); I=pd.read_pickle(W+'idx.pkl')
pd.set_option('display.width',250)
def big(e,ix,thr=0.03,a='2012-03-01'):
    x=pd.DataFrame({'etf':C[e].ffill().pct_change(),'idx':I[ix].pct_change()})[a:].dropna(); x['d']=x.etf-x.idx
    b=x[x.d.abs()>thr]; print(e,ix,'days with |diff|>',thr,':',len(b)); print((b*100).round(1).head(40).to_string())
big('NIFTYBEES','nifty_50'); big('JUNIORBEES','nifty_next_50',0.04); big('MID150BEES','nifty_midcap_150',0.04,'2019-02-05')
i=I['nifty_50'].dropna(); print('n50 idx gaps (calendar days>5):', [(a.date(),b.date()) for a,b in zip(i.index[:-1],i.index[1:]) if (b-a).days>5])
print('idx rows vs C rows since 2012-02-21:', len(i), len(C['2012-02-21':]))
miss=C['2012-02-21':].index.difference(i.index); print('dates in C not in idx:', len(miss), [d.date().isoformat() for d in miss[:40]])
for e,d in [('NIFTYBEES','2019-12'),('GOLDBEES','2019-12')]:
    print(e, C[e]['2019-12-12':'2019-12-27'].round(3).to_dict())
D='/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/rotation_dl/Indranil-Mondal_nifty-market-digest-bot/repo/data/history/'
import os
for f in sorted(os.listdir(D)):
    d=json.load(open(D+f)); s=d['series']; ks=list(s.keys()); print(f, ks[0], s[ks[0]], ks[-1], s[ks[-1]])
