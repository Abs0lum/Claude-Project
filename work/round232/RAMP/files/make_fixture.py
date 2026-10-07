"""Fixture for tests/test_roadramp8.mjs: the REAL cobble ramp blocks of BP-02 1.3.230 (identifier, states, placement trait,
collision height per part) and the street piece t_ramp8's cobble lane (the model a road ramp copies: part per cell along
the climb, cardinal_direction per cell). Usage: python3 -I make_fixture.py BP02_DIR OUT_JSON"""
import hashlib
import json
import sys
from pathlib import Path
sys.path.insert(0, "/home/user/Claude-Project/knowledge/tools")
import mcstructure as M

bp, out = Path(sys.argv[1]), Path(sys.argv[2])
blocks, src = {}, {}
for part in [f"4_q{k}" for k in range(1, 5)] + [f"8_e{k}" for k in range(1, 9)]:
    p = bp / "blocks" / f"pw_ramp_cobble_{part}.json"
    raw = p.read_bytes()
    b = json.loads(raw)["minecraft:block"]
    d = b["description"]
    blocks[d["identifier"]] = {
        "states": d.get("states", {}),
        "trait_states": d.get("traits", {}).get("minecraft:placement_direction", {}).get("enabled_states", []),
        "collision_h": b["components"]["minecraft:collision_box"]["size"][1],
        "rot": {p2["condition"].split("'")[3]: p2["components"]["minecraft:transformation"]["rotation"][1]
                for p2 in b.get("permutations", []) if "pw:snow') == 0" in p2["condition"]},
    }
    src[p.name] = hashlib.md5(raw).hexdigest()
piece = bp / "structures" / "pw" / "road" / "t_ramp8.mcstructure"
raw = piece.read_bytes()
_, root = M.decode(raw)
r = root.plain()
sx, sy, sz = r["size"]
st = r["structure"]
idx = st["block_indices"][0]
pal = st["palette"]["default"]["block_palette"]
lane = []
for x in range(sx):
    k = idx[(x * sy + 14) * sz + 6]                      # y 14 (the carriageway's ramp row), z 6 (the lane's centre)
    bl = pal[k]
    lane.append({"x": x, "name": bl["name"], "states": bl["states"]})
src[piece.name] = hashlib.md5(raw).hexdigest()
out.write_text(json.dumps({"source": "BP-02 1.3.230 (scratchpad/bp02-230), read by make_fixture.py", "md5": src,
                           "blocks": blocks, "t_ramp8_lane": {"size": [sx, sy, sz], "native": "travel +x, low end x 0",
                                                              "cells": lane}}, separators=(",", ":"), sort_keys=True))
print(out, len(blocks), "blocks", [c["name"].split("_")[-1] + ":" + c["states"]["minecraft:cardinal_direction"] for c in lane])
