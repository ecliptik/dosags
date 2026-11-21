# WARMUPRV -- round RV warm-up (written 2026-11-19; pre-registration, before any data). Not scored.
- WARMUPRT's line verbatim (l308.exe bc9c3704a839, mmd, ACSETUP-OFF-512X384-ROUND.CFG, TAS 1000, drive 0) + the BLASTER line.
- Added (information, read-only): RUN.BAT runs "DIR > PKGDIR.TXT" in the package dir just before AGS.EXE, collected as PKGDIR.TXT:
  the file count and bytes there, for round V1's start-up lead (every cell leaves its <TAG>.LOG in the package dir and DOS
  directory lookups are linear). Nothing is moved or deleted on the target.
- Stops the round on a BLASTER.TXT other than "A220 I7 D3 P330 T3", run-hw exit != 0, or no capture device afterwards.
- Round RV (the v0.1.1 gates): WARMUPRV, RVDST, RV16A, RV32A, RV8A, RV16B, RV32B, RV8B; one power-on, cap 120 min; dated 2026-11-19.
