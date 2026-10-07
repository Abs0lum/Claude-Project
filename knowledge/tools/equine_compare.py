#!/usr/bin/env python3
"""equine_compare.py — the equine family (horse / donkey / mule / zombie horse / skeleton horse): what the Patrix model
LOOKS like at rest in Java vs what OUR Bedrock files draw in game (his 09-28 18:36 report: "all of the parts, oriented
incorrectly, mispositioned, not connected in a way that looks natural").

Reference (Patrix): the Patrix JEM + FreshLX's CEM animations evaluated at rest (cem_eval.rest_pose with the VANILLA
per-frame seeds: neck ty 4 / tz -12 / rx 30 deg, body rx 0 — the animation reads neck.ty to decide rearing/eating),
baked to Bedrock bones by jem_convert.bake_rest2 (CONV-1 frames, verified on the vanilla pairs + our witnessed cow).

Ours: the shipped geometry + the animations the client entity runs, at rest (life_time 0, not moving, looking straight
ahead).  `relative_to: {"rotation": "entity"}` (animation.common.look_at_target on `head`; the horse's own
animation.horse.pw.headtrack on `head` AND `head2`) is honoured: that bone's WORLD orientation = the animated value
(target - this => the look target, level at rest) about its world pivot; its parents' rotations are discarded.
Small idle wobbles (ar_*_idle, *.pw.ambient: ±5 deg) are left out and reported as such.

Renders use the verified transform law (entity_render.transform) and the textured rasterizer (entity_tex_render).
Outputs: _docs/equine/<mob>_compare.png sheets + a per-part numbers table on stdout (world centre of every part box,
long-axis pitch) — Patrix vs ours.
"""
import json, math, re, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
from entity_render import transform
from block_render import Face, corners
from entity_tex_render import box_uv, render_entity, frame_camera, load_json
from jem_convert import bake_rest2, to_bedrock
from jem_convert import load_json as jload

ROOT = Path("/home/claude")
CEM = ROOT / "_intake/patrix-mobs/assets/minecraft/optifine/cem"
SEEDS = {"neck": {"ty": 4.0, "tz": -12.0, "rx": 0.5235988}, "body": {"rx": 0.0}, "tail": {"ry": 0.0}}
MOBS = {
    "horse": ("_build/rp07-1414", "horse.geo.json", "geometry.horse.patrix", "horse", ["head", "head2"]),
    "donkey": ("_build/rp07-1414", "pw_donkey.geo.json", "geometry.pw_donkey", "donkey", ["head"]),
    "mule": ("_build/rp07-1414", "pw_mule.geo.json", "geometry.pw_mule", "mule", ["head"]),
    "zombie_horse": ("_build/rp06-149", "zombie_horse.geo.json", "geometry.zombie_horse.patrix", "zombie_horse", ["head"]),
    "skeleton_horse": ("_build/rp06-149", "skeleton_horse.geo.json", "geometry.skeleton_horse.patrix", "skeleton_horse", ["head"]),
}
# Patrix part -> our bone (by role)
ROLE = [("body", "body", "body_cube"), ("neck", "neck3", "neck"), ("skull", "head2", "head2"), ("muzzle", "snout2", "snout"),
        ("ear A", "left_ear2", "left_ear"), ("ear B", "right_ear2", "right_ear"), ("forelock", "mane3", "mane_top"),
        ("mane", "mane2", "mane"), ("tail", "tail2", "tail")]


def rot_matrix(rot):
    return np.array([transform([1 if i == j else 0 for i in range(3)], [0, 0, 0], rot) for j in range(3)]).T


def bone_affines(bones, abs_rot=None, add_rot=None):
    """{bone: (A, t)} world = A @ p + t for a point p given in the geometry file frame of that bone."""
    abs_rot = abs_rot or {}; add_rot = add_rot or {}
    by = {b["name"]: b for b in bones}; out = {}

    def get(n):
        if n in out: return out[n]
        b = by[n]; piv = np.array(b.get("pivot", [0, 0, 0]), float)
        r = list(b.get("rotation", [0, 0, 0]) or [0, 0, 0])
        if n in add_rot: r = [r[i] + add_rot[n][i] for i in range(3)]
        par = b.get("parent")
        A0, t0 = get(par) if par and par in by else (np.eye(3), np.zeros(3))
        if n in abs_rot:                       # relative_to entity: orientation = the animated value only
            R = rot_matrix(abs_rot[n]); w = A0 @ piv + t0
            out[n] = (R, w - R @ piv)
        else:
            R = rot_matrix(r)
            out[n] = (A0 @ R, A0 @ (piv - R @ piv) + t0)
        return out[n]
    for b in bones: get(b["name"])
    return out


def posed_faces(bones, tw, th, aff):
    faces = []
    for b in bones:
        A, t = aff[b["name"]]; bmirror = bool(b.get("mirror", False))
        for c in b.get("cubes", []):
            o, s = c["origin"], c["size"]; infl = c.get("inflate", 0) or 0
            cs = corners(o, s, infl)
            piv, rot = c.get("pivot", [0, 0, 0]), c.get("rotation", [0, 0, 0])
            uvspec = c.get("uv", [0, 0]); mirror = bool(c.get("mirror", bmirror))
            if isinstance(uvspec, dict):
                rects = {}
                for name, f in uvspec.items():
                    u0, v0 = f["uv"]; us, vs = f.get("uv_size", [s[0], s[1]]); rects[name] = (u0, v0, u0 + us, v0 + vs)
            else:
                rects = box_uv(uvspec[0], uvspec[1], s, mirror)
            for name, pts in cs.items():
                if name not in rects: continue
                if infl == 0:
                    if s[0] == 0 and name not in ("east", "west"): continue
                    if s[1] == 0 and name not in ("up", "down"): continue
                    if s[2] == 0 and name not in ("north", "south"): continue
                P = [transform(p, piv, rot) if any(rot or []) else list(p) for p in pts]
                P = [list(A @ np.array(p, float) + t) for p in P]
                a, bb, cc, e = rects[name]
                faces.append(Face(P, (a / tw, bb / th, cc / tw, e / th), "*", name, b["name"]))
    return faces


def part_stats(bones, aff, name):
    """world centre + long-axis pitch (deg, + = front end UP; file -z is the front) of the bone's first cube."""
    b = next((x for x in bones if x["name"] == name), None)
    if not b or not b.get("cubes"): return None
    A, t = aff[name]; c = b["cubes"][0]; o = np.array(c["origin"], float); s = np.array(c["size"], float)
    ctr = A @ (o + s / 2) + t
    k = int(np.argmax(s)); axis = np.zeros(3); axis[k] = 1.0; v = A @ axis
    if k == 2: v = -v                              # z-long boxes: point the axis at the front (-z)
    pitch = math.degrees(math.atan2(v[1], math.hypot(v[0], v[2])))
    return ctr, pitch, "xyz"[k]


def patrix_bones(mob):
    jem = jload(CEM / f"{mob}.jem")
    bb, ctx, err = bake_rest2(jem, mob, seeds=SEEDS)
    assert not err, err
    tw, th = (jem.get("textureSize") or [64, 64])
    return to_bedrock(bb), tw, th


def our_bones(mob):
    rp, geo, ident, _, _ = MOBS[mob]
    doc = load_json(ROOT / rp / "models/entity" / geo)
    g = next(x for x in doc["minecraft:geometry"] if x["description"]["identifier"] == ident)
    return g["bones"], g["description"].get("texture_width", 64), g["description"].get("texture_height", 64)


def texture(mob):
    rp, _, _, ent, _ = MOBS[mob]
    d = load_json(ROOT / rp / f"entity/{ent}.entity.json")["minecraft:client_entity"]["description"]
    t = d["textures"]["default"]
    for ext in (".png", ".tga"):
        for base in (ROOT / rp, ROOT / "_build/rp07-1414", ROOT / "_build/rp06-149"):
            p = base / (t + ext)
            if p.exists(): return p
    raise FileNotFoundError(t)


def label(img, text, sub=None):
    d = ImageDraw.Draw(img)
    try: f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18); g = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except Exception: f = g = ImageFont.load_default()
    d.rectangle([0, 0, img.width, 26 if not sub else 46], fill=(20, 24, 32))
    d.text((8, 4), text, fill=(255, 255, 255), font=f)
    if sub: d.text((8, 27), sub, fill=(200, 210, 225), font=g)
    return img


def main(out_dir=ROOT / "_docs/equine", views=("east", "west", "front-east")):
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {}
    for mob in (sys.argv[1:] or MOBS):
        pb, ptw, pth = patrix_bones(mob); ob, otw, oth = our_bones(mob)
        paff = bone_affines(pb)
        oaff_static = bone_affines(ob)
        oaff_game = bone_affines(ob, abs_rot={n: [0, 0, 0] for n in MOBS[mob][4]})
        tex = texture(mob)
        pf = posed_faces(pb, ptw, pth, paff); of_s = posed_faces(ob, otw, oth, oaff_static); of_g = posed_faces(ob, otw, oth, oaff_game)
        rows = []
        # one shared camera per view (framed on the Patrix model) so all three columns are directly comparable
        for v in views:
            eye, tgt = frame_camera(pf + of_g, v)
            cols = [label(render_entity(pf, tex, eye, tgt, 480, 360, floor_y=0), f"PATRIX (Java, at rest) — {v}", "the JEM + FreshLX rest pose"),
                    label(render_entity(of_g, tex, eye, tgt, 480, 360, floor_y=0), f"OURS in game — {v}", "shipped geometry + look_at relative_to entity"),
                    label(render_entity(of_s, tex, eye, tgt, 480, 360, floor_y=0), f"ours, files only — {v}", "shipped geometry, no animation")]
            row = Image.new("RGB", (480 * 3 + 8, 360), (255, 255, 255))
            for i, c in enumerate(cols): row.paste(c, (i * 484, 0))
            rows.append(row)
        sheet = Image.new("RGB", (rows[0].width, sum(r.height + 6 for r in rows)), (255, 255, 255))
        y = 0
        for r in rows: sheet.paste(r, (0, y)); y += r.height + 6
        sheet.save(out_dir / f"{mob}_compare.png")
        # numbers
        tab = []
        for role, pn, on in ROLE:
            ps = part_stats(pb, paff, pn); os_ = part_stats(ob, oaff_game, on); ss = part_stats(ob, oaff_static, on)
            tab.append((role, pn, on, ps, os_, ss))
        report[mob] = tab
        print(f"\n=== {mob}  (texture {tex.relative_to(ROOT)})  world file-frame px: +y up, -z = front")
        print(f"{'part':9s} {'patrix':10s} {'ours':10s} | {'PATRIX centre':>22s} pitch | {'OURS in-game centre':>22s} pitch | {'delta (ours-patrix)':>22s} dpitch")
        for role, pn, on, ps, os_, ss in tab:
            f = lambda s: (f"({s[0][0]:5.1f},{s[0][1]:5.1f},{s[0][2]:6.1f}) {s[1]:+5.0f}" if s else f"{'—':>22s}      ")
            d = (f"({os_[0][0]-ps[0][0]:+5.1f},{os_[0][1]-ps[0][1]:+5.1f},{os_[0][2]-ps[0][2]:+6.1f}) {os_[1]-ps[1]:+5.0f}" if (ps and os_) else "")
            print(f"{role:9s} {pn:10s} {on:10s} | {f(ps)} | {f(os_)} | {d}")
    return report


if __name__ == "__main__":
    main()
