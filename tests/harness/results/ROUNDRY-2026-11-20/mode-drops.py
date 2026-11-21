#!/usr/bin/env python3
"""mode-drops.py RESULTS KERN -- RV's stick disconnects (kernel slice, usb 1-2) by cell phase, against the 486's own
mode changes (sdlports' question before RY's launch): the send reboot (run-hw's first job), the lock (RUN.BAT typed),
the game's exit to text mode (run-hw's text-mode wait trace: the first "changing" after "blind" past t+60 s, plus the
~3 s from the lock to the trace start), and the collect reboot (run-hw's last job). Read-only."""
import datetime, glob, os, re, sys
U = datetime.timezone.utc
R, K = sys.argv[1], sys.argv[2]
drops = [datetime.datetime.fromisoformat(m.group(1)).astimezone(U) for m in
         (re.match(r'^(\S+) \S+ kernel: usb 1-2: USB disconnect', l) for l in open(K)) if m]
cells = {}
for d in sorted(glob.glob(os.path.join(R, 'RV*-2026-11-19'))):
    dw = open(os.path.join(d, 'DRIVE-WALK.LOG')).read()
    out = open(os.path.join(d, 'run-hw.out'), errors='ignore').read()
    l = re.search(r"^(\S+) lock is run-hw", dw, re.M)
    t0 = datetime.datetime.fromisoformat('2026-11-19T' + l.group(1)).replace(tzinfo=U)
    sa = [datetime.datetime.fromtimestamp(float(x), U) for x in re.findall(r'"started_at": ([\d.]+)', out)]
    ex, prev = None, None
    for t, s in re.findall(r'^\s+t\+\s*([\d.]+)s\s+(\w+)', out, re.M):
        if float(t) > 60 and s == 'changing' and prev == 'blind':
            ex = t0 + datetime.timedelta(seconds=3 + float(t)); break
        prev = s
    cells[os.path.basename(d).split('-')[0]] = (sa[0], t0, ex, sa[-1])
n = {}
print('%-13s %-6s %-22s %9s %9s %9s %9s' % ('UTC', 'cell', 'phase', 'vs send', 'vs lock', 'vs exit', 'vs coll'))
for t in drops:
    c = [k for k, v in cells.items() if v[0] - datetime.timedelta(seconds=60) <= t <= v[3] + datetime.timedelta(seconds=240)]
    if not c:
        print('%s  between cells' % t.strftime('%T.%f')[:12]); n['between'] = n.get('between', 0) + 1; continue
    k = c[-1]; s, l0, ex, co = cells[k]
    ph = ('before send (DOS prompt)' if t < s else 'boot (send -> lock)' if t < l0 else
          'play (lock -> exit)' if ex and t < ex else 'after exit (-> collect)' if t < co else 'collect reboot')
    n[ph] = n.get(ph, 0) + 1
    f = lambda x: '%+9.1f' % (t - x).total_seconds() if x else '        ?'
    print('%s  %-6s %-24s %s %s %s %s' % (t.strftime('%T.%f')[:12], k, ph, f(s), f(l0), f(ex), f(co)))
print('by phase:', ', '.join('%s %d' % kv for kv in sorted(n.items(), key=lambda x: -x[1])), '; total', len(drops))
