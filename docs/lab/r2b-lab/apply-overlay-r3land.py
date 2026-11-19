#!/usr/bin/env python3
"""Lab gate overlay for ags 0368 (lever R3) -- never landed. Applies to vendor/ags in place (uncommitted), over 0001-0368.
Based on R1LAND-2026-11-06's overlay (FRAMEHASH, LABCLICKS, FORCE_WHOLE, NOGUARD), with:
 - DOSAGS_LAB_FRAMEHASH=1: FHASH.TXT, (loop counter, hash of the composited virtual screen) after every composite
 - DOSAGS_LABCLICKS=lc:x:y[:b],...: fixture clicks (b=1) / pointer moves (b=0)
 - DOSAGS_LAB_GUISKIP_BREAK=2: R3 control, mode 4's per-box list leaves out the carry boxes (LAB-R3's mode 5)
 - guard (b) = 0366's full-restore latch:
     DOSAGS_LAB_FORCE_WHOLE=N: every Nth room restore, the next room-rect mark takes invalidate_rect_on_surf's
       overflow exit (NumDirtyRegions = WHOLESCREENDIRTY, mark dropped), the path a 26th rect takes
     DOSAGS_LAB_NOGUARD=1: control, dos_guiclip_note_fullrestore counts but does not arm the latch
 - guard (a) = 0368's span-coarsening fallback:
     DOSAGS_LAB_SPANMAX=N: a row holds at most N spans before AGS stretches one (AGS: MAX_SPANS_PER_ROW = 4)
     DOSAGS_LAB_SPANPROBE=K[:Y]: every Kth room restore, two 2x2 marks (as a sprite's invalidation, screen coords,
       after the restore and its Reset) at the left and right ends of rows Y..Y+1 of the room viewport (default: its bottom two
       rows). With SPANMAX=1 the second one stretches the row's span across the whole gap between them.
     DOSAGS_LAB_NOCOARSE=1: control, dos_guiclip_note_span_stretch counts but does not record the stretch
 - DOSAGS_LAB_CKPT=lc,lc,...: at each listed loop counter print
     "DOS-PORT labck lc= rbspr_us= rbspr_calls= rts_us= rts_calls=" (instrumented flavour only)
 - guiclip_final gains " lab_forced= lab_noguard= lab_probes= lab_nocoarse= lab_spanmax="
"""
import sys
root = sys.argv[1]
def edit(rel, pairs):
    p = root + '/' + rel; s = open(p).read()
    for a, b in pairs:
        assert s.count(a) == 1, (rel, a[:70]); s = s.replace(a, b, 1)
    open(p, 'w').write(s)

edit('Engine/main/game_run.cpp', [(
"void UpdateGameOnce(bool do_controls, IDriverDependantBitmap *extra_ddb, int extra_x, int extra_y, bool skip_render_and_wait)\n{",
'''#ifdef __DJGPP__
static int dos_lc_mode = -1, dos_lc_n = 0, dos_lc_next = 0;   // GATE OVERLAY: DOSAGS_LABCLICKS
static long dos_lc_t[64]; static int dos_lc_x[64], dos_lc_y[64], dos_lc_b[64];
static int dos_ck_mode = -1, dos_ck_n = 0, dos_ck_next = 0; static long dos_ck_t[64];   // GATE OVERLAY: DOSAGS_LAB_CKPT
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
#ifndef DOSAGS_RELEASE
    if (dos_ck_mode < 0)
    {
        dos_ck_mode = 0;
        const char *e = getenv("DOSAGS_LAB_CKPT");
        while (e && *e && dos_ck_n < 64)
        {
            long t; int used = 0;
            if (sscanf(e, "%ld%n", &t, &used) != 1) break;
            dos_ck_t[dos_ck_n++] = t; e += used;
            if (*e == ',') e++;
        }
        if (dos_ck_n > 0) dos_ck_mode = 1;
    }
    if (dos_ck_mode == 1 && dos_ck_next < dos_ck_n && (long)get_loop_counter() >= dos_ck_t[dos_ck_next])
    {
        dos_ck_next++;
        Debug::Printf("DOS-PORT labck lc=%ld rbspr_us=%lld rbspr_calls=%ld rts_us=%lld rts_calls=%ld", (long)get_loop_counter(),
            dos_port_tick_timing.rb_sprite_time.total_us, dos_port_tick_timing.rb_sprite_time.calls,
            dos_port_tick_timing.render_to_screen_pertick.total_us, dos_port_tick_timing.render_to_screen_pertick.calls);
    }
#endif
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
'#include "debug/out.h"                 // DOS-PORT patch 0366: the guiclip witness line\n'
'extern uint32_t get_loop_counter();    // GATE OVERLAY\n'
'long dos_lab_forced = 0, dos_lab_probes = 0;   // GATE OVERLAY (draw_software.cpp counts)\n'
'int dos_lab_spanmax_v = 4;                     // GATE OVERLAY (draw_software.cpp sets)\n'), (
'''void dos_guiclip_note_fullrestore()
{
    dos_gc_set_latch(dos_gc_latch_fullrestore);''',
'''void dos_guiclip_note_fullrestore()
{
    static int _noguard = -1;   // GATE OVERLAY: DOSAGS_LAB_NOGUARD=1 counts the fire but does not arm the latch
    if (_noguard < 0) { const char *e = getenv("DOSAGS_LAB_NOGUARD"); _noguard = (e && e[0] == '1') ? 1 : 0; }
    if (_noguard) { dos_gc_latch_fullrestore++; return; }
    dos_gc_set_latch(dos_gc_latch_fullrestore);'''), (
'''void dos_guiclip_note_span_stretch()
{
    dos_gc_span_acc = 1;
    dos_gc_span_stretch++;''',
'''void dos_guiclip_note_span_stretch()
{
    static int _nocoarse = -1;   // GATE OVERLAY: DOSAGS_LAB_NOCOARSE=1 counts the stretch but does not record it
    if (_nocoarse < 0) { const char *e = getenv("DOSAGS_LAB_NOCOARSE"); _nocoarse = (e && e[0] == '1') ? 1 : 0; }
    if (_nocoarse) { dos_gc_span_stretch++; return; }
    dos_gc_span_acc = 1;
    dos_gc_span_stretch++;'''), (
'''" boxed=%ld boxes=%ld fb_coarse=%ld fb_whole=%ld span_stretch=%ld coarse_restores=%ld\\n",''',
'''" boxed=%ld boxes=%ld fb_coarse=%ld fb_whole=%ld span_stretch=%ld coarse_restores=%ld"
        " lab_forced=%ld lab_noguard=%d lab_probes=%ld lab_nocoarse=%d lab_spanmax=%d\\n",'''), (
'''        dos_gc_boxed, dos_gc_boxes, dos_gc_fb_coarse, dos_gc_fb_whole, dos_gc_span_stretch, dos_gc_coarse_restores);''',
'''        dos_gc_boxed, dos_gc_boxes, dos_gc_fb_coarse, dos_gc_fb_whole, dos_gc_span_stretch, dos_gc_coarse_restores,
        dos_lab_forced, getenv("DOSAGS_LAB_NOGUARD") && getenv("DOSAGS_LAB_NOGUARD")[0] == '1' ? 1 : 0,
        dos_lab_probes, getenv("DOSAGS_LAB_NOCOARSE") && getenv("DOSAGS_LAB_NOCOARSE")[0] == '1' ? 1 : 0, dos_lab_spanmax_v);'''), (
'''                const int _nb = dos_port_dirty.nbox, _nt = _nb + dos_port_dirty.carry_nbox;''',
'''                static int _gate_break = -1;   // GATE OVERLAY: DOSAGS_LAB_GUISKIP_BREAK=2 leaves the carry boxes out (control)
                if (_gate_break < 0) { const char *b = getenv("DOSAGS_LAB_GUISKIP_BREAK"); _gate_break = (b && b[0] == '2') ? 1 : 0; }
                const int _nb = dos_port_dirty.nbox, _nt = _nb + (_gate_break ? 0 : dos_port_dirty.carry_nbox);'''), (
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
extern long dos_lab_forced, dos_lab_probes;
extern int dos_lab_spanmax_v;
// GATE OVERLAY: DOSAGS_LAB_SPANMAX=N (spans per row before a stretch), DOSAGS_LAB_SPANPROBE=K[:Y] (two 2x2 marks)
static int dos_lab_spanmax = -1, dos_lab_probe_k = 0, dos_lab_probe_y = -1; static long dos_lab_probe_frames = 0;
static int dos_lab_spanmax_get()
{
    if (dos_lab_spanmax < 0)
    {
        const char *e = getenv("DOSAGS_LAB_SPANMAX");
        dos_lab_spanmax = (e && atoi(e) >= 1 && atoi(e) <= MAX_SPANS_PER_ROW) ? atoi(e) : MAX_SPANS_PER_ROW;
        dos_lab_spanmax_v = dos_lab_spanmax;
        const char *p = getenv("DOSAGS_LAB_SPANPROBE");
        if (p) { dos_lab_probe_k = atoi(p); const char *c = strchr(p, ':'); if (c) dos_lab_probe_y = atoi(c + 1); }
    }
    return dos_lab_spanmax;
}
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
'''        else if (dirtyRow[a].numSpans < MAX_SPANS_PER_ROW) {''',
'''        else if (dirtyRow[a].numSpans < dos_lab_spanmax_get()) {   // GATE OVERLAY: AGS's MAX_SPANS_PER_ROW'''), (
'''    dos_port_dirty_note_restore();   // patch 0193: marks made from here on are repainted next frame''',
'''    dos_port_dirty_note_restore();   // patch 0193: marks made from here on are repainted next frame
    if (dos_lab_force_n < 0) { const char *e = getenv("DOSAGS_LAB_FORCE_WHOLE"); dos_lab_force_n = e ? atoi(e) : 0; }   // GATE OVERLAY
    if (dos_lab_force_n > 0 && (++dos_lab_force_frames % dos_lab_force_n) == 0) dos_lab_force_next = true;'''), (
'''    RoomCamRects[view_index].Reset();
}''',
'''    RoomCamRects[view_index].Reset();
#ifdef __DJGPP__
    // GATE OVERLAY: span probe, AFTER the Reset (marks made before it are wiped): post-restore marks, like a sprite's
    dos_lab_spanmax_get();
    if (dos_lab_probe_k > 0 && (++dos_lab_probe_frames % dos_lab_probe_k) == 0)
    {
        const Rect &v = RoomCamRects[view_index].Viewport;
        const int py = dos_lab_probe_y >= 0 ? v.Top + dos_lab_probe_y : v.Bottom - 1;
        invalidate_rect_ds(v.Left, py, v.Left + 1, py + 1, false);
        invalidate_rect_ds(v.Right - 1, py, v.Right, py + 1, false);
        dos_lab_probes++;
    }
#endif
}''')])
print('overlay applied')
