#!/usr/bin/env python3
"""build_bump_assets.py — MR3 bump-map side-by-side test assets (D-C367).

One test creature pw:nbump with 8 looks (minecraft:variant 0-7): warden, dolphin, turtle, parrot (blue) — each twice:
  even variant = bump ON  (colour + Patrix MERS + converted Patrix normal)
  odd variant  = bump OFF (identical colour + identical MERS, NO normal)
Geometry = the mob's own shipped geometry (resolved at runtime from RP-06 / RP-07); the texture copies live in the
test RP so every texture_set sits beside its colour (H-18). No AI, no movement, no damage: it stands in its rest pose.

Writes _staging/bump/bp/... and _staging/bump/rp/... (merged into PW-TestRunner BP / RP by their builders) plus
_staging/bump/rig_row.json (the rig row for the lineup step).
"""
import json
import shutil
from pathlib import Path

ROOT = Path("/home/claude")
OUT = ROOT / "_staging/bump"
MOBS = [  # (label, geometry id, source pack build, texture rel path)
    ("Warden", "geometry.pw_warden", "rp06-1425", "textures/entity/warden/warden"),
    ("Dolphin", "geometry.dolphin.patrix", "rp07-1439", "textures/entity/dolphin/dolphin"),
    ("Turtle", "geometry.turtle.patrix", "rp07-1439", "textures/entity/turtle/turtle"),
    ("Parrot", "geometry.pw_parrot", "rp07-1439", "textures/entity/parrot/parrot_blue"),
]


def colour(pack, rel):
    for ext in (".png", ".tga"):
        p = ROOT / "_build" / pack / (rel + ext)
        if p.exists():
            return p
    raise FileNotFoundError(rel)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    tex_dir = OUT / "rp/textures/pw_test/nbump"
    tex_dir.mkdir(parents=True)
    textures, geos, geo_array, tex_array, row = {}, {}, [], [], []
    for i, (label, gid, pack, rel) in enumerate(MOBS):
        key = label.lower()
        src_col = colour(pack, rel)
        src_dir = src_col.parent
        stem = Path(rel).name
        normal = src_dir / f"{stem}_n.png"
        mers = src_dir / f"{stem}_mers.png"
        assert normal.exists() and mers.exists(), (label, normal, mers)
        geos[f"g_{key}"] = gid
        for mode in ("on", "off"):
            name = f"{key}_{mode}"
            shutil.copyfile(src_col, tex_dir / f"{name}{src_col.suffix}")
            shutil.copyfile(mers, tex_dir / f"{name}_mers.png")
            ts = {"color": name, "metalness_emissive_roughness_subsurface": f"{name}_mers"}
            if mode == "on":
                shutil.copyfile(normal, tex_dir / f"{name}_n.png")
                ts["normal"] = f"{name}_n"
            (tex_dir / f"{name}.texture_set.json").write_text(json.dumps(
                {"format_version": "1.21.30", "minecraft:texture_set": ts}, indent=1))
            tk = f"t_{name}"
            textures[tk] = f"textures/pw_test/nbump/{name}"
            geo_array.append(f"Geometry.g_{key}")
            tex_array.append(f"Texture.{tk}")
            v = len(tex_array) - 1
            row.append({"mob": "pw:nbump", "dx": v * 3, "event": f"pw:v{v}",
                        "name": f"{label} - bump {'ON' if mode == 'on' else 'OFF'}"})
    client = {"format_version": "1.10.0", "minecraft:client_entity": {"description": {
        "identifier": "pw:nbump", "materials": {"default": "entity_alphatest"}, "textures": textures,
        "geometry": geos, "render_controllers": ["controller.render.pw_nbump"],
        "spawn_egg": {"base_color": "#3a5f7a", "overlay_color": "#d9c27a"}}}}
    rc = {"format_version": "1.8.0", "render_controllers": {"controller.render.pw_nbump": {
        "arrays": {"geometries": {"Array.geo": geo_array}, "textures": {"Array.tex": tex_array}},
        "geometry": "Array.geo[query.variant]", "textures": ["Array.tex[query.variant]"],
        "materials": [{"*": "Material.default"}]}}}
    (OUT / "rp/entity").mkdir(parents=True)
    (OUT / "rp/render_controllers").mkdir(parents=True)
    (OUT / "rp/entity/pw_nbump.entity.json").write_text(json.dumps(client, indent=1))
    (OUT / "rp/render_controllers/pw_nbump.render_controllers.json").write_text(json.dumps(rc, indent=1))
    groups = {f"pw:v{v}": {"minecraft:variant": {"value": v}} for v in range(len(tex_array))}
    events = {f"pw:v{v}": {"add": {"component_groups": [f"pw:v{v}"]},
                           "remove": {"component_groups": [g for g in groups if g != f"pw:v{v}"]}}
              for v in range(len(tex_array))}
    bp = {"format_version": "1.21.0", "minecraft:entity": {
        "description": {"identifier": "pw:nbump", "is_spawnable": False, "is_summonable": True},
        "component_groups": groups,
        "components": {
            "minecraft:variant": {"value": 0},
            "minecraft:collision_box": {"width": 0.9, "height": 1.0},
            "minecraft:physics": {}, "minecraft:pushable": {"is_pushable": False, "is_pushable_by_piston": False},
            "minecraft:damage_sensor": {"triggers": {"cause": "all", "deals_damage": "no"}},
            "minecraft:nameable": {"always_show": True, "allow_name_tag_renaming": True},
            "minecraft:persistent": {}, "minecraft:knockback_resistance": {"value": 1.0},
            "minecraft:health": {"value": 20, "max": 20}},
        "events": events}}
    (OUT / "bp/entities").mkdir(parents=True)
    (OUT / "bp/entities/pw_nbump.json").write_text(json.dumps(bp, indent=1))
    (OUT / "rig_row.json").write_text(json.dumps(row, indent=1))
    print(f"pw:nbump: {len(tex_array)} looks; files:",
          sum(1 for _ in OUT.rglob('*') if _.is_file()))


if __name__ == "__main__":
    main()
