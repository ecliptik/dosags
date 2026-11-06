# Round G2 -- 2026-11-06: model C PASSES on a real OPL2 and on the MPU (proxy); SDL 0270 FALSIFIED (must not land)

One power-on 03:50:29Z-04:50:15Z (driver; powerguard confirmed), every cell exit 0, stamps matched. Operator's standing order
+ "fix both before v0.1". Pre-registrations 15d8975b (G1's cells re-run with new tags after vcctrl 988d843). Every
--boot-profile selection read 'flushed': True (vcctrl's fix, first live use; GUSS0B's first attempt missed, as in G1, and the
flush cleared it); no "Bad command" anywhere. vcctrl: no USB event, the audio stream never restarted, 4 corrupt video frames
(04:19:32, 04:26:46, 04:31:36, 04:36:19Z -- rising rate), none affecting an audio score.

| Cell | Binary / boot | Validity | capture-check3 | verdict |
|---|---|---|---|---|
| GUSS0B | lab S0 854228747226 (no 0270), PGGUS | ULTRASND 240,3,3,7,7, midi=gus, sound 3 x1, one segment | K1/K4 PASS; K2 FAIL (1.98 s); **K3 FAIL** (0.40 vs null 0.43); M1 -24; M2 0.476 vs 0.603 | as predicted (= G1's GUSS0); underruns 0, gusstreams opens=1 failures=0 reuses=6 |
| GUSS1B | lab S1 2d00e8b416f0 (SDL 0270), PGGUS | ULTRASND, midi=gus, sound 3 x2, one segment, card locked in the span | K1/K4 PASS; K2 FAIL (2.01 s); **K3 FAIL** (0.40 vs 0.43); M1 -24; M2 0.479 vs 0.602 | **FALSIFIED as registered** ("S1 K3 FAIL with S0's"): **SDL 0270 must not land** |
| ADLC16B | release 340584af1155 (ags 0355), PGADLIB, backend auto | BLASTER empty, BACKEND auto, model C line, "say OPL2", pcm=none, midi=opl3 chip=opl2 poll, 4,467 events, music 0 | K1 PASS, **K2 PASS** (0 frames), **M1 +0 cents**, **M2 0.763** vs 0.400 / 0.590; K3 FAIL by design | **PASS** (K1, K2, M1, M2): music right on a real OPL2 with no SB |
| MPUNB16B | release 340584af1155, PGSB, BLASTER cleared, wb (PROXY) | BLASTER empty, BACKEND wb, MPU cold-init ok, model C line, pcm=none, midi=wb poll, 4,467 events | K1 PASS, K2 PASS, **M1 -1 cent**, **M2 0.872** vs 0.394 / 0.730; K3 FAIL by design | **PASS** (proxy: the DSP exists but is never opened) |

Model C PCM timing witness (information): 14 silent clips released from 21 ms early to 104 ms late against their audio
length (registered expectation: never early). One clip ended 21 ms early (ADLC16B tick 89, 332 vs 353 ms) -- a small
model C edge to look at; no script visibly affected.

GUS reading: S0 and S1 are indistinguishable (K3 0.40 vs 0.43 both, the same K2/M1/M2), so the real PicoGUS does not respond to
the 8-bit sign flip the way DOSBox-X does. Either it reads 8-bit unsigned, or the GUS sound effects are not audible on it for
another reason -- D4 (the documented PicoGUS voice start race; REAP_GRACE) is the next suspect. The hub gus-pcm-fix stands
(underruns 0, no voice/DRAM exhaustion). The GUS music (K2 gap, -24 cents, M2) is the gus_sink.c investigation.
