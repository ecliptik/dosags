# R2 whole-fixture forecast (2026-11-07, before any R2 lever is built or measured; after round RC)
Baseline, 486, main 9e54b6d9 (R3 default), GC fixture, release: RCB1 / RCB2 98.43 / 98.24% displayed (110 / 123 of 7,003 skipped).
Per window (persec renders/ticks): room 1 5480-7890 skipped 79 / 75 (96.71 / 96.86%); room-2 entry 7890-8400 8 / 21; room 2
8400-9500 0 / 0; late 9500-end 15 / 19; the save-restore start 5437-5441 ~5. Room 1 holds ~6 clicks (each <= 5 skips after
MAX_CATCHUP, LAB-R2 Q3): ~25-30 of its skips are spike-bound, ~45-50 budget-bound (a drawn room-1 tick ~26.5 ms vs 25).
R2 (LAB-R2 design R2a + R2b, exact): 486 saving per room-1 drawn tick central 5.5 ms, band 3.5-6.5 -> room 1 under budget.
F1 (target, room 1): R2 cells' room-1 skips 20-40 (central 30), i.e. room 1 98.3-99.2% (central 98.8). Falsifier: either R2
cell's room-1 skips > 50, or less than 25 fewer than its same-binary R3-only arm (DOSAGS env toggle, ABBA) in that window.
F2 (whole fixture): R2 cells 98.9-99.5% displayed (central 99.1; 35-77 skips). Falsifier: either R2 cell < 98.6%, or
mean(R2) - mean(R3-only) < +0.5 points. 99% x2 is ON THE EDGE of this band, not claimed.
F3 (mechanism check, per room): entry, room 2 and late windows each within +-10 skips of the R3-only arm (R2 is room-1
characters; room 2's characters move less but R2 is exact there too); a > 10-skip gain there is a finding, a loss falsifies.
Rig shape when the lever exists: same-binary ABBA x1 on the GC fixture (R3-only vs R2) + one instrumented cell; S16 guard.
