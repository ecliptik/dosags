#include <stdio.h>
#include <time.h>
#include "dos_port_tick_timing.h"

/* DosPortTickTiming is a C++ struct with default member initializers,
 * so this probe is compiled as C++ (same language as the real engine
 * code that uses it), matching the actual mechanism exactly rather
 * than a reimplementation. */

DosPortTickTiming dos_port_tick_timing;

/* Real per-tick bracket-pair count, tallied from TNP82C's own real-
 * hardware RUNMANIFEST data (1000-tick run): summing every
 * tickstats_*_calls field gives ~18635 total DosPortTickScope
 * constructions across the whole run, i.e. ~18.6 per tick on average.
 * Rounded to 19 per simulated tick below. */
#define BRACKETS_PER_TICK 19
#define NUM_TICKS 1000

static long dummy_sink = 0;

int main(void)
{
    uclock_t t0, t1;
    long i, j;

    /* Baseline: NUM_TICKS * BRACKETS_PER_TICK empty function calls,
     * NO timing instrumentation at all -- pure loop/call overhead. */
    t0 = uclock();
    for (i = 0; i < NUM_TICKS; i++)
    {
        for (j = 0; j < BRACKETS_PER_TICK; j++)
        {
            dummy_sink += j; /* trivial body, matches the "empty bracket body" case */
        }
    }
    t1 = uclock();
    printf("baseline (no instrumentation): %.2f ms for %ld ticks (%.4f ms/tick)\n",
        (double)(t1 - t0) * 1000.0 / UCLOCKS_PER_SEC, (long)NUM_TICKS,
        (double)(t1 - t0) * 1000.0 / UCLOCKS_PER_SEC / NUM_TICKS);

    /* Instrumented: same loop, but each inner iteration is wrapped in
     * a real DosPortTickScope (the exact mechanism used throughout
     * patches 0079-0082), all sharing one phase bucket since we only
     * care about the TOTAL overhead, not per-phase breakdown here. */
    t0 = uclock();
    for (i = 0; i < NUM_TICKS; i++)
    {
        for (j = 0; j < BRACKETS_PER_TICK; j++)
        {
            DosPortTickScope scope(dos_port_tick_timing.script_vm);
            dummy_sink += j;
        }
    }
    t1 = uclock();
    printf("instrumented (%d brackets/tick): %.2f ms for %ld ticks (%.4f ms/tick)\n",
        BRACKETS_PER_TICK, (double)(t1 - t0) * 1000.0 / UCLOCKS_PER_SEC, (long)NUM_TICKS,
        (double)(t1 - t0) * 1000.0 / UCLOCKS_PER_SEC / NUM_TICKS);

    printf("recorded stats: calls=%ld total_ms=%ld mean_ms=%.4f\n",
        dos_port_tick_timing.script_vm.calls,
        dos_port_tick_timing.script_vm.total_ms,
        dos_port_tick_timing.script_vm.calls > 0
            ? (double)dos_port_tick_timing.script_vm.total_ms / dos_port_tick_timing.script_vm.calls
            : 0.0);

    printf("dummy_sink=%ld\n", dummy_sink);
    return 0;
}
