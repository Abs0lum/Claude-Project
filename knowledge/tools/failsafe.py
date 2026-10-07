#!/usr/bin/env python3
"""failsafe.py — THE FAILSAFE (his 02:21 / 02:22 10-03): a place I can only ADD to, never delete from, that holds every
current, correct detail and file — so that after a failure on either side (a sandbox wiped, a bad command of mine, a
lost phone) the whole state comes back from his Drive.

Two halves, both append-only by construction:
  * /home/claude/_failsafe/<stamp>/ — the local record of each snapshot (README + manifest + ledger entry). The
    recoverable-delete guard (tools/pw_safe.py) and the rm / mv shims REFUSE every delete, move-out or overwrite under
    _failsafe, PW_ALLOW_DELETE included.
  * Drive folder "AR-Failsafe" — one streamed, md5-verified tar per snapshot (failsafe-<stamp>.tar) with its manifest
    and README beside it; frozen build dirs go once each into "AR-Failsafe/builds" (<name>.tar). New files only: this
    tool has no update or delete call at all.

What a SNAPSHOT holds (the "current and correct" state): _logs/ (phase log, decision journal, every ledger), _docs/
(handoffs, status board, reports), tools/ (every tool, the script sources, the tests), the root *.md files, every
_build/<dir>/manifest.json + PW-DEPENDENCIES.md (what each frozen build is), and _intake/gofile-folder-*.txt (where the
deliveries live). NEVER: _intake/secrets/, the gofile credentials brief, transcripts, __pycache__, the archives.

Usage:
  failsafe.py snapshot [NOTE]              — dump the state now (NOTE = why: "stopping point", "before X")
  failsafe.py builds NAME [NAME ...]       — upload _build/NAME once each (skips names already recorded)
  failsafe.py restore STAMP OUT [SUBSTR ...] — pull members of snapshot STAMP (ledger key) into OUT, md5-checked
  failsafe.py restore-build NAME OUT [SUBSTR ...] — the same for a build tar
  failsafe.py list                         — what is on record
Complexity: O(bytes) one pass per upload; restores stream the tar once and stop when every wanted member is out."""
import hashlib
import json
import os
import sys
import tarfile
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import gdrive_oauth  # noqa: E402
import gdrive_upload as GU  # noqa: E402
from garbage_tar_to_drive import HashingReader, ResumableSink  # noqa: E402

ROOT = Path("/home/claude")
FS = ROOT / "_failsafe"
LEDGER = ROOT / "_logs/failsafe_ledger.json"            # {"snapshots": {stamp: entry}, "builds": {name: entry}}
TOP_NAME, BUILDS_NAME = "AR-Failsafe", "builds"
EXCLUDE_DIRS = {"__pycache__", "node_modules", ".git", "drive_census_0929"}     # the Drive census is Drive's own listing
SECRET_NAMES = {"session-brief-2026-09-20-C.txt"}
# a STATE snapshot carries the record, not the bulk: images / gifs (renders are re-derivable from the tools), files over
# 4 MiB (probe dumps, garbage manifests — those live in the garbage archive ledger) and the garbage manifests stay out;
# everything left out is listed in the README so nothing is silently missing
BULK_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".mp4", ".zip", ".mcpack", ".mcstructure", ".tar"}
BULK_BYTES = 4 * 2**20


def ledger():
    return json.loads(LEDGER.read_text()) if LEDGER.exists() else {"snapshots": {}, "builds": {}}


def save_ledger(led):
    LEDGER.write_text(json.dumps(led, indent=1))


SKIPPED = []


def snapshot_files():
    """the files of a state snapshot, as (absolute path, archive name); SKIPPED collects the bulk left out"""
    out = []
    SKIPPED.clear()

    def add_tree(base, arc_prefix):
        for p in sorted(base.rglob("*")):
            if not p.is_file() or p.is_symlink():
                continue
            if any(part in EXCLUDE_DIRS for part in p.relative_to(base).parts):
                continue
            if "secrets" in p.parts or p.name in SECRET_NAMES:
                continue
            arc = f"{arc_prefix}/{p.relative_to(base).as_posix()}"
            size = p.stat().st_size
            if p.suffix.lower() in BULK_SUFFIXES or size > BULK_BYTES or p.name.startswith("garbage-"):
                SKIPPED.append((arc, size))
                continue
            out.append((p, arc))

    add_tree(ROOT / "_logs", "_logs")
    add_tree(ROOT / "_docs", "_docs")
    add_tree(ROOT / "tools", "tools")
    for p in sorted(ROOT.glob("*.md")):
        out.append((p, p.name))
    for d in sorted((ROOT / "_build").iterdir()):
        if d.is_dir():
            for name in ("manifest.json", "PW-DEPENDENCIES.md"):
                if (d / name).is_file():
                    out.append((d / name, f"_build/{d.name}/{name}"))
    for p in sorted((ROOT / "_intake").glob("gofile-folder-*.txt")):
        out.append((p, f"_intake/{p.name}"))
    return out


def stream_tar(files, drive, parent, tar_name):
    """stream files as one tar to Drive; returns (drive result, md5, bytes, manifest rows [arc, size, md5])"""
    manifest = []
    sink = ResumableSink(drive, tar_name, parent)
    with tarfile.open(fileobj=sink, mode="w|", format=tarfile.PAX_FORMAT) as tar:
        for p, arc in files:
            info = tar.gettarinfo(str(p), arcname=arc)
            with open(p, "rb") as fh:
                hr = HashingReader(fh)
                tar.addfile(info, hr)
            manifest.append([arc, info.size, hr.md5.hexdigest()])
    r = sink.finish()
    md5, size = sink.md5.hexdigest(), sink.sent
    if not r or r.get("md5Checksum") != md5 or int(r.get("size", -1)) != size:
        raise RuntimeError(f"{tar_name}: Drive md5/size {r and r.get('md5Checksum')}/{r and r.get('size')} != sent {md5}/{size}")
    if len(manifest) != len(files):
        raise RuntimeError(f"{tar_name}: manifest {len(manifest)} != files {len(files)}")
    return r, md5, size, manifest


def readme_text(stamp, note, files, led, tar_entry):
    deliveries = []
    dl = ROOT / "_logs/delivery_ledger.md"
    if dl.exists():
        deliveries = [l for l in dl.read_text().splitlines() if l.startswith("- ")][-24:]
    builds = []
    for d in sorted((ROOT / "_build").iterdir()):
        m = d / "manifest.json"
        if m.is_file():
            try:
                h = json.loads(m.read_text(encoding="utf-8-sig"))["header"]
                builds.append(f"- `{d.name}` — {h.get('name')} v{'.'.join(map(str, h.get('version', [])))}")
            except Exception:
                builds.append(f"- `{d.name}` — (manifest unreadable)")
    status = ROOT / "_docs/recheck/STATUS-BOARD.md"
    board = status.read_text()[:6000] if status.exists() else "(no status board)"
    recorded = "\n".join(f"- `{k}` — {v.get('files')} files, {v.get('tar_bytes', 0) / 2**20:.1f} MiB, Drive id `{v.get('tar_id')}`" for k, v in led.get("builds", {}).items()) or "- (none yet)"
    return f"""# FAILSAFE SNAPSHOT {stamp}

**Why:** {note}
**When:** {time.strftime('%Y-%m-%d %H:%M:%S %Z')} (sandbox clock; CT = UTC−5)
**What:** {len(files)} files — `_logs/` (phase log, decision journal, every ledger), `_docs/` (handoffs, status board, reports), `tools/` (every tool, script sources, tests), the root `*.md`, every `_build/<dir>/manifest.json` + `PW-DEPENDENCIES.md`, the gofile delivery records. No secrets.
**Drive:** folder `AR-Failsafe` → `failsafe-{stamp}.tar` (id `{tar_entry['tar_id']}`, md5 `{tar_entry['tar_md5']}`, {tar_entry['tar_bytes']:,} B) + `failsafe-{stamp}.manifest.json` + this README. New files only; nothing in AR-Failsafe is ever updated or deleted by Claude.

## How to get everything back (from Drive alone)
1. Download `failsafe-{stamp}.tar` from Drive → `AR-Failsafe` and untar it into a fresh `/home/claude` (it recreates `_logs/`, `_docs/`, `tools/`, the root docs, the build manifests).
2. Or from a working sandbox with the OAuth files in place: `python3 tools/failsafe.py restore {stamp} /home/claude/_restore/{stamp} tools/ _logs/` (any path substrings; every file is md5-checked against the manifest).
3. Delivered packs: the gofile folder in `_intake/gofile-folder-*.txt` (md5 of every delivered file in `_logs/delivery_ledger.md`); frozen build dirs: `AR-Failsafe/builds/<name>.tar` → `python3 tools/failsafe.py restore-build <name> /home/claude/_build/<name>`.
4. Then read `_docs/recheck/STATUS-BOARD.md` and the newest `_docs/handoff/HANDOFF-*.md`: they say what was delivered, what is verified, and what comes next.

## Left out of this snapshot (bulk; still on disk, re-derivable or archived elsewhere)
{len(SKIPPED)} files, {sum(sz for _, sz in SKIPPED) / 2**20:.0f} MiB — images / gifs / packs / structures, files over 4 MiB, the garbage-archive manifests (Drive: AR-Garbage-Archives). First 40:
{chr(10).join(f"- `{arc}` {sz:,} B" for arc, sz in SKIPPED[:40])}

## Delivered (last lines of the delivery ledger)
{chr(10).join(deliveries) or '- (none)'}

## Build dirs on disk at snapshot time
{chr(10).join(builds)}

## Build dirs already on Drive (AR-Failsafe/builds)
{recorded}

## Status board at snapshot time (first 6,000 chars)
{board}
"""


def snapshot(note="snapshot"):
    led = ledger()
    stamp = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    files = snapshot_files()
    drive = GU.Drive()
    top = drive.folder(TOP_NAME)
    r, md5, size, manifest = stream_tar(files, drive, top, f"failsafe-{stamp}.tar")
    entry = {"tar_id": r["id"], "tar_md5": md5, "tar_bytes": size, "files": len(manifest), "note": note,
             "verified": time.strftime("%Y-%m-%dT%H:%M:%S")}
    local = FS / stamp
    local.mkdir(parents=True, exist_ok=False)
    (local / "manifest.json").write_text(json.dumps({"snapshot": stamp, "tar_md5": md5, "tar_bytes": size, "files": manifest}, indent=0))
    mr = drive.upload(local / "manifest.json", top, name=f"failsafe-{stamp}.manifest.json")
    entry["manifest_id"] = mr["id"]
    (local / "README.md").write_text(readme_text(stamp, note, files, led, entry))
    rr = drive.upload(local / "README.md", top, name=f"failsafe-{stamp}-README.md")
    entry["readme_id"] = rr["id"]
    (local / "ENTRY.json").write_text(json.dumps(entry, indent=1))
    with open(FS / "INDEX.md", "a") as f:
        f.write(f"- {stamp} · {note} · {len(files)} files · {size / 2**20:.1f} MiB · tar {entry['tar_id']} · README {entry['readme_id']}\n")
    led.setdefault("snapshots", {})[stamp] = entry
    save_ledger(led)
    print(f"FAILSAFE snapshot {stamp}: {len(files)} files, {size / 2**20:.1f} MiB, md5 {md5[:8]} == Drive · README {entry['readme_id']}")
    return stamp


def builds(names):
    led = ledger()
    drive = GU.Drive()
    top = drive.folder(TOP_NAME)
    sub = drive.folder(BUILDS_NAME, top)
    for name in names:
        if name in led.get("builds", {}):
            print(f"{name}: already on Drive (id {led['builds'][name]['tar_id']}) — never re-uploaded")
            continue
        d = ROOT / "_build" / name
        if not d.is_dir():
            print(f"{name}: no such build dir")
            continue
        files = [(p, f"{name}/{p.relative_to(d).as_posix()}") for p in sorted(d.rglob("*")) if p.is_file() and not p.is_symlink()]
        t0 = time.time()
        flat = name.replace("/", "__")                      # "markers-0.2.1/BP" -> markers-0.2.1__BP.tar
        r, md5, size, manifest = stream_tar(files, drive, sub, f"{flat}.tar")
        (FS / "builds").mkdir(parents=True, exist_ok=True)
        mpath = FS / "builds" / f"{flat}.manifest.json"
        if mpath.exists():
            mpath = FS / "builds" / f"{flat}.manifest-{int(time.time())}.json"
        mpath.write_text(json.dumps({"build": name, "tar_md5": md5, "tar_bytes": size, "files": manifest}, indent=0))
        mr = drive.upload(mpath, sub, name=f"{flat}.manifest.json")
        entry = {"tar_id": r["id"], "tar_md5": md5, "tar_bytes": size, "files": len(manifest), "manifest_id": mr["id"],
                 "verified": time.strftime("%Y-%m-%dT%H:%M:%S")}
        (FS / "builds" / f"{flat}.json").write_text(json.dumps(entry, indent=1))
        led.setdefault("builds", {})[name] = entry
        save_ledger(led)
        print(f"{name}: {len(manifest)} files, {size / 2**20:.1f} MiB md5 {md5[:8]} == Drive ({time.time() - t0:.0f} s)", flush=True)


def restore_tar(entry, manifest_rows, out_dir, wanted, strip_first=False):
    manifest = {arc: (size, md5) for arc, size, md5 in manifest_rows}
    targets = {p for p in manifest if not wanted or any(s in p for s in wanted)}
    if not targets:
        raise SystemExit("no manifest member matches")
    token = gdrive_oauth.access_token()
    req = urllib.request.Request(f"https://www.googleapis.com/drive/v3/files/{entry['tar_id']}?alt=media",
                                 headers={"Authorization": f"Bearer {token}"})
    out = Path(out_dir)
    found, bad = 0, []
    with urllib.request.urlopen(req, timeout=1800) as resp, tarfile.open(fileobj=resp, mode="r|") as tar:
        for member in tar:
            if member.name not in targets or not member.isfile():
                continue
            data = tar.extractfile(member).read()
            size, md5 = manifest[member.name]
            if len(data) != size or hashlib.md5(data).hexdigest() != md5:
                bad.append(member.name)
                continue
            rel = member.name.split("/", 1)[1] if strip_first and "/" in member.name else member.name
            dest = out / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            found += 1
            if found + len(bad) == len(targets):
                break
    return {"wanted": len(targets), "restored": found, "md5_mismatch": bad}


def main(argv):
    cmd = argv[0] if argv else "help"
    if cmd == "snapshot":
        snapshot(" ".join(argv[1:]) or "snapshot")
    elif cmd == "builds":
        builds(argv[1:])
    elif cmd == "restore":
        stamp, out, wanted = argv[1], argv[2], argv[3:]
        entry = ledger()["snapshots"][stamp]
        rows = json.loads((FS / stamp / "manifest.json").read_text())["files"]
        print(json.dumps(restore_tar(entry, rows, out, wanted), indent=1))
    elif cmd == "restore-build":
        name, out, wanted = argv[1], argv[2], argv[3:]
        entry = ledger()["builds"][name]
        rows = json.loads((FS / "builds" / f"{name.replace('/', '__')}.manifest.json").read_text())["files"]
        print(json.dumps(restore_tar(entry, rows, out, wanted, strip_first=True), indent=1))
    elif cmd == "list":
        led = ledger()
        for k, v in led.get("snapshots", {}).items():
            print(f"snapshot {k}: {v['files']} files, {v['tar_bytes'] / 2**20:.1f} MiB — {v.get('note')}")
        for k, v in led.get("builds", {}).items():
            print(f"build {k}: {v['files']} files, {v['tar_bytes'] / 2**20:.1f} MiB")
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
