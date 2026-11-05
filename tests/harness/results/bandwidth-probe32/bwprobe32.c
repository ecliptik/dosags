/* bwprobe32 -- how fast can the 486 + Mach64 write a 32-bit frame?
 *
 * Lab worker dosags-lab-metric, Gate S32 (LAB-S32.md). Derived from
 * ../bandwidth-probe/bwprobe.c (P2.0, 2026-09-17), which measured the LFB at
 * 640x480x8 (0x101) and 640x480x16 (0x111) only: 27.3 MB/s. No 32-bit mode was
 * ever measured, and AGS Quest forced-32 (S2Q1) pushes its dirty rects at an
 * EFFECTIVE 8.3 MB/s against 22.7 MB/s for the same demo, same rect geometry,
 * at 16-bit (AQF1). This probe says whether that is the card at 32 bpp or our
 * software.
 *
 * What it times, each at 640x480x16 (anchor: must reproduce 2026-09-17) and at
 * every 640x480 mode the BIOS lists with bpp 32 (and 24, reported, if listed):
 *   - whole blocks by LFB near pointer (rep movsl and libc memcpy) and through
 *     the banked A000h window with its 4F05h switches:
 *       460,800 B  (640x360x16, AGS Quest's rectangle at 16-bit)
 *       614,400 B  (640x480x16)
 *       921,600 B  (640x360x32, AGS Quest's rectangle at 32-bit)
 *     1,228,800 B  (640x480x32)
 *   - RECT-SHAPED pushes, one memcpy per row at the mode's own pitch, the way
 *     SDL's DOSVESA_UpdateWindowFramebuffer pushes a dirty rect:
 *       W px x H rows for W in {32, 64, 160, 320, 640}, H chosen so a rect is
 *       about 10 KB at 32 bpp (S2Q1's mean rect: 46.6 KB per present over 4.75
 *       rects), the same px geometry at 16 bpp.
 *   - WRITE-ONLY to the LFB (rep stosl, no source read), 1,228,800 B at 32 bpp:
 *     separates the card's write rate from the RAM read of the source.
 *
 * Build: i586-pc-msdosdjgpp-gcc -O2 -o bwprb32.exe bwprobe32.c
 * Output to stdout -- redirect it (BWPRB32 > PRBOUT32.TXT; 8.3 name); the screen shows
 * test pattern while it runs. Text mode 3 is restored on exit.
 * Under DOSBox-X its TIMES mean nothing (a rep movsl is charged one cycle);
 * there only the mode list, the verify lines and "done" are checked.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <dpmi.h>
#include <go32.h>
#include <sys/nearptr.h>
#include <sys/movedata.h>

#define SRC_BYTES 1228800L
static unsigned char *src;

static void copy_movsl(void *d, const void *s, long n)
{
    long d0, d1, d2;
    __asm__ __volatile__("cld\n\trep\n\tmovsl" : "=c" (d0), "=D" (d1), "=S" (d2)
            : "0" (n >> 2), "1" ((long)d), "2" ((long)s) : "memory", "cc");
}

static void write_stosl(void *d, long n)
{
    long d0, d1;
    __asm__ __volatile__("cld\n\trep\n\tstosl" : "=c" (d0), "=D" (d1)
            : "0" (n >> 2), "1" ((long)d), "a" (0x5A5A5A5AL) : "memory", "cc");
}

static void report(const char *route, const char *loop, long bytes, long reps, uclock_t ticks)
{
    double ms = (double)ticks * 1000.0 / UCLOCKS_PER_SEC / (double)reps;
    printf("%-30s %-10s bytes=%7ld reps=%4ld ms_per_copy=%8.3f MB_per_s=%7.2f\n",
           route, loop, bytes, reps, ms, (double)bytes / 1048576.0 / (ms / 1000.0));
}

/* Runs COPY until ~0.8 s have passed (at least 3 reps, at most 400). */
#define TIME_IT(ROUTE, LOOP, BYTES, COPY) do { \
    long reps_ = 0; uclock_t t0_ = uclock(), t1_; \
    do { COPY; reps_++; t1_ = uclock(); } \
    while ((reps_ < 3 || t1_ - t0_ < (uclock_t)UCLOCKS_PER_SEC * 8 / 10) && reps_ < 400); \
    report(ROUTE, LOOP, BYTES, reps_, t1_ - t0_); } while (0)

typedef struct { int mode, x, y, bpp, gran_kb, pitch; unsigned long phys; } modeinfo;

static int vbe_mode_info(int mode, modeinfo *mi)
{
    __dpmi_regs r;
    unsigned char info[256];
    memset(&r, 0, sizeof r);
    r.x.ax = 0x4F01; r.x.cx = mode;
    r.x.es = __tb >> 4; r.x.di = __tb & 0x0F;
    __dpmi_int(0x10, &r);
    if (r.x.ax != 0x004F) return 0;
    dosmemget(__tb, sizeof info, info);
    mi->mode = mode;
    mi->gran_kb = info[4] | (info[5] << 8);
    mi->pitch = info[0x10] | (info[0x11] << 8);
    mi->x = info[0x12] | (info[0x13] << 8);
    mi->y = info[0x14] | (info[0x15] << 8);
    mi->bpp = info[0x19];
    mi->phys = (unsigned long)info[0x28] | ((unsigned long)info[0x29] << 8) |
               ((unsigned long)info[0x2A] << 16) | ((unsigned long)info[0x2B] << 24);
    return 1;
}

/* The BIOS's own mode list (4F00h), so the 32-bit mode number is read, not
   guessed: UniVBE and the card's BIOS number 32-bit modes differently. */
static int vbe_mode_list(int *out, int max)
{
    __dpmi_regs r;
    unsigned char info[512];
    unsigned long seg, off, lin;
    int n = 0;
    memset(&r, 0, sizeof r);
    memset(info, 0, sizeof info);
    memcpy(info, "VBE2", 4);
    dosmemput(info, sizeof info, __tb);
    r.x.ax = 0x4F00; r.x.es = __tb >> 4; r.x.di = __tb & 0x0F;
    __dpmi_int(0x10, &r);
    if (r.x.ax != 0x004F) return 0;
    dosmemget(__tb, sizeof info, info);
    printf("VBE %d.%d, %d KB video memory\n", info[5], info[4], (info[0x12] | (info[0x13] << 8)) * 64);
    off = info[0x0E] | (info[0x0F] << 8);
    seg = info[0x10] | (info[0x11] << 8);
    lin = seg * 16 + off;
    while (n < max)
    {
        unsigned short m;
        dosmemget(lin + 2 * n, 2, &m);
        if (m == 0xFFFF) break;
        out[n++] = m;
    }
    return n;
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

/* One memcpy per row at the destination pitch, as the SDL present does. */
static void rect_put(unsigned char *lfb, int pitch, int row_bytes, int rows)
{
    int y;
    const unsigned char *s = src;
    unsigned char *d = lfb + 8 * pitch + 64;
    for (y = 0; y < rows; y++)
    {
        memcpy(d, s, row_bytes);
        s += row_bytes;
        d += pitch;
    }
}

static void mode_tests(const modeinfo *mi)
{
    static const long BLOCKS[] = { 460800L, 614400L, 921600L, 1228800L };
    static const int RECT_W[] = { 32, 64, 160, 320, 640 };
    const int bytespp = (mi->bpp + 7) / 8;
    const long frame = (long)mi->pitch * mi->y;
    char route[48];
    int i;

    printf("mode 0x%03X: %dx%d bpp=%d pitch=%d physbase=0x%08lX win_gran=%dKB frame=%ld\n",
           mi->mode, mi->x, mi->y, mi->bpp, mi->pitch, mi->phys, mi->gran_kb, frame);

    if (vbe_set_mode(mi->mode))
    {
        for (i = 0; i < 4; i++)
        {
            if (BLOCKS[i] > frame) continue;
            sprintf(route, "0x%03X/%d banked A000+4F05", mi->mode, mi->bpp);
            TIME_IT(route, "dosmemput", BLOCKS[i], banked_put(BLOCKS[i], mi->gran_kb));
        }
    }
    else
        printf("mode 0x%03X: banked mode set failed\n", mi->mode);

    if (mi->phys && vbe_set_mode(mi->mode | 0x4000))
    {
        __dpmi_meminfo m;
        m.address = mi->phys; m.size = 0x200000UL;
        if (__dpmi_physical_address_mapping(&m) == 0 && __djgpp_nearptr_enable())
        {
            unsigned char *lfb = (unsigned char *)(m.address + __djgpp_conventional_base);
            for (i = 0; i < 4; i++)
            {
                if (BLOCKS[i] > frame) continue;
                sprintf(route, "0x%03X/%d LFB nearptr", mi->mode, mi->bpp);
                TIME_IT(route, "movsl", BLOCKS[i], copy_movsl(lfb, src, BLOCKS[i]));
                TIME_IT(route, "memcpy", BLOCKS[i], memcpy(lfb, src, BLOCKS[i]));
            }
            if (frame >= 1228800L)
            {
                sprintf(route, "0x%03X/%d LFB write-only", mi->mode, mi->bpp);
                TIME_IT(route, "stosl", 1228800L, write_stosl(lfb, 1228800L));
            }
            else
            {
                sprintf(route, "0x%03X/%d LFB write-only", mi->mode, mi->bpp);
                TIME_IT(route, "stosl", 614400L, write_stosl(lfb, 614400L));
            }
            /* Rect-shaped: W px wide, rows so that a rect is ~10 KB at 4 B/px;
               the same px geometry at every depth. */
            for (i = 0; i < 5; i++)
            {
                int w = RECT_W[i];
                int rows = 10240 / (w * 4);
                long bytes;
                char loop[16];
                if (rows < 1) rows = 1;
                if (rows > mi->y - 16) rows = mi->y - 16;
                bytes = (long)w * bytespp * rows;
                sprintf(route, "0x%03X/%d LFB rect", mi->mode, mi->bpp);
                sprintf(loop, "w%dxh%d", w, rows);
                TIME_IT(route, loop, bytes, rect_put(lfb, mi->pitch, w * bytespp, rows));
            }
            copy_movsl(lfb, src, 4096);
            printf("verify 0x%03X LFB readback: %s\n", mi->mode, memcmp(lfb, src, 256) == 0 ? "ok" : "MISMATCH");
            __djgpp_nearptr_disable();
            __dpmi_free_physical_address_mapping(&m);
        }
        else
            printf("mode 0x%03X: LFB mapping / nearptr enable failed\n", mi->mode);
    }
    else
        printf("mode 0x%03X: no LFB (physbase=0x%08lX) or LFB mode set failed\n", mi->mode, mi->phys);
}

int main(void)
{
    int modes[256], n, i, found32 = 0;
    modeinfo mi;
    long k;

    setvbuf(stdout, NULL, _IONBF, 0);
    src = (unsigned char *)malloc(SRC_BYTES);
    if (!src) { printf("malloc failed\n"); return 1; }
    for (k = 0; k < SRC_BYTES; k++) src[k] = (unsigned char)((k * 7) ^ (k >> 9));
    uclock();
    printf("bwprobe32 UCLOCKS_PER_SEC=%ld\n", (long)UCLOCKS_PER_SEC);

    n = vbe_mode_list(modes, 256);
    printf("mode list: %d modes\n", n);
    for (i = 0; i < n; i++)
        if (vbe_mode_info(modes[i], &mi) && mi.x == 640 && mi.y == 480)
            printf("  listed 0x%03X 640x480 bpp=%d pitch=%d physbase=0x%08lX\n", mi.mode, mi.bpp, mi.pitch, mi.phys);

    /* Anchor first: 0x111 must reproduce 2026-09-17's 27.3 MB/s (LFB). */
    if (vbe_mode_info(0x111, &mi))
        mode_tests(&mi);
    else
        printf("mode 0x111: VBE mode info call failed -- anchor missing\n");

    for (i = 0; i < n; i++)
        if (vbe_mode_info(modes[i], &mi) && mi.x == 640 && mi.y == 480 && (mi.bpp == 32 || mi.bpp == 24))
        {
            mode_tests(&mi);
            if (mi.bpp == 32) found32++;
        }
    if (!found32)
        printf("no 640x480x32 mode listed\n");

    bios_mode(0x03);
    printf("done\n");
    return 0;
}
