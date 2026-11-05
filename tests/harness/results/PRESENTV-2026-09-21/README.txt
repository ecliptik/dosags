PRESENTV -- the present-narrowing defect, found and bracketed on DOSBox-X (no hardware), 2026-09-21.

Instrument: ags 0192 DOSAGS_PRESENT_VERIFY (a shadow of what was pushed to the screen; counts pixels
where the engine's frame differs from it). Method: AGS Quest AutoPilot demo, 640x480x16 1:1, alias ON.

matrix/            one presentverify summary per variant (stale_frames / frames, stale_px, max):
  V0 default 3100/3565 31.8M 29,917   V1 DOSAGS_DIRTY_PRESENT=0 0/3858   V2 DIRTY_BOXES=1 2693/3825
  V3 RUNBLIT=0 3015/3480   V4 GUI_NOINVAL=0 2889/3312   V5 direct-fb off 3035/3497 (uninformative: the
  verifier models rects, not the backend). latch-experiment-E1/E2: invalidate_all_* latching the present
  full moved first_stale from frame 14 to 149 and cut stale px 31.8M -> 10.1M (diff kept, NOT committed
  as a patch). E2's STALE lines print the pushed-rect list beside the stale bbox.
screen-series-V1/  screen-level series of V1 (narrowing off) by run-dosbox.sh --screen-series: CLEAN at
                   every walking and speech moment, so RAM is correct and the defect is the pushed rects.
screen-series-V0-adhoc/  the same demo with narrowing on (ad hoc capture): chains of character copies,
                   speech fragments, garbled boxes.
mode13h/           BENCH8 at the native 320x200 rung, alias ON: anim12 503 frames, 1 stale (the last, the
                   FixedPose teleport); walk stale from frame 2 (247 px).
The 2x rung is not on the path: G2R1's own log at 640x480 says narrow=0 full=1500 rej scaled=1500.
