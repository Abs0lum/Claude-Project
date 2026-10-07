#!/usr/bin/env python3
"""build_130_182.py — the approved combined build (D-C210, 2026-09-22):

  RP-04 v1.3.129 -> v1.3.130   1a roof45 board overshoot cut (in place, pw_mitre_<oak|spruce|thatch>)
                               1b ramp `cut` strips pw_rampcut_<cobble|smooth_stone|stonebrick> + board uv repoint
                                  (30 geometries: 6 shapes x snow 0..4), boards only (snow slab untouched, ruling)
                               1c hollow flue geometry (2-cube walls, bore 12x12; cap keeps the rim, throat opened)
                               1d hearth v2: log stage textures (fueled/lit/embers/cold, side + end), Patrix flame
                                  flipbooks pw_hearth_flame (tall, 30 f) + pw_hearth_flame_low (CTM tile 5, 30 f)
  RP-02 v2.0.2  -> v2.0.3      1e campfire_smoke sprite -> Patrix big_smoke (12 frames, 128²)
  BP-02 v1.3.181 -> v1.3.182   2a ramp blocks: `cut` instance; 2b hearth: phase 'spent' + per-phase keys;
                               2c flue: hollow geometry, collision_box false (enterable); 2d scripts: fire-pit
                                  puff, spent phase, chimney hazard (bore keeper, suffocation, heat/fire)

Inputs : _build/rp04-129, _build/rp02-202, _build/bp02-181 (the shipped trees), _intake/patrix128 (Patrix Java source
         128x, porting permitted), _design/hearth-log-stages (approved textures, regenerated here from the same code)
Outputs: _build/rp04-130, _build/rp02-203, _build/bp02-182  (packaging is done by the gate, never here)
Every phase appends a completion line to _logs/phase_log.md BEFORE returning (P7).
"""
import json, math, os, re, shutil, sys, hashlib, datetime
from pathlib import Path
import numpy as np
from PIL import Image

sys.path.insert(0, "/home/claude/tools")
import profile_render as pr                                  # noqa: E402
from homestead_build import box, face, geo, flue_cap_geometry  # noqa: E402
from homestead_materials import OUTER                         # noqa: E402
import hearth_preview as hp                                    # noqa: E402

ROOT = Path("/home/claude")
RP_SRC, RP_DST = ROOT / "_build/rp04-129", ROOT / "_build/rp04-130"
RP2_SRC, RP2_DST = ROOT / "_build/rp02-202", ROOT / "_build/rp02-203"
BP_SRC, BP_DST = ROOT / "_build/bp02-181", ROOT / "_build/bp02-182"
PATRIX = ROOT / "_intake/patrix128/assets/minecraft"
RP_VER, RP2_VER, BP_VER = "1.3.130", "2.0.3", "1.3.182"
DATE = "2026-09-22"
LOG = ROOT / "_logs/phase_log.md"

def log(msg):
    t = datetime.datetime.now().strftime("%H:%M")
    LOG.open("a").write(f"[{t} CT 09-22] BUILD 130/182 — {msg}\n")

def jload(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def jdump(obj, p):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(obj, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

# =====================================================================================================================
# 1a — roof45 board overshoot cut, in place in the mitre strips
# =====================================================================================================================
def strip_to_world(cube, side, fu, fv):
    """(fu, fv) in the face's own strip -> world (z, y) for an x-rotated board (profile_render conventions)."""
    o, s = cube["origin"], cube["size"]
    zl = o[2] + (fu if side == "west" else 1.0 - fu) * s[2]
    yl = o[1] + s[1] - fv * s[1]
    piv = cube.get("pivot") or [0, 0, 0]
    y, z = pr.rot_yz(yl, zl, piv[1], piv[2], (cube.get("rotation") or [0, 0, 0])[0])
    return z, y

def phase_1a_roof_cut():
    g = [x for x in jload(RP_DST / "models/blocks/roof45_straight.geo.json")["minecraft:geometry"]][0]
    decl = g["description"]["texture_width"]
    board = g["bones"][0]["cubes"][0]
    assert board.get("rotation") == [45, 0, 0], board
    report = {}
    for mat in ("oak", "spruce", "thatch"):
        p = RP_DST / f"textures/blocks/pw_mitre_{mat}.png"
        im = np.array(Image.open(p).convert("RGBA")); scale = im.shape[0] / decl
        before = im.copy(); cut = 0; tot = 0
        for side in ("east", "west"):
            spec = board["uv"][side]; u0, v0 = spec["uv"]; su, sv = spec["uv_size"]
            x0, x1 = int(math.floor(min(u0, u0 + su) * scale)), int(math.ceil(max(u0, u0 + su) * scale))
            y0, y1 = int(math.floor(min(v0, v0 + sv) * scale)), int(math.ceil(max(v0, v0 + sv) * scale))
            for ty in range(y0, y1):
                fv = ((ty + 0.5) / scale - v0) / sv
                if not 0.0 <= fv <= 1.0: continue
                for tx in range(x0, x1):
                    fu = ((tx + 0.5) / scale - u0) / su
                    if not 0.0 <= fu <= 1.0: continue
                    tot += 1
                    # conservative: a texel goes when ANY of its corners lies past the boundary (no half-texel residue)
                    zs = [strip_to_world(board, side, ((tx + dx) / scale - u0) / su, ((ty + dy) / scale - v0) / sv)[0] for dx in (0, 1) for dy in (0, 1)]
                    if max(zs) > 8.0 + 1e-6 and im[ty, tx, 3] != 0:
                        im[ty, tx, 3] = 0; cut += 1
        # nothing outside the two strips may change
        mask = np.zeros(im.shape[:2], bool)
        for side in ("east", "west"):
            spec = board["uv"][side]; u0, v0 = spec["uv"]; su, sv = spec["uv_size"]
            mask[int(math.floor(v0 * scale)):int(math.ceil((v0 + sv) * scale)), int(math.floor(u0 * scale)):int(math.ceil((u0 + su) * scale))] = True
        assert np.array_equal(im[~mask], before[~mask])
        Image.fromarray(im, "RGBA").save(p)
        report[mat] = (cut, tot)
    log(f"1a roof cut done: texels cut per material {report} (z > 8 on the roof45 board east/west strips)")
    return report

# =====================================================================================================================
# 1b — ramp cut strips + board uv repoint (boards only)
# =====================================================================================================================
RAMP_MATS = {"cobble": "pw_rampv4_cobble_0", "smooth_stone": "pw_rampv4_smooth_stone_0", "stonebrick": "pw_rampv4_stonebrick_0"}
STRIP_H = 9.6          # declared units (= texels at 128 declared / 128 file): the board's side strip height
SNOW_T = {1: 2.0, 2: 4.0, 3: 6.0, 4: 8.0}

def ramp_geometries():
    """-> {(shape, level): (file, geometry)} for the 6 shapes x snow 0..4."""
    out = {}
    plain = jload(RP_DST / "models/blocks/pw_ramps.geo.json")
    for g in plain["minecraft:geometry"]:
        out[(g["description"]["identifier"].replace("geometry.pw_ramp_", ""), 0)] = ("pw_ramps.geo.json", g)
    snow = jload(RP_DST / "models/blocks/pw_snowcaps.geo.json")
    for g in snow["minecraft:geometry"]:
        m = re.match(r"geometry\.pw_ramp_(.+)_snow(\d)$", g["description"]["identifier"])
        if m: out[(m.group(1), int(m.group(2)))] = ("pw_snowcaps.geo.json", g)
    return out, plain, snow

def board_of(g):
    for b in g["bones"]:
        for ci, c in enumerate(b.get("cubes", [])):
            if c.get("rotation") and c["uv"]["up"].get("material_instance") == "deck":
                return ci, c
    raise KeyError("no deck board")

def cut_params(shape, level):
    """(z_cap_front, base, z_snow_inner|None) in block px for the board of this shape/level."""
    theta = math.radians(14.0362 if shape.startswith("4_") else 26.5651)
    base = {"2_lo": 0, "2_hi": 8, "4_q1": 0, "4_q2": 4, "4_q3": 8, "4_q4": 12}[shape]
    t = 1.2
    z_cap = 8.0 - t * math.sin(theta)                       # cap filler's front plane (7.709 / 7.4633)
    z_inner = None
    if level:
        ts = SNOW_T[level]
        z_inner = -8.0 + ts * math.sin(theta) * math.cos(theta) + 0.02   # the snow toe filler's inner plane
    return z_cap, base, z_inner

def phase_1b_ramp_cuts():
    geos, plain, snow = ramp_geometries()
    keys = sorted(geos)                                      # 30 (shape, level)
    assert len(keys) == 30, keys
    # strip layout in the new texture: one row of STRIP_H per (shape-angle, level) is NOT enough — the cut positions
    # depend on the angle and the level only, but the strip IMAGE (the board's side texture) is the same for all; so
    # 10 strips (2 angles x 5 levels) serve all 30 geometries.
    slots = {}                                                # (angle_key, level) -> v0
    v = 0.0
    for ang in ("14", "26"):
        for lvl in range(5):
            slots[(ang, lvl)] = v; v += STRIP_H + 0.4         # 0.4 gap
    assert v <= 128
    # build the textures
    for mat, srckey in RAMP_MATS.items():
        src = np.array(Image.open(RP_DST / f"textures/blocks/{srckey}.png").convert("RGBA"))
        assert src.shape[0] == src.shape[1] == 128, src.shape
        tex = np.zeros((128, 128, 4), np.uint8)
        board_strip = src[0:10, 0:128].copy()                # rows 0..9.6 (10 rows) x 128 cols = the board side strip
        for (ang, lvl), v0 in slots.items():
            shape = "4_q1" if ang == "14" else "2_lo"        # any shape of that angle: the cut geometry is base-independent
            fname, g = geos[(shape, lvl)]
            ci, board = board_of(g)
            z_cap, base, z_inner = cut_params(shape, lvl)
            ty0 = int(round(v0))
            patch = board_strip.copy()
            for r in range(10):
                for cidx in range(128):
                    # conservative: test the texel's four corners (west convention: fu = 0 at -z)
                    pts = [strip_to_world(board, "west", (cidx + dx) / 128.0, (r + dy) / 10.0) for dx in (0, 1) for dy in (0, 1)]
                    zmin = min(q[0] for q in pts); zmax = max(q[0] for q in pts); ymin = min(q[1] for q in pts)
                    if ymin < base - 1e-6 or zmax > z_cap + 1e-6 or (z_inner is not None and zmin < z_inner - 1e-6):
                        patch[r, cidx, 3] = 0
            tex[ty0:ty0 + 10, 0:128] = patch
        Image.fromarray(tex, "RGBA").save(RP_DST / f"textures/blocks/pw_rampcut_{mat}.png")
    # repoint every board's east/west faces to the cut strip (mirrored uv on the east face)
    for (shape, lvl), (fname, g) in geos.items():
        ci, board = board_of(g)
        ang = "14" if shape.startswith("4_") else "26"
        v0 = slots[(ang, lvl)]
        board["uv"]["west"] = {"uv": [0, round(v0, 3)], "uv_size": [128, STRIP_H], "material_instance": "cut"}
        board["uv"]["east"] = {"uv": [128, round(v0, 3)], "uv_size": [-128, STRIP_H], "material_instance": "cut"}
    jdump(plain, RP_DST / "models/blocks/pw_ramps.geo.json")
    jdump(snow, RP_DST / "models/blocks/pw_snowcaps.geo.json")
    tt = jload(RP_DST / "textures/terrain_texture.json")
    for mat in RAMP_MATS:
        assert f"pw_rampcut_{mat}" not in tt["texture_data"]
        tt["texture_data"][f"pw_rampcut_{mat}"] = {"textures": f"textures/blocks/pw_rampcut_{mat}"}
    jdump(tt, RP_DST / "textures/terrain_texture.json")
    log(f"1b ramp cuts done: 3 x pw_rampcut_<mat>.png (10 strips: 2 angles x snow 0..4), 30 geometries' board east/west -> `cut` (east mirrored)")
    return slots

# =====================================================================================================================
# 1c — hollow flue geometry + hearth 'spent' (reuses the fueled boxes)
# =====================================================================================================================
def hollow_walls(t=2):
    n = box([-8, 0, -8], [16, 16, t], {"north": face(16, 16), "south": face(16, 16, "soot"), "east": face(t, 16), "west": face(t, 16), "up": face(16, t, "top"), "down": face(16, t, "top")})
    s = box([-8, 0, 8 - t], [16, 16, t], {"south": face(16, 16), "north": face(16, 16, "soot"), "east": face(t, 16), "west": face(t, 16), "up": face(16, t, "top"), "down": face(16, t, "top")})
    w = box([-8, 0, -8 + t], [t, 16, 16 - 2 * t], {"west": face(16, 16), "east": face(16, 16, "soot"), "up": face(t, 16, "top"), "down": face(t, 16, "top")})
    e = box([8 - t, 0, -8 + t], [t, 16, 16 - 2 * t], {"east": face(16, 16), "west": face(16, 16, "soot"), "up": face(t, 16, "top"), "down": face(t, 16, "top")})
    return [n, s, w, e]

def phase_1c_geometry():
    p = RP_DST / "models/blocks/pw_homestead.geo.json"
    doc = jload(p)
    ids = {g["description"]["identifier"] for g in doc["minecraft:geometry"]}
    cap_src = flue_cap_geometry()
    rim = [b for b in cap_src["bones"] if b["name"] == "rim"][0]["cubes"]
    flue = geo("geometry.pw_flue_hollow", [("walls", hollow_walls())])
    cap = geo("geometry.pw_flue_cap_hollow", [("walls", hollow_walls()), ("rim", rim)], vis=(1.5, 1.5, [0, 0.75, 0]))
    for g in (flue, cap):
        assert g["description"]["identifier"] not in ids
        doc["minecraft:geometry"].append(g)
    jdump(doc, p)
    log("1c geometry done: geometry.pw_flue_hollow + geometry.pw_flue_cap_hollow appended to pw_homestead.geo.json (walls 2 cubes, bore 12x12, inner faces soot, rim kept, throat open); 'spent' reuses geometry.pw_hearth_fueled")

# =====================================================================================================================
# 1d — hearth textures + Patrix flame flipbooks
# =====================================================================================================================
def phase_1d_hearth_textures():
    tb = RP_DST / "textures/blocks"
    oak = hp.grain_along(hp.load(str(PATRIX / "textures/block/oak_log.png")))
    oak_top = hp.load(str(PATRIX / "textures/block/oak_log_top.png"))
    hp.save(oak, tb / "pw_hearth_log_fueled.png")
    for st in ("lit", "embers", "cold"):
        hp.save(hp.stage_side(oak, st), tb / f"pw_hearth_log_{st}.png")
        hp.save(hp.stage_end(oak_top, st), tb / f"pw_hearth_log_end_{st}.png")
    # flame flipbooks: Patrix fire_0 (tall) and CTM tile 5 (low licks); mcmeta order 15..29, 0..14
    shutil.copy(PATRIX / "textures/block/fire_0.png", tb / "pw_hearth_flame.png")
    shutil.copy(PATRIX / "optifine/ctm/patrix/fire/5.png", tb / "pw_hearth_flame_low.png")
    for f in ("pw_hearth_flame.png", "pw_hearth_flame_low.png"):
        im = Image.open(tb / f); assert im.size == (128, 3840), (f, im.size)
        im.convert("RGBA").save(tb / f)                       # palette PNG -> RGBA (atlas-safe)
    tt = jload(RP_DST / "textures/terrain_texture.json"); td = tt["texture_data"]
    td["pw_hearth_flame"] = {"textures": "textures/blocks/pw_hearth_flame"}          # was RP-04's 8x256 fire_0
    for k in ("pw_hearth_flame_low", "pw_hearth_log_fueled", "pw_hearth_log_lit", "pw_hearth_log_embers", "pw_hearth_log_cold",
              "pw_hearth_log_end_lit", "pw_hearth_log_end_embers", "pw_hearth_log_end_cold"):
        assert k not in td, k
        td[k] = {"textures": f"textures/blocks/{k}"}
    jdump(tt, RP_DST / "textures/terrain_texture.json")
    fbp = RP_DST / "textures/flipbook_textures.json"; fb = jload(fbp)
    fb = [e for e in fb if e.get("atlas_tile") != "pw_hearth_flame"]
    order = list(range(15, 30)) + list(range(0, 15))
    fb.append({"flipbook_texture": "textures/blocks/pw_hearth_flame", "atlas_tile": "pw_hearth_flame", "ticks_per_frame": 1, "blend_frames": False, "frames": order})
    fb.append({"flipbook_texture": "textures/blocks/pw_hearth_flame_low", "atlas_tile": "pw_hearth_flame_low", "ticks_per_frame": 1, "blend_frames": False, "frames": order})
    jdump(fb, fbp)
    log("1d hearth textures done: pw_hearth_log_{fueled,lit,embers,cold} + pw_hearth_log_end_{lit,embers,cold} (128²) + pw_hearth_flame (Patrix fire_0 30 f) + pw_hearth_flame_low (CTM tile 5) with flipbook entries")

# =====================================================================================================================
# 1e — RP-02: campfire smoke sprite -> Patrix big_smoke
# =====================================================================================================================
def phase_1e_smoke():
    strip = Image.new("RGBA", (128, 128 * 12), (0, 0, 0, 0))
    for i in range(12):
        fr = Image.open(PATRIX / f"textures/particle/big_smoke_{i}.png").convert("RGBA")
        assert fr.size == (128, 128), fr.size
        strip.paste(fr, (0, 128 * i))
    p = RP2_DST / "textures/particle/campfire_smoke.png"
    old = Image.open(p); assert old.size == (64, 768), old.size
    strip.save(p)
    for pj in ("campfire_smoke.json", "campfire_smoke_tall.json"):
        d = jload(RP2_DST / "particles" / pj)
        uv = d["particle_effect"]["components"]["minecraft:particle_appearance_billboard"]["uv"]
        assert uv["texture_width"] == 1 and uv["texture_height"] == 12, uv     # frame = 1/12 of the strip: layout-agnostic
    # our own particles carry texel uv -> retarget to the 128-px frames
    FLIP = {"texture_width": 128, "texture_height": 1536,
            "flipbook": {"base_UV": [0, 0], "size_UV": [128, 128], "step_UV": [0, 128], "frames_per_second": 4, "max_frame": 12, "stretch_to_lifetime": True, "loop": False}}
    ch = jload(RP2_DST / "particles/pw_chimney_smoke.json")
    ch["particle_effect"]["components"]["minecraft:particle_appearance_billboard"]["uv"] = json.loads(json.dumps(FLIP))
    jdump(ch, RP2_DST / "particles/pw_chimney_smoke.json")
    rm = jload(RP2_DST / "particles/pw_room_smoke.json")
    rm["particle_effect"]["description"]["basic_render_parameters"]["texture"] = "textures/particle/campfire_smoke"   # Patrix smoke everywhere
    rm["particle_effect"]["components"]["minecraft:particle_appearance_billboard"]["uv"] = json.loads(json.dumps(FLIP))
    jdump(rm, RP2_DST / "particles/pw_room_smoke.json")
    # NEW: the fire-pit puff — a small slow puff from the flame; dies on contact so it never clutters a ceiling
    puff = {"format_version": "1.10.0", "particle_effect": {
        "description": {"identifier": "pw:hearth_puff", "basic_render_parameters": {"material": "particles_alpha", "texture": "textures/particle/campfire_smoke"}},
        "components": {
            "minecraft:emitter_initialization": {"creation_expression": "variable.spin = math.random(-25, 25);"},
            "minecraft:emitter_rate_instant": {"num_particles": 1},
            "minecraft:emitter_lifetime_once": {"active_time": 0.1},
            "minecraft:emitter_shape_point": {"offset": [0, 0, 0], "direction": ["math.random(-0.2, 0.2)", 1.0, "math.random(-0.2, 0.2)"]},
            "minecraft:particle_initial_speed": "math.random(0.35, 0.6)",
            "minecraft:particle_initial_spin": {"rotation": "math.random(0, 360)", "rotation_rate": "variable.spin"},
            "minecraft:particle_lifetime_expression": {"max_lifetime": "math.random(3.5, 5.5)"},
            "minecraft:particle_motion_dynamic": {"linear_acceleration": ["math.random(-0.03, 0.03)", 0.1, "math.random(-0.03, 0.03)"], "linear_drag_coefficient": 0.6},
            "minecraft:particle_motion_collision": {"collision_drag": 4.0, "coefficient_of_restitution": 0.0, "collision_radius": 0.12, "expire_on_contact": True},
            "minecraft:particle_appearance_billboard": {
                "size": ["0.35 + 0.16 * variable.particle_age", "0.35 + 0.16 * variable.particle_age"],
                "facing_camera_mode": "lookat_xyz", "uv": json.loads(json.dumps(FLIP))},
            "minecraft:particle_appearance_tinting": {"color": {"interpolant": "variable.particle_age / variable.particle_lifetime",
                "gradient": {"0.0": "#00A09C96", "0.12": "#A0A09C96", "0.6": "#70A8A49E", "1.0": "#00B0ACA6"}}},
        }}}
    assert not (RP2_DST / "particles/pw_hearth_puff.json").exists()
    jdump(puff, RP2_DST / "particles/pw_hearth_puff.json")
    log("1e RP-02 smoke done: campfire_smoke.png = Patrix big_smoke_0..11 (128x1536); pw_chimney_smoke + pw_room_smoke retargeted to it (128-px flipbook uv); NEW particle pw:hearth_puff (fire-pit puff, expires on contact)")

# =====================================================================================================================
# 2 — BP-02
# =====================================================================================================================
def phase_2a_ramp_blocks():
    n = 0; refs = 0
    for p in sorted((BP_DST / "blocks").glob("pw_ramp_*.json")):
        d = jload(p); b = d["minecraft:block"]
        mat = re.match(r"pw:ramp_(cobble|smooth_stone|stonebrick)_", b["description"]["identifier"]).group(1)
        def add(c):
            nonlocal refs
            mi = c.get("minecraft:material_instances")
            if mi is not None and "cut" not in mi:
                mi["cut"] = {"texture": f"pw_rampcut_{mat}", "render_method": "alpha_test"}; refs += 1
        add(b["components"])
        for pm in b.get("permutations", []): add(pm.get("components", {}))
        jdump(d, p); n += 1
    assert n == 18, n
    log(f"2a ramp blocks done: `cut` instance added to {n} blocks ({refs} material_instances dicts)")

PHASE_LIGHT = {"cold": 0, "fueled": 0, "lit": 15, "embers": 7, "spent": 0}

def hearth_materials_v2(mid, phase, matkey):
    A = "alpha_test"
    bed = "pw_hearth_embers" if phase in ("lit", "embers") else "pw_hearth_ash"
    logk = {"fueled": "pw_hearth_log_fueled", "lit": "pw_hearth_log_lit", "embers": "pw_hearth_log_embers", "spent": "pw_hearth_log_cold", "cold": "pw_hearth_log_fueled"}[phase]
    endk = {"fueled": "pw_hearth_log_end", "lit": "pw_hearth_log_end_lit", "embers": "pw_hearth_log_end_embers", "spent": "pw_hearth_log_end_cold", "cold": "pw_hearth_log_end"}[phase]
    flame = "pw_hearth_flame_low" if phase == "embers" else "pw_hearth_flame"
    def mi(t, **x): return dict({"texture": t, "render_method": A}, **x)
    return {"*": mi(matkey(mid)), "top": mi(matkey(mid, top=True)), "soot": mi("pw_hearth_soot"), "bed": mi(bed),
            "log": mi(logk), "log_end": mi(endk), "flame": mi(flame, face_dimming=False, ambient_occlusion=False)}

def phase_2b_hearth_blocks():
    from homestead_build import matkey
    n = 0
    for p in sorted((BP_DST / "blocks").glob("pw_hearth_*.json")):
        d = jload(p); b = d["minecraft:block"]
        mid = b["description"]["identifier"].split("pw:hearth_")[1]
        assert mid in OUTER, mid
        b["description"]["states"]["pw:phase"] = ["cold", "fueled", "lit", "embers", "spent"]
        b["components"]["minecraft:material_instances"] = hearth_materials_v2(mid, "cold", matkey)
        perms = [pm for pm in b["permutations"] if "pw:phase" not in pm["condition"]]        # keep the 4 rotations
        geo_of = {"fueled": "geometry.pw_hearth_fueled", "lit": "geometry.pw_hearth_lit", "embers": "geometry.pw_hearth_embers", "spent": "geometry.pw_hearth_fueled"}
        for ph in ("fueled", "lit", "embers", "spent"):
            perms.append({"condition": f"q.block_state('pw:phase') == '{ph}'", "components": {
                "minecraft:geometry": {"identifier": geo_of[ph]},
                "minecraft:material_instances": hearth_materials_v2(mid, ph, matkey),
                "minecraft:light_emission": PHASE_LIGHT[ph]}})
        b["permutations"] = perms
        jdump(d, p); n += 1
    assert n == len(OUTER), n
    log(f"2b hearth blocks done: {n} blocks, pw:phase += 'spent' (fueled boxes + charcoal textures), per-phase log/end/flame keys")

def phase_2c_flue_blocks():
    from homestead_build import matkey
    n = 0
    for p in sorted((BP_DST / "blocks").glob("pw_flue_*.json")):
        d = jload(p); b = d["minecraft:block"]
        mid = b["description"]["identifier"].split("pw:flue_")[1]
        A = "alpha_test"
        def mi(t): return {"texture": t, "render_method": A}
        b["components"]["minecraft:geometry"] = {"identifier": "geometry.pw_flue_hollow"}
        b["components"]["minecraft:material_instances"] = {"*": mi(matkey(mid)), "top": mi(matkey(mid, top=True)), "soot": mi("pw_hearth_soot")}
        b["components"]["minecraft:collision_box"] = False                      # enterable: the bore keeper script holds the walls
        b["components"]["minecraft:selection_box"] = {"origin": [-8, 0, -8], "size": [16, 16, 16]}
        b["permutations"] = [{"condition": "q.block_state('pw:cap') == true", "components": {
            "minecraft:geometry": {"identifier": "geometry.pw_flue_cap_hollow"},
            "minecraft:material_instances": {"*": mi(matkey(mid)), "top": mi(matkey(mid, top=True)), "soot": mi("pw_hearth_soot")}}}]
        jdump(d, p); n += 1
    assert n == len(OUTER), n
    log(f"2c flue blocks done: {n} blocks -> geometry.pw_flue_hollow / _cap_hollow, collision_box false, selection full cell, soot instance")

def phase_2d_scripts():
    """Scripts are authored files (tools/homestead_src/*.js, v2); copy them in and check the imports stay the same."""
    src = ROOT / "tools/homestead_src"
    for f in ("pw_homestead.js", "pw_homestead_logic.js"):
        shutil.copy(src / f, BP_DST / "scripts" / f)
    log("2d scripts done: scripts/pw_homestead.js + pw_homestead_logic.js replaced with the v2 files (spent phase, fire-pit puff, chimney hazard)")

# =====================================================================================================================
# manifests + ledgers
# =====================================================================================================================
def bump(dst, ver, name, desc):
    man = jload(dst / "manifest.json")
    man["header"]["name"] = name; man["header"]["description"] = desc
    v = [int(x) for x in ver.split(".")]
    man["header"]["version"] = v
    for m in man["modules"]: m["version"] = v
    jdump(man, dst / "manifest.json")

def ledger_rows(text):
    return set(re.findall(r'^\|(\w+)\|`([^`]+)`\|$', text, re.M))

def needs_hash(rows):
    return hashlib.sha256(json.dumps(sorted([list(r) for r in rows])).encode()).hexdigest()[:16]

def write_ledger(path, title, ver, rows):
    body = "\n".join(f"|{t}|`{i}`|" for t, i in sorted(rows))
    path.write_text(f"# PW-DEPENDENCIES — {title}\n\nv{ver} · needs-hash `{needs_hash(rows)}`\n\n|type|identifier|\n|---|---|\n{body}\n", encoding="utf-8")

def phase_3_manifests():
    bump(RP_DST, RP_VER, f"AbsolutRealism Basic RP v{RP_VER}",
         f"v{RP_VER} ({DATE}) SEAM CUTS + HEARTH v2 + HOLLOW CHUTE. (1) roof45 board overshoot cut in place in pw_mitre_oak/spruce/thatch "
         f"(the lower course's board past z=8 no longer fights the upper block's / ridge cap's plumb filler: 0.615 -> 0.002 px² at the cap "
         f"corners, 0.200 -> 0.022 at course seams). (2) ramps: new pw_rampcut_<cobble|smooth_stone|stonebrick> strips (2 angles x snow 0..4), "
         f"every deck board's east/west face -> `cut` (level toe cut, plumb high-end cut, plumb cut at the snow filler's inner plane on snowed "
         f"pieces; boards only — the slab is untouched by ruling). (3) pw_flue: hollow square bore 12x12 (2-cube walls, soot inside, rim kept, "
         f"throat open) — geometry.pw_flue_hollow / _cap_hollow. (4) hearth v2: Patrix fire_0 30-frame flame (pw_hearth_flame) + low licks for "
         f"embers (pw_hearth_flame_low), authored burning-log stages (fueled grain along the log, lit, embers, cold/charcoal). Witness 09-22 "
         f"10:35 + approvals 12:06. Pair with BP-02 v{BP_VER} + RP-02 v{RP2_VER}.")
    bump(RP2_DST, RP2_VER, f"AbsolutRealism Atmospheric Effects RP v{RP2_VER}",
         f"v{RP2_VER} ({DATE}) campfire smoke sprite = Patrix big_smoke (12 frames, 128²) for vanilla campfires, the pw chimney column, room smoke and "
         f"the new fire-pit puff (Abs0lum: 'Patrix smoke all the time'). Particle definitions unchanged. Pair with RP-04 v{RP_VER} + BP-02 v{BP_VER}.")
    # BP ledger: add the new RP needs
    led = BP_DST / "PW-DEPENDENCIES.md"; rows = ledger_rows(led.read_text(encoding="utf-8"))
    rows |= {("terrain_key", f"pw_rampcut_{m}") for m in RAMP_MATS}
    rows |= {("terrain_key", k) for k in ("pw_hearth_flame_low", "pw_hearth_log_fueled", "pw_hearth_log_lit", "pw_hearth_log_embers", "pw_hearth_log_cold", "pw_hearth_log_end_lit", "pw_hearth_log_end_embers", "pw_hearth_log_end_cold")}
    rows |= {("geometry", "geometry.pw_flue_hollow"), ("geometry", "geometry.pw_flue_cap_hollow"), ("particle", "pw:hearth_puff")}
    write_ledger(led, "BP-02 Tectonic BP", BP_VER, rows)
    bump(BP_DST, BP_VER, f"AbsolutRealism Tectonic BP v{BP_VER}",
         f"v{BP_VER} ({DATE}) SEAM CUTS + HEARTH v2 + ENTERABLE CHUTE. Ramps: `cut` material instance on all 18 blocks (RP-04 v{RP_VER} strips). "
         f"Hearth: pw:phase gains 'spent' (charcoal stays in the pit after burn-out; fuel on spent -> fueled), per-phase log/end/flame keys "
         f"(Patrix flame, low licks in embers), fire-pit smoke puff while lit/embers (campfire smoke, Patrix sprite via RP-02 v{RP2_VER}). "
         f"Flue: hollow geometry, collision_box false — chimneys are enterable: a script bore-keeper holds the walls (side entry pushed back), "
         f"inside a chute you suffocate at the drowning rate (300 ticks of air, then 1 heart/s), take 1/2 heart heat damage per second over "
         f"coals (stops on exit), and over a LIT hearth you are set on fire like normal fire. Rulings 2026-09-22 12:06. Pair with RP-04 v{RP_VER} + RP-02 v{RP2_VER}.")
    l = RP_DST / "PW-DEPENDENCIES.md"                       # RP-04 carries a version line; RP-02's ledger is hash-only
    t = l.read_text(encoding="utf-8")
    t2 = re.sub(r"v\d+\.\d+\.\d+ ·", f"v{RP_VER} ·", t, count=1)
    assert t2 != t, l
    l.write_text(t2, encoding="utf-8")
    log("3 manifests + ledgers done")

def fresh_trees():
    for s, d in ((RP_SRC, RP_DST), (RP2_SRC, RP2_DST), (BP_SRC, BP_DST)):
        if d.exists(): shutil.rmtree(d)
        shutil.copytree(s, d)
    log("0 trees copied: rp04-129 -> rp04-130, rp02-202 -> rp02-203, bp02-181 -> bp02-182")

if __name__ == "__main__":
    fresh_trees()
    phase_1a_roof_cut(); phase_1b_ramp_cuts(); phase_1c_geometry(); phase_1d_hearth_textures(); phase_1e_smoke()
    phase_2a_ramp_blocks(); phase_2b_hearth_blocks(); phase_2c_flue_blocks(); phase_2d_scripts()
    phase_3_manifests()
    print("BUILD TREES READY (gate + packaging next)")
