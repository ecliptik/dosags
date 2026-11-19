# D8S32 -- 5 Days S32P (32-bit 640x480) after the log move and directory rebuild (written 2026-11-06; pre-registration, before any data)
- Binary: D8REL.EXE = the v0.1 exe (release c754df64babd, sha256 d680e3b6...); defaults witnessed in STDOUT; BLASTER.TXT, else VOID.
- Fixture: GR32P's line verbatim (as N7S32 / V1S32).
- Question: does start-up (RUNMANIFEST preloop_ms) fall once C:\DOSAGS is a fresh ~60-entry directory instead of 716? Lead: DOS directory
  lookups scan every entry; the 716-entry directory (~45 sectors) may no longer fit DOS's buffers. V1: preloop 1,004 ms, whole-run 39.18 NOT MET (N7 864, 39.26).
- Prediction: preloop_ms <= 700 (central ~620, the 11-05 level); whole-run 39.25-39.35; displayed and steady as N7/V1.
- FALSIFIER (lead wrong): preloop_ms >= 850 in two or more of D8S16 / D8S32 / D8S8.
- Bar (PLAN-GATES, unchanged): both tick figures 39.2-40.8, fps_p50 >= 40, completeness >= 95%, witness clean, audio clean.
- Witness: the capture sheet (640x480 locks) or the camera.
- Round D8 (operator 2026-11-06 "Ok" to moving the collected logs): WARMUPD8, D8S16, D8S32, D8S8, D8MP; one power-on, cap 85 min (D8MP added before data); dated 2026-11-06.
