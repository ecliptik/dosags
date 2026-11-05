#!/usr/bin/env python3
"""witness_review.py RUN_DIR --who NAME --verdict clean|"trails at frames X-Y" [--note TEXT]

Records that a person LOOKED at RUN_DIR/witness/sheet.png (capture card) and sheet-camera.png (what the
monitor showed). Writes witness/REVIEWED.txt bound to the sha256 of those two sheets and flips
witness_reviewed in witness/MANIFEST.json. Anything other than the exact verdict "clean" makes the run's
figures void as far as port_game.py and parse-results.py are concerned. Refuses to record a review when the
sheet does not exist (nothing was captured) -- that cell is SHORT and its figure needs the witness rerun or an
explicit --no-witness reason, not a rubber stamp.
"""
import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import witness_check


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--who", required=True)
    ap.add_argument("--verdict", required=True)
    ap.add_argument("--note", default="")
    a = ap.parse_args()
    w = os.path.join(a.run_dir, "witness")
    shas = witness_check.sheet_shas(w)
    if shas["sheet.png"] is None and shas["sheet-camera.png"] is None:
        print("witness_review: neither %s/sheet.png nor sheet-camera.png exists -- nothing was captured to review" % w, file=sys.stderr)
        return 2
    mode, card_reason = "card+camera", ""
    try:
        man = json.load(open(os.path.join(w, "MANIFEST.json")))
        cman = json.load(open(os.path.join(w, "MANIFEST-camera.json")))
    except Exception:
        man, cman = {}, {}
    card = (man or {}).get("card") or {}
    if card.get("frozen"):
        # The capture card kept returning one picture or lost signal: a card sheet of identical tiles is not
        # evidence. A camera-only review is accepted ONLY on a recorded reason, and only if the camera witness
        # itself is complete.
        if shas["sheet-camera.png"] is None or (cman or {}).get("short", True):
            print("witness_review: the capture card was frozen (%s) and the camera witness is missing or SHORT -- there is "
                  "no picture to review. Fix the runner or rerun the cell." % card.get("state_samples"), file=sys.stderr)
            return 2
        mode = "camera-only"
        card_reason = "capture card frozen: unique_frames=%s of %s, state samples %s" % (
            card.get("unique_frames"), card.get("frames"), card.get("state_samples"))
    elif shas["sheet.png"] is None:
        print("witness_review: no card sheet and the manifest does not record a frozen card -- refusing a camera-only review "
              "with no recorded reason", file=sys.stderr)
        return 2
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = ["who=%s" % a.who, "when=%s" % now, "verdict=%s" % a.verdict, "mode=%s" % mode,
             "sheet_sha256=%s" % (shas["sheet.png"] or ""), "sheet_camera_sha256=%s" % (shas["sheet-camera.png"] or "")]
    if card_reason:
        lines.append("card_reason=%s" % card_reason)
    if a.note:
        lines.append("note=%s" % a.note)
    open(os.path.join(w, "REVIEWED.txt"), "w").write("\n".join(lines) + "\n")
    mp = os.path.join(w, "MANIFEST.json")
    if os.path.exists(mp):
        m = json.load(open(mp))
        m["witness_reviewed"] = True
        m["witness_verdict"] = a.verdict
        m["witness_reviewer"] = a.who
        json.dump(m, open(mp, "w"), indent=1)
    print("witness_review: recorded (%s: %s)" % (a.who, a.verdict))
    return 0 if a.verdict.lower() == "clean" else 1


if __name__ == "__main__":
    sys.exit(main())
