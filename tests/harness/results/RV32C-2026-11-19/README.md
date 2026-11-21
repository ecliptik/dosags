# RV32C -- 5 Days S32P (room 3, forced 32-bit, 640x480 centred 1x, pack24) on the v0.1.1 exe, third reading (written 2026-11-19; pre-registration, before any data)
- Binary: DISTV11.EXE = AGS.EXE extracted from dosags-v0.1.1.zip (the published v0.1.1 release; zip sha256 e36ef5f9...;
  check-dist --release PASS) = release f2e183845d2f (main 55d2b2fa) byte for byte (sha256 c68241073cb0...), the exe rounds RS / RT
  measured as their A cells. The zip's CWSDPMI.EXE and OPL3BANK.DAT equal the harness-staged files (checked). VOID if any differs.
- Fixture: GR32P's line verbatim, as N7S32 / V1S32 (S32P-ACSETUP-ON.CFG from round V1's staging, sha256 24d874f2...).
- Witness: STDOUT "vmmode DOSAGS_VM=(default) mode=3", "englev DOSAGS_ENGLEV=(default) on=1", "guiclip DOSAGS_GUI_CLIP=(default)
  mode=4", "charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guictrlmark DOSAGS_GUI_CTRL_MARK=(default) mode=1", "routeprewarm
  DOSAGS_ROUTE_PREWARM=(default) mode=0"; BLASTER.TXT "A220 I7 D3 P330 T3"; else VOID.
- Bar (PLAN-GATES, unchanged): both tick figures 39.2-40.8, fps_p50 >= 40, completeness >= 95%, screen witness clean, audio
  counters clean; the campaign line 99% displayed. Scored by tests/harness/gatebar.py after the round (as V1).
- Prediction: N7S32 99.52% / V1S32 99.64%: displayed 99.3-99.7%, steady 40.0-40.3, whole-run 39.10-39.40.
- REGRESSION line (reported beside the verdict): displayed < 99.0% or any audio counter non-zero. A tick figure out of band is
  NOT MET as registered (V1's rule), with preloop_ms / loop_ms / tail_ms printed beside it.
- Witness: the capture sheet (640x480 locks). With the first reading RV32A this is the scene's registered pair on f2e183845d2f.
- Round RV, third power-on (operator via sdlports: "One more power-on, 3 runs"): WARMUPRX, RV16C, RV32C, RV8C; cap 120 min (~45 expected); dated 2026-11-19.
- Witness fallback, registered before any data (the capture stick dropped 10 times in the second power-on): if the capture sheet
  has no frame of the game inside RV32C's play window, the camera sheet is RV32C's screen witness, and the cell is read on it
  (CLEAN required). If neither sheet shows the game, RV32C is VOID. A partial capture (frames for part of the window) is read
  on the capture frames it has, with the camera for the rest.
