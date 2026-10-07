#!/usr/bin/env python3
"""spiral_pad_render.py — render the BUILT test pad the way the ENGINE will assemble it, independently of spiral_gen's
own preview: read pw:spiral_pad.mcstructure back from bytes, resolve every block's permutation from its BP block JSON
(geometry id + transformation), load the geometry from the RP file, and place it under the MEASURED laws:
file x mirrored into the world (L-ROT-DIR), then minecraft:transformation right-handed in world coords about the block
centre (D-C487, civ_render.xform_world). A broken quarter / wrong hand / wrong cell shows as a broken helix here.
Usage: spiral_pad_render.py OUT.png"""
import json, math, re, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402
import block_render as BR  # noqa: E402
import spiral_gen as SG  # noqa: E402  (texture loader hook only)
import civ_render as CR  # noqa: E402

BP = Path("/home/claude/_build/spiraltest-0.0.3-bp")
RP = Path("/home/claude/_build/spiraltest-0.0.3-rp")


def tex_loader():
    base = RP / "textures/blocks/pw_spiral"
    def _tex(stem, frame=0):
        key = (stem, frame)
        if key in BR._texcache: return BR._texcache[key]
        p = base / f"{stem}.png"
        if not p.exists(): p = Path("/home/claude/_build/rp04-159/textures/blocks") / f"{stem}.png"
        import numpy as np
        a = np.asarray(Image.open(p).convert("RGBA")).astype("float32") / 255.0
        BR._texcache[key] = a
        return a
    BR.texture = _tex


def main(out):
    tex_loader()
    st = M.Structure.from_bytes((BP / "structures/pw/spiral_pad.mcstructure").read_bytes())
    blocks = {}
    for f in (BP / "blocks").glob("*.json"):
        d = json.loads(f.read_text())["minecraft:block"]
        blocks[d["description"]["identifier"]] = d
    geo_path = RP / "models/blocks/pw_spiral_stairs.geo.json"
    face_cache = {}
    faces, mats = [], {}
    sx, sy, sz = st.size
    n_blocks = 0
    for x in range(sx):
        for y in range(sy):
            for z in range(sz):
                e = st.get(x, y, z)
                if not e: continue
                name, states, _ = e
                sv = {k: v.value for k, v in states.items()}
                if name not in blocks:
                    if y == 0: continue                              # the floor: drawn as one plane below
                    for fc in BR.corners([x * 16, y * 16, z * 16], [16, 16, 16], 0).items():
                        faces.append(BR.Face(fc[1], (0, 0, 1, 1), "_plank", fc[0], "plank"))
                    continue
                bd = blocks[name]
                perm = None
                for p in bd["permutations"]:
                    c = p["condition"]
                    ok = all(re.search(rf"q\.block_state\('{re.escape(k)}'\) == '?{re.escape(str(v))}'?( |$)", c + " ") for k, v in sv.items())
                    if ok: perm = p; break
                if perm is None: raise SystemExit(f"no permutation for {name} {sv}")
                gid = perm["components"]["minecraft:geometry"]["identifier"]
                rot = perm["components"]["minecraft:transformation"]["rotation"]
                if gid not in face_cache: face_cache[gid] = BR.load_faces(geo_path, gid)
                pal = name.split("_", 4)[-1] if False else name.replace("pw:spiral_stairs_", "").split("_", 2)[-1]
                for inst, m in bd["components"]["minecraft:material_instances"].items():
                    mats[f"{pal}:{inst}"] = {"texture": m["texture"]}
                for f in face_cache[gid]:
                    pts = []
                    for p in f.pts:
                        w = [-p[0], p[1], p[2]]                              # file x mirrored into the world
                        w = CR.xform_world(w, rot, (0, 8, 0))                # the transformation, world law
                        pts.append([w[0] + x * 16 + 8, w[1] + y * 16, w[2] + z * 16 + 8])
                    faces.append(BR.Face(pts[::-1] if True else pts, f.uv, f"{pal}:{f.mat}", f.name, f.bone))
                n_blocks += 1
    mats["_plank"] = {"texture": "spruce_planks_v1"}
    mats["_floor"] = {"texture": "smooth_stone_v0"}
    floor = [BR.Face([[0, 16, 0], [sx * 16, 16, 0], [sx * 16, 16, sz * 16], [0, 16, sz * 16]], (0, 0, sx, sz), "_floor", "up", "_s")]
    W, H = 1100, 760
    cx, cz = sx * 8, sz * 8
    views = [("the pad from the south-east, above", (cx + 120, 260, cz + 420), (cx, 70, cz)),
             ("the pad from the north-west, low", (cx - 150, 60, cz - 420), (cx, 80, cz))]
    tiles = [(n, Image.fromarray(BR.render(faces + floor, mats, e, t, W, H, fov=50)[0])) for n, e, t in views]
    sheet = Image.new("RGB", (W, H * 2 + 90), (14, 13, 12))
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    d.text((10, 8), f"pw:spiral_pad as the ENGINE assembles it (structure bytes -> permutations -> geometry, world laws) · {n_blocks} stair blocks", fill=(235, 225, 200), font=font)
    for k, (nm, im) in enumerate(tiles):
        sheet.paste(im, (0, 44 + k * (H + 40)))
        d.text((10, 44 + k * (H + 40) + 6), nm, fill=(255, 240, 160), font=font)
    sheet.save(out)
    print("wrote", out, n_blocks, "blocks")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "/home/claude/_docs/program228/spiral/SPIRAL-PAD-ENGINE-v1.png")
