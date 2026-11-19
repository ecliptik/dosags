# WARMUPRH -- rig warm-up (written 2026-11-11; pre-registration, before any data)
- l308.exe (bc9c3704a839), MMD title, not scored. Checks: BLASTER.TXT = "A220 I7 D3 P330 T3" else STOP; capture device present;
  a capture STALE of any kind but "nolock" stops the round. DIRLIST.TXT: a read-only listing of C:\DOSAGS.
- Round RH (operator 2026-11-11: the moving fixture MS3 -- LAB-MOVE addendum 3, lab-rb 600b90e8 / 7f1980bb -- is the
  campaign's new measure, its target set only after this baseline; 99% x2 on the P9M1 line is retired, not met; sdlports'
  shape: calibration first and gated, a P9M1 bridge pair, the MS3 baseline cells named): WARMUPRH, RHCAL [RHCAL2 only on
  a GATE RECENTRE], RHM1..RHM4, RHP1 RHP2, RHMP (first to drop). One power-on, cap 120 min. Budget line: need at RHCAL
  3800 s (CAL 760 + the MS3 block 3040); whole round after the warm-up 6100 s (760 + 3040 + 1520 + 780), 6860 s with
  RHCAL2, vs CAP_MIN 120 x 60 - warm-up 630 - 240 = 6330 s: with RHCAL2 the instrumented cell RHMP drops, by design.
  Cell length: MS3 and cal cells ~670-700 s on the rig, the same floor as a DRIVE 5 cell (DRIVE6-RIG-CHECKS.md).
  Harness: drive-walk6.sh / drive6-cal.py / drive6-gate.sh / cell-template-d6.sh on main (2432f136 + the gate helper).
