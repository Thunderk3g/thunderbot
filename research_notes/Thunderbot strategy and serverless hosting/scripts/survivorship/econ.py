import numpy as np, json
# ---------- D. Momentum 30 vs Nifty 200 calendar years (NSE whitepaper Apr 2026, Exhibit 7; in earlier notes)
mom={2006:44.17,2007:100.84,2008:-60.04,2009:69.34,2010:19.75,2011:-16.07,2012:38.80,2013:12.89,2014:49.56,2015:10.85,2016:9.56,2017:57.46,2018:-1.66,2019:10.55,2020:19.95,2021:53.81,2022:-5.45,2023:41.71,2024:21.33,2025:-4.57}
exc={2006:7.44,2007:35.28,2008:-3.95,2009:-19.47,2010:4.13,2011:10.00,2012:5.17,2013:6.99,2014:12.25,2015:11.60,2016:4.48,2017:22.25,2018:-1.98,2019:0.52,2020:3.13,2021:24.93,2022:-10.36,2023:17.05,2024:6.58,2025:-14.13}
n200={y:mom[y]-exc[y] for y in mom}
rel=1.0; peak=1.0; pk_year=2005; rows=[]; wm=1; wb=1
for y in sorted(mom):
    wm*=1+mom[y]/100; wb*=1+n200[y]/100; rel=wm/wb
    rows.append((y,round(n200[y],1),round(rel,3)))
print("year, implied Nifty200 %, relative wealth Mom30/N200:", rows)
print("Mom30 CAGR 2006-25 %.1f ; N200 %.1f"%((wm**(1/20)-1)*100,(wb**(1/20)-1)*100))
ys=sorted(mom)
for w in (3,5):
    bad=[]
    for i in range(len(ys)-w+1):
        a=np.prod([1+mom[y]/100 for y in ys[i:i+w]])**(1/w)-1; b=np.prod([1+n200[y]/100 for y in ys[i:i+w]])**(1/w)-1
        if a<b: bad.append((ys[i],ys[i+w-1],round((a-b)*100,1)))
    print(f"{w}-calendar-year windows where Mom30 < N200: {len(bad)} of {len(ys)-w+1}:", bad)
# relative drawdown episodes
relw=[1.0]+[r[2] for r in rows]; yrs=[2005]+ys; pk=relw[0]; pky=2005
for y,r in zip(yrs,relw):
    if r>=pk: 
        if y-pky>1: print(f" relative underwater {pky}->{y} ({y-pky} yrs)")
        pk=r; pky=y
print(" still underwater since", pky, "peak rel", pk, "now", relw[-1])
# live years
def cum(d,yrs): return np.prod([1+d[y]/100 for y in yrs])
p='/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/dl/patel-26meet_nse-strategy-indices-visualised/repo/data/'
cy=json.load(open(p+'index_returns_calendar_year.json')); tr=json.load(open(p+'index_returns_tr.json')); t10=json.load(open(p+'index_returns_10y.json'))
B=cy['benchmarks']; D=cy['data']
def ann(d,ys): 
    return (np.prod([1+d[str(y)]/100 for y in ys])**(1/len(ys))-1)*100
print("\nLIVE full calendar years (TRI): index vs benchmark, annualised")
for nm,bn,ys in [('Nifty200 Momentum 30','Nifty 200',range(2021,2026)),('Nifty100 Low Volatility 30','Nifty 100',range(2020,2026)),('Nifty200 Quality 30','Nifty 200',range(2020,2026)),('Nifty Alpha Low-Volatility 30','Nifty 200',range(2020,2026)),('Nifty Alpha 50','Nifty 500',range(2020,2026)),('Nifty500 Value 50','Nifty 500',range(2020,2026)),('Nifty50 Value 20','Nifty 50',range(2020,2026)),('Nifty Midcap150 Momentum 50','Nifty Midcap 150',range(2023,2026)),('Nifty100 Quality 30','Nifty 100',range(2020,2026)),('Nifty Alpha Quality Low-Volatility 30','Nifty 200',range(2020,2026)),('Nifty Quality Low-Volatility 30','Nifty 200',range(2020,2026)),('Nifty Alpha Quality Value Low-Volatility 30','Nifty 200',range(2020,2026))]:
    ys=list(ys); a=ann(D[nm],ys); b=ann(B[bn],ys); wins=sum(D[nm][str(y)]>B[bn][str(y)] for y in ys)
    print(f" {nm:44s} {ys[0]}-{ys[-1]}: {a:5.1f}% vs {bn} {b:5.1f}% -> {a-b:+5.1f} pts; beat in {wins}/{len(ys)} yrs; yearly excess {[round(D[nm][str(y)]-B[bn][str(y)],1) for y in ys]}")
print("\nFirst-half vs second-half of the 10y window to 2 Sep 2026 (TRI): CAGR Sep2016-Sep2021 implied from 10y and 5y")
t10n={k.replace('-',' ').lower():v for k,v in t10['idx'].items()}
def first5(r10,r5): return (((1+r10/100)**10/(1+r5/100)**5)**(1/5)-1)*100
bf={k:first5(t10['bench'][k],tr['benchmarks'][k]['tr5']) for k in t10['bench']}
for nm,bn in [('Nifty200 Momentum 30','Nifty 200'),('Nifty100 Low Volatility 30','Nifty 100'),('Nifty200 Quality 30','Nifty 200'),('Nifty Alpha Low-Volatility 30','Nifty 200'),('Nifty Alpha 50','Nifty 500'),('Nifty500 Value 50','Nifty 500'),('Nifty50 Value 20','Nifty 50'),('Nifty Midcap150 Momentum 50','Nifty Midcap 150'),('Nifty100 Quality 30','Nifty 100'),('Nifty Alpha Quality Low-Volatility 30','Nifty 200'),('Nifty Quality Low-Volatility 30','Nifty 200'),('Nifty Alpha Quality Value Low-Volatility 30','Nifty 200'),('Nifty200 Alpha 30','Nifty 200'),('Nifty500 Momentum 50','Nifty 500'),('Nifty500 Multicap Momentum Quality 50','Nifty 500'),('Nifty500 Multifactor MQVLv 50','Nifty 500'),('Nifty500 Low Volatility 50','Nifty 500'),('Nifty500 Quality 50','Nifty 500')]:
    r10=t10n[nm.replace('-',' ').lower()]; r5=tr['data'][nm]['tr5']; f=first5(r10,r5)
    print(f" {nm:44s} 10y {r10:5.1f} (ex {r10-t10['bench'][bn]:+4.1f}) | Sep16-Sep21 {f:5.1f} (ex {f-bf[bn]:+5.1f}) | Sep21-Sep26 {r5:5.1f} (ex {r5-tr['benchmarks'][bn]['tr5']:+5.1f}) vs {bn}")
