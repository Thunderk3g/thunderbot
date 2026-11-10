import ast, re, pandas as pd
R='/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/dl/NegativeZone_nsepit/repo/src/nsepit/'
src=open(R+'membership.py').read()
tree=ast.parse(src); AL={}
for n in tree.body:
    if isinstance(n,ast.Assign) and getattr(n.targets[0],'id','')=='ALIASES': AL=ast.literal_eval(n.value)
def norm(s):
    s=re.sub(r'\[.*?\]','',str(s)).strip(); return AL.get(s,s)
cons=pd.read_csv(R+'data/nifty50_constituents.csv'); chg=pd.read_csv(R+'data/nifty50_changes.csv')
chg['date']=pd.to_datetime(chg['date'], dayfirst=True); chg=chg.sort_values('date')
cur=set(cons.Company.map(norm)); print("current", len(cur), "changes", len(chg), chg.date.min().date(), chg.date.max().date())
def at(d):
    s=set(cur)
    for _,r in chg[chg.date>d].sort_values('date',ascending=False).iterrows():
        s.discard(norm(r.included)); s.add(norm(r.excluded))
    return s
today=cur
for d in ['2005-04-01','2008-01-01','2011-01-01','2015-01-01','2018-01-01','2020-07-31','2021-01-01']:
    m=at(pd.Timestamp(d)); surv=m&today
    print(f"{d}: n={len(m)}; still in Nifty 50 (snapshot ~mid-2026 incl. changes to {chg.date.max().date()}): {len(surv)} ({100*len(surv)/max(len(m),1):.0f}%); gone: {len(m-today)}")
m11=at(pd.Timestamp('2011-01-01')); m20=at(pd.Timestamp('2020-07-31'))
print("2011 cohort gone by 2020-07-31:", len(m11-m20), sorted(m11-m20))
print("2011 cohort gone by today:", sorted(m11-today))
print("changes per year:", chg.groupby(chg.date.dt.year).size().to_dict())
