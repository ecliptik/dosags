#!/usr/bin/env python3
"""L1LAND gate overlay (LAB-L1R's apply-overlay-l1r.py with its anchors renamed from "DOS-PORT lab L1R" to "DOS-PORT
patch 0371" and LAB-RB's overlay looked up beside it; lab only, never landed): applies over 0001-0371. First runs LAB-RB's overlay
(../rb-lab/apply-overlay-rb.py: R3LAND's FRAMEHASH / LABCLICKS / ..., the GCL and H presets, the rb* lines), then adds the
L1R control and guard knobs (render-free, the same in both arms unless stated):
 - DOSAGS_LAB_RPW_STALE=1 (control C1, lever on only): the warm builds the cache from a COPY of the prepared mask with a
   41x13 block around the player cut out (unwalkable) and stamps it with the live mask's serial, so the first request
   serial-hits a wrong cache. The gate must DIFF.
 - DOSAGS_LAB_RPW_MASKCHG=1 (forced guard F1, both arms): right after the warm point, a 10x9 block 40..31 px left of the
   player (mask coords) is drawn unwalkable on thisroom.WalkAreaMask and dos_walkmask_gen is bumped -- what a
   DrawingSurface on the walkable mask does on release. On vs off must be EQUAL, the first request a rebuild.
 - DOSAGS_LAB_RPW_NOGUARD=1 (with MASKCHG, lever on only): after the change, the cache is re-stamped with the new mask's
   serial (the guard defeated). The gate must DIFF.
 - DOSAGS_LABCLICKS=G / =V: R3LAND's fixtures G and V (as LAB-R2B's overlay spells them)
 - "DOS-PORT labrpw lc= room= what= px= py=" for every knob action.
Usage: apply-overlay-l1r.py VENDOR_AGS_ROOT"""
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
        // L1R OVERLAY: R3LAND's fixtures G and V (LAB-R2B's spelling of them)
        static const char *k_g = "5600:160:150:0,5700:100:180:0,5800:290:170:0,5900:160:100:0,6000:60:135,6400:250:135,"
            "6800:1:135,7100:60:160:0,7200:200:190:0,7300:160:80:0,7500:40:130,7900:300:130,8050:150:150:0,8150:150:60:0";
        static const char *k_v = "6000:60:135,6400:250:135,6800:1:135,7000:160:80:0,7400:65:166:0,7800:65:166,8200:200:170:0,"
            "8600:300:185:0,9000:25:155:0,9050:65:166:0,9100:110:178:0,9150:25:166:0,9200:65:178:0,9250:110:155:0";
        if (e && strcmp(e, "G") == 0) e = k_g;
        if (e && strcmp(e, "V") == 0) e = k_v;''')])

edit('Engine/ac/route_finder_impl_legacy.cpp', [(
'''static unsigned long long rp_pw_us = 0, rp_pw_max_us = 0;
''',
'''static unsigned long long rp_pw_us = 0, rp_pw_max_us = 0;
extern int dos_lab_rpw_px, dos_lab_rpw_py;   // L1R OVERLAY (ac/room.cpp)
'''), (
'''  if (rp_pw_pending)
    rp_pw_first_none++; // the previous warm was never asked about''',
'''  {   // L1R OVERLAY: control C1, a stale warm stamped as current
    static int stale = -1;
    if (stale < 0) { const char *e = getenv("DOSAGS_LAB_RPW_STALE"); stale = (e && e[0] == '1') ? 1 : 0; }
    if (stale && dos_lab_rpw_px >= 0)
    {
      Bitmap *c = BitmapHelper::CreateBitmapCopy(mask, 8);
      c->FillRect(Rect(dos_lab_rpw_px - 20, dos_lab_rpw_py - 6, dos_lab_rpw_px + 20, dos_lab_rpw_py + 6), 0);
      int cx = -1, cy = -1;
      for (int y = 0; y < c->GetHeight() && cx < 0; y++)
        for (int x = 0; x < c->GetWidth(); x++)
          if (c->GetScanLine(y)[x] > 0) { cx = x; cy = y; break; }
      rp_req_mask = nullptr;
      if (cx >= 0) is_route_possible(c, cx, cy, cx, cy, _pfc);
      rp_req_mask = nullptr;
      rp_cache_serial = dos_walktemp_serial; // the lie: this cache describes the live mask
      delete c;
      AGS::Common::Debug::Printf("DOS-PORT labrpw what=stale px=%d py=%d serial=%lu", dos_lab_rpw_px, dos_lab_rpw_py, rp_cache_serial);
      rp_pw_n++; rp_pw_pending = 1;
      return true;
    }
  }
  if (rp_pw_pending)
    rp_pw_first_none++; // the previous warm was never asked about'''), (
'''static int is_route_possible_flood(Bitmap *tempw, int fromx, int fromy, int tox, int toy, const LegacyRouteFinder::PathfinderConfig &pfc)
{''',
'''void dos_rp_lab_stamp() // L1R OVERLAY: guard F1 disabled -- the cache claims the live mask's serial
{
  rp_cache_serial = dos_walktemp_serial;
}

static int is_route_possible_flood(Bitmap *tempw, int fromx, int fromy, int tox, int toy, const LegacyRouteFinder::PathfinderConfig &pfc)
{''')])

edit('Engine/ac/room.cpp', [(
'''    if (!room_pathfinder->DosPrewarm(prepare_walkable_areas(game.playercharacter)))
        dos_route_prewarm_skipped++;
}''',
'''    extern int dos_lab_rpw_px, dos_lab_rpw_py;   // L1R OVERLAY: the player, mask coords, for C1
    dos_lab_rpw_px = room_to_mask_coord(playerchar->x); dos_lab_rpw_py = room_to_mask_coord(playerchar->y);
    if (!room_pathfinder->DosPrewarm(prepare_walkable_areas(game.playercharacter)))
        dos_route_prewarm_skipped++;
}
int dos_lab_rpw_px = -1, dos_lab_rpw_py = -1;   // L1R OVERLAY
namespace AGS { namespace Engine { void dos_rp_lab_stamp(); } }
// L1R OVERLAY: guard F1 (both arms) and its disabled form, right after the warm point
void dos_lab_rpw_after()
{
    static int chg = -1, nog = -1;
    if (chg < 0) { const char *e = getenv("DOSAGS_LAB_RPW_MASKCHG"); chg = (e && e[0] == '1') ? 1 : 0;
                   e = getenv("DOSAGS_LAB_RPW_NOGUARD"); nog = (e && e[0] == '1') ? 1 : 0; }
    if (!chg || displayed_room < 0 || !thisroom.WalkAreaMask) return;
    const int px = room_to_mask_coord(playerchar->x), py = room_to_mask_coord(playerchar->y);
    thisroom.WalkAreaMask->FillRect(Rect(px - 40, py - 4, px - 31, py + 4), 0);
    { extern unsigned long dos_walkmask_gen; dos_walkmask_gen++; }
    Debug::Printf("DOS-PORT labrpw lc=%ld room=%d what=maskchg px=%d py=%d", (long)get_loop_counter(), displayed_room, px, py);
    if (nog && dos_route_prewarm_mode() == 1 && room_pathfinder)
    {
        prepare_walkable_areas(game.playercharacter);   // the post-change mask takes a new serial
        AGS::Engine::dos_rp_lab_stamp();
        Debug::Printf("DOS-PORT labrpw lc=%ld room=%d what=noguard", (long)get_loop_counter(), displayed_room);
    }
}''')])

edit('Engine/ac/event.cpp', [(
'''void dos_route_prewarm();   // DOS-PORT patch 0371 (ac/room.cpp)''',
'''void dos_route_prewarm();   // DOS-PORT patch 0371 (ac/room.cpp)
void dos_lab_rpw_after();   // L1R OVERLAY'''), (
'''        dos_route_prewarm();   // DOS-PORT patch 0371: no-op unless DOSAGS_ROUTE_PREWARM=1''',
'''        dos_route_prewarm();   // DOS-PORT patch 0371: no-op unless DOSAGS_ROUTE_PREWARM=1
        dos_lab_rpw_after();   // L1R OVERLAY''')])
print('L1R overlay applied')
