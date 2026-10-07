#!/usr/bin/env python3
"""knowledge_bundle.py — the AbsolutRealism KNOWLEDGE MIRROR (his ruling 2026-10-07 00:39 CT: "create folders for — and
always upload our changes to all of these places when we upload anything — project knowledge, custom instructions, and
anything else relevant, including all prompts").

Builds  _knowledge/AR-Knowledge-<stamp>/  and  _knowledge/AR-Knowledge-<stamp>.zip  with the layout the GitHub repo uses:

  knowledge/CLAUDE-AR.md        the full law                         (_knowledge/src/knowledge/CLAUDE-AR.md)
  knowledge/canonical/          the 7 canonical docs, byte-exact     (09-29 archive, read out of the Project)
  knowledge/current/            newest handoffs, checklists, decisions, lesson candidates, history addenda (>= 2026-10-01)
  knowledge/logs/               decision_journal, phase_log, intake_ledger, delivery_ledger
  knowledge/memory/             the Project's memory files           (_knowledge/memory_export/)
  knowledge/project-only/       Project docs that have no workspace copy (_knowledge/project_export/)
  knowledge/docs/               every other workspace document (text; small json); images stay on Drive
  knowledge/tools/              workspace tools + the CURRENT script sources (old bp02_src_22x copies and generated
                                files > 1 MB are left out and listed in MANIFEST "omitted")
  prompts/                      every prompt, upgraded               (_knowledge/src/prompts/)
  claude-settings/              settings.json + CLAUDE.md.repo-root  (_knowledge/src/claude-settings/, src/CLAUDE.md)
  knowledge/00-INDEX.md         generated map + read order
  knowledge/MANIFEST.json       generated: every file's bytes + md5 + source

Usage:  python3 tools/knowledge_bundle.py [--stamp 2026-10-07a] [--headline "text"]
Prints the zip path, size and md5. Refuses to overwrite an existing stamp (versions are never reused).
"""
import argparse
import hashlib
import json
import re
import shutil
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path("/home/claude")
KN = ROOT / "_knowledge"
SRC = KN / "src"
ARCHIVE_0929 = KN / "AbsolutRealism-Knowledge-2026-09-29" / "project-knowledge"
CANON = ["OPERATING-MANUAL-v4.md", "FOUNDATION-v3.md", "ARCHITECTURE-v3.md", "HISTORY-v4.md",
         "JEM-TO-BEDROCK-CONVERSION-STANDARD.md", "AR-Tree-Structure-Building-Guide.txt",
         "AbsolutRealism-FOG-LIGHTING-Stacking-Dossier.md"]
CURRENT_RE = re.compile(r"^(HANDOFF|LESSON-CANDIDATES|HISTORY-ADDENDUM|DECISIONS|TEST-CHECKLIST|QUESTIONS-AND|RESULTS-AND)"
                        r".*(2026-10-\d\d|-2\d\d)")
LOGS = ["decision_journal.md", "phase_log.md", "intake_ledger.md", "delivery_ledger.md"]
DOC_TEXT = {".md", ".txt", ".csv"}
TOOL_EXT = {".py", ".sh", ".js", ".mjs", ".json", ".md"}
OLD_SRC = re.compile(r"^bp02_src(_22[0-7])?$")          # superseded script-source copies (bp02_src_228 is current)
MAX_TOOL = 1_000_000
MAX_JSON_DOC = 150_000
SKIP_DOC_PARTS = ("before_", "bp02_entities", "node_modules", "__pycache__", "/convb/")
# secrets never enter the mirror: known strings are redacted, anything that LOOKS like a live credential aborts the build
REDACT = [re.compile(rb"[REDACTED]")]          # the expired gofile guest token (2026-09 doc)
SECRET_RE = re.compile(rb"ya29\.[A-Za-z0-9_-]{20,}|1//0[A-Za-z0-9_-]{30,}|GOCSPX-[A-Za-z0-9_-]{10,}|ghp_[A-Za-z0-9]{30,}"
                       rb"|github_pat_[A-Za-z0-9_]{20,}|sk-ant-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY")


def md5(data):
    """Hex md5 of bytes."""
    return hashlib.md5(data).hexdigest()


def newest_handoff_date(name):
    """Sort key for handoff-like names: the first YYYY-MM-DD in the name ('' if none)."""
    m = re.search(r"2026-\d\d-\d\d", name)
    return m.group(0) if m else ""


class Bundle:
    """Collects files into the bundle dir and records one manifest row per file."""

    def __init__(self, out):
        self.out, self.rows, self.omitted, self.seen = out, [], [], set()

    def add(self, rel, data, source):
        """Write data at rel (posix path inside the bundle) unless that path was already written."""
        if rel in self.seen:
            return
        self.seen.add(rel)
        for rx in REDACT:
            data = rx.sub(b"[REDACTED]", data)
        hit = SECRET_RE.search(data)
        if hit:
            raise SystemExit(f"possible secret in {source} at byte {hit.start()} — fix the source; nothing was shipped")
        dst = self.out / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_bytes(data)
        self.rows.append({"path": rel, "bytes": len(data), "md5": md5(data), "source": source})

    def add_file(self, rel, path):
        self.add(rel, Path(path).read_bytes(), str(Path(path).relative_to(ROOT)))


def collect(b):
    # 1. the law, prompts, settings
    b.add_file("knowledge/CLAUDE-AR.md", SRC / "knowledge" / "CLAUDE-AR.md")
    for p in sorted((SRC / "prompts").rglob("*")):
        if p.is_file():
            b.add_file("prompts/" + p.relative_to(SRC / "prompts").as_posix(), p)
    for p in sorted((SRC / "claude-settings").rglob("*")):
        if p.is_file():
            b.add_file("claude-settings/" + p.relative_to(SRC / "claude-settings").as_posix(), p)
    b.add_file("claude-settings/CLAUDE.md.repo-root", SRC / "CLAUDE.md")

    # 2. canonical (byte-exact copies read out of the Project; unchanged since 2026-07-11 per project_info)
    for n in CANON:
        p = ARCHIVE_0929 / n
        if not p.exists():
            raise SystemExit(f"canonical doc missing from the 09-29 archive: {n}")
        b.add("knowledge/canonical/" + n, p.read_bytes(), "claude.ai Project (09-29 byte-exact archive)")

    # 3. current state: handoffs etc. dated 2026-10-01 or later, from the workspace
    cur = []
    for p in (ROOT / "_docs").rglob("*"):
        if p.is_file() and p.suffix in DOC_TEXT and CURRENT_RE.match(p.name):
            d = newest_handoff_date(p.name)
            if d >= "2026-10-01" or "-228" in p.name:
                cur.append(p)
    for p in sorted(cur, key=lambda q: q.name):
        b.add_file("knowledge/current/" + p.name, p)

    # 4. logs + memory + project-only docs
    for n in LOGS:
        p = ROOT / "_logs" / n
        if p.exists():
            b.add_file("knowledge/logs/" + n, p)
    for p in sorted((ROOT / "_logs" / "agent_status").glob("*")):
        if p.is_file():
            b.add_file("knowledge/logs/agent_status/" + p.name, p)
    if (ROOT / "_logs" / "agent_brief_1007.md").exists():
        b.add_file("knowledge/logs/agent_brief_1007.md", ROOT / "_logs" / "agent_brief_1007.md")
    for p in sorted((KN / "memory_export").rglob("*.md")):
        b.add_file("knowledge/memory/" + p.relative_to(KN / "memory_export").as_posix(), p)
    pe = KN / "project_export"
    if pe.exists():
        for p in sorted(pe.rglob("*")):
            if p.is_file():
                b.add_file("knowledge/project-only/" + p.relative_to(pe).as_posix(), p)

    # 5. every other workspace document (text)
    for p in sorted((ROOT / "_docs").rglob("*")):
        if not p.is_file():
            continue
        s = p.as_posix()
        if any(x in s for x in SKIP_DOC_PARTS):
            continue
        rel = "knowledge/docs/" + p.relative_to(ROOT / "_docs").as_posix()
        if p.suffix in DOC_TEXT:
            b.add_file(rel, p)
        elif p.suffix == ".json":
            if p.stat().st_size <= MAX_JSON_DOC:
                b.add_file(rel, p)
            else:
                b.omitted.append({"path": s.replace(str(ROOT) + "/", ""), "bytes": p.stat().st_size, "why": "large json report"})

    # 6. tools (current sources only)
    for p in sorted((ROOT / "tools").rglob("*")):
        if not p.is_file() or p.suffix not in TOOL_EXT:
            continue
        parts = p.relative_to(ROOT / "tools").parts
        if any(x in ("node_modules", "__pycache__") for x in parts):
            continue
        if len(parts) > 1 and OLD_SRC.match(parts[0]):
            continue
        rel_s = "tools/" + "/".join(parts)
        if p.stat().st_size > MAX_TOOL:
            b.omitted.append({"path": rel_s, "bytes": p.stat().st_size, "why": "generated data > 1 MB (rebuilt by its tool)"})
            continue
        b.add_file("knowledge/" + rel_s, p)
    for d in sorted((ROOT / "tools").iterdir()):
        if d.is_dir() and OLD_SRC.match(d.name):
            b.omitted.append({"path": f"tools/{d.name}/", "bytes": 0, "why": "superseded script-source copy (bp02_src_228 is current)"})


def write_index(b, stamp, headline):
    by_top = {}
    for r in b.rows:
        top = "/".join(r["path"].split("/")[:2])
        by_top.setdefault(top, [0, 0])
        by_top[top][0] += 1
        by_top[top][1] += r["bytes"]
    src_of = {r["path"]: r["source"] for r in b.rows}
    cur = sorted((r["path"] for r in b.rows if r["path"].startswith("knowledge/current/HANDOFF")),
                 key=lambda s: (newest_handoff_date(s), (ROOT / src_of[s]).stat().st_mtime))
    lines = [f"# ABSOLUTREALISM KNOWLEDGE MIRROR — {stamp}", "",
             f"**Headline:** {headline}", "",
             "Built by `tools/knowledge_bundle.py`. Every file's md5 is in `knowledge/MANIFEST.json`.", "",
             "## Read order", "",
             "1. `knowledge/CLAUDE-AR.md` — the law (effort, witness rule, failure modes P1–P15, sync law, execution law, licence).",
             "2. `knowledge/canonical/` — OPERATING-MANUAL-v4 → FOUNDATION-v3 → ARCHITECTURE-v3 → HISTORY-v4.",
             f"3. The newest handoff = the CURRENT STATE: `{cur[-1] if cur else '(none)'}`.",
             "4. `knowledge/logs/decision_journal.md` (D-* rulings, ASSUMPTION, DEFERRAL) and `phase_log.md` (what shipped, md5s).",
             "5. `knowledge/memory/` — engine laws, ways of working, preferences, area notes.",
             "6. Everything in `knowledge/docs/` and `knowledge/project-only/` is reference — hypothesis only unless canonical (Source-Trust Law).",
             "", "## Folders", "", "| Folder | Files | Bytes |", "|---|---|---|"]
    for k in sorted(by_top):
        lines.append(f"| `{k}` | {by_top[k][0]} | {by_top[k][1]:,} |")
    lines += ["", "## Left out on purpose", "",
              "- Images, packs (.mcpack), worlds and build dirs — they live on Drive `ClaudeUploads/` (packs) and in the cloud workspace.",
              "- Secrets — never in the mirror.",
              f"- {len(b.omitted)} large/generated or superseded items, listed in MANIFEST `omitted`.", ""]
    data = "\n".join(lines).encode()
    b.add("knowledge/00-INDEX.md", data, "generated")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stamp", default=time.strftime("%Y-%m-%d"))
    ap.add_argument("--headline", default="knowledge sync")
    a = ap.parse_args()
    out = KN / f"AR-Knowledge-{a.stamp}"
    zpath = KN / f"AR-Knowledge-{a.stamp}.zip"
    if out.exists() or zpath.exists():
        raise SystemExit(f"{out.name} exists — stamps are never reused (pass --stamp {a.stamp}b)")
    b = Bundle(out)
    collect(b)
    write_index(b, a.stamp, a.headline)
    man = {"stamp": a.stamp, "headline": a.headline, "built_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "files": len(b.rows) + 1, "bytes": sum(r["bytes"] for r in b.rows), "rows": b.rows, "omitted": b.omitted}
    (out / "knowledge" / "MANIFEST.json").write_text(json.dumps(man, indent=1))
    # verify every row against disk before zipping (P8)
    for r in b.rows:
        if md5((out / r["path"]).read_bytes()) != r["md5"]:
            raise SystemExit(f"md5 mismatch after write: {r['path']}")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(out.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(out).as_posix())
    with zipfile.ZipFile(zpath) as z:
        bad = z.testzip()
        n = len(z.namelist())
    if bad:
        raise SystemExit(f"zip test failed at {bad}")
    data = zpath.read_bytes()
    print(json.dumps({"zip": str(zpath), "bytes": len(data), "md5": md5(data), "files": n,
                      "uncompressed": man["bytes"], "omitted": len(b.omitted)}))


if __name__ == "__main__":
    sys.exit(main())
