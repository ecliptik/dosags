#!/usr/bin/env python3
"""LAB-MMD 9.2 determinism guard (pre-registered in LAB-MMD.md section 9.2).
detdiff.py A_DIR B_DIR  -> exit 0 iff the kept sequences are identical.
Kept from STDOUT.TXT: every 'DOS-PORT statewit' line; every line beginning 'Game :' containing neither
'DOS-PORT' nor 'DOSAGS_XT'. Also AUTOPLT.LOG (after AUTOPLT_MASK, below) and every PH*.BMP by sha256."""
import hashlib, os, re, sys
# Masks for AUTOPLT.LOG, written down before the first comparison: none yet.
AUTOPLT_MASK = []
def kept(d):
    out = []; in_startup = False
    for raw in open(os.path.join(d, 'STDOUT.TXT'), 'rb').read().decode('latin1').splitlines():
        l = raw.rstrip('\r')
        # the startup timing block (excluded by the pre-registration as timing): its inner lines are
        # 'Game :' lines with no DOS-PORT tag, so they are cut by their BEGIN/END markers
        if '[DOS-PORT-STARTUP-BEGIN]' in l: in_startup = True; continue
        if '[DOS-PORT-STARTUP-END]' in l: in_startup = False; continue
        if in_startup: continue
        if 'DOS-PORT statewit' in l: out.append(l[l.index('DOS-PORT statewit'):])
        elif l.startswith('Game :') and 'DOS-PORT' not in l and 'DOSAGS_XT' not in l: out.append(l)
    return out
def autoplt(d):
    p = os.path.join(d, 'AUTOPLT.LOG')
    if not os.path.exists(p): return None
    ls = open(p, 'rb').read().decode('latin1').splitlines()
    for pat, rep in AUTOPLT_MASK: ls = [re.sub(pat, rep, l) for l in ls]
    return ls
def bmps(d):
    return {f: hashlib.sha256(open(os.path.join(d, f), 'rb').read()).hexdigest()[:16]
            for f in sorted(os.listdir(d)) if re.match(r'PH.*\.BMP$', f, re.I)}
a, b = sys.argv[1], sys.argv[2]
ka, kb = kept(a), kept(b)
ok = True
print('kept lines: %d vs %d (statewit %d vs %d)' % (len(ka), len(kb),
      sum('statewit' in l for l in ka), sum('statewit' in l for l in kb)))
if ka != kb:
    ok = False
    for i, (x, y) in enumerate(zip(ka, kb)):
        if x != y: print('FIRST DIFF at kept line %d:\n  A: %s\n  B: %s' % (i, x, y)); break
    else: print('FIRST DIFF: lengths differ')
pa, pb = autoplt(a), autoplt(b)
if pa is not None or pb is not None:
    print('AUTOPLT lines: %s vs %s' % (len(pa or []), len(pb or [])))
    if pa != pb:
        ok = False
        for i, (x, y) in enumerate(zip(pa or [], pb or [])):
            if x != y: print('AUTOPLT FIRST DIFF line %d:\n  A: %s\n  B: %s' % (i, x, y)); break
ba, bb = bmps(a), bmps(b)
if ba or bb:
    print('PH bmps: %s vs %s' % (ba, bb))
    if ba != bb: ok = False
print('EQUAL' if ok else 'DIFFERENT')
sys.exit(0 if ok else 1)
