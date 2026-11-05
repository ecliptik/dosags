#!/usr/bin/env python3
"""Analyze the S4 real-hardware MIDI gate-3 audio poll log.

Reuses audio_bands.py's own active_bands()/verdict() math (the identical
functions S2's PCM chime gate used) against the raw band_db readings
collected by audio_poll.py -- no re-derivation of the scoring logic.

Prints every poll with its active-band pattern, then flags the two
windows of interest:
  - the chime (bands 2/3 active -- 400/800 Hz, the two-tone PCM chime,
    already characterized by S2 on this same rig)
  - the tune (band 0 active alone at the edges -- C3 -- with band 1
    active in the middle -- D3/E3/F3/G3 -- against silence elsewhere)
"""
import json
import sys

sys.path.insert(0, "/home/claude/git/vcctrl/common")
import audio_bands as ab

path = sys.argv[1] if len(sys.argv) > 1 else "s4_audio_poll.jsonl"

rows = []
with open(path) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))

print(f"{'t':>7}  {'mean_db':>8}  {'active':>6}  bands_active_idx  band_db")
for r in rows:
    if "error" in r:
        print(f"{r['t']:>7}  ERROR: {r['error']}")
        continue
    lvl = r["level"]
    spec = r["spectrum"]
    band_db = spec["band_db"]
    active_idx = [i for i, d in enumerate(band_db)
                  if d >= max(band_db) - ab.BAND_ACTIVE_MARGIN_DB and d >= ab.BAND_FLOOR_DB]
    print(f"{r['t']:>7.1f}  {lvl['mean_db']:>8.2f}  {spec['active_bands']:>6}  {active_idx!s:<16}  {band_db}")
