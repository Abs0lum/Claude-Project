#!/usr/bin/env python3
"""street_ramp_preview.py — the new t_ramp8 street piece and the sidewalk-fixed t_ramp7 between flat straights, rendered with
the staged ramp blocks (his look before anything ships)."""
import os, shutil, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
os.environ["PW_STACK"] = "final"
sys.path.insert(0, "/home/claude/tools")
import civ_render as CR  # noqa: E402
import mcstructure as M  # noqa: E402
ST = Path("/home/claude/_staging/ramps228")
TMP = Path("/tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad/ramp8blocks")
if TMP.exists(): shutil.rmtree(TMP)
TMP.mkdir(parents=True)
for f in Path("/home/claude/_build/bp02-227/blocks").glob("*.json"): shutil.copy2(f, TMP / f.name)
for f in (ST / "bp/blocks").glob("*.json"): shutil.copy2(f, TMP / f.name)
CR.BP = TMP
# the renderer has no stair shapes: the vanilla stair curb and our seated stair curb as solid grey blocks (preview only)
for _n in ("minecraft:stone_brick_stairs", "pw:seated_stone_brick_stairs", "minecraft:stone_brick_slab", "minecraft:smooth_stone_slab"):
    CR.VCOL[_n] = (128, 128, 132)
    if "slab" in _n: CR.VTHIN[_n] = (-8, 0, -8, 16, 8, 16)
CR.RP_MODELS = [ST / "rp/models/blocks", Path("/home/claude/_build/rp04-158/models/blocks")]
for f in (ST / "rp/textures/blocks").glob("*.png"):
    if not f.stem.endswith(("_n", "_mer")): CR._tex[f.stem] = np.asarray(Image.open(f).convert("RGBA")).astype(np.float32) / 255.0
for f in Path("/home/claude/_build/rp04-158/textures/blocks").glob("pw_*.png"):
    if not f.stem.endswith(("_n", "_mer")): CR._tex.setdefault(f.stem, np.asarray(Image.open(f).convert("RGBA")).astype(np.float32) / 255.0)
ROAD = Path("/home/claude/_build/bp02-227/structures/pw/road"); NEW = Path("/home/claude/tools/bp02_overlay_228/structures/pw/road")

def blocks_of(path, ox, oy, oz):
    st = M.Structure.from_bytes(path.read_bytes()); out = []
    sx, sy, sz = st.size
    for x in range(sx):
        for y in range(10, sy):
            for z in range(sz):
                e = st.get(x, y, z)
                if not e or e[0] in ("minecraft:air", "minecraft:structure_void"): continue
                out.append([ox + x, oy + y, oz + z, e[0], {k: getattr(v, "value", v) for k, v in e[1].items()}])
    return out, sx

def street(ramp_file, oz):
    B, x = [], 0
    for _ in range(3):
        b, n = blocks_of(ROAD / "t_straight1.mcstructure", x, 0, oz); B += b; x += n
    b, n = blocks_of(ramp_file, x, 0, oz); B += b; x += n
    for _ in range(3):
        b, n = blocks_of(ROAD / "t_straight1.mcstructure", x, 1, oz); B += b; x += n
    return B, x

B1, L1 = street(NEW / "t_ramp8.mcstructure", 0)
B2, L2 = street(NEW / "t_ramp7.mcstructure", 16)
items = CR.scene({"datum_y": 10, "blocks": B1 + B2}, min_feet=0)
views = [("from the south-west, above: front street = new ramp8, back street = ramp7 with ramp sidewalks", (-4 * 16, 22 * 16, -9 * 16), (8 * 16, 14 * 16, 14 * 16)),
         ("ramp8 street from the low end, at eye level", (-3 * 16, 16.2 * 16, 6.5 * 16), (10 * 16, 15 * 16, 6.5 * 16)),
         ("ramp7 street: the new sidewalk ramps (left and right)", (-2 * 16, 16.5 * 16, 22.5 * 16), (8 * 16, 15 * 16, 22.5 * 16))]
tiles = []
for title, eye, tgt in views:
    im = Image.fromarray(CR.render(items, eye, tgt, W=760, H=420, fov=55))
    ImageDraw.Draw(im).text((8, 6), title, fill=(0, 0, 0)); tiles.append(im)
sheet = Image.new("RGB", (760, 3 * 425), (20, 20, 24))
for i, t in enumerate(tiles): sheet.paste(t, (0, i * 425))
out = "/home/claude/_docs/program228/STREET-RAMP8-PREVIEW-v1.png"
sheet.save(out); print(out)
