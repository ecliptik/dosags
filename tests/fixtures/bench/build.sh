#!/usr/bin/env bash
# build.sh -- build the BENCH package(s) from source with AGS's own
# headless tools. No Editor, no Wine. License: MIT.
#
# Usage: build.sh [--depth 8|16|32] [--ags-src DIR] [--tools DIR] [--out DIR]
#   --depth    8 (default) -> BENCH8.ags; 16/32 differ ONLY in Game.agf's
#              <ColorDepth> and in the RGBA export of the same drawings
#   --ags-src  AGS source tree at the pin (for agsdefns.sh); default
#              build/ags-pristine, else vendor/ags
#   --tools    host tools dir from build-host-tools.sh; default
#              build/host-tools
#   --out      default tests/harness/games/bench<depth>/ (gitignored, the
#              layout run-dosbox.sh expects)
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../.." && pwd)"
DEPTH=8; AGS_SRC=""; TOOLS="$REPO/build/host-tools"; OUT=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --depth) DEPTH="$2"; shift 2 ;;
        --ags-src) AGS_SRC="$2"; shift 2 ;;
        --tools) TOOLS="$2"; shift 2 ;;
        --out) OUT="$2"; shift 2 ;;
        *) echo "usage: $0 [--depth 8|16|32] [--ags-src DIR] [--tools DIR] [--out DIR]" >&2; exit 1 ;;
    esac
done
if [[ -z "$AGS_SRC" ]]; then
    if [[ -d "$REPO/build/ags-pristine" ]]; then AGS_SRC="$REPO/build/ags-pristine"; else AGS_SRC="$REPO/vendor/ags"; fi
fi
[[ -n "$OUT" ]] || OUT="$REPO/tests/harness/games/bench$DEPTH"
NAME="BENCH$DEPTH"
WORK="$REPO/build/bench-work/$NAME"
PKG="$WORK/pkg"
APIHDR="$AGS_SRC/Editor/AGS.Editor/Resources/agsdefns.sh"
for f in "$TOOLS/Compiler/agscc" "$TOOLS/Tools/agf2dta" "$TOOLS/Tools/agfexport" \
         "$TOOLS/Tools/spritepak" "$TOOLS/Tools/crmpak" "$TOOLS/Tools/agspak" \
         "$TOOLS/mkroom" "$APIHDR"; do
    [[ -e "$f" ]] || { echo "build.sh: missing $f -- run build-host-tools.sh" >&2; exit 1; }
done
rm -rf "$WORK"; mkdir -p "$PKG" "$OUT"
say() { echo "build.sh: $*"; }
run() { "$@" > "$WORK/last-tool.log" 2>&1 || { cat "$WORK/last-tool.log" >&2; echo "build.sh: FAILED: $*" >&2; exit 1; }; }

say "assets (depth $DEPTH)"
run python3 "$HERE/assets/generate_assets.py" "$WORK/assets" --depth "$DEPTH"
run python3 "$HERE/gen_agf.py" "$WORK/assets/palette.json" "$WORK/Game.agf" --depth "$DEPTH"
# The 8-bit project file is kept in the tree as the as-built reference
# (gen_agf.py is the source; this copy makes a schema drift visible in git).
[[ "$DEPTH" != 8 ]] || cp "$WORK/Game.agf" "$HERE/Game.agf"

say "sprites"
run "$TOOLS/Tools/spritepak" -c "$PKG/acsprset.spr" "$WORK/assets/sprites" -n "$PKG/sprindex.dat" -z none

say "game data"
run "$TOOLS/Tools/agf2dta" "$WORK/Game.agf" "$PKG/game28.dta"
run "$TOOLS/Tools/agfexport" autoash "$WORK/Game.agf" "$WORK/_auto.ash"
run "$TOOLS/Tools/agfexport" game-cfg "$WORK/Game.agf" "$WORK/acsetup.cfg"

say "scripts"
HDRS="$APIHDR:$WORK/_auto.ash"
: > "$PKG/ScriptModules.lst"
for mod in AutoPilot; do
    HDRS="$HDRS:$HERE/$mod.ash"
    run "$TOOLS/Compiler/agscc" -H "$HDRS" -o "$PKG/$mod.o" "$HERE/$mod.asc"
    echo "$mod.o" >> "$PKG/ScriptModules.lst"
done
HDRS="$HDRS:$HERE/GlobalScript.ash"
run "$TOOLS/Compiler/agscc" -H "$HDRS" -o "$PKG/GlobalScript.o" "$HERE/GlobalScript.asc"

say "room 1"
R="$WORK/assets/room1"
run "$TOOLS/Tools/crmpak" -c "$WORK/room1.img.crm" back0 "$R/bg.png" \
    mask-hotspot "$R/mask-hotspot.png" mask-region "$R/mask-region.png" \
    mask-walkarea "$R/mask-walkarea.png" mask-walkbehind "$R/mask-walkbehind.png"
ROOMXML="$HERE/rooms/room1.xml"
if [[ "$DEPTH" != 8 ]]; then
    # The two glitch-regression sprites exist only above 8-bit (a real
    # alpha channel / the magenta mask colour mean nothing in a paletted
    # game). Appended AFTER the spinners so object 0 (key) and 1..12
    # (spinners) keep their indices; both sit on the light wall between
    # the pillar and the sign.
    ROOMXML="$WORK/room1.xml"
    sed 's#</Room>#  <Object Name="GlitchAlpha" ScriptName="oGlitchA" X="182" Y="100" Sprite="40" Visible="1" Clickable="0"/>\n  <Object Name="GlitchMagenta" ScriptName="oGlitchM" X="208" Y="100" Sprite="41" Visible="1" Clickable="0"/>\n</Room>#' \
        "$HERE/rooms/room1.xml" > "$ROOMXML"
fi
run "$TOOLS/mkroom" "$WORK/room1.img.crm" "$ROOMXML" "$PKG/room1.crm"
run "$TOOLS/Tools/crmpak" -e "$PKG/room1.crm" ash "$WORK/room1.ash"
run "$TOOLS/Compiler/agscc" -H "$HDRS:$WORK/room1.ash" -o "$WORK/room1.o" "$HERE/rooms/room1.asc"
run "$TOOLS/Tools/crmpak" -i "$PKG/room1.crm" script "$WORK/room1.o"

say "font + audio"
cp "$HERE/assets/PressStart2P-Regular.ttf" "$PKG/agsfnt0.ttf"
cp "$WORK/assets/audio/tune.mid" "$PKG/au000000.mid"
cp "$WORK/assets/audio/chime.wav" "$PKG/au000001.wav"

say "pack"
rm -f "$OUT"/*.ags
run "$TOOLS/Tools/agspak" -c "$OUT/$NAME.ags" "$PKG"
cp "$WORK/acsetup.cfg" "$OUT/acsetup.cfg"
# The two sound variants every manifest in this repo names (validate:
# arms.<arm>.cfg). [sound] enabled is a stock engine key
# (Engine/main/config.cpp, CfgReadBoolInt), the same lever
# tools/port-game's layout stage uses for the sourced games.
sed 's/^enabled = .*/enabled = 1/' "$WORK/acsetup.cfg" > "$OUT/ACSETUP-ON.CFG"
sed 's/^enabled = .*/enabled = 0/' "$WORK/acsetup.cfg" > "$OUT/ACSETUP-OFF.CFG"
"$TOOLS/Tools/agspak" -l "$OUT/$NAME.ags" > "$WORK/pack-list.txt" 2>&1 || true
say "$OUT/$NAME.ags ($(stat -c %s "$OUT/$NAME.ags") bytes)"
