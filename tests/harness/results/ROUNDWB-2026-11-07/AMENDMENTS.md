# Round WB -- amendments on review (sdlports 2026-11-07), before any data; they bind every WB cell
1. Practical outcome, information next to the primary: each cell reports whether its whole-run met 39.2 (the S32P / S8 whole-run
   margin is the operator's goal behind this line).
2. If the displayed falsifier trips (mean(WB) - mean(WT) lower than -0.3 points), the line STOPS there: write-behind is not adopted
   for any round, whatever the save saving.
3. This round only MEASURES write-behind. Any later round that adopts it for gate cells needs its own operator decision.
4. (sdlports / vcctrl review, recorded at 17:56Z, after power-on (17:55:41Z), and BEFORE the first write-behind cell WBB1; option B: the round
   runs as driven; these are traceability gaps, the hazard behaviour is unchanged.) Known logging gaps in this round's driver,
   verbatim: (a) no "WB cell lost" line on the wedge path (wedge_fetch); (b) no active-cell tag in powerguard.sh or the driver's
   poweroff(); (c) CHKDSK2 runs only inside WBA4.
5. Scoring rule: any wedge_fetch or STOP during a WB cell is scored as "WB cell lost mid-run, cache possibly unflushed", with the
   cell tag taken from SUMMARY.txt's "<TAG> start" lines.
6. CHKDSK-first rule: if the round stops before WBA4's CHKDSK2, the NEXT power-on's first step is "CHKDSK C: < NUL" before anything
   writes; any error goes to sdlports before any other work. All three of 4(a)-(c) are coded into the driver and powerguard before
   the next round.
7. (after attempt 1, before any WB data) Attempt 1 ran only the warm-up (attempt1/README.md: my need() budget error). The round is
   re-run under the same READMEs with: CAP_MIN 120 (not 115); need() at ~690 s per cell (first cell of each pair = the remaining
   pairs' total: 5520 / 4140 / 2760 / 1380; second cells 690); and amendment 4's three gaps CODED: an ACTIVE-CELL.txt marker
   (tag, wb=0/1) written around every cell and read by poweroff() and powerguard.sh, which then log "fired DURING cell ... -- WB
   cell lost mid-run, cache possibly unflushed"; the same line on the wedge path; CHKDSK C: as the warm-up's FIRST pre-line.
8. Budget line (sdlports; every round README from now on): need total at the first timed cell (WBA1) = 5520 s vs (CAP_MIN x 60 -
   warm-up - 240) = 7200 - 630 - 240 = 6330 s. Attempt 1's was 6080 vs 6900 - 630 - 240 = 6030 (did not fit).
