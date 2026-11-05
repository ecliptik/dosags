One run at the known-bad configuration (ags 0195 + DOSAGS_BREAK_0193=1, bench8 anim12 at Mode 13h, alias ON) with midshot=1, frozen at
tick 520 (FRZ00) while the emulated screen was photographed; the engine's own frame at mid-run is PH02.BMP.
  mech-broken.png : left = the engine frame (PH02, the COMPLETE room), right = the emulated screen at the freeze (background missing).
  mech-fixed.png  : the same without the control knob: screen complete.
  non-black fraction: engine frame 1.000 in both; emulated screen 0.152 (broken) vs 0.599 (fixed).
So at the known-bad configuration the ENGINE drew the background into its frame; the loss is between what the engine pushes and what
reaches the screen.
sdl-trace-mode-and-fbcreate.txt: the SDL trace of a second such run (DOS_PORT_LOG=1): one framebuffer creation at flush 0, mode sets #1
and #2 at start, mode-set #3 only at shutdown. Nothing resets the display mid-run in this fixture.
