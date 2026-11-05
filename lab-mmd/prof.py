#!/usr/bin/env python3
"""LAB-MMD 22 probe 0306 profile reader.
prof.py RESULT_DIR EXE CCI_G_OBJ CC_INSTANCE_CPP [tick_lo tick_hi]
PROF.BIN (ver 3): 8 x u32 header (magic 'PROF', ver, hz, rtc_ticks, n, other, dropped, n_tickmarks),
then n_tickmarks x u32 (sample count at each loop tick), then n x u32 samples: EIP in bits 0-28 (EIP 1 =
not in PM app code), bit 31 script event, bit 30 inside update_game_once, bit 29 inside render/scene.
Functions by nm of EXE; inside ccInstance::Run, by addr2line -i on the -g object (its .text proven identical
to the linked object's), outermost cc_instance.cpp line -> the enclosing `case SCMD_*:` block, or 'head'."""
import os, re, struct, subprocess, sys, bisect, collections
T = os.path.expanduser('~/git/dosags-lab-mmd/tools/djgpp/bin/i586-pc-msdosdjgpp-')
d, exe, gobj, src = sys.argv[1:5]
lo_t, hi_t = (int(sys.argv[5]), int(sys.argv[6])) if len(sys.argv) > 6 else (200, 1000)
raw = open(os.path.join(d, 'PROF.BIN'), 'rb').read()
magic, ver, hz, rtc, n, other, dropped, nt = struct.unpack_from('<8I', raw, 0)
assert magic == 0x464F5250, 'bad magic'
marks = struct.unpack_from('<%dI' % nt, raw, 32)
samp = struct.unpack_from('<%dI' % n, raw, 32 + 4 * nt)
s0 = marks[lo_t] if lo_t < nt else 0
s1 = marks[hi_t] if hi_t < nt else n
win = samp[s0:s1]
print(f'hz={hz} rtc_ticks={rtc} pm_samples={n} other={other} dropped={dropped} tickmarks={nt}')
print(f'identity rtc == samples + dropped: {rtc} vs {n + dropped}  {"OK" if rtc == n + dropped else "MISMATCH"}')
print(f'window ticks {lo_t}-{hi_t}: samples {len(win)}')
# symbols
syms = []
for l in subprocess.run([T + 'nm', '-n', exe], capture_output=True, text=True).stdout.splitlines():
    p = l.split()
    if len(p) == 3 and p[1] in 'Tt': syms.append((int(p[0], 16), p[2]))
addrs = [a for a, _ in syms]
hdr = subprocess.run([T + 'objdump', '-h', exe], capture_output=True, text=True).stdout
m = re.search(r'\.text\s+([0-9a-f]+)\s+([0-9a-f]+)', hdr); tsz, tva = int(m.group(1), 16), int(m.group(2), 16)
bad = [e for e in win if (e & 0x1FFFFFFF) != 1 and not (tva <= (e & 0x1FFFFFFF) < tva + tsz)]
print(f'.text [{tva:#x},{tva+tsz:#x}): samples outside = {len(bad)}  {"OK" if not bad else "VOID"}')
def fn(e):
    i = bisect.bisect_right(addrs, e) - 1
    return syms[i] if i >= 0 else (0, '?')
run_exe = [a for a, s in syms if s == '__ZN10ccInstance3RunEl'][0]
run_obj = int([l.split()[0] for l in subprocess.run([T + 'nm', gobj], capture_output=True, text=True).stdout.splitlines() if l.endswith(' __ZN10ccInstance3RunEl')][0], 16)
# case blocks of Run in the source
lines = open(src).read().split('\n')
rs = next(i for i, l in enumerate(lines) if l.startswith('ccInstError ccInstance::Run('))
re_ = next(i for i in range(rs + 1, len(lines)) if lines[i] == '}')
sw = next(i for i in range(rs, re_) if re.match(r'\s+switch \(op_code\)', lines[i]))
cases = [(i + 1, m.group(1)) for i in range(sw, re_) for m in [re.match(r'\s+case (SCMD_\w+):', lines[i])] if m]
case_lines = [c[0] for c in cases]
def block(line):
    if line < rs + 1 or line > re_ + 1: return 'Run:other'
    if line <= sw + 1: return 'Run:head/prologue'
    i = bisect.bisect_right(case_lines, line) - 1
    return 'Run:' + (cases[i][1] if i >= 0 else 'switch')
run_offs = sorted({(e & 0x1FFFFFFF) - run_exe + run_obj for e in win if (e & 0x1FFFFFFF) != 1 and fn(e & 0x1FFFFFFF)[1] == '__ZN10ccInstance3RunEl'})
loc = {}
if run_offs:
    out = subprocess.run([T + 'addr2line', '-a', '-i', '-e', gobj, '-j', '.text'] + ['%#x' % o for o in run_offs],
                         capture_output=True, text=True).stdout.splitlines()
    cur = None; chain = {}
    for x in out:
        if x.startswith('0x'): cur = int(x, 16); chain[cur] = []
        elif cur is not None: chain[cur].append(x)
    for o in run_offs:
        cl = [int(x.rsplit(':', 1)[1].split()[0]) for x in chain.get(o, []) if 'cc_instance.cpp:' in x and x.rsplit(':', 1)[1].split()[0].isdigit()]
        loc[o] = block(cl[-1]) if cl else 'Run:?'
def key(e):
    a = e & 0x1FFFFFFF
    if a == 1: return 'NOT-IN-PM-APP-CODE'
    f = fn(a)[1]
    return loc.get(a - run_exe + run_obj, 'Run:?') if f == '__ZN10ccInstance3RunEl' else f
def bucket(e):
    s_, u_, r_ = e >> 31 & 1, e >> 30 & 1, e >> 29 & 1
    if r_: return 'render/scene'
    if s_: return 'script event'
    if u_: return 'logic, non-script'
    return 'outside update_game_once'
by = collections.defaultdict(collections.Counter)
for e in win: by[bucket(e)][key(e)] += 1
tot = len(win)
print('\nBUCKETS (share of window samples):')
for b_ in ('script event', 'logic, non-script', 'render/scene', 'outside update_game_once'):
    c = by[b_]; t = sum(c.values())
    print(f'  {b_:26s} {t:8d}  {100.0*t/max(tot,1):6.2f}%   not-in-PM {100.0*c["NOT-IN-PM-APP-CODE"]/max(t,1):5.1f}%')
for b_ in ('logic, non-script', 'script event', 'render/scene'):
    c = by[b_]; t = sum(c.values())
    print(f'\nTOP 25 in "{b_}" ({t} samples):')
    cum = 0
    for i, (k, v) in enumerate(c.most_common(25)):
        cum += v
        print(f'  {100.0*v/max(t,1):6.2f}%  cum {100.0*cum/max(t,1):6.2f}%  {v:7d}  {k}')
    top15 = sum(v for k, v in c.most_common(15) if k not in ('?',))
    print(f'  -> top-15 named cover {100.0*top15/max(t,1):.1f}% of "{b_}"')
rt = collections.Counter()
for e in win:
    k = key(e)
    if k.startswith('Run:'): rt[k] += 1
print(f'\nInside Run ({sum(rt.values())} samples) by block:')
for k, v in rt.most_common(): print(f'  {100.0*v/max(sum(rt.values()),1):6.2f}%  {v:7d}  {k}')
