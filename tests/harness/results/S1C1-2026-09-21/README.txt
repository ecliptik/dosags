S1C1 -- ags 0191 DOSBox-X correctness gate (slice C), pre-registered in PLAN.md step 1.

first-run/  binary_sha12=14801f016c21 (0191 before the flush-reason counters)
final-run/  binary_sha12=53df45d9ac94, sha256 e234a22733d6d60609f7c17d06083c19c159ffa324abbd689eaada3b2a6e02be
            = the binary the hardware A/B runs as arm B.

(a) BENCH8 and BENCH16 gui capture == baseline: PASS both runs.
(b) idle walk anim4 anim12 text unchanged at both depths; full fails as before (F2): PASS.
(c) AGS Quest harness: PASS all phases, PH01-PH03 match.
(d) mechanistic, AGS Quest DOSBox run:
      gCredits skipped 420 of 421 (>=415)   PASS
      gCredits changed 1 (<=3)              PASS
      guiskip flushed 51, late 0            flushed <= 8 MISSED
      dirtysrc uisprite px 12,670,908       within 5% of 11,723,320 MISSED (+8.08%)
    The two misses are a wrong model of OTHER GUIs, not a defect: final-run reads
    flushed=51 hidden=4 props=0 flag=47, by GUI idx 2 x37, idx 3 x7, idx 4 x6,
    idx 0 x1. Those GUIs change while drawn, the old tautological skip suppressed
    their marks too, and the fix now marks them (about 18.6k px per flush).
DOSBox-X: pixel accounting only, no rate claim.
