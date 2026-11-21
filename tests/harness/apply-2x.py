#!/usr/bin/env python3
"""apply-2x.py VENDOR_AGS -- the narrowed integer-2x present (SCALE2-NARROW) for the DOSBox-X gate and a later 486 A/B
(pre-registration: SCRATCH/2x/PREREG-2X.md; scope: SCOPE-2X.md). A LAB OVERLAY applied to main's 0383 tree in place, like
apply-pace-rig.py; never a patch without a new operator ruling, never in a release. Edits Engine/gfx/ali3dsw.cpp and
Engine/main/quit.cpp.

  DOSAGS_SCALE2_NARROW=1   (exactly "1"; default OFF) at an EXACT uniform 2x render frame (dst.w == 2 * vscreen w and
                           dst.h == 2 * vscreen h), on a present whose
                             - virtual screen is the one presented (no flip scratch), formats equal, 1/2/4 bytes a pixel,
                             - dst lies inside the window and its margins are already clean (0100),
                             - window surface still holds scale2(virtual screen) at this geometry (the LATCH, below),
                             - frame went through the scene path, nothing latched full, the dirty set is valid
                               (the same predicates 0124 narrows on at 1x; DOSAGS_DIRTY_PRESENT=0 switches it off too),
                           scale-blits ONLY the dirty boxes (game coordinates, clamped to the GAME size, not dst) into the
                           window surface at (dst.x + 2*x1, dst.y + 2*y1, 2*w, 2*h) and pushes exactly those rects.
                           Such a present skips 0091/0102's unchanged-frame check (the dirty set makes it redundant) and
                           invalidates its cache; a present that cannot narrow keeps the check, so an 8-bit fade keeps
                           0104's palette-only present.
                           Box choice: the clamped box set when its area is under the screen's, else the clamped bbox when
                           smaller than the screen (0124's rule), else full. (At 1x an UNBORDERED frame narrows on the bbox
                           alone; here the box set is used whenever it is valid, as 1x already does for a bordered frame.)
                           Every full 2x present (any present at that geometry that does not narrow) goes through a new
                           dword-store replicator (both output rows written directly, no row buffer, no per-row clock
                           reads) in place of 0087/0090's loops; the narrowed boxes use the same code.
                           The LATCH is armed only by that full replicator on the virtual screen at this geometry (window
                           surface + pixels + size + pitch, virtual-screen surface + pixels + size, dst), and dropped by any
                           other write to the window surface (a generic blit, a flip, another geometry, 1x), by
                           SetDisplayMode and by CreateVirtualScreen.
                           0193's carry merge moves ahead of the unchanged-frame check on 2x presents (switch on only) so
                           the decision sees the carried boxes; the 0124 block then does not merge again.
  DOSAGS_SCALE2_VERIFY=1   diagnostic, DOSBox-X only, never timed: after every 2x present that leaves the latch armed,
                           compare the WHOLE dst against scale2(virtual screen) pixel by pixel (not vacuous, unlike 0192).
  DOSAGS_SCALE2_BREAK=1    CONTROL ONLY (information since FIX-UP 2): each narrowed box is blitted one source column and
                           row short (pushed in full). Gate run 1 (gate1/) showed it has no power: a dirty box's last column
                           and row usually hold unchanged pixels, so nothing goes stale.
  DOSAGS_SCALE2_BREAK=2    CONTROL ONLY (FIX-UP 2, the registered control): the LAST box of every narrowed present is not
                           blitted at all but is still pushed -- a whole missed region the screen-equality gate and the
                           verifier must both see. Information since FIX-UP 3: gate run 2 (gate2/) showed it has no power
                           on B16-2x-walk -- the last box is a static re-invalidated object or a carried box whose region is
                           already up to date; it held a changed pixel on 0 of 1039 presents (diag-2x-boxes.py).
  DOSAGS_SCALE2_BREAK=3    CONTROL ONLY (FIX-UP 3, the registered control): NO box of any narrowed present is blitted, but
                           every box is still pushed -- the narrowed path writes nothing. The window then changes only on
                           full presents, so the stale set is exactly every pixel the virtual screen changed since the last
                           full present: empty only if the row gave the narrowed path nothing to draw. Any other value: off.
  Unset (all): no present-path behaviour changes. Costs: one static compare in Present() and in TryFast's 2x path, a
                           `!false` in the 0091 clean_case, a store in SetDisplayMode / CreateVirtualScreen. No log line.
Exit line (RUNMANI.LOG, switch on only, both flavours):
  "DOS-PORT scale2 on=1 break= verify= narrow= full= fullfast= pal= rects= px_src= skipcheck= rej geom= hint= fmt=
   nolatch= noscene= latched= norects= whole= latch_sets= latch_drops= vfy= vfy_bad= vfy_bad_px= vfy_first="
  narrow  = presents scale-blitted + pushed as boxes; rects / px_src = their boxes and SOURCE pixels (window px = 4x)
  full    = 2x-geometry presents that blitted in full (any path); fullfast = full blits by the new replicator (any geometry
            that reaches TryFast at scale 2, incl. a flip scratch)
  pal     = 0104 palette-only presents seen with the switch on (nothing written)
  skipcheck = narrowed presents on which 0102 would have run the unchanged-frame check (8-bit 320x240: all of them)
  rej *   = per-decision reasons a present did not narrow (geom: not exact 2x; hint: DOSAGS_DIRTY_PRESENT=0; fmt: flip,
            format, depth, dst outside, margins not clean; nolatch; noscene; latched (is_full); norects; whole: the box
            set and the bbox both cover the screen). They count decisions, so they include presents 0091 then skipped.
  latch_sets = full replicator presents that (re)armed the latch; latch_drops = armed -> dropped transitions
  vfy* = DOSAGS_SCALE2_VERIFY: presents checked, presents with a mismatch, mismatching source px, first bad check index
The dirtypresent counters (instrumented flavour) stay consistent: a narrowed 2x present counts as narrow (px_narrow in
game px) and NOT as rej scaled; every other 2x present still counts rej scaled.
RUNMANIFEST env allowlist: DOSAGS_SCALE2_BREAK / _NARROW / _VERIFY are hashed (unset contributes nothing)."""
import sys

V = sys.argv[1]
P_SW = V + '/Engine/gfx/ali3dsw.cpp'
P_QT = V + '/Engine/main/quit.cpp'
sw = open(P_SW, encoding='ascii', newline='').read()
qt = open(P_QT, encoding='ascii', newline='').read()
N = {'sw': 0, 'qt': 0}


def rep(which, src, a, b):
    assert src.count(a) == 1, (which, a[:70], src.count(a))
    assert a != b
    N[which] += 1
    return src.replace(a, b, 1)


# ---- 1. global state, the latch and the exit line (beside 0366's guiclip summary; quit.cpp's extern finds it) ----
sw = rep('sw', sw, '''        dos_gc_boxed, dos_gc_boxes, dos_gc_fb_coarse, dos_gc_fb_whole, dos_gc_span_stretch, dos_gc_coarse_restores);
}
#endif
''', '''        dos_gc_boxed, dos_gc_boxes, dos_gc_fb_coarse, dos_gc_fb_whole, dos_gc_span_stretch, dos_gc_coarse_restores);
}
// ---- SCALE2-NARROW (lab overlay apply-2x.py; DOSAGS_SCALE2_NARROW=1, default off): its switches, counters, latch
// and exit line. Global scope so quit.cpp's block-scope extern finds dos_scale2_summary.
struct DosScale2Stats
{
    long narrow = 0, full = 0, fullfast = 0, pal = 0, rects = 0, skipcheck = 0;
    long long px_src = 0;
    long rej_geom = 0, rej_hint = 0, rej_fmt = 0, rej_nolatch = 0, rej_noscene = 0, rej_latched = 0;
    long rej_norects = 0, rej_whole = 0;
    long latch_sets = 0, latch_drops = 0;
    long vfy = 0, vfy_bad = 0, vfy_first = -1, vfy_logged = 0;
    long long vfy_bad_px = 0;
};
static DosScale2Stats dos_s2;
static int dos_s2_mode = -1, dos_s2_break = 0, dos_s2_verify_on = 0, dos_s2_hint = 1;
static bool dos_s2_full_done = false;   // the full replicator ran in this present (set in TryFast, read in Present)
static void dos_s2_init()
{
    if (dos_s2_mode >= 0) return;
    const char *e = getenv("DOSAGS_SCALE2_NARROW");
    dos_s2_mode = (e && e[0] == '1' && e[1] == 0) ? 1 : 0;
    e = getenv("DOSAGS_SCALE2_BREAK");
    dos_s2_break = (e && e[0] >= '1' && e[0] <= '3' && e[1] == 0) ? e[0] - '0' : 0;   // FIX-UP 2: 2; FIX-UP 3: 3
    e = getenv("DOSAGS_SCALE2_VERIFY");
    dos_s2_verify_on = (e && e[0] == '1') ? 1 : 0;
    e = getenv("DOSAGS_DIRTY_PRESENT");   // read exactly as 0124 reads it
    dos_s2_hint = !(e && e[0] == '0');
}
static inline bool dos_s2_on() { if (dos_s2_mode < 0) dos_s2_init(); return dos_s2_mode == 1; }
// The latch: the window surface holds scale2(virtual screen) inside dst, at exactly this geometry.
struct DosScale2Latch
{
    bool valid = false;
    SDL_Surface *win = nullptr; void *win_px = nullptr; int ww = 0, wh = 0, wp = 0;
    SDL_Surface *src = nullptr; void *src_px = nullptr; int sw = 0, sh = 0;
    SDL_Rect dst = { 0, 0, 0, 0 };
};
static DosScale2Latch dos_s2_latch;
static bool dos_s2_latch_ok(SDL_Surface *win, SDL_Surface *src, const SDL_Rect &dst)
{
    const DosScale2Latch &l = dos_s2_latch;
    return l.valid && l.win == win && l.win_px == win->pixels && l.ww == win->w && l.wh == win->h && l.wp == win->pitch &&
        l.src == src && l.src_px == src->pixels && l.sw == src->w && l.sh == src->h &&
        l.dst.x == dst.x && l.dst.y == dst.y && l.dst.w == dst.w && l.dst.h == dst.h;
}
static void dos_s2_latch_set(SDL_Surface *win, SDL_Surface *src, const SDL_Rect &dst)
{
    DosScale2Latch &l = dos_s2_latch;
    l.win = win; l.win_px = win->pixels; l.ww = win->w; l.wh = win->h; l.wp = win->pitch;
    l.src = src; l.src_px = src->pixels; l.sw = src->w; l.sh = src->h;
    l.dst = dst;
    l.valid = true;
    dos_s2.latch_sets++;
}
static void dos_s2_latch_drop()
{
    if (dos_s2_latch.valid) { dos_s2_latch.valid = false; dos_s2.latch_drops++; }
}
void dos_scale2_summary(FILE *log)
{
    if (!log || !dos_s2_on()) return;
    const DosScale2Stats &s = dos_s2;
    fprintf(log, "DOS-PORT scale2 on=1 break=%d verify=%d narrow=%ld full=%ld fullfast=%ld pal=%ld rects=%ld px_src=%lld"
        " skipcheck=%ld rej geom=%ld hint=%ld fmt=%ld nolatch=%ld noscene=%ld latched=%ld norects=%ld whole=%ld"
        " latch_sets=%ld latch_drops=%ld vfy=%ld vfy_bad=%ld vfy_bad_px=%lld vfy_first=%ld\\n",
        dos_s2_break, dos_s2_verify_on, s.narrow, s.full, s.fullfast, s.pal, s.rects, s.px_src,
        s.skipcheck, s.rej_geom, s.rej_hint, s.rej_fmt, s.rej_nolatch, s.rej_noscene, s.rej_latched, s.rej_norects,
        s.rej_whole, s.latch_sets, s.latch_drops, s.vfy, s.vfy_bad, s.vfy_bad_px, s.vfy_first);
}
#endif
''')

# ---- 2. a mode set and a new virtual screen drop the latch (the identity keys catch both unless an allocator hands
# back the same addresses; this closes that) ----
sw = rep('sw', sw, '''bool SDLRendererGraphicsDriver::SetDisplayMode(const DisplayMode &mode)
{
''', '''bool SDLRendererGraphicsDriver::SetDisplayMode(const DisplayMode &mode)
{
#ifdef __DJGPP__
  dos_s2_latch_drop();   // SCALE2-NARROW
#endif
''')
sw = rep('sw', sw, '''  DestroyVirtualScreen();
  // Initialize virtual screen; size is equal to native resolution
''', '''  DestroyVirtualScreen();
#ifdef __DJGPP__
  dos_s2_latch_drop();   // SCALE2-NARROW
#endif
  // Initialize virtual screen; size is equal to native resolution
''')

# ---- 3. the replicator, the box set, the box blit and the verifier (before TryFast, which calls the replicator) ----
sw = rep('sw', sw, '''#ifdef __DJGPP__
// DOS-PORT patch 0087 (8-bit optimization pass, step C): fast integer
''', '''#ifdef __DJGPP__
// ---- SCALE2-NARROW (apply-2x.py): exact 2x nearest replication of one SOURCE rect (x, y, w, h) of sp into dp, where
// dp is the window surface at dst's top-left. Both output rows are written directly with dword stores: 8 bit, four
// source px -> two Uint32 (a,a,b,b)(c,c,d,d) per row, a 16-bit store for a 2-byte-aligned head and for the tail;
// 16 bit, one px -> one Uint32 (p | p << 16); 32 bit, one px -> two Uint32. Shifts only (no multiply: imul is 13-42
// clocks on the 486). Every output pixel belongs to exactly one source pixel, so there is no rounding.
typedef Uint16 __attribute__((__may_alias__)) dos_s2_u16;
typedef Uint32 __attribute__((__may_alias__)) dos_s2_u32;
static void dos_s2_blit_rect(const Uint8 *sp, int spitch, Uint8 *dp, int dpitch, int bpp, int x, int y, int w, int h)
{
    if (w <= 0 || h <= 0)
        return;
    for (int j = 0; j < h; ++j)
    {
        const Uint8 *s = sp + (size_t)(y + j) * (size_t)spitch + (size_t)x * (size_t)bpp;
        Uint8 *d0 = dp + (size_t)(2 * (y + j)) * (size_t)dpitch + (size_t)(2 * x) * (size_t)bpp;
        Uint8 *d1 = d0 + dpitch;
        int n = w;
        if (bpp == 1)
        {
            if ((((size_t)d0) & 2) != 0)
            {
                const Uint16 v = (Uint16)(s[0] | (s[0] << 8));
                *(dos_s2_u16 *)d0 = v; *(dos_s2_u16 *)d1 = v;
                ++s; d0 += 2; d1 += 2; --n;
            }
            for (; n >= 4; n -= 4)
            {
                const Uint32 q = *(const dos_s2_u32 *)s;                         // bytes a b c d
                const Uint32 lo = (q & 0xffu) | ((q & 0xff00u) << 8);            // a at byte 0, b at byte 2
                const Uint32 hi = ((q >> 16) & 0xffu) | ((q >> 8) & 0xff0000u);  // c at byte 0, d at byte 2
                const Uint32 v0 = lo | (lo << 8), v1 = hi | (hi << 8);          // a a b b, c c d d
                ((dos_s2_u32 *)d0)[0] = v0; ((dos_s2_u32 *)d0)[1] = v1;
                ((dos_s2_u32 *)d1)[0] = v0; ((dos_s2_u32 *)d1)[1] = v1;
                s += 4; d0 += 8; d1 += 8;
            }
            for (; n > 0; --n)
            {
                const Uint16 v = (Uint16)(s[0] | (s[0] << 8));
                *(dos_s2_u16 *)d0 = v; *(dos_s2_u16 *)d1 = v;
                ++s; d0 += 2; d1 += 2;
            }
        }
        else if (bpp == 2)
        {
            const dos_s2_u16 *s16 = (const dos_s2_u16 *)s;
            dos_s2_u32 *o0 = (dos_s2_u32 *)d0, *o1 = (dos_s2_u32 *)d1;
            for (int i = 0; i < n; ++i)
            {
                const Uint32 p = s16[i];
                const Uint32 v = p | (p << 16);
                o0[i] = v; o1[i] = v;
            }
        }
        else
        {
            const dos_s2_u32 *s32 = (const dos_s2_u32 *)s;
            dos_s2_u32 *o0 = (dos_s2_u32 *)d0, *o1 = (dos_s2_u32 *)d1;
            for (int i = 0; i < n; ++i)
            {
                const Uint32 p = s32[i];
                o0[2 * i] = p; o0[2 * i + 1] = p;
                o1[2 * i] = p; o1[2 * i + 1] = p;
            }
        }
    }
}

// The box set this present narrows to, in GAME coordinates clamped to the virtual screen (gw x gh) -- not to dst, which
// is the game size only at 1x (0131's clamps). Returns 0 when neither the set nor the bbox is smaller than the screen.
static int dos_s2_boxes(int gw, int gh, DosPortDirtyBox *out)
{
    long long area = 0;
    int n = 0;
    for (int i = 0; i < dos_port_dirty.nbox; ++i)
    {
        int x1 = dos_port_dirty.box[i].x1, y1 = dos_port_dirty.box[i].y1;
        int x2 = dos_port_dirty.box[i].x2, y2 = dos_port_dirty.box[i].y2;
        if (x1 < 0) x1 = 0;
        if (y1 < 0) y1 = 0;
        if (x2 > gw - 1) x2 = gw - 1;
        if (y2 > gh - 1) y2 = gh - 1;
        if (x2 < x1 || y2 < y1)
            continue;   // wholly off the virtual screen
        out[n].x1 = x1; out[n].y1 = y1; out[n].x2 = x2; out[n].y2 = y2;
        ++n;
        area += (long long)(x2 - x1 + 1) * (y2 - y1 + 1);
    }
    if (n > 0 && area < (long long)gw * gh)
        return n;
    int x1 = dos_port_dirty.x1, y1 = dos_port_dirty.y1, x2 = dos_port_dirty.x2, y2 = dos_port_dirty.y2;
    if (x1 < 0) x1 = 0;
    if (y1 < 0) y1 = 0;
    if (x2 > gw - 1) x2 = gw - 1;
    if (y2 > gh - 1) y2 = gh - 1;
    if (x2 >= x1 && y2 >= y1 && (long long)(x2 - x1 + 1) * (y2 - y1 + 1) < (long long)gw * gh)
    {
        out[0].x1 = x1; out[0].y1 = y1; out[0].x2 = x2; out[0].y2 = y2;
        return 1;
    }
    return 0;
}

static bool dos_s2_blit_boxes(SDL_Surface *src, SDL_Surface *win, const SDL_Rect &dst, const DosPortDirtyBox *box, int n)
{
    const int bpp = SDL_BYTESPERPIXEL(src->format);
    if (bpp != 1 && bpp != 2 && bpp != 4)
        return false;
    const bool src_lock = SDL_MUSTLOCK(src);
    const bool dst_lock = SDL_MUSTLOCK(win);
    if (src_lock && !SDL_LockSurface(src))
        return false;
    if (dst_lock && !SDL_LockSurface(win))
    {
        if (src_lock) SDL_UnlockSurface(src);
        return false;
    }
    const uclock_t _ts = dos_port_fine_uclock();
    Uint8 *dp = (Uint8 *)win->pixels + (size_t)dst.y * (size_t)win->pitch + (size_t)dst.x * (size_t)bpp;
    for (int i = 0; i < n; ++i)
    {
        int w = box[i].x2 - box[i].x1 + 1, h = box[i].y2 - box[i].y1 + 1;
        if (dos_s2_break == 1) { if (w > 1) --w; if (h > 1) --h; }   // CONTROL ONLY (DOSAGS_SCALE2_BREAK=1)
        if (dos_s2_break == 2 && i == n - 1) continue;   // CONTROL ONLY (DOSAGS_SCALE2_BREAK=2): last box not blitted
        if (dos_s2_break == 3) continue;   // CONTROL ONLY (DOSAGS_SCALE2_BREAK=3, FIX-UP 3): no box blitted
        dos_s2_blit_rect((const Uint8 *)src->pixels, src->pitch, dp, win->pitch, bpp, box[i].x1, box[i].y1, w, h);
    }
    dos_port_tick_record_us(dos_port_tick_timing.fastblit_hreplicate, dos_port_fine_elapsed_us(_ts));
    dos_port_tick_record_us(dos_port_tick_timing.fastblit_vmemcpy, 0);
    if (dst_lock) SDL_UnlockSurface(win);
    if (src_lock) SDL_UnlockSurface(src);
    return true;
}

// DOSAGS_SCALE2_VERIFY=1: the whole dst against scale2(src), every one of the four window px of every source px.
static void dos_s2_verify(SDL_Surface *src, SDL_Surface *win, const SDL_Rect &dst)
{
    const int bpp = SDL_BYTESPERPIXEL(src->format);
    long bad = 0;
    int bx1 = 1 << 30, by1 = 1 << 30, bx2 = -1, by2 = -1;
    const Uint8 *base = (const Uint8 *)win->pixels + (size_t)dst.y * (size_t)win->pitch + (size_t)dst.x * (size_t)bpp;
    for (int y = 0; y < src->h; ++y)
    {
        const Uint8 *s = (const Uint8 *)src->pixels + (size_t)y * (size_t)src->pitch;
        const Uint8 *d0 = base + (size_t)(2 * y) * (size_t)win->pitch;
        const Uint8 *d1 = d0 + win->pitch;
        for (int x = 0; x < src->w; ++x)
        {
            const Uint8 *p = s + (size_t)x * (size_t)bpp;
            const size_t o = (size_t)(2 * x) * (size_t)bpp;
            if (std::memcmp(p, d0 + o, bpp) != 0 || std::memcmp(p, d0 + o + bpp, bpp) != 0 ||
                std::memcmp(p, d1 + o, bpp) != 0 || std::memcmp(p, d1 + o + bpp, bpp) != 0)
            {
                bad++;
                if (x < bx1) bx1 = x;
                if (x > bx2) bx2 = x;
                if (y < by1) by1 = y;
                if (y > by2) by2 = y;
            }
        }
    }
    dos_s2.vfy++;
    if (bad > 0)
    {
        dos_s2.vfy_bad++;
        dos_s2.vfy_bad_px += bad;
        if (dos_s2.vfy_first < 0) dos_s2.vfy_first = dos_s2.vfy;
        if (dos_s2.vfy_logged < 12)
        {
            dos_s2.vfy_logged++;
            Debug::Printf("DOS-PORT scale2verify BAD check=%ld bad_px=%ld src_bbox=%d,%d..%d,%d",
                dos_s2.vfy, bad, bx1, by1, bx2, by2);
        }
    }
}

// DOS-PORT patch 0087 (8-bit optimization pass, step C): fast integer
''')

# ---- 4. the full-frame 2x through the replicator (TryFast, switch on only) ----
sw = rep('sw', sw, '''    const size_t dst_row_bytes = (size_t)src->w * (size_t)scale_x * bpp;
''', '''    const size_t dst_row_bytes = (size_t)src->w * (size_t)scale_x * bpp;

    if (scale_x == 2 && dos_s2_on() && (bpp == 1 || bpp == 2 || bpp == 4))
    {   // SCALE2-NARROW (apply-2x.py): the full-frame 2x through the same dword-store replicator as the boxes.
        // Accounted as one fastblit_hreplicate sample (replicate + both row writes); fastblit_vmemcpy 0.
        const uclock_t _ts = dos_port_fine_uclock();
        dos_s2_blit_rect(src_pixels, src->pitch, dst_pixels, dst->pitch, (int)bpp, 0, 0, src->w, src->h);
        dos_port_tick_record_us(dos_port_tick_timing.fastblit_hreplicate, dos_port_fine_elapsed_us(_ts));
        dos_port_tick_record_us(dos_port_tick_timing.fastblit_vmemcpy, 0);
        if (dst_lock) SDL_UnlockSurface(dst);
        if (src_lock) SDL_UnlockSurface(src);
        dos_s2.fullfast++;
        dos_s2_full_done = true;
        return true;
    }
''')

# ---- 5. the decision, ahead of 0091/0102's unchanged-frame check ----
sw = rep('sw', sw, '''    const size_t frame_bytes_for_skip = (size_t)blit_src->pitch * (size_t)blit_src->h;
''', '''    // ---- SCALE2-NARROW (apply-2x.py; DOSAGS_SCALE2_NARROW=1, default off): does this present narrow at 2x?
    // Decided BEFORE the unchanged-frame check, which a narrowing present skips (the dirty set says what changed).
    bool _s2_narrow = false;   // outside the guard: clean_case below reads it
#ifdef __DJGPP__
    bool _s2_cand = false;     // switch on and dst exactly 2x the presented surface
    bool _s2_merged = false;   // 0193's carry merged here; the 0124 block must not merge again
    int _s2_n = 0;             // boxes in _s2_box (GAME coordinates)
    DosPortDirtyBox _s2_box[DOS_PORT_DIRTY_MAX_BOXES];
    if (dos_s2_on())
    {
        dos_s2_full_done = false;
        _s2_cand = blit_src && dst.w == 2 * blit_src->w && dst.h == 2 * blit_src->h;
        if (!_s2_cand)
            dos_s2.rej_geom++;
        else
        {
            dos_port_dirty_merge_carry();   // patch 0193's merge, moved ahead of the check on 2x presents
            _s2_merged = true;
            const int _s2_bpp = SDL_BYTESPERPIXEL(blit_src->format);
            if (!dos_s2_hint)
                dos_s2.rej_hint++;
            else if (blit_src != _vscreenSurface || flip != kFlip_None || blit_src->format != win_surface->format ||
                     (_s2_bpp != 1 && _s2_bpp != 2 && _s2_bpp != 4) || !dst_inside || !margins_clean)
                dos_s2.rej_fmt++;
            else if (!dos_s2_latch_ok(win_surface, blit_src, dst))
                dos_s2.rej_nolatch++;
            else if (!dos_port_dirty.scene_path)
                dos_s2.rej_noscene++;
            else if (dos_port_dirty.is_full)
                dos_s2.rej_latched++;
            else if (!dos_port_dirty.valid || dos_port_dirty.nbox <= 0)
                dos_s2.rej_norects++;
            else
            {
                _s2_n = dos_s2_boxes(blit_src->w, blit_src->h, _s2_box);
                if (_s2_n > 0)
                {
                    _s2_narrow = true;
                    if (skip_allowed && (size_t)blit_src->pitch * (size_t)blit_src->h <= 100000u)
                        dos_s2.skipcheck++;   // 0102 would have run the check on this present
                }
                else
                    dos_s2.rej_whole++;
            }
        }
    }
#endif
    const size_t frame_bytes_for_skip = (size_t)blit_src->pitch * (size_t)blit_src->h;
''')
sw = rep('sw', sw, '''    const bool clean_case = skip_allowed && small_enough_to_check && (flip == kFlip_None) &&
''', '''    const bool clean_case = !_s2_narrow && skip_allowed && small_enough_to_check && (flip == kFlip_None) &&   // SCALE2
''')

# ---- 6. the blit: the boxes only on a narrowing present ----
sw = rep('sw', sw, '''        blitted = TryFastIntegerNearestBlit(blit_src, win_surface, dst);
''', '''        blitted = _s2_narrow ? dos_s2_blit_boxes(blit_src, win_surface, dst, _s2_box, _s2_n)   // SCALE2-NARROW
                             : TryFastIntegerNearestBlit(blit_src, win_surface, dst);
''')
sw = rep('sw', sw, '''            const long long _db = (long long)dst.w * dst.h * (_wf ? _wf->bytes_per_pixel : 0);
''', '''            long long _db = (long long)dst.w * dst.h * (_wf ? _wf->bytes_per_pixel : 0);
            if (_s2_narrow && blitted)   // SCALE2-NARROW: only the boxes were scale-blitted, 4 window px per source px
            {
                long long _sp = 0;
                for (int _i = 0; _i < _s2_n; ++_i)
                    _sp += (long long)(_s2_box[_i].x2 - _s2_box[_i].x1 + 1) * (_s2_box[_i].y2 - _s2_box[_i].y1 + 1);
                _db = 4 * _sp * (_wf ? _wf->bytes_per_pixel : 0);
            }
''')

# ---- 7. the latch and the verifier, after the blit ----
sw = rep('sw', sw, '''#ifdef __DJGPP__
    // Adopt for the NEXT frame once a frame has presented with steady 1x
''', '''#ifdef __DJGPP__
    if (dos_s2_on())   // SCALE2-NARROW: does the window surface still hold scale2(virtual screen) at this geometry?
    {
        if (palette_only_present)
            dos_s2.pal++;              // nothing written: the latch stands
        else if (_s2_narrow)
        {
            if (!blitted)              // the box blit failed and the generic blit ran in full: trust nothing
                dos_s2_latch_drop();
        }
        else
        {
            if (_s2_cand)
                dos_s2.full++;
            if (_s2_cand && dos_s2_full_done && blitted && blit_src == _vscreenSurface && flip == kFlip_None && dst_inside)
                dos_s2_latch_set(win_surface, blit_src, dst);
            else
                dos_s2_latch_drop();
        }
        if (dos_s2_verify_on && _s2_cand && dos_s2_latch_ok(win_surface, blit_src, dst))
            dos_s2_verify(blit_src, win_surface, dst);
    }
#endif
#ifdef __DJGPP__
    // Adopt for the NEXT frame once a frame has presented with steady 1x
''')

# ---- 8. the 0124 block: no second merge, a narrowed 2x present is not a rejection, push the doubled boxes ----
sw = rep('sw', sw, '''    dos_port_dirty_merge_carry();   // patch 0193: last interval's marks are repainted by THIS frame's restore
''', '''    if (!_s2_merged)   // SCALE2-NARROW: already merged ahead of the unchanged-frame check
    dos_port_dirty_merge_carry();   // patch 0193: last interval's marks are repainted by THIS frame's restore
''')
sw = rep('sw', sw, '''        if (!_dp_one_to_one) dos_port_dirty.rej_scaled++;
''', '''        if (_s2_narrow) { /* SCALE2-NARROW: narrowed below, not a rejection */ }
        else if (!_dp_one_to_one) dos_port_dirty.rej_scaled++;
''')
sw = rep('sw', sw, '''        if (!_dp_narrowed)
        {
            dos_port_dirty.frames_full++;
''', '''        if (_s2_narrow)
        {   // SCALE2-NARROW: push exactly what was scale-blitted, doubled, in WINDOW coordinates
            long long _a = 0;
            for (int _i = 0; _i < _s2_n; ++_i)
            {
                SDL_Rect &_r = _dp_rects[_i];
                _r.x = dst.x + 2 * _s2_box[_i].x1;
                _r.y = dst.y + 2 * _s2_box[_i].y1;
                _r.w = 2 * (_s2_box[_i].x2 - _s2_box[_i].x1 + 1);
                _r.h = 2 * (_s2_box[_i].y2 - _s2_box[_i].y1 + 1);
                _a += (long long)(_r.w / 2) * (_r.h / 2);
            }
            _dp_nrects = _s2_n;
            _dp_push = _dp_rects[0];
            _dp_narrowed = true;
            dos_port_dirty.frames_narrow++;
            dos_port_dirty.px_narrow += _a;   // game px, as at 1x
            dos_s2.narrow++;
            dos_s2.rects += _s2_n;
            dos_s2.px_src += _a;
        }
        if (!_dp_narrowed)
        {
            dos_port_dirty.frames_full++;
''')

# ---- quit.cpp: the exit line (both flavours, beside 0366/0369's) and the RUNMANIFEST allowlist ----
qt = rep('qt', qt, '''                dos_char_reuse_summary(run_manifest_log);
''', '''                dos_char_reuse_summary(run_manifest_log);
                extern void dos_scale2_summary(FILE *);   // SCALE2-NARROW (apply-2x.py): prints only when switched on
                dos_scale2_summary(run_manifest_log);
''')
qt = rep('qt', qt, '''            "DOSAGS_ROUTE_PREWARM",   // patch 0371: route-cache pre-warm in the room-load / restore stall (off by default)
''', '''            "DOSAGS_ROUTE_PREWARM",   // patch 0371: route-cache pre-warm in the room-load / restore stall (off by default)
            "DOSAGS_SCALE2_BREAK",    // SCALE2-NARROW (apply-2x.py): control only -- 1: 1 px short; 2: last box; 3: no box blitted
            "DOSAGS_SCALE2_NARROW",   // SCALE2-NARROW: the narrowed integer-2x present + full 2x replicator (off by default)
            "DOSAGS_SCALE2_VERIFY",   // SCALE2-NARROW: whole-frame scale2 compare per present -- a diagnostic, never timed
''')

assert N == {'sw': 13, 'qt': 2}, N
for name, text in ((P_SW, sw), (P_QT, qt)):
    assert text.isascii(), (name, 'non-ASCII')
open(P_SW, 'w', encoding='ascii', newline='').write(sw)
open(P_QT, 'w', encoding='ascii', newline='').write(qt)
print('SCALE2-NARROW applied: ali3dsw.cpp x%d, quit.cpp x%d' % (N['sw'], N['qt']))
