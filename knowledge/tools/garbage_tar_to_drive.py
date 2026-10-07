#!/usr/bin/env python3
"""garbage_tar_to_drive.py — his 20:23 H2 = b: each _garbage/<dir> goes to Drive as ONE uncompressed .tar, streamed
straight from disk to a Drive resumable upload (no local tar copy is written — the workspace is too tight for one).

Proof chain before any local removal:
  1. while streaming, the md5 + byte count of the exact tar bytes sent are computed;
  2. Drive's stored md5Checksum + size must equal them (else: error, nothing removed);
  3. a per-file manifest (relative path, size, md5 of every file read into the tar) is uploaded next to the tar as
     <dir>.manifest.json and also checked by Drive md5;
  4. the manifest file count must equal the local file count walked at the start.
Only then is the local folder removed. Drive folder: "AR-Garbage-Archives" (created by the app, drive.file scope).
Ledger: _logs/garbage_tar_ledger.json. Complexity: O(total bytes), one pass over each file.
Usage: garbage_tar_to_drive.py <dir> [<dir> ...]   (names inside /home/claude/_garbage)"""
import hashlib
import io
import os
import json
import shutil
import sys
import tarfile
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import gdrive_upload as GU  # noqa: E402

ROOT = Path("/home/claude")
GARB = ROOT / "_garbage"
LEDGER = ROOT / "_logs/garbage_tar_ledger.json"
CHUNK = 32 * 256 * 1024                      # 8 MiB, a multiple of 256 KiB as Drive requires
START = "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable&fields=id,name,md5Checksum,size"


class ResumableSink(io.RawIOBase):
    """File-like sink for tarfile: buffers bytes, sends full 8 MiB chunks to one Drive resumable session."""

    def __init__(self, drive, name, parent):
        super().__init__()
        self.drive, self.buf, self.sent = drive, bytearray(), 0
        self.md5 = hashlib.md5()
        meta = json.dumps({"name": name, "parents": [parent]}).encode()
        req = urllib.request.Request(START, data=meta, method="POST",
                                     headers={"Content-Type": "application/json; charset=UTF-8",
                                              "X-Upload-Content-Type": "application/x-tar", **drive._auth()})
        with urllib.request.urlopen(req, timeout=120) as r:
            self.session = r.headers["Location"]
        self.result = None

    def writable(self):
        return True

    def write(self, b):
        self.buf += b
        self.md5.update(b)
        while len(self.buf) >= CHUNK:
            self._put(bytes(self.buf[:CHUNK]), final=False)
            del self.buf[:CHUNK]
        return len(b)

    def _put(self, data, final):
        total = str(self.sent + len(data)) if final else "*"
        rng = f"bytes {self.sent}-{self.sent + len(data) - 1}/{total}" if data else f"bytes */{total}"
        delay = 2.0
        for attempt in range(6):
            req = urllib.request.Request(self.session, data=data, method="PUT",
                                         headers={"Content-Range": rng, **self.drive._auth()})
            try:
                with urllib.request.urlopen(req, timeout=300) as r:
                    self.result = json.load(r)          # 200/201 = upload complete
                break
            except urllib.error.HTTPError as e:
                if e.code == 308:                       # chunk accepted, upload continues
                    break
                if e.code in (429, 500, 502, 503, 504) and attempt < 5:
                    time.sleep(delay); delay *= 2; continue
                raise RuntimeError(f"chunk upload HTTP {e.code}: {e.read()[:200]!r}")
            except (urllib.error.URLError, TimeoutError):
                if attempt < 5:
                    time.sleep(delay); delay *= 2; continue
                raise
        self.sent += len(data)

    def finish(self):
        self._put(bytes(self.buf), final=True)
        self.buf.clear()
        return self.result


class HashingReader:
    """Wraps a file so the tar member's md5 is computed from the same bytes that go into the tar."""

    def __init__(self, f):
        self.f, self.md5 = f, hashlib.md5()

    def read(self, n=-1):
        b = self.f.read(n)
        self.md5.update(b)
        return b


def ship(name, drive, top, led):
    src = GARB / name
    files = sorted(p for p in src.rglob("*") if p.is_file() and not p.is_symlink())
    links = [p for p in src.rglob("*") if p.is_symlink()]
    manifest = []
    sink = ResumableSink(drive, f"{name}.tar", top)
    with tarfile.open(fileobj=sink, mode="w|", format=tarfile.PAX_FORMAT) as tar:
        for p in files:
            rel = p.relative_to(GARB).as_posix()
            info = tar.gettarinfo(str(p), arcname=rel)
            with open(p, "rb") as fh:
                hr = HashingReader(fh)
                tar.addfile(info, hr)
            manifest.append([rel, info.size, hr.md5.hexdigest()])
        for p in links:
            tar.add(str(p), arcname=p.relative_to(GARB).as_posix(), recursive=False)
    r = sink.finish()
    local_md5, local_size = sink.md5.hexdigest(), sink.sent
    if not r or r.get("md5Checksum") != local_md5 or int(r.get("size", -1)) != local_size:
        raise RuntimeError(f"{name}: Drive tar md5/size {r and r.get('md5Checksum')}/{r and r.get('size')} "
                           f"!= sent {local_md5}/{local_size} — nothing removed")
    if len(manifest) != len(files):
        raise RuntimeError(f"{name}: manifest {len(manifest)} files != local {len(files)} — nothing removed")
    mpath = Path(os.environ.get("GARBAGE_MANIFEST_DIR", str(ROOT / "_logs"))) / f"garbage-{name}.manifest.json"   # 10-05: /dev/shm when the disk is full
    mpath.write_text(json.dumps({"dir": name, "tar_md5": local_md5, "tar_bytes": local_size, "files": manifest,
                                 "symlinks": [p.relative_to(GARB).as_posix() for p in links]}, indent=0))
    mr = drive.upload(mpath, top, name=f"{name}.manifest.json")      # raises on md5 mismatch
    led[name] = {"tar_id": r["id"], "tar_md5": local_md5, "tar_bytes": local_size, "files": len(manifest),
                 "manifest_id": mr["id"], "verified": time.strftime("%Y-%m-%dT%H:%M:%S")}
    json.dump(led, open(LEDGER, "w"), indent=1)
    shutil.rmtree(src)
    print(f"{name}: {len(manifest)} files, tar {local_size / 2**20:.1f} MiB md5 {local_md5[:8]} == Drive -> local removed",
          flush=True)


def main(names):
    drive = GU.Drive()
    top = drive.folder("AR-Garbage-Archives")
    led = json.load(open(LEDGER)) if LEDGER.exists() else {}
    for n in names:
        if n in led:
            print(n, "already archived", led[n]["tar_md5"][:8]); continue
        t0 = time.time()
        ship(n, drive, top, led)
        print(f"  {time.time() - t0:.0f} s", flush=True)
    print("disk free MiB:", shutil.disk_usage(ROOT).free // 2**20)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    main(sys.argv[1:])
