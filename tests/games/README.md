# tests/games -- golden-reference game manifests

One subdirectory per game from PLAN.md's "Golden-reference games" survey,
produced by `tools/port-game/`. Each holds:

- `PIN` -- verified source URL, hash, license/freeware status. Never the
  game archive/binary itself.
- `manifest.yaml` -- what `inspect` found (DataVersion, audio format
  inventory, resolution/depth), what `convert`/`repack` did, the driving
  recipe, and validation results per environment.
- `inspect-report.json`, `convert-report.json` -- the tool's own raw
  output, committed alongside the manifest's hand-written summary.

Game data itself (the `.exe`/`.ags`, extracted assets, repacked
packages) is never committed anywhere in this repo -- rebuilt on demand
from each game's own `PIN`, same rule as `tests/harness/packages/
agsquest/`.
