# RMA2 -- MS3 swap ABBA, arm A: the default DPMI host (swap on), DOSAGS_MEMLOG=1 (written 2026-11-12; pre-registration, before any data)
- Binary: RMREL.EXE = main 4aff3001 release (ags 0001-0373 + 0376, the TEMPORARY DOSAGS_MEMLOG=1 diagnostic, off unless
  set; sdlports-reviewed), stamp 2725928f2e37, build_dirty=0, sha256 b221866b..., +1,879 B over round RL's 942ad0260d36. Off path: one
  cached int test per sample (lab: tick-phase call counts identical to the unpatched build). VOID if the staged stamp
  differs. BLASTER.TXT.
- Witness: STDOUT "DOS-PORT charreuse DOSAGS_CHAR_REUSE=(default) mode=2", "guiclip ...=(default) mode=4", "guictrlmark
  DOSAGS_GUI_CTRL_MARK=(default) mode=1", "routeprewarm ...=(default) mode=0" (the *_final mode= lines stand in if a startup
  line is missing); charreuse_final skips > 0, else VOID. Camera shows play.
- Play line: P9M1's verbatim (AGSSAVE.007 f486d0e9..., ACSETUP-ON-512X384-ROUND.CFG, --no-fine-timing, TAS exit 12440).
- MS3: DRIVE 6, DRIVE6_MODE=ms, one-call presses, the values from RMCALQ (or RMCAL); 114 presses. Runs only after a
  calibration GATE PASS.
- The question: the 486 freezes machine-wide (IRQ0 unserviced) ~0.66 s and ~1.5 s at the two known MS3 stalls, bound to the
  room-2 stay (round RL, lab-rb 51f5e511). Candidate under test: CWSDPMI r7 paging to its default swap file c:\cwsdpmi.swp
  (a VCPI client of EMM386 NOEMS; records give ~138 MB = free physical + swap at the minimum, so ~7-8 MB physical headroom).
- Arms, same binary, same line, DOSAGS_MEMLOG=1 in all four: A (RMA1, RMA2) = the default host as every earlier round; B
  (RMB1, RMB2) = `CWSDPMI -s-` on the RUN.BAT line before AGS.EXE (lab-verified, LAB-MOVE 10.20: it serves that one DPMI
  client and unloads with it). Arm witness from RUNMANI.LOG's memlog header and rows, testing only what the arm means (DPMI
  0400h flags bit 2 = virtual memory; the other bits depend on the host's mode under EMM386): A needs (flags & 4) != 0 and
  swap > 0; B needs (flags & 4) == 0 and swap=0 on every row. The full flags value is information. A cell whose witness
  fails is VOID for the ABBA (reported). The header's dropped > 0 (ring full, 512 rows) is information only.
- Out of memory: run-hw's collection waits for STDOUT.TXT AND the RUNMANIFEST log, so an AGS that dies without writing
  RUNMANI leaves run-hw REFUSED at its timeout and the round STOPS there (RMA2 and RMP1 are lost; the cell keeps whatever
  STDOUT.TXT shows). In a B arm that is read as "MS3 may not fit the 486's physical memory without swap", information,
  not a verdict. A cell that exits with RUNMANI but without a clean finish (RUNMANIFEST exit_code != 0, or STDOUT.TXT
  without "***** ENGINE HAS SHUTDOWN") is VOID-NOFINISH; in a B arm RMB2 is then not run and RMA2 still runs. A hang on
  an error screen is a timeout STOP, as in every round.
- Freeze-step witness (lab, lab-rb 8dbd89c2 move-lab/rj/rl/clocksteps-release.py; works on a plain release cell): per
  press, DRIVE-WALK.LOG's host down_at minus RUNMANI.LOG's "DOS-PORT journey kind=click ... t_ms=", paired 1:1 by index
  (the script refuses unless journeys == presses, 114 / 114); STDOUT.TXT's room-2 "event=ready" and RUNMANI's persec lines
  place each step in ticks after room-2 entry. LEVEL METHOD: each step = the change of the median offset between the
  step-free press stretches 21-33 | 36-52 | 54-90 | 95-114, i.e. +830 (33->36), +1,730 (52->54), +3,540 (90->95);
  resolution +-30 ms (null level differences inside the stretches, RLM1-4: max |30| ms, n 24). A-arm reference, RLM1-4
  (lab-rb CLOCK-STEPS-RLM.txt): +830 164 / 214 / 207 / 213 ms, +1,730 599 / 612 / 618 / 666 ms, +3,540 1,492 / 1,480 /
  1,492 / 1,486 ms; brackets +818..+959, +1,723..+1,793, +3,513..+3,686 ticks after entry. Memlog rows align to the steps
  through their lc (their ms is the game timer, not uclock).
- "Gone" in a B arm needs both: (a) the +1,730 and +3,540 level steps each < 150 ms (5x the null max), AND (b) a moved-
  freeze guard -- the per-press offset trace (each press's offset minus the previous one's; only sustained jumps, a late
  press reading + then -) shows no sustained step >= 150 ms anywhere from press 21 to 114. If (a) holds and (b) does not,
  that arm is mixed. The B arms' per-press traces are printed in the results.
- Prediction (falsifiable): if the CWSDPMI swap is the freeze, both B arms read "gone". FALSIFIED if either B arm keeps
  both: +1,730 >= 500 ms AND +3,540 >= 1,000 ms (the swap is then out; EMM386 / VCPI or SMI stay open), whatever A's
  memlog shows. Anything between (one step kept, a step 150-500 / 150-1,000 ms, or a guard failure) is reported as mixed,
  no verdict.
- Naming the mechanism, if both B arms read "gone": if the A arms' memlog rows show free physical pages at their floor
  within one to two samples either side of each step (rows come every ~1.8 s of engine time in the lab smoke, so nothing
  finer is claimed), the verdict is "CWSDPMI demand paging (physical shortage)"; if no floor shows near the steps, it is
  "CWSDPMI swap" only (the swap file is involved, e.g. its housekeeping or I/O, but paging from physical shortage is not
  shown).
- The A arms must themselves show both steps at those sizes (>= 500 / >= 1,000 ms, as RLM1-4 did); an A arm without them is reported and
  the ABBA reads inconclusive. The +830 step (164-214 ms in A) cannot discriminate at 150 ms: information only.
- Also reported (information): displayed % per cell (A vs B, beside RLM1-4's 90.68%; not a target reading), the memlog's
  free / phys / swap pages through room 2, the B arms' free physical minimum, and the drive6-gate.sh --play pointing line.
  Pointing is not a stop this round; a PLAY-VOID cell reads its steps only if journeys and presses still pair 114 / 114.
- USB4VC firmware 0.5.109 (as round RL, where it passed: strict FIFO, one event per packet, original spacing). Reported per
  cell: pkt_partial / pkt_timeout / mouse.dropped and ev_in == pkt_built; a partial voids an MS3 cell from that press (rule M0).
- Round RM (the freeze-cause round; sdlports' shape): WARMUPRM, RMCALQ [-> RMCAL on a calq miss], RMA1 RMB1 RMB2 RMA2 (the
  swap ABBA), RMP1 (P9M1 bridge; first to drop). One power-on, cap 120 min. Budget line: need at RMCALQ 1520 s (calq 760 +
  the full cal 760, counted up front); the ABBA block's graded needs RMA1 3040 / RMB1 2280 / RMB2 1520 / RMA2 760; whole round
  after the warm-up 5320 s with the full cal, 4560 s without, vs CAP_MIN 120 x 60 - warm-up 630 - 240 = 6330 s.
  DIAGNOSTIC ONLY: no cell of this round is scored against a target or counts toward the proof pair. MS3 target: not yet set
  (operator).
