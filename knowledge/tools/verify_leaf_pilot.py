#!/usr/bin/env python3
"""verify_leaf_pilot.py — gate for PW-TestRunner RP v0.4.0 (the leaf pilot assets) + the 24 pilot blocks in BP v0.4.9. Static checks only
rule OUT (P1); the in-game p15 run rules IN.
  A  RP manifest 0.4.0 (same uuids as 0.3.0), capabilities ["pbr"], min_engine 1.21.120
  B  RP diff vs 0.3.0: manifest + terrain_texture + en_US.lang changed, everything else only ADDED
  C  every JSON parses; 4 pilot geometries; each fits Bedrock's oversized-geometry rule (<= 30 px per axis, within +-30, >= 1 px in the block)
  D  24 blocks, each 9 permutations pw:pv 0..8; every material texture key is registered; every PNG exists (128x128 RGBA), has a
     texture set whose normal + MERS files exist at the same size
  E  face / card art is pure cutout (alpha only 0 or 255) -> alpha_test draws it exactly
  F  tint_method only on the 7 _bt blocks (Java's colour families); isotropic only on the 2 _iso blocks' CUBE-face materials (* and spruce top); alpha_test_to_opaque
     only on the 4 far-swap blocks; every other leaf material alpha_test; pv 0 = the opaque far cube
  G  shapes: pv 1-5, 8 full (spruce: 1-8 all full), pv 6-7 cards-only; each full pv has its own quarter-turn / face tile / card tile pair
  H  the p15 lineup only names blocks that exist; lang names every block
  I  render from the BUILT files (oak pv 1..8 + spruce pv 1) -> _docs/leaves/pilot/PILOT-BUILT-CHECK.png (for eyes)"""
import hashlib, json, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML
import java_leaf_study as J
from bb_truth import truth_posed_faces
from equine_compare import bone_affines
from block_render import Face

ROOT = Path("/home/claude")
RP, OLD, BP = ROOT / "_build/testrunner-rp-0.4.0", ROOT / "_build/testrunner-rp-0.3.0", ROOT / "_build/testrunner-0.4.9"
TINTED = {"oak": "default_foliage", "dark_oak": "default_foliage", "jungle": "default_foliage", "acacia": "default_foliage", "mangrove": "default_foliage",
          "birch": "birch_foliage", "spruce": "evergreen_foliage"}
res = []
def check(name, ok, detail=""):
    res.append((name, bool(ok))); print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))
md5 = lambda p: hashlib.md5(Path(p).read_bytes()).hexdigest()
jl = lambda p: ML._parse_json(Path(p).read_text(encoding="utf-8-sig"))

m, mo = jl(RP / "manifest.json"), jl(OLD / "manifest.json")
check("A RP manifest 0.4.0, uuids unchanged, pbr capability, min_engine 1.21.120",
      m["header"]["version"] == [0, 4, 0] and all(x["version"] == [0, 4, 0] for x in m["modules"]) and m["header"]["uuid"] == mo["header"]["uuid"]
      and [x["uuid"] for x in m["modules"]] == [x["uuid"] for x in mo["modules"]] and m.get("capabilities") == ["pbr"] and m["header"]["min_engine_version"] == [1, 21, 120])
tree = lambda d: {str(p.relative_to(d)): md5(p) for p in d.rglob("*") if p.is_file()}
tn, to = tree(RP), tree(OLD)
changed = sorted(k for k in set(tn) & set(to) if tn[k] != to[k]); removed = sorted(set(to) - set(tn)); added = sorted(set(tn) - set(to))
check("B RP diff vs 0.3.0 = manifest + terrain_texture + en_US.lang changed, nothing removed, the rest added",
      changed == ["manifest.json", "texts/en_US.lang", "textures/terrain_texture.json"] and not removed, f"changed {changed} removed {removed} added {len(added)}")
bad = []
for p in list(RP.rglob("*.json")) + list((BP / "blocks").glob("*.json")):
    try: jl(p)
    except Exception as e: bad.append(f"{p.name}: {e}")
geo = {g["description"]["identifier"]: g for g in jl(RP / "models/blocks/pw_pilot_leaves.geo.json")["minecraft:geometry"]}
fit = {}
for gid, g in geo.items():
    fs = truth_posed_faces(g["bones"], 16, 16, bone_affines(g["bones"])); P = np.array([p for f in fs for p in f.pts])
    lo, hi = P.min(0), P.max(0); size = hi - lo
    inside = all(lo[i] < (8 if i != 1 else 16) - 1 and hi[i] > (-8 if i != 1 else 0) + 1 for i in range(3))
    fit[gid] = (all(size <= 30.0001), all(np.abs(lo) <= 30) and all(np.abs(hi) <= 30), inside, [round(float(v), 1) for v in size])
check("C every JSON parses; 4 pilot geometries, each <= 30 px per axis, within +-30, >= 1 px inside the block",
      not bad and set(geo) == {"geometry.pw_pilot_full", "geometry.pw_pilot_cards", "geometry.pw_pilot_spruce", "geometry.pw_pilot_far"} and all(all(v[:3]) for v in fit.values()),
      "; ".join(bad[:3]) + " " + str({k.split(".")[-1]: v[3] for k, v in fit.items()}))
tt = jl(RP / "textures/terrain_texture.json")["texture_data"]
blocks = {}
for p in sorted((BP / "blocks").glob("pw_pilot_*.json")):
    d = jl(p)["minecraft:block"]; blocks[d["description"]["identifier"]] = d
probs, keys_used = [], set()
for ident, d in blocks.items():
    if d["description"]["states"].get("pw:pv") != list(range(9)) or len(d["permutations"]) != 9: probs.append(f"{ident} states/perms")
    for perm in d["permutations"] + [{"components": d["components"]}]:
        for mat in perm["components"].get("minecraft:material_instances", {}).values():
            keys_used.add(mat["texture"])
missing_keys = sorted(k for k in keys_used if k not in tt)
png_probs = []
for k in keys_used:
    if k not in tt: continue
    p = RP / (tt[k]["textures"] + ".png")
    if not p.exists(): png_probs.append(f"{k}: no png"); continue
    im = Image.open(p)
    if im.size != (128, 128) or im.mode != "RGBA": png_probs.append(f"{k}: {im.size} {im.mode}")
    ts = p.with_name(p.stem + ".texture_set.json")
    if not ts.exists(): png_probs.append(f"{k}: no texture set"); continue
    t = jl(ts)["minecraft:texture_set"]
    for layer in ("normal", "metalness_emissive_roughness_subsurface"):
        q = p.with_name(t.get(layer, "?") + ".png")
        if not q.exists() or Image.open(q).size != im.size: png_probs.append(f"{k}: {layer}")
check("D 24 pilot blocks x 9 permutations (pw:pv 0..8); every texture key registered; every PNG 128x128 RGBA with a texture set (normal + MERS, same size)",
      len(blocks) == 24 and not probs and not missing_keys and not png_probs, f"{len(blocks)} blocks, {len(keys_used)} keys; {probs[:2]} {missing_keys[:3]} {png_probs[:3]}")
alpha_bad = [k for k in keys_used if k in tt and not set(np.unique(np.asarray(Image.open(RP / (tt[k]['textures'] + '.png')))[..., 3])) <= {0, 255}]
check("E face / card art is pure cutout (alpha 0 or 255 only)", not alpha_bad, str(alpha_bad[:4]))
fprob = []
for ident, d in blocks.items():
    sp = ident.replace("pw:pilot_", "").replace("_leaves", "").rsplit("_", 1)[0] if ident.endswith(("_bt", "_iso", "_far", "_farp")) else ident.replace("pw:pilot_", "").replace("_leaves", "")
    for perm in d["permutations"]:
        pv = int(perm["condition"].split("==")[1])
        for name, mat in perm["components"]["minecraft:material_instances"].items():
            want_rm = "opaque" if pv == 0 else ("alpha_test_to_opaque" if ident.endswith(("_far", "_farp")) else "alpha_test")
            if mat["render_method"] != want_rm: fprob.append(f"{ident} pv{pv} {name} {mat['render_method']}")
            tm = mat.get("tint_method")
            if ident.endswith("_bt") != bool(tm) or (tm and tm != TINTED.get(sp)): fprob.append(f"{ident} tint {tm}")
            if bool(mat.get("isotropic")) != (ident.endswith("_iso") and name in ("*", "top") and pv > 0): fprob.append(f"{ident} pv{pv} {name} iso")
            if pv > 0 and (mat.get("ambient_occlusion") is not False or mat.get("face_dimming") is not False): fprob.append(f"{ident} AO/dim")
check("F tint only on the 7 _bt blocks (Java colour families); isotropic only on _iso face material; to_opaque only on far-swap blocks; pv 0 opaque; no AO / dimming",
      not fprob and sum(1 for i in blocks if i.endswith("_bt")) == 7, str(fprob[:4]))
gprob = []
for ident, d in blocks.items():
    spruce = "spruce" in ident; seen = set()
    for perm in d["permutations"]:
        pv = int(perm["condition"].split("==")[1]); c = perm["components"]; g = c["minecraft:geometry"]
        want = "geometry.pw_pilot_far" if pv == 0 else ("geometry.pw_pilot_spruce" if spruce else ("geometry.pw_pilot_cards" if pv in (6, 7) else "geometry.pw_pilot_full"))
        if g != want: gprob.append(f"{ident} pv{pv} {g}")
        if pv and g != "geometry.pw_pilot_cards":
            sig = (tuple(c.get("minecraft:transformation", {}).get("rotation", [0, 0, 0])), c["minecraft:material_instances"]["*"]["texture"], c["minecraft:material_instances"]["extra"]["texture"])
            if sig in seen: gprob.append(f"{ident} pv{pv} duplicate look")
            seen.add(sig)
check("G shapes: full pv 1-5 + 8 (spruce 1-8), cards-only pv 6-7; no two full variants of a block share turn + tiles", not gprob, str(gprob[:4]))
p15 = (BP / "scripts/pw_testrunner_p15.js").read_text()
import re
named = set(re.findall(r'block: "(pw:pilot_\{sp\}_leaves[a-z_]*)"', p15)) | set(re.findall(r"block: `(pw:pilot_\{sp\}_leaves[a-z_]*)`", p15))
spp = {"pw:pilot_{sp}_leaves_far": ["oak", "spruce"], "pw:pilot_{sp}_leaves_farp": ["oak", "spruce"], "pw:pilot_{sp}_leaves_iso": ["oak", "spruce"],
       "pw:pilot_{sp}_leaves_bt": list(TINTED)}
need = {t.replace("{sp}", s) for t in named for s in spp.get(t, [])}
need |= {f"pw:pilot_{s}_leaves" for s in ("oak", "birch", "spruce", "jungle", "acacia", "dark_oak", "mangrove", "cherry", "pale_oak", "azalea", "flowering_azalea")}
lang = (RP / "texts/en_US.lang").read_text()
check("H every block p15 plants exists in BP 0.4.9; every pilot block has a name", need <= set(blocks) and all(f"tile.{i}.name=" in lang for i in blocks), str(sorted(need - set(blocks))))

# I — render from the built files: oak pv 1..8 + spruce pv 1 (material -> atlas slot)
def built_faces(ident, pv, at):
    d = blocks[ident]; perm = next(p for p in d["permutations"] if p["condition"].endswith(f"== {pv}"))
    g = geo[perm["components"]["minecraft:geometry"]]; mats = perm["components"]["minecraft:material_instances"]
    names = list(mats); tiles = [Image.open(RP / (tt[mats[n]["texture"]]["textures"] + ".png")).convert("RGBA") for n in names]
    bones = json.loads(json.dumps(g["bones"]))
    for b in bones:
        for c in b["cubes"]:
            for f in c["uv"].values():
                slot = names.index(f.get("material_instance", "*")) if f.get("material_instance", "*") in names else 0
                f["uv"] = [f["uv"][0] + 16 * slot, f["uv"][1]]
    q = (perm["components"].get("minecraft:transformation", {}).get("rotation", [0, 0, 0])[1] // 90) % 4
    return J.block_faces(bones, 16 * len(names), 16, at, quarter=q, dimmed=False), tiles
cells = []
for ident, pv in [("pw:pilot_oak_leaves", v) for v in range(1, 9)] + [("pw:pilot_spruce_leaves", 1), ("pw:pilot_oak_leaves_farp", 1)]:
    F, tiles = built_faces(ident, pv, (0, 0, 0))
    atlas = J.build_atlas(tiles, J.TMP / "built_check.png")
    e, t = J.cam_for(F, (0.7, 0.45, 0.8), pad=1.1)
    cells.append(J.label(J.render(F, atlas, e, t, 260, 260), f"{ident.replace('pw:pilot_', '')} pv {pv}", "from the BUILT files", (40, 95, 55)))
sheet = Image.new("RGB", (5 * 264, 2 * 264), (255, 255, 255))
for i, c in enumerate(cells): sheet.paste(c, ((i % 5) * 264, (i // 5) * 264))
out = ROOT / "_docs/leaves/pilot/PILOT-BUILT-CHECK.png"; sheet.save(out)
check("I render from the built geometry + textures written", out.exists(), str(out))
print(f"\n{'GATE OPEN' if all(r[1] for r in res) else 'GATE SHUT'} {sum(r[1] for r in res)}/{len(res)}")
sys.exit(0 if all(r[1] for r in res) else 1)
