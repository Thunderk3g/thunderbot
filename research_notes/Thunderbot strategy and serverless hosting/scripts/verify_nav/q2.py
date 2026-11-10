import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/verify_nav/scripts')
from core import *
import copy
G=S([105085,115744,140088],'GOLDBEES NAV'); N=S([101325,115728,140084],'NIFTYBEES NAV (raw, split-adj)'); U=S([100822],'UTI Nifty 50 Index Reg-G (100822)'); J=S([101621,115729,140085],'JUNIORBEES NAV (raw)'); I=S([112957],'ICICI Pru Nifty Next 50 Index Reg-G (112957)'); M=S([146271],'MID150BEES NAV (146271)')
UD=S([120716],'UTI Nifty 50 Index Direct-G (120716)')
def addback(s,ref,dates,name):
    t=copy.copy(s); t.name=name; v=list(s.v)
    for d in dates:
        i=s.d.index(d); r=s.v[i]/s.v[i-1]; a=ref.at(s.d[i],0)[1]/ref.at(s.d[i-1],0)[1]
        f=r/a
        print('  add-back %s %s: series %.2f%% ref %.2f%% -> implied distribution %.2f%% of NAV (about Rs %.2f per today-unit)'%(name,d,100*(r-1),100*(a-1),100*(1-f),s.v[i-1]*(1-f)))
        for k in range(i): v[k]*=f
    t.v=v; t.s=list(zip(t.d,v)); return t
NT=addback(N,U,[D(2008,9,15),D(2009,7,9),D(2012,3,12),D(2013,3,14),D(2014,3,11),D(2015,2,20)],'NIFTYBEES NAV, distributions added back')
JT=addback(J,I,[D(2014,3,11)],'JUNIORBEES NAV, 2014 distribution added back')
L=[G,N,NT,U,J,JT,I,M]
OCT=D(2026,10,26); END=D(2026,11,9)
for s in L+[UD]: print(s.name,'first',s.first,'last',s.last,'%.4f'%s.v[-1])
print('\n| Year | '+' | '.join(s.name for s in L)+' |'); print('|---|'+'---|'*len(L))
for y in range(2008,2026):
    print('| %d | '%y+' | '.join(pct(s.yr(y),1) for s in L)+' |')
print('| 2026 to 26 Oct | '+' | '.join(pct(s.ret(D(2025,12,31),OCT),1) for s in L)+' |')
print('| 2026 to 9 Nov | '+' | '.join(pct(s.ret(D(2025,12,31),END),1) for s in L)+' |')
P=(('2008-2026',D(2007,12,31)),('2011-2026',D(2010,12,31)),('2008-2018',D(2007,12,31)),('2019-2026',D(2018,12,31)))
for e,lab in ((END,'to 9 Nov 2026'),(OCT,'to 26 Oct 2026')):
    print('\nPeriod stats',lab)
    for p,d0 in P:
        d1=D(2018,12,31) if p=='2008-2018' else e
        for s in L:
            c=s.cagr(d0,d1); m=s.mdd(d0,d1)
            if c is None: continue
            print('  %s | %s | CAGR %s | MDD %s (%s -> %s)'%(p,s.name,pct(c,1),pct(m[0],1),m[1],m[2]))
print('\nMID150BEES from first NAV',M.first,'to 26 Oct: CAGR',pct(M.cagr(M.first,OCT),1),'MDD',M.mdd(M.first,OCT),' to 9 Nov',pct(M.cagr(M.first,END),1))
print('MID150BEES from 4 Feb 2019 to 26 Oct',pct(M.cagr(D(2019,2,4),OCT),1))
# gold underwater
pk=max((v,d) for d,v in G.s if D(2012,6,1)<=d<=D(2013,12,31)); rec=[d for d,v in G.s if d>pk[1] and v>=pk[0]][0]
print('Gold peak',pk,'recovered',rec,'years',(rec-pk[1]).days/365.25)
m=G.mdd(D(2012,1,1),D(2019,12,31)); print('gold mdd 2012-2019',m)
print('NIFTYBEES NAV 15 May 2025 -> 26 Oct 2026',pct(N.ret(D(2025,5,15),OCT),2),' UTI direct',pct(UD.ret(D(2025,5,15),OCT),2))
print('26 Oct -> 9 Nov 2026: NIFTYBEES',pct(N.ret(OCT,END),2),'UTI direct',pct(UD.ret(OCT,END),2),'JUNIORBEES',pct(J.ret(OCT,END),2),'MID150BEES',pct(M.ret(OCT,END),2),'GOLD',pct(G.ret(OCT,END),2))
print('26 Oct -> 6 Nov',pct(N.ret(OCT,D(2026,11,6)),2), ' 30 Sep -> 9 Nov',pct(N.ret(D(2026,9,30),END),2),' 30 Oct -> 9 Nov',pct(N.ret(D(2026,10,30),END),2))
for s in (N,J,M,G):
    print(' last NAVs',s.name,[(str(d),round(v,3)) for d,v in s.s[-12:]])
# comparison with notes table
T={'GOLDBEES NAV':[24.5,24.9,21.7,29.9,11.2,-6.4,-9.3,-7.5,12.5,2.4,6.7,22.9,27.0,-5.2,12.8,14.7,19.4,71.8,5.5],
 'NIFTYBEES NAV (raw, split-adj)':[-52.1,75.6,18.6,-24.0,26.5,7.2,31.6,-4.3,4.0,29.9,4.8,13.6,15.4,26.0,5.5,21.0,10.4,11.7,-12.2],
 'JUNIORBEES NAV (raw)':[-63.7,123.9,18.0,-31.7,47.2,5.7,43.7,7.9,7.5,45.4,-7.5,1.0,15.8,30.4,0.8,26.9,28.1,2.5,-3.6],
 'MID150BEES NAV (146271)':[None]*12+[25.6,47.3,3.7,44.1,24.2,5.7,-6.1]}
print('\nDifferences vs computed_rotation_backtests.md (NAV minus exchange-close), pp; * = >1pp')
for s in L:
    if s.name not in T: continue
    for k,y in enumerate(list(range(2008,2026))+['2026 to 26 Oct']):
        t=T[s.name][k]
        if t is None: continue
        r=s.yr(y) if isinstance(y,int) else s.ret(D(2025,12,31),OCT)
        if r is None: continue
        d=100*r-t
        print('  %s %s: NAV %.1f vs notes %.1f diff %+.1f %s'%(s.name,y,100*r,t,d,'*' if abs(d)>1.0 else ''))
# also compare the dividend-added-back series vs notes
for s,key in ((NT,'NIFTYBEES NAV (raw, split-adj)'),(JT,'JUNIORBEES NAV (raw)'),(U,'NIFTYBEES NAV (raw, split-adj)'),(I,'JUNIORBEES NAV (raw)')):
    for k,y in enumerate(list(range(2008,2026))+['2026 to 26 Oct']):
        t=T[key][k]; r=s.yr(y) if isinstance(y,int) else s.ret(D(2025,12,31),OCT)
        if r is None: continue
        d=100*r-t
        if abs(d)>1.0: print('  [%s] %s: %.1f vs notes %s %.1f diff %+.1f *'%(s.name,y,100*r,key.split()[0],t,d))
