# PREREG-2X -- narrowed integer-2x present (SCALE2-NARROW) (2026-11-19)

Status: WRITTEN, NOT RUN. Nothing below has been built or run. Every step waits for the reviewer (sdlports, via the
lead).
Considered alternative (an abandoned parallel draft, kept in SCRATCH/2x-twox-abandoned/, not merged): defer the blit
until after the 0124 block and reuse 0124's own box code with a scale factor, so the blit and the push share one rect
list by construction. This design instead builds its own clamped box list before the unchanged-frame check and feeds
the same list to both, so the 0124 block's 1x code stays untouched.

SCRATCH = /home/claude/data/tmp/claude-1001/-home-claude-git-dosags/8d15788e-024f-45ef-9590-8caefc025dbf/scratchpad
Files: tests/harness/apply-2x.py (the overlay, uncommitted); SCRATCH/2x/apply-2x.diff (dry run on a copy of
dosags-ring's vendor/ags, ags 0383, d47c5b982; 2 files, +371 -4). Re-verified on a fresh copy: the diff body is
byte-identical (only the mtime stamps in the ---/+++ headers differ); the scratch trees were deleted. Scope: SCRATCH/scope-2x/SCOPE-2X.md.

## 1. What the overlay does (summary; the full contract is the script's docstring)

Switch: DOSAGS_SCALE2_NARROW=1 (exactly "1"). Default OFF.
At an exact uniform 2x frame (dst = 2 x vscreen), a present with the latch armed, the scene path, no full latch and a
valid dirty set does two things:
- it scale-blits only the dirty boxes. The boxes are in game coordinates, clamped to the GAME size, and land at
  (dst.x + 2*x1, dst.y + 2*y1, 2w, 2h);
- it pushes exactly those rects.
Those presents skip 0091/0102's unchanged-frame check. Every other 2x present stays a full blit plus a full push,
through a new dword-store replicator. Unset, the present path is unchanged and no log line is added.

Code sites (Engine/gfx/ali3dsw.cpp, line numbers at 0383):
- after dos_guiclip_summary (~135): switches, counters, latch, exit line (global scope);
- SetDisplayMode (228), CreateVirtualScreen (~419): the latch is dropped;
- before TryFastIntegerNearestBlit (1261): dos_s2_blit_rect, dos_s2_boxes, dos_s2_blit_boxes, dos_s2_verify;
- TryFast (after 1356): the full 2x path through the replicator when the switch is on;
- Present() before 0102's frame_bytes_for_skip (1811): the decision, plus 0193's merge moved ahead (2x presents only);
  clean_case gains !_s2_narrow;
- the blit site (1951): the box blit instead of TryFast on narrowed presents; 0230's BlitScBytes counts box bytes;
- after the blit (before 1977): latch set/drop and the optional verifier;
- the 0124 block: no second merge, no rej_scaled on a narrowed present, and the doubled rects go into _dp_rects /
  _dp_nrects / _dp_narrowed, so the existing push and 0230 PushBytes code pushes and counts them unchanged.
Engine/main/quit.cpp: the exit line after dos_char_reuse_summary (both flavours), and 3 allowlist entries.

Exit line (RUNMANI.LOG, only when the switch is on):
  DOS-PORT scale2 on=1 break= verify= narrow= full= fullfast= pal= rects= px_src= skipcheck= rej geom= hint= fmt=
  nolatch= noscene= latched= norects= whole= latch_sets= latch_drops= vfy= vfy_bad= vfy_bad_px= vfy_first=
Diagnostics: DOSAGS_SCALE2_VERIFY=1 runs a whole-frame window == scale2(vscreen) check after every 2x present that
leaves the latch armed; it logs "DOS-PORT scale2verify BAD ...". DOSAGS_SCALE2_BREAK=1 is a control: each narrowed box is
blitted one source column and row short, and pushed whole.

## 2. Dry-run review (done, from the diff)

- Rect rounding: none to do. Exact 2x maps every window px to exactly one source px. Push rect = 2 x (clamped game box),
  always even x/y/w/h relative to dst, and equal to the blitted rect (the push is built from the same _s2_box[]).
- Clamping: to vscreen w-1 / h-1 (game size), not dst.w-1 (0131's 1x clamps would let x reach 639 at 2x). A box wholly
  off-screen is dropped. The set is used when its clamped area is under the game area, else the bbox when smaller,
  else full. More permissive than 1x for an UNBORDERED frame, which narrows on the bbox alone; 1x already uses the set
  on bordered frames. Coverage is the same, since the boxes cover every add.
- Letterbox offsets: dst.x/dst.y are added once, in the push rects and in the blit base pointer
  (dp = win + dst.y*pitch + dst.x*bpp). A narrowed present requires margins_clean (0100) and dst_inside.
- Stride: source rows by src->pitch; output rows 2(y+j) and 2(y+j)+1 by win->pitch. 8 bit: a 2-byte head store when
  d0 is 2 mod 4, then a 4-px loop with one dword load and four dword stores, then a 16-bit tail; 16 bit: p|p<<16;
  32 bit: 4 stores. Byte order checked by hand: q = a|b<<8|c<<16|d<<24 -> v0 bytes a,a,b,b and v1 bytes c,c,d,d.
  may_alias typedefs avoid strict-aliasing miscompiles. Unaligned access is legal on x86, just slower.
- bpp: 1/2/4 only, formats equal (INDEX8 / RGB565 / XRGB8888). Anything else is rej_fmt and keeps today's path.
  32 bit + SDL_DOS_PACK24=1: the window surface is XRGB8888 and dos_pack24_push (SDL_dosframebuffer.c:1824-1872)
  clips and packs each pushed rect. It has no alignment requirement, so no SDL change.
- Palette (8 bit): SyncPaletteIfNeeded runs before the decision. SDL programs the DAC by palette version on any flush,
  whatever the rect list (SDL_dosframebuffer.c ~2113-2132, direct-FB branch). A narrowed present invalidates the 0091
  cache (clean_case false -> _lastPresentedValid = false), so a palette-only present can only follow a full present
  that refreshed the cache. Fades with no scene path keep the check and 0104.
- Cursor: AGS draws it into the vscreen and marks it (draw.cpp:4101, kDirtySrc_Cursor). SDL's direct-FB path
  composites none. The normal path composites and restores it.
- 0193 carry: merged ahead of the check on 2x presents. If the present is then skipped as unchanged (only possible on a
  present that does not narrow), the merged boxes stay in box[] because the frame reset does not run. They are pushed
  at the next present: the same union as today, merged into box[] earlier. The 0368 GUI clip reads box[] U carry_box[]
  and so sees the same union. Switch-on only.
- The latch is keyed on window surface + pixels + size + pitch, vscreen surface + pixels + size, and dst. It is armed
  only by the new full replicator from _vscreenSurface with no flip, and dropped by any other write (generic blit,
  flip scratch, 1x, other geometry), by a failed box blit, by SetDisplayMode and by CreateVirtualScreen. Screen shake
  moves dst, so presents go full until it is re-armed.
- Off-path identity: switch unset, the code differs only by the inert tests listed in the docstring. TryFast's old
  branches, the 0124 block's order, and 0091/0104 are all reached exactly as today.
- ASCII: the script asserts it; the diff is ASCII. A second application refuses (first anchor count 0).

## 3. Phase 2, step 1: the build (release flavour, dosags-ring, restore after)

Same pattern as SCRATCH/pa/build-rtpace.sh. Outputs go to SCRATCH/2x/exe/ (under /home/claude/data).

    set -eu; unset TMPDIR; ulimit -v 5000000
    W=/home/claude/data/worktrees/dosags-ring; SP=SCRATCH/2x; mkdir -p $SP/exe
    cd $W; [ -z "$(git -C vendor/ags status --porcelain)" ] || { echo dirty; exit 1; }
    restore() { git -C $W/vendor/ags checkout -q -- . && git -C $W/vendor/ags clean -fdq; }; trap restore EXIT
    make game DOSAGS_RELEASE=1 > $SP/build-plain.log 2>&1        # must reproduce c68241073cb0... (RT's 0383 release)
    python3 -I /home/claude/git/dosags/tests/harness/apply-2x.py vendor/ags
    git -C vendor/ags diff > $SP/vendor.diff                      # must equal apply-2x.diff's hunks
    make game DOSAGS_RELEASE=1 > $SP/build-s2.log 2>&1
    cp build/ags-release/ags.exe $SP/exe/S2NR.EXE; sha256sum $SP/exe/S2NR.EXE
    # optional, for dirtypresent cross-checks: the instrumented flavour (make game) -> $SP/exe/S2NI.EXE

Build VOID: the plain rebuild does not reproduce c68241073cb0; vendor.diff differs from the dry run; any compiler
warning in the new code (grep the log for ali3dsw.cpp warnings); vendor/ags not clean afterwards.

## 4. Phase 2, step 2: DOSBox-X screen-equality gate (no hardware)

gate-alias.sh's row() hard-codes A/B/C, so phase 2 needs a small driver, SCRATCH/2x/gate-2x.sh. It has the same
structure and calls tests/harness/run-dosbox.sh ... --freeze-capture DIR and tests/harness/screen-equal.py A B
--min N. Mode, as the AQ row (fixed, deterministic):
- --conf tools/dosbox-x.conf (fixed 40000 cycles);
- --env DOSAGS_FIXED_TIMESTEP=0 (said explicitly; the release flavour defaults it on);
- a row is VOID if any run reports frames_skipped > 0.
AGS_EXE = S2NR.EXE in every arm. The B reference is the same exe with the switch unset, i.e. today's code path.
Sound off in every row (the AQ precedent: audio timing can move script state).

Arms (each row):

    A   DOSAGS_SCALE2_NARROW=1                                  the run under test
    B   (switch unset) DOSAGS_DIRTY_PRESENT=0                   REFERENCE: today's full 2x (old TryFast, full push)
    F   DOSAGS_SCALE2_NARROW=1 DOSAGS_DIRTY_PRESENT=0           the new full replicator only (every present full)
    C1  DOSAGS_SCALE2_NARROW=1 DOSAGS_BREAK_0193=1              control: 0193 off, must DIFFER from B
    C2  DOSAGS_SCALE2_NARROW=1 DOSAGS_SCALE2_BREAK=1            control: narrowed blit 1 px short, must DIFFER from B
    V   DOSAGS_SCALE2_NARROW=1 DOSAGS_SCALE2_VERIFY=1           counters only (also compared to B, information)
    V2  DOSAGS_SCALE2_NARROW=1 DOSAGS_SCALE2_VERIFY=1 DOSAGS_SCALE2_BREAK=1   the verifier's own control

Common to every row: DOSAGS_MAX_SCALE=2, SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 (as the RV lines),
DOSAGS_FREEZE_TICKS=<ticks>, DOSAGS_TAS_AUTO_EXIT_TICK=<exit>.

Rows (scene lines from ROUNDRV-2026-11-19/driveRV.sh s16/s32/s8, moved to the 640x480 2x rung; cfg
tests/harness/presentation/trilbysnotes/ACSETUP-OFF-640X480.CFG staged as ACSETUP.CFG, which is full_window + round,
sound off):

    S16-2x   5days        --ags-arg --startr --ags-arg 3                                ticks 5,20,100,300,500,700,900  exit 1000
    S32P-2x  5days        --ags-arg --startr --ags-arg 3 DOSAGS_FORCE_COLOR_DEPTH=32
                          SDL_DOS_PACK24=1                                              same ticks
    S8-2x    trilbysnotes --ags-arg --startr --ags-arg 35 DOSAGS_MSGSKIP=1              same ticks
    B8-2x    bench8  arms walk, anim12, full   (320x200 -> 640x480 at y=40: the letterbox / margins case)
                                                                                         gate-alias TICKS, exit 1500
    B16-2x   bench16 arms walk, anim12         (16-bit letterbox)                       same

Ticks 5 and 20 sit on room entry (the fade-in and the first narrowed presents after the latch arms). There is no
fade fixture; the room-entry fade is the only fade coverage, and that is a stated gap. bench "walk" is the edge row
for the clamp, the best available.
--min 5 for game rows and 3 for bench rows, as gate-alias.sh.
Budget: 5 game rows x 7 arms + ~5 bench rows x 7 arms = ~70 runs; about 3-4 h of exclusive DOSBox-X lock at
gate-alias rates. The bench rows could drop to A/B/F/C2 if the lock is busy.

Witness per run (VOID if missed):
- render dest in the engine log: (0, 0, 639, 479 : 640 x 480) for the game rows, (0, 40, 639, 439 : 640 x 400) for
  the bench rows;
- the scale2 line PRESENT with on=1 in A/F/C1/C2/V/V2, and ABSENT in B (B is the switch-off path);
- S32P: the log shows the pack24 mode (24-bpp mode offered as XRGB8888). If DOSBox-X does not offer 640x480x24, the
  S32P row is VOID (not FAIL) and moves to the 486 step;
- frozen ticks equal pairwise (screen-equal.py voids otherwise).

Pass (the gate):
- every A == B pair, pixel for pixel, at every freeze tick in every row;
- every F == B pair (the full replicator is exact);
- V: vfy > 0 and vfy_bad = 0;
- C2 differs from B in at least every game row, and V2 shows vfy_bad > 0 (both controls have power);
- C1 differs from B in at least one row;
- exit codes as gate-alias.sh: 1 on any A/F mismatch or VOID, 3 if no control failed.

Predicted counters (A arms, 1000-tick game rows; from SCOPE-2X sec. 4 and the GL/RV readings):
- rej geom = 0 after the first present. Any early presents before the 640x480 frame is set count here, as
  information.
- full: 3-12 a run (first present nolatch=1, room entry noscene, latched 3-5 per 5000 ticks scaled down).
- narrow / (narrow + full) >= 95%.
- latch_sets = fullfast on the game rows. latch_drops <= 1 (no shake, no flip in these scenes).
- skipcheck = narrow at S8 (76,800-byte frame), 0 at S16 and S32P (153,600 / 307,200 B > 100,000).
- px_src / narrow: S8 ~2,200 (band 500-6,000); S16 ~1,300 (300-4,000); S32P 400-1,400 (100-4,000). These are
  DOSBox-X with no input, so they may sit low, and that is information.
- rects / narrow: S8 ~3.8, S16/S32P ~2.1 (band 1-8).
- F arms: narrow = 0, rej hint = every 2x present, fullfast = full.
- B arm: no scale2 line. 8-bit presents_skipped > 0 as today.

What falsifies the design (any one): an A != B pair; an F != B pair; vfy_bad > 0 in V; narrow = 0 in an A arm with
the latch armed (latch_sets > 0). Path not engaged = VOID, and the reason counters say why.

## 5. Phase 3 sketch (NOT pre-registered for running): the 486 A/B, 1x vs narrowed 2x

Only after the gate passes, with the operator's approval, in one power-on. Instrumented flavour (S2NI) in BOTH arms so
dirtypresent and the work vector print. Built from the same overlay, so the 1x arm runs the switch-off path.

- Scenes: the RV lines. S16 = 5days room 3. S32P = 5days room 3 + FORCE_COLOR_DEPTH=32 + SDL_DOS_PACK24=1.
  S8 = trilbysnotes room 35 + DOSAGS_MSGSKIP=1. All with $FB, TAS_AUTO_EXIT_TICK=5000, sound on.
- Arm A: today's gate line. MAX_SCALE=1; ACSETUP-ON-512X384-ROUND.CFG for S8/S16, S32P-ACSETUP-ON.CFG for S32P.
- Arm B: S32P-ACSETUP-ON.CFG (640x480, sound on; confirm game_scale_fs = round before staging) + DOSAGS_MAX_SCALE=2 +
  DOSAGS_SCALE2_NARROW=1.
- Order: warm-up, then A B B A per scene, 12 cells (~45-55 min of a 120-min cap). Budget line as the RV README.
- Witness: B is at 640x480, so the capture stick can lock (it needs its physical fix first, per the RV round);
  camera in both arms.
- Predictions, B against A (SCOPE-2X sec. 5, step 2, with the rewritten scaler):
  - S8: steady 40.0-40.3, fps_p50 40.00, displayed A - (0.3..1.5) pp, whole-run A - (0.05..0.2);
  - S16: steady 40.0-40.3, fps_p50 40.00, displayed A - (0.3..1.5) pp, whole-run A - (0.05..0.35);
  - S32P: steady 40.0-40.3, fps_p50 40.00, displayed A - (0.3..2.5) pp, whole-run A - (0.05..0.5);
  - B push bytes per present 3-5x A's at 8/16 bit;
  - against today's 2x anchor C364044 (26.99%, 9.78): B displayed >= 97%, fps_p50 40;
  - a full present at 2x on the rewritten path: 20-28 ms at 8 bit, 40-55 ms at 16, 75-140 ms at 32 pack24 [m]. The
    present_blit max in B reads it.
- Falsifies the model (any one):
  - B fps_p50 < 40 or steady < 40.0;
  - B displayed < 95%;
  - a per-call present cost outside the [m] range by > 2x;
  - B's scale2 line with narrow < 95% of 2x presents, or no line (VOID as a test of the design);
  - any witness defect (a trail, a stale cursor, border garbage).
- Bar: a 2x claim needs a new registration with the bar's rung clause changed, and that is the operator's call.
  Proof stays the registered pair.
- Known whole-run risk: 15-17 full presents a run at +20..+140 ms each, against margins of 0.42 / 0.65 / 0.58 s
  (RV8A/RV16A/RV32A). S32P is the likeliest to miss whole-run.

## 6. Step 0 (option for the operator; not run, not proposed for this phase)

A 1x render-delay probe on the 486, no new code. DOSAGS_MI_RENDER_DELAY_MS=N (ags 0251, draw.cpp:1610-1625: SDL_Delay
per rendered frame, both flavours) on the RV lines at N = 2 and N = 4, on S16 and S32P (S8 if the cap allows), 4-6
cells. It reads displayed% and whole-run against N.
- Rule: if N = 2 already takes displayed under 99.0% at a depth, the narrowed 2x cannot meet the 99% line there
  without offsetting savings. Re-scope before step 5.
- Caveat: the delay is flat, while the real cost grows with dirty area, so step 0 understates it.
- Witness gap: DOSAGS_MI_RENDER_DELAY_MS is NOT in the RUNMANIFEST env allowlist (quit.cpp:395-436), so the env hash
  cannot tell these cells apart. Witness it by the runner's per-cell env record (set/forbid), or add it to the
  allowlist in the probe build.

## 7. Open risks

1. Whole-run at 16/32 bit from the full 2x presents (SCOPE sec. 6, risk 1). The replicator removes the row buffer and
   memcpy, but the RAM write (4x the source bytes) and the full push stay. Alternative B (scale in the SDL push) is a
   hub change.
2. Correctness is seen only by screen-equality and the new verifier. The 0192 verifier is vacuous on this path.
3. Moving 0193's merge ahead of the check on 2x presents (switch on) is a reorder inside one Present. Reviewed equal
   above (same union), but the gate is the evidence.
4. The 8-bit 4-px loop does a 4-byte source read, which never runs past the row (n >= 4). Unaligned on the 486 costs
   cycles, not correctness.
5. The box cap tuned at 1x (8) may be wrong at 2x. Sweep DOSAGS_DIRTY_BOXES = 8/12/16 on DOSBox-X counters before the
   486.
6. The latch relies on nothing else writing the window surface between presents at 2x. True today: alias is 1x only,
   and SDL restores its cursor composite. A future change there must drop the latch.
7. The hub docs/video.md "never scale to fill" would need a dated amendment by PR if this ships. Not here.

## FIX-UP 1 (2026-11-19, the reviewer's three additions; written before any build or cell)

Written after sdlports accepted phase 1 (ce735153). Nothing is built or run until this section is committed. It adds
three things to sec. 4 and corrects sec. 4's run count. Everything else in sec. 4-7 stands unchanged, including:
- the fade gap (no fade fixture; the room-entry fade is the only fade coverage);
- the box-cap sweep (DOSAGS_DIRTY_BOXES 8/12/16), which stays information;
- phase 3, which stays a sketch only.

### F1.0 The gate driver and its reader (committed with this section, before any cell)

- tests/harness/gate-2x.sh runs every row and arm below with gate-alias.sh's machinery: run-dosbox.sh
  --freeze-capture, then screen-equal.py.
  - Mode: fixed 40000 cycles (tools/dosbox-x.conf), DOSAGS_FIXED_TIMESTEP=0, --no-host-input.
  - It copies each run's RUNMANI.LOG and STDOUT.TXT out of the stage at once (stage GC).
  - It records each arm's exe sha256 and refuses a --plain exe that is not c68241073cb0... .
  - It ends by calling the reader.
- tests/harness/gate-2x-read.py OUT is post-hoc and can be re-run on OUT alone. It prints PASS / FAIL / VOID / MISSING /
  INFO per row and check.
  - Exit 0: every registered check passed.
  - Exit 1: any FAIL, VOID or MISSING.
  - Exit 3: otherwise, but a control without power.
  - Its docstring lists the registered checks. They are the checks of sec. 4 plus F1.1-F1.3.
  - Checked once on synthetic run dirs (no emulator): parsing, the pair logic, control power and the 1x
    inertness arithmetic all read as intended.
- Output: OUT = SCRATCH/2x/gate/ under /home/claude/data, since the frames are about 100 MB. VERDICT.txt and the
  per-pair *-vs-*.txt files are copied into tests/harness/results/LAB2X-2026-11-19/ after the run.
- Invocation (phase 2):

      tests/harness/gate-2x.sh --exe SCRATCH/2x/exe/S2NR.EXE --plain SCRATCH/2x/exe/PLAIN.EXE --out SCRATCH/2x/gate

- Build step amendment (sec. 3): after the plain rebuild,
  `cp build/ags-release/ags.exe $SP/exe/PLAIN.EXE` and require its sha256 = c68241073cb0dbcc6f0870c22ba31a0d904dd2261e72a44fbb7ba75f6cfb7f43
  (the v0.1.1 AGS.EXE as shipped; RV README sec. 1). A mismatch VOIDs the build. The R arm runs that file.

### F1.1 A click row, CLK-2x (input coverage)

The line is 5days room 3 at 2x, as S16-2x, plus DOSAGS_TICKCLICKS=200,50,12. That is 12 engine clicks at ticks
200, 250, ... 750, all inside the 1000-tick run. It is the V011/RM83-SMOKE-5days pattern 1000,50,50 rescaled: the same
period, the first click after room entry, a count that ends 250 ticks before exit.
- Freeze ticks: 5, 20 (room entry); then, for six of the clicks, one tick after the click (cursor at its new point,
  the walk starting) and 25 ticks after it (mid-walk): 201, 225, 301, 325, 451, 475, 601, 625, 751, 775; then 900.
  13 freezes, --min 10.
- Arms: all of A B F C1 C2 V V2, plus R (F1.2).
- PASS rule: as the game rows. A == B, F == B and R == B at every freeze; V clean; C2 differs.
- Extra witness: in every arm, "DOS-PORT tickclicks first=200 period=50 count=12" and 12 "tickclick lc= n= x= y=" lines.
  The (lc, x, y) lists must be identical across arms; otherwise the row is VOID, since the arms met different input.

Does the click simulation move the DRAWN cursor? Yes, read from the source (dosags-ring, 0383):
- dos_tick_clicks (Engine/main/game_run.cpp:1999-2034, ags 0247) runs at the start of the tick's input phase (:2057).
  It calls SetMousePosition(px[k], py[k]), then SimulateMouseClick(kMouseLeft).
- SetMousePosition (ac/mouse.cpp:354-369) -> Mouse::SetPosition -> Mouse::SetSysPosition (device/mousew32.cpp:111-121),
  which sets sys_mouse_x/y. It then calls RefreshMouse -> ags_domouse -> Mouse::Poll (mousew32.cpp:82-109), which copies
  them into mousex/mousey.
- The cursor sprite is drawn at mousex - mouse_hotx (ac/draw.cpp:4100) and marked dirty as kDirtySrc_Cursor (:4101-4102).
So the drawn cursor moves, and its dirty marks are on the narrowed path, but only as a JUMP at each click tick: there
is no motion between clicks.

GUI hover:
- The 12 points are fixed (x 40-280, y 140-190 in room coordinates; game_run.cpp:2010-2011). They give a hover only if
  one lands on a GUI control with a mouse-over state. For 5days room 3 that cannot be read from source (the GUI layout
  is in the compiled game data). The CLK-2x frames will show it; it is not claimed.
- The tree has no tick-keyed mouse-MOTION driver: DOSAGS_TICKCLICKS is the only DOSAGS_TICK* input.
- The host-side drivers (drive-clicks-dosbox.sh, lab-drive-xdotool.sh) do move the real DOSBox-X mouse, so they give
  hover and motion. But they land on wall-clock time, so A and B would meet different game states at a freeze tick
  (ags 0247's own reason for existing). They also need the lock EXCLUSIVE (no --no-host-input). They cannot feed a
  pixel-for-pixel A/B.
- What does drive GUI redraw with no hardware is the bench fixture's script: `gui` shows and hides gMenu every 20 ticks;
  `full` opens the GUI and presses SAVE / LOAD / CLOSE (tests/fixtures/bench/README.md, scenes table). B8-2x-full is
  already a row.
- So: cursor movement and click-driven walking are covered (CLK-2x). GUI redraw is covered by script (B8-2x-full).
  GUI HOVER under real mouse motion is a stated GAP of this gate, like the fade. If it matters, the remedy is a
  tick-keyed motion sweep in the engine (a new lab knob, its own review), not this round.

### F1.2 An identity arm R on every game row (S16-2x, S32P-2x, S8-2x, CLK-2x)

- R = the PLAIN release exe (PLAIN.EXE, sha256 c68241073cb0..., the v0.1.1 AGS.EXE as shipped and the sec. 3 rebuild),
  at the row's 2x setup with the default env. That means no DOSAGS_SCALE2_* and no DOSAGS_DIRTY_PRESENT; at 2x the
  latter changes nothing today, since every 2x present is rej scaled.
- Registered: R == B at every freeze tick. This proves B, which is S2NR with the switch off, is today's 2x path,
  untouched by the overlay.
- Witness: R's EXE-SHA256 is the plain release; R's RUNMANI.LOG has no scale2 line. Either failing is VOID.
- If R != B: the overlay changed the switch-off path. That FAILs the "unset = unchanged" claim, and with it every
  A == B reading.

### F1.3 The 1x inertness pair on S16 (row S16-1x)

- Arms I1 (S2NR, DOSAGS_MAX_SCALE=1, DOSAGS_SCALE2_NARROW=1) and I0 (S2NR, DOSAGS_MAX_SCALE=1, switch unset).
- Setup: S16-2x's scene and freeze ticks, at the same 640x480 cfg. DOSBox-X has no 512x384 mode (the presentation
  README's rung (b) note), so the 1x rung here is 640x480 centred: render dest (160, 120, 479, 359 : 320 x 240),
  alias ON.
- Registered (not information):
  - I1 == I0 at every freeze tick;
  - I1's scale2 line reads narrow = full = fullfast = pal = rects = 0, latch_sets = 0, and every rej field but geom 0;
  - rej geom = presents_real + presents_skipped (I1's fps_basis line). Every present attempt reaches the decision
    and is counted geom at 1x; nothing else is touched.
- Witness: I0 has no scale2 line.

### F1.4 Run count (corrects sec. 4's budget line, which said 5 game rows; there were 3)

| Rows | Arms each | Runs |
|---|---|---|
| S16-2x, S32P-2x, S8-2x | 8 (A B F C1 C2 V V2 R) | 24 |
| CLK-2x | 8 | 8 |
| S16-1x | 2 (I1 I0) | 2 |
| B8-2x walk/anim12/full, B16-2x walk/anim12 | 7 | 35 |
| Total | | 69 |

sec. 4 as written was 56 runs, so this is +13. At fixed 40000 cycles with every tick rendered, that is about 4-5 h of
the DOSBox-X lock (the AQ row's rate; GATE_RUN_TIMEOUT 3000 s per run).
- Order: the game rows first (S16-2x, S32P-2x, S8-2x, CLK-2x, S16-1x), then the bench rows.
- If the lock is contended, the bench rows may be cut to A B F C2. The reader reports the rest MISSING, so a cut
  bench row is reported, not passed.

### F1.5 Gate verdict (amends sec. 4's Pass)

The gate passes only if gate-2x-read.py exits 0. That requires:
- every witness passes;
- A == B, F == B, R == B in every row that has them, and I1 == I0;
- the A path ran (narrow > 0, latch_sets > 0) and A's rej fmt = 0;
- V is clean, and I1 is inert;
- C2 differs in every game row, C1 differs in at least one row, and every V2 reads vfy_bad > 0.

Results:
- Exit 1: the gate FAILs (or is VOID; the reader names which).
- Exit 3: no FAIL, but the gate has no demonstrated power. That is not a pass.
- S32P-2x VOID on "pack24 not engaged" (DOSBox-X has no 640x480x24) is the registered exception: that row moves to
  the 486, and the rest of the gate is read without it.

## FIX-UP 2 (2026-11-20, after gate run 1; written before any rebuild or cell)

Gate run 1 (gate1/, e4e027ca) was NOT PASSED as registered (sdlports' ruling). The registered controls had no power:
C2 (DOSAGS_SCALE2_BREAK=1) differed from B in 0/7 S16-2x pairs and 0/13 CLK-2x pairs, and V2 read vfy_bad = 0 everywhere.
48 cells were VOID on frames_skipped = -1. B8-2x-full read "A rej fmt=0" FAIL (rej fmt = 1).
This section changes the control, the frames_skipped witness and the rej fmt check. Every other registered term stands.

### F2.1 Overlay: a whole-box break control (tests/harness/apply-2x.py)

- DOSAGS_SCALE2_BREAK=2 (exactly "2"): the LAST box of every narrowed present is not blitted, but it is still pushed. The
  window surface keeps that box's previous picture and the screen shows it. This is a whole missed region: the defect
  class the narrowed path must never have, and the one the screen-equality comparison and the verifier exist to see.
- DOSAGS_SCALE2_BREAK=1 (exactly "1"; before, any value starting "1") is kept as an information arm.
  Why it had no power: a dirty box's last column and row usually hold pixels that did not change (AGS invalidates
  generously, and boxes merge with slack), so blitting them one short leaves nothing stale. gate1's V2 at break = 1 read
  vfy_bad = 0, so the whole-frame verifier saw no stale pixel at all on those runs. The control was weak, not the check.
- Any other value is off. The exit line already prints break=, so it now reads 0, 1 or 2.
- Code delta against the phase-1 overlay: 3 lines (the parse, `break == 1` for the shrink, `break == 2 && i == n - 1`
  skips the blit) plus comments. Switch-off and switch-on-without-break code is unchanged.
- Dry run on a fresh copy of dosags-ring's vendor/ags (0383, clean): SCRATCH/2x/apply-2x.diff (2 files, +372 -4); the
  copy was deleted. It replaces the phase-1 diff as the reference for the rebuild's vendor-diff check.

### F2.2 Gate driver and reader (tests/harness/gate-2x.sh, gate-2x-read.py)

- C2 = DOSAGS_SCALE2_NARROW=1 DOSAGS_SCALE2_BREAK=2.
  - Registered: C2 DIFFERS from B at >= 1 comparable freeze in EVERY game row (S16-2x, S8-2x, CLK-2x; and S32P-2x
    if it is not excepted). On bench rows it is information.
  - A C2 that does not differ is printed NOPOWER (exit 3 if nothing else fails). A VOID C2 pair stays VOID (exit 1).
- V2 = DOSAGS_SCALE2_NARROW=1 DOSAGS_SCALE2_VERIFY=1 DOSAGS_SCALE2_BREAK=2.
  - Registered: vfy_bad > 0 in every row it runs, printed PASS / NOPOWER.
- C2i = DOSAGS_SCALE2_NARROW=1 DOSAGS_SCALE2_BREAK=1 (gate1's C2): a new information arm on the game rows only
  (S16-2x, S32P-2x, S8-2x, CLK-2x), compared with B and printed INFO.
- frames_skipped witness: an arm passes if its frames_skipped is 0 or -1 AND equals the row's reference arm's value. The
  reference is R on the game rows, B on the bench rows, and I0 on S16-1x. A reference outside {0, -1}, or any arm that
  differs from it, is VOID.
  - -1 is the engine's own reading of an un-timestepped run (game_run.cpp:1528-1546, ags 0048's note: RenderCounter
    resynced at the first-room reset). The plain exe R reads it too (gate1: S8-2x and the B8/B16 walk and anim12 rows,
    every arm).
- "A rej fmt=0" becomes "A rej fmt", INFO. "A path ran" (narrow > 0 and latch_sets > 0) stays registered.
- All other checks and the exit codes are unchanged: 0 pass, 1 any FAIL / VOID / MISSING, 3 a control without power.

### F2.3 The rej fmt = 1 in B8-2x-full, from the code (no runs)

The decision (apply-2x.py sec. 5, in Present() ahead of 0102's frame_bytes_for_skip) counts rej_fmt on any of these:
- blit_src != _vscreenSurface;
- flip != kFlip_None;
- a format mismatch, or bytes per pixel not 1/2/4;
- !dst_inside;
- !margins_clean.
It tests them BEFORE the latch.

The bench rows are BORDERED: dst = (0, 40, 640, 400) in 640x480. The game rows are not: dst = the whole window. With a
border, ags 0100's margins_clean is false until 0100 has cleared the margins for that exact window surface and dst
(_marginsClean*, set by the same present that fills them). So the FIRST present at the bordered geometry reads
margins_clean = false. That present is counted rej fmt, then fills the margins and blits in full, which is the present
that arms the latch. With no border, margins_clean is true by definition, and the first present falls through to the
latch test instead: rej nolatch.

gate1's A arms show exactly that:
- all five bench rows read fmt=1 nolatch=0;
- all three valid game rows (S16-2x, CLK-2x, S8-2x) read fmt=0 nolatch=1.
B8-2x-full's F arm reads fmt=0 because the hint test comes first there (rej hint=124).

Ruled out:
- a flip: the bench script has none;
- a non-vscreen source: blit_src is _vscreenSurface unless flipped;
- a format or depth mismatch: the same rows' full presents ran the new replicator (fullfast > 0), which requires
  src->format == dst->format and 1/2/4 bytes per pixel;
- dst outside the window: 640x400 at y=40 fits 640x480.

So the one rej fmt is the run's first present, classified fmt by the counter's test order. It is not a path defect,
and it is the same present today's path also presents in full. Information only (F2.2).

### F2.4 Re-sim of the new reader on gate1's cells (no emulator)

SCRATCH/2x/resim2.py copied SCRATCH/2x/gate (gate1's cells, held read-only during the re-sim) twice. The copies were
deleted afterwards. Output: SCRATCH/2x/RESIM-2.txt.

Positive copy:
- frames_skipped as gate1 ran;
- C2i = gate1's C2 as it ran (break = 1);
- C2 synthetic at break = 2: the scale2 line says break=2, and one freeze frame gets a 6x6 patch so it differs;
- V2 synthetic at break = 2 with vfy_bad = 37.
Reader exit 0, "0 FAIL, 0 VOID, 0 MISSING; controls: all have power".
- The -1 rows (S8-2x, B8/B16 walk and anim12) now pass their witnesses.
- Their real gate1 frames then compare equal: A==B, F==B and (S8-2x) R==B.
- C2i (break = 1) differs in 0/7, 0/13 and 0/7 pairs.
- B8-2x-full reads "A rej fmt INFO rej fmt=1".
- S32P-2x stays EXCEPTED.
(The A/F/R equalities are read from gate1's real frames. They are information from the re-sim, not a gate result.)

Negative copy: the positive copy plus four planted defects. Reader exit 1, "0 FAIL, 4 VOID; controls: C2 did not
differ in CLK-2x; a V2 read vfy_bad=0". Each defect was caught:
- S16-2x/F frames_skipped -1 against R's 0 -> VOID;
- S8-2x/A frames_skipped 0 against R's -1 -> VOID;
- CLK-2x/C2 with gate1's frames (no difference) -> NOPOWER;
- B8-2x-walk/V2 vfy_bad 0 -> NOPOWER.

### F2.5 The whole gate re-runs, on a rebuilt S2NR

A control changed after data, so NOTHING from gate1 is carried over. Every row and every arm re-runs on the new exe.
- Build: as sec. 3 + F1.0, unchanged (dosags-ring, release flavour, vendor restored).
  - The plain rebuild must reproduce c68241073cb0... and is kept as PLAIN.EXE.
  - The overlay's vendor diff must equal F2.1's SCRATCH/2x/apply-2x.diff apart from file headers and git's hunk-header
    function context (gate1's build check, by patch + cmp of the resulting files).
  - Output: S2NR.EXE, a new sha256, recorded.
- Gate:

      tests/harness/gate-2x.sh --exe SCRATCH/2x/exe/S2NR.EXE --plain SCRATCH/2x/exe/PLAIN.EXE --out SCRATCH/2x/gate2

  - Same mode: lane 398 (DOSBOX_DISPLAY_NUM=398) and DOSBOX_LOCK_WAIT=7200, as gate1.
  - A NEW output dir; gate1's cells stay as they are.
- Runs:

| Rows | Arms each | Runs |
|---|---|---|
| S16-2x, S32P-2x, S8-2x, CLK-2x | 9 (A B F C1 C2 C2i V V2 R) | 36 |
| S16-1x | 2 (I1 I0) | 2 |
| B8-2x walk/anim12/full, B16-2x walk/anim12 | 7 | 35 |
| Total | | 73 |

  - That is 4 more than gate1 (the C2i arms). At gate1's rate (69 runs in 4 h 14 min) it is about 4 h 30 min of the
    DOSBox-X lock.
- Verdict: F1.5 as amended by F2.2. The gate passes only if gate-2x-read.py exits 0. S32P-2x's F1.5 exception stands.

## FIX-UP 3 (2026-11-20, after gate run 2; written before any rebuild or gate cell)

Gate run 2 (gate2/, 34ee9cba) was NOT PASSED as registered (sdlports' ruling, reader exit 3). Its one failure:
B16-2x-walk's V2 (DOSAGS_SCALE2_BREAK=2 + the verifier) read vfy_bad = 0, and its C2 equalled B at 5/5 freezes. This
section changes the break control again and registers C2 on the bench rows. Every other registered term stands.

### F3.1 Diagnosis (information, not a rescue): why break=2 had no power on B16-2x-walk

- Tool: tests/harness/diag-2x-boxes.py (a66f85fa, link fix dee730eb), applied on top of apply-2x.py in a separate exe,
  S2DIAG.EXE 0138ff5c1479. It is active only with DOSAGS_SCALE2_VERIFY=1, and never in a gate exe or a release.
- Per narrowed present it logs the box list, and per box the changed and uncovered px, measured BEFORE the blit with the
  window up to date. It also counts what four candidate controls would leave stale.
- Runs: V arm of all eight 2x rows in DOSBox-X, lane 398. Summaries: DIAG-FIXUP3.txt.
- Answer for B16-2x-walk (1039 narrowed presents, 4-6 boxes each):
  - The last box held a changed px on 0 of 1039 presents (chg>0=0).
  - It touched a carried box on all 1039 (carryhit=1039; tag U=852, G=7, N=180). In other words, it is a box this
    frame re-invalidated, or one carried in by patch 0193, whose region is already up to date in the window.
  - It is not explained by containment: it was contained in or overlapped by earlier boxes on only 3 presents.
  - Only 197 of 1039 presents change any px at all ("all=197"). The walk bench redraws mostly identical frames.
- break=2's power was an accident of box order. In the rows where it had power, the last box happened to hold the
  moving object.

Per row, presents on which each candidate control would leave a changed px unblitted (narrowed presents in brackets):

| Row | narrowed | last (break=2) | largest | isolated | all (break=3) |
|---|---|---|---|---|---|
| S16-2x | 997 | 2 | 48 | 47 | 48 |
| S8-2x | 999 | 5 | 229 | 225 | 229 |
| CLK-2x | 997 | 14 | 132 | 132 | 137 |
| B8-2x-walk | 1040 | 1 | 198 | 196 | 198 |
| B8-2x-anim12 | 1040 | 502 | 501 | 501 | 502 |
| B8-2x-full | 120 | 1 | 2 | 3 | 4 |
| B16-2x-walk | 1039 | 0 | 177 | 190 | 197 |
| B16-2x-anim12 | 1039 | 501 | 500 | 500 | 501 |

"all" is the ceiling: no control that only removes blits can leave a present stale if none of its px changed.

### F3.2 The control: DOSAGS_SCALE2_BREAK=3 (tests/harness/apply-2x.py)

- Exactly "3": NO box of any narrowed present is blitted, but every box is still pushed. The narrowed path writes nothing.
  The window then changes only on full presents, so it holds the picture of the last full present.
  - This is the reviewer's "skip all boxes on every Nth narrowed present", at N = 1.
- Why it has power by construction: on any narrowed present whose boxes hold a changed px, that px is not written.
  - The verifier runs after the blit on the same present, so V2 reads vfy_bad >= the row's "all" count. That is > 0 in
    every row (min 4, B8-2x-full).
  - The stale px stay stale until the next full present. So the verifier keeps counting them, and a freeze in that
    window shows them.
  - The only way it has no power is a row that gives the narrowed path nothing to draw. In such a row A==B would also
    carry no information, so NOPOWER there is a true finding about the row.
- It is coarser than break=2: it proves the comparison sees a whole missed update, not a single missed box. The finer
  class is still covered by C1 (DOSAGS_BREAK_0193=1, the carry merge off), which differs as registered (FIX-UP 1).
- break=2 and break=1 stay in the code. break=1 stays as the C2i information arm. break=2 is no longer run.
- Code delta against FIX-UP 2's overlay:
  - the parse accepts '1'..'3';
  - one line, `if (dos_s2_break == 3) continue;`;
  - comments.
  Switch-off code and switch-on-without-break code are unchanged in effect.
- Dry-run diff: apply-2x-fixup3.diff. It was made by diff -ru on a clean copy of the two files from dosags-ring vendor/ags
  HEAD d47c5b982a35, with apply-2x.py (sha256 5e7b74497647...) run on the other copy. The build check is "same resulting
  files": apply-2x.py run on one clean copy and `patch -p1` of the diff on another are cmp-identical (ali3dsw.cpp
  de9f31f246e0..., quit.cpp 37dfcf7d3695...).

### F3.3 Checks that change (gate-2x.sh, gate-2x-read.py)

- C2 and V2 run at DOSAGS_SCALE2_BREAK=3, where they ran at 2. C2i is unchanged (break=1, information).
- New witness (VOID): the scale2 line's break= must read 3 in C2 and V2, 1 in C2i, and 0 in every other switch-on arm.
  This catches an arm that ran the wrong control.
- "C2 differs" (C2 vs B differs at >= 1 comparable freeze) is now registered on the bench rows too. In FIX-UP 2 it was
  information there.
  - The one exception is B8-2x-full, where it stays information. That row has 2 comparable freezes (ticks 10 and 40) and
    only 4 narrowed presents with any change (presents 1, 41, 42 and 82), so whether a freeze lands while px are stale
    can't be predicted from the code.
  - V2 stays registered on every row, B8-2x-full included. That is the row's powered control (vfy_bad >= 4 by F3.2).
- "V2 verifier power" (vfy_bad > 0) is registered on every row, as in FIX-UP 2.
- The exit codes are unchanged: 0 pass, 1 any FAIL / VOID / MISSING, 3 a control without power.

### F3.4 Re-sim of the new reader on gate2's cells (no emulator)

resim3.py copied SCRATCH/2x/gate2 twice; gate2 itself was not touched. The output is in RESIM-3.txt.

Positive copy:
- C2 and V2 relabelled to break=3.
- B16-2x-walk given F3.2's predicted outcome: one C2 freeze frame gets a 6x6 patch, and V2 reads vfy_bad = 197.
- Every other row keeps gate2's frames and counters, which already had power.
- Reader exit 0: "0 FAIL, 0 VOID, 0 MISSING; controls: all have power". B8-2x-full reads "C2 differs INFO 2 pair(s),
  0 differ".

Negative copy: the positive copy plus four planted defects. Reader exit 1: "0 FAIL, 3 VOID, 0 MISSING; controls: C2 did
not differ in B16-2x-walk,S16-2x; a V2 read vfy_bad=0". Each defect was caught:
- B16-2x-walk/V2 vfy_bad 0 -> V2 NOPOWER;
- B16-2x-walk/C2 with gate2's frames (equal to B) -> C2 NOPOWER, registered on a bench row;
- S16-2x/C2 still reporting break=2 -> witness C2 VOID;
- S8-2x/C2i reporting break=3 -> witness C2i VOID.

### F3.5 The whole gate re-runs, on a rebuilt S2NR

A control changed after data, so NOTHING from gate2 is carried over.
- Build: as F2.5, on the FIX-UP 3 overlay.
  - The plain rebuild must reproduce c68241073cb0....
  - The build's own vendor diff is checked as "same resulting files" against apply-2x-fixup3.diff (patch + cmp, F3.2).
  - The new S2NR sha256 is recorded.
- Gate: gate-2x.sh into a NEW dir SCRATCH/2x/gate3, with lane 398 and DOSBOX_LOCK_WAIT=7200, as gate2.
- Runs: the same 73 as F2.5. At gate2's rate (73 runs in 4 h 24 min), that is about 4 h 30 min.
- Verdict: the gate passes only if gate-2x-read.py exits 0. S32P-2x's F1.5 exception stands.
