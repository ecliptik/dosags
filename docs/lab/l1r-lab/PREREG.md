# LAB-L1R pre-registration (2026-11-08, written and committed before any lever data; lab only, DOSBox-X fixed 40k)
- Lever: DOSAGS_ROUTE_PREWARM=1 runs the legacy finder's unchanged is_route_possible() once (0211 analysis + 0319 labels)
  on prepare_walkable_areas(player) when the FadeIn event is processed (after BeforeFadein, so after a room load and a
  save restore, inside the stall tick). Per-request validation (serial / byte compare) is untouched. Unset/0 = off.
- G1 frames: FHASH + PRESENT_VERIFY EQUAL on vs off on every loop counter of G, V, GCL, H, intro, AQ (every tick rendered,
  RANDSEED=1). G2 release game lines EQUAL on vs off: 5 Days room 3, Trilby room 35, AGS Quest. Falsifier: any DIFF.
- C1 control (stale warm: cache built from a mask with a block cut out, stamped with the current serial): H must DIFF.
- F1 forced guard (a 10x9 unwalkable block drawn on the walkable mask + gen bump right after the warm): on vs off EQUAL,
  first request after it a rebuild (first_miss >= 1); F1-NOGUARD (cache re-stamped after the change): H must DIFF.
- T1 timing (H, --fixed-timestep, fine timing on): FindRoute at 6154 62 ms off -> <= 8 ms on; at 7895 182 -> <= 15 ms;
  both first requests serial hits (first_serial 2, first_miss 0). Restore tick +45..70 ms, room-2 entry tick +150..190 ms.
  Entry-window skips after 7895: 5 -> <= 1. Falsifier: 6154 > 15 ms, 7895 > 30 ms, or first_miss > 0 without forcing.
- 486 (not run here): LAB-RB section 7 stands -- per pair -6 skips (3-9) in room 1 + entry, +0.09 points (0.04-0.13).
