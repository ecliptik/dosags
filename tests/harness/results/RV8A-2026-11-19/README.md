# RV8A -- Trilby S8 (room 35, 8-bit 512x384) on the v0.1.1 exe, first reading (written 2026-11-19; pre-registration, before any data)
- Binary: DISTV11.EXE = AGS.EXE extracted from dosags-v0.1.1.zip (the published v0.1.1 release; zip sha256 e36ef5f9...;
  check-dist --release PASS) = release f2e183845d2f (main 55d2b2fa) byte for byte (sha256 c68241073cb0...), the exe rounds RS / RT
  measured as their A cells. The zip's CWSDPMI.EXE and OPL3BANK.DAT equal the harness-staged files (checked). VOID if any differs.
- Fixture: R1R1's S8 line verbatim, as N7S8 / V1S8 (MSGSKIP=1, drive 3; gatebar --msgskip).
- Witness: STDOUT "vmmode DOSAGS_VM=(default) mode=3", "englev DOSAGS_ENGLEV=(default) on=1", "guiclip DOSAGS_GUI_CLIP=(default)
  mode=4", "charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guictrlmark DOSAGS_GUI_CTRL_MARK=(default) mode=1", "routeprewarm
  DOSAGS_ROUTE_PREWARM=(default) mode=0"; BLASTER.TXT "A220 I7 D3 P330 T3"; else VOID.
- Bar (PLAN-GATES, unchanged): both tick figures 39.2-40.8, fps_p50 >= 40, completeness >= 95%, screen witness clean, audio
  counters clean; the campaign line 99% displayed. Scored by tests/harness/gatebar.py after the round (as V1).
- Prediction: N7S8 99.32% / V1S8 99.44%: displayed 99.3-99.6%, steady 40.1-40.3, whole-run 39.10-39.40.
- REGRESSION line (reported beside the verdict): displayed < 99.0% or any audio counter non-zero. A tick figure out of band is
  NOT MET as registered (V1's rule), with preloop_ms / loop_ms / tail_ms printed beside it.
- Witness: the camera sheet (dark room). With RV8B this is the scene's registered pair on f2e183845d2f.
- Round RV (the v0.1.1 gates): WARMUPRV, RVDST, RV16A, RV32A, RV8A, RV16B, RV32B, RV8B; one power-on, cap 120 min; dated 2026-11-19.
