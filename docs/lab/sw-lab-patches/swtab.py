#!/usr/bin/env python3
"""swtab.py RESULTS_DIR -- one row per cell: save size/sha, savegame_ms, int21 ms, CPU-side, fwrite/fseek ms, dry run."""
import os, re, sys
R = sys.argv[1]
print('(restart_savegame_ms: the trace header in SW cells; else the STDOUT line or, for 5days, the journey write_ms)')
print('| cell | prior (B) | save (B) | sha256[:12] | restart_savegame_ms | int21 n / ms | stdio fwrite ms | fseek ms | open / close ms | bracket - int21 (CPU-side) ms | dry run |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for c in sorted(os.listdir(R)):
    d = os.path.join(R, c)
    if not os.path.isdir(d): continue
    sv = open(os.path.join(d, 'SAVE-SHA256.txt')).read().split() if os.path.exists(os.path.join(d, 'SAVE-SHA256.txt')) else ['-', '-']
    pr = '-'
    if os.path.exists(os.path.join(d, 'PRIOR-SHA256.txt')):
        _p = open(os.path.join(d, 'PRIOR-SHA256.txt')).read().split(); pr = _p[-1] if len(_p) > 2 else 'MISSING'
    st = open(os.path.join(d, 'STDOUT.TXT'), 'rb').read().decode('latin1') if os.path.exists(os.path.join(d, 'STDOUT.TXT')) else ''
    m = re.search(r'restart_savegame_ms=(\d+)', st) or re.search(r'save_restartpoint .*write_ms=(\d+)', open(os.path.join(d,'RUNMANI.LOG'),'rb').read().decode('latin1') if os.path.exists(os.path.join(d,'RUNMANI.LOG')) else ''); sg = m.group(1) if m else '-'
    t = os.path.join(d, 'SWTRACE.TXT')
    if not os.path.exists(t):
        print('| %s | %s | %s | %s | %s | (off) | | | | | |' % (c, pr, sv[1], sv[0][:12], sg)); continue
    s = open(t).read()
    sg = re.search(r'savegame_ms=(\d+)', s).group(1) + ' (trace)'
    g = lambda k: (re.search(k + r'=([-\d.]+)', s) or [None, '-'])[1]
    br = float(g('bracket_ms')); i21 = float(g('int21_ms'))
    dry = re.search(r'dry=(\w+)(.*)', s).group(0).strip()
    print('| %s | %s | %s | %s | %s | %s / %.1f | %s | %s | %s / %s | %.1f | %s |' % (c, pr, sv[1], sv[0][:12], sg, g('int21_n'), i21,
          g('fwrite_ms'), g('fseek_ms'), g('open_ms'), g('close_ms'), br - i21, dry))
