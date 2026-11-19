# SU8B2 -- Trilby's Notes S8, arm B (CFREL), start-up ABBA (written 2026-11-07; pre-registration, before any data)
- Binary: CFREL.EXE = main 90083fe6 release, stamp 54d439f88378 (sha256 7770f865...; = round CF's); VOID if the staged stamp differs.
- Fixture: R1R1's S8 line verbatim (as D8S8 / CFS8) + the mechanism pre/post lines. Witness: the camera sheet (room 35 is dark).
- Scored (all 8 cells): restart_savegame_ms and preloop_ms (STDOUT / RUNMANI), every *_init_ms line, whole-run / steady (gatebar,
  information here), and the mechanism fields: SVPRE.TXT (AGSSAVE.999 exists? size; drive bytes free), DIRLIST.TXT (C:\DOSAGS entry
  count), SDRV.TXT (SMARTDRV /S), SVPOST.TXT (size after). Logs are NOT cleared before or during the round.
- H0 (the build does not regress start-up): paired d = CFREL - adjacent v0.1 restart_savegame_ms over the 4 pairs (SU32A1,SU32B1),
  (SU32B2,SU32A2), (SU8A1,SU8B1), (SU8B2,SU8A2). H0 holds if |mean d| <= 100 ms and d is not the same sign in all 4 pairs.
  FALSIFIER: CFREL slower in all 4 pairs AND mean d > 100 ms (then 0366/0367 regress the restart-point save; look at its path).
- Information: init-phase paired differences (expected within +-30 ms); the 8-cell spread of restart_savegame_ms (expected >= 100 ms,
  not sorted by binary); whether free bytes / file size track it better than the binary does. Known confound: SU32A1 and SU8A1 (both
  v0.1) are the first cells after a different game wrote AGSSAVE.999 (size changes; SVPRE shows it). SMARTDRV is write-through on C:
  (g2k README); C: is a CF card.
- Round SU (start-up ABBA after round CF's S32P / S8 whole-run misses; sdlports' design 2026-11-07): WARMUPSU; S32P block SU32A1 SU32B1 SU32B2 SU32A2; S8 block SU8A1 SU8B1 SU8B2 SU8A2; one power-on, cap 120 min; dated 2026-11-07.
