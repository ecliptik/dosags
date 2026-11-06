# V1S32 -- 5 Days S32P (room 3, 32-bit 640x480) on the v0.1 exe, the gate scene's second reading on the shipped build (written 2026-11-06; pre-registration, before any data)
- Binary: DISTV1.EXE = AGS.EXE extracted from build/dist/dosags-v0.1.zip (make dist DIST_VERSION=v0.1 DIST_REPO_URL=https://github.com/
  ecliptik/dosags; zip sha256 c0c6fe00...; check-dist --release PASS) = release c754df64babd (main c284ddfd) byte for byte (sha256
  d680e3b6...), the exe round N7 measured. The zip's CWSDPMI.EXE and OPL3BANK.DAT equal the harness-staged files (checked). VOID if any differs.
- Fixture: GR32P's line verbatim, as N7S32.
- Witness: STDOUT "vmmode DOSAGS_VM=(default) mode=3" and "englev DOSAGS_ENGLEV=(default) on=1"; BLASTER.TXT "A220 I7 D3 P330 T3"; else VOID.
- Bar (PLAN-GATES, unchanged): both tick figures 39.2-40.8, fps_p50 >= 40, completeness >= 95%, screen witness clean, audio
  counters clean; the campaign line 99% displayed. With N7's cell this is the scene's x2 on c754df64babd.
- Prediction: as N7S32 / GR32P (99.52%): displayed 99.3-99.6%, whole-run 39.15-39.40, steady 40.0-40.3.
- REGRESSION: displayed < 99.0%, any audio counter non-zero, or a tick figure out of band.
- Witness: the capture sheet (640x480 locks) or the camera.
- Round V1 (the v0.1 candidate as shipped): WARMUPV1, DIST2, V1S16, V1S32, V1S8; one power-on, cap 75 min; dated 2026-11-06.
