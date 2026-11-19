# R3LAND-2026-11-06 -- landing records for ags 0368 (lever R3, DOSAGS_GUI_CLIP default 4)

DOSBox-X only (cycles=fixed 40000, tests/harness/confs/dosbox-x-fixed40k-opl3.conf). Text records only: the frame
digests (FHASH.TXT), RUNMANI.LOGs, the game-output lines each equivalence read (GAMELINES.TXT), parse-results JSON,
the timing checkpoints (LABCK.TXT), the cell command lines (CELL.txt, stage dir masked), the lab overlays and the
compare tools. No images (AGS Quest's PH*.BMP stay out). Design and lab numbers: docs/lab/LAB-R3.md.

## Binaries (worktree ~/git/dosags-r3land, branch r3land off main 41d82c06; patches/ags/0368)
| exe | what | sha256 | binary_sha12 | build_dirty | bytes |
|---|---|---|---|---|---|
| R3INS | 0001-0368, instrumented | 1cb00ce1307d1f7bccbf3d65c3d9cbe61fb9228c847a4f0ece6e398bb2c2c91e | aa334361a087 | 0 | 8,688,503 |
| R3REL | 0001-0368, release | 7deb7ca9778676e53f920cf654813697b6ce7f8081ab3f5e5656ca5b12df8898 | 4c9f83b62c5c | 0 | 8,651,385 |
| MAINREL | main's release (= R1LAND's LAND2REL), P9 reference | 7770f865f33b6ce977fa56c09e03596e438af53ffb83d3013d06ee9ab717cf77 | 54d439f88378 | 0 | 8,649,343 |
| R3GATE | 0001-0368 + gate-overlay-v1.diff, instrumented (lab only) | 4cb1587e329c3da16e391fad249ed190b900b602b54b8e95db80d04c54e8e128 | 1f78995c6f35 | 1 | -- |
| R3GATE2 | 0001-0368 + gate-overlay.diff (v2), instrumented (lab only) | 04ae09690b74e9277c065b6dc57be009ccf18fc4772b7b13b6de6817a572e80f | 1e534e9d81bc | 1 | -- |
A full clean rebuild (build/ags and build/ags-release removed) from the committed tree reproduced R3INS and R3REL
byte for byte. Against main's 39c6e4b65079 / 54d439f88378: +2,042 bytes in each flavour.

## Overlays (applied by apply-overlay*.py to vendor/ags, built, reverted; never landed)
- v1 (gate-overlay-v1.diff, apply-overlay-v1.py; R3GATE): DOSAGS_LAB_FRAMEHASH=1, DOSAGS_LABCLICKS, DOSAGS_LAB_CKPT
  (rb_sprite_time / render_to_screen_pertick totals at listed loop counters), DOSAGS_LAB_GUISKIP_BREAK=2 (control: R3's
  per-box list without the carry boxes), guard (b): DOSAGS_LAB_FORCE_WHOLE=N + DOSAGS_LAB_NOGUARD=1 (R1LAND's, unchanged),
  guard (a): DOSAGS_LAB_SPANMAX=N (spans per row before AGS stretches one; AGS's is 4), DOSAGS_LAB_SPANPROBE=K[:Y] (every
  Kth room restore two 2x2 marks at the two ends of rows Y..Y+1), DOSAGS_LAB_NOCOARSE=1 (control: the stretch is
  counted, not recorded). guiclip_final gains lab_forced= lab_noguard= lab_probes= lab_nocoarse= lab_spanmax=.
- v1's probe was VOID: it marked before update_room_invreg_and_reset's RoomCamRects Reset(), which wiped the marks
  from AGS's rects (only dos_port_dirty kept them), so no probe ever reached a span. Cells AV-*, AG-*, AV2-N ran it
  (controls EQUAL: AV-N, AG-N, AV2-N). They are kept for the record and are not scored.
- v2 (gate-overlay.diff, apply-overlay.py; R3GATE2): v1 with the probe moved after the Reset (post-restore marks, as a
  sprite's). Only the guard (a) cells AV3-* / AG3-* ran on it.

## Fixtures (MMD = Maniac Mansion Deluxe; seeded DOSAGS_RANDSEED=1)
- G: save 007 restored in room 1, lab clicks + hovers, room 1 -> 2, exit 8600 (3164 loop counters).
- V: LAB-R3's verb-bar fixture: G's route, then pointer still / moving on the verb bar in room 2, exit 9400 (3964).
- intro: --startr 40, exit 1300 (1299). AQ: AGS Quest AutoPilot (3558).
- Gate cells: no --fixed-timestep (every tick rendered: "fixed-timestep: DISABLED" in each), no fine timing, no
  TICKLOG, DOSAGS_LAB_FRAMEHASH=1 + DOSAGS_PRESENT_VERIFY=1. Every cell's RUN.BAT SETs are <= 509 bytes, and each cell's
  witness line, labclicks n=14 (G, V) and lab_* fields were checked (cellcheck.py).
Compare, in this directory: `python3 fhcmp.py GG-0.FHASH.TXT GG-D.FHASH.TXT ...` (by loop counter, last record of
each); `python3 eqcmp.py P9-MAIN-D.GAMELINES.TXT P9-REL-D.GAMELINES.TXT`; `python3 cellcheck.py` reads cell dirs
(build/r3/results, not committed).

## Digest gates (R3GATE; arms: D = DOSAGS_GUI_CLIP unset = R3, 0, 2 = R1, B = BREAK control)
| fixture | D vs 0 | 2 vs 0 | B vs 0 | D's guiclip_final (flagged: skipped / boxed (boxes) / full) | PV stale px D / B |
|---|---|---|---|---|---|
| G | EQUAL 3164/3164 | EQUAL 3164/3164 | DIFF 2329/3164 (first lc 5439) | 9558: 6742 / 2475 (2510) / 341 | 0 / 0 |
| V | EQUAL 3964/3964 | EQUAL 3964/3964 | DIFF 3426/3964 (first lc 5439) | 11957: 6305 / 5556 (5605) / 96 | 0 / 0 |
| intro | EQUAL 1299/1299 | -- | DIFF 771/1299 (first lc 62) | 7874: 6441 / 47 (47) / 1386 | 0 / 0 |
| AQ | EQUAL 3558/3558 | -- | DIFF 2078/3558 (first lc 261) | 8637: 7343 / 1281 (2774) / 13 | 0 / 0 |
The counts equal LAB-R3 section 6's AGSR3B rows on every fixture.

## Forced fallbacks
| guard | forcing | fixture | default (R3) + forcing vs =0 + forcing | guard disabled + forcing vs =0 + forcing | fires (default arm) |
|---|---|---|---|---|---|
| (a) span coarsening -> bbox | SPANMAX=1, SPANPROBE=7:166 (R3GATE2) | V | AV3-D EQUAL 3964/3964 | AV3-N DIFF 3877/3964, PV stale 769,122 px | fb_coarse 2967 entries, coarse_restores 2266, span_stretch 203,834, probes 570 |
| (a) | same | G | AG3-D EQUAL 3164/3164 | AG3-N DIFF 3002/3164, PV stale 604,061 px | fb_coarse 3055, coarse_restores 2922, span_stretch 213,426, probes 456 |
| (b) full restore -> full (0366's latch_fullrestore) | FORCE_WHOLE=7 | G | BG-D EQUAL 3164/3164 | BG-N DIFF 3002/3164, PV stale 21,805,206 px | latch_fullrestore 439 of 456 forced, fb_whole 1314 entries |
| (b) | same | intro | BI-D EQUAL 1299/1299 | BI-N DIFF 1076/1299, PV stale 8,651,854 px | latch_fullrestore 155 of 188 forced, fb_whole 929 |
The =0 + forcing arms equal the unforced =0 arms on every tick (AV3-0 = GV-0, AG3-0 = GG-0, BI-0 = GI-0, BG-0 = GG-0),
so the forcing changes what is restored, never what a full composite shows.
Natural fires: none. span_stretch 0 and latch_fullrestore 0 in every unforced cell (G, V, intro, AQ, P9, 5 Days,
Trilby). Both guards are exercised only by the forcing.

## Equivalence and regression (release exe R3REL; game output lines, eqcmp.py)
| cell pair | fixture | result |
|---|---|---|
| P9-REL-D vs P9-MAIN-D (54d439f88378 default) | P9 shape: save 007, DOSAGS_TICKCLICKS=5500,60,30, exit 7436, --fixed-timestep | EQUAL (78) |
| P9-REL-2 / P9-REL-0 vs P9-MAIN-D | same | EQUAL / EQUAL (78) |
| RG-5D3S-D vs -0 | 5 Days room 3, 512x384 round, exit 3000 | exit 0/0, EQUAL (30); flagged 765, all full (same-space test fails) |
| RG-TN35-D vs -0 | Trilby room 35, DOSAGS_MSGSKIP=1, exit 3000 | exit 0/0, EQUAL (1121); flagged 835, all full |
| RG-AQ-D vs -0 | AGS Quest AutoPilot | exit 0/0, EQUAL (356); parse-results PASS both; D: skipped 7251, boxed 1254 (2742 boxes), full 12 |
P9-REL-D: flagged 5998, skipped 2047, boxed 3905 (3985 boxes), full 46, latched_full 6 -- the entries main's R1
clipped (3905) are the ones R3 draws per box. Witness `DOS-PORT guiclip DOSAGS_GUI_CLIP=(default) mode=4`; every
release cell "fixed-timestep: ENABLED".

## Timing (information only; R3GATE, fixture V, --fixed-timestep, fine timing on, no TICKLOG, DOSAGS_LAB_CKPT)
ms per render pass (render_to_screen_pertick calls in the window; 300 passes each, every tick rendered):
| window | rb_sprite R1 (TV-2) | rb_sprite R3 (TV-D) | render_to_screen R1 | R3 | LAB-R3 rb_sprite R1 -> R3 |
|---|---|---|---|---|---|
| E pointer in room 7100-7400 | 0.586 | 0.586 | 1.129 | 1.129 | 0.685 -> 0.726 |
| H1 still on a verb 7500-7800 | 2.641 | 0.762 | 3.184 | 1.304 | 2.743 -> 0.871 |
| H3 still, bar middle 8300-8600 | 2.921 | 0.731 | 3.481 | 1.293 | 3.023 -> 1.024 |
| H4 still, lower portrait 8700-9000 | 4.096 | 0.765 | 4.680 | 1.351 | 4.198 -> 0.875 |
| H5 moving over verbs 9000-9300 | 2.740 | 0.935 | 3.299 | 1.494 | 2.843 -> 1.045 |
Bar windows R1 2.64-4.10 -> R3 0.73-0.94 ms (LAB-R3: 2.74-4.20 -> 0.87-1.05); saving 1.81-3.33 ms per pass. The
pointer-in-room window no longer costs R3 anything over R1 (LAB-R3: +0.04 ms), because 0368 runs R1's empty-bbox
test before the box loop. Absolute levels are ~0.1 ms below LAB-R3's: its exe carried more lab instrumentation.
`python3 ckwin3.py TV-2.LABCK.TXT TV-D.LABCK.TXT` reproduces the table.

## Ratchet (tests/ratchet.yaml, instrumented R3INS aa334361a087 = build/ags/ags.exe,
`ratchet.sh --root <r3land> --no-build --no-host-wait --capture-display 390 --no-record`)
| run | result |
|---|---|
| 20261107T094503Z (RATCHET-20261107T094503Z-*.txt) | 39 pass (10 improved), 2 fail (exe-bytes 8688503 > 8686461, code-lock-bytes 5216640 > 5216176), 4 quarantined (screen-shards-alias-512x384 FAIL(q) 4: its known VOID freeze-tick drift, A=100 B=101 etc.; its fixed-40k row PASS) |
| 0368's delta vs main (0001-0367) | exe +2042 (both flavours), code-lock +464 (5216640 vs R1LAND's 5216176) |
| proposed limits (exact, no headroom; tests/ratchet.yaml on r3land) | exe-bytes 8688503, code-lock-bytes 5216640 |
Note (review, non-blocking): screen-shards-alias-512x384 read FAIL(q) in this run where R1LAND's ratchet read it PASS(q); it is
quarantined for that freeze-tick drift, so the difference is recorded as drift, not as a regression attributed to 0368.

An earlier run (20261107T090226Z) is void and not recorded: the worktree lacked the bench8 / bench16 / shards game
packages (11 screen checks ERROR "no .ags package"); its exe-bytes and code-lock-bytes read the same 8688503 / 5216640.
