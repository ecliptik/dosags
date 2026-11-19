# RM0380-2026-11-13 -- landing record for ags 0381 (removes 0380 whole; the operator keeps both heap switches off)

Build host only; nothing here touched the rig. Branch `rm0380` (worktree dosags-ring) on main 6e4dbcfa (round RQ's results).

- Decision (operator 2026-11-13, via sdlports, after ROUNDRQ-2026-11-13): keep DOSAGS_HEAP_UNLOCK and
  DOSAGS_HEAP_PREGROW_KB off; revisit only if room-load time becomes a goal. 0380's own message stated the path taken here:
  an exact revert if neither switch became the default. Option (b), keeping the switches as diagnostics, was not taken: no
  concrete next use (the lab's 9001 / 0380 and git history restore the lever if it is ever wanted).
- 0381 is `git revert` of 0380 in the vendor series. After `make patches` (0001-0381) the AGS tree is
  d90feab04c8483116219ea5d5e41bf35b872cb5d, the same tree as 0001-0379.
- Clean build (build/ags + build/ags-release wiped), build_dirty 0, stamp e5623c99f752:

| flavour | sha256 | bytes | = 0379 (RMDIAG-2026-11-13) |
|---|---|---|---|
| instrumented | 1d8252a6f29da486d8fb0ee2367309925c3f8caeecd0fdc2476c19915173b853 | 8,707,701 | yes |
| release | 2191042b343cfd66b9e01d09da100362af15b693fcf7019911a22eee9e87f728 | 8,669,559 | yes (stamp d5c8fe52808a) |

- Ratchet: not re-run -- the binaries are byte-identical to 0379's, which passed ratchet 20261112T225932Z at the limits
  restored here (exe-bytes 8707701, code-lock-bytes 5228512; tests/ratchet.yaml LIMIT comment).
- The round RP audio check (ROUNDRP-2026-11-13) ran on this exact release binary, so it stands for the 0381 series.
