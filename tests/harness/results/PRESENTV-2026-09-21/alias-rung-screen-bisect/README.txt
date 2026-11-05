Emulated-SCREEN bisect, DOSBox-X fast conf, bench8 anim12 at Mode 13h (ACSETUP-OFF-NATIVE.CFG, anim12.cfg, OLD package), one
binary per series, frames every 1 s of the emulated display (run-dosbox.sh --screen-series). Metric: median brightness of the
emulator window crop over the middle third of the game-phase frames (a complete room is ~30, patches around the spinners ~8).
  export 8.2   0190 8.2   0191 8.2   0192 8.2   0193 30.0   0194 30.0
  0192 with DOSAGS_DIRECT_VSCREEN=0 (alias off): 8.2, and the ags 0192 verifier reads stale_frames 503/503, first_stale_frame 1
  0192 with DOSAGS_DIRTY_PRESENT=0 (narrowing off): 30.0, verifier 0 stale
  0192 default (alias ON): 8.2 with the verifier reading 0 stale -- the verifier is BLIND at the alias rung.
The physical-screen hardware evidence for the same configuration is F2A1 (incomplete), F2D1 (complete with narrowing off) and F2B1/F2B2 (complete).
sheet-*.png / manifest-*.json only; full-resolution frames are in the scratchpad and are not committed.

brightness-table.txt is the output of tests/harness/screen-completeness.py over the full-resolution frames of these eight series
(kept in the scratchpad, not committed; the sheets here are their contact sheets). Reproduce by running
`AGS_EXE=<binary named ags.exe> tests/harness/run-dosbox.sh bench8old --fixed-timestep --include-extra ACSETUP-OFF-NATIVE.CFG:ACSETUP.CFG
--include-extra anim12.cfg:BENCH.CFG --env DOSAGS_SCENE=anim --env DOSAGS_TAS_AUTO_EXIT_TICK=1500 --screen-series DIR --series-every 1`
per binary (the executable must be named ags.exe: run-dosbox.sh places it at C:\ under its own name, and a name longer than 8.3
silently never starts, which cost one round here).
