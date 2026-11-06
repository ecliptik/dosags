# DIST2 -- the v0.1 zip as shipped, run the way README.TXT says (written 2026-11-06; pre-registration, before any data)
- Binary: DISTV1.EXE = AGS.EXE extracted from build/dist/dosags-v0.1.zip (make dist DIST_VERSION=v0.1 DIST_REPO_URL=https://github.com/
  ecliptik/dosags; zip sha256 c0c6fe00...; check-dist --release PASS) = release c754df64babd (main c284ddfd) byte for byte (sha256
  d680e3b6...), the exe round N7 measured. The zip's CWSDPMI.EXE and OPL3BANK.DAT equal the harness-staged files (checked). VOID if any differs.
- Fixture: DIST1's line verbatim (R4: 5days --startr 3, drive 2, README.TXT's ACSETUP example, --no-fixed-timestep = the release
  default, --no-fine-timing, no direct-framebuffer / backend SETs, TAS 5000, MIN_WAIT 270) + the BLASTER line.
- Witness: STDOUT "vmmode DOSAGS_VM=(default) mode=3" and "englev DOSAGS_ENGLEV=(default) on=1"; BLASTER.TXT "A220 I7 D3 P330 T3"; else VOID.
- PASS = exit 0, room 3, the fixed-timestep log line reads on, "DosMidiBackend: OPL3/OPL2 chip detected", STDOUT music 0 and
  >= 1 "Playing sound" line (any clip: DIST1's "sound 3" proxy is not reused), gatebar.py --label S16 --stamp c754df64babd
  --room 3 MET (both tick figures 39.2-40.8, fps_p50 >= 40, audio counters clean) with the camera sheet CLEAN. Else FAIL.
- Prediction: PASS at about N7S16's figures (39.24 / 40.13, 99.44%); DIST1 (pre-VM) 39.27 / 40.13, 99.56%.
- Round V1 (the v0.1 candidate as shipped): WARMUPV1, DIST2, V1S16, V1S32, V1S8; one power-on, cap 75 min; dated 2026-11-06.
