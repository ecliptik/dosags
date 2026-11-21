# RVDST -- the v0.1.1 zip as shipped, run the way README.TXT says (written 2026-11-19; pre-registration, before any data)
- Binary: DISTV11.EXE = AGS.EXE extracted from dosags-v0.1.1.zip (the published v0.1.1 release; zip sha256 e36ef5f9...;
  check-dist --release PASS) = release f2e183845d2f (main 55d2b2fa) byte for byte (sha256 c68241073cb0...), the exe rounds RS / RT
  measured as their A cells. The zip's CWSDPMI.EXE and OPL3BANK.DAT equal the harness-staged files (checked). VOID if any differs.
- Fixture: DIST2's line verbatim (DIST1's: 5days --startr 3, drive 2, README.TXT's ACSETUP example, --no-fixed-timestep = the
  release default, --no-fine-timing, no direct-framebuffer / backend SETs, TAS 5000, MIN_WAIT 270) + the BLASTER line.
- Witness: STDOUT "vmmode DOSAGS_VM=(default) mode=3", "englev DOSAGS_ENGLEV=(default) on=1", "guiclip DOSAGS_GUI_CLIP=(default)
  mode=4", "charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guictrlmark DOSAGS_GUI_CTRL_MARK=(default) mode=1", "routeprewarm
  DOSAGS_ROUTE_PREWARM=(default) mode=0"; BLASTER.TXT "A220 I7 D3 P330 T3"; else VOID.
- PASS = exit 0, room 3, the fixed-timestep log line reads on, "DosMidiBackend: OPL3/OPL2 chip detected", STDOUT music 0 and
  >= 1 "Playing sound" line, gatebar.py --label S16 --stamp f2e183845d2f --room 3 MET with the camera sheet CLEAN. Else FAIL.
- Prediction: PASS at about DIST2's figures (39.22 / 40.17, 99.42%). Not one of the gate pairs (as DIST2).
- Round RV (the v0.1.1 gates): WARMUPRV, RVDST, RV16A, RV32A, RV8A, RV16B, RV32B, RV8B; one power-on, cap 120 min; dated 2026-11-19.
