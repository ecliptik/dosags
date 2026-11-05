/* fsprobe -- what does one dos_port_dbg_log line actually cost on this card?
 *
 * The SDL3-DOS backend's dos_port_dbg_log does fprintf + fflush + fsync on
 * every call, and three of its call sites sit on a 100-flush cadence INSIDE
 * DOSVESA_UpdateWindowFramebuffer. A gate-window BENCH8 run does roughly
 * 8,000 flushes, so that is roughly 240 of these inside the present. Gate 2's
 * whole-run tick_rate misses its bar by 0.05-0.14 out of 39.2 -- about 0.3%
 * of the run -- so a per-call cost of even a few milliseconds is the same
 * order as the gap. Nobody has measured one on this target.
 *
 * Four arms, 200 iterations each, same ~90-byte line every time:
 *
 *   raw     fprintf only                     (stdio buffer, no syscall)
 *   flush   fprintf + fflush                 (adds the DOS write)
 *   sync    fprintf + fflush + fsync         (what dos_port_dbg_log does)
 *   reopen  fopen + fprintf + fclose         (the control: worst case)
 *
 * The interesting number is sync - flush: that is what fsync buys, and it is
 * the part that forces a FAT/directory commit rather than a buffered write.
 * Reported as min/mean/max per call in microseconds -- the MAX matters more
 * than the mean here, because the phenomenon being chased is a ~250 ms
 * outlier every ~20 s, not a steady tax.
 *
 * uclock() is the same clock SDL_GetPerformanceCounter uses on DJGPP
 * (src/timer/dos/SDL_systimer.c), so these microseconds are commensurable
 * with the fastpath-timing brackets.
 *
 * TZ is set before anything reads the clock: DJGPP with TZ unset produces
 * garbage libc zone state on real DOS and ~42 ms clock reads, which would
 * swamp exactly the signal this probe is looking for.
 *
 * ARM 5 was added after FPT1 and LGON1 both stalled on the write that
 * crossed 16,384 bytes -- FPT1's batch spanning 16,103 to 16,861 and LGON1's
 * 16,141 to 16,899, on different binaries, at the same flush index and the
 * same tick. That points at a FAT new-cluster allocation, but the 16 KB
 * cluster size is INFERRED from the coincidence and nothing has read it off
 * the volume. Arm 5 does both: it reports the real cluster size from DOS
 * itself, and it sweeps a file out past 96 KB one record at a time so every
 * boundary crossing in that range is timed individually. If the mechanism is
 * what we think, the spikes land on exact multiples of the reported cluster
 * size and nowhere else.
 *
 * Build: i586-pc-msdosdjgpp-gcc -O2 -o fsprobe.exe fsprobe.c
 * Run:   FSPROBE > PRBOUT.TXT
 * Writes and deletes FSPROBE.TMP and FSSWEEP.TMP in the current directory.
 * Run it TWICE from different directories -- once in the 316-entry C:\DOSAGS
 * and once in a fresh empty one -- to settle whether directory size drives
 * file-op cost. The exe takes no arguments; the BAT picks the location.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <dpmi.h>

#define ITERS 200
#define TMPNAME "FSPROBE.TMP"
#define SWEEPNAME "FSSWEEP.TMP"

/* Full path the sweep writes, FSPROBE_PATH; the drive letter in it (if any)
 * is what the geometry witness interrogates. */
static char g_sweep_path[128] = SWEEPNAME;
static unsigned long g_free_at_start = 0;
static int  g_sweep_drive = 0;   /* 0 = default, else 1=A */

static void resolve_sweep_path_from(const char *e)
{
    if (!e || !e[0]) e = getenv("FSPROBE_PATH");
    if (e && e[0]) {
        strncpy(g_sweep_path, e, sizeof(g_sweep_path) - 1);
        g_sweep_path[sizeof(g_sweep_path) - 1] = 0;
    }
    g_sweep_drive = 0;
    if (g_sweep_path[0] && g_sweep_path[1] == ':') {
        char c = g_sweep_path[0];
        if (c >= 'a' && c <= 'z') c = (char)(c - 'a' + 'A');
        g_sweep_drive = c - 'A' + 1;
    }
}

/* One sweep record. 800 bytes is close to the ~900 the SDL log writes per
 * 100-flush batch. Settable at runtime via FSPROBE_REC, because the record
 * size is the discriminator:
 *
 *   spikes at the same BYTE offsets  -> the trigger is a position, in the
 *                                       file, the allocation or the media;
 *   spikes at the same RECORD indices -> the trigger is an operation count,
 *                                       something above the media counting
 *                                       writes.
 *
 * At 800 bytes the spikes were record 8 / byte 6,400 and record 73 / byte
 * 58,400, twice. At 400 bytes those byte offsets are records 16 and 146, and
 * those record indices are bytes 3,200 and 29,200 -- the two families cannot
 * both be right. One env var, one binary, so nothing else varies. */
#define SWEEP_REC_MAX 4096
#define SWEEP_REC_DEFAULT 800
#define SWEEP_BYTES_DEFAULT 98304L  /* 96 KB */
/* Sweep length is runtime-settable via FSPROBE_SWEEP_KB because the open
 * question is now a RATE. Every sweep record is fsync'd, so every sweep byte
 * is a byte forced to the device -- which makes the sweep, run alone, a clean
 * events-per-device-byte measurement with no need to model what the arms
 * push and when. FSPROBE_ORDER=none skips the arms for exactly that. */
/* Report any record whose write cost this many us or more. The ordinary
 * cost is single-digit milliseconds and the event being hunted is ~230 ms,
 * so 20 ms separates them by an order of magnitude either way. */
#define SWEEP_SPIKE_US 20000UL

static const char *LINE =
    "fastpath-timing block @flush=12345: dpmi_ms_avg=0.001 copy_ms_avg=6.412 "
    "post_ms_avg=0.203 total_ms_avg=6.616 [over 100 flushes]\n";

struct stat_acc {
    unsigned long min_us, max_us;
    double sum_us;
    int n;
};

static void acc_init(struct stat_acc *a)
{
    a->min_us = 0xFFFFFFFFUL;
    a->max_us = 0;
    a->sum_us = 0.0;
    a->n = 0;
}

static void acc_add(struct stat_acc *a, unsigned long us)
{
    if (us < a->min_us) a->min_us = us;
    if (us > a->max_us) a->max_us = us;
    a->sum_us += (double)us;
    a->n++;
}

static void acc_print(const char *name, const struct stat_acc *a)
{
    printf("%-7s n=%d min_us=%lu mean_us=%.1f max_us=%lu total_ms=%.1f\n",
           name, a->n, a->min_us,
           a->n ? a->sum_us / a->n : 0.0,
           a->max_us, a->sum_us / 1000.0);
    fflush(stdout);
}

/* uclock() ticks per second; UCLOCKS_PER_SEC is a long long on DJGPP. */
static unsigned long elapsed_us(uclock_t t0, uclock_t t1)
{
    return (unsigned long)(((t1 - t0) * 1000000ULL) / UCLOCKS_PER_SEC);
}

/* INT 21h AH=36h -- Get Disk Free Space for the default drive.
 * AX = sectors per cluster (0xFFFF = invalid drive), BX = free clusters,
 * CX = bytes per sector, DX = total clusters. Reads the volume rather than
 * inferring it, which is the whole point. */
static void report_cluster_size(int drive);
static unsigned long free_bytes_on(int drive);

/* Each arm as its own function so FSPROBE_ORDER can run them in any order.
 * The order matters and that is the point: arms 1-3 each truncate and rewrite
 * bytes 0..25,600, so they all cross byte 6,400 at iteration 50, and whichever
 * one gets there FIRST is the one that pays if the ~220 ms event fires on the
 * first write to a region rather than on every write. In C:\DOSAGS `flush`
 * spiked at 212,867 us and in C:\FSTEST it peaked at 3,611 -- same arm, same
 * byte range, same crossing -- while `sync` spiked in both. Running `flush`
 * first turns that labelled speculation into a scored prediction. */
static int arm_raw(struct stat_acc *a)
{
    FILE *f = fopen(TMPNAME, "wb");
    int i;
    if (!f) return 0;
    for (i = 0; i < ITERS; i++) {
        uclock_t t0 = uclock();
        fprintf(f, "%s", LINE);
        acc_add(a, elapsed_us(t0, uclock()));
    }
    fclose(f);
    return 1;
}

static int arm_flush(struct stat_acc *a)
{
    FILE *f = fopen(TMPNAME, "wb");
    int i;
    if (!f) return 0;
    for (i = 0; i < ITERS; i++) {
        uclock_t t0 = uclock();
        fprintf(f, "%s", LINE);
        fflush(f);
        acc_add(a, elapsed_us(t0, uclock()));
    }
    fclose(f);
    return 1;
}

static int arm_sync(struct stat_acc *a)
{
    FILE *f = fopen(TMPNAME, "wb");
    int i;
    if (!f) return 0;
    for (i = 0; i < ITERS; i++) {
        uclock_t t0 = uclock();
        fprintf(f, "%s", LINE);
        fflush(f);
        fsync(fileno(f));
        acc_add(a, elapsed_us(t0, uclock()));
    }
    fclose(f);
    return 1;
}

static int arm_reopen(struct stat_acc *a)
{
    int i;
    for (i = 0; i < ITERS; i++) {
        uclock_t t0 = uclock();
        FILE *g = fopen(TMPNAME, "ab");
        if (g) { fprintf(g, "%s", LINE); fclose(g); }
        acc_add(a, elapsed_us(t0, uclock()));
    }
    return 1;
}


/* drive: 0 = default, 1 = A:, 3 = C: ... Taken from the path the sweep
 * actually opens, not from whatever the default drive happens to be. A
 * witness that interrogates the default while the callee writes an explicit
 * path can have both halves right and the cell silently void in the
 * flattering direction -- a clean "different device, no spikes" from a sweep
 * that ran on the CF card anyway. The witness sits on the callee. */
/* Free bytes on a drive, for the start/end-of-arm capacity witness. One
 * INT 21h call; distinguishes "the wrap is working" from "the wrap never
 * triggered because the arm was shorter than I thought". */
static unsigned long free_bytes_on(int drive)
{
    __dpmi_regs r;
    memset(&r, 0, sizeof(r));
    r.h.ah = 0x36;
    r.h.dl = (unsigned char)drive;
    __dpmi_int(0x21, &r);
    if (r.x.ax == 0xFFFF) return 0UL;
    return (unsigned long)r.x.bx * (unsigned long)r.x.ax * (unsigned long)r.x.cx;
}

static void report_cluster_size(int drive)
{
    __dpmi_regs r;

    /* INT 21h AH=19h -- current default drive, 0=A. Printed because a
     * boot-config change is being verified here and "the transfer returned 0
     * and a prompt appeared" is not proof the machine booted through the new
     * sequence. The drive letter and the geometry below are a DOS-SIDE
     * witness, independent of the transfer: the CF volume is 512 x 64 =
     * 32,768-byte clusters, 61,478 of them. Anything else is a different
     * device. A sweep that silently ran against the CF card again would look
     * like a clean result and would falsely convict DOS. */
    memset(&r, 0, sizeof(r));
    r.h.ah = 0x19;
    __dpmi_int(0x21, &r);
    printf("fsprobe: default drive = %c:, interrogating %s\n",
           'A' + r.h.al, drive ? "the sweep's own drive" : "the default drive");
    if (drive) printf("fsprobe: sweep drive = %c:\n", 'A' + drive - 1);
    fflush(stdout);

    memset(&r, 0, sizeof(r));
    r.h.ah = 0x36;
    r.h.dl = (unsigned char)drive;
    __dpmi_int(0x21, &r);
    if (r.x.ax == 0xFFFF) {
        printf("fsprobe: INT 21h/36h returned invalid-drive; cluster size UNKNOWN\n");
        return;
    }
    {
        unsigned long spc = r.x.ax, bps = r.x.cx;
        unsigned long total = r.x.dx, freec = r.x.bx;
        printf("fsprobe: bytes_per_sector=%lu sectors_per_cluster=%lu "
               "CLUSTER_BYTES=%lu\n", bps, spc, bps * spc);
        printf("fsprobe: total_clusters=%lu free_clusters=%lu "
               "volume_bytes=%lu free_bytes=%lu\n",
               total, freec, total * bps * spc, freec * bps * spc);
        if (bps * spc == 32768UL && total == 61478UL) {
            printf("fsprobe: GEOMETRY MATCHES THE CF VOLUME "
                   "(32768-byte clusters, 61478 total) -- this is C:, "
                   "NOT a different device.\n");
        } else {
            printf("fsprobe: geometry differs from the CF volume "
                   "(which is 32768 x 61478) -- this is a DIFFERENT device.\n");
        }
    }
    fflush(stdout);
}

/* Append SWEEP_REC-byte records out to SWEEP_BYTES, timing each write with
 * its fsync, and print every record that crosses SWEEP_SPIKE_US together
 * with the byte offset it ended at. */
static void sweep(void)
{
    static char rec[SWEEP_REC_MAX];
    FILE *f;
    long off = 0;
    int n = 0, spikes = 0;
    long attempted = 0, written = 0;
    int short_writes = 0, sync_fails = 0;
    unsigned long worst = 0, worst_off = 0;
    /* Cumulative elapsed time, and the non-spike total separately, because
     * every gap analysis so far has been in BYTES and time is the coordinate
     * the original observation pointed at -- the game's events reproduced
     * against the wall clock. Reconstructing it from an assumed per-record
     * cost does not work: the spread of the time gaps runs from 1.5x to 4.8x
     * as that assumption moves from 2 ms to 15 ms, so the answer would be a
     * property of the guess. Record it instead. */
    uclock_t sweep_t0;
    double cum_us = 0.0, quiet_us = 0.0;
    int quiet_n = 0;
    int recsz = SWEEP_REC_DEFAULT;
    long sweep_bytes = SWEEP_BYTES_DEFAULT;
    long sweep_ms = 0;       /* if set, TIME is the terminator */
    long wrap_bytes = 0;     /* if set, rewind the file at this size */
    uclock_t deadline_t0;

    {
        /* FSPROBE_SWEEP_MS -- run for a wall-clock duration instead of a byte
         * count. A RAM disk accepts a record in tens of microseconds against
         * this card's ~6,400, so a byte-matched arm finishes in 25-50 ms --
         * about a TENTH of one expected 436 ms period. Zero spikes would then
         * be guaranteed by construction and indistinguishable from the
         * finding: the most expensive false negative available, bought with
         * the one approved boot-config change. Match the arms on ELAPSED
         * TIME, and let the record count fall out of whatever the device
         * turns out to cost -- measured in the same run, never assumed,
         * because the conversion constant changes by two orders of magnitude
         * across the very change under test.
         *
         * FSPROBE_WRAP_KB -- rewind to offset 0 at this size. Time-matching a
         * RAM disk to a 3-second CF arm needs 25-50 MB of writes, which no
         * RAM disk here will hold. Both arms use the SAME wrap so the write
         * pattern is matched between them. */
        const char *e = getenv("FSPROBE_SWEEP_MS");
        if (e && e[0]) sweep_ms = atol(e);
        e = getenv("FSPROBE_WRAP_KB");
        if (e && e[0]) wrap_bytes = atol(e) * 1024L;
    }
    {
        const char *e = getenv("FSPROBE_SWEEP_KB");
        if (e && e[0]) {
            long v = atol(e);
            if (v >= 4 && v <= 4096) sweep_bytes = v * 1024L;
            else printf("fsprobe: FSPROBE_SWEEP_KB=%s out of range 4..4096, "
                        "using %ld\n", e, sweep_bytes);
        }
    }
    {
        const char *e = getenv("FSPROBE_REC");
        if (e && e[0]) {
            int v = atoi(e);
            if (v >= 64 && v <= SWEEP_REC_MAX) recsz = v;
            else printf("fsprobe: FSPROBE_REC=%s out of range 64..%d, using %d\n",
                        e, SWEEP_REC_MAX, recsz);
        }
    }

    memset(rec, 'x', (size_t)recsz);
    rec[recsz - 1] = '\n';

    f = fopen(g_sweep_path, "wb");
    if (!f) { printf("fsprobe: REFUSED -- cannot create %s\n", g_sweep_path); return; }

    g_free_at_start = free_bytes_on(g_sweep_drive);
    sweep_t0 = uclock();
    deadline_t0 = sweep_t0;
    if (sweep_ms > 0) {
        printf("\nfsprobe: sweep -- %d-byte records for %ld ms (TIME-terminated), "
               "wrap=%ld bytes, spikes >= %lu us\n",
               recsz, sweep_ms, wrap_bytes, (unsigned long)SWEEP_SPIKE_US);
    } else {
        printf("\nfsprobe: sweep -- %d-byte records to %ld bytes, spikes >= %lu us\n",
               recsz, sweep_bytes, (unsigned long)SWEEP_SPIKE_US);
    }
    printf("fsprobe: at this record size, byte 6400 is record %ld and byte "
           "58400 is record %ld; record 8 is byte %d and record 73 is byte %d\n",
           6400L / recsz, 58400L / recsz, 8 * recsz, 73 * recsz);
    fflush(stdout);

    for (;;) {
        if (sweep_ms > 0) {
            if ((long)(elapsed_us(deadline_t0, uclock()) / 1000UL) >= sweep_ms) break;
        } else if (off >= sweep_bytes) {
            break;
        }
        if (wrap_bytes > 0 && off >= wrap_bytes) {
            fseek(f, 0L, SEEK_SET);
            off = 0;
        }
        uclock_t t0 = uclock();
        unsigned long us;
        {
            /* Bytes written against bytes attempted, and fsync's return.
             * A short write on a full volume does not crash -- fwrite just
             * returns less, the loop runs happily, the arm completes in good
             * time and reports zero events. That is branch A's exact
             * signature produced by an arm that never wrote a byte. And an
             * fsync that fails costs nothing, which would flatten the very
             * distribution being sampled. Both are asserted, and a mismatch
             * voids the arm rather than reporting a plausible number. */
            size_t w = fwrite(rec, 1, (size_t)recsz, f);
            attempted += recsz;
            written += (long)w;
            if (w != (size_t)recsz) short_writes++;
            fflush(f);
            if (fsync(fileno(f)) != 0) sync_fails++;
        }
        us = elapsed_us(t0, uclock());
        off += recsz;
        n++;
        cum_us += (double)us;
        if (us < SWEEP_SPIKE_US) { quiet_us += (double)us; quiet_n++; }
        if (us > worst) { worst = us; worst_off = (unsigned long)off; }
        /* The first record is always printed, spike or not. fopen("wb")
         * creates a zero-length file with no clusters, so record 1 allocates
         * the FIRST cluster AND writes the starting-cluster field into the
         * directory entry; every later boundary crossing only extends the
         * chain. If first-allocation is dearer than extension, the
         * difference shows up right here and needs no separate arm. */
        if (n == 1) {
            printf("  FIRST rec=1     end_off=%-7ld us=%-8lu cum_ms=%.1f  "
                   "(first cluster + directory entry)\n", off, us, cum_us / 1000.0);
            fflush(stdout);
        }
        if (us >= SWEEP_SPIKE_US) {
            printf("  SPIKE rec=%-5d end_off=%-7ld us=%-8lu cum_ms=%.1f\n",
                   n, off, us, cum_us / 1000.0);
            fflush(stdout);
            spikes++;
        }
    }
    fclose(f);
    remove(g_sweep_path);
    printf("fsprobe: sweep done -- %d records, %ld device bytes, %d spikes, "
           "worst %lu us at off=%lu\n", n, off, spikes, worst, worst_off);
    printf("fsprobe: INTEGRITY attempted=%ld written=%ld short_writes=%d "
           "sync_fails=%d -> %s\n", attempted, written, short_writes,
           sync_fails,
           (attempted == written && short_writes == 0 && sync_fails == 0)
               ? "OK" : "ARM VOID");
    printf("fsprobe: free bytes on the sweep drive: start=%lu end=%lu\n",
           g_free_at_start, free_bytes_on(g_sweep_drive));
    printf("fsprobe: sweep elapsed %.1f ms by uclock, %.1f ms summed per-record; "
           "quiet records n=%d mean_us=%.1f\n",
           (double)elapsed_us(sweep_t0, uclock()) / 1000.0, cum_us / 1000.0,
           quiet_n, quiet_n ? quiet_us / quiet_n : 0.0);
    /* Deliberately NOT printing bytes/spikes. That division was in this
     * probe for four runs and we reasoned from it three times, and it fed an
     * argument that helped kill a hypothesis family before anyone knew the
     * detector was intermittent. Three runs of ONE configuration gave 7, 10
     * and 14 events -- so "one event per 56,228 bytes" was one
     * authoritative-looking number with a 2x-unreliable input dissolved into
     * it, carrying this instrument's credibility. events=N bytes=B invites
     * "is N all of them?"; a rate does not. Arithmetic belongs in the
     * analysis where it can be re-derived and audited, not in the probe
     * where it arrives pre-concluded. */
    printf("fsprobe: events=%d bytes=%ld "
           "(NO rate printed: detection is intermittent -- 7, 10 and 14 "
           "events across three runs of one configuration)\n", spikes, off);
    fflush(stdout);
    /* Free clusters again. If allocation cost scales with how full or how
     * fragmented the volume is, this is the quantity it scales with, and
     * reading it before and after costs one more INT 21h. */
    printf("fsprobe: volume after sweep:\n");
    report_cluster_size(g_sweep_drive);
}

/* FSPROBE_CAT=path[;path...] -- print files to stdout, which lands in the
 * already-fetched PRBOUT.TXT. Added to read C:\CONFIG.SYS and
 * C:\AUTOEXEC.BAT off the card before a boot-config change, because
 * vcctrl's file-list refuses the root of C: and the restore must be the
 * machine's own file rather than a reconstruction from a sibling repo --
 * which would be the same class of error as taking a figure from another
 * fixture. Read-only: it opens for reading and writes nothing. */
static void cat_files(const char *spec)
{
    char buf[256];
    char *tok;
    strncpy(buf, spec, sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = 0;
    for (tok = strtok(buf, ";"); tok; tok = strtok(NULL, ";")) {
        FILE *f = fopen(tok, "rb");
        int c, n = 0;
        printf("\n----- BEGIN %s -----\n", tok);
        if (!f) {
            printf("(cannot open)\n");
        } else {
            while ((c = fgetc(f)) != EOF) { putchar(c); n++; }
            fclose(f);
        }
        printf("\n----- END %s (%d bytes) -----\n", tok, n);
        fflush(stdout);
    }
}

/* FSPROBE_SYS_PRE / FSPROBE_SYS_MID -- semicolon-separated DOS commands run
 * via system(), before the sweep and between two sweeps. Added so a resident
 * that reconfigures at runtime can be A/B'd WITHIN ONE BOOT: both arms from
 * the same boot removes everything except the lever by construction, the
 * same reason a within-build A/B beats two binaries. No reboot, no
 * CONFIG.SYS edit, no restore to verify, no exposure to the post-FTP
 * keyboard hang. Output lands in the same PRBOUT.TXT, so a status command
 * run before and after is its own expect_log. */
static void run_cmds(const char *spec, const char *label)
{
    char buf[256];
    char *tok;
    if (!spec || !spec[0]) return;
    strncpy(buf, spec, sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = 0;
    for (tok = strtok(buf, ";"); tok; tok = strtok(NULL, ";")) {
        printf("\n===== %s: %s =====\n", label, tok);
        fflush(stdout);
        {
            int rc = system(tok);
            fflush(stdout);
            printf("===== %s rc=%d =====\n", label, rc);
            fflush(stdout);
        }
    }
}

int main(void)
{
    struct stat_acc raw, flush_a, sync_a, reopen;

    /* Before any clock read -- see the header. */
    resolve_sweep_path_from(NULL);
    printf("fsprobe: sweep path = %s\n", g_sweep_path);
    fflush(stdout);

    if (!getenv("TZ")) {
        setenv("TZ", "UTC0", 1);
        tzset();
    }

    report_cluster_size(g_sweep_drive);

    {
        const char *cat = getenv("FSPROBE_CAT");
        if (cat && cat[0]) { cat_files(cat); }
    }
    /* FSPROBE_ECHO -- print an env value back verbatim, with its length, so
     * the transit path's actual alphabet can be measured instead of guessed.
     * Two delimiters have been eaten at the same position with different
     * characters, while ';' at the same position survived, so neither a
     * length cut nor a whitespace split explains it -- and neither does the
     * "COMMAND.COM reads | as a pipe" story, which cannot account for '#'.
     * One mechanism has to explain both or neither is established. */
    {
        /* FSPROBE_E1..E12, each echoed verbatim with its length. Separate
         * variables because a delimited probe string cannot survive the very
         * mangling it is sent to detect -- if the layer eats a character, a
         * single string would be truncated at the first one and the rest of
         * the alphabet would go untested. One character per variable, plus a
         * plain control of the same length and a long plain control, so the
         * result distinguishes an alphabet from a length cut from a
         * whitespace split. */
        int k; char nm[16]; int any = 0;
        for (k = 1; k <= 16; k++) {
            const char *e;
            sprintf(nm, "FSPROBE_E%d", k);
            e = getenv(nm);
            if (e) {
                any = 1;
                printf("fsprobe: %-12s len=%3d [%s]\n", nm, (int)strlen(e), e);
            }
        }
        if (any) fflush(stdout);
        {
            const char *e = getenv("FSPROBE_ECHO");
            if (e) {
                printf("fsprobe: FSPROBE_ECHO len=%d [%s]\n", (int)strlen(e), e);
                fflush(stdout);
            }
        }
    }
    run_cmds(getenv("FSPROBE_SYS_PRE"), "PRE");

    printf("fsprobe: %d iterations per arm, line length %d bytes\n",
           ITERS, (int)strlen(LINE));
    printf("fsprobe: UCLOCKS_PER_SEC=%lu\n", (unsigned long)UCLOCKS_PER_SEC);
    fflush(stdout);

    acc_init(&raw);
    acc_init(&flush_a);
    acc_init(&sync_a);
    acc_init(&reopen);

    /* Arms, in the order FSPROBE_ORDER names (default raw,flush,sync,reopen
     * -- the order every run so far has used). */
    {
        const char *order = getenv("FSPROBE_ORDER");
        char buf[64];
        char *tok;
        if (!order || !order[0]) order = "raw,flush,sync,reopen";
        printf("fsprobe: arm order = %s\n", order);
        if (!strcmp(order, "none")) {
            printf("fsprobe: arms SKIPPED -- the sweep's fsync'd bytes are then\n");
            printf("fsprobe: the only bytes forced to the device in this run.\n");
            fflush(stdout);
            goto armsdone;
        }
        fflush(stdout);
        strncpy(buf, order, sizeof(buf) - 1);
        buf[sizeof(buf) - 1] = 0;
        for (tok = strtok(buf, ","); tok; tok = strtok(NULL, ",")) {
            if      (!strcmp(tok, "raw"))    { if (!arm_raw(&raw)) goto armfail; }
            else if (!strcmp(tok, "flush"))  { if (!arm_flush(&flush_a)) goto armfail; }
            else if (!strcmp(tok, "sync"))   { if (!arm_sync(&sync_a)) goto armfail; }
            else if (!strcmp(tok, "reopen")) { if (!arm_reopen(&reopen)) goto armfail; }
            else printf("fsprobe: unknown arm '%s' in FSPROBE_ORDER, skipped\n", tok);
        }
        goto armsdone;
armfail:
        printf("fsprobe: REFUSED -- cannot open %s\n", TMPNAME);
        return 1;
armsdone:
        ;
    }

    remove(TMPNAME);

    printf("\n");
    acc_print("raw", &raw);
    acc_print("flush", &flush_a);
    acc_print("sync", &sync_a);
    acc_print("reopen", &reopen);

    printf("\nfsprobe: fsync cost per call = mean_us(sync) - mean_us(flush) = %.1f us\n",
           (sync_a.n && flush_a.n)
               ? (sync_a.sum_us / sync_a.n) - (flush_a.sum_us / flush_a.n)
               : 0.0);
    printf("fsprobe: 240 such calls in a gate run = %.1f ms\n",
           (sync_a.n ? (sync_a.sum_us / sync_a.n) : 0.0) * 240.0 / 1000.0);
    /* FSPROBE_SEQ: '#'-separated stages, each a ';'-separated command list
     * run immediately before that stage's sweep. One sweep per stage.
     *
     * A-then-B is not enough here and abba-methodology.md opens with why.
     * Two of its reasons are unusually live for this phenomenon: the FIRST
     * write activity after boot is confounded with whichever arm runs first,
     * on a stall whose trigger is unknown and whose detection is
     * intermittent; and the device accumulates state in one direction only
     * -- wear levelling, cache occupancy, free-cluster position have each
     * been candidates in this investigation. A-B-B-A separates the lever
     * from both, and A-to-A agreement across the two A arms is the stability
     * check, read off the data rather than argued.
     *
     * The separator is '#' and NOT '|'. The first attempt used '|', which
     * COMMAND.COM reads as a pipe in the SET line the harness generates, so
     * the variable was silently truncated at the first stage. The run then
     * produced a complete, plausible-looking single-arm result -- the
     * flattering-direction failure again, in a new costume. '#' has no
     * meaning to COMMAND.COM; ';' inside a stage is already proven safe by
     * the status cell. */
    {
        /* FSPROBE_S1..FSPROBE_S8 -- one env var per stage, each a ';'-separated
         * command list. This replaces FSPROBE_SEQ's single delimited string.
         *
         * Two delimiters have now been eaten in transit: '|' by COMMAND.COM
         * as a pipe, and '#' by something in the chain that has not been
         * identified. Rather than audit a fourth parser and pick a fifth
         * delimiter, remove the delimiter: separate variables cannot be
         * truncated into each other, and a missing one is visible as a
         * missing one. FSPROBE_STAGES still asserts the count, so a variable
         * lost in transit refuses the run instead of shortening it. */
        {
            int want = 0, k;
            const char *w = getenv("FSPROBE_STAGES");
            char nm[16];
            if (w && w[0]) want = atoi(w);
            if (want > 0 && want <= 8) {
                int have = 0;
                for (k = 1; k <= 8; k++) {
                    sprintf(nm, "FSPROBE_S%d", k);
                    if (getenv(nm) && getenv(nm)[0]) have++;
                }
                printf("fsprobe: FSPROBE_STAGES=%d, found %d of FSPROBE_S1..S8\n",
                       want, have);
                if (have != want) {
                    printf("fsprobe: REFUSED -- %d stage variables expected, %d "
                           "present. Running nothing.\n", want, have);
                    for (k = 1; k <= 8; k++) {
                        sprintf(nm, "FSPROBE_S%d", k);
                        printf("fsprobe:   %s = [%s]\n", nm,
                               getenv(nm) ? getenv(nm) : "(unset)");
                    }
                    fflush(stdout);
                    return 2;
                }
                for (k = 1; k <= want; k++) {
                    char label[24], pnm[16];
                    /* FSPROBE_P<k>: per-stage sweep path, so the device can
                     * alternate WITHIN one boot. Without it the RAM-disk
                     * comparison would be between-boot, which is the confound
                     * every cell tonight was rebuilt to remove. */
                    sprintf(pnm, "FSPROBE_P%d", k);
                    resolve_sweep_path_from(getenv(pnm));
                    sprintf(nm, "FSPROBE_S%d", k);
                    sprintf(label, "STAGE%d", k);
                    printf("\nfsprobe: stage %d sweep path = %s\n", k, g_sweep_path);
                    fflush(stdout);
                    run_cmds(getenv(nm), label);
                    printf("\nfsprobe: ===== SWEEP %d (%s) =====\n", k, label);
                    fflush(stdout);
                    sweep();
                }
                goto seqdone;
            }
        }

        const char *seq = getenv("FSPROBE_SEQ");
        if (seq && seq[0]) {
            char buf[512];
            char *stage;
            int k = 0;
            /* FSPROBE_STAGES: what the CALLER intended. Changing the
             * separator fixed one bug; this fixes the class. The value
             * crosses four parsers -- host shell, transfer, DOS SET, C
             * getenv -- and only has to be mangled in one. A truncated list
             * and a genuinely short list produce identical output, so
             * nothing but an explicit expectation tells them apart, and the
             * '|' run proved that a quarter of an experiment reports itself
             * as a whole one with a zero exit. Count first, refuse on
             * mismatch, run nothing. */
            int want = 0;
            {
                const char *w = getenv("FSPROBE_STAGES");
                if (w && w[0]) want = atoi(w);
            }
            if (want > 0) {
                char cbuf[512];
                char *t;
                int have = 0;
                strncpy(cbuf, seq, sizeof(cbuf) - 1);
                cbuf[sizeof(cbuf) - 1] = 0;
                for (t = strtok(cbuf, "#"); t; t = strtok(NULL, "#")) have++;
                printf("fsprobe: FSPROBE_STAGES=%d, parsed %d stage(s)\n",
                       want, have);
                if (have != want) {
                    printf("fsprobe: REFUSED -- the stage list did not survive "
                           "the trip. Wanted %d, parsed %d. Running nothing.\n",
                           want, have);
                    printf("fsprobe: FSPROBE_SEQ as received: [%s]\n", seq);
                    fflush(stdout);
                    return 2;
                }
                fflush(stdout);
            }
            strncpy(buf, seq, sizeof(buf) - 1);
            buf[sizeof(buf) - 1] = 0;
            for (stage = strtok(buf, "#"); stage; stage = strtok(NULL, "#")) {
                char label[24];
                k++;
                sprintf(label, "STAGE%d", k);
                run_cmds(stage, label);
                printf("\nfsprobe: ===== SWEEP %d (%s) =====\n", k, label);
                fflush(stdout);
                sweep();
            }
        } else {
            sweep();
            {
                const char *mid = getenv("FSPROBE_SYS_MID");
                if (mid && mid[0]) {
                    run_cmds(mid, "MID");
                    printf("\nfsprobe: ===== SECOND SWEEP, arm B =====\n");
                    fflush(stdout);
                    sweep();
                }
            }
        }
    }

seqdone:
    printf("fsprobe: done\n");
    fflush(stdout);
    return 0;
}
