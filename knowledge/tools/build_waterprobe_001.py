#!/usr/bin/env python3
"""build_waterprobe_001.py — the R10 water probe pack (BDS only, never shipped to him): tools/waterprobe_src/main.js +
six custom blocks with minecraft:liquid_detection + two test entities (one with minecraft:buoyant).
Usage: python3 tools/build_waterprobe_001.py   (_build/waterprobe-0.0.1 must not exist)"""
import json
import shutil
import subprocess
import uuid
from pathlib import Path

DST = Path("/home/claude/_build/waterprobe-0.0.1")
SRC = Path("/home/claude/tools/waterprobe_src")
V = [0, 0, 1]


def block(ident, rules):
    comps = {"minecraft:geometry": "minecraft:geometry.full_block",
             "minecraft:material_instances": {"*": {"texture": "stone", "render_method": "opaque"}},
             "minecraft:destructible_by_mining": {"seconds_to_destroy": 1}}
    if rules is not None:
        comps["minecraft:liquid_detection"] = {"detection_rules": rules}
    return {"format_version": "1.21.80", "minecraft:block": {"description": {"identifier": ident}, "components": comps}}


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    (DST / "scripts").mkdir(parents=True)
    shutil.copy2(SRC / "main.js", DST / "scripts/main.js")
    W = {"liquid_type": "water"}
    blocks = {
        "wp:ld_default": None,
        "wp:ld_contain": [dict(W, can_contain_liquid=True, on_liquid_touches="no_reaction")],
        "wp:ld_popped": [dict(W, can_contain_liquid=False, on_liquid_touches="popped")],
        "wp:ld_broken": [dict(W, can_contain_liquid=False, on_liquid_touches="broken")],
        "wp:ld_blocking": [dict(W, can_contain_liquid=False, on_liquid_touches="blocking")],
        "wp:ld_stop_east": [dict(W, can_contain_liquid=True, on_liquid_touches="no_reaction", stops_liquid_flowing_from_direction=["east"])],
    }
    (DST / "blocks").mkdir()
    for ident, rules in blocks.items():
        (DST / "blocks" / (ident.split(":")[1] + ".json")).write_text(json.dumps(block(ident, rules), indent=1))
    (DST / "entities").mkdir()
    base = {"minecraft:physics": {}, "minecraft:collision_box": {"width": 0.8, "height": 0.8}, "minecraft:health": {"value": 10, "max": 10},
            "minecraft:pushable": {"is_pushable": True, "is_pushable_by_piston": True}}
    flo = dict(base)
    flo["minecraft:buoyant"] = {"base_buoyancy": 1.0, "apply_gravity": True, "simulate_waves": True, "big_wave_probability": 0.03,
                                "big_wave_speed": 10.0, "drag_down_on_buoyancy_removed": 0.0, "liquid_blocks": ["minecraft:water", "minecraft:flowing_water"]}
    for ident, comps in (("wp:float", flo), ("wp:sinker", base)):
        e = {"format_version": "1.21.0", "minecraft:entity": {"description": {"identifier": ident, "is_spawnable": False, "is_summonable": True},
                                                                "components": comps}}
        (DST / "entities" / (ident.split(":")[1] + ".json")).write_text(json.dumps(e, indent=1))
    m = {"format_version": 2,
         "header": {"name": "PW water probe 0.0.1 (BDS only)", "description": "R10: Bedrock water measured", "uuid": str(uuid.uuid4()),
                    "version": V, "min_engine_version": [1, 21, 120]},
         "modules": [{"type": "script", "language": "javascript", "entry": "scripts/main.js", "uuid": str(uuid.uuid4()), "version": V},
                     {"type": "data", "uuid": str(uuid.uuid4()), "version": V}],
         "dependencies": [{"module_name": "@minecraft/server", "version": "2.3.0"}]}
    (DST / "manifest.json").write_text(json.dumps(m, indent=1))
    r = subprocess.run(["node", "--check", str(DST / "scripts/main.js")], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    print(f"DONE {DST}: 6 liquid_detection blocks, wp:float (buoyant) + wp:sinker, script checked")


if __name__ == "__main__":
    main()
