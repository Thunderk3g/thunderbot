import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/verify_nav/scripts')
from core import *
import pandas as pd, warnings; warnings.simplefilter('ignore')
C=pd.read_pickle('/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/work/close.pkl')
H=S([100868],'HDFC Liquid'); 
print('HDFC Liquid last NAVs daily annualised %:',[(str(H.d[i])[5:],round(36500*(H.v[i]/H.v[i-1]-1)/max((H.d[i]-H.d[i-1]).days,1),2)) for i in range(len(H.d)-14,len(H.d))])
Z=S([152327],'LIQUIDCASE'); print('LIQUIDCASE last daily annualised %:',[(str(Z.d[i])[5:],round(36500*(Z.v[i]/Z.v[i-1]-1)/max((Z.d[i]-Z.d[i-1]).days,1),2)) for i in range(len(Z.d)-10,len(Z.d))])
s=S([149758],'SILVERBEES'); nav=pd.Series(s.v,index=pd.to_datetime(s.d)); df=pd.concat([C['SILVERBEES'].rename('px'),nav.rename('nav')],axis=1).dropna(); df['prem']=100*(df.px/df.nav-1)
print('SILVERBEES Oct 2025 premium: max %.2f on %s, min %.2f, median %.2f'%(df.loc['2025-10-01':'2025-10-31'].prem.max(),df.loc['2025-10-01':'2025-10-31'].prem.idxmax().date(),df.loc['2025-10-01':'2025-10-31'].prem.min(),df.loc['2025-10-01':'2025-10-31'].prem.median()))
print(df['2025-10-08':'2025-10-24'].round(2).to_string())
print(df['2026-01-28':'2026-02-04'].round(2).to_string())
print('SILVERBEES NAV calendar: 2023',pct(s.yr(2023)),'2024',pct(s.yr(2024)),'2025',pct(s.yr(2025)),'2026 to 26 Oct',pct(s.ret(D(2025,12,31),D(2026,10,26))),'to 9 Nov',pct(s.ret(D(2025,12,31),D(2026,11,9))))
Mo=S([114984],'MON100'); print('MON100 NAV calendar:',{y:pct(Mo.yr(y)) for y in (2012,2022,2024,2025)},'2026 to 26 Oct',pct(Mo.ret(D(2025,12,31),D(2026,10,26))))
N=S([120716],'N50d'); pk=max((v,d) for d,v in N.s if D(2024,9,1)<=d<=D(2024,10,31)); print('N50 direct vs Sep-2024 peak at 4 Sep 2026',pct(N.at(D(2026,9,4))[1]/pk[0]-1,2),'at 26 Oct 2026',pct(N.at(D(2026,10,26))[1]/pk[0]-1,2))
T=S([150738],'Tata'); M=S([146271],'MID150'); 
for e in (D(2026,10,26),D(2026,11,9)): print('Tata MidMom50 direct',T.first,'->',e,pct(T.cagr(T.first,e),2),'MID150BEES NAV same',pct(M.cagr(T.first,e),2))
print('MID150BEES calendar vs Tata: ',{y:(pct(T.yr(y)),pct(M.yr(y))) for y in (2023,2024,2025)})
K=S([149397],'Kotak Alpha'); F=S([147625],'N500'); 
print('Alpha50 ETF vs N500 direct, from',K.first,': ',pct(K.cagr(K.first,D(2026,11,9)),2),pct(F.cagr(K.first,D(2026,11,9)),2))
U=S([148703],'UTI mom d'); print('UTI mom direct NAV on dates:',[(str(d),U.at(d)[1]) for d in (D(2026,10,26),D(2026,10,30),D(2026,11,9))], 'date when NAV ~21.436 (+114.36%):',[str(d) for d,v in U.s if d>D(2026,6,1) and abs(v/10-2.1436)<0.004][:6])
