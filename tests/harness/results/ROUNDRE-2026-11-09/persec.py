import re,sys
for d in sys.argv[1:]:
    t=open(d+'/RUNMANI.LOG','rb').read().decode('latin1')
    rows=[tuple(int(x) for x in m) for m in re.findall(r'DOS-PORT persec t=(\d+) tick=(\d+) renders=(\d+) real=(\d+) skipped=(\d+) ms=(\d+)',t)]
    out=[]
    for a,b in zip(rows,rows[1:]):
        sk=(b[1]-a[1])-(b[2]-a[2])
        if sk>0: out.append('%d:%d'%(b[1],sk))
    stalls=re.findall(r'tick_stall index=(\d+) ms=(\d+)',t)
    print(d[:4],'stalls',stalls); print('  ',' '.join(out))
