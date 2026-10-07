#!/usr/bin/env python3
"""facings_sheet.py — #175: every authored direction-dependent piece drawn in all four facings under the MEASURED
transformation law (D-C487), so Abs0lum and I look at the same thing. Each tile: the piece on a stone pad, seen
from the south-east above; the RED strip marks the NORTH side of the piece's cell. The caption gives the state.
Output: outputs/BLOCK-FACINGS-1.png, -2.png, -3.png (12 rows each)."""
import json
import os
import sys
from pathlib import Path

os.environ["PW_STACK"] = "final"
sys.path.insert(0, "/home/claude/tools")
import civ_render as CR  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

CR.BP = Path("/home/claude/_build/bp02-206/blocks")
CR.RP_MODELS = [Path("/home/claude/_build/rp04-156/models/blocks"), Path("/home/claude/_build/rp01-117/models/blocks")]
CR.THIN["marker:n"] = (-8, 0, -8, 16, 1.5, 16)
CR.FLAT["marker:n"] = (215, 40, 40)
DIRS = ["north", "east", "south", "west"]
ROWS = [  # (label, block, extra states, state key)
    ("roof45 (eave = state side)", "pw:roof45_oak", {"minecraft:vertical_half": "bottom"}, "minecraft:cardinal_direction"),
    ("roof45 top half", "pw:roof45_oak", {"minecraft:vertical_half": "top"}, "minecraft:cardinal_direction"),
    ("roof45 ridge", "pw:roof45_ridge_oak", {}, "minecraft:cardinal_direction"),
    ("roof63 lower", "pw:roof63_lower_oak", {}, "minecraft:cardinal_direction"),
    ("roof63 upper", "pw:roof63_upper_oak", {}, "minecraft:cardinal_direction"),
    ("roof hip (corner n=NW)", "pw:roof_hip_oak", {"minecraft:vertical_half": "bottom"}, "minecraft:cardinal_direction"),
    ("roof hip top half", "pw:roof_hip_oak", {"minecraft:vertical_half": "top"}, "minecraft:cardinal_direction"),
    ("pyramidion", "pw:roof_pyramidion_oak", {"minecraft:vertical_half": "bottom"}, "minecraft:cardinal_direction"),
    ("ridge end (hip end = state side)", "pw:roof_ridge_end_oak", {"minecraft:vertical_half": "bottom"}, "minecraft:cardinal_direction"),
    ("gusset lower", "pw:roof_gusset_lower_oak", {"minecraft:vertical_half": "bottom"}, "minecraft:cardinal_direction"),
    ("gusset upper", "pw:roof_gusset_upper_oak", {"minecraft:vertical_half": "bottom"}, "minecraft:cardinal_direction"),
    ("crown ring straight (lip = state side)", "pw:crown_ring_oak", {"pw:ring_form": "straight"}, "minecraft:cardinal_direction"),
    ("crown ring corner (n = N+W)", "pw:crown_ring_oak", {"pw:ring_form": "corner"}, "minecraft:cardinal_direction"),
    ("rafter45", "pw:rafter45_oak", {}, "minecraft:cardinal_direction"),
    ("hearth (cold)", "pw:hearth_stone_bricks", {"pw:phase": "cold"}, "minecraft:cardinal_direction"),
    ("room wall (panel = state side)", "pw:room_wall", {"pw:material": "oak_planks"}, "minecraft:cardinal_direction"),
    ("room wall corner (n = N+E)", "pw:room_wall_corner", {"pw:material": "oak_planks"}, "minecraft:cardinal_direction"),
    ("wall prism (facade = state side)", "pw:wall_prism", {"pw:material": "oak_planks"}, "minecraft:cardinal_direction"),
    ("angled wall", "pw:angled_wall", {"pw:material": "oak_planks"}, "minecraft:cardinal_direction"),
    ("builders table", "pw:builders_table", {}, "minecraft:cardinal_direction"),
    ("ramp 2 lo (rises toward state)", "pw:ramp_cobble_2_lo", {"pw:var": 0, "pw:snow": 0}, "minecraft:cardinal_direction"),
    ("ramp 2 hi", "pw:ramp_cobble_2_hi", {"pw:var": 0, "pw:snow": 0}, "minecraft:cardinal_direction"),
    ("ramp 2 hi, snow 3", "pw:ramp_cobble_2_hi", {"pw:var": 0, "pw:snow": 3}, "minecraft:cardinal_direction"),
    ("ramp 4 q1", "pw:ramp_cobble_4_q1", {"pw:var": 0, "pw:snow": 0}, "minecraft:cardinal_direction"),
    ("ramp 4 q4", "pw:ramp_cobble_4_q4", {"pw:var": 0, "pw:snow": 0}, "minecraft:cardinal_direction"),
    ("chair", "pw:furn_chair_oak", {}, "minecraft:cardinal_direction"),
    ("bench", "pw:furn_bench_oak", {}, "minecraft:cardinal_direction"),
    ("stool", "pw:furn_stool_oak", {}, "minecraft:cardinal_direction"),
    ("barrel seat", "pw:furn_barrel_seat_oak", {}, "minecraft:cardinal_direction"),
    ("table (alone)", "pw:furn_table_oak", {}, "minecraft:cardinal_direction"),
    ("trestle", "pw:furn_trestle_oak", {}, "minecraft:cardinal_direction"),
    ("cupboard", "pw:furn_cupboard_oak", {}, "minecraft:cardinal_direction"),
    ("dresser", "pw:furn_dresser_oak", {}, "minecraft:cardinal_direction"),
    ("shelf", "pw:furn_shelf_oak", {}, "minecraft:cardinal_direction"),
    ("wall shelf", "pw:furn_wall_shelf_oak", {}, "minecraft:cardinal_direction"),
    ("coat pegs", "pw:furn_coat_pegs_oak", {}, "minecraft:cardinal_direction"),
    ("mantel", "pw:furn_mantel_oak", {}, "minecraft:cardinal_direction"),
    ("seated stairs (pw:facing)", "pw:seated_oak_stairs", {"pw:snow": 0}, "pw:facing"),
    ("snowcap stairs (pw:facing)", "pw:snowcap_stairs", {"pw:level": 1}, "pw:facing"),
]
TW, TH = 300, 230


def tile(block, states):
    man = {"datum_y": 1, "blocks": [[x, 0, z, "minecraft:smooth_stone", {}] for x in range(3) for z in range(3)]
           + [[1, 1, 1, block, states], [1, 1, 0, "marker:n", {}]]}
    items = CR.scene(man, min_feet=-1)
    eye = (1.5 * 16 + 2.6 * 16, 1 * 16 + 2.4 * 16, 1.5 * 16 + 2.6 * 16)
    return Image.fromarray(CR.render(items, eye, (1.5 * 16, 1 * 16 + 8, 1.5 * 16), W=TW, H=TH, fov=38))


def main():
    per = 13
    for s in range(0, len(ROWS), per):
        chunk = ROWS[s:s + per]
        sheet = Image.new("RGB", (4 * (TW + 8) + 220, 36 + len(chunk) * (TH + 8)), (22, 22, 26))
        d = ImageDraw.Draw(sheet)
        d.text((10, 10), "BLOCK FACINGS (true engine rotation, D-C487) - red strip = NORTH side of the cell - camera from the SOUTH-EAST", fill=(240, 240, 240))
        for i, dn in enumerate(DIRS):
            d.text((220 + i * (TW + 8) + 8, 22), f"state {dn}", fill=(255, 210, 120))
        for r, (label, block, extra, key) in enumerate(chunk):
            y = 36 + r * (TH + 8)
            d.text((10, y + TH // 2 - 6), label, fill=(240, 240, 240))
            d.text((10, y + TH // 2 + 8), block, fill=(150, 150, 160))
            for i, dn in enumerate(DIRS):
                st = dict(extra, **{key: dn})
                try:
                    im = tile(block, st)
                except Exception as e:  # noqa: BLE001
                    im = Image.new("RGB", (TW, TH), (60, 20, 20))
                    ImageDraw.Draw(im).text((8, 8), str(e)[:60], fill=(255, 200, 200))
                sheet.paste(im, (220 + i * (TW + 8), y))
        out = Path(f"/mnt/user-data/outputs/BLOCK-FACINGS-{s // per + 1}.png")
        sheet.save(out)
        print(out, sheet.size)


if __name__ == "__main__":
    main()
