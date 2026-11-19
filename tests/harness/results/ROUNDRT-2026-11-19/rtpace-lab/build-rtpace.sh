#!/usr/bin/env bash
# round RT: rebuild the 0383 release (must reproduce c68241073cb0...), then 0383 + tests/harness/apply-pace-rig.py in the
# RELEASE flavour (RTPACE). Run only after sdlports' reply to FIX-UP 1.
set -eu
unset TMPDIR
ulimit -v 5000000
W=/home/claude/data/worktrees/dosags-ring; E=/home/claude/data/worktrees/dosags-lab-pace/build/move/exe
SP=/home/claude/data/tmp/claude-1001/-home-claude-git-dosags/8d15788e-024f-45ef-9590-8caefc025dbf/scratchpad/pa
cd $W
[ -z "$(git -C vendor/ags status --porcelain)" ] || { echo "vendor/ags dirty -- stop"; exit 1; }
restore() { git -C $W/vendor/ags checkout -q -- . && git -C $W/vendor/ags clean -fdq; echo "vendor clean: [$(git -C $W/vendor/ags status --porcelain | wc -l)]"; }
trap restore EXIT
make game DOSAGS_RELEASE=1 > $SP/build-rt-plain.log 2>&1
echo "plain release: $(sha256sum build/ags-release/ags.exe | cut -c1-64) (want c68241073cb0dbcc6f0870c22ba31a0d904dd2261e72a44fbb7ba75f6cfb7f43)"
python3 /home/claude/git/dosags/tests/harness/apply-pace-rig.py vendor/ags
git -C vendor/ags diff > $SP/rtpace-vendor.diff
make game DOSAGS_RELEASE=1 > $SP/build-rtpace.log 2>&1 || { grep -n " error:" $SP/build-rtpace.log | grep -v fat-lto | head -20 | cut -c1-240; exit 1; }
cp build/ags-release/ags.exe $E/RTPACE.EXE
echo "RTPACE: $(sha256sum $E/RTPACE.EXE | cut -c1-64) $(stat -c %s $E/RTPACE.EXE) bytes"
echo BUILD-DONE
