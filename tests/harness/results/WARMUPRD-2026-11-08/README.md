# WARMUPRD -- rig warm-up (written 2026-11-08; pre-registration, before any data)
- Binary: l308.exe (bc9c3704a839), MMD title, TAS 1000; not scored. BLASTER.TXT must read "A220 I7 D3 P330 T3", else the round
  STOPS; capture STALE (other than nolock) or no capture device STOPS. DIRLIST.TXT read-only listing.
- Round RD (R2 = ags 0369, DOSAGS_CHAR_REUSE=2 on the R3 default, vs R3-only, to the 486, one power-on; sdlports' design 2026-11-08, LAB-R2B section 7): WARMUPRD, RDA1 RDB1 RDB2 RDA2, RDMP, RDS16 (first to drop); cap 100 min; dated 2026-11-08.
  Budget line: need at RDA1 (the ABBA block) 3040 s, whole round after the warm-up 4580 s (3040 + RDMP 780 + RDS16 760), vs
  CAP_MIN 100 x 60 - warm-up 630 - 240 = 5130 s available.
