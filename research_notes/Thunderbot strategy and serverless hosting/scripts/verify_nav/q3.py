import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/verify_nav/scripts')
from core import *
MD=S([148703],'UTI N200 Momentum 30 Direct-G (148703)'); MR=S([148704],'UTI N200 Momentum 30 Regular-G (148704)')
N=S([120716],'UTI Nifty 50 Direct-G (120716)'); F=S([147625],'Motilal Oswal Nifty 500 Index Direct-G (147625)')
NB=S([101325,115728,140084],'NIFTYBEES NAV')
others=[S([150738],'Tata Nifty Midcap150 Momentum 50 Index Direct-G (150738)'),S([152875],'Motilal Oswal Nifty 500 Momentum 50 Index Direct-G (152875)'),
 S([149397],'Kotak Nifty Alpha 50 ETF (149397)'),S([148456],'ICICI Pru Nifty Alpha Low-Vol 30 ETF (148456)'),S([141596],'ICICI Pru Nifty 100 Low Vol 30 ETF (141596)'),S([145648],'SBI Nifty 200 Quality 30 ETF (145648)'),
 S([150455],'ICICI Pru Nifty 200 Momentum 30 ETF (150455)'),S([146271],'MID150BEES NAV (146271)')]
print('SPLITS'); 
for x in SPLITLOG: print('  %s: %s %.4f -> %s %.4f ratio %.4f treated as x%g'%x)
END=D(2026,11,9); OCT=D(2026,10,26)
def dd24(s,lo=D(2024,6,1),hi=D(2024,12,31)):
    # peak = max NAV in window; trough = min after peak to END
    pk=max((v,d) for d,v in s.s if lo<=d<=hi and d>=s.first)
    after=[(v,d) for d,v in s.s if d>pk[1]]
    tr=min(after)
    rec=[d for d,v in s.s if d>tr[1] and v>=pk[0]]
    last=s.v[-1]/pk[0]-1
    hi2=max(after)
    return pk,tr,tr[0]/pk[0]-1,last,(rec[0] if rec else None),hi2
for s in (MD,MR):
    print('\n',s.name,'first',s.first,'%.4f'%s.v[0],'last',s.last,'%.4f'%s.v[-1])
    for lab,e in (('to 9 Nov 2026',END),('to 26 Oct 2026',OCT),('to 30 Oct 2026',D(2026,10,30)),('to 30 Jun 2026',D(2026,6,30))):
        print('   CAGR from first NAV',lab,pct(s.cagr(s.first,e),2),'| Nifty 50 direct',pct(N.cagr(s.first,e),2),'| Nifty 500 direct',pct(F.cagr(s.first,e),2),'| NIFTYBEES NAV',pct(NB.cagr(s.first,e),2), '| abs',pct(s.ret(s.first,e),2))
    # from Rs 10 on 10 Mar 2021 (allotment date per report)
    for e in (END,D(2026,10,30)):
        v=s.at(e)[1]; yrs=(e-D(2021,3,10)).days/365.25
        print('   from Rs10 on 10 Mar 2021 to',e,'NAV %.4f'%v,'CAGR %.2f%%'%(100*((v/10)**(1/yrs)-1)),'abs %.2f%%'%(100*(v/10-1)))
    print('   calendar years:',{y:pct(s.yr(y),2) for y in range(2022,2026)},'2026 to 2 Sep',pct(s.ret(D(2025,12,31),D(2026,9,2)),2),'to 30 Sep',pct(s.ret(D(2025,12,31),D(2026,9,30)),2),'to 26 Oct',pct(s.ret(D(2025,12,31),OCT),2),'to 9 Nov',pct(s.ret(D(2025,12,31),END),2))
    print('   2021 part (first NAV->31 Dec 2021)',pct(s.ret(s.first,D(2021,12,31)),2))
    pk,tr,dep,last,rec,hi2=dd24(s)
    print('   2024-25 DD: peak',pk,'trough',tr,'depth',pct(dep,2),'latest vs peak',pct(last,2),'recovered',rec,'highest since',hi2,pct(hi2[0]/pk[0]-1,2))
    print('   at 26 Oct 2026 vs peak',pct(s.at(OCT)[1]/pk[0]-1,2),' at 4 Sep 2026',pct(s.at(D(2026,9,4))[1]/pk[0]-1,2))
    print('   27 Sep 2024 -> 7 Apr 2025',pct(s.ret(D(2024,9,27),D(2025,4,7)),2),' Nifty50 direct same',pct(N.ret(D(2024,9,27),D(2025,4,7)),2),'N500',pct(F.ret(D(2024,9,27),D(2025,4,7)),2))
    print('   max DD since launch',s.mdd(s.first,END))
    for lab,e,yrs in (('1y to 15 Sep 2026',D(2026,9,15),1),('3y',D(2026,9,15),3),('5y',D(2026,9,15),5),('5y to 9 Nov 2026',END,5),('3y to 30 Oct 2026',D(2026,10,30),3),('3y to 30 Jun 2026',D(2026,6,30),3),('5y to 30 Jun 2026',D(2026,6,30),5),('1y to 9 Nov 2026',END,1),('3y to 9 Nov 2026',END,3)):
        d0=D(e.year-yrs,e.month,e.day)
        print('   trailing',lab,pct(s.cagr(d0,e),2),'N50',pct(N.cagr(d0,e),2),'N500',pct(F.cagr(d0,e),2))
    print('   NAV 30 Oct 2026',s.at(D(2026,10,30)))
print('\nNifty 50 / Nifty 500 calendar years (direct index funds):',{y:(pct(N.yr(y),2),pct(F.yr(y),2)) for y in range(2020,2026)},'2026 to 2 Sep',pct(N.ret(D(2025,12,31),D(2026,9,2)),2),pct(F.ret(D(2025,12,31),D(2026,9,2)),2),'to 9 Nov',pct(N.ret(D(2025,12,31),END),2),pct(F.ret(D(2025,12,31),END),2))
print('2021-2025 CAGR (31 Dec 2020->31 Dec 2025) N50',pct(N.cagr(D(2020,12,31),D(2025,12,31)),2),'N500',pct(F.cagr(D(2020,12,31),D(2025,12,31)),2))
print('2022-2025 CAGR: Mom direct',pct(MD.cagr(D(2021,12,31),D(2025,12,31)),2),'N50',pct(N.cagr(D(2021,12,31),D(2025,12,31)),2),'N500',pct(F.cagr(D(2021,12,31),D(2025,12,31)),2))
print('Apr 2024 -> Jun 2026 (28 Mar 2024 -> 30 Jun 2026): Mom direct',pct(MD.ret(D(2024,3,28),D(2026,6,30)),2),'N50',pct(N.ret(D(2024,3,28),D(2026,6,30)),2),'N500',pct(F.ret(D(2024,3,28),D(2026,6,30)),2))
pk,tr,dep,last,rec,hi2=dd24(N); print('Nifty 50 direct 2024-25 DD: peak',pk,'trough',tr,pct(dep,2),'latest vs peak',pct(last,2),'recovered',rec)
pk,tr,dep,last,rec,hi2=dd24(F); print('Nifty 500 direct 2024-25 DD: peak',pk,'trough',tr,pct(dep,2),'latest vs peak',pct(last,2),'recovered',rec)
print('\n| Fund | first NAV | CAGR first NAV -> 9 Nov 2026 | UTI Nifty 50 Direct same dates | excess | Nifty 500 same dates | 2024 peak | trough | depth | vs peak at 9 Nov 2026 | recovered | max DD since first NAV |')
for s in [MD,MR]+others:
    pk,tr,dep,last,rec,hi2=dd24(s)
    m=s.mdd(s.first,END)
    c=s.cagr(s.first,END); n=N.cagr(s.first,END); f=F.cagr(s.first,END)
    print('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s (%s -> %s) |'%(s.name,s.first,pct(c,2),pct(n,2),pct(c-n,2),pct(f,2),pk[1],tr[1],pct(dep,1),pct(last,1),rec or 'no',pct(m[0],1),m[1],m[2]))
    print('      calendar:',{y:pct(s.yr(y),1) for y in range(2019,2026)},'2026 to 9 Nov',pct(s.ret(D(2025,12,31),END),1),' 26 Oct CAGR',pct(s.cagr(s.first,OCT),2),'N50',pct(N.cagr(s.first,OCT),2))
