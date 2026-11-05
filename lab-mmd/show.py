import sys,re
src=open(sys.argv[1]).read().split('\n')
s=[i for i,l in enumerate(src) if l.startswith('__ZN10ccInstance3RunEl:')][0]
e=next(i for i in range(s+1,len(src)) if src[i].startswith('\t.globl'))
b=src[s:e]
ti=[i for i,l in enumerate(src) if l=='L514:'][0]
tab=[]
for l in src[ti+1:]:
    m=re.match(r'\t\.long\t(L\d+)',l)
    if not m: break
    tab.append(m.group(1))
lab={l[:-1]:i for i,l in enumerate(b) if re.match(r'^L\d+:$',l)}
def block(L,n=40):
    i=lab[L]; out=[]
    for l in b[i:i+n]:
        if l.startswith('\t.'): continue
        out.append(l)
        if l.startswith('\tjmp'): break
    return out
if sys.argv[2].startswith('L'):
    for L in sys.argv[2:]: print('\n'.join(block(L))); print('---')
else:
    for op in sys.argv[2:]:
        print('== op',op,tab[int(op)]); print('\n'.join(block(tab[int(op)])))
