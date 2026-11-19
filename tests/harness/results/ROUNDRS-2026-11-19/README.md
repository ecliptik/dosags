# Round RS -- pre-registration (for sdlports' review; no data; no power-on asked)

Written 2026-11-18 (UTC 22:xx) by the lead. The operator lifted the hold ("Lift the hold: queue the 486 round", via
sdlports); that is NOT a power-on approval -- the power-on question goes to the operator separately, after sdlports'
review and their check of vcctrl's video and camera state. The round date D = 2026-11-19 is a placeholder: the driver
refuses any other UTC day, and a "re-date, before any data" commit moves every dir and README to the actual day.

## 1. What runs, in what order, and what decides what
| order | tag | binary (sha256, manifest stamp) | play line | read by | decides |
|---|---|---|---|---|---|
| 1 | WARMUPRS | l308.exe (425c1609..., bc9c3704a839) | MMD warm-up, 1,000 ticks | BLASTER witness, capture state | rig health only; STOP if BLASTER != "A220 I7 D3 P330 T3" or capture absent |
| 2 | RSCALQ | rs0383.exe | DRIVE 6 calq, 13 presses | drive6-gate.sh --recheck against RJCAL | the DRIVE 6 values; on any miss RSCAL (full cal) runs in-round |
| 2b | RSCAL | rs0383.exe | DRIVE 6 cal | drive6-gate.sh --no-recentre | as above; no PASS -> no play cell this power-on |
| 3, 4 | RSA1, RSA2 | **rs0383.exe = the ags 0383 release** (c68241073cb0dbcc6f0870c22ba31a0d904dd2261e72a44fbb7ba75f6cfb7f43, 8,673,058 B; stamp f2e183845d2f; RM0383-2026-11-17) | round RR's MS3 line verbatim (DRIVE 6 ms, 114 presses, exit 12440, AGSSAVE.007 f486d0e9..., 512x384 cfg ON, --no-fine-timing), NO env switch (main's behaviour) | rs-read.py cell A; `rs-read.py verdict` | **the term 0383-CONFIRMS-RR** (section 2) |
| 5, 6 | RSI1, RSI2 | **rsowl.exe = the 0383 instrumented + apply-owedlog-rig.py** (a3320300a6f671bf7787aea4ee67ed10f28e5a5423385d02e90dcd4f461ed2d1, 8,910,102 B; stamp from the lab check, section 6) | round RL's RLTA line (fine timing on, DOSAGS_TICKLOG=12500, DOS_PORT_LOG=1, the same save, cfg and presses) + DOSAGS_LAB_OWEDLOG=5430, --collect TICKS.BIN --collect OWED.BIN | rs-read.py cell I; rs-owed.py cell | nothing: click-tick lengths and per-call debt, information for the pacer model (lab-rb PREREG-PACE50 section 4 + FIX-UP D); never an A/B, no displayed-% claim |
| 7 | RSA3 | rs0383.exe | as RSA1 | as RSA1 | enters the term only if valid; dropped first on time |
- rsowl.exe: built in the dosags-ring tree (main's patch series to 0383, vendor tree clean); a plain instrumented build in
  the same run reproduced e5c05cc0... (RM0383's instrumented sha) byte for byte first, then the overlay was applied and the
  exe built. The overlay is tests/harness/apply-owedlog-rig.py (committed with this): lab-rb apply-owedlog.py
  (PREREG-OWEDLOG, accepted) without its PACE50 dependence, records packed to 24 bytes, buffer 8,192, written at exit to
  OWED.BIN. Unset DOSAGS_LAB_OWEDLOG = no log (one getenv). Never a patch; never in a release.
- Staged from build/ws/roundRS (expected.txt: rs0383.exe, rsowl.exe, l308.exe, AGSSAVE.007); a mismatch stops the round
  before power-on; a manifest stamp other than the recorded one is STAMP-VOID; the driver refuses to start without a
  12-hex stamp recorded for both rs0383.exe and rsowl.exe.

## 2. The term (rs-read.py's docstring is the rule) and the predicted outcome
- A cell VALID: stamp f2e183845d2f; "DOS-PORT routestamp allocs= peak_bytes=" with allocs >= 1 and peak_bytes = 192000;
  exit_code=0 and ENGINE HAS SHUTDOWN; underruns = overwrites = 0; pairing PAIR-OK or PAIR-OK-114LATE (114EDGE expired).
- **0383-CONFIRMS-RR** (registered: RSA1 + RSA2; RSA3 joins if valid), against round RR's F arm -- the code 0383 kept byte for
  byte (RM0383 section 1; identity re-run IDENTICAL on 12 lab cells): RR F 359 / 324 / 409 skips, mean 364.0, range 85.
  - CONSISTENT: >= 2 valid A cells, every one within 239..494 (RR F's range widened by its own spread 85), and their mean
    within 279..449 (364 +- 85).
  - INCONSISTENT: >= 2 valid A cells and either test fails. NOT READ: fewer than 2.
  - What follows: CONSISTENT -> recorded: 0383 on main is what round RR measured (the default ruling's binary is
    confirmed on the 486). INCONSISTENT -> to sdlports: a change between 0382-F and 0383 the lab did not see, or the rig.
  - Information: the MS3 proof bar (a registered pair, both >= 99.0%): expected "no" (RR F 94.16-95.37%).
- **Predicted outcome:** skips 324-409 per cell (RR F), displayed about 94-95%; 114 journeys, PAIR-OK (round RR's finding:
  the levers do not move the run's end -- loop_ms within 0.09 s -- so press 114's margin stays near RR F's -1.08..-1.96 s).
- **The reader under the predicted outcome** (simulated before any data, scratch copies of RR's F cells re-stamped
  f2e183845d2f with the routestamp line): RRF1 / RRF2 / RRF3 as A cells read VALID, PAIR-OK, and CONSISTENT (mean 364.0);
  one copy edited to 560 skips reads INCONSISTENT; an O cell (no routestamp line) reads VOID (search witness); an A cell
  read as I without the I stamp reads VOID.
- **The pacer's microsecond sensitivity, when reading pairs** (lab-rb RESULT-OWEDLOG: microseconds per call move 2 / 21 /
  138 of 1,549 drawn flags near 25 ms ticks; round RR's same-binary range 85): no difference under 85 skips -- between two A
  cells, or between an A cell and RR -- is read as a difference. The term's bands are built from that 85.

## 3. The I cells (information)
- VALID for the per-call read: rs-owed.py's rule (OWED.BIN header and the RUNMANIFEST labowed line agree; the loop counter
  increasing; every record's drawn tick drawn in TICKS.BIN; the catch-up sum equals TICKS.BIN's skipped ticks over the
  logged span -- the engine's two logs agree with each other). Stamp, clean exit and audio as A (rs-read.py cell I).
- Read: click-tick lengths by room (the click tick and the two after; p10 / median / p90; how many over 50 / 75 / 100 ms)
  against the model's 52-73 ms, mapped to the release level two ways (offset -1.70 ms; scale x 0.937), both reported, with
  the log's own cost from the lab check as a correction band; the per-call debt (owed distribution, rebases by kind, waits,
  frame-time resets) and the grid offset (now - epoch mod 25 ms after the restore; the lab read 4.71 ms).
- **What the log's perturbation leaves readable, and what not.** The log adds per-call work and one clock read in each
  drawn tick's wait. Readable whatever it moves: the click ticks' own lengths (tens of ms against microseconds of log),
  the debt as the engine itself computed it (self-consistent by the catch-up check), the grid offset, the waits. Not
  readable: the I cells' skip counts as a release figure (another flavour, fine timing on, two logs), and any tick-for-tick
  comparison of drawn flags between RSI1 and RSI2 or with a release cell. **When ticks get shorter** -- the levers' click
  ticks, or ordinary room ticks near 25 ms -- the log's microseconds flip more drawn flags at the 25 ms boundary; the
  per-call records still describe what the engine did (the catch-up check holds per run), so the debt read survives; only
  cross-run flag equality and skip counts lose meaning, and they are not read. Click ticks under 50 ms simply lower the
  "> 50 ms" counts.
- **The buffer against the 486's calls.** One record per call from loop counter 5430 to the exit at 12440: at most 7,010
  calls (one drawn tick per call, the catch-up inside it). Expected about 5,500-5,800 (RLTA, the 0373 instrumented, skipped
  1,469 of 7,003; the levers cut about 200 on the release). Lab (DOSBox-X) calls over the same span: about 1,550 at
  B = 0-17 (RESULT-OWEDLOG: 1,552 / 1,520 / 1,333 records from 5430 to the exit at 7000). The buffer holds 8,192, so it cannot fill on
  this fixture; if it did, the rest is counted (dropped=), and the per-call read covers the logged prefix only and says so
  (not VOID). The records are written at exit, not during the run.
- Memory: the buffer is 196,608 bytes of static .bss. memory_min_free_kb for the I cells is printed apart from the A cells
  (RLTA, the 0373 instrumented: 137,984).

## 4. The watch list from round RR, and where each is read
| item | where it is read | what is expected |
|---|---|---|
| partial_waits | the board's resume.partial_waits, MSTATS-RELEASE minus MSTATS-TAKE, per cell (rs-read.py READ line), beside pkt_partial / pkt_timeout | +2 in every play cell (RR: +2 in every F cell, +1 in O; RESULT-SBRK: the fast search's fifth heap growth at click 1, now in every run); pkt_partial = pkt_timeout = 0 |
| press-3 timing | A cells: the persec second holding press 3's journey, beside presses 2 and 4 (READ line); I cells: click 3's own tick length from TICKS.BIN (rs-owed.py "press-3 watch") | RESULT-SBRK's estimate, roughly 25-40 ms of locked commit at click 3 (63 pages), once per run; RR's cells: 8 skips in the press-3 second in BOTH arms, so it did not show as skips there |
| memory_min_free_kb | RUNMANIFEST per cell (READ line); I cells apart | A: about 146,176 (RR F); the unexplained +128 KB against O is not re-tested (no O arm) -- stated |
| the pacer's microsecond sensitivity | the term's bands (section 2); rs-read.py prints it beside the verdict | no in-round difference under 85 skips is read |

## 5. The checks sdlports applies (the arithmetic)
- **need() against the cap.** CAP_MIN 120 = 7,200 s; budget after the warm-up = 7,200 - 630 (warm-up, as round RR's line)
  - 240 (the margin) = **6,330 s**. Blocks, each checked at its start against the time left:
  | block | needs (graded) | typical per cell (round RR / RL) |
  |---|---|---|
  | calibration | RSCALQ 1,520 (calq 760 + a full cal 760, counted up front) | 690 s (RR's calq) |
  | the registered pair | RSA1 1,520 / RSA2 760 | 672-690 s (RR's play cells) -> 750 |
  | the I block | RSI1 1,600 / RSI2 800 | 687 s (RLTA, TICKS.BIN 146 KB) + OWED.BIN (about 140 KB) -> 800 |
  | the third A cell | RSA3 760 | 750 |
  Largest needs per block: 1,520 + 1,520 + 1,600 + 760 = **5,400 s against 6,330: 930 s of slack**. Dropped first: RSA3,
  then the I block as a block; the registered pair is never dropped for them.
- **Expected mains on-time:** 75 s after relay-on + warm-up about 510 s + calq 690 + two A 1,380 + two I about 1,440 + RSA3
  685 = about **4,780 s, 80 min** (about **91 min** with an in-round full cal). The cap watchdog powers off at 120 min - 45 s;
  powerguard retries power-off after the driver ends; daemongap logs the daemon and the lock.
- **stdin.** Every vcctrl call in driveRS.sh (16), cellRS.sh's input-log call, powerguard.sh and daemongap.sh carries
  </dev/null; drive-walk6.sh's press loop already does (round RH's fix); the read loops (`while read` in drive-walk6.sh)
  feed from here-strings. The real wrapper itself sends /dev/null for every command but `type --secret` / `share put -`,
  which this round does not use. The mock (tests/harness/mock-vcctrl) never reads stdin -- the same behaviour.
- **Presses sent == planned, before the gate.** presscheck(): DRIVE-WALK.LOG's header "N presses" against its `click i ...
  ok=1` lines; a short cell is not gated or read as a play cell (PRESSES SHORT in SUMMARY.txt). RSCALQ 13, RSCAL the cal's
  count, every play cell 114.
- **The gate checks only what the cells use.** The calibration gate (drive6-gate.sh --recheck / --no-recentre) decides
  whether the play blocks run, because every play cell uses the DRIVE 6 values. The play gate (--play) and the pairing are
  printed for every play cell as information; what validates an A cell is rs-read.py's rule (the pairing), as in round RR.
- **The fixture and the reader under the predicted outcome:** section 2 (A) and section 3 (I; the lab check reads RSOWL's
  own cells with rs-owed.py before the round).

## 6. Before the round (lab, DOSBox-X; after sdlports' read of this, not before)
- **RSOWL's lab check** (the stamp, OWED.BIN parses, and FIX-UP D's "the log's own cost per tick from a lab pair with and
  without the log, same binary"): MS3 whole run, RA clicks, fine timing on, TICKLOG, RSOWL with DOSAGS_LAB_OWEDLOG=5430
  (on) and without (off), two each, serial, lane 398. Read: rs-owed.py cell (VALID; n, before, dropped) and rs-owed.py
  compare on / off (per-room ugo median difference = the per-tick cost band; drawn-flag differences reported, as
  RESULT-OWEDLOG found they move). The stamp is written to build/ws/roundRS/rsowl.STAMP from these cells.
- The re-date commit, ORDER-CONFIRMED, then the power-on question (sdlports to the operator).

## 7. Housekeeping
- **The Gateway is shared with psdoom (lock plan).** vcctrl's input lock is per cell (run-hw-<TAG>); between cells nobody
  holds it. So: (1) sdlports tells psdoom's owner the window (from the power-on question's OK to POWERGUARD-DONE); (2) the
  driver refuses to power on if the input lock is held by anyone or the target is already on; (3) daemongap.sh records the
  lock owner every 10 s and logs any owner other than run-hw-<RS tag> as FOREIGN LOCK; (4) after every cell the driver
  checks that log and a foreign owner TAINTS the cell and ends the round (power off). No psdoom session is live on this
  host now (ListAgents, 22:4xZ).
- **Witness frames:** tools/witness-ftp-check.sh (tesseract OCR of every staged WITNESS-send / -collect frame) must pass
  before any results commit; frames that fail are not committed.
- Not committed, as always: AGSSAVE files, audio, game data.
- The round's records go to tests/harness/results/<TAG>-<date>/ and ROUNDRS-<date>/ (the driver, the cell wrapper and
  the guards as run, expected.txt, the stamps, SUMMARY / VERDICT).

## 8. After sdlports' read (2026-11-18; accepted with three notes), and the RSOWL lab check
- **The lab check ran** (DOSBox-X, lane 398, serial, each started under load 1.0, all four under 1.5 at both ends, rc 0;
  rsowl-lab/CELLS.txt, rsowl-lab/RSOWL-LAB-OUT.txt):
  - **stamp 3cbe1d7e1239** in all four cells: written to build/ws/roundRS/rsowl.STAMP (and here);
  - the log-on cells: OWED.BIN 167,980 bytes = 28 + 24 x 6,998; n 6,998, before 0, dropped 0; **VALID by rs-owed.py's rule** in
    both (every record's drawn tick drawn in TICKS.BIN; catch-up sum 5 = TICKS.BIN's skipped ticks); memory_min_free_kb 164,336;
  - **the cost of the records** (on - off, same binary): ugo median -1 / -2 us per tick (p10 -9, p90 +1) over 6,989 ticks;
    drawn flags differ on 0 ticks in both pairs; off against off differs by 0 us.
    **sdlports' note 1:** the extra clock read in WaitForNextFrame (wait_us) runs on every wait even with the log unset,
    so the "off" arm carries it too. This band is the cost of the records, NOT of the whole overlay, and is not to be
    quoted as the overlay's cost. It does not touch the round's reads (the I cells are never compared with A).
  - **A limit of the lab check:** DOSAGS_LABCLICKS (the RA click script) is a lab-overlay feature, and RSOWL is plain 0383
    + the log, so these cells ran MS3 with NO clicks (0 click markers, room 1 only, 5 skips) -- the log and its file were
    exercised, the click path was not. On the 486 the clicks are DRIVE 6's real mouse. The click-tick read itself was
    exercised on round RL's RLTA TICKS.BIN (0373 instrumented, real 486 clicks): 114 click markers; room 1 click ticks
    117.1 / 125.8 / 155.4 ms (p10 / median / p90), room 2 64.1 / 67.9 / 70.8; the press-3 watch read clicks 2 / 3 / 4 =
    117.4 / 129.6 / 117.5 ms (ticks 6196 / 6284 / 6384).
- **sdlports' note 2:** an INCONSISTENT term goes to sdlports before anything else is read. No re-run and no extra A cell
  is added in-round to rescue the term (RSA3 runs only as pre-registered, and only enters if valid).
- **sdlports' note 3:** the psdoom window is named to the operator in the power-on question. ListAgents at
  2026-11-18T22:46:04Z lists no psdoom session; vcctrl's lock owner None at that time (ORDER-CONFIRMED).
- **The date:** D = 2026-11-19 is kept. At 22:46Z on 2026-11-18, the power-on question and an 80-90 minute round would
  cross 00:00Z, so the 19th is the expected launch day. If the start falls on another UTC day, the driver refuses and a
  re-date commit precedes any data.

## 9. Result (2026-11-19; raw to sdlports before this commit)
- **The power-on:** the operator answered "Power on now" to sdlports at about 22:48Z on 2026-11-18. That message reached
  this session at 02:17Z on the 19th, so the operator was asked again directly and answered "Power on now". Already the
  19th UTC: D matched, no re-date. vcctrl was pinged; lock unheld, capture present, no psdoom session.
- **The round:** relay-on 02:18:54, off 03:38:43 (1 h 20 min; cap 04:18:54). Order as registered: WARMUPRS, RSCALQ (PASS,
  0 px drift, so no RSCAL), RSA1, RSA2, RSI1, RSI2, RSA3. Every cell: run-hw exit=0, pre = post sha, stamp OK, presses
  sent = planned (13 / 114), PAIR-OK, recover=0. DAEMON-GAPS.txt never written (no daemon gap, no FOREIGN LOCK);
  daemon_start_t unchanged. Records: SUMMARY.txt, VERDICT.txt, POWERGUARD.txt here; each cell's READ.txt (and OWED-READ.txt).
- **The term: 0383-CONFIRMS-RR CONSISTENT.** A skips 380 / 463 / 379 (mean 407.3), every cell in 239..494, mean in
  279..449 (RR F 359 / 324 / 409, mean 364.0). Displayed 94.57% / 93.39% / 94.59% (mean 94.18%). The MS3 proof bar: no.
  0383 on main measures what round RR measured; the 43-skip difference in the means is under the 85-skip same-binary range
  and is not read.
- **The watch list:** partial_waits +2 in every A cell (as expected from RESULT-SBRK), +1 in both I cells (another binary:
  192 KB more .bss; not read further); pkt_partial = pkt_timeout = 0 everywhere. memory_min_free_kb 146,176 in every A
  cell (= RR F), 145,728 in the I cells. Press 2/3/4-second skips: A 9/3/3, 9/8/0, 9/6/0 -- press 3 is not singled out.
- **The I cells (information):** skips 1,719 / 1,722 (75.4%; fine timing and both logs on; never compared with A).
  OWED.BIN VALID in both (n 5,284 / 5,281, before 0, dropped 0). Click ticks (p10 / median / p90 ms):
  room 1 click 80.3 / 87.8 / 100.2 and 84.0 / 87.9 / 100.9; room 2 click 54.3 / 56.6 / 61.0 and 54.7 / 58.1 / 61.1;
  room 2 click+2 median 44.0 in both. Press-3 watch: clicks 2 / 3 / 4 = 85.3 / 88.1 / 80.1 and 84.1 / 88.1 / 80.2 ms.
  Per-call debt: owed 0 on 60-61% of calls, owed 1 on 21-23%, 2-5 on 4-5%, > 5 on 12-13 calls (= the clamp rebases, 13 / 12);
  no flag or ahead rebases; every drawn tick waited (median 0.03 ms); frame-time resets 484 / 491.
  Beside RLTA (0373 instrumented, round RL; another binary, information only): room 1 click median 125.8 -> 87.8 ms,
  room 2 67.9 -> 56.6 ms, press-3 watch 129.6 -> 88.1 ms.
- **The rig (vcctrl's board summary):** 0 losses (pkt_ok +3,516; 0 inhibit / timeout / partial / discarded / buf_full),
  no FLAG rows, every lock release unforced, 0 USB or uvcvideo events. 8 decode_errs, all launch blacks 20-23 s after a lock.
  The .117 ping was paused for the whole round (services). capture=STALE ("nolock") in every cell, the same as every round RR cell.
- **Witness frames:** 14 WITNESS-send / collect frames OCR'd (witness-ftp-check.sh on the staged set): no FTP session.
