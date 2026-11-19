# ROUNDRQ-2026-11-13 -- round RQ results: the heap lock-policy ABBA on MS3 (ags 0380) -- every registered term SUPPORTED

Pre-registration: 2b9b8cc9 + 07dfa6c0 (pushed before any data; sdlports APPROVED). Operator's power-on OK asked directly
in the dosags session. One power-on: relay-on 18:20:13Z, power OFF 19:51:16Z (driver), confirmed by powerguard 19:51:17Z
and vcctrl's power.log 19:51:11Z (91 min, cap 120). Driver exit 0; RQCALQ GATE PASS with 0 px drift (RQCAL not run);
every ABBA cell ran; no STOP. Diagnostic only; MS3 target: not yet set (operator).

## The cells (tests/harness/rq-steps.py; every cell VALID: arm witness, clean exit, PAIR-OK, audio 0 / 0, stamp b66bd61cb1df)

| cell | arm | S17 | S18 | L2 (game ms) | W17 = L2 + S17 | j1 (game ms at press 1) | hook free -> exit free (pages; phys 8,192) | hook_us | cover / pageability |
|---|---|---|---|---|---|---|---|---|---|
| RQO1 | O | +360 | +153 | 1,836 | 2,196 | 34,025 | 5,137 -> 3,745 | 10 | - |
| RQU1 | U | +21 | -64 | 2,158 | 2,179 | 36,277 | 5,137 -> 4,055 | 13 | pageability ok |
| RQP1 | P | +7 | +11 | 1,291 | 1,298 | 33,066 | 5,137 -> 3,585 at the hook -> 3,585 | 58,765 | cover ok |
| RQP2 | P | +12 | -20 | 1,294 | 1,306 | 32,968 | 5,137 -> 3,585 at the hook -> 3,585 | 58,846 | cover ok |
| RQU2 | U | -23 | +40 | 2,155 | 2,132 | 35,705 | 5,137 -> 4,055 | 10 | pageability ok |
| RQO2 | O | +287 | +185 | 1,894 | 2,181 | 34,253 | 5,137 -> 3,745 | 10 | - |

Arm witnesses (heappolicy_exit): O flags 0x1080->0x1080; U unlock=1, 0x1080->0x80; P pregrow_kb=6144 grown=1, flags kept.
env_block_sha O eec4d5b41015 (= RO's F cells' default env hash), U a49d93fcc25a, P 1521171ad24e.

## Verdict, by the pre-registered letter (VERDICT.txt; baseline B = both in-round O cells: S18 +153 / +185, W17 2,196 / 2,181)

- **S18 UNLOCK: SUPPORTED** (-64 / +40 ms, both <= 60; baseline both >= 120). The press-18 step (the 192-page commit at
  room-2 entry) is gone.
- **S18 PREGROW: SUPPORTED** (+11 / -20 ms).
- **W17 PREGROW: SUPPORTED** (1,298 / 1,306 ms < 2,181 - 60): the room-2 entry's wall cost falls by ~890 ms.
- **(d) PAGEABILITY: not falsified** (U exit free pages 4,055 / 4,055 >= 512; the largest sustained +shift outside the
  steps in U cells +26 / +33 ms, as in O +33 / +27; no CWSDPMI.SWP before or after in any cell -- the O control the same).
- No U cell stopped or ended unclean: no UNLOCK FAILED.

## Information (not terms)

- **UNLOCK's prediction held** (stated, not a bar): S17 down (+360 / +287 -> +21 / -23), L2 up (1,836 / 1,894 -> 2,158 /
  2,155), W17 flat (2,179 / 2,132 vs B median 2,189; within +-60). UNLOCK moves the room-2 load's commit from lost clock to
  counted clock and saves no wall time there; PREGROW removes the commit from the load.
- **The room-1 board hold** (vcctrl's USB4VC watch: one mouse hold at ~+42 s from the lock, the room-1 128-page commit,
  in every earlier F / O cell and in RQCALQ): present in RQO1 / RQO2 (+41.9 / +41.9 s), absent in all four U and P cells.
  ABBA-consistent, no exceptions. Keyboard-side host counters identical across all six play cells.
- **PREGROW's startup cost.** hook_us 58,765 / 58,846 (uclock: a lower bound, blind to lost ticks). j1 (game ms at the
  wall-timed press 1): O 34,025 / 34,253; P 33,066 / 32,968 (~1.1 s fewer than O); U 36,277 / 35,705 (~1.85 s MORE than
  O). Reading (post-data, not registered): O already loses ~1.85 s of clock before press 1 to its room-1 locked commits
  (which U removes); P loses ~2.95 s against U, so the one 1,552-page commit at the hook stops the clock for about
  3 s -- above the predicted 1.5-2 s. It happens once per run, before the save restore and the first room.
- **Skipped frames** (RUNMANI frames_skipped, the same exit tick 12,440 in every cell): O 577 / 589, U 579 / 627, P 630 /
  620 (RO's F cells, memlog on: 521 / 556; L 723 / 725). The levers do not raise displayed frames on MS3: a clock that no
  longer stops keeps its ticks, and the fixed-timestep loop then skips more renders to keep up (game time is kept, not
  lost). Not attributed further; it is the operator's trade (game-time accuracy vs displayed frames), as for the pacer.
- Physical memory on the 486 as CWSDPMI reports it: 8,192 pages (32 MB); free 5,137 at the hook in every cell.
- Rig (vcctrl): USB4VC ev_in = pkt_ok +4,203 (81 + 6 x 687), 0 losses, resumes +3 (the three O-side holds), max_wait_ms
  2,407 unchanged; input log 1,191 rows, 0 flagged, 0 forced releases; launch blacks 2-3 frames at RUN.BAT +18-19 s in
  WARMUPRQ / RQCALQ / RQP1 / RQO2 and one reboot black after RQP2's pull, none mid-play; 0 USB kernel events.

## Decision and next steps (operator 2026-11-13, via sdlports, after verification)

- KEEP BOTH SWITCHES OFF; the defaults stay as they are; revisit only if room-load time becomes a goal. 0380 is removed
  whole by ags 0381 (an exact revert; both flavours byte-identical to 0379's builds; RM0380-2026-11-13).
- Open, if the lever is ever revisited:
  - UNLOCK: a real in-run pageability witness (an engine-side sample of physical free pages / paging during play) is owed
    before it could be proposed as a default; this round's exit free pages and shift readings suffice only for a
    diagnostic arm.
  - PREGROW: the size is per game (6,144 KB is MS3's growth after the hook; AGS Quest grew past it in the lab), and the
    one commit at the hook stops the clock ~3 s before play; a general form would need per-game sizing or a measured
    growth step, and a decision on that startup stop.
  - The skipped-frames trade: both levers keep game time that O loses, and MS3 renders it as more skipped frames (O 577 /
    589, U 579 / 627, P 630 / 620); game-time accuracy vs displayed frames is the operator's trade, as for the pacer.

## What this settles, and what it does not

- Both levers remove the post-0377 press-18 step on the 486; PREGROW also removes ~0.9 s from the room-2 entry. UNLOCK is
  not a default candidate until a real in-run pageability witness exists (pre-registered open item).
- PREGROW's 6,144 KB is MS3's size: a fixture that grows past it falls back to locked sbrk blocks (lab: AGS Quest did).
  Choosing a default (or neither) is the operator's call, after this round; 0380's switches stay off by default.
- Displayed frames do not improve on MS3 (above). MS3 target: not yet set.

Files: SUMMARY.txt, VERDICT.txt, POWERGUARD.txt, the driver copies (driveRQ.sh, cellRQ.sh, powerguard.sh, daemongap.sh,
expected.txt, ORDER-CONFIRMED). Per cell: STEPS.txt, PAIRING.txt, PLAY-RESULT.txt, RUNMANI.LOG, STDOUT.TXT, DRIVE-WALK.LOG,
ROOTPRE.TXT / ROOTPOST.TXT, AUDIO-SHA256.txt and SAVE-SHA256.txt (captures and saves stay local).
