import sys, struct
sys.path.insert(0, '/home/claude/git/dosags-lab-mmd/tools/port-game')
import clib
import os; S=os.path.dirname(os.path.abspath(__file__))
OPS={}
num={}
for l in open('/home/claude/git/dosags-lab-mmd/vendor/ags/Common/script/cc_internal.h'):
    p=l.split()
    if len(p)>=3 and p[0]=='#define' and p[1].startswith('SCMD_'): num[p[1]]=int(p[2])
for l in open(S+'/ops.txt'):
    n,name,argc=l.split(); OPS[num[n]]=(name,int(argc))
def cstr(b,p):
    e=b.index(b'\0',p); return b[p:e].decode('latin1'), e+1
def parse(b,p):
    assert b[p:p+4]==b'SCOM'
    ver,gds,cs,ss=struct.unpack_from('<iiii',b,p+4); p+=20
    p+=gds
    code=list(struct.unpack_from('<%di'%cs,b,p)); p+=4*cs
    strings=b[p:p+ss]; p+=ss
    nf,=struct.unpack_from('<i',b,p); p+=4
    ft=b[p:p+nf]; p+=nf
    fx=struct.unpack_from('<%di'%nf,b,p); p+=4*nf
    ni,=struct.unpack_from('<i',b,p); p+=4
    imps=[]
    for _ in range(ni):
        s,p=cstr(b,p); imps.append(s)
    ne,=struct.unpack_from('<i',b,p); p+=4
    exps=[]
    for _ in range(ne):
        s,p=cstr(b,p); a,=struct.unpack_from('<i',b,p); p+=4; exps.append((s,a))
    secs=[]
    if ver>=83:
        ns,=struct.unpack_from('<i',b,p); p+=4
        for _ in range(ns):
            s,p=cstr(b,p); o,=struct.unpack_from('<i',b,p); p+=4; secs.append((s,o))
    return dict(ver=ver,code=code,fix=dict(zip(fx,ft)),imps=imps,exps=exps,secs=secs,end=p)
def funcs(sc):
    f=sorted((a&0xFFFFFF,n) for n,a in sc['exps'] if (a>>24)&0xFF==1)
    return f
def walk(sc,start,end):
    code=sc['code'];fix=sc['fix'];i=start;out=[]
    regimp={}
    while i<end:
        op=code[i]&0xFFFFFF
        if op not in OPS: out.append((i,'?%d'%op,[]));i+=1;continue
        name,argc=OPS[op];args=code[i+1:i+1+argc]
        ann=[]
        for k in range(argc):
            t=fix.get(i+1+k)
            if t==4: ann.append('IMPORT:'+sc['imps'][args[k]])
            elif t==2: ann.append('FUNC@%d'%args[k])
            elif t==3: ann.append('STR')
        out.append((i,name,args,ann)); i+=1+argc
    return out
if __name__=='__main__':
    d=open('/home/claude/git/dosags-lab-mmd/tests/harness/games/mmd/MANIAC.ags','rb').read()
    lib=clib.read_header(d)
    want=sys.argv[1]
    a=[x for x in lib.assets if x.file_name.lower()==want.lower()][0]
    b=d[a.offset:a.offset+a.size]
    idx=0; n=0
    while True:
        idx=b.find(b'SCOM',idx)
        if idx<0: break
        try:
            sc=parse(b,idx)
            fs=funcs(sc)
            print('SCOM #%d at %d ver=%d code=%d imports=%d funcs=%d names=%s'%(n,idx,sc['ver'],len(sc['code']),len(sc['imps']),len(fs),[x[1] for x in fs][:60]))
            n+=1; idx=sc['end']
        except Exception as e:
            idx+=4
