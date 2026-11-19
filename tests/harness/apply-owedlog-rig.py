#!/usr/bin/env python3
"""apply-owedlog-rig.py VENDOR_AGS -- the per-call pacer log for round RS's instrumented 486 run (lab-rb PREREG-PACE50
section 4 + FIX-UP D, the 486 run that also logs now - epoch and owed per pacer call). A DIAGNOSTIC overlay for one
rig round, applied to main's 0383 tree, instrumented flavour only; never a patch, never in a release.
It is lab-rb apply-owedlog.py (PREREG-OWEDLOG, accepted by sdlports) without its PACE50 dependence and with the record
packed and the buffer sized for the 486:
  - per call of dos_run_tick_fixed whose loop counter is at or after DOSAGS_LAB_OWEDLOG=<from> (unset: no log; one
    getenv), one 24-byte record in a static buffer of 8,192 (196,608 bytes of .bss):
      lc (int32), t_us (uint32, uclock microseconds, low 32 bits), since_us (int32, now - epoch when owed is computed),
      wait_us (int32, the drawn tick's WaitForNextFrame wait; -1 if none), owed (int16), catchup (uint8, ticks run),
      rebase (uint8: 0 none, 1 0163's flag at the top, 2 the clamp after the loop, 3 ahead), reset (uint8, the frame
      time was reset to now in that wait), 3 pad bytes;
  - calls before <from> are counted (before=), not logged; a full buffer counts the rest (dropped=);
  - at exit, OWED.BIN (binary, "wb") in the game directory: a 28-byte header (magic 0x3144574F "OWD1", version 1, n,
    before, dropped, from, record size 24; seven uint32 little-endian) and the n records; and one RUNMANIFEST line
    "DOS-PORT labowed from= n= before= dropped= bytes= write=ok|fail".
  - No I/O during the run.
The 486 run logs from 5430 to the exit at 12440: at most ~7,010 calls (one per drawn tick), under 8,192."""
import sys
V = sys.argv[1]


def ed(rel, pairs):
    p = V + '/' + rel
    s = open(p).read()
    for a, b in pairs:
        assert s.count(a) == 1, (rel, a[:70], s.count(a))
        s = s.replace(a, b, 1)
    open(p, 'w').write(s)


ed('Engine/ac/timer.cpp', [
    ('void WaitForNextFrame()\n{\n',
     'long long lab_ow_wait_us = -1; int lab_ow_reset = 0;   // OWEDLOG-RIG: set by the last WaitForNextFrame\n'
     'void WaitForNextFrame()\n{\n'),
    ('    if (next_frame_timestamp < (now - MAXIMUM_FALL_BEHIND*frameDuration)) {\n        next_frame_timestamp = now;\n    }\n',
     '    lab_ow_reset = 0;   // OWEDLOG-RIG\n'
     '    if (next_frame_timestamp < (now - MAXIMUM_FALL_BEHIND*frameDuration)) {\n        next_frame_timestamp = now;\n'
     '        lab_ow_reset = 1;   // OWEDLOG-RIG\n    }\n'),
    ('    last_tick_time = next_frame_timestamp;\n    next_frame_timestamp += frameDuration;\n',
     '    lab_ow_wait_us = (long long)std::chrono::duration_cast<std::chrono::microseconds>(Clock::now() - now).count();   // OWEDLOG-RIG\n'
     '    last_tick_time = next_frame_timestamp;\n    next_frame_timestamp += frameDuration;\n'),
])

ed('Engine/main/game_run.cpp', [
    ('using namespace AGS::Common;\nusing namespace AGS::Engine;\n',
     '''using namespace AGS::Common;
using namespace AGS::Engine;
// ---- OWEDLOG-RIG (round RS; tests/harness/apply-owedlog-rig.py): the per-call pacer log ----
extern long long lab_ow_wait_us; extern int lab_ow_reset;
struct LabOwedRec { int32_t lc; uint32_t t_us; int32_t since_us; int32_t wait_us; int16_t owed; uint8_t catchup, rebase, reset, pad[3]; };
static_assert(sizeof(LabOwedRec) == 24, "OWEDLOG-RIG record size");
static LabOwedRec lab_ow_buf[8192];
static long lab_ow_from = -2, lab_ow_n = 0, lab_ow_before = 0, lab_ow_dropped = 0;
'''),
    ('static void dos_run_tick_fixed()\n{\n',
     '''static void dos_run_tick_fixed()
{
    if (lab_ow_from == -2) { const char *e = getenv("DOSAGS_LAB_OWEDLOG"); lab_ow_from = e ? atol(e) : -1; }
    LabOwedRec lab_r = {};
    const bool lab_on = lab_ow_from >= 0 && (long)get_loop_counter() >= lab_ow_from;
    if (lab_ow_from >= 0 && !lab_on) lab_ow_before++;
    lab_r.lc = (int32_t)get_loop_counter();
'''),
    ('            epoch_ns = Clock::now();\n            epoch_tick = get_loop_counter();\n            dos_stall_resyncs++;\n',
     '            epoch_ns = Clock::now();\n            epoch_tick = get_loop_counter();\n            dos_stall_resyncs++;\n'
     '            lab_r.rebase = 1;   // OWEDLOG-RIG\n'),
    ('    long owed = expected_ticks - actual_ticks;\n',
     '    long owed = expected_ticks - actual_ticks;\n'
     '    lab_r.t_us = (uint32_t)std::chrono::duration_cast<std::chrono::microseconds>(now_ns.time_since_epoch()).count();   // OWEDLOG-RIG\n'
     '    lab_r.since_us = (int32_t)std::chrono::duration_cast<std::chrono::microseconds>(now_ns - epoch_ns).count();\n'
     '    lab_r.owed = (int16_t)(owed > 32767 ? 32767 : (owed < -32768 ? -32768 : owed));\n'),
    ('    if (n > 0) dos_catchup_events++;\n',
     '    if (n > 0) dos_catchup_events++;\n    lab_r.catchup = (uint8_t)n;   // OWEDLOG-RIG\n'),
    ('    if (owed > 0 || owed < -MAX_CATCHUP)\n    {\n        epoch_ns = Clock::now();\n        epoch_tick = get_loop_counter();\n    }\n',
     '    if (owed > 0 || owed < -MAX_CATCHUP)\n    {\n        epoch_ns = Clock::now();\n        epoch_tick = get_loop_counter();\n'
     '        if (lab_r.rebase == 0) lab_r.rebase = owed > 0 ? 2 : 3;   // OWEDLOG-RIG\n    }\n'),
    ('    // The one tick that actually renders + paces via WaitForNextFrame().\n    UpdateGameOnce(true);\n',
     '    // The one tick that actually renders + paces via WaitForNextFrame().\n'
     '    lab_ow_wait_us = -1; lab_ow_reset = 0;   // OWEDLOG-RIG\n    UpdateGameOnce(true);\n'
     '    if (lab_on)   // OWEDLOG-RIG\n    {\n'
     '        lab_r.wait_us = (int32_t)(lab_ow_wait_us > 0x7FFFFFFF ? 0x7FFFFFFF : lab_ow_wait_us); lab_r.reset = (uint8_t)lab_ow_reset;\n'
     '        if (lab_ow_n < 8192) lab_ow_buf[lab_ow_n++] = lab_r; else lab_ow_dropped++;\n    }\n'),
    ('    fprintf(log, "DOS-PORT tick_rate_steady=',
     '''    {   // OWEDLOG-RIG: the records to OWED.BIN (binary), one summary line here
        long lab_bytes = 0; const char *lab_w = "none";
        if (lab_ow_from >= 0)
        {
            FILE *f = fopen("OWED.BIN", "wb");
            const uint32_t h[7] = { 0x3144574Fu, 1u, (uint32_t)lab_ow_n, (uint32_t)lab_ow_before, (uint32_t)lab_ow_dropped,
                                    (uint32_t)lab_ow_from, (uint32_t)sizeof(LabOwedRec) };
            bool ok = f && fwrite(h, sizeof(h), 1, f) == 1 &&
                      (lab_ow_n == 0 || fwrite(lab_ow_buf, sizeof(LabOwedRec), (size_t)lab_ow_n, f) == (size_t)lab_ow_n);
            if (f && fclose(f) != 0) ok = false;
            lab_bytes = ok ? (long)(sizeof(h) + sizeof(LabOwedRec) * (size_t)lab_ow_n) : 0; lab_w = ok ? "ok" : "fail";
        }
        fprintf(log, "DOS-PORT labowed from=%ld n=%ld before=%ld dropped=%ld bytes=%ld write=%s\\n", lab_ow_from, lab_ow_n,
            lab_ow_before, lab_ow_dropped, lab_bytes, lab_w);
    }
    fprintf(log, "DOS-PORT tick_rate_steady='''),
])
print('OWEDLOG-RIG applied')
