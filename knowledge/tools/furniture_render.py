#!/usr/bin/env python3
"""furniture_render.py — textured player-POV preview of furniture_geo pieces with the real RP-04 Patrix stems.

Box-projected UVs (a face samples the material texture by its own world coordinates, 16 cubes = one 128-px tile, so the
grain runs continuously across a piece — the same mapping to_bedrock_geometry() writes into the shipped uv), painter's
algorithm with per-face shade (up 1.0 · front 0.88 · sides 0.74 · back 0.62 · down 0.45), rotations by the D-C197
convention (geo_preview.transform), alpha test.  Scene: spruce plank floor + stone-brick back wall at z = 16.
Usage: furniture_render.py OUT_PREFIX   -> OUT_PREFIX-seating.png / -storage.png / -fittings.png (4 pieces x 4 views)
"""
import math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import furniture_geo as FG
from geo_preview import transform as rot_transform

RP04 = "/home/claude/_build/rp04-136/textures/blocks/"
WOODS = {"oak": {"board": "oak_planks_v0", "post": "stripped_oak_log", "end": "stripped_oak_log_top"},
         "spruce": {"board": "spruce_planks_v0", "post": "stripped_spruce_log", "end": "stripped_spruce_log_top"},
         "dark oak": {"board": "dark_oak_planks_v0", "post": "stripped_dark_oak_log", "end": "stripped_dark_oak_log_top"}}
IRON = "pw_furn_iron"               # the fittings stem: wrought iron authored from the Patrix anvil's forged-iron band (_design/furniture)
EXTRA_TEX = {"pw_furn_iron": "/home/claude/_design/furniture/pw_furn_iron.png"}
FLOOR, WALL = "spruce_planks_v0", "stone_bricks_v13"
SHADE = {"up": 1.0, "north": 0.88, "east": 0.74, "west": 0.74, "south": 0.62, "down": 0.45}
_tex = {}
def tex(stem):
    """5x5-tiled RGBA texture so coordinates in -32..48 cubes map inside; returns (image, px per cube)."""
    if stem not in _tex:
        im = Image.open(EXTRA_TEX.get(stem, RP04 + stem + ".png")).convert("RGBA"); s = im.width // 16
        big = Image.new("RGBA", (im.width * 5, im.height * 5))      # 5x5 tiles: coordinates in -32..48 cubes map inside (tall pieces, wall tiles)
        for i in range(5):
            for j in range(5): big.paste(im, (i * im.width, j * im.height))
        _tex[stem] = (big, s)
    return _tex[stem]

class Camera:
    def __init__(self, eye, target, W, H, fov_deg=60):
        self.eye = np.array(eye, float); t = np.array(target, float)
        f = t - self.eye; f /= np.linalg.norm(f); r = np.cross(f, np.array([0, 1, 0.0])); r /= np.linalg.norm(r); u = np.cross(r, f)
        self.f, self.r, self.u, self.W, self.H = f, r, u, W, H; self.focal = (W / 2) / math.tan(math.radians(fov_deg) / 2)
    def project(self, p):
        d = np.array(p, float) - self.eye; z = d @ self.f
        if z <= 0.05: return None
        return (self.W / 2 + self.focal * (d @ self.r) / z, self.H / 2 - self.focal * (d @ self.u) / z, z)

def find_coeffs(dst, src):
    A, b = [], []
    for (x, y), (X, Y) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -X * x, -X * y]); A.append([0, 0, 0, x, y, 1, -Y * x, -Y * y]); b += [X, Y]
    return np.linalg.solve(np.array(A, float), np.array(b, float))

def inside_box(p, b, eps=1e-6):
    o, s = b["o"], b["s"]
    return all(o[i] + eps < p[i] < o[i] + s[i] - eps for i in range(3))

def hidden_by_others(pts, b, boxes):
    """a face whose four corners all lie strictly inside another (unrotated) box of the same piece is an internal face —
    the engine would never show it (the post end inside a slab); drop it so the painter's order cannot leak it."""
    for other in boxes:
        if other is b or "rot" in other: continue
        if all(inside_box(p, other) for p in pts): return True
    return False

def subdivide(pts, uvs, maxlen=4.0):
    """split a quad into a grid of sub-quads no longer than `maxlen` cubes per side (better painter's sorting for
    the big planes: the tabletop vs the small post faces)."""
    import itertools
    p0, p1, p2, p3 = [np.array(p, float) for p in pts]; t0, t1, t2, t3 = [np.array(t, float) for t in uvs]
    nu = max(1, int(math.ceil(np.linalg.norm(p1 - p0) / maxlen))); nv = max(1, int(math.ceil(np.linalg.norm(p3 - p0) / maxlen)))
    out = []
    for i in range(nu):
        for j in range(nv):
            a, bb, c, d = i / nu, (i + 1) / nu, j / nv, (j + 1) / nv
            def bil(P0, P1, P2, P3, u, v): return (P0 * (1 - u) * (1 - v) + P1 * u * (1 - v) + P2 * u * v + P3 * (1 - u) * v)
            out.append(([bil(p0, p1, p2, p3, u, v).tolist() for u, v in ((a, c), (bb, c), (bb, d), (a, d))],
                        [tuple(bil(t0, t1, t2, t3, u, v)) for u, v in ((a, c), (bb, c), (bb, d), (a, d))]))
    return out

def box_faces(b, mats, boxes=()):
    """faces of one furniture box: (name, stem, 3D points (rotated), texture coords in cubes)."""
    o, s = b["o"], b["s"]; x0, y0, z0 = o; x1, y1, z1 = o[0] + s[0], o[1] + s[1], o[2] + s[2]
    P = {"a": [x0, y0, z0], "b": [x1, y0, z0], "c": [x1, y1, z0], "d": [x0, y1, z0], "e": [x0, y0, z1], "f": [x1, y0, z1], "g": [x1, y1, z1], "h": [x0, y1, z1]}
    # corner order per face (counter-clockwise seen from outside) and the (u,v) of each corner in cube units
    F = {"north": (["a", "b", "c", "d"], lambda p: (p[0], -p[1])), "south": (["f", "e", "h", "g"], lambda p: (-p[0], -p[1])),
         "west": (["e", "a", "d", "h"], lambda p: (p[2], -p[1])), "east": (["b", "f", "g", "c"], lambda p: (-p[2], -p[1])),
         "up": (["d", "c", "g", "h"], lambda p: (p[0], p[2])), "down": (["e", "f", "b", "a"], lambda p: (p[0], -p[2]))}
    piv, rot = b.get("piv", [0, 0, 0]), b.get("rot", [0, 0, 0]); out = []
    for name, (keys, uvf) in F.items():
        inst = b.get("faces", {}).get(name, b["m"]); stem = mats[inst]
        pts = [rot_transform(P[k], piv, rot) if "rot" in b else P[k] for k in keys]
        uvs = [uvf(P[k]) for k in keys]
        if "rot" not in b and hidden_by_others(pts, b, boxes): continue
        for sp, su in subdivide(pts, uvs): out.append((name, stem, sp, su))
    return out

def scene_faces(mats, wall=True):
    out = []
    for x in range(-48, 64, 16):
        for z in range(-48, 64, 16):
            for sp, su in subdivide([[x, 0, z], [x + 16, 0, z], [x + 16, 0, z + 16], [x, 0, z + 16]], [(x, z), (x + 16, z), (x + 16, z + 16), (x, z + 16)], 8): out.append(("up", FLOOR, sp, su))
    if wall:
        for x in range(-48, 64, 16):
            for y in range(0, 48, 16):
                for sp, su in subdivide([[x, y, 16], [x + 16, y, 16], [x + 16, y + 16, 16], [x, y + 16, 16]], [(x, -y), (x + 16, -y), (x + 16, -y - 16), (x, -y - 16)], 8): out.append(("north", WALL, sp, su))
    return out

def render(faces, cam, bg=(30, 28, 26, 255)):
    canvas = Image.new("RGBA", (cam.W, cam.H), bg)
    order = sorted(faces, key=lambda f: -np.linalg.norm(np.mean(np.array(f[2], float), axis=0) - cam.eye))
    for name, stem, pts3, uvs in order:
        pts = [cam.project(p) for p in pts3]
        if any(p is None for p in pts): continue
        # back-face cull by the projected winding (faces are authored counter-clockwise from outside)
        (ax, ay, _), (bx, by, _), (cx, cy, _) = pts[0], pts[1], pts[2]
        if (bx - ax) * (cy - ay) - (by - ay) * (cx - ax) < 0: continue     # image y points down: outside faces wind clockwise on screen
        big, s = tex(stem); off = 32
        dst = [(p[0], p[1]) for p in pts]; src = [((u + off) * s, (v + off) * s) for (u, v) in uvs]
        try: coeffs = find_coeffs(dst, src)
        except np.linalg.LinAlgError: continue
        layer = big.transform((cam.W, cam.H), Image.PERSPECTIVE, tuple(coeffs), Image.BILINEAR)
        mask = Image.new("L", (cam.W, cam.H), 0); ImageDraw.Draw(mask).polygon(dst, fill=255)
        arr = np.array(layer).astype(np.float32); m = np.array(mask) > 0
        arr[..., :3] *= SHADE[name]; arr[..., 3] = np.where(m & (arr[..., 3] > 127), 255, 0)
        canvas.alpha_composite(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA"))
    return canvas

def views(piece, mats, W=300, H=300):
    h = piece["h"]; wallpiece = "wall" in piece["title"] or "mantel" in piece["title"]
    base = scene_faces(mats, wall=True)
    pf = [f for b in piece["boxes"] for f in box_faces(b, mats, piece["boxes"])]
    cams = [Camera((-12, 26, -26), (8, h / 2 + 1, 8), W, H, 42),        # player POV, front-left, eye 1.62 blocks, ~1.8 blocks away
            Camera((8, 26, -30), (8, h / 2, 8), W, H, 40),                # player POV, straight on
            Camera((26, 30, -18), (8, h / 2, 8), W, H, 40),               # front-right, higher
            Camera((8, h + 26, 2), (8, 0, 8), W, H, 48)]                  # from above (the plan view a builder wants)
    return [render(base + pf, c) for c in cams]

def sheet(names, out, cell=300):
    try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
    except Exception: font = ImageFont.load_default()
    cols = 4 * 1 + 2   # 4 views of oak + 3/4 view in spruce + dark oak
    rows = len(names)
    img = Image.new("RGBA", (cols * (cell + 6) + 6, rows * (cell + 44) + 30), (18, 18, 20, 255)); d = ImageDraw.Draw(img)
    for r, n in enumerate(names):
        piece = FG.PIECES[n]; y = 24 + r * (cell + 44)
        d.text((6, y - 17), f"{n}: {piece['title']}  ·  {len(piece['boxes'])} boxes, h {piece['h']} cubes", fill=(255, 220, 140, 255), font=font)
        vs = views(piece, {**WOODS["oak"], "iron": IRON}, cell, cell)
        vs.append(views(piece, {**WOODS["spruce"], "iron": IRON}, cell, cell)[0]); vs.append(views(piece, {**WOODS["dark oak"], "iron": IRON}, cell, cell)[0])
        labels = ["oak · player POV", "oak · straight on", "oak · right, high", "oak · from above", "spruce · player POV", "dark oak · player POV"]
        for c, (v, lab) in enumerate(zip(vs, labels)):
            x = 6 + c * (cell + 6); img.paste(v, (x, y)); d.text((x + 4, y + cell + 4), lab, fill=(220, 220, 220, 255), font=font)
    d.text((8, img.height - 20), "pw:furniture preview ROUND 2 — RP-04 v1.3.136 Patrix stems (oak/spruce/dark oak planks + stripped logs); front = -z toward the placer; fittings = pw_furn_iron (wrought iron from the Patrix anvil band)", fill=(180, 180, 180, 255), font=font)
    img.save(out); return img.size

if __name__ == "__main__":
    prefix = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/outputs/furniture-preview"
    for group, names in (("seating", ["table", "bench", "stool", "chair"]), ("storage", ["shelf", "wall_shelf", "cupboard", "dresser"]), ("fittings", ["trestle", "barrel_seat", "coat_pegs", "mantel"])):
        print(group, sheet(names, f"{prefix}-{group}.png"))
