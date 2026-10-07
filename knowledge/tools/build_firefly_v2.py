#!/usr/bin/env python3
"""build_firefly_v2.py — FIREFLY v2 (Abs0lum 23:47–23:5x: OURS v2 at 80% size, "GO — build now").

  RP-05 v1.3.49  (from _build/rp05-48)  the firefly bush = Patrix 256 bush + its animated firefly layer, wired the
      Bedrock way: terrain key "firefly_bush" = [textures/blocks/firefly_bush, textures/blocks/firefly_bush_firefly]
      (slot 0 bush, slot 1 fireflies), flipbook atlas_tile firefly_bush / atlas_index 1, 4 frames at 22 ticks,
      blended (Patrix .mcmeta: frametime 22, interpolate true). Dead weight removed: firefly_bush_v0 (128px, filled
      all three slots, so slot 1 drew the bush again) and the Java-named firefly_bush_emissive key/flipbook/png.
  RP-03 v1.3.60  (from _build/rp03-59)  texture sets for both layers, all layers pack-local (L-DEDUP-4):
      firefly_bush_mer re-converted by Lesson #156 (the old one was a raw copy of Patrix _s: smoothness read as
      metalness, porosity as roughness); new firefly_bush_firefly set (colour + MERS, 4 frames, emissive from the
      Patrix _s alpha); dead Java-named firefly_bush_emissive set (4 files) removed.
  RP-10 v1.3.40  (from _build/rp10-139) minecraft:firefly_particle (bush fireflies) and pw:firefly_ambient (BP-02's
      swamp fireflies) rewritten as OURS v2 FINAL: one firefly per emit, baked halo+core sprite
      textures/particle/pw_firefly_v2.png, billboard half-size 0.088 (x0.80), fullbright, particles_blend; flash
      rhythm = emitter state machine (dark 2–4 s, flash 0.5–1 s, 0.25 s rise, 0.5 s fade) — NO trig; drift =
      parametric Lissajous with trig arguments written in DEGREES per second; life 14–24 s with 1 s / 1.5 s fades.
Everything else byte-identical to the source packs. The variant bushes 2–4 are NOT used (P0: MCPE-126617)."""
import json, shutil, datetime, math
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path("/home/claude"); DATE = "2026-09-23"
PAT = ROOT / "_intake/patrix256-firefly/assets/minecraft/textures/block"
SRC = {"RP-05": ROOT / "_build/rp05-48", "RP-03": ROOT / "_build/rp03-59", "RP-10": ROOT / "_build/rp10-139"}
DST = {"RP-05": ROOT / "_build/rp05-49", "RP-03": ROOT / "_build/rp03-60", "RP-10": ROOT / "_build/rp10-140"}
VER = {"RP-05": "1.3.49", "RP-03": "1.3.60", "RP-10": "1.3.40"}
NAME = {"RP-05": "AbsolutRealism Flora RP", "RP-03": "AbsolutRealism PBR RP", "RP-10": "AbsolutRealism Terrain RP"}
DESC = {
    "RP-05": "v1.3.49 (2026-09-23) FIREFLY v2 — the firefly bush is the Patrix 256 bush with its animated firefly layer under "
             "Bedrock's names (slot 1 = textures/blocks/firefly_bush_firefly: 4 frames, 22 ticks, blended). Removed: the 128px "
             "firefly_bush_v0 that filled all three slots (slot 1 drew the bush again) and the Java-named firefly_bush_emissive "
             "key, flipbook and texture. Ships with RP-03 1.3.60 + RP-10 1.3.40.",
    "RP-03": "v1.3.60 (2026-09-23) FIREFLY v2 — firefly bush texture sets: bush MERS re-converted by Lesson #156 (was a raw copy "
             "of Patrix _s: smoothness read as metalness); new set for the firefly layer (colour + MERS, 4 frames, glow from the "
             "Patrix emissive map); the dead Java-named firefly_bush_emissive set removed. Ships with RP-05 1.3.49 + RP-10 1.3.40.",
    "RP-10": "v1.3.40 (2026-09-23) FIREFLY v2 — bush fireflies (minecraft:firefly_particle) and swamp fireflies "
             "(pw:firefly_ambient) redrawn as OURS v2 FINAL: one soft warm firefly with a white centre at 80% size "
             "(Abs0lum 23:47), a real flash rhythm (dark 2-4 s, flash 0.5-1 s), slow drift, trig in degrees. Ships with RP-05 "
             "1.3.49 + RP-03 1.3.60.",
}
FLY_TEX = "textures/particle/pw_firefly_v2"
HALF = 0.088                       # billboard half-extent (block) = 0.11 x 0.80
CORE_RATIO = 0.024 / 0.088         # core radius / halo radius (0.03 x 0.80 over 0.11 x 0.80)
WARM = (0.86, 1.0, 0.45); CREAM = (1.0, 1.0, 0.85); HALO_ALPHA = 0.7


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f:
        f.write(f"[{datetime.datetime.now().strftime('%H:%M')} CT 09-23] BUILD {m}\n")


def jload(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def jdump(o, p): Path(p).write_text(json.dumps(o, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def stamp(pack):
    p = DST[pack] / "manifest.json"; man = jload(p); vv = [int(x) for x in VER[pack].split(".")]
    man["header"]["name"] = f"{NAME[pack]} v{VER[pack]}"; man["header"]["version"] = vv; man["header"]["description"] = DESC[pack]
    for m in man["modules"]: m["version"] = vv
    jdump(man, p)


def fresh(pack):
    if DST[pack].exists(): shutil.rmtree(DST[pack])
    shutil.copytree(SRC[pack], DST[pack])


def rgba(path): return np.asarray(Image.open(path).convert("RGBA")).astype(np.int32)


def save_png(arr, path):
    Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA").save(path, optimize=True)


def mers_156(spec):
    """Lesson #156 (CONFIRMED v1.2.32) — LabPBR _s -> Bedrock MERS, per pixel:
    M = 255 if G >= 230 else 0 · E = A if A < 255 else 0 · R = 255 - R_lab · S = (B - 64) * 255 / 191 if B >= 65 else 0."""
    R, G, B, A = (spec[..., i] for i in range(4))
    out = np.zeros_like(spec)
    out[..., 0] = np.where(G >= 230, 255, 0)
    out[..., 1] = np.where(A < 255, A, 0)
    out[..., 2] = 255 - R
    out[..., 3] = np.where(B >= 65, np.round((B - 64) * 255 / 191), 0)
    return out


def bake_flyer(n=128):
    """One RGBA sprite that equals 'core OVER halo' of the approved simulation (firefly_compare model_prop at
    V2_SCALE): halo = soft disc (1 - r)^2.6 in WARM at alpha 0.7; core = max((1 - rc)^1.2, rc < 0.35) in CREAM,
    radius CORE_RATIO of the halo. Straight (non-premultiplied) alpha; transparent texels carry the halo colour so
    filtering never pulls a dark fringe."""
    yy, xx = np.mgrid[0:n, 0:n]
    r = np.hypot(xx - (n - 1) / 2, yy - (n - 1) / 2) / (n / 2)
    a_h = np.clip(1 - r, 0, 1) ** 2.6 * HALO_ALPHA
    rc = r / CORE_RATIO
    a_c = np.maximum(np.clip(1 - rc, 0, 1) ** 1.2, (rc < 0.35).astype(float))
    A = a_c + a_h * (1 - a_c)
    prem = np.array(CREAM)[None, None, :] * a_c[..., None] + np.array(WARM)[None, None, :] * (a_h * (1 - a_c))[..., None]
    rgb = np.where(A[..., None] > 1e-6, prem / np.maximum(A[..., None], 1e-6), np.array(WARM)[None, None, :])
    out = np.zeros((n, n, 4)); out[..., :3] = rgb * 255; out[..., 3] = A * 255
    return np.round(out).astype(np.int32)


# ---------------------------------------------------------------- the particle (both identifiers share it)
EMIT_CREATE = "v.fw_on = 0; v.fw_t0 = -10; v.fw_next = math.random(0.0, 3.0); v.fw_bright = 0;"
EMIT_UPDATE = ("v.fw_sw = v.emitter_age >= v.fw_next; "
               "v.fw_sw ? (v.fw_on = 1 - v.fw_on); "
               "v.fw_sw ? (v.fw_t0 = v.emitter_age); "
               "v.fw_sw ? (v.fw_next = v.emitter_age + (v.fw_on ? math.random(0.5, 1.0) : math.random(2.0, 4.0))); "
               "v.fw_bright = v.fw_on ? math.clamp((v.emitter_age - v.fw_t0) / 0.25, 0, 1) : math.clamp(1 - (v.emitter_age - v.fw_t0) / 0.5, 0, 1);")
# trig arguments are DEGREES: 23 deg/s = 0.40 rad/s, 61 deg/s = 1.06 rad/s ... (Molang math.sin takes degrees)
DRIFT = [
    "math.sin(v.particle_age * 23 + v.particle_random_1 * 360) * 0.40 + math.sin(v.particle_age * 61 + v.particle_random_3 * 360) * 0.12",
    "math.sin(v.particle_age * 19 + v.particle_random_2 * 360) * 0.14 + math.sin(v.particle_age * 47 + v.particle_random_4 * 360) * 0.05",
    "math.sin(v.particle_age * 17 + v.particle_random_4 * 360) * 0.40 + math.sin(v.particle_age * 53 + v.particle_random_1 * 360) * 0.12",
]
ALPHA = "v.fw_bright * math.clamp(math.min(v.particle_age / 1.0, (v.particle_lifetime - v.particle_age) / 1.5), 0.0, 1.0)"


def particle(identifier):
    return {
        "format_version": "1.10.0",
        "particle_effect": {
            "description": {"identifier": identifier,
                            "basic_render_parameters": {"material": "particles_blend", "texture": FLY_TEX}},
            "components": {
                "minecraft:emitter_initialization": {"creation_expression": EMIT_CREATE, "per_update_expression": EMIT_UPDATE},
                "minecraft:emitter_rate_instant": {"num_particles": 1},
                "minecraft:emitter_lifetime_once": {"active_time": 24.5},
                "minecraft:emitter_shape_point": {},
                "minecraft:particle_lifetime_expression": {"max_lifetime": "math.random(14.0, 24.0)"},
                "minecraft:particle_motion_parametric": {"relative_position": DRIFT},
                "minecraft:particle_appearance_billboard": {
                    "size": [HALF, HALF], "facing_camera_mode": "lookat_xyz",
                    "uv": {"texture_width": 128, "texture_height": 128, "uv": [0, 0], "uv_size": [128, 128]}},
                "minecraft:particle_appearance_tinting": {"color": ["1.0", "1.0", "1.0", ALPHA]},
            },
        },
    }


def build_rp05():
    fresh("RP-05"); B = DST["RP-05"]; blocks = B / "textures/blocks"
    save_png(rgba(PAT / "firefly_bush.png"), blocks / "firefly_bush.png")
    save_png(rgba(PAT / "firefly_bush_emissive.png"), blocks / "firefly_bush_firefly.png")
    for dead in ("firefly_bush_v0.png", "firefly_bush_emissive.png"):
        (blocks / dead).unlink()
    tt = jload(B / "textures/terrain_texture.json"); td = tt["texture_data"]
    td["firefly_bush"] = {"textures": ["textures/blocks/firefly_bush", "textures/blocks/firefly_bush_firefly"]}
    del td["firefly_bush_emissive"]
    jdump(tt, B / "textures/terrain_texture.json")
    fb = jload(B / "textures/flipbook_textures.json")
    before = len(fb)
    fb = [e for e in fb if e.get("atlas_tile") != "firefly_bush_emissive"]
    assert len(fb) == before - 1 and not any(e.get("atlas_tile") == "firefly_bush" for e in fb)
    fb.append({"flipbook_texture": "textures/blocks/firefly_bush_firefly", "atlas_tile": "firefly_bush", "atlas_index": 1,
               "ticks_per_frame": 22, "frames": [0, 1, 2, 3], "blend_frames": True})
    jdump(fb, B / "textures/flipbook_textures.json")
    tl = jload(B / "textures/textures_list.json")
    tl = [t for t in tl if t not in ("textures/blocks/firefly_bush_emissive", "textures/blocks/firefly_bush_v0")]
    tl += ["textures/blocks/firefly_bush", "textures/blocks/firefly_bush_firefly"]
    jdump(sorted(set(tl), key=tl.index), B / "textures/textures_list.json")
    stamp("RP-05"); log("RP-05 v1.3.49 built (_build/rp05-49)")


def build_rp03():
    fresh("RP-03"); B = DST["RP-03"]; blocks = B / "textures/blocks"
    shutil.copyfile(DST["RP-05"] / "textures/blocks/firefly_bush.png", blocks / "firefly_bush.png")            # same bytes as RP-05
    shutil.copyfile(DST["RP-05"] / "textures/blocks/firefly_bush_firefly.png", blocks / "firefly_bush_firefly.png")
    save_png(mers_156(rgba(PAT / "firefly_bush_s.png")), blocks / "firefly_bush_mer.png")
    save_png(mers_156(rgba(PAT / "firefly_bush_emissive_s.png")), blocks / "firefly_bush_firefly_mer.png")
    jdump({"format_version": "1.21.30", "minecraft:texture_set": {"color": "firefly_bush_firefly",
           "metalness_emissive_roughness_subsurface": "firefly_bush_firefly_mer"}}, blocks / "firefly_bush_firefly.texture_set.json")
    for dead in ("firefly_bush_emissive.png", "firefly_bush_emissive_mer.png", "firefly_bush_emissive_n.png", "firefly_bush_emissive.texture_set.json"):
        (blocks / dead).unlink()
    stamp("RP-03"); log("RP-03 v1.3.60 built (_build/rp03-60)")


def build_rp10():
    fresh("RP-10"); B = DST["RP-10"]
    save_png(bake_flyer(), B / (FLY_TEX + ".png"))
    jdump(particle("minecraft:firefly_particle"), B / "particles/firefly_particle.particle.json")
    jdump(particle("pw:firefly_ambient"), B / "particles/firefly_ambient.particle.json")
    tl_path = B / "textures/textures_list.json"
    if tl_path.exists():
        tl = jload(tl_path); tl.append(FLY_TEX); jdump(tl, tl_path)
    stamp("RP-10"); log("RP-10 v1.3.40 built (_build/rp10-140)")


if __name__ == "__main__":
    build_rp05(); build_rp03(); build_rp10()
