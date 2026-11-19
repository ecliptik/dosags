# WARMUPRM -- rig warm-up, plus read-only listings of C:\ and MEM (written 2026-11-12; pre-registration, before any data)
- l308.exe (bc9c3704a839), MMD title, not scored. Checks: BLASTER.TXT = "A220 I7 D3 P330 T3" else STOP; capture device present
  at the pre-flight; a capture STALE of any kind but "nolock" stops the round.
- ROOTLIST.TXT: `DIR C:\ /A` (read-only) -- CWSDPMI.SWP's size if present (the default swap file) and the drive's free bytes.
  MEMLIST.TXT: `MEM` (read-only) -- total / free extended memory and EMM386's state. Information for the ABBA, not a gate.
- The question: the 486 freezes machine-wide (IRQ0 unserviced) ~0.66 s and ~1.5 s at the two known MS3 stalls, bound to the
  room-2 stay (round RL, lab-rb 51f5e511). Candidate under test: CWSDPMI r7 paging to its default swap file c:\cwsdpmi.swp
  (a VCPI client of EMM386 NOEMS; records give ~138 MB = free physical + swap at the minimum, so ~7-8 MB physical headroom).
- Round RM (the freeze-cause round; sdlports' shape): WARMUPRM, RMCALQ [-> RMCAL on a calq miss], RMA1 RMB1 RMB2 RMA2 (the
  swap ABBA), RMP1 (P9M1 bridge; first to drop). One power-on, cap 120 min. Budget line: need at RMCALQ 1520 s (calq 760 +
  the full cal 760, counted up front); the ABBA block's graded needs RMA1 3040 / RMB1 2280 / RMB2 1520 / RMA2 760; whole round
  after the warm-up 5320 s with the full cal, 4560 s without, vs CAP_MIN 120 x 60 - warm-up 630 - 240 = 6330 s.
  DIAGNOSTIC ONLY: no cell of this round is scored against a target or counts toward the proof pair. MS3 target: not yet set
  (operator).
