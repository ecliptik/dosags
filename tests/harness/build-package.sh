#!/usr/bin/env bash
# build-package.sh -- rebuild a test package from its pinned upstream
# source plus this repo's own overlay, via the Wine AGS Editor set up by
# setup-wine.sh. See tests/harness/README.md.
#
# The 16-bit .ags data pak this produces is NEVER committed (AGS Quest's
# art is CC BY-NC-ND -- see packages/<pkg>/LICENSE-NOTES.md); only our
# own overlay/ content and this script are tracked. Output lands in the
# gitignored games/<pkg>/ directory.
#
# Usage:
#   ./setup-wine.sh                # once, or whenever the prefix is stale
#   ./build-package.sh agsquest

set -euo pipefail

usage() { echo "Usage: $0 <package-name>   (e.g. agsquest)" >&2; exit 1; }
[[ $# -eq 1 ]] || usage
PKG="$1"

HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PKG_DIR="$HARNESS_DIR/packages/$PKG"
PIN_FILE="$PKG_DIR/PIN"
[[ -f "$PIN_FILE" ]] || { echo "build-package.sh: no PIN file at $PIN_FILE" >&2; exit 1; }
# shellcheck disable=SC1090
. "$PIN_FILE"

WINEPREFIX="${WINEPREFIX:-/tmp/wine-ags-test}"
export WINEPREFIX
EDITOR_EXE="$WINEPREFIX/dl/AGS-RC2/AGSEditor.exe"
[[ -f "$EDITOR_EXE" ]] || { echo "build-package.sh: $EDITOR_EXE not found -- run setup-wine.sh first" >&2; exit 1; }

command -v wine >/dev/null || { echo "build-package.sh: wine not found in PATH" >&2; exit 1; }
command -v xvfb-run >/dev/null || { echo "build-package.sh: xvfb-run not found" >&2; exit 1; }
command -v patch >/dev/null || { echo "build-package.sh: patch not found" >&2; exit 1; }
command -v python3 >/dev/null || { echo "build-package.sh: python3 not found (needed by flatten-alpha.py)" >&2; exit 1; }

SRC_DIR="$WINEPREFIX/dl/$PKG-src"
GAMES_DIR="$HARNESS_DIR/games/$PKG"

echo "build-package.sh: cloning $GAME_REPO_URL @ $GAME_SHA"
rm -rf "$SRC_DIR"
git clone -q "$GAME_REPO_URL" "$SRC_DIR"
git -C "$SRC_DIR" checkout -q "$GAME_SHA"
ACTUAL_SHA="$(git -C "$SRC_DIR" rev-parse HEAD)"
if [[ "$ACTUAL_SHA" != "$GAME_SHA" ]]; then
    echo "build-package.sh: pin mismatch -- expected $GAME_SHA, got $ACTUAL_SHA" >&2
    exit 1
fi

GAME_DIR="$SRC_DIR/AGSQuest"
GAME_AGF="$GAME_DIR/Game.agf"
[[ -f "$GAME_AGF" ]] || { echo "build-package.sh: $GAME_AGF not found -- upstream layout changed?" >&2; exit 1; }

if [[ -f "$PKG_DIR/overlay/Game.agf.patch" ]]; then
    echo "build-package.sh: applying overlay/Game.agf.patch"
    patch -p1 -d "$SRC_DIR" < "$PKG_DIR/overlay/Game.agf.patch"
fi

# Copy our own script modules (.ash/.asc) into place. Game.agf.patch
# only wires the module's <ScriptAndHeader> entry into the project --
# the actual files it references have to exist on disk too.
shopt -s nullglob
for f in "$PKG_DIR"/overlay/*.ash "$PKG_DIR"/overlay/*.asc; do
    cp "$f" "$GAME_DIR/"
done
shopt -u nullglob

# Overlay assets (slice 4): our own font/audio, in the exact locations
# and naming conventions AGS's own compiler expects -- confirmed by
# reading Editor/AGS.Types/Font.cs and Editor/AGS.Editor/Components/
# AudioComponent.cs directly, not guessed.
ASSETS_DIR="$PKG_DIR/overlay/assets"
if [[ -d "$ASSETS_DIR" ]]; then
    # Fonts: the compiler globs agsfnt*.ttf/*.wfn in the PROJECT ROOT
    # by filename convention alone (Game.agf's own <SourceFilename> is
    # editor-display-only, never read by the compiler) -- font ID 3
    # (this overlay's Font entry in Game.agf.patch) needs agsfnt3.ttf
    # to exist there under exactly that name.
    if [[ -f "$ASSETS_DIR/PressStart2P-Regular.ttf" ]]; then
        cp "$ASSETS_DIR/PressStart2P-Regular.ttf" "$GAME_DIR/agsfnt3.ttf"
    fi

    # Audio: the compiler reads each clip's actual bytes from
    # AudioCache/au<Index:X6><ext-from-SourceFileName>, derived from
    # the clip's Index (a stable ID, not folder position) -- NOT from
    # SourceFileName's path directly. Index 17 (WAV, aAutopilotChime)
    # and 18 (MIDI, mAutopilotTune) are this overlay's own AudioClip
    # entries in Game.agf.patch.
    mkdir -p "$GAME_DIR/AudioCache"
    if [[ -f "$ASSETS_DIR/autopilot_chime.wav" ]]; then
        cp "$ASSETS_DIR/autopilot_chime.wav" "$GAME_DIR/AudioCache/au000011.wav"
    fi
    if [[ -f "$ASSETS_DIR/autopilot_tune.mid" ]]; then
        cp "$ASSETS_DIR/autopilot_tune.mid" "$GAME_DIR/AudioCache/au000012.mid"
    fi

    # Also place copies at the SourceFileName paths Game.agf.patch
    # declares, purely for consistency with upstream's own convention
    # (a real Assets/ tree an operator could inspect) -- not read by
    # the compiler, which only looks at AudioCache/ and agsfnt3.ttf.
    mkdir -p "$GAME_DIR/Assets/Fonts" "$GAME_DIR/Assets/Sound" "$GAME_DIR/Assets/Music"
    [[ -f "$ASSETS_DIR/PressStart2P-Regular.ttf" ]] && cp "$ASSETS_DIR/PressStart2P-Regular.ttf" "$GAME_DIR/Assets/Fonts/"
    [[ -f "$ASSETS_DIR/autopilot_chime.wav" ]] && cp "$ASSETS_DIR/autopilot_chime.wav" "$GAME_DIR/Assets/Sound/"
    [[ -f "$ASSETS_DIR/autopilot_tune.mid" ]] && cp "$ASSETS_DIR/autopilot_tune.mid" "$GAME_DIR/Assets/Music/"
fi

# Bake sprite-source PNG alpha into AGS's mask colour BEFORE compiling.
# Root cause of the 2026-09-15 "black boxes around sprites" glitch (see
# flatten-alpha.py's own header and PLAN.md's "Known graphical glitch"
# section): upstream gitignores acsprset.spr, so /compile recreates every
# sprite from its <Sprite><Source> PNG; with Game.agf.patch's HighColor
# retarget the editor discards PNG alpha (Editor/AGS.Editor/Utils/
# SpriteTools.cs AdjustImportParams only imports alpha for TrueColor games)
# and ImportMethod=LeaveAsIs keys nothing, so the RGB-black under alpha 0
# became OPAQUE black in the package. Both this port and the official
# Linux engine rendered that data byte-identically -- not a DOS bug.
# NOTE: this changes the package's sprite pixels, so the committed
# screenshot baselines in expected/<pkg>/ change with it -- re-baseline
# only after looking at the images (README, slice 5).
echo "build-package.sh: flattening sprite-source alpha to the AGS mask colour"
python3 "$HARNESS_DIR/flatten-alpha.py" "$GAME_AGF"

echo "build-package.sh: compiling via Wine AGS Editor (can take a minute)"
rm -rf "$GAME_DIR/Compiled"
# Wine's Z: drive maps the host filesystem root -- an absolute Windows
# path via Z: is required. A relative Game.agf argument (or the GUI's
# own relative file-open) reliably fails with "Unable to load the game
# '...' because it does not exist" -- see PLAN.md's eighth-session
# tooling finding. Do not "simplify" this back to a relative path.
WIN_GAME_AGF="Z:$(readlink -f "$GAME_AGF")"
WIN_GAME_AGF="${WIN_GAME_AGF//\//\\}"
xvfb-run -a wine "$EDITOR_EXE" /compile "$WIN_GAME_AGF"

COMPILED_AGS=("$GAME_DIR"/Compiled/Data/*.ags)
[[ -f "${COMPILED_AGS[0]}" ]] || { echo "build-package.sh: no .ags output under $GAME_DIR/Compiled/Data" >&2; exit 1; }
[[ ${#COMPILED_AGS[@]} -eq 1 ]] || { echo "build-package.sh: expected exactly one .ags output, found ${#COMPILED_AGS[@]}" >&2; exit 1; }

mkdir -p "$GAMES_DIR"
cp "${COMPILED_AGS[0]}" "$GAMES_DIR/"
echo "build-package.sh: wrote $GAMES_DIR/$(basename "${COMPILED_AGS[0]}")"
