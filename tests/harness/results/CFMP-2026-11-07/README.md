# CFMP -- MMD in play on the clean INSTRUMENTED landed build, R1 by default: profile + LAB-L1's P3 (written 2026-11-07; pre-registration, before any data)
- Binary: CFINS.EXE = main 90083fe6 instrumented (ags 0001-0367), stamp 39c6e4b65079, build_dirty=0, 8,686,461 B, sha256 5650fff9...;
  byte-identical to the reviewed LAND2INS (cmp -l: 0 differing bytes). VOID if the staged stamp differs. BLASTER.TXT as CFREL.
- R1 witness (no env: R1 is the default): STDOUT "DOS-PORT guiclip DOSAGS_GUI_CLIP=(default) mode=2", RUNMANI guiclip_final mode=2,
  else VOID. latch_fullrestore= is a scored field in every cell: expected 0; any value > 0 is the guard's first natural firing (a finding).
- Fixture: GCMP's line verbatim without the env (fine timing on, DOSAGS_TICKLOG=12500, TICKS.BIN collected, TAS 12440).
  Reader: tests/harness/f1/f1prof.py as fixed in c457cda9 (groups by tick).
- P3 (docs/lab/L1-PREREG.md, 759de2b1; scored here per review): script_vm 11.0-13.2 ms/tick, central 12.1 (GCMP 12.11).
  Falsifier: outside 11.0-13.2.
- Information (bands, not claims): rb_sprite_time per drawn frame 3.6-4.6 ms (GCMP 4.12); displayed 72-78% (GCMP 75.25%,
  fine timing on); process_events_dispatch 13.0-14.8 ms/tick (GCMP 13.86).
- Witness: the camera sheet shows play.
- Round CF (R1 confirmation on the clean landed build; operator via sdlports: "a confirmation round on the clean release build"; S16/S32P/S8 gate cells + P9 fixture x2 + CFMP): WARMUPCF, CFS16, CFS32, CFS8, CFM1, CFM2, CFMP; one power-on, cap 100 min; dated 2026-11-07.
