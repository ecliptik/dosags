# RLCALQ -- DRIVE 6 short re-check (calq) against round RJ's full calibration (gated) (written 2026-11-12; pre-registration, before any data)
- Binary: RLREL.EXE = main 728706d9 release (ags 0001-0373), stamp 942ad0260d36, build_dirty=0, sha256 36473d61...; = the
  reviewed L2DREL (R2 on and L2 on by default; L1 off; the 0374 cap not in this build). VOID if the staged stamp differs.
  BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  DOSAGS_GUI_CTRL_MARK=(default) mode=1", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup
  line is missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Play line: P9M1's verbatim (AGSSAVE.007 f486d0e9..., ACSETUP-ON-512X384-ROUND.CFG, --no-fine-timing, TAS exit 12440).
- DRIVE 6, DRIVE6_MODE=calq (13 presses, ~34 s of presses): the top-right corner (x 319) and DXL 52 alternating x 3 in room 1,
  the EXIT press (top-left corner, x 0) into room 2, DXA 75 / DXB 42 alternating x 3, all at DY 15 (RJCAL's PASS values).
- Reference: tests/harness/results/RJCAL-2026-11-11 (round RJ's full cal, which PASSed under the amended rules pre-registered
  before that round). RJCAL was measured on ags 0372; L2 (0373) changes GUI drawing, not pointer input, so it still applies.
- Read with `drive6-gate.sh RLCALQ --recheck RJCAL` (DRIVE6-RIG-CHECKS Q0-Q4): Q0 the reference re-reads PASS; Q1 calq used
  its values; Q2 every press walks, rooms exactly [1, 2], no GUI click; Q3 every point inside MS3's landing bands (corners 319 /
  0, DXL x 48..72, DXA x 177..201, DXB x 276..300, every y 116..140); Q4 drift printed beside each point, a point > 6 px from
  the reference -> GATE PASS ... NEXT-FULL-CAL (the next power-on runs the full cal). Any miss -> the full cal (RLCAL) runs in
  this power-on. G0 / G1 apply as in every DRIVE 6 cell.
- Prediction (information): GATE PASS with drift 0-1 px everywhere (RICAL and RJCAL measured the same values to the pixel on
  two power-ons).
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
