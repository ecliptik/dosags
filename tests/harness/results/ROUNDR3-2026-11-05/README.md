# Round R3 (the GR16 re-run R2 owed) -- 2026-11-05 result: GR16R3 MET, camera CLEAN -- S16 on the release flavour

One power-on: relay-on 21:00:01Z, power OFF 21:25:02Z (driver; powerguard confirmed), cap 21:35:01Z not reached.
Operator 2026-11-05, directly: "yes, start next run" (ORDER-CONFIRMED). Pre-registrations 3126b03b. Release a1dba5d61624,
pre-stage = staged = post-run.

| Cell | whole-run / steady | fps_p50 | completeness | audio counters | witness | verdict |
|---|---|---|---|---|---|---|
| WARMUPR3 (l308) | 29.91 / 33.02 | -- | -- | -- | camera: boot text + MMD title readable | not scored; close-watch passed |
| GR16R3 (S16) | 39.29 / 40.12 | 40.00 | 99.48% (26 skipped of 4,999); 100.24% presents | clean (pcm_irqs 818 = mixed 823 - inflight 5) | **camera CLEAN**: 5 Days room 3 on the LCD, character moves, no stuck or garbage regions | **MET x1** |

BLASTER.TXT "A220 I7 D3 P330 T3" in both cells. GATEBAR.txt (one cell given twice: its "x2" line means nothing; the
cell line is the reading). Comparison GL16A/B 39.29 / 40.13 and 39.29 / 40.10: whole-run equal, steady inside.
R2's GR16 (39.27 / 40.11, unwitnessed) agrees.

With R1 and R2: the release flavour now carries all three 486 gates -- S8 x2 (R1R1, R1R2) + CAPR8, S16 x1 (GR16R3),
S32P x1 (GR32P) -- and the WB arm at S16 (GR16WBR).

Rig: the capture stick stayed on USB (vcctrl: no kernel event, no auto-recovery) but logged 3 corrupt frames in ~17 min
(21:04:54Z in the warm-up, 21:15:18Z and 21:17:24Z in GR16R3) against R2's 1 in 67 min -- a warning sign (R1's dropout
followed corrupt frames). GR16R3's witness is the camera; the card cannot lock 512x384 (capture STALE "nolock").
vcctrld jobs in jobs/; no `settle` line.
Camera after exit (sdlports review): GR16R3's camera frames 16-28 (13:19:31 PST on) are black although the card saw text mode,
unlike frames 1-2 where the DOS text was readable -- most likely the LCD blanking or sleeping after the mode change. Outside the
scored window (the game ran ~13:17:30-13:19:25 PST, camera frames 4-15). For 512x384 cells the camera is the only witness, so
the LCD must be awake: each round's warm-up camera sheet is checked for that before its scored cells are read.
