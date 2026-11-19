#!/usr/bin/env python3
"""l1bana.py -- LAB-L1B reader: instruction counts from an L1B.EXE cell (DOSAGS_L1PROF=3).

    python3 -I l1bana.py CELL_DIR [--fn NAME ...] [--list] [--top N]

Prints, per tick (L1B's window ticks) for the seven per-tick template functions, each alone and together, and
for the whole VM:
  (a) instructions/tick, dispatch units/tick, the opcode histogram, the top 2- and 3-instruction sequences
      (opcode-only, with the dominant register form and the share that already ran inside one superinstruction);
  (b) script calls/returns per tick, activations, leaf activations (no script call made), ops per activation;
  (c) engine API calls per tick by function, and the getter timing loop (cycles per call at fixed 40000);
  --list: an annotated listing of each selected function's executed instructions, with executions per tick.
"""
import os, re, sys
from collections import defaultdict

W = '/home/claude/git/dosags-lab-l1'
REG = ['r0', 'sp', 'mar', 'ax', 'bx', 'cx', 'op', 'dx']
SEVEN = ['Extension', 'SetAlternativeAction', 'CheckTimers', 'GlobalCondition', 'IsOwnTimerExpired',
         'CheckDefaultAction', 'repeatedly_execute']
SUPER_LEN = {'S_farcall': 5}


def opnames():
    num = {}
    for l in open(W + '/vendor/ags/Common/script/cc_internal.h'):
        p = l.split()
        if len(p) >= 3 and p[0] == '#define' and p[1].startswith('SCMD_'):
            num[p[1]] = int(p[2])
    ops = {}
    for l in open(W + '/build/l1b/tools/ops.txt'):
        n, name, argc = l.split()
        ops[num[n]] = (name, int(argc))
    return ops


OPS = opnames()


def oname(op):
    return OPS.get(op, ('op%d' % op, 0))[0]


def fname(f):
    op = f & 127
    r1 = ((f >> 7) & 15) - 1
    r2 = ((f >> 11) & 15) - 1
    s = oname(op)
    regs = [REG[r] for r in (r1, r2) if r >= 0]
    return s + (' ' + ','.join(regs) if regs else '')


def load(d):
    t = open(os.path.join(d, 'L1PROF.TXT'), 'rb').read().decode('latin1').splitlines()
    R = dict(B={}, P=defaultdict(lambda: [0, 0]), O=defaultdict(int), U=defaultdict(int), A={}, W={}, C=defaultdict(int),
             G=[], S={}, F=defaultdict(list), X=defaultdict(dict), K=[], H={}, hdr={})
    for l in t:
        p = l.split(' ')
        k = p[0]
        if k == 'B':
            R['B'][int(p[1])] = (int(p[2]), int(p[3]), int(p[4]), ' '.join(p[5:]))
        elif k == 'P':
            R['P'][(int(p[1]), int(p[2]))] = [int(p[3]), int(p[4])]
        elif k == 'L1B':
            for kv in p[2:]:
                a, b = kv.split('=')
                R['hdr'][a] = int(b)
        elif k == 'H':
            R['H'][int(p[1])] = (p[2], int(p[3]), int(p[4]))
        elif k == 'O':
            R['O'][(int(p[1]), int(p[2]))] += int(p[3])
        elif k == 'U':
            R['U'][(int(p[1]), int(p[2]))] += int(p[3])
        elif k == 'A':
            R['A'][int(p[1])] = list(map(int, p[2:]))
        elif k == 'W':
            R['W'][int(p[1])] = (int(p[2]), int(p[3]))
        elif k == 'C':
            R['C'][(int(p[1]), int(p[2]))] += int(p[3])
        elif k == 'G':
            R['G'].append(tuple(map(int, p[1:8])))
        elif k == 'S':
            R['S'][int(p[1])] = (p[2], int(p[3]))
        elif k == 'F':
            R['F'][int(p[1])].append((int(p[2]), p[3]))
        elif k == 'X':
            R['X'][int(p[1])][int(p[2])] = (int(p[3]), ' '.join(p[4:]))
        elif k == 'K':
            R['K'].append(l)
    return R


def bname(R, b):
    return R['B'].get(b, (0, 0, 0, 'b%d' % b))[3]


def short(n):
    n = n.split('::')[-1] if '::' in n else n
    return n.split('$')[0]


def sel_buckets(R, names):
    out = {}
    for b, (cat, n, us, nm) in R['B'].items():
        if cat == 1 and nm.startswith('game::') and short(nm) in names:
            out[short(nm)] = b
    return out


def vm_buckets(R):
    return [b for b, v in R['B'].items() if v[0] == 1]


def main():
    a = sys.argv[1:]
    d = a[0]
    top = int(a[a.index('--top') + 1]) if '--top' in a else 20
    fns = [a[i + 1] for i, x in enumerate(a) if x == '--fn'] or SEVEN
    R = load(d)
    T = R['hdr']['ticks']
    hn = {h: v[0] for h, v in R['H'].items()}
    sb = sel_buckets(R, fns)
    allvm = vm_buckets(R)
    seven = [sb[f] for f in fns if f in sb]
    print('== %s  ticks=%d  groups=%d  gram_full=%d actover=%d' % (d, T, R['hdr']['groups'], R['hdr']['gram_full'],
                                                                   R['hdr']['actover']))
    att = sum(v[1] for v in R['H'].values())
    com = sum(v[2] for v in R['H'].values())
    print('superinstruction attempts %d commits %d (fallbacks %d)' % (att, com, att - com))

    def ops_of(bs):
        h = defaultdict(int)
        for (b, op), n in R['O'].items():
            if b in bs:
                h[op] += n
        return h

    def units_of(bs):
        h = defaultdict(int)
        for (b, hh), n in R['U'].items():
            if b in bs:
                h[hh] += n
        return h

    # (a) per function summary
    print('\n-- (a) instructions and dispatch units per tick')
    print('%-22s %9s %9s %7s %8s %9s %9s' % ('function', 'ops/tick', 'units/t', 'ops/u', 'fused%', 'VM-share', 'L1F-us/t'))
    vm_ops = sum(ops_of(allvm).values())
    groups = [(f, [sb[f]]) for f in fns if f in sb] + [('SEVEN', seven), ('ALL VM', allvm)]
    for f, bs in groups:
        o = sum(ops_of(bs).values())
        u = units_of(bs)
        un = sum(u.values())
        fused_ops = 0
        for hh, n in u.items():
            nm = hn.get(hh, '')
            if nm.startswith('S_'):
                fused_ops += n * SUPER_LEN.get(nm, 3)
        print('%-22s %9.1f %9.1f %7.2f %7.1f%% %8.1f%% %9s' % (f, o / T, un / T, o / un if un else 0,
                                                            100.0 * fused_ops / o if o else 0, 100.0 * o / vm_ops,
                                                            '%.1f' % (sum(R['B'][b][2] for b in bs) / T)))
    # opcode histograms
    print('\n-- (a) opcode histogram, ops/tick (share of the group)')
    for f, bs in [('SEVEN', seven)] + [(f, [sb[f]]) for f in fns if f in sb] + [('ALL VM', allvm)]:
        h = ops_of(bs)
        tot = sum(h.values())
        items = sorted(h.items(), key=lambda kv: -kv[1])
        print('%s (%.0f ops/tick): ' % (f, tot / T) + ', '.join('%s %.1f (%.1f%%)' % (oname(op), n / T, 100.0 * n / tot)
                                                               for op, n in items[:(18 if f in ('SEVEN', 'ALL VM') else 10)]))
    # dispatch units
    print('\n-- (a) dispatch units per tick by handler (SEVEN)')
    u = units_of(seven)
    tot = sum(u.values())
    print(', '.join('%s %.1f' % (hn.get(hh, hh), n / T) for hh, n in sorted(u.items(), key=lambda kv: -kv[1]) if n / T >= 0.5))
    # n-grams
    for nlen, flag in ((2, 0), (3, 1)):
        for f, bs in [('SEVEN', seven), ('ALL VM', allvm)] + ([(f, [sb[f]]) for f in fns if f in sb] if '--perfn' in a else []):
            ntop = top if f in ('SEVEN', 'ALL VM') else 8
            agg = defaultdict(lambda: [0, 0, defaultdict(int)])
            for b, fl, f1, f2, f3, n, nf in R['G']:
                if fl != flag or b not in bs:
                    continue
                key = (f1 & 127, f2 & 127) if flag == 0 else (f1 & 127, f2 & 127, f3 & 127)
                e = agg[key]
                e[0] += n
                e[1] += nf
                e[2][(f1, f2) if flag == 0 else (f1, f2, f3)] += n
            tot = sum(v[0] for v in agg.values())
            ops_tot = sum(ops_of(bs).values())
            print('\n-- (a) top %d %d-instruction sequences, %s (%.0f sequences/tick)' % (ntop, nlen, f, tot / T))
            print('%-4s %-34s %8s %7s %7s  %s' % ('#', 'opcodes', 'per tick', '% ops', 'fused', 'dominant form (share)'))
            for i, (k, (n, nf, forms)) in enumerate(sorted(agg.items(), key=lambda kv: -kv[1][0])[:ntop]):
                fk, fn_ = max(forms.items(), key=lambda kv: kv[1])
                print('%-4d %-34s %8.1f %6.1f%% %6.0f%%  %s (%.0f%%)' % (
                    i + 1, ' ; '.join(oname(x) for x in k), n / T, 100.0 * n / ops_tot, 100.0 * nf / n,
                    ' ; '.join(fname(x) for x in fk), 100.0 * fn_ / n))
    # (b) calls
    print('\n-- (b) script calls per tick, by callee (activations, leaf = made no script call)')
    print('%-24s %8s %8s %8s %8s %9s %9s %9s %8s' % ('callee', 'acts/t', 'entry/t', 'leaf/t', 'leaf0/t', 'ops/act',
                                                   'leafops/a', 'apis/act', 'calls/a'))
    tot_acts = tot_calls = tot_leaf = 0
    rows = []
    for b, v in R['A'].items():
        acts, leaf, leaf0, entries, unret, ops, leafops, apis, calls = v
        rows.append((acts, b, v))
    for acts, b, v in sorted(rows, reverse=True):
        acts, leaf, leaf0, entries, unret, ops, leafops, apis, calls = v
        tot_acts += acts - entries
        tot_leaf += (leaf - (entries if calls == 0 else 0))
        if acts / T < 0.05:
            continue
        print('%-24s %8.2f %8.2f %8.2f %8.2f %9.1f %9.1f %9.2f %8.2f' % (
            short(bname(R, b)), acts / T, entries / T, leaf / T, leaf0 / T, ops / acts if acts else 0,
            leafops / leaf if leaf else 0, apis / acts if acts else 0, calls / acts if acts else 0))
    ncall = sum(R['C'].values())
    print('script CALLs/tick (caller->callee pairs): %.2f; returns/tick (non-entry activations ended by ret): %.2f' % (
        ncall / T, tot_acts / T))
    print('caller -> callee per tick:')
    for (c, e), n in sorted(R['C'].items(), key=lambda kv: -kv[1]):
        if n / T >= 0.5:
            print('   %-24s -> %-24s %6.2f' % (short(bname(R, c)), short(bname(R, e)), n / T))
    # walks
    print('\n-- local-variable walks (mov sp,mar; subi mar,K): per tick and steps per walk')
    for f, bs in [(f, [sb[f]]) for f in fns if f in sb] + [('SEVEN', seven), ('ALL VM', allvm)]:
        n = sum(R['W'].get(b, (0, 0))[0] for b in bs)
        s = sum(R['W'].get(b, (0, 0))[1] for b in bs)
        print('   %-22s walks/tick %7.1f  steps/walk %5.2f' % (f, n / T, s / n if n else 0))
    # (c) API
    print('\n-- (c) engine API calls per tick from the per-tick functions (L1 P lines; us is probe-inflated)')
    api = defaultdict(lambda: [0, 0, defaultdict(int)])
    for (c, ab), (n, us) in R['P'].items():
        if R['B'].get(c, (0,))[0] != 1:
            continue
        e = api[bname(R, ab)]
        e[0] += n
        e[1] += us
        e[2][short(bname(R, c))] += n
    for nm, (n, us, callers) in sorted(api.items(), key=lambda kv: -kv[1][0]):
        if n / T < 0.2:
            continue
        print('   %-22s %7.2f/tick  callers: %s' % (nm, n / T, ', '.join('%s %.1f' % (k, v / T) for k, v in
                                                                         sorted(callers.items(), key=lambda kv: -kv[1])[:4])))
    print('   total API calls/tick from VM: %.1f' % (sum(v[0] for v in api.values()) / T))
    print('\n-- (c) getter timing loop (cycles per call at fixed 40000 = c - loop; e = an empty noinline call of the same signature)')
    for l in R['K']:
        m = re.findall(r' c\d=(\d+) e\d=(\d+)', l)
        if not m:
            continue
        cs = [int(x) / 1000.0 for x, _ in m]
        es = [int(y) / 1000.0 for _, y in m]
        print('   %s  -> cycles/call %s, empty call %s' % (l.split(' samples')[0], '/'.join('%.0f' % c for c in cs),
                                                          '/'.join('%.0f' % e for e in es)))
    if '--list' in a:
        listing(R, fns, T)


def listing(R, fns, T):
    # find the global script table: the S whose F list holds repeatedly_execute
    for sid, fl in R['F'].items():
        if any(n.startswith('repeatedly_execute') for _, n in fl):
            break
    else:
        return
    fl = sorted(R['F'][sid])
    X = R['X'][sid]
    for i, (addr, nm) in enumerate(fl):
        if nm.split('$')[0] not in fns:
            continue
        end = fl[i + 1][0] if i + 1 < len(fl) else 1 << 30
        print('\n== listing %s @%d' % (nm, addr))
        for pc in sorted(p for p in X if addr <= p < end):
            n, desc = X[pc]
            p = desc.split(' ')
            op, argc = int(p[0]), int(p[1])
            args = p[2:]
            regmask = []
            s = []
            for k, x in enumerate(args):
                s.append(x)
            print('%7d %8.2f  %-12s %s' % (pc, n / T, oname(op), ' '.join(s)))


if __name__ == '__main__':
    main()
