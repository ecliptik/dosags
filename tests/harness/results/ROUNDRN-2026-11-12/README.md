# Round RN -- 2026-11-12: ags 0377 (bounded mixer voice ring) on the 486 -- NO VERDICT by the pre-registered letter: both fixed arms are GATE PLAY-VOID (113 journeys for 114 presses), because without the freezes the wall-timed press 114 lands after the TAS exit; post-data information: both fixed arms are flat (room-2 steps -4..+9 ms vs the legacy arms' 217-221 / 605-657 / 1,426-1,490 ms), memlog flat after room-2 entry +71 ticks, the board's +91 / +109 / +131 / +177 s holds absent; audio clean in all arms; RNDT VOID (the tool's RTC reads were clobbered on the rig); P9M1 RNP1 99.37%

One power-on: relay-on 15:38:06Z, power OFF 17:08:22Z (driver exit 0; driver-started powerguard confirmed OFF 17:08:31Z, no
"fired DURING cell" line), cap 17:38:06Z not reached; vcctrld daemon_start_t 1794467128.02 at round start and end (unchanged
since round RM). Operator, directly (question tool): "Power on now (Recommended)", after sdlports' review and approval of
5adf49c1 + 987ddce1 (ags 0377) and 45001f99 (this round's pre-registrations; pushed with the operator's OK) and vcctrl's
pre-check (15:13Z). Every cell exited 0 with stamp OK (rnrel 93df50d751a8 = main 987ddce1 release, ags 0001-0373 + 0376 + 0377;
l308 bc9c3704a839), pre = staged = post; expected.txt (rnrel, l308, AGSSAVE.007, DPMITIME.EXE) OK at round start;
BLASTER.TXT "A220 I7 D3 P330 T3"; firmware 0.5.109 (fw=OK in every cell). `capture=STALE` (nolock) on every MMD cell is the
usual one; the camera is the play witness (warm-up shot 15:39:10Z: clean boot to C:\>).
**DIAGNOSTIC ONLY: no cell is scored against a target or counts toward the proof pair. MS3 target: not yet set (operator).**

| Cell | what | result |
|---|---|---|
| WARMUPRN | warm-up | exit 0; BLASTER ok (8.6 min) |
| RNCALQ | short re-check against RJCAL | **GATE PASS**, drift 0 px on every point (DXL 60, DXA 190, DXB 289, y 120) |
| RNCAL | full cal, only on a calq miss | not run |
| RNF1 | MS3, arm F (0377 default), memlog | **GATE PLAY-VOID** (113 walk targets / journeys for 114 presses); witness F OK; 91.48% (597) |
| RNL1 | MS3, arm L (DOSAGS_RING_LEGACY=1), memlog | PLAY-OK; witness L OK; 89.53% (733) |
| RNL2 | MS3, arm L, memlog | PLAY-OK; witness L OK; 89.72% (720) |
| RNF2 | MS3, arm F, memlog | **GATE PLAY-VOID** (113 for 114); witness F OK; 92.55% (522) |
| RNDT | DPMITIME (information) | ran, 8 files of 14 lines, rc=0, host flags as registered; **VOID**: every file fails the null-phase validity rule |
| RNP1 | P9M1 bridge on RNREL (0377 on), DRIVE 5, memlog off | 99.37% (44 of 7,003); no partial, no mouse.dropped -> counts |

Arm witnesses (voicering line): F legacy=0, compactions 38 / 39, moved 1,085,952 / 1,114,112 B, cap_max 128,000 (the lab's
R7-C1 read 38 / 1,085,952 / 128,000); L legacy=1, compactions 0, cap_max 4,037,632 (the lab's figure). env_block_sha
eec4d5b41015 in both F, 987d6065efbd in both L (the rule holds). Clean finish in all four (RUNMANIFEST exit_code=0, "*****
ENGINE HAS SHUTDOWN"); memlog 173 samples, dropped 0. **Audio (the F arms' hard bar): underruns 0 / overwrites 0 in all
four arms** (silent_irqs 0 in all four).

## The verdict: none by the letter (pre-registered terms, RNF1-2026-11-12/README.md)
The pre-registration reads a PLAY-VOID cell's steps only if journeys and presses pair 114 / 114. Both F arms logged 113
journeys for 114 presses, so neither F arm is readable and the prediction ("both F arms read gone") has no reading; the
falsifier did not fire either. sdlports checked this against the raw records with an independent parser.

**Why both F arms lost press 114 (post-data, sdlports-verified):** the presses are wall-timed and the run ends at game tick
12440 (DOSAGS_TAS_AUTO_EXIT_TICK, P9M1's line). In the legacy arms the engine clock stands still ~2.3 s in the freezes, so
the last press lands ~2.3 s earlier in game time, before the exit. Without the freezes it lands after the loop has stopped:

| cell | press 114 at game time (down_at minus presses 95-113's median offset) | last journey | last persec ms (tick) |
|---|---|---|---|
| RNF1 | 198.73 s | 197.49 s (press 113) | 197,307 (12,419) |
| RNF2 | 198.46 s | 197.35 s | 197,204 (12,413) |
| RNL1 | 195.23 s | 195.25 s (press 114) | 197,443 (12,406) |
| RNL2 | 194.63 s | 194.64 s | 197,847 (12,428) |

Presses 1-113 pair 1:1 in both F arms (no out-of-step press). RNF1's press 114 also sat under a 2,407 ms board hold at
the engine's exit (vcctrl, below); RNF2's had none, and lost its journey the same way. So this is a property of the MS3
fixture with the freezes gone, not of a cell: every MS3 cell on a fixed binary will lose press 114 to the 12440 exit until
the fixture changes (sdlports). Options are with the operator (see "Next").

## Post-data information: what the F arms show (move, lab-rb d0874d3f move-lab/rj/rn, read on copies)
Level method as registered (clocksteps-release.py rule), F truncated to presses 1-113 (last stretch 95-113) -- a labelled
post-data variant (clocksteps-rn.py); L read in full. The quick script in this dir (quicklevels.py) gives the same numbers and
reproduces RMA1's registered 214 / 657 / 1,486 ms.

| cell | arm | journeys / presses | +830 | +1,730 | +3,540 | largest per-press change, presses 21-113/114 |
|---|---|---|---|---|---|---|
| RNF1 | F | 113 / 114 | -4 ms | +2 ms | 0 ms | -73..+64 ms |
| RNL1 | L | 114 / 114 | +217 ms | +605 ms | +1,490 ms | 34/35 +225, 53 +735, 91-94 up to +509 |
| RNL2 | L | 114 / 114 | +221 ms | +657 ms | +1,426 ms | 34/35 +267, 53 +672, 91-94 up to +509 |
| RNF2 | F | 113 / 114 | 0 ms | +9 ms | +4 ms | -73..+64 ms |

- Both L arms keep both steps (>= 500 / >= 1,000 ms) at RL / RM's sizes: the control is valid.
- Both F arms read flat to the method's +-30 ms at all three steps, and no per-press change >= 150 ms anywhere in presses
  21-113. Had the pre-registered rule been satisfied, both would read "gone". This is information, not the verdict.
- Memlog (aligned through lc): L1 / L2 show the full rig sequence -128, -32, -768, -192 (+36..+72), -192 (+110..+152), -192
  (+798..+882), -512 (+1,690..+1,732), -992 (+3,509..+3,548), min free 1,889 pages. F1 / F2 show -128, -32, -768, -192
  (+36..+71) and then nothing to the end: min free 3,777 pages (14.8 MB vs 7.4 MB). The second early 192 (RM's +91 s hold)
  was the ring too; the room-1 -128 / -32 are not, as in the lab.
- Board holds (vcctrl; offsets from each cell's lock, at the board poll that saw the resume):

| cell | ev_in | holds |
|---|---|---|
| RNCALQ | +81 | +42.9 |
| RNF1 | +687 | +43.8; +206.5 at the engine's exit (2,407 ms, press 114's tail; the new max_wait_ms) |
| RNL1 | +687 | +42.4, +91.6, +108.7, +130.9, +178.2 |
| RNL2 | +687 | +42.4, +91.6, +109.8, +132.0, +177.3 |
| RNF2 | +687 | +43.4 |
| RNP1 | +94 | +94.0 (in the click at +92.8 s) |

  F arms: no resume at +91 / +109 / +131 / +177 s; L arms: all four plus +42. A hold needs a packet in flight, so an absent
  hold is "no stall the board could see", not proof of none (vcctrl).

## Displayed % (information; not a target reading)
F 91.48 / 92.55%, L 89.53 / 89.72%: pair gains +1.94 (F1 - L1) and +2.83 points (F2 - L2). Beside RLM1-4's 90.68% (SD 0.89)
and RM's 89.65-90.50%. The lab bound pre-registered as information (+0.24..+0.55, expectation 0 to +0.5) is exceeded.
Where it comes from (move, RN-WINDOWS.txt: skipped frames per window, F against ten legacy cells RNL1-2, RMA1-2, RMB1-2,
RLM1-4):

| window | legacy mean +- SD | F1 / F2 | F - legacy |
|---|---|---|---|
| room 1 | 162 +- 16 | 130 / 134 | -30 (-1.9 SD) |
| room 2, 0..790 | 90 +- 14 | 74 / 68 | -19 (-1.3) |
| +830 window | 30 +- 6 | 19 / 19 | -11 (-1.8) |
| 990..1690 | 73 +- 11 | 70 / 59 | -8 (-0.7) |
| +1,730 window | 29 +- 11 | 16 / 18 | -12 (-1.1) |
| 1890..3490 | 168 +- 27 | 157 / 122 | -28 (-1.0) |
| +3,540 window | 47 +- 4 | 28 / 20 | -23 (-5.7) |
| 3760..end | 81 +- 17 | 92 / 73 | +1 (+0.1) |
| total | 679 +- 50 | 586 / 513 | -130 (-2.6) |

- With a mechanism: the three step windows return ~46 skips per cell against the ten-cell legacy mean (+0.65 points), 64
  against RN's own L arms (+0.92); +3,540 alone is -5.7 SD. A little above the RL / RM-based bound because RN's L arms carried
  more excess there; consistent with it.
- Without a mechanism: the other ~84 skips (~1.2 points) are spread over every window at -0.1..-1.9 SD, room 1 included,
  where the arms commit the same pages and play the same ring bytes. RNL1 / RNL2 are the top two of the ten legacy cells and
  RNF2 is below all ten, while RNF1 sits inside the legacy range (RLM3 92.00%). On two F cells this is not attributable to
  0377: it needs replication before any claim.

## RNDT: VOID (the tool, not the question)
All 8 files ran (14 lines, rc=0) under the registered host: DPA flags 0x5 (bit 2 set), DPB flags 0x1 (bit 2 clear), each
B process after its own `CWSDPMI -s-`. Every file fails the pre-registered validity rule (null phases must read rtc_ms 1000
and |lost_ms| <= 55 ms): rtc_ms read 0, 43,200,000, -28,799,000, 140,340,000 and the like, and the windows' uclock lengths
were 55-750 ms instead of ~1 s. No prediction is read.
- Diagnosis (move, RNDT-DIAG.txt): the deltas keep a correct seconds part while minutes / hours jump, and 58 of 96 window
  lengths sit within 3 ms of a whole BIOS tick. DPMITIME v1 read ports 70h / 71h with interrupts on; on the 486 the IRQ0
  path (reflected through CWSDPMI / VCPI to the real-mode BIOS chain) leaves the CMOS index at register 0, so a minutes /
  hours read straddling an IRQ0 returned the seconds value. DOSBox-X's BIOS does not, so the lab passed. SDL patch 0260's own
  comment says the same: interrupts off around every port 70h use.
- Information that does not use the RTC: the touch's call_ms (uclock inside the call) was the same in reps 1-3 and in A and
  B: 2.6 / 20.3 / 72.2 / 198.3 ms (A), 2.6 / 19.5 / 70.0 / 192.3 ms (B) for 32 / 192 / 512 / 992 pages, 0.08-0.20 ms per page
  and rising with N. A first touch from a fresh process costs ~0.2 s for 992 pages with IRQ0 serviced between page faults
  (call_ms is blind only to a single interrupts-off stretch > 55 ms); that is ~1/7 of the engine's 1.49 s step. Not a
  verdict on the commit question: the per-page cost may grow with pages already committed (the engine has ~5,300-6,300 in
  use), or the engine's commit may go through another host path.
- move has built a fixed tool (lab only): DPMITIM2.EXE (dpmitime2.c, sha256 afeff82ededf1731...), interrupts off around every
  70h / 71h pair, a time taken only from two identical full reads, rtc_ok on every line, and a -b K ballast to test the
  growth reading. Any rig use is a later round, the operator's call.

## Bridge: P9M1 RNP1 99.37% (counts by the board-counter rule)
| Cell | displayed | room 1 + entry | room 2 | late | audio | in-play partials / mouse.dropped |
|---|---|---|---|---|---|---|
| RNP1 | 99.37% (44) | 35 | 1 | 0 | underruns 0 / overwrites 0 (silent_irqs 42; RMP1 41, RLP1 46) | 0 / 0 |

Inside the registered 98.6-99.4%; the binary now carries 0377 (RLP1 99.11%, RMP1 98.96%). One cell, information.

## USB4VC 0.5.109 and the rig (vcctrl)
- ev_in +2,923 = pkt_built = pkt_ok over the round (= RM's); pkt_partial, pkt_timeout, pkt_inhibit, ev_buf_full,
  ev_discarded, edge_merged, host_fe, superseded, abandon_budget all 0; zero mouse.dropped rows; no input-log errors.
  Resumes 15 (58 -> 73) = partial_waits; max_wait_ms 1,535 -> 2,407 (RNF1's exit-time hold).
- RNDT: no mouse input; ev_in +0, host_ff 0 (DPMITIME and `CWSDPMI -s-` did not reset the mouse).
- Capture: 6 black corrupt-frame events (13 decode errors): launches (RNCALQ, RNL1, RNL2, ~+20 s after the lock), staging
  reboots (before RNL2 and RNP1), and one at RNDT +62 s inside the DPMITIME phase (not placed: DPMITIME prints no wall time).
  Zero USB disconnects or resets.
- New since 2026-11-12: services' Home Assistant reads the target's smart plug once a minute and can switch it. It did not
  switch it during RN: the only power actions in power.log are the round's own on and off.

## Next (for the operator; nothing here is decided)
- **The MS3 fixture with the freezes gone.** Every fixed-binary MS3 cell will lose press 114 to the 12440 exit. Two
  options (sdlports and the coordinator): (1) raise DOSAGS_TAS_AUTO_EXIT_TICK (e.g. 12600, ~4 s past press 114) -- cleaner,
  but it moves MS3's denominator, so that round must re-baseline (sdlports prefers an F / L ABBA there: L is both the control
  and the new baseline); (2) keep 12440 and pre-register a pairing rule that admits 113 journeys only when the missing one is
  press 114 and its game time lies after the last persec -- keeps RLM1-4's 90.68% comparable, at the cost of a more complex
  rule and a 19-press last stretch.
- **A verdict for 0377** then needs a pre-registered round under the chosen fixture.
- **Removals owed:** 0376 (memlog) and 0377's DOSAGS_RING_LEGACY switch, after that verdict.
- **0377 is release-relevant** (any long or looping PCM voice on a live SB leaked ~22 KB/s on the v0.1 line); before it
  reaches a release, one harness audio check of the fixed default on a lockable mode (sdlports). Any v0.1.x is the
  operator's call.
- DPMITIM2 (the commit-cost question) is optional, a later round.

Files: SUMMARY.txt, driveRN.sh / cellRN.sh / powerguard.sh / daemongap.sh / expected.txt / ORDER-CONFIRMED, POWERGUARD.txt,
WINDOWS.txt (rescore windows), quicklevels.py; each cell's RUNMANI.LOG (memlog rows, voicering line), DRIVE-WALK.LOG, GATE /
PLAY-RESULT / FIRST-PRESS.json (RNCALQ's RECHECK-RESULT), BOARD-TAKE / BOARD-RELEASE.json, INPUT-LOG.jsonl; RNDT's
DPA*.TXT / DPB*.TXT and dpmitime.c. Captures and saves stay local (AUDIO-SHA256.txt, SAVE-SHA256.txt).
