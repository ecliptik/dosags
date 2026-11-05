import sys
from scdis import *
d=open('/home/claude/git/dosags-lab-mmd/tests/harness/games/mmd/MANIAC.ags','rb').read()
lib=clib.read_header(d)
b=[x for x in lib.assets if x.file_name.lower()=='ac2game.dta'][0]
b=d[b.offset:b.offset+b.size]
sc=parse(b,b.find(b'SCOM'))
fs=funcs(sc); names={a:n for a,n in fs}
st=[a for a,n in fs if n==sys.argv[1]][0]
en=min([a for a,n in fs if a>st] or [len(sc['code'])])
imp=None;fn=None;out=[]
for t in walk(sc,st,en):
    i,op,args=t[0],t[1],t[2]; ann=t[3] if len(t)>3 else []
    for x in ann:
        if x.startswith('IMPORT:'): imp=x[7:]
        if x.startswith('FUNC@'): fn=names.get(int(x[5:]),x)
    if op=='sourceline': out.append('\n@%d L%d:'%(i,args[0]))
    elif op=='farcall': out.append('[%s]'%imp)
    elif op=='call': out.append('<%s>'%fn)
    elif op in ('jzi','jnzi','jmpi'): out.append('%s->%d'%(op[:-1],i+2+args[0]))
    elif op=='ret': out.append('RET')
s=''.join(' '+x if not x.startswith('\n') else x for x in out)
print('\n'.join(l for l in s.split('\n') if l.split(':',1)[-1].strip()))
