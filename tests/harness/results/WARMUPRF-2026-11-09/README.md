# WARMUPRF -- rig warm-up (written 2026-11-09; pre-registration, before any data)
- l308.exe (bc9c3704a839), MMD title, not scored. Checks: BLASTER.TXT = "A220 I7 D3 P330 T3" else STOP; capture device present;
  a capture STALE of any kind but "nolock" stops the round. DIRLIST.TXT: a read-only listing of C:\DOSAGS.
- Round RF (ags 0371's L1 to the 486, one power-on; per LAB-RB section 7 and the operator's 2026-11-08 decisions: L1 lands
  default off, its S16 / S32P paired cells are information against the 39.2 floor if the budget allows; L2 (0372) is NOT in
  this round, its ABBA follows this one, sdlports 2026-11-09): WARMUPRF, RFA1 RFB1 RFB2 RFA2, RFMP, RFP0 RFP1 (the S32P pair
  drops first); cap 110 min. Budget line: need at RFA1 3040 s; whole round after the warm-up 5340 s (3040 + RFMP 780 + 1520),
  vs CAP_MIN 110 x 60 - warm-up 630 - 240 = 5730 s. An S16 pair as well does not fit (6860 > 6330 s even at 120 min): a later
  round.
