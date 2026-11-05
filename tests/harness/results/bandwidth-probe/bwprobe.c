/* bwprobe -- P2.0 of the 40/40 plan: how fast can THIS machine move a frame?
 *
 * Every present-path design in P2 rests on a bandwidth figure nobody has
 * measured on the 486DX2-66 + Mach64: the "~7 MB/s" in PLAN.md is what OUR
 * present path achieved, and doskutsu's 16 MB/s was a POD-83 through the
 * banked window. This times plain copies of the frame sizes that matter:
 *
 *    64,000  320x200x8   (a Mode 13h frame)
 *    76,800  320x240x8   (Trilby's Notes; doskutsu's frame)
 *   307,200  640x480x8   (today's 2x-scaled present)
 *   460,800  640x360x16  (AGS Quest's own rectangle)
 *   614,400  640x480x16  (AGS Quest's present today)
 *
 * by three routes -- a near-pointer write to the DPMI-mapped LFB (what
 * SDL_HINT_DOS_PREFER_LFB selects), dosmemput() through the 64 KB banked
 * window at A000h including its VBE 4F05h bank switches (what the backend's
 * direct path prefers by default), and Mode 13h's A000h -- with two copy
 * loops where that makes sense (`rep movsl`, and libc memcpy, which is what
 * the present path actually calls), and a system-RAM-to-system-RAM copy of
 * the same sizes as the CONTROL: what this CPU can move at all, with no bus
 * and no card in it.
 *
 * Build: i586-pc-msdosdjgpp-gcc -O2 -o bwprobe.exe bwprobe.c
 * Output goes to stdout -- redirect it; the screen is in a graphics mode and
 * full of test pattern while this runs. Text mode 3 is restored on exit.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <dpmi.h>
#include <go32.h>
#include <sys/nearptr.h>
#include <sys/movedata.h>

static unsigned char *src;
static const long SIZES[] = { 64000L, 76800L, 307200L, 460800L, 614400L };
#define NSIZES 5

static void copy_movsl(void *d, const void *s, long n)
{
    long d0, d1, d2;
    __asm__ __volatile__("cld\n\trep\n\tmovsl" : "=c" (d0), "=D" (d1), "=S" (d2)
            : "0" (n >> 2), "1" ((long)d), "2" ((long)s) : "memory", "cc");
}

/* WRITE-ONLY to system RAM. Added 2026-09-19.
 *
 * The CONTROL case above is read+write: every byte of payload costs a read
 * AND a write, so its MB/s is payload, not bus traffic. Several estimates
 * in the 40/40 campaign compared a one-sided loop against that two-sided
 * number and drew the wrong bound from it -- render_backbuffer's masked
 * blit reads every source pixel but writes only the ~60% that are not the
 * mask colour, so its traffic is asymmetric and neither the CONTROL figure
 * nor double it is the right ceiling.
 *
 * This measures the write half alone, so an asymmetric loop's floor can be
 * computed from measured reads and measured writes rather than inferred
 * from a symmetric figure. */
static void write_stosl(void *d, long n)
{
    long d0, d1;
    __asm__ __volatile__("cld\n\trep\n\tstosl" : "=c" (d0), "=D" (d1)
            : "0" (n >> 2), "1" ((long)d), "a" (0x5A5A5A5AL) : "memory", "cc");
}

static void report(const char *route, const char *loop, long bytes, long reps, uclock_t ticks)
{
    double ms = (double)ticks * 1000.0 / UCLOCKS_PER_SEC / (double)reps;
    printf("%-22s %-8s bytes=%6ld reps=%4ld ms_per_copy=%8.3f MB_per_s=%7.2f fps_ceiling=%6.1f\n",
           route, loop, bytes, reps, ms, (double)bytes / 1048576.0 / (ms / 1000.0), 1000.0 / ms);
}

/* Runs COPY until ~0.8 s have passed (at least 3 reps, at most 400). */
#define TIME_IT(ROUTE, LOOP, BYTES, COPY) do { \
    long reps_ = 0; uclock_t t0_ = uclock(), t1_; \
    do { COPY; reps_++; t1_ = uclock(); } \
    while ((reps_ < 3 || t1_ - t0_ < (uclock_t)UCLOCKS_PER_SEC * 8 / 10) && reps_ < 400); \
    report(ROUTE, LOOP, BYTES, reps_, t1_ - t0_); } while (0)

static int vbe_mode_info(int mode, unsigned long *phys, int *gran_kb, int *xres, int *yres, int *bpp)
{
    __dpmi_regs r;
    unsigned char info[256];
    memset(&r, 0, sizeof r);
    r.x.ax = 0x4F01; r.x.cx = mode;
    r.x.es = __tb >> 4; r.x.di = __tb & 0x0F;
    __dpmi_int(0x10, &r);
    if (r.x.ax != 0x004F) return 0;
    dosmemget(__tb, sizeof info, info);
    *gran_kb = info[4] | (info[5] << 8);
    *xres = info[0x12] | (info[0x13] << 8);
    *yres = info[0x14] | (info[0x15] << 8);
    *bpp = info[0x19];
    *phys = (unsigned long)info[0x28] | ((unsigned long)info[0x29] << 8) |
            ((unsigned long)info[0x2A] << 16) | ((unsigned long)info[0x2B] << 24);
    return 1;
}

static int vbe_set_mode(int mode_bx)
{
    __dpmi_regs r;
    memset(&r, 0, sizeof r);
    r.x.ax = 0x4F02; r.x.bx = mode_bx;
    __dpmi_int(0x10, &r);
    return r.x.ax == 0x004F;
}

static void vbe_set_bank(int pos)
{
    __dpmi_regs r;
    memset(&r, 0, sizeof r);
    r.x.ax = 0x4F05; r.x.bx = 0; r.x.dx = pos;
    __dpmi_int(0x10, &r);
}

static void bios_mode(int m)
{
    __dpmi_regs r;
    memset(&r, 0, sizeof r);
    r.x.ax = m;
    __dpmi_int(0x10, &r);
}

/* Whole-frame copy through the banked window: 64 KB at a time, one bank
   switch per chunk -- the switches are part of what this route costs. */
static void banked_put(long bytes, int gran_kb)
{
    long off = 0;
    int bank_step = gran_kb > 0 ? 64 / gran_kb : 1;
    int bank = 0;
    while (off < bytes)
    {
        long n = bytes - off > 65536L ? 65536L : bytes - off;
        vbe_set_bank(bank);
        dosmemput(src + off, n, 0xA0000);
        off += n;
        bank += bank_step;
    }
}

static void vesa_tests(int mode, const char *name, const long *sizes, int nsizes)
{
    unsigned long phys = 0; int gran = 0, x = 0, y = 0, bpp = 0, i;
    char route[40];
    if (!vbe_mode_info(mode, &phys, &gran, &x, &y, &bpp))
    {
        printf("mode 0x%03X (%s): VBE mode info call failed -- skipped\n", mode, name);
        return;
    }
    printf("mode 0x%03X %s: %dx%d bpp=%d physbase=0x%08lX win_gran=%dKB\n", mode, name, x, y, bpp, phys, gran);

    /* banked (no LFB bit) */
    if (vbe_set_mode(mode))
    {
        for (i = 0; i < nsizes; i++)
        {
            sprintf(route, "0x%03X banked A000+4F05", mode);
            TIME_IT(route, "dosmemput", sizes[i], banked_put(sizes[i], gran));
        }
    }
    else
        printf("mode 0x%03X: banked mode set failed\n", mode);

    /* LFB, near pointer */
    if (phys && vbe_set_mode(mode | 0x4000))
    {
        __dpmi_meminfo mi;
        mi.address = phys; mi.size = 0x200000UL;
        if (__dpmi_physical_address_mapping(&mi) == 0 && __djgpp_nearptr_enable())
        {
            unsigned char *lfb = (unsigned char *)(mi.address + __djgpp_conventional_base);
            for (i = 0; i < nsizes; i++)
            {
                sprintf(route, "0x%03X LFB nearptr", mode);
                TIME_IT(route, "movsl", sizes[i], copy_movsl(lfb, src, sizes[i]));
                TIME_IT(route, "memcpy", sizes[i], memcpy(lfb, src, sizes[i]));
            }
            /* Did those writes reach the card? Read the first 256 bytes back. */
            copy_movsl(lfb, src, sizes[0]);
            printf("verify 0x%03X LFB readback: %s\n", mode, memcmp(lfb, src, 256) == 0 ? "ok" : "MISMATCH");
            __djgpp_nearptr_disable();
            __dpmi_free_physical_address_mapping(&mi);
        }
        else
            printf("mode 0x%03X: LFB mapping / nearptr enable failed\n", mode);
    }
    else
        printf("mode 0x%03X: no LFB (physbase=0x%08lX) or LFB mode set failed\n", mode, phys);
}

int main(void)
{
    static const long S8[] = { 64000L, 76800L, 307200L };
    static const long S16[] = { 460800L, 614400L };
    static const long S512[] = { 64000L, 76800L, 196608L };
    unsigned char *dst;
    long i;

    setvbuf(stdout, NULL, _IONBF, 0);
    src = (unsigned char *)malloc(614400L);
    dst = (unsigned char *)malloc(614400L);
    if (!src || !dst) { printf("malloc failed\n"); return 1; }
    for (i = 0; i < 614400L; i++) src[i] = (unsigned char)((i * 7) ^ (i >> 9));
    memset(dst, 0, 614400L);
    uclock();
    printf("bwprobe UCLOCKS_PER_SEC=%ld\n", (long)UCLOCKS_PER_SEC);

    /* CONTROL: system RAM to system RAM. 614,400 B does not fit a 486's
       cache, so this is the machine's real memory-copy rate. */
    for (i = 0; i < NSIZES; i++)
    {
        TIME_IT("CONTROL sysram->sysram", "movsl", SIZES[i], copy_movsl(dst, src, SIZES[i]));
        TIME_IT("CONTROL sysram->sysram", "memcpy", SIZES[i], memcpy(dst, src, SIZES[i]));
    }

    /* WRITE-ONLY: the other half of the CONTROL, so an asymmetric loop can
       be costed from measured reads and measured writes. */
    for (i = 0; i < NSIZES; i++)
    {
        TIME_IT("WRITEONLY sysram", "stosl", SIZES[i], write_stosl(dst, SIZES[i]));
        TIME_IT("WRITEONLY sysram", "memset", SIZES[i], memset(dst, 0x5A, SIZES[i]));
    }

    /* The copy loop must actually copy -- under DOSBox-X a `rep movsl` is
       charged one cycle whatever its count, so its timings there mean
       nothing and only this line says the loop is right. */
    memset(dst, 0, 614400L);
    copy_movsl(dst, src, 614400L);
    printf("verify movsl sysram copy: %s\n", memcmp(dst, src, 614400L) == 0 ? "ok" : "MISMATCH");

    vesa_tests(0x101, "640x480x8", S8, 3);
    vesa_tests(0x111, "640x480x16", S16, 2);
    vesa_tests(0x1F3, "512x384x8 (UniVBE)", S512, 3);

    /* Mode 13h: 64,000 bytes to A000h, by dosmemput and by near pointer. */
    bios_mode(0x13);
    TIME_IT("mode13h A000", "dosmemput", 64000L, dosmemput(src, 64000L, 0xA0000));
    if (__djgpp_nearptr_enable())
    {
        unsigned char *vga = (unsigned char *)(0xA0000 + __djgpp_conventional_base);
        TIME_IT("mode13h A000 nearptr", "movsl", 64000L, copy_movsl(vga, src, 64000L));
        TIME_IT("mode13h A000 nearptr", "memcpy", 64000L, memcpy(vga, src, 64000L));
        __djgpp_nearptr_disable();
    }
    bios_mode(0x03);
    printf("done\n");
    return 0;
}
