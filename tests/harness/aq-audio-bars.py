#!/usr/bin/env python3
"""aq-audio-bars.py CELL_DIR FLOOR_DB PCM_SET -- the lockable-mode audio check's bars for one AGS Quest rig cell.

Round RP onward (pre-registered before any data). Read-only. Prints one VALID line, one line per bar, and one CELL
verdict line:
  CELL <tag> PASS | FAIL <bars> | VOID <reasons>

PCM_SET is the comma list of pcm_irqs values seen in the registered DOSBox-X reference renders (e.g. "180,181").
FLOOR_DB is the round's idle floor: the median mean dBFS of the floor samples (vcctrl level, 1.5 s).

Validity (all required, else VOID; a VOID cell is reported and is neither a PASS nor a FAIL):
  V1 RUNMANI.LOG exit_code=0 and STDOUT.TXT carries "ENGINE HAS SHUTDOWN"
  V2 the voicering line is present with compactions >= 1 (the bound was exercised in this cell)
  V3 every AutoPilot phase that began, except "quit" (the game exits inside it, so it never logs ok), has status=ok,
     and the "audio" phase is among them (the flow ran as registered)
  V4 STDOUT.TXT carries "Graphics mode set: 640 x 480" (the lockable mode)
  V5 exactly one audio capture segment (<TAG>-seg01.ogg, no seg02): a reconnect splits the capture and the level bar
     cannot be read across it
  (the binary stamp, the BLASTER witness and the staging hashes are checked by the round driver, not here)
Bars (each PASS or FAIL):
  B1 pcm_irqs is in PCM_SET
  B2 underruns = 0 and overwrites = 0
  B3 silent IRQs outside room transitions = 0: silent_irqs from audio_vital_status minus the irqs of "DOS-PORT silentirq"
     lines with since_room <= 2 (a transition gap); silent IRQs not accounted for by such lines count as outside
  B4 capture card locked: witness/MANIFEST.json card.frozen is false and no WITNESS-CAPTURE-STALE.txt
  B5 level: audio-compare.py's 1.5 s windows at >= FLOOR_DB + 10 dB form exactly one contiguous run of >= 6 windows
     (9 s >= the reference's 180 chunks x 512 / 11025 Hz = 8.36 s of PCM). Calibration (information): SB4S
     (2026-09-23) and N7AQ (2026-11-06) each show one run of 9 windows at about -14 dBFS.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def rd(p):
    try:
        return open(p, errors='replace').read()
    except OSError:
        return ''


def main():
    c, floor, pset = sys.argv[1].rstrip('/'), float(sys.argv[2]), {int(x) for x in sys.argv[3].split(',')}
    tag = re.sub(r'-\d{4}-\d{2}-\d{2}$', '', os.path.basename(c))
    rm, so = rd(c + '/RUNMANI.LOG'), rd(c + '/STDOUT.TXT')
    void = []
    m = re.search(r'^exit_code=(\d+)', rm, re.M)
    if not (m and m.group(1) == '0' and 'ENGINE HAS SHUTDOWN' in so):
        void.append('V1 no clean exit (exit_code=%s)' % (m.group(1) if m else 'none'))
    vr = re.search(r'DOS-PORT voicering compact_at=(\d+) compactions=(\d+) moved_bytes=(\d+) cap_max=(\d+)', rm)
    if not vr or int(vr.group(2)) < 1:
        void.append('V2 voicering %s' % ('compactions=%s' % vr.group(2) if vr else 'line missing'))
    ap = re.findall(r'AUTOPILOT phase=(\w+) status=(\w+)', rd(c + '/AUTOPLT.LOG'))
    began = {p for p, s in ap if s == 'begin'}
    ok = {p for p, s in ap if s == 'ok'}
    bad = sorted(began - ok - {'quit'})
    if bad or 'audio' not in ok:
        void.append('V3 AutoPilot phases not ok: %s%s' % (','.join(bad) or '-', '' if 'audio' in ok else ' (no audio ok)'))
    if 'Graphics mode set: 640 x 480' not in so:
        void.append('V4 not 640 x 480')
    segs = sorted(f for f in os.listdir(c) if re.match(re.escape(tag) + r'-seg\d+\.ogg$', f, re.I))
    if len(segs) != 1:
        void.append('V5 capture segments %d' % len(segs))
    print('VALID %s %s | voicering %s' % (tag, 'yes' if not void else 'no: ' + '; '.join(void),
                                           ' / '.join(vr.groups()) if vr else 'none'))
    av = dict(kv.split('=', 1) for kv in re.search(r'audio_vital_status=([^;\n]*)', rm).group(1).split(',') if '=' in kv) \
        if 'audio_vital_status=' in rm else {}
    g = lambda k: int(av[k]) if k in av and av[k].isdigit() else None
    fails = []

    def bar(name, okb, txt):
        print('%s %s %s %s' % (name, tag, 'PASS' if okb else 'FAIL', txt))
        if not okb:
            fails.append(name)
    pi = g('pcm_irqs')
    bar('B1', pi in pset, 'pcm_irqs=%s accepted {%s}' % (pi, ','.join(map(str, sorted(pset)))))
    ur, ow = g('underruns'), g('overwrites')
    bar('B2', ur == 0 and ow == 0, 'underruns=%s overwrites=%s' % (ur, ow))
    si = g('silent_irqs')
    trans = sum(int(i) for i, s in re.findall(r'DOS-PORT silentirq tick=\d+ room=-?\d+ irqs=(\d+) since_room=(\d+)', so)
                if int(s) <= 2)
    out = None if si is None else si - trans
    bar('B3', out == 0, 'silent_irqs=%s in_transitions=%d outside=%s' % (si, trans, out))
    try:
        card = json.load(open(c + '/witness/MANIFEST.json')).get('card') or {}
    except Exception:
        card = {}
    stale = os.path.exists(c + '/witness/WITNESS-CAPTURE-STALE.txt')
    bar('B4', card.get('frozen') is False and not stale,
        'card frozen=%s stale_file=%s samples=%s' % (card.get('frozen'), int(stale), card.get('state_samples')))
    if len(segs) == 1:
        d = json.loads(subprocess.run([sys.executable, HERE + '/audio-compare.py', os.path.join(c, segs[0]),
                                       '--floor-db', str(floor)], capture_output=True, text=True).stdout)
        L = d['level_db']
        hot = [i for i, x in enumerate(L) if x >= floor + 10]
        runs = []
        for i in hot:
            if runs and i == runs[-1][1] + 1:
                runs[-1][1] = i
            else:
                runs.append([i, i])
        lens = [b - a + 1 for a, b in runs]
        peak = max(L) if L else None
        bar('B5', len(runs) == 1 and lens[0] >= 6,
            'floor %.1f dB, windows >= floor+10: runs %s (start s %s), max window %.1f dBFS, %d windows / %.1f s' % (
                floor, lens, [round(a * 1.5, 1) for a, _ in runs], peak, len(L), d.get('seconds', 0)))
    else:
        bar('B5', False, 'unreadable (segments %d)' % len(segs))
    if void:
        print('CELL %s VOID %s' % (tag, '; '.join(void)))
    elif fails:
        print('CELL %s FAIL %s' % (tag, ' '.join(fails)))
    else:
        print('CELL %s PASS' % tag)


if __name__ == '__main__':
    main()
