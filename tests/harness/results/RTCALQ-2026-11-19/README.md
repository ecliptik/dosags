# RTCALQ -- DRIVE 6 short re-check on the 0383 release (pre-registration, before any data)
- Binary: rs0383.exe (the ags 0383 release, c6824107..., stamp f2e183845d2f). DRIVE6_MODE=calq, 13 presses, round RR's play line.
- Presses sent == planned (13) before the gate; gate: drive6-gate.sh --recheck against RJCAL-2026-11-11. PASS -> its values are used; any miss -> RTCAL runs in-round.
- Round RT (pre-registration: ROUNDRT-2026-11-19/README.md with FIX-UP 1 and 2, the rule; written 2026-11-19 before any data). One power-on, CAP_MIN 120. USB4VC firmware 0.5.109; pkt_partial / pkt_timeout / mouse.dropped and ev_in == pkt_built reported per cell; a partial voids an MS3 play cell from that press (rule M0).
