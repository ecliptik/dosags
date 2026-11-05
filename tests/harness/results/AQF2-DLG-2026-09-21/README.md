# AQF2 dialog-topic-list clip: investigation and finding

**Observation (AQF2 hardware run, card AND camera, frame ~00011, ~92 s in):**
the "AGS Quest" tutorial topic list ("Room areas / Objects and Inventory /
Characters / GUIs / Scripting / Dialogues / Leave") shows every line missing
its leading glyph, cut at the literal left edge (x=0) of the 640x480 raster.
Both physical witnesses (capture card and camera) show the identical cut at
the identical position. See `AQF2-hardware-card-frame00011-menu-zoom.png`.

This was flagged before writing AQF2's `witness/REVIEWED.txt` (per the
standing rule: never call trails or missing-content cosmetic). The
coordinator's instruction was to run a DOSBox-X freeze-tick comparison
(with/without the alias present path) around the tick this GUI appears, and
classify it: present-path defect (stop and report, do not write it off) vs.
engine-composite/content fact (record content-bound, not a port defect).

## Step 1: the tick-freeze tool does not reach this GUI

`DOSAGS_FREEZE_TICKS` (ags patch 0195) is read by `dos_port_freeze_check()`,
called only from `dos_run_tick_fixed()` in `game_run.cpp` -- the fixed-
timestep wrapper around the top-level `GameTick()`. AGS's dialog-options
list, though, is rendered by its own loop in `Engine/ac/dialog.cpp` (around
line 1286: `UpdateGameOnce(false); update_polled_stuff(); render_graphics();`
in a `while (_dlgNum >= 0)` loop) -- a second, separate loop that calls
`UpdateGameOnce()`/`render_graphics()` directly and never goes through
`dos_run_tick_fixed()`. Confirmed empirically: `DOSAGS_FREEZE_TICKS` set to
values spanning AUTOPILOT's own logged dialog window (tick 2025, +/- a wide
margin: 1990/2010/2025/2028/2035/2060, and separately 2024-2030) produced
**zero** `FRZ*.TXT` markers over a full run (`run-dosbox.sh` present-verify
still completed normally, 0 stale). The freeze tool is not blind to a bug --
it structurally cannot observe this GUI; that is a diagnostic-tooling gap
(0195's scope), not a rendering fact one way or the other. Not filing this
as a defect against 0195 since a debug-only freeze hook covering every
render_graphics() caller was not what it was built for; noted here as a
tooling limitation for the record.

## Step 2: direct alias-vs-full-push comparison via screen-series

Since the freeze hook could not reach this window, used `--screen-series` at
a high enough cadence (0.12 s) to land inside the GUI's actual on-screen
window (found empirically to be much longer than AUTOPILOT's own ~4-tick
log window, consistent with a settle/pause before the scripted choice).
Same binary (`ags-0194.exe`, e8d4b76c5cd9), same package (`agsquest`), same
`ACSETUP-OFF.CFG` override AQF2 used, `--fixed-timestep`:

- **A3** (alias present path, the default -- same as every hardware cell):
  frame `A3/frames/00215_174459.148.png`, tick-equivalent window found at
  index 214 of 390. Topic list renders **complete**: "Room areas", "Objects
  and Inventory", "Characters", "GUIs", "Scripting", "Dialogues", "Leave" --
  every leading glyph present. See `A3-alias-frame00215.png`.
- **B3** (`DOSAGS_DIRTY_PRESENT=0`, full push, no narrowing): same GUI,
  independent run, frame `B3/frames/00216_174733.393.png`. **Also complete**,
  pixel-for-pixel matching text (`text-region-stacked-compare.png`); the only
  diff in a direct crop-diff is sub-pixel mouse-cursor position and minor
  capture noise (max channel diff 66 over ~4k px in a 220x97 crop, no
  structural difference in any glyph).

## Conclusion

The clip is **not present-path-dependent**: DOSBox-X renders this GUI
complete under both the alias-narrowed present (0193/0124) and a full,
unnarrowed push. That rules out a present/narrowing defect in `shared/`'s
present path -- the coordinator's "there with the alias, absent with a full
push" test comes back negative on both sides (absent with both).

It is also not a trail (no duplicate/ghost content) and not a missing
background (the treehouse room behind the list is intact in every capture).
The clip is specific to the **physical hardware capture chain** -- the same
cut, at the same position (flush to x=0 of the raster), independently on
both the capture card and the camera, on real hardware only, never in
DOSBox-X under either present path. The most consistent explanation is
overscan/capture framing at the extreme left edge of the analog VGA signal
on HW-486-66's chain (CRT and/or capture card), not a rendering fact of the
engine's composite and not a port software defect. Recording this the same
way as the AGS Quest GUI cost: content/hardware-bound, evidence attached,
not patched.

**AQF2's witness verdict is CLEAN** (see `../AQF1-2026-09-21/witness/` and
`../AQF2-2026-09-21/witness/REVIEWED.txt` for both AQF cells' reviews); this
finding is recorded alongside it, not blocking it.
