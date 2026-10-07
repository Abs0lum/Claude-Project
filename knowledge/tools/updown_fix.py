#!/usr/bin/env python3
"""updown_fix.py — D-C278: turn the JEM-literal up/down faces of SHIPPED geometries into the Bedrock form (the fix
jem_convert.bedrock_uv now applies to every new build).

Each geometry is matched ONLY against its OWN source JEM (SOURCE below — the review of the first version found 48 rects that
are literal for one JEM and Bedrock-form for another: matching against every JEM turned 24 faces of the April humanoids
pw_zombie / pw_drowned whose UVs come from no JEM at all). A face is turned when its exact rect equals that JEM's
uvUp/uvDown copied literally (uv [u1,v1] size [u2-u1, v2-v1] -> uv [u2,v2] size [u1-u2, v1-v2]); a geometry is touched only
when at least half of its up/down faces are such literal copies (i.e. our converter wrote it from that JEM).
API: flip_pack(dst, skip, used_only) -> {identifier: (faces turned, file)}  ·  literal_left(doc_geometry, ident) -> count"""
import json, re, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
from updown_census import lj, CEM

# geometry identifier -> the Patrix JEM it was converted from (only converter-written geometries; vanilla / April hand-made /
# third-party ones are absent on purpose: creeper.v1.8, parrot, pw_zombie, pw_drowned, zombie.v1.8, sf_nba.*)
SOURCE = {
    "geometry.axolotl.patrix": "axolotl", "geometry.bee": "bee", "geometry.cod.patrix": "cod", "geometry.dolphin.patrix": "dolphin",
    "geometry.frog.patrix": "frog", "geometry.glow_squid.patrix": "glow_squid", "geometry.horse.patrix": "horse", "geometry.llama.patrix": "llama",
    "geometry.pig.patrix": "pig", "geometry.pufferfish_large.patrix": "puffer_fish_big", "geometry.pufferfish_medium.patrix": "puffer_fish_medium",
    "geometry.pufferfish_small.patrix": "puffer_fish_small", "geometry.pw_camel": "camel", "geometry.pw_cat": "cat", "geometry.pw_chicken": "chicken",
    "geometry.pw_chicken_cold": "cold_chicken", "geometry.pw_chicken_warm": "warm_chicken", "geometry.pw_cow": "cow", "geometry.pw_donkey": "donkey",
    "geometry.pw_fox": "fox", "geometry.pw_goat": "goat", "geometry.pw_mooshroom": "mooshroom", "geometry.pw_mule": "mule", "geometry.pw_panda": "panda",
    "geometry.pw_polar_bear": "polar_bear", "geometry.pw_tropicalfish_a": "tropical_fish_a", "geometry.pw_tropicalfish_b": "tropical_fish_b",
    "geometry.pw_wolf": "wolf", "geometry.pw_zombie_pigman": "zombified_piglin", "geometry.rabbit.patrix": "rabbit", "geometry.ravager": "ravager",
    "geometry.salmon.patrix": "salmon", "geometry.sheep.patrix": "sheep", "geometry.sheep_wool.patrix": "sheep_wool", "geometry.squid.patrix": "squid",
    "geometry.tadpole.patrix": "tadpole", "geometry.trader_llama.patrix": "trader_llama", "geometry.trader_llama_decor.patrix": "trader_llama_decor",
    "geometry.turtle.patrix": "turtle",
    "geometry.elder_guardian.patrix": "elder_guardian", "geometry.guardian.patrix": "guardian", "geometry.evoker.patrix": "evoker",
    "geometry.hoglin.patrix": "hoglin", "geometry.illusioner.patrix": "illusioner", "geometry.piglin.patrix": "piglin",
    "geometry.piglin_brute.patrix": "piglin_brute", "geometry.pw_husk": "husk", "geometry.pw_pillager": "pillager", "geometry.pw_vindicator": "vindicator",
    "geometry.pw_witch": "witch", "geometry.skeleton_horse.patrix": "skeleton_horse", "geometry.zoglin.patrix": "zoglin",
    "geometry.zombie_horse.patrix": "zombie_horse",
    "geometry.giant.patrix": "zombie",     # the giant was converted from the Patrix zombie (4/4 up/down faces are zombie.jem literals)
}
_SETS = {}


def jem_sets(stem):
    """(literal rects, Bedrock-form rects) of one JEM's uvUp/uvDown."""
    if stem not in _SETS:
        lit, bed = set(), set()
        j = lj(CEM / f"{stem}.jem")
        def walk(m):
            for b in m.get("boxes", []) or []:
                for k in ("uvUp", "uvDown"):
                    v = b.get(k)
                    if v:
                        u1, v1, u2, v2 = [float(x) for x in v]
                        lit.add((round(u1, 3), round(v1, 3), round(u2 - u1, 3), round(v2 - v1, 3)))
                        bed.add((round(u2, 3), round(v2, 3), round(u1 - u2, 3), round(v1 - v2, 3)))
            for s in m.get("submodels", []) or []: walk(s)
        for m in j.get("models", []): walk(m)
        _SETS[stem] = (lit, bed)
    return _SETS[stem]


def _key(f):
    return (round(float(f["uv"][0]), 3), round(float(f["uv"][1]), 3), round(float(f["uv_size"][0]), 3), round(float(f["uv_size"][1]), 3))


def _faces(g):
    for b in g.get("bones", []):
        for c in b.get("cubes", []):
            uv = c.get("uv")
            if not isinstance(uv, dict): continue
            for k in ("up", "down"):
                f = uv.get(k)
                if f and "uv_size" in f: yield f


def literal_left(g, ident):
    stem = SOURCE.get(ident)
    if not stem: return 0
    lit, _ = jem_sets(stem)
    return sum(1 for f in _faces(g) if _key(f) in lit)


def flip_geometry(g, ident):
    stem = SOURCE.get(ident)
    if not stem: return 0, "no source JEM"
    lit, _ = jem_sets(stem)
    faces = list(_faces(g)); hits = [f for f in faces if _key(f) in lit]
    if not faces or len(hits) * 2 < len(faces): return 0, f"only {len(hits)}/{len(faces)} faces are literal copies of {stem}.jem"
    for f in hits:
        (a, b), (w, h) = f["uv"], f["uv_size"]; f["uv"] = [a + w, b + h]; f["uv_size"] = [-w, -h]
    return len(hits), f"{len(hits)}/{len(faces)} from {stem}.jem"


def flip_pack(dst, skip=(), used_only=None):
    total, notes = {}, {}
    for p in sorted((Path(dst) / "models").rglob("*.json")):
        try: d = lj(p)
        except Exception: continue
        geos = d.get("minecraft:geometry") or []
        changed = False
        for g in geos:
            ident = g["description"]["identifier"]
            if ident in skip or ident not in SOURCE: continue
            if used_only is not None and ident not in used_only: continue
            n, why = flip_geometry(g, ident); notes[ident] = why
            if n: total[ident] = (n, str(p.relative_to(dst))); changed = True
        if changed: p.write_text(json.dumps(d, indent=1), encoding="utf-8")
    return total, notes


def check_turned(old_root, new_root, used, skip=(), renames=None):
    """Gate: for every used converter-written geometry (SOURCE, not skipped): each up/down face that was a literal copy of its
    own JEM in OLD is turned exactly in NEW, every other face and key is unchanged. Rebuilt ones (skip): every up/down face is
    in its own JEM's Bedrock form. Returns (ok, message, per-ident counts)."""
    import convb_round as R
    ok, msgs, counts = True, [], {}
    for ident, stem in SOURCE.items():
        if used is not None and ident not in used: continue
        try: _, gn = R.geo_file(Path(new_root), ident)
        except Exception: continue
        lit, bed = jem_sets(stem)
        if ident in skip:
            fs = list(_faces(gn)); good = all(_key(f) in bed for f in fs)
            ok &= good; counts[ident] = f"rebuilt: {sum(1 for f in fs if _key(f) in bed)}/{len(fs)} Bedrock form"
            if not good: msgs.append(f"{ident} rebuilt faces not all Bedrock form")
            continue
        _, go = R.geo_file(Path(old_root), ident)
        gn = json.loads(json.dumps(gn))
        for b in gn["bones"]:
            if renames and ident in renames:
                b["name"] = renames[ident].get(b["name"], b["name"])
                if b.get("parent") in renames[ident]: b["parent"] = renames[ident][b["parent"]]
        extra = [b for b in gn["bones"] if b["name"] not in {x["name"] for x in go["bones"]}]
        gn["bones"] = [b for b in gn["bones"] if b not in extra]
        fo = list(_faces(go)); lit_old = [f for f in fo if _key(f) in lit]
        expect_turn = len(lit_old) * 2 >= len(fo) and len(fo) > 0
        turned = 0; bad = 0
        for bn, bo in zip(gn["bones"], go["bones"]):
            if bn.get("name") != bo.get("name"): bad += 1; continue
            for cn, co in zip(bn.get("cubes", []), bo.get("cubes", [])):
                un, uo = cn.get("uv"), co.get("uv")
                if not isinstance(uo, dict):
                    bad += un != uo; continue
                for k in set(un) | set(uo):
                    fn, fo_ = un.get(k), uo.get(k)
                    if k in ("up", "down") and fo_ and "uv_size" in fo_ and _key(fo_) in lit and expect_turn:
                        want = {**fo_, "uv": [fo_["uv"][0] + fo_["uv_size"][0], fo_["uv"][1] + fo_["uv_size"][1]], "uv_size": [-fo_["uv_size"][0], -fo_["uv_size"][1]]}
                        if fn == want: turned += 1
                        else: bad += 1
                    elif fn != fo_: bad += 1
                strip = lambda c: {x: y for x, y in c.items() if x != "uv"}
                bad += strip(cn) != strip(co)
            bad += {x: y for x, y in bn.items() if x != "cubes"} != {x: y for x, y in bo.items() if x != "cubes"}
        good = bad == 0 and (turned == len(lit_old) if expect_turn else turned == 0)
        ok &= good; counts[ident] = f"{turned}/{len(fo)} turned" + ("" if expect_turn else " (not converter-written: left alone)")
        if not good: msgs.append(f"{ident}: turned {turned} of {len(lit_old)} literal, {bad} other differences")
    return ok, msgs, counts
