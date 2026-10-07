#!/usr/bin/env python3
"""ramp_v8.py — program 228 (his 12:20, 10-06): THE 8-BLOCK RAMP (rise 1 block over 8 cells, ~7.1 deg; the preferred street
ramp) for every ramp material, built by the v6.1 construction (tools/ramp_v6.py in the project: deck-on-line, step cubes
kissing the deck underside, cap filler at landing height, plumb-cut snow) + the 1.3.130 board-edge `cut` strips.

Self-check first: the 6 existing pieces (2_lo/2_hi, 4_q1..q4) x snow 0..4 are rebuilt by this code and compared with RP-04
1.3.158's shipped geometry, cube by cube (origin/size/pivot/rotation/uv within 0.002) — the 8-piece set is only trusted if
the 30 shipped geometries come out the same.

New pieces 8_e1..8_e8: base 2(i-1) px, rise 2 px, run 16 px. Snow 1..4 as the other families.
Outputs (into STAGE = _staging/ramps228/{rp,bp}):
  rp/models/blocks/pw_ramps8.geo.json              8 geometries (+ 32 snow geometries in pw_snowcaps_ramps8.geo.json)
  rp/textures/blocks/pw_deck7_<mat>_<var>.png      8 vars x mats (+ _n / _mer + texture_set) — the var atlas stretched
  rp/textures/blocks/pw_fill7e<i>_<mat>.png        side fills painted from the geometry (+ _n / _mer + texture_set)
  rp/textures/blocks/pw_rampcut8_<mat>.png         board-edge strips for the 7.1 deg board, snow 0..4 (+ _n / _mer)
  rp/terrain_texture_add.json                      the new keys
  bp/blocks/pw_ramp_<mat>_8_e<i>.json              from the shipped pw_ramp_<mat>_4_q1.json (permutations, var, snow)
Usage: ramp_v8.py [--check-only]"""
import copy
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path("/home/claude")
RP = ROOT / "_build/rp04-158"
BP = ROOT / "_build/bp02-227"
STAGE = ROOT / "_staging/ramps228"
TEX = 128
U = TEX / 16.0
DECK_T = 1.2
EPS = 0.02
INSET = 0.02
STEP_RISE = 2.0
STRIP_H = 9.6
PIECES = {"2_lo": (0, 8, 16), "2_hi": (8, 8, 16), "4_q1": (0, 4, 16), "4_q2": (4, 4, 16), "4_q3": (8, 4, 16), "4_q4": (12, 4, 16)}
PIECES8 = {f"8_e{i}": (2 * (i - 1), 2, 16) for i in range(1, 9)}
MATS = ["cobble", "smooth_stone", "stonebrick"]


def r4(v):
    return round(v, 4)


def rect_uv(z0, z1, y0, y1):
    return {"uv": [round((z0 + 8) * U, 3), round((16 - y1) * U, 3)], "uv_size": [round((z1 - z0) * U, 3), round((y1 - y0) * U, 3)]}


def box_uv(o, s):
    x0, y0, z0 = o
    x1, y1, z1 = o[0] + s[0], o[1] + s[1], o[2] + s[2]
    return {
        "up": {"uv": [round((x0 + 8) * U, 3), round((z0 + 8) * U, 3)], "uv_size": [round((x1 - x0) * U, 3), round((z1 - z0) * U, 3)]},
        "down": {"uv": [round((x0 + 8) * U, 3), round((z0 + 8) * U, 3)], "uv_size": [round((x1 - x0) * U, 3), round((z1 - z0) * U, 3)]},
        "north": {"uv": [round((8 - x1) * U, 3), round((16 - y1) * U, 3)], "uv_size": [round((x1 - x0) * U, 3), round((y1 - y0) * U, 3)]},
        "south": {"uv": [round((x0 + 8) * U, 3), round((16 - y1) * U, 3)], "uv_size": [round((x1 - x0) * U, 3), round((y1 - y0) * U, 3)]},
        "east": rect_uv(z0, z1, y0, y1),
        "west": rect_uv(z0, z1, y0, y1),
    }


def slope(base, rise, run):
    theta = math.atan2(rise, run)
    return theta, rise / run, math.hypot(rise, run)


def deck_cube(base, rise, run, thickness, material_up, lift=0.0, shift=0.0, trim_high=0.0):
    theta, k, L = slope(base, rise, run)
    y0 = base + lift - thickness
    cube = {
        "origin": [-8 + INSET, r4(y0), r4(-8 + shift)],
        "size": [r4(16 - 2 * INSET), r4(thickness), r4(L - trim_high)],
        "pivot": [0, r4(base), -8],
        "rotation": [r4(math.degrees(theta)), 0, 0],
        "uv": {
            "up": {"uv": [0, 0], "uv_size": [TEX, TEX], "material_instance": material_up},
            "down": {"uv": [0, 0], "uv_size": [TEX, TEX], "material_instance": material_up},
            "north": {"uv": [0, round((16 - thickness) * U, 3)], "uv_size": [TEX, round(thickness * U, 3)]},
            "south": {"uv": [0, round((16 - thickness) * U, 3)], "uv_size": [TEX, round(thickness * U, 3)]},
            "east": {"uv": [0, 0], "uv_size": [TEX, round(thickness * U, 3)]},
            "west": {"uv": [0, 0], "uv_size": [TEX, round(thickness * U, 3)]},
        },
    }
    if material_up == "snow":
        for f in cube["uv"].values():
            f["material_instance"] = "snow"
    return cube


def cap_filler(base, rise, run, thickness, lift, material=None):
    theta, k, L = slope(base, rise, run)
    top_at_8 = base + rise + lift / math.cos(theta)
    under_at_8 = top_at_8 - thickness / math.cos(theta)
    zc = 8 - thickness * math.sin(theta)
    o = [-8, r4(under_at_8), r4(zc)]
    s = [16, r4(top_at_8 - under_at_8), r4(8 - zc)]
    cube = {"origin": o, "size": s, "uv": box_uv(o, s)}
    if material:
        for f in cube["uv"].values():
            f["material_instance"] = material
    return cube


def snow_cubes(base, rise, run, level):
    theta, k, L = slope(base, rise, run)
    t_s = 2 * level * math.cos(theta)
    shift = (EPS + t_s) * math.tan(theta)
    slab = deck_cube(base, rise, run, t_s, "snow", lift=EPS + t_s, shift=shift, trim_high=t_s * math.tan(theta))
    cap = cap_filler(base, rise, run, t_s, EPS + t_s, material="snow")
    top_h = (EPS + t_s) / math.cos(theta)
    fz = t_s * math.sin(theta) + 0.02
    o = [-8, r4(base + EPS), -8]
    s = [16, r4(top_h - EPS), r4(fz)]
    filler = {"origin": o, "size": s, "uv": box_uv(o, s)}
    for f in filler["uv"].values():
        f["material_instance"] = "snow"
    return [slab, filler, cap]


def ramp_geometry(name, pieces, snow_level=0):
    base, rise, run = pieces[name]
    theta, k, L = slope(base, rise, run)
    under = DECK_T / math.cos(theta)
    cubes = []
    if base > 0:
        o, s = [-8, 0, -8], [16, base, 16]
        cubes.append({"origin": o, "size": s, "uv": box_uv(o, s)})
    i = 0
    while True:
        y_top = base + STEP_RISE * (i + 1)
        z0 = -8 + (y_top - base + under) / k
        if z0 >= 8 - 0.05:
            break
        o, s = [-8, r4(base + STEP_RISE * i), r4(z0)], [16, STEP_RISE, r4(8 - z0)]
        cubes.append({"origin": o, "size": s, "uv": box_uv(o, s)})
        i += 1
    cubes.append(deck_cube(base, rise, run, DECK_T, "deck", trim_high=DECK_T * math.tan(theta)))
    cubes.append(cap_filler(base, rise, run, DECK_T, 0.0))
    if snow_level:
        cubes.extend(snow_cubes(base, rise, run, snow_level))
    for c in cubes:                                # the shipped snow caps clamp a north-face v above the block top to 0
        for side in ("north", "south", "east", "west", "up", "down"):
            nf = c["uv"].get(side)
            if nf and nf.get("material_instance") == "snow" and nf["uv"][1] < 0:
                nf["uv"][1] = 0.0
    bones = [{"name": "ramp", "pivot": [0, 0, 0], "cubes": cubes}]
    bones.append({"name": "fills", "pivot": [0, 0, 0], "cubes": [
        {"origin": [7.75, 0, -8], "size": [0, 16, 16], "uv": {"east": {"uv": [TEX, 0], "uv_size": [-TEX, TEX], "material_instance": "fill"}}},
        {"origin": [-7.75, 0, -8], "size": [0, 16, 16], "uv": {"west": {"uv": [0, 0], "uv_size": [TEX, TEX], "material_instance": "fill"}}},
    ]})
    ident = "geometry.pw_ramp_%s%s" % (name, ("_snow%d" % snow_level) if snow_level else "")
    return {"description": {"identifier": ident, "texture_width": TEX, "texture_height": TEX,
                            "visible_bounds_width": 2, "visible_bounds_height": 2, "visible_bounds_offset": [0, 0.5, 0]},
            "bones": bones}


def board_of(g):
    for b in g["bones"]:
        for ci, c in enumerate(b.get("cubes", [])):
            if c.get("rotation") and c["uv"]["up"].get("material_instance") == "deck":
                return ci, c
    raise KeyError("no deck board")


def cut_slots(angles):
    slots, v = {}, 0.0
    for ang in angles:
        for lvl in range(5):
            slots[(ang, lvl)] = v
            v += STRIP_H + 0.4
    assert v <= 128, v
    return slots


def apply_cut(g, slot_v0):
    ci, board = board_of(g)
    board["uv"]["west"] = {"uv": [0, round(slot_v0, 3)], "uv_size": [128, STRIP_H], "material_instance": "cut"}
    board["uv"]["east"] = {"uv": [128, round(slot_v0, 3)], "uv_size": [-128, STRIP_H], "material_instance": "cut"}


# --------------------------------------------------------------------------------------------- the self-check
def close(a, b, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        if set(a) != set(b):
            return f"{path}: keys {sorted(set(a) ^ set(b))}"
        for k in a:
            r = close(a[k], b[k], f"{path}.{k}")
            if r:
                return r
        return None
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return f"{path}: len {len(a)} vs {len(b)}"
        for i, (x, y) in enumerate(zip(a, b)):
            r = close(x, y, f"{path}[{i}]")
            if r:
                return r
        return None
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return None if abs(a - b) <= 0.002 else f"{path}: {a} vs {b}"
    return None if a == b else f"{path}: {a!r} vs {b!r}"


def shipped_geometries():
    out = {}
    for fn in ("pw_ramps.geo.json", "pw_snowcaps.geo.json"):
        doc = json.loads((RP / "models/blocks" / fn).read_text(encoding="utf-8-sig"))
        for g in doc["minecraft:geometry"]:
            m = re.match(r"geometry\.pw_ramp_(.+?)(?:_snow(\d))?$", g["description"]["identifier"])
            if m:
                out[(m.group(1), int(m.group(2) or 0))] = g
    return out


def self_check():
    ship = shipped_geometries()
    slots = cut_slots(("14", "26"))
    bad = []
    for name in PIECES:
        for lvl in range(5):
            g = ramp_geometry(name, PIECES, lvl)
            apply_cut(g, slots[("14" if name.startswith("4_") else "26", lvl)])
            r = close(g, ship[(name, lvl)], f"{name}/snow{lvl}")
            if r:
                bad.append(r)
    return len(PIECES) * 5, bad



# --------------------------------------------------------------------------------------------- the 8-ramp
sys.path.insert(0, str(ROOT / "tools"))
import profile_render as pr  # noqa: E402

TB = RP / "textures/blocks"
SHADE = 0.855                                     # the shipped fills: the var-0 atlas x 0.855 (measured: mean diff 0.5 / 255)


def strip_to_world(cube, side, fu, fv):
    o, s = cube["origin"], cube["size"]
    zl = o[2] + (fu if side == "west" else 1.0 - fu) * s[2]
    yl = o[1] + s[1] - fv * s[1]
    piv = cube.get("pivot") or [0, 0, 0]
    y, z = pr.rot_yz(yl, zl, piv[1], piv[2], (cube.get("rotation") or [0, 0, 0])[0])
    return z, y


def load_rgba(name):
    return Image.open(TB / f"{name}.png").convert("RGBA")


def save_set(img, nrm, mer, name, out):
    """colour + _n + _mer + texture_set (format 1.21.30, as the shipped ramp textures)"""
    img.save(out / f"{name}.png")
    nrm.save(out / f"{name}_n.png")
    mer.save(out / f"{name}_mer.png")
    (out / f"{name}.texture_set.json").write_text(json.dumps({"format_version": "1.21.30", "minecraft:texture_set": {
        "color": name, "normal": f"{name}_n", "metalness_emissive_roughness_subsurface": f"{name}_mer"}}, indent=1))


def deck_textures(mat, out, keys):
    k = math.hypot(2, 16) / 16
    for var in range(8):
        src = f"pw_rampv4_{mat}_{var}"
        imgs = [load_rgba(src), load_rgba(src + "_n"), load_rgba(src + "_mer")]
        h = int(round(imgs[0].height * k))
        imgs = [im.resize((im.width, h), Image.LANCZOS) for im in imgs]
        name = f"pw_deck7_{mat}_{var}"
        save_set(*imgs, name, out)
        keys[name] = {"textures": f"textures/blocks/{name}"}


def fill_textures(mat, out, keys):
    """profile space (west face, identity uv): u = (z + 8) * 16, v = (16 - y) * 16 on a 256 x 256 texture; opaque where
    the point lies under the deck's TOP line (the walking surface) — the solids hide what is not a notch, nothing stands
    proud of the profile"""
    base = [load_rgba(f"pw_rampv4_{mat}_0" + s).resize((256, 256), Image.LANCZOS) for s in ("", "_n", "_mer")]
    col = np.asarray(base[0]).astype(np.float32)
    col[..., :3] *= SHADE
    for i in range(1, 9):
        b, rise = 2 * (i - 1), 2
        v, u = np.mgrid[0:256, 0:256]
        z, y = -8 + (u + 0.5) / 16.0, 16 - (v + 0.5) / 16.0
        top = b + rise * (z + 8) / 16.0
        a = (y <= top + 1.0 / 16) & (y >= 0)
        img = col.copy(); img[..., 3] = np.where(a, 255, 0)
        n = np.asarray(base[1]).copy(); n[..., 3] = np.where(a, 255, 0)
        m = np.asarray(base[2]).copy()
        name = f"pw_fill7e{i}_{mat}"
        save_set(Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGBA"), Image.fromarray(n, "RGBA"), Image.fromarray(m, "RGBA"), name, out)
        keys[name] = {"textures": f"textures/blocks/{name}"}


def cut_textures(mat, geos, out, keys):
    """the 1.3.130 board-edge strips for the 7.1 deg board: snow 0..4 in 5 slots; texels outside the board's visible
    side (below the plinth top, in front of the cap filler, behind the snow toe filler) are cleared"""
    slots = cut_slots(("7",))
    srcs = [np.asarray(load_rgba(f"pw_rampv4_{mat}_0" + s)) for s in ("", "_n", "_mer")]
    outs = [np.zeros((128, 128, 4), np.uint8) for _ in srcs]
    theta = math.atan2(2, 16)
    for lvl in range(5):
        g = geos[("8_e1", lvl)]
        ci, board = board_of(g)
        z_cap = 8.0 - DECK_T * math.sin(theta)
        z_inner = None if not lvl else -8.0 + 2 * lvl * math.cos(theta) * math.sin(theta) * math.cos(theta) / math.cos(theta) + 0.02
        ty0 = int(round(slots[("7", lvl)]))
        keep = np.ones((10, 128), bool)
        for r in range(10):
            for c in range(128):
                pts = [strip_to_world(board, "west", (c + dx) / 128.0, (r + dy) / 10.0) for dx in (0, 1) for dy in (0, 1)]
                zmin = min(q[0] for q in pts); zmax = max(q[0] for q in pts); ymin = min(q[1] for q in pts)
                if ymin < 0 - 1e-6 or zmax > z_cap + 1e-6 or (z_inner is not None and zmin < z_inner - 1e-6):
                    keep[r, c] = False
        for s, o in zip(srcs, outs):
            patch = s[0:10, 0:128].copy()
            if patch.shape[2] == 4:
                patch[..., 3] = np.where(keep, patch[..., 3], 0)
            o[ty0:ty0 + 10, 0:128] = patch
    name = f"pw_rampcut8_{mat}"
    save_set(*[Image.fromarray(o, "RGBA") for o in outs], name, out)
    keys[name] = {"textures": f"textures/blocks/{name}"}
    return slots


def blocks(mat, out):
    src = json.loads((BP / "blocks" / f"pw_ramp_{mat}_4_q1.json").read_text(encoding="utf-8-sig"))
    made = []
    for i in range(1, 9):
        d = copy.deepcopy(src)
        txt = json.dumps(d)
        txt = txt.replace(f'"pw:ramp_{mat}_4_q1"', f'"pw:ramp_{mat}_8_e{i}"')
        txt = re.sub(r'"geometry\.pw_ramp_4_q1(_snow\d)?"', lambda m: f'"geometry.pw_ramp_8_e{i}{m.group(1) or ""}"', txt)
        txt = re.sub(rf'"pw_deck14_{mat}_(\d)"', lambda m: f'"pw_deck7_{mat}_{m.group(1)}"', txt)
        txt = txt.replace(f'"pw_fill14q1_{mat}"', f'"pw_fill7e{i}_{mat}"').replace(f'"pw_rampcut_{mat}"', f'"pw_rampcut8_{mat}"')
        d = json.loads(txt)
        h = 2 * (i - 1) + 2                       # the v5 rule the family keeps: a flat box at base + 2 px
        for key in ("minecraft:collision_box", "minecraft:selection_box"):
            d["minecraft:block"]["components"][key] = {"origin": [-8, 0, -8], "size": [16, h, 16]}
        assert "4_q1" not in json.dumps(d) and "deck14" not in json.dumps(d) and "fill14" not in json.dumps(d), (mat, i)
        (out / f"pw_ramp_{mat}_8_e{i}.json").write_text(json.dumps(d, indent=1))
        made.append(f"pw:ramp_{mat}_8_e{i}")
    return made


def build(mats=MATS):
    rp, bp = STAGE / "rp", STAGE / "bp"
    (rp / "models/blocks").mkdir(parents=True, exist_ok=True); (rp / "textures/blocks").mkdir(parents=True, exist_ok=True)
    (bp / "blocks").mkdir(parents=True, exist_ok=True)
    slots = cut_slots(("7",))
    geos = {}
    for name in PIECES8:
        for lvl in range(5):
            g = ramp_geometry(name, PIECES8, lvl)
            apply_cut(g, slots[("7", lvl)])
            geos[(name, lvl)] = g
    (rp / "models/blocks/pw_ramps8.geo.json").write_text(json.dumps({"format_version": "1.16.0", "minecraft:geometry": [geos[(n, 0)] for n in PIECES8]}, indent=1))
    (rp / "models/blocks/pw_snowcaps_ramps8.geo.json").write_text(json.dumps({"format_version": "1.16.0", "minecraft:geometry": [geos[(n, l)] for n in PIECES8 for l in (1, 2, 3, 4)]}, indent=1))
    keys, made = {}, []
    for mat in mats:
        deck_textures(mat, rp / "textures/blocks", keys)
        fill_textures(mat, rp / "textures/blocks", keys)
        cut_textures(mat, geos, rp / "textures/blocks", keys)
        made += blocks(mat, bp / "blocks")
    (rp / "terrain_texture_add.json").write_text(json.dumps(keys, indent=1))
    return geos, keys, made



# --------------------------------------------------------------------------------------------- new stone materials (his 12:20)
PATRIX_ZIP = ROOT / "_intake/patrix262_basic/Patrix_26.2_128x_basic.zip"
CTM = "assets/minecraft/optifine/ctm/patrix/"
NEW_MATS = {                      # material id -> Patrix CTM variant folder (>= 8 tiles each, 128 px)
    "andesite": "andesite", "diorite": "diorite", "granite": "granite", "tuff": "tuff/normal", "tuff_brick": "tuff/brick",
    "calcite": "calcite", "blackstone": "blackstone/stone", "blackstone_brick": "blackstone/bricks/default",
    "cobbled_deepslate": "deepslate/cobbled", "deepslate_brick": "deepslate/brick/default", "deepslate_tile": "deepslate/tile",
    "brick": "bricks", "mud_brick": "mud/brick", "mossy_cobble": "cobblestone/mossy", "mossy_stonebrick": "stone_bricks/mossy",
    "stone": "stone",
}
DECK = {"2_lo": "pw_deck26", "2_hi": "pw_deck26", "4_q1": "pw_deck14", "4_q2": "pw_deck14", "4_q3": "pw_deck14", "4_q4": "pw_deck14"}
FILL = {"2_lo": "pw_fill26l", "2_hi": "pw_fill26u", "4_q1": "pw_fill14q1", "4_q2": "pw_fill14q2", "4_q3": "pw_fill14q3", "4_q4": "pw_fill14q4"}
for _i in range(1, 9):
    DECK[f"8_e{_i}"] = "pw_deck7"; FILL[f"8_e{_i}"] = f"pw_fill7e{_i}"
ALL_PIECES = dict(PIECES, **PIECES8)


def atlas(mat, folder, out, keys):
    """pw_rampv4_<mat>_<var> (var 0..7) from Patrix tiles 1..8 (+ #156 normal / MERS), as the shipped cobble atlas
    (pw_rampv4_cobble_k ~ Patrix cobblestone tile k+1, measured)"""
    import io, zipfile
    sys.path.insert(0, str(ROOT / "tools"))
    import mers_derive as MD
    z = zipfile.ZipFile(PATRIX_ZIP)
    rd = lambda n: Image.open(io.BytesIO(z.read(CTM + folder + "/" + n))).convert("RGBA")
    for var in range(8):
        k = var + 1
        col = rd(f"{k}.png").resize((128, 128), Image.LANCZOS)
        try:
            nrm = Image.fromarray(MD.normal_156(np.asarray(rd(f"{k}_n.png").resize((128, 128), Image.LANCZOS))), "RGBA")
        except KeyError:
            nrm = Image.new("RGBA", (128, 128), (128, 128, 255, 255))
        try:
            mer = Image.fromarray(MD.mers_156(np.asarray(rd(f"{k}_s.png").resize((128, 128), Image.BOX))), "RGBA")
        except KeyError:
            mer = Image.new("RGBA", (128, 128), (0, 0, 230, 0))
        name = f"pw_rampv4_{mat}_{var}"
        save_set(col, nrm, mer, name, out)
        keys[name] = {"textures": f"textures/blocks/{name}"}


def load_any(name, out):
    p = out / f"{name}.png"
    return Image.open(p if p.exists() else TB / f"{name}.png").convert("RGBA")


def decks_all(mat, out, keys):
    for prefix, (rise, run) in (("pw_deck26", (8, 16)), ("pw_deck14", (4, 16)), ("pw_deck7", (2, 16))):
        k = math.hypot(rise, run) / run
        for var in range(8):
            src = f"pw_rampv4_{mat}_{var}"
            imgs = [load_any(src + s, out) for s in ("", "_n", "_mer")]
            h = int(round(imgs[0].height * k))
            name = f"{prefix}_{mat}_{var}"
            save_set(*[im.resize((im.width, h), Image.LANCZOS) for im in imgs], name, out)
            keys[name] = {"textures": f"textures/blocks/{name}"}


def fills_all(mat, out, keys):
    base = [load_any(f"pw_rampv4_{mat}_0" + s, out).resize((256, 256), Image.LANCZOS) for s in ("", "_n", "_mer")]
    col = np.asarray(base[0]).astype(np.float32); col[..., :3] *= SHADE
    v, u = np.mgrid[0:256, 0:256]
    z, y = -8 + (u + 0.5) / 16.0, 16 - (v + 0.5) / 16.0
    for piece, (b, rise, run) in ALL_PIECES.items():
        a = (y <= b + rise * (z + 8) / run + 1.0 / 16) & (y >= 0)
        img = col.copy(); img[..., 3] = np.where(a, 255, 0)
        n = np.asarray(base[1]).copy(); n[..., 3] = np.where(a, 255, 0)
        name = f"{FILL[piece]}_{mat}"
        if name in keys:
            continue
        save_set(Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGBA"), Image.fromarray(n, "RGBA"), Image.fromarray(np.asarray(base[2]).copy(), "RGBA"), name, out)
        keys[name] = {"textures": f"textures/blocks/{name}"}


def cuts_all(mat, out, keys):
    """pw_rampcut_<mat> (14 / 26 deg, as 1.3.130) + pw_rampcut8_<mat> (7.1 deg)"""
    for tex_name, angles in ((f"pw_rampcut_{mat}", ("14", "26")), (f"pw_rampcut8_{mat}", ("7",))):
        slots = cut_slots(angles)
        srcs = [np.asarray(load_any(f"pw_rampv4_{mat}_0" + s, out)) for s in ("", "_n", "_mer")]
        outs = [np.zeros((128, 128, 4), np.uint8) for _ in srcs]
        for ang in angles:
            shape = {"14": "4_q1", "26": "2_lo", "7": "8_e1"}[ang]
            b, rise, run = ALL_PIECES[shape]
            theta = math.atan2(rise, run)
            for lvl in range(5):
                g = ramp_geometry(shape, ALL_PIECES, lvl)
                ci, board = board_of(g)
                z_cap = 8.0 - DECK_T * math.sin(theta)
                z_inner = None if not lvl else -8.0 + 2 * lvl * math.sin(theta) * math.cos(theta) + 0.02
                ty0 = int(round(slots[(ang, lvl)]))
                keep = np.ones((10, 128), bool)
                for r in range(10):
                    for c in range(128):
                        pts = [strip_to_world(board, "west", (c + dx) / 128.0, (r + dy) / 10.0) for dx in (0, 1) for dy in (0, 1)]
                        zmin = min(q[0] for q in pts); zmax = max(q[0] for q in pts); ymin = min(q[1] for q in pts)
                        if ymin < 0 - 1e-6 or zmax > z_cap + 1e-6 or (z_inner is not None and zmin < z_inner - 1e-6):
                            keep[r, c] = False
                for s, o in zip(srcs, outs):
                    patch = s[0:10, 0:128].copy()
                    patch[..., 3] = np.where(keep, patch[..., 3], 0)
                    o[ty0:ty0 + 10, 0:128] = patch
        save_set(*[Image.fromarray(o, "RGBA") for o in outs], tex_name, out)
        keys[tex_name] = {"textures": f"textures/blocks/{tex_name}"}


def blocks_all(mat, out):
    """every piece of the family for a new material, cloned from the shipped cobble block (8_e* from the staged cobble)"""
    made = []
    for piece in ALL_PIECES:
        src = (STAGE / "bp/blocks" if piece.startswith("8_") else BP / "blocks") / f"pw_ramp_cobble_{piece}.json"
        txt = src.read_text(encoding="utf-8-sig")
        txt = txt.replace('"pw:ramp_cobble_', f'"pw:ramp_{mat}_')
        txt = re.sub(r'"(pw_(?:rampv4|deck26|deck14|deck7|fill26l|fill26u|fill14q\d|fill7e\d|rampcut8|rampcut))_cobble((?:_\d)?)"', lambda m: f'"{m.group(1)}_{mat}{m.group(2)}"', txt)
        assert "cobble" not in txt.replace(mat, "") or mat.endswith("cobble"), (mat, piece, re.findall(r'"[^"]*cobble[^"]*"', txt)[:3])
        (out / f"pw_ramp_{mat}_{piece}.json").write_text(txt)
        made.append(f"pw:ramp_{mat}_{piece}")
    return made


def build_new_mats(mats=None):
    rp_t, bp_b = STAGE / "rp/textures/blocks", STAGE / "bp/blocks"
    keys = json.loads((STAGE / "rp/terrain_texture_add.json").read_text())
    made = []
    for mat, folder in (mats or NEW_MATS).items():
        atlas(mat, folder, rp_t, keys)
        decks_all(mat, rp_t, keys)
        fills_all(mat, rp_t, keys)
        cuts_all(mat, rp_t, keys)
        made += blocks_all(mat, bp_b)
        print(f"  {mat}: atlas + decks + fills + cuts + {len(ALL_PIECES)} blocks", flush=True)
    (STAGE / "rp/terrain_texture_add.json").write_text(json.dumps(keys, indent=1))
    return keys, made


if __name__ == "__main__":
    n, bad = self_check()
    print(f"self-check: {n} shipped geometries rebuilt, {len(bad)} differ")
    for b in bad[:12]:
        print("  ", b)
    if bad or "--check-only" in sys.argv:
        sys.exit(1 if bad else 0)
    geos, keys, made = build()
    print(f"8-ramp: {len(geos)} geometries, {len(keys)} texture keys, {len(made)} blocks -> {STAGE}")
    if "--new-mats" in sys.argv:
        keys2, made2 = build_new_mats()
        print(f"new materials: {len(NEW_MATS)}; texture keys now {len(keys2)}; blocks {len(made2)}")
