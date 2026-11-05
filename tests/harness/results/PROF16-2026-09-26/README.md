# PROF16 -- 486 profile of the S16 fixture, round S (pre-registration, before any data)
- Registration: lab-s8's lab/mmd 68e5b414 `lab-mmd/prof16/README.md` (docs/lab/s8.md), verbatim in substance; P1/P2/VOID as there.
- Binary: build/lab/AGSPRF16.EXE (lab/mmd), staged as prof16.exe, sha256 b4407f1a9f62008bbbc2e06a8f1f2ee33edba1c37a80db0e1e59288155e0ee72,
  10,795,834 B, stamp 9ae27591b0c8 (main b02f0cc0 + ags 0317 + probe 0306 v8). A profiling cell, not a gate figure.
- cfg: presentation/trilbysnotes/ACSETUP-OFF-512X384-ROUND.CFG:ACSETUP.CFG (sha256 25c9c3d3..., [sound] enabled=0,
  digiid=-1, midiid=-1).
- Cell: run-hw 5days --tag PROF16 --timeout 1800 --no-fine-timing, SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1,
  DOSAGS_TAS_AUTO_EXIT_TICK=5000, DOSAGS_TICKLOG=5200, DOSAGS_PROF=1024, --startr 3, --collect TICKS.BIN --collect PROF.BIN;
  drive-walk 25 2 90; PGSB; RUNHW_MIN_WAIT_S=270.
- P1: click #6's longest loop-counter interval within ~1 s is >= 250 ms, with PATH < 50% and FILEIO >= 30% of its samples;
  none >= 250 ms after click #6 with sound off -> the stall is audio-coupled.
- P2: pooled over all click ticks, PATH < 50% of samples.
- Scorer (lab-s8, after the round): python3 lab-mmd/s8name.py --prof <dir> --exe build/lab/AGSPRF16.EXE --click 6 <dir>.
- VOID: stamp != 9ae27591b0c8; run-hw exit != 0; staged CWSDPMI.EXE sha256 != 2de899fe...; prof HARD STOP / REFUSED;
  no PROF.BIN or TICKS.BIN; any room other than 3; a "DOS audio device opened" line in STDOUT.
