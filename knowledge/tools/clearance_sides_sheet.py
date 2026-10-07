#!/usr/bin/env python3
"""clearance_sides_sheet.py — his C1 (15:42 CT 10-02): show the cottage clearance column on the LEFT (as his r0 file
has it) versus the RIGHT (the written save-box rule), seen the way he would see it: standing in the street, facing the
front door. Reads his r0 template (Proving Grounds 09-28 world DB copy) and draws, for each option, a front view
(the street side, x = 0 wall) and a plan view from above. Output: /mnt/user-data/outputs/CLEARANCE-COLUMN-LEFT-vs-RIGHT.png"""
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402

R0 = "/tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad/r0.mcstructure"
DATUM_Y = 15
CELL = 34
COLOURS = {"air": None, "grass_block": (96, 150, 70), "cobblestone": (120, 120, 120), "oak_planks": (176, 140, 88),
           "spruce_log": (92, 66, 40), "wooden_door": (150, 105, 60), "glass_pane": (170, 210, 230),
           "stone_bricks": (130, 130, 130), "dirt": (120, 85, 60), "smooth_stone": (160, 160, 160)}
CLEAR = (255, 200, 60)


def name_at(structure, x, y, z):
    block = structure.get(x, y, z)
    if not block:
        return "air"
    full = block[0] if isinstance(block, tuple) else str(block)
    return full.split(":")[-1]


def colour_for(name):
    if name in COLOURS:
        return COLOURS[name]
    if "roof" in name:
        return (70, 50, 35)
    if "light_block" in name:
        return None
    return (200, 170, 120)


def front_view(structure, mirror):
    """Street view of the x = 0 wall. Viewer faces +x (east), so screen-left = z = 0 (north). Mirror flips z."""
    sx, sy, sz = structure.size
    img = Image.new("RGB", (sz * CELL, (sy - 13) * CELL), (210, 225, 240))
    draw = ImageDraw.Draw(img)
    for y in range(13, sy):
        for z in range(sz):
            col = z if not mirror else sz - 1 - z
            # first non-air block seen from the street along +x
            name = "air"
            for x in range(sx):
                n = name_at(structure, x, y, z)
                if n != "air" and colour_for(n):
                    name = n
                    break
            top = (sy - 1 - y) * CELL
            c = colour_for(name)
            if c:
                draw.rectangle((col * CELL, top, col * CELL + CELL - 1, top + CELL - 1), fill=c, outline=(40, 40, 40))
        clear_col = 0 if not mirror else sz - 1
    draw.rectangle((clear_col * CELL, 0, clear_col * CELL + CELL - 1, img.size[1] - 1), outline=CLEAR, width=4)
    return img


def plan_view(structure, mirror):
    """Ground floor seen from above; the street is at the BOTTOM, the viewer looks up the page (toward +x)."""
    sx, sy, sz = structure.size
    img = Image.new("RGB", (sz * CELL, sx * CELL), (230, 230, 230))
    draw = ImageDraw.Draw(img)
    for x in range(sx):
        for z in range(sz):
            col = z if not mirror else sz - 1 - z
            row = sx - 1 - x
            n15 = name_at(structure, x, DATUM_Y, z)
            n14 = name_at(structure, x, DATUM_Y - 1, z)
            c = colour_for(n15) if n15 != "air" else colour_for(n14)
            draw.rectangle((col * CELL, row * CELL, col * CELL + CELL - 1, row * CELL + CELL - 1),
                           fill=c or (230, 230, 230), outline=(60, 60, 60))
            if n15 == "wooden_door":
                draw.text((col * CELL + 6, row * CELL + 10), "door", fill=(0, 0, 0))
    clear_col = 0 if not mirror else sz - 1
    draw.rectangle((clear_col * CELL, 0, clear_col * CELL + CELL - 1, img.size[1] - 1), outline=CLEAR, width=4)
    return img


def main():
    structure = M.Structure.from_bytes(open(R0, "rb").read())
    panels = []
    for mirror, title in ((False, "A  LEFT  (your r0 file today)"), (True, "B  RIGHT  (the written save-box rule)")):
        fv, pv = front_view(structure, mirror), plan_view(structure, mirror)
        w = max(fv.size[0], pv.size[0]) + 40
        h = 40 + fv.size[1] + 40 + pv.size[1] + 70
        panel = Image.new("RGB", (w, h), (28, 28, 28))
        d = ImageDraw.Draw(panel)
        d.text((10, 10), title, fill=(255, 220, 120))
        d.text((10, 26), "From the street, facing the front door:", fill="white")
        panel.paste(fv, (20, 44))
        y2 = 44 + fv.size[1] + 10
        d.text((10, y2), "From above (street at the bottom):", fill="white")
        panel.paste(pv, (20, y2 + 18))
        d.text((10, y2 + 24 + pv.size[1]), "STREET  -  you stand here, facing up the page", fill=(160, 220, 255))
        d.text((10, y2 + 40 + pv.size[1]), "yellow outline = the empty clearance column", fill=CLEAR)
        panels.append(panel)
    out = Image.new("RGB", (sum(p.size[0] for p in panels) + 30, max(p.size[1] for p in panels)), (18, 18, 18))
    x = 0
    for p in panels:
        out.paste(p, (x, 0))
        x += p.size[0] + 30
    out = out.resize((out.size[0] * 2, out.size[1] * 2), Image.NEAREST)
    out.save("/mnt/user-data/outputs/CLEARANCE-COLUMN-LEFT-vs-RIGHT.png")
    print(out.size)


if __name__ == "__main__":
    main()
