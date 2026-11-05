DUPCHAR4 -- NOT a real-hardware cell. Local DOSBox-X-only diagnostic,
2026-09-22. Question: is room 3's two-figure frame (S2F2, DUPCHAR2,
DUPCHAR3, local-diag-freeze-r3) an artifact of the --startr 3 debug jump?
Pre-registered in PLAN.md (commit f2f57a7) before either arm ran.

Build: build/ags/ags.exe = vendor/ags at export-0197 (e622baaa8) plus a
THROWAWAY, uncommitted diagnostic, kept here as diag4-throwaway.diff and
reverted after (vendor/ags clean at export-0197 again, build/ags/ags.exe
rebuilt without it). The diagnostic:
  - room load: logs the player's x, y, on, transparency, view, loop,
    frame, flags, prevroom and the load tick ("DOS-PORT-DIAG4 load")
  - every rendered tick in room 3: the same player fields plus Object 0's
    on/view/x/y, printed whenever any of them changes
  - DOSAGS_DIAG4_REL3=1: DOSAGS_FREEZE_TICKS counts from the room-3 load
    tick, so both arms freeze at the same room-relative ticks even though
    natural entry depends on when START was clicked

Both arms: --fixed-timestep, cfg/ACSETUP.CFG (= presentation/trilbysnotes/
ACSETUP-OFF-512X384-ROUND.CFG), mode line "512 x 384 (16-bit) fullscreen",
"DOS-PORT vscreen alias ON x=96 y=72 320x240 pitch=1024" in both,
DOSAGS_FREEZE_TICKS=20,100,200,300,343,361,421 (room-3-relative; the last
four are local-diag-freeze-r3's FRZ00-FRZ03 ticks).

startr/  -- ./run-dosbox.sh 5days ... --ags-arg --startr --ags-arg 3
           presentverify frames=668 stale_frames=0 stale_px=0
natural/ -- same, no --startr; the game's own flow: room 1 -> room 2
           (intro narration, then the START/LOAD/QUIT title) -> one click
           on START (xdotool, private Xvfb :211) -> room 99 (title card)
           -> room 3. Quit with Alt+X after the last freeze.
           presentverify frames=10319 stale_frames=0 stale_px=0

Player state at room-3 load (DIAG4 load lines, verbatim):
  startr : room=3 tick=0    char=0(cTrb) x=160 y=160 on=1 tr=0 view=8 loop=0 frame=0 flags=0xa0008 prevroom=3
  natural: room=3 tick=7526 char=0(cTrb) x=15  y=194 on=1 tr=0 view=8 loop=0 frame=0 flags=0xa0008 prevroom=99

At the Object-0 turn-off (both arms, same script, same tick +-1):
  startr : tick=352 rel=352 cTrb x=71 y=126 on=1 tr=0 view=8 | obj0 on=0 view=13
  natural: tick=7879 rel=353 cTrb x=71 y=126 on=1 tr=0 view=8 | obj0 on=0 view=13

Frames (sheet.png in each arm is the contact sheet, labelled):
  startr  FRZ00-02 (rel 20/100/200): one figure, cTrb at the desk
          (160,160), no climb yet -- the real-hardware "frame 9, one
          character at the desk" state.
  startr  FRZ03-04 (rel 300/343): TWO figures -- Object 0 climbing in at
          the window/bookshelf AND cTrb at the desk. Reproduces FRZ00 /
          camera 00010.
  startr  FRZ05-06 (rel 361/421): one figure at the bookshelf.
  natural FRZ00-02: empty room (no figure).
  natural FRZ03-04: ONE figure -- Object 0 climbing in. Nothing at the
          desk, nothing at (15,194).
  natural FRZ05-06: one figure at the bookshelf, identical to startr's.
  The hourglass at the bottom-left of every natural frame is the mouse
  cursor (the host pointer was left where START had been clicked).

Reading (fact): the only difference between the arms is where the player
waits during the climb-in -- the authored default 160,160 under --startr,
15,194 on natural entry (set before room 3 by the room 2 / room 99 flow,
which --startr skips; stock AGS --startr sets only playerchar->room,
game_start.cpp:210-211). The room-3 script then moves him to 71,126 at the
Object-0 turn-off in both arms. Prediction MET: natural entry shows one
figure during the climb-in, --startr shows two.

Not determined (hypothesis only): WHY the player is invisible at 15,194
(on=1, tr=0, view=8 there). Likely a walk-behind or out-of-room parking
spot in the game's own data; not investigated (no room-script/room-data
hunt, per the dispatch).
