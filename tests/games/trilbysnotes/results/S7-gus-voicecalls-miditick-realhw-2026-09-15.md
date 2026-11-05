# S7-GUS -- GUS voice-setup call + midi_sched_tick() call-site cost, real-hardware result: all six exonerated, new source-verified candidate found -- 2026-09-15 (new session, continued)

Operator-approved cell (tag `GUSV1`, `binary_sha12=760ec38b22ea`, the
patches SDL/0146 + ags/0070 + ags/0071 build). Continuation of
`S7-gus-voicecalls-miditick-dosboxx-2026-09-15.md`'s own DOSBox-X pass --
this is the real-hardware measurement.

## A third harness gap: the "proven" manual boot workaround needed real-time recalibration this session

`run-rig.sh --boot-profile 3` failed a third time (`select_boot_profile ->
None`), same already-documented gap. More significantly, the manual
LED-edge boot-profile workaround itself -- which landed cleanly on
`PGGUS` on the FIRST attempt in both `GUST1` and `GUSD1` -- did **not**
transfer cleanly this session. Two live attempts using the previously-
recorded ~25s capslock-edge timing (one via LED polling, one via live
screenshot polling) both landed on the wrong menu default (`PGSB`, not
`PGGUS`), confirmed via independent screenshot each time
(`[PGSB] ready.` with stray `3` echoes -- the same harmless residue
`GUST1` already documented, just landing on the wrong profile this time).

Recovered by recording a full video of a third failed boot and
extracting frames via `ffmpeg`: the CONFIG.SYS text menu itself never
produces a stable, capturable video frame on this rig (a real VGA
sync-loss during that specific mode) -- capture goes straight from black
to "menu already resolved to PGSB," which is why blind LED/screenshot
polling alone could not catch the actual decision window. Derived a
tighter timing empirically from the recording (menu resolves ~35.5s
after `ctrl+alt+delete`, not the ~25s this investigation's prior two
cells both saw) and fired the keystroke burst blind at trigger+27-32s on
a fifth attempt -- landed cleanly on `PGGUS`
(`Running in GUS mode on port 240`, `[PGGUS] ready.`).

**This is new information worth flagging explicitly**: the manual
workaround is not the fully deterministic, session-independent protocol
the last two cells' "worked first-try both times" made it look like --
its timing appears to drift, and this session needed active
recalibration (video capture + frame extraction) rather than reusing the
previously-recorded constant. Still flagged, not fixed, per the same
scope boundary as before (`vcctrl`'s own `select_boot_profile()` --
this project's own tool, in scope to fix properly, but a good candidate
for its own focused session rather than another blind timing-constant
guess here).

An earlier `send-file --return` job again showed this investigation's
now-familiar low-severity pattern (the local `run-rig.sh` process killed
by the environment under memory pressure without affecting the
rig-side job) -- recovered the same way as before, via direct
`vc file-status` polling. All 7 result files verified byte-for-byte via
`get-file --return` + sha256 round trip.

## Result

```
exit_code=0
audio_vital_status=pcm=gus@11025m8,voices=8,underruns=0;midi=gus,events=76
STDOUT.TXT: DosMidiBackend: native GF1 (Gravis Ultrasound) backend active
DOS-PORT tick_rate=9.36 frames_skipped=165
DOS-PORT audioprb total_calls=68 window_calls=68 slots_us(min=67 mean=101588 max=6891495) pump_us(min=50 mean=58 max=113) regwrite(calls=0 min_us=0 mean_us=0 max_us=0) gusscan(calls=28 min_us=27 mean_us=109 max_us=170) voicefreq(calls=28 min_us=10 mean_us=11 max_us=15) voicevol(calls=66 min_us=27 mean_us=29 max_us=35) voicepan(calls=28 min_us=8 mean_us=9 max_us=11) voicestart(calls=28 min_us=44 mean_us=46 max_us=54) voicestop(calls=13 min_us=11 mean_us=11 max_us=14) miditick(calls=20 min_us=20 mean_us=567 max_us=3602)
DOS-PORT tickfx total_calls=36 window_calls=36 catchup_n_sum=163 catchup_us(min=15 mean=166927 max=4013841) realtick_us(min=5600 mean=376052 max=7032697) catchup_yield(switches=0 min_us=0 mean_us=0 max_us=0) realtick_yield(switches=0 min_us=0 mean_us=0 max_us=0)
```

`audio_vital_status` confirms real GUS MIDI dispatch (`midi=gus,
events=76`, zero underruns), `STDOUT.TXT` shows two `PlayMusic` calls
(room -10, then room 1) before the GF1 backend confirmation line, clean
shutdown, `exit_code=0`.

## Verdict: all six newly-bracketed candidates exonerated -- a third independent confirmation of the exact same outlier, and a strong new lead

**`slots_us` max = 6,891,495us** -- a third independent confirmation of
the same ~6.89s single-call outlier, within ~1100us of both prior
measurements:

| Run | slots_us max (us) |
|---|---:|
| `GUST1` (2026-09-14) | 6,890,560 |
| `GUSD1` (2026-09-15) | 6,890,385 |
| `GUSV1` (2026-09-15) | 6,891,495 |

A spread of 1110us across three independent runs on two different
binaries, out of a 6.89-SECOND quantity -- this is now conclusively a
deterministic, reproducible mechanism, not noise.

**None of the five voice-setup calls come close**: `voicefreq` max=15us,
`voicepan` max=11us, `voicestop` max=14us, `voicevol` max=35us (called
66 times, not 28 -- confirms it also fires from `sink_on_tick()`'s
release ramp as documented, not just note-on), `voicestart` max=54us.
Combined with `gusscan` (GetState, already exonerated, max=170us), every
individual GUS register-write call this investigation has now measured
is cheap and unremarkable -- consistent with every one of them being a
bounded handful of `outportb()`/`inportb()` calls, exactly as source
reading predicted, this time actually confirmed by measurement rather
than assumed.

**`miditick` max = 3,602us -- three orders of magnitude short of
6,891,495us.** This is the decisive result: the ENTIRE `midi_sched_tick()`
call -- its dispatch loop, every GUS register call it makes, tempo
math, everything -- cannot explain the outlier. `midi_sched_tick()`
itself, as a whole function, is conclusively ruled out.

## Where the outlier actually is: `miditick` calls (20) is less than `audioprb`'s total_calls (68)

This is the thread that points to the answer. `AudioPlayer::MidiPoll()`'s
own structure is:

```cpp
void AudioPlayer::MidiPoll()
{
    if (_playState == PlaybackState::PlayStateInitial)
        Init();                          // <-- NOT bracketed by miditick
    if (_playState != PlayStatePlaying)
        return;
    if (!_midiSched || !_midiSink)
        return;
    { /* miditick bracket starts HERE */
        midi_sched_tick(_midiSched, MidiNowMs());
    }
    ...
}
```

`slots_us` (in `audio_core_entry_poll()`) wraps the ENTIRE per-slot
`Poll()` call, including `Init()` -- but the `miditick` bracket added
this pass only wraps the `midi_sched_tick()` call itself, deliberately
placed AFTER `Init()` (matching the call's own position in the source).
`Init()` -> `MidiInit()` calls `dos_midi_backend_prepare_song()`, which
for the GUS backend is `gus_sink_prepare_song()`
(`shared/audio/gus_sink.c`) -- and `gus_sink_prepare_song()` loops over
every melodic/drum program the song's SMF data actually uses, calling
`upload_pat()` for each, which calls `SDL_DOSGusUploadSample()`
(`vendor/SDL/src/audio/dos/SDL_dosaudio_gus.c`) for every resident
subsample.

**Source-verified this entry**: `SDL_DOSGusUploadSample()` ->
`gus_upload_to()` -> (default path) `gus_upload_pio()` is a **byte-wise
PIO transfer loop over the entire sample's data**, `GUS_PIO_BURST=64`
bytes per `cli`/`sti` window, and -- critically -- `g_gus_pio_autoinc`
defaults to `false` (no `SDL_HINT_DOS_GUS_PIO_AUTOINC=1` hint set by
this test), meaning the DEFAULT path re-selects the FULL DRAM address
before EVERY SINGLE BYTE (the function's own comment: "~6 outportb/byte"
vs ~1 outportb/byte with autoinc on). For a real GM instrument set (up
to `GUS_MAX_SUBSAMPLES=8` resident subsamples per instrument, however
many instruments a real song's SMF data references, each subsample up to
`2*1024*1024` bytes per `gus_sink.c`'s own sanity cap), a real-hardware
byte-wise ISA PIO loop at ~6 outportb/byte is exactly the kind of
deterministic, per-song, one-shot, multi-second cost this whole
investigation has been chasing -- and it happens on the SAME `Poll()`
call whose `slots_us` shows the outlier, ONE call before `midi_sched_
tick()` (and therefore `miditick`'s own bracket) ever runs.

**This is a strong, source-verified candidate -- not yet directly
measured.** Per this hub's own "instrument the thing that produces the
unexplained quantity, not its neighbors" rule (already applied, and
already corrected a wrong assumption, twice earlier in this same
sub-investigation), the next diagnostic pass should bracket
`gus_sink_prepare_song()` and/or `SDL_DOSGusUploadSample()`/
`gus_upload_pio()` directly rather than trusting this source-reading
conclusion the way `reap_finished_voices()`'s architecture mismatch and
`SDL_DOSGusGetState()`'s assumed-slow status were both trusted, and both
wrong, earlier in this investigation.

## Not yet done

1. Bracket `gus_sink_prepare_song()` (or, more precisely, `SDL_DOSGus
   UploadSample()`/`gus_upload_pio()` individually, since that is the
   specific call this entry's source read identifies as the real
   candidate) with the same uclock()-based idiom as every other
   diagnostic in this sub-investigation, and re-run the real-hardware
   cell to confirm or refute this candidate directly.
2. If confirmed: this would be a genuine, real, likely-fixable software
   cost (`SDL_HINT_DOS_GUS_PIO_AUTOINC=1` alone -- already a real,
   already-existing hint, never enabled by default -- could plausibly
   cut the byte-wise overhead ~6x with zero new code, a very different,
   much better outcome than the OPL3/WaveBlaster hardware-constant
   verdict this whole S7 arc otherwise reached). If refuted: the next
   unexamined candidate would be `.pat` file I/O itself (`fopen`/`fread`
   in `upload_pat()`, `gus_sink.c`) or something in `dos_midi_backend_
   prepare_song()`'s own dispatch, neither source-verified this entry.
3. Re-verify (flagged again, still not root-caused) `vcctrl`'s own
   `select_boot_profile()` / the manual workaround's own timing drift --
   now a THIRD real, reproducible timing-sensitivity finding for this
   rig/profile combination, worth its own focused session before the
   next port that needs `--boot-profile` relies on either the automated
   path or the "proven" manual workaround as stable.
4. Acceptance gate items 4 and 5 (re-targeted at GUS) remain open.

Patches SDL/0146, ags/0070, ags/0071 stay landed (the diagnostic is
sound and narrowed the search space decisively, even though it did not
land on the answer itself).
