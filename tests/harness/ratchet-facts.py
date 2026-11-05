#!/usr/bin/env python3
"""ratchet-facts.py -- one cell's deterministic counters as RATCHET key=value lines.

    tests/harness/ratchet-facts.py <cell-dir>

Reads <cell-dir>/{RUNMANI.LOG,STDOUT.TXT,SDLDBG.LOG,run.log} (lab-cell.sh keeps them) and prints
one "RATCHET k=v" line per figure, for tests/ratchet.yaml. A figure this cell cannot give is
printed as NA (a ratchet check reading it then ERRORs), never as 0:

  stale_frames      ags 0192 verifier (DOS-PORT presentverify ... stale_frames=), last line
  pcm_irqs          IRQs that played PCM data (audio_vital_status, last)
  pcm_unaccounted   mixed - pcm_irqs - inflight (ags 0252): chunks the mixer produced while a
                    voice was active, minus IRQs that played data, minus chunks still queued
                    (stream + ring) when the status was taken (binaries before inflight=:
                    not subtracted, so sound playing through quit reads positive).
                    pcm_unaccounted_abs is its magnitude (the ratchet allows +-1: a partial
                    chunk, or one played between the two reads). Since SDL 0192 the SB silence gate is
                    off while content is active, so EVERY mixed chunk -- a sound's own digital
                    silence and, on the 8-bit path, its quiet passages included -- must be
                    played: 0 is exact accounting, > 0 is audio lost (overwritten, dropped),
                    < 0 is data played that the mixer never made (the gate letting idle
                    silence through). First measured exact on DOSBox-X 2026-09-23: 232 = 232,
                    108 of them all-zero.
  overwrites, underruns, silent_irqs, underflow_pads, partial_pulls   audio_vital_status, as
                    printed (the last two: ags 0213 / SDL 0197; NA on older binaries)
  midi_late_writes  isr mode: late_writes; poll mode: late50 (events > 50 ms late). Same
                    meaning in both modes, so a poll-mode control yields a number.
  midi_late_max_ms  audio_vital_status late_max_ms (both modes)
  sb_clk_permille   SB alive (2026-09-24): the ISR replay's MIDI song clock over the RTC span,
                    per mille (`clk=<song_ms>/<rtc_s>s`: song_ms / rtc_s). The song clock advances
                    only on SB IRQs, so a dead SB falls far behind (lab/journeys DLY-v1b: 213);
                    healthy runs are 956-983. NA without the ISR replay or with rtc_s <= 0.
  mistall_n         "MISTALL" lines (ags 0251 forced stalls that fired)
  code_lock_bytes   SDL 0194 "program code lock [...] = N bytes: locked" (SDLDBG.LOG; the cell
                    needs DOS_PORT_LOG=1); NA if absent, and NA if the line says anything but
                    "locked"
  exe_bytes         size of the AGS.EXE the cell staged (from run.log's stage dir), if present

Exit 1 if RUNMANI.LOG is missing (the cell did not finish).
"""
import os
import re
import sys


def read(path):
    try:
        return open(path, errors='replace').read()
    except OSError:
        return ''


def last_kv(text, key):
    m = re.findall(r'\b%s=([0-9]+)\b' % re.escape(key), text)
    return m[-1] if m else None


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    d = sys.argv[1]
    rm = read(os.path.join(d, 'RUNMANI.LOG'))
    if not rm:
        print('MISSING RUNMANI.LOG in %s' % d)
        return 1
    so = read(os.path.join(d, 'STDOUT.TXT'))
    dbg = read(os.path.join(d, 'SDLDBG.LOG'))
    runlog = read(os.path.join(d, 'run.log'))
    out = {}

    pv = [l for l in (so + '\n' + runlog).splitlines() if 'presentverify frames=' in l]
    out['stale_frames'] = last_kv(pv[-1], 'stale_frames') if pv else None

    avs = re.findall(r'audio_vital_status=(\S+)', rm)
    a = avs[-1] if avs else ''
    pcm, midi = (a.split(';', 1) + [''])[:2] if a else ('', '')
    for k in ('pcm_irqs', 'overwrites', 'underruns', 'silent_irqs', 'underflow_pads', 'partial_pulls'):
        out[k] = last_kv(pcm, k)
    mixed = last_kv(pcm, 'mixed')
    # audio_vital_status=NA: the mixer never opened, so it mixed no chunks -- a true 0 (the one
    # field that can say so; every other audio figure stays NA)
    out['pcm_mixed'] = mixed if mixed is not None else ('0' if avs and avs[-1] == 'NA' else None)
    out['pcm_mixed_zero'] = last_kv(pcm, 'mixed_zero')
    out['pcm_mixed_quiet'] = last_kv(pcm, 'mixed_quiet')
    infl = re.findall(r'\binflight=(-?[0-9]+)', pcm)
    out['pcm_inflight'] = infl[-1] if infl else None
    if mixed is not None and out['pcm_irqs'] is not None:
        u = int(mixed) - int(out['pcm_irqs'])
        if infl and int(infl[-1]) >= 0:
            u -= int(infl[-1])
        out['pcm_unaccounted'] = str(u)
        out['pcm_unaccounted_abs'] = str(abs(u))
    else:
        out['pcm_unaccounted'] = None
        out['pcm_unaccounted_abs'] = None
    if 'midi_tick=isr' in midi:
        out['midi_late_writes'] = last_kv(midi, 'late_writes')
    elif 'midi_tick=poll' in midi:
        out['midi_late_writes'] = last_kv(midi, 'late50')
    else:
        out['midi_late_writes'] = None
    out['midi_late_max_ms'] = last_kv(midi, 'late_max_ms')
    out['midi_events'] = last_kv(midi, 'events')
    ck = re.findall(r'clk=([0-9]+)/(-?[0-9]+)s', midi)
    if 'midi_tick=isr' in midi and ck and int(ck[-1][1]) > 0:
        out['sb_clk_permille'] = str(int(ck[-1][0]) // int(ck[-1][1]))
    else:
        out['sb_clk_permille'] = None

    out['mistall_n'] = str(len(re.findall(r'MISTALL tick=', so)))

    m = re.findall(r'program code lock \[[^]]*\) = ([0-9]+) bytes: (\S+)', dbg)
    # (lab-cell.sh keeps the stage's LOGS/SDLDBG.LOG as SDLDBG.LOG)
    out['code_lock_bytes'] = m[-1][0] if m and m[-1][1] == 'locked' else None

    st = re.findall(r'(/tmp/dos-port-dosbox\.[A-Za-z0-9]+)', runlog)
    exe = ''
    if st and os.path.isdir(st[-1]):
        exe = next((os.path.join(st[-1], f) for f in os.listdir(st[-1]) if f.lower() == 'ags.exe'), '')
    out['exe_bytes'] = str(os.path.getsize(exe)) if exe else None

    for k, v in out.items():
        print('RATCHET %s=%s' % (k, v if v is not None else 'NA'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
