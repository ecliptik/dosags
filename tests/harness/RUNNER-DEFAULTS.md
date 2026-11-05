# Runner default diff: `run-hw.sh` vs `run-dosbox.sh`

**Why this file exists.** On 2026-09-19 an instrument was "verified under
DOSBox-X" while living in a code path the emulator had never entered,
because `run-hw.sh` sets `DOSAGS_FIXED_TIMESTEP=1` by default and
`run-dosbox.sh` never set it at all. The emulator reported
`frames_skipped=0`, which read as *the emulator keeps up* and actually
meant *the code is switched off*. **Every DOSBox validation of anything in
that path had been vacuous** -- not wrong, vacuous, which is worse because
it looks like coverage.

One undocumented divergence hid an entire code path. This file enumerates
all of them so the next one is reviewable rather than rediscovered.

**Rule this establishes:** a divergence between the two runners is a
statement about which code the emulator can and cannot validate. It has to
be deliberate and written down here, not a side effect of one script
growing a default the other did not.

## The diff

| setting | `run-hw.sh` | `run-dosbox.sh` | what differs in the engine |
|---|---|---|---|
| `DOSAGS_FIXED_TIMESTEP` | **`1` by default** (`--no-fixed-timestep` opts out) | **unset**; `--fixed-timestep` opts in | **`dos_run_tick_fixed()` entirely** -- the catch-up accumulator, `MAX_CATCHUP` repayment, frame skipping, and every instrument in that path. Unset, `GameTick()` calls `UpdateGameOnce()` directly. |
| `SDL_DOS_AUDIO_SB_SKIP_DETECTION` | not set -- real hardware is detected | **`1`, hardcoded** in `dosbox-run.sh` | SDL3-DOS Sound Blaster autodetection (`patches/SDL/0001`'s escape hatch). **The detection path never runs under the emulator.** Same class of vacuity as the timestep case, for audio. |
| `BLASTER` | not set by the runner | **`A220 I5 D1 H5 T6`, hardcoded** | BLASTER-string parsing. On the target this comes from the machine's own `AUTOEXEC.BAT` (see `reference_sibling_repos_and_rig_config`), so the variable is probably present in both -- **but with different values, and the runner is not the thing setting it.** Not yet verified against the target's actual AUTOEXEC; flagged, not resolved. |
| `DOSAGS_LOG_TAG`, `DOS_PORT_LOG_TAG` | set to the cell tag | unset | Log file naming only. No engine behaviour. Benign. |
| `--user-data-dir` | `C:\DOSAGS` (the package dir) | `c:\` | Where `RUNMANI.LOG`, `AUTOPLT.LOG` and `PH0N.BMP` land. No engine behaviour, but it is why collection differs. Benign. |
| `C:\VGACAP\MODE12` after the run | yes | no | VGA capture restore on the target. Not engine code. Benign. |
| stall/skip-adjacent timing | real 486 timing | emulated, `cycles=max` | Not a setting, but the reason `--fixed-timestep` alone does not make the emulator representative: under DOSBox every skip is adjacent to a large blocking operation, where hardware shows a steady 13.2% through ordinary play. |

## Decisions

**`DOSAGS_FIXED_TIMESTEP` -- opt-in, not default.** The committed DOSBox-X
expectations (`expected/agsquest/dosbox-x.json`, the `PH0N.BMP` hashes)
were all recorded without it, and flipping the default would silently
change what every existing baseline compares against.

**That is a reason to re-record the expectations under a known
configuration, not a reason to leave the gate blind.** Re-recording is not
done and is the outstanding action from this audit. Until it is, **any
instrument verification on a fixed-timestep path must pass
`--fixed-timestep` explicitly**, and the flag's own comment in
`run-dosbox.sh` says so.

**`SDL_DOS_AUDIO_SB_SKIP_DETECTION` -- unresolved.** The emulator cannot
validate SB detection while this is hardcoded on. Whether that matters
depends on whether anything in the detection path is still changing; it is
not on the 40/40 critical path, so it is recorded rather than fixed.
**It should not be discovered the same way the timestep divergence was.**

## When a code path can only be entered under real timing

The pre-cell rule ("prove the code executes before spending a cell") has no
way to be satisfied off-target for a path the emulator cannot enter even
with the right environment. `DOSAGS_SKIPTEST=1` (patch 0143) is the answer
for the per-skip instrument: it forces the reporting branch once, at a
fixed tick, exercising only the report and never an extra tick, so it
cannot perturb what it verifies.

**Generalised: an instrument on a timing-gated path ships with a
forced-execution mode, or it cannot be verified before the cell that
depends on it.** That is a requirement on instrumented code, not a
workaround.

## Hazard: an MCP power action can leave the hardware lock held

**Symptom in the log:**

    run-hw.sh: REFUSED -- send-file did not verify cleanly
    hw_guard: REFUSED -- input lock is held by 'mcp:claude:<pid>'
    HW-RECOVERY ... outcome=STOPPED-lock-held-by-mcp:claude:<pid>

**It presents as a send-file verification failure**, with the lock on a
secondary line. The first line points at the transfer, the cable or the
target. Observed 2026-09-19 on cell FIVE1.

**Mechanism, read from source rather than assumed** -- the first
explanation recorded here was that a coordinator session's status polling
took the lock, and that was wrong. `vcctrl_power_state` and
`vcctrl_activity` do not go through `_gated_run`, and `_gated_run`
releases in a `finally` unless the lock is sticky. **Reads were never
candidates.**

`vcctrl_power` **does** bypass `_gated_run` and calls `_run_vcctrl`
directly with `--as OWNER`, so if the daemon grants the lock on a power
action nothing on the MCP side is responsible for releasing it. The timing
fits: `held_s` 307 against `load_on_s` 269 puts the lock acquisition
17-38 s **before** the machine came up. **The power-on in question was
mine**, issued from this worker a few minutes earlier.

**The owner string cannot say whose it was.** `mcp:claude:<pid>` names the
MCP *server* process, and sessions here appear to share it -- which is how
the coordinator read their own PID and concluded it was their polling.
**That ambiguity is part of the defect, not just of this incident.**

**Working rule until vcctrl says otherwise: treat an MCP power action as
lock-taking.** After bringing the machine up through the MCP tool, check
`vcctrl_lock_status` and release if it is held with nothing inflight -- or
use the CLI path the harness already uses. One check costs nothing beside
a refused cell.

**The guard was right to refuse.** It will not touch a machine another
owner holds, and that rule does not bend. It now also logs `held_s`,
`inflight` count and a `lock_looks_stale` flag, so *stale, safe to
escalate* is distinguishable in the record from *someone is genuinely
working* without a human reconstructing it.

### FIXED in vcctrl `e56a6c8` -- but the workaround is still live this session

**Mechanism, confirmed by vcctrl and different from both earlier guesses:**
`vcctrl_power` called `LOCK.ensure()` itself and then `_run_vcctrl()`
directly, **bypassing `_gated_run`, whose `finally` is the only release
path an MCP tool has.** So every power on/off/cycle held the lock until
the 300 s idle timer expired -- polled every 15 s, which is exactly the
285-then-307 observed. Fixed by routing it through `_gated_run`, with
`profile="default"` pinned so a session default cannot redirect a mains
action to another daemon.

**The fix is not active here.** Each session spawns its own MCP server and
picks up new code only on restart; ours predates the commit and restarting
mid-campaign is worse than the workaround.

> **SESSION-SCOPED WORKAROUND -- expires when this session ends:**
> **call `vcctrl_lock_release` immediately after every `vcctrl_power`.**
> Both sessions share one MCP server process, which is also why the owner
> string read as the coordinator's PID for a power-on the worker issued.

**Status reads are exonerated:** `vcctrl_power_state`, `vcctrl_activity`
and `vcctrl_lock_status` go through `_run_vcctrl_p` and never touch the
lock or the idle timer.

**Residual, unreproduced:** a lock leaked by an MCP process that **dies
hard** is unbounded -- the 300 s timer lives in that process and the daemon
has no expiry of its own. A killed session would wedge the rig
indefinitely. Not what happened here.

### Operator ruling: the guard refuses on a stale lock, permanently

**No automatic escalation, not even for a hard-killed owner.** A refused
cell costs one run and is obvious in the log; `lock.broken` publishes
`taint=True` by design, so an automatic break during an unattended
overnight session would produce **silently tainted data that the next
reader has no reason to distrust.** With `e56a6c8` fixing the leak, stale
locks should be rare enough that the trade is clearly wrong.

**The diagnostic half is the permanent answer, not step one toward
escalation.**

### Our bug, not theirs: we discarded a precise refusal and paraphrased it

vcctrl grepped their repo: neither `"did not verify"` nor `"job.ok"`
appears there. **The daemon's own refusal already leads with the lock** --
`input locked by '<owner>' since <t>`, plus `locked_by`. `run-hw.sh` then
printed a summary line that buried that under a transfer verdict, and
**the tail of the log is what anyone reads first.**

Fixed: `hw_guard` returns 3 specifically for "lock held by another owner",
and `run-hw.sh` now leads with the lock in that case, keeping the transfer
verdict as a consequence rather than the headline.

**Rule, because this is the second instance today:** *when wrapping
something that already reports, pass its report through -- do not restate
it.* The other instance was patch 0081's bracket comment asserting
"nothing here touches the back buffer" about a call chain that reaches the
background restore. **Both times the information we needed already existed
and our own layer threw it away or paraphrased it wrongly.**

### Originally filed with vcctrl

A power action through the MCP path can leave the hardware input lock
held. Open questions filed with it: whether the idle timer is refreshed by
unrelated same-owner calls, which would make a stale lock immortal; and
whether the owner string can carry a caller-level identifier so this is
diagnosable from a log instead of by elimination.

Evidence: owner `mcp:claude:1917968`, `held_s` 307, `inflight: []`, no
harness process running, cleared only by an explicit `vcctrl_lock_release`.

## Parallel DOSBox-X on one host: the lock, your display, your own emulator (2026-09-23)

Several workers run DOSBox-X on this box at once. Three rules, all enforced by the harness:

- **Host-wide lock** (hub `dosbox-run.sh`, `/tmp/dos-port-dosbox.lock`): plain functional runs take
  it SHARED; `--sb-live` and `--interactive` runs take it EXCLUSIVE. A gate or series takes it
  EXCLUSIVE once around the whole series through `dosbox-lock.sh` (`gate-alias.sh`,
  `gate-present.sh`, and `run-dosbox.sh`'s `--freeze-capture` / `--screen-series` / `--sb-live`
  paths) and exports `DOSBOX_LOCK_HELD=1` so the runs inside do not take it again. A throwaway
  series script does the same: `source tests/harness/dosbox-lock.sh; dosbox_lock_series NAME ||
  exit $?; trap dosbox_lock_release EXIT`. A waiter prints the recorded holder from
  `<lockfile>.who`, marked alive or STALE. Test LOCK1 (`results/LOCK1-2026-09-23/`): a gate and an
  `--sb-live` cell started 3 s apart; the cell waited until the gate released.
- **Your own display** (`DOSBOX_DISPLAY_NUM`; dosags-worker 211, the labs 221/231/241/261):
  freeze and series captures photograph the root window, so `run-dosbox.sh` refuses a display that
  already shows a DOSBox-X window.
- **Your own emulator:** the watchers find this run's stage through its own process ancestry, the
  kill matches that stage exactly, and an EXIT trap takes down the watchers, the emulator and the
  Xvfb when the runner is killed (a caller's `timeout`). Never `ps | head -1`, never a global
  `pkill dosbox-x`.

### run-dosbox.sh refusals and failures added 2026-09-23

- **`AGS_EXE`'s basename must be DOS 8.3** (at most 8 characters before `.exe`). The exe is staged under
  its own name and `RUN.BAT` calls it by that name; `ags-0209-clean.exe` gives "Bad command or
  filename" at a DOS prompt. Copy a pinned binary to `.../ags.exe`. run-dosbox.sh now refuses
  (exit 2).
- **An interactive run must be able to end.** `--interactive`, `--freeze-capture` and
  `--screen-series` hold the host-wide lock EXCLUSIVE, and interactive DOSBox-X does not exit when
  the game does. Every interactive run is now stopped 3 s after the engine writes `RUNMANIFEST-END`,
  and a run with neither `--env DOSAGS_TAS_AUTO_EXIT_TICK=N` nor an explicit `--timeout` is refused
  (exit 2). (A lab run held the lock idle for ~4.5 min before this.)
- **`--timeout` no longer counts the wait for the lock** (2026-09-24): run-dosbox.sh takes the lock
  itself, then starts the timeout. A run whose game still never wrote STDOUT.TXT exits 1 with "the
  game never ran" (it used to exit 0 with an empty stage).
- `--no-verify-present` runs used to exit 1 before printing the stage dir (the missing presentverify
  line failed a grep under pipefail); fixed.

### Fixed cycles may share the lock (2026-09-23, hub bb5482c)

DOSBox-X at FIXED cycles (`cycles = fixed N`, e.g. `tools/dosbox-x.conf` or
`confs/dosbox-x-fixed40k-opl3.conf`) is deterministic whatever the host load, so
time comparisons belong there (at cycles=max the emulated speed drifts even
within one tick: RT1a's identical mask passes fell from ~17 to ~2 ms), and such
runs take the lock SHARED:
- `run-dosbox.sh --conf <fixed-cycles conf>` takes it shared for every run type,
  interactive, freeze and series included.
- `GATE_CONF=<conf> gate-alias.sh` runs every row under that conf, and shares
  when it is fixed-cycles (`GATE_RUN_TIMEOUT` raises the per-run timeout, since
  rows run slower at fixed cycles).
- A throwaway series script: `dosbox_lock_series NAME shared`.
EXCLUSIVE stays for cycles=max timing/rate, cycles=max gates and `--sb-live` at
cycles=max. A nested series that needs exclusive under a shared parent is
refused (exit 75): a shared holder cannot upgrade in place.
`dosbox_conf_fixed_cycles CONF` (in `dosbox-lock.sh`) is the detector.
Writer priority (2026-09-24): `dosbox-lock.sh` now sources the hub's
`dosbox-lock-lib.sh` (intent lock, hub b9b7364), so a queued exclusive waiter
blocks NEW shared takers -- the fix for the over-an-hour starvation seen
2026-09-23. It only works when every taker uses the library: take the lock through
`dosbox-lock.sh` (or the hub's `dosbox-run.sh`), never with a bare `flock`.

### Displays and host input (2026-09-24, hub b79e724 / ee910e5)

- `run-dosbox.sh` owns its display per the hub's pattern (tooling.md): it takes display N's flock
  (fd 5) after the host lock, starts its own Xvfb with fds 4-9 closed and waits until that pid
  answers, runs `dosbox-run.sh` with `DOSBOX_DISPLAY_HELD=1`, and on exit kills its Xvfb and WAITS
  for it before the display is released. Two cells pinned to the same display now run one after
  the other (DISPTEST-2026-09-24: bench8 and Shards on :211, the second waited, each captured its
  own game, no lock left held by an Xvfb).
- A DOSBox-X window on a display this run holds is an orphan of a killed run and is refused.
- `--no-host-input`: required for a display run to share the host lock at fixed cycles. It asserts
  nothing on the host drives input (AutoPilot, freeze gates). `gate-alias.sh` passes it; xdotool-
  driven cells (click-cell.sh) take the lock EXCLUSIVE.
