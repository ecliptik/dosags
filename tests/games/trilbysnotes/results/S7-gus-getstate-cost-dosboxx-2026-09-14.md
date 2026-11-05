# S7-GUS -- SDL_DOSGusGetState() per-call cost diagnostic: patches landed, DOSBox-X validated -- 2026-09-14/15 (new session)

Continuation of `S7-gus-midi-realhw-2026-09-14.md`'s own "Not yet done"
item 1. Before proposing any fix to `gus_sink.c`'s `reap_finished_
voices()`, this measures `SDL_DOSGusGetState()`'s own real-hardware cost
directly, per this hub's "instrument the thing that produces the
unexplained quantity, not its neighbors" rule -- and per a real course-
correction caught before writing any fix: `reap_finished_voices()`
genuinely needs the FULL voice-active mask (it must know every busy
voice's state to decide which to reap), unlike `gus_pcm_stream_pump()`'s
own single-voice query that `SDL_DOSGusVoiceActive()` (patch SDL/0140)
was built for -- the handoff's own speculation that the same fix
pattern "directly applies" here was not re-verified before now, and a
fresh read of `reap_finished_voices()`'s call shape shows it does not.

## Patches landed

- **`patches/SDL/0145`** (`vendor/SDL/src/audio/dos/SDL_dosaudio_gus.c`):
  brackets `SDL_DOSGusGetState()`'s real (non-early-return) path with
  `uclock()`-based timestamps, exposes `SDL_DOSGusGetStateDiagSnapshot()`
  -- same idiom as the OPL3 regwrite diagnostic (SDL/0141) this mirrors.
- **`patches/ags/0069`** (`Engine/media/audio/audio_core.cpp`): folds
  the snapshot into the existing `DOS-PORT audioprb` log line as a new
  `gusscan(calls=... min_us=... mean_us=... max_us=...)` field,
  alongside the already-landed `regwrite` field (mutually exclusive per
  backend -- OPL3 populates one, GUS populates the other). Same
  discard-snapshot-before-the-slot-loop pattern as the regwrite fold-in
  (patch 0062), for the same attribution-correctness reason.

## DOSBox-X validation

`binary_sha12=c6d6f6626df8`. Wiring confirmed: the new `gusscan` field
appears correctly in the log line, parses cleanly, no crash. As
expected (and consistent with `S7-gus-midi-dosboxx-2026-09-14.md`'s own
finding), DOSBox-X's `[gus]` emulation does not present as real GF1
hardware here (`midi=none,events=0`), so `gusscan(calls=0...)` --
correctly zero, not a wiring failure; this diagnostic cannot be
exercised under DOSBox-X at all, only real hardware can answer the
actual question. Clean shutdown, `exit_code=0`, no regression against
the prior binary.

## Not yet done

1. The real-hardware cell -- the actual measurement. Will show whether
   `slots_us`'s own 6.9s max under GUS (`GUST1`) is call VOLUME (many
   cheap `SDL_DOSGusGetState()` calls stacking up during a catch-up
   burst -- the `gusscan calls` field will be large, `mean_us` small) or
   a genuine single-call stall (`calls` small, `max_us` itself huge).
   This determines whether `reap_finished_voices()` needs a frequency
   fix (call it less often, e.g. only when the voice pool is actually
   exhausted rather than on every allocation) or whether there's a
   deeper GF1-communication stall worth its own investigation.
2. Acceptance gate items 4 and 5 (re-targeted at GUS per the operator's
   2026-09-15 decision) remain open pending this fix + a proper ABBA.
