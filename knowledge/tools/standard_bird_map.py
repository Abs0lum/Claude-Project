#!/usr/bin/env python3
"""standard_bird_map.py — Standardization Phase 1 (birds first): how far each flying / bird-like mob's rig is from the
Patrix parrot flight template (D-C364 / his 02:20 + F1: phantom + bat join the flight standard).

Per mob: every bone gets a ROLE (body, neck, head, beak, crest, wing, leg, foot, tail, other) and a SIDE (l / r / mid) from
its name tokens (token-exact) and, for an unnamed side, its pivot x (+x = the mob's left, as the parrot's left_wing2 at x +1.7).
Wing chains are read through the hierarchy: a wing bone's descendants belong to that wing. Measured per side:
  joints  = wing bones in the longest root->tip chain (1 = one stiff plate, 2 = shoulder + hinge, 3 = shoulder + elbow + wrist)
  pieces  = wing bones that carry cubes
The template needs >= 2 joints and >= 2 pieces per wing (inner + outer across a true hinge) — the parrot has 4 joints
(shoulder, fly_rot, fly2, hinge) and 4 pieces (inner + 3 primaries) on its flight wing.
Writes _docs/standard/BIRD-RIG-MAP.json and prints the summary.
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import mers_derive as D  # noqa: E402  (geo_index, tokens)

ROLE_TOKENS = [  # first match wins, checked in this order
    ("beak", {"beak", "bill", "beaks", "mouth", "jaw", "mandible", "pico", "boca"}),
    ("crest", {"crest", "comb", "wattle", "feathers", "feather", "tuft", "plume", "crown"}),
    ("foot", {"foot", "feet", "claw", "claws", "talon", "talons", "toe", "toes", "ankle", "pie", "pies", "garra", "garras"}),
    ("wing", {"wing", "wings", "arm", "arms", "membrane", "primary", "primaries", "secondary", "ala", "alas"}),
    ("leg", {"leg", "legs", "thigh", "shin", "knee", "hip", "pata", "patas", "pierna"}),
    ("tail", {"tail", "tails", "tailfeathers", "cola"}),
    ("neck", {"neck", "cuello"}),
    ("head", {"head", "skull", "face", "eye", "eyes", "cabeza"}),
    ("body", {"body", "torso", "chest", "belly", "spine", "root", "all", "main", "base", "cuerpo"}),
]
LEFT, RIGHT = {"left", "l", "lft"}, {"right", "r", "rgt"}
FLIERS = {"minecraft:phantom", "minecraft:bat"}


def role_of(name):
    t = D.tokens(name)
    for role, keys in ROLE_TOKENS:
        if t & keys:
            return role
    return "other"


def side_of(bone):
    t = D.tokens(bone["name"])
    if t & LEFT:
        return "l"
    if t & RIGHT:
        return "r"
    if bone.get("cubes"):  # where the bone's cubes sit decides (some rigs share one pivot for both wings: owl_ytri)
        xs = [c.get("origin", [0, 0, 0])[0] + abs(c.get("size", [0, 0, 0])[0]) / 2 for c in bone["cubes"]]
        x = sum(xs) / len(xs)
    else:
        x = (bone.get("pivot") or [0, 0, 0])[0]
    return "l" if x > 0.25 else ("r" if x < -0.25 else "mid")


def analyse(geo):
    bones = {b["name"]: b for b in geo.get("bones") or []}
    kids = {}
    for b in bones.values():
        kids.setdefault(b.get("parent"), []).append(b["name"])
    roles = {n: role_of(n) for n in bones}
    # inherit 'wing' down the hierarchy: anything under a wing bone (bone5, bone10 …) is that wing's piece
    def inherit(n, under_wing, side):
        r = roles[n]
        if under_wing and r in ("other", "body"):
            roles[n] = "wing"
        s = side_of(bones[n]) if not under_wing else side
        for k in kids.get(n, []):
            inherit(k, under_wing or roles[n] == "wing", s if under_wing or roles[n] == "wing" else None)
    for top in kids.get(None, []):
        inherit(top, False, None)
    out = {"bones": len(bones), "cubes": sum(len(b.get("cubes") or []) for b in bones.values())}
    for side in ("l", "r"):
        wing = [n for n in bones if roles[n] == "wing" and side_of(bones[n]) == side]
        # longest chain of wing bones
        wing_set = set(wing)

        def depth(n):
            ks = [k for k in kids.get(n, []) if k in wing_set]
            return 1 + max((depth(k) for k in ks), default=0)
        tops = [n for n in wing if bones[n].get("parent") not in wing_set]  # a shared midline 'wings' parent is not this side's joint
        out[f"wing_{side}_joints"] = max((depth(n) for n in tops), default=0)
        out[f"wing_{side}_pieces"] = sum(1 for n in wing if bones[n].get("cubes"))
    c = Counter(roles.values())
    for r in ("head", "neck", "beak", "crest", "leg", "foot", "tail", "body"):
        out[r] = c.get(r, 0)
    out["other"] = sorted(n for n in bones if roles[n] == "other" and bones[n].get("cubes"))[:12]
    return out


def main():
    census = json.loads((ROOT / "_docs/standard/SKELETON-CENSUS.json").read_text())
    idx = D.geo_index()
    rows = []
    for c in census:
        if c["body_plan"] not in ("bird", "bat") and c["id"] not in FLIERS:
            continue
        g = idx.get(c["geometry"])
        if not g:
            continue
        a = analyse(g)
        joints = min(a["wing_l_joints"], a["wing_r_joints"])
        pieces = min(a["wing_l_pieces"], a["wing_r_pieces"])
        a.update({"id": c["id"], "source": c["source"], "geometry": c["geometry"],
                  "flies": "fly" in (c.get("animations") or {}) or c["id"] in FLIERS,
                  "class": ("TEMPLATE-READY" if joints >= 2 and pieces >= 2 else
                            "SPLIT-NEEDED" if joints >= 1 and pieces >= 1 else "NO-WINGS-FOUND")})
        rows.append(a)
    out = ROOT / "_docs/standard/BIRD-RIG-MAP.json"
    out.write_text(json.dumps(rows, indent=1))
    print(len(rows), "bird-like mobs;", Counter(r["class"] for r in rows))
    print("fliers (fly animation or F1):", sum(r["flies"] for r in rows), Counter(r["class"] for r in rows if r["flies"]))
    print("joints per wing:", Counter(min(r["wing_l_joints"], r["wing_r_joints"]) for r in rows))
    print("pieces per wing:", Counter(min(r["wing_l_pieces"], r["wing_r_pieces"]) for r in rows))
    print("no neck bone:", sum(1 for r in rows if not r["neck"]), " no foot bone:", sum(1 for r in rows if not r["foot"]),
          " no tail:", sum(1 for r in rows if not r["tail"]), " no beak bone:", sum(1 for r in rows if not r["beak"]))
    for r in rows:
        if r["class"] == "NO-WINGS-FOUND":
            print("  NO-WINGS:", r["id"], r["other"][:6])
    print(out)


if __name__ == "__main__":
    main()
