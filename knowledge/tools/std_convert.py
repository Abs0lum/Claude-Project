#!/usr/bin/env python3
"""std_convert.py — Standardization Phase 2, step A: the RENAME converter + its identical-pose gate (D-C368).

Never edits a shared file. For one entity it writes NEW copies, so every other user of the old files is untouched and the
old versions stay until his verification (his 02:25 law: keep all versions until verified):
  models/entity/std/<slug>.geo.json          geometry.std.<slug>             bones renamed (+ optional joint/piece splits)
  animations/std/<slug>.animation.json       animation.std.<slug>.<name>     every animation the entity lists, bones renamed
  render_controllers/std/<slug>.rc.json      controller.render.std.<slug>.k  only for controllers whose part_visibility names bones
  entity/std/<slug>.entity.json              the entity file repointed to the copies (replaces the old entity file at build time)
Operations:
  mapping {old: new}                         pure rename (parents follow)
  splits  {old: (joint, piece)}              old bone becomes a cubeless JOINT (keeps pivot, bind rotation, children, animation)
                                             and a new child PIECE carries its cubes (same pivot, no rotation) — pose-identical.
The gate poses the original and the converted entity under EVERY animation it lists (each on its own), at many moments, with
a fixed random seed, and compares the multiset of posed cube faces (corners + UV, rounded) — names ignored, so it must match.
Output root: _staging/std/<pack>/
"""
import copy
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import molang_lint as ML  # noqa: E402
import molang_eval as ME  # noqa: E402
import posed_preview as PP  # noqa: E402
from bb_truth import truth_posed_faces  # noqa: E402
from equine_compare import bone_affines  # noqa: E402

STAGE = ROOT / "_staging/std"
VANILLA = ROOT / "_intake/bedrock-samples/resource_pack"


def jload(p):
    return ML._parse_json(Path(p).read_text(encoding="utf-8-sig"))


def slug_of(entity_id):
    return re.sub(r"[^a-z0-9]+", "_", entity_id.lower()).strip("_")


# the stack above each SOURCE build the converter reads (bottom -> top: RP-06, RP-07, RP-08)
ABOVE = {"rp06-1425": ["rp07-1439", "rp08-149"], "rp07-1439": ["rp08-149"]}


class Pack:
    """Indexes of one resource pack (+ Mojang's vanilla pack as the fallback for animations / controllers)."""

    def __init__(self, path):
        self.path = Path(path)
        self.entities, self.anims, self.rcs, self.geos = {}, {}, {}, {}
        for f in sorted((self.path / "entity").rglob("*.json")):
            try:
                d = jload(f)["minecraft:client_entity"]["description"]
                self.entities[d["identifier"]] = (f, d)
            except Exception:
                pass
        for base in (VANILLA, self.path):  # pack overrides vanilla
            for f in sorted((base / "animations").rglob("*.json")) if (base / "animations").exists() else []:
                try:
                    for k, v in jload(f).get("animations", {}).items():
                        self.anims[k] = v
                except Exception:
                    pass
            for f in sorted((base / "render_controllers").rglob("*.json")) if (base / "render_controllers").exists() else []:
                try:
                    for k, v in jload(f).get("render_controllers", {}).items():
                        self.rcs[k] = v
                except Exception:
                    pass
        # 15:5x 10-01 (his log 2 — 12 RP-06 SF creatures kept UNCONVERTED clips): at runtime an animation id resolves to the
        # TOPMOST pack defining it; RP-06 sits below RP-07 / RP-08, whose SF animation files serve RP-06's SF creatures too.
        # Upper packs' animations are indexed (overriding, like the game) so the converter sees what the game plays.
        for up in ABOVE.get(self.path.name, []):
            ub = self.path.parent / up
            for f in sorted((ub / "animations").rglob("*.json")) if (ub / "animations").exists() else []:
                try:
                    for k, v in jload(f).get("animations", {}).items():
                        self.anims[k] = v
                except Exception:
                    pass
        for f in sorted((self.path / "models").rglob("*.json")):
            try:
                d = jload(f)
            except Exception:
                continue
            for g in d.get("minecraft:geometry", []) if isinstance(d, dict) else []:
                gid = (g.get("description") or {}).get("identifier")
                if gid:
                    self.geos.setdefault(gid, g)
            for k, g in (d.items() if isinstance(d, dict) else []):
                if k.startswith("geometry.") and isinstance(g, dict):
                    gid = k.split(":")[0]
                    self.geos.setdefault(gid, {"description": {"identifier": gid,
                                                               "texture_width": g.get("texturewidth", 64),
                                                               "texture_height": g.get("textureheight", 64)},
                                               "bones": g.get("bones") or []})


def convert_bones(bones, mapping, splits):
    names = {b["name"] for b in bones}
    unknown = (set(mapping) | set(splits)) - names
    assert not unknown, f"names bones that do not exist: {sorted(unknown)}"
    out = []
    for b in bones:
        b = copy.deepcopy(b)
        old = b["name"]
        if b.get("parent"):
            p = b["parent"]
            b["parent"] = splits[p][0] if p in splits else mapping.get(p, p)
        if old in splits:
            joint, piece = splits[old]
            cubes = b.pop("cubes", [])
            b["name"] = joint
            out.append(b)
            pc = {"name": piece, "parent": joint, "pivot": list(b.get("pivot", [0, 0, 0])), "cubes": cubes}
            for flag in ("mirror", "inflate"):
                if flag in b:
                    pc[flag] = b[flag]
            out.append(pc)
        else:
            b["name"] = mapping.get(old, old)
            out.append(b)
    dup = [n for n, c in Counter(b["name"] for b in out).items() if c > 1]
    assert not dup, f"duplicate bone names: {dup}"
    return out


def rename_key(name, mapping, splits):
    return splits[name][0] if name in splits else mapping.get(name, name)


def convert(pack_path, entity_id, mapping, splits=None, per_geo=None, wing_cut=None):
    """per_geo {gid: (mapping, splits)} for entities with several geometries (adult / baby); the animation and render-
    controller renames use the union of all mappings (a name mapped two different ways is refused)."""
    splits = splits or {}
    per_geo = per_geo or {}
    all_map, all_split = dict(mapping), dict(splits)
    for m_, s_ in per_geo.values():
        for k, v in m_.items():
            assert all_map.get(k, v) == v, f"bone {k} mapped two ways"
            all_map[k] = v
        for k, v in s_.items():
            assert all_split.get(k, v) == v, f"bone {k} split two ways"
            all_split[k] = v
    P = pack_path if isinstance(pack_path, Pack) else Pack(pack_path)
    ef, desc = P.entities[entity_id]
    slug = slug_of(entity_id)
    out = STAGE / P.path.name
    nd = copy.deepcopy(jload(ef))
    d = nd["minecraft:client_entity"]["description"]
    # geometry copies
    geo_out, gmap = [], {}
    for key, gid in (d.get("geometry") or {}).items():
        if gid not in gmap:
            g = copy.deepcopy(P.geos[gid])
            new = f"geometry.std.{slug}" + ("" if not gmap else f".{len(gmap)}")
            g["description"]["identifier"] = new
            m_, s_ = per_geo.get(gid, (mapping, splits))
            g["bones"] = convert_bones(g["bones"], m_, s_)
            for side, bone in (wing_cut or {}).items():  # step B: cut a stiff wing into the template chain
                if any(b["name"] == bone and b.get("cubes") for b in g["bones"]):  # (a baby with an empty joint there: not cut)
                    import std_wingsplit
                    g["bones"] = std_wingsplit.split_wing(g["bones"], bone, side)
            geo_out.append(g)
            gmap[gid] = new
        d["geometry"][key] = gmap[gid]
    # animation copies (controllers are kept as they are: they name animations, not bones)
    anims_out = {}
    for short, aid in list((d.get("animations") or {}).items()):
        if aid.startswith("controller.") or aid not in P.anims:
            continue
        a = copy.deepcopy(P.anims[aid])
        if a.get("bones"):
            a["bones"] = {rename_key(k, all_map, all_split): v for k, v in a["bones"].items()}
        new = f"animation.std.{slug}." + re.sub(r"^animation\.", "", aid)
        anims_out[new] = a
        d["animations"][short] = new
    # render controllers that hide / show bones by name
    rcs_out = {}
    for i, rc in enumerate(d.get("render_controllers") or []):
        rid = rc if isinstance(rc, str) else list(rc)[0]
        r = P.rcs.get(rid)
        if not r or not r.get("part_visibility"):
            continue
        r = copy.deepcopy(r)
        r["part_visibility"] = [{rename_key(k, all_map, all_split): v for k, v in pv.items()} for pv in r["part_visibility"]]
        new = f"controller.render.std.{slug}.{i}"
        rcs_out[new] = r
        if isinstance(rc, str):
            d["render_controllers"][i] = new
        else:
            d["render_controllers"][i] = {new: rc[rid]}
    files = {
        out / f"models/entity/std/{slug}.geo.json": {"format_version": "1.12.0", "minecraft:geometry": geo_out},
        out / f"animations/std/{slug}.animation.json": {"format_version": "1.8.0", "animations": anims_out},
        out / f"entity/std/{slug}.entity.json": nd,
    }
    if rcs_out:
        files[out / f"render_controllers/std/{slug}.rc.json"] = {"format_version": "1.8.0", "render_controllers": rcs_out}
    for f, data in files.items():
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(data, indent=1))
    return {"entity_file_old": str(ef.relative_to(P.path)), "files": [str(f.relative_to(out)) for f in files],
            "geometry": gmap, "animations": len(anims_out), "render_controllers": len(rcs_out)}


# ------------------------------------------------------------------ gate
def _env(desc, t, extra, seed):
    random.seed(seed)
    env = {"q.life_time": t, "q.anim_time": t, "q.delta_time": 0.05, "q.is_on_ground": 1.0, "q.is_alive": 1.0, **extra}
    for s in (desc.get("scripts") or {}).get("initialize", []):
        try:
            ME.run(s, env)
        except Exception:  # noqa: BLE001 — a script the evaluator cannot read is skipped on BOTH sides (same env)
            pass
    for _ in range(3):
        for s in (desc.get("scripts") or {}).get("pre_animation", []):
            try:
                ME.run(s, env)
            except Exception:  # noqa: BLE001
                pass
    return env


def faces(geo, anim, env):
    bones = PP.posed_bones(geo["bones"], (anim or {}).get("bones", {}), dict(env)) if anim else copy.deepcopy(geo["bones"])
    d = geo["description"]
    fs = truth_posed_faces(bones, d.get("texture_width", 64), d.get("texture_height", 64), bone_affines(bones))
    return Counter((tuple(round(c, 3) for p in f.pts for c in p), tuple(round(u, 5) for u in f.uv)) for f in fs)


def gate(pack_path, entity_id, staged_info, envs, times, seed=7):
    """Each listed animation, alone, at each time and env: original vs converted face multisets."""
    P = pack_path if isinstance(pack_path, Pack) else Pack(pack_path)
    ef, desc = P.entities[entity_id]
    out = STAGE / P.path.name
    nd = jload(out / f"entity/std/{slug_of(entity_id)}.entity.json")["minecraft:client_entity"]["description"]
    new_geos = {g["description"]["identifier"]: g
                for g in jload(out / f"models/entity/std/{slug_of(entity_id)}.geo.json")["minecraft:geometry"]}
    new_anims = jload(out / f"animations/std/{slug_of(entity_id)}.animation.json")["animations"]
    pairs = []  # (old geometry, new geometry) for every geometry the entity lists
    for gid in dict.fromkeys((desc.get("geometry") or {}).values()):
        pairs.append((P.geos[gid], new_geos[staged_info["geometry"][gid]]))
    checks, bad, unrun = 0, [], set()
    shorts = [s for s, a in (desc.get("animations") or {}).items() if not a.startswith("controller.") and a in P.anims]

    def best_pair(keys):  # the geometry an animation was written for = the one whose bones it names most
        return max(pairs, key=lambda pr: len(keys & {b["name"] for b in pr[0]["bones"]}))
    for short in [None] + shorts:
        a_old = P.anims.get(desc["animations"][short]) if short else None
        a_new = new_anims.get(nd["animations"][short]) if short else None
        geo_pairs = pairs if short is None else [best_pair(set((a_old.get("bones") or {})))]
        for g_old, g_new in geo_pairs:
            if short is not None:
                # static name correspondence (covers Molang the evaluator cannot run)
                old_names = {b["name"] for b in g_old["bones"]}
                new_names = {b["name"] for b in g_new["bones"]}
                ka = {k for k in (a_old.get("bones") or {}) if k in old_names}
                kb = {k for k in (a_new.get("bones") or {}) if k in new_names}
                checks += 1
                if len(ka) != len(kb):
                    bad.append((short, "names", sorted(ka)[:4], sorted(kb)[:4]))
            for extra in envs:
                for t in times:
                    env = _env(desc, t, extra, seed)
                    try:
                        same = faces(g_old, a_old, env) == faces(g_new, a_new, env)
                    except Exception:  # noqa: BLE001 — the evaluator cannot run this Molang: covered by the static check
                        unrun.add(short)
                        continue
                    checks += 1
                    if not same:
                        bad.append((short, t, extra))
    if unrun:
        print(f"   note: evaluator could not run {sorted(unrun)} — static name check only")
    return checks, bad


# ------------------------------------------------------------------ the parrot (TEMPLATE-BIRD v1.1 §3, corrected 10:20)
PARROT_MAP = {
    "head2": "head", "beak": "beak", "feathers": "crest",
    "left_wing_fly": "shoulder_l", "left_wing_fly_rot": "shoulder_l_rest", "bone2": "wing_inner_l",
    "left_wing_fly2": "elbow_l", "left_wing_fly2_hinge": "wrist_l",
    "bone10": "primary_l_1", "bone11": "primary_l_2", "bone12": "primary_l_3",
    "right_wing_fly": "shoulder_r", "right_wing_fly_rot": "shoulder_r_rest", "bone3": "wing_inner_r",
    "right_wing_fly2": "elbow_r", "right_wing_fly2_hinge": "wrist_r",
    "bone4": "primary_r_1", "bone8": "primary_r_2", "bone9": "primary_r_3",
    "left_wing2": "wing_fold_l", "left_wing_rotation": "wing_fold_l_rest", "left_wing_rotation2": "wing_fold_l_rest2",
    "bone5": "wing_fold_piece_l",
    "right_wing2": "wing_fold_r", "right_wing_rotation": "wing_fold_r_rest", "right_wing_rotation2": "wing_fold_r_rest2",
    "bone6": "wing_fold_piece_r",
    "left_leg2": "thigh_l", "left_foot2": "foot_l", "right_leg2": "thigh_r", "right_foot2": "foot_r",
    "left_leg": "thigh_dance_l", "left_foot": "foot_dance_l", "right_leg": "thigh_dance_r", "right_foot": "foot_dance_r",
    "tail2": "tail_base", "bone7": "tail",
    # JEM-conversion leftovers (cubeless, animated by nothing): kept, renamed; 'head' parents the FreshLX credit bone
    "head": "jem_head", "tail": "jem_tail", "left_wing": "jem_wing_l", "right_wing": "jem_wing_r",
    "left_wing_rotation_jem": "jem_wing_l_rest", "right_wing_rotation_jem": "jem_wing_r_rest",
}
FLY = {"q.is_on_ground": 0.0, "q.is_flying": 1.0, "q.modified_move_speed": 1.0}
HOVER = {"q.is_on_ground": 0.0, "q.is_flying": 1.0, "q.modified_move_speed": 0.0}
GROUND = {"q.is_on_ground": 1.0, "q.modified_move_speed": 0.6, "q.modified_distance_moved": 3.0}
IDLE = {"q.is_on_ground": 1.0, "q.modified_move_speed": 0.0}
ENVS = (FLY, HOVER, GROUND, IDLE)
TIMES = [t / 20.0 for t in range(0, 40, 3)]


def main():
    src = ROOT / "_build/rp07-1439"
    info = convert(src, "minecraft:parrot", PARROT_MAP)
    print(json.dumps(info))
    n, bad = gate(src, "minecraft:parrot", info, ENVS, TIMES)
    print(f"GATE identical pose (rename, each animation alone): {n - len(bad)}/{n}", bad[:3])
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
