#!/usr/bin/env python3
"""cottage_census_sheet.py — his 17:50: "in the original cottage you're using to build others from - I may have missed
zones and stations AND decor". Census of his r0 template (Proving Grounds 09-28 world copy): three floor plans seen from
ABOVE (street / front door on the LEFT edge, x = 0), every block that is not wall / floor / roof / fill labelled, plus the
stations and zones the r1 rebuild added on its own (tools/civgen.py) for comparison.
Output: /mnt/user-data/outputs/COTTAGE-r0-CENSUS.png"""
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402

R0 = "/tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad/r0.mcstructure"
CELL = 92
FLOORS = [("CELLAR (feet y 10)", [10, 11, 12]), ("GROUND FLOOR (feet y 15)", [14, 15, 16]), ("LOFT (feet y 19)", [19])]
FILL = {"stone_bricks": (125, 125, 125), "oak_planks": (176, 140, 88), "spruce_log": (92, 66, 40),
        "cobblestone": (110, 110, 110), "glass_pane": (170, 210, 230), "dirt": (95, 70, 50), "ladder": (150, 110, 60)}
SHORT = {"furn_chair_oak": "chair", "furn_table_oak": "table", "furn_wall_shelf_oak": "shelf", "furn_mantel_oak": "mantel",
         "hearth_oak_planks": "hearth", "wooden_door": "door", "manhole_cover": "manhole", "port_sewer": "sewer port"}
STRUCTURAL = {"air", "light_block_14", "dirt", "stone_bricks", "oak_planks", "smooth_stone", "stone", "cobblestone",
              "spruce_log", "grass_block", "glass_pane", "ladder", "flue_oak_planks", "roof45_spruce", "roof45_ridge_spruce"}


def main():
    st = M.Structure.from_bytes(open(R0, "rb").read())
    sx, sy, sz = st.size
    font = ImageFont.load_default()
    W = len(FLOORS) * (sz * CELL + 40) + 20
    H = sx * CELL + 520
    img = Image.new("RGB", (W, H), (24, 24, 28))
    d = ImageDraw.Draw(img)
    d.text((14, 8), "His cottage r0 seen from ABOVE, drawn as if you stand in the street at the BOTTOM of each plan facing the "
           "front door: the door wall is the bottom row, your left is the left.", fill=(235, 235, 235), font=font)
    for fi, (title, ys) in enumerate(FLOORS):
        ox, oy = 20 + fi * (sz * CELL + 40), 40
        d.text((ox, oy), title, fill=(255, 210, 120), font=font)
        oy += 18
        for x in range(sx):
            for z in range(sz):
                labels, base = [], None
                for y in ys:
                    b = st.get(x, y, z)
                    name = b[0].split(":")[-1] if b else "air"
                    if name in STRUCTURAL:
                        if name in FILL and base is None and y == ys[0] + (1 if len(ys) > 1 else 0):
                            base = FILL[name]
                    else:
                        labels.append(SHORT.get(name, name))
                x0, y0 = ox + z * CELL, oy + (sx - 1 - x) * CELL
                d.rectangle([x0, y0, x0 + CELL - 2, y0 + CELL - 2], fill=base or (60, 60, 66))
                for i, lab in enumerate(dict.fromkeys(labels)):
                    d.rectangle([x0 + 3, y0 + 4 + i * 16, x0 + CELL - 5, y0 + 18 + i * 16], fill=(250, 245, 220))
                    d.text((x0 + 6, y0 + 5 + i * 16), lab, fill=(20, 20, 20), font=font)
        d.text((ox, oy + sx * CELL + 4), "bottom row = door wall (street side)", fill=(180, 180, 180), font=font)
    ty = sx * CELL + 100
    lines = [
        "WHAT r0 CONTAINS",
        "  cellar: barrel, 2 chests, ladder up, manhole (to a sewer port 4 blocks below)",
        "  ground: door, datum, furnace, table + 2 chairs, hearth + mantel, wall shelf, trapdoor to the cellar, 2 windows",
        "  loft: bed, chest, wall shelf, chair, the hearth's upper part; light = 95 invisible light blocks",
        "WHAT r0 DOES NOT CONTAIN",
        "  stations: NONE (0 of the 18 roles)      zones: NONE (0 of the 12 kinds)",
        "  decor: NONE - no lanterns / candles, rugs / carpets, plants / pots, pictures, item frames, food, tools, curtains",
        "WHAT THE r1 REBUILD ADDED ON ITS OWN (my layout, not yours)",
        "  stations: door, hearth, table, seat x2, store x2 (cellar chest + ground chest), bed",
        "  zones: threshold (inside the door), kitchen (ground floor), cellar, quarters (loft)",
        "  NOT given a station in r1: furnace (oven), barrel, 3rd chest, 3rd chair; no prep / counter surface exists",
    ]
    for i, t in enumerate(lines):
        d.text((20, ty + i * 18), t, fill=(255, 210, 120) if t.isupper() or t.startswith("WHAT") else (230, 230, 230), font=font)
    img.save("/mnt/user-data/outputs/COTTAGE-r0-CENSUS.png")
    print(img.size)


if __name__ == "__main__":
    main()
