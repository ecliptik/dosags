#!/usr/bin/env python3
"""LAB-RB overlay (lab only, never landed): instrumentation over 0001-0369 to attribute MMD's remaining skipped frames.
Applies to vendor/ags in place (uncommitted). First runs R3LAND-2026-11-06's overlay unchanged (apply-overlay-r3land.py:
DOSAGS_LABCLICKS, DOSAGS_LAB_FRAMEHASH, DOSAGS_LAB_CKPT, ...), then adds:
 - DOSAGS_LABCLICKS=GCL: LAB-R2's preset (LAB-L1's 16 GCL clicks), as LAB-R2B's overlay spells it
 - "DOS-PORT rbfull lc= why= at= already= post= fn= pos=": every dos_port_dirty_set_full() call (cap 4000 lines), with
   the caller tag stack (file:line of the invalidate_screen() / invalidate_all_rects() / invalidate_all_camera_rects() /
   construct_game_scene() call, outermost first), whether full was already latched, whether it came after this interval's
   restore (post=1 -> carried into the next frame), the script function running (fn=, innermost) and its script position
 - "DOS-PORT rbpfull lc= why=": at the present, when the frame is pushed with the full latch set (the reason that won)
 - "DOS-PORT rbff lc= scene= is_full= carry_full= why=": once per scene in which R2b's mark fell back on ff_full
 - "DOS-PORT rbslow lc= d= us= ...": every UpdateGameOnce (any depth) whose inclusive wall time is >= DOSAGS_LAB_SLOWMS
   (default 40) ms: per-phase deltas (tick timing scopes; fine ones need fine timing on), lab brackets (FindRoute, GUI
   redraw, sprite load, sound load, asset open, RoomProcessClick: us/calls), full latches, the script functions run in
   that tick (name:us, depth)
Usage: apply-overlay-rb.py VENDOR_AGS_ROOT"""
import os, subprocess, sys
root = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
subprocess.check_call([sys.executable, os.path.join(here, 'apply-overlay-r3land.py'), root])


def edit(rel, pairs):
    p = root + '/' + rel; s = open(p).read()
    for a, b in pairs:
        assert s.count(a) == 1, (rel, a[:80]); s = s.replace(a, b, 1)
    open(p, 'w').write(s)


def prepend(rel, text):
    p = root + '/' + rel; s = open(p).read()
    open(p, 'w').write(text + s)


INC = '#include "util/dos_lab_rb.h"   // RB OVERLAY\n'

open(root + '/Common/util/dos_lab_rb.h', 'w').write('''// RB OVERLAY (lab only): brackets and per-tick script records for LAB-RB.
#ifndef DOS_LAB_RB_H
#define DOS_LAB_RB_H
#ifdef __DJGPP__
#include <time.h>
struct DosLabT { long long us; long n; };
enum { kLabPath = 0, kLabGuiDraw, kLabSprLoad, kLabSndLoad, kLabAsset, kLabRoomClick, kLabCount };
extern DosLabT dos_lab_t[kLabCount];   // defined in Common/ac/spritecache.cpp
struct DosLabScope
{
    int k; uclock_t t0;
    explicit DosLabScope(int k_) : k(k_), t0(uclock()) {}
    ~DosLabScope()
    {
        long long d = (long long)(uclock() - t0) * 1000000LL / UCLOCKS_PER_SEC;
        if (d < 0) d = 0;
        dos_lab_t[k].us += d; dos_lab_t[k].n++;
    }
};
#define DOS_LAB_SCOPE(k) DosLabScope _dos_lab_scope_##k(k)
struct DosLabAcc   // v6: adds the scope's us to a counter
{
    long long &acc; uclock_t t0;
    explicit DosLabAcc(long long &a) : acc(a), t0(uclock()) {}
    ~DosLabAcc() { long long d = (long long)(uclock() - t0) * 1000000LL / UCLOCKS_PER_SEC; if (d > 0) acc += d; }
};
// v6: legacy route finder split, reset by Pathfinding::FindRoute (defined in Engine/ac/route_finder_impl_legacy.cpp)
extern long long dos_lab_rf_irp_us, dos_lab_rf_dij_us, dos_lab_rf_try_us, dos_lab_rf_see_us;
extern long dos_lab_rf_passes, dos_lab_rf_scans, dos_lab_rf_cells, dos_lab_rf_see_n, dos_lab_rf_dij_n, dos_lab_rf_try_n;
struct DosLabFnRec { char name[32]; long us; int depth; };
#define DOS_LAB_FN_CAP 16
extern DosLabFnRec dos_lab_fn_tick[DOS_LAB_FN_CAP];   // defined in Engine/script/script.cpp
extern int dos_lab_fn_tick_n;
extern long dos_lab_full_calls;                       // defined in Engine/ac/draw_software.cpp
#else
#define DOS_LAB_SCOPE(k)
#endif
#endif
''')

# --- GCL preset (LAB-R2B's spelling) ---
edit('Engine/main/game_run.cpp', [(
'''    Debug::Printf("DOS-PORT labclick lc=%ld n=%d x=%d y=%d click=%d", lc, k + 1, dos_lc_x[k], dos_lc_y[k], dos_lc_b[k]);''',
'''    Debug::Printf("DOS-PORT labclick lc=%ld n=%d x=%d y=%d click=%d", lc, k + 1, dos_lc_x[k], dos_lc_y[k], dos_lc_b[k]);
    {   // RB OVERLAY v2: the GUI table once, and the GUI under every lab click
        static bool _rb_dumped = false;
        if (!_rb_dumped)
        {
            _rb_dumped = true;
            for (int g = 0; g < game.numgui; ++g)
                Debug::Printf("DOS-PORT rbgui id=%d x=%d y=%d w=%d h=%d displayed=%d clickable=%d controls=%d", g, guis[g].GetX(),
                    guis[g].GetY(), guis[g].GetWidth(), guis[g].GetHeight(), guis[g].IsDisplayed() ? 1 : 0,
                    guis[g].IsClickable() ? 1 : 0, guis[g].GetControlCount());
            for (int g = 0; g < game.numgui && g < 2; ++g)   // v7: GUI 0 and 1 controls, and the clip option
                for (int c = 0; c < guis[g].GetControlCount(); ++c)
                {
                    GUIObject *o = guis[g].GetControl(c);
                    Debug::Printf("DOS-PORT rbctl gui=%d id=%d type=%d x=%d y=%d w=%d h=%d visible=%d", g, c, (int)guis[g].GetControlType(c),
                        o->GetX(), o->GetY(), o->GetWidth(), o->GetHeight(), o->IsVisible() ? 1 : 0);
                }
            Debug::Printf("DOS-PORT rbclip clipcontrols=%d", game.options[OPT_CLIPGUICONTROLS]);
        }
        int _rb_gui = -1;
        for (int g = game.numgui - 1; g >= 0; --g)
            if (guis[g].IsDisplayed() && guis[g].IsClickable() && dos_lc_x[k] >= guis[g].GetX() && dos_lc_y[k] >= guis[g].GetY() &&
                dos_lc_x[k] < guis[g].GetX() + guis[g].GetWidth() && dos_lc_y[k] < guis[g].GetY() + guis[g].GetHeight())
            { _rb_gui = g; break; }
        Debug::Printf("DOS-PORT rbclick lc=%ld x=%d y=%d gui=%d", lc, dos_lc_x[k], dos_lc_y[k], _rb_gui);
    }'''), (
'''        const char *e = getenv("DOSAGS_LABCLICKS");''',
'''        const char *e = getenv("DOSAGS_LABCLICKS");
        // RB OVERLAY: LAB-R2's preset (LAB-L1's GCL fixture, GCMP's 16 click ticks), as LAB-R2B spells it
        static const char *k_gcl = "6178:250:135,6510:60:135,6974:250:135,7205:60:135,7543:250:135,7890:1:135,8118:40:130,"
            "8519:300:130,8772:40:130,9253:300:130,9566:40:130,9935:300:130,10244:40:130,10722:300:130,11063:40:130,12136:300:130";
        if (e && strcmp(e, "GCL") == 0) e = k_gcl;
        // RB OVERLAY: H = RDMP's 14 post-restore click ticks, with positions chosen to repeat RDMP's game-log actions
        // (room-1 walks to 204,98 / 319,98 / 34,128 / 0,128, GUI 10 x3, room-2 walk to 925,69, GUI 1 x5, room-2 exit at x 319)
        static const char *k_h = "6154:204:98,6409:319:98,6640:160:8,6946:160:8,7315:34:128,7701:0:128,7895:285:69,8231:160:8,"
            "8665:30:165,9070:30:165,9432:30:165,10003:319:101,10648:30:165,11751:30:165";
        if (e && strcmp(e, "H") == 0) e = k_h;''')])

# --- lab brackets ---
edit('Common/ac/spritecache.cpp', [(
'''Bitmap *SpriteCache::LoadSprite(sprkey_t index, bool lock)
{''',
'''Bitmap *SpriteCache::LoadSprite(sprkey_t index, bool lock)
{
    DOS_LAB_SCOPE(kLabSprLoad);   // RB OVERLAY''')])
prepend('Common/ac/spritecache.cpp', '#ifdef __DJGPP__\nDosLabT dos_lab_t[kLabCount];   // RB OVERLAY (global scope)\n#endif\n')
prepend('Common/ac/spritecache.cpp', INC)
prepend('Common/data/assetmanager.cpp', INC)
edit('Common/data/assetmanager.cpp', [(
'''std::unique_ptr<Stream> AssetManager::OpenAsset(const String &asset_name, const String &filter) const
{''',
'''std::unique_ptr<Stream> AssetManager::OpenAsset(const String &asset_name, const String &filter) const
{
    DOS_LAB_SCOPE(kLabAsset);   // RB OVERLAY''')])
prepend('Engine/ac/route_finder.cpp', INC + '#include <stdint.h>\n#include "debug/out.h"\nextern void dos_lab_script_where(char *buf, int n);   // RB OVERLAY\nextern uint32_t get_loop_counter();\n')
edit('Engine/ac/route_finder.cpp', [(
'''    int move_speed_x, int move_speed_y, bool exact_dest, bool ignore_walls)
{
    std::vector<Point> path;''',
'''    int move_speed_x, int move_speed_y, bool exact_dest, bool ignore_walls)
{
    DOS_LAB_SCOPE(kLabPath);   // RB OVERLAY
    const uclock_t _rb_t0 = uclock();   // RB OVERLAY: v2 rbroute line
    std::vector<Point> path;
    struct RbRoute { const uclock_t t0; int sx, sy, dx, dy; const std::vector<Point> &p; ~RbRoute()
    {
        long long d = (long long)(uclock() - t0) * 1000000LL / UCLOCKS_PER_SEC; if (d < 0) d = 0;
        if (d >= 5000)
        {
            char w[128]; dos_lab_script_where(w, sizeof(w));
            AGS::Common::Debug::Printf("DOS-PORT rbroute lc=%ld us=%ld src=%d,%d dst=%d,%d nodes=%d irp=%ld dij=%ld/%ld passes=%ld scans=%ld cells=%ld try=%ld/%ld see=%ld/%ld %s",
                (long)get_loop_counter(), (long)d, sx, sy, dx, dy, (int)p.size(), (long)dos_lab_rf_irp_us, (long)dos_lab_rf_dij_us,
                dos_lab_rf_dij_n, dos_lab_rf_passes, dos_lab_rf_scans, dos_lab_rf_cells, (long)dos_lab_rf_try_us, dos_lab_rf_try_n,
                (long)dos_lab_rf_see_us, dos_lab_rf_see_n, w);
        }
    } } _rb_route{_rb_t0, srcx, srcy, dstx, dsty, path};
    dos_lab_rf_irp_us = dos_lab_rf_dij_us = dos_lab_rf_try_us = dos_lab_rf_see_us = 0;   // v6
    dos_lab_rf_passes = dos_lab_rf_scans = dos_lab_rf_cells = dos_lab_rf_see_n = dos_lab_rf_dij_n = dos_lab_rf_try_n = 0;''')])
prepend('Engine/media/audio/sound.cpp', INC)
edit('Engine/media/audio/sound.cpp', [(
'''std::unique_ptr<SoundClip> load_sound_clip(const AssetPath &apath, const char *extension_hint, bool loop)
{''',
'''std::unique_ptr<SoundClip> load_sound_clip(const AssetPath &apath, const char *extension_hint, bool loop)
{
    DOS_LAB_SCOPE(kLabSndLoad);   // RB OVERLAY''')])
prepend('Engine/ac/global_game.cpp', INC)
edit('Engine/ac/global_game.cpp', [(
'''void RoomProcessClick(int xx, int yy, int mood)
{''',
'''void RoomProcessClick(int xx, int yy, int mood)
{
    DOS_LAB_SCOPE(kLabRoomClick);   // RB OVERLAY''')])

# --- v6: legacy route finder split ---
prepend('Engine/ac/route_finder_impl_legacy.cpp', INC + '''#ifdef __DJGPP__
long long dos_lab_rf_irp_us = 0, dos_lab_rf_dij_us = 0, dos_lab_rf_try_us = 0, dos_lab_rf_see_us = 0;   // RB OVERLAY v6
long dos_lab_rf_passes = 0, dos_lab_rf_scans = 0, dos_lab_rf_cells = 0, dos_lab_rf_see_n = 0, dos_lab_rf_dij_n = 0, dos_lab_rf_try_n = 0;
#endif
''')
edit('Engine/ac/route_finder_impl_legacy.cpp', [(
'''int can_see_from(const Bitmap *wallscreen, int x1, int y1, int x2, int y2)
{''',
'''int can_see_from(const Bitmap *wallscreen, int x1, int y1, int x2, int y2)
{
  DosLabAcc _rb_see(dos_lab_rf_see_us); dos_lab_rf_see_n++;   // RB OVERLAY v6'''), (
'''static int is_route_possible(const Bitmap *wallscreen, int fromx, int fromy, int tox, int toy, const LegacyRouteFinder::PathfinderConfig &pfc)
{''',
'''static int is_route_possible(const Bitmap *wallscreen, int fromx, int fromy, int tox, int toy, const LegacyRouteFinder::PathfinderConfig &pfc)
{
  DosLabAcc _rb_irp(dos_lab_rf_irp_us);   // RB OVERLAY v6'''), (
'''static int find_route_dijkstra(const Bitmap *wallscreen, int fromx, int fromy, int destx, int desty, const LegacyRouteFinder::PathfinderConfig &pfc)
{''',
'''static int find_route_dijkstra(const Bitmap *wallscreen, int fromx, int fromy, int destx, int desty, const LegacyRouteFinder::PathfinderConfig &pfc)
{
  DosLabAcc _rb_dij(dos_lab_rf_dij_us); dos_lab_rf_dij_n++;   // RB OVERLAY v6'''), (
'''  while (foundAnswer < 0) {''',
'''  while (foundAnswer < 0) {
    dos_lab_rf_passes++; dos_lab_rf_scans += iteration; dos_lab_rf_cells = iteration;   // RB OVERLAY v6'''), (
'''  if (try_this_square(wallscreen, srcx, srcy, tox[0], toy[0]) == 0)''',
'''  int _rb_tr; { DosLabAcc _rb_t(dos_lab_rf_try_us); dos_lab_rf_try_n++; _rb_tr = try_this_square(wallscreen, srcx, srcy, tox[0], toy[0]); }   // RB OVERLAY v6
  if (_rb_tr == 0)''')])

# --- caller tags: draw.h / draw_software.h macros, parenthesized definitions ---
edit('Engine/ac/draw.h', [(
'''void invalidate_screen();''',
'''void invalidate_screen();
#ifdef __DJGPP__   // RB OVERLAY: caller tag around every call
void dos_lab_tag_push(const char *f, int l);
void dos_lab_tag_pop();
#define invalidate_screen() (dos_lab_tag_push(__FILE__, __LINE__), invalidate_screen(), dos_lab_tag_pop())
#endif'''), (
'''void construct_game_scene(bool full_redraw = false);''',
'''void construct_game_scene(bool full_redraw = false);
#ifdef __DJGPP__   // RB OVERLAY
#define construct_game_scene(...) (dos_lab_tag_push(__FILE__, __LINE__), construct_game_scene(__VA_ARGS__), dos_lab_tag_pop())
#endif'''), (
'''void invalidate_rect(int x1, int y1, int x2, int y2, bool in_room);''',
'''void invalidate_rect(int x1, int y1, int x2, int y2, bool in_room);
#ifdef __DJGPP__   // RB OVERLAY v4
#define invalidate_rect(...) (dos_lab_tag_push(__FILE__, __LINE__), invalidate_rect(__VA_ARGS__), dos_lab_tag_pop())
#endif''')])
edit('Engine/ac/draw_software.h', [(
'''void invalidate_all_rects();''',
'''void invalidate_all_rects();
#ifdef __DJGPP__   // RB OVERLAY
void dos_lab_tag_push(const char *f, int l);
void dos_lab_tag_pop();
#define invalidate_all_rects() (dos_lab_tag_push(__FILE__, __LINE__), invalidate_all_rects(), dos_lab_tag_pop())
#endif'''), (
'''void invalidate_all_camera_rects(int view_index);''',
'''void invalidate_all_camera_rects(int view_index);
#ifdef __DJGPP__   // RB OVERLAY
#define invalidate_all_camera_rects(v) (dos_lab_tag_push(__FILE__, __LINE__), invalidate_all_camera_rects(v), dos_lab_tag_pop())
#endif''')])
edit('Engine/ac/draw.cpp', [(
'''void invalidate_rect(int x1, int y1, int x2, int y2, bool in_room)
{''',
'''void (invalidate_rect)(int x1, int y1, int x2, int y2, bool in_room)   // RB OVERLAY v4
{'''), (
'''                invalidate_sprite(t.X, t.Y, t.DDB, in_room);''',
'''                if ((long)t.DDB->GetWidth() * t.DDB->GetHeight() >= 20000)   // RB OVERLAY v4
                    Debug::Printf("DOS-PORT rbbig lc=%ld in_room=%d x=%d y=%d w=%d h=%d drawindex=%u char=%d skipinv=%d", (long)get_loop_counter(),
                        in_room ? 1 : 0, t.X, t.Y, t.DDB->GetWidth(), t.DDB->GetHeight(), (unsigned)t.DrawIndex, t.DosCharId, t.SkipInvalidate ? 1 : 0);
                invalidate_sprite(t.X, t.Y, t.DDB, in_room);'''), (
'''void invalidate_screen()
{''',
'''void (invalidate_screen)()   // RB OVERLAY: parenthesized past the tag macro
{'''), (
'''void construct_game_scene(bool full_redraw)
{''',
'''void (construct_game_scene)(bool full_redraw)   // RB OVERLAY
{'''), (
'''        else if (dos_port_dirty.is_full || dos_port_dirty.carry_full)  { dos_cr_ff_full++; dos_cr_ff++; }''',
'''        else if (dos_port_dirty.is_full || dos_port_dirty.carry_full)
        {
            dos_cr_ff_full++; dos_cr_ff++;
            static long _rb_last = -1;   // RB OVERLAY: once per scene
            if (_rb_last != dos_cr_scene)
            {
                _rb_last = dos_cr_scene;
                Debug::Printf("DOS-PORT rbff lc=%ld scene=%ld is_full=%d carry_full=%d why=%s", (long)get_loop_counter(),
                    dos_cr_scene, dos_port_dirty.is_full ? 1 : 0, dos_port_dirty.carry_full ? 1 : 0,
                    dos_port_dirty.full_reason ? dos_port_dirty.full_reason : "-");
            }
        }'''), (
'''                    if (draw_with_controls)
                        gui.DrawWithControls(gbg.Bmp.get());
                    else
                        gui.DrawSelf(gbg.Bmp.get());''',
'''                    {
                    { extern unsigned long dos_lab_gui_mask; if (index < 32) dos_lab_gui_mask |= 1UL << index; }   // RB OVERLAY v3
                    DOS_LAB_SCOPE(kLabGuiDraw);   // RB OVERLAY
                    if (draw_with_controls)
                        gui.DrawWithControls(gbg.Bmp.get());
                    else
                        gui.DrawSelf(gbg.Bmp.get());
                    }''')])
prepend('Engine/ac/draw.cpp', INC)
edit('Engine/ac/draw_software.cpp', [(
'''void invalidate_all_rects()
{''',
'''void (invalidate_all_rects)()   // RB OVERLAY
{'''), (
'''void invalidate_all_camera_rects(int view_index)
{''',
'''void (invalidate_all_camera_rects)(int view_index)   // RB OVERLAY
{'''), (
'''void dos_port_dirty_set_full(const char *why)
{''',
'''// RB OVERLAY: caller tags and the set_full logger
static const char *dos_lab_tag_f[8]; static int dos_lab_tag_l[8]; static int dos_lab_tag_n = 0;
void dos_lab_tag_push(const char *f, int l)
{
    if (dos_lab_tag_n < 8) { dos_lab_tag_f[dos_lab_tag_n] = f; dos_lab_tag_l[dos_lab_tag_n] = l; }
    dos_lab_tag_n++;
}
void dos_lab_tag_pop() { if (dos_lab_tag_n > 0) dos_lab_tag_n--; }
static const char *dos_lab_short(const char *f) { const char *p = strstr(f, "Engine/"); return p ? p + 7 : f; }
extern void dos_lab_script_where(char *buf, int n);
extern uint32_t get_loop_counter();
long dos_lab_full_calls = 0;
static void dos_lab_full_note(const char *why)
{
    dos_lab_full_calls++;
    if (dos_lab_full_calls > 4000) return;
    char tags[200]; tags[0] = 0;
    const int n = dos_lab_tag_n < 8 ? dos_lab_tag_n : 8;
    for (int i = 0; i < n; ++i)
    {
        const size_t l = strlen(tags);
        snprintf(tags + l, sizeof(tags) - l, "%s%s:%d", i ? ">" : "", dos_lab_short(dos_lab_tag_f[i]), dos_lab_tag_l[i]);
    }
    if (n == 0) snprintf(tags, sizeof(tags), "-");
    char w[128]; dos_lab_script_where(w, sizeof(w));
    Debug::Printf("DOS-PORT rbfull lc=%ld why=\\"%s\\" at=%s already=%d post=%d %s", (long)get_loop_counter(), why, tags,
        dos_port_dirty.is_full ? 1 : 0, dos_port_dirty.restore_seen ? 1 : 0, w);
}

void dos_port_dirty_set_full(const char *why)
{
    dos_lab_full_note(why);   // RB OVERLAY'''), (
'''void dos_port_dirty_add_screen(int x1, int y1, int x2, int y2)
{''',
'''void dos_lab_big_note(int x1, int y1, int x2, int y2);   // RB OVERLAY v4
void dos_port_dirty_add_screen(int x1, int y1, int x2, int y2)
{
    dos_lab_big_note(x1, y1, x2, y2);   // RB OVERLAY v4'''), (
'''void dos_port_dirty_frame_reset()
{''',
'''void dos_lab_big_note(int x1, int y1, int x2, int y2)   // RB OVERLAY v4: marks >= 20000 px, with the caller tags
{
    static long _n = 0;
    if ((long)(x2 - x1 + 1) * (y2 - y1 + 1) < 20000 || ++_n > 3000) return;
    char tags[200]; tags[0] = 0;
    const int n = dos_lab_tag_n < 8 ? dos_lab_tag_n : 8;
    for (int i = 0; i < n; ++i)
    {
        const size_t l = strlen(tags);
        snprintf(tags + l, sizeof(tags) - l, "%s%s:%d", i ? ">" : "", dos_lab_short(dos_lab_tag_f[i]), dos_lab_tag_l[i]);
    }
    Debug::Printf("DOS-PORT rbmark lc=%ld box=%d,%d-%d,%d src=%d post=%d at=%s", (long)get_loop_counter(), x1, y1, x2, y2,
        dos_port_dirty_source, dos_port_dirty.restore_seen ? 1 : 0, n ? tags : "-");
}

void dos_port_dirty_frame_reset()
{''')])
prepend('Engine/ac/draw_software.cpp', INC)

edit('Engine/gfx/ali3dsw.cpp', [(
'''    dos_port_dirty_merge_carry();   // patch 0193: last interval's marks are repainted by THIS frame's restore''',
'''    dos_port_dirty_merge_carry();   // patch 0193: last interval's marks are repainted by THIS frame's restore
    if (dos_port_dirty.is_full)     // RB OVERLAY
        Debug::Printf("DOS-PORT rbpfull lc=%ld why=%s", (long)get_loop_counter(),
            dos_port_dirty.full_reason ? dos_port_dirty.full_reason : "-");''')])

# --- script function records (script.cpp) ---
prepend('Engine/script/script.cpp', INC)
edit('Engine/script/script.cpp', [(
'''static bool DoRunScriptFuncCantBlock(ccInstance *sci, NonBlockingScriptFunction* funcToRun, bool hasTheFunc)
{''',
'''#ifdef __DJGPP__
// RB OVERLAY: the running script function stack and this tick's function records
DosLabFnRec dos_lab_fn_tick[DOS_LAB_FN_CAP]; int dos_lab_fn_tick_n = 0;
static const char *dos_lab_fn_stack[16]; static int dos_lab_fn_depth = 0;
struct DosLabFnScope
{
    const char *nm; uclock_t t0;
    explicit DosLabFnScope(const char *n) : nm(n), t0(uclock())
    { if (dos_lab_fn_depth < 16) dos_lab_fn_stack[dos_lab_fn_depth] = n; dos_lab_fn_depth++; }
    ~DosLabFnScope()
    {
        dos_lab_fn_depth--;
        long long d = (long long)(uclock() - t0) * 1000000LL / UCLOCKS_PER_SEC; if (d < 0) d = 0;
        if (d >= 1000 && dos_lab_fn_tick_n < DOS_LAB_FN_CAP)
        {
            DosLabFnRec &r = dos_lab_fn_tick[dos_lab_fn_tick_n++];
            snprintf(r.name, sizeof(r.name), "%s", nm); r.us = (long)d; r.depth = dos_lab_fn_depth;
        }
    }
};
void dos_lab_script_where(char *buf, int n)
{
    const char *fn = dos_lab_fn_depth > 0 ? dos_lab_fn_stack[(dos_lab_fn_depth < 16 ? dos_lab_fn_depth : 16) - 1] : "-";
    ScriptPosition pos;
    if (dos_lab_fn_depth > 0 && get_script_position(pos))
        snprintf(buf, n, "fn=%s pos=%s:%d", fn, pos.Section.GetCStr(), pos.Line);
    else
        snprintf(buf, n, "fn=%s pos=-", fn);
}
#endif

static bool DoRunScriptFuncCantBlock(ccInstance *sci, NonBlockingScriptFunction* funcToRun, bool hasTheFunc)
{'''), (
'''    ccInstError result = sci->CallScriptFunction(funcToRun->FunctionName, funcToRun->ParamCount, funcToRun->Params);''',
'''#ifdef __DJGPP__
    DosLabFnScope _dos_lab_fn(funcToRun->FunctionName.GetCStr());   // RB OVERLAY
#endif
    ccInstError result = sci->CallScriptFunction(funcToRun->FunctionName, funcToRun->ParamCount, funcToRun->Params);'''), (
'''    const ccInstError inst_ret = curscript->Inst->CallScriptFunction(tsname, numParam, params);''',
'''#ifdef __DJGPP__
    DosLabFnScope _dos_lab_fn(tsname.GetCStr());   // RB OVERLAY
#endif
    const ccInstError inst_ret = curscript->Inst->CallScriptFunction(tsname, numParam, params);''')])

# --- v7: label text changes (length only; the text is game data) ---
edit('Engine/ac/label.cpp', [(
'''    if (labl->GetText() != newtx) {
        labl->SetText(newtx);''',
'''    if (labl->GetText() != newtx) {
#ifdef __DJGPP__
        { extern void dos_lab_label_note(int, int, int, int); dos_lab_label_note(labl->GetParentID(), labl->GetID(),
            (int)labl->GetText().GetLength(), (int)strlen(newtx)); }   // RB OVERLAY v7
#endif
        labl->SetText(newtx);''')])
prepend('Engine/ac/label.cpp', '#include <string.h>\n')

# --- v5: who marks a GUI changed (codes: 1 GUIMain::MarkChanged, 2 MarkControlChanged, 3 NotifyControlPosition,
#     4 NotifyControlState with mark_changed, 10 GUIObject::MarkChanged obj=control id) ---
prepend('Common/gui/guimain.cpp', '#ifdef __DJGPP__\nvoid (*dos_lab_guimark_hook)(int, int, int) = nullptr;   // RB OVERLAY v5\n#endif\n')
edit('Common/gui/guimain.cpp', [(
'''void GUIMain::MarkChanged()
{''',
'''void GUIMain::MarkChanged()
{
#ifdef __DJGPP__
    if (dos_lab_guimark_hook) dos_lab_guimark_hook(_id, 1, -1);   // RB OVERLAY v5
#endif'''), (
'''void GUIMain::MarkControlChanged()
{''',
'''void GUIMain::MarkControlChanged()
{
#ifdef __DJGPP__
    if (dos_lab_guimark_hook) dos_lab_guimark_hook(_id, 2, -1);   // RB OVERLAY v5
#endif'''), (
'''void GUIMain::NotifyControlPosition()
{''',
'''void GUIMain::NotifyControlPosition()
{
#ifdef __DJGPP__
    if (dos_lab_guimark_hook) dos_lab_guimark_hook(_id, 3, -1);   // RB OVERLAY v5
#endif'''), (
'''void GUIMain::NotifyControlState(int objid, bool mark_changed)
{''',
'''void GUIMain::NotifyControlState(int objid, bool mark_changed)
{
#ifdef __DJGPP__
    if (dos_lab_guimark_hook && mark_changed) dos_lab_guimark_hook(_id, 4, objid);   // RB OVERLAY v5
#endif''')])
prepend('Engine/gui/gui_engine.cpp', '#ifdef __DJGPP__\nextern void (*dos_lab_guimark_hook)(int, int, int);   // RB OVERLAY v5\n#endif\n')
edit('Engine/gui/gui_engine.cpp', [(
'''void GUIObject::MarkChanged()
{''',
'''void GUIObject::MarkChanged()
{
#ifdef __DJGPP__
    if (dos_lab_guimark_hook) dos_lab_guimark_hook(_parentID, 10, _id);   // RB OVERLAY v5
#endif''')])
edit('Engine/script/script.cpp', [(
'''static bool DoRunScriptFuncCantBlock(ccInstance *sci, NonBlockingScriptFunction* funcToRun, bool hasTheFunc)
{''',
'''extern void (*dos_lab_guimark_hook)(int, int, int);   // RB OVERLAY v5
extern uint32_t get_loop_counter();
static void dos_lab_guimark(int g, int code, int obj)
{
    static long n = 0;
    if (++n > 4000) return;
    char w[128]; dos_lab_script_where(w, sizeof(w));
    Debug::Printf("DOS-PORT rbguimark lc=%ld gui=%d code=%d obj=%d %s", (long)get_loop_counter(), g, code, obj, w);
}
void dos_lab_label_note(int g, int c, int oldlen, int newlen)   // RB OVERLAY v7
{
    static long n = 0;
    if (++n > 4000) return;
    char w[128]; dos_lab_script_where(w, sizeof(w));
    Debug::Printf("DOS-PORT rblabel lc=%ld gui=%d ctrl=%d oldlen=%d newlen=%d %s", (long)get_loop_counter(), g, c, oldlen, newlen, w);
}
static struct DosLabGuimarkInit { DosLabGuimarkInit() { dos_lab_guimark_hook = dos_lab_guimark; } } dos_lab_guimark_init;

static bool DoRunScriptFuncCantBlock(ccInstance *sci, NonBlockingScriptFunction* funcToRun, bool hasTheFunc)
{''')])

# --- per-tick slow-tick breakdown (game_run.cpp) ---
PH = ['script_vm', 'rep_exec_vm', 'process_events_dispatch', 'game_objects_update', 'input_handling', 'room_check',
      'gui_poll', 'gui_context_cursor', 'ground_interactions', 'drawable_object_states', 'scene_construct',
      'render_to_screen_pertick', 'wait_next_frame', 'audio_sync', 'persistent_anims', 'end_of_tick', 'rep_exec_wrapper',
      'objects_scale', 'input_poll', 'sc_room_view', 'sc_ui_view', 'sc_overlays', 'sc_prep_chars', 'sc_draw_list',
      'sc_viewports', 'bg_restore', 'rb_sprite_time', 'present_update_window']
SH = ['script', 'repvm', 'events', 'objs', 'input', 'room', 'guipoll', 'gctx', 'ground', 'dstates', 'scene', 'render',
      'wait', 'audio', 'anims', 'eot', 'repw', 'oscale', 'ipoll', 'sroom', 'sui', 'sovl', 'schars', 'sdraw', 'svp', 'bgr',
      'rbspr', 'pres']
snap = '\n'.join('        s[%d] = t.%s.total_us;' % (i, p) for i, p in enumerate(PH))
delta = ' '.join('%s=%%ld' % n for n in SH)
dargs = ', '.join('(long)(t.%s.total_us - s[%d])' % (p, i) for i, p in enumerate(PH))
edit('Engine/main/game_run.cpp', [(
"void UpdateGameOnce(bool do_controls, IDriverDependantBitmap *extra_ddb, int extra_x, int extra_y, bool skip_render_and_wait)\n{",
'''#ifdef __DJGPP__
// RB OVERLAY: per-UpdateGameOnce breakdown of slow ticks (DOSAGS_LAB_SLOWMS, default 40 ms, inclusive wall time)
static int dos_lab_tick_depth = 0;
unsigned long dos_lab_gui_mask = 0;   // v3: GUIs redrawn (bit = index), reset per top-level tick
static long dos_lab_slow_us = -1;
struct DosLabTickScope
{
    long long s[%d]; long long l[kLabCount]; long ln[kLabCount]; uclock_t t0; int fn0; long full0; long lc0; long long px0, pp0;
    DosLabTickScope()
    {
        if (dos_lab_slow_us < 0) { const char *e = getenv("DOSAGS_LAB_SLOWMS"); dos_lab_slow_us = (e && atol(e) > 0) ? atol(e) * 1000 : 40000; }
        dos_lab_tick_depth++;
        if (dos_lab_tick_depth == 1) { dos_lab_fn_tick_n = 0; dos_lab_gui_mask = 0; }
        px0 = dos_port_tick_timing.rb_sprite_px; pp0 = dos_port_dirty.px_narrow + dos_port_dirty.px_full;
        const DosPortTickTiming &t = dos_port_tick_timing;
%s
        for (int k = 0; k < kLabCount; ++k) { l[k] = dos_lab_t[k].us; ln[k] = dos_lab_t[k].n; }
        fn0 = dos_lab_fn_tick_n; full0 = dos_lab_full_calls; lc0 = (long)get_loop_counter();
        t0 = uclock();
    }
    ~DosLabTickScope()
    {
        long long us = (long long)(uclock() - t0) * 1000000LL / UCLOCKS_PER_SEC; if (us < 0) us = 0;
        if (us >= dos_lab_slow_us || dos_lab_t[kLabGuiDraw].n != ln[kLabGuiDraw] || dos_lab_full_calls != full0 ||
            dos_lab_t[kLabPath].n != ln[kLabPath])   // v2: also every tick with a GUI redraw, a full latch or a FindRoute
        {
            const DosPortTickTiming &t = dos_port_tick_timing;
            char fns[400]; fns[0] = 0;
            for (int i = fn0; i < dos_lab_fn_tick_n; ++i)
            {
                const size_t len = strlen(fns);
                snprintf(fns + len, sizeof(fns) - len, "%%s%%s:%%ld@%%d", i > fn0 ? "," : "", dos_lab_fn_tick[i].name,
                         dos_lab_fn_tick[i].us, dos_lab_fn_tick[i].depth);
            }
            Debug::Printf("DOS-PORT rbslow lc=%%ld d=%%d us=%%ld %s path=%%ld/%%ld gui=%%ld/%%ld spr=%%ld/%%ld snd=%%ld/%%ld asset=%%ld/%%ld rclick=%%ld/%%ld full=%%ld guis=%%lx sprpx=%%ld prespx=%%ld fn=%%s",
                lc0, dos_lab_tick_depth, (long)us, %s,
                (long)(dos_lab_t[kLabPath].us - l[kLabPath]), dos_lab_t[kLabPath].n - ln[kLabPath],
                (long)(dos_lab_t[kLabGuiDraw].us - l[kLabGuiDraw]), dos_lab_t[kLabGuiDraw].n - ln[kLabGuiDraw],
                (long)(dos_lab_t[kLabSprLoad].us - l[kLabSprLoad]), dos_lab_t[kLabSprLoad].n - ln[kLabSprLoad],
                (long)(dos_lab_t[kLabSndLoad].us - l[kLabSndLoad]), dos_lab_t[kLabSndLoad].n - ln[kLabSndLoad],
                (long)(dos_lab_t[kLabAsset].us - l[kLabAsset]), dos_lab_t[kLabAsset].n - ln[kLabAsset],
                (long)(dos_lab_t[kLabRoomClick].us - l[kLabRoomClick]), dos_lab_t[kLabRoomClick].n - ln[kLabRoomClick],
                dos_lab_full_calls - full0, dos_lab_gui_mask, (long)(t.rb_sprite_px - px0),
                (long)(dos_port_dirty.px_narrow + dos_port_dirty.px_full - pp0), fns[0] ? fns : "-");
        }
        dos_lab_tick_depth--;
    }
};
#endif

void UpdateGameOnce(bool do_controls, IDriverDependantBitmap *extra_ddb, int extra_x, int extra_y, bool skip_render_and_wait)
{''' % (len(PH), snap, delta, dargs)), (
'''    DosTickStallScope _dos_tick_stall_scope; // patch 0093''',
'''    DosLabTickScope _dos_lab_tick_scope;     // RB OVERLAY: declared first, so it closes last
    DosTickStallScope _dos_tick_stall_scope; // patch 0093''')])
prepend('Engine/main/game_run.cpp', INC)
print('RB overlay applied')
