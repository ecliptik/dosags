import sys,re
def load(p):
    src=open(p).read().split('\n')
    s=[i for i,l in enumerate(src) if l.startswith('__ZN10ccInstance3RunEl:')][0]
    e=next(i for i in range(s+1,len(src)) if src[i].startswith('\t.globl'))
    b=src[s:e]
    jt=None; loop=None
    for i,l in enumerate(b):
        m=re.match(r'\tjmp\t\*(L\d+)\(,%e..,4\)',l)
        if m:
            jt=m.group(1)
            # loop label = last label before the head that is followed by the codeInst load
            for k in range(i,0,-1):
                if re.match(r'^L\d+:$',b[k]) and b[k+1].startswith('\tmovl\t-') and '24(%eax)' in b[k+3]: loop=b[k][:-1]; break
            break
    ti=[i for i,l in enumerate(src) if l==jt+':'][0]
    tab=[]
    for l in src[ti+1:]:
        m=re.match(r'\t\.long\t(L\d+)',l)
        if not m: break
        tab.append(m.group(1))
    lab={l[:-1]:i for i,l in enumerate(b) if re.match(r'^L\d+:$',l)}
    # back-edge label: target of 'jmp' after 'andl $2, %eax' most common
    from collections import Counter
    c=Counter()
    for i,l in enumerate(b):
        m=re.match(r'\tjmp\t(L\d+)$',l)
        if m and b[i-1]=='\tandl\t$2, %eax': c[m.group(1)]+=1
    back=c.most_common(1)[0][0]
    return b,tab,lab,loop,back
def ins(l): return l.startswith('\t') and not l.startswith('\t.')
def walk(b,lab,L,stops):
    i=lab[L]; n=0; seen=set()
    while n<300:
        l=b[i]
        m=re.match(r'^(L\d+):$',l)
        if m and m.group(1) in stops and n>0: return n
        if ins(l):
            n+=1
            m=re.match(r'\tjmp\t(L\d+)$',l)
            if m:
                t=m.group(1)
                if t in stops: return n
                if t in seen: return n
                seen.add(t); i=lab[t]; continue
            if l.startswith('\tjmp\t*'): return n
        i+=1
    return n
for p in sys.argv[1:3]:
    b,tab,lab,loop,back=load(p)
    # back-edge length
    bn=walk(b,lab,back,{loop})
    res=[walk(b,lab,tab[op],{back,loop}) for op in (3,6,2,36,7,29,30,34,28,39,35,15,12,1,8,5,38,19,23,11,31)]
    print(p.split('/')[-1], 'back-edge',bn,'handlers(mov,movl,subi,srcline,memread4,push,pop,farpush,jzi,setfuncargs,farsubsp,cmpeq,sub,addi,memwrite4,ret,thisaddr,gte,call,add,jmpi)',res)
