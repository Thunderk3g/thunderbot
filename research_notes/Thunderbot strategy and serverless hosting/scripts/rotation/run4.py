"""Q4: main backtests, pre-cost, three cash treatments, four periods."""
import sys; sys.path.insert(0,'/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/rotation')
from engine import *
A4=['N50','NN50','MID','GOLD']; A3=['N50','NN50','MID']; U3=['N50','NN50','GOLD']
def strategies(P,SG,mode='ME',n=200,lag=0):
    dd=decision_dates(mode)
    S={}
    S['a  B&H Nifty 50 (NIFTYBEES)']=(tgt_fixed({'N50':1.0},dd),dict(annual=False,trade_on_change=False))
    S['b  Nifty>1.01x200DMA else cash']=(tgt_trend(SG,['N50'],dd,n,1.01),{})
    S['b0 Nifty>1.00x200DMA else cash']=(tgt_trend(SG,['N50'],dd,n,1.00),{})
    S['c  4 sleeves trend 1.00x']=(tgt_trend(SG,A4,dd,n,1.00),{})
    S['c1 4 sleeves trend 1.01x']=(tgt_trend(SG,A4,dd,n,1.01),{})
    S['d  dual mom top2 of 4, 200DMA filter']=(tgt_dual(SG,A4,dd,2,'sma',n),{})
    S['d2 dual mom top2 of 4, 12m>6% filter']=(tgt_dual(SG,A4,dd,2,'abs'),{})
    S['e-c no gold: 3 equity sleeves 1.00x']=(tgt_trend(SG,A3,dd,n,1.00),{})
    S['e-d no gold: top2 of 3 equity']=(tgt_dual(SG,A3,dd,2,'sma',n),{})
    S['u-c N50+NN50+GOLD sleeves 1.00x']=(tgt_trend(SG,U3,dd,n,1.00),{})
    S['u-d top2 of N50,NN50,GOLD']=(tgt_dual(SG,U3,dd,2,'sma',n),{})
    S['f1 EW 4 assets, annual rebal']=(tgt_fixed({a:0.25 for a in A4},dd),dict(trade_on_change=False,band=0.0))
    S['f2 75% N50 / 25% gold, annual']=(tgt_fixed({'N50':0.75,'GOLD':0.25},dd),dict(trade_on_change=False,band=0.0))
    S['f3 B&H Next 50 (JUNIORBEES)']=(tgt_fixed({'NN50':1.0},dd),dict(annual=False,trade_on_change=False))
    S['f4 B&H Midcap (index PR chain)']=(tgt_fixed({'MID':1.0},dd),dict(annual=False,trade_on_change=False))
    S['f5 B&H Gold (GOLDBEES)']=(tgt_fixed({'GOLD':1.0},dd),dict(annual=False,trade_on_change=False))
    S['f6 EW 3 equity, annual rebal']=(tgt_fixed({a:1/3 for a in A3},dd),dict(trade_on_change=False,band=0.0))
    return S
if __name__=='__main__':
    P=P0[A4]; SG=SG0[A4]
    gn,c1,c2=gold_neutral(P0); print(f"gold CAGR 2008-2018 {c1*100:.2f}%, 2019-2026 {c2*100:.2f}%; neutralised series 2019-2026 CAGR {((gn.iloc[-1]/gn['2018-12-31'])**(365.25/(gn.index[-1]-pd.Timestamp('2018-12-31')).days)-1)*100:.2f}%")
    Pg=P.copy(); Pg['GOLD']=gn; SGg=SG.copy(); SGg['GOLD']=gn
    S=strategies(P,SG); Sg=strategies(Pg,SGg)
    for k in ['c  4 sleeves trend 1.00x','d  dual mom top2 of 4, 200DMA filter','f1 EW 4 assets, annual rebal','f2 75% N50 / 25% gold, annual','f5 B&H Gold (GOLDBEES)']:
        S['g '+k[3:]+' [gold de-trended 2019+]']=Sg[k]+(Pg,)
    res=[]
    for per,(a,z) in list(PERIODS.items())+[('2013-2026',('2012-12-31','2026-10-26'))]:
        for nm,v in S.items():
            T,kw=v[0],v[1]; PP=v[2] if len(v)>2 else P
            row={'period':per,'strategy':nm}
            for cm in ['c6','c0','cA']:
                eq,st=simulate(px_with_cash(PP,cm),T,a,z,**kw); pf=perf(eq)
                if cm=='c6':
                    row.update({'CAGR6':pf['cagr'],'vol':pf['vol'],'MDD':pf['mdd'],'peak':pf['peak'],'trough':pf['trough'],'worstY':f"{pf['worst_y']} {pf['worst']:+.1f}",'UWyrs':pf['uw_years'],'UW':f"{pf['uw'][0]}->{pf['uw'][1]}",'orders/yr':st['orders']/pf['years'],'events/yr':st['events']/pf['years'],'cash%':st['cash_share']*100})
                else: row['CAGR'+cm[1]]=pf['cagr']; row['MDD'+cm[1]]=pf['mdd']
            res.append(row)
    R=pd.DataFrame(res); R.to_pickle(OUT+'res4.pkl')
    pd.set_option('display.width',400); pd.set_option('display.max_columns',40); pd.set_option('display.max_rows',500)
    for per in R.period.unique():
        print('\n=====',per); print(R[R.period==per].drop(columns='period').round(1).to_string(index=False))
