# WARMUPR2 -- round R2 warm-up (written 2026-11-05; pre-registration, before any data). Not scored.
- WARMUPR1's line verbatim (l308.exe bc9c3704a839, mmd, ACSETUP-OFF-512X384-ROUND.CFG, TAS 1000, drive 0) + the BLASTER line.
- A BLASTER.TXT other than "A220 I7 D3 P330 T3" stops the round before any scored cell; a failed warm-up stops it and powers off.
- Close watch (operator 2026-11-05): the capture state and vcctrl's decode errors through the warm-up are read before the WB pair;
  capture STALE or a USB event in the warm-up stops the round before any scored cell (R1's early warning was corrupt frames at minute 15).
- Round R2: WARMUPR2, GR16WBP, GR16WBR, GR16, GR32P; one power-on, cap 75 min; dated 2026-11-05, else re-dated first.
