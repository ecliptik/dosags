# RMDIAG-2026-11-13 -- landing records for ags 0378 + 0379 (the owed removals after round RO)

DOSBox-X only. Branch `rmdiag` (worktree dosags-ring) on main 9db6262c (round RO's results) + patches/ags/0378 + 0379.
Nothing here touched the rig. Round RO (ROUNDRO-2026-11-12, SUPPORTED) is the condition both removals were owed on.

## 1. The patches

- **0378 removes 0376** (the TEMPORARY DOSAGS_MEMLOG diagnostic): the exact reverse of 0376's commit (git revert). The
  ring of 0500h readings, the 0400h read and the "DOS-PORT memlog" lines leave game_run.cpp; DOSAGS_MEMLOG leaves the env
  allowlist (quit.cpp). Patch 0043's sampler and memory_min_free_kb line are untouched.
- **0379 removes 0377's TEMPORARY DOSAGS_RING_LEGACY switch**: dos_ring_legacy() and its getenv go; the compaction
  condition is `read_pos >= RING_COMPACT_BYTES` alone (the code every fixed arm ran on the rig); DOSAGS_RING_LEGACY leaves
  the env allowlist. 0377's bound, its counters and its exit witness STAY; the witness drops only the constant field:
  `DOS-PORT voicering compact_at= compactions= moved_bytes= cap_max=` (the release audio check reads compactions >= 1
  from it).
- After both, no source file under Engine/ or Common/ mentions DOSAGS_MEMLOG, DOSAGS_RING_LEGACY, ring_legacy or memlog.
- Slots: 0374 (cap-3 lever, branch cap3) and 0375 (hitchdiag, held) stay reserved; 0378 / 0379 are the next free.

## 2. 0376's removal terms: byte-identical to the series without 0376

0376's own message: "the rebuilt release and instrumented exes must be byte-identical to builds of the series without
0376." Checked two ways:
- Source: the AGS tree after 0001-0373 + 0376 + 0377 + 0378 is git tree c79dae74084988c5e6eaa7714f3e301ed88e0430, the
  same tree as 0001-0373 + 0377 applied without 0376 (0377 cherry-picked onto 0373, re-exported for the reference build).
- Binaries: the series stopped at 0378 and the no-0376 reference series, each built clean, both flavours:

| build | stamp | instrumented sha256 / bytes | release sha256 / bytes |
|---|---|---|---|
| 0001-0378 (0379 held out) | 66abccb99f12 | 3c33eea4c8ceb259... / 8,708,267 | 1e6c63c36915e20d... / 8,669,613 |
| 0001-0373 + 0377 without 0376 | 66abccb99f12 | 3c33eea4c8ceb259... / 8,708,267 | 1e6c63c36915e20d... / 8,669,613 |

Byte-identical in both flavours (BUILDS.txt has the full hashes).

## 3. The landing builds (two clean builds per flavour, build/ags + build/ags-release wiped, make patches first)

`make patches` applies 0001-0379 cleanly (series fingerprint 5a3a2514ff85). `make build-dirty`: 0.

| flavour | sha256 | stamp_sha12 | bytes | vs 0377 (main) | round 1 == round 2 |
|---|---|---|---|---|---|
| instrumented | 1d8252a6f29da486d8fb0ee2367309925c3f8caeecd0fdc2476c19915173b853 | e5623c99f752 | 8,707,701 | -2,445 (7e19b2963a3f, 8,710,146) | yes |
| release (DOSAGS_RELEASE=1) | 2191042b343cfd66b9e01d09da100362af15b693fcf7019911a22eee9e87f728 | d5c8fe52808a (corrected) | 8,669,559 | -1,933 (93df50d751a8, 8,671,492) | yes |

Sections, release vs round RO's rnrel (93df50d751a8): .text -1,536; .data / .bss +0.

Correction (2026-11-13, after the merge be0d1d37): the release row first gave stamp e5623c99f752. That is the
INSTRUMENTED stamp (BUILDS.txt's per-round `sha12=` line is the instrumented build's; the ratchet cells, which run the
instrumented exe, print binary_sha12=e5623c99f752). DOSAGS_RELEASE=1 is in the stamp's input (Makefile), so the release
flavour has its own stamp, as rnrel's 93df50d751a8 differs from 0377's instrumented 7e19b2963a3f. The release exe
2191042b... prints **binary_sha12=d5c8fe52808a** (lab cell AQV1, 2026-11-13, the lockable-mode audio check's validity
step). Likewise section 2's stamp 66abccb99f12 is the instrumented builds' stamp; the release byte-identity there rests
on the sha256s, which are unchanged. No hash or verdict here changes.

## 4. Ratchet

`.sdl-dos-ports/shared/tools/ratchet.sh --root <rmdiag> --no-build --no-host-wait --capture-display 398 --no-record`.

| run | result |
|---|---|
| 20261112T225932Z (RATCHET-20261112T225932Z-*) | **PASS: 41 pass (12 improved), 0 fail, 0 blocked, 4 quarantined** |
| proposed limits (exact; tests/ratchet.yaml LIMIT comment) | **exe-bytes 8710146 -> 8707701, code-lock-bytes 5230400 -> 5228512** (= 0373's 8706959 / 5228176 + 742 / + 336 for 0377's ring) |

- The 12 improved: exe-bytes and code-lock-bytes (the removals; they failed in RING's run, over the then-limits), and
  exactly the 10 that improved in RING's run (journey-*-p95-ms-fixed x4, pcm-*-sb-5days x2, midi-stall-fired,
  sb-alive-clk-* x3); those 10 limits are not proposed here.
- One lab cell of move's (MS3-grow4, lab only) took the DOSBox-X lock between two ratchet units and ran in its own
  worktree; the lock serialises DOSBox-X instances, nothing overlapped.

## 5. Lab smoke: the witness lines (from the ratchet's own RUNMANI.LOGs)

- The voicering line stays, in its new form, in every unit with an SB mixer:

| run | voicering (this run) | RING's run (20261112T095514Z, with legacy=0) |
|---|---|---|
| sb-5days | compactions=0 moved_bytes=0 cap_max=32768 | 2 / 57,344 / 131,072 |
| mi-throttle-isr | 2 / 57,344 / 131,072 | 2 / 55,296 / 131,072 |
| mi-stall-isr | 0 / 0 / 4,096 | 0 / 0 / 131,072 |
| clicks | 2 / 57,344 / 131,072 | 8 / 229,376 / 131,072 |
| clicks-throttled-quick | 4 / 112,640 / 131,072 | 0 / 0 / 131,072 |
| aq-journeys | 0 / 0 / 84,672 | 0 / 0 / 84,672 |

  The live-SB units' counts vary from run to run (clicks 8 -> 2, clicks-throttled-quick 0 -> 4, sb-5days 2 -> 0) while
  every check on those units passes; 0379 removes only a condition that was false by default, so this is the units'
  own timing, not the patch. The compaction path is exercised in this run (clicks, clicks-throttled-quick,
  mi-throttle-isr). cap_max stays <= 131,072 everywhere.
- No "DOS-PORT memlog" line in any unit (0 lines; 0376 is gone).

## 6. Not done here

- The lockable-mode audio check (sdlports' terms) is the next owed item before 0377 reaches a release; it reads this
  witness's compactions.
- The LOCK_MEMORY finding (ROUNDRO README correction; lab-rb ba9369ec / c8af8810) is a separate, undecided lever.

Files: BUILDS.txt (every build's hashes and stamps), RATCHET-20261112T225932Z-report.txt / -summary.txt.
