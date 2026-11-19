#!/usr/bin/env python3
"""cellcheck.py CELL_DIR... -- one line per cell: rc, SET bytes in RUN.BAT, fixed-timestep state, guiclip witness,
labclicks n, FHASH records, presentverify stale_px, exit/quit line, and the guiclip_final counters."""
import os, re, sys
for d in sys.argv[1:]:
    def rd(n):
        p = os.path.join(d, n)
        return open(p, 'rb').read().decode('latin1') if os.path.exists(p) else ''
    cell, out, rm, bat = rd('CELL.txt'), rd('STDOUT.TXT'), rd('RUNMANI.LOG'), rd('RUN.BAT')
    rc = re.search(r'^rc=(\d+)', cell)
    sets = sum(len(l) for l in bat.splitlines() if l.upper().startswith('SET '))
    ft = re.search(r'fixed-timestep: ([A-Z]+)', out)
    gw = re.search(r'DOS-PORT guiclip DOSAGS_GUI_CLIP=(\S+) mode=(\d)', out)
    lc = re.search(r'labclicks n=(\d+)', out)
    fh = rd('FHASH.TXT').count('\n')
    pv = re.search(r'presentverify frames=(\d+) stale_frames=(\d+) stale_px=(\d+)', out + rm)
    gf = re.search(r'guiclip_final (.*)', rm)
    ex = re.search(r'exit_code=(\S+)|exitcode=(\S+)', rm)
    print('%-12s rc=%s sets=%d ft=%s witness=%s labclicks=%s fhash=%d pv=%s %s' % (
        os.path.basename(d.rstrip('/')), rc.group(1) if rc else '?', sets, ft.group(1) if ft else '-',
        ('%s/m%s' % gw.groups()) if gw else 'MISSING', lc.group(1) if lc else '-', fh,
        ('%s/%s/%s' % pv.groups()) if pv else '-', ex.group(0) if ex else ''))
    if gf: print('    ' + gf.group(1).strip())
