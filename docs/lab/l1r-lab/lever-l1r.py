#!/usr/bin/env python3
"""Lab lever L1R (LAB-RB L1): pre-warm the legacy pathfinder's per-mask cache in the room-load / restore stall.
Applies to vendor/ags in place (uncommitted), over 0001-0369. Never landed from here (the port patch would be 0371).

DOSAGS_ROUTE_PREWARM: unset or 0 = off (the 0369 head), 1 = on. When the FadeIn event is processed (event.cpp; queued by
GameUpdateProcessEvents for a new room after its BeforeFadein event, and for a restored save) the engine prepares the
walkable mask for the player character (prepare_walkable_areas, as move_character_impl does) and calls the legacy
finder's unchanged is_route_possible() once on it, with source = destination = the first walkable pixel. That runs the
same 0211 analysis + 0319 labels the first request on that mask would run, and records the same serial. The request
path is untouched: every request still matches the cache by serial or byte compare (0211/0317/0319) or rebuilds it.
Witness: "DOS-PORT routeprewarm DOSAGS_ROUTE_PREWARM=<v|(default)> mode=<n>" (first room load); RUNMANI:
"DOS-PORT routeprewarm_final mode= prewarms= built= matched= nowalk= skipped= us= max_us= first_serial= first_compare=
first_miss= first_none= pending=" (first_*: how the first is_route_possible after each warm found the cache).
Usage: lever-l1r.py VENDOR_AGS_ROOT"""
import sys
root = sys.argv[1]


def edit(rel, pairs):
    p = root + '/' + rel; s = open(p).read()
    for a, b in pairs:
        assert s.count(a) == 1, (rel, a[:80]); s = s.replace(a, b, 1)
    open(p, 'w').write(s)


edit('Engine/ac/route_finder.h', [(
'''    void SetWalkableArea(const AGS::Common::Bitmap *walkablearea, int coord_scale = 1);
''',
'''    void SetWalkableArea(const AGS::Common::Bitmap *walkablearea, int coord_scale = 1);
#ifdef __DJGPP__
    // DOS-PORT lab L1R: build this finder's per-mask analysis for `mask` now, exactly as the first request on that mask
    // would; false when the implementation keeps none. Requests still validate it against their own mask.
    virtual bool DosPrewarm(const AGS::Common::Bitmap *mask) { (void)mask; return false; }
#endif
''')])

edit('Engine/ac/route_finder_impl_legacy.h', [(
'''    void Configure(GameDataVersion game_ver) override;
''',
'''    void Configure(GameDataVersion game_ver) override;
#ifdef __DJGPP__
    bool DosPrewarm(const Common::Bitmap *mask) override;   // DOS-PORT lab L1R
#endif
''')])

edit('Engine/ac/route_finder_impl_legacy.cpp', [(
'''extern unsigned long dos_walktemp_serial;
''',
'''extern unsigned long dos_walktemp_serial;
// DOS-PORT lab L1R: the pre-warm's counters (reported by dos_rp_report); mode and skipped live in ac/room.cpp
extern int dos_route_prewarm_mode();
extern long dos_route_prewarm_skipped;
static long rp_pw_n = 0, rp_pw_builds = 0, rp_pw_built = 0, rp_pw_nowalk = 0;
static long rp_pw_first_serial = 0, rp_pw_first_compare = 0, rp_pw_first_miss = 0, rp_pw_first_none = 0;
static int rp_pw_pending = 0;
static unsigned long long rp_pw_us = 0, rp_pw_max_us = 0;
'''), (
'''      rp_fast, rp_n_serial_hits, rp_n_compares, rp_n_label_answers, rp_n_verified, rp_n_serial_mismatch, rp_n_label_mismatch, rp_labels_ok ? 1 : 0, rp_label_us);
''',
'''      rp_fast, rp_n_serial_hits, rp_n_compares, rp_n_label_answers, rp_n_verified, rp_n_serial_mismatch, rp_n_label_mismatch, rp_labels_ok ? 1 : 0, rp_label_us);
  if (log) // DOS-PORT lab L1R
    fprintf(log, "DOS-PORT routeprewarm_final mode=%d prewarms=%ld built=%ld matched=%ld nowalk=%ld skipped=%ld us=%llu max_us=%llu first_serial=%ld first_compare=%ld first_miss=%ld first_none=%ld pending=%d\\n",
      dos_route_prewarm_mode(), rp_pw_n, rp_pw_built, rp_pw_n - rp_pw_built, rp_pw_nowalk, dos_route_prewarm_skipped, rp_pw_us,
      rp_pw_max_us, rp_pw_first_serial, rp_pw_first_compare, rp_pw_first_miss, rp_pw_first_none, rp_pw_pending);
'''), (
'''  bool hit = (rp_req_mask == wallscreen && rp_cache_src != nullptr && rp_cache_maxgran == pfc.MaxGranularity);
  if (!hit && serial_hit)
  {
    hit = true;''',
'''  bool hit = (rp_req_mask == wallscreen && rp_cache_src != nullptr && rp_cache_maxgran == pfc.MaxGranularity);
  bool pw_by_serial = false; // DOS-PORT lab L1R: observed only
  if (!hit && serial_hit)
  {
    hit = true;
    pw_by_serial = true;'''), (
'''    if (hit)
      rp_cache_serial = (wallscreen == walkable_areas_temp) ? dos_walktemp_serial : 0; // 0319 (A)
  }''',
'''    if (hit)
      rp_cache_serial = (wallscreen == walkable_areas_temp) ? dos_walktemp_serial : 0; // 0319 (A)
  }
  if (rp_pw_pending) // DOS-PORT lab L1R: how the first request after a warm found the cache (counted, never acted on)
  {
    rp_pw_pending = 0;
    if (!hit) rp_pw_first_miss++;
    else if (pw_by_serial) rp_pw_first_serial++;
    else rp_pw_first_compare++;
  }'''), (
'''  // DOS-PORT patch 0211: keep the analysis for the next call on the same mask
  delete rp_cache_src;''',
'''  // DOS-PORT patch 0211: keep the analysis for the next call on the same mask
  rp_pw_builds++; // DOS-PORT lab L1R: counted only
  delete rp_cache_src;'''), (
'''static int is_route_possible_flood(Bitmap *tempw, int fromx, int fromy, int tox, int toy, const LegacyRouteFinder::PathfinderConfig &pfc)
{''',
'''#ifdef __DJGPP__
// DOS-PORT lab L1R: run the first request's is_route_possible() now, on the mask that request will be given, with
// source = destination = the first walkable pixel (a trivial question the analysis must still be built to answer).
// rp_req_mask is cleared before and after, as FindRouteImpl clears it at the start of every request; suggestx/suggesty
// and walk_area_granularity[] are rewritten by every request before they are read.
bool LegacyRouteFinder::DosPrewarm(const Bitmap *mask)
{
  if (!mask || mask->GetColorDepth() != 8)
    return false;
  const uclock_t t0 = uclock();
  int fx = -1, fy = -1;
  for (int y = 0; y < mask->GetHeight() && fx < 0; y++)
  {
    const uint8_t *s = mask->GetScanLine(y);
    for (int x = 0; x < mask->GetWidth(); x++)
      if (s[x] > 0) { fx = x; fy = y; break; }
  }
  if (fx < 0)
  {
    rp_pw_nowalk++; // nothing walkable: a request would return before the analysis too
    return false;
  }
  if (rp_pw_pending)
    rp_pw_first_none++; // the previous warm was never asked about
  rp_pw_pending = 0;
  const long b0 = rp_pw_builds;
  rp_req_mask = nullptr;
  is_route_possible(mask, fx, fy, fx, fy, _pfc);
  rp_req_mask = nullptr;
  if (rp_pw_builds != b0)
    rp_pw_built++;
  rp_pw_n++;
  rp_pw_pending = 1;
  long long d = (long long)(uclock() - t0) * 1000000LL / UCLOCKS_PER_SEC;
  if (d < 0) d = 0;
  rp_pw_us += (unsigned long long)d;
  if ((unsigned long long)d > rp_pw_max_us) rp_pw_max_us = (unsigned long long)d;
  return true;
}
#endif

static int is_route_possible_flood(Bitmap *tempw, int fromx, int fromy, int tox, int toy, const LegacyRouteFinder::PathfinderConfig &pfc)
{''')])

edit('Engine/ac/room.cpp', [(
'''void init_room_pathfinder()
{''',
'''#ifdef __DJGPP__
// DOS-PORT lab L1R: DOSAGS_ROUTE_PREWARM (unset/0 = off, 1 = on); see dos_route_prewarm()
static int dos_route_prewarm_mode_v = -1;
long dos_route_prewarm_skipped = 0;   // FadeIns with the lever on but no legacy pathfinder / no room
int dos_route_prewarm_mode()
{
    if (dos_route_prewarm_mode_v < 0)
    {
        const char *e = getenv("DOSAGS_ROUTE_PREWARM");
        dos_route_prewarm_mode_v = (e && e[0] == '1' && e[1] == 0) ? 1 : 0;
        Debug::Printf(kDbgMsg_Info, "DOS-PORT routeprewarm DOSAGS_ROUTE_PREWARM=%s mode=%d", e ? e : "(default)",
            dos_route_prewarm_mode_v);
    }
    return dos_route_prewarm_mode_v;
}
// Called when the FadeIn event is processed (ac/event.cpp): after a room load (its BeforeFadein event has run) and after
// a save restore, before the fade-in and before the room's first tick. Prepares the walkable mask for the player, as
// move_character_impl() does for the player's walk, and has the pathfinder build its per-mask analysis for it.
void dos_route_prewarm()
{
    if (dos_route_prewarm_mode() != 1)
        return;
    if (displayed_room < 0 || !room_pathfinder || game.playercharacter < 0)
    {
        dos_route_prewarm_skipped++;
        return;
    }
    if (!room_pathfinder->DosPrewarm(prepare_walkable_areas(game.playercharacter)))
        dos_route_prewarm_skipped++;
}
#endif

void init_room_pathfinder()
{
#ifdef __DJGPP__
    dos_route_prewarm_mode();   // DOS-PORT lab L1R: the witness line, once
#endif''')])

edit('Engine/ac/event.cpp', [(
'''void process_event(const AGSEvent *evp)
{''',
'''#ifdef __DJGPP__
void dos_route_prewarm();   // DOS-PORT lab L1R (ac/room.cpp)
#endif

void process_event(const AGSEvent *evp)
{'''), (
'''    else if (evp->Type == kAGSEvent_FadeIn)
    {
        current_fade_in_effect();''',
'''    else if (evp->Type == kAGSEvent_FadeIn)
    {
#ifdef __DJGPP__
        dos_route_prewarm();   // DOS-PORT lab L1R: no-op unless DOSAGS_ROUTE_PREWARM=1
#endif
        current_fade_in_effect();''')])

edit('Engine/main/quit.cpp', [(
'''            "DOSAGS_PRESENT_VERIFY",  // patch 0192: reads the surface twice per present -- a diagnostic, never a timed cell
''',
'''            "DOSAGS_PRESENT_VERIFY",  // patch 0192: reads the surface twice per present -- a diagnostic, never a timed cell
            "DOSAGS_ROUTE_PREWARM",   // lab L1R: route-cache pre-warm in the room-load / restore stall (off by default)
''')])
print('lever L1R applied')
