# VM slice 3 -- superinstructions -- REPORT

## 0. PRE-REGISTRATION of the fixed-40000 timing bands (written 2026-11-06T03:00:35Z, BEFORE any slice-3 timing run)

Binary AGSVM4 (instrumented, build/ags/ags.exe with slice 3); cell build/vmlab/cell.sh mmdcs (MMD character select,
1000 ticks, fixed 40000, --fixed-timestep). Measure: script event ms/tick (evtype script us / n). One binary, arms by env.
Reference: slice-2 fast 5.124 ms/tick (TF4-MMDCS, AGSVM3); legacy ~9.31.
Dynamic counts per tick from the witness runs (W3B*/W3F, fz=): farcall 170, localload 387, localstore 19,
pushmovlpop 171, popbinmov 114 (277 alone), cmpmovjz 129 (180 alone).
Saving per execution (hand count against the slice-2 singles' -S paths): farcall 60-75 (4 dispatches, the fcs reloads,
the type chain, the DirectPtr call skipped for plain ints), localload ~27, localstore ~27, pushmovlpop ~24,
popbinmov ~12, cmpmovjz ~13; the division fixes (farsubsp's size check and PopCount, movl's import lookup) ~16 + ~10.

| arm (DOSAGS_VM=fast, DOSAGS_VM_FUSE=) | predicted change vs FUSE=0 | band (ms/tick) |
|---|---|---|
| 0 (division fixes only) vs slice-2 5.124 | -0.03 to -0.15 | 4.97-5.09 |
| 1 farcall | -0.15 to -0.45 | |
| 2 localload | -0.12 to -0.40 | |
| 4 localstore | 0 to -0.05 | |
| 8 pushmovlpop | -0.04 to -0.16 | |
| 16 popbinmov | -0.02 to -0.14 | |
| 32 cmpmovjz | -0.01 to -0.10 | |
| 0x3F all (the default) | central -0.71 | **4.05-4.75** |
| legacy (DOSAGS_VM unset) | | 9.20-9.35 |

Falsifier: the all-fused arm outside 4.05-4.75, or a single superop's change outside its band in the wrong direction
(slower than FUSE=0) -- that superop is dropped (its code costs cache on the 486 for nothing).

## 1. What slice 3 adds (vm-slice3.diff; supersedes vm-slice2b.diff)
- Six superinstructions, chosen from MMD's mix, each behind a DOSAGS_VM_FUSE bit (default all in DOSAGS_VM=fast;
  none in fastnofuse/fastgeneric), installed by a fusion pass after decode in the opcode slot of the group's first
  instruction (every constituent keeps its single handler): farcall (farpush ax; setfuncargs N; movl ax,IMPORT; farcall ax;
  farsubsp M), localload / localstore (mov sp,mar; subi mar,K; memread4|memwrite4 R), pushmovlpop (push ax; movl ax,L;
  pop bx), popbinmov (pop bx; sub|add|cmpeq|gte bx,ax; mov bx,ax), cmpmovjz (cmpeq|cmpne|gt|lt|gte|lte bx,ax; mov bx,ax;
  jzi). Check-then-commit: a failed precondition leaves through h_generic before any state changes.
- The two constant divisions removed: the import lookup (SystemImports::GetByIndexFast, byte compare, inline) and the
  engine-call argument stack's size checks (HasAtLeast / PopCountFast, pointer compares); farcall's DirectPtr is skipped
  for values it would not change.
- Lab only (-DDOSAGS_VMTRACE): the shadow check (DOSAGS_VM_SHADOW=1), the line/call-point digest (vmsync, folded at
  every sourceline/farcall/callscr/call/ret, and by the fused farcall at its call), superinstruction counts (fz=).

## 2. Gates (DOSBox-X fixed 40000, --fixed-timestep; witness AGSVM4W / AGSVM4W2)
- **Shadow check, 0 mismatches:** every superinstruction execution checked against its constituents run by DosVmStep:
  MMD-CS 989,435 checks, AGS Quest 4,594, 5 Days 4,462, MMD intro 3,663,429 -- 0 mismatches. One superinstruction at a
  time on MMD-CS (FUSE=1,2,4,8,16,32): 169,946 / 387,060 / 18,991 / 170,649 / 277,298 / 179,852 checks, 0 mismatches each.
- **Line/call-point digest + state digests + instruction count, legacy vs fused (FUSE=all):** EQUAL on MMD-CS (40 lines,
  vmops 5,685,500), AGS Quest incl. its save/restore (142, 61,166), 5 Days room 3 seeded (80, 87,851), MMD intro rooms
  40->49->46->1 (300, 20,903,406); EQUAL for every single-bit arm on MMD-CS; kept Game lines EQUAL everywhere.
  First run: vmops lagged by 3 inside AQ's and the intro's blocking engine calls -- the LAB counter added the fused
  farcall's constituents after the call; moved before the call (witness-only code), re-run: EQUAL (results/*.w1 kept).
- **Slice-2 trace gates re-run (per-instruction digest):** legacy = fast unfused (FUSE=0) = fastgeneric on all four
  fixtures, EQUAL; the trace control (one AX bit) makes both digests DIFFER on all four.
- **Ratchet subset (aq-journeys' 10 checks, ratchet.sh itself -- the lock was free):** PASS 10/10 decode off and
  10/10 fast (fused); fast: boot p95 7575, room 11745, save 889, load 10166 (limits 7901 / 12295 / 913 / 10929).
- Release rig exe on DOSBox-X: legacy vs fast kept Game lines EQUAL on MMD-CS and 5 Days room 3; stamp and build_dirty=1
  in RUNMANIFEST; env_block_sha differs between the arms.

## 3. Timing (scored against section 0; MMD-CS, fixed 40000, AGSVM4, ms/tick of the script event)

| arm | measured | change vs FUSE=0 | band | verdict |
|---|---|---|---|---|
| legacy | 9.256 | | 9.20-9.35 | met |
| fast FUSE=0 (division fixes) | 5.009 | -0.115 vs slice-2 5.124 | 4.97-5.09 | met |
| FUSE=1 farcall | 4.881 | -0.128 | -0.15 to -0.45 | **MISSED (small side)** |
| FUSE=2 localload | 4.684 | -0.325 | -0.12 to -0.40 | met |
| FUSE=4 localstore | 4.995 | -0.014 | 0 to -0.05 | met |
| FUSE=8 pushmovlpop | 4.874 | -0.135 | -0.04 to -0.16 | met |
| FUSE=16 popbinmov | 4.903 | -0.106 | -0.02 to -0.14 | met |
| FUSE=32 cmpmovjz | 4.927 | -0.082 | -0.01 to -0.10 | met |
| **all (default fast)** | **4.308** | -0.701 | 4.05-4.75 | **met** |

MMD's script event at fixed 40000: legacy 9.256 -> slice 2 5.124 -> **slice 3 4.308 (2.15x; -16% on slice 2)**.
farcall missed its band on the small side (-0.128 against >= -0.15): it is still a gain, so by the registered rule it
stays; the model overcounted its saving (the slice-2 callext path was leaner than my hand count; the DirectPtr skip saves
less than a full call for most arguments).

## 4. Hot-loop size (-S of the timing build's DosVmLoop)
- ip in %edi, this in %esi at every dispatch (this loaded once; the two other %ebp+8 references are a save/restore
  around h_callext's DirectPtr loop); 46 `jmp *(%edi)` dispatch sites + 2 `jmp *8(%edx)` (ip = edx+8).
- DosVmLoop: 1,890 instructions, 6,701 bytes (slice 2: 1,281 / 4,418); sum of all handler hot paths 5,360 bytes
  (slice 2: 2,544). The superinstructions are 2,400 bytes of it (farcall 505, the pop/cmp families ~1,700).
- Only executed code occupies the 486's 8 KB cache: on MMD the singles that the superinstructions replace still run
  elsewhere, so the hot set grows by roughly the superinstructions' ~2.4 KB. That is the named suspect if the 486 gains
  less than fixed cycles show (draft E1's falsifier). localstore buys 0.014 ms for 111 bytes; the four rare cmpmovjz
  variants (ne/gt/lt/lte) are candidates to drop if the 486 says code size costs.

## 5. Rig binaries (both default legacy; built from vm-slice3.diff's tree; lab binaries, build_dirty=1)
| file | flavour | sha256 | binary_sha12 | bytes |
|---|---|---|---|---|
| build/vmlab/rig3/VM3REL.EXE | release | 0ade9355a9bbb39ef1e22aa641537370a9f4282aa22b78bb48311d70c872982a | 1781fe2bf36c | 8,636,327 |
| build/vmlab/rig3/VM3INS.EXE | instrumented (fine timing) | 82c9400ed79e7b8227aed9bc5fd3d27c0f06d0a6317a279efde624d307b4af42 | 4bbb3f1224a5 | 8,674,469 |
VM3INS differs from the timed AGSVM4 only in the build stamp (13 bytes: the immediates that write "4bbb3f1224a5" vs "04c6b2ee5c70"); the witness-only counter move changes no non-trace code.

## 6. Drafts: build/vmlab/PREREG3-486-DRAFT.md (E1 slice-3 ABBA, E2 = the deferred D3 5 Days S16 fast).
