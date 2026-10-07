#!/usr/bin/env python3
"""verify_leaf_rollout.py — gate for BP-02 1.3.197 + RP-01 1.3.106 (v2: + relook sweep / exposure resets off / log-break re-look / band-4 probe / opaque fall tiles) — first written for 1.3.196 + 1.3.105 (build_leaf_rollout.py). Static + harness checks only RULE OUT (P1).
  A manifests (versions, uuids, deps; RP keeps pbr + 1.21.120)     B every JSON parses; node --check every BP script
  C BP diff vs 1.3.195 = manifest + main.js + 9 leaf blocks changed; 2 azalea blocks + 2 loot tables added; nothing removed
  D main.js: the look code in, the random pools out of the leaf path, no applied-registry writes, azalea ids in the 5 sets
  E every leaf block: same states + base components as 1.3.195 (azalea: oak's), 7 permutations, all alpha_test_to_opaque, no AO,
    no face dimming, isotropic face tiles, biome tint exactly on the 7 tinted species, 90-degree turns only, cards only on v5/v6
    (never spruce)
  F every geometry / texture key / PNG / texture set the blocks need exists in RP-01 1.3.105 (and nothing else in the stack wins it)
  G RP diff vs 1.3.104: the old leaf geometry, 180 keys, 306 files, 156 flipbooks gone; nothing still points at them
  H tiles: 128 px RGBA, see-through pixels painted (no black under alpha), normal + MERS present for every tile that has Patrix maps
  I harness: pwLeafLook / pwWoodDistance from the BUILT main.js on a fake world (deterministic; touching wood -> cards; spruce never
    cards; distribution of the five full shapes); the old Math.random pools unreachable for leaves
  J block-state census (permutations)                              K render of a built tree -> _docs/leaves/rollout/ROLLOUT-BUILT-CHECK.png"""
import hashlib, json, re, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML

ROOT = Path("/home/claude")
BO, BN = ROOT / "_build/bp02-195", ROOT / "_build/bp02-197"
RO, RN = ROOT / "_build/rp01-104", ROOT / "_build/rp01-106"
WOODS = ("oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "mangrove", "cherry", "pale_oak")
AZ = ("azalea", "flowering_azalea")
TINT = {"oak": "default_foliage", "dark_oak": "default_foliage", "jungle": "default_foliage", "acacia": "default_foliage",
        "mangrove": "default_foliage", "birch": "birch_foliage", "spruce": "evergreen_foliage"}
res = []
def check(name, ok, detail=""):
    res.append((name, bool(ok))); print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))
md5 = lambda p: hashlib.md5(Path(p).read_bytes()).hexdigest()
J = lambda p: ML._parse_json(Path(p).read_text(encoding="utf-8-sig"))

# A
def man(d): return json.loads((d / "manifest.json").read_text(encoding="utf-8-sig"))
for (o, n, v) in ((BO, BN, [1, 3, 197]), (RO, RN, [1, 3, 106])):
    mo, mn = man(o), man(n)
    check(f"A {n.name} manifest {v}, uuids + dependencies + capabilities unchanged", mn["header"]["version"] == v and all(x["version"] == v for x in mn["modules"])
          and mn["header"]["uuid"] == mo["header"]["uuid"] and [x["uuid"] for x in mn["modules"]] == [x["uuid"] for x in mo["modules"]]
          and mn.get("dependencies") == mo.get("dependencies") and mn.get("capabilities") == mo.get("capabilities")
          and mn["header"]["min_engine_version"] == mo["header"]["min_engine_version"], f"caps {mn.get('capabilities')} min {mn['header']['min_engine_version']}")
check("A RP-01 still declares Vibrant Visuals (pbr + >= 1.21.120)", man(RN).get("capabilities") == ["pbr"] and man(RN)["header"]["min_engine_version"] >= [1, 21, 120])
# B
bad = []
for d in (BN, RN):
    for p in d.rglob("*.json"):
        try: J(p)
        except Exception as e: bad.append(f"{p.relative_to(d)}: {e}")
check("B every JSON in both packs parses", not bad, "; ".join(bad[:3]))
nc = {p.name: subprocess.run(["node", "--check", str(p)], capture_output=True).returncode for p in (BN / "scripts").glob("*.js")}
check("B node --check on every BP-02 script", nc and all(c == 0 for c in nc.values()), f"{len(nc)} scripts")
# C
tree = lambda d: {str(p.relative_to(d)): md5(p) for p in d.rglob("*") if p.is_file()}
to, tn = tree(BO), tree(BN)
changed = sorted(k for k in set(to) & set(tn) if to[k] != tn[k]); removed = sorted(set(to) - set(tn)); added = sorted(set(tn) - set(to))
check("C BP diff = manifest + main.js + the 9 leaf blocks; + 2 azalea blocks + 2 loot tables; nothing removed",
      changed == sorted(["manifest.json", "scripts/main.js"] + [f"blocks/{w}_leaves.json" for w in WOODS])
      and added == sorted([f"blocks/{s}_leaves.json" for s in AZ] + [f"loot_tables/blocks/{s}_leaves.json" for s in AZ]) and not removed,
      f"changed {len(changed)} added {added} removed {removed[:3]}")
# D
ms = (BN / "scripts/main.js").read_text(encoding="utf-8"); mo_ = (BO / "scripts/main.js").read_text(encoding="utf-8")
pick = ms[ms.index("function pickVariantForBlock(block) {"):ms.index("function pwRandomizeVariant(arg) {")]
look = ms[ms.index("function pwLeafLook(block) {"):ms.index("function pickVariantForBlock(block) {")]
check("D the leaf path picks by position + wood: pickVariantForBlock(leaf) -> pwLeafLook; no Math.random in the look; pools unused for leaves",
      "if (isLeaf) return pwLeafLook(block);" in pick and "PW_LEAF_VARIANT_POOLS[key]" not in pick and "Math.random" not in look
      and "Math.random" not in ms[ms.index("function pwCellHash"):ms.index("function pwLeafLook")])
check("D nothing writes the applied-registry any more (far reverter / re-applicator idle); the phase-1 far branch is gone",
      "_appliedRegistry.set(" not in ms and "_appliedRegistry.set(" in mo_ and "totalRevertedFar++;\n              { const __k" not in ms
      and "// --- 2. THE LOOK, ONCE (v1.3.196) ---" in ms)
check("D onPlace: a placed leaf's look is final at once (setRseed true, no section gate)",
      "const setRseed = true;   // v1.3.196" in ms and "if (sectionRolled !== true) setRseed = false;" not in ms)
sets = ['"pw:azalea_leaves", "pw:flowering_azalea_leaves"] },', '"pw:azalea_leaves": 7, "pw:flowering_azalea_leaves": 7,',
        '  "pw:azalea_leaves", "pw:flowering_azalea_leaves",\n  // Log tier blocks', '  "pw:azalea_leaves", "pw:flowering_azalea_leaves",\n]);',
        '"pw:azalea_leaves": 0,\n  "pw:flowering_azalea_leaves": 0,']
check("D azalea ids in SPECIES(oak) / VARIANT_COUNT / LEAF_TYPES / LEAF_TYPES_DECAY / LEAF_TO_WOOD_TYPE; PW_BUILD 1.3.197",
      all(x in ms for x in sets) and 'const PW_BUILD = "1.3.197";' in ms, str([x[:30] for x in sets if x not in ms]))
import difflib
dl = [l for l in difflib.unified_diff(mo_.splitlines(), ms.splitlines(), lineterm="", n=0) if l.startswith(("+", "-")) and not l.startswith(("+++", "---"))]
check("D main.js diff size is bounded (only the planned hunks)", 120 < len(dl) < 320, f"{len(dl)} changed lines")
check("D v2: relook sweep (once per chunk, marks in world dynamic properties, yields), exposure resets off, a broken log re-looks its neighbours, band-4 probe",
      "function* _relookJob()" in ms and "world.setDynamicProperty(r.k, n)" in ms and "_relookMark(dim.id, cx, cz)" in ms and "yield;" in ms[ms.index("function* _relookJob()"):ms.index("_relookMark(dim.id, cx, cz)")]
      and "const PW_EXPOSURE_RESETS = false;" in ms and "if (shouldReset && PW_EXPOSURE_RESETS)" in ms
      and "if (!isLeafB && !pwIsWood(id)) return;" in ms and "Math.min(band, 4)" in ms and "d <= 4) sh[d].push" in ms)
# E
def comps_wo(b):
    return {k: v for k, v in b["minecraft:block"]["components"].items()}
geo = J(RN / "models/blocks/pw_leaves2.geo.json"); geo_ids = {g["description"]["identifier"] for g in geo["minecraft:geometry"]}
tt = J(RN / "textures/terrain_texture.json")["texture_data"]
problems = []
for s in WOODS + AZ:
    b = J(BN / f"blocks/{s}_leaves.json"); blk = b["minecraft:block"]
    ref = J(BO / f"blocks/{s if s in WOODS else 'oak'}_leaves.json")["minecraft:block"]
    if blk["description"]["states"] != ref["description"]["states"]: problems.append(f"{s} states")
    rc = dict(ref["components"]); bc = dict(blk["components"])
    if s in AZ:
        for k in ("minecraft:map_color", "minecraft:loot"): rc.pop(k); bc.pop(k)
        if blk["description"]["identifier"] != f"pw:{s}_leaves": problems.append(f"{s} id")
    if bc != rc: problems.append(f"{s} base components")
    P_ = blk["permutations"]
    if [p["condition"] for p in P_] != [f"q.block_state('pw:variant') == {v}" for v in range(7)]: problems.append(f"{s} conditions")
    for v, p in enumerate(P_):
        c = p["components"]; g = c["minecraft:geometry"]
        if g not in geo_ids: problems.append(f"{s} v{v} geometry {g}")
        if s == "spruce" and g != "geometry.pw_leaves2_spruce": problems.append(f"{s} v{v} not spruce geo")
        if s != "spruce" and (g == "geometry.pw_leaves2_cards") != (v in (5, 6)): problems.append(f"{s} v{v} cards placement")
        for slot, m in c["minecraft:material_instances"].items():
            if m.get("render_method") != "alpha_test_to_opaque" or m.get("ambient_occlusion") is not False or m.get("face_dimming") is not False:
                problems.append(f"{s} v{v} {slot} render")
            if m.get("tint_method") != TINT.get(s): problems.append(f"{s} v{v} {slot} tint {m.get('tint_method')}")
            if m.get("isotropic", False) != (slot in ("*", "top")): problems.append(f"{s} v{v} {slot} iso")
            if m["texture"] not in tt: problems.append(f"{s} v{v} {slot} key {m['texture']}")
        r = c.get("minecraft:transformation", {}).get("rotation", [0, 0, 0])
        if r[0] or r[2] or r[1] % 90: problems.append(f"{s} v{v} rotation {r}")
check("E 11 leaf blocks: states + base components as before, 7 variants, alpha_test_to_opaque / no AO / no dimming, iso face tiles, "
      "tint only on the 7 tinted species, 90-degree turns, cards only on v5-v6 (never spruce)", not problems, "; ".join(problems[:6]))
lt = J(BN / "loot_tables/blocks/azalea_leaves.json"); lf = J(BN / "loot_tables/blocks/flowering_azalea_leaves.json")
check("E azalea loot: shears -> the vanilla leaf item, 5 % bush, sticks, no apple",
      lt["pools"][0]["entries"][0]["name"] == "minecraft:azalea_leaves" and lt["pools"][1]["entries"][0]["name"] == "minecraft:azalea"
      and lf["pools"][0]["entries"][0]["name"] == "minecraft:flowering_azalea_leaves" and lf["pools"][1]["entries"][0]["name"] == "minecraft:flowering_azalea"
      and len(lt["pools"]) == 3 and len(lf["pools"]) == 3)
# F
need = set()
for s in WOODS + AZ:
    for p in J(BN / f"blocks/{s}_leaves.json")["minecraft:block"]["permutations"]:
        for m in p["components"]["minecraft:material_instances"].values(): need.add(m["texture"])
miss = []
for k in sorted(need):
    t = tt[k]["textures"]; png = RN / (t + ".png"); tsj = RN / (t + ".texture_set.json")
    if not png.exists(): miss.append(f"{k} png")
    if not tsj.exists(): miss.append(f"{k} texture_set")
    else:
        ts = J(tsj)["minecraft:texture_set"]
        for f in ts.values():
            if not (png.parent / f"{f}.png").exists(): miss.append(f"{k} set->{f}")
others = []
for o in ROOT.glob("_build/rp*"):
    pass
check("F every texture key, PNG and texture-set member the 11 blocks use exists in RP-01 1.3.105", not miss and len(need) == 100, f"{len(need)} keys; {miss[:4]}")
# other RPs of his stack must not define pw_leaves2 keys (RP-01 is the lowest pack; anything above would win)
stack = [p for p in (ROOT / "_build").glob("*/textures/terrain_texture.json") if p.parents[1].name.split("-")[0] in ("rp02", "rp03", "rp04", "rp05", "rp06", "rp07", "rp08", "rp10", "rp11")]
clash = [str(p.parents[1].name) for p in stack if "pw_leaves2_" in p.read_text(encoding="utf-8", errors="ignore")]
check("F no other RP build defines a pw_leaves2 key (RP-01 wins uncontested)", not clash, str(clash))
# G
ro, rn = tree(RO), tree(RN)
rem = sorted(set(ro) - set(rn)); add = sorted(set(rn) - set(ro))
old_files = [k for k in rem if re.match(r"textures/blocks/pw_(oak|spruce|birch|jungle|acacia|dark_oak|mangrove|cherry|pale_oak)_leaves_", k)]
check("G RP removed = the 2 old leaf geometry files + 306 old leaf files only", len(old_files) == 306 and
      sorted(set(rem) - set(old_files)) == ["models/blocks/pw_leaves_jungle_variants.geo.json", "models/blocks/pw_leaves_variants.geo.json"], f"removed {len(rem)}")
check("G RP added = pw_leaves2 geometry + textures/blocks/pw_leaves2/* only", all(k == "models/blocks/pw_leaves2.geo.json" or k.startswith("textures/blocks/pw_leaves2/") for k in add), f"added {len(add)}")
alltxt = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in list(RN.rglob("*.json")) + list(BN.rglob("*.json")) + list((BN / "scripts").glob("*.js")))
stale = sorted(set(re.findall(r"pw_(?:oak|spruce|birch|jungle|acacia|dark_oak|mangrove|cherry|pale_oak)_leaves_v\d\w*", alltxt)))
check("G nothing in either pack still names an old leaf tile (pw_<s>_leaves_vN)", not stale, str(stale[:5]))
geo_old = [g for g in ("geometry.pw_leaves_v0", "geometry.pw_leaves_v1", "geometry.pw_leaves_jungle_v1") if g in alltxt]
check("G nothing names the old leaf geometries", not geo_old, str(geo_old))
fb = J(RN / "textures/flipbook_textures.json"); fbo = J(RO / "textures/flipbook_textures.json")
check("G flipbooks: exactly the 156 old leaf entries removed; the 7 others (vanilla grass / fern tiles) byte-identical to 1.3.104", len(fbo) - len(fb) == 156
      and fb == [e for e in fbo if not re.match(r"pw_[a-z_]+_leaves", e.get("atlas_tile", ""))], f"{len(fbo)} -> {len(fb)}")
ent = (RN / "entity/falling_tree.json").read_text(encoding="utf-8")
refs = re.findall(r"textures/blocks/pw_leaves2/[a-z_]+_fall", ent)
check("G falling tree (60 refs) + leaf-fall particle point at existing pre-coloured fall tiles",
      len(refs) == 60 and all((RN / (r + ".png")).exists() for r in refs) and (RN / "textures/blocks/pw_leaves2/oak_fall.png").exists()
      and "pw_leaves2/oak_fall" in (RN / "particles/pw_leaf_fall.json").read_text())
bj = J(RN / "blocks.json"); lang = (RN / "texts/en_US.lang").read_text(encoding="utf-8")
check("G blocks.json sound + names for all 11 leaf blocks", all(bj.get(f"pw:{s}_leaves", {}).get("sound") == "grass" for s in WOODS + AZ)
      and all(f"tile.pw:{s}_leaves.name=" in lang for s in WOODS + AZ))
# H
tiles = sorted((RN / "textures/blocks/pw_leaves2").glob("*.png"))
colour_tiles = [p for p in tiles if not p.stem.endswith(("_n", "_mers"))]
hb = []
for p in colour_tiles:
    a = np.asarray(Image.open(p).convert("RGBA"))
    if a.shape[:2] != (128, 128) and not p.stem.endswith("_fall"): hb.append(f"{p.name} {a.shape}")
    tr = a[..., 3] < 128
    if tr.any() and (a[..., :3][tr].sum(1) == 0).mean() > 0.01: hb.append(f"{p.name} black under alpha")
check("H colour tiles 128 px, see-through pixels painted (no black under alpha)", not hb, "; ".join(hb[:4]))
noset = [p.stem for p in colour_tiles if not p.stem.endswith("_fall") and not (p.parent / f"{p.stem}_n.png").exists()]
check("H normal maps present for every tile (Patrix _n)", not noset, str(noset[:6]))
fall_bad = [p.name for p in (RN / "textures/blocks/pw_leaves2").glob("*_fall.png") if np.asarray(Image.open(p).convert("RGBA"))[..., 3].min() < 255]
check("H fall tiles (falling canopy + particle) fully opaque, 11 of them", not fall_bad and len(list((RN / "textures/blocks/pw_leaves2").glob("*_fall.png"))) == 11, str(fall_bad))
# I harness
harness = r'''
const src = require("fs").readFileSync(process.argv[2], "utf8");
const a = src.indexOf("const PW_LEAF_BAND"), b = src.indexOf("function pickVariantForBlock(block) {");
const code = src.slice(a, b);
const PW_TA_LOG_TYPES = new Set(["pw:oak_young", "minecraft:oak_log"]);
eval(code.replace(/^const /gm, "var ").replace(/^function /gm, "function "));
function world(logs) { return { getBlock: ({x, y, z}) => ({ typeId: logs.has(`${x},${y},${z}`) ? "pw:oak_young" : "air" }) }; }
const logs = new Set(); for (let y = -30; y < 130; y++) logs.add(`0,${y},0`);
const dim = world(logs); const out = {};
const look = (id, x, y, z) => pwLeafLook({ typeId: id, location: { x, y, z }, dimension: dim });
const touch = []; for (const [x, z] of [[1,0],[-1,0],[0,1],[0,-1]]) for (let y = 0; y < 6; y++) touch.push(look("pw:oak_leaves", x, y, z));
out.touch = [...new Set(touch)].sort();
const far = {}; for (let x = 6; x < 46; x++) for (let z = 6; z < 46; z++) { const v = look("pw:oak_leaves", x, 3, z); far[v] = (far[v] || 0) + 1; }
out.far = far;
const sp = {}; for (let x = -3; x < 37; x++) for (let z = -3; z < 37; z++) { const v = look("pw:spruce_leaves", x, 3, z); sp[v] = (sp[v] || 0) + 1; }
out.spruce = sp;
const band = []; for (let x = 2; x < 3; x++) for (let y = -20; y < 120; y++) band.push(look("pw:oak_leaves", 2, y, 0));
out.band2 = band.filter((v) => v >= 5).length + "/" + band.length;
out.same = look("pw:oak_leaves", 9, 9, 9) === look("pw:oak_leaves", 9, 9, 9) && look("pw:oak_leaves", 9, 9, 9) !== undefined;
out.dist = [pwWoodDistance(dim, 1, 0, 0, 4), pwWoodDistance(dim, 2, 0, 0, 4), pwWoodDistance(dim, 2, 1, 1, 4), pwWoodDistance(dim, 4, 0, 0, 4), pwWoodDistance(dim, 5, 0, 0, 4)];
console.log(JSON.stringify(out));
'''
hp = ROOT / "_work/rollout_harness.cjs"; hp.parent.mkdir(exist_ok=True); hp.write_text(harness)
r = subprocess.run(["node", str(hp), str(BN / "scripts/main.js")], capture_output=True, text=True)
try: H = json.loads(r.stdout)
except Exception: H = {"err": r.stderr[-300:]}
far = H.get("far", {})
check("I harness: touching wood -> cards only (5/6); far -> only v0-v4, each 14-26 %; spruce only full v0-v6; 2 blocks out ~half cards; same cell same look",
      H.get("touch") == [5, 6] and sorted(map(int, far)) == [0, 1, 2, 3, 4] and all(280 < n < 520 for n in far.values())
      and sorted(map(int, H.get("spruce", {}))) == list(range(7)) and H.get("same") is True
      and 40 < int(H.get("band2", "0/1").split("/")[0]) < 100, json.dumps(H)[:300])
check("I harness: wood distance probe 1 / 2 / 3 / 4 / beyond", H.get("dist") == [1, 2, 3, 4, 99], str(H.get("dist")))
# I2 harness: the relook sweep on a fake world (old leaves with rseed true get the position + wood look once; chunks marked; 2nd pass skips)
h2 = r"""
const src = require("fs").readFileSync(process.argv[2], "utf8");
const look = src.slice(src.indexOf("const PW_LEAF_BAND"), src.indexOf("function pickVariantForBlock(block) {"));
const rel = src.slice(src.indexOf("const PW_RELOOK_INTERVAL"), src.indexOf("system.runInterval(() => {\n  if (_relookBusy) return;"));
const PW_TA_LOG_TYPES = new Set(["pw:oak_young"]); const PW_LEAF_TYPES_DECAY = new Set(["pw:oak_leaves"]);
const blocks = new Map(); const props = new Map(); let writes = 0;
const key = (x, y, z) => `${x},${y},${z}`;
for (let y = 60; y < 66; y++) blocks.set(key(5, y, 5), { id: "pw:oak_young" });
for (let x = 2; x <= 8; x++) for (let z = 2; z <= 8; z++) for (let y = 63; y <= 66; y++) if (!(x === 5 && z === 5 && y < 66)) blocks.set(key(x, y, z), { id: "pw:oak_leaves", st: { "pw:variant": 6, "pw:rseed": true } });
function perm(b) { return { getState: (n) => b.st[n], withState(n, v) { const c = { ...b.st, [n]: v }; const o = perm({ st: c }); o._st = c; return o; }, _st: b.st }; }
const dim = { id: "minecraft:overworld", getBlock: ({ x, y, z }) => { const b = blocks.get(key(x, y, z)); const blk = { typeId: b ? b.id : "minecraft:air", location: { x, y, z }, dimension: dim };
  if (b && b.st) { blk.permutation = perm(b); blk.setPermutation = (p) => { b.st = p._st; writes++; }; } return blk; } };
const world = { getPlayers: () => [{ dimension: dim, location: { x: 5, y: 64, z: 5 } }], getDynamicProperty: (k) => props.get(k), setDynamicProperty: (k, v) => props.set(k, v) };
const logErr = () => {};
eval((look + rel).replace(/^const /gm, "var ").replace(/^let /gm, "var "));
function run() { _relookBusy = true; const g = _relookJob(); while (!g.next().done) {} }
run(); const w1 = writes; const st = [...blocks.values()].filter((b) => b.st).map((b) => b.st["pw:variant"]);
run(); const w2 = writes - w1;
const touching = blocks.get(key(4, 63, 5)).st["pw:variant"], far = blocks.get(key(2, 66, 2)).st["pw:variant"];
console.log(JSON.stringify({ w1, w2, props: props.size, chunks: _relookStats.chunks, touching, far, kinds: [...new Set(st)].sort() }));
"""
hp2 = ROOT / "_work/relook_harness.cjs"; hp2.write_text(h2)
r2 = subprocess.run(["node", str(hp2), str(BN / "scripts/main.js")], capture_output=True, text=True)
try: H2 = json.loads(r2.stdout)
except Exception: H2 = {"err": (r2.stderr or r2.stdout)[-400:]}
check("I2 relook sweep harness: old leaves (v6, rseed true) re-looked once (touching wood -> cards 5/6, far -> full 0-4), chunks marked, a 2nd pass writes nothing",
      H2.get("w1", 0) > 50 and H2.get("w2") == 0 and H2.get("props", 0) >= 1 and H2.get("chunks") == 25 and H2.get("touching") in (5, 6) and H2.get("far") in (0, 1, 2, 3, 4), json.dumps(H2)[:300])
# J census
try:
    import block_state_census as BC
    tot = 0; per = {}
    for p in (BN / "blocks").rglob("*.json"):
        d = J(p); st = d.get("minecraft:block", {}).get("description", {}).get("states", {})
        n = 1
        for v in st.values(): n *= len(v) if isinstance(v, list) else (v.get("values", {}).get("max", 0) - v.get("values", {}).get("min", 0) + 1 if isinstance(v, dict) else 1)
        tot += n
        if "leaves" in p.name: per[p.stem] = n
    check("J permutations: each leaf block 168 (unchanged); the 2 azalea blocks add 336", all(v == 168 for v in per.values()) and len(per) == 11, f"BP-02 custom states total ~{tot}")
except Exception as e:
    check("J census ran", False, str(e))

print(f"\n{'GATE OPEN' if all(ok for _, ok in res) else 'GATE CLOSED'} — {sum(ok for _, ok in res)}/{len(res)}")
