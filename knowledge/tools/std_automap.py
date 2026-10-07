#!/usr/bin/env python3
"""std_automap.py — Phase 2 step A for the jointed-wing birds: derive each rig's mapping onto the TEMPLATE-BIRD names
automatically (roles / sides from tools/standard_bird_map.py: token-exact English + Spanish names, cube-based sides), run
tools/std_convert.convert + gate on every mob, and write a review table _docs/standard/AUTOMAP-BIRDS.md.

Naming (TEMPLATE-BIRD v1.1):
  containers above the body        root, root_2, root_3 …        body (largest torso piece), body_2 … (other torso pieces)
  neck / head / beak               neck, neck_2 … / head, head_2 … / beak (upper) + jaw_lower (lower, by height), crest …
  wing chain per side (outward)    piece 0 = wing_inner (joint shoulder), 1 = primary_1 (joint wrist), k = primary_k
                                   (joint primary_base_k); cubeless bones between = <joint>_rest, _rest2 …
                                   a cube-carrying wing bone whose parent is not its own joint is SPLIT into joint + piece
  leg chain per side               pieces thigh, shin, foot, toe_k (joints hip, knee, ankle, toe_base_k)
  tail                             tail_base (cubeless) / tail, tail_2 …; side tail pieces tail_fan_l / tail_fan_r
  anything else                    keeps its name and is LISTED for review (morph parts, saddles, items …)
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import standard_bird_map as B  # noqa: E402
import std_convert as S  # noqa: E402


def volume(b):
    return sum(abs(c.get("size", [0, 0, 0])[0] * c.get("size", [0, 0, 0])[1] * c.get("size", [0, 0, 0])[2]) or 0.01
               for c in b.get("cubes") or [])


def centroid_y(b):
    cs = b.get("cubes") or []
    if not cs:
        return (b.get("pivot") or [0, 0, 0])[1]
    return sum(c.get("origin", [0, 0, 0])[1] + abs(c.get("size", [0, 0, 0])[1]) / 2 for c in cs) / len(cs)


def automap(geo):
    bones = {b["name"]: b for b in geo["bones"]}
    kids = defaultdict(list)
    for b in geo["bones"]:
        kids[b.get("parent")].append(b["name"])
    def role_of(n):
        tk = B.D.tokens(n)
        if tk & {"arm", "arms"} and not tk & {"wing", "wings", "ala", "alas"}:
            return "other"
        return B.role_of(n)
    role = {n: role_of(n) for n in bones}

    def inherit(n, under):  # descendants of a wing / leg / tail bone belong to it
        if under and role[n] in ("other", "body"):
            role[n] = under
        nxt = role[n] if role[n] in ("wing", "leg", "foot", "tail") else under
        for k in kids[n]:
            inherit(k, nxt if nxt != "foot" else "foot")
    for top in kids[None]:
        inherit(top, None)
    from equine_compare import bone_affines
    import numpy as np
    aff = bone_affines(geo["bones"])

    def world_x(b, p):
        A, tr = aff[b["name"]]
        return float((A @ np.array(p, float) + tr)[0])

    def side_of(b):
        """side from the BIND-POSE world position (a parent's 180° turn flips its children: the WA duck)."""
        cs = b.get("cubes") or []
        if cs:
            xs = [world_x(b, [c["origin"][0] + c["size"][0] / 2, c["origin"][1] + c["size"][1] / 2,
                              c["origin"][2] + c["size"][2] / 2]) for c in cs]
            if min(xs) < -0.5 and max(xs) > 0.5 and len(xs) >= 2:
                return "both"
            x = sum(xs) / len(xs)
        else:
            x = world_x(b, b.get("pivot", [0, 0, 0]))
        # the bone's real place decides (file +x = the mob's own left, as Mojang's humanoid leftArm at +5); a name's
        # "left" / "right" only breaks a tie on the midline — the Naturalist flamingo's leftWing sits at -x (its right)
        if x > 0.5:
            return "l"
        if x < -0.5:
            return "r"
        if B.D.tokens(b["name"]) & B.LEFT:
            return "l"
        if B.D.tokens(b["name"]) & B.RIGHT:
            return "r"
        return "l" if x > 0.25 else ("r" if x < -0.25 else "mid")
    side = {n: side_of(bones[n]) for n in bones}
    mapping, splits, review, used = {}, {}, [], set()

    def take(old, new):
        base, k = new, 2
        while new in used:
            new = f"{base}_{k}"
            k += 1
        used.add(new)
        mapping[old] = new
        return new

    # WA "morph" humanoid sub-rig (body_human …): its own morph_ namespace, outside the bird tree
    if "body_human" in bones:
        morph = {}
        def under(n, anc):
            while n:
                if n == anc:
                    return True
                n = bones[n].get("parent")
            return False
        top = "body_human"
        while bones[top].get("parent"):
            top = bones[top]["parent"]
        for n in bones:
            if under(n, top):
                low = n.lower()
                s_ = "l" if low.startswith("left") or low in ("la",) else ("r" if low.startswith("right") or low in ("ra",) else "")
                base = ("arm" if "arm" in low else "forearm" if low in ("la", "ra") else "item" if "item" in low
                        else "body" if low == "body_human" else "waist" if low.startswith("waist") else low)
                morph[n] = f"morph_{base}" + (f"_{s_}" if s_ else "")
        for n, v in morph.items():
            take(n, v)
            role[n] = "morph"
    # head joint with exactly one cube child of no other role: the child is the head piece
    for n in [n for n in bones if role[n] == "head" and not bones[n].get("cubes")]:
        ch = [k for k in kids[n] if bones[k].get("cubes") and role[k] in ("other", "head", "body") and abs(sum(c.get("origin", [0, 0, 0])[0] + abs(c.get("size", [0, 0, 0])[0]) / 2 for c in bones[k]["cubes"]) / len(bones[k]["cubes"])) < 1.0]
        if len(ch) == 1:
            take(n, "head")
            take(ch[0], "skull")
            role[ch[0]] = "skull"
    # ears (bat): small cube bones under the head piece / joint, one per side
    for n in bones:
        p = bones[n].get("parent")
        if n not in mapping and p in mapping and mapping[p] in ("head", "skull") and bones[n].get("cubes") \
                and role[n] == "other" and side_of(bones[n]) in ("l", "r") and n not in ("beak",):
            take(n, f"ear_{side_of(bones[n])}")
            role[n] = "ear"
    # body
    bodies = sorted([n for n in bones if role[n] == "body" and bones[n].get("cubes")], key=lambda n: -volume(bones[n]))
    for n in bodies:
        take(n, "body")
    # containers: cubeless ancestors of the main body
    if bodies:
        chain, p = [], bones[bodies[0]].get("parent")
        while p:
            chain.append(p)
            p = bones[p].get("parent")
        for n in reversed(chain):
            if n not in mapping and not bones[n].get("cubes"):
                take(n, "root")
    for n in bones:
        if role[n] == "body" and n not in mapping:
            take(n, "body_frame")
    # neck / head / crest
    for r, base in (("neck", "neck"), ("crest", "crest")):
        for n in [n for n in bones if role[n] == r]:
            take(n, base)
    heads = sorted([n for n in bones if role[n] == "head" and n not in mapping], key=lambda n: (not bones[n].get("cubes"), -volume(bones[n])))
    for n in heads:
        take(n, "head" if bones[n].get("cubes") else "head_frame")
    beaks = sorted([n for n in bones if role[n] == "beak"], key=lambda n: -centroid_y(bones[n]))
    for i, n in enumerate(beaks):
        take(n, "beak" if i == 0 else "jaw_lower")
    # chains per side
    def chain_of(r_set, s):
        mine = [n for n in bones if role[n] in r_set and side[n] == s]
        tops = [n for n in mine if bones[n].get("parent") not in mine]
        order = []

        def walk(n):
            order.append(n)
            for k in kids[n]:
                if k in mine:
                    walk(k)
        for t in tops:
            walk(t)
        return order

    # bilateral leg pieces (both legs' cubes in one bone: they move together) -> side-less plural names
    both_names = ["thighs", "shins", "feet", "toes"]
    bi = 0
    both_legs = [n for n in bones if role[n] in ("leg", "foot") and side[n] == "both"]
    for n in sorted(both_legs, key=lambda n: -centroid_y(bones[n])):  # hip to toe = top to bottom
        if bones[n].get("cubes"):
            nm = both_names[min(bi, 3)]
            splits[n] = (f"{nm}_joint", nm) if nm not in used else (f"{nm}_joint_{bi}", f"{nm}_{bi}")
            used.update(splits[n])
            bi += 1
    for s in ("l", "r"):
        # wings
        piece_i = 0
        last_joint = None
        rest_n = defaultdict(int)
        for n in chain_of({"wing"}, s):
            b = bones[n]
            joint_name = ("shoulder" if piece_i == 0 else "wrist" if piece_i == 1 else f"primary_base_{piece_i}") + f"_{s}"
            piece_name = ("wing_inner" if piece_i == 0 else f"primary_{s}_{piece_i}") + ("" if piece_i else f"_{s}")
            if b.get("cubes"):
                parent = b.get("parent")
                if parent in mapping and mapping[parent] == joint_name and len([k for k in kids[parent] if k in bones]) == 1:
                    take(n, piece_name)
                elif kids[n] or True:
                    splits[n] = (joint_name, piece_name)
                    used.update((joint_name, piece_name))
                piece_i += 1
                last_joint = joint_name
            else:
                # a cubeless wing bone: the joint of the NEXT piece if its only child carries cubes, else a rest helper
                ch = [k for k in kids[n] if k in bones]
                if len(ch) == 1 and bones[ch[0]].get("cubes") and joint_name not in used:
                    take(n, joint_name)
                else:
                    key = last_joint or joint_name
                    rest_n[key] += 1
                    take(n, f"{key}_rest" + ("" if rest_n[key] == 1 else str(rest_n[key])))
        # legs
        names = ["thigh", "shin", "foot"]
        joints = ["hip", "knee", "ankle"]
        pi = 0
        leg_chain = chain_of({"leg", "foot"}, s)
        toe_k = 0
        for n in leg_chain:
            b = bones[n]
            sib = [k for k in kids[b.get("parent")] if k in leg_chain and bones[k].get("cubes") and not kids[k]]
            if b.get("cubes") and not kids[n] and len(sib) >= 2:  # a row of toes on one parent
                toe_k += 1
                splits[n] = (f"toe_base_{s}_{toe_k}", f"toe_{s}_{toe_k}")
                used.update(splits[n])
                continue
            if b.get("cubes"):
                if pi < 3:
                    j, pc = f"{joints[pi]}_{s}", f"{names[pi]}_{s}"
                else:
                    j, pc = f"toe_base_{s}_{pi - 2}", f"toe_{s}_{pi - 2}"
                if role[n] == "foot" and pi < 2:  # a foot reached early (2-piece legs): it is the foot
                    j, pc = f"ankle_{s}", f"foot_{s}"
                    pi = 2
                splits[n] = (j, pc)
                used.update((j, pc))
                pi += 1
            else:
                take(n, f"{joints[min(pi, 2)]}_{s}_frame")
    for n in [n for n in bones if role[n] in ("leg", "foot") and n not in mapping and n not in splits and not bones[n].get("cubes")]:
        take(n, "legs_frame")
    # tail
    for n in [n for n in bones if role[n] == "tail" and n not in mapping and n not in splits]:
        if not bones[n].get("cubes"):
            take(n, "tail_base")
        elif side[n] in ("l", "r") and bones[n].get("parent") in bones and role.get(bones[n]["parent"]) == "tail":
            take(n, f"tail_fan_{side[n]}")
        else:
            take(n, "tail")
    for n, v in {"saddled": "saddle", "wheat_troush": "feed_trough"}.items():  # gear spelled in other words
        if n in bones and n not in mapping and n not in splits:
            take(n, v)
    for n in bones:
        if n not in mapping and n not in splits:
            review.append(n)
    # a new name must not equal the name of a bone that keeps its own name
    keep = {n for n in bones if n not in mapping and n not in splits}
    for k, v in list(mapping.items()):
        if v in keep and v != k:
            i = 2
            while f"{v}_{i}" in used or f"{v}_{i}" in keep:
                i += 1
            mapping[k] = f"{v}_{i}"
            used.add(mapping[k])
    mapping = {k: v for k, v in mapping.items() if k != v}
    return mapping, splits, review


def baby_map(adult_geo, adult_map, adult_splits, geo):
    """Mapping for a second geometry of the same entity (baby): every bone name it shares with the adult gets the ADULT's
    decision (identity included — animations are shared); only its own bones are mapped automatically."""
    m2, s2, _ = automap(geo)
    adult_names = {b["name"] for b in adult_geo["bones"]}
    names = {b["name"] for b in geo["bones"]}
    shared = adult_names & names
    m2 = {k: v for k, v in m2.items() if k not in shared}
    s2 = {k: v for k, v in s2.items() if k not in shared}
    for k in shared:
        if k in adult_splits:
            s2[k] = adult_splits[k]
        elif adult_map.get(k, k) != k:
            m2[k] = adult_map[k]
    taken = {v for k, v in m2.items()} | {x for j, p in s2.values() for x in (j, p)} | \
            {k for k in names if k not in m2 and k not in s2}
    for k in [k for k in m2 if k not in shared]:  # a baby-only automatic name that clashes: keep the bone's own name
        if list(m2.values()).count(m2[k]) > 1 or m2[k] in {n for n in names if n not in m2 and n not in s2}:
            del m2[k]
    return m2, s2


MANUAL = {
    "geometry.pw_phantom": ({
        "pw_pitch": "root", "head": "jem_head", "head2": "head", "body": "body_frame", "body2": "body",
        "tail3": "tail", "tail4": "tail_2",
        "right_wing2": "shoulder_r", "right_wing_sub_0": "wing_inner_r", "right_wing_tip2": "elbow_r",
        "right_wing_tip2_hinge": "wrist_r", "right_wing_tip_sub_0": "primary_r_1",
        "left_wing_tip2": "elbow_l",
        "right_wing": "jem_wing_r", "left_wing": "jem_wing_l", "tail": "jem_tail", "tail2": "jem_tail_2",
        "left_wing_tip": "jem_wing_tip_l", "right_wing_tip": "jem_wing_tip_r"},
        {"left_wing2": ("shoulder_l", "wing_inner_l"), "left_wing_tip2_hinge": ("wrist_l", "primary_l_1")}),
}


def main(ids=None):
    rows = json.loads((ROOT / "_docs/standard/BIRD-RIG-MAP.json").read_text())
    todo = [r for r in rows if r["class"] == "TEMPLATE-READY" and r["id"] != "minecraft:parrot"]
    if ids:
        todo = [r for r in todo if r["id"] in ids]
    packs = {}
    lines = ["# AUTOMAP — jointed-wing birds (Phase 2 step A)", "",
             "| mob | gate | splits | renamed | kept for review |", "|---|---|---|---|---|"]
    detail = []
    results = {}
    for r in todo:
        census = next(c for c in json.loads((ROOT / "_docs/standard/SKELETON-CENSUS.json").read_text()) if c["id"] == r["id"])
        pack = ROOT / "_build" / census["rp"].replace("rp07-1438", "rp07-1439").replace("rp06-1424", "rp06-1425")
        P = packs.setdefault(str(pack), S.Pack(pack))
        geo = P.geos[r["geometry"]]
        if r["geometry"] in MANUAL:
            mapping, splits = MANUAL[r["geometry"]]
            review = []
        else:
            mapping, splits, review = automap(geo)
        ef, desc = P.entities[r["id"]]
        per_geo = {g: baby_map(geo, mapping, splits, P.geos[g])
                   for g in set((desc.get("geometry") or {}).values()) - {r["geometry"]}}
        try:
            info = S.convert(P, r["id"], mapping, splits, per_geo)
            n, bad = S.gate(P, r["id"], info, S.ENVS, S.TIMES[::2])
            gate_s = f"{n - len(bad)}/{n}"
        except AssertionError as e:
            gate_s, bad = f"REFUSED {e}"[:80], ["refused"]
        results[r["id"]] = (gate_s, bad[:2])
        lines.append(f"| {r['id']} | {gate_s} | {len(splits)} | {len(mapping)} | {', '.join(review[:8])} |")
        detail.append(f"\n### {r['id']} (`{r['geometry']}`)\n" +
                      "\n".join(f"- `{k}` → `{v}`" for k, v in mapping.items()) +
                      ("\n" + "\n".join(f"- `{k}` → joint `{j}` + piece `{p}`" for k, (j, p) in splits.items()) if splits else ""))
        print(r["id"], gate_s, bad[:1])
    (ROOT / "_docs/standard/AUTOMAP-BIRDS.md").write_text("\n".join(lines + ["", "## Mappings"] + detail) + "\n")
    return results


if __name__ == "__main__":
    main(sys.argv[1:] or None)
