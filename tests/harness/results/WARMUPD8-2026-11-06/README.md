# WARMUPD8 -- round D8 warm-up + read-only listings of the REBUILT C:\DOSAGS (written 2026-11-06; pre-registration, AMENDED before any data). Not scored.
- AMENDMENT (sdlports, before data): FAT directories never shrink -- a MOVE only marks slots deleted (0xE5) and lookups still walk
  every slot to the end marker, so a move-only arm would test nothing. Instead vcctrl rebuilds the directory at the DOS prompt
  before this round (its own window, step by step, nothing deleted): MOVE C:\DOSAGS\*.LOG and LOGS\*.LOG to C:\OLDLOG (+\LOGS);
  MD C:\DOSAGSN (+\LOGS); MOVE the remaining C:\DOSAGS files into C:\DOSAGSN; rename C:\DOSAGS -> C:\DOSAGSO, C:\DOSAGSN -> C:\DOSAGS.
- Line: WARMUPP9's (l308.exe bc9c3704a839, mmd, OFF cfg, TAS 1000, drive 0) + the BLASTER line + read-only DIR listings of
  C:\DOSAGS, its LOGS, C:\OLDLOG and C:\DOSAGSO (collected).
- Before (WARMUPP9): C:\DOSAGS 716 entries (658 *.LOG), LOGS 215. Expected: C:\DOSAGS ~60 entries in a fresh directory.
  VOID (the round's question unanswered) if C:\DOSAGS holds > 100 entries or the rebuild did not happen.
- Stops the round on a BLASTER.TXT other than "A220 I7 D3 P330 T3", run-hw exit != 0, or no capture device afterwards.
- Round D8 (operator 2026-11-06 "Ok" to moving the collected logs): WARMUPD8, D8S16, D8S32, D8S8, D8MP; one power-on, cap 85 min (D8MP added before data); dated 2026-11-06.
