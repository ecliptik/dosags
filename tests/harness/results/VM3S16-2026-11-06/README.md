# VM3S16 -- 5 Days S16 with the slice-3 fast VM on the release exe, the no-regression gate cell (F1b's deferred D3) (written 2026-11-06; pre-registration, before any data)
- Binary: VM3REL.EXE as E1 (stamp 1781fe2bf36c, build_dirty=1).
- Fixture: GR16R3's line verbatim (5days --startr 3, drive 2 = walk 25 2 90, ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG,
  direct framebuffer, TAS 5000, --no-fine-timing, fixed timestep, PGSB, MIN_WAIT 270, --timeout 1800, BLASTER line) + DOSAGS_VM=fast.
- Bar (PLAN-GATES, unchanged): both tick figures 39.2-40.8, fps_p50 >= 40, completeness >= 95%, camera clean, audio counters
  clean (overwrites 0, late_writes 0, silent_irqs 0 outside room loads); the campaign line 99% displayed.
- Prediction: as GR16R3 (39.29 / 40.12, 99.48%): whole-run 39.15-39.40, steady 40.0-40.3, displayed >= 99.3%. 5 Days runs ~44
  VM ops a tick (< 0.1 ms/tick saved); fast mode's decode adds ~0.1-0.15 s to game start and room 3's load (486 estimate).
- REGRESSION (fast disturbs something besides VM time): displayed < 99.0%, any audio counter non-zero, or a tick figure out of band.
- Witness: the camera sheet (512x384: the card cannot lock); BLASTER line. Lab worktree ~/git/dosags-lab-vm, patch vm-slice3.diff; docs/lab/VM-SLICE3.md. build_dirty=1: figures read from the manifests (gatebar VOIDs dirty).
- Round E (PLAN-FPS lever V slice 3): WARMUPE, VM3A1, VM3B1, VM3B2, VM3A2, VM3S16; one power-on, cap 85 min; dated 2026-11-06, else re-dated first.
