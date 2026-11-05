#!/usr/bin/env python3
"""audio-rec.py -- record vcctrl's live Ogg Opus audio side-stream to files for a whole cell.

  audio-rec.py OUT_PREFIX SECONDS      (stop early with SIGTERM)

Writes OUT_PREFIX-segNN.ogg, one per websocket connection: each connection starts with the
stream's own header pages (the daemon replays them), so every segment is a complete Ogg file.
A dropped connection is reconnected at once into the next segment, and every connect/drop is
logged with its wall time to OUT_PREFIX-segments.log, so a gap in the recording is visible
rather than silently spliced. Keepalive pings are off: the daemon's websocket does not answer
them (the first 8.3 cell lost the stream after 40 s to a ping timeout).
"""
import asyncio
import re
import signal
import sys
import time

import websockets

import os


def ws_url():
    """The daemon's audio websocket, from the rig's own config -- no hostname in this repo.
    VCCTRL_WEB (env) first, then vcctrl's control.web (vcctrl.yaml) through vcctrl_common, found
    beside VCCTRL_BIN (default ../vcctrl/bin, as run-hw.sh). The https:// web URL becomes wss://."""
    web = os.environ.get("VCCTRL_WEB", "")
    if not web:
        here = os.path.dirname(os.path.abspath(__file__))
        vbin = os.environ.get("VCCTRL_BIN") or os.path.join(here, "..", "..", "..", "vcctrl", "bin", "vcctrl")
        sys.path.insert(0, os.path.dirname(os.path.abspath(vbin)))
        try:
            import vcctrl_common
            web = vcctrl_common.VCCTRL_WEB
        except Exception as e:
            sys.exit("audio-rec.py: no VCCTRL_WEB and vcctrl_common not importable (%s)" % e)
    if not web:
        sys.exit("audio-rec.py: no vcctrl web URL (set VCCTRL_WEB, or control.web in vcctrl.yaml)")
    return re.sub(r"^http", "ws", web.rstrip("/")) + "/wsaudio?codec=opus"


URL = ws_url()


async def main(prefix, secs):
    stop = asyncio.Event()
    asyncio.get_running_loop().add_signal_handler(signal.SIGTERM, stop.set)
    t0 = time.time()
    seg = 0
    with open(prefix + "-segments.log", "a") as log:
        while not stop.is_set() and time.time() - t0 < secs:
            seg += 1
            out = "%s-seg%02d.ogg" % (prefix, seg)
            pages = 0
            try:
                async with websockets.connect(URL, max_size=None, open_timeout=20,
                                              ping_interval=None) as ws:
                    log.write("%s connect %s\n" % (time.strftime("%H:%M:%S"), out)); log.flush()
                    with open(out, "wb") as f:
                        while not stop.is_set() and time.time() - t0 < secs:
                            try:
                                msg = await asyncio.wait_for(ws.recv(), timeout=1.0)
                            except asyncio.TimeoutError:
                                continue
                            if isinstance(msg, (bytes, bytearray)):
                                f.write(msg); pages += 1
            except Exception as exc:  # noqa: BLE001 -- any drop: log it, reconnect
                log.write("%s drop %s pages=%d %s\n" % (time.strftime("%H:%M:%S"), out, pages,
                                                         type(exc).__name__)); log.flush()
                await asyncio.sleep(0.5)
                continue
            log.write("%s end %s pages=%d\n" % (time.strftime("%H:%M:%S"), out, pages)); log.flush()
    print("segments=%d seconds=%.1f" % (seg, time.time() - t0))


asyncio.run(main(sys.argv[1], float(sys.argv[2])))
