# Slice 0 -- `-S` read of the computed-goto VM loop (2026-11-05; compile only)

Scope as defined in VM-DESIGN.md 5 / 2.10: a 6-handler computed-goto sketch, compiled with the
project's real DJGPP cross-compiler and the release build's flags, read in `-S` and in the object.
Nothing in `vendor/` or any tracked file was touched; nothing was run (no DOSBox-X, no hardware); no
commits. Everything is in `~/git/dosags/build/ws/vmstudy/slice0/` (untracked `build/`).

## Verdict

**HARD STOP does NOT fire. The primary mechanism (computed goto) holds.**
- `ip` is in `%ebx` and `this` in a callee-saved register (`%esi` in the 6-handler sketch, `%edi` in
  the 13-handler stress sketch) at every dispatch of every handler. `this` is loaded once from
  `8(%ebp)` in the prologue and never reloaded (exactly 1 reference to `8(%ebp)` in each `.s`); no
  instruction writes the `this` register after the prologue.
- Every handler ends in its own dispatch, `addl $N,%ebx; jmp *(%ebx)` -- 2 instructions (the design
  assumed 4). GCC did not merge the tails: 8 indirect jumps for 7 handlers + entry, 16 for 13 + entry.
  No `-fno-gcse`/`-fno-crossjumping` needed.
- The fallbacks (regparm(3) tail-call handlers; switch over a decoded index) were NOT exercised: the
  condition for trying them (a spill) did not occur.

Caveat, stated plainly: this is a sketch of 6 (and, as an extra, 13) handlers. The full loop
(~30 singles + 8 superops) has not been compiled; the stress sketch is the evidence that adding the
heavy handlers (a fused engine call with calls, loops and a 64-bit counter) does not break the
allocation. The full loop's `-S` remains the gate in slice 2.

## Toolchain and flags (as the release build uses them for `cc_instance.cpp`)

- `~/git/dosags/tools/djgpp/bin/i586-pc-msdosdjgpp-g++`, GCC 12.2.0 (the compiler named in
  `build/ags-release/Engine/CMakeFiles/ags.dir/flags.make`).
- `CXX_DEFINES`, `CXX_INCLUDES` and `CXX_FLAGS` read verbatim from that `flags.make` by `cc.sh`
  (includes `-O3 -DNDEBUG -std=c++11 -fno-strict-aliasing -fwrapv -fsigned-char -DDOSAGS_RELEASE`,
  the NOSIMD defines, `-include .../dos_compat.h`, the same warning set). No extra flags.
- Outputs: `cg.s`/`cg.o` (6 handlers), `cg13.s`/`cg13.o` (13 handlers), assembler listings
  `cg.lst`/`cg13.lst` (`as -al`, for byte offsets), `cg.dis` (objdump -d -r). Analyzer: `analyze.py`
  (follows each handler's hot path from its table label to the dispatch, counts instructions and bytes,
  flags `%ebp`-slot references).

## What was compiled

`common.h`: a stand-in for `ccInstance` with the same member kinds in a similar order (the real
class cannot gain members without editing `vendor/`), the REAL `RuntimeScriptValue`
(`script/runtimescriptvalue.h`), the real `cc_error`/`currentline` declarations, stand-ins for
`new_line_hook`, the import vector, the watchdog clock. `Frame` holds every other `Run()` local and is
address-taken (passed to the out-of-line `StepGeneric`), so it lives at `-N(%ebp)` as designed.

`cg.cpp` (slice 0 as defined): `mov`, `movl_int`, `sourceline` (hook as call-out with `_pc` sync and
abort test), `jzi`, `push` (both always-on stack asserts, SP-type and Data-slot checks to generic),
`ret` (stack assert, invalidate, `POP_CALL_STACK`, start-bit check on the return pc), plus
`h_generic` (one out-of-line legacy step).

`cg13.cpp` (extra, informational): the above + `pop` (J form), `jmpi` with the full backward-jump
watchdog, `LOCAL_LOAD`, `PUSH_MOVL_POP`, `CMP_MOV_JZ` (cmpeq form), `FARPUSH_CALLEXT` (import lookup,
`DirectPtr` fast exit, `dos_port_work` counter, `SPfn` call, `cc_has_error`, abort test, `farsubsp`),
all check-then-commit.

## Per-handler hot path: measured vs the design's hand estimate (x86 instructions incl. dispatch)

The design's estimates (VM-DESIGN 3.1) were body + 4 for dispatch; measured dispatch is 2.

| handler | measured (6-h) | measured (13-h) | design estimate | hot-path bytes (13-h) | `%ebp`-slot refs on the hot path |
|---|---|---|---|---|---|
| mov | 14 | 14 | 16 | 51 | 0 |
| movl_int | 10 | 10 | 12 | 45 | 0 |
| sourceline (no hook) | 8 | 8 | 10 | 33 | 0 |
| jzi | 5 (AX.Ptr set) / 9 | 5 / 9 | 11 | 30 | 0 |
| push | 36 | 34 | 32 | 142 | 1 (a temporary, not ip/this) |
| ret | 40 | 40 | 32 | 181 | 5 (frame fields `curnest`, `loopIterationCheckDisabled`, `dbase`, `startbits` -- by design) |
| pop (J form) | -- | 26 | 26 | 114 | 0 |
| jmpi forward / backward (no poll) | -- | 6 / 25 | 14 (mix) | 21 / 98 | 0 / 5 (frame loop counters, by design) |
| LOCAL_LOAD (3 ops; 2.66 walk steps) | -- | ~47 (33 at 0 steps + 6 per step) | 46 | 116 | 0 |
| PUSH_MOVL_POP (3 ops) | -- | 40 | 39 | 198 | 1 (temporary) |
| CMP_MOV_JZ (3 ops) | -- | 24 | 28 | 116 | 0 |
| FARPUSH_CALLEXT (5 ops, 1 int arg, API body excluded) | -- | 152 | 99 | 569 | 32 (ip parked in a slot across the `DirectPtr` loop and the call, restored to `%ebx` before dispatch; frame fields) |
| generic exit | 18 | 18 | -- | 64 | 3 (`dbase`) |

Reading:
- The simple handlers come in 2 under the estimate (the 2-instruction dispatch).
- `push` +6%, `ret` +25% (frame-field traffic and the start-bit test), the superops within +-10%.
- `FARPUSH_CALLEXT` is +54%. About 30 of its 152 instructions are two divisions by a constant that
  the C++ asked for: `std::vector<ScriptImport>::size()` (sizeof 36) for the import bounds check, and
  the `FunctionCallStack` element count (sizeof 20) in `farsubsp`. Both can be written as pointer
  comparisons (`idx * 36 < end - begin`, `head + n <= end`), which should bring it to ~120. The
  register pressure inside this handler (ip moved to a stack slot across the calls) is live-range
  splitting inside one handler, not a spill across dispatch.

**Effect on the design's fixed-cycles estimate (VM-DESIGN 3.2):** substituting the measured counts
for the units measured here (~78% of the modelled instructions) and keeping hand counts for the rest:
~96-102k x86 instructions/tick for VM + marshalling on MMD-CS (16.5-17.6 per original op), against
the design's paper 95k. With the 1.3-1.6x allowance now applied only to the unmeasured ~24k:
~103-116k, i.e. **~18-20 instructions per op, ~2.8-3.1x fewer than today's ~57** (design band:
21-27, 2.1-2.6x). Recommendation: do NOT move the pre-registered bands on this; the full loop has
more handlers and more pressure, and the lab's history (G, M, L) says estimates fall, not rise. The
486 band (1.7-2.6x) is unchanged: slice 0 says nothing about CPI.

## Hot-loop byte size

| | 6-handler sketch | 13-handler sketch |
|---|---|---|
| whole function (prologue, handlers, cold paths) | 1,002 bytes, 244 instructions | 2,473 bytes, 607 instructions |
| contiguous hot region (first dispatch to first cold block; GCC put the error paths after all handlers) | 608 bytes (0x130-0x390) | ~1,936 bytes (0x1c0-0x950), + ~110 bytes of semi-hot blocks |
| sum of hot paths | 482 bytes (6 handlers) | ~1,750 bytes (13 handlers incl. generic and both jmpi paths) |
| alignment padding | 45 bytes | 85 bytes |

Projection for the full loop (~38 handlers at ~150 bytes each in the 13-handler sketch's hot
region): **~5-6 KB hot, above the design's <= 4 KB target.** The 8 KB 486 cache is shared with data
and with the engine code that runs at every call, so this matters. Levers, in order: drop superops
that do not pay for their bytes (slice 3's per-superop rule), remove the two constant divisions,
move rare branches of hot handlers into `h_generic`, check `-falign-labels`/`-falign-jumps` for this
TU only. The legacy `Run` is 3,365 instructions (~10-12 KB) for comparison.

## Sketch deviations from the final code (none affects the verdict)

- `VMInst` is a stand-in; real member offsets differ (displacement sizes can move bytes, not counts).
- Stand-ins for `new_line_hook`, `simp._imports`, `_maxWhileLoops`, the clock compare.
- `FARPUSH_CALLEXT` handles only the static-function, no-object case; plugin and object calls go to
  `h_generic`, as the design specifies for the fused form.
- The first `cg13` draft violated check-then-commit (pushed, then fell back to generic); fixed before
  the counts above were taken.
