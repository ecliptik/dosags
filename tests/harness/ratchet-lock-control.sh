#!/usr/bin/env bash
# ratchet-lock-control.sh OUT -- the control for tests/ratchet.yaml's code-lock-bytes check: a
# recorded cell's SDL 0194 lock line (results/MCLK-2026-09-23) with the locked size raised by 1 MB (above any limit this
# file is likely to hold),
# read by the same ratchet-facts.py. It proves the parser and the limit, not a real code growth
# (that needs a second build). Writes OUT/facts.txt. No DOSBox-X.
set -u
HARNESS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${1:?out dir}"; SRC="$HARNESS/results/MCLK-2026-09-23"
mkdir -p "$OUT/cell"
cp "$SRC/RUNMANI.LOG" "$SRC/STDOUT.TXT" "$OUT/cell/"
python3 -c 'import re,sys; t=open(sys.argv[1],errors="replace").read()
sys.stdout.write(re.sub(r"\) = ([0-9]+) bytes: locked", lambda m: ") = %d bytes: locked" % (int(m.group(1)) + 1048576), t))' \
    "$SRC/SDLDBG.LOG" > "$OUT/cell/SDLDBG.LOG"
python3 "$HARNESS/ratchet-facts.py" "$OUT/cell" > "$OUT/facts.txt"
/usr/bin/grep 'code_lock_bytes' "$OUT/facts.txt"
