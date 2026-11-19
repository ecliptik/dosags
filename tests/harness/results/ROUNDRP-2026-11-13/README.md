# ROUNDRP-2026-11-13 -- round RP results: the lockable-mode audio check for ags 0377 at 0379 -- PASS

Pre-registration: ef251f4f (pushed before any data; sdlports APPROVED). Operator's power-on OK asked directly in the
dosags session. One power-on: relay-on 09:27:25Z, power OFF 10:00:00Z (driver), confirmed OFF by powerguard 10:00:07Z and
by vcctrl's power.log 09:59:55Z (32.5 min mains-on, cap 60). Driver exit 0, every cell ran, nothing dropped.

## Verdict, by the pre-registered letter

**PASS: RPAQ1 and RPAQ2 are both VALID and both pass B1-B5** (tests/harness/aq-audio-bars.py, F = -66.35 dBFS, pcm_irqs
set {180,181} from REFAQ0379-2026-11-13). The lockable-mode audio check sdlports set before 0377 reaches a release is met
on the 0379 release (main be0d1d37, sha256 2191042b..., binary_sha12 d5c8fe52808a).

| cell | VALID (V1-V5, stamp, BLASTER) | voicering compactions / moved / cap_max | B1 pcm_irqs | B2 underruns / overwrites | B3 silent outside transitions | B4 card | B5 runs >= F+10 | CELL |
|---|---|---|---|---|---|---|---|---|
| RPAQ1 | yes; stamp OK; A220 I7 D3 P330 T3 | 2 / 55,532 / 169,344 | 180 | 0 / 0 | 0 (silent_irqs 0) | locked 104, frozen 12, frozen=False | one run of 8 (from 370.5 s), max -14.2 dBFS | **PASS** |
| RPAQ2 | yes; stamp OK; A220 I7 D3 P330 T3 | 2 / 55,876 / 169,344 | 180 | 0 / 0 | 0 (silent_irqs 0) | locked 100, frozen 12, frozen=False | one run of 8 (from 358.5 s), max -14.2 dBFS | **PASS** |

Both: exit 0, ENGINE HAS SHUTDOWN, 640 x 480, all 18 AutoPilot phases but quit ok (audio among them), one capture segment,
staged sha256 = pre = post (2191042b343c), build_dirty 0.

## The round

| step | result |
|---|---|
| WARMUPRP (l308, MMD title) | run-hw exit 0, stamp OK bc9c3704a839, BLASTER [A220 I7 D3 P330 T3]; capture STALE nolock (the 320x200 title, allowed); after it capture True locked |
| RPFLOOR (09:37:13-09:38:13Z) | OK, F = **-66.35 dBFS** (median of 145 samples, -66.78..-65.85); capture locked at start and end; no release / acquire needed |
| RPAQ1 (09:38:13Z) | as above |
| RPAQ2 (09:49:10Z) | as above |

## Information (not bars)

- **The rig matches the reference closely.** moved_bytes 55,532 / 55,876 are exactly the two values the DOSBox-X renders
  show (REFAQB / REFAQ / AQV); cap_max 169,344 as in all 15 renders. mixed = pcm_irqs = 180, drains 0, ring_max_ms
  743/743, MIDI late_max_ms 0, clk 2961 / 2963 ms per 3 s (RTC).
- B5's run is 8 windows (12 s) at -14.2 dBFS peak window in both cells vs 9 in SB4S / N7AQ on older binaries; >= 6 needed.
- Independent bracket (vcctrl, `vcctrl level 20000` every ~20 s, VCCTRL-LEVEL-20S.log; RPAQ2 only): the 20 s window ending
  09:55:19Z read -21.04 mean / -13.08 peak (every chunk at -13), the next -54.81 / -36.11 (the tail), every other window
  -64.5..-67.2 (the floor). Agrees with the sampler-based B5 read.
- Rig health (vcctrl): USB4VC ev_in = pkt_ok = 13066 (+0 over the round), resumes 86 (+0), 0 losses, no mouse traffic;
  input log 174 rows, 0 flagged, every lock released normally; one reboot black (3 frames at 09:28:53-54Z, after the first
  transfer reboot), decode_errs 19 -> 22; 0 USB kernel events. The audio reader never read -91 while powered (the
  pre-flight -91.0 with the target off was exact digital silence, per vcctrl; a fresh reader read the same).
- services paused its 5-minute ICMP ping of the target (started 2026-11-13 ~06:02Z, so never during RO or earlier) and
  held the plug for the round; vcctrl sent the all-clear.

## Not changed by this round

- The open lab item: why one DOSBox-X render in two or three writes one extra chunk (REFAQ0379 README). Both rig cells
  read 180.
- MS3 target: not yet set (operator). No cell counts toward any fps goal.
- Next, per the operator (2026-11-13, via sdlports): the LOCK_MEMORY lever -- lab patch 9001 to slot 0380 with an exit
  free-page sample, for review; then a pre-registered OFF / UNLOCK / PREGROW MS3 round reading off17-pre / off18-pre
  (baseline RO / RN F), with in-round OFF control, PREGROW's startup cost witnessed, and (d)'s swap / free-page witnesses
  in UNLOCK cells. Power-on needs a fresh operator OK.

Files: SUMMARY.txt (driver), POWERGUARD.txt, VCCTRL-LEVEL-20S.log, the driver copies (driveRP.sh, cellRP.sh, powerguard.sh,
daemongap.sh, expected.txt, PCMSET, ORDER-CONFIRMED). Per cell: AUDIO-BARS.txt, RUNMANI.LOG, STDOUT.TXT, LEVEL.log,
AUDIO-SHA256.txt (captures stay local), SAVE-SHA256.txt; AQ cells IMAGE-SHA256.txt (no AGS Quest image enters git).

## Addendum (2026-11-13, after round RP): the cause of the one-chunk jitter -- answered in the lab (move, lab-rb df52b851)

move-lab/rj/aq/AQ-PCMIRQS.txt (a lab overlay counting chunks per voice, no slot; six renders with the REFAQB command):
- AGS Quest's flow has ONE PCM voice: a streamed clip acquired at tick 3149 (AutoPilot phase=audio begin) and STOPPED at
  the phase's end (tick 3569) with 29-33 KB still unplayed; every mixed chunk is its data (nodata=0, so mixed = pcm_irqs).
- So pcm_irqs = the 512-sample chunks the SB consumed at its own real-time rate (46.4 ms each) between the voice's start
  and a stop fixed in GAME time: the run's timing moves that span across a chunk boundary. Six lab renders read 180 / 179 /
  180 / 180 / 180 / 181 (179 on the overlay build, a little extra main-thread work).
- The hypothesis above (a clip's start phase against the chunk grid) is REFUTED: the voice starts at chunk 0 in every
  render and ends by Stop, not by running out.
- Consequence for bar B1: the registered set {180,181} is not a bound. A rig value of 179 or 182 would be the same timing
  mechanism, not a defect. Round RP's verdict is unaffected (both cells read 180). For any later round on this flow, a bar
  on the mechanism is the robust form (pcm_irqs == mixed; underruns / overwrites / silent_irqs 0; pcm_irqs within a
  registered tolerance of the reference), or a count taken from the voice's own data rather than the device clock.
