<!--
Machine-readable port summary. Keep in sync with the hub's ports.yaml
entry for adventure-game-studio. The yaml and "Where it stands" were
rewritten 2026-11-04 (PLAN-NEXT step 3) from the gate evidence of
fdbaf461; the cell tables further down are the historical record and
are not rewritten. PLAN.md holds the chronological record.
-->

# dosags -- status

```yaml
name: dosags (hub candidate: adventure-game-studio)
upstream: https://github.com/adventuregamestudio/ags
upstream_revision: 94e271df9c14484d89f4861100f643d39555dae7 (tag v3.6.3.13)
upstream_license: Artistic License 2.0  # verified by reading License.txt +
                                        # Copyright.txt at the pin, see
                                        # LICENSE-REVIEW.md
language: C++ (C++11)
original_sdl_version: "2"
target_sdl_version: "3"
graphics_api: software  # AGS's "Software" driver (ali3dsw.cpp), presenting
                        # via SDL_GetWindowSurface at the game's native
                        # depth (patches/ags/0029-0031, 0075), with dirty-rect
                        # and pillarbox-alias presents (0193, 0196)
native_resolution: 320x200 and 320x240 games, shown 1:1 centred at 512x384
  (the gate setting) or 640x480, or 2x-scaled at 640x480; 640x360 (AGS
  Quest) letterboxed 1:1 at 640x480
color_depth: 8-bit (INDEX8), 16-bit (RGB565) and 32-bit (XRGB8888,
  shown via pack24 on the Mach64) -- all three MET their 486 gate at
  40 ticks/s with sound on (2026-09-30, below)
build_flavours: instrumented (default `make`, the ratchet and every gate
  cell) and release (`make DOSAGS_RELEASE=1`, ags 0351: timing
  instrumentation compiled out, fixed timestep ON by default). Both
  carry the AUDIOPRB retirement (ags 0352/0353, SDL 0269) and ags 0354.
  The release flavour has DOSBox-X ratchet parity (41 pass) and, on the
  486, carries the S8 gate (round R1 2026-11-05: ABBA EQUIVALENT, S8 MET
  x2, CAPR8 PASS); gate cells use it from R1 on.
fixed_timestep: release ON by default (DOSAGS_FIXED_TIMESTEP=0 turns it
  off); instrumented opt-in (=1), set by the harness for every gate cell
audio_stack: native, no SDL2_sound/mojoAL. PCM: a fixed-voice mixer
  (8 voices) on one SDL3 stream at 11025 Hz mono; WAV/VOC loader;
  Sound Blaster PCM via the SDL3-DOS SB backend, GUS PCM via the hub's
  gus_pcm_stream. MIDI: the hub's midi_sched with OPL3 (default; F-number
  table fixed 2026-09-30, +1 cent on the 486), WaveBlaster/MPU-401 (with
  the RTC pump, SDL_HINT_DOS_AUDIO_WB_RTC_PUMP=1) and GUS sinks, chosen by
  SDL_HINT_DOS_AUDIO_BACKEND (auto/opl3/wb/gus/none). OGG/MP3 are
  host-transcoded to WAV by tools/port-game; tracker music is not played
  (libxmp-lite planned, not vendored); no video player.
input_stack: SDL3 DOS keyboard + PS/2 mouse through the ported event pump
  (ags 0017). A press+release shorter than one poll can be missed below
  1 fps.
filesystem_dependencies: resolved. DOS platform driver (ags 0036);
  save/config dirs default to "."; Allegro drive-prefix fix (0037). No
  plugins: built-ins compiled out, dynamic loading resolves to the dummy.
threading: single-threaded by construction (AGS_DISABLE_THREADS) plus a
  DOS no-op mutex shim (ags 0014)
networking: none
external_dependencies: linked -- SDL3 (vendored + patched), Allegro 4.4.3
  subset, FreeType 2.1.3 + AllegroFont 2.0.9, aastr, miniz, stb_image,
  GLM, the hub's shared modules, DJGPP libc, GCC runtime. Shipped beside
  the exe -- CWSDPMI r7. See THIRD-PARTY.md and LICENSE-REVIEW.md.
release_packaging: `make dist` (2026-11-04) builds build/dist/dosags-<V>.zip
  from the release flavour and checks it against THIRD-PARTY.md and
  LICENSE-REVIEW.md (scripts/check-dist.sh). Not releasable until the
  source has a public URL.
copyrighted_assets: none -- no AGS game data is shipped or tracked. Test
  games are pinned by hash in tests/games/*/PIN and
  tests/harness/packages/*/PIN.
dos_status: PLAYABLE   # the hub's ports.yaml value (sdlports owns it); the
                       # gates below are the OPTIMIZING bar, met; v0.1 waits
                       # on PLAN-NEXT R1
dos_minimum_target: 486DX2-66 / 16 MB, ATI Mach64 (VESA via UniVBE) --
  the gate machine (HW-486-66 has 48 MB; 16 MB is a target, unmeasured)
dos_recommended_target: null
maintainer: null
```

`dos_status` values (same ladder as `ports.yaml` in the sdl-dos-ports hub):

```
BACKLOG
RESEARCH
BLOCKED
BOOTSTRAP
COMPILES
STARTS
TITLE_SCREEN
PLAYABLE          <- here
FULL_GAME
OPTIMIZING
RELEASE_READY
```

Difficulty score (also tracked in the hub's `ports.yaml`): **5** (major
engine-port effort).

## Where it stands (2026-11-04)

The 486 gates (PLAN-GATES) were MET 2026-09-30 (fdbaf461). The bar, per
colour depth, on HW-486-66 (486DX2-66, ATI Mach64), sound on, fixed
timestep, run twice: both tick figures (whole-run / steady) within
39.2-40.8, fps_p50 >= 40, completeness >= 95%, a clean camera witness,
and clean audio counters (overwrites 0, late 0, silent 0 outside room
loads). One harness-scored 640x480 capture listen per depth closes it.

| Gate | Fixture | Bar cells: whole-run / steady (binary) | Capture listen (binary) | WaveBlaster arm (ef123dba0adf) |
|---|---|---|---|---|
| S8 | Trilby's Notes room 35, 8-bit, 512x384 centred 1x, OPL3 | GL8A 39.26 / 40.23, GL8B 39.35 / 40.29 (8249193ed041) | CAPS8 PASS (8249193ed041) | WBC8R PASS |
| S16 | 5 Days a Stranger room 3, 16-bit, 512x384 centred 1x, OPL3 | GL16A 39.29 / 40.13, GL16B 39.29 / 40.10 (8249193ed041) | CAPS16 PASS, OPL3 +1 cent (64d449a5b895) | WBC16R PASS |
| S32 (S32P) | 5 Days room 3 forced 32-bit, 640x480 centred 1x, pack24, OPL3 | GL32A 39.28 / 40.12, GL32B 39.34 / 40.07 (8249193ed041) | CAPS32R PASS, OPL3 +1 cent (e3a83135dc9c) | WBC32R PASS |

fps_p50 is 40.00 in every cell. The caveats are stated in PLAN.md's
"Gates" paragraph:
- n=2, and the whole-run margins are 0.06-0.15.
- The evidence spans four binaries.
- The bar cells and CAPS8 had the ~89-cent-sharp OPL3 table, since
  fixed. Pitch is not in the bar.
- S8's capture scorer has no pitch check, and none is claimed there.

Since then:
- **D2 FAILED as registered** (cold-start sound latency <= 1.0 ms):
  4.30 ms median over 39 cold starts on the 486 (cd217660). It stays
  failed.
- **Release flavour** (ags 0351, 23230d06) and **AUDIOPRB retirement +
  room-entry stdout commit** (ags 0352-0354, SDL 0269, da012275). Both
  flavours pass the DOSBox-X ratchet (41 pass, 0 fail; runs
  20261105T000223Z instrumented 7e5dfe26f272 and 20261105T005648Z
  release a1dba5d61624).
- **Round R1 (2026-11-05, tests/harness/results/ROUNDR1-2026-11-05)**:
  RELEASE ABBA on S8, instrumented 7e5dfe26f272 vs release a1dba5d61624
  (main f2228d5e): mean whole-run 39.24 vs 39.25, steady 40.26 vs 40.255
  -> EQUIVALENT (operator tolerance 0.10). Release cells R1R1 39.27 /
  40.27 and R1R2 39.23 / 40.24, both MET -> **S8 MET x2 on the release
  flavour** (camera CLEAN at the 09-30 standard). CAPR8 (640x480 capture
  listen, release): PASS (K2 16.6 dB, K3 0.41 vs 0.13, K4 >= 51.0 / 44.0
  dB). Whole-run margins 0.03-0.07 (09-30: 0.06-0.15). Gate cells move to
  the release flavour; R2 (GR16, GR32P, GR16WB) remains for S16 / S32P.
- **`make dist`** (05cfb7f4): the player zip, checked against the
  licence records. Not releasable until the source is published.
- Next: PLAN-NEXT R1 (operator ask), then v0.1.

## Milestone ladder at a glance (PLAN.md "Milestones" is the record)

| Milestone | State |
|---|---|
| BOOTSTRAP-0 .. PLAYABLE | done (2026-09-10 .. 2026-09-11) |
| Fixed timestep (S0, patches 0046-0048) | done 2026-09-11; opt-in via `DOSAGS_FIXED_TIMESTEP=1`, enforced by the harness/framework for every benchmark cell |
| Sound | claimed 2026-09-15 (GUS path; OPL3/WB fps bar waived) |
| Game porting framework | claimed 2026-09-15, operator sign-off (F5) -- all five gate-set games (Trilby's Notes, 5 Days a Stranger, Maniac Mansion Deluxe, Shards of God, IOAWN4T) validate on DOSBox-X from their manifests alone (F2); all three in-profile games (Trilby's Notes, 5 Days a Stranger, Maniac Mansion Deluxe) have a real-hardware sound_off sanity record on HW-486-66 produced through `check`/`record` (F3) |
| 32-bit display path | done: the S32 (S32P) gate was MET 2026-09-30 (5 Days room 3 forced 32-bit, 640x480 centred 1x, pack24, sound on) |
| Compatibility sweep | claimed 2026-09-16, operator sign-off -- six games (Trilby's Notes, 5 Days a Stranger, Maniac Mansion Deluxe, Shards of God, IOAWN4T, 7 Days a Skeptic) swept on DOSBox-X: boots/title PASS across the board (each reaches and idles in its own start room, exit_code=0); first-room/playable/complete honestly not-reached/not-attempted (title screens wait for player input, none injected this pass; no input-injection automation exists for closed binaries -- an honest scope limit, not a defect). King's Quest III (Infamous Adventures) was dropped after its only download path turned out to be itch.io's session/JS-gated download-URL endpoint with no plain mirror; 7 Days a Skeptic (same developer/hosting pattern as the other two Yahtzee games) replaced it. See PLAN.md's "Compatibility sweep" section. |
| FULL_GAME | not started (needs the self-authored test game) |
| OPTIMIZING ("40/40") -- 40 fps / 40 Hz on HW-486-66 | **Gate 1 CLAIMED 2026-09-18** (Trilby's Notes 8-bit idle: `fps_p50` 40.00, steady 40.04, whole-run 39.54 vs 39.2, 5/5). **Gate 2 RE-CLAIMED, SCOPED, 2026-09-21 (operator decision):** 8-bit 320x200 at Mode 13h on anim12 (in-place animation) AND the walk arm (moving position), Mach64-only, on the fixed binary (ags 0194) -- anim12 x2: `fps_p50` 40.00, steady 40.01, whole-run 39.34, 2,481 presents; walk arm x2: `fps_p50` 40.00, steady 39.99, whole-run 39.34/39.32, 982 presents; both witness-reviewed clean, both pass the alias screen-equality gate with a working control; margin over the 39.2 floor 0.12-0.14 with the +215-224 ms whole-run residual still unexplained. **Does NOT cover any real game.** See PLAN.md for the full evidence and the prior OPEN/REOPENED history in place. **Gate 3 RE-HOMED 2026-09-21**: AGS Quest (16-bit 640x360) closed on evidence at 38.0, content-bound (40.61 with its GUI hidden); the 16-bit gate is now 5 Days a Stranger (320x200) in play at a centred 1x rung. **Gate 3 CLAIMED 2026-09-22 (operator decision via the question tool, on the pre-agreed "replicate once, then claim" condition):** 16-bit 320x200, 5 Days a Stranger IN PLAY (room 3 via `--startr 3`, drive-walk 2 s), 512x384 centred 1x with the pillarbox alias ON (ags 0196, `binary_sha12=340fa8167624`), Mach64-only, sound off -- S2F2 / S2F3: steady 39.97 / 39.95, whole-run 39.26 / 39.24, stable 39.47 / 39.46, `fps_p50` 40.00 x2, ~100% presents; camera witness clean both cells apart from the `--startr` two-figure beat (DUPCHAR4: a debug-jump artifact). Caveats: whole-run margin 0.04-0.06; n=2; 0196 binary, not 0197; does NOT cover Maniac Mansion Deluxe or 32-bit. 32-bit: two zero-code cells owed. **Step 3 CLOSED 2026-09-22** (work-order step, not a gate): ags patch 0196 makes the 8-bit alias/direct path engage on a centred 1x rung (previously full-window-width only) -- Trilby's Notes in play at 512x384 now gets the alias (`vscreen alias ON x=96 y=72`), `tick_rate_steady` 39.99, stable rate 39.91, `presents_real` 5003/`render_passes` 4990 (~100%, was 3.6% before the drive-walk cadence fix). **Generalized to the other 320-wide catalogue titles, DOSBox-X-gated, 2026-09-22**: 5 Days a Stranger (16-bit) and Maniac Mansion Deluxe (16-bit, via its BENCH16 stand-in) both PASS clean (5/5, controls fail as required); Shards of God (32-bit, first exercise of this patch at that depth anywhere) FAILS screen-equal at one of five freeze ticks, but the alias-disabled diagnostic reproduces the identical divergence byte-for-byte, decoupling it from patch 0196 -- a pre-existing title-screen content question, not a placement-math defect (see PLAN.md for the full check, including why a clean-tick rerun was tried and reverted). Real-hardware in-play validation not yet started for any of the three. See `PLAN.md` (plan of record) and `PLAN-LOG.md` (history). |
| RELEASE_READY | in progress: release flavour (2026-11-04), `make dist` (2026-11-04); S8 carried on the 486 (R1 2026-11-05); v0.1 waits on R2 (S16 / S32P) and the source snapshot at github.com/ecliptik/dosags |

## Real-hardware figures (HW-486-66 + ATI Mach64, `DOSAGS_FIXED_TIMESTEP=1`, sound off)

Every row names its fixture, rung and date; they are not interchangeable.
`fps_p50` counts render passes, not displayed frames. Numbers are from
`tests/games/*/manifest.yaml` and `tests/harness/results/`; DOSBox-X
figures are never quoted as performance results (its 18% gap on 32-bit
was ~100x on hardware).

| Fixture | Depth / res | Rung | fps_p50 | tick_rate (whole-run / steady) | Note | Date |
|---|---|---|---|---|---|---|
| Trilby's Notes, title idle | 8-bit 320x240 | 640x480 2x | **40.00** | **39.54** / 40.04 | Gate 1. ~23 real presents per run | 2026-09-18 |
| BENCH8 anim12 (synthetic, 12 sprites) | 8-bit 320x200 | Mode 13h 1:1 | **40.00** | **39.41** / 40.01 | Gate 2 history: 4/4, 99.9% frames shown, patch 0189 binary (superseded below) | 2026-09-20 |
| BENCH8 anim12 (synthetic, 12 sprites), fixed binary | 8-bit 320x200 | Mode 13h 1:1 | **40.00** x2 | **39.34** x2 / 40.01 x2 | Gate 2 RE-CLAIMED SCOPED 2026-09-21: 2,481 real presents, witness reviewed clean, alias screen-equality gate pass. ags 0194 | 2026-09-21 |
| BENCH8 walk arm (synthetic, 4 objects), fixed binary | 8-bit 320x200 | Mode 13h 1:1 | **40.00** x2 | **39.34 / 39.32** / 39.99 x2 | Gate 2 RE-CLAIMED SCOPED 2026-09-21: 982 real presents, witness reviewed clean (camera only), alias screen-equality gate pass. ags 0194 | 2026-09-21 |
| BENCH8 anim12 | 8-bit 320x200 | 640x480 2x (default) | 14.99 | -- | the rung a 320x240 game lands on | 2026-09-18 |
| BENCH8 anim12 | 8-bit 320x200 | 512x384 / 640x480 centred 1x | 26.89 / 19.72 | -- | pre-alias, pre-multi-rect | 2026-09-18 |
| AGS Quest AutoPilot (demo) | 16-bit 640x360 | 640x480 1:1 letterboxed | 38.0 stable (40.61 GUI hidden) | -- / 41.5 | content-bound; the demo's ceiling. 2026-09-21 note: measured with ags patch 0169 stage 1 ON, which shipped with a stale-pixel-on-hide defect and an "unchanged" test that read the flags after they were cleared; stands as measured pending the slice C confirmation cell (PLAN.md step 1) | 2026-09-20 |
| 5 Days a Stranger | 16-bit 320x200 | default | 5.45 | 14.28 / -- | pre-optimisation sanity cell; re-homed Gate 3 | 2026-09-16 |
| Maniac Mansion Deluxe | 16-bit 320x200 | default | 2.73 | 10.80 / -- | pre-optimisation sanity cell | 2026-09-16 |
| AGS Quest forced to 32-bit | 32-bit 640x360 | 640x480 1:1 | 2.88 (16-bit arm 6.67) | 8.16 / -- | pre-alias | 2026-09-16 |
| Shards of God, title idle | 32-bit 320x200 | 640x480 2x | 0.05 | 0.32 / -- | pre-everything | 2026-09-15 |
| Trilby's Notes, title idle, campaign open | 8-bit 320x240 | 640x480 2x | 4.99 | 23.8 / -- | 1000-tick window, not comparable to the 5000-tick rows | 2026-09-15 |
| Trilby's Notes, IN PLAY, fixed binary | 8-bit 320x240 | 512x384 centred 1x | 40.00 | 39.05 / 39.99 | S2T1: no alias (correct, not full-width). Stable rate 39.91. `presents_real` 180/4968=3.6%, under the 30% in-play bar -- reported as an idle-room cell per its own pre-registered rule, not sustained in-play | 2026-09-22 |
| Trilby's Notes, IN PLAY, ags 0196 (pillarbox-alias fix), driver fixed | 8-bit 320x240 | 512x384 centred 1x | 40.00 | 39.06 / 39.99 | S2T2: **alias ON x=96 y=72** (patch 0196, confirmed on real hardware). Stable rate 39.91. `presents_real` 5003/`render_passes` 4990 (~100%) -- decisively clears the 30% in-play bar with a fixed drive-walk cadence (2s, was 8s). Step 3's bar met | 2026-09-22 |
| 5 Days a Stranger, title idle, fixed binary | 16-bit 320x200 | 512x384 centred 1x | 40.00 | 40.20 / 40.20 | S2F1: no alias, `presents_skipped`=0 at 16bpp, both matching prediction. Stable rate 39.999 (predicted 30, 25-40) | 2026-09-22 |
| Maniac Mansion Deluxe, title idle, fixed binary | 16-bit 320x200 | 512x384 centred 1x | 6.84 | 26.08 / 28.34 | S2M1: model falsified (predicted 30, 25-40) -- root-caused to `tickstats_process_events_dispatch` alone costing 26.47ms/tick, not a present-path defect. Stable rate 6.75 | 2026-09-22 |
| Shards of God, title idle, fixed binary | 32-bit 320x200 | 512x384 centred 1x | -- | -- | S2S1/S2S2: UNMEASURED -- both attempts hit a post-collection dead-link hang (HARDWARE.md, bounded tier); no manifest collected, no VOID, not falsified, simply not run to completion | 2026-09-22 |
| 5 Days a Stranger, IN PLAY, ags 0196 (pillarbox alias) | 16-bit 320x200 | 512x384 centred 1x | 40.00 x2 | 39.26 / 39.97 (S2F2); 39.24 / 39.95 (S2F3) | **Gate 3 CLAIMED.** Alias ON x=96 y=72; room 3 via `--startr 3`, drive-walk 2 s; stable rate 39.47 / 39.46; `presents_real` 4950/4938, 4951/4939 render passes. Camera witness only (card cannot lock 512x384). Whole-run margin 0.06 / 0.04 | 2026-09-22 |
| AGS Quest forced-32, demo to tick 1500, fixed binary | 32-bit 640x360 | 640x480 1:1 letterboxed | 39.45 | 16.25 / 40.52 | S2Q1: alias ON (correct, full-width). Stable rate 35.41 against predicted 16 (8-25) -- missed high, not falsified (4x bound not crossed); today's 32-bit/16-bit cost ratio is 0.937x vs the 2026-09-16 baseline's 0.43x, candidate explanation the present-path work since then | 2026-09-22 |

Target is 40 (native AGS rate). Whole-run `tick_rate` is `N / (fixed + N/steady)`
and so depends on window length; `fps_p50` and `tick_rate_steady` do not.

## Gate cells, sound ON (PLAN-GATES claim procedure, from round Q)

Scope note (coordinator 2026-09-26): Maniac Mansion Deluxe's "under 25 ms/tick" logic reading stays scoped to the
builds it measured -- main 221fb28 (round O MAINABS, `3cf8c4a48fe6`) and main 389a37a (round P MAINABS-P,
`a30ee9702c2a`). Later landings that move the VM (0316, 0236) are not re-read with MAINABS; under PLAN-GATES the gate
cells measure the engine directly.

One row per cell; the bar is PLAN-GATES' (both tick figures 39.2-40.8, fps_p50 >= 40, completeness >= 95%,
camera clean, audio counters clean, x2). Player default (fine timing off) unless stated.

| Cell | Fixture | Binary | fps_p50 | tick_rate (whole-run / steady) | Audio | Verdict | Date |
|---|---|---|---|---|---|---|---|
| S16Q1 | 5 Days room 3, S16 gate fixture (SB2C1), OPL3, 512x384 centred 1x | main 75543c93 `b1cd5ccee175` | 40.00 | **39.18** / 40.08 | late 0, overwrites 0, underruns 0, silent 0 | **NOT MET** as registered: whole-run 0.02 under 39.2 (3 stall ticks, 1546 ms) | 2026-09-26 |
| S16Q2 | as S16Q1 | as S16Q1 | 40.00 | **39.13** / 40.09 | late 0, overwrites 0, underruns 0, silent 0 | **NOT MET**: whole-run 0.07 under (the same 3 stalls, 1546 ms); prediction falsified | 2026-09-26 |
| WBLR | 5 Days own flow, WB (DreamBlaster S2) via the RTC pump | lab-wb land3 `fe1b2285e8f7` | -- | 32.78 / 33.67 | midi_tick rtc, c_redrain 84, late 0, stuck 0 | D 0.697 against 0.70 (lab-wb): not a landing run | 2026-09-26 |
| PLAYQ1 | MMD in play, AGSSAVE.007 restored in room 1, held clicks | main 75543c93 `b1cd5ccee175` | -- | (restore) / 35.39 | -- | **VOID** as registered (LAB-MMD 50.4): entered room 2 at loop 6937 | 2026-09-26 |
| PLAYQ2 | as PLAYQ1 | as PLAYQ1 | -- | (restore) / 35.26 | -- | **VOID** as registered: entered room 2 at loop 6859 | 2026-09-26 |
| S8R1 | Trilby room 35, original S8H protocol (--startr 35, 5000 ticks, walk 25 2 80), OPL3, 512x384 centred 1x | main 5ca997b3 `9297b7d42365` | 40.00 | **38.76** / 40.24 | late 0, overwrites 0, underruns 0, **silent 6** (not timestamped; the only present gap over the 743 ms ring is 1282 ms at t=51.0 s, room 35 throughout: outside room loads; consistent with, not tick-verified as, the known first-decode stall) | **NOT MET** as registered: whole-run 0.44 under 39.2 (stall_ticks 2, stall_ms 3099); audio item not met; prediction (38.3-38.9) held; completeness -- (not emitted in this LOG) | 2026-09-26 |
| S8R2 | as S8R1 | as S8R1 | 40.00 | **38.76** / 40.27 | late 0, overwrites 0, underruns 0, **silent 4** (only gap over the ring: 1084 ms at t=52.3 s, as S8R1) | **NOT MET** as registered: whole-run 0.44 under (stall_ticks 2, stall_ms 3378); audio item not met; prediction held; completeness -- | 2026-09-26 |
| S32R1 | AGS Quest rooms 1-3, S2Q1 protocol, 640x480x32 1:1, sound-on cfg (staged as ACSETUP.CFG), 1500 ticks | main 5ca997b3 `9297b7d42365` | 40.00 | 16.62 / 40.74 | pcm opened (sb@11025m16), pcm_irqs 0, mixed 0, midi none: nothing played in the window | **BASELINE only** (operator ruling: S32 needs a new fixture); no gate verdict | 2026-09-26 |
| S32R2 | as S32R1 | as S32R1 | 40.00 | 16.58 / 40.74 | as S32R1 (pcm_irqs 0, mixed 0) | **BASELINE only**; no gate verdict | 2026-09-26 |
| WBLRP | 5 Days own flow, WB (DreamBlaster S2), DOSAGS_MIDI_TICK=poll | lab-wb land4 `e11030a21286` | 5.99 | 32.69 / 33.58 | midi_tick poll, late_max 436 ms, overwrites 0, silent 24 | lab-wb: **VALID**; D 0.667 (information; poll is not a candidate); B PASS (WBLR vs WBLRP chroma 0.949). LAB-WB 38 on (WBLR, WBLRP): m 0.030 < 0.07 -> "landing waits; investigate" (governs). **No WB landing from round R** | 2026-09-26 |
| WBLR2 | 5 Days own flow, WB via the RTC pump (SDL_HINT_DOS_AUDIO_WB_RTC_PUMP=1) | as WBLRP | 6.00 | 32.79 / 33.67 | midi_tick rtc, c_redrain 78, late 0, stuck 0, overwrites 0, silent 20 | lab-wb: A PASS, D **0.702** (>= 0.70), B PASS (chroma 0.969), screen CLEAN: meets its registered PASS rule but **does not land** (LAB-WB 38's branch governs); m(WBLR2, WBLRP) 0.035 | 2026-09-26 |
| PACEIA1 | PACEI (LAB-JOURNEYS 8.50) arm A: C3-512 (Trilby room 35, OPL3, DRAIN_STI=0), SDL_HINT_DOS_OPL_PACE_K=128, fine timing on | main 0cb807ee `794a45491c4b` | 40.00 | 31.99 / 40.24 | pace 128/2570, pcm_irqs 2150, silent 2 (FP_AMB), late 0, overwrites 0, underruns 0 | scored with the ABBA: **PACEI CLEARED** (pacei-score.py 179af48c) | 2026-09-26 |
| PACEIB1 | PACEI arm B: as A1, no pace hint (SDL 0256 default) | as PACEIA1 | 40.00 | 31.71 / 40.26 | pace 0/2570, pcm_irqs 2082, silent 2 (FP_AMB), late 0, overwrites 0, underruns 0 | as PACEIA1 | 2026-09-26 |
| PACEIB2 | as PACEIB1 | as PACEIA1 | 40.00 | 32.06 / 40.31 | pace 0/2570, pcm_irqs 2126, silent 3 (FP_AMB), late 0, overwrites 0, underruns 0 | as PACEIA1 | 2026-09-26 |
| PACEIA2 | as PACEIA1 | as PACEIA1 | 40.00 | 31.75 / 40.28 | pace 128/2570, pcm_irqs 2178, silent 3 (FP_AMB), late 0, overwrites 0, underruns 0 | as PACEIA1: A [2, 3] mean 2.5 = B [2, 3] mean 2.5, no health fails | 2026-09-26 |
| PROF16 | lab-s8's S16 profile: 5 Days room 3, sound off, drive-walk 25 2 90, DOSAGS_PROF=1024 | lab/mmd AGSPRF16 `9ae27591b0c8` (build_dirty 1, as its lab smoke test) | 40.00 | 39.38 / 40.08 | sound off (no audio device) | **P1: FALSIFIED as registered** (click #6, lc 431: no interval >= 250 ms, max ~59 ms; index off by one against S16Q; the time-matched click #7 is 201 ms, pathfinder-dominated, FILEIO 0.8%); **P2: HELD** (pooled PATH 20.7%); build_dirty=1 expected, not VOID (lab-s8, lab/mmd 157bf84d) | 2026-09-26 |
| S32PA1 | S32P-HW (lab/metric 81c46b3b + 8f38fdf0 + 7d30fe8d) arm A: 5 Days room 3, forced 32, 640x480 centred 1x, pack24, sound on (OPL3), DOSAGS_FADE_RESYNC=0, fine off | main 397d1f2a `883a862a2d79` (PicoGUS pacing on: pace 128/2570, pgdetect 1) | 40.00 | 39.21 / 40.03 | pcm_irqs 714, silent 0, late 0, overwrites 0, underruns 0; skips 38 | ABBA verdict below; S32 bar IN (whole-run); witness PARTIAL | 2026-09-27 |
| S32PB1 | as S32PA1, arm B: DOSAGS_FADE_RESYNC=1 | as S32PA1 | 40.00 | **39.11** / 40.01 | pcm_irqs 747, **silent 2 in play** (ticks 279, 2431), late 0, overwrites 0; skips 28 | S32 bar OUT (whole-run 39.11); witness PARTIAL | 2026-09-27 |
| S32PB2 | as S32PB1 | as S32PA1 | 40.00 | 39.21 / 39.95 | pcm_irqs 419, **silent 2 in play** (ticks 279, 4978), late 0, overwrites 0; skips 18 | S32 bar IN (whole-run); witness PARTIAL | 2026-09-27 |
| S32PA2 | as S32PA1 | as S32PA1 | 40.00 | **39.15** / 40.05 | pcm_irqs 902, **silent 1 in play** (tick 566), late 0, overwrites 0; skips 31 | lab-s32p-hw.py (bb67ce17): **VERDICT: VOID [] spreads 0.06/0.10** -- float edge (see PLAN); both readings NO FLIP; **Gate S32P NOT MET** | 2026-09-27 |
| AUDH16 | lab-s8's audio split of the S16 fixture, sound on (5 Days room 3, 512x384, OPL3) | lab/mmd AGSAUDP4 `90f81deaa3fc` (build_dirty 1, probe build) | 40.00 | 39.21 / 40.07 | pace 128/2570, pcm_irqs 1309, silent 2 in play (ticks 279, 2957), late 0, overwrites 0 | **P1 FALSIFIED, P2 FALSIFIED (read clause), P3 HELD** (lab-s8, lab/mmd bebfc3ab / de88173f); witness PARTIAL | 2026-09-27 |
| IOA0 | S16-IOARMS-HW (lab/metric 1dbb648f + dce69329 + 62dcbf82) arm OFF (no env); AUDH16's S16 fixture, 5 Days room 3, sound on, fine off | lab/mmd AGSIOH `80463ed30b91` (build_dirty 1, probe; main 4dd196a4) | 40.00 | 39.22 / 40.10 | pcm_irqs 1087, silent 2 (ticks 646, 3994), late 0, overwrites 0 | asset_open n=5 mean 55.2 max 56; capture=STALE (camera-only, operator decision); camera CLEAN | 2026-09-28 |
| IOES | S16-IOARMS-HW (lab/metric 1dbb648f + dce69329 + 62dcbf82) 0241 + shadow (DOSAGS_STATEXISTS=1 DOSAGS_EXISTSHADOW=1): the GATE; AUDH16's S16 fixture, 5 Days room 3, sound on, fine off | lab/mmd AGSIOH `80463ed30b91` (build_dirty 1, probe; main 4dd196a4) | 40.00 | 39.29 / 40.09 | pcm_irqs 919, silent 0, late 0, overwrites 0 | asset_open n=5 mean 65.0 max 65; **ES gate PASS** (compared 25, mismatches 0); capture=STALE (camera-only); camera CLEAN | 2026-09-28 |
| IO41 | S16-IOARMS-HW (lab/metric 1dbb648f + dce69329 + 62dcbf82) 0241 (DOSAGS_STATEXISTS=1); AUDH16's S16 fixture, 5 Days room 3, sound on, fine off | lab/mmd AGSIOH `80463ed30b91` (build_dirty 1, probe; main 4dd196a4) | 40.00 | 39.24 / 40.13 | pcm_irqs 881, silent 8 (ticks 279, 959, 2513, 4015), late 0, overwrites 0 | asset_open n=5 mean 21.2 max 22: **0241 saving 33.9 ms (pred 25-45): HOLDS**; capture=ok; camera CLEAN | 2026-09-28 |
| IO42 | S16-IOARMS-HW (lab/metric 1dbb648f + dce69329 + 62dcbf82) 0241+0242 (+DOSAGS_PAKHANDLE=1); AUDH16's S16 fixture, 5 Days room 3, sound on, fine off | lab/mmd AGSIOH `80463ed30b91` (build_dirty 1, probe; main 4dd196a4) | 40.00 | 39.25 / 40.15 | pcm_irqs 1323, silent 1 (tick 2484), late 0, overwrites 0 | asset_open n=4 mean 13.0 max 13; pakhandle opened=1: **0242 further saving 8.2 ms (pred 15-25): HOLDS** (falsifier < 5 ms; below the predicted range); capture=ok; camera CLEAN | 2026-09-28 |
| IO22 | S16-IOARMS-HW (lab/metric 1dbb648f + dce69329 + 62dcbf82) 0241+0242+0322 (+DOSAGS_PCM_ADOPT=1), informational repeat; AUDH16's S16 fixture, 5 Days room 3, sound on, fine off | lab/mmd AGSIOH `80463ed30b91` (build_dirty 1, probe; main 4dd196a4) | 40.00 | 39.27 / 40.14 | pcm_irqs 1208, silent 1 (tick 279), late 0, overwrites 0 | asset_open n=5 mean 13.0 max 13 -- reported only (lab-s8's 0322 arm); capture=ok; camera CLEAN | 2026-09-28 |
| IOA1 | S16-IOARMS-HW (lab/metric 1dbb648f + dce69329 + 62dcbf82) arm OFF (no env); AUDH16's S16 fixture, 5 Days room 3, sound on, fine off | lab/mmd AGSIOH `80463ed30b91` (build_dirty 1, probe; main 4dd196a4) | 40.00 | 39.24 / 40.08 | pcm_irqs 966, silent 2 (ticks 3495, 4495), late 0, overwrites 0 | asset_open n=5 mean 55.0 max 55; drift OFF-OFF 0.2 ms (VOID if > 10); capture=ok; camera CLEAN | 2026-09-28 |
| INCA1 | 0320 ABBA arm A (DOSAGS_PCM_INCR=0; lab/mmd 6bc62599 + e33f53be + 141e8167); round R's S8R1 fixture (Trilby room 35, sound on, fine off); pins STATEXISTS=1 PAKHANDLE=1 PCM_ADOPT=0 MIDI_MEM=1 | main 5bec55aa `d18d63368af6` | 40.00 | 39.18 / 40.25 | pcm_irqs 2162, silent 0, late 0, overwrites 0, underruns 0 | M1 848 ms; 486 gate bar MEETS; capture=STALE (512x384, stick present; camera is the witness), camera CLEAN | 2026-09-28 |
| INCB1 | as INCA1, arm B (DOSAGS_PCM_INCR=1) | main 5bec55aa `d18d63368af6` | 40.00 | 39.09 / 40.29 | pcm_irqs 2087, silent 1 in play (tick 972), late 0, overwrites 0, underruns 0 | M1 574 ms; gate bar DOES NOT MEET (tick 972); capture=STALE (512x384), camera CLEAN | 2026-09-28 |
| INCB2 | as INCB1 | main 5bec55aa `d18d63368af6` | 40.00 | 39.03 / 40.27 | pcm_irqs 2088, silent 0, late 0, overwrites 0, underruns 0 | M1 574 ms; gate bar MEETS; capture=STALE (512x384), camera CLEAN | 2026-09-28 |
| INCA2 | as INCA1 | main 5bec55aa `d18d63368af6` | 40.00 | **38.37** / 40.27 | pcm_irqs 2114, silent 0, late 0, overwrites 0, underruns 0 | M1 857 ms; abba320.py (d3dc8239): deltas -274 / -283 ms, drift 9 ms, prediction HELD; **VERDICT: NOT SEPARABLE** (B silent IRQs 1 vs A 0); capture=STALE (512x384), camera CLEAN | 2026-09-28 |
| S32FF0 | 0240 killswitch pair, DOSAGS_FADEFAST32=0 (lab/metric S32P-FF-HW + 00a30802 + 7d30fe8d + f5d2a7a6); S32P fixture (5 Days room 3, forced 32, 640x480 centred 1x, pack24, sound on, fine off) | main 5bec55aa `d18d63368af6` | 40.00 | 38.90 / 40.04 | pcm_irqs 661, silent 1 in play (tick 747), late 0, overwrites 0 | entry fade 2274 ms; S32 bar OUT; capture=ok, camera CLEAN | 2026-09-28 |
| S32FF1 | as S32FF0, DOSAGS_FADEFAST32=1 (0240 on) | main 5bec55aa `d18d63368af6` | 40.00 | 39.30 / 40.10 | pcm_irqs 662, silent 3 (ticks 76, 3916, 4916), late 0, overwrites 0 | entry fade 981 ms (0.43x), gain +0.40; lab-s32p-ff-hw.py (02a57e4d = 5786b508 output): **VERDICT: VOID (fast fade over 0.9 s but under 0.6x -- stated, not a pass)**; S32 bar IN; capture=ok, camera CLEAN | 2026-09-28 |
| ADPA1 | arm A (DOSAGS_PCM_ADOPT=0); 0322 safety ABBA (lab/mmd 017050ef); S16 fixture (5 Days room 3, sound on, fine off); pins STATEXISTS=1 PAKHANDLE=1 MIDI_MEM=1 PCM_INCR=0 | main d533b56d `ef123dba0adf` | 40.00 | 39.24 / 40.14 | pcm_irqs 834, silent 1 in play (tick 4932), late 0, overwrites 0, underruns 0 | adopted=0; stall100 361 ms; gate bar DOES NOT MEET; camera CLEAN (capture frozen in play) | 2026-09-28 |
| ADPB1 | as ADPA1, arm B (DOSAGS_PCM_ADOPT=1) | main d533b56d `ef123dba0adf` | 40.00 | 39.32 / 40.11 | pcm_irqs 1077, silent 2 in play (ticks 3962, 4465), late 0, overwrites 0, underruns 0 | adopted=5; stall100 290 ms; gate bar DOES NOT MEET; camera CLEAN | 2026-09-28 |
| ADPB2 | as ADPB1 | main d533b56d `ef123dba0adf` | 40.00 | 39.34 / 40.08 | pcm_irqs 760, silent 3 in play (ticks 699, 816, 4578), late 0, overwrites 0, underruns 0 | adopted=4; stall100 237 ms; gate bar DOES NOT MEET; camera CLEAN | 2026-09-28 |
| ADPA2 | as ADPA1 | main d533b56d `ef123dba0adf` | 40.00 | 39.32 / 40.10 | pcm_irqs 774, silent 1 in play (tick 1764), late 0, overwrites 0, underruns 0 | adopted=0; stall100 318 ms; abba322.py (c19cb451): silent B 5 vs A 2, drift 0.08; **VERDICT: KEEP OFF** (0322 stays OFF); camera CLEAN | 2026-09-28 |
| RPF1A | F1 (DOSAGS_RP_FAST unset, 0319 fast path); ags 0319 killswitch ABBA (lab/mmd 0b5aaeea); round B RTHB/RTHN recipe (5 Days room 3, sound OFF, drive 0, RT_BENCH 13 x3 + RT_RAND 300, TAS 1150, fine off) | lab-s8 AGSRPW `55959f2577ca` (main d533b56d + 0319 + probe, dirty 1) | 40.00 | 24.69 / 40.53 | sound off (no audio device) | rpcache fast=1 serial_hits=313 labels_ok=1; mean request 40.32 ms, worst 244.5 ms; camera CLEAN (capture frozen in play) | 2026-09-29 |
| RPF0A | as RPF1A, F0 (DOSAGS_RP_FAST=0) | lab-s8 AGSRPW `55959f2577ca` (main d533b56d + 0319 + probe, dirty 1) | 40.00 | 21.88 / 40.53 | sound off | rpcache fast=0 serial_hits=0; mean 57.65 ms, worst 173.0 ms; camera CLEAN | 2026-09-29 |
| RPF0B | as RPF0A | lab-s8 AGSRPW `55959f2577ca` (main d533b56d + 0319 + probe, dirty 1) | 40.00 | 21.92 / 40.53 | sound off | rpcache fast=0 serial_hits=0; mean 57.67 ms, worst 172.9 ms; camera CLEAN | 2026-09-29 |
| RPF1B | as RPF1A | lab-s8 AGSRPW `55959f2577ca` (main d533b56d + 0319 + probe, dirty 1) | 40.00 | 24.69 / 40.53 | sound off | rpcache fast=1 serial_hits=313 labels_ok=1; mean 40.25 ms, worst 244.6 ms; rp486.py (bdd54dc8): routes IDENTICAL, saving 30.1% / 30.2%; **VERDICT: LANDING GATES**; worst request ROSE +41% (prediction half not held, sent to lab-s8); camera CLEAN | 2026-09-29 |
| INCA3 | 0320 confirmation (lab/mmd cee07b0f + f227b8b6 + 7f0c43c9), arm A (DOSAGS_PCM_INCR=0); round V's INCA1 fixture and pins (Trilby room 35, sound on, fine off) (round X) | main 5bec55aa `d18d63368af6` | 40.00 | 38.46 / 40.26 | pcm_irqs 2169, silent 0, late 0, overwrites 0, underruns 0 | M1 855 ms; gate bar MEETS; capture=STALE (512x384), camera CLEAN | 2026-09-29 |
| INCB3 | as INCA3, arm B (DOSAGS_PCM_INCR=1) (round X) | main 5bec55aa `d18d63368af6` | 40.00 | 38.78 / 40.24 | pcm_irqs 2140, silent 1 in play (tick 903, SLICE-only), late 0, overwrites 0, underruns 0 | M1 575 ms; gate bar DOES NOT MEET (tick 903); capture=STALE (512x384), camera CLEAN | 2026-09-29 |
| INCB4 | as INCA3, arm B (DOSAGS_PCM_INCR=1) (round X) | main 5bec55aa `d18d63368af6` | 40.00 | 38.72 / 40.21 | pcm_irqs 2158, silent 0, late 0, overwrites 0, underruns 0 | M1 575 ms; gate bar MEETS; capture=STALE (512x384), camera CLEAN | 2026-09-29 |
| INCA4 | as INCA3 (round X) | main 5bec55aa `d18d63368af6` | 40.00 | 38.64 / 40.25 | pcm_irqs 2083, silent 0, late 0, overwrites 0, underruns 0 | M1 856 ms; gate bar MEETS; capture=STALE (512x384), camera CLEAN | 2026-09-29 |
| INCA5 | as INCA3 (round X2) | main 5bec55aa `d18d63368af6` | 40.00 | 38.80 / 40.26 | pcm_irqs 2168, silent 0, late 0, overwrites 0, underruns 0 | M1 856 ms; gate bar MEETS; capture=STALE (512x384), camera CLEAN | 2026-09-29 |
| INCB5 | as INCA3, arm B (DOSAGS_PCM_INCR=1) (round X2) | main 5bec55aa `d18d63368af6` | 40.00 | 38.71 / 40.25 | pcm_irqs 2106, silent 0, late 0, overwrites 0, underruns 0 | M1 577 ms; gate bar MEETS; capture=STALE (512x384), camera CLEAN | 2026-09-29 |
| INCB6 | as INCA3, arm B (DOSAGS_PCM_INCR=1) (round X2) | main 5bec55aa `d18d63368af6` | 40.00 | 38.59 / 40.29 | pcm_irqs 2130, silent 0, late 0, overwrites 0, underruns 0 | M1 576 ms; gate bar MEETS; capture=STALE (512x384), camera CLEAN | 2026-09-29 |
| INCA6 | as INCA3 (round X2) | main 5bec55aa `d18d63368af6` | 40.00 | 38.68 / 40.23 | pcm_irqs 2097, silent 0, late 0, overwrites 0, underruns 0 | M1 858 ms; gate bar MEETS; capture=STALE (512x384), camera CLEAN; abba320c.py (7f0c43c9) pooled V+X+X2: deltas -274/-283, -280/-281, -279/-282 ms, Fisher p 0.227, SLICE-ONLY INCB3 tick 903 -> **VERDICT: KEEP OFF** (0320 stays OFF) | 2026-09-29 |
| IOB0 | S16-IOARMS2-HW (lab/metric 167e2a91), arm OFF (DIRCACHE=0 READDIRECT=0); round U's S16 fixture (5 Days room 3, sound on, fine off); pins STATEXISTS=1 PAKHANDLE=1 MIDI_MEM=1 PCM_ADOPT=0 PCM_INCR=0 | lab-s32 us probe `labUSY0` (main d533b56d + usprobe, dirty 1; sha256 3d4f1c1d...) | 40.00 | 39.29 / 40.10 | pcm_irqs 1034, silent 1 in play (tick 982), late 0, overwrites 0, underruns 0 | asset_open 13.99 ms; fade 626 ms; gate bar DOES NOT MEET; SUMMARY STAMP-VOID = driver regex error (RUNMANI labUSY0, pre/post 3d4f1c1d54fe); camera CLEAN (capture frozen in play) | 2026-09-29 |
| IODS | as IOB0, arm 0245+shadow (DIRCACHE=1 SHADOW=1), the gate | lab-s32 us probe `labUSY0` (main d533b56d + usprobe, dirty 1; sha256 3d4f1c1d...) | 40.00 | 39.18 / 40.09 | pcm_irqs 1053, silent 0, late 0, overwrites 0, underruns 0 | asset_open 13.92 ms; gate PASS (21/0); fade 886 ms; gate bar MEETS; SUMMARY STAMP-VOID = driver regex error (RUNMANI labUSY0, pre/post 3d4f1c1d54fe); camera CLEAN (capture frozen in play) | 2026-09-29 |
| IODC | as IOB0, arm 0245 (DIRCACHE=1) | lab-s32 us probe `labUSY0` (main d533b56d + usprobe, dirty 1; sha256 3d4f1c1d...) | 40.00 | 39.20 / 40.09 | pcm_irqs 1350, silent 2 in play (ticks 591, 723), late 0, overwrites 0, underruns 0 | asset_open 1.65 ms; fade 865 ms; gate bar DOES NOT MEET; SUMMARY STAMP-VOID = driver regex error (RUNMANI labUSY0, pre/post 3d4f1c1d54fe); camera CLEAN (capture frozen in play) | 2026-09-29 |
| IORD | as IOB0, arm 0246 (READDIRECT=1) | lab-s32 us probe `labUSY0` (main d533b56d + usprobe, dirty 1; sha256 3d4f1c1d...) | 40.00 | 39.30 / 40.10 | pcm_irqs 939, silent 1 in play (tick 3418), late 0, overwrites 0, underruns 0 | asset_open 13.76 ms; fade 623 ms; gate bar DOES NOT MEET; SUMMARY STAMP-VOID = driver regex error (RUNMANI labUSY0, pre/post 3d4f1c1d54fe); camera CLEAN (capture frozen in play) | 2026-09-29 |
| IOBB | as IOB0, arm 0245+0246 | lab-s32 us probe `labUSY0` (main d533b56d + usprobe, dirty 1; sha256 3d4f1c1d...) | 40.00 | 39.22 / 40.02 | pcm_irqs 997, silent 3 in play (ticks 673, 1811, 4059), late 0, overwrites 0, underruns 0 | asset_open 1.66 ms; fade 866 ms; gate bar DOES NOT MEET; SUMMARY STAMP-VOID = driver regex error (RUNMANI labUSY0, pre/post 3d4f1c1d54fe); camera CLEAN (capture frozen in play) | 2026-09-29 |
| IOB1 | as IOB0, arm OFF (as IOB0) | lab-s32 us probe `labUSY0` (main d533b56d + usprobe, dirty 1; sha256 3d4f1c1d...) | 40.00 | 39.32 / 40.06 | pcm_irqs 730, silent 1 in play (tick 738), late 0, overwrites 0, underruns 0 | asset_open 14.15 ms (n=3); fade 623 ms; lab-io2-hw.py (ee0de7b0): **0245 HOLDS 12.42 ms, audio not clean; 0246 HOLDS 9.95 vs 20.13 ms midpoint, audio clean**; drift 0.16 ms; SUMMARY STAMP-VOID = driver regex error (RUNMANI labUSY0, pre/post 3d4f1c1d54fe); camera CLEAN (capture frozen in play) | 2026-09-29 |
| WBD8P | WB S8 poll control (lab/wb 4a4585d0 + c080538f; DOSAGS_MIDI_TICK=poll); Trilby room 35 at 640x480 centred 1x, WB backend, pump + PREROLL_MS=200 hints, TAS 6500, fine off | main d533b56d `ef123dba0adf` | 40.00 | 39.16 / 40.25 | midi_tick=poll; WB MIDI | D 0.280 (information); capture locked; camera CLEAN | 2026-09-29 |
| WBD8R | as WBD8P, pump arm (midi_tick rtc) | main d533b56d `ef123dba0adf` | 40.00 | 39.15 / 40.22 | midi_tick=rtc, late_writes 0, preroll=5/198/422/3, clk 0.9672 | depth-score.py (c080538f): A PASS, B PASS (chroma 0.957), D 0.288 -> **VERDICT: FAIL** (D < 0.70: one re-run per the operator rule); capture locked; camera CLEAN | 2026-09-29 |
| WBD32P | WB S32P poll control (lab/wb 4a4585d0 + c080538f; DOSAGS_MIDI_TICK=poll); 5 Days room 3, forced 32, 640x480 centred 1x, pack24, WB pump hint, TAS 6500, fine off | main d533b56d `ef123dba0adf` | 40.00 | 39.37 / 40.05 | midi_tick=poll; WB MIDI | D 0.727 (information); capture locked; camera CLEAN | 2026-09-29 |
| WBD32R | as WBD32P, pump arm (midi_tick rtc) | main d533b56d `ef123dba0adf` | 40.00 | 39.39 / 40.06 | midi_tick=rtc, late_writes 0, preroll=0/0/0/0, clk 1.0007, bytes 99.9% | depth-score.py (c080538f): A PASS, B PASS (chroma 0.905), D 0.630 -> **VERDICT: FAIL** (D < 0.70: one re-run per the operator rule); capture locked; camera CLEAN | 2026-09-29 |
| RRF1A | F1 (DOSAGS_RP_FAST unset); 0319 re-cut 2 killswitch ABBA (lab/mmd 54f4ff73); RP486's W2 fixture (5 Days room 3, sound OFF, drive 0, RT_BENCH 13 x3 + RT_RAND 300, TAS 1150, fine off) | lab-s8 AGSRPW2 `514d0a6cb094` (main d533b56d + 0319 re-cut 2 + probe, dirty 1) | 40.00 | 24.56 / 40.53 | sound off (no audio device) | rpcache fast=1 serial_hits=313 labels_ok=1 label_us=10482; mean 40.43 ms, worst 173.0 ms; camera CLEAN; capture STALE(nolock) | 2026-09-29 |
| RRF0A | as RRF1A, F0 (DOSAGS_RP_FAST=0) | lab-s8 AGSRPW2 `514d0a6cb094` (main d533b56d + 0319 re-cut 2 + probe, dirty 1) | 40.00 | 21.89 / 40.53 | sound off | rpcache fast=0 serial_hits=0; mean 57.27 ms, worst 171.8 ms; camera CLEAN | 2026-09-29 |
| RRF0B | as RRF0A | lab-s8 AGSRPW2 `514d0a6cb094` (main d533b56d + 0319 re-cut 2 + probe, dirty 1) | 40.00 | 21.89 / 40.53 | sound off | rpcache fast=0 serial_hits=0; mean 57.27 ms, worst 171.9 ms; camera CLEAN | 2026-09-29 |
| RRF1B | as RRF1A | lab-s8 AGSRPW2 `514d0a6cb094` (main d533b56d + 0319 re-cut 2 + probe, dirty 1) | 40.00 | 24.55 / 40.53 | sound off | rpcache fast=1 serial_hits=313 labels_ok=1 label_us=10345; mean 40.46 ms, worst 172.8 ms; rp486b.py (240dd83f): routes IDENTICAL, saving 29.4% / 29.3%, worst -0.7% / -0.5%; **VERDICT: LANDING GATES**; P-row0 MISSED, P-label MISSED, P-mean HELD; camera CLEAN | 2026-09-29 |
| Z3A1 | Z3 MEASUREMENT (lab/mmd 15fca729 + b77e6948), arm A (PCM_INCR=0); round V's S8 recipe (Trilby room 35, sound on, fine off); pins STATEXISTS=1 PAKHANDLE=1 PCM_ADOPT=0 MIDI_MEM=1 | lab-s8 AGSLAC4 `2f73bacd1f95` (main d533b56d + look-ahead candidate + buffered probe, dirty 1) | 40.00 | 39.27 / 40.31 | pcm_irqs 2051, silent 1 (tick 1252, EOD SLICE), late 0, overwrites 0, underruns 0 | M1 869 ms; sound11 margin/gap 170.2 / 76.8 ms; sound18 175.6 / 714.4 ms; cost 10573 ns/rec; camera CLEAN | 2026-09-29 |
| Z3B1 | as Z3A1, arm B (PCM_INCR=1) | lab-s8 AGSLAC4 `2f73bacd1f95` (main d533b56d + look-ahead candidate + buffered probe, dirty 1) | 40.00 | 38.82 / 40.25 | pcm_irqs 2104, silent 0, late 0, overwrites 0, underruns 0 | M1 576 ms; sound11 margin/gap 160.8 / 71.6 ms; sound18 120.9 / 370.5 ms; cost 11146 ns/rec; camera CLEAN | 2026-09-29 |
| Z3C1 | as Z3A1, arm C (PCM_INCR=1 + PCM_LOOKAHEAD=2) | lab-s8 AGSLAC4 `2f73bacd1f95` (main d533b56d + look-ahead candidate + buffered probe, dirty 1) | 40.00 | 39.18 / 40.28 | pcm_irqs 2094, silent 0, late 0, overwrites 0, underruns 0 | M1 563 ms; sound11 margin/gap 160.2 / 66.4 ms; sound18 167.4 / 369.3 ms; cost 11143 ns/rec; camera CLEAN | 2026-09-29 |
| Z3C2 | as Z3A1, arm C | lab-s8 AGSLAC4 `2f73bacd1f95` (main d533b56d + look-ahead candidate + buffered probe, dirty 1) | 40.00 | 39.28 / 40.25 | pcm_irqs 2101, silent 0, late 0, overwrites 0, underruns 0 | M1 562 ms; sound11 margin/gap 160.1 / 66.8 ms; sound18 125.4 / 369.4 ms; cost 10561 ns/rec; camera CLEAN | 2026-09-29 |
| Z3B2 | as Z3A1, arm B | lab-s8 AGSLAC4 `2f73bacd1f95` (main d533b56d + look-ahead candidate + buffered probe, dirty 1) | 40.00 | 38.55 / 40.25 | pcm_irqs 2134, silent 0, late 0, overwrites 0, underruns 0 | M1 574 ms; sound11 margin/gap 161.0 / 72.2 ms; sound18 123.4 / 368.1 ms; cost 11139 ns/rec; camera CLEAN | 2026-09-29 |
| Z3A2 | as Z3A1, arm A | lab-s8 AGSLAC4 `2f73bacd1f95` (main d533b56d + look-ahead candidate + buffered probe, dirty 1) | 40.00 | 38.65 / 40.29 | pcm_irqs 2108, silent 0, late 0, overwrites 0, underruns 0 | M1 933 ms; sound11 margin/gap 170.1 / 76.9 ms; sound18 176.5 / 777.2 ms; cost 10553 ns/rec; camera CLEAN; z3.py (912453a5): MEASUREMENT ONLY, no verdict, no flip | 2026-09-29 |
| GS8A | Gate S8 re-reading (round R S8R line: Trilby room 35, walk, sound on, fine off), player default | main b7ac6c46 `3074cd9ce099` | 40.00 | 39.19 / 40.24 | pcm_irqs 2102, silent 0, late 0, overwrites 0, underruns 0 | skipped 47, stall_ms 1942; completeness 99.06%; camera CLEAN; capture STALE | 2026-09-29 |
| GS8B | as GS8A | main b7ac6c46 `3074cd9ce099` | 40.00 | **38.51** / 40.28 | pcm_irqs 2101, silent 0, late 0, overwrites 0, underruns 0 | skipped 45, stall_ms 4315; **S8 NOT MET** (whole-run 0.01 / 0.69 under); camera CLEAN | 2026-09-29 |
| GS16A | Gate S16 re-reading (round Q S16Q line: 5 Days room 3, walk, sound on, fine off), player default | main b7ac6c46 `3074cd9ce099` | 40.00 | 39.28 / 40.10 | pcm_irqs 988, **silent 2 in play (ticks 1864, 4494)**, late 0, overwrites 0, underruns 0 | skipped 30, stall_ms 1097; completeness 99.40%; camera CLEAN; capture STALE | 2026-09-29 |
| GS16B | as GS16A | main b7ac6c46 `3074cd9ce099` | 40.00 | 39.31 / 40.10 | pcm_irqs 1129, silent 0, late 0, overwrites 0, underruns 0 | skipped 27; **S16 NOT MET on audio only** (ticks in band x2); camera CLEAN | 2026-09-29 |
| GS32A | Gate S32 re-reading on S32P (5 Days room 3, forced 32, 640x480 centred 1x, pack24, walk, sound on, fine off), player default | main b7ac6c46 `3074cd9ce099` | 40.00 | 39.32 / 40.12 | pcm_irqs 379, **silent 2 in play (ticks 921, 1421)**, late 0, overwrites 0, underruns 0 | skipped 18; completeness 99.64%; camera CLEAN; capture ok | 2026-09-29 |
| GS32B | as GS32A | main b7ac6c46 `3074cd9ce099` | 40.00 | 39.28 / 40.08 | pcm_irqs 601, **silent 1 in play (tick 4912)**, late 0, overwrites 0, underruns 0 | skipped 25; **S32 NOT MET on audio only** (ticks in band x2); camera CLEAN | 2026-09-29 |
| IDA1 | 0320 candidacy-2 decisive test (lab/mmd 3804a35d), arm A (PCM_INCR=0); round V S8 recipe (Trilby room 35, sound on, fine off); pins STATEXISTS/PAKHANDLE/PCM_ADOPT=0/MIDI_MEM (round ID1) | main b7ac6c46 + lab 0323 `f17997f06baa` | 40.00 | 39.08 / 40.26 | pcm_irqs 2141, silent 0, late 0, overwrites 0, underruns 0 | M1 892 ms; capture=STALE (512x384), camera CLEAN | 2026-09-29 |
| IDD1 | as IDA1, arm D (PCM_INCR=1 + PCM_INCR_MIN=8) (round ID1) | main b7ac6c46 + lab 0323 `f17997f06baa` | 40.00 | 38.61 / 40.25 | pcm_irqs 2132, silent 0, late 0, overwrites 0, underruns 0 | M1 545 ms; capture=STALE (512x384), camera CLEAN | 2026-09-29 |
| IDD2 | as IDA1, arm D (PCM_INCR=1 + PCM_INCR_MIN=8) (round ID1) | main b7ac6c46 + lab 0323 `f17997f06baa` | 40.00 | 39.16 / 40.26 | pcm_irqs 2152, silent 1 in play (tick 876, SLICE-only), late 0, overwrites 0, underruns 0 | M1 544 ms; capture=STALE (512x384), camera CLEAN | 2026-09-29 |
| IDA2 | as IDA1 (round ID1) | main b7ac6c46 + lab 0323 `f17997f06baa` | 40.00 | 39.18 / 40.24 | pcm_irqs 2041, silent 1 in play (tick 1037, SLICE), late 0, overwrites 0, underruns 0 | M1 836 ms; capture=STALE (512x384), camera CLEAN | 2026-09-29 |
| IDA3 | as IDA1 (round ID2) | main b7ac6c46 + lab 0323 `f17997f06baa` | 40.00 | 39.08 / 40.20 | pcm_irqs 2120, silent 0, late 0, overwrites 0, underruns 0 | M1 841 ms; capture=STALE (512x384), camera CLEAN | 2026-09-29 |
| IDD3 | as IDA1, arm D (PCM_INCR=1 + PCM_INCR_MIN=8) (round ID2) | main b7ac6c46 + lab 0323 `f17997f06baa` | 40.00 | 38.75 / 40.25 | pcm_irqs 2097, silent 0, late 0, overwrites 0, underruns 0 | M1 547 ms; capture=STALE (512x384), camera CLEAN | 2026-09-29 |
| IDD4 | as IDA1, arm D (PCM_INCR=1 + PCM_INCR_MIN=8) (round ID2) | main b7ac6c46 + lab 0323 `f17997f06baa` | 40.00 | 39.37 / 40.24 | pcm_irqs 2164, silent 0, late 0, overwrites 0, underruns 0 | M1 546 ms; capture=STALE (512x384), camera CLEAN | 2026-09-29 |
| IDA4 | as IDA1 (round ID2) | main b7ac6c46 + lab 0323 `f17997f06baa` | 40.00 | 39.31 / 40.27 | pcm_irqs 2153, silent 0, late 0, overwrites 0, underruns 0 | M1 840 ms; capture=STALE (512x384), camera CLEAN | 2026-09-29 |
| IDA5 | as IDA1 (round ID3) | main b7ac6c46 + lab 0323 `f17997f06baa` | 40.00 | 38.58 / 40.22 | pcm_irqs 2105, silent 0, late 0, overwrites 0, underruns 0 | M1 842 ms; capture=STALE (512x384), camera CLEAN | 2026-09-29 |
| IDD5 | as IDA1, arm D (PCM_INCR=1 + PCM_INCR_MIN=8) (round ID3) | main b7ac6c46 + lab 0323 `f17997f06baa` | 40.00 | 38.86 / 40.26 | pcm_irqs 2208, silent 2 in play (ticks 788 SLICE-only, 968 EOD SLICE), late 0, overwrites 0, underruns 0 | M1 545 ms; capture=STALE (512x384), camera CLEAN | 2026-09-29 |
| IDD6 | as IDA1, arm D (PCM_INCR=1 + PCM_INCR_MIN=8) (round ID3) | main b7ac6c46 + lab 0323 `f17997f06baa` | 40.00 | 38.73 / 40.23 | pcm_irqs 2191, silent 0, late 0, overwrites 0, underruns 0 | M1 547 ms; capture=STALE (512x384), camera CLEAN | 2026-09-29 |
| IDA6 | as IDA1 (round ID3) | main b7ac6c46 + lab 0323 `f17997f06baa` | 40.00 | 38.84 / 40.25 | pcm_irqs 2133, silent 0, late 0, overwrites 0, underruns 0 | M1 841 ms; capture=STALE (512x384), camera CLEAN; abba320d.py (b2f83e52, clock fix) pooled: deltas -347/-292, -294/-294, -297/-294 ms, Fisher p 0.500, SLICE-ONLY D IDD2 t876 + IDD5 t788 -> **VERDICT: KEEP OFF** (0320 stays OFF) | 2026-09-29 |
| WBC8P | WB clean S8 poll control (lab/wb d4b2db0c; DOSAGS_MIDI_TICK=poll); Trilby room 40 idle (music 10, no PCM), 640x480 centred 1x, WB pump + PREROLL_MS=200 hints, TAS 6500, fine off | main d533b56d `ef123dba0adf` | 40.00 | 39.04 / 58.03 | midi_tick=poll; no PCM play | D 0.864 (information); capture locked; camera CLEAN | 2026-09-29 |
| WBC8R | as WBC8P, pump arm (midi_tick rtc) | main d533b56d `ef123dba0adf` | 40.00 | 39.09 / 57.66 | midi_tick=rtc, late_writes 0, preroll 5/75/175/3, clk 1.0033, bytes 100.0% | depth-score.py (d4b2db0c, --no-pcm): A PASS, B PASS (chroma 0.990), D 0.843 -> **VERDICT: PASS**; capture locked; camera CLEAN | 2026-09-29 |
| WBC32P | WB clean S32P poll control (lab/wb d4b2db0c; DOSAGS_MIDI_TICK=poll); 5 Days room 13 idle (music 0, no PCM), forced 32, 640x480 centred 1x, pack24, WB pump hint, TAS 6500, fine off | main d533b56d `ef123dba0adf` | 40.00 | 39.43 / 40.01 | midi_tick=poll; no PCM play | D 0.802 (information); capture locked; camera CLEAN | 2026-09-29 |
| WBC32R | as WBC32P, pump arm (midi_tick rtc) | main d533b56d `ef123dba0adf` | 40.00 | 39.44 / 40.01 | midi_tick=rtc, late_writes 0, preroll 0/0/0/0, clk 1.0000, bytes 99.8% | depth-score.py (d4b2db0c, --no-pcm): A PASS, B PASS (chroma 0.940), D 0.780 -> **VERDICT: PASS**; capture locked; camera CLEAN | 2026-09-29 |
| CSV16H1 | probe v3 486 round (lab/mmd COLDSTART3.md "486 ROUND"), Gate S16 line (5 Days room 3, 512x384, walk, sound on, fine off), player default (round CS1) | main b7ac6c46 + probe v3 `95519022159e` | 40.00 | 39.26 / 40.12 | pcm_irqs 787, silent 0, late 0, overwrites 0, underruns 0 | 9 cold starts, no charges; capture=STALE (512x384), camera CLEAN | 2026-09-29 |
| CSV32H1 | as CSV16H1 on the Gate S32P line (forced 32, 640x480 centred 1x, pack24) (round CS1) | main b7ac6c46 + probe v3 `95519022159e` | 40.00 | 39.25 / 40.10 | pcm_irqs 263, silent 2 in play (ticks 913, 4913), late 0, overwrites 0, underruns 0 | both IN-PUMP (priming pumps of lc 911 / 4911); capture ok, camera CLEAN | 2026-09-29 |
| CSV16H2 | as CSV16H1 (round CS1) | main b7ac6c46 + probe v3 `95519022159e` | 40.00 | 39.30 / 40.12 | pcm_irqs 1094, silent 1 in play (tick 2297), late 0, overwrites 0, underruns 0 | FEED (lc 2295 priming pump, fill 0); capture=STALE (512x384), camera CLEAN | 2026-09-29 |
| CSV32H2 | as CSV32H1 (round CS1) | main b7ac6c46 + probe v3 `95519022159e` | 40.00 | 39.34 / 40.09 | pcm_irqs 324, silent 0, late 0, overwrites 0, underruns 0 | 6 cold starts, no charges; capture ok, camera CLEAN | 2026-09-29 |
| CSV16H3 | as CSV16H1 (round CS1) | main b7ac6c46 + probe v3 `95519022159e` | 40.00 | 39.29 / 40.14 | pcm_irqs 221, silent 1 in play (tick 784), late 0, overwrites 0, underruns 0 | IN-PUMP (priming pump of lc 782); capture=STALE (512x384), camera CLEAN | 2026-09-29 |
| CSV32H3 | as CSV32H1 (round CS1) | main b7ac6c46 + probe v3 `95519022159e` | 40.00 | 39.26 / 40.09 | pcm_irqs 300, silent 0, late 0, overwrites 0, underruns 0 | 5 cold starts, no charges; timeout capped to 1736 s; capture ok, camera CLEAN | 2026-09-29 |
| CSV8H1 | as CSV16H1 on the Gate S8 line (Trilby room 35, 512x384, walk, sound on, fine off, no MSGSKIP) (round CS2) | main b7ac6c46 + probe v3 `95519022159e` | 40.00 | 38.98 / 40.25 | pcm_irqs 2069, silent 1 in play (tick 1037), late 0, overwrites 0, underruns 0 | IN-PUMP (priming pump of lc 1036, the sound11 spot); capture=STALE (512x384), camera CLEAN | 2026-09-29 |
| CSV8H2 | as CSV8H1 (round CS2) | main b7ac6c46 + probe v3 `95519022159e` | 40.00 | 38.94 / 40.32 | pcm_irqs 2111, silent 0, late 0, overwrites 0, underruns 0 | 2 cold starts, no charges; capture=STALE (512x384), camera CLEAN | 2026-09-29 |
| CSV8H3 | as CSV8H1 (round CS2) | main b7ac6c46 + probe v3 `95519022159e` | 40.00 | 39.01 / 40.28 | pcm_irqs 2148, silent 0, late 0, overwrites 0, underruns 0 | 2 cold starts, no charges; coldstart3.py (3a55115d) pooled over 9 cells: all CONSISTENT; IN-PUMP 4, FEED 1, GAP 0, OWED 0; P1 HELD, P2 FALSIFIED as written (tick window; same pump seq, a reading), P3 not reproduced | 2026-09-29 |
| GM8A | Gate S8 re-reading with DOSAGS_MSGSKIP=1 (round GATE's GS8 line: Trilby room 35, walk, sound on, fine off), no other pins (round S8M) | main a504b469 `d8c3aa2eafdf` | 40.00 | 39.21 / 40.16 | pcm_irqs 2124, silent 0, late 0, overwrites 0, underruns 0 | skipped 48, stall_ms 1607; completeness 100.28% / 99.04%; one msgskip n=1; camera CLEAN; capture STALE | 2026-09-29 |
| GM8B | as GM8A (round S8M) | main a504b469 `d8c3aa2eafdf` | 40.00 | 39.21 / 40.24 | pcm_irqs 2079, silent 0, late 0, overwrites 0, underruns 0 | skipped 43, stall_ms 1641; completeness 100.28% / 99.14%; one msgskip n=1; camera CLEAN; **the bar MET x2** (whole-run 0.01 over the floor, as recorded); not comparable with pre-MSGSKIP S8 whole-run | 2026-09-29 |
| GL16A | Gate S16 re-read under the ags 0347 counter (round GATE's GS16 line: 5 Days room 3, 512x384, walk, sound on, fine off), player default (round BATCH) | main 553588d4 `8249193ed041` | 40.00 | 39.29 / 40.13 | pcm_irqs 939, silent 0, startlat 0, late 0, overwrites 0, underruns 0 | skipped 21, stall_ms 1107; completeness 100.24% / 99.58%; camera CLEAN; capture STALE | 2026-09-30 |
| GL16B | as GL16A (round BATCH) | main 553588d4 `8249193ed041` | 40.00 | 39.29 / 40.10 | pcm_irqs 725, silent 0, startlat 1 (t1914), late 0, overwrites 0, underruns 0 | skipped 34, stall_ms 1039; completeness 100.24% / 99.32%; camera CLEAN; gatebar.py: **S16 bar MET x2** (capture listen outstanding) | 2026-09-30 |
| GL32A | Gate S32 re-read under the ags 0347 counter (round GATE's GS32 S32P line: 5 Days room 3, forced 32, 640x480 centred 1x, pack24, walk), player default (round BATCH) | main 553588d4 `8249193ed041` | 40.00 | 39.28 / 40.12 | pcm_irqs 727, silent 0, startlat 0, late 0, overwrites 0, underruns 0 | skipped 18, stall_ms 1391; completeness 100.24% / 99.64%; camera CLEAN; capture ok | 2026-09-30 |
| GL32B | as GL32A (round BATCH) | main 553588d4 `8249193ed041` | 40.00 | 39.34 / 40.07 | pcm_irqs 354, silent 0, startlat 3 (t2413, 3914, 4913), late 0, overwrites 0, underruns 0 | skipped 19, stall_ms 1028; completeness 100.24% / 99.62%; camera CLEAN; gatebar.py: **S32 bar MET x2** (capture listen outstanding) | 2026-09-30 |
| GL8A | Gate S8 re-read under the ags 0347 counter (round S8M's GM8 line: Trilby room 35, 512x384, walk, DOSAGS_MSGSKIP=1) (round BATCH) | main 553588d4 `8249193ed041` | 40.00 | 39.26 / 40.23 | pcm_irqs 2048, silent 0, startlat 0, late 0, overwrites 0, underruns 0 | skipped 51, stall_ms 1646; completeness 100.28% / 98.98%; one msgskip n=1; camera CLEAN; capture STALE | 2026-09-30 |
| GL8B | as GL8A (round BATCH) | main 553588d4 `8249193ed041` | 40.00 | 39.35 / 40.29 | pcm_irqs 2118, silent 0, startlat 0, late 0, overwrites 0, underruns 0 | skipped 34, stall_ms 1568; completeness 100.28% / 99.32%; one msgskip n=1; camera CLEAN; gatebar.py: **S8 bar MET x2** (CAPS8 listen by lab-wb) | 2026-09-30 |
| CAPS8 | S8 capture check at 640x480 (lab/wb caff563d; round S8M's GM8A line + DOSAGS_MSGSKIP=1, S32P cfg + MAX_SCALE=1, MIN_WAIT 300) (round BATCH) | main 553588d4 `8249193ed041` | 40.00 | 39.29 / 40.16 | pcm_irqs 2069 + inflight 19 = mixed 2088, silent 0 (0347), startlat 0, late 0, overwrites 0, underruns 0 | capture-check.py (caff563d; lab/wb 37bf008c): K1 0 zero frames, K2 worst 24.7 dB (< 25: PASS; information: one 11.6 ms frame at 299.25 s), K3 NCC 0.41 vs null 0.14, K4 >= 52.8 / 47.8 dB, K5 clean -> **CAPTURE CHECK PASS (S8 640x480 capture listen closed by score)**; capture locked; camera CLEAN | 2026-09-30 |
| WBC16P | WB clean S16 poll control (lab/wb c9e25c2c; DOSAGS_MIDI_TICK=poll); 5 Days room 13 idle (music 0, no PCM), native 16-bit, 640x480 centred 1x, WB pump hint, TAS 6500, fine off (round BATCH) | main d533b56d `ef123dba0adf` | 40.00 | 39.48 / 40.01 | midi_tick=poll; no PCM play | D 0.794 (information); capture locked; camera CLEAN | 2026-09-30 |
| WBC16R | as WBC16P, pump arm (midi_tick rtc) (round BATCH) | main d533b56d `ef123dba0adf` | 40.00 | 39.50 / 40.01 | midi_tick=rtc, late_writes 0, preroll 0/0/0/0, clk 0.9995, bytes 99.9% | depth-score.py (caff563d registered invocation; lab/wb 37bf008c): A PASS, B PASS (chroma 0.973 vs bar 0.634), D 0.785 -> **VERDICT: PASS**; WB bar now PASS at S8 / S16 / S32P on ef123dba0adf; capture locked; camera CLEAN | 2026-09-30 |
| CAPS16 | S16 capture check at 640x480 (lab/wb eaa7c4fc + 6def499d; round BATCH's GL16 line with S32P cfg + MAX_SCALE=1, 16-bit kept, MIN_WAIT 300) (round CAPS) | main 3aee50b4 `64d449a5b895` | 40.00 | 39.36 / 40.12 | pcm_irqs 354 = mixed 354, silent 0, startlat 0, late 0, overwrites 0, **underruns 6** (= primes 6; 0 on every pre-0348 cell; lab-s8 investigating) | capture-check3.py (33cde13b; lab/wb 4194baf5, coordinator re-run): K1-K4 PASS, **M1 +1 cent** (pre-fix OPL3 +91), **M2 0.809** -> **CAPTURE CHECK PASS (S16 640x480 capture listen closed by score)**; capture locked; camera CLEAN | 2026-09-30 |
| CAPS32 | S32 capture check at 640x480 (lab/wb eaa7c4fc + 6def499d; round BATCH's GL32 line verbatim) (round CAPS) | main 3aee50b4 `64d449a5b895` | 40.00 | 39.26 / 40.09 | pcm_irqs 748 = mixed 748, silent 0, startlat 0, late 0, overwrites 0, **underruns 6** (= primes 6) | **VOID as registered**: no "Playing sound 3" (sounds 10 x3, 9 x1); re-run once as CAPS32R (lab/wb 49aa373f), held for the 0348 underruns question; capture locked; camera CLEAN | 2026-09-30 |
| CAPS32R | the CAPS32 re-run (lab/wb 49aa373f rule + 32378c49 binary; round BATCH's GL32 line verbatim) (round C32R) | main 8f439c0f `e3a83135dc9c` | 40.00 | 39.29 / 40.12 | pcm_irqs 483 = mixed 483, silent 0, startlat 0, late 0, overwrites 0, underruns 0 | capture-check3.py (33cde13b; lab/wb e042cbad, coordinator re-run): K1 0, K2 longest 1 frame, K3 0.61 vs null 0.52, **M1 +1 cent**, **M2 0.801**, K4 >= 33.3 / 33.8 dB, K5 clean -> **CAPTURE CHECK PASS (S32 640x480 capture listen closed by score)**; capture locked; camera CLEAN | 2026-09-30 |

WBLR2 note (2026-09-26): operator override ~16:55Z 2026-09-26 (question tool) of LAB-WB 38's "landing waits"
branch -> the WB RTC-pump series (SDL 0260-0267 + ags 0340-0345, opt-in via SDL_HINT_DOS_AUDIO_WB_RTC_PUMP=1) landed
on main in the commit that adds this note, WBLR2 being the landing run. Round R's rows stand as recorded.

## Test infrastructure

- `tests/harness/` -- AGS Quest AutoPilot harness (18 phases, screenshot
  hash regression, DOSBox-X + `run-hw.sh` real-hardware flow).
- `tools/port-game/` -- the Game porting framework (`inspect`,
  `convert`, `repack`, `layout`, `validate`, `record`, `all`), manifests
  under `tests/games/<id>/`.
- `tests/fixtures/minimal-game-package/` -- synthetic package generator
  used for TITLE_SCREEN; the real test game is planned in PLAN.md
  ("First test game -- authoring plan").
- `tests/probes/` -- isolated DJGPP/SDL/DOSBox-X probes.
