# S5 WaveBlaster -- real-hardware confirmation, HW-486-66, 2026-09-13

Two independent cells against AGS Quest, `SDL_HINT_DOS_AUDIO_BACKEND=wb`,
staged via `tests/harness/run-rig.sh agsquest --env SDL_HINT_DOS_AUDIO_BACKEND=wb`.
Same staged binary both times (`binary_sha12=b5af4b212659`).

## Cell 1 -- S5WB1 (correctness/dispatch only)

`S5WB1.LOG` / `S5WB1-STDOUT.TXT`. No audio capture running (this cell's
own agent crashed mid-write-up on an unrelated API error before spectral
polling was set up -- raw evidence recovered from `/tmp` and independently
re-verified from scratch by the coordinating session before anything
below was written).

- 18/18 phases + optional `dialog` `ok` (`chosen=14`, "Leave"), `exit_code=0`.
- `audio_vital_status=pcm=sb@11025m16,voices=8,underruns=0;midi=wb,events=170`
  -- zero PCM regression (identical device string/underruns to the existing
  PGSB baseline), real wb dispatch (170 events, non-zero).
- `STDOUT.TXT`: `DosMidiBackend: WaveBlaster/MPU-401 cold-init succeeded
  (ran before the PCM device opened, as required)` at boot,
  `DosMidiBackend: WaveBlaster/MPU-401 backend active` at the audio phase.
- Screenshots byte-identical to the existing baseline (see cell 2's hashes
  below -- both cells produced the exact same three files).

## Cell 2 -- S5WB2 (same cell, plus continuous spectral capture)

Run BEFORE touching the rig for this cell: `prediction.md`, written from
the tune's own raw MIDI note sequence, before any poll data was seen.

`S5WB2.LOG`, `STDOUT.TXT`, `AUTOPLT.LOG`, `PH0{1,2,3}.BMP`,
`audio-poll-raw.jsonl` (`poll-audio.sh` producing it),
`analyze-audio-poll.py` + `audio-poll-analysis.txt` (its output).

Results: **byte-for-byte identical to cell 1** in every field that should
be deterministic -- `binary_sha12`, `duration_s=608`, `fps_p50=8.57`/
`fps_p95=9.62`, `audio_vital_status=...;midi=wb,events=170`, `exit_code=0`,
`dialog chosen=14`, and all three screenshot sha256 hashes
(`9f9d9bd9...`/`6051787...`/`5b98f4da...`, matching the pre-existing
S2/S4 baseline exactly -- zero regression from wb across two independent
runs).

### The spectral capture -- real, audible WaveBlaster output confirmed

`vcctrl level`/`spectrum` polled every ~3.5s for the whole run (this
session's own script, `poll-audio.sh`, modeled on S4MIDI1's methodology
but using the JSON-returning `vcctrl level`/`vcctrl spectrum` commands
directly rather than the text-formatted `vcctrl-audio` CLI).

**Ambient floor, matching S2/S4 precedent on this exact rig**: mean_db
~-67 to -69dB, 0/8 active bands, for the entire run except one window.

**The window** (`t=708.3` to `t=779.0` in this poll's own elapsed-time
reference, ~71s duration): mean_db jumps from ambient -67dB to as strong
as **-22.8dB** -- a ~44dB departure -- with 3-6 of the 8 octave bands
active simultaneously (vs. 0 at every other sample in the run), then a
clean return to the established ambient floor. This is unambiguous: real,
loud, sustained audio was captured by the rig's line-in during exactly
the window the `audio` phase's own MIDI tune should be playing.

**The pre-registered band prediction was wrong about WHICH bands, right
about the headline question.** `prediction.md` predicted the melody's raw
fundamentals (C4-G4, 261.6-392.0 Hz, all falling in the 200-400Hz band)
would dominate, since `waveblaster_sink` does no OPL3-style transpose
(unlike S4's DMXOPL path, which put C3/D3-G3 across two bands after a
-12 semitone shift). The ACTUAL dominant energy landed one to two octaves
higher, in the 400-800Hz and 800-1600Hz bands. This is explained, not
hand-waved: GM program 80 ("Lead 1 (square)") is a harmonically bright,
odd-harmonic-rich voice, and the notes' own 3rd harmonics (784-1176 Hz for
this melody) land almost exactly where the real energy showed up. A real
GM wavetable/sampled square-lead patch commonly carries more energy in its
upper harmonics than a napkin sine-wave model predicts -- the prediction's
method (map fundamentals to bands) was reasonable given available
information, and the miss is a genuine, reportable finding about this
voice's real timbre, not a mistake to bury.

**This also resolves the audio-routing question raised before the
cell**: `README.TXT`'s DreamBlaster section documents a one-time
`MIXERSET.EXE` unmute step for the `VIBRA` profile's Vibra16S mixer, but
says nothing about an equivalent step for `PGSB`/PicoGUS's own WB-header
audio return. The capture proves none is needed here -- the DreamBlaster
S2's real analog output reaches the rig's line-in cleanly under the stock
`PGSB` boot profile, no extra step, no profile switch.

## What this closes out for S5

- Hub hoist (`shared/audio/waveblaster_sink.{c,h}`) + DOSBox-X validation:
  done previously (see PLAN.md's own "S5, WaveBlaster hub hoist +
  DOSBox-X validation" section).
- Real-hardware correctness (acceptance-1-equivalent for wb): done, this
  write-up, both cells.
- Real-hardware acoustic confirmation: done, this write-up, cell 2's
  spectral capture.
- Decision 7 (operator listen): RESOLVED, asked fresh (not assumed to
  carry forward from S4's own waiver) -- the operator confirmed the
  spectral evidence above satisfies decision 7 on its own, same
  resolution S4 reached. No raw audio file was needed.
- GUS: untouched, separate slice.

## A real, unrelated incident during this investigation

The first attempt at cell 2 (implementing agent, "S5WB1" + write-up) was
killed twice by a spurious API content-policy error (`[bio]` tag) while
reading its own plain technical log output -- unrelated to anything
sensitive in this task. The coordinating session recovered the raw
pulled files from `/tmp` (the crashed agent's own OUT_DIR, never
committed) and independently re-verified every claim in this write-up
against those raw files and a freshly-run second cell, rather than trust
the crashed agent's own narrative.

Separately, cell 2's own result collection hit the already-documented
"Scroll Lock did not clear, so the reboot did not happen" vcctrl quirk
(same one S4MIDI1 hit) -- confirmed via a live `vcctrl shot` showing the
machine already sitting at a clean `C:\DOSAGS>` prompt, recovered via a
plain retry of the `get-file` pull (no reboot needed), succeeding
immediately -- same recovery this quirk has had every prior time.
