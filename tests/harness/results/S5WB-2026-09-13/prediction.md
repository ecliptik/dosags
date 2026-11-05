# S5WB2 pre-registered band prediction (written before seeing poll results)

Tune source: tests/harness/packages/agsquest/overlay/assets/generate_assets.py
Raw MIDI notes (no OPL3-style transpose -- waveblaster_sink is a pure byte
pass-through): melody = [60, 62, 64, 65, 67, 65, 64, 60] = C4 D4 E4 F4 G4 F4 E4 C4
GM program 80 (Lead 1, square) on channel 0.

Fundamental frequencies:
  C4 = 261.63 Hz
  D4 = 293.66 Hz
  E4 = 329.63 Hz
  F4 = 349.23 Hz
  G4 = 392.00 Hz

vcctrl 8 fixed octave bands (Hz, lower edge): 100,200,400,800,1600,3200,6400,12800
  band 0: 100-200
  band 1: 200-400   <-- ALL FIVE fundamentals land here (261.6-392.0 Hz)
  band 2: 400-800
  band 3: 800-1600

Prediction: unlike S4's OPL3 result (which split C3 into band 0 and
D3/E3/F3/G3 into band 1, because of DMXOPL's GM-program-80 -12 semitone
transpose), this melody's RAW notes never leave band 1 -- there is no
transpose in waveblaster_sink. Expect band 1 to dominate for the ENTIRE
tune window, not split across two bands. A real GM "Lead 1 (square)"
timbre is harmonically rich (square-wave-like), so secondary energy in
band 2 (400-800Hz, ~2nd-3rd harmonic) and possibly band 3 is plausible
and would NOT contradict this prediction -- but band 1 should be the
clear, sustained peak throughout, clearly separated from the ~-67 to
-85dB ambient floor S2/S4 already established on this exact rig/profile.

Ambient floor just confirmed live (pre-run): mean_db -67.17dB, band_db
all -76 to -86dB, active_bands=0 -- matches precedent.

If instead the capture shows dispatch evidence (RUNMANIFEST midi=wb,
events>0) but NO spectral departure from ambient anywhere in the run,
that is the audio-ROUTING-not-mixed-in signature flagged earlier
(PicoGUS's own WB-header audio return may need an unmute/mixer step
analogous to VIBRA profile's MIXERSET.EXE, never documented for PGSB) --
not a backend/dispatch failure.
