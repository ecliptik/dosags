# RLCAL -- DRIVE 6 full calibration (runs only on a calq miss) (written 2026-11-12; pre-registration, before any data)
- Binary: RLREL.EXE = main 728706d9 release (ags 0001-0373), stamp 942ad0260d36, build_dirty=0, sha256 36473d61...; = the
  reviewed L2DREL (R2 on and L2 on by default; L1 off; the 0374 cap not in this build). VOID if the staged stamp differs.
  BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  DOSAGS_GUI_CTRL_MARK=(default) mode=1", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup
  line is missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Play line: P9M1's verbatim (AGSSAVE.007 f486d0e9..., ACSETUP-ON-512X384-ROUND.CFG, --no-fine-timing, TAS exit 12440).
- Runs ONLY if RLCALQ's gate is not GATE PASS; otherwise not run (its dir keeps this README only).
- DRIVE 6, DRIVE6_MODE=cal (61 presses, ~152 s), as RJCAL: the measurement prelude (information), the corner checks, and the
  DXL / DXA / DXB / DY sweeps. Read with `drive6-gate.sh RLCAL --no-recentre`: G0, G1, C1, C2 / C3, C10 (each sweep's >= 15-count
  single packets within 2 px of its line), C9, C8 repeatability, C4-C7 (in band, inside the swept range, >= 15 counts). GATE
  PASS -> its values go to every MS3 cell; anything else (a RECENTRE included: no third cal this power-on) -> no MS3 cell runs;
  the bridge pair still runs. A press-path STOP (G0 / G1) is never answered mid-round.
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
