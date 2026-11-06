# What is left of MMD's tick on the 486 outside the VM, and what each piece could give (desk read, 2026-11-06)

Sources: F1MMDP (round F1a, probe 0306 on main = legacy VM, fine timing on, sound off: 1024 Hz samples, window ticks 40-4999,
143,524 samples = 28.3 ms/tick), VMPROF (round F1b, slice 2 fast, fine on, sound off: tickstats), round E (slice 3 release,
sound on: 91.54% displayed). Model (fits F1b and E): displayed = (25 - logic)/pass + 0.033, pass = 9.04 ms.

## Where today's (slice 3, release) 25 ms tick goes, estimated
- logic ~17.0 ms/tick (F1b's 17.44 - ~0.4 from E's gain), of which
  - script event ~12.3: the interpreter (Run) ~7.6 and engine API calls made from scripts ~4.7. F1a: 23% of the script event's
    samples (4.7 of 20.3 ms) are outside Run; the API side did not get faster with the VM work.
  - non-script logic ~4.7 (VMPROF: 17.44 - 12.70): character updates ~1.24 (F1a: update_character_scale 6.2%,
    FixupCharacterLoopAndFrame 5.0, UpdateCharacterMoveAndAnim 4.6, Follower 4.2, Animating/Moving/Idle 4.6 of this bucket),
    uclock ~0.40 (8.0%; fine-timing brackets included), UpdateGameOnce itself 0.21, GetCharIDAtRoom 0.17, input ~0.72,
    gui_context_cursor 0.38, rep_exec wrapper 0.40, drawable states/objects_scale ~1.2 (VMPROF), malloc/free/SDL events ~0.3.
- render ~8.3 ms/tick = 0.915 passes x 9.04: render_to_screen 6.39 (sprite blits rb_sprite_time 5.06 -- _linear_draw_sprite16
  is 51% of all render/scene samples -- bg_restore 0.60, present 0.56) + scene 2.65 (room view 1.81, viewports 1.05).
- 99% displayed needs logic <= ~16.35 (-0.7 ms/tick) at today's pass, or pass <= ~8.33 (-0.71 ms/pass) at today's logic.

## Levers outside the VM, central estimates on the 486 (ms/tick of logic unless stated)
| # | lever | basis | central | risk / exactness |
|---|---|---|---|---|
| 1 | Character update early-outs: an idle character's scale/loop/frame fixups re-run every tick (update_character_scale, FixupCharacterLoopAndFrame) | 1.24 ms/tick of character work in F1a | -0.40 | medium: needs a proof per field that inputs are unchanged |
| 2 | GetCharIDAtRoom: the same (x,y) hit test runs several times a tick (GetLocationName / GetLocationType x2 / engine) | 0.41 in the script event + 0.17 in logic | -0.25 | medium: invalidate on any character change within the tick |
| 3 | cc_has_error() out of line after every engine call (170/tick) + GetGUIAt | 0.14 + 0.18 in the script event | -0.12 | low: inline the flag read; exact |
| 4 | Formatting work: _doprnt is 1.1% of the script event + 1.3% of logic (~0.3 ms). Part is StrFormat (script-visible, must stay), part is debug_script_log formatting before its filter (debug.cpp:423-430) | ~0.3 | -0.10 | low, but the split must be counted first (the KPI fixture runs --log-stdout=+mgs:all, so some lines are real output) |
| 5 | uclock in the release flavour (fine timing off removes most of F1a's 0.4) | residual readers: pacer, audio, SDL timer | -0.05 | low; small |
| 6 | VM remainder (Run ~7.6): whatever round 4's cache test leaves room for (sourceline fusion, call/ret trimming) | slice 3 realized r ~0.5 of fixed-40k savings | -0.30 | medium; round 4 decides the shape |
| 7 | **Render: _linear_draw_sprite16** (~4.6 ms of the 9.04 pass): opaque-span copies for MMD's large, mostly opaque GUI sprites; skip re-compositing a GUI whose surface did not change | 5.06 ms/pass of sprite time | **-1.2 ms/pass** (~-1.1 ms/tick at 92% displayed) | medium-high: the class that produced trails before; the screen gate and present verifier guard it |
| 8 | Scene construct (sc_room_view 1.81, viewports 1.05 per pass) | 2.65 ms/pass | -0.3 ms/pass | medium |

## Verdict (arithmetic, not a measurement)
- Logic side: 1+2+3+4+5+6 central -1.2 ms/tick against the -0.7 needed; 1+2+3 alone (-0.77) reach it, all three engine work
  outside the VM, two of them medium-risk. Render side: 7 alone (-1.2/pass) reaches it.
- So 99% on MMD looks REACHABLE, not a wall, at central estimates -- but every row is a desk estimate from a legacy-VM,
  fine-timing-on profile (+-50%), and slice 3 just showed a 2-4x shortfall between a fixed-cycles estimate and the 486. The
  engine-side rows come from 486 samples directly (no fixed-cycles discount), which makes them firmer than the VM rows.
- Cheapest first: 3 (exact, small), then 1 and 2 (one probe-free count of calls/tick each in DOSBox-X), then 7 if logic stalls.
