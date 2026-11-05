# tests/harness -- the AGS Quest test harness

A standing, automated test harness that drives a real AGS game package
end-to-end, entirely from AGS script running inside the compiled
package, so fps/load-time/room-transition/memory/audio measurements are
taken the same way every time on DOSBox-X (correctness gate) and on real
hardware (the only source of benchmark numbers). See `PLAN.md`'s "Test
harness (AGS Quest)" section for the full design (decisions, engine
facts, architecture, phase table, work order) -- this README is the
practical "how do I run it" companion, not a second copy of that spec.

## What's committed vs. not

Only our own code and assets are tracked:

- `setup-wine.sh`, `build-package.sh`, `run-dosbox.sh`, `run-hw.sh`,
  `parse-results.py`
- `packages/<pkg>/PIN` (upstream pins), `overlay/` (our patches/scripts/
  assets only), `LICENSE-NOTES.md`
- `results/` (numbers + hashes) and `expected/` (screenshot hashes)

**Never committed:** anything under `games/` (gitignored) -- the
compiled `.ags` game data itself, rebuilt on demand from a pinned
upstream SHA. AGS Quest's own art is CC BY-NC-ND (see
`packages/agsquest/LICENSE-NOTES.md`); no screenshot of it is committed
either, only hashes.

## Running it

```bash
# One-time (or whenever /tmp/wine-ags-test is gone/stale): ~30-40 min,
# mostly winetricks installing .NET 4.6 under Xvfb.
./setup-wine.sh

# Rebuild the package from the pinned upstream SHA + our overlay.
./build-package.sh agsquest
# -> tests/harness/games/agsquest/AGSQuest.ags

# (Slice 2+) Run the autopilot under DOSBox-X and parse the results.
./run-dosbox.sh agsquest
./parse-results.py <staged-run-dir>

# (Slice 5) A screenshot with no committed baseline yet is reported as
# "new", not a failure -- look at the actual image (converted from the
# staged PH0N.BMP, e.g. with ImageMagick's `convert`) BEFORE trusting
# it, then commit the baseline:
./parse-results.py <staged-run-dir> --update-baseline

# (Slice 6) Real hardware, via vcctrl (../../../vcctrl checked out as a
# sibling repo, or VCCTRL_BIN=/path/to/vcctrl/bin/vcctrl). Powers on if
# needed, stages+sends the package, runs it, and collects results:
./run-hw.sh agsquest --tag HW1 --power-on
./parse-results.py <collected-dir> --tag HW-486-66-<date>-agsquest
```

`setup-wine.sh` reuses an existing working `$WINEPREFIX` (default
`/tmp/wine-ags-test`) if the AGS Editor and dotnet46 are already there --
safe to re-run. `build-package.sh` always re-clones+recompiles fresh
(cheap next to the one-time Wine setup) so the output can never silently
drift from the pinned SHA + current overlay.

## Status

- [x] Slice 1: skeleton + reproducible package build (`setup-wine.sh`,
      `build-package.sh`, `packages/agsquest/PIN` + `overlay/Game.agf.patch`).
- [x] Slice 2: autopilot v0 + DOSBox-X runner + parser v0
      (`overlay/AutoPilot.ash`/`.asc`, `run-dosbox.sh`, `parse-results.py`).
      Gate met: a green DOSBox-X run, `RUNMANI.LOG` present, all 16
      phases (`boot`..`quit`) report `ok` (`quit` itself logs `begin`
      only, by design -- the engine exits before a `quit ok` line could
      ever be written; a clean `exit_code=0` in `RUNMANI.LOG` is quit's
      own success signal).
- [x] Slice 3: engine instrumentation patches (`patches/ags/0041`-`0044`:
      fps p50/p95, room-transition ms timestamps, DPMI free-memory
      minimum, run-identity env vars). Each `/sdldos:review`ed and
      confirmed by a real DOSBox-X run before landing; see
      `PATCH-SEQUENCE.md`'s "Phase I" section for the full mechanism
      and confirming numbers for each.
- [x] Slice 4: overlay assets -- our own CC0 WAV chime + generated MIDI
      tune (`overlay/assets/generate_assets.py`, no external audio
      tools/samples) + a verified OFL TrueType font ("Press Start 2P",
      pinned at a real `google/fonts` commit, license read directly),
      wired into the `audio`/`intro` phases; `LICENSE-NOTES.md` records
      all three. Gate met: package still compiles and parses; the TTF
      font visibly renders in a real room-3 screenshot (the intro
      cutscene's own dialogue line, in the new font's distinct pixel
      glyphs -- not committed, per this package's own NC-ND art rule).
- [x] Slice 5: screenshots + hash regression + first committed
      `results/` record. Three inline `SaveScreenShot()` calls in
      `AutoPilot.asc` (`PH01.BMP` settle/room3, `PH02.BMP` interior/
      room4, `PH03.BMP` gem-balcony/room3 -- SaveScreenShot can only
      capture the *current* frame, so each fires at its own phase
      transition, not from the `shots` phase itself, which is now a
      completion check). `parse-results.py` hashes them and compares
      against `expected/<pkg>/<environment>.json`; a screenshot with no
      baseline yet is reported `new` (not a failure) until
      `--update-baseline` is run -- only after actually looking at the
      image. Confirmed deterministic (byte-identical hashes) across
      three independent DOSBox-X runs before the baseline was
      committed. **Caution learned 2026-09-16:** "looking at the image"
      must include asking whether every sprite's transparency is right
      -- the first committed baselines enshrined solid black boxes
      around every alpha-authored sprite (the package's own data
      defect: the Editor drops PNG alpha for a HighColor game, see
      `PLAN.md` "Black-box sprite glitch -- root cause") and passed
      inspection because the boxes were mistaken for content. The
      official Linux engine renders the same package identically, so a
      baseline diff against `ags64 --gfxdriver software` on the same
      package is the cheap way to tell engine behaviour from data. First `results/dosbox-x-2026-09-11-agsquest.{md,json}`
      record committed, marked correctness-only.
- [x] Slice 6: hub rig-script generalization + first real-hardware run.
      vcctrl's `harness/vcctrl-sweep|-cell|-collect` and the path-touching
      `bin/vcctrl-*` tools are now profile-driven instead of hardcoded to
      doskutsu (done in the vcctrl repo; see the hub's
      `docs/hardware-testing.md`). The actual first HW-486-66 run used
      vcctrl's generic file-transfer primitives (stage-file/send-file/
      get-file) with a purpose-built `RUN.BAT`, not vcctrl-cell directly
      -- AGS.EXE takes real CLI args and needs shell stdout redirection,
      a different shape than vcctrl-cell's env-var+CFG-file model built
      for doskutsu. `run-hw.sh` now automates that sequence (written
      from, and matching, the manual run -- not yet exercised end-to-end
      itself, treat its first real invocation with normal care). Gate
      met: all 16 phases `ok`, `exit_code=0`, real `fps_p50=9.62`/
      `fps_p95=10.09` (first-ever real-hardware datum for this port),
      all three screenshots byte-identical to the DOSBox-X baseline.
      First `results/HW-486-66-2026-09-11-agsquest.{md,json}` record
      committed -- see that file for the full writeup, including a real
      harness gap found and fixed (RUN.BAT needs a console-mode-restore
      step after AGS.EXE exits, or a successfully-finished run reads as
      a hang for minutes afterward).
- [x] Slice 7 (optional, non-gating): `dialog` phase + input-latency
      approximation. `dRedMage.Start()` turned out unusable for this
      (deferred when called from script, and its own intro text drains
      any pre-queued click before the options screen exists -- see
      PLAN.md's eleventh-session "Current state" and the Measured
      Constants table's 2026-09-11 rows for the full chain of real
      engine findings this took). Final design: `Dialog.DisplayOptions()`
      (genuinely synchronous) with a `Mouse.SetPosition()`+one-tick-wait+
      `Mouse.Click()` on "Leave"'s own row, coordinates read off a live
      DOSBox-X capture. `patches/ags/0045` (`/sdldos:review`ed) adds
      paired `inject`/`processed` uclock() timestamps around the
      simulated click, real deltas 11-24ms across several runs. `dialog`
      is a new OPTIONAL phase in `parse-results.py` (`OPTIONAL_PHASES`)
      -- shown in the rendered record, never gates pass/fail. Gate met:
      several real, reproducible DOSBox-X runs, `dialog` reports `ok`
      with `chosen=14` every time, all 16 pre-existing phases plus the
      three screenshot hashes unaffected. Real-hardware confirmation
      (optional, not required to close this slice) done too, same
      session: HW-486-66 tag `HW8`, same `chosen=14`, first real-hardware
      input-latency datum for this port (223ms, vs. DOSBox-X's own
      11-24ms). Getting a clean run surfaced and fixed three real bugs in
      this repo's own `run-hw.sh` (missing `--replace`, two fragile
      polling loops, a cleanup-trap that deleted its own results before
      they could be read) alongside unrelated pre-existing bugs on the
      shared vcctrl rig, none of them a dosags/AGS defect. See
      `results/HW-486-66-2026-09-11-agsquest-slice7.md` and PLAN.md's
      eleventh-session "Current state" for the full writeup.
- [x] Slice 8: `guimenu` and `anim` phases, closing the two real gaps found
      in the "Milestone mapping"'s own `PLAYABLE` gate (GUI coverage was
      previously just one title-screen button click; animation was never
      exercised or checked anywhere). `guimenu` clicks `btnOpenMenu` (the
      real in-game-menu opener `GlobalScript.asc` itself uses -- toggles
      `gInGameMenu`, the same GUI hosting the Save/Load buttons) and polls
      for `gInGameMenu.Visible`; `Button.Click()` turned out deferred via
      the same `QueueScriptFunction()` path already found for
      `RunInteraction()`/`Dialog.Start()`, confirmed by reading
      `Engine/ac/gui.cpp`'s `process_interface_click()` directly rather
      than assumed. `anim` samples room 4's own always-running chandelier
      object (`oChandelier`, animated by `room4.asc`'s own `room_Load()`,
      not by this module) via `Object.Frame` twice across a poll window,
      confirming a real frame-value change rather than trusting
      `Object.Animating` alone. Gate met, first try, no vendor patch
      needed: two independent DOSBox-X runs both PASS clean, all 16
      pre-existing phases plus optional `dialog` unaffected, all three
      screenshot hashes still match baseline, `anim_detail` logs a real
      `frame0=0 frame1=1 animating=1` both times. **Also confirmed on
      real hardware (HW-486-66, tag HW10)** after a rig-side keystroke-
      corruption bug (two failed HW9 attempts) was root-caused and fixed
      by the vcctrl peer session, not a dosags/AGS defect -- clean PASS
      first try, `anim`/`guimenu` tick-counted durations byte-for-byte
      identical to the DOSBox-X run. See `results/
      HW-486-66-2026-09-11-agsquest-slice8.md` and PLAN.md's
      twelfth-session "Current state" for the full writeup.
