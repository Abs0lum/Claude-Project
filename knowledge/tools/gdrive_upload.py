#!/usr/bin/env python3
"""gdrive_upload.py — D-C288: byte-exact uploads from this workspace into Abs0lum's Google Drive through the
'AR Uploader' app (tools/gdrive_oauth.py, scope drive.file). His rules (18:14-18:17 CT 09-29): at least one copy of
every unique version, duplicates unnecessary, files kept whole and exact ("continuity and quality").

How it works:
- Files are uploaded AS-IS (no conversion to Google Docs), so Drive stores the exact bytes. Drive reports an md5 for
  every stored file; each one is compared with the local md5 — a mismatch is an error, never a warning.
- Folders mirror the local tree. drive.file only lets the app see what it created, so the top folder is created by the
  app (it can then be moved anywhere in Drive without losing access).
- Resumable + idempotent: `_logs/gdrive_upload_ledger.json` records local path -> Drive id + md5. A re-run skips
  anything already uploaded with the same md5 and uploads only new or changed files (a changed file is uploaded as a
  NEW file next to the old one — the old version is kept, never overwritten).
- Retries 429 / 5xx with exponential backoff. Nothing secret is printed (tokens stay in memory).
Complexity: O(n) uploads for n files; folder ids are cached, so each folder is created / looked up once.

Usage:
  gdrive_upload.py tree <local_dir> "<top folder name>"   upload a whole folder tree
  gdrive_upload.py file <local_file> <drive_folder_id>    upload one file into a folder the app created
API: upload_tree(local_dir, top_name) -> summary dict"""
import hashlib, json, mimetypes, sys, time, urllib.error, urllib.parse, urllib.request, uuid
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import gdrive_oauth as OA

API = "https://www.googleapis.com/drive/v3/files"
UPLOAD = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart&fields=id,name,md5Checksum,size,parents"
FOLDER = "application/vnd.google-apps.folder"
LEDGER = Path("/home/claude/_logs/gdrive_upload_ledger.json")
TEXT_TYPES = {".md": "text/markdown", ".py": "text/x-python", ".js": "text/javascript", ".mjs": "text/javascript",
              ".json": "application/json", ".txt": "text/plain", ".csv": "text/csv", ".html": "text/html", ".sh": "text/x-shellscript"}


class Drive:
    def __init__(self):
        self._token, self._t = None, 0.0
        self.folders = {}

    def _auth(self):
        if not self._token or time.time() - self._t > 2400:        # access tokens live 3600 s; refresh at 40 min
            self._token, self._t = OA.access_token(), time.time()
        return {"Authorization": "Bearer " + self._token}

    def _call(self, req_factory, tries=6):
        delay = 1.0
        for attempt in range(tries):
            req = req_factory()
            for k, v in self._auth().items(): req.add_header(k, v)
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    return json.load(r)
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", "replace")[:300]
                if e.code in (429, 500, 502, 503, 504) and attempt < tries - 1:
                    time.sleep(delay); delay *= 2; continue
                raise RuntimeError(f"Drive API HTTP {e.code}: {body}")
            except (urllib.error.URLError, TimeoutError) as e:
                if attempt < tries - 1: time.sleep(delay); delay *= 2; continue
                raise RuntimeError(f"Drive API network error: {e}")

    def find_folder(self, name, parent):
        q = f"name = '{name.replace(chr(39), chr(92) + chr(39))}' and mimeType = '{FOLDER}' and trashed = false" + \
            (f" and '{parent}' in parents" if parent else "")
        url = API + "?" + urllib.parse.urlencode({"q": q, "fields": "files(id,name)", "spaces": "drive"})
        files = self._call(lambda: urllib.request.Request(url))["files"]
        return files[0]["id"] if files else None

    def folder(self, name, parent=None):
        key = (parent, name)
        if key not in self.folders:
            fid = self.find_folder(name, parent)
            if not fid:
                meta = {"name": name, "mimeType": FOLDER, **({"parents": [parent]} if parent else {})}
                body = json.dumps(meta).encode()
                fid = self._call(lambda: urllib.request.Request(API + "?fields=id", data=body, method="POST",
                                                                headers={"Content-Type": "application/json"}))["id"]
            self.folders[key] = fid
        return self.folders[key]

    def upload(self, local, parent, name=None):
        data = Path(local).read_bytes()
        ctype = TEXT_TYPES.get(Path(local).suffix.lower()) or mimetypes.guess_type(str(local))[0] or "application/octet-stream"
        boundary = "ar-" + uuid.uuid4().hex
        meta = json.dumps({"name": name or Path(local).name, "parents": [parent]}).encode()
        body = (f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n").encode() + meta + \
               (f"\r\n--{boundary}\r\nContent-Type: {ctype}\r\n\r\n").encode() + data + f"\r\n--{boundary}--\r\n".encode()
        r = self._call(lambda: urllib.request.Request(UPLOAD, data=body, method="POST",
                                                      headers={"Content-Type": f"multipart/related; boundary={boundary}"}))
        local_md5 = hashlib.md5(data).hexdigest()
        if r.get("md5Checksum") != local_md5 or int(r.get("size", -1)) != len(data):
            raise RuntimeError(f"STORED BYTES DIFFER for {local}: drive md5 {r.get('md5Checksum')} size {r.get('size')} vs local {local_md5} {len(data)}")
        return {"id": r["id"], "md5": local_md5, "bytes": len(data)}


def _ledger():
    return json.load(open(LEDGER)) if LEDGER.exists() else {}


def upload_tree(local_dir, top_name):
    root = Path(local_dir); d = Drive(); led = _ledger()
    top = d.folder(top_name)
    done = skipped = 0; nbytes = 0; t0 = time.time()
    files = sorted(p for p in root.rglob("*") if p.is_file())
    for i, p in enumerate(files, 1):
        rel = p.relative_to(root).as_posix(); key = f"{top_name}/{rel}"
        md5 = hashlib.md5(p.read_bytes()).hexdigest()
        if led.get(key, {}).get("md5") == md5: skipped += 1; continue
        parent = top
        for part in rel.split("/")[:-1]: parent = d.folder(part, parent)
        r = d.upload(p, parent)
        prev = led.get(key)
        if prev: led.setdefault(key + " (earlier versions)", []).append(prev)   # keep every version's record
        led[key] = {**r, "uploaded": time.strftime("%Y-%m-%dT%H:%M:%S")}
        done += 1; nbytes += r["bytes"]
        if done % 25 == 0:
            json.dump(led, open(LEDGER, "w"), indent=0)
            print(f"  {i}/{len(files)} … {done} uploaded, {skipped} already there", flush=True)
    json.dump(led, open(LEDGER, "w"), indent=0)
    return {"top_folder_id": top, "files": len(files), "uploaded": done, "already_there": skipped, "bytes": nbytes,
            "md5_verified": done, "seconds": round(time.time() - t0, 1)}


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "tree":
        print(json.dumps(upload_tree(sys.argv[2], sys.argv[3])))
    elif len(sys.argv) >= 4 and sys.argv[1] == "file":
        print(json.dumps(Drive().upload(sys.argv[2], sys.argv[3])))
    else:
        raise SystemExit(__doc__)
