# RF0382-2026-11-17 -- landing records for ags 0382 (the legacy route finder's levers; DOSAGS_ROUTE_FAST, OFF by default)

DOSBox-X and build host only; nothing here touched the rig. Branch `rf0382` (worktree dosags-ring) on main 64fc3b05 +
patches/ags/0382. For sdlports' review; not merged.

## 1. The patch
- **What:** the three output-identical route-finder levers the lab gated (lab-rb docs/lab/move-lab/ms99: PREREG-R-SW,
  RESULT-RSW-1 identity, RESULT-RSW-2 reading, RESULT-P82 this patch's own lab result) behind a TEMPORARY switch,
  default OFF, tested once per CALL (sdlports' ruling 2026-11-17):
  - unset: find_route_dijkstra and do_line run as they were. Their text is untouched: the diff removes exactly two lines,
    the two call sites (in __find_route and in can_see_from).
  - DOSAGS_ROUTE_FAST=1 (exactly "1"): find_route_dijkstra_fast -- the function's text with R1 (a uint8 generation stamp
    per mask cell instead of the 0xFF fill of beenhere) and R2 (each pass walks a bitset of the active slots) -- and, in
    can_see_from, R3 (do_line's pixel walk inline on an 8-bit mask, stopping at the first wall).
- **Memory:** one stamp grid, W x H bytes (64,000 for a 320 x 200 mask, 192,000 for 960 x 200), allocated at the first
  search on a mask size, freed and re-allocated when the size changes, freed in ~LegacyRouteFinder. A failed allocation
  quits ("insufficient memory to allocate pathfinder stamp buffer"); today's per-call beenhere buffer, twice that size, is
  unchecked.
- **Witness:** RUNMANI.LOG `DOS-PORT routefast on= stamp_allocs= stamp_peak_bytes=` (allocs counts size changes, not
  searches); DOSAGS_ROUTE_FAST joins the env allowlist (quit.cpp), so each arm hashes differently.
- **TEMPORARY:** the commit message states the removal -- after the 486 A/B and the operator's ruling on the default, a
  following patch removes the switch and the body that lost.
- No lab knob, no loop counters, no lab file. Written by lab-rb docs/lab/move-lab/ms99/make-0382.py, which takes the lever
  text from the gated lab overlay; the script's output equals the committed vendor file (sha256 a5ea8310...).
- Slots: 0374 (cap-3 lever) and 0375 (hitchdiag) stay reserved; 0382 is the next free.
- Provenance: patches/ags/0382 is `git format-patch` of the vendor commit; after `make patches` the vendor tree is
  e6ab9a74c1baf2a96098777ea529daa271732805, the authored commit's tree. ASCII only; no fopen.
- One fix-up before these records (branch commit 540c7922): the first release smoke showed the witness printing on=0
  with the switch set when no route was asked for; the line now evaluates the switch itself. Everything below is from
  after that fix.

## 2. Builds (make patches first; round 1 incremental, round 2 with build/ags + build/ags-release wiped)
| flavour | sha256 | stamp | bytes | vs 0379 / 0381 | r1 == r2 |
|---|---|---|---|---|---|
| instrumented | 6b65deb124d608ce0b8102190abf7d239aabc301677d6d6ae76740ff186f3d63 | 1aa3e2ce83b7 | 8,715,475 | +7,774 (1d8252a6, 8,707,701) | yes |
| release (DOSAGS_RELEASE=1) | 5ea0d5cc846a13edd5ffac31b26ada72bf000ec527462bb4af89cb574e749f23 | 483247a02652 (printed by the smoke cells) | 8,676,821 | +7,262 (2191042b, 8,669,559) | yes |

`make build-dirty`: 0.

## 3. Lab smoke (DOSBox-X, the 0382 release itself, no lab overlay)
| cell | game, fixture | env | routefast | exit | frames_skipped | env_block_sha |
|---|---|---|---|---|---|---|
| RF82-SMOKE-mmd-off | MMD, save 7, DOSAGS_TICKCLICKS=5500,60,20, to tick 6,800 | none | on=0 allocs=0 | 0 | 5 | 48d1a37a20a2 |
| RF82-SMOKE-mmd-on | the same | DOSAGS_ROUTE_FAST=1 | on=1 allocs=0 | 0 | 5 | 39674386e6a6 |
| RF82-SMOKE-aq-off | AGS Quest, fresh start, 4,000 ticks | none | on=0 allocs=0 | 0 | 822 | 60b897dc76c4 |
| RF82-SMOKE-aq-on | the same | DOSAGS_ROUTE_FAST=1 | on=1 allocs=0 | 0 | 822 | 6317ddf1a3b8 |
- Clean exits with the switch unset and set; the env witness differs per arm; 20 tick-keyed clicks and 20 click journeys
  in each MMD cell.
- **The fast search did not run in the smoke** (stamp_allocs=0): these fixtures ask for no Dijkstra search (the engine's
  tick-click sweep lands on MMD's action bar or on points in plain line of sight; AGS Quest's intro asks for no route).
  In a release-flavour binary the ON body is exercised by the lab build P82LR's identity cells (section 4), and on the
  rig an F cell without stamp_allocs >= 1 is VOID by the round's pre-registration.

### 3a. Added after round RR: a release smoke in which the fast search DOES run (sdlports' requirement for the removal patch)
A non-lab fixture exists after all: **5days, fresh start, the engine's tick-keyed clicks DOSAGS_TICKCLICKS=1000,50,50,
4,000 ticks.** The 0382 release itself (5ea0d5cc, no overlay):

| cell | env | routefast | exit | click journeys | frames_skipped | env_block_sha |
|---|---|---|---|---|---|---|
| RF82-SRCH-5days-off | none | on=0 allocs=0 | 0 | 50 | 31 | 60b897dc76c4 |
| RF82-SRCH-5days | DOSAGS_ROUTE_FAST=1 | **on=1 stamp_allocs=1 stamp_peak_bytes=64000** | 0 | 50 | 31 | 6317ddf1a3b8 |

The same sweep on Trilby's Notes, on MMD's fresh start and on MMD's save 7 (130 clicks) asks for no Dijkstra search
(stamp_allocs=0 in each). So 5days with tick-keyed clicks is the release smoke fixture for the fast body from here on.

## 4. The lab on the patch's two bodies (lab-rb RESULT-P82, 7c0a5f96)
Lab builds = the lab's REF overlay + the patch's source change (make-0382.py --lab): P82LI / P82LR / P82LM.
- **Identity, both flavours, both switch values, against REF:** 24 cells IDENTICAL (MS3's 114 route calls, the 5,292
  request grid corpus, the 2,892 cross-split requests; the trail-cap exit and the try_this_square fallback counted and
  equal). On MS3 the ON witness reads on=1 stamp_allocs=2 stamp_peak_bytes=192000.
- **OFF against plain:** +0.09 lab ms per click tick (limit 0.5); per call +0.2% / +0.3%.
- **ON, directly:** 38,455 / 10,826 lab us per warm call in rooms 1 / 2 (SW123: 38,441 / 10,821); click ticks -7.58 lab
  ms against plain (SW123 -7.68).
- **The model reading on this build, by the letter:** 1.164 (min 0.333) instrumented, 1.266 (min 0.423) release, by rule
  H; rule P 1.515 / 1.753. The instrumented minimum is under 0.35 and the release mean under SW123's 1.340; the verdict
  rests on SW123's pre-registered pass plus the direct cost equivalence (sdlports' ruling after the figures; RESULT-P82
  has the reasoning and rule H's +-0.3). MS3 by the model, release: 571 -> 418 skips (rule H), 351 (rule P). A narrow
  lab pass; the 486 settles it.

## 5. Ratchet
`.sdl-dos-ports/shared/tools/ratchet.sh --root <rf0382> --no-build --no-host-wait --capture-display 398 --no-record`.

| run | result |
|---|---|
| 20261117T115135Z | FAIL: 39 pass (10 improved), 2 fail, 0 blocked, 4 quarantined -- exe-bytes 8715475 > 8707701 and code-lock-bytes 5234928 > 5228512 (0382's code, expected); nothing else |
| proposed limits (exact; tests/ratchet.yaml LIMIT comment) | exe-bytes 8707701 -> 8715475 (+7,774), code-lock-bytes 5228512 -> 5234928 (+6,416) |

The limits are not edited on this branch; raising them is a commit sdlports reviews with the merge.

## 6. Not done here
- The MS3 rig round (RR): pre-registered on this branch (tests/harness/results/*RR*-2026-11-17, tests/harness/rr-read.py)
  for sdlports' review. Power-on needs the operator's direct OK.
- The removal patch (the switch and the body that loses): after the round and the operator's ruling on the default.
