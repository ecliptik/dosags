#!/usr/bin/env bash
# gate-alias.sh -- the SCREEN == FULL-PUSH gate for every ALIAS-ON row (DOSBox-X, no hardware).
#
# gate-present.sh's verifier answers "do the pushed rects cover what the engine drew". It cannot answer "did the engine draw
# into the surface the alias adopted": with the alias on, the engine's frame IS the window surface, so a frame that was never
# drawn into it reads equal to the verifier's shadow. On 2026-09-21 the Mode 13h anim12 screen was found incomplete on every
# binary up to ags 0192 while the verifier read zero. This gate covers that second question by looking at the screen.
#
# Per alias-ON row (bench8 at the Mode 13h native rung, all 7 arms; the AGS Quest AutoPilot demo at 640x480x16 with the alias
# at y=60; bench8 at the 512x384 centred rung, two arms -- ags patch 0196's own gate, see below): run the arm three times
# with the engine freezing at chosen ticks (ags patch 0195) while the emulated screen is photographed,
#   A  default present                    -- the run under test
#   B  DOSAGS_DIRTY_PRESENT=0              -- the FULL-PUSH REFERENCE
#   C  DOSAGS_BREAK_0193=1                 -- the CONTROL: 0193's two mechanisms off; expected to DIFFER from B
# and require A == B pixel for pixel at every freeze, both froze at the same tick. C is the evidence the check can fail.
# Exit 1 if any A differs from B (or a pair is void/missing); exit 3 if no control failed anywhere (the gate would have no
# demonstrated power).
#
#   tests/harness/gate-alias.sh [--out DIR] [--arms "anim12 walk"] [--no-aq] [--no-control] [--no-pillarbox]
#                               [--no-bench16] [--no-catalogue] [--catalogue "5days shards"]
#   AGS_EXE=path/to/ags.exe overrides the binary (must carry ags patch 0195).
#   --rows "label ..."  run only these rows (labels as in summary.txt); the others are skipped whole.
#   --break-a           ALSO set DOSAGS_BREAK_0193=1 on the A run: a row must then FAIL. This is the
#                       per-row control for tests/ratchet.yaml (the check reads that row's problem
#                       count; a control that leaves A == B proves the row has no power).
set -u
HARNESS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HARNESS/../.." && pwd)"
ROW_AGS_ARGS=()   # per-row extra AGS args (catalogue --startr, see GATE_CAT_STARTR_<pkg>)
ROWS=""; BREAK_A=0; OUT=""; DO_AQ=1; DO_CTL=1; DO_PB=1; DO_B16=1; DO_CAT=1; ARMS="idle walk anim4 anim12 text gui full"
CATALOGUE="5days shards"
while [[ $# -gt 0 ]]; do
    case "$1" in
        --out) OUT="$2"; shift 2 ;;
        --arms) ARMS="$2"; shift 2 ;;
        --no-aq) DO_AQ=0; shift ;;
        --no-control) DO_CTL=0; shift ;;
        --no-pillarbox) DO_PB=0; shift ;;
        --no-bench16) DO_B16=0; shift ;;
        --no-catalogue) DO_CAT=0; shift ;;
        --catalogue) CATALOGUE="$2"; shift 2 ;;
        --rows) ROWS=" $2 "; shift 2 ;;
        --break-a) BREAK_A=1; shift ;;
        *) echo "usage: $0 [--out DIR] [--arms \"a b\"] [--no-aq] [--no-control] [--no-pillarbox] [--no-bench16] [--no-catalogue] [--catalogue \"a b\"]" >&2; exit 2 ;;
    esac
done
[[ -n "$OUT" ]] || OUT="$(mktemp -d)"
mkdir -p "$OUT"
# Host-wide DOSBox-X lock: ONE ACQUIRE PER RUN (2026-09-24, coordinator; was one EXCLUSIVE hold around
# the whole gate, hub 258d04f). The gate no longer takes the lock itself: every run_one below calls
# run-dosbox.sh, which takes the lock for that run in the mode the run needs -- EXCLUSIVE for a
# freeze capture at cycles=max, SHARED at a fixed-cycles conf with --no-host-input (GATE_CONF, and
# the AGS Quest row's default fixed-cycles mode) -- and releases it when the run ends. A whole-gate
# hold kept every other worker queued for the gate's full hour and defeated writer priority (hub
# fc70b4a). Nothing in the gate needs a hold across runs: each run has its own stage dir and, since
# b79e724, its own Xvfb and display flock, and A/B/C are compared file to file after the runs.
# Inside a caller that already holds the lock (ratchet.sh units export DOSBOX_LOCK_HELD=1), the runs
# take nothing, exactly as before.
# GATE_CONF=path (2026-09-23): run every row under that DOSBox-X conf; a fixed-cycles conf makes
# the gate deterministic whatever the host load, so its runs take the lock SHARED (hub bb5482c).
source "$HARNESS/dosbox-lock.sh"
GATE_CONF_ARGS=(); [[ -n "${GATE_CONF:-}" ]] && GATE_CONF_ARGS=(--conf "$GATE_CONF")
# GATE_FIXED_TIMESTEP=0 (2026-09-24): run WITHOUT --fixed-timestep. GameTick then updates the game
# once per tick and renders every tick, so a freeze lands on its target tick exactly -- the lab
# standard for screen-equality at fixed 40000 cycles, where the fixed-timestep catch-up would skip
# rendered ticks (AGS Quest skipped 1305 frames and froze 1-5 ticks late). GATE_ASSERT_NO_SKIP=1
# then VOIDs any row where a run reports frames_skipped > 0 (a freeze could have been stepped over).
# 2026-11-04: "without" is now SAID, not assumed -- DOSAGS_FIXED_TIMESTEP=0 is passed explicitly, because
# the DOSAGS_RELEASE flavour (ags 0351) defaults the fixed timestep ON when the variable is unset. Relying
# on the engine default ran a release-exe row WITH the catch-up (agsquest-alias-y60: frames_skipped
# 1291/1301, VOID). The instrumented flavour reads "0" exactly as it read "unset".
GATE_TS_ARGS=(--fixed-timestep); [[ "${GATE_FIXED_TIMESTEP:-1}" == "0" ]] && GATE_TS_ARGS=(--env DOSAGS_FIXED_TIMESTEP=0)
FIX="$REPO/tests/fixtures/bench/cfg"
NATIVE="$HARNESS/presentation/bench8/ACSETUP-OFF-NATIVE.CFG"
# ags patch 0196's own gate: bench8 (320x200 native) staged at the SAME 512x384-round cfg
# every 320-wide catalogue title used today (S2T1/S2F1/S2M1/S2S1) -- centred both ways, x=96
# y=92 (matches S2M1's own logged "render dest (96, 92, 415, 291 : 320 x 200)" exactly), the
# real geometry the fix targets: Trilby's Notes (320x240) at this same rung is ALSO centred
# both ways (x=96, y=72), so "both offsets nonzero" is not a hypothetical for this campaign,
# it is the primary target case. A pure horizontal-only row (x!=0, y=0) is not included: that
# needs a window whose HEIGHT exactly matches the game's native height while its WIDTH does
# not -- no VESA mode in this rig's enumeration has a nonstandard height paired with a wider-
# than-native width (512x200/640x200 are not offered), so no current or near-future 320-wide
# fixture can land there; the pure-vertical case (x=0, y=60) already has a standing row below
# (agsquest-alias-y60) and is unchanged by this patch's own symmetry with the x handling.
PILLARBOX="$HARNESS/presentation/trilbysnotes/ACSETUP-OFF-512X384-ROUND.CFG"
declare -A SCENE=( [idle]=idle [walk]=walk [anim4]=anim [anim12]=anim [text]=text [gui]=gui [full]=full [walk-gate]=walk [anim12-gate]=anim )
declare -A TICKS=( [idle]=100,300,500,700,900 [walk]=100,300,500,700,900 [anim4]=100,300,500,700,900 [anim12]=100,300,500,700,900
                   [text]=100,300,500,700,900 [gui]=100,300,500,700,900 [full]=10,40,80,120,200
                   [walk-gate]=500,1500,2500,3500,4500 [anim12-gate]=500,1500,2500,3500,4500 )   # the 5000-tick --gate windows
AQ_TICKS=100,420,700,1000,1300,1600,1900,2200,2700,3300
SUMMARY="$OUT/summary.txt"; : > "$SUMMARY"
FAILS=0; CONTROLS_FAILED=0; CONTROLS_RUN=0

run_one() { # dir pkg cfgs... -- envs...
    local d="$1" pkg="$2"; shift 2
    local incl=() envs=()
    while [[ $# -gt 0 && "$1" != "--" ]]; do incl+=(--include-extra "$1"); shift; done; shift
    while [[ $# -gt 0 ]]; do envs+=(--env "$1"); shift; done
    mkdir -p "$d"
    # No outer `timeout` (2026-09-26): since the per-run lock split each run_one waits for the host lock INSIDE
    # run-dosbox.sh, and an outer timeout counts that wait -- under contention it killed runs still queued for the
    # lock (LAB-S32 23.13: arms "Terminated" while "waiting ... to take the exclusive lock"). run-dosbox.sh's own
    # --timeout starts after the lock is taken and bounds the run itself.
    ( cd "$HARNESS" && ./run-dosbox.sh "$pkg" --no-host-input "${GATE_TS_ARGS[@]}" "${incl[@]}" "${envs[@]}" "${GATE_CONF_ARGS[@]}" "${ROW_AGS_ARGS[@]}" --freeze-capture "$d" --timeout "$(( ${GATE_RUN_TIMEOUT:-900} - 100 ))" ) > "$d/run.log" 2>&1
}

row() { # label pkg min-pairs freeze-ticks scene-envs... (cfg files via $ROWCFG array)
    local label="$1" pkg="$2" min="$3" ticks="$4"; shift 4
    local base=("$@") a="$OUT/$label/A" b="$OUT/$label/B" c="$OUT/$label/C"
    [[ -z "$ROWS" || "$ROWS" == *" $label "* ]] || return 0
    local abreak=(); [[ $BREAK_A -eq 1 ]] && abreak=(DOSAGS_BREAK_0193=1)
    run_one "$a" "$pkg" "${ROWCFG[@]}" -- "${base[@]}" "DOSAGS_FREEZE_TICKS=$ticks" "${abreak[@]}"
    run_one "$b" "$pkg" "${ROWCFG[@]}" -- "${base[@]}" "DOSAGS_FREEZE_TICKS=$ticks" DOSAGS_DIRTY_PRESENT=0
    python3 "$HARNESS/screen-equal.py" "$a" "$b" --min "$min" > "$OUT/$label/A-vs-B.txt" 2>&1; local rc=$?
    local verdict="ok"; [[ $rc -eq 0 ]] || { verdict="FAIL"; FAILS=$((FAILS + 1)); }
    if [[ "${GATE_ASSERT_NO_SKIP:-0}" == "1" ]]; then
        local sk skips=""
        for x in "$a" "$b"; do
            sk="$(/usr/bin/grep -aho 'frames_skipped=[0-9]*' "$(cat "$x/stage" 2>/dev/null)/RUNMANI.LOG" 2>/dev/null | head -1 | cut -d= -f2)"
            skips="$skips${skips:+/}${sk:-?}"
            if [[ "${sk:-x}" != "0" ]]; then [[ "$verdict" == VOID* ]] || { [[ "$verdict" == FAIL ]] || FAILS=$((FAILS + 1)); verdict="VOID"; }; fi
        done
        echo "frames_skipped A/B: $skips" >> "$OUT/$label/A-vs-B.txt"
        [[ "$verdict" == VOID ]] && verdict="VOID(skipped $skips)"
    fi
    local ctl="-"
    if [[ $DO_CTL -eq 1 ]]; then
        run_one "$c" "$pkg" "${ROWCFG[@]}" -- "${base[@]}" "DOSAGS_FREEZE_TICKS=$ticks" DOSAGS_BREAK_0193=1
        python3 "$HARNESS/screen-equal.py" "$c" "$b" --min "$min" > "$OUT/$label/C-vs-B.txt" 2>&1; local crc=$?
        CONTROLS_RUN=$((CONTROLS_RUN + 1))
        if [[ $crc -ne 0 ]]; then ctl="control FAILS as required"; CONTROLS_FAILED=$((CONTROLS_FAILED + 1)); else ctl="control did NOT fail (no power on this row)"; fi
    fi
    printf '%-22s A==B: %-4s | %s | %s\n' "$label" "$verdict" "$(/usr/bin/grep -a "screen-equal:" "$OUT/$label/A-vs-B.txt" | tail -1) $(/usr/bin/grep -a "frames_skipped A/B" "$OUT/$label/A-vs-B.txt" | tail -1)" "$ctl" >> "$SUMMARY"
}

for arm in $ARMS; do
    d="$OUT/cfg-$arm"; mkdir -p "$d"; cp "$NATIVE" "$d/ACSETUP.CFG"; cp "$FIX/$arm.cfg" "$d/BENCH.CFG"
    ROWCFG=("$d/ACSETUP.CFG" "$d/BENCH.CFG")
    min=3; [[ "$arm" == full ]] && min=2
    exit_tick=1500; [[ "$arm" == *-gate ]] && exit_tick=6000   # a --gate window is 5000 ticks; the 1500 safety net would cut it
    row "bench8-alias-$arm" bench8 "$min" "${TICKS[$arm]}" "DOSAGS_SCENE=${SCENE[$arm]}" "DOSAGS_TAS_AUTO_EXIT_TICK=$exit_tick"
done
# AGS Quest runs with SOUND OFF (2026-09-22, coordinator decision; PLAN.md step 8, "AQ gate row").
# Its music is SB PCM. Once SDL patch 0191 made the driver ring pace playback to the device, when a
# clip finishes is wall-clock time, and a script step that waits on a sound can land a tick either
# side between the A and B runs (AUTOPLT phase=key ok at 1194 vs 1195) -- a game-state divergence
# this row would read as a present defect. This gate judges the present path; audio has its own
# cells (AR*/OVW*, step 8.3). The cfg carries only [sound] enabled=0; every other setting stays the
# package default this row always used.
if [[ $DO_AQ -eq 1 ]]; then
    d="$OUT/cfg-aq"; mkdir -p "$d"; printf '[sound]\r\nenabled=0\r\n' > "$d/ACSETUP.CFG"
    ROWCFG=("$d/ACSETUP.CFG")
    # Mode (coordinator decision 2026-09-24, PLAN.md): fixed 40000 cycles (tools/dosbox-x.conf), NO
    # fixed timestep (every tick renders, so each freeze lands on its tick; needs ags 0214), and the
    # row VOIDs if any run skipped a frame. At cycles=max this row diverged by one tick now and then
    # (host timing); in this mode it was 3/3 clean. It leaves quarantine after 10 consecutive clean
    # runs in this mode; any divergence here resets the count. GATE_AQ_LEGACY=1 runs the old way.
    if [[ "${GATE_AQ_LEGACY:-0}" != "1" ]]; then
        _ts=("${GATE_TS_ARGS[@]}"); _cf=("${GATE_CONF_ARGS[@]}"); _ns="${GATE_ASSERT_NO_SKIP:-0}"; _rt="${GATE_RUN_TIMEOUT:-}"
        GATE_TS_ARGS=(--env DOSAGS_FIXED_TIMESTEP=0); GATE_CONF_ARGS=(--conf "$REPO/tools/dosbox-x.conf"); GATE_ASSERT_NO_SKIP=1;   # explicit off: see GATE_TS_ARGS above (2026-11-04)
        GATE_RUN_TIMEOUT="${GATE_RUN_TIMEOUT:-3000}"
        row "agsquest-alias-y60" agsquest 8 "$AQ_TICKS"
        GATE_TS_ARGS=("${_ts[@]}"); GATE_CONF_ARGS=("${_cf[@]}"); GATE_ASSERT_NO_SKIP="$_ns"; GATE_RUN_TIMEOUT="$_rt"
        [[ -n "$GATE_RUN_TIMEOUT" ]] || unset GATE_RUN_TIMEOUT
    else
        row "agsquest-alias-y60" agsquest 8 "$AQ_TICKS"
    fi
fi
if [[ $DO_PB -eq 1 ]]; then
    for arm in idle anim12; do
        d="$OUT/cfg-512x384-$arm"; mkdir -p "$d"; cp "$PILLARBOX" "$d/ACSETUP.CFG"; cp "$FIX/$arm.cfg" "$d/BENCH.CFG"
        ROWCFG=("$d/ACSETUP.CFG" "$d/BENCH.CFG")
        row "bench8-alias-512x384-$arm" bench8 3 "${TICKS[$arm]}" "DOSAGS_SCENE=${SCENE[$arm]}" "DOSAGS_TAS_AUTO_EXIT_TICK=1500"
    done
fi
# ags patch 0196 generalization (2026-09-22): the x,y placement math is proven at 8bpp (bench8
# above, twice, plus real hardware -- PLAN.md S2T2). What is NOT yet exercised anywhere is the
# patch's one new arithmetic term, dst.x * bytes_per_pixel, with a NONZERO product -- every
# existing row with bytes_per_pixel > 1 (agsquest-alias-y60) has dst.x == 0. BENCH16 is the same
# source as BENCH8 at 320x200/16bpp (tests/games/bench16), an exact geometry match for Maniac
# Mansion Deluxe's own 320x200/16bpp at this rung -- reuses the pillarbox rows' own pattern.
if [[ $DO_B16 -eq 1 ]]; then
    for arm in idle anim12; do
        d="$OUT/cfg-b16-512x384-$arm"; mkdir -p "$d"; cp "$PILLARBOX" "$d/ACSETUP.CFG"; cp "$FIX/$arm.cfg" "$d/BENCH.CFG"
        ROWCFG=("$d/ACSETUP.CFG" "$d/BENCH.CFG")
        row "bench16-alias-512x384-$arm" bench16 3 "${TICKS[$arm]}" "DOSAGS_SCENE=${SCENE[$arm]}" "DOSAGS_TAS_AUTO_EXIT_TICK=1500"
    done
fi
# Real-game rows, no synthetic fixture available at these native sizes/depths: 5 Days a Stranger
# (320x240/16bpp, x=96 y=72 -- the SAME x,y as Trilby's own hardware-proven S2T2 case, but at
# 16bpp instead of 8bpp) and Shards of God (320x200/32bpp, x=96 y=92 -- the first exercise of
# this patch at 32bpp anywhere, DOSBox-X or hardware; no BENCH32 has ever been built). Title-idle
# freeze ticks only (no AutoPilot to drive either past its title screen); DOSAGS_TAS_AUTO_EXIT_TICK
# bounds the run so it does not sit waiting for a keypress after the freezes are done.
declare -A CAT_TICKS=( [5days]=100,300,500,700,900 [shards]=100,300,500,700,900 )
# GATE_CAT_TICKS_<pkg>=t1,t2,... (2026-11-04) overrides one catalogue row's freeze ticks, e.g. for a row
# whose title goes static early (Shards: static after tick 100, so --break-a cannot make it differ there).
for _p in 5days shards; do _v="GATE_CAT_TICKS_$_p"; [[ -n "${!_v:-}" ]] && CAT_TICKS[$_p]="${!_v}"; done
# GATE_CAT_STARTR_<pkg>=N (2026-11-04) starts that catalogue row in room N (AGS's --startr debug jump) instead
# of on its title, and labels it "<pkg>-r<N>-alias-512x384" so it never shares a label with the title row. The
# jump leaves the player at the room's default position with no input; that is enough for a present-path
# comparison (A == B), and the point is a scene that MOVES, so --break-a can make it fail.
if [[ $DO_CAT -eq 1 ]]; then
    for pkg in $CATALOGUE; do
        d="$OUT/cfg-cat-$pkg"; mkdir -p "$d"; cp "$PILLARBOX" "$d/ACSETUP.CFG"
        ROWCFG=("$d/ACSETUP.CFG")
        _v="GATE_CAT_STARTR_$pkg"; _lab="$pkg-alias-512x384"; ROW_AGS_ARGS=()
        if [[ -n "${!_v:-}" ]]; then _lab="$pkg-r${!_v}-alias-512x384"; ROW_AGS_ARGS=(--ags-arg --startr --ags-arg "${!_v}"); fi
        row "$_lab" "$pkg" 5 "${CAT_TICKS[$pkg]}" "DOSAGS_TAS_AUTO_EXIT_TICK=1000"
        ROW_AGS_ARGS=()
    done
fi
echo "gate-alias: $FAILS failing row(s); controls that failed as required: $CONTROLS_FAILED of $CONTROLS_RUN; table in $SUMMARY" >&2
cat "$SUMMARY"
[[ $FAILS -eq 0 ]] || exit 1
if [[ $DO_CTL -eq 1 && $CONTROLS_FAILED -eq 0 ]]; then echo "gate-alias: NO control failed anywhere: the check has no demonstrated power" >&2; exit 3; fi
exit 0
