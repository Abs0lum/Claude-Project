#!/usr/bin/env python3
"""fidelity_sheet.py — 1d of the R15 round (his "Go on all", D-C309): the six Patrix-fidelity mobs, SHIPPED geometry next to
the Patrix 26.2 JEM (Converter B bake), rest pose, one shared camera per view so sizes compare 1:1, each drawn with the
SHIPPED texture. Plus a texture-compatibility number: the share of the bake's cube faces whose UV rectangle lands on painted
texels of the shipped texture (a bake that needs a different texture layout shows up here).
Output: _docs/fidelity/FIDELITY-<mob>.png + FIDELITY-SUMMARY.json"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import fa_preview as FP
from equine_compare import bone_affines
from bb_truth import truth_posed_faces, face_uvs
from entity_tex_render import render_entity
from convb_preview3 import camera, FOV

OUT = Path("/home/claude/_docs/fidelity"); OUT.mkdir(parents=True, exist_ok=True)
W, H = 560, 420
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
MOBS = [("fox", Path("/home/claude/_build/rp07-1427")), ("goat", Path("/home/claude/_build/rp07-1427")),
        ("cat", Path("/home/claude/_build/rp07-1427")), ("ocelot", Path("/home/claude/_build/rp07-1427")),
        ("cod", Path("/home/claude/_build/rp07-1427")), ("iron_golem", Path("/home/claude/_build/rp07-1427")),
        ("hoglin", Path("/home/claude/_build/rp06-1421")), ("zoglin", Path("/home/claude/_build/rp06-1421"))]


def shot(bones, tw, th, tex, cam, label):
    f = truth_posed_faces(bones, tw, th, bone_affines(bones))
    fl = min(0.0, min(q[1] for x in f for q in x.pts))
    im = render_entity(f, tex, cam[0], cam[1], W, H, fov=FOV, floor_y=fl).convert("RGB")
    d = ImageDraw.Draw(im); d.rectangle([0, 0, W, 20], fill=(30, 40, 60)); d.text((5, 3), label, fill=(255, 255, 255), font=F)
    return im


def uv_coverage(bones, tw, th, tex):
    """share of face UV rectangles (of the bake) that hit painted texels (alpha > 0) in the shipped texture"""
    img = np.asarray(Image.open(tex).convert("RGBA")); ih, iw = img.shape[:2]; sx, sy = iw / tw, ih / th
    hit = tot = 0
    for b in bones:
        for c in b.get("cubes", []) or []:
            for face, (u1, v1, u2, v2) in face_uvs(c.get("uv"), c["size"], bool(c.get("mirror", b.get("mirror", False)))).items():
                a0, a1 = sorted((u1, u2)); b0, b1 = sorted((v1, v2))
                if a1 - a0 < 1e-6 or b1 - b0 < 1e-6: continue
                x0, x1 = int(np.floor(a0 * sx)), int(np.ceil(a1 * sx)); y0, y1 = int(np.floor(b0 * sy)), int(np.ceil(b1 * sy))
                reg = img[max(0, y0):min(ih, y1), max(0, x0):min(iw, x1), 3]
                tot += 1; hit += int(reg.size > 0 and (reg > 0).mean() > 0.5)
    return round(hit / tot, 3) if tot else None


def main():
    summary = {}
    for mob, D in MOBS:
        desc = R.jl(D / f"entity/{mob}.entity.json")["minecraft:client_entity"]["description"]
        gid = desc["geometry"].get("default") or list(desc["geometry"].values())[0]
        tex_key = list(desc["textures"].values())[0]
        tex = D / (tex_key + ".png")
        _, g = R.geo_file(D, gid) if (D / "models/entity").exists() else (None, None)
        ours = g["bones"]; tw, th = g["description"]["texture_width"], g["description"]["texture_height"]
        pb, ptw, pth, info = FP.bake_any(mob, "26.2")
        cov_bake = uv_coverage(pb, ptw, pth, tex); cov_ours = uv_coverage(ours, tw, th, tex)
        rows = []
        for view in ("east", "front", "top"):
            f_all = truth_posed_faces(ours, tw, th, bone_affines(ours)) + truth_posed_faces(pb, ptw, pth, bone_affines(pb))
            cam = camera(f_all, view)
            rows.append((shot(ours, tw, th, tex, cam, f"SHIPPED {mob} ({gid}) - {view}"),
                         shot(pb, ptw, pth, tex, cam, f"PATRIX 26.2 JEM bake - {view} (shipped texture)")))
        sheet = Image.new("RGB", (2 * W + 6, len(rows) * (H + 6)), (255, 255, 255))
        for i, (a, b) in enumerate(rows): sheet.paste(a, (0, i * (H + 6))); sheet.paste(b, (W + 6, i * (H + 6)))
        p = OUT / f"FIDELITY-{mob}.png"; sheet.save(p)
        summary[mob] = {"geometry": gid, "texture": tex_key, "tex_size_geo": [tw, th], "tex_size_bake": [ptw, pth],
                        "uv_cover_shipped": cov_ours, "uv_cover_bake_on_shipped_texture": cov_bake,
                        "cubes_shipped": sum(len(b.get("cubes", [])) for b in ours), "cubes_bake": sum(len(b.get("cubes", [])) for b in pb)}
        print(mob, summary[mob], p, flush=True)
    json.dump(summary, open(OUT / "FIDELITY-SUMMARY.json", "w"), indent=1)


if __name__ == "__main__":
    main()
