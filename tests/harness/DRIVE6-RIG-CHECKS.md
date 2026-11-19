# DRIVE 6 rig checks (MS3 baseline and calibration rounds)

Source: LAB-MOVE.md sections 3.5 and 8 (lab-rb).

Tools:
- tests/harness/drive-walk6.sh: DRIVE6_MODE=ms for the play cells, cal for the calibration cell.
- tests/harness/drive6-cal.py: reads the calibration cell, or an MS3 cell with --play.
- tests/harness/drive6-gate.sh: the round driver's one-line decision after a cell, from drive6-cal.py. After the cal
  cell: `GATE PASS <env>` (exit 0), `GATE RECENTRE <env>` (exit 3: re-run the cal cell once with these centres, then
  `--no-recentre`), `GATE STOP <reason>` (exit 1). After an MS3 cell (`--play`): `GATE PLAY-OK` (0) or
  `GATE PLAY-VOID <reason>` (1). It writes CAL-RESULT.txt / PLAY-RESULT.txt and GATE.txt into the cell dir.
- tests/harness/cell-template-d6.sh: the round cell script, cellRG.sh + DRIVE 6.
- tests/harness/drive6-pointer.py: the pointer model, and `replay`, its evidence from every DRIVE 5 run.

**The pointer model** (drive6-pointer.py; fits 229 of 232 DRIVE 5 runs click by click, and round RH's RHCAL press):
- one `vcctrl mouse move` is one PS/2 packet, and the USB4VC board caps it at +-127 counts per axis, so a big move is
  a 127-count move;
- CuteMouse moves linearly, 3.0 px per count in x and 1.5 in y, in a 512x384 screen, for packets of 12 counts and up.
  y is exactly half of x: SDL3-DOS divides fn 0Bh's mickeys by fn 1Bh's mickeys-per-pixel, 8 across and 16 down.
  - Independent y packets give 1.5 px per count: RICAL's CAL-BR (120 counts -> 180 px from the 383 clamp), and DRIVE
    5's 127, 90 and 40-count moves (1.50, 1.50, 1.475).
  - RICAL's DY slope (1.866 over 8..21 counts; 1.59 over 12..21; 1.63 over 15..21) is not a different y gain. It is
    the small-packet loss at 8..11, plus whole-pixel readings of 1.5-pixel steps over a 6..9-count span. The 1.5 model
    predicts every DY point from 12 counts up to 1 px (12 -> 116 and 21 -> 130 exactly).
- A packet under 12 counts loses counts before the cursor sees it (round RI): <= 9 counts lose 8/3, 10 lose 2, 11
  lose 1. This is upstream of INT 33h (our SDL3-DOS / AGS path is float end to end).
- The play path sends only single packets of 15..127 counts, and DRIVE6_DY must be >= 15;
- MMD's frame sits 1:1 at (96,92) in it, so the cursor can hide up to 96 / 92 px outside the frame.

Every DRIVE 6 press therefore parks in a corner with two 127-count packets, then makes two target packets (4 vcctrl
calls). The old single "+-480" corner moved only 127 counts, and the old scale (x 1.5, y ~1.45) is withdrawn.

**What the lab can and cannot reproduce.**
- **(i) CuteMouse / INT 33h acceleration or speed doubling on the 486's PS/2 path: cannot.** DOSBox-X has its own
  INT 33h emulation and no PS/2 device, and the lab cells place the cursor directly.
- **(ii) USB4VC's handling of a single event over 127 counts (clip or carry): cannot.** There is no board in the lab.
- On the Gateway there is no host-side chunking (vcctrl: one `mouse move` = one EV_REL event, then the board).
- **What the lab can reproduce:** the game side, i.e. what lies under a point (walk, GUI, object, hotspot, exit).
- **So the cal cell measures (i) and (ii) on the 486:** its prelude (check C10, and CAL-MCLIP for clip vs carry).

**The witness is the game's own log.** STDOUT.TXT's `MoveCharacter: request move cDave: X0,Y0 to X,Y` lines give each
click's exact point. The camera only confirms game state. The VGA capture does not lock on this mode ("nolock" is
expected).

Every check below runs on files the round already collects:
- STDOUT.TXT;
- DRIVE-WALK.LOG;
- INPUT-LOG.jsonl;
- run-hw.out.

## First, on every DRIVE 6 cell: a short run (drive6-gate.sh, ahead of any other check)

| # | check | pass | fail -> stop condition |
|---|---|---|---|
| G0 | DRIVE-WALK.LOG's `done: N presses` against the planned count in its first line | N == planned (114 ms / 61 cal / 13 calq / 83 m) | `GATE STOP presses sent N < planned M` (cal) / `GATE PLAY-VOID ...` (ms); no done line: the driver did not finish. Round RH's RHCAL reads `presses sent 1 < planned 40` |
| G1 | Failed presses: each click line's `rc_press` / `ok` / `failed_at` (one-call press) or `rc_home / rc_x / rc_y / rc_down / rc_up` (split) | none | `GATE STOP` / `GATE PLAY-VOID N failed press(es), first: click K (failed_at=...)`. The driver re-checks the lock after any failed press |

## Before the first DRIVE 6 cell (once per round)

| # | check | pass | fail -> stop condition |
|---|---|---|---|
| P1 | Dry run on the round host: `DRIVE6_MODE=ms tests/harness/drive-walk6.sh --dry-run` (and `=cal`) with the round's DRIVE6_* values; `drive6-pointer.py plan` on it | 114 presses (ms) / 61 (cal); each press is 4 moves of <= 127 counts (CAL-BR 3; the prelude's slow / fast probes more; CAL-MCLIP's one 200); the plan puts every MS3 press inside its band | anything else: **do not start the round**. drive-walk6.sh refuses old-model values itself (DY outside 0..30, ...) |
| P2 | The round driver exports DRIVE6_MODE and DRIVE6_DY / DXL / DXA / DXB for DRIVE 6 cells (or sets them per cell), and calls cell-template-d6.sh's copy | DRIVE-WALK.LOG's first line names the mode and values | wrong mode or values in the first cell's log: **stop after that cell** |

## The calibration cell (DRIVE6_MODE=cal; one per power-on, before any MS3 cell)

Run line: P9M1's play line verbatim (AGSSAVE.007, ACSETUP-ON-512X384-ROUND.CFG, release exe, --no-fine-timing,
`DOSAGS_TAS_AUTO_EXIT_TICK=12440`) with DRIVE 6 and `DRIVE6_MODE=cal`. The cell has 61 presses, ~152 s
(drive-walk6.sh's header has the full list):
- **The measurement prelude**, room 1, 11 presses 4 s apart. It measures the transfer function itself, which the lab
  cannot:
  - one x packet each of 8, 20, 30, 45, 60 and 88 counts (x = 285 - 3 d);
  - 60 counts as 4 slow packets (0.4 s apart) and as 4 fast ones;
  - 16 y counts as one packet and as 4 slow ones;
  - one 200-count packet: x 75 if the board clips, 205 if it carries.
  Every point is clear of room 1's two live regions (x 238..247 and 275..290, from the lab hover map).
- **Room 1**, 22 presses: CAL-C (the TR corner, x must be 319) alternates with CAL-DXL, swept 44..60 counts (x 36..84).
- **CAL-EXIT:** the TL corner, x must be 0. It walks the kid into room 2.
- **Room 2**, from EXIT + 10 s, 22 presses: CAL-DXA, swept 66..81 (x 172..217), alternates with CAL-DXB, swept 39..51
  (x 262..298). The DXA presses also carry the DY sweep, 8..21 counts (y 110..130), ascending. They carry it rather
  than B because at y <= 111, room x 932..955 is hotspot 2: a click there walks to the hotspot's own point, 942,138
  (the lab replica showed it). For the same reason MS3's B must keep y >= ~112.
- **5 more presses:** CAL-BR (the bottom-right corner) read the screen's bottom bound, for information.

Every quantity's points are fitted with a line (the pointer is linear). The value that hits the target comes from the
line, so one run converges even if the default is off. It does so as long as the rig's gains are within x -7%..+8%
and y +-4.6% of the model's; the measured gains are good to < 1%. A and B are calibrated in room 2, where MS3 uses
them; in room 1 an object at x ~285-289 swallows clicks where B lands.

Read with:

    tests/harness/drive6-cal.py STDOUT.TXT DRIVE-WALK.LOG     (or tests/harness/drive6-gate.sh <cell dir>)

| # | check | pass | fail -> stop condition |
|---|---|---|---|
| C1 | Every press walks | walk targets logged == presses sent (50); no "Mouse click over GUI"; rooms entered exactly [1, 2], the change right after CAL-EXIT; every press in its room; room-1 points at x >= 20, every point at y <= 142 | **stop the round**: pointing is not under control. A y >= 143 press hit the verb bar |
| C2 | TR corner: CAL-C, two (+127,-127) packets, then (0,+127), (0,+DY) | x == **319** on all 11 | **stop the round**: the corner does not clamp; R / A / B have no anchor |
| C3 | TL corner: CAL-EXIT, two (-127,-127) packets, then (0,+127), (0,+DY) | x == **0** | **stop the round**: L / EXIT have no anchor |
| C4 | DY: the fitted line's value for y **120** (never under 15: the nearest allowed value is taken), on the sweep's values of 15 counts and up (8..14 are reported as information) | lands in **116..140** and lies inside the swept 15..21 | outside the sweep: `GATE RECENTRE` with the fitted value, re-run the cell once; still outside: **stop the round** |
| C5 | DXL: the fitted value for x **60** | in **48..72**, inside the sweep | as C4 |
| C6 | DXA: the fitted value for screen x **190** (room x - 640) | in **177..201** (room 817..841), inside the sweep | as C4 |
| C7 | DXB: the fitted value for screen x **289** | in **276..300** (room 916..940), inside the sweep | as C4 |
| C8 | Repeatability: each value's repeats | **<= 2 px** (DRIVE 5's identical moves logged identical points on three days) | **stop the round**: the mouse is drifting or dropping. Check D1 / D2 before any re-run |
| C9 | The slope of each line against the model: DXL +3.0, DXA / DXB -3.0, DY +1.5 px per count | within **25%** | **stop the round**: the pointer path is not the one the model and drive-walk6.sh assume |
| C10 | Linearity over exactly the sizes the play path sends (amended after round RI, sdlports): each quantity's sweep points of **15 counts and up** -- DXL 44..60, DXA 66..81, DXB 39..51, DY 15..21, all single packets measured directly | every point within **2 px** of its line | **stop the round**: the response is not linear over the play path's sizes, so no fit (and no extrapolation) transfers |
| -- | Information, not a check | the whole measurement prelude (one-packet sizes 8..88; 60 counts as 4 slow / 4 fast packets; 16 y counts as 4 x 4; the clip / carry probe) and every sweep value under 15 counts. All still printed in CAL-RESULT.txt, the slow / fast probe's landings beside one packet's included. Round RI: packets under 12 counts lose counts (x 8 -> 269, not 261; 4 x 4 y -> 106, not 122) | none. The reason is stated in CAL-RESULT.txt: the play path sends one packet per move, each of 15..127 counts, so neither small packets nor multi-packet moves are ever sent |
| -- | What guards against the board merging queued events | the DXL / DXA / DXB / DY sweeps, not the slow / fast probe. Every sweep press is sent exactly as the play path sends its presses: one `vcctrl mouse press` call at pace 0.05, the two corner packets (127, -127) then the target packets (e.g. `127,-127 127,-127 -75,127 0,11`). The board sums whatever is queued before a packet goes out and caps the sum at 127, so a merge would move the landings: a corner packet merged into the target's x packet (127 - 75 = 52 counts) lands 150+ px off; the target's (x, +127) merged with (0, +DY) clips y to 127 and loses DY's 22+ px. Either fails C10's line or C4-C7's band | the sweeps' checks above (C4-C7, C10) |
| -- | No extrapolated value passes | C4-C7 pass only for a value inside its swept range, on a line that C8 says holds within 2 px across the sweep | a value outside the sweep is `GATE RECENTRE`: it is only the centre of the next cell's sweep, which must measure it |

**Result.** `drive6-gate.sh` prints `GATE PASS DRIVE6_DY=.. DRIVE6_DXL=.. DRIVE6_DXA=.. DRIVE6_DXB=..`; the model's own
values are 15 / 52 / 75 / 42. Those values go to every MS3 cell of the same power-on.
- **A later power-on runs the short re-check instead** (below), against the last full calibration that PASSes.
- A miss in the re-check, or no PASSing reference, means a full calibration cell.

## The short re-check (DRIVE6_MODE=calq; each later power-on, before any MS3 cell)

Proposed after round RI: RICAL measured every value directly with 0-1 px spread (DXL 52 -> 60, DXA 75 -> 190,
DXB 42 -> 289, DY 15 -> 120 over 46 presses; corners 319 / 0). A power-on that changes nothing needs only a check of
those points, not the sweeps again.

**Run line:** P9M1's play line with DRIVE 6, `DRIVE6_MODE=calq`, and DRIVE6_DY / DXL / DXA / DXB set to the
reference's values.

**The cell:** 13 presses, 2 s apart, ~34 s from the first press (one-call presses; latency stub: late max 0.07 s):
- room 1: CAL-C (TR corner) and CAL-DXL alternate, 3 times each;
- CAL-EXIT (TL corner);
- room 2, 10 s after the exit: CAL-DXA and CAL-DXB alternate, 3 times each;
- every press at y from DY.

The cell still runs ~670-700 s on the rig, because run-hw's floor sets a cell's wall length. The saving is no second
cal cell and no re-centre, not minutes inside the cell.

**Read with:** `tests/harness/drive6-gate.sh <cell dir> --recheck <reference cal dir>`. G0 and G1 (short run, failed
press) come first, as for any DRIVE 6 cell.

| # | check | pass | fail -> stop condition |
|---|---|---|---|
| Q0 | The reference (e.g. round RI's RICAL), re-read with the current rules | PASS | `GATE STOP`: no reference; run the full calibration |
| Q1 | calq used the reference's values (its log header) | DY / DXL / DXA / DXB equal | `GATE STOP`; run calq again with the right values |
| Q2 | Every press walks; rooms exactly [1, 2]; no GUI click; each press in its room | as stated | `GATE STOP` -> the full calibration |
| Q3 | Every press against **MS3's landing bands** (sdlports): CAL-C x 319, CAL-EXIT x 0, DXL x 48..72, DXA x 177..201 (room 817..841), DXB x 276..300 (room 916..940), every y 116..140 | every press inside its band, so a re-check PASS means for MS3 what a full-cal PASS means | `GATE STOP recheck: <first miss>` -> **the full calibration**; no MS3 cell until it PASSes |
| Q4 | Drift from the reference: each point against the reference's own measurement (x per kind, the corners 319 / 0; y the reference's DY median), printed beside every point, e.g. `DXL 57 (ref 60, -3 px)`, and each quantity's worst point in the PASS line | every point within **6 px** of the reference | not a stop: `GATE PASS <env> NEXT-FULL-CAL drift: ...`. The values serve this power-on (every press landed in MS3's bands), but **the next power-on runs the full calibration**, not calq on this reference: chained re-checks on a drifting reference could walk the rig to a band edge unseen |

**Result:** `GATE PASS DRIVE6_DY=.. DRIVE6_DXL=.. DRIVE6_DXA=.. DRIVE6_DXB=.. [NEXT-FULL-CAL] drift: DXL .. (ref .., .. px) /
DXA .. / DXB .. / y ..`. The reference's values go to every MS3 cell of the power-on; a round driver takes only the
`DRIVE6_*=N` words (as driveRI.sh's apply() does), and records NEXT-FULL-CAL for the next power-on.

**Tested** on the pointer-model stub against a copy of RICAL:
- an unchanged rig: PASS;
- an unchanged rig: worst drift y +1 px;
- x gain -2%: PASS, drift DXL -3 / DXA +3 / DXB +2 / y +1 px;
- x gain -5%: PASS NEXT-FULL-CAL, drift DXL 52 (ref 60, -8 px) / DXA 201 (ref 190, +11 px) / DXB +6 / y +1 px: MS3
  still lands in band this power-on, the next one runs the full cal;
- y gain -3% / -5%: STOP (y 114 / 109, outside 116..140). y has 4 px of band below the reference's 120, so a y drift
  downward stops before it reaches the 6-px flag; upward it is flagged from +7 px.
- driveRI.sh's apply() on a NEXT-FULL-CAL line takes exactly DY 15 / DXL 52 / DXA 75 / DXB 42 (the drift text has no
  `DRIVE6_*=N` word).
- CAL-BR's line in CAL-RESULT.txt reports the driver's bottom bound (383 expected). It is not a bar. It decides whether
  a later revision may anchor at the bottom (3 calls a press instead of 4).

## Every DRIVE 6 cell (calibration and MS3)

| # | check | pass | fail -> stop condition |
|---|---|---|---|
| D1 | Moves sent: INPUT-LOG.jsonl's `cmd` records, in either form. **One-call press** (DRIVE6_PRESS=one, the default for ms and cal): ONE `mouse_press` record per press, `ok: true`, detail `left dwell=0.2 moves=127,-127 127,-127 -75,127 0,15` for an A press: the planned moves in order. A daemon-side refusal (limits, unknown button, the lock held by someone else) is a `cmd.error` record instead, with nothing sent. **Split press** (DRIVE6_PRESS=split): the press's `mouse_move` records, then `mouse_down`, `mouse_up`. A stuck-button audit counts a `mouse_press` as balanced. On this profile one EV_REL is one packet (no mouse_max_step), so DRIVE 6 keeps every move at <= 127 itself | every press's moves as planned, all ok; no `cmd.error` | a missing, extra or failed move, or any `cmd.error`: cell **VOID**. Twice in a round: **stop the round** |
| D2 | Drops: INPUT-LOG.jsonl `mouse.dropped` rows in the lock window. Count them and note their times against DRIVE-WALK.LOG's presses | **reported, not a bar on its own.** Every DRIVE 5 cell has 1-3 rows (pkt_partial / pkt_timeout / edge_merged: RGA1 3, RGB1 2, RFMP 2, RDMP 3, RCMP 1), and DRIVE 5's logged click points were still identical across three runs | a drop that changes a click shows up in the game log: C1 / C8 in the calibration cell, M1-M3 in a play cell, and those stop. More than 5 rows in one cell: note it for the vcctrl owner |
| D3 | CLI timing: DRIVE-WALK.LOG `late=` on every press | **<= 0.20 s** (the budget below) | one press over: note it. More than 3, or any > 0.5 s: cell **VOID**; in two cells: **stop the round** |
| D4b | vcctrl's own replies (one-call presses): `FIRST-PRESS.json` (the cell's first press, always) and `FAILED-PRESS-<click>.json` (each failed press) beside DRIVE-WALK.LOG in the cell's results dir: the reply as printed (steps with ok / t_ms, dwell_s, elapsed_ms; on a failure failed_at, release, and vcctrl's one-line error from stderr, in the order they arrived) | FIRST-PRESS.json present, every step ok; no FAILED-PRESS file | read with G1 / D4: a FAILED-PRESS file is a failed press (`release` says whether the button was let go) |
| D4 | Return codes: DRIVE-WALK.LOG `rc_press` and `ok` (one) or `rc_home / rc_x / rc_y / rc_down / rc_up` (split) | all **0** / ok=1 (the gate's G1) | cell **VOID**; **stop the round** if the next cell repeats it. A one-call press that fails after the down still releases the button (its JSON's `release`) |
| D5 | Lock / run: DRIVE-WALK.LOG ends `done: N presses` with N = 114 (ms) / 40 (cal); run-hw.out `run-hw exit=0` | as stated | fewer presses: the run ended early; cell **VOID** (the round driver's run-hw stop rule applies as for DRIVE 5) |

### D3's budget: every call and spawn in drive-walk6.sh's live loop, per press

Measured costs:
- vcctrl calls: round RH's RHP1 INPUT-LOG, consecutive mouse commands 0.08-0.58 s apart (median 0.199 s); a latency
  stub at 0.15-0.20 s a call reproduces the 0.176 s median.
- Spawns: this VM, median of 20 runs.

| step | process spawned | cost | how often |
|---|---|---|---|
| lock check `owner_now`: `vcctrl lock status` piped to `python3` (json) | vcctrl + python3 | ~0.18 s + ~0.05 s | every 10th press (n % 10 == 5) and after any failed call -- no longer every press |
| wait until the press's move start / its planned time | none: bash `read -t` on a pipe (builtin sleep), `$EPOCHREALTIME` arithmetic | 0 | every press |
| pointer moves: `vcctrl mouse move` | vcctrl | 0.15-0.20 s each | 4 per full press; 2 per reclamp press (DRIVE6_MS_PATH=reclamp); prelude probes more |
| `vcctrl mouse down left` | vcctrl | 0.15-0.20 s | every press |
| dwell | none (builtin sleep; inside the daemon for a one-call press) | 0.2 s (DRIVE6_DWELL; was 0.4). A one-call press's dwell has `mouse click`'s `click_hold_s` floor (vcctrl MOUSE.md 10b); gateway2000 sets none (vcctrl examples/vcctrl.example.yaml; only the Macintosh profile has one, 0.1 s), so 0.2 s is used as asked. Every press line logs `dwell_s=`, the reply's dwell actually used: a value above 0.2 means a floor went live, and this budget grows by the difference | every press |
| `vcctrl mouse up left` | vcctrl | 0.15-0.20 s | every press |
| log line (clock, late=, rc codes) | none: `printf -v` / `printf '%(..)T'` (was `date` + `tee`, + 3 python3 for timing) | < 0.1 ms | every press |
| the press's moves | none: built once before the first press | 0 | -- |
| **one-call press** `vcctrl --as OWNER mouse press --moves "..." --dwell 0.2 --pace 0.05` (replaces the moves, down, dwell and up above) | vcctrl | one round trip (~0.15-0.20 s) + the daemon's own ~0.45 s (4 moves x 0.05 pace, the 0.2 s dwell, up + pace) | every press (DRIVE6_PRESS=one); the cal prelude's 2 slow probes stay split |

**Totals against MS3's gaps** (1.14-1.26 s; room 2's ~1.2 s cadence is fixed by the registered fixture):
- **One-call press (the default for ms and cal):** latency stub (0.15-0.20 s round trip, emulating the daemon's own
  time), 114 MS3 presses: wall median 0.65 s (daemon 0.45 s); late= max 0.02 s logged, 0.04 s true (the stub's real
  down times), median 0.00, final 0.01; **none over 0.2 s**. The cal cell (61 presses): late max 0.03 s.
  - The pace is 0.05 s, not vcctrl's 0.012: the board sums every event queued before a packet goes out and caps the
    sum at 127, so two 127-count corner moves 12 ms apart could merge into one capped packet. The calibration's
    sweeps, sent exactly as the play path sends (corner packets then target packets, one call, pace 0.05), show a
    merge as moved landings: C10 or C4-C7 fails. The prelude's fast probe is information only.
  - late= for a one-call press is an estimate: call start + half the call's overhead (wall - elapsed_ms) + the down
    step's t_ms.
- **Full press** (4 moves + down + up + dwell): ~1.25-1.4 s, more than the gap. Latency stub: median 1.28 s a press,
  late= median 3.65 s, 95 of 98 room-2 presses over 0.2 s, **9.68 s late by the last press. Does not fit**, by
  ~0.08 s a press.
- **Reclamp press** (2 moves + down + up + dwell): ~0.9-1.0 s.
  - Latency stub: median 0.96 s; late= max **0.16 s**, final 0.00, none over 0.2 s.
  - The 10 full presses among them: late max 0.16, mean 0.07; recovered on the next press.
  - At the top of the range (every call 0.206 s): 12 of 98 presses 0.21-0.37 s late (the full presses and the one
    after), final 0.02.
- **Split** is the fallback (DRIVE6_PRESS=split). On the full path it does not fit (above); with
  DRIVE6_MS_PATH=reclamp it fits under the same stub (late max 0.17 s, final 0.00).

## Every MS3 play cell (DRIVE6_MODE=ms)

Read with:

    tests/harness/drive6-cal.py --play STDOUT.TXT DRIVE-WALK.LOG      (reads INPUT-LOG.jsonl beside DRIVE-WALK.LOG for M0)

| # | check | pass | fail -> stop condition |
|---|---|---|---|
| M0 | No board partial packet (round RJ; checked first). Record: vcctrld's `INPUT-LOG.jsonl` in the cell dir, its `mouse.dropped` rows with `pkt_partial` > 0 (`polled_t` = the board poll that saw it; the board polls about once a second). Each press's window is from the same file's own cmd rows (`mouse_press`, by the lock's owner), so both times are on vcctrld's clock | no `pkt_partial` row whose `polled_t - 1 s` falls at or before the last press's call end | **VOID the cell from the first press whose call ends at or after `polled_t - 1 s`** (a partial in the park voids from press 1): `GATE PLAY-VOID framing slip at press N (pkt_partial polled t=<time>Z, INPUT-LOG mouse.dropped; ...)`. Reason: stock usb4vc abandons a packet after a > 200 ms between-byte timeout or a mid-byte inhibit, and CuteMouse keeps the bytes already sent: its 3-byte framing stays shifted for the rest of the run, and every later press lands pinned bottom-left (RJM1 from press 52, RJM2 from press 53: docs/lab/LAB-MOVE.md section 10). Not a pointing failure: the calibration stands. A missing INPUT-LOG.jsonl, or press calls that don't match the presses sent, is VOID (the partial can't be placed). `edge_merged` drops are printed, not a void |
| M1 | Every press walks | walk targets == 114; rooms entered exactly [1, 2]; no "Mouse click over GUI" | **VOID the cell and stop the round**: pointing has left the calibrated band (the next cells would measure a different scene) |
| M2 | Room 1 pointing | R x == 319; L x 48..72; EXIT x == 0; y 116..140 (calibrated target 120) | as M1 |
| M3 | Room 2 pointing | A room x **817..841**; B room x **916..940**; y 116..140 (the lab-tested +-12 px) | as M1 |
| M4 | The kid stays in room 2 | no `Now in room 1` after room 2 (the exit fires at x ~949) | as M1 |
| M5 | Game end before the run-hw floor | run-hw.out's screen goes static by ~t+235 s; `waited` <= ~310 s (DRIVE 5 cells: game end ~t+223 s, waited ~301 s) | over: note the extra wall time against the round budget. The cell stands unless it hit the timeout |

## Not a stop

- **The capture.** WITNESS-CAPTURE-STALE with stale_kind "nolock" is expected on this mode, as for DRIVE 5.
- **The camera.** It confirms room 1 / room 2 and the cursor. It is not read for positions: its frame estimates were
  wrong (x ~1.8 / y ~0.75 px per count against the measured 3.0 / 1.5, before the cap and the hidden margins).

## Round budget facts

- **The run line.** MS3 and the calibration cell use P9M1's play line verbatim:
  - AGSSAVE.007;
  - ACSETUP-ON-512X384-ROUND.CFG;
  - `DOSAGS_TAS_AUTO_EXIT_TICK=12440`;
  - the release exe, `--no-fine-timing`, `RUNHW_MIN_WAIT_S=270`;
  - plus DRIVE 6 and DRIVE6_MODE.
- **DRIVE 5 cells, measured.** An MMD cell on that line takes **670-697 s** (RGA1 670, RGB1 683, RGA2 671, RFA1 688,
  RDMP 677, RFMP 697).
  - The game reaches the TAS exit ~t+223 s after RUN.BAT.
  - run-hw collects at ~t+301 s: the 270 s floor plus 60 s of a static screen. The floor, not the game, sets the run
    phase.
- **An MS3 cell: the same 670-700 s expected.** Plan the same 750 s "typical" and 1800 s timeout as a DRIVE 5 cell.
  - The pacer model (LAB-MOVE est486b) has MS3 losing 0.4-4.3 s more game time than the DRIVE 5 fixture: wall from
    the restore to the exit is 181.7-185.2 s against 181.3 s.
  - So the game ends at ~t+224-228 s, inside the floor. This is a model figure; check M5.
- **The calibration cell: the same 670-700 s.** Its 61 presses end ~152 s after the first press, which comes ~41 s
  after the lock: well before the TAS exit.
- **Lab vs rig line.** The lab's MS3 cells ran RFMP's instrumented line (fine timing on, TICKLOG, ROUTE_PREWARM=1).
  The P9M1 line has no pre-warm, so the first click after each room load costs more on the rig (LAB-RB: 237 / 374 ms
  without it). The click schedule and the walking do not depend on any of these.
