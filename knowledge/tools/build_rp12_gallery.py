#!/usr/bin/env python3
"""build_rp12_gallery.py — RP-12 "AbsolutRealism Gallery" (D-C571 v2; RP-08 is the ITEMS pack — the gallery was first built under that number by mistake, 10-05 09:1x): one client entity + one framed JPEG texture per work
of the catalogue (_intake/art/catalogue.json after art_catalogue.py), the frame geometries (one per class w x h, four
facing bones), the render controller (part visibility by pw:facing), the connoisseur's book icon + lang.
Why a pack of its own: RP-01 stays at its size; the gallery can be left out on a slow download.
Why one entity type per work: a texture is loaded when its entity type is first rendered, so a world only loads what
hangs near the player (lesson candidate LC-GAL-1: to be witnessed on PS5 + phone).
Texture: the picture fitted into the class canvas (stretched when the aspect mismatch <= 12 %, else matted on linen),
a period frame drawn in (gilt cassetta < 1600, gilt bevel baroque / rococo / 19th, ebony with a gilt lip for the Dutch /
Flemish), 256 px per block up to 4 blocks (1024 px max), JPEG q85. Palette-free: no terrain atlas cost.
Usage: build_rp12_gallery.py OUT_DIR [--limit=N] [--only=key,key] [--version=1.0.0]
Complexity: O(works x pixels) — a few minutes for ~4,500 works."""
import io
import json
import math
import re
import sys
import time
import uuid
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, "/home/claude/tools")
import art_catalogue as AC  # noqa: E402

CAT = Path("/home/claude/_intake/art/catalogue.json")
NAMESPACE_UUID = uuid.UUID("5e1a9b2c-7d3f-4e6a-9c1b-2a4d6f8e0c13")      # stable pack uuids across rebuilds (uuid5)


def arg(name, default):
    v = next((a.split("=", 1)[1] for a in sys.argv if a.startswith(f"--{name}=")), None)
    return default if v is None else type(default)(v)


def key_id(key):
    """catalogue key 'nga:1236' -> entity id suffix 'nga_1236' (CMA ids like 1944.90 -> 1944_90)"""
    return re.sub(r"[^a-z0-9]+", "_", key.lower())


# ------------------------------------------------------------------------------------------------ the framed texture
def frame_style(rec):
    nat = (rec.get("artist_nat") or "").lower()
    try:
        y = int(rec.get("year") or 1700)
    except (TypeError, ValueError):
        y = 1700
    if any(k in nat for k in ("dutch", "flemish", "netherlandish")) and 1580 <= y <= 1720:
        return "ebony"
    if y < 1600:
        return "cassetta"
    if y >= 1800:
        return "plain"
    return "baroque"


def draw_frame(W, H, B, style, rng):
    """an RGB float array (H, W, 3) of the frame band (B px) with alpha mask; the inside is left to the picture"""
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.minimum(np.minimum(xx, W - 1 - xx), np.minimum(yy, H - 1 - yy)).astype(np.float32)   # distance to the outer edge
    t = np.clip(d / max(1, B - 1), 0, 1)                                                      # 0 outer edge .. 1 inner lip
    if style == "ebony":
        base = np.array([34, 24, 18], np.float32)
        shade = 0.75 + 0.35 * np.sin(t * math.pi) ** 2                                          # a rounded black moulding
        col = base[None, None, :] * shade[..., None]
        lip = (t > 0.86)                                                                        # the gilt inner lip
        gold = np.array([205, 165, 70], np.float32) * (0.8 + 0.3 * np.sin((t - 0.86) / 0.14 * math.pi))[..., None]
        col = np.where(lip[..., None], gold, col)
    else:
        gold = np.array([212, 170, 72], np.float32)
        if style == "cassetta":                                                                  # flat panel between two mouldings
            prof = np.where(t < 0.18, 0.55 + 2.5 * t, np.where(t < 0.82, 0.95 + 0.08 * np.sin(t * 9), 0.6 + 2.2 * (1 - t)))
        elif style == "plain":
            prof = 0.7 + 0.5 * np.clip(np.sin(t * math.pi), 0, 1) ** 1.5
        else:                                                                                    # baroque: deep bevel, bright ridge, dark hollow, inner ridge
            prof = 0.55 + 0.6 * np.sin(t * math.pi * 1.5) ** 2 + 0.25 * np.exp(-((t - 0.3) / 0.06) ** 2) - 0.2 * np.exp(-((t - 0.6) / 0.08) ** 2)
        col = gold[None, None, :] * np.clip(prof, 0.35, 1.25)[..., None]
        if style == "baroque":                                                                  # corner cartouches: a brighter diamond
            cx = np.minimum(xx, W - 1 - xx); cy = np.minimum(yy, H - 1 - yy)
            cart = np.exp(-((cx - B * 0.5) ** 2 + (cy - B * 0.5) ** 2) / (2 * (B * 0.35) ** 2))
            col = col * (1 + 0.25 * cart[..., None])
    col = col + rng.normal(0, 4, col.shape)
    mask = d < B
    return col, mask


def compose(rec, rng):
    fr = rec["frame"]
    W, H = fr["tex"]
    ppb = fr["ppb"]
    B = max(6, round(ppb * 0.09))
    im = Image.open(rec["file"]).convert("RGB")
    iw, ih = W - 2 * B, H - 2 * B
    r_pic = im.width / im.height
    r_box = iw / ih
    mis = abs(math.log(r_pic / r_box))
    canvas = Image.new("RGB", (W, H), (44, 38, 32))
    if mis <= math.log(1.12):
        pic = im.resize((iw, ih), Image.LANCZOS)                       # a small stretch nobody sees
        canvas.paste(pic, (B, B))
        mat = False
    else:                                                              # matted: linen around the picture
        s = min(iw / im.width, ih / im.height)
        pw, ph = max(1, round(im.width * s)), max(1, round(im.height * s))
        pic = im.resize((pw, ph), Image.LANCZOS)
        lin = np.full((H, W, 3), (118, 104, 86), np.float32) + rng.normal(0, 5, (H, W, 3))
        canvas = Image.fromarray(np.clip(lin, 0, 255).astype(np.uint8))
        x0, y0 = B + (iw - pw) // 2, B + (ih - ph) // 2
        canvas.paste(pic, (x0, y0))
        d = ImageDraw.Draw(canvas)
        d.rectangle([x0 - 2, y0 - 2, x0 + pw + 1, y0 + ph + 1], outline=(60, 50, 40), width=2)   # the mat's bevel
        mat = True
    arr = np.asarray(canvas).astype(np.float32)
    col, mask = draw_frame(W, H, B, frame_style(rec), rng)
    arr = np.where(mask[..., None], col, arr)
    # a varnish shadow inside the frame (the rabbet)
    yy, xx = np.mgrid[0:H, 0:W]
    dd = np.minimum(np.minimum(xx, W - 1 - xx), np.minimum(yy, H - 1 - yy)).astype(np.float32) - B
    shadow = np.clip(1 - np.clip(dd, 0, 6) / 6, 0, 1) * (dd >= 0)
    arr = arr * (1 - 0.35 * shadow)[..., None]
    out = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    return out, mat


# ------------------------------------------------------------------------------------------------ geometry
def frame_geometries(classes):
    geos = []
    for (w, h), (W, H) in sorted(classes.items()):
        bw, bh = w * 16, h * 16
        strip_v = {"uv": [0, 0], "uv_size": [1, H]}
        strip_h = {"uv": [0, 0], "uv_size": [W, 1]}
        dot = {"uv": [0, 0], "uv_size": [1, 1]}
        front = {"uv": [0, 0], "uv_size": [W, H]}

        def cube(origin, size, front_face):
            uv = {"north": strip_v, "south": strip_v, "east": strip_v, "west": strip_v, "up": strip_h, "down": strip_h}
            uv = {k: (front if k == front_face else (dot if k == {"north": "south", "south": "north", "east": "west", "west": "east"}.get(front_face) else v)) for k, v in uv.items()}
            return {"origin": origin, "size": size, "uv": uv}
        bones = [
            {"name": "n", "pivot": [0, 0, 0], "cubes": [cube([-bw / 2, 0, 7], [bw, bh, 1], "north")]},
            {"name": "s", "pivot": [0, 0, 0], "cubes": [cube([-bw / 2, 0, -8], [bw, bh, 1], "south")]},
            {"name": "e", "pivot": [0, 0, 0], "cubes": [cube([-8, 0, -bw / 2], [1, bh, bw], "east")]},
            {"name": "w", "pivot": [0, 0, 0], "cubes": [cube([7, 0, -bw / 2], [1, bh, bw], "west")]},
        ]
        geos.append({"description": {"identifier": f"geometry.pw_frame_{w}x{h}", "texture_width": W, "texture_height": H,
                                     "visible_bounds_width": max(w, 2) + 1, "visible_bounds_height": h + 1, "visible_bounds_offset": [0, h / 2, 0]},
                     "bones": bones})
    return {"format_version": "1.12.0", "minecraft:geometry": geos}


RENDER = {"format_version": "1.10.0", "render_controllers": {"controller.render.pw_art": {
    "geometry": "Geometry.default", "materials": [{"*": "Material.default"}], "textures": ["Texture.default"],
    # 1.0.1 (10-05): Bedrock draws the entity model turned 180 deg at yaw 0 — each facing shows the OPPOSITE bone
    "part_visibility": [{"*": False}, {"s": "query.property('pw:facing') == 0"}, {"w": "query.property('pw:facing') == 1"},
                        {"n": "query.property('pw:facing') == 2"}, {"e": "query.property('pw:facing') == 3"}]}}}


def client_entity(key, w, h):
    kid = key_id(key)
    return {"format_version": "1.10.0", "minecraft:client_entity": {"description": {
        "identifier": f"pw:art_{kid}", "materials": {"default": "entity"}, "textures": {"default": f"textures/gallery/{kid}"},
        "geometry": {"default": f"geometry.pw_frame_{w}x{h}"}, "render_controllers": ["controller.render.pw_art"]}}}


def book_icon():
    """a 256 px item icon: a red-leather book with a small gilt frame on the cover"""
    im = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([40, 24, 216, 232], radius=14, fill=(122, 34, 30), outline=(70, 18, 16), width=5)
    d.rectangle([40, 24, 62, 232], fill=(96, 26, 24))
    for y in range(40, 220, 24):
        d.line([(50, y), (50, y + 12)], fill=(200, 160, 70), width=3)
    d.rectangle([96, 72, 190, 170], outline=(214, 172, 74), width=8)
    d.rectangle([108, 84, 178, 158], fill=(70, 100, 140))
    d.polygon([(108, 158), (178, 158), (178, 130), (150, 112), (126, 136), (108, 124)], fill=(60, 110, 60))
    d.ellipse([154, 92, 170, 108], fill=(240, 220, 160))
    d.text((80, 190), "CONNOISSEUR", fill=(214, 172, 74))
    return im.filter(ImageFilter.SMOOTH)


def main():
    out = Path(sys.argv[1])
    limit = arg("limit", 0)
    only = arg("only", "")
    version = arg("version", "1.0.0")
    scale = arg("scale", 1.0)                                        # 0.5 = the LITE pack (128 px per block, ~a quarter of the bytes) for the phone (Q36)
    lite = scale < 0.999
    if out.exists():
        raise SystemExit(f"never rebuild {out} — move it to _garbage first")
    cat = json.loads(CAT.read_text())
    keys = [k for k in cat if (not only or k in only.split(","))]
    if limit:
        keys = keys[:limit]
    (out / "textures/gallery").mkdir(parents=True)
    (out / "textures/items").mkdir(parents=True)
    (out / "entity").mkdir()
    (out / "models/entity").mkdir(parents=True)
    (out / "render_controllers").mkdir()
    (out / "texts").mkdir()
    rng = np.random.default_rng(1)
    classes, n, matted, t0 = {}, 0, 0, time.time()
    sizes = 0
    for k in keys:
        rec = cat[k]
        if "frame" not in rec:
            rec["frame"] = AC.frame_class(rec)
        if not Path(rec["file"]).exists():
            continue
        fr = dict(rec["frame"])
        if lite:
            fr["ppb"] = max(32, int(fr["ppb"] * scale) // 8 * 8)
            fr["tex"] = [int(fr["w"] * fr["ppb"]), int(fr["h"] * fr["ppb"])]
        rec = dict(rec, frame=fr)
        classes[(fr["w"], fr["h"])] = tuple(fr["tex"])
        img, mat = compose(rec, rng)
        kid = key_id(k)
        f = out / "textures/gallery" / f"{kid}.jpg"
        img.save(f, "JPEG", quality=85, optimize=True)
        sizes += f.stat().st_size
        matted += mat
        (out / "entity" / f"pw_art_{kid}.entity.json").write_text(json.dumps(client_entity(k, fr["w"], fr["h"]), separators=(",", ":")))
        n += 1
        if n % 250 == 0:
            print(f"  {n}/{len(keys)} textures, {sizes / 1e6:.0f} MB, {time.time() - t0:.0f} s", flush=True)
    (out / "models/entity/pw_frames.geo.json").write_text(json.dumps(frame_geometries(classes), indent=1))
    (out / "render_controllers/pw_art.render.json").write_text(json.dumps(RENDER, indent=1))
    book_icon().save(out / "textures/items/pw_connoisseur_book.png")
    (out / "textures/item_texture.json").write_text(json.dumps({"resource_pack_name": "rp12", "texture_name": "atlas.items",
                                                                "texture_data": {"pw_connoisseur_book": {"textures": "textures/items/pw_connoisseur_book"}}}, indent=1))
    (out / "texts/en_US.lang").write_text("item.pw:connoisseur_book.name=Connoisseur's Book\n" + "".join(
        f"entity.pw:art_{key_id(k)}.name={(cat[k].get('title') or 'Untitled').replace(chr(10), ' ')}\n" for k in keys if Path(cat[k]['file']).exists()))
    (out / "texts/languages.json").write_text('["en_US"]')
    ver = [int(x) for x in version.split(".")]
    (out / "manifest.json").write_text(json.dumps({"format_version": 2, "header": {
        "name": f"RP-12 AbsolutRealism Gallery{' LITE' if lite else ''} v{version}", "description": f"v{version} (2026-10-05) THE GALLERY{' LITE (128 px per block, for the phone)' if lite else ''}: {n} public-domain paintings (CC0: National Gallery of Art, the Met, Cleveland) as framed entity textures for the CIVITAS buildings and the palace, {len(classes)} frame classes, the Connoisseur's Book icon. Personal use. Install ONE of full / LITE.",
        "uuid": str(uuid.uuid5(NAMESPACE_UUID, "rp12-lite-header" if lite else "rp12-header")), "version": ver, "min_engine_version": [1, 21, 120]},
        "modules": [{"description": "gallery", "type": "resources", "uuid": str(uuid.uuid5(NAMESPACE_UUID, "rp12-lite-module" if lite else "rp12-module")), "version": ver}]}, indent=1))
    (out / "pack_icon.png").write_bytes((Path("/home/claude/_build/rp01-123/pack_icon.png")).read_bytes())
    print(f"RP-12 {version}: {n} works, {matted} matted, {len(classes)} classes, textures {sizes / 1e6:.0f} MB ({time.time() - t0:.0f} s) -> {out}", flush=True)
    json.dump({"works": n, "classes": {f"{w}x{h}": list(t) for (w, h), t in classes.items()}, "bytes": sizes}, open(out / "GALLERY-BUILD.json", "w"), indent=1)


if __name__ == "__main__":
    main()
