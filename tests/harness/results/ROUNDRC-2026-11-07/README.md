# Round RC -- 2026-11-07: R3 (ags 0368, the default) WORKS on the 486 -- MMD in play 88.9% -> 98.3% displayed (ABBA); late stretch 80% -> 99.4%; every band met. Save trace: the restart save's excess is CF-card write stalls on new clusters

One power-on: relay-on 16:05:46Z, power OFF 17:44:40Z (driver exit 0; driver-started powerguard confirmed OFF 17:44:41Z), cap
18:00:46Z not reached; vcctrld daemon_start_t unchanged (1793979061.92). Operator, directly (question tool): "Power on after the
check (Recommended)", after sdlports' check of 9835c01c passed. Every cell exit 0, stamp OK, pre = staged = post; BLASTER.TXT "A220
I7 D3 P330 T3"; camera sheets show play in every MMD cell (kids walk, room 1 -> 2) and room 3 in RCS16. No recovery.
Binaries: RCREL = main 9e54b6d9 release 4c9f83b62c5c (sha256 7deb7ca9...), RCINS = instrumented aa334361a087 (1cb00ce1...), both
build_dirty=0 and byte-identical to the reviewed R3REL / R3INS (`cmp -l`: 0 differing bytes; the stamp hashes the build inputs).

| Cell | arm | displayed (1 - skipped/ticks) | late stretch 9500-end (renders/ticks) | steady | fps_p50 | guiclip_final (key fields) |
|---|---|---|---|---|---|---|
| RCA1 | R1 (=2) | 87.99% (841 of 7,003) | 79.6% | 39.89 | 34.18 | mode=2 skipped=10661 clipped=7805 latch_fullrestore=0 |
| RCB1 | R3 (default) | **98.43%** (110) | **99.5%** | 39.97 | 40.00 | mode=4 skipped=11756 boxed=8902 boxes=8925 fb_coarse=0 fb_whole=0 latch_fullrestore=0 |
| RCB2 | R3 (default) | **98.24%** (123) | **99.3%** | 39.96 | 40.00 | mode=4 skipped=13048 boxed=7575 boxes=7590 fb_coarse=0 fb_whole=0 latch_fullrestore=0 |
| RCA2 | R1 (=2) | 89.82% (713) | 80.9% | 39.87 | 37.15 | mode=2 skipped=11693 clipped=7157 latch_fullrestore=0 |
| RCMP | R3, instrumented | 90.55% (662; fine timing on) | 98.7% | 39.91 | 38.73 | mode=4 boxed=8067 fb_coarse=0 fb_whole=0 latch_fullrestore=0 |
| RCS16 | R3 (default) | 99.48% (26 of 4,999) | -- | 40.15 (whole 39.29) | 40.00 | mode=4 flagged=4555 skipped=0 boxed=0 (R3 does not engage) |

Raw guiclip_final lines are in each cell's RUNMANI.LOG. Late stretch = differences of the cumulative persec (tick, renders)
pairs over loop ticks >= 9500. span_stretch=0 and coarse_restores=0 in every cell: neither guard fired naturally on the 486.

## R3 ABBA (pre-registered, LAB-R3 section 3 verbatim): every band MET, no falsifier tripped
- (a) Late stretch, R3 cells 99.5% / 99.3%: band 93-100% (central 97) -- in; both >= 92%; each over its adjacent R1 arm by
  +19.9 (RCB1 vs RCA1 79.6) and +18.4 (RCB2 vs RCA2 80.9) points (>= +10 required).
- (b) Whole fixture, R3 cells 98.43% / 98.24%: band 94.0-98.5% (central 96.5) -- in, near the top; both >= 93%;
  mean(R3) - mean(R1) = 98.34 - 88.91 = **+9.43 points** (>= +4 required). R1 arms (87.99 / 89.82) sit inside CF's band (86-92).
- (c) RCMP, render per drawn tick over 9500-end (fixed f1prof grouping, drawn ticks 2,902 of 2,939): **median 2.66 ms** (band
  2.4-3.6, central 2.7) -- in; 4.16 ms below the R1 reference (CFMP: 6.82 ms over 1,921 drawn of 2,939; a different binary and
  day, as registered) (>= 2.5 required). Late-stretch drawn-tick ugo median 24.71 ms (CFMP 28.61).
- Campaign line (>= 99% x2): NOT met (98.43 / 98.24), as registered -- the remainder is room 1 (R2), the room-2 entry and clicks.
- RCMP information: script_vm 12.47 ms/tick (CF 12.18); rb_sprite_time per drawn frame 12,538.5 / 6,373 presents = 1.97 ms (CFMP
  3.96); room-2 entry at loop tick 8296 (CFMP 8020: the host clicks land differently run to run).
- RCS16 (the guard): gatebar S16 **MET** (39.29 / 40.15, fps_p50 40.00, 99.48%, audio clean, camera CLEAN); R3 did not engage
  (boxed 0), as registered; restart_savegame 465 ms, preloop 864.

## The save-trace pair (round SW1's SW1TA / SW1TB, run first here as amended)
| cell | lever | restart_savegame_ms | INT 21h | ms in INT 21h | the 40h writes (bytes: ms) |
|---|---|---|---|---|---|
| SW1TA | OFF (stream) | 463 | 117 | 316.7 | first data write 15,296 B: **224.1**; the other 15 writes 0.2-10.8 each; fseek total 283 (it carries the flushes) |
| SW1TB | ON (one write) | 718 | 11 | 564.3 | 16,384: **310.2**; 16,384: 6.3; 16,384: **226.0**; 10,386: 4.8 (one fwrite = 549 ms) |
Reading (information; the trace cells' timings were registered as not scored): a 16 KB write normally costs 5-11 ms on this
machine, but some writes take 224-310 ms. In SW1TB the two stalled writes are the ones that START a new 32 KB cluster (bytes 0 and
32,768); in SW1TA the first data write stalled and a later cluster-crossing write (14,640 B at ~24-39 KB) did not. So the restart
save is ~210-260 ms of base work plus 0, 1 or 2 stalls of ~220-310 ms -- the 210 / ~500 / ~720 ms tiers seen in rounds D8, CF, SU
and SW1 -- and the stalls sit in the card's handling of a write (consistent with the ~212 ms single-sector CF stall in PLAN-LOG),
not in the engine's call pattern. The DOS-level lever cannot remove them; lever 1 stays un-landed (sdlports 2026-11-07).
CHKDSK2 (after SW1TB) vs CHKDSK1 (round SW1): no errors either time; 7,880 free clusters (was 7,898), 6,873 files (was 6,860).

## Rig (vcctrl)
No USB event, no recovery, daemon unchanged. 5 corrupt capture frames (decode_errs 87 of 1,809,561), all at launches or collect
reboots: 17:15:53Z (RCA2 launch), 17:27:19 / 17:27:24Z (RCMP launch), 17:32:11 / 17:32:12Z (near RCMP's end, its collect reboot). jobs/: the last 16 file
jobs (the warm-up's send and pull had aged out of vcctrld's last 16).

Files: SUMMARY.txt, driveRC.sh / cellRC.sh / powerguard.sh / daemongap.sh / expected.txt / ORDER-CONFIRMED, POWERGUARD.txt, jobs/;
RCS16 GATEBAR.txt; RCMP F1PROF.txt / F1PROF-room1.txt / F1PROF-late.txt / TICKS.BIN; SW1TA / SW1TB SWTRACE.TXT; SW1TB CHKDSK2.TXT.
Captures and saves stay local (AUDIO-SHA256.txt, SAVE-SHA256.txt).
