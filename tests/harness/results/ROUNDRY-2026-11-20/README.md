# Round RY -- the narrowed 2x present (SCALE2-NARROW) on the 486, at the 640x480 2x rung (written 2026-11-20; pre-registration, before any data)

Status: terms accepted by sdlports with changes (review of the draft 8f2a37c32dd2), folded in below. The reader and its
simulation are written (sec. 6). The driver is gen-driveRY.py (sec. 2). Nothing is staged or run. The power-on needs the
owner's direct OK in session; vcctrl is pinged before it.

## 0. Why, and what decides
- LAB2X gate3 PASSED as registered in DOSBox-X (a3411645, sdlports' ruling). The narrowed 2x path draws the same frames as
  the reference there. This round asks what it costs on the 486, which is the only place a performance claim can rest.
- The owner, in session:
  - decision 01M7W318SCKJXDDNCM6FB1D1CZ: item 3, the capture stick is the witness; item 4, if 2x proves out on the 486 it
    ships as an opt-in switch, default off;
  - decision 01M7X8X4SVZNCB41005GSYWSG7 (3): the stick stays the witness despite its USB drops, and a drop during a run
    voids that run;
  - decision 01M7XPBAR870HGWWG15X2AAXRV: the bar is "Same bar, new rung" (sec. 4), and the shape is "One power-on, 7 runs"
    (sec. 2).
- S32P-2x moves here from the gate (F1.5): pack24 is not engaged in DOSBox-X. Information from gate3's S32P-2x row
  (sdlports, read raw): its window surface is XRGB8888 (FORCE_COLOR_DEPTH 16 -> 32). Though the row is EXCEPTED, A, F and
  R == B at 0 px at all 7 freezes; V reads vfy_bad=0 over vfy=1012; V2 at break=3 has power (vfy_bad 521). So the 4-bpp
  narrowed blit is lab-checked as information. The one part untested anywhere is pack24's handling of the pushed rects on
  the 486. The RY32B sheet review looks for exactly that (sec. 5).
- Measurement only on the target: nothing there is moved or deleted.

## 1. Binary
- S2NR.EXE = gate3's exe, byte for byte: sha256 9599809419c821e0aed4a1740e82f311a07cbea663a4580e7544f892be539043 (8,681,739 B).
  It is the release flavour (the RV gate line's flavour) with tests/harness/apply-2x.py (5e7b74497647...) applied on ags 0383.
  Its log reads binary_sha12=f42436aadd7b and "DOS-PORT build_dirty=1": the overlay is not a committed patch.
- build_dirty=1 is accepted ONLY for this exe: PRE-STAGE-SHA256.txt and POST-RUN-SHA256.txt must both read
  9599809419c8...; anything else, or any other build_dirty value, is VOID.
- Why this exe and not a clean patch build: it is the exe the emulator gate passed (sdlports agrees). Landing the overlay as
  a numbered patch is a later step, if this round proves 2x out (sec. 8).
- The overlay's lab controls (DOSAGS_SCALE2_BREAK, DOSAGS_SCALE2_VERIFY) stay unset in every cell. The witness is the scale2
  line's "break=0 verify=0".

## 2. Cells and order (one power-on, cap 120 min)
WARMUPRY (WARMUPRV's line: l308, BLASTER read, PKGDIR) -> RY16B1 RY32B1 RY8B1 (the first readings, one block, needed
whole) -> RY16B2 RY32B2 RY8B2 (the second readings, one block) -> RY16A (an information anchor, last, dropped first).
- B cells: RV's scene lines on S2NR, with S32P-ACSETUP-ON.CFG (sha256 24d874f2..., sound on, full_window; the 640x480 cfg
  round V1 staged) at every depth, and DOSAGS_MAX_SCALE=2 DOSAGS_SCALE2_NARROW=1:
  - RY16B*: 5days, --startr 3, $FB, TAS_AUTO_EXIT_TICK=5000.
  - RY32B*: the same, plus DOSAGS_FORCE_COLOR_DEPTH=32 SDL_DOS_PACK24=1.
  - RY8B*: trilbysnotes, --startr 35, DOSAGS_MSGSKIP=1, $FB, TAS_AUTO_EXIT_TICK=5000.
  The 320x240 games land at 640x480, render dest (0, 0, 639, 479 : 640 x 480).
- The cfg, against the one RV8 and RV16 used (tests/harness/presentation/trilbysnotes/ACSETUP-ON-512X384-ROUND.CFG, staged as
  ACSETUP.CFG for both games): the whole diff is one line, so the sound and MIDI settings are identical:

      21c21
      < fullscreen = 512x384
      ---
      > fullscreen = full_window

  RV32 used S32P-ACSETUP-ON.CFG itself.
- RY16A: RV16A's line verbatim (ACSETUP-ON-512X384-ROUND.CFG, 1x) on S2NR with the switch unset. Information only. It tells
  S2NR's switch-off path apart from RV's exe on the rig.
- The B-against-A predictions (sec. 7) are read against RV's A readings (RV16A/RV16C, RV32A/RV32C, RV8A/RV8C on
  c68241073cb0). They are information, cross-day (2026-11-19 against RY's day), and named as such. A full ABBA (9,120 s of
  need) does not fit in one power-on (about 6,250 s).
- The driver: gen-driveRY.py writes build/ws/roundRY/driveRY.sh from round RV3's committed driver (RV3/driveRV3.sh). It keeps:
  - the lock watch with GUARD LOCK;
  - ACTIVE-CELL, and no recovery cycle;
  - every vcctrl call with </dev/null;
  - the date and README checks.
  need() is 760 s a cell, so the blocks need 2,280 / 2,280 / 760 against about 6,250 s after the 75 s settle, the warm-up and
  the 240 s reserve (sdlports checked the sum). Expected: about 85 min mains on.
- A cut block goes to a later round as RV did. No re-run inside this round, and no rescue runs.
- **Stop rule after WARMUPRY** (sdlports, before any data). The warm-up goes through a boot, the game's mode set and the exit
  back to text mode, which a 486-off soak cannot exercise.
  - Any stick drop anywhere in the warm-up stops the round before the B blocks: the driver powers off and reports. That
    costs one warm-up instead of about 85 min of VOID cells. No re-run inside the round.
  - A drop is a bad card-state.log sample, or a kernel drop line on the stick's port in vcctrl's live tee from the cell's
    START.UTC on.
  - So is the lack of a live record: the tee missing, starting after the warm-up, or silent for more than 90 s.
  - The driver's check is `ry-read.py --kern KERN-TEE.txt warmup <dir>` (exit 1 = STOP).
  - Its stop path is dry-tested by test-warmstop.sh (WARMSTOP-TEST.txt). It runs the driver's own lines with poweroff
    stubbed, in 6 cases (clean, card, kdrop, notee, stale, latetee): all PASS.

## 3. Registered pair
Per depth on S2NR at the 2x rung: <depth>B1 + <depth>B2. The terms are MET x2 (both MET), MET x1 or NOT MET. A cell that
is VOID or PATH-OFF (sec. 5), or not run, counts as not MET and is named as such.

## 4. The bar (owner, decision 01M7XPBAR870HGWWG15X2AAXRV: "Same bar, new rung")
- PLAN-GATES' bar numbers, unchanged: both tick figures 39.2-40.8, fps_p50 >= 40, completeness >= 95%, audio counters clean
  (pcm_irqs exact, overwrites 0, late_writes 0, silent_irqs 0 outside room loads), screen witness clean, x2.
- Only the rung clause changes: "512x384 centred 1x (S32: 640x480x32 1:1)" becomes "640x480, integer 2x, SCALE2-NARROW on" at
  every depth.
- The campaign's 99% displayed line stays the REGRESSION line, reported beside the verdict and not scored, as in RV.
- Scored by gatebar.py's cell reading through ry-read.py (sec. 6). A tick figure out of band is NOT MET (V1's rule).

## 5. Outcomes and witnesses per cell
States: VOID (the measurement is not valid), PATH-OFF (valid, but the design did not engage), MET, NOT MET.
- VOID:
  - gatebar.py voids it: stamp f42436aadd7b, exit_code, room, a missing field, msgskip; build_dirty other than as in sec. 1;
  - STDOUT lacks one of RV's six default lines (vmmode, englev, guiclip, charreuse, guictrlmark, routeprewarm), or
    BLASTER.TXT is not "A220 I7 D3 P330 T3";
  - B cells: the scale2 line in <TAG>.LOG is missing or not on=1 break=0 verify=0; render dest is not
    (0, 0, 639, 479 : 640 x 480);
  - RY32B*: STDOUT lacks "DOS-PORT pack24 engaged mode=0x0112 640x480" (RV32C's line);
  - RY16A: a scale2 line is present, or render dest is not (96, 72, 415, 311 : 320 x 240) (RV16A's);
  - a stick drop, or a missing stick record (below).
- PATH-OFF (B cells; sdlports' item 2): narrow / (narrow + full) < 95%. The measurement is fine, the design did not engage.
  It counts as not MET, and is not VOID.
- **Screen witness: the capture stick (B at 640x480 locks).**
  - CLEAN when the capture sheet shows the game in its play window with no trail, stale cursor or border garbage. For RY32B
    (sdlports' item 4), CLEAN also needs no stale or garbage rectangle at the walker or at the cursor: those are where
    pack24 packs the narrowed rects.
  - RY16A (512x384 does not lock) is read on the camera, information only. The camera runs in every cell as information.
- **Stick drops (decision 01M7X8X4; no camera fallback).**
  - **Play window (registered; owner decision 01M7XQPAWZF30XMWY4JRPPJNDH, "a stick drop counts from the run's start to
    game exit + 10 s"):** from the lock line to the game's exit + 10 s; a run with no exit anchor is VOID.
    - It starts at DRIVE-WALK.LOG's "lock is run-hw-<TAG>'s" line (UTC), when the harness takes the 486 to type RUN.BAT.
    - It ends at the exit anchor + 10 s. The anchor is run-hw.out's text-mode wait trace: the first sample past t+60 s that
      reads "changing" right after "blind". 512x384 is blind all through play; 640x480 goes blind at the mode switch. The
      end is taken as lock + t + 10 s; the trace starts about 3 s after the lock, so that is at least 7 s past the real
      exit. The run's own mode set and its exit to text mode are inside the window; the log pull after it is not.
    - The end is capped at the input-lock window's end: drive-walk's "lock no longer" line, or, when drive-walk hit its
      click cap and logged no release (RV8: 80 clicks), the last run-hw.out job's started_at + 5 s. On RV's 7 cells with
      both records, the release came 0.2-2.6 s after that job's start. Neither record, or no anchor: VOID.
    - Information, the 8649192c rule (`--window lock`): the whole input-lock window. It can't miss, but it also counts the
      log pull after exit (RY-SIM-LOCK.txt).
  - Why not "T0 + 30 s + the run's ms", as drafted: nothing on RV's records proves the 30 s. RV's level log shows game sound
    only in the RV32 cells, starting +23.5 / +25.7 s after T0 and ending +145.5 / +145.7 s. That is 11 s inside a +157 s
    window, on two cells only. The lock window is about 275 s; it also holds the log pull after exit.
  - A drop is either of:
    1. a witness/card-state.log sample (run-hw samples the card every ~2.1 s; times are the VM's local time,
       America/Los_Angeles) inside the play window with state unavailable, starting or nosignal, or with
       last_frame_age_s > 2.5. RV's clean cells read at most 0.28 s.
       - "frozen" is NOT a drop (sdlports' item B). vcctrld (daemon/vcctrld.py at c11bcc8) calls the picture frozen when
         bytes still arrive but its last 8 frames are byte-identical: a repeating source, such as a still scene. It is
         nosignal when no bytes arrive.
         - Across RV's card-state logs, all 19,959 frozen samples had a frames counter that had advanced since the
           previous sample, with last_frame_age_s at most 0.231 s.
         - The age > 2.5 s rule catches a real stall in any state, frozen included.
    2. a kernel line inside the play window on the stick's port: "USB disconnect", "Cannot enable", "unable to enumerate"
       or "device descriptor read". The hub-port form usbB-portP is port B-P. The stick's port is any port named by
       "New USB device found, idVendor=0001, idProduct=ff02", or by a "### STICK-PORT <port>" line. The port moves between
       power-ons (vcctrl), so the rule is keyed to the ID, never to a port number.
  - The kernel record: vcctrl tees `journalctl -k -f --utc -o short-iso-precise` on the capture host to a file from before
    relay-on until after power-off. Its first lines are "### TEE-START <t> UTC" and "### STICK-PORT <port>", and vcctrl
    appends a "### ALIVE <t> UTC" heartbeat every 30 s (the warm-up stop rule reads them). Right after power-off, vcctrl pulls the journal slice for the power-on window. Both go
    in build/ws/roundRY/ as KERN-TEE.txt and KERN-SLICE.txt, with "### WINDOW <from> UTC .. <to> UTC" headers and the host
    name scrubbed.
    - The slice is the authority; vcctrl diffs the tee against it and reports any difference.
    - The journal is volatile (in /run, flooded by a dropping stick, cleared by a reboot of the capture host), so the
      slice is pulled at once.
    - If the tee was not armed, or the capture host rebooted, vcctrl says so.
  - VOID also when, for a B cell (sdlports' item 3; "no file" or "no lines" never reads as "no drop"):
    - DRIVE-WALK.LOG, witness/card-state.log, START.UTC or the kernel slice is missing or unreadable;
    - no card-state sample falls in the play window;
    - no WINDOW of the slice covers the play window;
    - a drop-kind kernel line in the play window is on a port that no line ties to the stick or to another device.
- **Precondition before the power-on ask: a stick soak** (owner decision 01M7XQPFSWYEAKEZJXZGTDMPRT; vcctrl's watch
  01M7XPDTEMBYN9DDXYGW4TTWAD).
  - vcctrl watches the stick for about 1 h, with the 486 off.
  - The ask needs no stick disconnect in the soak window, and none in the minutes between the soak's end and the ask.
  - If drops continue, the connection gets fixed (cable / port / hub / stick, the owner's call) before any power-on ask.
    The drop rule itself stays strict.
  - The soak's window, kernel line count and vcctrl's report go into SUMMARY.txt and this README before the ask.
  - For reference (vcctrl, 2026-11-20): 39 disconnects since the 16:36Z reseat, none since 19:05:30Z.

## 6. Reader, and its simulation before any data
- tests/harness/ry-read.py (`--kern KFILE cell DIR LABEL`, `--kern KFILE pair LABEL DIR_1 DIR_2`; LABEL B16 / B32 / B8 /
  A16). It imports gatebar.py's cell reading and rv-read.py's witness lines, and adds sec. 1 and sec. 5.
- gatebar.py amendment (2026-11-20, before any data): a caller may accept one build_dirty value (args.allow_dirty). Only
  ry-read.py sets it, and only after the sha256 witness. gatebar's CLI never sets it, so every earlier reading is unchanged
  (checked: RV16A + RV16C still read "S16: MET x2").
- ry-sim-mk.py made scratch copies of RV's cells as S2NR at 2x would leave them. Every copy has stamp f42436aadd7b,
  build_dirty=1, the S2NR sha, the 2x render dest and a scale2 line. RV's REAL card-state.log, DRIVE-WALK.LOG and START.UTC
  are kept. The registered reading is RY-SIM-EXIT.txt (`--window exit`); RY-SIM-LOCK.txt is the same set read with the
  lock window, as information.
- **On RV's real stick records** (sdlports' item 3). The kernel slice comes from vcctrl: kern-rv-2026-11-19.txt, sha256
  2dd9110fd5fa..., host name scrubbed. The journal survives only from 2026-11-19T17:49:02Z, so it covers 17:49:02-18:08:55Z
  and 18:37:00-19:24:30Z: 57 stick disconnects and 3 Cannot enable.
  - First power-on, not covered: RVDST, RV16A, RV16B, RV32A and RV8A read VOID on "no kernel WINDOW covers the play window".
    That is the rule working: no record is not "no drop".
  - Covered, with the registered exit window (RY-SIM-EXIT.txt): RV16C MET; RV8B NOT MET (late_writes 3), as RV read them;
    RV32B VOID (no exit anchor: the stick was dead); RV32C and RV8C VOID (drops mid-play). So 3 of the 5 are VOID.
  - Covered, with the lock window (information, RY-SIM-LOCK.txt): all five read VOID on stick drops, and the card log and
    the kernel agree on each:
    - RV32B: the stick was dead, 120 nosignal samples;
    - RV32C: 8 bad samples, first at +3.3 s; kernel first at +0.8 s;
    - RV8C: 7 bad samples, first at +85.4 s;
    - RV16C: 3 bad samples at +237.7 to +241.9 s; kernel first at +236.2 s;
    - RV8B: 1 bad sample at +210.3 s; kernel at +208.7 s.
  - RV16C's and RV8B's drops fall after the game's exit (play ends about +146 s), during the log pull. Under the drafted
    +30 s window, both would have read as RV read them (MET; NOT MET on late_writes). That is the cost of a window that
    cannot miss, and the reason for the soak precondition.
  - RV32C was read CLEAN in RV on its capture frames. Under this rule it is VOID.
  - Do the drops cluster on the 486's own mode changes? (sdlports' question; mode-drops.py, MODE-DROPS.txt.) All 57
    stick disconnects in the slice, by the phase of the cell around them:

    | phase | drops | 486 mode change? |
    |---|---|---|
    | at the DOS prompt, before the send | 17 | none (idle text mode) |
    | boot (send reboot -> lock) | 16 | yes (BIOS / DOS) |
    | collect reboot | 9 | yes |
    | play (lock -> exit) | 9 | none inside a run's one mode (RV32C at +0.8 / +3.7 / +22.4 / +48.1 s; RV8C at +83 to +137 s) |
    | after the exit (-> collect) | 6 | the exit to text mode, 5-82 s before |

    - They come in bursts in time (17:49-18:08Z, then 18:55-19:16Z), in every phase. 26 of the 57 fall where the 486
      changes no mode: 17 at the prompt and 9 mid-play.
    - RV32C's +0.8 s drop is before RUN.BAT is even typed: run-hw takes the lock, then types CD and RUN.BAT. So it is not
      AGS's mode set.
    - This does not support "the stick drops on mode changes". It reads as a fault in bursts, by time.
  - The window (DECIDED, owner decision 01M7XQPAWZF30XMWY4JRPPJNDH: `--window exit`; the lock window is information):
    - from the lock line to the game's exit + 10 s;
    - the exit is anchored on run-hw.out's text-mode wait trace: the first "changing" after "blind" past t+60 s. The trace
      starts about 3 s after the lock, so lock + t + 10 s is at least 7 s past the real exit;
    - a cell with no anchor is VOID;
    - it keeps the run's own mode set and exit inside the window, and leaves out the log pull after it.
    - On RV's records (RY-SIM-EXIT.txt): RV16C MET and RV8B NOT MET (late_writes), as RV read them; RV32B, RV32C and
      RV8C stay VOID. RV32B has no anchor (its stick was dead); RV32C and RV8C have drops mid-play.
    - The owner's rule is "a drop during a run". With this window the run's own mode switches are "during"; the log pull
      after the exit is not.
  - The 10 s frame-gap rule of the draft is DROPPED. RV's witness frames are sampled every 9.1-11.4 s whatever the stick
    does: RV32C had 5 drops and a max gap of 10.4 s. So a gap rule has no power. The card-state samples replace it.
- Planted cases, each read as intended:
  - pos16 / pos32 / pos8 (RV16A / RV32A / RV8A with a planted, drop-free WINDOW): MET, as RV read them;
  - noscale2: VOID;
  - pathoff (90%): PATH-OFF;
  - nopack24: VOID;
  - dirtynosha (PLAIN's sha with build_dirty=1): VOID;
  - cardin (unavailable at +60 s): VOID;
  - cardout (the same at +400 s, past the lock release): MET;
  - cardage (locked, age 3.1 s): VOID;
  - nocard: VOID;
  - nowalk: VOID;
  - kstick (a disconnect on the stick's port at +60 s): VOID;
  - kunattr (the same on a port tied to no device): VOID;
  - kother (on the camera's port): MET;
  - norelease (no lock-release line): the window ends at the last run-hw job + 5 s, MET;
  - noanchor (run-hw.out's trace with no "changing" sample): VOID with the exit window (MET with the lock window);
  - noend (no release line and no run-hw job after the lock): VOID;
  - a16: MET;
  - a16bad (a scale2 line): VOID.

## 7. Predictions (B against RV's A readings, cross-day; PREREG-2X sec. 5, SCOPE-2X sec. 5), registered as information
- S8: steady 40.0-40.3, fps_p50 40.00, displayed A - (0.3..1.5) pp, whole-run A - (0.05..0.2).
- S16: steady 40.0-40.3, fps_p50 40.00, displayed A - (0.3..1.5) pp, whole-run A - (0.05..0.35).
- S32P: steady 40.0-40.3, fps_p50 40.00, displayed A - (0.3..2.5) pp, whole-run A - (0.05..0.5).
- Whole-run, from RV's A readings (39.32-39.43): S16 39.03-39.38 and S32P 38.88-39.35, both straddling the bar's 39.2
  floor; S8 39.12-39.28. S32P is the likeliest to be NOT MET, on whole-run (PREREG-2X sec. 5: 15-17 full presents a run at
  +20..+140 ms each). A NOT MET there is a live outcome, not a surprise.
- Against today's 2x anchor C364044 (S8 at 2x before the overlay: 26.99% displayed, fps_p50 9.78): B displayed >= 97%,
  fps_p50 40.
- The scale2 line in B: narrow share >= 95%, rej geom = 0 after the first present, full 10-20 a run.
- Falsifies the model (any one): B fps_p50 < 40 or steady < 40.0; B displayed < 95%; a witness defect (a trail, a stale
  cursor, border garbage).
- The stick: at its present drop rate, several B cells may read VOID. On RV's records, every covered cell would have. That
  is a property of the witness, not of 2x. The soak precondition (sec. 5) is there for it.

## 8. What follows
- A MET here is a result about the overlay build S2NR (9599809419c8), not about any release (sdlports' item 1). No release
  claim exists until the patched exe has its own pair.
- MET x2 at a depth: 2x proves out at that depth on the overlay build. The overlay becomes a numbered ags patch, default
  off (owner item 4), reviewed by sdlports and checked "same resulting files" against the overlay. The release that
  carries it gets its own registered pair.
- NOT MET, PATH-OFF or VOID: read as registered and sent to sdlports and the owner. Another power-on is the owner's call.
- The push (9 local commits) stays held until 2x passes here or is parked (owner item 2).

## 9. Housekeeping
- The Gateway is shared. The driver refuses to power on while the input lock is held or the target is on.
- The bus hold rig.gateway2000.plug is taken before the power-on. vcctrl is pinged and arms the kernel tee before relay-on.
- Witness frames: tests/harness/witness-ftp-check.sh on the staged set before any results commit.
- Not committed: audio captures, saves, game data. Raw results go to sdlports before any results commit.

## 10. Result (2026-11-21; raw to sdlports before this commit; sdlports' ruling: NOT MET at every depth)

**2x on the 486 does not pass as registered.** B16 MET x1, B32 NOT MET, B8 NOT MET.

### The power-on
- The owner gave the direct OK in session at 01:00Z, after the clean soak (decision 01M7XQPFSWYEAKEZJXZGTDMPRT) and sdlports'
  final OK.
- Before relay-on: services renewed rig.gateway2000.plug to 03:15Z; vcctrl armed the watch set and the kernel tee
  (TEE-START 01:00:41Z, STICK-PORT 1-2); two ALIVE lines and 0 kernel lines were checked before the driver started.
- Relay-on 01:01:53Z; power OFF 02:51:15Z (powerguard confirmed 02:51:22Z, 0 mW); driver exit 1.
- WARMUPRY passed every stop check, the stick rule included ("WARMUP stick: clean ... 01:03:09 .. 01:13:36 UTC").
- RY16B1, RY32B1, RY8B1, RY16B2 and RY32B2 each read run-hw exit=0, pre = post 9599809419c8, stamp f42436aadd7b,
  build_dirty=1.
- RY8B2: the game ran (lock 02:18:22.5-02:23:03.4Z, 80 clicks), but the collect failed at get-file's return reboot ("the
  machine never reset -- Scroll Lock did not clear"). The screen read no-picture until the 1800 s budget ran out, with no
  recovery by design. Then "STOP after RY8B2"; RY16A did not run. RY8B2's logs are still on the target's C:\DOSAGS.
- Records in RY/: SUMMARY.txt, POWERGUARD.txt, driveRY.sh, expected.txt, KERN-SLICE.txt, KERN-TEE.txt and RY-READ.txt.

### The stick
- Zero drops in the round. KERN-SLICE.txt (sha256 566c642371af..., vcctrl) covers 01:00:41-02:52:00Z with 0 kernel lines of
  any kind. Its CONTROL line shows the same query returning a known drop from 2026-11-20, so the empty result is not a
  broken query.
- The tee holds 222 ALIVE lines, with no gap over 35 s, and no journal lines. Capture respawn counters were unchanged.
- decode_errs 69 -> 82: all flat frames at a launch or an exit (vcctrl).

### The reading
ry-read.py at 24dc1cde against KERN-SLICE.txt (RY/RY-READ.txt; sdlports re-ran it, cmp-identical):

| cell | whole / steady | fps_p50 | displayed (skipped) | audio | registered (exit window) | lock window (information) |
|---|---|---|---|---|---|---|
| RY16B1 | 39.32 / 40.03 | 40.00 | 99.20% (40) | clean | MET | MET |
| RY32B1 | 38.98 / 40.10 | 40.00 | 99.16% (42) | clean | VOID (no exit anchor); NOT MET on figures (whole-run) | NOT MET |
| RY8B1 | 39.44 / 40.28 | 40.00 | 99.52% (24) | clean | VOID (no exit anchor); MET on figures | MET |
| RY16B2 | 39.22 / 40.00 | 40.00 | 99.20% (40) | silent_irqs 1 (tick 788) | NOT MET | NOT MET |
| RY32B2 | 37.72 / 38.84 | 40.00 | 95.24% (238) | silent_irqs 13, start_latency 2 | VOID (no exit anchor); NOT MET on figures | NOT MET |
| RY8B2 | -- | -- | -- | -- | VOID (no log collected) | VOID |

- Pairs, registered: B16 MET x1; B32 NOT MET; B8 NOT MET. Lock window (information): B16 MET x1; B32 NOT MET; B8 MET x1.
  No depth reaches MET x2 under either window.
- Witnesses, checked by sdlports from raw:
  - every scale2 line reads on=1 break=0 verify=0 vfy_bad=0. Narrow share: 4957/4972 (B16); 4955/4970 and 4759/4774
    (B32); 4878/4883 (B8). So no cell is PATH-OFF;
  - RY32B* each print "DOS-PORT pack24 engaged mode=0x0112 640x480" once;
  - render dest is 640x480 in every B cell.
- Screen (sdlports, sheets plus full 640x480 frames: RY32B1 #4 #10, RY32B2 #3 #13): the walker and the footprint cursor are
  drawn whole, with no stale or garbage rectangles. RY32B is CLEAN, so pack24 handles the narrowed rects on the 486.
  RY32B1 #14 is the exit's flat frame.

### Findings (sdlports)
- **The exit anchor fails at 2x** (a reader-fixture failure, not a stick fault). The registered anchor, "changing" right
  after "blind", was built from RV's 1x traces. At 2x:
  - RY16B1 reads blind->changing at t+154.4 s;
  - RY32B1 and RY32B2 read static->changing at t+155.9 / t+158.6 s;
  - RY8B1 has one lone blind sample at t+148.3 s.
  By the letter the three VOIDs stand. They change no depth result. A future 2x round re-registers the anchor from RY's
  traces before any data: for example from the game's own log (lock line + preloop_ms + loop_ms + tail_ms).
- **B32 fails on speed.** RY32B1: whole-run 38.98, stall_ms 2713 (B16's is 1414). RY32B2 has a late event: 238 frames
  skipped and 13 silent IRQs, all at ticks 4762-4817, with steady 38.84. That event is named as information; its cause is
  not established.
- **B16 fails on one silent IRQ in play** (RY16B2, tick 788). Its rates are inside the band in both cells.
- **Against the model** (sec. 7):
  - fps_p50 40.00 in every cell;
  - displayed 99.16-99.52% everywhere but RY32B2. That is far above today's 2x anchor (C364044: 26.99%);
  - whole-run straddles 39.2 as predicted. S32P is the miss, as predicted.
- **Next** (the owner, asked by sdlports): park 2x or plan another round; the held push; whether to fetch RY8B2's logs.
  sdlports does not recommend a power-on just for the fetch: by the letter it cannot change B8.
- Witness frames: tests/harness/witness-ftp-check.sh on the staged set before this commit. No audio segment and no save is
  committed.

## 11. Addendum: RY8B2's logs, fetched (2026-11-21; information only; the sec. 10 ruling stands)

### The fetch
- One power-on to fetch the logs the round could not collect: the owner, asked by sdlports, then the direct OK in my session
  at 03:11Z. I held rig.gateway2000.plug, services paused its ping, and vcctrl armed a light watch.
- Relay-on 03:12:21Z. `vcctrl get-file RY8B2.LOG STDOUT.TXT RY8B2SDL.LOG --stay --from C:\DOSAGS` ran at 03:13:51Z.
  `--stay` skips the return reboot that failed in RY8B2's collect. Pull finished 03:15:03Z; power OFF 03:15:10Z, 0 mW,
  164 s on mains. The stick was quiet (vcctrl).
- Collected into RY8B2-2026-11-21/fetch/: RY8B2.LOG (sha256 f9dfe1b83266...) and STDOUT.TXT (affe1197e466...), with
  FETCH-LOG.txt, get-file.out, file-status.json and SHA256SUMS.
- RY8B2SDL.LOG was refused by get-file as "not in the target's own DIR of C:\DOSAGS": it was never written.

### What the log says
- binary_sha12 f42436aadd7b, build_dirty 1, exit_code 0, room 35, msgskip n=1, render dest 640x480. The scale2 line reads
  on=1 break=0 verify=0, narrow 4310 / full 5.
- Whole-run 31.69, steady 32.21, fps_p50 39.96.
- frames_skipped 592 of 5002: 88.16% displayed.
- loop_ms 156,877 (about 125,000 in RY's other cells).
- silent_irqs 323: 317 silentirq lines at ticks 4051-4895, all in play. overwrites, underruns and late_writes are 0.
- stalls100: 160 stalls, 61.2 a minute, 50,316 ms in total, longest 821 ms.

### The reading
- ry-read.py, on a scratch copy with the fetched files: VOID in either window. BLASTER.TXT and the stick records were never
  collected.
- On its figures, RY8B2 is NOT MET on every term. B8 stays NOT MET.

### Information
- Both cells of RY's second 2x block degraded late in their runs:
  - RY32B2: 238 skipped frames and 13 silent IRQs at ticks 4762-4817;
  - RY8B2: silent IRQs from tick 4051, and a run 25% longer.
- After RY8B2 the 486 showed no picture, and its collect reboot did not happen.
- The cause is not established.

### What follows
- 2x is PARKED (the owner, via sdlports, bus decision-draft 01M7Y1B8GJSNGWWFEYM8M8HW5D): it stays opt-in, default off,
  with no more 486 time this week.
