#!/usr/bin/env python3
"""convb_preview.py — his 09-28 20:44 GO: the Converter B PREVIEW for the FAIL mobs (nothing built into a pack).

Per mob: the NEW geometry (tools/convb.py: the Patrix JEM in its FreshLX rest posture, bones renamed so our animations and
render controllers still bind) next to the OLD shipped geometry (in game: relative_to-entity look applied), same cameras,
same texture file the entity binds. Plus per mob:
  holes  = % of box area whose UV lands on transparent texels (alpha-card planes excluded) — "missing parts of the texture"
  joints = a bone whose boxes touch no other bone's boxes (sampled OBB contact, 0.3 px) = a FLOATING part
  unbound = bone names our animations / RCs use that the new geometry lacks (those channels would do nothing)
  this   = animation channels written as "... this ..." on a bone that now has a bind rotation (they would cancel the pose)
Outputs: _docs/convb/<mob>.png, _docs/convb/convb_preview.png, _docs/convb/report.json
"""
import glob, json, re, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
from convb import bake, rename, relocate_leg_pivots
from equine_compare import bone_affines, posed_faces
from face_alpha_census import all_geometries, resolve_texture, jl, face_rects, opaque_fraction
from entity_tex_render import render_entity, frame_camera
from verify_rp07_1415_rp06_1410 import world_boxes, inside_frac

ROOT = Path("/home/claude"); OUT = ROOT / "_docs/convb"
PACKS = [("RP-07", ROOT / "_build/rp07-1415"), ("RP-06", ROOT / "_build/rp06-1411")]
# label -> (entity stem, geometry key in the entity, JEM name, texture key)
JOBS = [("turtle", "turtle", "default", "turtle", "default"), ("salmon", "salmon", "default", "salmon", "default"),
        ("dolphin", "dolphin", "default", "dolphin", "default"), ("axolotl", "axolotl", "default", "axolotl", "default"),
        ("wolf", "wolf", "default", "wolf", "default"), ("camel", "camel", "default", "camel", "default"),
        ("zombified piglin", "zombie_pigman", "default", "zombified_piglin", "default"), ("chicken", "chicken", "default", "chicken", "default"),
        ("frog", "frog", "default", "frog", "default"), ("squid", "squid", "default", "squid", "default"),
        ("glow squid", "glow_squid", "default", "glow_squid", "default"), ("tropical fish A", "tropicalfish", "typeA", "tropical_fish_a", "typeA"),
        ("tropical fish B", "tropicalfish", "typeB", "tropical_fish_b", "typeB"), ("panda", "panda", "default", "panda", "default"),
        ("llama", "llama", "default", "llama", "default"), ("cow", "cow", "default", "cow", "default"),
        ("mooshroom", "mooshroom", "default", "mooshroom", "default"), ("rabbit", "rabbit", "default", "rabbit", "default")]
W, H = 400, 300
try:
    FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15); FR = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    FT = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
except Exception:
    FB = FR = FT = ImageFont.load_default()


def entity(stem):
    for tag, rp in PACKS:
        f = rp / f"entity/{stem}.entity.json"
        if f.exists(): return tag, rp, jl(f)["minecraft:client_entity"]["description"]
    raise FileNotFoundError(stem)


# D-C277 (P11): an entity's animations may live in ANOTHER pack of the stack (RP-06 humanoids use RP-07's
# animation.humanoid_articulated.*); the library loads the whole stack, top pack first (the top pack wins a duplicate id)
STACK = [ROOT / "_build/rp07-1418", ROOT / "_build/rp06-1411"]
STACK_RANK = {"rp07": 0, "rp06": 1}


def library(rp):
    anims, rcs = {}, {}
    rp = Path(rp); fam = rp.name.split("-")[0]
    packs = sorted([rp] + [s for s in STACK if s.name.split("-")[0] != fam], key=lambda q: STACK_RANK.get(q.name.split("-")[0], 9))
    for root in packs + [ROOT / "_intake/bedrock-samples/resource_pack"]:
        for f in glob.glob(str(root / "animations/*.json")):
            d = jl(f)
            if d:
                for k, v in d.get("animations", {}).items(): anims.setdefault(k, v)
        for f in glob.glob(str(root / "render_controllers/*.json")):
            d = jl(f)
            if d:
                for k, v in d.get("render_controllers", {}).items(): rcs.setdefault(k, v)
    return anims, rcs


def bind_info(desc, anims, rcs):
    names, rel, this = set(), {}, []
    for short, aid in (desc.get("animations") or {}).items():
        a = anims.get(aid)
        if not isinstance(a, dict): continue
        for bn, bv in (a.get("bones") or {}).items():
            names.add(bn)
            if isinstance(bv, dict):
                if (bv.get("relative_to") or {}).get("rotation") == "entity": rel[bn] = aid
                for ch in ("rotation", "position"):
                    v = bv.get(ch)
                    if isinstance(v, list) and any(isinstance(x, str) and re.search(r"\bthis\b", x) for x in v): this.append((aid, bn, ch))
    for rc in desc.get("render_controllers", []):
        k = rc if isinstance(rc, str) else list(rc)[0]
        for p in (rcs.get(k, {}).get("part_visibility") or []): names |= {n for n in p if n != "*"}
    # Bedrock bone names are case-insensitive (D-C267: the pillager set animates `rightarm` on our `rightArm`): one name per
    # lower-case key, the mixed-case spelling preferred
    by_low = {}
    for n in sorted(names, key=lambda x: (x == x.lower(), x)): by_low.setdefault(n.lower(), n)
    names = set(by_low.values())
    return names, rel, this


def holes(bones, tw, th, tp):
    alpha = np.asarray(Image.open(tp).convert("RGBA"))[..., 3]
    area = tot = 0.0
    for b in bones:
        for c in b.get("cubes", []):
            s = c["size"]
            if min(s) < 0.05: continue
            for name, rect in face_rects(c, b.get("mirror", False)).items():
                d = {"north": (s[0], s[1]), "south": (s[0], s[1]), "east": (s[2], s[1]), "west": (s[2], s[1]), "up": (s[0], s[2]), "down": (s[0], s[2])}[name]
                a = d[0] * d[1]
                if a < 2.0: continue
                op, off = opaque_fraction(alpha, rect, tw, th); tot += a
                if op < 0.5 or off: area += a
    return 100.0 * area / tot if tot else 0.0


def floating(bones):
    W_ = {}
    for x in world_boxes(bones): W_.setdefault(x[0], []).append(x[2])
    out = []
    for n, boxes in W_.items():
        others = [q for m, bs in W_.items() if m != n for q in bs]
        if not any(inside_frac(p, q) or inside_frac(q, p) for p in boxes for q in others): out.append(n)
    return sorted(out)


def tile(img, title, sub, color):
    img = img.convert("RGB"); d = ImageDraw.Draw(img); d.rectangle([0, 0, W, 36], fill=color)
    d.text((6, 2), title, fill=(255, 255, 255), font=FB); d.text((6, 19), sub, fill=(222, 228, 238), font=FR)
    return img


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    G = all_geometries(); report = {}; rows = []
    only = set(sys.argv[1:])
    for label, stem, gkey, jname, tkey in JOBS:
        if only and label not in only and stem not in only: continue
        tag, rp, desc = entity(stem); anims, rcs = library(rp)
        gid = desc["geometry"][gkey]; _, old, otw, oth = G[gid]
        tp = resolve_texture(desc["textures"][tkey])
        names, rel, this = bind_info(desc, anims, rcs)
        new, ntw, nth, info = bake(jname)
        new, mapping, missing = rename(new, names - {"placeholder_bone"}, old)
        new = relocate_leg_pivots(new, {n for n in names if re.fullmatch(r"leg\d", n) or n.endswith("_leg")})
        nb = {b["name"]: b for b in new}
        this_bad = [t for t in this if t[1] in nb and any(abs(v) > 0.01 for v in nb[t[1]].get("rotation", [0, 0, 0]))]
        old_aff = bone_affines(old, abs_rot={n: [0, 0, 0] for n in rel if n in {b["name"] for b in old}})
        of = posed_faces(old, otw, oth, old_aff); nf = posed_faces(new, ntw, nth, bone_affines(new))
        h_old, h_new = holes(old, otw, oth, tp), holes(new, ntw, nth, tp)
        fl_old, fl_new = floating(old), floating(new)
        r = {"entity": stem, "pack": tag, "geometry": gid, "texture": str(tp.relative_to(ROOT)), "texture_size_geo_old": [otw, oth], "texture_size_jem": [ntw, nth],
             "holes_old_pct": round(h_old, 1), "holes_new_pct": round(h_new, 1), "floating_old": fl_old, "floating_new": fl_new,
             "mapping": {k: v for k, v in mapping.items() if k != v}, "unbound": missing, "relative_to_look": rel, "this_on_rotated": this_bad,
             "seeds": sorted(info["seeds"]), "template": info["template"], "bake_errors": len(info["errors"]), "hidden_at_rest": info["hidden_at_rest"], "dropped": info["dropped"],
             "bones_new": len(new), "cubes_new": sum(len(b["cubes"]) for b in new), "cubes_old": sum(len(b.get("cubes", [])) for b in old)}
        report[label] = r
        cells = []
        for v in ("east", "front-east"):
            e, t = frame_camera(nf + of, v)
            sub_new = f"holes {h_new:.0f}% · floating {len(fl_new)}"
            sub_old = f"holes {h_old:.0f}% · floating {len(fl_old)}"
            cells.append(tile(render_entity(nf, tp, e, t, W, H, fov=55), f"{label.upper()} — NEW ({v})", sub_new, (30, 70, 140)))
        for v in ("east", "front-east"):
            e, t = frame_camera(nf + of, v)
            cells.append(tile(render_entity(of, tp, e, t, W, H, fov=55), f"{label.upper()} — OLD ({v})", sub_old, (130, 30, 30)))
        row = Image.new("RGB", (4 * (W + 4) - 4, H), (255, 255, 255))
        for i, c in enumerate(cells): row.paste(c, (i * (W + 4), 0))
        row.save(OUT / f"{stem}_{gkey}.png"); rows.append(row)
        print(f"{label:18s} {tag} holes {h_old:5.1f}% -> {h_new:5.1f}%  floating {len(fl_old)} -> {len(fl_new)} {fl_new}  unbound {missing}  "
              f"this-on-rotated {len(this_bad)}  rel-look {sorted(rel)}  map {r['mapping']}  bake-errors {r['bake_errors']}")
    json.dump(report, open(OUT / "report.json", "w"), indent=1)
    if rows:
        head = Image.new("RGB", (rows[0].width, 46), (20, 24, 32))
        ImageDraw.Draw(head).text((10, 10), "CONVERTER B PREVIEW — NEW (blue: the Patrix model in its rest pose, our bone names) vs OLD (red: what ships now) · 2026-09-28", fill=(255, 255, 255), font=FT)
        for part, chunk in enumerate((rows[:9], rows[9:])):
            if not chunk: continue
            sheet = Image.new("RGB", (rows[0].width, 46 + sum(r.height + 6 for r in chunk)), (255, 255, 255)); sheet.paste(head, (0, 0)); y = 52
            for r_ in chunk: sheet.paste(r_, (0, y)); y += r_.height + 6
            sheet.save(OUT / f"convb_preview_{part + 1}.png")


if __name__ == "__main__":
    main()
