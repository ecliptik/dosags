# V1S8 -- Trilby's Notes S8 (room 35) on the v0.1 exe, the gate scene's second reading on the shipped build (written 2026-11-06; pre-registration, before any data)
- Binary: DISTV1.EXE = AGS.EXE extracted from build/dist/dosags-v0.1.zip (make dist DIST_VERSION=v0.1 DIST_REPO_URL=https://github.com/
  ecliptik/dosags; zip sha256 c0c6fe00...; check-dist --release PASS) = release c754df64babd (main c284ddfd) byte for byte (sha256
  d680e3b6...), the exe round N7 measured. The zip's CWSDPMI.EXE and OPL3BANK.DAT equal the harness-staged files (checked). VOID if any differs.
- Fixture: R1R1's S8 line verbatim, as N7S8 (MSGSKIP=1, drive 3).
- Witness: STDOUT "vmmode DOSAGS_VM=(default) mode=3" and "englev DOSAGS_ENGLEV=(default) on=1"; BLASTER.TXT "A220 I7 D3 P330 T3"; else VOID.
- Bar (PLAN-GATES, unchanged): both tick figures 39.2-40.8, fps_p50 >= 40, completeness >= 95%, screen witness clean, audio
  counters clean; the campaign line 99% displayed. With N7's cell this is the scene's x2 on c754df64babd.
- Prediction: N7S8 99.32%, R1R1 / R1R2 99.48 / 99.44%: displayed 99.3-99.6%, steady 40.1-40.3. If below 99.4% again, S8's small drop on the VM build is recorded as real (both readings), not a regression unless < 99.0%.
- REGRESSION: displayed < 99.0%, any audio counter non-zero, or a tick figure out of band.
- Witness: the camera sheet (room 35 is dark -- compare N7S8 and GL8A).
- Round V1 (the v0.1 candidate as shipped): WARMUPV1, DIST2, V1S16, V1S32, V1S8; one power-on, cap 75 min; dated 2026-11-06.
