# LAB2X gate, second run (2026-11-20T01:53:28Z - 06:17:52Z; DOSBox-X, lane 398): NOT PASSED

Registered terms: PREREG-2X.md + FIX-UP 1 + FIX-UP 2 (ce735153, b085087b, c7270f3a). Builds: PLAIN.EXE c68241073cb0... (the
shipped release, reproduced), S2NR.EXE f0bff4532adc615c8df88ed8c95bf0cf6342ba4c661013f3edd026c3e2d00daf (8,681,739 B; overlay
tests/harness/apply-2x.py sha256 63181bee582b...). 73 runs, every rc 0. Reader tests/harness/gate-2x-read.py (sha256
0e0eaf89bb8d...): exit 3, "0 FAIL, 0 VOID, 0 MISSING; controls: a V2 read vfy_bad=0" (GATE-READ.txt; VERDICT.txt is the
driver's copy of the same reading).

**Verdict (sdlports' ruling): NOT PASSED as registered (exit 3).** FIX-UP 2 F2.2 requires V2 (DOSAGS_SCALE2_BREAK=2 with the
verifier) to read vfy_bad > 0 in every row it runs. B16-2x-walk read vfy=1040 vfy_bad=0. Its C2 also equals B at 5/5 freezes
(an INFO check on bench rows). No rescue run. Its A, C2 and V2 scale2 counters are identical apart from break and verify
(narrow=1039, rects=4517, px_src=1962754), so the break=2 path ran on every narrowed present and skipped a box that left
nothing stale. Why is the open question for FIX-UP 3.

Information beside the verdict (encouraging, not a pass):
- A==B, F==B and R==B 0-differ at every freeze (S16-2x 7/7, S8-2x 7/7, CLK-2x 13/13; bench rows A==B and F==B 5/5, B8-full
  2/2).
- C2 (break=2) differs from B in every game row (S16-2x 5/7, S8-2x 3/7, CLK-2x 10/13). On S16-2x, per sdlports' read of the
  frames: A-B is 0 px at all 7 freezes; C2-B is 496 px at FRZ00-03 (a stale hourglass cursor), 2436 px at FRZ04, 0 at FRZ05-06.
- V2 has power in every other row: vfy_bad S16 521, S8 579, CLK 900, B16-anim12 790, B8-anim12 1040, B8-full 40, B8-walk 1040.
- V is clean everywhere (vfy_bad=0). The 1x pair S16-1x is inert (I1==I0 7/7, rej geom=1012).
- The share of presents A narrowed: 98.5% (S16-2x, CLK-2x), 99.6% (S8-2x), 96.8-99.9% (bench rows).
- C2i (break=1, information) differs 0 everywhere, as in gate1.
- S32P-2x is EXCEPTED as registered: pack24 is not engaged in DOSBox-X, so the row moves to the 486.

Build check, stated as done (sdlports' note): the build's own `git diff` (vendor.diff) and the registered
apply-2x-fixup2.diff (diff -ru) are NOT byte-equal as text. They differ in format, and the 1973/1974 hunk places a duplicated
"#endif / #ifdef __DJGPP__" boundary differently. Their sorted +/- line sets are identical (+367 -4 each). The check that
holds is "same resulting files". It took the two files from dosags-ring vendor/ags HEAD d47c5b982a35 (clean) and made three
copies of each:
- apply-2x.py (63181bee) run on the first copy;
- `patch -p1` of apply-2x-fixup2.diff on the second;
- `patch -p1` of vendor.diff on the third.

All three copies were cmp-identical: Engine/gfx/ali3dsw.cpp 6465cc54c1d1..., Engine/main/quit.cpp a0fa91135bdd....

Next (sdlports): a lab-only diagnosis of the B16-walk box lists (information, not a rescue), then FIX-UP 3 with a break
control that has power by construction on every row, bench rows included, its reader re-simulated on copies of these cells
with a negative copy. Then the WHOLE gate re-runs on the new build after sdlports' OK.

Kept here: per-cell RUNMANI.LOG, RUN-ARGS.txt, rc, EXE-SHA256.txt, ROW.txt, and the per-row *-vs-B.txt comparison lines.
Not kept: the freeze frames (game screens) and STDOUT (in the scratchpad, SCRATCH/2x/gate2).
