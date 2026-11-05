#!/usr/bin/env bash
# Shards option (a): up to 4 --startr rooms, deterministic mode, plain then --break-a. Stops at the first
# room where plain is A==B ok and --break-a makes A!=B. Budget: 4 rooms, no more.
cd ~/git/dosags
S=/tmp/claude-1001/-home-claude-git-dosags/8d15788e-024f-45ef-9590-8caefc025dbf/scratchpad/shards-probe
mkdir -p "$S"
export DOSBOX_DISPLAY_NUM=211 GATE_CONF="$PWD/tests/harness/confs/dosbox-x-fixed40k-opl3.conf" GATE_FIXED_TIMESTEP=0 GATE_ASSERT_NO_SKIP=1
C=(--no-aq --no-control --no-pillarbox --no-bench16 --catalogue shards)
for N in 6 9 1 5; do
  lab="shards-r$N-alias-512x384"
  for mode in plain break; do
    o="$S/r$N-$mode"; rm -rf "$o"; ex=(); [[ $mode == break ]] && ex=(--break-a)
    GATE_CAT_STARTR_shards=$N tests/harness/gate-alias.sh --out "$o" "${C[@]}" --rows "$lab" "${ex[@]}" > "$o.log" 2>&1
    line=$(grep -h "^ *$lab" "$o"/*.txt "$o.log" 2>/dev/null | head -1)
    echo "r$N $mode: $line"
    grep -hE 'frames_skipped|VOID' "$o"/"$lab"/A-vs-B.txt "$o.log" 2>/dev/null | head -3 | sed 's/^/    /'
    grep -aohE 'Now in room -?[0-9]+' "$o.log" | sort | uniq -c | sed 's/^/    /'
  done
  if grep -q "$lab.*A==B: ok" "$S/r$N-plain.log" "$S/r$N-plain"/*.txt 2>/dev/null && grep -q "$lab.*A==B: FAIL" "$S/r$N-break.log" "$S/r$N-break"/*.txt 2>/dev/null; then
    echo "FOUND r$N"; break
  fi
done
