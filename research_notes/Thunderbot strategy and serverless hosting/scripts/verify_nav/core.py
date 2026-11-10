import sys, bisect, datetime as dt, math
sys.path.insert(0,'/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/verify_nav/scripts')
from navlib import load
D=dt.date
SPLITLOG=[]
def near_pow10(r):
    for k in (-2,-1,1,2):
        t=10.0**k
        if abs(r/t-1)<0.04: return t
    return None
def build(codes, name):
    """stitch codes (oldest first), then back-adjust power-of-ten unit changes so the series is on today's unit basis"""
    s=[]
    for c in codes:
        m,x,bad=load(c)
        if s: x=[r for r in x if r[0]>s[-1][0]]
        s+=x
    out=list(s); 
    # walk backwards applying factors
    factor=1.0; adj=[None]*len(s)
    adj[-1]=s[-1][1]
    for i in range(len(s)-1,0,-1):
        r=s[i][1]/s[i-1][1]
        t=near_pow10(r)
        if t is not None:
            SPLITLOG.append((name,s[i-1][0],s[i-1][1],s[i][0],s[i][1],r,t))
            factor*=t
        adj[i-1]=s[i-1][1]*factor
    return [(s[i][0],adj[i]) for i in range(len(s))]
class S:
    def __init__(self,codes,name):
        self.name=name; self.codes=codes
        self.s=build(codes,name); self.d=[x[0] for x in self.s]; self.v=[x[1] for x in self.s]
        self.first=self.d[0]; self.last=self.d[-1]
    def at(self,date,maxlag=7):
        i=bisect.bisect_right(self.d,date)-1
        if i<0: return None
        if (date-self.d[i]).days>maxlag: return None
        return self.d[i],self.v[i]
    def ret(self,d0,d1,maxlag=7):
        a=self.at(d0,maxlag); b=self.at(d1,maxlag)
        if not a or not b: return None
        return b[1]/a[1]-1
    def cagr(self,d0,d1,maxlag=7):
        a=self.at(d0,maxlag); b=self.at(d1,maxlag)
        if not a or not b: return None
        yrs=(b[0]-a[0]).days/365.25
        return (b[1]/a[1])**(1/yrs)-1
    def mdd(self,d0,d1,maxlag=7):
        a=self.at(d0,maxlag)
        if not a: return None
        i0=self.d.index(a[0]); i1=bisect.bisect_right(self.d,d1)
        pk=-1; pkd=None; best=(0,None,None)
        for i in range(i0,i1):
            v=self.v[i]
            if v>pk: pk=v; pkd=self.d[i]
            dd=v/pk-1
            if dd<best[0]: best=(dd,pkd,self.d[i])
        return best
    def yr(self,y,end=None):
        d0=D(y-1,12,31); d1=end or D(y,12,31)
        return self.ret(d0,d1)
def pct(x,n=1):
    return '—' if x is None else (('%.'+str(n)+'f')%(100*x)).replace('-','−')
