import re,sys,shutil,os
S,R=sys.argv[1:3]
def mk(src,dst,skips,stretch,stamp='pppppppppppp',lab=True,t=45,ticks=None,persec_stretch=None,old_line=False):
    shutil.copytree(os.path.join(R,src),os.path.join(S,dst))
    ps_st = stretch if persec_stretch is None else persec_stretch
    for f in os.listdir(os.path.join(S,dst)):
        if f.upper().endswith('.LOG'):
            p=os.path.join(S,dst,f); s=open(p,errors='replace').read()
            s=s.replace('binary_sha12=f2e183845d2f','binary_sha12='+stamp)
            if f=='RUNMANI.LOG':
                s=re.sub(r'frames_skipped=\d+','frames_skipped=%d'%skips,s)
                s=re.sub(r'loop_ms=(\d+)',lambda m:'loop_ms=%d'%round(int(m.group(1))*stretch),s)
                def ps(m):
                    tick,ms=int(m.group(2)),int(m.group(3))
                    return m.group(1)+'ms=%d'%(ms if tick<5520 else round(ms+(ms-22000)*(ps_st-1)))
                s=re.sub(r'(DOS-PORT persec t=\d+ tick=(\d+) renders=\d+ real=\d+ skipped=\d+ )ms=(\d+)',ps,s)
                if ticks: s=re.sub(r'(tick_rate_steady=[\d.]+ )ticks=7003',r'\1ticks=%d'%ticks,s)
                if lab and old_line: s=s.replace('DOS-PORT tick_rate_steady=','DOS-PORT labpace stall_ms=%d rebases=170 forgiven_ticks=60 max_forgiven_ticks=60 spins=0\nDOS-PORT tick_rate_steady='%t,1)
                elif lab: s=s.replace('DOS-PORT tick_rate_steady=','DOS-PORT labpace stall_ms=%d rebases=170 forgiven_ticks=260 max_forgiven_ticks=148 max_forgiven_short_ticks=3 spins=0\nDOS-PORT tick_rate_steady='%t,1)
            open(p,'w').write(s)
A1,A2,A3='RSA1-2026-11-19','RSA2-2026-11-19','RSA3-2026-11-19'
shutil.copytree(os.path.join(R,A1),os.path.join(S,'RTA1-2026-11-19')); shutil.copytree(os.path.join(R,A2),os.path.join(S,'RTA2-2026-11-19'))
for d,a in (('met',(20,1.008,15,1.009)),('bar',(20,1.008,80,1.009)),('time',(20,1.008,15,1.025)),('edge',(70,1.008,15,1.0199))):
    os.makedirs(os.path.join(S,d))
    for x in ('RTA1-2026-11-19','RTA2-2026-11-19'): shutil.copytree(os.path.join(S,x),os.path.join(S,d,x))
    mk(A3,d+'/RTP1-2026-11-19',a[0],a[1]); mk(A1,d+'/RTP2-2026-11-19',a[2],a[3])
os.makedirs(os.path.join(S,'odd'))
mk(A2,'odd/RTP3-2026-11-19',18,1.025)                 # an extra P cell over the time limit
mk(A2,'odd/RTP9-2026-11-19',18,1.008,lab=False)       # no labpace -> VOID
mk(A2,'odd/RTP8-2026-11-19',18,1.008,t=50)            # wrong T -> VOID
mk(A2,'odd/RTP7-2026-11-19',18,1.008,ticks=6990)      # ticks != 7003 -> VOID
mk(A2,'odd/RTP6-2026-11-19',18,1.008,persec_stretch=1.02)  # G and Gwin disagree -> HELD
mk(A2,'odd/RTP5-2026-11-19',18,1.025,persec_stretch=1.05)  # G over 2.0 AND G/Gwin disagree -> HELD first (FIX-UP 1)
mk(A2,'odd/RTP4-2026-11-19',18,1.008,old_line=True)        # the pre-fix-up labpace line (no short field) -> VOID
