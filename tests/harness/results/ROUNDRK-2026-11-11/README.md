# Round RK -- 2026-11-11: USB4VC 0.5.108 PASSES its pre-registered hardware test (0 partial packets in 2,310, every MS3 stall rescued, holds up to 2,216 ms); the framing slip is gone, but each MS3 cell still went PLAY-VOID on one press -- the press spanning stall #2 lands at the next press's target (the board's post-hold summing) -- so there is still no MS3 baseline; P9M1 cells 99.14 / 98.80%, information only by the registered GUI-click rule

One power-on: relay-on 22:44:17Z, power OFF 00:04:18Z (driver exit 0; driver-started powerguard confirmed OFF 00:04:21Z, no
"fired DURING cell" line), cap 00:44:17Z not reached; vcctrld daemon_start_t unchanged (1794436694.32). Operator, directly
(question tool): "Power on now", after sdlports' shape check of 2c4b4015 (harness 5d3bfebe) and vcctrl's pre-check (rig clear,
watches armed 22:44Z; warm-up camera shot 22:45:22Z lit and readable, no password). Every cell exited 0 with stamp OK
(rkrel 942ad0260d36 / rkins 39abbc4b5c34, ags 0001-0373), pre = staged = post; BLASTER.TXT "A220 I7 D3 P330 T3"; witness lines
as registered (guictrlmark (default) mode=1: L2 on by default).
**Firmware note:** every cell's SUMMARY line reads `fw=VOID:firmware '0.5.108', staging record says '0.5.107'` (FW-VOID.txt).
That is a stale FW_EXPECT constant in the driver (carried from earlier rounds), not a cell defect: the pre-registration names
0.5.108, and the field is not among its VOID conditions. Each cell's BOARD-TAKE.json reads `fw_ver [0, 5, 108]` (RKCALQ, RKM1,
RKM2, RKMP, RKP1, RKP2). FW_EXPECT is fixed for later rounds in a separate harness commit (sdlports 2026-11-11).

| Cell | what | result |
|---|---|---|
| WARMUPRK | warm-up; first keyboard traffic through 0.5.108 | exit 0; BLASTER ok; typing worked |
| RKCALQ | short re-check against RJCAL | **GATE PASS**, drift 0 px on every point (DXL 60, DXA 190, DXB 289, y 120) |
| RKCAL | full cal, only on a calq miss | not run |
| RKM1 | MS3 baseline | **PLAY-VOID**: press 91 A at (929,121), outside 817..841 (113 of 114 presses in band) |
| RKM2 | MS3 baseline | **PLAY-VOID**: press 91, the same (113 of 114) |
| RKM3, RKM4 | MS3 baseline | not run: "two MS3 cells VOID on pointing (23:30:33)", as registered |
| RKP1 | P9M1, DRIVE 5 | 99.14% (60 of 7,003) |
| RKP2 | P9M1, DRIVE 5 | 98.80% (84 of 7,003) |
| RKMP | MS3 instrumented, TICKS | ran; drive6-gate.sh --play on a copy: PLAY-VOID (112 walks of 114) |

## Firmware verdict (pre-registered): PASS
- **pkt_partial 0 in every in-play window** -- and in the whole round: ev_in 2,324, pkt_built 2,310 = pkt_ok 2,310; pkt_partial,
  pkt_timeout, pkt_inhibit, edge_merged, ev_discarded, ev_buf_full all 0; zero mouse.dropped rows (vcctrl). Under 0.5.107, round
  RJ had 8 partials. The 14-event gap ev_in - pkt_built is moves summed into fewer packets after long holds (RKM1 4, RKM2 4, RKMP
  6), not losses.
- **Resumes inside +-5 s of both known stalls in every MS3 cell** (offsets from lock.acquired): RKM1 +131.5 / +132.5 s (636 ms)
  and +177.7 / +178.7 s (1,247 ms); RKM2 +130 s and +177 s (1,323 ms); RKMP +132.5 s and +178.8 / +179.8 s (~1 s).
- **Rescues vs ordinary waits** (vcctrl; information): a resume counts any packet that waited > 2 ms mid-packet, so only a
  max_wait_ms >= 200 ms marks a packet 0.5.107 would have abandoned. Confirmed rescues: RKM1 636 and 1,247 ms, RKM2 1,323 ms, RKP2
  2,216 ms (at the engine's exit, 8.7 s after the loop's last record: no measure touched). RKM2's stall #1, RKMP's two and RKP1's
  two resumes completed within one board poll, and max_wait_ms (a high-water mark) cannot show their lengths. Small resumes
  (38-104 ms) elsewhere are ordinary bus waits made visible.
- Keyboard through 0.5.108: RUN.BAT typing in every cell; kb_inhibit_retry 28 (normal retries).

## Why the MS3 cells still VOIDed: the press spanning stall #2 (information; LAB-MOVE 10, lab-rb)
- RKM1 and RKM2: presses 1-90 and 92-114 in band (A 830 / B 929, y 120-121); the framing never slipped. Stall #1 (press 52-53)
  delayed press 52 (press 53's click found the kid at x 876 instead of ~924) but it landed right.
- Press 91 (stall #2, a 1.25-1.32 s hold): the game logged two clicks back to back at (929,121) with the kid at one spot, then
  press 93 at 830. Press 91's held packet completed ~1 s late; the board (0.5.108) then summed press 91's queued same-button moves
  into one packet (vcctrl), so the corner re-home was lost and press 91's click registered at press 92's landing point.
- vcctrl's 0.5.109 (built, host-tested, not flashed; the operator's call): one queued event = one packet, strictly in order,
  replayed with its original spacing (capped at 250 ms), never merged across a button change, consolidating only when the queue is
  nearly full; and a 5 s wait budget for a packet that has not started. Press 91 would then land at its own target, late.
- The root cause stays the 486's stall (see round RJ's addendum and LAB-MOVE 10.10: audio_core_entry_poll -> SDL_DOSAudioPump's
  100 ms TryLock backstop, not proven); round RL's no-build PUMP_TIMEOUT=10 cell is the planned discriminator.

**No MS3 baseline.** Information only, not a baseline: RKM1 / RKM2 read 674 / 589 skips of 7,003 (90.4 / 91.6% displayed) with
113 of 114 presses walking -- the first nearly complete MS3 runs on the 486 (L2 on); RKMP (fine timing on) 1,116 skips (84.1%).
These are VOID cells by the registered rule and are not the campaign's measure.

## P9M1 cells (DRIVE 5): 99.14 / 98.80% -- information only by the registered rule
| Cell | displayed | room 1 + entry | room 2 | late | stall_ticks | audio | GUI clicks logged (presses) | walk targets |
|---|---|---|---|---|---|---|---|---|
| RKP1 | 99.14% (60) | 39 | 6 | 7 | 3 | 0 / 0 | 14 (29) | the 5 usual |
| RKP2 | 98.80% (84) | 40 | 9 | 27 | 3 | 0 / 0 | 14 (29) | the 5 usual |

Neither cell had an in-play board partial (0.5.108). The registered rule also makes a cell information only if its GUI-click
count differs from RH's 13 for the same presses: both logged 14 for 29 presses, so by the letter **this round has no bridge**.
Observation, for the next pre-registration: that rule is too strict -- the GUI-click count varies with the wall-timed clicks even
in cells with no known drop (round RG's eight cells logged 9-15 for 28-30 presses), so it cannot by itself mark a dropped click.
With 0.5.108 the board's own counters (pkt_partial, mouse.dropped) are the direct witness; the next round should use them instead.
RKP1 / RKP2 sit inside the registered 98.6-99.3% (L2-on expectation 98.90-99.03%).

## Rig (vcctrl)
Capture stick (probation, usb1-2): three disconnects early, each recovered by itself within ~2-5 s (22:49:40.8Z before any cell;
22:51:04.7Z and 22:51:07.4Z in WARMUPRK, a ~5 s video hole), then none for the last 73 min. Still a hardware item. Corrupt
frames: 2 unique, black, at launches (WARMUPRK 22:50:09Z, RKP1 23:34:50Z). Locks clean; every call ok.

Files: SUMMARY.txt, driveRK.sh / cellRK.sh / powerguard.sh / daemongap.sh / expected.txt / ORDER-CONFIRMED, POWERGUARD.txt,
WINDOWS.txt; RKCALQ's RECHECK-RESULT / GATE / FIRST-PRESS.json; RKM1 / RKM2's PLAY-RESULT / GATE / FIRST-PRESS.json; RKMP's
TICKS.BIN; every cell's BOARD-TAKE.json / BOARD-RELEASE.json. Captures and saves stay local (AUDIO-SHA256.txt, SAVE-SHA256.txt).

## Note (sdlports, after the round): the MS3 model looks pessimistic
RKM1 / RKM2's information-only 90.4 / 91.6% (VOID cells, so no verdict) sit above the 71-89% model range pre-registered for the
MS3 baseline in round RH (est486b; its later refit gave 81.2-82.8%). The model looks pessimistic for MS3 on ags 0373 (L2 on). Its
walking-tick cost is the first suspect, as registered; refit it before the next model figure is quoted.

## Correction (lab-rb 761dc437, LAB-MOVE 10.14, read on copies): the board's hold is not the 486's slow tick
The sections above call the hold at press 91 "stall #2" and name the 486's stall as the root cause. RKMP's ticks, placed on the
engine clock beside the board's poll times (anchors: presses 45-50, spread 0.05 s), say otherwise:
- Stall #1: the board window holds one 129.1 ms undrawn tick (lc 9490, room-2 entry +1,725, press 52's after-click tick, as in
  RJMP); everything else is ordinary. RKM1's hold here was 636 ms, ~5x that tick.
- Stall #2: the hold began within engine 169.83..170.83 s and ended by 171.82 s. No tick in that window exceeds 68 ms. The lone
  long tick nearby (lc 11304, 166.6 ms, entry +3,539) ends at 169.25 s, at least 0.6 s before the hold could start; press 90's
  packets went through without a hold.
- So the aux port stays held 0.6-1.3 s while the game loop runs at full rate. The hitch and the hold fall at the same game time
  (entry +~1,725 / +~3,540) but are separate events. vcctrl saw no guest mouse command, which points at interrupt or controller
  level (IRQ12 unserviced, or the 8042 busy). Untested: the hitch's SDL_Delay(1) -> BIOS INT 15h/86h waits use the RTC (IRQ8, on
  the same slave PIC as IRQ12). Round RL's PUMP_TIMEOUT pair is where that gets tested (information there, not its verdict).
- RKMP's presses (lab read; no gate file): 90 of 114 in band. Press 91's click hit GUI 10 (the top strip; the merged burst lost
  the corner re-home), and presses 92-113 each landed on the PREVIOUS press's target, a one-press lag that never recovered (RKM1
  / RKM2 recovered at press 93).
