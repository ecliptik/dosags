# RLM1 -- MS3 (moving fixture) on ags 0373's release, default config: the campaign baseline cell (written 2026-11-12; pre-registration, before any data)
- Binary: RLREL.EXE = main 728706d9 release (ags 0001-0373), stamp 942ad0260d36, build_dirty=0, sha256 36473d61...; = the
  reviewed L2DREL (R2 on and L2 on by default; L1 off; the 0374 cap not in this build). VOID if the staged stamp differs.
  BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  DOSAGS_GUI_CTRL_MARK=(default) mode=1", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup
  line is missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Play line: P9M1's verbatim (AGSSAVE.007 f486d0e9..., ACSETUP-ON-512X384-ROUND.CFG, --no-fine-timing, TAS exit 12440).
- MS3: DRIVE 6, DRIVE6_MODE=ms, one-call presses, the values from RLCALQ (or RLCAL); 114 presses. Runs only after a
  calibration GATE PASS. Pointing witness (drive6-gate.sh --play): M0 first (a board pkt_partial voids from the press whose
  call meets it), then G0 / G1 / D1+ (all 114 presses sent and ok, every press walks, rooms exactly [1, 2], A room 817..841,
  B 916..940, y 116..140). A PLAY-VOID cell is VOID for the baseline (reported, not scored); two VOIDs stop the block.
  INPUT-LOG mouse.dropped is reported; a drop VOIDs a cell only through M0 or the walk / landing checks.
- The MS3 baseline (the campaign's measure): RLM1..RLM4, default config on ags 0373 (L2 on). Reported: displayed = 1 -
  frames_skipped/ticks per cell, the mean and SD, skips per window (room 1 + exit, room 2), catchup and audio lines.
  Expectation, information only (not a falsifiable prediction): round RK's RKM1 / RKM2 -- VOID cells on one press each, with
  113 of 114 presses walking, same build -- read 90.4 / 91.6% displayed. The est486b model (81-83%) looked pessimistic there
  and is not quoted as an expectation until refitted. Scene rule: MS3's displayed % is never
  reported in the same column as P9M1's. No target is set by this round; the operator sets it from this baseline.
- USB4VC firmware 0.5.109 (flashed 2026-11-12 ~00:08Z by vcctrl, operator's OK in this session: 0.5.108's resume plus one
  queued event = one packet in strict order, replayed with its original spacing (capped at 250 ms), never merged across a
  button change, consolidating only at a 14-deep queue; a 5 s budget for a packet not yet started). Each cell's BOARD-TAKE.json
  fw_ver must read [0, 5, 109] (FW_EXPECT 0.5.109). Firmware verdict for this round, per DRIVE 6 cell, from INPUT-LOG.jsonl
  mouse.dropped and vcctrl's per-cell board report: PASS if pkt_partial 0 and pkt_timeout 0 in every in-play window AND
  ev_in == pkt_built over the cell (no summing; a nonzero gap means the queue really reached 14) AND, in every MS3 cell, the
  press spanning each known stall (~+132 / ~+178 s after the lock) lands at its OWN target (late is allowed). FAIL if any
  pkt_partial / pkt_timeout > 0, or a stall-spanning press lands at another press's target. A resume under 200 ms is an
  ordinary wait, not a rescue; max_wait_ms is a high-water mark. The powered check of 0.5.109 rides on WARMUPRL (typing)
  and RLCALQ (clicks): a keyboard or click failure there stops the round.
- Round RL (operator 2026-11-12: flash 0.5.109 first, then the audio test plus the MS3 baseline; sdlports' terms): WARMUPRL,
  RLCALQ (re-check against RJCAL) [-> RLCAL, the full cal, on any calq miss], RLTA / RLTB (the PUMP_TIMEOUT pair, instrumented
  MS3), RLM1..RLM4 (MS3 baseline), RLP1 (one P9M1 bridge cell; first to drop). One power-on, cap 120 min. Budget line: need
  at RLCALQ 3080 s (calq 760 + full cal 760 up front + the pair 1560; amended before data per sdlports, so a long warm-up
  costs MS3 cells, not the pair), then the MS3 block's graded needs from RLM1 (3040 / 2280 / 1520 / 760), vs CAP_MIN 120 x 60
  - warm-up ~600 - 240 = ~6350 s; RLP1 (760) runs only if the full cal did not. Harness: local main (drive6-gate.sh with M0, calq drift,
  NEXT-FULL-CAL; cell-template-d6.sh FW_EXPECT 0.5.109). Campaign: MS3 is the measure, its target set from this baseline.
