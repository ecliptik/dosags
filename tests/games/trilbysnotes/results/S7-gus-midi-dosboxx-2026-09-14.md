# S7 -- GUS MIDI escape-hatch test: DOSBox-X pass (known detection gap, correctness-only) -- 2026-09-14 (new session)

Follow-up to `S7-midi-no-backend-realhw-2026-09-14.md`'s own practical-
implication note. This investigation's whole S7 arc measured the tax
exclusively against OPL3 and WaveBlaster/MPU-401 -- both of which
concurrently coexist with the SB16 device on this rig's PicoGUS card
(same firmware, same physical card, SB16 emulation active alongside
the MIDI chip emulation). GUS is structurally different: the S5 GUS
architecture work (`PLAN.md`, "S5 GUS architecture -- decided
2026-09-13") established that GUS is a **genuine firmware-mode swap**,
not an add-on -- under `PGGUS`, the card runs Ultrasound-emulation
firmware only, with no SB16 emulation active at all (`sys_audio_init()`'s
own "Model B, out-of-band" branch never even calls `SDL_InitSubSystem(
SDL_INIT_AUDIO)`). If this investigation's working hypothesis (a
persistent hardware/electrical effect of activating a second legacy
interface *alongside* the SB16 emulation) is right, GUS -- which never
has an SB16 counterpart active on the card at all -- should escape the
tax entirely. This is directly actionable: GUS was already built,
DOSBox-X-validated, and real-hardware-confirmed for gameplay in S5
(AGS Quest, tag `GUSQ2`, `tick_rate=6.48`, real dispatch, zero
underruns) -- but never combined with `DOSAGS_FIXED_TIMESTEP=1` (S5
predates that combination entirely; S7's own founding premise is that
fixed-timestep's catch-up mechanism is what exposes this whole tax
family).

## DOSBox-X validation

Same binary as `NOBK1` (`binary_sha12=433340f66668`, unmodified -- GUS
support needed no new patch, already fully wired since S5). Added a
scratch `[gus]` section to `dosbox-x-fast.conf` (`gus=true gusbase=240
gusirq=7 gusdma=3`, matching this rig's real jumpers, reverted after)
per `GUS-PROBES.md`'s own documented recipe. Ran Trilby's Notes with
`SDL_HINT_DOS_AUDIO_BACKEND=gus`, `ULTRASND=240,3,3,7,7`,
`ULTRADIR=C:\ULTRASND` (matching the real rig's own AUTOEXEC values),
`DOSAGS_FIXED_TIMESTEP=1`, `DOSAGS_TAS_AUTO_EXIT_TICK=200`.

**Result: clean run, `exit_code=0`, no crash, no hang** -- but `audio_
vital_status` shows `midi=none,events=0`, not real GUS MIDI dispatch.
`LOGS\SDLDBG.LOG` shows why: `audio: SDL/0112 GUS GF1 detect: present=0
base=0x240 irq=7 dma=3 dram=0KB voices=20 rate=30870Hz` -- `gus_parse_
ultrasnd()` correctly parsed the `ULTRASND` string (base/irq/dma all
match), but the actual GF1 hardware-presence probe (a DRAM read/write
signature test) reports absent under DOSBox-X's own `[gus]` emulation
with this configuration. **This is a pre-existing, already-documented
gap, not a new bug**: the S5 GUS architecture design notes flagged this
exact uncertainty before any GUS code was real-hardware-tested ("does
DOSBox-X's GUS emulation support voice_active_mask polling well enough
to validate the swap-on-reap logic at all -- an open question"), and
this session did not attempt to root-cause DOSBox-X's own GUS emulation
further -- consistent with this hub's "never contribute upstream" scope
(DOSBox-X is an external dependency) and its own "DOSBox-X is a
correctness gate, not a performance proxy" discipline.

**What this DOSBox-X pass DOES confirm**: the PCM/mixer subsystem
correctly selects the GUS branch (`DOSAudioMixer: GUS PCM path active`),
the engine correctly falls back to `midi=none` when GF1 presence fails
(the same graceful-degradation contract `dos_midi_backend_open()`'s
other backends already use), and nothing about combining GUS with
`DOSAGS_FIXED_TIMESTEP=1` for the first time crashes or hangs. This is
enough to proceed to real hardware, where GF1 presence is already
independently confirmed working (`GUSQ2`, `present` implied by real
dispatch, `midi=gus,events=146`, zero underruns) -- DOSBox-X's own gap
here says nothing about real-hardware behavior, per the same boundary
this whole investigation has relied on throughout (DOSBox-X never
reproduced the original tax either).

## Not yet done

1. The real-hardware cell -- the actual test. Needs `--boot-profile 3`
   (PGGUS) via `run-rig.sh`, `SDL_HINT_DOS_AUDIO_BACKEND=gus`,
   `DOSAGS_FIXED_TIMESTEP=1`, `DOSAGS_TAS_AUTO_EXIT_TICK=200`. `ULTRASND`/
   `ULTRADIR` do not need explicit `--env` passthrough on real hardware --
   the PGGUS boot profile's own `AUTOEXEC.BAT` already sets both as real
   DOS environment variables before `RUN.BAT` launches, and `sys_audio_
   init()`'s existing bridge picks them up automatically.
2. Acceptance gate items 4 and 5 remain FAIL (unaffected either way by
   this test -- it targets a different practical question, not the
   pre-registered OPL3 acceptance bar).
