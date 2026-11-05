import sys,re
exec(open('/home/claude/git/dosags-lab-mmd/lab-mmd/hwalk.py').read().split('for p in sys.argv')[0])
mix={3:813,6:722,2:554,36:550,7:454,29:384,30:299,34:289,28:183,39:175,35:168,15:126,12:96,1:91,8:87,5:66,38:66,19:65,23:64,11:57,31:49}
def score(p):
    src=open(p).read().split('\n')
    s=[i for i,l in enumerate(src) if l.startswith('__ZN10ccInstance3RunEl:')][0]
    e=next(i for i in range(s+1,len(src)) if src[i].startswith('\t.globl'))
    body=[l for l in src[s:e] if l.startswith('\t') and not l.startswith('\t.')]
    try:
        b,tab,lab,loop,back=load(p)
    except Exception as ex:
        return len(body),None,None,str(ex)
    if loop is None:
        # find loop label as the target of the back-edge's final je
        i=lab[back]
        for l in b[i:i+12]:
            m=re.match(r'\tje\t(L\d+)',l)
            if m: loop=m.group(1); break
    head=walk(b,lab,loop,{back}) if loop else -1
    bk=0; i=lab[back]
    for l in b[i:i+12]:
        if l.startswith('\t') and not l.startswith('\t.'):
            bk+=1
            if l.startswith('\tje'): break
    h=sum(walk(b,lab,tab[op],{back,loop})*c for op,c in mix.items())
    pc_mem=any('(%ebp)' in l and 'leal\t1(' not in l for l in b[lab[back]:lab[back]+3])
    return len(body),head,bk,h
for p in sys.argv[1:]:
    n,head,bk,h=score(p)
    print(f"{p.split('/')[-1]:28s} Run {n}  head(to dispatch,1st path) {head}  back-edge {bk}  weighted handlers {h}")
