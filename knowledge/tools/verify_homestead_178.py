#!/usr/bin/env python3
"""verify_homestead_178.py — SHIP GATE for BP-02 v1.3.178 / RP-04 v1.3.128 / RP-02 v2.0.2 (HOMESTEAD).

Static checks rule OUT (#77); only Abs0lum's witness rules IN.  Packaging happens ONLY inside this gate
(D-101): every check must pass before a single .mcpack is written to /mnt/user-data/outputs.

Checks
  J   every JSON in the three trees parses
  B1  new block identifiers are unique and collide with nothing in BP-02
  B2  every state has <= 16 values (16-value law)
  B3  one collision box (or false), origin y >= 0, inside [-8..8]x[0..16]x[-8..8]
  B4  every geometry id referenced resolves to RP-04 .128 models (or minecraft:geometry.full_block)
  B5  for every (block, permutation-context) the geometry's material_instance names are covered by the
      material_instances in force (no "Missing referenced asset")
  B6  every texture key referenced resolves in RP-04 .128 terrain_texture.json (fire_0 incl.), and the
      key's path(s) exist as PNG in the RP-04 tree
  B7  permutation conditions only reference declared states; rotation table == roof45's
  B8  custom_components used by blocks are registered in the scripts
  R   recipes parse, result ids exist, patterns well formed, no duplicate recipe identifiers
  G   geometry: identifiers unique, uv_size <= 16, face names valid, texture_width 16
  S   node --check on every changed script; unit tests pass; materials module == block ids;
      main.js import present exactly once; @minecraft/server pin unchanged (Lesson #53)
  T   textures: 128x128 RGBA, texture sets reference existing files; lang has one line per new block
  P   particles/fog parse, identifiers as expected, sprite exists
  I   byte identity: every file carried from the source packs is byte-identical except the allowed set
  Z   package -> from-zip identity -> version-spot gate (verify_pack_versions.py)
"""
import json, os, re, sys, hashlib, zipfile, subprocess, glob, io
from pathlib import Path
from PIL import Image

ROOT = Path("/home/claude")
BP_SRC, RP04_ZIP, RP02_ZIP = ROOT / "_packs/bp02-177", ROOT / "_packs/RP-04-v1_3_127.mcpack", ROOT / "_packs/RP-02-v2_0_1.mcpack"
BP, RP04, RP02 = ROOT / "_build/bp02-178", ROOT / "_build/rp04-128", ROOT / "_build/rp02-202"
OUT = Path("/mnt/user-data/outputs")
sys.path.insert(0, str(ROOT / "tools"))
from homestead_materials import OUTER, INNER16, RAFTER_WOODS  # noqa: E402

NEW_BLOCKS = [f"pw:hearth_{m}" for m in OUTER] + [f"pw:flue_{m}" for m in OUTER] + [f"pw:wall_{m}" for m in OUTER] + [f"pw:rafter45_{w}" for w in RAFTER_WOODS]
ROT = {"north": [0, 0, 0], "west": [0, 90, 0], "south": [0, 180, 0], "east": [0, -90, 0]}
FACES = {"north", "south", "east", "west", "up", "down"}

results = []
def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))
    return bool(ok)

def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8-sig"))

# ---------------------------------------------------------------- J: parse everything (strict for files we wrote; carried files reported)
def _src_names():
    names = {"BP-02": set(), "RP-04": set(), "RP-02": set()}
    for p in BP_SRC.rglob("*"):
        if p.is_file(): names["BP-02"].add(str(p.relative_to(BP_SRC)).replace(os.sep, "/"))
    for label, zp in (("RP-04", RP04_ZIP), ("RP-02", RP02_ZIP)):
        with zipfile.ZipFile(zp) as z: names[label] = set(n for n in z.namelist() if not n.endswith("/"))
    return names
SRC_NAMES = _src_names()
bad, carried_bad = [], []
for label, tree in (("BP-02", BP), ("RP-04", RP04), ("RP-02", RP02)):
    for p in tree.rglob("*.json"):
        rel = str(p.relative_to(tree)).replace(os.sep, "/")
        try: load(p)
        except Exception as e:
            (carried_bad if rel in SRC_NAMES[label] else bad).append(f"{label}/{rel}: {str(e)[:60]}")
check("J  every JSON we wrote parses strictly", not bad, "; ".join(bad[:5]))
if carried_bad: print(f"note: {len(carried_bad)} carried file(s) are not strict JSON (Bedrock-lenient, untouched, byte-identical): " + "; ".join(carried_bad[:3]))

# ---------------------------------------------------------------- blocks
blocks = {}
for p in (BP / "blocks").glob("*.json"):
    d = load(p); blocks[d["minecraft:block"]["description"]["identifier"]] = (p, d["minecraft:block"])
ids = [load(p)["minecraft:block"]["description"]["identifier"] for p in (BP / "blocks").glob("*.json")]
check("B1 identifiers unique + all new blocks present", len(ids) == len(set(ids)) and all(i in blocks for i in NEW_BLOCKS), f"{len(ids)} blocks, {len(NEW_BLOCKS)} new")
old_ids = {load(p)["minecraft:block"]["description"]["identifier"] for p in (BP_SRC / "blocks").glob("*.json")}
check("B1b no collision with v1.3.177 identifiers", not (set(NEW_BLOCKS) & old_ids))

bad = [f"{i}:{s}" for i in NEW_BLOCKS for s, v in blocks[i][1]["description"].get("states", {}).items() if len(v) > 16]
check("B2 16-value law", not bad, "; ".join(bad[:5]))

def box_ok(b):
    if b is False: return True
    o, s = b["origin"], b["size"]
    return o[1] >= 0 and -8 <= o[0] and o[0] + s[0] <= 8 and o[1] + s[1] <= 16 and -8 <= o[2] and o[2] + s[2] <= 8
bad = []
for i in NEW_BLOCKS:
    c = blocks[i][1]["components"]
    cb = c.get("minecraft:collision_box", "MISSING")
    if cb == "MISSING" or not box_ok(cb): bad.append(i)
    for pm in blocks[i][1].get("permutations", []):
        if "minecraft:collision_box" in pm.get("components", {}): bad.append(i + ":perm-collision")
check("B3 single collision box law (y>=0, in-cell, never per-permutation)", not bad, "; ".join(bad[:5]))

# geometry ids available in RP-04 .128
geos = {}
for p in (RP04 / "models/blocks").glob("*.json"):
    try: d = load(p)
    except Exception: continue
    for g in d.get("minecraft:geometry", []):
        geos[g["description"]["identifier"]] = g
def geo_ref(c):
    g = c.get("minecraft:geometry")
    if isinstance(g, str): return g
    if isinstance(g, dict): return g.get("identifier")
    return None
bad = []
for i in NEW_BLOCKS:
    refs = [geo_ref(blocks[i][1]["components"])] + [geo_ref(pm.get("components", {})) for pm in blocks[i][1].get("permutations", [])]
    for r in refs:
        if r is None: continue
        if r == "minecraft:geometry.full_block": continue
        if r not in geos: bad.append(f"{i}->{r}")
check("B4 geometry references resolve", not bad, "; ".join(bad[:5]))

def geo_instances(gid):
    if gid == "minecraft:geometry.full_block": return set()
    names = set()
    for b in geos[gid]["bones"]:
        for c in b.get("cubes", []):
            for f, u in c.get("uv", {}).items():
                names.add(u.get("material_instance", "*"))
    return names
bad = []
for i in NEW_BLOCKS:
    blk = blocks[i][1]
    base_c = blk["components"]
    contexts = [("base", base_c)]
    for pm in blk.get("permutations", []):
        merged = dict(base_c); merged.update(pm.get("components", {}))
        contexts.append((pm["condition"], merged))
    for name, c in contexts:
        g = geo_ref(c)
        if g is None: continue
        need = geo_instances(g); have = set(c.get("minecraft:material_instances", {}).keys())
        if not need <= have: bad.append(f"{i} [{name[:40]}] missing {sorted(need - have)}")
check("B5 every geometry material_instance is defined in every context", not bad, "; ".join(bad[:3]))

tt = load(RP04 / "textures/terrain_texture.json")["texture_data"]
def key_paths(v):
    t = v.get("textures"); out = []
    for e in (t if isinstance(t, list) else [t]):
        if isinstance(e, str): out.append(e)
        elif isinstance(e, dict):
            if "variations" in e: out += [vv.get("path") if isinstance(vv, dict) else vv for vv in e["variations"]]
            else: out.append(e.get("path"))
    return [p for p in out if p]
used_keys = set()
for i in NEW_BLOCKS:
    blk = blocks[i][1]
    for c in [blk["components"]] + [pm.get("components", {}) for pm in blk.get("permutations", [])]:
        for k, v in c.get("minecraft:material_instances", {}).items(): used_keys.add(v["texture"])
missing_keys = sorted(k for k in used_keys if k not in tt)
missing_png = []
for k in used_keys:
    if k in tt:
        for pth in key_paths(tt[k]):
            if not (RP04 / (pth + ".png")).exists() and not (RP04 / (pth + ".tga")).exists(): missing_png.append(f"{k}->{pth}")
check("B6 texture keys resolve in RP-04 .128", not missing_keys, "missing: " + ", ".join(missing_keys[:8]))
check("B6b every path behind those keys exists (no dangling variation)", not missing_png, "; ".join(missing_png[:5]))

bad = []
for i in NEW_BLOCKS:
    blk = blocks[i][1]
    states = set(blk["description"].get("states", {}).keys())
    traits = blk["description"].get("traits", {})
    if "minecraft:placement_direction" in traits: states.add("minecraft:cardinal_direction")
    for pm in blk.get("permutations", []):
        for s in re.findall(r"q\.block_state\('([^']+)'\)", pm["condition"]):
            if s not in states: bad.append(f"{i}:{s}")
        tr = pm.get("components", {}).get("minecraft:transformation")
        if tr:
            d = re.search(r"cardinal_direction'\) == '(\w+)'", pm["condition"]).group(1)
            if tr["rotation"] != ROT[d]: bad.append(f"{i}:rot:{d}")
check("B7 conditions reference declared states; rotation table == roof45", not bad, "; ".join(bad[:5]))

scripts_txt = "".join(p.read_text(encoding="utf-8") for p in (BP / "scripts").glob("*.js"))
registered = set(re.findall(r'registerCustomComponent\("([^"]+)"', scripts_txt))
used = set()
for i in NEW_BLOCKS: used |= set(blocks[i][1]["components"].get("minecraft:custom_components", []))
check("B8 custom components registered", used <= registered, f"used {sorted(used)} registered {sorted(registered & used)}")

# ---------------------------------------------------------------- recipes
rids = []; bad = []
for p in (BP / "recipes").glob("pw_*.json"):
    d = load(p); r = d.get("minecraft:recipe_shaped") or d.get("minecraft:recipe_shapeless")
    if not r: continue
    rid = r["description"]["identifier"]; rids.append(rid)
    res = r["result"]["item"]
    if res.startswith("pw:") and res not in blocks and not (BP / "items" / (res.split(":")[1] + ".json")).exists(): bad.append(f"{rid}: result {res} unknown")
    if "pattern" in r:
        rows = r["pattern"]
        if not (1 <= len(rows) <= 3 and len({len(x) for x in rows}) == 1 and len(rows[0]) <= 3): bad.append(f"{rid}: pattern shape")
        for ch in set("".join(rows)) - {" "}:
            if ch not in r["key"]: bad.append(f"{rid}: key {ch} undefined")
dups = {x for x in rids if rids.count(x) > 1}
check("R  recipes well formed, results exist, identifiers unique", not bad and not dups, "; ".join(bad[:3]) + (" dups: " + ",".join(dups) if dups else ""))
check("R2 one recipe per new block", all(i in rids for i in NEW_BLOCKS), f"{sum(i in rids for i in NEW_BLOCKS)}/{len(NEW_BLOCKS)}")

# ---------------------------------------------------------------- geometry file
gf = load(RP04 / "models/blocks/pw_homestead.geo.json")
gids = [g["description"]["identifier"] for g in gf["minecraft:geometry"]]
bad = []
for g in gf["minecraft:geometry"]:
    if g["description"]["texture_width"] != 16: bad.append("tw")
    for b in g["bones"]:
        for c in b["cubes"]:
            for f, u in c["uv"].items():
                if f not in FACES: bad.append(f"face {f}")
                if u["uv_size"][0] > 16 or u["uv_size"][1] > 16: bad.append("uv>16")
                if u["uv"][0] + u["uv_size"][0] > 16.0001 or u["uv"][1] + u["uv_size"][1] > 16.0001: bad.append("uv overflow")
            if any(s == 0 for s in c["size"]) and not c.get("inflate"): bad.append("zero-axis box without inflate (#175)")
all_geo_ids = [g["description"]["identifier"] for p in (RP04 / "models/blocks").glob("*.json") for g in load(p).get("minecraft:geometry", [])]
check("G  geometry ids unique across RP-04, faces/uv valid, #175 inflate", not bad and len(all_geo_ids) == len(set(all_geo_ids)) and len(gids) == 6, "; ".join(sorted(set(bad))[:5]))

# ---------------------------------------------------------------- scripts
bad = []
for f in ("pw_homestead.js", "pw_homestead_logic.js", "pw_homestead_materials.js", "main.js"):
    r = subprocess.run(["node", "--check", str(BP / "scripts" / f)], capture_output=True, text=True)
    if r.returncode != 0: bad.append(f"{f}: {r.stderr.strip()[:200]}")
check("S1 node --check", not bad, "; ".join(bad))
r = subprocess.run(["node", str(ROOT / "tools/homestead_src/test_logic.mjs")], capture_output=True, text=True)
check("S2 logic unit tests", r.returncode == 0 and "tests passed" in r.stdout, r.stdout.strip().splitlines()[-1] if r.stdout else r.stderr[:200])
mats = (BP / "scripts/pw_homestead_materials.js").read_text()
mods = {k: json.loads(v) for k, v in re.findall(r"export const (\w+) = (\[.*?\]);", mats)}
check("S3 materials module == block ids", set(mods["HEARTH_IDS"] + mods["FLUE_IDS"] + mods["WALL_IDS"] + mods["RAFTER_IDS"]) == set(NEW_BLOCKS) and mods["INNER16"] == list(INNER16))
mj = (BP / "scripts/main.js").read_text()
check("S4 main.js imports pw_homestead.js exactly once; rest identical", mj.count('import "./pw_homestead.js"') == 1 and mj.replace('import "./pw_homestead.js"; // HOMESTEAD: hearth / flue / dual wall / rafter (v1.3.178)\n', "") == (BP_SRC / "scripts/main.js").read_text())
man = load(BP / "manifest.json"); man0 = load(BP_SRC / "manifest.json")
check("S5 @minecraft deps unchanged (Lesson #53)", man.get("dependencies") == man0.get("dependencies"), json.dumps(man.get("dependencies")))
# relative imports resolve
bad = [m for m in re.findall(r'from "\./([^"]+)"', (BP / "scripts/pw_homestead.js").read_text()) if not (BP / "scripts" / m).exists()]
check("S6 relative imports resolve", not bad, ", ".join(bad))

# ---------------------------------------------------------------- textures + lang
bad = []
for nm in ("pw_hearth_soot", "pw_hearth_ash", "pw_hearth_embers"):
    for suf in (".png", "_mers.png"):
        p = RP04 / "textures/blocks" / (nm + suf)
        im = Image.open(p)
        if im.size != (128, 128) or im.mode != "RGBA": bad.append(f"{nm}{suf}: {im.size} {im.mode}")
    ts = load(RP04 / "textures/blocks" / (nm + ".texture_set.json"))["minecraft:texture_set"]
    for k in ("color", "metalness_emissive_roughness_subsurface"):
        if not (RP04 / "textures/blocks" / (ts[k] + ".png")).exists(): bad.append(f"{nm}: set ref {ts[k]} missing")
check("T1 textures 128x128 RGBA + texture sets resolve", not bad, "; ".join(bad))
lang = (RP04 / "texts/en_US.lang").read_text().splitlines()
check("T2 lang: one line per new block", all(any(l.startswith(f"tile.{i}.name=") for l in lang) for i in NEW_BLOCKS) and len(lang) == len(NEW_BLOCKS))

# ---------------------------------------------------------------- particles + fog
pr = load(RP02 / "particles/pw_room_smoke.json"); pc = load(RP02 / "particles/pw_chimney_smoke.json"); fg = load(RP02 / "fogs/pw_smoke_room_fog_setting.json")
ok = (pr["particle_effect"]["description"]["identifier"] == "pw:room_smoke" and pc["particle_effect"]["description"]["identifier"] == "pw:chimney_smoke"
      and fg["minecraft:fog_settings"]["description"]["identifier"] == "pw:smoke_room" and fg["format_version"] == "1.21.90")
sprites = [pr["particle_effect"]["description"]["basic_render_parameters"]["texture"], pc["particle_effect"]["description"]["basic_render_parameters"]["texture"]]
ok = ok and all((RP02 / (s + ".png")).exists() for s in sprites)
ok = ok and "minecraft:particle_motion_collision" in pr["particle_effect"]["components"]
check("P  particles + fog identifiers, sprites exist, room smoke collides", ok, ", ".join(sprites))
# script ids match
st = (BP / "scripts/pw_homestead.js").read_text()
check("P2 script uses the same particle/fog ids", 'spawnParticle("pw:room_smoke"' in st and 'spawnParticle("pw:chimney_smoke"' in st and "push pw:smoke_room" in st)

# ---------------------------------------------------------------- I: byte identity of carried files
def tree_hashes(root):
    return {str(p.relative_to(root)).replace(os.sep, "/"): hashlib.md5(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}
def zip_hashes(zp):
    with zipfile.ZipFile(zp) as z: return {n: hashlib.md5(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith("/")}
ALLOWED = {
    "BP-02": {"manifest.json", "PW-DEPENDENCIES.md", "scripts/main.js"},
    "RP-04": {"manifest.json", "PW-DEPENDENCIES.md", "textures/terrain_texture.json"},
    "RP-02": {"manifest.json"},
}
for label, src, dst in (("BP-02", tree_hashes(BP_SRC), tree_hashes(BP)), ("RP-04", zip_hashes(RP04_ZIP), tree_hashes(RP04)), ("RP-02", zip_hashes(RP02_ZIP), tree_hashes(RP02))):
    changed = sorted(n for n, h in src.items() if n in dst and dst[n] != h and n not in ALLOWED[label])
    removed = sorted(n for n in src if n not in dst)
    added = sorted(n for n in dst if n not in src)
    check(f"I  {label}: carried files byte-identical (+{len(added)} added, {len(removed)} removed)", not changed and not removed, "; ".join((changed + removed)[:5]))

# ---------------------------------------------------------------- terrain_texture: only additions
tt0 = json.loads(zipfile.ZipFile(RP04_ZIP).read("textures/terrain_texture.json").decode("utf-8-sig"))
same = all(tt0["texture_data"][k] == tt[k] for k in tt0["texture_data"]) and set(tt) - set(tt0["texture_data"]) == {"pw_hearth_soot", "pw_hearth_ash", "pw_hearth_embers", "pw_hearth_log", "pw_hearth_log_end"}
check("I2 RP-04 terrain_texture: every existing entry unchanged, exactly 5 keys added", same and all(tt0[k] == tt0[k] for k in ("resource_pack_name",)) )

# ---------------------------------------------------------------- Z: package inside the gate
failed = [n for n, ok, _ in results if not ok]
if failed:
    print(f"\nGATE CLOSED — {len(failed)} failing check(s): {failed}\nNOTHING PACKAGED.")
    sys.exit(1)

def pack(tree, out):
    if out.exists(): out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(tree.rglob("*")):
            if p.is_file(): z.write(p, str(p.relative_to(tree)).replace(os.sep, "/"))
OUT.mkdir(parents=True, exist_ok=True)
outs = {"BP-02": OUT / "BP-02-AbsolutRealism-Tectonic-BP-v1_3_178.mcpack",
        "RP-04": OUT / "RP-04-AbsolutRealism-Basic-RP-v1_3_128.mcpack",
        "RP-02": OUT / "RP-02-AbsolutRealism-Atmospheric-Effects-RP-v2_0_2.mcpack"}
for label, tree in (("BP-02", BP), ("RP-04", RP04), ("RP-02", RP02)):
    pack(tree, outs[label])
    ident = zip_hashes(outs[label]) == tree_hashes(tree)
    check(f"Z1 {label} from-zip identity", ident)
r = subprocess.run(["python3", str(ROOT / "tools/verify_pack_versions.py")] + [str(p) for p in outs.values()], capture_output=True, text=True)
print(r.stdout.strip())
check("Z2 version-spot gate", r.returncode == 0)
failed = [n for n, ok, _ in results if not ok]
if failed:
    for p in outs.values():
        if p.exists(): p.unlink()
    print(f"\nGATE CLOSED at packaging — {failed}; packages removed."); sys.exit(1)
print("\nGATE OPEN — packaged:")
for p in outs.values():
    b = p.read_bytes(); print(f"  {p.name}  {len(b):,} B  md5 {hashlib.md5(b).hexdigest()}")
print(f"\n{len(results)} checks, all PASS")
