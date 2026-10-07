#!/usr/bin/env python3
"""build_grasstint_t34.py — his 23:41 OK on T3 / T4 (vanilla grass_block side tint).
Witness so far: T1 (list form, key grass_block_side, overlay #df6827) = band ORANGE (static colour, not biome);
T2 (variations + overlay) = untinted. Hypothesis H-ROUTE: RP-04 blocks.json sends minecraft:grass_block's side to our
key 'grass_block_side', and only Mojang's own key 'grass_side' gets the 26.50 biome colour matching.
  T3 = blocks.json minecraft:grass_block side -> 'grass_side' (+ Mojang's carried_textures), grass_side = ONE texture
       (our v0) with overlay #df6827 in Mojang's list form.
  T4 = as T3, grass_side = list of our 16 side textures, each with overlay #df6827 (tests whether variety survives).
Read: T3 green+biome-coloured -> H-ROUTE confirmed. T4 also -> variety kept. T4 orange/odd -> one texture only."""
import json
import shutil
import uuid
from pathlib import Path

B = Path("/home/claude/_build")
OVERLAY = "#df6827"


def build(name, grass_side, desc):
    dst = B / f"grasstint-{name.lower()}-100"
    assert not dst.exists(), "never rebuild a build dir"
    (dst / "textures").mkdir(parents=True)
    (dst / "blocks.json").write_text(json.dumps({"format_version": "1.1.0", "minecraft:grass_block": {
        "sound": "grass", "isotropic": {"up": True},
        "carried_textures": {"up": "grass_carried_top", "down": "grass_carried_bottom", "side": "grass_carried"},
        "textures": {"up": "grass_block_top", "down": "dirt", "side": "grass_side"}}}, indent=2))
    (dst / "textures/terrain_texture.json").write_text(json.dumps(
        {"resource_pack_name": "pw_grasstint", "texture_name": "atlas.terrain", "padding": 8, "num_mip_levels": 4,
         "texture_data": {"grass_side": grass_side}}, indent=2))
    (dst / "manifest.json").write_text(json.dumps({"format_version": 2, "header": {
        "name": f"PW-GrassTint {name} v1.0.0",
        "description": f"TEST ONLY (10-01): {desc} Put it at the TOP of the stack; look at vanilla grass block sides. "
                       "Not for normal play.",
        "uuid": str(uuid.uuid4()), "version": [1, 0, 0], "min_engine_version": [1, 21, 120]},
        "modules": [{"description": f"grass side tint test {name}", "type": "resources", "uuid": str(uuid.uuid4()),
                     "version": [1, 0, 0]}], "capabilities": ["pbr"]}, indent=2))
    shutil.copy2(B / "lighttest-sat-100/pack_icon.png", dst / "pack_icon.png")
    print("built", dst.name)


if __name__ == "__main__":
    build("T3", {"textures": [{"path": "textures/blocks/grass_block_side_v0", "overlay_color": OVERLAY}]},
          "T3 = side routed to Mojang's 'grass_side' key, one texture.")
    build("T4", {"textures": [{"path": f"textures/blocks/grass_block_side_v{i}", "overlay_color": OVERLAY} for i in range(16)]},
          "T4 = side routed to Mojang's 'grass_side' key, our 16 textures as a list.")
