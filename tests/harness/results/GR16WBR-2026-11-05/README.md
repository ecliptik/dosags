# GR16WBR -- WB pump arm at S16 on the RELEASE flavour, round R2 (written 2026-11-05; pre-registration, before any data)
- Binary: rel.exe (R1's) = build/ags-release/ags.exe a1dba5d61624, build_dirty 0, sha256 1fc012c16d41...; VOID if the stamp differs.
- Fixture: WBC16R's line verbatim (build/ws/roundBATCH/WBC16.ARGS: 5days --startr 13, music 0, no PCM, IDLE drive 0, native 16-bit,
  S32P-ACSETUP-ON.CFG:ACSETUP.CFG, MAX_SCALE=1, direct framebuffer, TAS 6500, SDL_HINT_DOS_AUDIO_BACKEND=wb _WB_TX_DELAY=320
  _WB_DRR_POLL=1 _WB_RTC_PUMP=1, --no-fine-timing, PGSB, MIN_WAIT 450, --timeout 1800) + the BLASTER line.
- Valid only if: midi_tick=rtc, stamp, build_dirty 0, bpp 2, room 13, NO PCM play logged, manifest complete, card locked, one audio segment;
  a capture dropout in either WB cell VOIDs the pair (it is scored from the capture), re-run in a later round.
- Witness: BLASTER.TXT (RUN.BAT `ECHO %BLASTER% > BLASTER.TXT`, --collect) must read "A220 I7 D3 P330 T3" stripped, else VOID.
  Camera sheet first. Capture: operator 2026-11-05 bar -- R2 only after a named stick/cable swap + 90 min clean (vcctrl).
- Scorer (committed before data; = WBC16R's line, lab/wb caff563d registered invocation, archive/lab-wb-2026-11-04 LAB-WB-data/):
  depth-score.py --sha a1dba5d61624 --no-pcm 5days_music0.mid (3e2ac1b9...) D0REF.wav (874b8e8d...) 113.999 GR16WBR-seg01.ogg
  GR16WBR/GR16WBR.LOG GR16WBP-seg01.ogg GR16WBP/GR16WBP.LOG. PASS = A1-A6 + B vs GR16WBP + D >= 0.70 + screen CLEAN + clean exit;
  D < 0.70 with the rest passing: one re-run. Control: the same scorer reproduces WBC16R's PASS exactly.
- Comparison: WBC16R on ef123dba0adf (A PASS, B 0.973 vs 0.634, D 0.785). Prediction: PASS, D 0.70-0.85.
- Round R2: WARMUPR2, GR16WBP, GR16WBR, GR16, GR32P; one power-on, cap 75 min; dated 2026-11-05, else re-dated first.
