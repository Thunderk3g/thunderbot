import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/verify_nav/scripts')
from core import *
L=[S([100868],'HDFC Liquid Reg-G (100868)'),S([103340],'ICICI Pru Liquid Reg-G (103340)'),S([105280],'SBI Liquid Reg-G (105280)'),
   S([101206],'SBI Overnight Reg-G (101206)'),S([101996],'HDFC Overnight Reg-G (101996)'),
   S([152327],'LIQUIDCASE Zerodha (152327)'),S([152555],'LIQUIDADD DSP BSE Liquid Rate ETF (152555)'),S([152891],'GROWWLIQID (152891)')]
print('SPLIT/FACE-VALUE EVENTS'); 
for x in SPLITLOG: print('  %s: %s %.4f -> %s %.4f ratio %.4f treated as x%g'%x)
for s in L:
    print(s.name,'first',s.first,'%.4f'%s.v[0],'last',s.last,'%.4f'%s.v[-1])
    # anomalies
    for i in range(1,len(s.d)):
        r=s.v[i]/s.v[i-1]-1; gap=(s.d[i]-s.d[i-1]).days
        if r<-0.0002 or r>0.004*max(gap,1)/1: 
            if s.d[i]>=D(2007,12,1): print('   anomaly %s -> %s  %.4f%% (gap %dd)'%(s.d[i-1],s.d[i],100*r,gap))
END=D(2026,11,10); OCT=D(2026,10,26)
print('\n| Year | '+' | '.join(s.name for s in L)+' |'); print('|---|'+'---|'*len(L))
for y in range(2008,2026):
    print('| %d | '%y+' | '.join(pct(s.yr(y),2) for s in L)+' |')
print('| 2026 to 26 Oct | '+' | '.join(pct(s.ret(D(2025,12,31),OCT),2) for s in L)+' |')
print('| 2026 to latest NAV | '+' | '.join(pct(s.ret(D(2025,12,31),s.last),2) for s in L)+' |')
print('| 2026 YTD annualised | '+' | '.join(pct(s.cagr(D(2025,12,31),s.last),2) for s in L)+' |')
print('\npart-year first-year returns for ETFs (first NAV -> 31 Dec of that year), absolute and annualised')
for s in L[5:]:
    y=s.first.year
    a=s.v[0]; b=s.at(D(y,12,31))
    days=(b[0]-s.first).days
    print(' ',s.name,s.first,'->',b[0],'%.3f%% abs, %.2f%% annualised (simple x365/days)'%(100*(b[1]/a-1),100*(b[1]/a-1)*365/days))
print('\nPeriod CAGR (31 Dec start -> latest NAV), and arithmetic mean of calendar years')
for lab,d0,y0 in (('2008-2026',D(2007,12,31),2008),('2011-2026',D(2010,12,31),2011),('2019-2026',D(2018,12,31),2019),('2008-2016',D(2007,12,31),2008),('2017-2026',D(2016,12,31),2017),('2021-2026',D(2020,12,31),2021),('2024-2026',D(2023,12,31),2024)):
    for s in L[:5]:
        e=s.last if lab!='2008-2016' else D(2016,12,31)
        c=s.cagr(d0,e); c2=s.cagr(d0,OCT) if lab!='2008-2016' else None
        ys=[s.yr(y) for y in range(y0,2026 if lab!='2008-2016' else 2017)]
        print('  %s %-32s CAGR to %s %s | to 26 Oct 2026 %s | mean of full calendar years %s'%(lab,s.name,e,pct(c,2),pct(c2,2),pct(sum(ys)/len(ys),2)))
print('\nETF since first NAV CAGR to latest and to 26 Oct 2026, with overnight funds on identical dates')
for s in L[5:]:
    for e in (OCT,s.last):
        print('  %s %s -> %s: ETF %s | SBI Overnight %s | HDFC Overnight %s | HDFC Liquid %s'%(s.name,s.first,e,pct(s.cagr(s.first,e),2),pct(L[3].cagr(s.first,e),2),pct(L[4].cagr(s.first,e),2),pct(L[0].cagr(s.first,e),2)))
# report windows: LIQUIDCASE since 24 Jan 2024, LIQUIDADD since 3 Apr 2024, GROWWLIQID since 26 Sep 2024, to 26 Oct 2026
for s,d0 in ((L[5],D(2024,1,24)),(L[6],D(2024,4,3)),(L[7],D(2024,9,26))):
    print('  report window %s %s -> 26 Oct 2026: %s  (SBI ON %s, HDFC ON %s)'%(s.name,d0,pct(s.cagr(d0,OCT),2),pct(L[3].cagr(d0,OCT),2),pct(L[4].cagr(d0,OCT),2)))
print('\nTrailing annualised as of latest NAV (simple annualisation: return x 365/days; 1y is plain 365-day return)')
for s in L:
    e=s.last; o=[]
    for lab,dd in (('7d',7),('30d',30),('91d',91),('365d',365)):
        a=s.at(e-dt.timedelta(days=dd),3)
        days=(e-a[0]).days
        o.append('%s %.2f%% (from %s)'%(lab,100*(s.v[-1]/a[1]-1)*365/days,a[0]))
    print('  ',s.name,e,' | '.join(o))
print('\nNAV checks: LIQUIDCASE 4 Nov 2026',L[5].at(D(2026,11,4)),' worst daily change of ETFs:')
for s in L[5:]:
    print('  ',s.name,min((s.v[i]/s.v[i-1]-1,s.d[i]) for i in range(1,len(s.v))))
