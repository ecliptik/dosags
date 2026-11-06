# VM3A1 -- VM slice 3 (superinstructions) on the 486, MMD character select ABBA cell 1 of 4 (VM3A1 VM3B1 VM3B2 VM3A2), arm A legacy (written 2026-11-06; pre-registration, before any data)
- Binary: VM3REL.EXE = lab release build of vm-slice3.diff, stamp 1781fe2bf36c, build_dirty=1 (lab binary), 8,636,327 B,
  sha256 0ade9355a9bb...; VOID if a cell's stamp/sha differs. A and B are the same file; the arm is the env only (fast = all six superops).
- Fixture: F1MMDK's line verbatim (as round F1b's VMABBA) + --env DOSAGS_VM=legacy (A) / =fast (B); BLASTER.TXT and
  env_block_sha (differs A vs B) witnesses as F1b. Scorer: gatebar.py --label MMD --stamp 1781fe2bf36c --room 50 per cell.
- Basis: F1b on the 486: fast (slice 2) 86.94% displayed, logic excl. render 17.44, render pass 9.04 (6.39 + 2.65);
  model displayed = (25 - logic)/pass gave 83.6% for F1b (3 points pessimistic). Slice 3 at fixed 40k: 5.124 -> 4.308 ms/tick
  (-16% of the VM's time); on the 486 assumed the same share of F1b's 12.70 ms script_vm: -1.7 to -2.4 ms.
- Prediction A: as F1b's legacy arm (26.7% displayed, steady 36.5): 20-35%, steady 35.0-37.5.
- Prediction B: logic 15.0-15.7 -> displayed 95-100% (central 99%), steady 39.2-40.8, fps_p50 38-40.
- GAIN (vs slice 2): both B >= 90% displayed and steady >= 39.2. MET (the campaign line): both B >= 99.0%.
- FALSIFIER (the 486's cache/CPI erases the superinstructions): either B < 88% displayed (no better than slice 2's 86.94%
  beyond noise). The hot loop grew 4.4 -> 6.7 KB (all handlers; hot paths 2.5 -> 5.4 KB): that is the named suspect.
- Lab worktree ~/git/dosags-lab-vm, patch vm-slice3.diff; docs/lab/VM-SLICE3.md. build_dirty=1: figures read from the manifests (gatebar VOIDs dirty).
- Round E (PLAN-FPS lever V slice 3): WARMUPE, VM3A1, VM3B1, VM3B2, VM3A2, VM3S16; one power-on, cap 85 min; dated 2026-11-06, else re-dated first.
