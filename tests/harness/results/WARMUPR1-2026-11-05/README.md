# WARMUPR1 -- round R1 warm-up (written 2026-11-05; pre-registration, before any data). Not scored.
- WARMUPBT's line verbatim (build/ws/roundBATCH/driveBATCH.sh (a)): l308.exe (stamp bc9c3704a839, sha256 425c1609f50ac62c...), mmd,
  ACSETUP-OFF-512X384-ROUND.CFG, SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1, DOSAGS_TAS_AUTO_EXIT_TICK=1000, fine timing on, drive 0, --timeout
  1500; plus the BLASTER line (the round's first boot-profile read, before any gate cell).
- Reads: boot, staging and fetch through vcctrld 8e291c4's settle (the R1 result attaches every send/fetch job log and its `settle`
  warnings; the screen witness is checked for truncated commands); capture lock, camera, USB4VC counters (snapshots.py, fw 0.5.107 = vcctrl
  board 11-05); Caps Lock state (vcctrl: comes up ON from cold; reported).
- Witness: BLASTER.TXT (RUN.BAT `ECHO %BLASTER% > BLASTER.TXT` before AGS.EXE, --collect) stripped must read "A220 I7 D3 P330 T3"
  (profiles/dosags.yaml profile_witness, PGSB), else the round STOPS before any gate cell. Camera sheet reviewed before scoring; capture
  STALE is reported, not VOID (vcctrl 11-05: the stick dropped out 11-04 18:23-18:37 PST, target off).
- A failed warm-up (run-hw exit != 0) stops the round and powers off, as in round BATCH.
- Round R1: WARMUPR1, R1I1, R1R1, R1R2, R1I2, CAPR8; one power-on, cap 80 min; dated 2026-11-05, else re-dated first.
