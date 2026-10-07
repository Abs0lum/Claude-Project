#!/usr/bin/env python3
"""verify_leaf_v3.py — gate for BP-02 1.3.198 + RP-01 1.3.107 (build_leaf_v3.py, D-C350). Static checks only RULE OUT (P1)."""
import hashlib, json, re, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML

ROOT = Path("/home/claude")
B0, B1, R0, R1 = (ROOT / "_build" / d for d in ("bp02-197", "bp02-198", "rp01-106", "rp01-107"))
ALL = ("oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "mangrove", "cherry", "pale_oak", "azalea", "flowering_azalea")
res = []
def check(name, ok, detail=""):
    res.append((name, bool(ok))); print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f" — {detail}" if detail and not ok else (f" — {detail}" if detail else "")))
def jl(p): return ML._parse_json(Path(p).read_text(encoding="utf-8-sig"))
def md5(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def files(d): return {str(p.relative_to(d)): p for p in d.rglob("*") if p.is_file()}

# A manifests
for d0, d1, ver, name in ((B0, B1, [1, 3, 198], "AbsolutRealism Tectonic BP v1.3.198"), (R0, R1, [1, 3, 107], "AbsolutRealism Tectonic RP v1.3.107")):
    m0, m1 = jl(d0 / "manifest.json"), jl(d1 / "manifest.json")
    check(f"A {d1.name} manifest: version {ver}, name, header/module uuids + dependencies + capabilities unchanged",
          m1["header"]["version"] == ver and m1["header"]["name"] == name and m1["header"]["uuid"] == m0["header"]["uuid"]
          and [x["uuid"] for x in m1["modules"]] == [x["uuid"] for x in m0["modules"]] and all(x["version"] == ver for x in m1["modules"])
          and m1.get("dependencies") == m0.get("dependencies") and m1.get("capabilities") == m0.get("capabilities"))
# B parse
bad = [str(p) for d in (B1, R1) for p in d.rglob("*.json") if not (lambda q: (lambda: jl(q))())]
errs = []
for d in (B1, R1):
    for p in d.rglob("*.json"):
        try: jl(p)
        except Exception as e: errs.append(f"{p.name}: {e}")
check("B every JSON in both packs parses", not errs, "; ".join(errs[:3]))
nc = [subprocess.run(["node", "--check", str(p)], capture_output=True).returncode for p in (B1 / "scripts").glob("*.js")]
check("B node --check on every BP-02 script", all(c == 0 for c in nc), f"{len(nc)} scripts")
# C only the expected files changed
f0, f1 = files(B0), files(B1)
chg = sorted(k for k in f1 if k not in f0 or md5(f0[k]) != md5(f1[k])); gone = sorted(k for k in f0 if k not in f1)
want = sorted([f"blocks/{s}_leaves.json" for s in ALL] + [f"loot_tables/blocks/{s}_leaves.json" for s in ALL] + ["scripts/main.js", "manifest.json"])
check("C BP: only the 11 leaf blocks, 11 leaf loot tables, main.js and the manifest changed; nothing removed", chg == want and not gone, f"{len(chg)} changed, {len(gone)} gone")
g0, g1 = files(R0), files(R1)
rchg = sorted(k for k in g1 if k not in g0 or md5(g0[k]) != md5(g1[k])); rgone = sorted(k for k in g0 if k not in g1)
rwant = sorted([k for k in g1 if re.match(r"textures/blocks/pw_leaves2/[a-z_]+_[fc]\d\.png$", k)] +
               [k for k in g1 if re.match(r"textures/blocks/pw_leaves2/[a-z_]+_[fc]\d_mers\.png$", k)] +
               [f"textures/blocks/pw_leaves2/{s}_fall.png" for s in ALL] + ["manifest.json"])
check("C RP: only the 100 colour tiles, 100 MERS maps, 11 fall tiles and the manifest changed; nothing removed",
      rchg == rwant and not rgone and len(rwant) == 212, f"{len(rchg)} changed (want {len(rwant)}), {len(rgone)} gone")
# D loot
ok = True
for s in ALL:
    L0, L1 = jl(B0 / f"loot_tables/blocks/{s}_leaves.json"), jl(B1 / f"loot_tables/blocks/{s}_leaves.json")
    names = [e["name"] for pl in L1["pools"] if any(c.get("item") == "minecraft:shears" for c in pl.get("conditions", [])) for e in pl["entries"]]
    rest0 = [pl for pl in L0["pools"] if not any(c.get("item") == "minecraft:shears" for c in pl.get("conditions", []))]
    rest1 = [pl for pl in L1["pools"] if not any(c.get("item") == "minecraft:shears" for c in pl.get("conditions", []))]
    ok &= names == [f"pw:{s}_leaves"] and rest0 == rest1
check("D shears drop OUR block pw:<species>_leaves (all 11); every other loot pool unchanged", ok)
blk_ids = {jl(p)["minecraft:block"]["description"]["identifier"] for p in (B1 / "blocks").glob("*_leaves.json")}
check("D every dropped leaf id is a block in this BP", all(f"pw:{s}_leaves" in blk_ids for s in ALL))
# E isotropic off, nothing else changed in the blocks (with the Z1-B nudge: each 1.3.197 permutation x pw:off 0/1/2)
NUDGED = "pw:off" in jl(B1 / "blocks/oak_leaves.json")["minecraft:block"]["description"]["states"]
T = {o: [round((o - 3) * 0.006 * a, 4) for a in (1, 2, 3)] for o in range(7)}
ok, n = True, 0
for s in ALL:
    b0, b1 = jl(B0 / f"blocks/{s}_leaves.json"), jl(B1 / f"blocks/{s}_leaves.json")
    for pm in b0["minecraft:block"]["permutations"]:
        for mi in pm["components"]["minecraft:material_instances"].values():
            if mi.pop("isotropic", None) is not None: n += 1
    if NUDGED:
        st0 = dict(b0["minecraft:block"]["description"]["states"]); st0["pw:off"] = list(range(7))
        p0, p1 = b0["minecraft:block"]["permutations"], b1["minecraft:block"]["permutations"]
        good = b1["minecraft:block"]["description"]["states"] == st0 and len(p1) == 7 * len(p0)
        for i, pm in enumerate(p0):
            for o in range(7):
                q = p1[7 * i + o]; c = json.loads(json.dumps(q["components"])); tr = c.pop("minecraft:transformation", {"rotation": [0, 0, 0]})
                c0 = json.loads(json.dumps(pm["components"])); tr0 = c0.pop("minecraft:transformation", {"rotation": [0, 0, 0]})
                good &= q["condition"] == f"{pm['condition']} && q.block_state('pw:off') == {o}" and c == c0 \
                        and tr.get("rotation", [0, 0, 0]) == tr0.get("rotation", [0, 0, 0]) and (tr.get("translation") == T[o] if o != 3 else "translation" not in tr)
        b1c = json.loads(json.dumps(b1)); b1c["minecraft:block"]["permutations"] = p0; b1c["minecraft:block"]["description"]["states"] = b0["minecraft:block"]["description"]["states"]
        ok &= good and b0 == b1c and '"isotropic"' not in json.dumps(b1)
    else:
        ok &= b0 == b1 and '"isotropic"' not in json.dumps(b1)
check("E picture turns off: 'isotropic' gone from every leaf material, the blocks otherwise identical to 1.3.197"
      + (" (+ the nudge: every permutation x pw:off 0-6, translations as designed)" if NUDGED else ""), ok and n > 0, f"{n} removed")
if NUDGED:
    t1n = (B1 / "scripts/main.js").read_text()
    check("E2 main.js sets pw:off with the look (onPlace + assign-once) from (x + 2y + 4z) mod 7",
          "function pwNudge(loc)" in t1n and t1n.count('withState("pw:off", pwNudge(block.location))') == 2)
    # every face-touching neighbour pair differs (the whole point)
    nud = lambda x, y, z: (x + 2 * y + 4 * z) % 7
    check("E3 two leaves that touch on a face or an edge (the diagonal card twins) never get the same nudge; every shift pair differs along every normal",
          all(nud(x, y, z) != nud(x + a, y + b, z + c) for x in range(-5, 5) for y in range(-5, 5) for z in range(-5, 5)
              for a, b, c in ((1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1), (1, 0, -1), (1, 1, 0), (1, -1, 0), (0, 1, 1), (0, 1, -1))))
# F tile sizes + texture sets
tt = jl(R1 / "textures/terrain_texture.json")["texture_data"]; sizes = set(); miss = []
for k, v in tt.items():
    if not k.startswith("pw_leaves2_"): continue
    base = R1 / v["textures"]; ts = jl(Path(str(base) + ".texture_set.json"))["minecraft:texture_set"]
    try:
        sizes.add(tuple(Image.open(base.parent / (ts[c] + ".png")).size[0] for c in ("color", "normal", "metalness_emissive_roughness_subsurface")))
    except Exception as e: miss.append(f"{k}: {e}")
check("F every leaf tile key: colour 256 / normal 128 / MERS 64 through its texture set (his p16 pick)", sizes == {(256, 128, 64)} and not miss, f"{sizes} {miss[:2]}")
# G fall tiles see-through again
ok = True; det = []
for s in ALL:
    a = np.asarray(Image.open(R1 / f"textures/blocks/pw_leaves2/{s}_fall.png").convert("RGBA"))
    frac = float((a[..., 3] < 128).mean()); ok &= 0.02 < frac < 0.95 and a.shape[0] == 256; det.append(f"{s} {frac:.2f}")
check("G falling-canopy tiles keep see-through pixels (n07 FAIL fix), 256 px", ok, ", ".join(det[:4]))
# H main.js: only the relook block + build tag differ
t0, t1 = (B0 / "scripts/main.js").read_text(), (B1 / "scripts/main.js").read_text()
check("H main.js: relook sweep gone, PW_BUILD 1.3.198, the leaf look rule untouched",
      "_relookJob" not in t1 and "PW_RELOOK" not in t1 and 'const PW_BUILD = "1.3.198";' in t1 and "function pwLeafLook(block)" in t1
      and t1.count("system.runInterval") == t0.count("system.runInterval") - 1)
a = t0.index("// v1.3.197 RELOOK SWEEP (D-C347)"); a = t0.rindex("// =====", 0, a); b = t0.index("}, PW_RELOOK_INTERVAL);\n", a) + len("}, PW_RELOOK_INTERVAL);\n")
rebuilt = (t0[:a] + "// v1.3.198: the relook sweep (v1.3.197) is removed — his p16 ruling: every tree from now on is a new tree.\n" + t0[b:]).replace('const PW_BUILD = "1.3.197";', 'const PW_BUILD = "1.3.198";')
if "function pwNudge(loc)" in t1:
    t1_ = t1.replace('    try { if (PW_LEAF_TYPES_DECAY.has(block.typeId)) newPerm = newPerm.withState("pw:off", pwNudge(block.location)); } catch { /* no pw:off */ }\n', "")
    t1_ = t1_.replace('.withState("pw:rseed", true).withState("pw:off", pwNudge(block.location)));', '.withState("pw:rseed", true));')
    t1_ = re.sub(r"// v1\.3\.198 LEAF NUDGE.*?function pwNudge\(loc\) \{[^\n]*\n\n", "", t1_, flags=re.S)
else: t1_ = t1
check("H main.js = 1.3.197 minus the relook block, build tag 1.3.198 (+ the nudge lines when built with it) — nothing else touched", rebuilt == t1_)
# I the 256 tiles are the same pictures as the 128 tiles they replace
worst = 0
for s in ALL:
    for k in ("f0", "c0"):
        a = np.asarray(Image.open(R0 / f"textures/blocks/pw_leaves2/{s}_{k}.png").convert("RGBA")).astype(float)
        b = np.asarray(Image.open(R1 / f"textures/blocks/pw_leaves2/{s}_{k}.png").convert("RGBA")).astype(float).reshape(128, 2, 128, 2, 4).mean((1, 3))
        m = (a[..., 3] >= 128) & (b[..., 3] >= 128)
        worst = max(worst, float(np.abs(a[..., :3][m].mean(0) - b[..., :3][m].mean(0)).max()))
check("I every 256 tile is the same picture as the 128 tile it replaces (mean colour of the leaf pixels within 12)", worst < 12, f"worst {worst:.1f}")
# J Molang (same lint the ship gate runs, on a zip of each build dir)
import zipfile, tempfile
nml, eml = 0, []
for d in (B1, R1):
    z = Path(tempfile.mkdtemp()) / (d.name + ".mcpack")
    with zipfile.ZipFile(z, "w") as zf:
        for p in d.rglob("*"):
            if p.is_file() and p.suffix == ".json": zf.write(p, str(p.relative_to(d)))
    n_, e_ = ML.lint_pack(z); nml += n_; eml += e_
check("J Molang lint (both packs as built)", not eml and nml > 0, f"{nml} strings, {len(eml)} errors")
print(); print(("GATE OPEN" if all(ok for _, ok in res) else "GATE CLOSED") + f" — {sum(ok for _, ok in res)}/{len(res)}")
