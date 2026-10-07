#!/usr/bin/env python3
"""build_embers.py — HEARTH EMBERS E1 + E2 + E3 (D-C258; Abs0lum 18:17 09-27 "Embers pick - can we do all three? If yes, then all 3").

Witness (16:28): "I didn't see embers in the fire, I only saw the fire itself." Investigation D-C256: the files render as
written — the ember bed is a 1-cube dark strip under the logs (3.5 % of the hearth's pixels), the ember-phase logs have no
bright texel, nothing sparks. Three corrections, three complete packs:

  E1  RP-04 v1.3.139  models/blocks/pw_homestead.geo.json — every hearth phase: the bed becomes a 14x2x10 COAL BED (x -7..7,
      y 1..3, z -6..4), the logs lift 1 cube, the flame cross starts 1 cube higher; textures/blocks/pw_hearth_embers.png (+ _mers)
      = GLOWING COALS authored from the Patrix Java magma (porting permitted) with our ember ramp, emissive on the hot cells.
      Same material key 'bed' -> BP-02's block files are untouched by E1.
  E2  RP-04 v1.3.139  texture sets for pw_hearth_log_lit / _log_end_lit / _log_embers / _log_end_embers: MERS with the
      orange crack network EMISSIVE (Vibrant Visuals makes the cracks glow; without VV nothing changes).
  E3  RP-02 v2.0.5    particles/pw_ember.json + textures/particle/pw_ember.png — tiny additive sparks that rise, drift and
      fade (expire on contact, so a ceiling stops them);
      BP-02 v1.3.188  scripts/pw_homestead.js — the fire-pit puff cycle also spawns sparks: lit ~45 % of cycles, embers 1 in 6;
      scripts/main.js PW_BUILD 1.3.188; manifests stamped.
Everything else in the three packs is byte-identical to RP-04 .138 / RP-02 2.0.4 / BP-02 .187 (the gate asserts the diff).
"""
import json, shutil, datetime, hashlib, re
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path("/home/claude"); DATE = "2026-09-27"
RP4_SRC, RP4_DST, RP4_VER = ROOT / "_build/rp04-138", ROOT / "_build/rp04-139", "1.3.139"
RP2_SRC, RP2_DST, RP2_VER = ROOT / "_build/rp02-204", ROOT / "_build/rp02-205", "2.0.5"
BP2_SRC, BP2_DST, BP2_VER = ROOT / "_build/bp02-187", ROOT / "_build/bp02-188", "1.3.188"
MAGMA = ROOT / "_intake/patrix128/assets/minecraft/textures/block/magma.png"
DESIGN = ROOT / "_design/hearth-embers"; DESIGN.mkdir(parents=True, exist_ok=True)


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{datetime.datetime.now().strftime('%H:%M')} CT 09-27] BUILD EMBERS — {m}\n")


def jload(p): return json.loads(re.sub(r"^\s*//.*$", "", Path(p).read_text(encoding="utf-8-sig"), flags=re.M))
def jdump(o, p): Path(p).write_text(json.dumps(o, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
def sub(text, old, new, label):
    n = text.count(old); assert n == 1, f"{label}: expected exactly 1 match, found {n}"; return text.replace(old, new)
def save_rgba(a, p): Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), "RGBA").save(p)


# ----------------------------------------------------------------------------------------------------------- E1 geometry
BED_ORIGIN, BED_SIZE = [-7, 1, -6], [14, 2, 10]
def bed_uv():
    w, h, d = BED_SIZE
    return {"up": {"uv": [0, 0], "uv_size": [w, d], "material_instance": "bed"}, "north": {"uv": [0, 0], "uv_size": [w, h], "material_instance": "bed"},
            "south": {"uv": [0, 0], "uv_size": [w, h], "material_instance": "bed"}, "east": {"uv": [0, 0], "uv_size": [d, h], "material_instance": "bed"},
            "west": {"uv": [0, 0], "uv_size": [d, h], "material_instance": "bed"}}


def raise_hearth(geo):
    """E1 on one hearth geometry: coal bed 14x2x10, logs +1, flames +1 (origin + pivot)."""
    touched = {"bed": 0, "logs": 0, "flames": 0}
    for b in geo["bones"]:
        if b["name"] == "bed":
            c = b["cubes"][0]; c["origin"] = list(BED_ORIGIN); c["size"] = list(BED_SIZE); c["uv"] = bed_uv(); touched["bed"] += 1
        elif b["name"] == "logs":
            for c in b["cubes"]: c["origin"][1] += 1; touched["logs"] += 1
        elif b["name"] == "flames":
            for c in b["cubes"]: c["origin"][1] += 1; c["pivot"][1] += 1; touched["flames"] += 1
    return touched


# ----------------------------------------------------------------------------------------------------------- textures
def coal_texture():
    """pw_hearth_embers v2: glowing coals — Patrix magma cells pushed toward yellow-white, dark crust kept; returns (rgba, mers)."""
    mag = np.asarray(Image.open(MAGMA).convert("RGBA")).astype(np.float32) / 255
    lum = 0.3 * mag[..., 0] + 0.59 * mag[..., 1] + 0.11 * mag[..., 2]
    glow = np.clip((lum - 0.25) / 0.5, 0, 1) ** 1.2                      # 0 on the crust, 1 in the hot cells
    coal = mag.copy()
    coal[..., :3] = mag[..., :3] * (1 - glow[..., None]) + np.array([1.0, 0.78, 0.30]) * glow[..., None] + mag[..., :3] * glow[..., None] * 0.15
    coal[..., 3] = 1.0
    # MERS (1.21.30, metalness_emissive_roughness_subsurface): R metal 0 · G emissive = glow · B roughness 210 crust / 120 hot · A subsurface 0
    mers = np.zeros_like(mag); mers[..., 1] = glow; mers[..., 2] = (210 - 90 * glow) / 255; mers[..., 3] = 0
    return np.clip(coal, 0, 1), mers


def crack_mers(rgba):
    """E2: emissive where the log texture carries the orange ember cracks (hue 10..45 deg, saturated, not dark)."""
    a = rgba[..., :3]
    mx, mn = a.max(-1), a.min(-1); sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0); val = mx
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    # hue for the orange band: red dominant, green between 0.25 r and 0.75 r, blue low
    orange = (r > 0.45) & (g > 0.18 * r) & (g < 0.78 * r) & (b < 0.55 * g + 0.05) & (sat > 0.45)
    emis = np.where(orange, np.clip((val - 0.3) / 0.6, 0.35, 1.0), 0.0).astype(np.float32)
    mers = np.zeros_like(rgba); mers[..., 1] = emis; mers[..., 2] = (215 - 95 * emis) / 255; mers[..., 3] = 0
    return mers, float(orange.mean())


def texture_set(name):
    return {"format_version": "1.21.30", "minecraft:texture_set": {"color": name, "metalness_emissive_roughness_subsurface": f"{name}_mers"}}


def build_rp04():
    if RP4_DST.exists(): shutil.rmtree(RP4_DST)
    shutil.copytree(RP4_SRC, RP4_DST)
    # E1 geometry
    gp = RP4_DST / "models/blocks/pw_homestead.geo.json"; d = jload(gp)
    done = {}
    for g in d["minecraft:geometry"]:
        ident = g["description"]["identifier"]
        if ident.startswith("geometry.pw_hearth_"): done[ident] = raise_hearth(g)
    assert set(done) == {"geometry.pw_hearth_cold", "geometry.pw_hearth_fueled", "geometry.pw_hearth_lit", "geometry.pw_hearth_embers"}, done
    assert all(t["bed"] == 1 for t in done.values()) and done["geometry.pw_hearth_lit"]["flames"] == 2 and done["geometry.pw_hearth_lit"]["logs"] == 4, done
    jdump(d, gp)
    # E1 coal texture (same key)
    coal, mers = coal_texture()
    save_rgba(coal, RP4_DST / "textures/blocks/pw_hearth_embers.png"); save_rgba(mers, RP4_DST / "textures/blocks/pw_hearth_embers_mers.png")
    # E2 crack emissive texture sets
    tl = jload(RP4_DST / "textures/textures_list.json"); added = []
    stats = {}
    for name in ("pw_hearth_log_lit", "pw_hearth_log_end_lit", "pw_hearth_log_embers", "pw_hearth_log_end_embers"):
        rgba = np.asarray(Image.open(RP4_DST / f"textures/blocks/{name}.png").convert("RGBA")).astype(np.float32) / 255
        m, frac = crack_mers(rgba); stats[name] = round(frac, 4)
        save_rgba(m, RP4_DST / f"textures/blocks/{name}_mers.png"); jdump(texture_set(name), RP4_DST / f"textures/blocks/{name}.texture_set.json")
        for k in (f"textures/blocks/{name}_mers",):
            if k not in tl: tl.append(k); added.append(k)
    jdump(sorted(tl) if tl == sorted(tl) else tl, RP4_DST / "textures/textures_list.json")
    # manifest + ledger
    man = jload(RP4_DST / "manifest.json"); v = [int(x) for x in RP4_VER.split(".")]
    man["header"]["name"] = f"AbsolutRealism Basic RP v{RP4_VER}"; man["header"]["version"] = v
    for mod in man["modules"]: mod["version"] = v
    man["header"]["description"] = (f"v{RP4_VER} ({DATE}) HEARTH EMBERS (witness 16:28 'I only saw the fire itself'): E1 the ember bed is now a 14x2x10 GLOWING COAL BED "
                                    "(Patrix-magma coals, emissive) in every hearth phase, logs lifted 1 cube, flames start 1 cube higher; E2 the lit / ember log cracks are "
                                    "emissive under Vibrant Visuals (4 new texture sets). Same material keys - pairs with BP-02 v1.3.187+ unchanged; RP-02 v2.0.5 + BP-02 v1.3.188 add the sparks (E3). "
                                    "Everything else byte-identical to v1.3.138.")
    jdump(man, RP4_DST / "manifest.json")
    led = RP4_DST / "PW-DEPENDENCIES.md"; led.write_text(led.read_text(encoding="utf-8").replace("v1.3.138 ·", f"v{RP4_VER} ·", 1), encoding="utf-8")
    log(f"RP-04 v{RP4_VER}: 4 hearth geometries raised (bed 14x2x10, logs +1, flames +1); coal texture + MERS; E2 texture sets {stats}; textures_list +{len(added)}; manifest stamped")


# ----------------------------------------------------------------------------------------------------------- E3 particle
def ember_particle():
    return {"format_version": "1.10.0", "particle_effect": {
        "description": {"identifier": "pw:ember", "basic_render_parameters": {"material": "particles_add", "texture": "textures/particle/pw_ember"}},
        "components": {
            "minecraft:emitter_initialization": {"creation_expression": "variable.gust = math.random(-0.5, 0.5);"},
            "minecraft:emitter_rate_instant": {"num_particles": 2},
            "minecraft:emitter_lifetime_once": {"active_time": 0.1},
            "minecraft:emitter_shape_point": {"offset": [0, 0, 0], "direction": ["math.random(-0.35, 0.35)", 1.0, "math.random(-0.35, 0.35)"]},
            "minecraft:particle_initial_speed": "math.random(0.7, 1.4)",
            "minecraft:particle_lifetime_expression": {"max_lifetime": "math.random(1.2, 2.6)"},
            "minecraft:particle_motion_dynamic": {"linear_acceleration": ["variable.gust", 0.7, "variable.gust * 0.5"], "linear_drag_coefficient": 1.1},
            "minecraft:particle_motion_collision": {"collision_drag": 10.0, "coefficient_of_restitution": 0.0, "collision_radius": 0.02, "expire_on_contact": True},
            "minecraft:particle_appearance_billboard": {
                "size": ["0.05 * (1.0 - 0.6 * variable.particle_age / variable.particle_lifetime) * (0.85 + 0.15 * math.sin(variable.particle_age * 900))",
                         "0.05 * (1.0 - 0.6 * variable.particle_age / variable.particle_lifetime) * (0.85 + 0.15 * math.sin(variable.particle_age * 900))"],
                "facing_camera_mode": "lookat_xyz", "uv": {"texture_width": 16, "texture_height": 16, "uv": [0, 0], "uv_size": [16, 16]}},
            "minecraft:particle_appearance_tinting": {"color": {"interpolant": "variable.particle_age / variable.particle_lifetime",
                                                                "gradient": {"0.0": "#FFFFF2C0", "0.3": "#FFFFC050", "0.7": "#FFFF6A20", "1.0": "#00B02A00"}}}}}}


def ember_texture(path):
    """16x16 soft spark: white core, warm halo, transparent edge (additive material -> glows)."""
    y, x = np.mgrid[0:16, 0:16]; r = np.sqrt((x - 7.5) ** 2 + (y - 7.5) ** 2) / 7.5
    core = np.clip(1 - r / 0.35, 0, 1); halo = np.clip(1 - r, 0, 1) ** 2
    a = np.zeros((16, 16, 4), np.float32)
    a[..., 0] = np.clip(core + halo * 1.0, 0, 1); a[..., 1] = np.clip(core + halo * 0.62, 0, 1); a[..., 2] = np.clip(core * 0.9 + halo * 0.2, 0, 1)
    a[..., 3] = np.clip(core + halo * 0.9, 0, 1)
    save_rgba(a, path)


def build_rp02():
    if RP2_DST.exists(): shutil.rmtree(RP2_DST)
    shutil.copytree(RP2_SRC, RP2_DST)
    jdump(ember_particle(), RP2_DST / "particles/pw_ember.json")
    ember_texture(RP2_DST / "textures/particle/pw_ember.png")
    man = jload(RP2_DST / "manifest.json"); v = [int(x) for x in RP2_VER.split(".")]
    man["header"]["name"] = f"AbsolutRealism Atmospheric Effects RP v{RP2_VER}"; man["header"]["version"] = v
    for mod in man["modules"]: mod["version"] = v
    man["header"]["description"] = (f"v{RP2_VER} ({DATE}) HEARTH EMBERS E3: particle pw:ember (tiny additive sparks that rise, drift and fade; expire on contact) + its "
                                    "16x16 texture, spawned by BP-02 v1.3.188 from lit / ember hearths. Everything else byte-identical to v2.0.4.")
    jdump(man, RP2_DST / "manifest.json")
    log(f"RP-02 v{RP2_VER}: particles/pw_ember.json + textures/particle/pw_ember.png; manifest stamped")


def build_bp02():
    if BP2_DST.exists(): shutil.rmtree(BP2_DST)
    shutil.copytree(BP2_SRC, BP2_DST)
    p = BP2_DST / "scripts/pw_homestead.js"; s = p.read_text(encoding="utf-8")
    s = sub(s, "// pw_homestead.js — HOMESTEAD family runtime (BP-02 v1.3.182; room wall test fixed in v1.3.185; room FOG off + stuck-fog sweep in v1.3.187): hearth · flue · dual wall · rafter.",
            "// pw_homestead.js — HOMESTEAD family runtime (BP-02 v1.3.182; room wall test fixed in v1.3.185; room FOG off + stuck-fog sweep in v1.3.187; ember SPARKS in v1.3.188): hearth · flue · dual wall · rafter.", "header")
    s = sub(s, 'const PUFF_ID = "pw:hearth_puff";\n',
            'const PUFF_ID = "pw:hearth_puff";\n'
            'const EMBER_ID = "pw:ember";        // v1.3.188 (D-C258, E3): sparks from the fire pit — RP-02 v2.0.5 particle; lit ~45 % of puff cycles, embers 1 in 6\n'
            'const EMBER_LIT = 0.45, EMBER_EMBERS_EVERY = 6;\n', "ember constants")
    s = sub(s, "    try { dim.spawnParticle(PUFF_ID, loc); } catch { /* particle pack missing: silent */ }\n  }\n}\n",
            "    try { dim.spawnParticle(PUFF_ID, loc); } catch { /* particle pack missing: silent */ }\n  }\n  emberCycle();\n}\n"
            "/** E3 (v1.3.188): ember sparks rise from the coal bed of every lit / ember hearth a player is near. */\n"
            "function emberCycle() {\n"
            "  for (const [, t] of puffTargets) {\n"
            "    const want = t.phase === \"lit\" ? Math.random() < EMBER_LIT : (puffNo % EMBER_EMBERS_EVERY === 0);\n"
            "    if (!want) continue;\n"
            "    let dim; try { dim = world.getDimension(t.dimId); } catch { continue; }\n"
            "    const loc = { x: t.x + 0.5 + (Math.random() - 0.5) * 0.45, y: t.y + 0.2 + Math.random() * 0.25, z: t.z + 0.5 + (Math.random() - 0.5) * 0.45 };\n"
            "    try { dim.spawnParticle(EMBER_ID, loc); } catch { /* particle pack missing: silent */ }\n"
            "  }\n"
            "}\n", "ember cycle")
    p.write_text(s, encoding="utf-8")
    m = BP2_DST / "scripts/main.js"; t = m.read_text(encoding="utf-8")
    t = sub(t, 'const PW_BUILD = "1.3.187";', 'const PW_BUILD = "1.3.188";', "PW_BUILD"); m.write_text(t, encoding="utf-8")
    man = jload(BP2_DST / "manifest.json"); v = [int(x) for x in BP2_VER.split(".")]
    man["header"]["name"] = f"AbsolutRealism Tectonic BP v{BP2_VER}"; man["header"]["version"] = v
    for mod in man["modules"]: mod["version"] = v
    man["header"]["description"] = (f"v{BP2_VER} ({DATE}) HEARTH EMBERS E3: the fire-pit puff cycle also spawns pw:ember sparks (lit ~45 % of cycles, embers 1 in 6) from the coal bed "
                                    "of every lit / ember hearth a player is near — needs RP-02 v2.0.5 (the particle) and pairs with RP-04 v1.3.139 (coal bed). "
                                    "Everything else byte-identical to v1.3.187.")
    jdump(man, BP2_DST / "manifest.json")
    log(f"BP-02 v{BP2_VER}: pw_homestead.js emberCycle (EMBER_ID pw:ember) + main.js PW_BUILD + manifest stamped")


def main():
    build_rp04(); build_rp02(); build_bp02()


if __name__ == "__main__":
    main()
