#!/usr/bin/env python3
"""knowledge_snapshot.py — D-C288 (his 17:48 CT 09-29: "upload everything current into a Google drive folder for knowledge
specifically and we can start again loading and saving knowledge here").

Builds _knowledge/AbsolutRealism-Knowledge-<date>/ :
  project-knowledge/<path>   every unique path in project knowledge (from _logs/project_docs_0929.json):
                             - read from the project itself (project_read results recovered byte-exact from the session's
                               transcripts, incl. subagent transcripts), or
                             - for docs/tools that live in this workspace, the CURRENT workspace file (source = workspace)
  workspace/                 current knowledge that is NOT in project knowledge: tools/ (all .py/.js/.mjs/.sh), _docs/*.md|.json|.csv|.html,
                             _logs/{decision_journal,phase_log,intake_ledger,delivery_ledger}.md
  MANIFEST.json              one row per file: path, bytes, md5, source, class, created_at
  00-INDEX.md                what is where, read order, the classes
Then zips it (deterministic order) next to the folder.
"""
import hashlib, json, os, re, sys, zipfile, collections, glob
from pathlib import Path

ROOT = Path("/home/claude")
DATE = "2026-09-29"
OUT = ROOT / "_knowledge" / f"AbsolutRealism-Knowledge-{DATE}"
SESSION = Path("/root/.claude/projects/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2")
CANON = ["OPERATING-MANUAL-v4.md", "FOUNDATION-v3.md", "ARCHITECTURE-v3.md", "HISTORY-v4.md", "JEM-TO-BEDROCK-CONVERSION-STANDARD.md",
         "AR-Tree-Structure-Building-Guide.txt", "AbsolutRealism-FOG-LIGHTING-Stacking-Dossier.md"]
LATEST_HANDOFF = "HANDOFF-SESSION-2026-09-22-SEAMS-HEARTH-V2.md"
ACTIVE = ["PLAN-OWNERSHIP-WAVE-2026-09-28.md", "MOB-SWEEP-2026-09-29.md", "TESTRUNNER-GUIDE-v1.md", "MOB-CONVERSION-PHASE0-PROTOCOL-2026-09-27.md",
          "MOB-CONVERSION-RESEARCH-2026-09-27.md", "R2-WITNESS-READS-2026-09-28.md", "P0-WITNESS-READS-2026-09-27.md"]


def md5(b): return hashlib.md5(b).hexdigest()


def project_reads():
    """latest project_read result per path, from the main transcript + every subagent transcript (file order = time order)."""
    files = [SESSION.parent / (SESSION.name + ".jsonl")] + sorted(SESSION.glob("subagents/*.jsonl"), key=lambda p: p.stat().st_mtime)
    got = {}

    def walk(o):
        if isinstance(o, dict):
            for v in o.values(): yield from walk(v)
        elif isinstance(o, list):
            for v in o: yield from walk(v)
        elif isinstance(o, str) and o.startswith('{"method":"project_read"'): yield o
    for f in files:
        for line in open(f, encoding="utf-8"):
            if "project_read" not in line: continue
            try: d = json.loads(line)
            except Exception: continue
            for s in walk(d):
                try: j = json.loads(s)
                except Exception: continue
                if isinstance(j.get("content"), str): got[j["path"]] = j
    return got


def local_index():
    idx = collections.defaultdict(list)
    for base in ("tools", "_docs", "_logs"):
        for p in (ROOT / base).rglob("*"):
            if p.is_file(): idx[p.name].append(p)
    return idx


def local_for(path, idx):
    rel = path.lstrip("/")
    if rel.startswith("claude/tools/"):
        p = ROOT / "tools" / rel[len("claude/tools/"):]
        if p.exists(): return p
    cands = idx.get(rel.split("/")[-1], [])
    pref = [c for c in cands if "/_docs/" in str(c) and "/convb/" not in str(c)] or cands
    return sorted(pref, key=lambda c: -c.stat().st_mtime)[0] if pref else None


def classify(rel):
    name = rel.split("/")[-1]
    if name in CANON: return "CANONICAL"
    if name == LATEST_HANDOFF: return "CURRENT-STATE (latest handoff)"
    if name in ACTIVE: return "ACTIVE-WORKING"
    if rel.startswith("claude/tools/") or name.endswith((".py", ".js", ".mjs")): return "TOOL"
    if name.startswith("HANDOFF"): return "HISTORICAL-HANDOFF (superseded; chronicle source)"
    return "SUPERSEDED-REFERENCE (hypothesis source only, per Source-Trust Law)"


def main():
    import shutil
    if OUT.exists(): shutil.rmtree(OUT)
    docs = json.load(open(ROOT / "_logs/project_docs_0929.json"))
    reads = project_reads(); idx = local_index()
    rows = []; seen = collections.Counter(); created = collections.defaultdict(list)
    for d in docs: created[d["path"]].append(d["created_at"])
    missing = []
    for path in dict.fromkeys(d["path"] for d in docs):
        rel = path.lstrip("/")
        if (OUT / "project-knowledge" / rel).exists():            # "/X.md" and "X.md" twins: keep both if bytes differ
            pass
        src = None
        if path in reads:
            data = reads[path]["content"].encode("utf-8"); src = "project_read"
        else:
            lp = local_for(path, idx)
            if lp: data = lp.read_bytes(); src = f"workspace:{lp.relative_to(ROOT).as_posix()}"
        if src is None: missing.append(path); continue
        dst = OUT / "project-knowledge" / rel
        if dst.exists():
            if dst.read_bytes() == data:
                for r in rows:
                    if r["path"] == "project-knowledge/" + rel: r["also_listed_as"] = path
                continue
            dst = dst.with_name(dst.stem + ".slash-variant" + dst.suffix)
        dst.parent.mkdir(parents=True, exist_ok=True); dst.write_bytes(data)
        rows.append({"path": dst.relative_to(OUT).as_posix(), "project_path": path, "bytes": len(data), "md5": md5(data), "source": src,
                     "class": classify(rel), "created_at": sorted(created[path]), "copies_in_project": len(created[path])})
    # workspace-only knowledge
    ws = []
    for p in sorted((ROOT / "tools").rglob("*")):
        if p.is_file() and p.suffix in (".py", ".js", ".mjs", ".sh", ".json", ".md") and "__pycache__" not in str(p) and p.stat().st_size < 3_000_000:
            ws.append(p)
    for p in sorted((ROOT / "_docs").rglob("*")):
        if p.is_file() and p.suffix in (".md", ".json", ".csv", ".html", ".txt") and p.stat().st_size < 3_000_000:
            ws.append(p)
    for n in ("decision_journal.md", "phase_log.md", "intake_ledger.md", "delivery_ledger.md"):
        ws.append(ROOT / "_logs" / n)
    have = {(r["path"].split("/")[-1], r["md5"]) for r in rows}
    for p in ws:
        data = p.read_bytes()
        if (p.name, md5(data)) in have: continue                     # already in project-knowledge/ byte-identical
        dst = OUT / "workspace" / p.relative_to(ROOT)
        dst.parent.mkdir(parents=True, exist_ok=True); dst.write_bytes(data)
        rows.append({"path": dst.relative_to(OUT).as_posix(), "bytes": len(data), "md5": md5(data), "source": "workspace (current)",
                     "class": "WORKSPACE-" + ("TOOL" if p.parts[len(ROOT.parts)] == "tools" else "DOC-OR-LOG")})
    man = {"built": DATE, "project_docs_listed": len(docs), "unique_project_paths": len(dict.fromkeys(d["path"] for d in docs)),
           "project_read_recovered": sum(1 for r in rows if r.get("source") == "project_read"), "missing": missing, "files": rows}
    (OUT / "MANIFEST.json").write_text(json.dumps(man, indent=1))
    return man


if __name__ == "__main__":
    m = main()
    c = collections.Counter(r["class"] for r in m["files"])
    print("files", len(m["files"]), "missing", m["missing"]); print(c)
    print("bytes", sum(r["bytes"] for r in m["files"]))
