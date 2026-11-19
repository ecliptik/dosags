# Round RJ -- 2026-11-11: the DRIVE 6 calibration PASSED (identical to RICAL), but every MS3 cell lost PS/2 framing at a board partial packet at ~+132 s (press 52-53) and went PLAY-VOID -- the first two stopped the MS3 block as registered; the USB4VC board abandons a partly sent packet, a firmware fix (0.5.108) is built, not flashed; no MS3 baseline; P9M1 cells 98.79 / 98.84%, drop-affected again

One power-on: relay-on 21:10:10Z, power OFF 22:27:38Z (driver exit 0; driver-started powerguard confirmed OFF 22:27:43Z, no
"fired DURING cell" line), cap 23:10:10Z not reached; vcctrld daemon_start_t unchanged (1794424802.12). Operator, directly
(question tool): "Power on now", after sdlports' shape check of f2b59133 + 25e526cf (harness local main 84ca3445) and vcctrl's
pre-check (rig clear, watches armed 21:10Z; warm-up camera shot 21:11:13Z lit and readable, no password; the power-on was clean
on the mouse counters). Every cell exited 0 with stamp OK, pre = staged = post; BLASTER.TXT "A220 I7 D3 P330 T3"; witness lines
as registered.

| Cell | what | result |
|---|---|---|
| WARMUPRJ | warm-up | exit 0; BLASTER ok |
| RJCAL | DRIVE 6 full calibration (amended C10) | **GATE PASS** DY 15 / DXL 52 / DXA 75 / DXB 42 |
| RJCAL2 | conditional re-centre | not run (PASS) |
| RJM1 | MS3 baseline | **PLAY-VOID** (gate: 58 walk targets for 114 presses); framing lost from press 52 (below) |
| RJM2 | MS3 baseline | **PLAY-VOID** (56 for 114); framing lost from press 53 |
| RJM3, RJM4 | MS3 baseline | not run: "two MS3 cells VOID on pointing (21:53:37)", as registered |
| RJP1 | P9M1, DRIVE 5 | 98.79% (85 of 7,003); drop-affected (below) |
| RJP2 | P9M1, DRIVE 5 | 98.84% (81 of 7,003); drop-affected |
| RJMP | MS3 on the instrumented build, TICKS | ran (CALOK); framing lost from press 52 again (the driver does not gate it; drive6-gate.sh --play on a copy: PLAY-VOID, 56 for 114) |

**No MS3 baseline.** The registered measure (RJM1..RJM4's displayed %) does not exist this round: both cells that ran are VOID,
and RJM3 / RJM4 were not run. Information only, not a baseline and not comparable: RJM1 / RJM2 / RJMP read 789 / 715 / 834 skips
of 7,003, but from press 52-53 on every click hit the verb bar and the kid stopped walking, so those totals mix ~half a moving run
with ~half a standing one.

## RJCAL: PASS, and the pointer model holds across power-ons
CAL-RESULT.txt is identical in substance to RICAL's: corners 319 / 0; the clip probe at x 75; DXL / DXA / DXB at exactly 3.000 px
per count, 0.0 px residual, landing 60 / 190 / 289; DY 15 -> y 120 on 46 repeats (spread 1); small packets (information) losing
counts exactly as the per-packet model says. FIRST-PRESS.json (vcctrl's reply, kept for the first time): elapsed_ms 473.5, every
step ok, moves at t_ms 50 / 100 / 150 / 201, dwell 0.2 s. 61 presses, 0 press errors, 0 board drops.

## Why every MS3 cell failed: PS/2 framing lost at a board partial packet
- **The shape.** In RJM1, RJM2 and RJMP every press up to 51 lands in band (room 1, then room 2's A 830 / B 929 at y 120). The
  first wrong landing is press 53 in all three (a walk to screen x 0); from press 54 every click is "Mouse click over GUI 1" (the
  verb bar) to the end. Nothing recovers.
- **The board witness (vcctrl).** Each cell's first {pkt_partial +1, pkt_timeout +1, pkt_inhibit 0} board poll falls in press 52's
  or 53's call window (RJM1 21:37:23.343Z / press 52; RJM2 21:48:37.948Z / press 53; RJMP 22:22:24.15Z / press 52), at ~+132 s after
  lock.acquired in all three; a second partial follows at ~+178 s (press ~91) with edge_merged +2 a poll later. host_cmd / host_ff /
  host_f5 / kb_inhibit_retry are flat around every in-play partial (the guest sent the mouse nothing). RJCAL and RICAL (2.5 s
  cadence, kid standing) had no partial.
- **The mechanism (LAB-MOVE section 10, lab-rb fcb716bf; desync.py).** USB4VC 0.5.107 abandons a PS/2 packet when the host holds
  the bus >= 200 ms between bytes; the bytes already clocked out stay with the host, and CuteMouse 2.1b4 does not resync on bit 3,
  so every later 3-byte packet is read shifted. Re-framing MS3's real byte stream after a 1- or 2-byte slip pins every click at the
  bottom-left, on the verb bar -- what all three cells show. Poll-merging of correctly framed packets is ruled out: no grouping of a
  press's packets can reach x 0 or y >= 143. The board does not coalesce moves (vcctrl's counters).
- **What holds the bus.** Not a mouse command (host_cmd flat), not a mid-byte inhibit (pkt_inhibit 0). 60 of 100 historical
  partials fall in the engine's exit; the in-play ones (RJ's among them) come mostly with the game loop at full speed, so IRQ12 goes
  unserviced at interrupt level. Our code holds interrupts off only briefly and never touches the 8042 (LAB-MOVE 10.7); the open
  suspects are below it (CuteMouse's IRQ12 path, CWSDPMI's reflection, the BIOS disk path, the SB ISR). For MS3 the partials are
  deterministic in game time (~+132 / ~+178 s), so something the game does at fixed points in room 2 triggers it; RJMP's TICKS.BIN
  is the trace to read (analysis to follow as an addendum).
- **The fix.** vcctrl built USB4VC firmware 0.5.108 ("resume": an interrupted packet is kept until the host has every byte; a
  bounded, non-blocking wait; no OR-merge across a button change; +-127 summing unchanged), host-tested 11 / 11. Not flashed: the
  operator chose build now, flash later. MS3 back to back is the hardware test (expect pkt_partial flat, pkt_resumed rising at
  press ~52). Until then the gate VOIDs an MS3 cell from the press that meets a pkt_partial (drive6h cd151f0b, local; for the next
  round's pre-registration).

## P9M1 cells (DRIVE 5): 98.79 / 98.84% -- no bridge again
| Cell | displayed | room 1 + entry | room 2 | late | stall_ticks | audio | GUI clicks logged | walk targets |
|---|---|---|---|---|---|---|---|---|
| RJP1 | 98.79% (85) | 49 | 4 | 24 | 4 | 0 / 0 | 8 | the 5 usual + 959,101 |
| RJP2 | 98.84% (81) | 49 | 10 | 14 | 3 | 0 / 0 | 10 | the 5 usual |

Both had an in-play partial (RJP1 21:59:52.85Z, engine 129.4 s; RJP2 22:12:02.05Z, engine 175.4 s), and their game logs differ
from RH's 13 GUI clicks for the same presses (RJP1 also logged an extra walk to 959,101). Under the registered rule both are
information only: **this round has no bridge.** The partial problem therefore also touches every DRIVE 5 cell from its partial on
(LAB-MOVE 10.6: walks end before most partials, so walk targets survive, but later clicks and their GUI ticks do not).

## Rig (vcctrl)
No capture-stick USB event during the cells. After the last cell (from 22:27:11Z, past the 22:27:35Z power-off) the stick
churned on usb3-2 (devices 80 -> 82..90, "Cannot enable. Maybe the USB cable is bad?", kernel power cycles; vcctrld's own port cycle at 22:28:05Z), still absent at
22:28:20Z -- the same shape as the 2026-11-10 23:38Z idle churn; no cell data affected; vcctrl asked the operator about the
stick / cable and asked that no round start until it is back. Mouse: 8 partials this round
(RJM1 x2, RJM2 x2, RJP1, RJP2, RJMP x2; all pkt_timeout + pkt_partial, pkt_inhibit 0); no stuck button; every vcctrl call ok. One black corrupt frame at the RJM2 launch.
jobs/ not collected.

Files: SUMMARY.txt, driveRJ.sh / cellRJ.sh / powerguard.sh / daemongap.sh / expected.txt / ORDER-CONFIRMED, POWERGUARD.txt,
WINDOWS.txt; RJCAL's CAL-RESULT.txt / GATE.txt / FIRST-PRESS.json; RJM1 / RJM2's PLAY-RESULT.txt / GATE.txt; RJMP's TICKS.BIN.
Captures and saves stay local (AUDIO-SHA256.txt, SAVE-SHA256.txt in each cell).

## Addendum (after the round, from the round's own records; lab-rb LAB-MOVE sections 10.6 and 10.8)
- **RJMP's TICKS: a lone logic-side stall before each MS3 partial** (lab-rb 9f9b9ad1). Room 2's only ticks of their kind: lc 9508,
  119.5 ms, undrawn, right after press 52's click and inside partial 1's window (engine 124.21 s); lc 11294, 201.5 ms, adjacent
  to a click, 0.7 s before partial 2's window (engine 169.66 s; the wall-to-engine anchor is good to ~1 s). They are 45.5 s
  (1,820 ticks) apart, matching RJM1 / RJM2's lost-tick seconds and all three cells' partials. The instrumented skipframe line
  for lc 9508's frame totals 172.1 ms with 112.6 ms outside every timed phase (that residue is median 10.5 ms over the run, the
  next-largest 32.8). Apart from the room load and the first room-2 click, every other room-2 tick is <= 96.5 ms. The later 231
  / 539 ms ticks carry the misread clicks and are consequences. Reading: the game does something at a fixed game time, for
  ~110-200 ms, that none of the engine's phase timers cover; if it holds IRQ12 off it does so through a call (disk, BIOS, or
  another real-mode path), since our own interrupts-off sections are all short. It is also a frame-pacing cost RUNMANI's
  >= 250 ms stall list misses. Not every partial is this: RDMP (DRIVE 5) partialed at engine 123.5 s with no tick over 31 ms.
  The lab is identifying the game content at those ticks; instrumentation would be a reviewed diagnostic patch.
- **sdlports' DRIVE 5 question (why past DRIVE 5 cells with partials kept matching walk targets).** Answered from the records
  (lab-rb 5f33a32c, move-lab/rj/drive5partials.py, DRIVE5-PARTIALS.txt): DRIVE 5's walking ends before its partials begin, so no
  re-framing is involved. Of 213 DRIVE 5 cells with STDOUT.TXT and INPUT-LOG.jsonl, 151 have a partial; the first falls at click 9
  or later in 150 of them (clustered at clicks 16-21 and 39-50), while walk targets appear only at event positions 1-9 (homed clicks
  1-7); the one exception (CSV16H3, click 4) logs no walks. 60 of 100 placeable partials fall in the engine's exit, after every
  measure ends. For past A/Bs the effect is noise from the partial's click onward (later clicks hit the verb bar and change the
  scene's GUI ticks; RIP1 / RIP2 / RJP1 / RJP2's GUI-click counts are instances); it is unbiased only if partials are independent
  of the arm, which has not been tabulated.
- **MS3's tick costs on the 486, from RJMP (presses 17-51, the stretch still in frame; lab-rb c64c3ff3, move-lab/rj/MS3-COSTS.txt).
  Information, not a baseline** (RJMP is the instrumented build with fine timing on, and its run is VOID from press 52). Medians,
  486 vs est486b's model: walking ticks (1,073) logic 18.1 / 18.0 ms + draw 6.8 / 6.6 ms = 24.9 vs 24.6 ms against the 25 ms budget
  (est486b's main unknown, now measured: as modelled); idle 18.0 / 17.5 + 4.9 / 4.9; click ticks logic 63.6 vs 51.6 ms (the model's
  click scale ~1.44 should be ~1.95); the post-click large present ~34 ms at click +2 / +3. Over the stretch RJMP skipped 398 of
  1,648 ticks (75.8% displayed); est486b's ranges (327 fitted, 261..428; 368 with the click scale at 1.95) contain it, the fitted
  point ~18% low, mostly the click logic. The first measured look at a moving MMD scene on the 486: walking alone leaves ~0.1 ms of
  slack, so every click's debt is repaid in skipped frames.
