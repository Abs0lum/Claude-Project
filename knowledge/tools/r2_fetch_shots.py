#!/usr/bin/env python3
"""r2_fetch_shots.py — download every ROUND-2 screenshot in _intake/r2-shots/manifest.json (stem, drive id, size) into
_intake/r2-shots/<stem>.png, byte-size verified against the Drive listing; parallel; re-runnable (present + right size = skipped)."""
import json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "/home/claude/tools")
import remote_zip
OUT = "/home/claude/_intake/r2-shots"
M = json.load(open(os.path.join(OUT, "manifest.json")))

def fetch(item):
    stem, fid, size = item
    path = os.path.join(OUT, f"{stem}.png")
    if os.path.exists(path) and os.path.getsize(path) == size: return stem, "cached", size
    for attempt in range(3):
        try:
            url = f"https://drive.google.com/uc?export=download&id={fid}"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=180) as r: data = r.read()
            if len(data) != size or not data.startswith(b"\x89PNG"):
                url = remote_zip.drive_url(fid)
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=180) as r: data = r.read()
            if len(data) == size and data.startswith(b"\x89PNG"):
                open(path, "wb").write(data); return stem, "ok", len(data)
            last = f"size {len(data)} != {size}"
        except Exception as e: last = str(e)[:80]
        time.sleep(2 + attempt * 3)
    return stem, "FAILED " + last, 0

t0 = time.time()
with ThreadPoolExecutor(max_workers=6) as ex: res = list(ex.map(fetch, M))
ok = [r for r in res if r[1] in ("ok", "cached")]; bad = [r for r in res if r[1].startswith("FAILED")]
print(f"{len(ok)}/{len(M)} present ({sum(r[2] for r in ok)/1e6:.0f} MB) in {time.time()-t0:.0f}s; failed: {bad[:10]}")
