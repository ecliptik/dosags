# LANDING -- script VM + engine levers as patches/ags 0359-0365 (lab worktree, not committed)

Base: main a8d6164c, vendor/ags 94e271df + main's series 0001-0355 (tree 8afe6c67 = main's 579245b5b).
Slots 0356-0358 are left free for the GUS patches; this series touches none of their files
(GUS: openalsource.cpp, dos_audio_mixer.cpp/.h). Built from the lab snapshots that were each gated
(vm-slice1, -2b, -3, -3b, -3c in build/landing/snap/), renumbered 0355 -> 0359..0364 in comments,
with the one-off lab probes taken out (below). Every commit compiles on its own (instrumented flavour).

## The series (patches/ags/)

| slot | patch | bytes | diffstat |
|---|---|---|---|
| 0359 | script VM slice 1: decode every script once at load (inert unless DOSAGS_VM asks) | 23,636 | 5 files, +427 |
| 0360 | script VM slice 2: a threaded fast loop over the decoded stream (DOSAGS_VM=fast) | 96,433 | 4 files, +2120 -117 |
| 0361 | script VM slice 3: six superinstructions and two divisions off the hot path | 33,203 | 4 files, +480 -9 |
| 0362 | lever 3: the fast loop tests ccError.HasError inline after an engine call | 3,130 | 2 files, +7 -2 |
| 0363 | lever 1: skip the per-tick update of a character that provably cannot change | 11,286 | 5 files, +124 -2 |
| 0364 | lever 2: memoise GetCharIDAtRoom inside a whitelisted engine call | 20,725 | 5 files, +183 -11 |
| 0365 | the fast script VM and engine levers 1 + 2 by default; env keeps the fallbacks | 7,226 | 4 files, +17 -13 |

Lever 3 sits before levers 1 and 2 because that is the order it was built and gated in (it was gated alone).
0365 is separate so the default can be reverted without touching the code: DOSAGS_VM=legacy and DOSAGS_ENGLEV=0
are the runtime fallbacks; "vmmode"/"englev" witness lines are printed on every run ("(default)" when unset);
DOSAGS_ENGLEV and DOSAGS_VM_FUSE join the RUNMANIFEST env allowlist.

## Lab-only code: what stays, what left

- STAYS in the series, compiled only with -DDOSAGS_VMTRACE (make AGS_RUNSTATS_DEF=-DDOSAGS_VMTRACE): the
  per-instruction trace digest, the statewit witness, the line/call digest, the superinstruction shadow
  (DOSAGS_VM_SHADOW=1) and the lever shadows (DOSAGS_ENGLEV_SHADOW=1). They are the gates' instruments and are
  woven through the handlers; moving them to a side patch would make that patch rewrite the loop. Neither
  flavour defines DOSAGS_VMTRACE. CORRECTION (sdlports review 2026-11-06, confirmed on main's builds): both exes still
  carry dos_englev_shadow() and its "DOSAGS_ENGLEV_SHADOW" string -- 0363 gates the call sites under DOSAGS_VMTRACE but
  defines the function unconditionally (dead code: never called, no behaviour or cost). "DOSAGS_VM_CHECK" is also present
  by design (an opt-in, default-off decode check). No statewit, VM-shadow or trace strings remain. Queued: move the
  definition under #ifdef DOSAGS_VMTRACE in the next patch that changes the binary anyway (not now: N7 measures this exe).
- LEFT the series (one-off investigations, kept as lab-only patches outside it, both apply on top of 0365):
  build/landing/lab/lab-levercount.patch (the DOSAGS_LEVERCOUNT calls-per-tick probe, 9 files) and
  build/landing/lab/lab-cmemo-diag.patch (lever 2's miss histogram, DOSAGS_VMTRACE).

## Gates (DOSBox-X, fixed 40000, --fixed-timestep, headless; display 263/264)

Builds from `make patches` (fingerprint 3ecc4317438f, verify-patches-applied OK), vendor trees clean, build_dirty=0:

| flavour | file | bytes | stamp | sha256 |
|---|---|---|---|---|
| instrumented | build/ags/ags.exe (= build/landing/bin/LINS.EXE) | 8,683,881 | f3a8774e03c8 | c1dff74b7a45... |
| release | build/ags-release/ags.exe (= LREL.EXE) | 8,646,251 | c754df64babd | d680e3b6fcfc... |
| lab witness (-DDOSAGS_VMTRACE) | build/ags-w/ags.exe (= LWIT.EXE) | 8,714,794 | f3a8774e03c8 (*) | 934eec143cfa... |

(*) The stamp does not fold AGS_RUNSTATS_DEF, so the lab build carries the instrumented stamp (pre-existing).

Digests, LWIT.EXE. Reference L = DOSAGS_VM=legacy DOSAGS_ENGLEV=0 (upstream Run, levers off); D = no env (the new
defaults); N = DOSAGS_VM_FUSE=0; E = D + DOSAGS_ENGLEV_SHADOW=1; S = D + both shadows; C = L + the trace control.

| fixture | D vs L (sync + state) | N vs L (full trace) | VM shadow (S) | lever 1 shadow (E) | lever 2 hits / shadow checks / bad (E) | C |
|---|---|---|---|---|---|---|
| MMD character select | EQUAL | EQUAL | 989,435 / 0 | 100,899 / 0 | 2997 / 2997 / 0 | DIFF@12 |
| AGS Quest (with restore) | EQUAL | EQUAL | 4,594 / 0 | 2,719 / 0 | 0 / 0 / 0 | DIFF@20 |
| 5 Days room 3, seeded | EQUAL | EQUAL | 4,462 / 0 | 15,992 / 0 (RNG 2 = 2) | 0 / 0 / 0 | DIFF@14 |
| MMD intro, seeded | EQUAL | EQUAL | 3,663,429 / 0 | 631,475 / 0 | 10,875 / 10,875 / 0 | DIFF@42 |

- The series' legacy arm equals the lab's legacy arm (W9L) line for line; D's full trace is DIFF@0 by construction
  (fused), its sync digest is the gate. Kept Game lines EQUAL in every arm except the control.
- S on AGS Quest: state digests equal at every line, but its line/call digest drifts from line 137 (the audio
  phase ends 2 ticks later, 3571 vs 3569): both shadows together cost enough emulated time per tick to move an
  audio-timed wait. The shadows' counts (0 mismatches) are S's gate, as in slice 3. With both shadows on, lever 2
  makes no hits (the VM shadow replays through the stepper, which invalidates) -- hence arm E.

## Full ratchet (tests/ratchet.yaml, unchanged; instrumented build/ags/ags.exe f3a8774e03c8; report 20261106T123141Z)

`ratchet.sh --root <worktree> --no-build --no-host-wait --capture-display 264 --no-record` (no --controls), ~75 min of units:
**39 pass (10 improved), 2 fail, 0 blocked, 4 quarantined; the only failures are the two size checks.**
(build/landing/ratchet-full/ratchet-report.txt; the quarantined shards-alias-512x384 full-speed row failed as before.)

Proposed limits (exact, no headroom, the instrumented flavour the nightly builds):

| check | limit now | measured | proposed | delta |
|---|---|---|---|---|
| exe-bytes | 8638525 | 8683881 | **8683881** | +45,356 (0359-0365's code; release flavour 8,646,251 B, +44,844 vs 0355's release 8,601,407) |
| code-lock-bytes | 5177312 | 5214848 | **5214848** | +37,536 (the VM file lands inside the locked text range) |

Improved, left as they are (lower them with --propose-lower if wanted): journey p95 boot 7582 / room 11741 / save 893 /
load 10162 (limits 7901 / 12295 / 913 / 10929); pcm-accounting 0 (le 1); pcm-mixed 148 (ge 50); midi-stall-fired 19
(ge 10); sb-alive-clk 987 / 997 / 997 (ge 900).

## Smoke (DOSBox-X)

- AGS Quest AutoPilot, run-dosbox.sh defaults + parse-results.py, both flavours, no env (fast VM + levers):
  **PASS -- all phases ok**, PH01-PH03 screenshot hashes match expected/agsquest/dosbox-x.json; exit_code 0;
  build_dirty=0; vmmode "(default) mode=3", englev "(default) on=1" (build/landing/smoke/).
- MMD character select and 5 Days room 3 (fixed 40k), both flavours: defaults vs DOSAGS_VM=legacy DOSAGS_ENGLEV=0 kept
  Game lines EQUAL; build_dirty=0. MMD CS release tick_rate_steady 40.20 (defaults) vs 40.07 (fallback).

## ASCII
All seven patches, both lab-only patches, LANDING.md: 0 non-ASCII bytes; no added line with trailing whitespace.

## Not done here
No commit, no push, nothing in ~/git/dosags. The x2 486 re-run on the clean main release build is the next round.

## Landed on main (2026-11-06)
The seven patches were copied byte-for-byte into ~/git/dosags/patches/ags; `make patches` gave vendor tree 7dc1074a
(= the lab branch lab-vm-landing's tree) and fingerprint 3ecc4317438f. Main's release build is byte-identical to
LREL.EXE (d680e3b6...). Main's instrumented build is 50c027e7... (same stamp f3a8774e03c8, same size, same symbols;
a clean rebuild reproduces it -- the lab's LINS.EXE differs only in the link order of the libgcc/libsupc++ members);
AGS Quest AutoPilot PASS on it, defaults printed (mode=3, on=1). Ratchet size checks on main: 8683881 / 5214848,
limits raised to those (tests/ratchet.yaml). The two lab-only patches are kept in docs/lab/vm-lab-patches/ (not applied).
