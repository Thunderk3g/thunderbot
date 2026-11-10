import sys
sys.path.insert(0,'/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/verify_nav/scripts')
from navlib import *
for c in sys.argv[1:]:
    m,s,bad=load(c)
    print(c,'|',m.get('fund_house'),'|',m.get('scheme_name'),'|',m.get('scheme_category'),'|',m.get('isin_growth'))
    if not s: print('   EMPTY'); continue
    print('   n=%d bad=%d first=%s %.4f last=%s %.4f'%(len(s),bad,s[0][0],s[0][1],s[-1][0],s[-1][1]))
    # gaps > 10 days
    g=[(a[0],b[0]) for a,b in zip(s,s[1:]) if (b[0]-a[0]).days>10]
    if g: print('   gaps>10d:',[(str(a),str(b)) for a,b in g][:8], len(g))
    for d0,v0,d1,v1,r in jumps(s,0.8,1.25): print('   JUMP %s %.4f -> %s %.4f ratio %.4f'%(d0,v0,d1,v1,r))
