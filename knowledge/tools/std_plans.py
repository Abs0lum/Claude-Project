#!/usr/bin/env python3
"""std_plans.py — Phase 2b for every body plan other than birds and quadrupeds (TEMPLATES-OTHER-PLANS v1; his T1 naming
language for ALL mobs, the "one step past Patrix" principle, D1 = b). Same converter and gate as the birds / quadrupeds:
a COPY of each rig with standard names (std_convert), new joints at rotation 0, every texel kept, gated identical
under every one of the mob's animations (UV-sample correspondence).

Kinds:
  limbed     lizard / crocodilian, ape, amphibian, macropod, turtle, pinniped — four limbs. Limb tops are found from the
             leg bones' bind-pose WORLD position: side by x; the two limbs of a side are FRONT / HIND by z (an upright
             ape: by height when the height difference is larger). Pieces take the plan's names; one-piece limbs are cut
             to the plan's piece count (std_quad.cut_piece: per-face UV sub-rectangles).
  legs       insects, arachnids, crustaceans — n leg pairs numbered from the front (k = 1 … n): hip_k_<s> -> femur_k_<s>,
             knee_k_<s> -> tibia_k_<s>, ankle_k_<s> -> foot_k_<s> (+ tarsus); insect one-piece legs cut to 3, crustacean
             to 2. Wings (insects): wing_root_<s> -> wing_<s>, a second pair wing_root_hind_<s> -> wing_hind_<s>.
  chain      fish, cetacean, snake, cephalopod, jellyfish — names only: body, body_2 … (front to back), head / skull,
             jaw_lower, tail chain tail, tail_2 …, fins / flippers by side and place, tentacle_k.
  keep       humanoid, fantasy — their rigs ARE the standard (Patrix / vanilla, H1 = my recommendation he deferred to):
             no conversion; engine-bound names (armour, items, player-style animations) stay.
Writes _docs/standard/PLANS-STANDARD.md."""
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
import std_quad as Q  # noqa: E402
import std_cube as CU  # noqa: E402
from equine_compare import bone_affines  # noqa: E402

LIMBED = {
    "lizard_croc": ((("shoulder", "upper_arm"), ("elbow", "forearm"), ("wrist", "front_foot")),
                    (("hip", "thigh"), ("knee", "shin"), ("ankle", "hind_foot"))),
    "biped_ape": ((("shoulder", "upper_arm"), ("elbow", "forearm"), ("wrist", "hand")),
                  (("hip", "thigh"), ("knee", "shin"), ("ankle", "foot"))),
    "amphibian": ((("shoulder", "upper_arm"), ("elbow", "forearm"), ("wrist", "hand")),
                  (("hip", "thigh"), ("knee", "shin"), ("ankle", "foot"))),
    "macropod": ((("shoulder", "upper_arm"), ("elbow", "forearm"), ("wrist", "paw")),
                 (("hip", "thigh"), ("knee", "shin"), ("ankle", "foot"))),
    "turtle": ((("shoulder", "upper_arm"), ("elbow", "front_foot")), (("hip", "thigh"), ("knee", "hind_foot"))),
    "pinniped": ((("shoulder", "fore_upper"), ("elbow", "fore_flipper")), (("hip", "hind_flipper"),)),
}
LEGS = {"insect_flying": 3, "insect_walking": 3, "arachnid": 3, "crustacean": 2}
CHAIN = {"fish", "cetacean", "snake", "cephalopod", "jellyfish"}
KEEP = {"humanoid", "fantasy", "object"}
CUTS = {3: {"front": (0.43, 0.86), "hind": (0.35, 0.70)}, 2: {"front": (0.5,), "hind": (0.5,)}}
LEG_NAMES = (("hip", "femur"), ("knee", "tibia"), ("ankle", "foot"))

ROLE = [
    ("wing", {"wing", "wings", "ala", "alas", "elytra", "forewing", "hindwing"}),
    ("antenna", {"antenna", "antennae", "antennas", "feeler", "feelers"}),
    ("ear", {"ear", "ears", "oreja", "orejas"}),
    ("horn", {"horn", "horns", "antler", "antlers", "tusk", "tusks", "colmillo", "colmillos"}),
    ("jaw", {"jaw", "mandible", "mandibles", "sob", "lower", "chin", "mund0", "mund1", "pincer", "pincers", "chelicera"}),
    ("tentacle", {"tentacle", "tentacles", "tentaculo"}),
    ("fin", {"fin", "fins", "flipper", "flippers", "aleta", "fluke", "fern", "gills", "gill"}),
    ("claw", {"claw", "claws", "pinza", "chela"}),
    ("leg", {"leg", "legs", "pata", "patas", "pierna", "thigh", "shin", "knee", "hip", "paw", "paws", "foot", "feet",
             "toe", "toes", "arm", "arms", "hand", "hands", "forearm", "elbow", "wrist", "ankle", "glove", "palp",
             "pedipalp", "femur", "tibia", "tarsus"}),
    ("tail", {"tail", "tails", "cola", "rabo", "stinger"}),
    ("neck", {"neck", "cuello"}),
    ("head", {"head", "skull", "face", "cabeza"}),
    ("abdomen", {"abdomen"}),
    ("thorax", {"thorax", "torso", "chest"}),
    ("body", {"body", "spine", "root", "all", "main", "base", "cuerpo", "hips", "pelvis", "waist", "back", "shell",
              "carapace", "mantle", "bell"}),
]


def role_of(name):
    t = D.tokens(name)
    if name.startswith("pw_") and t & {"neck", "spine", "shoulder", "elbow", "hip", "knee", "ankle"}:
        return "placeholder"
    for role, keys in ROLE:
        if t & keys:
            return role
    return "other"


class Rig:
    def __init__(self, geo):
        self.geo = geo
        self.bones = {b["name"]: b for b in geo["bones"]}
        self.kids = defaultdict(list)
        for b in geo["bones"]:
            self.kids[b.get("parent")].append(b["name"])
        self.aff = bone_affines(geo["bones"])
        self.role = {n: role_of(n) for n in self.bones}
        self.mapping, self.splits, self.used = {}, {}, set()

        def inherit(n, under):
            if under and self.role[n] in ("other", "body"):
                self.role[n] = under
            nxt = self.role[n] if self.role[n] in ("leg", "tail", "wing", "fin", "tentacle", "antenna", "claw", "ear",
                                                   "horn") else under
            for k in self.kids[n]:
                inherit(k, nxt)
        for top in self.kids[None]:
            inherit(top, None)

    def wpos(self, n):
        b = self.bones[n]
        A, t = self.aff[n]
        cs = b.get("cubes") or []
        if cs:
            return np.mean([A @ CU.centre(c) + t for c in cs], axis=0)
        return A @ np.array(b.get("pivot", [0, 0, 0]), float) + t

    def wtop(self, n):
        A, t = self.aff[n]
        return A @ np.array(self.bones[n].get("pivot", [0, 0, 0]), float) + t

    def mid_x(self):
        """17:1x (whale_wwa): the rig's midline = the x centre of all its cubes' bounding box (0 for the usual centred rig;
        the WA humpback is modelled at x = 2, which put its jaw and fin container on the left)."""
        if not hasattr(self, "_mid"):
            pts = [self.aff[n][0] @ p + self.aff[n][1] for n, b in self.bones.items() for c in (b.get("cubes") or [])
                   for p in CU.corners(c)]
            self._mid = float((min(p[0] for p in pts) + max(p[0] for p in pts)) / 2) if pts else 0.0
        return self._mid

    def side(self, n, eps=0.3):
        x = float(self.wpos(n)[0]) - self.mid_x()
        if x > eps:
            return "l"
        if x < -eps:
            return "r"
        t = D.tokens(n)
        return "l" if t & Q.LEFT else ("r" if t & Q.RIGHT else "mid")

    def take(self, old, new):
        if old in self.mapping or old in self.splits:
            return
        base, k = new, 2
        while new in self.used:
            new = f"{base}_{k}"
            k += 1
        self.used.add(new)
        self.mapping[old] = new

    def split(self, old, joint, piece):
        if old in self.mapping or old in self.splits:
            return
        for x in (joint, piece):
            assert x not in self.used, f"name {x} used twice"
        self.used.update((joint, piece))
        self.splits[old] = (joint, piece)

    def order(self, members):
        mem = set(members)
        out = []

        def walk(n):
            if n in mem:
                out.append(n)
            for k in self.kids[n]:
                walk(k)
        for t in [n for n in members if self.bones[n].get("parent") not in mem]:
            walk(t)
        return out

    # ------------------------------------------------------------ common: body / head / face / tail
    def core(self):
        B = self.bones
        vol = Q.volume
        bodies = sorted([n for n in B if self.role[n] in ("body", "thorax") and B[n].get("cubes")], key=lambda n: -vol(B[n]))
        if not bodies:
            cand = [n for n in B if B[n].get("cubes") and self.role[n] == "other"]
            bodies = sorted(cand, key=lambda n: -vol(B[n]))[:1]
        # front to back for the numbered segments
        bodies_fb = sorted(bodies, key=lambda n: float(self.wpos(n)[2]))
        if bodies:
            self.take(bodies[0], "body")
            for n in bodies_fb:
                if n != bodies[0]:
                    self.take(n, "body")
            p = B[bodies[0]].get("parent")
            chain = []
            while p:
                chain.append(p)
                p = B[p].get("parent")
            for n in reversed(chain):
                if not B[n].get("cubes") and self.role[n] in ("body", "other", "thorax"):
                    self.take(n, "root")
        for n in B:
            if self.role[n] in ("body", "thorax"):
                self.take(n, "body_frame" if not B[n].get("cubes") else "body")
        for n in [n for n in B if self.role[n] == "abdomen"]:
            self.take(n, "abdomen" if B[n].get("cubes") else "abdomen_joint")
        for n in [n for n in B if self.role[n] == "neck"]:
            self.take(n, "neck" if B[n].get("cubes") else "neck_base")
        heads = sorted([n for n in B if self.role[n] == "head"], key=lambda n: (not B[n].get("cubes"), -vol(B[n])))
        for i, n in enumerate(heads):
            if i == 0 and B[n].get("cubes"):
                self.split(n, "head", "skull")
            elif i == 0:
                self.take(n, "head")
            else:
                self.take(n, "head_frame" if not B[n].get("cubes") else "skull")
        for n in [n for n in B if self.role[n] == "jaw"]:
            s = self.side(n)
            self.take(n, "jaw_lower" if s == "mid" else f"mandible_{s}")
        for r, base in (("ear", "ear"), ("horn", "horn"), ("antenna", "antenna"), ("claw", "claw")):
            for n in self.order([n for n in B if self.role[n] == r]):
                s = self.side(n)
                self.take(n, f"{base}_{s}" if s in ("l", "r") else base)
        tails = self.order([n for n in B if self.role[n] == "tail"])
        k = 0
        for n in tails:
            if not B[n].get("cubes"):
                self.take(n, "tail_base" if k == 0 else f"tail_joint_{k + 1}")
            else:
                k += 1
                self.take(n, "tail" if k == 1 else f"tail_{k}")
        for n in [n for n in B if self.role[n] == "fin"]:
            if not B[n].get("cubes") and any(B[k].get("parent") == n for k in B):
                self.take(n, "fin_frame")      # 17:1x: a cubeless container of fins (whale_wwa `fins`) is not itself a fin
                continue
            s = self.side(n)
            p = self.wpos(n)
            if s in ("l", "r"):
                self.take(n, f"fin_{s}")
            else:
                self.take(n, "fin_dorsal" if p[1] >= float(self.wpos(self.mapping_inv("body"))[1] if self.mapping_inv("body") else 0) else "fin_ventral")
        for i, n in enumerate(self.order([n for n in B if self.role[n] == "tentacle"])):
            self.take(n, f"tentacle_{i + 1}" if B[n].get("cubes") else f"tentacle_joint_{i + 1}")

    def mapping_inv(self, new):
        for k, v in self.mapping.items():
            if v == new:
                return k
        for k, (j, p) in self.splits.items():
            if p == new or j == new:
                return k
        return None

    # ------------------------------------------------------------ limbs: chains per side
    def limb_chains(self, roles=("leg",)):
        """{(side, i)}: chains (top -> bottom) of leg bones, one per limb; tops = a leg bone whose parent is not a leg bone
        of the same side (a midline container is not a limb)."""
        B = self.bones
        legs = [n for n in B if self.role[n] in roles and n not in self.mapping and n not in self.splits]
        sided = {n: self.side(n) for n in legs}
        chains = defaultdict(list)
        for s in ("l", "r"):
            mem = [n for n in legs if sided[n] == s]
            ms = set(mem)
            tops = [n for n in mem if B[n].get("parent") not in ms]
            def has_cubes(n):
                return bool(B[n].get("cubes")) or any(has_cubes(k) for k in self.kids[n] if k in ms)

            def grow(n, prefix):
                # a node whose leg children branch into >= 2 cube-carrying legs is a CONTAINER (AnF beetle
                # legs_left -> leg_left_1..3, crab leg_left -> pivots): each branch is its own leg
                kids_ = [k for k in self.kids[n] if k in ms and has_cubes(k)]
                path = prefix + [n]
                if len(kids_) >= 2:
                    if B[n].get("cubes"):
                        chains[s].append(path)
                    for k in kids_:
                        grow(k, [])
                elif kids_:
                    grow(kids_[0], path)
                elif any(B[x].get("cubes") for x in path):
                    chains[s].append(path)
            for t in tops:
                grow(t, [])
        return chains, [n for n in legs if sided[n] == "mid"]

    def name_chain(self, ch, names, extra_joint, extra_piece):
        """map a limb chain onto (joint, piece) names; returns the piece names in order."""
        B = self.bones
        pi = 0
        pieces = []
        for n in ch:
            if B[n].get("cubes"):
                j, pc = (names[pi] if pi < len(names) else (f"{extra_joint}_{pi - len(names) + 1}",
                                                             f"{extra_piece}_{pi - len(names) + 1}"))
                par = B[n].get("parent")
                if par in self.mapping and self.mapping[par] == j and len(self.kids[par]) == 1:
                    self.take(n, pc)
                else:
                    self.split(n, j, pc)
                pieces.append(pc)
                pi += 1
            else:
                kids = self.kids[n]
                nxt = names[pi][0] if pi < len(names) else f"{extra_joint}_{pi - len(names) + 1}"
                if len(kids) == 1 and B[kids[0]].get("cubes") and kids[0] in ch and nxt not in self.used:
                    self.take(n, nxt)
                else:
                    self.take(n, f"{names[min(pi, len(names) - 1)][0]}_frame")
        return pieces

    def finish(self):
        keep = {n for n in self.bones if n not in self.mapping and n not in self.splits}
        for k, v in list(self.mapping.items()):
            if v in keep and v != k:
                i = 2
                while f"{v}_{i}" in self.used or f"{v}_{i}" in keep:
                    i += 1
                self.mapping[k] = f"{v}_{i}"
                self.used.add(self.mapping[k])
        for k, (j, p) in self.splits.items():
            for x in (j, p):
                assert x not in keep or x == k, f"split name {x} collides with a kept bone"
        self.mapping = {k: v for k, v in self.mapping.items() if k != v}
        review = [n for n in keep if self.role[n] != "placeholder"]
        return self.mapping, self.splits, review


def sfx(names, s):
    return tuple((f"{j}_{s}", f"{p}_{s}") for j, p in names)


def automap_limbed(geo, plan):
    R = Rig(geo)
    R.core()
    front_n, hind_n = LIMBED[plan]
    chains, mids = R.limb_chains()
    info = {}
    for s, chs in chains.items():
        chs = [c for c in chs]
        if len(chs) >= 2:
            tops = [R.wtop(c[0]) for c in chs]
            zs = [float(t[2]) for t in tops]
            ys = [float(t[1]) for t in tops]
            if max(ys) - min(ys) > max(zs) - min(zs):   # an upright ape: the arm is the HIGH limb
                order = sorted(range(len(chs)), key=lambda i: -ys[i])
            else:
                order = sorted(range(len(chs)), key=lambda i: zs[i])
            pick = [chs[order[0]], chs[order[-1]]]
            labels = ["front", "hind"]
        else:
            body = R.mapping_inv("body")
            bz = float(R.wpos(body)[2]) if body else 0.0
            pick = chs
            labels = ["front" if float(R.wtop(chs[0][0])[2]) < bz else "hind"]
        for ch, lab in zip(pick, labels):
            names = sfx(front_n if lab == "front" else hind_n, s)
            info[f"{lab}_{s}"] = (R.name_chain(ch, names, f"{lab}_toe_base_{s}", f"{lab}_toe_{s}"), names)
    for n in mids:
        R.take(n, "legs_frame" if not R.bones[n].get("cubes") else "legs")
    m, sp, rv = R.finish()
    return m, sp, rv, info


def automap_legs(geo, plan):
    R = Rig(geo)
    R.core()
    # insect wings: per side, front pair then hind pair
    for s in ("l", "r"):
        ws = [n for n in R.bones if R.role[n] == "wing" and R.side(n) == s and n not in R.mapping and n not in R.splits]
        cubed = sorted([n for n in ws if R.bones[n].get("cubes")], key=lambda n: float(R.wpos(n)[2]))
        for i, n in enumerate(cubed[:2]):
            j, p = (f"wing_root_{s}", f"wing_{s}") if i == 0 else (f"wing_root_hind_{s}", f"wing_hind_{s}")
            par = R.bones[n].get("parent")
            if par in ws and par not in R.mapping and len(R.kids[par]) == 1 and not R.bones[par].get("cubes"):
                R.take(par, j)
                R.take(n, p)
            else:
                R.split(n, j, p)
        for n in ws:
            R.take(n, f"wing_frame_{s}")
    chains, mids = R.limb_chains(("leg",))
    info = {}
    if any(len(v) > 5 for v in chains.values()) or (chains and len({len(v) for v in chains.values()}) > 1
                                                      and plan == "arachnid"):
        # the leg reading does not make sense (Patrix spider: 9 "legs" on one side, none on the other — its 118-bone
        # rig nests segments under side frames): legs keep their own names, the rest is standardized
        chains = {}
    for s, chs in chains.items():
        chs = sorted(chs, key=lambda c: float(R.wtop(c[0])[2]))   # front first
        for k, ch in enumerate(chs, 1):
            names = tuple((f"{j}_{k}_{s}", f"{p}_{k}_{s}") for j, p in LEG_NAMES)
            info[f"leg_{k}_{s}"] = (R.name_chain(ch, names, f"tarsus_joint_{k}_{s}", f"tarsus_{k}_{s}"), names)
    for n in mids:
        R.take(n, "legs_frame" if not R.bones[n].get("cubes") else "legs")
    m, sp, rv = R.finish()
    return m, sp, rv, info


def automap_chain(geo, plan):
    R = Rig(geo)
    R.core()
    # remaining cube segments behind the body on the midline (snake / fish bodies named b1, body3 …): body_k
    m, sp, rv = R.finish()
    return m, sp, rv, {}


def cuts(g, info, n_target):
    log = []
    names = {b["name"] for b in g["bones"]}
    for key, (pieces, tmpl) in info.items():
        have = [p for p in pieces if p in names]
        lab = "front" if key.startswith("front") else "hind"
        n_t = min(n_target, len(tmpl))
        if not have or len(have) >= n_t:
            continue
        try:
            if len(have) == 1 and have[0] == tmpl[0][1]:
                fr = CUTS[3][lab][:n_t - 1] if n_t == 3 else (0.5,)
                Q.cut_piece(g, have[0], fr, list(tmpl[1:n_t]), tmpl[0][0])
                log.append(f"{key}: 1 -> {n_t}")
            elif len(have) == 2 and n_t == 3 and have[1] == tmpl[1][1]:
                Q.cut_piece(g, have[1], (Q.CUT2[lab],), [tmpl[2]], tmpl[1][0])
                log.append(f"{key}: 2 -> 3")
        except AssertionError as e:   # (a limb whose cubes turn different ways stays one piece; the mob goes on)
            log.append(f"{key}: not cut ({e})")
    return log


def baby_map(adult_geo, adult_map, adult_splits, geo, fn, plan):
    m2, s2, _, _ = fn(geo, plan)
    shared = {b["name"] for b in adult_geo["bones"]} & {b["name"] for b in geo["bones"]}
    m2 = {k: v for k, v in m2.items() if k not in shared}
    s2 = {k: v for k, v in s2.items() if k not in shared}
    for k in shared:
        if k in adult_splits:
            s2[k] = adult_splits[k]
        elif adult_map.get(k, k) != k:
            m2[k] = adult_map[k]
    names = {b["name"] for b in geo["bones"]}
    keep = {n for n in names if n not in m2 and n not in s2}
    for k in list(m2):
        if k not in shared and (list(m2.values()).count(m2[k]) > 1 or m2[k] in keep):
            del m2[k]
    shared_names = {m2[k] for k in shared if k in m2} | {x for k in shared if k in s2 for x in s2[k]}
    for k in [k for k in s2 if k not in shared]:
        if set(s2[k]) & shared_names:
            del s2[k]
    for k in [k for k in m2 if k not in shared]:
        if m2[k] in shared_names:
            del m2[k]
    return m2, s2


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


def dedupe_bones(geo):
    """17:1x (backlog whale_wwa): an authored rig with two bones of ONE name (the WA humpback: a cubeless top `body` and a
    cubed `body` under it at the same pivot, no rotation) — the engine keys bones by name, so the rig is ambiguous and the
    converter refused it. Every later duplicate gets the next free `<name>_N`; children keep their parent name, which now
    means the FIRST bone of that name (with equal pivots and no rotation this changes no drawn pixel). Returns the renames."""
    seen, ren = set(), []
    names = {b["name"] for b in geo["bones"]}
    for b in geo["bones"]:
        n = b["name"]
        if n in seen:
            k = 2
            while f"{n}_{k}" in names:
                k += 1
            b["name"] = f"{n}_{k}"
            names.add(b["name"])
            ren.append((n, b["name"]))
        seen.add(n)
    return ren


def main(plans=None, ids=None, report=None):
    import std_birds_b as BB
    census = json.loads((ROOT / "_docs/standard/SKELETON-CENSUS.json").read_text())
    plans = plans or sorted(set(LIMBED) | set(LEGS) | CHAIN)
    todo = [c for c in census if c["body_plan"] in plans and (not ids or c["id"] in ids)]
    packs = {}
    out = Path(report) if report else ROOT / "_docs/standard/PLANS-STANDARD.md"
    lines = ["# OTHER BODY PLANS — standard names (+ limb joints where the plan has them) · Phase 2b", "",
             "| plan | mob | gate (moments / texel misses) | limbs (pieces before) | cuts | placeholders removed | kept for review |",
             "|---|---|---|---|---|---|---|"]
    for c in todo:
        plan, mob = c["body_plan"], c["id"]
        rp = c["rp"].replace("rp07-1438", "rp07-1439").replace("rp06-1424", "rp06-1425").replace("rp08-148", "rp08-149")
        if rp not in packs:
            packs[rp] = S.Pack(S.VANILLA if rp == "resource_pack" else ROOT / "_build" / rp)
        P = packs[rp]
        fn = automap_limbed if plan in LIMBED else automap_legs if plan in LEGS else automap_chain
        n_t = 3 if plan in LIMBED and plan not in ("turtle", "pinniped") else (2 if plan in ("turtle", "pinniped") else
                                                                                 LEGS.get(plan, 0))
        log, info, review, dropped = [], {}, [], 0
        try:
            ef, desc = P.entities[mob]
            Q_ensure_geos(P, desc)
            for g_ in set((desc.get("geometry") or {}).values()):
                if g_ in P.geos:
                    for a_, b_ in dedupe_bones(P.geos[g_]):
                        log.append(f"duplicate bone {a_} -> {b_}")
            gid = c["geometry"] if c["geometry"] in P.geos else (desc.get("geometry") or {}).get(
                "default", next(iter((desc.get("geometry") or {}).values())))
            geo = P.geos[gid]
            mapping, splits, review, info = fn(geo, plan)
            per_geo = {}
            dec_m, dec_s = dict(mapping), dict(splits)      # decisions so far: a bone name decided once stays decided
            decided = {b["name"] for b in geo["bones"]}     # (kept-as-is is a decision too)
            for g in sorted(set((desc.get("geometry") or {}).values()) - {gid}):
                m_, s_ = baby_map(geo, mapping, splits, P.geos[g], fn, plan)
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
            if n_t:
                for g in st.geo["minecraft:geometry"]:
                    log += cuts(g, info, n_t)
            dropped = Q.drop_placeholders(st)
            dang = Q.drop_dangling(P, mob, st, mapping, splits, per_geo)
            if dang:
                log.append(f"{dang} dangling channels dropped")
            st.save()
            n, miss, unrun = BB.gate_uv(P, mob, sinfo, (S.GROUND, S.IDLE, S.FLY), [0.0, 0.35, 0.7])
            gate_s = f"{n} / {miss}" + (f" (not run: {', '.join(unrun)[:40]})" if unrun else "")
        except Exception as e:  # noqa: BLE001
            gate_s = f"REFUSED {str(e)[:80]}"
        limbs = ", ".join(f"{k} {len(v[0])}" for k, v in sorted(info.items()))
        lines.append(f"| {plan} | {mob} | {gate_s} | {limbs} | {'; '.join(sorted(set(log)))} | {dropped} | "
                     f"{', '.join(review[:8])} |")
        print(plan, mob, gate_s, limbs, sorted(set(log)), flush=True)
    import report_merge as RM   # 10-01: partial runs merge into the standing report
    RM.write_table(out, "\n".join(lines) + "\n", partial=bool(ids) and not report)


if __name__ == "__main__":
    a = sys.argv[1:]
    plans = [x for x in a if ":" not in x] or None
    ids = [x for x in a if ":" in x] or None
    main(plans, ids)
