# LAB-L1B -- what shape the VM lever should take for MMD's seven per-tick functions (lab worktree ~/git/dosags-lab-l1)

Copied into the main repo 2026-11-06 from the lab worktree ~/git/dosags-lab-l1 (measurement only); probe diff and readers in
docs/lab/l1b-lab-patches/, per-cell analyses, cost model and margin in docs/lab/l1b-results/. Exes and vm.s stay local.

Lab only. This is a measurement: no speed lever was built and nothing was committed anywhere. ~/git/dosags, ~/git/dosags-r1land,
~/git/dosags-lab-r3 and ~/git/dosags-nightly were not touched, and there was no rig or vcctrl use. Times are DOSBox-X
fixed-40000 emulated time (normal core: about 1 cycle per x86 instruction, 40 cycles per us) unless a row says 486.

## 0. Answer first

- **Per tick, the seven functions run 5,216 VM instructions in 3,092 dispatch units.** They are 91.6% of all VM
  instructions (5,693 a tick). The counts are the same to 0.1% in GCL (16 walk clicks), G (clicks and hovers) and on
  character select: the work is fixed per tick, as LAB-L1 found.
- **The superinstructions already cover the hot code.** 58% of these instructions run inside one, at 1.69
  instructions per dispatch. All 6.96 M superinstruction attempts in GCL committed: no fallbacks. Of the top 20
  3-instruction sequences, the biggest unfused ones are small idioms:
  - sourceline + local load: 4.5% of instructions;
  - jzi + sourceline;
  - local load into ax, then a push or an engine-call argument;
  - an `x == L` branch, split across two superinstructions.
  None of these saves more than about 15 cycles per execution.
- **The largest single VM cost is the engine-call path.** The fused farcall handler takes about 165 instructions per
  call, before the API function runs. At 151 calls a tick that is 22.6% of the modelled VM time in the seven, and more
  than the API bodies themselves. Next come the local-variable load with its stack walk (20.4%) and call/ret (7.7%).
  The 61 instructions a tick that MMD sends through the generic stepper (memwritelit, memread1, memwrite1) cost 6.1%.
- **What the script does each tick** (section 6). It polls the verb-coin interface's state. It scans 30 timer
  global ints and checks 24 more ("own timers"), all inactive. It re-parses the hotspot name's `>x` default-verb
  suffix 14 times. It resets the normal and mouse-over picture of each of the 10 verb buttons (18 SetButtonPic and 18
  FindGUIID("MAINGUI") calls).
- **Ranked levers** (486 central saving per tick; section 8):
  1. getter intrinsics, -0.40 ms (band 0.34-0.48);
  2. native handlers for the three stepper opcodes, -0.07;
  3. a trimmed generic engine-call path, -0.09 alone or -0.045 after 1;
  4. more superinstructions, -0.07;
  5. a cheaper call/ret, -0.04.

  All five are exact, all are engine-generic, and all can be gated on digests. Together they make about -0.6 ms/tick
  on the 486 (about -0.84 ms/tick at fixed 40k, 20% of the per-tick script).
- **Recommendation: build the getter intrinsics first.**
  - They cover GetGlobalInt, StrGetCharAt, StrLen, GetCursorMode, IsGamePaused and GetPlayerCharacter: 106 calls a
    tick.
  - Each one is recognised by the engine API function it resolves to, never by the game.
  - Fixed 40k: -0.42 ms/tick (band 0.35-0.50).
  - 486: -0.40 ms/tick (band 0.34-0.48). I built that from 486 per-call samples for the API half and from the
    measured r = 0.3-0.7 for the VM half (section 9).
- **Margin.** After R1 and R3 (central), a drawn room-2 tick is 24.1 ms, and its p95 on the GCMP shape is 24.86 ms.
  - Intrinsics: p95 24.46 ms; drawn ticks over 25 ms fall from 3.7% to 1.0%.
  - (Corrected in section 10: p95 24.27 -> 23.87 ms, over 25 ms 1.8% -> 1.5%; the first figures used the off-by-one pairing.)
  - All five levers: p95 about 24.3 ms.
- **No candidate, and no combination of them, is predicted to reach 99% displayed on the GC fixture.**
  - The ticks still over 25 ms are spikes of 27-380 ms: clicks and the room entry.
  - Room 1 (about 94.5% displayed in release) gains the most, about +1 to +1.5 points for the whole fixture.
  - Whole fixture, central: about 97.5% with the intrinsics and about 98% with everything, against R3's 96.5%.

## 1. Setup

- Worktree ~/git/dosags-lab-l1, at the L1 state: lab-play.diff plus lab-l1.diff, the vendor trees as in LAB-L1.md
  section 1, and `#define DOSAGS_L1VM 0`.
- The L1B probe source is build/l1b/lab-l1b.diff, over that state. Its patched files are kept in build/l1b/src/ and
  the originals in build/l1b/orig/.
- build/l1b/build.sh does three things:
  - sets DOSAGS_L1VM=1 and DOSAGS_L1B=1;
  - builds and copies build/l1b/exe/L1B.EXE;
  - puts both defines back to 0.
- The vendor files were then restored from build/l1b/orig/. A plain `make all` rebuilt **L1E.EXE byte for byte**
  (sha256 77a393f9...), so the L1 tree and results are as they were. build/l1/ was not written.
- Cells: conf tests/harness/confs/dosbox-x-fixed40k-opl3.conf, R1 on (DOSAGS_GUI_CLIP=2), DOSAGS_RANDSEED=1. The rest is
  as LAB-L1:
  - save 007, sound on, fixed timestep, fine timing;
  - displays 386 and 387, at most two DOSBox-X instances;
  - every wait goes through tools/waitfor.sh, with a pid file and a timeout.

  The cell scripts are build/l1b/{cell,fix,pair}.sh, copies of build/l1's that write to build/l1b/results/.

| cell | exe | L1PROF | fixture | window (ticks) | SET bytes | witnesses |
|---|---|---|---|---|---|---|
| GCL3 | L1B | 3 | GCL (GC + 16 walk clicks) | 5437-12439 (7003) | ~496 (= GCL1's: same SETs, "3" for "1") | FT ENABLED, mode=2, guiclip_final mode=2, script_vm in RUNMANI |
| G3 | L1B | 3 | G (5 clicks + 9 moves) | 5437-8599 (3163) | ~490 (G1's 511 minus the TICKLOG SET; G3 runs NOTL) | same |
| CS3 | L1B | 3 | MMD character select, F1MMDP's line in DOSBox-X, no restore, exit 1000 | 40-999 (960) | small | FT ENABLED (no guiclip: R1 does not apply there) |
| SMOKEB | L1B | 3 | S (exit 5800) | 5437-5799 | small | probe smoke only |

- **Inertness: EQUAL.** I compared the 'Game :' lines with every *_ms / *_us / t_ms / ms / us field removed
  (build/l1b/tools/gameeq.py):

  | comparison | Game lines | result |
  |---|---|---|
  | GCL3 vs GCLREF (R1INS) | 120 | EQUAL |
  | GCL3 vs GCL2 (L1F) | 120 | EQUAL |
  | G3 vs G1 (L1E) | 87 | EQUAL |
  | G3 vs G2 (L1F) | 87 | EQUAL |

  The control GCLREF vs GC01 (a different fixture) is DIFF.

  The getter timing loop (section 5) calls only side-effect-free getters, with the arguments of a live call. Game
  output shows it changes nothing.

## 2. The probe (DOSAGS_L1PROF=3, exe built with DOSAGS_L1B=1; counts only)

- **Scope.** Level 3 is level 2 (L1F's buckets, which say which script function is running) plus instruction counts.
  It counts from loop tick 5437 by default; DOSAGS_L1WIN overrides that.
- **Hook points.** The hooks reuse the VM's trace hook points:
  - VM_TRACE at every dispatch and in the stepper loop;
  - VM_FUSED at every superinstruction commit, which counts the constituents after the first;
  - call, ret, VM entry and exit;
  - the local-variable walk;
  - engine-call entry.
- **Instruction counts.** Every executed original instruction is counted once. A superinstruction counts as its
  constituents; a superinstruction that falls back would show as attempts > commits, and there were none.
- **What is recorded:**
  - per function: the opcode histogram, dispatch units per handler, walk steps;
  - 2- and 3-instruction sequences per function, with register operands and whether the whole sequence ran inside
    one superinstruction;
  - per-pc execution counts, with each instruction decoded at first touch (import names, string literals, global
    addresses);
  - activations: calls, returns, leaf (no script call made), ops and API calls per activation.
- **Getter timing loop.** At a getter's 200th, 2,000th, 20,000th and 100,000th call, the probe times 256 calls of
  the getter's own Sc_ function with the live arguments, using RDTSC (= emulated cycles). It subtracts the empty loop,
  and also times an empty noinline function of the same signature.
- **Timing.** The probe's own timing is not scored: it changes the loop's register allocation. Per-unit costs come
  from the -S of the timing build (section 7).
- **Readers** (all in build/l1b/tools/, run with python3 -I):
  - l1bana.py: tables (a)-(c) and `--list`, the annotated listing;
  - model.py: the cost model;
  - margin2.py: the 486 margin;
  - profsyms.py: 486 per-symbol samples from F1MMDP's PROF.BIN;
  - gameeq.py: inertness.

## 3. (a) Instructions, opcodes and sequences (GCL3; G3 and CS3 agree to 0.1%)

### 3.1 Per function

The L1F VM share is LAB-L1's exclusive time (raw, with the probe's per-switch cost inside). The model column is the
probe-free cost model of section 7. It reproduces the VM total within 2-8%: 3.02 ms/tick against 3.06-3.25.

| function | calls/tick | instr/tick | units/tick | instr/unit | in a superinstr | L1F VM ms/tick (share) | model ms/tick (share) | model's top items |
|---|---|---|---|---|---|---|---|---|
| Extension | 14 | 1,062 | 606 | 1.75 | 60.5% | 0.890 (23.7%) | 0.670 (22.2%) | farcall 26%, stepper ops 23%, local load 12% |
| SetAlternativeAction | 10 | 1,102 | 730 | 1.51 | 47.4% | 0.688 (18.3%) | 0.582 (19.3%) | farcall 25%, local load + walk 29% |
| CheckTimers | 1 | 1,232 | 624 | 1.97 | 71.6% | 0.569 (15.1%) | 0.539 (17.9%) | local load 26%, farcall 23%, push 9% |
| GlobalCondition | 5 | 492 | 305 | 1.61 | 55.2% | 0.356 (9.5%) | 0.261 (8.7%) | farcall 13%, local load 11% |
| IsOwnTimerExpired | 24 | 600 | 312 | 1.92 | 68.0% | 0.346 (9.2%) | 0.280 (9.3%) | farcall 35%, ret 12% |
| CheckDefaultAction | 1 | 323 | 245 | 1.32 | 34.1% | 0.295 (7.8%) | 0.206 (6.8%) | call 19%, push 17%, farcall 14% |
| repeatedly_execute | 1 (entry) | 406 | 270 | 1.50 | 49.3% | 0.273 (7.3%) | 0.213 (7.1%) | call 29%, push-literal-pop 12% |
| **seven** | | **5,216** | **3,092** | 1.69 | 58.2% | 3.417 (90.9%) | **2.751 (91.3%)** | |
| all VM | | 5,693 | 3,362 | 1.69 | 58.4% | 3.757 | 3.014 | |

### 3.2 Opcode histogram, the seven (instructions per tick, share)

mov 757 (14.5%), movl 667 (12.8%), subi 514 (9.9%), sourceline 507 (9.7%), memread4 413 (7.9%), push 361 (6.9%), pop 284
(5.4%), farpush 254 (4.9%), jzi 175 (3.4%), farcall 157 (3.0%), setfuncargs 157 (3.0%), farsubsp 151 (2.9%), cmpeq 115,
sub 95, addi 81, memwrite4 80, gte 64, call 59, ret 56, thisaddr 56, add 56, jmpi 47, **memwritelit 33, memread1 14,
memwrite1 14 (the stepper's 61)**, muli 28, land 8, lor 6, cmpne 4, lt 2, gt 1. 31 opcodes in all.
- **Per function:** see build/l1b/results/GCL3-ana.txt, top 10 each.
- **Dispatch units per tick:**

  | handler | units/tick | handler | units/tick |
  |---|---|---|---|
  | linenum | 507 | S_localload | 351 |
  | movl_int | 266 | push | 201 |
  | S_pushmovlpop | 160 | mov | 157 |
  | S_farcall | 151 | subi | 144 |
  | farpush | 103 | S_eqjz | 87 |
  | addi | 81 | memread | 62 |
  | stepper | 61 | memwrite | 61 |
  | call | 59 | ret | 56 |
  | thisaddr | 56 | addreg | 56 |
  | S_popsubmov | 56 | jz | 54 |
  | jmp | 47 | | |

### 3.3 Top 20 sequences, the seven (per tick; fused = share that ran inside ONE existing superinstruction)

| # | 2-instruction sequence (dominant register form) | /tick | % instr | fused | | 3-instruction sequence (dominant form) | /tick | % instr | fused |
|---|---|---|---|---|---|---|---|---|---|
| 1 | mov sp,mar ; subi mar | 398 | 7.6 | 93% | | mov sp,mar ; subi mar ; memread4 ax | 351 | 6.7 | 100% |
| 2 | subi mar ; memread4 ax | 351 | 6.7 | 100% | | sourceline ; mov sp,mar ; subi mar | 243 | 4.7 | 0% |
| 3 | push ax ; movl ax | 284 | 5.4 | 56% | | mov bx,ax ; jzi ; sourceline | 174 | 3.3 | 0% |
| 4 | sourceline ; mov sp,mar | 277 | 5.3 | 0% | | push ax ; movl ax ; pop bx | 160 | 3.1 | 100% |
| 5 | mov bx,ax ; jzi | 175 | 3.4 | 69% | | setfuncargs ; movl ax ; farcall ax | 157 | 3.0 | 96% |
| 6 | jzi ; sourceline | 174 | 3.3 | 0% | | farpush ax ; setfuncargs ; movl ax | 151 | 2.9 | 100% |
| 7 | movl ax ; pop bx | 160 | 3.1 | 100% | | movl ax ; farcall ax ; farsubsp | 151 | 2.9 | 100% |
| 8 | movl ax ; farcall ax | 157 | 3.0 | 96% | | memread4 ax ; push ax ; movl ax | 118 | 2.3 | 0% |
| 9 | setfuncargs ; movl ax | 157 | 3.0 | 96% | | pop bx ; cmpeq bx,ax ; mov bx,ax | 115 | 2.2 | 19% |
| 10 | farpush ax ; setfuncargs | 151 | 2.9 | 100% | | subi mar ; memread4 ax ; push ax | 112 | 2.1 | 0% |
| 11 | farcall ax ; farsubsp | 151 | 2.9 | 100% | | subi mar ; memread4 ax ; farpush ax | 111 | 2.1 | 0% |
| 12 | memread4 ax ; farpush ax | 139 | 2.7 | 0% | | jzi ; sourceline ; mov sp,mar | 109 | 2.1 | 0% |
| 13 | memread4 ax ; push ax | 118 | 2.3 | 0% | | cmpeq bx,ax ; mov bx,ax ; jzi | 107 | 2.1 | 81% |
| 14 | pop bx ; cmpeq bx,ax | 115 | 2.2 | 19% | | movl ax ; pop bx ; cmpeq bx,ax | 93 | 1.8 | 0% |
| 15 | cmpeq bx,ax ; mov bx,ax | 115 | 2.2 | 95% | | memread4 ax ; farpush ax ; setfuncargs | 86 | 1.6 | 0% |
| 16 | movl ax ; push ax | 107 | 2.1 | 0% | | pop bx ; sub bx,ax ; mov bx,ax | 84 | 1.6 | 67% |
| 17 | sourceline ; movl ax | 101 | 1.9 | 0% | | farsubsp ; push ax ; movl ax | 80 | 1.5 | 0% |
| 18 | sub bx,ax ; mov bx,ax | 95 | 1.8 | 59% | | farcall ax ; farsubsp ; push ax | 80 | 1.5 | 0% |
| 19 | pop bx ; sub bx,ax | 84 | 1.6 | 67% | | push ax ; mov sp,mar ; subi mar | 75 | 1.4 | 0% |
| 20 | farsubsp ; push ax | 80 | 1.5 | 0% | | movl ax ; push ax ; mov sp,mar | 65 | 1.2 | 0% |

- **The six existing superinstructions own every big sequence.** The 0%-fused rows are the joins between them:
  - sourceline before a local load;
  - a local load that feeds a push or an engine-call argument;
  - the jump that ends one line and the sourceline that starts the next.
- **Why `pop bx ; cmpeq` is only 19% fused.** In `if (x == L)` the pop belongs to push-literal-pop, so the compare
  runs as eqjz: the idiom takes two dispatches.
- **Other tables.** The same tables for ALL VM, and per function (top 8), are in build/l1b/results/GCL3-ana.txt.

## 4. (b) Calls and returns

| callee | activations/tick | leaf (no script call) | ops/activation | API calls/activation | called from |
|---|---|---|---|---|---|
| IsOwnTimerExpired | 24.0 | 24.0 | 25 | 1.0 | repeatedly_execute 24 |
| Extension | 14.0 | 14.0 | 76 | 3.0 | SetAlternativeAction 10, CheckDefaultAction 2, Add/RemoveExtension 1+1 |
| SetAlternativeAction | 10.0 | 0 | 110 | 3.6 | CheckDefaultAction 10 |
| isAction | 5.0 | 5.0 (no API either) | 13 | 0 | GlobalCondition 5 |
| GlobalCondition | 5.0 | 2.0 | 98 | 2.4 | CheckDefaultAction 3, UpdateActionBar 2 |
| UpdateActionBar, TranslateAction, CheckDefaultAction, CheckTimers, Add/RemoveExtension | 1.0 each | TranslateAction, CheckTimers | 53-1232 | 2-30 | repeatedly_execute / CheckDefaultAction |
| repeatedly_execute (entry) | 1.0 | -- | 406 | 6 | the engine |

- **Volume.** 64.0 script CALLs and 64.0 returns a tick, plus the two entry functions' returns. 0 legacy runs and 0
  stepper calls.
- **Leaves.** 47 of the 64 calls (73%) go to leaf functions. Only isAction's 5 (8%) make no engine call either.
  - Every other leaf calls the engine. GetGlobalInt's error text carries the script call stack, so leaf inlining
    could not be exact; it is not proposed.
- **Cost per call/ret pair** (-S of the timing build, fixed-40k cycles):

  | part | cycles |
  |---|---|
  | call handler | 92 |
  | ret handler | 55 |
  | caller's `movl ax,FUNC` | 10 |
  | caller's `subi sp,4n`: out-of-line PopDataFromStack, 1 argument | ~27 |
  | callee's thisaddr | 7 |
  | **total** | **~190 (4.75 us)** |

  64 pairs make 0.30 ms/tick, 10% of the modelled VM. That excludes the argument pushes, which the call needs anyway.
- **Where the call handler's 92 cycles go:**
  - stack and call-stack checks;
  - PUSH_CALL_STACK, 3 stores;
  - the return address pushed as a 20-byte value;
  - the thisbase/funcstart relocation;
  - frame stores;
  - the start-bit test.

  The ret handler is its mirror image, plus a second start-bit test.

## 5. (c) The trivial getters (API calls that only read a field or a string)

The fixed-40k cost per call is the getter timing loop's figure: the Sc_ function called through its pointer with the live
arguments, the loop subtracted. A noinline call of the same signature costs 18 of those cycles. The 486 column is
F1MMDP, round F1a's 1024 Hz samples on MMD character select. That fixture runs these same functions per tick, at the
same rates (CS3: GetGlobalInt 54.0, StrGetCharAt 28.8, StrLen 16.8 a tick).

| getter | calls/tick (GCL3) | callers | API cost/call, fixed 40k | 486: Sc_ + body samples | 486 per call | what the call does |
|---|---|---|---|---|---|---|
| GetGlobalInt | 55.3 | CheckTimers 30, IsOwnTimerExpired 24, room_b 1.3 | 41 cycles (1.0 us) | Sc_GetGlobalInt 0.077 + GetGlobalInt 0.048 ms/tick | **2.3 us** | bounds check, `play.globalscriptvars[i]` |
| StrGetCharAt | 28.0 | Extension 28 | 45-65 cycles (strlen of the name) | 0.062 + 0.041 (+ strlen) | ~3.6 us | `strlen(s)`, then `s[i]` or 0 |
| StrLen | 16.0 | Extension 14, Add/RemoveExtension 2 | 44 cycles | Sc_strlen 0.058 (+ strlen) | ~3.5 us | strlen |
| GetCursorMode | 4.0 | GlobalCondition 3, UpdateActionBar 1 | 21 cycles | under the listing floor | ~1.4 us (est.) | `cur_mode` |
| IsGamePaused | 2.0 | repeatedly_execute 2 | 31 cycles | -- | ~1.4 us (est.) | `game_paused > 0` |
| GetPlayerCharacter | 1.0 | GlobalCondition 1 | 28 cycles | -- | ~1.4 us (est.) | `game.playercharacter` |
| **total** | **106.3** | | | | | |

Not trivial, so not intrinsic candidates:
- GetGUIAt (212-407 cycles: a walk over the GUIs).
- FindGUIID (a string compare against the cache).
- GetInvAt, GetLocationType and GetLocationName.
- IsTimerExpired, which clears the timer.
- StrCopy, StrSetCharAt and StrCat, which write.

**What an intrinsic skips.** Today each call is the fused farcall handler. On the -S it is about 165 instructions for
1 argument (+7 per further argument, plus an out-of-line DirectPtr call for a string argument), plus the API function
above. The handler's 165 instructions:
- **Operand reads and checks: 62.** 27 of them are SystemImports::GetByIndexFast's bounds test in 64-bit arithmetic.
  The rest are the import type check, next_call_needs_object, and the call stack's space check.
- **Argument marshalling: 39** (the fcs push, 20 bytes):
  - num_args;
  - `ax = import value`, 20 bytes;
  - the DirectPtr test loop.
- **_pc sync and was_just_callas: 7.**
- **API dispatch: 18:**
  - the dos_port_work 64-bit counter;
  - the lever-2 memo hook;
  - argument setup;
  - the indirect call.
- **After the call: 39:**
  - the cc_has_error read;
  - the 20-byte result copy out of a stack temporary;
  - three frame stores;
  - the abort test;
  - farsubsp with its bound;
  - the dispatch.

An intrinsic keeps about 40 of these:
- the import identity test;
- the argument read and the body;
- `ax = SetInt32(result)`;
- the dos_port_work counter;
- the memo hook for GetGlobalInt and IsGamePaused, which are not on lever 2's whitelist;
- the three frame stores and the fcs pop;
- the dispatch.

The intrinsic saves about 125-140 VM cycles per call, plus the API's 21-65 (minus the strlen that StrGetCharAt and
StrLen still do).

## 6. (d) What MMD's script does every tick (global script, GCL3 per-pc counts, build/l1b/results/GCL3-ana.txt --list)

repeatedly_execute (1 a tick):
- `if (!IsGamePaused())` (2 calls);
- CheckTimers();
- 24 calls of `if (IsOwnTimerExpired(n)) {...}`, all false;
- UpdateActionBar();
- CheckDefaultAction();
- two FindGUIID + SetButtonPic.

The functions it calls:
- **CheckTimers** (1 a tick, 1,232 instructions): `int t = 30; int i = 399; while (i >= 400 - t) { if (GetGlobalInt(i) >= 2)
  {...}; i--; }`. It reads global ints 399 down to 370, the template's 30 timer slots. All are inactive (< 2).
- **IsOwnTimerExpired(n)** (24 a tick, 25 instructions each): `if (GetGlobalInt(400 - n) == 1) {...} return 0;`.
  Always false.
- **CheckDefaultAction** (1 a tick):
  - GetLocationName at the mouse into a buffer;
  - Extension(buffer);
  - GetLocationType x2 and GetInvAt;
  - GlobalCondition x3;
  - Add/RemoveExtension;
  - then **SetAlternativeAction x10**, one per verb button;
  - StrCopy.
- **SetAlternativeAction** (10 a tick, 110 instructions each):
  - reads the button's entries from three global int arrays (global data 716, 756, 796);
  - calls Extension on the location name, to compare the default-verb character;
  - then `SetButtonPic(FindGUIID("MAINGUI"), b, 1, pic)` and `SetButtonPic(FindGUIID("MAINGUI"), b, 2, pic)`. That
    sets the normal and mouse-over pictures, usually to the values they already have (18 of each a tick).
- **Extension(s)** (14 a tick, 76 instructions each). It reads the `>x` / `$x` default-verb suffix of the hotspot name:
  `len = StrLen(s); if (StrGetCharAt(s, len-2) == '>') c = StrGetCharAt(s, len-1); else if (... == '$') ...; return c;`.
  - Its locals are a char and an int declared with memwritelit, and the char result goes through memwrite1 and
    memread1. Those are the 61 stepper instructions a tick.
- **GlobalCondition(k)** (5 a tick): an if-chain over the template's conditions. It tests the mouse over the
  inventory, the location type and a GUI button. It calls GetInvAt, GetCursorMode, GetGUIAt, GetGUIObjectAt and
  isAction.

Plainly: 90% of MMD's interpreter time is the 9-verb template re-deriving the same UI state every tick:
- 30 + 24 timer slots polled through GetGlobalInt (55 calls);
- the hotspot name's suffix re-parsed 14 times;
- 10 verb buttons re-pictured.

None of it depends on input (LAB-L1 P1/P2). Caching any of it across ticks would change script-visible behaviour, and
is not proposed (VM-DESIGN 6).

## 7. The cost model (how the shares in sections 3, 4 and 8 were made)

- **Per-unit costs.** Hot-path x86 instructions per dispatch unit, counted on the -S of the timing build's DosVmLoop
  (build/l1b/s/vm.s). That file is the restored source with DOSAGS_L1VM=0 and DOSAGS_L1B=0, identical to L1E's.

  | unit | cycles | unit | cycles |
  |---|---|---|---|
  | linenum | 8 | mov | 14 |
  | movl int | 10 | movl import | 47 |
  | push | 33 | pop | 26 |
  | jz | 8 | thisaddr | 7 |
  | call | 92 | ret | 55 |
  | S_farcall | 165 | S_localload | 46 + 6 per walk step |
  | S_pushmovlpop | 36 | S_popsubmov | 38 |
  | S_eqjz | 24 | S_gtejz | 19 |
  | stepper op | 110 | | |

  - The stepper figure is from slice 2's fastgeneric run: about 122 cycles per instruction, all included.
  - Measured walk steps per local access: 2.63.
- **Check.** The model gives 3.01 ms/tick for the whole VM. Against it:
  - L1F's raw VM is 3.76 ms/tick. LAB-L1 bounds the probe's own cost inside it at about 0.70, which leaves 3.06.
  - L1E's per-tick script is 4.25 ms/tick. Taking off the API bodies (about 0.80) and the outside part (0.20)
    leaves 3.25.

  So the model matches to 2-8%. Per function it is within about 20% of L1F's raw times. The gaps follow L1F's
  per-switch probe cost, which is largest in Extension and GlobalCondition.
- **The seven, by handler** (model, cycles per tick, share):

  | handler | cycles/tick | share |
  |---|---|---|
  | S_farcall | 24.9k | 22.6% |
  | S_localload | 16.1k | 14.7% |
  | stepper ops | 6.7k | 6.1% |
  | push | 6.6k | 6.0% |
  | walk steps | 6.3k | 5.7% |
  | S_pushmovlpop | 5.8k | 5.2% |
  | call | 5.4k | 4.9% |
  | subi | 4.3k | 3.9% |
  | linenum | 4.1k | 3.7% |
  | ret | 3.1k | 2.8% |
  | movl_int | 2.7k | 2.4% |
  | addi | 2.6k | 2.4% |
  | farpush | 2.5k | 2.2% |
  | mov | 2.2k | 2.0% |
  | the rest | | under 2% each |

## 8. Lever candidates (exact, engine-generic; ranked by 486 saving)

How the 486 column is scaled is in section 9. The share column is of the per-tick script, 4.25 ms/tick at fixed 40k
(GCL1).

| rank | candidate | fixed 40k ms/tick (share) | 486 ms/tick | exact? | gate |
|---|---|---|---|---|---|
| 1 | **Getter intrinsics** (section 5's six getters, 106 calls/tick) | **-0.42 (9.9%)**, band 0.35-0.50 | **-0.40, band 0.34-0.48** | yes | see 8.1 |
| 2 | **Native handlers for the stepper's memwritelit, memread1 and memwrite1** (61/tick in MMD; each now 110 cycles through DosVmStep, about 25 native) | -0.13 (3.0%) | -0.045 to -0.09 (central -0.07); possibly more, since the stepper is a big switch, cold in the 486's 8 KB cache | yes: the stepper's text, inline | per-instruction trace digest legacy = fast = fastgeneric on the four games; the trace control DIFF; opcode coverage count per game |
| 3 | **Engine-call path trim** | -0.17 alone (all 178 calls + 35 import loads); -0.08 after 1 (the 72 calls left) | -0.06 to -0.12 alone; -0.03 to -0.06 after 1 | yes: the same predicates | as 8.1, plus the slice-3 shadow check on the farcall superinstruction |
| 4 | **More superinstructions** for the joins in 3.3 | -0.13 to -0.15 together (3%) | -0.04 to -0.10 | yes | per superinstruction: shadow check, 0 mismatches on the four games; line/call digest + state digests + instruction count EQUAL vs legacy; its own fixed band; dropped if it misses (code bytes cost on the 486) |
| 5 | **Cheaper call/ret** | -0.07 (1.7%) | -0.025 to -0.05 | yes | line/call digest (call/ret are sync points) + state digests EQUAL; trace control DIFF; MMD intro fixture (CALLAS, room swaps) included |
| -- | all five | about -0.84 (20%) | about -0.5 to -0.8 (central -0.6) | | |

What each candidate does:
- **2, native stepper handlers.** These are rare opcodes in general, but MMD runs them in its hot Extension.
- **3, engine-call path trim.** Three changes:
  - GetByIndexFast's 64-bit bound becomes `index < size()`, which GCC compiles to a multiply: about -21 cycles. The
    same applies to h_movl_imp.
  - The stack-space tests compare against precomputed limit pointers.
  - DirectPtr gets a cheaper type test.

  About -35 cycles a call.
- **4, more superinstructions.** Each saves 4-15 cycles per execution:
  - sourceline + local load (255/tick);
  - jzi + sourceline (184);
  - local load + engine-call argument (157). The intermediate `ax` dies inside the farcall group, so skipping it is
    exact;
  - local load + push (133);
  - push-literal-pop + compare-branch (103);
  - farcall + push of the result (85).
- **5, cheaper call/ret.** About -45 cycles a pair, over 64 pairs:
  - `movl ax,FUNC ; call ax` fused, with the target validated once at decode;
  - an inline PopDataFromStack for `subi sp,N`;
  - ret trimmed.

Not proposed:
- **Inlining leaf script functions.** Every leaf but isAction calls the engine, which can raise an error carrying the
  call stack, so it is not exact (section 4).
- **A faster local-variable walk.** The walk depends on the live stack shape (VM-DESIGN 6). Its 6 cycles per step is
  already tight.
- **Caching anything across ticks.** Not exact.

Outside the VM, noted only. SetButtonPic on an unchanged slot still runs replace_sprite_changed_callback and
FindAndRemoveButtonAnimation (patch 0305 skips only Set*Image), and FindGUIID("MAINGUI") runs 23 times a tick. On the
486 that path was about 0.3-0.45 ms/tick in F1a's samples:
- SetButtonPic 0.090;
- Sc_SetButtonPic 0.069;
- Button_SetNormalGraphic 0.090;
- Button_SetMouseOverGraphic 0.038;
- FindGUIID 0.072 + Sc_FindGUIID 0.052;
- replace_sprite_changed_callback 0.032.

An exact API-side early-out (no animation active, callback a no-op) is a separate candidate. It needs its own audit.

### 8.1 Exactness and gates for the getter intrinsics (engine-generic; nothing MMD-specific)

1. **Recognition is by engine function, never by game.** The decode/fuse pass tags a farcall site whose import
   resolves to one of six engine API functions: Sc_GetGlobalInt, Sc_StrGetCharAt, Sc_strlen, Sc_GetCursorMode,
   Sc_IsGamePaused and Sc_GetPlayerCharacter.
   - Imports can change at run time (room loads; a plugin may re-register a name). So every execution re-checks
     `import->Value.Type == kScValStaticFunction && SPfn == &Sc_X`, one compare, and runs the normal path if not.
2. **The bodies are the engine's own, inline:**
   - GetGlobalInt: `0 <= i < MAXGSVALUES`, else the normal path, so quitprintf and its message happen exactly as
     today.
   - StrGetCharAt: a null string pointer takes the normal path. Otherwise `(posn < 0 || posn >= strlen(s)) ? 0 :
     s[posn]`, as a signed char under -fsigned-char.
   - StrLen: strlen. GetCursorMode: cur_mode. IsGamePaused: game_paused > 0. GetPlayerCharacter: game.playercharacter.
   - The arguments pass through DirectPtr's resolution exactly as the farcall does it.
3. **The state left behind is the same:**
   - ax = SetInt32(result): Type, IValue, Ptr 0, MgrPtr 0, Size 4;
   - next_call_needs_object 0, num_args_to_func -1, was_just_callas -1;
   - the fcs popped by farsubsp's count, including the earlier farpush'd argument;
   - dos_port_work[kDW_ScriptExt] incremented;
   - the lever-2 memo bumped when it is live, for the two getters that are not on its whitelist (GetGlobalInt,
     IsGamePaused).

   What it may skip:
   - The `_pc` sync, the cc_has_error read and the abort test: the intrinsic makes no call-out, and those are only
     observable across one.
   - Whether to write the dead fcs slot beyond the head is the gate's call.
4. **Gates:**
   - The line/call digest + state digests + instruction count EQUAL: legacy vs fast without intrinsics vs fast with
     them. The fixtures:
     - 5 Days room 3 seeded;
     - Trilby's Notes;
     - AGS Quest with its save/restore;
     - MMD character select, MMD intro, and MMD in play (GCL and G).
     The witness build keeps the farcall's sync fold at the same point.
   - A lab intrinsic shadow: each intrinsic hit also runs the real Sc_ call, and the return value, fcs and memo
     generation are compared. 0 mismatches.
   - An intrinsic hit count per game and per getter.
   - The trace control DIFF.
   - Kept Game lines EQUAL.
   - aq-journeys.

## 9. 486 scaling (DOSBox-X understates per-call cost; how I scaled)

- **The VM half: instructions removed inside the loop.** I use r = 486 ms saved per fixed-40k ms saved, at 0.3-0.7.
  - Round E realized r ~0.50. Round C4's release cells gave ~0.34, and its profile cells 0.69 (P4B - P4F).
  - The farcall + localload arm read ~0.24 on displayed % (R4B - R4N, x1 cells).
  - So removing VM instructions buys less on the 486 than at fixed cycles, not more.
- **The API half: removing the call into the engine and the wrapper.** I do not scale this from DOSBox-X at all. I use
  the 486 per-call cost measured directly by F1a's sampling profile on character select, the same per-tick functions
  at the same call rates (CS3):
  - GetGlobalInt, Sc_ + body: 2.3 us a call on the 486, against 1.0 us at fixed 40k (2.3x).
  - StrGetCharAt ~3.6 us (about 2.5x) and StrLen ~3.5 us (about 3x).

  This is where fixed cycles understate. The 486 pays for foreign code in the 8 KB cache, and for the 20-byte result
  stores through its write-through cache.
- **Getter intrinsics:**

  | part | fixed 40k | 486 |
  |---|---|---|
  | VM half | 0.34 ms/tick | x r 0.3-0.7 = 0.10-0.24 ms/tick |
  | API half | 0.08 ms/tick | about 0.24 ms/tick (GetGlobalInt 0.125, StrGetCharAt about 0.07 after keeping its strlen, StrLen about 0.035, the other three about 0.01) |
  | **total** | 0.42 ms/tick | **0.34-0.48 ms/tick, central 0.40** |

  This is below the ~0.65 ms/tick quoted in review. Reaching 0.65 would need r near 1.4 on the VM half, which no round
  has shown.
- **The other candidates.** Their savings are almost all VM instructions, so I used r 0.3-0.7. Candidate 2 might run
  above that, because the stepper is a big switch that is cold in the 486's cache.
- The legacy-era F1a CALLEXT machinery (12 us a call on the 486, about 3.4x fixed) suggests a higher ceiling for the
  VM half of an engine call. I did not use it: it was measured on the legacy Run, not on the fused farcall.

## 10. Margin and 99% (486, GCMP TICKS.BIN shape)

- **Model** (build/l1b/tools/margin2.py; output build/l1b/results/MARGIN.txt).
  - Window: room 2's early stretch, loop ticks 8000-8689. There, drawn ticks already run R3's render level: render
    2.69, scene 4.15, logic 17.82 ms.
  - Logic is shifted -0.55 ms so that the mean drawn tick is the post-R1+R3 central 24.1 ms (17.4 + 2.7 + 4.0).
  - Each lever's saving comes off every tick's logic. The per-tick script is fixed per tick (LAB-L1 P1/P2; CS3, GCL3
    and G3 agree here to 0.1%).

| lever (486 central) | saving ms/tick | mean drawn tick | p95 drawn tick | drawn ticks > 25 ms |
|---|---|---|---|---|
| none (R1 + R3 central) | 0 | 24.10 | 24.86 | 3.7% |
| 5 cheaper call/ret | 0.04 | 24.06 | 24.82 | 3.5% |
| 2 native stepper ops / 4 superinstructions | 0.07 each | 24.03 | 24.79 | 3.2% |
| 3 call-path trim (alone) | 0.09 | 24.01 | 24.77 | 3.1% |
| **1 getter intrinsics** | **0.40 (0.34-0.48)** | **23.70** | **24.46 (24.38-24.52)** | **1.0%** |
| all five | ~0.6 (0.5-0.8) | 23.5 | 24.3 (24.1-24.4) | 0.9% |

**Correction (2026-11-06, later; found in review by sdlports): the table above used the f1prof off-by-one pairing**
(margin2.py keyed TICKS.BIN by raw loop counter; a tick's update_game_once close is stamped lc+1). Re-run grouped by tick
(MARGIN.txt regenerated; old version in git history), same window 8000-8689:

| lever (486 central) | saving ms/tick | mean drawn tick | p95 drawn tick | drawn ticks > 25 ms |
|---|---|---|---|---|
| none (R1 + R3 central) | 0 | 24.10 | **24.27** (was 24.86) | **1.8%** (was 3.7%) |
| 5 cheaper call/ret | 0.04 | 24.06 | 24.23 | 1.6% |
| 2 / 4 | 0.07 | 24.03 | 24.20 | 1.5% |
| 3 call-path trim | 0.09 | 24.01 | 24.18 | 1.5% |
| **1 getter intrinsics** | 0.40 (0.34-0.48) | 23.70 | **23.87** (23.79-23.93) | **1.5%** (was 1.0%) |
| all five | ~0.6 (0.5-0.8) | 23.50 | 23.67 (23.47-23.77) | 1.2-1.5% |

- With correct pairing the window's drawn ticks include the 380 ms click tick at 8118 and a 53 ms tick at 8124, which
  pull the mean drawn tick to 25.34 and so the logic shift to -1.24 (was -0.55); the p95 is lower and the >25 ms share
  is now mostly ticks a 0.4-0.6 ms saving does not bring under. The intrinsics move the >25 ms share 1.8% -> 1.5%, not
  3.7% -> 1.0%: their room-2 margin effect is smaller than stated above.
- The 'sim displ.' column of MARGIN.txt is not a forecast: its lag model has no MAX_CATCHUP / resync (LAB-R2), so one
  380 ms spike costs it ~15 skips; ignore it.
- Unchanged: the 99% verdict for VM levers (none reaches it), and the intrinsics' displayed band in section 3 (+0.3 to
  +2.0 points, central +1.0), which comes from room 1's budget-bound share, not from this table. The intrinsics'
  pre-registration states its margin claim from the corrected table.

- **99%: no candidate reaches it, alone or together.**
- **Room 2.** The drawn ticks still over 25 ms after any of these are spikes: 27-52 ms ticks and the click ticks (380
  ms at 8119). Shaving 0.4-0.6 ms off every tick does not bring them under.
- **The rest of the fixture.** R3's central 96.5% (about 240 skips of about 6,940) breaks down as:
  - room 1, about 125-130 skips: GCB1/GCB2 release real presents per tick, 94.4% / 94.7%;
  - the room-2 entry and first-route hitch;
  - the late-stretch spikes.
- **Room 1 is budget-bound,** so a logic saving helps there.
  - MMD-REMAINDER's linear model (1/pass = about 11 points per ms) is an upper bound. It gives room 1 +4.4 points
    for the intrinsics (+1.5 whole fixture) and about +6.5 (+2.2) for all five.
  - The tail reading is about half that.
  - Whole fixture: about 97-98% (central ~97.5) with the intrinsics, and about 97.5-98.5% (central ~98) with all five.
- **The rest of the way to 99%** needs room 1's render (R2) and the spike sources. These VM levers do not reach them.

## 11. Recommendation: the first L1 lever, and the 486 band to pre-register

**Build the getter intrinsics first** (rank 1):
- **It is the largest exact lever.** It is about two thirds of everything the VM data supports.
- **Its 486 saving rests mostly on measured 486 per-call costs,** not on the r factor that has disappointed before.
- **It is narrow and auditable:** six engine functions, one compare each to recognise them, and the normal path as
  the fallback for everything unusual.
- **It is engine-generic.** It helps any game that polls GetGlobalInt or the string getters per tick, and costs the
  others one compare at the sites it tags.
- **Code size.** It adds about 0.4-0.6 KB to the hot loop. Slice 3 and C4 showed that executed superinstruction code
  did not hurt.

Bands to pre-register (before any data):
- **Fixed 40k** (L1E-style instrumented exe, GCL fixture): per-tick script (L1 entries) 4.25 -> 3.75-3.90 ms/tick,
  central 3.83 (-0.35 to -0.50).
  - Intrinsic hits: GetGlobalInt 55, StrGetCharAt 28, StrLen 16, GetCursorMode 4, IsGamePaused 2 and
    GetPlayerCharacter 1 per tick, exact counts.
  - 0 mismatches in the shadow.
- **486, instrumented profile cell** (GCMP's line, R1 + R3 on, same-binary arms by env): script_vm -0.25 to -0.55
  ms/tick, central -0.40.
  - Falsifier: a saving under 0.15 ms/tick, or any regression.
  - The band is widened on the low side for r's spread, and on the high side because the 486 per-call cost of the
    VM half is not measured on the fast loop.
- **486, release, whole GC fixture, displayed** (R1 + R3 on; intrinsics off -> on, ABBA): +0.3 to +2.0 points,
  central +1.0, almost all in room 1.
  - 99% is not predicted.
  - Falsifier: either B - A < 0 or mean(B - A) < +0.3 points.
- **5 Days S16 guard:** displayed unchanged within 0.2 points.

## 12. Files

- **Write-up:** ~/git/dosags-lab-l1/LAB-L1B.md (this file).
- **Probe:** ~/git/dosags-lab-l1/build/l1b/lab-l1b.diff (654 lines, ASCII), over the L1 state, with
  build/l1b/src/{cc_instance_vm,dos_l1prof}.cpp and build/l1b/orig/. The vendor tree is restored, and L1E.EXE rebuilds
  byte for byte.
- **Scripts:**
  - build/l1b/build.sh;
  - build/l1b/{cell,fix,pair}.sh, copies of build/l1's writing to build/l1b/results;
  - build/l1b/cs.sh, the character select cell.
- **Readers:** build/l1b/tools/{l1bana,model,margin2,profsyms,gameeq}.py; scdis.py and ops.txt from
  archive/lab-mmd-2026-11-04 (ops.txt is used by l1bana).
- **-S:** build/l1b/s/vm.s, the timing build's cc_instance_vm.cpp, identical to L1E's.
- **Results** (build/l1b/results/):
  - GCL3/, G3/, CS3/, SMOKEB/, each with STDOUT.TXT, RUNMANI.LOG, RUN.BAT, L1PROF.TXT and CELL.txt;
  - {GCL3,G3,CS3}-ana.txt (with --perfn --list for GCL3 and G3);
  - {GCL3,G3}-model.txt;
  - MARGIN.txt.

| exe | flavour | sha256 | binary_sha12 | bytes | used for |
|---|---|---|---|---|---|
| build/l1b/exe/L1B.EXE | instrumented; L1E + L1F hooks (DOSAGS_L1VM=1) + L1B counts (DOSAGS_L1B=1); build_dirty=1 | 8161e2490906bded324cc559908b47f10cb37310fdbc92954ace62994acdcdc7 | 5fe904b176ed | 8,809,601 | GCL3, G3, CS3, SMOKEB |
| build/l1/exe/L1E.EXE | (L1's, rebuilt identically after the restore) | 77a393f9a049b55243c87715a496fa53719241479dc8a6ec9110a3881cf66ddf | 70d1d006eea9 | 8,734,278 | restore check |

L1B.EXE is a lab binary for counting. Its timing is not scored, and it is not for the rig.
