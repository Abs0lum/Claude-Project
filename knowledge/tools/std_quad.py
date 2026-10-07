#!/usr/bin/env python3
"""std_quad.py — Phase 2b, QUADRUPEDS (TEMPLATE-QUADRUPED v1, his Q1 = b, Q2): every four-legged mob's rig gets the
standard names and real leg joints, as a COPY (std_convert), gated identical under every one of its animations.

Step 1 — names (automap_quad): body / root containers / neck / head (joint + skull piece) / snout / jaw_lower / ears /
horns / tail chain / four limbs. A limb is found from its leg bones' bind-pose WORLD position: side by x (+x = the mob's
left), front / hind by z against the body's centre (north = -z = the front). Per limb, cube pieces top -> bottom:
   front  shoulder -> upper_arm, elbow -> forearm, wrist -> front_foot, front_toe_base_k -> front_toe_k
   hind   hip -> thigh, knee -> shin, hock -> hind_foot, hind_toe_base_k -> hind_toe_k
Step 2 — leg cuts (his Q1 = b): a limb with ONE piece is cut along its length at front 43 / 86 %, hind 35 / 70 % (template
ratios); a limb with TWO pieces has its lower piece cut at front 75 %, hind 54 % of its length (forearm : foot = 43 : 14,
shin : foot = 35 : 30). UV is resolved per face and sub-rectangled (std_wingsplit.cut_cube): every texel stays where it
was. New joints have rotation 0 -> every pose of every old animation is unchanged; they bend once the walks drive them.
Step 3 — his Q2: cubeless `pw_*` placeholder leaves that nothing references are removed.
Gate: UV-sample correspondence (std_birds_b.gate_uv) old original vs new staged, under every animation of the entity.
Writes _docs/standard/QUAD-STANDARD.md."""
import copy
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import mers_derive as D  # noqa: E402
import std_convert as S  # noqa: E402
import std_stepc as SC  # noqa: E402
import std_wingsplit as W  # noqa: E402
import std_cube as CU  # noqa: E402
from equine_compare import bone_affines  # noqa: E402

LEFT, RIGHT = {"left", "l", "lft", "izq", "izquierda"}, {"right", "r", "rgt", "der", "derecha"}
ROLE_TOKENS = [
    ("ear", {"ear", "ears", "oreja", "orejas"}),
    ("horn", {"horn", "horns", "antler", "antlers", "tusk", "tusks", "colmillo", "colmillos", "cuerno", "cuernos"}),
    ("jaw", {"jaw", "mandible", "sob", "lower", "chin"}),
    ("snout", {"snout", "nose", "muzzle", "mouth", "trompa", "trunk", "beak", "hocico", "boca", "nariz"}),
    ("leg", {"leg", "legs", "pata", "patas", "pierna", "thigh", "shin", "knee", "hip", "paw", "paws", "hoof", "hooves",
             "foot", "feet", "toe", "toes", "claw", "claws", "pie", "pies", "arm", "arms", "hand", "hands", "calf",
             "elbow", "forearm", "ankle", "hock", "wrist", "brazo"}),
    ("tail", {"tail", "tails", "cola", "rabo"}),
    ("neck", {"neck", "cuello"}),
    ("head", {"head", "skull", "face", "cabeza"}),
    ("body", {"body", "torso", "chest", "belly", "spine", "root", "all", "main", "base", "cuerpo", "hips", "pelvis",
              "waist", "back", "shoulders"}),
]
FRONT = (("shoulder", "upper_arm"), ("elbow", "forearm"), ("wrist", "front_foot"))
HIND = (("hip", "thigh"), ("knee", "shin"), ("hock", "hind_foot"))
CUT1 = {"front": (0.43, 0.86), "hind": (0.35, 0.70)}
CUT2 = {"front": 0.43 / 0.57, "hind": 0.35 / 0.65}


def role_of(name):
    t = D.tokens(name)
    if name.startswith("pw_") and t & {"neck", "spine", "shoulder", "elbow", "hip", "knee", "ankle"}:
        return "placeholder"
    for role, keys in ROLE_TOKENS:
        if t & keys:
            return role
    return "other"


def volume(b):
    return sum(abs(c["size"][0] * c["size"][1] * c["size"][2]) or 0.01 for c in b.get("cubes") or [])


def automap_quad(geo):
    bones = {b["name"]: b for b in geo["bones"]}
    kids = defaultdict(list)
    for b in geo["bones"]:
        kids[b.get("parent")].append(b["name"])
    role = {n: role_of(n) for n in bones}

    def inherit(n, under):
        if under and role[n] in ("other", "body"):
            role[n] = under
        nxt = role[n] if role[n] in ("leg", "tail", "ear", "horn") else under
        for k in kids[n]:
            inherit(k, nxt)
    for top in kids[None]:
        inherit(top, None)
    aff = bone_affines(geo["bones"])

    def wpos(n):
        b = bones[n]
        A, t = aff[n]
        cs = b.get("cubes") or []
        if cs:
            return np.mean([A @ CU.centre(c) + t for c in cs], axis=0)
        return A @ np.array(b.get("pivot", [0, 0, 0]), float) + t

    def wtop(n):
        A, t = aff[n]
        return A @ np.array(bones[n].get("pivot", [0, 0, 0]), float) + t
    mapping, splits, review, used = {}, {}, [], set()

    def take(old, new):
        base, k = new, 2
        while new in used:
            new = f"{base}_{k}"
            k += 1
        used.add(new)
        mapping[old] = new
        return new
    # WA "morph" humanoid sub-rig: its own morph_ namespace (as on the WA birds)
    if "body_human" in bones:
        top = "body_human"
        while bones[top].get("parent"):
            top = bones[top]["parent"]

        def under(n, anc):
            while n:
                if n == anc:
                    return True
                n = bones[n].get("parent")
            return False
        for n in bones:
            if n != top and under(n, top) and n != top:
                low = n.lower()
                s_ = "l" if low.startswith("left") or low == "la" else ("r" if low.startswith("right") or low == "ra" else "")
                base = ("arm" if "arm" in low else "forearm" if low in ("la", "ra") else "item" if "item" in low
                        else "body" if low == "body_human" else "waist" if low.startswith("waist") else low)
                take(n, f"morph_{base}" + (f"_{s_}" if s_ else ""))
                role[n] = "morph"
    # body: the largest torso piece; other torso pieces body_2 …; cubeless ancestors = root containers
    bodies = sorted([n for n in bones if role[n] == "body" and bones[n].get("cubes")], key=lambda n: -volume(bones[n]))
    if not bodies:  # no torso by name: the largest cube bone that is not a limb / head / tail
        cand = [n for n in bones if bones[n].get("cubes") and role[n] in ("other",)]
        bodies = sorted(cand, key=lambda n: -volume(bones[n]))[:1]
        for n in bodies:
            role[n] = "body"
    for n in bodies:
        take(n, "body")
    if bodies:
        p = bones[bodies[0]].get("parent")
        chain = []
        while p:
            chain.append(p)
            p = bones[p].get("parent")
        for n in reversed(chain):
            if n not in mapping and not bones[n].get("cubes") and role[n] in ("body", "other"):
                take(n, "root")
    for n in bones:
        if role[n] == "body" and n not in mapping:
            take(n, "body_frame" if not bones[n].get("cubes") else "body")
    body_c = np.mean([wpos(n) for n in bodies], axis=0) if bodies else np.zeros(3)
    # neck / head / snout / jaw / ears / horns
    for n in [n for n in bones if role[n] == "neck"]:
        take(n, "neck" if bones[n].get("cubes") else "neck_base")
    heads = sorted([n for n in bones if role[n] == "head"], key=lambda n: (not bones[n].get("cubes"), -volume(bones[n])))
    for i, n in enumerate(heads):
        if i == 0 and bones[n].get("cubes"):
            splits[n] = ("head", "skull")
            used.update(("head", "skull"))
        elif i == 0:
            take(n, "head")
        else:
            take(n, "head_frame" if not bones[n].get("cubes") else "skull")
    for n in sorted([n for n in bones if role[n] == "snout"], key=lambda n: -volume(bones[n])):
        take(n, "snout" if not re.search(r"trompa|trunk", n.lower()) else "trunk")
    for n in [n for n in bones if role[n] == "jaw"]:
        take(n, "jaw_lower")

    def side(n):
        x = float(wpos(n)[0])
        if x > 0.3:
            return "l"
        if x < -0.3:
            return "r"
        t = D.tokens(n)
        return "l" if t & LEFT else ("r" if t & RIGHT else "mid")
    for r in ("ear", "horn"):
        for n in [n for n in bones if role[n] == r]:
            s = side(n)
            base = r if r == "ear" else ("antler" if re.search(r"antler", n.lower()) else
                                         "tusk" if re.search(r"tusk|colmillo", n.lower()) else "horn")
            take(n, f"{base}_{s}" if s in ("l", "r") else base)
    # limbs (v2, 13:37): chains by HIERARCHY per side, then the side's chains paired front / hind; alternate models
    # (SF black bear: left_arm_berries / left_arm_honey drawn over the arm, shown by render controller) are not segments
    legs = [n for n in bones if role[n] == "leg"]

    def aabb(n):
        A, t = aff[n]
        P = np.array([A @ p + t for c in bones[n].get("cubes") or [] for p in CU.corners(c)])
        return P.min(axis=0), P.max(axis=0)

    def overlap(a, b):
        (la, ha), (lb, hb) = aabb(a), aabb(b)
        inter = np.clip(np.minimum(ha, hb) - np.maximum(la, lb), 0, None)
        va = np.prod(np.maximum(ha - la, 1e-3))
        return float(np.prod(inter) / va)
    alt = set()
    for n in legs:
        if not bones[n].get("cubes"):
            continue
        p = bones[n].get("parent")
        anc = p
        while anc in bones and not bones[anc].get("cubes") and role.get(anc) == "leg":
            anc = bones[anc].get("parent")
        if anc in bones and role.get(anc) == "leg" and bones[anc].get("cubes") and overlap(n, anc) > 0.6:
            alt.add(n)
    for n in list(alt):
        for k in [k for k in bones if k in legs]:
            q = k
            while q in bones:
                if q == n:
                    alt.add(k)
                    break
                q = bones[q].get("parent")
    legs_c = [n for n in legs if n not in alt]

    def desc_cubed(n):
        out = [n] if bones[n].get("cubes") else []
        for k in kids[n]:
            out += desc_cubed(k)
        return out

    def side_of(n):
        if bones[n].get("cubes"):
            x = float(wpos(n)[0])
            return "l" if x > 0.3 else ("r" if x < -0.3 else "mid")
        # a cubeless leg bone takes the side of the cubes under it; cubes on BOTH sides = a container (SF badger `legs`
        # pivots at x 2.5 but holds all four legs)
        xs = [float(wpos(k)[0]) for k in desc_cubed(n) if k in legs_c]
        if not xs:
            x = float(wtop(n)[0])
            return "l" if x > 0.3 else ("r" if x < -0.3 else "mid")
        if min(xs) < -0.3 and max(xs) > 0.3:
            return "mid"
        return "l" if sum(xs) > 0 else "r"
    sided = {n: side_of(n) for n in legs_c}
    chains = defaultdict(list)
    for s_ in ("l", "r"):
        ms = {n for n in legs_c if sided[n] == s_}

        def has_c(n):
            return bool(bones[n].get("cubes")) or any(has_c(k) for k in kids[n] if k in ms)

        def grow(n, prefix, s_=s_, ms=ms):
            # a node whose leg children branch into >= 2 cube-carrying legs is a CONTAINER: each branch its own limb
            br = [k for k in kids[n] if k in ms and has_c(k)]
            path = prefix + [n]
            if len(br) >= 2:
                if bones[n].get("cubes"):
                    chains[s_].append(path)
                for k in br:
                    grow(k, [])
            elif br:
                grow(br[0], path)
            elif any(bones[x].get("cubes") for x in path):
                chains[s_].append(path)
        for t in [n for n in ms if bones[n].get("parent") not in ms]:
            grow(t, [])
    limbs = {}
    for s_, chs in chains.items():
        if len(chs) >= 2:
            tops = [wtop(c[0]) for c in chs]
            zs, ys = [float(t[2]) for t in tops], [float(t[1]) for t in tops]
            key = (lambda i: -ys[i]) if max(ys) - min(ys) > max(zs) - min(zs) else (lambda i: zs[i])
            order_ = sorted(range(len(chs)), key=key)
            limbs[(s_, "front")] = chs[order_[0]]
            limbs[(s_, "hind")] = chs[order_[-1]]
        elif chs:
            limbs[(s_, "front" if float(wtop(chs[0][0])[2]) < body_c[2] else "hind")] = chs[0]
    info = {}
    for (s, fh), order in limbs.items():
        mem = set(order)
        names = FRONT if fh == "front" else HIND
        toe = "front_toe" if fh == "front" else "hind_toe"
        pi = 0
        pieces = []
        for n in order:
            b = bones[n]
            if b.get("cubes"):
                if pi < 3:
                    j_, pc = f"{names[pi][0]}_{s}", f"{names[pi][1]}_{s}"
                else:
                    j_, pc = f"{toe}_base_{s}_{pi - 2}", f"{toe}_{s}_{pi - 2}"
                par = b.get("parent")
                if par in mapping and mapping[par] == j_ and len([k for k in kids[par]]) == 1:
                    take(n, pc)
                else:
                    splits[n] = (j_, pc)
                    used.update((j_, pc))
                pieces.append(pc)
                pi += 1
            else:
                ch = kids[n]
                nxt = names[pi][0] + f"_{s}" if pi < 3 else f"{toe}_base_{s}_{pi - 2}"
                if len(ch) == 1 and bones[ch[0]].get("cubes") and ch[0] in mem and nxt not in used:
                    take(n, nxt)
                else:
                    take(n, f"{(names[min(pi, 2)][0])}_{s}_frame")
        info[f"{fh}_{s}"] = pieces
    legs = [n for n in legs if n not in alt]
    for n in [n for n in legs if n not in mapping and n not in splits]:
        take(n, "legs_frame" if not bones[n].get("cubes") else "legs")
    # tail chain
    tails = [n for n in bones if role[n] == "tail" and n not in mapping and n not in splits]
    for n in tails:
        take(n, "tail" if bones[n].get("cubes") else "tail_base")
    # placeholders (his Q2) keep their name here; removed after conversion when nothing references them
    for n in bones:
        if n not in mapping and n not in splits and role[n] != "placeholder":
            review.append(n)
    keep = {n for n in bones if n not in mapping and n not in splits}
    for k, v in list(mapping.items()):
        if v in keep and v != k:
            i = 2
            while f"{v}_{i}" in used or f"{v}_{i}" in keep:
                i += 1
            mapping[k] = f"{v}_{i}"
            used.add(mapping[k])
    for k, (j, p) in list(splits.items()):
        for x in (j, p):
            assert x not in keep or x == k, f"split name {x} collides with a kept bone"
    mapping = {k: v for k, v in mapping.items() if k != v}
    return mapping, splits, review, info


def baby_map(adult_geo, adult_map, adult_splits, geo):
    m2, s2, _, _ = automap_quad(geo)
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
    keep = {n for n in names if n not in m2 and n not in s2}
    for k in list(m2):
        if k not in shared and (list(m2.values()).count(m2[k]) > 1 or m2[k] in keep):
            del m2[k]
    # a baby-only decision whose names the shared (adult) decisions already produce: dropped (SF zebra baby: its own
    # `skull2` was split to head + skull, as the shared `skull`)
    shared_names = {m2[k] for k in shared if k in m2} | {x for k in shared if k in s2 for x in s2[k]}
    for k in [k for k in s2 if k not in shared]:
        if set(s2[k]) & shared_names:
            del s2[k]
    for k in [k for k in m2 if k not in shared]:
        if m2[k] in shared_names:
            del m2[k]
    return m2, s2


# ------------------------------------------------------------------ step 2: leg cuts
def cut_piece(g, piece, fractions, new_names, joint_of_piece):
    """cut `piece` (a cube bone) along its length into len(fractions) + 1 slabs; slab 0 stays in `piece`, slab k goes to
    new_names[k-1] = (joint, piece) chained under the previous piece; children of `piece` move to the last slab."""
    by = SC.bones_of(g)
    P_ = by[piece]
    cubes = P_.get("cubes", [])
    if not cubes:
        return None   # (a baby geometry whose piece of that name is empty)
    P_.pop("cubes")
    piv = np.array(by[joint_of_piece].get("pivot", [0, 0, 0]), float)
    # tilted cubes (WA / YSav legs): cut in the cubes' own frame — all of the piece's cubes must share one rotation +
    # pivot; the joint pivot goes into that frame, the new joints' pivots come back out of it
    rots = {(tuple(c.get("rotation") or [0, 0, 0]), tuple(c.get("pivot") or [0, 0, 0])) for c in cubes}
    if len(rots) > 1:
        P_["cubes"] = cubes
        raise AssertionError("leg cubes with different rotations")
    Rq = CU.cube_R(cubes[0])
    q = np.array(cubes[0].get("pivot") or [0, 0, 0], float)
    piv = Rq.T @ (piv - q) + q
    axis = W.span_axis(cubes, piv)
    lo = min(min(c["origin"][axis], c["origin"][axis] + c["size"][axis]) for c in cubes)
    hi = max(max(c["origin"][axis], c["origin"][axis] + c["size"][axis]) for c in cubes)
    near_lo = abs(piv[axis] - lo) <= abs(piv[axis] - hi)
    cuts = [lo + f * (hi - lo) if near_lo else hi - f * (hi - lo) for f in fractions]
    edges = sorted([lo, hi] + cuts)
    n_sl = len(fractions) + 1
    slabs = [[] for _ in range(n_sl)]
    for c in cubes:
        cs = copy.deepcopy(c)
        cs.setdefault("mirror", bool(P_.get("mirror", False)))
        for a, b, nc in W.cut_cube(cs, axis, sorted(cuts)):
            mid = (a + b) / 2
            k = sum(1 for e in edges[1:-1] if mid > e) if near_lo else sum(1 for e in edges[1:-1] if mid < e)
            slabs[k].append(nc)
    P_["cubes"] = slabs[0]
    others = [k for k in range(3) if k != axis]
    centre = {k: (min(min(c["origin"][k], c["origin"][k] + c["size"][k]) for c in cubes) +
                  max(max(c["origin"][k], c["origin"][k] + c["size"][k]) for c in cubes)) / 2 for k in others}
    old_children = [b for b in g["bones"] if b.get("parent") == piece]
    prev = piece
    at = g["bones"].index(P_) + 1
    for i, (jn, pn) in enumerate(new_names):
        p = [0.0, 0.0, 0.0]
        p[axis] = cuts[i]
        for k in others:
            p[k] = centre[k]
        pf = Rq @ (np.array(p) - q) + q          # back to the file frame
        g["bones"][at:at] = [{"name": jn, "parent": prev, "pivot": [round(float(x), 5) for x in pf]},
                             {"name": pn, "parent": jn, "pivot": [round(float(x), 5) for x in pf], "cubes": slabs[i + 1]}]
        at += 2
        prev = pn
    for b in old_children:
        b["parent"] = prev
    return axis


def leg_cuts(g, info):
    log = []
    names = {b["name"] for b in g["bones"]}
    for key, pieces in info.items():
        fh, s = key.split("_")
        tmpl = FRONT if fh == "front" else HIND
        have = [p for p in pieces if p in names]
        if not have:
            continue
        try:
            if len(have) == 1:
                p0 = have[0]
                if p0 != f"{tmpl[0][1]}_{s}":
                    continue
                cut_piece(g, p0, CUT1[fh], [(f"{tmpl[1][0]}_{s}", f"{tmpl[1][1]}_{s}"),
                                            (f"{tmpl[2][0]}_{s}", f"{tmpl[2][1]}_{s}")], f"{tmpl[0][0]}_{s}")
                log.append(f"{key}: 1 -> 3")
            elif len(have) == 2:
                p1 = have[1]
                if p1 != f"{tmpl[1][1]}_{s}":
                    continue
                cut_piece(g, p1, (CUT2[fh],), [(f"{tmpl[2][0]}_{s}", f"{tmpl[2][1]}_{s}")], f"{tmpl[1][0]}_{s}")
                log.append(f"{key}: 2 -> 3")
        except AssertionError as e:   # a limb whose cubes turn different ways stays as it is; the mob goes on
            log.append(f"{key}: not cut ({e})")
    return log


def drop_dangling(P, mob, st, mapping, splits, per_geo):
    """animation channels that name a bone the ORIGINAL geometry does not have did nothing; after renaming they could
    land on a NEW bone of that name (AnF grizzly: its idle drives a non-existent `head`, and the standard `head` joint
    now exists -> 3,240 texel misses). Every staged animation is rebuilt from the original keeping real bones only."""
    ef, desc = P.entities[mob]
    real = set()
    for gid in set((desc.get("geometry") or {}).values()):
        real |= {b["name"] for b in P.geos[gid]["bones"]}
    all_map, all_split = dict(mapping), dict(splits)
    for m_, s_ in per_geo.values():
        all_map.update(m_)
        all_split.update(s_)
    slug = S.slug_of(mob)
    n = 0
    for short, aid in (desc.get("animations") or {}).items():
        if aid.startswith("controller.") or aid not in P.anims:
            continue
        new_id = f"animation.std.{slug}." + re.sub(r"^animation\.", "", aid)
        a = st.anim["animations"].get(new_id)
        old = P.anims[aid].get("bones") or {}
        if a is None or not old:
            continue
        dang = [k for k in old if k not in real]
        if dang:
            a["bones"] = {S.rename_key(k, all_map, all_split): copy.deepcopy(v) for k, v in old.items() if k in real}
            n += len(dang)
    return n


def drop_placeholders(st):
    referenced = set()
    for a in st.anim["animations"].values():
        referenced |= set(a.get("bones") or {})
    if st.rc:
        for r in st.rc["render_controllers"].values():
            for pv in r.get("part_visibility", []):
                referenced |= set(pv)
    n = 0
    for g in st.geo["minecraft:geometry"]:
        parents = {b.get("parent") for b in g["bones"]}
        keep = []
        for b in g["bones"]:
            if b["name"].startswith("pw_") and not b.get("cubes") and b["name"] not in parents and b["name"] not in referenced:
                n += 1
                continue
            keep.append(b)
        g["bones"] = keep
    return n


_GEO_INDEX = None


def Q_ensure_geos(P, desc):
    """geometries the entity names but its pack does not hold (vanilla legacy files, another pack of the stack): from
    the census geometry index (mers_derive.geo_index), which reads every pack + vanilla."""
    global _GEO_INDEX
    for gid in set((desc.get("geometry") or {}).values()):
        if gid not in P.geos:
            if _GEO_INDEX is None:
                import mers_derive as _D
                _GEO_INDEX = _D.geo_index()
            if gid in _GEO_INDEX:
                P.geos[gid] = _GEO_INDEX[gid]


def main(ids=None):
    import std_birds_b as BB
    census = json.loads((ROOT / "_docs/standard/SKELETON-CENSUS.json").read_text())
    todo = [c for c in census if c["body_plan"] in ("quadruped",)]
    if ids:
        todo = [c for c in todo if c["id"] in ids]
    packs = {}
    lines = ["# QUADRUPEDS — standard names + real leg joints (Phase 2b)", "",
             "| mob | gate (moments / texel misses) | limbs (pieces before) | cuts | placeholders removed | kept for review |",
             "|---|---|---|---|---|---|"]
    detail = []
    for c in todo:
        rp = c["rp"].replace("rp07-1438", "rp07-1439").replace("rp06-1424", "rp06-1425").replace("rp08-148", "rp08-149")
        if rp not in packs:   # vanilla entities ("resource_pack") stage from the vanilla samples; they ship in RP-07
            packs[rp] = S.Pack(S.VANILLA if rp == "resource_pack" else ROOT / "_build" / rp)
        P = packs[rp]
        mob = c["id"]
        try:
            ef, desc = P.entities[mob]
            Q_ensure_geos(P, desc)
            gid = c["geometry"]
            geo = P.geos[gid]
            mapping, splits, review, info = automap_quad(geo)
            per_geo = {}
            dec_m, dec_s = dict(mapping), dict(splits)      # decisions so far: a bone name decided once stays decided
            decided = {b["name"] for b in geo["bones"]}     # (kept-as-is is a decision too)
            for g in sorted(set((desc.get("geometry") or {}).values()) - {gid}):
                m_, s_ = baby_map(geo, mapping, splits, P.geos[g])
                names_g = {b["name"] for b in P.geos[g]["bones"]}
                for k in names_g & decided:
                    m_.pop(k, None)
                    s_.pop(k, None)
                    if k in dec_s:
                        s_[k] = dec_s[k]
                    elif k in dec_m:
                        m_[k] = dec_m[k]
                # a new name already produced by an earlier decision for ANOTHER bone: keep this bone's own name
                taken = set(dec_m.values()) | {x for v in dec_s.values() for x in v}
                for k in [k for k in m_ if k not in dec_m and m_[k] in taken]:
                    del m_[k]
                for k in [k for k in s_ if k not in dec_s and set(s_[k]) & taken]:
                    del s_[k]
                dec_m.update(m_)
                dec_s.update(s_)
                decided |= names_g
                per_geo[g] = (m_, s_)
            sinfo = S.convert(P, mob, mapping, splits, per_geo)
            st = SC.Staged(P.path.name, mob)
            log = []
            for g in st.geo["minecraft:geometry"]:
                gi = info if g["description"]["identifier"] == sinfo["geometry"][gid] else \
                    {k: v for k, v in info.items()}
                log += leg_cuts(g, gi)
            dropped = drop_placeholders(st)
            dang = drop_dangling(P, mob, st, mapping, splits, per_geo)
            if dang:
                log.append(f"{dang} dangling channels dropped")
            st.save()
            n, miss, unrun = BB.gate_uv(P, mob, sinfo, (S.GROUND, S.IDLE), [0.0, 0.35, 0.7])
            gate_s = f"{n} / {miss}" + (f" (not run: {', '.join(unrun)[:40]})" if unrun else "")
        except Exception as e:  # noqa: BLE001
            gate_s, log, dropped, info, review, mapping, splits = f"REFUSED {str(e)[:70]}", [], 0, {}, [], {}, {}
        limbs = ", ".join(f"{k} {len(v)}" for k, v in sorted(info.items()))
        lines.append(f"| {mob} | {gate_s} | {limbs} | {'; '.join(sorted(set(log)))} | {dropped} | {', '.join(review[:8])} |")
        detail.append(f"\n### {mob}\n" + "\n".join(f"- `{k}` → `{v}`" for k, v in mapping.items()) +
                      ("\n" + "\n".join(f"- `{k}` → joint `{j}` + piece `{p}`" for k, (j, p) in splits.items()) if splits else ""))
        print(mob, gate_s, limbs, sorted(set(log)), flush=True)
    (ROOT / "_docs/standard/QUAD-STANDARD.md").write_text("\n".join(lines + ["", "## Mappings"] + detail) + "\n")


if __name__ == "__main__":
    main(sys.argv[1:] or None)
