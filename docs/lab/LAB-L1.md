# LAB-L1 -- MMD in play: is the script interpreter's cost fixed per tick or click-driven? (lab worktree ~/git/dosags-lab-l1)

Copied into the main repo 2026-11-06 from the lab worktree (base 759de2b1 + lab-play.diff) as the lab record that scores
docs/lab/L1-PREREG.md P1/P2; diffs and the reader l1ana.py in docs/lab/l1-lab-patches/, per-cell analyses in
docs/lab/l1-results/. Exes are lab-only (build_dirty=1) and are not committed.

Lab only. Answers docs/lab/L1-PREREG.md (main 759de2b1, written before any L1 data; not edited). No lever built. Nothing
committed anywhere; ~/git/dosags, ~/git/dosags-r1land, ~/git/dosags-lab-r3 and ~/git/dosags-nightly untouched; no rig or
vcctrl use. All times are DOSBox-X fixed-40000 emulated time unless a row says 486. P1 and P2 are scored as shares and
ratios, never as DOSBox-X ms.

## 0. Answer first

- **P1 MET.** Per-tick entries carry 98.0% (GCL, 16 walk clicks), 97.5% (fixture G) and 100.0% (GC0, no input) of
  script_vm. Central was 98%, falsifier < 90%.
- **P2 MET.** On input-free ticks, script_vm/tick is 0.982x the all-tick mean in GCL and 0.983x in G (-1.8% / -1.7%).
  The band was +-10%; the falsifier was input-free more than 15% lower.
- **P3 is not scored here.** See section 9 (scoping note).
- The per-tick cost is one function: the global script's `repeatedly_execute`. It is 95.0% of script_vm in GCL and runs
  4.12 ms/tick on input-free ticks and 4.13 on input-near ticks. Room rep_exec (`room_c` in room 1, `room_b` in room 2) is
  3.0-4.3%. MMD has no script modules and no repeatedly_execute_always: rep_exec_vm runs 6 times in a whole run, as on
  the 486 (GCMP: 6).
- Click handlers are small, and most of their time is engine work, not interpreter work. `on_mouse_click` costs 33 ms per
  click on average (one 244 ms click on a long room-2 walk). 98% of that is the engine API `Room::ProcessClick`
  (pathfinding / walk setup); the interpreter's own part is 0.5 ms per click.
- Inside the per-tick script (level 2, exclusive time):
  - The interpreter (VM) is **75-79%** and engine API calls are **21-25%**, after the probe bound in section 6.1. Raw
    figures are 79.0% / 21.0%.
  - Scripts make about 180 API calls a tick. GetGlobalInt is called 55 times a tick, StrGetCharAt 28, FindGUIID 23,
    SetButtonPic 20 and StrLen 16.
  - Seven verb-bar template functions carry 90% of VM time: Extension, SetAlternativeAction, CheckTimers, GlobalCondition,
    IsOwnTimerExpired, CheckDefaultAction and repeatedly_execute.
- 486 cross-check (coarse, GCMP TICKS.BIN). On the 16 click ticks, the whole tick's cost above the median of its
  neighbours sums to 0.78 s. That is 0.91% of GCMP's 84.8 s script_vm, and it bounds the 486's click-driven share near 1%.
  GCMP's largest single script_vm entry is 352 ms, the size of the 244 ms DOSBox-X click.

## 1. Setup

- Worktree `git -C ~/git/dosags worktree add --detach ~/git/dosags-lab-l1 759de2b1`.
  - vendor/ags (94e271df) and vendor/SDL (74a74628) are cloned from ~/git/dosags/vendor at the manifest pins.
  - `make patches` gives series fingerprint 3ecc4317438f. patches/ is identical at 579c0b5c and 759de2b1.
  - Then `git apply ~/git/dosags-lab-play/lab-play.diff`.
  - Copied in (untracked): vendor/cwsdpmi, tests/harness/games/{mmd,agsquest} and the tools/djgpp symlink.
  - tools/waitfor.sh is copied from main (2210af37). Every background wait uses it, with a pid file and a timeout.
- Check: `make all` on lab-play.diff alone gives build/l1/exe/R1INS.EXE, **byte-identical to LAB-PLAY's R1INS** (sha256
  f5089493..., the GCINS/GCMP exe).
- Conf tests/harness/confs/dosbox-x-fixed40k-opl3.conf (cputype pentium_slow, core normal, cycles fixed 40000). Sound ON,
  using trilbysnotes ACSETUP-ON-512X384-ROUND.CFG as ACSETUP.CFG. Fixed timestep, fine timing on.
- Every cell runs with DOSAGS_GUI_CLIP=2 (R1 on) and DOSAGS_RANDSEED=1. The restore is save 007 from
  ~/git/dosags/build/ws/roundQ/AGSSAVE.007 (sha256 f486d0e9..., the same as roundGC's), via `--loadsavedgame 7`.
  At most two DOSBox-X instances run at once, on displays 386/387.
- Fixtures (build/l1/fix.sh):
  - **GC0** = the P9/GC fixture verbatim: TAS exit 12440, no input. The kid stands in room 1 for 7,003 ticks.
  - **GCL** = GC0 plus 16 DOSAGS_LABCLICKS walk clicks at GCMP's own click ticks, taken from GCMP's TICKS.BIN:
    6178 6510 6974 7205 7543 7890 8118 8519 8772 9253 9566 9935 10244 10722 11063 12136.
    - Room 1 alternates (250,135)/(60,135). The click at 7890 is (1,135) and walks to the left edge, so room 2 is entered
      at lc 7972 (GCMP: 7900).
    - Room 2 alternates (40,130)/(300,130).
    - This is the DOSBox-X stand-in for GCMP's host-held PS/2 clicks, whose game positions are not recorded.
  - **G** = lab fixture G (LAB-PLAY 1 / LAB-R3 1): exit 8600. It has 5 walk clicks and 9 pointer moves, including verb-bar
    hovers, and enters room 2 at lc 6882.
- **DOS environment trap.** GCL's RUN.BAT reached 522 SET bytes with DOSAGS_TICKLOG. That is at the ~520 limit, though
  that run lost nothing. GCL therefore runs without TICKLOG (NOTL=1, 496 SET bytes); its room entries come from the L1
  entry labels. Every scored cell was checked for three witnesses:
  - STDOUT `fixed-timestep: ENABLED`;
  - `DOS-PORT guiclip DOSAGS_GUI_CLIP=2 mode=2`;
  - script_vm recorded in RUNMANI.LOG, which proves that the last SET (DOSAGS_TICKSTATS_FINE) survived.
  All three are present in every cell in section 3.

## 2. Instrumentation (lab only; lab-l1.diff over lab-play.diff, lab-l1-full.diff = whole vendor/ags diff; ASCII)

DOSAGS_L1PROF (read once at ags_entry_point; unset or 0 = off, and every hook is then one test).
Main file: vendor/ags/Engine/main/dos_l1prof.{h,cpp}.

- **Level 1 (entries; exe L1E).**
  - script.cpp brackets every script_vm entry. The bracket sits inside the existing script_vm uclock bracket of
    RunScriptFunction, around CallScriptFunction. Each record holds:
    - the loop counter at start and end, and the depth;
    - the instance (game / roomN / modN / dialogs) and the function name;
    - the event context (process_event's type, sub-type and room event, set by a scope in event.cpp);
    - its us, and the us of game loops nested inside it (blocking calls; UpdateGameOnce while an entry is open).
  - rep_exec_vm entries (DoRunScriptFuncCantBlock) are logged the same way, as kind 1.
  - Output goes to L1PROF.TXT at exit (quit.cpp, beside TICKS.BIN).
  - The L1 entries sum to 97.7-98.3% of tickstats script_vm. The remainder is the outer bracket's own reads.
- **Level 2 (buckets; exe L1F, the same source with `#define DOSAGS_L1VM 1` in cc_instance_vm.cpp).**
  - The fast VM is hooked at:
    - entry and exit (DosVmRun, and the legacy Run branch of DosVmEnter);
    - h_call and h_ret (the new pc goes to a function, through the script's export table);
    - h_callext and h_s_farcall (the API function goes to its name, through a reverse lookup of simp);
    - the generic stepper's CALL, RET and CALLEXT.
  - Exclusive time is kept per script function, per API function, and per (caller function, API) pair. Nested game loops
    get their own bucket.
  - The level-2 clock is RDTSC. Under cputype pentium_slow, DOSBox-X counts emulated cycles, so this is emulated time:
    measured 39.9993 ticks/us against uclock over the run. A uclock read costs 4.7 us of emulated time (calibrated), too
    much for ~490 switches a tick.
  - Each hook reads the clock twice. The bookkeeping between the two reads goes to a separate probe category, not to
    any bucket.
  - legacy_runs = 0 in every cell: every MMD script runs in the fast VM.
- **Inertness.** Game output ('Game :' lines with every *_ms/_us/t_ms timing field removed) is **EQUAL** (108 of 108
  lines) across four GCL cells: R1INS (GCLREF), L1E unset (GCL0), L1E level 1 (GCL1) and L1F level 2 (GCL2). G1 vs G2
  (75 lines) and GC01 vs GC02 are also EQUAL.
  script_vm totals in GCL:
  | cell | script_vm total | vs R1INS |
  |---|---|---|
  | R1INS (GCLREF) | 30.339 s | reference |
  | L1E unset (GCL0) | 30.400 s | +0.2% |
  | L1E level 1 (GCL1) | 30.955 s | +2.0% (the entry reads) |
  | L1F level 2 (GCL2) | 43.208 s | +42% (probe; level 2 is attribution only, never scored for P1/P2) |

## 3. Cells

| cell | exe | L1PROF | fixture | ticks (window) | inputs | witnesses | used for |
|---|---|---|---|---|---|---|---|
| GCL1 | L1E | 1 | GCL | 5437-12439 (7003) | 16 clicks | FT on, mode=2, fine on, 496 B | **P1, P2** |
| G1 | L1E | 1 | G | 5437-8599 (3163) | 5 clicks + 9 moves | FT on, mode=2, fine on, 511 B | **P1, P2** |
| GC01 | L1E | 1 | GC0 | 5437-12439 (7003) | none | FT on, mode=2, fine on, 297 B | P1 (P2 is vacuous: no input tick) |
| GCL2 / G2 / GC02 | L1F | 2 | GCL / G / GC0 | as above | as above | as above | functions, API calls (sections 5-6) |
| GCLREF | R1INS | - | GCL | 7003 | 16 clicks | as above, 475 B | inertness reference |
| GCL0 | L1E | unset | GCL | 7003 | 16 clicks | as above | inertness |
The window runs from the first `repeatedly_execute` after the restore (lc 5437) to the TAS exit, as GCMP's 7,004 ticks
do. Input means a labclick or labmove line (STDOUT) or a dequeued click or key (TICKS.BIN). Input-free means no input
within +-40 ticks.

## 4. P1 and P2

| | GCL1 | G1 | GC01 | prereg |
|---|---|---|---|---|
| script_vm entries/tick | 2.003 | 2.003 | 2.000 | 486 GCMP: 2.00 (14,041 over 7,004) |
| per-tick entries' share of script_vm (**P1**) | **98.01%** | **97.46%** | 100.00% | >= 95% MET (central 98); < 90% falsifies |
| game loops nested in entries (blocking) | 0 | 0 | 0 | -- |
| input-free ticks / all-tick mean (**P2**) | **0.9823 (-1.77%)**, 5707 of 7003 ticks | **0.9830 (-1.70%)**, 2029 of 3163 | 1.0000 (vacuous) | within +-10% MET; > 15% lower falsifies |
| input-near ticks / all-tick mean | 1.078 | 1.030 | -- | information |
| per-tick script_vm p05 / p50 / p95 / max (ms) | 4.110 / 4.267 / 4.274 / 244.3 | 4.116 / 4.272 / 4.280 / 244.5 | 4.110 / 4.110 / 4.116 / 59.0 | information |
- **P1 MET and P2 MET** on both scored cells. The level-2 cells agree: P1 98.54 / 98.09 / 100.00%, P2 -1.17 / -1.19%.
- Neither the walk clicks nor the verb-bar hovers move the per-tick script. Their only effect is the one-off entries on
  click ticks and the room-entry handlers.

## 5. script_vm per entry point and per tick class (level 1; ms per tick of the class; n entries)

GCL1 (7003 ticks: 5707 input-free, 1296 input within +-40):
| class | entry point | n | share | input-free ms/tick | input-near ms/tick |
|---|---|---|---|---|---|
| per-tick | game repeatedly_execute | 7002 | 94.99% | 4.116 | 4.131 |
| event | game on_mouse_click (kTS_MouseClick) | 16 | 1.76% | 0 | 0.411 |
| per-tick | room2 rep_exec (room_b) | 4467 | 1.69% | 0.074 | 0.071 |
| per-tick | room1 rep_exec (room_c) | 2535 | 1.33% | 0.057 | 0.060 |
| event | room2 before-fadein (room_a) | 1 | 0.15% | 0.008 | 0 |
| event | room2 after-fadein (room_c) | 1 | 0.07% | 0.003 | 0 |
| event | room1 region1_a, on_event x4 | 5 | 0.01% | 0.001 | 0 |
| | **total** | 14027 | | **4.259** | **4.673** |

G1 (3163 ticks: 2029 input-free, 1134 input within +-40):
| class | entry point | n | share | input-free ms/tick | input-near ms/tick |
|---|---|---|---|---|---|
| per-tick | game repeatedly_execute | 3162 | 94.31% | 4.122 | 4.113 |
| event | game on_mouse_click | 5 | 2.03% | 0 | 0.248 |
| per-tick | room1 rep_exec (room_c) | 1445 | 1.67% | 0.069 | 0.080 |
| per-tick | room2 rep_exec (room_b) | 1717 | 1.47% | 0.067 | 0.060 |
| event | room2 room_a / room_c / region1_a / on_event | 6 | 0.53% | 0.035 | 0 |
| | **total** | 6336 | | **4.293** | **4.500** |

GC01 (no input): repeatedly_execute 3.957 ms/tick (95.70%) and room1 room_c 0.178 (4.30%); total 4.134.
Every entry is top level: no script_vm entry nests inside another, and no blocking call runs a game loop inside an entry.

Event entries split between the interpreter and the engine (GCL2, level 2): 626 ms in total, of which VM 7.8 ms and API
595 ms. Room::ProcessClick^3 is 518 ms of the API part (16 calls) and room_a's RemoveWalkableArea 47 ms (1 call).
**The click-driven cost is engine work called from the click handler, not interpreter work.**

## 6. What the per-tick script does (level 2, exclusive emulated time, whole played run)

### 6.1 Interpreter vs engine API in the per-tick entries
| cell | VM ms/tick (raw) | API ms/tick | outside-VM (CallScriptFunction) | API calls/tick | probe (excluded) |
|---|---|---|---|---|---|
| GCL2 | 3.757 | 0.996 | 0.197 | 178.5 | 1.041 |
| G2 | 3.755 | 1.002 | 0.202 | 179.1 | 1.047 |
| GC02 | 3.747 | 0.879 | 0.198 | 183.0 | 1.065 |
- Probe bound. Level 1's per-tick entries cost 4.250 ms/tick in GCL1. Level 2's VM + API + outside sum to 4.950, so
  ~0.70 ms/tick of hook call and return cost, about 1.4 us per bucket switch, is left inside the buckets. Where the hooks sit,
  most of it probably falls in the calling (VM) functions.
- With all of it taken off the VM: VM 75.4%, API 24.6%. With none taken off (raw): VM 79.0%, API 21.0%. **So the VM is
  75-79% and the API 21-25% of the per-tick script's own time.**
- For comparison, MMD-REMAINDER read 77% / 23% from the 486 F1a sampling profile.

### 6.2 Top script functions (GCL2; segments = switches into the function: one per call plus one per return into it)
| function | segments/tick | VM ms/tick | of VM |
|---|---|---|---|
| game::Extension(1) | 56.0 | 0.890 | 23.7% |
| game::SetAlternativeAction(3) | 56.0 | 0.688 | 18.3% |
| game::CheckTimers(0) | 31.0 | 0.569 | 15.1% |
| game::GlobalCondition(1) | 22.0 | 0.356 | 9.5% |
| game::IsOwnTimerExpired(1) | 48.0 | 0.346 | 9.2% |
| game::CheckDefaultAction(0) | 25.0 | 0.295 | 7.8% |
| game::repeatedly_execute(0) | 34.0 | 0.273 | 7.3% |
| game::UpdateActionBar(0) | 11.0 | 0.109 | 2.9% |
| game::TranslateAction(4) | 6.0 | 0.064 | 1.7% |
| game::AddExtension(2) / isAction(1) / RemoveExtension(1) | 5.0 / 5.0 / 4.0 | 0.048 / 0.041 / 0.037 | 3.3% |
| room1::room_c / room2::room_b (room rep_exec) | 3.6 / 1.9 | 0.025 / 0.020 | 1.2% |
- The first seven are 90.9% of VM time. G2 and GC02 give the same figures to within +-0.02 ms. These are the verb-bar
  template's per-tick functions: the default-verb extension parsed out of the location name, the alternative-action
  button pictures, global-int timers, and the hover/condition tests. They do the same work every tick whatever the input.

### 6.3 Engine API calls made from scripts per tick (GCL2; exclusive time; % of the per-tick VM+API)
| API | calls/tick | ms/tick | share of VM+API | main callers |
|---|---|---|---|---|
| SetButtonPic | 20.0 | 0.164 | 3.4% | SetAlternativeAction 18, repeatedly_execute 2 |
| GetGlobalInt | 55.3 | 0.124 | 2.6% | CheckTimers 30, IsOwnTimerExpired 24 |
| FindGUIID | 23.0 | 0.097 | 2.0% | SetAlternativeAction 18, repeatedly_execute 2, UpdateActionBar 2 |
| GetLocationType | 3.0 | 0.091 | 1.9% | CheckDefaultAction 2, GlobalCondition 1 |
| StrGetCharAt | 28.0 | 0.078 | 1.6% | Extension 28 |
| GetLocationName | 1.0 | 0.071 | 1.5% | CheckDefaultAction 1 |
| StrCopy | 6.0 | 0.066 | 1.4% | TranslateAction 2, CheckDefaultAction 2, UpdateActionBar 2 |
| GetInvAt | 5.0 | 0.059 | 1.2% | GlobalCondition 3, CheckDefaultAction 2 |
| StrContains | 1.0 | 0.055 | 1.2% | TranslateAction |
| StrFormat | 1.0 | 0.052 | 1.1% | TranslateAction |
| StrLen | 16.0 | 0.037 | 0.8% | Extension 14 |
| GetGUIObjectAt | 2.0 | 0.024 | 0.5% | GlobalCondition |
| SetLabelText / GetGUIAt / StrCat / IsTimerExpired / GetCursorMode / GetTranslation / StrSetCharAt / IsGamePaused / SetLabelColor / GetPlayerCharacter | 1-4 each | 0.002-0.012 each | 1.3% together | |
| (event only) Room::ProcessClick | 16 per run | 0.074 averaged | -- | on_mouse_click |
- GetLocationType and GetLocationName depend on where the pointer is. With the pointer parked top-left (GC0) they cost
  0.023 + 0.020 ms/tick. Over the room (GCL) they cost 0.091 + 0.071. That is the GetCharIDAtRoom path, with lever 2's
  memo already on by default.
- FindGUIID already has a 16-entry cache (DOS port), and SetButtonPic already skips an unchanged slot (patch 0305).
  What is left in both is the API call path itself: about 4-8 us a call at fixed 40000.

## 7. MMD-REMAINDER rows 1-6

| row | verdict from L1 |
|---|---|
| 1 character update early-outs | Outside script_vm; L1 neither supports nor kills it. Lever 1 has already landed (0363/0365, on by default). |
| 2 GetCharIDAtRoom via GetLocationName/Type | **Weakened.** With lever 2's memo in, the whole GetLocationName + GetLocationType cost is 0.04 ms/tick idle to 0.16 ms/tick with the pointer in the room: 1-3.4% of the per-tick VM+API. Any further cut is a fraction of that. |
| 3 cc_has_error + GetGUIAt | cc_has_error is already inline (lever 3). GetGUIAt runs **1 call/tick in play** (14 on character select), 0.007-0.011 ms/tick = 0.2%. **Killed** as a lever. |
| 4 formatting | StrFormat 1 call/tick, 0.052 ms/tick (1.1%), and the output is script-visible. LEVERS-REPORT counted 0 debug_script_log calls a tick. **Killed** for MMD in play. |
| 5 uclock in the release flavour | Outside L1 (L1 runs the instrumented flavour with fine timing on); not tested. |
| 6 VM remainder | **Supported, and it is the bulk.** The interpreter is 75-79% of the per-tick script's time, and 91% of that is in seven template functions that do the same work every tick. |
The prereg's branch (P1 and P2 hold) says "target the per-tick scripts' API calls (rows 2-4) and the VM's per-instruction
cost". The data splits that: rows 2-4 are small and already cut, and the VM is three quarters of the per-tick time.

## 8. Proposed lever shape for L1 (a proposal only; nothing built)

1. **Primary: the fast VM's cost inside the seven per-tick template functions.**
   - These are Extension, SetAlternativeAction, CheckTimers, GlobalCondition, IsOwnTimerExpired, CheckDefaultAction and
     repeatedly_execute: 3.4 of 3.76 VM ms/tick here, ~300 VM segments a tick, and ~180 API calls a tick.
   - The first step is a measurement, not a lever: a per-function opcode / superinstruction histogram of these seven,
     taken with a VMTRACE-style counting build, at instruction level, which L1 did not measure.
   - That histogram picks between the candidate shapes:
     - superinstructions for their hot sequences (string-char loops in Extension, global-int reads and compares in the
       timer functions, button-pic setup in SetAlternativeAction);
     - a cheaper script-to-script call/ret for leaf functions.
   - Exactness gates as for slices 2-3: the line/call digest, the per-instruction digest and the state digests.
2. **Secondary, exact, small: the API call path for the trivial getters.**
   - GetGlobalInt (55/tick), StrGetCharAt (28), StrLen (16), GetCursorMode (4), IsGamePaused (2) and GetPlayerCharacter
     (1): ~106 calls a tick, 0.26 ms/tick of exclusive API time here (5.4% of VM+API).
   - Their bodies are a few loads. A VM intrinsic per function, recognised through the import at decode time and done
     inline in h_s_farcall, would skip the RuntimeScriptValue wrapper and the API macro.
   - On the 486, F1a found the per-call cost far above the instruction count. This is the class of cost that fixed cycles
     understate.
3. **Not L1:** the click handlers (0.8-2% of script_vm, and mostly pathfinding); rows 2-4 (above).
The 486 effect cannot be read from these DOSBox-X ms. For scale only (not a prediction): GCMP script_vm 12.11 ms/tick
against GCL1's 4.34 is a ratio of ~2.8.

## 9. Scoping note: P3 (coordinator, 2026-11-06)

**P3 (R1 build in play, 486: script_vm 11.0-13.2 ms/tick, central 12.1) is not scored in the lab.** DOSBox-X absolute ms
are not 486 ms. P3 is scored from the instrumented in-play cell of the upcoming R1 confirmation round, which runs the same
exe flavour as GCMP with 0366 in. **P1 and P2 are scored here, in the lab, as attribution shares and ratios** (section 4).

## 10. Files

- Write-up: ~/git/dosags-lab-l1/LAB-L1.md (this file).
- Diffs: ~/git/dosags-lab-l1/lab-l1.diff holds the L1 hooks over lab-play.diff. ~/git/dosags-lab-l1/lab-l1-full.diff is
  the whole vendor/ags working-tree diff over the 0365 head (lab-play + L1, new files included).
  vendor/ags/Engine/script/cc_instance_vm.cpp is left at `#define DOSAGS_L1VM 0`.
- Scripts:
  - build/l1/cell.sh: one cell, based on LAB-R3's.
  - build/l1/fix.sh: fixtures GC0 / GCL / G / S.
  - build/l1/pair.sh: two cells on displays 386/387, waited with tools/waitfor.sh.
  - build/l1/rest.sh and build/l1/build2.sh.
- Reader: `python3 -I build/l1/tools/l1ana.py build/l1/results/<CELL> [--pad 40] [--top N]`. Its outputs are
  build/l1/results/<CELL>-ana.txt.
- Results: build/l1/results/{GCL1,GCL2,G1,G2,GC01,GC02,GCLREF,GCL0}/, holding STDOUT.TXT, RUNMANI.LOG, RUN.BAT,
  L1PROF.TXT, TICKS.BIN (not GCL) and CELL.txt.
  - SMOKE1 and SMOKE2 are early probes. results/old/ holds the first GCL pair, which ran on the earlier L1F with the
    probe cost inside the buckets; it is not scored.

| exe (build/l1/exe/) | flavour | sha256 | binary_sha12 | bytes | used for |
|---|---|---|---|---|---|
| L1E.EXE | instrumented, lab-play + L1 entries (DOSAGS_L1VM=0) | 77a393f9a049b55243c87715a496fa53719241479dc8a6ec9110a3881cf66ddf | 70d1d006eea9 | 8,734,278 | **P1/P2 (GCL1, G1, GC01)**, GCL0 |
| L1F.EXE | instrumented, L1E + VM hooks (DOSAGS_L1VM=1) | 83d5b4d23ba67907166c80780bea0079758dd6df711fa82ed0be25e78a04ea1f | 7ebf2aa7d7ab | 8,734,790 | level-2 attribution (GCL2, G2, GC02) |
| R1INS.EXE | lab-play only (= LAB-PLAY R1INS = GCINS) | f5089493b1a828198cb0ebfaa3b7f8b9d944b203a55507b67884762483cea044 | 5dc54892ad56 | 8,696,018 | build check, GCLREF |
All three carry build_dirty=1 (uncommitted lab edits in vendor/ags). They are lab binaries, not for the rig.
