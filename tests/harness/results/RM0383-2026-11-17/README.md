# RM0383-2026-11-17 -- landing records for ags 0383 (removes 0382's TEMPORARY switch DOSAGS_ROUTE_FAST and the old search bodies)

DOSBox-X and build host only; nothing here touched the rig. Branch `rm0383` (worktree dosags-ring) on main a98b65ea +
patches/ags/0383. For sdlports' review; not merged. Mandate: the operator's ruling of 2026-11-17 after round RR, "On,
remove old code" (PLAN.md a98b65ea; tests/harness/results/ROUNDRR-2026-11-17).

## 1. The patch
- **The switch is gone:** dos_rf_fast / dos_rf_fast_on() and both tests of it (in __find_route and in can_see_from).
- **The bodies that lost are gone:** the old find_route_dijkstra and its CHECK_MIN. find_route_dijkstra_fast and
  CHECK_MIN_FAST take their names and their place in the file. The surviving function is 0382's fast body byte for byte
  after the rename (sdlports compared them), so the code that stays is the code round RR ran.
- **Against the pre-0382 route finder exactly 8 lines are removed** -- the do_line call site, CHECK_MIN's first test, the
  two lines of the 0xFF fill, the pass-loop header, two `visited[numreplace] = -1;` lines and the vstate line -- and the
  levers are added. An 8-bit mask takes the inline line-of-sight walk; other depths keep do_line and line_callback.
- **The env allowlist entry is gone:** quit.cpp is byte-equal to its pre-0382 text.
- **The exit line:** "DOS-PORT routefast on= stamp_allocs= stamp_peak_bytes=" becomes "DOS-PORT routestamp allocs=
  peak_bytes=". The switch witness goes with the switch; the memory witness stays (sdlports: it is the only witness
  that a search ran in a smoke).
- Unchanged: the stamp grid (W x H bytes, one at a time; allocated at the first search on a mask size, freed and
  re-allocated on a size change, freed in ~LegacyRouteFinder; quit on a failed allocation), the wrap at generation 255.
- Written by lab-rb docs/lab/move-lab/ms99/make-0383.py. Slots: 0374 and 0375 stay reserved; 0383 is the next free.
- Provenance: patches/ags/0383 is `git format-patch` of the vendor commit; after `make patches` the vendor tree is
  3453b66d29bf64c63a9b50b00e092ac1441a7a21, the authored commit's tree. ASCII only; no fopen.
- tests/harness/rr-read.py now says in its header that it reads 0382 binaries only (0383 has no routefast line and
  another stamp, so a later binary's cell reads VOID there by design; the 114EDGE rule expired with round RR).

## 2. Builds (make patches first; round 1 incremental, round 2 with build/ags + build/ags-release wiped)
| flavour | sha256 | stamp | bytes | vs 0382 | vs 0379 / 0381 | r1 == r2 |
|---|---|---|---|---|---|---|
| instrumented | e5c05cc01ab31633d4915725bcc64c04ebccd59ac1313c2f947817055238f08b | 78dd12df1b6f | 8,711,712 | -3,763 | +4,011 | yes |
| release (DOSAGS_RELEASE=1) | c68241073cb0dbcc6f0870c22ba31a0d904dd2261e72a44fbb7ba75f6cfb7f43 | f2e183845d2f (printed by the smoke cells) | 8,673,058 | -3,763 | +3,499 | yes |

`make build-dirty`: 0.

## 3. Identity: the 0382 gate re-run on the result (lab builds P83LI c27afb12 / P83LR b60d157b = the lab's REF overlay +
## the 0382 and 0383 source changes, so the surviving body carries the lab's probes and counters)
Against REF's cells of the same flavour, mode and game (lab-rb RESULT-RSW-1): every call record and chain, the corpus
rooms and block chains, the split masks, and the seven Dijkstra exit / fallback counters. Reader lab-rb p83-read.py,
output P83-OUT.txt. With no switch left there are 12 cells, not 24.

| flavour | grid corpus: ms3 / 5days / Trilby | split pass: ms3 / 5days / Trilby |
|---|---|---|
| instrumented | IDENTICAL x 3 (routestamp allocs 2, peak 192,000 / 0 / 1, 64,000) | IDENTICAL x 3 (2, 192,000 / 1, 64,000 / 1, 64,000) |
| release | IDENTICAL x 3 (as instrumented) | IDENTICAL x 3 (as instrumented) |
0 mismatches, 0 missing, every cell rc 0, no old "routefast" line in any. Coverage is RESULT-RSW-1's: MS3's 114 route
calls, 5,292 corpus requests, 2,892 cross-split requests, the trail-cap exit and the try_this_square fallback counted
and equal. (5days' grid corpus runs no Dijkstra search: allocs 0 there, as before.)

## 4. Release smoke, the 0383 release itself (c6824107, no lab overlay) -- a fixture in which the search DOES run
| cell | game, fixture | routestamp | exit | click journeys | frames_skipped | stamp |
|---|---|---|---|---|---|---|
| RM83-SMOKE-5days | 5days, fresh start, DOSAGS_TICKCLICKS=1000,50,50, 4,000 ticks | **allocs=1 peak_bytes=64000** | 0 | 50 | 31 | f2e183845d2f |
| RM83-SMOKE-mmd | MMD, save 7, DOSAGS_TICKCLICKS=5500,60,20, to tick 6,800 | allocs=0 peak_bytes=0 (this sweep asks for no search) | 0 | 20 | 5 | f2e183845d2f |
The 5days cell matches the 0382 release's two cells on the same fixture (RF0382-2026-11-17 section 3a: switch off and
on, 50 journeys and 31 skipped frames in each), and the MMD cell matches 0382's (20 journeys, 5 skipped).

## 5. Ratchet
`.sdl-dos-ports/shared/tools/ratchet.sh --root <rm0383> --no-build --no-host-wait --capture-display 398 --no-record`.

| run | result |
|---|---|
| 20261117T195038Z | PASS: 41 pass (12 improved), 0 fail, 0 blocked, 4 quarantined; exe-bytes 8711712 and code-lock-bytes 5231440 read IMPROVED against 0382's limits |
| limits, tightened on this branch (tests/ratchet.yaml, the LIMIT comment rewritten: it no longer names a switch) | exe-bytes 8715475 -> 8711712 (-3,763; +4,011 against 0381), code-lock-bytes 5234928 -> 5231440 (-3,488; +2,928 against 0381) |

## 6. Not done here
- No rig round: the surviving code is the F arm of round RR byte for byte in its search body; the release binary differs
  from round RR's (the switch tests and the old body are gone), which the identity cells and the smoke cover in DOSBox-X.
  A registered MS3 pair on this binary belongs to the next rig round, whatever its question is.
- The partial_waits observation from round RR (the board counted one extra wait in each F cell, no event lost) is open
  and is now a property of every run; it goes to the next round's watch list.
