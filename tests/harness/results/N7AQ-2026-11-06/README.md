# N7AQ -- AGS Quest AutoPilot on the shipped build, information cell, target (d) (written 2026-11-06; pre-registration, before any data)
- Binary: N7REL.EXE = main c284ddfd build/ags-release/ags.exe (ags 0001-0365, DOSAGS_RELEASE=1), stamp c754df64babd, build_dirty=0,
  8,646,251 B, sha256 d680e3b6fcfc... (byte-identical to the lab-gated LREL.EXE); staged from build/ws/roundN7 (expected.txt). VOID if it differs.
- No DOSAGS_VM / DOSAGS_ENGLEV / DOSAGS_VM_FUSE in RUN.BAT: STDOUT must carry "DOS-PORT vmmode DOSAGS_VM=(default) mode=3" and
  "DOS-PORT englev DOSAGS_ENGLEV=(default) on=1", else VOID. BLASTER.TXT "A220 I7 D3 P330 T3", else VOID.
- Fixture: F1AQK's line verbatim (F1a: agsquest, drive 0, games/5days/ACSETUP-ON.CFG, --no-fine-timing, MIN_WAIT 240).
- Basis: F1AQK steady 41.09, fps_p50 39.49, displayed 93.04%, stall_ms 89,926 (whole-run 19.79); its cost is GUI + room loads,
  which no landed lever targets; DOSBox-X AutoPilot PASS on this series (all phases ok).
- Information only (no band is claimed): displayed, stall_ms, whole-run and the phase results are reported against F1AQK.
- Exit 0 and all AutoPilot phases ok are required, else the cell is a FAIL (a correctness regression, not a speed one).
- No rendered frame is committed (AGS Quest licence, operator 2026-11-05); image hashes only.
- Round N7 (PLAN-FPS: the landed VM + levers on the shipped build): one power-on, cap 100 min; dated 2026-11-06.
- Order: WARMUPN7, N7M1, N7M2, N7S16, N7S32, N7S8, N7AQ (the last droppable on time).
