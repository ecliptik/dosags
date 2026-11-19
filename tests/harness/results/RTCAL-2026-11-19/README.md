# RTCAL -- DRIVE 6 full calibration on the 0383 release, only on an RTCALQ miss (pre-registration, before any data)
- Binary: rs0383.exe (stamp f2e183845d2f). DRIVE6_MODE=cal, round RR's play line; gate drive6-gate.sh --no-recentre. No PASS -> no play cell this power-on.
- Round RT (pre-registration: ROUNDRT-2026-11-19/README.md with FIX-UP 1 and 2, the rule; written 2026-11-19 before any data). One power-on, CAP_MIN 120. USB4VC firmware 0.5.109; pkt_partial / pkt_timeout / mouse.dropped and ev_in == pkt_built reported per cell; a partial voids an MS3 play cell from that press (rule M0).
