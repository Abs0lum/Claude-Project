#!/usr/bin/env python3
"""SHIP GATE — version-spot consistency for .mcpack files.

Every spot that carries the pack version must agree:
  filename (vX_Y_Z) · header.name (vX.Y.Z) · header.description lead (vX.Y.Z)
  · header.version · every modules[].version · PW-DEPENDENCIES.md stamp (if the
  ledger format carries one: a line starting 'vX.Y.Z · ').
Usage: verify_pack_versions.py PACK [PACK ...]   (exit 1 on any mismatch)
"""
import json, os, re, sys, zipfile

def check(path):
    problems = []
    z = zipfile.ZipFile(path)
    names = z.namelist()
    if "manifest.json" not in names:
        return ["no manifest.json"]
    raw = z.read("manifest.json").decode("utf-8-sig")
    try:
        man = json.loads(raw)
    except json.JSONDecodeError:
        man = json.loads(re.sub(r"//.*", "", raw))
    header = man.get("header", {})
    ver = ".".join(map(str, header.get("version", [])))
    fname = re.search(r"v(\d+)_(\d+)_(\d+)", os.path.basename(path))
    if not fname or ".".join(fname.groups()) != ver:
        problems.append(f"filename version != header.version ({ver})")
    m = re.search(r"v(\d+\.\d+\.\d+)", header.get("name", ""))
    if not m:
        problems.append("header.name carries no version")
    elif m.group(1) != ver:
        problems.append(f"header.name says v{m.group(1)}, header.version is {ver}")
    m = re.match(r"\s*v(\d+\.\d+\.\d+)", header.get("description", ""))
    if not m:
        problems.append("header.description does not lead with the version")
    elif m.group(1) != ver:
        problems.append(f"header.description leads with v{m.group(1)}, header.version is {ver}")
    for mod in man.get("modules", []):
        mv = ".".join(map(str, mod.get("version", [])))
        if mv != ver:
            problems.append(f"module {mod.get('type')} version {mv} != {ver}")
    if "PW-DEPENDENCIES.md" in names:
        text = z.read("PW-DEPENDENCIES.md").decode("utf-8", "replace")
        m = re.search(r"^v(\d+\.\d+\.\d+)(?= · )", text, re.M)
        if m and m.group(1) != ver:
            problems.append(f"PW-DEPENDENCIES.md stamp v{m.group(1)} != {ver}")
    if z.testzip() is not None:
        problems.append("zip integrity failure")
    return problems

if __name__ == "__main__":
    bad = 0
    for p in sys.argv[1:]:
        probs = check(p)
        print(("FAIL " if probs else "OK   ") + os.path.basename(p) + ("" if not probs else "\n     - " + "\n     - ".join(probs)))
        bad += bool(probs)
    sys.exit(1 if bad else 0)
