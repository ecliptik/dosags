import sys,re,difflib
def run(p):
    src=open(p).read().split('\n')
    s=[i for i,l in enumerate(src) if l.startswith('__ZN10ccInstance3RunEl:')][0]
    e=next(i for i in range(s+1,len(src)) if src[i].startswith('\t.globl'))
    b=[l for l in src[s:e] if l.startswith('\t') and not l.startswith('\t.')]
    return [re.sub(r'-?\d+\(%ebp\)','S(%ebp)',re.sub(r'\bL[A-Z]*\d+\b','L',l)) for l in b]
a=run(sys.argv[1]); b=run(sys.argv[2])
sm=difflib.SequenceMatcher(None,a,b,autojunk=False)
ch=[op for op in sm.get_opcodes() if op[0]!='equal']
print('opcode-level changes:',len(ch),' removed',sum(i2-i1 for t,i1,i2,j1,j2 in ch),' added',sum(j2-j1 for t,i1,i2,j1,j2 in ch))
for t,i1,i2,j1,j2 in ch[:25]: print(t,a[i1:i2][:4],'->',b[j1:j2][:4])
