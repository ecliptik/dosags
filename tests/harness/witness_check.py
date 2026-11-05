"""witness_check.py -- the shared, structural half of "someone looked at the screen".

run-hw.sh leaves <run_dir>/witness/{sheet.png,sheet-camera.png,MANIFEST.json}. A person looks at the
sheets and records it with witness_review.py, which writes REVIEWED.txt bound to the sha256 of the sheets
that were looked at. port_game.py (check/record/validate) and parse-results.py call check() and REFUSE a
figure whose run has a witness directory but no clean, current review. "Witness reviewed: clean" is
therefore a file the tooling reads, not a sentence someone remembers to write.

check(run_dir) returns None when the run has no witness directory at all (a DOSBox-X run, or a cell from
before the standing order: those are not judged by this), else a dict with "ok" and a "detail".
"""
import hashlib
import json
import os


def _sha(path):
    if not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def sheet_shas(wdir):
    return {n: _sha(os.path.join(wdir, n)) for n in ("sheet.png", "sheet-camera.png")}


def check(run_dir):
    wdir = os.path.join(run_dir, "witness")
    if not os.path.isdir(wdir):
        return None
    rev = os.path.join(wdir, "REVIEWED.txt")
    if not os.path.exists(rev):
        return {"ok": False, "reviewed": False,
                "detail": "witness_reviewed=false: no witness/REVIEWED.txt -- look at witness/sheet.png and "
                          "sheet-camera.png, then run witness_review.py; a rate from an unreviewed run is not a result"}
    fields = {}
    for line in open(rev, errors="replace"):
        if "=" in line:
            k, v = line.split("=", 1)
            fields[k.strip()] = v.strip()
    verdict = fields.get("verdict", "")
    cur = sheet_shas(wdir)
    if fields.get("mode") == "camera-only":
        try:
            frozen = bool(((json.load(open(os.path.join(wdir, "MANIFEST.json"))) or {}).get("card") or {}).get("frozen"))
        except Exception:
            frozen = False
        if not frozen or not fields.get("card_reason"):
            return {"ok": False, "reviewed": True, "verdict": verdict,
                    "detail": "camera-only review without a recorded frozen-card reason in the manifest"}
    for name, want in (("sheet.png", fields.get("sheet_sha256")), ("sheet-camera.png", fields.get("sheet_camera_sha256"))):
        if want and cur.get(name) != want:
            return {"ok": False, "reviewed": True, "verdict": verdict,
                    "detail": "REVIEWED.txt does not match the current %s (the sheet changed after it was reviewed)" % name}
    if verdict.lower() != "clean":
        return {"ok": False, "reviewed": True, "verdict": verdict, "who": fields.get("who"),
                "detail": "witness reviewed by %s: %s -- a rate from a run whose sheet shows trails is void" % (fields.get("who"), verdict)}
    return {"ok": True, "reviewed": True, "verdict": "clean", "who": fields.get("who"), "when": fields.get("when"),
            "detail": "witness reviewed: clean (%s, %s)" % (fields.get("who"), fields.get("when"))}
