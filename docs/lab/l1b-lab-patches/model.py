#!/usr/bin/env python3
"""LAB-L1B cost model: per-unit x86 instruction counts read from the -S of the timing build's DosVmLoop
(build/l1b/s/vm.s; DOSBox-X normal core ~1 cycle per instruction), weighted by L1B's dispatch counts.
model.py CELL_DIR"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l1bana as A
# per-unit hot-path instructions incl. dispatch (see LAB-L1B.md section 3)
C = dict(linenum=8, mov=14, movl_int=10, movl_gvar=11, movl_str=11, movl_imp=47, push=33, pop=26, jz=8, jnz=8,
         jmp=12, addreg=8, subreg=8, muli=8, mulreg=10, isequal=15, notequal=15, greater=12, lessthan=12, gte=12, lte=12,
         bitand=10, bitor=10, xorreg=10, **{'and': 15, 'or': 15},
         thisaddr=7, setfuncargs=5, farpush=24, farsubsp=17, addi=32, subi=30, memread=25, memwrite=25, call=92, ret=55,
         callext=115, generic=110, STEPPER=110, checkbounds=8, checknull=6, checknullreg=6,
         S_farcall=165, S_localload=46, S_localstore=48, S_pushmovlpop=36, S_popsubmov=38, S_popaddmov=38,
         S_popeqmov=36, S_popgtemov=33, S_eqjz=24, S_nejz=24, S_gtjz=19, S_ltjz=19, S_gtejz=19, S_ltejz=19)
WALK = 6   # per step of the local-variable walk (localload/localstore/subi on MAR)
def model(R, bs, T):
    hn = {h: v[0] for h, v in R['H'].items()}
    tot = 0.0; parts = {}
    for (b, h), n in R['U'].items():
        if b not in bs: continue
        nm = hn.get(h, '?')
        c = C.get(nm, 30) * n
        parts[nm] = parts.get(nm, 0) + c
        tot += c
    ws = sum(R['W'].get(b, (0, 0))[1] for b in bs)
    parts['walk steps'] = WALK * ws
    tot += WALK * ws
    return tot / T, {k: v / T for k, v in parts.items()}
if __name__ == '__main__':
    R = A.load(sys.argv[1]); T = R['hdr']['ticks']
    sb = A.sel_buckets(R, A.SEVEN); seven = list(sb.values()); allvm = A.vm_buckets(R)
    print('%-22s %10s %9s %10s' % ('function', 'model cyc/t', 'model ms', 'L1F ms raw'))
    for f in A.SEVEN + ['SEVEN', 'ALL VM']:
        bs = [sb[f]] if f in sb else (seven if f == 'SEVEN' else allvm)
        m, _ = model(R, bs, T)
        print('%-22s %10.0f %9.3f' % (f, m, m / 40000.0))
    m, parts = model(R, seven, T)
    print('\nSEVEN by handler (cycles/tick, share of model):')
    for k, v in sorted(parts.items(), key=lambda kv: -kv[1]):
        if v / m >= 0.005: print('   %-16s %8.0f %5.1f%%' % (k, v, 100 * v / m))
