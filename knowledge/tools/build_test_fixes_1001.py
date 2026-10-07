#!/usr/bin/env python3
"""build_test_fixes_1001.py — his 21:05 report.

1) VV OFF on the PS5 with the test packs: our 3 test packs (SandTest A, SandTest B, LightTest Saturation-NOW) have NO
   "capabilities": ["pbr"] in the manifest; every main pack has it. -> v1.0.1 of each: same header/module uuids (so the
   import replaces 1.0.0), version 1.0.1, + capabilities ["pbr"]. Files otherwise byte-identical.
2) GRASS SIDE TINT experiment (vanilla minecraft:grass_block; his Q1: lavender band = untinted fringe, measured RGB
   146,132,140 = the raw colour of grass_block_side_v0.tga's fringe, so NO tint is applied). Two terrain-only test packs
   (no textures: the images + texture sets stay in RP-04, so nothing is shadowed):
     T1 = Mojang's exact 26.50 form: "textures": [ {"path": <our v0>, "overlay_color": "#df6827"} ]  (one texture)
     T2 = our 16 variations, overlay_color changed from "#79c05a" to Mojang's "#df6827"
   Read: T1 tinted + T2 tinted -> the colour value was the cause, T2 is the fix (keeps variety);
         T1 tinted + T2 not   -> overlay is ignored with variations;  neither -> the mask/texture itself."""
import json
import re
import shutil
import uuid
from pathlib import Path

ROOT = Path("/home/claude")
B = ROOT / "_build"


def jl(p):
    return json.loads(re.sub(r"(?m)^\s*//.*$", "", p.read_text(encoding="utf-8-sig")))


def bump(src, dst):
    assert not (B / dst).exists(), "never rebuild a build dir"
    shutil.copytree(B / src, B / dst)
    m = jl(B / dst / "manifest.json")
    m["header"]["version"] = [1, 0, 1]
    m["header"]["name"] = m["header"]["name"].replace("v1.0.0", "v1.0.1")
    for mod in m["modules"]:
        mod["version"] = [1, 0, 1]
    m["capabilities"] = ["pbr"]
    m["header"]["description"] = m["header"]["description"] + " v1.0.1: Vibrant Visuals capable (pbr)."
    (B / dst / "manifest.json").write_text(json.dumps(m, indent=2))
    print("built", dst)


def grass_test(name, data, desc):
    dst = B / f"grasstint-{name.lower()}-100"
    assert not dst.exists(), "never rebuild a build dir"
    (dst / "textures").mkdir(parents=True)
    (dst / "textures/terrain_texture.json").write_text(json.dumps(
        {"resource_pack_name": "pw_grasstint", "texture_name": "atlas.terrain", "padding": 8, "num_mip_levels": 4,
         "texture_data": data}, indent=2))
    (dst / "manifest.json").write_text(json.dumps({"format_version": 2, "header": {
        "name": f"PW-GrassTint {name} v1.0.0",
        "description": f"TEST ONLY (10-01): {desc} Put it at the TOP of the stack and look at vanilla grass block "
                       "sides (world-generated ground). Not for normal play.",
        "uuid": str(uuid.uuid4()), "version": [1, 0, 0], "min_engine_version": [1, 21, 120]},
        "modules": [{"description": f"grass side tint test {name}", "type": "resources", "uuid": str(uuid.uuid4()),
                     "version": [1, 0, 0]}], "capabilities": ["pbr"]}, indent=2))
    shutil.copy2(B / "lighttest-sat-100/pack_icon.png", dst / "pack_icon.png")
    print("built", dst.name)


def main():
    bump("sandtest-a-100", "sandtest-a-101")
    bump("sandtest-b-100", "sandtest-b-101")
    bump("lighttest-sat-100", "lighttest-sat-101")
    side = jl(B / "rp04-147/textures/terrain_texture.json")["texture_data"]["grass_block_side"]
    assert side["textures"]["overlay_color"] == "#79c05a"
    t1 = {"textures": [{"path": "textures/blocks/grass_block_side_v0", "overlay_color": "#df6827"}]}
    t2 = json.loads(json.dumps(side))
    t2["textures"]["overlay_color"] = "#df6827"
    grass_test("T1", {"grass_side": t1, "grass_block_side": t1},
               "T1 = Mojang's exact grass side form (one texture, overlay #df6827).")
    grass_test("T2", {"grass_side": t2, "grass_block_side": t2},
               "T2 = our 16 grass side variations with Mojang's overlay colour #df6827.")


if __name__ == "__main__":
    main()
