# WBA2 -- 5 Days S32P line, write-through (as today), ABBA cell (written 2026-11-07; pre-registration, before any data)
- Binary: RCREL.EXE = main 9e54b6d9 release, stamp 4c9f83b62c5c, build_dirty=0, sha256 7deb7ca9...; VOID if the staged stamp differs.
  Fixture: GR32P's line verbatim (as SU32* / SW1*), + round SU's mechanism lines.
- Arm lines: last pre-lines "SMARTDRV C+" (WB) / "SMARTDRV C" (WT), then "SMARTDRV /S > SDRVON.TXT"; first post-lines, both arms,
  "SMARTDRV /C", "SMARTDRV C", "SMARTDRV /S > SDRVOFF.TXT" (before the SDL-log copy, MODE12 and every collect / reboot). SDRVON
  must show C: write cache yes (WB) / no (WT), else VOID; SDRVOFF must show "C: yes no", else the round STOPS.
- PRIMARY: paired d = WT - WB on restart_savegame_ms over (WBA1,WBB1) (WBB2,WBA2) (WBA3,WBB3) (WBB4,WBA4): median d >= 150 ms
  (central ~330, band 200-550); FALSIFIED if median d < 100. Basis: WT = ~210-260 ms + 0-2 card stalls of 220-310 (round RC trace);
  WB leaves ~100-150 ms of serialisation (LAB-SW). Lost pair: median of complete pairs, n stated; < 3 complete = VOID.
- REQUIRED: displayed mean(WB) - mean(WT) within +-0.3 points; FALSIFIED if WB lower by > 0.3 (the lazy flush moving card stalls
  into play). Whole-run / steady: information (WB expected +0.05-0.15 whole-run).
- SAFETY: CHKDSK C: (read-only, < NUL) before (WARMUPWB) and after (WBA4); any lost clusters / chains or cross-links STOP the line
  and go to sdlports / the operator. Exposure: a hard power cut inside a WB cell can lose cached writes.
- Amendments before data (ROUNDWB-2026-11-07/AMENDMENTS.md): whole-run vs 39.2 reported; a tripped displayed falsifier stops the line.
- Round WB (operator via sdlports 2026-11-07: SMARTDRV write-behind PER CELL in RUN.BAT, boot config untouched; a CONFIGURATION result, hub setup note only if it holds): WARMUPWB, WBA1 WBB1 WBB2 WBA2 WBA3 WBB3 WBB4 WBA4; one power-on, cap 115 min; dated 2026-11-07.
