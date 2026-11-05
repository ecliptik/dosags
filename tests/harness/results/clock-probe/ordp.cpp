// ordp -- replicate patch 0095's start-of-main sequence exactly: the RTC
// edge sync (which makes the process's FIRST uclock() call) and only then
// the first time() call. TNC96A1 logged started_utc=2059-04-13.
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <dos.h>
#include <pc.h>
static int dos_port_cmos_read(int reg) { outportb(0x70, reg & 0x7F); return inportb(0x71); }
static long dos_port_rtc_read_s()
{
    for (int tries = 0; tries < 4096; tries++)
    {
        if (dos_port_cmos_read(0x0A) & 0x80) continue;
        int sec = dos_port_cmos_read(0x00);
        int m = dos_port_cmos_read(0x02);
        int h = dos_port_cmos_read(0x04);
        const int reg_b = dos_port_cmos_read(0x0B);
        if (dos_port_cmos_read(0x0A) & 0x80) continue;
        if (dos_port_cmos_read(0x00) != sec) continue;
        const bool pm = (h & 0x80) != 0;
        h &= 0x7F;
        if (!(reg_b & 0x04)) { sec = ((sec >> 4) * 10) + (sec & 0x0F); m = ((m >> 4) * 10) + (m & 0x0F); h = ((h >> 4) * 10) + (h & 0x0F); }
        if (!(reg_b & 0x02)) h = (h % 12) + (pm ? 12 : 0);
        if (h > 23 || m > 59 || sec > 59) return -1;
        return (long)h * 3600L + (long)m * 60L + (long)sec;
    }
    return -1;
}
static long dos_port_rtc_wait_edge(uclock_t *edge_uclock)
{
    const long s0 = dos_port_rtc_read_s();
    if (s0 < 0) return -1;
    const uclock_t t_start = uclock();
    for (;;)
    {
        const long s = dos_port_rtc_read_s();
        const uclock_t t = uclock();
        if (s >= 0 && s != s0) { if (edge_uclock) *edge_uclock = t; return s; }
        if (t - t_start > (uclock_t)UCLOCKS_PER_SEC * 3) return -1;
    }
}
int main(void)
{
    setvbuf(stdout, NULL, _IONBF, 0);
    uclock_t e0 = 0, e1 = 0;
    const long s_start = dos_port_rtc_wait_edge(&e0);   // FIRST uclock() of the process is in here
    const time_t t0 = time(0);                           // FIRST time() of the process
    struct tm *g = gmtime(&t0);
    char buf[64]; strftime(buf, sizeof buf, "%Y-%m-%dT%H:%M:%SZ", g);
    printf("after_sync rtc_s=%ld time()=%lu started_utc=%s\n", s_start, (unsigned long)t0, buf);
    struct date d; struct time t; getdate(&d); gettime(&t);
    printf("dos_date=%04d-%02d-%02d dos_time=%02d:%02d:%02d\n", d.da_year, d.da_mon, d.da_day, t.ti_hour, t.ti_min, t.ti_sec);
    // hold ~20 s like a (short) run, then the end sync, as quit.cpp does
    const uclock_t h0 = uclock();
    while (uclock() - h0 < (uclock_t)UCLOCKS_PER_SEC * 20) { volatile time_t x = time(0); (void)x; }
    const long s_end = dos_port_rtc_wait_edge(&e1);
    long span = s_end - s_start; if (span <= 0) span += 86400L;
    printf("end_sync rtc_start=%ld rtc_end=%ld rtc_span_s=%ld uclock_ms=%ld ratio=%.5f\n", s_start, s_end, span,
        (long)((e1 - e0) * 1000 / UCLOCKS_PER_SEC), (double)(e1 - e0) / UCLOCKS_PER_SEC / (double)span);
    getdate(&d); gettime(&t);
    printf("dos_date=%04d-%02d-%02d dos_time=%02d:%02d:%02d\n", d.da_year, d.da_mon, d.da_day, t.ti_hour, t.ti_min, t.ti_sec);
    return 0;
}
