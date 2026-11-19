#!/usr/bin/env python3
"""guardcheck.py VENDOR_ROOT [REV_RANGE] -- every line added by REV_RANGE (default HEAD~1..HEAD; "WT" = the working
tree against HEAD), mapped to its line in the patched file and to the #if nesting that encloses it. Prints, per file,
each contiguous block of added lines with the guard that covers it (the line of the innermost enclosing positive
__DJGPP__ branch: #ifdef __DJGPP__, #if defined(__DJGPP__) ..., or the #else of #ifndef __DJGPP__), and a verdict per
file. A block's own #ifdef / #endif lines count as covered when they open / close that block's guard."""
import re, subprocess, sys
root = sys.argv[1]
rng = sys.argv[2] if len(sys.argv) > 2 else 'HEAD~1..HEAD'
if rng == 'WT':
    files = subprocess.run(['git', '-C', root, 'diff', '--name-only'], capture_output=True, text=True).stdout.split()
    dargs, show = ['diff', '-U0'], None
else:
    files = subprocess.run(['git', '-C', root, 'diff', '--name-only', rng], capture_output=True, text=True).stdout.split()
    dargs, show = ['diff', '-U0', rng], rng.split('..')[1]
total_bad = 0
for f in files:
    diff = subprocess.run(['git', '-C', root] + dargs + ['--', f], capture_output=True, text=True).stdout
    added = set()
    for m in re.finditer(r'^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@', diff, re.M):
        a, n = int(m.group(1)), int(m.group(2) if m.group(2) is not None else 1)
        added.update(range(a, a + n))
    text = (subprocess.run(['git', '-C', root, 'show', '%s:%s' % (show, f)], capture_output=True).stdout.decode('latin1')
            if show else open(root + '/' + f, encoding='latin1').read())
    lines = text.split('\n')
    stack = []   # [kind, opening line]
    cover = {}
    for i, l in enumerate(lines, 1):
        s = l.strip()
        opened = None
        if s.startswith('#if'):
            pos = bool(re.match(r'#ifdef\s+__DJGPP__\b', s) or re.match(r'#if\s+defined\s*\(\s*__DJGPP__\s*\)', s))
            neg = bool(re.match(r'#ifndef\s+__DJGPP__\b', s))
            stack.append(['pos' if pos else 'neg' if neg else 'other', i]); opened = stack[-1]
        elif s.startswith('#else') and stack:
            k = stack[-1][0]; stack[-1][0] = 'neg' if k == 'pos' else 'pos' if k == 'neg' else 'other'
        elif s.startswith('#elif') and stack:
            stack[-1][0] = 'other'
        closing = None
        if s.startswith('#endif') and stack:
            closing = stack[-1]
        if i in added:
            g = [e for e in stack if e[0] == 'pos']
            if g: cover[i] = 'guard @%d' % g[-1][1]
            elif closing and closing[0] == 'pos': cover[i] = 'closes guard @%d' % closing[1]
            elif not s: cover[i] = 'blank'
            else: cover[i] = 'UNGUARDED'
        if closing is not None:
            stack.pop()
    blocks = []
    for i in sorted(added):
        if blocks and i == blocks[-1][1] + 1 and cover[i].replace('closes ', '') == cover[blocks[-1][0]].replace('closes ', ''):
            blocks[-1][1] = i
        else:
            blocks.append([i, i])
    bad = sum(1 for v in cover.values() if v == 'UNGUARDED')
    total_bad += bad
    print('== %s: %d added lines in %d blocks, %d unguarded -> %s' % (f, len(added), len(blocks), bad, 'OK' if bad == 0 else 'FAIL'))
    for a, b in blocks:
        first = lines[a - 1].strip()[:70]
        print('   %5d-%-5d %-18s %s' % (a, b, cover[a].replace('closes ', ''), first))
print('TOTAL unguarded: %d' % total_bad)
