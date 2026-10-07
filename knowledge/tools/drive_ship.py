#!/usr/bin/env python3
"""drive_ship.py — deliver finished packs straight into Abs0lum's Google Drive (his 12:11 CT 10-04 ask: a folder named
"ClaudeUploads" instead of the gofile page). Uses the 'AR Uploader' app (tools/gdrive_oauth.py, scope drive.file) through
tools/gdrive_upload.Drive for the token and the folder lookup; nothing secret is ever printed.

Why a separate tool: gdrive_upload.Drive.upload sends one multipart request, which Drive limits to 5 MB; packs run to
~250 MB, so this tool uses a RESUMABLE session, streamed from disk in 8 MiB chunks (no whole-file copy in memory).

Gate per file (any failure = error, never a warning):
  1. the md5 + byte count of the exact bytes sent are computed while streaming;
  2. the upload's answer AND a fresh metadata read (files.get) must both report md5Checksum + size equal to them.
Idempotent: _logs/drive_ship_ledger.json maps "<folder>/<name>" -> {id, md5, bytes, uploaded}. A file already there with
the same md5 is skipped; a changed file is uploaded as a NEW file beside the old one (nothing is overwritten or deleted).
Complexity: O(total bytes) — one read pass per file; folder id looked up / created once.
Usage: drive_ship.py [--folder NAME[/SUB]] FILE [FILE ...]   (default folder: ClaudeUploads, at the top of My Drive)
       drive_ship.py --list [--folder NAME]                   (what the app has put in that folder: name, size, md5)"""
import hashlib
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import gdrive_upload as GU  # noqa: E402

LEDGER = Path("/home/claude/_logs/drive_ship_ledger.json")
CHUNK = 32 * 256 * 1024                      # 8 MiB — a multiple of 256 KiB, as Drive requires for non-final chunks
START = "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable&fields=id,name,md5Checksum,size"
FIELDS = "id,name,md5Checksum,size,parents,createdTime"


def _ledger():
    return json.loads(LEDGER.read_text()) if LEDGER.exists() else {}


def _start_session(drive, name, parent, total):
    """Open one resumable session; returns the session URL (Drive's Location header)."""
    meta = json.dumps({"name": name, "parents": [parent]}).encode()
    req = urllib.request.Request(START, data=meta, method="POST",
                                 headers={"Content-Type": "application/json; charset=UTF-8",
                                          "X-Upload-Content-Type": "application/octet-stream",
                                          "X-Upload-Content-Length": str(total), **drive._auth()})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.headers["Location"]


def _put_chunk(drive, session, data, start, total, tries=6):
    """PUT bytes [start, start+len) of total. Returns the final JSON on the last chunk, None while incomplete (308)."""
    end = start + len(data) - 1
    delay = 1.0
    for attempt in range(tries):
        req = urllib.request.Request(session, data=data, method="PUT",
                                     headers={"Content-Length": str(len(data)),
                                              "Content-Range": f"bytes {start}-{end}/{total}", **drive._auth()})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.load(r)                                   # 200/201: the upload is complete
        except urllib.error.HTTPError as e:
            if e.code == 308:                                         # Resume Incomplete: Drive holds bytes up to Range
                rng = e.headers.get("Range")                          # e.g. "bytes=0-8388607"
                got = int(rng.split("-")[1]) + 1 if rng else 0
                if got != end + 1:
                    raise RuntimeError(f"Drive kept {got} bytes, expected {end + 1} (chunk not fully stored)")
                return None
            if e.code in (429, 500, 502, 503, 504) and attempt < tries - 1:
                time.sleep(delay); delay *= 2; continue
            raise RuntimeError(f"Drive upload HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:300]}")
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < tries - 1:
                time.sleep(delay); delay *= 2; continue
            raise RuntimeError(f"Drive upload network error: {e}")
    raise RuntimeError("Drive upload: retries exhausted")


def _meta(drive, file_id):
    url = f"{GU.API}/{file_id}?" + urllib.parse.urlencode({"fields": FIELDS})
    return drive._call(lambda: urllib.request.Request(url))


def ship_file(drive, path, folder_id, folder_name, led):
    """Stream one file into the folder and prove Drive stores exactly its bytes. Returns a record dict."""
    p = Path(path)
    total = p.stat().st_size
    key = f"{folder_name}/{p.name}"
    local_md5 = hashlib.md5()
    with p.open("rb") as fh:                                          # md5 first: decides the idempotent skip
        for block in iter(lambda: fh.read(CHUNK), b""):
            local_md5.update(block)
    md5 = local_md5.hexdigest()
    if led.get(key, {}).get("md5") == md5:
        return {**led[key], "name": p.name, "skipped": True}
    session = _start_session(drive, p.name, folder_id, total)
    sent_md5, sent, result, t0 = hashlib.md5(), 0, None, time.time()
    with p.open("rb") as fh:
        while sent < total:
            data = fh.read(CHUNK)
            sent_md5.update(data)
            result = _put_chunk(drive, session, data, sent, total)
            sent += len(data)
            if total > 4 * CHUNK and (sent // CHUNK) % 6 == 0:
                print(f"    {p.name}: {sent / 1e6:.0f} / {total / 1e6:.0f} MB", flush=True)
    if result is None:
        raise RuntimeError(f"{p.name}: the last chunk was not acknowledged as complete")
    if sent_md5.hexdigest() != md5 or sent != total:
        raise RuntimeError(f"{p.name}: the bytes read while sending differ from the file (changed during upload?)")
    stored = _meta(drive, result["id"])                               # a fresh read of what Drive holds
    for label, r in (("upload answer", result), ("metadata read", stored)):
        if r.get("md5Checksum") != md5 or int(r.get("size", -1)) != total:
            raise RuntimeError(f"STORED BYTES DIFFER ({label}) for {p.name}: drive md5 {r.get('md5Checksum')} "
                               f"size {r.get('size')} vs local {md5} {total}")
    rec = {"id": result["id"], "md5": md5, "bytes": total, "uploaded": time.strftime("%Y-%m-%dT%H:%M:%S"),
           "seconds": round(time.time() - t0, 1)}
    prev = led.get(key)
    if prev:
        led.setdefault(key + " (earlier versions)", []).append(prev)
    led[key] = rec
    LEDGER.write_text(json.dumps(led, indent=1))
    return {**rec, "name": p.name, "skipped": False}


def list_folder(drive, folder_id):
    q = f"'{folder_id}' in parents and trashed = false"
    url = GU.API + "?" + urllib.parse.urlencode({"q": q, "fields": "files(id,name,size,md5Checksum,createdTime)",
                                                 "orderBy": "createdTime desc", "pageSize": 200, "spaces": "drive"})
    return drive._call(lambda: urllib.request.Request(url))["files"]


def main():
    args, folder_name, listing = sys.argv[1:], "ClaudeUploads", False
    while args and args[0].startswith("--"):
        if args[0] == "--folder":
            folder_name, args = args[1], args[2:]
        elif args[0] == "--list":
            listing, args = True, args[1:]
        else:
            raise SystemExit(f"unknown flag {args[0]}\n{__doc__}")
    if not listing and not args:
        raise SystemExit(__doc__)
    drive = GU.Drive()
    folder_id = None                                                  # "A/B" = folder B inside A, from the top of My Drive
    for part in folder_name.split("/"):
        folder_id = drive.folder(part, folder_id)                     # looked up, or created by the app if missing
    if listing:
        for f in list_folder(drive, folder_id):
            print(f"{f['name']:<60} {int(f.get('size', 0)):>12,} B  md5 {f.get('md5Checksum')}  {f.get('createdTime')}")
        return
    led, ok = _ledger(), True
    print(f"folder {folder_name} ({folder_id})")
    for path in args:
        try:
            r = ship_file(drive, path, folder_id, folder_name, led)
            state = "already there" if r["skipped"] else f"uploaded in {r['seconds']} s"
            print(f"PASS {r['name']}  {r['bytes']:,} B  md5 {r['md5']}  (Drive md5 == local, size == local; {state})")
        except Exception as e:  # noqa: BLE001
            ok = False
            print(f"FAIL {Path(path).name}: {e}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
