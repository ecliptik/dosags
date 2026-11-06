# VMB1 -- VM fast loop on the 486, MMD character select ABBA cell 2 of 4 (VMA1 VMB1 VMB2 VMA2), arm B fast (written 2026-11-06; pre-registration, before any data)
- Binary: VMREL.EXE = lab release build of vm-slice2.diff (+ handler table), stamp c044ae62df3f, build_dirty=1 (lab binary, by design),
  8,631,643 B, sha256 86b57787...; VOID if a cell's staged stamp/sha differs. A and B are the SAME file; the arm is the env only.
- Fixture: F1MMDK's line verbatim (run-hw mmd, ACSETUP-ON-512X384-ROUND.CFG:ACSETUP.CFG, direct framebuffer, TAS 5000, --no-fine-timing,
  drive none, room 50 idle, PGSB, MIN_WAIT 270, --timeout 1800, BLASTER line) + --env DOSAGS_VM=legacy (A) or =fast (B).
  Witness: BLASTER.TXT "A220 I7 D3 P330 T3"; RUNMANIFEST env_block_sha must differ A vs B (DOSAGS_VM is allowlisted), else VOID.
- Scorer: gatebar.py --label MMD --stamp c044ae62df3f --room 50 per cell; frames displayed = 1 - frames_skipped/ticks.
- Prediction A (legacy): as F1MMDK (27.8% displayed, steady 35.76): displayed 20-35%, steady 35.0-37.0.
- Prediction B (fast): logic 25.3 -> 14.6-18.1 ms/tick (VM 1.7-2.6x on ~17.4 ms), one pass 9.5 ms: displayed 70-100% (central ~93%),
  steady 39.2-40.8, fps_p50 28-40. 99% displayed needs logic <= ~15.5: inside the band only at its fast end.
- GAIN if min(B1,B2) - max(A1,A2) >= +35 points displayed and both B steady >= 39.2. Audio counters clean in all four, else VOID.
- FALSIFIER (the 486's CPI erases the gain): min(B) displayed < 50% (= VM speedup < ~1.4x), or min(B) - max(A) < 10 points (erased).
- Lab worktree ~/git/dosags-lab-vm, patch vm-slice2b.diff (slice 1 + 2 + handler table); docs/lab/VM-SLICE2.md. Scored as a set: VMA1 VMB1 VMB2 VMA2.
- Round F1b (PLAN-FPS lever V, slice 2 on the 486): WARMUPF1B, VMA1, VMB1, VMB2, VMA2, VMPROF; one power-on, cap 80 min; dated 2026-11-06, else re-dated first.
