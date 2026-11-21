#!/usr/bin/env bash
# gate-2x.sh -- the LAB 2x screen-equality gate (DOSBox-X, no hardware) for the narrowed integer-2x present overlay
# tests/harness/apply-2x.py. Registered in tests/harness/results/LAB2X-2026-11-19/PREREG-2X.md (sec. 4 + FIX-UP 1); the
# verdicts come from tests/harness/gate-2x-read.py, which this calls at the end and which can be re-run on OUT alone.
#
# It reuses gate-alias.sh's machinery (run-dosbox.sh --freeze-capture: the engine freezes at chosen ticks, ags 0195, and
# the emulated screen is photographed; screen-equal.py compares two runs pixel for pixel at equal ticks) with its own arm
# set, because gate-alias.sh's row() hard-codes A/B/C:
#   A   S2NR  DOSAGS_SCALE2_NARROW=1                                   the run under test
#   B   S2NR  DOSAGS_DIRTY_PRESENT=0 (switch unset)                    REFERENCE: today's full 2x
#   F   S2NR  DOSAGS_SCALE2_NARROW=1 DOSAGS_DIRTY_PRESENT=0            the new full-frame 2x copier only
#   C1  S2NR  DOSAGS_SCALE2_NARROW=1 DOSAGS_BREAK_0193=1               control: 0193 off
#   C2  S2NR  DOSAGS_SCALE2_NARROW=1 DOSAGS_SCALE2_BREAK=3             control: no narrowed box blitted (FIX-UP 3; was 2)
#   C2i S2NR  DOSAGS_SCALE2_NARROW=1 DOSAGS_SCALE2_BREAK=1             information (game rows): boxes 1 px short (gate1's C2)
#   V   S2NR  DOSAGS_SCALE2_NARROW=1 DOSAGS_SCALE2_VERIFY=1            whole-frame verifier
#   V2  S2NR  DOSAGS_SCALE2_NARROW=1 DOSAGS_SCALE2_VERIFY=1 DOSAGS_SCALE2_BREAK=3   the verifier's control (FIX-UP 3)
#   R   PLAIN (the shipped 0383 release, sha256 c68241073cb0...) default env   identity: must equal B (game rows)
#   I1  S2NR  DOSAGS_MAX_SCALE=1 DOSAGS_SCALE2_NARROW=1  } the 1x inertness pair (row S16-1x): equal, and I1's
#   I0  S2NR  DOSAGS_MAX_SCALE=1                         } scale2 line all zeros but rej geom
# Mode (every run): fixed 40000 cycles (tools/dosbox-x.conf), DOSAGS_FIXED_TIMESTEP=0 said explicitly (the release flavour
# defaults it on), --no-host-input (the only input is the engine's own DOSAGS_TICKCLICKS), sound off (cfg), direct
# framebuffer on (as the RV lines). Each run's RUNMANI.LOG / STDOUT.TXT are copied out of the stage at once (stage GC).
#
#   tests/harness/gate-2x.sh --exe PATH/S2NR.EXE --plain PATH/PLAIN.EXE --out DIR [--rows "S16-2x CLK-2x ..."]
#                            [--arms "A B ..."] [--read-only]
#   GATE_RUN_TIMEOUT=S (default 3000) bounds each run after its lock is taken.
#   --rows / --arms restrict what runs (the reader then reports the rest MISSING); --read-only runs nothing.
# Exit: the reader's (0 PASS, 1 a FAIL or VOID, 3 a control without power).
# FIX-UP 2 (PREREG-2X.md): C2 / V2 at DOSAGS_SCALE2_BREAK=2, C2i (BREAK=1) as information on the game rows; the reader's
# frames_skipped witness accepts 0 or -1 when the whole row reads the reference arm's value; "rej fmt=0" is information.
# FIX-UP 3: C2 / V2 at DOSAGS_SCALE2_BREAK=3 (no narrowed box blitted); C2 registered on the bench rows too.
set -u
HARNESS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HARNESS/../.." && pwd)"
PLAIN_SHA256=c68241073cb0dbcc6f0870c22ba31a0d904dd2261e72a44fbb7ba75f6cfb7f43
EXE=""; PLAIN=""; OUT=""; ROWS=""; ARMS_ONLY=""; READ_ONLY=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --exe) EXE="$2"; shift 2 ;;
        --plain) PLAIN="$2"; shift 2 ;;
        --out) OUT="$2"; shift 2 ;;
        --rows) ROWS=" $2 "; shift 2 ;;
        --arms) ARMS_ONLY=" $2 "; shift 2 ;;
        --read-only) READ_ONLY=1; shift ;;
        *) echo "usage: $0 --exe S2NR.EXE --plain PLAIN.EXE --out DIR [--rows \"..\"] [--arms \"..\"] [--read-only]" >&2; exit 2 ;;
    esac
done
[[ -n "$OUT" ]] || { echo "gate-2x: --out is required" >&2; exit 2; }
mkdir -p "$OUT"
if [[ $READ_ONLY -eq 0 ]]; then
    [[ -f "$EXE" && -f "$PLAIN" ]] || { echo "gate-2x: --exe and --plain must both exist" >&2; exit 2; }
    for x in "$EXE" "$PLAIN"; do
        [[ "$(basename "$x")" =~ ^[A-Za-z0-9_-]{1,8}\.[Ee][Xx][Ee]$ ]] || { echo "gate-2x: $x is not an 8.3 name" >&2; exit 2; }
    done
    _ps="$(sha256sum "$PLAIN" | cut -c1-64)"
    [[ "$_ps" == "$PLAIN_SHA256" ]] || { echo "gate-2x: REFUSED: --plain sha256 $_ps is not the shipped release $PLAIN_SHA256" >&2; exit 2; }
    [[ "$(sha256sum "$EXE" | cut -c1-64)" != "$PLAIN_SHA256" ]] || { echo "gate-2x: REFUSED: --exe is the plain release" >&2; exit 2; }
    { echo "exe $(sha256sum "$EXE")"; echo "plain $(sha256sum "$PLAIN")"; echo "started $(date -u +%FT%TZ)"; } > "$OUT/BINARIES.txt"
fi
CONF="$REPO/tools/dosbox-x.conf"
CFG640="$HARNESS/presentation/trilbysnotes/ACSETUP-OFF-640X480.CFG"
CFG640B="$HARNESS/presentation/bench8/ACSETUP-OFF-640X480.CFG"
FIX="$REPO/tests/fixtures/bench/cfg"
FB=SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1

arm_env() {
    case "$1" in
        A)  echo "DOSAGS_SCALE2_NARROW=1" ;;
        B)  echo "DOSAGS_DIRTY_PRESENT=0" ;;
        F)  echo "DOSAGS_SCALE2_NARROW=1 DOSAGS_DIRTY_PRESENT=0" ;;
        C1) echo "DOSAGS_SCALE2_NARROW=1 DOSAGS_BREAK_0193=1" ;;
        C2) echo "DOSAGS_SCALE2_NARROW=1 DOSAGS_SCALE2_BREAK=3" ;;     # FIX-UP 3 (FIX-UP 2: 2; before: 1)
        C2i) echo "DOSAGS_SCALE2_NARROW=1 DOSAGS_SCALE2_BREAK=1" ;;    # FIX-UP 2: gate1's C2, information
        V)  echo "DOSAGS_SCALE2_NARROW=1 DOSAGS_SCALE2_VERIFY=1" ;;
        V2) echo "DOSAGS_SCALE2_NARROW=1 DOSAGS_SCALE2_VERIFY=1 DOSAGS_SCALE2_BREAK=3" ;;   # FIX-UP 3 (FIX-UP 2: 2)
        R|I0) echo "" ;;
        I1) echo "DOSAGS_SCALE2_NARROW=1" ;;
        *) echo "gate-2x: unknown arm $1" >&2; exit 2 ;;
    esac
}

# run_one DIR ARM PKG TICKS EXIT ; uses ROWCFG (files staged; NAME after ':'), ROWENV, ROWARGS
run_one() {
    local d="$1" arm="$2" pkg="$3" ticks="$4" ex="$5"
    local exe="$EXE"; [[ "$arm" == R ]] && exe="$PLAIN"
    local args=() e
    for e in "${ROWCFG[@]}"; do args+=(--include-extra "$e"); done
    for e in "${ROWENV[@]}" $(arm_env "$arm") "DOSAGS_FREEZE_TICKS=$ticks" "DOSAGS_TAS_AUTO_EXIT_TICK=$ex"; do args+=(--env "$e"); done
    for e in "${ROWARGS[@]}"; do args+=(--ags-arg "$e"); done
    rm -rf "$d"; mkdir -p "$d"
    printf '%s\n' "arm=$arm pkg=$pkg exe=$exe" "${args[@]}" > "$d/RUN-ARGS.txt"
    sha256sum "$exe" > "$d/EXE-SHA256.txt"
    ( cd "$HARNESS" && AGS_EXE="$exe" ./run-dosbox.sh "$pkg" --no-host-input --env DOSAGS_FIXED_TIMESTEP=0 --conf "$CONF" \
        "${args[@]}" --freeze-capture "$d" --timeout "${GATE_RUN_TIMEOUT:-3000}" ) > "$d/run.log" 2>&1
    echo $? > "$d/rc"
    local st=""; [[ -f "$d/stage" ]] && st="$(cat "$d/stage")"
    [[ -n "$st" && -d "$st" ]] || st="$(grep -o '/[^[:space:]"]*/dos-port-dosbox\.[A-Za-z0-9]*' "$d/run.log" | tail -1)"
    if [[ -n "$st" && -d "$st" ]]; then
        cp "$st/RUNMANI.LOG" "$st/STDOUT.TXT" "$d/" 2>/dev/null || true
    fi
    echo "$(date -u +%T) $(basename "$(dirname "$d")")/$arm rc=$(cat "$d/rc")" >> "$OUT/progress.txt"
}

# row LABEL PKG TICKS EXIT "ARMS" ; ROWCFG / ROWENV / ROWARGS set by the caller
row() {
    local label="$1" pkg="$2" ticks="$3" ex="$4" arms="$5" a
    [[ -z "$ROWS" || "$ROWS" == *" $label "* ]] || return 0
    mkdir -p "$OUT/$label"
    printf 'pkg=%s ticks=%s exit=%s arms=%s\n' "$pkg" "$ticks" "$ex" "$arms" > "$OUT/$label/ROW.txt"
    for a in $arms; do
        [[ -z "$ARMS_ONLY" || "$ARMS_ONLY" == *" $a "* ]] || continue
        run_one "$OUT/$label/$a" "$a" "$pkg" "$ticks" "$ex"
    done
}

if [[ $READ_ONLY -eq 0 ]]; then
    GAME_ARMS="A B F C1 C2 C2i V V2 R"   # FIX-UP 2: + C2i
    GT=5,20,100,300,500,700,900
    # the three gate scenes (ROUNDRV-2026-11-19/driveRV.sh s16 / s32 / s8), moved to the 640x480 2x rung, sound off
    ROWCFG=("$CFG640:ACSETUP.CFG"); ROWARGS=(--startr 3)
    ROWENV=(DOSAGS_MAX_SCALE=2 "$FB")
    row S16-2x 5days "$GT" 1000 "$GAME_ARMS"
    ROWENV=(DOSAGS_MAX_SCALE=2 "$FB" DOSAGS_FORCE_COLOR_DEPTH=32 SDL_DOS_PACK24=1)
    row S32P-2x 5days "$GT" 1000 "$GAME_ARMS"
    ROWARGS=(--startr 35); ROWENV=(DOSAGS_MAX_SCALE=2 "$FB" DOSAGS_MSGSKIP=1)
    row S8-2x trilbysnotes "$GT" 1000 "$GAME_ARMS"
    # FIX-UP 1 (1): the click row -- 12 engine clicks (patch 0247) at ticks 200, 250, ... 750; freezes just after each
    # of six clicks (+1) and mid-walk (+25)
    ROWARGS=(--startr 3); ROWENV=(DOSAGS_MAX_SCALE=2 "$FB" DOSAGS_TICKCLICKS=200,50,12)
    row CLK-2x 5days 5,20,201,225,301,325,451,475,601,625,751,775,900 1000 "$GAME_ARMS"
    # FIX-UP 1 (3): the 1x inertness pair on S16 (640x480 cfg, DOSAGS_MAX_SCALE=1: centred 1x, the alias rung)
    ROWARGS=(--startr 3); ROWENV=(DOSAGS_MAX_SCALE=1 "$FB")
    row S16-1x 5days "$GT" 1000 "I1 I0"
    # bench letterbox rows (320x200 -> 640x480 at y=40); gate-alias.sh's freeze ticks, no R arm
    ROWARGS=()
    for arm in walk anim12 full; do
        d="$OUT/_cfg/b8-$arm"; mkdir -p "$d"; cp "$CFG640B" "$d/ACSETUP.CFG"; cp "$FIX/$arm.cfg" "$d/BENCH.CFG"
        ROWCFG=("$d/ACSETUP.CFG" "$d/BENCH.CFG")
        sc=walk; [[ $arm == anim12 ]] && sc=anim; [[ $arm == full ]] && sc=full
        tk=100,300,500,700,900; [[ $arm == full ]] && tk=10,40,80,120,200
        ROWENV=(DOSAGS_MAX_SCALE=2 "$FB" "DOSAGS_SCENE=$sc")
        row "B8-2x-$arm" bench8 "$tk" 1500 "A B F C1 C2 V V2"
    done
    for arm in walk anim12; do
        d="$OUT/_cfg/b16-$arm"; mkdir -p "$d"; cp "$CFG640B" "$d/ACSETUP.CFG"; cp "$FIX/$arm.cfg" "$d/BENCH.CFG"
        ROWCFG=("$d/ACSETUP.CFG" "$d/BENCH.CFG")
        sc=walk; [[ $arm == anim12 ]] && sc=anim
        ROWENV=(DOSAGS_MAX_SCALE=2 "$FB" "DOSAGS_SCENE=$sc")
        row "B16-2x-$arm" bench16 100,300,500,700,900 1500 "A B F C1 C2 V V2"
    done
    echo "finished $(date -u +%FT%TZ)" >> "$OUT/BINARIES.txt"
fi
python3 "$HARNESS/gate-2x-read.py" "$OUT" ${ROWS:+--rows "$ROWS"} | tee "$OUT/VERDICT.txt"
exit "${PIPESTATUS[0]}"
