#!/usr/bin/env python3
"""garbage_restore.py — pull selected files back out of a Drive garbage archive (.tar written by garbage_tar_to_drive.py)
WITHOUT downloading the whole tar to disk: the tar is streamed from Drive (OAuth, drive.file scope: the app created it)
through tarfile's stream mode, only the wanted members are written, and the stream stops as soon as all were found.
Every restored file is checked against the archive manifest's md5 (the manifest is what was verified at archive time).

Usage: garbage_restore.py <archive-dir-name> <out-dir> <member-path-substring> [...]
       e.g. garbage_restore.py 20261002-214903 _restore/rp04-150 _build/rp04-150/textures/blocks/pw_mitre_
Complexity: O(bytes streamed) — worst case the whole tar, one pass, no local copy of the tar."""
import hashlib
import json
import sys
import tarfile
import urllib.request
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import gdrive_oauth  # noqa: E402

LEDGER = Path("/home/claude/_logs/garbage_tar_ledger.json")


def manifest_for(archive):
    """{member path -> (size, md5)} from the local copy of the archive manifest."""
    data = json.loads(Path(f"/home/claude/_logs/garbage-{archive}.manifest.json").read_text())
    return {path: (size, md5) for path, size, md5 in data["files"]}


def restore(archive, out_dir, wanted_substrings):
    entry = json.loads(LEDGER.read_text())[archive]
    manifest = manifest_for(archive)
    targets = {p for p in manifest if any(s in p for s in wanted_substrings)}
    if not targets:
        raise SystemExit("no manifest member matches")
    token = gdrive_oauth.access_token()
    req = urllib.request.Request(f"https://www.googleapis.com/drive/v3/files/{entry['tar_id']}?alt=media",
                                 headers={"Authorization": f"Bearer {token}"})
    out = Path(out_dir)
    found, bad = 0, []
    with urllib.request.urlopen(req, timeout=600) as resp, tarfile.open(fileobj=resp, mode="r|") as tar:
        for member in tar:
            if member.name not in targets or not member.isfile():
                continue
            data = tar.extractfile(member).read()
            size, md5 = manifest[member.name]
            if len(data) != size or hashlib.md5(data).hexdigest() != md5:
                bad.append(member.name)
                continue
            dest = out / member.name.split("/", 1)[1]
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            found += 1
            if found + len(bad) == len(targets):
                break
    return {"wanted": len(targets), "restored": found, "md5_mismatch": bad}


if __name__ == "__main__":
    print(json.dumps(restore(sys.argv[1], sys.argv[2], sys.argv[3:]), indent=1))
