#!/usr/bin/env python3
"""std_birds_b.py — Phase 2 step B batch: the SPLIT-NEEDED birds.
FLIGHT birds: standard names (std_automap) + each side's one-piece wing renamed `shoulder_<s>` and cut (std_wingsplit).
FLUTTER / NO-FLIGHT / non-flying babies: standard names only (his C1 + F2: no flier rework).
Gate: every listed animation alone + bind pose, at a few moments, UV-sample correspondence old <-> new (0 misses required).
Writes _docs/standard/WINGSPLIT-BIRDS.md."""
import json
import sys
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import std_automap as A  # noqa: E402
import std_convert as S  # noqa: E402
import std_wingsplit as W  # noqa: E402
import standard_bird_map as B  # noqa: E402
import posed_preview as PP  # noqa: E402
from bb_truth import truth_posed_faces  # noqa: E402
from equine_compare import bone_affines  # noqa: E402

FLUTTER = {"minecraft:chicken", "sf_nba:turkey", "sf_nba:peafowl", "sf_nba:kakapo",
           "pw:turkey_wa", "pw:kakapo_wwa"}   # his F2 classes cover every pack's turkey + kakapo (12:20 fix)
NO_FLIGHT = {"pw:ostrich_anf", "pw:ostrich_wa", "pw:ostrich_ysav", "pw:ostrich_ws", "sf_nba:ostrich", "pw:emu_ytri", "pw:cassowary_ytri",
             "sf_nba:kiwi", "sf_nba:emperor_penguin"}


def flight_class(mob_id):
    if mob_id in FLUTTER:
        return "FLUTTER"
    if mob_id in NO_FLIGHT:
        return "NO-FLIGHT"
    if "baby" in mob_id:
        return "BABY"
    return "FLIGHT"


def posed_faces(geo, anim, env):
    bones = PP.posed_bones(geo["bones"], (anim or {}).get("bones", {}), dict(env)) if anim else geo["bones"]
    d = geo["description"]
    return truth_posed_faces(bones, d.get("texture_width", 64), d.get("texture_height", 64), bone_affines(bones))


def gate_uv(P, mob_id, info, envs, times):
    ef, desc = P.entities[mob_id]
    slug = S.slug_of(mob_id)
    out = S.STAGE / P.path.name
    nd = S.jload(out / f"entity/std/{slug}.entity.json")["minecraft:client_entity"]["description"]
    new_geos = {g["description"]["identifier"]: g for g in S.jload(out / f"models/entity/std/{slug}.geo.json")["minecraft:geometry"]}
    new_anims = S.jload(out / f"animations/std/{slug}.animation.json")["animations"]
    pairs = [(P.geos[g], new_geos[info["geometry"][g]]) for g in dict.fromkeys((desc.get("geometry") or {}).values())]
    shorts = [s for s, a in (desc.get("animations") or {}).items() if not a.startswith("controller.") and a in P.anims]
    checks, misses, unrun = 0, 0, set()
    for short in [None] + shorts:
        a_old = P.anims.get(desc["animations"][short]) if short else None
        a_new = new_anims.get(nd["animations"][short]) if short else None
        gp = pairs if short is None else [max(pairs, key=lambda pr: len(set((a_old.get("bones") or {})) & {b["name"] for b in pr[0]["bones"]}))]
        for g_old, g_new in gp:
            for extra in envs:
                for t in times:
                    env = S._env(desc, t, extra, 7)
                    try:
                        fo, fn = posed_faces(g_old, a_old, env), posed_faces(g_new, a_new, env)
                    except Exception:  # noqa: BLE001
                        unrun.add(short)
                        continue
                    so, sn = W._samples(fo, 3), W._samples(fn, 3)
                    misses += W._covered(so, fn) + W._covered(sn, fo)
                    checks += 1
    return checks, misses, sorted(x for x in unrun if x)


def main(ids=None):
    rows = json.loads((ROOT / "_docs/standard/BIRD-RIG-MAP.json").read_text())
    census = {c["id"]: c for c in json.loads((ROOT / "_docs/standard/SKELETON-CENSUS.json").read_text())}
    todo = [r for r in rows if r["class"] in ("SPLIT-NEEDED", "NO-WINGS-FOUND")]
    if ids:
        todo = [r for r in todo if r["id"] in ids]
    packs = {}
    lines = ["# WINGSPLIT — Phase 2 step B (stiff-wing + wingless birds)", "",
             "| mob | class | wing cut | gate (moments / texel misses) | not run by the evaluator | kept for review |",
             "|---|---|---|---|---|---|"]
    for r in todo:
        rp = census[r["id"]]["rp"].replace("rp07-1438", "rp07-1439").replace("rp06-1424", "rp06-1425")
        P = packs.setdefault(rp, S.Pack(ROOT / "_build" / rp))
        geo = P.geos[r["geometry"]]
        mapping, splits, review = A.automap(geo)
        cls = flight_class(r["id"])
        cut = {}
        if cls == "FLIGHT" and r["class"] == "SPLIT-NEEDED":
            bones = {b["name"]: b for b in geo["bones"]}
            for s in ("l", "r"):
                # the one cube-carrying wing bone of this side: undo its joint/piece split, rename it to the shoulder
                cand = [k for k, (j, pc) in splits.items() if j == f"shoulder_{s}"] + \
                       [k for k, v in mapping.items() if v == f"wing_inner_{s}" and bones[k].get("cubes")]
                if len(cand) == 1:
                    k = cand[0]
                    splits.pop(k, None)
                    parent = bones[k].get("parent")
                    if parent and mapping.get(parent) == f"shoulder_{s}":
                        # the plate hangs under an empty shoulder joint: the plate itself is cut, under that shoulder
                        mapping[k] = f"wing_root_{s}"
                        cut[s] = f"wing_root_{s}"
                    else:
                        mapping[k] = f"shoulder_{s}"
                        cut[s] = f"shoulder_{s}"
        ef, desc = P.entities[r["id"]]
        per_geo = {g: A.baby_map(geo, mapping, splits, P.geos[g])
                   for g in set((desc.get("geometry") or {}).values()) - {r["geometry"]}}
        try:
            info = S.convert(P, r["id"], mapping, splits, per_geo, wing_cut=cut)
            n, miss, unrun = gate_uv(P, r["id"], info, (S.FLY, S.GROUND), [0.0, 0.35, 0.7])
            gate_s = f"{n} / {miss}"
        except AssertionError as e:
            gate_s, unrun = f"REFUSED {e}"[:70], []
        lines.append(f"| {r['id']} | {cls} | {'yes' if cut else 'no'} | {gate_s} | {', '.join(unrun)} | {', '.join(review[:6])} |")
        print(r["id"], cls, "cut" if cut else "-", gate_s, unrun, flush=True)
    import report_merge as RM   # 10-01: partial runs merge
    RM.write_table(ROOT / "_docs/standard/WINGSPLIT-BIRDS.md", "\n".join(lines) + "\n", partial=bool(ids))


if __name__ == "__main__":
    main(sys.argv[1:] or None)
