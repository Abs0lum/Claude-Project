#!/usr/bin/env python3
"""palace_spiral_render.py — program 228: images of the palace's spiral sites (engine-law stair geometry via
spiral_site_render; other blocks plain coloured cubes). For each site: an oblique cutaway (everything above the top
storey's head height removed, the near half of the walls on the camera side cut) and a straight-down plan at every
storey it serves (blocks above that storey's head height removed). Doors marked red, the floor in front marked blue.
Usage: palace_spiral_render.py [label-substring ...]"""
import sys
sys.path.insert(0, "/home/claude/tools")
import palacegen as PG
import spiral_site_render as R
import mcstructure as M

R.CUBE_TEX.update({"minecraft:blue_wool": "_blue"})
_orig = R.tex_loader
def tex_loader():
    _orig()
    import numpy as np
    f = R.BR.texture
    def t(stem, frame=0):
        if stem == "_blue":
            a = np.zeros((16, 16, 4), "float32"); a[..., 2] = 0.85; a[..., 1] = 0.35; a[..., 3] = 1; return a
        return f(stem, frame)
    R.BR.texture = t
R.tex_loader = tex_loader


def main(want):
    p = PG.build()
    for sp in p.spirals:
        if want and not any(w in sp["label"] for w in want): continue
        x0, z0, x1, z1 = sp["well"]
        X0, X1, Z0, Z1 = max(0, x0 - 7), min(127, x1 + 7), max(0, z0 - 7), min(127, z1 + 7)
        top = sp["floors"][-1]
        F0 = sp["f0"] - 1
        sx, sz = X1 - X0 + 1, Z1 - Z0 + 1
        st = M.Structure((sx, top - F0 + 4, sz))
        for x in range(X0, X1 + 1):
            for z in range(Z0, Z1 + 1):
                for f in range(F0, top + 3):
                    e = p.st.get(x, p.y(f), z)
                    if e and e[0] not in ("minecraft:air", "minecraft:structure_void", "minecraft:light_block_14"):
                        st.set(x - X0, f - F0, z - Z0, e[0], {k: v for k, v in e[1].items()})
        for d in sp["doors"]:
            st.set(d["cell"][0] - X0, d["feet"] - 1 - F0, d["cell"][1] - Z0, "minecraft:red_wool", {})
        for (x, f, z) in sp["landing"]:
            if not (x0 <= x <= x1 and z0 <= z <= z1):
                st.set(x - X0, f - F0, z - Z0, "minecraft:blue_wool", {})
        cx, cz = ((x0 + x1 + 1) / 2 - X0) * 16, ((z0 + z1 + 1) / 2 - Z0) * 16
        H = (top - F0) * 16
        views = [("cutaway from the south-east (walls south/east of the well cut, roof off)", (cx + 330, H + 260, cz + 420), (cx, H / 2, cz))]
        skips = [lambda x, y, z, n: (y > top - F0 + 2) or ((x + X0) > x1 and n != "minecraft:blue_wool" and n != "minecraft:red_wool" and "spiral" not in n and y > 1) or ((z + Z0) > z1 and "spiral" not in n and n not in ("minecraft:blue_wool", "minecraft:red_wool") and y > 1)]
        R.render(st, f"/home/claude/_docs/program228/spiral/PALACE-{sp['label'].replace(' ', '_')}-v1.png", views,
                 f"palace · {sp['label']} · {sp['design']} {sp['pal']} {sp['hand']} · storeys {sp['floors']} (red = door beside the step, blue = floor in front)", skips[0])
        tiles = []
        for S in [sp["f0"]] + sp["floors"]:
            lv = S - F0
            R.render(st, f"/tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad/plan_{S}.png",
                     [(f"storey walking level {S}, straight down (north up)", (cx, lv * 16 + 520, cz + 90), (cx, lv * 16, cz))],
                     f"{sp['label']} · storey {S}", lambda x, y, z, n, lv=lv: y > lv + 1)
            tiles.append(f"/tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad/plan_{S}.png")
        from PIL import Image
        ims = [Image.open(t) for t in tiles]
        w = sum(i.width for i in ims); h = max(i.height for i in ims)
        sheet = Image.new("RGB", (w, h), (14, 13, 12))
        ox = 0
        for i in ims: sheet.paste(i, (ox, 0)); ox += i.width
        sheet.save(f"/home/claude/_docs/program228/spiral/PALACE-{sp['label'].replace(' ', '_')}-plans-v1.png")
        print(sp["label"], "rendered")


if __name__ == "__main__":
    main(sys.argv[1:])
