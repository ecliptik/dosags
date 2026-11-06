#!/usr/bin/env bash
# public-snapshot.sh -- build the public GitHub snapshot of a dosags commit, locally. NEVER pushes.
#
#   scripts/public-snapshot.sh <commit> [--dry-run] [--message-file F] [--ref R]
#
# The public repo (github.com/ecliptik/dosags) is not a mirror: it starts from one orphan snapshot
# (a4695848, operator 2026-11-05) and each later sync is one more commit on top, whose parent is the
# last published snapshot, recorded locally as refs/public/github-main (never pushed to Forgejo).
#
# The tree is <commit>'s tree minus the drop rule (operator's choice of content, 2026-11-05):
# under tests/harness/results/ only, any *.png *.jpg *.jpeg *.bmp *.gif *.bin (any case) and any
# AGSSAVE.* (any case) -- photos, frame dumps, binary tick dumps and AGS saves; the text record stays.
# It is built in a temporary index (GIT_INDEX_FILE), so the work tree and the real index are untouched.
#
# REFUSES (exit 1) when the filtered tree:
#   - still has a path the drop rule matches (a check on the result, not only on the filter);
#   - names a *.ts.net host other than *.example.ts.net, in any file (text or binary) or path.
# Also refuses when <commit>'s filtered tree equals the last snapshot's (nothing to publish), unless
# --dry-run, which only prints the tree id and the counts.
#
# Without --dry-run it writes the commit (parent = --ref, default refs/public/github-main) and moves
# the ref with an old-value check. Pushing is a separate step, done after the operator's OK:
#   git push github refs/public/github-main:refs/heads/main     (not by this script)
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
COMMIT=""; DRY=0; MSGFILE=""; REF=refs/public/github-main
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)      DRY=1; shift ;;
        --message-file) MSGFILE="$2"; shift 2 ;;
        --ref)          REF="$2"; shift 2 ;;
        -*) echo "usage: $0 <commit> [--dry-run] [--message-file F] [--ref R]" >&2; exit 2 ;;
        *)  COMMIT="$1"; shift ;;
    esac
done
die() { echo "public-snapshot: $*" >&2; exit 1; }
[[ -n "$COMMIT" ]] || die "no commit given"
SRC=$(git rev-parse --verify "$COMMIT^{commit}") || die "not a commit: $COMMIT"
PARENT=$(git rev-parse --verify -q "$REF^{commit}") || die "$REF does not exist (the first snapshot, a4695848, was made by hand)"
SHORT=$(git rev-parse --short=8 "$SRC")

DROP_RE='^tests/harness/results/(.*\.([Pp][Nn][Gg]|[Jj][Pp][Gg]|[Jj][Pp][Ee][Gg]|[Bb][Mm][Pp]|[Gg][Ii][Ff]|[Bb][Ii][Nn])|(.*/)?[Aa][Gg][Ss][Ss][Aa][Vv][Ee]\.[^/]*)$'

TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
export GIT_INDEX_FILE="$TMP/index"
git ls-tree -r --full-tree "$SRC" > "$TMP/all"
# ls-tree lines are "mode SP type SP sha TAB path"; the filter reads the path after the TAB.
# The pattern goes in through ENVIRON, not -v: -v processes escapes and would turn \. into "any char".
DROP_RE="$DROP_RE" awk -F'\t' '$2 ~ ENVIRON["DROP_RE"] { print > "'"$TMP"'/dropped"; next } { print }' "$TMP/all" > "$TMP/kept"
touch "$TMP/dropped"
git read-tree --empty
git update-index --index-info < "$TMP/kept"
TREE=$(git write-tree)
unset GIT_INDEX_FILE

# Checks on the RESULT tree.
bad=$(git ls-tree -r --name-only "$TREE" | grep -E "$DROP_RE" || true)
[[ -z "$bad" ]] || die "the filtered tree still has dropped-rule paths: $(echo "$bad" | head -3 | tr '\n' ' ')"
hosts=$( { git ls-tree -r --name-only "$TREE"; git grep -a -h -o -E '[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.ts\.net' "$TREE" -- . 2>/dev/null; } \
         | grep -o -E '[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.ts\.net' | grep -v -E '(^|\.)example\.ts\.net$' | sort -u || true)
[[ -z "$hosts" ]] || die "the filtered tree names $(echo "$hosts" | wc -l) tailnet host(s) other than *.example.ts.net (names not printed; run git grep -n ts.net $TREE)"

echo "public-snapshot: source $SRC"
echo "public-snapshot: kept $(wc -l < "$TMP/kept") files, dropped $(wc -l < "$TMP/dropped") ($(awk -F'\t' '{print $2}' "$TMP/dropped" | sed -E 's/.*\.//' | sort | uniq -c | sort -rn | awk '{printf "%s %s, ", $1, $2}' | sed 's/, $//'))"
echo "public-snapshot: tree $TREE; last snapshot $PARENT (tree $(git rev-parse "$PARENT^{tree}"))"
echo "public-snapshot: checks passed (no dropped-rule path; no *.ts.net name but *.example.ts.net)"
if (( DRY )); then
    echo "public-snapshot: --dry-run: no commit, $REF unchanged"
    exit 0
fi
[[ "$TREE" != "$(git rev-parse "$PARENT^{tree}")" ]] || die "tree equals the last snapshot's: nothing to publish"

if [[ -n "$MSGFILE" ]]; then
    [[ -s "$MSGFILE" ]] || die "empty or missing --message-file $MSGFILE"
    cp "$MSGFILE" "$TMP/msg"
else
    cat > "$TMP/msg" <<EOF
dosags: public source snapshot of Forgejo main $SHORT

Sync of the public repository to Forgejo main $SHORT. The history lives in the project's private
forge; commit hashes cited in STATUS.md, PLAN*.md and the results READMEs refer to it.

Test evidence under tests/harness/results/ is the text record only (logs, JSON, READMEs,
checksums); camera and screen photos, BMP frame dumps, AGS save files and binary tick dumps are
omitted. No AGS game data is included: games are supplied by the player, as described in README.md.
EOF
fi
NEW=$(git commit-tree "$TREE" -p "$PARENT" -F "$TMP/msg")
git update-ref -m "public-snapshot $SHORT" "$REF" "$NEW" "$PARENT"
echo "public-snapshot: $REF $PARENT -> $NEW (not pushed)"
