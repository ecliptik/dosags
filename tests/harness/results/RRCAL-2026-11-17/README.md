# RRCAL -- DRIVE 6 calibration on the 0382 release (written 2026-11-17; pre-registration, before any data)
- the full DRIVE 6 calibration, run only on a calq miss; a RECENTRE or STOP ends the MS3 block (no third cal this power-on) (drive6-gate.sh; DRIVE6-RIG-CHECKS Q0-Q4 / G0 G1 C1-C10), as RQCALQ / RQCAL. No switch set (arm O's binary state).
  Not scored. A press-path STOP is never answered mid-round.
- Binary: R0382.EXE = the ags 0382 release (ags 0001-0382; 0382 = the route finder's levers behind DOSAGS_ROUTE_FAST,
  default off), DOSAGS_RELEASE=1, sha256 5ea0d5cc846a13ed..., 8,676,821 B, stamp 483247a02652, build_dirty=0 (an
  incremental and a clean build byte-identical; RF0382-2026-11-17). Staged from build/ws/roundRR (expected.txt: r0382.exe,
  l308.exe, AGSSAVE.007); a mismatch stops the round before power-on; a manifest stamp other than 483247a02652 is
  STAMP-VOID. BLASTER.TXT "A220 I7 D3 P330 T3" (else STOP at the warm-up).
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
