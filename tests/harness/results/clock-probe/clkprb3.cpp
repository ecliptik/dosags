// clkprb3 -- why did gettimeofday() cost 42 ms inside the engine after the
// patch-0095 RTC edge sync (cell TNC96A1), when it costs 1.3 ms standalone?
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <sys/time.h>
#include <dpmi.h>
#include <pc.h>
static int cmos(int reg) { outportb(0x70, reg & 0x7F); return inportb(0x71); }
static double gtod_us(int n) {
  uclock_t t0 = uclock(); struct timeval tv; volatile long s = 0;
  for (int i = 0; i < n; i++) { gettimeofday(&tv, 0); s += tv.tv_usec; if (uclock() - t0 > (uclock_t)UCLOCKS_PER_SEC * 6) { n = i + 1; break; } }
  return (double)(uclock() - t0) * 1e6 / UCLOCKS_PER_SEC / n;
}
static double int21_us(int ah, int n) {
  uclock_t t0 = uclock(); __dpmi_regs r;
  for (int i = 0; i < n; i++) { memset(&r, 0, sizeof r); r.h.ah = ah; __dpmi_int(0x21, &r); if (uclock() - t0 > (uclock_t)UCLOCKS_PER_SEC * 6) { n = i + 1; break; } }
  return (double)(uclock() - t0) * 1e6 / UCLOCKS_PER_SEC / n;
}
static void show(const char *tag) {
  struct timeval tv; gettimeofday(&tv, 0);
  time_t t = tv.tv_sec; struct tm *tm = localtime(&t);
  printf("%-28s gtod_us=%9.1f int21_2c_us=%8.1f int21_2a_us=%8.1f  dos=%02d:%02d:%02d\n",
    tag, gtod_us(300), int21_us(0x2c, 300), int21_us(0x2a, 300), tm->tm_hour, tm->tm_min, tm->tm_sec);
}
static void rtc_show(const char *tag) {
  int a = cmos(0x0A), b = cmos(0x0B), s = cmos(0), m = cmos(2), h = cmos(4);
  printf("%-28s regA=%02x regB=%02x h=%02x m=%02x s=%02x\n", tag, a, b, h, m, s);
}
int main(void) {
  setvbuf(stdout, NULL, _IONBF, 0);
  uclock();
  show("0_before_anything");
  printf("port70_readback=%02x (not readable on most chipsets)\n", inportb(0x70));
  rtc_show("1_rtc_regs");
  show("1_after_rtc_port_reads");
  // the engine's edge sync, as patch 0095 does it
  { int s0 = cmos(0); uclock_t t0 = uclock(); long polls = 0;
    for (;;) { if (cmos(0x0A) & 0x80) { polls++; continue; } int s = cmos(0); polls++; if (s != s0) break; if (uclock() - t0 > (uclock_t)UCLOCKS_PER_SEC * 3) break; }
    printf("2_edge_sync polls=%ld waited_ms=%ld\n", polls, (long)((uclock() - t0) * 1000 / UCLOCKS_PER_SEC)); }
  show("2_after_edge_sync");
  outportb(0x70, 0x0A); show("3_index_left_at_0A");
  outportb(0x70, 0x0C); show("3_index_left_at_0C");
  outportb(0x70, 0x00); show("3_index_left_at_00");
  outportb(0x70, 0x8D); show("4_index_8D_nmi_masked");
  outportb(0x70, 0x0D); show("4_index_0D_nmi_enabled");
  { __dpmi_regs r; memset(&r, 0, sizeof r); r.h.ah = 2; __dpmi_int(0x1A, &r);
    printf("5_int1a_02 flags=%04x %02x:%02x:%02x\n", r.x.flags, r.h.ch, r.h.cl, r.h.dh); }
  show("5_after_int1a_02");
  rtc_show("6_rtc_regs_end");
  return 0;
}
