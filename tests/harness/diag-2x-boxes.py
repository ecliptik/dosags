#!/usr/bin/env python3
"""diag-2x-boxes.py VENDOR_AGS -- LAB DIAGNOSTIC ONLY, applied on top of tests/harness/apply-2x.py (run that first).
Why does DOSAGS_SCALE2_BREAK=2 (the last narrowed box not blitted) leave nothing stale on the B16-2x-walk row (gate2:
V2 vfy=1040 vfy_bad=0)? Information for FIX-UP 3, not a rescue; never in a gate exe, never in a release.

Gating: active only when DOSAGS_SCALE2_VERIFY=1 (with DOSAGS_SCALE2_NARROW=1; the verifier is already a DOSBox-X-only
diagnostic, and gate-2x.sh's V / V2 arms set it, so the registered driver runs this unchanged). Off by default; with
VERIFY unset the only cost is one bool test per narrowed present and per summary.

On every narrowed 2x present, BEFORE the boxes are blitted (window = what the screen shows, src = the new frame):
  per box i: area; chg[i] = source px whose four window px differ from scale2(src) (pixels that CHANGED and need the
  blit); cov[i] = px also inside another box of this present; unc[i] = changed px inside no other box (what skipping
  box i alone would leave stale); ovl[i] = box i intersects another box;
  tag: from a snapshot of dos_port_dirty taken just before 0193's carry merge (apply-2x.py sec. 5):
    U = slot that existed before the merge, unchanged by it; G = slot that existed and was grown by a carry box;
    N = slot CREATED by the merge (a carry box that touched nothing); b = the bbox fallback (set not used);
  K flag: box intersects a carried (previous interval's post-restore) box.
Exit lines in RUNMANI.LOG after the scale2 line (both flavours):
  "DOS-PORT s2diag sum ..."  aggregates over every narrowed present (counts, the box-count histogram, the last box's
                             tag / containment / change, and what four candidate controls would have left stale)
  "DOS-PORT s2diag p=..."    one line per narrowed present for the first 400 (boxes as x1,y1,x2,y2:tag:area:chg:unc:cov)
"""
import sys

V = sys.argv[1]
P_SW = V + '/Engine/gfx/ali3dsw.cpp'
sw = open(P_SW, encoding='ascii', newline='').read()
assert 'SCALE2-NARROW (apply-2x.py)' in sw, 'apply-2x.py first'
N = [0]


def rep(src, a, b):
    assert src.count(a) == 1, (a[:70], src.count(a))
    N[0] += 1
    return src.replace(a, b, 1)


# 1. the dump at the end of the summary (the diag block itself goes in front of the summary, at global scope)
sw = rep(sw, '''        s.rej_whole, s.latch_sets, s.latch_drops, s.vfy, s.vfy_bad, s.vfy_bad_px, s.vfy_first);
}''', '''        s.rej_whole, s.latch_sets, s.latch_drops, s.vfy, s.vfy_bad, s.vfy_bad_px, s.vfy_first);
    dos_s2d_dump(log);   // S2DIAG
}''')

# 2. the diagnostic itself, at GLOBAL scope in front of the summary (the box blit, in the driver's namespace, calls it)
sw = rep(sw, '''void dos_scale2_summary(FILE *log)
{''', '''// ---- S2DIAG (diag-2x-boxes.py; LAB DIAGNOSTIC, active only with DOSAGS_SCALE2_VERIFY=1) ----
struct DosS2Diag
{
    int pre_nbox = 0; bool pre_valid = false, pre_full = false;
    DosPortDirtyBox pre_box[DOS_PORT_DIRTY_MAX_BOXES];
    int carry_n = 0; bool carry_full = false;
    DosPortDirtyBox carry[DOS_PORT_DIRTY_MAX_BOXES];
    long p = 0, hist[DOS_PORT_DIRTY_MAX_BOXES + 1] = {}, carry_presents = 0;
    long last_tag[4] = {0, 0, 0, 0};   // U G N b
    long last_k = 0, last_chg = 0, last_unc = 0, last_contained = 0, last_ovl = 0, last_n1 = 0;
    long h_last = 0, h_big = 0, h_iso = 0, h_iso_none = 0, h_all = 0, h_maxunc = 0;
    long long tot_chg = 0, last_chg_px = 0, last_unc_px = 0, last_area = 0;
    char buf[200000]; int used = 0, lines = 0;
};
static DosS2Diag dos_s2d;
static inline bool dos_s2d_on() { return dos_s2_on() && dos_s2_verify_on; }
static void dos_s2d_pre()   // just before 0193's carry merge on a 2x candidate present
{
    if (!dos_s2d_on()) return;
    DosS2Diag &g = dos_s2d;
    g.pre_nbox = dos_port_dirty.nbox; g.pre_valid = dos_port_dirty.valid; g.pre_full = dos_port_dirty.is_full;
    for (int i = 0; i < g.pre_nbox; ++i) g.pre_box[i] = dos_port_dirty.box[i];
    g.carry_n = dos_port_dirty.carry_nbox; g.carry_full = dos_port_dirty.carry_full;
    for (int i = 0; i < g.carry_n; ++i) g.carry[i] = dos_port_dirty.carry_box[i];
}
static inline bool dos_s2d_in(const DosPortDirtyBox &b, int x, int y)
{
    return x >= b.x1 && x <= b.x2 && y >= b.y1 && y <= b.y2;
}
static inline bool dos_s2d_isect(const DosPortDirtyBox &a, const DosPortDirtyBox &b)
{
    return a.x1 <= b.x2 && b.x1 <= a.x2 && a.y1 <= b.y2 && b.y1 <= a.y2;
}
static void dos_s2d_present(SDL_Surface *src, SDL_Surface *win, const SDL_Rect &dst, const DosPortDirtyBox *box, int n)
{
    if (!dos_s2d_on() || n <= 0) return;
    DosS2Diag &g = dos_s2d;
    const int bpp = SDL_BYTESPERPIXEL(src->format);
    const Uint8 *base = (const Uint8 *)win->pixels + (size_t)dst.y * (size_t)win->pitch + (size_t)dst.x * (size_t)bpp;
    long area[DOS_PORT_DIRTY_MAX_BOXES], chg[DOS_PORT_DIRTY_MAX_BOXES], unc[DOS_PORT_DIRTY_MAX_BOXES];
    long cov[DOS_PORT_DIRTY_MAX_BOXES];
    bool ovl[DOS_PORT_DIRTY_MAX_BOXES], kf[DOS_PORT_DIRTY_MAX_BOXES];
    char tag[DOS_PORT_DIRTY_MAX_BOXES];
    // tags: map the clamped boxes back to dos_port_dirty.box (as dos_s2_boxes builds them)
    int map[DOS_PORT_DIRTY_MAX_BOXES], m = 0;
    for (int k = 0; k < dos_port_dirty.nbox; ++k)
    {
        const DosPortDirtyBox &b = dos_port_dirty.box[k];   // dos_s2_boxes drops exactly the wholly off-screen ones
        if (b.x2 < 0 || b.y2 < 0 || b.x1 > src->w - 1 || b.y1 > src->h - 1 || b.x2 < b.x1 || b.y2 < b.y1) continue;
        if (m < n) map[m] = k;
        ++m;
    }
    const bool mapped = (m == n);
    long long tot = 0;
    for (int i = 0; i < n; ++i)
    {
        const DosPortDirtyBox &b = box[i];
        area[i] = (long)(b.x2 - b.x1 + 1) * (b.y2 - b.y1 + 1);
        chg[i] = unc[i] = cov[i] = 0; ovl[i] = false; kf[i] = false;
        for (int j = 0; j < n; ++j) if (j != i && dos_s2d_isect(b, box[j])) ovl[i] = true;
        for (int c = 0; c < g.carry_n; ++c) if (dos_s2d_isect(b, g.carry[c])) kf[i] = true;
        if (!mapped) tag[i] = 'b';
        else
        {
            const int k = map[i];
            if (k >= g.pre_nbox) tag[i] = 'N';
            else
            {
                const DosPortDirtyBox &q = dos_port_dirty.box[k], &o = g.pre_box[k];
                tag[i] = (q.x1 == o.x1 && q.y1 == o.y1 && q.x2 == o.x2 && q.y2 == o.y2) ? 'U' : 'G';
            }
        }
        for (int y = b.y1; y <= b.y2; ++y)
        {
            const Uint8 *s = (const Uint8 *)src->pixels + (size_t)y * (size_t)src->pitch;
            const Uint8 *d0 = base + (size_t)(2 * y) * (size_t)win->pitch;
            const Uint8 *d1 = d0 + win->pitch;
            for (int x = b.x1; x <= b.x2; ++x)
            {
                bool other = false, earlier = false;
                for (int j = 0; j < n; ++j)
                    if (j != i && dos_s2d_in(box[j], x, y)) { other = true; if (j < i) earlier = true; }
                if (other) cov[i]++;
                const Uint8 *p = s + (size_t)x * (size_t)bpp;
                const size_t o = (size_t)(2 * x) * (size_t)bpp;
                const bool c = std::memcmp(p, d0 + o, bpp) != 0 || std::memcmp(p, d0 + o + bpp, bpp) != 0 ||
                    std::memcmp(p, d1 + o, bpp) != 0 || std::memcmp(p, d1 + o + bpp, bpp) != 0;
                if (c) { chg[i]++; if (!other) unc[i]++; if (!earlier) tot++; }
            }
        }
    }
    g.p++;
    g.hist[n]++;
    if (g.carry_n > 0) g.carry_presents++;
    g.tot_chg += tot;
    const int L = n - 1;
    g.last_tag[tag[L] == 'U' ? 0 : tag[L] == 'G' ? 1 : tag[L] == 'N' ? 2 : 3]++;
    if (n == 1) g.last_n1++;
    if (kf[L]) g.last_k++;
    if (chg[L] > 0) g.last_chg++;
    if (unc[L] > 0) g.last_unc++;
    if (cov[L] == area[L]) g.last_contained++;
    if (ovl[L]) g.last_ovl++;
    g.last_chg_px += chg[L]; g.last_unc_px += unc[L]; g.last_area += area[L];
    int big = 0, iso = -1, mu = 0;
    for (int i = 0; i < n; ++i)
    {
        if (area[i] > area[big]) big = i;
        if (iso < 0 && !ovl[i]) iso = i;
        if (unc[i] > unc[mu]) mu = i;
    }
    if (unc[L] > 0) g.h_last++;
    if (unc[big] > 0) g.h_big++;
    if (iso < 0) g.h_iso_none++; else if (chg[iso] > 0) g.h_iso++;
    if (tot > 0) g.h_all++;
    if (unc[mu] > 0) g.h_maxunc++;
    if (g.lines < 400 && g.used < (int)sizeof(g.buf) - 1200)
    {
        g.lines++;
        g.used += snprintf(g.buf + g.used, sizeof(g.buf) - g.used,
            "DOS-PORT s2diag p=%ld n=%d pre=%d%s carry=%d%s tot_chg=%lld |", g.p, n, g.pre_nbox,
            g.pre_valid ? "" : "(inv)", g.carry_n, g.carry_full ? "(full)" : "", tot);
        for (int i = 0; i < n && g.used < (int)sizeof(g.buf) - 100; ++i)
            g.used += snprintf(g.buf + g.used, sizeof(g.buf) - g.used, " %d,%d,%d,%d:%c%s:%ld:%ld:%ld:%ld",
                box[i].x1, box[i].y1, box[i].x2, box[i].y2, tag[i], kf[i] ? "K" : "", area[i], chg[i], unc[i], cov[i]);
        g.used += snprintf(g.buf + g.used, sizeof(g.buf) - g.used, "\\n");
    }
}
static void dos_s2d_dump(FILE *log)
{
    if (!log || !dos_s2d_on()) return;
    const DosS2Diag &g = dos_s2d;
    fprintf(log, "DOS-PORT s2diag sum presents=%ld carry_presents=%ld tot_chg_px=%lld last: tag U=%ld G=%ld N=%ld b=%ld"
        " carryhit=%ld n1=%ld chg>0=%ld unc>0=%ld contained=%ld overlaps=%ld area=%lld chg_px=%lld unc_px=%lld"
        " | would leave stale (presents): last=%ld largest=%ld isolated=%ld (no isolated box %ld) all=%ld maxunc=%ld | hist",
        g.p, g.carry_presents, g.tot_chg, g.last_tag[0], g.last_tag[1], g.last_tag[2], g.last_tag[3], g.last_k, g.last_n1,
        g.last_chg, g.last_unc, g.last_contained, g.last_ovl, g.last_area, g.last_chg_px, g.last_unc_px,
        g.h_last, g.h_big, g.h_iso, g.h_iso_none, g.h_all, g.h_maxunc);
    for (int i = 1; i <= DOS_PORT_DIRTY_MAX_BOXES; ++i)
        if (g.hist[i]) fprintf(log, " %d:%ld", i, g.hist[i]);
    fprintf(log, "\\n");
    fwrite(g.buf, 1, g.used, log);
}
void dos_scale2_summary(FILE *log)
{''')

# 3. call it after the locks, before the timed blit
sw = rep(sw, '''    const uclock_t _ts = dos_port_fine_uclock();
    Uint8 *dp = (Uint8 *)win->pixels + (size_t)dst.y * (size_t)win->pitch + (size_t)dst.x * (size_t)bpp;
    for (int i = 0; i < n; ++i)''', '''    dos_s2d_present(src, win, dst, box, n);   // S2DIAG: before anything is blitted
    const uclock_t _ts = dos_port_fine_uclock();
    Uint8 *dp = (Uint8 *)win->pixels + (size_t)dst.y * (size_t)win->pitch + (size_t)dst.x * (size_t)bpp;
    for (int i = 0; i < n; ++i)''')

# 4. the snapshot just before the carry merge
sw = rep(sw, '''            dos_port_dirty_merge_carry();   // patch 0193's merge, moved ahead of the check on 2x presents
''', '''            dos_s2d_pre();   // S2DIAG: the set before the carry merge
            dos_port_dirty_merge_carry();   // patch 0193's merge, moved ahead of the check on 2x presents
''')

assert N[0] == 4, N
assert sw.isascii()
open(P_SW, 'w', encoding='ascii', newline='').write(sw)
print('S2DIAG applied: ali3dsw.cpp x%d' % N[0])
