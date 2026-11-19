# RLTA -- MS3 instrumented, the DEFAULT audio pump backstop (100 ms): the PUMP_TIMEOUT pair's control (written 2026-11-12; pre-registration, before any data)
- Binary: RLINS.EXE = main 728706d9 instrumented (ags 0001-0373), stamp 39abbc4b5c34, build_dirty=0, sha256 5fc33941...; = the
  reviewed L2DINS. VOID if the staged stamp differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  DOSAGS_GUI_CTRL_MARK=(default) mode=1", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup
  line is missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Fixture: RDMP's line (fine timing on, DOSAGS_TICKLOG=12500, TICKS.BIN) with DRIVE 6 ms and the calibrated values, plus SET
  DOS_PORT_LOG=1 in BOTH cells (the witness line lives in the SDL debug log, LOGS\<TAG5>SDL.LOG, which run-hw already copies
  up and collects; its write cost is the same in both arms). Only after a calibration GATE PASS. The pointing witness of
  RLM1..RLM4 is reported (drive6-gate.sh --play) but does not decide this pair.
- The PUMP_TIMEOUT discriminator (sdlports' terms; lab-rb LAB-MOVE 10.10): round RJ's RJMP and every earlier instrumented 486
  run show 100-200 ms logic-side hitches at fixed offsets from room-2 entry (+818..865, +1720..1747, +3506..3564 ticks; RJMP lc
  9508 / 11294), named by the tick stats as audio_core_entry_poll -> SDL_DOSAudioPump's TryLock spin with its 100 ms
  backstop (SDL/0068). RLTA runs the default (100); RLTB sets SDL_HINT_DOS_DOS_AUDIO_PUMP_TIMEOUT=10.
  Witness: the cell's SDL log line "audio: SDL/0068 SDL_DOSAudioPump TryLock+timeout backstop active (N ms cap; ...)" with
  N = 100 (RLTA) / 10 (RLTB), else the cell is VOID. Proven from the log, not from RUN.BAT.
  Prediction: in RLTB the three known hitches shrink to 10-20 ms quanta; in RLTA they reappear at 100-200 ms as in RJMP / RKMP.
  FALSIFIED (the pump spin is not the mechanism) if any of RLTB's three stays >= 100 ms.
  Audio is a hard bar in both: underruns 0 and overwrites 0. A shorter backstop that buys frames by dropping audio is a trade,
  not a fix, and is reported as one.
  Board (information; vcctrl's per-cell report): if RLTB shows no long holds (no resume >= 200 ms) where RLTA does, that is
  evidence the spin is what holds IRQ12 off. Recorded beside the 486 durations.
  Displayed (fine timing on) is reported apart from RLM1..RLM4, never averaged with them. RLTA is not directly comparable
  to RJMP / RKMP, which ran without DOS_PORT_LOG=1: the in-round pair is the comparison.
- Amendment before any data (2026-11-12, lab-rb 761dc437 / LAB-MOVE 10.14): RKMP showed the board's hold is NOT the slow tick
  itself: at stall #2 the 0.6-1.3 s hold starts >= 0.6 s after the long tick ends and overlaps no tick over 68 ms. The pair's
  verdict is unchanged (it is decided on the 486's tick durations). The board line stays information: a hold that vanishes
  with the 10 ms backstop would support the slave-PIC idea (the spin's BIOS INT 15h/86h waits use IRQ8, beside IRQ12); a
  hold that stays while the hitch shrinks would say the two only share game time.
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
