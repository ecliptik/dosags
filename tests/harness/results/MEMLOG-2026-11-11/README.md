# MEMLOG-2026-11-11 -- landing records for ags 0376 (DOSAGS_MEMLOG, TEMPORARY diagnostic)

DOSBox-X only. Branch `memlog` on local main f3147823 (series 0001-0373) + patches/ags/0376. Lab history and the
diagnostic's question: lab-rb, docs/lab/LAB-MOVE.md 10.19-10.21. Nothing here touched the rig.

## 1. The patch

- 0376 is the slot (main ends at 0373; 0374 cap3 and 0375 hitchdiag are reserved). Subject without "provisional".
- Code comment: a TEMPORARY diagnostic whose removal is owed (removed once the freeze cause is named, or together
  with 0375's removal), wrapped to the file's comment width (~75 columns).
- **Changed since the lead's review:** the 512-entry ring (24 KB) is malloc'ed at the first sample, only when
  DOSAGS_MEMLOG=1, instead of a static array. The static array put 24 KB in .bss, which this toolchain's exe carries
  in the file: +26,967 B instrumented over 0373 (later sections shifted by 0x6800), and 24 KB of every run's memory,
  release included, with the diagnostic off. A failed malloc leaves the diagnostic off; the emit hook returns unless
  on == 1, and every ring write is under on.

## 2. Builds (two clean builds per flavour, build/ wiped before each round, make patches first)

`make patches` applies the series cleanly (fingerprints 59d4f9603b9f / 8c0ca6b28491); vendor/ags head 09baaa5f, tree
2c27302a728a. `make build-dirty` after the second round: build_dirty=0 for both flavours.

| flavour | sha256 | stamp_sha12 | bytes | vs 0373 | round 1 == round 2 |
|---|---|---|---|---|---|
| instrumented | 448e6d155c36a392c7beee07d04ca1fcf297517b9f0fc62a5f8801982bdfe848 | ff560ae548b8 | 8,709,350 | +2,391 (39abbc4b5c34, 8,706,959) | yes (cmp) |
| release (DOSAGS_RELEASE=1) | b221866b9a2a0104945a0599b1442f3403548ff42e9820e9ecba7e5de022649a | 2725928f2e37 | 8,670,696 | +1,879 (942ad0260d36, 8,668,817) | yes (cmp) |

Sections against 0373 (objdump -h): .text +1,536 in both flavours; .data +512 instrumented, +0 release; .bss +0.

## 3. Ratchet

`.sdl-dos-ports/shared/tools/ratchet.sh --root <memlog> --no-build --no-host-wait --capture-display 398 --no-record`
(as pace ran it for 0374), on the builds above. Game packages copied from the cap3 worktree (gitignored; byte-equal).

| run | result |
|---|---|
| 20261112T031935Z (RATCHET-20261112T031935Z-*) | 39 pass (10 improved), **2 fail, both the expected size checks**, 4 quarantined. exe-bytes 8709350 > 8706959; code-lock-bytes 5229840 > 5228176. The same 10 improved as CAP3R's 20261112T012145Z |
| proposed limits (exact, no headroom; tests/ratchet.yaml, LIMIT comment) | **exe-bytes 8709350, code-lock-bytes 5229840** (+2,391 / +1,664 on 0373's) |

An earlier run (20261112T031349Z) ERRORed every check: the new worktree had no game packages. Not a result.
The limits are measured on 0373 without 0374: if 0374 lands first, re-measure on the combined series. When 0376 is
removed, the limits return to 0373's.

## 4. Smoke (agsquest, the autopilot, fixed40k, --fixed-timestep; SMOKE-*.RUNMANI.LOG / RUN.BAT)

| cell | exe | DOSAGS_MEMLOG | exit | RUNMANI lines | memlog lines |
|---|---|---|---|---|---|
| on | 0376 instrumented ff560ae548b8 | 1 | 0 | 492 | 105 (header + 104 rows) |
| off | 0376 instrumented ff560ae548b8 | unset | 0 | 387 | 0 |
| b373 | 0373 instrumented 39abbc4b5c34 | 1 (unknown to it) | 0 | 387 | 0 |
| rel | 0376 release 2725928f2e37 | 1 | 0 | 337 | 105 (header + 104 rows) |

- The RUNMANIFEST block (BEGIN..END, 21 lines) has the same keys in the same order in all three. Against b373 only
  binary_sha12, started_utc and fps_p50 (7.36 vs 7.35) differ; env_block_sha is equal (DOSAGS_MEMLOG is not in the
  env allowlist; its witness is the memlog header line itself).
- The memlog lines follow `DOS-PORT memory_min_free_kb=158640` (line 22): header on line 23, rows 24-127. With the
  memlog lines removed and digits masked, the on cell's log has the same shape as off's (0 diff lines).
- Rows: lc 42 / ms 5615 to lc 3675 / ms 195253; host 0.90 flags 0x5, phys 11,916 pages, free 8,604 -> 6,892,
  swap 32,768, 23-24 us per call; the last row's largest_kb (158,640) equals memory_min_free_kb.
- The release flavour (cell rel, added for the round design: the no-swap ABBA runs the release build) prints the same
  memlog block after `memory_min_free_kb` (line 22 / 23), keeps the click journeys and persec records the clock-step
  witness reads, and its RUNMANIFEST block has the same keys as the other three.
- Clock note: a memlog row's `ms` is get_runtime_ms() (AGS's game timer, its own zero); journey t_ms and persec ms are
  uclock since engine start. Rows line up with the journeys through `lc`, via persec's tick per engine second.
