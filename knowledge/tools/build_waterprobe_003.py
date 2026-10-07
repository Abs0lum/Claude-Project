#!/usr/bin/env python3
"""build_waterprobe_003.py — R10's open items (his 20:35): tools/waterprobe3_src/main.js + nine test blocks with
minecraft:liquid_detection on NON-full shapes: wp:x_* (built-in cross geometry, no collision — a plant / grate) and
wp:low_* (our ramp quarter's geometry, a 4-px collision slab). Run with BP-02 beside it (E19 reads our own blocks).
Usage: python3 tools/build_waterprobe_003.py   (_build/waterprobe-0.0.3 must not exist)"""
import json
import shutil
import subprocess
import uuid
from pathlib import Path

DST = Path("/home/claude/_build/waterprobe-0.0.3")
SRC = Path("/home/claude/tools/waterprobe3_src")
V = [0, 0, 3]


def block(ident, geo, coll, rules):
    comps = {"minecraft:geometry": geo, "minecraft:material_instances": {"*": {"texture": "stone", "render_method": "alpha_test"}},
             "minecraft:destructible_by_mining": {"seconds_to_destroy": 1}, "minecraft:collision_box": coll,
             "minecraft:selection_box": {"origin": [-8, 0, -8], "size": [16, 4, 16]}, "minecraft:light_dampening": 0}
    if rules is not None:
        comps["minecraft:liquid_detection"] = {"detection_rules": rules}
    return {"format_version": "1.21.80", "minecraft:block": {"description": {"identifier": ident}, "components": comps}}


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    (DST / "scripts").mkdir(parents=True)
    shutil.copy2(SRC / "main.js", DST / "scripts/main.js")
    W = {"liquid_type": "water"}
    rules = {"noreact": [dict(W, can_contain_liquid=False, on_liquid_touches="no_reaction")],
             "popped": [dict(W, can_contain_liquid=False, on_liquid_touches="popped")],
             "broken": [dict(W, can_contain_liquid=False, on_liquid_touches="broken")],
             "blocking": [dict(W, can_contain_liquid=False, on_liquid_touches="blocking")],
             "contain": [dict(W, can_contain_liquid=True, on_liquid_touches="no_reaction")]}
    (DST / "blocks").mkdir()
    for k in ("noreact", "popped", "broken", "blocking", "contain"):
        b = block(f"wp:x_{k}", "minecraft:geometry.cross", False, rules[k])
        (DST / "blocks" / f"x_{k}.json").write_text(json.dumps(b, indent=1))
    for k in ("popped", "broken", "contain", "blocking"):
        b = block(f"wp:low_{k}", "geometry.pw_ramp_4_q1", {"origin": [-8, 0, -8], "size": [16, 4, 16]}, rules[k])
        (DST / "blocks" / f"low_{k}.json").write_text(json.dumps(b, indent=1))
    m = {"format_version": 2,
         "header": {"name": "PW water probe 0.0.3 (BDS only)", "description": "R10 open items", "uuid": str(uuid.uuid4()), "version": V, "min_engine_version": [1, 21, 120]},
         "modules": [{"type": "script", "language": "javascript", "entry": "scripts/main.js", "uuid": str(uuid.uuid4()), "version": V},
                     {"type": "data", "uuid": str(uuid.uuid4()), "version": V}],
         "dependencies": [{"module_name": "@minecraft/server", "version": "2.3.0"}]}
    (DST / "manifest.json").write_text(json.dumps(m, indent=1))
    r = subprocess.run(["node", "--check", str(DST / "scripts/main.js")], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    print(f"DONE {DST}")


if __name__ == "__main__":
    main()
