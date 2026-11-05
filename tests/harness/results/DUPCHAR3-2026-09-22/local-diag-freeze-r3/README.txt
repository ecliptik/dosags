local-diag-freeze-r3 -- NOT a real-hardware cell. Local DOSBox-X-only
diagnostic, run after DUPCHAR3's real-hardware collection, to check the
leading Character-side-gap hypothesis for the duplicate sighting without
spending another real-hardware round (per the coordinator's "no further
hardware round until source-grounded" instruction, 2026-09-22).

Build: build/ags/ags.exe, vendor/ags on top of export-0197
(e622baaa8) plus one throwaway, uncommitted diagnostic line in
Engine/ac/room.cpp (a debug_script_log of thisroom.Options.PlayerCharOff
at load_new_room's player-character branch -- reverted after this run,
never part of any patch).

Command:
  ./run-dosbox.sh 5days --fixed-timestep --timeout 180 \
    --env DOSAGS_TAS_AUTO_EXIT_TICK=500 \
    --ags-arg --startr --ags-arg 3 \
    --freeze-capture <dir> --env DOSAGS_FREEZE_TICKS=300,340,360,420

Result: DOS-PORT presentverify frames=286 stale_frames=0 stale_px=0
stale_px_max=0 -- zero stale pixels for the whole run (this engine's own
narrowed-present correctness verifier, ags patch 0192).

FRZ00 (tick=300) and FRZ01 (tick=343): TWO identical gray-suited figures
on screen at once -- one by the bookshelf, one at the desk. Same
signature as every real-hardware sighting (S2F2, DUPCHAR2, DUPCHAR3).

FRZ02 (tick=361, right after STDOUT.TXT's "Object 0 turned off" /
"Object 0 stop moving"): ONE figure remains (bookshelf). The desk area is
cleanly restored -- no ghost, matching the stale_px=0 verifier result.

FRZ03 (tick=421): same single figure, now with "And the gentleman thief
makes his entrance." on screen.

Reading: this is consistent with the two-figure moment being the game's
own scripted entrance (Object 0 plays a stand-in walk-in animation at the
desk while Character cTrb, never hidden -- PlayerCharOff=0, confirmed by
the diagnostic line above -- already waits at the bookshelf), not a
stale/unflushed sprite. Object 0's own turn-off is clean (zero stale
pixels), consistent with patch 0197 doing its job correctly on an event
that was never the cause of the visible "duplicate." See PLAN.md's
DUPCHAR3 write-up for the full account and the open question this does
not settle (whether this is intentional game direction -- needs the
operator's own reference knowledge, not something this engine trace can
decide by itself).
