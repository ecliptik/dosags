# LAB-MMD -- what `process_events_dispatch` actually is on Maniac Mansion Deluxe

Branch `lab/mmd` (worktree `~/git/dosags-lab-mmd`), worker `dosags-lab-mmd`. PLAN.md step 9.1.
LAB ONLY: no real-hardware run is part of this slice. DOSBox-X figures are a RANKING, never
evidence of 486 time. Game data (MMD, user-supplied) is never modified.

---

## 1. Read-first findings (source, vendor/ags at the 0209 series head; no run involved)

### 1.1 What `process_events_dispatch` brackets

`tickstats_process_events_dispatch` is ags patch 0082's whole-function `DosPortTickScope` on
`processallevents()` (`Engine/ac/event.cpp`). It is INCLUSIVE: everything reached from the
events queued this tick, including the script VM (`script_vm`, `RunScriptFunction`), every
engine API the script calls, and any nested game loop a blocking call pumps.

What gets queued, per ordinary tick (read in `Engine/main/game_run.cpp`):

- `GameUpdateEarlyRepExec()` runs `repeatedly_execute_always` immediately (NOT in dispatch;
  that is `rep_exec_wrapper`/`rep_exec_vm`), then **queues** `AGSEvent_Script(kTS_Repeat)` and
  `AGSEvent_Object(Room, Repexec)`. So the global script's `repeatedly_execute` and the room's
  rep-exec both run INSIDE dispatch, via `QueueScriptFunction` -> `RunScriptFunctionAuto` ->
  `RunUnclaimableEvent` (every module, then the global script) / `RunScriptFunctionInRoom`.
- Any hotspot/region/room interaction events (`kAGSEvent_Object`), GUI clicks
  (`kAGSEvent_GUI` -> `process_interface_click`), fade-in (`kAGSEvent_FadeIn` ->
  `current_fade_in_effect()`), and new-room events.

### 1.2 Where render work can land inside dispatch -- two different paths

(a) **Nested game loops.** Every blocking engine call goes through `GameLoopUntilEvent()` ->
`GameLoopUntilState::Run()` -> `UpdateGameOnce()`: `Wait`/`WaitKey`/`WaitMouseKey`
(`global_game.cpp:1160,1191`), `Display`/speech (`display.cpp:534`, `character.cpp:2769`),
blocking walk/move (`character.cpp:443,1128`, `object.cpp:391`, `script.cpp:981`), blocking
animate (`character.cpp:245`, `global_object.cpp:280`, `script.cpp:1063,1068`), button
animation (`button.cpp:88`); plus direct `UpdateGameOnce()` calls in dialog options
(`dialog.cpp:558,1286,1874`) and the inventory window (`invwindow.cpp:484,500`). If a handler
dispatched from `processallevents()` makes one of these calls, whole ticks (with their own
`render_graphics()` -> `render_to_screen()`) run inside the outer dispatch bracket.

(b) **Screen transitions that draw without a tick.** `kAGSEvent_FadeIn` ->
`current_fade_in_effect()` runs the fade state's `Draw()` per step, and each step calls
`render_to_screen()` directly (`screen.cpp:234,421,428,432,580`) -- no `UpdateGameOnce()`, so no
nested tick. This is the only path by which `render_to_screen` appears under dispatch
WITHOUT a nested tick.

### 1.3 How a nested tick is double-counted

- `process_events_dispatch` (outer) includes the whole nested tick (its render, its script, its
  present). The nested tick's own `processallevents()` hits `inside_processevent` and
  **returns at once, flushing its queue** (`events.clear()`), so it adds a near-zero call, not a
  second copy of dispatch time -- but its events are dropped, not deferred.
- `update_game_once_total` counts the nested tick as a call AND includes its time in the outer
  tick: double-counted in that phase's total.
- `render_to_screen` counts the nested render once, but that time also sits inside the outer
  `process_events_dispatch`. Summing the two double-counts it. `DosTickStallScope` (0142/0159)
  is the only exclusive accounting: `self_us` excludes nested ticks, `dos_tick_nested_us` holds
  them.

### 1.4 What the S2M1 hardware logs already say (re-read, not re-run)

`~/git/dosags/tests/harness/results/S2M1-2026-09-22/` (0194 binary `e8d4b76c5cd9`,
character select, title idle to tick 1000). These lines were recorded but not in PLAN.md's
summary:

- **Nested ticks in S2M1 = 0, by call count.** `update_game_once_total calls=999` =
  render passes 239 (`game_tick_outer calls=239`, `fps_basis render_passes=239`) + catch-up
  ticks 760 (`catchup ticks=760`). Every `UpdateGameOnce()` call was a top-level one; a
  nested tick would make calls exceed the sum. (`RUNMANI.LOG` lines 42, 43, 74, 76.)
- **`render_to_screen` "nested" is the fade.** `render_to_screen calls=251` against
  `render_to_screen_pertick calls=238`: 13 calls outside `render_graphics()`, i.e. path (b).
- **The 894 ms outlier is the room-50 fade-in, inside dispatch.** `evtype fadein n=1
  us=894002`; `stallwhat tick=1 self_ms=1023 children_ms=0 ... events_us=894279`;
  `DOSAGS_XT fadein_begin t_ms=1594 / fadein_end t_ms=2486` (892 ms). One event, no nested
  tick, 13 direct renders.
- **Dispatch by event type** (`STDOUT.TXT` `evtype`/`evobj`/`evroom`):
  `script n=999 us=24258973` (**24.26 ms/tick, 91.7% of dispatch's 26.47 s**: the global
  `repeatedly_execute`, the only `kAGSEvent_Script` an idle screen queues);
  `object n=2003 us=1290984` (room `Repexec n=999 us=1020434`, 1.02 ms/tick; hotspot
  `n=1001 us=134309`, 0.13 ms each; `beforefadein` 96.6 ms once); `fadein` 894 ms once.
- Engine-side GUI polling is already bracketed and small: `gui_poll` 0.03 ms/tick,
  `gui_context_cursor` 0.39 ms/tick.
- `script_vm` (24.63 s over 2003 calls) is inclusive of every engine API the script calls,
  so it does NOT separate interpreter cost (H1) from API cost (H2/H3). That split is what
  no existing field gives, and what the probe is for.

---

## 2. PRE-REGISTRATION (committed before any probe run)

### 2.1 Hypotheses, falsifiers, and the field each is read from

Shares are of dispatch time over the measured window, **excluding the fade-in dispatch**
(it gets its own line). "Probe" fields are defined in 2.2.

| | hypothesis | supported if | falsified if | field |
|---|---|---|---|---|
| H0 | nested-loop accounting; the real cost is the nested render | nested ticks inside dispatch carry >= 50% of dispatch time, and `render_to_screen` inside dispatch ~ one per dispatch | nested-tick time inside dispatch < 10% of dispatch AND in-dispatch renders are fade steps only | `mmdprobe dispatch nested_n nested_us rts_n rts_us maxdepth` |
| H1 | bytecode interpreter cost | VM self time (entry time - API time - nested time) >= 50% of dispatch | VM self time < 25% of dispatch | `mmdprobe entry ... us self_us insns` and `mmdprobe fn` |
| H2 | one DOS-expensive engine call per tick (the old `Clock::now()` class) | ONE API name >= 50% of dispatch at >= 0.5 ms per call, called ~once or a few times per tick | no single API name >= 25% of dispatch | `mmdprobe api name n us` (ranked) |
| H3 | GUI control polling across many controls | engine-side `gui_poll`+`gui_context_cursor` >= 25% of the tick, OR script calls to GUI/control APIs sum >= 50% of dispatch | both < 10% | existing `tickstats_gui_poll`/`gui_context_cursor` per room segment; `mmdprobe api` summed over GUI/control names |

They are not exclusive: H1 and H2/H3 split one number (the script event). The verdict is
the ranked split, with ms and share.

**Prior, stated so it can be wrong:** from 1.4, H0 is already falsified for the character
select on hardware (0 nested ticks) and H3's engine-side form is too (0.42 ms/tick). My lean
for the remaining split is **H1 largest (>= 50% of dispatch), no single API >= 25% (H2
falsified), GUI APIs < 20% (H3 falsified)**. Low confidence: a SCUMM-style verb UI calls
`GetLocationName`/`GetLocationType`-class hit tests every tick, and those walk every
character/object with sprite pixel tests, which could make one API name dominant.

**DOSBox-X bias, stated in advance:** DOSBox-X emulates a fixed instruction rate, and its
cost for port I/O and real-mode interrupts (INT 21h, PIT reads) bears no fixed ratio to a
486's. A DOS-expensive call (H2's class) can therefore rank LOW here and still dominate on
the 486. So H2 is judged on call COUNT and source reading as well as ms: for each top-10
API I record calls/tick and whether its source path makes a DOS/BIOS/port call per call. A
cross-ratio check: DOSBox-X ms/tick of the script event divided by the 486's 24.26, against
the same ratio for `render_backbuffer` (486: 9.43 ms/call). If the script ratio is > 2x the
render ratio (the script is relatively much cheaper under emulation), that is a flag for an
I/O-class cost DOSBox-X does not reproduce, and it goes into the hardware-cell list.

### 2.2 The probe (ags 0290, probe build only, reverted after; the diff is kept)

Never a gate binary. One global counter increment per VM instruction; everything else at
call/return/dispatch boundaries.

- `mmdprobe entry` -- per script entry function (the name passed to
  `CallScriptFunction`, keyed with its script): calls, inclusive us, `insns` (instructions
  executed while it was the outermost frame, exclusive of other entries run in nested
  ticks), `api_n`/`api_us` (engine API calls from its code), `nested_us`, and
  `self_us = us - api_us - nested_us` = the interpreter's own time.
- `mmdprobe fn` -- per script function reached (entry or `SCMD_CALL`/`SCMD_CALLAS` target):
  calls, exclusive `insns`, `api_n`, `api_us`; name from the script's export table, else the
  first line number and section. VM time per function is DERIVED
  (`insns x` the entry's `self_us/insns`), and labelled so.
- `mmdprobe api` -- per engine API function pointer (`SCMD_CALLEXT`): name (via
  `simp.FindName`), calls, us exclusive of nested ticks, max us.
- `mmdprobe dispatch` -- per room segment: calls, us, max, `nested_n`, `nested_us`,
  `maxdepth` (tick depth reached inside dispatch), `rts_n`/`rts_us` (`render_to_screen`
  calls and time inside dispatch), and the top-3 dispatches (tick, us, what they held).
- `mmdprobe evtype` -- the existing `evtype` split, per room segment, with `insns`, `api_us`,
  `nested_us` added.
- `mmdprobe seg` -- per room segment: ticks and the deltas of `update_game_once_total`,
  `process_events_dispatch`, `script_vm`, `gui_poll`, `gui_context_cursor`,
  `render_to_screen`, so each room's tick decomposes on its own.
- `mmdprobe cost` -- the probe's own clock-read count and the measured cost of one
  `uclock()` in this environment (1000 reads timed at start).

Segments dump when `displayed_room` changes and at quit.

**What each field would print if the answer were the opposite, and the path that lets it:**
- nested: a blocking call in a handler -> `GameLoopUntilEvent` -> `UpdateGameOnce` ->
  `DosTickStallScope` at depth >= 2 -> `nested_n++`, `nested_us += tick`. Positive control:
  the in-play run crosses the intro, whose room scripts are expected to make blocking
  calls; that segment must show `nested_n > 0`, or the counter is blind and H0's verdict is
  void.
- api: every `SCMD_CALLEXT` passes through one code block; timed with a `uclock()` pair,
  minus nested-tick time inside the call. The opposite (all API) would show
  `api_us ~ us`; a probe-OFF toggle (`DOSAGS_MMDPROBE_APITIME=0`) runs the same binary
  without the clock pairs, and the difference in `script_vm` per tick is the timing's own
  cost.
- insns: counted at the loop head; the opposite (no VM cost) would show a small insns count
  against a large `self_us`. Checked by `self_us / insns` being similar across entries.
- rts inside dispatch: snapshot of the existing `render_to_screen` totals at dispatch entry
  and exit; must show 12-13 calls in the fade-in dispatch (1.4), else it is blind.

**The probe's own cost:** three arms of the character-select run -- baseline binary (no
probe), probe with API timing ON, probe with API timing OFF -- and the `script_vm` ms/tick of
each. If the probe moves `script_vm` per tick by more than 20%, shares are recomputed from
counts and the cost is reported beside them.

### 2.3 Runs (DOSBox-X, ranking only; none before the coordinator's "go")

Uniform: `--fixed-timestep`, `SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1`, the S2M1 config
(`presentation/trilbysnotes/ACSETUP-OFF-512X384-ROUND.CFG` staged as `ACSETUP.CFG`), sound off,
`DOSBOX_DISPLAY_NUM=261` for anything interactive, the hub lock held as the coordinator directs.

- **MMD-CS** -- character select (the S2M1 screen), no input, `DOSAGS_TAS_AUTO_EXIT_TICK=1000`.
  Three arms per 2.2. Prediction: `script` event >= 85% of dispatch; `nested_n = 0`;
  `rts_n` 12-13, all in one dispatch (the fade); hypotheses per my prior above.
- **MMD-PLAY** -- the first in-play room reached through the game's OWN flow (pick two kids
  with held clicks, let the intro run), then idle and a few walk clicks in that room, auto
  exit ~1500 ticks after entry. `--startr` is not used for the measured entry (DUPCHAR4).
  Prediction: the global `repeatedly_execute` is the same script, so its per-tick cost is
  within 2x of MMD-CS's; the room rep-exec differs.

**Void a run if:** the mode line is not 512x384 16-bit; the room sequence in `STDOUT.TXT`
does not show the measured room reached by the game's own flow (for MMD-PLAY); the probe's
fade-in `rts_n` is not 12-13 on MMD-CS (blind instrument); the parts in `mmdprobe entry` do
not sum to within 5% of `script_vm` for the segment.

**Stop condition:** a named mechanism (which function/API/interpreter path, ms and share),
a ranked fix list ordered by breadth, and the hardware cells wanted. No fix in this slice.

---

## 3. Probe build (2026-09-23; built, not yet run -- DOSBox-X on HOLD)

- Diff kept at `lab-mmd/probe-0290-mmdprobe.diff` (working-tree changes on the 0209 series head,
  never committed to `vendor/ags` or `patches/ags/`; reverted after the runs). Files:
  `Engine/main/dos_port_mmdprobe.h` (new), `script/cc_instance.cpp` (instruction counter at the
  loop head; fn push at `SCMD_CALL`/`SCMD_CALLAS`/`CallScriptFunction`, pop at non-final
  `SCMD_RET` and after each `Run()`; `SCMD_CALLEXT` timing), `ac/event.cpp` (dispatch and
  event scopes, room segments, the dump), `main/game_run.cpp` (`dos_tick_nested_n`,
  max depth inside dispatch), `main/quit.cpp` (final dump).
- Binaries (`build/lab/`, not committed): probe `ags-0290probe.exe` sha256 `0bf382bb...`;
  baseline (the same tree with the probe stashed) `ags-base.exe` sha256 `b395af34...`.
  The probe binary reports `build_dirty=1` by construction; it is never a gate binary.

---

## 4. Static read of MMD's compiled global script (read-only; no run)

Tool: `lab-mmd/scdis.py` (+ `cg.py`, `lst.py`, `ops.txt`): parses the `SCOM` blocks in the
package's `ac2game.dta` / `roomNN.crm` in memory (the game data is only read), and walks the
bytecode with the engine's own opcode table (`sccmd_info`, arg counts) and fixups (import
names at `farcall`, function targets at `call`). Source lines are the script's own
`sourceline` operands. Static counts are call SITES, not per-tick counts.

- Global script: `SCOM` v81, 130,393 code words, 386 imports, 189 exported functions -- a
  Lucasarts-style verb template (`UpdateActionBar`, `CheckDefaultAction`, `TranslateAction`,
  `VariableExtensions`, `SetAlternativeAction`, `GlobalCondition`, `CheckTimers`, `SetOwnTimer`/
  `IsOwnTimerExpired`). No backward jumps anywhere on the rep-exec call graph: no loops; the
  cost is straight-line code and API calls.
  **CORRECTION (2026-09-23, after the first probe run):** wrong. The loop check tested the opcode
  name `jmp`; the engine's table calls it `jmpi`, so it counted nothing. Re-run with `jmpi`:
  `CheckTimers` (L271-274) loops, 30 iterations per tick (`GetGlobalInt` x2 + `SetGlobalInt` per
  pass), which the probe caught first (1,232 instructions/tick from 77 static). `SetPlayer` and
  `MovePlayerEx` also loop, but only on actions, not per tick. Every other function on the
  per-tick path is loop-free.
- `repeatedly_execute` (L1626-2054, 3,031 static instructions). Unless paused, every tick:
  `CheckTimers`, then **~30 `IsOwnTimerExpired(n)` blocks** (each a script call + `GetGlobalInt`
  /`SetGlobalInt` through the timer helpers; the bodies behind them fire only on expiry), then
  (L2037-2039) **`CheckDefaultAction()` and `UpdateActionBar()`**, then (L2044-2053) up to three
  `FindGUIID`+`SetButtonPic` pairs.
- `CheckDefaultAction` (L655-702), every tick: `GetLocationName` (hit test across characters,
  objects, hotspots), `GetLocationType` x1-2, `GetInvAt`, `Extension()` (string scan via
  `StrGetCharAt`/`StrLen`), **3x `GlobalCondition`** (each up to `GetInvAt` x3, `GetCursorMode`,
  `GetLocationType`, `GetGUIAt`, `FindGUIID`, `GetGUIObjectAt` x2), `StrCopy` x2, and **10x
  `SetAlternativeAction`** (each: `Extension()` + two `FindGUIID`+`SetButtonPic` pairs, so up to
  ~20 `FindGUIID` and ~20 `SetButtonPic` per tick). When the hovered name carries an extension
  it also calls `VariableExtensions` (4,870 static instructions: 64 `GetHotspotAt`, 68
  `GetPlayerCharacter`, 74 `GetGlobalInt` sites; the 2.x compiler evaluates both sides of `&&`).
- `UpdateActionBar`, every tick: `GlobalCondition`, `TranslateAction` (`StrCopy` x14,
  `StrFormat` x3, `StrContains` x2, `GetTranslation`), `SetLabelText`, `SetLabelColor`.
- Room 50 (character select): 13 functions, 1,953 code words; its rep-exec is small (hardware:
  1.02 ms/tick).
- `AdjustLights` calls the AGSflashlight plugin; S2M1's STDOUT says `Placeholder functions for
  the plugin 'AGSflashlight' found` -- the port resolves them to no-op stubs, so they are cheap,
  AND MMD's darkness/flashlight effect is not drawn under this port (a correctness note, outside
  this slice).

Engine side of the per-tick APIs (read): `FindGUIID` is a linear name compare over all GUIs
(`global_gui.cpp:45`); `SetButtonPic` -> `Button_SetNormalGraphic` is guarded (no redraw, no log
when the slot is unchanged); `SetGlobalInt` logs only on change, but `debug_script_log` formats
its string BEFORE any channel filter (`debug.cpp:423`), so every logging call pays a
`vsnprintf` whether or not anything prints.

**What this changes in the prediction (written before any run):** the per-tick path is
roughly 100-150 engine API calls in straight-line code with no loops, not a hot interpreter
loop. So I now expect **API time >= VM self time** (H1 < 50%), spread over many names, with
`GetLocationName`/`GetLocationType`/`GetGUIAt`/`GetGUIObjectAt`/`FindGUIID` the likeliest top
entries. No single one is expected to be >= 25% (H2 still expected falsified). The
pre-registered thresholds in 2.1 are unchanged; this is a revised lean, not a revised test.

### 4.1 Compatibility finding: the AGSflashlight effect is never drawn (not a speed issue)

`vendor/ags/Engine/plugin/plugin_stubs.cpp:130-138` registers AGS's own no-op stubs for
`agsflashlight` (`Set*` -> `Sc_PluginStub_Void`, `Get*` -> `Sc_PluginStub_Int0`), and the port
builds with `AGS_BUILTIN_PLUGINS=OFF`, so S2M1 logs `Placeholder functions for the plugin
'AGSflashlight' found`. The calls resolve and cost next to nothing; the effect is absent.

Where MMD uses it (static read, `lab-mmd/scdis.py`): global `AdjustLights()` (L912-933) reads
the room property `lightsource`, then sets `SetFlashlightDarkness(GetFlashlightMaxLightLevel())`
(a dark room) or `SetFlashlightBrightness(GetFlashlightMinLightLevel())`, and when three
GlobalInts and the player character match, a flashlight that follows the mouse
(`SetFlashlightDarknessSize`/`BrightnessSize`/`FollowMouse`). Callers: `repeatedly_execute`
(behind two timer blocks, L1827-1841), `on_event` (room entry), `SetPlayer` (switching kids),
`GiveInvEx`, `inventory8_a`, and `ClickOnLightSwitch`. Rooms that reference
`ClickOnLightSwitch`/`AdjustLights`: **5, 10, 13, 18, 24, 31**. In those rooms, with the lights
off, the original game darkens the screen (or shows a flashlight circle); this port shows them
fully lit. Since `Get*LightLevel` stubs return 0, the script's own darkness value is 0 too. The
probe's `api` table will give the call rate (expected: rare outside room entry and the two
timer blocks).

---

## 5. Runs (2026-09-23, DOSBox-X, ranking only; all under the hub lock taken EXCLUSIVE per series)

Binaries: `AGSBASE.EXE` sha256 `b395af34b208...` (the 0209 series head, clean tree) and `AGSPROBE.EXE`
`d0c050167f6d...` (the same plus `lab-mmd/probe-0290-mmdprobe.diff`, which gained the empty-pair
calibration after the smoke run). Uniform: `--fixed-timestep`, `SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1`,
`--no-verify-present`, the S2M1 512x384 round config staged as `ACSETUP.CFG`, sound off. Mode line
`512 x 384 (16-bit) fullscreen` in every run. Raw: `tests/harness/results/<TAG>-2026-09-23/`
(`STDOUT.TXT`, `RUNMANI.LOG`, `RUN.BAT`, `RUN.txt`); tools `lab-mmd/run-series.sh`, `run-play.sh`,
`drive-play.sh`, `analyze.py`, `room.py`.

**Deviations from 2.3, stated:**
1. **Fixed cycles.** The first series (MMDCS-*) ran at `cycles=max` (the `--fast` default). Identical
   code drifted run to run: `render_backbuffer` 1.103-1.701 ms/call; the two baseline arms read the
   script event at 1.975 vs 1.658 ms/tick (host load ~5 from other workers' builds; the lock
   serialises DOSBox-X, not the CPU). Re-run as MMDCF-* with `tools/dosbox-x.conf` (`core=normal`,
   `cycles=fixed 40000`): **zero spread** -- MMDCF-B1 and -B2 `STDOUT.TXT` are byte-identical; O1=O2
   and P1=P2 to the microsecond. Every ms below is MMDCF (or PLAY at the same conf). MMDCS stays on
   disk as recorded. Caveat: fixed cycles charges ~1 cycle per emulated instruction, so it ranks by
   instruction count, not 486 CPI.
2. **The `api_us` correction.** A DOSBox-X `uclock()` read costs 2.97 us (`cycles=max`) / 4.22 us
   (fixed): as much as a whole API call. `api_us` is therefore reported corrected by one empty-pair
   reading per call (`pair_ns`, measured in-run, 1000 pairs): `api_corr = api_us - n x pair`.
3. **Harness workarounds** (not patched, reported): an AGS_EXE name over 8.3 is "Bad command";
   `run-dosbox.sh` exits 1 before printing the stage dir when no `presentverify` line exists
   (`set -e` + `pipefail` on the `_pv=` grep). The runners find the stage by its own `RUN.BAT`.
4. **MMD-PLAY window:** P1 was idle in room 1 (I did not get clicks in before the run ended; the
   intro is long), so P2 re-ran it with `drive-play.sh`: hover over named things every 1 s and a
   hold-then-release walk click every ~11 s (20 clicks). The hover path never reached
   `VariableExtensions` (no hovered name carried an extension); recorded as not exercised.

### 5.1 MMD-CS (character select, room 50, 1000 ticks, fixed 40000)

| arm | dispatch ms/tick (excl. fade) | script event ms/tick | `script_vm` ms/tick | `render_backbuffer` ms/call |
|---|---|---|---|---|
| B1 = B2 (baseline) | **11.409** | **10.984** (96.3%) | 11.159 | 9.419 |
| O1 = O2 (probe, API clocks off) | 13.435 | 12.948 | 13.170 (+18.0%) | 9.410 |
| P1 = P2 (probe, API clocks on) | 15.189 | 14.692 | 14.945 (+33.9%) | 9.382 |

Probe fields (P1; counts are identical in O and P):
- `dispatch room=50 n=1000 nested_n=0 nested_us=0 maxdepth=0 rts_n=13 rts_us=25652`; `dtop rank=1
  tick=0 us=582152 rts_n=13 evmask=0x40c` = the fade-in (894 ms on the 486).
- `entry repeatedly_execute calls=999`: **5,624 VM instructions and 174.0 API calls per call**.
  `room_b` (the room's rep-exec): 24 instructions, 1 API, 0.10 ms. Hotspot events: 0.04 ms/tick.
- API, corrected, **1.04 ms/tick** over 21 names (P1, `pair_ns=4224`): `GetLocationType` 3/tick 0.191,
  `SetButtonPic` 20/tick 0.180, `FindGUIID` 23/tick 0.172, `GetLocationName` 1/tick 0.070, `GetInvAt`
  5/tick 0.062, `StrCopy` 6/tick 0.061, `StrContains` 0.058, `StrFormat` 0.055, `GetGlobalInt`
  54/tick 0.052, `StrGetCharAt` 28/tick 0.045, `SetLabelText` 2/tick 0.029, `GetGUIObjectAt` 0.025.
- Script functions, exclusive instructions per tick: `CheckTimers` 1,232 (30-pass loop),
  `SetAlternativeAction` 1,102 (x10), `Extension` 1,062 (x14), `IsOwnTimerExpired` 600 (x24),
  `GlobalCondition` 491 (x5), `repeatedly_execute` 406, `CheckDefaultAction` 323,
  `UpdateActionBar` 141, `TranslateAction` 85.
- Engine-side GUI: `gui_poll` 0.011 + `gui_context_cursor` 0.136 = 0.15 ms/tick (baseline).

**The split of the baseline script event (10.98 ms/tick):** API (corrected) 1.04 ms = 9.5%;
interpreter (VM self) about 9.7 ms = ~88%; wrapper ~0.2 ms. As shares of dispatch excluding the
fade (11.41): **VM ~85%, API ~9%, room rep-exec + hotspot + dispatch wrapper ~5%, nested 0%.**
VM per instruction at fixed 40000: ~1.7 us (about 69 emulated x86 instructions per VM op). Scaled
to the 486's 24.26 ms/tick with the same split: ~21 ms VM = **~3.8 us, ~250 cycles per VM op**
(an estimate; the hardware cell in section 8 measures it).

Probe cost (pre-registered 20% bar): the O arm moves `script_vm` +18.0% (under the bar); the P arm
+33.9% (over), so API ms come from the corrected P arm and the ranking rests on counts.

Cross-ratio check (2.1): 486 / DOSBox-X at fixed 40000 -- `render_backbuffer` 9.43 / 9.42 = 1.00;
script event 24.26 / 10.98 = 2.21. **Over the pre-registered 2x flag.** Read, not resolved: no API
on the path does DOS/BIOS/port I/O per call (source read, all 21), so the likelier cause is CPI:
fixed cycles charges one cycle per instruction, and the VM is branchy, call-heavy, large-footprint
code that a 486 (8 KB cache) runs at far worse CPI than a tight blit loop. Hardware cell HW-MMD-1
settles it.

### 5.2 MMD-PLAY (the game's own flow, fixed 40000, display :261)

Flow in both runs: `Now in room 50` -> 40 -> 49 -> 46 -> **1** (in front of the mansion, the first
in-play room; the intro rooms 40/49/46 are cutscenes). Kids: Dave + Syd + Bernard, picked with held
clicks; START clicked; intro not skipped. Witness sheets: `MMDPLAY-P1/-P2 .../series/sheet.png`
(reviewed: selection, intro, credits, room 1 complete; in P2 Dave walks between the click targets;
no trails at sheet scale).

- **Nested-tick positive control (the counter is not blind):** each intro room's cutscene runs
  inside ONE dispatch -- room 40 `room_a` 31.2 s with `nested_n=1253 maxdepth=2 rts_n=1248`, room 49
  12.3 s / 501, room 46 30.8 s / 1234, room 1's entry `room_b` 39.7 s / 1596. That is H0's shape,
  and it is real -- but only in blocking cutscenes, where the ticks keep running and rendering.
- **Room 1 in play** (P2, 6,990 dispatches after the entry cutscene; 20 walk clicks):
  dispatch **15.71 ms/tick** (probe P arm), `repeatedly_execute` **5,618 instructions, 173.6 API
  calls, 14.45 ms/call** -- the same as the character select (P1 idle: 5,624 / 174.0 / 14.48); room
  rep-exec `room_c` 121 instructions, 9 APIs, 0.40 ms/tick; API corrected 1.24 ms/tick, same names
  and order. Prediction ("within 2x of MMD-CS") met: it is the same script at the same cost.
- **A second in-play cost, per walk click:** `on_mouse_click` -> `Room::ProcessClick` 15 calls,
  **mean 58 ms, max 150 ms** at fixed 40000 (walk pathfinding, the legacy path finder). One click is
  2-6 ticks of hitch in emulation, likely 2x that on the 486.

---

## 6. Verdicts (pre-registered thresholds from 2.1)

| | verdict | numbers |
|---|---|---|
| H0 nested-loop accounting | **FALSIFIED** for play and character select | nested 0 of 11.41 ms/tick, `maxdepth=0`, in-dispatch renders = the 13 fade steps only (S2M1 on the 486: 0 nested ticks by call count). True, and harmless, only in blocking cutscenes (5.2) |
| H1 interpreter | **SUPPORTED** | VM self ~85% of dispatch (~9.7 of 11.41 ms/tick at fixed 40000); 5,624 VM ops per tick |
| H2 one DOS-expensive call | **FALSIFIED** | largest single API `GetLocationType` 1.7% of dispatch; no per-call DOS I/O on the path (source) |
| H3 GUI polling | **FALSIFIED** | GUI-control APIs (`SetButtonPic`, `FindGUIID`, `SetLabelText`/`Color`, `GetGUIAt`/`ObjectAt`) ~0.42 ms/tick = 3.7%; engine-side 0.15 ms/tick = 1.3% |

**The 894 ms outlier (S2M1), on its own line:** the room-50 fade-in, `kAGSEvent_FadeIn` inside
dispatch at tick 0: 13 direct `render_to_screen` calls, no nested tick (582 ms at fixed 40000). A
per-room-entry cost, not a per-tick one; every room entry pays it (1.31 s at fixed 40000 for rooms
40/49/46/1, 16 steps each).

**Named mechanism:** MMD's global `repeatedly_execute` -- a verb-template action-line refresh that
runs every tick whether or not anything changed (30 timer checks in `CheckTimers`, 24
`IsOwnTimerExpired`, 10 `SetAlternativeAction` each re-scanning the hovered name with
`Extension()` and re-setting two button pictures, 3-5 `GlobalCondition`, `UpdateActionBar`
re-formatting the action line) -- costs **5,624 bytecode instructions and 174 engine API calls per
tick**, identical in the character select and in play. The time is the AGS bytecode
interpreter's per-instruction cost on a 486 (~85% of dispatch), not any one engine call, not GUI
polling, and not nested loops. At an estimated ~3.8 us per VM op on the 486, 5.6k ops is ~21 ms of
a 25 ms tick.

**What the budget needs (486 figures from S2M1, estimate):** a rendered tick today is roughly
script event 24.3 + other dispatch 1.2 + other tick phases ~4.5 + `scene_construct` 2.6 +
`render_backbuffer` 9.4 + present ~1 (alias on) = **~43 ms against a 25 ms budget**. With
everything else unchanged the script event has to fall to ~6 ms: **about a 4x faster interpreter
path**, or a smaller interpreter gain combined with render-side savings. Nothing here requires a
trade the player would notice; it is the size of the engine work that is the finding.

---

## 7. Ranked candidate fixes, by breadth (no fix in this slice)

1. **VM interpreter per-instruction cost (engine-wide: every AGS game's scripts).** In
   `ccInstance::Run()` each op: re-reads and masks the code word, two `CC_ERROR_IF_RETCODE` bounds
   checks, looks up `sccmd_info`, materialises every argument into a `RuntimeScriptValue` (5 field
   stores per arg), calls `FixupArgument()` for literal operands (`movl`, the commonest op in
   `repeatedly_execute`: 836 of 3,031 static), and moves registers/stack slots as 20-byte
   `RuntimeScriptValue` copies. Candidate levers, each to be measured separately: resolve fixups
   once at load instead of per execution; skip arg materialisation for ops that read raw ints;
   hoist the per-op bounds checks to jump/call targets; slimmer register moves. **First step
   (measurement, lab): a per-opcode count per tick on MMD-CS** (one counter per opcode, cheap) to
   weight the levers before writing any of them. Needs a 4x-class result to close MMD alone.
2. **Script -> engine API call path (engine-wide).** 174 calls/tick at ~6 us each at fixed 40000
   (~3.5 VM ops per call): `SCMD_CALLEXT` marshalling (the `DirectPtr()` loop, `RuntimeScriptValue`
   return) plus the `Sc_*` wrappers. Specific, behaviour-preserving: `Button_SetNormalGraphic`
   early-out when the slot is unchanged (it still runs `replace_sprite_changed_callback`,
   `FindAndRemoveButtonAnimation`'s scan and `SetSize` every call; 20/tick here); a name->index
   cache for `FindGUIID` (a linear `String` compare over every GUI, 23/tick); cheaper
   `GetLocationType`/`GetLocationName` hit tests (0.26 ms/tick). Upper bound ~9% of dispatch.
3. **`debug_script_log` formats before any filter (engine-wide).** `String::FromFormatV` runs even
   when no channel prints. Small here (only value-changing calls log), but it taxes every game that
   changes state per tick. Cheap fix: test the channel filter first.
4. **Walk-click pathfinding (engine-wide for legacy-pathfinder games).** `Room::ProcessClick`
   mean 58 / max 150 ms per click at fixed 40000: an in-play hitch per click, separate from the
   per-tick rate. Measure on hardware before touching it.
5. **Room-entry fade (engine-wide, 16-bit).** 894 ms per entry on the 486 (13-16 full renders).
   Already has ags 0122's fast step; a per-transition cost, not a rate one.
6. **Title-specific:** none. MMD's own script (the 30-pass timer loop, the per-tick
   `SetAlternativeAction` refresh) is user-supplied game data and is not modified.

Correctness finding carried alongside (4.1): AGSflashlight is stubbed, so the dark rooms
5/10/13/18/24/31 draw fully lit.

---

## 8. Hardware cells wanted (the coordinator batches rounds and asks the operator)

All HW-486-66 Mach64, 512x384 round config (the S2M1 one), fixed timestep, sound off, direct
framebuffer. Character select to tick 1000 (~36 s of ticks at the 486's rate, plus boot and
collection, ~3-4 min each).

- **HW-MMD-0** (step 9.0 re-baseline): clean binary at the current head (alias on), character
  select, tick 1000. S2M1 was pre-alias. Gives today's dispatch, `render_to_screen` and the budget.
- **HW-MMD-1** (settles the cross-ratio flag and gives the 486's cost per VM op and per API):
  `AGSPROBE.EXE`, same cell. Expect ~5,624 insns/tick. `pair_ns` on the 486 corrects `api_us` (the
  486's `uclock()` is 4.9 us). If VM self stays >= 80% of dispatch, the flag is CPI, not I/O.
- **HW-MMD-2**: `AGSPROBE.EXE` with `DOSAGS_MMDPROBE_APITIME=0`: the probe's own cost on the 486.
- **HW-MMD-3** (optional, needed for 9.0's in-play row): the clean binary, the game's own flow to
  room 1 with held vcctrl clicks (select 2 kids, START, let the intro run: about 7 minutes at 40
  ticks/s, longer on the 486), then walk clicks. Gives the in-play rate and the per-click
  pathfinding hitch on real hardware.

Probe reverted from `vendor/ags` after the runs (2026-09-23): the working tree's diff was compared
byte-for-byte with `lab-mmd/probe-0290-mmdprobe.diff` (identical), then the four files were checked
out and the header removed; `verify-patches-applied.sh` passes on the clean tree.

---

## 9. Step 9.2 -- interpreter levers (lab-only, engine-wide)

### 9.1 (of 9.2) Instruments

- **Probe 0291, opcode counts** (`lab-mmd/probe-0291-opcount.diff`, `AGSOPC.EXE` sha256 `c6fce032f858`):
  per room segment and at quit -- count of every opcode, arguments materialised at the loop head,
  `GetStackPtrOffsetRw` calls and entries stepped (LOADSPOFFS / SUB on MAR), `GetStackPtrOffsetFw`
  calls and steps (FIXUP_STACK), `FixupArgument` calls by fixup type, MEMREAD/MEMWRITE by the MAR
  register's value type. Counts only, no clocks.
- **Probe 0292, determinism witness** (`lab-mmd/probe-0292-statewit.diff`, `AGSWIT.EXE` sha256
  `5a92dd80d4ef`): every 25 logic ticks, `DOS-PORT statewit tick= room= chars= objs= gints= gdata=
  rdata= player=x,y` -- FNV-1a digests of every character (room, x, y, z, loop, frame, view, walking,
  animating, flags, wait), the room's objects (x, y, on, view, loop, frame, cycling, moving, sprite,
  transparency, baseline), all GlobalInts, and the live global and room script data.
  `DOSAGS_WIT_PERTURB_TICK=N` moves the player one pixel at tick N: the control.
- Cost model for ranking: `tools/dosbox-x.conf` (`core=normal`, fixed 40000) charges about one cycle
  per emulated instruction, so a handler's x86 instruction count (read from `-S` output of the clean
  `cc_instance.cpp` at the build's own flags, `-O3 -std=c++11 -fwrapv -fno-strict-aliasing`, i586)
  times its per-tick count ranks it in fixed-cycles ms.

### 9.2 (of 9.2) Determinism guard, PRE-REGISTERED before any lever build

Every lever is judged by a pair of builds identical except the lever: clean (for ms) and witness =
clean + 0292 (for equality). **A lever passes only if all of these hold; any difference stops the
slice and is reported.**

Fixtures (no input, so the only difference between arms is the build):
1. **MMD-CS**: `mmd`, the 512x384 round config, `DOSAGS_TAS_AUTO_EXIT_TICK=1000`.
2. **AGS Quest AutoPilot**: `agsquest`, auto-exit 6000 (the AutoPilot quits at ~3560), its own
   phase log `AUTOPLT.LOG` and `PH0N.BMP` captures.
3. **5 Days a Stranger**: `5days`, 512x384 round config, `--startr 3`, auto-exit 2000 (a diagnostic
   entry, the same for both arms; it is an equality fixture, not a measured entry).

Filter, defined now: from `STDOUT.TXT` keep only
- every `DOS-PORT statewit` line, verbatim;
- every line beginning `Game :` that contains neither `DOS-PORT` nor `DOSAGS_XT` (script-driven
  events: room changes, GlobalInt sets, music/sound, cursor modes, views, GUI on/off, speech);
- and compare `AUTOPLT.LOG` verbatim (if it carries a timing field, that field is masked and the
  mask is written down before comparing), and every `PH*.BMP` by sha256.
Everything else (`DOS-PORT tickstats`, `persec`, `stallwhat`, `skipframe`, `room_transition`, the
startup block, `RUNMANIFEST`, `opcount`, `mmdprobe`) is timing or instrument and is not compared.
Equality: the kept sequences identical line for line, same length.

Arms per fixture: `W0` = witness baseline, `W1` = witness lever, `WC` = witness baseline with
`DOSAGS_WIT_PERTURB_TICK` (MMD 300, AGS Quest 500, 5 Days 300). Required: `W0 == W1` and
`W0 != WC` (the control demonstrates power); also `W0` run twice is equal (the baseline is
deterministic on this fixture). Timing mode for the equality runs: `--fixed-timestep`, fixed 40000.

Screen gate: the same three fixtures WITHOUT the fixed timestep (so every tick renders and a freeze
lands on the requested tick exactly), `--freeze-capture` with `DOSAGS_FREEZE_TICKS` at 200, 500, 900
(AGS Quest: 400, 1500, 3000), `screen-equal.py W0 W1` must pass every pair, and `screen-equal.py W0
WC` must fail at least one (the control).

Measurement: clean base vs clean lever, fixed 40000, `--fixed-timestep`, MMD-CS 1000 ticks and AGS
Quest AutoPilot; report per-tick VM ops (unchanged by construction), script-event ms and dispatch
ms before/after, and the running factor toward the ~4x.

### 9.3 (of 9.2) Opcode counts (probe 0291, fixed 40000; raw `tests/harness/results/{MMDOC-1,AQOC-1,5DOC-1}-2026-09-23/`)

| fixture | VM ops / tick | args materialised / tick | notes |
|---|---|---|---|
| MMD-CS (room 50, 1000 ticks) | **5,642** | 8,184 (1.45/op) | `mov` 813, `movl` 722, `subi` 554, `sourceline` 550, `memread4` 454, `push` 384, `pop` 299, `farpush` 289, `jzi` 183, `farcall` 175, `setfuncargs` 175, `farsubsp` 168; stack walk 430 calls/1,144 steps; fixups 417 none / 204 import / 64 func / 43 gdata / 28 string; MAR reads 383 stack / 42 global |
| AGS Quest AutoPilot (per room segment) | 7 - 35 (327 in the 2-tick menu) | 7 - 44 | quits at tick 3570 |
| 5 Days room 3 (`--startr 3`, 2000 ticks) | 44 | 63 | |

**Finding that bounds every interpreter lever:** only MMD is interpreter-heavy. Its verb template runs
128x 5 Days' and 160-800x AGS Quest's per-tick bytecode. An interpreter lever is engine-wide in code,
but its payoff lands on script-heavy games (template games like this one); on the other two fixtures
every lever below is under 0.1 ms/tick, while the correctness risk applies to all of them.

Handler costs, read from the clean build's `-S` output (i586, `-O3`): the shared loop head is ~21
x86 instructions + 6 per argument + 5 on the back-edge; handler bodies are 6-25 (`farcall` 70,
`pop` 41, `ret` 38). At ~69 emulated instructions per VM op (9.7 ms / 5,642 ops x 40,000/ms), the
loop head and argument decode are about half of all interpreter time.

Levers ranked by (MMD ops or args per tick) x (x86 instructions saved), fixed-40000 ms estimate:

| lever | estimate (MMD) | behaviour risk |
|---|---|---|
| G. pre-decode the bytecode once (argument count, fixups resolved, handler index) -- structural | ~170k instr/tick, **~4 ms** | highest: touches every op's decode |
| B. loop-head decode kept in registers (instance id, arg count stored twice today) | ~34k, ~0.85 ms | low |
| **A. arguments decoded as plain ints (5 stores -> 1 per arg)** | **~29k net, ~0.72 ms** | **lowest: 3 handlers complete their value** |
| C. `sourceline` fast path ahead of decode | ~14k, ~0.35 ms | low (currentline/hook kept) |
| D. `subi`-on-MAR / LOADSPOFFS stack walk | ~13k, ~0.3 ms | medium |
| F. `memread4`/`memwrite4` type switch | ~7k, ~0.2 ms | medium |
| E. per-execution `FIXUP_IMPORT` lookup | ~6k, ~0.15 ms | low (subsumed by G) |

A-F together are ~1.35x on MMD's interpreter time; **the ~4x the budget wants is not reachable with
micro-levers.** Only G is in that class. A is first because it is the smallest behaviour surface, and
it also tests the whole guard end to end.

### 9.4 (of 9.2) Lever A, ags patch 0293 -- PRE-REGISTRATION (before any lever run)

Change (`lab-mmd/lever-0293-intargs.diff`, working tree only until it passes): the loop head stores
each argument as its `IValue` only; `LITTOREG` and `WRITELIT` call `SetInt32(IValue)` on their
second argument before `FixupArgument` (the exact value the old head built); `NEWARRAY` reads
`Arg3i() != 0` (== `GetAsBool()` on an int-set value: `Ptr` null, so `!IsNull()` is `IValue != 0`).
No other handler reads an argument as anything but `IValue` (`grep` of `codeOp.Arg[123]()` /
`codeOp.Args[`: those three only; `DumpInstruction` under `DEBUG_CC_EXEC`, compiled out, would print
stale types). Builds: `AGSL1.EXE` sha256 `101ca62a8527` (clean + 0293), `AGSL1W.EXE` `6bbaa18a36d8`
(+ 0292 witness).

Predictions (fixed 40000, `--fixed-timestep`, clean builds B vs L1):
- VM ops per tick unchanged exactly (MMD 5,642; a script property, not the interpreter's).
- x86 instructions: the head's per-argument work goes from 6 to 2 (read in `-S` output), so MMD
  -32.7k per tick for arguments, +~3.8k for the three completing handlers: **~-29k/tick**.
- MMD-CS script event **10.98 -> 10.26 ms/tick (-0.72, band -0.4 to -1.0)**; dispatch 11.41 -> ~10.69.
  Running factor toward ~4x: **1.07x**.
- AGS Quest and 5 Days: under 0.01 ms/tick of script change (7-63 args/tick).
- Voids: VM op counts differ between arms (the counting is wrong or the lever changed control flow).

Witness, as pre-registered in 9.2: `detdiff.py W0 W1` EQUAL on MMD-CS, AGS Quest, 5 Days; W0a == W0b;
W0 != WC on each; screen gate W0 vs W1 at the freeze ticks pass, W0 vs WC fails somewhere. Stop and
report if any W0/W1 difference appears.

### 9.5 (of 9.2) Lever A (0293) -- RESULT, and a STOP on the 5 Days fixture

All cells fixed 40000, the lock SHARED (hub bb5482c), raw `tests/harness/results/<TAG>-2026-09-23/`.

**Filter implementation fix (before reading any lever verdict, recorded):** the first MMD W0-vs-W1
comparison differed at `Game : (room:50) preloop_game_start_script_ms=92` vs `=86`. That line is in
the startup timing block, which 9.2 lists as not compared, but its inner lines are `Game :` lines
with no `DOS-PORT` tag, so the kept-line rule let them through. `detdiff.py` now cuts the block by
its `[DOS-PORT-STARTUP-BEGIN]`/`[...-END]` markers, as the pre-registration's own exclusion list says.
No other rule changed.

**Timing (clean builds; MMDTB is byte-identical to MMDCF-B1 from 9.1):**

| | MMDTB (base) | MMDTL1 (0293) | change | predicted |
|---|---|---|---|---|
| script event ms/tick | 10.984 | **10.231** | **-0.753** | -0.72 (band -0.4 to -1.0): **met** |
| dispatch ms/tick excl. fade | 11.409 | 10.652 | -0.757 | ~-0.72 |
| `script_vm` ms/tick | 11.159 | 10.397 | -0.762 | |
| VM ops / tick (probe 0291 on each: MMDOC-1 vs MMDOCL1) | 5,642 | 5,642 | every `opcount` line identical | unchanged: **met** |
| AGS Quest dispatch / `script_vm` ms/tick (AQTB vs AQTL1) | 37.472 / 25.298 | 37.473 / 25.297 | none | < 0.01: **met** |

Running factor on MMD's script event: **1.074x** (x86 instructions: about -30k of ~389k per tick).
The 2.2x CPI flag means the 486 gain from interpreter work is likely larger than fixed-cycles
shows; counts carry the claim.

**Determinism guard:**
- MMD-CS: W0a == W0b EQUAL (61 kept lines, 40 statewit); **W0 == W1 EQUAL**; W0 vs WC DIFFERENT
  first at `statewit tick=300` (player 203 -> 204): the control has power.
- AGS Quest AutoPilot: W0a == W0b EQUAL (483 kept, 142 statewit, 39 AUTOPLT lines, 3 PH*.BMP);
  **W0 == W1 EQUAL including all three PH*.BMP hashes**; W0 vs WC DIFFERENT (statewit tick=500 and
  PH01.BMP).
- **5 Days: VOID -- its baseline is not deterministic.** W0a vs W0b differ in `gdata` (the global
  script's data) from `statewit tick=1025`, toggling between two digests. Cause, read:
  `engine.cpp:691` `play.randseed = time(nullptr); srand(play.randseed);` and 5 Days' global script
  imports `Random`; the emulated time of day comes from the host, so every run seeds differently.
  W0 vs W1 differs the same way (tick 1525), which therefore says nothing about the lever. Per the
  stop rule, the slice stops here and reports.
- Screen gate (freeze captures): **not run yet** -- stopped before it.

**Proposed remedy (needs the coordinator's OK, not done):** give the witness build (0292, lab-only)
a fixed seed -- `DOSAGS_WIT_SEED=N` -> `play.randseed = N; srand(N)` right after `engine.cpp:692` --
then re-run 5 Days W0a/W0b/W1/WC. That changes only the equality fixture's input, never a
measured binary, and it would make any title that uses `Random` usable as a guard fixture.

---

## 10. Hardware round A: the exact binaries and environment (for the main worker to stage)

**Do not rebuild these.** Both files are chmod read-only in this worktree until round A finishes;
every later lab build is written under a different name.

| file (`~/git/dosags-lab-mmd/build/lab/`) | sha256 | what it is |
|---|---|---|
| `AGSBASE.EXE` | `b395af34b208d7818d4e48727f4e1e478a110d93fdf4f73b00352d9048165ff0` | the 0209 series head, clean tree (`build_dirty=0`) -- same bytes as `ags-base.exe` |
| `AGSPROBE.EXE` | `d0c050167f6dc91bd7e13f52c500581bcd0dc9843a104e2cdbc2cade74fbb319` | the same + `lab-mmd/probe-0290-mmdprobe.diff` (with the empty-pair calibration); reports `build_dirty=1` by construction; never a gate binary -- same bytes as `ags-0290probe.exe` |

Common to every cell (the S2M1 cell's shape): game `mmd` (`MANIAC.ags` sha256 `25152e54...`, as in
`~/git/dosags/tests/harness/games/mmd/`), config `tests/harness/presentation/trilbysnotes/ACSETUP-OFF-512X384-ROUND.CFG`
staged as `ACSETUP.CFG` (sha256 `25c9c3d31972188474f98d0be4fd298d2b8aea13cb2b07da14b5d5b4ce8990cb`), run-hw's default fixed timestep, sound off, no input,
`--env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env DOSAGS_TAS_AUTO_EXIT_TICK=1000`.

| cell | binary | extra env | expected on the logs | read |
|---|---|---|---|---|
| HW-MMD-0 | `AGSBASE.EXE` | none | mode line `512 x 384 (16-bit)`; `Now in room 50` | the 9.0 re-baseline: `tick_rate_steady`, stable rate, `process_events_dispatch`, `evtype script`, `render_to_screen` |
| HW-MMD-1 | `AGSPROBE.EXE` | none | `mmdprobe cost ... apitime=1`; `entry ...repeatedly_execute ... insns=` ~5,624/call | 486 us per VM op (`self_us/insns`), per-API us corrected by `pair_ns`, the cross-ratio flag |
| HW-MMD-2 | `AGSPROBE.EXE` | `DOSAGS_MMDPROBE_APITIME=0` | `mmdprobe cost ... apitime=0` | the probe's own cost on the 486 |

`DOSAGS_MMDPROBE_APITIME` is not in the RUNMANIFEST environment allowlist, so `env_block_sha` will
match HW-MMD-1's; the `mmdprobe cost` line's `apitime=` field is the witness that it took effect.

### 9.6 (of 9.2) Seed hook (0294) and lever B (0295) -- PRE-REGISTRATION (before any 0295 run)

**ags 0294, test harness hook (coordinator decision 2026-09-24):** `DOSAGS_RNG_SEED=<n>` replaces
`play.randseed = time(nullptr)` in `engine_init_game_settings()` only when set; unset, the seed is the
time of day exactly as before (shipping behaviour unchanged). Added to the RUNMANIFEST env allowlist
(alphabetical, between `DOSAGS_PRESENT_VERIFY` and `DOSAGS_TAS_AUTO_EXIT_TICK`), so a seeded cell's
`env_block_sha` says so. Diff `lab-mmd/patch-0294-rngseed.diff`. Seeded witness builds: `AGSWITS.EXE`
`4a2a989dcbbf` (base + 0294 + 0292), `AGSL1WS.EXE` `e1968d3fe510` (+ 0293). 5 Days guard re-run with
`DOSAGS_RNG_SEED=12345` (cells 5DSW0a/b, 5DSW1, 5DSWC): W0a == W0b must now be EQUAL before W0 vs W1
means anything.

**ags 0295, lever B -- decode into locals** (`lab-mmd/lever-0295-decode-locals.diff`, on top of 0293):
the loop head decodes the opcode, argument count and arguments into function locals instead of the
`ScriptOperation codeOp` struct. `codeOp` is address-taken (`FixupArgument(codeOp.Args[1], ...)`) and
the build uses `-fno-strict-aliasing`, so today every field is a memory store per instruction -- the
instance id and the argument count twice each -- read or not. The instance id (only `CALLAS` uses it)
is computed there from the saved code word. The three argument locals are declared once outside the
loop (zeroed once), set per instruction only as far as its argument count, the same contract the old
`Args[]` had. 106 accessor uses (`Arg1i/2i/3i`) become the locals; `LITTOREG`/`WRITELIT` still build
`codeOp.Args[1]` for `FixupArgument`; the `DEBUG_CC_EXEC` dump fills `codeOp` from the locals.
Compiles with no `-Wmaybe-uninitialized` warning.

Read in the `-S` output: the loop head before the argument switch goes from **15 to 10 x86
instructions** (the stores of the code, the instance id twice, the argument count twice, and the
shift, become one spilled code word and one argument count). Argument loads unchanged (2 per arg).

Predictions (fixed 40000, clean builds L1 = base+0293 vs L2 = base+0293+0295):
- VM ops per tick unchanged (probe 0291 ported onto 0295 = `AGSOCL2.EXE` `a0e881f00998`; every
  `opcount` line identical to MMDOC-1).
- **-5 x86 instructions per VM op x 5,642 = -28.2k/tick -> MMD script event 10.231 -> ~9.53 ms/tick
  (-0.70, band -0.4 to -1.0).** Cumulative from base 10.984: **~1.15x**.
- AGS Quest: under 0.01 ms/tick change.
- Builds: `AGSL2.EXE` `5a2c83a71560` (timing, no 0294), `AGSL2WS.EXE` `8918b51069dd` (+0294 +0292).

Guard: W0 = `AGSWITS.EXE`, W2 = `AGSL2WS.EXE`, on MMD-CS and AGS Quest (seed unset) and 5 Days
(seed 12345); each W0 == W2 EQUAL, with the W0a == W0b and control results from the same seeded
builds. Stop and report on any difference.

**AMENDMENT to 9.6 (2026-09-24, coordinator decision, before any seeded cell ran):** the seed moves
INTO the lab-only witness build as `DOSAGS_WIT_SEED` (`lab-mmd/probe-0292-statewit.diff` now also
patches `engine_init_game_settings()`); ags 0294 / `DOSAGS_RNG_SEED` is withdrawn (diff deleted, never
in the series, never in a measured binary). The two queued series were stopped before they started
(no result directories). Rebuilt witness binaries: `AGSWIT2.EXE` `e4b60af68566` (base + 0292),
`AGSL1W2.EXE` `7838bd575a0e` (+0293), `AGSL2W2.EXE` `128699f28e3c` (+0293 +0295). Timing and
opcount binaries unchanged (`AGSL2.EXE` `5a2c83a71560` and `AGSOCL2.EXE` `a0e881f00998` never
contained the seed). The `AGSWITS`/`AGSL1WS`/`AGSL2WS` builds are superseded, unused.

---

## 11. Lever G -- pre-decode the bytecode once: DESIGN (read-first and pre-registration only; NO CODE)

For the coordinator to take to the operator. Every figure is MMD at fixed 40000 unless stated.

### 11.1 What exists today (read in `vendor/ags` at the 0209 head)

- Each primary script instance copies the script's code into `ResolvedScriptData::code` (an
  `intptr_t` per word, 4 bytes on DJGPP) and a parallel `code_fixups` byte per word (`_Create`).
  Forks (`repExecAlways` etc.) share the same `_scriptData`.
- Load-time work already done: `FIXUP_GLOBALDATA` words are replaced by a `ScriptVariable*`
  (`CreateRuntimeCodeFixups`); `FIXUP_IMPORT` words become an index into the system import table
  `simp`, and a `CALLEXT` whose import is another script's function is rewritten to `CALLAS` with
  that instance's id in bits 22-31 (`ResolveImportFixups`).
- Per-execution work that G would move to load: masking the code word, looking up the argument
  count (`sccmd_info`), checking the opcode range, and -- for `LITTOREG`/`WRITELIT` (755/tick on MMD)
  -- `FixupArgument`'s switch on the fixup type; for `FIXUP_IMPORT` (204/tick) a `simp.GetByIndex()`
  and a 20-byte `RuntimeScriptValue` copy; for `FIXUP_STACK` a forward stack walk.
- A code word is `opcode | instance_id << 22`. The opcode uses 7 of its 22 low bits (74 opcodes), so
  **bits 7-21 are free** in every instruction word.
- Import values can change after load: room scripts add their exports to `simp` when a room loads
  and remove them when it unloads (`ImportScriptExports`/`RemoveScriptExports`), so an index can
  point at a different value later. That is why the value is fetched on every execution today, and
  G must keep that behaviour (11.3).

### 11.2 The decoded form, and when it is built

Two layers, both built once per primary instance at the end of `_Create` + `ResolveImportFixups`
(script load and room load; never on a call), shared by forks exactly as `code` is:

1. **Packed instruction word (no extra memory):** at load, each instruction's word gets its
   argument count (bits 7-8) and its second argument's fixup type (bits 9-11) written into the free
   bits. The loop head then reads one word and dispatches: no `sccmd_info` load, no argument-count
   chain, no range check (validated once at load: an unknown opcode or an argument running past the
   end fails the load with the same error text it gives at run time today).
2. **Threaded dispatch:** the `switch` becomes GCC's computed goto (`goto *handler[op]`, a documented
   GCC extension DJGPP's gcc 12.2 supports), each handler ending in its own "decode next and jump".
   This removes the jump back to the loop head and the separate loop-condition test; the abort flag
   is still tested per instruction (same place in the sequence), and `CALL`/`RET`/`CALLAS` keep
   their `continue` semantics.
3. **Import cache with a generation check:** a 20-byte `RuntimeScriptValue` slot per `FIXUP_IMPORT`
   site, filled at load, plus a `simp` generation counter bumped by every `Add`/`Remove`. A site
   whose cached generation differs re-reads `simp.GetByIndex()` exactly as today. Stable imports (the
   engine API, which is almost all of MMD's 204/tick) never re-read.

Not in G (each is separate and smaller): register-to-register copies of the 20-byte value (`mov`
813/tick), `GetStackPtrOffsetRw`'s backward walk (430/tick), `ReadValue`/`WriteValue` type switches.

### 11.3 How every op's semantics are kept

- **Fixups:** `FIXUP_NOFIXUP`, `FUNCTION`, `STRING`, `GLOBALDATA`, `STACK` give the same value as
  `FixupArgument` does today (the packed fixup type selects the same code, without the switch);
  `STACK` still walks the stack at run time (its result depends on the live stack); `IMPORT` via
  the generation-checked cache (11.2.3), which re-reads whenever `simp` changed, so a room script's
  exports swapped by a room change are seen exactly as now.
- **Imports and CALLAS:** the load-time `CALLEXT`->`CALLAS` rewrite stays as it is; G only adds bits
  below bit 22, so the instance id is untouched.
- **Strings:** unchanged (`_strings + offset`, resolved per use).
- **Jumps:** unchanged. Offsets stay in code-word units and the code array is not reordered or
  compacted, so every relative jump, `CALL` target (a pc loaded into a register), export address
  (`ResolveExports` takes a code pointer) and pushed return address means what it means now.
- **Debugger and line numbers:** `SCMD_LINENUM` keeps writing `_lineNumber`/`currentline` and calling
  `new_line_hook` on every execution; `_pc` stays a word index, so `GetCallStack`/`GetScriptPosition`
  and `DetermineScriptLine` read the same positions.
- **Anything reading `code` as original bytecode:** `DetermineScriptLine` (error messages) masks with
  `INSTANCE_ID_REMOVEMASK`; it must mask the new bits too (`& 0x7F`). Every reader of `_code` gets
  audited for the same (`grep`), and the audit list is part of the patch.
- **Timeout watchdog:** the backward-jump loop counter and the `FastClock` check stay per backward
  `JMP`, unchanged.

### 11.4 Memory cost

- Packed words: **0 bytes** (bits already there).
- Handler table: 74 pointers, 296 bytes, static.
- Import cache: 20 bytes x import sites x loaded instances, plus a 4-byte generation per site. MMD:
  25,850 import fixups over all 51 scripts; live at once = the global script plus one room (+ the
  dialog script), at most ~9-12k sites -> **~0.25 MB** worst case (MMD's global + room 2). 5 Days:
  3,309 in total (~60 KB live). AGS Quest: 1,030 (~20 KB).
- 5 Days' and AGS Quest's whole bytecode is 81k and 24k words; MMD's is 537k (global 130k, largest
  room 68k), so MMD is also the memory worst case among the fixtures.

### 11.5 Realistic estimate (x86 instructions per VM op, from the `-S` output and the op counts)

| stage | instr / op | MMD script event, fixed 40000 | factor from base |
|---|---|---|---|
| base | ~69 | 10.98 ms | 1.00x |
| + A (0293, measured) | ~63 | 10.23 ms | 1.07x |
| + B (0295, predicted) | ~58 | ~9.53 ms | ~1.15x |
| + G (packed word -3/op, threaded dispatch -5/op, import cache -25 x 204/tick, no-fixup path -6 x 417/tick) | **~49** | **~8.2 ms** (-1.3) | **~1.34x** |

**The ~4x the budget wants is not reachable by interpreter work.** After G the remaining ~49 per op
are handler bodies (~15), 20-byte value copies, stack pushes/pops and the stack walk, and the 174
engine API calls (1.04 ms) -- each a separate, smaller lever, and the value-copy one is an
engine-wide type change. Stacking everything in 9.3's table plus G plausibly reaches ~1.5-1.7x on
MMD's script event at fixed cycles. The 2.2x CPI flag (5.1) says the 486 may gain more per removed
instruction than fixed cycles shows (stores are the expensive thing a 486 does, and A/B/G remove
stores); HW-MMD-1 plus one hardware cell per landed lever measures that. On the 486 figures from
S2M1, a rendered MMD tick is ~43 ms against 25; at ~1.6x on the script event it is ~33-34 ms
(~30 fps) unless `render_backbuffer` (9.4 ms) and the other phases also move. That is the trade to
put to the operator with the G decision.

### 11.6 How equivalence would be proven (the 9.2 guard, extended)

- The determinism guard as pre-registered (statewit every 25 ticks, `Game :` events, `AUTOPLT.LOG`,
  `PH*.BMP`), `W0 == WG` on MMD-CS, AGS Quest and 5 Days (seeded), with the baseline-twice and
  perturbation-control results on the same builds; plus MMD-PLAY driven through the intro (the
  cutscenes' blocking calls, `CALLAS` into room scripts across five room changes, which exercises the
  import cache's generation check on every room load).
- Op counts: probe 0291 ported onto G must print every `opcount` line identical to base (G may not
  change which ops run).
- Load-time validation proof: a build that decodes both ways and compares, for every instruction of
  every script in all three games at load, the packed argument count and fixup type against
  `sccmd_info` and `code_fixups` -- a count of mismatches that must be 0, reported per game.
- Screen gate (freeze captures, exclusive lock, display 261) on the three fixtures.
- A control for the import cache: a lab switch that bumps the generation never (stale cache) must
  make MMD-PLAY diverge at its first room change -- evidence the check has power.

### 11.7 What other games gain

In proportion to their per-tick bytecode. The fixtures measured: MMD 5,642 ops/tick, 5 Days 44,
AGS Quest 7-35. At ~20 instructions saved per op across A+B+G, 5 Days saves ~0.02 ms/tick and AGS
Quest less: nothing measurable. The payoff is for games whose scripts run a lot every tick -- the
Lucasarts-style verb templates (MMD's is the Proskrito/Lucasfan lineage) and verb-coin templates
that refresh an action line and button states in `repeatedly_execute`. Their per-tick counts are not
measured here; a count on one or two such titles would size it before the decision.

### 11.8 The whole path to 40, beyond the interpreter (486 estimates; game data untouched)

Basis: S2M1 on the 486 (0194, alias off, character select), per tick unless stated. A rendered tick
today: script event 24.3 + other dispatch 1.2 + other logic 4.5 (`input_handling` 1.08,
`game_objects_update` 1.06, `drawable_object_states` 0.64, `input_poll` 0.48, `objects_scale` 0.52,
`gui_context_cursor` 0.39, `rep_exec_wrapper` 0.39, the rest) + `scene_construct` 2.6 +
`render_backbuffer` 9.4 + present ~0.7-1 (the alias removes S2M1's 7.6 ms RAM copy) = **~43 ms**
against 25. Estimates are ranges, marked by how they were reached; HW-MMD-0/1 replace them.

| lever | where it acts | 486 estimate | risk | basis |
|---|---|---|---|---|
| Interpreter A+B+G | script event 24.3 | **-6 to -8 ms** (to ~16-18) | A, B low; G highest in the engine | fixed-cycles 1.34x; more if the 2.2x CPI flag means stores cost the 486 extra (A/B/G remove stores) |
| Remaining interpreter micro-levers (C-F) | script event | -1 to -2 ms | low-medium | 9.3 table x 2.2 |
| API early-outs: `SetButtonPic` unchanged-slot early return (20/tick), `FindGUIID` name cache (23/tick) | API share of the script event (1.04 of 10.98 at fixed cycles; ~2.3 ms on the 486) | -0.4 to -0.6 ms | low (pure caching of a pure lookup; the setter already no-ops on an equal slot) | per-API corrected times x 2.2 |
| Per-tick engine work (the 4.5 ms "other logic") | input, object updates, cursor/GUI context | -1 to -1.5 ms | low-medium; needs a probe first (e.g. whether `input_handling`'s 1.08 ms is repeated INT 33h mouse calls per tick) | 4.5 ms measured; recoverable share not yet measured |
| `render_backbuffer` | 9.4 ms/render, of which sprite blits ~9.3 (`rb_sprite_time` 716 calls x 3.26 ms / 252 renders; ~39k sprite px per render, 320x57 the largest) | -2 to -4 ms (opaque GUI surfaces as plain copies instead of masked blits; skip re-compositing a GUI whose surface did not change) | medium-high: this is the class that has produced trails before; the screen gate and the present verifier are the guards | S2M1 sprite counters |
| Room-entry fade | not per tick: 0.9 s once per room entry | 0 ms/tick (improves transitions only) | low | `evtype fadein` |

**Sum, and the honest ceiling:** -10 to -16 ms from ~43 -> **~27-33 ms per rendered tick, ~30-37
fps**, with the top of that range needing the risky render work AND the CPI bonus. Holding 40 fps
rendered needs the script event near ~8 ms -- about 3x -- which no semantics-preserving engine work
here reaches. What stays within reach is a different and still valuable line: **the game running at
full SPEED.** Logic alone (everything but rendering) is ~31 ms/tick today; A+B+G bring it to ~23-25
ms, so the 40 Hz logic rate (`tick_rate_steady` >= 39.2) is plausible with the fixed timestep's
catch-up skipping renders -- MMD plays at its correct speed at ~20-30 displayed frames/s. That is not
the Gate 3 bar (which also wants `fps_p50` >= 40), so it is the trade to put to the operator: a
full-speed-at-lower-fps target for MMD, or keep the 40 fps bar and accept that MMD does not meet it
on this machine without changing what its script does every tick.

**Not proposed (changes behaviour):** running `repeatedly_execute` less often than every tick, or
caching `GetLocationName`/`GetLocationType` across ticks -- both alter script-visible timing or
results.

### 9.7 (of 9.2) Seeded 5 Days guard, and lever B (0295) -- RESULTS

**5 Days with `DOSAGS_WIT_SEED=12345` (witness builds `AGSWIT2`/`AGSL1W2`):** 5DSW0a == 5DSW0b
**EQUAL** (101 kept lines, 80 statewit; `gdata` now stable, e.g. `a2091861` at tick 1025 in both);
**5DSW0 == 5DSW1 (lever A) EQUAL**; 5DSW0 vs 5DSWC DIFFERENT at `statewit tick=300` (player 160 ->
161). Lever A's determinism guard is now complete on all three fixtures.

**Lever B (0295) timing (clean builds, fixed 40000):**

| | MMDTL1 (A) | MMDTL2 (A+B) | change | predicted |
|---|---|---|---|---|
| script event ms/tick | 10.231 | **9.474** | **-0.757** | -0.70 (band -0.4 to -1.0): **met** |
| dispatch ms/tick excl. fade | 10.652 | 9.894 | -0.758 | |
| VM ops / tick (MMDOC-1 vs MMDOCL2, probe 0291 ported onto 0295) | 5,642 | 5,642 | every `opcount` line identical | unchanged: **met** |
| AGS Quest `script_vm` ms/tick (AQTL1 vs AQTL2) | 25.297 | 25.296 | none | < 0.01: **met** |

**Running total on MMD's script event: 10.984 -> 9.474 ms/tick = 1.159x** (A 1.074x, B 1.080x on top).
x86 instructions: ~-59k of ~389k per tick so far.

**Lever B guard (W0 = `AGSWIT2`, W2 = `AGSL2W2`):** MMDSW0 == MMDW2 EQUAL; AQSW0 == AQW2 EQUAL
including all three `PH*.BMP`; 5DSW0a == 5DSW2 EQUAL (seeded). Cross-build check: MMDSW0 (`AGSWIT2`)
== MMDW0a (`AGSWIT`, the pre-seed witness): the seed code is inert when unset. The controls with
power are 9.5's (same statewit code) and 5DSWC above.

Screen gate for A and B: running (freeze captures at 200/500/900, AGS Quest 400/1500/3000, no fixed
timestep, exclusive lock, display 261; arms W0, W1, W2, WC).

### 9.8 (of 9.2) 0293 and 0295 as real patches, and the `/sdldos:review` result

`lab-mmd/patches/0293-...patch` and `0295-...patch`: `git format-patch` output of two commits made on a
throwaway branch in `vendor/ags` (deleted; vendor `master` untouched, the series count unchanged).
Held in `lab-mmd/` until the screen gate passes; then they move to `patches/ags/` on the coordinator's
merge. Review against `/sdldos:review`:
1. Provenance: `git am` of both onto a clean worktree at the 0209 head reproduces the measured working
   tree byte for byte (`git diff` compared, `index` lines aside); both also `git am` cleanly on top of
   origin/main's 0210-0213.
2. Slots: 0293 and 0295 are in this worker's range (ags 0290-0309); origin/main uses none of
   0290-0309. 0290-0292 name lab-only probe diffs (never patches); 0294 was withdrawn (9.6
   amendment), a deliberate gap -- the series already has gaps.
3. DJGPP: no `fopen`, no non-ASCII, no SIMD/asm (the only keyword hits are `ASSERT_*`), no new
   64-bit or `size_t` assumptions, no trailing whitespace on added lines.
4. Neutral naming: not applicable (port-owned `patches/ags`, no hint or log name added).
5. Precedent: none cited; 0295 states its dependency on 0293.
6. Not diagnostics: both are permanent engine changes.
7. Built with DJGPP and run on DOSBox-X on three fixtures with the determinism guard EQUAL (9.5,
   9.7); **the screen gate is the remaining condition** before landing.

### 9.9 (of 9.2) Screen gate: the first attempt was VOID (my pre-registration error); AMENDMENT

The 12 screen-gate cells (`*SGW0/W1/W2/WC`) ran without the fixed timestep as 9.2 said, and captured
**no frames**: ags 0195's `dos_port_freeze_check()` is called only from `dos_run_tick_fixed()`
(`game_run.cpp`, source read), so with the fixed timestep off no freeze ever fires. 9.2's premise
("without the fixed timestep every tick renders, so a freeze lands on the requested tick") was
wrong about where the freeze lives. Those cells are void as screen evidence. Their `statewit`
lines are still valid determinism evidence on the non-fixed-timestep path, and they agree: W0 == W1
== W2 EQUAL on MMD, AGS Quest and 5 Days (seeded); W0 vs WC DIFFERENT on all three.

**Amendment, before the re-run:** the screen gate runs WITH `--fixed-timestep` (so 0195's freezes
fire), at `tools/dosbox-x-fast.conf` (`cycles=max`), so the emulated CPU stays ahead of 40 Hz and
every steady-state tick is a rendered tick -- a freeze then lands on the requested tick in every arm.
Pixels do not depend on timing, so this conf choice cannot move the screen result; the tick equality
it needs is checked per pair by `screen-equal.py` (a pair whose actual ticks differ is void, not
equal). Exclusive lock, display 261, arms and freeze ticks as before, tags `*SG2*`.

### 9.10 (of 9.2) Screen gate (re-run per 9.9) -- PASS for 0293 and 0295

`tools/dosbox-x-fast.conf`, `--fixed-timestep`, exclusive lock, display 261, freeze captures via ags
0195. Every arm froze at exactly the requested ticks (MMD and 5 Days 200/500/900, AGS Quest
400/1500/3000; `FRZnn.txt` `tick=` equal to `want=` in all 12 cells). `screen-equal.py` (whole
capture, pixel for pixel, pair void on a tick mismatch):

| fixture | W0 vs W1 (0293) | W0 vs W2 (0293+0295) | W0 vs WC (control) |
|---|---|---|---|
| MMD-CS | 3/3 equal | 3/3 equal | 3/3 equal -- no power here: the perturbed player is not drawn on the character-select screen (expected; the statewit control differs) |
| AGS Quest AutoPilot | 3/3 equal | 3/3 equal | **DIFFERS at tick 400** (124 px, bbox 676,541-685,565) |
| 5 Days (seeded) | 3/3 equal | 3/3 equal | **DIFFERS at tick 200** (1,904 px, bbox 816,711-852,831) |

The gate has demonstrated power (two of three controls fail, as the pre-registration requires "at
least one"). **0293 and 0295 have now cleared every pre-registered guard: determinism (9.5, 9.7, 9.9),
op counts, timing predictions, and screens.**

---

## 12. API early-outs (coordinator-approved, engine-wide, low risk) -- READ-FIRST and measurement

Main at cc5b66f5 (0293+0295 landed). Baseline `AGSM1.EXE` sha256 `9a17a60d3cc1` (clean build of main,
`build_dirty=0`, sha12 `4a5cca2fa1fd`). Probe 0296 (`lab-mmd/probe-0296-apiprobe.diff`, `AGSAPI.EXE`
`c7767d08684e`, lab only, reverted after): counts, and ABLATION switches that measure cost only and are
not semantics-preserving by design. Fixed 40000, 1000 ticks of MMD-CS, lock shared via the hub library.
Raw `tests/harness/results/API*-2026-09-23/`.

**Counts (MMD-CS, per tick):** `FindGUIID` 23.0 calls, **1.91 GUIs scanned per call** (43,961 / 22,978);
`SetButtonPic` 20.0 calls (normal 11.0, mouse-over 9.0, pushed 0), **every one leaving the slot
unchanged** (19,980 of 19,980). AGS Quest calls neither; 5 Days calls `FindGUIID` 1.5/tick, no
`SetButtonPic`.

**Ablations (script event over 999 ticks; the probe-on, ablation-off arm APIC0 = 9,496,724 us):**

| arm | what it skips | script event | per tick |
|---|---|---|---|
| APICF | `FindGUIID`'s whole scan (pointer cache, no validation) | 9,353,655 us | **-0.143 ms** |
| APICS1 | everything after the argument checks for unchanged normal slots (11/tick) | 9,432,282 us | **-0.064 ms** |
| APICS2 | the whole `SetButtonPic` body incl. argument checks (20/tick) | 9,335,170 us | -0.162 ms |
| APIB (no probe) | -- | 9,464,986 us | (the probe's own counters cost +0.032 ms/tick) |

**What an exact early-out may skip (source read):**
- `SetButtonPic` with an unchanged slot must still run `FindAndRemoveButtonAnimation` (setting a
  picture stops a running button animation: script-visible), must still read the sprite's size for
  `SetSize` (a dynamic sprite can change size under the same slot number), and
  `replace_sprite_changed_callback` (idempotent, but skipping it is only exact if the registration is
  already current). `SetCurrentImage`/`SetCurrentColors` are already change-guarded, and
  `UpdateCurrentImage()` runs on every button state change, so re-setting the same image is a no-op.
  What is left to skip is a few compares: **an exact early-out saves at most ~0.02 ms/tick of APICS1's
  0.064** (the rest is the animation stop and the size read it must keep). **Recommendation: do not
  land it** -- the cost is the call path (marshalling and the argument checks, APICS2 - APICS1), which
  an early-out inside the setter cannot reach.
- `FindGUIID`: GUI names are set only when game data loads (`GUIMain::ReadFromFile`) and the list is
  replaced only at `game.cpp:603` (`guis.clear()` on unload) and `game_init.cpp:473` (load); there is no
  script API that renames a GUI, and `ReadFromSavegame` does not touch `_name`. So a cache of
  (query -> first matching index), cleared at those two points, returns exactly what the scan returns.
  A pointer-keyed entry validated by comparing the cached copy of the query text (not the GUI names)
  costs one short `strcmp`. **Worth doing:** upper bound -0.143 ms/tick, expected ~-0.12 ms/tick.

The pre-registration for the `FindGUIID` cache waits for HW-MMD-1/2's API-time split (coordinator,
2026-09-24): it will carry a fixed-cycles prediction, a separate 486 prediction with a wider band,
and the HW-MMD cell that would falsify it.

### 12.1 ags 0297 -- `FindGUIID` answer cache: PRE-REGISTRATION (was a draft; finalised in 13.4 with the 486 band from HW-MMD-1)

**Change** (`lab-mmd/lever-0297-findguiid-cache.diff`, working tree only): a 16-entry cache, direct-mapped
by the query pointer, each entry holding the query pointer, a copy of the query text (< 32 chars) and
the GUI **index** found (an `int` -- never a `GUIMain*` or a name pointer, so no reallocation of
`guis[]` can leave it dangling). Hit iff same pointer AND `strcmp(copy, query) == 0`; otherwise the
original scan runs unchanged (`FindGUIIDScan`) and a found index (>= 0) is remembered. A miss is never
remembered: the scan still `quit()`s exactly as before. `FindGUIIDCacheReset()` is called at both
points the GUI list is replaced.

**Exactness -- where GUI names and the list can change in this pinned revision (source read):**
- Names: `GUIMain::_name` is written only in `GUIMain::ReadFromFile` (`Common/gui/guimain.cpp:657`,
  `:662`), i.e. game data load. No script API renames a GUI.
- The list: replaced only at `Engine/ac/game.cpp:603` (`guis.clear()`, game unload) and
  `Engine/game/game_init.cpp:473` (`guis = std::move(ents.Guis)`, game load) -- both now reset the cache.
- Restore: `ReadGUI` (`Engine/game/savegame_components.cpp:935-947`, and the second component version at
  `:1008-1013`) asserts the save's GUI count equals `game.numgui` (`AssertGameContent`, `:207-216`) and
  reads state into the existing `guis[i]` via `GUIMain::ReadFromSavegame` (`guimain.cpp:749-`), which
  never writes `_name`; it neither resizes nor rebuilds `guis[]`. The before/after-restore hooks
  (`Engine/game/savegame.cpp:518`, `:791`) only unexport/re-export GUI controls.
- Old-format saves: none reach a different path -- `kSvgVersion_LowestSupported = kSvgVersion_Components`
  (`Engine/game/savegame.h:64`), and older saves are refused at `savegame.cpp:299`.
- A restore that loads another game goes through `game_init.cpp:473`, which resets the cache.

**Correctness self-test (probe 0298, `lab-mmd/probe-0298-fgiselftest.diff`, `AGSFGST.EXE` `91905f43fa47`,
lab only):** at `DOSAGS_FGI_SELFTEST=<tick>`, outside any script, for every GUI name and (for `g`-names)
its stripped, upper- and lower-case forms: cached `FindGUIID` twice (a miss then a hit) and through a
second buffer with the same text, each against the uncached scan; a reused buffer with different text
must not return the old answer; then `save_game(998)` and `try_restore_save(998)` (what
`RestoreGameSlot` does outside a script) and the whole comparison again with the cache warm. Run on
MMD-CS, AGS Quest and 5 Days. **Stated: 0 mismatches in every phase, restore=ok.**

**Predictions (fixed 40000, `AGSM1.EXE` vs `AGSFG.EXE` `d1e43cfe54c4`):**
- VM ops and API call counts unchanged (the cache sits inside `FindGUIID`).
- MMD-CS script event **-0.12 ms/tick (band -0.06 to -0.143)** -- the ablation's -0.143 is the upper
  bound, minus a short `strcmp` per hit. AGS Quest: 0 (no calls); 5 Days: < 0.01 (1.5 calls/tick).
- **486: -0.50 ms/tick (band -0.30 to -0.65)** -- from HW-MMD-1 (section 13): `FindGUIID` 32.7 us/call,
  ~8 us of it the call path; the falsifying cell is HW-MMD-5 (clean main + 0297 at the HW-MMD-0 cell)
  against HW-MMD-4 (13.4).

**Guard:** the 9.2 determinism guard (W0 = `AGSMW.EXE` `a53db0db5398`, W1 = `AGSFGW.EXE` `8543b9cb01f3`) on
the three fixtures, and the screen gate as in 9.9.

---

## 13. Hardware round A/B: HW-MMD-0 and HW-MMD-1 scored (HW-MMD-2 pending); the 486 split; MMD decision material

Raw (the main worker's runs): `~/git/dosags/tests/harness/results/HW-MMD-{0,1}-2026-09-24/`. HW-486-66,
Mach64, 512x384 round config, fixed timestep, sound off, character select to tick 1000,
`env_block_sha=d5be4eb3c26d` (the S2M1 value) in both.

**Scored against section 10 exactly as written:**
- HW-MMD-0 (`AGSBASE.EXE`, manifest `binary_sha12=234a4db92f12`, `build_dirty=0`): mode line `512 x 384
  (16-bit) fullscreen` -- met; `Now in room 50` -- met. Read: `tick_rate_steady` 29.09, whole-run 26.75,
  `fps_p50` 7.79 (273 render passes, 726 catch-up ticks); `process_events_dispatch` 26.85 ms/tick;
  `evtype script` 24.72 ms/tick; `render_to_screen` 10.80 ms/call (S2M1 18.50: the alias removed the
  7.6 ms RAM copy, as 11.8 predicted); `render_backbuffer` 9.49; `scene_construct` 2.60; fade 803 ms.
- HW-MMD-1 (`AGSPROBE.EXE`, `build_dirty=1` expected): `mmdprobe cost ... apitime=1` -- met;
  `entry ...repeatedly_execute ... insns=` **5,624/call -- met** (op counts are a script property: same on
  the 486 as in DOSBox-X). Read below.

**The 486 split of the script event (24.72 ms/tick clean):**
- API time (HW-MMD-1, corrected by the 486's own `pair_ns=4272`): **5.30 ms/tick over 175 calls = 21%**
  of the clean script event (fixed-cycles: 9.5%). The VM and dispatch wrapper: **~19.4 ms, ~3.45 us per
  VM op (~228 cycles)** (estimate in 5.1: ~3.8 us). The probe build itself runs the script event at 39.34
  ms/tick (+59% over clean); HW-MMD-2 (API clocks off) splits that cost, pending.
- **Cross-ratio flag (5.1), resolved in part:** 486 / fixed-40000 is 1.01 for `render_backbuffer`, ~2.0x
  for the VM, and **~5.1x for engine API calls** (an upper bound: measured under the probe, see the
  cache confound in 13.2). The call path itself is the expensive thing on the 486:
  `GetGlobalInt`, a one-line getter, costs **8.2 us per call** (~540 cycles, 54/tick = 0.44 ms/tick);
  `SetButtonPic` 52.4 us (20/tick = **1.05 ms/tick**), `FindGUIID` 32.7 us (23/tick = **0.75 ms/tick**),
  `GetLocationType` 218 us (3/tick = 0.66), `StrCopy` 63 us (6/tick = 0.38), `StrGetCharAt` 11.8 us
  (28/tick = 0.33), `GetLocationName` 284 us (1/tick), `StrFormat` 227 us (1/tick).
- Consequence for section 12: fixed cycles under-ranked the API path. The `SetButtonPic` body on the 486
  (~44 us/call after the ~8 us call path) is ~0.9 ms/tick; what share of it an EXACT early-out can skip is
  not known from fixed cycles. The "do not land" recommendation stands on exactness grounds, but its
  size argument was a fixed-cycles one; an on-hardware ablation would settle it (proposed HW cell below).

**0297 486 band (fills 12.1):** `FindGUIID` 32.7 us/call on the 486, of which the call path is ~8 us (the
`GetGlobalInt` proxy); a cache hit replaces the ~25 us scan with a pointer compare and a short `strcmp`
(~2-3 us). **Prediction: -0.50 ms/tick on the 486 (band -0.30 to -0.65)**, against -0.12 at fixed 40000.
(Built on the probe-measured 32.7 us: an upper bound -- see 13.2's cache confound; a result below -0.30
points there first.)
Falsifying cells: **HW-MMD-5** = clean main + 0297 at the HW-MMD-0 cell, scored against **HW-MMD-4**
(clean main, 0293+0295, same cell): script event and dispatch per tick; and optionally HW-MMD-6 = the
0296-style probe on main + 0297, reading `FindGUIID`'s per-call time directly (predicted ~8-11 us/call).

### 13.1 MMD target decision material (for the operator)

486 figures from HW-MMD-0 (the current binary before 0293/0295): **logic 31.3 ms/tick** (dispatch 26.9, of
it the script event 24.7; other logic 4.4) and **13.4 ms per render pass** (`render_to_screen` 10.8 incl.
`render_backbuffer` 9.5 and a 0.7 ms present, plus `scene_construct` 2.6). A rendered tick is **44.7 ms**
against 25. Today: 29.1 logic ticks/s (the game runs at 73% speed) and ~7.8 fps.

Lever estimates on the 486 (fixed-cycles results x the measured ratios: ~2.0x VM, ~5x API; ranges; the
API rows rest on the probe-measured ~5x, an upper bound for a clean build -- 13.2):

| lever | 486 estimate on logic | status | risk |
|---|---|---|---|
| A+B (0293, 0295) | -2.5 to -3.5 ms | landed; HW-MMD-4 measures | low |
| G (pre-decode, 11) | -2 to -3 ms | design only | highest in the engine |
| C-F (micro-levers) | -1.5 to -3 ms | not started | low-medium |
| 0297 FindGUIID cache | -0.3 to -0.65 ms | built, pre-registered pending | low |
| API call path (CALLEXT marshalling, ~8 us x 174 calls = 1.4 ms) | -0.5 to -0.9 ms | not designed | medium |
| other per-tick engine work (4.4 ms) | -0.5 to -1.5 ms | needs a probe | low-medium |
| render side (`render_backbuffer` 9.5 ms per render) | -2 to -4 ms per render | not designed | medium-high |

**The three honest targets (486):**
1. **40 fps rendered (the Gate 3 bar): not reachable.** It needs logic + render <= 25 ms; with render at
   ~10-13 ms, logic would have to fall to ~12-15 ms -- the script event near ~5-8 ms, a 3-5x cut that no
   semantics-preserving engine work here reaches.
2. **Full speed (40 logic ticks/s) at a low displayed rate: plausible, with G.** Every lever except
   render: logic ~31.3 - 10 = **~21 ms** -> 40 x 21 = 840 ms/s of logic, ~160 ms/s left for renders ->
   **~12 fps** (13.4 ms renders), ~15 fps with render-side work. **Without G** (A+B, C-F, API, engine
   work): logic ~23.5 ms -> ~60 ms/s for renders -> **~4-5 fps** at full speed -- not a real target.
3. **Full speed at ~20 fps:** needs logic <= ~18-20 ms AND renders ~10 ms: every lever including G and
   the render work, and the top of each range. Possible, not likely.
This corrects 11.8's "~20-30 fps at full speed" (a fixed-cycles estimate); the 486's 5x API cost and the
measured 13.4 ms render pass move it down to ~12-15 fps.

**What would firm these numbers up before a decision:** HW-MMD-4 (A+B's real 486 gain -- the VM ratio
in practice), HW-MMD-2 (the probe's own cost), and, if G is considered, nothing more is needed first: G's
design (11) and its guard (11.6) stand.

### 13.2 HW-MMD-2 scored, and the probe's own cost on the 486

Raw `~/git/dosags/tests/harness/results/HW-MMD-2-2026-09-24/`. Section 10's expectation: `mmdprobe cost ...
apitime=0` -- **met** (`uclock_reads=12013`: only the entry/dispatch/event clocks; `insns_total=5685500`,
identical to HW-MMD-1). Whole-run 21.79, steady 23.30. Script event **33.49 ms/tick** (HW-MMD-0 clean 24.72;
HW-MMD-1 with API clocks 39.34):
- the instruction counter and function bookkeeping cost **+8.77 ms/tick, +35%** on the 486 (fixed cycles:
  +18%) -- the probe is heavy there, as its per-instruction increment and per-call hash suggest;
- the API clock pairs cost a further **+5.85 ms/tick, ~34 us per call** -- far more than two 4.3 us
  `uclock()` reads; the rest is outside the timed interval (the 64-bit divide in `dp_mmd_us()`,
  `__divdi3` on a 486, and the per-call bookkeeping). So HW-MMD-1's per-API times (inside the interval,
  corrected by one empty-pair reading) stand; the VM share is taken as clean total minus API (13).
- Lesson for the next probe on the 486: time with raw `uclock_t` differences and convert once at dump.
- **Cache confound (coordinator, 2026-09-24), not re-run:** the 486 has an 8 KB unified L1, and the
  probe's per-instruction counter and per-call hash tables run between API calls, so they can evict the
  API path's lines. The per-API figures measured under the probe (`FindGUIID` 32.7 us, `SetButtonPic`
  52.4 us, `GetGlobalInt` 8.2 us) and the **"API ~5.1x" ratio are therefore an UPPER BOUND for a clean
  build**, not a clean measurement. HW-MMD-4/5 (clean builds) test this directly: **if 0297 lands below
  -0.30 ms/tick on the 486, this confound is the first explanation to check, before the call-path model.**

### 13.3 OPERATOR DECISIONS (2026-09-24, via the question tool, relayed by the coordinator)

1. **MMD target: FULL SPEED (40 logic ticks/s) AT ~20 fps** -- the stretch target (13.1 option 3): every
   lever, G included, plus render-side work, each at the top of its range.
2. **Lever G: BUILD IT, with full gates**, as its own patch series in this worker's ags range:
   instruction-for-instruction equivalence against the current VM on MMD, AGS Quest and 5 Days in
   DOSBox-X, including a room change that swaps imports and a save/restore; then a before/after
   hardware cell. It lands only if every gate passes. G's gates and its 486 prediction are
   pre-registered before any G code runs.
Order of work (coordinator): 0297's pre-registration and lab gates; G's design pre-registration; G's
code; then C-F and render-side levers (unless a read-first shows one is cheap and independent).

### 13.4 Hardware cells for the next batch (the coordinator schedules)

Same cell as HW-MMD-0 (mmd, `ACSETUP-OFF-512X384-ROUND.CFG` as `ACSETUP.CFG`, run-hw default fixed
timestep, sound off, no input, `SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1`, `DOSAGS_TAS_AUTO_EXIT_TICK=1000`).
Binaries are chmod read-only here until the batch runs.

| cell | binary (`~/git/dosags-lab-mmd/build/lab/`) | extra env | reads / predicts |
|---|---|---|---|
| **HW-MMD-4** | `AGSM1.EXE` sha256 `9a17a60d3cc19068110cff59602f7bdea708f49b2e649ff6f1d62f5b9e314715` (clean main cc5b66f5: 0210-0213 + 0293 + 0295; manifest `binary_sha12=4a5cca2fa1fd`, `build_dirty=0`) | none | A+B's real 486 gain vs HW-MMD-0: script event per tick. Fixed-cycles cut was -1.51 ms (1.159x); at the measured ~2.0x VM ratio, **predicted -3.0 ms/tick (band -2.0 to -4.5)**, i.e. 24.72 -> ~21.7 |
| **HW-MMD-5** | clean main + 0297 -- built from the committed series only after 0297 passes its lab gates (a working-tree build would be `build_dirty=1`) | none | 0297 vs HW-MMD-4: **-0.50 ms/tick (band -0.30 to -0.65)** |
| HW-MMD-6 (only if HW-MMD-5 misses its band) | the 0296-style probe on main + 0297 | none | `FindGUIID` per call ~8-11 us |
| HW-SBP-0 / HW-SBP-1 (optional, if the batch has room) | `AGSAPI.EXE` sha256 `c7767d08684ee32b4eac73d94cdabaeb7b6ada6d4c41ac912dbfa2d7ce349418` (main + lab probe 0296, `build_dirty=1`) | HW-SBP-1: `DOSAGS_ABL_SBP=1` | the 486 cost of `SetButtonPic` after its argument checks for the 11 unchanged normal-slot calls/tick (fixed cycles: 0.064 ms/tick); decides whether an exact early-out is worth designing (section 12) |

`DOSAGS_ABL_SBP` is not in the RUNMANIFEST allowlist; the `apiprobe` line's counts are its witness only
indirectly (the ablation returns early, so `same=` still counts): score HW-SBP-1 by its script event
against HW-SBP-0, not by `env_block_sha`.

---

## 14. Lever G (operator: BUILD IT) -- PRE-REGISTRATION of the series, its gates and its predictions (before any G code)

Design as in section 11 (read there). Built on main after 0297 lands (or on cc5b66f5 + 0297 if it has
not yet). Three patches, each measured and gated separately, in this worker's ags range:

| patch | what | fixed-40000 estimate (MMD script event) |
|---|---|---|
| **0299** packed decode info | at instance creation, after `ResolveImportFixups`, write each instruction's argument count (bits 7-8) and argument-2 fixup type (bits 9-11) into the code word's free bits; validate every instruction once at load (opcode range, arguments inside the code) with today's error texts; mask the new bits in `DetermineScriptLine` and every other `_code` reader (a `grep` audit list goes in the commit) | -0.2 to -0.5 ms |
| **0300** threaded dispatch | the `switch` becomes computed goto (`goto *handler[op]`), each handler ending in "advance, test the abort flag, decode next, jump"; `CALL`/`RET`/`CALLAS` keep their `continue` semantics; `LINENUM` and the backward-`JMP` watchdog unchanged | -0.5 to -1.0 ms |
| **0301** import cache | per `FIXUP_IMPORT` site a cached `RuntimeScriptValue` + generation; `SystemImports` gets a generation counter bumped by every `Add`/`Remove`/`RemoveScriptExports`/`Clear`; a site whose generation differs re-reads `simp.GetByIndex()` exactly as today | -0.1 to -0.3 ms |
| **G total** | | **-1.3 ms (band -0.8 to -1.8): 9.474 -> ~8.2 ms/tick; cumulative from base ~1.34x** |

**486 prediction:** the measured VM ratio is ~2.0x (13), so **G: -2.6 ms/tick of the script event (band -1.5
to -3.5)** against HW-MMD-4 (main with 0293+0295) -- with 0297 in both arms if it has landed. Falsifying
cell: **HW-MMD-7** = clean main + G at the HW-MMD-0 cell, scored against HW-MMD-5 (or HW-MMD-4 if 0297 has
not landed). A result outside the band is reported as a finding about the model, not argued away.

**Gates (all must pass; any failure stops the series and is reported):**
1. **Instruction-for-instruction equivalence (new, lab-only probe 0302 "VM trace digest"):** a hook at
   the point every instruction is dispatched folds (code instance id, pc, opcode, and after the previous
   instruction the IValue and Type of AX, BX, CX, DX, MAR, OP and the stack pointer's offset) into an
   FNV-1a digest; the digest and the instruction count are printed at every 25-tick statewit line and at
   every script entry's return. Applied to BOTH the current VM and G (the hook sits in the switch's
   loop head today and in G's dispatch macro). Required: every digest line identical, base vs G, on:
   - MMD-CS (1000 ticks); AGS Quest AutoPilot (to its quit: 4 rooms, 7 room changes, save and restore
     phases in its own script); 5 Days `--startr 3` seeded;
   - **MMD-INTRO: `--startr 40`**, the intro's own room chain 40 -> 49 -> 46 -> 1 with no input (blocking
     cutscenes, nested ticks, CALLAS into room scripts, room exports swapped in `simp` at every load): the
     "room change that swaps imports" gate, deterministic (a diagnostic entry, identical in both arms);
   - **save/restore**: a lab-only switch in the witness build, `DOSAGS_WIT_SAVERESTORE_TICK=N`, saves to
     slot 997 and restores it at tick N (outside any script, as 0298 does) on each of the four fixtures.
2. The 9.2 determinism guard (statewit, `Game :` events, AutoPilot log, PH*.BMP) EQUAL on the four
   fixtures, with baseline-twice EQUAL and the perturbation control DIFFERENT.
3. Op counts: probe 0291 ported onto G prints every `opcount` line identical to base.
4. Load-time decode check (lab-only, in 0299's test build): for every instruction of every script loaded
   in every fixture, the packed argument count and fixup type equal `sccmd_info` / `code_fixups`;
   **stated: 0 mismatches**, reported per game.
5. **Import-cache control:** a lab switch that never bumps the generation (a stale cache) must make the
   trace digest of MMD-INTRO or AGS Quest DIFFER at or after the first room change -- the evidence the
   generation check has power. If it does not differ, the gate is void and so is 0301.
6. Screen gate (as 9.9) on the four fixtures, with controls.
7. `/sdldos:review`, and a clean build from the committed series.
8. Hardware: HW-MMD-7 before/after, as above.

Memory to report (not a gate): the import cache's bytes per loaded instance, from a count at load
(estimate 11.4: <= ~0.25 MB for MMD).

### 14.1 Read-first refinement before any G code (2026-09-24) -- the band stands, the expectation moves to its low end

- **0301 (import cache) is withdrawn before code.** `SystemImports::GetByIndex` is a bounds check and a
  vector index (`Engine/script/systemimports.cpp:179-185`), not a lookup by name; a cache would save ~5
  instructions per `FIXUP_IMPORT` fixup, ~1k instructions/tick on MMD (~-0.025 ms at fixed 40000). The
  import-cache gate (14, gate 5) and its control fall away with it; the room-change and save/restore
  equivalence gates stay (they test 0299/0300 across instance creation).
- **0300 (threaded dispatch):** after 0293/0295 the part only threading removes is the jump to the shared
  loop tail and the opcode range check (`cmpl $73; ja`): ~1.5 instructions/op, **~-0.2 ms**.
- **0299 carries G:** validate every instruction once at load and pack the argument count into the code
  word; pad the code array with 3 zero words so all three argument words are loaded unconditionally --
  which removes the argument-count compare chain (`cmpl $2; je; cmpl $3; je; decl; je`) and the
  `sccmd_info` load from every instruction: ~4-6 instructions/op, **~-0.6 to -0.85 ms**. Exactness
  details found in the read: packing happens at the end of `ResolveImportFixups` (the last step of every
  instance's creation: `script.cpp:277`, `room.cpp:1234`), after its `CALLEXT`->`CALLAS` rewrite, and is
  idempotent; if the load-time walk finds an opcode the VM would reject, that instance is NOT packed and
  runs the unchanged decode path -- a malformed script that never executes its bad instruction keeps
  loading and running exactly as today. Every reader of `_code` masks with `& 0x7F` where it wants the
  opcode (14 `_code[` sites in `cc_instance.cpp`, listed in the commit).
- **Revised expectation, inside the pre-registered band:** G ~-0.8 to -1.05 ms/tick at fixed 40000 (band
  -0.8 to -1.8 unchanged), ~-1.6 to -2.1 ms on the 486 (band -1.5 to -3.5 unchanged). If 0300 lands
  under -0.1 ms it is dropped as not worth its behaviour surface.

### 14.2 The operator's target (full speed at ~20 fps) with G's revised range -- arithmetic, one table

486, from HW-MMD-0: logic 31.28 ms/tick, render pass 13.4 ms. Full speed at 20 fps needs
**40 x logic + 20 x render <= 1000 ms/s**. Lever values are 486 estimates (13.1, G per 14.1); the API
rows rest on the probe-measured ~5x (an upper bound, 13.2).

| lever | central | top of range |
|---|---|---|
| A+B (0293, 0295) -- landed; HW-MMD-4 measures | -3.0 | -3.5 |
| G (0299, maybe 0300) -- 14.1 | -1.85 | -2.1 |
| C-F micro-levers | -2.25 | -3.0 |
| 0297 `FindGUIID` cache | -0.5 | -0.65 |
| API call path | -0.7 | -0.9 |
| other per-tick engine work | -1.0 | -1.5 |
| **logic per tick** | **22.0 ms** | **19.6 ms** |
| render side (per render) | -3.0 -> 10.4 ms | -4.0 -> 9.4 ms |
| **ms/s at 40 ticks + 20 renders** | **1,087 (over)** | **973 (fits, 2.7% margin)** |
| **displayed fps at full speed** | **~11.6** | **~23** |

**Plainly:** with every lever at the TOP of its range the target is reachable, by a 2.7% margin. At
central estimates it is not: full speed runs at ~12 fps, short by **~2.2 ms/tick of logic (or ~4.4 ms
per render)**. The levers that would have to overdeliver are the largest and least certain: **A+B** (HW-
MMD-4 measures it first) and **C-F** (not yet read in detail), then the render side; G's revision (top of
range -3.0 -> -2.1 ms/tick) cost 0.9 ms/tick x 40 = 36 ms/s: the top-of-range sum went from ~937 to ~973. The API-derived
rows may shrink once HW-MMD-5 removes the cache confound, which would widen the shortfall.

#### 12.1 AMENDMENT (2026-09-24): the 0298 self-test procedure changed after runs -- handled like a void

Kept runs and their cause (raw `tests/harness/results/FGST-{MMD,AQ,5D}-2026-09-23/`):
- **FGST-MMD: valid** -- latched at tick 300, 0 mismatches in all three phases (246 queries each, 19 GUIs),
  `restore=ok`.
- **FGST-AQ: harness error, void.** The forced `save_game(998)` at tick 500 collided with the AGS Quest
  AutoPilot's own save/restore state machine (it entered its restore phase at tick 500, its restore of
  `agssave.001` failed, and after our restore of 998 the script failed with `Null pointer referenced` in
  `on_event` and the game quit at 36 s). The two phases that ran printed 0 mismatches; they prove nothing
  about restore.
- **FGST-5D: harness error, void.** No self-test line: the hook fired only on exactly tick 300 outside a
  script, and 5 Days' room 3 was inside a blocking script then.
- FGST2-* (latch fix; AGS Quest without a forced save) are superseded before being scored: AGS Quest calls
  `FindGUIID` 0 times (APICAQ `calls=0`), so at its AutoPilot's restore the cache would be EMPTY and a
  post-restore pass would prove nothing (coordinator, 2026-09-24).

**Procedure, amended before the re-run (v3, `AGSFGST3.EXE`):**
- The hook latches on the first tick >= N outside any script and LOGS that tick.
- Every query gets its OWN buffer (one cache key each; v1/v2 used two buffers, so the cache held at most
  two entries); each phase logs `cache_entries=` (filled slots when it starts) and `hits=` (lookups
  answered from the cache in that phase), besides `queries=` and `mismatches=`.
- MMD and 5 Days: at N, a fill sweep, then `save_game(998)`, a sweep, `try_restore_save(998)`, a sweep --
  the post-restore sweep must show `hits > 0` and 0 mismatches.
- AGS Quest: a fill sweep at N1 = 1900 (before the AutoPilot's own save/restore phase at ~tick 2024; no
  forced save), then a post-restore sweep at N2 = 2100 with the cache still filled: `cache_entries > 0`
  at its start, `hits > 0`, 0 mismatches. If the AutoPilot's restore did not run between N1 and N2
  (checked from its `phase=restore status=ok` line), the AGS Quest cell is void.

### 14.3 G (0299) gates -- interim results (DOSBox-X, fixed 40000; raw `tests/harness/results/G*-2026-09-23/`)

Builds: base witness `AGSBW.EXE` `582dece2112e` (main + 0297 + 0292 + 0302), G witness `AGSGW.EXE`
`ab5e2a8caa7b` (+ 0299 + 0303); timing `AGSFG.EXE` `d1e43cfe54c4` (main + 0297) vs `AGSG1.EXE` `db939fdb9cf1`
(+ 0299). The statewit line now carries the VM trace digest (`vmtrace=`, `vmops=`), so `detdiff.py`'s
statewit comparison is the instruction-for-instruction comparison.

| gate | MMD-CS | AGS Quest AutoPilot | 5 Days (seeded) | MMD-INTRO (`--startr 40`) |
|---|---|---|---|---|
| 1. trace digest base == G | **EQUAL** (`vmops` 5,685,500 = probe 0291's `insns_total`) | **EQUAL** | **EQUAL** | **EQUAL** (29,520,906 ops; rooms 40 -> 49 -> 46 -> 1 in both) |
| 1. save/restore arms base == G | **EQUAL** (tick 400, `restore=ok`) | its own AutoPilot save/restore, in both arms | **EQUAL** (tick 800, `restore=ok`) | **EQUAL** (tick 7000, `restore=ok`) |
| 2. baseline twice | EQUAL | EQUAL | EQUAL | EQUAL |
| 2. state control (player x) | DIFFERENT | DIFFERENT | DIFFERENT | DIFFERENT |
| 4. load-time decode check (0303) | 0 mismatches, every instance | 0 | 0 | 0 (every room script in the chain) |

**Gate 1's power, a gap found and being closed:** the state control never moves `vmtrace` (those scripts
do not read the player's x in the window), so it shows the state digest's power, not the trace's. The
trace hook's coverage is shown by `vmops` equalling the independent opcode probe's count; its register
sensitivity gets a VM-level control -- `DOSAGS_VMTRACE_CONTROL=N` flips bit 0 of the first engine call's
return value in AX after tick N (`lab-mmd/probe-0302-vmtrace-control.diff`, `AGSBWV.EXE` `75ccab8a76f0`).
Inert when unset: GVC-MMD0 == GMMD-BW0a **EQUAL**. The four control cells (GVC-MMD/-AQ/-5D/-INT, each must
DIFFER in `vmtrace` from its baseline) were stopped before running (the round C lock), as were the G timing
cells GT-MMD-G / GT-AQ-B / GT-AQ-G (GT-MMD-B ran) and G's screen gate (not yet specified as cells); all
re-run after lab-metric's round C trigger. Gate 3 (op counts) is subsumed by gate 1: the digest folds every
executed opcode in order, and `vmops` matches.

### 14.4 HW-MMD-4 scored (A+B on the 486), and 14.2 redone with A+B measured

Raw `~/git/dosags/tests/harness/results/HW-MMD-4-2026-09-24/` (main worker's run): exit 0, pre = post
`9a17a60d3cc1`, `binary_sha12=4a5cca2fa1fd`, `build_dirty=0`, room 50, no recovery.

**Scored against 13.4 exactly as written** (script event per tick = `evtype script` us / n):

| | HW-MMD-0 (0209 head) | HW-MMD-4 (main: +0210-0213 +0293 +0295) | change | predicted |
|---|---|---|---|---|
| script event ms/tick | 24.74 | **20.57** | **-4.17** | -3.0 (band -2.0 to -4.5): **met**, upper part of the band |
| logic ms/tick (update_game_once minus render and scene) | 31.28 | 27.07 | -4.21 | |
| `tick_rate_steady` / whole-run / `fps_p50` | 29.09 / 26.75 / 7.79 | 33.22 / 30.41 / 8.82 | | |
| `render_to_screen` ms/call | 10.80 | 10.79 | none | |

Caveat on attribution: HW-MMD-4's binary also carries 0210-0213 (clip decode, legacy pathfinder, audio
status); this cell has sound off and no walking, so those are not exercised here, and the script event
does not include them -- the -4.17 is A+B's.

**What it says:** on the 486, A+B is **1.203x** on the script event against 1.159x at fixed cycles --
the removed stores pay **~2.8x** their fixed-cycles cost (13's working ratio for VM work was ~2.0x). The
2.2x CPI flag (5.1) is read as confirmed for store-heavy interpreter work. Levers of the same kind (G, C-F)
are rescaled with a 2.0-2.8x ratio below; the API rows keep the probe-measured (upper-bound) basis.

**14.2 redone** -- logic from HW-MMD-4 (27.07 ms/tick, A+B in), render 13.4 ms; full speed at 20 fps needs
40 x logic + 20 x render <= 1000 ms/s:

| lever (486, ms/tick of logic) | low | central | top |
|---|---|---|---|
| A+B -- **measured** | in the base | in the base | in the base |
| G (0299, maybe 0300): fixed -0.8 to -1.05 x 2.0-2.8 | -1.6 | -2.25 | -2.9 |
| C-F: fixed -1.0 to -1.5 x 2.0-2.8 | -2.0 | -3.0 | -4.1 |
| 0297 `FindGUIID` cache (API; upper-bound basis) | -0.3 | -0.5 | -0.65 |
| API call path (upper-bound basis) | -0.5 | -0.7 | -0.9 |
| other per-tick engine work | -0.5 | -1.0 | -1.5 |
| **logic per tick** | **22.2** | **19.6** | **17.0** |
| render side (per render) | -2 -> 11.4 | -3 -> 10.4 | -4 -> 9.4 |
| **ms/s at 40 ticks + 20 renders** | 1,115 (over) | **993 (fits, 0.7% margin)** | 869 |
| **fps at full speed** | ~10 | **~21** | ~34 |

**Plainly:** with A+B measured on the 486, the operator's target (full speed at ~20 fps) is now reachable
at the CENTRAL estimates -- by a 0.7% margin, i.e. only just -- and comfortably at the top of the ranges.
At the low end it is not (~10 fps). The swing is C-F and G (both still fixed-cycles estimates x a ratio
measured once), then the render side; the API rows may shrink when HW-MMD-5 removes the cache confound.

### 14.5 G (0299) timing -- SCORED: MISSED its band; and the VM trace control's power

**Timing (fixed 40000, clean builds; GT-MMD-B = main + 0297 `AGSFG.EXE`, GT-MMD-G = + 0299 `AGSG1.EXE`):**
MMD script event **9.377 -> 9.352 ms/tick = -0.025** against the pre-registered G band **-0.8 to -1.8** (14.1
expected 0299 alone at -0.6 to -0.85). **Missed.** AGS Quest: 37.444 / 37.446 dispatch (no change, as for
any interpreter lever there).

Mechanism (read in the final 0299's `-S` output, after the result): the packed loop head is shorter (17
x86 instructions vs B's ~21), but the two unconditional argument loads hold `%esi`/`%edi` at the head, and
GCC stops keeping `_pc` in `%ebx` and `this` in `%esi` across the loop as it did for B: `_pc` lives in a
stack slot (`-576(%ebp)`) and `this` is reloaded from `8(%ebp)`; the back-edge grows from 3 instructions
to 8, and every handler touching `_pc` or `this` pays extra loads. The head's saving is spent on register
pressure in the rest of the loop. **14.1's estimate counted the head, not the loop's register
allocation: the model was wrong.** Recommendation to the coordinator: do not land 0299; withdraw 0300
unbuilt (computed goto typically worsens GCC's allocation further, and its estimate was ~1.5 instr/op
before that); drop HW-MMD-7. With G at ~0, 14.4's central case becomes logic ~21.9 ms, ~1,082 ms/s, ~12
fps at full speed.

**Gate 1's power (VM-level control, `AGSBWV.EXE`):** one flipped bit in one engine call's AX changes
`vmtrace` on MMD 28/40 statewit lines (from tick 325), AGS Quest 122/142 (525), 5 Days 66/80 (375), MMD-
INTRO 318/360 (1075); inert when unset (GVC-MMD0 == baseline). G's correctness gates all pass -- it is
the value that fails.

#### 12.1 AMENDMENT 2 (2026-09-24, coordinator GO): self-test v4 -- v3 had no power over cache hits

Kept on record: **FGST3-MMD** (v3) -- latched at tick 300, 0 mismatches in every phase, but **`hits=0` in
every phase**: the 64 per-query buffers are 40 bytes apart, so the pointer hash `((uintptr)p >> 2) & 15`
puts them into only 8 of the 16 slots, and each entry is evicted before its re-lookup in the next pass --
the cached path was never exercised by the test. (The game itself does hit: 0297's -0.097 ms needs it,
and the APICF ablation, the same slot function on MMD's real script-literal pointers, answered 22,975 of
22,978 calls from the cache -- 3 warm-up misses: the in-game pointers do not collide this way, so 0297's
486 band is not made optimistic by collisions.) FGST3-AQ/-5D are superseded before scoring.

**v4 procedure, before its runs:** per query, a lookup immediately followed by a second lookup of the same
pointer (the second must be a cache hit), both against the uncached scan; before the save, the cache's
RESIDENT keys that point into the test's own buffers are snapshotted, and right after the restore exactly
those are looked up first -- each must hit and match the scan. Logged per phase: `hits=` (must be >= the
number of queries), `resident=` and `resident_hits=` (must be equal and > 0 after the restore),
`mismatches=` (must be 0). AGS Quest: fill at the first tick >= 1900 outside a script, snapshot, and the
post-restore check at the first tick >= 2100 (after its own AutoPilot restore, which must be seen in its
log between the two, else void). MMD and 5 Days: fill, snapshot, save, restore, check -- at one tick.

### 13.5 HW-SBP-0 / HW-SBP-1 scored (the 486 cost of `SetButtonPic` after its argument checks)

Raw `~/git/dosags/tests/harness/results/HW-SBP-{0,1}-2026-09-24/` (main worker's runs): both exit 0, no
recovery, `binary_sha12=f7b0d940965c` (`AGSAPI.EXE`, probe 0296), `build_dirty=1` as expected. Scored as
13.4 says -- by script event per tick, not `env_block_sha` (the `apiprobe` counts are identical in both:
`setbuttonpic calls=19980 normal=10989 over=8991 same=19980`; the ablation returns after `same` is counted).

| | HW-SBP-0 (no ablation) | HW-SBP-1 (`DOSAGS_ABL_SBP=1`) | change |
|---|---|---|---|
| script event ms/tick | 21.049 | 20.361 | **-0.687** |
| `tick_rate_steady` | 32.61 | 33.38 | |

**Read:** the part of `SetButtonPic` after its argument checks, for the 11 unchanged normal-slot calls per
tick, costs **~62 us per call on the 486** -- against 5.8 us at fixed cycles (APICS1, 12): **~10.7x**, the
largest 486/fixed ratio measured in this campaign. (The probe's own counters: HW-SBP-0 is +0.46 ms/tick
over the clean HW-MMD-4.) Section 12's "do not land" rested on the fixed-cycles size (<= 0.02 ms/tick
skippable); on the 486 the whole post-check body is 0.69 ms/tick, so **an exact early-out is worth
designing if its skippable part is where the 486 time goes**. What it must still run (12): the button
animation stop and the sprite-size read for `SetSize`; what it could skip: `SetNormalImage` ->
`UpdateCurrentImage`, `replace_sprite_changed_callback`'s `DoesSpriteExist`/`IsDynamicSprite` checks, the
`SpriteInfos` reads. Nothing there looks like 4,000 cycles from the source; the 486 split between those
parts is unknown (cache misses across scattered GUI and sprite tables are the likely cost), so the next
step would be a 486 sub-ablation cell, not a guess.

#### 12.2 ags 0297 lab gates -- RESULTS (every lab gate PASSES; screen gate scored 2026-09-24)

- **Timing (fixed 40000):** MMD-CS script event 9.474 -> 9.377 ms/tick, **-0.097** (pre-registered band -0.06
  to -0.143: **met**); AGS Quest 37.444 / 37.444 dispatch (no `FindGUIID` calls: no change, as predicted).
- **Determinism guard** (`AGSMW.EXE` vs `AGSFGW.EXE`): MMD, AGS Quest, 5 Days (seeded) -- baseline twice
  EQUAL, **0297 == baseline EQUAL**, control DIFFERENT, on all three.
- **Self-test v4** (`AGSFGST4.EXE` `9cee007a1dd1`, raw `FGST4-*-2026-09-23`): 0 mismatches in every phase;
  hits = one per query on the immediate re-lookup (MMD 64, AGS Quest 36, 5 Days 12+); **after the restore,
  every resident key answered from the cache: resident 8 / resident_hits 8 / 0 mismatches** on MMD
  (latched tick 300, `restore=ok`), 5 Days (latched 523, `restore=ok`) and AGS Quest (fill at 2015, the
  AutoPilot's own save and restore both `ok` at tick 2024, check at 2261). **PASS, with power.**
- **Screen gate** (`fgscreen.spec`: `tools/dosbox-x-fast.conf`, `--fixed-timestep`, exclusive lock, display
  261, freezes via ags 0195; raw `tests/harness/results/{MMD,AQ,5D}SG3{MW0,FGW,MWC}-2026-09-23/`). Every
  freeze landed on its requested tick (`FRZnn.TXT` `tick=` == `want=` in all 27 captures). `screen-equal.py`:

  | fixture | W0 vs 0297 (`AGSFGW`) | W0 vs WC (control) |
  |---|---|---|
  | MMD-CS | 3/3 equal | 3/3 equal (no power on this screen, as in 9.10: the perturbed player is not drawn) |
  | AGS Quest AutoPilot | 3/3 equal | **DIFFERS at tick 400** (124 px, bbox 676,541-685,565) |
  | 5 Days (seeded) | 3/3 equal | **DIFFERS at tick 200** (1,904 px, bbox 816,711-852,831) |

  **PASS, with power** (two of three controls differ, the same pixels as 9.10's). **0297 has cleared every
  pre-registered lab gate:** timing band, determinism guard, self-test v4, screen gate.

### 14.6 OPERATOR DECISIONS (2026-09-24 ~08:05Z, via the question tool, relayed by the coordinator) -- verbatim

> (1) Lever G: TRY THE REGISTER-FRIENDLY VARIANT, TIME-BOXED.
>   - ~1.5 h to code it and read the loop's -S.
>   - HARD STOP if _pc or `this` leave their registers. Stop and report; spend nothing on runs.
>   - If they stay in registers, pre-register the variant first (fixed band -0.1 to -0.5 ms, 486 -0.3 to -1.4), then run the full gates.
>   - 0299 as built is not landed either way.
> (2) MMD TARGET CHANGED: FULL GAME SPEED (40 logic ticks/s) is the firm goal. Frame rate is secondary: whatever results, probably ~12-15. Anything above that is a bonus. So what counts now is logic per tick: 27.07 measured, <= ~22 needed to leave render room, and < 25 is the hard line.

Work order (coordinator): the G variant's 1.5 h first; then the `SetButtonPic` exact early-out read-first;
then 0297's screen gate, v4 done, and landing; then C-F.

**Remaining levers ranked by 486 ms/tick of LOGIC** (logic 27.07 measured, HW-MMD-4; need -2.07 for the
< 25 hard line, -5.07 for <= 22):

| rank | lever | 486 estimate | basis | status |
|---|---|---|---|---|
| 1 | C-F interpreter micro-levers | -2.0 to -4.1 | fixed -1.0 to -1.5 x 2.0-2.8 (A+B's measured ratio) | not read in detail |
| 2 | other per-tick engine work (4.4 ms) | -0.5 to -1.5 | needs a probe | not started |
| 3 | G register-friendly variant | -0.3 to -1.4 | fixed -0.1 to -0.5 x 2.8 | time-boxed now |
| 4 | API call path (CALLEXT marshalling) | -0.5 to -0.9 | probe-measured, upper bound (13.2) | not designed |
| 5 | `SetButtonPic` exact early-out | 0 to -0.69 | HW-SBP: post-check body 0.687 ms/tick; skippable share unknown | read-first next |
| 6 | 0297 `FindGUIID` cache | -0.3 to -0.65 | HW-MMD-1 per-call cost (upper bound) | lab gates passed but screen; HW-MMD-5 |

Central sum ~-6.4 ms -> logic ~20.7 (<= 22 met); the < 25 hard line needs only 0297 plus the low end of C-F.

### 14.7 G register-friendly variant -- HARD STOP at the -S read (operator rule 14.6(1)); no runs

Time box started ~13:37Z; stopped ~13:50Z at the first decision point. The variant (`lab-mmd/lever-0299-
gvariant-on-0299.diff`, applied on 0299): packed argument count kept, the head's argument loads removed,
each packed-mode handler reads `code[_pc+1]`/`code[_pc+2]` where it uses them (compile-time `OPA1`/`OPA2`).
Compiled with the build's own flags (`-O3`, i586) and read in `RunT<true>`:
- head: 14 x86 instructions to the dispatch jump -- but it begins `movl -580(%ebp),%eax; movl 24(%eax),%edx;
  movl -572(%ebp),%eax`: **`_pc` lives in the stack slot `-572(%ebp)`**;
- back-edge: `movl -576(%ebp),%ebx; movl -572(%ebp),%esi; leal 1(%ebx,%esi),%edi; movl 8(%ebp),%ebx; movl
  %edi,-572(%ebp); movl %edi,1784(%ebx)` + the abort test: **`this` is reloaded from `8(%ebp)`** and `_pc`
  is loaded and stored through its slot every instruction (lever B: `_pc` in `%ebx`, `this` in `%esi`,
  back-edge 3 instructions).
**`_pc` and `this` have left their registers: the operator's hard-stop condition. Stopped; nothing run;
nothing pre-registered.** Reading: in `RunT<true>` GCC's allocation of this 3,000-instruction function
does not keep the loop state in registers once the head is restructured, whether the arguments are
loaded in the head (0299) or in the handlers (this variant); lever B's shape is the one it allocates
well. Neither 0299 nor the variant lands. The vendor tree is back to main + 0297 (the landing candidate).

The G screen gate (`gscreen.spec`, queued before the hard stop) ran anyway from the relaunch script. It
is recorded, not scored as a gate, because G is not landing. `AGSGW` vs `AGSBW` is equal in 12/12 captures
on MMD, AGS Quest, 5 Days and the interior; the control differs on AGS Quest t400 and 5 Days t200, as in
9.10. One procedural note for any future screen gate on the interior fixture: its first freeze asked for
tick 2000 and landed on 2824 in all three arms, identically (a stretch with no fixed-timestep ticks). The
pair still compares like with like, but a gate that needs t2000 exactly should pick a tick outside that
stretch.

## 15. `SetButtonPic` exact early-out -- READ-FIRST (2026-09-24; no code, no runs)

Source read in `vendor/ags` (main + 0297): `Engine/ac/global_button.cpp` `SetButtonPic`;
`Engine/ac/button.cpp` `Button_SetNormalGraphic`, `Button_SetMouseOverGraphic`,
`FindAndRemoveButtonAnimation`/`FindButtonAnimation`; `Engine/ac/draw.cpp`
`replace_sprite_changed_callback`, `add_`/`remove_sprite_changed_callback`, `notify_sprite_changed`;
`Common/gui/guibutton.cpp` `Set*Image`, `UpdateCurrentImage`, `SetCurrentImage`, `SetCurrentColors`,
`OnColorsChanged`, `OnTextColorChanged`, `SetButtonFlags`, `ReadFromFile`/`ReadFromSavegame`;
`Common/gui/guiobject.cpp` `SetSize`, `SetBackColor`, `SetBorderColor`; `Common/ac/spritecache.cpp`
`DoesSpriteExist`.

**What an unchanged-slot call runs today** (MMD: 11 normal + 9 mouse-over calls per tick, all unchanged:
HW-SBP `same=19980` of 19980). The debug log is already skipped (`!=` test). Then:

| part | normal (ptype 1) | mouse-over (ptype 2) | skip exactly? |
|---|---|---|---|
| a. `Set*Image(same)` -> `UpdateCurrentImage()` | yes | yes | **YES**, see the invariant below |
| b. `SpriteInfos[slot].Width/Height` + `SetSize(w,h)` | yes (slot != 0) | no | **NO**: script can resize the button (`Button.Width`), or a dynamic sprite of that number can change size; `SetSize` restores the sprite size. It already returns at once when the size is equal |
| c. `replace_sprite_changed_callback(n, n)` -> `DoesSpriteExist(n) && IsDynamicSprite()` | yes | yes | **NO**: if the slot was set while sprite n did not exist or was not dynamic, and a dynamic sprite n was created since, this same-slot call is the one that registers the callback (the engine keeps notify entries across delete and recreate, see `notify_sprite_changed`). `Add` is already idempotent |
| d. `FindAndRemoveButtonAnimation` (linear scan of `animbuts`) | yes | yes | **NO**: `SetButtonPic` stops an animation started since, whatever the slot |

**The invariant that makes (a) exact.** `UpdateCurrentImage` is a pure function of button members
(`_isMouseOver`, `_isPushed`, the three images, the normal/mouse-over/pushed colors, `_buttonFlags`'
dynamic-colors and flat-style bits). It only ever writes through `SetCurrentImage`/`SetCurrentColors`,
which return without a write when nothing changes. Every engine-reachable writer of those inputs calls
`UpdateCurrentImage` afterwards:
- the image setters and `SetImages`;
- mouse enter/leave and push/release;
- `SetDynamicColors` and `SetFlatStyle`;
- the mouse-over/pushed color setters;
- `OnColorsChanged` (behind `GUIObject::SetBackColor`/`SetBorderColor`) and `OnTextColorChanged` (behind
  `SetTextColor`);
- `ReadFromFile` and `ReadFromSavegame`, which end with it.

The only writer that does not is `GUIButton::SetButtonFlags`, and it has **no caller** in the engine or
common tree (`/usr/bin/grep -rn SetButtonFlags`: definition and declaration only). So on entry to an
unchanged-slot call, the current image and colors already equal what `UpdateCurrentImage` would compute.
Skipping `Set*Image` when the slot equals the stored one leaves every member byte-identical.
(Guard for the patch: a comment at `SetButtonFlags` naming the dependency, so that a future caller adds
the update call.)

**So the exact early-out removes only (a):** a store of the same value, plus `UpdateCurrentImage`'s
branches and two compare-and-return calls. Per call that is about 60-100 instructions, times 20 calls per
tick. Everything the source suggests could be expensive on the 486 stays: the scattered table reads in
b-d (the `SpriteInfos` entry, `_spriteData[n]`, `animbuts`, and the GUI/control objects). That fits the
10.7x 486/fixed ratio of 13.5 being memory-bound rather than instruction-bound.

**Where the 0.687 ms/tick may actually go (unknown; not guessed).** The ablation removed a-d together for
the 11 normal calls, so it cannot separate:
- the parts from one another;
- the body's own time from the L1 relief it gives the code around it (the confound of 13.2): the 0.687
  ms/tick is an upper bound for a-d;
- the 9 mouse-over calls, which were not ablated at all. Their cost is not in the 0.687.

**Proposed design (for GO; one concern, ags slot 0305 in my range):** in `Button_SetNormalGraphic`,
`Button_SetMouseOverGraphic` and `Button_SetPushedGraphic`, call `Set*Image(slotn)` only when `slotn`
differs from the stored slot. Everything else stays in place and in order: the size read and `SetSize`,
`replace_sprite_changed_callback`, `FindAndRemoveButtonAnimation`. Add the `SetButtonFlags` comment. Not
`__DJGPP__`-gated: it is exact on every platform, so no DOS assumption hides in it. Name it
`DOS-PORT patch 0305` as the series convention requires.

**Predictions, to be fixed at GO (numbers set now, before any code):**
- fixed 40000, MMD-CS script event: **-0.01 to -0.06 ms/tick**. That is 20 calls x 60-100 instructions,
  plus a margin for call overhead, at 40 instructions/us.
- 486 (logic ms/tick): **0 to -0.30**. The low end is the ratio of 2.0 measured for A+B; the high end is
  the 10.7x of the whole post-check body, applied to this part's fixed-cycles cost. That high end is
  unlikely, because the expensive-looking memory touches all remain.
- **Falsifier:** a fixed-cycles change outside the band in either direction, or any
  determinism/screen/state-witness difference, means stop.

**Gates (the 0297 set):**
- determinism guard on MMD, AGS Quest and 5 Days (seeded), with the control;
- screen gate, fast conf, exclusive;
- fixed-cycles timing on MMD-CS;
- VM op counts unchanged, by construction;
- a 486 cell pair: clean main vs main+0305, both on the 0230 tree. This can ride as a third arm in the
  HW-MMD-5 session to save a separate power-on.

**Optional, only if the operator wants the 0.687 ms/tick explained:** a lab-only sub-ablation probe
(0304, extending 0296's `DOSAGS_ABL_SBP`), cost-only and not semantic. Modes skip b, c, d separately for
the unchanged normal calls, and a-d for the mouse-over calls. Counters: dynamic-sprite hits, ticks with
`animbuts` non-empty, and `SetSize` calls that actually resize. That is up to 5 486 cells plus a repeat
HW-SBP-0 for drift, and it would only matter if the answer justified a non-trivial design for b-d (per-button
"size synced" tracking with invalidation hooks), which is itself not obviously exact. **Recommendation:
land 0305 on the lab gates plus its HW arm; skip the sub-ablation.** Rank in 14.6 revised: 0 to -0.30,
below 0297.

#### 12.3 0297 on the 0230 tree -- re-guard PRE-REGISTRATION (2026-09-24, before the runs)

main moved to 8ac262e1 (ags 0214, 0230, 0231; SDL 0210). Merged into lab/mmd. The vendor trees were
re-applied clean from the series (`verify-patches-applied` 0), and 0297 was applied on top (`apply
--check` clean, same 4 files and 44 insertions).

Binaries, full sha256:

| binary | contents | sha256 |
|---|---|---|
| `AGSM2` | clean main, `build_dirty=0` | `6d886a4ccf2032248206307e3a31f445e23806bd53032d68c14e4144ab333798` |
| `AGSFG2` | main + 0297 | `e5e0ebda5fae61b8ef59830d6a4e7edb25827867a2537fb88d860d8c9b0dbf76` |
| `AGSMW2` | main + 0292 witness | `7ffec691103f77315ac5217ed409dad7a5f9b9d36dea0fcb4e71cbb3ee4b2121` |
| `AGSFGW2` | main + 0297 + 0292 | `9d49ef32c910ea6bb3e25c91fb1ef2364ce128e700fb568e113e0d80af3ed229` |

`AGSM2` is not byte-identical to the main worker's own build of 8ac262e1 (`build/ws/main-0214/ags.exe`,
`e2195303...`). Only same-worktree binaries are compared here.

Spec `lab-mmd/fg2.spec`, fixed 40000, shared lock per cell. Predictions (unchanged from 12.1, since 0230's
counters sit on the CALLEXT path and 0297 sits inside `FindGUIID`, so the two do not interact):
- **Determinism:** baseline twice EQUAL, 0297 == baseline EQUAL, control DIFFERENT, on each of MMD, AGS
  Quest and 5 Days (seeded).
- **Timing:** MMD-CS script event, 0297 - clean, **-0.06 to -0.143 ms/tick**.
- **Falsifier / stop:** any guard difference, or timing outside the band.
- The screen gate is not re-run: pixels were equal on the old tree, and 0230 and 0231 carry their own
  gates. That is a choice, stated here.

**12.3 RESULTS (fg2, raw `tests/harness/results/{FG2TB,FG2T}-MMD-2026-09-24/`, `{MMD2,AQ2,5D2}{MW0a,MW0b,FGW,MWC}-2026-09-24/`;
all 14 cells rc=0; long `wall_s` values are lock waits):**

| check | MMD | AGS Quest | 5 Days (seeded) |
|---|---|---|---|
| baseline twice | EQUAL | EQUAL | EQUAL |
| 0297 == baseline | **EQUAL** | **EQUAL** | **EQUAL** |
| control (perturbed) | DIFFERENT | DIFFERENT | DIFFERENT |

Timing, MMD-CS script event (`evtype script`): clean `AGSM2` **9.484** vs `AGSFG2` **9.386 ms/tick,
-0.098**. The band was -0.06 to -0.143: **met**. It is the same delta as on the old tree (-0.097). Steady
40.04 in both.

**0297 passes on the 0230 tree. Landing next.**

## 16. Levers C-F -- READ-FIRST on the current VM (2026-09-24; no code, no runs): the 9.3 estimates are stale

Read in `vendor/ags` at main 8ac262e1 (A+B landed; 0230's per-instruction counter is compiled only when
`AGS_WORK_SCRIPT_INS=1`, so it is absent from timed builds). The clean build's `-S` output for
`cc_instance.cpp` (the build's own flags, `-O3`, i586) is kept in the session scratchpad. The handler
paths were read with a small walker over `ccInstance::Run`'s dispatch table (`L514`, 74 entries). It
follows unconditional jumps and fall-through branches to the loop back-edge, so it is a rough static
count, not a profile.
MMD-CS per-tick opcode counts are 9.3's (probe 0291); they are properties of the bytecode, which A and B
did not change.

**Why the 9.3 figures no longer hold.** 9.3 ranked C-F when every argument cost five stores and the
head stored the instance id and the argument count twice. A and B removed exactly that. The head is now:
- 12 instructions to the dispatch jump;
- 2-3 per argument;
- the argument-count branch chain (up to 6);
- a 3-instruction back-edge, plus a 2-instruction abort test.

That is ~20 per VM op, ~113k instructions/tick at 5,642 ops (**~2.8 ms/tick at fixed cycles, the largest
single block**). Each C-F lever saves work inside a handler, and those handlers are now small:

| lever | per-tick count (MMD) | what it would save now | fixed-cycles estimate | exact? / risk |
|---|---|---|---|---|
| C. `sourceline` fast path ahead of decode | 550 | a pre-dispatch `op == LINENUM` test costs 2 instructions on every other op (5,092/tick, ~10k) and saves ~18 on each `sourceline` (~9.9k) | **~0 or negative: DROP** | -- |
| D. O(1) `LOADSPOFFS`/`subi`-on-MAR stack walk | 430 calls, 1,144 steps | the walk is 6 instructions per step (~6.9k/tick). An O(1) lookup needs a per-entry byte-offset array kept on every push/pop (~680/tick) | **~0.05-0.12 ms** | exact in principle; medium risk (every stack push/pop path) |
| E. load-time `FIXUP_IMPORT` resolution | 204 | the `GetByIndex` bounds check and one 20-byte copy, ~15 instructions (~3k) | **~0.08 ms** | needs proof that no import value changes after load (room change, plugin export). That is G's territory, and G does not land |
| F. `memread4`/`memwrite4` type switch | 454 + 87 | the switch is the semantics (stack, global, data, dynamic object): ~3-4 instructions of dispatch | **~0.05 ms** | little to gain: DROP |
| **H (new).** `movl` (`LITTOREG`) with `FIXUP_NOFIXUP`: `reg.SetInt32(arg2)` directly | up to 417 | today it runs `SetInt32` into the address-taken `codeOp.Args[1]` (5 stores), then the fixup switch, then a 20-byte copy into the register (5 loads + 5 stores) | **~0.1-0.16 ms** | exact: `SetInt32` writes all five fields. One point to settle: `ASSERT_CC_ERROR` after the fixup returns if a VM error is already pending. Either show that none can be pending at an instruction's start, or keep that call |
| **I (new).** argument decode without the count branch chain | 5,642 | load `arg1`/`arg2` unconditionally (code array padded by 2 words at load, keeping the end-of-code check), `arg3` behind one test: ~3 instructions saved on 1-argument ops, ~1 on 2-argument ops | **~0.2-0.25 ms** | exact if the padding and the end-of-code check are right. Low-medium risk: it touches every op, but only the reads. It also changes the register picture that G failed on, so it needs a `-S` read first, as G's variant did |

**Re-estimate:** C-F plus H and I together come to **~0.4-0.6 ms/tick at fixed cycles**, not 9.3's
1.0-1.5. With A+B's measured 486/fixed ratio (2.0-2.8) that is **-0.8 to -1.7 ms/tick on the 486**, not
14.6's -2.0 to -4.1.

**Consequence for the operator's target (logic < 25, need -2.07 ms/tick from 27.07):**
- The designed levers now sum to **-0.9 to -2.65**:
  - 0297: -0.30 to -0.65;
  - 0305 (`SetButtonPic`): 0 to -0.30;
  - C-F/H/I: -0.8 to -1.7.
- **The hard line is reached only in the upper half of that range.**
- The rest has to come from the two rows of 14.6 that are not designed yet:
  - the API call path (-0.5 to -0.9, an upper bound);
  - the other per-tick engine work (4.4 ms, -0.5 to -1.5).
- There is also a gap in this static account. VM head plus handler paths is ~250k instructions/tick, and
  the API bodies are ~42k (1.04 ms corrected, fixed cycles). The script event is ~375k, so ~80k/tick
  (~2 ms at fixed cycles) is not located.

**Recommendation (for the coordinator, before any C-F code):**
1. The next measurement is a fixed-cycles probe that splits the script event into three parts: VM loop,
   CALLEXT marshalling, and the API bodies plus everything outside `Run`. It needs no 486 cell, since
   fixed cycles counts instructions deterministically. It would locate the ~80k, which is the largest
   unexplained block that remains.
2. Of the micro-levers, H (exact, small surface) goes first. I goes only after a `-S` read shows the loop
   state stays in registers.
3. D and E wait for the split. C and F are dropped.

Each lever keeps the usual discipline: pre-registered fixed-cycles band, determinism guard, screen gate.

### 16.1 Coordinator decisions (2026-09-24, relayed; this message was sent before 16 reached them)

- **G is CLOSED.** 14.7 is the operator's hard-stop rule (14.6(1)) firing about 15 minutes into the time
  box. Nothing of G lands.
- 0297's screen gate is accepted, and so is the landing plan (merge main, clean re-apply, re-guard on
  the 0230 tree, format-patch plus review, land, build the HW-MMD-5 arms).
- **0305 (`SetButtonPic` exact early-out): GO, in this order: 0297 landing, then the C-F read-first
  (done as 16), then 0305.** Pre-register it as 15 proposes. Its 486 arm rides in the HW-MMD-5 session
  only if its lab gates have passed by the time round D is staged; otherwise it waits. No sub-ablation
  cells.
- **Gate note (interior fixture):** the first freeze asked for t2000 and landed at t2824 in every arm
  (14.7). So that fixture's early ticks are one long blocking script with no fixed-timestep ticks.
  Future gates on it pick freeze ticks past ~t2824.

### 16.2 Split probe 0304 -- PRE-REGISTRATION (coordinator GO 2026-09-24; before any probe code)

The coordinator accepted 16. Order: fg2, then the 0297 landing, then this probe, then 0305, then H.
Before H, its pending cc-error point is settled by reading the code. D, E and I wait for this probe's
result; I also needs a `-S` read.

**What it measures.** MMD-CS script event per tick, at fixed 40000 cycles, split four ways:
- **R_out**: the event minus time inside the outermost `ccInstance::Run` (dispatch, function lookup,
  instance setup and everything else outside the VM);
- **R_vm**: `Run` minus the time inside `SCMD_CALLEXT` handlers;
- **R_marsh**: the `CALLEXT` handler minus the API body (argument marshalling, checks, result
  conversion);
- **R_api**: the API function bodies.

**Design constraints:**
- The build is lab-only ags probe 0304 on main + 0297 (after the landing), `__DJGPP__`-gated, and never
  in `patches/`.
- No per-instruction counter.
- Only the outermost level is timed; anything nested inside an API body counts as API.
- Clock reads are raw `uclock_t` differences, converted once at dump (13.2's lesson).
- Each region is corrected by (its read count) x (the calibrated cost of one read), measured in the same
  run.
- Counters: `Run` entries, `CALLEXT` calls and reads per tick.

**Probe checks (void if either fails):**
- (a) The probe build with its reads switched off must give the clean build's script event within 1%.
- (b) The reads-on minus reads-off difference must equal reads x the calibrated read cost within +-10%.

`CALLEXT` calls per tick must be 174-175, as in 9.1.

**Expected shares, from 16's static count** (fixed cycles, ~9.3 ms event on main + 0297; ~40
instructions/us):

| region | expected | basis |
|---|---|---|
| R_vm | 5.0 - 7.5 ms | head ~113k + handler paths and inner switches ~120k instructions/tick |
| R_marsh | 0.3 - 0.8 ms | `farcall` path ~74 instructions x 175, plus the per-argument conversion loop |
| R_api | 0.8 - 1.2 ms | 1.04 ms corrected (P1, before 0297), less 0297's -0.1 |
| R_out | 0.5 - 2.5 ms | the ~80k instructions/tick that 16 could not locate (~2 ms) |

**Reading, fixed now:**
- R_out >= 1.5 ms: the unlocated block is outside the VM, and the next read-first is the event/dispatch
  path (`RunScriptFunction`, function-name lookup, instance setup).
- R_out < 0.5 ms: 16's static model undercounts the VM, and loop-level work (I) moves up.
- In between: both.

R_marsh and R_api re-price the API call-path row of 14.6 (a probe-measured upper bound until now) with a
fixed-cycles figure. A 486 cell for the split is proposed only if the fixed-cycles result leaves a
decision open.

**16.2 build record (before any run).** Probe 0304 is `lab-mmd/probe-0304-split.diff` (the probe alone on
main + 0297), plus `probe-0304-split-with-0297.diff` (the vendor working tree it was built from).

`AGSSPL.EXE` sha256 `d99b0cbfd8e78bf1598a429fae9d44586a3dfb6fdad10b6b3c5beae8615f3d59`, `build_dirty=1`.

Clock reads per `CALLEXT`, when timed:
- one at the handler start;
- one before the API dispatch;
- one after the API returns.

The few instructions after the API returns (error test, AX store) fall in R_vm.

Calibration: 1000 back-to-back read pairs, measured at the first `Run`.

Spec `lab-mmd/split.spec` has three cells:
- reads off;
- reads on;
- reads on again.

Check (a)'s reference is `FG2T-MMD` (`AGSFG2`, main + 0297, same conf), from the fg2 series. It is not
re-run: fixed cycles is deterministic for the same binary and env.

While building: the vendor tree's 0297 commit was soft-reset back into the working tree, because
`verify-patches-applied` refuses a commit that `patches/ags/` does not have yet. The format-patch was
already saved.

**16.3 H's pending cc-error point -- settled by reading (2026-09-24).** Every `cc_error` site inside `Run`
was listed (`awk` over `cc_instance.cpp` lines 600-1720) with the code that follows it. All of them
`return kInstErr_Generic` at once, except one: **`WRITELIT` with an unexpected data size (line 861) calls
`cc_error` and then `break`s.** That leaves an error pending at the next instruction's start, where the
next `ASSERT_CC_ERROR` returns. The compiler never emits such a `WRITELIT`, but nothing stops a data
file from doing so. The helpers' own error paths (`CC_ERROR_IF_RETVAL` in the stack walks, the
`RuntimeScriptValue` read and write paths) have not been audited one by one either.

**So H keeps the check:**

    if (fixup == FIXUP_NOFIXUP) { reg1.SetInt32(op_arg2); ASSERT_CC_ERROR(); }

That is exact in every state, error states included. The check is a real call here: the `-S` output shows
`cc_has_error()` called, not inlined. So H saves ~10 instructions per no-fixup `movl` instead of ~15, and
its estimate becomes **~0.08-0.12 ms/tick at fixed cycles** (16's row said 0.1-0.16). H stays queued after
the split probe and 0305, as ordered.

### 16.4 0297 LANDED on main (80a6d6f5, 2026-09-24); HW-MMD-5 arms built

Main moved twice while 0297 waited: first 0214/0230/0231/SDL 0210, then lab/journeys (ags 0250-0253, SDL
0220-0222). Each time: merged, re-applied clean (`verify-patches-applied` 0), 0297 applied cleanly at the
end of the series. 0250-0253 do not touch the files 0297 touches: 0250 only adds journey instrumentation
around `save_game` in `game.cpp`. The fg2 guard (12.3) ran on the first tree; the journeys tree got
apply, verify and a clean build, as the landing rule asks. The landing commit carries
`patches/ags/0297`, `LAB-MMD.md` and `lab-mmd/`; raw results stay on lab/mmd.

**HW-MMD-5 arms**, same session, same cell as HW-MMD-0/4 (13.4: mmd, `ACSETUP-OFF-512X384-ROUND.CFG`, fixed
timestep, sound off, no input, `SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1`, `DOSAGS_TAS_AUTO_EXIT_TICK=1000`).
Main has moved since HW-MMD-4 (0214, 0230's always-on `CALLEXT` counter, 0231, journeys), so HW-MMD-4 is
not the comparison: arm A is main just before 0297. Both binaries are chmod read-only.

| cell | binary (`~/git/dosags-lab-mmd/build/lab/`) | tree | stamp |
|---|---|---|---|
| **HW-MMD-5A** | `AGSM3.EXE` sha256 `dfb2aea83e04a13dd2319e63299f6c1d0d20433def22ad76a6d3cdd33e570c25` | main 939d957b (series without 0297; ags fingerprint 76385ae4d42e) | `build_dirty=0 sha12=0aa50f02be56` |
| **HW-MMD-5B** | `AGSL297.EXE` sha256 `6bd425537035b9960ce8d509588e68c649faf31dd0b72cb8f24009beb46ac90d` | main 80a6d6f5 (with 0297; ags 8c9f6f7ee2d2) | `build_dirty=0 sha12=9a3b05ce7e20` |

**Prediction (unchanged from 12.1):** B - A script event **-0.50 ms/tick, band -0.30 to -0.65**. Order
A B, or ABBA if the batch has room (drift control). If B - A comes in under -0.30 in magnitude, the 13.2
L1-cache confound is the first explanation to check, before the call-path model. 0305's arm joins only if
its lab gates have passed by the time round D is staged (16.1).

### 16.5 AMENDMENT to 16.2 (2026-09-24, before any split run): the probe is rebuilt on landed main

0297 has landed and main now includes journeys (16.4), so the probe is rebuilt on main 80a6d6f5
(`lab-mmd/probe-0304-split-on-80a6d6f5.diff`; the probe hunks are unchanged). `AGSSPL2.EXE` sha256
`a551a11e4949ef8efc336c66d133bc644d51a60c3d29000b58aadf810097d51b`, `build_dirty=1`.

Check (a)'s reference is now `SPLREF-MMD`: a fixed-cycles run of the clean `AGSL297.EXE` (HW-MMD-5B's
binary), in the same spec. `AGSSPL.EXE` (16.2) is superseded and not run. Predictions, reading and void
checks are unchanged. Journeys' instrumentation is outside the VM and API paths, so if it adds to the
event time at all, the addition lands in R_out.

### 16.6 Split probe 0304 -- VOID by check (a); cause found; v2 proposed (2026-09-24)

Raw `tests/harness/results/{SPLREF,SPLOFF,SPLON,SPLON2}-MMD-2026-09-24/`, all rc=0. Fixed 40000, MMD-CS 1000
ticks. Counts: `runs=999`, `callext=173826` (174/tick, as pre-registered), `reads=523476` (= 2 x 999 + 3 x
173,826). The two reads-on runs are byte-identical.

- **Check (a) FAILS, so the run is VOID.** With reads off, the probe's script event is **10.188 ms/tick**,
  against the clean `AGSL297`'s **9.387**: +0.80 ms (+8.5%; the limit was 1%).
- Check (b) passes: reads-on minus reads-off is 2.245 ms/tick, against 524 reads x 4.23 us (calibrated
  `pair1000_t=5044` raw ticks) = 2.215 predicted (+1.3%).

**Cause (from `-S`, same flags, same tree with and without the probe):**
- In `ccInstance::Run` the probe build reloads **`this` from `8(%ebp)` at 292 sites against 70**, and the
  function grows from **3,365 to 3,862 instructions**.
- The loop head itself is almost the same, but `%esi` now holds the op word instead of `this`.
- The RAII scope object and the `CALLEXT` hunks changed GCC's register allocation for the whole
  interpreter: the same sensitivity that sank G (14.5, 14.7).

**Any instrumentation inside `Run` perturbs what it measures.**

**Indicative only (void run, not a result):** corrected for read cost, R_out ~0.2, R_marsh ~0.34, R_api
~1.12 ms/tick. The +0.80 ms of perturbation presumably sits in R_vm. The API bodies are separate
functions that `Run`'s allocation does not touch, so R_api is the least disturbed of the three. It
agrees with P1's corrected 1.04.

**Proposed v2 (needs GO; not run):**
- Time `Run` from its only outside caller, `CallScriptFunction` (`cc_instance.cpp:451`; the other caller
  is `SCMD_CALL`'s recursion inside `Run`). Time only the outermost call inside a `kAGSEvent_Script`
  dispatch, plus the event scope. That gives **R_out = event - Run exactly**, which is the variable the
  16.2 reading keys on.
- **Pre-check before any run:** the `-S` of `Run` must be identical to the clean build's apart from label
  numbers. Same instruction count; same `8(%ebp)` reload count, 70. If it is not identical, no run.
- Checks (a) and (b) as in 16.2.
- R_marsh and R_api cannot be timed without code inside `Run`. They are taken from 13 and 16.6's
  indicative figures, and the v2 result is stated with that caveat.
- Cost: one build, 3 cells (reference, reads off, reads on).

### 16.7 ags 0305 (`SetButtonPic` exact early-out) -- PRE-REGISTRATION (2026-09-24; no code yet)

GO (16.1). Nothing of 0305 runs before the split question (16.6) is settled.

**Change (one concern).** In `Button_SetNormalGraphic`, `Button_SetMouseOverGraphic` and
`Button_SetPushedGraphic` (`Engine/ac/button.cpp`), call `Set*Image(slotn)` only when `slotn` differs from
the stored slot. Everything else stays, in the same order:
- the debug log (its existing `!=` test);
- `old_slotn`;
- the `SpriteInfos` size read and `SetSize`;
- `replace_sprite_changed_callback`;
- `FindAndRemoveButtonAnimation`.

Also a comment at `GUIButton::SetButtonFlags` (`Common/gui/guibutton.cpp`) saying that it does not call
`UpdateCurrentImage` and that 0305 relies on nothing calling it. The whole change is exact on every
platform (15's invariant). **Change from 15:** 15 proposed no gate; 0305 is `__DJGPP__`-gated like 0297,
so host builds keep upstream behaviour and every host-side comparison stays against upstream. Slot: ags 0305, this worker's range.

**Baseline:** main 80a6d6f5 (`AGSL297.EXE`, clean). Builds:
- main + 0305;
- main + 0292 witness;
- main + 0305 + 0292 witness.

**Predictions:**
- fixed 40000, MMD-CS script event: **-0.01 to -0.06 ms/tick**;
- AGS Quest and 5 Days: 0 within noise (few or no calls);
- VM op counts: unchanged, by construction;
- 486, on a later cell only if the lab gates pass before round D is staged: **0 to -0.30 ms/tick**.

**Falsifier / stop:** a fixed-cycles change outside the band in either direction; any determinism,
state-witness or screen difference.

**Gates (the 0297 set):**
- determinism guard (baseline twice, 0305 == baseline, perturbed control) on MMD, AGS Quest and 5 Days
  (seeded);
- screen gate: fast conf, `--fixed-timestep`, exclusive, display 261; freezes at 200/500/900 on MMD and
  5 Days and at 400/1500/3000 on AGS Quest; pixel-equal pairs, and at least one control must differ;
- fixed-cycles timing on MMD-CS;
- `/sdldos:review` before landing.

### 16.8 Split probe v2 -- GO (coordinator); pre-check PASSED; build (2026-09-24, before any v2 run)

**Gate note for any future VM probe (coordinator):** instrumentation inside `ccInstance::Run` perturbs
`Run`. GCC's register allocation for the interpreter is sensitive to any added code: 16.6's probe
reloaded `this` at 292 sites against 70, which is the G mechanism. A VM probe either stays outside
`Run`, or proves by `-S` that `Run` is unchanged, or states its perturbation as measured by a reads-off
arm against the clean build.

**v2 (`lab-mmd/probe-0304v2-split.diff`, on main 80a6d6f5):** the outermost `Run` inside a script
event is timed from `CallScriptFunction`, around the `Run(start_at)` call. That is `Run`'s only outside
caller. Also the event-scope flag in `event.cpp` and the dump in `quit.cpp`. Nothing inside `Run`.

**Hard pre-check -- PASSED:** `-S` of `cc_instance.cpp` (build flags) with and without v2. `Run` is
**identical** after label renumbering: 3,365 instructions and 70 `this` reloads from `8(%ebp)` in both,
4,124 lines, 0 differing.

Build: `AGSSPL3.EXE` sha256 `86481e0b50538c777678860980c6e9dd2fdd702dcc881b2fdd47e1ac4e0efc39`,
`build_dirty=1`.

Spec `lab-mmd/split2.spec`: reads off, reads on. Check (a)'s reference is 16.6's `SPLREF-MMD`
(`AGSL297`, same conf; fixed cycles is deterministic for the same binary and env), so 2 new cells
instead of 3. Checks (a) and (b) and the reading are as in 16.2. R_marsh and R_api stay at 16.6's
indicative values, labelled as such.

### 16.9 Split probe v2 -- RESULT (raw `tests/harness/results/SPL2{OFF,ON}-MMD-2026-09-24/`, reference `SPLREF-MMD`)

Counts: `runs=999` (one outermost `Run` per script event), `reads=1998` with reads on. Calibration:
`pair1000_t=5039`, so one read costs 4.22 us.

| check | value | limit | |
|---|---|---|---|
| (a) reads off vs clean `AGSL297` | 9.389 vs 9.387 ms/tick, **+0.02%** | 1% | **PASS** |
| (b) reads on - reads off | 8.17 us/tick vs 2 reads x 4.22 = 8.45 predicted, -3.4% | +-10% | **PASS** |

**Split (fixed 40000, MMD-CS, main 80a6d6f5, corrected for read cost):**

| region | ms/tick | share | status |
|---|---|---|---|
| script event | 9.389 | 100% | measured |
| outermost `Run` | 9.187 | 97.8% | measured |
| **R_out** (event - `Run`) | **0.202** | **2.2%** | measured |
| R_api | ~1.12 | ~12% | indicative (16.6, void run; P1 gave 1.04) |
| R_marsh | ~0.34 | ~4% | indicative (16.6) |
| R_vm (`Run` - API - marsh) | ~7.7 | ~82% | derived from the indicative pair |

**Reading, as fixed in 16.2: R_out < 0.5 ms, so the ~80k instructions/tick that 16 could not locate are
inside the VM. 16's static walker undercounts the interpreter, and loop-level work (I) moves up.**

R_vm ~7.7 ms is ~310k instructions/tick, ~55 per VM op, against the walker's ~40. The walker follows
fall-through paths and does not count called helpers:
- `PushValueToStack`/`PopValueFromStack`;
- `RuntimeScriptValue::ReadValue`/`WriteValue` by type;
- the inner type and fixup switches that ended in `indirect` in its output.

The predicted R_vm band (5.0-7.5) is exceeded at its top; R_marsh and R_api fall inside theirs.

**What this means for the lever list:**
1. R_out (0.2 ms) is too small to be a lever: dispatch, lookup and setup outside the VM are cheap.
2. The API rows are ~1.5 ms together (bodies 1.12 + marshalling 0.34, indicative). 0297 already took
   its share, and 0305 is small.
3. **The VM itself is ~7.7 ms of the 9.4.** Beyond A+B it is the only large block, and G has shown that
   restructuring it hits GCC's register allocation.

A per-handler cost account that counts helpers is needed before I, D or E is sized. It has to be
static (`-S` plus call graph), because in-`Run` instrumentation perturbs `Run` (16.8 gate note).

**16.7 build record (2026-09-24, before any 0305 run).** `lab-mmd/lever-0305-setbuttonpic-earlyout.diff`,
on main 80a6d6f5. The guarded `Set*Image` calls are braced, so no misleading-indentation warning (none
in the build log). Binaries, all `build_dirty=1`:

| binary | contents | sha256 |
|---|---|---|
| `AGS305` | main + 0305 | `206b393cd48ab03c69cbd97656f4fd6de2696e3deaa97650508a896537dccbd5` |
| `AGSMW3` | main + 0292 witness | `cf203b2b51a22e958d46596d3a2b03ac8f5143a2b1e323b25b69ac388acef624` |
| `AGS305W` | main + 0305 + 0292 | `fbee9ab16c7c67516af07c6137900b9f2c505c623d27764ae12f9bb46dc6c36e` |

The timing baseline is `SPLREF-MMD` (clean `AGSL297`, same conf; fixed cycles is deterministic).

Specs:
- `lab-mmd/g305.spec`: timing plus the determinism guard, fixed 40000, shared per cell.
- `lab-mmd/g305screen.spec`: the screen gate. Fast conf, exclusive, display 261. It runs after g305 and
  never beside a freeze-capture gate.

### 16.3 CORRECTION (2026-09-24, found during 17): `ASSERT_CC_ERROR` is empty in release builds

`cc_instance.cpp` defines `ASSERT_CC_ERROR`, `CC_ERROR_IF_RETCODE` and `CC_ERROR_IF_RETVAL` only
`#if (DEBUG_CC_EXEC)`. The build does not set that, so all three expand to nothing. The `-S` output shows
exactly one `cc_has_error` call in `Run`, the explicit one in `CALLEXT`. The loop head's
invalid-instruction and end-of-code checks are compiled out too.

So 16.3's premise ("`cc_has_error()` is a real call, H keeps it") was wrong. H costs nothing to keep
exact, and its saving goes back to ~15 instructions per no-fixup `movl`. I's padding is not optional:
with no end-of-code check in release, the unconditional argument reads need the padded code array to
stay inside the allocation.

## 17. Per-handler cost account of R_vm (static; coordinator order: before 0305) -- 2026-09-24

**Method (static only, per the constraint):**
- **Source:** `-S` of `cc_instance.cpp` on main 80a6d6f5 (build flags), with the handlers read one by
  one from `Run`'s dispatch table `L514` (`lab-mmd/show.py`, `walk.py`).
- **Branch directions** are taken from the source's semantics (e.g. `sourceline` with no hook, `subi` by
  register type), not from fall-through.
- **Called helpers** are counted from the linked binary (`objdump`/`nm` of `ags.exe`):
  - `malloc` 120 static instructions, `free` 54, `__divdi3` 143, `_M_default_append` 173, `new` 30,
    `delete` 12. Dynamic paths are estimated from these.
  - `uclock` is taken at its calibrated 4.23 us = ~169 instruction-equivalents (16.9's `pair1000_t`).
- **Weights:** MMD-CS's measured mix (probe 0291, all 31 opcodes it executes, 5,642/tick), with the
  measured sub-splits:
  - fixups: none 417, import 204, func 64, gdata 43, string 28;
  - MAR reads: stack 383, global 42, object 28, static array 1;
  - `subi` on MAR: 430, from `lsp_calls`, since `LOADSPOFFS` never runs.

Script: `lab-mmd/account.py`.

**Loop overhead per op** (head to the dispatch jump, plus the back-edge): 24 instructions for 0-argument
ops, 27 for 1-argument, 25 for 2-argument. The argument-count chain is `cmp 2 / cmp 3 / dec`, then the
loads and spills, then the range check and the jump.

| block | per tick | notes |
|---|---|---|
| loop head + back-edge | **146.9k (43%)** | 5,642 ops x ~26 |
| `movl` handlers | 36k (50.0k with overhead) | fixup switch, then `SetInt32` into the address-taken `codeOp.Args[1]`, then a 20-byte copy into the register; import path +`GetByIndex` call |
| `mov` | 15k (35.8k) | 20-byte register copy |
| `push` | 20k (30.7k) | two stack-space checks (not compiled out) + `WriteValue` switch on SP's own type + 20-byte write |
| `subi` on MAR (stack walk) | 19k (30.1k) | inlined `GetStackPtrOffsetRw`, 2.66 steps x 6 |
| `memread4` | 14k (26.5k) | MAR type switch + 20-byte write |
| `pop` | 12.5k (20.6k) | copy to a temp, zero the entry, copy the temp to the register (20 bytes twice) |
| `sourceline` | 5k (19.8k) | nearly all loop overhead |
| **65 `Run` entries** (64 `SCMD_CALL` recursions + 1 outermost) | **39.9k** | ~614 each; see below |
| everything else | ~40k | `farpush`, `farsubsp`, `jzi`, `cmpeq`, `ret`, `call`, ... |
| **total** | **344.8k = 8.62 ms** | |

**Reconciliation:** R_vm = `Run` 9.187 (measured) - R_api ~1.12 - R_marsh ~0.34 (both indicative) =
**~7.7 ms = ~308k**. The static total is **+37k (+12%) over**. The residual sits within:
- the estimated rows (`memwrite4`, `memwritelit`, object reads, `subi` on SP, malloc's dynamic path);
- the indicative R_api/R_marsh (+-0.2 ms moves R_vm by +-8k);
- DOSBox-X's cycle accounting, which is not exactly one cycle per instruction.

16's walker was 25% under because it missed the `Run` entries and the helpers. This account places
every large block.

**New finding: the per-`Run` entry cost.** Every script function call (`SCMD_CALL` recursion) and every
outermost run pays:
- (a) `FunctionCallStack func_callstack(16)`: a `std::vector<RuntimeScriptValue>` `resize(16)`. That is
  `operator new` -> `malloc`(320 bytes), 16 value-initialised entries, and on exit `delete` ->
  `free`. ~250 instructions.
- (b) the watchdog stamp `_lastAliveTs = FastClock::now()`, which is patch 0096's `DosUclockClock`: a
  `uclock()` port read (~169 instruction-equivalents) plus two 64-bit `__divdi3` and multiplies for the
  nanosecond conversion (~70). The stamp is only compared at every 1024th backward jump of a frame.
- (c) ~125 instructions of prologue and epilogue.

That is ~40k instructions/tick, ~1.0 ms at fixed cycles. On the 486, `divl` is 40 cycles and the port
reads cross the ISA bus, so this part is likely more expensive than its fixed-cycles share.

**Levers ranked by instructions saved per tick (fixed cycles), with register-allocation risk.** Every
lever below changes code in or around `Run`. Each needs 16.8's `-S` check (the loop body identical, or
the change stated and measured) before any run.

| lever | what | saves / tick | fixed ms | exact? | register-allocation risk |
|---|---|---|---|---|---|
| **I** | argument decode without the count chain (unconditional `arg1`/`arg2` loads, code array padded by 2 words, `arg3` behind one test) | ~12k | ~0.30 | yes, with the padding (no end-of-code check exists in release) | **HIGH**: it is the loop head, where G failed |
| **H'** (H generalised) | `movl`/`memwritelit` decode straight into the register: no-fixup -> `reg.SetInt32(arg2)`; other fixups write the register directly instead of via `codeOp.Args[1]` | ~11k | ~0.28 | yes (`SetInt32` writes all 5 fields; the `ASSERT` is empty) | medium: handler-local, and it removes an address-taken local, which may help |
| **M (new)** | `FunctionCallStack` with 16 entries of inline storage (same value-init, same doubling to the heap past 16) instead of a heap vector per `Run` | ~10k | ~0.25 | yes (same contents; un-pushed entries still value-initialised) | medium: `Run`'s frame grows by 320 bytes; `Push` is inlined into `farpush` |
| **L2 (new)** | watchdog: take the first stamp lazily instead of at every `Run` entry | ~11k | ~0.27 | **NO**: `sys_evt_process_pending` can run later inside loops over 1024 iterations and 60 ms. **Operator decision** | low-medium (prologue) |
| **L (new)** | watchdog: store the raw `uclock_t` and convert at the (rare) compare, with the same formula | ~4.5k | ~0.11 (more on the 486: `divl`) | yes (same conversion, same clamp) | low-medium (prologue; the member type changes) |
| J (new) | `pop` copies the stack entry straight into the register (no temp) | ~3k | ~0.07 | yes (registers and stack do not alias) | low-medium |
| D | O(1) stack walk | ~3k net | ~0.08 | yes | medium (every push/pop maintains an index) |
| E | load-time import resolution | ~2.7k | ~0.07 | needs a proof of no import changes after load | medium |

**Sum of the exact levers (I, H', M, L, J, D, E): ~46k/tick, ~1.15 ms at fixed cycles.** At A+B's measured
2.0-2.8x that is **-2.3 to -3.2 ms/tick on the 486**, against 16's -0.8 to -1.7. The difference is M, L and
H' (generalised), found by this account. With 0297 (-0.30 to -0.65, on the 486 now) and 0305 (0 to
-0.30), the designed-and-exact total reaches **-2.6 to -4.2**, past the -2.07 that the < 25 line needs.
That holds only if the levers do not cost each other their register allocation. Each lands alone, with
its own `-S` check and gates.

**Suggested order** (lowest risk and largest first; the coordinator decides):
1. M (exact, per-call);
2. H';
3. L;
4. I last, because of its risk;
5. J, D and E only if still needed.

L2 goes to the operator as a semantics question.

### 17.1 Coordinator decisions (2026-09-24, two messages that crossed)

- Section 17 is accepted, and so is the 16.3 correction.
- **Order:** score 0305 and land it; then **M -> H' -> L -> I** (I last). Each lever lands alone, with its own
  pre-registration, lab gates, and an `-S` check that reports `Run`'s instruction count and `this`
  reloads against clean. J, D and E are done only if still needed after those.
- **Probe 0306 (RTC sampling profiler): GO, after M.** It no longer gates the ranking. It is the tool
  that checks the 2.0-2.8x scaling on the 486 and whether the account's +12% is real. Conditions:
  1. **IRQ8:** lab-wb's WaveBlaster RTC pump (SDL 0230+) owns IRQ8 when `midi_tick=rtc`. 0306 refuses
     to start (logged, exit) if IRQ8 is already hooked by anything other than the BIOS. Its cells run
     with sound off or with a non-RTC MIDI tick.
  2. **Real mode and V86 time:** RTC interrupts that fire in real mode or V86 (DOS/BIOS calls, the DPMI
     host) either miss a PM-only handler or arrive with a meaningless EIP. RTC ticks are counted
     separately (a real-mode stub counter, or the RTC tick count against the samples recorded), and
     "not in PM app code" is its own bucket, so check (c) is not biased.
  3. HARD STOP on the known-address busy loop, and every recorded EIP must fall inside the exe's
     `.text`.
  4. Lab-only, never in `patches/`, an honest stamp, its own build directory, and the `-S` identity
     pre-check.
  5. The expected handler ranking (from 17) is pre-registered before any profile is read.
  If it validates, it is a hub candidate (`shared/tools`); the coordinator takes it to the hub.
- **L2 (lazy watchdog stamp): PARKED.** It is not exact, and the exact levers reach the line on paper.
  It goes to the operator only if they fall short on hardware.
- HW-MMD-5 (0297) is running in round D's tail today. Its result feeds the band check for every later
  lever.

### 18. Lever M, ags 0307 (`FunctionCallStack` with inline storage) -- PRE-REGISTRATION (2026-09-24, before any M run)

Order per 17.1: 0305 lands first, then M. **Slot numbering:** 0306 is reserved for the profiler, so M is
0307, H' will be 0308 and L 0309. That leaves I outside this worker's range (0290-0309); a slot for I is
asked of the coordinator before I is written.

**Change** (`lab-mmd/lever-0307-M-callstack-inline.diff`, `__DJGPP__`-gated, `Engine/script/cc_instance.cpp`
only). `FunctionCallStack` holds its first 16 entries in an inline array instead of a
`std::vector` resized on construction:
- The inline entries are default-constructed by `RuntimeScriptValue()`, as `resize()` value-initialised
  them.
- Growth past the current size builds a heap vector of twice the size, copies the old entries into its
  upper half and places the head at the middle, exactly as the vector version did.
- `GetHead`, `GetSize`, `Push` and `PopCount` keep their semantics.

`Run` constructs one of these on every entry, including every script function call through `SCMD_CALL`
recursion. So the change removes, per entry, `operator new` -> `malloc`, `_M_default_append`'s
bookkeeping, and `delete` -> `free`.

**`-S` check** (17.1's rule; `lab-mmd/hwalk.py`, `runcmp2.py`), `Run` against clean 80a6d6f5:
- **3,388 instructions against 3,365 (+23); `this` reloads 80 against 70 (+10).** The frame grows by
  304 bytes, which renumbers every stack offset.
- **The loop head is identical** apart from frame offsets. The **back-edge is identical**: `_pc` stays
  in `%ebx` and `this` in `%esi`.
- The hot-handler path lengths are identical for mov, movl, subi, sourceline, memread4, push, pop,
  farpush, jzi, setfuncargs, cmpeq, sub, addi, memwrite4, thisaddr, gte, call, add and jmpi. Two differ:
  **farsubsp +3 and ret +1** (~0.6k instructions/tick on MMD's mix).
- `_M_default_append` is still referenced once, from the growth path, which MMD never takes.

**Predictions (baseline: main with 0305 landed, clean):**
- fixed 40000, MMD-CS script event: **-0.15 to -0.35 ms/tick**. That is 65 `Run` entries/tick x
  150-250 instructions for the allocator, minus the ~0.6k from farsubsp and ret, at 40 instructions/us.
- AGS Quest: under 0.05 ms/tick (few script calls a tick). 5 Days: under 0.05.
- VM op counts unchanged.
- 486, on a later cell: **-0.3 to -1.0 ms/tick** (2.0-2.8x; the allocator touches scattered memory, so
  the upper end is plausible).

**Falsifier / stop:**
- a fixed-cycles change outside the band, in either direction;
- any determinism, state-witness or screen difference;
- a rebuilt `-S` that no longer matches the check above (loop head, back-edge, hot paths).

**Gates:** the 0297 set:
- determinism guard with baseline-twice and perturbation controls on MMD, AGS Quest and 5 Days (seeded);
- screen gate (fast conf, `--fixed-timestep`, exclusive, display 261, freezes as before);
- fixed-cycles timing on MMD-CS;
- `/sdldos:review` before landing.

**18.1 (coordinator, 2026-09-24):** the range is extended to **ags 0310-0319**, in addition to
0290-0309. 0300 and 0301 are not reused: the series applies in numeric order, so an I at 0300 would sit
before 0305 and 0307, and its loop-head hunks would apply against the wrong context. **I goes to 0310**
(or wherever lands last). M's pre-registration is accepted; its arms get built after 0305 lands.

#### 16.7 RESULTS -- ags 0305 passes every lab gate (2026-09-24)

Raw `tests/harness/results/{G305T-MMD,{MMD3,AQ3,5D3}{MW0a,MW0b,SBW,MWC},{MMD,AQ,5D}SG5{MW0,SBW,MWC}}-2026-09-24/`; all 22 cells
rc=0.
- **Timing (fixed 40000, MMD-CS):** clean `AGSL297` (`SPLREF-MMD`) 9.387 -> `AGS305` 9.353 ms/tick, **-0.034**
  (band -0.01 to -0.06: **met**).
- **Determinism guard:** on MMD, AGS Quest and 5 Days (seeded), the baseline twice is EQUAL, **0305 ==
  baseline EQUAL**, and the control is DIFFERENT.
- **Screen gate** (fast conf, `--fixed-timestep`, exclusive, display 261): every freeze landed on its
  requested tick. 0305 vs baseline is 3/3 equal on every fixture. The control differs on AGS Quest t400
  (124 px) and 5 Days t200 (1,904 px), the same pixels as 9.10 and 12.2, so the gate has power.

Next: format-patch, `/sdldos:review`, and landing on main (landing set only, no force). Its 486 arm goes
into the next round with a hardware session (not round D, which is already staged).

### 18.2 0305 LANDED (97ed39c4); HW arms for 0305; M's arms built (2026-09-24, before any M run)

**0305** is on main as 97ed39c4. Main had moved to 882fe9c8 with harness and PLAN changes only (no
vendor patches). Series re-applied clean, fingerprint e37383025da0; `verify-patches-applied` 0.

**HW arms for 0305** (the next round with a hardware session; same cell as HW-MMD-5). Prediction: B - A
**0 to -0.30 ms/tick**.
- A: `AGSL297.EXE`, sha256 `6bd425537035b9960ce8d509588e68c649faf31dd0b72cb8f24009beb46ac90d`, main 80a6d6f5.
  Its vendor series is identical to 882fe9c8's.
- B: `AGSL305.EXE`, sha256 `f159e932a8058e70b08fd03454580e2abfa8060fb227bd26730ca441a650f3c2`, main 97ed39c4,
  `build_dirty=0 sha12=75ae0819b212`. Read-only.

**M on main 97ed39c4.** The `-S` check was repeated on this tree and matches 18 exactly:
- clean `Run` has 3,365 instructions and 70 `this` reloads, identical to 80a6d6f5's;
- with M: 3,388 and 80; the back-edge and loop head are identical;
- hot paths are identical except farsubsp +3 and ret +1.

Binaries, all `build_dirty=1`:

| binary | contents | sha256 |
|---|---|---|
| `AGSM307` | main + M | `b4b5d577000bcd2c608424417983edbc01086c0006bbaa2a6bc4436eddfe28c4` |
| `AGSMW4` | main + 0292 | `21a07441640a34b69449cc409d74aaf0fe04576635ae37d9ceb53d087d857817` |
| `AGSMW4M` | main + M + 0292 | `a1880dae6c0e03c3149515c875dec9bdd832f7e8e48436ceba518685b33a7d68` |

The timing baseline is `AGSL305` (clean main), run in the same spec (MMD, and AGS Quest for its
under-0.05 prediction). Specs: `lab-mmd/gM.spec` (fixed 40000, shared per cell) and
`lab-mmd/gMscreen.spec` (fast conf, exclusive, display 261).

### 18.3 HW-MMD-5A scored (round D, 2026-09-24): a fresh 486 baseline; 5B dropped for time

Raw `~/git/dosags/tests/harness/results/HW-MMD-5A-2026-09-24/`: exit 0, room 50, `binary_sha12=0aa50f02be56`,
`build_dirty=0` (`AGSM3`, main 939d957b = current main without 0297). **HW-MMD-5B was dropped** because it
would have run past the round's cap, so there is **no 0297 A/B yet**. It moves to the next round, together
with the 0305 pair and M's pair if M has landed by then.

Against HW-MMD-4 (`AGSM1`, cc5b66f5), same cell, both over 999 script events:

| | HW-MMD-4 | HW-MMD-5A | change |
|---|---|---|---|
| script event ms/tick | 20.567 | **20.050** | **-0.517** |
| dispatch ms/tick | 22.686 | 22.154 | -0.53 |
| `rb` ms/call | 9.480 | 9.576 | +0.10 |
| steady / whole-run tick rate | 33.22 / 30.41 | 33.02 / 30.16 | -0.20 / -0.25 |

**What moved between them:** 0214, 0230, 0231 and journeys (0250-0253). None of them changes the script
path's instruction count: at fixed cycles MMD-CS's script event went 9.474 (`AGSM1`) -> 9.484 (the 0230 tree,
`AGSM2`), +0.01. The **486's -0.52 ms/tick with no fixed-cycles change is therefore a code-layout or cache
effect** (the 8 KB unified L1 and where the hot handlers now sit), not less work. Hardware repeats of one
binary have shown spreads of ~0.02% (8.2's CTR cells), so it is not run noise either.

**AMENDED 2026-09-24 (coordinator): this is a HYPOTHESIS, not a finding.** HW-MMD-4 and 5A differ in binary
*and* in day and boot. The 0.02% repeat spread came from other fixtures (C1P, CTR), not from this MMD
cell. The next MMD block's ABBA (18.4) separates the two.

**Consequence for every hardware band (0297 -0.30 to -0.65, 0305 0 to -0.30, M -0.3 to -1.0):** a binary
change can move MMD's 486 script event by about +-0.5 ms/tick through layout alone, the same size as
the levers. An A/B still measures the lever *plus* its layout shift, and that shift is a real property
of the landed binary, so the landed gain is what the A/B shows. But a miss or an overshoot of a band by
~0.5 ms is not evidence about the lever's mechanism. The coordinator is asked to consider one repeat of
an A arm in the next MMD block (that bounds run spread for this cell directly) and to read every
lever's band with this +-0.5 ms layout term in mind.

### 18.4 Next MMD hardware block -- ABBA and the reading rule (pre-registered 2026-09-24, before the round)

Coordinator order: every pair runs **ABBA**. If the whole block does not fit in one round, 0297's pair
goes first. Same cell as HW-MMD-0/4/5A. All binaries are clean (`build_dirty=0`) and read-only.

| pair | A | B | order | prediction B - A (486 script event, ms/tick) |
|---|---|---|---|---|
| **0297** (first) | `AGSM3.EXE` `dfb2aea83e04a13dd2319e63299f6c1d0d20433def22ad76a6d3cdd33e570c25` (main 939d957b) | `AGSL297.EXE` `6bd425537035b9960ce8d509588e68c649faf31dd0b72cb8f24009beb46ac90d` (main 80a6d6f5) | A B B A | -0.50 (band -0.30 to -0.65) |
| **0305** | `AGSL297.EXE` (as above) | `AGSL305.EXE` `f159e932a8058e70b08fd03454580e2abfa8060fb227bd26730ca441a650f3c2` (main 97ed39c4) | A B B A | 0 to -0.30 |
| M (only if landed by then) | clean main before M | clean main with M | A B B A | -0.3 to -1.0 |

**Reading rule (fixed now, the same for every pair):**
- **Run noise** N = the larger of |A1 - A2| and |B1 - B2| (script event, ms/tick). If N > 0.3 ms/tick, this
  cell is too noisy to score any band, and the pair is reported as noise-bound with its numbers.
- **Effect** D = mean(B) - mean(A).
- **Scored against the band with a stated +-0.5 ms/tick layout term:**
  - "band met" if D is inside the band;
  - "consistent with the band plus layout" if D is outside the band by at most N + 0.5;
  - "band missed" only beyond that.
- "Band missed" triggers 13.2's cache-confound check (and, for M, a look at the layout of `Run`'s hot
  blocks) before anything is concluded about the lever's mechanism.
- **The layout hypothesis (18.3)** is confirmed for this cell if N <= 0.05 ms/tick while
  |mean(5A-style A) - HW-MMD-5A| stays small and the pairs' D values scatter beyond their bands. It is
  refuted if N is of the order of 0.5 ms/tick (then 18.3 was run or boot noise). It stays open if neither
  happens.
- **Denominators:** every figure is the `evtype script` total divided by its 999 events, and every
  pair's four runs come from the same session.

**18.4 AMENDMENT (coordinator, 2026-09-24, before the round): a net-effect verdict comes first.**

- **Admission:** every code change also moves layout, so no A/B can separate a lever's own effect from its
  layout shift. With N + 0.5 of slack, the "consistent with band + layout" verdict can absorb almost any
  result for a small lever. For 0305 (band 0 to -0.30), any D from about +0.5 to -0.8 would be
  "consistent". So **the band verdicts for 0305 have no power over its mechanism.** For 0297 and M they
  are weak. The band verdicts stay in the record as written, as secondary.
- **Primary verdict per pair, NET EFFECT of the landed binary on the 486** (N and D as in 18.4):
  - **D < -N: GAIN**, the landed binary is faster on the 486.
  - **|D| <= N: NO MEASURABLE EFFECT.**
  - **D > +N: REGRESSION.** Investigate before anything else lands on top of it.
- **Keep or revert:** a lever with no measurable effect on the 486 stays landed only if it is exact and
  free. 0305 qualifies: it is exact, and its only cost is one compare per call.

### 18.5 0297 ABBA on the 486 (round E) -- SCORED by 18.4

Raw `~/git/dosags/tests/harness/results/M297{A1,B1,B2,A2}-2026-09-24/`. All four exit 0, one session:

| run | binary | script event (`evtype script` / 999) | steady | start (UTC) | power state at start |
|---|---|---|---|---|---|
| A1 | `AGSM3` 0aa50f02be56 | **20.224** ms/tick | 32.64 | 11:25:54 | **OFF: this cell powered the machine on** |
| B1 | `AGSL297` 9a3b05ce7e20 | 19.721 | 33.28 | 11:33:58 | on |
| B2 | `AGSL297` | 19.743 | 33.28 | 11:41:55 | on |
| A2 | `AGSM3` | 20.016 | 33.07 | 11:49:40 | on |

**By the pre-registered rule:**
- N = max(|A1-A2| 0.208, |B1-B2| 0.022) = **0.208 ms/tick**, below the 0.3 noise-bound limit.
- D = mean(B) 19.732 - mean(A) 20.120 = **-0.388 ms/tick**.
- **NET EFFECT: GAIN** (D < -N): the landed binary with 0297 is faster on the 486.
- Band (secondary): **met**, -0.388 is inside -0.30 to -0.65. The fixed-cycles cut was -0.098, so the
  486/fixed ratio for this lever is ~4.0x. That is inside 13.2's probe-measured upper bound (~5.1x), as
  expected once the probe's cache pollution is gone.
- **Layout hypothesis (18.3): OPEN by the rule.** N is neither <= 0.05 nor ~0.5.

**Sensitivity, stated separately (the rule is not re-applied):**
- A1 is the only run that started from power-off. The 486 in a cold machine ran MMD's script event
  ~0.21 ms/tick slower than the same binary warm.
- Among warm runs, the same binary repeats within 0.02-0.03 ms/tick, **even across sessions**: B1/B2
  0.022; `AGSM3` 20.050 in HW-MMD-5A (another session, warm) against 20.016 in A2, 0.034.
- With A1 set aside, D against A2 alone is -0.284 (just outside the band's -0.30 end).
- HW-MMD-4 and HW-MMD-5A were both warm cells, not power-on ones. So 18.3's -0.52 between them is two
  different binaries under warm-run conditions whose same-binary spread is ~0.03. That leans toward the
  layout hypothesis, but the rule says OPEN, and it stays OPEN until a pre-registered test decides it.

**Procedure proposal (for the coordinator, not applied retroactively):** start every hardware block with
a discarded warm-up cell after power-on (any binary, not scored), or put the power-on in a non-measured
step. The first measured cell of this block carried a ~0.2 ms/tick power-on penalty that doubled N.

### 18.6 Lever M -- fixed-cycles timing MISSES its band: STOP (pre-registered falsifier), 2026-09-24

Raw `tests/harness/results/{GMREF,GMT}-{MMD,AQ}-2026-09-24/`.

| | clean `AGSL305` | M (`AGSM307`) | change |
|---|---|---|---|
| MMD-CS script event (fixed 40000) | 9.354 ms/tick | 9.325 | **-0.029** |
| AGS Quest (135 events) | 366.25 ms/event | 366.20 | ~0 (as predicted) |

**The band was -0.15 to -0.35: MISSED, by a factor of ~5.** Per 18's falsifier, M stops. M is exact: the
MMD guard so far is EQUAL, with the control DIFFERENT. The remaining guard and screen cells are left to
finish for the record.

**Why the estimate was wrong:** -0.029 ms plus the +0.6k instructions/tick from farsubsp/ret is ~1.8k
instructions/tick, **~28 instructions per `Run` entry** saved, not 150-250.
- 17 sized the allocator from the helpers' **static** instruction counts (`malloc` 120, `free` 54,
  `_M_default_append` 173).
- Their dynamic paths are short. DJGPP's `malloc` is nmalloc: a `_searchfree` bucket hit and ~15
  instructions around it. The 16 value-initialisations, which 17 counted inside `_M_default_append`,
  still run in M (inline `RuntimeScriptValue()` constructors).
- So the per-call vector cost was mostly construction, which M keeps.

**Consequences:**
1. **17's per-`Run` entry cost is overstated.** Its ~250 for "(a) the vector" is really ~30 plus the
   16-entry construction, which both versions pay. That is ~11k of 17's +37k overcount, so 17's
   reconciliation improves to about +7%.
2. The **(b) watchdog stamp** part stands on better ground: the `uclock` read (~169
   instruction-equivalents) is measured, not estimated. L's divide saving (~70 per entry) is an estimate
   of the same kind that just failed, and has to be re-derived from `__divdi3`'s dynamic path (the
   operands are known) before L is pre-registered.
3. The ranking in 17 used static helper sizes only for M (and L's divides). H' and I are loop and handler
   paths read directly from `Run`'s `-S`, which is the method that 0293/0295 validated.

**For the coordinator:**
- (a) Land M as "exact and free", like 0305, or drop it? It saves ~0.03 ms/tick at fixed cycles, and
  its `-S` cost is two hot handlers +4. My read: it is not free enough to land on its own merits. I
  recommend **dropping M** and carrying the lesson.
- (b) Proceed to H' as ordered? Its estimate comes from `Run`'s own handler paths (no helper
  estimates), but it deserves a re-check of its instruction count against the `-S` of the changed
  handler before pre-registration, which I will do as part of its `-S` check.

### 18.7 Coordinator decisions; M DROPPED; H', L and I re-derived from dynamic paths; the target table with measured numbers (2026-09-24)

**Decisions (coordinator):**
- **M is DROPPED:** exact but not free. Tested (18, 18.2, 18.6), and the diff is kept at
  `lab-mmd/lever-0307-M-callstack-inline.diff`. Slot 0307 is not reused.
- H' is next, after its `-S` re-check.
- L is re-derived from `__divdi3`'s dynamic path before its pre-registration.
- **Rule from here on:** every estimate that rests on helper code uses a *dynamic* path. The
  static-helper method has now gone wrong twice: M over, 16's walker under.

**Re-derived sizes (all fixed 40000, MMD-CS mix):**
- **H' (0308), from its own `-S`** (`lab-mmd/lever-0308-Hp-littoreg-direct.diff`, `LITTOREG` only):
  - `Run` goes 3,365 -> 3,395 instructions, with `this` reloads unchanged at 70. The back-edge and every
    other hot handler are identical.
  - `movl`'s full path per fixup, clean -> H': none 35 -> 29, gdata 41 -> 37, func 38 -> 33,
    string 41 -> 38, import 58 -> 53.
  - Weighted by the fixups: **~4.1k instructions/tick, ~0.10 ms/tick** (17 said ~11k). Building the value
    in the register costs the same five stores as the copy it replaces; only the `codeOp` round trip
    goes.
- **L (0309), dynamic path.** `__divdi3` with a 32-bit divisor and a dividend whose high word is below
  it (both divisions in `DosUclockClock::now()`, for the first hour of uptime) runs **42 instructions,
  one `divl`**. From the `uclock` call to the store of `_lastAliveTs`, `Run`'s prologue has 53
  instructions inline. Keeping the raw clamped `uclock_t` needs ~12. So L saves **~125 instructions per
  `Run` entry, x 65 = ~8.1k/tick, ~0.20 ms/tick** (17 said ~4.5k). Its own `-S` check comes at
  pre-registration.
- **I (0310), from `Run`'s head paths** (read from `-S`, as 0293/0295 were, whose predictions landed
  within 5%):
  - the argument-count chain costs 9 instructions for a 1-argument op and 7 for a 2-argument op;
  - unconditional loads of `arg1`/`arg2` (padded code) plus one `arg3` test cost 6;
  - that saves 3 x 2,971 (1-argument ops) + 1 x 2,607 (2-argument ops) = **~11.5k/tick, ~0.29 ms/tick**,
    *if* the head's register allocation survives. That can only be known from its `-S`, and the head is
    where G failed.
- J, D and E (from `Run`'s paths; E's `GetByIndex` from its dynamic path): ~3k, ~3k and ~2.7k/tick.

**14.2's target table, with measured numbers** (486 logic ms/tick; the line is < 25):

| item | 486 ms/tick | basis |
|---|---|---|
| logic before 0297 (HW-MMD-4) | 27.07 | measured |
| 0297 | -0.84 | HW-MMD-4 script event 20.57 -> warm B1/B2 19.73; includes the main-branch drift that 18.3 describes, so it is not 0297 alone (0297's own ABBA D is -0.39) |
| **logic now (estimate)** | **~26.2** | 27.07 - 0.84 |
| **still to find for < 25** | **~1.2** | |

**Remaining exact levers, 486 ms/tick.** Scaling is fixed-cycles x 2.0-2.8, A+B's measured VM ratio.
L's range is computed from its cycles, because `divl` and `mul` are heavy on the 486.

| lever | fixed ms | low | central | high | main risk |
|---|---|---|---|---|---|
| I | 0.29 | 0 (fails `-S`) | 0.6 | 0.8 | head register allocation (the G mechanism) |
| L | 0.20 | 0.4 | 0.5 | 0.6 | prologue `-S` |
| H' | 0.10 | 0.2 | 0.25 | 0.3 | small |
| 0305 (landed, not yet measured on the 486) | 0.03 | 0 | 0.1 | 0.3 | none |
| J, D, E (if pursued) | 0.2 | 0 | 0.3 | 0.5 | medium (D, E) |
| **sum** | | **~0.6** | **~1.75** | **~2.5** | |

Every row also carries 18.3's +-0.5 ms/tick layout term per binary, in either direction.

**Plainly: yes on the central estimate.** The remaining exact levers cover the ~1.2 ms with ~0.5 ms to
spare, **but only if I lands.** Without I, L + H' + 0305 + J/D/E gives ~1.15 central, which is at the line
with no margin. On the low estimate (I fails its `-S`, the rest at the bottom) they do not cover it.
- **Probability of covering 1.2 ms on the 486 with exact levers:** low scenario ~25%, central ~55%,
  high ~75%. **My single number: ~55%.**
- It hinges on I's register allocation and on how the layout term falls.
- If the exact levers fall short on hardware, the parked L2 (lazy watchdog stamp, ~0.27 ms fixed and
  likely ~0.3 on the 486, not exact) is the known fallback for the operator to decide on.

### 19. Lever H', ags 0308 (`LITTOREG` builds its literal in the register) -- PRE-REGISTRATION (2026-09-24, before any H' run)

**Change** (`lab-mmd/lever-0308-Hp-littoreg-direct.diff`, `__DJGPP__`-gated, `LITTOREG` only):
`reg1.SetInt32(arg2); FixupArgument(reg1, ...)` instead of building the value in `codeOp.Args[1]` and
copying 20 bytes into the register.
- **Exact:** `FixupArgument` reads only the code word, the fixup tables, the strings and the stack,
  never the registers. Every case either leaves the argument as `SetInt32` made it or overwrites it
  whole, the same in both versions. `ASSERT_CC_ERROR` is empty in release (16.3 correction). In a
  `DEBUG_CC_EXEC` build it would return after the register was already written, where the original
  returned before. That is an error-abort path that only debug builds have.
- `WRITELIT` (33/tick) is left unchanged, one concern.

**`-S` (18.7):** `Run` 3,365 -> 3,395 instructions; `this` reloads 70 -> 70. The back-edge and every other
hot handler are identical. `movl`'s paths are shorter by 6 / 4 / 5 / 3 / 5 (none / gdata / func / string /
import).

**Predictions** (baseline: clean main 97ed39c4, `AGSL305`; its fixed-cycles MMD figure 9.354 comes from
`GMREF-MMD`, which is deterministic and not re-run):
- fixed 40000, MMD-CS script event: **-0.07 to -0.13 ms/tick** (4.1k instructions +-30%);
- AGS Quest and 5 Days: under 0.02;
- 486, net-effect verdict primary (18.4): 0.2-0.3 ms/tick central.

**Falsifier / stop:** outside the fixed band in either direction; any guard or screen difference; a
rebuilt `-S` that differs from the above.

**Gates:** guard x3 with controls, screen gate, timing, `/sdldos:review`.

### 20. Lever L, ags 0309 (the script watchdog keeps its stamp raw) -- PRE-REGISTRATION (2026-09-24, before any L run)

Order (coordinator): L, then I (hard stop at its `-S` read), then H'.

**Change** (`lab-mmd/lever-0309-L-watchdog-raw.diff`, `__DJGPP__`-gated):
- `DosUclockClock::now()` (patch 0096, `Engine/util/time_util.h`) is split into two parts, and
  `now()` = `from_raw(now_raw())`. Values are unchanged for every caller:
  - `now_raw()`: the `uclock()` read with the same single shared monotonic clamp;
  - `from_raw()`: the same two-divide nanosecond conversion.
- `ccInstance` keeps `_lastAliveRaw` (a `uclock_t`) instead of `_lastAliveTs`. It is written at `Run`
  entry, in `NotifyAlive()`, and at the watchdog's reset.
- The one comparison (every 1024th backward jump) converts it with `from_raw()`, the same formula, so
  it compares the same nanosecond values as before.
- **Exact:** the same clock reads at the same points, the same clamp, the same converted values at the
  compare, and the same outcome of every `> timeout` test.

**`-S` check** (against clean 97ed39c4):
- `Run` **3,365 -> 3,329 instructions; `this` reloads 70 -> 23**.
- **The loop head is identical** (frame offsets aside), **the back-edge is identical** (`_pc` in
  `%ebx`, `this` in `%esi`), and every hot handler path is identical.
- The stamp at `Run` entry goes from **53 instructions + 2 `__divdi3` calls** (42 instructions each on
  this path, 18.7) to **14 instructions, no divide**.

**Predictions** (baseline `AGSL305`, fixed MMD 9.354 from `GMREF-MMD`):
- fixed 40000, MMD-CS script event: 65 `Run` entries x ~123 instructions = ~8.0k, so **-0.14 to
  -0.26 ms/tick** (+-30%);
- AGS Quest and 5 Days: under 0.02 (few `Run` entries a tick);
- 486, net-effect verdict primary (18.4): central ~0.5 ms/tick (two 40-cycle `divl`s and the 64-bit
  multiplies per entry).

**Falsifier / stop:** outside the fixed band in either direction; any guard or screen difference; a
rebuilt `-S` that differs.

**Gates:** guard x3 with controls (baseline and control cells reused from gM: same binary and conf),
screen gate, timing, `/sdldos:review`.

**20 build record:** `AGSWD309.EXE` (main + L) sha256 `5a622aa83493833b5edb803713e1c370cb81d0f12193d0491494eef2d3f76eca`;
`AGSMW4WD.EXE` (main + L + 0292) `00fc6bcd6736ec2cc1f8350ded31571486e2f06e534a4a5376a37164e56e6bac`; both
`build_dirty=1`. They were built as `AGSL309`/`AGSMW4L` and renamed before any run, so as not to be
confused with the landed-main `AGSL*` builds. Specs: `lab-mmd/gL.spec` and `gLscreen.spec`.

### 21. Lever I, ags 0310 -- HARD STOP at the `-S` read (coordinator rule, as for G's variant); no runs, nothing pre-registered (2026-09-24)

**Written** (`lab-mmd/lever-0310-I-argdecode-unconditional.diff`, `__DJGPP__`-gated):
- the loop head reads `op_arg1`/`op_arg2` unconditionally and `op_arg3` only when `argc > 2`;
- the resolved code vector is padded by `kCodeReadPad` = 2 zero words;
- `_codesize` is taken from `code_fixups.size()`, the real size.

**`-S` read** (build flags, against clean 97ed39c4):
- `Run` 3,365 -> 3,485 instructions; `this` reloads 70 -> 25.
- **`_pc` has left `%ebx`: it now lives in the stack slot `-576(%ebp)`.** The loop head begins
  `movl -576(%ebp),%eax; sall $2,%eax`.
- The back-edge is `movl -576(%ebp),%edi; movl -588(%ebp),%ecx; leal 1(%ecx,%edi),%edx; movl %edx,-576(%ebp);
  movl %edx,1784(%esi)`, so `_pc` goes through memory on every instruction (107 references to the slot).
  Clean has `_pc` in `%ebx` and a 3-instruction back-edge.
- `%ebx` is now the scratch register for the argument loads. `this` stays in `%esi`.

**`_pc` left its register: the hard-stop condition. Stopped; nothing run; nothing pre-registered.** The
vendor tree is back to clean main.

**Reading.** This is the third time the same mechanism has decided a loop-head change: G (14.5),
G's variant (14.7), and now I. With unconditional argument loads GCC wants two more registers live
across the head, and on i586 it gives up `_pc`'s register to get them. Lever B's head shape (a branch
chain in which each path loads only what it needs) is the one this function allocates well. **The
loop head of `ccInstance::Run` should be considered closed to restructuring under this compiler and
flags.** Any future head lever needs a way to pin `_pc` (e.g. a local `register` variable with an asm
constraint, or splitting the dispatch into its own function). Each is a design question, not a tweak.

**Consequence for 18.7's target:** without I, the central sum of the remaining exact levers is
**~1.15 ms/tick** (L 0.5, H' 0.25, 0305 0.1, J/D/E 0.3), against the ~1.2 needed, **at the line with no
margin**. The low estimate falls short. The coordinator decides whether to take the parked L2 (the
lazy watchdog stamp: ~0.27 ms fixed, likely ~0.3 on the 486, not exact) to the operator now.

## 22. Probe 0306 -- RTC sampling profiler: DESIGN and PRE-REGISTRATION (2026-09-24, before any profile exists)

GO: coordinator (17.1), after M; M is settled (dropped). Lab-only, never in `patches/`, own build dir,
honest stamp (`build_dirty=1`). If it validates, it is a hub candidate (`shared/tools`), taken there by
the coordinator.

**Mechanism:**
- IRQ8, the CMOS RTC periodic interrupt (vector 0x70), programmed to 1024-4096 Hz through register A;
  PIE is set in register B. The PIT is untouched, because DJGPP's `uclock()` reads it.
- A small locked asm handler is installed with `__dpmi_set_protected_mode_interrupt_vector`. On each
  interrupt it:
  - counts every RTC tick (`rtc_ticks`);
  - reads the interrupted CS:EIP from its iret frame;
  - if CS equals the app's own code selector, stores EIP in a locked sample buffer; otherwise counts
    the interrupt in the **"not in PM app code"** bucket (real mode, V86, DOS/BIOS calls, the DPMI host);
  - reads RTC register C (ack), sends EOI to both PICs, and returns with `iret`.
- DJGPP's own hardware handlers (`__djgpp_timer_hdlr`, `__djgpp_hw_exception` in `libc.a`
  `exceptn.o`, read by disassembly) use the same `iret`-frame convention, though they take the exact
  EIP through the DS-limit fault instead. Whether the frame EIP is the client's under CWSDPMI is
  exactly what the HARD STOP below checks.

**Attribution:**
- Samples are mapped to functions with `nm`, and to source lines with `addr2line` on a `-g` build of
  the same tree.
- **`-g` does not change code:** `Run`'s `-S` with and without `-g` is identical (3,365 instructions,
  same sequence). The `.text` of the `-g` and non-`-g` executables is compared byte for byte before any
  mapping. If it differs, the mapping is void.
- Lines inside `ccInstance::Run` map to their `case SCMD_*:` block, or to "loop head/back-edge" for the
  lines before the dispatch `switch`.

**Conditions (17.1):**
1. **Refuse to start** (logged, exit) if IRQ8 is already hooked by anything other than the BIOS: the
   real-mode vector 70h not in segment F000, or the PM vector 70h already in the app's own code
   selector. Cells run with sound off (no RTC MIDI tick).
2. **"Not in PM app code"** is its own bucket. RTC ticks = PM app samples + other + dropped (buffer
   full), checked exactly.
3. **HARD STOP:** at startup, before the game, a validation loop spins for ~0.5 s inside a known
   `noinline` function. At least 90% of that window's samples must fall inside that function's
   address range, **and every recorded EIP must fall inside the exe's `.text`**. Otherwise: log, restore
   the vectors and exit. No profile is read.
4. Lab-only; `-S` identity pre-check (`Run` unchanged by the probe).
5. The expected ranking, below.

**Checks on a profile run (MMD-CS, 1000 ticks, fixed 40000, sound off):**
- (a) With the sampler off (env), the script event equals clean within 1%.
- (b) Sampler on vs off: the difference is ~ samples x the ISR cost measured in the validation loop,
  within +-25% (the ISR cost is small, so the tolerance is wide).
- (c) The share of PM samples inside `Run` and its callees during script events matches the split's
  measured `Run` share, within +-3 points. For this, the probe also counts samples taken while
  `dp_split_in_evt`-style flags are set, with the flags kept outside `Run`, as in 16.8.

**Expected ranking inside `Run`'s own code, MMD-CS** (from 17, corrected by 18.6/18.7; the share of
`Run`-internal samples):
1. loop head + back-edge ~40%;
2. `movl` ~13%;
3. `mov` ~10%;
4. `push` ~9%;
5. `subi` stack walk ~9%;
6. `memread4` ~7%;
7. `pop` ~6%;
8. `sourceline` (its handler only) ~1.5%;
9. the rest.

Outside `Run` during script events:
- `_uclock` plus `__divdi3` from the watchdog stamp: ~2-3% of the event;
- `malloc`/`free`: small (~0.5%, after 18.6);
- API bodies ~12% (16.9).

**Reading:** a handler more than 2x off its expected share is a finding for the account (17). The
486 profile (a later cell, through the coordinator) is read against this same list, to measure the
per-block 486/fixed ratios.

### 22.1 AMENDMENT (2026-09-24, before any profile run): the mapping check is done per object; build record

- **Mapping check changed.** A whole-program `-g` twin could not be linked (`make AGS_RUNSTATS_DEF="... -g"`
  broke an unrelated define path: an undefined `dosags_spr_px`). So the "`-g` and non-`-g` `.text`
  identical" check moved from the executable to the object that matters:
  - `cc_instance.cpp` compiled with `-g` (build flags, `build/lab/AGSPROF-cc_instance-g.o`) against the
    linked build's own `cc_instance.cpp.obj`: **`.text` byte-identical** (`objcopy -j .text`, `cmp`).
  - Samples inside `ccInstance::Run` are mapped as `EIP - Run@exe + Run@obj` through `addr2line -a -i` on
    the `-g` object. The outermost `cc_instance.cpp` line picks the `case SCMD_*:` block (or head/prologue).
  - Everything outside `Run` is mapped by `nm -n` of the executable.
  - Tool: `lab-mmd/prof.py`.
- **Build:**
  - Own build dir `build/ags-prof`; `lab-mmd/probe-0306-rtcprof.diff` (new
    `Engine/platform/dos/dos_prof.{h,cpp}` + hooks in `event.cpp`, `game_run.cpp`, `quit.cpp`,
    `engine.cpp` and `CMakeLists.txt`).
  - `AGSPROF.EXE` sha256 `b815239be53d931b3f6e154fb705f5e66ebed4b36e9d3491921ae3a29d4cd456`, `build_dirty=1`.
  - **`-S` identity:** `cc_instance.cpp` is untouched by the probe, and `Run` is identical to clean
    (3,365 instructions, 70 `this` reloads, 0 differing lines).
  - `.text` grows 0xA00 bytes and `.bss` 2 MB (the 512k-sample buffer).
- **Cells** (`lab-mmd/prof.spec`), fixed 40000, sound off (`[sound] enabled=0` in the cell's `ACSETUP.CFG`):
  - reads off (check (a) against `GMREF-MMD`);
  - sampler on at 4096 Hz, twice.
  - The startup validation (HARD STOP) runs in every sampler-on cell.
  - `run-cells.sh` now also collects `PROF.BIN` (edited with `sed -i`, which gives a new inode, so no
    running script is touched).

### 23. "K" -- frame-pointer read-first (coordinator, 2026-09-24): NOT PROMISING; not pre-registered; no runs

**(1) Where the frame pointer comes from.** No build file sets any frame-pointer flag (the `flags.make`,
`Makefile`, `sdl3-dos.mk` and CMake lists were searched). `i586-pc-msdosdjgpp-g++ -O3 -Q
--help=optimizers` reports **`-fomit-frame-pointer [disabled]` even at `-O3`**: keeping frame pointers is
this DJGPP GCC 12.2 build's target default.

**(2) What depends on frame pointers in this port.** Nothing in the port's code: no
`__builtin_frame_address`/`__builtin_return_address`, no stack walker, no traceback use in its docs or
harness. The profiler (0306) reads the interrupted EIP only. C++ exceptions use DWARF unwind tables
(`LEHB`/`_Unwind_Resume` in `Run`; no SJLJ), which do not need a frame pointer. **The one dependency is
DJGPP's own crash dump:** its "Call frame traceback EIPs" follows the `%ebp` chain, so a crash with a
frame-pointer-less function on the stack would give a broken or short traceback from that frame on.
That would be acceptable for one hot TU, with a note.

**(3) `-S` of clean `Run` with the flag** (build flags plus the option, `cc_instance.cpp` only):

| build | `Run` instrs | `%ebp`-slot refs | frame set up in `Run` |
|---|---|---|---|
| clean | 3,365 | 622 | yes |
| `-fomit-frame-pointer` | 3,692 | 907 | **yes** |
| + `-maccumulate-outgoing-args` | 3,513 | 899 (+211 `%esp`) | **yes** |
| + `-mincoming-stack-boundary=2 -mpreferred-stack-boundary=2` | 3,610 | 909 | **yes** |

The flag works for the file: functions with a frame setup drop from 50 to 14. But **`Run` is one of those
that keep `%ebp` as a frame pointer in every variant**, so no register is freed. And the allocation of
`Run` gets *worse*: +145 to +327 instructions, +280 stack-slot references, and `%esi` goes to the
argument count instead of `this` in the head. Stack realignment is ruled out by the boundary=2
variant, and SJLJ exception handling by (2). Why GCC keeps `%ebp` in `Run` was not established (that
would mean reading GCC's `frame_pointer_needed` decision in its RTL dumps). Within the read-first's
scope, **K does not free a register for `Run`, so it cannot reopen the loop head. K is not
pre-registered, and I is not re-read on top of it.**

(As a side note for any future attempt: the per-function
`__attribute__((optimize("omit-frame-pointer")))` would face the same `frame_pointer_needed` decision,
since the TU-wide flag already applies to `Run` and is overridden there.)

**18.6 addendum (record only; M is dropped):** M's remaining gate cells all finished, rc=0 in 25/25.
- **Determinism guard:** EQUAL on MMD, AGS Quest and 5 Days, with every control DIFFERENT.
- **Screen gate:** 9/9 equal; the controls differ on AGS Quest t400 and 5 Days t200.
- M was exact, as designed. It is dropped for its size (18.6/18.7), not for correctness.
- These baseline and control cells (`AGSMW4`) serve as the reused baselines for H' (19) and L (20).

### 20.1 Lever L -- RESULTS: exact, but MISSES its band (~zero effect): STOP. And the cause: 17's "65 `Run` entries a tick" was WRONG (2026-09-24)

Raw `tests/harness/results/{GLT-MMD,{MMD4,AQ4,5D4}LW,{MMD,AQ,5D}SG7LW}-2026-09-24/`: rc=0 in 7/7.
**Hashes verified:** `sha256sum` equals the manifest `sha12` for every cell (`AGSWD309` 5a622aa83493, `AGSMW4WD`
00fc6bcd6736), and the reused baseline is `AGSL305` f159e932a805.
- **Timing:** MMD-CS 9.354 (`GMREF-MMD`) -> **9.349 ms/tick, -0.005**. Band -0.14 to -0.26: **MISSED**. Per 20's
  falsifier, L stops.
- **Guard:** EQUAL on MMD, AGS Quest and 5 Days, with the controls DIFFERENT. **Screen:** 9/9 equal; every
  freeze landed on its tick. L is exact.

**Why: `SCMD_CALL` does not recurse into `Run`.** It pushes the return address and jumps within the same
`Run` loop (`cc_instance.cpp` `case SCMD_CALL:`, "Call another function within same script, just save PC
and continue from there"). **Only `SCMD_CALLAS`** (a call into another script instance) recurses
(`if (Run(...))`). In 17 I read that `CALLAS` code as `CALL`. MMD executes **no `callas`** (probe 0291's
histogram), so `Run` is entered **~1-2 times a tick** (16.9 measured `runs=999` outermost runs over 999
script events), **not 65**.

**Consequences:**
1. **17's "65 `Run` entries x ~614 = 39.9k/tick" block is wrong.** At ~1.5 entries it is ~1k. The static
   total becomes ~345k - 40k + ~1k = **~306k against the ~308k measured: the account reconciles within
   ~1%**. So 18.6's "~28 instructions per entry" for M was also computed over the wrong count: M's
   measured -0.029 ms (~1.2k instructions) is ~800 per actual entry, consistent with the allocator path.
2. **M and L missed for the same reason.** Both levers are exact, and both act per `Run` entry, which is
   rare. L's measured -0.005 ms is ~123 instructions x ~1.5 entries, which is what it should be.
3. **L2 (the parked lazy watchdog stamp) is worthless for the same reason.** One `uclock` read per `Run`
   entry is ~1.5 reads a tick.
4. **H' (19) is unaffected:** its size comes from `movl`'s own handler paths, x 722 per tick.

**18.7's target table, corrected** (486 ms/tick, central): L 0.5 -> **~0**; H' 0.25; 0305 0.1; J/D/E 0.3. The
remaining *designed* exact levers sum to **~0.65 against the ~1.2 needed. They do not reach the < 25 line.**
The loop head (~43% of the VM) is closed to restructuring under this compiler (G, G's variant, I; K cannot
free a register).

**Recommendation:** drop L (exact but ~zero; the diff is kept); do not land. The next lever class to read
is set out in the report to the coordinator.

### 24. Per-file codegen flags for `cc_instance.cpp` -- a `-S` scan (2026-09-24; text only, nothing run)

After 20.1, the designed exact levers reach ~0.65 of the ~1.2 ms/tick needed. Register allocation has
decided every loop-head change, so the scan asks whether a per-file flag, exact by construction, gives
`Run` a better loop.

Method: `cc_instance.cpp` with the build flags plus one option each (`lab-mmd/score.py`). The measures
are `Run`'s instruction count, the head path to the dispatch, the back-edge, and handler paths weighted
by MMD's mix (the 21 top opcodes).

| option | `Run` instrs | head | back-edge | weighted handlers | `_pc` / `this` |
|---|---|---|---|---|---|
| (clean) | 3,365 | 19 | 5 | 98.4k | `%ebx` / `%esi` |
| `-mtune=i486` (and `-march=i486`: identical) | 3,234 | 20 | 7 | **85.4k** | **stack slot** / `%ebx` |
| `-O2` | 3,109 | 20 | 5 | 106.3k | |
| `-fsched-pressure` | 3,365 | 19 | 5 | 98.4k | no change (no pre-RA scheduling on x86) |
| `-fira-region=one` | 3,362 | 19 | 5 | 98.4k | |
| `-fira-algorithm=priority` | 3,458 | 20 | 7 | 99.6k | |
| `-fno-gcse` | 3,699 | 19 | 5 | 111.3k | |
| `-fno-tree-pre` | 3,023 | -- | -- | -- | `_pc` reloaded from the member every head |
| `-fschedule-insns -fsched-pressure` | 3,477 | -- | -- | -- | `_pc` in a stack slot |

**Reading:**
- At fixed cycles (instruction count), nothing beats clean. The head plus back-edge plus weighted
  handlers total: clean ~233.8k; `-mtune=i486` ~237.8k (+4k).
- **`-mtune=i486` is the one variant that is a real question for the 486.** GCC's i486 cost model moves
  about 2 instructions per op out of the handlers (weighted -13k) into the head and back-edge (+3 per
  op), and it spills `_pc` to a stack slot. On an i486, an L1-hit memory operand costs about one cycle.
  i486 scheduling also avoids address-generation interlocks, which the 486 has and fixed cycles cannot
  see. So the variant's 486 cost cannot be predicted from fixed cycles in either direction. **This also
  means the `_pc`-spill hard-stop rule (G variant, I) was calibrated on fixed-cycles thinking. On the
  real 486 a spilled `_pc` may cost much less than its instruction count suggests.** That is a
  hypothesis; only a hardware cell can test it.
- Candidate hardware test (for the coordinator; nothing built): ABBA of clean main against main with
  `cc_instance.cpp` (or the whole engine) built with `-mtune=i486`. The net-effect verdict comes first.
  The whole-engine variant would also touch render, which the operator's goal counts as secondary.

## 25. Round G -- PRE-REGISTRATION (2026-09-24; round G needs the operator's approval; scorers committed with this section)

Scorers, committed here: **`lab-mmd/abba.py`** (18.4's rule, verbatim; checked against round E: it reproduces
18.5's N 0.208, D -0.388, GAIN, band met, and flags A1 POWER-ON) and **`lab-mmd/prof.py`** (the profile reader).
Coordinator decisions carried in: L dropped (20.1); L2 withdrawn (moot); J and D held unless the profile
shows nothing bigger.

### 25.1 The 486 profile cell (probe 0306)

**What already exists (no new cell needed):** the tick-stat timers already split the non-script logic on
the 486, from M297B1 (`M297B1.LOG`, ms per 1000 ticks):

| phase | ms/tick |
|---|---|
| dispatch outside the VM (`process_events_dispatch` 21.79 - `script_vm` 20.02) | ~1.8 |
| `input_handling` | 1.50 |
| `game_objects_update` | 1.07 |
| `input_poll` | 0.70 |
| `drawable_object_states` | 0.65 |
| `objects_scale` | 0.52 |
| `rep_exec_wrapper` | 0.39 |
| `gui_context_cursor` | 0.38 |
| `catchup_audio_poll` | 0.15 |
| the rest | <0.3 |

Against logic (`update_game_once_total` 30.63 - render 3.01 - scene 0.70 = ~26.9) - `script_vm` 20.02 =
~6.9 ms/tick non-script, **the named phases cover > 90%.** So "mapped" at phase level is done. **What the
profile must add is the function level inside those phases**, above all `input_handling` + `input_poll`
(~2.2 ms/tick on a run with **no** input) and `game_objects_update`.

**Binary:** `AGSPROF2.EXE` sha256 `c94d803fed0df70bff8efdcb7d275f0fd7824c63c3f178909b397e216e04632c` (probe 0306 v3,
`lab-mmd/probe-0306-rtcprof-v3.diff`, own build dir `build/ags-prof`, `build_dirty=1`).
- **Every RTC tick is a sample**: the EIP when the interrupted CS is ours, else a marker EIP 1 ("not in PM
  app code": real mode/V86/host, e.g. INT 33h mouse or INT 16h keyboard calls).
- Each sample carries the phase bits: bit 31 script event, bit 30 inside `update_game_once`, bit 29
  render/scene (kept by depth).
- Identity: `rtc_ticks = samples + dropped`.
- `-S`: `Run` identical to clean. `cc_instance.cpp`'s `-g` object has `.text` byte-identical to the linked
  one (`build/lab/AGSPROF2-cc_instance-g.o`).

**It runs in DOSBox-X first** (`lab-mmd/prof.spec`: reads off, on, on). Only if that passes the HARD STOP,
(a) and (b) does the 486 cell go to the coordinator. The 486 cell is the same cell as HW-MMD-5 at 4096 Hz;
**plus the same binary with `DOSAGS_PROF` unset**, in the same session, for the overhead bound.

**VOID rules:**
- The startup validation fails (HARD STOP; the program exits 4).
- Any window EIP falls outside `.text`, the marker excepted.
- `rtc_ticks != samples + dropped`, or `dropped > 0`.
- **Overhead:** the profiled run's `update_game_once_total` per tick exceeds the unprofiled run's
  (same binary, `DOSAGS_PROF` unset) by more than **ISR cost x sample rate x 1.5**, where the ISR cost
  is measured as (sampler-on - sampler-off) / samples in DOSBox-X, and bounded above by 5% of the tick.
- Check (c) is replaced, since the phases are now tagged directly. The **script-event share of logic
  samples must match the tick-stat share** (`script_vm` / logic, ~74%) **within +-5 points**.

**What counts as MAPPED** (the output must show it): in the "logic, non-script" bucket, **the top-15
named functions plus the "not in PM app code" bucket cover >= 80% of its samples**, and
`input_handling` + `input_poll`'s time is attributed to named functions or to real mode at >= 80%.
Otherwise the profile is reported as **unmapped at function level**, with the shares it did get.

**Expected (pre-registered before any profile):**
- the script-event share of logic ~74%;
- inside `Run`: 17's list (head/back-edge ~40%, `movl` ~13%, `mov` ~10%, `push` ~9%, stack walk ~9%, ...);
- `input_poll` mostly **not in PM app code** (a mouse/keyboard driver call per tick);
- `input_handling` in PM code (AGS's input processing), plus an unknown share of real mode.

### 25.2 `-mtune=i486` ABBA (practical-lever test)

**Scope: `cc_instance.cpp` alone** (`lab-mmd/lever-mtune486-cc_instance.diff`: one
`set_source_files_properties(... COMPILE_OPTIONS "-mtune=i486")` in `Engine/CMakeLists.txt`; own build dir
`build/ags-mtune`). Why this file alone:
- It is the narrower claim: the VM's scheduling only. 24's `-S` read is of this file.
- A whole-engine retune would also move render code and every layout. The operator counts render as
  secondary, and it would not tell us whether the VM gains.
- Layout still moves everywhere after this object (its `.text` grows 30,000 -> 30,592 bytes).

**Registered as a practical test ("does this build run faster on the 486"), NOT as evidence for the
AGI/scheduling mechanism.** Code layout moves with the flag, and 18.3's layout hypothesis stays open.
**The `_pc`-spill hard-stop rule stays for fixed-cycles work, unchanged, until hardware data exists.**

**Arms (ABBA, same cell as HW-MMD-5):**
- A = `AGSL305.EXE` `f159e932a8058e70b08fd03454580e2abfa8060fb227bd26730ca441a650f3c2` (clean main
  97ed39c4; the series is unchanged since).
- B = `AGSMT486.EXE` `f4f6ed4dd71c5aa9b989e02fade51f15250a9670fa85422d55bde4b91124041e` (main + the flag,
  `build_dirty=1`), read-only.

**Lab gates first** (`lab-mmd/gMT.spec`): the fixed-cycles timing cell (prediction, from 24's count:
**+0.05 to +0.15 ms/tick, i.e. slower at fixed cycles**), and the determinism guard x3
(`AGSMT486W.EXE` `a0bd09f6f09c58da1b0d374c693607664962495a628eea240476b3960d8c7f47`, main + flag + 0292,
against the reused `AGSMW4` baselines and controls). A guard difference means stop: a codegen flag must
not change behaviour.

**Verdict (`abba.py`, no band):**
- **GAIN only if D < -N**, where N is the ABBA's own same-binary spread. A GAIN is reported as "this build
  is faster on the 486 by D", with no mechanism claimed.
- NO MEASURABLE EFFECT or REGRESSION: the flag is not adopted.
- Denominators as in 18.4. A power-on first cell is flagged by the scorer and, per 18.5's proposal, a
  discarded warm-up cell precedes the block.

### 25.3 The remaining MMD pairs

- **0305** (18.4, unchanged): ABBA `AGSL297` / `AGSL305`, band 0 to -0.30; net-effect verdict first; the
  band has no power over the mechanism (18.4 amendment).

  **0305 arms for round G** (operator-approved, 2026-09-24; run order A B B A after the round's warm-up cell;
  score with `lab-mmd/abba.py` at commit 027dff00):

  | arm | path | sha256 (file) | manifest `binary_sha12` (build stamp) | tree |
  |---|---|---|---|---|
  | **A** | `~/git/dosags-lab-mmd/build/lab/AGSL297.EXE` | `6bd425537035b9960ce8d509588e68c649faf31dd0b72cb8f24009beb46ac90d` | `9a3b05ce7e20` (as in round E's M297B1/B2) | main 80a6d6f5 (0297 in, 0305 out), `build_dirty=0` |
  | **B** | `~/git/dosags-lab-mmd/build/lab/AGSL305.EXE` | `f159e932a8058e70b08fd03454580e2abfa8060fb227bd26730ca441a650f3c2` | `75ae0819b212` | main 97ed39c4 (0305 in), `build_dirty=0` |

  Both files are chmod read-only; their sha256s were re-verified 2026-09-24. **The manifest's `binary_sha12`
  is the build stamp (a hash of the vendor trees and flags), not a prefix of the file's sha256.** A run is
  the right arm if its manifest shows the stamp in this table. Scoring:
  `lab-mmd/abba.py <A1> <B1> <B2> <A2> -0.30 0` (band 0 to -0.30, secondary).
- **H' (0308), ONLY if its lab gates (19) pass:** ABBA clean main / main + 0308, built from the committed
  series after landing (as 0297 and 0305 were). Band 0.2-0.3 ms/tick (secondary). Pre-registered here;
  the arms' hashes are added before the round if H' lands.

**Order within the MMD block, if it does not all fit:** 0305, then the `-mtune` ABBA, then the profile
pair, then H'. That order puts the one landed-but-unmeasured lever first and the possible largest
practical gain next. The coordinator orders the round.

### 19.1 Lever H' (0308) -- RESULTS: every lab gate PASSES (2026-09-24)

Raw `tests/harness/results/{GHT-MMD,{MMD4,AQ4,5D4}HW,{MMD,AQ,5D}SG7HW}-2026-09-24/`: rc=0 in 7/7. **Hashes
verified:** `sha256sum` equals the manifest `sha12` for every cell (`AGSH308` 50f8d621e5c3, `AGSMW4H` 25e18edb987f).
- **Timing (fixed 40000, MMD-CS):** `AGSL305` 9.354 (`GMREF-MMD`) -> `AGSH308` **9.257 ms/tick, -0.097** (band
  -0.07 to -0.13: **met**). The -S estimate (4.1k instructions = 0.10 ms) was right; `movl`'s paths come
  straight from `Run`'s own `-S`.
- **Determinism guard:** EQUAL on MMD, AGS Quest and 5 Days, with the controls DIFFERENT.
- **Screen gate:** 9/9 equal; every freeze landed on its tick.

**Landing:**
- Main had moved again (a new vendor patch plus the Makefile stamp change `faefbe2d`). Merged; the series
  was re-applied clean with 0308 last (fingerprint 0ce6532350fd, `verify-patches-applied` 0). The new
  patch is audio-side (the silence throttle); the MMD cells run with sound off.
- **Round H arms (clean, read-only):**
  - A = `AGSPRE308.EXE` (current main without 0308) sha256
    `c23527e611a6f11dd504c5b037ed798f1ee075b3da9e02cdd9972a371c2686b8`, stamp `f05b69e9454b`;
  - B = `AGSL308.EXE` (main with 0308) sha256 `425c1609f50ac62cb712109f383e1fff99955d77830f93943dc3d491d849607f`,
    stamp `bc9c3704a839`.
  - The stamps use the new stamp rule (`faefbe2d`). The round G 0305 arms keep their compiled-in old-rule
    stamps (25.3).

### 22.2 Probe 0306 (v3) in DOSBox-X -- HARD STOP fired: the iret-frame EIP is not the client's (2026-09-24)

Raw `tests/harness/results/PROF{OFF,ON,ON2}-MMD-2026-09-24/`, `AGSPROF2` c94d803fed0d, rc=0.
- **Check (a) PASSES:** with the sampler off, 9.3448 ms/tick against clean 9.3447. The probe is inert when
  off.
- **Both sampler-on cells stopped at the validation:** `samples=4201 in_loop=0 other=4206 ticks=4206`. **Every
  RTC interrupt reported a frame CS other than the app's**, so the frame the PM handler receives under
  this DPMI host (CWSDPMI in DOSBox-X) does not carry the interrupted client CS:EIP at `[esp]`. The host
  reflects the IRQ through its own code, which is exactly the risk 22 named. The HARD STOP did its job:
  the program restored the vectors and exited 4. **No profile was read.** The 486 profile cell does not go
  to round H in this form.

**Proposal (needs GO): v4, taking the EIP the way DJGPP's own SIGPROF does.** The IRQ8 handler calls
`__djgpp_hw_exception` (libc `exceptn.o`, read in 22). That shrinks the app's DS limit, so the app's next
data access faults, and the DPMI exception frame carries the client's exact CS:EIP. A registered signal
handler then records `__djgpp_exception_state_ptr->__eip` with the phase bits.
- Real-mode and host time is then attributed to the first PM app instruction after it returns, which is a
  known bias. The "other" count is therefore taken from the RTC ticks the handler sees while the forced
  flag is pending, and reported separately.
- The same HARD STOP and `.text` checks apply.
- It is the libc-proven path, at the cost of a fault per sample: ~4 k faults/s. The overhead VOID rule
  (25.1) covers it.
