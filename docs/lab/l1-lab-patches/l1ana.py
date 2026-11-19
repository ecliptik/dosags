#!/usr/bin/env python3
# LAB-L1 reader: l1ana.py RESULTDIR [--lo LC] [--hi LC] [--pad 40]
# Reads L1PROF.TXT (entries; level-2 buckets), STDOUT.TXT (witness lines, labclick lines), TICKS.BIN (dequeued
# clicks/keys, room entries), RUNMANI.LOG (tickstats script_vm, rep_exec_vm). ASCII output.
import sys, os, re, struct, argparse, collections

ap = argparse.ArgumentParser()
ap.add_argument('d')
ap.add_argument('--lo', type=int, default=None)
ap.add_argument('--hi', type=int, default=None)
ap.add_argument('--pad', type=int, default=40)
ap.add_argument('--top', type=int, default=25)
a = ap.parse_args()
D = a.d

def rd(name):
    p = os.path.join(D, name)
    return open(p, 'rb').read().decode('latin-1') if os.path.exists(p) else ''

out = []
def P(s=''):
    out.append(s)

# ---- witnesses
so = rd('STDOUT.TXT')
ft = 'fixed-timestep: ENABLED' in so
m = re.search(r'DOS-PORT guiclip DOSAGS_GUI_CLIP=(\S+) mode=(\d)', so)
gc = m.group(2) if m else None
m = re.search(r'DOS-PORT l1prof level=(\d+)', so)
lvl = int(m.group(1)) if m else 0
cell = rd('CELL.txt').strip()
runbat = rd('RUN.BAT')
setbytes = sum(len(l) + 2 for l in runbat.splitlines() if l.upper().startswith('SET '))
P('== %s' % os.path.basename(D.rstrip('/')))
P('cell: %s' % cell[:200])
P('witness: fixed-timestep ENABLED=%s guiclip mode=%s l1prof level=%d RUN.BAT SET bytes=%d' % (ft, gc, lvl, setbytes))
rm = rd('RUNMANI.LOG')
ts = {}
for k in ('script_vm', 'rep_exec_vm', 'process_events_dispatch', 'update_game_once_total'):
    m = re.search(r'tickstats_%s calls=(\d+) .*total_us=(\d+)' % k, rm)
    if m:
        ts[k] = (int(m.group(1)), int(m.group(2)))

# ---- inputs
clicks = []   # (lc, kind)
for m in re.finditer(r'DOS-PORT labclick lc=(\d+) n=\d+ x=(-?\d+) y=(-?\d+) click=(\d)', so):
    clicks.append((int(m.group(1)), 'labclick' if m.group(4) == '1' else 'labmove'))
rooms = []
tb = os.path.join(D, 'TICKS.BIN')
deq = []
if os.path.exists(tb):
    b = open(tb, 'rb').read()
    n = struct.unpack_from('<5I', b, 0)[2]
    for i in range(n):
        lc, v = struct.unpack_from('<2I', b, 20 + 8 * i)
        kind, val = v >> 28, v & 0x0FFFFFFF
        if kind == 4:
            rooms.append((lc, val))
        elif kind in (5, 6):
            deq.append((lc, 'click' if kind == 5 else 'key'))
inputs = sorted(set([c[0] for c in clicks] + [d[0] for d in deq]))
P('inputs: labclick/labmove %d (%s); dequeued click/key %d (%s); rooms %s' % (
    len(clicks), ' '.join('%d%s' % (c[0], '' if c[1] == 'labclick' else 'm') for c in clicks), len(deq),
    ' '.join(str(d[0]) for d in deq), rooms))

# ---- L1PROF
names = {}
ents = []
buckets = []
pairs = []
hdr = ''
neg = [0]
for line in rd('L1PROF.TXT').splitlines():
    if line.startswith('L1PROF'):
        hdr = line
    elif line.startswith('N '):
        _, i, s = line.split(' ', 2)
        names[int(i)] = s
    elif line.startswith('E '):
        f = line.split()
        v = list(map(int, f[1:])) + [0]
        kind, lc0, lc1, depth, name, evt, evsub, evroom, us, nest, vm, api, oth, apin, pr = v[:15]
        if us >= 0x80000000:   # a negative uclock difference stored unsigned (uclock is not monotonic): clamp, as tickstats does
            us = 0; neg[0] += 1
        ents.append(dict(kind=kind, lc0=lc0, lc1=lc1, depth=depth, name=names.get(name, '?%d' % name), evt=evt,
                         evsub=evsub, evroom=evroom, us=us, nest=nest, vm=vm, api=api, oth=oth, apin=apin, pr=pr))
    elif line.startswith('B '):
        f = line.split(' ', 5)
        buckets.append(dict(id=int(f[1]), cat=int(f[2]), n=int(f[3]), us=int(f[4]), name=f[5]))
    elif line.startswith('P '):
        f = line.split()
        pairs.append(tuple(map(int, f[1:])))
P('L1PROF: %s' % hdr)
P('entries with a negative uclock difference (clamped to 0): %d' % neg[0])
if not ents:
    print('\n'.join(out)); sys.exit(0)

if not rooms:   # no TICKS.BIN: room entries from the entries' room labels
    prev = None
    for e in ents:
        m = re.match(r'room(\d+)\|', e['name'])
        if m and m.group(1) != prev:
            rooms.append((e['lc0'], int(m.group(1)))); prev = m.group(1)
    P('rooms (from entry labels): %s' % rooms)
fine = ts.get('script_vm', (0, 0))[0] > 0
P('witness: fine timing ON (script_vm recorded, i.e. the last SET DOSAGS_TICKSTATS_FINE survived) = %s' % fine)
first_play = min(e['lc0'] for e in ents if e['name'].endswith('|repeatedly_execute'))
lo = a.lo if a.lo is not None else first_play
last = max(e['lc0'] for e in ents)
hi = a.hi if a.hi is not None else last + 1
nt = hi - lo
P('window: loop ticks %d <= lc < %d (%d ticks); first repeatedly_execute at %d' % (lo, hi, nt, first_play))

EVT = {1: 'script', 2: 'object', 3: 'fadein', 4: 'gui', 0: 'newroom', -1: 'none'}
TS = {1: 'rep_exec', 2: 'key', 3: 'mouse_click', 4: 'text_input'}
OBJ = {0: 'hotspot', 1: 'room', 2: 'region', 3: 'object', 4: 'character', 5: 'inventory'}

def eclass(e):
    nm = e['name'].split('|', 1)[1]
    if e['kind'] == 1:
        return 'per-tick', 'rep_exec_vm:' + nm
    if nm == 'repeatedly_execute':
        return 'per-tick', 'repeatedly_execute'
    if e['evt'] == 2 and e['evsub'] == 1 and e['evroom'] == 6:
        return 'per-tick', 'room rep_exec (' + e['name'] + ')'
    if nm in ('repeatedly_execute_always', 'late_repeatedly_execute_always'):
        return 'per-tick', nm
    if e['evt'] == 1:
        ctx = 'event ' + TS.get(e['evsub'], str(e['evsub']))
    elif e['evt'] == 2:
        ctx = 'interaction ' + OBJ.get(e['evsub'], str(e['evsub'])) + ('' if e['evroom'] < 0 else ' ev%d' % e['evroom'])
    elif e['evt'] == 4:
        ctx = 'gui'
    else:
        ctx = EVT.get(e['evt'], str(e['evt']))
    if 'dialog' in e['name']:
        ctx = 'dialog'
    return 'event', ctx + ': ' + e['name']

W = [e for e in ents if lo <= e['lc0'] < hi]
sv = [e for e in W if e['kind'] == 0]           # script_vm entries (RunScriptFunction)
sv0 = [e for e in sv if e['depth'] == 0]        # top level only (nested ones are inside an outer bracket)
tot = sum(e['us'] for e in sv)
tot0 = sum(e['us'] for e in sv0)
P()
P('-- script_vm (RunScriptFunction) entries in the window: %d (%.3f/tick), %d nested; sum us %d (top level %d) = %.3f ms/tick'
  % (len(sv), len(sv) / nt, len(sv) - len(sv0), tot, tot0, tot0 / 1000.0 / nt))
if 'script_vm' in ts:
    c, u = ts['script_vm']
    allsv = sum(e['us'] for e in ents if e['kind'] == 0)
    P('   tickstats script_vm whole run: calls %d total_us %d; L1 entries whole run: %d, us %d (ratio %.4f)'
      % (c, u, sum(1 for e in ents if e['kind'] == 0), allsv, allsv / u if u else 0))
if 'rep_exec_vm' in ts:
    P('   tickstats rep_exec_vm whole run: calls %d total_us %d' % ts['rep_exec_vm'])

# per entry point table
agg = collections.OrderedDict()
for e in sv0:
    cl, key = eclass(e)
    k = (cl, key)
    if k not in agg:
        agg[k] = [0, 0, 0, 0, 0, 0, 0]
    r = agg[k]
    r[0] += 1; r[1] += e['us']; r[2] += e['nest']; r[3] += e['vm']; r[4] += e['api']; r[5] += e['oth']; r[6] += e['apin']
P()
P('-- script_vm by entry point (top level), window')
P('%-9s %-58s %7s %10s %8s %7s %9s %s' % ('class', 'entry point', 'n', 'us', 'ms/tick', 'share', 'nest_us', '(l2: vm/api/oth us, api calls)'))
pt = 0
for (cl, key), r in sorted(agg.items(), key=lambda kv: -kv[1][1]):
    if cl == 'per-tick':
        pt += r[1]
    P('%-9s %-58s %7d %10d %8.3f %6.2f%% %9d %s' % (cl, key[:58], r[0], r[1], r[1] / 1000.0 / nt, 100.0 * r[1] / tot0 if tot0 else 0,
      r[2], ('%d/%d/%d, %d' % (r[3], r[4], r[5], r[6])) if lvl >= 2 else ''))
P1 = pt / tot0 if tot0 else 0
P('P1 per-tick entries share of script_vm (top level): %.2f%%   [MET if >= 95%%, FALSIFIED if < 90%%]' % (100 * P1))
nest_tot = sum(r[2] for r in agg.values())
P('   of which time in game loops nested inside entries (blocking): %d us = %.2f%% of script_vm' % (nest_tot, 100.0 * nest_tot / tot0 if tot0 else 0))
ptx = sum(r[1] - r[2] for (cl, k), r in agg.items() if cl == 'per-tick')
P('   P1 excluding nested game loops from both sides: %.2f%%' % (100.0 * ptx / (tot0 - nest_tot) if tot0 > nest_tot else 0))

# ---- tick classes (P2)
per = collections.defaultdict(int)
pertick_only = collections.defaultdict(int)
for e in sv0:
    per[e['lc0']] += e['us']
    if eclass(e)[0] == 'per-tick':
        pertick_only[e['lc0']] += e['us']
import bisect
def near(lc):
    i = bisect.bisect_left(inputs, lc - a.pad)
    return i < len(inputs) and inputs[i] <= lc + a.pad
roomlc = [r[0] for r in rooms]
def nearroom(lc):
    return any(abs(lc - r) <= a.pad for r in roomlc)
ticks = list(range(lo, hi))
free = [t for t in ticks if not near(t)]
busy = [t for t in ticks if near(t)]
free_nr = [t for t in free if not nearroom(t)]
def mean(ts_, d):
    return sum(d.get(t, 0) for t in ts_) / len(ts_) / 1000.0 if ts_ else float('nan')
m_all = mean(ticks, per); m_free = mean(free, per); m_busy = mean(busy, per)
P()
P('-- tick classes (input = labclick/labmove/dequeued click or key; input-free = none within +-%d ticks)' % a.pad)
P('%-34s %7s %12s %14s' % ('class', 'ticks', 'script_vm ms', 'per-tick-only'))
for lab, tl in (('all ticks', ticks), ('input-free', free), ('input within +-%d' % a.pad, busy),
                ('input-free, no room entry +-%d' % a.pad, free_nr)):
    P('%-34s %7d %12.3f %14.3f' % (lab, len(tl), mean(tl, per), mean(tl, pertick_only)))
if ticks and free:
    P('P2 input-free / all-tick mean: %.4f (%.2f%%)   [MET if within +-10%%, FALSIFIED if input-free > 15%% lower]'
      % (m_free / m_all, 100 * (m_free / m_all - 1)))
    if busy:
        P('   input-near / all-tick mean: %.4f' % (m_busy / m_all))

# entry point x tick class matrix (ms/tick within each class)
fset = set(free); bset = set(busy)
mat = collections.OrderedDict()
for e in sv0:
    k = eclass(e)[1]
    r = mat.setdefault(k, [0, 0, 0, 0])
    if e['lc0'] in fset: r[0] += e['us']; r[2] += 1
    elif e['lc0'] in bset: r[1] += e['us']; r[3] += 1
P()
P('-- script_vm per entry point x tick class (ms per tick of the class; n entries)')
P('%-58s %14s %14s' % ('entry point', 'input-free', 'input +-%d' % a.pad))
for k, r in sorted(mat.items(), key=lambda kv: -(kv[1][0] + kv[1][1])):
    P('%-58s %8.3f %5d %8.3f %5d' % (k[:58], r[0] / 1000.0 / max(1, len(free)), r[2], r[1] / 1000.0 / max(1, len(busy)), r[3]))
tf = sum(r[0] for r in mat.values()); tb_ = sum(r[1] for r in mat.values())
P('%-58s %8.3f %5s %8.3f' % ('total', tf / 1000.0 / max(1, len(free)), '', tb_ / 1000.0 / max(1, len(busy))))

# per-tick script_vm distribution
vals = sorted(per.get(t, 0) / 1000.0 for t in ticks)
if vals:
    q = lambda p: vals[min(len(vals) - 1, int(p * len(vals)))]
    P('   per-tick script_vm ms: p05 %.3f p50 %.3f p95 %.3f max %.3f' % (q(0.05), q(0.5), q(0.95), vals[-1]))
big = sorted(((per[t], t) for t in ticks if per.get(t, 0) > 0), reverse=True)[:8]
P('   largest ticks (us@lc): ' + ' '.join('%d@%d' % (u, t) for u, t in big))

# ---- level 2: buckets
if lvl >= 2 and buckets:
    ntw = hi - lo
    # buckets are whole-run; per tick over the whole run's played ticks
    allticks = last + 1 - first_play
    cat = collections.defaultdict(int)
    for b in buckets:
        cat[b['cat']] += b['us']
    vmapi = cat[1] + cat[2]
    P()
    P('-- level 2 (whole run, %d played ticks; buckets are exclusive emulated time, rdtsc)' % allticks)
    P('   VM (script functions) %d us = %.3f ms/tick; engine API %d us = %.3f ms/tick; nested game loops %d us; VM share of VM+API %.1f%%'
      % (cat[1], cat[1] / 1000.0 / allticks, cat[2], cat[2] / 1000.0 / allticks, cat[3], 100.0 * cat[1] / vmapi if vmapi else 0))
    m = re.search(r'c_switch_x1000=(\d+)', hdr); csw = int(m.group(1)) / 1000.0 / 40.0 if m else 0
    nsw = sum(b['n'] for b in buckets if b['cat'] in (1, 2))
    P('   switches into VM/API buckets: %d (%.1f/tick); calibrated switch cost %.3f us -> %.3f ms/tick of probe cost in these buckets'
      % (nsw, nsw / allticks, csw, nsw * csw / 1000.0 / allticks))
    api_n = int(re.search(r'api_n=(\d+)', hdr).group(1))
    P('   engine API calls from scripts: %d = %.1f/tick' % (api_n, api_n / allticks))
    P()
    P('   top script functions (exclusive VM time)')
    P('   %-48s %9s %8s %10s %8s %7s' % ('function', 'entries', 'n/tick', 'us', 'ms/tick', 'of VM'))
    for b in sorted([b for b in buckets if b['cat'] == 1], key=lambda b: -b['us'])[:a.top]:
        P('   %-48s %9d %8.2f %10d %8.3f %6.2f%%' % (b['name'][:48], b['n'], b['n'] / allticks, b['us'], b['us'] / 1000.0 / allticks,
          100.0 * b['us'] / cat[1] if cat[1] else 0))
    P()
    P('   engine API functions called from scripts (exclusive time; n = calls)')
    P('   %-48s %9s %8s %10s %8s %7s %9s' % ('API', 'calls', 'n/tick', 'us', 'ms/tick', 'of API', 'of VM+API'))
    for b in sorted([b for b in buckets if b['cat'] == 2], key=lambda b: -b['us'])[:a.top]:
        P('   %-48s %9d %8.2f %10d %8.3f %6.2f%% %8.2f%%' % (b['name'][:48], b['n'], b['n'] / allticks, b['us'], b['us'] / 1000.0 / allticks,
          100.0 * b['us'] / cat[2] if cat[2] else 0, 100.0 * b['us'] / vmapi if vmapi else 0))
    bn = {b['id']: b['name'] for b in buckets}
    P()
    P('   top (caller function -> API) pairs by inclusive time')
    for c, ap_, n, us in sorted(pairs, key=lambda p: -p[3])[:a.top]:
        P('   %-40s -> %-30s %8d %7.2f/tick %9d us %7.3f ms/tick' % (bn.get(c, '?%d' % c)[:40], bn.get(ap_, '?%d' % ap_)[:30], n, n / allticks, us,
          us / 1000.0 / allticks))
    # per-tick entry: vm/api/oth split per class
    P()
    for cl in ('per-tick', 'event'):
        es = [e for e in sv0 if eclass(e)[0] == cl]
        s = lambda k: sum(e[k] for e in es)
        if es:
            P('   %-8s entries: us %d = vm %d + api %d + outside-VM %d + probe %d + nested loops %d (gap %d); api calls %d'
              % (cl, s('us'), s('vm'), s('api'), s('oth'), s('pr'), s('nest'), s('us') - s('vm') - s('api') - s('oth') - s('pr') - s('nest'), s('apin')))
print('\n'.join(out))
