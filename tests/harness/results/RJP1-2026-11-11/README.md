# RJP1 -- MMD IN PLAY (P9M1 line, DRIVE 5) on ags 0372's release, default config: the bridge pair (written 2026-11-11; pre-registration, before any data)
- Binary: RJREL.EXE = main release (ags 0001-0372), stamp 8c123c770d0b, build_dirty=0, sha256 5af21f2a...; = round RG's
  RGREL (R2 on by default; L1 / L2 off by default). VOID if the staged stamp differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  ...=(default) mode=0", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup line is
  missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Fixture: P9M1's line verbatim (as RGA1 / RGA2: DRIVE 5 host clicks, AGSSAVE.007, TAS 12440, sound ON cfg). Witness:
  camera shows play (room 1 -> 2). Windows as ROUNDRD's rule (room 1 + entry 5480-8400, room 2 8400-9500, late).
- Purpose (sdlports): ties MS3's new line to every earlier round on the same day and build, and shows the day's drift.
  Information, not a campaign claim (P9M1 99% x2 is retired). Expected level: the same binary's default cells in rounds
  RF / RG / RH read 98.80-98.94% (RI's two cells were drop-affected, information only) (RE's 0370 build 98.97-99.06%); a pair outside 98.5-99.3% is reported as day drift.
- Timing note (sdlports): the bridge runs ~65-75 min after the warm-up (~10-25 min if the MS3 block does not run).
  A cell whose game log shows a different GUI-click count from RH's 13 for the same presses (a DRIVE 5 mouse drop) is
  information only.
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
