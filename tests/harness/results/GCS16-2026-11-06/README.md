GCS16
# GCS16 -- 5 Days S16 on the R1 lab exe WITH R1 ON: the S16 regression guard (written 2026-11-06; pre-registration, before any data)
- Binary: GCREL.EXE = lab R1REL (lab-play.diff on the 0365 head; release, stamp f81265edd05e, build_dirty=1: lab, not shipped),
  sha256 50b02ec9..., 8,653,691 B; VOID if it differs. BLASTER.TXT "A220 I7 D3 P330 T3", STDOUT vmmode mode=3 / englev on=1.
- Arm B (R1 on): SET DOSAGS_GUI_CLIP=2; STDOUT "DOS-PORT guiclip DOSAGS_GUI_CLIP=2 mode=2" and RUNMANI.LOG "guiclip_final
  mode=2" with skipped > 0, else VOID.
  Exception: R1 never engages on 5 Days room 3 (lab: its 320x200 picture sits in a 320x240 virtual screen, every flagged GUI
  fails 0170's same-space check), so here guiclip_final must show flagged > 0 and skipped = 0 (skipped > 0 is a finding).
- Fixture: GR16's line verbatim (as P9S16 / D8S16) + SET DOSAGS_GUI_CLIP=2. Scored as a gate cell (PLAN-GATES bar, unchanged).
- Prediction: MET -- displayed 99.3-99.6%, steady 40.0-40.3 (P9S16 99.52% / 40.08, D8S16). The guard: NOT MET = R1's binary
  regresses S16, and R1 does not land as built. It guards the binary, not R1's skip (which has no power on this scene).
- Witness: the camera sheet (512x384).
- Round GC (lever R1 to the 486; operator "Keep going to improve MMD fps"; sdlports: band as stated, S16 guard MET): WARMUPGC,
  GCS16, GCA1 GCB1 GCB2 GCA2, GCMP, GCAQA GCAQB; one power-on, cap 115 min; dated 2026-11-06.
