import json, re, sys

path = "/tmp/claude-1001/-home-claude-git-sdl-dos-ports/b7e5d73b-64bc-4e7b-9750-d225ac8a37a8/scratchpad/s5wb2_audio_poll.jsonl"
raw = open(path).read()
# fix bc's leading-dot decimals (".001171267" -> "0.001171267") so json can parse
raw = re.sub(r'(?<=[:\s])\.(\d)', r'0.\1', raw)

dec = json.JSONDecoder()
records = []
i = 0
n = len(raw)
while i < n:
    while i < n and raw[i] in ' \t\r\n':
        i += 1
    if i >= n:
        break
    try:
        obj, end = dec.raw_decode(raw, i)
    except json.JSONDecodeError:
        # skip to next '{' at start of a record (a line starting with {"t":)
        nxt = raw.find('{"t"', i + 1)
        if nxt == -1:
            break
        i = nxt
        continue
    records.append(obj)
    i = end

print(f"parsed {len(records)} records")

BAND_HZ = [100, 200, 400, 800, 1600, 3200, 6400, 12800]

rows = []
for r in records:
    t = r.get("t")
    lvl = r.get("level", {})
    spec = r.get("spectrum", {})
    mean_db = lvl.get("mean_db")
    active = spec.get("active_bands")
    band_db = spec.get("band_db")
    rows.append((t, mean_db, active, band_db))

rows.sort(key=lambda x: x[0] if x[0] is not None else -1)

print(f"{'t':>8} {'mean_db':>8} {'active':>6}  band_db")
for t, mean_db, active, band_db in rows:
    bd = " ".join(f"{b:6.1f}" for b in band_db) if band_db else "?"
    marker = "  <<<" if (active and active > 0) else ""
    print(f"{t:8.1f} {mean_db:8.2f} {active!s:>6}  {bd}{marker}")

# summarize windows where active_bands > 0
print("\n=== windows with active_bands > 0 ===")
in_window = False
for t, mean_db, active, band_db in rows:
    is_active = bool(active and active > 0)
    if is_active and not in_window:
        print(f"-- window start t={t:.1f}")
        in_window = True
    if not is_active and in_window:
        print(f"-- window end   t={t:.1f}")
        in_window = False
    if is_active:
        top_band = max(range(len(band_db)), key=lambda i: band_db[i])
        print(f"   t={t:7.1f} mean_db={mean_db:7.2f} active={active} top_band=idx{top_band}({BAND_HZ[top_band]}Hz) band_db={band_db}")
