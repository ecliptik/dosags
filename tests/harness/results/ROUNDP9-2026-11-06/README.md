# Round P9 -- 2026-11-06: MMD IN PLAY is 67.6% displayed x2 (not 99.9%); 7 Days in play 99.50% MET; P9S16 99.52% MET

One power-on 17:10:40Z-18:05:31Z (driver exit 0; powerguard confirmed OFF 18:05:32Z), cap 18:35:40Z not reached. Operator to
vcctrl: "Continue round"; to this session: "measure gameplay fps too". Pre-registrations 3179ebbf. Binary p9rel.exe = the v0.1
exe (release c754df64babd); every cell exit 0, stamp OK, pre = staged = post; defaults witnessed (mode=3, on=1); BLASTER.TXT
"A220 I7 D3 P330 T3" in all five.

| Cell | what | steady | fps_p50 | displayed (1 - skipped/ticks) | witness | verdict |
|---|---|---|---|---|---|---|
| WARMUPP9 | l308 + DIR listings | 32.88 | -- | -- | nolock | C:\DOSAGS 716 entries (658 *.LOG), LOGS 215 |
| P9S16 | 5 Days S16 | 40.08 (whole 39.34) | 40.00 | 99.52% (24) | camera CLEAN | **MET**; preloop 796 ms |
| P9M1 | **MMD in play** (save 007, 17 host clicks) | 39.94 | **28.00** | **67.63%** (2,267 of 7,003) | camera: kids walk, room 1 -> 2 | **NOT MET** |
| P9M2 | **MMD in play** (as P9M1) | 39.90 | **27.92** | **67.58%** (2,270 of 7,003) | camera: as P9M1 | **NOT MET** |
| P9SD | 7 Days room 2 in play (62 engine-click walks) | 39.99 | 40.00 | 99.50% (25 of 5,007) | camera: cEgo walks | **MET** (F17DK 99.48%) |

- MMD in play (the first gameplay reading since the VM work): logic keeps time (steady 39.9) but the machine renders about two
  frames in three -- per-second renders/ticks room 1 62.2% / 60.8%, room 2 69.1% / 69.4% (character select N7M1: 100.0%).
  Room 2 skips even while the kid stands still (camera), so it is not only walking. Clicks: 17 seen of 17 (journey p50 18 ms,
  p95 316 ms). Long stalls: the restore (~2.0 s) and the room-2 entry (~3.8 s). Both cells agree to 0.05 points.
  Falsifier (< 95% in either = the levers do not carry into play): TRIPPED. The 99.90% figure is the idle character select only.
- 7 Days in play holds 99.5%: the shortfall is specific to MMD in play, not to gameplay in general.
- Start-up probe: P9S16 preloop 796 ms with C:\DOSAGS at 716+ entries -- the registered (A) prediction (>= 900) MISSED; V1's
  926-1,004 is not explained by directory size alone. D8 (rebuilt directory) is the direct test.
- Next: D8MP (pre-registered 88f3b724) profiles MMD in play on the instrumented exe: render/present vs script vs clicks.
- Rig (vcctrl): 1 corrupt capture frame (17:48:10.0Z, in P9M2), decode_errs 9 -> 11; no USB event, no recovery. 10 file jobs.

Files: SUMMARY.txt, driveP9.sh / cellP9.sh / powerguard.sh / daemongap.sh / expected.txt / ORDER-CONFIRMED, POWERGUARD.txt,
jobs/*.json, GATEBAR.txt (P9S16). Captures and saves stay local (AUDIO-SHA256.txt, SAVE-SHA256.txt).
