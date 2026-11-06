#!/usr/bin/env bash
# make-dist.sh -- package the RELEASE flavour (build/ags-release/ags.exe) as a
# DOS zip for players. Called by `make dist`, which builds the exe first.
#
#   scripts/make-dist.sh [--version V] [--repo-url URL] [--out DIR]
#
# Writes <out>/dosags-<V>/ (the staged tree, 8.3 names, CRLF text) and
# <out>/dosags-<V>.zip, then runs scripts/check-dist.sh on the zip.
#
# The file list is THIRD-PARTY.md's dist-files table; check-dist.sh fails if
# the zip and that table disagree in either direction. No game data, ever.
#
# AGS.EXE is the release exe byte for byte: no stubedit here. The build sets
# its stub minstack explicitly (Makefile AGS_MINSTACK, 512 KB = the value
# every gate measured); MANIFEST.TXT records it read from the stub, and this
# script refuses any other value.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
VERSION=dev; REPO_URL=""; OUT="$ROOT/build/dist"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --version)  VERSION="$2"; shift 2 ;;
        --repo-url) REPO_URL="$2"; shift 2 ;;
        --out)      OUT="$2"; shift 2 ;;
        *) echo "usage: $0 [--version V] [--repo-url URL] [--out DIR]" >&2; exit 2 ;;
    esac
done
die() { echo "make-dist: $*" >&2; exit 1; }
[[ "$VERSION" =~ ^[A-Za-z0-9._-]+$ ]] || die "bad --version '$VERSION'"
# The zip step runs inside the staged tree, so a relative --out must be made absolute first.
mkdir -p "$OUT"; OUT="$(cd "$OUT" && pwd)"

EXE=build/ags-release/ags.exe
CWS_EXE=vendor/cwsdpmi/cwsdpmi.exe
CWS_DOC=vendor/cwsdpmi/cwsdpmi.doc
AGS_LIC=vendor/ags/License.txt
AGS_COPY=vendor/ags/Copyright.txt
FTL=vendor/ags/Common/libsrc/freetype-2.1.3/docs/FTL.txt
OPL3BANK=.sdl-dos-ports/shared/audio/opl3bank.dat
OPL3BANK_SHA=8c7a17a017a213f5f4c63a631fa2eb06b33640b1c49e5e3faf0eb203d25a354b
DMXOPL_LIC=docs/dist/licenses/DMXOPL-LICENSE.txt
for f in "$EXE" "$CWS_EXE" "$CWS_DOC" "$AGS_LIC" "$AGS_COPY" "$FTL" "$OPL3BANK" "$DMXOPL_LIC" LICENSE THIRD-PARTY.md docs/dist/README.TXT; do
    [[ -s "$f" ]] || die "missing $f"
done
# The CWSDPMI bytes are pinned (vendor/binaries.manifest): refuse anything else.
while read -r path _url sha; do
    [[ -z "$path" || "$path" == \#* ]] && continue
    got=$(sha256sum "$path" | cut -d' ' -f1)
    [[ "$got" == "$sha" ]] || die "$path sha256 $got does not match vendor/binaries.manifest ($sha)"
done < vendor/binaries.manifest

# The OPL3 bank is the hub's DMXOPL-generated file (THIRD-PARTY.md / LICENSE-REVIEW.md); refuse other bytes.
[[ "$(sha256sum "$OPL3BANK" | cut -d' ' -f1)" == "$OPL3BANK_SHA" ]] || die "$OPL3BANK is not the reviewed bank ($OPL3BANK_SHA)"

# The release exe must come from a clean, release-flavour build of the
# recorded patch series.
make -s verify-patches-applied >/dev/null || die "vendor trees do not match patches/ (make verify-patches-applied)"
bd=$(make -s DOSAGS_RELEASE=1 build-dirty)
[[ "$bd" == "build_dirty=0 "* ]] || die "release build is dirty: $bd"
SHA12=${bd##*sha12=}
# quit.cpp's strncpy of the 12-char stamp compiles to three 4-byte immediate
# stores, so the stamp is in the exe as three pieces, not one string.
python3 -c "import sys;d=open(sys.argv[1],'rb').read();s=sys.argv[2].encode();sys.exit(0 if all(s[i:i+4] in d for i in (0,4,8)) else 1)" "$EXE" "$SHA12" \
    || die "stamp $SHA12 not found in $EXE"

STAGE="$OUT/dosags-$VERSION"; ZIP="$OUT/dosags-$VERSION.zip"
rm -rf "$STAGE" "$ZIP"; mkdir -p "$STAGE"
crlf() { sed 's/\r$//; s/$/\r/'; }

install -m 0644 "$EXE"     "$STAGE/AGS.EXE"
install -m 0644 "$CWS_EXE" "$STAGE/CWSDPMI.EXE"
install -m 0644 "$OPL3BANK" "$STAGE/OPL3BANK.DAT"
crlf < "$CWS_DOC"  > "$STAGE/CWSDPMI.DOC"
crlf < LICENSE     > "$STAGE/LICENSE.TXT"
crlf < "$AGS_LIC"  > "$STAGE/ARTISTIC.TXT"
crlf < "$AGS_COPY" > "$STAGE/AGSCOPY.TXT"
crlf < "$FTL"      > "$STAGE/FTL.TXT"
crlf < THIRD-PARTY.md > "$STAGE/3RDPARTY.TXT"
url="${REPO_URL:-(not yet published -- see 3RDPARTY.TXT)}"
sed -e "s|@VERSION@|$VERSION|g" -e "s|@SHA12@|$SHA12|g" -e "s|@REPO_URL@|$url|g" docs/dist/README.TXT | crlf > "$STAGE/README.TXT"

# NOTICES.TXT: each linked library's own licence text, copied from the
# vendored source at build time (never retyped).
{
    sect() { printf '\n==============================================================================\n%s\n==============================================================================\n\n' "$1"; }
    echo "Licence notices for the libraries statically linked into AGS.EXE."
    echo "The AGS engine's own licence is ARTISTIC.TXT; FreeType's is FTL.TXT."
    sect "SDL 3 (zlib licence) -- vendor/SDL/LICENSE.txt"
    cat vendor/SDL/LICENSE.txt
    sect "miniz -- vendor/ags/libsrc/miniz/miniz.c"
    sed -n '2,25p' vendor/ags/libsrc/miniz/miniz.c
    sect "stb_image -- vendor/ags/libsrc/stb/LICENSE"
    cat vendor/ags/libsrc/stb/LICENSE
    sect "GLM (OpenGL Mathematics) -- vendor/ags/libsrc/glm/copying.txt"
    cat vendor/ags/libsrc/glm/copying.txt
    sect "aastr 0.1.1 (gift-ware) -- vendor/ags/Common/libsrc/aastr-0.1.1/aastr.c"
    sed -n '1,14p' vendor/ags/Common/libsrc/aastr-0.1.1/aastr.c
    sect "AllegroFont 2.0.9 (FreeType Project License, FTL.TXT) -- vendor/ags/Common/libsrc/alfont-2.0.9/README.txt"
    sed -n '1,22p' vendor/ags/Common/libsrc/alfont-2.0.9/README.txt
    sect "Allegro 4.4.3 (giftware)"
    cat <<'EOF'
The Allegro 4.4.3 subset vendored inside AGS carries no licence file of
its own; its sources point to Allegro's readme.txt. Allegro 4.4.3's
licence (docs/src/license._tx at upstream tag 4.4.3) is the giftware
licence: "Allegro is gift-ware. It was created by a number of people
working in cooperation, and is given to you freely as a gift. You may
use, modify, redistribute, and generally hack it about in any way you
like, and you do not have to give us anything in return." Thanks to the
Allegro developers. See LICENSE-REVIEW.md in the source repository.
EOF
    sect "OPL3BANK.DAT: DMXOPL GM FM bank (MIT) -- github.com/sneakernets/DMXOPL @ e83c144a2e6d, LICENSE"
    cat "$DMXOPL_LIC"
    sect "sdl-dos-ports shared modules (MIT) -- .sdl-dos-ports/LICENSE"
    cat .sdl-dos-ports/LICENSE
    sect "DJGPP C library and GCC runtime"
    cat <<'EOF'
Built with DJGPP and GCC 12.2.0, linked with the stock DJGPP C library.
DJGPP's copying.dj: runtime objects and libraries "when linked into an
application, may be distributed without sources ONLY if the recipient is
given sufficient information to obtain a copy of djgpp themselves."
DJGPP is available from https://www.delorie.com/djgpp/
The GCC runtime (libgcc, libstdc++) is used under the GCC Runtime Library
Exception, version 3.1.
EOF
} | crlf > "$STAGE/NOTICES.TXT"

# MANIFEST.TXT last: hashes of everything else, plus the build facts.
minstack=$(python3 -c "import struct,sys;d=open(sys.argv[1],'rb').read(0x220);assert d[0x200:0x210]==b'go32stub, v 2.05';print(struct.unpack_from('<I',d,0x214)[0]//1024)" "$STAGE/AGS.EXE") \
    || die "could not read the stub minstack from AGS.EXE"
[[ "$minstack" == 512 ]] || die "AGS.EXE stub minstack is ${minstack} KB, not the 512 KB every gate measured (Makefile AGS_MINSTACK)"
{
    echo "DOSAGS $VERSION"
    echo "build_sha12=$SHA12 flavour=release (DOSAGS_RELEASE=1)"
    echo "ags_exe_bytes=$(stat -c %s "$STAGE/AGS.EXE") stub_minstack_kb=$minstack"
    echo "source_commit=$(git rev-parse HEAD)$(git diff --quiet HEAD -- . 2>/dev/null || echo ' (+uncommitted changes)')"
    echo
    (cd "$STAGE" && LC_ALL=C ls | grep -v '^MANIFEST.TXT$' | xargs sha256sum)
} | crlf > "$STAGE/MANIFEST.TXT"

touch -d "@$(git log -1 --format=%ct)" "$STAGE"/*
(cd "$STAGE" && LC_ALL=C ls | zip -q -X -D "$ZIP" -@)
echo "make-dist: $ZIP ($(stat -c %s "$ZIP") bytes, AGS.EXE $SHA12)"
exec "$ROOT/scripts/check-dist.sh" "$ZIP" ${REPO_URL:+--repo-url "$REPO_URL"}
