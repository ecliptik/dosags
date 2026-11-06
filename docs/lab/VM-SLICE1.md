# VM slice 1 -- the decoder only (2026-11-05): RESULTS

Worktree `~/git/dosags-lab-vm` (detached at 785bcb1c), vendor trees copied from `~/git/dosags/vendor`
and re-applied with `make patches` (fingerprints recorded, `verify-patches-applied` passes; ags tree
49328a75 and SDL tree 580997cd equal main's). Patch: `~/git/dosags-lab-vm/vm-slice1.diff` (applies
cleanly to the clean ags tree). DOSBox-X only, fixed 40000 (`tests/harness/confs/dosbox-x-fixed40k-opl3.conf`),
`--fixed-timestep`, headless, shared lock; `DOSBOX_DISPLAY_NUM` 263/264. No hardware, no commits.

## The patch (inert by default)

- `Engine/script/cc_instance_vm.cpp` (new): `DosVmMode()`, `DosVmDecode()`, `DosVmCheck()`.
- `cc_instance.h`: `ResolvedScriptData` gains `dcode`, `dstart`, `decoded_ok` (DJGPP only).
- `cc_instance.cpp`: 4 lines at the end of `ResolveImportFixups()` (`if (DosVmMode() > 0) DosVmDecode();`)
  and two one-line opcode-table accessors at the END of the file. `Run()` untouched.
- `Engine/CMakeLists.txt`: the new source. `quit.cpp`: `DOSAGS_VM` in the RUNMANIFEST env allowlist.
- `DOSAGS_VM` unset or `legacy`: one cached `getenv()`, no allocation, no decode. `decode`: decode + log.
  `check`: decode + an independent re-derivation of every instruction (walk over the ORIGINAL
  `ccScript::code`, registers by pointer arithmetic, jumps against its own start set, LITTOREG/WRITELIT
  values by building the legacy `FixupArgument` result and the decoded one and comparing all 5 fields).
- `Run()` machine code: identical. `-S` of `cc_instance.cpp`, clean vs patched, `ccInstance::Run` with
  labels normalised: 4,150 lines each, no difference. (The object-level diff is the switch jump table's
  address only.)

## Binaries

| | sha256 (12) | binary_sha12 | bytes |
|---|---|---|---|
| AGSBASE (clean instrumented, worktree build) | d72fe181d8fa | 7e5dfe26f272 | 8,636,055 -- byte-identical to `~/git/dosags/build/ags/ags.exe` |
| AGSVM1 (+ slice 1, build_dirty=1) | a13daf199d45 | a753601ebc42 | 8,643,777 (+7,722) |

## Decode check (DOSAGS_VM=check): 0 mismatches, 0 ineligible

| fixture | scripts decoded (incl. re-decodes on room loads) | instructions checked | mismatches | ineligible |
|---|---|---|---|---|
| MMD character select (room 50, 1000 ticks) | global (130,393 words, 54,343 instr) + room 50 (1,953 / 821) | 55,164 | **0** | 0 |
| AGS Quest AutoPilot (to quit, 4 rooms, its own save/restore) | 16 (AutoPilot, Global, Dialog, rooms 1-4, all re-decoded after its restore) | 32,566 | **0** | 0 |
| 5 Days, room 3 (seeded, 2000 ticks) | global (26,331 / 10,486) + room 3 (1,900 / 781) | 11,267 | **0** | 0 |

Every category 0 (start bits, opcode/kind, register, jump, fixed-up value, raw operand, padding).
Shape of the code: no FIXUP_STACK (`movl_slow=0`), no jump to a non-start (`jump_slow=0`), no fixup on
any other argument (`otherfix=0`), no NULL ops. CALLAS sites: MMD 0, AGS Quest 13, 5 Days room 3: 5.
LITTOREG fixups, MMD global: int 6,000 / gvar 575 / string 1,139 / import 5,566.

## Memory (decode on)

4 bytes per code word + 1 bit: MMD global 537,884 B, room 50 8,072 B (MMD room 2, its largest, would be
~280 KB: live peak ~0.82 MB as estimated). 5 Days 108,628 + 7,852 B. AGS Quest 17-26 KB per script,
~97 KB live. The `tot_bytes` field is CUMULATIVE (it counts re-decodes), not live; decoded memory is
freed with the instance's `_scriptData`.
`memory_min_free_kb` (largest free DPMI block, virtual): MMD 166,256 -> 165,680 (-576 KB, matches the
decoded bytes); 5 Days -64 KB; **AGS Quest -1,536 KB** against ~97 KB live -- most likely fragmentation
from allocating and freeing a decoded stream on each of its 16 script loads (the metric is the largest
block, not total free; base vs decoder-off already differ by 384 KB). Not a leak proof either way;
worth a total-free reading before decode is ever on by default.

## Decode time and load time (fixed 40000; emulated ms, deterministic per binary)

Decode costs **~2.0 us per code word at fixed 40000 (~80 emulated cycles/word)** -- 2-3x my design
estimate. MMD global: 260.9 ms; AQ room 3 (6,319 words): 12.7 ms; 5 Days global: 52.0 ms.

| figure | AGSBASE | AGSVM1 off | AGSVM1 decode | AGSVM1 check |
|---|---|---|---|---|
| MMD `script_vm_init_ms` | 1,237 | 1,239 | **1,501** | 1,896 |
| MMD room 50 load bracket | 200 | 203 | 206 | 214 |
| MMD `total_to_first_frame_ms` | 5,577 | 5,583 | 5,863 | 6,255 |
| AQ load brackets r1/r2/r3/r4 (first) | 940/1089/1064/1001 | 942/1086/1067/999 | 944/1088/1078/1015 | 945/1094/1098/1026 |
| 5 Days `script_vm_init_ms` / room 3 bracket | 752 / 200 | 752 / 200 | 806 / 206 | 885 / 212 |
| AQ journeys p95 boot/room/save/load (ratchet-cell) | 7542/11728/895/10103 | 7541/11733/900/10107 | 7576/11741/894/10161 | -- |

**Room-load allowance (proposed for registration before decode is ever on by default):** +2.0 us per
word of the room script at fixed 40000, i.e. +13 ms on AGS Quest's largest room and ~+136 ms on MMD
room 2; game start +2.0 us/word of the global/module scripts (+261 ms MMD, +52 ms 5 Days). The AQ
journey limits keep their headroom with decode on (room p95 11,741 vs 12,295; load 10,161 vs 10,929;
boot 7,576 vs 7,901). On the 486 (not measured; 1.5-2.5x fixed cycles assumed for a streaming loop)
that is ~0.4-0.65 s added to MMD's start and ~0.2-0.35 s to its room-2 load -- material for PLAN-FPS
target (b). The decoder is not tuned: it calls two out-of-line opcode-table accessors per argument
(across TUs), makes two passes and zero-fills the vector first; copying the table into the VM TU and
fusing the passes should cut it 2-3x. Recommended before slice 2's timing cells.

## Decoder OFF: did anything move?

- **Behaviour: no.** Kept `Game :` lines identical in every arm (MMD 21, AQ 341, 5 Days 21); AGS Quest
  PH01-03.BMP identical in all 6 AQ runs; the script event per tick unchanged (MMD 9.258 base,
  9.256 off/decode/check -- nothing executes the stream yet).
- **Timing: by a deterministic, binary-level few ms.** Repeats are byte-for-byte reproducible per binary
  (B == B2, OFF == OFF2), yet base vs decoder-off differ: MMD first room load +6 ms, room bracket +3 ms;
  AQ brackets -3..+3 ms; AQ journeys p95 room +5, save +5, load +4, boot -1. `Run()` is identical, so
  this is the binary changing (size, data layout), not the decoder running.
- **AUTOPLT.LOG differs in one place**: the AutoPilot's audio-phase end / quit tick 3570 (base) vs
  3569 (every AGSVM1 arm, decoder off included). Deterministic per binary; the audio-phase timing field
  that LAB-MMD 34.1 already masks in the guard.
- `env_block_sha` unchanged with `DOSAGS_VM` unset (MMD 9036ef98e429 in both), distinct when set.

## Ratchet subset (worktree `tests/ratchet.yaml`, `AGS_EXE` absolute, `--no-build --no-record`)

Chosen: the `aq-journeys` run and all 10 of its checks (script-driven AutoPilot through 4 rooms,
save and load -- the part of the ratchet the script VM drives) plus `exe-bytes`. Not run: the
gate-alias screen captures (3 h, present path), the sb-live audio rows and the xdotool click rows --
none touch script loading. Controls not run (they prove the checks' power, not this change).

| exe | result |
|---|---|
| AGSBASE | **PASS 11/11** (4 improved) |
| AGSVM1, decoder off | **10 pass (4 improved), 1 FAIL: `exe-bytes`** -- 8,643,777 > limit 8,636,055 |

`exe-bytes` is a size ratchet whose limit equals today's exe exactly, so ANY added engine code fails it
(+7,722 bytes here). Raising it is a reviewed limit change, not something this slice can pass.

## Files

- `~/git/dosags-lab-vm/vm-slice1.diff` -- the patch (495 lines, ASCII)
- `~/git/dosags-lab-vm/build/vmlab/` -- `exe/AGSBASE.EXE`, `exe/AGSVM1.EXE`, `cell.sh`, `compare.py`,
  `results/{B,B2,OFF,OFF2,DEC,CHK}-{MMDCS,AQ,5D3}/` (STDOUT.TXT, RUNMANI.LOG, AUTOPLT.LOG, PH*.BMP),
  `ratchet/{AGSVM1,AGSBASE}/` + logs, `ratchet/DEC-journeys/`, `runcmp/run-{base,vm1}.s` (the Run()
  identity check), build logs.
