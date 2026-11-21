# LAB2X gate, third run (2026-11-20T16:26:14Z - 21:15:06Z; DOSBox-X, lane 398): PASSED

Registered terms: PREREG-2X.md + FIX-UP 1 + FIX-UP 2 + FIX-UP 3 (ce735153, b085087b, c7270f3a, dfbf3cc4). Builds:
- PLAIN.EXE c68241073cb0... (the shipped release, reproduced);
- S2NR.EXE 9599809419c821e0aed4a1740e82f311a07cbea663a4580e7544f892be539043 (8,681,739 B; overlay tests/harness/apply-2x.py
  sha256 5e7b74497647...).

73 runs, every rc 0. Reader tests/harness/gate-2x-read.py at dfbf3cc4 (sha256 02f268a7cab5...): exit 0, "0 FAIL, 0 VOID,
0 MISSING; controls: all have power" (GATE-READ.txt, with an rc=0 line; VERDICT.txt is the driver's copy of the same
reading).

**Verdict (sdlports' ruling): PASSED as registered (reader exit 0).** S32P-2x is EXCEPTED under F1.5 (pack24 is not engaged
in DOSBox-X) and moves to the 486. This is an emulator gate: it says the 2x narrowed path draws the same frames as the
reference here. It is not a performance claim. That is for the 486 A/B.

sdlports verified from raw:
- It re-ran the reader at dfbf3cc4 on the cells: exit 0, output byte-identical to VERDICT.txt.
- All 73 rc files are 0. EXE-SHA256 shows 69 runs on S2NR 9599809419c8 and 4 on PLAIN c68241073cb0.
- The break= witnesses read from RUNMANI.LOG: A 0 (9 runs), C2 3 (9), V2 3 (9), C2i 1 (4).
- Its own frame compare: A-B is 0 px on B16-2x-walk FRZ00-02 and CLK-2x FRZ00-02. C2-B there is 1728/1728/1936 px and
  496/496/656 px; on the B16-walk montage the C2 walker is visibly stale at its start position.

Registered lines, all PASS:
- A==B 0-differ at every freeze (S16-2x 7/7, S8-2x 7/7, CLK-2x 13/13, bench rows 5/5, B8-full 2/2). F==B likewise. R==B 0
  in S16-2x, S8-2x and CLK-2x.
- V (the verifier) is clean everywhere (vfy_bad=0).
- V2 (break=3 with the verifier) has power in all 8 rows. Its vfy_bad is next to DIAG-FIXUP3.txt's "all" count (the
  presents with a changed px in some box); V2 >= all in every row:

  | Row | V2 vfy_bad | DIAG "all" |
  |---|---|---|
  | S16-2x | 521 | 48 |
  | S8-2x | 875 | 229 |
  | CLK-2x | 950 | 137 |
  | B8-2x-walk | 1040 | 198 |
  | B8-2x-anim12 | 1040 | 502 |
  | B8-2x-full | 120 | 4 |
  | B16-2x-walk | 1035 | 197 |
  | B16-2x-anim12 | 790 | 501 |

- C2 (break=3) differs from B in all 7 registered rows: S16-2x 5/7, S8-2x 4/7, CLK-2x 12/13, and 5/5 in B8-walk, B8-anim12,
  B16-walk and B16-anim12. On B8-2x-full (information) it differs 2/2.
- The 1x pair S16-1x is inert: I1==I0 7/7, rej geom=1012.

Information:
- In gate2, at break=2, B16-2x-walk's V2 read 0. Here it reads 1035.
- S16-2x and B16-2x-anim12 read the same V2 counts as gate2's break=2 (521, 790).
- C2i (break=1) differs 0 in every game row, as in gates 1 and 2.
- C1 (DOSAGS_BREAK_0193=1) differs: S16-2x 3/7, S8-2x 4/7, CLK-2x 11/13, B8-walk 5/5, B8-full 2/2, B8-anim12 and the B16
  rows 0/5.

Build check, stated as "same resulting files" (as in gate2): PLAIN reproduced byte for byte. The build's own vendor.diff
and the registered apply-2x-fixup3.diff, each patched onto a clean copy of dosags-ring vendor/ags HEAD d47c5b982a35, gave
cmp-identical files (Engine/gfx/ali3dsw.cpp de9f31f246e0..., Engine/main/quit.cpp 37dfcf7d3695...).

Next (sdlports): the 486 A/B pre-reg, drafted for sdlports' review. It has:
- the capture stick as witness (a stick drop during a run voids that run; owner decision 01M7X8X4SVZNCB41005GSYWSG7);
- S32P-2x's pack24 check;
- the KPI and bar stated before any data. The 2x bar is the owner's call.

If 2x proves out there, it ships opt-in, default off (owner decision 01M7W318SCKJXDDNCM6FB1D1CZ item 4). The power-on needs
the owner's direct OK. The push stays held until 2x passes on the 486 or is parked.

Kept here: per-cell RUNMANI.LOG, RUN-ARGS.txt, rc, EXE-SHA256.txt, ROW.txt, and the per-row *-vs-B.txt comparison lines.
Not kept: the freeze frames (game screens) and STDOUT (in the scratchpad, SCRATCH/2x/gate3).
