# RNL2 -- MS3 ring ABBA, arm L: DOSAGS_RING_LEGACY=1 (the old growth), DOSAGS_MEMLOG=1 (written 2026-11-12; pre-registration, before any data)
- Binary: RNREL.EXE = main 987ddce1 release (ags 0001-0373 + 0376 + 0377; sdlports-reviewed), stamp 93df50d751a8, build_dirty=0,
  sha256 ce8d275f..., +796 B over round RM's 2725928f2e37. 0377 bounds the mixer's per-voice ring (patch 0049's Voice::ring:
  the consumed prefix is dropped once it reaches 64 KB) and is ON by default; its TEMPORARY DOSAGS_RING_LEGACY=1 switch
  restores the old unbounded growth (removal owed after this round, with 0376). VOID if the staged stamp differs.
  BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  DOSAGS_GUI_CTRL_MARK=(default) mode=1", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup
  line is missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Play line: P9M1's verbatim (AGSSAVE.007 f486d0e9..., ACSETUP-ON-512X384-ROUND.CFG, --no-fine-timing, TAS exit 12440).
- MS3: DRIVE 6, DRIVE6_MODE=ms, one-call presses, the values from RNCALQ (or RNCAL); 114 presses. Runs only after a
  calibration GATE PASS.
- The question: rounds RL / RM found the 486 freezing machine-wide (IRQ0 unserviced) ~0.2 / ~0.65 / ~1.5 s in the room-2
  stay, each at a DPMI physical-page commit (192 / 512 / 992 pages, the same with and without CWSDPMI's swap). The lab
  (move, lab-rb move-lab/rj/rm LAB-RING.txt / LAB-RING377.txt) named the owner: patch 0049's per-voice ring drops its
  consumed prefix only when fully drained, so with a live SB the looping room-2 ambient voice (sound 96, channel 1) grows
  ~22 KB/s with 2x reallocations (0.75 / 2 / 3.9 MB), and each reallocation's copy commits the new block at once. Under
  test: ags 0377 (bounded ring) against its own legacy switch, same binary, same line.
- Release relevance (information; sdlports): the leak is not MMD-only. Any long or looping PCM voice on a live SB grows
  ~22 KB/s on the v0.1 line (~20 MB in a 15-minute stay; the ratchet's live-SB 5 Days unit compacts too), so 0377 is a
  release-relevant fix; any v0.1.x is the operator's call. Before 0377 reaches a release, one harness audio check of the
  fixed default on a lockable mode (an existing 640x480 audio cell against its reference) is owed: not in this round
  (budget), the next one.
- Arms, same binary, same line, DOSAGS_MEMLOG=1 in all four: F (RNF1, RNF2) = 0377's default (the bounded ring); L (RNL1,
  RNL2) = DOSAGS_RING_LEGACY=1 (the old growth). Arm witness from RUNMANI.LOG's "DOS-PORT voicering legacy= compact_at=
  compactions= moved_bytes= cap_max=" line: F needs legacy=0, compactions >= 1 and cap_max <= 196,608; L needs legacy=1 and
  compactions=0 (cap_max reported; lab 4,037,632). Read after the round: env_block_sha equal within each arm and different
  between F and L (the switch is in the allowlist), else the ABBA is VOID. A cell without the voicering line, or failing
  its arm's terms, is VOID for the ABBA (reported). A cell that exits with
  RUNMANI but without a clean finish (RUNMANIFEST exit_code != 0, or STDOUT.TXT without "***** ENGINE HAS SHUTDOWN") is
  VOID-NOFINISH; an AGS that dies without RUNMANI leaves run-hw REFUSED at its timeout and the round STOPS there. A hang
  on an error screen is a timeout STOP, as in every round. The memlog header's dropped > 0 is information only.
- Freeze-step witness (unchanged from round RM; lab-rb 8dbd89c2 move-lab/rj/rl/clocksteps-release.py): per press,
  DRIVE-WALK.LOG's host down_at minus RUNMANI.LOG's "DOS-PORT journey kind=click ... t_ms=", paired 1:1 by index (refuses
  unless journeys == presses, 114 / 114). LEVEL METHOD: each step = the change of the median offset between the step-free
  press stretches 21-33 | 36-52 | 54-90 | 95-114, i.e. +830 (33->36), +1,730 (52->54), +3,540 (90->95); resolution +-30 ms.
  Reference (the legacy behaviour, rounds RL / RM, 8 cells): +830 164-214 ms, +1,730 599-666 ms, +3,540 1,476-1,492 ms.
- "Gone" in an F arm needs both: (a) the +1,730 and +3,540 level steps each < 150 ms, AND (b) the moved-freeze guard: the
  per-press offset trace (each press's offset minus the previous one's; only sustained jumps) shows no sustained step
  >= 150 ms anywhere from press 21 to 114. If (a) holds and (b) does not, that arm is mixed. The F arms' per-press traces
  are printed in the results.
- Prediction (falsifiable): with 0377 the ring no longer reallocates in the stay, so both F arms read "gone". FALSIFIED if
  either F arm keeps both: +1,730 >= 500 ms AND +3,540 >= 1,000 ms (0377 is then not the fix on the 486, whatever the lab
  shows). Anything between (one step kept, a step 150-500 / 150-1,000 ms, or a guard failure) is reported as mixed, no
  verdict.
- The L arms must themselves show both steps at those sizes (>= 500 / >= 1,000 ms, as all 8 RL / RM cells did); an L arm
  without them is reported and the ABBA reads inconclusive.
- Secondary (information, registered): the +830 step < 150 ms in both F arms (L: 164-214 ms, too close to 150 to
  discriminate alone). Memlog (rows every ~1 s, aligned to the step axis through lc): F arms show no row-to-row drop of
  free physical pages >= 64 after room-2 entry +120 ticks (lab: the last F commit ends by +81: 192 pages at +43..+81); L
  arms show RM's sequence (192 / 512 / 992-page drops in the +850 / +1,743 / +3,570 brackets, lab and RM). Board holds
  (vcctrl, lock offsets): the +91 / +109 / +131 / +177 s holds (RM's map: the +161 and +850 192s, the 512, the 992) are
  absent in F and present in L; the +42 s hold (the room-1 128-page commit, before room 2) is in both arms. A hold needs a
  packet in flight, so an absent hold in L says nothing.
- Also reported (information): displayed % per cell (F vs L, beside RLM1-4's 90.68% and RM's 89.65-90.50%; not a target
  reading). Lab bound (lab-rb 4a3b7384 STEPSKIPS.txt): the skipped ticks around the three steps exceed the room-2 rate by
  +17..+49 per cell in RL / RM: if all came back, RLM1-4 would read +0.24..+0.55 points (mean 90.68 -> ~91.06%), an upper
  bound; expectation 0 to +0.5 points, inside RLM1-4's SD 0.89, so one ABBA pair cannot resolve it. The freezes themselves
  stop the clock and are not skipped ticks: displayed % is no witness of the fix (the lab reads 99.77% in every arm and
  says nothing about the 486). Each F run should be ~2.3 s shorter in wall time (information). The voicering line's
  compactions / moved_bytes / cap_max per arm (lab F: 38 / 1,085,952 / 128,000). The drive6-gate.sh --play pointing
  line. Pointing is not a stop this round; a PLAY-VOID cell reads its steps only if journeys and presses still pair
  114 / 114.
- Audio, a HARD BAR in the F arms (0377 changes the mixer for every SB user): underruns 0 / overwrites 0 in RUNMANI's
  audio status. An F arm with an underrun or overwrite is reported as an audio regression, and 0377 is then not kept on
  by default without a fix, whatever its steps read. L arms: reported.
- USB4VC firmware 0.5.109 (as rounds RL / RM). Reported per cell: pkt_partial / pkt_timeout / mouse.dropped and ev_in ==
  pkt_built; a partial voids an MS3 cell from that press (rule M0).
- Round RN (the fix round for ags 0377): WARMUPRN, RNCALQ [-> RNCAL on a calq miss], RNF1 RNL1 RNL2 RNF2 (the ring ABBA),
  RNDT (DPMITIME, information), RNP1 (P9M1 on RNREL; first to drop). One power-on, cap 120 min. Budget line: need at
  RNCALQ 1520 s (calq 760 + the full cal 760, counted up front); the ABBA block's graded needs RNF1 3040 / RNL1 2280 /
  RNL2 1520 / RNF2 760 (counted from the ABBA alone, so it never waits on what follows); then RNDT 900 and RNP1 760, each
  under its own need after the ABBA (CUT reset): RNP1 and then RNDT are dropped before any ABBA arm is. Whole round after
  the warm-up 6220 s with the full cal, 5460 s without, vs CAP_MIN 120 x 60 - warm-up 630 - 240 = 6330 s: with the
  full cal, a warm-up more than ~110 s over its 630 costs RNP1 (then RNDT), not an arm.
  DIAGNOSTIC ONLY: no cell of this round is scored against a target or counts toward the proof pair. MS3 target: not yet set
  (operator).
