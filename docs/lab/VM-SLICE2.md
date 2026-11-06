# VM slice 2 (+ slice-1 follow-ups) -- REPORT

## 0. PRE-REGISTRATION of the timing band (written 2026-11-05T23:05:05Z, BEFORE any slice-2 timing run)

Binary: AGSVM2 (worktree build/ags/ags.exe with vm-slice2), instrumented flavour, no trace.
Cell: MMD character select, room 50, 1000 ticks, DOSBox-X fixed 40000 (dosbox-x-fixed40k-opl3.conf),
--fixed-timestep, ACSETUP-OFF-512X384-ROUND.CFG, SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 (build/vmlab/cell.sh mmdcs).
Measure: script event ms/tick = evtype script us / n (STDOUT.TXT). Same binary, two arms:
- A: DOSAGS_VM unset (legacy Run). Predicted 9.20-9.32 ms/tick (slice-1 AGSVM1 off arm: 9.256).
- B: DOSAGS_VM=fast (unfused threaded loop). **Predicted 4.6-6.4 ms/tick, central 5.4.**

Basis: the full loop's -S read (section 3) per-handler counts weighted by probe 0291's MMD-CS opcode
histogram: ~156k x86 instructions/tick for VM + marshalling (legacy ~320k), +-30% for walker paths
and the unmeasured cost of the generic stepper (memwritelit, memread1/memwrite1, object reads go
through it, ~90 ops/tick); script event = 370k - 320k + (109..203k). This is tighter than and below
VM-DESIGN's slice-2 band (6.0-7.2), which predates the slice-0/slice-2 -S reads; that band is stated
here for the record and is NOT the one scored.
Falsifier: B outside 4.6-6.4, or A outside 9.20-9.32 -> reported as a miss of the model, not argued.
AGS Quest and 5 Days timing: informational only (no band).

(Timing runs started after this section was written: results/TIMING-START.UTC.)

## 1. AGS Quest memory: NOT a leak

AGSVM2 with `DOSAGS_VM=decode` / `check` on the AutoPilot (to quit, incl. its own save/restore at tick
2024). New counters in the patch: bytes allocated at every decode, bytes freed in
`~ResolvedScriptData()` (a `vmfree` line each), live = allocated - freed, and the heap break `sbrk(0)`.

- 16 decodes, **16 frees; 272,052 B allocated, 272,052 B freed, live 0 at quit.**
- Live never exceeds what is loaded: 57,236 B (AutoPilot + Global + Dialog) + the current room
  (up to room 3's 26,080 B) = 83,316 B peak; every room unload frees its stream before the next room's
  decode (`vmfree bytes=26080 live=57236 ...` before each `vmdecode ... room4`). The restore frees all
  seven and re-decodes them (live 0 -> 57,236 again), not on top of them.
- Heap break: grows only on the first visit to each room and once in the second half
  (0x11e1078 -> 0x12c20a8), then stays flat through four more room3/room4 decodes -- no growth per decode.
- `memory_min_free_kb` (largest free DPMI block, sampled once a second): decode off 160,496; decode
  158,896 (-1,600 KB, identical in the decode and check arms). With 0 bytes live at quit and a flat
  break, the drop is the heap's high-water / DPMI-block granularity moving when the first room loads
  ask for a few KB more, not retained memory. A "largest block" metric cannot tell these apart; the
  allocated/freed counters can.

## 2. Decoder tuned: one pass, table in the TU, no zero-fill

- Opcode table copied into the VM TU once (no cross-TU call per argument); one pass (forward jump
  targets recorded and resolved after the walk); `dcode` built by `reserve` + `push_back`, no zero-fill.
- **Check arm: 0 mismatches** on MMD character select (55,164 instructions), AGS Quest (16 loads),
  5 Days room 3 -- every category 0, 0 ineligible (results/CHK3-*).
- **Cost: 1.25-1.30 us per code word at fixed 40000** in decode/check mode (MMD global 163.5 ms for
  130,393 words; slice 1: 2.0 us/word, 260.9 ms) -- 1.6x faster, ~50 emulated cycles/word. The design
  figure was 30-60 instructions/word; this is at its top, not below it.
- In fast mode the decoder writes handler addresses directly and pays a `HandlerFor()` call per
  instruction: **1.61 us/word** (MMD global 209 ms; game start +211 ms at fixed 40000). A kind->handler
  table lookup would remove most of that; not done in this slice (it would invalidate the gate runs).

## 3. The full loop's -S (DosVmLoop, release flags, cc_instance_vm.cpp)

- **ip in %edi, this in %ebx at every dispatch.** `this` is loaded once from 8(%ebp) and never
  reloaded; all 36 dispatch sites are `jmp *(%edi)`; the frame pointer `fr` is a parameter slot
  (12(%ebp)), reloaded where used, by design. Inside `h_callext` GCC parks ip and this in stack slots
  across the DirectPtr loop and restores them before dispatch (live-range splitting inside one
  call-out handler, not a spill across dispatch). Gate: PASS.
- Size: DosVmLoop is 1,281 instructions, 4,418 bytes including its cold paths; sum of the 41 handlers'
  hot paths 2,544 bytes. (Legacy Run(): 3,365 instructions.)
- Hot-path instructions per handler (incl. the 2-instruction dispatch), vs slice 0's sketch:

| handler | slice 2 | slice 0 | | handler | slice 2 | slice 0 |
|---|---|---|---|---|---|---|
| mov | 12 | 14 | | push | 30 | 34-36 |
| movl int / gvar / str / imp | 6 / 7 / 7 / 24 | 10 | | pop | 24 | 26 |
| sourceline (no hook) | 8 | 8 | | ret | 49 | 40 |
| jzi / jnzi | 4-6 / 4 | 5-9 | | call | ~103 | -- |
| jmpi forward | 8 | 6 | | farcall (engine call path) | 99 | (152 fused) |
| subi plain / on MAR (2.66 steps) | 9 / ~40 | -- | | farpush / farsubsp | 20 / 31 | -- |
| addi plain | 10 | -- | | setfuncargs / thisaddr | 3 / 5 | -- |
| memread4 (stack) | ~25 | -- | | cmpeq / gte | 15 / 10 | -- |

  `call` and `ret` are the expensive ones (frame-field traffic, call-stack arrays, start-bit test);
  both are 64-66 per tick on MMD. Not superops; candidates for later trimming.

## 4. Gates (all on DOSBox-X, fixed 40000, --fixed-timestep unless stated)

Witness build AGSVM2W (= AGSVM2 + `-DDOSAGS_VMTRACE`): per-instruction trace digest folded before
every executed instruction by BOTH VMs (instance, pc, opcode, all 8 registers' type/value/size and
pointer presence, stack index of stack pointers, stack-data offset, the top three stack entries,
line number, call depth), printed with the 0292-style state digests every 25 ticks.
Arms per fixture: WL legacy, WL2 legacy again, WF `DOSAGS_VM=fast`, WG `DOSAGS_VM=fastgeneric`
(every instruction through DosVmStep), WC trace control (`DOSAGS_VMTRACE_CONTROL`: one AX bit flipped
after the first engine call past tick N, legacy VM), WP state control (`DOSAGS_WIT_PERTURB_TICK`).

| fixture | statewit lines | vmops (instructions traced) | WL=WL2 | WL=WF | WL=WG | WC differs | WP differs |
|---|---|---|---|---|---|---|---|
| MMD character select (1000 ticks) | 40 | 5,685,500 | EQUAL | **EQUAL** | **EQUAL** | yes (t325) | yes (t300) |
| AGS Quest AutoPilot (to quit; own save+restore at t2024) | 142 | 61,166 | EQUAL | **EQUAL** | **EQUAL** | yes (t525) | yes (t500) |
| 5 Days room 3, seeded (2000 ticks) | 80 | 87,851 | EQUAL | **EQUAL** | **EQUAL** | yes (t375) | yes (t300) |
| MMD intro `--startr 40`, rooms 40->49->46->1 (7500 ticks, 47 CALLAS sites) | 300 | 20,903,406 | EQUAL | **EQUAL** | **EQUAL** | yes (t1075) | yes (t1000) |

Also EQUAL in every WL/WF/WG pair: the kept `Game :` lines, AGS Quest's AUTOPLT.LOG (raw, unmasked)
and PH01-03.BMP. MMD-CS vmops 5,685,500 equals LAB-MMD's independent count for this fixture.

**Screen gate** (AGSVM2, no fixed timestep, freeze captures, `screen-equal.py`): fast vs legacy
**9/9 equal** (MMD t200/500/900, AQ t400/1500/3000, 5 Days t200/500/900); the perturbation control
differs on AQ t400 and 5 Days t200 (MMD's control is equal at its three ticks, as in LAB-MMD 9.10).

## 5. Timing (scored against section 0)

| cell (AGSVM2, fixed 40000) | legacy (DOSAGS_VM unset) | fast | band | verdict |
|---|---|---|---|---|
| MMD-CS script event ms/tick | **9.311** | **5.130** | A 9.20-9.32 / B 4.6-6.4 | **both MET** |
| MMD-CS `tickstats_script_vm` total | 9,403 ms | 5,230 ms | | |
| MMD-CS fastgeneric (test mode) | | 19.087 | | 2x slower than legacy, as expected |
| 5 Days room 3 script event ms/event | 0.257 | 0.213 | info | |
| AGS Quest script event ms/event | 359.77 | 359.84 | info | no change: its events are engine-bound |

**MMD script event: 9.311 -> 5.130 ms/tick, 1.82x at fixed cycles** (VM+marshalling ~2.4x if the
non-VM ~1.7 ms is unchanged). Behaviour in the timing arms: kept `Game :` lines equal (MMD, AQ, 5 Days),
AQ PH*.BMP and AUTOPLT equal. Load-time cost of fast mode: MMD `script_vm_init_ms` 1,240 -> 1,451
(+211, the fast-mode decode), room 50 +5 ms. `memory_min_free_kb` MMD -640 KB (the decoded streams).

## 6. Ratchet subset (aq-journeys' 10 checks; exe-bytes excluded as asked)

`ratchet.sh` itself could not run: another session's full ratchet on `~/git/dosags` (pid 361802,
`--busy-wait 3600`, gate-alias included) holds `/tmp/sdl-dos-ports-ratchet.lock`, and both of my
invocations timed out on `--lock-wait 1800` (exit 3; `ratchet2/{off,fast}.log`). I did not bypass the
lock. Instead I ran the same unit the ratchet runs (`tests/harness/ratchet-cell.sh OUT lab agsquest
--fixed-timestep --conf .../dosbox-x-fixed40k-opl3.conf --timeout 1800`, + `--env DOSAGS_VM=fast` for
the fast arm), which takes the DOSBox-X lock itself, and applied `tests/ratchet.yaml`'s limits to its
facts.txt with `ratchet_facts_check.py`. Controls not run.

| check | limit | decode off | fast |
|---|---|---|---|
| stale_frames | eq 0 | 0 PASS | 0 PASS |
| room_n / save_n / load_n / boot_n | 8 / 1 / 1 / 1 | PASS | PASS |
| journeys_unfinished | eq 0 | 0 PASS | 0 PASS |
| boot_p95_ms | le 7901 | 7541 | 7570 |
| room_p95_ms | le 12295 | 11733 | 11740 |
| save_p95_ms | le 913 | 895 | 895 |
| load_p95_ms | le 10929 | 10114 | 10162 |

All 10 PASS in both arms (fast's boot/load p95 carry the fast-mode decode, +29/+48 ms).

## 7. Files

- Patch: `~/git/dosags-lab-vm/vm-slice2.diff` (slice 1 + 2; supersedes vm-slice1.diff). Lab-only parts
  are compiled only with `-DDOSAGS_VMTRACE` (trace fold, its control, the statewit printer in
  game_run.cpp, a trace call in Run()'s loop head and its CALLEXT).
- Binaries: `build/vmlab/exe/AGSVM2.EXE` (timing/behaviour, sha c027a415d490...), `AGSVM2W.EXE`
  (witness, 695ea8c76da2...).
- Raw: `build/vmlab/results/` -- `W{L,L2,F,G,C,P}-{MMDCS,AQ,5D3,MMDINTRO}` (witness),
  `S{L,F,C}-{MMDCS,AQ,5D3}` (screen gate, `frz/frames`), `T{L,F,G}-*`, `OFF3-AQ`, `DEC3-AQ`, `CHK3-*`;
  `build/vmlab/ratchet2/cell-{off,fast}`; `-S`: `build/vmlab/s2/{vm.s,loop.s,vm.lst,tbl.txt}`;
  scripts `cell.sh`, `scell.sh`, `wgate.py`, `compare.py`, `ratchet_facts_check.py`.

## 8. Notes for the next slice

- `call` (~103) and `ret` (49) are the most expensive common handlers left; `farcall` 99.
- Fast-mode decode pays `HandlerFor()` per instruction (1.61 vs 1.25 us/word): use a table.
- The lab-only work counter (make AGS_WORK_SCRIPT_INS=1) does not count instructions run by the fast
  loop; a work-vector cell must run legacy or the counter must be added.
- Not run: the full ratchet (gate-alias captures, sb-live audio rows, xdotool click rows), any 486 cell.
