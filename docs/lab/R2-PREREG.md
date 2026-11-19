# R2 pre-registration (2026-11-06, before any R2 lab data): room 1's shortfall, R2+R3 forecast, and the spike cap on the GC fixture
Baseline, 486, R1 on: room 1 (loop ticks 5480-7890) runs ~94.5% displayed in release (GCB1/GCB2 presents per tick); GCMP
(instrumented, fine on) drawn-tick medians there: logic 16.18, render 4.10, scene 5.56 ms (ugo 26.49; p95 27.22).
Q1 (lab split, shares of a room-1 drawn tick, scored as shares): logic 58-64% (central 61), scene 19-23% (21), render 14-17%
(15). Character work = sc_prep_chars + character sprite blits + their bg restore: 3.5 ms central (band 2.5-5.0) of a
26.5 ms drawn tick. Falsifier: character work < 2.0 ms (13%), which would mean R2 is not room 1's lever.
Q2 (486 release, GC fixture, R1+R3+R2, no intrinsics): displayed central 97.8%, band 97.0-98.6%. Basis: R3 central 96.5%
leaves ~240 skips (LAB-L1B: ~125-130 in room 1, ~110 in room 2 entry/spikes/scroll); R2 at -1.5 ms or more per drawn tick
in room 1 leaves ~30-50 there.
Q2 falsifier (added on review, still before any R2 data): either release cell of the 486 round lands outside 97.0-98.6%.
Q3 (the cap): GCMP has 21 ticks of 40-250 ms in the fixture (clicks: Room::ProcessClick pathfinding, mean 33 ms, max 244;
plus the room-2 entry); recovering them at 25 - logic ms per catch-up tick costs 122-151 skips (1.8-2.2%) instrumented.
Predicted spike-attributable skips in release: 1.0-2.0% of ticks (central 1.4). So every per-tick lever together caps this
fixture at ~98.0-99.0% (central 98.4): 99% x2 is NOT expected on the GC fixture unless the spikes are cut.
Falsifier for Q3: a release cell measures spike-attributable skips < 1.0% (then per-tick levers alone could reach 99%).
