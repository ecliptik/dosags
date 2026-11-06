# Round F1a (PLAN-FPS step 2) -- 2026-11-06: where each game's 25 ms tick goes on the 486

One power-on 00:00:54Z-01:15:38Z (driver; powerguard confirmed), cap 01:25:54Z. Operator's standing order
(ORDER-CONFIRMED). Pre-registrations 2079a101, readers 63d351d2, gatebar amendment c08f8dc4. KPI cells: release
a1dba5d61624 (sound on); PROFILE cells: probe 0306 v9 770a7ba9e60f (build_dirty=1, sound off, fine timing on, PROF.BIN +
TICKS.BIN). Every cell exit 0, stamp matched, BLASTER "A220 I7 D3 P330 T3". First round on vcctrl 1e5a1e7's transfer BATs:
every send ok, every pull delivered its files, no password text in any job log, reboot witness "ready-prompt". vcctrl: no
USB event, 0 decode errors, the audio stream never restarted.

## KPI (release, sound on)

| Cell | Scene | steady | fps_p50 | displayed (1 - fs/ticks) | verdict |
|---|---|---|---|---|---|
| F1MMDK | MMD character select, room 50, idle | 35.76 | 9.94 | **27.77%** (3,611 of 4,999 skipped) | NOT MET (as MABSP: 25%) |
| F17DK | 7 Days room 2, walking (save restore + engine clicks) | 39.99 | 40.00 | **99.48%** (f1persec: renders/ticks 99.66%, real/renders 100%) | **MET** (restore cell: whole-run and gatebar's presents are restore artefacts, as registered) |
| F1AQK | AGS Quest AutoPilot, rooms 1-4 | 41.09 | 39.49 | 93.04% | NOT MET; stall_ms 89,926 (whole-run 19.79) |

## PROFILE (probe, sound off; GATEBAR/F1PROF/PROF/S8NAME .txt in each dir)

**MMD character select (F1MMDP), ms per game tick:** update_game_once 28.16 = process_events_dispatch 21.88 (of it
**script_vm 20.47**, 10,003 calls) + game_objects_update 1.11 + drawable states 0.69 + input 0.77 + GUI cursor 0.43 + ...;
render_to_screen **6.71 ms per pass** (render_backbuffer 5.45) + scene_construct **2.84 per pass** -- a frame costs ~9.5 ms
(the earlier "<= ~15 ms" was an upper bound). Every tick is over 25 ms (TICKS.BIN: logic median 25.33, p95 35.07).
Samples: script event 71.8%, logic non-script 17.9%, render/scene 9.2%. Inside the script event, **Run:head/prologue
31.5%** (dispatch overhead), then SCMD_LITTOREG 6.6, SUB 5.5, LOOPCHECKOFF 4.2, POPREG 4.1, CALLEXT 3.6, PUSHREG 3.0, CALL
3.0. Non-script logic: __wrap_uclock 8.0% (timer reads, ~0.5 ms/tick), update_character_scale 6.2, character
move/animate/follow ~15. Render: _linear_draw_sprite16 51%.
**Reading:** the script VM is the wall. At 1.82x (lab slice 2, fixed 40k) logic would be ~16 ms + one frame 9.5 ms --
close to, not inside, 25 ms; the superinstructions (slice 3) and the sprite blitter are the next levers.

**7 Days room 2 (F17DP):** update_game_once 24.94 ms/tick of which **wait_next_frame 13.44 (idle)**; busy 11.50 = logic
6.08 + scene 3.36 + render 2.06; script_vm only 1.27. Samples: 80% of "non-script logic" is the frame wait itself. Plenty
of headroom: an ordinary in-play room is not VM-bound.

## Reading for PLAN-FPS

- MMD is a script-VM wall (lever V); 7 Days in play is already at 40 fps / 99.5%.
- AGS Quest loses its frames to blocking ticks (~90 s of stalls over the run) -- a stall/load question, target (b)/(d).
- Shards and Iowna: no fixture (packages lack audio.vox). Not measured.

Files: SUMMARY.txt, driver and helpers, ORDER-CONFIRMED, POWERGUARD.txt, jobs/*.json. PROF.BIN (~0.6 MB) and TICKS.BIN are
kept with their cells (our own profiler output). Captures and saves stay local (AUDIO-SHA256.txt / SAVE-SHA256.txt).

## F1AQK images (operator 2026-11-05, AGS Quest licence: no rendered frame is committed)

AGS Quest's art is CC BY-NC-ND and our package is a retarget (tests/harness/packages/agsquest/LICENSE-NOTES.md: "No
screenshot of this package's rendered content is ever committed"). F1AQK's PH01-03.BMP, WITNESS-*.jpg and witness
sheets stay on disk, untracked; their sha256 are in F1AQK-2026-11-06/IMAGE-SHA256.txt. Witness verdict (capture locked,
640x480; reviewed 2026-11-06): the AutoPilot crosses the forest and treehouse rooms, characters move between frames, the
game's text boxes and GUI draw; frame #11 shows a part-drawn screen (the treehouse above, help text over black below)
during a GUI transition -- recorded as observed, not judged a trail; F1AQK is a room-crossing baseline, not a claim.
