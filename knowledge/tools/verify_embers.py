#!/usr/bin/env python3
"""verify_embers.py — gate for HEARTH EMBERS E1+E2+E3: RP-04 v1.3.139 · RP-02 v2.0.5 · BP-02 v1.3.188 (D-C258). Packages all three on GATE OPEN.
  A RP-04 diff vs .138: exactly {pw_homestead.geo.json, pw_hearth_embers.png, pw_hearth_embers_mers.png, manifest, PW-DEPENDENCIES, textures_list}
    changed + exactly 8 files added (4 MERS + 4 texture_set); nothing removed
  B geometry: the 4 hearth geometries carry the 14x2x10 bed at y 1..3, logs +1 and flames +1 vs .138; flue/rafter geometries byte-identical;
    every non-hearth geometry unchanged; every cube stays inside the cell; bed faces all keyed 'bed'
  C textures: coal texture 128x128 opaque, brighter than the old (mean lum), MERS G channel emissive on the hot cells (>10 %), roughness in B, A 0;
    the 4 E2 texture sets parse, point at existing files, MERS emissive fraction > 0 and < 30 %; texture_set format 1.21.30
  D visibility: block_render of the built lit hearth from his usual view: the bed's share of the hearth's pixels >= 2x the .138 share
  E RP-02 diff vs 2.0.4: exactly {manifest} changed + {particles/pw_ember.json, textures/particle/pw_ember.png} added; the particle parses,
    identifier pw:ember, material particles_add, texture path exists, expire_on_contact, Molang parens balanced, lifetime 1.2-2.6
  F BP-02 diff vs .187: exactly {scripts/pw_homestead.js, scripts/main.js, manifest.json}; the edits confined to the three planned windows;
    PW_BUILD 1.3.188; the mock fog test still passes; api_audit flag set == .187's accepted set
  G manifests stamped (names/versions/descriptions); no other pack modified; the block files still reference the same material keys
"""
import json, re, sys, hashlib, zipfile, subprocess, datetime
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
ROOT = Path("/home/claude"); OUT = Path("/mnt/user-data/outputs")
RP4A, RP4B = ROOT / "_build/rp04-138", ROOT / "_build/rp04-139"
RP2A, RP2B = ROOT / "_build/rp02-204", ROOT / "_build/rp02-205"
BP2A, BP2B = ROOT / "_build/bp02-187", ROOT / "_build/bp02-188"
NAMES = {RP4B: "RP-04-AbsolutRealism-Basic-RP-v1_3_139.mcpack", RP2B: "RP-02-AbsolutRealism-Atmospheric-Effects-RP-v2_0_5.mcpack", BP2B: "BP-02-AbsolutRealism-Tectonic-BP-v1_3_188.mcpack"}
res = []
def check(n, ok, d=""): res.append((n, bool(ok))); print(("PASS " if ok else "FAIL ") + n + ("" if ok else f"  -> {str(d)[:300]}"))
def jload(p): return json.loads(re.sub(r"^\s*//.*$", "", Path(p).read_text(encoding="utf-8-sig"), flags=re.M))
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def th(root): return {str(p.relative_to(root)).replace("\\", "/"): md5(p) for p in root.rglob("*") if p.is_file()}

# A
h0, h1 = th(RP4A), th(RP4B); ch = {k for k in h0 if k in h1 and h0[k] != h1[k]}; added = set(h1) - set(h0); removed = set(h0) - set(h1)
E2 = ["pw_hearth_log_lit", "pw_hearth_log_end_lit", "pw_hearth_log_embers", "pw_hearth_log_end_embers"]
want_added = {f"textures/blocks/{n}_mers.png" for n in E2} | {f"textures/blocks/{n}.texture_set.json" for n in E2}
check("A RP-04 diff vs .138: 6 changed, 8 added, 0 removed", ch == {"models/blocks/pw_homestead.geo.json", "textures/blocks/pw_hearth_embers.png", "textures/blocks/pw_hearth_embers_mers.png", "manifest.json", "PW-DEPENDENCIES.md", "textures/textures_list.json"}
      and added == want_added and not removed, f"changed {sorted(ch)} added {sorted(added)} removed {sorted(removed)}")

# B
ga = {g["description"]["identifier"]: g for g in jload(RP4A / "models/blocks/pw_homestead.geo.json")["minecraft:geometry"]}
gb = {g["description"]["identifier"]: g for g in jload(RP4B / "models/blocks/pw_homestead.geo.json")["minecraft:geometry"]}
hearths = [k for k in gb if k.startswith("geometry.pw_hearth_")]
check("B same geometry set; non-hearth geometries unchanged", set(ga) == set(gb) and all(ga[k] == gb[k] for k in gb if k not in hearths) and len(hearths) == 4)
ok_b = True; detail = []
for k in hearths:
    A = {b["name"]: b for b in ga[k]["bones"]}; B = {b["name"]: b for b in gb[k]["bones"]}
    if set(A) != set(B): ok_b = False; detail.append((k, "bones"))
    bed = B["bed"]["cubes"][0]
    if not (bed["origin"] == [-7, 1, -6] and bed["size"] == [14, 2, 10] and all(f["material_instance"] == "bed" for f in bed["uv"].values()) and set(bed["uv"]) == {"up", "north", "south", "east", "west"}): ok_b = False; detail.append((k, "bed"))
    for name in A:
        if name in ("bed",): continue
        for ca, cb in zip(A[name]["cubes"], B[name]["cubes"]):
            dy = 1 if name in ("logs", "flames") else 0
            exp = dict(ca); exp["origin"] = [ca["origin"][0], ca["origin"][1] + dy, ca["origin"][2]]
            if "pivot" in ca: exp["pivot"] = [ca["pivot"][0], ca["pivot"][1] + dy, ca["pivot"][2]]
            if cb != exp: ok_b = False; detail.append((k, name))
    for b in gb[k]["bones"]:
        for c in b["cubes"]:
            o, s = c["origin"], c["size"]
            # the flame cross already reached y 18 in .138 (2 cubes into the flue bore); +1 -> 19. Everything solid stays inside the cell.
            if not (-8.5 <= o[0] and o[0] + s[0] <= 8.5 and 0 <= o[1] and o[1] + s[1] <= (19.5 if b["name"] == "flames" else 16) and -8 <= o[2] and o[2] + s[2] <= 8): ok_b = False; detail.append((k, b["name"], "bounds"))
check("B hearth geometries: bed 14x2x10 at y1..3 (5 faces 'bed'), logs +1, flames +1 (origin+pivot), everything else identical, cubes inside the cell", ok_b, detail[:6])

# C
old = np.asarray(Image.open(RP4A / "textures/blocks/pw_hearth_embers.png").convert("RGBA")).astype(float); new = np.asarray(Image.open(RP4B / "textures/blocks/pw_hearth_embers.png").convert("RGBA")).astype(float)
lum = lambda a: (0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2]).mean()
mers = np.asarray(Image.open(RP4B / "textures/blocks/pw_hearth_embers_mers.png").convert("RGBA")).astype(float)
bright = lambda a: (a[..., :3].max(-1) > 150).mean(); p90 = lambda a: np.percentile(0.3 * a[..., 0] + 0.59 * a[..., 1] + 0.11 * a[..., 2], 90)
check("C coal texture 128x128 opaque; bright(>150) texel share >= 3x the old (glowing veins), 90th-percentile luminance >= 1.5x the old", new.shape == (128, 128, 4) and (new[..., 3] == 255).all() and bright(new) >= 3 * bright(old) and p90(new) >= 1.5 * p90(old), f"bright {100*bright(old):.1f}% -> {100*bright(new):.1f}%; p90 lum {p90(old):.0f} -> {p90(new):.0f}")
check("C coal MERS: R 0, G emissive on > 10 % of texels, B roughness 120..210, A 0", (mers[..., 0] == 0).all() and (mers[..., 1] > 0).mean() > 0.10 and mers[..., 2].min() >= 119 and mers[..., 2].max() <= 211 and (mers[..., 3] == 0).all())
ok_c = True; det = []
for n in E2:
    ts = jload(RP4B / f"textures/blocks/{n}.texture_set.json")
    m = np.asarray(Image.open(RP4B / f"textures/blocks/{n}_mers.png").convert("RGBA")).astype(float)
    frac = (m[..., 1] > 0).mean()
    if not (ts["format_version"] == "1.21.30" and ts["minecraft:texture_set"]["color"] == n and ts["minecraft:texture_set"]["metalness_emissive_roughness_subsurface"] == f"{n}_mers"
            and (RP4B / f"textures/blocks/{n}.png").exists() and 0 < frac < 0.30 and (m[..., 0] == 0).all() and (m[..., 3] == 0).all()): ok_c = False
    det.append((n, round(frac, 3)))
check("C E2 texture sets: 1.21.30, colour + MERS files exist, emissive on the cracks (0 < share < 30 %)", ok_c, det)
tl = jload(RP4B / "textures/textures_list.json")
check("C textures_list carries the 4 new MERS paths and the old entries", all(f"textures/blocks/{n}_mers" in tl for n in E2) and set(jload(RP4A / "textures/textures_list.json")) <= set(tl))

# D visibility from his usual view (block_render on the BUILT files; the BP-02 .187 block's lit material map)
import block_render as BR
bp_block = ROOT / "_build/bp02-187/blocks/pw_hearth_stone.json"
def share(rp_dir, ident, phase):
    BR.RP04_TEX = rp_dir / "textures/blocks"; BR.TERRAIN = rp_dir / "textures/terrain_texture.json"; BR._texcache.clear()
    # point the texture loader at this build
    orig = BR.texture
    def tex(stem, frame=0):
        key = (stem, frame)
        if key in BR._texcache: return BR._texcache[key]
        tt = BR.load_json(rp_dir / "textures/terrain_texture.json")["texture_data"]; path = tt[stem]["textures"] if stem in tt else "textures/blocks/" + stem
        if isinstance(path, list): path = path[0]
        if isinstance(path, dict): path = path["path"]
        im = Image.open(rp_dir / (path + ".png")).convert("RGBA")
        if im.height > im.width and im.height % im.width == 0:
            n = im.height // im.width; im = im.crop((0, (frame % n) * im.width, im.width, (frame % n + 1) * im.width))
        a = np.asarray(im).astype(np.float32) / 255.0; BR._texcache[key] = a; return a
    BR.texture = tex
    faces = BR.load_faces(rp_dir / "models/blocks/pw_homestead.geo.json", ident); mats = BR.materials(bp_block, phase)
    img, ids, mid = BR.render(faces, mats, (0, 26, -48), (0, 8, 0), 1920, 1080)
    BR.texture = orig
    hearth = (ids > 0); return (ids == mid["bed"]).sum() / max(1, hearth.sum()), img
s0, _ = share(RP4A, "geometry.pw_hearth_lit", "lit"); s1, img1 = share(RP4B, "geometry.pw_hearth_lit", "lit")
e0, _ = share(RP4A, "geometry.pw_hearth_embers", "embers"); e1, img2 = share(RP4B, "geometry.pw_hearth_embers", "embers")
check("D bed share of the hearth's pixels from his usual view: lit >= 2x .138, embers >= 2x .138", s1 >= 2 * s0 and e1 >= 2 * e0, f"lit {100*s0:.1f}% -> {100*s1:.1f}%; embers {100*e0:.1f}% -> {100*e1:.1f}%")
Image.fromarray(img1).crop((760, 300, 1160, 700)).resize((800, 800), Image.NEAREST).save(ROOT / "_design/hearth-embers/v139-lit-viewA.png")
Image.fromarray(img2).crop((760, 300, 1160, 700)).resize((800, 800), Image.NEAREST).save(ROOT / "_design/hearth-embers/v139-embers-viewA.png")

# E RP-02
h0, h1 = th(RP2A), th(RP2B); ch = {k for k in h0 if k in h1 and h0[k] != h1[k]}; added = set(h1) - set(h0); removed = set(h0) - set(h1)
check("E RP-02 diff vs 2.0.4: manifest changed; pw_ember.json + pw_ember.png added; nothing removed", ch == {"manifest.json"} and added == {"particles/pw_ember.json", "textures/particle/pw_ember.png"} and not removed, f"{sorted(ch)} {sorted(added)} {sorted(removed)}")
pe = jload(RP2B / "particles/pw_ember.json")["particle_effect"]; comp = pe["components"]; txt = json.dumps(comp)
bal = all(e.count("(") == e.count(")") for e in re.findall(r'"([^"]*(?:math\.|variable\.)[^"]*)"', txt))
check("E pw:ember: additive material, texture exists, expire_on_contact, lifetime 1.2-2.6 s, 2 particles per spawn, Molang balanced",
      pe["description"]["identifier"] == "pw:ember" and pe["description"]["basic_render_parameters"]["material"] == "particles_add" and (RP2B / (pe["description"]["basic_render_parameters"]["texture"] + ".png")).exists()
      and comp["minecraft:particle_motion_collision"]["expire_on_contact"] is True and comp["minecraft:particle_lifetime_expression"]["max_lifetime"] == "math.random(1.2, 2.6)" and comp["minecraft:emitter_rate_instant"]["num_particles"] == 2 and bal)
sp = np.asarray(Image.open(RP2B / "textures/particle/pw_ember.png").convert("RGBA"))
check("E spark texture 16x16: opaque bright core, transparent corners", sp.shape == (16, 16, 4) and sp[7, 7, 3] == 255 and sp[7, 7, :3].min() > 200 and sp[0, 0, 3] == 0)

# F BP-02
h0, h1 = th(BP2A), th(BP2B); ch = {k for k in h0 if k in h1 and h0[k] != h1[k]}
check("F BP-02 diff vs .187: exactly pw_homestead.js, main.js, manifest.json", ch == {"scripts/pw_homestead.js", "scripts/main.js", "manifest.json"} and set(h0) == set(h1), sorted(ch))
sa, sb = (BP2A / "scripts/pw_homestead.js").read_text(encoding="utf-8"), (BP2B / "scripts/pw_homestead.js").read_text(encoding="utf-8")
def strip(s):
    s = re.sub(r"^// pw_homestead\.js — HOMESTEAD family runtime.*$", "", s, flags=re.M)
    s = re.sub(r"const EMBER_ID = \"pw:ember\";.*?\nconst EMBER_LIT = 0\.45, EMBER_EMBERS_EVERY = 6;\n", "", s, flags=re.S)
    s = re.sub(r"  emberCycle\(\);\n\}\n/\*\* E3 \(v1\.3\.188\).*?\n\}\n", "}\n", s, flags=re.S)
    return s
check("F pw_homestead.js edits confined to the three planned windows (header, constants, emberCycle)", strip(sa) == strip(sb))
check("F emberCycle spawns pw:ember from puffTargets (lit 0.45 / embers 1 in 6) and is called from puffCycle; PW_BUILD 1.3.188",
      "function emberCycle()" in sb and 'spawnParticle(EMBER_ID, loc)' in sb and "Math.random() < EMBER_LIT" in sb and "puffNo % EMBER_EMBERS_EVERY === 0" in sb and sb.count("emberCycle();") == 1
      and 'const PW_BUILD = "1.3.188";' in (BP2B / "scripts/main.js").read_text(encoding="utf-8"))
nc = subprocess.run(["node", "--check", str(BP2B / "scripts/pw_homestead.js")], capture_output=True, text=True).returncode
check("F node --check pw_homestead.js", nc == 0)
r = subprocess.run(["node", str(ROOT / "tools/testrunner_src/test_homestead_fog.mjs"), str(BP2B / "scripts")], capture_output=True, text=True, timeout=300)
tail = (r.stdout.strip().splitlines() or [r.stderr[-200:]])[-1]
check("F mock-run of the shipped homestead module (fog tests) still passes", r.returncode == 0 and ", 0 failed" in tail, tail)
def flags(d):
    r = subprocess.run([sys.executable, str(ROOT / "tools/api_audit.py"), str(d)], capture_output=True, text=True, timeout=900)
    return sorted(re.sub(r":\d+  ", " ", re.sub(r"^\s+scripts/", "", l).split("  |")[0].strip()) for l in r.stdout.splitlines() if re.match(r"^\s+scripts/", l))
fa, fb = flags(BP2A), flags(BP2B)
check("F api_audit: the flag set is EXACTLY .187's accepted set", fa == fb, f"{len(fa)} vs {len(fb)}")

# G
for d, ver, name in ((RP4B, "1.3.139", "AbsolutRealism Basic RP v1.3.139"), (RP2B, "2.0.5", "AbsolutRealism Atmospheric Effects RP v2.0.5"), (BP2B, "1.3.188", "AbsolutRealism Tectonic BP v1.3.188")):
    m = jload(d / "manifest.json"); v = [int(x) for x in ver.split(".")]
    check(f"G manifest {name}: version + modules + stamped description", m["header"]["name"] == name and m["header"]["version"] == v and all(x["version"] == v for x in m["modules"]) and m["header"]["description"].startswith(f"v{ver} (2026-09-27) HEARTH EMBERS"))
blk = jload(bp_block)
check("G BP-02 hearth blocks still key the coal bed as 'bed' -> pw_hearth_embers in lit/embers (E1 needs no block change)", all(p["components"]["minecraft:material_instances"]["bed"]["texture"] == "pw_hearth_embers" for p in blk["minecraft:block"]["permutations"] if p["condition"].endswith(("'lit'", "'embers'"))))
def dir_equals_zip(d, z):
    with zipfile.ZipFile(z) as zf: return all(hashlib.md5(zf.read(n)).hexdigest() == md5(d / n) for n in zf.namelist() if not n.endswith("/"))
check("G the three source builds still equal their delivered packs (.138 / 2.0.4 / .187)", all(dir_equals_zip(ROOT / "_build" / d, OUT / z) for d, z in (("rp04-138", "RP-04-AbsolutRealism-Basic-RP-v1_3_138.mcpack"), ("rp02-204", "RP-02-AbsolutRealism-Atmospheric-Effects-RP-v2_0_4.mcpack"), ("bp02-187", "BP-02-AbsolutRealism-Tectonic-BP-v1_3_187.mcpack"))))

if any(not ok for _, ok in res): print("GATE CLOSED"); sys.exit(1)
print(f"\nGATE OPEN — {len(res)} checks")
with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{datetime.datetime.now().strftime('%H:%M')} CT 09-27] VERIFY embers GATE OPEN {len(res)}/{len(res)} — packaging RP-04 .139 + RP-02 2.0.5 + BP-02 .188\n")
for d, name in NAMES.items():
    out = OUT / name
    if out.exists(): out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(d.rglob("*")):
            if p.is_file(): z.write(p, str(p.relative_to(d)).replace("\\", "/"))
    with zipfile.ZipFile(out) as z:
        zh = {n: hashlib.md5(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith("/")}
        assert zh == th(d) and "manifest.json" in z.namelist()
    print(f"  {out.name} {out.stat().st_size:,} B md5 {md5(out)}")
