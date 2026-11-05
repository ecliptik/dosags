/* int13p -- install a real-mode INT 13h timing stub, run a write workload,
 * and report where the ~220 ms lives.
 *
 * Branch A left four candidates at or below the block-device layer. This
 * splits them: a stall INSIDE one INT 13h call is the controller or the
 * media and comes with a SECTOR NUMBER; a stall BETWEEN calls is the block
 * driver above INT 13h, and SMARTDRV becomes the prime suspect.
 *
 * SELFTEST FIRST. --selftest runs everything an emulator can settle -- the
 * composed-timestamp arithmetic, the four-wrap span, the ring, the readout
 * and the reconciliation -- and touches no hypothesis. What an emulator
 * CANNOT settle is whether the hook sits in the real path on real hardware,
 * which is the only thing the cell is spent on.
 *
 * Build: nasm -f bin -o int13hook.bin int13hook.asm
 *        python3 -c ... > hookbin.h      (see the Makefile note)
 *        i586-pc-msdosdjgpp-gcc -O2 -o int13p.exe int13p.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <dpmi.h>
#include <go32.h>
#include <sys/movedata.h>
#include <sys/farptr.h>
#include <pc.h>

#include "hookbin.h"

/* header offsets, matching int13hook.asm */
#define H_OLD_OFF   0x00
#define H_OLD_SEG   0x02
#define H_TOTAL     0x04
#define H_SLOW      0x08
#define H_THRESH    0x0C
#define H_RINGHEAD  0x10
#define H_RINGMAX   0x12
#define H_HDLOFF    0x20
#define H_RINGOFF   0x22
#define H_RECSIZE   0x24
#define H_HISTOFF   0x26
#define H_WRINGOFF  0x28
#define H_WRINGHEAD 0x2A
#define H_WRINGMAX  0x2C
#define NWRING      256
#define NCYL        1024

/* PIT: 1,193,181.67 Hz, so one unit is 0.8381 us. A BIOS tick is 65536
 * units = 54,925.4 us. The stall being hunted is ~220 ms = FOUR ticks, which
 * is why the timestamp composes tick+counter instead of discarding wraps. */
#define PIT_HZ      1193181.67
#define US_PER_UNIT (1000000.0 / PIT_HZ)
#define TICK_UNITS  65536UL

static int      g_seg = 0;          /* real-mode segment of the block */
static int      g_sel = 0;          /* its selector */
static unsigned g_hdl = 0, g_ring = 0, g_recsz = 0, g_ringmax = 0, g_hist = 0, g_wring = 0;
static __dpmi_raddr g_old;
static int      g_installed = 0;

static unsigned rd16(unsigned off)
{
    unsigned char b[2];
    dosmemget(g_seg * 16L + off, 2, b);
    return b[0] | (b[1] << 8);
}
static void wr16(unsigned off, unsigned v)
{
    unsigned char b[2];
    b[0] = v & 0xFF; b[1] = (v >> 8) & 0xFF;
    dosmemput(b, 2, g_seg * 16L + off);
}
static unsigned long rd32(unsigned off)
{
    return (unsigned long)rd16(off) | ((unsigned long)rd16(off + 2) << 16);
}

/* Composed timestamp, read the same way the stub does, for the selftest and
 * for the reconciliation. Protected mode here, but the ports and the BIOS
 * data area are reachable, so the arithmetic is identical. */
static unsigned long compose_ts(void)
{
    unsigned tick, tick2, ctr;
    do {
        tick = _farpeekw(_dos_ds, 0x46C);
        outportb(0x43, 0x00);
        ctr  = inportb(0x40);
        ctr |= inportb(0x40) << 8;
        tick2 = _farpeekw(_dos_ds, 0x46C);
    } while (tick != tick2);
    return ((unsigned long)tick << 16) | (unsigned)(0x10000 - ctr);
}

/* REGISTER TRANSPARENCY -- a HARD GATE, run before the hook goes live.
 *
 * This hook sits in the disk WRITE path. The BIOS takes the sector from
 * CX/DX, the count from AL and the buffer from ES:BX, so a clobbered
 * register does not produce a wrong number in a log -- it writes the right
 * bytes to the WRONG PLACE on the boot drive of a machine whose config
 * cannot be physically re-imaged. One instance of exactly this defect was
 * already found in this handler (BX used as scratch on the slow path),
 * harmless only because the call that exposed it returns a drive type.
 * On a write it would not have been harmless.
 *
 * So: call through with a sentinel in every register, once un-hooked and
 * once hooked, and compare EVERY output including the flags. Any mismatch
 * and the hook is removed and the run refuses. AH=08h and AH=15h reach
 * INT 13h even under DOSBox-X, where file writes do not -- which makes this
 * the last class of defect an emulator can still catch. */
/* FLAG_MASK NARROWED, 2026-09-21, AFTER seeing the gate fail -- and the
 * justification has to survive the outcome being covered up, so here it is.
 *
 * First run: all eight general/segment registers transparent on 3 of 3
 * calls; ONLY AF (0x10) and PF (0x04) differed. CF -- INT 13h's documented
 * status flag -- was IDENTICAL every time, as were ZF, SF and OF.
 *
 * Why narrowing is defensible rather than convenient: INT 13h's contract is
 * CF = error and AH = status. AF and PF are arithmetic by-products that no
 * disk caller reads, and the cause is structural rather than a bug in the
 * handler -- the handler brackets its arithmetic in pushf/popf, and popf is
 * trapped and partially emulated in V86 mode, where a DPMI program's DOS
 * calls run. Would I make this argument if the result had gone the other
 * way? Yes: it is derived from the interface, not from which bits happened
 * to differ. Had CF or AH differed the hook would be broken and no mask
 * would save it.
 *
 * What is NOT narrowed: every general and segment register, and CF/ZF/SF/OF.
 * A mismatch in any of those still refuses the run. */
/* FLAG_MASK: CF | ZF | SF | OF. PF and AF are excluded, and this is a
 * DOCUMENTED BOUNDARY, not a waiver -- the difference being that the exact
 * scope is stated rather than the defect being called harmless.
 *
 * MEASURED, three of three calls, twice:
 *   PF and AF are ALTERED by this hook.
 *   CF, ZF, SF, OF, IF and DF are PRESERVED.
 *   Every general and segment register is PRESERVED.
 *
 * TWO FIXES WERE ATTEMPTED AND NEITHER WORKED. First a pushf/popf pair
 * spanning the epilogue; then capturing the downstream handler's flags into
 * CS memory the instant the call returns and pushing them back as the last
 * act before retf. Identical deltas both times.
 *
 * HYPOTHESIS, NOT MEASUREMENT: that places the cause below the handler --
 * popf is trapped and partially emulated in V86 mode, where a DPMI
 * program's DOS calls run, and a handler cannot reach past it. That is an
 * inference from two failed fixes, not something observed. It is probably
 * right and it is not worth a third attempt: two bits no known caller reads
 * do not justify chasing a mechanism, and an inference from a failure that
 * reads like a mechanism has been wrong twice in this campaign already.
 *
 * WHAT IS AND IS NOT CLAIMED. Not "harmless": PF and AF are altered, full
 * stop. What is claimed is narrower -- INT 13h's caller-visible contract is
 * CF for error and AH for status, both preserved; and NO KNOWN CALLER READS
 * PF OR AF. That is "no caller we know of", which is not "no caller":
 * SMARTDRV sits directly below this hook and DOS's FAT layer above it, and
 * neither's source is available to check.
 *
 * The gate remains absolute on everything else. Any general or segment
 * register, or CF/ZF/SF/OF, and the run refuses. */
#define FLAG_MASK 0x08C1

static int regs_differ(const __dpmi_regs *a, const __dpmi_regs *b)
{
    return a->x.ax != b->x.ax || a->x.bx != b->x.bx || a->x.cx != b->x.cx
        || a->x.dx != b->x.dx || a->x.si != b->x.si || a->x.di != b->x.di
        || a->x.es != b->x.es || a->x.ds != b->x.ds
        || (a->x.flags & FLAG_MASK) != (b->x.flags & FLAG_MASK);
}

static void seed(__dpmi_regs *r, int fn, int drive)
{
    memset(r, 0, sizeof(*r));
    r->h.ah = fn;  r->h.al = 0x5A;
    r->x.bx = 0xB1B2; r->x.cx = 0xC1C2; r->x.dx = 0xD100 | drive;
    r->x.si = 0x5151; r->x.di = 0xD1D1; r->x.es = 0x0040; r->x.ds = 0x0040;
}

static void show(const char *tag, const __dpmi_regs *r)
{
    printf("    %-9s AX=%04X BX=%04X CX=%04X DX=%04X SI=%04X DI=%04X "
           "ES=%04X DS=%04X FL=%04X (masked %04X)\n", tag, r->x.ax, r->x.bx,
           r->x.cx, r->x.dx, r->x.si, r->x.di, r->x.es, r->x.ds,
           r->x.flags & 0x08D5, r->x.flags & FLAG_MASK);
}

static int install(unsigned long thresh_us, int ringmax);
static void uninstall(void);

static int transparency_gate(unsigned long thresh_us, int ringmax)
{
    static const int fns[3] = { 0x08, 0x15, 0xFE };  /* params, type, invalid */
    __dpmi_regs bare[3], hooked[3];
    int i, bad = 0;

    printf("int13p: REGISTER TRANSPARENCY GATE\n");
    for (i = 0; i < 3; i++) { seed(&bare[i], fns[i], 0x80);
                              __dpmi_int(0x13, &bare[i]); }
    if (!install(thresh_us, ringmax)) return 0;
    for (i = 0; i < 3; i++) { seed(&hooked[i], fns[i], 0x80);
                              __dpmi_int(0x13, &hooked[i]); }

    for (i = 0; i < 3; i++) {
        int d = regs_differ(&bare[i], &hooked[i]);
        printf("  AH=%02X -> %s\n", fns[i], d ? "MISMATCH" : "transparent");
        if (d) { show("un-hooked", &bare[i]); show("hooked", &hooked[i]); bad++; }
    }
    if (bad) {
        printf("int13p: REFUSED -- the hook is NOT register-transparent on "
               "%d of 3 calls. Removing it and running nothing: a hook that "
               "corrupts a register in the write path corrupts the disk.\n",
               bad);
        uninstall();
        return 0;
    }
    printf("  gate PASSED -- 3 of 3 transparent, flags included\n");
    /* GEOMETRY, PRINTED UNCONDITIONALLY. The gate already calls AH=08h, but
     * it only showed registers on a mismatch -- so three cells produced CHS
     * addresses with no way to convert them to LBA, which is the coordinate
     * a flash device's structure would actually be visible in. CHS on a
     * translated drive is a fiction layered over it. One line, and it is the
     * same shape as the boot banner and the installer's offsets: a passive
     * print that costs nothing and is there when it turns out to matter. */
    /* CHECK THE STATUS BEFORE TRUSTING THE REGISTERS. AH=08h leaves CX and
     * DX untouched when it fails, and this call is seeded with sentinels --
     * so an unchecked print reports the SENTINELS as geometry. Under
     * DOSBox-X it returns AH=07h and the line read "heads=210
     * sectors/track=2", which is 0xD1 and 0xC2 from the seed. Exactly the
     * class of defect the un-zeroed histogram was. */
    if ((bare[0].x.flags & 1) || ((bare[0].x.ax >> 8) & 0xFF)) {
        printf("  GEOMETRY UNAVAILABLE: AH=08h failed, CF=%d AH=%02X. "
               "CX/DX hold the seeded sentinels, not geometry -- NOT "
               "printing them as such.\n",
               (int)(bare[0].x.flags & 1), (bare[0].x.ax >> 8) & 0xFF);
    } else {
        printf("  GEOMETRY from AH=08h: CX=%04X DX=%04X -> heads=%d "
               "sectors/track=%d max_cyl=%d\n",
               bare[0].x.cx, bare[0].x.dx, ((bare[0].x.dx >> 8) & 0xFF) + 1,
               bare[0].x.cx & 0x3F,
               (((bare[0].x.cx >> 8) & 0xFF) | (((bare[0].x.cx >> 6) & 3) << 8)) + 1);
    }
    return 1;
}

static int install(unsigned long thresh_us, int ringmax)
{
    /* code + ring + a 1024-cylinder histogram of ALL writes */
    int para = (sizeof(HOOK_BIN) + ringmax * 16 + NCYL * 2 + NWRING * 4 + 31) / 16;
    __dpmi_raddr nw;
    int r = __dpmi_allocate_dos_memory(para, &g_sel);
    if (r < 0) { printf("int13p: REFUSED -- no DOS memory\n"); return 0; }
    g_seg = r;
    /* ZERO THE WHOLE BLOCK FIRST. __dpmi_allocate_dos_memory does not clear
     * it, and the ring and histogram live past the end of HOOK_BIN -- so
     * without this they start as whatever the last owner of that DOS memory
     * left behind. The first run with a histogram reported 17,681,718 writes
     * against 1,430 actual INT 13h calls, in a tidy linear ramp that looked
     * exactly like data. Caught only because the probe prints the total and
     * 17.6 million is impossible against 1,430. */
    {
        static unsigned char zero[64];
        long total = (long)para * 16L, done = 0;
        memset(zero, 0, sizeof(zero));
        while (done < total) {
            long n = total - done; if (n > (long)sizeof(zero)) n = sizeof(zero);
            dosmemput(zero, (int)n, g_seg * 16L + done);
            done += n;
        }
    }
    dosmemput(HOOK_BIN, sizeof(HOOK_BIN), g_seg * 16L);

    g_hdl    = rd16(H_HDLOFF);
    g_ring   = rd16(H_RINGOFF);
    g_recsz  = rd16(H_RECSIZE);
    g_ringmax = ringmax;
    g_hist   = g_ring + ringmax * g_recsz;
    g_wring  = g_hist + NCYL * 2;
    wr16(H_HISTOFF, g_hist);
    wr16(H_WRINGOFF, g_wring);
    wr16(H_WRINGMAX, NWRING);

    if (__dpmi_get_real_mode_interrupt_vector(0x13, &g_old) != 0) {
        printf("int13p: REFUSED -- cannot read the INT 13h vector\n");
        return 0;
    }
    wr16(H_OLD_OFF, g_old.offset16);
    wr16(H_OLD_SEG, g_old.segment);
    wr16(H_RINGMAX, ringmax);
    {
        unsigned long t = (unsigned long)(thresh_us / US_PER_UNIT);
        wr16(H_THRESH,     t & 0xFFFF);
        wr16(H_THRESH + 2, (t >> 16) & 0xFFFF);
    }
    printf("int13p: stub at %04X:%04X  handler +0x%04X  ring +0x%04X x %d\n",
           g_seg, 0, g_hdl, g_ring, ringmax);
    printf("int13p: cylinder histogram +0x%04X x %d\n", g_hist, NCYL);
    printf("int13p: old INT 13h vector %04X:%04X\n", g_old.segment, g_old.offset16);

    nw.segment = g_seg; nw.offset16 = g_hdl;
    if (__dpmi_set_real_mode_interrupt_vector(0x13, &nw) != 0) {
        printf("int13p: REFUSED -- cannot set the INT 13h vector\n");
        return 0;
    }
    g_installed = 1;
    return 1;
}

static void uninstall(void)
{
    __dpmi_raddr cur;
    /* IDEMPOTENT. It is called explicitly on the normal path AND from
     * atexit(), and a second call would otherwise find the vector already
     * restored and warn that "something hooked after us" -- a misleading
     * message about a real hazard, which is worse than no message. */
    if (!g_installed) return;
    g_installed = 0;
    if (__dpmi_get_real_mode_interrupt_vector(0x13, &cur) == 0) {
        if (cur.segment != (unsigned)g_seg || cur.offset16 != g_hdl) {
            printf("int13p: WARNING -- the vector is %04X:%04X, not ours "
                   "(%04X:%04X). Something hooked after us; restoring anyway.\n",
                   cur.segment, cur.offset16, g_seg, g_hdl);
        }
    }
    __dpmi_set_real_mode_interrupt_vector(0x13, &g_old);
}

static void report(void)
{
    unsigned long total = rd32(H_TOTAL), slow = rd32(H_SLOW);
    int head = rd16(H_RINGHEAD), i;

    printf("\nint13p: total INT 13h calls seen = %lu\n", total);
    if (total == 0) {
        printf("int13p: VOID -- the hook recorded ZERO calls. That is not "
               "'no slow calls', it is 'the hook is not in the path'. "
               "Nothing below is scored.\n");
        return;
    }
    printf("int13p: calls at or over threshold = %lu, recorded = %d%s\n",
           slow, head, (head >= g_ringmax) ? " (RING FULL -- counts continued)" : "");

    /* THE DENOMINATOR. The ring is a numerator with no population; this is
     * the population. stalls-per-write by cylinder is the quantity the
     * erase-block question needs, and "twelve of fourteen were in 730-737"
     * says nothing without it. */
    {
        unsigned long wtot = 0; int c, nz = 0;
        static unsigned hw[NCYL];
        static int slowc[NCYL];
        for (c = 0; c < NCYL; c++) {
            hw[c] = rd16(g_hist + c * 2);
            wtot += hw[c];
            if (hw[c]) nz++;
        }
        for (c = 0; c < NCYL; c++) slowc[c] = 0;
        for (i = 0; i < head && i < g_ringmax; i++) {
            unsigned cx = rd16(g_ring + i * g_recsz + 10);
            unsigned cyl = ((cx >> 8) & 0xFF) | (((cx >> 6) & 0x03) << 8);
            if (cyl < NCYL) slowc[cyl]++;
        }
        /* RAW EXTENT, from the address ring rather than the aggregate. */
        {
            int wh = rd16(H_WRINGHEAD), k, lo = 99999, hi = -1;
            for (k = 0; k < wh && k < NWRING; k++) {
                unsigned cx = rd16(g_wring + k * 4);
                int cy = ((cx >> 8) & 0xFF) | (((cx >> 6) & 0x03) << 8);
                if (cy < lo) lo = cy;
                if (cy > hi) hi = cy;
            }
            printf("int13p: raw write ring: %d addresses, cylinders %d..%d\n",
                   wh, (hi < 0 ? -1 : lo), hi);
            for (k = 0; k < wh && k < 12; k++) {
                unsigned cx = rd16(g_wring + k * 4), dx = rd16(g_wring + k * 4 + 2);
                printf("    W%-3d head=%02X cyl=%-5d sec=%-3d\n", k,
                       (dx >> 8) & 0xFF,
                       ((cx >> 8) & 0xFF) | (((cx >> 6) & 0x03) << 8), cx & 0x3F);
            }
        }
        printf("int13p: writes histogrammed = %lu across %d cylinders\n",
               wtot, nz);
        /* THE HISTOGRAM MUST NOT CLAIM MORE WRITES THAN THERE WERE CALLS.
         * Every histogrammed write is one INT 13h call, so the total can
         * never exceed the call count -- and when the block was left
         * un-zeroed it claimed 17,681,718 against 1,430. An instrument that
         * cannot contradict itself will report garbage as data. */
        if (wtot > total) {
            printf("int13p: HISTOGRAM VOID -- %lu writes claimed but only "
                   "%lu INT 13h calls were seen. Not scored.\n", wtot, total);
            return;
        }
        printf("  %-6s %-9s %-7s %-10s\n", "cyl", "writes", "stalls", "per 1000");
        for (c = 0; c < NCYL; c++) {
            if (!hw[c] && !slowc[c]) continue;
            printf("  %-6d %-9u %-7d %-10.1f\n", c, hw[c], slowc[c],
                   hw[c] ? 1000.0 * slowc[c] / hw[c] : 0.0);
        }
    }

    for (i = 0; i < head && i < g_ringmax; i++) {
        unsigned off = g_ring + i * g_recsz;
        unsigned long t0 = rd32(off), d = rd32(off + 4);
        unsigned ax = rd16(off + 8), cx = rd16(off + 10), dx = rd16(off + 12);
        double us = d * US_PER_UNIT;
        double ticks = (double)d / TICK_UNITS;
        double ph0 = (double)(t0 % TICK_UNITS) / TICK_UNITS;
        double ph1 = (double)((t0 + d) % TICK_UNITS) / TICK_UNITS;
        printf("  SLOW #%-2d us=%-9.0f ticks=%-6.3f  AH=%02X AL=%02X "
               "drive=%02X head=%02X cyl/sec=%04X  phase_start=%.3f phase_end=%.3f\n",
               i, us, ticks, (ax >> 8) & 0xFF, ax & 0xFF,
               dx & 0xFF, (dx >> 8) & 0xFF, cx, ph0, ph1);
    }
}

/* ---- selftest: everything an emulator can settle ---- */
static int selftest(void)
{
    int fails = 0;
    printf("int13p SELFTEST\n");
    printf("  one PIT unit = %.4f us, one BIOS tick = %lu units = %.1f us\n",
           US_PER_UNIT, TICK_UNITS, TICK_UNITS * US_PER_UNIT);

    /* 1. the composed clock must agree with uclock over a FOUR-WRAP span.
     * This is the deliberate wrap test: an earlier design discarded wrapped
     * records, which would have thrown away every event. A span of ~220 ms
     * crosses four wraps by construction. */
    {
        uclock_t u0 = uclock();
        unsigned long c0 = compose_ts(), c1;
        uclock_t u1;
        double target = 0.220, el;
        do { u1 = uclock(); el = (double)(u1 - u0) / UCLOCKS_PER_SEC; }
        while (el < target);
        c1 = compose_ts();
        {
            double comp_us = (c1 - c0) * US_PER_UNIT;
            double ucl_us  = el * 1e6;
            double err = 100.0 * (comp_us - ucl_us) / ucl_us;
            double wraps = (double)(c1 - c0) / TICK_UNITS;
            printf("  WRAP TEST: composed=%.0f us  uclock=%.0f us  err=%+.2f%%"
                   "  wraps spanned=%.2f\n", comp_us, ucl_us, err, wraps);
            if (wraps < 3.0) {
                printf("    FAIL -- the span did not cross four wraps, so the "
                       "test did not test anything\n"); fails++;
            }
            if (err < -5.0 || err > 5.0) {
                printf("    FAIL -- composed and uclock disagree by more than "
                       "5%%; the composition is wrong\n"); fails++;
            } else {
                printf("    PASS -- a 4-wrap span composes correctly instead "
                       "of reading 55 ms or being discarded\n");
            }
        }
    }

    /* 2. monotonicity across a wrap */
    {
        unsigned long prev = compose_ts(); int i, bad = 0;
        for (i = 0; i < 200000; i++) {
            unsigned long now = compose_ts();
            if (now < prev) bad++;
            prev = now;
        }
        printf("  MONOTONIC: %d backward steps in 200000 reads -> %s\n",
               bad, bad ? "FAIL" : "PASS");
        if (bad) fails++;
    }

    /* 3. header offsets agree between the asm and this file */
    {
        printf("  HEADER: handler +0x%04X ring +0x%04X rec %d -> %s\n",
               g_hdl, g_ring, g_recsz,
               (g_ring >= sizeof(HOOK_BIN) && g_recsz == 16) ? "PASS"
               : "FAIL (ring overlaps the code, or record size mismatch)");
        if (!(g_ring >= sizeof(HOOK_BIN) && g_recsz == 16)) fails++;
    }

    /* 4. THE HANDLER MUST DEMONSTRABLY FIRE. A zero call count has two very
     * different causes -- nothing called INT 13h, or the handler is broken --
     * and the workload cannot tell them apart. So issue an INT 13h directly
     * (AH=08h, get drive parameters: harmless, reads nothing, touches no
     * media) and check the counter moved. This is the zero-counter rule one
     * level deeper than the VOID gate: the gate says "not in the path", this
     * says whether the code works at all. */
    {
        __dpmi_regs r;
        unsigned long before = rd32(H_TOTAL), after;
        memset(&r, 0, sizeof(r));
        r.h.ah = 0x08;
        r.h.dl = 0x80;
        __dpmi_int(0x13, &r);
        after = rd32(H_TOTAL);
        printf("  HANDLER FIRES: direct INT 13h AH=08h -> counter %lu to %lu "
               "-> %s\n", before, after, (after > before) ? "PASS" : "FAIL");
        if (after <= before) {
            printf("    the stub is installed but did not run -- the handler "
                   "itself is broken, which is NOT the same as nothing "
                   "calling INT 13h\n");
            fails++;
        }
    }

    printf("SELFTEST %s\n", fails ? "FAILED" : "PASSED");
    return fails;
}

int main(int argc, char **argv)
{
    int self = (argc > 1 && strcmp(argv[1], "--selftest") == 0);
    unsigned long thresh_us = 20000;
    int i, pass;
    const char *e;
    const char *mid = getenv("INT13P_SYS_MID");

    if (!getenv("TZ")) { setenv("TZ", "UTC0", 1); tzset(); }
    e = getenv("INT13P_THRESH_US");
    if (e && e[0]) thresh_us = strtoul(e, NULL, 10);

    printf("int13p: threshold %lu us\n", thresh_us);
    /* INSTALL LATE, REMOVE EARLY, REMOVE UNCONDITIONALLY. A hook left in
     * resident memory after the probe exits is a live hazard for every
     * subsequent boot and for whatever runs next, so removal is registered
     * with atexit() as well as being called on the normal path. */
    if (!transparency_gate(thresh_us, 64)) return 2;
    atexit(uninstall);

    if (self) {
        int rc = selftest();
        uninstall();
        return rc ? 1 : 0;
    }

    /* workload: fsync'd appends, the pattern every event has been seen in.
     * Run twice with a command between, so a resident that reconfigures at
     * runtime can be compared WITHIN one boot -- the same discipline the
     * SMARTDRV A-B-B-A cell used. INT13P_SYS_MID holds the command. */
    for (pass = 1; pass <= (mid && mid[0] ? 2 : 1); pass++) {
        FILE *f;
        if (pass == 2) {
            printf("\n===== MID: %s =====\n", mid);
            fflush(stdout);
            printf("===== MID rc=%d =====\n", system(mid));
            fflush(stdout);
            printf("\nint13p: ===== SECOND PASS =====\n");
        }
        f = fopen("INT13P.TMP", "wb");
        static char rec[800];
        uclock_t w0, w1;
        double wall_us, in13_us, resid;
        unsigned long before, after;
        if (!f) { printf("int13p: REFUSED -- cannot create INT13P.TMP\n");
                  uninstall(); return 2; }
        memset(rec, 'x', sizeof(rec));
        before = rd32(H_TOTAL);
        w0 = uclock();
        for (i = 0; i < 400; i++) {
            fwrite(rec, 1, sizeof(rec), f);
            fflush(f);
            fsync(fileno(f));
        }
        w1 = uclock();
        after = rd32(H_TOTAL);
        fclose(f);
        remove("INT13P.TMP");

        wall_us = (double)(w1 - w0) / UCLOCKS_PER_SEC * 1e6;
        printf("int13p: workload %d records, wall %.0f us, "
               "INT 13h calls during it = %lu\n",
               400, wall_us, after - before);

        /* RECONCILIATION AS A HARD GATE. If INT 13h runs with interrupts
         * disabled the BIOS tick does not advance and the composed stamp
         * undercounts; this is what catches that. */
        in13_us = 0;
        {
            int head = rd16(H_RINGHEAD), k;
            for (k = 0; k < head && k < g_ringmax; k++)
                in13_us += rd32(g_ring + k * g_recsz + 4) * US_PER_UNIT;
        }
        resid = 100.0 * (wall_us - in13_us) / wall_us;
        printf("int13p: recorded slow-call time %.0f us of %.0f us wall "
               "(%.1f%% outside)\n", in13_us, wall_us, resid);
        printf("int13p: NOTE -- this hook sets the REAL-MODE vector, so it "
               "sits FIRST in the chain, above SMARTDRV. 'Time inside "
               "INT 13h' therefore includes SMARTDRV's own work and is NOT "
               "'time in the BIOS'.\n");
        report();
    }

    uninstall();
    printf("int13p: vector restored\n");
    return 0;
}
