# F1MMDP -- Maniac Mansion Deluxe character select, PROFILE (probe 0306), round F1a (written 2026-11-06; pre-registration, before any data)
- Binary: probe 0306 v9 on main a746d522 (~/git/dosags-lab-prof build/lab-prof/prof/ags.exe, sha256 5bfa27cae98b..., stamp 770a7ba9e60f,
  build_dirty=1 by construction; instrumented). A PROFILE cell: attribution only, never a rate figure. Sound OFF (the probe hangs at
  the first SDL_Delay with sound on; lab-prof finding), so the profile is logic + render without the audio cost.
- Fixture: F1MMDK's line but ACSETUP-OFF-512X384-ROUND.CFG (sound off), fine timing ON (DOSAGS_TICKSTATS_FINE=1), DOSAGS_TICKLOG=5200,
  DOSAGS_PROF=1024, --collect TICKS.BIN --collect PROF.BIN.
- Readers (committed 63d351d2): f1/f1prof.py F1MMDP --lo 40 --hi 4999 (per-phase ms/tick, TICKS.BIN logic/render/scene/ugo);
  f1/s8name.py --prof F1MMDP --exe <probe exe> F1MMDP (per-tick split, per-function samples); f1/prof.py (ccInstance::Run by SCMD block).
- VOID: stamp != 770a7ba9e60f; exit != 0; no PROF.BIN or TICKS.BIN; PROF.BIN dropped > 0 or samples outside .text; room != 50;
  a "DOS audio device opened" line (sound must be off).
- Questions it answers: render ms per pass (measured, replacing the <= ~15 ms upper bound), logic split (script VM vs events vs
  engine), the hot functions; checks the VM study's ~20 ms script-event figure on today's main.
- Witness: camera sheet; BLASTER line as F1MMDK.
- Round F1a (PLAN-FPS step 2): WARMUPF1, F1MMDK, F1MMDP, F17DK, F17DP, F1AQK; one power-on, cap 85 min; dated 2026-11-06, else re-dated first.
