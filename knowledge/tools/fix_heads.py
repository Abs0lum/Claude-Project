#!/usr/bin/env python3
"""fix_heads.py — his content log 2 (15:42 CT 10-01): `armor_offset.default_neck` clashes.

Evidence: the engine generates that locator per MODEL (42 / 43 "existing" values in log 2 were MY explicit locators, the
other value differed per model) -> explicit locators only add clashes. The clash appears only where the std naming gave
2+ models of ONE entity a bone named `head` at different places (the SF originals had none).
Fix (hypothesis, his next log decides):
  1. every explicit armor_offset.default_neck I added is removed;
  2. in each entity's NON-default models, the std `head` bone gets back its ORIGINAL name (found in the source model by the
     same pivot + the same cubes; if the original name was `head` too, or none matches: head_<slot>);
  3. every animation channel / part_visibility key for `head` of that entity is DUPLICATED under the restored name, so the
     extra models move exactly as before (a channel naming a bone a model lacks is ignored by the game).
Runs on the BASE (_staging/std). Report: _docs/standard/FIX-HEADS.json."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import std_convert as S  # noqa: E402

LOC = "armor_offset.default_neck"
SRC = {"rp07-1439": "rp07-1439", "rp06-1425": "rp06-1425", "rp08-149": "rp08-149"}


def strip_locators(G):
    n = 0
    for g in G["minecraft:geometry"]:
        for b in g["bones"]:
            if LOC in (b.get("locators") or {}):
                del b["locators"][LOC]
                n += 1
                if not b["locators"]:
                    del b["locators"]
    return n


def same_cubes(a, b):
    ca = sorted((tuple(c.get("origin", [])), tuple(c.get("size", []))) for c in a.get("cubes") or [])
    cb = sorted((tuple(c.get("origin", [])), tuple(c.get("size", []))) for c in b.get("cubes") or [])
    return ca == cb


def original_name(src_geo, std_head):
    piv = np.array(std_head.get("pivot", [0, 0, 0]), float)
    for b in src_geo["bones"]:
        if np.allclose(np.array(b.get("pivot", [0, 0, 0]), float), piv, atol=1e-4) and same_cubes(b, std_head):
            return b["name"]
    return None


def run(stage=S.STAGE):
    rep = {"locators_removed": 0, "entities": []}
    packs = {k: S.Pack(ROOT / "_build" / v) for k, v in SRC.items()}
    for ef in sorted(stage.glob("*/entity/std/*.entity.json")):
        pk = ef.parent.parent.parent.name
        slug = ef.name.split(".entity.json")[0]
        gf = ef.parent.parent.parent / "models/entity/std" / f"{slug}.geo.json"
        if not gf.exists():
            continue
        G = S.jload(gf)
        removed = strip_locators(G)
        rep["locators_removed"] += removed
        ent = S.jload(ef)
        desc = ent["minecraft:client_entity"]["description"]
        geos = desc.get("geometry") or {}
        by_id = {g["description"]["identifier"]: g for g in G["minecraft:geometry"]}
        models = [(slot, by_id[g]) for slot, g in geos.items() if g in by_id]
        heads = [(slot, m, next((b for b in m["bones"] if b["name"] == "head"), None)) for slot, m in models]
        heads = [h for h in heads if h[2]]
        pivots = {json.dumps(h[2].get("pivot", [0, 0, 0])) for h in heads}
        changed_geo = removed > 0
        if len(heads) >= 2 and len(pivots) >= 2:
            default_slot = "default" if "default" in geos else models[0][0]
            ident = desc["identifier"]
            P = packs.get(pk)
            orig_desc = P.entities.get(ident, (None, {}))[1] if P else {}
            renames = {}
            for slot, m, hb in heads:
                if slot == default_slot:
                    continue
                src_gid = (orig_desc.get("geometry") or {}).get(slot)
                src_geo = P.geos.get(src_gid) if (P and src_gid) else None
                name = original_name(src_geo, hb) if src_geo else None
                if not name or name.lower() == "head" or name in {b["name"] for b in m["bones"]}:
                    name = f"head_{slot}"
                for b in m["bones"]:
                    if b.get("parent") == "head":
                        b["parent"] = name
                hb["name"] = name
                renames[slot] = name
                changed_geo = True
            new_names = sorted(set(renames.values()))
            # duplicate every `head` channel of the entity's animations under the restored names
            af = ef.parent.parent.parent / "animations/std" / f"{slug}.animation.json"
            n_dup = 0
            if af.exists():
                A = S.jload(af)
                for aid, a in A["animations"].items():
                    bones = a.get("bones") or {}
                    if "head" in bones:
                        for nn in new_names:
                            if nn not in bones:
                                bones[nn] = json.loads(json.dumps(bones["head"]))
                                n_dup += 1
                af.write_text(json.dumps(A, indent=1))
            # render controllers' part_visibility under the std folder
            rc_dup = 0
            for rf in (ef.parent.parent.parent / "render_controllers/std").glob(f"{slug}*.json"):
                R = S.jload(rf)
                for rc in (R.get("render_controllers") or {}).values():
                    for pv in rc.get("part_visibility") or []:
                        if "head" in pv:
                            for nn in new_names:
                                pv.setdefault(nn, pv["head"])
                                rc_dup += 1
                rf.write_text(json.dumps(R, indent=1))
            rep["entities"].append({"entity": ident, "renamed": renames, "channels_duplicated": n_dup, "visibility_duplicated": rc_dup})
        if changed_geo:
            gf.write_text(json.dumps(G, indent=1))
    (ROOT / "_docs/standard/FIX-HEADS.json").write_text(json.dumps(rep, indent=1))
    return rep


if __name__ == "__main__":
    r = run()
    print("explicit locators removed:", r["locators_removed"], "· entities with restored head names:", len(r["entities"]))
    for e in r["entities"][:60]:
        print("  ", e["entity"], e["renamed"], "channels dup", e["channels_duplicated"])
