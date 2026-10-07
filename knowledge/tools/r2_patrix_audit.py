#!/usr/bin/env python3
"""r2_patrix_audit.py — RESEARCH AUDIT R2 (no build; D-C255): the shipped RP-07 `geometry.<mob>.patrix` files vs the
Patrix Java source JEMs converted with the vanilla-verified mapping CONV-1 (see r1_jem_vs_bedrock.py).

For each of the 39 shipped patrix geometries:
  * convert the Patrix JEM (Blockbench 4.12.4 semantics: top-level translate = -pivot_BB; submodel translate = pivot_BB,
    accumulated from depth >= 1; boxes absolute at top level, relative to the submodel pivot below; per-face uv*;
    sizeAdd -> inflate; mirrorTexture u -> mirror) -> Bedrock bones
  * compare CUBES (file coordinates: origin + size) — how many Patrix cubes the shipped file reproduces exactly
  * compare the RENDERED pose (world AABB of every cube through its bone chain with the verified rotation law) — this is
    what the player sees; a cube with the right numbers under a wrong pivot/rotation renders elsewhere (the trader llama)
  * compare bone pivots + rotations for cube-matched bones, and list Patrix cubes with no counterpart / extra cubes
Output: a table + per-mob detail, and a JSON at _logs/r2_patrix_audit.json.  Nothing is written into any pack.
"""
import json, re, math, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
from entity_render import transform
from jem_convert import convert as jem_convert_full, load_json as _lj
ROOT = Path("/home/claude")
CEM = ROOT / "_intake/patrix-mobs/assets/minecraft/optifine/cem"
OURS = ROOT / "_build/rp07-1410/models/entity"
NAME_MAP = {"pufferfish_large": "puffer_fish_big", "pufferfish_medium": "puffer_fish_medium", "pufferfish_small": "puffer_fish_small",
            "tropicalfish_a": "tropical_fish_a", "tropicalfish_b": "tropical_fish_b", "tropicalfish_pattern_a": "tropical_fish_pattern_a", "tropicalfish_pattern_b": "tropical_fish_pattern_b"}


def load_json(p):
    return json.loads(re.sub(r"^\s*//.*$", "", Path(p).read_text(encoding="utf-8-sig"), flags=re.M))


FACES = ("north", "east", "south", "west", "up", "down")


def face_uv(box):
    out = {}
    for f in FACES:
        k = "uv" + f.capitalize(); v = box.get(k)
        if v: out[f] = {"uv": [v[0], v[1]], "uv_size": [v[2] - v[0], v[3] - v[1]]}
    return out or None


def jem_to_bedrock(model):
    """CONV-1. Returns bones [{name, parent, pivot, rotation, mirror, cubes:[{origin,size,inflate,uv}]}] in FILE coords."""
    bones = []

    def add_bone(name, parent, origin_bb, rot, mirror, boxes, box_offset):
        b = {"name": name, "parent": parent, "pivot": [-origin_bb[0], origin_bb[1], origin_bb[2]], "rotation": [-rot[0], -rot[1], rot[2]], "mirror": mirror, "cubes": []}
        for box in boxes or []:
            c = box.get("coordinates")
            if not c: continue
            fx, fy, fz = c[0] + box_offset[0], c[1] + box_offset[1], c[2] + box_offset[2]
            w, h, d = c[3], c[4], c[5]
            b["cubes"].append({"origin": [-(fx + w), fy, fz], "size": [w, h, d], "inflate": box.get("sizeAdd", 0) or 0,
                               "uv": face_uv(box) or (list(box["textureOffset"]) if box.get("textureOffset") else None)})
        bones.append(b); return b

    for part in model.get("models", []):
        if not isinstance(part, dict): continue
        name = part.get("part") or part.get("id")
        t = part.get("translate", [0, 0, 0]); origin = [-t[0], -t[1], -t[2]]
        top = add_bone(name, None, origin, part.get("rotate", [0, 0, 0]), "u" in (part.get("mirrorTexture") or ""), part.get("boxes"), [0, 0, 0])
        top["attach"] = bool(part.get("attach")); top["scale"] = part.get("scale")

        def sub(submodels, parent, depth, parent_origin):
            for i, sm in enumerate(submodels or []):
                tr = list(sm.get("translate", [0, 0, 0]))
                if depth >= 1: tr = [tr[k] + parent_origin[k] for k in range(3)]
                o = tr if "translate" in sm else (parent_origin if depth >= 1 else [0, 0, 0])
                b = add_bone(sm.get("id") or f"{name}_sub_{i}", parent["name"], o, sm.get("rotate", [0, 0, 0]), "u" in (sm.get("mirrorTexture") or ""), sm.get("boxes"), o)
                sub(sm.get("submodels"), b, depth + 1, o)
        sub(part.get("submodels"), top, 0, origin)
    return bones


def bedrock_geo(path, ident):
    d = load_json(path)
    g = [x for x in d["minecraft:geometry"] if x["description"]["identifier"] == ident][0]
    bones = []
    for b in g["bones"]:
        bones.append({"name": b["name"], "parent": b.get("parent"), "pivot": b.get("pivot", [0, 0, 0]), "rotation": b.get("rotation", [0, 0, 0]),
                      "cubes": [{"origin": c["origin"], "size": c["size"], "inflate": c.get("inflate", 0) or 0, "uv": c.get("uv")} for c in b.get("cubes", [])]})
    return bones, g["description"]


def world_aabb(bones):
    """[(bone, origin, size, aabb)] — every cube's 8 corners through its bone chain with the verified rotation law."""
    by = {b["name"]: b for b in bones}
    out = []
    for b in bones:
        chain = []; n = b["name"]; seen = set()
        while n and n in by and n not in seen:
            seen.add(n); chain.append((by[n]["pivot"], by[n]["rotation"])); n = by[n]["parent"]
        for c in b["cubes"]:
            o, s = c["origin"], c["size"]
            P = [[o[0] + dx * s[0], o[1] + dy * s[1], o[2] + dz * s[2]] for dx in (0, 1) for dy in (0, 1) for dz in (0, 1)]
            for piv, r in chain:
                if any(r): P = [transform(p, piv, r) for p in P]
            aabb = [min(p[i] for p in P) for i in range(3)] + [max(p[i] for p in P) for i in range(3)]
            out.append((b["name"], o, s, aabb))
    return out


def key(v, tol=0.05): return tuple(round(x / tol) for x in v)


def audit(mob):
    jem = CEM / f"{NAME_MAP.get(mob, mob)}.jem"
    ours_path = OURS / f"{mob}.geo.json"
    if not jem.exists() or not ours_path.exists(): return None
    jd = load_json(jem)
    conv = jem_to_bedrock(jd)                      # static (file) pose
    conv_rest, ctx, errs = jem_convert_full(jd, rest=True)   # animated rest pose (what the player sees)
    ours, desc = bedrock_geo(ours_path, f"geometry.{mob}.patrix")
    # cube-level (file coords)
    ocubes = {}
    for b in ours:
        for c in b["cubes"]: ocubes.setdefault(key(c["origin"] + c["size"]), []).append(b)
    n_p = sum(len(b["cubes"]) for b in conv); n_o = sum(len(b["cubes"]) for b in ours)
    matched = 0; unmatched = []; piv_ok = 0; rot_ok = 0; bone_pairs = 0; piv_bad = []; rot_bad = []
    for b in conv:
        for c in b["cubes"]:
            k = key(c["origin"] + c["size"])
            if k in ocubes:
                matched += 1; ob = ocubes[k][0]
                bone_pairs += 1
                # compare the full chain pose: pivot/rotation of the owning bone (root parts vs ours)
                if all(abs(b["pivot"][i] - ob["pivot"][i]) <= 0.05 for i in range(3)): piv_ok += 1
                else: piv_bad.append((b["name"], b["pivot"], ob["name"], ob["pivot"]))
                if all(abs(b["rotation"][i] - ob["rotation"][i]) <= 0.05 for i in range(3)): rot_ok += 1
                else: rot_bad.append((b["name"], b["rotation"], ob["name"], ob["rotation"]))
            else:
                unmatched.append((b["name"], c["origin"], c["size"]))
    # rendered pose (world AABB)
    pa = world_aabb(conv_rest); oa = world_aabb(ours)
    oset = {}
    for name, o, s, aabb in oa: oset.setdefault(key(aabb, 0.1), []).append(name)
    pose_ok = sum(1 for name, o, s, aabb in pa if key(aabb, 0.1) in oset)
    pose_bad = [(name, [round(v, 1) for v in aabb]) for name, o, s, aabb in pa if key(aabb, 0.1) not in oset]
    # nearest-cube distance (rest pose vs ours): mean over Patrix cubes of the min centre distance to any of our cubes of the same size
    def centre(a): return [(a[i] + a[i + 3]) / 2 for i in range(3)]
    dists = []
    for name, o, s, aabb in pa:
        best = None
        for n2, o2, s2, a2 in oa:
            if all(abs(s[i] - s2[i]) < 0.06 for i in range(3)):
                c1, c2 = centre(aabb), centre(a2); d = math.sqrt(sum((c1[i] - c2[i]) ** 2 for i in range(3)))
                best = d if best is None or d < best else best
        dists.append(best)
    same_size = [d for d in dists if d is not None]
    mean_off = (sum(same_size) / len(same_size)) if same_size else None
    max_off = max(same_size) if same_size else None
    no_size_match = sum(1 for d in dists if d is None)
    extra = n_o - matched
    attach = [b["name"] for b in conv if b.get("attach")]
    return {"mob": mob, "patrix_cubes": n_p, "ours_cubes": n_o, "cube_match": matched, "pose_match": pose_ok, "extra_in_ours": extra,
            "bones_patrix": len([b for b in conv if b["cubes"]]), "bones_ours": len([b for b in ours if b["cubes"]]),
            "pivot_ok": piv_ok, "rot_ok": rot_ok, "bone_pairs": bone_pairs, "unmatched": unmatched, "pose_bad": pose_bad, "mean_offset": mean_off, "max_offset": max_off, "no_size_match": no_size_match, "anim_errors": errs, "piv_bad": piv_bad, "rot_bad": rot_bad, "attach_parts": attach,
            "patrix_rot_bones": [(b["name"], b["rotation"]) for b in conv if any(b["rotation"])]}


def main():
    mobs = sorted(p.name.replace(".geo.json", "") for p in OURS.glob("*.geo.json") if "stripmine" not in p.name)
    rows = []
    for m in mobs:
        try:
            r = audit(m)
        except Exception as e:
            print(f"{m}: ERROR {e}"); continue
        if r: rows.append(r)
    print(f"{'mob':24s} {'cubes P/O':>10s} {'cube=':>6s} {'pose=':>6s} {'extra':>5s} {'piv=':>5s} {'rot=':>5s} {'meanOff':>8s} {'maxOff':>7s} {'noSize':>6s}  verdict")
    for r in rows:
        v = "EXACT" if r["pose_match"] == r["patrix_cubes"] and r["extra_in_ours"] == 0 else ("POSE-DIFF" if r["cube_match"] == r["patrix_cubes"] else "GEOMETRY-DIFF")
        mo = f"{r['mean_offset']:.2f}" if r['mean_offset'] is not None else "-"; mx = f"{r['max_offset']:.1f}" if r['max_offset'] is not None else "-"
        print(f"{r['mob']:24s} {r['patrix_cubes']:4d}/{r['ours_cubes']:<5d} {r['cube_match']:6d} {r['pose_match']:6d} {r['extra_in_ours']:5d} {r['pivot_ok']:5d} {r['rot_ok']:5d} {mo:>8s} {mx:>7s} {r['no_size_match']:6d}  {v}")
    json.dump(rows, open(ROOT / "_logs/r2_patrix_audit.json", "w"), indent=1)
    print("\nDETAIL (first 4 unmatched cubes / pose-bad per mob):")
    for r in rows:
        if r["unmatched"] or r["pose_bad"] or r["extra_in_ours"]:
            print(f"- {r['mob']}: unmatched {len(r['unmatched'])} {r['unmatched'][:4]}; pose-bad {len(r['pose_bad'])} {r['pose_bad'][:3]}; piv-bad {r['piv_bad'][:2]}; rot-bad {r['rot_bad'][:2]}; attach {r['attach_parts']}")


if __name__ == "__main__":
    main()
