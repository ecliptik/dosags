GCMP
# GCMP -- MMD IN PLAY, per-phase PROFILE on the R1 instrumented exe, R1 ON (written 2026-11-06; pre-registration, before any data)
- Binary: GCINS.EXE = lab R1INS (same diff and tree as GCREL; instrumented, stamp 5dc54892ad56, build_dirty=1), sha256
  f5089493...; VOID if it differs. A PROFILE cell: attribution, not a rate figure (fine timing costs ~0.7 ms/tick).
- Arm B (R1 on): SET DOSAGS_GUI_CLIP=2; STDOUT "DOS-PORT guiclip DOSAGS_GUI_CLIP=2 mode=2" and RUNMANI.LOG "guiclip_final
  mode=2" with skipped > 0, else VOID.
- Fixture: D8MP's line verbatim (P9M1's + fine timing, DOSAGS_TICKLOG=12500, --collect TICKS.BIN) + SET DOSAGS_GUI_CLIP=2.
  Reader: tests/harness/f1/f1prof.py GCMP-2026-11-06 [--lo/--hi per room], as D8MP.
- Question: does R1 remove the sprite cost on the 486 (mechanism, PLAN-FPS rule: confirm the KPI and the mechanism)?
- Prediction: rb_sprite_time per drawn frame 1.5-3.7 ms (D8MP: 2.659 ms x 3 = ~8.0); script_vm unchanged (12.4 +- 1.0 ms/tick).
  Falsifier: rb_sprite_time per drawn frame > 4.0 ms. Information: render_to_screen, scene, displayed vs D8MP.
- Witness: camera sheet shows play; exit 0; TICKS.BIN present, else VOID.
- Round GC (lever R1 to the 486; operator "Keep going to improve MMD fps"; sdlports: band as stated, S16 guard MET): WARMUPGC,
  GCS16, GCA1 GCB1 GCB2 GCA2, GCMP, GCAQA GCAQB; one power-on, cap 115 min; dated 2026-11-06.
