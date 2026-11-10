import pandas as pd, numpy as np
W='/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/work/'
C=pd.read_pickle(W+'close.pkl'); T=pd.read_pickle(W+'turn.pkl'); I=pd.read_pickle(W+'idx.pkl'); M=pd.read_pickle(W+'master.pkl')
for k in ['nifty_50','cnx_nifty','s_p_cnx_nifty','nifty_next_50','cnx_nifty_junior','nifty_midcap_150','nifty_midcap_100','cnx_midcap','nifty_free_float_midcap_100','nifty_full_midcap_100','nifty_200','cnx_200','nifty200_momentum_30','nifty_1d_rate_index','nifty_10_yr_benchmark_g_sec','nifty_composite_g_sec_index','gsec10_nse_index','gsecbm_nse_index','nifty_4_8_yr_g_sec_index','nifty_50_futures_tr_index','nifty_50_arbitrage']:
    if k in I:
        s=I[k].dropna(); print(f"IDX {k:36s} {s.index.min().date()} -> {s.index.max().date()} n={len(s)} first={s.iloc[0]:.2f} last={s.iloc[-1]:.2f}")
    else: print('IDX',k,'MISSING')
etfs=['NIFTYBEES','JUNIORBEES','MID150BEES','GOLDBEES','SILVERBEES','LIQUIDBEES','LIQUIDCASE','LIQUIDADD','GROWWLIQID','MON100','MAFANG','MASPTOP50','LTGILTBEES','GILT5YBEES','SETF10GILT','MOM30IETF','MOMENTUM30','MOMOMENTUM','HDFCMOMENT','MOMENTUM','ALPL30IETF','LOWVOLIETF','M100','MIDCAPETF','MIDCAPIETF','HDFCMID150','LIQUIDIETF','LIQUID','LIQUIDETF','LIQUID1','ABSLLIQUID','LIQUIDSBI','GOLDIETF','SETFGOLD','HDFCGOLD','GOLD1','KOTAKGOLD','NIF100BEES','SETFNIF50','NIFTYIETF','NEXT50IETF','SETFNN50','MIDCAP','MOM100']
for e in etfs:
    if e in C:
        s=C[e].dropna(); r=s.pct_change(); big=r[r.abs()>0.2]
        print(f"ETF {e:12s} {s.index.min().date()} -> {s.index.max().date()} n={len(s)} first={s.iloc[0]:.3f} last={s.iloc[-1]:.3f} big={[(d.date().isoformat(),round(x*100,1)) for d,x in big.items()]}")
    else:
        m=M[(M.symbol==e)|(M.previous_symbols.fillna('').str.contains(e))]
        print('ETF',e,'MISSING', m[['key','symbol','first_date','last_date']].values.tolist())
print(M[M.symbol.str.contains('LIQ|GILT|GSEC|MOM|MID|GOLD|SILV|BEES')][['key','symbol','series','first_date','last_date','status','previous_symbols']].to_string())
