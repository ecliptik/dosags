EXPORT1 -- patch-series export and its DOSBox-X correctness gate, 2026-09-21
============================================================================

What this is: raw evidence for PLAN.md work order step 1. No target time.

oracle.txt
    Tree hashes of the dirty vendor working state taken BEFORE any commit
    (temporary index + write-tree), against the tree produced by applying the
    exported series to a pristine pin with `git am --keep-cr`, and against the
    tree in vendor/ after the real `make patches`. All three are equal for
    both vendors. Also the series fingerprints and `make build-dirty`.

bench16-validate-all.json, bench8-validate-all.json
    `port_game.py validate --arm all` on DOSBox-X, clean binary
    binary_sha12 667514e4b97d. Per arm: RUNMANIFEST, every check, capture hash.
      idle walk anim4 anim12 text : PASS, hash == 2026-09-17 baseline (both depths)
      gui                          : FAIL, capture hash differs (both depths)
      full                         : FAIL, run ends 2 s in (both depths)

bisect/
    gui16_noinval  DOSAGS_GUI_NOINVAL=0 -> capture == baseline hash  (CAUSE)
    gui16_norunblit, gui16_nodirty      -> capture unchanged (1a16d9c2...), so
                                           not the run blit and not the present
    gui8_noinval   same, at 8-bit -> capture == baseline (3cbb692a...)
    full16_*       four variants (base, noinval, norunblit, nodirty): all end
                   at phase=restore begin; none of the switches changes it.

images/gui_off_vs_on.png
    Left: stage 1 off (== baseline). Right: stage 1 on (the default). The menu
    the fixture hid (FixedPose sets gMenu.Visible = false, then waits 40
    still ticks before SaveScreenShot) is still painted.
images/gui_diff.png
    Differing pixels: 7,559 of 64,000, bbox (100,40)-(220,112).

full-arm/
    AUTOPLT.LOG, STDOUT.TXT, B16FULL.LOG of a kept-stage `full` run. STDOUT.TXT
    shows, after "Restoring saved game", the script error
      Error: FileWriteRawLine: invalid file handle; file not previously opened
      or has been closed   (AutoPilot line 90, from WriteLog)
    Fixture commit 155ad57 (2026-09-20) holds the log handle open; a restore
    closes script file handles.

agsquest/
    tests/harness/run-dosbox.sh agsquest --fixed-timestep, parsed by
    parse-results.py: PASS all phases, PH01-PH03 hashes all "match", same
    binary_sha12. The standing gate is GREEN while the gui defect exists: its
    three capture moments do not expose it.
