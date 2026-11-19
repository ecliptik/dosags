# WARMUPRL -- rig warm-up (and the powered check of USB4VC 0.5.109) (written 2026-11-12; pre-registration, before any data)
- l308.exe (bc9c3704a839), MMD title, not scored. Checks: BLASTER.TXT = "A220 I7 D3 P330 T3" else STOP; capture device present
  at the pre-flight; a capture STALE of any kind but "nolock" stops the round. DIRLIST.TXT: a read-only listing of C:\DOSAGS.
  The cell types RUN.BAT through the rig's keyboard on the new firmware: a typing failure (the cell not running) stops the round.
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
- Capture stick: on probation (back on the Pi's usb1-2 since 22:38:11Z after the operator's reseat; it failed on this port
  before). Pre-flight video_state / camera_state before relay-on. A capture drop mid-round does not stop the round on its own:
  the camera is the play witness (the stick never locks MMD's mode anyway) and the game's own log is the pointing witness.
- Round RL (operator 2026-11-12: flash 0.5.109 first, then the audio test plus the MS3 baseline; sdlports' terms): WARMUPRL,
  RLCALQ (re-check against RJCAL) [-> RLCAL, the full cal, on any calq miss], RLTA / RLTB (the PUMP_TIMEOUT pair, instrumented
  MS3), RLM1..RLM4 (MS3 baseline), RLP1 (one P9M1 bridge cell; first to drop). One power-on, cap 120 min. Budget line: need
  at RLCALQ 3080 s (calq 760 + full cal 760 up front + the pair 1560; amended before data per sdlports, so a long warm-up
  costs MS3 cells, not the pair), then the MS3 block's graded needs from RLM1 (3040 / 2280 / 1520 / 760), vs CAP_MIN 120 x 60
  - warm-up ~600 - 240 = ~6350 s; RLP1 (760) runs only if the full cal did not. Harness: local main (drive6-gate.sh with M0, calq drift,
  NEXT-FULL-CAL; cell-template-d6.sh FW_EXPECT 0.5.109). Campaign: MS3 is the measure, its target set from this baseline.
