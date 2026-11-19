# Round RL -- 2026-11-12: the MS3 baseline exists (4 of 4 cells valid, 90.68% displayed, SD 0.89); USB4VC 0.5.109 PASSES (4,297 events = 4,297 packets, 0 losses, 0 consolidation, every stall-spanning press at its own target); the PUMP_TIMEOUT discriminator is FALSIFIED (the SB pump's lock spin is not the hitch); the 486 freezes machine-wide ~0.66 s and ~1.5 s at the two known stalls; P9M1 bridge 99.11%

One power-on: relay-on 00:13:17Z, power OFF 01:53:51Z (driver exit 0; driver-started powerguard confirmed OFF 01:54:01Z, no
"fired DURING cell" line), cap 02:13:17Z not reached; vcctrld daemon_start_t unchanged (1794436694.32). Operator, directly
(question tool): "Power on now (Recommended)", after sdlports' review of 18d8bf85 + the pre-data amendment 3f6f86b2 (need at
RLCALQ 3080) and vcctrl's pre-check (all-clear 00:13Z, firmware [0,5,109], counters 0 since the flash; warm-up camera shot
00:14:22Z normal boot screen, no password). Every cell exited 0 with stamp OK (rlrel 942ad0260d36 / rlins 39abbc4b5c34, ags
0001-0373; = round RK's), pre = staged = post; BLASTER.TXT "A220 I7 D3 P330 T3"; witness lines as registered (guictrlmark
(default) mode=1). Every cell's BOARD-TAKE.json reads `fw_ver [0, 5, 109]` and its SUMMARY line `fw=OK` (FW_EXPECT 0.5.109).
`capture=STALE` on every cell is the usual one (the stick never locks MMD's mode; the camera is the play witness).

| Cell | what | result |
|---|---|---|
| WARMUPRL | warm-up; first keyboard traffic through 0.5.109 | exit 0; BLASTER ok; typing worked (8.4 min, longer than usual) |
| RLCALQ | short re-check against RJCAL | **GATE PASS**, drift 0 px on every point (DXL 60, DXA 190, DXB 289, y 120) |
| RLCAL | full cal, only on a calq miss | not run |
| RLTA | MS3 instrumented, PUMP_TIMEOUT default (100) | GATE PLAY-OK; witness "(100 ms cap"; 79.02% (1,469 skips) |
| RLTB | MS3 instrumented, PUMP_TIMEOUT=10 | GATE PLAY-OK; witness "(10 ms cap"; 79.38% (1,444 skips) |
| RLM1 | MS3 baseline | **GATE PLAY-OK**, 90.10% (693 of 7,003) |
| RLM2 | MS3 baseline | **GATE PLAY-OK**, 90.40% (672) |
| RLM3 | MS3 baseline | **GATE PLAY-OK**, 92.00% (560) |
| RLM4 | MS3 baseline | **GATE PLAY-OK**, 90.22% (685) |
| RLP1 | P9M1 bridge, DRIVE 5 | 99.11% (62 of 7,003); no partial, no mouse.dropped -> counts |

## The MS3 baseline (the campaign's measure)
RLM1..RLM4, release build, default config on ags 0373 (L2 on), DRIVE 6 ms with RLCALQ's values, every cell's 114 presses sent,
ok, walking, and landing in band (drive6-gate.sh --play: GATE PLAY-OK x4). Audio underruns 0 / overwrites 0 in every cell.

| | RLM1 | RLM2 | RLM3 | RLM4 | mean | SD |
|---|---|---|---|---|---|---|
| frames_skipped (of 7,003) | 693 | 672 | 560 | 685 | 652.5 | 62 |
| displayed | 90.10% | 90.40% | 92.00% | 90.22% | **90.68%** | 0.89 |

Information only, as registered: round RK's VOID cells read 90.4 / 91.6%, inside this range. No target is set by this round; the
operator sets MS3's target from this baseline. Each cell carries the two machine-wide freezes below (~0.66 s + ~1.5 s of wall
time in which the engine clock stood still), which the displayed figure does not see as skipped ticks.

## USB4VC 0.5.109: PASS (pre-registered)
- pkt_partial 0 and pkt_timeout 0 in every in-play window, and over the round (vcctrl): ev_in 4,297 = pkt_built 4,297 = pkt_ok
  4,297; pkt_inhibit, edge_merged, ev_discarded, ev_buf_full, superseded, abandon_budget all 0; zero mouse.dropped rows.
- ev_in == pkt_built in every cell (RLTA..RLM4 687 / 687 each, RLCALQ 81 / 81): no consolidation at all (0.5.108: 14 in RK).
- Every stall-spanning press landed at its own target, late: GATE PLAY-OK in all six MS3 cells. RLTA's presses after stall #2
  step through presses 92-94 (~0.5 s each) and are steady from 95, as vcctrl expected (lab-rb 51f5e511).
- Resumes 35, partial_waits 35; exact holds RLTA stall #2 1,533 ms and RLTB stall #2 1,535 ms (max_wait_ms is a high-water mark,
  so every other stall is bounded only by its poll: within one poll, or spanning one, <= 1,535 ms).
- Keyboard: every cell launched by typing; kb_inhibit_retry 36 (normal). host_fe 0.

## The PUMP_TIMEOUT discriminator: FALSIFIED (pre-registered terms; lab-rb 51f5e511, LAB-MOVE 10.15, read on copies)
Witnessed in each cell's SDL log: "SDL/0068 SDL_DOSAudioPump TryLock+timeout backstop active (100 ms cap" (RLTA) / "(10 ms cap"
(RLTB). The prediction was that RLTB's three known hitches shrink to 10-20 ms quanta; falsified if any stays >= 100 ms.

| hitch (room-2 entry +) | RLTA (100) | RLTB (10) |
|---|---|---|
| +818..865 | lc 8548 (+844), 154.8 ms | lc 8560 (+844), 95.0 ms |
| +1,720..1,747 | lc 9411 (+1,707), 138.1 ms | lc 9422 (+1,706), 138.1 ms |
| +3,506..3,564 | lc 11197 (+3,493), 167.8 ms | lc 11210 (+3,494), 223.5 ms |
| catchup_audio_poll max / wait_next_frame max | 30 / 218 ms | 30 / 219 ms |
| audio | underruns 0, overwrites 0 | underruns 0, overwrites 0 (prime_retries 3) |
| board hold at stall #2 | 1,533 ms | 1,535 ms |

Two of RLTB's three stay >= 100 ms, at RLTA's offsets: the SB pump's lock spin is not the hitch, and LAB-MOVE 10.10's best fit
is withdrawn. Audio held its hard bar in both arms. The 10 ms setting is not a fix and is not proposed.
Note: RLTA / RLTB ran with DOS_PORT_LOG=1 in both arms; its fsync'd log writes stall a present on the CF card ~220-245 ms about
6 times per cell (the "flushslow" lines; patch 0188/0189's record), so their displayed figures carry that cost and are not
comparable to RJMP / RKMP or to RLM1..RLM4.

## What the stalls are: the 486 freezes machine-wide (lab-rb 51f5e511 / c15bc2e6 / 8f37e76a / 6da4ed74 / 90d5612f, LAB-MOVE 10.15-10.19; information)
- Per press, the host's down time minus the game's click time (SDL log journeys) is constant to ~30 ms except for permanent
  steps: RLTA +660 ms at press 53 and +1,488 ms over presses 92-94; RLTB +670 / +1,499 ms; RKM1 +623 / 1,510, RKM2 +677 / 1,188,
  RKMP +645 / 1,211. Engine time stood still while wall time ran: IRQ0 (the timer the engine clock rests on) was not serviced
  for ~0.66 s and ~1.5 s. The kid's positions at the next clicks agree. Stall #2's freeze matches the board's 1,533 / 1,535 ms
  hold; the board holds only while a packet is in flight, so its stall #1 readings are shorter.
- The 100-200 ms hitch ticks are the part of each freeze the frozen clock caught. The P9M1 (DRIVE 5) cells show the same steps
  at the same offsets: ~0.3 s at room-2 entry +~830, ~0.66 s at +~1,730, ~1.4 s at +~3,540 ticks -- doubling in spacing and
  length.
- Bound to the room-2 stay: three cells that reload room 1 (RDMP, RJP1, REC2) show the first two and nothing >= 150 ms after the
  reload, the 1.4 s freeze included. Nothing is logged at the freeze points (no sound / music / file event, pcmcache 2 misses
  all run, no file-I/O phase). The drive is written all through play (AGS's stdout log fflush()es each line; SMARTDRV caches
  reads only), so a disk-idle power-management timer is out as far as these records go; no POWER.EXE in the boot config.
- Ruled out: the SB pump spin (this round); DJGPP's sbrk move-with-interrupts-off (it lives only behind _CRT0_FLAG_UNIX_SBRK,
  and our build uses the non-moving 0501h path); the lab shows no heap growth >= 32 KB in a room-2 stay.
- Open: CWSDPMI r7 (VCPI client of EMM386, default swap file c:\cwsdpmi.swp) paging, EMM386 / VCPI activity, or SMI. The
  records hold only DPMI 0500h's largest block (min ~138 MB on the 486, = free physical + swap), so free physical at the minimum
  is ~7-8 MB if the swap file is 128 MB. Next round's candidates (lab-verified, lab-rb c325382b, LAB-MOVE 10.20; not landed): a
  DOSAGS_MEMLOG=1 diagnostic logging every 0500h field once a second (cost not measurable), and a no-swap arm (`CWSDPMI -s-` in
  RUN.BAT, witnessed by DPMI flags 0x1 and swap 0). No BIOS / CMOS setup: the operator's standing rule.

## Bridge: P9M1 RLP1 99.11% (counts by the board-counter rule)
| Cell | displayed | room 1 + entry | room 2 | late | stall_ticks | audio | in-play partials / mouse.dropped | walk targets |
|---|---|---|---|---|---|---|---|---|
| RLP1 | 99.11% (62) | 40 | 7 | 7 | 3 | 0 / 0 | 0 / 0 | the 5 usual |

Inside the registered 98.6-99.3% (L2-on expectation 98.90-99.03%); RK's information-only RKP1 / RKP2 read 99.14 / 98.80%. GUI
clicks logged 14 for 30 presses (information; no longer a rule).

## Rig (vcctrl)
Capture stick: zero disconnects all round (steady since 22:51:08Z, ~3 h). Corrupt frames 5 unique, all black, at launches
(RLCALQ, RLM1, RLM4, RLP1) and once in the post-RLTB reboot gap. Locks clean, 9 acquired and released; every call ok; balance 0.
For later (vcctrl): a per-stall wait counter, giving an exact length for every resume.

Files: SUMMARY.txt, driveRL.sh / cellRL.sh / powerguard.sh / daemongap.sh / expected.txt / ORDER-CONFIRMED, POWERGUARD.txt,
WINDOWS.txt; each DRIVE 6 cell's GATE / PLAY-RESULT / FIRST-PRESS.json (RLCALQ's RECHECK-RESULT); RLTA / RLTB's TICKS.BIN and
<TAG>SDL.LOG; every cell's BOARD-TAKE.json / BOARD-RELEASE.json. Captures and saves stay local (AUDIO-SHA256.txt,
SAVE-SHA256.txt).
