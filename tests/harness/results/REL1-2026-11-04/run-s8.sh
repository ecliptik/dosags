#!/usr/bin/env bash
# one DOSBox-X S8 cell (GL8 line, no host drive) on a given exe; copies results to $OUTROOT/$TAG-2026-11-04
set -u
TAG=$1; EXE=$2; OUTROOT=$3
cd ~/git/dosags
dir=$(AGS_EXE="$EXE" tests/harness/run-dosbox.sh trilbysnotes --timeout 1200 \
  --conf tests/harness/confs/dosbox-x-fixed40k-opl3.conf \
  --include-extra tests/harness/presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG \
  --env DOSAGS_LOG_TAG=$TAG --env DOS_PORT_LOG_TAG=$TAG --env DOSAGS_FIXED_TIMESTEP=1 \
  --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env DOSAGS_TAS_AUTO_EXIT_TICK=5000 --env DOSAGS_MSGSKIP=1 \
  --ags-arg --startr --ags-arg 35 --no-fine-timing --sb-live 2>"$OUTROOT/$TAG.err" | tail -1)
echo "stage=$dir"
mkdir -p "$OUTROOT/$TAG-2026-11-04"
cp -r "$dir"/. "$OUTROOT/$TAG-2026-11-04/" 2>/dev/null
ls "$OUTROOT/$TAG-2026-11-04" | head -30
