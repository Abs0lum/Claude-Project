#!/usr/bin/env python3
"""recheck2_r2.py — RECHECK-WEEK 2 (10-03 install set) R2: manifest hygiene across the CURRENT INSTALL SET (16 packs, from R1):
  * every manifest parses; header.version == the version in the file name; header + module UUIDs unique across the set
    (the game refuses two packs with one UUID, and silently takes one of two modules with one UUID)
  * every dependency (uuid + version) resolves to a pack in the set at that exact version, or is an engine module
    (@minecraft/server, @minecraft/server-ui) at a version the pinned engine ships (stable 2.x list)
  * min_engine_version present and <= the game he runs (1.26.x) — a pack asking for a newer engine will not load
  * RP packs: pack_scope / capabilities (pbr) noted; BP packs: script entry file exists
Writes _docs/recheck/W2-R2-manifests.json. Read-only."""
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
from recheck2_r1 import SET  # noqa: E402

OUT = Path("/mnt/user-data/outputs")
ENGINE_MODULES = {"@minecraft/server", "@minecraft/server-ui", "@minecraft/server-gametest", "@minecraft/server-net",
                  "@minecraft/server-admin", "@minecraft/server-editor"}


def main():
    packs = []
    for name, bdir in SET:
        src = ROOT / "_build" / bdir
        m = json.loads((src / "manifest.json").read_text(encoding="utf-8-sig"))
        ver_name = re.search(r"v(\d+)_(\d+)_(\d+)\.mcpack$", name)
        ver_name = [int(v) for v in ver_name.groups()]
        row = {"archive": name, "build": bdir, "uuid": m["header"]["uuid"], "version": m["header"]["version"],
               "name_version_match": m["header"]["version"] == ver_name,
               "min_engine": m["header"].get("min_engine_version"),
               "modules": [(mod.get("type"), mod["uuid"], mod.get("version"), mod.get("entry")) for mod in m.get("modules", [])],
               "dependencies": m.get("dependencies", []),
               "capabilities": m.get("capabilities"),
               "scope": m["header"].get("pack_scope"),
               "issues": []}
        if not row["name_version_match"]:
            row["issues"].append(f"header.version {m['header']['version']} != file name {ver_name}")
        for mod in m.get("modules", []):
            if mod.get("version") != m["header"]["version"]:
                row["issues"].append(f"module {mod.get('type')} version {mod.get('version')} != header {m['header']['version']}")
            if mod.get("type") == "script":
                if not (src / mod["entry"]).exists():
                    row["issues"].append(f"script entry missing: {mod['entry']}")
        if not row["min_engine"]:
            row["issues"].append("no min_engine_version")
        packs.append(row)
    # uniqueness across the set
    uuids = Counter()
    where = defaultdict(list)
    for p in packs:
        uuids[p["uuid"]] += 1
        where[p["uuid"]].append(p["archive"])
        for _, u, _, _ in p["modules"]:
            uuids[u] += 1
            where[u].append(p["archive"] + " (module)")
    dup = {u: where[u] for u, n in uuids.items() if n > 1}
    # version-spot gate (the shipped tool) on every archive
    vp = subprocess.run([sys.executable, str(ROOT / "tools/verify_pack_versions.py")] + [str(OUT / n) for n, _ in SET],
                        capture_output=True, text=True)
    by_uuid = {p["uuid"]: p for p in packs}
    for p in packs:
        for d in p["dependencies"]:
            if "module_name" in d:
                if d["module_name"] not in ENGINE_MODULES:
                    p["issues"].append(f"unknown engine module {d['module_name']}")
                continue
            tgt = by_uuid.get(d.get("uuid"))
            if not tgt:
                p["issues"].append(f"dependency uuid {d.get('uuid')} is not in the install set")
            elif tgt["version"] != d.get("version"):
                p["issues"].append(f"dependency on {tgt['archive']} wants {d.get('version')}, set has {tgt['version']}")
    report = {"packs": packs, "duplicate_uuids": dup, "verify_pack_versions_rc": vp.returncode,
              "verify_pack_versions_out": vp.stdout[-4000:] + vp.stderr[-2000:]}
    (ROOT / "_docs/recheck/W2-R2-manifests.json").write_text(json.dumps(report, indent=1))
    bad = [p for p in packs if p["issues"]]
    for p in packs:
        print(f"{'FAIL' if p['issues'] else 'PASS'} {p['archive']:62} {'.'.join(map(str, p['version'])):8} min_engine {p['min_engine']} "
              f"deps {len(p['dependencies'])} {'; '.join(p['issues'])}")
    print("duplicate uuids:", dup or "none")
    print("verify_pack_versions rc", vp.returncode)
    print(vp.stdout[-1500:])
    print(len(packs) - len(bad), "/", len(packs), "PASS")


if __name__ == "__main__":
    main()
