# P9S16 -- 5 Days S16 on the v0.1 exe: the start-up probe (written 2026-11-06; pre-registration, before any data)
- Binary: P9REL.EXE = build/ags-release/ags.exe = the v0.1 zip's AGS.EXE (release c754df64babd, sha256 d680e3b6..., tag v0.1);
  defaults (no VM/lever env): STDOUT "vmmode (default) mode=3" and "englev (default) on=1", BLASTER.TXT "A220 I7 D3 P330 T3", else VOID.
- Fixture: GR16's line verbatim (as N7S16 / V1S16). Scored as a gate cell (PLAN-GATES bar, unchanged) AND for preloop_ms.
- Question: V1's pre-loop start-up (926-1,004 ms) vs N7's (722-864 ms) on the identical exe. Two leads: (A) C:\DOSAGS entry
  growth (each cell adds files; P9 adds more), (B) off-time before relay-on (N7 ~2 h 45 m, V1 98 s; P9 ~1 h).
- Prediction (A): preloop >= 900 ms (no cleanup has happened). (B) would show preloop back in 722-864. Reported, not gated.
- Bar prediction: displayed 99.3-99.6%, steady 40.0-40.3; whole-run 39.10-39.30 (on the band edge, as V1).
- Witness: the camera sheet (512x384).
- Round P9 (post-v0.1 gameplay; operator 2026-11-06 "measure gameplay fps too", "Continue round"): WARMUPP9, P9S16, P9M1,
  P9M2, P9SD; one power-on, cap 85 min; dated 2026-11-06.
