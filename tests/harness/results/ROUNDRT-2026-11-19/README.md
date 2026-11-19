# Round RT -- pre-registration: the pacer A/B on MS3 (for sdlports' review; no data; nothing built; no power-on asked)

Written 2026-11-19 by the lead, after the operator's ruling (relayed by sdlports, ~03:5xZ): **at most 2.0% game time
lost per run** for a pacer A/B on the 486, replacing the 2026-11-09 limit of 0.2% (PLAN.md 110adf6f). The rule is lab-rb
PACER-SCOPING.md's candidate B: 0163's long-tick rule at a threshold T below 250 ms. sdlports reads this first. No
build, no lab cell and no power-on question until they reply. The round date D = 2026-11-19 is a placeholder; the
driver refuses any other UTC day, and a "re-date, before any data" commit moves every dir and README to the actual day.
MS3 target: 99% frames displayed. The proof bar is unchanged: a registered pair, both cells >= 99.0%.

## 0. At the top
- **Threshold: T = 45 ms, not 50** (section 2). Round RS logged the real click ticks on the 486 for the first time.
  At the release level, 2-7 of room 2's 98 click ticks sit UNDER 50 ms (min 46-48), and none under 45. At 50 the rule
  would sit on the edge of the room-2 click distribution; 45 clears it by about 6-8 ms (p10). The model's game-time
  price of 45 against 50 is +0.03-0.08 points.
- **The game-time measure needs the operator's reading of "lost per run" (section 3, question Q1).** Measured as the
  game's clock against the wall over the play window, the SHIPPED pacer already loses 2.33-2.42% per run on MS3 (round
  RS's A cells; the room loads). So a total reading of 2.0% would fail today's binary. This pre-registration reads the
  limit as the extra game time the rule loses beyond the shipped pacer in the same power-on (G), as the 0.2% it replaces
  was. The total is printed beside it.
- **Predicted (model on round RS's own 486 tick logs, mapped to the release level):** P skips 8-22 per run (99.7-99.9%
  displayed); G +0.65..+0.90%. The older pacer-bound model (T = 50) said 98.95% worst mean at +1.45 points. The fixture
  holds under the prediction (section 5); the reader keeps its denominator (section 6).

## 1. What runs, in what order, and what decides what
| order | tag | binary | play line | read by | decides |
|---|---|---|---|---|---|
| 1 | WARMUPRT | l308.exe (425c1609..., bc9c3704a839) | MMD warm-up, 1,000 ticks | BLASTER witness, capture state | rig health only; STOP as round RS |
| 2 | RTCALQ (+ RTCAL on a miss) | rs0383.exe | DRIVE 6 calq / cal | drive6-gate.sh, as round RS | the DRIVE 6 values; no PASS -> no play cell |
| 3 | RTA1 | **rs0383.exe = the ags 0383 release** (c68241073cb0..., stamp f2e183845d2f; the binary on main, rounds RS / RR) | round RR's MS3 line verbatim (DRIVE 6 ms, 114 presses, exit 12440, AGSSAVE.007, 512x384 cfg ON, --no-fine-timing), NO env switch | pa-read.py cell A | the A baseline for G; information against RS |
| 4, 5 | **RTP1, RTP2** (the registered pair) | **rtpace.exe = the same 0383 tree + tests/harness/apply-pace-rig.py, RELEASE flavour** (sha256 and stamp from the lab, section 7) | the same line + `--env DOSAGS_LAB_STALL_MS=45` | pa-read.py cell P | **the term PACE-MS3** (section 4) |
| 6 | RTA2 | rs0383.exe | as RTA1 | as RTA1 | the A baseline (ABBA: A P P A) |
| 7 | RTP3 | rtpace.exe | as RTP1 | as RTP1 | the time rule only (every valid P cell), never the bar; dropped first on time |
- **The switch** (tests/harness/apply-pace-rig.py, committed with this): lab-rb apply-pace50.py (PREREG-PACE50 + FIX-UP 2,
  accepted; RESULT-PACE50-LAB2 read it exact: "at 50 ms no forced stall made a skip"). It is cut down for a release build:
  - DOSAGS_LAB_STALL_MS=T raises 0163's flag when a top-level tick's own time (DosTickStallScope's self_us -- present in
    the release flavour; only its work vector is compiled out) is over T ms, and implies DOSAGS_STALL_RESYNC=1. The debt
    after such a tick is forgiven (the epoch rebased) instead of repaid.
  - The exit line "DOS-PORT labpace stall_ms= rebases= forgiven_ticks= max_forgiven_ticks= spins=".
  - DOSAGS_LAB_SPIN (forced long ticks) is kept for the lab cells only and is never set on the rig. It spins just
    after DosTickStallScope opens, because the release flavour has no per-tick-log scope.
  - BASESPIN is dropped.
  - Unset: two getenv calls at the first tick and a few compares per tick.
  - Dry-run on a copy of the 0383 tree: applies, a 98-line diff. Never a patch, never in a release.
- **As switched, the rule forgives any tick over 45 ms, not only the clicks:** the restore (about 2 s) and the room-2
  load (about 3.7 s) are forgiven whole, without the five catch-up ticks the shipped pacer runs first (PACER-SCOPING's
  NOTE). That is part of its figures (G included), not separate from them.
- Staged from build/ws/roundRT (expected.txt: rs0383.exe, rtpace.exe, l308.exe, AGSSAVE.007). A mismatch stops the
  round before power-on, and a manifest stamp other than the recorded one is STAMP-VOID. The driver refuses to start
  without a 12-hex stamp for both rs0383.exe and rtpace.exe.

## 2. The threshold: 45 ms (lab reasons, from round RS's 486 logs)
- **The rule's whole effect sits on one step:** the room-2 click tick. With the route-finder levers, every click tick
  is over 50 ms in the old model and most are under 75. So a threshold between those values decides whether about 98
  clicks per run are forgiven or repaid (PACER-SCOPING CORRECTION 2). That correction asked for a measured click tick;
  round RS's RSI1 / RSI2 give one.
- Round RS's click ticks (instrumented flavour; mapped to the release level by the model's two mappings, offset -1.70 ms
  and scale x 0.937):

  | room, tick | n | instrumented min / p10 / median | release level (offset / scale) p10 | over 45 / over 50 (release, both mappings, both cells) |
  |---|---|---|---|---|
  | room 1 click | 16 | 80.1 / 80.3-84.0 / 87.8-87.9 | 75-82 | 16 / 16 |
  | room 2 click | 98 | 49.4 / 54.3-54.7 / 56.6-58.1 | 50.9-53.0 | **98 / 91-96** |
  | room 2 click+2 | 98 | 17.9 / 18.1 / 44.0 | 16.4-17.1 | 0-2 / 0-1 |

- **At 50 ms, 2 to 7 room-2 clicks per run fall under the threshold**, and the room-2 click p10 (50.9 by the scale
  mapping) is within 1 ms of it. A release click tick a few ms faster than the mapping would put T = 50 back into the 75
  ms row (most clicks repaid, about 95.6%). **At 45 ms all 98 room-2 clicks are over it in both cells by both mappings
  (margin 6-8 ms at p10).** At most 2 of the "+2" ticks (about 42 ms at the release level) are also over it.
- The model's price (pa-model.py, PA-MODEL-OUT.txt: lab-rb pacesim.py over RSI1 / RSI2's TICKS.BIN at the release
  mappings). "lost" is the debt forgiven over the run, the restore included:

  | policy | skipped (4 runs: 2 cells x 2 mappings) | displayed | lost, ms per run | lost beyond the shipped pacer |
  |---|---|---|---|---|
  | shipped | 235-317 (the 486 release: 379-463) | 95.5-96.6% | 5,225-5,750 | -- |
  | forgive = 55 | 46-75 | 98.9-99.3% | 6,425-6,800 | +775-1,400 |
  | forgive = 50 | 15-26 | 99.6-99.8% | 6,650-6,975 | +1,100-1,550 |
  | **forgive = 45** | **8-22** | **99.7-99.9%** | **6,725-7,075** | **+1,175-1,600 = +0.65..+0.88% of 181 s** |
  | forgive = 40 | 0-4 | 99.9-100% | 6,475-6,925 | +1,050-1,300 (283-299 rebases: the +2 ticks too) |

- **Limits of the model:**
  - pacesim.py's repaying rows are "unverified mechanism" (lab-rb RESULT-PACESIM): it under-counts the shipped
    pacer's skips. Here 235-317 against the 486's 379-463, about x1.4.
  - The forgiving rows (T = 75, 50) reproduced the engine exactly (RESULT-PACE50-LAB2). P's residual skips are
    repayments of debts under 45 ms, so they may be under-counted by the same x1.4: 11-31. The 99% line is 70.
  - The instrumented ticks mapped to the release are a model too. The 486 release cells measure the real thing.
- **Why the price is small:** when the pacer forgives a click tick's debt, AGS's own frame schedule (WaitForNextFrame,
  which falls back only after 3 frames) still repays most of the overrun by not waiting on the next ticks, which are
  drawn. What is truly lost is the part the schedule cannot absorb.

## 3. The game-time measure (sdlports' point a), defined before any data
- **G (registered) = loop_ms(P cell) / mean loop_ms(the round's valid A cells) - 1.** loop_ms is the engine's own wall
  span of the game loop, first tick entry to last tick exit (RUNMANIFEST "DOS-PORT tick_rate_steady ... loop_ms="). Both
  arms run the same 7,003 ticks to the TAS exit at 12440, so G is the extra wall time the same game took: the game time
  the rule gave up beyond the shipped pacer. Round RS's A cells: loop_ms 181,297 / 181,166 / 181,122 (spread 175 ms =
  0.10%; RR F 181,180-181,270).
- **Gwin (cross-check) = Lwin(P) - mean Lwin(A)**, where Lwin = 1 - 25 ms x (k1 - k0) / (m1 - m0) over the persec rows
  (tick k, engine ms m), from the first row with tick >= 5520 to the last. The restore's settling is excluded.
  **G and Gwin must agree within 0.5 points in every valid P cell, else the time reading is HELD** and goes to sdlports.
  They differ by design only at the restore, which the rule forgives whole: about 5 ticks = 125 ms = 0.07%.
- **The clock both are read on** is the engine's uclock, the clock the pacer itself uses. It is bracketed by the host:
  ms3-pairing.py's LEVEL line is the offset of the host-timed presses against the engine's journeys. Since 0377 it reads
  within +-30 ms per step (RS: -18..+8 ms), so the engine's ms track the host's wall clock. Printed per cell.
- **The pass rule: every valid P cell's G <= 2.0%** (RTP3 included when it runs).
- **Printed beside it, information only:**
  - Lwin itself: the game's clock against the wall, room loads included. The shipped pacer reads 2.33-2.42% (RS A);
    predicted for P about 3.0-3.3%.
  - P's labpace forgiven_ticks x 25 ms: the engine's own count of what the rule dropped, restore and loads included.
- **Q1 (to sdlports, for the operator before the power-on question):** what does "<= 2.0% game time lost per run" mean?
  - This pre-registration reads it as **G, the extra over the shipped pacer**, measured against the same power-on's A
    cells: the same quantity the 0.2% limit measured ("extra game time per in-play run", 2026-11-09).
  - If the operator meant the total (Lwin), the shipped binary already fails it (2.33-2.42%), and P would read about
    3.0-3.3%: TIME-OVER whatever the bar.
  - The term is written for G. A total reading changes only the pass rule's input; the reader prints both.

## 4. The term PACE-MS3 (pa-read.py's docstring is the rule) and the predicted outcome
- VALID, both kinds:
  - round RS's A rule: the stamp; the routestamp witness (allocs >= 1, peak 192000); exit_code=0 and ENGINE HAS
    SHUTDOWN; underruns = overwrites = 0; PAIR-OK or PAIR-OK-114LATE;
  - plus ticks = 7003 on the tick_rate_steady line, and loop_ms present;
  - P also needs a labpace line with stall_ms=45 and spins=0. An A cell has no labpace line.
- **PACE-MS3:**
  - **MET:** RTP1 and RTP2 valid and both >= 99.0% displayed, at least one valid A cell, and every valid P cell's
    G <= 2.0%.
  - **BAR-NOT-MET:** as MET, but one or both registered cells under 99.0%.
  - **TIME-OVER:** at least one valid A cell, and any valid P cell's G > 2.0%, whatever the bar reads.
  - **HELD:** G and Gwin disagree by more than 0.5 points in any valid P cell.
  - **NOT READ:** RTP1 or RTP2 not valid, or no valid A cell.
  - The registered pair is RTP1 + RTP2 only. RTP3 can fail the time rule but never makes the bar (2026-11-09: other
    cells that clear 99% do not count).
- **What follows:**
  - MET -> the claim "MS3 >= 99% displayed with the 45 ms long-tick rule (0163 at 45 ms), game time lost +G% against
    the shipped pacer" goes to the operator as a NEW restated goal naming the setting (the 2026-11-09 wording). Nothing
    ships without their ruling: a shipped rule would be a patch through sdlports' review, with its own identity cells.
  - Every other outcome -> to sdlports, as read, with no rescue cells.
- **Information:** each valid A cell against round RS / RR's band (239..494 skips; outside goes to sdlports beside the
  term); per P cell the rebases, the forgiven ticks, the pairing WITNESS and LEVEL lines; the watch list from round RS
  (partial_waits +2 at press 1, memory_min_free_kb, the press-3 second).
- **Predicted outcome:**
  - A: 379-463 skips (RS), loop_ms 181.1-181.3 s, Lwin 2.3-2.4%.
  - P: 8-31 skips (99.6-99.9%), G +0.65..+0.88% (model on RS's logs; the older model: +1.45 at T = 50), Lwin 3.0-3.3%,
    rebases about 170-180 (114 clicks + the restore, the loads and a few others), PAIR-OK.
  - The term: MET. Where it could fail: residual repayment larger than even x1.4 (BAR-NOT-MET), or a forgiven-debt
    price the model misses (TIME-OVER only beyond +2.0%, more than twice the predicted price).

## 5. The fixture under the predicted outcome (sdlports' point c; round RN's lesson)
pa-fixture-sim.py (tests/harness; output FIXTURE-SIM-OUT.txt), on round RS's and RR's release A cells and RS's
instrumented tick logs:
- **Press 114 against the loop end.** The presses are host-timed and the exit is tick-timed. A rule that loses game time
  makes the same 7,003 ticks take LONGER, so the loop ends later and press 114 lands further inside it, the opposite of
  round RN:

  | stretch g | 0 | 1.0% | 1.5% | 2.0% (the limit) | 3.0% |
  |---|---|---|---|---|---|
  | press 114 - last persec ms, 6 release cells | -0.7..-1.7 s | -2.5..-3.5 s | -3.4..-4.4 s | -4.4..-5.4 s | -6.2..-7.2 s |

  So PAIR-OK with 114 journeys is expected, and PAIR-OK-114LATE cannot arise unless P ran FASTER than A.
- **The room change (the only one: every cell visits rooms 1 and 2 only).**
  - Press 17 is the first room-2 press. On the 486 it lands 1,814 / 1,840 ms after room 2's first tick (RSI1 / RSI2;
    the release is faster, so its margin is larger).
  - Between press 16 and room 2, the rule can delay the game by the overruns it forgives on that stretch: 69-98 ms (the
    ticks over T, release mappings, T = 45 or 50).
  - So press 17 keeps a margin of more than 1.7 s.
- **Room state at any other press.** Each press starts a new walk from where the last one left the character. What the
  rule changes in one 1.5 s press interval is at most one forgiven click overrun (about 30-60 ms of walking), and the
  next click retargets the walk. No press depends on the character's arrival. No other room or scripted state change
  happens in the run. A press cannot land in a different room state.
- **Pairing offsets** (host down_at minus the engine's journey ms) are wall against wall: the rule does not move them
  except through the click tick's own latency, which it leaves as it is. The LEVEL steps are unchanged.

## 6. The reader under the predicted outcome (sdlports' point d)
- **The denominator does not change:** displayed % = 1 - frames_skipped / ticks, and frames_skipped = loop counter -
  render counter.
  - A forgiven debt is NOT a skipped frame and NOT a tick: the catch-up ticks are simply not run then. The 7,003 ticks
    to the exit at 12440 all still run, later in wall time.
  - So both arms divide by the same 7,003 ticks, and what the rule gives up shows in G, not in the denominator.
  - pa-read.py checks ticks = 7003 per cell (VOID otherwise) and computes displayed from the cell's own ticks figure,
    not a constant.
- **Simulated before any data** (READER-SIM-OUT.txt; reader-sim-mk.py builds the inputs): edited copies of RS's A cells,
  with the stamp changed, a labpace line added, frames_skipped set, and loop_ms and the persec ms past 5520 stretched.
  Every case read as built:
  - MET (20 / 15 skips, G +0.74 / +0.94);
  - BAR-NOT-MET (one cell at 80 skips, 98.86%);
  - TIME-OVER (G +2.54; and an RTP3 at +2.43 with a MET pair);
  - the edge (70 skips = 99.00% passes; G +2.03 fails);
  - HELD (persec stretched apart from loop_ms: G +0.73 against Gwin +1.85);
  - VOID for a missing labpace line, stall_ms=50, ticks 6990, an A cell read as P, a P cell read as A;
  - NOT READ with no A cell.

## 7. Lab first (sdlports' point e; after sdlports' reply to this, not before)
- **Build:**
  - In the dosags-ring tree (main's 0383 series, vendor clean), first a plain release build that reproduces
    c68241073cb0... byte for byte.
  - Then apply-pace-rig.py, the release build (rtpace.exe), and the vendor restored. sha256, the overlay diff and the
    build log are recorded.
  - `ulimit -v 5000000`; one compile at a time.
- **Lab cells** (DOSBox-X, lane 398, serial; the MS3 restore, release flavour, --no-fine-timing, no clicks, exit tick
  7000). The release flavour has no per-tick log, so the checks use the exit lines:

  | cell | binary, env | registered check |
  |---|---|---|
  | LA | rs0383.exe | the reference |
  | L0 | rtpace.exe, nothing set | the same frames_skipped, catchup line and ticks as LA; labpace stall_ms=0 rebases=0 spins=0 |
  | L45 | rtpace.exe, STALL_MS=45 | labpace stall_ms=45, rebases >= 1 (the restore is over 45 ms), frames_skipped as LA |
  | L0S | rtpace.exe, the 12 spins of PACE50 (5600..6700; 40 / 60 / 80 / 120 ms x 3) | catch-up fires in this binary: frames_skipped >= 6 (precondition, as PACE50's null at B = 0, which read 11); each labspin's self_ms printed |
  | L45S | rtpace.exe, STALL_MS=45 + the same spins | every spin whose self_ms > 45 has flagged=1 and the rest 0; frames_skipped = 0 (as PACE50 T50 at B = 0); rebases = flagged spins + L45's |

  - L0S is the precondition: if it reads frames_skipped = 0, the spin checks are VOID and that is reported, not worked
    around.
  - The stamp for build/ws/roundRT/rtpace.STAMP comes from these cells.
  - pa-read.py cell runs on all five. They are not play cells, so they read valid=no for the pairing, but ticks,
    loop_ms and labpace parse; that is printed.
  - The result goes to sdlports before the re-date, ORDER-CONFIRMED and the power-on question.
- **need() against the cap** (round RS's arithmetic). CAP_MIN 120 = 7,200 s; budget after the warm-up = 7,200 - 630 -
  240 = **6,330 s**. Graded needs, each checked at its block's start:

  | block | needs |
  |---|---|
  | calibration | RTCALQ 1,520 (calq 760 + a full cal 760, counted up front) |
  | the A/B block, needed whole | RTA1 3,040 / RTP1 2,280 / RTP2 1,520 / RTA2 760 |
  | the third P cell | RTP3 760 |

  - Largest needs: 1,520 + 3,040 + 760 = **5,320 s against 6,330: 1,010 s of slack.** Dropped first: RTP3. The A/B
    block is never split.
  - P cells run up to 2% (about 3.6 s) longer than A: inside each cell's 750 s typical.
- **Expected mains-on time:** 75 s after relay-on + warm-up about 510 + calq 690 + five play cells about 3,450 = about
  **4,725 s, 79 min** (about 90 with an in-round full cal).
- **The guards and checks** are round RS's, unchanged but for the names:
  - driveRT.sh, cellRT.sh, powerguard.sh and daemongap.sh are generated from round RS's committed copies by
    gen-driveRT.py, which asserts every edit;
  - every vcctrl call carries </dev/null (17 in driveRT.sh);
  - presses sent == planned before any gate;
  - the lock watch for the Gateway shared with psdoom (a FOREIGN LOCK taints the cell and ends the round);
  - one power-on, ending at POWERGUARD-DONE or the cap.

## 8. Housekeeping
- The lab works on copies of round records only.
- tools/witness-ftp-check.sh must pass before any results commit.
- Never committed: AGSSAVE files, audio, game data.
- Records go to tests/harness/results/<TAG>-<date>/ and ROUNDRT-<date>/.
- To-do before the round (not done yet):
  - the cell READMEs per tag;
  - expected.txt and the stamps (after the lab);
  - ORDER-CONFIRMED with the psdoom check at the time.

## 9. Questions with this pre-registration
- **Q1 (operator, through sdlports):** "lost per run" = G, the extra over the shipped pacer (this pre-registration),
  or the total? (Section 3.)
- **Q2 (operator, through sdlports):** the 2026-11-09 "no forgiven slip over about 150 ms" limit is not in the relay.
  - The model's largest forgiven debt away from the loads is 250-325 ms under every policy, the shipped pacer included
    (PACER-SCOPING CORRECTION 1).
  - Under this rule, the restore (about 2 s) and the room-2 load (about 3.7 s) are forgiven whole.
  - Is that limit lifted with the new 2.0%? If it stands, this rule fails it, as every policy does.
- **Q3 (sdlports):** T = 45 in place of the scoped 50, for section 2's reasons. Or register 50 as scoped and accept the
  edge?
- **Q4 (sdlports):** DOSAGS_LAB_SPIN stays in the rig binary (unset on the rig), so the binary the lab checks is the
  binary the rig runs. Or should there be two builds?

## FIX-UP 1 (2026-11-19, after sdlports' review of 2b7b7b69; before any build or lab cell)
**The answers.**
- Q1 (operator, sdlports' question tool): **"Extra <= 2.0%"**. The limit is G, the extra over the shipped pacer against
  the same power-on's A cells, as registered. sdlports disclosed that their limit question had framed T = 50 as "1.84%
  per run", the model's TOTAL (shipped 0.38%); they told the operator so, and the operator chose the extra reading.
- Q2 (operator): **"Lifted"**. The 2026-11-09 "no forgiven slip over about 150 ms" limit does not apply to this A/B; G
  <= 2.0% is the only time limit. Added as information per P cell (below).
- Q3 (sdlports): T = 45 accepted, for section 2's reasons. Choosing T from round RS's data is prior data; the 486 P
  cells are the measurement.
- Q4 (sdlports): one binary, with the spin left in and unset on the rig. VALID's spins=0 is the witness.

**Change 1: L45's expected value, from the mechanism, and every L row re-checked under the predicted outcome.** This
section replaces section 7's L rows.
- The lab fixture's own long ticks: the round RS lab check's no-click MS3 cells (MS99-RSOWL-off-1/-2, the 0383 code,
  instrumented, exit 12440) have exactly two ticks over 30 ms in the whole run. One is the restore, 1,488 ms at loop
  tick 5436; the other is 31.8 ms at 5442. **So no natural lab tick other than the restore is over 45 ms.** The release
  flavour's ticks are shorter still.
- Those cells skip exactly 5 frames (ticks 5437-5441): the catch-up after the restore, clamped at five (catchup ticks=5
  events=1 clamped=1).
- PACE50's re-run, the same mechanism at B = 0 (no base spin):
  - the null (0163 at 250 on) forgave the restore: rebases 1, forgiven_ticks 58, and only the spins skipped (11);
  - T = 50 with the 12 spins: 0 skipped; rebases 10 (the restore + 9 spins over 50); forgiven 63 (58 + 5);
  - spin self times as the flag saw them: 47.3 / 67.4 / 87.3 / 127.4 ms, i.e. nominal + 7.3 ms in the instrumented
    flavour.

| cell | binary, env | registered expectation (from the mechanism) | what is reported beside it |
|---|---|---|---|
| LA | rs0383.exe | frames_skipped 5 (the restore's catch-up; catchup ticks=5 events=1 clamped=1); resyncs 0; no labpace line | the reference |
| L0 | rtpace.exe, nothing set | labpace stall_ms=0 rebases=0 max_forgiven_short_ticks=0 spins=0 (the registered check, sdlports' change 2) | frames_skipped and the catchup line against LA's, as INFORMATION (expected equal: 5); a difference goes to sdlports, not a STOP |
| L45 | rtpace.exe, STALL_MS=45 | **frames_skipped 0** (the restore forgiven whole, no other tick over 45 ms); catchup ticks=0; resyncs 1; labpace stall_ms=45 rebases=1 forgiven_ticks 58 +- 1 max_forgiven_ticks = forgiven_ticks max_forgiven_short_ticks=0 spins=0 | any second rebase = a natural lab tick over 45 ms, reported with its count |
| L0S | rtpace.exe, the 12 spins (5600..6700; 40 / 60 / 80 / 120 ms x 3), nothing else set | the shipped path in this binary: frames_skipped - LA's >= 6 (precondition; PACE50's null read 11 from the spins: 0 0 1 2 / 1 1 0 2 / 1 1 0 2), so frames_skipped about 16 (5 + 11); labpace rebases=0 | each labspin self_ms (expected nominal + about 5-7 ms) |
| L45S | rtpace.exe, STALL_MS=45 + the same spins | frames_skipped 0; resyncs and labpace rebases = 1 + the spins flagged; each labspin flagged = (self_ms > 45); max_forgiven_short_ticks <= 4 (a 120 ms spin's debt: about 4 ticks less the one-tick lead) | forgiven_ticks (58 + the spins'); which 40 ms spins were flagged |

- **The one place the outcome is not fixed in advance:** whether the 40 ms spins are flagged. In the release flavour the
  base tick may add less than the instrumented 7.3 ms, which would put a 40 ms spin's own time near 45. Either way the
  registered check is flagged = (self_ms > 45). An unflagged 40 ms spin leaves a debt under one tick, which the
  one-tick lead absorbs: PACE50's null skipped 0 after every 40 ms spin. So frames_skipped = 0 holds either way, and
  only the rebase count moves (10 or 13).
- L0S is the precondition. If frames_skipped - LA's < 6, the spin checks (L0S, L45S) are VOID and that is reported, not
  worked around. LA, L0 and L45 are read anyway.
- pa-read.py cell runs on all five. They are not play cells: no clicks, so no route search, no routestamp allocs and no
  pairing, and ticks != 7003 at exit 7000. They read valid=no for those reasons by design; the labpace fields, loop_ms
  and frames_skipped parse, and that is what is printed.

**Change 2:** L0's match with LA is information, not a STOP (in the table above). No rig cell runs rtpace.exe unset: the
A arm is rs0383.exe itself.

**Change 3: pa-read.py's precedence** when several outcomes hold: **HELD, then NOT READ, then TIME-OVER, then MET /
BAR-NOT-MET** (docstring). Two reader-sim cases were added (READER-SIM-OUT.txt):
- a P cell with G +2.43% AND Gwin +4.58% reads HELD, not TIME-OVER;
- HELD with RTP2 missing reads HELD, not NOT READ.

**Overlay change, for the Q2 information** (apply-pace-rig.py; pace-rig-overlay.diff, the dry-run on a copy of the
0383 tree: applies, 109 lines). The labpace line's max_forgiven_ticks cannot separate the restore and the room-2 load
from the clicks: on MS3 it will be the room-2 load, about 148 ticks. So one field is added:
- **max_forgiven_short_ticks** = the largest debt forgiven by a rebase whose flagging ticks were all at or under 250 ms;
- a flag set by any top-level tick over 250 ms (0163's own stall threshold) and cleared with 0163's flag;
- what it excludes: the restore, the room loads, and any other tick over 250 ms. On the 486's A cells that is one more
  tick, 281 ms at about loop tick 6050, near press 3.
- pa-read.py prints both slips per P cell (x 25 ms), requires the field in a P cell's labpace line, and VOIDs the
  pre-fix-up line format (reader-sim case RTP4).
- Expected on the rig: largest forgiven about 3.7 s (the room-2 load); largest outside the long ticks about 25-75 ms (a
  room-1 click's overrun of about 60 ms, 1-3 ticks after the one-tick lead).

Because this changes the overlay, it goes to sdlports before the build, and the build waits for their reply.

## FIX-UP 2 (2026-11-19, sdlports' read of FIX-UP 1; before the build)
sdlports accepted FIX-UP 1's L rows, L0's information status, the precedence, the reader-sim cases and PLAN.md's record of
Q1 / Q2. The overlay is accepted with one change to the new field.
- **The change:** the "long" mark (lab_pace_prev_long) is now set right beside 0163's own `dos_tick_prev_was_stall =
  true` (patch 0163's line inside `if (self_us > DOS_TICK_STALL_THRESHOLD_US)`), with the same condition and no depth
  check.
  - FIX-UP 1 set it only at dos_tick_depth == 0. A NESTED tick over 250 ms raises 0163's flag, and the implied resync
    forgives it, so that rebase would have counted as "short".
  - "Short" now means every rebase that 0163's own flag did not raise, as stated.
  - The 45 ms flag stays at depth 0, as registered (PACE50's rule).
  - Regenerated pace-rig-overlay.diff (dry-run on a copy of the 0383 tree: applies, 115 lines).
- **Note, no change:** IsGamePaused()'s early return in dos_run_tick_fixed skips the clear, so both marks carry over a
  pause. MS3 does not pause.
- **Lab expectations added, the test that the field separates the two:**
  - L45: max_forgiven_short_ticks = 0. The restore is the only rebase, and it is over 250 ms.
  - L45S: max_forgiven_short_ticks = the largest flagged spin's debt in ticks, which equals max_forgiven_ticks among the
    spin rebases. The restore's 58 stays out of it.
- sdlports reads FIX-UP 2 with the lab result; the build goes ahead now (their word). Still no re-date,
  ORDER-CONFIRMED, power-on question or push.

## The lab check: RESULT (2026-11-19; DOSBox-X, lane 398, serial; rtpace-lab/)
- **Build** (rtpace-lab/build-rtpace.sh, in dosags-ring, the vendor tree clean before and after):
  - the plain release reproduced **c68241073cb0dbcc6f0870c22ba31a0d904dd2261e72a44fbb7ba75f6cfb7f43** byte for byte;
  - then apply-pace-rig.py (FIX-UP 2; the vendor diff equals pace-rig-overlay.diff) and the release build:
    **rtpace.exe = 57d33a6ef957ce79cdbc4377d1359fd9edd1a8a1b4abc4b6f408d24513b7c067, 8,677,257 B (+4,199 B), stamp
    57357c4a0c72** (build/ws/roundRT/rtpace.STAMP and here);
  - no warning in the overlay's code; the rebuild's other warnings are the vendor tree's own.
- **The reader** (tests/harness/rt-lab-read.py) was committed (0cdf5ba3) while the cells ran, before any was read.
  Output: rtpace-lab/RT-LAB-OUT.txt; the exit lines: rtpace-lab/EXIT-LINES.txt; the cells: rtpace-lab/CELLS.txt.
- **15 of 15 registered checks PASS.**
  - LA (rs0383.exe): 5 skipped (the restore's catch-up, catchup 5 / 1 / 1), resyncs 0, no labpace line.
  - L0 (rtpace.exe, unset): labpace 0 / 0 / short 0 / spins 0. Information: frames_skipped 5 and the catchup line
    EQUAL to LA's.
  - L45: **0 skipped**, catchup 0, resyncs 1; labpace stall_ms=45 rebases=1 forgiven 58, max 58, **short 0**: the
    restore was forgiven whole, and no natural lab tick other than the restore was over 45 ms.
  - L0S (spins, rule off), the precondition: 15 skipped, 10 over LA's 5 (required >= 6; PACE50's null read 11).
    Rebases 0. Spin self times 46 / 66 / 86 / 126 ms, nominal + 6 ms in the release flavour (the instrumented read
    + 7.3).
  - L45S: **0 skipped**; resyncs = rebases = 13 = 1 + 12 flagged. Every spin flagged == (self_ms > 45): all 12, the
    40 ms spins at 46 ms, 1 ms over. Forgiven 61; max 58 (the restore); **short 1** -- the field separates the
    restore from the spins, as FIX-UP 2 registered.
- **Load averages** are in CELL.txt; LA started at 2.73 / 1.90 / 1.09. These are deterministic exit-counter cells, not
  timing reads, and L0 equals LA exactly; the 1.5 rule is for reading cells and is reported, not applied.
- **Staged** in build/ws/roundRT (gitignored): rs0383.exe, rtpace.exe, l308.exe, AGSSAVE.007 (expected.txt, copied
  here), both stamps, driveRT.sh / cellRT.sh / powerguard.sh / daemongap.sh as committed. The per-cell READMEs
  (WARMUPRT, RTCALQ, RTCAL, RTA1, RTP1, RTP2, RTA2, RTP3) are written.
- Still owed before the round, in this order: sdlports' read of this result and of FIX-UP 2; the re-date if the launch
  day is not 2026-11-19; ORDER-CONFIRMED with the psdoom check at the time; the power-on question.

## NOTE after sdlports' read of the lab result (2026-11-19; information, no overlay change, no rebuild)
- sdlports accepted the lab check from raw: the overlay diff, EXIT-LINES.txt against all 15 checks, and sha256sum -c
  on build/ws/roundRT. LA at load 2.73 needs no re-run: exit counters, and L0 == LA exactly.
- **forgiven_ticks under-reads the wall time the rule gives up.** L45S - L45 loop_ms = 40,819 - 40,518 = 301 ms for the
  12 spins, but forgiven beyond the restore = 61 - 58 = 3 ticks = 75 ms: each rebase's debt is floored to whole ticks,
  and a sub-tick debt reads 0. So labpace forgiven_ticks x 25 and max_forgiven_short_ticks x 25 are **lower bounds in
  whole ticks**. pa-read.py now labels them so, and the report to the operator will too.
- G (loop_ms) stays the measure and is unaffected.
- The operator, via sdlports: "Push now" (origin/main = e8f2f10f) and, for the power-on, "Later today". HOLD: no
  re-date, no ORDER-CONFIRMED, no power-on question until sdlports relays that the operator is ready.

## 10. Result (2026-11-19; raw to sdlports before this commit; accepted from raw)
- **The power-on:** the operator said "Run it" to sdlports at 09:18Z, relayed to this session at once; sdlports' checks
  at 09:18Z: power off, lock owner none, capture present, build/ws/roundRT sha256sum -c 4 OK, tree clean at 1539c84c.
  D = 2026-11-19 matched, no re-date. ORDER-CONFIRMED at 09:18Z (ListAgents: no psdoom session; lock owner null;
  power off, 0 mW). The operator was then asked directly and answered "Power on now". vcctrl was pinged.
- **The round:** relay-on 09:19:21Z; relay-off 10:41:59Z (vcctrl's power.log, "done on=False"; POWERGUARD confirmed OFF
  at 10:42:08; the driver's own line reads 10:42:04). 1 h 23 min, cap 11:19:21. Order as registered: WARMUPRT, RTCALQ
  (GATE PASS, +0 px drift on all four, so no RTCAL), RTA1, RTP1, RTP2, RTA2, RTP3; nothing dropped. Every cell: run-hw
  exit=0, pre = post sha, stamp OK (A f2e183845d2f, P 57357c4a0c72), presses sent = planned (13 / 114), PAIR-OK,
  recover=0, ENGINE HAS SHUTDOWN, underruns = overwrites = 0, ticks = 7003. DAEMON-GAPS.txt never written (no daemon
  gap, no FOREIGN LOCK); daemon_start_t unchanged. Records: SUMMARY.txt, VERDICT.txt, POWERGUARD.txt here; each cell's
  READ.txt. sdlports re-ran pa-read.py --stamp-p 57357c4a0c72 --t-ms 45 verdict over the five cells: identical.
- **The term PACE-MS3: TIME-OVER** (G > 2.0% in RTP1, RTP2, RTP3). The bar is also not met: RTP1 97.04%, RTP2 97.04%.

  | cell | kind | skips | displayed | loop_ms | Lwin | G | Gwin | rebases | forgiven ticks (lower bound) |
  |---|---|---|---|---|---|---|---|---|---|
  | RTA1 | A | 327 | 95.33% | 181,308 | 2.430% | | | | |
  | RTP1 | P | 207 | 97.04% | 185,604 | 4.730% | +2.381% | +2.309% | 120 | 381 (>= 9,525 ms) |
  | RTP2 | P | 207 | 97.04% | 185,671 | 4.768% | +2.418% | +2.346% | 119 | 386 (>= 9,650 ms) |
  | RTA2 | A | 365 | 94.79% | 181,267 | 2.413% | | | | |
  | RTP3 | P | 212 | 96.97% | 185,586 | 4.734% | +2.371% | +2.313% | 119 | 378 (>= 9,450 ms) |

  Mean A loop_ms 181,288, mean A Lwin 2.422%. G and Gwin agree within 0.07 points in every P cell (not HELD). The A
  cells are inside RS / RR's 239..494 band. labpace in every P cell: stall_ms 45, max_forgiven_ticks 151 (>= 3,775 ms,
  the room-2 load), max_forgiven_short_ticks 3 (>= 75 ms), spins 0.
- **catchup (ticks / events / clamped / resyncs):** A 327/284/4/0 and 365/311/4/0; P 207/207/0/120, 207/207/0/119,
  212/212/0/119. stall_ticks 4 in every cell. Every P skip is a single-tick catch-up (events = ticks, clamped 0).
- **The model missed.** Predicted (section 4): P 8-31 skips (99.6-99.9% displayed), G +0.65..+0.88%. Measured: about
  207 skips (97.0%), G +2.37..+2.42%. About 116 rebases per run fall on ticks between 45 and 250 ms (max short 3 ticks),
  ticks the model did not count: it was built from RS's measured click ticks, not from every tick's self time.
- Information, a two-point slope only (A against P in this round, at T = 45 and the shipped pacer): about 4.3 s of
  loop time for about 140 fewer skips. It is not extrapolated to any other T.
- **The press-114 margins** (WITNESS, loop_end_est): A -2,807 / -1,353 ms; P -6,327 / -7,327 / -6,552 ms. LEVEL lines
  within -34..+21 ms. memory_min_free_kb 146,176 in every cell.
- **build_dirty=1 in the P cells** is expected: RTPACE is built from the overlay applied to an uncommitted vendor tree
  (the four lab RTPACE cells read the same); the stamp matches.
- **The rig (vcctrl's summary):** 0 losses (pkt_ok +3,516 = 81 + 5 x 687; buf_full / discarded / partial / timeout /
  inhibit 0); every lock owner the expected run-hw-<TAG>, every release unforced; 0 USB events on 1-2 and 3-2.
  decode_errs 42 -> 50, all flat-black at the WARMUPRT launch, the reboot after RTA1 and the RTP2 launch. No capture
  drop. capture=STALE ("nolock") in every cell, as in every round RR / RS cell.
- **Witness frames:** 14 WITNESS-send / collect frames OCR'd (witness-ftp-check.sh on the staged set): no FTP session.
- **What follows:** to sdlports, as read (pa-read.py). No further analysis, no new pre-registration until the operator
  picks a direction (sdlports is asking). No push: 1539c84c and this round's commits go to the operator with the results.
