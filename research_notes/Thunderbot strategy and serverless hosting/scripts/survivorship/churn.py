import pandas as pd, re, sys
p='/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/dl/rishabhjain0295-web_nifty500-momentum-backtest/repo/data/IndexInclExcl.xls'
x=pd.ExcelFile(p)
def load(sn):
    df=x.parse(sn); df.columns=['idx','date','name','desc']
    df['date']=pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    df['name']=df['name'].astype(str).str.strip().str.replace(r'\s+',' ',regex=True)
    df['key']=df['name'].str.lower().str.replace(r'\s*-\s*merged.*$','',regex=True).str.replace(r'[^a-z0-9]','',regex=True).str.replace(r'(limited|ltd)$','',regex=True)
    df['incl']=df['desc'].str.lower().str.contains('inclusion')
    return df.dropna(subset=['date']).sort_values('date', kind='stable').reset_index(drop=True)
def status_at(df, d):
    """names with events: member status at date d (True/False)"""
    out={}
    for k,g in df.groupby('key', sort=False):
        before=g[g.date<=d]
        if len(before): out[k]=bool(before.iloc[-1].incl)
        else: out[k]=not bool(g.iloc[0].incl)   # status before first event
    return out
for sn,size in [('Nifty 50',50),('Nifty Next 50',50),('Nifty 100',100),('Nifty 200',200),('Nifty 500',500)]:
    df=load(sn)
    print(f"\n===== {sn}: events {len(df)}, {df.date.min().date()} -> {df.date.max().date()}; inclusions {df.incl.sum()}, exclusions {(~df.incl).sum()}")
    ex=df[~df.incl].groupby(df.date.dt.year).size()
    print(" exclusions/yr:", dict(ex))
    end=df.date.max()
    for d0 in ['2005-04-01','2008-01-01','2011-01-01','2015-01-01']:
        d0=pd.Timestamp(d0)
        if d0<df.date.min(): continue
        s0=status_at(df,d0); s1=status_at(df,end)
        leavers=[k for k in s0 if s0[k] and not s1[k]]
        yrs=(end-d0).days/365.25
        ex_n=((~df.incl)&(df.date>d0)).sum()
        print(f" cohort {d0.date()} -> {end.date()} ({yrs:.1f}y): members-with-events at start {sum(s0.values())}; left by end {len(leavers)} of {size} = {100*len(leavers)/size:.0f}% ; exclusion events in window {ex_n} ({ex_n/yrs/size*100:.1f}% of index per yr)")
# notable blow-ups
pat=re.compile(r'dewan|yes bank|reliance capital|reliance communic|unitech|suzlon|jaiprakash assoc|videocon|satyam|kingfisher|lanco|gtl|reliance infra|reliance power|jet air|housing development & infra|il&fs|infrastructure leasing|pc jeweller|vakrangee|amtek|bhushan steel|educomp|deccan chron|punj lloyd|ivrcl|gitanjali|cox|zee ent|indiabulls housing|future retail|srei|idea cell|vodafone idea|jaypee|global trust|pentamedia|dsq|himachal futur|ranbaxy|patni', re.I)
rows=[]
for sn in ['Nifty 50','Nifty 100','Nifty 200','Nifty 500']:
    df=load(sn); m=df[df.name.str.contains(pat)]
    for _,r in m.iterrows(): rows.append((r['name'],sn,r.date.date(),'IN' if r.incl else 'OUT'))
o=pd.DataFrame(rows,columns=['name','index','date','act']).sort_values(['name','date'])
print("\nNOTABLE NAMES events:"); print(o.to_string(index=False)[:9000])
