# Derived scorer references (never in git; regenerate from this file)

The capture scorers read reference audio derived from game data. Game data and
anything rendered from it stay out of git, so these files live under the
gitignored `build/lab/renders/`. A cleanup that removes `build/` removes them;
this file is how to get them back. Every recipe below was re-run on 2026-11-04
after the lab-wb worktree (and its build/) was retired, and each output matched
the sha256 the 09-29/30 cell READMEs recorded, byte for byte.

Scripts: `LAB-WB-data/` on branch lab/wb (tag archive/lab-wb-2026-11-04), which
also needs that branch's `tests/harness/` beside it (render-onsets.py imports
`../tests/harness/audio-compare.py`). Extract both with
`git archive archive/lab-wb-2026-11-04 LAB-WB-data tests/harness | tar -x -C DIR`.
Game packages: `tests/harness/games/` (gitignored). Asset extraction:
`tools/port-game/clib.py` (`read_header(data).assets`, bytes at
`data[offset:offset+size]`).

Tools as of 2026-11-04: fluidsynth 2.4.4+dfsg-1+deb13u3, fluid-soundfont-gm
3.1-5.3 (/usr/share/sounds/sf2/FluidR3_GM.sf2, sha256 74594e8f4250680a...),
Python 3.13.5.

| File | Used by | How it is made | sha256 |
|---|---|---|---|
| trilby_sound11.wav | capture-check.py (S8, CAPS8; K3 effect clip) | asset `sound11.wav` of trilbysnotes/NOTES.ags, raw bytes | 3951702ff7afefbd870bb424e600ed4e46628af507fdaa53b10953940af5749b |
| 5days_sound3.wav | capture-check3.py (S16 / S32P, CAPS16 / CAPS32R; K3) | asset `sound3.wav` of 5days/5DAYS.ags, raw bytes | 5ecb6a02ae31df97afdb3744e294020d5ea80329562c498fe3466041358636b8 |
| 5days_music0.mid | depth-score.py (WB arm, WBC*); input to D0REF | asset `music0.mid` of 5days/5DAYS.ags, raw bytes | 3e2ac1b96f172f03789a724c7a911eca06c5d6d52425e140069ed66179613713 |
| D0REF.mid | input to D0REF.wav | `song-loop-ref.py music0.mid D0REF.mid 240` (music0.mid = 5days_music0.mid; 3 loops of 113.999 s) | 2ca0e94395d0cf9785dc3ec6051aac16a44ca58ab9b188b26a535a652f2e32e5 |
| D0REF.wav | capture-check3.py (K2, M1, M2, D; loop 113.999), depth-score.py | `render-onsets.py 100 D0REF.mid` (fluidsynth -ni -g 0.6 -r 22050, FluidR3_GM) | 874b8e8d39138c3eb0d08c9e4f09fcb449b469224b3213fe979c7f522a8cf031 |

A regenerated render that does not match its sha256 (a different fluidsynth or
soundfont) may be used only where both arms of a comparison share it, and a
cell scored against it says so; it never re-scores a cell recorded against the
hashes above.
