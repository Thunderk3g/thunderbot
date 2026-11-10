import pandas as pd, numpy as np
W='/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/work/'
I=pd.read_pickle(W+'idx.pkl'); N=pd.read_pickle(W+'n50_returns.pkl')
a=I['nifty_alpha_50'].dropna(); r=a.pct_change(); print("alpha50 |ret|>15% days:\n", r[r.abs()>0.15])
# repair: treat |daily move|>25% in an index as a rebasing artefact
def repair(s):
    r=s.pct_change().fillna(0); bad=r.abs()>0.25; r[bad]=0; return (1+r).cumprod()*s.iloc[0], int(bad.sum())
n50f=pd.read_csv('/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/dl/rishabhjain0295-web_nifty500-momentum-backtest/repo/data/index/NIFTY50.csv')
print(n50f.columns.tolist(), n50f.iloc[0].tolist(), n50f.iloc[-1].tolist())
dc=[c for c in n50f.columns if 'date' in c.lower()][0]; cc=[c for c in n50f.columns if c.lower()=='close'][0]
n50=pd.Series(pd.to_numeric(n50f[cc],errors='coerce').values, index=pd.DatetimeIndex(pd.to_datetime(n50f[dc],errors='coerce')).normalize()).dropna(); n50=n50[~n50.index.duplicated()].sort_index()
off=I['nifty_50'].dropna(); j=n50.index.intersection(off.index); print("yahoo/NSE Nifty50 file vs bhavcopy index file: max abs diff % on overlap:", float(((n50[j]/off[j]-1).abs()).max()*100), "n", len(j))
n50=pd.concat([n50[:off.index[0]-pd.Timedelta(days=1)], off]); 
CASH=0.065; COST=0.0015
def filt(asset_ret, sig_price, name, start, end, own=False):
    """month-end check: invested next day if signal price > 200DMA at month-end close"""
    ar=asset_ret[start:end]; sp=sig_price.reindex(sig_price.index.union(ar.index)).ffill()
    sma=sp.rolling(200).mean(); on=(sp>sma)
    me=ar.index.to_series().groupby([ar.index.year,ar.index.month]).last().values
    sig=pd.Series(np.nan,index=ar.index); sig.loc[me]=on.reindex(me).astype(float).values; sig=sig.ffill().shift(1).fillna(1.0)
    daily_cash=(1+CASH)**(1/252)-1
    # pre-tax
    sw=(sig.diff().abs()>0); r=np.where(sig>0, ar, daily_cash) - np.where(sw, COST, 0.0); r=pd.Series(r,index=ar.index)
    # after-tax simulation (rate: STCG 20.8% if held<=365d else LTCG 13.0%; no exemption; loss pool carried fwd; cash interest taxed 31.2%)
    def aftertax(sigser):
        val=1.0; basis=1.0; entry=ar.index[0]; inv=True; pool=0.0; eq=[]
        for d,x in ar.items():
            s=sigser.loc[d]
            if s>0 and not inv:   # re-enter
                val*=(1-COST); basis=val; entry=d; inv=True
            if s==0 and inv:      # exit: realise
                val*=(1-COST); gain=val-basis; rate=0.208 if (d-entry).days<=365 else 0.13
                g=gain+pool
                if g>0: val-=g*rate; pool=0.0
                else: pool=g
                inv=False
            val*= (1+x) if inv else (1+daily_cash*(1-0.312))
            eq.append(val)
        eq=pd.Series(eq,index=ar.index)
        liq=eq.iloc[-1]
        if inv:
            gain=liq-basis+pool; rate=0.208 if (ar.index[-1]-entry).days<=365 else 0.13
            liq-= max(gain,0)*rate
        return eq, liq
    def S(x):
        eq=(1+x).cumprod(); yrs=(x.index[-1]-x.index[0]).days/365.25; dd=eq/eq.cummax()-1; return (eq.iloc[-1]**(1/yrs)-1)*100, x.std()*np.sqrt(252)*100, dd.min()*100
    yrs=(ar.index[-1]-ar.index[0]).days/365.25
    bh=S(ar); f=S(r)
    eqf,liqf=aftertax(sig); eqb,liqb=aftertax(pd.Series(1.0,index=ar.index))
    ddf=(eqf/eqf.cummax()-1).min()*100
    nsw=int(sw.sum()); tim=float(sig.mean()*100)
    print(f"{name:46s} {ar.index[0].date()}..{ar.index[-1].date()} | B&H {bh[0]:5.1f}% vol {bh[1]:4.1f} DD {bh[2]:6.1f} | filter {f[0]:5.1f}% vol {f[1]:4.1f} DD {f[2]:6.1f} | switches {nsw} ({nsw/yrs:.1f}/yr) in-mkt {tim:3.0f}% | after-tax liquidated CAGR: B&H {(liqb**(1/yrs)-1)*100:5.1f}% vs filter {(liqf**(1/yrs)-1)*100:5.1f}% (filter after-tax DD {ddf:5.1f})")
def price_to_ret(s): return s.pct_change().fillna(0)
m30=I['nifty200_momentum_30'].dropna(); a50,nb=repair(I['nifty_alpha_50'].dropna()); print("alpha50 repaired days:", nb)
n200=I['nifty_200'].dropna(); lv=I['nifty100_low_volatility_30'].dropna()
pm=N["PIT Nifty 50 (reconstructed)|Mom top15 keep25"]; pm10=N["PIT Nifty 50 (reconstructed)|Mom top10 keep17"]; pe=N["PIT Nifty 50 (reconstructed)|EW all"]
pmp=(1+pm).cumprod(); 
print("\nSignal = Nifty 50 vs its 200-DMA, month-end check, cash 6.5%, 0.15% per switch")
filt(price_to_ret(n50), n50, 'Nifty 50 PR', '2006-04-03','2026-10-26')
filt(price_to_ret(n50), n50, 'Nifty 50 PR', '2011-01-03','2026-10-26')
filt(pm, n50, 'PIT N50 momentum top15/keep25 (own, PR)', '2006-04-03','2026-10-26')
filt(pm, n50, 'PIT N50 momentum top15/keep25 (own, PR)', '2011-01-03','2026-10-26')
filt(pm, n50, 'PIT N50 momentum top15/keep25 (own, PR)', '2006-04-03','2010-12-31')
filt(pm10, n50, 'PIT N50 momentum top10/keep17 (own, PR)', '2006-04-03','2026-10-26')
filt(price_to_ret(m30), n50, 'Nifty200 Momentum 30 PR (LIVE)', '2020-08-25','2026-10-26')
filt(price_to_ret(a50), n50, 'Nifty Alpha 50 PR (LIVE, repaired)', '2013-03-01','2026-10-26')
filt(price_to_ret(n200), n50, 'Nifty 200 PR', '2012-03-01','2026-10-26')
filt(price_to_ret(lv), n50, 'Nifty100 Low Vol 30 PR (LIVE)', '2016-07-11','2026-10-26')
print("\nSignal = the asset's OWN 200-DMA")
filt(pm, pmp, 'PIT N50 momentum top15/keep25 (own, PR)', '2007-04-02','2026-10-26')
filt(price_to_ret(m30), m30, 'Nifty200 Momentum 30 PR (LIVE)', '2021-07-01','2026-10-26')
filt(price_to_ret(a50), a50, 'Nifty Alpha 50 PR (LIVE, repaired)', '2014-01-01','2026-10-26')
# alpha 50 repaired stats
s=a50['2013-03-01':]; yrs=(s.index[-1]-s.index[0]).days/365.25; dd=s/s.cummax()-1; b=I['nifty_500'].dropna()['2013-03-01':]
print("Alpha50 repaired from 2013-03-01: CAGR %.1f vol %.1f maxDD %.1f (%s) ; Nifty500 CAGR %.1f"%(((s.iloc[-1]/s.iloc[0])**(1/yrs)-1)*100, np.log(s).diff().std()*np.sqrt(252)*100, dd.min()*100, dd.idxmin().date(), ((b.iloc[-1]/b.iloc[0])**(1/yrs)-1)*100))
x=(s/b.reindex(s.index)).dropna(); pk=x.cummax(); und=(x<pk); 
# longest relative underwater
best=0;st=None;bs=None
for d,u in und.items():
    if u and st is None: st=d
    if not u and st is not None:
        if (d-st).days>best: best=(d-st).days; bs=(st.date(),d.date())
        st=None
if st is not None and (x.index[-1]-st).days>best: best=(x.index[-1]-st).days; bs=(st.date(),'ongoing')
print("Alpha50 vs Nifty500 longest relative underwater: %.1fy %s; max rel DD %.1f%%"%(best/365.25,bs,((x/pk-1).min())*100))
