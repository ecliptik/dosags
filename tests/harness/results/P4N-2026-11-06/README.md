# P4N -- round C4 cell, instrumented trio P4C, arm 0x00 fusion off (written 2026-11-06; pre-registration, before any data)
- Binary: VM3INS.EXE (stamp 4bbb3f1224a5, build_dirty=1, 8,674,469 B, sha256 82c9400ed79e...); VOID if it differs. Same code as the
  timed AGSVM4 (only the 13 stamp bytes differ).
- Fixture: F1MMDK's line (ACSETUP-ON, PGSB, TAS 5000, room 50 idle) WITHOUT --no-fine-timing, + DOSAGS_VM=fast + DOSAGS_VM_FUSE:
  P4F = 0x3F, P4B = 0x03, P4N = 0x00. Read: tickstats_script_vm total_ms / ticks (f1/f1prof.py), update_game_once, render per pass.
- Comparison: F1b's VMPROF (slice 2 = 0x00 without the division fixes, sound OFF): script_vm 12.70 ms/tick, logic 17.44, pass 9.04.
- Prediction (sound on may add a few tenths to every arm alike): P4F 11.7-12.9 ms/tick; P4N = P4F + 0.27 to +0.43 (H-CPI);
  P4B = P4F + 0.10 to +0.15 (H-CPI) or <= P4F (H-cache). Render per pass unchanged across arms (9.0 +- 0.4).
- FALSIFIER of the cache hypothesis: P4B - P4F >= +0.08 ms/tick. Also scored: r on the 486 = (P4N - P4F) / 0.701.
- Reading rule: release (R4*) decides the KPI; the profile (P4*) decides the mechanism. If they disagree, report both, claim neither.
- x1 each: a mechanism test, not a KPI claim.
- Round C4 (PLAN-FPS lever V, slice-3 cache test): WARMUPC4, R4F, P4B, R4N, P4F, R4B, P4N; one power-on, cap 90 min; dated 2026-11-06.
- NOT RUN: dropped by the driver's cap guard (650 s left < 700 s at 07:21:05Z). A later round if needed.
