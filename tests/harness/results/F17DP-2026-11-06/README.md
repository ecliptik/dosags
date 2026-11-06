# F17DP -- 7 Days a Skeptic room 2, PROFILE (probe 0306), round F1a (written 2026-11-06; pre-registration, before any data)
- Binary: probe 0306 v9 on main a746d522 (~/git/dosags-lab-prof build/lab-prof/prof/ags.exe, sha256 5bfa27cae98b..., stamp 770a7ba9e60f,
  build_dirty=1 by construction; instrumented). A PROFILE cell: attribution only, never a rate figure. Sound OFF (the probe hangs at
  the first SDL_Delay with sound on; lab-prof finding), so the profile is logic + render without the audio cost.
- Fixture: F17DK's line but ACSETUP-OFF-512X384-ROUND.CFG, fine timing ON, DOSAGS_TICKLOG=12200, DOSAGS_PROF=1024,
  --collect TICKS.BIN --collect PROF.BIN.
- Readers: f1/f1prof.py F17DP --lo 7263 --hi 12149; f1/s8name.py --prof; f1/prof.py over the same tick window.
- VOID: as F1MMDP, room != 2. Witness: camera sheet; BLASTER line.
- Questions: per-phase split of an in-play walking room on the 486 (logic / render / scene), the hot functions.
- Round F1a (PLAN-FPS step 2): WARMUPF1, F1MMDK, F1MMDP, F17DK, F17DP, F1AQK; one power-on, cap 85 min; dated 2026-11-06, else re-dated first.
