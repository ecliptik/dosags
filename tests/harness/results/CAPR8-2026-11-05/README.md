# CAPR8 -- S8 capture check at 640x480 on the RELEASE flavour, round R1 (written 2026-11-05; pre-registration, before any data)
- Operator 2026-11-04, option (a): the release build's end-to-end audio check at S8 -- CAPS8's protocol on the release exe.
- Binary: rel.exe = build/ags-release/ags.exe (main f2228d5e, DOSAGS_RELEASE=1, step 1b + ags 0354), a1dba5d61624, build_dirty 0,
  8,598,425 B, sha256 1fc012c16d41.... VOID if the staged stamp differs.
- Fixture: CAPS8's line verbatim (build/ws/roundBATCH/CAPS8.ARGS: the GL8 line but S32P-ACSETUP-ON.CFG (24d874f2...):ACSETUP.CFG +
  DOSAGS_MAX_SCALE=1, 640x480 centred 1x, MIN_WAIT 300) + the BLASTER line.
- Witness: BLASTER.TXT (RUN.BAT `ECHO %BLASTER% > BLASTER.TXT` before AGS.EXE, --collect) must read "A220 I7 D3 P330 T3" stripped
  (profiles/dosags.yaml profile_witness), else VOID. Camera sheet first; capture STALE reported (stick dropouts 11-04 18:23-18:37 PST).
- Valid only if (as CAPS8): stamp, build_dirty 0, room 35, one "DOS-PORT msgskip n=1", STDOUT logs sound 11, ambient 18, music 9 and 4,
  manifest complete, exit 0, card locked through the span.
- Scorer: capture-check.py (archive/lab-wb-2026-11-04 LAB-WB-data/ = lab/wb caff563d, sha256 33133f390a4b...) CAPR8-seg01.ogg CAPR8/CAPR8.LOG
  build/lab/renders/trilby_sound11.wav (3951702f...). PASS = K1-K4 PASS + K5 meets the gate bar's audio line. No pitch claim at S8.
- Comparison: CAPS8 on 8249193ed041: K1 0 zero frames, K2 worst 24.7 dB, K3 NCC 0.41 vs null 0.14, K4 >= 52.8 / 47.8 dB, K5 clean.
- Prediction: PASS at about CAPS8's figures (REL1: the scorer reads a release manifest identically). Capture stays local; sha256 recorded.
- Round R1: WARMUPR1, R1I1, R1R1, R1R2, R1I2, CAPR8; one power-on, cap 80 min; dated 2026-11-05, else re-dated first.
