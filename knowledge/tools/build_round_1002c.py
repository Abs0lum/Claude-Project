#!/usr/bin/env python3
"""build_round_1002c.py — ROUND 1002c: Patrix 4 x 4 plank grids, 11 species (his 00:07 / 00:53).
BP-02 1.3.201 (from 1.3.200):
  blocks/pw_planks_grid_<species>.json  pw:<species>_planks_grid, states pw:gx/gy/gz (position mod 4, written once),
      64 permutations -> per-face tile; drops the vanilla plank; flammable except crimson / warped
  loot_tables/blocks/pw_planks_<species>.json
  scripts/pw_planks.js (swap ONCE: on placement + scanner near players) imported by main.js; PW_BUILD 1.3.201
RP-04 1.3.149 (from 1.3.148): textures/blocks/pw_planks/* (176 tiles + maps, _staging/planks), terrain keys
  pw_planks_<species>_<n>, blocks.json sound 'wood' for the 11 blocks, en_US.lang names.
Face -> tile (Patrix 'repeat' 4 x 4, tile = 1 + col + 4*row, row 0 = top of the picture), seen from outside the face:
  up    col = gx           row = gz
  down  col = gx           row = (4 - gz) % 4
  south col = gx           row = (4 - gy) % 4        (+z face, viewer looks north: right = east)
  north col = (4 - gx) % 4 row = (4 - gy) % 4        (-z face, right = west)
  east  col = (4 - gz) % 4 row = (4 - gy) % 4        (+x face, right = north)
  west  col = gz           row = (4 - gy) % 4        (-x face, right = south)
Block above -> row - 1 (boards continue upward); block to the viewer's right -> col + 1."""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import molang_lint as ML  # noqa: E402

B = ROOT / "_build"
SPECIES = ["oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "mangrove", "cherry", "pale_oak", "crimson", "warped"]
NAMES = {"oak": "Oak", "spruce": "Spruce", "birch": "Birch", "jungle": "Jungle", "acacia": "Acacia", "dark_oak": "Dark Oak",
         "mangrove": "Mangrove", "cherry": "Cherry", "pale_oak": "Pale Oak", "crimson": "Crimson", "warped": "Warped"}
MAPCOL = {"oak": "#8f7748", "spruce": "#815a35", "birch": "#d7cb8d", "jungle": "#976d4d", "acacia": "#d87f33",
          "dark_oak": "#664c33", "mangrove": "#993333", "cherry": "#e3b4ad", "pale_oak": "#e4d9d4", "crimson": "#943f61",
          "warped": "#3a8e8c"}
BP_SRC, BP_DST, BP_VER = B / "bp02-200", B / "bp02-201", [1, 3, 201]
RP_SRC, RP_DST, RP_VER = B / "rp04-148", B / "rp04-149", [1, 3, 149]


def jl(p):
    return json.loads(re.sub(r"(?m)^\s*//.*$", "", p.read_text(encoding="utf-8-sig")))


def tile(sp, col, row):
    return f"pw_planks_{sp}_{1 + col + 4 * row}"


def faces(sp, gx, gy, gz):
    r = (4 - gy) % 4
    def mi(t):
        return {"texture": t, "render_method": "opaque"}
    return {"up": mi(tile(sp, gx, gz)), "down": mi(tile(sp, gx, (4 - gz) % 4)),
            "south": mi(tile(sp, gx, r)), "north": mi(tile(sp, (4 - gx) % 4, r)),
            "east": mi(tile(sp, (4 - gz) % 4, r)), "west": mi(tile(sp, gz, r))}


def block(sp):
    comps = {
        "minecraft:geometry": "minecraft:geometry.full_block",
        "minecraft:material_instances": faces(sp, 0, 0, 0),
        "minecraft:destructible_by_mining": {"seconds_to_destroy": 2.0},
        "minecraft:destructible_by_explosion": {"explosion_resistance": 3},
        "minecraft:loot": f"loot_tables/blocks/pw_planks_{sp}.json",
        "minecraft:map_color": MAPCOL[sp],
        "minecraft:display_name": f"tile.pw:{sp}_planks_grid.name",
        "tag:wood": {},
        "tag:minecraft:is_axe_item_destructible": {},
    }
    if sp not in ("crimson", "warped"):
        comps["minecraft:flammable"] = {"catch_chance_modifier": 5, "destroy_chance_modifier": 20}
    perms = []
    for gx in range(4):
        for gy in range(4):
            for gz in range(4):
                perms.append({"condition": f"q.block_state('pw:gx') == {gx} && q.block_state('pw:gy') == {gy} && "
                                           f"q.block_state('pw:gz') == {gz}",
                              "components": {"minecraft:material_instances": faces(sp, gx, gy, gz)}})
    return {"format_version": "1.21.80", "minecraft:block": {
        "description": {"identifier": f"pw:{sp}_planks_grid",
                        "menu_category": {"category": "none"},
                        "states": {"pw:gx": [0, 1, 2, 3], "pw:gy": [0, 1, 2, 3], "pw:gz": [0, 1, 2, 3]}},
        "components": comps, "permutations": perms}}


def bump(man, ver, name_ver, desc):
    m = jl(man)
    old = ".".join(map(str, m["header"]["version"]))
    m["header"]["version"] = ver
    for mod in m["modules"]:
        mod["version"] = ver
    m["header"]["name"] = re.sub(r"v\d+\.\d+\.\d+", "v" + name_ver, m["header"]["name"])
    m["header"]["description"] = f"v{name_ver} (2026-10-02) {desc} Includes all of v{old}."
    man.write_text(json.dumps(m, indent=2))
    return m


def main():
    assert not BP_DST.exists() and not RP_DST.exists(), "never rebuild a build dir"
    shutil.copytree(BP_SRC, BP_DST)
    shutil.copytree(RP_SRC, RP_DST)
    # ---- BP
    lt = BP_DST / "loot_tables/blocks"
    lt.mkdir(parents=True, exist_ok=True)
    lint_fail = 0
    for sp in SPECIES:
        d = block(sp)
        for p in d["minecraft:block"]["permutations"]:
            errs = ML.check(p["condition"])
            lint_fail += 1 if errs else 0
        (BP_DST / f"blocks/pw_planks_grid_{sp}.json").write_text(json.dumps(d, indent=1))
        (lt / f"pw_planks_{sp}.json").write_text(json.dumps({"pools": [{"rolls": 1, "entries": [
            {"type": "item", "name": f"minecraft:{sp}_planks", "weight": 1}]}]}, indent=1))
    shutil.copy2(ROOT / "_staging/planks/pw_planks.js", BP_DST / "scripts/pw_planks.js")
    mp = BP_DST / "scripts/main.js"
    s = mp.read_text(encoding="utf-8")
    anchor = 'import "./pw_mob_light.js";'
    assert s.count(anchor) == 1 and 'pw_planks.js' not in s
    s = s.replace(anchor, 'import "./pw_planks.js"; // v1.3.201: Patrix 4x4 plank grids, swap once (his 00:53, 10-02)\n' + anchor, 1)
    assert s.count('const PW_BUILD = "1.3.200";') == 1
    s = s.replace('const PW_BUILD = "1.3.200";', 'const PW_BUILD = "1.3.201";', 1)
    mp.write_text(s, encoding="utf-8")
    bump(BP_DST / "manifest.json", BP_VER, "1.3.201",
         "Plank grids: vanilla planks of 11 species swap ONCE to pw:<species>_planks_grid showing Patrix's seamless 4x4 "
         "board pattern on every face; breaking drops the vanilla plank.")
    # ---- RP
    src = ROOT / "_staging/planks/rp04/textures/blocks/pw_planks"
    dst = RP_DST / "textures/blocks/pw_planks"
    shutil.copytree(src, dst)
    tp = RP_DST / "textures/terrain_texture.json"
    t = jl(tp)
    add = json.loads((ROOT / "_staging/planks/rp04/TERRAIN.json").read_text())
    assert not set(add) & set(t["texture_data"])
    t["texture_data"].update(add)
    tp.write_text(json.dumps(t, indent=1))
    bj = RP_DST / "blocks.json"
    b = jl(bj)
    for sp in SPECIES:
        b[f"pw:{sp}_planks_grid"] = {"sound": "wood"}
    bj.write_text(json.dumps(b, indent=1))
    lang = RP_DST / "texts/en_US.lang"
    ls = lang.read_text(encoding="utf-8")
    if not ls.endswith("\n"):
        ls += "\n"
    for sp in SPECIES:
        ls += f"tile.pw:{sp}_planks_grid.name={NAMES[sp]} Planks\n"
    lang.write_text(ls, encoding="utf-8")
    m = bump(RP_DST / "manifest.json", RP_VER, "1.3.149",
             "Plank grids: Patrix 256 planks, 16 tiles per species (11 species) with depth + shine maps, for the BP-02 "
             "1.3.201 grid blocks.")
    assert "pbr" in (m.get("capabilities") or [])
    print("BP-02 1.3.201 + RP-04 1.3.149 built; blocks", len(SPECIES), "perms", 64 * len(SPECIES),
          "tiles", len(list(dst.glob("*.texture_set.json"))), "lint fails", lint_fail)


if __name__ == "__main__":
    main()
