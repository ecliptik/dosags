// clkprobe2 -- P1 item 2 (40/40 plan): what the NEW engine Clock
// (DosUclockClock, patches/ags/0096) actually does on the machine it has
// to work on. Companion to clkprobe.cpp, which measured the old one; kept
// separate so that record stays as it was.
//
// Includes the engine's own util/time_util.h, so "Clock" below is
// whatever the engine really uses at the pinned patch level -- build it
// after `make patches`:
//   i586-pc-msdosdjgpp-g++ -O2 -std=gnu++11 -I vendor/ags/Engine \
//       -o /tmp/clkprb2.exe tests/harness/results/clock-probe/clkprobe2.cpp
//
// Every loop is bounded by a wall budget as well as a count (the first
// clkprobe hung for minutes in a loop that was not).
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <dpmi.h>
#include <pc.h>
#include <chrono>
#include "util/time_util.h"

using AGS::Engine::Clock;

static long long us_of(uclock_t d) { return (long long)d * 1000000LL / UCLOCKS_PER_SEC; }

static int cmos(int reg) { outportb(0x70, reg & 0x7F); return inportb(0x71); }
static int rtc_sec_raw(void)
{
    for (int i = 0; i < 4096; i++)
    {
        if (cmos(0x0A) & 0x80) continue;
        int s = cmos(0x00);
        if (cmos(0x0A) & 0x80) continue;
        if (cmos(0x00) != s) continue;
        return s;
    }
    return -1;
}
// spins to the next RTC second edge; returns uclock at the edge, 0 on timeout
static uclock_t rtc_edge(void)
{
    const int s0 = rtc_sec_raw();
    const uclock_t t0 = uclock();
    for (;;)
    {
        const int s = rtc_sec_raw();
        const uclock_t t = uclock();
        if (s >= 0 && s != s0) return t;
        if (t - t0 > (uclock_t)UCLOCKS_PER_SEC * 3) return 0;
    }
}

int main(void)
{
    setvbuf(stdout, NULL, _IONBF, 0);
    volatile long long sink = 0;
    printf("clkprobe2 UCLOCKS_PER_SEC=%ld Clock::is_steady=%d period=%ld/%ld\n",
        (long)UCLOCKS_PER_SEC, (int)Clock::is_steady, (long)Clock::period::num, (long)Clock::period::den);

    // 1. cost of one engine Clock read, beside raw uclock()
    {
        const long N = 200000;
        uclock_t t0 = uclock();
        for (long i = 0; i < N; i++) sink += (long long)uclock();
        uclock_t t1 = uclock();
        for (long i = 0; i < N; i++) sink += Clock::now().time_since_epoch().count();
        uclock_t t2 = uclock();
        printf("1_cost uclock_us=%.3f engine_Clock_now_us=%.3f n=%ld\n",
            (double)us_of(t1 - t0) / N, (double)us_of(t2 - t1) / N, N);
    }

    // 2. raw uclock(): how often, and how far, does it step backwards?
    {
        const uclock_t lim = (uclock_t)UCLOCKS_PER_SEC * 8;
        const uclock_t t0 = uclock();
        uclock_t prev = t0, worst = 0;
        long reads = 0, back = 0;
        for (;;)
        {
            const uclock_t t = uclock();
            reads++;
            if (t < prev) { back++; if (prev - t > worst) worst = prev - t; }
            prev = t;
            if (t - t0 > lim && t > t0) break;
        }
        printf("2_raw_uclock reads=%ld backward_steps=%ld worst_backward_us=%lld over_s=8\n",
            reads, back, us_of(worst));
    }

    // 3. the engine Clock over the same kind of loop: backward steps must
    //    be ZERO (the monotonic guard), and the largest forward step shows
    //    what the guard costs (time held still, then released).
    {
        const auto t0 = Clock::now();
        auto prev = t0;
        long reads = 0, back = 0;
        long long worst_fwd_ns = 0;
        for (;;)
        {
            const auto t = Clock::now();
            reads++;
            if (t < prev) back++;
            const long long d = std::chrono::duration_cast<std::chrono::nanoseconds>(t - prev).count();
            if (d > worst_fwd_ns) worst_fwd_ns = d;
            prev = t;
            if (t - t0 > std::chrono::seconds(8)) break;
        }
        printf("3_engine_Clock reads=%ld backward_steps=%ld worst_forward_step_us=%lld over_s=8\n",
            reads, back, worst_fwd_ns / 1000);
    }

    // 4. uclock vs the CMOS RTC (its own 32.768 kHz crystal) over 10 s
    {
        const uclock_t e0 = rtc_edge();
        uclock_t e = e0;
        int edges = 0;
        while (e0 && e && edges < 10) { e = rtc_edge(); if (e) edges++; }
        if (!e0 || !e)
            printf("4_rtc_ratio status=rtc_unreadable edges=%d\n", edges);
        else
            printf("4_rtc_ratio status=ok rtc_s=%d uclock_us=%lld ratio=%.5f\n",
                edges, us_of(e - e0), (double)us_of(e - e0) / (edges * 1000000.0));
    }

    // 5. does INT 1Ah AH=02h advance here? (frozen under DOSBox-X)
    {
        __dpmi_regs r;
        memset(&r, 0, sizeof r); r.h.ah = 2; __dpmi_int(0x1A, &r);
        const int s0 = r.h.dh;
        const uclock_t t0 = uclock();
        int s = s0; long polls = 0;
        while (s == s0 && uclock() - t0 < (uclock_t)UCLOCKS_PER_SEC * 3)
        { memset(&r, 0, sizeof r); r.h.ah = 2; __dpmi_int(0x1A, &r); s = r.h.dh; polls++; }
        printf("5_int1a_ah02 advanced=%d polls=%ld waited_ms=%lld\n",
            (int)(s != s0), polls, us_of(uclock() - t0) / 1000);
    }

    // 6. the pacer's own loop shape: 200 deadlines on a 25 ms grid. Total
    //    must be 5000 ms by uclock AND by the RTC bracket around it.
    {
        const uclock_t e0 = rtc_edge();
        const uclock_t u0 = uclock();
        auto deadline = Clock::now();
        long long worst_over_ns = 0;
        for (int i = 0; i < 200; i++)
        {
            deadline += std::chrono::milliseconds(25);
            Clock::time_point t;
            for (;;) { t = Clock::now(); if (t >= deadline) break; }
            const long long over = std::chrono::duration_cast<std::chrono::nanoseconds>(t - deadline).count();
            if (over > worst_over_ns) worst_over_ns = over;
        }
        const uclock_t u1 = uclock();
        const uclock_t e1 = rtc_edge();
        printf("6_pacer_grid frames=200 uclock_ms=%.3f worst_overshoot_us=%lld rtc_bracket_us=%lld (expect 5000 + <1000 ms to next edge)\n",
            (double)us_of(u1 - u0) / 1000.0, worst_over_ns / 1000, (e0 && e1) ? us_of(e1 - e0) : -1LL);
    }

    printf("sink=%lld\n", (long long)sink);
    return 0;
}
