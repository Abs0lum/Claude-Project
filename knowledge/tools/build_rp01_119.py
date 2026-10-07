#!/usr/bin/env python3
"""build_rp01_119.py — RP-01 1.3.119 from the frozen 1.3.118 (never rebuilt): the CARBON-COPY falling tree (D-C524).

  * models/entity/ft_tpl/<template>.geo.json — one geometry per tree template (tools/ft_tpl_gen.py), leaf atlases per species
  * entity/falling_tree.json — 544 geometries + 9 leaf atlases + lift/turn animations; the three OLD render controllers now
    run only when ft:tpl < 0 (vanilla trees / BFS fallback keep the old model), three NEW ones when ft:tpl >= 0
  * render_controllers/ft_tpl.json — trunk (trunk texture), canopy (leaf atlas), collar; part_visibility hides the layers
    at or below the cut (ft:lift) — layer L shows when L >= ft:lift
  * animations/ft_tpl.animation.json — ft_lift_<k> (constant position, engine law: no q.property arithmetic in position
    channels) and ft_turn (rotation channel reads q.property('ft:turn'), like the existing fall animation reads fall_angle)
Usage: build_rp01_119.py [--planes=N]"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

B = Path("/home/claude/_build")
SRC, DST = B / "rp01-118", B / "rp01-119"
BP = B / "bp02-216"
MAX_LAYERS = 48
WOOD_LEAF = ["oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "mangrove", "cherry", "oak", "oak", "pale_oak", "oak"]


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    planes = next((a for a in sys.argv if a.startswith("--planes=")), "--planes=2")
    shutil.copytree(SRC, DST)
    r = subprocess.run([sys.executable, "/home/claude/tools/ft_tpl_gen.py", str(DST), str(BP), planes], capture_output=True, text=True)
    print(r.stdout[-1500:], r.stderr[-1500:])
    if r.returncode != 0:
        raise SystemExit("generator failed")
    index = json.loads(Path("/home/claude/_docs/fell/ft_tpl_index.json").read_text())
    names = [e["name"] for e in index]

    # ---------------------------------------------------------------- animations
    anims = {f"animation.ft_tpl.lift_{k}": {"loop": True, "bones": {"tlift": {"position": [0, -16 * k, 0]}}} for k in range(1, MAX_LAYERS)}
    anims["animation.ft_tpl.turn"] = {"loop": True, "bones": {"tturn": {"rotation": [0, "q.property('ft:turn')", 0]}}}
    (DST / "animations/ft_tpl.animation.json").write_text(json.dumps({"format_version": "1.10.0", "animations": anims}, indent=1))

    # ---------------------------------------------------------------- render controllers
    layer_vis = []
    for L in range(MAX_LAYERS):
        cond = f"q.property('ft:lift') <= {L}"
        layer_vis.append({f"w{L}": cond})
        layer_vis.append({f"l{L}_*": cond})
    geo_arr = {"Array.tpl_geos": [f"Geometry.tpl_{i}" for i in range(len(names))]}
    geo_expr = "Array.tpl_geos[q.property('ft:tpl')]"
    trunk_tex = json.loads((SRC / "render_controllers/falling_tree.json").read_text())["render_controllers"]["controller.render.ft_falling_tree"]
    collar_rc = json.loads((SRC / "render_controllers/falling_tree.json").read_text())["render_controllers"]["controller.render.ft_falling_tree_collar"]
    rcs = {
        "controller.render.ft_tpl_trunk": {
            "arrays": {"geometries": geo_arr, "textures": trunk_tex["arrays"]["textures"]},
            "geometry": geo_expr, "materials": [{"*": "Material.trunk"}], "textures": trunk_tex["textures"],
            "color": trunk_tex.get("color", {"r": "1", "g": "1", "b": "1"}),
            "part_visibility": [{"*": True}] + layer_vis + [{"l*": False}, {"break_collar": False}]},
        "controller.render.ft_tpl_canopy": {
            "arrays": {"geometries": geo_arr, "textures": {"Array.leaf_atlas": [f"Texture.leafatlas_{s}" for s in WOOD_LEAF]}},
            "geometry": geo_expr, "materials": [{"*": "Material.default"}],
            "textures": ["Array.leaf_atlas[q.property('ft:wood_type')]"],
            "part_visibility": [{"*": True}] + layer_vis + [{"w*": False}, {"break_collar": False}]},
        "controller.render.ft_tpl_collar": {
            "arrays": {"geometries": geo_arr, "textures": collar_rc["arrays"]["textures"]},
            "geometry": geo_expr, "materials": [{"*": "Material.default"}], "textures": collar_rc["textures"],
            "part_visibility": [{"*": False}, {"break_collar": True}]},
    }
    (DST / "render_controllers/ft_tpl.json").write_text(json.dumps({"format_version": "1.10.0", "render_controllers": rcs}, indent=1))

    # ---------------------------------------------------------------- client entity
    ep = DST / "entity/falling_tree.json"
    e = json.loads(ep.read_text())
    d = e["minecraft:client_entity"]["description"]
    for i, n in enumerate(names):
        d["geometry"][f"tpl_{i}"] = f"geometry.ft_tpl.{n}"
    for s in sorted(set(WOOD_LEAF)):
        d["textures"][f"leafatlas_{s}"] = f"textures/entity/fallingtree/leafatlas_{s}"
    for k in range(1, MAX_LAYERS):
        d["animations"][f"ft_lift_{k}"] = f"animation.ft_tpl.lift_{k}"
    d["animations"]["ft_turn"] = "animation.ft_tpl.turn"
    anim = d["scripts"]["animate"]
    anim.append({"ft_turn": "q.property('ft:tpl') >= 0"})
    for k in range(1, MAX_LAYERS):
        anim.append({f"ft_lift_{k}": f"q.property('ft:tpl') >= 0 && q.property('ft:lift') == {k}"})
    old_rcs = d["render_controllers"]
    if old_rcs != ["controller.render.ft_falling_tree", "controller.render.ft_falling_tree_canopy", "controller.render.ft_falling_tree_collar"]:
        raise SystemExit(f"unexpected render controllers {old_rcs}")
    d["render_controllers"] = [{rc: "q.property('ft:tpl') < 0"} for rc in old_rcs] + \
        [{rc: "q.property('ft:tpl') >= 0"} for rc in ("controller.render.ft_tpl_trunk", "controller.render.ft_tpl_canopy", "controller.render.ft_tpl_collar")]
    ep.write_text(json.dumps(e, indent=1))

    # ---------------------------------------------------------------- manifest
    mp = DST / "manifest.json"
    m = json.loads(mp.read_text())
    m["header"]["version"] = [1, 3, 119]
    for mod in m["modules"]:
        mod["version"] = [1, 3, 119]
    m["header"]["name"] = "AbsolutRealism Tectonic RP v1.3.119"
    desc = m["header"]["description"]
    if not desc.startswith("v1.3.118 (2026-10-03) "):
        raise SystemExit("description prefix")
    m["header"]["description"] = ("v1.3.119 (2026-10-03) FALLING TREE carbon copy: the falling tree is built from the felled tree's own "
                                  "template (every log and leaf, new leaf look, turned like the tree). Includes all of " + desc)[:1000]
    mp.write_text(json.dumps(m, indent=1))
    print(f"DONE {DST}: {len(names)} geometries, animations {len(anims)}, render controllers 3 new")


if __name__ == "__main__":
    main()
