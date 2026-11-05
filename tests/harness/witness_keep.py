"""witness_keep.py -- keep one physical-screen frame (and, every third pass, a camera frame).

Imported by run-hw.sh's two waiting loops (the stability poll and the collection retry) so the
frames the harness was already grabbing are kept instead of overwritten. Frame files are named
<seq>_<HHMMSS.mmm>.jpg, monotonic with the wall clock; the seq is a counter file shared by both
loops. Nothing here judges a frame. See run-hw.sh's WITNESS comment for why it exists.
"""
import datetime
import json
import os
import shutil
import subprocess


def raw_frame(vcctrl_bin, dest):
    """The newest capture-card frame, RAW: `timeline` to find its seq, then `frame <seq>`.

    Not the judged `shot`/grab() path. That path refuses a frame it cannot classify as a
    picture -- including a perfectly correct STATIC screen ("every frame was a duplicate") --
    so a witness built on it would read SHORT exactly while a menu or a title sits still, and
    people learn to ignore SHORT. The daemon passes no judgement on a raw frame; a person does.
    Returns True if a frame was written."""
    try:
        out = subprocess.run([vcctrl_bin, "timeline"], capture_output=True, text=True, timeout=20).stdout
        frames = json.loads(out).get("frames") or []
        if not frames:
            return False
        seq = max(f["seq"] for f in frames)
        rc = subprocess.run([vcctrl_bin, "frame", str(seq), "--out", dest],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20).returncode
        return rc == 0 and os.path.exists(dest)
    except Exception:
        return False


def card_state(wit_dir, vcctrl_bin):
    """Append one line to witness/card-state.log: wall time, the daemon's capture-card state (locked / nosignal /
    ...), the frame counter and the age of its newest frame. Sampled every ~2 s while the cell runs, so the stream
    can be compared ACROSS a video mode switch: whether a rung is one the card genuinely cannot lock, or one it loses
    lock on after the switch, is a question this log answers with data instead of an anecdote."""
    if not wit_dir:
        return
    try:
        out = subprocess.run([vcctrl_bin, "video", "state"], capture_output=True, text=True, timeout=15).stdout
        d = json.loads(out)
        line = "%s state=%s frames=%s last_frame_age_s=%s" % (
            datetime.datetime.now().strftime("%H%M%S.%f")[:-3], d.get("state"), d.get("frames"), d.get("last_frame_age_s"))
    except Exception as exc:
        line = "%s state=UNREADABLE (%s)" % (datetime.datetime.now().strftime("%H%M%S.%f")[:-3], exc)
    with open(os.path.join(wit_dir, "card-state.log"), "a") as f:
        f.write(line + "\n")


def keep(shot, poll_no, wit_dir, vcctrl_bin):
    """Keep one witness frame. `shot` (the judged grab the caller already made) is only a
    fallback if the raw fetch fails; the frame kept is the RAW one."""
    if not wit_dir:
        return
    seqf = os.path.join(wit_dir, ".seq")
    try:
        seq = int(open(seqf).read()) + 1 if os.path.exists(seqf) else 1
        open(seqf, "w").write(str(seq))
        ts = datetime.datetime.now().strftime("%H%M%S.%f")[:-3]
        dest = os.path.join(wit_dir, "frames", "%05d_%s.jpg" % (seq, ts))
        if not raw_frame(vcctrl_bin, dest) and shot and os.path.exists(shot):
            shutil.copyfile(shot, dest)
        if poll_no % int(os.environ.get("WITNESS_CAMERA_EVERY", "1")) == 0:   # every pass by default: the card cannot see every rung
            subprocess.run([vcctrl_bin, "camera", "shot", "--out",
                            os.path.join(wit_dir, "camera", "%05d_%s.jpg" % (seq, ts))],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
    except Exception as exc:  # a witness that fails says so, it does not stop the cell
        print("  witness keep failed (%s) -- the sheet will say it is short" % exc)
