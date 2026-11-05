import sys, collections
from scdis import *
d=open('/home/claude/git/dosags-lab-mmd/tests/harness/games/mmd/MANIAC.ags','rb').read()
lib=clib.read_header(d)
a=[x for x in lib.assets if x.file_name.lower()=='ac2game.dta'][0]
b=d[a.offset:a.offset+a.size]
sc=parse(b,b.find(b'SCOM'))
fs=funcs(sc); starts=[x[0] for x in fs]
bounds={fs[i][0]:(fs[i+1][0] if i+1<len(fs) else len(sc['code'])) for i in range(len(fs))}
name={a:n for a,n in fs}
def info(addr):
    ins=walk(sc,addr,bounds[addr])
    calls=[];exts=[];back=0;lastimp=None;lastfn=None
    for t in ins:
        i,op,args=t[0],t[1],t[2]; ann=t[3] if len(t)>3 else []
        for x in ann:
            if x.startswith('IMPORT:'): lastimp=x[7:]
            if x.startswith('FUNC@'): lastfn=int(x[5:])
        if op=='farcall': exts.append(lastimp)
        if op=='call': calls.append(lastfn)
        if op=='jmpi' and args[0]<0: back+=1
    return len(ins),calls,exts,back
root=[a for a,n in fs if n.startswith(sys.argv[1]+'$')][0]
seen=set();order=[];q=[root]
while q:
    f=q.pop(0)
    if f in seen or f not in bounds: continue
    seen.add(f);order.append(f)
    n,c,e,bk=info(f)
    q+= [x for x in c if x is not None]
for f in order:
    n,c,e,bk=info(f)
    ec=collections.Counter(e)
    print('%-28s ins_static=%5d backjmps=%2d calls=%s'%(name[f],n,bk,sorted(set(name.get(x,'?%s'%x) for x in c))))
    print('   ext:',', '.join('%s x%d'%(k,v) for k,v in ec.most_common()))
