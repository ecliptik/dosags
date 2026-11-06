# dosags -- next work order (ADOPTED 2026-11-04)

Drafted by the dosags session after the 2026-11-04 review, with the hub
coordinator's (sdlports) view folded in and its review fixes applied. It
continues PLAN-GATES.md, whose gates were MET on 2026-09-30 (fdbaf461); it
does not change any bar or ruling. ADOPTED by the operator directly in the
dosags session on 2026-11-04 ("adopt the plan, start the release build
switch"); step 1 starts the same day. Decisions 2-4 below are still open.
Every power-on is still its own operator ask. ASCII only.

## Where we are (2026-11-04)

- Gates S8 / S16 / S32 (S32P) MET x2 at the PLAN-GATES bar, sound on,
  Mach64, 486DX2-66; a harness-scored 640x480 capture listen per depth;
  WB arm PASS at S8 / S16 / S32P (WBC8R / WBC16R / WBC32R). Caveats on the
  record: evidence spans four binaries; n=2; whole-run margins 0.06-0.15;
  the bar cells and CAPS8 had the ~89-cent-sharp OPL3 table (fixed since,
  3aee50b4; pitch is not in the bar). OPL3 pitch with the fixed table
  is confirmed on the 486 at S16 and S32P (CAPS16 / CAPS32R, +1 cent) and is
  depth-independent: one opl3_sink F-number table serves every colour depth.
  S8's capture scorer (capture-check.py) has no pitch check, and none is
  claimed there.
- D2 (cold-start latency <= 1.0 ms) FAILED as registered: 4.30 ms median.
  It stays failed on the record; it is not re-registered.
- Main 1c1bcaa5; landing binary af3f0824499e (0348-0350, byte-identical to
  lab-s8's build). No commits since 2026-09-30 (operator pause, lifted
  2026-11-04).
- PLAN-GATES said release packaging starts the day after the third gate
  (2026-10-01). Not started: there is no release build switch, no
  `make dist`, and the phrase TEMPORARY DIAGNOSTIC appears in 30 patch
  files (21 in patches/ags, 9 in patches/SDL; PLAN-GATES counted 20).
  Some of those files remove or fold an earlier diagnostic rather than add
  one; step 1 settles the real list.
- Stale: STATUS.md's yaml (still says 32-bit is "PERFORMANCE-BLOCKED on
  the 486 tier"), README Status/Build, and in the hub COMPATIBILITY.md
  (09-22 figures) and the ports.yaml notes (sdlports owns and is drafting
  the hub rows).
- Hub: 4 commits past the pin, docs and ports.yaml only (05d5e9b
  harness-lessons.md, plugin 1.0.99). Optional pull; nothing gates on it.

## Rig (vcctrl dinspect 2026-11-04, SYSINFO.TXT fetched and verified)

dinspect ran (job scan-20261104T174839.141Z, PGSB boot); SYSINFO.TXT was
fetched by pull-20261104T175212.110Z (614 B, sha256 2d0c8447..., dated
11-04-26 on the card) and matches the camera read field for field:
486DX2 ~66 MHz with FPU; 640 KB + 47 MB extended (48 MB); UniVBE 6.70
(VBE 3.0) on an ATI Mach64 CT (1002:4354) with 2 MB; PicoGUS hardware 2.0
on firmware picogus-sb-dbopl3 v4.1.1 (pgusinit 3.9.0), SB 2.0 at
A220 I7 D3, MPU-401 at 330, OPL at 388; MS-DOS 6.22; EMM386 NOEMS.
Against the 09-30 gate cells (fixture lines name the PGSB boot): same
boot profile, same firmware and IRQ/DMA. R1 is a confirmation, not a
re-baseline. (dinspect does not split XMS from EMS; NOEMS is from the
repo copy of CONFIG.SYS, not read off the card.)
Open rig items, to settle before the R1 power-on ask:
- The WaveBlaster daughterboard is not proven by an inventory (the
  PicoGUS MPU answers without one). It was audible on 2026-09-29 (WBC
  cells scored PASS on the capture). R2's GR16WB re-confirms it; R1 does
  not depend on it.
- VGA capture stick: moved by the operator to usb3-port2 (the
  controller shared with the room camera), re-enumerated ~09:53 PST
  2026-11-04, locked with a live picture. Stability unproven (September
  re-seats held 35-67 min). Every cell needs the capture and camera
  witness: before the R1 ask, vcctrl re-checks dmesg and video_state and
  reports no USB error or disconnect over a span longer than the R1 round
  (90+ min), with both devices on the shared controller.
  MET 2026-11-04 14:15 PST (vcctrl): no USB error on the stick since the
  09:52 move, ~4 h 23 min on one device number, spanning a Gateway power
  cycle and a vcctrld restart; video_state device_present true,
  decode_errs 0, fast_failures 0. Re-check on the day of the R1 ask.
  vcctrld 8e291c4 (deployed 14:15): each send/get now waits ~4-5 s per
  file for the target's batch -- budget it in R1's staging time (an
  18-file fetch is ~1.5 min slower). R1 is that fix's first hardware use:
  the R1 result attaches the vcctrl job log for every send/fetch, notes any
  `settle` warnings, and checks the screen witness for truncated commands.
  First live use 2026-11-04 14:19-14:23 PST (vcctrl, operator-approved,
  psdoom files): 3-file pull, every command whole, 4.4-4.7 s per file; the
  stick stayed on USB through the power cycle. R1 is still its first use
  with sends to the card.
  Every R1/R2 cell carries a run-time witness of the boot profile's BLASTER
  value (PGSB: "A220 I7 D3 P330 T3", the menu default as of the 2026-11-04
  dinspect; e.g. a profile_witness value as doskutsu uses), so a changed
  default VOIDs the cell instead of being measured. Budget 22-30 s for an
  occasional slow mTCP FTP login per transfer.
  Done 2026-11-04: profiles/dosags.yaml profile_witness is filled
  (BLASTER = "A220 I7 D3 P330 T3", one-way). Nothing in this repo reads it
  yet, and run-hw.sh has no BLASTER witness. Each R1 cell therefore records
  the value at run time (a RUN.BAT line writing %BLASTER% to a file
  fetched with the logs) and VOIDs on a mismatch. That line goes into the
  pre-registration.
- Caps Lock is ON at the target (logged by both scan jobs, left as is).
  The R1 WARMUP checks it before any staged command is typed.

## Work order (recommended)

### 1. Release build switch (worker, no rig, ~1 day)

One compile-time switch, `make DOSAGS_RELEASE=1` -> `-DDOSAGS_RELEASE`
(in AGS_CXX_FLAGS_BASE, so the release exe gets its own binary_sha12;
built in build/ags-release against the same SDL sysroot). The 2026-11-04
inventory (every DOS-PORT instrumentation path, its gate, default and
cost) decides what it does:

Compiled out in the release flavour (as built, ags 0351):
- every tick-timing scope, manual bracket and record (dos_port_tick_timing.h:
  constant-false fine test, empty RAII scope), incl. 0315's coarse scopes,
  and the tickstats_* quit lines;
- 0316's per-tick log (DOSAGS_TICKLOG is not read; the room/input event
  sites keep a null-pointer test);
- 0230's work-vector snapshots, per-tick loops and work scope= lines (the
  counters themselves stay: integer adds, and the persec series reads them);
- the stallwhat and skipframe attribution;
- the per-call brackets for script file I/O, object setup, screenshots and
  8-bit fade steps;
- the periodic rbstruct / dirtypresent / bgstruct / biggui lines;
- the quit-time counter dump (everything between the phase aggregates and
  the yardstick) except presentverify;
- the DOSAGS_TICKSTATS_FINE, DOSAGS_TICKLOG, DOSAGS_FLIP_INSTR and
  DOSAGS_CLOCK_CROSSCHECK reads.
Not compiled out (deferred, judged not worth a patch now): the other
diagnostic-only env hooks (FADE_TRACE, the *_VERIFY and *_SHADOW checks,
FORCE_DARKEN, DISABLE_COLORMAP_HOOK, SKIPTEST, MIDI_SILENT_CHIP,
MIDI_NO_BACKEND) -- each is a cached getenv and a branch when unset; the
one-shot startup / room-load timing brackets; the midilate line (rare, on a
>100 ms MIDI gap).

Kept in the release flavour:
- RUNMANIFEST and everything gatebar.py and capture-check3.py read: the
  0093 yardstick (DosTickStallScope: tick_rate_steady, fps_basis, stalls),
  tick_rate / frames_skipped, build_dirty, audio_vital_status and its
  counters (incl. SDL 0190 / 0250), the MIDI fragment's clk= and midi=,
  the silentirq / startlat lines, upstream "Now in room" / "Playing
  sound" / "Playing music" log lines (via --log-stdout);
- what the DOSBox-X ratchet runs on: journeys (0250), presentverify
  (env-gated), the freeze instrument (env-gated; the screen-alias rows
  freeze), BREAK_0193 (a ratchet control), MISTALL / MI_RENDER_DELAY
  stress (env-gated), SDLDBG.LOG (SDL side, DOS_PORT_LOG);
- harness test switches, all default off: MSGSKIP, RANDSEED, TICKCLICKS,
  TAS_AUTO_EXIT_TICK, LOG_TAG / SCENE, FORCE_COLOR_DEPTH, MAX_SCALE;
- every functional kill switch (DIRECT_VSCREEN, DIRTY_PRESENT, RP_FAST,
  PAKHANDLE, ...), the one-shot lines midistream, pcmcache, rpcache,
  uclockwrap, video_banked_mode.

Default changed in the release flavour only (operator 2026-11-04):
DOSAGS_FIXED_TIMESTEP defaults ON, because every gate cell ran with it
(run-hw.sh sets it); env DOSAGS_FIXED_TIMESTEP=0 still turns it off. The
instrumented flavour and the ratchet keep today's default.

Not in the switch: no SDL-side compile define (SDL is built by the hub
fragment). The SDL-side always-on costs (0015's present-phase timer reads,
0250's ISR drain timing) are unmeasured; they stay, and get a local
patches/SDL gate later only if a measurement asks for it.

Diagnostic retirement (step 1b, same pass, both flavours): the TEMPORARY
DIAGNOSTIC marker sits in 30 patch files, but only one live family
carries it: AUDIOPRB (7 timers; off by default since ags 0218 / SDL 0199,
behind SDL_HINT_DOS_AUDIO_DIAG_TIMING; no gate or scorer reads it). Of the
30: 8 add it (ags 0059, 0071, 0072; SDL 0136, 0141, 0145-0147), 7 fold or
gate it (ags 0061, 0062, 0069, 0070, 0073, 0218; SDL 0199), 1 removes one
(SDL 0137 reverts 0136), and 14 only carry the phrase in diff context. 1b
removes the AUDIOPRB family with new patches (ags + local patches/SDL),
leaving the one "audioprb timing=off" line out too. PLAN-GATES' count of
20 is not reproducible from the tree.

Scorer contract: on DOSBox-X, both scorers score a release-flavour log
(gatebar.py on main; capture-check3.py from `git show
lab/wb:LAB-WB-data/capture-check3.py`, the worktree is retired). If a
field a scorer reads goes missing, it goes back into the release flavour.

Done when: both flavours build; the instrumented flavour's stamp and bytes
are unchanged by the switch patch except where 1b removes code; the
nightly DOSBox-X ratchet passes on both (the release run through
ratchet.sh on a release build); both scorers score a release-flavour log;
the release exe's size, sha and stamp are recorded.

Status 2026-11-04: step 1 DONE (ags 0351, 23230d06; evidence
tests/harness/results/REL1-2026-11-04). Step 1b DONE locally with ags
0354 (ags 0352/0353/0354, SDL 0269): full ratchets 20261105T000223Z
(instrumented 7e5dfe26f272, 8,636,055 B) and 20261105T005648Z (release
a1dba5d61624, 8,598,425 B), both 41 pass / 0 fail. No scorer reads
audioprb or rb_max_spr_* (git grep, main and archive/lab-wb), so the
scorer contract check was not re-run for 1b. Evidence and the superseded
interim runs: tests/harness/results/REL1B-2026-11-04.

### 2. `make dist` (worker, no rig, ~0.5 day)

A zip: release exe (stubedit stack recorded), CWSDPMI.EXE + its licence,
LICENSE, Artistic 2.0 text, THIRD-PARTY.md, a player README (setup, sound
backends, BLASTER/ULTRASND, known limits, the D2 note). No game data. A
check that the zip contents match LICENSE-REVIEW.md and THIRD-PARTY.md.
No tailnet hostnames in anything tracked (forgejo.example.ts.net
placeholder).

Status 2026-11-04: DONE locally. `make dist [DIST_VERSION=..]
[DIST_REPO_URL=..]` builds the release flavour. scripts/make-dist.sh
stages 11 files (8.3 names, CRLF text) into build/dist/dosags-<V>.zip.
scripts/check-dist.sh then checks the zip against THIRD-PARTY.md's
dist-files table (both directions) and LICENSE-REVIEW.md's sections. It
also checks:
- that AGS.EXE is byte-identical to the release exe;
- the MANIFEST.TXT hashes;
- ASCII/CRLF, with CWSDPMI.DOC and FTL.TXT exempt from the ASCII check
  as unaltered upstream text;
- that README.TXT carries the FreeType, DJGPP, CWSDPMI and Modified
  Version notices;
- tailnet hosts and game-data names.
Each of these was shown to fail on a broken zip. AGS.EXE ships unmodified
with the stub minstack the build leaves (512 KB, the DJGPP default), the
same stack every gate measured; MANIFEST.TXT records it from the stub.
OPEN for v0.1:
(1) there is no public source URL yet (dosags is not on GitHub), so the
    zip prints NOT RELEASABLE and `check-dist.sh --release` fails;
(2) whether to set an explicit minstack: it would change the measured
    binary.
The dev zip a1dba5d61624 passes the check.

### 3. Status surfaces (worker, no rig, same day as 1-2)

STATUS.md yaml + figure table from fdbaf461; README Status and Build
rewritten from STATUS.md. I check sdlports' hub text (COMPATIBILITY.md
row, ports.yaml notes) against fdbaf461; neither of us edits the other's
files.

Status 2026-11-04: DONE locally. STATUS.md has a new yaml block and a
"Where it stands" table. The table holds the S8/S16/S32P bar cells,
capture listens and WB arm from fdbaf461's evidence, plus D2, the release
flavour and `make dist`. The older cell tables stay as the record.
README.md: Status, Target Hardware, Build and Components are rewritten
from STATUS.md, and the tailnet host is replaced (doskutsu and dossage
link to their public GitHub repos; the rest use the
forgejo.example.ts.net placeholder). dos_status stays PLAYABLE, the
hub's value. The hub text was checked read-only and the findings were
sent to sdlports. Still to settle: tailnet hosts in three working
configs (.claude/settings.json, skills-lock.json,
tests/harness/audio-rec.py), which were asked about rather than changed.

### 4. Rounds R1 and R2 (rig, TWO separate operator asks, <= 6 cells each)

Every pre-registration (<= 15 lines, PLAN-GATES procedure) names the
09-30 comparison figure and the binary it came from (e.g. GL16A/B on
8249193ed041), so no figure is compared across denominators. It also says
that both ABBA flavours carry step 1b (ags 0352/0353, SDL 0269) and ags
0354: the ABBA compares two such builds and cannot isolate 0269's change to
SDL_DOSOpl3WriteRegister (the OPL hot path, also replayed from the SB ISR),
and every GR / CAPR comparison against a 09-30 figure includes both. 0354
adds one DOS write (a stdout commit) per room load, inside the existing
room-load stall. Which S8 figures include it: the fixture's only room
load (room 35 via --startr) is in the pre-loop (GL8A: load_end 630 ms,
preloop_ms 634), so tick_rate_steady, stall_ms and the stall list exclude
it -- but the WHOLE-RUN tick_rate's denominator includes the pre-loop
(GL8A: 5002 ticks / 39.26 = 127.4 s vs loop_ms 125.9 s), so a commit of C
ms lowers whole-run by ~39.26 x C / 127400 (30 ms -> -0.009; S8's
whole-run margins have been 0.01-0.15). The ABBA is unaffected (both arms
carry 0354); a comparison with GL8A/B is not. The cost is measured
directly on the 486 by the DOSAGS_XT load_begin -> load_end bracket in
STDOUT (both flavours; it spans the commit): GL8A read 212 -> 630 ms. Void rule
as PLAN-GATES. Sound on, OPL3 pitch fix in both flavours.

R1 -- does the release flavour carry the gates (PLAN-GATES lever 2):
- WARMUP + rig health (capture, camera, USB4VC counters).
- RELEASE ABBA on the S8 fixture (original S8H protocol): instrumented vs
  release flavour, same commit. The ABBA decides whether gate cells run on
  the release flavour from then on. Prediction: release >= instrumented on
  both tick figures. The comparison figure is GL8A/B on 8249193ed041.
- No D2b in R1. The inventory showed the D2 timing (and LABZ) came from
  lab probe builds (lab/mmd: lab-mmd/gate/probe-coldstart3rd-on-0348*.diff),
  not from main in either flavour. A D2b reading needs a probe binary as a
  third arm, which R1's 6 cells do not hold. D2 stays FAILED as
  registered; a D2b cell can ride on a later round with the probe build.
- CAPR8 (operator 2026-11-04, option (a)): the release build's end-to-end
  audio check at S8 -- a 640x480 capture listen at Trilby room 35 scored by
  capture-check.py exactly as CAPS8 ran it (lab/wb caff563d, sha256
  33133f390a4b2338...; reference trilby_sound11.wav sha256 3951702f...,
  tests/harness/REFERENCES.md), on the release exe. No pitch claim at S8:
  that scorer has no pitch check, and room 35's ambient masks the music.
  Comparison figure: CAPS8 on 8249193ed041 (main 553588d4) -- K1 0 zero
  frames, K2 worst 24.7 dB (< 25), K3 NCC 0.41 vs null 0.14, K4 >= 52.8 /
  47.8 dB, K5 clean.

Pre-registered 2026-11-05 (before any data): WARMUPR1, R1I1 R1R1 R1R2 R1I2 (A instr 7e5dfe26f272,
B release a1dba5d61624, main f2228d5e), CAPR8; scorer tests/harness/abba-r1.py; driver
build/ws/roundR1/driveR1.sh (untracked, as round BATCH's), cap 80 min. Operator rule 2026-11-05:
EQUIVALENT if mean(B) >= mean(A) - 0.10 on both tick figures (NOT SEPARABLE if |A1-A2| >= 0.30);
both B cells MET count as the release flavour's S8 x2, so R2 drops GR8.

DONE 2026-11-05 (tests/harness/results/ROUNDR1-2026-11-05): ABBA EQUIVALENT (whole-run B - A
+0.010, steady -0.005; drift 0.02 / 0.04), R1R1 and R1R2 MET -> release S8 x2; CAPR8 PASS. Gate
cells move to the release flavour. Capture stick failed mid-round (R1I2; off USB 16:59:23-17:02:07Z, back
without the approved sysfs reset) -- the cable/stick needs a fix before R2.

R2 -- only if the ABBA says the gate cells move to the release flavour (it did; GR8 dropped):
- WARMUP; GR16, GR32P (gate bar x1 per depth, original protocols)
  and GR16WB (WB arm x1 at S16), all on the release exe. Comparison
  figures: GL16A/B and GL32A/B on 8249193ed041, WBC16R on
  ef123dba0adf. Prediction: each at or above its 09-30 figure.
- If a depth falls out of band, it gets one x2 re-run on the same binary
  before the release; the 09-30 claim is not withdrawn by an x1 miss, and
  the miss is recorded.
Pre-registered 2026-11-05 (before any data): WARMUPR2, GR16WBP + GR16WBR (the WB arm needs its
same-binary poll control, so GR16WB is a P+R pair), GR16, GR32P, all on release a1dba5d61624; driver
build/ws/roundR2/driveR2.sh (untracked), cap 75 min. Power-on bar (operator 2026-11-05): a named
capture stick/cable swap, then 90+ min clean in the Pi's kernel log from it (vcctrl), then a close
watch on the warm-up (the driver stops on a non-nolock capture STALE or no capture device).
DONE 2026-11-05 (tests/harness/results/ROUNDR2-2026-11-05): GR32P MET (39.29 / 40.12), GR16WB PASS
(D 0.744), GR16 figures MET (39.27 / 40.11) but no screen witness (camera pointed away, capture card
does not lock 512x384) -- one GR16 re-run with the camera on, before v0.1. DONE in R3 2026-11-05:
GR16R3 MET (39.29 / 40.12, 99.48%), camera CLEAN. Operator waived the
capture bar for this round; the stick did not drop (one corrupt frame, outside every scored window).
R4 ("as shipped", 2026-11-05, tests/harness/results/ROUNDR4-2026-11-05): DIST1 plays at the gate rate as shipped
(39.27 / 40.13, 99.56%, camera CLEAN) but FAILs as registered on a walk-dependent proxy (no "Playing sound 3";
effects 9/10 played). GUSC16 FAIL: the GUS backend runs but K2/K3/M1/M2 fail and underruns=39631 (09-15: 0) --
a GUS PCM regression to locate. ADLC16 VOID: without BLASTER the engine disables ALL audio, so OPL2 music never
starts -- AdLib-only / MPU-only players get silence. Both are v0.1 blockers for the README's sound claims;
README.TXT now states the limits. Next: fix audio init without SB, find the GUS regression, re-run both cells.
G1/G2 (2026-11-06): model C (ags 0355) PASSES on the 486 -- ADLC16B (PGADLIB, OPL2, auto): K1/K2/M1 +0 cents/M2 0.763;
MPUNB16B (MPU proxy, wb): M1 -1 cent, M2 0.872. The hub gus-pcm-fix holds (underruns 0, no exhaustion), but GUS sound effects
are still not heard (K3) and SDL 0270 (8-bit sign flip) is FALSIFIED on the rig: it must not land. Next for GUS: D4
(REAP_GRACE) and the GUS MIDI path (gus_sink.c: K2 gap, -24 cents). README.TXT keeps 'prefer opl3 or wb' for GUS.
If the ABBA says the release flavour is not equivalent, R2 does not run:
v0.1 ships the release flavour only if the ABBA shows no loss; otherwise
the operator decides between shipping the instrumented flavour (the 09-30
evidence) and a lab slice on the difference.

### 5. v0.1 release (after R1, and R2 if it runs, pass)

In dosags: the tag, the dist zip as the release artifact, vault
`plog -c release`, kanban next line. Via sdlports (hub files, theirs):
gallery entry, ports.yaml dos_status and notes, COMPATIBILITY.md row.

### 5a. v0.1 -- RELEASED 2026-11-06 (operator, via sdlports)

Tag v0.1 on f0f9275c; zip c0c6fe00...; AGS.EXE c754df64babd. Record: DIST2 PASS; S16 MET x2; S32P and S8 MET 1 of 2
each (V1 misses the whole-run band only); MMD 99.90% x2. No third gate reading before release (operator).

Post-release items, in order:
1. **Gameplay fps** (operator 2026-11-06: "measure gameplay fps too"): MMD in play from the room-1 save x2,
   Iowna and Shards in play (never measured on the 486), 5 Days across rooms -- engine-driven walking, frames
   displayed over the play window. Every scored figure so far is one room or MMD's idle character select.
2. **Start-up variance** (S32P / S8 whole-run misses in V1): pre-loop start-up rose from ~620 ms (11-05) to
   926-1,004 ms (V1) on the same scene. Lead: C:\DOSAGS accumulates every cell's <TAG>.LOG and <TAG5>SDL.LOG
   (run-hw.sh never deletes there; ~670 cells), and DOS directory lookups are linear. Next round's warm-up lists
   the directory; a cleanup (move the collected logs to a subdirectory) needs the operator's OK.
3. Cleanup patch: 0363's dos_englev_shadow() definition under #ifdef DOSAGS_VMTRACE (dead code today).
4. GUS (v0.2): PCM effects missing, MIDI gaps and pitch.

### 6. After v0.1 (low priority, spare rig room only)

- PLAY486 / MMD in play (LAB-MMD 50.4): fills spare room in a round after
  the cells above; never displaces them.
- D2: no rig time of its own; a D2b cell (lab/mmd probe build on the
  current main) can ride along on a round that has room.
- Still parked: MMD sound on, ViRGE / Cirrus, tracker music, P3 / PROF486
  / TAIL / SCRIPTH.
- Retired: the Vibra16S WB lane. Operator 2026-11-04: the Gateway 2000 has
  no Vibra16S fitted, only the PicoGUS.

## Decisions for the operator

1. Adopt this order (release work first, then R1)? sdlports recommended
   release first as well; today's pick was the OPL3 fix for doskutsu and
   dossage.
2. Gateway time: doskutsu and dossage have no rounds queued; psdoom is a
   separate session. Does psdoom want the Gateway?
3. DECIDED 2026-11-04 (operator, via sdlports): archive + retire. Done:
   build/archive/dosags-labs-2026-11-04.tar.xz (untracked, never
   committed), sha256
   aa63f8671a0680285cde32c06799afeba80cb0505482f0d06f738855dd9f3d6a,
   37,303,760 B, 3010 files / 354,103,334 B unpacked (manifest beside it;
   tar -t matches it, tar -d clean). It holds the untracked data of
   lab-metric / lab-mmd / lab-wb, main's GATE0216-2026-09-25 (removed from
   main after the check), and the gitignored raw results found only in
   lab-journeys / lab-metric / lab-mmd. Local tags archive/lab-metric-,
   lab-mmd-, lab-wb-, bench8-2026-11-04 (lab-journeys keeps its 09-26
   tag); not pushed. Worktrees lab-journeys and bench8 removed;
   dosags-nightly is never touched.
4. Power-on: two separate asks through sdlports. R1 (release ABBA +
   CAPR8) once steps 1-3 are done and the rig checks are clean; R2 (gate
   bars on the release exe) only if R1's ABBA calls for it.
