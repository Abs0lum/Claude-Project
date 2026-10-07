#!/usr/bin/env python3
"""p0_compare.py — "his shot | our geometry from the same side | my read" sheets for the P0 witness round.

The left column is a native-resolution crop of Abs0lum's screenshot (never a thumbnail: crops are cut at 1:1 from the
2404x1080 PNG and only ever scaled UP), the middle column is the RP-07 1.4.11 geometry rendered with entity_render
(verified rotation law, bone-coloured, world frame: the mob faces SOUTH as the rig holds it), the right column is the
literal read + the question for him.  Camera per view (world blocks, relative to the mob's feet):
    front  = 3.0 blocks SOUTH, eye 1.6 up, looking north       (what he sees from where he stood)
    west   = 4.0 blocks WEST,  eye 1.6 up, looking east
    east   = 4.0 blocks EAST,  eye 1.6 up, looking west
    top    = 6.0 blocks UP (0.3 south), looking down, screen-up = north
Usage (module): sheet(out, title, geo_path, ident, rows=[(stem, box, view, read), ...], feet_y=0.0, extra_rot=None)
"""
import colorsys, json, math, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "tools")
from entity_render import load_geo, render, _load

SHOTS = Path("_intake/p0-shots")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
CAMS = {  # name: (eye offset in blocks from the mob's feet, target offset)
    "front": ((0.0, 1.6, 3.0), (0.0, 0.5, 0.0)),
    "front-near": ((0.0, 1.3, 2.0), (0.0, 0.5, 0.0)),
    "west": ((-4.0, 1.6, 0.0), (0.0, 0.5, 0.0)),
    "east": ((4.0, 1.6, 0.0), (0.0, 0.5, 0.0)),
    "top": ((0.0, 6.0, 0.3), (0.0, 0.3, 0.0)),
    "top-near": ((0.0, 4.0, 0.2), (0.0, 0.3, 0.0)),
    "back": ((0.0, 1.6, -3.0), (0.0, 0.5, 0.0)),
    "front-high": ((0.0, 3.0, 3.0), (0.0, 0.4, 0.0)),
}


def to_world(cubes):
    """file frame -> world frame for a mob facing SOUTH: file -z (front) -> world +z (south); file +x (left) -> world +x (east)."""
    return [(bone, [[p[0], p[1], -p[2]] for p in P]) for bone, P in cubes]


def bone_colours(names):
    cols = {}
    n = max(1, len(names))
    for i, b in enumerate(sorted(names)):
        h = (i * 0.61803) % 1.0
        r, g, bb = colorsys.hsv_to_rgb(h, 0.55 + 0.35 * ((i * 7) % 3) / 2, 0.95 - 0.25 * ((i * 5) % 2))
        cols[b] = (int(r * 255), int(g * 255), int(bb * 255))
    return cols


def render_view(cubes, view, size=(560, 420), fov=70.0, colours=None, ground=0.0, fill=0.8):
    """Camera on the named side, backed off so the mob spans `fill` of the frame height (or width for top views)."""
    eye_off, _ = CAMS[view]
    xs = [p[0] for _, P in cubes for p in P]; ys = [p[1] for _, P in cubes for p in P]; zs = [p[2] for _, P in cubes for p in P]
    cx, cy, cz = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2
    W, H = size
    # visible half-extent along the screen axes for this view
    if view.startswith("top"):
        half = max(max(xs) - min(xs), max(zs) - min(zs)) / 2
        aspect_fill = fill * min(1.0, H / W)
    elif view in ("front", "front-near", "front-high", "back"):
        half = max((max(xs) - min(xs)) / 2 * H / W, (max(ys) - min(ys)) / 2)
        aspect_fill = fill
    else:
        half = max((max(zs) - min(zs)) / 2 * H / W, (max(ys) - min(ys)) / 2)
        aspect_fill = fill
    dist = max(20.0, half / math.tan(math.radians(fov) / 2) / aspect_fill + max(max(xs) - min(xs), max(zs) - min(zs)) / 4)
    d = [eye_off[0], eye_off[1], eye_off[2]]
    n = math.sqrt(sum(v * v for v in d)) or 1.0
    d = [v / n for v in d]
    eye = [cx + d[0] * dist, cy + d[1] * dist, cz + d[2] * dist]
    tgt = [cx, cy, cz]
    return render(cubes, eye, tgt, fov=fov, size=size, colours=colours, ground=ground * 16 if ground is not None else None, bg=(214, 224, 236))


def crop_native(stem, box, out_w=560, out_h=420):
    im = Image.open(SHOTS / f"{stem}.png")
    c = im.crop(box)
    # scale UP only (never below native), keep aspect by padding
    w, h = c.size
    s = max(1.0, min(out_w / w, out_h / h))
    c = c.resize((int(w * s), int(h * s)), Image.LANCZOS if s > 1 else Image.NEAREST)
    canvas = Image.new("RGB", (out_w, out_h), (20, 20, 24))
    canvas.paste(c, ((out_w - c.size[0]) // 2, (out_h - c.size[1]) // 2))
    return canvas, s


def wrap(d, text, x, y, w, font, fill=(30, 30, 30), lh=17):
    words = text.split(" "); line = ""
    for wd in words:
        t = (line + " " + wd).strip()
        if d.textlength(t, font=font) > w and line:
            d.text((x, y), line, fill=fill, font=font); y += lh; line = wd
        else:
            line = t
    if line: d.text((x, y), line, fill=fill, font=font); y += lh
    return y


def sheet(out, title, geo_path, ident, rows, feet_y=0.0, extra_rot=None, note=None, cubes_override=None):
    F = ImageFont.truetype(FONT, 14); FB = ImageFont.truetype(FONTB, 16); FS = ImageFont.truetype(FONT, 12)
    cubes = cubes_override if cubes_override is not None else (to_world(load_geo(geo_path, ident, extra_rot=extra_rot)) if geo_path else [])
    bones = sorted({b for b, _ in cubes})
    cols = bone_colours(bones)
    W1, H1 = 560, 420
    legend_h = 22 * ((len(bones) + 3) // 4) + 30
    H = 70 + len(rows) * (H1 + 36) + legend_h + (40 if note else 0)
    W = 3 * W1 + 40
    sh = Image.new("RGB", (W, H), (240, 241, 245)); d = ImageDraw.Draw(sh)
    d.text((12, 10), title, fill=(20, 20, 20), font=FB)
    d.text((12, 34), f"geometry: {Path(geo_path).name if geo_path else '-'} / {ident} — rendered with the verified law, mob facing SOUTH as the rig holds it; bone colours in the legend below", fill=(70, 70, 70), font=FS)
    y = 62
    for stem, box, view, read in rows:
        crop, s = crop_native(stem, box)
        if isinstance(view, Image.Image):      # a ready-made render (e.g. textured) for this row
            rv = view.resize((W1, H1)) if view.size != (W1, H1) else view; view = "textured"
        else:
            rv = render_view(cubes, view, size=(W1, H1), colours=cols, ground=feet_y)
        sh.paste(crop, (12, y)); sh.paste(rv, (24 + W1, y))
        d.rectangle([12, y, 12 + W1, y + H1], outline=(90, 90, 90)); d.rectangle([24 + W1, y, 24 + 2 * W1, y + H1], outline=(90, 90, 90))
        d.text((12, y + H1 + 4), f"HIS SHOT {stem}.png  (native crop x{s:.1f}, {view} view)", fill=(20, 20, 20), font=F)
        d.text((24 + W1, y + H1 + 4), f"OUR FILE from the same side ({view})", fill=(20, 20, 20), font=F)
        wrap(d, read, 36 + 2 * W1, y + 4, W1 - 24, F)
        y += H1 + 36
    d.text((12, y + 4), "bone legend:", fill=(20, 20, 20), font=FB)
    yy = y + 28
    for i, b in enumerate(bones):
        x = 12 + (i % 4) * ((W - 24) // 4)
        d.rectangle([x, yy + (i // 4) * 22, x + 14, yy + (i // 4) * 22 + 14], fill=cols[b], outline=(40, 40, 40))
        d.text((x + 20, yy + (i // 4) * 22 - 2), b, fill=(30, 30, 30), font=FS)
    if note:
        wrap(d, note, 12, y + legend_h + 6, W - 24, F, fill=(120, 30, 30))
    sh.save(out)
    return out


def bone_table(geo_path, ident):
    doc = _load(geo_path)
    geo = next(g for g in doc["minecraft:geometry"] if g["description"]["identifier"] == ident)
    rows = []
    for b in geo["bones"]:
        rows.append((b["name"], b.get("parent"), b.get("pivot"), b.get("rotation"), len(b.get("cubes", [])),
                     [(c["origin"], c["size"], c.get("rotation")) for c in b.get("cubes", [])][:3]))
    return rows
