#!/usr/bin/env python3
"""LAB-R2: per-character table between two DOSAGS_LAB_CKPT checkpoints (labck c=r2char lines), or the whole run
(RUNMANI.LOG r2char lines) when no window is given.   r2char.py CELL_DIR [--ck LO HI]"""
import os, re, sys

F = ('frames path xform tinted crop key_same pos_same pic_same wbchg notified hashed img_same ks_img_diff kd_img_same '
     'us_con us_prep us_blit px_blit n_blit px_img').split()


def parse(line):
    d = {}
    for m in re.finditer(r'(\w+)=(\S+)', line):
        d[m.group(1)] = m.group(2)
    return d


def num(d):
    o = {}
    for k in F:
        v = d.get(k, '0')
        o[k] = [int(x) for x in v.split('/')] if '/' in v else int(v)
    o['name'] = d.get('name'); o['sz'] = d.get('sz'); o['sp'] = d.get('sp')
    return o


def main():
    a = sys.argv[1:]; d = a[0]
    txt = open(os.path.join(d, 'STDOUT.TXT'), 'rb').read().decode('latin1')
    rows = {}
    if '--ck' in a:
        lo, hi = int(a[a.index('--ck') + 1]), int(a[a.index('--ck') + 2])
        at = {}
        for line in txt.splitlines():
            if 'labck c=r2char' in line:
                p = parse(line); at.setdefault(int(p['lc']), {})[int(p['ch'])] = num(p)
        A, B = at.get(lo, {}), at.get(hi, {})
        for ch, b in B.items():
            x = A.get(ch)
            r = {}
            for k in F:
                if isinstance(b[k], list):
                    r[k] = [bb - (x[k][i] if x else 0) for i, bb in enumerate(b[k])]
                else:
                    r[k] = b[k] - (x[k] if x else 0)
            r['name'], r['sz'], r['sp'] = b['name'], b['sz'], b['sp']
            rows[ch] = r
        bgA = [parse(l) for l in txt.splitlines() if 'labck c=r2bg' in l]
        bg = {int(p['lc']): p for p in bgA}
        if lo in bg and hi in bg:
            g = lambda k: int(bg[hi][k]) - int(bg[lo][k])
            print('restore split (detail mode only): restores %d, px all %d, px in character rects %d (%.1f%%)' % (
                g('restores'), g('bgpx_all'), g('bgpx_char'), 100.0 * g('bgpx_char') / max(1, g('bgpx_all'))))
        print('window lc %d..%d' % (lo, hi))
    else:
        rm = open(os.path.join(d, 'RUNMANI.LOG'), 'rb').read().decode('latin1')
        for line in rm.splitlines():
            if line.startswith('DOS-PORT r2char'):
                p = parse(line); rows[int(p['ch'])] = num(p)
    print('%-4s %-10s %6s %-22s %5s %6s %8s %8s %8s %8s %8s %9s %9s %9s %10s %s' % (
        'ch', 'name', 'frames', 'path h/c/r/d', 'xform', 'tint', 'crop', 'key=', 'pos=', 'img=/hash', 'ks!img', 'con us/f',
        'prep us/f', 'blit us/f', 'blit px/f', 'sz sp'))
    for ch in sorted(rows):
        r = rows[ch]; f = max(1, r['frames'])
        print('%-4d %-10s %6d %-22s %5d %6d %4d/%-4d %8d %8d %4d/%-4d %8d %9.1f %9.1f %9.1f %10.0f %s %s' % (
            ch, r['name'], r['frames'], '/'.join(map(str, r['path'][1:])), r['xform'], r['tinted'], r['crop'][0] if isinstance(r['crop'], list) else 0,
            r['crop'][1] if isinstance(r['crop'], list) else 0, r['key_same'], r['pos_same'], r['img_same'], r['hashed'], r['ks_img_diff'],
            r['us_con'] / f, r['us_prep'] / f, r['us_blit'] / max(1, r['n_blit']), r['px_blit'] / max(1, r['n_blit']), r['sz'], r['sp']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
