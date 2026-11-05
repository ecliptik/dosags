/* clkprobe.c -- is uclock() telling the truth on this machine?
 *
 * Why this exists. Every tick_rate figure this campaign has produced --
 * including Gate 1's claimed 39.54 and Gate 3's 41.35 -- is
 * LoopCounter / get_runtime_ms(), and get_runtime_ms() is backed by
 * uclock(), which is derived from PIT channel 0. The pacer's deadline
 * wait watches the same clock. A "pacer overshoot" of about 3% has been
 * recorded and parked as cosmetic since the AQ work; if instead uclock
 * runs 3% fast, then every rate this campaign has reported is 3% high and
 * a 39.54 or a 41.35 against a 40 bar has no margin to absorb it.
 *
 * The CMOS real-time clock is a separate crystal on a separate device.
 * DJGPP's time() reads it. So RTC-versus-uclock over a long interval is a
 * genuinely independent check, not the PIT grading its own homework.
 *
 * The BIOS tick counter at 0040:006C is included as a THIRD reading, and
 * it answers a different question: it comes off the same PIT crystal as
 * uclock but through a different divisor path, so agreement there with
 * disagreement against the RTC would point at the crystal, while
 * disagreement between the two PIT-derived numbers would point at
 * uclock's own scaling.
 *
 * Deliberately long (default 60 RTC seconds). The RTC has 1-second
 * resolution, so a short run cannot resolve 3%: at 60 s the +/-1 s edge
 * uncertainty is 1.7%, and edge-aligning the start (below) halves the
 * error that matters.
 */

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <dos.h>
#include <dpmi.h>
#include <go32.h>
#include <sys/farptr.h>

/* BIOS tick count, 0040:006C, incremented by IRQ0 at 18.2065 Hz. */
static unsigned long bios_ticks(void)
{
    unsigned long t;
    _farsetsel(_dos_ds);
    t = _farnspeekl(0x46C);
    return t;
}

int main(int argc, char **argv)
{
    int want_s = (argc > 1) ? atoi(argv[1]) : 60;
    time_t t0, t1, tnow;
    uclock_t u0, u1;
    unsigned long b0, b1;
    double rtc_s, uclock_s, bios_s;

    /* TZ must be set before any libc time call on this target -- unset TZ
     * gives garbage zone state and ~42 ms clock reads on real DOS. */
    putenv("TZ=UTC0");
    tzset();

    if (want_s < 5) want_s = 5;

    printf("clkprobe: uclock vs CMOS RTC vs BIOS ticks, %d RTC seconds\n", want_s);
    printf("UCLOCKS_PER_SEC=%ld\n", (long)UCLOCKS_PER_SEC);
    fflush(stdout);

    /* Edge-align: spin until the RTC second changes, so the start instant
     * is known to much better than a second. Without this the start edge
     * alone contributes up to 1 s of error in the same direction as the
     * thing being measured. */
    t0 = time(NULL);
    do { tnow = time(NULL); } while (tnow == t0);
    t0 = tnow;

    u0 = uclock();
    b0 = bios_ticks();

    /* Wait for want_s RTC seconds. Poll time() only -- nothing here may
     * depend on the clock under test. */
    do { tnow = time(NULL); } while ((long)(tnow - t0) < want_s);
    t1 = tnow;

    u1 = uclock();
    b1 = bios_ticks();

    rtc_s    = (double)(long)(t1 - t0);
    uclock_s = (double)(u1 - u0) / (double)UCLOCKS_PER_SEC;
    bios_s   = (double)(b1 - b0) / 18.2064819336;

    printf("rtc_s=%.3f\n", rtc_s);
    printf("uclock_s=%.3f  uclock_over_rtc=%.5f  err_pct=%+.3f\n",
           uclock_s, uclock_s / rtc_s, 100.0 * (uclock_s / rtc_s - 1.0));
    printf("bios_s=%.3f  bios_over_rtc=%.5f  err_pct=%+.3f\n",
           bios_s, bios_s / rtc_s, 100.0 * (bios_s / rtc_s - 1.0));
    printf("uclock_over_bios=%.5f\n", uclock_s / bios_s);

    /* Read it out in the terms the campaign actually cares about: if
     * uclock runs fast, a measured rate is high by the same factor. */
    printf("\nIF uclock is the reference, a measured 41.35 tick/s is really %.2f\n",
           41.35 * rtc_s / uclock_s);
    printf("IF uclock is the reference, a measured 39.54 tick/s is really %.2f\n",
           39.54 * rtc_s / uclock_s);

    printf("done\n");
    return 0;
}
