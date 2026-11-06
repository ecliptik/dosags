# GR16WBP -- WB poll control at S16 on the RELEASE flavour, round R2 (written 2026-11-05; pre-registration, before any data)
- Binary: rel.exe = build/ags-release/ags.exe (DOSAGS_RELEASE=1, main f2228d5e; minstack 512k explicit since 806b0ec1, exe unchanged),
  stamp a1dba5d61624, build_dirty 0, 8,598,425 B, sha256 1fc012c16d41...; R1's binary. VOID if the staged stamp differs.
- Fixture: WBC16R's line verbatim (build/ws/roundBATCH/WBC16.ARGS: 5days --startr 13, music 0, no PCM, IDLE drive 0, native 16-bit,
  S32P-ACSETUP-ON.CFG:ACSETUP.CFG, MAX_SCALE=1, direct framebuffer, TAS 6500, SDL_HINT_DOS_AUDIO_BACKEND=wb _WB_TX_DELAY=320
  _WB_DRR_POLL=1 _WB_RTC_PUMP=1, --no-fine-timing, PGSB, MIN_WAIT 450, --timeout 1800) + the BLASTER line, plus --env DOSAGS_MIDI_TICK=poll.
- Valid only if: midi_tick=poll, stamp, build_dirty 0, bpp 2, room 13, NO PCM play logged, manifest complete, card locked, one audio segment.
- Witness: BLASTER.TXT (RUN.BAT `ECHO %BLASTER% > BLASTER.TXT`, --collect) must read "A220 I7 D3 P330 T3" stripped, else VOID.
  Camera sheet first. Capture: operator 2026-11-05 bar -- R2 only after a named stick/cable swap + 90 min clean (vcctrl).
- Scored by GR16WBR's depth-score.py line: GR16WBP is its B control; its D is information. Run order GR16WBP then GR16WBR, adjacent.
- Comparison: WBC16P on ef123dba0adf, D 0.794 (information).
- Round R2: WARMUPR2, GR16WBP, GR16WBR, GR16, GR32P; one power-on, cap 75 min; dated 2026-11-05, else re-dated first.
