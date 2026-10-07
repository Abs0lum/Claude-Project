#!/usr/bin/env python3
"""leaf_cut_preview.py — LEAF PROTOCOL render for the full block-state cut (his R17 answer 6: "we can perform the full cut").
Read-only render of RP-01 1.3.104's leaf geometries (the RP does not change): once pw:open_n/e/s/w and bone_visibility go, every
leaf shows ALL its corner fillers. A leaf with canopy on both sides looks exactly as today; only a leaf whose north or south side
faces AIR changes — its fillers there (1-6 cubes reaching 4-6 px into the air cell) now show. East / west carry no fillers in any
variant (census D-C315). Output: _docs/leaves/LEAF-CUT-BEFORE-AFTER.png."""
import copy, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML
from bb_truth import truth_posed_faces
from entity_tex_render import render_entity
from convb_preview3 import camera, FOV
from equine_compare import bone_affines

RP = Path("/home/claude/_build/rp01-104"); OUT = Path("/home/claude/_docs/leaves"); TMP = Path("/tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad")
W, H = 330, 290
FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13); FR = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)


def geo(fname, gid):
    d = ML._parse_json((RP / "models/blocks" / fname).read_text())
    return next(g for g in d["minecraft:geometry"] if g["description"]["identifier"] == gid)


def tex(name):
    p = RP / "textures/blocks" / (name + ".png")
    if not p.exists(): p = RP / "textures/blocks/pw_oak_leaves_v1.png"
    q = TMP / (p.stem + "_rgba.png"); Image.open(p).convert("RGBA").save(q); return q


def hidden(bones, hide):
    bones = copy.deepcopy(bones); by = {b["name"]: b for b in bones}
    for b in bones:
        p = b["name"]
        while p:
            if p in hide: b["cubes"] = []; break
            p = by[p].get("parent")
    return bones


def main():
    rows = []
    for label, fname, gid, tname in (("OAK v1", "pw_leaves_variants.geo.json", "geometry.pw_leaves_v1", "pw_oak_leaves_v1"),
                                     ("OAK v4", "pw_leaves_variants.geo.json", "geometry.pw_leaves_v4", "pw_oak_leaves_v4"),
                                     ("JUNGLE v2", "pw_leaves_jungle_variants.geo.json", "geometry.pw_leaves_jungle_v2", "pw_jungle_leaves_v2")):
        g = geo(fname, gid); tw, th = g["description"]["texture_width"], g["description"]["texture_height"]; tp = tex(tname)
        allf = truth_posed_faces(g["bones"], tw, th, bone_affines(g["bones"]))
        cells = []
        for view, vname in (("top", "from above, camera leaning north: NORTH IS AT THE BOTTOM"), ("front", "from the north side, level")):
            e, t = camera(allf, view, pad=1.6)
            for state, hide, col in (("TODAY - edge leaf, air to the north", {"pw_nf"}, (120, 70, 20)), ("AFTER THE CUT - same leaf", set(), (30, 90, 40))):
                bones = hidden(g["bones"], hide)
                img = render_entity(truth_posed_faces(bones, tw, th, bone_affines(bones)), tp, e, t, W, H, fov=FOV, floor_y=0.0).convert("RGB")
                d = ImageDraw.Draw(img); d.rectangle([0, 0, W, 34], fill=col)
                d.text((6, 2), f"{label}: {state}", fill=(255, 255, 255), font=FB); d.text((6, 19), vname, fill=(235, 235, 235), font=FR)
                cells.append(img)
        row = Image.new("RGB", (4 * (W + 4) - 4, H), (255, 255, 255))
        for i, c in enumerate(cells): row.paste(c, (i * (W + 4), 0))
        rows.append(row)
    out = Image.new("RGB", (rows[0].width, len(rows) * (H + 4) - 4 + 46), (255, 255, 255)); d = ImageDraw.Draw(out)
    d.text((6, 4), "LEAF STATE FULL CUT — only a leaf whose NORTH or SOUTH side faces air changes: its corner fillers there now show (4-6 px into the air cell).", fill=(20, 20, 20), font=FB)
    d.text((6, 24), "Leaves with canopy on both sides: identical to today. East / west: no fillers in any variant. Variant 0 (the far cube) and v3 (inner) have none.", fill=(20, 20, 20), font=FR)
    for i, r in enumerate(rows): out.paste(r, (0, 46 + i * (H + 4)))
    OUT.mkdir(parents=True, exist_ok=True); p = OUT / "LEAF-CUT-BEFORE-AFTER.png"; out.save(p); print(p)


if __name__ == "__main__":
    main()
