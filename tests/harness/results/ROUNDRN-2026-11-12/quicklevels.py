import re,sys,statistics as st
def s(t): h,m,x=t.split(':'); return int(h)*3600+int(m)*60+float(x)
for c in sys.argv[1:]:
    R=c
    D=[s(re.search(r'down_at=(\S+)',l).group(1)) for l in open(R+'/DRIVE-WALK.LOG') if ' click ' in l and 'down_at=' in l]
    J=[int(re.search(r't_ms=(\d+)',l).group(1))/1000 for l in open(R+'/RUNMANI.LOG',errors='replace') if 'journey kind=click' in l]
    n=min(len(D),len(J)); off=[(D[i]-J[i])*1000 for i in range(n)]
    def med(a,b): return st.median(off[a-1:min(b,n)])
    L=[med(21,33),med(36,52),med(54,90),med(95,114)]
    print(c, 'presses',len(D),'journeys',len(J),'| +830 %+.0f  +1730 %+.0f  +3540 %+.0f ms' % (L[1]-L[0],L[2]-L[1],L[3]-L[2]))
