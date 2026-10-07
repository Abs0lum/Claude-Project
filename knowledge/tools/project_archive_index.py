#!/usr/bin/env python3
"""project_archive_index.py — the "where every moved file lives" index for the Project→Drive relocation (his ruling
01:24 CT 2026-10-07: relocate the claude/tools/* copies to Drive, point to them from project knowledge, THEN clean up,
leaving a file that records the location of every moved file).

Inputs:  _logs/project_tools_archive_rows.json  (project_path, created_at, bytes, md5, drive_name — from the fresh reads)
         _logs/drive_ship_ledger.json           (Drive id + md5 per uploaded file)
Output:  _knowledge/MOVED-TO-DRIVE-INDEX.md      (one row per moved file; refuses to write if ANY row lacks a Drive copy
                                                 whose md5 equals the Project copy's md5)
"""
import json
import sys
from pathlib import Path

ROOT = Path("/home/claude")
FOLDER = "ClaudeUploads/project-archive-2026-10-07"
FOLDER_ID = "1KrQ1gkjdESoamXYodpDx-mt0nyVr8Fb3"
ZIP = "PROJECT-TOOLS-ARCHIVE-2026-10-07.zip"


def main():
    rows = json.load(open(ROOT / "_logs/project_tools_archive_rows.json"))
    ledger = json.load(open(ROOT / "_logs/drive_ship_ledger.json"))
    z = ledger[f"{FOLDER}/{ZIP}"]
    bad = []
    for r in rows:
        e = ledger.get(f"{FOLDER}/{r['drive_name']}")
        if not e or e["md5"] != r["md5"] or e["bytes"] != r["bytes"]:
            bad.append(r["project_path"])
        else:
            r["drive_id"] = e["id"]
    if bad:
        raise SystemExit(f"{len(bad)} file(s) without a verified Drive copy, e.g. {bad[:3]} — index NOT written")
    lines = [
        "# MOVED TO DRIVE — INDEX OF EVERY RELOCATED PROJECT FILE (2026-10-07)",
        "",
        "Abs0lum's ruling (01:24 CT 2026-10-07): the claude/tools/* copies were moved out of project knowledge to Google Drive",
        "to free room; this file records where every one of them now lives. Each was read fresh from the Project, saved",
        "byte-exact, uploaded, and its Drive md5 checked equal to the Project copy BEFORE the Project copy was deleted.",
        "",
        f"- Drive folder: `{FOLDER}` (folder id `{FOLDER_ID}`)",
        f"- One zip with all {len(rows)} files: `{ZIP}` (file id `{z['id']}`, {z['bytes']:,} B, md5 `{z['md5']}`);"
        " paths inside the zip = the original Project paths.",
        "- Single files: same folder; Drive name = the path after `claude/tools/` with `/` written as `__`.",
        "- Also in the knowledge mirror (Drive `ClaudeUploads/knowledge/`, GitHub `knowledge/`) under `knowledge/tools/`"
        " (newer workspace versions).",
        "- To fetch one in a cloud session: `bash tools/drive_pull.sh <file id> <out path>` (or the Google Drive connector).",
        "",
        f"## The {len(rows)} files",
        "",
        "| Project path | Bytes | md5 | Drive file id | Created in Project |",
        "|---|---|---|---|---|",
    ]
    for r in sorted(rows, key=lambda x: x["project_path"]):
        lines.append(f"| {r['project_path']} | {r['bytes']} | {r['md5']} | {r['drive_id']} | {r['created_at'][:10]} |")
    out = ROOT / "_knowledge/MOVED-TO-DRIVE-INDEX.md"
    out.write_text("\n".join(lines) + "\n")
    print(f"index written: {out} ({out.stat().st_size:,} B, {len(rows)} rows, 0 unverified)")


if __name__ == "__main__":
    sys.exit(main())
