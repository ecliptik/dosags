#!/usr/bin/env python3
"""ckwin3.py CELL_DIR|LABCK.TXT... -- per-window ms per render pass from the R3LAND overlay's checkpoints
(DOS-PORT labck lc= rbspr_us= rbspr_calls= rts_us= rts_calls=). Window (A, B]: totals at B minus totals at A;
passes = render_to_screen_pertick calls in the window. Windows are LAB-R3's fixture-V windows."""
import os, re, sys
WIN = [('E pointer in room', 7100, 7400), ('H1 still on a verb', 7500, 7800), ('H3 still, bar middle', 8300, 8600),
       ('H4 still, lower portrait', 8700, 9000), ('H5 moving over verbs', 9000, 9300)]
def load(p):
    if os.path.isdir(p): p = os.path.join(p, 'STDOUT.TXT')
    ck = {}
    for m in re.finditer(r'labck lc=(\d+) rbspr_us=(\d+) rbspr_calls=(\d+) rts_us=(\d+) rts_calls=(\d+)',
                         open(p, 'rb').read().decode('latin1')):
        ck[int(m.group(1))] = tuple(int(x) for x in m.groups()[1:])
    return ck
cells = [(a, load(a)) for a in sys.argv[1:]]
print('%-38s' % 'window' + ''.join('%30s' % os.path.basename(a.rstrip('/')) for a, _ in cells))
print('%-38s' % '' + ''.join('%30s' % 'rb_sprite  render_to_screen  n' for _ in cells))
for name, a, b in WIN:
    row = '%-38s' % ('%s %d-%d' % (name, a, b))
    for _, ck in cells:
        if a not in ck or b not in ck: row += '%30s' % 'n/a'; continue
        d = [ck[b][i] - ck[a][i] for i in range(4)]
        n = d[3]
        row += '%30s' % ('%.3f  %.3f  %d' % (d[0] / 1000.0 / n, d[2] / 1000.0 / n, n) if n else 'n=0')
    print(row)
