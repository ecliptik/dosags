import sys,re
def run(p):
    src=open(p).read().split('\n')
    s=[i for i,l in enumerate(src) if l.startswith('__ZN10ccInstance3RunEl:')][0]
    e=next(i for i in range(s+1,len(src)) if src[i].startswith('\t.globl'))
    b=src[s:e]
    # normalise local labels (Lnnn, LEHBnn, LEHEnn, LCnn, LFBnn...) by order of first appearance
    names={}
    def norm(l):
        def r(m):
            k=m.group(0)
            if k not in names: names[k]='L#%d'%len(names)
            return names[k]
        return re.sub(r'\bL[A-Z]*\d+\b',r,l)
    ins=[norm(l) for l in b if l.strip() and not l.startswith('\t.cfi')]
    return ins,sum(1 for l in b if l.startswith('\t') and not l.startswith('\t.')),sum('8(%ebp),' in l for l in b)
a,na,ra=run(sys.argv[1]); b,nb,rb=run(sys.argv[2])
print('clean: instrs',na,'this-reloads',ra,'| probe: instrs',nb,'this-reloads',rb)
diffs=[(i,x,y) for i,(x,y) in enumerate(zip(a,b)) if x!=y]
print('lines',len(a),len(b),'differing lines',len(diffs)+abs(len(a)-len(b)))
for d in diffs[:10]: print(d)
