# AGS Quest depth comparison (patch 0079/0080 tick timing), 2026-09-16

40fps push step 3, round 3: first real use of AGS Quest as the
iteration vehicle (operator decision, replacing Shards of God -- 20-70+
real minutes per Shards cell made it too expensive to keep iterating
on). AGS Quest's own AutoPilot script gives bounded completion (no
`DOSAGS_TAS_AUTO_EXIT_TICK` needed), and the same `DOSAGS_FORCE_COLOR_DEPTH`
lever (patch 0076) exercises the same depth paths.

AGS Quest's own native color depth is 16-bit (`HighColor`, baked into
`overlay/Game.agf.patch`) -- the reverse of Shards (native 32-bit). Two
real-hardware cells, same content, same binary (`binary_sha12=cd8540625e54`,
patch series 0001-0080 applied):

- `AQ16N1`: native, no override.
- `AQ32F1`: `DOSAGS_FORCE_COLOR_DEPTH=32`.

Both completed the full AutoPilot sequence naturally (`exit_code=0`,
`AUTOPILOT phase=quit status=begin` reached in both STDOUT.TXT files).

## Results

| | AQ16N1 (16-bit native) | AQ32F1 (32-bit forced) | Ratio |
|---|---|---|---|
| duration_s | 276 | 452 | 1.64x |
| tick_rate | 13.43 | 8.16 | 1.65x |
| fps_p50 | 6.67 | 2.88 | -- |
| `script_vm` total_ms (% of run) | 126844 (46.0%) | 229569 (50.8%) | 1.81x |
| `script_vm` max_ms (outlier) | 18449 | 33414 | 1.81x |
| `script_vm` per-call, outlier excluded | 218.54ms | 395.47ms | **1.81x** |
| `render_backbuffer` mean_ms | 7.56 | 9.72 | 1.29x |
| `render_backbuffer` total_ms (% of run) | 8696 (3.2%) | 9828 (2.2%) | 1.13x |
| `input_poll` / `audio_sync` | 0.00ms both | 0.00ms both | ruled out |

## Audio candidate verified directly, not assumed

DOSBox-X (`./run-dosbox.sh agsquest`, no overrides) shows real audio
active ("Initializing audio", "DOSAudioMixer: opened 11025 Hz mono
S16, 8 voices", "DOS audio device opened"). **Real hardware shows
"Audio is disabled" in both AQ16N1 and AQ32F1's own STDOUT.TXT** --
genuinely different from the DOSBox-X environment, not assumed from
the absence of an ACSETUP-OFF.CFG override (AGS Quest has no such file
at all; this game's audio state was previously unverified for the
real-hardware harness). Cause not investigated further this round.
`input_poll`/`audio_sync` both reporting exactly 0.00ms in both real
cells is consistent with this -- a disabled subsystem's own per-tick
check is cheap enough to round to 0ms at 1ms uclock() granularity.

## Interpretation

Unlike Shards' round 2 (S16TV1/S32TV1), where neither script_vm nor
render_backbuffer explained the depth scaling, AGS Quest's richer,
more representative content gives a real, specific answer:

- `render_backbuffer` is a real but MINOR contributor: mean cost rises
  29% between depths, but it is only 2-3% of total run time either
  way.
- `script_vm` dominates (46-51% of total run time) and its per-call
  cost -- BOTH the single largest outlier AND the remaining ~496
  calls' own average -- scales by an essentially identical **1.81x**
  in both measures, closely tracking (and slightly exceeding) the
  1.64-1.65x overall scaling.

Caveat, same class as Shards' own patch 0079 finding: `RunScriptFunction()`
can recursively re-enter the whole tick loop (including nested renders)
via a script's own blocking `Wait()`/animation-wait calls. AGS Quest's
AutoPilot drives many more scripted interactions (menu navigation,
dialog, animation waits) than Shards' idle title screen, so it is
plausible that MORE than one of the 497 script_vm samples carries some
nested re-entrant time, not just the single largest outlier -- this
patch's aggregate-only design (no per-call histogram) cannot fully
separate "genuine interpreter cost that scales with depth" from
"nested-tick time that happens to recur across many samples." The
internal consistency of the 1.81x ratio across both the outlier and
the non-outlier remainder is suggestive of a real, depth-correlated
effect rather than one runaway sample, but this is not a microscope-
level proof.

## Raw data

- `HW-486-66-2026-09-16-AQ16N1.LOG` / `-STDOUT.TXT`
- `HW-486-66-2026-09-16-AQ32F1.LOG` / `-STDOUT.TXT`
