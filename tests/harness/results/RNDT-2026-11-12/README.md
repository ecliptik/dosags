# RNDT -- DPMITIME on the 486: the DPMI host's physical-page commit cost, default host and `CWSDPMI -s-` (information) (written 2026-11-12; pre-registration, before any data)
- RNDT: an l308 MMD-title launch (as the warm-up; not scored) carrying DPMITIME lines before AGS.EXE (shape below; each
  `CWSDPMI -s-` serves its one client and unloads, so AGS.EXE gets the default host).
- DPMITIME.EXE, a new binary on the target (a lab tool, not part of the engine): source lab-rb ba816420
  docs/lab/move-lab/rj/rm/dpmitime/dpmitime.c (sha256 65f625d05b924585...; standalone, ASCII; a copy is in this dir); build
  `i586-pc-msdosdjgpp-gcc -O2 -Wall -Wextra -o DPMITIME.EXE dpmitime.c` (no stubedit); 184,491 B, sha256
  694091858659ed634cc0b75d8c23b5e4c7c1a7e058a806adc2e6a73391fa3432 -- move's lab build, and an independent rebuild
  from that source on this host is byte-identical. It is in the round's expected.txt, checked with the exes before the
  power-on (a mismatch stops the round).
- The question: is a physical-page commit itself (first touch through CWSDPMI / EMM386 VCPI) what stops IRQ0 on the 486, or
  what the engine does around it? It matters beyond the ring: the room-2 load commits 768 pages.
- Shape (move, against page retention inside one process): one DPMITIME process per size, largest first: `DPMITIME N -n 3 >
  DPAN.TXT` for N = 992, 512, 192, 32 (the default host, autoloaded per process), then the same four as DPBN.TXT, each
  after its own `CWSDPMI -s-` line (no swap). Rep 1 of each file = a cold commit of N pages from a fresh host, as in the
  engine; reps 2-3 = warm (they show retention directly). 8 files collected, 14 lines each (header, 12
  phase lines, "DPMITIME done rc=0"); a file of another length is reported.
- Fields (per phase line; lab-rb ba816420 dpmitime/README.md): lost_ms = rtc_ms - uclock_ms over the phase's RTC-edge-to-
  edge window = the IRQ0-unserviced time, the same quantity the engine's level steps read; whole lost BIOS ticks (~54.9
  ms), reading up to one tick low (the PIC holds one pending IRQ0). bios_ticks vs expect_ticks is the same loss in ticks
  (cross-check, same mechanism). call_ms = uclock across the call alone (blind to the freeze). A phase longer than 1 s
  spans more RTC seconds; nothing is truncated. free = DPMI 0500h free pages after the phase: if the 486's host commits at
  0501h instead of first touch, the cost moves to the alloc row, so alloc + touch are read together.
- Validity: each file's own header carries its process's DPMI 0400h flags: DPA files need bit 2 set (virtual memory),
  DPB files bit 2 clear (each B process follows its own `CWSDPMI -s-` line, which serves that one client and unloads); a
  file whose header reads the other arm is VOID. Every null phase rtc_ms 1000 and |lost_ms| <= 55 ms
  (bios_ticks 18-19). A null phase losing >= 55 ms marks that file noisy (something else steals IRQ0), reported, and that
  file is not read for the prediction. Exit 2 / "FAIL 0501h" in a file = that size not read.
- Prediction (sdlports' hypothesis: the commit itself, CWSDPMI over VCPI with interrupts off, is the freeze). Reference,
  the engine's level steps for the same commits (RL / RM): 192 pages -> 164-214 ms, 512 -> 594-666, 992 -> 1,476-1,492.
  SUPPORTED if in BOTH arms the rep-1 alloc + touch lost_ms reads 992 >= 1,000 ms, 512 >= 400 ms, 192 >= 110 ms, with
  every null / free phase <= 55 ms and the 32-page rep 1 <= 110 ms. FALSIFIED if 992's rep-1 alloc + touch lost_ms
  < 300 ms in both arms (the commit then cannot explain a fifth of the 1.5 s freeze; the engine's copy, or its use of the
  new memory, becomes the open candidate). Anything between: mixed, no verdict.
- Information: lost per page and the ratios lost(512) / lost(192) (engine ~2.5-3.5) and lost(992) / lost(512) (~1.9-2.6);
  large lost_ms with small call_ms = interrupts off, large call_ms with ~0 lost_ms = per-page work with interrupts on
  (which cannot make clock steps); reps 2-3 vs rep 1 (retention); A vs B (swap).
- Run time: ~25 s per process (lab), ~3.5 min for all 8, plus host loads; then the l308 launch (~8 min, as the warm-up).
- Information only: nothing here changes round RN's ABBA reading. Runs after the ABBA and before RNP1 (RNP1 drops first).
- Round RN (the fix round for ags 0377): WARMUPRN, RNCALQ [-> RNCAL on a calq miss], RNF1 RNL1 RNL2 RNF2 (the ring ABBA),
  RNDT (DPMITIME, information), RNP1 (P9M1 on RNREL; first to drop). One power-on, cap 120 min. Budget line: need at
  RNCALQ 1520 s (calq 760 + the full cal 760, counted up front); the ABBA block's graded needs RNF1 3040 / RNL1 2280 /
  RNL2 1520 / RNF2 760 (counted from the ABBA alone, so it never waits on what follows); then RNDT 900 and RNP1 760, each
  under its own need after the ABBA (CUT reset): RNP1 and then RNDT are dropped before any ABBA arm is. Whole round after
  the warm-up 6220 s with the full cal, 5460 s without, vs CAP_MIN 120 x 60 - warm-up 630 - 240 = 6330 s: with the
  full cal, a warm-up more than ~110 s over its 630 costs RNP1 (then RNDT), not an arm.
  DIAGNOSTIC ONLY: no cell of this round is scored against a target or counts toward the proof pair. MS3 target: not yet set
  (operator).
