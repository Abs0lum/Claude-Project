#!/usr/bin/env python3
"""r3_fetch_shots.py — download the R3 screenshots listed in _intake/r3-shots/manifest.json from the Drive (byte-size verified)."""
import json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "tools")
import remote_zip

OUT = "_intake/r3-shots"


def fetch(item):
    stem, fid, size = item
    path = os.path.join(OUT, f"{stem}.png")
    if os.path.exists(path) and os.path.getsize(path) == size: return stem, "cached"
    last = ""
    for attempt in range(3):
        try:
            for url in (f"https://drive.google.com/uc?export=download&id={fid}", None):
                url = url or remote_zip.drive_url(fid)
                with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=120) as r:
                    data = r.read()
                if len(data) == size and data.startswith(b"\x89PNG"):
                    open(path, "wb").write(data); return stem, "ok"
                last = f"size {len(data)} != {size}"
        except Exception as e:
            last = repr(e)[:120]
        time.sleep(2 + 3 * attempt)
    return stem, "FAIL " + last


if __name__ == "__main__":
    items = json.load(open(os.path.join(OUT, "manifest.json")))
    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(fetch, items))
    bad = [r for r in res if not r[1] in ("ok", "cached")]
    print(f"{len(res) - len(bad)}/{len(res)} downloaded, size-verified", bad)
