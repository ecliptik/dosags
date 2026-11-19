# Round RM -- 2026-11-12: the CWSDPMI swap is NOT the 486's freeze (pre-registered prediction FALSIFIED: both no-swap arms keep both freezes at full size, 608 / 1,479 and 664 / 1,488 ms vs the default arms' 657 / 1,486 and 604 / 1,476); information: in all four MS3 cells each freeze coincides, to its ~1 s window, with the DPMI host committing a block of physical pages (192 / 512 / 992 pages, page-for-page the same sequence with and without swap), physical memory never short; P9M1 bridge RMP1 98.96%

One power-on: relay-on 07:35:15Z, power OFF 08:52:40Z (driver exit 0; driver-started powerguard confirmed OFF 08:52:49Z, no
"fired DURING cell" line), cap 09:35:15Z not reached; vcctrld daemon_start_t 1794467128.02 at round start and end (vcctrl's
user-approved redeploy at 07:05Z, before the round). Operator, directly (question tool): "Power on now, dark room", after
sdlports' review and approval of 43b2cfef + acc3bad9 + 234faa95 (pushed with 0376 by the operator's OK) and vcctrl's
pre-check (04:45Z, re-confirmed after the 07:05Z restart). The room was dark, but the camera read the monitor clearly (vcctrl's
warm-up shot; the operator confirmed): the screen witness stands as in earlier rounds (ORDER-CONFIRMED carries the correction).
Every cell exited 0 with stamp OK (rmrel 2725928f2e37 = main 4aff3001 release, ags 0001-0373 + 0376; l308 bc9c3704a839),
pre = staged = post; BLASTER.TXT "A220 I7 D3 P330 T3"; firmware 0.5.109 (fw=OK in every cell). `capture=STALE` (nolock) on
every MMD cell is the usual one: the stick never locks the 512x384 mode; the camera is the play witness.
**DIAGNOSTIC ONLY: no cell is scored against a target or counts toward the proof pair. MS3 target: not yet set (operator).**

| Cell | what | result |
|---|---|---|
| WARMUPRM | warm-up + read-only `DIR C:\ /A`, `MEM` | exit 0; BLASTER ok; listings below (8.6 min) |
| RMCALQ | short re-check against RJCAL | **GATE PASS**, drift 0 px on every point (DXL 60, DXA 190, DXB 289, y 120) |
| RMCAL | full cal, only on a calq miss | not run |
| RMA1 | MS3, arm A (default host), memlog | PLAY-OK; witness A OK (flags 0x5, swap 32,768); 90.10% (693) |
| RMB1 | MS3, arm B (`CWSDPMI -s-`), memlog | PLAY-OK; witness B OK (flags 0x1, swap 0 every row); 89.69% (722) |
| RMB2 | MS3, arm B (`CWSDPMI -s-`), memlog | PLAY-OK; witness B OK (flags 0x1, swap 0 every row); 89.65% (725) |
| RMA2 | MS3, arm A (default host), memlog | PLAY-OK; witness A OK (flags 0x5, swap 32,768); 90.50% (665) |
| RMP1 | P9M1 bridge, DRIVE 5, memlog off | 98.96% (73 of 7,003); no partial, no mouse.dropped -> counts |

Every ABBA cell: clean finish (RUNMANIFEST exit_code=0, "***** ENGINE HAS SHUTDOWN"), journeys / presses 114 / 114, memlog
173-174 samples, dropped 0; audio underruns 0 / overwrites 0 in every cell. No B arm ran out of memory (memory_min_free_kb 7,552).

## The verdict (pre-registered terms; lab-rb e87acc2e / 417c3045 / 0f844aa0 / 90a73e02, move-lab/rj/rm/, read on copies)
Level method: the change of the median per-press offset (DRIVE-WALK down_at minus RUNMANI's journey t_ms) between the press
stretches 21-33 | 36-52 | 54-90 | 95-114; +-30 ms.

| cell | arm | flags / swap pages | +830 | +1,730 | +3,540 | reading |
|---|---|---|---|---|---|---|
| RMA1 | A | 0x5 / 32,768 | +214 ms | +657 ms | +1,486 ms | valid A arm |
| RMB1 | B | 0x1 / 0 | +169 ms | **+608 ms** | **+1,479 ms** | keeps both: FALSIFIED |
| RMB2 | B | 0x1 / 0 | +213 ms | **+664 ms** | **+1,488 ms** | keeps both: FALSIFIED |
| RMA2 | A | 0x5 / 32,768 | +171 ms | +604 ms | +1,476 ms | valid A arm |

- Both A arms show both required steps (>= 500 / >= 1,000 ms), inside round RL's RLM1-4 (599-666 / 1,480-1,492 ms).
- Both B arms keep both (>= 500 AND >= 1,000 ms): **the CWSDPMI swap is not the freeze.** EMM386 / VCPI or SMI stay open, as
  registered. A and B are indistinguishable: +1,730 A 604-657 vs B 608-664; +3,540 A 1,476-1,486 vs B 1,479-1,488 ms.
- The moved-freeze guard fails in both B arms with the freezes unmoved: per-press changes >= 150 ms sit at the same presses
  as in A (34/35, 53, 91-94).
- The +830 step (169-214 ms) is information only, as registered.
- Displayed (information, not a target reading): A 90.10 / 90.50%, B 89.69 / 89.65%, beside RLM1-4's 90.68% (SD 0.89). B's
  ~0.6 point is inside a day's spread and is not read as an effect.

## Information outside the verdict: each freeze sits on a physical page commit
(lab-rb e87acc2e..90a73e02; memlog rows map to the step axis exactly -- memlog lc = the loop counter = persec's tick -- and come
every ~40 ticks, about 1 s, on the 486; the lab smoke's 1.8 s was agsquest at lab speed.)
- All four cells commit the identical sequence of physical pages (DPMI 0500h free pages) at the same game points, with and
  without a paging file: -128, -32 (room 1), -768 (the room-2 load), -192, -192, -192, -512, -992. Free physical starts at
  4,897 pages and ends at 1,889 (7.4 MB of 8,192 pages = 32 MB as CWSDPMI sees it): memory never runs short, so the
  pre-registered "free pages at the floor" naming does not apply.
- After room-2 entry the match is one-to-one in 4 / 4 cells: every commit window overlaps a step bracket and every step
  >= 150 ms has a commit (192 pages -> 146-243 ms; 512 -> 604-728 ms; 992 -> ~1,480 ms); odds of RMA1's alignment at random
  ~1e-5. Alignment holds to the ~1 s window and no finer: neither record orders commit and freeze inside it.
- The board's holds (vcctrl; lab-rb 8845c9ac holdmap.py / HOLDS-RM.txt) sit at the same lock offsets in all four MS3 cells,
  +42 / +91 / +109 / +131 / +177 s (spread <= 3 s), and map onto commits: +42 = the room-1 128-page commit, +91 = the second
  early 192, +109 = the +830 192, +131 = the 512, +177 = the 992. The room-1 commit holds the board in 4 / 4 cells while the
  guest loses <= ~50-70 ms there: a small freeze below the guest method's floor. The commits with no hold had no packet in
  flight, which says nothing.
- Candidates (hypotheses, not findings): the commit itself through the host chain (CWSDPMI as a VCPI client getting pages
  from EMM386, per page), or what the engine does with the new memory in that second. memlog counts committed pages only and
  cannot tell them apart. The lab's earlier "no heap growth >= 32 KB in a room-2 stay" disagrees with the 486's commits and is
  being reconciled first (MS3 in DOSBox-X with DOSAGS_MEMLOG=1, then the owning allocation). A no-EMM386 arm would change the
  target's CONFIG.SYS: the operator's call.

## Warm-up listings (information)
- `DIR C:\ /A`: no CWSDPMI.SWP at rest (the default host creates and removes it per run); 254,771,200 bytes free.
- `MEM`: 49,152K total; XMS 47,941K, 43,556K free; UMBs in use (Upper 187K); MS-DOS in the HMA. CWSDPMI reports 8,192
  physical pages (32 MB) to the engine.

## Bridge: P9M1 RMP1 98.96% (counts by the board-counter rule)
| Cell | displayed | room 1 + entry | room 2 | late | stall_ticks | audio | in-play partials / mouse.dropped |
|---|---|---|---|---|---|---|---|
| RMP1 | 98.96% (73) | 39 | 20 | 6 | 3 | 0 / 0 | 0 / 0 |

Inside the registered 98.6-99.3% (RLP1 99.11%). Binary is RL's + 0376 (memlog off here).

## USB4VC 0.5.109 and the rig (vcctrl)
- ev_in +2,923 = pkt_built = pkt_ok over the round (687 per MS3 cell, 81 RMCALQ, 94 RMP1); nothing summed; pkt_partial,
  pkt_timeout, pkt_inhibit, ev_buf_full, ev_discarded, edge_merged, superseded, abandon_budget, host_fe all 0; zero
  mouse.dropped rows. pkt_resumed / partial_waits +23 (35 -> 58); max_wait_ms stayed 1,535 (RL's), so every RM hold was
  shorter. The new daemon mouse.resumed event matched every board "VC MOUSE RESUME" line (23 resumes, 27 rows: straddles).
- Capture stick: zero disconnects, no USB kernel events; 2 corrupt frames, one flat-black pair at 08:11:13Z (the reboot before
  RMB1). Locks clean; 0 ok:false; 0 refusals.

Files: SUMMARY.txt, driveRM.sh / cellRM.sh / powerguard.sh / daemongap.sh / expected.txt / ORDER-CONFIRMED, POWERGUARD.txt,
WINDOWS.txt; each cell's RUNMANI.LOG (memlog rows), DRIVE-WALK.LOG, GATE / PLAY-RESULT / FIRST-PRESS.json (RMCALQ's
RECHECK-RESULT), BOARD-TAKE / BOARD-RELEASE.json, INPUT-LOG.jsonl; WARMUPRM's ROOTLIST.TXT / MEMLIST.TXT. Captures and saves
stay local (AUDIO-SHA256.txt, SAVE-SHA256.txt).
