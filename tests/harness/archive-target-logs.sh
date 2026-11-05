#!/usr/bin/env bash
# archive-target-logs.sh -- fetch every <TAG>.LOG off the target and verify
# each one before anything is deleted.
#
# C:\DOSAGS has accumulated one log per cell since 2026-09-11 and now holds
# 316 files. The repo's tests/harness/results/ tree holds 55 cells. For the
# difference, the target is the only copy, so this script's contract is:
#
#   VERIFY EVERY FILE, THEN PRINT WHAT A CLEAR WOULD DELETE. IT NEVER
#   DELETES ANYTHING ITSELF.
#
# Deleting is a separate, deliberate step a human or a later script takes
# after reading this one's report. A fetch-and-delete in one pass is how the
# only copy of something goes missing on a partial failure.
#
# Scope: .LOG files only, 281 of them, 6.1 MB. The .AGS and .EXE files on
# that volume total 91 MB and are staged from this repo on every single cell
# -- fetching them would be 90 MB of transfer to re-acquire what is already
# in git.
#
# Usage:
#   ./archive-target-logs.sh [--out DIR] [--from DOS-DIR]
#
# Default --out is tests/harness/results/target-archive-<date>/.

set -uo pipefail

HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT_DIR="$HARNESS_DIR/results/target-archive-$(date +%F)"
FROM='C:\DOSAGS'

while [[ $# -gt 0 ]]; do
    case "$1" in
        --out)  OUT_DIR="$2"; shift 2 ;;
        --from) FROM="$2"; shift 2 ;;
        *) echo "archive-target-logs.sh: unknown argument $1" >&2; exit 2 ;;
    esac
done

vc() { "$HARNESS_DIR/../../tools/vcctrl/bin/vcctrl" "$@" 2>/dev/null || vcctrl "$@"; }

mkdir -p "$OUT_DIR"
echo "== archive-target-logs.sh: $FROM -> $OUT_DIR =="

# The listing is a RETAINED reading, not a live poll. Refuse to work from a
# stale one: a name that has since been deleted fetches nothing, and a name
# added since is not in the list at all and would be silently left behind --
# which is the exact failure this whole exercise is about.
LIST="$(vc file-list --from "$FROM")" || { echo "REFUSED: no listing" >&2; exit 1; }
AGE="$(printf '%s' "$LIST" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("age_s","?"))')"
echo "listing age: ${AGE}s"
if python3 -c "import sys; sys.exit(0 if float('$AGE') < 3600 else 1)" 2>/dev/null; then
    echo "  (fresh enough)"
else
    echo "REFUSED: listing is ${AGE}s old. Run a cell or file-refresh first --" >&2
    echo "  a stale listing silently omits anything added since it was taken." >&2
    exit 1
fi

mapfile -t NAMES < <(printf '%s' "$LIST" | python3 -c '
import json,sys
def files(o):
    if isinstance(o,list) and o and isinstance(o[0],dict) and "name" in o[0]: return o
    if isinstance(o,dict):
        for v in o.values():
            r=files(v)
            if r: return r
    return []
for f in files(json.load(sys.stdin)):
    if f["name"].upper().endswith(".LOG") and f.get("fetchable"):
        print("%s\t%d" % (f["name"], f.get("bytes",0)))
')

echo "${#NAMES[@]} .LOG files to fetch"
[[ ${#NAMES[@]} -gt 0 ]] || { echo "REFUSED: nothing to fetch" >&2; exit 1; }

FAILED=0
VERIFIED=0
: > "$OUT_DIR/MANIFEST.tsv"
for row in "${NAMES[@]}"; do
    name="${row%%$'\t'*}"
    want="${row##*$'\t'}"
    vc get-file "$name" --return --from "$FROM" >/dev/null
    vc pulled save "$name" --out "$OUT_DIR/$name" >/dev/null 2>&1
    if [[ ! -f "$OUT_DIR/$name" ]]; then
        echo "  MISSING  $name" >&2; FAILED=$((FAILED+1)); continue
    fi
    got="$(stat -c %s "$OUT_DIR/$name")"
    if [[ "$got" != "$want" ]]; then
        echo "  SIZE     $name: got $got, listing said $want" >&2
        FAILED=$((FAILED+1)); continue
    fi
    printf '%s\t%s\t%s\n' "$name" "$got" "$(sha256sum "$OUT_DIR/$name" | cut -d' ' -f1)" \
        >> "$OUT_DIR/MANIFEST.tsv"
    VERIFIED=$((VERIFIED+1))
done

echo
echo "verified $VERIFIED / ${#NAMES[@]}, failed $FAILED"
if (( FAILED > 0 )); then
    echo "REFUSED: $FAILED file(s) did not verify. DELETE NOTHING." >&2
    echo "  The target is the only copy of part of this campaign's evidence." >&2
    exit 1
fi
echo "all files verified and listed in $OUT_DIR/MANIFEST.tsv"
echo
echo "A clear would delete these ${#NAMES[@]} names from $FROM."
echo "This script does not delete. Commit the archive first, then clear"
echo "deliberately as a separate step."
