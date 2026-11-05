#!/usr/bin/env python3
"""generate_assets.py -- builds this overlay's own WAV clip and MIDI
track from scratch (no external audio tools, no third-party samples).
Original work, CC0 (no rights reserved) -- see LICENSE-NOTES.md.

Run from this directory: `python3 generate_assets.py`. Regenerates
autopilot_chime.wav and autopilot_tune.mid in place; both are also
committed as binary output so the harness doesn't need this script at
build time, only at asset-authoring time.
"""
import math
import struct
import wave

# ---------------------------------------------------------------- WAV ----
# A short two-tone ascending "pickup" chime -- exercises the SB PCM path
# in the harness's `audio` phase. Mono, 16-bit PCM, 22050 Hz (a DOS
# Sound Blaster-friendly rate).

SAMPLE_RATE = 22050


def tone(freq_hz, duration_s, amplitude=0.5, fade_s=0.01):
    n = int(SAMPLE_RATE * duration_s)
    fade_n = max(1, int(SAMPLE_RATE * fade_s))
    samples = []
    for i in range(n):
        t = i / SAMPLE_RATE
        env = 1.0
        if i < fade_n:
            env = i / fade_n
        elif i > n - fade_n:
            env = (n - i) / fade_n
        v = amplitude * env * math.sin(2 * math.pi * freq_hz * t)
        samples.append(int(v * 32767))
    return samples


def write_wav(path):
    data = tone(523.25, 0.10) + tone(783.99, 0.14)  # C5 then G5
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        f.writeframes(struct.pack(f"<{len(data)}h", *data))


# --------------------------------------------------------------- MIDI ----
# A short 8-note original tune, Standard MIDI File format 0, single
# track, one instrument (Lead 1 (square), program 80 -- a chiptune-ish
# voice fitting a DOS game). Hand-built byte-for-byte; no MIDI library.

def vlq(n):
    """MIDI variable-length quantity encoding."""
    out = [n & 0x7F]
    n >>= 7
    while n:
        out.insert(0, (n & 0x7F) | 0x80)
        n >>= 7
    return bytes(out)


def build_midi(path):
    ticks_per_quarter = 96
    note_len = ticks_per_quarter // 2  # eighth notes
    # A simple ascending-then-resolving 8-note phrase, MIDI note numbers.
    melody = [60, 62, 64, 65, 67, 65, 64, 60]  # C D E F G F E C

    events = bytearray()
    events += vlq(0) + bytes([0xC0, 80])  # program change: Lead 1 (square)
    for i, note in enumerate(melody):
        dt_on = 0 if i == 0 else 0
        events += vlq(dt_on) + bytes([0x90, note, 100])   # note on
        events += vlq(note_len) + bytes([0x80, note, 0])  # note off
    events += vlq(0) + bytes([0xFF, 0x2F, 0x00])  # end of track

    mtrk = b"MTrk" + struct.pack(">I", len(events)) + bytes(events)
    mthd = b"MThd" + struct.pack(">IHHH", 6, 0, 1, ticks_per_quarter)

    with open(path, "wb") as f:
        f.write(mthd + mtrk)


if __name__ == "__main__":
    write_wav("autopilot_chime.wav")
    build_midi("autopilot_tune.mid")
    print("wrote autopilot_chime.wav, autopilot_tune.mid")
