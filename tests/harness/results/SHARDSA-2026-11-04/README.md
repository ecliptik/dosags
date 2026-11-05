# SHARDSA -- Shards --startr room probe for a gating alias row, 2026-11-04

Operator option (a), via sdlports: find a Shards room where DOSAGS_BREAK_0193=1
on A makes A != B in the gate's deterministic mode, so a Shards alias row can
gate with a --break-a control. Budget: 4 rooms, plain + --break-a. Fallback (b):
ship the deterministic title row as information only.

Mode: GATE_CONF=confs/dosbox-x-fixed40k-opl3.conf, GATE_FIXED_TIMESTEP=0,
GATE_ASSERT_NO_SKIP=1, freeze ticks 100,300,500,700,900, auto-exit tick 1000,
GATE_CAT_STARTR_shards=N (gate-alias ea812635). Instrumented build
7e5dfe26f272. Script: shards-probe.sh. Frame PNGs are not kept (game imagery).

Picking the rooms: the title is room 0. No room has an animated background
(no AnimBg block in any room0-9.crm; parsed against vendor/ags
Common/game/room_file.cpp). Rooms were picked from their compiled script
imports (repeatedly_execute, Animate, SetTimer): 6, 9, 1, 5, in that order.

| room | plain                         | --break-a                     |
|------|-------------------------------|-------------------------------|
| 6    | ok, 5 pairs, 0 problems, 0/0  | ok, 5 pairs, 0 problems, 0/0  |
| 9    | VOID, 2 pairs (froze at 100, 300 only), skips ?/? | same          |
| 1    | VOID, 5 pairs equal, skips ?/? | same (5 pairs equal)         |
| 5    | FAIL, 0 pairs: script error on the jump | same                 |

- Room 6: deterministic and clean, but the break has no effect: no control.
- Rooms 1 and 9: RUNMANI reads frames_skipped=-1 (one render more than loop
  ticks, the offset ags 0048 describes, not a skip). gate-alias's
  frames_skipped regex takes only digits, so the row VOIDs. Room 1's pairs are
  equal with the break on as well, so it has no control either way. Room 9
  never reached tick 500.
- Room 5: "Error: ObjectOff: invalid object specified" at load; the debug jump
  skips state the room script expects.

A --startr debug jump leaves the player at the room's default position with
no input. No room of the 4 gave A != B under the break. The budget is spent and
was not extended. Result: fallback (b). tests/ratchet.yaml adds the
deterministic title row (gate-shards-fixed /
screen-shards-alias-512x384-fixed40k) quarantined, information only, "no
control by construction".

## The new row, validated on both flavours

`ratchet.sh --only screen-shards-alias-512x384-fixed40k`:
- instrumented: 20261105T030422Z. Staged binary 7e5dfe26f272. ok, 5 pairs, 0 problems, skips 0/0. PASS(q).
- release: 20261105T031423Z, with AGS_EXE set to an absolute path. Staged binary a1dba5d61624. ok, 5 pairs, 0 problems, skips 0/0. PASS(q).

A first release attempt, 20261105T031401Z, used a relative AGS_EXE. gate-alias runs from tests/harness, so run-dosbox.sh could not find the exe. That run is ERROR(q) with no frames. It was a harness invocation fault; set AGS_EXE to an absolute path.
