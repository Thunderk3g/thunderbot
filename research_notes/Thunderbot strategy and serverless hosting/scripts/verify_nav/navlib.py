import json, os, datetime as dt
B='/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/verify_nav'
def load(code):
    """returns meta, list of (date, nav) ascending, dropping zero/invalid NAVs and duplicate dates"""
    j=json.load(open(f'{B}/data/mf_{code}.json'))
    rows={}
    bad=0
    for r in j.get('data',[]):
        try:
            d=dt.datetime.strptime(r['date'],'%d-%m-%Y').date(); v=float(r['nav'])
        except Exception: bad+=1; continue
        if v<=0: bad+=1; continue
        rows[d]=v
    s=sorted(rows.items())
    return j.get('meta',{}), s, bad
def jumps(s, lo=0.6, hi=1.6):
    out=[]
    for (d0,v0),(d1,v1) in zip(s,s[1:]):
        r=v1/v0
        if r<lo or r>hi: out.append((d0,v0,d1,v1,r))
    return out
