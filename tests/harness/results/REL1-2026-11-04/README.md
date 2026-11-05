# REL1 -- PLAN-NEXT step 1: the DOSAGS_RELEASE flavour keeps the scorer contract (DOSBox-X, 2026-11-04)

LAB ONLY (DOSBox-X; no 486 figure here). The release exe's real-hardware audio and timing stay
OPEN until R1 runs (RELEASE ABBA on S8, CAPR8).

- Binaries, one commit (main + ags 0351; series fingerprint 3dcf01e8be00 after the message-only amend, 92715cb93495 when built -- same tree 6351fa96, same stamps), both build_dirty 0:
  instrumented `72126e58db4f` (build/ags/ags.exe, 8,670,630 B, sha256 f847957f...);
  release `b26f82d0ce64` (`make DOSAGS_RELEASE=1`, build/ags-release/ags.exe, 8,633,512 B,
  sha256 9cb0aebc...).
- Instrumented vs af3f0824499e (sha256 27a2f5e6..., the 0348-0350 landing binary):
  `cmp-instr-vs-af3f.txt`, 13 bytes at 32775-32778, 32798-32801, 32808-32811, 32818 -- the stamp's
  12 ASCII characters as four movl immediates at file offset 0x8000-0x8031, the fourth overlapping
  the third (last character + NUL). Nothing else differs.
- gatebar.py: cells XI8B / XR8B (`run-s8.sh`: GL8 line, Trilby room 35, fixed 40k OPL3 conf,
  --sb-live, MSGSKIP, TAS 5000, fixed timestep; no host drive). Full verdict on both, identical
  fields and structure (`gatebar-XI8B.txt`, `gatebar-XR8B.txt`); both NOT MET on fps_p50 ~21
  (fixed 40k cycles), identically. A first pair without --sb-live VOIDed both on "missing
  late_writes" (poll MIDI); see run-dosbox.sh's --sb-live note.
- capture-check.py (S8) and capture-check3.py (S16/S32P): each run twice on the SAME 486 capture
  with each flavour's manifest, so any output difference comes from the log. capture-check.py on
  CAPS8-seg01.ogg + XI8B / XR8B: PASS both, identical except K5 pcm_irqs 1756 / 1755; K1-K4
  reproduce CAPS8's recorded figures. capture-check3.py on CAPS16-seg01.ogg + XI16 / XR16
  (`run-5d.sh`: CAPS16 line, 5 Days room 3, S32P cfg 24d874f2, --sb-live): PASS both, identical
  except K5 pcm_irqs 516 / 308 (sound 3 played 2x / 3x, no fixed seed); M1 +1 cent as CAPS16.
  Scorers from lab/wb (archive/lab-wb-2026-11-04), references per tests/harness/REFERENCES.md.
- Ratchet: the release exe, AGS_EXE override (exe-bytes reads it since 63b97d5d); result appended
  below when it finishes. The instrumented flavour's ratchet evidence is the cmp above against
  af3f0824499e (nightly 20261104T103257Z: 41 pass, 0 fail).
- Ratchet on the release exe: 20261104T190430Z PASS -- 41 pass (12 improved), 0 fail, 0 blocked, 3
  quarantined; every manifest in the run carries binary_sha12=b26f82d0ce64. exe-bytes 8,633,512 (limit
  8,670,630); code-lock-bytes 5,150,832 (limit 5,181,776). No limit is lowered by this result.
  Report copied here as ratchet-report-release.txt.
- F4 (review 2026-11-04: are the release run's 3 quarantined checks the nightly's 3?): same three
  names, but two read differently, so both were chased (alias/):
  - screen-agsquest-alias-y60-fixed40k: ERROR(q) on release (VOID, frames_skipped 1291/1301) vs PASS(q)
    on the nightly. Cause: gate-alias.sh "ran without fixed timestep" by OMITTING the flag, and the release
    flavour defaults it on. Fixed in gate-alias.sh (DOSAGS_FIXED_TIMESTEP=0 passed explicitly, both
    places); re-run on the release exe: ok, 10 pairs, 0 problems, skips 0/0.
  - screen-shards-alias-512x384 (cycles=max, fixed timestep, quarantined for tick-landing jitter): 4
    problems on release vs 1 on the nightly. Three more runs each, same session: release 6/4/6,
    instrumented 4/3/3. Every release problem is "froze at different ticks" (VOID); every release pair
    that was compared was equal; one instrumented run had the known tick-100 DIFFERS. In the AQ row's
    deterministic mode (fixed 40k, timestep off, no-skip assert) both flavours: 5 pairs, 0 problems,
    skips 0/0. The release flavour renders shards identically; it lands full-speed freezes off-target
    more often. Not a release defect; the row's mode is a ratchet question.
