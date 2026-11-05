# WBLR2 -- round R WB cell (lab-wb's pre-registration, docs/lab/wb.md at lab/wb 306c51a5, before any data)
- Binary (coordinator 2026-09-26): land4 = main 5ca997b3 + the WB series, binary_sha12 e11030a21286, build_dirty 0, sha256 23793dfc18e28ab63553f162336f6ac2de9dc7effcc31c0db50281449dad329c (T1/TO1 PASS). Lab-wb's lines below name land3 fe1b2285e8f7; per the coordinator they apply to land4, whose stamp replaces land3's here.
- WBLRP: land4 e11030a21286, WBLR's exact fixture and env + `DOSAGS_MIDI_TICK=poll`; valid if midi_tick=poll, card locked through W.
- 38's table applied to (WBLR, WBLRP) as registered, unchanged by 24.8. The margin m = D(WBLR) - D(WBLRP) is recorded.
- WBLR2 (re-registered 2026-09-26 under the ORIGINAL bar, before any data): land4, WBLR's exact fixture and env.
  Pass = A1-A6 + c_redrain + **D >= 0.70** at W + B against WBLRP at min(W) + screen CLEAN + clean exit -> **land**.
  D < 0.70 with the rest passing -> a genuine-pass miss is possible (~6%): re-run, per the operator; no landing on it.
- Predictions: WBLRP D 0.53-0.62; WBLR2 A 0/0, D 0.70-0.76, B chroma >= 0.95.
- Void: wrong midi_tick, a card unlock inside W, or a sha12 mismatch.
- Staged (dosags-worker): RUNHW_MIN_WAIT_S=600 (16000-tick auto-exit ~470 s + load); --timeout 1200; one wedge budget; WBLRP first.
