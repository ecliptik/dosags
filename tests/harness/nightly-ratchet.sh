#!/usr/bin/env bash
# nightly-ratchet.sh -- run dosags' tests/ratchet.yaml unattended, on a clean build of origin/main, in a
# worktree of its own. For cron (nightly; weekly with --controls). LAB ONLY: DOSBox-X, never hardware.
#
#   tests/harness/nightly-ratchet.sh [--controls] [--setup]
#
#   --controls   also run every check's control (weekly: a pass takes hours)
#   --setup      create the worktree ($DOSAGS_NIGHTLY_ROOT) if it does not exist yet (first run only;
#                without it a missing worktree is an error, so a typo never creates trees)
#
# Environment (defaults in brackets):
#   DOSAGS_NIGHTLY_ROOT     the dedicated worktree [~/git/dosags-nightly]. Never the main worker's
#                           ~/git/dosags or a lab tree: the ratchet builds, resets and cleans it.
#   DOSAGS_REPO             the repository the worktree belongs to (setup only) [~/git/dosags]
#   DOSAGS_GAME_DATA        where the game packages live (gitignored; not in any checkout)
#                           [~/git/dosags/tests/harness/games]; each package the runs need is SYMLINKED
#                           into the worktree's tests/harness/games/ (read-only use; nothing is copied)
#   DOSAGS_VENDOR_SEED      an existing checkout whose vendor/SDL, vendor/ags (and vendor/cwsdpmi) are copied
#                           instead of cloning upstream [unset: scripts/fetch-sources.sh]
#   DOSAGS_NIGHTLY_DISPLAY  the Xvfb display number for capture units [271] -- not a worker's (211 main,
#                           221/231/241/261 labs)
#
# Each run: guards -> fetch -> detached checkout of origin/main (reset --hard; untracked files removed,
# gitignored vendor/ build/ games/ kept) -> game data links -> apply the patch series to clean vendor
# trees -> make all -> ratchet.sh --root <worktree> --no-build. Every step is logged to
# <worktree>/build/ratchet/nightly-<utc>.log; the ratchet writes its own build/ratchet/<run-id>/ as ever.
#
# GUARDS (skip cleanly, logged, exit 2 = "nothing failed, something blocked", as ratchet.sh):
#   - a hardware round is running (a run-hw.sh process exists): the nightly waits for no one;
#   - the ratchet lock (/tmp/sdl-dos-ports-ratchet.lock) is held (another ratchet run).
# EXIT: ratchet.sh's code (0 pass, 1 fail, 2 blocked/interrupted, 3 could not run); 1 also for a failed
# fetch, apply or build; 2 for a skip.
#
# The script copies itself to a temporary file and re-executes from there first, because the checkout
# step rewrites the file it was started from.
set -u

if [[ -z "${NIGHTLY_REEXEC:-}" ]]; then
    tmp="$(mktemp /tmp/nightly-ratchet.XXXXXX.sh)"
    cp "$0" "$tmp" && chmod +x "$tmp"
    NIGHTLY_REEXEC="$tmp" exec bash "$tmp" "$@"
fi
trap 'rm -f "$NIGHTLY_REEXEC"' EXIT

NIGHTLY="${DOSAGS_NIGHTLY_ROOT:-$HOME/git/dosags-nightly}"
REPO="${DOSAGS_REPO:-$HOME/git/dosags}"
DATA="${DOSAGS_GAME_DATA:-$HOME/git/dosags/tests/harness/games}"
SEED="${DOSAGS_VENDOR_SEED:-}"
DISP="${DOSAGS_NIGHTLY_DISPLAY:-271}"
CONTROLS=0; SETUP=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --controls) CONTROLS=1; shift ;;
        --setup) SETUP=1; shift ;;
        *) echo "usage: $0 [--controls] [--setup]" >&2; exit 3 ;;
    esac
done
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
LOGDIR="$NIGHTLY/build/ratchet"
LOG="$LOGDIR/nightly-$STAMP.log"
if [[ -d "$NIGHTLY" ]]; then mkdir -p "$LOGDIR"; else LOG="/tmp/dosags-nightly-$STAMP.log"; fi
log() { printf '%s %s\n' "$(date -u +%H:%M:%SZ)" "$*" | tee -a "$LOG"; }
die() { log "FAIL: $*"; exit "${2:-1}"; }

log "nightly-ratchet start: root=$NIGHTLY controls=$CONTROLS display=:$DISP"

# ---- guards
if pgrep -f '(^|/)run-hw\.sh( |$)' >/dev/null 2>&1; then
    log "SKIP: a hardware round is running (run-hw.sh: $(pgrep -f '(^|/)run-hw\.sh( |$)' | tr '\n' ' '))"; exit 2
fi
exec 9>>/tmp/sdl-dos-ports-ratchet.lock
if ! flock -n 9; then log "SKIP: the ratchet lock is held (another ratchet run)"; exit 2; fi
flock -u 9; exec 9>&-

# ---- worktree
if [[ ! -d "$NIGHTLY" ]]; then
    [[ $SETUP -eq 1 ]] || die "$NIGHTLY does not exist (run once with --setup)" 3
    git -C "$REPO" fetch -q origin || die "fetch in $REPO"
    git -C "$REPO" worktree add --detach "$NIGHTLY" origin/main >>"$LOG" 2>&1 || die "worktree add"
    mkdir -p "$LOGDIR"; cat "$LOG" >> "$LOGDIR/nightly-$STAMP.log"; LOG="$LOGDIR/nightly-$STAMP.log"
fi
cd "$NIGHTLY" || die "cd $NIGHTLY"
[[ "$(git rev-parse --show-toplevel 2>/dev/null)" == "$NIGHTLY" ]] || die "$NIGHTLY is not a worktree root" 3
case "$NIGHTLY" in "$HOME/git/dosags"|"$HOME/git/dosags-lab-"*) die "refusing to run in $NIGHTLY (a worker's tree)" 3 ;; esac
git fetch -q origin || die "git fetch"
git checkout -q --detach origin/main || die "checkout origin/main"
git reset -q --hard origin/main || die "reset"
git clean -q -fd || die "clean"
log "tree: $(git log -1 --format='%h %s' | cut -c1-100)"

# ---- toolchain link, vendor trees, game data
[[ -e tools/djgpp ]] || ./scripts/setup-symlinks.sh >>"$LOG" 2>&1 || die "setup-symlinks"
for v in SDL ags; do
    if [[ ! -d "vendor/$v/.git" ]]; then
        if [[ -n "$SEED" && -d "$SEED/vendor/$v/.git" ]]; then
            log "vendor/$v: copying from $SEED"; cp -a "$SEED/vendor/$v" "vendor/$v" || die "copy vendor/$v"
        else
            log "vendor/$v: fetching"; ./scripts/fetch-sources.sh >>"$LOG" 2>&1 || die "fetch-sources"
        fi
    fi
done
# CWSDPMI is staged by hand in every checkout (gitignored, no manifest; see .gitignore), and every
# DOSBox-X cell refuses to start without it (run-dosbox.sh: "vendor/cwsdpmi/cwsdpmi.exe not found").
# Without this step the first nightly ran every unit, each failing in 1-2 s, and reported 35 ERRORs.
if [[ ! -f vendor/cwsdpmi/cwsdpmi.exe ]]; then
    for src in "$SEED" "$REPO"; do
        if [[ -n "$src" && -f "$src/vendor/cwsdpmi/cwsdpmi.exe" ]]; then
            mkdir -p vendor/cwsdpmi && cp -a "$src/vendor/cwsdpmi/." vendor/cwsdpmi/ || die "copy vendor/cwsdpmi"
            log "vendor/cwsdpmi: copied from $src"; break
        fi
    done
    [[ -f vendor/cwsdpmi/cwsdpmi.exe ]] || die "vendor/cwsdpmi/cwsdpmi.exe missing (stage it, or set DOSAGS_VENDOR_SEED)" 3
fi
mkdir -p tests/harness/games
for pkg in agsquest 5days bench8 bench16 shards trilbysnotes; do
    [[ -e "tests/harness/games/$pkg" ]] && continue
    if [[ -d "$DATA/$pkg" ]]; then ln -s "$DATA/$pkg" "tests/harness/games/$pkg"; log "games/$pkg -> $DATA/$pkg"
    else log "WARN: no game data for $pkg under $DATA (checks that need it will ERROR)"; fi
done

# ---- clean series, build
./scripts/apply-patches.sh >>"$LOG" 2>&1 || die "apply-patches (a dirty vendor tree is refused, never reset)"
make -s verify-patches-applied >>"$LOG" 2>&1 || die "verify-patches-applied"
timeout 2400 make -j8 all >>"$LOG" 2>&1 || die "build"
log "build: $(make -s build-dirty build-sha12 2>/dev/null | tr '\n' ' ')"

# ---- the ratchet
A=(--root "$NIGHTLY" --no-build --no-host-wait --busy-wait 14400 --capture-display "$DISP")
[[ $CONTROLS -eq 1 ]] && A+=(--controls)
export DOSBOX_DISPLAY_NUM="$DISP"
.sdl-dos-ports/shared/tools/ratchet.sh "${A[@]}" >>"$LOG" 2>&1
rc=$?
# ---- quarantine streaks (coordinator 2026-09-24): a quarantined check leaves quarantine after 10
# consecutive clean runs; the count is taken from ratchet.sh's own history (build/ratchet/state.tsv,
# one line per check per run) -- trailing PASS/IMPROVED results, reset by anything else -- and
# appended to this run's report.
for q in screen-agsquest-alias-y60-fixed40k; do
    streak="$(awk -F'\t' -v c="$q" '$3 == c { s = ($4 ~ /^(PASS|IMPROVED)/) ? s + 1 : 0 } END { print s + 0 }' build/ratchet/state.tsv 2>/dev/null)"
    line="QUARANTINE STREAK $q: ${streak:-0} consecutive clean run(s) (leaves quarantine at 10)"
    echo "$line" >> build/ratchet/latest/ratchet-report.txt 2>/dev/null
    log "$line"
done
log "ratchet exit $rc: $(cat build/ratchet/latest/ratchet-summary.txt 2>/dev/null)"
log "report: $(readlink -f build/ratchet/latest)/ratchet-report.txt"
exit $rc
