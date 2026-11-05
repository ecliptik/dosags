# Presentation bake-off configs (40/40 plan, P2.1)

Sound-off `ACSETUP.CFG` variants for BENCH8 that select each presentation
candidate; stage one as `ACSETUP.CFG` with `run-hw.sh ... --extra-file
tests/harness/presentation/bench8/<file>:ACSETUP.CFG` (or `run-dosbox.sh
--include-extra` on a copy named `ACSETUP.CFG`).

| candidate | file | plus | what the engine logs (DOSBox-X, 2026-09-17) |
|---|---|---|---|
| (d) today's default: 640x480, 2x letterboxed | `ACSETUP-OFF-640X480.CFG` | -- | `render dest (0, 40, 639, 439 : 640 x 400)` |
| (c) 640x480, centred 1x | `ACSETUP-OFF-640X480.CFG` | `--env DOSAGS_MAX_SCALE=1` (patch 0101) | `render dest (160, 140, 479, 339 : 320 x 200)` |
| (b) 512x384, centred 1x (UniVBE mode 0x01F3) | `ACSETUP-OFF-512X384-ROUND.CFG` | optionally `--env SDL_HINT_DOS_FORCE_MODE_ID=0x01F3` | needs a card/TSR that has the mode; DOSBox-X's oversized conf falls back to 640x400 2x |
| (a) Mode 13h, full screen (true 320x200 8-bit games only) | `ACSETUP-OFF-NATIVE.CFG` | -- | `Graphics mode set: 320 x 200 (8-bit) fullscreen`, `render dest (0, 0, 319, 199)` |

All four were run under DOSBox-X (the hub's `dosbox-x-oversized.conf` for
b/c/d, the standard conf for a) and the window screenshots looked right:
picture where the log says, margins black.
