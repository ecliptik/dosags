#!/usr/bin/env python3
"""LAB-L1B inertness: 'Game :' lines of two STDOUT.TXTs with every timing field (*_ms=, *_us=, t_ms=, ms=, us=) removed.
gameeq.py A/STDOUT.TXT B/STDOUT.TXT"""
import re, sys
def g(p):
    out = []
    for l in open(p, 'rb').read().decode('latin1').splitlines():
        if not l.startswith('Game :'):
            continue
        l = re.sub(r'\b\w*_(ms|us)=\S+', '', l)
        l = re.sub(r'\b(t_ms|ms|us)=\S+', '', l)
        out.append(re.sub(r'\s+', ' ', l).strip())
    return out
a, b = g(sys.argv[1]), g(sys.argv[2])
eq = a == b
print('%s %d vs %d lines: %s' % ('EQUAL' if eq else 'DIFF', len(a), len(b), sys.argv[1] + ' | ' + sys.argv[2]))
if not eq:
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            print('first diff at %d:\n  %s\n  %s' % (i, x, y)); break
