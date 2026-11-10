import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/verify_nav/scripts')
from core import *
from navlib import load
G=S([105085,115744,140088],'GOLDBEES'); N=S([101325,115728,140084],'NIFTYBEES'); U=S([100822],'UTI N50 Reg-G'); J=S([101621,115729,140085],'JUNIORBEES'); I=S([112957],'ICICI NN50 Reg-G'); M=S([146271],'MID150BEES')
print('SPLITS'); 
for x in SPLITLOG: print('  %s: %s %.4f -> %s %.4f ratio %.4f treated as x%g'%x)
# raw NAVs around Dec 2019
for c,nm in ((140084,'NIFTYBEES'),(140088,'GOLDBEES'),(140085,'JUNIORBEES')):
    m,s,b=load(c); print(nm,[(str(d),v) for d,v in s if D(2019,12,16)<=d<=D(2019,12,24)])
def daily(s):
    return {s.d[i]:(s.v[i]/s.v[i-1]-1,s.d[i-1]) for i in range(1,len(s.d))}
def cmp(a,b,th=0.004):
    da=daily(a); db=daily(b); out=[]
    for d in sorted(da):
        if d in db and da[d][1]==db[d][1]:
            x=da[d][0]-db[d][0]
            if abs(x)>th: out.append((d,da[d][0],db[d][0],x))
    return out
print('NIFTYBEES vs UTI N50 daily diff >0.4%')
for d,x,y,z in cmp(N,U): print('  %s BeES %.2f%% UTI %.2f%% diff %.2f%%'%(d,100*x,100*y,100*z))
print('JUNIORBEES vs ICICI NN50 daily diff >0.4%')
for d,x,y,z in cmp(J,I): print('  %s JBeES %.2f%% ICICI %.2f%% diff %.2f%%'%(d,100*x,100*y,100*z))
print('big daily moves (>12%) in any series')
for s in (G,N,U,J,I,M):
    for d,(r,p) in daily(s).items():
        if abs(r)>0.12: print('  ',s.name,p,'->',d,'%.2f%%'%(100*r))
print('stitch boundaries')
for s in (G,N,J):
    for d in (D(2011,8,18),D(2011,8,22),D(2016,11,3),D(2016,11,7)): print('  ',s.name,s.at(d,0))
