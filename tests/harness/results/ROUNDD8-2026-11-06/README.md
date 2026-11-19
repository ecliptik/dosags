# Round D8 -- 2026-11-06: rebuilt C:\DOSAGS -> S16 / S32P / S8 all MET (start-up 824 / 648 / 650 ms); MMD in play is logic + sprite bound

One power-on 18:28:49Z-19:21:24Z (driver exit 0; powerguard confirmed OFF 19:21:32Z), cap 19:53:49Z not reached. Operator: "Ok" to
moving the logs; copy-verify-delete rebuild approved via vcctrl; "We need to improve MMD framerate" / "Keep going to improve MMD fps".
Pre-registrations 405d5177 + amendments f98d61f0 (rebuild instead of move-only) and 88f3b724 (D8MP), all before data. Every cell
exit 0, stamp OK, pre = staged = post; BLASTER.TXT "A220 I7 D3 P330 T3" in all five. Gateway off ~20 s before relay-on.

| Cell | binary | whole / steady | fps_p50 | displayed | preloop ms | witness | verdict |
|---|---|---|---|---|---|---|---|
| WARMUPD8 | l308 | 30.52 / 33.15 | -- | -- | 1,228 | nolock | C:\DOSAGS 60 entries (fresh), OLDLOG 664, DOSAGSO 58 |
| D8S16 | rel c754df64babd | 39.30 / 40.08 | 40.00 | 99.48% (26) | 824 | camera CLEAN | **MET** |
| D8S32 | rel | 39.40 / 40.17 | 40.00 | 99.52% (24) | 648 | capture CLEAN | **MET** |
| D8S8 | rel | 39.37 / 40.23 | 40.00 | 99.28% (36) | 650 | camera CLEAN (dark) | **MET** |
| D8MP | instr f3a8774e03c8 | -- / 39.77 | 21.87 | 53.2% (3,279 of 7,003; profile overhead) | -- | camera: kids walk 1 -> 2 | PROFILE |

- Directory lead (registered): preloop <= 700 in 2 of 3 (S32P 648, S8 650; S16 824); falsifier (>= 850 in two) NOT tripped. All
  three whole-run figures back in band (V1: 39.18 / 39.13 misses). Mixed, not clean: S16 barely moved and P9S16 (cluttered, 796)
  disagrees -- start-up also varies run to run. Off-time (B) does not fit (D8 had ~20 s off). Practical: keep C:\DOSAGS small.
- D8MP, MMD in play on the 486 (f1prof.py: F1PROF.txt whole run, F1PROF-room1.txt): script_vm 12.39 ms/tick (as the character
  select), logic excl. wait 17.26 ms/tick; per drawn frame render_to_screen 9.71 ms (sprite draws 2.66 ms x 3 = ~8.0) + scene
  4.73 (sc_room_view 3.89); present_update_window only 0.86 ms. TICKS.BIN medians over all 4,685 room-2 window ticks (just over half
  are drawn, so render/scene medians sit on drawn ticks): logic 17.65 + render 8.22 + scene 3.96 (~30 ms vs 25) -> every other tick drawn. Registered (R) "render/present-bound" FALSIFIED (script_vm + dispatch >
  render); (S) script-bound holds with render a strong second; (C) clicks: not the cause (ugo > 25 ms on 2,551 of 4,685 room-2
  ticks, far beyond 21 clicks).
- Rig (vcctrl): 2 corrupt capture frames (18:53:04.4Z in D8S32, off its sheet; 19:14:15.6Z in D8MP), no USB event, no recovery.

Files: SUMMARY.txt, driveD8.sh / cellD8.sh / powerguard.sh / daemongap.sh / expected.txt / ORDER-CONFIRMED, POWERGUARD.txt,
jobs/*.json, GATEBAR.txt per gate cell, D8MP/F1PROF*.txt. Captures and saves stay local (AUDIO-SHA256.txt, SAVE-SHA256.txt).
