# S7 -- real-hardware re-run of the patch-0060 fix, HW-486-66 -- 2026-09-14

Continuation of `S7-abba-2026-09-13.md` (root cause) and
`S7-fix-dosbox-x-2026-09-14.md` (instrumentation + fix, DOSBox-X
validated). This is the real-hardware A/B/B/A re-run those two
explicitly said was still required before acceptance gate items 4/5
could close. Operator-approved real-hardware session.

## Raw data (A/B/B/A block, same recipe as 2026-09-13)

Trilby's Notes, `DOSAGS_FIXED_TIMESTEP=1`, `DOSAGS_TAS_AUTO_EXIT_TICK=1000`,
default PGSB boot profile, binary `binary_sha12=6e4c8a677027` (patches
0059+0060 both applied) throughout.

| Cell | Tag | Arm | fps_p50 | fps_p95 | tick_rate | duration_s | audio_vital_status |
|---|---|---|---|---|---|---|---|
| A1 | F7A1 | sound-off | 5.17 | 5.50 | 23.68 | 49 | NA |
| B1 | F7B1 | sound-on (OPL3) | 0.58 | 0.61 | 3.37 | 308 | pcm=sb@11025m16,voices=8,underruns=0;midi=opl3,events=4980 |
| B2 | F7B2 | sound-on (OPL3) | 0.58 | 0.61 | 3.37 | 309 | pcm=sb@11025m16,voices=8,underruns=0;midi=opl3,events=4976 |
| A2 | F7A2 | sound-off | 5.22 | 5.50 | 23.77 | 49 | NA |

All four: `exit_code=0`, `critical_count=0`, `warn_count=0`, same
`binary_sha12` throughout. Game identity independently confirmed via
STDOUT.TXT (`Game title: 'Trilby's Notes'`) for every cell that produced
one.

**A-to-A spread**: fps_p50 5.17 vs 5.22 (delta 0.05), tick_rate 23.68 vs
23.77 (delta 0.09) -- tight, matches the 2026-09-13 baseline's own
spread almost exactly. **B-to-B**: fps_p50/fps_p95/tick_rate identical to
two decimal places; event counts 4980 vs 4976 (close, not required to
match exactly unlike the 2026-09-13 block since this is a different
binary). Block is valid.

## Verdict: FAIL, same magnitude as pre-fix

Baseline (sound-off) avg fps_p50 = (5.17 + 5.22) / 2 = **5.195**.
Sound-on fps_p50 = **0.58**. Cost = **4.615 fps**, against the
pre-registered `<= 1.5 fps` bar.

**The patch-0060 fix produces no measurable real-hardware improvement.**
Compare directly to the pre-fix 2026-09-13 block (same workload, same
rig, same pre-registered bar):

| | pre-fix (2026-09-13) | post-fix (2026-09-14) |
|---|---|---|
| sound-off tick_rate | ~23.8 | ~23.7 |
| sound-on tick_rate | ~3.27 | ~3.37 |
| sound-off fps_p50 | ~4.99 avg | ~5.195 avg |
| sound-on fps_p50 | ~0.57 | ~0.58 |
| cost | 4.42 fps | 4.615 fps |

tick_rate moved from 3.27 to 3.37 -- a ~3% change, indistinguishable
from run-to-run noise given the A-to-A spread above. **This directly
contradicts the DOSBox-X validation in `S7-fix-dosbox-x-2026-09-14.md`**,
which measured a real (if partial) recovery under a deliberately slowed
DOSBox-X conf (tick_rate 13.85 -> 15.37 there). DOSBox-X's own
WaitDevice/DOS_Yield/SDL_Delay timing model evidently does not predict
real-hardware behavior here -- exactly the reason this hub treats
DOSBox-X as a correctness gate, never a performance proxy, and exactly
why this real-hardware re-run was required before closing anything.

**What this means for the root-cause diagnosis**: patch 0060 removes the
mid-catch-up-burst calls to `audio_core_entry_poll()`, leaving exactly
one call per `GameTick()` (via `WaitForNextFrame()`) unchanged. That this
had ~zero real-hardware effect means the up-to-6x multiplier was NOT
the dominant real-hardware cost -- most of the real per-`GameTick()`
audio-service cost must be concentrated in that one remaining call, not
spread proportionally across the removed extra calls the way the
DOSBox-X data suggested. The DOSBox-X-measured mechanism (`WaitDevice`
finding the ring already full on redundant back-to-back calls) may
simply not be what real SB16 hardware does under this exact call
pattern, or something else entirely dominates on real hardware. **Not
yet identified** -- see "Not yet done" below.

## A real harness bug found and worked around, not routed around silently

`tests/harness/run-rig.sh`'s `wait_for_stable_screen()` gave a **false
"run complete" signal at ~135s** for both F7B1 and F7B2, well before
the engine's own real completion (confirmed after recovery: `duration_s`
=308/309 in each cell's own RUNMANIFEST, written by `quit()`'s clean-
shutdown path, which only ever runs on a genuine clean exit). Mechanism:
the detector is content-blind (a 32x24 downsampled frame-signature diff,
threshold-8, >2% pixels changed = "changing") and requires 60s of
`static` state past a 90s floor to declare completion. At `fps_p50=0.58`,
consecutive real renders ~1.7s apart can plausibly look visually
identical to this coarse a comparison for well over 60s even while the
engine is genuinely still ticking -- the heuristic was tuned/validated
against AGS Quest's own higher-fps walkthrough, not against a
catastrophically-degraded sound-on arm's own worst case.

**Consequence chain, all downstream of that one false positive**: the
script proceeded to "collecting results" while AGS.EXE was still
genuinely running -> `vc get-file`'s own reset step never got a live
response (the DOS side was busy, not idle) -> `"reason": "the machine
never reset -- Scroll Lock did not clear"` (`vcctrl`'s own
`OPEN-FAULTS.md` sec 23 precedent, same rig/project) -> `wait_for_job_
done` gave up after its full 1800s -> next cell (F7B2) ran into the same
thing since the underlying game was STILL not done.

**Recovery**: `vcctrl verify-input` confirmed PS/2 alive; a fresh KVM
capture (not the embedded frame in the failed job's own response, which
turned out to be a stale/cached frame, not a live one) showed a genuinely
idle `C:\DOSAGS>` prompt -- the game HAD finished on its own by then.
`vcctrl power cycle` (sanctioned recovery for this exact signature per
the same precedent, safe because the job had already failed rather than
being mid-run) restored clean responsiveness, confirmed via a full init-
banner capture (CuteMouse, PicoGUSinit, MSCDEX, `[PGSB] ready`) -- not
just inferred from `power state`. The engine's own `F7B1.LOG`/`F7B2.LOG`
(written before the hang-that-wasn't was ever suspected) survived on
disk and were fetched directly afterward, which is what actually
recovered this session's real numbers.

**In hindsight the power-cycle was not necessary** -- nothing was
actually hung, the game finished on its own once given enough real
time -- but it was harmless (a cycle from an already-idle DOS prompt),
and was the sanctioned recovery for the symptom actually observed at
the time (a stuck collection + a `no-reset` refusal, indistinguishable
in the moment from the documented genuine-hang precedent). Treated per
this hub's own "instrument/verify before concluding" discipline: input
was checked, a fresh independent capture was taken, and the actual
engine-written manifests were recovered and read before trusting any
theory -- not assumed from the first ambiguous signal.

**Fix needed** (not yet made): `wait_for_stable_screen()`'s
`STILL_SECONDS`/`MIN_WAIT_S` pair needs to scale with (or otherwise
account for) the arm's own expected fps, not use one constant tuned for
AGS Quest's walkthrough -- or the detector needs to stop being purely
content-blind (e.g. also poll for the tag's own `<TAG>.LOG` appearing on
the target as a positive completion signal, which the engine only ever
writes at genuine clean shutdown). Filed here rather than fixed inline
this session -- the real-hardware campaign already used its budget on
recovery and diagnosis; fixing and re-validating this properly deserves
its own slice.

## A second open question: AUDIOPRB.LOG produced no real-hardware data

Patch 0059's own diagnostic (the same binary, `binary_sha12=6e4c8a677027`)
never appended anything during either 308s/309s sound-on run. The only
line in `AUDIOPRB.LOG` on the target is from the earlier sound-off cell
(`slots_us`/`pump_us` mean ~14us, matching the expected near-zero
no-device-open cost) -- fetched and confirmed directly off `C:\DOSAGS`
post-recovery, not inferred. Given real MIDI events genuinely dispatched
(4980/4976, confirmed via `audio_vital_status`), `audio_core_entry_
poll()` was clearly being called many times over 308s -- so the 200-call
flush threshold should have been crossed repeatedly. It wasn't. Not
diagnosed this session -- a real gap in the one diagnostic tool built to
answer exactly this question, worth understanding before trusting it
again. Candidates worth checking first, not yet verified: file I/O
contention with real SB16 DMA/IRQ activity on this DOS target (unlike
the diagnostic's DOSBox-X runs, which had no such contention), a real-
hardware-specific silent `fopen()`/`fprintf()` failure, or a bug in the
window-accounting logic that only manifests when calls interleave with
audio at real, uneven rates rather than DOSBox-X's more uniform timing.

## Not yet done

1. **Explain why the real-hardware cost doesn't track the DOSBox-X-
   measured mechanism.** The fix targeted a real, measured DOSBox-X cost
   center (`SDL_DOSAudioPump`'s `WaitDevice` ring-wait, hit more often by
   the removed multiplier) but that reduction didn't move the real-
   hardware number. Need real-hardware per-call instrumentation --
   `audio_core_entry_poll()`/`dos_audio_mixer_pump()`'s own real cost,
   directly, on HW-486-66 -- which requires fixing the AUDIOPRB.LOG gap
   above first.
2. Fix `wait_for_stable_screen()`'s low-fps false-positive (see above)
   before the next real-hardware campaign wastes rig time on it again.
3. Acceptance gate items 4 and 5 **remain FAIL**. Patch 0060 stays
   landed (it's a real, correct simplification -- catch-up ticks
   genuinely don't need mid-burst audio service, per S1's own original
   reasoning for the call it narrows) but is not sufficient on its own.
   Patch 0059's diagnostic stays landed too, still needed for the next
   investigation round -- not reverted yet, contrary to its own "to be
   reverted once the fix lands and re-measures clean" note, because
   there is no clean re-measurement to revert it against yet.