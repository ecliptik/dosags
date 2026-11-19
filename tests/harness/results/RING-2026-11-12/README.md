# RING-2026-11-12 -- landing records for ags 0377 (bound the mixer voice ring)

DOSBox-X only. Branch `ring` on local main 64128ecd (series 0001-0373 + 0376) + patches/ags/0377. The cause and the
lab verification: lab-rb docs/lab/move-lab/rj/rm (LAB-RING.txt: the owner; LAB-RING377.txt: this patch). Nothing here
touched the rig.

## 1. The patch

- 0049's per-voice ring dropped its consumed prefix only when fully drained. With a live SB, a looping voice (MMD room
  2's ambient sound 96) never drains, so the vector grew ~22 KB/s with 2x reallocations: the 486's room-2 freezes.
- Fix: amortized compaction at the single writer (dos_audio_mixer_voice_write): once read_pos >= 64 KB, erase the
  consumed prefix (memmove of <= 32 KB unread). Readers untouched. Capacity <= 192 KB per voice (128,000 B measured).
- TEMPORARY switch DOSAGS_RING_LEGACY=1 (env allowlist, read once): the old growth, for the rig ABBA's legacy arm; a
  separable hunk (dos_ring_legacy(), its term in the compaction condition, "legacy=" in the witness, the allowlist
  line). Removal owed after that round.
- Witness: `DOS-PORT voicering legacy= compact_at= compactions= moved_bytes= cap_max=` in RUNMANI.LOG.

## 2. Builds (two clean builds per flavour, build/ wiped before each round, make patches first)

`make patches` applies the series cleanly (fingerprints 59d4f9603b9f / c4dd0995e971). `make build-dirty`: 0 for both.

| flavour | sha256 | stamp_sha12 | bytes | vs 0376 (main) | round 1 == round 2 |
|---|---|---|---|---|---|
| instrumented | 8862f42481323db2d9d10f5a6c5c1e9d7c72e24bac9076051e2f3b057f87df03 | 7e19b2963a3f | 8,710,146 | +796 (ff560ae548b8, 8,709,350) | yes (cmp) |
| release (DOSAGS_RELEASE=1) | ce8d275f0602e5ce857f2237edb86517619d9170492928951f99659ce2a1e888 | 93df50d751a8 | 8,671,492 | +796 (2725928f2e37, 8,670,696) | yes (cmp) |

Sections against 0376 (objdump -h): .text +512 in both flavours; .data +0; .bss +0.

## 3. Ratchet

`.sdl-dos-ports/shared/tools/ratchet.sh --root <ring> --no-build --no-host-wait --capture-display 398 --no-record`.

| run | result |
|---|---|
| 20261112T095514Z (RATCHET-20261112T095514Z-*) | 39 pass (10 improved, the same 10 as MEMLOG / CAP3R), **2 fail, both the expected size checks**, 4 quarantined. exe-bytes 8710146 > 8709350; code-lock-bytes 5230400 > 5229840 |
| proposed limits (exact; tests/ratchet.yaml LIMIT comment) | **exe-bytes 8710146, code-lock-bytes 5230400** (+796 / +560 on 0376's) |

The live-SB units print the witness: sb-5days `compactions=2 moved_bytes=57344 cap_max=131072` (5 Days' voices
compacted too), mi-throttle-isr 2 / 55,296 / 131,072, mi-stall-isr 0 / 0 / 131,072.

## 4. Smoke (agsquest, the autopilot, fixed40k, --fixed-timestep; SMOKE-i / SMOKE-r)

- Both flavours exit 0. The RUNMANIFEST block (21 lines) has the same keys in the same order as main's 0376 smoke
  (MEMLOG-2026-11-11 SMOKE-off). Against it only binary_sha12, started_utc, fps_p50 (7.36 vs 7.35) and two timing
  counters inside audio_vital_status (skipped_silent 3545 / 3547, clk 3056 / 3055) differ.
- With digits masked, the instrumented log has the same shape as 0376's plus one line:
  `DOS-PORT voicering legacy=0 compact_at=65536 compactions=0 moved_bytes=0 cap_max=84672` (-silent: the SB plays
  nothing, so no voice outgrows a compaction here; the live-SB proof is in LAB-RING377.txt and the ratchet units).
