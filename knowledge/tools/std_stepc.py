#!/usr/bin/env python3
"""std_stepc.py — Phase 2 step C (his P2 GO, 10:58): complete the TEMPLATE-BIRD v1.1 wing chain on the 38 jointed-wing
birds staged by step A, and split the YSav black eagle's shared leg bones into left / right (his P3).
Every change is an IDENTITY insertion, a rename, or a cube cut with UV kept — the gate (UV-sample correspondence under every
animation, old original vs new staged) must show 0 misses.
  rename   primary_base_<k>_<s> -> primary_base_<s>_<k>                     (template spelling)
  elbow    elbow_<s> inserted directly above wrist_<s> (wrist pivot)        (T5 b: the elbow moves)
  chain    primary_base_<s>_1 below the wrist holding every wrist child; then primary_base_<s>_k (pivot = piece k) each
           under the previous base, holding pieces k..n                       (T5 b: chained primaries)
  cut      fewer than 3 primaries: the LAST primary piece is cut along its span into the missing count (T3 b)
  legs     (YSav black eagle) every leg bone duplicated per side, cubes by x sign, animation channels copied to both
"""
import copy
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import std_convert as S  # noqa: E402
import std_wingsplit as W  # noqa: E402
import std_birds_b as BB  # noqa: E402


class Staged:
    """One staged entity's geometry list + animations + render controllers, edited together."""

    def __init__(self, pack, mob):
        self.dir = S.STAGE / pack
        self.slug = S.slug_of(mob)
        self.gp = self.dir / f"models/entity/std/{self.slug}.geo.json"
        self.ap = self.dir / f"animations/std/{self.slug}.animation.json"
        self.rp = self.dir / f"render_controllers/std/{self.slug}.rc.json"
        self.geo = S.jload(self.gp)
        self.anim = S.jload(self.ap)
        self.rc = S.jload(self.rp) if self.rp.exists() else None

    def save(self):
        self.gp.write_text(json.dumps(self.geo, indent=1))
        self.ap.write_text(json.dumps(self.anim, indent=1))
        if self.rc:
            self.rp.write_text(json.dumps(self.rc, indent=1))

    def rename(self, old, new):
        for g in self.geo["minecraft:geometry"]:
            for b in g["bones"]:
                if b["name"] == old:
                    b["name"] = new
                if b.get("parent") == old:
                    b["parent"] = new
        for a in self.anim["animations"].values():
            if a.get("bones") and old in a["bones"]:
                a["bones"][new] = a["bones"].pop(old)
        if self.rc:
            for r in self.rc["render_controllers"].values():
                r["part_visibility"] = [{(new if k == old else k): v for k, v in pv.items()} for pv in r.get("part_visibility", [])]


def bones_of(g):
    return {b["name"]: b for b in g["bones"]}


def insert_above(g, bone, name):
    by = bones_of(g)
    b = by[bone]
    nb = {"name": name, "pivot": list(b.get("pivot", [0, 0, 0]))}
    if b.get("parent"):
        nb["parent"] = b["parent"]
    b["parent"] = name
    g["bones"].insert(g["bones"].index(b), nb)


def insert_below(g, bone, name, pivot, children):
    nb = {"name": name, "parent": bone, "pivot": list(pivot)}
    g["bones"].insert(g["bones"].index(bones_of(g)[bone]) + 1, nb)
    for b in g["bones"]:
        if b["name"] in children:
            b["parent"] = name


def cut_last(g, s, n_have):
    """cut primary_<s>_<n_have> into (4 - n_have) slabs from its base outward; new bases chained."""
    by = bones_of(g)
    last = by[f"primary_{s}_{n_have}"]
    base = by[last["parent"]]
    cubes = last.pop("cubes", [])
    k_new = 4 - n_have
    piv = np.array(base.get("pivot", [0, 0, 0]), float)
    axis = W.span_axis(cubes, piv)
    lo = min(min(c["origin"][axis], c["origin"][axis] + c["size"][axis]) for c in cubes)
    hi = max(max(c["origin"][axis], c["origin"][axis] + c["size"][axis]) for c in cubes)
    near_lo = abs(piv[axis] - lo) <= abs(piv[axis] - hi)
    fr = [i / k_new for i in range(1, k_new)]
    cuts = [lo + f * (hi - lo) if near_lo else hi - f * (hi - lo) for f in fr]
    edges = sorted([lo, hi] + cuts)
    slabs = [[] for _ in range(k_new)]
    for c in cubes:
        cs = copy.deepcopy(c)
        cs.setdefault("mirror", bool(last.get("mirror", False)))  # a bone-level mirror applies to cubes without their own
        for a, b, nc in W.cut_cube(cs, axis, sorted(cuts)):
            mid = (a + b) / 2
            idx = sum(1 for e in edges[1:-1] if mid > e) if near_lo else sum(1 for e in edges[1:-1] if mid < e)
            slabs[idx].append(nc)
    last["cubes"] = slabs[0]
    others = [k for k in range(3) if k != axis]
    centre = {k: (min(c["origin"][k] for c in cubes) + max(c["origin"][k] + c["size"][k] for c in cubes)) / 2 for k in others}
    prev_base = base["name"]
    at = g["bones"].index(last) + 1
    for j in range(1, k_new):
        p = [0.0, 0.0, 0.0]
        p[axis] = cuts[j - 1]
        for k in others:
            p[k] = centre[k]
        bn, pn = f"primary_base_{s}_{n_have + j}", f"primary_{s}_{n_have + j}"
        g["bones"][at:at] = [{"name": bn, "parent": prev_base, "pivot": p},
                             {"name": pn, "parent": bn, "pivot": list(p), "cubes": slabs[j]}]
        at += 2
        prev_base = bn


def complete_wing(st, g, s):
    log = []
    by = bones_of(g)
    if f"wrist_{s}" not in by:
        return [f"{s}: no wrist"]
    for k in range(2, 9):
        old = f"primary_base_{k}_{s}"
        if old in by:
            st.rename(old, f"primary_base_{s}_{k}")
            log.append(f"rename {old}")
    by = bones_of(g)
    if f"elbow_{s}" not in by:
        insert_above(g, f"wrist_{s}", f"elbow_{s}")
        log.append("elbow")
    by = bones_of(g)
    pieces = sorted([n for n in by if n.startswith(f"primary_{s}_") and n[len(f'primary_{s}_'):].isdigit()],
                    key=lambda n: int(n.rsplit("_", 1)[1]))
    if f"primary_base_{s}_1" not in by:
        kids = [b["name"] for b in g["bones"] if b.get("parent") == f"wrist_{s}"]
        p1 = by.get(f"primary_{s}_1", by[f"wrist_{s}"]).get("pivot", by[f"wrist_{s}"].get("pivot", [0, 0, 0]))
        insert_below(g, f"wrist_{s}", f"primary_base_{s}_1", p1, set(kids))
        log.append("base_1")
    # chain: pieces k..n under base_k
    for k in range(2, len(pieces) + 1):
        by = bones_of(g)
        base_k = f"primary_base_{s}_{k}"
        piece_k = f"primary_{s}_{k}"
        if base_k in by:
            continue
        prev = f"primary_base_{s}_{k - 1}"
        movers = {f"primary_{s}_{j}" for j in range(k, len(pieces) + 1)} | {f"primary_base_{s}_{j}" for j in range(k + 1, 9)}
        movers = {m for m in movers if m in by and by[m].get("parent") == prev}
        insert_below(g, prev, base_k, by[piece_k].get("pivot", [0, 0, 0]), movers)
        log.append(f"base_{k}")
    if 0 < len(pieces) < 3:
        cut_last(g, s, len(pieces))
        log.append(f"cut primary_{len(pieces)} into {4 - len(pieces)}")
    return log


YSAV_BILATERAL = {"pw:african_black_eagle_ysav", "pw:fisher_eagle_ysav"}


def split_bilateral_legs(st, g):
    """YSav black eagle: duplicate the leg subtree (from legs_frame) per side, cubes by x sign; copy animation channels."""
    by = bones_of(g)
    top = "legs_frame"
    sub, stack = [], [top]
    while stack:
        n = stack.pop()
        sub.append(n)
        stack += [b["name"] for b in g["bones"] if b.get("parent") == n]
    rename_side = {"thighs": "thigh", "shins": "shin", "feet": "foot", "toes": "toe", "thighs_joint": "hip",
                   "shins_joint": "knee", "feet_joint": "ankle", "toes_joint": "toe_base"}
    new = []
    for s, keep in (("l", lambda x: x > 0), ("r", lambda x: x <= 0)):
        for n in sub:
            b = copy.deepcopy(by[n])
            base = rename_side.get(n, n)
            b["name"] = f"{base}_{s}"
            if b.get("parent") and b["parent"] in sub:
                b["parent"] = f"{rename_side.get(b['parent'], b['parent'])}_{s}"
            if b.get("cubes"):
                b["cubes"] = [c for c in b["cubes"]
                              if keep(c["origin"][0] + abs(c["size"][0]) / 2)]
            new.append(b)
    g["bones"] = [b for b in g["bones"] if b["name"] not in sub] + new
    for a in st.anim["animations"].values():
        bs = a.get("bones") or {}
        for n in sub:
            if n in bs:
                ch = bs.pop(n)
                for s in ("l", "r"):
                    bs[f"{rename_side.get(n, n)}_{s}"] = copy.deepcopy(ch)
    return [f"legs split per side ({len(sub)} bones x 2)"]


def main(ids=None):
    rows = json.loads((ROOT / "_docs/standard/BIRD-RIG-MAP.json").read_text())
    census = {c["id"]: c for c in json.loads((ROOT / "_docs/standard/SKELETON-CENSUS.json").read_text())}
    todo = [r["id"] for r in rows if r["class"] == "TEMPLATE-READY"]
    if ids:
        todo = [i for i in todo if i in ids]
    packs = {}
    lines = ["# STEP C — wing chain completed on the jointed-wing birds (+ YSav eagle legs)", "",
             "| mob | changes | gate (moments / texel misses) |", "|---|---|---|"]
    for mob in todo:
        rp = census[mob]["rp"].replace("rp07-1438", "rp07-1439").replace("rp06-1424", "rp06-1425")
        P = packs.setdefault(rp, S.Pack(ROOT / "_build" / rp))
        st = Staged(rp, mob)
        log = []
        for g in st.geo["minecraft:geometry"]:
            for s in ("l", "r"):
                log += complete_wing(st, g, s)
            # 10-01: every creature on the YSav eagle model (black eagle + fish eagle share it) gets the per-side legs
            if mob in YSAV_BILATERAL and any(b["name"] == "legs_frame" for b in g["bones"]):
                log += split_bilateral_legs(st, g)
        st.save()
        ef, desc = P.entities[mob]
        info = {"geometry": {gid: g["description"]["identifier"] for gid, g in
                             zip(dict.fromkeys((desc.get("geometry") or {}).values()), st.geo["minecraft:geometry"])}}
        n, miss, unrun = BB.gate_uv(P, mob, info, (S.FLY, S.GROUND), [0.0, 0.35, 0.7])
        lines.append(f"| {mob} | {'; '.join(sorted(set(log)))} | {n} / {miss} |")
        print(mob, n, miss, sorted(set(log)), flush=True)
    import report_merge as RM   # 10-01: partial runs merge
    RM.write_table(ROOT / "_docs/standard/STEPC-BIRDS.md", "\n".join(lines) + "\n", partial=bool(ids))


if __name__ == "__main__":
    main(sys.argv[1:] or None)
