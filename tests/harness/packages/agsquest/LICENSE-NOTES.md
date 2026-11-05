# agsquest package -- licensing notes

Upstream: [`adventuregamestudio/ags-demo-game`](https://github.com/adventuregamestudio/ags-demo-game)
("AGS Quest"), pinned per `PIN`. Read directly from that repo at the
pinned SHA, not from memory or a summary:

- Scripts (`.asc`/`.ash`, `Game.agf`, room logic): **0BSD**
  (`LICENSE_0BSD.md`) -- public-domain-equivalent, no restriction.
- Art, audio, and other game assets: **CC BY-NC-ND 4.0**
  (`LICENSE_CC4-BY-NC-ND.md`) -- non-commercial, **no derivatives**. This
  is why nothing from this package is committed anywhere in this repo or
  the hub: the color-depth retarget in `overlay/Game.agf.patch` and the
  room recompilation `build-package.sh` triggers are themselves
  derivative works of the NC-ND art.

**What this means for the harness, concretely:**

- `games/` (the compiled `.ags` output) is gitignored -- never committed.
- No screenshot of this package's rendered content is ever committed;
  `expected/` stores screenshot **hashes** for regression, never images.
- `overlay/Game.agf.patch` is a plain-text unified diff against upstream
  `Game.agf` -- itself not a redistribution of the asset content, only
  the two changed XML lines -- but the *result* of applying it (a
  recompiled NC-ND game package) still never leaves `games/`.
- Anything committed under `overlay/` beyond the `Game.agf.patch` (the
  autopilot script, our own WAV/MIDI/TTF assets from slice 4) is our own
  original or separately-licensed content, recorded in this file as it's
  added -- never upstream AGS Quest content.

This package is used for **local engine testing only** -- see
`CLAUDE.md`'s licensing rules and `PLAN.md`'s "Test harness (AGS Quest)"
decision 2. It is not, and will never become, this port's committed
`tests/fixtures/` spec-compliant test game.

## Our own overlay assets (slice 4, `overlay/assets/`)

- **`autopilot_chime.wav`, `autopilot_tune.mid`** -- both wholly
  original, generated from scratch by `overlay/assets/
  generate_assets.py` (no external audio tools, no third-party samples,
  no MIDI library -- the WAV is a synthesized two-tone sine chime, the
  MIDI an 8-note hand-written phrase, both built byte-for-byte in that
  script). **CC0 (no rights reserved)** -- original work, freely
  committable and redistributable. Re-run the script to regenerate
  either file in place; both are also committed as binary output so the
  harness doesn't need Python at package-build time.
- **`PressStart2P-Regular.ttf`** -- "Press Start 2P" by The Press Start
  2P Project Authors (Cody Boisclair, cody@zone38.net), copyright 2012.
  **SIL Open Font License 1.1** (`PressStart2P-OFL.txt` in this same
  directory, the license file as pinned below -- read directly, not
  assumed from the font's name or its "ofl/" collection path). Reserved
  Font Name: "Press Start 2P" (per OFL's own definition, this means a
  modified version of the font may not keep using that name -- not
  relevant here since it's used unmodified).
  - Source: `https://github.com/google/fonts`, path
    `ofl/pressstart2p/PressStart2P-Regular.ttf`, pinned commit
    `e06fe11c39051bddaef73ec338a9d1c8175723f1` (the latest commit
    touching that path as of 2026-09-11, confirmed via `gh api
    repos/google/fonts/commits`, not `main` -- a moving ref).
  - `PressStart2P-Regular.ttf` sha256:
    `034c77f1f05ec89421e4a63f0e3a4ca1ecf852cc6d2bf611f126f275728e017d`
  - `PressStart2P-OFL.txt` sha256:
    `705960c3281a5765ecc0b59bd4ed7ca59eed165748076bc2fc3e8fdbfeb944b0`
