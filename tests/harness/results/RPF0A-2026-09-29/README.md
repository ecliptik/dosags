# RPF0A -- RP486 cell 2 of 4 (RPF1A RPF0A RPF0B RPF1B), round W2 (pre-registration, before any data)
- Registration: lab-s8 lab/mmd 0b5aaeea lab-mmd/rp486/README.md "ROUND W AMENDMENT" (supersedes the earlier binary, cell and
  scorer lines); nothing added. Decides whether ags 0319 is deleted, reported, or goes to the landing gates.
- Arm: F0 = `--env DOSAGS_RP_FAST=0` (the killswitch).
- Binary: lab-s8's AGSRPW (lab/mmd build/lab/AGSRPW.EXE) staged as rpw.exe, sha256 45f641f0ce51760ad9cc2244631331f88e6a8c02e9ec8a61d639fae422269b80,
  8,673,112 B, stamp 55959f2577ca (build_dirty=1 expected) = landed main d533b56d + ags 0319 + RT3's route-hash probe with control.
- Fixture: round B's RTHB/RTHN recipe -- run-hw 5days --startr 3, --timeout 2400, --no-fine-timing, SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1,
  DOSAGS_TAS_AUTO_EXIT_TICK=1150, DOSAGS_RT_BENCH=@RTBENCH.TXT (RTBENCH.TXT sha256 05cab28e...), DOSAGS_RT_RAND=300,7, sound OFF
  cfg ACSETUP-OFF-512X384-ROUND.CFG:ACSETUP.CFG (sha256 25c9c3d3...), drive 0 (no clicks), PGSB, no RUNHW_MIN_WAIT_S.
- Scorer: lab-mmd/rp486/rp486.py at lab/mmd bdd54dc8: rp486.py 55959f2577ca <RPF1A> <RPF0A> <RPF0B> <RPF1B>.
- DELETE 0319: routes not identical across the four cells, or either pair's mean-request saving < 10%. LANDING GATES: >= 20% in
  both pairs. REPORT: 10-20% in both (weighed against +7,785 exe bytes).
- VOID: stamp != 55959f2577ca; exit != 0; room != 3; not exactly 339 routewhat rows; RUN.BAT's RP_FAST not the arm's; rpcache not
  fast=1 serial_hits>0 labels_ok=1 (F1) / fast=0 serial_hits=0 (F0); an audio device opened (sound OFF: no silent IRQs possible).
- Prediction: F1 >= 20% below F0 in both pairs (central ~30%).
