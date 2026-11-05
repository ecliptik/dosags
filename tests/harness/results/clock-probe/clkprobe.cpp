// clkprobe -- 40/40 plan, P1 item 1. Synthetic DJGPP probe, same style as
// overhead-probe/ovhtest.cpp: measure with uclock() the per-call cost of
// the primitives the idle per-tick path actually executes.
//
// Hypothesis under test (PLAN.md "40/40 plan", finding 3): on an idle
// screen the engine spends ~22 ms/tick with zero script work, in costs so
// constant they smell like a shared cause -- the engine's Clock::now()
// (std::chrono, which on this libstdc++ has no CLOCK_MONOTONIC and falls
// back to gettimeofday(); DJGPP's gettimeofday() references __dpmi_int
// twice plus mktime/localtime, confirmed by disassembling libc.a) and the
// per-tick __dpmi_int(0x33) mouse poll.
//
// Includes the ENGINE'S OWN header so (a) is the exact type the engine
// uses, not a lookalike.
#include <stdio.h>
#include <time.h>
#include <sys/time.h>
#include <dpmi.h>
#include <string.h>
#include <chrono>
#include <thread>
#include "util/time_util.h"

using AGS::Engine::Clock;

static double us_per(uclock_t t0, uclock_t t1, long n)
{
    return (double)(t1 - t0) * 1000000.0 / (double)UCLOCKS_PER_SEC / (double)(n > 0 ? n : 1);
}

// Every measured loop is bounded by BOTH an iteration count and a wall
// budget: the first DOSBox-X run of this probe sat >4 minutes in
// sleep_for(0) (usleep() spins on clock(), which only steps every ~55 ms),
// and a probe must report that rather than hang on it. The budget check
// reads uclock() once per 16 iterations, so its own cost (measured as the
// control, item c) stays out of the per-call figure to within ~6%.
#define BUDGET_S 6
#define BOUNDED(N_, BODY_) \
    do { \
        const uclock_t _lim = (uclock_t)UCLOCKS_PER_SEC * BUDGET_S; \
        t0 = uclock(); done = 0; \
        while (done < (N_)) { BODY_; done++; \
            if ((done & 15) == 0 && (uclock() - t0) > _lim) break; } \
        t1 = uclock(); \
    } while (0)

int main(void)
{
    const long N = 10000;
    uclock_t t0, t1;
    long i, done;
    volatile long long sink = 0;
    (void)i;
    setvbuf(stdout, NULL, _IONBF, 0);

    printf("clkprobe N=%ld UCLOCKS_PER_SEC=%ld\n", N, (long)UCLOCKS_PER_SEC);
    printf("Clock is_steady=%d  high_resolution_clock::is_steady=%d  period=%ld/%ld\n",
        (int)Clock::is_steady, (int)std::chrono::high_resolution_clock::is_steady,
        (long)Clock::period::num, (long)Clock::period::den);

    // (c) control: uclock() itself
    BOUNDED(N, sink += (long long)uclock());
    printf("c_uclock              us_per_call=%.3f n=%ld\n", us_per(t0, t1, done), done);

    // (a) the engine's actual Clock::now()
    BOUNDED(N, sink += Clock::now().time_since_epoch().count());
    printf("a_engine_Clock_now    us_per_call=%.3f n=%ld\n", us_per(t0, t1, done), done);

    // (a') decomposition: what Clock::now() bottoms out in
    BOUNDED(N, { struct timeval tv; gettimeofday(&tv, 0); sink += tv.tv_usec; });
    printf("a1_gettimeofday       us_per_call=%.3f n=%ld\n", us_per(t0, t1, done), done);

    BOUNDED(N, { __dpmi_regs r; memset(&r, 0, sizeof r); r.h.ah = 0x2C; __dpmi_int(0x21, &r); sink += r.h.dl; });
    printf("a2_dpmi_int21_gettime us_per_call=%.3f n=%ld\n", us_per(t0, t1, done), done);

    {
        struct tm tmv; time_t now = time(0); tmv = *localtime(&now);
        BOUNDED(N, { struct tm c = tmv; sink += (long long)mktime(&c); });
        printf("a3_mktime             us_per_call=%.3f n=%ld\n", us_per(t0, t1, done), done);
    }

    // (b) one mouse poll exactly as DOSVESA_PumpEvents() issues it (ax=3)
    {
        __dpmi_regs r; memset(&r, 0, sizeof r); r.x.ax = 0; __dpmi_int(0x33, &r);
        printf("mouse_driver_present=%d buttons=%d\n", (int)(r.x.ax == 0xFFFF), (int)r.x.bx);
    }
    BOUNDED(N, { __dpmi_regs r; r.x.ax = 0x3; __dpmi_int(0x33, &r); sink += r.x.cx; });
    printf("b_dpmi_int33_mouse    us_per_call=%.3f n=%ld\n", us_per(t0, t1, done), done);

    // (d) what the pacing wait can execute
    BOUNDED(N, std::this_thread::sleep_for(std::chrono::nanoseconds(0)));
    printf("d1_sleep_for_0        us_per_call=%.3f n=%ld\n", us_per(t0, t1, done), done);

    BOUNDED(N, __dpmi_yield());
    printf("d2_dpmi_yield         us_per_call=%.3f n=%ld\n", us_per(t0, t1, done), done);

    {
        const long M = 100;
        BOUNDED(M, std::this_thread::sleep_for(std::chrono::milliseconds(1)));
        printf("d3_sleep_for_1ms      us_per_call=%.3f n=%ld\n", us_per(t0, t1, done), done);
        BOUNDED(M, std::this_thread::sleep_for(std::chrono::milliseconds(10)));
        printf("d4_sleep_for_10ms     us_per_call=%.3f n=%ld\n", us_per(t0, t1, done), done);
        BOUNDED(M, std::this_thread::sleep_for(std::chrono::milliseconds(25)));
        printf("d5_sleep_for_25ms     us_per_call=%.3f n=%ld\n", us_per(t0, t1, done), done);
    }

    // Resolution of the engine Clock: smallest and typical nonzero step
    // between successive now() values. The frame pacer schedules 25 ms
    // periods off this clock, so a coarse step matters independently of cost.
    {
        long steps = 0; long long min_step = -1, sum_step = 0;
        Clock::time_point prev = Clock::now();
        uclock_t start = uclock();
        while ((uclock() - start) < (uclock_t)UCLOCKS_PER_SEC * 2)
        {
            Clock::time_point cur = Clock::now();
            if (cur != prev)
            {
                long long d = std::chrono::duration_cast<std::chrono::microseconds>(cur - prev).count();
                if (d > 0) { if (min_step < 0 || d < min_step) min_step = d; sum_step += d; steps++; }
                prev = cur;
            }
        }
        printf("Clock_resolution steps_in_2s=%ld min_step_us=%lld mean_step_us=%lld\n",
            steps, min_step, steps ? sum_step / steps : 0LL);
    }

    printf("sink=%lld\n", (long long)sink);
    return 0;
}
