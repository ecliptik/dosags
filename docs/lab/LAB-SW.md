# LAB-SW -- the restart-point save write (AGSSAVE.999): where its time goes, and which exact levers remain

Copied into the main repo 2026-11-07 from the lab worktree ~/git/dosags-lab-sw (base main; lab only). Diffs, tools, TABLE.md,
GATES.md and the no-rate-limit conf in docs/lab/sw-lab-patches/. Exes and collected saves stay local (saves are game-derived data
and are never committed).

Lab worktree ~/git/dosags-lab-sw (detached at main 41d82c06, vendor/ags at the 0367 head, series fingerprint df1c98f6ab85).
Sections 0-7: measurement only. **Update 2026-11-07 (sections 8-9): lever 1 built in the lab (DOSAGS_SAVEMEM), gates G1-G5
all PASS in DOSBox-X, and the SW1 pre-registration final draft.** Still lab only: nothing committed from the worktree. Every AGSSAVE.999 collected stays local
(build/sw/saves/, gitignored); only sha256 and size are recorded here.

## 0. Setup and instrument

- Worktree: `git -C ~/git/dosags worktree add --detach ~/git/dosags-lab-sw main`; tools/djgpp via
  scripts/setup-symlinks.sh; vendor/ags and vendor/SDL cloned from ~/git/dosags/vendor; `make patches` (series applied
  cleanly, fingerprint df1c98f6ab85); vendor/cwsdpmi copied; tests/harness/games/{5days,trilbysnotes,mmd} symlinked
  read-only to main's packages.
- Lab diff: build/sw/lab-sw.diff (407 lines, sha256 410d510e..., ASCII), over the 0367 head. DOSAGS_SW unset = off
  (one test per hook):
  - **=1**: counters and a call trace for the slot-999 SaveGame() only (dos_sw_active is 1 only inside it).
    - every BufferedStream::Write (size histogram, logical runs);
    - every BufferedStream flush;
    - FileStream open / fwrite / fseek / fclose, with uclock time;
    - **every INT 21h** issued while active, through `-Wl,--wrap=__dpmi_int` (all DJGPP libc DOS calls go through
      __dpmi_int). Per call: AH/AL, BX/CX/DX in, carry, DX:AX out, uclock start and duration. Checked: 191 call sites
      route to __wrap___dpmi_int; the only direct call left is the wrapper's own __real.
    - Dump to SWTRACE.TXT after restart_savegame_ms is stamped, plus one `DOS-PORT swlab` line.
  - **=2**: also, after the real write, a dry SaveGame into a VectorStream (the same steps as StartSavegame() +
    SaveGame(), minus File::CreateFile), timed, then compared byte for byte with the file just written.
- Exe: **build/sw/exe/swlab1.exe, sha256 35f676ac8d47c08a78df7f327ffbf3ba1c177af65701b07a1828df8fa7e22fd8** (instrumented
  flavour, `make game`). The un-patched build of the same tree (before the lab diff) was 5650fff9...; not used for cells.
- Cells: build/sw/swcell.sh through tests/harness/lab-cell.sh, `--sb-live`, DOSBOX_DISPLAY_RANGE=392-393, at most two at
  once (build/sw/drive1.sh, drive2.sh). Conf tests/harness/confs/dosbox-x-fixed40k-opl3.conf; the "cpu" cells use
  build/sw/dosbox-x-fixed40k-opl3-norate.conf = the same plus `hard drive data rate limit = 0` (section 3 says why).
  DOSAGS_TAS_AUTO_EXIT_TICK=400, DOSAGS_RANDSEED=1 (all but the first two cells). Lines:
  - **S32P**: 5days --startr 3, roundSU's S32P-ACSETUP-ON.CFG, DOSAGS_FORCE_COLOR_DEPTH=32, DOSAGS_MAX_SCALE=1,
    SDL_DOS_PACK24=1 (SU's S32 line);
  - **S16**: 5days --startr 3, ACSETUP-ON-512X384-ROUND.CFG (CF's S16 line);
  - **S8**: trilbysnotes --startr 35, ACSETUP-ON-512X384-ROUND.CFG, DOSAGS_MSGSKIP=1 (SU's S8 line);
  - **MMD**: the title, ACSETUP-OFF-512X384-ROUND.CFG (SU's warm-up line).
  - The prior AGSSAVE.999 was staged with `--include-extra <save>:AGSSAVE.999` (rig state: the file always exists).
    "-new" cells have no prior file; "-shrink" stages MMD's 146,822 B save under 5days; "-grow" stages 5days' 59,538 B
    under Trilby.
- Sizes reproduce the rig exactly: **5days 59,538 B, Trilby 61,199 B, MMD 146,822 B**.
- RUN.BAT SET lines: 322 bytes at most. Every staging dir was deleted after its cell was recorded.
- Results: build/sw/results/<cell>/{SWTRACE.TXT, STDOUT.TXT, RUNMANI.LOG, RUN.BAT, SAVE-SHA256.txt, PRIOR-SHA256.txt};
  tools build/sw/tools/{swan.py (counts), swtab.py (table), eqcmp.py (LAB-R2's, game output lines)}.

## 1. The write path on DOS, layer by layer (read from vendor/ags at the 0367 head and the DJGPP 2.05 libc source)

DJGPP source: djlsr205.zip (the pinned toolchain reports DJGPP 2.05), read in the session scratchpad; the facts used
below were checked against the toolchain's own headers (BUFSIZ 16384 in sys-include/stdio.h, the FILE flags in
libc/file.h) and the exe's stub info (minkeep = transfer buffer = 16,384).

1. **Engine.** SetRestartPoint() -> SaveGameSlot(999):
   - GetDiskFreeSpaceMB (restart_diskcheck_ms, 0);
   - save_game(): no screenshot for this slot (restart_screenshot_ms, 0);
   - SaveGame() inside patch 0107's restart_savegame_ms bracket. **Patch 0108 turns compression OFF for slot 999.**
     No component is deflated; the user image is absent.
2. **Not serialised to memory first.** SaveGame() -> StartSavegame() -> File::CreateFile ->
   File::OpenFile(kFile_CreateAlways, kStream_Write):
   - a FileStream with C mode **"wb"** (File::GetCMode), wrapped in a **BufferedStream (BufferSize 8 KB, static for
     every stream)**, wrapped in a Stream;
   - the serialisers write into that stream directly.
3. **Seek-back patching, inside SaveGame():**
   - WriteDescription writes a 20 B FileFormat placeholder at offset 39 and the env-info size placeholder, patched at
     once (always inside the buffer).
   - **WriteComponent, per component:**
     - writes the tag and six int32 placeholders;
     - Serialize();
     - Seek(header_pos) and write 4 B; Seek(data_sz_pos) and write 12 B; Seek(data_end);
     - that is three seeks per component.
   - The end: WriteFileFormat seeks back to offset 39 and writes 20 B.
   - When the component still fits in the 8 KB buffer, those seeks land inside it and cost nothing. When it does not,
     BufferedStream::Write flushes (FlushBuffer -> FileStream::Write) and the next flush reseeks the base
     (FileStream::Seek = fseek + ftell).
4. **BufferedStream.** Open() calls base Seek(0,END) and Seek(0,BEGIN). The buffer is flushed when a write position:
   - lies before the buffer;
   - lies past the buffer's end;
   - or has reached 8 KB.
   - No explicit Flush() is ever called on this stream: 0 'F' records in every trace. It is flushed once more at close.
5. **DJGPP stdio, fopen("wb"):**
   - open(O_WRONLY|O_CREAT|O_TRUNC|O_BINARY);
   - __solve_symlinks: findfirst, which is 1Ah + 4Eh;
   - _open, INT 21h **3Dh**;
     - if the file is absent: 43h + **3Ch** creat;
   - then, because O_TRUNC is set on an opened file, **`_write(fd, 0, 0)` = INT 21h 40h with CX=0, which truncates the
     existing file to 0 at open**;
   - setmode / fd properties: 44h00h, 60h truename.
6. **FILE buffer.** There is no setvbuf anywhere in Engine/Common: the only two setvbuf calls are in
   platform/windows/acplwin.cpp, for stdout/stderr.
   - The first _flsbuf mallocs **__tb_size = 16,384 B** (the stub's transfer buffer; the header's BUFSIZ is also
     16384).
   - fwrite memcpy's into it and flushes full 16 KB buffers.
7. **_write -> _write_int:** dosmemput into the 16 KB DOS transfer buffer, then **one INT 21h 40h per <= 16 KB chunk**.
8. **fseek on a write FILE** = fflush (a 40h for pending bytes) + lseek (42h). **ftell** = lseek(fd, 0, SEEK_CUR)
   (42h01h).
9. **The zero-fill-gap check.** llseek with offset > 0 sets FILE_DESC_ZERO_FILL_EOF_GAP, so the next _write first runs
   _write_fill_seek_gap:
   - _get_dev_info (44h00h);
   - lfilelength: no LFN on 6.22, so 42h01h, 42h02h, 42h00h;
   - llseek(cur) (42h01h).
   - That is **five extra DOS calls before every write that follows a seek.**
10. **No fflush by the engine, no fsync, no _commit (68h), no 0Dh disk reset** anywhere in this path. fclose = fflush +
    INT 21h **3Eh**.
11. **DOS (MS-DOS 4.0 source, microsoft/MS-DOS on GitHub; 6.22 is assumed to share this FAT logic and was not read):**
    - The 40h CX=0 at offset 0 frees the file's whole cluster chain (RELEASE). RELEASE does **not** touch dpb_next_free.
    - Extending writes call ALLOCATE. ALLOCATE scans **first-fit upward from dpb_next_free** (the last cluster
      allocated), wraps to cluster 2 at the end of the disk, and leaves dpb_next_free at the last cluster it found.
    - A partial-sector write pre-reads the sector unless the sector lies beyond VALSEC, the old end of file (BUFWRT,
      "Skip preread if SECPOS>VALSEC").
    - The written buffer is marked dirty, not written.
    - **Close updates the directory entry and calls FLUSHBUF, which writes every dirty buffer: data tails, patched
      sectors, FAT sectors (both copies) and the directory sector.**

## 2. Counts, one restart-point save each (prior file present, as on the rig)

Cells S32-same2, S16-dry, S8-same, MM-same. S32P and S16 have identical counts and sizes but differ in content (sha
below).

| | 5days S32P / S16 | Trilby room 35 | MMD title |
|---|---|---|---|
| file size (B) | 59,538 | 61,199 | 146,822 |
| Stream-level writes (BufferedStream::Write calls) / bytes | 9,547 / 59,866 | 9,670 / 61,527 | 19,235 / 147,150 |
| ... of which 4 B (WriteInt32) | 7,870 | 8,070 | 12,673 |
| ... 1 B / 2 B | 337 / 458 | 345 / 419 | 1,016 / 4,155 |
| ... 7 B / 8 B / 10 B | 298 / 81 / 383 | 278 / 79 / 367 | 282 / 111 / 568 |
| ... 17-64 / 65-256 / 257-1K / 1K-4K / >= 8K | 23 / 4 / 10 / 1 / 1 | 26 / 7 / 11 / 1 / 1 | 36 / 4 / 104 / 1 / 1 |
| BufferedStream flushes = fwrite calls / bytes | 19 / 59,622 | 19 / 61,283 | 33 / 146,922 |
| fwrite sizes | 8192 x5, 4K-8K x3, 512-4K x1, 17-511 x2, 1-16 x8 | the same buckets | 8192 x16, 4K-8K x1, 512-4K x4, 17-511 x2, 1-16 x10 |
| FileStream seeks (fseek + ftell each) | 15 | 15 | 18 |
| **INT 21h total** | **117** | **117** | **146** |
| 40h write (incl. 1 CX=0 truncate) | 16 | 16 | 24 |
| ... data writes: extending | 6 (59,538 B) | 6 (61,199 B) | 12 (146,822 B) |
| ... data writes: in place (patches) | 9 (84 B) | 9 (84 B) | 11 (100 B) |
| 42h lseek (AL=0 / 1 / 2) | 82 (27 / 41 / 14) | 82 (27 / 41 / 14) | 100 (33 / 50 / 17) |
| 44h ioctl (dev info: 13 gap checks + 1 at open) | 14 | 14 | 17 |
| open-side 1Ah / 4Eh / 3Dh / 60h; close 3Eh | 1 / 1 / 1 / 1; 1 | the same | the same |
| clusters allocated (32 KB clusters, CHKDSK LOG-CF) | 2 | 2 | 5 |
| distinct file sectors patched in place | 4 (0, 45, 60, 81) | 4 (0, 45, 56, 85) | 5 (0, 31, 192, 218, 241) |
| extending writes that start mid-sector (DOS buffers a tail each time) | 5 | 5 | 11 |

- **The DOS-level calls (40h, the INT 21h total) are the same in every prior-file state**: new, same, shrink, grow.
  With no prior file, 3Dh fails and 1Ah/4Eh x3 + 43h + 3Ch are added: 123 INT 21h (5days, Trilby), 152 (MMD).
- **Extend versus overwrite.** The open truncates the old file to 0 in all four states.
  - Every byte of the save is written by an extending write.
  - The only in-place overwrites are the 9 (11 for MMD) header patches, 4-20 bytes each, into sectors written earlier
    in the same save.
  - DOS never overwrites the previous run's file in place. It frees that file's chain and allocates fresh clusters from
    dpb_next_free.

## 3. Time split under DOSBox-X (fixed 40k), CPU side

Two facts set how these must be read:
- **DOSBox-X's default `hard drive data rate limit` emulates disk time** on a mounted host directory. In the specified
  conf, a 42h or 40h on the save costs about 1 ms of *emulated* time: S32P INT 21h = 81 ms of a 168 ms bracket. That is
  neither a CF figure nor CPU work, so the CPU-side split below comes from the norate conf, where an INT 21h costs
  ~19.6 us (the DPMI round trip at 40k).
- **The instrument costs time itself.** On the norate conf: 5days 89.8 vs 71, Trilby 86.6 vs 68, MMD 160.4 vs 125 ms
  (SW=1 bracket vs the uninstrumented off arm). That scales with the BufferedStream::Write count (9.5k / 9.7k / 19.2k):
  ~1.9 us per call of the per-Write counter hook. Counts are unaffected; times are quoted
  from the un-instrumented arms where possible.

All ms at fixed 40k. Cells: *-offcpu (uninstrumented, norate), *-cpu (SW=1, norate), *-dry / *-drycpu (SW=2),
*-off (uninstrumented, default conf).

| | 5days S32P | Trilby r35 | MMD title |
|---|---|---|---|
| **restart_savegame_ms, uninstrumented, norate** (MMD/Trilby from the STDOUT line; 5days from the journey write_ms, which equals it where both exist) | **71** | **68** | **125** |
| the same on the default conf (DOSBox-X disk-rate emulation on) | 151 | 77 | 236 |
| SW=1 bracket, norate (instrumented) | 89.8 | 86.6 | 160.4 |
| ... INT 21h, all calls: n / ms (~19.6 us each = DPMI round trip) | 117 / 2.29 | 117 / 2.29 | 146 / 2.85 |
| ... fwrite (stdio memcpy + its 40h calls) | 0.90 | 0.92 | 2.63 |
| ... fseek + ftell (fflush 40h + 42h x6 per seek) | 3.29 | 3.31 | 3.91 |
| ... fopen / fclose | 0.25 / 0.22 | 0.25 / 0.22 | 0.25 / 0.22 |
| **= the whole stdio + DOS path, CPU side** | **4.7** | **4.7** | **7.0** |
| **serialisation into the BufferedStream** (uninstrumented total - path) | **~66** | **~63** | **~118** |
| **dry: serialisation into a VectorStream** (uninstrumented, timed in the SW=2 cells, identical in the rate-limited and norate cells) | **54.3** | **51.3** | **89.3** |
| INT 21h on the default conf (emulated disk time, not CPU) | 81 | 11 | 114 |

**Reading.**
- On the CPU side the save is **~93-94% serialisation and ~6% stdio/DOS** (4.7 of 71 ms).
- Of the serialisation, **~12-29 ms is the BufferedStream's per-call cost** over a VectorStream's (the same ~9.5k-19k
  Write calls).
- The stdio/DOS path is cheap on the CPU side because DOSBox-X answers DOS in its own code. On the 486 the same 117
  calls each cross CWSDPMI into real-mode DOS. Then DOS does real FAT and buffer work and the BIOS talks to the CF
  card. That cost can only be scaled from the counts in section 2.
- Default-conf INT 21h time is DOSBox-X's own disk-rate emulation. It moves between cells and games (81 vs 11 ms for
  the same 117 calls) and is not a 486 prediction.
- Repeatability: Trilby SW=1 brackets 95 ms in all five default-conf cells (new, new2, same, grow, dry) and 86.6 in
  the norate cell. 5days 166-172 default, 89.8 norate.

Full per-cell table: `python3 build/sw/tools/swtab.py build/sw/results` (section 7).

## 4. Why a shrinking rewrite could be faster -- what the code says, and what decides it on the 486

**From the code, a shrink is NOT a lighter write for the engine, libc or DOS.**
- The engine and libc issue the same INT 21h sequence (section 2), the same 117 calls, in every state: new, same,
  shrink (S32-shrink: MMD's 146,822 B file under it), grow (S8-grow).
- fopen "wb" truncates to 0 at open in every state. So the old size changes only:
  - how many FAT entries RELEASE walks: 5 against 2, trivial;
  - possibly how many FAT sectors the freed chain dirties: 1 or 2 per FAT copy, depending on where the old chain lay.
- Each candidate in turn:
  - **Truncation freeing clusters first.** It happens in every state, not only in a shrink. A shrink frees more
    clusters, which is more FAT work, not less.
  - **FAT allocation, first fit.** RELEASE leaves dpb_next_free alone and ALLOCATE scans upward from it. So the new
    clusters do not go back into the clusters just freed (unless the scan wraps). They go to the next free clusters
    past the last allocation in this boot: here the cell's own earlier redirect files (SVPRE, DIRLIST, SDRV) and
    whatever came before.
    - **Where the save lands is set by the previous writes, not by the old file's size.**
    - Two costs depend on where it lands:
      - the length of the scan: UNPACK reads FAT sectors through DOS buffers and SMARTDRV until it finds a free entry,
        with 256 entries per FAT sector. The disk is ~87% full (~7,900 of 61,478 clusters free);
      - **which physical CF sectors** the data, FAT and directory writes hit.
    - A shrink correlates with "landed elsewhere" only through the history (SU32A1 came after the MMD warm-up). It is
      not a mechanism.
  - **Read-modify-write.** The pre-read rule depends on the NEW file's VALSEC, which starts at 0 after the truncation.
    So it is identical in every state:
    - the 9 in-place patches pre-read their 4 distinct sectors unless those are still in a DOS buffer. They were
      written by direct multi-sector transfers, so normally they are not;
    - each extending write that starts mid-sector reuses the tail buffer the previous write left (5 of them per
      5days/Trilby save);
    - nothing here differs between a shrink and a same-size rewrite.
  - **SMARTDRV's read cache.** It can only serve those pre-reads (and FAT-scan reads), and only if it holds the sectors.
    Whether SMARTDRV 5.0 keeps written sectors in its cache in write-through mode was not read here. It does not depend
    on the old size either.
- **So the code does not explain the 210 ms cell, and the n = 1 shrink correlation should not be leaned on.** D8S8 wrote
  in 228 ms after a GROWING write, and on other days v0.1 has ranged 213-529 ms with no size change.
- **What the record does contain is a known CF mechanism of this shape on this card:** dosags PLAN-LOG 2026-09-19..21,
  int13-probe, and the hub's hardware-quirks row.
  - A **single-sector write blocks ~205-220 ms inside one INT 13h call** (AH=03 AL=01) at specific LBAs.
  - Twelve of fourteen fell in cylinders 730-737; one was at cylinder 0, in the FAT/directory region.
  - "Plain fsync on this card costs ~5 ms."
  - Each save issues a set of single-sector writes:
    - at FLUSHBUF on close: the dirty data tails (5; 11 for MMD), the patched sectors (4; 5 for MMD), 1-2 FAT sectors
      x 2 copies, and the directory sector of C:\DOSAGS;
    - earlier, on any buffer eviction.
  - The FAT and directory sectors are rewritten every run.
  - A bimodal "0 or 1+ stalls" cost per save fits the record: 210-228 against 426-593 ms. It is not proven by it: the
    excess is 216-383 ms, not a clean multiple of 212.

**The 486 measurement that decides it.** This lab exe (or its release twin with only the trace), DOSAGS_SW=1, on the
S32P line, in one machine state, with the INT 21h trace per cell:
1. **Which call holds the excess.** Is the 210-300 ms inside one 40h data write, one in-place 40h patch, the open's 40h
   CX=0 (RELEASE: FAT), or the 3Eh close (FLUSHBUF: dirty data, FAT and directory sectors)? The trace times every one
   at 0.84 us resolution. A ~210 ms single call is the stall; a spread over many 40h calls is throughput or FAT scanning.
2. **Whether the prior file's size matters**, same binary, one boot:
   - (a) prior 59,538 B, (b) prior 146,822 B (shrink), (c) no prior file, alternated as ABBA;
   - with `DIR C:\DOSAGS\AGSSAVE.999` and `CHKDSK C:` (read-only: free clusters) before and after;
   - the shrink hypothesis predicts (b) < (a) in every pair; the CF-stall hypothesis predicts no size effect, with the
     stall following the call that writes the stalling sector.
3. **Optional, decisive for "which sector":** fold the existing int13-probe hook (tests/harness/results/int13-probe/
   int13hook.asm, hookbin.h; its slow-call ring records CHS) into the same lab build. Then the stalled call's LBA can be
   read as data / FAT / directory. It is not built here: DOSBox-X's mounted C: never reaches INT 13h, so it can only be
   validated on the 486.

## 5. Candidate exact levers

**Basis for the 486 estimates.**
- **CPU.** The DOSBox-X saving at 40k (section 3, un-instrumented) is scaled by 1.5-2.3x, the 486/40k ratios this repo
  has measured on engine work: room entry 4.1 s / 2.2 s = 1.9x; 380 / 244 ms = 1.56x; GetGlobalInt 2.3x (LAB-R2/R3).
  Sanity check: 71 ms x 1.5-2.3 = 105-165 ms, under the 486's best observed write (210-213 ms), which leaves ~45-105 ms
  for real disk work.
- **I/O.** Per single-sector CF operation, 1-5 ms ("plain fsync ~5 ms" on this card). Plus the possibility (section 4)
  that one ~210-300 ms stall rides on a sector this lever stops writing.
- **Exactness gate for every lever**, run as one gate:
  - sha256 of AGSSAVE.999 equal, lever on vs off, on 5days (S32P and S16), Trilby and MMD, with DOSAGS_RANDSEED=1;
  - save/load round trips EQUAL;
  - every game output line EQUAL (eqcmp.py).
  - **Seeding is required for the sha gate:** unseeded, two runs differ in 2 bytes at offset 2051 (play's random seed,
    time()). Seeded, every cell here gave one sha per fixture, in every arm and prior state:
    - 5days S32P ab2b12a0..., 5days S16 80350c10..., Trilby c19cb511..., MMD db6d2347...;
    - the off arms (S32-off, S8-off, MM-off, *-offcpu) equal the SW=1/2 arms;
    - eqcmp EQUAL on every SW arm vs off (19 lines on 5days, 27 on Trilby, 27 on MMD).

| rank | lever | DOS calls per save (5days; MMD) | CPU saving at 40k (measured) | 486 estimate | exactness |
|---|---|---|---|---|---|
| **1** | **A. Serialise the whole save into memory (VectorStream), then open and write once.** Same open ("wb" truncate), the bytes go out in one fwrite (16 KB DOS chunks), then close. | 40h: 16 -> 5 (1 truncate + 4 x <=16 KB; MMD 24 -> 10); 42h 82 -> 0-4; 44h 14 -> 1; no in-place writes; 1 buffered tail instead of 5 (11); 0 patched sectors instead of 4 (5) | 5days 71 -> ~56 (dry 54.3 + one write ~1.5): **~15 ms**; Trilby 68 -> ~53: ~15; MMD 125 -> ~92: ~33 | CPU 23-35 ms (MMD 50-75); I/O: ~8 fewer dirty single-sector writes and 4 fewer pre-reads, 10-60 ms. **No-stall case ~35-95 ms**. If the stall rides on a removed data-sector rewrite: + the whole ~210-300 ms excess | **Measured byte-equal**: dry_equal=1 on all four fixtures (S32P, S16, Trilby, MMD; the drycpu repeats too). It is the same serialiser writing into a Stream with the same Seek/Write/GetPosition semantics. BufferedStream and MemoryStream both clamp Seek to [0, end] and overwrite in place, so every patch lands at the same offset. Only the stream behind it changes. Memory peak = file size (146,822 B for MMD). Errors: the write fails at the end instead of part way; today SaveGame() checks no write result either way. |
| 2 | F. The same effect through BufferedStream: a per-instance buffer of at least the file size for this one stream | as A, plus the 4 open-time seeks | slightly less than A (the BufferedStream per-call cost stays: ~12 ms of the 63 ms serialisation at 40k, Trilby) | below A | exact for the same reason, but it touches a class every file read uses (BufferSize is a static const): more surface than A. |
| 3 | D. Stage each component in memory and write header + data sequentially (no per-component seek-back) | removes the 4 (MMD 5) component patch pairs, keeps WriteFileFormat's final 20 B patch at offset 39 (1 in-place write, 1 pre-read of sector 0) | ~ A minus one seek pair | a little less than A | exact (same bytes in the same order); memory peak = the largest component. Dominated by A. |
| 4 | **DECLINED (sdlports review, 2026-11-07): gives up crash safety; not built.** E. Overwrite in place instead of truncating: open "r+b" (fall back to "wb" if the file is absent), write, then cut the file at the final length (`_write(fd,0,0)` at EOF) | removes RELEASE + ALLOCATE when the size is unchanged: no FAT sector dirtied at all; a shrink frees only the tail; a growth allocates only the extra | ~0 | **only worth anything if the 486 trace puts the excess in FAT work** (open's 40h CX=0, the allocating 40h, or 3Eh's FAT flush). Then up to the whole excess. Otherwise ~0. Best combined with A | bytes exact if the final cut is made. **Not equivalent on failure:** a crash part way leaves old bytes past the write point, a header-valid but mixed save, where today's truncate leaves a short file. Needs the operator's call even if exact. |
| 5 | B. A larger setvbuf on the FILE | none removed: every fseek in DJGPP fflushes first, and _write_int splits at the 16 KB transfer buffer regardless; the FILE already merges BufferedStream's 8 KB flushes into 16 KB 40h calls | ~0 | ~0 | exact, and pointless. |
| -- | C. Remove per-write flushes | there are none: no fflush, fsync or _commit in the path. The flushes are fseek's side effect, which A/D remove | -- | -- | -- |
| -- | Pre-size the file | DJGPP's lseek past EOF zero-fills the gap on the next write: up to 2x the bytes written, and the size is not known before serialisation (it is after A) | negative | negative | exact, counter-productive. |

## 6. Pre-registration draft for the first lever (486)

**Superseded by section 9** (the final draft, sized to the gates in section 8). Kept as first written.

**Round SW1 (draft, not registered).** Lever A behind one env toggle in one lab binary. Proposed name:
DOSAGS_SAVEMEM, =1 serialise to memory and write once, =0 today's path. The SW=1 trace stays in the same build, off
unless set.

- **Binary and gates before any rig time (DOSBox-X, fixed 40k, seeded):**
  - AGSSAVE.999 sha256 equal, SAVEMEM=1 vs 0, on 5days S32P (ab2b12a0...), 5days S16 (80350c10...), Trilby
    (c19cb511...) and MMD title (db6d2347...);
  - restore round trip EQUAL: a --loadsavedgame 999 cell from each arm's save, eqcmp of the restored run's output
    lines, both arms;
  - eqcmp EQUAL on every fixture;
  - the SW=1 trace in the ON arm shows the predicted counts: 40h = 1 truncate + ceil(size / 16384) data writes, zero
    in-place writes, 42h <= 4.
- **Cells (one power-on, one machine state).** Round SU's RUN.BAT mechanism fields: SVPRE / DIRLIST / SDRV / SVPOST.
  Add `CHKDSK C:` (read-only) before the first cell and after the last, for free clusters.
  - **S32P line verbatim** (as SU32*): ABBA x2 = OFF ON ON OFF OFF ON ON OFF, 8 timing cells, **DOSAGS_SW unset**. The
    trace costs 18-35 ms at 40k, mostly in the per-Write hook, which the ON arm would not pay (it writes to a
    VectorStream), so it would bias the timing.
  - **2 trace cells at the end:** OFF + SW=1, then ON + SW=1. They attribute the time per INT 21h call (section 4,
    point 1).
  - Optional: the S8 line ABBA x1 (4 cells).
  - 10-14 cells, about one SU-length power-on.
- **Prediction on restart_savegame_ms, S32P (OFF expected ~420-600, as SU's 426-516):**
  - **H1, registered band: every ON cell 110-210 ms**, from ~500. This is the case where the excess rides on a sector
    the lever stops writing: the unaligned buffered tails or the patched sectors. Basis:
    - ON CPU (54.3 + ~1.5 ms at 40k) x 1.5-2.3 = 85-130 ms;
    - plus the sequential write, FAT and directory flush: ~30-80 ms, which is the OFF floor's I/O (210 - 71 x 1.5-2.3
      = 47-103) less 10-60.
  - **Floor claim (holds whatever the mechanism): mean paired d = OFF - ON >= 35 ms** (estimate 35-95 for S32P).
- **Falsifiers:**
  - H1 is falsified if **any ON cell exceeds 260 ms while its adjacent OFF cell is >= 400 ms.** Then the excess is not
    on the removed writes; the two trace cells say where it is (FAT/allocation -> lever E is next; directory or close
    -> neither lever).
  - The floor claim is falsified if mean d < 20 ms.
  - The exactness gate is falsified by any sha256 / round-trip / output-line DIFF. That stops the round before the rig.
- **Validity:** H1 is scored only if >= 3 of 4 OFF cells read >= 400 ms. On a stall-free day (OFF ~210) H1 is VOID; the
  floor claim is still scored.
- **Information, not scored:**
  - OFF and ON spread;
  - free clusters before and after;
  - whether the ON arm's trace cell still carries a single >= 150 ms call, and which.

## 7. Cells, results and files

- **Exactness evidence collected here** (no lever built):
  - **dry_equal=1 in all 7 SW=2 cells**: S32-dry, S32-drycpu, S16-dry, S8-dry, S8-drycpu, MM-dry, MM-drycpu. The in-memory
    serialisation equals the file byte for byte.
  - Seeded saves have one sha per fixture across SW off / 1 / 2, conf and prior state:
    - 5days S32P ab2b12a0445b22bb3c4caf43bb63a6022795dc1154d52bafce00c287bea2a0e9;
    - 5days S16 80350c1030a205213aeaac3af3c388859a92492d6a3668372a1c46676b7d767e;
    - Trilby c19cb511d7c077c9f793074ed256f2633a070ada2e782679f3349e32ab5bc47a;
    - MMD db6d2347575ae8c6b10435ac75b63b67eba92609a3c56c544b272d211d06e64c;
    - unseeded (S32-new, S32-same, S8-new): b31841d3..., ebf94307..., 6b4e0091..., which differ only in the time()
      seed bytes.
  - eqcmp.py, game output lines EQUAL:
    - S8-new2 / S8-same / S8-dry / S8-offcpu vs S8-off (27 lines);
    - MM-new / MM-same / MM-dry vs MM-off (27);
    - S32-new2 / S32-dry / S32-shrink / S32-offcpu vs S32-off (19);
    - S16-new / S16-dry vs S16-off (19).
  - **Save/load round trips were not run** (no lever exists to compare). They are a gate in section 6.
- **Not done / limits:**
  - Nothing here measures CF, SMARTDRV or DOS 6.22 itself.
  - The DOS buffer, FAT and pre-read semantics are read from the MS-DOS 4.0 source and assumed for 6.22.
  - No INT 13h counts: DOSBox-X's mounted drive never reaches INT 13h.
  - The 486 estimates in section 5 are scaled, with the basis stated.
- **Files** (worktree ~/git/dosags-lab-sw, all untracked; build/ is gitignored):
  - LAB-SW.md (this write-up);
  - build/sw/lab-sw.diff (the lab instrumentation over vendor/ags 0367);
  - build/sw/exe/swlab1.exe (sha256 35f676ac...);
  - build/sw/{swcell.sh, drive1.sh, drive2.sh, args.sh, dosbox-x-fixed40k-opl3-norate.conf};
  - build/sw/tools/{swan.py, swtab.py, eqcmp.py};
  - build/sw/results/<cell>/ (30 cells; S16-same's first attempt failed because its prior did not exist yet, and was
    re-run in drive2);
  - build/sw/results/{TABLE.md, drive1.log, drive2.log};
  - build/sw/saves/ (game-derived, local only, never commit).

All cells:

(restart_savegame_ms: the trace header in SW cells; else the STDOUT line or, for 5days, the journey write_ms)
| cell | prior (B) | save (B) | sha256[:12] | restart_savegame_ms | int21 n / ms | stdio fwrite ms | fseek ms | open / close ms | bracket - int21 (CPU-side) ms | dry run |
|---|---|---|---|---|---|---|---|---|---|---|
| MM-cpu | 146822 | 146822 | db6d2347575a | 160 (trace) | 146 / 2.9 | 2.626 | 3.911 | 0.246 / 0.220 | 157.6 | dry=off |
| MM-dry | 146822 | 146822 | db6d2347575a | 261 (trace) | 146 / 104.2 | 21.419 | 82.391 | 1.399 / 3.099 | 157.6 | dry=on dry_ms=89.309 dry_bytes=146822 disk_bytes=146822 dry_equal=1 |
| MM-drycpu | 146822 | 146822 | db6d2347575a | 160 (trace) | 146 / 2.9 | 2.622 | 3.908 | 0.246 / 0.221 | 157.6 | dry=on dry_ms=89.309 dry_bytes=146822 disk_bytes=146822 dry_equal=1 |
| MM-new | - | 146822 | db6d2347575a | 271 (trace) | 152 / 114.0 | 23.713 | 87.431 | 1.751 / 5.402 | 157.7 | dry=off |
| MM-off | 146822 | 146822 | db6d2347575a | 236 | (off) | | | | | |
| MM-offcpu | 146822 | 146822 | db6d2347575a | 125 | (off) | | | | | |
| MM-same | 146822 | 146822 | db6d2347575a | 266 (trace) | 146 / 109.2 | 25.031 | 84.582 | 1.756 / 1.939 | 157.6 | dry=off |
| S16-dry | 59538 | 59538 | 80350c1030a2 | 171 (trace) | 117 / 82.3 | 6.955 | 70.131 | 1.643 / 5.942 | 89.3 | dry=on dry_ms=56.894 dry_bytes=59538 disk_bytes=59538 dry_equal=1 |
| S16-new | - | 59538 | 80350c1030a2 | 171 (trace) | 123 / 82.2 | 6.690 | 69.440 | 2.643 / 5.943 | 89.4 | dry=off |
| S16-off | 59538 | 59538 | 80350c1030a2 | 154 | (off) | | | | | |
| S16-same | 59538 | 59538 | 80350c1030a2 | 172 (trace) | 117 / 83.3 | 7.048 | 71.080 | 1.644 / 5.943 | 89.3 | dry=off |
| S32-cpu | 59538 | 59538 | ab2b12a0445b | 89 (trace) | 117 / 2.3 | 0.903 | 3.290 | 0.246 / 0.223 | 87.5 | dry=off |
| S32-dry | 59538 | 59538 | ab2b12a0445b | 169 (trace) | 117 / 82.2 | 7.193 | 70.399 | 1.633 / 5.307 | 87.4 | dry=on dry_ms=54.289 dry_bytes=59538 disk_bytes=59538 dry_equal=1 |
| S32-drycpu | 59538 | 59538 | ab2b12a0445b | 89 (trace) | 117 / 2.3 | 0.904 | 3.290 | 0.246 / 0.224 | 87.5 | dry=on dry_ms=54.289 dry_bytes=59538 disk_bytes=59538 dry_equal=1 |
| S32-new | - | 59538 | b31841d31503 | 168 (trace) | 123 / 81.0 | 7.407 | 67.463 | 2.637 / 5.942 | 87.6 | dry=off |
| S32-new2 | - | 59538 | ab2b12a0445b | 168 (trace) | 123 / 81.0 | 7.452 | 67.427 | 2.632 / 5.942 | 87.6 | dry=off |
| S32-off | 59538 | 59538 | ab2b12a0445b | 151 | (off) | | | | | |
| S32-offcpu | 59538 | 59538 | ab2b12a0445b | 71 | (off) | | | | | |
| S32-same | 59538 | 59538 | ebf94307c744 | 168 (trace) | 117 / 81.2 | 7.406 | 68.543 | 1.637 / 5.942 | 87.5 | dry=off |
| S32-same2 | 59538 | 59538 | ab2b12a0445b | 172 (trace) | 117 / 85.2 | 7.406 | 74.367 | 1.633 / 4.133 | 87.4 | dry=off |
| S32-shrink | 146822 | 59538 | ab2b12a0445b | 166 (trace) | 117 / 79.1 | 7.409 | 66.509 | 1.632 / 5.942 | 87.5 | dry=off |
| S8-cpu | 61199 | 61199 | c19cb511d7c0 | 86 (trace) | 117 / 2.3 | 0.920 | 3.310 | 0.247 / 0.221 | 84.3 | dry=off |
| S8-dry | 61199 | 61199 | c19cb511d7c0 | 95 (trace) | 117 / 11.1 | 2.923 | 9.861 | 0.379 / 0.329 | 84.3 | dry=on dry_ms=51.263 dry_bytes=61199 disk_bytes=61199 dry_equal=1 |
| S8-drycpu | 61199 | 61199 | c19cb511d7c0 | 86 (trace) | 117 / 2.3 | 0.916 | 3.308 | 0.246 / 0.221 | 84.3 | dry=on dry_ms=51.264 dry_bytes=61199 disk_bytes=61199 dry_equal=1 |
| S8-grow | 59538 | 61199 | c19cb511d7c0 | 95 (trace) | 117 / 11.1 | 2.924 | 9.859 | 0.379 / 0.329 | 84.3 | dry=off |
| S8-new | - | 61199 | 6b4e00913fe3 | 95 (trace) | 123 / 11.2 | 2.925 | 9.762 | 0.721 / 0.329 | 84.4 | dry=off |
| S8-new2 | - | 61199 | c19cb511d7c0 | 95 (trace) | 123 / 11.3 | 2.920 | 9.797 | 0.729 / 0.329 | 84.4 | dry=off |
| S8-off | 61199 | 61199 | c19cb511d7c0 | 77 | (off) | | | | | |
| S8-offcpu | 61199 | 61199 | c19cb511d7c0 | 68 | (off) | | | | | |
| S8-same | 61199 | 61199 | c19cb511d7c0 | 95 (trace) | 117 / 11.1 | 2.927 | 9.863 | 0.380 / 0.329 | 84.3 | dry=off |

## 8. Lever 1 built (lab): DOSAGS_SAVEMEM, serialise to memory then write once -- and its gates G1-G5

**Code** (build/sw/lab-sw2.diff over vendor/ags 0367, 676 lines, sha256 4915942e177d6798..., ASCII). The diff is
cumulative: section 0's tracer plus the following.
- **Engine/game/savegame.cpp, SaveGame(): every save, not only slot 999.** No reason to scope it was found:
  - normal saves are deflated and smaller, and their screenshot (when the game has one) is deflated too;
  - the memory needed is the file size;
  - plugins' save hooks are not built on DOS (AGS_BUILTIN_PLUGINS=OFF).
  The steps:
  - DOSAGS_SAVEMEM, read once. `0` = today's streaming path, untouched. Unset or anything else = 1.
  - =1: **the FileStream is opened first** (fopen "wb", the same truncation and the same failure point as today,
    before any serialisation). Then:
    - the whole save is serialised into a std::vector through a VectorStream, with 256 KB reserved. These are the same
      steps as StartSavegame() + SaveGame(), factored into dos_save_body();
    - one FileStream::Write (one fwrite) of the image;
    - Close (fclose).
  - A write shortfall is counted (`short=`) and otherwise ignored, as today's path ignores write results.
- **Memory failure.** A std::bad_alloc while reserving or growing is caught. The partial image is freed, the
  already-open FileStream is wrapped in the usual BufferedStream (exactly File::OpenFile's construction), and the
  streaming path runs from the start. This is counted as `fallback=`.
  - The only state a second serialisation re-touches is DoBeforeSave's, which are idempotent copies.
  - G4 checks exactly this with the failure forced after the whole image was serialised.
- **Lab knob** (instrumented flavour only): DOSAGS_LAB_SAVEMEM_FAIL=1 makes the reservation fail; =2 makes the failure
  come after the full serialisation.
- **Witness, both flavours, one line per save** (in save_game, after the write is timed and recorded):
  `DOS-PORT savemem DOSAGS_SAVEMEM mode=m slot=n path=mem|fallback|stream bytes=B mem=.. fallback=.. stream=.. short=.. failknob=k`.
- **Release flavour:**
  - the lever and the witness only;
  - the tracer, the __dpmi_int wrap (now conditional in Engine/CMakeLists.txt) and every lab knob are compiled out.
  - Checked with nm: no wrap, dos_sw_, dos_lab_ or saveat symbol in swrel2.exe.
- **Lab-only gate helpers** (instrumented flavour):
  - LAB-PLAY's DOSAGS_LABCLICKS and DOSAGS_LAB_FRAMEHASH, copied verbatim from docs/lab/r3-lab-patches/lab-r3-full.diff;
  - DOSAGS_LAB_SAVEAT=lc:slot, a scripted normal save: SaveGameSlot(slot, "LABSAVE") when the loop counter first
    reaches lc.

**Exes (lab records, build_dirty=1, from base main 41d82c06 + build/sw/lab-sw2.diff):**

| exe | flavour | sha256 | binary_sha12 | use |
|---|---|---|---|---|
| build/sw/exe/swrel2.exe | release (`make DOSAGS_RELEASE=1 game`) | 3b76f3dce4014ab22b1dc043d13153f5d03926fe7f66c08898bce9d1a16d9249 | 761f64ceccac | SW1 ABBA timing cells |
| build/sw/exe/swlab2.exe | instrumented (`make game`) | 6c1a2f2dd002d1221d71f51b81306eb55a2bcf83acbc8e74f316f00ff92fdd4b | c72796d35101 | SW1 trace cells, the G fixture, G4/G5 |

Every gate cell's RUNMANI.LOG carries its exe's binary_sha12 and build_dirty=1 (build/sw/results/GATES.md, "stamps").

**Gate fixtures** (DOSBox-X fixed 40k, DOSAGS_RANDSEED=1 everywhere):
- S32P, S16, S8 and MMD title: section 0's lines, --sb-live, with the prior AGSSAVE.999 present.
- **G**: LAB-PLAY's fixture G, the same command as docs/lab LAB-R3 section 6.
  - MMD from save 007 (f486d0e9...), --loadsavedgame 7, the 14 LABCLICKS, exit 8600;
  - every tick rendered (no fixed timestep), FRAMEHASH + PRESENT_VERIFY;
  - **plus DOSAGS_LAB_SAVEAT=6500:1**: a normal, deflated save to slot 1 at lc 6500.
  - The restore from 007 skips the restart point, so G writes no 999.
- **GS**: G cut at exit 6600, for the fallback cells.
- **GR**: restore the produced AGSSAVE.001 (--loadsavedgame 1), exit 7600, FRAMEHASH.
- **S8R**: restore the produced AGSSAVE.999 under Trilby (--loadsavedgame 999).
- RUN.BAT SET bytes: G 492, the largest. The last SET (DOSAGS_SAVEMEM) survived in every cell: the witness shows the
  intended mode in all of them.

### G1 byte equality (SAVEMEM=0 vs =1)

| fixture | file | =0 sha256 (size) | =1 sha256 (size) | equal | =0 witness | =1 witness |
|---|---|---|---|---|---|---|
| S32P | AGSSAVE.999 | ab2b12a0445b22bb3c4caf43bb63a6022795dc1154d52bafce00c287bea2a0e9 (59538) | ab2b12a0445b22bb3c4caf43bb63a6022795dc1154d52bafce00c287bea2a0e9 (59538) | EQUAL | mode=0 slot=999 path=stream bytes=0 mem=0 fallback=0 stream=1 short=0 failknob=0 | mode=1 slot=999 path=mem bytes=59538 mem=1 fallback=0 stream=0 short=0 failknob=0 |
| S16 | AGSSAVE.999 | 80350c1030a205213aeaac3af3c388859a92492d6a3668372a1c46676b7d767e (59538) | 80350c1030a205213aeaac3af3c388859a92492d6a3668372a1c46676b7d767e (59538) | EQUAL | mode=0 slot=999 path=stream bytes=0 mem=0 fallback=0 stream=1 short=0 failknob=0 | mode=1 slot=999 path=mem bytes=59538 mem=1 fallback=0 stream=0 short=0 failknob=0 |
| S8 Trilby r35 | AGSSAVE.999 | c19cb511d7c077c9f793074ed256f2633a070ada2e782679f3349e32ab5bc47a (61199) | c19cb511d7c077c9f793074ed256f2633a070ada2e782679f3349e32ab5bc47a (61199) | EQUAL | mode=0 slot=999 path=stream bytes=0 mem=0 fallback=0 stream=1 short=0 failknob=0 | mode=1 slot=999 path=mem bytes=61199 mem=1 fallback=0 stream=0 short=0 failknob=0 |
| MMD title | AGSSAVE.999 | db6d2347575ae8c6b10435ac75b63b67eba92609a3c56c544b272d211d06e64c (146822) | db6d2347575ae8c6b10435ac75b63b67eba92609a3c56c544b272d211d06e64c (146822) | EQUAL | mode=0 slot=999 path=stream bytes=0 mem=0 fallback=0 stream=1 short=0 failknob=0 | mode=1 slot=999 path=mem bytes=146822 mem=1 fallback=0 stream=0 short=0 failknob=0 |
| G: normal save slot 1 (deflated) | AGSSAVE.001 | 360d7df1604efe75d16effe79457ac4889deffa8b9c6f219fa7450524e0844fc (13552) | 360d7df1604efe75d16effe79457ac4889deffa8b9c6f219fa7450524e0844fc (13552) | EQUAL | mode=0 slot=1 path=stream bytes=0 mem=0 fallback=0 stream=1 short=0 failknob=0 | mode=1 slot=1 path=mem bytes=13552 mem=1 fallback=0 stream=0 short=0 failknob=0 |

### G3 game output lines and frame digest (=0 vs =1)

- R-S32-m0 19 lines | R-S32-m1 19 lines | EQUAL
- R-S16-m0 19 lines | R-S16-m1 19 lines | EQUAL
- R-S8-m0 27 lines | R-S8-m1 27 lines | EQUAL
- R-MM-m0 27 lines | R-MM-m1 27 lines | EQUAL
- I-G-m0 35 lines | I-G-m1 35 lines | EQUAL
- frame digest, fixture G: I-G-m0: 3194 records, 3164 loop counters / I-G-m1: 3194 records, common lc 3164, EQUAL 3164, DIFF 0

### G4 forced fallback (DOSAGS_LAB_SAVEMEM_FAIL)

| cell | file | OFF (=0) sha256 | ON (=1) sha256 | fallback sha256 | equal to OFF | equal to ON | witness |
|---|---|---|---|---|---|---|---|
| I-S8-f1 | AGSSAVE.999 | c19cb511d7c077c9 | c19cb511d7c077c9 | c19cb511d7c077c9 | EQUAL | EQUAL | mode=1 slot=999 path=fallback bytes=61199 mem=0 fallback=1 stream=0 short=0 failknob=1 |
| I-S8-f2 | AGSSAVE.999 | c19cb511d7c077c9 | c19cb511d7c077c9 | c19cb511d7c077c9 | EQUAL | EQUAL | mode=1 slot=999 path=fallback bytes=61199 mem=0 fallback=1 stream=0 short=0 failknob=2 |
| I-Gs-f1 | AGSSAVE.001 | 360d7df1604efe75 | 360d7df1604efe75 | 360d7df1604efe75 | EQUAL | EQUAL | mode=1 slot=1 path=fallback bytes=13552 mem=0 fallback=1 stream=0 short=0 failknob=1 |
| I-Gs-f2 | AGSSAVE.001 | 360d7df1604efe75 | 360d7df1604efe75 | 360d7df1604efe75 | EQUAL | EQUAL | mode=1 slot=1 path=fallback bytes=13552 mem=0 fallback=1 stream=0 short=0 failknob=2 |

### G2 round trips (save with X, restore with Y; vs 0/0)

- R-S8R-00 18 lines | R-S8R-10 18 lines | EQUAL
- R-S8R-00 18 lines | R-S8R-01 18 lines | EQUAL
- R-S8R-00 18 lines | R-S8R-11 18 lines | EQUAL
- I-GR-00 9 lines | I-GR-10 9 lines | EQUAL
- I-GR-00 9 lines | I-GR-01 9 lines | EQUAL
- I-GR-00 9 lines | I-GR-11 9 lines | EQUAL
- frame digest, slot-1 restores: I-GR-00: 1115 records, 1100 loop counters / I-GR-10: 1115 records, common lc 1100, EQUAL 1100, DIFF 0 / I-GR-01: 1115 records, common lc 1100, EQUAL 1100, DIFF 0 / I-GR-11: 1115 records, common lc 1100, EQUAL 1100, DIFF 0

**G1 PASS.** Equal on all four restart-point fixtures and on the normal deflated slot-1 save.

**G2 PASS.** Every restore printed `Restoring saved game './agssave.999'` (or `.001`).
- S8R: 18 lines each.
- GR: 9 lines each, and the frame digest is EQUAL 1100 of 1100 from lc 6500.

**G3 PASS.**
- Output lines are EQUAL on all five fixtures.
- **Frame digest on fixture G: EQUAL 3164 of 3164 loop counters**, from lc 5436 to 8599. That spans the slot-1 save
  at 6500.

**G4 PASS.**
- The forced fallback, at both knob points (the reservation fails; or the failure comes after the full image), gives
  **the OFF arm's bytes**. They also equal ON.
- fallback=1 on the witness line.
- I-S8-f2's trace shows the full memory image (M record, 61,199 B), then the streaming path's own 117 INT 21h, the same
  as OFF.

**G5 PASS** (SW=1 tracer, swlab2.exe):

| | 5days S32P | Trilby r35 | MMD title | predicted (section 5) |
|---|---|---|---|---|
| INT 21h total, =0 -> =1 | 117 -> **11** | 117 -> **11** | 146 -> **16** | -- |
| 40h (incl. the open's CX=0 truncate) | 16 -> **5** (1 + 16384 x3 + 10386) | 16 -> **5** (1 + 16384 x3 + 12047) | 24 -> **10** (1 + 16384 x8 + 15750) | 16 -> 5; MMD 24 -> 10 |
| 42h | 82 -> **0** | 82 -> **0** | 100 -> **0** | 0-4 |
| 44h | 14 -> **1** | 14 -> **1** | 17 -> **1** | 1 |
| in-place (patch) writes | 9 -> **0** | 9 -> **0** | 11 -> **0** | 0 |
| fwrite calls | 19 -> **1** | 19 -> **1** | 33 -> **1** | 1 |
| buffered partial-sector tails | 5 -> **1** | 5 -> **1** | 11 -> **1** | 1 |
| serialise into memory (trace M record, ms at 40k) | 54.4 | 50.8 | 89.3 | = the dry runs (54.3 / 51.3 / 89.3) |

- Cells: I-S32-m1sw, T-S8-m1sw, I-MM-m1sw. The =0 side is I-S8-m0sw on this exe (identical to section 2's swlab1
  counts) and section 2.
- 42h is 0, not the 0-4 predicted, because the lever writes through a bare FileStream: BufferedStream::Open's four
  seeks are gone too.

**Timing in DOSBox-X** (release swrel2.exe, uninstrumented; restart_savegame_ms or the journey write_ms):

| line | default conf (disk-rate emulation on): =0 -> =1 | norate conf (CPU side): =0 -> =1 |
|---|---|---|
| 5days S32P | 145 -> 68 | **70 -> 56** (and 70 -> 56 again: N-S32-*b) |
| 5days S16 | 150 -> 70 | -- |
| Trilby r35 | 77 -> 60 | **67 -> 53** |
| MMD title | 229 -> 118 | **123 -> 93** |

- The CPU-side saving is measured at 14 / 14 / 30 ms. Section 5 predicted ~15 / ~15 / ~33 from the dry runs. The saves
  are sha-equal and the output lines EQUAL in all of these cells.
- The default-conf column includes DOSBox-X's emulated disk time (about 1 ms per file call), which the lever cuts with
  the call count. It is not a 486 figure.

## 9. SW1 pre-registration (final draft, not registered): lever 1 on the 486

**What is tested.** Lever 1 (section 8): DOSAGS_SAVEMEM=1, serialise to memory and write once, against =0, today's
streaming path. It is one env toggle inside one binary.

**Binaries: lab records, not a landing** (sdlports note 6).
- Both are built from the lab worktree, from base main 41d82c06 plus build/sw/lab-sw2.diff. Their manifest stamps carry
  build_dirty=1.
- **Timing exe: swrel2.exe**, the release flavour: sha256 3b76f3dce4014ab22b1dc043d13153f5d03926fe7f66c08898bce9d1a16d9249, binary_sha12 761f64ceccac, build_dirty=1.
  - It carries the lever and its witness line.
  - It has no tracer (no __dpmi_int wrap) and no lab knobs.
- **Trace exe: swlab2.exe**, the instrumented flavour: sha256 6c1a2f2dd002d1221d71f51b81306eb55a2bcf83acbc8e74f316f00ff92fdd4b, binary_sha12 c72796d35101, build_dirty=1.
  - It carries the lever, the SW=1 tracer, DOSAGS_LAB_SAVEMEM_FAIL, and LAB-PLAY's DOSAGS_LABCLICKS and
    DOSAGS_LAB_FRAMEHASH.
  - It also carries DOSAGS_LAB_SAVEAT.
- Both go through /sdldos:review as a **lab binary record**.
- The ON arm lands later as its own patch, 0369 or after, behind R3's 0368. It is re-validated then.

**Gates already met in DOSBox-X** (section 8): G1-G5, every one EQUAL or as predicted.

**Machine state.** One power-on.
- The rig's usual RUN.BAT mechanism lines per cell, as round SU: SVPRE / DIRLIST / SDRV / SVPOST.
- **CHKDSK C: before the first cell and after the last, read-only** (sdlports note 5):
  - never /F; run as `CHKDSK C: < NUL > CHKDSKn.TXT` so that it cannot prompt;
  - collected for the free-cluster count and the lost-chain line;
  - a CHKDSK that reports errors is recorded, not acted on.

**Cells.**
- **Timing: the S32P line verbatim** (round SU's S32), swrel2.exe, **trace OFF** (DOSAGS_SW unset; sdlports note 4).
  - ABBA x2: OFF ON ON OFF OFF ON ON OFF, so 8 cells. OFF = DOSAGS_SAVEMEM=0, ON = =1.
  - The witness line `DOS-PORT savemem DOSAGS_SAVEMEM mode=m slot=999 path=...` must show mode=0 path=stream in OFF
    cells and mode=1 path=mem fallback=0 in ON cells. A cell whose witness disagrees is VOID.
- **Trace: 2 cells at the end**, swlab2.exe, the S32P line, DOSAGS_SW=1: OFF, then ON. Only these two have the trace on.
  - They attribute the time per INT 21h call. The ON cell's predicted counts are those G5 met in DOSBox-X: INT 21h 11;
    40h = 1 + 4; 42h 0; 44h 1.
  - Their timings are not scored.
- **Optional: the S8 line**, ABBA x1, swrel2.exe, trace off, 4 cells.
- 10 cells (14 with S8): about one SU-length power-on.

**Scored on restart_savegame_ms, from the engine's own line:**
- **Primary claim, the floor.** The **median paired saving d = OFF - ON over the 4 ABBA pairs is >= 30 ms.** The mean
  is reported beside it. **Falsified if the median d < 20 ms.**
  - The basis is mechanism-free:
    - CPU, measured on this binary pair: 70 -> 56 ms at 40k on S32P (twice), so 14 ms; x 1.5-2.3 gives 21-32 ms;
    - DOS work removed (G5): 117 -> 11 INT 21h; 9 -> 0 in-place patches; 5 -> 1 buffered tails; 4 -> 0 patched sectors.
      That is about 4 pre-reads and 8 single-sector writes fewer; at 1-5 ms per single-sector CF operation, 10-60 ms.
    - **Estimate 31-92 ms, central ~50.**
  - **Why 30 and the median, not section 6's 35 and the mean.** 35 sits above the bottom of the estimate (31). One
    ~212 ms stall landing in a single cell moves a 4-pair mean by ~50 ms either way: round SU had exactly one such
    pair, +216. The median of 4 pairs survives one such pair.
- **Second hypothesis, H1 (stated, not the headline).** If the run-to-run excess (OFF ~426-593 against the ~210 floor)
  rides on a sector this lever stops writing, **every ON cell reads 110-210 ms.**
  - **Falsified if any ON cell exceeds 260 ms while its adjacent OFF cell is >= 400 ms.**
  - **VOID unless >= 3 of 4 OFF cells read >= 400 ms** (on a stall-free day there is nothing to remove).
  - Why H1 is not the headline: the mechanism is unproven. The ~212 ms single-sector CF stall is documented on this
    card (int13-probe), but nothing yet places it on the data rewrites rather than on the FAT or directory sectors,
    which every save writes either way. The two trace cells are what would place it.
- **Information, not scored:**
  - OFF / ON spread;
  - free clusters before and after;
  - the two trace cells' per-call times: is the excess one call (a stall) or spread, and which call (40h data, 40h
    patch, the open's truncate, or 3Eh close)?
  - whole-run and preloop_ms per cell.

**The floor no I/O lever can touch** (sdlports note 3).
- At fixed 40k, serialisation is about 94% of the save: about 66 of 71 ms on 5 Days. The stdio + DOS path is 4.7 ms of
  CPU.
- Scaled 1.5-2.3x to the 486, that is **about 100-150 ms of the save's floor that no I/O lever can touch.**
- Lever 1 itself takes out the BufferedStream's share of it: serialisation into memory is 54.3 ms at 40k, about
  81-125 ms on the 486, and that remains with lever 1 on.
- **If H1 is VOID or falsified, the next lever class is faster serialisation**, not more I/O work. For example:
  - fewer per-call Stream::Write invocations: 7,870 of 9,547 calls on 5 Days are 4-byte WriteInt32;
  - batching a component's fields into one write.
  - It must be exact in the same way (sha256 equal on G1's five saves).

**My view on the headline.** The floor should be the primary claim, and H1 the stated second hypothesis.
- What is measured is the floor's mechanism: the CPU and the DOS-call counts.
- H1 rests on an unproven placement of the ~212 ms CF stall. Every save still writes the FAT and directory sectors
  with lever 1 on, and those are the sectors the int13-probe also saw stall (cylinder 0).
- If H1 holds, the round will show it anyway (ON 110-210 against OFF ~500). Headlining it would overstate what is known
  before the trace cells place the excess.

**Declined:** lever E, the "r+b" overwrite in place. It gives up crash safety (sdlports note 1) and is not built.

### Files for sections 8-9 (worktree ~/git/dosags-lab-sw, untracked; build/ is gitignored)

- build/sw/lab-sw2.diff: tracer + lever 1 + the lab gate helpers, over vendor/ags 0367.
- build/sw/exe/{swrel2.exe, swlab2.exe}.
- build/sw/{args.sh, swcell.sh, drive3.sh (gates), drive4.sh (norate timing)}.
- build/sw/tools/{gates.py, fhcmp.py (LAB-R2's)}.
- build/sw/results/{GATES.md, drive3.log, drive4.log}.
- Gate cells build/sw/results/{R-*, I-*, T-S8-m1sw, N-*}/.
- Saves: build/sw/saves/, local only; sha256 above.
