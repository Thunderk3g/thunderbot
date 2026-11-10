import pandas as pd
p='/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/dl/BKKB20_nse-index-history/repo/NSE_INDEX_HISTORY_FINAL_V3.xlsx'
f=pd.read_excel(p, sheet_name='FLAT_LIST'); f['Effective_Date']=pd.to_datetime(f['Effective_Date'])
s=pd.read_excel(p, sheet_name='SUMMARY'); print(s.head(8).to_string())
for idx in ['NIFTY 50','NIFTY 100','NIFTY 500']:
    g=f[f.Index==idx].groupby('Effective_Date').Symbol.nunique()
    print(idx, "snapshots", len(g)); print("  ", ', '.join(f"{d.date()}:{n}" for d,n in g.items()))
n=f[f.Index=='NIFTY 100']; dates=sorted(n.Effective_Date.unique())
last=set(n[n.Effective_Date==dates[-1]].Symbol)
for d in dates:
    m=set(n[n.Effective_Date==d].Symbol); print(pd.Timestamp(d).date(), len(m), "still in latest:", len(m&last))
