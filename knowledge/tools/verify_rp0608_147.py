#!/usr/bin/env python3
"""verify_rp0608_147.py — gate for RP-06 v1.4.7 + RP-08 v1.4.7 (D-C260). Packages both on GATE OPEN.
  A manifests: version 1.4.7, names, uuids unchanged from 1.4.6
  B every JSON parses (with the BOM/comment tolerance Bedrock has)
  C diff vs the 1.4.6 zip = exactly the purge list + manifest.json + textures_list.json + PW-DEPENDENCIES.md; nothing added
  D no purged path remains; no RP-07 1.4.12 NEUTRAL path (entity/, models/entity pw_*, textures/entity/pw_*) is shipped by either pack
  E every client entity left in the pack still resolves its geometry/texture inside the pack OR inside RP-07 1.4.12 (nothing orphaned
     by the purge); RP-06 no longer defines minecraft:zombie_pigman
  P package -> /mnt/user-data/outputs/RP-06-AbsolutRealism-Hostile-Mobs-RP-v1_4_7.mcpack + RP-08-AbsolutRealism-Items-RP-v1_4_7.mcpack"""
import glob, hashlib, json, os, re, sys, time, zipfile
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
from build_rp0608_147 import PACKS
OUTS = {"RP-06": Path("/mnt/user-data/outputs/RP-06-AbsolutRealism-Hostile-Mobs-RP-v1_4_7.mcpack"), "RP-08": Path("/mnt/user-data/outputs/RP-08-AbsolutRealism-Items-RP-v1_4_7.mcpack")}
RP7 = ROOT / "_build/rp07-1412"
res = []

def check(name, ok, detail=""):
    res.append((name, bool(ok), detail)); print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))

def md5b(b): return hashlib.md5(b).hexdigest()
def jl(text): return json.loads(re.sub(r"^\s*//.*$", "", text.lstrip("﻿"), flags=re.M))

rp7_geos, rp7_tex = set(), set()
for p in glob.glob(str(RP7 / "models/entity/*.json")):
    try:
        j = jl(Path(p).read_text(encoding="utf-8"))
        for g in j.get("minecraft:geometry", []): rp7_geos.add(g["description"]["identifier"])
        rp7_geos |= {k for k in j if k.startswith("geometry.")}
    except Exception: pass
for p in (RP7 / "textures").rglob("*"):
    if p.is_file(): rp7_tex.add(str(p.relative_to(RP7)).replace(os.sep, "/").rsplit(".", 1)[0])

def orphans_of(entities, geos, texs):
    """entities: {name: description}; returns the geometry/texture refs that resolve neither in-pack nor in RP-07 1.4.12."""
    out = []
    for name, d in entities.items():
        for g in (d.get("geometry") or {}).values():
            if g not in geos and g not in rp7_geos: out.append(f"{name}:geo:{g}")
        for t in (d.get("textures") or {}).values():
            if t not in texs and t not in rp7_tex: out.append(f"{name}:tex:{t}")
    return set(out)

def census_zip(zpath):
    geos, texs, ents = set(), set(), {}
    with zipfile.ZipFile(zpath) as z:
        for n in z.namelist():
            if n.startswith("models/entity/") and n.endswith(".json"):
                try:
                    j = jl(z.read(n).decode("utf-8"))
                    for g in j.get("minecraft:geometry", []): geos.add(g["description"]["identifier"])
                    geos |= {k for k in j if k.startswith("geometry.")}
                except Exception: pass
            elif n.startswith("textures/") and not n.endswith("/"):
                texs.add(n.rsplit(".", 1)[0])
            elif n.startswith("entity/") and n.endswith(".json"):
                try: ents[os.path.basename(n)] = jl(z.read(n).decode("utf-8"))["minecraft:client_entity"]["description"]
                except Exception: pass
    return geos, texs, ents

for pk, cfg in PACKS.items():
    dst = cfg["dst"]
    with zipfile.ZipFile(cfg["src"]) as z:
        old = {n: md5b(z.read(n)) for n in z.namelist() if not n.endswith("/")}
    new = {str(p.relative_to(dst)).replace(os.sep, "/"): md5b(p.read_bytes()) for p in dst.rglob("*") if p.is_file()}
    mo = jl(zipfile.ZipFile(cfg["src"]).read("manifest.json").decode("utf-8")); mn = jl((dst / "manifest.json").read_text(encoding="utf-8"))
    check(f"A {pk} manifest 1.4.7, name, uuids unchanged", mn["header"]["version"] == [1, 4, 7] and mn["header"]["name"] == cfg["name"] and mn["header"]["uuid"] == mo["header"]["uuid"]
          and [m["uuid"] for m in mn["modules"]] == [m["uuid"] for m in mo["modules"]] and all(m["version"] == [1, 4, 7] for m in mn["modules"]) and mn["header"]["description"].startswith("v1.4.7 (2026-09-27)"))
    bad = []
    for p in dst.rglob("*.json"):
        try: jl(p.read_text(encoding="utf-8"))
        except Exception as e: bad.append(f"{p.relative_to(dst)}: {str(e)[:40]}")
    check(f"B {pk} every JSON parses", not bad, "; ".join(bad[:3]))
    removed = sorted(set(old) - set(new)); added = sorted(set(new) - set(old)); changed = sorted(k for k in set(old) & set(new) if old[k] != new[k])
    expected_removed = sorted(r for r in cfg["purge"] if r in old)
    check(f"C {pk} diff = purge list removed, manifest/textures_list/PW-DEPENDENCIES changed, nothing added",
          removed == expected_removed and not added and set(changed) <= {"manifest.json", "textures/textures_list.json", "PW-DEPENDENCIES.md"},
          f"removed {len(removed)} (expected {len(expected_removed)}), added {added[:3]}, changed {changed}")
    left = [r for r in cfg["purge"] if (dst / r).exists()]
    neutral_paths = [n for n in new if n.startswith("entity/") and (RP7 / n).exists() and pk == "RP-08"]   # an Items pack ships no client entities RP-07 owns
    pw_paths = [n for n in new if "/pw_" in n and (n.startswith("models/entity/pw_") or n.startswith("textures/entity/pw_"))]
    check(f"D {pk} no purged path remains; no RP-07 pw_ neutral path shipped", not left and not neutral_paths and not pw_paths, f"left {left} neutral {neutral_paths[:3]} pw {pw_paths[:3]}")
    # E orphans: only NEW orphans count (the sf_nba base already had unresolved refs in 1.4.6 — not this build's doing)
    geos, texs, ents = set(), set(), {}
    for p in (dst / "models/entity").glob("*.json"):
        try:
            j = jl(p.read_text(encoding="utf-8"))
            for g in j.get("minecraft:geometry", []): geos.add(g["description"]["identifier"])
            geos |= {k for k in j if k.startswith("geometry.")}
        except Exception: pass
    for p in (dst / "textures").rglob("*"):
        if p.is_file(): texs.add(str(p.relative_to(dst)).replace(os.sep, "/").rsplit(".", 1)[0])
    for p in dst.glob("entity/*.json"):
        try: ents[p.name] = jl(p.read_text(encoding="utf-8"))["minecraft:client_entity"]["description"]
        except Exception: pass
    ids = {d.get("identifier") for d in ents.values()}
    og, ot, oe = census_zip(cfg["src"])
    before, after = orphans_of(oe, og, ot), orphans_of(ents, geos, texs)
    new_orphans = sorted(after - before)
    check(f"E {pk} no client entity newly orphaned by the purge (geometry/texture resolves in-pack or in RP-07 1.4.12)", not new_orphans, f"{len(ids)} entities; pre-existing unresolved refs {len(before)} (sf_nba base), new {new_orphans[:6]}")
    if pk == "RP-06":
        check("E RP-06 no longer defines minecraft:zombie_pigman (RP-07 1.4.12 owns it)", "minecraft:zombie_pigman" not in ids)

ok = all(o for _, o, _ in res)
stamps = []
if ok:
    for pk, cfg in PACKS.items():
        out = OUTS[pk]
        if out.exists(): out.unlink()
        n = 0
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(cfg["dst"].rglob("*")):
                if p.is_file(): z.write(p, str(p.relative_to(cfg["dst"])).replace(os.sep, "/")); n += 1
        with zipfile.ZipFile(out) as z: badz = z.testzip()
        md5 = hashlib.md5(out.read_bytes()).hexdigest()
        check(f"P {pk} package", badz is None, f"{out.name} {n} members {out.stat().st_size:,} B md5 {md5}")
        stamps.append(f"{pk} 1.4.7 {out.stat().st_size:,} B md5 {md5}")
stamp = f"RP-06/RP-08 1.4.7 GATE {'OPEN' if all(o for _, o, _ in res) else 'CLOSED'} {sum(1 for _, o, _ in res if o)}/{len(res)}" + (" -> " + " · ".join(stamps) if stamps else "")
with open(ROOT / "_logs/phase_log.md", "a") as fh: fh.write(f"[{time.strftime('%H:%M')} CT 09-27] VERIFY {stamp}\n")
print(stamp); sys.exit(0 if all(o for _, o, _ in res) else 1)
