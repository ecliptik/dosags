#!/usr/bin/env python3
"""Lab gate overlay for ags 0366+0367 (never landed). Applies to vendor/ags in place (uncommitted):
 - DOSAGS_LAB_FRAMEHASH=1: FHASH.TXT, (loop counter, hash of the composited virtual screen) after every composite
 - DOSAGS_LABCLICKS=lc:x:y[:b],...: fixture G's clicks (b=1) / moves (b=0)
 - DOSAGS_LAB_GUISKIP_BREAK=1: control, mode 2 skips every flagged entry
 - DOSAGS_LAB_FORCE_WHOLE=N: every Nth room restore, the next room-rect mark takes invalidate_rect_on_surf's
   overflow exit (NumDirtyRegions = WHOLESCREENDIRTY, mark dropped), the path a 26th rect takes
 - DOSAGS_LAB_NOGUARD=1: control, dos_guiclip_note_fullrestore counts but does not arm the latch
 - guiclip_final gains " lab_forced=N lab_noguard=0|1"
"""
import sys
root = sys.argv[1]
def edit(rel, pairs):
    p = root + '/' + rel; s = open(p).read()
    for a, b in pairs:
        assert a in s, (rel, a[:60]); s = s.replace(a, b, 1)
    open(p, 'w').write(s)

edit('Engine/main/game_run.cpp', [(
"void UpdateGameOnce(bool do_controls, IDriverDependantBitmap *extra_ddb, int extra_x, int extra_y, bool skip_render_and_wait)\n{",
'''#ifdef __DJGPP__
static int dos_lc_mode = -1, dos_lc_n = 0, dos_lc_next = 0;   // GATE OVERLAY: DOSAGS_LABCLICKS
static long dos_lc_t[64]; static int dos_lc_x[64], dos_lc_y[64], dos_lc_b[64];
static void dos_lab_clicks()
{
    if (dos_lc_mode < 0)
    {
        dos_lc_mode = 0;
        const char *e = getenv("DOSAGS_LABCLICKS");
        while (e && *e && dos_lc_n < 64)
        {
            long t; int x, y, used = 0, b = 1, used2 = 0;
            if (sscanf(e, "%ld:%d:%d%n", &t, &x, &y, &used) != 3) break;
            e += used;
            if (*e == ':' && sscanf(e, ":%d%n", &b, &used2) == 1) e += used2;
            dos_lc_t[dos_lc_n] = t; dos_lc_x[dos_lc_n] = x; dos_lc_y[dos_lc_n] = y; dos_lc_b[dos_lc_n] = b; dos_lc_n++;
            if (*e == ',') e++;
        }
        if (dos_lc_n > 0) { dos_lc_mode = 1; Debug::Printf("DOS-PORT labclicks n=%d", dos_lc_n); }
    }
    if (dos_lc_mode != 1 || dos_lc_next >= dos_lc_n) return;
    const long lc = (long)get_loop_counter();
    if (lc < dos_lc_t[dos_lc_next]) return;
    const int k = dos_lc_next++;
    SetMousePosition(dos_lc_x[k], dos_lc_y[k]);
    if (dos_lc_b[k]) SimulateMouseClick(kMouseLeft);
    Debug::Printf("DOS-PORT labclick lc=%ld n=%d x=%d y=%d click=%d", lc, k + 1, dos_lc_x[k], dos_lc_y[k], dos_lc_b[k]);
}
#endif

void UpdateGameOnce(bool do_controls, IDriverDependantBitmap *extra_ddb, int extra_x, int extra_y, bool skip_render_and_wait)
{'''), (
"        dos_tick_clicks();   // patch 0247: no-op unless DOSAGS_TICKCLICKS is set\n",
"        dos_tick_clicks();   // patch 0247: no-op unless DOSAGS_TICKCLICKS is set\n        dos_lab_clicks();    // GATE OVERLAY\n")])

edit('Engine/gfx/ali3dsw.cpp', [(
'#include "debug/out.h"                 // DOS-PORT patch 0366: the guiclip witness line\n',
'#include "debug/out.h"                 // DOS-PORT patch 0366: the guiclip witness line\nextern uint32_t get_loop_counter();    // GATE OVERLAY\nlong dos_lab_forced = 0;               // GATE OVERLAY (draw_software.cpp counts)\n'), (
'''void dos_guiclip_note_fullrestore()
{
    dos_gc_set_latch(dos_gc_latch_fullrestore);
}''',
'''void dos_guiclip_note_fullrestore()
{
    static int _noguard = -1;   // GATE OVERLAY: DOSAGS_LAB_NOGUARD=1 counts the fire but does not arm the latch
    if (_noguard < 0) { const char *e = getenv("DOSAGS_LAB_NOGUARD"); _noguard = (e && e[0] == '1') ? 1 : 0; }
    if (_noguard) { dos_gc_latch_fullrestore++; return; }
    dos_gc_set_latch(dos_gc_latch_fullrestore);
}'''), (
'''" latch_events=%ld latch_alias=%ld latch_buffer=%ld latch_tint=%ld latch_fullrestore=%ld\\n",''',
'''" latch_events=%ld latch_alias=%ld latch_buffer=%ld latch_tint=%ld latch_fullrestore=%ld lab_forced=%ld lab_noguard=%d\\n",'''), (
'''        dos_gc_latch_events, dos_gc_latch_alias, dos_gc_latch_buffer, dos_gc_latch_tint, dos_gc_latch_fullrestore);''',
'''        dos_gc_latch_events, dos_gc_latch_alias, dos_gc_latch_buffer, dos_gc_latch_tint, dos_gc_latch_fullrestore,
        dos_lab_forced, getenv("DOSAGS_LAB_NOGUARD") && getenv("DOSAGS_LAB_NOGUARD")[0] == '1' ? 1 : 0);'''), (
'''            if (dos_guiclip_mode() == 2 && native_bmp &&
                IntersectRects(isect, Rect(drawAtX, drawAtY, drawAtX + native_bmp->GetWidth() - 1,
                                           drawAtY + native_bmp->GetHeight() - 1)).IsEmpty())''',
'''            static int _gate_break = -1;   // GATE OVERLAY: DOSAGS_LAB_GUISKIP_BREAK=1 skips every flagged entry (control)
            if (_gate_break < 0) { const char *b = getenv("DOSAGS_LAB_GUISKIP_BREAK"); _gate_break = (b && b[0] == '1') ? 1 : 0; }
            if (dos_guiclip_mode() == 2 && native_bmp && (_gate_break ||
                IntersectRects(isect, Rect(drawAtX, drawAtY, drawAtX + native_bmp->GetWidth() - 1,
                                           drawAtY + native_bmp->GetHeight() - 1)).IsEmpty()))'''), (
'''    _stageVirtualScreen = virtualScreen;
    _rendSpriteBatch = UINT32_MAX;
    ClearDrawLists();
}''',
'''    _stageVirtualScreen = virtualScreen;
    _rendSpriteBatch = UINT32_MAX;
    ClearDrawLists();
#ifdef __DJGPP__
    {   // GATE OVERLAY: DOSAGS_LAB_FRAMEHASH=1 -> FHASH.TXT
        static int fh_mode = -1; static unsigned long *fh_buf = nullptr; static long fh_n = 0;
        static const long FH_CAP = 40000;
        struct FhDump { static void dump() { FILE *f = fopen("FHASH.TXT", "w"); if (!f) return;
            for (long i = 0; i < fh_n; ++i) fprintf(f, "%lu %08lx\\n", fh_buf[2 * i], fh_buf[2 * i + 1]); fclose(f); } };
        if (fh_mode < 0)
        {
            const char *e = getenv("DOSAGS_LAB_FRAMEHASH");
            fh_mode = (e && e[0] == '1') ? 1 : 0;
            if (fh_mode) { fh_buf = (unsigned long *)malloc(sizeof(unsigned long) * 2 * FH_CAP); atexit(FhDump::dump); }
        }
        if (fh_mode == 1 && fh_buf && fh_n < FH_CAP && virtualScreen)
        {
            unsigned long hsh = 2166136261UL;
            const int bw = virtualScreen->GetWidth() * virtualScreen->GetBPP();
            for (int y = 0; y < virtualScreen->GetHeight(); ++y)
            {
                const uint32_t *row = reinterpret_cast<const uint32_t *>(virtualScreen->GetScanLine(y));
                for (int x = 0; x < bw / 4; ++x) { hsh ^= row[x]; hsh *= 16777619UL; hsh ^= hsh >> 15; }
            }
            fh_buf[2 * fh_n] = (unsigned long)::get_loop_counter();
            fh_buf[2 * fh_n + 1] = hsh & 0xFFFFFFFFUL;
            fh_n++;
        }
    }
#endif
}''')])

edit('Engine/ac/draw_software.cpp', [(
'''void invalidate_rect_on_surf(int x1, int y1, int x2, int y2, DirtyRects &rects)
{
    if (rects.DirtyRows.size() == 0)
        return;
''',
'''#ifdef __DJGPP__
// GATE OVERLAY: DOSAGS_LAB_FORCE_WHOLE=N -- after every Nth room restore, the next room-rect mark takes the overflow
// exit below (NumDirtyRegions = WHOLESCREENDIRTY, mark dropped), the path a 26th rect in one interval takes.
static int dos_lab_force_n = -1; static long dos_lab_force_frames = 0; static bool dos_lab_force_next = false;
extern long dos_lab_forced;
#endif
void invalidate_rect_on_surf(int x1, int y1, int x2, int y2, DirtyRects &rects)
{
    if (rects.DirtyRows.size() == 0)
        return;
#ifdef __DJGPP__
    if (dos_lab_force_next && &rects != &BlackRects)
    {
        dos_lab_force_next = false; dos_lab_forced++;
        rects.NumDirtyRegions = WHOLESCREENDIRTY;   // as the overflow branch: too many rects, whole surface dirty
        return;
    }
#endif
'''), (
'''    dos_port_dirty_note_restore();   // patch 0193: marks made from here on are repainted next frame''',
'''    dos_port_dirty_note_restore();   // patch 0193: marks made from here on are repainted next frame
    if (dos_lab_force_n < 0) { const char *e = getenv("DOSAGS_LAB_FORCE_WHOLE"); dos_lab_force_n = e ? atoi(e) : 0; }   // GATE OVERLAY
    if (dos_lab_force_n > 0 && (++dos_lab_force_frames % dos_lab_force_n) == 0) dos_lab_force_next = true;''')])
print('overlay applied')
