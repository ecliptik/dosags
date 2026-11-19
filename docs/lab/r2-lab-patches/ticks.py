#!/usr/bin/env python3
"""LAB-R2 TICKS.BIN reader (ags 0316 format + LAB-R2 lab kinds), grouped by TICK, not by loop counter.

Record order inside one tick N: [click/key/room events], scene (3), render (2) and the lab kinds, wait (7), then the
update_game_once close (1), which is stamped with lc N+1 because the loop counter advances before that close. So a tick
is "every record up to and including the next kind-1 record", and its id is that kind-1 record's lc minus 1.
(f1prof.py groups by lc instead, which pairs tick N-1's ugo with tick N's render/scene.)
Kinds: 1 ugo, 2 render, 3 scene, 4 room, 5 click, 6 key; lab: 7 wait, 8 sc_prep_chars, 9 char blit us, 10 bg_restore,
11 restore px, 12 restore px in character rects, 13 rb_sprite_time us, 14 char blit px.  Values are us unless px.
"""
import struct

NAMES = {1: 'ugo', 2: 'render', 3: 'scene', 7: 'wait', 8: 'prep', 9: 'cblit', 10: 'bg', 11: 'bgall', 12: 'bgchar',
         13: 'rbspr', 14: 'cpx'}


def load(path):
    b = open(path, 'rb').read()
    magic, ver, n, dropped, cap = struct.unpack('<5I', b[:20])
    assert magic == 0x474F4C54 and ver == 1, 'not a TICKS.BIN v1'
    r = struct.unpack('<%dI' % (2 * n), b[20:20 + 8 * n])
    recs = [(r[2 * i], r[2 * i + 1] >> 28, r[2 * i + 1] & 0x0FFFFFFF) for i in range(n)]
    ticks, cur, rooms, bad = [], {}, [], []
    for lc, k, v in recs:
        if k == 1:
            t = {'lc': lc - 1, 'ugo': v}
            for kk, vv in cur.items():
                t[kk] = vv
            t['drawn'] = 'render' in cur
            ticks.append(t)
            cur = {}
        elif k == 4:
            rooms.append((lc, v)); cur['room'] = v
        elif k == 5:
            cur['click'] = cur.get('click', 0) + 1
        elif k == 6:
            cur['key'] = cur.get('key', 0) + 1
        else:
            nm = NAMES.get(k, 'k%d' % k)
            if v >= 0x0FFFFFFF:   # a negative elapsed (uclock step back) cast and clamped: count as 0, note it
                bad.append((lc, nm)); v = 0
            cur[nm] = cur.get(nm, 0) + v
    return {'ticks': ticks, 'rooms': rooms, 'dropped': dropped, 'cap': cap, 'nrec': n, 'bad': bad}


def med(xs):
    xs = sorted(xs)
    if not xs:
        return float('nan')
    m = len(xs) // 2
    return xs[m] if len(xs) % 2 else 0.5 * (xs[m - 1] + xs[m])


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))] if xs else float('nan')
