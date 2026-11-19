#!/usr/bin/env python3
"""Attribute each run of skipped ticks to the drawn tick(s) before it (RDMP TICKS.BIN, grouped by tick)."""
import sys, collections; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ticks import load
T=load(sys.argv[1]); lo=int(sys.argv[2]) if len(sys.argv)>2 else 5436
tk=[t for t in T['ticks'] if t['lc']>=lo]
clicks=[t['lc'] for t in tk if t.get('click')]
cat=collections.Counter(); rows=[]
i=0
while i<len(tk):
    if tk[i]['drawn']: i+=1; continue
    j=i
    while j<len(tk) and not tk[j]['drawn']: j+=1
    run=j-i
    # cause = the costliest tick among the 2 ticks before the run
    prev=[t for t in tk[max(0,i-2):i]]
    c=max(prev,key=lambda t:t['ugo']) if prev else None
    lc=c['lc']; u=c['ugo']/1e3; sc=c.get('scene',0)/1e3
    near=[k for k in clicks if 0<=lc-k<=8]
    if u>250: k='stall>250ms'
    elif c.get('click'): k='click tick'
    elif near and sc>12: k='post-click GUI tick'
    elif u>60: k='no-event spike'
    else: k='ordinary (ugo<=60)'
    cat[k]+=run; rows.append((tk[i]['lc'],run,lc,round(u,1),round(sc,1),k))
    i=j
for r in rows: print(*r)
print(dict(cat), 'total', sum(cat.values()))
