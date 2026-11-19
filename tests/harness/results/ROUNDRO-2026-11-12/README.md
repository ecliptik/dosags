# Round RO -- results (2026-11-12): ags 0377 is the fix for the 486's room-2 freezes -- SUPPORTED

One power-on: relay-on 20:57:15Z, power OFF 22:27:28Z (driver exit 0; driver-started powerguard confirmed OFF 22:27:30Z;
vcctrl's power.log OFF 22:27:23Z, 90 min on). Every pre-registered cell ran; none dropped. Binary RNREL.EXE = round RN's
(main 987ddce1 release, stamp 93df50d751a8, sha256 ce8d275f...), stamp OK in every cell, staged sha = pre-stage = post-run.
vcctrld one process throughout (daemon_start_t 1794467128.02 at start and end). Operator's power-on OK asked directly in
this session (20:56Z); vcctrl pre-check passed (services: Home Assistant never switches the plug). Pre-registrations:
commit 50af4a4e (sdlports-approved, pushed before any data). DIAGNOSTIC ONLY: no cell is scored against a target or counts
toward the proof pair. MS3 target: not yet set (operator).

| Cell | What | Result |
|---|---|---|
| WARMUPRO | l308 MMD title, rig warm-up | run-hw exit 0, BLASTER "A220 I7 D3 P330 T3", capture present |
| ROCALQ | DRIVE 6 calq vs RJCAL | GATE PASS, drift +0 px on DXL / DXA / DXB / y (ROCAL not run); 98.57% (information) |
| ROF1 | MS3, arm F (0377 default), memlog | PAIR-OK 114 / 114; PLAY-OK; witness F OK; steps -2 / -1 / +13 ms |
| ROL1 | MS3, arm L (DOSAGS_RING_LEGACY=1), memlog | PAIR-OK 114 / 114; PLAY-OK; witness L OK; steps +223 / +609 / +1,488 ms |
| ROL2 | MS3, arm L, memlog | PAIR-OK 114 / 114; PLAY-OK; witness L OK; steps +170 / +655 / +1,482 ms |
| ROF2 | MS3, arm F, memlog | PAIR-OK-114LATE 113 / 114; PLAYREAD OK-114LATE; witness F OK; steps +1 / -6 / -4 ms |
| RODT | DPMITIM2 ballast test (information) | all 8 files valid; reading (a) SUPPORTED (c(6144) / c(0) = 8.84x A, 9.11x B) |
| ROP1 | P9M1 on RNREL, DRIVE 5 | 99.36% (45 of 7003), inside the registered 98.6-99.5% |

## The verdict (pre-registered terms, ROF1-2026-11-12/README.md): SUPPORTED

- Validity, every ABBA cell: arm witness as registered (F: legacy=0, compactions 39, moved_bytes 1,114,112, cap_max
  128,000; L: legacy=1, compactions 0, cap_max 4,037,632); env_block_sha equal within each arm and different between them
  (F eec4d5b41015, = RN's F; L 987d6065efbd); RUNMANIFEST exit_code 0 and "ENGINE HAS SHUTDOWN" in all four; memlog
  flags 0x5, 173 samples, dropped 0; pairing PAIR-OK or PAIR-OK-114LATE.
- Pairing (tests/harness/ms3-pairing.py, as committed; PAIRING-ALL.txt). Three cells paired 114 / 114. ROF2 is the case the
  rule was registered for: press 114 at game 198,839.0 ms, last persec ms 198,360, diff +479.0 ms (3a, strict: pass); loop-
  end estimate 198,509.4 ms, margin +329.6 ms (3b, strict: pass); presses 1-113 pair 1:1 (worst sustained shift -35 ms at
  press 12; outside the brackets +30 ms at press 44). ROF1's press 114 landed inside the run this time (diff -598.0 ms),
  so it paired normally. drive6-gate.sh --play: PLAY-OK in ROF1 / ROL1 / ROL2; ROF2 PLAY-VOID with the single failure
  "logged 113 walk targets for 114 presses" in a PAIR-OK-114LATE cell = PLAYREAD OK-114LATE (presses 1-113 in their bands).

| Cell | Arm | Pairing | +830 (33->36) | +1,730 (52->54) | +3,540 (90->95) | per-press change, presses 21-n | largest sustained shift |
|---|---|---|---|---|---|---|---|
| ROF1 | F | 114 / 114 | -2 ms | -1 ms | +13 ms | -42..+42 ms | +30 ms (press 106) |
| ROL1 | L | 114 / 114 | +223 ms | +609 ms | +1,488 ms | -57..+630 ms | +1,480 ms (press 93) |
| ROL2 | L | 114 / 114 | +170 ms | +655 ms | +1,482 ms | -113..+764 ms | +1,491 ms (press 93) |
| ROF2 | F | 113 / 114, late | +1 ms | -6 ms | -4 ms | -85..+57 ms | -35 ms (press 40) |

- F "gone" in both arms: (a) the +1,730 and +3,540 steps are < 150 ms (-1 / +13 and -6 / -4 ms, flat to the method's
  +-30 ms), and (b) the moved-freeze guard holds: no per-press change >= 150 ms and no sustained shift >= 150 ms anywhere in
  presses 21-114 (ROF1) / 21-113 (ROF2). The falsifier (either F arm keeping +1,730 >= 500 AND +3,540 >= 1,000 ms) is not met.
- L valid: both L arms keep both steps at full size (>= 500 / >= 1,000 ms: 609 / 1,488 and 655 / 1,482 ms), the per-press
  jumps at presses 34, 53 and 91-94, as all ten RL / RM / RN legacy cells did.
- Audio hard bar met: underruns 0 / overwrites 0 in both F arms (and both L arms); silent_irqs 0 in all four.
- So, by the letter: SUPPORTED. With 0377 the mixer's voice ring no longer reallocates during the room-2 stay, and the
  486's three room-2 freezes (~0.2 / ~0.6 / ~1.5 s of stopped clock) are gone, on the same binary and line where the legacy
  switch brings them back. Together with round RN's post-data reading (same split), four F cells and four L cells now read
  the same way. The removals owed follow: ags 0376 (memlog, TEMPORARY) and 0377's DOSAGS_RING_LEGACY switch.

## Registered secondaries (information)
- +830 step < 150 ms in both F arms: -2 / +1 ms (L: 223 / 170 ms).
- Memlog (free physical pages, rows ~1 s, ticks from room-2 entry): F arms' only drop >= 64 pages after entry is 192 pages at
  +70 ticks (ROF1, ROF2), nothing after +120 (as registered; RN: +71). L arms: 192 at +68 / +75, 192 at +148 / +153, 192 at
  +843 / +842, 512 at +1,730 / +1,734, 992 at +3,547 / +3,553 (= the step brackets). Minimum free 3,777 pages (14.8 MB) in F
  vs 1,889 (7.4 MB) in L, as in RN.
- Board holds (vcctrl; offsets from the lock, first poll showing the wait): F one hold each (+41.7, +43.2 s); L five each
  (ROL1 +42.4 / +90.5 / +107.6 / +130.8 / +177.9 s, ROL2 +42.0 / +90.2 / +107.3 / +130.7 / +176.9 s), within ~2.5 s of RN's.
  The +42 s hold (the room-1 commit) is in both arms; the four later ones only in L. Both L cells' ~+177 s hold (the 992-page
  commit) was caught mid-wait across a 1 s poll, none of the other L holds was (information: consistent with it being the
  longest; one-second polls cannot measure it). RN's RNF1 exit-time hold did not recur. max_wait_ms stays 2,407 (RN's).

## Displayed % (information; no target reading)

| Cell | Arm | displayed | room 1 + entry | room 2 | late | audio | in-play partials / mouse.dropped |
|---|---|---|---|---|---|---|---|
| ROF1 | F | 92.56% (521) | 204 | 81 | 228 | underruns 0 / overwrites 0 | 0 / 0 |
| ROL1 | L | 89.68% (723) | 236 | 122 | 357 | 0 / 0 | 0 / 0 |
| ROL2 | L | 89.65% (725) | 247 | 163 | 307 | 0 / 0 | 0 / 0 |
| ROF2 | F | 92.06% (556) | 203 | 104 | 241 | 0 / 0 | 0 / 0 |

- RO is the replication RN asked for. RN: F 91.48 / 92.55%, L 89.53 / 89.72%. RO: F 92.56 / 92.06%, L 89.68 / 89.65%.
  Over both rounds (same binary, same line, memlog on), every F cell is above every L cell: F mean 92.16%, L mean 89.65%,
  +2.5 points. RN attributed +0.65-0.9 points to the step windows; the rest of the gap now replicates but is not
  attributed here (the L arms run the old ring's growth all through the stay, not only at the three steps). RLM1-4 (the
  MS3 baseline, memlog off, legacy ring) read 90.68% (SD 0.89). Any MS3 target remains the operator's call.
- Full windows: WINDOWS.txt (ROUNDRF-2026-11-09/rescore.py).

## RODT: DPMITIM2 on the 486 (pre-registered terms, RODT-2026-11-12/README.md): reading (a) SUPPORTED
- Validity: all 8 files 10 lines (K=0) / 11 lines (K>0), "done rc=0"; header flags 0x5 (bit 2 set) in every D2A file and
  0x1 (clear) in every D2B file; header free 8,164 pages >= K + 992 for every K; every null phase lost_ms 0.0; every touch
  line rtc_ok=1. No file noisy, no K unread.
- c(K) = (rep-1 touch call_ms + lost_ms) / 992, ms per page:

| Arm | c(0) | c(2048) | c(4096) | c(6144) | c(6144) / c(0) | non-decreasing |
|---|---|---|---|---|---|---|
| A (default host) | 0.201 | 0.770 | 1.277 | 1.779 | 8.84x | yes |
| B (CWSDPMI -s-) | 0.195 | 0.771 | 1.276 | 1.779 | 9.11x | yes |

- Reading (a) SUPPORTED by the letter (>= 3x and monotonic in both arms): a first touch costs more per page the more pages
  the process already has committed, ~linearly (+0.25 ms per page per 1,000 pages committed), the same with and without
  swap. At the engine's ~5,300-6,300 pages in use that is ~1.5-1.8 ms per page, the size of the engine's steps (1.28-1.50 ms
  per page). Information: the touch rows lose no ticks (lost_ms <= 0.1, bios_ticks = expect): the commit runs with the
  clock going; rep 2 = rep 1 (no retention); A = B.
- Post-data, information only (not registered; labelled): the FREE rows (0502h of the 992 pages) lose BIOS ticks, growing
  with K: rep-1 lost_ms 55 / 659 / 1,154 / 1,648 ms (A) and 55 / 604 / 1,099 / 1,648 ms (B) for K = 0 / 2048 / 4096 / 6144;
  bios_ticks 6-7 of 18.2 expected (K=2048) and 6-16 of 36.4 (K=4096, 6144), cross-checking the loss; call_ms (uclock, blind
  to lost ticks) reads 18-86 ms. v2 marks these lines rtc_ok=0 because uclock falls > 25% short of the RTC window -- which
  is the tick loss itself -- so by the registered rule they are not read. Reading for the lab (move): releasing committed
  pages may run with interrupts off for ~0.27 ms per page per 1,000 pages committed; a vector reallocation commits the new
  block (touch, clock running) and then frees the old one (interrupts off), which would put the IRQ0-unserviced part of
  each legacy freeze in the free, not the commit. A hypothesis, for a lab check, not a finding.
- CORRECTION (2026-11-12, after the lab check; lab-rb 46605dac move-lab/rj/rn/LAB-REALLOC.txt): the free-row hypothesis
  above is REFUTED for the engine. In the lab, the legacy ring's growth split into its three libstdc++ steps shows the
  free never reaches the host (DJGPP's free() keeps the old block in malloc's free list; free pages never rise in any
  legacy run, lab or rig memlog), so DPMITIM2's explicit 0502h free has no counterpart in play. The 2 MB and 4 MB
  growths commit their whole new block (-512 / -992 pages) at the sbrk inside the ALLOC step, before a byte is copied.
  A standalone probe with the same libc calls stays lazy, so something in the engine's process makes its sbrk blocks
  commit eagerly. The cause (lab-rb ba9369ec, LAB-REALLOC.txt, confirmed in the lab; this replaces an earlier note
  here that ruled LOCK_MEMORY out from a static check): _crt0_startup_flags reads 0x1080 at every growth in play --
  LOCK_MEMORY (0x1000) is SET. The vendored SDL defines the flags as LOCK_MEMORY | NONMOVE_SBRK
  (src/main/dos/SDL_sysmain_runapp.c) and clears LOCK_MEMORY only in SDL_RunApp, which AGS never calls (its own entry
  point; 0 call sites in the exe). So DJGPP's ___sbrk locks (DPMI 0600h) every new heap block in play: the whole block
  is committed and pinned in one host call at allocation. The probe with LOCK kept set reproduces the engine (sbrk(2 MB)
  -512 pages, vector.reserve(4 MB) -1,040 at allocation; touching adds 0); with LOCK cleared the same calls are lazy.
  Reading for the 486 (not a rig finding): each freeze is that one long 0600h call; it also explains RM (locked pages
  are never paged, so the swap was never involved) and suggests every runtime heap extension pays it (room loads
  included). 0377's verdict is unaffected (it removes the biggest source). Clearing LOCK_MEMORY after startup is a
  candidate lever (not built; needs an ISR-buffer audit first): an operator / sdlports decision.
- RODT's l308 title launch: run-hw exit 0, stamp OK bc9c3704a839, no mouse input (ev_in +0).

## Bridge: P9M1 ROP1 99.36% (counts by the board-counter rule)
| Cell | displayed | room 1 + entry | room 2 | late | audio | in-play partials / mouse.dropped |
|---|---|---|---|---|---|---|
| ROP1 | 99.36% (45) | 36 | 1 | 0 | underruns 0 / overwrites 0 (silent_irqs 42; RNP1 42) | 0 / 0 |

Inside the registered 98.6-99.5%; RNP1 99.37% on the same binary. One cell, information.

## USB4VC 0.5.109 and the rig (vcctrl)
- ev_in +2,923 = pkt_ok over the round (= RN's); pkt_partial, pkt_timeout, pkt_inhibit, ev_buf_full, ev_discarded,
  edge_merged, host_fe, superseded, abandon_budget, inhibit_retry all 0; zero mouse.dropped rows; no input-log errors,
  refusals or ok:false rows. Resumes 13 (73 -> 86) = partial_waits; 15 mouse.resumed rows (two L holds split across polls).
  Host over the round: host_cmd +281, ff +66, f5 +18, kb_inhibit_retry +32 (RN +280 / +66 / +16 / +32).
- Capture: one black launch event (ROL2, +18 s after the lock: 4 decode errors, one flat-black frame truncated at row 464
  of 480), the launch pattern RN saw three times; none at the staging reboots or in RODT this time. Zero USB disconnects,
  zero usb_recover cycles.
- Wall-time note: RUNMANIFEST duration_s reads 198-199 s in every MS3 cell; it is taken from the engine's own clock, which
  stops during an IRQ0-unserviced freeze, so it is no witness of the F runs being shorter in wall time (not read).

## Next
- Removals owed now that the verdict is in: ags 0376 (DOSAGS_MEMLOG, TEMPORARY) and 0377's DOSAGS_RING_LEGACY switch
  (0377's bounded ring stays, ON). New patch slots, sdlports review, a clean rebuild and ratchet.
- Before 0377 reaches a release: the lockable-mode audio check (sdlports' terms: an SB4S-shape cell, AGS Quest, PGSB,
  640x480, capture locked, the 0377-default binary, memlog off, against a DOSBox-X reference made before the round; valid
  only if its voicering line shows compactions >= 1). Any v0.1.x is the operator's call.
- Lab (move): the RODT free-row reading above.
- MS3 target: not yet set (operator). With the freezes gone the fixed binary reads ~92.1-92.6% on MS3 (memlog on).

Files: SUMMARY.txt, PAIRING-ALL.txt, WINDOWS.txt, driveRO.sh / cellRO.sh / powerguard.sh / daemongap.sh / expected.txt /
ORDER-CONFIRMED, POWERGUARD.txt. Per cell: AUDIO-SHA256.txt / SAVE-SHA256.txt (the .ogg and AGSSAVE files are not
committed).
