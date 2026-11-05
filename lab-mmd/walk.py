import sys,re
src=open(sys.argv[1]).read().split('\n')
start=[i for i,l in enumerate(src) if l.startswith('__ZN10ccInstance3RunEl:')][0]
end=next(i for i in range(start+1,len(src)) if src[i].startswith('\t.globl'))
body=src[start:end]
ti=[i for i,l in enumerate(src) if l=='L514:'][0]
tab=[]
for l in src[ti+1:]:
    m=re.match(r'\t\.long\t(L\d+)',l)
    if not m: break
    tab.append(m.group(1))
lab={l[:-1]:i for i,l in enumerate(body) if re.match(r'^L\d+:$',l)}
STOP={'L588','L804','L627','L987'}
def ins(l): return l.startswith('\t') and not l.startswith('\t.')
def walk(L,maxn=400):
    i=lab[L]; n=0; calls=[]; seen=set(); path=[]
    while n<maxn:
        l=body[i]
        m=re.match(r'^(L\d+):$',l)
        if m and m.group(1) in STOP and n>0: return n,calls,m.group(1)
        if ins(l):
            n+=1
            m=re.match(r'\tjmp\t(L\d+)$',l)
            if m:
                t=m.group(1)
                if t in STOP: return n,calls,t
                if t in seen: return n,calls,'loop:'+t
                seen.add(t); i=lab[t]; continue
            if l.startswith('\tjmp\t*'): return n,calls,'indirect'
            m=re.match(r'\tcall\t(\S+)',l)
            if m: calls.append(m.group(1)[:40])
        i+=1
    return n,calls,'max'
ops=dict(a.split('=') for a in sys.argv[2:])
tot=0
for name,num in ops.items():
    op,cnt=num.split(':'); n,calls,how=walk(tab[int(op)])
    tot+=n*int(cnt)
    print(f'{name:12s} op{op:>3s} x{cnt:>4s}/tick  path {n:3d} instr  -> {how:10s} {n*int(cnt):6d}  calls {calls}')
print('sum handler instr/tick (fall-through paths, excl. called fns):',tot)
