#!/usr/bin/env python3
"""R2LAND gate overlay for ags 0369 (lever R2, DOSAGS_CHAR_REUSE) -- never landed. Applies to vendor/ags in place
(uncommitted), over 0001-0369. First runs LAB-R2B's overlay (apply-overlay-r2b.py, its anchors renamed from "lab lever
R2" to "patch 0369 R2"; it runs R3LAND-2026-11-06's apply-overlay-r3land.py first), then adds two in-place-edit forcings
and their controls:
 - DOSAGS_LAB_CR_DYN=N  every Nth scene, each character standing still (walking 0, animating 0) in the room has its
     current view frame's sprite edited IN PLACE through the script path: a static frame sprite is first replaced by a
     dynamic copy (DynamicSprite.CreateFromExistingSprite, the frame's Graphic set to it), then
     DynamicSprite.GetDrawingSurface(), DrawingColor, DrawRectangle (2x2, position and colour move with each edit),
     DrawingSurface.Release() -> on_dynsprite_surface_release -> game_sprite_updated -> notify_sprite_changed.
   DOSAGS_LAB_CR_NONOTIFY=1  control: construct_object_gfx's cache test ignores the change notification for an R2a
     candidate only (dos_cr_allow set: R2's pre-test passed). Mode 0 is unaffected (dos_cr_allow is never set there).
 - DOSAGS_LAB_CR_WBM=N  every Nth scene a walk-behind mask edit through Room.GetDrawingSurfaceForMask(walk-behind):
     on odd N-windows, under each still character the lower half of its rect is saved and filled with area 15 (its
     baseline set to 1000 once per room with SetWalkBehindBase, so it crops every character); on even windows the
     saved pixels are put back. Then DrawingSurface.Release() -> on_room_mask_surface_release -> walkbehinds_recalc.
   DOSAGS_LAB_CR_NOWBGEN=1  control: R2's key ignores the walk-behind mask generation (dos_cr_wb_gen).
 - "DOS-PORT charreuse_lab2 ..." after charreuse_final: dyn_forced dyn_created dyn_refused (an R2a candidate whose
   cache test failed only on the notification) dyn_nonotify_hits (the control's hits in spite of it), wbm_forced
   wbm_restored wbm_refused (an R2a candidate refused only by the mask generation) wbm_ignored (the control's hits in
   spite of it), and the knob values.
Usage: apply-overlay-r2land.py VENDOR_AGS_ROOT"""
import os, subprocess, sys
root = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
subprocess.check_call([sys.executable, os.path.join(here, 'apply-overlay-r2b.py'), root])
def edit(rel, pairs):
    p = root + '/' + rel; s = open(p).read()
    for a, b in pairs:
        assert s.count(a) == 1, (rel, a[:80]); s = s.replace(a, b, 1)
    open(p, 'w').write(s)

edit('Engine/ac/draw.cpp', [(
'''static int dos_cr_allow = 0;
static int dos_cr_hit = 0;
#endif''',
'''static int dos_cr_allow = 0;
static int dos_cr_hit = 0;
int dos_lab_cr_nonotify();   // R2LAND OVERLAY (defined below)
long dos_lab_cr_dyn_refused = 0, dos_lab_cr_dyn_nonotify_hits = 0;
#endif'''), (
'''    // If we have the image cached, use it
    if ((objsav.image != nullptr) &&
        (objsav.sppic == specialpic) &&
        // not a dynamic sprite, or not sprite modified lately
        (!actsp.IsChangeNotified()) &&''',
'''    // R2LAND OVERLAY: an R2a candidate whose sprite change was notified (the test below refuses it, unless the control)
    const bool _lab_dyn = dos_cr_allow && (objsav.image != nullptr) && (objsav.sppic == specialpic) &&
        actsp.IsChangeNotified();
    if (_lab_dyn) { if (dos_lab_cr_nonotify()) dos_lab_cr_dyn_nonotify_hits++; else dos_lab_cr_dyn_refused++; }
    // If we have the image cached, use it
    if ((objsav.image != nullptr) &&
        (objsav.sppic == specialpic) &&
        // not a dynamic sprite, or not sprite modified lately
        (!actsp.IsChangeNotified() || (_lab_dyn && dos_lab_cr_nonotify())) &&'''), (
'''static int dos_lab_cr_verify() { return dos_lab_env("DOSAGS_LAB_CR_VERIFY", dos_lab_cr_verify_v); }''',
'''static int dos_lab_cr_verify() { return dos_lab_env("DOSAGS_LAB_CR_VERIFY", dos_lab_cr_verify_v); }
static int dos_lab_cr_nonotify_v = -1, dos_lab_cr_nowbgen_v = -1;   // R2LAND OVERLAY
int dos_lab_cr_nonotify() { return dos_lab_env("DOSAGS_LAB_CR_NONOTIFY", dos_lab_cr_nonotify_v); }
static int dos_lab_cr_nowbgen() { return dos_lab_env("DOSAGS_LAB_CR_NOWBGEN", dos_lab_cr_nowbgen_v); }
long dos_lab_cr_dyn_forced = 0, dos_lab_cr_dyn_created = 0;
long dos_lab_cr_wbm_forced = 0, dos_lab_cr_wbm_restored = 0, dos_lab_cr_wbm_refused = 0, dos_lab_cr_wbm_ignored = 0;'''), (
'''r.key.room == displayed_room && r.key.bgf == play.bg_frame && r.key.wbg == dos_cr_wb_gen;''',
'''r.key.room == displayed_room && r.key.bgf == play.bg_frame && (r.key.wbg == dos_cr_wb_gen || dos_lab_cr_nowbgen());'''), (
'''    DosCrKey _kc = k; if (dos_lab_cr_nobasel()) { _kc.basel = r.key.basel; wbc = false; }   // R2B OVERLAY: control (ii)''',
'''    DosCrKey _kc = k; if (dos_lab_cr_nobasel()) { _kc.basel = r.key.basel; wbc = false; }   // R2B OVERLAY: control (ii)
    if (dos_lab_cr_nowbgen()) _kc.wbg = r.key.wbg;   // R2LAND OVERLAY: control, the key without the mask generation'''), (
'''        dos_lab_cr_toggles, dos_lab_cr_basel_n, dos_lab_cr_cam_n, dos_lab_cr_cam_moves);
}''',
'''        dos_lab_cr_toggles, dos_lab_cr_basel_n, dos_lab_cr_cam_n, dos_lab_cr_cam_moves);
    fprintf(log, "DOS-PORT charreuse_lab2 dyn=%s nonotify=%d dyn_forced=%ld dyn_created=%ld dyn_refused=%ld"
        " dyn_nonotify_hits=%ld wbm=%s nowbgen=%d wbm_forced=%ld wbm_restored=%ld wbm_refused=%ld wbm_ignored=%ld\\n",
        getenv("DOSAGS_LAB_CR_DYN") ? getenv("DOSAGS_LAB_CR_DYN") : "-", dos_lab_cr_nonotify(), dos_lab_cr_dyn_forced,
        dos_lab_cr_dyn_created, dos_lab_cr_dyn_refused, dos_lab_cr_dyn_nonotify_hits,
        getenv("DOSAGS_LAB_CR_WBM") ? getenv("DOSAGS_LAB_CR_WBM") : "-", dos_lab_cr_nowbgen(), dos_lab_cr_wbm_forced,
        dos_lab_cr_wbm_restored, dos_lab_cr_wbm_refused, dos_lab_cr_wbm_ignored);
}'''), (
'''#endif

void prepare_characters_for_drawing()
{''',
'''// R2LAND OVERLAY: in-place edits of what a still character's image is made from (render-only, the same in every arm)
#include "ac/dynamicsprite.h"
#include "ac/drawingsurface.h"
#include "ac/global_walkbehind.h"
#include "ac/room.h"
#include "ac/dynobj/scriptdynamicsprite.h"
#include "ac/dynobj/scriptdrawingsurface.h"
#include "ac/dynobj/dynobj_manager.h"
#include <map>
static int dos_lab_dyn_k = -1, dos_lab_dyn_a = 0, dos_lab_wbm_k = -1, dos_lab_wbm_a = 0;
static std::map<int, ScriptDynamicSprite *> dos_lab_dyn_spr;   // dynamic slot -> its script object (kept referenced)
struct DosLabWbmSave { int room = -1000, x1 = 0, y1 = 0, x2 = -1, y2 = -1; std::vector<uint8_t> px; };
static std::vector<DosLabWbmSave> dos_lab_wbm_save;
static int dos_lab_wbm_room = -1000;
static int dos_lab_cr_wbm_on() { return dos_lab_pair("DOSAGS_LAB_CR_WBM", dos_lab_wbm_k, dos_lab_wbm_a, 0); }
static void dos_lab_cr_force_edits(int charid, const CharacterInfo &chin, int atx, int aty, int w, int h)
{
    const bool still = chin.walking == 0 && chin.animating == 0;
    if (dos_lab_pair("DOSAGS_LAB_CR_DYN", dos_lab_dyn_k, dos_lab_dyn_a, 0) > 0 && (dos_cr_scene % dos_lab_dyn_k) == 0 &&
        still && chin.view >= 0)
    {
        ViewFrame &vf = views[chin.view].loops[chin.loop].frames[chin.frame];
        if (!(vf.pic > 0 && dos_lab_dyn_spr.count(vf.pic)))
        {
            ScriptDynamicSprite *ds = DynamicSprite_CreateFromExistingSprite(spriteset.DoesSpriteExist(vf.pic) ? vf.pic : 0, 1);
            if (ds)
            {
                ccAddObjectReference(ccGetObjectHandleFromAddress(ds));   // never collected while the frame uses it
                dos_lab_dyn_spr[ds->slot] = ds;
                vf.pic = ds->slot;   // what ViewFrame.Graphic = ... does
                dos_lab_cr_dyn_created++;
            }
        }
        auto it = dos_lab_dyn_spr.find(vf.pic);
        if (it != dos_lab_dyn_spr.end())
        {
            ScriptDrawingSurface *sf = DynamicSprite_GetDrawingSurface(it->second);
            const Bitmap *b = spriteset[vf.pic];
            const int k = (int)++dos_lab_cr_dyn_forced;
            const int bw = b->GetWidth(), bh = b->GetHeight();
            const int x = (k * 5) % std::max(1, bw - 1), y = bh / 4 + (k * 3) % std::max(1, bh / 2);
            DrawingSurface_SetDrawingColor(sf, b->GetColorDepth() == 8 ? 1 + (k * 29) % 254 : 1 + (k * 40503) % 65534);
            DrawingSurface_DrawRectangle(sf, x, y, x + 1, y + 1);
            DrawingSurface_Release(sf);   // -> on_dynsprite_surface_release -> game_sprite_updated -> notify_sprite_changed
        }
    }
    if (dos_lab_cr_wbm_on() > 0 && (dos_cr_scene % dos_lab_wbm_k) == 0 && displayed_room >= 0)
    {
        if ((int)dos_lab_wbm_save.size() < game.numcharacters) dos_lab_wbm_save.resize(game.numcharacters);
        DosLabWbmSave &sv = dos_lab_wbm_save[charid];
        const bool fill = ((dos_cr_scene / dos_lab_wbm_k) & 1) != 0;
        if (fill && still && sv.room != displayed_room)
        {
            if (dos_lab_wbm_room != displayed_room)
            { dos_lab_wbm_room = displayed_room; SetWalkBehindBase(MAX_WALK_BEHINDS - 1, 1000); }
            ScriptDrawingSurface *sf = Room_GetDrawingSurfaceForMask(kRoomAreaWalkBehind);
            Bitmap *m = sf->StartDrawing();
            sv.x1 = std::max(0, atx); sv.y1 = std::max(0, aty + h / 2);
            sv.x2 = std::min(m->GetWidth() - 1, atx + w - 1); sv.y2 = std::min(m->GetHeight() - 1, aty + h - 1);
            sv.px.clear();
            for (int y = sv.y1; y <= sv.y2; ++y)
                for (int x = sv.x1; x <= sv.x2; ++x)
                { uint8_t *l = m->GetScanLineForWriting(y); sv.px.push_back(l[x]); l[x] = MAX_WALK_BEHINDS - 1; }
            sv.room = displayed_room;
            sf->FinishedDrawing();
            DrawingSurface_Release(sf);   // -> on_room_mask_surface_release -> walkbehinds_recalc
            dos_lab_cr_wbm_forced++;
        }
        else if (!fill && sv.room == displayed_room)
        {
            ScriptDrawingSurface *sf = Room_GetDrawingSurfaceForMask(kRoomAreaWalkBehind);
            Bitmap *m = sf->StartDrawing();
            size_t i = 0;
            for (int y = sv.y1; y <= sv.y2; ++y)
                for (int x = sv.x1; x <= sv.x2; ++x)
                    m->GetScanLineForWriting(y)[x] = sv.px[i++];
            sv.room = -1000;
            sf->FinishedDrawing();
            DrawingSurface_Release(sf);
            dos_lab_cr_wbm_restored++;
        }
    }
}
#endif

void prepare_characters_for_drawing()
{'''), (
'''        usebasel += dos_lab_cr_basel_now(charid);   // R2B OVERLAY: forced baseline change (draw only)
#endif''',
'''        usebasel += dos_lab_cr_basel_now(charid);   // R2B OVERLAY: forced baseline change (draw only)
        dos_lab_cr_force_edits(charid, chin, atx, aty, chex.width, chex.height);   // R2LAND OVERLAY
#endif'''), (
'''        dos_cr_allow = _cr ? dos_cr_pre(charid, chin, chex, actsp, atx, aty, usebasel) : 0;   // patch 0369 R2a''',
'''        dos_cr_allow = _cr ? dos_cr_pre(charid, chin, chex, actsp, atx, aty, usebasel) : 0;   // patch 0369 R2a
        if (_cr && dos_lab_cr_wbm_on() > 0 && charid < (int)dos_cr_rec.size() &&
            dos_cr_rec[charid].valid && dos_cr_rec[charid].key.wbg != dos_cr_wb_gen)   // R2LAND OVERLAY: counts
        {
            if (dos_cr_allow) dos_lab_cr_wbm_ignored++;   // only with NOWBGEN
            else
            {
                const int _g = dos_cr_wb_gen; dos_cr_wb_gen = dos_cr_rec[charid].key.wbg;
                if (dos_cr_pre(charid, chin, chex, actsp, atx, aty, usebasel)) dos_lab_cr_wbm_refused++;
                dos_cr_wb_gen = _g;
            }
        }''')])
print('r2land overlay applied')
