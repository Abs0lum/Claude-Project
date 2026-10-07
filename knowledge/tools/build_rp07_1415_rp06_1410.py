#!/usr/bin/env python3
"""build_rp07_1415_rp06_1410.py — his 09-28 19:20 GO (D-C268 / D-C269).

RP-07 Neutral Mobs RP v1.4.15 (from v1.4.14):
  1. EQUINE CONVERTER B — geometry.horse.patrix / geometry.pw_donkey / geometry.pw_mule rebuilt from the Patrix JEMs by
     tools/equine_b.py (FreshLX rest posture: the head rides the neck, two ears in place, mane on the neck, tail; legs pivot
     at their top, children of the body). Identifiers kept, so nothing else has to change to find them.
  2. LOOK — `look_at_target` on horse / donkey / mule -> animation.pw_equine.look: parent-relative (the FreshLX split:
     neck pitch = look pitch / 1.5 and yaw / 2, head yaw / 6). Replaces the relative_to-entity look that reset the head to level.
     The mule's ar_neck_look (the same job) leaves its animate list.
  3. EYES REMOVED (his ruling): geometry.villager (villager + wandering trader) pupils / lids / brows · geometry.bee eyeballs ·
     geometry.ravager eyebrow + pupils · geometry.zombie.villager_v2 eye layers / eyeballs / brow — the zombie villager's skin had
     NO painted eyes, so what its eye planes showed at rest is baked flat into the face texels first (zombie-villager.png).
     Every `*.pw.eyes` animation (they animate r_pupil / l_pupil — bones no geometry has) leaves every entity.
     NOT touched: the iron golem's `eyebrow_guard` (a brow-ridge cube, not an eye).
  4. manifest 1.4.15, uuid kept.
RP-06 Hostile Mobs RP v1.4.10 (from v1.4.9):
  1. geometry.zombie_horse.patrix / geometry.skeleton_horse.patrix rebuilt the same way (the skeleton horse gets its neck back).
  2. look_at_target -> animation.pw_undead_equine.look (same content; this pack's own id).
  3. manifest 1.4.10, uuid kept.
Everything else byte-identical (verify_rp07_1415_rp06_1410.py asserts the diff)."""
import json, re, shutil, sys, time
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
from equine_b import build as build_equine
from block_render import corners

ROOT = Path("/home/claude"); DATE = "2026-09-28"
R7_SRC, R7_DST, R7_VER = ROOT / "_build/rp07-1414", ROOT / "_build/rp07-1415", "1.4.15"
R6_SRC, R6_DST, R6_VER = ROOT / "_build/rp06-149", ROOT / "_build/rp06-1410", "1.4.10"
EQUINES_07 = [("horse", "horse.geo.json", "geometry.horse.patrix"), ("donkey", "pw_donkey.geo.json", "geometry.pw_donkey"),
              ("mule", "pw_mule.geo.json", "geometry.pw_mule")]
EQUINES_06 = [("zombie_horse", "zombie_horse.geo.json", "geometry.zombie_horse.patrix"),
              ("skeleton_horse", "skeleton_horse.geo.json", "geometry.skeleton_horse.patrix")]
EYES = {"villager.geo.json": ("geometry.villager", ["pupil_r", "pupil_l", "lids_main", "brows_main"]),
        "bee.geo.json": ("geometry.bee", ["eyeballs"]),
        "ravager.geo.json": ("geometry.ravager", ["eyebrow", "pupil_right", "pupil_left", "eyelids"]),
        "zombie_villager_v2.geo.json": ("geometry.zombie.villager_v2", ["eye_right", "eye_left", "eye_layer_x", "eye_layer_x2", "eye_layer_y",
                                                                         "eye_layer_y2", "eyeball", "eyebrown"])}
ZV_TEX = "textures/entity/zombie_villager2/zombie-villager.png"


def look_anim(ident):
    return {"format_version": "1.8.0", "animations": {ident: {"loop": True, "bones": {
        "neck": {"rotation": ["math.clamp(query.target_x_rotation / 1.5, -20.0, 20.0)", "math.clamp(query.target_y_rotation / 2.0, -20.0, 20.0)", 0.0]},
        "head": {"rotation": [0.0, "math.clamp(query.target_y_rotation / 6.0, -15.0, 15.0)", 0.0]}}}}}


def jl(p):
    """JSON with // line comments and trailing commas tolerated (both occur in shipped entity files)."""
    t = re.sub(r"^\s*//.*$", "", Path(p).read_text(encoding="utf-8-sig"), flags=re.M)
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        return json.loads(re.sub(r",(\s*[}\]])", r"\1", t))


def wj(p, d):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(d, indent=1), encoding="utf-8")


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT 09-28] BUILD {m}\n")


def geometry_doc(ident, bones, tw, th):
    return {"format_version": "1.16.0", "minecraft:geometry": [{"description": {"identifier": ident, "texture_width": tw, "texture_height": th,
            "visible_bounds_width": 3.0, "visible_bounds_height": 3.5, "visible_bounds_offset": [0.0, 1.5, 0.0]}, "bones": bones}]}


def write_equines(dst, jobs):
    for mob, fname, ident in jobs:
        p = dst / "models/entity" / fname
        old = jl(p); ids = [g["description"]["identifier"] for g in old["minecraft:geometry"]]
        assert ids == [ident], (fname, ids)                  # the file holds exactly this geometry — replace it whole
        bones, tw, th, rep = build_equine(mob)
        assert not rep["rest_errors"], rep["rest_errors"]
        wj(p, geometry_doc(ident, bones, tw, th))
        log(f"{dst.name}: {ident} <- Patrix {mob}.jem (Converter B; {len(bones)} bones, {sum(len(b['cubes']) for b in bones)} cubes)")


def set_look(dst, ent, anim_id, drop=()):
    p = dst / f"entity/{ent}.entity.json"; d = jl(p); desc = d["minecraft:client_entity"]["description"]
    desc["animations"]["look_at_target"] = anim_id
    for k in drop:
        desc["animations"].pop(k, None)
        desc["scripts"]["animate"] = [a for a in desc["scripts"]["animate"] if not (a == k or (isinstance(a, dict) and k in a))]
    wj(p, d)


def drop_pw_eyes(dst):
    n = []
    for p in sorted((dst / "entity").glob("*.json")):
        if ".pw.eyes" not in p.read_text(encoding="utf-8-sig", errors="replace"): continue
        d = jl(p); desc = d.get("minecraft:client_entity", {}).get("description", {})
        keys = [k for k, v in (desc.get("animations") or {}).items() if isinstance(v, str) and re.search(r"\.pw\.eyes$", v)]
        if not keys: continue
        for k in keys:
            del desc["animations"][k]
            sc = desc.get("scripts") or {}
            if "animate" in sc:
                sc["animate"] = [a for a in sc["animate"] if not (a == k or (isinstance(a, dict) and k in a))]
        wj(p, d); n.append(p.stem.split(".")[0])
    return n


def strip_bones(bones, names):
    drop = set(names); changed = True
    while changed:
        changed = False
        for b in bones:
            if b["name"] not in drop and b.get("parent") in drop: drop.add(b["name"]); changed = True
    present = {b["name"] for b in bones}
    return [b for b in bones if b["name"] not in drop], sorted(drop & present)


SOCKET_RGBA = (28, 22, 16, 255)    # what an open eye hole shows today where no eyeball sits behind it: the dark head interior


def bake_zombie_villager_eyes(dst, zv_bones):
    """Paint what the face shows from the front at rest into the head's front-face texels, so the eye bones can go.
    The FA-style skin has 2x2 transparent eye HOLES; the red eyeball planes sit BEHIND the (inflated) face and show through
    them; the brow plane sits IN FRONT of the face. Per texel, front to back: brow (if its texel is opaque) > the face's own
    opaque texel > an eyeball behind a hole > the dark socket. Returns {what: texel count}."""
    by = {b["name"]: b for b in zv_bones}
    head = by["head"]["cubes"][0]; hf = head["uv"]["north"]; infl = head.get("inflate", 0) or 0
    u0, v0 = hf["uv"]; us, vs = hf["uv_size"]
    TL, TR, BR, BL = [np.array(p, float) for p in corners(head["origin"], head["size"], infl)["north"]]
    z_face = TL[2]
    tex_p = dst / ZV_TEX; src = np.asarray(Image.open(tex_p).convert("RGBA")); img = src.copy()
    H, W = img.shape[:2]; sx, sy = W / 64.0, H / 64.0
    planes = []                                            # (z, x0, x1, y0, y1, uv rect, name) — every eye cube's north face
    for n in ("eyeball_right", "eyeball_left", "eyebrown"):
        for c in by[n]["cubes"]:
            f = c["uv"]["north"]; o, s = c["origin"], c["size"]
            planes.append((o[2], o[0], o[0] + s[0], o[1], o[1] + s[1], (f["uv"][0], f["uv"][1], f["uv"][0] + f["uv_size"][0], f["uv"][1] + f["uv_size"][1]), n))

    def sample(P, pl):
        z, x0, x1, y0, y1, (pu0, pv0, pu1, pv1), n = pl
        if not (x0 <= P[0] <= x1 and y0 <= P[1] <= y1): return None
        q = [np.array(p, float) for p in corners([x0, y0, z], [x1 - x0, y1 - y0, 0.05], 0)["north"]]
        fa = (P[0] - q[0][0]) / (q[1][0] - q[0][0]); fb = (q[0][1] - P[1]) / (q[0][1] - q[3][1])
        px = src[min(H - 1, max(0, int((pv0 + (pv1 - pv0) * fb) * sy))), min(W - 1, max(0, int((pu0 + (pu1 - pu0) * fa) * sx)))]
        return px if px[3] >= 128 else None

    count = {"brow": 0, "eyeball": 0, "socket": 0}
    front = [p for p in planes if p[0] < z_face]; behind = [p for p in planes if p[0] >= z_face]
    for tv in range(int(round(v0 * sy)), int(round((v0 + vs) * sy))):
        for tu in range(int(round(u0 * sx)), int(round((u0 + us) * sx))):
            a = ((tu + 0.5) / sx - u0) / us; b = ((tv + 0.5) / sy - v0) / vs
            P = TL + (TR - TL) * a + (BL - TL) * b             # the file-frame point on the face under this texel
            hit = next((px for px in (sample(P, pl) for pl in front) if px is not None), None)
            if hit is not None: img[tv, tu] = hit; count["brow"] += 1; continue
            if src[tv, tu, 3] >= 128: continue
            hit = next((px for px in (sample(P, pl) for pl in behind) if px is not None), None)
            if hit is not None: img[tv, tu] = hit; count["eyeball"] += 1
            else: img[tv, tu] = SOCKET_RGBA; count["socket"] += 1
    Image.fromarray(img).save(tex_p, optimize=True)
    return count


def remove_eyes(dst):
    out = {}
    for fname, (ident, names) in EYES.items():
        p = dst / "models/entity" / fname; d = jl(p)
        g = next(x for x in d["minecraft:geometry"] if x["description"]["identifier"] == ident)
        if ident == "geometry.zombie.villager_v2":
            out["zombie-villager.png painted texels"] = bake_zombie_villager_eyes(dst, g["bones"])
        g["bones"], dropped = strip_bones(g["bones"], names)
        wj(p, d); out[ident] = dropped
    return out


def manifest(dst, ver, name, desc):
    mp = dst / "manifest.json"; man = jl(mp); v = [int(x) for x in ver.split(".")]
    man["header"]["version"] = v
    for m in man["modules"]: m["version"] = v
    man["header"]["name"] = name; man["header"]["description"] = desc
    wj(mp, man)


def main():
    for src, dst in ((R7_SRC, R7_DST), (R6_SRC, R6_DST)):
        if dst.exists(): shutil.rmtree(dst)
        shutil.copytree(src, dst)
    # ---- RP-07
    write_equines(R7_DST, EQUINES_07)
    wj(R7_DST / "animations/pw_equine_look.animation.json", look_anim("animation.pw_equine.look"))
    set_look(R7_DST, "horse", "animation.pw_equine.look"); set_look(R7_DST, "donkey", "animation.pw_equine.look")
    set_look(R7_DST, "mule", "animation.pw_equine.look", drop=("ar_neck_look",))
    eyes_ents = drop_pw_eyes(R7_DST)
    eyes = remove_eyes(R7_DST)
    log(f"rp07-1415: look -> animation.pw_equine.look (horse, donkey, mule; mule ar_neck_look dropped); pw_eyes dropped from {eyes_ents}; eyes removed {eyes}")
    manifest(R7_DST, R7_VER, f"AbsolutRealism Neutral Mobs RP v{R7_VER}",
             f"v{R7_VER} ({DATE}) EQUINES + EYES (D-C269): horse, donkey and mule rebuilt from the Patrix models (the head sits on the neck and "
             "leans with it, two ears, mane on the neck); they look at you by turning neck and head together. The added 3D/animated eyes are "
             "gone (villager, wandering trader, bee, ravager, zombie villager — its eyes are painted into the skin). Everything else "
             "byte-identical to v1.4.14.")
    # ---- RP-06
    write_equines(R6_DST, EQUINES_06)
    wj(R6_DST / "animations/pw_undead_equine_look.animation.json", look_anim("animation.pw_undead_equine.look"))
    set_look(R6_DST, "zombie_horse", "animation.pw_undead_equine.look"); set_look(R6_DST, "skeleton_horse", "animation.pw_undead_equine.look")
    manifest(R6_DST, R6_VER, f"AbsolutRealism Hostile Mobs RP v{R6_VER}",
             f"v{R6_VER} ({DATE}) UNDEAD EQUINES (D-C269): zombie horse and skeleton horse rebuilt from the Patrix models (head on the neck; the "
             "skeleton horse has its neck back); they look at you by turning neck and head together. Everything else byte-identical to v1.4.9.")
    log(f"rp06-1410: zombie/skeleton horse Converter B + animation.pw_undead_equine.look; manifests {R7_VER} / {R6_VER}")


if __name__ == "__main__":
    main()
