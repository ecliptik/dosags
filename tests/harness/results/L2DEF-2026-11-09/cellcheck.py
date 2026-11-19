#!/usr/bin/env python3
"""cellcheck.py CELL_DIR... (LAB-L2G copy: + the guictrlmark witness and guictrlmark_final / labgc2_final lines)
 -- (R3LAND's cellcheck.py + LAB-R2B fields) one line per cell: rc, SET bytes in RUN.BAT (total and
longest line), fixed-timestep state, guiclip and charreuse witnesses, labclicks n, FHASH records, presentverify, then the
guiclip_final / charreuse_final / charreuse_lab counters."""
import os, re, sys
for d in sys.argv[1:]:
    def rd(n):
        p = os.path.join(d, n)
        return open(p, 'rb').read().decode('latin1') if os.path.exists(p) else ''
    cell, out, rm, bat = rd('CELL.txt'), rd('STDOUT.TXT'), rd('RUNMANI.LOG'), rd('RUN.BAT')
    rc = re.search(r'^rc=(\d+)', cell)
    setl = [l for l in bat.splitlines() if l.upper().startswith('SET ')]
    sets = sum(len(l) for l in setl)
    ft = re.search(r'fixed-timestep: ([A-Z]+)', out)
    gw = re.search(r'DOS-PORT guiclip DOSAGS_GUI_CLIP=(\S+) mode=(\d)', out)
    cw = re.search(r'DOS-PORT charreuse DOSAGS_CHAR_REUSE=(\S+) mode=(\d)', out)
    lc = re.search(r'labclicks n=(\d+)', out)
    rw = re.search(r'DOS-PORT guictrlmark DOSAGS_GUI_CTRL_MARK=(\S+) mode=(\d)', out)
    fh = rd('FHASH.TXT').count('\n')
    pv = re.search(r'presentverify frames=(\d+) stale_frames=(\d+) stale_px=(\d+)', out + rm)
    ex = re.search(r'exit_code=(\S+)|exitcode=(\S+)', rm)
    print('%-14s rc=%s sets=%d/%d ft=%s gc=%s cr=%s gm=%s labclicks=%s fhash=%d pv=%s %s' % (
        os.path.basename(d.rstrip('/')), rc.group(1) if rc else '?', sets, max([len(l) for l in setl] or [0]),
        ft.group(1) if ft else '-', ('%s/m%s' % gw.groups()) if gw else 'MISSING', ('%s/m%s' % cw.groups()) if cw else 'MISSING',
        ('%s/m%s' % rw.groups()) if rw else 'MISSING', lc.group(1) if lc else '-', fh, ('%s/%s/%s' % pv.groups()) if pv else '-', ex.group(0) if ex else ''))
    for k in ('guictrlmark_final', 'labgc2_final', 'guiclip_final'):
        m = re.search(r'DOS-PORT ' + k + r' (.*)', rm)
        if m: print('    %s %s' % (k, m.group(1).strip()))
