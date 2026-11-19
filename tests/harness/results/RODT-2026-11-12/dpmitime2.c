/* dpmitime.c -- LAB TOOL (standalone DJGPP exe, not a patch): what one bare DPMI allocation of N pages costs the
 * machine, and whether that cost is time with IRQ0 not serviced (round RM follow-up; sdlports' discriminator 1).
 *
 * For each block size (pages of 4 KB; default 32 192 512 992) and repetition, four phases, each run alone between two
 * CMOS RTC second edges:
 *   null   nothing (the method's own error)
 *   alloc  DPMI 0501h, N*4096 bytes (what DJGPP's NONMOVE sbrk does for a new heap block)
 *   touch  write one byte to every page of that block (first touch; commits the pages if the host commits lazily)
 *   free   DPMI 0502h
 * Per phase it prints:
 *   call_ms     uclock() across the call alone (blind to lost IRQ0 ticks, like the engine's own clock)
 *   rtc_ms      the RTC time between the two edges (whole seconds; the RTC runs whatever the CPU does)
 *   uclock_ms   uclock() between the same two edges
 *   lost_ms     rtc_ms - uclock_ms: time during which IRQ0 was not serviced (each lost BIOS tick = 54.9 ms)
 *   bios_ticks  BIOS tick count (0040:006C) across the edges, against rtc_ms / 54.925 expected
 *   free        DPMI 0500h free physical pages after the phase (eager vs lazy commit)
 * The RTC is read through ports 70h / 71h (update-in-progress wait; BCD or binary per register 0Bh).
 *
 * VERSION 2 (after round RN's RNDT): on the Gateway 486 the RTC reads were garbage. The rig's timer-tick path (IRQ0,
 * reflected to the real-mode BIOS) leaves port 70h's index on register 0 (seconds): a minutes / hours read that
 * straddled an IRQ0 returned the seconds value, so edges fired on BIOS ticks (windows of k x 54.9 ms) and rtc_ms came
 * out as whole hours / minutes. v2:
 *   - interrupts off around every 70h / 71h pair (DJGPP disable() / enable(); port 70h is shared, as SDL's 0260 says);
 *   - a time is taken only when two consecutive full reads (UIP clear, seconds / minutes / hours) agree;
 *   - each line carries rtc_ok=1 only when rtc_ms is 1000..60000 and the window's uclock is within 25% of it;
 *   - -b K: before the phases, allocate and touch a ballast of K pages (kept to the end; timed on its own line), so
 *     the per-page cost can be read against pages already committed;
 *   - -X: lab only, inject the rig's failure (index set to 0 between a read's index write and its data read, once
 *     every 7 rtc_sec calls) to show the guard rejects it.
 * Usage: DPMITIME [pages ...] [-n REPS] [-b BALLAST_PAGES] [-X]      e.g. DPMITIME 992 -n 3 -b 4096
 * Output: plain text on stdout, one "DPMITIME ..." line per phase plus a header; redirect to a file on the rig.
 * Exit 0 when every phase ran; 2 when an allocation failed (the line says which).
 */
#include <dos.h>
#include <dpmi.h>
#include <go32.h>
#include <pc.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/farptr.h>
#include <time.h>

static int rtc_binary = 0;

static int inject = 0;
static unsigned long inject_n = 0, rtc_retries = 0;

static int rtc_reg_raw(int reg, int clobber)
{
    int v;
    disable();
    outportb(0x70, reg);
    if (clobber)
        outportb(0x70, 0x00);   /* -X: what the rig's IRQ0 path did between our index write and data read */
    v = inportb(0x71);
    enable();
    return v;
}

static int rtc_reg(int reg)
{
    return rtc_reg_raw(reg, 0);
}

static int rtc_val(int v)
{
    return rtc_binary ? v : ((v >> 4) * 10 + (v & 15));
}

/* one full read: seconds of the day, outside an update cycle */
static long rtc_once(void)
{
    int s, m, h, clob = 0;
    if (inject && (++inject_n % 7) == 0)
        clob = 1;
    while (rtc_reg(0x0A) & 0x80)
        ;
    s = rtc_val(rtc_reg(0x00));
    m = rtc_val(rtc_reg_raw(0x02, clob));
    h = rtc_val(rtc_reg(0x04) & 0x7F);
    return h * 3600L + m * 60L + s;
}

/* seconds of the day: two consecutive full reads that agree */
static long rtc_sec(void)
{
    long a = rtc_once(), b;
    for (;;)
    {
        b = rtc_once();
        if (a == b)
            return a;
        rtc_retries++;
        a = b;
    }
}

typedef struct
{
    long rtc;          /* RTC seconds of day at the edge */
    uclock_t u;        /* uclock() right after the edge */
    unsigned long bt;  /* BIOS tick count right after the edge */
} Edge;

/* wait for the next RTC second change; record uclock and BIOS ticks at it */
static void edge(Edge *e)
{
    long a = rtc_sec(), b;
    do
        b = rtc_sec();
    while (b == a);
    e->u = uclock();
    e->bt = _farpeekl(_dos_ds, 0x46C);
    e->rtc = b;
}

static unsigned long free_pages(void)
{
    __dpmi_free_mem_info fi;
    if (__dpmi_get_free_memory_information(&fi) != 0)
        return 0xFFFFFFFFUL;
    return fi.total_number_of_free_pages;
}

static void report(const char *phase, int pages, int rep, const Edge *a, const Edge *b, uclock_t call, int ok)
{
    long ds = b->rtc - a->rtc;
    double rtc_ms, uc_ms;
    if (ds < 0)
        ds += 86400L;
    rtc_ms = ds * 1000.0;
    uc_ms = (double)(b->u - a->u) * 1000.0 / UCLOCKS_PER_SEC;
    printf("DPMITIME phase=%s pages=%d rep=%d ok=%d call_ms=%.1f rtc_ms=%.0f uclock_ms=%.1f lost_ms=%.1f "
           "bios_ticks=%lu expect_ticks=%.1f free=%lu rtc_ok=%d\n",
           phase, pages, rep, ok, (double)call * 1000.0 / UCLOCKS_PER_SEC, rtc_ms, uc_ms, rtc_ms - uc_ms,
           b->bt - a->bt, rtc_ms / 54.9254, free_pages(),
           (rtc_ms >= 1000.0 && rtc_ms <= 60000.0 && uc_ms >= 0.75 * rtc_ms && uc_ms <= 1.25 * rtc_ms) ? 1 : 0);
    fflush(stdout);
}

int main(int argc, char **argv)
{
    int sizes[32], nsizes = 0, reps = 3, i, r, rc = 0, ballast = 0;
    __dpmi_version_ret v;

    for (i = 1; i < argc; i++)
    {
        if (!strcmp(argv[i], "-n") && i + 1 < argc)
            reps = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-b") && i + 1 < argc)
            ballast = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-X"))
            inject = 1;
        else if (nsizes < 32 && atoi(argv[i]) > 0)
            sizes[nsizes++] = atoi(argv[i]);
    }
    if (nsizes == 0)
    {
        sizes[0] = 32; sizes[1] = 192; sizes[2] = 512; sizes[3] = 992;
        nsizes = 4;
    }
    if (reps < 1)
        reps = 1;
    rtc_binary = (rtc_reg(0x0B) & 0x04) != 0;
    (void)uclock();   /* DJGPP: the first call reprograms the PIT; do it before any measurement */
    __dpmi_get_version(&v);
    printf("DPMITIME v2 host dpmi=%d.%02d flags=0x%x (bit2 virtual memory=%d) rtc_binary=%d rtc_b=0x%02x free=%lu reps=%d "
           "ballast=%d inject=%d\n", v.major, v.minor, v.flags, (v.flags >> 2) & 1, rtc_binary, rtc_reg(0x0B), free_pages(),
           reps, ballast, inject);
    fflush(stdout);
    if (ballast > 0)
    {
        Edge a, b;
        uclock_t t0, t1;
        __dpmi_meminfo bm;
        int bsel, ok;
        unsigned long p;
        memset(&bm, 0, sizeof bm);
        bm.size = (unsigned long)ballast * 4096UL;
        edge(&a); t0 = uclock();
        ok = __dpmi_allocate_memory(&bm) == 0;
        bsel = ok ? __dpmi_allocate_ldt_descriptors(1) : -1;
        ok = ok && bsel >= 0 && __dpmi_set_segment_base_address(bsel, bm.address) == 0 &&
             __dpmi_set_segment_limit(bsel, bm.size - 1) == 0;
        if (ok)
            for (p = 0; p < (unsigned long)ballast; p++)
                _farpokeb(bsel, p * 4096UL, (unsigned char)p);
        t1 = uclock(); edge(&b);
        report("ballast", ballast, 0, &a, &b, t1 - t0, ok);   /* kept (never freed) until exit */
        if (!ok)
        {
            printf("DPMITIME FAIL ballast pages=%d\n", ballast);
            return 2;
        }
    }

    for (i = 0; i < nsizes; i++)
    {
        for (r = 1; r <= reps; r++)
        {
            Edge a, b;
            uclock_t t0, t1;
            __dpmi_meminfo mi;
            int sel = -1, ok;
            unsigned long p;
            const int n = sizes[i];

            edge(&a); t0 = uclock(); t1 = uclock(); edge(&b);
            report("null", n, r, &a, &b, t1 - t0, 1);

            memset(&mi, 0, sizeof mi);
            mi.size = (unsigned long)n * 4096UL;
            edge(&a); t0 = uclock();
            ok = __dpmi_allocate_memory(&mi) == 0;
            t1 = uclock(); edge(&b);
            report("alloc", n, r, &a, &b, t1 - t0, ok);
            if (!ok)
            {
                printf("DPMITIME FAIL 0501h pages=%d\n", n);
                rc = 2;
                continue;
            }

            sel = __dpmi_allocate_ldt_descriptors(1);
            ok = sel >= 0 && __dpmi_set_segment_base_address(sel, mi.address) == 0 &&
                 __dpmi_set_segment_limit(sel, mi.size - 1) == 0;
            edge(&a); t0 = uclock();
            if (ok)
                for (p = 0; p < (unsigned long)n; p++)
                    _farpokeb(sel, p * 4096UL, (unsigned char)p);
            t1 = uclock(); edge(&b);
            report("touch", n, r, &a, &b, t1 - t0, ok);
            if (sel >= 0)
                __dpmi_free_ldt_descriptor(sel);

            edge(&a); t0 = uclock();
            ok = __dpmi_free_memory(mi.handle) == 0;
            t1 = uclock(); edge(&b);
            report("free", n, r, &a, &b, t1 - t0, ok);
        }
    }
    printf("DPMITIME done rc=%d rtc_retries=%lu\n", rc, rtc_retries);
    return rc;
}
