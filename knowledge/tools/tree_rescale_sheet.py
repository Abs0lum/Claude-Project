#!/usr/bin/env python3
"""tree_rescale_sheet.py — before/after renders of one template per group (side view, same camera, 1.8 m player for scale)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/claude/tools")
import entity_render as ER  # noqa: E402
import tree_rescale as T  # noqa: E402

def voxels(path):
    _, _, names, cells = T.read(path)
    rootc = next(p for p, pi in cells.items() if names[pi].startswith("pw:") and names[pi].endswith("_root"))
    out = []
    for p, pi in cells.items():
        n = names[pi]
        kind = "wood" if T.is_wood(n) else ("leaf" if T.is_leaf(n) else None)
        if not kind:
            continue
        x, y, z = 16 * (p[0] - rootc[0]), 16 * (p[1] - rootc[1]), -16 * (p[2] - rootc[2])
        out.append((kind, [[x-8,y,z-8],[x+8,y,z-8],[x+8,y+16,z-8],[x-8,y+16,z-8],[x-8,y,z+8],[x+8,y,z+8],[x+8,y+16,z+8],[x-8,y+16,z+8]]))
    # player 1.8 m tall, 0.6 wide, 4 blocks in front of the trunk
    px, pz = 64, 48
    out.append(("player", [[px-5,0,pz-5],[px+5,0,pz-5],[px+5,29,pz-5],[px-5,29,pz-5],[px-5,0,pz+5],[px+5,0,pz+5],[px+5,29,pz+5],[px-5,29,pz+5]]))
    return out

def main():
    src, dst, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    groups = sys.argv[4].split(",")
    cols = {"wood": (105, 75, 48), "leaf": (72, 135, 52), "player": (200, 60, 60)}
    W, Hh = 330, 420
    sheet = Image.new("RGB", (W * 2 * 2 + 30, (Hh + 30) * ((len(groups) + 1) // 2) + 10), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    for i, g in enumerate(groups):
        name = f"{g}_00.mcstructure"
        ox, oy = (i % 2) * (W * 2 + 30), (i // 2) * (Hh + 30)
        for j, (lab, base) in enumerate((("BEFORE", src), ("AFTER", dst))):
            vx = voxels(base / name)
            eye, tgt = [0, 230, 900], [0, 230, 0]
            im = ER.render(vx, eye, tgt, fov=50, size=(W, Hh), colours=cols, ground=0, outline=False)
            sheet.paste(im, (ox + j * W, oy + 25))
            d.text((ox + j * W + 6, oy + 6), f"{g}_00  {lab}", fill=(0, 0, 0))
    sheet.save(out)
    print("saved", out)

if __name__ == "__main__":
    main()
