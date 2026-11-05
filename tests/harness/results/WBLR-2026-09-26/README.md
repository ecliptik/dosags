# WBLR -- the 486 confirmation of the WB landing series, round Q
(lab-wb's pre-registration, copied verbatim from ~/git/dosags-lab-wb/docs/lab/wb.md at lab/wb 70d0b711, before any data)
- Binary land3: `~/git/dosags-lab-wb/build/lab/land3c/ags.exe`, sha12 fe1b2285e8f7, build_dirty=0, sha256 8863510a13b73e2b8e0ea786e453bda72776f346817b5ee2cd1c1f427d7e1bbb.
- Fixture = WBLC2's: PGSB, 5 Days own flow, WBF1 env + `SDL_HINT_DOS_AUDIO_WB_RTC_PUMP=1`, --timeout 1200, one wedge budget.
- Valid: midi_tick=rtc, sha12 as above, card locked through W (24.7).
- Pass: A1-A6, c_redrain present, D >= 0.70 at W, screen CLEAN, clean exit. B not re-scored (same pump stream as land1).
- Prediction: A 0/0 (as WBF1/WBF2/WBLC2), c_redrain 70-95, D ~0.72-0.76.
- Void/next: one stuck or late -> second run, no landing; D < 0.70 -> add WBLRP poll control first.
- If ags 0236/0238 (gfx; no shared files) land first, land3 is rebuilt with them and R1 + RO1 re-run before staging.
- Staged (dosags-worker): RUNHW_MIN_WAIT_S=600 (16000-tick auto-exit ~470 s at ~34 ticks/s + load).
