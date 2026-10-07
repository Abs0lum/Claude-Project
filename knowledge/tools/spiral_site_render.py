#!/usr/bin/env python3
"""spiral_site_render.py — the engine-law render (spiral_pad_render's laws: permutation -> geometry, file x mirrored, the
transformation right-handed in world coords) of ANY structure holding main-pack spiral blocks (lowercase ids from
tools/bp02_overlay_228/blocks, geometry + textures from _staging/spiral228/rp). Other blocks: plain cubes coloured by
kind (floor planks, walls stone, door-floor marker red). render(st, out, views, title)"""
import json, re, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402
import block_render as BR  # noqa: E402
import civ_render as CR  # noqa: E402

OVB = Path("/home/claude/tools/bp02_overlay_228/blocks")
RP = Path("/home/claude/_staging/spiral228/rp")
RP04 = Path("/home/claude/_build/rp04-159/textures/blocks")
CUBE_TEX = {"minecraft:spruce_planks": "spruce_planks_v1", "minecraft:red_wool": "_red", "minecraft:stone_bricks": "stone_bricks",
            "minecraft:smooth_stone": "smooth_stone_v0"}


def derived_tex(name):
    """a cube's texture from its id: RP-04's <stem>.png or <stem>_v0.png, else stone bricks"""
    stem = name.split(":")[-1]
    for c in (stem, stem + "_v0", stem.replace("_block", ""), stem + "_side"):
        if (RP04 / f"{c}.png").exists(): return c
    return "stone_bricks"


def tex_loader():
    import numpy as np
    def _tex(stem, frame=0):
        key = (stem, frame)
        if key in BR._texcache: return BR._texcache[key]
        if stem == "_red":
            a = np.zeros((16, 16, 4), "float32"); a[..., 0] = 0.8; a[..., 1] = 0.15; a[..., 2] = 0.1; a[..., 3] = 1
        else:
            p = RP / "textures/blocks/pw_spiral" / f"{stem}.png"
            if not p.exists(): p = RP04 / f"{stem}.png"
            if not p.exists(): p = RP04 / "stone_bricks.png"
            a = np.asarray(Image.open(p).convert("RGBA")).astype("float32") / 255.0
        BR._texcache[key] = a
        return a
    BR.texture = _tex


def render(st, out, views, title, skip=lambda x, y, z, name: False):
    tex_loader()
    blocks = {}
    for f in OVB.glob("pw_spiral_stairs_*.json"):
        d = json.loads(f.read_text())["minecraft:block"]
        blocks[d["description"]["identifier"]] = d
    geo_path = RP / "models/blocks/pw_spiral_stairs.geo.json"
    face_cache, faces, mats = {}, [], {}
    sx, sy, sz = st.size
    n_blocks = 0
    for x in range(sx):
        for y in range(sy):
            for z in range(sz):
                e = st.get(x, y, z)
                if not e: continue
                name, states, _ = e
                if name in ("minecraft:air", "minecraft:structure_void") or skip(x, y, z, name): continue
                sv = {k: v.value for k, v in states.items()}
                if name not in blocks:
                    t = CUBE_TEX.get(name) or derived_tex(name)
                    mats[t] = {"texture": t}
                    for fc in BR.corners([x * 16, y * 16, z * 16], [16, 16, 16], 0).items():
                        faces.append(BR.Face(fc[1], (0, 0, 1, 1), t, fc[0], "cube"))
                    continue
                bd = blocks[name]
                perm = None
                for p in bd["permutations"]:
                    c = p["condition"]
                    if all(re.search(rf"q\.block_state\('{re.escape(k)}'\) == '?{re.escape(str(v))}'?( |$)", c + " ") for k, v in sv.items()):
                        perm = p; break
                if perm is None: raise SystemExit(f"no permutation for {name} {sv}")
                gid = perm["components"]["minecraft:geometry"]["identifier"]
                rot = perm["components"]["minecraft:transformation"]["rotation"]
                if gid not in face_cache: face_cache[gid] = BR.load_faces(geo_path, gid)
                pal = name.replace("pw:spiral_stairs_", "").split("_", 2)[-1]
                for inst, m in bd["components"]["minecraft:material_instances"].items():
                    mats[f"{pal}:{inst}"] = {"texture": m["texture"]}
                for f in face_cache[gid]:
                    pts = []
                    for p in f.pts:
                        w = CR.xform_world([-p[0], p[1], p[2]], rot, (0, 8, 0))
                        pts.append([w[0] + x * 16 + 8, w[1] + y * 16, w[2] + z * 16 + 8])
                    faces.append(BR.Face(pts[::-1], f.uv, f"{pal}:{f.mat}", f.name, f.bone))
                n_blocks += 1
    W, H = 1000, 700
    tiles = [(nm, Image.fromarray(BR.render(faces, mats, e, t, W, H, fov=50)[0])) for nm, e, t in views]
    sheet = Image.new("RGB", (W * min(2, len(tiles)), (H + 40) * ((len(tiles) + 1) // 2) + 50), (14, 13, 12))
    d = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    d.text((10, 10), f"{title} · {n_blocks} stair blocks (engine laws)", fill=(235, 225, 200), font=font)
    for k, (nm, im) in enumerate(tiles):
        ox, oy = (k % 2) * W, 50 + (k // 2) * (H + 40)
        sheet.paste(im, (ox, oy))
        d.text((ox + 10, oy + 6), nm, fill=(255, 240, 160), font=font)
    sheet.save(out)
    print("wrote", out, n_blocks, "stair blocks")
