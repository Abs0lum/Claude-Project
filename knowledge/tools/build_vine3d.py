#!/usr/bin/env python3
"""build_vine3d.py — ROUND 1002e: 3D vines (his 09:30 Q1 = a: swap once, scripted climbing, vines stop spreading).
Geometry: the 12 Patrix 26.2 vine models; for each vanilla vine_direction_bits value (Bedrock: 1 south, 2 west,
4 north, 8 east; 0 = hanging from the block above) the Patrix blockstate's model + Java 'y' turn is BAKED into its own
geometry by rotating the Java elements in Java space (clockwise from above: (x, z) -> (16 - z, x); x-axis tilts become
z-axis tilts, z-axis tilts become x-axis tilts with the sign flipped; faces north->east->south->west->north), then
converted with the witnessed Blockbench Java->Bedrock mapping (java_leaf_study.java_to_bedrock). No engine-side
transformation is used for direction (one less sign convention to trust).
Bits 0 uses Patrix vine_u (flat under the block above).
BP-02 1.3.202 (from 1.3.201): blocks/pw_vine.json (pw:bits 0-15 -> geometry, pw:v 0-11 -> texture), loot (shears ->
  vanilla vine), scripts/pw_vine.js (swap once + climbing), main.js import, PW_BUILD 1.3.202.
RP-01 1.3.113 (from 1.3.112): models/blocks/pw_vine_b<bits>.geo.json x16, textures/blocks/pw_vine/ (our 12 vine 256
  colours + maps copied from RP-04 so key, image and set are in one pack; Patrix vine_extra graded to our vine colour +
  its maps), keys pw_vine_v0..11 + pw_vine_extra, blocks.json sound, en_US name.
Materials: '*' = the variant's vine tile, 'extra' = vine_extra; alpha_test, tint default_foliage (vanilla vines are
foliage-tinted), no AO, no face dimming (Java shade:false)."""
import copy
import io
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import java_leaf_study as J  # noqa: E402
import mers_derive as MD  # noqa: E402
import molang_lint as ML  # noqa: E402
import pbr_round as PR  # noqa: E402
import tier_round as TR  # noqa: E402

B = ROOT / "_build"
BP_SRC, BP_DST, BP_VER = B / "bp02-201", B / "bp02-202", [1, 3, 202]
RP_SRC, RP_DST, RP_VER = B / "rp01-112", B / "rp01-113", [1, 3, 113]
VINE_SRC = B / "rp04-150/textures/blocks"
FACE_CW = {"north": "east", "east": "south", "south": "west", "west": "north", "up": "up", "down": "down"}


def rot_cw(el):
    """one clockwise quarter turn (seen from above) of a Java element about the block centre."""
    e = copy.deepcopy(el)
    fr, to = el["from"], el["to"]
    e["from"] = [16 - to[2], fr[1], fr[0]]
    e["to"] = [16 - fr[2], to[1], to[0]]
    r = el.get("rotation")
    if r:
        ox, oy, oz = r["origin"]
        nr = dict(r)
        nr["origin"] = [16 - oz, oy, ox]
        if r["axis"] == "x":
            nr["axis"] = "z"
        elif r["axis"] == "z":
            nr["axis"], nr["angle"] = "x", -r["angle"]
        e["rotation"] = nr
    e["faces"] = {FACE_CW[k]: v for k, v in el["faces"].items()}
    return e


def model_for_bits(Z, bits):
    if bits == 0:
        return json.loads(Z.read("assets/minecraft/models/block/vine_u.json")), "vine_u", 0
    s, w, n, e = bool(bits & 1), bool(bits & 2), bool(bits & 4), bool(bits & 8)
    key = f"east={str(e).lower()},north={str(n).lower()},south={str(s).lower()},up=false,west={str(w).lower()}"
    bs = json.loads(Z.read("assets/minecraft/blockstates/vine.json"))["variants"][key]
    name = bs["model"].split("/")[-1]
    m = json.loads(Z.read(f"assets/minecraft/models/block/{name}.json"))
    turns = (bs.get("y", 0) // 90) % 4
    for _ in range(turns):
        m["elements"] = [rot_cw(x) for x in m["elements"]]
    return m, name, bs.get("y", 0)


def jl(p):
    return json.loads(re.sub(r"(?m)^\s*//.*$", "", p.read_text(encoding="utf-8-sig")))


def bump(man, ver, desc):
    m = jl(man)
    old = ".".join(map(str, m["header"]["version"]))
    m["header"]["version"] = ver
    for mod in m["modules"]:
        mod["version"] = ver
    vs = ".".join(map(str, ver))
    m["header"]["name"] = re.sub(r"v\d+\.\d+\.\d+", "v" + vs, m["header"]["name"])
    m["header"]["description"] = f"v{vs} (2026-10-02) {desc} Includes all of v{old}."
    man.write_text(json.dumps(m, indent=2))
    return m


def main():
    assert not BP_DST.exists() and not RP_DST.exists(), "never rebuild a build dir"
    Z = zipfile.ZipFile(PR.PATRIX256)
    shutil.copytree(BP_SRC, BP_DST)
    shutil.copytree(RP_SRC, RP_DST)
    # ---- RP: geometry
    md = RP_DST / "models/blocks"
    md.mkdir(parents=True, exist_ok=True)
    report = {}
    for bits in range(16):
        m, name, y = model_for_bits(Z, bits)
        bones = J.java_to_bedrock(m, {"#vine": 0, "#cross": 0, "#extra": 0}, mat_names={"#extra": "extra"})
        lo, hi, size = J.bounds(bones, 16, 16)
        assert max(size) <= 30, (bits, size)
        geo = {"format_version": "1.12.0", "minecraft:geometry": [{
            "description": {"identifier": f"geometry.pw_vine_b{bits}", "texture_width": 16, "texture_height": 16,
                            "visible_bounds_width": 2, "visible_bounds_height": 2.5, "visible_bounds_offset": [0, 0.75, 0]},
            "bones": bones}]}
        (md / f"pw_vine_b{bits}.geo.json").write_text(json.dumps(geo, indent=1))
        report[bits] = {"model": name, "java_y": y, "cubes": len(bones[0]["cubes"]), "size_px": size}
    # ---- RP: textures (ownership: copies of our vine tiles + the extra card)
    td = RP_DST / "textures/blocks/pw_vine"
    td.mkdir(parents=True)
    keys = {}
    for i in range(12):
        for suf in ("", "_n256", "_mer256"):
            shutil.copy2(VINE_SRC / f"vine_v{i}{suf}.png", td / f"vine_v{i}{suf}.png")
        (td / f"vine_v{i}.texture_set.json").write_text(json.dumps({"format_version": "1.21.30", "minecraft:texture_set": {
            "color": f"vine_v{i}", "normal": f"vine_v{i}_n256", "metalness_emissive_roughness_subsurface": f"vine_v{i}_mer256"}},
            indent=1))
        keys[f"pw_vine_v{i}"] = {"textures": f"textures/blocks/pw_vine/vine_v{i}"}
    ours = np.asarray(Image.open(VINE_SRC / "vine_v0.png").convert("RGBA"))
    ex = np.asarray(Image.open(io.BytesIO(Z.read("assets/minecraft/textures/block/extra/vine_extra.png"))).convert("RGBA"))
    Image.fromarray(TR.grade_match(ex, ours), "RGBA").save(td / "vine_extra.png")
    Image.fromarray(MD.normal_156(np.asarray(Image.open(io.BytesIO(
        Z.read("assets/minecraft/textures/block/extra/vine_extra_n.png"))).convert("RGBA"))), "RGBA").save(td / "vine_extra_n.png")
    Image.fromarray(MD.mers_156(np.asarray(Image.open(io.BytesIO(
        Z.read("assets/minecraft/textures/block/extra/vine_extra_s.png"))).convert("RGBA"))), "RGBA").save(td / "vine_extra_mer.png")
    (td / "vine_extra.texture_set.json").write_text(json.dumps({"format_version": "1.21.30", "minecraft:texture_set": {
        "color": "vine_extra", "normal": "vine_extra_n", "metalness_emissive_roughness_subsurface": "vine_extra_mer"}}, indent=1))
    assert Image.open(td / "vine_extra.png").size[0] == Image.open(td / "vine_extra.png").size[1]
    keys["pw_vine_extra"] = {"textures": "textures/blocks/pw_vine/vine_extra"}
    tp = RP_DST / "textures/terrain_texture.json"
    t = jl(tp)
    assert not set(keys) & set(t["texture_data"])
    t["texture_data"].update(keys)
    tp.write_text(json.dumps(t, indent=1))
    bj = RP_DST / "blocks.json"
    b = jl(bj)
    b["pw:vine"] = {"sound": "vines"}
    bj.write_text(json.dumps(b, indent=1))
    lp = RP_DST / "texts/en_US.lang"
    ls = lp.read_text(encoding="utf-8")
    lp.write_text(ls + ("" if ls.endswith("\n") else "\n") + "tile.pw:vine.name=Vines\n", encoding="utf-8")
    bump(RP_DST / "manifest.json", RP_VER, "3D vines: Patrix vine leaf-card models for every vine attachment (16 geometries) "
         "+ the 12 vine 256 tiles and Patrix vine_extra with depth + shine, for BP-02 1.3.202 pw:vine.")
    # ---- BP: block
    def mi(v):
        base = {"render_method": "alpha_test", "tint_method": "default_foliage", "ambient_occlusion": False,
                "face_dimming": False}
        return {"*": {"texture": f"pw_vine_v{v}", **base}, "extra": {"texture": "pw_vine_extra", **base}}
    perms = [{"condition": f"q.block_state('pw:bits') == {bits}",
              "components": {"minecraft:geometry": f"geometry.pw_vine_b{bits}"}} for bits in range(16)]
    perms += [{"condition": f"q.block_state('pw:v') == {v}",
               "components": {"minecraft:material_instances": mi(v)}} for v in range(12)]
    bad = [p["condition"] for p in perms if ML.check(p["condition"])]
    assert not bad, bad
    blk = {"format_version": "1.21.80", "minecraft:block": {
        "description": {"identifier": "pw:vine", "menu_category": {"category": "none"},
                        "states": {"pw:bits": list(range(16)), "pw:v": list(range(12))}},
        "components": {
            "minecraft:geometry": "geometry.pw_vine_b1",
            "minecraft:material_instances": mi(0),
            "minecraft:collision_box": False,
            "minecraft:selection_box": {"origin": [-8, 0, -8], "size": [16, 16, 16]},
            "minecraft:light_dampening": 0,
            "minecraft:destructible_by_mining": {"seconds_to_destroy": 0.2},
            "minecraft:destructible_by_explosion": {"explosion_resistance": 0.2},
            "minecraft:flammable": {"catch_chance_modifier": 15, "destroy_chance_modifier": 100},
            "minecraft:loot": "loot_tables/blocks/pw_vine.json",
            "minecraft:map_color": "#4a7a27",
            "minecraft:display_name": "tile.pw:vine.name",
            "minecraft:replaceable": {},
        },
        "permutations": perms}}
    (BP_DST / "blocks/pw_vine.json").write_text(json.dumps(blk, indent=1))
    (BP_DST / "loot_tables/blocks/pw_vine.json").write_text(json.dumps({"pools": [{"rolls": 1, "entries": [
        {"type": "item", "name": "minecraft:vine", "weight": 1}],
        "conditions": [{"condition": "match_tool", "item": "minecraft:shears"}]}]}, indent=1))
    shutil.copy2(ROOT / "_staging/vine3d/pw_vine.js", BP_DST / "scripts/pw_vine.js")
    mp = BP_DST / "scripts/main.js"
    s = mp.read_text(encoding="utf-8")
    anchor = 'import "./pw_planks.js";'
    assert s.count(anchor) == 1 and "pw_vine.js" not in s
    s = s.replace(anchor, 'import "./pw_vine.js"; // v1.3.202: 3D vines, swap once + scripted climbing (his Q1 = a, 10-02)\n' + anchor, 1)
    assert s.count('const PW_BUILD = "1.3.201";') == 1
    s = s.replace('const PW_BUILD = "1.3.201";', 'const PW_BUILD = "1.3.202";', 1)
    mp.write_text(s, encoding="utf-8")
    bump(BP_DST / "manifest.json", BP_VER, "3D vines: vanilla vines swap ONCE to pw:vine (Patrix leaf-card models, 12 "
         "variants); climb by holding jump, sneak to hold, slow safe descent; swapped vines no longer spread.")
    (ROOT / "_docs/vines").mkdir(parents=True, exist_ok=True)
    (ROOT / "_docs/vines/BUILD-VINE3D.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report))


if __name__ == "__main__":
    main()
