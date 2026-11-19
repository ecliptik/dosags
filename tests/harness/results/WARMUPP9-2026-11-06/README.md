# WARMUPP9 -- round P9 warm-up + read-only directory listing (written 2026-11-06; pre-registration, before any data). Not scored.
- WARMUPN7's line verbatim (l308.exe bc9c3704a839, mmd, ACSETUP-OFF-512X384-ROUND.CFG, TAS 1000, drive 0) + the BLASTER line
  + RUN.BAT pre-lines `DIR C:\DOSAGS /A /B > DIRLIST.TXT` and `DIR C:\DOSAGS\LOGS /A /B > DIRLOGS.TXT` (collected; read-only).
- Question (start-up variance, PLAN-NEXT 5a item 2): how many entries do C:\DOSAGS and its LOGS hold? Prediction: hundreds of
  per-cell <TAG>.LOG / <TAG5>SDL.LOG files (run-hw.sh never deletes there). Fewer than 100 entries in C:\DOSAGS falsifies the lead.
- Stops the round on a BLASTER.TXT other than "A220 I7 D3 P330 T3", run-hw exit != 0, or no capture device afterwards.
- Round P9 (post-v0.1 gameplay; operator 2026-11-06 "measure gameplay fps too", "Continue round"): WARMUPP9, P9S16, P9M1,
  P9M2, P9SD; one power-on, cap 85 min; dated 2026-11-06.
