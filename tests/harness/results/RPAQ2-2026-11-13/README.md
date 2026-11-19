# RPAQ2 -- AGS Quest on the 0379 release (second cell, terms as RPAQ1), the lockable-mode audio check (written 2026-11-13; pre-registration, before any data)
- Fixture (the SB4S shape, on the current AGS Quest rig line, N7AQ 2026-11-06): agsquest, drive 0 (AutoPilot: its MIDI tune
  and the CC0 chime in the `audio` phase), `--no-fine-timing`, SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1,
  games/5days/ACSETUP-ON.CFG as ACSETUP.CFG (sound on, 640x480 16-bit), BLASTER witness; PGSB; RUNHW_MIN_WAIT_S 240. The
  tag carries "AQ" (licence rule: no AGS Quest image enters git; image hashes only). Captures (.ogg) stay local
  (AUDIO-SHA256.txt), as every round.
- Reference: tests/harness/results/REFAQ0379-2026-11-13 (five DOSBox-X renders of this binary and flow, REFAQB1-5, made and
  committed with this pre-registration, before any rig data): pcm_irqs set {180,181}; compactions 2 in every render.
- Read by tests/harness/aq-audio-bars.py <cell> <F> 180,181 (committed with this pre-registration; its docstring is the rule):
  VALID only if all of: V1 exit_code=0 and "ENGINE HAS SHUTDOWN"; V2 the cell's OWN voicering line shows compactions >= 1
  (sdlports: the lab pre-check is not enough); V3 every AutoPilot phase but quit ok, `audio` among them; V4 "Graphics mode
  set: 640 x 480"; V5 exactly one capture segment. The driver adds: stamp d5c8fe52808a (else STAMP-VOID) and BLASTER.TXT
  "A220 I7 D3 P330 T3" (else BLASTER-VOID). A VOID cell is reported; it is neither a pass nor a fail.
  Bars (sdlports' terms):
  B1 pcm_irqs in {180,181} (exactly the values seen in the five registered renders; any other value FAILS)
  B2 underruns = 0 and overwrites = 0
  B3 silent IRQs outside room transitions = 0 (silent_irqs minus the irqs of `silentirq` lines with since_room <= 2;
     silent IRQs no such line accounts for count as outside)
  B4 capture card locked (witness MANIFEST card.frozen false, no WITNESS-CAPTURE-STALE.txt)
  B5 level: audio-compare.py's 1.5 s windows at >= F + 10 dB form exactly ONE contiguous run of >= 6 windows (9 s, >= the
     reference's 180 chunks x 512 / 11025 Hz = 8.36 s of PCM)
- Round verdict (both cells): PASS = RPAQ1 and RPAQ2 both VALID and both pass B1-B5 -> the lockable-mode audio check is met
  for 0377 at 0379. FAIL = any VALID cell fails any bar -> 0377 does not reach a release until the failure is understood
  (reported with the bar's numbers). INCOMPLETE = anything else (a VOID or dropped cell, no FAIL) -> a later round; no
  pass is claimed from one cell.
- Calibration of the bars on the 486's earlier AGS Quest cells (pre-0377 binaries, information): N7AQ (2026-11-06) and SB4S
  (2026-09-23) both pass B1-B5 with F = -67.9 (pcm_irqs 180 / 181; one run of 9 windows at about -14 dBFS, starting
  370.5 / 349.5 s into the capture), and both read VOID on V2 (no voicering line: they predate 0377). Synthetic controls
  on N7AQ's records (LAB, scratch only): pcm_irqs 182 -> FAIL B1; underruns 1 -> FAIL B2; 2 silent IRQs at since_room 1
  plus 1 unaccounted -> FAIL B3, 2 at since_room 1 only -> PASS; a STALE file -> FAIL B4; floor -25 dB (run of 4) -> FAIL
  B5; compactions 0 -> VOID V2; two capture segments -> VOID V5.
- Open item (lab, owed, not a blocker): why one render in two or three writes one extra chunk (REFAQ0379 README).
- Round RP: the lockable-mode audio check owed before ags 0377 (the bounded mixer voice ring; the 486 room-2 freeze fix,
  round RO SUPPORTED) reaches a release (sdlports' terms, 2026-11-12, amended 2026-11-13). One power-on, CAP_MIN 60.
  Order: WARMUPRP -> RPFLOOR -> RPAQ1 -> RPAQ2. Driver build/ws/roundRP/driveRP.sh (from driveRO.sh), cell
  build/ws/roundRP/cellRP.sh (cellRO.sh verbatim: audio-sampler.sh + audio-rec.py run in every cell). Budget: warm-up
  ~630 s from relay-on (RO: 593-630), floor 60-130 s, RPAQ1 / RPAQ2 typical 780 s each (N7AQ's line) = ~2,320 s vs
  60 x 60 - 240 = 3,360 s; a cell that does not fit (ccell's typical-time rule) is dropped and reported, never cut short.
- Binary: the 0379 release, main be0d1d37, sha256 2191042b343cfd66..., binary_sha12 d5c8fe52808a (r0379.STAMP; a mismatch is
  STAMP-VOID), staged from build/ws/roundRP (expected.txt; a mismatch stops the round before power-on). Memlog is gone
  (0378), the legacy switch is gone (0379): the cells run the default, as a release would.
- Not in this round: the LOCK_MEMORY lever (lab study only; move). Its swap / free-page prediction (sdlports' (d)) belongs
  to the round whose binary carries the lever, not this one. MS3 target: not yet set (operator). Diagnostic and release
  check only; no cell counts toward any fps goal.
