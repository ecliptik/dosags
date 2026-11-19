#!/usr/bin/env python3
"""fhcmp.py REF ARM... (each a cell dir holding FHASH.TXT, or a <cell>.FHASH.TXT file) -- compare FHASH.TXT (loop counter, FNV-1a of the composited virtual screen) by loop counter.
A loop counter rendered more than once (catch-up re-renders, fades) is compared on its LAST record in each arm."""
import sys, os
def load(d):
    h = {}
    n = 0
    for line in open(d if os.path.isfile(d) else os.path.join(d, 'FHASH.TXT')):
        lc, v = line.split(); h[int(lc)] = v; n += 1
    return h, n
ref, rn = load(sys.argv[1])
print('%s: %d records, %d loop counters' % (sys.argv[1], rn, len(ref)))
for d in sys.argv[2:]:
    a, an = load(d)
    common = sorted(set(ref) & set(a))
    diff = [lc for lc in common if ref[lc] != a[lc]]
    print('%s: %d records, common lc %d, EQUAL %d, DIFF %d%s' % (d, an, len(common), len(common) - len(diff), len(diff),
          (', first diff lc %d, last %d' % (diff[0], diff[-1])) if diff else ''))
