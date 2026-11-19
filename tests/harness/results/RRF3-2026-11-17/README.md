# RRF3 -- MS3 on the 0382 release, route-finder arm F (written 2026-11-17; pre-registration, before any data)
- Binary: R0382.EXE = the ags 0382 release (ags 0001-0382; 0382 = the route finder's levers behind DOSAGS_ROUTE_FAST,
  default off), DOSAGS_RELEASE=1, sha256 5ea0d5cc846a13ed..., 8,676,821 B, stamp 483247a02652, build_dirty=0 (an
  incremental and a clean build byte-identical; RF0382-2026-11-17). Staged from build/ws/roundRR (expected.txt: r0382.exe,
  l308.exe, AGSSAVE.007); a mismatch stops the round before power-on; a manifest stamp other than 483247a02652 is
  STAMP-VOID. BLASTER.TXT "A220 I7 D3 P330 T3" (else STOP at the warm-up).
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  DOSAGS_GUI_CTRL_MARK=(default) mode=1", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup
  line is missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Play line: P9M1's verbatim (AGSSAVE.007 f486d0e9..., ACSETUP-ON-512X384-ROUND.CFG, --no-fine-timing, TAS exit 12440), as
  rounds RN / RO / RQ (without RQ's `DIR C:\ /A` lines).
- DRIVE 6, DRIVE6_MODE=ms, the calibrated values (RRCALQ / RRCAL).
- Arm: F (DOSAGS_ROUTE_FAST=1: the stamp grid, the frontier walk, the inline line-of-sight walk). Third pair (its own block; dropped first on time).
- Read by tests/harness/rr-read.py (committed with this pre-registration; its docstring is the rule): `rr-read.py cell`
  per cell (READ.txt), `rr-read.py verdict` over every cell that ran (VERDICT.txt).
- VALID cell: the arm witness in RUNMANI.LOG -- "DOS-PORT routefast on=0 stamp_allocs=0 ..." for O; "on=1", stamp_allocs
  >= 1 and stamp_peak_bytes=192000 for F (room 2's mask is 960 x 200; an F cell whose fast search never ran is VOID) --
  the manifest stamp binary_sha12=483247a02652 in the cell's logs (checked by rr-read.py itself, as well as by the
  driver), RUNMANIFEST exit_code=0 and "ENGINE HAS SHUTDOWN", audio underruns = overwrites = 0, the driver's BLASTER
  check, and the pairing: PAIR-OK, PAIR-OK-114LATE (ms3-pairing.py), or -- for this round only -- 114EDGE (below). A VOID
  cell is read by no term.
- Readings: skips = RUNMANI frames_skipped (the same exit tick 12,440 in every cell); displayed = 1 - skips / 7,003;
  skips per CLICK second and per OTHER second from the persec rows (a second is a click second when a click journey's
  t_ms falls in it).
- The term (needs a registered pair: >= 2 valid cells in EACH arm, else NOT READ). CUT = mean(O skips) - mean(F skips);
  SPREAD = the larger of the two arms' in-round ranges.
  R-SKIPS SUPPORTED: CUT >= 80 skips per run (the lab's X: 0.70 per click-second x 114), CUT > SPREAD, and every F cell
    below every O cell.
  R-SKIPS FALSIFIED: CUT < 23 (0.20 x 114).
  MIXED: anything else.
  The third pair (RRF3 / RRO3) is read only when BOTH of its cells are valid; otherwise the verdict is over the
  registered cells and a lone third-pair cell is printed as information.
  Information: the proof bar for the MS3 target reads YES only if every valid F cell, and at least two, is >= 99.0%.
  What follows: SUPPORTED -> the switch's default goes to the operator (after it, a following patch removes the switch and
  the body that lost). FALSIFIED or MIXED -> back to the lab through sdlports; no default question is put.
- The lab's prediction, stated before the round (lab-rb RESULT-RSW-2 eb92f3b9 and the 0382 lab result; a MODEL of the 486
  from DOSBox-X measurements, never measured on the 486, and a narrow pass: rule-H minima carry +-0.3 per click-second):
  CUT between 153 and 220 skips per run (rule H 571 -> 407..418; rule P 571 -> 351), the ensemble's smallest member near
  40; displayed about 94.0-95.0% in F against about 91.6-91.8% in O (RQ's O cells: 577 / 589 skips). The control: skips
  per OTHER second should not move by more than the O pair's own difference.
- Press 114 under the predicted outcome (restated after sdlports' review, before any data). The levers shorten click
  ticks, so less game time is lost and the run ENDS EARLIER; the presses are wall-timed, so the last press moves toward
  the end of the run. In RQ's O cells press 114's game time sat 2.5 s before the loop end (margins -2,573 / -2,544 ms;
  114 journeys, PAIR-OK), and press 113 is 1.14 s before press 114.
  - The saving per click on the 486, from the lab's per-room savings (0382 ON against plain: room 1 27.1 lab ms, room 2
    4.4) and RLTA's own click-tick ratios (sdlports: room 1 133.0 ms on the 486 against 80.24 lab = 1.66x; room 2 71.9
    against 32.16 = 2.24x): room 1 45 ms x 16 clicks + room 2 9.8 ms x 98 clicks = 1.7 s. The room-2 fill (384,000 bytes
    per call) is priced by the model at about 7-9 ms; at this machine's measured memory rates it is plausibly 11-15 ms,
    which adds 0.2-0.8 s. **Predicted: the run ends 1.7-2.5 s earlier; the 486 tick record bounds it near 3.7 s.**
  - So press 114's margin is predicted between about -0.9 and -0.05 s (PAIR-OK, 114 journeys), and it may pass the end.
    Both F cells would sit at about the same margin, so the pairing rule must read every case:
    - margin clearly negative: 114 journeys, PAIR-OK;
    - margin clearly positive (the run ended before press 114): 113 journeys, PAIR-OK-114LATE (ms3-pairing.py's rule);
    - **114EDGE (this round only, in rr-read.py):** 113 journeys for 114 presses, the pairing's ONLY failures are (3a) /
      (3b), and press 114's estimated game time is no more than 150 ms short of the loop-end estimate. VALID. The 150 ms:
      a click needs its own click tick (about 60-70 ms with the levers) and up to two more frames (50 ms) to be presented
      and logged, and the pairing's estimates carry +-30 ms.
    - **112 journeys or fewer: PAIR-VOID, a STATED LIMIT of this fixture.** It would mean the run ended more than about
      3.7 s earlier (a saving above about 31 ms per click); MS3's press schedule then needs changing before the levers can
      be read on it, and the F arm is NOT READ this round. No 113LATE rule is added.
  - A 114LATE or 114EDGE cell ran one click fewer than a 114-journey cell (about 4 skips: one click-second); its count of
    click seconds is printed so the difference is seen.
- Memory: the levers keep one stamp grid, W x H bytes of locked heap: 64,000 bytes for room 1's 320 x 200 mask, 192,000
  for room 2's 960 x 200; freed and re-allocated on the room change, so at most 192,000 bytes at a time (47 pages).
  Witness: stamp_allocs and stamp_peak_bytes on the routefast line; a failed allocation would quit with "insufficient
  memory to allocate pathfinder stamp buffer" (the cell is then not a clean exit).
- A STOP in an F cell: the driver labels it and the round stops there with NO recovery cycle (any power cycle goes to the
  operator). Attribution by hand from the cell's records: in play (AGS started per STDOUT.TXT / RUNMANI.LOG, or the
  camera shows the game or a frozen game screen) = a finding AGAINST the levers; outside AGS (staging, a run-hw refusal,
  the FTP collect / return reboot with the game's clean shutdown on record) = a rig stop, and the F arm is NOT READ.
- Not in this round, stated: Trilby's Notes. The lab's grid corpus read the levers 1.5% SLOWER per request in Trilby's
  room; no rig fixture makes Trilby ask for routes, so that stays a stated limit of this round, not a tested one. And
  no dispatch-cost measurement for the native-compilation research: its program does not exist yet and the cap has no
  room beside the third pair.
- Simulation (before any data; scratch copies of RQO1 / RQO2 with the 0382 stamp and a routefast line, frames_skipped
  edited; "ended S earlier" = the persec ms compressed linearly and every click journey later than the new loop-end
  estimate dropped): two O copies and two F copies at 410 / 430 skips read R-SKIPS SUPPORTED (CUT 163, SPREAD 20) with the F
  run ended 0 / 1.7 / 2.4 s earlier (PAIR-OK), 2.56 s (one F cell 114EDGE at margin -6 ms, the other PAIR-OK), 2.7 and
  3.6 s (PAIR-OK-114LATE); at 3.8 s both F cells have 112 journeys, PAIR-VOID, and the term is NOT READ (the stated
  limit). F copies at 570 / 575 read FALSIFIED (CUT 10.5); an F copy with stamp_allocs=0, or with another manifest stamp,
  is VOID; a lone valid RRF3 (300 skips) is printed and left out of the verdict, and with a valid RRO3 beside it both
  enter (SPREAD then 130); F copies at 60 / 65 skips beside one at 410 read the proof bar "no".
- Round RR: the route-finder levers' ABBA on MS3. WARMUPRR, RRCALQ [-> RRCAL on a calq miss], RRO1 RRF1 RRF2 RRO2 (the
  registered pairs), then RRF3 RRO3 (a third pair, its own block). One power-on, CAP_MIN 120. Budget line (as RQ): need at
  RRCALQ 1520 s (calq 760 + the full cal 760, counted up front); the ABBA's graded needs RRO1 3040 / RRF1 2280 / RRF2 1520 /
  RRO2 760; the third pair RRF3 1520 / RRO3 760 (it runs only if both fit). After the warm-up: 4560 s for the cal and the
  four registered cells, 6080 s with the third pair, vs 120 x 60 - warm-up 630 - 240 = 6330 s: the registered pairs keep
  about 1,770 s of slack; the third pair is dropped first (a warm-up more than ~250 s over its 630, or cells running long).
  MS3 target: 99% frames displayed on MS3 (operator 2026-11-13; kept 2026-11-17, "Keep 99%, add research"); the proof bar
  is a REGISTERED pair, both cells >= 99.0%. This round is NOT expected to meet it: the lab model reads about 94-95% with
  the levers on. Its question is whether the levers cut skips on the 486 at all, and by how much.
- USB4VC firmware 0.5.109. Reported per cell: pkt_partial / pkt_timeout / mouse.dropped and ev_in == pkt_built; a partial
  voids an MS3 cell from that press (rule M0).
