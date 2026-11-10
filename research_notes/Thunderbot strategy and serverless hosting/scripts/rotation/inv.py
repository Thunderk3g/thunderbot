import pandas as pd, numpy as np
W='/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/work/'
C=pd.read_pickle(W+'close.pkl'); T=pd.read_pickle(W+'turn.pkl'); I=pd.read_pickle(W+'idx.pkl'); M=pd.read_pickle(W+'master.pkl')
print(C.shape, C.index.min(), C.index.max()); print(I.shape, I.index.min(), I.index.max())
print(M.columns.tolist()); print(M.head(3).to_string())
import re
cols=list(I.columns)
for pat in ['nifty_50','next','junior','midcap','200','rate','liquid','gsec','g_sec','gilt','tri','total','bond','money','1d','gold','silver']:
    print(pat, [c for c in cols if pat in c][:60])
