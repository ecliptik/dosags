#!/usr/bin/env python3
"""eqcmp.py A_DIR B_DIR -- compare the game output lines of two cells: STDOUT.TXT lines starting 'Game :' plus
'DOS-PORT tickclick' lines, dropping lines that carry wall/emulated times (t_ms=, *_ms=, ms=)."""
import re, sys, os
def kept(d):
    out = []
    for l in open(os.path.join(d, 'STDOUT.TXT'), 'rb').read().decode('latin1').splitlines():
        if not (l.startswith('Game :') or l.startswith('DOS-PORT tickclick')): continue
        if re.search(r'(^|[ _])(t_)?ms=|_ms=|_us=', l): continue
        out.append(l.rstrip())
    return out
a, b = kept(sys.argv[1]), kept(sys.argv[2])
same = a == b
print('%s %d lines | %s %d lines | %s' % (sys.argv[1], len(a), sys.argv[2], len(b), 'EQUAL' if same else 'DIFF'))
if not same:
    import difflib
    for l in list(difflib.unified_diff(a, b, lineterm='', n=0))[:20]: print('  ' + l)
