#!/usr/bin/env bash
# setup-wine.sh -- one-time (idempotent) setup of the Wine prefix used to
# compile AGS test packages non-interactively via the real AGS Editor's
# `/compile` CLI flag. See tests/harness/README.md and PLAN.md's "Test
# harness (AGS Quest)" section for why this exists and what it replaces
# (there is no Linux-native AGS compiler -- see PLAN.md's "First test
# game selection criteria").
#
# Idempotent: if $WINEPREFIX already has a working AGSEditor.exe and
# dotnet46 installed, this is a no-op. Safe to re-run any time; does NOT
# reuse a partial/broken prefix (deletes and rebuilds Wine's dotnet46
# state that winetricks itself manages -- it does not delete the whole
# prefix, since other prefix state such as agsquest-refrun/ is harmless
# to keep).
#
# Fresh-machine cost: ~30-40 minutes, almost all of it winetricks
# installing .NET Framework 4.6 (a real Windows Forms/.NET dependency of
# the AGS Editor, not a shortcut we can skip).
#
# Usage:
#   ./setup-wine.sh
#   WINEPREFIX=/some/other/path ./setup-wine.sh

set -euo pipefail

HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIN_FILE="$HARNESS_DIR/packages/agsquest/PIN"
[[ -f "$PIN_FILE" ]] || { echo "setup-wine.sh: missing $PIN_FILE" >&2; exit 1; }
# shellcheck disable=SC1090
. "$PIN_FILE"

WINEPREFIX="${WINEPREFIX:-/tmp/wine-ags-test}"
export WINEPREFIX
EDITOR_DIR="$WINEPREFIX/dl/AGS-RC2"
EDITOR_EXE="$EDITOR_DIR/AGSEditor.exe"
ZIP_PATH="$WINEPREFIX/dl/AGS-RC2.zip"
WINETRICKS="$WINEPREFIX/winetricks"

mkdir -p "$WINEPREFIX/dl"

if [[ -f "$EDITOR_EXE" ]] && [[ -d "$WINEPREFIX/drive_c/windows/Microsoft.NET/Framework" ]]; then
    echo "setup-wine.sh: existing prefix at $WINEPREFIX already has AGSEditor.exe + dotnet46 -- reusing, nothing to do."
    exit 0
fi

echo "setup-wine.sh: no working prefix at $WINEPREFIX -- building from scratch (~30-40 min)."

command -v wine >/dev/null || { echo "setup-wine.sh: wine not found in PATH" >&2; exit 1; }
command -v cabextract >/dev/null || { echo "setup-wine.sh: cabextract not found (winetricks dotnet46 needs it)" >&2; exit 1; }
command -v xvfb-run >/dev/null || { echo "setup-wine.sh: xvfb-run not found" >&2; exit 1; }
command -v unzip >/dev/null || { echo "setup-wine.sh: unzip not found" >&2; exit 1; }

wineboot --init >/dev/null 2>&1 || true

if [[ ! -x "$WINETRICKS" ]]; then
    echo "setup-wine.sh: fetching winetricks"
    curl -fsSL -o "$WINETRICKS" https://raw.githubusercontent.com/Winetricks/winetricks/master/src/winetricks
    chmod +x "$WINETRICKS"
fi

echo "setup-wine.sh: installing dotnet46 under Xvfb (long step)"
xvfb-run -a "$WINETRICKS" -q dotnet46

if [[ ! -f "$ZIP_PATH" ]] || ! echo "$EDITOR_SHA256  $ZIP_PATH" | sha256sum -c - >/dev/null 2>&1; then
    echo "setup-wine.sh: fetching AGS Editor $EDITOR_VERSION"
    curl -fsSL -o "$ZIP_PATH" "$EDITOR_RELEASE_URL"
fi
echo "$EDITOR_SHA256  $ZIP_PATH" | sha256sum -c -

rm -rf "$EDITOR_DIR"
mkdir -p "$EDITOR_DIR"
unzip -q "$ZIP_PATH" -d "$EDITOR_DIR"

[[ -f "$EDITOR_EXE" ]] || { echo "setup-wine.sh: AGSEditor.exe not found after unzip" >&2; exit 1; }

echo "setup-wine.sh: prefix ready at $WINEPREFIX"
