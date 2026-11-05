#!/bin/bash
# Polls vcctrl level+spectrum every ~3.5s for up to DURATION seconds,
# appending one JSON line per poll to OUT. Matches S4MIDI1's own
# ~3.5s-interval methodology.
set -u
cd ~/git/vcctrl || exit 1
OUT="$1"
DURATION="${2:-750}"
START=$(date +%s.%N)
: > "$OUT"
while true; do
  NOW=$(date +%s.%N)
  ELAPSED=$(echo "$NOW - $START" | bc)
  DONE=$(echo "$ELAPSED >= $DURATION" | bc)
  if [ "$DONE" = "1" ]; then
    break
  fi
  LVL=$(./bin/vcctrl level 3000 2>/dev/null)
  SPEC=$(./bin/vcctrl spectrum 3000 2>/dev/null)
  printf '{"t": %s, "level": %s, "spectrum": %s}\n' "$ELAPSED" "$LVL" "$SPEC" >> "$OUT" 2>/dev/null
  sleep 3.5
done
echo "poll loop done, $(wc -l < "$OUT") samples written to $OUT"
