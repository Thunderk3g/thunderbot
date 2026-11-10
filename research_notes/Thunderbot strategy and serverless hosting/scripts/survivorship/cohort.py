import pandas as pd, numpy as np, ast, re
W='/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/work/'
Rp='/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/dl/NegativeZone_nsepit/repo/src/nsepit/'
C=pd.read_pickle(W+'close.pkl').astype('float64'); M=pd.read_pickle(W+'master.pkl')
tree=ast.parse(open(Rp+'membership.py').read())
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
    for _,r in chg[chg.date>d].sort_values('date',ascending=False).iterrows(): s.discard(norm(r.included)); s.add(norm(r.excluded))
    return s
Cf=C.ffill(); st=M.set_index('key').status
for d0 in ['2006-04-03','2011-01-03','2016-01-04']:
    m=at(pd.Timestamp(d0)); rows=[]
    for n in m:
        k=alias.get(N2S[n],N2S[n]); p0=Cf.loc[:d0,k].iloc[-1]; p1=Cf[k].iloc[-1]; yrs=(C.index[-1]-pd.Timestamp(d0)).days/365.25
        rows.append((n,k,n in cur,(p1/p0)**(1/yrs)-1, st.get(k)))
    df=pd.DataFrame(rows,columns=['name','key','still','cagr','status'])
    g=df.groupby('still').cagr.agg(['count','median','mean'])
    print(f"\nNifty 50 cohort of {d0}: price-only CAGR to 2026-10-26 (delisted names frozen at last traded price)"); print((g*[1,100,100]).round(1).to_string())
    print(" leavers now inactive/delisted:", int(((~df.still)&(df.status=='inactive')).sum()), "| leavers with negative price CAGR:", int(((~df.still)&(df.cagr<0)).sum()), "| worst:", [(r.name,round(r.cagr*100,1)) for r in df.sort_values('cagr').head(8).itertuples(index=False)])
