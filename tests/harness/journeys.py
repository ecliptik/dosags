#!/usr/bin/env python3
"""journeys.py -- read ags patch 0250's journey lines and cross-check them.

    tests/harness/journeys.py <stage-or-results-dir> [--host-clicks LOG]

Reads RUNMANI.LOG (journey / journey_summary / journey_input / stallshare /
stalls100 lines) and STDOUT.TXT, prints one table, then a second witness for
each figure that has one elsewhere in the log:

  room start   == the "DOS-PORT room_transition ... event=start" t_ms of the
                  same room (patch 0042, same uclock anchor): a mismatch means
                  the journey started somewhere else (NewRoom() earlier than
                  new_room(), which is allowed, shows as journey <= start line)
  stall share  recomputed from the persec rows (patch 0093/0094): each row
                  interval's render passes per second, time-weighted. Not the
                  same windows (persec rows are ~1.0-1.2 s apart and skip
                  blocking stalls), so it is a consistency check, not equality
  clicks       --host-clicks: the drive-clicks-dosbox.sh log; host presses
                  injected vs mouse_presses_hw (driver) vs mouse_presses_seen
                  vs journey kind=click n

Last, "RATCHET key=value" lines for tests/ratchet.yaml to read. A figure that
would be vacuous is printed as NA, never as 0, so a ratchet check on it reads
no number and ERRORs: lost_clicks is NA when the mouse driver's counters were
never read (hw_checks=0, e.g. no mouse); lost_inputs is only printed with
--host-clicks, and is the END-TO-END count

    lost_inputs = (host clicks - clicks the engine received)
                + (host keys   - keys the engine received)

where "received" = journeys + unfinished + cleared of that kind (the engine
had the event; what it did with it is the journey's business). It catches a
loss anywhere between the host and the engine's queue, which the driver-vs-
poll lost_clicks alone cannot (a key the pump drained but never mapped, a
driver that missed the press). host_clicks / host_keys are printed too: a
check must also pin them, or a driver script that injected nothing would
read lost_inputs=0. Exit 1 if RUNMANI.LOG has no journey_basis line (the
binary does not carry patch 0250).
"""
import os
import re
import sys


def kv(line):
    return dict(re.findall(r'(\w+)=([^\s,]+)', line))


def main():
    args = sys.argv[1:]
    host = None
    if '--host-clicks' in args:
        i = args.index('--host-clicks')
        host = args[i + 1]
        del args[i:i + 2]
    if len(args) != 1:
        print(__doc__)
        return 2
    d = args[0]
    rm = open(os.path.join(d, 'RUNMANI.LOG'), errors='replace').read().splitlines()
    so_path = os.path.join(d, 'STDOUT.TXT')
    so = open(so_path, errors='replace').read().splitlines() if os.path.exists(so_path) else []
    if not any(l.startswith('DOS-PORT journey_basis') for l in rm):
        print('MISSING journey_basis: binary without ags patch 0250')
        return 1
    out = []
    recs = [kv(l) for l in rm if l.startswith('DOS-PORT journey ')]
    summ = {kv(l)['kind']: kv(l) for l in rm if l.startswith('DOS-PORT journey_summary')}
    inp = next((kv(l) for l in rm if l.startswith('DOS-PORT journey_input')), {})
    ss = next((kv(l) for l in rm if l.startswith('DOS-PORT stallshare')), {})
    st = next((kv(l) for l in rm if l.startswith('DOS-PORT stalls100')), {})

    print('%-18s %5s %7s %7s %7s %9s  %s' % ('kind', 'n', 'p50', 'p95', 'max', 'p95_upper',
                                             'failed/unfinished/superseded/rerequested/cleared'))
    for k, s in summ.items():
        print('%-18s %5s %7s %7s %7s %9s  %s/%s/%s/%s/%s' % (
            k, s['n'], s['p50_ms'], s['p95_ms'], s['max_ms'], s.get('p95_upper_ms', '-'),
            s.get('failed', '-'), s['unfinished'], s['superseded'], s.get('rerequested', '-'), s['cleared']))
    print()
    for r in recs:
        if r.get('kind') in ('boot', 'room', 'save', 'save_restartpoint', 'load'):  # inputs: too many
            print('  ' + ' '.join('%s=%s' % (a, b) for a, b in r.items()))
    print()

    # second witness 1: room start vs the patch 0042 start line
    starts = {}
    for l in so:
        m = re.search(r'DOS-PORT room_transition t_ms=(\d+) event=start room=(\d+)', l)
        if m:
            starts.setdefault(int(m.group(2)), []).append(int(m.group(1)))
    for r in recs:
        if r.get('kind') != 'room':
            continue
        to = int(r['to'])
        cand = starts.get(to, [])
        t = int(r['t_ms'])
        near = min(cand, key=lambda x: abs(x - t)) if cand else None
        print('room %s->%s journey t_ms=%d  0042 start t_ms=%s  diff=%s ms' % (
            r['from'], to, t, near, (near - t) if near is not None else 'MISSING'))

    # second witness 2: persec-based stall share
    rows = [kv(l) for l in rm if l.startswith('DOS-PORT persec ')]
    tot = below = 0.0
    for a, b in zip(rows, rows[1:]):
        dt = (int(b['ms']) - int(a['ms'])) / 1000.0
        if dt <= 0:
            continue
        rate = (int(b['renders']) - int(a['renders'])) / dt
        tot += dt
        if rate < int(ss.get('floor', 39)):
            below += dt
    if ss:
        print('stallshare engine: %s of %s windows below %s (share %s; nojourney %s)' % (
            ss['below'], ss['windows'], ss['floor'], ss['share'], ss['share_nojourney']))
    if tot:
        print('stallshare persec witness (render passes, time-weighted): %.4f over %.0f s' % (below / tot, tot))
    if st:
        print('stalls>100ms: n=%s per_min=%s max_ms=%s nojourney n=%s per_min=%s tail_ms=%s' % (
            st['n'], st['per_min'], st['max_ms'], st['n_nojourney'], st['per_min_nojourney'], st.get('tail_ms')))

    # clicks: three counts
    if inp:
        print('input: driver presses=%s seen=%s lost=%s; kbd irq=%s drained=%s' % (
            inp['mouse_presses_hw'], inp['mouse_presses_seen'], inp['lost_clicks'],
            inp['kbd_bytes_irq'], inp['kbd_bytes_drained']))
    def received(kind):
        s = summ.get(kind, {})
        return sum(int(s.get(f, 0)) for f in ('n', 'unfinished', 'cleared')) + int(s.get('failed', 0))

    if host:
        hl = open(host).read().splitlines()
        injected = sum(1 for l in hl if ' press ' in l)
        keys = sum(1 for l in hl if ' key i=' in l)
        aborted = any(' ABORT ' in l for l in hl)
        rc_click, rc_key = received('click'), received('key')
        lost = (injected - rc_click) + (keys - rc_key)
        print('clicks: host injected=%d driver=%s seen=%s engine received=%d; keys injected=%d engine received=%d'
              '; lost_inputs=%d%s' % (injected, inp.get('mouse_presses_hw'), inp.get('mouse_presses_seen'),
                                      rc_click, keys, rc_key, lost, ' (driver ABORTED)' if aborted else ''))
        out.append('host_clicks=%d host_keys=%d' % (injected, keys))
        # 2026-11-04 (ags 0354): a host driver that saw the room line LATE injects late, and its tail
        # then runs past the auto-exit tick: lost inputs that are a harness fault, not the engine's.
        # The engine's own room load_end (DOSAGS_XT) to its first received click read 16.5-17.6 s on every
        # instrumented run before 0354 and 8.7-9.6 s on both flavours with it (ratchets 20261105T000223Z,
        # 20261105T005648Z); the stdout-buffering fault read 36-109 s.
        # Past LATE_START_MS the cell is VOID: lost_inputs is withheld, so the check reads no number.
        LATE_START_MS = 30000
        room_end = [int(m.group(1)) for l in so for m in [re.search(r'DOSAGS_XT t_ms=(\d+) phase=load_end room=', l)] if m]
        first_click = [int(m.group(1)) for l in rm for m in [re.search(r'^DOS-PORT journey kind=click room=-?\d+ t_ms=(\d+)', l)] if m]
        late = None
        if room_end and first_click:
            gap = first_click[0] - room_end[-1] if first_click[0] >= room_end[-1] else first_click[0] - room_end[0]
            out.append('click_start_ms=%d' % gap)
            if gap > LATE_START_MS:
                late = gap
                print('VOID: first click %d ms after the room load_end (bound %d): the host started late, '
                      'so lost_inputs is not scored' % (gap, LATE_START_MS))
        if not aborted and late is None:
            out.append('lost_inputs=%d' % lost)
        try:
            out.append('driver_short=%d' % (injected - int(inp['mouse_presses_hw'])))
        except (KeyError, ValueError):
            pass

    # ratchet fields
    for k, s in summ.items():
        out.append('%s_n=%s %s_p95_ms=%s %s_p95_upper_ms=%s %s_failed=%s %s_unfinished=%s' % (
            k, s['n'], k, s['p95_ms'], k, s.get('p95_upper_ms', 'NA'), k, s.get('failed', 'NA'),
            k, s['unfinished']))
    out.append('journeys_unfinished=%d journeys_failed=%d' % (
        sum(int(s['unfinished']) for s in summ.values()),
        sum(int(s.get('failed', 0)) for s in summ.values())))
    if inp:
        lc = inp['lost_clicks'] if int(inp.get('hw_checks', 0)) > 0 else 'NA'
        out.append('lost_clicks=%s hw_checks=%s kbd_undrained=%s' % (lc, inp.get('hw_checks'),
                                                                     inp['kbd_bytes_undrained']))
    print()
    for o in out:
        print('RATCHET ' + o)
    return 0


if __name__ == '__main__':
    sys.exit(main())
