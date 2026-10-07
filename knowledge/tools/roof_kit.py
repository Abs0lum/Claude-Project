#!/usr/bin/env python3
"""roof_kit.py — task #171 (his 17:31: only ridge + cap work; hip, pyramidion, ridge_end, gussets, roof63, crown_ring
"I want to fix them, but if I can't, I want to delete them"). ONE placeable structure with every questioned piece in the
assembly it was made for, on a stone pad, numbered left to right (seen from the south, standing in front of the pad):
  1  gusset column      (s1)  roof_gusset_lower + upper, stacked twice
  2  hip junction       (s2)  two roof45 meeting a gusset pair
  3  pyramid 5x5        (s3)  8 hips + 16 roof45 + the pyramidion cap
  4  ridge run          (s4)  roof45 both sides, ridge in the middle, ridge_end at each end
  5  crown ring         (s6)  12 crown_ring pieces
  6  steep gable 63°    (NEW) roof63 lower + upper, two steps each side, upper pieces meeting at the top
Writes BP-02 1.3.206 structures/pw/roof_kit.mcstructure (load: /structure load pw:roof_kit ~ ~ ~) and a true-geometry
render sheet (tools/civ_render.py) to outputs/ROOF-KIT.png."""
import json
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402

SRC = Path("/home/claude/_build/bp02-206/structures/pw")
OUT = SRC / "roof_kit.mcstructure"
ASSEMBLIES = ["s1_gusset_column", "s2_hip_junction", "s3_pyramid_5x5", "s4_ridge_run", "s6_crown_ring"]
GAP = 3


def gable63():
    st = M.Structure((3, 4, 4))
    for x in range(3):
        for z, face, y0 in ((0, "north", 0), (1, "north", 2), (2, "south", 2), (3, "south", 0)):
            st.set(x, y0, z, "pw:roof63_lower_oak", {"minecraft:cardinal_direction": M.s(face), "minecraft:vertical_half": M.s("bottom")})
            st.set(x, y0 + 1, z, "pw:roof63_upper_oak", {"minecraft:cardinal_direction": M.s(face), "minecraft:vertical_half": M.s("bottom")})
            if y0 == 2:
                for y in (0, 1):
                    st.set(x, y, z, "minecraft:oak_planks")          # the gable wall under the upper step
    return st


def main():
    parts = [(n, M.Structure.from_bytes((SRC / f"{n}.mcstructure").read_bytes())) for n in ASSEMBLIES]
    parts.append(("roof63_gable", gable63()))
    W = sum(p.size[0] for _, p in parts) + GAP * (len(parts) + 1)
    H = max(p.size[1] for _, p in parts) + 1
    D = max(p.size[2] for _, p in parts) + 2 * GAP
    kit = M.Structure((W, H, D))
    for x in range(W):
        for z in range(D):
            kit.set(x, 0, z, "minecraft:smooth_stone")
    ox, placed = GAP, []
    for name, p in parts:
        oz = (D - p.size[2]) // 2
        for x in range(p.size[0]):
            for y in range(p.size[1]):
                for z in range(p.size[2]):
                    b = p.get(x, y, z)
                    if b and b[0] != "minecraft:air":
                        kit.set(ox + x, y + 1, oz + z, b[0], b[1])
        placed.append({"n": len(placed) + 1, "assembly": name, "x": ox, "width": p.size[0]})
        ox += p.size[0] + GAP
    OUT.write_bytes(kit.to_bytes())
    # manifest for the true-geometry renderer
    blocks = []
    for x in range(W):
        for y in range(H):
            for z in range(D):
                b = kit.get(x, y, z)
                if b:
                    blocks.append([x, y, z, b[0], {k: v.value for k, v in b[1].items()}])
    man = {"name": "pw:roof_kit", "size": [W, H, D], "datum_y": 1, "blocks": blocks, "assemblies": placed}
    mp = Path("/home/claude/_staging/roof_kit_manifest.json")
    mp.write_text(json.dumps(man))
    print(json.dumps({"size": [W, H, D], "assemblies": placed}, indent=1))


if __name__ == "__main__":
    main()
