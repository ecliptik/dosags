# minimal-game-package

`build_fixture.py` generates a minimal, throwaway synthetic AGS game
package (a `.ags` CLIB v6 container) just large enough to satisfy every
hard requirement between `engine_init_gamedata()` and the graphics-mode
switch, for the `TITLE_SCREEN` milestone. This is **not** the real
hand-authored first test game PLAN.md describes -- it has no rooms,
sprites, or real script content, and is not meant to be kept once a real
test game exists.

## Usage

```
python3 build_fixture.py game.ags 8    # 8-bit (INDEX8)
python3 build_fixture.py game.ags 16   # 16-bit (RGB565)
```

Stage the output as `*.ags` alongside `ags.exe` (AGS's own DOS auto-search
finds it in the current directory, no config or command-line argument
needed) and run with `--user-data-dir c:\` (or another writable path) --
this staged DOSBox-X environment has no writable default save directory,
and `check_write_access()` fails gracefully without it.

## Byte layout

Every field is derived by reading the pinned AGS source
(`~/git/dosags/vendor/ags/`) directly, cited by file:line in
`build_fixture.py`'s own comments -- not guessed. See that file for the
full field-by-field derivation (CLIB header, `game28.dta` main-game-file
header, `GameSetupStructBase`, font/interaction/character/GUI records,
minimal `ccScript` global script).

## A real bug found the hard way

An earlier, byte-complete version of this fixture crashed silently deep
inside `ReadGameData()`, with zero diagnostic output. An extensive
isolated-probe investigation (ruling out DJGPP/toolchain/optimization-
level/stale-object explanations one at a time) eventually found the real
cause: `GameSetupStruct::read_interaction_scripts()`'s legacy (2.x)
branch (`Common/ac/gamesetupstruct.cpp:130-178`) has an *unconditional*
trailing `numIntrVars = in->ReadInt32()` (line 173) followed by a loop
reading that many more records -- present regardless of
`numcharacters`/`numinvitems`, and easy to miss if you stop reading the
function at its two per-character/per-invitem loops. This fixture had
never supplied that field; the missing 4 bytes made the read consume the
*next* asset's own signature bytes as a garbage count (~1.3 billion),
driving the trailing loop catastrophically out of bounds. See
`build_interaction_scripts_legacy()`'s own docstring and PLAN.md's
Measured constants (2026-09-10, fifth session) for the full account.
The lesson: read a function to its actual last line before concluding
"minimal" bytes are supplied -- not to where the loops look done.
