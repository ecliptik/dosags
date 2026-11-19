# ROF2 -- MS3 ring ABBA, arm F: the bounded ring (0377's default), DOSAGS_MEMLOG=1 (written 2026-11-12; pre-registration, before any data)
- Binary: RNREL.EXE, round RN's binary unchanged = main 987ddce1 release (ags 0001-0373 + 0376 + 0377; sdlports-reviewed),
  stamp 93df50d751a8, build_dirty=0, sha256 ce8d275f.... 0377 bounds the mixer's per-voice ring (patch 0049's
  Voice::ring: the consumed prefix is dropped once it reaches 64 KB) and is ON by default; its TEMPORARY
  DOSAGS_RING_LEGACY=1 switch restores the old unbounded growth (removal owed after this round's verdict, with 0376).
  VOID if the staged stamp differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  DOSAGS_GUI_CTRL_MARK=(default) mode=1", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup
  line is missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Play line: P9M1's verbatim (AGSSAVE.007 f486d0e9..., ACSETUP-ON-512X384-ROUND.CFG, --no-fine-timing, TAS exit 12440).
- MS3: DRIVE 6, DRIVE6_MODE=ms, one-call presses, the values from ROCALQ (or ROCAL); 114 presses. Runs only after a
  calibration GATE PASS.
- The question: is ags 0377 the fix for the 486's room-2 freezes? Rounds RL / RM: the 486 freezes machine-wide (IRQ0
  unserviced) ~0.2 / ~0.65 / ~1.5 s in the room-2 stay, each at a DPMI physical-page commit (192 / 512 / 992 pages). The
  lab (move) named the owner: patch 0049's per-voice ring grows ~22 KB/s on a live SB with 2x reallocations. Round RN ran
  this ABBA and gave NO VERDICT by its letter: with the freezes gone, the wall-timed press 114 lands after the 12440 TAS
  exit, so both F cells logged 113 journeys for 114 presses (GATE PLAY-VOID; journeys != presses), which RN's terms did
  not read. Post-data (information, labelled in ROUNDRN-2026-11-12): F flat (-4..+9 ms), L 217-221 / 605-657 /
  1,426-1,490 ms. Round RO repeats the ABBA with the pairing rule registered before any data (operator 2026-11-12: "Keep
  12440, new rule"; the exit tick stays, so RO's cells compare directly with RL / RM / RN).
- Release relevance (information; sdlports): any long or looping PCM voice on a live SB grows ~22 KB/s on the v0.1 line,
  so 0377 is release-relevant; any v0.1.x is the operator's call. Before 0377 reaches a release, one harness audio check
  of the fixed default on a lockable mode is still owed (not in this round).
- Arms, same binary, same line, DOSAGS_MEMLOG=1 in all four: F (ROF1, ROF2) = 0377's default (the bounded ring); L (ROL1,
  ROL2) = DOSAGS_RING_LEGACY=1 (the old growth). Arm witness from RUNMANI.LOG's "DOS-PORT voicering legacy= compact_at=
  compactions= moved_bytes= cap_max=" line: F needs legacy=0, compactions >= 1 and cap_max <= 196,608; L needs legacy=1 and
  compactions=0 (cap_max reported; RN 4,037,632). Read after the round: env_block_sha equal within each arm and different
  between F and L (the switch is in the allowlist), else the ABBA is VOID. A cell without the voicering line, or failing
  its arm's terms, is VOID for the ABBA (reported). A cell that exits with RUNMANI but without a clean finish (RUNMANIFEST
  exit_code != 0, or STDOUT.TXT without "***** ENGINE HAS SHUTDOWN") is VOID-NOFINISH; an AGS that dies without RUNMANI
  leaves run-hw REFUSED at its timeout and the round STOPS there. A hang on an error screen is a timeout STOP, as in every
  round. The memlog header's dropped > 0 is information only.
- PAIRING (new in RO, registered before any data): tests/harness/ms3-pairing.py, sha256 be9046a79c8be0f7ebe0541146bd6b9be1a6a1e56394c40e91056780092d65d9,
  from move's lab checker (lab-rb 957760ea clocksteps-ro.py) with condition (3) pinned (sdlports). Offset of press k =
  DRIVE-WALK.LOG down_at minus journey k's RUNMANI t_ms. Verdicts:
  PAIR-OK: journeys == presses == 114, t_ms strictly increasing, first room-2 journey #17, and no sustained offset shift
  <= -150 ms in presses 6-109 (5-press median after minus 5-press median before).
  PAIR-OK-114LATE: journeys 113, presses 114, and all of: (1) t_ms strictly increasing, first room-2 journey #17; (2) no
  sustained shift <= -150 ms in presses 6-108 (a missing journey shifts every later offset by about -1 press interval,
  >= ~1 s), and no sustained shift >= +150 ms in presses 23-108 outside the step brackets (windows overlapping presses
  33-36, 52-54, 90-95); (3) press 114's game time (its down_at minus the median offset of presses 95-113) is (3a)
  STRICTLY GREATER than the last persec line's ms= field, no tolerance, AND (3b) STRICTLY GREATER than the loop-end
  estimate (last persec ms + (exit tick - its tick) x the ms per tick of the last 5 persec rows), no tolerance. (3b) is
  the stricter: the last persec line precedes the exit by ~20 ticks (~0.5 s), and RN's journey 113 itself came after it.
  PAIR-VOID: anything else, every failed condition listed. A cell is read for its steps only under PAIR-OK or
  PAIR-OK-114LATE. An F cell whose ONLY failed condition is the (2) positive shift outside the brackets is reported as
  MIXED for that arm (a moved freeze and an extra journey cannot be told apart), not VOID; any other PAIR-VOID is VOID for
  the ABBA.
  Witness, every MS3 cell, printed by the driver into SUMMARY.txt and kept as PAIRING.txt: "WITNESS <cell>
  press114_game_ms= last_persec_ms= diff_ms=" (diff = press114_game_ms - last_persec_ms; a 114-journey cell prints journey
  114's t_ms), then the loop-end estimate and press 114's margin over it; then the PAIR and LEVEL lines.
  Simulation before the round (this checker as committed, on round records): RNF1 / RNF2 PAIR-OK-114LATE, press114_game_ms
  198,727.0 / 198,467.0, last_persec_ms 197,307 / 197,204, diff +1,420.0 / +1,263.0 ms, margin over the estimate +897.1 /
  +593.7 ms, levels -4 / +2 / +0 and +0 / +9 / +4 ms; RNL1 / RNL2 / RMA1 PAIR-OK 114 / 114, levels 217 / 605 / 1,490, 221 /
  657 / 1,426, 214 / 657 / 1,486 ms (= RN's and RM's published reads). Controls on copies of RNL1's RUNMANI.LOG, all
  PAIR-VOID: journey 10 dropped (first room-2 journey #16; -2,589 ms at press 10; (3a) and (3b)); journey 60 dropped (-1,164
  ms at press 60; (3a), (3b)); journey 113 dropped and journey 114 dropped ((3a), (3b): press 114 lands 2.2 s before the
  last persec line); journey 60 dropped + journey 100 duplicated (114 / 114, but -1,164 ms at press 60).
- Pointing (drive6-gate.sh --play), combined by the driver into a PLAYREAD line: OK = GATE PLAY-OK; OK-114LATE = GATE
  PLAY-VOID whose ONLY failure in PLAY-RESULT.txt is "logged 113 walk targets for 114 presses" in a PAIR-OK-114LATE cell
  (presses 1-113 pointing-checked in their bands); otherwise VOID, reported. Pointing is not a stop.
- Freeze steps, LEVEL METHOD (as round RN): each step = the change of the median offset between the step-free press
  stretches 21-33 | 36-52 | 54-90 | 95-114 (95-113 under PAIR-OK-114LATE), i.e. +830 (33->36), +1,730 (52->54), +3,540
  (90->95); resolution +-30 ms. Reference (the legacy behaviour, rounds RL / RM / RN, 10 cells): +830 164-221 ms, +1,730
  599-666 ms, +3,540 1,426-1,492 ms.
- "Gone" in an F arm needs both: (a) the +1,730 and +3,540 level steps each < 150 ms, AND (b) the moved-freeze guard: the
  per-press offset trace shows no sustained step >= 150 ms anywhere from press 21 to 114 (113 under PAIR-OK-114LATE). If
  (a) holds and (b) does not, that arm is mixed. The F arms' per-press traces are printed in the results.
- Prediction (falsifiable): with 0377 the ring no longer reallocates in the stay, so both F arms read "gone". FALSIFIED if
  either F arm keeps both: +1,730 >= 500 ms AND +3,540 >= 1,000 ms. Anything between (one step kept, a step 150-500 /
  150-1,000 ms, or a guard failure) is reported as mixed, no verdict. SUPPORTED = both F arms "gone", both L arms valid
  (below), every ABBA cell valid (arm witness, env_block_sha, PAIR-OK / PAIR-OK-114LATE, clean exit), and the audio bar
  met: then 0377 is the fix on the 486, and the removals of 0376 and of 0377's switch follow.
- The L arms must themselves show both steps at those sizes (>= 500 / >= 1,000 ms, as all 10 RL / RM / RN legacy cells
  did); an L arm without them is reported and the ABBA reads inconclusive.
- Secondary (information, registered): the +830 step < 150 ms in both F arms (RN F: -4 / 0 ms). Memlog: F arms show no
  row-to-row drop of free physical pages >= 64 after room-2 entry +120 ticks (RN F: flat after +71); L arms show the
  192 / 512 / 992-page drops in the +850 / +1,743 / +3,570 brackets. Board holds: the +91 / +109 / +131 / +177 s holds
  absent in F, present in L (a hold needs a packet in flight, so an absent L hold says nothing); the +42 s hold in both.
- Also reported (information): displayed % per cell, F vs L (RN: F 91.48 / 92.55%, L 89.53 / 89.72%; +0.65-0.9 points
  attributable to the step windows, the rest needed replication; RO is that replication, no claim either way). The
  voicering line per arm (RN F: 38-39 compactions, cap_max 128,000). Each F run's wall time vs L.
- Audio, a HARD BAR in the F arms (0377 changes the mixer for every SB user): underruns 0 / overwrites 0 in RUNMANI's
  audio status. An F arm with an underrun or overwrite is reported as an audio regression, and 0377 is then not kept on
  by default without a fix, whatever its steps read. L arms: reported.
- USB4VC firmware 0.5.109 (as rounds RL / RM / RN). Reported per cell: pkt_partial / pkt_timeout / mouse.dropped and
  ev_in == pkt_built; a partial voids an MS3 cell from that press (rule M0).
- Round RO (the verdict round for ags 0377): WARMUPRO, ROCALQ [-> ROCAL on a calq miss], ROF1 ROL1 ROL2 ROF2 (the ring
  ABBA), RODT (DPMITIM2, information), ROP1 (P9M1 on RNREL; first to drop). One power-on, cap 120 min. Budget line: need
  at ROCALQ 1520 s (calq 760 + the full cal 760, counted up front); the ABBA block's graded needs ROF1 3040 / ROL1 2280 /
  ROL2 1520 / ROF2 760 (counted from the ABBA alone, so it never waits on what follows); then RODT 900 and ROP1 760, each
  under its own need after the ABBA (CUT reset): ROP1 and then RODT are dropped before any ABBA arm is. Whole round after
  the warm-up 6220 s with the full cal, 5460 s without, vs CAP_MIN 120 x 60 - warm-up 630 - 240 = 6330 s: with the
  full cal, a warm-up more than ~110 s over its 630 costs ROP1 (then RODT), not an arm. (Round RN, same shape: warm-up
  593 s from relay-on, no full cal, every cell ran, power off at 90 min.)
  DIAGNOSTIC ONLY: no cell of this round is scored against a target or counts toward the proof pair. MS3 target: not yet set
  (operator).
