# dosags -- gate plan (2026-09-26)

Written by the dos-review session after the 2026-09-25 review. ADOPTED by the
operator as the work order on 2026-09-26 (~05:5xZ, question tool, relayed by the
coordinator), with the amendments marked "operator 2026-09-26" below. It does not
replace PLAN.md's bars or rulings; it replaces the work order and the process
around each cell. ASCII only.

## Operator decisions, 2026-09-26 (question tool, dos-review session)

1. Gates S8 / S16 / S32 come before any release packaging.
2. 32-bit stays a 486 gate (S32 at the same bar as S8/S16).
3. WaveBlaster must pass the full LAB-WB 24 bar at every depth, as well as OPL3.
4. Rig time: operator 2026-09-26: keep asking each round (no standing window).
   Every power-on still needs the operator's question-tool approval, relayed by
   the coordinator.

## What the review found (why this plan exists)

- 16 rounds, ~19 h of target time, 09-24..09-26: no sound-on gate claimed.
- S16 has been within 0.07 of the floor since round F (09-24) and has not
  been re-run. 24 patches landed on main after that build, including the
  ones with the largest measured 486 gains (SDL 0240 inputs -1.55 ms/tick,
  ags 0315 logic -0.69 ms/tick, ags 0215/0216 decode, ags 0233 +1.67
  stable at 32-bit, SDL 0250-0256 late MIDI writes 504 -> 0). No gate
  fixture has been measured with sound on against the current engine.
- 270 doc-only + 180 results-only commits against 75 patch commits this
  week; PLAN.md 6.2k lines, PLAN-LOG.md 26.5k. Cells were cut from every
  round (TAIL/SCRIPTH eight rounds running). Four lab branches 70-215
  commits ahead of main; the WaveBlaster series is unlanded.
- STATUS.md's table stops at 09-22, README's status is from 09-22 and
  its build section from 09-10, the hub tracker from 09-17.

## The bar (unchanged) and the claim procedure (lighter, same bar)

Bar per depth, sound ON, Mach64, fixed timestep, 512x384 centred 1x
(S32: 640x480x32 1:1): both tick figures 39.2-40.8, fps_p50 >= 40,
completeness >= 95%, camera witness clean, x2; audio by the counters
(pcm_irqs exact, overwrites 0, late_writes 0, silent_irqs 0 outside room
loads); one 640x480 capture listen per depth. WB arm: LAB-WB 24 A/B/D.

Claim procedure from round Q on:
- A gate cell is pre-registered in at most 15 lines in its results
  directory README (fixture, binary sha12, prediction, void rule). No
  scorer script unless the metric is new. No PLAN.md section per cell.
- The result is one row in STATUS.md's table, committed with the raw
  results. A claim adds one paragraph under "Gates" in PLAN.md.
- A failed gate cell is not re-run until a lab fix has a DOSBox-X ratchet
  pass and a stated 486 prediction. Diagnostic cells cost rig time only
  when they decide a lab slice's direction; otherwise they run on DOSBox-X.

## Position per gate and the specific reason each is open

| Gate | Best sound-on figure (build) | Why it is open | First move |
|---|---|---|---|
| S16 (5 Days room 3) | whole-run 39.14/39.13, steady 39.98/39.95 (round F, SDL 0213 build, 09-24) | 0.06 under the floor; unmeasured since | re-measure x2 on current main |
| S8 (Trilby room 35) | 38.04/38.24 (rounds D/F, pre-CAP3 builds); later cells changed the fixture protocol and are not comparable | end-of-dialogue stall 1.1-1.7 s, a ~254 ms script tick (unnamed), late writes now 0 on the landed series | re-baseline x2 on current main at the ORIGINAL S8H protocol; name the 254 ms tick with ags 0316 |
| S32 (AGS Quest forced-32) | stable 36.25 sound on (round F, old build); 38.93 sound off (round J, C3) | skips 64/5000 from heavy present frames; sound-on cost unmeasured on current main | re-measure x2 sound on on current main |
| WB arm, all depths | WBLC2 PASS n=1 on the 5 Days INTRO (a cutscene), steady 33.9 there | the series is unlanded; the RTC pump's in-play CPU cost on a gate fixture is unmeasured at any depth | WBLR lands the series; then S16 WB x2 in play |

## Levers, ranked by expected gain per rig minute

1. Measure the current engine at every gate fixture (three rounds, no code).
   Expected: S16 in band; S8 +0.3..0.6 from the landed decode fix and
   0315/0240; S32 sound on near 38.9.
2. Release build switch: one compile-time switch that removes every
   DOS-PORT instrumentation path except RUNMANIFEST (tickstats, work
   vector, freeze instrument, presentverify, AUDIOPRB). 0315 alone bought
   0.69 ms/tick; the 0230 counters cost 0.77% of busy time. One ABBA on
   the S8 fixture decides whether gate cells run on the release flavour
   from then on. Lab cost ~1 day (worker).
3. S8 stalls (lab-s8): the dialogue stall and the 254 ms tick, named from
   0316's per-tick log on DOSBox-X, fixed in the script VM / asset path.
   Target: no tick over 100 ms in the S8H protocol on DOSBox-X at fixed
   cycles; predicted whole-run gain stated before the cell.
4. S32 heavy frames (lab-s32): skips 64 -> <= 25 per 5000 ticks with sound
   on. Mechanism is the lab's choice (present-window narrowing at the
   24-bpp pack, or splitting a heavy present across ticks); the DOSBox-X
   work vector must show the pixel reduction before rig time.
5. WB pump cost (lab-wb): if S16 WB x2 in play is under 39.2, the lever is
   the pump rate (2048 Hz -> 1024/512 Hz with running status) and the
   per-IRQ work; measured as ms/tick of ISR time on DOSBox-X first.

## Round plan (one 90-minute round per operator approval, <= 6 cells, nothing cut)

If a round runs short, the next round's first cell moves up. A cell that
does not fit waits; it is never squeezed by a shorter timeout.

| Round | Cells (all sound ON unless stated) | Decides |
|---|---|---|
| Q | WARMUP; S16 x2 on current main, OPL3; WBLR (WB series confirmation, land3); PACEI on/off (pacing default) | S16 OPL3 claim or the residual; WB series lands; 0256 default |
| R | WARMUP; S16 WB x2 in play (landed series); S8 x2 re-baseline, original S8H protocol, OPL3; RELEASE ABBA (instrumented vs release flavour, S8 fixture) x1 | WB in-play cost; S8 true gap; whether gate cells switch to the release flavour |
| S | WARMUP; S32 x2 sound on, OPL3; S32 WB x1; S8 stall fix ABBA x2 (lab-s8 slice 1) | S32 true gap; WB at 32-bit; the S8 stall fix's 486 effect |
| T | WARMUP; S8 x2 on the fix (claim attempt); S32 heavy-frame fix ABBA x2; S8 WB x1 | S8 claim; S32 fix effect; WB at 8-bit |
| U | WARMUP; S32 x2 on the fix (claim attempt); replications owed from Q-T | S32 claim |
| V-X | WB arms x2 per depth on the final binaries; 640x480 capture listen per depth (3 cells); anything falsified in Q-U | WB gate per depth; the listen record |

Honest estimate: three OPL3 gates in 5 rounds if the S8 and S32 fixes
land by rounds S and T; the WB gate at every depth adds 2-3 rounds, and
more if the pump's in-play cost is over ~0.5 ms/tick. About 10 calendar
days for everything, two weeks if WB needs a pump-rate change.

## Agents (five, one fewer than now) and their deliverables

- coordinator (existing sdldos session): verifies, relays, owns the hub.
- worker: the rig, landing, STATUS.md, PLAN.md; owns S16 and the release
  switch. Lands ags 0316 (opt-in, cost-free when off) before round R.
- lab-wb: WBLR package, then the in-play pump cost and per-depth arms.
- lab-s8 (the lab-mmd agent, reassigned; MMD's logic bar is met and
  recorded): the S8 stalls via 0316, in its existing worktree.
- lab-s32 (the lab-metric agent): S32 heavy frames. 0236/0238 land or are
  deleted in the first 48 h.
- lab-journeys: retires after PACEI is scored; its branch is archived.

Rules: a lab slice has one named deliverable and a 486 prediction; a
patch lands on main or is deleted within 48 h of its lab PASS; no lab
branch lives more than three days without a rebase onto main; each lab
keeps its record under docs/lab/<slice>.md capped at 300 lines, appended
only with results, never with narrative.

## Parked until the three gates are claimed (no rig time, no lab time)

Operator 2026-09-26 amendment: MMD in play (PLAY486, LAB-MMD 50.4) is NOT parked. It
stays in the queue at LOW priority: it fills spare room in a round after the gate
cells and never displaces them. P3, PROF486, TAIL and SCRIPTH stay parked as below.

MMD sound on (logic bar met: 24.63 ms/tick);
D35/DEC35 follow-ups; placement pins 0313/0314 (deleted); LOGRAM/CF
investigations (closed as bounded); Vibra16S lane; ViRGE and Cirrus;
tracker music (libxmp); the external write-up; TAIL and SCRIPTH as
standalone cells (SCRIPTH's question is answered by 0316's log on
DOSBox-X; TAIL's by the USB4VC counters already flashed).

Release packaging (release switch as a dist flavour, make dist with
CWSDPMI and licence texts, gallery entry, tag) starts the day after the
third gate is claimed. LICENSE-REVIEW.md is already complete.

## Process rules that cut the cost per cell

- PLAN.md is cut to: goal, bars, rulings, this round table, the gates
  paragraphs, "how to re-enter". Target under 400 lines. Everything else
  moves to PLAN-LOG.md, which is then frozen (append nothing).
- Every round's result is one commit: raw results + STATUS.md rows +
  at most 10 lines in PLAN.md. No separate staging-record commits; the
  staging list lives in the round's driver script.
- The nightly ratchet is the only DOSBox-X gate anyone runs before a
  round. A lab does not re-run the alias gate by hand.
- Hub skill edits are batched once a week into one commit and one
  plugin version bump.
- Diagnostic retirement: the 20 TEMPORARY DIAGNOSTIC patches get a
  keep/switch/remove decision in one worker pass when the release switch
  lands; at least half are removed.

## Reporting cadence (so "what do we have" is answerable in a minute)

- STATUS.md's figure table gains a row for every gate cell, in the
  result commit. It is the single source; README's Status quotes it.
- The hub's ports.yaml entry, COMPATIBILITY.md row, the vault log
  (plog -c milestone) and the kanban next line change at every gate
  claim and at every landed player-facing series.
- Every Friday: a 20-line digest in PLAN.md's "Position by depth" table,
  nothing else.

## Housekeeping this week (worker, between rounds)

- Pull the .sdl-dos-ports subtree forward (20 hub commits behind); move
  the HARDWARE.md row that only exists in the subtree copy into the hub.
- Land or delete: ags 0316, lab/wb series, lab/metric 0236/0238.
- Archive lab/journeys and wip/9b2; delete the tpit, d35f, wip9b2 and
  nightly-duplicate worktrees (about 6 GB); prune raw captures older
  than seven days from tests/harness/results (2.5 GB), keeping manifests.
- Rewrite README's Status and Build sections from STATUS.md.
