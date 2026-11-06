# N7S32 -- 5 Days S32P (32-bit 640x480) on the shipped build, gate cell (written 2026-11-06; pre-registration, before any data)
- Binary: N7REL.EXE = main c284ddfd build/ags-release/ags.exe (ags 0001-0365, DOSAGS_RELEASE=1), stamp c754df64babd, build_dirty=0,
  8,646,251 B, sha256 d680e3b6fcfc... (byte-identical to the lab-gated LREL.EXE); staged from build/ws/roundN7 (expected.txt). VOID if it differs.
- No DOSAGS_VM / DOSAGS_ENGLEV / DOSAGS_VM_FUSE in RUN.BAT: STDOUT must carry "DOS-PORT vmmode DOSAGS_VM=(default) mode=3" and
  "DOS-PORT englev DOSAGS_ENGLEV=(default) on=1", else VOID. BLASTER.TXT "A220 I7 D3 P330 T3", else VOID.
- Fixture: GR32P's line verbatim (R2: 5days, drive 2, --startr 3, S32P-ACSETUP-ON.CFG, FORCE_COLOR_DEPTH=32, MAX_SCALE=1, PACK24=1).
- Bar (PLAN-GATES, unchanged): both tick figures 39.2-40.8, fps_p50 >= 40, completeness >= 95%, screen witness clean, audio
  counters clean; the campaign line 99% displayed.
- Prediction: as GR32P (39.29 / 40.12, 99.52%): displayed 99.3-99.6%, whole-run 39.15-39.40, steady 40.0-40.3.
- REGRESSION: displayed < 99.0%, any audio counter non-zero, or a tick figure out of band.
- Witness: the capture sheet (640x480 locks) or the camera.
- Round N7 (PLAN-FPS: the landed VM + levers on the shipped build): one power-on, cap 100 min; dated 2026-11-06.
- Order: WARMUPN7, N7M1, N7M2, N7S16, N7S32, N7S8, N7AQ (the last droppable on time).
