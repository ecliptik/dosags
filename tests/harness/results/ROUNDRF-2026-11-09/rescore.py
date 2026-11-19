import re,sys,glob,os
W=[('r1entry',5480,8400),('room1',5480,7890),('entry',7890,8400),('room2',8400,9500),('late',9500,10**9)]
for d in sys.argv[1:]:
    t=''
    for f in sorted(glob.glob(os.path.join(d,'RUNMANI.LOG'))): t+=open(f,'rb').read().decode('latin1')
    rows=[tuple(int(x) for x in m) for m in re.findall(r'DOS-PORT persec t=(\d+) tick=(\d+) renders=(\d+) real=(\d+) skipped=(\d+) ms=(\d+)',t)]
    def at(k):  # last row with tick <= k
        c=[r for r in rows if r[1]>=k]; return c[0] if c else rows[-1]
    out=[]
    for n,a,b in W:
        ra,rb=at(a),at(min(b,rows[-1][1]))
        dt=rb[1]-ra[1]; sk=dt-(rb[2]-ra[2]); out.append('%s %d (%.2f%%)'%(n,sk,100*(1-sk/dt) if dt else 0))
        if n=='late': out.append('late_stretch %.1f%%'%(100*(rb[2]-ra[2])/dt))
    fs=re.findall(r'frames_skipped=(\d+)',t); tk=re.findall(r'tick_rate_steady=\S+ ticks=(\d+)',t) or re.findall(r'\bticks=(\d+)',t)
    disp=''
    if fs and tk: disp='displayed %.2f%% (%s of %s)'%(100*(1-int(fs[-1])/int(tk[-1])),fs[-1],tk[-1])
    cr=re.findall(r'charreuse_final[^\n]*',t); gc=re.findall(r'guiclip_final[^\n]*',t)
    print(os.path.basename(d.rstrip('/')),disp,'|',' ; '.join(out))
    print('   ',(cr[-1][:200] if cr else 'no charreuse_final')); print('   ',(gc[-1][:200] if gc else 'no guiclip_final'))
