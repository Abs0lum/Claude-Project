#!/usr/bin/env python3
"""build_rp06_148.py — RP-06 Hostile Mobs RP v1.4.8: the HOSTILE WIRING build (D-C263, Abs0lum 23:28 "this all needs to be fixed").
The stack census showed eight RP-06 client entities pointing at VANILLA geometry ids (geometry.zombie.v1.8, geometry.skeleton.v1.8,
geometry.zombie.drowned.v1.16, geometry.zombie.husk.v1.8, geometry.pillager, geometry.skeleton.stray.v1.8, geometry.vindicator.v1.8,
geometry.witch) while their converted Patrix geometries (geometry.<mob>.patrix, Bedrock humanoid bone names + articulated forearms/
shins) sat unused — the same M1 wiring fault RP-07 had before 1.4.12.  v1.4.8, for drowned · husk · pillager · skeleton · stray ·
vindicator · witch · zombie:
  - models/entity/pw_<mob>.geo.json = the .patrix geometry under the unshadowable id geometry.pw_<mob> (L-ENT-SHADOW)
  - entity: geometry.default -> geometry.pw_<mob>; material default -> entity_alphatest (the Patrix models carry alpha-cut planes);
    min_engine_version -> 1.21.0 (so our definition outranks vanilla's, as the cow/RP-07 1.4.12 pattern); animations, render
    controllers, textures and scripts untouched (the third-party animation sets target the vanilla humanoid bone names the .patrix
    geometries use; the stray keeps its vanilla overlay geometry + clothes controller)
Everything else byte-identical to v1.4.7 (the gate asserts the diff)."""
import copy, json, re, shutil, time
from pathlib import Path
ROOT = Path("/home/claude"); SRC, DST, VER, DATE = ROOT / "_build/rp06-147", ROOT / "_build/rp06-148", "1.4.8", "2026-09-27"
MOBS = ["drowned", "husk", "pillager", "skeleton", "stray", "vindicator", "witch", "zombie"]
def jl(p): return json.loads(re.sub(r"^\s*//.*$", "", Path(p).read_text(encoding="utf-8-sig"), flags=re.M))
def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT 09-27] BUILD {m}\n")
if DST.exists(): shutil.rmtree(DST)
shutil.copytree(SRC, DST)
report = {"geometries": [], "entities": []}
for mob in MOBS:
    j = jl(DST / f"models/entity/{mob}.geo.json")
    g = next(g for g in j["minecraft:geometry"] if g["description"]["identifier"] == f"geometry.{mob}.patrix")
    g = copy.deepcopy(g); g["description"]["identifier"] = f"geometry.pw_{mob}"
    (DST / f"models/entity/pw_{mob}.geo.json").write_text(json.dumps({"format_version": j.get("format_version", "1.12.0"), "minecraft:geometry": [g]}, indent=1), encoding="utf-8")
    report["geometries"].append(f"pw_{mob} <- geometry.{mob}.patrix ({len(g['bones'])} bones, tex {g['description'].get('texture_width')}x{g['description'].get('texture_height')})")
    ep = DST / f"entity/{mob}.entity.json"; e = jl(ep); d = e["minecraft:client_entity"]["description"]
    before = dict(geometry=dict(d["geometry"]), mev=d.get("min_engine_version"), mat=dict(d["materials"]))
    d["geometry"]["default"] = f"geometry.pw_{mob}"
    d["materials"]["default"] = "entity_alphatest"
    d["min_engine_version"] = "1.21.0"
    # M1 texture-path faults found on the way: the Patrix skins were in the pack, the entities pointed at RP-07's vanilla files
    REMAP = {"vindicator": {"default": "textures/entity/illager/vindicator"},     # 512x512 (was textures/entity/vindicator, 64x64 in RP-07)
             "witch": {"default": "textures/entity/witch"}}                       # 512x1024 (was textures/entity/witch.v2, 64x128 in RP-07)
    for k, v in REMAP.get(mob, {}).items():
        before.setdefault("tex", {})[k] = d["textures"].get(k); d["textures"][k] = v
    ep.write_text(json.dumps(e, indent=1), encoding="utf-8")
    report["entities"].append({"mob": mob, "before": before, "after": dict(geometry=d["geometry"], mev="1.21.0", mat=d["materials"])})
man = jl(DST / "manifest.json"); v = [1, 4, 8]
man["header"]["version"] = v
for m in man["modules"]: m["version"] = v
man["header"]["name"] = f"AbsolutRealism Hostile Mobs RP v{VER}"
man["header"]["description"] = (f"v{VER} ({DATE}) HOSTILE WIRING (D-C263): drowned, husk, pillager, skeleton, stray, vindicator, witch and zombie now draw their "
                                "converted Patrix geometries (geometry.pw_<mob>, unshadowable copies of the .patrix files that sat unused) on entity_alphatest with "
                                "min_engine_version 1.21.0; the vindicator and witch entities now point at the Patrix skins already in this pack (illager/vindicator 512x512, witch 512x1024) instead of RP-07's vanilla files; animations and controllers unchanged. Everything else byte-identical to v1.4.7.")
(DST / "manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
json.dump(report, open(ROOT / "_logs/rp06_148_build_report.json", "w"), indent=1)
log(f"RP-06 v{VER}: 8 hostile entities rewired to geometry.pw_<mob> (entity_alphatest, mev 1.21.0); manifest stamped -> {DST}")
