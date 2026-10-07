#!/usr/bin/env python3
"""fetch_shots.py — download a witness round's screenshots from his Drive folder (public-link files) into a folder,
byte-size + PNG-signature verified, md5 recorded; files already present with the right size are skipped.
Usage: fetch_shots.py <dir-with-manifest.json>   (manifest = [[stem, drive_id, size, original_name], ...])"""
import hashlib, json, os, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, "/home/claude/tools")
import remote_zip


def fetch(out, item):
    stem, fid, size, _ = item
    path = os.path.join(out, f"{stem}.png")
    if os.path.exists(path) and os.path.getsize(path) == size:
        return stem, "cached", hashlib.md5(open(path, "rb").read()).hexdigest()
    last = ""
    for attempt in range(3):
        try:
            data = b""
            for url in (f"https://drive.google.com/uc?export=download&id={fid}", None):
                url = url or remote_zip.drive_url(fid)
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=120) as r: data = r.read()
                if len(data) == size and data.startswith(b"\x89PNG"): break
            if len(data) == size and data.startswith(b"\x89PNG"):
                open(path, "wb").write(data)
                return stem, "ok", hashlib.md5(data).hexdigest()
            last = f"size {len(data)} != {size}"
        except Exception as e:
            last = repr(e)[:80]
        time.sleep(2 + 3 * attempt)
    return stem, "FAIL " + last, ""


def main(out):
    items = json.load(open(os.path.join(out, "manifest.json")))
    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(lambda it: fetch(out, it), items))
    json.dump(res, open(os.path.join(out, "fetch_result.json"), "w"), indent=0)
    bad = [r for r in res if r[1].startswith("FAIL")]
    print(f"{len(res) - len(bad)}/{len(res)} downloaded + verified; failures {bad}")


if __name__ == "__main__":
    main(sys.argv[1])
