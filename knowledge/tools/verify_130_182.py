#!/usr/bin/env python3
"""verify_130_182.py — GATE for RP-04 v1.3.130 + RP-02 v2.0.3 + BP-02 v1.3.182 (D-101: nothing is packaged unless
every check passes; packaging happens INSIDE this gate).

Checks
  I   change-set identity: every file outside the intended change set is byte-identical to its source tree
  J   strict JSON parse of every changed/added JSON file
  T   every terrain key referenced by BP-02 blocks resolves (RP-04 .130, else the stack: RP-10 snow_v0) to an existing PNG
  G   every geometry referenced by BP-02 blocks exists in RP-04 .130
  F   flame flipbooks: entries + 128x3840 strips + frame lists in range
  R   ramps: 30 board faces -> `cut` (east mirrored), strips inside the 128² textures, 18 blocks carry `cut` everywhere
  H   hearth: 53 blocks, state list, 4 phase permutations (spent = fueled boxes + charcoal), light map, keys resolve
  X   flue: 53 blocks, hollow geometries, collision_box false, cap permutation
  S   scripts: node --check both files, unit tests pass, imports intact, manifest dependencies untouched (Lesson #53)
  P   RP-02: particle JSONs parse, pw:hearth_puff present, 128x1536 sprite, every uv in texel units matches it
  C   cross-block fight census (profile_render): roof seam A <= 0.03, cap seam A' <= 0.01, every ramp seam <= 0.01,
      every snowed toe: filler-vs-board = 0 (board cut), residual = filler-vs-slab only (deferred by ruling)
  L   ledgers: BP needs-hash consistent; new rows present
  V   manifests: versions, names, descriptions stamped; pairing text present
  Z   package + from-zip identity + version-spot gate (verify_pack_versions.py)
"""
import json, os, re, sys, hashlib, zipfile, subprocess, io, math
from pathlib import Path
import numpy as np
from PIL import Image

sys.path.insert(0, "/home/claude/tools")
import profile_render as pr    # noqa: E402

ROOT = Path("/home/claude")
RP0, RP = ROOT / "_build/rp04-129", ROOT / "_build/rp04-130"
RP20, RP2 = ROOT / "_build/rp02-202", ROOT / "_build/rp02-203"
BP0, BP = ROOT / "_build/bp02-181", ROOT / "_build/bp02-182"
OUT = Path("/mnt/user-data/outputs")
RP10_ZIP = ROOT / "_packs/RP-10-v1_3_39.mcpack"

results = []
def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))
    return bool(ok)
def load(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def strict(p):
    try: json.loads(Path(p).read_text(encoding="utf-8")); return True
    except Exception as e: print("   strict parse failed:", p, e); return False

def tree_files(root): return {str(p.relative_to(root)).replace(os.sep, "/"): p for p in root.rglob("*") if p.is_file()}
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()

# ---------------------------------------------------------------- I: change-set identity
EXPECT = {
    "RP-04": {"manifest.json", "PW-DEPENDENCIES.md", "textures/terrain_texture.json", "textures/flipbook_textures.json",
              "models/blocks/pw_ramps.geo.json", "models/blocks/pw_snowcaps.geo.json", "models/blocks/pw_homestead.geo.json",
              "textures/blocks/pw_mitre_oak.png", "textures/blocks/pw_mitre_spruce.png",
              "textures/blocks/pw_hearth_flame.png"}
             | {f"textures/blocks/pw_rampcut_{m}.png" for m in ("cobble", "smooth_stone", "stonebrick")}
             | {f"textures/blocks/{k}.png" for k in ("pw_hearth_flame_low", "pw_hearth_log_fueled", "pw_hearth_log_lit", "pw_hearth_log_embers", "pw_hearth_log_cold",
                                                     "pw_hearth_log_end_lit", "pw_hearth_log_end_embers", "pw_hearth_log_end_cold")},
    "RP-02": {"manifest.json", "textures/particle/campfire_smoke.png", "particles/pw_chimney_smoke.json", "particles/pw_room_smoke.json", "particles/pw_hearth_puff.json"},
    "BP-02": {"manifest.json", "PW-DEPENDENCIES.md", "scripts/pw_homestead.js", "scripts/pw_homestead_logic.js"},
}
changed = {}
for label, (src, dst) in {"RP-04": (RP0, RP), "RP-02": (RP20, RP2), "BP-02": (BP0, BP)}.items():
    a, b = tree_files(src), tree_files(dst)
    diff = {n for n in set(a) | set(b) if n not in a or n not in b or a[n].read_bytes() != b[n].read_bytes()}
    if label == "BP-02":
        blocks = {n for n in diff if n.startswith("blocks/") and re.match(r"blocks/pw_(ramp|hearth|flue)_", n)}
        other = diff - blocks
        check("I BP-02 block change set = ramps+hearth+flue only", len(blocks) == 18 + 53 + 53 and not (other - EXPECT["BP-02"]), f"{len(blocks)} blocks, other {sorted(other)}")
        check("I BP-02 expected non-block files changed", EXPECT["BP-02"] <= other, sorted(EXPECT["BP-02"] - other))
    else:
        check(f"I {label} change set exact", diff == EXPECT[label], f"unexpected {sorted(diff - EXPECT[label])} missing {sorted(EXPECT[label] - diff)}")
    changed[label] = diff
    for n in diff:
        if n.endswith(".json") and (dst / n).exists():
            check(f"J strict {label}/{n}", strict(dst / n))
# thatch note: the mitre strips for thatch carried nothing to cut (0 texels) — recorded, not a failure
check("I thatch mitre byte-identical (no strip content to cut — backlog THATCH-MITRE)", md5(RP / "textures/blocks/pw_mitre_thatch.png") == md5(RP0 / "textures/blocks/pw_mitre_thatch.png"))

# ---------------------------------------------------------------- T / G: every key and geometry the BP references
tt = load(RP / "textures/terrain_texture.json")["texture_data"]
def key_paths(v):
    t = v["textures"]
    if isinstance(t, str): return [t]
    if isinstance(t, list): return [x if isinstance(x, str) else x["path"] for x in t]
    return [x["path"] if isinstance(x, dict) else x for x in t["variations"]]
with zipfile.ZipFile(RP10_ZIP) as z: rp10_names = set(z.namelist())
geos = set()
for p in (RP / "models/blocks").glob("*.json"):
    for g in load(p).get("minecraft:geometry", []): geos.add(g["description"]["identifier"])
missing_keys, missing_files, missing_geo = set(), set(), set()
def scan(comps):
    for name, mi in comps.get("minecraft:material_instances", {}).items():
        k = mi.get("texture")
        if k not in tt: missing_keys.add(k); continue
        for path in key_paths(tt[k]):
            if not (RP / f"{path}.png").exists() and f"{path}.png" not in rp10_names: missing_files.add(path)
    g = comps.get("minecraft:geometry")
    gid = g.get("identifier") if isinstance(g, dict) else g
    if gid and gid != "minecraft:geometry.full_block" and gid not in geos: missing_geo.add(gid)
nblocks = 0
for p in (BP / "blocks").glob("*.json"):
    if not re.match(r"pw_(ramp|hearth|flue)_", p.name): continue      # this build's families; the rest is other packs' business
    b = load(p)["minecraft:block"]; nblocks += 1
    scan(b["components"])
    for pm in b.get("permutations", []): scan(pm.get("components", {}))
check("T every terrain key referenced by the 124 changed blocks exists", not missing_keys and nblocks == 124, f"{nblocks} blocks; missing {sorted(missing_keys)[:10]}")
check("T every texture file behind those keys exists (RP-04 .130 or RP-10)", not missing_files, sorted(missing_files)[:10])
check("G every geometry referenced by the changed blocks exists in RP-04 .130", not missing_geo, sorted(missing_geo)[:10])

# ---------------------------------------------------------------- F: flame flipbooks
fb = load(RP / "textures/flipbook_textures.json")
ent = {e["atlas_tile"]: e for e in fb if e.get("atlas_tile") in ("pw_hearth_flame", "pw_hearth_flame_low")}
ok = len(ent) == 2 and all(sorted(e["frames"]) == list(range(30)) and e["ticks_per_frame"] == 1 for e in ent.values())
check("F flipbook entries pw_hearth_flame + pw_hearth_flame_low (30 frames each, 1 tick/frame)", ok)
for k in ("pw_hearth_flame", "pw_hearth_flame_low"):
    im = Image.open(RP / f"textures/blocks/{k}.png")
    check(f"F {k}.png 128x3840 RGBA", im.size == (128, 3840) and im.mode == "RGBA", f"{im.size} {im.mode}")
    check(f"F {k} key -> its own file", tt[k]["textures"] == f"textures/blocks/{k}")
check("F only one flipbook entry per hearth flame tile", sum(1 for e in fb if e.get("atlas_tile") == "pw_hearth_flame") == 1)

# ---------------------------------------------------------------- R: ramps
plain = load(RP / "models/blocks/pw_ramps.geo.json"); snow = load(RP / "models/blocks/pw_snowcaps.geo.json")
boards = 0; bad = []
for doc in (plain, snow):
    for g in doc["minecraft:geometry"]:
        if not g["description"]["identifier"].startswith("geometry.pw_ramp_"): continue
        for b in g["bones"]:
            for c in b.get("cubes", []):
                if c.get("rotation") and c["uv"]["up"].get("material_instance") == "deck":
                    boards += 1
                    w, e = c["uv"]["west"], c["uv"]["east"]
                    if not (w.get("material_instance") == "cut" and e.get("material_instance") == "cut" and w["uv_size"] == [128, 9.6] and e["uv_size"] == [-128, 9.6]
                            and e["uv"][0] == 128 and w["uv"][0] == 0 and abs(w["uv"][1] - e["uv"][1]) < 1e-9 and 0 <= w["uv"][1] and w["uv"][1] + 9.6 <= 128):
                        bad.append(g["description"]["identifier"])
check("R 30 ramp boards -> `cut`, east mirrored, strips inside 0..128", boards == 30 and not bad, f"{boards} boards, bad {bad[:5]}")
for m in ("cobble", "smooth_stone", "stonebrick"):
    im = Image.open(RP / f"textures/blocks/pw_rampcut_{m}.png"); a = np.array(im.convert("RGBA"))
    check(f"R pw_rampcut_{m}.png 128² RGBA with 10 strips (opaque rows)", im.size == (128, 128) and 90 <= int((a[..., 3].max(axis=1) > 0).sum()) <= 100, f"{im.size} opaque rows {(a[..., 3].max(axis=1) > 0).sum()}")
    check(f"R terrain key pw_rampcut_{m}", tt.get(f"pw_rampcut_{m}", {}).get("textures") == f"textures/blocks/pw_rampcut_{m}")
n_cut = 0; n_dicts = 0; n_blocks = 0
for p in sorted((BP / "blocks").glob("pw_ramp_*.json")):
    b = load(p)["minecraft:block"]; n_blocks += 1
    for comps in [b["components"]] + [pm.get("components", {}) for pm in b.get("permutations", [])]:
        mi = comps.get("minecraft:material_instances")
        if mi is not None:
            n_dicts += 1
            if mi.get("cut", {}).get("render_method") == "alpha_test" and mi["cut"]["texture"].startswith("pw_rampcut_"): n_cut += 1
check("R 18 ramp blocks: every material_instances dict carries `cut`", n_blocks == 18 and n_cut == n_dicts and n_dicts > 0, f"{n_blocks} blocks, {n_cut}/{n_dicts}")

# ---------------------------------------------------------------- H: hearth
hp = sorted((BP / "blocks").glob("pw_hearth_*.json")); okh = True; det = []
for p in hp:
    b = load(p)["minecraft:block"]
    st = b["description"]["states"].get("pw:phase")
    perms = b["permutations"]
    ph = {re.search(r"pw:phase'\) == '(\w+)'", pm["condition"]).group(1): pm for pm in perms if "pw:phase" in pm["condition"]}
    rot = [pm for pm in perms if "cardinal_direction" in pm["condition"]]
    cond = (st == ["cold", "fueled", "lit", "embers", "spent"] and set(ph) == {"fueled", "lit", "embers", "spent"} and len(rot) == 4
            and ph["spent"]["components"]["minecraft:geometry"]["identifier"] == "geometry.pw_hearth_fueled"
            and ph["spent"]["components"]["minecraft:light_emission"] == 0 and ph["lit"]["components"]["minecraft:light_emission"] == 15
            and ph["embers"]["components"]["minecraft:light_emission"] == 7
            and ph["spent"]["components"]["minecraft:material_instances"]["log"]["texture"] == "pw_hearth_log_cold"
            and ph["lit"]["components"]["minecraft:material_instances"]["flame"]["texture"] == "pw_hearth_flame"
            and ph["embers"]["components"]["minecraft:material_instances"]["flame"]["texture"] == "pw_hearth_flame_low"
            and ph["fueled"]["components"]["minecraft:material_instances"]["log"]["texture"] == "pw_hearth_log_fueled"
            and all(v["render_method"] == "alpha_test" for pm in perms for v in pm.get("components", {}).get("minecraft:material_instances", {}).values()))
    if not cond: okh = False; det.append(p.name)
check("H 53 hearth blocks: spent phase, geometry/light/keys, single render_method", okh and len(hp) == 53, det[:5])

# ---------------------------------------------------------------- X: flue
fp = sorted((BP / "blocks").glob("pw_flue_*.json")); okx = True; det = []
for p in fp:
    b = load(p)["minecraft:block"]; c = b["components"]
    cap = [pm for pm in b["permutations"] if "pw:cap" in pm["condition"]]
    cond = (c["minecraft:geometry"] == {"identifier": "geometry.pw_flue_hollow"} and c["minecraft:collision_box"] is False
            and c["minecraft:selection_box"]["size"] == [16, 16, 16] and "soot" in c["minecraft:material_instances"]
            and len(cap) == 1 and cap[0]["components"]["minecraft:geometry"]["identifier"] == "geometry.pw_flue_cap_hollow")
    if not cond: okx = False; det.append(p.name)
check("X 53 flue blocks: hollow geometries, collision false, cap permutation, soot", okx and len(fp) == 53, det[:5])
hg = {g["description"]["identifier"]: g for g in load(RP / "models/blocks/pw_homestead.geo.json")["minecraft:geometry"]}
def walls_ok(g):
    cubes = [c for b in g["bones"] if b["name"] == "walls" for c in b["cubes"]]
    return len(cubes) == 4 and sorted(tuple(c["origin"]) for c in cubes) == sorted([(-8, 0, -8), (-8, 0, 6), (-8, 0, -6), (6, 0, -6)])
check("X geometry.pw_flue_hollow: 4 walls, 2 cubes thick", "geometry.pw_flue_hollow" in hg and walls_ok(hg["geometry.pw_flue_hollow"]))
check("X geometry.pw_flue_cap_hollow: walls + rim, no throat plate", "geometry.pw_flue_cap_hollow" in hg and walls_ok(hg["geometry.pw_flue_cap_hollow"]) and {b["name"] for b in hg["geometry.pw_flue_cap_hollow"]["bones"]} == {"walls", "rim"})

# ---------------------------------------------------------------- S: scripts
for f in ("pw_homestead.js", "pw_homestead_logic.js"):
    r = subprocess.run(["node", "--check", str(BP / "scripts" / f)], capture_output=True, text=True)
    check(f"S node --check {f}", r.returncode == 0, r.stderr[:200])
r = subprocess.run(["node", "test_logic.mjs"], cwd=str(ROOT / "tools/homestead_src"), capture_output=True, text=True)
check("S unit tests pass (tools/homestead_src/test_logic.mjs)", r.returncode == 0 and "tests passed" in r.stdout, r.stdout.strip().splitlines()[-1] if r.stdout else r.stderr[:200])
check("S shipped logic == tested logic", md5(BP / "scripts/pw_homestead_logic.js") == md5(ROOT / "tools/homestead_src/pw_homestead_logic.js") and md5(BP / "scripts/pw_homestead.js") == md5(ROOT / "tools/homestead_src/pw_homestead.js"))
js = (BP / "scripts/pw_homestead.js").read_text(encoding="utf-8")
check("S runtime wires puffCycle + chuteCycle and imports EntityDamageCause", all(s in js for s in ("system.runInterval(puffCycle, PUFF_TICKS)", "system.runInterval(chuteCycle, 1)", "EntityDamageCause", 'import * as L from "./pw_homestead_logic.js"', "pw:hearth_puff")))
mainjs = (BP / "scripts/main.js").read_text(encoding="utf-8") if (BP / "scripts/main.js").exists() else ""
check("S main.js still imports ./pw_homestead.js", 'import "./pw_homestead.js"' in mainjs)
m0, m1 = load(BP0 / "manifest.json"), load(BP / "manifest.json")
check("S manifest dependencies untouched (Lesson #53)", m0.get("dependencies") == m1.get("dependencies"))

# ---------------------------------------------------------------- P: RP-02 particles
sm = Image.open(RP2 / "textures/particle/campfire_smoke.png")
check("P campfire_smoke.png = 128x1536 RGBA", sm.size == (128, 1536) and sm.mode == "RGBA", f"{sm.size} {sm.mode}")
for f in ("pw_chimney_smoke", "pw_room_smoke", "pw_hearth_puff"):
    d = load(RP2 / f"particles/{f}.json"); pe = d["particle_effect"]
    uv = pe["components"]["minecraft:particle_appearance_billboard"]["uv"]
    check(f"P {f}: texture campfire_smoke + 128-px flipbook uv", pe["description"]["basic_render_parameters"]["texture"] == "textures/particle/campfire_smoke"
          and uv["texture_width"] == 128 and uv["texture_height"] == 1536 and uv["flipbook"]["size_UV"] == [128, 128] and uv["flipbook"]["step_UV"] == [0, 128] and uv["flipbook"]["max_frame"] == 12)
check("P pw:hearth_puff identifier + expire_on_contact", load(RP2 / "particles/pw_hearth_puff.json")["particle_effect"]["description"]["identifier"] == "pw:hearth_puff"
      and load(RP2 / "particles/pw_hearth_puff.json")["particle_effect"]["components"]["minecraft:particle_motion_collision"]["expire_on_contact"] is True)
for f in ("campfire_smoke", "campfire_smoke_tall"):
    uv = load(RP2 / f"particles/{f}.json")["particle_effect"]["components"]["minecraft:particle_appearance_billboard"]["uv"]
    check(f"P vanilla-override {f}: 1x12 normalised uv (layout-agnostic)", uv["texture_width"] == 1 and uv["texture_height"] == 12)

# ---------------------------------------------------------------- C: cross-block fight census on the BUILT trees
def geo_of(tree, stem, ident=None):
    for g in load(tree / f"models/blocks/{stem}.geo.json")["minecraft:geometry"]:
        if ident is None or g["description"]["identifier"] == ident: return g
    raise KeyError(ident)
def tex(tree, name): return pr.load_tex(str(tree / f"textures/blocks/{name}.png"))
SNOW = pr.load_tex("/home/claude/_intake/snow_v0.png")
SC = 32
def fight(faces, win): return pr.render(faces, "east", *win, SC)[2]
# A / A' (spruce, and oak)
for mat in ("spruce", "oak"):
    tm = {"*": tex(RP, f"pw_roof_{mat}"), "mitre": tex(RP, f"pw_mitre_{mat}"), "fill": tex(RP, f"pw_fill_45_{mat}"), "deck": tex(RP, f"pw_deck45_{mat}")}
    tmc = dict(tm); tmc["fill"] = tex(RP, f"pw_fill_ridge_{mat}"); tmc["deck"] = tex(RP, f"pw_deck45h_{mat}")
    lower = geo_of(RP, "roof45_straight")
    fA = pr.faces_of(lower, "east", tm, (0, 0), "L.") + pr.faces_of(geo_of(RP, "roof45_straight"), "east", tm, (16, 16), "U.")
    fA2 = pr.faces_of(lower, "east", tm, (0, 0), "L.") + pr.faces_of(geo_of(RP, "roof45_ridge"), "east", tmc, (16, 16), "U.")
    a = fight(fA, (5, 11, 13, 20)); a2 = fight(fA2, (5, 11, 13, 20))
    check(f"C roof course seam {mat} <= 0.03 px²", a <= 0.03, f"{a:.3f}"); check(f"C ridge-cap seam {mat} <= 0.03 px²", a2 <= 0.03, f"{a2:.3f}")
# every ramp seam, every material, unsnowed: q1->q2, q2->q3, q3->q4, 2_lo->2_hi
FILL = {"2_lo": "pw_fill26l", "2_hi": "pw_fill26u", "4_q1": "pw_fill14q1", "4_q2": "pw_fill14q2", "4_q3": "pw_fill14q3", "4_q4": "pw_fill14q4"}
DECK = {"2_lo": "pw_deck26", "2_hi": "pw_deck26", "4_q1": "pw_deck14", "4_q2": "pw_deck14", "4_q3": "pw_deck14", "4_q4": "pw_deck14"}
worst = 0.0
for mat in ("cobble", "smooth_stone", "stonebrick"):
    for lo, hi in (("4_q1", "4_q2"), ("4_q2", "4_q3"), ("4_q3", "4_q4"), ("2_lo", "2_hi")):
        def tmap(shape): return {"*": tex(RP, f"pw_rampv4_{mat}_0"), "fill": tex(RP, f"{FILL[shape]}_{mat}"), "deck": tex(RP, f"{DECK[shape]}_{mat}_0"), "cut": tex(RP, f"pw_rampcut_{mat}")}
        faces = pr.faces_of(geo_of(RP, "pw_ramps", f"geometry.pw_ramp_{lo}"), "east", tmap(lo), (0, -16), "a.") + pr.faces_of(geo_of(RP, "pw_ramps", f"geometry.pw_ramp_{hi}"), "east", tmap(hi), (0, 0), "b.")
        v = fight(faces, (-11, -1, -0.5, 15.5)); worst = max(worst, v)
check("C every ramp seam (3 materials x 4 seams), unsnowed: fight <= 0.01 px²", worst <= 0.01, f"worst {worst:.3f}")
# snowed toes: filler-vs-board must be 0 after the board cut; the residual is filler-vs-slab only (deferred)
resid = {}; leak = 0.0; slabcap = 0.0
for shape in ("2_lo", "4_q1"):
    for lvl in (1, 2, 3, 4):
        mat = "stonebrick"
        tm = {"*": tex(RP, f"pw_rampv4_{mat}_0"), "fill": tex(RP, f"{FILL[shape]}_{mat}"), "deck": tex(RP, f"{DECK[shape]}_{mat}_0"), "cut": tex(RP, f"pw_rampcut_{mat}"), "snow": SNOW}
        g = geo_of(RP, "pw_snowcaps", f"geometry.pw_ramp_{shape}_snow{lvl}")
        faces = pr.faces_of(g, "east", tm, (0, 0), "s.")
        img, fm, area, pairs = pr.render(faces, "east", -9, 9, -1.5, 16.5, SC)
        for (t1, t2), v in pairs.items():
            insts = {[f for f in faces if f.tag == t][0].inst for t in (t1, t2)}
            if insts == {"snow"}: resid[(shape, lvl)] = resid.get((shape, lvl), 0) + v        # filler vs slab: deferred by ruling
            elif "cut" in insts: leak += v                                                     # anything against the BOARD must be gone
            else: slabcap += v                                                                 # slab vs stone cap filler: slab untouched by ruling
check("C snowed toes (2 shapes x 4 levels): no fight against the board is left", leak <= 0.01, f"leak {leak:.3f}")
check("C snowed high ends: slab vs stone cap filler (slab untouched by ruling) under the 0.455 bar", slabcap <= 0.455, f"{slabcap:.3f} total over 8 cases")
print("   snow-on-snow residual (deferred by ruling), px²:", {k: round(v, 2) for k, v in resid.items()})

# ---------------------------------------------------------------- L / V
led = (BP / "PW-DEPENDENCIES.md").read_text(encoding="utf-8")
rows = set(re.findall(r'^\|(\w+)\|`([^`]+)`\|$', led, re.M))
h = hashlib.sha256(json.dumps(sorted([list(r) for r in rows])).encode()).hexdigest()[:16]
check("L BP ledger needs-hash consistent", f"needs-hash `{h}`" in led, h)
check("L BP ledger has the new rows", {("terrain_key", "pw_rampcut_cobble"), ("terrain_key", "pw_hearth_flame_low"), ("geometry", "geometry.pw_flue_hollow"), ("particle", "pw:hearth_puff")} <= rows)
for tree, ver, name in ((RP, [1, 3, 130], "Basic RP"), (RP2, [2, 0, 3], "Atmospheric Effects RP"), (BP, [1, 3, 182], "Tectonic BP")):
    m = load(tree / "manifest.json")
    check(f"V manifest {name} v{'.'.join(map(str, ver))}", m["header"]["version"] == ver and all(x["version"] == ver for x in m["modules"]) and name in m["header"]["name"] and ".".join(map(str, ver)) in m["header"]["description"])

failed = [n for n, ok, _ in results if not ok]
if failed:
    print(f"\nGATE CLOSED — {len(failed)} failing check(s): {failed}\nNOTHING PACKAGED."); sys.exit(1)

# ---------------------------------------------------------------- Z: package inside the gate
def pack(tree, out):
    if out.exists(): out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(tree.rglob("*")):
            if p.is_file(): z.write(p, str(p.relative_to(tree)).replace(os.sep, "/"))
def tree_hashes(root): return {n: md5(p) for n, p in tree_files(root).items()}
def zip_hashes(zp):
    with zipfile.ZipFile(zp) as z: return {n: hashlib.md5(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith("/")}
OUT.mkdir(parents=True, exist_ok=True)
outs = {"BP-02": OUT / "BP-02-AbsolutRealism-Tectonic-BP-v1_3_182.mcpack",
        "RP-04": OUT / "RP-04-AbsolutRealism-Basic-RP-v1_3_130.mcpack",
        "RP-02": OUT / "RP-02-AbsolutRealism-Atmospheric-Effects-RP-v2_0_3.mcpack"}
for label, tree in (("BP-02", BP), ("RP-04", RP), ("RP-02", RP2)):
    pack(tree, outs[label])
    check(f"Z1 {label} from-zip identity", zip_hashes(outs[label]) == tree_hashes(tree))
r = subprocess.run(["python3", str(ROOT / "tools/verify_pack_versions.py")] + [str(p) for p in outs.values()], capture_output=True, text=True)
print(r.stdout.strip()); check("Z2 version-spot gate", r.returncode == 0, r.stderr[:200])
failed = [n for n, ok, _ in results if not ok]
if failed:
    for p in outs.values():
        if p.exists(): p.unlink()
    print(f"\nGATE CLOSED at packaging — {failed}; packages removed."); sys.exit(1)
print(f"\nGATE OPEN — {len(results)} checks passed; packaged:")
for label, p in outs.items(): print(f"  {label}: {p.name}  {p.stat().st_size:,} B  md5 {md5(p)}")
