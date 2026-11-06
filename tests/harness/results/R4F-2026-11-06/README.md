# R4F -- round C4, release trio R4C, arm 0x3F all six (written 2026-11-06; pre-registration, before any data)
- Binary: VM3REL.EXE (round E's: stamp 1781fe2bf36c, build_dirty=1, 8,636,327 B, sha256 0ade9355a9bb...); VOID if it differs.
  A superinstruction a mask turns off is never installed and never executes, so it takes no cache.
- Fixture: F1MMDK's line verbatim, as round E's VM3B cells, + DOSAGS_VM=fast + DOSAGS_VM_FUSE=<mask>: R4F 0x3F (all six),
  R4B 0x03 (farcall + localload only), R4N 0x00 (fusion off). Witness: BLASTER.TXT; RUN.BAT's SET line and STDOUT's "vmfuse
  mask=0x.." must name the arm's mask, else VOID (env_block_sha is the same in all three). gatebar.py --label MMD --stamp 1781fe2bf36c --room 50.
- Fixed 40k (AGSVM4, measured): 0x3F 4.308, 0x03 4.556, 0x00 5.009 ms/tick; 0x03 drops ~1.1-1.5 KB of EXECUTED superop code for
  +0.248 fixed ms, 0x00 all ~2.4 KB for +0.701. Model: displayed = (25 - logic)/9.04 + 0.033; round E r = 0.50 (0.39-0.61).
- H-CPI (cache does not matter): R4F 91.0-92.0%; R4B = R4F -1.1 to -1.7 points; R4N = R4F -3.0 to -4.7; all steady >= 39.2.
- H-cache: R4B >= R4F - 0.3. FALSIFIER of the cache hypothesis: R4B - R4F <= -1.0 point; between -1.0 and -0.3 inconclusive.
- Audio counters clean, else VOID. x1 each: a mechanism test, not a KPI claim. Release cells decide the KPI, the P4 cells the
  mechanism; if they disagree, report both and claim neither.
- Order: WARMUPC4, R4F, P4B, R4N, P4F, R4B, P4N (~11 min each).
- Round C4 (PLAN-FPS lever V, slice-3 cache test): one power-on, cap 90 min; dated 2026-11-06.
