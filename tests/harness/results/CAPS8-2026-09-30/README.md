# CAPS8 -- S8 capture check at 640x480, round BATCH (lab/wb caff563d LAB-WB-data/readmes/CAPS8-README.md; written 2026-09-29, pre-registration, before any data)
- Binary (amended 2026-09-29, before any data): main 553588d4 (62c06f3e + ags 0347), stamp 8249193ed041, build_dirty 0, sha256
  60b461ab57321ec1bf90b9dd162d4d46237e169182af3ec25fb7da1460f29777, 8,668,939 B, staged as mainb.exe; VOID if the staged stamp differs.
- Fixture: round S8M's GM8A line verbatim (trilbysnotes --startr 35, drive 3 = walk 25 2 80, OPL3 on PGSB, direct framebuffer, TAS 5000,
  --no-fine-timing, --env DOSAGS_MSGSKIP=1, --timeout 1800) EXCEPT the capture mode: S32P-ACSETUP-ON.CFG:ACSETUP.CFG (24d874f2...)
  + --env DOSAGS_MAX_SCALE=1 (640x480 centred 1x, which the dongle locks). RUNHW_MIN_WAIT_S=300. Audio only.
- Valid only if: stamp, build_dirty 0, room 35, exactly one "DOS-PORT msgskip n=1", STDOUT logs sound 11, ambient sound 18, music 9
  and 4, manifest complete, exit 0, card locked through the span.
- Scorer (committed before data; caff563d = c81170d7's logic): capture-check.py CAPS8-seg01.ogg CAPS8/RUNMANI.LOG
  build/lab/renders/trilby_sound11.wav. PASS = K1-K4 PASS + K5 counters meet the gate bar's audio line; K5 reads silent_irqs under
  0347 (dropouts only), start_latency_irqs reported, not part of K5.
- Prediction (lab-wb): K1-K4 PASS at the WBD8R/WBD8P figures; counters clean. DOSBox-X CAP8B on this binary: silent 0, latency 0.
- Round BATCH ("Batch after 0347 lands"): warm-up, CAPS8, GL16, GL32, GL8, WBC16; one power-on; dated 2026-09-30, else re-dated first.
  The capture (game music) stays local; its sha256 goes in AUDIO-SHA256.txt.
