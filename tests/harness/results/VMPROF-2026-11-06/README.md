# VMPROF -- VM fast loop, instrumented fine-timing read of script_vm on the 486, MMD character select (written 2026-11-06; pre-registration, before any data)
- Binary: VMINS.EXE = lab instrumented build, stamp b58ad934471b, build_dirty=1, 8,669,273 B, sha256 c1e6b572...; VOID if it differs.
- Fixture: F1MMDK's line but instrumented exe, fine timing ON (no --no-fine-timing), sound off (as round F1a's profile), DOSAGS_VM=fast.
- Read: tickstats_script_vm total_ms/1000 ticks, process_events_dispatch, update_game_once, render passes (fine-timing lines).
- Comparison: round F1a's probe on main, same room: script_vm 20.47 ms/tick, dispatch 21.9, update_game_once 28.2.
- Prediction: script_vm 9.8-13.3 ms/tick (central 11.4: 85% of 20.47 at 1.7-2.6x, the other ~3.1 unchanged);
  update_game_once 17.5-21.5; render per pass unchanged (6.7 +- 0.5 + scene 2.8 +- 0.3).
- FALSIFIER: script_vm > 14.5 ms/tick (VM < ~1.5x on the 486 against 1.82x at fixed cycles on the whole event).
- One cell, x1: it explains D1, it is not a claim.
- Round F1b (PLAN-FPS lever V, slice 2 on the 486): WARMUPF1B, VMA1, VMB1, VMB2, VMA2, VMPROF; one power-on, cap 80 min; dated 2026-11-06, else re-dated first.
