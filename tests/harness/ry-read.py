#!/usr/bin/env python3
"""ry-read.py -- round RY's readings (ROUNDRY-2026-11-20 README): the narrowed 2x present on the 486 at 640x480.
Read-only. Written and simulated before any data (sdlports' review of the RY draft, 2026-11-20).

  ry-read.py --kern KFILE cell DIR LABEL            one cell
  ry-read.py --kern KFILE pair LABEL DIR_1 DIR_2    a depth's registered pair: MET x2 / MET x1 / NOT MET
  ry-read.py --kern TEE warmup DIR                 the driver's stop rule after WARMUPRY: exit 0 clean, 1 STOP
  --window exit|lock   exit (REGISTERED, owner decision 01M7XQPAWZF30XMWY4JRPPJNDH: the lock line .. the game's exit + 10 s;
                       no exit anchor = VOID) or lock (8649192c's input-lock window, kept as information)

LABEL: B16, B32, B8 (the 2x cells) or A16 (the 1x information anchor). KFILE: the round's kernel slice (vcctrl's
`journalctl -k --utc -o short-iso-precise`, one or more "### WINDOW <from> UTC .. <to> UTC" header lines).

A cell's state is one of:
  VOID      the measurement is not valid: gatebar.py voids it (stamp f42436aadd7b, exit_code, room, a missing field,
            msgskip; build_dirty other than 1), or a witness below fails;
  PATH-OFF  the measurement is valid but the design did not engage: a B cell's scale2 line reads
            narrow / (narrow + full) < 95%. It counts as not MET (sdlports' review item 2);
  MET / NOT MET   gatebar.py's bar, unchanged (both tick figures 39.2-40.8, fps_p50 >= 40, completeness >= 95%,
            audio counters), at the 640x480 2x rung (owner 2026-11-20: "Same bar, new rung").

Witnesses (VOID if any fails):
- exe: PRE-STAGE-SHA256.txt and POST-RUN-SHA256.txt both read S2NR's sha256 (9599809419c8...). build_dirty=1 is
  accepted only then (gatebar's allow_dirty), never otherwise;
- STDOUT: RV's six default lines; BLASTER.TXT "A220 I7 D3 P330 T3";
- B cells:
  - the scale2 line in <TAG>.LOG with on=1 break=0 verify=0;
  - STDOUT render dest (0, 0, 639, 479 : 640 x 480);
  - B32 also "DOS-PORT pack24 engaged mode=0x0112 640x480";
- A16: no scale2 line; render dest (96, 72, 415, 311 : 320 x 240) (RV16A's);
- the stick (B cells; decision 01M7X8X4). Play window (registered, --window exit; decision 01M7XQPAWZF30XMWY4JRPPJNDH): from DRIVE-WALK.LOG's "lock is
  run-hw-<TAG>'s" line (UTC) to the game's exit + 10 s. The exit anchor is run-hw.out's text-mode wait trace: the first
  "changing" right after "blind" past t+60 s, taken as lock + t (the trace starts ~3 s after the lock, so the end is at
  least 7 s past the real exit). No anchor: VOID. The end is also capped at the input-lock window's end (drive-walk's
  "lock no longer" line, or the last run-hw.out job's started_at + 5 s when drive-walk hit its click cap). A drop inside
  the window VOIDs the cell:
  - witness/card-state.log: a sample with state unavailable / starting / nosignal, or last_frame_age_s > 2.5. The file's
    times are the VM's local time (America/Los_Angeles), converted to UTC. "frozen" is not a drop: vcctrld calls a
    picture frozen when bytes still arrive but the last 8 frames are identical (a repeating source); the age rule
    catches a real stall in any state;
  - KFILE: a kernel line on the stick's port (a port named by "New USB device found, idVendor=0001, idProduct=ff02" or
    by a "### STICK-PORT <port>" line), of the kinds "USB disconnect", "Cannot enable", "unable to enumerate",
    "device descriptor read". The hub-port form usbB-portP maps to B-P;
  - missing or unreadable DRIVE-WALK.LOG, card-state.log or KFILE, a KFILE with no WINDOW covering the play window, or a
    drop-kind line on a port that no line ties to the stick or to another device: VOID ("no file" or "no lines" never
    reads as "no drop").
Beside each verdict (information): REGRESSION (displayed < 99.0% or an audio counter non-zero), start-up ms, and the
scale2 counters. Every MET is "subject to the capture sheet CLEAN" (RY32B: no stale or garbage rectangles at the walker
or the cursor, sdlports' item 4).
"""
import argparse
import contextlib
import datetime
import importlib.util
import io
import os
import re
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
_s = importlib.util.spec_from_file_location('gatebar', os.path.join(HERE, 'gatebar.py'))
gb = importlib.util.module_from_spec(_s)
_s.loader.exec_module(gb)
_r = importlib.util.spec_from_file_location('rvread', os.path.join(HERE, 'rv-read.py'))
rv = importlib.util.module_from_spec(_r)
_r.loader.exec_module(rv)

STAMP = 'f42436aadd7b'
SHA = '9599809419c821e0aed4a1740e82f311a07cbea663a4580e7544f892be539043'
ROOM = {'B16': 3, 'B32': 3, 'B8': 35, 'A16': 3}
DEST2X = 'render dest (0, 0, 639, 479 : 640 x 480)'
DEST1X = 'render dest (96, 72, 415, 311 : 320 x 240)'
PACK24 = 'DOS-PORT pack24 engaged mode=0x0112 640x480'
S2 = re.compile(r'^DOS-PORT scale2 on=(\d+) break=(\d+) verify=(\d+) narrow=(\d+) full=(\d+) .*$', re.M)
STICK_ID = 'idVendor=0001, idProduct=ff02'
DROP_KINDS = ('USB disconnect', 'Cannot enable', 'unable to enumerate', 'device descriptor read')
BAD_STATES = ('unavailable', 'starting', 'nosignal')
LA = ZoneInfo('America/Los_Angeles')
UTC = datetime.timezone.utc


def rd(p):
    try:
        return open(p, errors='replace').read()
    except OSError:
        return None


def utc(s):
    return datetime.datetime.fromisoformat(s).astimezone(UTC)


def kern_parse(path):
    """-> (windows [(from, to)], stick_ports set, drops [(t, port, line)], other_ports set) or None if unreadable."""
    txt = rd(path)
    if txt is None:
        return None
    wins, stick, other, drops = [], set(), set(), []
    tee = {'start': None, 'alive': None}
    for ln in txt.splitlines():
        m = re.match(r'^### (TEE-START|ALIVE) (\S+ \S+) UTC', ln)
        if m:
            t = datetime.datetime.fromisoformat(m.group(2)).replace(tzinfo=UTC)
            k = 'start' if m.group(1) == 'TEE-START' else 'alive'
            tee[k] = t if k == 'start' else max(t, tee['alive'] or t)
            continue
        m = re.match(r'^### WINDOW (\S+ \S+) UTC \.\. (\S+ \S+) UTC', ln)
        if m:
            wins.append(tuple(datetime.datetime.fromisoformat(x).replace(tzinfo=UTC) for x in m.groups()))
            continue
        m = re.match(r'^### STICK-PORT (\S+)', ln)
        if m:
            stick.add(m.group(1))
            continue
        m = re.match(r'^(\S+) \S+ kernel: usb (\S+): (.*)$', ln)
        if not m:
            continue
        t, port, rest = utc(m.group(1)), m.group(2), m.group(3)
        h = re.match(r'^usb(\d+)-port(\d+)$', port)
        if h:
            port = '%s-%s' % h.groups()
        if rest.startswith('New USB device found'):
            (stick if STICK_ID in rest else other).add(port)
        if any(k in rest for k in DROP_KINDS):
            drops.append((t, port, ln))
    KTEE[path] = tee
    return wins, stick, drops, other


KTEE = {}


def exit_anchor(d, t0):
    """The game's exit back to text mode, from run-hw.out's text-mode wait trace: the first sample past t+60 s that reads
    "changing" right after "blind" (512x384 is blind all through play; 640x480 goes blind at the mode switch). The trace
    starts after RUN.BAT is typed, a few s after the lock, so t0 + t is at or before the real moment + the trace step."""
    tr = re.findall(r'^\s+t\+\s*([\d.]+)s\s+(\w+)', rd(os.path.join(d, 'run-hw.out')) or '', re.M)
    prev = None
    for t, st in tr:
        if float(t) > 60 and st == 'changing' and prev == 'blind':
            return t0 + datetime.timedelta(seconds=float(t))
        prev = st
    return None


WINDOW = 'exit'   # 'exit': the registered window (owner decision 01M7XQPAWZF30XMWY4JRPPJNDH); 'lock': 8649192c's lock window, information


def stick_check(d, tag, log, kern):
    """-> list of VOID reasons (empty = no drop in the play window), plus an information line."""
    why = []
    dw = rd(os.path.join(d, 'DRIVE-WALK.LOG'))
    cs = rd(os.path.join(d, 'witness', 'card-state.log'))
    su = rd(os.path.join(d, 'START.UTC'))
    if dw is None or cs is None or su is None:
        return ['stick: DRIVE-WALK.LOG / witness/card-state.log / START.UTC missing'], ''
    day = su.strip()[:10]
    m = re.search(r"^(\d\d:\d\d:\d\d\.\d+) lock is run-hw-" + re.escape(tag) + "'s", dw, re.M)
    m1 = re.search(r"^(\d\d:\d\d:\d\d\.\d+) lock no longer run-hw-" + re.escape(tag) + "'s", dw, re.M)
    # The window is the whole input-lock window (sdlports' review item A): it holds the play, whatever the load time,
    # and also the log pull after exit, so it is over-strict but cannot miss the end of play. Its end is drive-walk's
    # lock-release line; drive-walk stops logging at its click cap (RV8 cells: 80 clicks, no release line), so then it
    # is the last run-hw job's started_at (the collect, after the game exits) + 5 s. Measured on RV's 7 cells with both:
    # the release came 0.2-2.6 s after that job's start.
    if not m:
        return ['stick: no play window (DRIVE-WALK.LOG lock-taken line missing)'], ''
    t0 = datetime.datetime.fromisoformat(day + 'T' + m.group(1)).replace(tzinfo=UTC)
    if m1:
        t1 = datetime.datetime.fromisoformat(day + 'T' + m1.group(1)).replace(tzinfo=UTC)
        if t1 < t0:
            t1 += datetime.timedelta(days=1)
        how = 'lock release'
    else:
        sa = [float(x) for x in re.findall(r'"started_at": ([\d.]+)', rd(os.path.join(d, 'run-hw.out')) or '')]
        sa = [x for x in sa if x > t0.timestamp()]
        if not sa:
            return ['stick: no play window end (no lock-release line and no run-hw job after the lock)'], ''
        t1 = datetime.datetime.fromtimestamp(max(sa) + 5, UTC)
        how = 'last run-hw job + 5 s'
    if WINDOW == 'exit':
        ea = exit_anchor(d, t0)
        if ea is None:
            return ['stick: no exit anchor in run-hw.out (window "exit")'], ''
        t1 = min(t1, ea + datetime.timedelta(seconds=10))
        how = 'exit anchor + 10 s'
    # card-state.log: HHMMSS.sss local (VM) time
    cbad, n = [], 0
    for ln in cs.splitlines():
        p = ln.split()
        if len(p) < 4 or not re.match(r'^\d{6}\.\d+$', p[0]):
            continue
        loc = datetime.datetime.strptime(day + p[0][:6], '%Y-%m-%d%H%M%S').replace(tzinfo=LA)
        t = (loc + datetime.timedelta(seconds=float('0.' + p[0].split('.')[1]))).astimezone(UTC)
        if t.date() != t0.date():  # a local-day roll-over: the local date is the UTC day's, shifted
            loc = loc + datetime.timedelta(days=(t0.date() - t.date()).days)
            t = (loc + datetime.timedelta(seconds=float('0.' + p[0].split('.')[1]))).astimezone(UTC)
        if not (t0 <= t <= t1):
            continue
        n += 1
        s = p[1].split('=', 1)[-1]
        age = float(p[3].split('=', 1)[-1])
        if s in BAD_STATES or age > 2.5:
            cbad.append('+%.1f s %s age %.1f' % ((t - t0).total_seconds(), s, age))
    if n == 0:
        why.append('stick: no card-state sample in the play window')
    if cbad:
        why.append('stick drop (card-state): %d sample(s): %s' % (len(cbad), '; '.join(cbad[:4])))
    if kern is None:
        why.append('stick: kernel slice missing or unreadable')
    else:
        wins, stick, drops, other = kern
        if not any(a <= t0 and t1 <= b for a, b in wins):
            why.append('stick: no kernel WINDOW covers the play window %s .. %s' % (t0.strftime('%T'), t1.strftime('%T')))
        kin = [(t, p, l) for t, p, l in drops if t0 <= t <= t1]
        ks = [x for x in kin if x[1] in stick]
        ku = [x for x in kin if x[1] not in stick and x[1] not in other]
        if ks:
            why.append('stick drop (kernel): %d line(s), first +%.1f s on %s' % (
                len(ks), (ks[0][0] - t0).total_seconds(), ks[0][1]))
        if ku:
            why.append('stick: %d drop-kind kernel line(s) on unattributed port(s) %s' % (
                len(ku), ','.join(sorted(set(x[1] for x in ku)))))
    info = '   stick (information): play window %s .. %s UTC (end: %s), %d card-state samples in it' % (
        t0.strftime('%T'), t1.strftime('%T'), how, n)
    return why, info


def cell(d, label, kern):
    """-> (state, lines) with state in MET / NOT MET / PATH-OFF / VOID."""
    tag = os.path.basename(d.rstrip('/')).split('-')[0]
    a = argparse.Namespace(stamp=STAMP, room=ROOM[label], msgskip=(label == 'B8'), allow_dirty=None)
    pre, post = rd(os.path.join(d, 'PRE-STAGE-SHA256.txt')) or '', rd(os.path.join(d, 'POST-RUN-SHA256.txt')) or ''
    sha_ok = pre.split()[:1] == [SHA] and post.split()[:1] == [SHA]
    if sha_ok:
        a.allow_dirty = '1'
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = gb.cell(d, a)
    lines = buf.getvalue().rstrip('\n').splitlines()
    out = rd(os.path.join(d, 'STDOUT.TXT')) or ''
    log = rd(os.path.join(d, tag + '.LOG')) or ''
    have = set(l.strip() for l in out.splitlines())
    wv = []
    if not sha_ok:
        wv.append('exe sha256 pre/post != S2NR %s...' % SHA[:12])
    miss = [w for w in rv.WITNESS if w not in have]
    if miss:
        wv.append('witness line(s) missing: ' + ' | '.join(miss))
    bl = (rd(os.path.join(d, 'BLASTER.TXT')) or '').replace('\r', '').strip()
    if bl != rv.BLASTER:
        wv.append('BLASTER.TXT [%s] != [%s]' % (bl, rv.BLASTER))
    s2 = S2.findall(log)
    share = None
    if label.startswith('B'):
        if not s2:
            wv.append('no scale2 line')
        else:
            on, brk, vfy, nar, ful = (int(x) for x in s2[-1])
            if (on, brk, vfy) != (1, 0, 0):
                wv.append('scale2 on=%d break=%d verify=%d (must be 1 0 0)' % (on, brk, vfy))
            share = 100.0 * nar / (nar + ful) if nar + ful else 0.0
            lines.append('   scale2 (information): %s' % S2.search(log).group(0)[len('DOS-PORT scale2 '):][:150])
        if DEST2X not in out:
            wv.append('render dest is not ' + DEST2X)
        if label == 'B32' and PACK24 not in out:
            wv.append('pack24 not engaged at 640x480 ("%s" missing)' % PACK24)
        sw, sinfo = stick_check(d, tag, log, kern)
        wv += sw
        if sinfo:
            lines.append(sinfo)
    else:
        if s2:
            wv.append('A16 has a scale2 line (the switch must be unset)')
        if DEST1X not in out:
            wv.append('render dest is not ' + DEST1X)
    lines.append('   witness: %s' % ('OK' if not wv else 'FAIL -- ' + '; '.join(wv)))
    g = lambda k: (re.findall(r'\b' + k + r'=(\d+)', log) or ['?'])[-1]
    lines.append('   start-up (information): preloop_ms %s loop_ms %s tail_ms %s' % (g('preloop_ms'), g('loop_ms'), g('tail_ms')))
    if r is None or wv:
        state = 'VOID'
    elif share is not None and share < 95.0:
        state = 'PATH-OFF'
        lines.append('   PATH-OFF: narrow share %.1f%% < 95%% (the design did not engage; counts as not MET)' % share)
    else:
        state = 'MET' if r else 'NOT MET'
    if state != 'VOID':
        fs = re.findall(r'^DOS-PORT tick_rate=[\d.]+ frames_skipped=(\d+)', log, re.M)
        tk = re.findall(r'^DOS-PORT tick_rate_steady=[\d.]+ ticks=(\d+)', log, re.M)
        disp = 100.0 * (1 - int(fs[-1]) / int(tk[-1])) if fs and tk else None
        avs = (re.findall(r'^audio_vital_status=(.*)$', log, re.M) or [''])[-1]
        bad = [k for k in ('overwrites', 'underruns', 'late_writes')
               if int((re.findall(r'\b' + k + r'=(\d+)', avs) or ['0'])[-1])]
        reg = (['displayed %.2f%% < 99.0%%' % disp] if disp is not None and disp < 99.0 else []) + \
              ['%s non-zero' % k for k in bad]
        lines.append('   REGRESSION: %s' % ('; '.join(reg) if reg else 'none'))
    lines.append('READ %s %s: %s' % (os.path.basename(d.rstrip('/')), label, state))
    return state, lines


def warmup(d, kpath, now=None):
    """The round's stop rule after WARMUPRY (sdlports, before any data): any stick drop in the warm-up -- its boot, the
    game's mode set and the exit to text mode -- or no live stick record stops the round before the B blocks.
    -> (ok, lines). The kernel record is vcctrl's live tee: it must carry "### TEE-START <t> UTC" at or before the cell's
    START.UTC and a "### ALIVE <t> UTC" heartbeat within 90 s of now."""
    now = now or datetime.datetime.now(UTC)
    why = []
    su = rd(os.path.join(d, 'START.UTC'))
    cs = rd(os.path.join(d, 'witness', 'card-state.log'))
    if su is None:
        return False, ['WARMUP stick: START.UTC missing -> STOP']
    ts = datetime.datetime.fromisoformat(su.strip().replace('Z', '+00:00')).astimezone(UTC)
    day = ts.strftime('%Y-%m-%d')
    if cs is None:
        why.append('witness/card-state.log missing')
    else:
        bad = []
        for ln in cs.splitlines():
            p = ln.split()
            if len(p) < 4 or not re.match(r'^\d{6}\.\d+$', p[0]):
                continue
            st, age = p[1].split('=', 1)[-1], float(p[3].split('=', 1)[-1])
            if st in BAD_STATES or age > 2.5:
                bad.append('%s %s age %.1f' % (p[0], st, age))
        if bad:
            why.append('card-state: %d bad sample(s): %s' % (len(bad), '; '.join(bad[:4])))
    k = kern_parse(kpath) if kpath else None
    if k is None:
        why.append('kernel tee missing or unreadable')
    else:
        wins, stick, drops, other = k
        tee = KTEE.get(kpath, {})
        if tee.get('start') is None or tee['start'] > ts:
            why.append('kernel tee did not start before the warm-up (TEE-START %s, START.UTC %s)' % (tee.get('start'), ts))
        if tee.get('alive') is None or (now - tee['alive']).total_seconds() > 90:
            why.append('kernel tee not alive (last ALIVE %s, now %s)' % (tee.get('alive'), now.strftime('%T')))
        ks = [x for x in drops if x[0] >= ts and x[1] in stick]
        ku = [x for x in drops if x[0] >= ts and x[1] not in stick and x[1] not in other]
        if ks:
            why.append('kernel: %d stick drop line(s), first %s on %s' % (len(ks), ks[0][0].strftime('%T'), ks[0][1]))
        if ku:
            why.append('kernel: %d drop-kind line(s) on unattributed port(s)' % len(ku))
    if why:
        return False, ['WARMUP stick: STOP -- ' + '; '.join(why)]
    return True, ['WARMUP stick: clean (card-state and kernel tee, %s .. %s UTC)' % (ts.strftime('%T'), now.strftime('%T'))]


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument('--kern')
    ap.add_argument('--window', choices=('lock', 'exit'), default='exit')
    ap.add_argument('--now')
    ap.add_argument('rest', nargs='*')
    o = ap.parse_args()
    a = o.rest
    global WINDOW
    WINDOW = o.window
    if len(a) == 2 and a[0] == 'warmup':
        now = datetime.datetime.fromisoformat(o.now).astimezone(UTC) if o.now else None
        ok, ls = warmup(a[1], o.kern, now)
        print('\n'.join(ls))
        sys.exit(0 if ok else 1)
    kern = kern_parse(o.kern) if o.kern else None
    if len(a) == 3 and a[0] == 'cell':
        print('\n'.join(cell(a[1], a[2], kern)[1]))
    elif len(a) == 4 and a[0] == 'pair' and a[1].startswith('B'):
        if os.path.realpath(a[2]) == os.path.realpath(a[3]):
            sys.exit('pair: the same cell twice')
        st = []
        for d in a[2:]:
            s, ls = cell(d, a[1], kern)
            st.append((os.path.basename(d.rstrip('/')), s))
            print('\n'.join(ls))
        n = sum(1 for _, s in st if s == 'MET')
        v = 'MET x2' if n == 2 else 'MET x1' if n == 1 else 'NOT MET'
        notmet = ', '.join('%s %s' % (t, s) for t, s in st if s != 'MET')
        print('DEPTH %s on S2NR %s (overlay build, 640x480 2x): %s%s (subject to the capture sheet CLEAN in each MET cell)' % (
            a[1], STAMP, v, (' -- not MET: ' + notmet) if notmet else ''))
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
