#!/usr/bin/env python3
"""Lab lever R2 (LAB-R2B.md): DOSAGS_CHAR_REUSE -- an unchanged character reuses its prepared image (R2a) and, in mode 2,
its composite (R2b). Applies to vendor/ags in place (uncommitted), over 0001-0368. Lab only; never landed as is.
Usage: lever-r2b.py VENDOR_AGS_ROOT"""
import sys
root = sys.argv[1]
def edit(rel, pairs):
    p = root + '/' + rel; s = open(p).read()
    for a, b in pairs:
        assert s.count(a) == 1, (rel, a[:80]); s = s.replace(a, b, 1)
    open(p, 'w').write(s)

# ---------------------------------------------------------------------------------------------------------------- draw.cpp
edit('Engine/ac/draw.cpp', [(
# A: the R2a permission/hit flags, ahead of construct_object_gfx
'''static bool construct_object_gfx(const ViewFrame *vf, int pic,
    const Size &scale_size,''',
'''#ifdef __DJGPP__
// DOS-PORT lab lever R2a (DOSAGS_CHAR_REUSE >= 1; see prepare_characters_for_drawing). dos_cr_allow is set for the one
// construct_char_gfx call of a character whose input key, outside this function's own cache test, equals last scene's
// and whose raw bitmap is still the one last scene left final; the cached branch then returns "intact" (dos_cr_hit).
static int dos_cr_allow = 0;
static int dos_cr_hit = 0;
#endif
static bool construct_object_gfx(const ViewFrame *vf, int pic,
    const Size &scale_size,'''), (
# B: the cached branch
'''            (walk_behind_baselines_changed == 0))
        {
            return true;
        }
        recycle_bitmap(actsp.Bmp, objsav.image->GetColorDepth(), objsav.image->GetWidth(), objsav.image->GetHeight());''',
'''            (walk_behind_baselines_changed == 0))
        {
            return true;
        }
#ifdef __DJGPP__
        // lab lever R2a: the cache test above matched (sprite and mirror, the six tint/light fields, zoom, no change
        // notification), the caller matched the rest of the key against last scene, so actsp.Bmp already holds the
        // re-copy plus the crop-out this branch and the caller would redo.
        if (dos_cr_allow && (actsp.Bmp != nullptr))
        {
            dos_cr_hit = 1;
            return true;
        }
#endif
        recycle_bitmap(actsp.Bmp, objsav.image->GetColorDepth(), objsav.image->GetWidth(), objsav.image->GetHeight());'''), (
# C: SpriteListEntry carries the character id
'''    // composited IN FULL -- only the invalidation is skipped.
    bool SkipInvalidate = false;
#endif''',
'''    // composited IN FULL -- only the invalidation is skipped.
    bool SkipInvalidate = false;
    int DosCharId = -1;   // lab lever R2: this entry is character DosCharId's texture
#endif'''), (
# F: clear_drawobj_cache drops the records
'''    for (int i = 0; i < MAX_ROOM_OBJECTS; ++i)
        dos_port_obj_prev[i] = DosPortObjPrev();
#endif
    // room overlays cache''',
'''    for (int i = 0; i < MAX_ROOM_OBJECTS; ++i)
        dos_port_obj_prev[i] = DosPortObjPrev();
    {   extern void dos_cr_reset_all(int why); dos_cr_reset_all(0); }   // lab lever R2: textures are gone
#endif
    // room overlays cache'''), (
# D: prepare_characters_for_drawing -- the R2 block ahead of it, hooks inside it
'''void prepare_characters_for_drawing()
{
    set_our_eip(33);
    const bool hw_accel = !drawstate.SoftwareRender;

    // draw characters
    for (int charid = 0; charid < game.numcharacters; ++charid)
    {
        const CharacterInfo &chin = game.chars[charid];
        if (chin.on == 0)
            continue; // disabled
        if (chin.room != displayed_room)
            continue; // in another room
''',
'''#ifdef __DJGPP__
// DOS-PORT lab lever R2 (dosags docs/lab/LAB-R2.md section 6; LAB-R2B.md). DOSAGS_CHAR_REUSE: unset or 0 = off (the 0368
// head); 1 = R2a only; 2 = R2a + R2b. Software renderer only.
//  R2a, the prepared image. In MMD room 1 the three kids are key-same in 88.5% of frames, and each frame still re-copied
//   the cached image into the raw bitmap and re-ran the walk-behind crop-out. When the whole input key equals last
//   scene's (sprite and mirror, view/loop/frame, the six tint/light fields, zoom, width/height, final position and
//   baseline, transparency, the no-walk-behinds flag, walk_behind_baselines_changed, the dynamic-sprite change mark, the
//   same room and background frame) and the raw bitmap is the one last scene left, it still holds last scene's final
//   image: only construct_object_gfx and walkbehinds_cropout write it, both from here, and the crop-out is a function of
//   the key. construct_object_gfx returns "intact", so no re-copy, no crop-out, no texture sync.
//  R2b, the composite (mode 2). A character that took R2a, was composited last scene and composites idempotently
//   (transparency 0, no alpha channel) skips its invalidation like 0233's room overlays: its rect is not marked, so it is
//   not restored and not presented, and it is flagged to the driver like 0169's GUI entries, so R3 (0368) draws it only
//   inside the dirty boxes that reach it. Outside them the buffer still holds last scene's composite of it, at the same
//   place, under and over the same entries (anything that changed there is marked, so it is inside a box).
//   (1) A character whose last composite skipped its mark and that is now off, in another room, not drawn or not
//       key-same (its baseline included) gets its OLD rect marked here, before this scene's restore (0197's convention).
//   (2) It is marked and drawn in full instead -- not skipped -- when 0366's latch is armed for this composite
//       (latch_fullrestore included), the camera or viewport moved, the whole surface is invalidated (dos_port_dirty
//       full, or its carry full), 0368's coarse guard is set, or more than one room viewport is drawn. In the driver a
//       flagged entry under the latch is drawn in full, as for GUIs.
//   (3) Every record is dropped (old rects of unmarked ones marked) when the drawobj cache is cleared, the room
//       changes, or a scene passed without a composite.
// Witness: "DOS-PORT charreuse DOSAGS_CHAR_REUSE=<v|(default)> mode=<0|1|2>" at startup; "DOS-PORT charreuse_final ..."
// in RUNMANI.LOG.
struct DosCrKey
{
    int pic, view, loop, frame, tr, tg, tb, ta, tl, ll, zoom, mir, w, h, x, y, basel, transp, nowb, room, bgf;
};
struct DosCrRec
{
    bool valid = false;      // composited in scene `seen`: key/bmp/ddb/rect describe that composite
    bool unmarked = false;   // ... and that composite skipped its invalidation
    bool elig = false;       // this scene: R2a hit, key-same, idempotent, composited last scene
    long seen = -1;          // the scene it was last composited in
    long prep = -1;          // the scene it was last prepared in
    DosCrKey key;
    const void *bmp = nullptr, *ddb = nullptr;
    int rx = 0, ry = 0, rw = 0, rh = 0;   // what invalidate_sprite() marks for that composite (room coords)
};
static std::vector<DosCrRec> dos_cr_rec;
static int dos_cr_mode_v = -1;
static long dos_cr_scene = 0;            // scenes constructed (construct_game_scene)
static long dos_cr_prev_scene = -1;      // the scene the characters were last prepared in
static long dos_cr_prev_comp = -1;       // composites done when they were
static int dos_cr_room = -1000;
static int dos_cr_nview = 0;             // room viewports drawn in the last scene
static Rect dos_cr_cam, dos_cr_vp; static bool dos_cr_cam_valid = false; static bool dos_cr_cam_moved = false;
long dos_cr_hits = 0, dos_cr_keyfail = 0, dos_cr_elig = 0, dos_cr_skips = 0, dos_cr_refused = 0;
long dos_cr_ff = 0, dos_cr_ff_latch = 0, dos_cr_ff_cam = 0, dos_cr_ff_full = 0, dos_cr_ff_coarse = 0, dos_cr_ff_multi = 0;
long dos_cr_mark_old = 0, dos_cr_mo_off = 0, dos_cr_mo_key = 0, dos_cr_mo_end = 0, dos_cr_mo_reset = 0;
long dos_cr_resets = 0, dos_cr_reset_why[3] = {0, 0, 0};
extern long dos_cr_composites;           // gfx/ali3dsw.cpp: composites done (RenderToBackBuffer)
extern int dos_guiclip_latched_next();   // gfx/ali3dsw.cpp: 0366's latch is armed for the next composite
extern int dos_guiclip_coarse();         // gfx/ali3dsw.cpp: 0368 guard (a) is set for the next composite
int dos_char_reuse_mode()
{
    if (dos_cr_mode_v < 0)
    {
        const char *e = getenv("DOSAGS_CHAR_REUSE");
        dos_cr_mode_v = (e && e[0] == '1' && e[1] == 0) ? 1 : (e && e[0] == '2' && e[1] == 0) ? 2 : 0;
        Debug::Printf("DOS-PORT charreuse DOSAGS_CHAR_REUSE=%s mode=%d", (e && *e) ? e : "(default)", dos_cr_mode_v);
    }
    return dos_cr_mode_v;
}
static void dos_cr_mark_old_rect(DosCrRec &r, long &why)
{
    dos_port_dirty_source = kDirtySrc_RoomSprite;
    invalidate_rect(r.rx, r.ry, r.rx + r.rw, r.ry + r.rh, true);
    dos_port_dirty_source = kDirtySrc_Other;
    r.unmarked = false;
    why++; dos_cr_mark_old++;
}
// why: 0 drawobj cache cleared, 1 room changed, 2 a scene passed without a composite (or a scene gap)
void dos_cr_reset_all(int why)
{
    for (auto &r : dos_cr_rec)
    {
        if (r.valid && r.unmarked) dos_cr_mark_old_rect(r, dos_cr_mo_reset);   // marking more is always safe
        r = DosCrRec();
    }
    dos_cr_resets++; dos_cr_reset_why[why < 0 ? 0 : why > 2 ? 2 : why]++;
}
void dos_char_reuse_scene_begin()   // construct_game_scene, before anything is restored or drawn
{
    dos_cr_scene++;
    dos_cr_nview = 0;
}
// prepare_characters_for_drawing: once per scene, before the characters
static void dos_cr_begin_chars()
{
    if ((int)dos_cr_rec.size() < game.numcharacters) dos_cr_rec.resize(game.numcharacters);
    if (displayed_room != dos_cr_room) { if (dos_cr_room != -1000) dos_cr_reset_all(1); dos_cr_room = displayed_room; }
    else if (dos_cr_prev_scene >= 0 &&
             (dos_cr_prev_scene != dos_cr_scene - 1 || dos_cr_composites != dos_cr_prev_comp + 1))
        dos_cr_reset_all(2);
    dos_cr_prev_scene = dos_cr_scene;
    dos_cr_prev_comp = dos_cr_composites;
    // the camera and viewport of the (one) room view, against last scene's
    dos_cr_cam_moved = true;
    auto vp = play.GetRoomViewport(0);
    auto cam = vp ? vp->GetCamera() : nullptr;
    if (vp && cam)
    {
        const Rect c = cam->GetRect(), v = vp->GetRect();
        dos_cr_cam_moved = !dos_cr_cam_valid || !(c == dos_cr_cam) || !(v == dos_cr_vp);
        dos_cr_cam = c; dos_cr_vp = v; dos_cr_cam_valid = true;
    }
    else dos_cr_cam_valid = false;
}
// the character is not drawn this scene
static void dos_cr_char_gone(int charid)
{
    if (charid >= (int)dos_cr_rec.size()) return;
    DosCrRec &r = dos_cr_rec[charid];
    if (r.valid && r.unmarked) dos_cr_mark_old_rect(r, dos_cr_mo_off);
    r.valid = false; r.elig = false;
}
// before construct_char_gfx: may R2a reuse last scene's final image?
static int dos_cr_pre(int charid, const CharacterInfo &chin, const CharacterExtras &chex, const ObjTexture &actsp,
                      int atx, int aty, int usebasel)
{
    DosCrRec &r = dos_cr_rec[charid];
    return r.valid && r.seen == dos_cr_scene - 1 && r.prep == dos_cr_scene - 1 && actsp.Bmp && actsp.Ddb &&
        r.bmp == actsp.Bmp.get() && r.ddb == actsp.Ddb && walk_behind_baselines_changed == 0 &&
        r.key.view == chin.view && r.key.loop == chin.loop && r.key.frame == chin.frame &&
        r.key.w == chex.width && r.key.h == chex.height && r.key.x == atx && r.key.y == aty && r.key.basel == usebasel &&
        r.key.transp == chin.transparency && r.key.nowb == ((chin.flags & CHF_NOWALKBEHINDS) != 0) &&
        r.key.room == displayed_room && r.key.bgf == play.bg_frame;
}
// after prepare_and_add_object_gfx (usebasel as it went to the sprite list)
static void dos_cr_post(int charid, const CharacterInfo &chin, const CharacterExtras &chex, const ObjectCache &cs,
                        const ObjTexture &actsp, int atx, int aty, int usebasel, bool hit, bool wbc)
{
    DosCrRec &r = dos_cr_rec[charid];
    const DosCrKey k = { cs.sppic, chin.view, chin.loop, chin.frame, cs.tintr, cs.tintg, cs.tintb, cs.tintamnt,
                         cs.tintlight, cs.lightlev, cs.zoom, (int)cs.mirrored, chex.width, chex.height, atx, aty, usebasel,
                         chin.transparency, (chin.flags & CHF_NOWALKBEHINDS) != 0, displayed_room, play.bg_frame };
    const bool last = r.valid && r.seen == dos_cr_scene - 1;
    const bool same = last && !wbc && memcmp(&k, &r.key, sizeof(k)) == 0;
    if (hit && !same) dos_cr_keyfail++;   // cannot happen: R2a's test is a subset of the key; counted, never assumed
    const bool idem = chin.transparency == 0 && actsp.SpriteID < game.SpriteInfos.size() &&
        (game.SpriteInfos[actsp.SpriteID].Flags & SPF_ALPHACHANNEL) == 0;
    r.elig = dos_cr_mode_v == 2 && hit && same && idem;
    if (dos_cr_mode_v == 2 && hit && same && !idem) dos_cr_refused++;
    if (r.elig) dos_cr_elig++;
    // rule (1): last composite left unmarked and this one will not look the same -> its old rect goes out now
    if (r.valid && r.unmarked && !r.elig) dos_cr_mark_old_rect(r, dos_cr_mo_key);
    r.key = k; r.bmp = actsp.Bmp.get(); r.ddb = actsp.Ddb; r.prep = dos_cr_scene;
}
// put_sprite_list_on_screen(in_room): after this scene's restore, before the entry's mark. Returns true to skip the mark.
static bool dos_cr_put(const SpriteListEntry &t)
{
    if (t.DosCharId < 0 || t.DosCharId >= (int)dos_cr_rec.size()) return false;
    DosCrRec &r = dos_cr_rec[t.DosCharId];
    if (r.prep != dos_cr_scene) return false;
    bool skip = false;
    if (r.elig)
    {
        if (dos_cr_nview > 1)                                          { dos_cr_ff_multi++; dos_cr_ff++; }
        else if (dos_cr_cam_moved)                                     { dos_cr_ff_cam++; dos_cr_ff++; }
        else if (dos_port_dirty.is_full || dos_port_dirty.carry_full)  { dos_cr_ff_full++; dos_cr_ff++; }
        else if (dos_guiclip_latched_next())                           { dos_cr_ff_latch++; dos_cr_ff++; }
        else if (dos_guiclip_coarse())                                 { dos_cr_ff_coarse++; dos_cr_ff++; }
        else skip = true;
    }
    r.valid = true; r.unmarked = skip; r.seen = dos_cr_scene;
    r.rx = t.X; r.ry = t.Y; r.rw = t.DDB->GetWidth(); r.rh = t.DDB->GetHeight();
    if (skip) dos_cr_skips++;
    return skip;
}
// end of construct_game_scene: a record not composited this scene describes nothing on the screen any more. If it was
// left unmarked its old pixels are still there: mark them (a safety net; rule (1) is meant to have caught it already).
void dos_char_reuse_scene_end()
{
    for (auto &r : dos_cr_rec)
    {
        if (!r.valid || r.seen == dos_cr_scene) continue;
        if (r.unmarked) dos_cr_mark_old_rect(r, dos_cr_mo_end);
        r.valid = false;
    }
}
void dos_char_reuse_summary(FILE *log)
{
    if (!log) return;
    extern long dos_cr_drv_flagged, dos_cr_drv_skipped, dos_cr_drv_boxed, dos_cr_drv_boxes, dos_cr_drv_full,
                dos_cr_drv_latched, dos_cr_drv_clipped;
    fprintf(log, "DOS-PORT charreuse_final mode=%d hits=%ld keyfail=%ld elig=%ld skips=%ld refused=%ld forced_full=%ld"
        " ff_latch=%ld ff_cam=%ld ff_full=%ld ff_coarse=%ld ff_multi=%ld mark_old=%ld mo_off=%ld mo_key=%ld mo_end=%ld"
        " mo_reset=%ld resets=%ld reset_cache=%ld reset_room=%ld reset_gap=%ld drv_flagged=%ld drv_skipped=%ld"
        " drv_boxed=%ld drv_boxes=%ld drv_clipped=%ld drv_full=%ld drv_latched=%ld scenes=%ld\\n",
        dos_cr_mode_v, dos_cr_hits, dos_cr_keyfail, dos_cr_elig, dos_cr_skips, dos_cr_refused, dos_cr_ff,
        dos_cr_ff_latch, dos_cr_ff_cam, dos_cr_ff_full, dos_cr_ff_coarse, dos_cr_ff_multi, dos_cr_mark_old, dos_cr_mo_off,
        dos_cr_mo_key, dos_cr_mo_end, dos_cr_mo_reset, dos_cr_resets, dos_cr_reset_why[0], dos_cr_reset_why[1],
        dos_cr_reset_why[2], dos_cr_drv_flagged, dos_cr_drv_skipped, dos_cr_drv_boxed, dos_cr_drv_boxes,
        dos_cr_drv_clipped, dos_cr_drv_full, dos_cr_drv_latched, dos_cr_scene);
}
#endif

void prepare_characters_for_drawing()
{
    set_our_eip(33);
    const bool hw_accel = !drawstate.SoftwareRender;
#ifdef __DJGPP__
    const int _cr = drawstate.SoftwareRender ? dos_char_reuse_mode() : 0;   // lab lever R2
    if (_cr) dos_cr_begin_chars();
#endif

    // draw characters
    for (int charid = 0; charid < game.numcharacters; ++charid)
    {
        const CharacterInfo &chin = game.chars[charid];
#ifdef __DJGPP__
        if (_cr && (chin.on == 0 || chin.room != displayed_room))
            dos_cr_char_gone(charid);   // lab lever R2 rule (1)
#endif
        if (chin.on == 0)
            continue; // disabled
        if (chin.room != displayed_room)
            continue; // in another room
'''), (
'''        // Generate raw bitmap in ObjTexture and store parameters in ObjectCache.
        bool actsp_modified = !construct_char_gfx(charid, false);
        // Prepare the object texture
        prepare_and_add_object_gfx(chsav, actsp, actsp_modified,
            Size(chex.width, chex.height), atx, aty, usebasel,
            (chin.flags & CHF_NOWALKBEHINDS) == 0, chin.transparency, hw_accel);
#if (AGS_PLATFORM_DEBUG)
        actsp.Ddb->SetTag(String::FromFormat("CHAR%d:%s", chin.index_id, chin.scrname));
#endif
        // Finally, add the texture to the draw list
        add_to_sprite_list(actsp.Ddb, atx, aty, usebasel, actsp.DrawIndex);
    }
}''',
'''        // Generate raw bitmap in ObjTexture and store parameters in ObjectCache.
#ifdef __DJGPP__
        const bool _cr_wbc = walk_behind_baselines_changed != 0;
        dos_cr_allow = _cr ? dos_cr_pre(charid, chin, chex, actsp, atx, aty, usebasel) : 0;   // lab lever R2a
        dos_cr_hit = 0;
#endif
        bool actsp_modified = !construct_char_gfx(charid, false);
#ifdef __DJGPP__
        const bool _cr_hit = dos_cr_hit != 0;
        dos_cr_allow = 0; dos_cr_hit = 0;
        if (_cr_hit) dos_cr_hits++;
#endif
        // Prepare the object texture
        prepare_and_add_object_gfx(chsav, actsp, actsp_modified,
            Size(chex.width, chex.height), atx, aty, usebasel,
            (chin.flags & CHF_NOWALKBEHINDS) == 0, chin.transparency, hw_accel);
#if (AGS_PLATFORM_DEBUG)
        actsp.Ddb->SetTag(String::FromFormat("CHAR%d:%s", chin.index_id, chin.scrname));
#endif
#ifdef __DJGPP__
        if (_cr) dos_cr_post(charid, chin, chex, chsav, actsp, atx, aty, usebasel, _cr_hit, _cr_wbc);
        const size_t _cr_n = sprlist.size();
#endif
        // Finally, add the texture to the draw list
        add_to_sprite_list(actsp.Ddb, atx, aty, usebasel, actsp.DrawIndex);
#ifdef __DJGPP__
        if (sprlist.size() > _cr_n) sprlist.back().DosCharId = charid;   // lab lever R2: the entry is this character
#endif
    }
}'''), (
# E: put_sprite_list_on_screen
'''            // mark the image's region as dirty
#ifdef __DJGPP__
            if (!t.SkipInvalidate)   // patch 0169 stage 1
#endif''',
'''            // mark the image's region as dirty
#ifdef __DJGPP__
            // lab lever R2b: an unchanged character skips its mark, as 0233's room overlays do
            const bool _cr_skip = in_room && t.DosCharId >= 0 && dos_cr_mode_v >= 1 && dos_cr_put(t);   // records in 1 and 2
            if (!t.SkipInvalidate && !_cr_skip)   // patch 0169 stage 1
#endif'''), (
'''                if (_h2 && t.SkipInvalidate)
                    gfxDriver->DosPortClipNextToDirty(true);
            }
#endif''',
'''                if (_h2 && (t.SkipInvalidate || _cr_skip))   // lab lever R2b: flagged like 0169's GUI entries
                    gfxDriver->DosPortClipNextToDirty(true);
                if (_cr_skip)
                    gfxDriver->DosPortNextIsChar(2);
            }
#endif'''), (
# G: scene begin / end
'''    dos_port_dirty.scene_path = true;
    if (full_redraw)
        dos_port_dirty_set_full("full_redraw requested");
    dos_port_gui_flush_unmarked();   // patch 0191: before the restore below
#endif''',
'''    dos_port_dirty.scene_path = true;
    if (full_redraw)
        dos_port_dirty_set_full("full_redraw requested");
    dos_port_gui_flush_unmarked();   // patch 0191: before the restore below
    dos_char_reuse_scene_begin();    // lab lever R2
#endif'''), (
'''    dos_port_over_end_frame();   // patch 0233
#endif''',
'''    dos_port_over_end_frame();   // patch 0233
    dos_char_reuse_scene_end();  // lab lever R2
#endif'''), (
'''// Schedule room rendering: background, objects, characters
static void construct_room_view()
{''',
'''#ifdef __DJGPP__
void dos_char_reuse_scene_begin();   // lab lever R2 (defined above prepare_characters_for_drawing)
void dos_char_reuse_scene_end();
#endif
// Schedule room rendering: background, objects, characters
static void construct_room_view()
{'''), (
'''        const Rect &view_rc = viewport->GetRect();
        const Rect &cam_rc = camera->GetRect();
        const float view_sx = (float)view_rc.GetWidth() / (float)cam_rc.GetWidth();''',
'''#ifdef __DJGPP__
        dos_cr_nview++;   // lab lever R2: R2b only with one room viewport
#endif
        const Rect &view_rc = viewport->GetRect();
        const Rect &cam_rc = camera->GetRect();
        const float view_sx = (float)view_rc.GetWidth() / (float)cam_rc.GetWidth();''')])

# ---------------------------------------------------------------------------------------------------------- driver headers
edit('Engine/gfx/graphicsdriver.h', [(
'''    virtual void DosPortClipNextToDirty(bool) {}
#endif''',
'''    virtual void DosPortClipNextToDirty(bool) {}
    // lab lever R2: one-shot, the next DrawSprite is a character (2 = an R2b entry that skipped its mark)
    virtual void DosPortNextIsChar(int) {}
#endif''')])
edit('Engine/gfx/ali3dsw.h', [(
'''    void DosPortClipNextToDirty(bool on) { _dosNextClipDirty = on; }
private:
    bool _dosNextClipDirty = false;''',
'''    void DosPortClipNextToDirty(bool on) { _dosNextClipDirty = on; }
    void DosPortNextIsChar(int c) { _dosNextChar = c; }   // lab lever R2
private:
    bool _dosNextClipDirty = false;
    int _dosNextChar = 0;''')])
edit('Engine/gfx/gfxdriverbase.h', [(
'''    bool dos_clip_dirty = false;
#endif''',
'''    bool dos_clip_dirty = false;
    int dos_char = 0;   // lab lever R2: 2 = a character entry that skipped its mark (R2b)
#endif''')])

# ------------------------------------------------------------------------------------------------------------ ali3dsw.cpp
edit('Engine/gfx/ali3dsw.cpp', [(
'''void dos_guiclip_summary(FILE *log)
{''',
'''// lab lever R2 (ac/draw.cpp): what R2b's guard reads, and the driver's side of its counters
long dos_cr_composites = 0;
long dos_cr_drv_flagged = 0, dos_cr_drv_skipped = 0, dos_cr_drv_boxed = 0, dos_cr_drv_boxes = 0, dos_cr_drv_full = 0;
long dos_cr_drv_latched = 0, dos_cr_drv_clipped = 0;
int dos_char_reuse_mode();   // ac/draw.cpp
int dos_guiclip_latched_next() { return dos_gc_latch >= 2; }   // the next composite decays it to >= 1: latched
int dos_guiclip_coarse() { return dos_gc_coarse; }
void dos_guiclip_summary(FILE *log)
{'''), (
'''SDLRendererGraphicsDriver::SDLRendererGraphicsDriver()
{
#ifdef __DJGPP__
  dos_guiclip_mode();   // patch 0366: the witness line, once, at startup''',
'''SDLRendererGraphicsDriver::SDLRendererGraphicsDriver()
{
#ifdef __DJGPP__
  dos_guiclip_mode();   // patch 0366: the witness line, once, at startup
  dos_char_reuse_mode();   // lab lever R2: its witness line''',
), (
'''    if (dos_gc_latch > 0) dos_gc_latch--;
    if (dos_gc_latch_fr > 0) dos_gc_latch_fr--;   // patch 0368''',
'''    if (dos_gc_latch > 0) dos_gc_latch--;
    if (dos_gc_latch_fr > 0) dos_gc_latch_fr--;   // patch 0368
    dos_cr_composites++;   // lab lever R2'''), (
'''        e.dos_clip_dirty = _dosNextClipDirty;   // patch 0170
        _dosNextClipDirty = false;              // one-shot, never sticky''',
'''        e.dos_clip_dirty = _dosNextClipDirty;   // patch 0170
        _dosNextClipDirty = false;              // one-shot, never sticky
        e.dos_char = _dosNextChar;              // lab lever R2
        _dosNextChar = 0;'''), (
'''    else
        _dosNextClipDirty = false;   // do not leak onto the next sprite''',
'''    else
    {
        _dosNextClipDirty = false;   // do not leak onto the next sprite
        _dosNextChar = 0;
    }'''), (
'''    if (sprite.dos_clip_dirty)
    {
        dos_gc_flagged++;
        bool _gc_clipped = false;''',
'''    if (sprite.dos_clip_dirty)
    {
        dos_gc_flagged++;
        if (sprite.dos_char == 2) dos_cr_drv_flagged++;   // lab lever R2b
        bool _gc_clipped = false;'''), (
'''            if (_gm >= 2 && native_bmp && _ge.IsEmpty())
            {
                dos_gc_skipped++;''',
'''            if (_gm >= 2 && native_bmp && _ge.IsEmpty())
            {
                if (sprite.dos_char == 2) dos_cr_drv_skipped++;   // lab lever R2b
                dos_gc_skipped++;'''), (
'''                if (_r3_n == 0)   // the bbox reached the entry, no box did: nothing to draw
                {
                    dos_gc_skipped++;''',
'''                if (_r3_n == 0)   // the bbox reached the entry, no box did: nothing to draw
                {
                    if (sprite.dos_char == 2) dos_cr_drv_skipped++;   // lab lever R2b
                    dos_gc_skipped++;'''), (
'''                dos_gc_boxed++;
                dos_gc_boxes += _r3_n;''',
'''                dos_gc_boxed++;
                dos_gc_boxes += _r3_n;
                if (sprite.dos_char == 2) { dos_cr_drv_boxed++; dos_cr_drv_boxes += _r3_n; }   // lab lever R2b'''), (
'''                dos_gc_clipped++;
                _gc_clipped = true;
            }
        }
        if (!_gc_clipped)
        {
            dos_gc_full++;''',
'''                dos_gc_clipped++;
                if (sprite.dos_char == 2) dos_cr_drv_clipped++;   // lab lever R2b (mode 2's bbox, or 4's guard (a))
                _gc_clipped = true;
            }
        }
        if (!_gc_clipped)
        {
            if (sprite.dos_char == 2) { dos_cr_drv_full++; if (dos_gc_latch) dos_cr_drv_latched++; }   // lab lever R2b
            dos_gc_full++;''')])

# --------------------------------------------------------------------------------------------------------------- quit.cpp
edit('Engine/main/quit.cpp', [(
'''            "DOSAGS_BREAK_0193",      // patch 0195: control for the screen-equality gate; a diagnostic
''',
'''            "DOSAGS_BREAK_0193",      // patch 0195: control for the screen-equality gate; a diagnostic
            "DOSAGS_CHAR_REUSE",      // lab lever R2: character reuse (0 off by default; 1 = R2a; 2 = R2a + R2b)
'''), (
'''                extern void dos_guiclip_summary(FILE *);
                dos_guiclip_summary(run_manifest_log);''',
'''                extern void dos_guiclip_summary(FILE *);
                dos_guiclip_summary(run_manifest_log);
                extern void dos_char_reuse_summary(FILE *);   // lab lever R2, both flavours
                dos_char_reuse_summary(run_manifest_log);''')])
print('lever R2 applied')
