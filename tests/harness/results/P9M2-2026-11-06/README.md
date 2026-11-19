# P9M2 -- Maniac Mansion Deluxe IN PLAY on the v0.1 exe, cell 2 of 2 (written 2026-11-06; pre-registration, before any data)
- Binary: P9REL.EXE = build/ags-release/ags.exe = the v0.1 zip's AGS.EXE (release c754df64babd, sha256 d680e3b6..., tag v0.1);
  defaults (no VM/lever env): STDOUT "vmmode (default) mode=3" and "englev (default) on=1", BLASTER.TXT "A220 I7 D3 P330 T3", else VOID.
- Fixture: PLAYQ1's line (round Q) with sound ON: AGSSAVE.007 (sha256 f486d0e9...) restores in room 1 in front of the mansion;
  host held clicks (DRIVE 5: drive-walk.sh 40 8 30, real PS/2 presses) walk the kids; TAS 12440 (absolute; ~7,000 played ticks).
  Room changes are play, not a void (PLAYQ's rule dropped). Engine clicks can't play MMD (verb bar; build/ws/gameplay-prep).
- Score: displayed = 1 - frames_skipped/ticks over the played ticks, tick_rate_steady, fps_p50, rooms visited, walk clicks seen
  (drive-align.py), stall list (click / room-entry hitches). Whole-run is a restore artefact (as F17DK) and is not scored.
- Basis: room 1's per-tick script = the character select's (LAB-MMD 5.2); N7M 99.90%. Extra: click pathfinding, room fades.
- Prediction: steady 39.9-40.1; displayed 97.0-99.7% (central 99.0%): ~25 clicks x 2-5 frames + any room entry.
- MET (campaign line): both cells >= 99.0% displayed, steady 39.2-40.8. NOT MET otherwise; < 95% in either = the levers do not
  carry into play (falsifier). Information either way: per-click hitch on the shipped exe.
- Witness: the camera sheet must show play (kids moving in room 1 or beyond), else VOID (not "in play").
- Round P9 (post-v0.1 gameplay; operator 2026-11-06 "measure gameplay fps too", "Continue round"): WARMUPP9, P9S16, P9M1,
  P9M2, P9SD; one power-on, cap 85 min; dated 2026-11-06.
