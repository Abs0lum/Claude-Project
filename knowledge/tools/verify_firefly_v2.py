#!/usr/bin/env python3
"""verify_firefly_v2.py — gate for FIREFLY v2 (RP-05 1.3.49 · RP-03 1.3.60 · RP-10 1.3.40). Packages on GATE OPEN.

  A  manifests: version, name, unique stamped description, uuids unchanged, pbr capability kept
  B  every JSON in the three built packs parses
  C  file-level diff vs the source packs == exactly the planned change list (nothing else moved)
  D  RP-05 wiring: 2-slot terrain key, one flipbook (atlas_tile firefly_bush, index 1, 22 ticks, blended), frames
     = image height / width = 4, every member pack-local, textures_list consistent, 256px cap
  E  RP-03 sets: layers pack-local (L-DEDUP-4), format 1.21.30 MERS, sizes match colour, MERS == Lesson #156
     recomputed from the Patrix _s, colour copies byte-identical to RP-05
  F  RP-10 particles: both ids, texture pack-local 128x128, half-size 0.088, particles_blend, fullbright (no
     lighting component), no trig in the brightness (fade/flash) expressions
  G  PREVIEW FROM THE SHIPPED JSON (tools/molang_eval.py, degrees): alpha reaches 1.0; the drift moves; flash
     rhythm, glow size and speed match the approved simulation (firefly_compare model_prop at V2_SCALE)
  H  suite-wide: no reference left to the removed names; nothing above RP-05 in the stack overrides the bush key,
     its flipbook, or the two particle ids (L-DEDUP-1 / stack census)
"""
import json, re, sys, hashlib, zipfile, math, random, statistics
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
import molang_eval as M
import firefly_compare as fc
import build_firefly_v2 as bf

ROOT = Path("/home/claude"); OUT = Path("/mnt/user-data/outputs")
PACKS = {"RP-05": ("RP-05-AbsolutRealism-Flora-RP-v1_3_49.mcpack",), "RP-03": ("RP-03-AbsolutRealism-PBR-RP-v1_3_60.mcpack",),
         "RP-10": ("RP-10-AbsolutRealism-Terrain-RP-v1_3_40.mcpack",)}
res = []
def check(name, ok, detail=""):
    res.append((name, bool(ok))); print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f" — {detail}" if detail else ""))
def jload(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def tree(d): return {str(p.relative_to(d)).replace("\\", "/"): md5(p) for p in Path(d).rglob("*") if p.is_file()}
def arr(p): return np.asarray(Image.open(p).convert("RGBA")).astype(np.int32)

# ---------------------------------------------------------------- A manifests
for k in PACKS:
    a, b = jload(bf.SRC[k] / "manifest.json"), jload(bf.DST[k] / "manifest.json"); v = [int(x) for x in bf.VER[k].split(".")]
    ok = (b["header"]["version"] == v and all(m["version"] == v for m in b["modules"]) and b["header"]["uuid"] == a["header"]["uuid"]
          and [m["uuid"] for m in b["modules"]] == [m["uuid"] for m in a["modules"]] and b.get("capabilities") == a.get("capabilities") == ["pbr"]
          and b["header"]["name"] == f"{bf.NAME[k]} v{bf.VER[k]}" and b["header"]["description"].startswith(f"v{bf.VER[k]} (2026-09-23) FIREFLY v2")
          and b["header"]["description"] != a["header"]["description"])
    check(f"A {k} manifest {bf.VER[k]}", ok, b["header"]["name"])

# ---------------------------------------------------------------- B JSON parse
for k in PACKS:
    bad = []
    for p in bf.DST[k].rglob("*.json"):
        try: jload(p)
        except Exception as e: bad.append((str(p), str(e)[:60]))
    check(f"B {k} every JSON parses", not bad, f"{len(list(bf.DST[k].rglob('*.json')))} files" + (f" BAD {bad[:3]}" if bad else ""))

# ---------------------------------------------------------------- C planned change list only
PLAN = {
    "RP-05": ({"textures/blocks/firefly_bush.png", "textures/blocks/firefly_bush_firefly.png"},
              {"textures/blocks/firefly_bush_v0.png", "textures/blocks/firefly_bush_emissive.png"},
              {"manifest.json", "textures/terrain_texture.json", "textures/flipbook_textures.json", "textures/textures_list.json"}),
    "RP-03": ({"textures/blocks/firefly_bush_firefly.png", "textures/blocks/firefly_bush_firefly_mer.png", "textures/blocks/firefly_bush_firefly.texture_set.json"},
              {"textures/blocks/firefly_bush_emissive.png", "textures/blocks/firefly_bush_emissive_mer.png", "textures/blocks/firefly_bush_emissive_n.png",
               "textures/blocks/firefly_bush_emissive.texture_set.json"},
              {"manifest.json", "textures/blocks/firefly_bush_mer.png", "textures/blocks/firefly_bush.png"}),
    "RP-10": ({"textures/particle/pw_firefly_v2.png"}, set(),
              {"manifest.json", "particles/firefly_particle.particle.json", "particles/firefly_ambient.particle.json"}),
}
for k in PACKS:
    A, B = tree(bf.SRC[k]), tree(bf.DST[k])
    added, removed = set(B) - set(A), set(A) - set(B); changed = {f for f in set(A) & set(B) if A[f] != B[f]}
    pa, pr, pc = PLAN[k]
    # RP-03's firefly_bush.png is rewritten with RP-05's bytes; allowed to be unchanged if the bytes happen to match
    required = pc - {"textures/blocks/firefly_bush.png"}      # RP-03's colour copy may keep identical bytes
    ok = added == pa and removed == pr and changed <= pc and required <= changed
    check(f"C {k} only the planned files moved", ok, f"+{len(added)} -{len(removed)} ~{len(changed)} of {len(B)} files")

# ---------------------------------------------------------------- D RP-05 wiring
R5 = bf.DST["RP-05"]
td = jload(R5 / "textures/terrain_texture.json")["texture_data"]
key = td.get("firefly_bush", {}).get("textures")
fb = [e for e in jload(R5 / "textures/flipbook_textures.json") if e.get("atlas_tile") in ("firefly_bush", "firefly_bush_emissive")]
ok = key == ["textures/blocks/firefly_bush", "textures/blocks/firefly_bush_firefly"] and "firefly_bush_emissive" not in td
check("D1 RP-05 terrain key firefly_bush = [bush, firefly layer]; Java key gone", ok, str(key))
e = fb[0] if len(fb) == 1 else {}
glow = arr(R5 / "textures/blocks/firefly_bush_firefly.png"); bush = arr(R5 / "textures/blocks/firefly_bush.png")
ok = (len(fb) == 1 and e.get("atlas_index") == 1 and e.get("ticks_per_frame") == 22 and e.get("blend_frames") is True
      and e.get("frames") == list(range(glow.shape[0] // glow.shape[1])) and glow.shape[0] // glow.shape[1] == 4 and glow.shape[0] % glow.shape[1] == 0
      and (R5 / (e.get("flipbook_texture", "x") + ".png")).exists())
check("D2 RP-05 one flipbook: atlas_tile firefly_bush / index 1 / 22 ticks / blended / 4 frames, source pack-local", ok, json.dumps(e))
check("D3 RP-05 sizes: bush 256x256, firefly layer 256x1024 (256px cap)", bush.shape[:2] == (256, 256) and glow.shape[:2] == (1024, 256))
pat_b, pat_g = arr(bf.PAT / "firefly_bush.png"), arr(bf.PAT / "firefly_bush_emissive.png")
check("D4 RP-05 pixels == Patrix 256 source (bush + emissive)", (bush == pat_b).all() and (glow == pat_g).all())
tl = jload(R5 / "textures/textures_list.json")
ok = all((R5 / (t + ".png")).exists() or (R5 / (t + ".tga")).exists() for t in tl if "firefly" in t) and not any(("_v0" in t or "emissive" in t) and "firefly" in t for t in tl) \
     and {"textures/blocks/firefly_bush", "textures/blocks/firefly_bush_firefly"} <= set(tl) and len(tl) == len(set(tl))
check("D5 RP-05 textures_list: firefly entries exist pack-locally, dead ones gone, no duplicates", ok, f"{len(tl)} entries")

# ---------------------------------------------------------------- E RP-03 sets
R3 = bf.DST["RP-03"] / "textures/blocks"
okall, notes = True, []
for stem in ("firefly_bush", "firefly_bush_firefly"):
    ts = jload(R3 / f"{stem}.texture_set.json"); s = ts["minecraft:texture_set"]
    layers = [s.get("color"), s.get("normal"), s.get("metalness_emissive_roughness_subsurface")]
    local = all((R3 / f"{l}.png").exists() for l in layers if isinstance(l, str))
    col = arr(R3 / f"{s['color']}.png"); mer = arr(R3 / f"{s['metalness_emissive_roughness_subsurface']}.png")
    same = col.shape == mer.shape and (not s.get("normal") or arr(R3 / f"{s['normal']}.png").shape[:2] == col.shape[:2])
    okall &= ts["format_version"] == "1.21.30" and local and same
    notes.append(f"{stem}: {[l for l in layers if l]} local={local} sizes={col.shape[:2]}")
check("E1 RP-03 both sets: format 1.21.30, every layer pack-local, layer sizes match", okall, " | ".join(notes))
exp1 = bf.mers_156(arr(bf.PAT / "firefly_bush_s.png")); exp2 = bf.mers_156(arr(bf.PAT / "firefly_bush_emissive_s.png"))
got1, got2 = arr(R3 / "firefly_bush_mer.png"), arr(R3 / "firefly_bush_firefly_mer.png")
check("E2 RP-03 MERS == Lesson #156 of the Patrix _s (both layers, every pixel)", (got1 == exp1).all() and (got2 == exp2).all(),
      f"bush M/E/R/S mean {got1[bush[..., 3] >= 128].mean(0).round(1).tolist()} · firefly E max {int(got2[..., 1].max())}")
check("E3 RP-03 colour copies byte-identical to RP-05's", md5(R3 / "firefly_bush.png") == md5(R5 / "textures/blocks/firefly_bush.png")
      and md5(R3 / "firefly_bush_firefly.png") == md5(R5 / "textures/blocks/firefly_bush_firefly.png"))
check("E4 RP-03 the Java-named emissive set is gone", not list(R3.glob("firefly_bush_emissive*")))

# ---------------------------------------------------------------- F RP-10 particles
R10 = bf.DST["RP-10"]
P = {}
for f in ("firefly_particle", "firefly_ambient"):
    P[f] = jload(R10 / f"particles/{f}.particle.json")["particle_effect"]
ids = {P[f]["description"]["identifier"] for f in P}
tex = P["firefly_particle"]["description"]["basic_render_parameters"]["texture"]
t_img = arr(R10 / (tex + ".png"))
c = P["firefly_particle"]["components"]
ok = (ids == {"minecraft:firefly_particle", "pw:firefly_ambient"} and all(P[f]["description"]["basic_render_parameters"] == {"material": "particles_blend", "texture": bf.FLY_TEX} for f in P)
      and t_img.shape == (128, 128, 4) and all("minecraft:particle_appearance_lighting" not in P[f]["components"] for f in P)
      and all(P[f]["components"]["minecraft:particle_appearance_billboard"]["size"] == [0.088, 0.088] for f in P)
      and P["firefly_particle"]["components"] == P["firefly_ambient"]["components"])
check("F1 RP-10 both ids, same look: particles_blend, pack-local 128px sprite, half-size 0.088, fullbright", ok, f"{sorted(ids)}")
bright = c["minecraft:emitter_initialization"]["per_update_expression"] + c["minecraft:particle_appearance_tinting"]["color"][3]
check("F2 RP-10 brightness expressions contain no trig (the degrees trap cannot reach the flash)", not re.search(r"math\.(sin|cos)", bright))
check("F3 RP-10 firefly_trail / firefly_emitter untouched", md5(R10 / "particles/firefly_trail.particle.json") == md5(bf.SRC["RP-10"] / "particles/firefly_trail.particle.json")
      and md5(R10 / "particles/firefly_emitter.particle.json") == md5(bf.SRC["RP-10"] / "particles/firefly_emitter.particle.json"))

# ---------------------------------------------------------------- G preview from the shipped JSON
def shipped_one(comp, rng, dt=0.05):
    """One emitter + its single particle, evaluated literally at 20 Hz. Returns (ts, alpha, x, y, z)."""
    env = {f"v.emitter_random_{i}": rng.random() for i in range(1, 5)}
    env.update({f"v.particle_random_{i}": rng.random() for i in range(1, 5)})
    env.update({"v.emitter_age": 0.0, "v.particle_age": 0.0})
    M.run(comp["minecraft:emitter_initialization"]["creation_expression"], env, rng)
    life = M.run(comp["minecraft:particle_lifetime_expression"]["max_lifetime"], env, rng); env["v.particle_lifetime"] = life
    upd = comp["minecraft:emitter_initialization"]["per_update_expression"]; rel = comp["minecraft:particle_motion_parametric"]["relative_position"]
    alpha = comp["minecraft:particle_appearance_tinting"]["color"][3]
    out = []
    while env["v.particle_age"] < life:
        M.run(upd, env, rng)
        out.append((env["v.particle_age"], M.run(alpha, env, rng), *(M.run(r, env, rng) for r in rel)))
        env["v.emitter_age"] += dt; env["v.particle_age"] += dt
    return np.array(out)

def approved_one(rng, dt=0.05):
    m = fc.model_prop(rng, fc.V2_SCALE); f = m["spawn"](0); out = []
    x0, y0 = f.x, f.y
    while f.age < f.life:
        m["step"](f, dt); f.x += f.vx * dt; f.y += f.vy * dt
        L = m["look"](f); out.append((f.age, max(l[3] for l in L), f.x - x0, f.y - y0, 0.0)); f.age += dt
    return np.array(out)

def rhythm(runs):
    """flashes per 10 s, fraction of time > 0.5, mean flash length (s), mean gap between flash starts (s) — mid-life only."""
    rates, duty, lens, gaps = [], [], [], []
    for r in runs:
        t, a = r[:, 0], r[:, 1]; mid = (t > 1.0) & (t < t[-1] - 1.5); on = (a > 0.5) & mid
        starts = np.where(on[1:] & ~on[:-1])[0]; span = mid.sum() * 0.05
        rates.append(len(starts) / span * 10); duty.append(on.sum() / max(1, mid.sum()))
        if len(starts) > 1: gaps.append(np.diff(starts).mean() * 0.05)
        runlen, cur = [], 0
        for v in on:
            if v: cur += 1
            elif cur: runlen.append(cur * 0.05); cur = 0
        lens += runlen
    return np.mean(rates), np.mean(duty), np.mean(lens), np.mean(gaps)

rngS, rngA = random.Random(7), random.Random(7)
S = [shipped_one(c, rngS) for _ in range(300)]; A_ = [approved_one(rngA) for _ in range(300)]
peak = max(r[:, 1].max() for r in S)
check("G1 shipped alpha reaches full brightness (fade not capped)", peak > 0.99, f"peak {peak:.3f} (old RP-10 line: 0.099)")
span = np.mean([np.ptp(r[:, 2]) for r in S]); spanz = np.mean([np.ptp(r[:, 4]) for r in S])
check("G2 shipped drift really moves (trig in degrees)", span > 0.3 and spanz > 0.3, f"mean x range {span:.2f} · z range {spanz:.2f} blocks over a life")
rs, ra = rhythm(S), rhythm(A_)
okr = all(abs(x - y) / y < 0.25 for x, y in zip(rs, ra))
check("G3 shipped flash rhythm matches the approved simulation (within 25%)", okr,
      "shipped/approved: flashes per 10 s {:.2f}/{:.2f} · lit {:.0%}/{:.0%} · flash {:.2f}/{:.2f} s · gap {:.2f}/{:.2f} s".format(rs[0], ra[0], rs[1], ra[1], rs[2], ra[2], rs[3], ra[3]))
spd_s = np.mean([np.hypot(np.diff(r[:, 2]), np.diff(r[:, 3])).mean() / 0.05 for r in S]); spd_a = np.mean([np.hypot(np.diff(r[:, 2]), np.diff(r[:, 3])).mean() / 0.05 for r in A_])
check("G4 shipped drift speed within 1.5x of the approved (side view)", 1 / 1.5 < spd_s / spd_a < 1.5, f"{spd_s:.3f} vs {spd_a:.3f} blocks/s")
TEXF = t_img.astype(np.float32) / 255
gs = fc.glow_size([(TEXF, 0.088, (1, 1, 1), 1.0, False)])
ga = fc.glow_size([(fc.TEX["prop_halo"], 0.11 * fc.V2_SCALE, (0.86, 1.0, 0.45), 0.7, False), (fc.TEX["prop_core"], 0.03 * fc.V2_SCALE, (1, 1, 0.85), 1.0, False)])
check("G5 shipped sprite size == approved H FINAL (bright centre and whole glow within 5%)",
      abs(gs[0] - ga[0]) / ga[0] < 0.05 and abs(gs[1] - ga[1]) / ga[1] < 0.05, f"centre {gs[0]:.3f}/{ga[0]:.3f} · glow {gs[1]:.3f}/{ga[1]:.3f} blocks")

# ---------------------------------------------------------------- H suite-wide
def pack_texts():
    dirs = [bf.DST[k] for k in PACKS] + [ROOT / d for d in ("_build/rp01-104", "_build/rp02-204", "_build/rp04-138", "_build/rp07-1410", "_build/markers-0.2.1/RP", "_build/bp02-186")]
    for d in dirs:
        for p in d.rglob("*"):
            if p.is_file() and p.suffix in (".json", ".js"): yield str(p.relative_to(ROOT)), p.read_text(encoding="utf-8", errors="ignore"), d
    for z in ("_packs/RP-06-v1_4_6.mcpack", "_packs/RP-08-v1_4_6.mcpack", "_packs/RP-11-v1_3_35.mcpack", "_packs/PW-StripMine-RP-v3_0_1.mcpack"):
        with zipfile.ZipFile(ROOT / z) as zf:
            for n in zf.namelist():
                if n.endswith((".json", ".js")): yield z + ":" + n, zf.read(n).decode("utf-8", "ignore"), z
dead, above, ids_seen = [], [], {}
ABOVE = ("rp10-140", "rp07-1410", "markers-0.2.1", "RP-06", "RP-08", "RP-11", "StripMine")
for name, text, src in pack_texts():
    if ("firefly_bush_v0" in text or "firefly_bush_emissive" in text) and not name.endswith("manifest.json"): dead.append(name)   # manifests: prose only
    if any(a in str(src) for a in ABOVE) and name.rsplit("/", 1)[-1] in ("terrain_texture.json", "flipbook_textures.json", "blocks.json"):
        if re.search(r'"firefly_bush"\s*:', text) or re.search(r'"atlas_tile"\s*:\s*"firefly_bush"', text): above.append(name)
    for pid in ("minecraft:firefly_particle", "pw:firefly_ambient"):
        if f'"identifier": "{pid}"' in text or f'"identifier":"{pid}"' in text: ids_seen.setdefault(pid, []).append(name)
check("H1 suite-wide: no reference left to firefly_bush_v0 / firefly_bush_emissive", not dead, str(dead[:4]))
check("H2 nothing above RP-05 overrides the bush key or its flipbook", not above, str(above[:4]))
check("H3 each particle id defined once in the stack (RP-10)", all(len(v) == 1 and v[0].startswith("_build/rp10-140") for v in ids_seen.values()) and len(ids_seen) == 2,
      json.dumps(ids_seen))
print("INFO H: StripMine RP 3.0.2 is not on disk — 3.0.1 censused (EXCLUSION noted; the 3.0.1->3.0.2 delta is StripMine content)")

if any(not ok for _, ok in res): print("GATE CLOSED"); sys.exit(1)
print(f"\nGATE OPEN — {len(res)} checks")
import datetime
with open(ROOT / "_logs/phase_log.md", "a") as f:
    f.write(f"[{datetime.datetime.now().strftime('%H:%M')} CT 09-23] VERIFY firefly v2 GATE OPEN {len(res)}/{len(res)} — packaging\n")
for k, (name,) in PACKS.items():
    out = OUT / name; B = bf.DST[k]
    if out.exists(): out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(B.rglob("*")):
            if p.is_file(): z.write(p, str(p.relative_to(B)).replace("\\", "/"))
    with zipfile.ZipFile(out) as z:
        zh = {n: hashlib.md5(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith("/")}
        assert zh == tree(B) and "manifest.json" in z.namelist()
    print(f"  {out.name} {out.stat().st_size:,} B md5 {md5(out)}")
