#!/usr/bin/env python3
"""audio-compare.py -- judge a real-hardware audio capture against a reference render.

Step 8.3 (PLAN.md). The capture harness is the judge of SB audio correctness; this is the part
of it that compares WHAT played, not just THAT something played. Inputs are any files ffmpeg
decodes (the vcctrl Ogg Opus side-stream recording, a DOSBox-X F12+W WAV). Everything is
decoded to mono 11025 Hz.

  audio-compare.py CAPTURE [--ref REF] [--floor-db DB] [--from S] [--to S] [--ref-from S] [--ref-to S]

Prints one JSON object:
  level      per 1.5 s window: mean dBFS; count of windows >= floor+10 dB (--floor-db, the
             capture's idle floor measured with the target at a DOS prompt)
  tempo      dominant period (s) of the onset-strength envelope's autocorrelation, 0.25-2.0 s
  with --ref:
    tempo_ratio   capture period / reference period
    chroma_score  mean cosine similarity of 0.5 s chroma frames at the best alignment
                  (lags whose overlap covers >= half the shorter side's non-silent frames;
                  silent frames skipped), and two CONTROLS computed the same way:
                  the reference transposed by 5 semitones, and time-reversed. A match has to
                  beat both controls, or the score says nothing about melody.

No thresholds live here; the pre-registration in PLAN.md states them.
"""
import argparse
import json
import subprocess
import sys

import numpy as np

SR = 11025
N_FFT = 2048
HOP = 256


def load(path, t0=None, t1=None):
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error"]
    if t0 is not None:
        cmd += ["-ss", str(t0)]
    cmd += ["-i", path]
    if t1 is not None:
        cmd += ["-t", str(t1 - (t0 or 0))]
    cmd += ["-ac", "1", "-ar", str(SR), "-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)


def stft_mag(x):
    if len(x) < N_FFT:
        x = np.pad(x, (0, N_FFT - len(x)))
    n = 1 + (len(x) - N_FFT) // HOP
    idx = np.arange(N_FFT)[None, :] + HOP * np.arange(n)[:, None]
    frames = x[idx] * np.hanning(N_FFT)[None, :]
    return np.abs(np.fft.rfft(frames, axis=1))


def level_windows(x, win_s=1.5):
    w = int(win_s * SR)
    out = []
    for i in range(0, len(x) - w + 1, w):
        rms = np.sqrt(np.mean(x[i:i + w] ** 2)) + 1e-12
        out.append(round(20 * np.log10(rms), 1))
    return out


def onset_env(mag):
    flux = np.maximum(np.diff(np.log1p(mag * 100), axis=0), 0).sum(axis=1)
    flux = flux - np.convolve(flux, np.ones(16) / 16, mode="same")
    return np.maximum(flux, 0)


def tempo_period(env):
    fps = SR / HOP
    env = env - env.mean()
    ac = np.correlate(env, env, mode="full")[len(env) - 1:]
    lo, hi = int(0.25 * fps), int(2.0 * fps)
    if hi >= len(ac):
        return None
    lag = lo + int(np.argmax(ac[lo:hi]))
    return round(lag / fps, 4)


def chroma(mag, frame_s=0.5):
    """0.5 s chroma frames (unit vectors) and a per-frame 'has content' mask (frame energy within
    40 dB of the loudest frame), so silence -- whose normalised chroma is noise -- never scores."""
    freqs = np.fft.rfftfreq(N_FFT, 1.0 / SR)
    sel = (freqs >= 55) & (freqs <= 2000)
    pc = (np.round(12 * np.log2(freqs[sel] / 440.0)) % 12).astype(int)
    c = np.zeros((mag.shape[0], 12))
    for k in range(12):
        c[:, k] = (mag[:, sel][:, pc == k] ** 2).sum(axis=1)
    per = max(1, int(frame_s * SR / HOP))
    n = c.shape[0] // per
    c = c[:n * per].reshape(n, per, 12).mean(axis=1)
    e = c.sum(axis=1)
    mask = e > (e.max() * 1e-4 if len(e) else 0)
    c = c / (np.linalg.norm(c, axis=1, keepdims=True) + 1e-12)
    return c, mask


def best_alignment(a, b, frac=0.5):
    """Best mean cosine over all lags whose overlap covers >= frac of the shorter sequence's
    content frames; frames where either side is silent are skipped."""
    (ca, ma), (cb, mb) = a, b
    need = max(8, int(frac * min(ma.sum(), mb.sum())))
    best = (-1.0, 0)
    for lag in range(-(len(cb) - 1), len(ca)):
        a0, b0 = max(0, lag), max(0, -lag)
        n = min(len(ca) - a0, len(cb) - b0)
        if n <= 0:
            continue
        m = ma[a0:a0 + n] & mb[b0:b0 + n]
        if m.sum() < need:
            continue
        s = float(np.mean(np.sum(ca[a0:a0 + n][m] * cb[b0:b0 + n][m], axis=1)))
        if s > best[0]:
            best = (s, lag)
    return round(best[0], 4), best[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("capture")
    ap.add_argument("--ref")
    ap.add_argument("--floor-db", type=float)
    ap.add_argument("--from", dest="t0", type=float)
    ap.add_argument("--to", dest="t1", type=float)
    ap.add_argument("--ref-from", type=float)
    ap.add_argument("--ref-to", type=float)
    a = ap.parse_args()

    x = load(a.capture, a.t0, a.t1)
    mx = stft_mag(x)
    lv = level_windows(x)
    res = {"capture": a.capture, "seconds": round(len(x) / SR, 2), "level_db": lv,
           "tempo_period_s": tempo_period(onset_env(mx))}
    if a.floor_db is not None:
        res["windows_10db_over_floor"] = sum(1 for v in lv if v >= a.floor_db + 10)
        res["windows_total"] = len(lv)
    if a.ref:
        r = load(a.ref, a.ref_from, a.ref_to)
        mr = stft_mag(r)
        tp = tempo_period(onset_env(mr))
        res["ref"] = a.ref
        res["ref_tempo_period_s"] = tp
        if tp and res["tempo_period_s"]:
            res["tempo_ratio"] = round(res["tempo_period_s"] / tp, 4)
        cx, cr = chroma(mx), chroma(mr)
        res["chroma_score"], res["chroma_lag_frames"] = best_alignment(cx, cr)
        res["control_transposed5"] = best_alignment(cx, (np.roll(cr[0], 5, axis=1), cr[1]))[0]
        res["control_reversed"] = best_alignment(cx, (cr[0][::-1], cr[1][::-1]))[0]
    json.dump(res, sys.stdout, indent=1)
    print()


if __name__ == "__main__":
    main()
