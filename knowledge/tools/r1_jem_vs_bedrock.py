#!/usr/bin/env python3
"""r1_jem_vs_bedrock.py — CONTROLLED EXPERIMENT R1 (research, no build; D-C255).

Question: what is the exact JEM(invertAxis "xy") -> Bedrock geometry mapping, and which rotation-sign convention does
the engine use?  Ground truth: Mojang converted the SAME Java models to both sides — the CEM Template Models
(Ewan Howell, v5.0.3: the vanilla Java models in JEM form, used by every CEM author) and Mojang's own vanilla Bedrock
geometries (bedrock-samples 1.26.50.4).  If a candidate mapping reproduces Mojang's Bedrock bones (pivot, rotation,
cubes, uv) from the JEM templates across many mobs, it is the mapping.

Candidate mappings (derived from the Blockbench 4.12.4 codecs, optifine_jem.js + bedrock.js):
  pivot_B    = (t.x, -t.y, -t.z)                      (t = JEM translate of a top-level part)
  origin_B   = (-(c.x + w), c.y, c.z), size (w,h,d)   (c = JEM box coordinates; x mirrored)
  rotation_B = (-r.x, -r.y, +r.z)                      (r = JEM rotate)   <- candidate M0
alternatives tried for the rotation sign: every sign triple; and for x: mirrored vs not.

Output: a per-mob table (bones matched by cube set; pivot / rotation agreement per candidate) + a summary.
"""
import json, re, itertools, sys
from pathlib import Path
ROOT = Path("/home/claude")
TPL = json.load(open(ROOT / "_intake/cem-templates/cem_template_models.json"))["models"]
BED = ROOT / "_intake/bedrock-samples/resource_pack/models/entity"


def load_json(p):
    return json.loads(re.sub(r"^\s*//.*$", "", Path(p).read_text(encoding="utf-8-sig"), flags=re.M))


# ---------- JEM -> "Blockbench frame" (world frame) bones, per the Blockbench 4.12.4 importer ----------
def jem_to_bb(model):
    """Return list of bones {name, parent, origin, rotation, cubes:[{from, size, uv, mirror, inflate}]} in the BB frame."""
    bones = []
    for part in model.get("models", []):
        if not isinstance(part, dict): continue
        name = part.get("part") or part.get("id")
        t = part.get("translate", [0, 0, 0])
        origin = [-t[0], -t[1], -t[2]]
        rot = part.get("rotate", [0, 0, 0])
        bone = {"name": name, "parent": None, "origin": origin, "rotation": list(rot), "cubes": [], "mirror": part.get("mirrorTexture", "") and "u" in part.get("mirrorTexture", "")}
        bones.append(bone)
        for box in part.get("boxes", []):
            c = box["coordinates"]
            bone["cubes"].append({"from": [c[0], c[1], c[2]], "size": [c[3], c[4], c[5]], "uv": box.get("textureOffset"), "inflate": box.get("sizeAdd", 0)})

        def sub(submodels, parent_bone, depth, parent_origin):
            for i, sm in enumerate(submodels or []):
                tr = list(sm.get("translate", [0, 0, 0]))
                if depth >= 1: tr = [tr[k] + parent_origin[k] for k in range(3)]
                o = tr if "translate" in sm else (parent_origin if depth >= 1 else [0, 0, 0])
                b = {"name": sm.get("id") or f"{name}_sub_{i}", "parent": parent_bone["name"], "origin": o, "rotation": list(sm.get("rotate", [0, 0, 0])), "cubes": [],
                     "mirror": bool(sm.get("mirrorTexture", "") and "u" in sm.get("mirrorTexture", ""))}
                bones.append(b)
                for box in sm.get("boxes", []):
                    c = box["coordinates"]
                    b["cubes"].append({"from": [c[0] + o[0], c[1] + o[1], c[2] + o[2]], "size": [c[3], c[4], c[5]], "uv": box.get("textureOffset"), "inflate": box.get("sizeAdd", 0)})
                sub(sm.get("submodels"), b, depth + 1, o)
        sub(part.get("submodels"), bone, 0, origin)
    return bones


# ---------- BB frame -> Bedrock file frame ----------
def bb_to_bedrock(bones, rot_signs=(-1, -1, 1), mirror_x=True):
    out = []
    for b in bones:
        o = b["origin"]
        pivot = [-o[0], o[1], o[2]] if mirror_x else list(o)
        rot = [b["rotation"][k] * rot_signs[k] for k in range(3)]
        cubes = []
        for c in b["cubes"]:
            f, s = c["from"], c["size"]
            origin = [-(f[0] + s[0]), f[1], f[2]] if mirror_x else list(f)
            cubes.append({"origin": origin, "size": list(s), "uv": c["uv"], "inflate": c["inflate"]})
        out.append({"name": b["name"], "parent": b["parent"], "pivot": pivot, "rotation": rot, "cubes": cubes})
    return out


# ---------- vanilla Bedrock geometry ----------
def bedrock_bones(path, ident=None):
    d = load_json(path)
    geos = d.get("minecraft:geometry")
    if geos is None:  # 1.8.0 format
        geos = [{"description": {"identifier": k}, "bones": v.get("bones", [])} for k, v in d.items() if k.startswith("geometry.")]
    if ident: geos = [g for g in geos if g["description"]["identifier"] == ident] or geos
    best = max(geos, key=lambda g: sum(len(b.get("cubes", [])) for b in g["bones"]))
    bones = []
    for b in best["bones"]:
        rot = b.get("rotation") or b.get("bind_pose_rotation") or [0, 0, 0]
        cubes = [{"origin": c["origin"], "size": c["size"], "uv": c.get("uv"), "inflate": c.get("inflate", 0)} for c in b.get("cubes", [])]
        bones.append({"name": b["name"], "parent": b.get("parent"), "pivot": b.get("pivot", [0, 0, 0]), "rotation": list(rot), "cubes": cubes})
    return best["description"]["identifier"], bones


def cube_key(c, tol=0.01):
    return tuple(round(v / tol) for v in c["origin"] + c["size"])


def approx(a, b, tol=0.01):
    return all(abs(a[i] - b[i]) <= tol for i in range(3))


PAIRS = [  # (template name, bedrock file, identifier or None)
    ("cow", "cow.geo.json", None), ("pig", "pig.geo.json", None), ("sheep", "sheep.geo.json", "geometry.sheep.sheared.v1.8"), ("sheep_wool", "sheep.geo.json", "geometry.sheep.v1.8:geometry.sheep.sheared.v1.8"),
    ("llama", "llama.geo.json", None), ("wolf", "wolf.geo.json", None), ("chicken", "chicken.geo.json", None), ("cat", "cat.geo.json", None), ("ocelot", "ocelot.geo.json", None),
    ("fox", "fox.geo.json", None), ("panda", "panda.geo.json", None), ("polar_bear", "polar_bear.geo.json", None), ("horse_21.1", "horse_v3.geo.json", None), ("horse", "horse_v3.geo.json", None),
    ("dolphin", "dolphin.geo.json", None), ("turtle", "turtle.geo.json", None), ("cod", "cod.geo.json", None), ("salmon", "salmon.geo.json", None), ("axolotl", "axolotl.geo.json", None),
    ("frog", "frog.geo.json", None), ("goat", "goat.geo.json", None), ("rabbit", "rabbit.geo.json", None), ("parrot", "parrot.geo.json", None), ("spider", "spider.geo.json", None),
    ("camel", "camel.geo.json", None), ("sniffer", "sniffer.geo.json", None), ("bee", "bee.geo.json", None), ("zombie", "zombie.geo.json", None), ("villager", "villager_v2.geo.json", None),
    ("iron_golem", "iron_golem.geo.json", None), ("creeper", "creeper.geo.json", None), ("enderman", "enderman.geo.json", None), ("mooshroom", "mooshroom.geo.json", None), ("ravager", "ravager.geo.json", None),
    ("hoglin", "hoglin.geo.json", None), ("strider", "strider.geo.json", None), ("armadillo", "armadillo.geo.json", None), ("allay", "allay.geo.json", None), ("warden", "warden.geo.json", None), ("tadpole", "tadpole.geo.json", None),
    ("squid", "squid.geo.json", None), ("bat", "bat.geo.json", None), ("phantom", "phantom.geo.json", None), ("blaze", "blaze.geo.json", None), ("ghast", "ghast.geo.json", None), ("silverfish", "silverfish.geo.json", None), ("endermite", "endermite.geo.json", None),
    ("vex", "vex.geo.json", None), ("witch", "witch.geo.json", None), ("wither_skeleton", "wither_skeleton.geo.json", None), ("skeleton", "skeleton.geo.json", None), ("drowned", "drowned.geo.json", None), ("husk", "husk.geo.json", None), ("stray", "stray.geo.json", None),
    ("zombie_villager", "zombie_villager_v2.geo.json", None), ("pillager", "pillager.geo.json", None), ("vindicator", "vindicator.geo.json", None), ("evoker", "evoker.geo.json", None), ("piglin", "piglin.geo.json", None), ("guardian", "guardian.geo.json", None),
    ("magma_cube", "magma_cube.geo.json", None), ("slime", "slime.geo.json", None), ("shulker", "shulker.geo.json", None), ("snow_golem", "snow_golem.geo.json", None), ("wither", "wither_boss.geo.json", None), ("dragon", "ender_dragon.geo.json", None),
    ("donkey_21.1", "horse_v3.geo.json", None), ("glow_squid", "glow_squid.geo.json", None), ("copper_golem", "copper_golem.geo.json", None), ("breeze", "breeze.geo.json", None), ("creaking", "creaking.geo.json", None), ("bogged", "bogged.geo.json", None), ("tropical_fish_a", "tropical_fish.geo.json", None), ("pufferfish_big", "pufferfish.geo.json", None),
]


def evaluate(tname, bfile, ident, rot_signs, mirror_x):
    if tname not in TPL or not (BED / bfile).exists(): return None
    model = json.loads(TPL[tname]["model"])
    conv = bb_to_bedrock(jem_to_bb(model), rot_signs, mirror_x)
    bid, van = bedrock_bones(BED / bfile, ident)
    # index vanilla bones by cube-set key
    van_index = {}
    for b in van:
        for c in b["cubes"]:
            van_index.setdefault(cube_key(c), []).append(b)
    matched = 0; piv_ok = 0; rot_ok = 0; rot_tested = 0; unmatched = []; rot_bad = []; piv_bad = []
    for b in conv:
        if not b["cubes"]: continue
        cands = None
        for c in b["cubes"]:
            s = set(id(x) for x in van_index.get(cube_key(c), []))
            cands = s if cands is None else (cands & s)
        cands = [x for x in van if id(x) in (cands or set())]
        if not cands:
            unmatched.append(b["name"]); continue
        vb = cands[0]; matched += 1
        if approx(b["pivot"], vb["pivot"]): piv_ok += 1
        else: piv_bad.append((b["name"], b["pivot"], vb["name"], vb["pivot"]))
        if any(abs(v) > 0.001 for v in b["rotation"]) or any(abs(v) > 0.001 for v in vb["rotation"]):
            rot_tested += 1
            if approx(b["rotation"], vb["rotation"], 0.05): rot_ok += 1
            else: rot_bad.append((b["name"], b["rotation"], vb["name"], vb["rotation"]))
    return {"template": tname, "bedrock": bid, "bones": sum(1 for b in conv if b["cubes"]), "matched": matched, "piv_ok": piv_ok, "rot_tested": rot_tested, "rot_ok": rot_ok, "unmatched": unmatched, "rot_bad": rot_bad, "piv_bad": piv_bad, "van_bones": sum(1 for b in van if b["cubes"])}


def main():
    signs = list(itertools.product((-1, 1), repeat=3))
    totals = {}
    for mx in (True, False):
        for sg in signs:
            agg = [0, 0, 0, 0, 0]  # bones matched piv_ok rot_tested rot_ok
            for t, f, i in PAIRS:
                r = evaluate(t, f, i, sg, mx)
                if not r: continue
                agg[0] += r["bones"]; agg[1] += r["matched"]; agg[2] += r["piv_ok"]; agg[3] += r["rot_tested"]; agg[4] += r["rot_ok"]
            totals[(mx, sg)] = agg
    print("candidate            cubes-matched  pivots-ok  rot-tested  rot-ok")
    for (mx, sg), a in sorted(totals.items(), key=lambda kv: (-kv[1][1], -kv[1][2], -kv[1][4])):
        print(f"mirror_x={str(mx):5s} signs={sg}   {a[1]:4d}/{a[0]:<4d}   {a[2]:4d}     {a[3]:4d}      {a[4]:4d}")
    print("\nPER MOB under M0 (mirror_x=True, signs=(-1,-1,1)):")
    for t, f, i in PAIRS:
        r = evaluate(t, f, i, (-1, -1, 1), True)
        if not r: print(f"  {t:18s} (no pair on disk)"); continue
        print(f"  {t:18s} -> {r['bedrock']:36s} bones {r['matched']:2d}/{r['bones']:<2d} (vanilla {r['van_bones']:2d})  pivots {r['piv_ok']:2d}  rot {r['rot_ok']}/{r['rot_tested']}"
              + (f"  UNMATCHED {r['unmatched']}" if r['unmatched'] else "") + (f"  ROT-BAD {r['rot_bad']}" if r['rot_bad'] else "") + (f"  PIV-BAD {r['piv_bad'][:3]}" if r['piv_bad'] else ""))


if __name__ == "__main__":
    main()
