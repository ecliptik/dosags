#!/usr/bin/env bash
# check-dist.sh -- verify a dist zip against the repo's licence records.
#
#   scripts/check-dist.sh <zip> [--repo-url URL] [--release]
#
# FAILS (exit 1) when:
#   - the zip's file list differs from THIRD-PARTY.md's dist-files table
#     (either direction), or a name is not upper-case DOS 8.3;
#   - a table row names a LICENSE-REVIEW.md section that does not exist;
#   - anything looks like game data (.ags .vox .crm .tra .dta .exe other
#     than AGS.EXE / CWSDPMI.EXE);
#   - AGS.EXE is not byte-identical to build/ags-release/ags.exe, or
#     MANIFEST.TXT's sha256 lines do not verify;
#   - a text file is not ASCII with CRLF line ends (CWSDPMI.DOC and FTL.TXT
#     are checked for CRLF only: they ship upstream's text unaltered, and
#     FTL.txt has a Latin-1 copyright sign);
#   - README.TXT lacks a notice a licence requires (FreeType disclaimer,
#     DJGPP source pointer, CWSDPMI source notice, Modified Version note);
#   - any file names a tailnet host (*.ts.net other than the
#     forgejo.example.ts.net placeholder).
# With --release it also fails when README.TXT has no public source URL
# (Artistic 2.0 s.4/6, DJGPP and CWSDPMI all need one); without it, that is
# printed as NOT RELEASABLE and the check still passes.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ZIP=""; RELEASE=0; REPO_URL=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --release)  RELEASE=1; shift ;;
        --repo-url) REPO_URL="$2"; shift 2 ;;
        -*) echo "usage: $0 <zip> [--repo-url URL] [--release]" >&2; exit 2 ;;
        *)  ZIP="$1"; shift ;;
    esac
done
[[ -f "$ZIP" ]] || { echo "check-dist: no zip '$ZIP'" >&2; exit 2; }
exec python3 -I - "$ROOT" "$ZIP" "$RELEASE" "$REPO_URL" <<'PY'
import hashlib, os, re, sys, zipfile
root, zpath, release, repo_url = sys.argv[1], sys.argv[2], sys.argv[3] == "1", sys.argv[4]
fails = []
def fail(msg): fails.append(msg)

tp = open(os.path.join(root, "THIRD-PARTY.md"), encoding="ascii").read()
m = re.search(r"<!-- dist-files:begin -->(.*?)<!-- dist-files:end -->", tp, re.S)
if not m:
    sys.exit("check-dist: THIRD-PARTY.md has no dist-files table")
rows = {}
for line in m.group(1).splitlines():
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) < 4 or not cells[0].startswith("`"):
        continue
    rows[cells[0].strip("`")] = cells
lr = open(os.path.join(root, "LICENSE-REVIEW.md"), encoding="ascii").read()
headings = [h.strip() for h in re.findall(r"^## (.+)$", lr, re.M)]
for name, cells in rows.items():
    sec = cells[3].strip("`")
    if not any(h.startswith(sec) for h in headings):
        fail("THIRD-PARTY row %s names LICENSE-REVIEW.md section '%s', which does not exist" % (name, sec))

z = zipfile.ZipFile(zpath)
names = [i.filename for i in z.infolist()]
if any("/" in n for n in names):
    fail("zip has subdirectories: %s" % [n for n in names if "/" in n])
for n in sorted(set(names) - set(rows)):
    fail("in the zip but not in THIRD-PARTY.md's dist-files table: %s" % n)
for n in sorted(set(rows) - set(names)):
    fail("in THIRD-PARTY.md's dist-files table but not in the zip: %s" % n)
for n in names:
    if not re.fullmatch(r"[A-Z0-9_-]{1,8}(\.[A-Z0-9_]{1,3})?", n):
        fail("not an upper-case 8.3 name: %s" % n)
    ext = n.rsplit(".", 1)[-1]
    if ext in ("AGS", "VOX", "CRM", "TRA", "DTA") or (ext == "EXE" and n not in ("AGS.EXE", "CWSDPMI.EXE")):
        fail("looks like game data: %s" % n)

data = {n: z.read(n) for n in names}
rel = open(os.path.join(root, "build/ags-release/ags.exe"), "rb").read()
if data.get("AGS.EXE") != rel:
    fail("AGS.EXE is not byte-identical to build/ags-release/ags.exe")
man = data.get("MANIFEST.TXT", b"").decode("ascii", "replace")
listed = {}
for line in man.splitlines():
    mm = re.fullmatch(r"([0-9a-f]{64})  (\S+)", line.strip())
    if mm:
        listed[mm.group(2)] = mm.group(1)
for n in names:
    if n == "MANIFEST.TXT":
        continue
    if listed.get(n) != hashlib.sha256(data[n]).hexdigest():
        fail("MANIFEST.TXT sha256 missing or wrong for %s" % n)

for n in names:
    if not n.endswith((".TXT", ".DOC")):
        continue
    b = data[n]
    if b.replace(b"\r\n", b"").count(b"\n"):
        fail("%s has LF-only line ends" % n)
    if n not in ("CWSDPMI.DOC", "FTL.TXT") and any(c > 127 for c in b):
        fail("%s is not ASCII" % n)

readme = data.get("README.TXT", b"").decode("ascii", "replace")
for need, why in [
    ("based in part on the work of the FreeType Team", "FreeType Project License s.2 (binary redistribution)"),
    ("https://www.delorie.com/djgpp/", "DJGPP copying.dj (how to obtain DJGPP)"),
    ("https://sandmann.dotster.com/cwsdpmi/", "CWSDPMI.DOC (site for the source)"),
    ("right to receive the source code", "CWSDPMI.DOC (notice to users)"),
    ("Modified Version", "Artistic License 2.0 s.4 (documented as differing)"),
]:
    if need not in readme.replace("\r\n", " ").replace("\n", " ").replace("  ", " "):
        fail("README.TXT lacks '%s' -- %s" % (need, why))

for n, b in data.items():
    for host in set(re.findall(rb"[A-Za-z0-9-]+\.[A-Za-z0-9-]+\.ts\.net", b)):
        if host != b"forgejo.example.ts.net":
            fail("%s names a tailnet host: %s" % (n, host.decode("ascii", "replace")))

published = "not yet published" not in readme
if release and not published:
    fail("--release: README.TXT has no public source URL")
if repo_url and repo_url not in readme:
    fail("README.TXT does not carry --repo-url %s" % repo_url)

print("check-dist: %s -- %d files, %d bytes" % (os.path.basename(zpath), len(names), os.path.getsize(zpath)))
for f in fails:
    print("FAIL: " + f)
if not published:
    print("NOT RELEASABLE: no public source URL in README.TXT (pass --repo-url to make-dist)")
print("check-dist: %s" % ("FAIL" if fails else "PASS"))
sys.exit(1 if fails else 0)
PY
