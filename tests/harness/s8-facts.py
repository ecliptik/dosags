#!/usr/bin/env python3
"""s8-facts.py -- the Gate S8 lab figures of one cell (lab/journeys, 2026-09-23).

    tests/harness/s8-facts.py <cell-dir> [--tickstats]

Prints one "S8 k=v ..." line: the rate fields as the manifest has them (tick_rate,
tick_rate_steady, fps_p50, render_passes, presents_real, frames_skipped, ticks), the
fixed-cycles cost figures the pre-registration ranks on (ms per tick of the main-loop
idle wait, of the audio pump, of render_to_screen), the audio counters (pcm_unaccounted,
overwrites, silent_irqs, midi late writes) and stall share / stalls > 100 ms (ags 0250).
With --tickstats, also every tickstats_* total as ms per game tick, for ranking phases.

The rates are DOSBox-X figures at fixed 40k cycles: a ranking between arms, never a
prediction of the 486.
"""
import os
import re
import sys


def kv(text, key):
    m = re.findall(r'\b%s=(-?[0-9.]+)' % re.escape(key), text)
    return m[-1] if m else None


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if len(args) != 1:
        print(__doc__)
        return 2
    d = args[0]
    try:
        rm = open(os.path.join(d, 'RUNMANI.LOG'), errors='replace').read()
    except OSError:
        print('MISSING RUNMANI.LOG')
        return 1
    ts = {}
    for m in re.finditer(r'DOS-PORT tickstats_(\w+) calls=(\d+) total_ms=(\d+)[^\n]*?total_us=(\d+)', rm):
        ts[m.group(1)] = (int(m.group(2)), int(m.group(4)) / 1000.0)
    ticks = kv(rm, 'ticks')
    f = {}
    for k in ('tick_rate', 'tick_rate_steady', 'fps_p50', 'render_passes', 'presents_real', 'frames_skipped'):
        f[k] = kv(rm, k)
    # ticks: the manifest prints two (gate window and whole run); the loop total is update_game_once calls
    nt = ts.get('update_game_once_total', (0, 0))[0]
    f['ticks'] = str(nt) if nt else ticks
    per = lambda name: ('%.2f' % (ts[name][1] / nt)) if nt and name in ts else None
    f['idle_ms_per_tick'] = per('wait_next_frame')
    f['audio_poll_ms_per_tick'] = per('catchup_audio_poll')
    f['render_ms_per_tick'] = per('render_to_screen')
    f['update_ms_per_tick'] = per('update_game_once_total')
    # S8L1 amendment: under saturation the cost of an arm shows as render passes lost; the
    # time per render pass (render_to_screen per call) converts them to ms per tick
    if 'render_to_screen' in ts and ts['render_to_screen'][0]:
        f['ms_per_render_pass'] = '%.2f' % (ts['render_to_screen'][1] / ts['render_to_screen'][0])
    if nt and 'update_game_once_total' in ts and 'render_to_screen' in ts:
        f['nonrender_ms_per_tick'] = '%.2f' % ((ts['update_game_once_total'][1] - ts['render_to_screen'][1]) / nt)
    avs = re.findall(r'audio_vital_status=(\S+)', rm)
    a = avs[-1] if avs else ''
    pcm, midi = (a.split(';', 1) + [''])[:2] if a else ('', '')
    mixed, irqs = kv(pcm, 'mixed'), kv(pcm, 'pcm_irqs')
    f['pcm_irqs'] = irqs
    infl = re.findall(r'\binflight=(-?[0-9]+)', pcm)
    f['pcm_inflight'] = infl[-1] if infl else None
    f['pcm_unaccounted'] = (str(int(mixed) - int(irqs) - (int(infl[-1]) if infl and int(infl[-1]) >= 0 else 0))
                            if mixed and irqs else None)
    f['overwrites'] = kv(pcm, 'overwrites')
    f['silent_irqs'] = kv(pcm, 'silent_irqs')
    f['midi_tick'] = (re.findall(r'midi_tick=(\w+)', midi) or [None])[-1]
    f['midi_events'] = kv(midi, 'events')
    f['midi_late'] = kv(midi, 'late_writes') if 'midi_tick=isr' in midi else kv(midi, 'late50')
    f['midi_late_max_ms'] = kv(midi, 'late_max_ms')
    ss = re.findall(r'DOS-PORT stallshare [^\n]*', rm)
    st = re.findall(r'DOS-PORT stalls100 [^\n]*', rm)
    if ss:
        f['stall_share'] = kv(ss[-1], 'share')
        f['stall_share_nojourney'] = kv(ss[-1], 'share_nojourney')
    if st:
        f['stalls100_per_min'] = kv(st[-1], 'per_min')
        f['stalls100_max_ms'] = kv(st[-1], 'max_ms')
    msl = re.findall(r'DOS-PORT midistream [^\n]*', rm)
    if msl:
        for k in ('basis', 'first_s', 'span_windows', 'zero_windows', 'longest_gap_s', 'trailing_gap_s', 'p5', 'p50'):
            m = re.findall(r'\b%s=(\S+)' % k, msl[-1])
            f['midistream_' + k] = m[-1] if m else None
    print('S8 ' + ' '.join('%s=%s' % (k, v if v is not None else 'NA') for k, v in f.items()))
    if '--tickstats' in sys.argv and nt:
        for name, (calls, ms) in sorted(ts.items(), key=lambda x: -x[1][1]):
            print('  %-36s %9.3f ms/tick  (%d calls)' % (name, ms / nt, calls))
    return 0


if __name__ == '__main__':
    sys.exit(main())
