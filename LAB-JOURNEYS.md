# LAB-JOURNEYS -- journey metrics, the dosags ratchet file, then Gate S8 (lab only)

Worker: `dosags-lab-journeys`, worktree `~/git/dosags-lab-journeys`, branch `lab/journeys`,
DOSBox-X display 231, patch range ags 0250-0269 / SDL 0220-0229. LAB ONLY: no hardware, no
vcctrl, no power. Plan of record: PLAN.md "Next campaign (operator direction 2026-09-23)", and
the hub's `plans/LESSONS-CLAUDE-AI-PERF-2026-09-23.md` sections 1, 3 and 6.

**Every DOSBox-X figure in this file is a count or a ranking, never a rate claim.** DOSBox-X
predicts pixel accounting and rates not at all (PLAN.md "Instrumentation inventory and hazards").

## 0. Recovery of the stopped predecessor's work (2026-09-23, restart)

The previous instance of this worker was stopped (it launched DOSBox-X during a coordinator
hold) before it committed anything or wrote this file. Everything below was left uncommitted
in the worktree or committed only inside `vendor/` (which is gitignored). This section records
what it left. **V** = verified by reading the file or the log in full. **I** = inferred (intent,
or anything the files do not state).

### 0.1 What was left, and where

| item | where it was | status |
|---|---|---|
| ags 0250 "WIP journeys" (+761 lines, 11 files) | commit `8d2c2fc10` in `vendor/ags` only; never exported to `patches/ags/` | V: read in full |
| ags 0251 "WIP lab stress probes" (+44 lines) | commit `84e7f0311` in `vendor/ags` only | V: read in full |
| SDL 0220 "count the mouse presses the level poll never saw" | `patches/SDL/0220-*.patch` (untracked) AND commit `08664280e` in `vendor/SDL` | V: the file's body is byte-identical to `git format-patch -1 08664280e` apart from line 1 (the `From <sha>` line: the file says `52ea67416`, the vendor commit is `08664280e`; I: the commit was re-made once, e.g. by an `apply-patches.sh` run, after the file was written) |
| `tests/harness/run-dosbox.sh` edit (+23/-2) | working tree | V: see 0.4 |
| `tests/harness/journeys.py`, `click-cell.sh`, `drive-clicks-dosbox.sh`, `lab-cell.sh` | untracked | V: read in full, see 0.3 |
| results JC40, JC6Q, JC6H, JMSI, JMSP (all `-2026-09-23`) | untracked | V: see 0.5 |

The three vendor commits were exported to scratch before anything else was touched.

### 0.2 What ags 0250 (WIP) does -- V, read from the code

`Engine/platform/dos/dos_journeys.{h,cpp}` plus hooks. One clock: `uclock()` minus
`dos_port_engine_start_uclock` (patch 0042's anchor). Nothing prints while the game runs;
`dos_journey_emit()` writes to RUNMANI.LOG from `quit()` next to the patch 0093 yardstick.
Every journey ENDS at a present ATTEMPT (`SDLRendererGraphicsDriver::Present`, any exit, via a
scope guard: pixels pushed, palette only, or skipped as unchanged).

| journey | start | end | sub-intervals |
|---|---|---|---|
| boot | engine start (t=0) | first present after the first fade-in ends (or the fade-in of `DOSAGS_JOURNEY_TITLE_ROOM`) | to_fadein_end, fadein_end_to_present |
| room | `NewRoom()` / `new_room()` request (first of the two; a changed target is `retargeted=1`) | first present after the new room's fade-in ends | to_fadein_end, fadein_end_to_present |
| save / save_restartpoint (slot 999) | `SaveGameSlot()` (or `save_game()` entry when no script request, e.g. a dialog) | first present after the file is written (marked BEFORE the GameSaved event) | write_ms, done_to_present |
| load | `RestoreGameSlot()` (or `try_restore_save()` entry) | first present with `!screen_is_faded_out` and no fade-in running, after the state is restored (marked BEFORE GameRestored) | restore_ms, done_to_present; `room_changed`, `failed` |
| click / click_sim / key | the SDL event's own timestamp (the pump that produced it) | first present after the engine dequeues it | poll_to_dequeue, dequeue_to_present; `dropped`, `ts_fallback` |

Also emitted: `journey_summary` per kind (n, nearest-rank p50/p95, max, unfinished,
superseded, retargeted, cleared, overflow); `journey_input` (SDL 0220's driver vs seen press
counts, `lost_clicks`, keyboard IRQ bytes vs drained bytes); `stallshare` (whole 1 s windows
from the first present with fewer present attempts than `DOSAGS_JOURNEY_FPS_FLOOR`, default 39;
empty seconds count as below; a `nojourney` variant drops windows with a boot/room/save/load
journey pending); `stalls100` (present-to-present gaps > 100 ms, n, per minute, max, first 48
listed as `stall100` lines).

### 0.3 The harness scripts -- V, read

- `journeys.py <dir> [--host-clicks LOG]`: prints the journey table, then second witnesses:
  room start vs patch 0042's `room_transition ... event=start` line; stall share recomputed from
  the `persec` rows (a consistency check, not equality); the three click counts (host injected /
  driver / engine). Ends with `RATCHET key=value` lines. Exit 1 if there is no `journey_basis`
  line.
- `drive-clicks-dosbox.sh STAGE LOG ...`: waits for "Now in room", focuses the DOSBox-X window
  once, takes the mouse capture with one click, then N press-hold-release clicks (one xdotool
  process per click, so the hold is the hold) and N key taps, logging every host press with a
  host timestamp. `--through-title` clicks through 5 Days' intro text and START; `--wait-room`.
- `click-cell.sh OUT ...`: one interactive `run-dosbox.sh` run on display 231 with the driver
  above, finds its OWN dosbox-x by process ancestry, stops it when the manifest is complete,
  copies the evidence and runs journeys.py.
- `lab-cell.sh OUT <run-dosbox.sh args>`: one headless cell, keeps RUN.BAT/RUNMANI/STDOUT/
  SDLDBG/AUTOPLT and the run log.

### 0.4 The run-dosbox.sh edit -- V; superseded by main

It replaced the watchers' `ps ... | head -1` stage lookup (the lowest-PID dosbox-x on the host)
with an `own_stage` that walks the parent chain to the runner's `$$`. Main landed the same fix
independently (`7a011759`, `5d6acfac`, `ba3fd8c6`: ancestry-based `own_stage`, exact-stage kill,
EXIT cleanup, the host-wide lock, the occupied-display refusal). On the rebase main's version is
kept whole; the predecessor's diff is kept as `tests/harness/results/JREC-2026-09-23/
run-dosbox-predecessor.diff` for the record.

### 0.5 The results -- counts V, timings NOT COMPARABLE

All five ran on binary `binary_sha12=6b561d6787eb`, `build_dirty=1` (ags 0250/0251 existed only
as vendor commits), `--fixed-timestep --interactive`, 5 Days a Stranger `--startr 3`,
`DOSAGS_TAS_AUTO_EXIT_TICK=4000`, `DOSAGS_PRESENT_VERIFY=1`. They ran 14:08-14:24 local, while
other workers' DOSBox-X runs overlapped (before the hub lock existed) and, per the coordinator,
partly after a coordinator hold. **Every timing-dependent figure from them (journey ms, p50/p95,
stall share, stalls/min, fps, tick rates) is NOT COMPARABLE** and is kept only as evidence that
the fields populate. Pure counts are fine.

| cell | condition (RUN.BAT + CLICKS.LOG) | host presses / driver / seen / click journeys | lost | keys host / journeys | kbd irq/drained | stale_frames |
|---|---|---|---|---|---|---|
| JC40 | no throttle; 20 clicks x 80 ms hold (+1 capture click), 5 keys | 21 / 21 / 21 / 21 | 0 | 5 / 5 | 10 / 10 | 0 |
| JC6Q | `DOSAGS_MI_RENDER_DELAY_MS=150` (ags 0251, ~6 fps); 20 x **20 ms** hold, 5 keys | 21 / 21 / **4** / 4 | **17** | 5 / 5 | 10 / 10 | 0 |
| JC6H | same throttle; 20 x **400 ms** hold, no keys | 21 / 21 / 21 / 21 | 0 | 0 / 0 | 0 / 0 | 0 |
| JMSI | (I: MIDI stall cell, ISR arm) | empty run.log, no stage, no result | | | | |
| JMSP | (I: MIDI stall cell, poll arm) | empty run.log, no stage, no result | | | | |

What the counts show (V): the lost-click counter has power -- quick clicks at ~6 renders/s are
lost (17 of 21), the same clicks held 400 ms are not (0 of 21), and at the unthrottled rate an
80 ms click survives (0 of 21). The driver saw every host press in all three cells (21/21), so
the loss is between the driver and SDL's level poll, exactly where SDL 0220 says. Every seen
click became a click journey (seen == click n), no journey was unfinished, superseded or
cleared, no event used the timestamp fallback. Keys: 5/5, no bytes left undrained. This is the
real-hardware "hold the mouse down across a poll" behaviour (memory note, 2026-09-15/16)
reproduced on DOSBox-X by the throttle.

What the cells do NOT cover (V): room, save and load journeys are n=0 in all three (one room,
`--startr 3`); only the restart-point save (slot 999) ran. `boot` ended in room 3 (the
`--startr` room), not a title. No `--sb-live` cell exists. JMSI/JMSP (I: named for the MISI/MISP
stall cells on main, which used the same `DOSAGS_UR3_STALL_EVERY` probe as a throwaway diff)
produced nothing; I infer they were started at the moment the worker was stopped.

### 0.6 Defects found while re-reading (fixed in later commits on this branch, see section 1)

- `journeys.py` prints `lost_clicks` from the driver-vs-poll difference only. With no mouse
  driver (or a driver the pump never read) it prints `hw=0 seen=0 lost=0` -- a vacuous zero that
  reads as a pass. `hw_checks` must be > 0 and the driver count must equal the host's injected
  count before `lost=0` means anything.
- `click-cell.sh` waited 120 s for its own dosbox-x; under main's lock a queued run waits longer,
  and the cell would give up while its run was still queued. It now takes the lock itself, once
  around the whole cell.
- (I) The click journey starts at the pump that produced the event, not at the physical press:
  a press made during a 150 ms render delay waits for the next pump, and that wait is not in
  the journey. See section 1.

## 1. Journey metrics, finished (ags 0250, SDL 0220, ags 0251, ags 0252) -- 2026-09-23

### 1.1 What changed from the predecessor's WIP

Re-read against the engine at the pinned revision (`Engine/ac/global_game.cpp`, `game.cpp`,
`event.cpp`, `main/game_run.cpp`), asking for each field "what would it print if the journey
failed, and which path lets it":

| path found | what the WIP printed | fix |
|---|---|---|
| `SaveGameSlot()` refuses for disk space (< 2 MB free) and returns before `save_game()` | nothing: the journey stayed pending and the NEXT save's journey started at this refused request (an inflated value, not a count) | the refusal now records a `failed=1` save |
| a failed/refused save or load | a per-record `failed=1`, excluded from n and p95, and no count in the summary -- a ratchet reading the summary saw a clean n | `journey_summary ... failed=N` |
| a second `SaveGameSlot`/`RestoreGameSlot` while one is still queued (`inside_script`) | silently absorbed | counted as `rerequested=`; the journey keeps the first start |
| a click the level poll never saw | no journey, no trace in the journey lines (only the separate `lost_clicks`) | documented in the header; journeys.py's end-to-end `lost_inputs` against the host's own injection log |
| a click that WAS seen waited for the poll | the journey starts at the pump that stamped the event, so up to one pump gap (~170 ms at 6 fps) is invisible | SDL 0220 records each pump's start time in a 16-entry ring; `SDL_DOSInputWaitBoundNS()` gives the upper bound; each input record has `wait_bound_ms`, the summary `p95_upper_ms`/`max_upper_ms` and `bound_unknown=` |
| a freeze that lasts until the auto-exit | no present after it, so no window closes and no stall is counted | `stalls100 ... tail_ms=` (last present to quit), reported, not folded in |
| no mouse driver / counters never read | `lost_clicks=0` | journeys.py prints `lost_clicks=NA` when `hw_checks=0` |
| a driver script that injected nothing | `lost_inputs` would be 0 | the ratchet pins `host_clicks`/`host_keys` to the injected count |

Checked and found sound: a load that re-runs the game (`RunAGSGame` + `load_new_game_restore`)
keeps ONE journey from the first request through the re-run's restore; a room change requested
before a restore is `superseded` by it; a room left before any present after its fade-in ends
at the fade's last present (`ended_in_fade=1`) or is `superseded` if the fade presented nothing;
the keyboard ring overwrites on overflow while IRQ 1 keeps counting, so a lost key byte shows as
`kbd_bytes_undrained > 0`; `current_fade_in_effect()` has one caller (`kAGSEvent_FadeIn`, queued
by `GameUpdateProcessEvents` for every room entry), so every room entry passes the fade hooks.

ags 0251 (the two stress switches) is kept in the series as permanent test tooling, off unless
set: the ratchet's stall/throttle and lost-click cells need it in a reproducible build. Retire
it only together with the ratchet checks that use it (midi-late-stall, midi-stall-fired,
midi-late-throttle, lost-inputs-throttled-held and the lost-input controls).

ags 0252 (new) makes "pcm accounting exact" checkable in every build: `mixed=`, `mixed_zero=`,
`mixed_quiet=` in `audio_vital_status`. The UR8 throwaway diff (2026-09-22) is its origin.

### 1.2 The journeys, as reported, with DOSBox-X values (JAQ1-2026-09-23)

JAQ1: AGS Quest AutoPilot demo, `--fixed-timestep`, clean build `7dffe09f0587` (`build_dirty=0`),
run under the EXCLUSIVE DOSBox-X lock (no other emulator beside it). **DOSBox-X ms are not
hardware predictions**; they show the fields populate and what their shape is. Counts are exact.

| journey | definition (start -> end) | n | p50 / p95 ms | notes |
|---|---|---|---|---|
| boot to title | engine start -> first present after the first fade-in (or the fade-in of `DOSAGS_JOURNEY_TITLE_ROOM`) | 1 | 2590 | room 1; excludes DOS loader, DPMI and static init |
| room transition | `NewRoom()`/`new_room()` -> first present after the new room's fade-in | 8 | 1178 / 1766 | every start = patch 0042's `room_transition event=start` t_ms, diff 0-1 ms (second witness); 1 of 8 `ended_in_fade` (room 1->2) |
| save | `SaveGameSlot()` -> file written (before GameSaved) -> next present | 1 | 76 | write 38 ms |
| load | `RestoreGameSlot()` -> state restored (before GameRestored) -> first present not faded and not fading | 1 | 2151 | restore 702 ms; `room_changed=1` (AQ changes room inside its restore) |
| click / key | SDL event timestamp (its pump) -> engine dequeue -> next present; `wait_bound_ms` = the unseen wait before the pump | 0 / 0 (1 `click_sim`: AutoPilot's synthetic click) | - | real clicks: see the click cells; JC40/JC6Q/JC6H figures are NOT COMPARABLE (section 0.5) |
| stall share | whole 1 s windows with < 39 present attempts | 58 of 103 (0.563); without journeys 0.476 | - | DOSBox-X rates mean nothing for the target; shape only |
| stalls > 100 ms | present-to-present gaps | 14 (8.1/min), max 747; without journeys 1 | - | `tail_ms=432` (last present to quit) |

Also printed per run: `journey_input` (driver presses, seen presses, lost_clicks, keyboard IRQ vs
drained bytes) and, per stall, a `stall100` line with its time and whether a journey was pending.

## 3. Gate S8 (8-bit, sound on) -- lab work on DOSBox-X (operator decision 2026-09-23)

**Bar (PLAN.md "Next campaign"):** Trilby's Notes in play, 512x384x8 centred 1x, pillarbox alias ON
(the S2T2 fixture: hardware steady 39.99, stable 39.91, sound OFF), with sound ON (SB PCM + MIDI, both
OPL3 and WaveBlaster): both tick figures 39.2-40.8, `fps_p50` >= 40, completeness >= 95%, camera
clean, x2 on hardware; audio counters: pcm = expected, `overwrites=0`, `late_writes=0`,
`silent_irqs=0` outside room loads. The bar is judged on hardware only; this section ranks costs.

### 3.1 PRE-REGISTRATION S8L1 (2026-09-23): what sound costs at 8-bit, ranked, on DOSBox-X

**Question.** On the S8 fixture, how much main-loop time per game tick does each part of sound take:
PCM effects (SB mixer pump + stream), MIDI on OPL3 (plan on the main loop, replay in the SB IRQ),
MIDI on the MPU-401/WaveBlaster (poll)? A ranking decides where the first S8 change goes.

**Cells.** `tests/harness/s8-cell.sh OUT ARM`: Trilby `--startr 3`, cfg
`presentation/trilbysnotes/ACSETUP-{OFF,ON}-512X384-ROUND.CFG`, `--fixed-timestep`, exit tick 5000,
host clicks every ~2.3 s (200 ms hold, S2T2's cadence), **FIXED 40k cycles** (`dosbox-x-fixed40k-opl3.conf`;
the wb arm `dosbox-x-fixed40k-mpu401.conf`, new: the fast MPU conf with core/cycles as the fixed OPL3
one), lock SHARED (hub rule bb5482c), display 231. Arms: `off` (sound off), `pcm`
(`DOSAGS_MIDI_NO_BACKEND=1`: effects only), `opl3` (effects + OPL3 ISR replay), `wb` (effects +
MPU-401 poll). Order off, pcm, opl3, wb, wb, opl3, pcm, off (ABBA-style, 2 per arm), binary
`eba15e780f2e` (clean).

**Figures (s8-facts.py), per game tick:** `idle_ms_per_tick` (wait_next_frame), `audio_poll_ms_per_tick`
(catchup_audio_poll: the mixer pump), `update_ms_per_tick`, `render_passes`, `frames_skipped`;
audio: `pcm_unaccounted`, `overwrites`, `silent_irqs`, MIDI late; ags 0250 stall share and
stalls > 100 ms. The cost of an arm = its `update_ms_per_tick` minus `off`'s (the ISR's own time is
inside that difference, since it steals cycles from whatever it interrupts), cross-checked by the
drop in idle.

**Predictions (made before any S8 cell ran):**
1. Ranking of the increment over `off`: **pcm > opl3 - pcm > wb - pcm**, i.e. the PCM effects path
   (8-voice mix + SDL stream + the pump) is the largest single cost at 8-bit, the OPL3 ISR replay
   second, the WaveBlaster poll smallest on DOSBox-X (its 320 us per-byte TX wait is real time, but
   Trilby's music is ~10 events/s).
2. Size: `opl3` costs **0.5 - 3 ms per tick** more than `off` at fixed 40k.
3. Audio counters in every sound arm: `pcm_unaccounted=0`, `overwrites=0`, `opl3` late writes 0.
   `silent_irqs` > 0 only around room loads (none are expected in room 3 play).
**Void if:** an arm's cell does not reach room 3, the clicks do not register (`host_clicks` != the
engine's received count), `build_dirty=1`, or two cells of one arm differ by more than the
difference being ranked (then the ranking is noise and says so).
**What changes next depends on it:** the top-ranked cost is the first S8 candidate change, pre-
registered separately; a sound-on cost under 0.2 ms/tick would mean sound is not what stands
between S2T2 and S8, and the hardware cells below go first.

### 3.2 Hardware cells S8 will need (for the coordinator to batch; NOT run by this worker)

| cell | what | why |
|---|---|---|
| S8H-O1/O2 | Trilby in play, S2T2 command (512x384x8 centred, alias, `drive-walk.sh <TAG> 25 2 80`, 5000 ticks), cfg `ACSETUP-ON-512X384-ROUND.CFG`, PicoGUS SB + OPL3, clean build carrying 0250-0252 | the S8 bar itself, OPL3 arm, x2; counters read from the manifest (0252 accounting, 0250 stall share) |
| S8H-W1/W2 | the same with MIDI to the WaveBlaster (DreamBlaster on the PicoGUS header) | the WB arm, x2 -- depends on dosags-lab-wb's on-time WB transport |
| S8H-A0 | the same binary, sound OFF (S2T2 cfg) | an anchor: S2T2 ran on 0196; 0250's per-present uclock() is new hot-path cost (~5 us/present) |
| S8H-L | Trilby at 640x480, sound on, capture on | the one 640x480 capture listen per depth |

## 4. Follow-ups (open)

- **ratchet.sh per-run lock mode (hub 0655ad7):** at the next subtree bump, mark the FIXED runs
  `lock: shared` and make their `--conf` visible to ratchet.sh's cycles check (today the path is
  relative to `tests/harness/`, because lab-cell.sh runs run-dosbox.sh from there; ratchet.sh reads
  it relative to the port root, so it may read "asserted" rather than "verified").
- **One lock helper, not two:** `tests/harness/lab-lock.sh` (SHARED for a fixed-cycles `--conf`)
  should fold into the main worker's `dosbox-lock.sh` once that sources the hub's
  `dosbox-lock-lib.sh` (intent lock, hub b9b7364). Coordinator, 2026-09-23.
- **Inserted-silence check:** `pcm_unaccounted` on mi-stall-isr / mi-throttle-isr is -156 / -55 today
  (silence played into a starved stream while content is active). Once the main worker's SDL 0197 /
  ags 0213 (drop underflow padding) lands, add `pcm-accounting-stall` and `-throttle` checks, eq 0,
  with a pre-0197 build or the padding switch as control.

### 3.3 AMENDMENT to S8L1 (2026-09-23, after the first cell, `off`, and before any sound arm was read)

The first cell (`results/S8L1-VOID-1-off-2026-09-23`) broke two things in the design:
1. **Void by its own rule:** 56 host clicks, 51 reached the driver: the 55-click driver outlived the
   5000-tick game and its last 5 clicks landed at a DOS prompt. Now 45 clicks (~104 s, ending before
   the exit at ~127 s). The second cell (`S8L1-STOPPED-2-pcm`) was stopped mid-run and was not read.
2. **The fixture saturates at fixed 40k:** `idle_ms_per_tick` 0.03, `frames_skipped` 2507 of 4999
   ticks, ~43 ms per render pass (`present_update_window` ~40 ms of it -- against 0.95 ms on the 486
   in S2T2; the emulated 512x384 LFB present is far dearer here than on the target). With no idle
   time, "Δ update_ms_per_tick, cross-checked by idle" cannot see a cost: it shows as render passes
   lost. **Amended cost metric:** cost of an arm (ms per tick) = (render_passes_off -
   render_passes_arm) x ms_per_render_pass_off / ticks, from the same-position cells of the ABBA;
   secondary: Δ `nonrender_ms_per_tick` (update - render per tick). Predictions 1-3 stand unchanged
   (ranking pcm > opl3-pcm > wb-pcm; opl3 0.5-3 ms/tick; counters). The run restarts from cell 1
   with fresh tags.

### 3.4 S8L1 RESULT (2026-09-23): sound costs ~1.1 ms/tick at fixed 40k, all of it PCM -- no MIDI plays on the S8 fixture

Eight cells, `results/S8L1-{1..8}-{arm}-2026-09-23`, binary `eba15e780f2e` (clean), FIXED 40k,
all valid (every host click reached the engine, `lost_inputs=0`; room 3; alias ON `x=96 y=72`).

| arm | render passes (ABBA pair) | cost vs off, ms/tick (passes lost x 43.21 ms / 4999) | nonrender ms/tick | pcm_irqs | MIDI |
|---|---|---|---|---|---|
| off | 2493 / 2494 | - | 3.32 / 3.31 | - | - |
| pcm | 2360 / 2372 | 1.10 | 4.48 / 4.38 | 2701 / 2702 | none |
| opl3 | 2363 / 2370 | 1.10 | 4.46 / 4.40 | 2701 / 2702 | **none (backend never opened, events=0)** |
| wb | 2366 / 2373 | 1.07 | 4.43 / 4.37 | 2702 / 2702 | **none** |

**The finding that matters more than the ranking:** Trilby's music is MIDI (`music1.mid` ..
`music10.mid` in the package; there is no music 0), but the S8 fixture -- room 3 entered with
`--startr 3`, the S2T2 cell -- plays **no MIDI at all**: `Playing music 0` at startup (nothing), then
room 3's `Playing ambient sound 9 on channel 1`, a continuous PCM loop (2720 chunks, none all-zero).
The hardware cell S2T2 shows the same two lines. So on the fixture as defined, the S8 bar's "MIDI:
OPL3 and WaveBlaster" and `late_writes=0` are **vacuous**; the arms `opl3` and `wb` measured PCM only.
A MIDI-playing in-play state is needed (probe S8MP below). **Coordinator decision needed:** keep room
3 (PCM-only S8) or move the S8 fixture to a room that plays MIDI.

Predictions: (1) the ranking pcm > opl3-pcm > wb-pcm is **untestable** here (both MIDI increments
are 0 because nothing played); (2) "opl3 costs 0.5-3 ms/tick" -- 1.10, inside the band, but it is the
PCM cost; (3) counters: `overwrites=0`, `silent_irqs=0` in every sound cell; `pcm_unaccounted` 18-19
in every sound cell = the chunks still in the ring and stream at quit (the ambient loop plays
through the exit; ~743 ms ring = 16 chunks + the stream), not a loss -- this binary predates 0252's
`inflight=` field, which now makes that residual 0 (to be confirmed on the next build).

Where the ~1.1 ms/tick of PCM goes (mean of the pairs, ms per tick, pcm - off): the idle wait
+0.42 (`wait_next_frame`: the cooperative audio thread's PlayDevice runs inside SDL_Delay's yield),
`game_objects_update` +0.39 (unexplained: characters/objects only; candidates: the ISR's cycles
landing in whichever phase it interrupts, or the ambient channel's per-tick update -- not resolved),
the mixer pump `catchup_audio_poll` +0.29. Three parts of the same size; none dominates.
At fixed 40k this fixture is present-bound (43 ms per render pass, ~40 of it the emulated 512x384
present, against 0.95 ms on the 486), so the ~4.4% of a 25 ms tick is a ranking figure, not a 486
prediction. `stalls100` with sound (14-18/min, max ~130 ms) are three-render-interval gaps of the
saturated emulator (none with sound off), not stalls a 486 would show.

### 3.5 PRE-REGISTRATION S8L2 (2026-09-23): the same ranking where MIDI plays -- Trilby room 16

The S8MP probe (`results/S8MP-2026-09-23/summary.txt`: `--startr N`, 400 ticks, fixed 40k, sound on,
headless) found MIDI starting in room 1 (`music 1`, 102 events) and room 16 (`[Room script:21]
Playing music 4`, 683 events in 400 ticks -- the busiest), none in the rooms seen so far otherwise.
Room 16 at 512x384x8 engages the same alias (`x=96 y=72 320x240`). Whether room 16 is walkable
in-play is not known yet; `presents_real` / render passes and the click journeys will show it.

**Cells:** `S8_ROOM=16 s8-cell.sh`, the S8L1 arms and order (off, pcm, opl3, wb, wb, opl3, pcm, off),
S8L1's amended cost metric (render passes lost x off's ms per pass / ticks; secondary nonrender
ms/tick), same binary `eba15e780f2e`, FIXED 40k, SHARED lock through the hub library.
**Predictions:** (1) now testable: pcm > opl3 - pcm > wb - pcm; (2) opl3 - pcm (the MIDI part alone)
0.2 - 1.5 ms/tick -- music 4 is ~70 events/s at the probe's rate, and on DOSBox-X an OPL3 register
write is cheap, so the planning on the main loop dominates; (3) `opl3` arm `midi_tick=isr` and
`late_writes=0`; `wb` arm `midi_tick=poll` with late50 > 0 (the poll path is late at low render
rates -- the SB5W hardware finding); `overwrites=0`; `pcm_unaccounted` = the ring+stream residual
(this binary predates `inflight=`).
**Void if:** room 16 is not reached, a cell's host clicks do not all reach the engine, `midi=none`
in the opl3 or wb arm, or the two cells of an arm differ by more than the difference being ranked.

## 5. SDL 0197 / ags 0213 witness for S16U1 (coordinator priority, 2026-09-24) -- PASS

Pre-registered by the main worker in dosags `3342b5c9` (PLAN.md, item (b)). This branch rebased onto
main `77681da4` (SDL 0196+0197, ags 0210-0213, 0293/0295; the same patch set as the main build
`4339326550df`) plus this branch's SDL 0220 and ags 0250-0252. ags 0252 was re-cut on 0213
(conflict in `format_status_string`: both add fields; both kept; the two status buffers grow
512 -> 640 bytes, since 0213 + 0252 brought the string to ~470 bytes and a truncation would cut the
MIDI tail silently). All cells: 5 Days `--startr 3`, `--fixed-timestep --sb-live`,
`confs/dosbox-x-fixed40k-opl3.conf` (FIXED 40000), lock SHARED through dosags' `dosbox-lock.sh`
(hub intent-lock library), `AGS_EXE` pinned to a saved copy so no rebuild could change it mid-series.
Raw: `tests/harness/results/W0197-*-2026-09-24/` (`cell/` = RUN.BAT, RUNMANI.LOG, STDOUT.TXT;
`facts.txt` = the RATCHET figures).

| cell | binary | ticks / stalls | mixed | pcm_irqs | inflight | **pcm_unaccounted** | **underflow_pads** | partial_pulls | silent_irqs | overwrites | **late_writes** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| W1 witness (mi-stall-isr) | `e094b3dc566c` (rebased, 0197+0213), build_dirty=0 | 3000 / 19 x 1.5 s | 441 | 441 | 0 | **0** | **279** | 0 | 96 | 0 | **0** |
| W0 control (same cell) | `3e52fca583e4` (pre-0197 base 1995a4fe + 0220/0250-0252), build_dirty=0 | 3000 / 19 | 54 | 98 | 0 | **-44** | NA (pre-0213) | NA | 8 | 0 | 0 |
| W2 no-stall, 16-bit (CA16 style) | `e094b3dc566c` | 8000 / 0 | 679 | 679 | 0 | **0** | **0** | 0 | 29 | 0 | 0 |
| W3 no-stall, `SDL_HINT_DOS_AUDIO_SB_FORCE_8BIT=1` (CA8 style) | `e094b3dc566c` | 8000 / 0 | 997 | 997 | 0 | **0** | **0** | 0 | 29 | 0 | 0 |

**Against the bar:** (1) W1: `pcm_unaccounted` 0 (bar: within +-1) -- PASS; `underflow_pads` 279 > 0 --
the fix fired -- PASS; `late_writes` 0 through 19 forced stalls -- PASS. (2) Control W0: the
pre-0197 build shows the defect, -44 (98 IRQs played data, 54 chunks mixed: silence the mixer never
made, played mid-sound) -- the witness has power. **The magnitude is not the ~-156 the bar quoted:**
-156 was the same cell at cycles=max (trial, 2026-09-23); at fixed 40k the pre-0197 cell read -90 in
the full ratchet run (eba15e780f2e) and -44 here, because 5 Days picks its ambient sounds at random
(W0 mixed 54 chunks, W1 441): how much silence gets inserted depends on how much sound is playing
when each stall hits. The sign and the presence are the witness; the size is not reproducible.
(3) No-stall cells W2/W3: exact (679 = 679, 997 = 997), `underflow_pads=0`, `partial_pulls=0`
recorded; on the 8-bit path all 57 quiet chunks were played (the 0192 fix holds). Not verified
independently: that W3's device really ran 8-bit (the status string's `m16` is the MIXER format, as
in main's CA8; this cell collected no SDL debug log) -- the hint is in its RUN.BAT.

Other observations: W1's 96 `silent_irqs` are the stalls themselves -- with 0197 the ring now runs
empty during a 1.5 s stall instead of being fed core padding, so the silence shows where it happens
(the Gate S8/S16 bar counts silent IRQs "outside room loads": forced stalls are not room loads, so a
real stall of that length on the 486 would count against it). W2/W3's 29 silent IRQs with no forced
stall are unexplained here (the room-3 lattice stalls of PLAN 8.3 are the obvious candidate).

### 3.6 AMENDMENT to S8L2 (2026-09-24, before any room-16 cell ran)

- **Binary:** `4de5c421abe5` (clean), not `eba15e780f2e`: this branch is now rebased on main `77681da4`
  (SDL 0197, ags 0213, 0293/0295) for the 0197 witness, and carries the new **ags 0253** (MIDI stream
  steadiness: per-second MIDI work reaching the chip, `DOS-PORT midistream` in RUNMANI.LOG). It does
  NOT carry SDL 0221 (the lost-click fix, pre-registered separately). Saved as `build/ws/s8l2/ags.exe`
  and pinned with `AGS_EXE`. S8L1's figures (other binary) are not compared with S8L2's.
- **Coordinator decision 2026-09-24:** S8 moves to a room that plays MIDI; room 3 stays as the
  PCM-only reference row. Before room 16 counts as the S8 fixture, a **suitability report**: player
  control and walkable motion (every host click received, click journeys, `presents_real` well above
  idle), the 8-bit mode line and alias line, a steady MIDI stream across the run (0253: `zero_windows`,
  `longest_gap_s`, `trailing_gap_s`, events per window), and a witness sheet. Room 1 is reported
  alongside as the fallback.
- **Added cells (suitability, not ranking):** `S8L2-S16` and `S8L2-S01`: `S8_SERIES=1 S8_ROOM=16|1
  s8-cell.sh ... opl3` (frames every 2 s -> `series/sheet.png`); the capture load keeps them out of the
  ranking. **Suitability predictions:** room 16: every host click received, `midistream zero_windows`
  <= 2 over the span with `trailing_gap_s` 0 (the song does not end inside 5000 ticks), mode `512 x
  384 (8-bit)`, alias ON; room 1 likewise, or it is the title (then no walkable motion: reported as
  such).

## 6. SDL 0221: deliver the presses the level poll missed (coordinator GO 2026-09-24)

### 6.1 PRE-REGISTRATION F0221 (2026-09-24, before any 0221 cell ran)

**Patch:** `patches/SDL/0221-*` -- every pump reads INT 33h function 5 (left, right) and, for each
button, delivers the presses the level read could not see: an up if SDL still has the button down,
then (down, up) per missed press, before the level send; the engine receives exactly the driver's
press count, in order, ending in the level state. 0220's `seen_presses` now counts presses
DELIVERED, so `lost_clicks = hw - seen` reads 0 when nothing is missed and negative for a phantom.
**Binaries (clean, the same series but for 0221):** with 0221 `5dbae9954df9`
(`build/ws/f0221/ags.exe`), without `4de5c421abe5` (`build/ws/s8l2/ags.exe`).

| cell | recipe (click-cell.sh, 5 Days `--startr 3`) | binary | prediction |
|---|---|---|---|
| F1 | JC6Q: cycles=max default conf, `DOSAGS_MI_RENDER_DELAY_MS=150`, 20 clicks x **20 ms** + 5 keys | 0221 | **lost_inputs 0**, `lost_clicks` 0, host 21 = driver 21 = engine 21 |
| F0 | F1 on the control binary | no 0221 | **~17 lost** (JC6Q: 17 of 21); lost_inputs >= 10 |
| F2 | JC40: cycles=max, no throttle, 20 x **80 ms** + 5 keys | 0221 | unchanged: 0 lost, 21/21, keys 5/5 |
| F3 | fixed 40k (5 Days renders ~3/s), 20 x **80 ms** + 5 keys | 0221 | **0 lost** |
| F3c | F3 on the control binary | no 0221 | ~13 lost (full ratchet run 20260924T020702Z: 13 of 21) |

**No phantom clicks, in every 0221 cell:** host clicks = driver presses (`mouse_presses_hw`) = presses
the engine received (click journeys + unfinished + cleared + failed), and `lost_clicks` = 0, never
negative. Keys unchanged (5/5). **Cost:** two more real-mode INT 33h per pump than 0220 (which read
every 8th pump) -- not measured here; a rate cell on the 486 is the only valid measure, and the
coordinator is told it is owed.
**Void if:** the driver saw fewer presses than the host injected (injection failed), a cell did not
reach room 3, or `build_dirty=1`.
**If it passes:** the no-loss ratchet click runs go back to quick clicks, and the coordinator takes
0221 to the hub's shared patches.

### 3.7 S8L2 SUITABILITY RESULT (2026-09-24): neither room 16 nor room 1 is an in-play MIDI fixture; and a new S8 blocker -- the ISR replay's 256-writes-per-IRQ cap

Binary `4de5c421abe5` (clean), FIXED 40k, `S8_SERIES=1`, opl3 arm, 45 host clicks at ~2.3 s.
Raw: `results/S8L2-S16-2026-09-24/`, `results/S8L2-S01-2026-09-24/` (each: `cell/`, `facts.txt`,
`s8.txt`, `series/sheet.png`).

| | room 16 | room 1 |
|---|---|---|
| what it is (witness sheet) | a scripted **cutscene** (two characters, dialogue advanced by the clicks), then the game moves to **room 5** at t=29 s (a red room: more dialogue, then characters standing) | the **title menu** (New Game / Resume / Quit), static |
| mode / alias | 512 x 384 (8-bit), alias ON x=96 y=72 | same |
| host clicks -> driver -> engine | 46 / 46 / 46, lost 0 | 46 / 46 / 46, lost 0 |
| MIDI (0253 midistream, isr_writes per 1 s) | music 4 for **27 s**, then silence: span 137 windows, 110 zero, trailing gap 110 s | music 1 across the run: span 122, 22 zero, longest gap 5 s, trailing 1 s, p50 38 writes/s |
| PCM | 117 IRQs (room 5's ambient) | **none** (pcm_irqs 0) |
| **MIDI late_writes (ISR replay)** | **160**, late_max 46 ms | **2316 of 16084**, late_max **92 ms** |
| isr_burst | **256** | **256** |

**Suitability verdict:** room 16 is not in play and its MIDI stops when the cutscene ends; room 1 is
the title, with no motion and no PCM. Neither meets "player control, walkable motion, steady MIDI,
PCM + MIDI". The S8MP re-probe (room 22 with a longer timeout; rooms 29-42, void before) is running.
The ranking cells of S8L2 in room 16 were **not run**: stopped by me before cell 1, since they would
mostly have measured room 5 (no MIDI) -- void by S8L2's own terms.

**The finding that matters for S8 (and any OPL3 title with dense music):** the SDL ISR replay (SDL
0193) writes at most `MIDI_DEFER_MAX_PER_IRQ` = **256** queued OPL register writes per SB IRQ ("bound
on ISR time per IRQ", `SDL_dosaudio_sb.c`). Every 5 Days cell peaked at `isr_burst` 79-80 and read
`late_writes=0`. Trilby's music hits the cap exactly (`isr_burst=256`) and the overflow waits for the
next IRQ(s): 2316 late writes, up to 92 ms (two IRQ periods) in room 1's music. On the 486 the same
cap applies, so Gate S8's `late_writes=0` cannot pass on Trilby's MIDI as the replay stands, whatever
the fixture room. This is the main worker's SDL 0193-0196 area; a candidate change (a larger or
adaptive per-IRQ budget, or planning dense bursts' non-audible writes -- instrument loads -- ahead of
their stamp) needs a pre-registration and the ISR-time cost measured on the 486 (an OPL3 write is a
few us; 512 per IRQ would be ~1-3 ms of ISR). Not changed here.

### 6.2 F0221 RESULT (2026-09-24): PASS on every pre-registered line

Raw: `tests/harness/results/F0221-{F1,F0,F2,F3,F3c}-2026-09-24/` (`cell/`, `facts.txt`). All clean builds.
F1/F0 ran EXCLUSIVE at cycles=max (the JC6Q/JC40 recipe); F3/F3c SHARED at fixed 40k.

| cell | binary | recipe | host / driver / delivered / engine clicks | lost_inputs | lost_clicks | keys | fps_p50 | prediction |
|---|---|---|---|---|---|---|---|---|
| F1 | 0221 `5dbae9954df9` | 150 ms delay, 20 ms clicks | 21 / 21 / 21 / 21 | **0** | 0 | 5/5 | 3.96 | 0 -- MET |
| F0 | no 0221 `4de5c421abe5` | same | 21 / 21 / 8 / 8 | **13** | 13 | 5/5 | 3.97 | ~17, >= 10 -- MET (power) |
| F2 | 0221 | JC40: no delay, 80 ms | 21 / 21 / 21 / 21 | 0 | 0 | 5/5 | 26.84 | unchanged -- MET |
| F3 | 0221 | fixed 40k, 80 ms | 21 / 21 / 21 / 21 | **0** | 0 | 5/5 | 3.21 | 0 -- MET |
| F3c | no 0221 | same | 21 / 21 / 8 / 8 | **13** | 13 | 5/5 | 3.22 | ~13 -- MET |

**No phantom clicks:** in every 0221 cell host = driver = delivered (`mouse_presses_seen`) = engine
received = 21, `lost_clicks` 0 (never negative). **Not measured:** 0221's cost (two real-mode INT 33h
per pump); owed as a 486 rate cell before it is called free.

### 6.3 SDL 0222 + PRE-REGISTRATION F0222 (2026-09-24): a run-time switch back to level-only reads

Why: with 0221 in the series, the ratchet's lost-click checks need a control that can still lose a
click in the SAME build (see the 0222 message). `SDL_HINT_DOS_MOUSE_LEVEL_ONLY=1` = pre-0221 behaviour.
Binary `348920d7fe7b` (0221 + 0222, clean). **Cells** (the F3 recipe, fixed 40k, 20 x 80 ms + 5 keys):
**G1** hint unset -> 0 lost, 21/21 (0221 unchanged by 0222); **G0** hint =1 -> ~13 lost (as F3c),
`lost_clicks` = hw - level edges > 0. Void if the driver saw fewer than 21.

### 3.8 S8L3 SUITABILITY (2026-09-24): room 35 is the in-play MIDI + PCM candidate

Same method as 3.7 (opl3 arm, fixed 40k, witness sheet, 45 host clicks), binary `5dbae9954df9` (clean;
carries 0221 and 0253). Raw: `results/S8L3-S{40,22,35,37,42}-2026-09-24/`.

| room | what the witness sheet shows | rooms visited | PCM IRQs | MIDI (0253: span / zero windows / longest gap / trailing / p50 writes/s) | late_writes / isr_burst | verdict |
|---|---|---|---|---|---|---|
| 40 | narrated story text over a figure (a sequence) | 40 | 0 | 194 / 0 / 0 / 0 / 98 (music 10) | 0 / 66 | not in play; MIDI-only reference |
| 22 | narration, then room 23: a ship deck, the figure never moves | 22, 23 | 0 | 157 / 29 / 3 / 0 / 56 (music 9) | 0 / 121 | not in play |
| **35** | **a forest: a short dialogue, then one character at a different place frame to frame -- walkable play** | **35 only** | **2041** (sound 11, ambient 18; accounting exact, 0 overwrites, 0 silent IRQs) | **127 / 8 / 7 / 0 / 581** (music 9, then music 4 from the room script) | **510 / 256 (the cap)** | **candidate** |
| 37 | leaves for room 38 inside the run | 37, 38 | 624 | 136 / 21 / 3 / 0 / 57 (music 9) | 160 / 256 | unstable |
| 42 | leaves for rooms 0 and 2; MIDI stops for the last 91 s | 42, 0, 2 | 2365 | 169 / 97 / 91 / 91 / 0 | 178 / 256 | no |

Every cell: 512 x 384 (8-bit), alias ON; host 46 = driver 46 = engine 46 clicks. **Room 35** (`--startr
35`) is the S8 candidate: player in play, PCM and dense MIDI together, no room change, no trailing
silence. It also exercises the 256-writes-per-IRQ cap hardest seen so far (p50 581 writes/s, 510 late
writes): on it, Gate S8's `late_writes=0` fails until the replay's per-IRQ budget is dealt with.
At fixed 40k: tick_rate 38.97, fps_p50 19.53 (DOSBox-X, not a 486 figure). Its short opening
dialogue should be excluded from any rate window (the S2T2 `drive-walk.sh` warm-up already skips 25 s).

**F0222 RESULT (2026-09-24): PASS.** `348920d7fe7b` (clean), F3 recipe (fixed 40k, 80 ms clicks):
G1 (hint unset) 21 / 21 / 21 / 21, lost 0 -- 0221 unchanged by 0222; G0 (`SDL_HINT_DOS_MOUSE_LEVEL_ONLY=1`)
21 / 21 / 9 / 9, **lost 12** (`lost_clicks` 12) -- the switch restores the pre-0221 loss in the same
binary. Raw: `results/F0222-G{1,0}-2026-09-24/`. The ratchet's click runs go back to quick clicks
(80 ms at fixed 40k; 20 ms at the 150 ms render delay), with the switch as their control.

## 2. The ratchet (tests/ratchet.yaml, format v1) -- controls pass (2026-09-24)

Full hand run with `--controls`, branch at `978a4fde`, binary `348920d7fe7b`:
`build/ratchet/20260924T100738Z/ratchet-report.txt`. Summary line:
**`ratchet 20260924T100738Z FAIL: 37 pass (7 improved), 4 fail, 0 blocked, 2 quarantined, controls run
| controls failed: control.stale-frames-sb-5days:NOPOWER control.journeys-unfinished:NOPOWER
control.pcm-mixed-sb-5days:NONUMBER control.overwrites-sb-5days:NOPOWER`** -- every CHECK passed
(the 4 "fail" are those four controls); 33 controls made their checks fail as required (12 screen
rows via `--break-a`, the AQ verifier 728 stale frames, the journey counts and p95s, pcm accounting
1193, MIDI late 1080 / 6163 / 7535, stall-fired 0, lost inputs 12 / 13 / 16 with SDL 0222's switch,
injected-count pins, exe +4 KB, code lock +1 MB).

The four, fixed in `tests/ratchet.yaml` (commit after this section) and re-verified
(`build/ratchet/20260924T122427Z`, `--only journeys-unfinished,pcm-mixed-sb-5days --controls`: both OK):
- `stale-frames-sb-5days`: **deleted** -- 5 Days runs at its default 2x rung, where the narrowed
  present is always rejected, so the verifier cannot fail there: the check was vacuous (the AQ row and
  the gate keep stale frames covered).
- `journeys-unfinished`: control now `DOSAGS_JOURNEY_TITLE_ROOM=99` (boot never ends) -> 1, OK. An
  auto-exit tick cannot land inside a room or load journey: AGS runs the load and the fade inside one
  blocking tick.
- `pcm-mixed-sb-5days`: `ratchet-facts.py` now reports `pcm_mixed=0` when the mixer never opened
  (`audio_vital_status=NA`) -- a true 0 -- so the sound-off control reads 0, OK.
- `overwrites-sb-5days`: **quarantined (reported only)** -- no switch makes a correct build overwrite
  (a 2-chunk ring, and the same with no background audio thread, `results/OVWC-2026-09-24`, both 0);
  an overwrite loses audio, so `pcm-accounting` (control OK) fails on it anyway.

Quarantined: `screen-agsquest-alias-y60`, `screen-shards-alias-512x384` (its control has no power),
`overwrites-sb-5days`. Nightly (crontab) is the coordinator's call once this merges.

## 7. Operator decision and hardware pre-registrations (2026-09-24)

**OPERATOR (~13:40Z, via the coordinator): Trilby's Notes room 35 is the S8 fixture.** Room 3 stays the
PCM-only reference row. The first 486 run in room 35 is a BASELINE and is expected to show late MIDI
writes; Gate S8 can pass only once the 256-writes-per-IRQ cap is fixed (section 8, this worker's).

### 7.1 PRE-REGISTRATION S8H (next hardware batch; the coordinator stages, this worker does not touch hardware)

Command (S2T2's, room changed): `run-hw.sh trilbysnotes --tag <TAG> --timeout 1800 --env
SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env DOSAGS_TAS_AUTO_EXIT_TICK=5000 --ags-arg --startr --ags-arg 35
--extra-file tests/harness/presentation/trilbysnotes/ACSETUP-<ON|OFF>-512X384-ROUND.CFG:ACSETUP.CFG`,
with `tests/harness/drive-walk.sh <TAG> 25 2 80` alongside (the 25 s warm-up covers room 35's opening
dialogue). Binary: the landed main build carrying SDL 0220-0222 and ags 0250-0253 (clean, named at
landing). PicoGUS SB + OPL3.

| cell | cfg | purpose |
|---|---|---|
| S8H-A0 | ACSETUP-OFF (sound off) | anchor: room 35's rate with no sound, on this binary |
| S8H-O1, S8H-O2 | ACSETUP-ON | the S8 bar's OPL3 arm, x2 -- a BASELINE |
| (S8H-W1/W2) | ACSETUP-ON, WaveBlaster | deferred: waits on dosags-lab-wb's on-time WB transport |

**Predictions (DOSBox-X at fixed 40k measured room 35 at `isr_burst=256`, `late_writes=510`):**
O1/O2: `late_writes > 0` with `isr_burst=256` (the cap binds on the 486 too); `pcm_unaccounted` within
+-1 (ags 0252), `overwrites=0`; `midistream` span >= 100 windows with `trailing_gap_s` 0 (ags 0253);
host clicks = driver presses = presses delivered (SDL 0220/0221: `lost_clicks=0`); the tick figures
are measured, not predicted (the first sound-on room-35 cells anywhere). A0: `tick_rate_steady` >= 39.2
(S2T2's room 3 read 39.99; room 35 is unmeasured). **VOID if:** the room is not 35, `build_dirty=1`,
the witness is not reviewed, or `midistream` shows no MIDI.

### 7.2 PRE-REGISTRATION C221 (next hardware batch): what SDL 0221 costs on the 486

0221 reads INT 33h function 5 twice per pump (0220 read it every 8th pump). The price is real-mode
round trips on the target, invisible on DOSBox-X. **Cells:** an ABBA pair on the Gate 2 fixture
(BENCH8 anim12 at Mode 13h, `--gate` 5000 ticks, sound off -- the most stable rate cell this port has):
A = landed build with `SDL_HINT_DOS_MOUSE_LEVEL_ONLY=1` (SDL 0222: 0221 off, 0220's counters still
read every pump -- so this isolates 0221's delivery logic, not the reads), B = the same binary, hint
unset; A B B A. Plus one cell of the pre-0220 main binary for the reads themselves, if the coordinator
wants the whole cost. **Prediction:** B - A within the run-to-run floor (|delta| <= 0.02 on
`tick_rate_steady`); the reads (2 x ~30-50 us per pump at ~40 pumps/s) cost <= 0.4% of a tick against
the pre-0220 binary. **Falsified by** a steady-rate drop > 0.05 in B.

## 8. The ISR replay's per-IRQ write cap (coordinator: this worker's, 2026-09-24)

**The defect (section 3.7/3.8):** SDL 0193's `MidiDeferDrain` writes at most `MIDI_DEFER_MAX_PER_IRQ` =
256 queued OPL writes per SB IRQ (~46 ms); room 35's music needs more in some IRQs, the rest slip one or
two IRQs (fixed 40k: `isr_burst=256`, `late_writes=510`). Each OPL write in the ISR is 1 out + 6 status
reads (address settle) + 1 out + 6 reads (data settle): ~14 ISA I/O cycles, on the 486 very roughly
10-20 us (not measured -- that is part of this work). 256 writes = ~2.5-5 ms of ISR per IRQ.
**Rules (coordinator):** new SDL patches from 0223 on top of 0193-0196 (the main worker's; told through
the coordinator), never an edit of them; rank the options in the lab first; the time an IRQ spends in
the ISR stays bounded and stated; a 486 cell measures the ISR cost.

### 8.1 PRE-REGISTRATION CAP1 (2026-09-24): instrument, then rank the options on DOSBox-X

**Instrument (SDL 0223 + ags 0254, both permanent reporting, default behaviour unchanged):**
`SDL_HINT_DOS_MIDI_DEFER_MAX_PER_IRQ` (env, read when the replay is enabled; default 256 = today; clamped
16..8192); per run: `cap` in force, `cap_hits` (IRQs that stopped at the cap with a due entry left),
and the drain's own time from raw PIT channel-0 reads in the ISR (`isr_max_us`, `isr_mean_us` over IRQs
that wrote anything, `isr_us_per_write`) -- appended to the MIDI part of `audio_vital_status`.
The PIT timing assumes channel 0 counts at 1.193 MHz with a period longer than one drain (true under
uclock's mode; stated per cell; void where the OPL timer pump owns ch0).

**Cells (fixed 40k, `--sb-live`, OPL3 conf, clean build with 0223/0254; `S8_ROOM` cells via s8-cell.sh,
opl3 arm, same click driver):**
| arm | budget | room 35 | room 40 | 5 Days room 3 (mi-stall-isr recipe, no stall) |
|---|---|---|---|---|
| K256 | 256 (default) | x2 | x1 | x1 |
| K512 | 512 | x2 | x1 | x1 |
| K1024 | 1024 | x1 | - | - |
| KMAX | 8192 (= queue: unbounded) | x1 | - | - |
**Plus an offline look at option (b), writing non-audible parts ahead:** a lab-only dump of the queue
entries of the room-35 IRQs that hit the cap, classified by register group (A0/B0 = pitch/key-on,
40-55 = level, 20-35/60-95/E0-F5/C0-C8 = instrument). Ranking (b) needs only what fraction of a capped
burst is instrument loading that could move earlier; it is not implemented unless it ranks first.

**Predictions:** (1) KMAX's `isr_burst` = room 35's true peak demand, between 257 and 800 writes, and
KMAX late_writes 0; (2) K512 late_writes 0 on room 35 if the peak is <= 512, else fewer than K256;
(3) room 40 and 5 Days: identical to K256 at every budget (their peaks are 66-121); (4) the capped
bursts are dominated (>= 60%) by instrument-group writes (program changes at a phrase start) -- if so,
option (b) removes the peak without lengthening the ISR at all; (5) on DOSBox-X `isr_us_per_write` is
emulator time and ranks nothing -- the 486 cell (8.2, after the lab) states the real cost.
**Void if:** the room is not 35/40/3 as listed, `midi_tick` is not isr, or `build_dirty=1`.
**Decision rule:** pick the option that makes room 35's `late_writes` 0 with the SMALLEST worst-case ISR
time per IRQ (budget x per-write cost on the 486); a raised budget is acceptable only with the 486's
per-write cost measured and the resulting worst-case ISR time stated.

## 9. LANDING RECORD: lab/journeys on dosags main (2026-09-24)

**Applied series gains exactly:** SDL `0220` (mouse press counts vs the level poll), `0221` (deliver the
presses the poll missed -- the lost-click fix), `0222` (`SDL_HINT_DOS_MOUSE_LEVEL_ONLY`, off by
default); ags `0250` (journeys + stall share), `0251` (lab stress switches, off unless set), `0252` (PCM
chunk accounting), `0253` (MIDI stream steadiness). Nothing lab-only enters the series: SDL 0223 / ags
0254 (section 8, the cap instrument) are not part of this landing, and the CAP1 dump was a throwaway
(`results/CAP1-2026-09-24/cap1-dump-throwaway.patch` will be its only record).
**Review (sdldos:review, every patch):** real `git format-patch` output from the vendor commits; slots
in this worker's ranges (SDL 0220-0222, ags 0250-0253); ASCII-only; no `fopen`; port-owned naming;
0251's retirement condition is in its message; no temporary diagnostic.
**Checks on the exact tree (rebased on main `8ac262e1`):** the full series applies on clean vendor trees
(SDL ..0197, 0210, 0220-0222; ags ..0214, 0230, 0231, 0250-0253, 0293, 0295); `make
verify-patches-applied` exits 0; clean build **`binary_sha12=32cc99df4761`, `build_dirty=0`**, sha256
`6a234d23406d9302855e8af0c112011f060ca4bb616e277e65ba79305ca2efd8` (`build/land/ags.exe`); the new
strings are present (`journey_basis`, `midistream`, `lost_clicks`, `SDL_HINT_DOS_MOUSE_LEVEL_ONLY`).
**Gate (full `gate-alias.sh` on `32cc99df4761`, AGS_EXE pinned):** `results/GATE-land-journeys-2026-09-24/`.
13/14 rows A == B, **14/14 controls fail as required**. `agsquest-alias-y60`: 10/10 equal.
`shards-alias-512x384`: FRZ00 froze at tick 101 vs 100 (the known, quarantined tick-100 divergence;
its control has no power), ticks 300-900 equal. Under "every row A == B except the quarantined rows",
the gate **passes**. (gate-alias.sh exits 1 on the Shards row, as it does for every gate since 0209.)
**Also landing:** `tests/ratchet.yaml` + harness (`journeys.py`, `ratchet-facts.py`, `ratchet-cell.sh`,
`ratchet-lock-control.sh`, `lab-cell.sh`, `click-cell.sh`, `drive-clicks-dosbox.sh`, `lab-lock.sh`,
`s8-cell.sh`, `s8-facts.py`), `gate-alias.sh --rows/--break-a` (additive), `confs/dosbox-x-fixed40k-
mpu401.conf`, this record and its results directories. The ratchet's limits were set on `348920d7fe7b`
(the same series before the rebase onto 0214/0230/0231); the first nightly run re-derives them if the
rebase moved exe size or the code lock (expected: a FAIL on `exe-bytes`/`code-lock-bytes` would be the
series growth, reviewed and lowered/raised by the coordinator, not a regression).
