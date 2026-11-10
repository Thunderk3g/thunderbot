"""Q1-Q3: inventory, big-move scan, calendar-year returns, period stats, liquidity."""
import pandas as pd, numpy as np, json
S='/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/'
W=S+'work/'; OUT=S+'rotation/'
C=pd.read_pickle(W+'close.pkl'); T=pd.read_pickle(W+'turn.pkl'); I=pd.read_pickle(W+'idx.pkl')
D=pd.read_pickle(OUT+'panel.pkl'); P=D['P']; RAW=D['RAW']; CASH=D['CASH']
pd.set_option('display.width',300); pd.set_option('display.max_columns',40)
days=C.index
etfs=['NIFTYBEES','JUNIORBEES','MID150BEES','GOLDBEES','SILVERBEES','LIQUIDBEES','LIQUIDCASE','LIQUIDADD','GROWWLIQID','MON100','MAFANG','MASPTOP50','LTGILTBEES','GILT5YBEES','SETF10GILT','MOM30IETF','MOMENTUM30','MOMOMENTUM','HDFCMOMENT','MOMENTUM','ALPL30IETF','LOWVOLIETF','MOM100']
print("=== Q1 big-move scan (|1-day| > 10%) and liquidity (Rs crore/day)")
last=days[-1]; d3=days[days>last-pd.DateOffset(months=3)]; d12=days[days>last-pd.DateOffset(months=12)]
print(f"windows: 3m {d3[0].date()}..{last.date()} ({len(d3)} days); 12m {d12[0].date()}..{last.date()} ({len(d12)} days)")
rows=[]
for e in etfs:
    s=C[e].dropna(); r=s.pct_change(); b20=r[r.abs()>0.2]; b10=r[(r.abs()>0.1)&(r.abs()<=0.2)]
    t=T[e]/1e7
    def st(dd):
        x=t.reindex(dd); return x.mean(skipna=True), x.fillna(0).median(), int(x.notna().sum())
    a3,m3,n3=st(d3); a12,m12,n12=st(d12)
    rows.append([e,s.index[0].date(),len(s),'; '.join(f"{d.date()} {x*100:+.1f}%" for d,x in b20.items()) or '-', len(b10), '; '.join(f"{d.date()} {x*100:+.1f}%" for d,x in b10.items())[:150], round(a3,2),round(m3,2),round(a12,2),round(m12,2),n12])
print(pd.DataFrame(rows,columns=['etf','first','n','moves>20%','n 10-20%','moves 10-20%','avg3m','med3m','avg12m','med12m','days traded 12m']).to_string(index=False))
print("turnover unit check NIFTYBEES last 5:", (T['NIFTYBEES'].tail(5)).tolist(), 'close', C['NIFTYBEES'].tail(2).tolist())
# TRI check
H=S+'rotation_dl/Indranil-Mondal_nifty-market-digest-bot/repo/data/history/'
for f,e,ix in [('nifty_50.json','NIFTYBEES','n50_idx'),('nifty_next_50.json','JUNIORBEES','nn50_idx'),('nifty_midcap_150.json','MID150BEES','mid150_idx')]:
    s=json.load(open(H+f))['series']; tri=pd.Series({pd.Timestamp(k):v.get('tri') for k,v in s.items()}).dropna()
    a,z=pd.Timestamp('2025-05-15'),pd.Timestamp('2026-10-26')
    print(f"TRI check {a.date()}..{z.date()}: {f[:-5]} TRI {100*(tri[z]/tri[a]-1):+.2f}% | {e} {100*(C[e].ffill()[z]/C[e].ffill()[a]-1):+.2f}% | price index {100*(RAW[ix][z]/RAW[ix][a]-1):+.2f}%")
    lv={k:v.get('level') for k,v in s.items() if v.get('level')}; kk=sorted(lv)[-1]; print('   latest level in file', kk, lv[kk], 'vs 26 Oct', RAW[ix][z], f"{100*(lv[kk]/RAW[ix][z]-1):+.1f}%")
print("\n=== Q2 calendar-year returns (%)")
ser={'GOLDBEES (ETF)':P['GOLD'],'Nifty50 idx PR':RAW['n50_idx'],'NIFTYBEES (ETF)':P['N50'],'Next50 idx PR':RAW['nn50_idx'],'JUNIORBEES (ETF)':P['NN50'],
     'Midcap100 idx PR':RAW['mid100_idx'],'Midcap150 idx PR':RAW['mid150_idx'],'MOM100 (Mid100 ETF)':C['MOM100'].ffill(),'MID150BEES (ETF)':C['MID150BEES'].ffill(),
     'N200 Mom30 idx PR':RAW['mom30_idx'],'Nifty 1D Rate idx':RAW['rate1d_idx'],'LIQUIDCASE (ETF)':C['LIQUIDCASE'].ffill(),'SILVERBEES (ETF)':C['SILVERBEES'].ffill(),'MON100 (ETF)':C['MON100'].ffill()}
Y={}
for k,s in ser.items():
    ye=s.groupby(s.index.year).last(); cnt=s.dropna().groupby(s.dropna().index.year).count()
    r=ye.pct_change()*100
    # require the prior year-end value to exist (full-year only)
    Y[k]=r
Y=pd.DataFrame(Y).loc[2008:2026]
print(Y.round(1).to_string(na_rep='  -'))
for k,s in ser.items(): print(f"   first date {k:22s} {s.first_valid_index().date()}")
def stats(s,a,z):
    s=s.dropna(); 
    if s.index[0]>pd.Timestamp(a): return None
    x=s[:a]; p0=x.index[-1]; w=s[p0:z]
    yrs=(w.index[-1]-w.index[0]).days/365.25; cagr=(w.iloc[-1]/w.iloc[0])**(1/yrs)-1
    vol=w.pct_change().std()*np.sqrt(252); dd=w/w.cummax()-1; t=dd.idxmin(); pk=w[:t].idxmax()
    return cagr*100,vol*100,dd.min()*100,pk.date(),t.date()
print("\nPeriod stats: CAGR / vol / maxDD (peak->trough) ; best yr / worst yr. Period starts at the last close before the start date.")
for nm,a,z in [('2008-2026','2007-12-31','2026-10-26'),('2011-2026','2010-12-31','2026-10-26'),('2008-2018','2007-12-31','2018-12-31'),('2019-2026','2018-12-31','2026-10-26')]:
    print(nm)
    for k,s in ser.items():
        st=stats(s,a,z)
        if st is None: print(f"   {k:22s} n/a (starts {s.first_valid_index().date()})"); continue
        yy=Y[k].loc[int(nm[:4]):int(nm[5:])].dropna()
        print(f"   {k:22s} CAGR {st[0]:5.1f} vol {st[1]:5.1f} maxDD {st[2]:6.1f} ({st[3]}->{st[4]}) best {yy.idxmax()} {yy.max():+.1f} worst {yy.idxmin()} {yy.min():+.1f}")
# stats from own first full date for short series
print("since-inception stats for short series")
for k in ['Midcap100 idx PR','Midcap150 idx PR','MID150BEES (ETF)','N200 Mom30 idx PR','Nifty 1D Rate idx','LIQUIDCASE (ETF)','MOM100 (Mid100 ETF)']:
    s=ser[k].dropna(); st=stats(s,s.index[0],'2026-10-26'); print(f"   {k:22s} from {s.index[0].date()} CAGR {st[0]:5.2f} vol {st[1]:5.1f} maxDD {st[2]:6.1f} ({st[3]}->{st[4]})")
# liquid ETFs vs 1D rate index
for e in ['LIQUIDCASE','LIQUIDADD','GROWWLIQID','LIQUID1']:
    s=C[e].dropna(); a=s.index[0]; i=RAW['rate1d_idx']; yrs=(s.index[-1]-a).days/365.25
    print(f"   {e}: {a.date()}.. ann {((s.iloc[-1]/s.iloc[0])**(1/yrs)-1)*100:.2f}% vs 1D rate index {((i.iloc[-1]/i[a])**(1/yrs)-1)*100:.2f}% ; worst 1-day {s.pct_change().min()*100:.2f}% ; down days {int((s.pct_change()<-0.0002).sum())} of {len(s)}")
print('LIQUIDBEES price range', C['LIQUIDBEES'].min(), C['LIQUIDBEES'].max())
# Nifty after 26 Oct
n=pd.read_pickle(OUT+'n50_index_to_nov.pkl'); sma=n.rolling(200).mean()
print(pd.DataFrame({'close':n,'sma200':sma,'ratio':n/sma})['2026-08-25':].iloc[[0,5,25,26,-8,-6,-1]].round(4))
me=n.groupby([n.index.year,n.index.month]).tail(1); print(pd.DataFrame({'close':me,'ratio':(n/sma).reindex(me.index)})['2025-06-01':].round(4).to_string())
print('Nifty 50 index 2025 close', n[:'2025-12-31'].iloc[-1], '; YTD to 26 Oct', n['2026-10-26']/n[:'2025-12-31'].iloc[-1]-1, '; to 6 Nov', n.iloc[-1]/n[:'2025-12-31'].iloc[-1]-1)
