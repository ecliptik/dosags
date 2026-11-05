# LAB-S32 -- Gate S32 (32-bit), lab side

Branch `lab/metric` (worktree `~/git/dosags-lab-metric`), worker `dosags-lab-metric`. Operator
decision 2026-09-23 (hub plan, "Campaign using this setup"): this worker owns 32-bit. LAB ONLY:
every hardware cell below is a REQUEST for the coordinator to batch into an operator-approved round.

## 1. The gate

**Fixture:** AGS Quest forced-32, 640x480x32 1:1 (alias ON y=60), the AutoPilot demo. Hardware
baseline S2Q1-2026-09-22 (0194 `e8d4b76c5cd9`, sound OFF): `tick_rate_steady` 40.52, 189 of 1499
frames skipped, **stable 35.41**, `fps_p50` 39.45, `present_update_window` mean 11.5 ms.

**Bar (sound ON: SB PCM + MIDI, OPL3 arm and WaveBlaster arm):** both tick figures 39.2-40.8,
`fps_p50` >= 40, completeness >= 95%, camera clean, x2 on hardware; audio counters: `pcm_irqs` =
expected chunks, `overwrites=0`, `late_writes=0`, `silent_irqs=0` outside room loads.

**Distance to the bar.** Stable 35.41 sound off, and sound costs: the same demo at 16-bit is 37.78
stable sound off (AQF1) against about 34.3 with sound on (SB3S-2026-09-22: steady 40.60, 554 of 3587
skipped). Stable >= 39.2 means skipping no more than about 3% of ticks. On S2Q1 the 486 is busy
874 ms of every second (24.7 ms per render x 35.4 renders); rendering every tick needs roughly 4 ms
less per render with sound off, more with sound on. **The cut needed is on the order of 4-6 ms per
render.** That estimate is arithmetic on S2Q1 and SB3S, not a model prediction.

## 2. Where the 486's time goes (hardware S2Q1, whole-run means per call)

| phase | ms per call | what the lab vector says it is (LS2Q, steady scope, per render) |
|---|---|---|
| `present_update_window` | 11.50 | 46.6 KB pushed in 4.75 rects (the fades' full frames are in the excluded scope) |
| `render_backbuffer` | 7.92 | 3.8k px masked + **11.3k px alpha-blended** (`spr_msk_px`, `spr_bld_px`) |
| `scene_construct` | 5.47 | 7.7 sprites; `bg_restore` 2.96 ms of it (9.6k px x 4 B) |
| `script_vm` | blocking, excluded | 25 ins/tick, 0.9 API calls/tick |

Lab run: `tests/harness/results/LABS32-2026-09-23/LS2Q/` (lab binary `6bc92c4015ff`, same env
and cfg as S2Q1; `dirtypresent` narrow/full/px within 3% of the 486's own lines, so the content
matches). The lab counts are the 486's work. Their prices are not validated for 32-bit
(LAB-METRIC.md section 6): no 32-bit cell was among the five.

## 3. Lead 1: the 32-bit push runs at a third of the 16-bit push's rate per byte

Same demo, same dirty-rect geometry (the `dirtypresent` lines agree), whole run:

| cell | bytes pushed (lab, whole run) | hardware `present_update_window` | effective rate |
|---|---|---|---|
| AQF1, 640x480x16 | 207.6 MB, 3873 presents, 17822 rects | 9160 ms | **22.7 MB/s** |
| S2Q1, 640x480x32 | 134.9 MB, 1585 presents, 7260 rects | 16274 ms | **8.3 MB/s** |

The bandwidth probe (2026-09-17) measured the LFB at 27.3 MB/s in modes 0x101 and 0x111 only
(8 and 16 bpp). **No 32-bit mode was ever measured.**
- **H1 (card):** at 640x480x32 the Mach64 accepts CPU writes at about 8-10 MB/s. Plausible because
  display refresh at 32 bpp takes about twice the VRAM bandwidth of 16 bpp.
- **H2 (our software):** the card is as fast at 32 bpp as at 16, and the 32-bit present path does
  something extra (per-row cost, a conversion, a second pass).

The two call for opposite work (H1: push fewer bytes, or find a faster route; H2: fix the path),
and only the 486 can tell them apart. -> hardware cell **BW32**, section 5.

## 4. Lead 2: at 32 bpp, transparent-background GUIs are alpha-blended every render

Read from the source (`vendor/ags`, 3.6.3 + series):
- `GUIMain::HasAlphaChannel()` (`Engine/gui/gui_engine.cpp:37`): a GUI with no background image and
  no background colour has an alpha channel whenever `game.GetColorDepth() >= 24`.
- `draw.cpp:2882` syncs the GUI texture with that flag, and `SDLRendererGraphicsDriver::RenderSpriteBatch`
  (`ali3dsw.cpp:942`) draws a `has_alpha` texture with `set_alpha_blender()` + `draw_trans_sprite`,
  i.e. a per-pixel alpha blend through a blender function pointer.
- At 16 bpp the same GUI takes the masked path (AQF1: `spr_bld_px=0`).

LS2Q: 16.66M px blended in steady scope = **11.3k px per render**, against 3.8k masked. A rough
per-pixel split of S2Q1's 7.92 ms `render_backbuffer` puts about 6 ms in the blend (about 36
cycles/px). That uses an unmeasured masked-at-32-bit price, so it is an estimate, not a
measurement.

**Candidate C1 (ags patch in 0231-0249, not written yet):** when a `has_alpha` texture is
(re)built, which for a GUI happens only when the GUI changes, scan its alpha once. If every alpha is
0 or 255, draw it each render with a binary-alpha skip copy: alpha 0 skipped, alpha 255 copied.
That is pixel-identical to the blender for those two values and costs about as much as a masked
blit. Any other alpha keeps the blender. First step, lab only: count how many blended textures
and px are binary-alpha on this fixture. If they are not, C1 is dead before it is written.

## 5. Hardware requests (for the coordinator to batch)

### BW32 -- the 32-bit bandwidth probe (no game, one run, about 1 minute of probe time)

Probe: `tests/harness/results/bandwidth-probe32/bwprobe32.c` / `bwprb32.exe` (built on this
branch, DJGPP `-O2`; functional check under DOSBox-X in the same directory). It reads the BIOS mode
list, times 640x480x16 (0x111, the anchor) and every listed 640x480 mode with bpp 32 (and 24):
whole blocks (460,800 to 1,228,800 B) by LFB `rep movsl` and `memcpy` and through the banked
window, LFB write-only (`rep stosl`), and rect-shaped pushes (one `memcpy` per row at the mode's
pitch, 32-640 px wide, ~10 KB per rect at 32 bpp).
Run as `BWPRB32 > PRBOUT32.TXT` from `C:\` on HW-486-66 (CWSDPMI beside it). Collect PRBOUT32.TXT.

**Binary of record for round A (do not rebuild before round A finishes):**
- `tests/harness/results/bandwidth-probe32/bwprb32.exe` in the worktree `~/git/dosags-lab-metric`.
  It is gitignored like every `*.exe`, and identified by hash:
  **sha256 `37fc42255a4a792f74fa42d760ef3cf20d6f48da95d3efe299c7be677ab3a577`**, 187,995 bytes.
- Built from `bwprobe32.c` (sha256 `3e86a5337f5d9e505a0bd5f0b3c81b0953b298044c5005403d28edb1694e7f45`,
  committed) with `i586-pc-msdosdjgpp-gcc (GCC) 12.2.0`: `i586-pc-msdosdjgpp-gcc -O2 -Wall -o bwprb32.exe bwprobe32.c`.
- DPMI host: `vendor/cwsdpmi/cwsdpmi.exe` (sha256 `2de899fecaa90632b8b9bdfc0305cb0375e59ae252c37e32d06c1ed3f98a8f44`),
  staged beside it as `CWSDPMI.EXE`.
- Functional check (DOSBox-X, times meaningless): `dosbox-x-2026-09-23-bwprb32.txt`. It lists 0x112/0x1F1
  640x480x32, verify ok on 0x111/0x112/0x1F1, 48 timed rows, `done`.

**Run steps (round A, main worker):**
1. Stage `BWPRB32.EXE` and `CWSDPMI.EXE` to `C:\` (vcctrl send-file). Verify the staged sha256 of
   `BWPRB32.EXE` equals the hash above; **VOID if not**.
2. From the DOS prompt, at `C:\`: `BWPRB32 > PRBOUT32.TXT`. It sets graphics modes and draws a test
   pattern for about 1-2 minutes, then restores text mode and returns to the prompt.
3. Run `C:\VGACAP\MODE12` afterwards (capture restore, standing practice).
4. Collect `PRBOUT32.TXT` into `tests/harness/results/bandwidth-probe32/HW-486-66-<date>-bwprb32-PRBOUT32.TXT`.
   The file must end with `done`, else the run is incomplete and VOID.
5. Score against the pre-registration below, anchor first.

**PRE-REGISTRATION (fixed before the run):**
- **Anchor:** 0x111 LFB `memcpy` 614,400 B within 27.3 +- 10% MB/s. **VOID** if outside: the probe
  or the machine differs from 2026-09-17, and nothing else in the file is read.
- **H1 is supported if** the 32-bit LFB whole-block `memcpy` is **<= 12 MB/s**. **H2 is supported
  if** it is **>= 20 MB/s**. Between 12 and 20: neither. That is reported as such, and the
  rect-shaped rows decide which share of the 8.3 MB/s effective rate is the card.
- **Stated prediction (H1 favoured):** 32-bit LFB block write 8-12 MB/s. LFB write-only no more
  than 1.3x the copy. The 16-bit rect rows within 20% of the 16-bit block rate at widths >= 160 px.
- **What each outcome does next:**
  - H1: S32's present is bus-bound at about 8 MB/s. Every KB pushed costs about 0.12 ms, so the
    lever is fewer bytes: tighter dirty rects, skipping pixels unchanged since the last present,
    or the banked route if it measures faster at 32 bpp.
  - H2: the lab reads the 32-bit branch of `DOSVESA_UpdateWindowFramebuffer` and the AGS present
    for the extra work.
  - No game cell is spent on the present until BW32 is back.
- Not measured by this cell: refresh rate (UniVBE's choice, not set by the probe).

### Later, once C1 exists and passes its lab gate (NOT requested yet)

S2Q1-fixture pair, C1 off vs on, sound off, x2 each: the 486 price of the alpha blend vs the
binary-alpha path. Then the sound-on S32 cells (OPL3 and WaveBlaster arms).

## 6. What the lab metric can and cannot say here (LAB-METRIC.md sections 5-9)

- Counts: exact. LS2Q reproduces the 486's own `dirtypresent` px within 3%.
- Prices: the pre-registered model FAILED. The render-bound cells held 0.93-1.40 held out, but no
  32-bit cell and no blend-class pixel was ever in the validation. So for S32 the counters RANK
  candidates only by the work they remove (bytes, px by class). They do not predict ms.
- B-lite (fixed-cycles emulated time, LAB-METRIC.md section 9) would price the blend-vs-skip loop
  difference, which is CPU work. It is not validated yet, so any figure from it is labelled a screen.

## 7. C1 (ags 0231): exact fast path for 32-bit binary-alpha blends

**Lab finding that opened it (throwaway instrument, never committed; binary built from a temporarily
edited `ali3dsw.cpp`, the vendor tree restored afterwards):** on the S2Q1 fixture, 10,001+ blended
draws, **every blended pixel's alpha is 0 or 255** (`amid=0` throughout), and global alpha is always
255. 82% of blended px are alpha 0, and the blender still processes each of them.

**Mechanism (patch 0231, `Common/gfx/allegrobitmap.cpp` `Bitmap::TransBlendBlt`, `__DJGPP__`):**
`_blender_alpha32` at a=0 returns `dst & 0x00FFFFFF` and at a=255 returns `src & 0x00FFFFFF`.
Host-verified against a verbatim copy of the function over 5e7 random pixel pairs plus edge values:
0 mismatches. The fast loop mirrors Allegro's `_linear_draw_trans_sprite32` exactly: same
clipping, mask colour skipped, and any other alpha calls the installed blender. **So its output
equals draw_trans_sprite's for every input by construction.** There is no per-texture flag.
Taken only when src and dst are 32-bit and `_blender_func32 == _blender_alpha32`.
`DOSAGS_ALPHAFAST=0` disables it (same binary for an A/B). Manifest line:
`DOS-PORT alphafast calls= fallback= px= mid_px=`.

**PRE-REGISTRATION, lab correctness gate G1 (fixed before the run):** C1 lab binary, AGS Quest
full AutoPilot at forced-32 (S2Q1 env and cfg without the auto-exit, so every phase screenshot is
taken), DOSBox-X default fast conf, `--fixed-timestep`, arms `DOSAGS_ALPHAFAST=0` (A) and unset (B),
order A B A B.
- **PASS iff** every `PH*.BMP` is byte-identical across all four runs, AND the B runs report
  `alphafast calls > 0`, AND `mid_px = 0`.
- If the two A runs differ from each other (the known one-tick startup nondeterminism), the gate is
  **INCONCLUSIVE, not a pass**. It is then re-run with a fixed-cycles conf.
- A FAIL stops C1.

**Screen, not a validation (B-lite, labelled):** the same A/B under `confs/dosbox-x-fixed25k.conf`
on the S2Q1 fixture (auto-exit 1500), EXCLUSIVE lock. Emulated `render_backbuffer` ms per call is
reported as a direction and a size. Its 486 value is the hardware pair in section 5 ("Later").

**G1 addition (coordinator, 2026-09-23), pre-registered before its run:** one 16-bit pass. AGS Quest
at its native 16 bpp (same cfg, no forced depth), full AutoPilot, arms A (`DOSAGS_ALPHAFAST=0`) and B
(on), order A B (`G1/g16.sh`). **PASS iff** the B run's `alphafast calls=0` (the fast path never
engages below 32 bpp), OR every `PH*.BMP` of A and B is byte-identical. The fast path must not reach
depths where it is not needed. If calls > 0 at 16 bpp, that is reported as a finding even if the
output is identical.

**G1 amendment (coordinator, 2026-09-23), before any G1 run produced output.** Both earlier launches
were stopped while still queued on the lock, so no run exists. G1 and G1-16 now run at **fixed
40000, `core=normal`** (`tools/dosbox-x.conf`, deterministic per lab-mmd), with **one EXCLUSIVE
lock per run**, not a shared lock around the series. Reason: AGS Quest's known one-tick AutoPilot
divergence at cycles=max under host load could fail the A/B spuriously or pass it for the wrong
reason. `AUTOPLT.LOG` is kept for every run. **If an A/B pair differs, the AutoPilot phase ticks
of the two runs are compared before C1 is blamed.** A pair whose phase ticks differ is
INCONCLUSIVE (divergence), not a FAIL. The pass lines are unchanged.

### 7.1 G1 RESULT: **PASS** (2026-09-24, fixed 40000 `core=normal`, EXCLUSIVE per run)

Raw: `tests/harness/results/LABS32-2026-09-23/G1/g1-{A-1,B-2,A-3,B-4}/` (RUNMANI, STDOUT, AUTOPLT,
PH*.BMP), `INDEX.TXT`. Binary `build/lab/C1L` (`binary_sha12=8eb834caa429`, the dirty-tree build of
exactly the code landed as 0231).

| run | PH01 | PH02 | PH03 | `alphafast` | exit |
|---|---|---|---|---|---|
| A-1 (off) | 50e4283a24be | 75f725e1840e | ee2c08ff363e | calls=0 fallback=23209 | 0 |
| B-2 (on) | 50e4283a24be | 75f725e1840e | ee2c08ff363e | **calls=22376** fallback=947 px=41791611 **mid_px=0** | 0 |
| A-3 (off) | same | same | same | calls=0 fallback=23209 | 0 |
| B-4 (on) | same | same | same | calls=22376 fallback=947 px=41791611 mid_px=0 | 0 |

- Every `PH*.BMP` is byte-identical across the four runs, calls > 0, `mid_px=0`: **PASS** as registered.
- **Determinism at fixed cycles:** A-1 = A-3 and B-2 = B-4 in every count, render pass and AutoPilot
  tick. The only difference in the manifests is `render_backbuffer` total_us, off by 6 and 14 us
  in about 30 s: clock jitter.
- **A vs B AutoPilot ticks** are identical except the end of the `audio` phase (A 3571, B 3569),
  and so the phases after it. That phase waits on a clip's playback in emulated time, and C1
  changes the code's speed, so a two-tick shift there is expected. It is not the known
  startup divergence (the splash and every earlier phase match).
- **Coverage, stated:** the AutoPilot writes 3 screenshots. The byte-level evidence for exactness
  is those 3 frames, plus the construction (the fast loop reproduces `_blender_alpha32`'s result
  for every alpha value) and the 5e7-sample host check. The 947 fallbacks in B are blends with a
  global alpha < 255 (`_trans_alpha_blender32`), which go to Allegro unchanged.
- **SCREEN, not a validation (B-lite unvalidated until its verdict):** emulated
  `render_backbuffer` **8.28 -> 5.57 ms per call** (-2.71 ms, -33%) at fixed 40000. With B-lite's
  S2M1 calibration k_R = 1.13, that suggests about -3.1 ms per call on the 486.

### 7.2 G1-16 RESULT: **PASS** (fixed 40000, EXCLUSIVE per run)

Raw: `results/LABS32-2026-09-23/G1/g16-{A-1,B-2}/`. AGS Quest native 16 bpp (`640 x 480 (16-bit)`,
surface RGB565), full AutoPilot, C1 binary `8eb834caa429`. Both arms show `alphafast calls=0
fallback=0`: `TransBlendBlt` is never reached at this depth, so the fast path cannot engage.
PH01-03 are byte-identical A vs B (`7ac5213ff8b4`, `3b2651677ea1`, `623fc3a701e2`), and so are the
AutoPilot logs. Both registered conditions hold.

**Landed:** `patches/ags/0231-DOS-PORT-patch-0231-exact-fast-path-for-32-bit-alpha.patch`
(format-patch of vendor commit `1485c5941`; re-applied by `make patches` on clean trees, series
fingerprint `0b617bee56fa`, vendor HEAD `6677f4408`). `/sdldos:review` done before landing:
- slot: 0231, the next free slot in the lab-metric range;
- DJGPP constraints: no `fopen`/`size_t`/SIMD, ASCII-only;
- gating code read: the `draw_trans_sprite` dispatch, the vtable32 entries, the 32-bit branch of
  cspr.h, `_blender_alpha32`;
- permanent, not a diagnostic;
- builds clean.

## 8. ROUND B PRE-REGISTRATION (written before round B; hardware run by the main worker)

Binaries (all in `~/git/dosags-lab-metric/build/`, gitignored, identified by sha256):

| name | what | `binary_sha12` | sha256 |
|---|---|---|---|
| `round-b/timed/ags.exe` | 0209 + 0230 + **0231**, timed build (no script_ins), `build_dirty=0` | `f429957f47dc` | `7ba8d49fc5eecd1d12e6ffd9908d3ea53409ce4ceda87a4b71682166edc47e6f` |
| `lab/A2/ags.exe` | 0209 **without** 0230, built from a separate checkout of `vendor/ags` at 0209, same flags | label **`a0a0a0a0a0a0` set by hand** (not a series fingerprint) | `08e5ff91790861002d33ca6735ae1fc4aa71d92f37420d763084988df0fe4eb9` |
| `lab/B2/ags.exe` | 0209 + **0230**, timed build | `640060d25f24` | `d46ee5fa8b67865eba233346988ef65b0381722e1dc6b3bb6d2250babcdf4408` |

### 8.1 C1P -- C1 off/on on the S2Q1 fixture, sound off, x2 each (4 runs, A B B A)

Fixture exactly as S2Q1: `run-hw.sh agsquest --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env
DOSAGS_FORCE_COLOR_DEPTH=32 --env DOSAGS_TAS_AUTO_EXIT_TICK=1500 --extra-file
tests/harness/games/trilbysnotes/ACSETUP-OFF.CFG:ACSETUP.CFG`, binary `round-b/timed`. Arm A adds
`--env DOSAGS_ALPHAFAST=0`, arm B does not. Tags C1PA1, C1PB1, C1PB2, C1PA2.

- **VOID a run if:**
  - `binary_sha12` is not `f429957f47dc`, or `build_dirty` is not 0;
  - the mode line is not `640 x 480 (32-bit)`, or the alias is not `ON y=60`;
  - there is more than one manifest block, or an SDL trace was collected;
  - arm A shows `alphafast calls` > 0, or arm B shows `alphafast calls=0`.
- **Witness:** card + camera sheets reviewed clean before any rate is written.
- **Predictions (fixed now):**
  1. Arm A reproduces S2Q1:
     - `render_backbuffer` mean 7.92 +- 15% ms;
     - `present_update_window` 11.5 +- 15% ms;
     - stable rate 35.41 +- 2.
     If not, report it: the binary differs from 0194 by 0209 and 0230 (counters +~1%).
  2. **B - A `render_backbuffer` mean per call: -3.1 ms (range -2.0 to -4.5).** Source: the G1
     screen (-2.71 ms emulated) x k_R 1.13 (B-lite's S2M1 calibration). **Falsified if the drop is
     under 1.0 ms.** Beyond -4.5 ms is reported as a model miss, not a failure.
  3. `present_update_window` and `scene_construct` per call unchanged within +-10%. C1 touches
     only the blend.
  4. Stable rate: B above A. Not predicted to reach 39.2 sound off; stated as a direction only.
  5. B's `alphafast`: calls > 0, `mid_px=0` (as in the lab). `mid_px` > 0 on the 486 is reported:
     the output would still be exact, since those pixels go to the blender.
  6. PH01.BMP, A vs B: expected byte-identical (a check, not a void).
- **What it decides:** C1's price on the 486 per call, which is the step toward S32's 4-6 ms cut.

### 8.2 CTR -- the 0230 counters' cost on the 486 (A2 vs B2), render-bound, sound off (4 runs, A B B A)

Fixture exactly as AQF1: `run-hw.sh agsquest --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1
--extra-file tests/harness/games/trilbysnotes/ACSETUP-OFF.CFG:ACSETUP.CFG` (640x480x16 1:1, alias
ON y=60, AutoPilot to its own quit). Arm A = `lab/A2`, arm B = `lab/B2`. Tags CTRA1, CTRB1,
CTRB2, CTRA2.

- **VOID a run if:**
  - `binary_sha12` does not match its arm (A2's hand-set label `a0a0a0a0a0a0`, B2's `640060d25f24`);
  - the mode line is not `640 x 480 (16-bit)`, or the alias is not `ON y=60`;
  - there is more than one manifest block, or an SDL trace was collected.
- **Measured:** busy per render (`loop_ms - stall_ms - wait_next_frame`, over render passes) and
  `tick_rate_steady`, per run. The A-A and B-B spreads are reported first.
- **Prediction:** B's busy per render +0.5% to +2.0% over A's (DOSBox-X ranking: +0.82% BENCH8,
  +1.28% MMD, section 7 of LAB-METRIC.md). **If |B - A| is inside the larger of the A-A and B-B
  spreads, the result is "not measurable at n=2", not zero.**
- **What it decides:** whether the always-on counters may stay in timed builds. The coordinator's
  call, with this number.

## 9. BW32 RESULT and candidate C2 (24-bpp present of a 32-bit surface)

### 9.1 BW32 (round A, 2026-09-24, main worker) -- scored against section 5

Raw: `~/git/dosags/tests/harness/results/BW32-2026-09-24/HW-486-66-2026-09-24-bwprb32-PRBOUT32.TXT`
(ends `done`, every readback ok). The 486's BIOS (UniVBE, VBE 3.0) numbers its modes differently from
DOSBox-X: 0x112 is **24 bpp** there, and 32 bpp is 0x1B0.

| check | result | verdict |
|---|---|---|
| anchor 0x111 LFB memcpy 614,400 B, 27.3 +- 10% | 27.30 MB/s | valid |
| H1 (32-bit LFB block memcpy <= 12 MB/s) | 0x1B0: memcpy 7.70, movsl 7.69 | **H1 SUPPORTED** (the card) |
| stated: 32-bit block 8-12 MB/s | 7.70 | missed low by 4% |
| stated: write-only <= 1.3x copy | 10.22 / 7.70 = 1.33x | missed, marginally |
| stated: 16-bit rects at >= 160 px within 20% of the block rate | 28.2-30.2 vs 27.3 | met |
| (not predicted) 24 bpp, 0x112, LFB, pitch 1920 | memcpy **27.22**, write-only 30.03, rects 20.2-27.0 | full bus speed |

**H2 is not supported.** 32-bit rects run at 5.67-7.56 MB/s, which is the card's own 32-bpp rate, so
the 8.3 MB/s seen in the game is not our software. A 32-bpp pixel costs about 0.52 us to put on
screen, against about 0.11 us at 24 bpp, with the same 8:8:8 colour.

### 9.2 C2 design (SDL patch in 0210-0219, not written yet)

Facts it rests on:
- AGS never calls the SDL direct-FB API: `/usr/bin/grep` over `vendor/ags` finds only the two
  banked-mode counters in `quit.cpp`.
- The engine talks to the display only through the window surface and
  `SDL_UpdateWindowSurface(Rects)`.
- With the direct framebuffer (the port default), SDL's surface is a system-RAM buffer, and
  `DOSVESA_UpdateWindowFramebuffer` copies each dirty rect row by row into VRAM
  (`SDL_memcpy` per row, LFB near pointer, `SDL_DOS_PREFER_LFB=1`).
- The 486 lists 24-bpp LFB modes at 640x480 (0x0112, pitch 1920) and 512x384 (0x01C4, pitch 1536),
  both direct colour (model 6). Their colour masks are not in any log yet.

Mechanism, behind a hint (`SDL_DOS_PACK24=1`; off by default):
1. **Modes.**
   - A 24-bpp direct-colour LFB mode whose masks are R at bit 16, G at 8, B at 0 (8 bits each) is
     advertised to the application as `SDL_PIXELFORMAT_XRGB8888`, marked "packed 24" internally.
   - The native 32-bpp mode of the same WxH is hidden, so an application asking for 32 bpp gets the
     24-bpp one.
   - Any other mask layout is left alone: no pack, no hiding.
   - The mode log line gains the masks, so the 486's layout is recorded on the first hardware run.
2. **Surface.** It stays XRGB8888 in system RAM (engine, alias and C1 unchanged). `fb_state`
   carries `vram_bpp=3` beside the surface's 4, and `pitches_match` is false (2560 vs 1920).
3. **Push.** For each dirty rect row, pack 4 -> 3 bytes straight into the LFB: per 4 px, 4 dword
   loads, 3 dword stores; the ragged ends byte by byte. XRGB8888 in memory is B,G,R,X; the 24-bpp
   mode with R16/G8/B0 is B,G,R. The pack drops the X byte and nothing else, so the displayed RGB
   is identical to what the 32-bit path shows. The banked route packs into a row buffer and uses
   the existing banked copy.
4. **Non-direct path** (`CreateNormalFramebuffer`, e.g. with the direct-FB hint off): its LFB
   surface gets the real 24-bpp format, so SDL's own blit converts. Slower, still correct.
5. **Lab-only verifier** (`SDL_DOS_PACK24_VERIFY=1`): after each push, read every pushed rect back
   from VRAM, unpack, compare with the surface's RGB, and count mismatched px. The result goes in a
   log line.

### 9.3 PRE-REGISTRATION: lab gate G2 (C2 correctness)

- **Conf:** `confs/dosbox-x-fixed40k-24bpp.conf` = `tools/dosbox-x.conf` (fixed 40000,
  `core=normal`) + `[video] vesa vbe 1.2 modes are 32bpp = false`. DOSBox-X's 0x112 then becomes
  640x480x24 like the Mach64's, while its other 32-bpp 640x480 id stays.
- **Runs:** S2Q1 fixture (forced-32, AutoPilot, auto-exit 1500), with C1 on. Arm A: hint off
  (32-bpp mode). Arm B: `SDL_DOS_PACK24=1 SDL_DOS_PACK24_VERIFY=1`. Order A B A B, EXCLUSIVE per run.
- **PASS iff all hold:**
  1. B's verify line: pushed px > 0, **mismatched px = 0**, over every present of the run.
  2. B's mode line reads 640x480, the SDL log says packed-24 on 0x112, and the masks R16/G8/B0 are
     logged.
  3. A and B have identical `dirtypresent` lines and an identical `work scope=steady` push_bytes
     and push_rects (the same rects are pushed).
  4. `PH*.BMP` byte-identical across all four runs.
  5. A1 = A3 and B2 = B4 (determinism).
- A FAIL stops C2. If DOSBox-X's 24-bpp masks are not R16/G8/B0, the pack does not engage: that
  is reported as "not testable in the lab", and a lab-side swap variant is written before any
  hardware.
- **Screen (not validated; B-lite k_R applies only to CPU phases):** B's emulated
  `present_update_window` time at fixed 40k measures the pack loop's CPU cost (a `rep movs` push
  costs ~0 there). Reported for what it is.

### 9.4 PRE-REGISTRATION: C2's 486 prediction (for a later round, after G2 passes)

On the S2Q1 fixture (sound off, C1 on in both arms), C2 on vs off:
- **`present_update_window` mean per call: predicted 4.5 ms (3.6-5.5), from 11.5 in S2Q1.**
  Basis: S2Q1's effective 0.48 us per pushed px, against 0.15-0.23 us for C2. That C2 range is
  24-bpp rect writes at 20-27 MB/s (0.11-0.15 us/px, BW32), plus the 4th source byte read, plus
  ~5 cycles/px of pack.
- Falsified if C2's mean exceeds **7.5 ms**, i.e. less than a 35% cut.
- Beyond 3.6 ms: reported as a model miss in the good direction.
- `render_backbuffer` and `scene_construct` unchanged within +-10%.
- Stated as a direction only, not a verdict: with C1's predicted -3.1 ms and C2's about -7 ms, the
  sound-off S2Q1 busy per render (24.7) would fall by about 10 ms. That is more than the 4-6 ms S32
  needs, before sound. Sound ON is the next lab step (an S32 sound-on work vector).

### 8.1 RESULT: C1P (round B, 2026-09-24, main worker) -- C1 on the 486: prediction 2 HOLDS

Raw: `~/git/dosags/tests/harness/results/C1P{A1,B1,B2,A2}-2026-09-24/`. Every run: `binary_sha12=f429957f47dc`,
`build_dirty=0`, pre = staged = post sha256, mode `640 x 480 (32-bit)`, alias `ON x=0 y=60`, one
manifest block: **no VOID.** A: `alphafast calls=0 fallback=9143`. B: `calls=9123 / 9131, mid_px=0`.
PH01.BMP `50e4283a24be` in all four (the same frame as G1's lab runs). **Witness:** all eight sheets
(card + camera) reviewed. Splash, title, the forest room with one character instance, complete
backgrounds, text and speech boxes, then the demo's fade to black. No trails, nothing missing.

| run | `render_backbuffer` ms/call | `present_update_window` | `scene_construct` | steady | skipped / 1499 | **stable** | busy/render | `fps_p50` |
|---|---|---|---|---|---|---|---|---|
| A1 (off) | 8.01 | 11.56 | 5.45 | 40.54 | 192 | **35.35** | 24.91 | 39.45 |
| B1 (on) | 4.14 | 11.52 | 5.49 | 40.64 | 158 | **36.36** | 20.97 | 39.92 |
| B2 (on) | 4.14 | 11.52 | 5.49 | 40.62 | 157 | **36.37** | 20.99 | 39.92 |
| A2 (off) | 8.02 | 11.57 | 5.45 | 40.53 | 192 | **35.34** | 24.93 | 39.49 |

(stable = steady x (1 - skipped/ticks); busy = loop - stall - wait_next_frame, over render passes.)

| prediction (8.1) | result | verdict |
|---|---|---|
| 1. A reproduces S2Q1: rb 7.92 +-15%, present 11.5 +-15%, stable 35.41 +-2 | 8.01 / 11.56 / 35.35 | holds |
| **2. B - A `render_backbuffer`: -3.1 ms (-2.0 to -4.5); falsified under 1.0** | **-3.88 ms/call** (-48%) | **holds** |
| 3. present and scene unchanged +-10% | 11.52 vs 11.56; 5.49 vs 5.45 | holds |
| 4. stable: B above A (direction only) | 36.37 vs 35.35 (+1.0) | holds |
| 5. `mid_px=0` | 0 | holds |
| 6. PH01 A = B | identical | holds |

- **The screening number was low by the amount B-lite said it would be.** G1's emulated -2.71 ms
  x k_R 1.13 = -3.1 predicted, -3.88 measured: 486/prediction = 1.25. That matches B-lite's
  stated ~25% under-prediction for render-bound cells (LAB-METRIC.md 11). This is one data point,
  recorded, not a re-calibration.
- **Why the stable rate rose only +1.0 while busy per render fell 3.9 ms:** the skips are bursts.
  `wait_next_frame` doubled (4.3 -> 8.6 s: the machine is idle more), but the ticks that still skip
  are spikes. The per-skip samples (`skipframe`, STDOUT) show:
  - A: 33 samples, median total 45.7 ms, of which present 16.1, rb 11.3, scene 8.3, with
    `present_px` median 108,578 (big dirty areas).
  - B: 27 samples, median total 41.7 ms, present 19.0, **rb 7.9**, scene 8.7.
  C1 took about 3.4 ms off each skip tick, but a skip tick is dominated by pushing ~108k px at
  32 bpp. **That spike is what C2 removes** (section 9: about 4x cheaper per pushed px at 24 bpp).
- C1 is worth 3.9 ms per render on the 486 and is exact. It stays. It does not reach S32 by
  itself.

### 8.2 RESULT: CTR (round B, 2026-09-24) -- the always-on 0230 counters cost **+0.77%** busy per render on the 486

Raw: `~/git/dosags/tests/harness/results/CTR{A1,B1,B2,A2}-2026-09-24/`. Every run: the arm's own
`binary_sha12` (A `a0a0a0a0a0a0`, hand-set label; B `640060d25f24`), `build_dirty=0`, pre = staged =
post, `640 x 480 (16-bit)`, alias ON y=60, one manifest block: **no VOID**. Witness: all eight
sheets were reviewed. The four were stacked at half scale; CTRB1's card sheet was read at full
scale. Forest, treehouse interior, one character instance, complete backgrounds, the credits
panel, then the end. No trails.

| run | steady | skipped / ticks | stable | render passes | busy ms | **busy / render** |
|---|---|---|---|---|---|---|
| A1 (no 0230) | 41.16 | 295 / 3577 | 37.77 | 3282 | 58379 | **17.788** |
| B1 (0230) | 41.22 | 295 / 3575 | 37.82 | 3280 | 58799 | **17.926** |
| B2 (0230) | 41.22 | 295 / 3575 | 37.82 | 3280 | 58801 | **17.927** |
| A2 (no 0230) | 41.16 | 295 / 3577 | 37.77 | 3282 | 58393 | **17.792** |

- **Spreads first:** A-A 0.004 ms (0.02%), B-B 0.001 ms (0.01%).
- **B - A = +0.137 ms per render = +0.77%**, 30x the larger spread: measurable at n=2.
  **Prediction (+0.5% to +2.0%) HOLDS.** The DOSBox-X ranking said +0.82% (BENCH8) and +1.28% (MMD).
- The stable rate does not move (37.77 vs 37.82; the skip count is identical). On this fixture the
  counters cost busy time, not frames. A fixture at the edge of its budget would pay it in frames.
- The A arm reproduces AQF1 (17.82 ms/render, stable 37.78).
- **For the coordinator's call:** keeping the always-on counters in timed builds costs about 0.14 ms
  per render (0.8%) on a render-bound 486 cell. The script-instruction counter stays lab-only
  (+20.6% on MMD in DOSBox-X).

**Coordinator decision (2026-09-24): ACCEPT the always-on 0230 counters in timed builds**, under
three conditions:
1. Both arms of any hardware comparison carry the same counter state. ABBA within one build family
   already guarantees this.
2. Any comparison against a pre-0230 record (S2Q1, AQF1, the gate figures) states the **+0.77%
   busy-per-render offset** beside it, uncorrected.
3. Release/player builds carry none of it.
Reason: 0.14 ms per render, no frame cost on this fixture, and it buys the B-lite work vector. The
script-instruction counter stays lab-only (`AGS_WORK_SCRIPT_INS=1` -> `-DDOSAGS_WORK_SCRIPT_INS`,
set only on the make command line; `AGS_CXX_FLAGS_BASE` in the Makefile, part of the build
fingerprint).

**Condition 3 is NOT enforced today, stated plainly.** The port has no release/player build: the
Makefile has no release target or flag (checked: no `RELEASE`/`PLAYER` switch), and every DJGPP build
compiles 0230's counters under `#ifdef __DJGPP__`. So does every other DOS-PORT instrument
(tickstats, RUNMANIFEST, skipframe...). **Proposed gate, not implemented, for the coordinator to
approve:**
- a macro `DOSAGS_WORK_VECTOR` wrapping 0230's always-on increments and its report lines;
- defined by default in `AGS_CXX_FLAGS_BASE` and dropped by `make AGS_RELEASE=1`, as a separate
  patch in 0232-0249, so a release build has none of it and the fingerprint says so.
It changes every timed binary's `binary_sha12`, which is why it waits for your word. Whether
AGS_RELEASE should also drop the rest of the instrumentation is a wider question for the release
packaging work, not this slice.

**Coordinator decision (2026-09-24), superseding the proposed gate above:** not landed now,
because changing every timed binary's `binary_sha12` mid-campaign breaks comparability for no
gain. **The 0230 work vector joins the rest of the DOS-PORT instrumentation in the
release-packaging question (a single AGS_RELEASE switch for all of it), decided when release
packaging is built.** The coordinator carries this item in the hub plan.

### 9.5 G2 RESULT: **FAIL as written** (condition 3). The cause is a design error in the gate, not a pixel error. C2 is stopped pending the coordinator.

Raw: `results/LABS32-2026-09-23/G2/g2-{A-1,B-2,A-3,B-4}/` (+ `smoke-B-1/`, not part of the gate).
Binary `3093249035de` (build_dirty=1: the uncommitted SDL change).

| condition (9.3) | result | |
|---|---|---|
| 1. B's verify: pushed px > 0, **mismatched px = 0** over every present | pushed 32,826,846, **mismatch 0** (B-2 and B-4) | holds |
| 2. mode 640x480, pack24 on 0x112, masks R16/G8/B0 logged | `pack24 engaged mode=0x0112 ... path=lfb`, `masks=r16/8 g8/8 b0/8` | holds |
| **3. A and B: identical `dirtypresent`, push_bytes, push_rects** | A 68,744,436 B / 7,002 rects; **B 65,253,820 / 6,849** | **FAILS** |
| 4. `PH*.BMP` identical across all four | PH01 `50e4283a24be` in all four | holds |
| 5. A-1 = A-3, B-2 = B-4 | identical within each arm (dirtypresent, work vector, pack24 line) | holds |

**Why condition 3 fails (read from the runs):** under `--fixed-timestep`, the frames rendered depend
on each frame's emulated cost:
- A: 1476 renders, 24 skipped.
- B: 1443 renders, 57 skipped. B's `present_update_window` costs 10.57 ms per call emulated against
  A's 0.94.
- A's push is `rep movs`, which DOSBox-X charges about nothing for. B's is the pack loop, **plus the
  verifier reading every pushed pixel back**, all charged as CPU.
- A different set of rendered frames pushes different dirty rects.

So condition 3 cannot hold whenever the arms differ in emulated cost. It was specified wrongly: it
tests the timing, not the pack. The pixel-level witness (condition 1: every pushed pixel read back
from VRAM equals the surface's RGB, 0 of 32.8M) is unaffected.

**Also not a valid screen:** B's 10.57 ms per present includes the verifier, so it is not the pack
loop's cost. A screen of C2's CPU cost needs a run with the verifier off.

**Proposed re-gate G2b (to pre-register only with the coordinator's word; not run):** the same
A B A B, fixed 40000, **without `--fixed-timestep`** (every tick then renders once, so the frame
sequence cannot depend on cost). Conditions 1-5 as in 9.3, all expected to hold. Plus one
verifier-off B run at fixed timestep, for the pack loop's emulated cost as a labelled screen.

### 9.6 PRE-REGISTRATION: re-gate G2b (coordinator-approved 2026-09-24; written and committed before any G2b run)

G2 stays recorded as a FAIL of its condition 3 (9.5). G2b is a new gate with the cause removed:
**no `--fixed-timestep`**. With `DOSAGS_FIXED_TIMESTEP` unset, `GameTick()` calls `UpdateGameOnce()`
once per tick (patch 0047's shape). There is no catch-up skip, so the frame sequence cannot depend
on per-frame cost.

- **Binary:** `build/lab/C2b` (`binary_sha12=4738fda3c29b`, `build_dirty=1`). It is G2's code plus one
  hint-gated lab diagnostic in the uncommitted SDL change: `SDL_DOS_RECT_HASH=1` hashes (FNV-1a) the
  ordered sequence of update calls, each call's rect count, and every rect's x,y,w,h exactly as the
  application passed them. At exit it prints `DOS-PORT recthash calls= rects= fnv=`.
- **Conf:** `confs/dosbox-x-fixed40k-24bpp.conf` (fixed 40000, `core=normal`, VBE 1.2 truecolor = 24 bpp).
- **Runs:** S2Q1 fixture (forced-32, AutoPilot, auto-exit 1500), C1 on, `SDL_DOS_RECT_HASH=1` in all.
  - Arm A: pack off.
  - Arm B: `SDL_DOS_PACK24=1 SDL_DOS_PACK24_VERIFY=1`.
  - Order A B A B, one EXCLUSIVE lock per run (hub library). Runner: `G2/g2b.sh`.

**PASS iff all five hold:**
1. B's verify: pushed px > 0 and **mismatched px = 0**.
2. B: mode 640x480, `pack24 engaged mode=0x0112 ... path=lfb`, masks `r16/8 g8/8 b0/8` in the SDL log.
3. **Exact frame equality A vs B:**
   - `render_passes` equal across all four runs;
   - `frames_skipped=0` in all four;
   - the `recthash` line (calls, rects, fnv) identical across all four, i.e. the same ordered rect list.
4. `PH*.BMP` byte-identical across all four.
5. A-1 = A-3 and B-2 = B-4.

**VOID (named in advance):** any run with `frames_skipped > 0`, because the premise (one render per
tick) failed. It is re-run once; a second void is reported, not retried.

**Screen, reported beside G2b, NOT part of the verdict:** one run `S` = B without the verifier, WITH
`--fixed-timestep` (the S2Q1 conditions), same binary and conf. Its emulated
`present_update_window` ms per call is set against G2 A-1's 0.94 ms (the `rep movs` push, which
emulation charges ~nothing for). It is the pack loop's emulated CPU cost: labelled a screen, since
B-lite was never validated for this code. **The hardware C2 cells remain the only cost evidence**;
their prediction is pre-registered after G2b passes (present_update_window on the S2Q1 fixture,
packed 24 vs 32, with a falsifier).

### 9.7 G2b RESULT: **PASS** (one literal deviation, stated). C2 is pixel-exact.

Raw: `results/LABS32-2026-09-23/G2/g2b-{A-1,B-2,A-3,B-4}/`, `INDEXB.TXT`; binary `4738fda3c29b`
(0210+0211, `build_dirty=1`), fixed 40000 24-bpp conf, no `--fixed-timestep`.

| run | render_passes | `recthash` (calls / rects / fnv) | verify | present ms/call (emulated) | PH01 |
|---|---|---|---|---|---|
| A-1 | 1501 | 1603 / 7326 / `8ef9f848` | -- | 0.96 | `50e4283a24be` |
| B-2 | 1501 | 1603 / 7326 / `8ef9f848` | pushed 34,037,190, **mismatch 0** | 10.60 | `50e4283a24be` |
| A-3 | 1501 | 1603 / 7326 / `8ef9f848` | -- | 0.96 | `50e4283a24be` |
| B-4 | 1501 | 1603 / 7326 / `8ef9f848` | pushed 34,037,190, **mismatch 0** | 10.60 | `50e4283a24be` |

1. Verify, mismatched px = 0: **holds**.
2. B: `pack24 engaged mode=0x0112 640x480 ... path=lfb`, masks `r16/8 g8/8 b0/8`: **holds**.
3. Exact frame equality: `render_passes` 1501 in all four, and the full ordered rect list is the
   same (hash `8ef9f848` over 1603 calls, 7326 rects): **holds**.
   **Literal deviation:** `frames_skipped` reads **-1**, not the registered 0, in all four runs.
   The field is `LoopCounter - RenderCounter` (`dos_get_frames_skipped`). -1 means one render more
   than ticks (1501 renders over 1500 ticks: a render before the first counted tick), i.e. **no
   skipped frame**. The registered VOID (> 0) is not triggered. The premise (one render per tick)
   is shown directly by the equal render counts and the identical rect-list hash.
4. PH01 byte-identical in all four: **holds**.
5. A-1 = A-3, B-2 = B-4: **holds** (every figure above; emulated timings identical).

**Verdict: PASS.** The deviation in 3 is stated here for the coordinator to overrule if they read
it differently.

**Screen (NOT part of the verdict; B-lite never validated for this code):** run `g2b-screen-S-1`
(pack on, verifier off, `--fixed-timestep`, S2Q1 conditions). Emulated `present_update_window`
**4.16 ms per call** against 0.96 for the `rep movs` push (G2b A). The pack loop is therefore about
3.2 ms per present emulated, over 33.6M px / 1575 presents = 21.4k px per present, i.e. about 6
emulated instructions per pixel. That agrees with the compiled inner loop (`objdump` of
`dos_pack24_row`: 29 instructions per 4 px, one stack spill). The verifier costs 6.4 ms per present
emulated (B-2 10.60 against S 4.16), so the B arms' timings are never a cost figure.

**0210 vs 0211 split (for the hardware build):**
- 0210 (what ships) and 0211 (lab-only: verifier + rect hash) are separate format-patches.
  `patches/SDL/0210-pack24-present-32bit-surface-through-24bpp-mode.patch` is landed.
  `C2-split/0211-pack24-lab-verify-and-rect-hash.patch` is kept beside the results and is **not**
  in the applied series.
- `C2-split/pack-functions-0210-vs-0210+0211.diff.txt`: `dos_mode_is_pack24` and `dos_pack24_row`
  are **identical** in 0210 alone and 0210+0211. `dos_pack24_push` differs only by the verifier's
  read-only block after the pack. So G2b's pixel evidence applies to 0210's pack path unchanged.

**Coordinator ruling on G2b (2026-09-24): PASS accepted, deviation accepted.** For future gates the
no-skip condition is written as **"`render_passes` = ticks + 1 (equivalently `frames_skipped` <= 0)"**
so the literal cannot bite again.

### 9.8 PRE-REGISTRATION: C2P -- C2 on the 486 (next batch; hardware run by the main worker)

**Binary (one, both arms):** `~/git/dosags-lab-metric/build/round-c/timed/ags.exe`, `binary_sha12=a2485a373bd2`,
`build_dirty=0`, sha256 `d50f95e0705fb8371dfea8b97932a63db693ba852b0d667c419d8138b481cd63`.
Contents: ags 0209 + 0230 + **0231 (C1)**, SDL + **0210 only** (no 0211: `strings` finds no `recthash`
or `PACK24_VERIFY`). **Precondition before staging:** its DOSBox-X run (`G2/hw0210-B-1`, queued) must
reproduce G2b's PH01 (`50e4283a24be`) and `pushed_px=34037190`. If it does not, this pre-registration
is withdrawn.

**Fixture:** exactly S2Q1/C1P: `run-hw.sh agsquest --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1 --env
DOSAGS_FORCE_COLOR_DEPTH=32 --env DOSAGS_TAS_AUTO_EXIT_TICK=1500 --extra-file
tests/harness/games/trilbysnotes/ACSETUP-OFF.CFG:ACSETUP.CFG`, sound off, C1 on in both arms (default).
Arm A: as is (32-bpp mode 0x1B0). Arm B: `--env SDL_DOS_PACK24=1` (24-bpp mode 0x0112, packed).
Order **A B B A**, tags C2PA1, C2PB1, C2PB2, C2PA2.

**VOID a run if any of:**
1. staged sha256 or `binary_sha12` differs from the above, or `build_dirty` is not 0;
2. the engine's mode line is not `640 x 480 (32-bit)` (both arms: the engine always sees a 32-bit surface);
3. arm B's STDOUT lacks `DOS-PORT pack24 engaged mode=0x0112 640x480 vram_pitch=1920 src_pitch=2560
   path=lfb` or the exit line `DOS-PORT pack24 active=1 mode=0x0112`; or arm A has any `pack24` line.
   The pack engages only for a 24-bpp mode whose masks are R16/G8/B0 (`DOS_ModeIsPack24Candidate`),
   so the engaged line is itself the evidence of the 486's colour layout; no SDL trace is needed;
4. `alphafast calls=0` (C1 must be on in both arms);
5. more than one manifest block, or an SDL trace was collected;
6. **the witness**, judged by the **camera**, since the capture card may not lock the 24-bpp mode:
   - arm B's monitor picture must match arm A's frame for frame in content and colour: the
     parchment title, the forest greens, the blue character, the text box;
   - no horizontal stripes, no skew or shear (a wrong pitch), no colour-channel swap (wrong byte
     order), no snow;
   - any of those makes the run VOID, and the finding is reported (it would mean the 486's 0x0112
     is not what the mode info says).
   The card sheet is reviewed too, if it locks.

**Predictions, with the arithmetic (every input measured; stated before the run):**

*Inputs:*
- S2Q1-fixture pushes: 21.3k px per present, whole run (lab: 33.6M px / 1575 presents, run
  `g2b-screen-S-1`; LS2Q 134.9 MB / 4 B / 1585 = 21.3k).
- BW32 (486): 32 bpp 7.70 MB/s; 24 bpp rects 20.2-27.0 MB/s, block 27.2.
- C1PB (486): present 11.52 ms per call. Skip ticks (54 `skipframe` samples, C1PB1+B2): median total
  41.7 ms, of which present 19.0 ms (p25 14.4, p75 21.5).
- Screen: pack loop 3.20 ms per present emulated (4.16 - 0.96, fixed 40000).
- B-lite: k_R 1.13, with the 1.25x render-bound under-prediction C1P showed.

*P1 -- arm A reproduces C1PB* (same binary family, +0231, same fixture):
- present 11.52 +- 10% ms;
- stable 36.37 +- 1.5.
- Model check: 21.3k px x 4 B / 7.70 MB/s = 10.55 ms of bytes. The other ~1 ms is 32-bpp rect
  inefficiency (5.7-7.6 MB/s for rects).

*P2 -- arm B `present_update_window` mean per call:*
- bytes: 21.3k x 3 B = 63.9 KB at 20.2-27.0 MB/s = **2.3-3.0 ms**;
- pack CPU: 3.20 ms emulated x k_R 1.13 = **3.6 ms**; x 1.41 (with the 1.25 render bias) = **4.5 ms**;
- the loop's three LFB stores per four pixels can overlap its ALU work (486 write buffer) partly
  or not at all:
  - fully overlapped: max(CPU, bytes) = 3.6-4.5 ms;
  - not at all: CPU + bytes = 5.9-7.5 ms;
  - half: **5.3 ms**.
- **PREDICTED: 5.3 ms (range 3.6-7.5)**, from 11.52.
- **Falsified if B's mean exceeds 7.5 ms** (less than a 35% cut, as 9.4 set), **or is under 3.0 ms**
  (faster than the CPU part alone: the model would be wrong in kind).
- Also scored, unchanged: 9.4's earlier prediction, 4.5 (3.6-5.5).

*P3 -- skip-tick present (median of B's `skipframe present`):*
- A's median skip-tick present is 19.0 ms, about 19.0 / 11.52 x 21.3k = 35.1k px.
- B: 35.1k px x (5.3 / 21.3k) ms/px = **8.7 ms (range 5.9-12.4)**.
- **Falsified if B's median exceeds 12.4 ms.**

*P4 -- stable rate:*
- busy per render: 20.98 - (11.52 - 5.3) x 1.077 presents/render = about 14.3 ms, well inside
  the 24.6 ms tick;
- skips come from spikes: a median skip tick falls from 41.7 to about 41.7 - (19.0 - 8.7) = 31.4 ms;
- overrun per spike: 17.1 -> 6.8 ms, so skips about 157 x 6.8/17.1 = about 62;
- stable about 40.6 x (1 - 62/1499) = **38.9 (range 37.5-39.9)**.
- **Falsified if B's stable rate is under 37.0** (the present cut did not reach the skips).
- Not predicted to meet the S32 bar: sound is off, and 39.2 sits inside the range, not below it.

*P5:* `render_backbuffer` and `scene_construct` per call unchanged +-10% (C2 touches only the push).

*P6:* PH01.BMP identical A vs B (the engine surface is the same). A check, not a void.

**9.8 precondition: MET (2026-09-24).** `G2/hw0210-B-1`: the staged binary itself
(`binary_sha12=a2485a373bd2`, `build_dirty=0`), S2Q1 fixture with G2b's conditions, `SDL_DOS_PACK24=1`:
- `pack24 engaged mode=0x0112 640x480 ... path=lfb`;
- **`pushed_px=34037190`** and **PH01 `50e4283a24be`**, both identical to G2b's B runs;
- `render_passes` 1501;
- no `recthash` line (0211 absent; its hint is ignored);
- `alphafast calls=10114 mid_px=0`.
The 0210-only build pushes exactly the pixels the 0210+0211 build verified.

### 9.9 RESULT: C2P (round C, 2026-09-24) -- C2 on the 486: present **11.53 -> 6.72 ms**, stable **36.37 -> 37.52**

Raw: `~/git/dosags/tests/harness/results/C2P{A1,B1,B2,A2}-2026-09-24/`. **No VOID:**
- every run: `a2485a373bd2`, `build_dirty=0`, exit 0, `640 x 480 (32-bit)`, one manifest, `alphafast calls` 9130-9388;
- B: `pack24 engaged mode=0x0112 640x480 vram_pitch=1920 src_pitch=2560 path=lfb` and
  `pack24 active=1 mode=0x0112 pushed_px=31138950`; A: no pack24 line;
- **witness:** all eight sheets reviewed. The camera shows B's 24-bpp picture right: parchment
  title, forest greens, the blue character, speech text, no stripes, skew, channel swap or snow.
  The card locked the 24-bpp mode as well.
- PH01 `50e4283a24be` in all four.

| run | present ms/call | rb | scene | steady | skipped | **stable** | busy/render | stall ms | `fps_p50` |
|---|---|---|---|---|---|---|---|---|---|
| A1 (32 bpp) | 11.53 | 4.15 | 5.47 | 40.63 | 157 | **36.37** | 20.96 | 53401 | 39.92 |
| B1 (packed 24) | **6.72** | 4.23 | 5.52 | 40.67 | 116 | **37.52** | 18.71 | 49134 | 40.00 |
| B2 (packed 24) | **6.72** | 4.23 | 5.52 | 40.67 | 116 | **37.52** | 18.71 | -- | 40.00 |
| A2 (32 bpp) | 11.53 | 4.15 | 5.48 | 40.66 | 158 | **36.37** | 20.97 | -- | 39.92 |

| prediction (9.8) | predicted | measured | verdict |
|---|---|---|---|
| P1 A reproduces C1PB | present 11.52 +-10%, stable 36.37 +-1.5 | 11.53, 36.37 | **holds** |
| **P2 B present per call** | **5.3 (3.6-7.5); falsified > 7.5 or < 3.0** | **6.72** | **holds** (upper half) |
| (9.4, scored as promised) | 4.5 (3.6-5.5) | 6.72 | **misses** |
| **P3 skip-tick present, median** | **8.7 (5.9-12.4); falsified > 12.4** | **13.6** (34 samples) | **FALSIFIED** |
| P4 stable | 38.9 (37.5-39.9); falsified < 37.0 | 37.52 | holds, at the lower edge; skips 116 vs ~62 estimated |
| P5 rb, scene +-10% | unchanged | +1.9%, +0.9% | holds |
| P6 PH01 A = B | identical | identical | holds |

**P2, what 6.72 says about the model:** it sits at the "no overlap" end of the arithmetic (CPU 3.6-4.5
+ bytes 2.3-3.0 = 5.9-7.5). On the 486, the pack loop's LFB stores do **not** overlap its ALU work to
any useful degree: the time is CPU plus bus, not the larger of the two. 9.4's 4.5 assumed a lighter
loop and full overlap, and it misses. Per pushed pixel: 11.53 -> 6.72 ms over ~20.9k px, **0.55 ->
0.32 us** (0.58x).

**Where the present saving went (the coordinator's question, read from the phase totals, A1 vs B1):**
- `present_update_window` fell 6.69 s in total. **4.27 s of that is inside stall ticks** (`stall_ms`
  53.4 -> 49.1 s): the fades' full-frame pushes, which busy and the stable rate exclude by
  definition.
- Of the rest, the machine now idles more (`wait_next_frame` +2.21 s) and renders 41 more frames
  (each ~16 ms), so busy per render falls only 20.96 -> 18.71.
- The gain is real but lands partly where the gate does not count it.

**Why the skips fell only 157 -> 116 (P3 falsified), from the per-skip samples (`skipframe`, A 52 / B 34):**

| median of skip ticks | A | B |
|---|---|---|
| total | 44.9 ms | 34.6 ms |
| present | 19.5 | **13.6** |
| render_backbuffer | 8.1 | 8.1 |
| scene_construct | 8.7 | 8.6 |
| other | 7.2 | 4.0 |
| `present_px` (engine's own count) | 112,073 | 112,073 |

1. On the ticks that skip, C2 cut the present by only 0.70x (19.5 -> 13.6), not the whole-run
   0.58x. These are the heavy frames (the engine's `present_px`, the same median in both arms),
   and per pixel they cost B more than the mean present does. P3 scaled A's skip-tick present by
   the mean per-pixel ratio, and that is what failed. Why heavy frames pack less well is not
   established; the per-px figures above are all the record holds.
2. A B skip tick still takes 34.6 ms against a 24.6 ms tick. **Even with a free present it would
   take about 21 ms of rb + scene + other.** On these frames `render_backbuffer` (8.1) and
   `scene_construct` (8.6) run at about 1.9x and 1.6x their per-call means (4.2 and 5.5). The
   remaining skips are heavy-content frames that the render side alone brings close to the budget.
3. Even with the measured totals, the linear overrun model is optimistic. Overrun per spike falls
   20.3 -> 10.0 ms, and 157 x 10.0/20.3 = 77 skips, against 116 measured. Skips come in runs,
   and a tick that owes time carries it forward, so halving the spike does not halve the skips.
   P4's estimate of ~62 was built on the P3 input, which was falsified.

**Standing:** C1 + C2 together take S2Q1's sound-off stable rate from 35.35 (C1P A) to **37.52**,
and `fps_p50` to 40.00. The S32 bar (39.2, sound on) is not met. What stands between them, on the
record: heavy-frame ticks where present (13.6) + render_backbuffer (8.1) + scene_construct (8.6)
exceed the tick, and then sound's own cost on top. The next lab step is to find what makes those
frames heavy (dirty area, background restore, sprite count), from the lab work vector on the same
fixture, before proposing C3.

## 10. PRE-REGISTRATION: S32S1 -- the first sound-on 32-bit cell since C1/C2 (next batch)

The S32 bar is sound ON. Since C1 and C2 there has been no 32-bit figure with sound on. This one cell
states where sound leaves S2Q1. It is a measurement to plan from, not a gate attempt.

- **Binary:** the landing build of C1+C2 on dosags main (section 11: `binary_sha12` and sha256
  there, `build_dirty=0`).
- **Fixture:** S2Q1 with sound: `run-hw.sh agsquest --env SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1
  --env DOSAGS_FORCE_COLOR_DEPTH=32 --env DOSAGS_TAS_AUTO_EXIT_TICK=1500 --env SDL_DOS_PACK24=1
  --extra-file tests/harness/games/5days/ACSETUP-ON.CFG:ACSETUP.CFG`.
  - That cfg is `trilbysnotes/ACSETUP-OFF.CFG` with only `[sound] enabled=1` changed (diffed), so
    the rung is S2Q1's.
  - PGSB (PicoGUS in SB mode), OPL3 music (no backend hint), the target's own BLASTER.
  - Tag S32S1, one run.
- **VOID if:**
  - the binary hash or `build_dirty` differs;
  - the mode line is not `640 x 480 (32-bit)`, or there is no `pack24 engaged mode=0x0112 ... path=lfb`;
  - `alphafast calls=0`;
  - `audio_vital_status` does not show `pcm=sb` and `midi=opl3`;
  - more than one manifest, or an SDL trace;
  - the camera witness is not clean (as in 9.8).
- **Predictions (fixed now):**
  - *A1 audio counters (the S32 audio bar):* `underruns=0`, `overwrites=0`, MIDI `late_writes=0`,
    `pcm_irqs` > 0, `silent_irqs=0` outside room loads.
    - Basis: SB5O (0 late of 12,233 writes, isr), SB3S (0 overwrites).
    - Falsified by any nonzero `late_writes` or `overwrites`.
  - *A2 stable rate:* sound costs time on every tick (the SB IRQ, the MIDI plan, mixing).
    - At 16 bpp the same demo went 37.78 (AQF1) -> about 34.3 with sound (SB3S): about -3.5.
    - **Predicted: 34.8 (range 33.0-37.0)**, from C2P B's 37.52 sound-off.
    - **Falsified if above 37.52** (sound cannot make it faster) **or below 31.0.**
    - **Not predicted to meet the S32 bar (39.2).**
  - *A3:* `fps_p50` 39-40; present per call 6.72 +- 10% (C2P B), the push being unaffected by sound.
- **What it decides:** the size of the gap S32 still has with sound on, and which phase sound's
  time lands in (from the tickstats deltas against C2P B). That becomes the input to the
  heavy-frame read-first and any C3.

**RESULT NOTE (2026-09-24, see 16): two of this pre-registration's arms failed.**
- **A1 was vacuous, and that is my pre-registration error.** Nothing played in the 1500-tick
  window (`pcm_irqs=0`, `midi=none`). AGS Quest's AutoPilot only starts its audio phase at tick
  3144, past the auto-exit I chose. A1 tested nothing.
- **A2 is FALSIFIED.** Measured stable 27.27, below the 31.0 floor. The cause is SDL's 10 ms
  silence throttle sleeping the game loop (16.1; D2 in 17), which this prediction did not know of.

## 11. LANDING RECORD: C1 (ags 0231) + C2 (SDL 0210) + the 0230 work vector on dosags main (2026-09-24)

**Applied series gains exactly:**
- `patches/ags/0230-...work-vector-deterministic-counts.patch`. It was regenerated: its two
  `SCMD_CALLEXT` counter lines moved below the argument conversion so that lab-mmd's 0295, which
  rewrites that case's first lines, still applies after it. Same increments, still before the
  engine call.
- `patches/ags/0231-...exact-fast-path-for-32-bit-alpha.patch`.
- `patches/SDL/0210-pack24-present-32bit-surface-through-24bpp-mode.patch`. It is hint-gated
  (`SDL_DOS_PACK24=1`); making it default-on is an operator decision.

No lab-only patch enters the series. SDL 0211 (verifier + rect hash) stays a record under
`results/LABS32-2026-09-23/C2-split/`.

**Checks on the exact tree:**
- `make patches` on clean trees: the full series applies (ags ..0213, 0230, 0231, 0293, 0295;
  SDL ..0197, 0210).
- `make verify-patches-applied` exits 0.
- Clean build: **`binary_sha12=d37c10b9f891`, `build_dirty=0`**, sha256
  `a24c3de41086aa533f1b1c0f5e2546ee6f665393aa3152b64f9dc13f8d450f3c` (`build/land/ags.exe`).
  `alphafast` and `pack24` strings are present; no `recthash`/`PACK24_VERIFY`.

**Gate (full `gate-alias.sh` on `d37c10b9f891`):** `results/GATE-land-C1C2-2026-09-24/`.
- 12/14 rows A == B, 14/14 controls fail as required.
- `agsquest-alias-y60`: FRZ05 froze at 1600 vs 1601 (the known one-tick divergence, quarantined);
  the other 9 freezes are equal.
- `shards-alias-512x384`: did not run. The Shards package is game data, gitignored, and was absent
  in the lab worktree.
- **Solo re-run** (`results/GATE-land-C1C2-2026-09-24-rerun/`, Shards package staged locally from
  main's tree, not committed):
  - `agsquest-alias-y60`: **10/10 equal**;
  - `shards-alias-512x384`: tick 100 only differs, bbox `(512, 513, 1152, 913)` (the
    pre-existing, quarantined Shards defect); ticks 300-900 equal.
- Under the rule "every row A == B except the quarantined rows", the gate **passes**.

## 12. Heavy-frame read-first (S2Q1 fixture, C1+C2 on the 486). Facts first; no C3 here.

Sources, all hardware:
- C2P's own `persec` (ticks, renders) and, because 0230 ships, **`workpersec`** (cumulative pushed
  bytes, composited sprite px, background-restore px), once per second;
- the `skipframe` samples;
- `AUTOPLT.LOG` phases.

Tool: `tests/harness/lab-persec-work.py RESULTDIR` (skips per second = ticks - renders, work per
render, phase).

### 12.1 Where the skips are: two scenes, not a spread

C2PB1 (C1+C2), per second:

| window | ticks | AutoPilot phase (script) | skipped | pushed kpx / render | sprite kpx / render | bg-restore kpx / render |
|---|---|---|---|---|---|---|
| quiet seconds | most of the run | settle, unlock, walking done | **0** | **6-8** | 9-12 | 6-8 |
| t=10-12 | 248-369 | `menu`: title screen (room 2), before PLAY | **25** | 18-28 | 19-27 | 16-25 |
| t=28-34 | 952-1213 | `key`: `player.Walk(88,286)`, bench interaction, speech (TTF font 3) | **61** | 19-42 | 17-29 | 13-22 |
| t=6, 14, 17 | ~128, ~424, ~547 | room entries / settle | 18 | 6-13 | 9-10 | 6-13 |
| t=2-5, 13 | 81-84, ~381 | fades / room change (mostly stall ticks) | 5 | 2995 or 152 total (full frames) | -- | -- |

About 86 of B's ~116 skips fall in the two scene windows. The A arm (32 bpp, C1 only) shows the
same windows with more skips (t=10-12: 38, t=29-31: 51, t=34: 20).

**What makes those frames heavy:** the dirty area. Per render, the pushed px, the composited sprite px
and the restored background px **rise together, 3-7x the quiet level.** One cause, three costs: a
larger dirty region is restored (bg), recomposited (sprites under the dirty clip) and pushed.

Arithmetic check against the skip ticks:
- 42k px pushed at C2's measured 0.32 us/px is about **13.4 ms**; the skip-tick present median is
  13.6 ms.
- The skip ticks' `render_backbuffer` 8.1 and `scene_construct` 8.6 ms sit at 1.9x and 1.6x their
  means, the same scaling.

### 12.2 Fades

The full-screen pushes (2995k px in a second at t=3-5; 150-200k px per render at t=13) are room
transitions and fades. Nearly all of them run in **stall ticks** (C2P's stall time fell 4.27 s with
C2, 9.9), so they cost about 5 skips. They matter for the transition journey, not for the stable
rate.

### 12.3 Why C2's per-pixel cost is higher on heavy frames: measured, cause not established

At matched engine `present_px` (skipframe samples, 20k-px bins), B/A present is:

| `present_px` bin | 60-80k | 80-100k | 100-120k | 120-140k | 180-200k |
|---|---|---|---|---|---|
| B / A | 0.76 | 0.66 | 0.68 | 0.67 | 0.63 |

The whole-run ratio is 0.58. **So selection explains part of 9.9's 0.70, not all: on heavy frames a
pushed pixel costs C2 relatively more.** Candidates, none tested:
- (a) many narrow rows: the pack pays about 15 instructions of setup per row plus a byte-wise tail,
  while the 32-bit path's per-row overhead hides under its 7.7 MB/s bus time;
- (b) source rows evicted from the 486's 8 KB L1 by the larger composite: the CPU-bound pack pays
  the misses, the bus-bound 32-bit push hides them;
- (c) rect-shape effects on LFB write efficiency. BW32's rect rows argue against this (24-bpp narrow
  rects lose relatively less than 32-bpp ones).

### 12.4 What is not known, and the measurement that would say (proposed, not run)

Unknown:
- the geometry of the dirty rects in the two windows (how many rects, rows, widths; what dirties
  them: the walking sprite's box, the speech overlay, a GUI);
- the title-screen window's content (what animates at ticks 248-369).

**Proposed lab measurement H1-GEOM:**
- a lab-only per-present geometry log (0211-style, hint-gated, never in the applied series): per
  present, the tick, rect count, total rows, row-width histogram (<=32, <=64, <=160, <=320, >320
  px) and pushed px;
- S2Q1 fixture, no fixed timestep (so every tick renders the same content), fixed 40000;
- quiet ticks compared with ticks 248-369 and 952-1213.

It answers the dirty-area shape and candidate (a) directly, and names what is being redrawn. (b)
needs the 486, and would only get a cell if (a) does not explain it.

## 13. PRE-REGISTRATION: H1-GEOM (coordinator GO 2026-09-24; written and committed before the run)

**Question:** why a pushed pixel costs C2 relatively more on heavy frames (B/A 0.63-0.76 at matched
`present_px`, against 0.58 for the whole run; 12.3). This tests candidate (a), narrow rows.

**Instrument:** SDL 0212, **lab-only** (hint `SDL_DOS_GEOM_LOG=1`; record copy
`results/LABS32-2026-09-24-H1GEOM/0212-geom-log-LAB-ONLY.patch`; never in `patches/`). One line per
update: `DOS-PORT geom p= rects= rows= px= w32= w64= w160= w320= wbig=` (rows per rect-width bucket,
rects as the engine passed them). Binary `build/lab/GEOM` = the landed series + 0212, built without
the verify step (the safety check rightly refuses a vendor tree ahead of `patches/`).

**Run:** `results/LABS32-2026-09-24-H1GEOM/h1geom.sh`:
- S2Q1 fixture (forced-32, auto-exit 1500), `SDL_DOS_PACK24=1`;
- fixed 40000 24-bpp conf, **no `--fixed-timestep`** (every tick renders, so each frame's content is
  the tick's);
- one EXCLUSIVE lock.
Present index -> tick via the run's own `persec` rows (tick, cumulative real presents), linear within
a second.

**Windows (from 12.1):** HEAVY = ticks 248-369 and 952-1213. WHOLE = every present.
QUIET = ticks 540-940 and 1250-1500.

**Model for (a):**
- C2's time per present = a x px + c_row x rows. The 32-bit push hides its per-row cost under its
  7.7 MB/s bus time, so A = b x px, with b = 0.55 us/px (C1P/C2P A).
- The B/A ratio is then R = a/b + (c_row/b) x rho, where rho = rows / px.
- The measured rise from the whole run (R 0.58) to heavy frames (R 0.67) needs
  **c_row = 0.09 x 0.55 / (rho_HEAVY - rho_WHOLE) us per row.**

**Verdict on (a), fixed now:**
- **CONFIRMED** iff rho_HEAVY > rho_WHOLE **and** the implied c_row <= 2.0 us (130 cycles at 66 MHz;
  the pack's per-row call, setup and byte-wise tail is roughly 30-60 cycles, and anything up to
  2 us is within reach of cache effects on the row start).
- **KILLED** iff rho_HEAVY <= rho_WHOLE (heavy rows are not narrower), **or** the implied c_row > 3.0 us
  (an implausible per-row cost).
- **INCONCLUSIVE** for an implied c_row in (2.0, 3.0].
- If (a) is killed, candidate (b) (L1 misses on large composites) is the remaining named
  explanation. It needs the 486, and a cell is proposed, not run.

Also reported, not part of the verdict:
- per window: px per present, rects per present, mean px per row, and the share of rows in the
  <= 32 and <= 64 px buckets;
- the DOSBox-X counts that answer "what is the dirty area's shape" (12.4).

**13 addendum (before the run): the H1-GEOM binary, and a build-hygiene catch.**
- The first GEOM build ran `cmake --build build/ags` directly, because `make build-ags` rightly
  refuses a vendor tree ahead of `patches/`. It inherited that directory's cached configure flags,
  so the binary would have stamped itself `binary_sha12=d37c10b9f891 build_dirty=0`: the landing
  binary's identity, on different code.
- Caught before any run (the queued run was stopped while still waiting for the lock). Rebuilt in a
  separate build directory (`build/lab-geom-build`) with an explicit lab stamp.
- **H1-GEOM binary: `build/lab/GEOM/ags.exe`, `binary_sha12=lab0212geom0` (a label, not a series
  fingerprint), `build_dirty=1`, sha256 `562e9804c5217989ebf1af29835ed7f281377a03893980d7695342d622b938c0`**
  (landed series + lab-only SDL 0212).
- The relinked `build/ags/ags.exe` was deleted. The landing binary of record stays
  `build/land/ags.exe` (sha256 `a24c3de4...`).
- **Before any later landing build from this worktree:** `make patches` (apply-patches resets the
  vendor trees; 0212 is saved as a `.patch` beside these results), then an SDL rebuild, then
  `make build-ags` with the verify step.

### 13.1 H1-GEOM RESULT: candidate (a) **KILLED** -- heavy frames push *wider* rows, not narrower

Raw: `results/LABS32-2026-09-24-H1GEOM/` (RUNMANI, STDOUT with 1603 `geom` lines, AUTOPLT, PH01).
Run valid:
- `binary_sha12=lab0212geom0`, `build_dirty=1`, exit 0;
- `render_passes` 1501 (= ticks + 1, no skip);
- `pack24 ... pushed_px=34037190`, identical to G2b, so these are the same frames.
Scored by `tests/harness/lab-h1geom.py` (committed before the results were read, 95c2bdda).

| window | presents | px / present | rects / present | **px per row** | rows in rects <= 32 px | <= 64 px |
|---|---|---|---|---|---|---|
| HEAVY (ticks 248-369, 952-1213) | 389 | **24,609** | 5.04 | **137.6** | 29.3% | 25.7% |
| QUIET (ticks 540-940, 1250-1500) | 652 | 7,004 | 4.92 | **44.9** | 27.5% | 38.5% |
| WHOLE | 1603 | 21,233 | 4.57 | 132.8 | 25.0% | 29.9% |

- rho_HEAVY - rho_WHOLE = -0.00026 rows/px <= 0: **(a) KILLED as registered.** Heavy frames' rows are
  3x wider than quiet frames' and as wide as the whole run's (which the fades' full-width frames
  dominate).
- **The shape of the heavy frames (12.4's first question):** the same number of rects per present
  (about 5) as quiet frames, but each much larger. Pushed area is 3.5x, rows are 3x wider. The heavy
  windows redraw larger regions, not more pieces. Which objects they are (walk box, speech overlay,
  GUI) is not in this log; it records sizes, not positions.

**POST HOC (labelled; not a registered test): a width model also fails to explain the anomaly.**
- BW32's rect rows give the 32-bit push a per-pixel cost that falls with row width (0.673 us at
  32 px -> 0.505 at 640 px), while C2 carries a flat pack CPU cost (0.21 us/px, from the whole-run
  0.32) plus 24-bpp bytes.
- So B/A rises with width: 0.52 at 32 px -> 0.62 at 640 px.
- At the measured widths that model gives QUIET 0.544, WHOLE 0.593, **HEAVY 0.594**. It separates
  quiet from heavy frames but **not heavy from whole**, and heavy against whole is the anomaly
  (0.63-0.76 against 0.58).

**Where the per-pixel anomaly stands:**
- **Unexplained.** Remaining candidates:
  - (b) L1/cache effects on large composites (needs the 486);
  - (d) a sampling artifact. The `skipframe` `present` and `present_px` are deltas over the interval
    since the previous snapshot (`game_run.cpp` ~2425-2450), not single frames, so 12.3's
    matched-bin comparison compares intervals whose frame content can differ between arms.
- It does not change the practical reading: **the skip ticks' cost scales with dirty area** (12.1),
  and at C2's rates a 24.6k-px present is about 8 ms on the whole-run ratio, or 13.6 ms measured on
  skip ticks.

**H1-GEOM is written up.** Directions the data points to, not yet a proposal: cut the work that scales
with the dirty area on heavy frames (restore + recomposite + push of about 25k px each).
- **(i)** Find which objects make those regions 3.5x larger. That needs positions (a lab-only
  position log) and the AutoPilot's own script: the walk, the bench interaction, the TTF speech.
- **(ii)** Cheaper per-px work in background restore and compositing at 32 bpp; `bg_restore` and
  `render_backbuffer` scale with the same area.
- The vendor tree is back to the applied series (`make patches`; SDL HEAD 0210; `verify` exits 0).

## 14. PRE-REGISTRATION: H2-POS -- which objects make the heavy regions 3.5x bigger (coordinator GO; before the run)

**Known going in** (patch 0175's whole-run totals, C2PB1 on the 486):
- room-sprite marks: 6,760, 9.09M px (about 1.3k px each);
- UI-sprite marks: **281, 4.60M px (about 16.4k px each)**;
- cursor: 80k px.
The UI stage marks rarely but hugely. Per-frame and per-object attribution is missing.

**Instrument:** ags 0232, **lab-only** (env `DOSAGS_DIRTY_LOG=1`; record copy
`results/LABS32-2026-09-24-H2POS/0232-dirty-log-LAB-ONLY.patch`; never in `patches/`). It logs every
screen-space dirty mark at 0175's choke point (`dos_port_dirty_add_screen`):
`DOS-PORT dirtylog tick= src= kind= id= x1= y1= x2= y2= px=`.
- The draw-list adders tag each entry with its object: 1 room object (id), 2 character (id), 3 room
  overlay, 4 walk-behind, 5 UI overlay (overlay id), 6 GUI (gui index).
- Marks not made from the draw list (0197's object-flush, the 0193 carry, text) log kind 0 with
  their source.

**Binary:** `build/lab/DLOG/ags.exe`, `binary_sha12=lab0232dlog0` (a label), `build_dirty=1`, sha256
`55ed59ff4e8283e3d85c18cc2ff913d041b179fa0b983463a38383c4ccb39476`. Built in its own directory
(`build/lab-dlog-build`) from the landed series + 0232.

**Run:** `results/LABS32-2026-09-24-H2POS/h2pos.sh`:
- S2Q1 fixture, `SDL_DOS_PACK24=1`;
- fixed 40000 24-bpp conf, **no `--fixed-timestep`**;
- one EXCLUSIVE lock.
**VOID if** `pushed_px` differs from 34,037,190 (H1-GEOM's and G2b's: the same frames), or
`render_passes` differs from ticks + 1.

**Reading (fixed; scorer `tests/harness/lab-h2pos.py`, committed with this):**
- Per (source, kind, id): marked px per tick in HEAVY (ticks 248-369, 952-1213) and QUIET
  (540-940, 1250-1500); **excess = HEAVY rate - QUIET rate**.
- **THE CAUSE** iff one (source, kind, id) carries >= 50% of the total positive excess. Otherwise
  the heavy regions have a **SPREAD** cause, and the top three are named with their shares.
- Marked px are the regions asked for, before the box set merges them. They are proportional to,
  not equal to, what is pushed. Reported as such.
- Ids are resolved to names (character/object/GUI) from the AutoPilot script and the game's own
  data where the log alone cannot say.

### 14.1 H2-POS RESULT: registered verdict THE CAUSE = the carry (52.0%); the object behind it is the **speech overlay** (`OVER_TEXTSPEECH`, 46.5% directly)

Raw: `results/LABS32-2026-09-24-H2POS/` (16,440 `dirtylog` lines). **Valid:** `binary_sha12=lab0232dlog0`,
`build_dirty=1`, exit 0, `render_passes` 1501, `pushed_px=34037190`: the same frames as H1-GEOM and G2b.
Scored by `lab-h2pos.py` (committed before the run).

Marked px per tick: HEAVY **38,299**, QUIET **13,854** (x2.76).

| source / object | HEAVY px/tick | QUIET px/tick | excess | share of excess |
|---|---|---|---|---|
| carry (0193: last frame's marks kept for the next present, as merged boxes) | 19,625 | 6,893 | 12,733 | **52.0%** |
| UI overlay id 4 = **`OVER_TEXTSPEECH`** (`runtime_defines.h`) | 11,384 | **0** | 11,384 | **46.5%** |
| GUI 2, GUI 4, other UI | 372 | 0 | 372 | 1.5% |
| room objects 0-3, cursor | same in both windows | | ~0 | 0.0% |

**Registered verdict: THE CAUSE = carry (52.0% >= 50%), as written.**

**Reading it (descriptive; not a second verdict):**
- The carry is not an object. It is patch 0193's re-marking of the previous frame's regions for
  the next present, so its heavy excess is an echo of the heavy frames' own marks.
- The only object whose marks exist in the heavy windows and not in the quiet ones is the
  **speech overlay**.
- Descriptive split by window: title 248-369 carries 23.0k px/tick of carry + 15.3k of speech
  overlay; key 952-1213 carries 18.0k + 9.6k; quiet 540-940 carries 6.8k + 0.
- The speech overlay's marks run from tick 260 to 1191 in three recurring bboxes, each about
  **390-440 x 38-48 px, each held for about 39 frames**: a Say() line that stays put while it is
  shown.
- **It is re-marked on every frame it is shown.** Patch 0169's unchanged-source skip
  (`SkipInvalidate`) is only ever passed for GUIs, never for overlays. The carry then marks it
  again for the next present.
- **So the heavy regions are the speech text box, marked every frame it is shown and doubled by
  the carry.** Room objects 0-3 (3.4k + 1.9k + 0.3k px/tick) cost the same in every window.

**Answer to 12.4's question:** the frames that skip are the frames with a speech line on screen, on
the title screen and in the walk to the bench. Their dirty area is dominated by re-marking a static
speech box and its carry echo.

**Not yet a proposal (C3 is held until S32S1's sound-on result, per the coordinator):**
- The direction this points to: mark an overlay dirty only when its image or position changed,
  as 0169 already does for GUIs. It stays composited in full, as 0169 does.
- Upper bound, labelled as an estimate: heavy marked px/tick 38.3k -> about 14k, the quiet level,
  if a static speech line were marked once rather than every frame (the carry echo goes with it).
- The vendor tree is back to the applied series (`make patches`; verify exits 0).

## 15. C3 READ-FIRST AND DESIGN: an overlay is marked dirty only when it changed (ags 0233; no code yet)

Coordinator GO for read-first and design (2026-09-24). Code waits for S32S1 (in round D now). Every
claim below cites the code it was read from (`vendor/ags` at the landed series).

### 15.1 What counts as "overlay changed" (the coordinator's (1))

The overlay's own change flag is **incomplete**, exactly as GUIs' flags were before 0190/0191:
- `ScreenOverlay::MarkChanged()` fires on `SetImage`, `SetSpriteNum`, `SetScaledSize`
  (screenoverlay.cpp 79/104/126) and in overlay.cpp (476: text re-render; 552: forced recreate).
- It does **not** fire on `SetPosition`, `SetTransparency`, `SetZOrder` or `SetVisible`
  (screenoverlay.cpp 60-90; screenoverlay.h 106-117).
- Shared-sprite edits (DrawingSurface on a dynamic sprite) reach the overlay only as its texture's
  notify mark: `game_sprite_updated -> notify_sprite_changed -> *NotifyMark = UINT32_MAX` (draw.cpp
  1259-1289), read as `overtx.IsChangeNotified()`.
- The flag is read and cleared inside the prepare loop (draw.cpp ~3229-3269:
  `has_changed = over.HasChanged()`, plus the room-layer position check when walk-behinds crop,
  plus the software-mode unloaded-asset recache, then `over.ClearChanged()`).

**C3's definition, in two parts, mirroring 0190 + 0191 for GUIs:**
1. **Captured flag (0190-style):** per overlay slot, `changed = has_changed || overtx.IsChangeNotified()`,
   recorded in the prepare loop *before* `ClearChanged()`, the same expression that decides the
   texture re-sync. That covers:
   - image replacement, text re-render (TTF glyphs are rendered into the overlay image by
     `SetImage`, so any new text is a new image), scaled size, and shared-sprite edits;
   - the portrait's frame and blink changes (update.cpp ~575-584: `game_sprite_updated(...)` then
     `face_over->MarkChanged()`).
2. **Prev record (0191-style), compared at add time:**
   - overlay id (catches slot reuse after removal);
   - sprite number;
   - final drawn position (`get_overlay_position`, i.e. x/y plus offsets; room coordinates for
     room-layer overlays);
   - scaled width and height;
   - transparency;
   - z-order;
   - alpha-channel flag;
   - room-layer flag.
   Any difference means changed.

**Shown/hidden and removal:**
- An overlay that was drawn last frame and is not drawn this frame (hidden, fully transparent,
  removed, or slot freed) gets its **old rect marked once**, like 0194 for GUIs and 0197 for room
  objects. Today that repaint happens only through the 0193 carry of last frame's mark, which C3
  would remove.
- Late flush, as 0191: an overlay left unmarked last frame and changed now has its **old** rect
  marked too (its new rect is marked by the normal invalidation).
- Room-layer overlays are flushed in room space (`invalidate_rect(..., true)`), UI overlays in
  screen space.

### 15.2 Content under a static overlay (the coordinator's (2)), and a correctness condition 0169 does not state

- Whatever changes under a static overlay marks its own rect (room sprite, character, object, the
  0197 object flush), so the background restore repaints it.
- The overlay is still **composited** every frame: `add_to_sprite_list(..., skip_invalidate)` only
  sets `SkipInvalidate`, and the entry stays in the draw list (draw.cpp ~1663-1676). So it is drawn
  over the changed content. That is 0169's argument for GUIs (draw.cpp ~2980-2996), and the
  overlay path takes the same route.
- **But the unmarked entry's composite is clipped by 0170 to the dirty BBOX, not the box union**
  (ali3dsw.cpp ~810-826: "can only draw too much, never too little"). Inside that bbox, in the gaps
  between restored boxes, the overlay is drawn again over **last frame's pixels, which already
  contain it**. That is harmless only if re-compositing is **idempotent**: an opaque blit, a masked
  blit, or an alpha blend whose alpha is only 0/255 (C1's proof), at full opacity. A partial-alpha
  or semi-transparent overlay would **double-blend** in those gaps.
- **C3 therefore skips only idempotent overlays:** transparency 0 (engine alpha 255) **and** no
  alpha channel. AGS Quest's speech box qualifies: it never appeared among C1's alpha-blended
  textures (LABALPHA, 7.1). Binary-alpha overlays could be admitted later by a once-per-sync alpha
  scan; that is not in C3.
- **Finding, reported and not fixed here:** 0169 skips GUIs with no such condition. A 32-bpp game
  whose skipped GUI has partial alpha would double-blend in the bbox gaps. AGS Quest's GUIs are
  0/255 only (C1's scan), so no current fixture shows it. It goes to the coordinator as a latent
  defect for 0169.

### 15.3 The carry echo (the coordinator's (3))

- 0193's carry is `post_box`, filled only by `dos_port_dirty_add_screen` from real marks made after
  the interval's restore (draw_software.cpp ~474-480).
- It is replayed next present by `dos_port_dirty_merge_carry` with `restore_seen` off, so a replayed
  mark is never re-recorded (draw_software.cpp ~622-649).
- **An overlay that is not marked contributes nothing to the next carry.** Its echo vanishes with
  its mark, except where the box set had merged it with another mark (merges only enlarge).

### 15.4 Overlay types (the coordinator's (4))

| type | created / updated | how C3 sees a change |
|---|---|---|
| `OVER_TEXTSPEECH` (4) | `Say()`: display.cpp 489, overlay.cpp 452/462-467 | each new line = `SetImage` |
| `OVER_TEXTMSG` (1) | `Display()`: display.cpp 488/521 | `SetImage` per message; removal -> hidden flush |
| `OVER_PICTURE` (3) | KQ6-style portrait: character.cpp ~3026/3088; animated in update.cpp ~541-584 | frame and blink changes: `game_sprite_updated` + `MarkChanged` |
| `OVER_COMPLETE` (2) | QFG4 full-screen portrait: character.cpp ~3010 | same as picture |
| custom (>= 5) | `Overlay.CreateGraphical/CreateTextual`, `SayBackground` (global_character.cpp 593, timeout -> removal) | Text/Graphic -> `MarkChanged`; X/Y/Transparency/ZOrder -> prev record; removal -> hidden flush |
| room-layer overlays | `Overlay.CreateRoomGraphical/Textual` (`kOver_RoomLayer`, overlay.cpp 450-456) | same, recorded in room coordinates; a camera move already invalidates the whole viewport |

Each row is exercised by a gate row (15.5) or named as untested.

### 15.5 Gates (pre-registered; run only after S32S1 is in and C3 is written)

- **G3a:** the full `gate-alias.sh` on the C3 build. Every row A == B except the quarantined rows;
  every control with power fails.
- **G3b, the overlay gate (new BENCH scene `speech`):**
  - a `Say` line held for 120 ticks, over (i) anim12's animating objects and (ii) the player
    walking left to right beneath the box;
  - then a `SayBackground` line that times out;
  - then a room-layer overlay moved by script (X/Y only, which `MarkChanged` does not flag);
  - then a textual overlay whose Transparency goes 0 -> 50 (must NOT be skipped, 15.2);
  - then a KQ6 portrait with animation, if the BENCH character has a speech view, **else that
    row is stated untested**.
  - Run at the 8-bpp alias rung and the 16-bpp 512x384 rung (the gate's existing BENCH rungs),
    freeze-captured like gate-alias: A = C3 on, B = full-push reference.
  - **Control C = `DOSAGS_BREAK_C3=1`:** skip every overlay's invalidation regardless of change.
    It must differ from B, or the gate has no power.
  - **PASS iff A == B at every freeze in both rungs and C != B.**
- **G3c (lab):** H2-POS's reading re-run on the C3 binary (the same S2Q1 frames):
  - **HEAVY marked px/tick predicted <= 20k** (upper bound of the saving: to ~14k, the quiet level);
  - `OVER_TEXTSPEECH`'s marks fall to about one per line shown (from 273 in the windows);
  - pushed px falls in proportion;
  - **falsified if HEAVY marked px/tick stays > 30k.**

### 15.6 486 prediction (for the cell after G3a-c pass; fixed now)

S2Q1 fixture, C1+C2+C3, sound off, against C2P B (stable 37.52, 116 skips):
- **Mechanism:** about 86 of the 116 skips sit in the two speech windows (12.1). C3 brings those
  frames toward the quiet frames' work: push about 24.6k -> 8k px/render, with the restore and
  composite under the clip falling with it.
- **Skip-tick arithmetic, from C2P's 34.6 ms median skip tick:**
  - present 13.6 -> about 3-4 ms;
  - rb 8.1 -> about 5 ms;
  - scene 8.6 -> about 6 ms;
  - other 4.0 unchanged;
  - about 18-19 ms total, inside the 24.6 ms tick.
- **Predicted: skips 116 -> 35 (range 20-55)**, the rest being room entries/settle (~18) and fades
  (~5); **stable 39.7 (range 39.2-40.2)**.
- **Falsified if stable < 38.5 or skips > 70.**
- Sound-off only. The sound-on figure is pre-registered once S32S1 says what sound costs.

### 15.7 Patch and number

`ags 0233` (0232 is the lab-only dirty log, never landed; numbers stay reserved). One concern: the
unchanged-overlay invalidation skip with its hidden/late flushes and the idempotence condition.
- Env `DOSAGS_OVER_NOINVAL=0` disables it, as `DOSAGS_GUI_NOINVAL` does for 0169.
- `DOSAGS_BREAK_C3=1` is the gate's control.
- Counters in the manifest: marks skipped, flushes on hide, late flushes, non-idempotent
  refusals.

## 16. S32S1 RESULT (round D, 2026-09-24) and where sound's time goes on the 486

Raw: `~/git/dosags/tests/harness/results/S32S1-2026-09-24/`.
- **No VOID:** `binary_sha12=d37c10b9f891`, `build_dirty=0`, exit 0, `640 x 480 (32-bit)`,
  `pack24 engaged mode=0x0112 ... path=lfb` (`pushed_px=25988009`), `alphafast calls=6860`, one
  manifest.
- **Witness:** card and camera sheets reviewed. Splash, title, the forest room with one character
  instance, complete backgrounds, the text box, then the end. Clean.

| prediction (section 10) | predicted | measured | verdict |
|---|---|---|---|
| A1 audio counters | underruns 0, overwrites 0, late_writes 0, **pcm_irqs > 0**, silent_irqs 0 | underruns 0, overwrites 0, silent_irqs 0, **pcm_irqs 0**, `midi=none events=0` | **vacuous** (see below) |
| A2 stable | 34.8 (33.0-37.0); falsified above 37.52 or **below 31.0** | 40.11 x (1 - 480/1499) = **27.27** | **FALSIFIED** (sound costs far more than predicted) |
| A3 | fps_p50 39-40; present 6.72 +-10% | fps_p50 **28.97**; present 7.35 | fps_p50 falsified; present holds (7.35 <= 7.39) |

**My pre-registration's audio arm was vacuous.** Nothing played in the 1500-tick window:
- `pcm_irqs=0`, and `skipped_silent=1557` (about one per tick);
- the MIDI backend never opened (`midi=none`);
- AGS Quest's AutoPilot plays its MIDI tune and chime in its `audio` phase, which starts at tick
  about 3149 (AUTOPLT), past S2Q1's auto-exit.
So S32S1 measured **sound enabled but silent**, not playing sound.

**Confound, stated:** S32S1 ran main's `d37c10b9f891`, which adds ags 0210-0213, lab-mmd's
0293/0295 and SDL 0197 on top of C2P B's `a2485a373bd2`. There is no sound-off control on
`d37c10b9f891`. The mechanism below does not depend on those patches.

### 16.1 Where sound's time goes: a 10 ms sleep per tick, on the main thread, whenever the mixer is silent

The 486's own audio probe (`audioprb`, every 200 polls, RUNMANI) over all 1605 polls:
- `slots_us` mean about 95 us (AGS's audio slots);
- **`pump_us` mean about 11,000 us** (min 191, max 12,661).
`catchup_audio_poll` (the catch-up tick's poll): **5,272 ms over 479 calls, 11.0 ms per call**,
against 22 ms over 117 calls sound-off (C2PB1). On render ticks the same poll runs inside
`WaitForNextFrame()`, so it hides in `wait_next_frame` (11.3 ms per call, against 7.3 sound-off).

**The mechanism, read from the code:**
1. `audio_core_entry_poll()` (audio_core.cpp ~754-865) runs once per tick. dosags builds
   `AGS_DISABLE_THREADS`, so it runs on the game's **main thread**.
2. It calls `dos_audio_mixer_pump()` (dos_audio_mixer.cpp ~485): with no active voice it mixes
   nothing, then calls `SDL_DOSAudioPump()`.
3. That calls `SDL_PlaybackAudioThreadIterate()` -> `DOSSOUNDBLASTER_PlayDevice`
   (SDL_dosaudio_sb.c ~4289).
4. In `PlayDevice`, a silent buffer while content is not active takes the silence throttle:
   **`if (all_silence) { dos_port_audio_skipped_silent_count++; SDL_Delay(10); ...}`**.
The throttle was written for a background audio thread (its comment: "throttle ~100 iter/sec when
quiescent"). In the no-thread build it **sleeps the game's main loop for 10 ms (measured ~11) on
every tick with nothing to play**.

**The same throttle across the 486's other sound-on cells (pump mean vs silence):**

| cell | depth | `pcm_irqs` | `skipped_silent` | pump mean |
|---|---|---|---|---|
| S8L1-2-pcm | 8 | 2701 (playing throughout) | **0** | **0.63 ms** |
| SB5O | 16 | 1828 | 13,127 | 6.2 ms |
| SB3S | 16 | 180 | -- | 8.1 ms |
| S16U1 | 16 | 991 | 3,293 | 11.0 ms |
| **S32S1** | 32 | **0** | 1,557 | **11.0 ms** |

**Answer to the coordinator's question:**
- It is not decode, the mixer or the ISR: the mixing work is about 0.1 ms (slots) and about
  0.6 ms/pump when content plays (S8L1).
- It is **a 10 ms `SDL_Delay` per tick whenever the mixer is silent.** About 40% of the 486's
  time at 40 ticks/s. That explains S32S1's 27.3 stable against 37.5 sound-off.
- S8L1's ~1.1 ms/tick was a cell that never went silent, so it never hit this.
- **The throttle hits every depth and every sound-on cell in its silent stretches** (between
  clips, before music starts, during pauses). It is not a 32-bit problem, and it is bigger than the
  speech box (C3).

### 16.2 What follows (for the coordinator; nothing run)

- **Zero-code test available:** the existing hints `SDL_HINT_DOS_SILENCE_DETECT=0` or
  `SDL_HINT_DOS_DOS_AUDIO_QUIESCENCE_GATE=0` take `PlayDevice`'s no-delay path. Silent buffers are
  then written to the ring instead, so the SB keeps running on silence (IRQ cost as a playing
  cell, ~0.6 ms/pump).
- **A lab check is possible first:** at fixed cycles DOSBox-X's `SDL_Delay` advances emulated time,
  so the 10 ms should reproduce there. A/B that hint on the S2Q1 sound-on fixture.
- **The fix belongs in SDL** (the no-thread pump should never sleep; the throttle only makes sense
  on a real audio thread). It touches every port that pumps from its main loop, so ownership (my
  SDL range 0210-0219, or the main worker's audio work) is the coordinator's call.
- **This outranks C3.** Sound-on S32 is 27.3; removing the throttle is worth up to ~10 stable fps
  here, against C3's ~2 (15.6).

## 17. Tracked defects (found in this campaign; each gets its own patch and gate, never bundled)

| id | defect | where | status | fix direction |
|---|---|---|---|---|
| D1 | **0169's unchanged-GUI invalidation skip can double-blend.** A skipped GUI is still composited, clipped by 0170 to the dirty **bbox**. In the bbox gaps between restored boxes it lands on last frame's pixels, which already contain it. For a GUI with partial alpha, or with transparency above 0, that blends it a second time. | draw.cpp ~2980-3033 (0169/0191 skip); ali3dsw.cpp ~810-826 (0170 bbox clip) | **latent**: AGS Quest's GUIs are 0/255 alpha only (C1's scan, 7.1), so no current fixture shows it | apply C3's idempotence condition to the GUI skip: skip only a GUI with transparency 0 and no partial alpha (no alpha channel, or proven 0/255). Own small patch in the lab-metric range, own gate (a partial-alpha GUI fixture with a control). Coordinator ruling 2026-09-24 |
| D2 | **SDL's silence throttle sleeps the main thread.** `DOSSOUNDBLASTER_PlayDevice` calls `SDL_Delay(10)` on every silent buffer. In a no-thread build (dosags) the pump runs on the game loop, so every silent tick loses ~10-11 ms. | SDL_dosaudio_sb.c ~4289+ (the `all_silence` branch) | **measured on the 486** (16.1): S32S1 pump 11.0 ms/tick; stable 27.27 sound-on | the no-thread pump must never sleep. Owner and order: coordinator's call (16.2) |

## 18. PRE-REGISTRATION: C3 (ags 0233) -- fixture, fixture equivalence, G3a-G3d (written before any C3 run)

Coordinator 2026-09-24: C3 code may follow the sound breakdown; the BENCH change is OK on this
branch if no existing BENCH scene's output changes. Everything below was committed before any run
it scores. Only an unscored fixture smoke (18.2) runs first.

### 18.0 Corrections found while writing 0233 (before any C3 data)

- **0170's clip is opt-in.** It engages only with `DOSAGS_GUI_CLIP=1` (draw.cpp,
  put_sprite_list_on_screen), and no harness script or cell sets it (`/usr/bin/grep`).
  - So a skipped entry is composited over its **whole** rect every frame, not clipped to the
    dirty bbox as 15.2 and D1 say.
- **15.2 still holds, for a stronger reason.** The idempotence condition is needed across the
  whole rect, not only in bbox gaps. The condition itself is unchanged.
- **D1 is worse in kind, still latent.** A skipped GUI with partial alpha or transparency would
  blend onto itself over its whole rect on every frame. Every gate row passes and C1's alpha scan
  shows no such GUI in AGS Quest. The row in 17 stands with this correction.
- **15.6 amended (the rb term only).** C3 saves restore + push + carry, not composite: the box is
  still composited in full.
  - rb 8.1 -> about 6.5 ms (was: about 5).
  - The skip tick comes to about 20-21 ms, still inside the 24.6 ms tick.
  - Prediction and falsifier unchanged: **skips 35 (20-55), stable 39.7 (39.2-40.2); falsified if
    stable < 38.5 or skips > 70.**

### 18.1 The binary

- **C3 binary:** `build/lab/C3/ags.exe`, `binary_sha12=lab0233c3v0` (a label), `build_dirty=1`,
  sha256 `334200f6e2edebadc7befbc42db5f5f740684a7e167fcb246e06837d9331e4f1`.
  - Built in its own directory `build/lab-c3-build` from the landed series plus 0233, with the
    Makefile's own cmake flags.
  - 0233 is vendor commit `ac8f04900`. Its record is
    `results/LABS32-2026-09-24-C3/0233-WIP-not-yet-gated.patch`. It is **not** in `patches/`.
    It goes there only after G3a-G3d pass, `/sdldos:review` and the coordinator's word.
- **G3c binary:** `build/lab/C3DLOG/ags.exe`, `lab0233dlog0`, `build_dirty=1`, sha256
  `1cc0d5682aa407a48ac9425486b628ecce2bd96a6703dd46be75e51d97fae559`.
  - Lab-only 0232 (dirty log) on top of 0233, built from a side worktree
    (`build/ags-c3dlog-src`), so the main vendor tree is untouched.
  - One trivial conflict was resolved: the 0232 tag sits before 0233's add call.
- **What 0233 does** (full text in the commit message):
  - the 0190-style captured change flag;
  - the 0191-style record compared at add time: id, layer, drawn position incl. auto-placement,
    scaled size, sprite, transparency, z, alpha flag;
  - it skips only idempotent overlays (transparency 0, no alpha channel);
  - old-rect flushes: before the restore (hidden / props / flag), at add time (late), and at the
    end of the frame (safety net).
  - `DOSAGS_OVER_NOINVAL=0` switches it off; `DOSAGS_BREAK_C3=1` is the control.
  - Manifest line: `DOS-PORT overskip mode= skipped= marked= refused= hidden= props= flag= late= end=`.

### 18.2 The fixture: BENCH scene `speech` (SC_SPEECH = 8, `cfg/speech.cfg`)

- **Content:**
  - 12 spinners animate;
  - on 20-tick beats, a blocking `SayAt(8, 104, 304, ...)` of 82 characters, held ~120 ticks
    (OVER_TEXTSPEECH over spinner row 2);
  - spinner 11 moved to and fro **beneath** the box (Say stops the speaker's own walk, so the
    player cannot be the moving thing);
  - a `SayBackground` bubble (auto-placed custom overlay, timeout removal);
  - a room-layer graphical overlay moved by X/Y;
  - a screen textual overlay stepping Transparency 0..50.
- **Untested at BENCH level, stated:**
  - OVER_PICTURE / OVER_COMPLETE portraits: BENCH's character has no speech view;
  - DrawingSurface edits of a shared sprite;
  - alpha-channel overlays (none at 8/16 bpp).
- **Changes to existing code paths:**
  - the ParseLine bound (`SC_DARK` -> `SC_SPEECH`);
  - `SC_ANIM || SC_SPEECH` in BeginScene;
  - FixedPose additions that do nothing in other scenes (`StopMoving` on a non-moving object;
    removing overlays that are null).
- **Build reproducibility:**
  - AGS host tools were built from a pristine clone at the pin `94e271df` (`build/ags-pristine`).
  - The unmodified source rebuilds the current `BENCH8.ags` / `BENCH16.ags` byte for byte, except
    3 bytes twice: the sprite file's timestamp id in the header and in SPRINDEX.
- **New packages** (gitignored; installed as `games/bench8n`, `bench16n`, with the old packages
  untouched):
  - `BENCH8.ags` sha256 `0a8b22e9ed1a26ff71c5de394f61922fc102bc93684fe0269025ac1dbc38e526`;
  - `BENCH16.ags` sha256 `a9dbc3c1ad8a7ba4277716bb68818ab0ff504247c9258c89eeac2cded8b16fd1`.
- **Unscored smoke first** (`results/LABS32-2026-09-24-C3/smoke/`, landing binary, shared lock):
  does the scene run, and do its frames show each element. If the smoke forces a fixture change,
  this section is amended with the new sha256s **before** FIXEQ runs.

### 18.3 FIXEQ: the coordinator's condition (every existing BENCH gate row unchanged)

- **Runner:** `results/LABS32-2026-09-24-C3/FIXEQ/fixeq.sh`. **Scorer:** `tests/harness/lab-fixture-eq.py`.
- **Engine held constant:** `build/land/ags.exe` (`d37c10b9f891`). Only the package differs.
- **Alias rows** (gate-alias.sh's bench rows, arm A, 11 rows):
  - 7 arms at the native rung;
  - idle/anim12 at 8-bpp 512x384;
  - idle/anim12 at 16-bpp 512x384.
  - OLD vs NEW must agree on:
    - every freeze capture, pixel for pixel at the same tick (min pairs as the gate: 3, `full` 2);
    - PH01.BMP byte for byte;
    - AUTOPLT.LOG line for line (game state, not only pixels).
- **Present rows** (gate-present.sh's 35 rows):
  - NEW's PH01 sha256 equals `expected/bench<d>/dosbox-x.json`;
  - its verifier line says `stale_frames=0`.
- **PASS iff all 46 rows pass and none is VOID.**
- **Any FAIL is not a C3 matter.** G3b does not count until it is resolved with the coordinator:
  a fixture fix, or an explicit re-baseline stated as a change.
- **Lock:** exclusive per run through the hub library (the gates' own default-conf mode),
  released between runs.

### 18.4 G3a: the standing gate on C3

`AGS_EXE=build/lab/C3/ags.exe gate-alias.sh --out results/LABS32-2026-09-24-C3/G3A`, the
Shards package staged locally as in 11.
- **PASS iff every row A == B except the quarantined rows** (`agsquest-alias-y60`'s one-tick
  divergence; `shards-alias-512x384` tick 100), and every control with power fails.
- **Limit, stated:** gate-alias's B (`DOSAGS_DIRTY_PRESENT=0`) only widens the **push**. C3
  changes the back buffer's **restore**, so a C3 trail would sit in both A and B, and G3a cannot
  see it. G3b/G3d exist for that.

### 18.5 G3b (BENCH `speech`) and G3d (AGS Quest at S2Q1's 32-bit settings)

**Runner:** `results/LABS32-2026-09-24-C3/g3.sh`. **Scorer:** `tests/harness/lab-g3.py`.
Exclusive lock per run. Default conf, `--fixed-timestep`.

- **Arms (all on the C3 binary):**
  - **A** = C3 on, default present;
  - **B** = **C3 OFF** (`DOSAGS_OVER_NOINVAL=0`) + full push (`DOSAGS_DIRTY_PRESENT=0`): the
    pre-C3 picture, so any pixel C3 changes, in the back buffer or the present, is A != B;
  - **C** = control `DOSAGS_BREAK_C3=1`.
- **Rows:**
  - G3b `bench8n` at the native 8-bpp rung, freezes at ticks 40, 80, ... 1000 (25), min 20 equal;
  - G3b `bench16n` at the 16-bpp 512x384 rung, the same freezes, min 20;
  - G3d `agsquest` with S2Q1's ACSETUP (sound off), `DOSAGS_FORCE_COLOR_DEPTH=32`,
    `SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1`; freezes at the gate's AQ ticks plus six inside the
    speech windows (100, 280, 320, 360, 420, 700, 980, 1020, 1100, 1180, 1300, 1600, 1900, 2200,
    2700, 3300: 16), min 12. A VOID pair (a different tick) is excluded and reported.
- **Per row:**
  - A == B: no pair differs, none missing, equal pairs >= min; for BENCH, PH01 A == B too;
  - **engaged:** A's `overskip` line says `mode=1`, `skipped > 0`.
- **PASS iff every row passes both, and the control differs from B in at least one BENCH row and
  in the AGS Quest row.**

### 18.6 G3c: H2-POS's reading on C3

- **Runner:** `results/LABS32-2026-09-24-C3/G3C/g3c.sh`: `h2pos.sh` with only the binary, output
  dir and lock tag changed (diff in the commit).
- **Scorer:** `tests/harness/lab-g3c.py`.
- **Valid if:** `lab0233dlog0`, `render_passes` 1501, exit 0.
- **HEAVY marked px/tick:** predicted **<= 20,000** (H2-POS: 38,299; QUIET 13,854).
  **Falsified above 30,000**; between the two, PARTIAL.
- **Reported, not in the verdict:** OVER_TEXTSPEECH marks in HEAVY, predicted <= 30 (H2-POS: 273).

### 18.7 Order, and the hardware cell this leads to

- **Order:** smoke (unscored) -> FIXEQ -> G3b/G3d -> G3a -> G3c.
- **If all pass:** `/sdldos:review` on 0233, then ask the coordinator about landing.
- **Hardware cell for the coordinator's batch, once they pass:**
  - **C3P:** S2Q1 fixture, sound off, the C3 binary, x2 (camera-judged VOIDs as C2P);
  - prediction 15.6 as amended in 18.0.
- The sound-on S32 prediction waits for the D2 decision (16.2).

## 19. PRE-REGISTRATION: D2 -- the SDL silence throttle: lab A/B, the fix (SDL 0213), and the hardware proof

Coordinator 2026-09-24:
- the lab A/B of the hint is GO now;
- the real fix is mine, in my SDL range (0213+), reviewed by the main worker through the
  coordinator;
- the hardware proof goes in the next round;
- C3 (18) waits behind this.
Everything below was committed before any D2 run.

### 19.0 Where the sleep comes from, and why "does the device have a thread" is not the test

- **Origin.** The `SDL_Delay(10)` is hub patch SDL/0050's quiescence throttle, moved from
  GetDeviceBuf into PlayDevice by 0054. It was written for doskutsu's background playback thread:
  "throttle ~100 iter/sec when quiescent".
  - [Corrected during `/sdldos:review`, 19.8: an earlier version of this line also named 0143.
    0143 is the audio-thread-existence diagnostic (NO_BG_THREAD) and carries no
    `SDL_Delay(10)`.]
- **dosags runs that background thread too.** `SDL_HINT_DOS_AUDIO_NO_BG_THREAD` is a diagnostic
  only (0143) and is unset. So dosags has two callers of PlayDevice:
  - the device thread, as in doskutsu;
  - the game loop, through `SDL_DOSAudioPump()` (SDL/0067), called from `audio_core_entry_poll()`.
    That poll runs once per tick, and again about every ms inside `WaitForNextFrame()` while the
    wait has room (timer.cpp ~150-175).
- **The test is therefore the caller's identity:**
  - sleep only when `SDL_GetCurrentThreadID() == SDL_GetThreadID(device->thread)`;
  - with no device thread, nothing sleeps.
  - Thread ids are real on DOS (`DOS_GetCurrentThreadID()` is >= 1).
  - `threadid` is set before `SDL_CreateThread` returns (it waits on `ready_sem`).
- **Behaviour on each path:**
  - the device thread keeps its throttle exactly, so a doskutsu-style port sees no change in its
    steady state;
  - the skip itself is unchanged on every path: the silent buffer is not written, so the SB still
    drains to its idle pause.
  - The background thread's own `SDL_Delay` yields (`DOS_Yield()` each loop,
    SDL_systimer.c ~66-90), so its sleep hands the CPU back to the game.

### 19.1 The fix and the binaries

- **SDL 0213**, vendor commit `3c486a7bd`:
  "silence throttle: sleep on the device thread only, never in the application's pump".
  Plus one OpenDevice banner line (`SDL/0213 silence throttle ...`).
  - Not in `patches/` yet. It goes there after this A/B passes, `/sdldos:review`, and the main
    worker's review through the coordinator.
- **The worktree:** lab/metric merged current main (`7fad051e`; ags 0214, 0252, 0253, 0297, SDL
  0220-0222 now in). `make patches`, verify exits 0.
- **N:** `build/d2/N/ags.exe`, the clean build of that tree.
  - `binary_sha12=b579ea800acd`, `build_dirty=0`;
  - sha256 `c8a95ef3a4eea57190201450a270209237a130a1a553fdaa417e6a728715a6be`.
- **F:** `build/d2/F/ags.exe`, the same tree plus 0213.
  - Linked against SDL built in its own sysroot (`build/sysroot-0213`), so `build/sysroot` stays
    true to `patches/`.
  - `lab0213nosl0`, `build_dirty=1`;
  - sha256 `9f71962553b6403a7c53c6fe8665d6514af56fc60eb0c8a4d87dc239119826c8`.
  - The banner string is in F and not in N.
- **H (the zero-code arm):** N + `SDL_HINT_DOS_SILENCE_DETECT=0`. That skips the whole
  silence-detect block, so silent buffers **are** written: no sleep, but no idle pause either.

### 19.2 The lab A/B

- **Runner:** `results/LABS32-2026-09-24-D2/d2.sh`. **Scorer:** `tests/harness/lab-d2.py`.
- **Conditions:** fixed 40000, core=normal, OPL3 conf, `--sb-live`, **no `--fixed-timestep`**,
  one EXCLUSIVE lock per cell (hub library).
- **S16 fixture (the lab copy of SB2C1/S16U1):**
  - `5days --startr 3`, `ACSETUP-ON-512X384-ROUND.CFG`, `SDL_DOS_ALLOW_DIRECT_FRAMEBUFFER=1`,
    exit 5000;
  - walked by `lab-drive-xdotool.sh walk 25 2 90`;
  - SFX (SB PCM) + OPL3 music.
  - It has both playing and silent stretches: S16U1 on the 486 recorded `pcm_irqs=991`,
    `skipped_silent=3293`.
- **S2Q fixture:**
  - AGS Quest forced to 32 bpp at S2Q1's rung (`5days/ACSETUP-ON.CFG`, `SDL_DOS_PACK24=1`), with
    `confs/dosbox-x-fixed40k-opl3-24bpp.conf` (the OPL3 conf plus the 24-bpp VBE line);
  - run to the AutoPilot's own quit (exit 4000 as a safety net). So it covers the silent stretch
    **and** the audio phase (ticks ~3144-3564: MIDI tune + chime), unlike S32S1.
- **Cells:** S16-N, S16-H, S16-F, S2Q-N, S2Q-F (order as listed).
- **Predictions** (per cell: call-weighted pump mean over the audioprb windows, the window
  maximum, the vital status, and `s8-facts.py`):
  - **V (validity):** each N cell reproduces the throttle: `skipped_silent > 0` and pump mean
    >= 3,000 us. **If not, the lab cannot see D2, and the A/B is VOID** (stated, not scored).
  - **P1 (the fix):** F's pump mean **<= 1,200 us** (from ~11,000 on silent stretches; ~600 when
    content plays, S8L1). **No 200-call window mean above 1,500 us.** `skipped_silent > 0`: the
    skip is kept.
  - **P2 (the hint):** H's pump mean <= 1,200 us, `skipped_silent == 0`.
  - **P3 (no regression):**
    - every cell: `overwrites == 0`, `|pcm_unaccounted| <= 1` (ags 0252; NA is reported);
    - F against N on the same fixture: `underruns` and `underflow_pads` each <= N's + 2;
    - S16-F: MIDI `late_writes == 0`.
  - **P4 (ranking only; fixed 40000 is not the 486):** stable (steady x (1 - skipped/ticks)),
    F >= N on each fixture.
  - **PASS iff** both fixtures have an N and an F cell, V holds, and P1-P4 hold.
- **Reported, not scored:**
  - H against F (H keeps the SB's IRQs running through silence; F lets it idle-pause);
  - `idle_pauses`; `silent_irqs`; `fps_p50`.

### 19.3 The hardware proof (next round; runs only after 19.2 passes and 0213 is reviewed into `patches/`)

The binary for both cells is the clean main build that includes 0213 (named when built). The
baseline is its own parent without 0213 (built the same way).

- **HW-D2a -- S16 sound-on, fix vs no fix.** SB2C1's recipe exactly (as S16U1: drive-walk, PGSB,
  OPL3), ABBA: **D2N1, D2F1, D2F2, D2N2**.
  - Basis: S16U1 on `4339326550df`: `tick_rate` 39.05, `frames_skipped` 59 of 4999, pump mean
    11.0 ms, `skipped_silent` 3293.
  - **Predicted, each F cell:**
    - pump mean <= 1.5 ms;
    - `skipped_silent > 0`;
    - `frames_skipped` <= 30;
    - **`tick_rate` >= 39.20** (the S16 floor), range 39.20-39.70.
  - **N cells should repeat S16U1** (`tick_rate` 38.9-39.2, pump mean >= 8 ms).
  - Both: `overwrites=0`, `late_writes=0`, `pcm_unaccounted` within +-1, `underflow_pads=0`.
  - **Falsified if** either F cell's `tick_rate` is below the mean of the N cells, or either F
    cell skips more than 59.
- **HW-D2b -- S32 with audio actually playing.** S2Q1's recipe (as S32S1: PGSB, OPL3,
  `SDL_DOS_PACK24=1`, forced 32) with **no 1500-tick exit** (safety net 4000), so the AutoPilot
  runs through its audio phase. F binary; tag **S32F1**, one run.
  - **Predicted:**
    - pump mean <= 1.5 ms (S32S1: 11.0);
    - whole-run stable **37.0 (range 36.0-37.8)**, against C2P B's 37.52 sound-off and
      S32S1's 27.27. That is sound-off less the playing cost (~0.6 ms/pump while content plays,
      S8L1) over the ~420 audio-phase ticks.
    - Audio counters: `pcm_irqs > 0` (the chime plays), MIDI `events > 0` with
      `late_writes=0`, `overwrites=0`, `pcm_unaccounted` within +-1, `silent_irqs=0` outside
      room loads.
  - **Falsified if** stable is below 35.0, or pump mean above 3 ms.
  - This cell is the first sound-on S32 figure that actually plays sound. It does not claim the
    S32 bar: that needs C3 as well (18).
- **Hardware cells for the coordinator's batch:** D2N1, D2F1, D2F2, D2N2, S32F1. The same VOID
  rules as S32S1 (10), plus the binary identities above.

### 19.4 D2 LAB A/B RESULT: **VOID as registered** (my validity rule was wrong); descriptively, the fix does what it should

**Raw:** `results/LABS32-2026-09-24-D2/` (S16-N, S16-H, S16-F, S2Q-N, S2Q-F; `INDEX.TXT`; scorer output
`SCORE.TXT`). Binaries as 19.1. The staged `ags.exe` of each F cell carries the 0213 string and
each N stage's does not. The 0213 banner itself is not in STDOUT: `dos_port_dbg_log` is off by
default, and the banner was informative, not scored.

| cell | calls | pump mean us | window max us | skipped_silent | pcm_irqs | mixed | pcm_unacc | underruns / pads / ovw | stable | fps_p50 |
|---|---|---|---|---|---|---|---|---|---|---|
| S16-N | 27,886 | 1,630 | 10,080 | 3,490 | 1,090 | 1,090 | 0 | 0 / 0 / 0 | 39.73 | 40.00 |
| S16-H | 86,260 | 73 | 88 | 0 | 2,721 | 984 | **-1,753** | 0 / 0 / 0 | 39.74 | 40.00 |
| S16-F | 73,245 | 358 | 414 | 44,310 | 1,208 | 1,208 | 0 | 0 / 0 / 0 | 39.74 | 40.00 |
| S2Q-N | 4,023 | 9,371 | 10,125 | 3,607 | 251 | 251 | 0 | 0 / 0 / 0 | 36.78 | 39.56 |
| S2Q-F | 34,284 | 350 | 351 | 32,951 | 251 | 251 | 0 | 0 / 0 / 0 | **37.83** | 40.00 |

**Registered verdict: VOID.**
- V failed for S16-N: pump mean 1,630 us against the >= 3,000 us rule.
- **This is my error in the rule, not an absence of the throttle.** V took a mean over every
  pump call. In the S16 cell most calls are the ~1 ms polls that `WaitForNextFrame()` makes while
  it has slack: 27,886 calls for 5,000 ticks.
- I found that polling while writing 0213 (its comment says so), after V was committed, and did
  not go back and correct V.
- The throttle is there: 3,490 silent calls, a window mean of 10,080 us, i.e. about 35 s of the
  run asleep in the pump.
- The rule was one silent-call cost diluted by idle-time polls.

**Descriptive reading (not a verdict):**
- **S2Q, the 32-bit fixture through its audio phase.**
  - N reproduces the throttle, and there it is the cost: pump mean 9,371 us.
  - F: pump mean 350 us, with no window above 351. The skip is kept (32,951 skips) and
    accounting is exact.
  - Stable 36.78 -> **37.83** (+1.05) and `fps_p50` 39.56 -> 40.00 at fixed 40000, where
    `wait_next_frame` falls 15.27 -> 13.77 ms/tick.
  - It passes P1, P3 and P4 as written.
- **S16 at fixed 40000 has so much slack that the throttle lands entirely in idle time.**
  - `update_game_once`, `wait_next_frame` and `render_to_screen` per tick are identical to 0.04
    ms across N, H and F, and none skips a frame.
  - The lab S16 cell **cannot rank D2 by rate**. The 486's S16U1 (idle 14.0 ms/tick, 59 skips)
    is the place for that: HW-D2a.
  - F's pump is 358 us mean and 414 us window max, the skip is kept, accounting is exact, and
    MIDI late is 0.
- **H (the zero-code hint) is not a fix candidate.**
  - It writes every silent buffer, so the SB never idles: `pcm_irqs` 2,721 against 1,090-1,208.
  - It breaks 0252's accounting identity: `mixed` 984 against `pcm_irqs` 2,721, `inflight` 16,
    so `pcm_unaccounted` -1,753. The silence chunks it writes play as IRQs but were never mixed
    by the engine.
  - P3 fails for H as registered.

**What would make it a scored pass (for the coordinator; nothing re-run):**
- Re-run the five cells under a corrected V, pre-registered before the run: in each N cell,
  `skipped_silent >= 1000` **and** a pump window mean >= 8,000 us (the silent-call cost itself,
  not diluted by idle polls).
- P1-P4 unchanged, except H's accounting line, which should be recorded as H's known identity
  break rather than scored.
- Or take S2Q's pair as the evidence, and let HW-D2a / S32F1 settle it on the 486.

### 19.5 AMENDMENT (coordinator 2026-09-24; committed before the re-run it scores): V2, and an S2Q-only re-run

- **The 19.4 cells stay VOID as registered.** Nothing below re-scores them. The amended scorer
  was run on them once, as a code check of the new rule only; that output is not a verdict and is
  not recorded as one.
- **V2 replaces V.** The throttle is present iff `skipped_silent > 0` AND either:
  - the mean pump time over **silent** calls is >= 8,000 us; or
  - the silent calls' summed pump time is >= 10% of the run's `loop_ms`.
- **How V2 is computed.** audioprb does not split calls by silence, so both quantities are
  **lower bounds**:
  - silent time >= total pump time - (non-silent calls x 2,000 us);
  - total pump time = call-weighted window mean x `total_calls`;
  - 2,000 us caps a non-silent call (S8L1 playing mean 630 us; no F window in 19.4 above 414 us).
- **The re-run is the S2Q pair only**, `S2Q-N` then `S2Q-F`, exactly as 19.2 (same binaries,
  conf and recipe). Output goes to `results/LABS32-2026-09-24-D2R/` (`D2_OUT` override in
  `d2.sh`, a path change only). Scored by `lab-d2.py --fixtures S2Q`.
  - P1, P3 and P4 are unchanged.
  - **PASS iff V2 holds for S2Q-N, and P1, P3 and P4 hold for S2Q-F.**
- **S16 is not re-run.** At fixed 40000 its throttle lands entirely in idle time, and N/H/F are
  identical per tick (19.4). The lab cannot rank D2 there; HW-D2a does that on the 486.
- **If it passes:** 0213 is formatted into `patches/SDL/0213-*.patch` on lab/metric,
  `/sdldos:review` runs, and the coordinator routes it to the main worker. The hardware cells of
  19.3 go in round E.

### 19.6 Crossed messages: the re-run is scored under both validity rules (committed before it runs)

- **Two rules arrived.** The coordinator's amendment (V2, 19.5) and, in a crossed message, the
  rule I proposed in 19.4, which the coordinator endorsed (**V1c**: `skipped_silent >= 1000`
  AND some audioprb window mean >= 8,000 us).
- The S2Q re-run had not started when this was written. **It is scored under both, and both
  must hold for S2Q-N.** Anything else is VOID. This is the stricter reading, so neither rule
  can be picked after seeing data.
- P1, P3 and P4 are unchanged. H stands as recorded in 19.4 (not a fix candidate, known identity break).

### 19.7 D2 S2Q RE-RUN RESULT: **PASS** (V2 and V1c hold; P1, P3, P4 hold)

- **Raw:** `results/LABS32-2026-09-24-D2R/` (S2Q-N, S2Q-F; `INDEX.TXT`; `SCORE.TXT`).
- **Identity:**
  - binaries as 19.1;
  - the 0213 string is in F's staged `ags.exe`, not in N's;
  - both ran the AutoPilot through its audio phase (ticks 3144-3564) to its own quit.

| cell | calls | pump mean us | window max us | skipped_silent | pcm_irqs = mixed | unacc | underruns / pads / ovw | stable | fps_p50 |
|---|---|---|---|---|---|---|---|---|---|
| S2Q-N | 4,023 | 9,380 | 10,124 | 3,608 | 251 | 0 | 0 / 0 / 0 | 36.77 | 39.60 |
| S2Q-F | 34,275 | **350** | **351** | 32,943 | 251 | 0 | 0 / 0 / 0 | **37.83** | 40.00 |

- **V2:** silent-call mean >= 10,229 us; silent sum >= 36.9 s = 18.1% of `loop_ms` 204,132. Holds.
- **V1c:** 3,608 >= 1000 silent calls; window max 10,124 >= 8,000. Holds.
- **P1:** F's pump mean 350 <= 1,200, window max 351 <= 1,500, skip kept (32,943). Holds.
- **P3:** overwrites 0; unaccounted 0; F's underruns/pads 0 <= N's + 2. Holds.
- **P4:** stable 37.83 >= 36.77 (ranking only, fixed 40000). Holds.
- **Reproducibility:** the pair repeats 19.4's descriptive S2Q figures to within 9 us of pump mean
  and 0.01 of stable.
- **Next (19.5):** 0213 into `patches/SDL/`, `make patches`, verify, a clean build,
  `/sdldos:review`, then to the coordinator for the main worker's review.

### 19.8 SDL 0213 in `patches/` on lab/metric: `/sdldos:review` and the clean build's DOSBox-X confirmation

- **Patch:** `patches/SDL/0213-dos-patch-0213-silence-throttle-sleep-on-the-device-.patch`,
  formatted with `git format-patch --start-number 213`.
- **Series:** `make patches` applies it (0210, 0213, 0220-0222); `verify-patches-applied` exits 0.
- **Clean build:** `build/ags/ags.exe`, **`binary_sha12=8c17fa080524`, `build_dirty=0`**, sha256
  `c54998ce97f9d7a889d5afc996fcd101a020705a17394d462d3c620c4b469982` (copied to `build/d2/L/`).
- **`/sdldos:review`:**
  1. **Provenance:** real format-patch output. Its diff equals the applied vendor commit.
  2. **Slot:** 0213 is the next free in my SDL range. 0211 and 0212 stay reserved for the
     lab-only records and are never landed.
  3. **DJGPP:** no `fopen`; the added lines are ASCII-only; no SIMD; no `size_t` assumption.
  4. **Naming:** not applicable (port-owned series); no new hint.
  5. **Cited history, read against the code:** this **found an error.** The commit message said
     the throttle was "carried by 0054 and 0143". 0143 is the NO_BG_THREAD diagnostic, and its
     patch has no `SDL_Delay(10)`. Corrected to "0050's, moved from GetDeviceBuf into PlayDevice
     by 0054", commit message only.
     - The corrected build is **byte-identical** to the first (`cmp`: 0 bytes differ, same stamp).
     - The same wrong citation in 19.0 is corrected in place, with a note.
  6. **Diagnostic:** only a permanent OpenDevice banner line (via `dos_port_dbg_log`, off by
     default). Not temporary, so it needs no removal plan.
  7. **Build and smoke:** the clean build is confirmed under DOSBox-X by S2Q-L below.
- **Confirmation (informative, not a scored cell):** S2Q-L, 19.2's S2Q recipe on the clean build,
  in `results/LABS32-2026-09-24-D2R/S2Q-L/`.
  - Pump mean 350 us, window max 351, `skipped_silent` 32,936;
  - `pcm_irqs` = mixed = 251, unaccounted 0, overwrites / underruns / pads 0;
  - stable 37.86, `fps_p50` 40.00;
  - the AutoPilot ran through its audio phase, and `build_dirty=0`.
  - This matches S2Q-F (19.7).
- **Status:** on lab/metric only. It goes to the main worker's review through the coordinator,
  and is not on main.
- **Hardware binaries for round E (19.3):**
  - fix = this clean build `8c17fa080524` (or its equivalent on main once landed);
  - baseline = the same tree without 0213, `b579ea800acd` (`build/d2/N/`).

### 18.8 AMENDMENT to C3's pre-registration (before any G3 run): C3 rebuilt on the merged tree; G3c gets a same-binary control

The coordinator accepted section 18 (2026-09-24), and C3's runs come after D2's A/B (19). Since
18 was written, lab/metric merged main (`7fad051e`: ags 0214, 0252, 0253, 0297; SDL 0213 and
0220-0222). So every G3 binary is rebuilt on that tree. FIXEQ (18.3) is unchanged: it holds the
engine constant at `build/land/ags.exe` as registered, and its inputs (fixture, packages,
`expected/*.json`, `run-dosbox.sh`, `screen-equal.py`) are unchanged by the merge (`git diff`).

- **C3 v1:** `build/lab/C3v1/ags.exe`, `binary_sha12=lab0233c3v1`, `build_dirty=1`, sha256
  `29e613a3c958feba2eae66a46d97a025e35154738785bfc0c19f37b20c25d2af`.
  - 0233 (the 18.1 WIP patch, unchanged) applied cleanly onto the current ags series, as
    `3979cff4f` in the side worktree `build/ags-c3-src`.
  - Built in `build/lab-c3v1-build` against `build/sysroot` (lab/metric's SDL series, including
    0213).
  - `g3.sh` now points at it. G3b/G3d are otherwise as 18.5.
- **C3DLOG v1:** `build/lab/C3DLOGv1/ags.exe`, `lab0233dlog1`, `build_dirty=1`, sha256
  `236ae82c3b6cc24048946a5d7d88449e49f96c095447f98cebb4cd647cd8991c`.
  - 0232 (lab-only) on top of `3979cff4f`, with the same one-line conflict resolution as 18.1.
- **G3c, amended:** two runs on C3DLOG v1, **ON** (as built) and **OFF**
  (`DOSAGS_OVER_NOINVAL=0`). The tree moved since H2-POS, so the reference is now the
  same-binary OFF run, not a number from the old tree.
  - **Valid iff:**
    - both runs have `lab0233dlog1`, `render_passes` 1501, exit 0;
    - `overskip` says `mode=0` for OFF and `mode=1` for ON;
    - OFF reproduces H2-POS's heavy frames: HEAVY within +-25% of 38,299 (28,724-47,874).
    - Otherwise G3c is VOID.
  - **Verdict on ON unchanged:** predicted <= 20,000; falsified > 30,000; PARTIAL between.
  - `g3c.sh` and `lab-g3c.py` are rewritten for this, before any run.
- **G3a** runs the gate as main now has it (`gate-alias.sh` at `7fad051e`), with
  `AGS_EXE=build/lab/C3v1/ags.exe`.
  - Its AQ row now runs at fixed 40000 with no fixed timestep and a no-skip assert (main's own
    change; it needs ags 0214, which C3 v1 has). A skipped frame there is VOID, not FAIL.
  - Quarantine as main records it (AQ still counting toward 10 clean runs; `shards-alias-512x384`
    tick 100).
- **The hardware cell after all pass (C3P, 18.7)** takes a clean build of lab/metric's series
  plus 0233, named when built.

### 19.9 PRE-REGISTRATION: 0213 v2 (the main worker's review) -- evidence before approval

- **Review outcome (main worker, via the coordinator):** CHANGES, one item. The thread-identity
  test has a startup window:
  - `device->thread` is assigned only after `SDL_CreateThread` returns, and the cooperative
    scheduler runs the new thread first;
  - with SDL/0086's yield killswitched (`SDL_HINT_DOS_DOS_AUDIO_COOP_YIELD=0`) and silence at
    open, the audio thread would loop WaitDevice/PlayDevice with neither sleep nor yield;
  - main would then never run again.
  - Everything else checked out: the throttle is kept on the audio thread, the main loop never
    sleeps, 0192/0197 are untouched, and the thread ids are valid.
- **0213 v2** (`patches/SDL/0213-dos-patch-0213-silence-throttle-never-sleep-inside-t.patch`,
  lab/metric `21c79840`):
  - `SDL_DOSAudioPump()` brackets its Iterate with a counter;
  - PlayDevice sleeps only when the counter is zero. So every non-pump path, the device thread
    included, keeps the throttle exactly as before, and no startup window exists.
  - The series applies, verify exits 0, and the applied commit equals the formatted one.
  - **Clean build `build/d2/F2/ags.exe`: `binary_sha12=8b339ddf451e`, `build_dirty=0`**, sha256
    `5862de43b28ea2673b876041dc1a5fe59330471d959c17b6b43f2a09b0ebc118` (the v2 banner string is
    in it).
- **Evidence** (`results/LABS32-2026-09-24-D2V2/`, `d2.sh` with `D2_EXE_F=build/d2/F2/ags.exe`,
  19.2's S2Q recipe, EXCLUSIVE):
  1. **S2Q-F** on v2, scored by `lab-d2.py --fixtures S2Q` under **19.6's rules** (V2 + V1c on N;
     P1, P3, P4 on F).
     - N is 19.7's cell unchanged (linked in as `S2Q-N`); it stands.
     - **Expected: the same as 19.7's F** (pump ~350 us, stable ~37.8, accounting exact).
  2. **S2Q-Y**, the startup smoke: the v2 binary with `SDL_HINT_DOS_DOS_AUDIO_COOP_YIELD=0`.
     AGS Quest is silent from open until its audio phase at tick ~3144.
     - **PY:** it must not hang (manifest `exit_code=0`, AutoPilot reached `phase=quit`), and it
       must play once content arrives (`pcm_irqs > 0`).
     - A hang would be the run's timeout expiring with no manifest exit code. That is a FAIL.
- **PASS iff (1) passes 19.6's rules and (2) passes PY.** Then `/sdldos:review` again, and back to
  the coordinator.

### 18.9 AMENDMENT to 18.2 (before FIXEQ counts): the smoke moved the speech box onto row 2

- **Smoke v0** (`results/LABS32-2026-09-24-C3/smoke/v0/`, landing binary):
  - the scene runs to its own quit with `stale_frames=0`, and every element appears;
  - but a frame diff (t=40 box up against t=160 box down) puts the `SayAt(8, 104, ...)` box at
    game **y 84-104**. The 3-line box ends near the y given. It sat **above** spinner row 2
    (114-138) and overlapped the moving spinner by ~4 px.
  - So 18.2's "box over spinner row 2" was not true, and content under a static box was barely
    exercised.
- **Fix (fixture only):**
  - `SayAt` y 104 -> **136**;
  - spinner 11's to-and-fro path moves from baseline 126 to **138** (row 2 itself);
  - a comment in the scene records why.
- **Smoke v1** (`smoke/bench8n`, `smoke/bench16n`):
  - the same diff puts the box at game **y 116-136**, over row 2, with the spinners showing
    through;
  - both runs complete with `stale_frames=0`.
- **New packages** (replacing 18.2's):
  - `BENCH8.ags` sha256 `020e402257296cb0fdbd41f42a69b8d72be2f147d969d9aca9ce4d570644f0b9`;
  - `BENCH16.ags` sha256 `86a9f71796ba74781147bd12e1aaf442256dedc8a3f29cbd28421f34916a6ae8`.
- **FIXEQ** had started on the v0 packages. It was stopped at its first row, is kept in
  `FIXEQ-void-v0pkg/` with a README, and is not scored. FIXEQ now runs on these packages,
  otherwise exactly as 18.3.

### 19.10 0213 v2 EVIDENCE RESULT: **PASS**; `/sdldos:review` of v2 clean

**Raw:** `results/LABS32-2026-09-24-D2V2/` (S2Q-F, S2Q-Y; S2Q-N linked from 19.7; `INDEX.TXT`;
`SCORE.TXT`).

| cell | binary | pump mean us | window max | skipped_silent | pcm_irqs = mixed | unacc | underruns / pads / ovw | stable | fps_p50 |
|---|---|---|---|---|---|---|---|---|---|
| S2Q-N (19.7) | b579ea800acd | 9,380 | 10,124 | 3,608 | 251 | 0 | 0 / 0 / 0 | 36.77 | 39.60 |
| S2Q-F | 8b339ddf451e (v2) | **338** | 339 | 33,101 | 251 | 0 | 0 / 0 / 0 | **37.86** | 40.00 |
| S2Q-Y (COOP_YIELD=0) | 8b339ddf451e (v2) | 338 | 339 | 33,190 | 251 | 0 | 0 / 0 / 0 | 37.80 | 39.96 |

- **Under 19.6's rules:** V2 and V1c hold on N (unchanged). P1, P3 and P4 hold on F.
- **PY:** S2Q-Y did not hang (`exit_code=0`, AutoPilot reached `phase=quit`) and played once
  content arrived (`pcm_irqs` 251).
- **VERDICT PASS.** v2 matches v1's F (19.7) within 12 us of pump and 0.03 of stable.
- **`/sdldos:review` of v2:**
  - **provenance:** the applied commit equals the formatted one;
  - **slot:** 0213 is kept, not renumbered;
  - **DJGPP:** no `fopen`, the added lines are ASCII-only, no trailing whitespace, no SIMD;
  - **naming:** n/a;
  - **cited history, read in code:** SDL/0086's WaitDevice yield and its
    `SDL_HINT_DOS_DOS_AUDIO_COOP_YIELD` killswitch; SDL/0067's pump taking `device->lock` before
    Iterate;
  - **the counter** is incremented and decremented directly around Iterate, under that lock,
    with no return between;
  - **diagnostic:** a permanent banner only;
  - **built and smoked:** above.
  - **Clean.**
- **Status:** on lab/metric (`21c79840`), for the main worker's approval. Not on main.

### 18.10 Harness merge at the cell boundary (coordinator 2026-09-24; before FIXEQ counts)

- Main now carries hub `b79e724`'s display and lock rules in `run-dosbox.sh`: display flock,
  its own Xvfb with the lock fds closed, `DOSBOX_DISPLAY_HELD`, and shared at fixed cycles only
  with `--no-host-input`. `gate-alias.sh` passes `--no-host-input`. Main also carries ags 0305.
- **Merged into lab/metric** (`e71d71a9`) between cells: after the D2 v2 cells and before
  FIXEQ's second row.
  - FIXEQ's one completed row (`bench8-alias-idle/old`, old harness) is voided to
    `FIXEQ-void-preharness/`, so the whole series runs on one harness.
- `make patches` again (ags now ends at 0305); verify exits 0.
- **My runners comply:**
  - none starts its own Xvfb or keep-alive (`run-dosbox.sh` owns the display);
  - every xdotool run (`d2.sh` S16) is EXCLUSIVE;
  - FIXEQ, G3 and G3c take the lock EXCLUSIVE per run.
- **The registered G3 binaries (18.8) stay as built.** C3 v1 and C3DLOG v1 predate ags 0305
  (SetButtonPic, a GUI-button change outside the overlay path) and linked SDL 0213 v1. The G3
  cells run with sound off, so 0213's form is not exercised there.
- The C3P hardware build (18.7) will be taken from the then-current series.

### 19.11 LANDING RECORD: SDL 0213 v2 on dosags main (2026-09-24)

- **Approval:** the main worker APPROVES 0213 v2 (lab/metric `21c79840`), relayed by the
  coordinator about 20:28Z.
- **Landing set:** main's applied series gains exactly
  `patches/SDL/0213-dos-patch-0213-silence-throttle-never-sleep-inside-t.patch`, plus this record
  (`LAB-S32.md`). Nothing else from lab/metric lands: the C3 fixture, scorers and runners stay
  on the branch.
- **Base:** origin/main `882f9029`. Since the build and gate below, main gained only
  `tests/harness/lab-cell.sh`, which is outside the series, the build and the gate harness.
- **verify:** `make verify-patches-applied` exits 0 on main's series + 0213.
- **Clean build:** `binary_sha12=b983bf9d146a`, `build_dirty=0`, sha256
  `02c9eaeb690204e8b9dc856e2f4eff794db371bfec93456ee32c0cc934a72678`.
  - The stamp is a content fingerprint of the vendor trees and flags, so it is the landing
    binary whatever commit carries the patch.
- **Gate:** `results/GATE-land-0213-2026-09-24/` on lab/metric, main's current `gate-alias.sh`
  (b79e724 harness), `AGS_EXE` = that binary (`binary_sha12=b983bf9d146a build_dirty=0` in the
  runs' manifests).
  - **14/14 rows A == B, 14/14 controls fail as required**;
  - `agsquest-alias-y60` 10/10 pairs, `frames_skipped` 0/0;
  - `shards-alias-512x384` 5/5.
- **Next:** round F's D2 variant starts from this binary (19.3's cells with fix = `b983bf9d146a`).
