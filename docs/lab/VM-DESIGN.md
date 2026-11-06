# VM-DESIGN -- a structurally faster AGS script interpreter for dosags (design study, 2026-11-05)

Read-only study. Nothing was edited, built or run. Sources read: `vendor/ags` at its HEAD
(f40187689, patch 0354; the DOS-PORT series is applied in that tree, so every line number below is
the PATCHED code), `patches/ags/` (0230, 0293, 0295, 0308 touch `cc_instance.cpp`), and the archived
lab record `git show archive/lab-mmd-2026-11-04:LAB-MMD.md` (cited as LAB-MMD n.m). MMD's bytecode
was read statically from `tests/harness/games/mmd/MANIAC.ags` with the archived `lab-mmd/scdis.py`
parser (read only; no engine involved).

## 0. Summary

- Today's `Run()` spends ~54 x86 instructions per VM op inside the interpreter proper (R_vm ~306k
  instructions/tick at fixed 40000 on MMD-CS, LAB-MMD 17 corrected by 20.1), plus ~2.4/op of CALLEXT
  marshalling and ~10/op of API bodies and wrapper: ~66.5/op for the whole script event after A+B
  (0293/0295); the ~69 figure predates them. **~26 of the 54 are the loop head and back-edge
  (decode, `sccmd_info`, argument-count chain, switch, `_pc` advance) -- ~48% of R_vm.** The rest is
  handler bodies whose cost is dominated by 20-byte `RuntimeScriptValue` traffic (5 loads + 5 stores
  per copy), the backward stack walk for every local variable access, and push/pop invalidation.
- The design: **decode each script once at load into an index-parallel "threaded" stream** (one
  intptr_t per original code word: a handler address in the opcode slot, pre-processed operands in
  the argument slots), run it with **GCC computed-goto dispatch in a new, small function that keeps
  only two values live across dispatch (`ip`, `this`)**, add **eight measured superinstructions**
  that cover ~55% of MMD's ops (local-variable load/store, push-literal-pop, pop-binop-move,
  compare-move-branch, argument push + engine call), and route every rare opcode and every odd case
  through a **frame-based generic stepper** with the legacy semantics. The legacy `Run()` stays
  byte-for-byte as it is, selected at run time (`DOSAGS_VM=legacy|fast|fastnofuse`), so the 486 can
  be measured with a same-binary ABBA (no placement term between arms).
- **Estimate (MMD-CS mix):** paper count ~16 x86 instructions per original VM op for VM + marshalling
  (today ~57); with a 1.3-1.6x allowance for real GCC code over hand counts, **~21-27/op, i.e. 2.1-2.7x
  fewer instructions**. Fixed-cycles script event 9.39 -> ~4.4-5.1 ms/tick. **486: script event ~20 ->
  ~9.5-12.5 ms/tick (central ~10.5), the VM itself ~1.7-2.6x (central ~2.1x)**, because stores into
  the 486's write-through cache are the part this design reduces least (~25% fewer, not 2.5x).
  Logic 24.6 -> ~14-17 ms/tick (central ~15).
- **Plainly:** 2x on the VM is a realistic target; 3x is not supported by this analysis without also
  changing the value representation, which would change behaviour/ABI. And no VM speedup alone gets
  MMD to 99% frames displayed at 40 fps: that needs logic + one render <= 25 ms with a render of up
  to ~15 ms, i.e. logic <= ~10 ms, and even a 3x VM leaves logic at ~11 ms. What this design can
  deliver is MMD at full speed (40 ticks/s) with roughly 55-85% of frames displayed instead of 25%.
- **The known killer is register allocation** (G and its variant failed on it, LAB-MMD 14.5/14.7; I
  and K never got past it, 16-24). The design is shaped around that (two live values, no member `_pc`
  in the loop, no destructible locals, cold paths out of line) and has two designed fallbacks
  (tail-call-threaded handlers; a decoded-index switch). **Slice 0 is a `-S` read with a hard stop,
  before any run.**

---

## 1. How `Run()` spends its instructions today

All lines are `vendor/ags/Engine/script/cc_instance.cpp` unless stated. Counts are MMD-CS at fixed
40000 (probe 0291, 5,642 ops/tick; LAB-MMD 9.3) and the `-S`-based per-handler account (LAB-MMD 17,
`lab-mmd/account.py`, corrected in 20.1: `Run` is entered ~1-2 times a tick, not 65, so the static
total reconciles with the measured R_vm ~308k within ~1%).

### 1.1 The per-op loop (~24-27 x86 instructions per op, ~147k/tick, ~48% of R_vm)

| step | where | what it costs |
|---|---|---|
| loop test `while ((_flags & INSTF_ABORTED) == 0)` | :643 | load + test + branch, every op |
| fetch the code word, mask the instance id | :661-662 | `codeInst->_code[_pc]` (base + index), `and` |
| range check (compiled OUT in release) | :664-665 | `CC_ERROR_IF_RETCODE` is empty unless `DEBUG_CC_EXEC` (:284-320; LAB-MMD 16.3) |
| argument count from the opcode table | :667 | `sccmd_info[op].ArgCount`, a 16-byte-stride table (:53-68, :70-146) |
| end-of-code check (compiled OUT) | :669-670 | as above -- so release has NO bounds check on argument reads |
| argument decode switch | :679-692 | compare chain `cmp 2 / cmp 3 / dec` (up to 9 instrs on 1-arg ops, 7 on 2-arg), then 1 load per argument (0293 made these plain ints, 0295 made them locals) |
| opcode dispatch | :713 | `cmpl $73; ja default; jmp *table(,%eax,4)` |
| back-edge `_pc += op_argc + 1` | :1709 | 3-5 instrs; `_pc` is a MEMBER, so GCC must keep it coherent in memory around every store through a pointer (the build uses `-fno-strict-aliasing`) and every call |

LAB-MMD 17: 24 instructions for 0-argument ops, 27 for 1-argument, 25 for 2-argument.

### 1.2 Handler bodies on the MMD mix (instructions per op including the loop share, per tick)

| op (count/tick) | handler + loop | what the handler does (source) |
|---|---|---|
| `movl` LITTOREG (722) | ~69 total | 0308's DJGPP path :846-848: `SetInt32` (5 stores) then `FixupArgument` (:536-584): a switch on `codeInst->_code_fixups[_pc+2]` every execution; FIXUP_IMPORT (204/tick) calls `SystemImports::GetByIndex` out of line (`systemimports.cpp:179-185`) and copies 20 bytes |
| `mov` REGTOREG (813) | ~44 | :783-789, a 20-byte struct copy |
| `push` (384) | ~80 | `ASSERT_STACK_SPACE_AVAILABLE` (:325-331, two compares, NOT compiled out), `PushValueToStack` (:2343-2349) -> `WriteValue` switch on SP's type then on the slot's type (`runtimescriptvalue.h:411-466`), 20-byte write, `Size = 4`, two member updates |
| `subi` on MAR (430) | ~70 | :766-774 -> `GetStackPtrOffsetRw` (:2398-2415): a backward walk summing entry `Size`s, 2.66 steps per call measured (lsp_steps 1,143,860 / lsp_calls 429,572) |
| `memread4` (454) | ~55 | :858-864 -> `ReadValue` (`runtimescriptvalue.h:363-405`), type switch, 20-byte write; object types call a virtual `ReadInt32` |
| `pop` (299) | ~69 | :1092-1098 -> `PopValueFromStack` (:2361-2369): copy to a temp, `Invalidate()` the slot (5 stores), copy the temp to the register (J, 0312, would remove the temp; not landed) |
| `sourceline` (550) | ~36 | :715-720: two stores and the `new_line_hook` test; almost all of it is loop overhead |
| `farpush` (289) | ~50 | :1448-1453 -> `FunctionCallStack::Push` (:191-201) |
| `farcall` (175) | ~39 VM + ~78 marshalling | :1367-1447: `DirectPtr()` per argument out of line (`runtimescriptvalue.cpp:201-219`, a no-op for plain ints), type dispatch, the API call through `SPfn`, `cc_has_error()`, 20-byte copy into AX |
| `farsubsp` (168), `setfuncargs` (175), `jzi` (183), `cmpeq` (126), `ret` (66), `call` (64), ... | 30-90 each | :1454-1474, :1304-1309, :1070-1076, :928-934, :821-837, :1009-1041 |

Two structural facts behind those numbers:
- **`RuntimeScriptValue` is 20 bytes** (`runtimescriptvalue.h:52-107`: Type, IValue/FValue,
  Ptr, MgrPtr, Size). Every register move, push, pop and memory read is 5 loads + 5 stores; every
  `Set*` is 5 stores. On the 486DX2 the L1 is 8 KB unified and write-through with a 4-entry write
  buffer, so stores drain at bus speed; LAB-MMD 14.4 measured that the stores A+B removed paid
  **~2.8x** their fixed-cycles cost on the 486.
- **Only `SCMD_CALLAS` recurses into `Run`** (:1351); `SCMD_CALL` stays in the same loop (:1009-1041).
  Per-`Run`-entry costs (the `FunctionCallStack` vector, the watchdog `FastClock::now()` at :621) are
  therefore ~1-2 per tick and irrelevant (LAB-MMD 18.6 M and 20.1 L both measured ~0).

### 1.3 Why the 486 pays ~250 cycles per op

Script event ~20 ms/tick on current main (~1.33M cycles at 66 MHz) for 5,642 ops = ~235-250 cycles/op;
VM self ~85% of it is ~200 cycles over ~57 instructions: **CPI ~3.5-3.8**, far above the ~1.5-2 a 486
reaches on cache-resident code. Contributors, all read from the record, none separately measured:
- `Run` is 3,365 instructions (LAB-MMD 23 table), roughly 10-12 KB of code -- larger than the whole L1,
  and every one of the ~175 engine calls a tick runs foreign code through the same 8 KB;
- store traffic (above);
- placement: moving the VM block by 0x80 bytes cost ~0.85 ms/tick on the script event (LAB-MMD 38.4,
  40), i.e. cache-set conflicts are a first-order term.

### 1.4 What the lab already established (constraints on any design)

- **G (packed decode, 0299)** passed every correctness gate and missed its band (-0.025 vs -0.8 to
  -1.8 ms): restructuring the head made GCC spill `_pc` to `-576(%ebp)` and reload `this` from
  `8(%ebp)`; the back-edge grew from 3 to 8 instructions (LAB-MMD 14.5). **G's register-friendly
  variant hit the operator's hard stop at the `-S` read** (14.7). Threaded dispatch (0300) was
  withdrawn unbuilt on that reasoning.
- **I** (unconditional argument loads) was never built: same risk (16, 18.7).
- **K** (`-fomit-frame-pointer`) does not free `%ebp` for `Run`, and makes its allocation worse (23).
- **Per-file flags:** nothing beats the clean flags at fixed cycles; `-mtune=i486` is +0.37 ms at
  fixed cycles, its 486 effect only measurable on hardware (24, 25.2).
- **Rule:** every estimate that rests on helper code uses the helper's dynamic path (18.7).

The common thread: inside one 3,000-instruction function with a member `_pc`, a code-base pointer,
decoded arguments and ~10 more locals, i386's 6 usable registers do not stretch. A design that wants
2x must change the shape of the loop, not trim it.

---

## 2. The design

### 2.1 Overview

```
ResolveImportFixups()  --(end of load, once per primary instance)-->  Decode()
        code[] (unchanged, legacy keeps using it)          dcode[] (new, index-parallel, shared by forks)
                                                          startbits[] (1 bit per word: "an instruction starts here")

Run(curpc):   if (vm_mode != legacy && codeInst->decoded_ok && !debug_run)  return RunFast(curpc);
              ... legacy body unchanged ...

RunFast():    owns the frame (FunctionCallStack etc.), calls RunLoop(frame) -- a noinline function with
              NO destructible locals, computed-goto dispatch, ip + this live, everything else in the frame.
              Rare ops / odd cases -> StepGeneric(frame, pc): one instruction, legacy semantics, from code[].
```

### 2.2 The decoded form

**Index-parallel layout (no pc mapping needed).** `dcode` has the same length as `code` (+3 padding
words). For an instruction at `pc` with `argc` arguments:
- `dcode[pc]` = the address of its handler label (`&&h_xxx`; DJGPP's flat model gives code and data
  the same base, so a label address stored in data is directly `jmp *`-able);
- `dcode[pc+1..pc+argc]` = its arguments, pre-processed by OPCODE (never by handler, so a superop and
  a single handler read the same operand words).

Consequences: `_pc` <-> `ip` is `ip = dbase + pc` (4-byte words on DJGPP); relative jumps, `CALL`
targets loaded from registers, return addresses on the VM stack, export code pointers
(`ResolveExports`, :2146) and `CALLAS` address arithmetic (:1343) all keep meaning exactly what they
mean today; `GetCallStack`/`GetScriptPosition` (:1714-1734) see the same `_pc`.

**Operand pre-processing (per opcode):**

| operand kind | stored as | notes |
|---|---|---|
| register | `reg * sizeof(RuntimeScriptValue)` (byte offset, 0..140) | handlers address `this->_registers` + offset in one addressing mode; decode requires 0 <= reg < 8, else the script is ineligible |
| plain literal | as is | |
| `jzi`/`jnzi`/`jmpi` offset | `(arg + 2) * 4` byte delta (legacy: `_pc += arg` in the handler, then `+= argc+1` at :1709) | target must be inside the code and a start, else the jump is decoded to the generic handler |
| LITTOREG/WRITELIT arg 2, `FIXUP_NOFIXUP` or `FIXUP_FUNCTION` | the int value; handler `movl_int` | `FixupArgument` gives `SetInt32(code)` for both (:542-556) |
| `FIXUP_GLOBALDATA` | `&((ScriptVariable*)code)->RValue`; handler `movl_gvar` | the word already holds the `ScriptVariable*` since load (:2108-2114); `globalvars` is an `unordered_map`, nodes are stable |
| `FIXUP_STRING` | `codeInst->_strings + code`; handler `movl_str` | `_strings` is the ccScript's vector data (:1792), fixed for the instance's life, same for forks |
| `FIXUP_IMPORT` | the import INDEX (as today); handler `movl_imp` does the lookup at run time | see 2.4 |
| `FIXUP_STACK` | raw; generic handler | depends on the live stack (:577-579) |
| any other opcode's argument | the raw word | other handlers ignore fixups today; a GLOBALDATA-rewritten word is read as a raw int there, and stays so |

**Eligibility (all or nothing per script):** the decode walk from pc 0 must find only valid opcodes
(< 74), no instruction running past the end, only valid register operands. If anything fails, the
instance is marked ineligible and **always runs the legacy `Run`** -- a malformed script keeps today's
behaviour (including today's undefined behaviour) by construction. The decode log line reports the
count of ineligible instances (expected 0 on MMD, AGS Quest, 5 Days; to be shown, not assumed).

**Start bitmap:** 1 bit per word, set at every instruction start. Checked only on dynamic transfers
(`CALL`, `RET`, `CALLAS` entry, ~180/tick on MMD): if a target is not a start (never produced by the
compiler), the loop runs `StepGeneric` from that pc until it reaches a start -- which is exactly what
the legacy loop would execute there.

### 2.3 Where it lives, when it is built, what it costs

- Storage: two new members of `ccInstance::ResolvedScriptData` (cc_instance.h:253-269):
  `std::vector<intptr_t> dcode; std::vector<uint32_t> dstart;` plus `bool decoded_ok`. `_scriptData`
  is a `shared_ptr` shared by forks (:1788), so forks (rep-exec-always etc.) reuse it, and a room
  unload frees it with the room's instance.
- Built: at the end of `ResolveImportFixups()` (:2187-2215), i.e. after the `CALLEXT`->`CALLAS` rewrite
  (:2211-2212), which is the last step of instance creation for every game script (script.cpp:270-280)
  and every room (room.cpp:1252-1256), and before any fork is made (script.cpp:285-300,
  room.cpp:1258). `_code` is never written after this point (all writers are :1971, :2114, :2208,
  :2212, all at load). Decode runs in every VM mode so the heap layout is the same in both A/B arms.
- **Memory:** 4 bytes per code word + 1 bit. MMD: global script 130,393 words -> 521.6 KB + 16.3 KB;
  largest room (room2) 67,794 words -> 271.2 KB + 8.5 KB; live at once ~0.82 MB (global + one room;
  536,554 words over all 51 scripts, only ~200k live). 5 Days ~81k words in total, AGS Quest ~24k
  (LAB-MMD 11.4), so tens to ~100 KB live. On a 16 MB machine that is ~5% for MMD. **Physical
  footprint is not measured on this rig** (it has 48 MB; `memory_min_free_kb` is the largest free
  DPMI block, virtual -- PLAN.md 4014); the decode log line should print bytes per instance.
- **Load time:** one linear pass, est. 30-60 x86 instructions per word: ~0.1 s for MMD's global
  script and up to ~0.05-0.1 s for its largest room on the 486 (estimate). It lands inside the room
  load bracket; the ratchet's `journey-room-p95-ms-fixed` must get an explicit allowance, registered
  before the slice that adds decode.

### 2.4 Fixups, imports, strings

- Global data and strings resolve to fixed pointers at decode (table above).
- **Imports stay a run-time lookup, by index, exactly as today.** `SystemImports::Add` overwrites an
  existing slot for non-script symbols (`systemimports.cpp:122-158`), `Remove`/`RemoveScriptExports`
  clear slots (:160-168, :199+), and the `_imports` vector can reallocate on `Add`; room loads add and
  remove room exports. A value or pointer cached at load would be wrong after those (LAB-MMD 11.1; and
  14.1 showed the lookup is only ~5 instructions, so caching buys nothing). The handler inlines
  `GetByIndex` (bounds check + index) through a new one-line inline accessor in `systemimports.h`, and
  copies `Value` (20 bytes) into the register. A null import keeps today's release behaviour: the
  register keeps `SetInt32(index)` and `cc_error("cannot resolve import...")` is raised, then
  execution continues (the `ASSERT_CC_ERROR` after it is empty in release, :313-318).
- `CALLAS`: the instance id stays in the original `code[pc]` word; the rare `CALLAS` handler reads it
  from `code` and looks up `LoadedInstances[instId]` at run time, as today (:1340-1342).
- `FIXUP_STACK`: generic (forward walk at run time, :517-531).

### 2.5 The loop

**Live state across dispatch: `ip` (a local `const intptr_t *`) and `this`.** Everything else is in a
POD frame struct that is a local of `RunLoop` (so it is `%ebp`-relative, needing no register):
`dbase`, `codeInst`, `curnest`, `thisbase[50]`, `funcstart[50]`, `num_args_to_func`,
`next_call_needs_object`, `was_just_callas`, `loopIterationCheckDisabled`, `loopIterations`,
`loopCheckIterations`, `timeout`, a pointer to the `FunctionCallStack` owned by the `RunFast` wrapper
(the wrapper owns everything with a destructor, so `RunLoop` has no EH cleanup edges -- the legacy
`Run` has them, LAB-MMD 23).

**Dispatch:** each handler ends with `ip += n; goto *(void*)*ip;` (3 instructions: add, load, jmp).
GCC 12 supports labels-as-values in C++ mode for every target; nothing in DJGPP restricts it, but
that is to be verified by `-S` in slice 0, including that the dispatch is replicated into handlers
(`-fno-crossjumping` / `-fno-gcse` for this TU only if the `-S` shows the tails merged; GCC's own
manual recommends `-fno-gcse` for computed-goto interpreters). The new code goes in its own TU
(`Engine/script/cc_instance_fast.cpp`, a new patch) so its flags never touch the legacy `Run`.

**`_pc` rule:** the member `_pc` is NOT maintained per instruction. It is written
(`_pc = ip - dbase`) immediately before every call out of the loop (engine API, `CALLAS`'s nested
`Run`, `new_line_hook`, `sys_evt_process_pending`, virtual `ObjMgr` reads/writes, managed-object
helpers, allocators, `cc_error`) and on every exit. External code can only observe `_pc` during such
calls (`GetCallStack`, `GetScriptPosition`, `Abort()`'s `_pc != 0` test at :270-274), so it sees the
same value as with legacy: the pc of the instruction being executed (the legacy member is coherent at
calls for the same reason). On exit after an abort, `_pc` is the next instruction's pc, as legacy
leaves it after :1709.

**Abort rule:** legacy tests `INSTF_ABORTED` before every instruction (:643). The flag is set only by
`ccInstance::Abort()`, whose callers are all engine code (global_game.cpp:444, script.cpp:312-321)
reachable only during a call out of the VM. So the fast loop tests the flag once at entry and after
every handler path that calls out (the same list as the `_pc` rule) -- the first instruction it
would have stopped before is the first one it stops before. Pure handlers (moves, arithmetic, stack,
jumps without the watchdog path) skip the test.

**Errors:** every `cc_error` path is cold and out of line; it syncs `_pc` (and, inside a superop, see
2.6) first, so error texts and the call stack in them are identical.

**Generic stepper:** `StepGeneric(frame, pc)` is a noinline function containing all 74 cases with the
legacy text, operating on the frame instead of `Run`'s locals and reading `code[]`/`code_fixups[]`.
It handles: ops MMD rarely or never runs (`NEWARRAY`, `MEMWRITEPTR`, float ops, `ZEROMEMORY`,
`CREATESTRING`, ...; 42 of the 73 real opcodes never run in MMD-CS), `FIXUP_STACK`, non-start targets, and
the precondition-failure path of every fast handler. A lab mode (`DOSAGS_VM=fastgeneric`) sends EVERY
op through it, which tests the stepper itself against legacy on the fixtures.

**Code size:** the hot function holds ~30 single handlers (~10-30 instructions each) and 8 superops
(~25-100), est. ~1,000 instructions, ~3-4 KB, against the legacy `Run`'s 3,365 instructions. Cold
paths live in `StepGeneric` and small noinline helpers.

### 2.6 Superinstructions

Found by reading MMD's compiled global script (old 2.x compiler output, SCOM v81) and weighting each
per-tick function's static code by its measured dynamic instruction count (LAB-MMD 5.1). Typical
compiler output, `IsOwnTimerExpired` (global script pc 3204-3249):

```
movl ax,400 ; push ax ; mov sp,mar ; subi mar,12 ; memread4 ax ; pop bx ; sub bx,ax ; mov bx,ax
farpush ax ; setfuncargs 1 ; movl ax,IMPORT:GetGlobalInt ; farcall ax ; farsubsp 1
push ax ; movl ax,1 ; pop bx ; cmpeq bx,ax ; mov bx,ax ; jzi +49
```

| superop | pattern (register operands must match exactly) | est. units/tick | ops covered |
|---|---|---|---|
| FARPUSH_CALLEXT | `farpush ax; setfuncargs N; movl ax,<IMPORT>; farcall ax; farsubsp N` | ~205 | 5 each |
| LOCAL_LOAD | `mov sp,mar; subi mar,K; memread4/memread1 R` (R in ax..dx) | ~365 | 3 |
| LOCAL_STORE | `mov sp,mar; subi mar,K; memwrite4/memwrite1 R` | ~45 | 3 |
| TOS_WRITE | `mov sp,mar; memwrite4 ax / memwritelit 4,L; addi sp,4` (declare-and-initialise a local) | ~75 | 3 |
| PUSH_MOVL_POP | `push ax; movl ax,L (int literal); pop bx` | ~140 | 3 |
| POP_BINOP_MOV | `pop bx; add/sub/cmp* bx,ax; mov bx,ax` | ~105 | 3 |
| CMP_MOV_JZ | `cmp* bx,ax; mov bx,ax; jzi/jnzi` | ~75 | 3 |
| BINOP_MOV | `add/sub/cmp* bx,ax; mov bx,ax` | ~75 | 2 |

Together: ~5,600 ops/tick in ~3,300 dispatch units (1.7 ops per dispatch); ~3,100 ops/tick run inside
superops. Counts are from static code weighted per function (method in the appendix); the real
per-tick figure comes from the decode build's own counter in slice 3.

**Exactness rules for every superop:**
1. **Overlap-safe:** a superop lives in the opcode slot of its FIRST instruction; every constituent
   keeps its own handler in its own slot. A jump, call or return into the middle of a pattern runs the
   constituents singly. So groups need no basic-block analysis at all, and patterns may overlap.
2. **Check, then commit:** a superop tests every precondition any constituent could fail or branch
   on (stack space/size asserts :325-347, SP being `kScValStackPtr`, the target slot not being a
   `kScValData` entry, the import being non-null) BEFORE it writes anything. If one fails it jumps to
   the constituents' single handlers from the group's first pc, which raise the error with the correct
   `_pc` and state.
3. **Same final state, including the unglamorous parts:** e.g. PUSH_MOVL_POP must leave `bx` = old
   `ax` with `Size` forced to 4 (the push sets it, :430), the slot at SP `Invalidate()`d (5 zero
   stores; later `ADD SP` and pushes test it, :735 and runtimescriptvalue.h:420), `ax` =
   `SetInt32(L)`, `_stackdataPtr` back where it was. LOCAL_LOAD must leave MAR holding the walked stack
   pointer (MAR is architecturally live after the group); the walk starts from SP, not from MAR
   (:2401), so the intermediate `mov sp,mar` value is dead inside the group. `subi` on MAR only walks
   if MAR's type is a stack pointer (:758), which is why "SP is a stack pointer" is a precondition.
4. **Call-outs end the fused part:** in FARPUSH_CALLEXT the post-call constituent (`farsubsp`) runs
   only after the abort test passes, exactly where legacy would test the flag; on abort the loop
   exits with `_pc` = pc of `farsubsp`; on `cc_has_error()` it exits with `_pc` = pc of `farcall`.
   AX is still written with the import value before the call (it is overwritten after), and
   `was_just_callas = -1`, `next_call_needs_object = 0`, `num_args_to_func = -1` are stored as legacy
   leaves them.
5. Marshalling inside FARPUSH_CALLEXT inlines `DirectPtr`'s fast exit: call it only when
   `Type == kScValGlobalVar || Type == kScValStackPtr || Ptr != nullptr`
   (runtimescriptvalue.cpp:201-219 is a no-op otherwise). `dos_port_work[kDW_ScriptExt]++` (0230) and
   the lab-only instruction counter (which adds the constituent count) stay.

Not fused: `sourceline` (550/tick) stays its own handler (two stores + the hook test + dispatch, ~10
instructions; legacy ~36), so line-number and hook behaviour is literally per instruction, and every
`sourceline` is a sync point for the trace gate (5.2).

### 2.7 Calls and nested instances

- `CALL` (:1009-1041): same `MAXNEST`, `PUSH_CALL_STACK` (:495-503), return address
  `pc + 2` pushed as an int, same `thisbase`/`funcstart` relocation for old scripts, then
  `ip = dbase + target` after a start-bit check.
- `RET` (:821-837): pops the pc, `_returnValue`/exit on pc 0, `POP_CALL_STACK` (:505-512) restoring
  `_lineNumber` and `currentline`, `ip = dbase + pc` after a start-bit check.
- `CALLAS` (:1310-1366, cold handler): legacy code, with `_pc` synced; the nested `Run()` goes through
  the same entry dispatcher, so the callee instance runs fast or legacy by ITS own eligibility. Shared
  `this` (registers, stack, call stack) works as today.
- `CALLEXT` singly (when not fused): legacy text with the `_pc` and abort rules.
- `CallScriptFunction` (:383-492) is untouched; it calls `Run`, which picks the path.

### 2.8 Debugging, line numbers, watchdog, abort, errors

- `DEBUG_CC_EXEC` builds and `SCOPT_DEBUGRUN` (opcode dump, :613-615, :697-709) always use legacy.
- `SCMD_LINENUM`: per instruction, `_lineNumber`, `currentline`, `new_line_hook(this, line)`.
- Watchdog: the entry stamp (:620-621) unchanged; backward `jmpi` runs the same counter, the
  `INSTF_RUNNING` test, `_maxWhileLoops` abort and the 1024-iteration `FastClock` check (:1104-1129);
  its `sys_evt_process_pending()` is a call-out (sync `_pc`, test abort after).
- Stack asserts that are always on (:325-356) are kept in every handler/superop that legacy runs them
  in; the empty-in-release macros stay empty.

### 2.9 The A/B switch

- `DOSAGS_VM` read once at startup (as the other `DOSAGS_*` knobs, e.g. engine.cpp:694):
  `legacy` (default until the 486 decides), `fast`, `fastnofuse` (single handlers only),
  `fastgeneric` (lab: every op through `StepGeneric`), plus a lab bitmask `DOSAGS_VM_FUSE=` to enable
  superops one at a time. Add `DOSAGS_VM` to the RUNMANIFEST env allowlist (patch 0077, quit.cpp:394)
  and print `vm_mode=` in RUNMANIFEST, so every cell records its arm (LAB-MMD 10's lesson about a knob
  missing from the allowlist).
- The check is one test per `Run` entry (1-2 a tick); the hot loop never sees it.
- Both arms are the same binary with the same decode and heap, so a same-binary ABBA removes the
  0.2-0.85 ms placement term that has dogged every VM lever (LAB-MMD 38.4, 41.4, 48.2).

### 2.10 Dispatch mechanism and its fallbacks (decided in slice 0 by `-S`, never by hope)

1. **Primary: computed goto in `RunLoop`.** Pass if, in `-S` at the build's flags: `ip` and `this` sit
   in callee-saved registers in every hot handler with no reload of `this` from the frame, each hot
   handler ends in its own `jmp *`, and the hot handlers' instruction counts are within ~1.3x of
   section 3's table.
2. **Fallback A: tail-call threading.** Each handler a `static` function with
   `__attribute__((regparm(3)))` taking `(ccInstance*, const intptr_t *ip, Frame*)` in
   `%eax/%edx/%ecx` and ending in `return ((Handler)*ip)(self, ip, f);`; the TU built with
   `-fomit-frame-pointer`. Register allocation is then per handler, which removes the failure mode
   G hit. GCC 12 has no `musttail`, so the gate is mechanical: zero `call *` dispatches in `-S`, every
   handler ends in `jmp *`. A missed sibcall grows the C stack per op and would crash within seconds in
   DOSBox-X -- loud, not subtle.
3. **Fallback B: switch over a decoded handler index.** Keeps pre-decode, operand pre-processing and
   superops; gives back ~4-6 instructions/op of dispatch. If both 1 and 2 fail, this is what remains,
   at roughly 1.6-2.0x instead of 2.1-2.7x at fixed cycles.

---

## 3. Estimate

### 3.1 Per-unit hand count (x86 instructions incl. a 4-instruction dispatch; MMD-CS mix)

| unit | units/tick | instr | k instr/tick |
|---|---|---|---|
| FARPUSH_CALLEXT (VM side + marshalling, API body excluded) | 211 | 99 | 20.9 |
| LOCAL_LOAD (walk 2.66 steps, MAR write, read) | 364 | 46 | 16.7 |
| push | 183 | 32 | 5.9 |
| PUSH_MOVL_POP | 142 | 39 | 5.5 |
| sourceline | 548 | 10 | 5.5 |
| movl (int/gvar/str/import variants) | 451 | 12 | 5.4 |
| POP_BINOP_MOV | 105 | 39 | 4.1 |
| farpush (not fused) | 163 | 21 | 3.4 |
| TOS_WRITE | 76 | 44 | 3.3 |
| call / ret | 50 / 84 | 54 / 32 | 2.7 / 2.7 |
| subi leftovers (SP free, plain, unfused walks) | 112 | 24 | 2.7 |
| addi (SP alloc, plain) | 109 | 20 | 2.2 |
| LOCAL_STORE | 43 | 48 | 2.1 |
| CMP_MOV_JZ | 73 | 28 | 2.0 |
| mov / BINOP_MOV / memread4 / memwrite4 | 109 / 77 / 66 / 36 | 16 / 19 / 22 / 24 | 1.7 / 1.5 / 1.4 / 0.9 |
| jmpi, jzi, add, thisaddr, muli, other singles | ~295 | 7-34 | 4.0 |
| **total** | **~3,300 dispatches** | | **~95k** |

Today, same scope: R_vm ~306k + marshalling ~14k = ~320k/tick (~57/op).

### 3.2 Fixed cycles (DOSBox-X, 40000, MMD-CS)

- Paper: ~95k, **~16-17 instructions per original op** (3.4x).
- **Allowance:** these are hand counts, not `-S`. G, M and L all missed because estimates did not
  survive real codegen or dynamic paths (LAB-MMD 14.5, 18.6, 20.1). Applying 1.3-1.6x to the new code:
  **~124-152k, i.e. ~21-27 instructions per op, 2.1-2.6x on VM + marshalling.**
- Script event = that + API bodies ~45k + outside-`Run` ~8k (LAB-MMD 16.9): **~177-205k = ~4.4-5.1
  ms/tick vs 9.39 today (1.8-2.1x on the whole event).**
- Intermediate, unfused fast loop (slice 2): dispatch ~26 -> ~4 per op and cheaper `movl`, R_vm
  ~306k -> ~175k paper, ~190-200k with the allowance: **script event ~6.5-6.7 ms (band 6.0-7.2)**.

### 3.3 The 486

Assumptions, stated: script event on current main ~20 ms/tick (logic 24.6, LAB-MMD 49.10; the VM
measured 20.0 with fine timing on, 48.1); ~85% of it (~17 ms) in the interpreter and ~0.7 ms in
marshalling, ~9% (~1.8 ms) API bodies, ~0.5 ms the rest -- the split the user gave and LAB-MMD 5.1/16.9
support.

Two readings, because the CPI of what remains is the open question:
- **Equal CPI** (time scales with instructions): VM + marshalling 17.7 ms / 2.1-2.6 = 6.8-8.4 ms.
- **Store-weighted** (rough decomposition of today's ~1.18M VM cycles/tick: ~320k instructions at
  ~1.6 CPI, ~35k stores at ~4 extra cycles each, the remaining ~0.5M as cache refills). The new loop
  keeps ~27k stores (RuntimeScriptValue writes are architectural; superops remove ~25% of stores, not
  60%), runs ~124-152k instructions, and touches a 3-4 KB hot loop instead of a 10-12 KB one (refills
  assumed to fall 40-60%): ~0.52-0.67M cycles = 7.8-10 ms.

**Prediction band (to be pre-registered as such): VM + marshalling 6.8-10 ms (central ~8), so the
script event ~9.5-12.5 ms/tick (central ~10.5), saving ~7.5-10.5 ms/tick; VM speedup 1.7-2.6x,
central ~2.1x. MMD logic 24.6 -> ~14-17 ms/tick (central ~15).**

What that buys at 40 ticks/s, with a render pass of up to ~15 ms (an upper bound, PLAN-FPS):
renders per second = (1000 - 40 x logic) / 15: logic 14 -> ~29 (~72% displayed); 15 -> ~27 (67%);
17 -> ~21 (53%). Today 25%.

### 3.4 Effect on other games

In proportion to per-tick bytecode: 5 Days ~44 ops/tick, AGS Quest 7-35 (LAB-MMD 9.3): under
0.05 ms/tick. The decode adds load time and memory to every game; the correctness risk applies to every
game. The payoff is for template-style games that run thousands of ops per tick (MMD's lineage).

---

## 4. Risks

1. **Behaviour drift in superops.** The dangerous details are the ones listed in 2.6(3): Size forced to
   4 on push, `Invalidate` on pop, `kScValData` slots beyond SP (push then writes into the data buffer
   instead, and pop returns the data entry -- runtimescriptvalue.h:418-424), MAR's leftover value,
   `_stackdataPtr`, error `_pc`. Mitigations: check-then-commit, a lab "shadow check" (2 below), and
   the extended trace digest. Residual: a case none of the fixtures reaches.
2. **Rare opcodes.** MMD-CS runs 31 of the 73 real opcodes. The other 42 run through `StepGeneric`, a copy
   of the legacy text: copying is a drift risk of its own, covered only as far as the fixtures run
   those opcodes. Mitigation: `fastgeneric` mode on every fixture; an opcode-coverage count across all
   fixture games (probe 0291 extended), with never-executed opcodes listed as uncovered in the record.
3. **Register allocation (the G mechanism).** Addressed by shape (2 live values, no member `_pc`, no
   EH edges, cold code out of line) and by the slice-0 hard stop with two designed fallbacks. It may
   still fail; then the honest fallback is 2.10(3).
4. **Code size vs the 8 KB cache.** Target: hot loop <= 4 KB, measured from `nm`/`-S`. Superops add
   code; each must pay for its bytes on the 486, not just at fixed cycles. Placement still moves
   absolute numbers by up to ~0.85 ms per link (LAB-MMD 38.4); the same-binary ABBA isolates the VM
   effect, a MAINABS pair gives the absolute.
5. **GCC computed goto under DJGPP.** A GNU extension supported by GCC on all targets; no
   DJGPP-specific obstacle is known, but GCC may merge the replicated dispatch tails (crossjumping,
   gcse) or factor them; checked in slice 0, per-TU flags only.
6. **The 486 CPI of the remainder** (3.3): fixed cycles cannot see it in either direction; only the
   hardware ABBA can. The store share is why the band's low end is 1.7x.
7. **Memory and load time** (2.3): ~0.8 MB live and ~0.1 s per large load on MMD; unmeasured on 16 MB.
8. **A second interpreter to maintain.** It is vendored, pinned code with no upstream merges planned;
   still, any later patch to legacy handlers must be mirrored, and the `fastgeneric` + trace gates are
   the tripwire.
9. **Not risks, checked:** import values and room-change swaps (kept dynamic, 2.4); `CALLAS` instance
   ids (read at run time); exports and code pointers (index-parallel layout); `_code` mutation after
   load (none, 2.3).

---

## 5. Staged plan (smallest slice first; every slice DOSBox-X-gated before any 486 cell)

Every slice: pre-registered fixed-cycles band and falsifier before its first run (LAB-MMD rule,
PLAN-FPS KPI section); stop on a miss. Gates reuse the repo's tools: `tests/ratchet.yaml` via
`.sdl-dos-ports/shared/tools/ratchet.sh --controls` (counts and equalities on DOSBox-X, every check
with a control); the AGS Quest journeys (`aq-journeys`, `journeys-*` rows; `tests/harness/journeys.py`);
`tests/harness/screen-equal.py` freeze-capture screen gate; and the archived lab instruments
`lab-mmd/probe-0291-opcount.diff`, `probe-0292-statewit.diff`, `probe-0302-vmtrace.diff` (+ its
`-control` diff) and `detdiff.py` from `archive/lab-mmd-2026-11-04`. Fixtures as LAB-MMD 9.2/14:
MMD-CS (1000 ticks), AGS Quest AutoPilot, 5 Days `--startr 3` with `DOSAGS_RANDSEED`, MMD-INTRO
(`--startr 40`, rooms 40->49->46->1: blocking cutscenes, nested ticks, room-export swaps), and the
save/restore arms.

**Slice 0 -- `-S` read only (no runs).** `RunLoop` with ~6 handlers (`mov`, `movl_int`, `sourceline`,
`jzi`, `push`, `ret`/exit) plus the generic exit, compiled with the build's flags. Read: `ip`/`this`
registers, `this` reloads, `jmp *` per handler, instruction counts against 3.1. **HARD STOP** if
`ip` or `this` leave their registers: repeat with fallback A; if that fails too, report and decide
on fallback B before any further code.

**Slice 1 -- decoder only, nothing executes it.** Decode + start bitmap + eligibility at load; a lab
verifier that re-derives every instruction's opcode, argc and operands from `dcode` and compares with
`sccmd_info`/`code`/`code_fixups` on every script of every fixture (expected: 0 mismatches, 0
ineligible -- as 0303 did for G). Log: bytes and decode ms per instance. Checks: fixed-cycles script
event unchanged within 0.5%; ratchet full pass; journey room-load p95 within the pre-registered
allowance.

**Slice 2 -- fast loop, single handlers only (`DOSAGS_VM=fastnofuse`).** Gates:
- **per-instruction trace digest** (0302, extended to fold all five fields of all eight registers,
  SP's and `_stackdataPtr`'s offsets): legacy vs fastnofuse EQUAL on all fixtures and save/restore
  arms; `vmops` equal; the 0302 control (one flipped AX bit) DIFFERENT;
- the same with `fastgeneric` (tests `StepGeneric`);
- the statewit determinism guard EQUAL, baseline twice EQUAL, perturbation control DIFFERENT;
- screen gate, and `ratchet.sh --controls` with `DOSAGS_VM=fastnofuse` passed through (`--env`);
- timing: MMD-CS script event in the pre-registered band (6.0-7.2 ms, 3.2); AGS Quest/5 Days within
  noise.

**Slice 3 -- superops, one per sub-slice, largest first** (FARPUSH_CALLEXT, LOCAL_LOAD,
PUSH_MOVL_POP, POP_BINOP_MOV, TOS_WRITE, CMP_MOV_JZ, BINOP_MOV, LOCAL_STORE), each behind its
`DOSAGS_VM_FUSE` bit. Gates per superop:
- **shadow check** (lab build): for every execution, snapshot registers, the stack window
  `[SP-8, SP+2]`, `_stackdataPtr` and the touched stack-data bytes; run the superop; save; restore;
  run the constituents singly; compare everything; mismatches must be 0 on all fixtures (for
  FARPUSH_CALLEXT, the pre-call part);
- **sync-point digest** (folded at every `sourceline`, call-out and `Run` exit, where fused and
  unfused execution coincide) legacy vs fast EQUAL; `vmops` equal (superops add their constituent
  count);
- the decode build's own count of units/tick per superop, replacing the appendix's static estimate;
- per-superop fixed-cycles band; drop any superop whose measured saving is below its band (code size
  on the 486 is not free).
- After all: the full slice-2 gate list with `DOSAGS_VM=fast`; predicted MMD-CS script event 4.4-5.1
  ms at fixed 40000 (band 4.0-5.5).

**Slice 4 -- the 486 (operator approval per round, as now).** Same-binary ABBA, A=`legacy`,
B=`fast`, MMD-CS at the player default, scored with the existing `abba.py` rule. Pre-registered:
script event -7.5 to -10.5 ms/tick, logic 14-17 ms/tick, `tick_rate_steady` >= 39.2. Then a MAINABS
pair for the absolute, and the PLAN-FPS catalogue cells with `fast` to show no regression elsewhere.

**Slice 5 -- default.** Flip the default to `fast` only after slice 4 and a full ratchet; keep
`legacy` selectable in the release flavour for field fallback.

**Optional later (486-only measurable):** store elision in the fast loop's value writers (write only
the fields that differ, e.g. `SetInt32` into a register already holding an integer with null pointers
and Size 4 writes 1 word instead of 5; same for `Invalidate` of an already-invalid slot). Memory
contents are identical by construction; fixed cycles would show it as SLOWER (more instructions), so
only a 486 ABBA can rank it. It attacks the term that caps this design at ~2x.

---

## 6. Infeasible or not proposed (and why)

- **Pre-resolving import values at load:** not exact (2.4).
- **Static local-variable offsets instead of the stack walk:** the stack holds variable-size entries
  (`PushDataToStack`, :2351-2359) and the walk's result depends on them; replacing it needs a proof of
  stack shape per pc. The walk stays (it is the largest single cost left in LOCAL_LOAD).
- **A smaller `RuntimeScriptValue` or untyped registers:** would cut the store traffic that bounds
  this design, but it is the engine-wide script API/ABI (`ScriptAPIFunction` takes
  `RuntimeScriptValue` arrays; plugins); out of scope for a behaviour-identical change.
- **A JIT to x86:** DJGPP's flat model would make heap code executable in principle, but error
  positions, abort, watchdog, nested instances and the debugger hooks would all need re-proving in
  generated code; not proposed.
- **3x on the VM, or 99% displayed at 40 fps on MMD from the VM alone:** see 0 and 3.3.
- **Running `repeatedly_execute` less often, caching `GetLocationName`/`GetLocationType` across
  ticks:** changes script-visible behaviour (LAB-MMD 11.8); not proposed.

---

## Appendix: how the idiom counts were made

Static, read-only: `scdis.py`'s `parse()`/`walk()` over `ac2game.dta`'s SCOM block in
`tests/harness/games/mmd/MANIAC.ags` (130,393 words, 386 imports, SCOM v81). For each per-tick function
(CheckTimers, SetAlternativeAction, Extension, IsOwnTimerExpired, GlobalCondition, repeatedly_execute,
CheckDefaultAction, UpdateActionBar, TranslateAction), its static instruction list was weighted by
(dynamic exclusive instructions/tick from LAB-MMD 5.1) / (static instruction count), then patterns were
matched greedily (superops not spanning a jump target, for the count only -- correctness does not need
that restriction, 2.6(1)). Weighted total 5,442 ops/tick against probe 0291's 5,642; scaled up by
1.037. Uniform weighting inside a function is an approximation (e.g. `repeatedly_execute` runs 406 of
its 3,031 static instructions a tick); slice 3's own counter replaces it. The opcode histogram used in
section 1 is probe 0291's raw output,
`archive/lab-mmd-2026-11-04:tests/harness/results/MMDOC-1-2026-09-23/STDOUT.TXT`.
