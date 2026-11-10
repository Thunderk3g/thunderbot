"""Backtest engine for the rotation study. All figures are own computations from the panel built by prep.py."""
import numpy as np, pandas as pd
OUT='/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/rotation/'
D=pd.read_pickle(OUT+'panel.pkl'); P0=D['P']; SG0=D['SG']; CASH=D['CASH']
days=P0.index
EQ={'N50','NN50','MID'}
PERIODS={'2008-2026':('2007-12-31','2026-10-26'),'2011-2026':('2010-12-31','2026-10-26'),'2008-2018':('2007-12-31','2018-12-31'),'2019-2026':('2018-12-31','2026-10-26')}

def order_cost(V, side, asset, liq_etf=True):
    """Groww delivery order cost in rupees incl. slippage."""
    if V<=0: return 0.0
    if asset=='LIQ' and not liq_etf: return 0.0
    brk=min(20.0,max(5.0,0.001*V)); exch=0.0000297*V; sebi=0.000001*V
    gst=0.18*(brk+exch+sebi)
    stamp=0.00015*V if side=='buy' else 0.0
    stt=0.00001*V if (side=='sell' and asset in EQ) else 0.0
    dp=23.60 if side=='sell' else 0.0
    slip=(0.0010 if asset=='MID' else 0.0005)*V
    return brk+exch+sebi+gst+stamp+stt+dp+slip

# ---------------- signals / targets ----------------
def decision_dates(mode='ME'):
    g=days.to_series().groupby([days.year,days.month])
    if mode=='ME':
        d=g.last().values[:-1]          # drop the incomplete last month (data ends 26 Oct 2026)
    else:
        k=int(mode); d=[x.iloc[k-1] if len(x)>=k else x.iloc[-1] for _,x in g]
        last=[x for _,x in g][-1]
        if len(last)<k: d=d[:-1]
    return pd.DatetimeIndex(d)
def sma_ratio(SG, n):
    if n=='10m':
        me=decision_dates('ME'); m=SG.loc[me]; r=(m/m.rolling(10,min_periods=9).mean())
        return r.reindex(days).ffill()   # only meaningful on month-end decisions
    return SG/SG.rolling(n,min_periods=int(n*0.95)).mean()
def tgt_trend(SG, assets, dd, n=200, buf=1.0, weights=None):
    r=sma_ratio(SG[assets],n).loc[dd]; on=(r>buf)
    w=pd.Series(1.0/len(assets),index=assets) if weights is None else pd.Series(weights)
    T=on.astype(float)*w; T['LIQ']=1-T.sum(axis=1); return T
def tgt_dual(SG, assets, dd, topk=2, filt='sma', n=200, buf=1.0, cash_rate=0.06):
    X=SG[assets]; B=X.bfill()
    r6=X/B.shift(126)-1; r12=X/B.shift(252)-1; sc=((r6+r12)/2).loc[dd]
    if filt=='sma': ok=(sma_ratio(X,n).loc[dd]>buf)
    else: ok=(r12.loc[dd]>cash_rate)
    rk=sc.rank(axis=1,ascending=False,method='first')
    T=((rk<=topk)&ok).astype(float)/topk; T[sc.isna()]=0.0
    T['LIQ']=1-T.sum(axis=1); return T
def tgt_fixed(weights, dd):
    T=pd.DataFrame([weights]*len(dd),index=dd).fillna(0.0)
    if 'LIQ' not in T: T['LIQ']=0.0
    return T

# ---------------- simulator ----------------
def simulate(PX, TGT, start, end, capital=1.0, costs=False, tax=False, slab=0.312, liq_etf=True, lag=0, band=0.05, annual=True, trade_on_change=True):
    """PX: daily prices (cols include 'LIQ'); TGT: target weights at decision dates. Trades at the close of decision day (+lag days).
    Trades happen when the target changes, and at the last decision of each calendar year (annual rebalance); an asset is traded only if
    it is opened, closed, or more than `band` (share of portfolio) away from target. LIQ is the residual."""
    assets=[c for c in TGT.columns if c!='LIQ']+['LIQ']; TGT=TGT[assets]
    start=pd.Timestamp(start); end=pd.Timestamp(end)
    px=PX[assets]; idx=px.index; i0=idx.get_loc(start); i1=idx.get_loc(end)
    pv=px.values; nA=len(assets); L=nA-1
    units=np.zeros(nA); idle=0.0; lots=[[] for _ in range(nA)]
    fy={'eq_st':0.0,'eq_lt':0.0,'gold_st':0.0,'gold_lt':0.0,'liq':0.0}; cf={'st':0.0,'lt':0.0}
    stats={'orders':0,'cost':0.0,'tax':0.0,'events':0}
    def c_(V,side,a): return order_cost(V,side,assets[a],liq_etf) if costs else 0.0
    def buy(a,budget,i):
        nonlocal idle
        if budget<=0: return
        c=c_(budget,'buy',a); val=budget-c
        if val<=0: idle+=budget; return
        u=val/pv[i,a]; units[a]+=u; lots[a].append([u,budget/u,i]); stats['orders']+=(1 if (a!=L or liq_etf) else 0); stats['cost']+=c
    def realise(a,u_sold,proceeds,i,book,lts):
        rem=u_sold; ppu=proceeds/u_sold
        while rem>1e-12 and lts:
            lot=lts[0]; q=min(rem,lot[0]); g=q*(ppu-lot[1]); lt=(idx[i]-idx[lot[2]]).days>365
            nm=assets[a]
            if nm in EQ: book['eq_lt' if lt else 'eq_st']+=g
            elif nm=='GOLD': book['gold_lt' if lt else 'gold_st']+=g
            else: book['liq']+=g
            lot[0]-=q; rem-=q
            if lot[0]<=1e-12: lts.pop(0)
    def sell(a,V,i):
        V=min(V,units[a]*pv[i,a])
        if V<=0: return 0.0
        u=V/pv[i,a]; c=c_(V,'sell',a); pr=V-c
        realise(a,u,pr,i,fy,lots[a]); units[a]-=u
        if units[a]<1e-12: units[a]=0.0; lots[a].clear()
        stats['orders']+=(1 if (a!=L or liq_etf) else 0); stats['cost']+=c; return pr
    def tax_due(book,cfw):
        rate={'slabst':slab,'eq_st':0.208}
        st={'slabst':book['gold_st']+book['liq'],'eq_st':book['eq_st']}; lt={'gold_lt':book['gold_lt'],'eq_lt':book['eq_lt']}
        stl=-sum(min(v,0) for v in st.values())-cfw['st']; ltl=-sum(min(v,0) for v in lt.values())-cfw['lt']
        st={k:max(v,0) for k,v in st.items()}; lt={k:max(v,0) for k,v in lt.items()}
        for k in ['gold_lt','eq_lt']:                       # LT losses only against LT gains
            x=min(ltl,lt[k]); lt[k]-=x; ltl-=x
        order=sorted(st,key=lambda k:-rate[k])+['gold_lt','eq_lt']   # ST losses against highest-taxed gains first
        if slab<0.13: order=['eq_st','gold_lt','eq_lt','slabst']
        for k in order:
            tgt=st if k in st else lt; x=min(stl,tgt[k]); tgt[k]-=x; stl-=x
        t=slab*st['slabst']+0.208*st['eq_st']+0.13*lt['gold_lt']+0.13*max(lt['eq_lt']-125000.0,0.0)
        return t,{'st':-stl,'lt':-ltl}
    def pay(t,i):
        nonlocal idle
        if t<=0: return
        stats['tax']+=t
        x=min(idle,t); idle-=x; t-=x
        if t<=0: return
        lv=units[L]*pv[i,L]; x=min(lv,t)
        if x>0:
            f=1-x/lv if lv>0 else 1; units[L]*=f
            for lot in lots[L]: lot[0]*=f
            t-=x
        if t>1e-9:
            tot=(units*pv[i]).sum()
            if tot>0:
                f=max(0.0,1-t/tot); units[:]*=f
                for a in range(nA):
                    for lot in lots[a]: lot[0]*=f
    dd=TGT.index; ddpos=idx.get_indexer(dd)
    prev=TGT.loc[:start].iloc[-1].values.copy()
    # initial purchase at the close of `start`
    for a in range(nA):
        if prev[a]>0: buy(a,prev[a]*capital,i0)
    ev=[]   # (exec index, kind, payload)
    yrs=dd.year
    for k,(d,p) in enumerate(zip(dd,ddpos)):
        if d<=start: continue
        e=p+lag
        if e>i1 or d>end: continue
        is_ann=(k+1<len(dd) and yrs[k+1]!=yrs[k])
        ev.append((e,1,(TGT.values[k],is_ann)))
    if tax:
        s=idx.to_series().iloc[i0:i1+1]; mar=s[s.index.month==3].groupby(s[s.index.month==3].index.year).last()
        for d in mar: ev.append((idx.get_loc(d),2,None))
    ev.sort(key=lambda x:(x[0],x[1]))
    U=np.zeros((i1-i0+1,nA)); IDL=np.zeros(i1-i0+1); cur=i0
    def flush(to):
        nonlocal cur
        U[cur-i0:to-i0]=units; IDL[cur-i0:to-i0]=idle; cur=to
    for e,kind,pl in ev:
        flush(e)
        if kind==1:
            tg,is_ann=pl; changed=not np.allclose(tg,prev,atol=1e-9)
            if (changed and trade_on_change) or (annual and is_ann):
                stats['events']+=1
                val=units*pv[e]; V=val.sum()+idle; des=tg*V; cash=idle; idle=0.0; buys=[]
                for a in range(L):
                    dlt=des[a]-val[a]
                    if (tg[a]==0 and val[a]>0) or (val[a]==0 and tg[a]>0) or abs(dlt)>band*V:
                        if dlt<0: cash+=sell(a,-dlt,e)
                        elif dlt>0: buys.append((a,dlt))
                need=sum(b for _,b in buys)
                if need>cash:
                    lv=units[L]*pv[e,L]; x=min(lv,(need-cash)*1.002+ (30 if (costs and liq_etf) else 0))
                    if x>0: cash+=sell(L,x,e)
                sc=min(1.0,cash/need) if need>0 else 0.0
                for a,b in buys: buy(a,b*sc,e); cash-=b*sc
                if cash>0:
                    if (not costs) or (not liq_etf) or cash>0.005*V: buy(L,cash,e)
                    else: idle+=cash
            prev=tg.copy()
        else:
            t,cfn=tax_due(fy,cf); cf.update(cfn); pay(t,e)
            for k_ in fy: fy[k_]=0.0
    flush(i1+1)
    eqv=pd.Series((U*pv[i0:i1+1]).sum(axis=1)+IDL,index=idx[i0:i1+1])
    wl=pd.Series((U[:,L]*pv[i0:i1+1,L]+IDL)/eqv.values,index=eqv.index)
    # liquidation value at end: sell everything, settle this FY's tax
    liqv=eqv.iloc[-1]
    if tax or costs:
        book=dict(fy); tot=0.0
        for a in range(nA):
            V=units[a]*pv[i1,a]
            if V<=0: continue
            c=c_(V,'sell',a); pr=V-c; tot+=pr
            if tax: realise(a,units[a],pr,i1,book,[l[:] for l in lots[a]])
        tot+=idle
        if tax:
            t,_=tax_due(book,cf); tot-=t
        liqv=tot
    stats['liq_value']=liqv; stats['cash_share']=float(wl.mean())
    return eqv,stats

def perf(eq):
    yrs=(eq.index[-1]-eq.index[0]).days/365.25; cagr=(eq.iloc[-1]/eq.iloc[0])**(1/yrs)-1
    r=eq.pct_change().dropna(); vol=r.std()*np.sqrt(252); dd=eq/eq.cummax()-1; t=dd.idxmin(); pk=eq[:t].idxmax()
    ye=eq.groupby(eq.index.year).last(); yr=ye.pct_change(); yr.iloc[0]=ye.iloc[0]/eq.iloc[0]-1
    if eq.index[0].month==12 and len(eq[eq.index.year==eq.index[0].year])<=1: yr=yr.iloc[1:]
    # longest underwater spell (calendar days from a peak until it is regained; ongoing spells count to the end)
    cm=eq.cummax(); under=eq<cm*(1-1e-9); best=0; st=None; bs=None; last_peak=eq.index[0]
    for d,u in under.items():
        if u and st is None: st=last_peak
        if not u:
            if st is not None and (d-st).days>best: best=(d-st).days; bs=(st.date(),d.date())
            st=None; last_peak=d
    if st is not None and (eq.index[-1]-st).days>best: best=(eq.index[-1]-st).days; bs=(st.date(),'ongoing')
    return dict(cagr=cagr*100,vol=vol*100,mdd=dd.min()*100,peak=pk.date(),trough=t.date(),worst_y=int(yr.idxmin()),worst=yr.min()*100,uw_years=best/365.25,uw=bs,years=yrs)
def px_with_cash(P, cash='c6'):
    X=P.copy(); X['LIQ']=CASH[cash]; return X
def gold_neutral(P):
    """GOLD from 2019 with a constant daily log-drift removed so that its 2019-2026 CAGR equals its 2008-2018 CAGR."""
    g=P['GOLD']; a=g['2007-12-31']; b=g['2018-12-31']; c=g.iloc[-1]
    y1=(pd.Timestamp('2018-12-31')-pd.Timestamp('2007-12-31')).days/365.25; cagr1=(b/a)**(1/y1)-1
    m=g.index>pd.Timestamp('2018-12-31'); n=m.sum(); y2=(g.index[-1]-pd.Timestamp('2018-12-31')).days/365.25
    target=np.log(1+cagr1)*y2; actual=np.log(c/b); adj=(actual-target)/n
    lr=np.log(g).diff(); lr[m]=lr[m]-adj; out=np.exp(lr.fillna(0).cumsum())*g.dropna().iloc[0]; out[g.isna()]=np.nan
    return out, cagr1, (c/b)**(1/y2)-1
