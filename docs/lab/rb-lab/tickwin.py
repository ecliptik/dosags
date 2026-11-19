#!/usr/bin/env python3
import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ticks import load
T=load(sys.argv[1]); lo,hi=int(sys.argv[2]),int(sys.argv[3])
for t in T['ticks']:
    if lo<=t['lc']<=hi: print(t['lc'],'drawn' if t['drawn'] else 'SKIP ','ugo=%.1f sc=%.1f rn=%.1f'%(t['ugo']/1e3,t.get('scene',0)/1e3,t.get('render',0)/1e3),'room=%s'%t.get('room','') ,'C' if t.get('click') else '')
