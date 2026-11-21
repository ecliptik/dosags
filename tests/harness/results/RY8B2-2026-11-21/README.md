# RY8B2 -- Trilby's Notes S8 (room 35, 8-bit, msgskip) at the 640x480 2x rung, SCALE2-NARROW on S2NR (written 2026-11-21; round RY; pre-registration, before any data)
- Binary: s2nr.exe = S2NR.EXE, LAB2X gate3's exe (sha256 9599809419c8...; stamp f42436aadd7b, build_dirty=1 accepted only
  with pre-stage = post-run = that sha256). Round RY README sec. 1. VOID otherwise.
- Witness: RV's six default STDOUT lines and BLASTER "A220 I7 D3 P330 T3" (README sec. 5); else VOID.
- Fixture: RV8A's scene line at the 640x480 2x rung: S32P-ACSETUP-ON.CFG (24d874f2...), DOSAGS_MAX_SCALE=2,
  DOSAGS_SCALE2_NARROW=1, DOSAGS_MSGSKIP=1. Witness: the scale2 line on=1 break=0 verify=0, render dest (0, 0, 639, 479 : 640 x 480).
- Bar (owner 01M7XPBAR870HGWWG15X2AAXRV, "Same bar, new rung"): PLAN-GATES' numbers unchanged at 640x480 integer 2x;
  99% displayed is the REGRESSION line. Read by tests/harness/ry-read.py: MET / NOT MET / PATH-OFF (narrow share
  < 95%, not MET) / VOID.
- Screen witness: the capture stick. A stick drop in the play window (card-state.log or the kernel slice keyed to
  idVendor=0001 idProduct=ff02) VOIDS the cell; a missing record is VOID. No camera fallback (decision 01M7X8X4).
- Prediction (information, against RV's A readings, cross-day): steady 40.0-40.3, fps_p50 40.00, whole-run 39.12-39.28, displayed RV - 0.3..1.5 pp.
- With RY8B1 this is the depth's registered pair on the overlay build S2NR; no release claim (README sec. 8).
