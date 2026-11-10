import json, sys, re
B='/tmp/claude-0/-home-user-thunderbot/e06b3674-c1d3-5929-b7a1-9860e62bca6e/scratchpad/verify_nav'
L=json.load(open(B+'/data/all_schemes.json'))
for pat in sys.argv[1:]:
    print('==',pat)
    r=re.compile(pat,re.I)
    for s in L:
        if r.search(s['schemeName']): print(s['schemeCode'],'|',s['schemeName'],'|',s.get('isinGrowth'))
