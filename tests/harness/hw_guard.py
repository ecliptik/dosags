#!/usr/bin/env python3
"""hw_guard.py -- "did the reboot actually take?", and the one recovery.

WHY THIS EXISTS. vcctrl's send-file/get-file --return reboot the target
twice: into the NET profile for the FTP session, and back out. vcctrl proves
the FIRST reboot itself (it refuses if Scroll Lock never clears). Nothing
proved the RETURN one, and on 2026-09-16 and again on 2026-09-17 it never
happened: the mTCP session finished ("221 Goodbye"), the PS/2 link was no
longer carrying keystrokes, the reboot chord went nowhere, the job still
reported ok, and the target sat at the finished FTP log until the operator
noticed by eye. The next cell then hung in its own first reboot. A harness
bug is a bug: this makes the harness notice, recover ONCE, and say so in the
run record.

THE WITNESS is positive, not the absence of an error:
  * LED edges, from the daemon's own trace (`vcctrl led-changes`): POST
    clears Scroll Lock (1 -> 0, "a reset happened") and RDYPULSE.COM -- the
    last line of AUTOEXEC's READY path, right after it prints
    "[<profile>] ready." -- sets it (0 -> 1, "a boot completed"). A --return
    job must show TWO completed boots after the point it started; a power
    cycle, one. Counted by trace sequence number, so no clock on this side
    is compared with the daemon's.
  * The screen, read by OCR from a judged `vcctrl shot`: it must not still
    be the mTCP log. Recorded with every verdict; an LED "ready" under an
    FTP screen is a contradiction and counts as NO witness.
Reading both is passive: no keystroke is sent to find out.

THE RECOVERY (only ever after a file-job step, when no SDL3-DOS program can
be running -- verify-input's lock-key press lands in a running game as real
input, so it is NEVER sent while one may be alive; run-hw.sh's long comment
on that stands): confirm the input lock is free, run verify-input, and
  * verified false -> ONE full power cycle, wait for the POST/ready edge
    pair (vcctrl_common.wait_cold_boot, the tested primitive), read the
    screen, verify-input must now be true;
  * verified true  -> the link is alive and the machine simply did not
    reboot: one reboot chord through vcctrl_common.select_boot_profile(None)
    (which carries its own edge witnesses); if that fails, the power cycle.
A second recovery in the same run is refused: the run stops with a message.
This never loops on power actions.

Every recovery appends one HW-RECOVERY line to the run record
(RECOVERY.TXT in the collected dir -- port_game.py check surfaces it) and to
tests/harness/results/hw-recoveries.log, so how often this happens is a
number rather than a memory.

THE MAINTENANCE WINDOW. An operator can say "this machine stays off (or
untouched) until <time>": `hw_guard.py hold-set --until 2026-09-17T15:15
--reason "..."`. Until then `hold-check` exits 4, run-hw.sh and
run-probe-hw.sh refuse to start, and -- the part that matters -- the
recovery refuses too: a harness that power-cycles a machine somebody
switched off on purpose is worse than one that hangs. Every power or input
action in this file goes through require_no_hold(). The hold lives outside
the repo ($HW_HOLD_FILE, default ~/.config/dosags/hw-hold.json): it is a
fact about one bench on one afternoon, not about the project. An expired
hold is ignored and reported as expired; `hold-clear` removes it.

FORCED-FAILURE FLAGS, to exercise the branches on a healthy machine:
  HW_GUARD_FORCE_NO_WITNESS=send,collect   the named step(s) report "no
      witness" without waiting out the bound
  HW_GUARD_FORCE_VERIFY_FALSE=1            the recovery's FIRST verify-input
      reading is treated as false (the real reading is still taken and logged)
A forced recovery is recorded as forced=1 so it can never be mistaken for a
real fault in the log.

The generic procedure lives in the hub:
.sdl-dos-ports shared/skills/dos-rig-operations/references/power-management.md
"""
import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
VCCTRL_BIN = os.environ.get("VCCTRL_BIN", os.path.join(REPO_ROOT, "..", "vcctrl", "bin", "vcctrl"))
sys.path.insert(0, os.path.dirname(VCCTRL_BIN))
import vcctrl_common as vcc  # noqa: E402

PERSISTENT_LOG = os.environ.get("HW_GUARD_PERSISTENT_LOG", os.path.join(HERE, "results", "hw-recoveries.log"))
HOLD_FILE = os.environ.get("HW_HOLD_FILE", os.path.join(os.path.expanduser("~"), ".config", "dosags", "hw-hold.json"))
WITNESS_S_ENV = "HW_GUARD_WITNESS_S"  # override the witness bound (the dry-run tests use seconds, not minutes)

# A working return reboot has been seen to take ~85 s end to end on this machine,
# so nothing is declared failed before well past that.
DEFAULT_WITNESS_S = 150

FTP_MARKERS = ("goodbye", "transfer complete", "server closed", "ftp>", "mtcp", "ftp session ended")  # last: vcctrl 1e5a1e7 BATs (FTP output to NUL), 2026-11-05


def _parse_when(text):
    """ISO 8601. A value with no UTC offset means THIS machine's local time,
    which is the bench's wall clock -- what an operator saying "15:15" means."""
    import datetime
    dt = datetime.datetime.fromisoformat(text.strip().replace(" ", "T"))
    if dt.tzinfo is None:
        dt = dt.astimezone()
    return dt


def active_hold():
    """(until_datetime, reason) while a hold is in force, else None."""
    import datetime
    try:
        with open(HOLD_FILE) as f:
            h = json.load(f)
        until = _parse_when(h["until"])
    except (OSError, ValueError, KeyError):
        return None
    if datetime.datetime.now(datetime.timezone.utc) >= until:
        return None
    return until, h.get("reason", "")


def require_no_hold(what):
    h = active_hold()
    if h is None:
        return True
    print("hw_guard: REFUSED (%s) -- maintenance window: no power or input action on the target "
          "before %s. Reason: %s. (%s; `hw_guard.py hold-clear` lifts it.)"
          % (what, h[0].isoformat(timespec="minutes"), h[1] or "none given", HOLD_FILE), file=sys.stderr)
    return False


def cmd_hold_set(args):
    until = _parse_when(args.until)
    os.makedirs(os.path.dirname(HOLD_FILE), exist_ok=True)
    with open(HOLD_FILE, "w") as f:
        json.dump({"until": until.isoformat(), "reason": args.reason,
                   "set_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}, f)
    print("hold set until %s (%s)" % (until.isoformat(timespec="minutes"), HOLD_FILE))
    return 0


def cmd_hold_clear(_args):
    try:
        os.remove(HOLD_FILE)
        print("hold cleared")
    except OSError:
        print("no hold file")
    return 0


def cmd_hold_check(_args):
    if require_no_hold("hold-check"):
        try:
            with open(HOLD_FILE) as f:
                print("no hold in force (an EXPIRED one is on file: %s)" % json.load(f).get("until"))
        except (OSError, ValueError):
            print("no hold in force")
        return 0
    return 4


def led_changes(n=80):
    try:
        return vcc.vc_json("led-changes", str(n)).get("changes", [])
    except Exception:
        return []


def newest_seq():
    ch = led_changes(4)
    return max((c.get("seq", 0) for c in ch), default=0)


def edges_since(seq0):
    """(post_edges, ready_edges) among LED transitions with seq > seq0."""
    post = ready = 0
    for c in led_changes():
        if c.get("seq", 0) <= seq0:
            continue
        f, t = c.get("from", {}), c.get("to", {})
        if f.get("scrolllock") == 1 and t.get("scrolllock") == 0:
            post += 1
        if f.get("scrolllock") == 0 and t.get("scrolllock") == 1:
            ready += 1
    return post, ready


def screen_reading(save_to=None):
    """'ready-prompt' | 'ftp-log' | 'other' | 'no-picture' | 'no-ocr', by OCR
    of a judged frame. Passive."""
    out = save_to or os.path.join(tempfile.mkdtemp(prefix="hwguard-"), "shot.jpg")
    r = subprocess.run([VCCTRL_BIN, "shot", "--out", out], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(out):
        return "no-picture"
    try:
        o = subprocess.run(["tesseract", out, "-", "--psm", "6"], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return "no-ocr"
    text = o.stdout.lower()
    tail = "\n".join([ln for ln in text.splitlines() if ln.strip()][-8:])
    if any(m in tail for m in FTP_MARKERS):
        return "ftp-log"
    if re.search(r"\]\s*ready", text):
        return "ready-prompt"
    # A bare DOS prompt as the LAST line ("C:\DOSAGS>"): the game has exited and left the console. A running
    # game shows a picture, whose OCR does not end in a drive-prompt line. Used to tell "the game is done
    # and the link is dead" (recover) from "the game is still running" (send nothing).
    #
    # 2026-09-22: broadened from an anchored `^[a-z]:\\[^\s>]*>[\s_]*$` (required a clean read of the
    # ENTIRE "C:\DOSAGS>" prefix) after real-hardware evidence (dosags' keepalive investigation,
    # PLAN.md, HANGTEST2) showed tesseract can misread the whole "C:\" prefix on a bare, otherwise-
    # empty screen -- "C:\DOSAGS>" came back as "U =NDUSAGS>" three separate times, same frame content,
    # same --psm 6 this function actually uses. The colon+backslash almost never survive that specific
    # failure mode, so no amount of loosening the MIDDLE of that old pattern would have matched it: the
    # anchor itself was the wrong end. What tesseract does get right, consistently, is the trailing ">"
    # (a visually distinct glyph) and that the line is short (a prompt, not a sentence or a boot-log
    # line). So this now anchors on THOSE two ends instead: any short last line ending in ">" (trailing
    # whitespace/underscore ignored), at least 2 characters before it so a lone ">" from noise doesn't
    # count. Deliberately NOT anchoring on the drive-letter prefix at all any more.
    #
    # Why this doesn't loosen ftp-log/ready-prompt: both are checked, and can already return, above this
    # point -- this branch only ever runs once neither matched, so nothing here changes what counts as
    # either of those.
    #
    # Why a real game's on-screen text is unlikely to false-positive into this: AGS dialogue/UI text is
    # English sentences and does not end in a literal ">" as a matter of course (that is a DOS/shell
    # prompt convention, not natural game text) -- checked against this session's own logged game text
    # (AGS Quest's speech lines, Maniac Mansion Deluxe's "Please select two other kids.") to confirm none
    # of it would match. And if it ever does false-positive anyway, both this function's callers are
    # already bounded by an existing property, not a new one this change introduces: `guard recover`'s
    # reboot-chord against a still-running SDL3-DOS game fails harmlessly (the game's own replaced
    # keyboard IRQ handler means the chord simply does not land -- see run-hw.sh's own long comment on
    # exactly this), and the keepalive's Caps Lock press is not bound to any AGS game action.
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if lines:
        core = lines[-1].rstrip(" _")
        if core.endswith(">") and 2 <= len(core) <= 30:
            return "dos-prompt"
    return "other"


def forced_steps():
    return {s.strip() for s in os.environ.get("HW_GUARD_FORCE_NO_WITNESS", "").split(",") if s.strip()}


def cmd_screen(_args):
    """Print one word: the OCR classification of the current screen (passive, sends nothing)."""
    print(screen_reading())
    return 0


def cmd_seq(_args):
    print(newest_seq())
    return 0


def cmd_witness(args):
    if args.step in forced_steps():
        print(json.dumps({"witness": False, "forced": True, "step": args.step,
                          "note": "HW_GUARD_FORCE_NO_WITNESS -- bound not waited out"}))
        return 1
    t0 = time.time()
    post = ready = 0
    while True:
        post, ready = edges_since(args.since_seq)
        if ready >= args.need:
            break
        if time.time() - t0 >= args.timeout:
            break
        time.sleep(3)
    screen = screen_reading(args.shot)
    ok = ready >= args.need and screen != "ftp-log"
    print(json.dumps({"witness": ok, "forced": False, "step": args.step, "post_edges": post,
                      "ready_edges": ready, "need": args.need, "screen": screen,
                      "waited_s": round(time.time() - t0, 1)}))
    return 0 if ok else 1


def verify_input():
    r = subprocess.run([VCCTRL_BIN, "verify-input"], capture_output=True, text=True)
    try:
        return bool(json.loads(r.stdout).get("verified")), r.stdout.strip().replace("\n", " ")[:300]
    except Exception:
        return False, ("unparseable: " + (r.stdout or r.stderr))[:300]


def lock_owner():
    try:
        return vcc.vc_json("lock", "status").get("owner")
    except Exception:
        return "UNKNOWN"


def lock_staleness():
    """How long the lock has been held, and whether anything is actually running.

    A refusal has to stay a refusal -- the guard does not touch a machine
    someone else holds, and that rule does not bend. But on 2026-09-19 a
    cell was blocked for 307 s by another Claude session's vcctrl MCP
    process, which had taken the lock through STATUS POLLING and never
    released it, with nothing inflight the whole time. The guard could not
    tell that from someone genuinely driving the machine, so it gave up
    identically in both cases and the failure surfaced as a send-file
    verification error pointing at the transfer.

    Reporting held_s and inflight emptiness does not change the decision;
    it makes "stale, safe to escalate" legible to whoever reads the record
    without them having to work it out. Returns (held_s, inflight_count),
    either as None when unavailable -- this is diagnostics, and it must
    never be the reason a refusal fails to be logged.
    """
    held_s = inflight_n = None
    try:
        held_s = vcc.vc_json("lock", "status").get("held_s")
    except Exception:
        pass
    try:
        infl = vcc.vc_json("activity").get("inflight")
        if isinstance(infl, list):
            inflight_n = len(infl)
    except Exception:
        pass
    return held_s, inflight_n


def write_record(args, fields):
    line = "HW-RECOVERY " + " ".join("%s=%s" % (k, json.dumps(v) if isinstance(v, str) and (" " in v or not v) else v)
                                      for k, v in fields.items())
    for path in (args.record, PERSISTENT_LOG):
        if not path:
            continue
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "a") as f:
            f.write(line + "\n")
    print(line)


def power_cycle_and_verify(owner):
    """One power cycle, then the full boot and the link. Returns (ok, detail)."""
    if not require_no_hold("power cycle"):
        return False, "maintenance window -- power cycle refused"
    vcc.set_lock_owner(owner)
    subprocess.run([VCCTRL_BIN, "lock", "acquire", "--as", owner], capture_output=True, text=True)
    try:
        r = subprocess.run([VCCTRL_BIN, "power", "cycle", "--as", owner], capture_output=True, text=True)
        if r.returncode != 0:
            return False, "power cycle refused: " + (r.stdout or r.stderr).strip()[:200]
        booted = vcc.wait_cold_boot(240)
    finally:
        subprocess.run([VCCTRL_BIN, "lock", "release", "--as", owner], capture_output=True, text=True)
    if booted is None:
        return False, "no POST/ready edge pair within 240 s of the power cycle"
    time.sleep(3)
    screen = screen_reading()
    ok, raw = verify_input()
    return ok and screen != "ftp-log", "boot_s=%.0f screen=%s verify_input=%s" % (booted, screen, ok)


def cmd_recover(args):
    t0 = time.time()
    forced = args.step in forced_steps()
    if args.state and os.path.exists(args.state):
        print("hw_guard: REFUSED -- this run already used its one automatic recovery (%s). "
              "A second reboot failure in one run is a hardware fault, not something to power-cycle "
              "through: stopping. See tests/harness/results/hw-recoveries.log."
              % open(args.state).read().strip(), file=sys.stderr)
        write_record(args, {"tag": args.tag, "step": args.step, "seen": args.seen, "action": "none",
                            "outcome": "STOPPED-second-failure", "forced": int(forced),
                            "time_lost_s": 0, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        return 3
    if args.state:
        with open(args.state, "w") as f:
            f.write("%s at %s" % (args.step, time.strftime("%H:%M:%S")))

    if not require_no_hold("recover at step '%s'" % args.step):
        write_record(args, {"tag": args.tag, "step": args.step, "seen": args.seen, "action": "none",
                            "outcome": "STOPPED-maintenance-window", "forced": int(forced),
                            "time_lost_s": 0, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        return 4

    owner = lock_owner()
    if owner not in (None, "", "UNKNOWN"):
        held_s, inflight_n = lock_staleness()
        stale = (inflight_n == 0)
        hint = ""
        if stale:
            hint = (" -- NOTHING INFLIGHT, so this lock is very likely STALE."
                    " First question: is another session polling the rig?"
                    " vcctrl_power_state/vcctrl_activity have been observed"
                    " taking this lock and not releasing it.")
        print("hw_guard: REFUSED -- input lock is held by %r (held_s=%s inflight=%s)%s"
              % (owner, held_s, inflight_n, hint), file=sys.stderr)
        write_record(args, {"tag": args.tag, "step": args.step, "seen": args.seen, "action": "none",
                            "outcome": "STOPPED-lock-held-by-" + str(owner), "forced": int(forced),
                            "lock_held_s": held_s, "lock_inflight": inflight_n,
                            "lock_looks_stale": int(bool(stale)),
                            "time_lost_s": 0, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
        return 3

    real_verified, raw = verify_input()
    verified = real_verified
    if os.environ.get("HW_GUARD_FORCE_VERIFY_FALSE") == "1":
        verified = False
    me = "hw-guard-%s" % args.tag
    action, ok, detail = "", False, ""
    if verified:
        action = "reboot-chord"
        vcc.set_lock_owner(me)
        subprocess.run([VCCTRL_BIN, "lock", "acquire", "--as", me], capture_output=True, text=True)
        try:
            res = vcc.select_boot_profile(None)
        finally:
            subprocess.run([VCCTRL_BIN, "lock", "release", "--as", me], capture_output=True, text=True)
        ok, detail = bool(res), "select_boot_profile(None) -> %s" % (res,)
        if ok:
            ok, raw2 = verify_input()
            detail += " verify_input_after=%s" % ok
    if not ok:
        action = (action + "+" if action else "") + "power-cycle"
        ok, detail2 = power_cycle_and_verify(me)
        detail = (detail + " ; " if detail else "") + detail2
    write_record(args, {"tag": args.tag, "step": args.step, "seen": args.seen,
                        "verify_input_before": str(real_verified).lower(), "action": action,
                        "outcome": "RECOVERED" if ok else "FAILED", "detail": detail,
                        "forced": int(forced or os.environ.get("HW_GUARD_FORCE_VERIFY_FALSE") == "1"),
                        "time_lost_s": int(time.time() - t0),
                        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    if not ok:
        print("hw_guard: recovery FAILED (%s) -- stopping; the target machine needs a person." % detail, file=sys.stderr)
        return 3
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("seq").set_defaults(fn=cmd_seq)
    sub.add_parser("screen", help="print the OCR class of the current screen; passive").set_defaults(fn=cmd_screen)
    hs = sub.add_parser("hold-set", help="operator maintenance window: no power/input before --until")
    hs.add_argument("--until", required=True, help="ISO 8601; no offset = this machine's local time")
    hs.add_argument("--reason", default="")
    hs.set_defaults(fn=cmd_hold_set)
    sub.add_parser("hold-clear").set_defaults(fn=cmd_hold_clear)
    sub.add_parser("hold-check", help="exit 0 if free, 4 if a hold is in force").set_defaults(fn=cmd_hold_check)
    w = sub.add_parser("witness")
    w.add_argument("--since-seq", type=int, required=True)
    w.add_argument("--need", type=int, required=True, help="completed boots required (2 for a --return job)")
    w.add_argument("--timeout", type=int, default=int(os.environ.get(WITNESS_S_ENV, DEFAULT_WITNESS_S)))
    w.add_argument("--step", required=True)
    w.add_argument("--shot")
    w.set_defaults(fn=cmd_witness)
    r = sub.add_parser("recover")
    r.add_argument("--tag", required=True)
    r.add_argument("--step", required=True)
    r.add_argument("--seen", required=True)
    r.add_argument("--record", help="run-record file to append the HW-RECOVERY line to")
    r.add_argument("--state", help="per-run state file enforcing ONE recovery per run")
    r.set_defaults(fn=cmd_recover)
    args = ap.parse_args()
    sys.exit(args.fn(args))


if __name__ == "__main__":
    main()
