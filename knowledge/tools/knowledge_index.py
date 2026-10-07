#!/usr/bin/env python3
"""knowledge_index.py — D-C288: writes 00-INDEX.md for a knowledge snapshot built by knowledge_snapshot.py and zips it
(deterministic order and timestamps), then proves zip == folder. Usage: knowledge_index.py <zip-name>"""
import collections, hashlib, json, re, sys, zipfile
from pathlib import Path

OUT = Path("/home/claude/_knowledge/AbsolutRealism-Knowledge-2026-09-29")
CORE = ["OPERATING-MANUAL-v4.md", "FOUNDATION-v3.md", "ARCHITECTURE-v3.md", "HISTORY-v4.md", "HANDOFF-SESSION-2026-09-22-SEAMS-HEARTH-V2.md",
        "JEM-TO-BEDROCK-CONVERSION-STANDARD.md", "AR-Tree-Structure-Building-Guide.txt", "AbsolutRealism-FOG-LIGHTING-Stacking-Dossier.md",
        "TESTRUNNER-GUIDE-v1.md", "PLAN-OWNERSHIP-WAVE-2026-09-28.md", "MOB-SWEEP-2026-09-29.md", "PLAN-MENAGERIE-PROGRAM-2026-09-29.md"]
MEANING = {"CANONICAL": "authoritative law and reference (custom instructions §2)", "CURRENT-STATE (latest handoff)": "the authoritative current state",
           "ACTIVE-WORKING": "live plans and protocols in use", "TOOL": "tools as published to the project",
           "WORKSPACE-TOOL": "tools newer than their project copy, or never published", "WORKSPACE-DOC-OR-LOG": "reports, baselines, plans, logs (+ newer doc versions)",
           "HISTORICAL-HANDOFF (superseded; chronicle source)": "older handoffs — sources for HISTORY, not law",
           "SUPERSEDED-REFERENCE (hypothesis source only, per Source-Trust Law)": "older designs, research, studies — hypothesis sources only"}
MULTI = [("HANDOFF-SESSION-2026-07-19-SWEEP-PARITY-MERS.md", 9), ("HANDOFF-SESSION-2026-07-19-PACK-REVIEW.md", 7), ("HANDOFF-SESSION-2026-09-20-RAMPS-V6-LLAMAS.md", 3),
         ("HANDOFF-SESSION-2026-08-09-C-SESSION-TAIL.md", 2), ("CIVITAS-THE-TOOL-LADDER-v1.md", 2), ("FINDINGS-DECK-INVESTIGATION-2026-08-15.md", 2),
         ("PW-GIVE-LIST-v3.md", 2), ("HANDOFF-SESSION-2026-07-19-BUILDERS-WAVE.md", 2)]


def first_doc(p):
    try: t = open(OUT / p, encoding="utf-8", errors="replace").read(4000)
    except Exception: return ""
    mm = re.search(r'"""(.*?)(\n|""")', t, re.S) or re.search(r"^\s*(?://|#)\s*(.+)$", t, re.M)
    return (mm.group(1).strip() if mm else "")[:160].replace("|", "/")


def main(zipname):
    m = json.load(open(OUT / "MANIFEST.json")); rows = m["files"]
    by = collections.defaultdict(list)
    for r in rows: by[r["class"]].append(r)
    pk = [r for r in rows if r["path"].startswith("project-knowledge/")]
    pnames = {r["path"].split("/")[-1] for r in pk}
    newer = [r for r in rows if r["path"].startswith("workspace/") and r["path"].split("/")[-1] in pnames]

    def find(name):
        c = [r for r in rows if r["path"].split("/")[-1] == name]
        c.sort(key=lambda r: (r["path"].startswith("project-knowledge/"), r["path"]))   # newest (workspace) first
        return c[0] if c else None
    core = [(n, find(n)) for n in CORE]
    L = ["# ABSOLUTREALISM — KNOWLEDGE ARCHIVE 2026-09-29 (v2: every unique version) · 00-INDEX\n",
         "Built by `tools/knowledge_snapshot.py` + `tools/knowledge_index.py` (D-C288). Abs0lum's rulings: 17:48 CT 09-29 (\"upload everything current into a Google drive folder for knowledge\") and 18:14 (\"duplicates are unnecessary … I want at least one copy of every unique version of every file, folder, or document\").\n",
         f"**Contents:** {len(rows)} files, {sum(r['bytes'] for r in rows):,} bytes, md5 per file in `MANIFEST.json`. The folder paths inside the zip are the original ones.\n",
         "## Folders\n",
         f"- `project-knowledge/` — all {len(pk)} files that were in the claude.ai project on 09-29, **read out of the project itself, byte-exact** ({m['unique_project_paths']} path strings; `/X` and `X` twins with identical bytes are stored once).",
         f"  - {len(pk) - len(newer)} of them are byte-identical to the current workspace file they came from.",
         f"  - The other {len(newer)} have a NEWER version in `workspace/` — both versions are kept.",
         "- `workspace/` — current knowledge that is not identical to anything in the project:",
         "  - newer versions (the 17 above);",
         "  - tools and docs that were never published;",
         "  - the 4 logs (`decision_journal`, `phase_log`, `intake_ledger`, `delivery_ledger`).\n",
         "## Versions this archive could NOT capture (they stay in the project, untouched)\n",
         "These 8 file names have several same-name copies in the project, and reading by name returns ONE copy. The older copies cannot be exported through the project connection, so they are never deleted from the project.",
         "Three names also have a different-size version already loose in the Drive: SWEEP-PARITY-MERS 7,414 B, PACK-REVIEW 7,203 B and BUILDERS-WAVE 3,417 B.\n",
         "| Name | Copies in project | Captured here |\n|---|---|---|"]
    for n, c in MULTI: L.append(f"| {n} | {c} | 1 |")
    L.append("\n## Classes\n")
    L.append("| Class | Files | Meaning |\n|---|---|---|")
    for k, v in MEANING.items(): L.append(f"| {k} | {len(by[k])} | {v} |")
    L.append("\n## Read order (unchanged law)\n")
    L.append("1. OPERATING-MANUAL-v4 → FOUNDATION-v3 → ARCHITECTURE-v3 → HISTORY-v4.")
    L.append("2. The newest HANDOFF is the current state (revision 30 is in `workspace/_docs/`; the project holds revision 29).")
    L.append("3. The conversion standard, the tree guide and the fog dossier are the standing references.\n")
    L.append("## The project core after the move (his pick: core + all tools)\n")
    L.append("| Doc | Bytes | Newest version in this archive |\n|---|---|---|")
    for n, r in core: L.append(f"| {n} | {r['bytes']:,} | `{r['path']}` |" if r else f"| {n} | — | MISSING |")
    L.append("\n## Newer workspace versions of project files\n")
    for r in sorted(newer, key=lambda r: r["path"]): L.append(f"- `{r['path']}` — {r['bytes']:,} B · md5 `{r['md5']}`")
    L.append("\n## TOOLS-INDEX (first docstring line)\n")
    L.append("| Tool | Where | What |\n|---|---|---|")
    for r in sorted([r for r in rows if "TOOL" in r["class"]], key=lambda r: (r["path"].split("/")[-1], r["path"])):
        L.append(f"| {r['path'].split('/')[-1]} | `{r['path']}` | {first_doc(r['path'])} |")
    L.append("\n## Everything else\n")
    for k in ["CANONICAL", "CURRENT-STATE (latest handoff)", "ACTIVE-WORKING", "WORKSPACE-DOC-OR-LOG", "HISTORICAL-HANDOFF (superseded; chronicle source)",
              "SUPERSEDED-REFERENCE (hypothesis source only, per Source-Trust Law)"]:
        L.append(f"\n### {k}\n")
        for r in sorted(by[k], key=lambda r: r["path"]): L.append(f"- `{r['path']}` — {r['bytes']:,} B · md5 `{r['md5']}`")
    idx = "\n".join(L) + "\n"
    (OUT / "00-INDEX.md").write_text(idx, encoding="utf-8")
    zp = OUT.parent / zipname
    if zp.exists(): raise SystemExit(f"REFUSED: {zp.name} exists (never reuse a name for different bytes)")
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for p in sorted(OUT.rglob("*")):
            if p.is_file():
                zi = zipfile.ZipInfo(OUT.name + "/" + p.relative_to(OUT).as_posix(), date_time=(2026, 9, 29, 18, 0, 0))
                zi.compress_type = zipfile.ZIP_DEFLATED; zi.external_attr = 0o644 << 16
                z.writestr(zi, p.read_bytes())
    bad = n = 0
    with zipfile.ZipFile(zp) as z:
        for i in z.infolist():
            n += 1
            if z.read(i) != (OUT / i.filename.split("/", 1)[1]).read_bytes(): bad += 1
    print(f"index {len(idx.encode()):,} B; zip {zp.name} {zp.stat().st_size:,} B md5 {hashlib.md5(zp.read_bytes()).hexdigest()} entries {n} mismatch {bad}")


if __name__ == "__main__":
    main(sys.argv[1])
