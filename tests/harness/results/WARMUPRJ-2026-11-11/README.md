# WARMUPRJ -- rig warm-up (written 2026-11-11; pre-registration, before any data)
- l308.exe (bc9c3704a839), MMD title, not scored. Checks: BLASTER.TXT = "A220 I7 D3 P330 T3" else STOP; capture device present;
  a capture STALE of any kind but "nolock" stops the round. DIRLIST.TXT: a read-only listing of C:\DOSAGS.
- Round RJ (round RI's registered shape, re-run: RI's calibration stopped on C10 -- small-packet linearity, a part of
  the pointer path the play presses never use -- while every play-path quantity passed directly; the amended C10 and
  the small-packet model were written after RI's data and reviewed by sdlports, so RI's calibration is NOT re-read: RJ
  opens with a fresh full cal under the amended rules, registered here before power-on; the short re-check (calq) is for
  the round after, with RJ's passing cal as its reference). Campaign context unchanged: MS3 (LAB-MOVE addendum 3) is the
  campaign's measure, its target set only after this baseline; P9M1's 99% x2 is retired, not met. WARMUPRJ, RJCAL [RJCAL2
  only on a GATE RECENTRE], RJM1..RJM4, RJP1 RJP2, RJMP (first to drop). One power-on, cap 120 min. Budget line as RI:
  need at RJCAL 3800 s; whole round after the warm-up 6100 s, 6860 s with RJCAL2, vs 6330 s: with RJCAL2, RJMP drops.
  Harness (local main 84ca3445, sdlports-reviewed): drive-walk6.sh (one-call press, pace 0.05, dwell 0.2, every packet
  15..127 counts; FIRST-PRESS.json / FAILED-PRESS-<n>.json kept), drive6-pointer.py (one move = one PS/2 packet capped at
  +-127; 3.0 / 1.5 px per count; packets <= 11 counts lose counts upstream of INT 33h), drive6-cal.py / drive6-gate.sh.
  Press-path stop rule (sdlports): a cal STOP for press-path reasons (G0 / G1 / the fast-probe merge) is never answered
  mid-round; any fallback to DRIVE6_PRESS=split is for a later round.
