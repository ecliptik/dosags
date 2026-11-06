# GUS backend on the release exe -- findings (2026-11-05, lab; rig evidence GUSC16-2026-11-05)

Not a regression. No change since the 09-15 S7 GUS cells (385676cb) alters what the GF1 plays: the hub GUS files
(gus_pcm_stream.c/.h, gus_sink.c, gus_dram_floor.c) are byte-identical; SDL 0199 and 0269 touch SDL_dosaudio_gus.c
with diagnostics only; ags 0352 removes diagnostics only; ags 0348/0349 return early on GUS; the mixer's GUS pump
branch (vendor/ags/Engine/platform/dos/dos_audio_mixer.cpp:659-680) is unchanged but for a reporting call. The 09-15
cells show no PCM clip played (GUSQ2: only "Playing music 0"; SNDB: midi=none), so their underruns=0 proved nothing.
The one behavioural change on the path is ags 0096 (7d35c007, 09-17): audio pumped ~1/ms while waiting for the
next frame (Engine/ac/timer.cpp:169), which multiplies the underrun counter and would expose D4.

Bugs (all present at 09-15; hub `.sdl-dos-ports/shared/audio/gus_pcm_stream.c` + the engine's finish rule):
- D1 short clips and clip tails never play: gus_pcm_stream.c:109 uploads only full 4,096-byte chunks; every clip
  loses (len mod 4096) bytes (sound 3: 1,757 B); clips < 4,096 B (every 5 Days footstep) never start.
- D2 channels never finish: the unsent tail keeps IsEmpty() false (openalsource.cpp:48 via dos_audio_mixer.cpp:425),
  so AudioPlayer::Poll (audioplayer.cpp:355) never ends the clip; each pump past the last half adds one underrun
  (gus_pcm_stream.c:310) -- the 39,631 is stuck streams x pump calls, not audible dropouts.
- D3 SFX voices and GF1 DRAM leak: gus_pcm_stream_close (:336) frees the voice only if the stream started; each
  never-started short clip leaks one of the 5 SFX voices (after five, all later PCM is silent) and each failed open
  still allocates 8 KB of DRAM and raises the floor (:165, :180 before the voice allocation at :182).
- D4 (hypothesis, rig only): SDL_dosaudio_gus.c:161-171 documents a PicoGUS start race (a just-started voice reads
  "stopped"); its guard (SDL_HINT_DOS_GUS_REAP_GRACE) is off by default and SDL_DOSGusVoiceActive (:1102-1124) shares
  it. With 0096's ~1 ms polls the stream would skip half-buffers (simulated: 1,116 of 1,486 ms of sound 3 audible).

Reproduction: 86Box (v5.3, ap5s, GUS 240h/5/1, 1 MB) passes the GF1 probe and dispatches GUS MIDI; the counters
reproduce with both binaries (today's a1dba5d61624: 8,481 in 129 s; the 385676cb tree: 486 in 135 s at ~9 fps), with
the rig's stuck-channel signature (a repeated sound goes to a new channel). 86Box plays no audio from our driver
(Gravis's own ULTRINIT + PLAYFILE is audible) -- not investigated. A host simulation of the unchanged hub
gus_pcm_stream.c (stub GF1) confirms D1-D3 and the pump-rate scaling. Lab files: build/ws/gusbisect/ (untracked),
worktree ~/git/dosags-lab-gus.

Not determined: K3 (sound 3 absent from the capture: D1-D3 predict ~1.49 s should play; D4 could explain it); the
music's 1.02 s gap (one zero-event MIDI window and a 359 ms main-loop stall at tick 2404 in the rig log; no GUS MIDI
code changed); M1/M2 (pre-registered as patch-set differences).

Fix direction (hub change, review first): flush a padded tail when the source is done (D1/D2); free the voice on
close whether or not it started, and allocate the voice before uploading (D3); then test D4 on the rig
(REAP_GRACE, and the old binary build/ws/gusbisect/bin/old385676cb.exe sha256 253bb58b... as a control).
