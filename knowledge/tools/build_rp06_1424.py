#!/usr/bin/env python3
"""build_rp06_1424.py — RP-06 Hostile Mobs RP v1.4.24 from v1.4.23 (R17, his 11:05 "GO all"; journal D-C317 / D-C318).

THE VEX HELD-ITEM PROBE. His p12 h01 / h02: the vex holds the sword / shard (the rig's log proves it: "CONFIRMED in vex's main hand")
but draws nothing. Census D-C317: of the 10 entities with a rightItem bone, 9 draw their item; every humanoid among them carries a
bone named `rightArm` (Mojang's name) in the item's chain, the allay (which draws) hangs rightItem on `body`, and the vex is the only
one whose Mojang geometry HAS rightArm (geometry.vex.v1.8) while ours calls it `right_arm`. Two candidates, one build:
  A (held SWORD, or nothing)   geometry.pw_vex_probe_a = ours with right_arm / left_arm renamed rightArm / leftArm (Mojang's names);
                                the JEM animation drives both spellings, so the arms move the same
  B (held AMETHYST SHARD)      geometry.pw_vex_probe_b = ours with rightItem / leftItem moved under `body` (the allay's arrangement),
                                same rest position and orientation as before (they no longer follow the arm swing: probe only)
The entity picks the geometry by what is in its main hand (v.pw_vx_probe, set in pre_animation) through its own render controller.
p14 v01 (sword) / v02 (shard) -> whichever draws names the cause. geometry.pw_vex stays in the pack (the fix build returns to one
geometry). Everything else byte-identical to 1.4.23. verify: verify_rp06_1424.py"""
import copy, json, shutil, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import molang_lint as ML
import wing_contact as WC

ROOT = Path("/home/claude")
SRC, DST, VER = ROOT / "_build/rp06-1423", ROOT / "_build/rp06-1424", "1.4.24"
RENAME = {"right_arm": "rightArm", "left_arm": "leftArm"}
PROBE_VAR = "v.pw_vx_probe = q.is_item_name_any('slot.weapon.mainhand', 'minecraft:amethyst_shard') ? 1.0 : 0.0;"
RC_ID = "controller.render.pw_vex_probe"


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT {time.strftime('%m-%d')}] BUILD rp06-1424: {m}\n")


def probe_a(g):
    g = copy.deepcopy(g); g["description"]["identifier"] = "geometry.pw_vex_probe_a"
    for b in g["bones"]:
        b["name"] = RENAME.get(b["name"], b["name"])
        if b.get("parent") in RENAME: b["parent"] = RENAME[b["parent"]]
    return g


def probe_b(g):
    """rightItem / leftItem under body with the same rest world pivot + orientation (computed, then proven equal)"""
    g = copy.deepcopy(g); g["description"]["identifier"] = "geometry.pw_vex_probe_b"
    before = WC.affines(g["bones"], {})
    by = {b["name"]: b for b in g["bones"]}
    world0 = {}
    for item, arm in (("rightItem", "right_arm"), ("leftItem", "left_arm")):
        b = by[item]; A0, t0 = before[item]
        world0[item] = A0 @ np.array(b["pivot"], float) + t0            # its world pivot at rest
        Ab, tb = before["body"]
        b["parent"] = "body"
        b["pivot"] = [round(float(x), 4) for x in np.linalg.solve(Ab, world0[item] - tb)]
        b["rotation"] = [float(x) for x in by[arm].get("rotation", [0, 0, 0])]   # body * arm = the old chain's orientation
    after = WC.affines(g["bones"], {})
    for item in ("rightItem", "leftItem"):
        A1, t1 = after[item]; A0, _ = before[item]
        w1 = A1 @ np.array(by[item]["pivot"], float) + t1
        assert float(np.abs(A1 - A0).max()) < 1e-6, f"{item} orientation moved"
        assert float(np.abs(w1 - world0[item]).max()) < 1e-3, f"{item} pivot moved {w1} vs {world0[item]}"
    return g


def main():
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    p, g = R.geo_file(DST, "geometry.pw_vex")
    ga, gb = probe_a(g), probe_b(g)
    d = R.jl(p); fmt = d.get("format_version", "1.16.0")
    R.wj(DST / "models/entity/pw_vex_probe_a.geo.json", {"format_version": fmt, "minecraft:geometry": [ga]})
    R.wj(DST / "models/entity/pw_vex_probe_b.geo.json", {"format_version": fmt, "minecraft:geometry": [gb]})
    log("geometry.pw_vex_probe_a (arms named rightArm / leftArm) + geometry.pw_vex_probe_b (hand bones under body)")
    # the JEM animation drives both arm spellings (a bone missing from the current geometry is skipped by the engine)
    ap = DST / "animations/pw_vex.animation.json"; a = R.jl(ap); an = a["animations"]["animation.pw_vex.jem"]["bones"]
    for old, new in RENAME.items():
        assert old in an and new not in an
        an[new] = copy.deepcopy(an[old])
    R.wj(ap, a)
    # render controller: vanilla vex's textures (charging) + the geometry by held item
    rc = {"format_version": "1.10.0", "render_controllers": {RC_ID: {
        "arrays": {"textures": {"Array.textures": ["Texture.default", "Texture.charging"]},
                   "geometries": {"Array.geos": ["Geometry.probe_a", "Geometry.probe_b"]}},
        "geometry": "Array.geos[v.pw_vx_probe ?? 0.0]", "materials": [{"*": "Material.default"}],
        "textures": ["Array.textures[query.is_charging]"], "ignore_lighting": True}}}
    R.wj(DST / "render_controllers/pw_vex_probe.render.json", rc)
    pe = DST / "entity/vex.entity.json"; v = ML._parse_json(pe.read_text(encoding="utf-8")); desc = v["minecraft:client_entity"]["description"]
    desc["geometry"] = {"default": "geometry.pw_vex", "probe_a": "geometry.pw_vex_probe_a", "probe_b": "geometry.pw_vex_probe_b"}
    desc["render_controllers"] = [RC_ID]
    desc["scripts"]["pre_animation"] = [PROBE_VAR] + list(desc["scripts"]["pre_animation"])
    R.wj(pe, v)
    log(f"vex entity: geometry by held item ({RC_ID}); pre_animation +1 (v.pw_vx_probe)")
    mp = DST / "manifest.json"; m = R.jl(mp); vv = [int(x) for x in VER.split(".")]
    m["header"]["version"] = vv
    for mod in m["modules"]: mod["version"] = vv
    m["header"]["name"] = f"AbsolutRealism Hostile Mobs RP v{VER}"
    m["header"]["description"] = (f"v{VER} (2026-09-30) PROBE: the vex tries two ways of holding its item (sword: Mojang's arm names; "
                                  "amethyst shard: the item hung on the body like the allay). Includes all of 1.4.23.")
    R.wj(mp, m)
    log(f"manifest {VER}")


if __name__ == "__main__":
    main()
