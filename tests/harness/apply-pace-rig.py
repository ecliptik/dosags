#!/usr/bin/env python3
"""apply-pace-rig.py VENDOR_AGS -- round RT's pacer switch for the 486 A/B (PREREG in ROUNDRT-<date>/README.md). A
LAB OVERLAY for one rig round, applied to main's 0383 tree, built in the RELEASE flavour; never a patch without a new
operator ruling, never in a release.
It is lab-rb apply-pace50.py (PREREG-PACE50 + FIX-UP 2, accepted by sdlports; the switch read exact in RESULT-PACE50-LAB2)
cut down to what a release-flavour 486 run needs:
  DOSAGS_LAB_STALL_MS=T   0163's flag is also raised when a top-level tick's own time (DosTickStallScope's self_us, the
                          time the flag already reads; in the release flavour too) is over T ms, and DOSAGS_STALL_RESYNC
                          is implied: the debt after such a tick is forgiven (the epoch rebased) instead of repaid. The
                          stall statistics keep their 250 ms (tick_stall lines and tick_rate_steady unchanged).
  DOSAGS_LAB_SPIN=tick:ms[,tick:ms...]   LAB CELLS ONLY (never set on the rig): a uclock spin of ms just after the tick's
                          DosTickStallScope opens (the release flavour has no per-tick-log scope), on the first call at or
                          after each tick (at most 32) -- inside the tick's own time, as a long click tick is on the 486.
  Unset (both): no code path changes beyond two getenv calls at the first tick and a few compares per tick.
  Dropped from apply-pace50.py: DOSAGS_LAB_BASESPIN (the lab's knife-edge regimes; not needed here).
Exit line (RUNMANI.LOG): "DOS-PORT labpace stall_ms= rebases= forgiven_ticks= max_forgiven_ticks= max_forgiven_short_ticks=
spins=" and, per spin,
"DOS-PORT labspin i= want_tick= tick= nominal_ms= self_ms= flagged=" (self_ms: the tick's own time as the flag saw it).
rebases counts every 0163 rebase (the restore's and the room loads' included); forgiven_ticks is the debt each dropped.
FIX-UP 1 (sdlports' Q2 information): max_forgiven_short_ticks = the largest debt forgiven by a rebase that 0163's own flag
(a tick over 250 ms, nested or not) did not raise -- i.e. outside the restore, the room loads and any other tick over 250 ms.
FIX-UP 2 (sdlports): the "long" mark is set beside 0163's own `dos_tick_prev_was_stall = true`, with the same condition
and no depth check, so a nested tick over 250 ms is never counted as short. The 45 ms flag stays at depth 0 (PACE50's
rule). IsGamePaused()'s early return in dos_run_tick_fixed skips the clear, so the marks carry over a pause; MS3 does not
pause."""
import sys
V = sys.argv[1]
p = V + '/Engine/main/game_run.cpp'
s = open(p).read()


def rep(a, b):
    global s
    assert s.count(a) == 1, (a[:70], s.count(a))
    s = s.replace(a, b, 1)


rep('static bool dos_tick_prev_was_stall = false;\n', '''static bool dos_tick_prev_was_stall = false;
// ---- PACE-RIG (round RT; tests/harness/apply-pace-rig.py): the long-tick rule's threshold ----
static long lab_pace_stall_us = -1;          // -1 unread, 0 off, else the threshold in us
static long lab_pace_rebases = 0, lab_pace_forgiven = 0, lab_pace_max_forgiven = 0;
static long lab_pace_max_short = 0;          // FIX-UP 1: the largest debt forgiven after a tick NOT over 250 ms
static bool lab_pace_prev_long = false;      // FIX-UP 1: a tick over 250 ms ran since the last call
static int lab_pace_nspin = 0, lab_pace_next = 0, lab_pace_in_spin = -1;
static long lab_pace_want[32], lab_pace_ms[32], lab_pace_tick[32], lab_pace_self_ms[32];
static int lab_pace_flagged[32];
static void lab_pace_init()
{
    if (lab_pace_stall_us >= 0) return;
    const char *e = getenv("DOSAGS_LAB_STALL_MS");
    lab_pace_stall_us = (e && atol(e) > 0) ? atol(e) * 1000L : 0;
    const char *sp = getenv("DOSAGS_LAB_SPIN");
    while (sp && *sp && lab_pace_nspin < 32)
    {
        char *end = nullptr;
        const long t = strtol(sp, &end, 10);
        if (end == sp || *end != ':') break;
        const long ms = strtol(end + 1, &end, 10);
        lab_pace_want[lab_pace_nspin] = t; lab_pace_ms[lab_pace_nspin] = ms; lab_pace_tick[lab_pace_nspin] = -1;
        lab_pace_self_ms[lab_pace_nspin] = -1; lab_pace_flagged[lab_pace_nspin] = 0; lab_pace_nspin++;
        if (*end != ',') break;
        sp = end + 1;
    }
}
static void lab_pace_spin()
{
    lab_pace_init();
    lab_pace_in_spin = -1;
    if (lab_pace_next >= lab_pace_nspin || dos_tick_depth != 1) return;
    const long lc = (long)get_loop_counter();
    if (lc < lab_pace_want[lab_pace_next]) return;
    lab_pace_tick[lab_pace_next] = lc;
    const uclock_t t0 = uclock();
    while ((long long)(uclock() - t0) * 1000LL / UCLOCKS_PER_SEC < lab_pace_ms[lab_pace_next]) { }
    lab_pace_in_spin = lab_pace_next++;
}
''')
rep('    DosTickStallScope _dos_tick_stall_scope; // patch 0093\n',
    '    DosTickStallScope _dos_tick_stall_scope; // patch 0093\n'
    '    lab_pace_spin();   // PACE-RIG: lab cells only (DOSAGS_LAB_SPIN); inside the tick\'s own time\n')
rep('        if (self_us > DOS_TICK_STALL_THRESHOLD_US)\n        {\n            if (dos_tick_stall_total < DOS_TICK_STALL_CAP)',
    '''        if (lab_pace_in_spin >= 0 && dos_tick_depth == 0)   // PACE-RIG: the spun tick's own time, as the flag sees it
        {
            lab_pace_self_ms[lab_pace_in_spin] = (long)(self_us / 1000);
            lab_pace_flagged[lab_pace_in_spin] = (lab_pace_stall_us > 0 && self_us > lab_pace_stall_us) ? 1 : 0;
            lab_pace_in_spin = -1;
        }
        if (lab_pace_stall_us > 0 && self_us > lab_pace_stall_us && dos_tick_depth == 0)
            dos_tick_prev_was_stall = true;                  // PACE-RIG: 0163's flag at the threshold
        if (self_us > DOS_TICK_STALL_THRESHOLD_US)
        {
            if (dos_tick_stall_total < DOS_TICK_STALL_CAP)''')
rep('''        if (hint < 0) { const char *h = getenv("DOSAGS_STALL_RESYNC");
                        hint = (h && h[0] == '1') ? 1 : 0; }''', '''        if (hint < 0) { const char *h = getenv("DOSAGS_STALL_RESYNC");
                        hint = (h && h[0] == '1') ? 1 : 0;
                        lab_pace_init(); if (lab_pace_stall_us > 0) hint = 1; }   // PACE-RIG: implied''')
rep('''            epoch_ns = Clock::now();
            epoch_tick = get_loop_counter();
            dos_stall_resyncs++;''', '''            {   // PACE-RIG: the ticks this rebase forgives
                const long f = (long)((Clock::now() - epoch_ns) / tick_dur) - (long)(get_loop_counter() - epoch_tick);
                if (f > 0) { lab_pace_forgiven += f; if (f > lab_pace_max_forgiven) lab_pace_max_forgiven = f;
                             if (!lab_pace_prev_long && f > lab_pace_max_short) lab_pace_max_short = f; }   // FIX-UP 1
                lab_pace_rebases++;
            }
            epoch_ns = Clock::now();
            epoch_tick = get_loop_counter();
            dos_stall_resyncs++;''')
rep('            dos_tick_prev_was_stall = true;   // patch 0163\n',
    '            dos_tick_prev_was_stall = true;   // patch 0163\n'
    '            lab_pace_prev_long = true;        // PACE-RIG FIX-UP 2: beside 0163\'s own flag (no depth condition, as it)\n')
rep('''        dos_tick_prev_was_stall = false;
    }
''', '''        dos_tick_prev_was_stall = false;
        lab_pace_prev_long = false;   // PACE-RIG FIX-UP 1
    }
''')
rep('    fprintf(log, "DOS-PORT tick_rate_steady=', '''    lab_pace_init();   // PACE-RIG
    fprintf(log, "DOS-PORT labpace stall_ms=%ld rebases=%ld forgiven_ticks=%ld max_forgiven_ticks=%ld max_forgiven_short_ticks=%ld spins=%d\\n",
        lab_pace_stall_us / 1000, lab_pace_rebases, lab_pace_forgiven, lab_pace_max_forgiven, lab_pace_max_short, lab_pace_nspin);
    for (int i = 0; i < lab_pace_nspin; ++i)
        fprintf(log, "DOS-PORT labspin i=%d want_tick=%ld tick=%ld nominal_ms=%ld self_ms=%ld flagged=%d\\n", i, lab_pace_want[i],
            lab_pace_tick[i], lab_pace_ms[i], lab_pace_self_ms[i], lab_pace_flagged[i]);
    fprintf(log, "DOS-PORT tick_rate_steady=''')
open(p, 'w').write(s)
print('PACE-RIG applied')
