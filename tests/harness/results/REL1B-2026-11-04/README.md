# REL1B -- PLAN-NEXT step 1b (AUDIOPRB retirement) and ags 0354, 2026-11-04

DOSBox-X only. No real-hardware run; the Gateway stayed off.

## What landed

- ags 0352: retire the AUDIOPRB audio cost timers (engine half; -831 lines).
- ags 0353: release flavour skips the rb_max_spr_* update in ali3dsw.cpp.
- ags 0354: fflush + fsync stdout at every room entry (DJGPP only).
- SDL 0269: retire the AUDIOPRB OPL3/GUS timings (SDL half; -434 lines,
  pure deletion; the GUS_DIAG ring stays).

Both flavours carry all four.

## Gating runs (full ratchet, --no-build, display 211)

| flavour      | binary_sha12 | exe bytes | ratchet run       | result                    |
|--------------|--------------|-----------|-------------------|---------------------------|
| instrumented | 7e5dfe26f272 | 8,636,055 | 20261105T000223Z  | 41 pass (12 improved), 0 fail, 3 quarantined |
| release      | a1dba5d61624 | 8,598,425 | 20261105T005648Z  | 41 pass (12 improved), 0 fail, 3 quarantined |

Release run used AGS_EXE=build/ags-release/ags.exe. Each run's
binary_sha12 was checked in its report tree (6 hits each, one stamp).

code-lock-bytes: instrumented 5,175,008, release 5,144,064.

lost-inputs first-click start (journeys.py click_start_ms, bound 30000):
instrumented 8664 / 9627 ms, release 9347 / 9579 ms. lost_inputs 0 on both.
The ratchet prints "SHOULD QUARANTINE (flaky: 3 non-pass in last 10)" for
lost-inputs; the three non-passes are the pre-0354 release runs below,
whose cause is found and fixed. Not quarantined.

The quarantined screen-shards-alias-512x384 row FAILed on both runs as
before (full speed, non-deterministic; release run also VOIDed FRZ00 on a
100/101 freeze-tick mismatch). It is never gating.

## Interim runs (pre-0354, superseded)

- 20261104T212237Z (instrumented, 1b only): bench8-alias-512x384-anim12
  A!=B once. Re-run clean on both flavours (5 pairs, 0 problems).
  Reported, not excused; it did not recur in the gating runs.
- 20261104T221555Z, 20261104T231553Z, 20261104T232804Z (release, 1b only):
  lost-inputs 18 / 18 / 3. The instrumented flavour on the same series lost
  0 (20261104T231000Z, 20261104T232212Z). Cause: DOSBox-X buffers a
  mounted-drive host file until the guest commits it (INT 21h AH=68h); the
  release build writes less to stdout, so the host saw the room's
  load_end late and the host clicker started 36-109 s after the room
  loaded (instrumented: 16.5-17.6 s). Not a 1b effect. Fixed by ags 0354
  (commit at room entry) plus the journeys.py late-start guard (VOID when
  the first click is more than 30 s after load_end). With 0354:
  20261104T234308Z and 20261104T234859Z (dirty build 947db322b9da),
  lost 0/0, first click at engine t=8.8 s.

## AUDIOPRB reader check

No code reads AUDIOPRB output. git grep over *.py *.sh *.yaml Makefile
(results excluded) finds only prose: tests/ratchet.yaml:501,
tests/games/trilbysnotes/manifest.yaml:172-184, tests/harness/run-hw.sh:981
(all comments / descriptions). The lab/wb scorers
(archive/lab-wb-2026-11-04, capture-check.py, capture-check3.py,
gatebar.py) have 0 hits.

## Real-hardware note

0354 adds a commit at the S8 fixture's only room load, which is in the
pre-loop; whole-run tick_rate drops by ~39.26 x C / 127400 for a commit of
C ms. See PLAN-NEXT.md step 4 (R1). Not measured on the 486 yet.
