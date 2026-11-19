# LOCK0380-2026-11-13 -- landing records for ags 0380 (the heap's lock policy in play; both switches OFF by default)

DOSBox-X and build host only; nothing here touched the rig. Branch `lock0380` (worktree dosags-ring) on main cf801eb2
(round RP's results) + patches/ags/0380. Operator 2026-11-13 (via sdlports): turn move's lab patch 9001 into slot 0380
with an exit free-page sample, for review, after round RP; then pre-register an OFF / UNLOCK / PREGROW MS3 round.

## 1. The patch

- From lab patch 9001 (move, lab-rb ce5d138d move-lab/rj/lock/; LOCKSTUDY.txt), same mechanism, renamed out of "lab":
  dos_heap_policy() in Engine/main/game_start.cpp, once after "Starting game" (engine and SDL up, before the save restore /
  first room).
  - DOSAGS_HEAP_UNLOCK=1 (exactly "1"): clear _CRT0_FLAG_LOCK_MEMORY (the SDL_RunApp mirror AGS never runs).
  - DOSAGS_HEAP_PREGROW_KB=N (1..65536; else 0): keep LOCK, malloc(N KB) + free once.
  - Both unset: no flag change and no allocation; the cost is two getenvs and two 0500h host calls at the hook (~0.3 ms
    each on the 486), one 0500h call at exit, and the two log lines.
- New in 0380 (sdlports / move's (d)): the exit witness in RUNMANI.LOG, `DOS-PORT heappolicy_exit unlock= pregrow_kb=
  grown= crt0_flags= free_at_hook= hook_us= free_pages= phys_pages= unlocked_pages= paging_file_pages=` (0500h at exit),
  written next to 0377's voicering line. The hook's own line stays on the debug log (STDOUT).
- Both names join the env allowlist (quit.cpp), so each arm hashes differently (smoke: env_block_sha b8c440c1f606 /
  64096ec5e5c1 / c0ddf3f7a55d).
- TEMPORARY switches; the commit message states the removal: after the rig ABBA a later patch makes the chosen policy
  unconditional or reverts 0380 whole.
- Slots: 0374 (cap-3 lever) and 0375 (hitchdiag) stay reserved; 0380 is the next free.
- Provenance: patches/ags/0380 is `git format-patch` of the vendor commit; after `make patches` the vendor tree is
  2b568e7156b15c1cd7b42c86f21e7979da53f481, the committed patch's tree, and format-patch of the re-applied HEAD equals the
  file except the From line. ASCII only; no fopen.

## 2. Builds (two clean rounds; build/ags + build/ags-release wiped; make patches first)

| flavour | sha256 | stamp | bytes | vs 0379 | r1 == r2 |
|---|---|---|---|---|---|
| instrumented | 650bab1f26b15b316ff584823f249f2c4eaeb160176e7059d4d84c233766cd31 | 38d8ca231bf7 | 8,709,077 | +1,376 (e5623c99f752, 8,707,701) | yes |
| release (DOSAGS_RELEASE=1) | 0e6637f41c3a2a722349c9c2cd863b82090283683ac369baecb9dd91801d13ca | b66bd61cb1df (printed by the smoke cells) | 8,670,423 | +864 (d5c8fe52808a, 8,669,559) | yes |

`make build-dirty`: 0. BUILDS.txt has the build log's summary.

## 3. Lab smoke (DOSBox-X, the 0380 release, AGS Quest on round RP's registered reference line, live SB)

| cell | env | heappolicy (hook) | heappolicy_exit free / phys / unlocked / paging_file pages | exit | AutoPilot ok | pcm_irqs / ur / ow / silent | voicering |
|---|---|---|---|---|---|---|---|
| LKOFF | none | flags 0x1080->0x1080, free 9596->9596, us 3 | 6,972 / 11,916 / 11,916 / 32,768 | 0 | 18 | 180 / 0 / 0 / 0 | 2 / 55,532 / 169,344 |
| LKUNL | DOSAGS_HEAP_UNLOCK=1 | flags 0x1080->0x80, free 9596->9596, us 3 | 7,167 / 11,916 / 11,916 / 32,768 | 0 | 18 | 180 / 0 / 0 / 0 | 2 / 55,532 / 169,344 |
| LKPRE | DOSAGS_HEAP_PREGROW_KB=6144 | flags kept, free 9596->8044 (-1,552), grown 1, us 4,719 | 7,020 / 11,916 / 11,916 / 32,768 | 0 | 18 | 181 / 0 / 0 / 0 | 2 / 55,532 / 169,344 |

- The switches do what the lab patch did: UNLOCK clears 0x1000; PREGROW 6,144 KB commits 1,552 pages at the hook, as in
  move's MS3 lab arm. UNLOCK ends with 195 more free pages than OFF (lazy commits; MS3 lab: ~264).
- On AGS Quest the heap grows past 6 MB (PREGROW exit free 7,020 < 8,044 at the hook): the pre-grow size is per fixture,
  as move warned; MS3's 6,144 KB came from MS3's own growth.
- Witness caveats for the rig pre-reg: under CWSDPMI, unlocked_pages read equal to phys_pages here and paging_file_pages is
  the swap partition's size (32,768 = 128 MB), not its use -- so the pageability witness is the swap FILE's size before /
  after (`DIR C:\ /A`, as round RM) plus free_pages, not these two fields.

## 4. Ratchet

`.sdl-dos-ports/shared/tools/ratchet.sh --root <lock0380> --no-build --no-host-wait --capture-display 398 --no-record`.

| run | result |
|---|---|
| 20261113T101728Z | FAIL: 38 pass (10 improved), 3 fail, 4 quarantined -- exe-bytes 8709077 > 8707701 and code-lock-bytes 5229440 > 5228512 (0380's code, expected), and screen-bench8-alias-512x384-anim12 (1 problem in 4 pairs) |
| 20261113T112153Z (`--only screen-bench8-alias-512x384-anim12`) | PASS |
| proposed limits (exact; tests/ratchet.yaml LIMIT comment) | exe-bytes 8707701 -> 8709077 (+1,376), code-lock-bytes 5228512 -> 5229440 (+928) |

- The anim12 row's failure is an intermittent of the gate itself: with the switches unset 0380 changes no rendering code,
  it passed on the immediate re-run, and the same row failed in 2 earlier ratchet runs on other series (main
  20261104T212237Z; a nightly 20261101T103533Z) of ~122 reports found. shards-alias-512x384 (quarantined) failed as usual.

## 5. Not done here

- The OFF / UNLOCK / PREGROW MS3 rig round: pre-registered next, after sdlports reviews 0380. Power-on needs a fresh
  operator OK.

Files: BUILDS.txt, smoke/LK{OFF,UNL,PRE}/ (RUN.BAT, RUNMANI.LOG, STDOUT.TXT, AUTOPLT.LOG), RATCHET-*-report.txt.
