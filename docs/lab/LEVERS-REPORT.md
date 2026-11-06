# Levers 3 / 4 / 1 / 2 outside the VM -- REPORT (lab only)

## 0. PRE-REGISTRATION of the fixed-40000 timing band for lever 3 (written 2026-11-06T06:09:02Z, BEFORE its timing run)
- Change: cc_has_error() after every engine call in the fast loop (h_callext, h_s_farcall) becomes an inline read of
  ccError.HasError (cc_common.cpp's ccError given external linkage under DJGPP; same flag, same test). GetGUIAt: not changed
  until its count is in (section 2).
- Cell: build/vmlab/cell.sh mmdcs on AGSVM6 (instrumented, vm-slice3 + lever 3), DOSAGS_VM=fast (all six superops).
- Count: ~175 engine calls a tick on MMD-CS (170 fused farcalls + the unfused rest); saving ~4 x86 instructions each (call, the
  callee's load/ret, the result test) = ~0.7k instructions/tick.
- **Predicted: script event 4.268-4.305 ms/tick (slice 3: 4.308; change -0.003 to -0.040).** Legacy arm unchanged 9.20-9.35.
- Note: F1a's 486 profile put cc_has_error at 0.70% of the script event (~0.14 ms/tick, ~0.8 us a call): the 486 cost of
  the call is far above its instruction count; fixed cycles cannot show that, so this band is small by construction and the
  486 is where lever 3 is judged.

## 1. Lever 3 (cc_has_error inline after engine calls) -- DONE, all gates pass
- Patch (in vm-slice3b.diff): cc_common.cpp's ccError gets external linkage under DJGPP; the fast loop's two post-call tests
  (h_callext, h_s_farcall) read ccError.HasError inline. DosVmStep (the legacy text) keeps cc_has_error().
- Gates (witness AGSVM6W, fixed 40000): line/call digest + state digests + instruction count EQUAL legacy vs fast (all six
  superops) on MMD-CS, AGS Quest (incl. its save/restore), 5 Days room 3 seeded, MMD intro; per-instruction digest EQUAL
  legacy vs fast unfused on all four; the trace control DIFFERS on all four. aq-journeys via ratchet.sh: 10/10 PASS decode off
  and 10/10 fast (boot 7572 / room 11746 / save 882 / load 10159).
- Timing (scored against section 0): fast 4.294 ms/tick (band 4.268-4.305: met; -0.014 vs slice 3's 4.308); legacy 9.256.
- GetGUIAt: NOT changed. Count: 14 calls/tick on MMD-CS (13,987 per 1000 ticks), each a reverse walk over the GUIs with an
  out-of-line IsInteractableAt per displayed GUI. An exact cut would be to inline IsInteractableAt's tests in the loop;
  F1a puts GetGUIAt at ~0.18 ms/tick on the 486 -> central -0.05 at best. Not worth its own round; can ride with lever 2.

## 2. Counts per tick on MMD character select (probe AGSVM6C = AGSVM6 + -DDOSAGS_LEVERCOUNT, ticks 250-1000, fast and legacy identical)
| what | per tick | note |
|---|---|---|
| debug_script_print (debug_script_log/_warn/_print) | **0** (62 in the whole run, all before tick 250) | Debug::Printf 0.01/tick |
| String::FromFormatV/FormatV (two vsnprintf passes each) | 2.0 | |
| ScriptSprintf (StrFormat / String.Format) | 2.0 | script-visible output |
| GetCharIDAtRoom | **6.0** | **5.0 of them repeat an (x, y, hit) already asked in the same tick** |
| ... characters reaching the sprite test per call | 1.0 | the cost is the scan of the character array, not the sprite test |
| update_character_scale | 2.0 | inputs and outputs identical to the previous call 100% of the time |
| UpdateCharacterMoveAndAnim (and Fixup / Moving / Animating / Follower / Idle each) | **102** | every 'on' character in the game, every tick; 1 of them is in room 50 |
| GetGUIAt | 14 | |

## 3. Decisions the counts support
- **Lever 4: drop.** Under the KPI fixture there is no per-tick debug formatting on MMD-CS to skip: debug_script_print runs 0
  times a tick. The _doprnt time is StrFormat / String formatting (2 + 2 a tick), which scripts see. Nothing exact to remove.
- **Lever 1, re-scoped: not update_character_scale** (2 calls a tick; its ~0.32 ms in F1a cannot be 2 calls and is likely
  misattribution) **but the 102-character per-tick update**: UpdateCharacterMoveAndAnim and its five callees run for all 102
  'on' characters, 101 of them in other rooms. That matches F1a's ~1.24 ms/tick of character work (~12 us a character).
  An exact early-out per character needs a per-function no-op proof: Moving and Idle already return for other rooms,
  Fixup is idempotent while (view, loop, frame) are unchanged, but Animating runs off-room and Follower can call Random()
  (an RNG draw is state). Design: skip only characters that are not turning, not moving, not animating, not idling,
  not following, and whose (view, loop, frame) were validated unchanged -- replicating `process_idle_this_time = 0`.
  Central -0.4 to -0.6 ms/tick on the 486; medium risk; same digests + a per-character state digest as gates.
- **Lever 2: worth doing, but not trivially exact.** 5 of 6 calls a tick are same-key repeats; a per-tick memo would save
  ~5/6 of ~0.58 ms = central -0.35 to -0.45 ms/tick. Exactness needs an invalidation rule: the scripts call other APIs
  between the hit tests. Design: memo keyed (x, y, hit_options) + a generation counter bumped by every engine call that is
  not on a pure-read whitelist (GetLocationName/Type, GetInvAt, GetGUIAt, GetGUIObjectAt, GetGlobalInt, Str* reads, ...)
  and by every tick; cached char_lowest_yp restored with the result. Medium risk (the whitelist is the proof).
- Together, levers 1 + 2 central ~ -0.8 to -1.0 ms/tick: past the ~0.7 that 99% needs, at medium risk each.

## 4. Files
- Patch: ~/git/dosags-lab-vm/vm-slice3b.diff = vm-slice3 + lever 3 + the probe (compiled only with -DDOSAGS_LEVERCOUNT;
  inert otherwise). Binaries: build/vmlab/exe/AGSVM6.EXE (instrumented), AGSVM6W.EXE (witness), AGSVM6C.EXE (count probe).
- Raw: build/vmlab/results/{T6L,T6F,W6L,W6N,W6F,W6C}-*, LC-MMDCS / LCL-MMDCS (counts), build/vmlab/ratchet6/.

## 5. PRE-REGISTRATION -- levers 1 + 2, fixed-40000 bands (written 2026-11-06T06:53:04Z, BEFORE their timing runs)
- Binary AGSVM7 (instrumented, vm-slice3b + levers 1 + 2 behind DOSAGS_ENGLEV); cell.sh mmdcs; both arms DOSAGS_VM=fast;
  arm A DOSAGS_ENGLEV unset (off), arm B DOSAGS_ENGLEV=1. Same binary.
- Reference (AGSVM6, fast): script event 4.294 ms/tick; tickstats game_objects_update 0.551 ms/tick.
- Lever 1: 102 'on' characters a tick, 101 in other rooms; at fixed cycles the whole game_objects_update is 0.551 ms
  (~216 instructions a character incl. objects), the skip leaves ~20 of a character's ~180.
  **Predicted game_objects_update: A 0.53-0.57, B 0.10-0.30 ms/tick.**
- Lever 2: 5 of 6 GetCharIDAtRoom calls a tick answered from the memo; each scan ~400-1200 instructions; the whitelist
  test costs ~4 instructions per engine call (175 a tick). **Predicted script event: A 4.28-4.31, B 4.14-4.27 ms/tick.**
- Falsifier: B outside either band, or B slower than A on either figure.

## 6. Levers 1 + 2, first builds: scored against section 5 (results, before any redesign)
- v1 (AGSVM7, memo hooks inline with locals): the fast loop lost its register allocation (dispatch off %edi).
  Script event A 4.618, B 4.627 (legacy 9.249). A outside its band 4.28-4.31: the build was wrong, not the lever.
- v2 (AGSVM7 rebuilt, hooks out of line, -S: 46 `jmp *(%edi)` again): A 4.270, B 4.557 ms/tick.
  **Lever 2 FALSIFIED: B outside 4.14-4.27 and slower than A by +0.287.** (A itself 0.01 under its band.)
  game_objects_update A 0.569 (band 0.53-0.57 met), **B 0.145 (band 0.10-0.30 met): lever 1 MET.**
- Gates on v2 (AGSVM7W; W7L legacy, W7F fast+ENGLEV, W7S +shadow, W7N FUSE=0+ENGLEV, W7C control):
  lever 1 shadow 0 mismatches on all four (mmdcs 100899 checks, aq 2719, 5d3 15992, intro 631475; rnd 0/0/2/0 the
  same with and without the skip); state and sync digests EQUAL to legacy on all four (the el=/cm= lab counters
  excluded); controls DIFF. But lever 2 had **0 memo hits** (mmdcs 3996 lookups, intro 14500): the gain was zero
  and the cost was the hooks.
- Why 0 hits (lab miss histogram, AGSVM7D): every miss was invalidated by a generic VM step -- SCMD_MEMREAD (7)
  through the stepper (an object/array field read), then WRITELIT (4) and MEMWRITEB (26) into script memory, then
  StrCat and StrCopy (not on the list). The remaining misses are first lookups of a VM run (one a run).
- The 5-of-6 repeat count of section 2 counted engine-side calls too; inside the VM there are 4 a tick on MMD
  character select, 3 of them repeats (the most any memo inside one VM run can answer).

## 7. Lever 2 v3 (lazy hooks, minimal whitelist): what changed
- Hooks: an engine call from the fast loop stores its function in dos_vm_curcall and clears it on return; it
  checks the whitelist ONLY while the memo holds a live entry (dos_cmemo_live), else it costs a load and a branch.
  A hit test uses the memo only when the innermost engine call from the VM is whitelisted. Invalidation (bump, live=0)
  on: a call off the list; a generic step other than a memory read or a write into script memory (stack, global
  variable, global data block); the line hook; the pending-events check; every VM entry and exit; a legacy Run.
- Whitelist cut from 22 to 10, the calls measured between a memo store and a hit on MMD char select and intro:
  GetLocationType, GetLocationName, StrGetCharAt, StrLen, StrSetCharAt, StrCat, StrCopy, GetPlayerCharacter,
  GetCursorMode, GetInvAt (each audited: script buffers, GUI/inventory reads, plain reads; GetLocationName also
  writes its buffer and play.get_loc_name_last_time, not read by the hit test).
- Lab, before the final two names (AGSVM8W, 8-name list): 2997 lookups, 1998 hits, 1998 shadow checks, 0 mismatches.

## 8. PRE-REGISTRATION -- lever 2 v3, fixed-40000 bands (written 2026-11-06T08:04:25Z, BEFORE its timing run)
- Binary AGSVM8 (instrumented, levers 1 + 2 v3 + 3); cell.sh mmdcs; arm A DOSAGS_VM=fast, ENGLEV unset; arm B
  DOSAGS_VM=fast DOSAGS_ENGLEV=1; legacy arm L for reference. Same binary.
- A: the off path now stores dos_vm_curcall and tests dos_cmemo_live per engine call (~2 instructions, 175 a tick).
  **Predicted script event A 4.25-4.30 ms/tick** (v2 A 4.270).
- B: hooks ~free while the memo is not live; 3 scans a tick answered from the memo at ~400-1500 instructions each,
  less ~100 instructions of checks while live. **Predicted B - A: -0.15 to -0.02 ms/tick; B 4.11-4.28.**
- Lever 1 unchanged: **game_objects_update A 0.53-0.57, B 0.10-0.30 ms/tick.**
- Falsifier: B - A outside -0.15..-0.02 (in particular B slower than A), or either game_objects_update outside its band.

## 9. Lever 2 v3 (AGSVM8): scored against section 8, then one fix
- Timing (fixed 40k, mmdcs, AGSVM8): legacy 9.259; **A 4.363 (band 4.25-4.30: MISSED, +0.093 over v2's A)**;
  **B 4.273, B - A -0.090 (band -0.15..-0.02: MET; B band 4.11-4.28: MET)**; game_objects_update A 0.569 / B 0.145 (MET).
- Repeatability: the same binary is deterministic (T8A2 = T8A to 4 digits). Re-run with env pads of 1/22/333 bytes
  (shifts the PIT phase): tickstats_script_vm is stable to 1 ms in every arm (T7A 4.3614-4.3621 s, T8A 4.4551-4.4560,
  T8B 4.3666-4.3670); the "evtype script" figure took one +54.9 ms uclock step in 2 of 15 runs (T8AP333, T8BP22) -- a
  fixed-cycle bracket can gain one BIOS tick (PLAN-LOG's uclock hole). Same-binary deltas read from script_vm are clean.
- Cause of A's miss (from -S): GCC stopped inlining DosVmStep into the fast loop once the memo test sat inline in it,
  so every generic step paid an extra call frame (v2's loop called DosVmStepBody directly). Not a lever cost.
- Fix (v3b, AGSVM9): the stepper's memo test moves to an out-of-line dos_memo_step(); -S: DosVmStep inlined again,
  46 `jmp *(%edi)`, the loop calls DosVmStepBody once and dos_memo_step once. Behaviour identical.

## 10. PRE-REGISTRATION -- v3b (AGSVM9), fixed-40000 (written 2026-11-06T09:50:08Z, BEFORE its timing run)
- Same cells as section 8 on AGSVM9 (instrumented). Read script event AND tickstats_script_vm (glitch-robust, section 9).
- **A 4.25-4.30 ms/tick (v2's A 4.270); B - A -0.15..-0.02 (v3 measured -0.090); game_objects_update A 0.53-0.57,
  B 0.10-0.30.** Falsifier as section 8.

## 11. v3b (AGSVM9) timing, scored against section 10
- legacy 9.259; **A 4.332 (band 4.25-4.30: MISSED again, +0.062 over v2's A; script_vm 4.4235 s vs v2 4.3616)**;
  **B 4.256, B - A -0.076 (MET)**; pads reproduce to 1 ms; game_objects_update A 0.569 / B 0.145 (MET).
- The stepper fix bought 0.032 of the 0.094. What is left is the hooks' own off path: v3 stores dos_vm_curcall on every
  engine call (and works out which function it is) whether or not the levers are on; v2 skipped both behind dos_englev_on.
- Experiment X10 (timing only, not a candidate unless it passes every gate): the same hooks behind if (dos_englev_on).
  **Pre-registered (written 2026-11-06T09:56:50Z, before it runs): A 4.26-4.29; B - A -0.12..-0.03.**
- X10 scored: **A 4.325 (band 4.26-4.29: MISSED), B - A -0.050 (MET)**. Guarding the hooks behind dos_englev_on
  buys 0.006: the hooks are not where the remaining off-arm cost is. Not isolated further (regalloc-level in a
  2.3k-line loop; worth <= 0.02 ms on the 486 at r 0.34). X10 dropped; v3b kept.
- Reference caveat: AGSVM6 (no levers) fast reads 4.294 by script event but its script_vm (4.4412 s) carries a +55 ms
  step (its vm-minus-event gap is 147 ms vs 92 in every other arm). By script_vm the no-lever baseline is ~4.386 s,
  so v3b's off arm costs ~+0.037 ms/tick over no lever code; v2's off arm read 0.025 under it.

## 12. v3b gates (AGSVM9W) -- ALL PASS
| fixture | lever 1 shadow (checks / bad) | lever 2 (lookups / hits / shadow checks / bad) | RNG draws L / F | state+sync digests vs legacy (F, S, N) |
|---|---|---|---|---|
| MMD char select | 100899 / 0 | 3996 / 2997 / 2997 / 0 | 0 / 0 | EQUAL (N: full trace EQUAL too) |
| AGS Quest (with restore) | 2719 / 0 | 0 / 0 / 0 / 0 | 0 / 0 | EQUAL |
| 5 Days room 3 seeded | 15992 / 0 | 0 / 0 / 0 / 0 | 2 / 2 | EQUAL |
| MMD intro seeded | 631475 / 0 | 14500 / 10875 / 10875 / 0 | 0 / 0 | EQUAL |
- Fused arms' full trace is DIFF@0 by construction (as slice 3's W6F); the sync digest is their gate. Controls: v3's
  W8C arms DIFF on all four (v3b changes only where the stepper's test is compiled). Legacy W9L = W8L = W7L.
- aq-journeys ratchet subset on AGSVM9: off 10 pass, fast + ENGLEV=1 10 pass (build/vmlab/ratchet9/).
- Rig binaries (build/vmlab/rig9/, default legacy VM and levers off; lab builds, build_dirty=1):
| file | flavour | sha256 | binary_sha12 | bytes |
|---|---|---|---|---|
| VM9REL.EXE | release | 1dee66de150106cb59c0ebb16ccc83605bbede84241b197933fe416630c34138 | 23fd25201ec9 | 8,643,269 |
| VM9INS.EXE | instrumented | df5ee7acf14fa7ac8d5750cf3ab55ef13849d894c1ae7226cdbc2f4a58036028 | c313551f4112 | 8,680,899 |
- DOSBox-X sanity: VM9REL legacy / fast+ENGLEV=0 / fast+ENGLEV=1 / legacy+ENGLEV=1 on MMD-CS and legacy vs fast+ENGLEV=1
  on 5 Days room 3: kept Game lines EQUAL; VM9INS legacy vs fast+ENGLEV=1 EQUAL; stamps and build_dirty in RUNMANIFEST.
- Patch: ~/git/dosags-lab-vm/vm-slice3c.diff (slice 3 + levers 1, 2, 3 + lab probes; ASCII). Drafts: PREREG5-486-DRAFT.md.
