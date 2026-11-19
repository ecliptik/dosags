#!/usr/bin/env python3
"""Lab gate overlay for patch 0369 R2 (DOSAGS_CHAR_REUSE) -- never landed. Applies to vendor/ags in place (uncommitted), over
0001-0368 + lever-r2b.py. First runs R3LAND-2026-11-06's overlay unchanged (apply-overlay-r3land.py: DOSAGS_LAB_FRAMEHASH,
DOSAGS_LABCLICKS, DOSAGS_LAB_CKPT, DOSAGS_LAB_GUISKIP_BREAK, DOSAGS_LAB_FORCE_WHOLE, DOSAGS_LAB_NOGUARD, DOSAGS_LAB_SPANMAX,
DOSAGS_LAB_SPANPROBE, DOSAGS_LAB_NOCOARSE), then adds:
 - DOSAGS_LABCLICKS=GCL: LAB-R2's preset, LAB-L1's 16 GCL clicks; =G / =V: R3LAND's fixture G / V clicks and hovers
   (presets keep RUN.BAT's SETs short)
 - DOSAGS_LAB_CR_VERIFY=1: every R2a reuse also rebuilds the image the old way (cached image re-copied into a scratch
   bitmap, the walk-behind crop-out run on it) and compares it byte for byte with the reused one
 - controls: DOSAGS_LAB_CR_NODRAW=1 (i) an R2b character is not drawn at all (no per-box redraw);
             DOSAGS_LAB_CR_NOBASEL=1 (ii) the key ignores the baseline and walk_behind_baselines_changed
 - forcings (lab-only, render-only, the same in every arm):
     DOSAGS_LAB_CR_TOGGLE=N[:ch]  character ch (default 1) is not drawn on every Nth scene (as if turned off)
     DOSAGS_LAB_CR_CAM=N[:m]      every Nth scene: m=0 (default) invalidate_screen(), what on_roomcamera_changed does on a
                                  camera move; m=1 the room camera moved by 1 px (where the room is wider than it)
     DOSAGS_LAB_CR_BASEL=N[:ch]   character ch's (default 0) draw baseline +1000 on scenes where (scene / N) is odd
   0366's latch is forced with R3LAND's DOSAGS_LAB_FORCE_WHOLE=N (a whole-surface restore every Nth room restore).
 - guards disabled (each a control for one forcing): DOSAGS_LAB_CR_NOMARK=1 (rule (1)'s old-rect marks counted, not
   made), DOSAGS_LAB_CR_NOLATCH=1 (R2b ignores 0366's latch at the mark and in the driver), DOSAGS_LAB_CR_NOCAM=1 (R2b
   ignores a camera move / whole-surface invalidation at the mark and in the driver)
 - DOSAGS_LAB_TK=1 (instrumented flavour): lab TICKS.BIN kinds 7 wait, 8 sc_prep_chars, 10 bg_restore, 9 character blit us
   per pass, 14 character blit px per pass, 13 rb_sprite_time us per pass (LAB-R2's numbering)
 - DOSAGS_LAB_CKPT also prints "DOS-PORT labck c=cr lc= ..." (charreuse counters, sc_prep_chars, bg_restore, char blits)
 - "DOS-PORT labroom ..." once per room (size, viewport, camera); "DOS-PORT charreuse_lab ..." after charreuse_final
Usage: apply-overlay-r2b.py VENDOR_AGS_ROOT"""
import os, subprocess, sys
root = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
subprocess.check_call([sys.executable, os.path.join(here, 'apply-overlay-r3land.py'), root])
def edit(rel, pairs):
    p = root + '/' + rel; s = open(p).read()
    for a, b in pairs:
        assert s.count(a) == 1, (rel, a[:80]); s = s.replace(a, b, 1)
    open(p, 'w').write(s)

edit('Engine/main/game_run.cpp', [(
'''        const char *e = getenv("DOSAGS_LABCLICKS");''',
'''        const char *e = getenv("DOSAGS_LABCLICKS");
        // R2B OVERLAY: LAB-R2's preset (LAB-L1's GCL fixture, GCMP's 16 click ticks)
        static const char *k_gcl = "6178:250:135,6510:60:135,6974:250:135,7205:60:135,7543:250:135,7890:1:135,8118:40:130,"
            "8519:300:130,8772:40:130,9253:300:130,9566:40:130,9935:300:130,10244:40:130,10722:300:130,11063:40:130,12136:300:130";
        if (e && strcmp(e, "GCL") == 0) e = k_gcl;
        // R2B OVERLAY: R3LAND's fixtures G and V (their clicks and hovers, spelled out in R3LAND's lane scripts)
        static const char *k_g = "5600:160:150:0,5700:100:180:0,5800:290:170:0,5900:160:100:0,6000:60:135,6400:250:135,"
            "6800:1:135,7100:60:160:0,7200:200:190:0,7300:160:80:0,7500:40:130,7900:300:130,8050:150:150:0,8150:150:60:0";
        static const char *k_v = "6000:60:135,6400:250:135,6800:1:135,7000:160:80:0,7400:65:166:0,7800:65:166,8200:200:170:0,"
            "8600:300:185:0,9000:25:155:0,9050:65:166:0,9100:110:178:0,9150:25:166:0,9200:65:178:0,9250:110:155:0";
        if (e && strcmp(e, "G") == 0) e = k_g;
        if (e && strcmp(e, "V") == 0) e = k_v;'''), (
'''        Debug::Printf("DOS-PORT labck lc=%ld rbspr_us=%lld rbspr_calls=%ld rts_us=%lld rts_calls=%ld", (long)get_loop_counter(),
            dos_port_tick_timing.rb_sprite_time.total_us, dos_port_tick_timing.rb_sprite_time.calls,
            dos_port_tick_timing.render_to_screen_pertick.total_us, dos_port_tick_timing.render_to_screen_pertick.calls);''',
'''        Debug::Printf("DOS-PORT labck lc=%ld rbspr_us=%lld rbspr_calls=%ld rts_us=%lld rts_calls=%ld", (long)get_loop_counter(),
            dos_port_tick_timing.rb_sprite_time.total_us, dos_port_tick_timing.rb_sprite_time.calls,
            dos_port_tick_timing.render_to_screen_pertick.total_us, dos_port_tick_timing.render_to_screen_pertick.calls);
        { extern void dos_lab_cr_ckpt(long); dos_lab_cr_ckpt((long)get_loop_counter()); }   // R2B OVERLAY''')])

edit('Engine/ac/timer.cpp', [(
'''    DosPortTickScope _dos_port_wait_scope(dos_port_tick_timing.wait_next_frame);''',
'''    extern int dos_lab_tk();   // R2B OVERLAY: kind 7
    DosPortTickScope _dos_port_wait_scope(dos_port_tick_timing.wait_next_frame, dos_lab_tk() ? 7 : 0);''')])

edit('Engine/ac/draw_software.cpp', [(
'''    DosPortTickScope _dp_bg(dos_port_tick_timing.bg_restore);''',
'''    extern int dos_lab_tk();   // R2B OVERLAY: kind 10
    DosPortTickScope _dp_bg(dos_port_tick_timing.bg_restore, dos_lab_tk() ? 10 : 0);''')])

edit('Engine/ac/draw.cpp', [(
# env helpers, ahead of the lever block
'''struct DosCrKey
{''',
'''// R2B OVERLAY: lab knobs (env, read once)
static int dos_lab_env(const char *n, int &v) { if (v < 0) { const char *e = getenv(n); v = (e && e[0] == '1') ? 1 : 0; } return v; }
static int dos_lab_cr_nodraw_v = -1, dos_lab_cr_nobasel_v = -1, dos_lab_cr_nomark_v = -1, dos_lab_cr_nolatch_v = -1;
static int dos_lab_cr_nocam_v = -1, dos_lab_cr_verify_v = -1, dos_lab_tk_v = -1;
static int dos_lab_cr_nodraw() { return dos_lab_env("DOSAGS_LAB_CR_NODRAW", dos_lab_cr_nodraw_v); }
static int dos_lab_cr_nobasel() { return dos_lab_env("DOSAGS_LAB_CR_NOBASEL", dos_lab_cr_nobasel_v); }
static int dos_lab_cr_nomark() { return dos_lab_env("DOSAGS_LAB_CR_NOMARK", dos_lab_cr_nomark_v); }
int dos_lab_cr_nolatch() { return dos_lab_env("DOSAGS_LAB_CR_NOLATCH", dos_lab_cr_nolatch_v); }
int dos_lab_cr_nocam() { return dos_lab_env("DOSAGS_LAB_CR_NOCAM", dos_lab_cr_nocam_v); }
static int dos_lab_cr_verify() { return dos_lab_env("DOSAGS_LAB_CR_VERIFY", dos_lab_cr_verify_v); }
int dos_lab_tk()
{
#ifdef DOSAGS_RELEASE
    return 0;
#else
    return dos_lab_env("DOSAGS_LAB_TK", dos_lab_tk_v);
#endif
}
long dos_lab_cr_nodraw_n = 0, dos_lab_cr_nomark_n = 0, dos_lab_cr_vchecks = 0, dos_lab_cr_vmismatch = 0;
long dos_lab_cr_toggles = 0, dos_lab_cr_basel_n = 0, dos_lab_cr_cam_n = 0, dos_lab_cr_cam_moves = 0;
long long dos_lab_cr_vpx = 0;
struct DosCrKey
{'''), (
'''    dos_port_dirty_source = kDirtySrc_RoomSprite;
    invalidate_rect(r.rx, r.ry, r.rx + r.rw, r.ry + r.rh, true);
    dos_port_dirty_source = kDirtySrc_Other;
    r.unmarked = false;
    why++; dos_cr_mark_old++;''',
'''    if (dos_lab_cr_nomark()) dos_lab_cr_nomark_n++; else {   // R2B OVERLAY: guard (1) disabled -> counted, not made
    dos_port_dirty_source = kDirtySrc_RoomSprite;
    invalidate_rect(r.rx, r.ry, r.rx + r.rw, r.ry + r.rh, true);
    dos_port_dirty_source = kDirtySrc_Other;
    }
    r.unmarked = false;
    why++; dos_cr_mark_old++;'''), (
'''        r.bmp == actsp.Bmp.get() && r.ddb == actsp.Ddb && walk_behind_baselines_changed == 0 &&''',
'''        r.bmp == actsp.Bmp.get() && r.ddb == actsp.Ddb && (walk_behind_baselines_changed == 0 || dos_lab_cr_nobasel()) &&'''), (
'''r.key.x == atx && r.key.y == aty && r.key.basel == usebasel &&''',
'''r.key.x == atx && r.key.y == aty && (r.key.basel == usebasel || dos_lab_cr_nobasel()) &&'''), (
'''    const bool same = last && !wbc && memcmp(&k, &r.key, sizeof(k)) == 0;''',
'''    DosCrKey _kc = k; if (dos_lab_cr_nobasel()) { _kc.basel = r.key.basel; wbc = false; }   // R2B OVERLAY: control (ii)
    const bool same = last && !wbc && memcmp(&_kc, &r.key, sizeof(k)) == 0;'''), (
'''        else if (dos_cr_cam_moved)                                     { dos_cr_ff_cam++; dos_cr_ff++; }
        else if (dos_port_dirty.is_full || dos_port_dirty.carry_full)  { dos_cr_ff_full++; dos_cr_ff++; }
        else if (dos_guiclip_latched_next())                           { dos_cr_ff_latch++; dos_cr_ff++; }''',
'''        else if (dos_cr_cam_moved && !dos_lab_cr_nocam())              { dos_cr_ff_cam++; dos_cr_ff++; }   // R2B OVERLAY knobs
        else if ((dos_port_dirty.is_full || dos_port_dirty.carry_full) && !dos_lab_cr_nocam()) { dos_cr_ff_full++; dos_cr_ff++; }
        else if (dos_guiclip_latched_next() && !dos_lab_cr_nolatch())  { dos_cr_ff_latch++; dos_cr_ff++; }'''), (
'''        dos_cr_drv_clipped, dos_cr_drv_full, dos_cr_drv_latched, dos_cr_scene);
}''',
'''        dos_cr_drv_clipped, dos_cr_drv_full, dos_cr_drv_latched, dos_cr_scene);
    fprintf(log, "DOS-PORT charreuse_lab verify=%d vchecks=%ld vmismatch=%ld vpx=%lld nodraw=%d nodraw_n=%ld nobasel=%d"
        " nomark=%d nomark_n=%ld nolatch=%d nocam=%d toggles=%ld basel_forced=%ld cam_forced=%ld cam_moves=%ld\\n",
        dos_lab_cr_verify(), dos_lab_cr_vchecks, dos_lab_cr_vmismatch, dos_lab_cr_vpx, dos_lab_cr_nodraw(), dos_lab_cr_nodraw_n,
        dos_lab_cr_nobasel(), dos_lab_cr_nomark(), dos_lab_cr_nomark_n, dos_lab_cr_nolatch(), dos_lab_cr_nocam(),
        dos_lab_cr_toggles, dos_lab_cr_basel_n, dos_lab_cr_cam_n, dos_lab_cr_cam_moves);
}'''), (
# scene-dependent helpers, after the lever block
'''#endif

void prepare_characters_for_drawing()
{''',
'''// R2B OVERLAY: forcings, verify, room log, checkpoint
static int dos_lab_pair(const char *n, int &k, int &a, int defa)
{
    if (k < 0) { k = 0; a = defa; const char *e = getenv(n); if (e) { k = atoi(e); const char *c = strchr(e, ':'); if (c) a = atoi(c + 1); } }
    return k;
}
static int dos_lab_tog_k = -1, dos_lab_tog_ch = 1, dos_lab_bas_k = -1, dos_lab_bas_ch = 0, dos_lab_cam_k = -1, dos_lab_cam_m = 0;
static bool dos_lab_cr_toggle_now(int charid)
{
    if (dos_lab_pair("DOSAGS_LAB_CR_TOGGLE", dos_lab_tog_k, dos_lab_tog_ch, 1) <= 0 || charid != dos_lab_tog_ch) return false;
    if ((dos_cr_scene % dos_lab_tog_k) != 0) return false;
    dos_lab_cr_toggles++;
    return true;
}
static int dos_lab_cr_basel_now(int charid)
{
    if (dos_lab_pair("DOSAGS_LAB_CR_BASEL", dos_lab_bas_k, dos_lab_bas_ch, 0) <= 0 || charid != dos_lab_bas_ch) return 0;
    if (((dos_cr_scene / dos_lab_bas_k) & 1) == 0) return 0;
    dos_lab_cr_basel_n++;
    return 1000;
}
void dos_lab_cr_cam_force()   // construct_game_scene, before play.UpdateViewports()
{
    if (dos_lab_pair("DOSAGS_LAB_CR_CAM", dos_lab_cam_k, dos_lab_cam_m, 0) <= 0 || displayed_room < 0) return;
    if ((dos_cr_scene % dos_lab_cam_k) != 0) return;
    dos_lab_cr_cam_n++;
    auto cam = play.GetRoomCamera(0);
    if (dos_lab_cam_m == 1 && cam && thisroom.Width > cam->GetRect().GetWidth())
    {
        const Rect r = cam->GetRect();
        cam->SetAt(r.Left > 0 ? r.Left - 1 : r.Left + 1, r.Top);
        dos_lab_cr_cam_moves++;
    }
    else
        invalidate_screen();   // what on_roomcamera_changed() does on a camera move
}
static int dos_lab_room_seen = -1000;
static void dos_lab_cr_prep_hook()
{
    if (displayed_room == dos_lab_room_seen) return;
    dos_lab_room_seen = displayed_room;
    auto vp = play.GetRoomViewport(0);
    auto cam = vp ? vp->GetCamera() : nullptr;
    const Rect v = vp ? vp->GetRect() : Rect(), c = cam ? cam->GetRect() : Rect();
    Debug::Printf("DOS-PORT labroom room=%d w=%d h=%d vp=%d,%d,%d,%d cam=%d,%d,%d,%d nviews=%d", displayed_room,
        thisroom.Width, thisroom.Height, v.Left, v.Top, v.GetWidth(), v.GetHeight(), c.Left, c.Top, c.GetWidth(),
        c.GetHeight(), play.GetRoomViewportCount());
}
static void dos_lab_cr_verify_one(int ch, const ObjectCache &cs, const ObjTexture &a, int atx, int aty, int basel, bool wb)
{
    static std::unique_ptr<Bitmap> scratch;
    dos_lab_cr_vchecks++;
    if (!cs.image || !a.Bmp) { dos_lab_cr_vmismatch++; return; }
    recycle_bitmap(scratch, cs.image->GetColorDepth(), cs.image->GetWidth(), cs.image->GetHeight());
    scratch->Blit(cs.image.get(), 0, 0);   // construct_object_gfx's cached branch
    if (wb && drawstate.WalkBehindMethod == DrawOverCharSprite)
        walkbehinds_cropout(scratch.get(), atx, aty, basel);   // prepare_and_add_object_gfx, actsp_modified
    bool same = scratch->GetWidth() == a.Bmp->GetWidth() && scratch->GetHeight() == a.Bmp->GetHeight() &&
                scratch->GetColorDepth() == a.Bmp->GetColorDepth();
    const int bw = scratch->GetWidth() * scratch->GetBPP();
    for (int y = 0; same && y < scratch->GetHeight(); ++y)
        same = memcmp(scratch->GetScanLine(y), a.Bmp->GetScanLine(y), bw) == 0;
    dos_lab_cr_vpx += (long long)scratch->GetWidth() * scratch->GetHeight();
    if (!same)
    {
        dos_lab_cr_vmismatch++;
        if (dos_lab_cr_vmismatch <= 20)
            Debug::Printf("DOS-PORT crverify MISMATCH lc=%u scene=%ld ch=%d at=%d,%d basel=%d", (unsigned)get_loop_counter(),
                dos_cr_scene, ch, atx, aty, basel);
    }
}
void dos_lab_cr_ckpt(long lc)
{
    extern long dos_cr_drv_skipped, dos_cr_drv_boxed, dos_cr_drv_boxes, dos_cr_drv_full;
    extern long long dos_lab_tk_cblit_us_all, dos_lab_tk_cblit_px_all; extern long dos_lab_tk_cblit_n_all;
    Debug::Printf("DOS-PORT labck c=cr lc=%ld hits=%ld elig=%ld skips=%ld ff=%ld mark_old=%ld drv_skipped=%ld drv_boxed=%ld"
        " drv_boxes=%ld drv_full=%ld prep_us=%lld prep_calls=%ld bg_us=%lld bg_calls=%ld cblit_us=%lld cblit_px=%lld cblit_n=%ld"
        " scenes=%ld", lc, dos_cr_hits, dos_cr_elig, dos_cr_skips, dos_cr_ff, dos_cr_mark_old, dos_cr_drv_skipped,
        dos_cr_drv_boxed, dos_cr_drv_boxes, dos_cr_drv_full, dos_port_tick_timing.sc_prep_chars.total_us,
        dos_port_tick_timing.sc_prep_chars.calls, dos_port_tick_timing.bg_restore.total_us,
        dos_port_tick_timing.bg_restore.calls, dos_lab_tk_cblit_us_all, dos_lab_tk_cblit_px_all, dos_lab_tk_cblit_n_all,
        dos_cr_scene);
}
#endif

void prepare_characters_for_drawing()
{'''), (
'''    if (_cr) dos_cr_begin_chars();
#endif''',
'''    if (_cr) dos_cr_begin_chars();
    dos_lab_cr_prep_hook();   // R2B OVERLAY
#endif'''), (
'''        const CharacterInfo &chin = game.chars[charid];
#ifdef __DJGPP__
        if (_cr && (chin.on == 0 || chin.room != displayed_room))''',
'''        const CharacterInfo &chin = game.chars[charid];
#ifdef __DJGPP__
        if (chin.on != 0 && chin.room == displayed_room && dos_lab_cr_toggle_now(charid))   // R2B OVERLAY: forced "off"
        { if (_cr) dos_cr_char_gone(charid); continue; }
        if (_cr && (chin.on == 0 || chin.room != displayed_room))'''), (
'''        int usebasel = chin.get_baseline();

        // Generate raw bitmap in ObjTexture and store parameters in ObjectCache.
#ifdef __DJGPP__''',
'''        int usebasel = chin.get_baseline();
#ifdef __DJGPP__
        usebasel += dos_lab_cr_basel_now(charid);   // R2B OVERLAY: forced baseline change (draw only)
#endif

        // Generate raw bitmap in ObjTexture and store parameters in ObjectCache.
#ifdef __DJGPP__'''), (
'''        if (_cr_hit) dos_cr_hits++;''',
'''        if (_cr_hit) dos_cr_hits++;
        if (_cr_hit && dos_lab_cr_verify())   // R2B OVERLAY: rebuild the reused image the old way and compare
            dos_lab_cr_verify_one(charid, chsav, actsp, atx, aty, usebasel, (chin.flags & CHF_NOWALKBEHINDS) == 0);'''), (
'''        { DosPortTickScope _dp(dos_port_tick_timing.sc_prep_chars);''',
'''        { DosPortTickScope _dp(dos_port_tick_timing.sc_prep_chars, dos_lab_tk() ? 8 : 0);   // R2B OVERLAY: kind 8'''), (
'''                if (_cr_skip)
                    gfxDriver->DosPortNextIsChar(2);''',
'''                if (_cr_skip)
                    gfxDriver->DosPortNextIsChar(2);
                else if (t.DosCharId >= 0 && dos_lab_tk())
                    gfxDriver->DosPortNextIsChar(1);   // R2B OVERLAY: timed as a character'''), (
'''            gfxDriver->DrawSprite(t.X, t.Y, t.DDB);
        }
        else if (t.RenderStage >= 0)''',
'''#ifdef __DJGPP__
            if (_cr_skip && dos_lab_cr_nodraw())   // R2B OVERLAY: control (i), not drawn at all
            { gfxDriver->DosPortClipNextToDirty(false); gfxDriver->DosPortNextIsChar(0); dos_lab_cr_nodraw_n++; continue; }
#endif
            gfxDriver->DrawSprite(t.X, t.Y, t.DDB);
        }
        else if (t.RenderStage >= 0)'''), (
'''    dos_char_reuse_scene_begin();    // patch 0369 R2
#endif''',
'''    dos_char_reuse_scene_begin();    // patch 0369 R2
    { extern void dos_lab_cr_cam_force(); dos_lab_cr_cam_force(); }   // R2B OVERLAY
#endif''')])

edit('Engine/gfx/ali3dsw.cpp', [(
'''int dos_guiclip_latched_next() { return dos_gc_latch >= 2; }''',
'''int dos_guiclip_latched_next() { return dos_gc_latch >= 2; }
extern int dos_lab_cr_nolatch(), dos_lab_cr_nocam(), dos_lab_tk();   // R2B OVERLAY (ac/draw.cpp)
long long dos_lab_tk_cblit_us = 0, dos_lab_tk_cblit_px = 0, dos_lab_tk_cblit_us_all = 0, dos_lab_tk_cblit_px_all = 0;
long dos_lab_tk_cblit_n_all = 0;'''), (
'''        if (dos_gc_latch == 0 && _dp_same_space &&
            dos_port_dirty.valid && !dos_port_dirty.is_full && !dos_port_dirty.carry_full)''',
'''        const bool _lab_crc = sprite.dos_char == 2;   // R2B OVERLAY: guards disabled for R2b entries only
        if ((dos_gc_latch == 0 || (_lab_crc && dos_lab_cr_nolatch())) && _dp_same_space && dos_port_dirty.valid &&
            ((!dos_port_dirty.is_full && !dos_port_dirty.carry_full) || (_lab_crc && dos_lab_cr_nocam())))'''), (
'''    int _r3_k = 0;
    do {''',
'''    const bool _tk_ch = sprite.dos_char != 0 && dos_lab_tk();   // R2B OVERLAY: time a character's composite
    const uclock_t _tk_t0 = _tk_ch ? uclock() : 0; long long _tk_px = 0;
    int _r3_k = 0;
    do {'''), (
'''    } while (++_r3_k < _r3_n);   // patch 0368
#endif''',
'''    if (_tk_ch) _tk_px += _dw_px;   // R2B OVERLAY
    } while (++_r3_k < _r3_n);   // patch 0368
    if (_tk_ch)
    {
        const long long _us = dos_port_tick_elapsed_us(_tk_t0);
        dos_lab_tk_cblit_us += _us; dos_lab_tk_cblit_px += _tk_px;
        dos_lab_tk_cblit_us_all += _us; dos_lab_tk_cblit_px_all += _tk_px; dos_lab_tk_cblit_n_all++;
    }
#endif'''), (
'''    {   // GATE OVERLAY: DOSAGS_LAB_FRAMEHASH=1 -> FHASH.TXT''',
'''    if (dos_lab_tk())   // R2B OVERLAY: per-pass kinds 9 / 14 / 13
    {
        static long long _tk_rb_last = 0;
        dos_port_ticklog_add(9, (unsigned long)dos_lab_tk_cblit_us);
        dos_port_ticklog_add(14, (unsigned long)dos_lab_tk_cblit_px);
        dos_port_ticklog_add(13, (unsigned long)(dos_port_tick_timing.rb_sprite_time.total_us - _tk_rb_last));
        _tk_rb_last = dos_port_tick_timing.rb_sprite_time.total_us;
    }
    dos_lab_tk_cblit_us = dos_lab_tk_cblit_px = 0;
    {   // GATE OVERLAY: DOSAGS_LAB_FRAMEHASH=1 -> FHASH.TXT''')])
print('r2b overlay applied')
