# WARMUPWB -- warm-up + SMARTDRV syntax check + CHKDSK before (written 2026-11-07; pre-registration, before any data)
- Binary: l308.exe (bc9c3704a839), MMD title, TAS 1000; not scored. BLASTER.TXT must read "A220 I7 D3 P330 T3", else STOP.
- "SMARTDRV /? > SDHELP.TXT": must show "drive[+|-]", a "+ ... write-behind" line and a "/C ... write" line, else the round STOPS
  after the warm-up (no write-behind cell runs). "SMARTDRV /S > SDRV0.TXT" and "CHKDSK C: < NUL > CHKDSK1.TXT" recorded.
- Round WB (operator decision via sdlports 2026-11-07: SMARTDRV write-behind PER CELL in RUN.BAT, boot config untouched; a CONFIGURATION result, reported by the hub only as a setup note if it holds): WARMUPWB, WBA1 WBB1 WBB2 WBA2 WBA3 WBB3 WBB4 WBA4; one power-on, cap 115 min; dated 2026-11-07.
