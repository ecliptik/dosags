#!/usr/bin/env python3
"""ckwin.py CELL_DIR A:B [A:B ...] -- per-window table from LAB-PLAY checkpoints (DOSAGS_LAB_CKPT).
Window (A, B]: cumulative totals at checkpoint B minus those at A. The checkpoint's own print cost (self_us of
checkpoint A, paid inside tick A's input_poll / update_game_once_total / game_tick_outer) is subtracted from
those three. Prints ms per tick (ticks = B - A) and ms per call for render-side phases."""
import re, sys, os
d = sys.argv[1]
t = open(os.path.join(d, 'STDOUT.TXT'), 'rb').read().decode('latin1')
ph, w, c, selfus, evt = {}, {}, {}, {}, {}
for m in re.finditer(r'labck lc=(\d+) ph=(\w+) calls=(\d+) us=(\d+)', t):
    ph.setdefault(int(m.group(1)), {})[m.group(2)] = (int(m.group(3)), int(m.group(4)))
for m in re.finditer(r'labck lc=(\d+) w=(\d+) v=(-?\d+)', t):
    w.setdefault(int(m.group(1)), {})[int(m.group(2))] = int(m.group(3))
for m in re.finditer(r'labck lc=(\d+) c=(\w+) (.*)', t):
    kv = dict(x.split('=') for x in m.group(3).split())
    c.setdefault(int(m.group(1)), {}).update({m.group(2) + '.' + k: int(v) for k, v in kv.items()})
for m in re.finditer(r'labck lc=(\d+) self_us=(\d+)', t):
    selfus[int(m.group(1))] = int(m.group(2))
for m in re.finditer(r'labck lc=(\d+) evt=(\d+) n=(\d+) us=(\d+)', t):
    evt.setdefault(int(m.group(1)), {})[int(m.group(2))] = (int(m.group(3)), int(m.group(4)))
WN = ["ticks", "renders", "presents", "script_ins", "script_ext", "push_bytes", "push_rects", "blit1x_bytes", "blitsc_bytes",
      "cmp_bytes", "cache_bytes", "bg_px", "fill_px", "spr_n", "spr_opq_px", "spr_msk_px", "spr_bld_px", "file_bytes", "file_calls"]
rows = []
for spec in sys.argv[2:]:
    a, b = map(int, spec.split(':'))
    n = b - a
    s = selfus.get(a, 0)
    D = {}
    for k in ph[b]:
        cb, ub = ph[b][k]; ca, ua = ph[a].get(k, (0, 0))
        us = ub - ua
        if k in ('update_game_once_total', 'game_tick_outer', 'input_poll'):
            us -= s
        D[k] = (cb - ca, us)
    WV = {WN[i]: w[b][i] - w[a][i] for i in w[b]}
    CV = {k: c[b][k] - c[a].get(k, 0) for k in c[b]}
    EV = {i: (evt[b][i][0] - evt[a][i][0], evt[b][i][1] - evt[a][i][1]) for i in evt[b]}
    rows.append((spec, n, D, WV, CV, EV))
def g(D, k): return D.get(k, (0, 0))
print('window'.ljust(28) + ''.join(r[0].rjust(13) for r in rows))
def line(lbl, f):
    print(lbl.ljust(28) + ''.join(f(r).rjust(13) for r in rows))
line('ticks', lambda r: '%d' % r[1])
line('render passes', lambda r: '%d' % g(r[2], 'render_to_screen')[0])
line('renders/ticks %', lambda r: '%.1f' % (100.0 * g(r[2], 'render_to_screen')[0] / r[1]))
pt = lambda k: (lambda r: '%.3f' % (g(r[2], k)[1] / 1000.0 / r[1]))
pc = lambda k: (lambda r: '%.3f' % (g(r[2], k)[1] / 1000.0 / max(1, g(r[2], k)[0])))
print('-- ms per tick')
for k in ('update_game_once_total', 'wait_next_frame', 'script_vm', 'process_events_dispatch', 'game_objects_update',
          'drawable_object_states', 'objects_scale', 'input_handling', 'input_poll', 'gui_context_cursor', 'rep_exec_wrapper',
          'scene_construct', 'render_to_screen'):
    line(k, pt(k))
def logic_other(r):
    D = r[2]; n = r[1]
    u = g(D, 'update_game_once_total')[1] - g(D, 'wait_next_frame')[1] - g(D, 'render_to_screen')[1] - g(D, 'scene_construct')[1]
    return u / 1000.0 / n
line('logic (ugo-wait-render-scene)', lambda r: '%.3f' % logic_other(r))
line('  of which dispatch', pt('process_events_dispatch'))
line('  other logic', lambda r: '%.3f' % (logic_other(r) - g(r[2], 'process_events_dispatch')[1] / 1000.0 / r[1]))
line('busy (ugo-wait)', lambda r: '%.3f' % ((g(r[2], 'update_game_once_total')[1] - g(r[2], 'wait_next_frame')[1]) / 1000.0 / r[1]))
print('-- ms per render pass')
for k in ('scene_construct', 'sc_room_view', 'sc_viewports', 'bg_restore', 'sc_prep_chars', 'sc_prep_objects', 'sc_ui_view', 'sc_preroom',
          'render_to_screen', 'render_backbuffer', 'rb_sprite_time', 'present_update_window', 'present_blit', 'present_dirty_check'):
    line(k, lambda r, k=k: '%.3f' % (g(r[2], k)[1] / 1000.0 / max(1, g(r[2], 'render_to_screen')[0])))
line('pass = scene + render', lambda r: '%.3f' % ((g(r[2], 'scene_construct')[1] + g(r[2], 'render_to_screen')[1]) / 1000.0 / max(1, g(r[2], 'render_to_screen')[0])))
print('-- work per render pass')
for k in ('push_bytes', 'push_rects', 'bg_px', 'spr_n', 'spr_msk_px', 'spr_opq_px', 'spr_bld_px', 'fill_px', 'blit1x_bytes'):
    line(k, lambda r, k=k: '%.0f' % (r[3].get(k, 0) / max(1, g(r[2], 'render_to_screen')[0])))
line('script_ext / tick', lambda r: '%.1f' % (r[3].get('script_ext', 0) / r[1]))
for k in ('dirty.narrow', 'dirty.full', 'rb.bgwhole', 'lab.camchg', 'lab.vpchg', 'lab.invall', 'lab.invcam'):
    line(k + ' (count)', lambda r, k=k: '%d' % r[4].get(k, 0))
line('evt script ms/tick', lambda r: '%.3f' % (r[5].get(1, (0, 0))[1] / 1000.0 / r[1]))
line('evt object ms/tick', lambda r: '%.3f' % (r[5].get(2, (0, 0))[1] / 1000.0 / r[1]))
print('-- LAB-R3 per render pass')
pp = lambda k: (lambda r: '%.1f' % (r[4].get(k, 0) / max(1, g(r[2], 'render_to_screen')[0])))
for k in ('r3.skipped', 'r3.clipped', 'r3.full', 'r3.multi', 'r3.rects', 'r3.r3_px', 'r3.clip_px', 'r3.full_px', 'r3.guinoskip_n',
          'r3.guiredraw_n', 'r3.fb_bbox', 'r3.fb_whole'):
    line(k, pp(k))
line('gui re-render ms/pass', lambda r: '%.3f' % (r[4].get('r3.guiredraw_us', 0) / 1000.0 / max(1, g(r[2], 'render_to_screen')[0])))
