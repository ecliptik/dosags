F2A1 -- anim12, Mode 13h, EXPORT binary + OLD fixture (the G2R2 configuration; A arm of the F2 ABBA). First real-hardware
cell of the witness runner.

Witness, as found: the capture card FROZE at Mode 13h. witness/frames holds 9 card frames of which 1 is unique (the first
game frame, spinner rows on black); the daemon's own state read "nosignal" (coordinator, 15:05). Only the camera saw the
game: 3 frames at the old ~30 s cadence (witness/camera/). Looked at by dosags-worker: 12 spinners in two rows at different
rotation phases in the three frames, the player, the key and the cursor, no duplicated sprites -- clean. That is a lesser
witness than the standing order asks for (3 frames, not one per <= 8 s), so this cell has NO witness/REVIEWED.txt and its
figures are the A arm of an ABBA, not a claim. The runner was changed afterwards (8 s cadence, camera every pass, a
capture-card state log every ~2 s, camera-only review accepted only when the manifest records a frozen card).

CORRECTION, 2026-09-21 (dosags-worker, in place): the paragraph above calls the three camera frames "clean". THAT WAS WRONG.
The room's background (brick wall, window, pillar, sign, floor) is missing on the physical screen: black, with small lit
patches around the spinners only. I read the missing background as low camera exposure. The coordinator's camera frames
(lit fraction 0.13, identical layout at 15:05:00 / 15:05:33 / 15:06:06) and F2B1's frames (the complete room, lit
fraction 0.51) show it plainly. F2A1's rate is VOID. See PLAN.md step 1, "F2A1 IS VOID".
