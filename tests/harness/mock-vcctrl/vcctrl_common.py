"""Shim of ~/git/vcctrl/bin/vcctrl_common.py for the MOCK vcctrl next to it:
the handful of names hw_guard.py / run-hw.sh import, implemented over the
mock CLI so that no real daemon is ever contacted. Same signatures, same
return conventions (None = could not / did not)."""
import json, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
VCCTRL = os.path.join(HERE, "vcctrl")
LOCK_OWNER = None


def set_lock_owner(name):
    global LOCK_OWNER
    LOCK_OWNER = name


def vc(*args, check=True):
    r = subprocess.run([VCCTRL] + list(args), capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError("mock vcctrl %s failed" % " ".join(args))
    return r.stdout.strip()


def vc_json(*args):
    out = vc(*args, check=False)
    return json.loads(out) if out else {}


def _ready_edges():
    ch = vc_json("led-changes", "80").get("changes", [])
    return sum(1 for c in ch if c["from"]["scrolllock"] == 0 and c["to"]["scrolllock"] == 1), \
        max((c["seq"] for c in ch), default=0)


_EDGES_AT_IMPORT = None


def wait_cold_boot(timeout=240):
    """The mock's power cycle lays its edges down synchronously, so "did a
    boot complete" is whether a ready edge appeared since this module was
    imported (hw_guard imports it before it does anything). Deliberately
    NOT answered by calling verify-input: the tests count those calls."""
    now, _ = _ready_edges()
    return 42.0 if now > _EDGES_AT_IMPORT else None


def select_boot_profile(digit, edge_timeout=60, ready_timeout=200):
    before, _ = _ready_edges()
    vc("combo", "ctrl", "alt", "delete", check=False)
    after, _ = _ready_edges()
    return {"edge_s": 1.0, "ready_s": 16.0, "attempts": 0, "keys": 0} if after > before else None


def grab(tag, n=16):
    """(path, mean) of the mock's current screen -- static, so run-hw.sh's
    wait_for_stable_screen settles at its own floor."""
    dst = os.path.join(os.environ["MOCK_VC_STATE"], "grab-%s.jpg" % tag)
    vc("shot", "--out", dst, check=False)
    return (dst, 10.0) if os.path.exists(dst) else (None, None)


_EDGES_AT_IMPORT, _ = _ready_edges() if os.environ.get("MOCK_VC_STATE") else (0, 0)
