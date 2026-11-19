#!/usr/bin/env python3
"""L2LAND gate overlay (LAB-L2G section 8's apply-overlay-l2g-slim.py, anchors renamed to patch 0372; lab only, never
landed): applies over 0001-0372. As apply-overlay-l2g.py, anchors adapted to the slim code, plus DOSAGS_LAB_GC2_CAP=N (the slot cap
forced to N, 0..16; the forced overflow cell). First runs LAB-RB's overlay
(apply-overlay-rb.py, in this directory), then adds:
 - DOSAGS_LABCLICKS=G / =V: R3LAND's fixtures G and V (as LAB-R2B's overlay spells them)
 - DOSAGS_LAB_GC2_VERIFY=1 (on arm; reads only): for every L2 GUI, a copy of its texture before the redraw is compared
   with the redrawn texture OUTSIDE the marked rects; differing px are counted (must be 0) and the first 20 events
   printed ("DOS-PORT labgc2 verify gui= px_out= px_in=")
 - controls (on arm): DOSAGS_LAB_GC2_NOMARK=1 (C1) the L2 path marks nothing; DOSAGS_LAB_GC2_SHORT=N (C2) each rect
   is marked N px short on every side
 - forcings (both arms, every N loop ticks, on GUI g control c; default g 0 c 0; "DOSAGS_LAB_GC2_x=N[:g:c]"):
     MOVE=N  F1: the control moves +1 px in x on odd windows and back on even ones; every 4th window it shrinks by 1 px
             in width instead
     VIS=N   F2: the GUI is hidden for one window, then (next odd window) its transparency is set to 10 for one window
     TEXT=N  F3: a label control's text gets " WWWWWWWWWWWW" appended on odd windows and is restored on even ones
   "DOS-PORT labgc2 force what= lc=" per action (first 40)
 - "DOS-PORT labgc2_final verify_checks= verify_px_out= verify_px_in= forced=" after guictrlmark_final
Usage: apply-overlay-l2g.py VENDOR_AGS_ROOT"""
import os, subprocess, sys
root = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
subprocess.check_call([sys.executable, os.path.join(here, 'apply-overlay-rb.py'), root])


def edit(rel, pairs):
    p = root + '/' + rel; s = open(p).read()
    for a, b in pairs:
        assert s.count(a) == 1, (rel, a[:80]); s = s.replace(a, b, 1)
    open(p, 'w').write(s)


edit('Engine/main/game_run.cpp', [(
'''        if (e && strcmp(e, "H") == 0) e = k_h;''',
'''        if (e && strcmp(e, "H") == 0) e = k_h;
        // L2G OVERLAY: R3LAND's fixtures G and V (LAB-R2B's spelling of them)
        static const char *k_g = "5600:160:150:0,5700:100:180:0,5800:290:170:0,5900:160:100:0,6000:60:135,6400:250:135,"
            "6800:1:135,7100:60:160:0,7200:200:190:0,7300:160:80:0,7500:40:130,7900:300:130,8050:150:150:0,8150:150:60:0";
        static const char *k_v = "6000:60:135,6400:250:135,6800:1:135,7000:160:80:0,7400:65:166:0,7800:65:166,8200:200:170:0,"
            "8600:300:185:0,9000:25:155:0,9050:65:166:0,9100:110:178:0,9150:25:166:0,9200:65:178:0,9250:110:155:0";
        if (e && strcmp(e, "G") == 0) e = k_g;
        if (e && strcmp(e, "V") == 0) e = k_v;'''), (
'''        dos_lab_clicks();    // GATE OVERLAY
''',
'''        dos_lab_clicks();    // GATE OVERLAY
        { extern void dos_lab_gc2_force(); dos_lab_gc2_force(); }   // L2G OVERLAY
''')])

edit('Engine/ac/draw.cpp', [(
'''// Before the texture redraw: nothing may have flagged the GUI between the flush and here.
static void dos_gc2_before_redraw(int i, GUIMain &g)
{''',
'''// L2G OVERLAY: knobs and the verify
static int dos_lab_gc2_env(const char *n) { const char *e = getenv(n); return (e && *e) ? atoi(e) : 0; }
static Bitmap *dos_lab_gc2_copy[64];
static long dos_lab_gc2_checks = 0, dos_lab_gc2_forced = 0;
static long long dos_lab_gc2_px_out = 0, dos_lab_gc2_px_in = 0;
static void dos_lab_gc2_verify_before(int i)
{
    static int v = -1; if (v < 0) v = dos_lab_gc2_env("DOSAGS_LAB_GC2_VERIFY");
    delete dos_lab_gc2_copy[i]; dos_lab_gc2_copy[i] = nullptr;
    if (v && dos_gc2_ok[i] && guibg[i].Bmp) dos_lab_gc2_copy[i] = BitmapHelper::CreateBitmapCopy(guibg[i].Bmp.get());
}
static void dos_lab_gc2_verify_after(int i)
{
    Bitmap *a = dos_lab_gc2_copy[i], *b = guibg[i].Bmp.get();
    if (!a) return;
    dos_lab_gc2_copy[i] = nullptr;
    long out = 0, in = 0;
    if (b && a->GetWidth() == b->GetWidth() && a->GetHeight() == b->GetHeight() && a->GetBPP() == b->GetBPP())
    {
        const int bpp = a->GetBPP();
        for (int y = 0; y < a->GetHeight(); ++y)
        {
            const uint8_t *ra = a->GetScanLine(y), *rb = b->GetScanLine(y);
            for (int x = 0; x < a->GetWidth(); ++x)
            {
                if (memcmp(ra + x * bpp, rb + x * bpp, bpp) == 0) continue;
                bool inside = false;
                const DosGc2Gui *gb = dos_gc2_g[i];
                for (int k = 0; gb && k < gb->markedn; ++k) if (gb->marked[k].R().IsInside(x, y)) { inside = true; break; }
                if (inside) in++; else out++;
            }
        }
    }
    else out = -1;   // the texture changed size: counted as a failure
    dos_lab_gc2_checks++;
    dos_lab_gc2_px_out += out < 0 ? 1000000 : out; dos_lab_gc2_px_in += in;
    static int printed = 0;
    if (out != 0 && printed < 20) { printed++; Debug::Printf("DOS-PORT labgc2 verify gui=%d px_out=%ld px_in=%ld", i, out, in); }
    delete a;
}
void dos_lab_gc2_report(FILE *log)
{
    if (log) fprintf(log, "DOS-PORT labgc2_final verify_checks=%ld verify_px_out=%lld verify_px_in=%lld forced=%ld\\n",
        dos_lab_gc2_checks, dos_lab_gc2_px_out, dos_lab_gc2_px_in, dos_lab_gc2_forced);
}
// forcings, both arms: called once per UpdateGameOnce (game_run.cpp)
static void dos_lab_gc2_parse(const char *n, int &every, int &g, int &c)
{
    every = 0; g = 0; c = 0; const char *e = getenv(n);
    if (e && *e) sscanf(e, "%d:%d:%d", &every, &g, &c);
}
void dos_lab_gc2_force()
{
    static int init = 0, mv_n, mv_g, mv_c, vi_n, vi_g, vi_c, tx_n, tx_g, tx_c;
    static long last_lc = -1;
    static String tx_orig; static bool tx_on = false;
    static int mv_state = 0, vi_state = 0;
    if (!init) { init = 1; dos_lab_gc2_parse("DOSAGS_LAB_GC2_MOVE", mv_n, mv_g, mv_c);
                 dos_lab_gc2_parse("DOSAGS_LAB_GC2_VIS", vi_n, vi_g, vi_c); dos_lab_gc2_parse("DOSAGS_LAB_GC2_TEXT", tx_n, tx_g, tx_c); }
    if (displayed_room < 0) return;
    const long lc = (long)get_loop_counter();
    if (lc == last_lc) return;
    last_lc = lc;
    if (mv_n > 0 && lc % mv_n == 0 && mv_g < game.numgui && mv_c < guis[mv_g].GetControlCount())
    {
        GUIObject *o = guis[mv_g].GetControl(mv_c);
        const long w = lc / mv_n;
        if ((w % 4) == 3) { if (mv_state == 0) { o->SetWidth(o->GetWidth() - 1); mv_state = 2; } }
        else if (mv_state == 2) { o->SetWidth(o->GetWidth() + 1); mv_state = 0; }
        else if (mv_state == 0) { o->SetX(o->GetX() + 1); mv_state = 1; }
        else { o->SetX(o->GetX() - 1); mv_state = 0; }
        dos_lab_gc2_forced++;
        if (dos_lab_gc2_forced <= 40) Debug::Printf("DOS-PORT labgc2 force what=move state=%d lc=%ld", mv_state, lc);
    }
    if (vi_n > 0 && lc % vi_n == 0 && vi_g < game.numgui)
    {
        GUIMain &g = guis[vi_g];
        switch (vi_state)
        {
        case 0: g.SetVisible(false); break;
        case 1: g.SetVisible(true); break;
        case 2: g.SetTransparency(10); break;
        default: g.SetTransparency(0); break;
        }
        vi_state = (vi_state + 1) % 4;
        dos_lab_gc2_forced++;
        if (dos_lab_gc2_forced <= 40) Debug::Printf("DOS-PORT labgc2 force what=vis state=%d lc=%ld", vi_state, lc);
    }
    if (tx_n > 0 && lc % tx_n == 0 && tx_g < game.numgui && tx_c < guis[tx_g].GetControlCount() &&
        guis[tx_g].GetControlType(tx_c) == kGUILabel)
    {
        GUILabel *l = static_cast<GUILabel *>(guis[tx_g].GetControl(tx_c));
        if (!tx_on) { tx_orig = l->GetText(); l->SetText(String::FromFormat("%s WWWWWWWWWWWW", tx_orig.GetCStr())); tx_on = true; }
        else { l->SetText(tx_orig); tx_on = false; }
        dos_lab_gc2_forced++;
        if (dos_lab_gc2_forced <= 40) Debug::Printf("DOS-PORT labgc2 force what=text on=%d lc=%ld", tx_on ? 1 : 0, lc);
    }
}

// Before the texture redraw: nothing may have flagged the GUI between the flush and here.
static void dos_gc2_before_redraw(int i, GUIMain &g)
{'''), (
'''        dos_gc2_ok[i] = false;   // the draw loop's late mark covers the whole old rect, as R3 does today
        dos_gc2_mismatch++;
    }
}''',
'''        dos_gc2_ok[i] = false;   // the draw loop's late mark covers the whole old rect, as R3 does today
        dos_gc2_mismatch++;
    }
    dos_lab_gc2_verify_before(i);   // L2G OVERLAY
}'''), (
'''    dos_gc2_pending[i] = 0;''',
'''    dos_lab_gc2_verify_after(i);   // L2G OVERLAY: before the marked rects are reused
    dos_gc2_pending[i] = 0;'''), (
'''    for (int k = 0; k < b->markedn; ++k)
    {
        const Rect r = b->marked[k].R();
        dos_port_dirty_source = kDirtySrc_UiSprite;''',
'''    static int _nomark = -1, _short = -1;   // L2G OVERLAY: controls C1 / C2
    if (_nomark < 0) { _nomark = dos_lab_gc2_env("DOSAGS_LAB_GC2_NOMARK"); _short = dos_lab_gc2_env("DOSAGS_LAB_GC2_SHORT"); }
    for (int k = 0; k < b->markedn; ++k)
    {
        if (_nomark) break;
        Rect r = b->marked[k].R();
        if (_short > 0) { r = Rect(r.Left + _short, r.Top + _short, r.Right - _short, r.Bottom - _short); b->marked[k].Set(r); }
        if (r.IsEmpty()) continue;
        dos_port_dirty_source = kDirtySrc_UiSprite;'''), (
'''// Before the texture redraw: nothing may have flagged the GUI between the flush and here.''',
'''// (the verify reads dos_gc2_marked after a C2 shrink: it then checks the shrunk rects)
// Before the texture redraw: nothing may have flagged the GUI between the flush and here.''')])

edit('Engine/ac/draw.cpp', [(
'''static bool dos_gc2_try(int i, GUIMain &g)
{''',
'''static int dos_lab_gc2_env(const char *n);   // L2G OVERLAY (defined below)
static bool dos_gc2_try(int i, GUIMain &g)
{'''), (
'''#define DOS_GC2_CAP DOS_GC2_MAXC   // the slot cap in force: a GUI with more controls takes the 0371 path (slots_overflow)''',
'''static int dos_lab_gc2_cap()   // L2G OVERLAY: DOSAGS_LAB_GC2_CAP=N forces the slot cap to N (0..16)
{
    static int c = -1;
    if (c < 0) { const char *e = getenv("DOSAGS_LAB_GC2_CAP"); c = (e && *e) ? atoi(e) : DOS_GC2_MAXC;
                 if (c < 0) c = 0; if (c > DOS_GC2_MAXC) c = DOS_GC2_MAXC;
                 if (e && *e) Debug::Printf("DOS-PORT labgc2 cap=%d", c); }
    return c;
}
#define DOS_GC2_CAP dos_lab_gc2_cap()   // L2G OVERLAY''')])

edit('Engine/main/quit.cpp', [(
'''            dos_gc2_report(run_manifest_log);              // DOS-PORT patch 0372
''',
'''            dos_gc2_report(run_manifest_log);              // DOS-PORT patch 0372
            { extern void dos_lab_gc2_report(FILE *); dos_lab_gc2_report(run_manifest_log); }   // L2G OVERLAY
''')])
print('L2G overlay applied')
