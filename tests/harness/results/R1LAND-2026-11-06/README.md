# R1LAND-2026-11-06 -- landing records for ags 0366 (lever R1, default on) and 0367

DOSBox-X only (cycles=fixed 40000, tests/harness/confs/dosbox-x-fixed40k-opl3.conf). Text records only: the frame
digests (FHASH.TXT), RUNMANI.LOGs, the game-output lines each comparison read (GAMELINES.TXT), parse-results JSON,
the cell command lines (CELL.txt, stage dir masked) and the lab overlay. Analysis: ~/git/dosags-lab-play/LAB-PLAY.md
sections 7-10; hazard source for the full-restore guard: ~/git/dosags-lab-r3/LAB-R3.md (lab-r3.diff).

## Binaries (worktree ~/git/dosags-r1land, branch r1land off main 579c0b5c; patches/ags 0366 sha256 31e9e229...,
0367 sha256 bd9a69ab...)
| exe | what | sha256 | binary_sha12 | build_dirty | bytes |
|---|---|---|---|---|---|
| LAND2INS | 0001-0367, instrumented | 5650fff91d7e1be85677a7c17db078820f2412bda2ff00d1f70fc022fb9a893d | 39c6e4b65079 | 0 | 8,686,461 |
| LAND2REL | 0001-0367, release | 7770f865f33b6ce977fa56c09e03596e438af53ffb83d3013d06ee9ab717cf77 | 54d439f88378 | 0 | 8,649,343 |
| O366INS | 0001-0366 only, instrumented | f0b5461568ed6d4a89fb774c6826253f31392fd02dc472c05aa9aa3c30374c1f | b3f3ba3ff679 | 0 | 8,686,549 |
| O366REL | 0001-0366 only, release | e04245c03ecce1c1aba16d7beea4a5e33e712f3bf0b4ddf3f32afe71b4124968 | 2c92d816bb7e | 0 | 8,649,431 |
| GATE2INS | 0001-0367 + gate-overlay.diff (lab only, never landed) | 9a02b679d16fa693cb722fda4ef0e1ed4fae245560351fa34022a17ce8b0766d | -- | 1 | -- |
A clean rebuild from the committed tree reproduced LAND2INS / LAND2REL byte for byte.

## Overlay (gate-overlay.diff, applied by apply-overlay.py, reverted after the build)
DOSAGS_LAB_FRAMEHASH=1 (FHASH.TXT: loop counter, hash of the composited virtual screen after every composite);
DOSAGS_LABCLICKS (fixture G's clicks and hovers); DOSAGS_LAB_GUISKIP_BREAK=1 (control: mode 2 skips every flagged
entry); DOSAGS_LAB_FORCE_WHOLE=N (after every Nth room restore the next room-rect mark takes invalidate_rect_on_surf's
overflow exit, NumDirtyRegions = WHOLESCREENDIRTY with the mark dropped -- the path a 26th rect takes);
DOSAGS_LAB_NOGUARD=1 (control: dos_guiclip_note_fullrestore counts but does not arm the latch). guiclip_final gains
lab_forced= and lab_noguard=.

## Fixtures
- G: MMD, save 007 restored in room 1, seeded, lab clicks + hovers, room 1 -> 2 at lc 6882, exit 8600 (3164 ticks).
- intro: MMD --startr 40, seeded, exit 1300 (1299 ticks).
- Gate cells run without --fixed-timestep (every tick rendered) and with DOSAGS_PRESENT_VERIFY=1.
Compare: `python3 fhcmp.py <ref> <arm>...` (by loop counter); `python3 eqcmp.py <a> <b>` on GAMELINES.

## Results
(see the hand-back table; summarised here)
| gate | fixture G | intro |
|---|---|---|
| default (LG2-D) vs =0 (LG2-0) | EQUAL 3164/3164 | EQUAL 1299/1299 |
| control BREAK (LG2-C) vs =0 | DIFF 2443/3164 | DIFF 781/1299 |
| forced whole restore every 7th: default (FG-D) vs =0 (FG-0) | EQUAL 3164/3164 | EQUAL 1299/1299 |
| forced, guard disabled (FG-N) vs =0 | DIFF 3002/3164 (stale_px 20.6M) | DIFF 1076/1299 (stale_px 8.7M) |
| guard fires (latch_fullrestore) natural / forced | 0 / 439 of 456 forced | 0 / 155 of 188 forced |

| equivalence (P9 shape: save 007, DOSAGS_TICKCLICKS=5500,60,30, seeded, exit 7436), game lines | result |
|---|---|
| LAND2REL default vs lab R1REL GUI_CLIP=2 (via the unguarded landed exe, same counts) | EQUAL (78) |
| LAND2REL =0 vs shipped release c754df64babd | EQUAL (78) |
| LAND2INS default / =0 vs the unguarded landed instrumented exe | EQUAL / EQUAL (78) |
| witness, default arm | `DOS-PORT guiclip DOSAGS_GUI_CLIP=(default) mode=2`; guiclip_final skipped=2047 clipped=3905 full=46 latched_full=6 latch_fullrestore=0 |

| regression, LAND2REL default vs =0 | exit | game lines | default arm guiclip_final | other |
|---|---|---|---|---|
| 5 Days room 3, S16 presentation (512x384 round) | 0 / 0 | EQUAL (30) | flagged 765, all full (same-space test fails) | -- |
| Trilby room 35, 512x384, DOSAGS_MSGSKIP=1 | 0 / 0 | EQUAL (1121) | flagged 835, all full | -- |
| AGS Quest AutoPilot | 0 / 0 | EQUAL (356) | skipped 6358, clipped 2131, full 11 | parse-results PASS both; PH01-03 match; 0 stale |

| ratchet (tests/ratchet.yaml, instrumented 39c6e4b65079, `ratchet.sh --root <r1land> --no-build --no-host-wait --capture-display 273 --no-record`) | |
|---|---|
| run 20261107T023741Z | 39 pass (10 improved), 2 fail (exe-bytes 8686461 > 8683881, code-lock-bytes 5216176 > 5214848), 4 quarantined PASS |
| 0367's own delta (0366+0367 vs 0366 alone) | exe -88 (both flavours), code-lock -96 (CL-O366INS 5216272 vs CL-LAND2INS 5216176) |
| proposed limits (exact) | exe-bytes 8686461, code-lock-bytes 5216176 (tests/ratchet.yaml on r1land) |
An earlier run (20261107T021743Z) ERRORed on 38 checks because the host disk was full (661 MB free; facts files not
written); it is void and not recorded here. The first run on the unguarded build (20261106T234402Z) was stopped by me
when the guard addendum arrived (INTERRUPTED rows); its completed rows all passed.
