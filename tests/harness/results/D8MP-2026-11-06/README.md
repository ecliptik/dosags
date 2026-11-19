# D8MP -- Maniac Mansion Deluxe IN PLAY, per-phase PROFILE on the instrumented exe (written 2026-11-06; pre-registration, AMENDMENT before any D8 data)
- Why: P9M1 / P9M2 (v0.1 release exe) read 67.6% / 67.6% displayed in play (room 1 ~61%, room 2 ~69% renders per tick; fps_p50
  ~28) against 99.90% at the idle character select. Which phase eats the frame budget in play?
- Binary: D8INS.EXE = main c284ddfd instrumented build/ags/ags.exe (stamp f3a8774e03c8, sha256 50c027e7...); VOID if it differs.
  A PROFILE cell: attribution, not a rate figure for the shipped exe (fine timing costs ~0.7 ms/tick on the 486).
- Fixture: P9M1's line (AGSSAVE.007 room 1, host held clicks DRIVE 5, TAS 12440, sound ON cfg) + fine timing ON (run-hw default),
  DOSAGS_TICKLOG=12500, --collect TICKS.BIN. DOSBox-X sanity (same line, no clicks): TICKS.BIN written, f1prof.py parses it.
- Reader (committed): tests/harness/f1/f1prof.py D8MP-2026-11-06 [--lo/--hi per room] -> tickstats ms/tick and the per-tick
  logic / render / scene split.
- Hypotheses, each with its falsifier: (R) render-bound -- render_to_screen + present >= 50% of a skipped tick's busy time;
  falsified if script_vm + process_events_dispatch exceeds render. (S) script-bound -- the opposite. (C) click/pathfinding --
  ticks > 25 ms cluster at click ticks; falsified if fewer than half of the > 25 ms ticks fall within 3 ticks of a click.
- Prediction: (R) holds -- in play the rooms scroll and characters move, so the dirty-rect present redraws most of the screen
  (DOSBox-X hint: present_update_window ~90% of render_to_screen); script_vm stays near the character select's.
- Witness: camera sheet shows kids walking; exit 0; TICKS.BIN present, else VOID. Round D8 (operator "Ok"): WARMUPD8, D8S16, D8S32, D8S8, D8MP; one power-on, cap 85 min; dated 2026-11-06.
