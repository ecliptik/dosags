# RODT -- DPMITIM2 on the 486: does the per-page commit cost grow with the pages already committed? (information) (written 2026-11-12; pre-registration, before any data)
- RODT: an l308 MMD-title launch (as the warm-up; not scored) carrying DPMITIM2 lines before AGS.EXE, one process per
  line: `DPMITIM2 992 -n 2 -b K > D2A<K>.TXT` for K = 0, 2048, 4096, 6144 (the default host, autoloaded per process),
  then the same four as D2B<K>.TXT, each after its own `CWSDPMI -s-` line (no swap; it serves that one client and
  unloads, so AGS.EXE gets the default host). 8 files collected.
- DPMITIM2.EXE, a new binary on the target (lab tool v2, not part of the engine): source lab-rb d0874d3f
  docs/lab/move-lab/rj/rm/dpmitime/dpmitime2.c (sha256 353376197ae8305a...; standalone, ASCII; a copy is in this dir);
  build `i586-pc-msdosdjgpp-gcc -O2 -Wall -Wextra -o DPMITIM2.EXE dpmitime2.c` (no stubedit); 185,616 B, sha256
  afeff82ededf17314ffe939b4fe9366cb6880d350f8bf33f5698c088451314fb -- move's lab build, and an independent rebuild from
  that source on this host is byte-identical. In the round's expected.txt with the exes. v2 fixes v1's rig failure (RNDT
  VOID: v1 read the RTC with interrupts on, and IRQ0 left the CMOS index on register 0): interrupts off around every
  70h / 71h pair, a time only from two identical reads, rtc_ok per line; -b K allocates and touches K pages first (its
  own timed line) and keeps them to exit.
- The question (RNDT-DIAG, move): a cold first touch of 992 pages cost call_ms 198 ms on the 486 (0.20 ms per page; fit
  a N + b N^2) with the clock running, ~1/7 of the engine's 1.49 s step. Two readings: (a) the per-page cost grows with the
  pages already committed (the N^2 term; at the engine's ~5,300-6,300 pages in use ~0.7-0.84 ms per page, near the
  engine's 1.28-1.50 ms); (b) the engine's commit takes another host path that a first touch does not.
- File validity: 10 lines for K=0, 11 for K>0 (header, [ballast], null / alloc / touch / free x 2 reps, "DPMITIME done
  rc=0"); the header's DPMI 0400h flags bit 2 set in D2A files, clear in D2B files (else that file is VOID); free
  pages at the header >= K + 992 (rig: 8,165 in RN). A line with rtc_ok=0 is not read; a null phase with |lost_ms| > 55
  marks that file noisy (not read for the prediction, reported); exit 2 / "FAIL" = that K not read.
- Cost per page c(K) = (rep-1 touch call_ms + rep-1 touch lost_ms) / 992 (call_ms is the touch's length with the clock
  running; lost_ms the IRQ0-unserviced time, if any). Prediction (move's terms): reading (a) SUPPORTED if in BOTH arms
  c(6144) >= 3 x c(0) and c is non-decreasing over K = 0, 2048, 4096, 6144. Reading (a) FALSIFIED if c(6144) <= 1.5 x
  c(0) in both arms (then (b): the engine's commit path is the open candidate). Anything else: mixed, no verdict. A K
  not read in either arm leaves that arm unread for the prediction.
- Information: the ballast line's own cost (a K-page cold commit) per page; rep 2 vs rep 1 (retention); A vs B (swap);
  lost_ms > 0 on any touch (interrupts off). Nothing here changes round RO's ABBA reading. Runs after the ABBA and
  before ROP1 (ROP1 drops first). Run time (lab): ~3.5-4.2 min for the 8 processes, then the l308 launch (~8 min).
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
