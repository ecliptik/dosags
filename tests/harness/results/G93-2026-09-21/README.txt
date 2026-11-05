G93 -- ags 0193 DOSBox-X gate (binary_sha12 8a02766376a0, build_dirty=0, oracle 727e2121fb43...).
summary.txt: 28 arm/rung rows + the AGS Quest whole run. 27 of 28 rows and the AGS Quest run read stale_frames=0; every
capture hash equals its baseline. The one FAIL is bench16 gui at the 16-bit centred-1x rung (see gui16-c1x-diagnosis.txt):
a defect in ags 0191's skip record, not in 0193's mechanism. The 8-bit gui rows show 52 presents only because the
unchanged-frame skip removes the rest.
Row labels in summary-raw.txt collapsed (a script variable bug); summary.txt has them restored from the fixed row order.
