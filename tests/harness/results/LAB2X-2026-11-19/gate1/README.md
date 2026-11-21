# LAB2X gate, first run (2026-11-19T20:21:34Z - 2026-11-20T00:35Z; DOSBox-X, lane 398): NOT PASSED

Registered terms: PREREG-2X.md + FIX-UP 1 (ce735153, b085087b). Builds: PLAIN.EXE c68241073cb0... (the shipped release,
reproduced), S2NR.EXE 553fac679b4caa46... (8,681,227 B). 69 runs, every rc 0. Reader tests/harness/gate-2x-read.py: exit 1,
"3 FAIL, 48 VOID, 0 MISSING; controls: C2 did not differ in CLK-2x, S16-2x, S8-2x; a V2 read vfy_bad=0" (GATE-READ.txt).

**Verdict (sdlports' ruling): the gate as registered is NOT PASSED.** The registered controls had no power (C2 =
DOSAGS_SCALE2_BREAK=1 differed from B in 0/7 S16-2x and 0/13 CLK-2x pairs; V2 read vfy_bad=0 everywhere), and 48 cells are VOID
by the witness rule frames_skipped=0 (S8-2x and the B8 / B16 walk and anim12 rows read frames_skipped=-1 in every arm, the plain
exe R included: the engine's known un-timestepped value, game_run.cpp:1528-1546). B8-2x-full: "A rej fmt=0" FAIL (rej fmt=1).
S32P-2x EXCEPTED as registered (pack24 not engaged in DOSBox-X; moves to the 486).

Information beside the verdict, where the cells are valid (encouraging, not a pass): A==B, F==B and R==B equal at every freeze
(S16-2x 7/7, CLK-2x 13/13, B8-full 2/2); V clean (vfy_bad=0); the 1x pair S16-1x inert (I1==I0 7/7, rej geom = every present);
C1 (DOSAGS_BREAK_0193=1) differed (3/7, 11/13, 2/2), so the comparison has power over missed regions. A at S16-2x narrowed
98.5% of presents (narrow 997, full 15).

Next: FIX-UP 2 (a whole-box break control, the frames_skipped witness, rej fmt as information), then the WHOLE gate re-run on
the new build. Kept here: per-cell RUNMANI.LOG, RUN-ARGS.txt, rc, ROW.txt, EXE-SHA256.txt; not kept: the freeze frames (game
screens) and STDOUT (in the scratchpad, SCRATCH/2x/gate).
