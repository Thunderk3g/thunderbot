import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/verify_nav/scripts')
from core import *
N=S([101325,115728,140084],'NIFTYBEES'); U=S([100822],'UTI N50 Reg-G'); J=S([101621,115729,140085],'JUNIORBEES'); G=S([105085,115744,140088],'GOLDBEES')
for a,b in ((D(2008,9,9),D(2008,9,19)),(D(2009,7,6),D(2009,7,13)),(D(2012,3,7),D(2012,3,14)),(D(2013,3,11),D(2013,3,18)),(D(2014,3,6),D(2014,3,13)),(D(2015,2,17),D(2015,2,24))):
    print('---')
    for i,d in enumerate(N.d):
        if a<=d<=b:
            u=U.at(d,0); j=J.at(d,0)
            print(d,'BeES %.3f (%.2f%%)'%(N.v[i],100*(N.v[i]/N.v[i-1]-1)),'UTI',u and '%.4f'%u[1],'JB',j and '%.3f'%j[1])
# yearly comparison BeES vs UTI
for y in range(2007,2017): print(y,'BeES',pct(N.yr(y),2),'UTI',pct(U.yr(y),2),'diff',pct(N.yr(y)-U.yr(y),2))
