#!/usr/bin/env python3
"""nwr_entity_lint.py — PER-ENTITY never-written-reads (10-01, extends D-C317's pack-level molang_nwr_lint).

Bedrock variables (v.* / variable.*) belong to ONE entity. A clip copied from another creature (shared_<kind>, fam_<kind>)
may read a variable only its original creature's scripts set; on the new creature that read is unknown (the golem lesson:
an unknown read is an error that stops the statement / channel). The pack-level lint cannot see this — the variable IS
written somewhere in the pack, just not by this entity (P11: the per-entity space was unaudited).

For every client entity: WRITES = its own scripts (initialize / pre_animation / animate conditions) + the timelines and
`variables` blocks of every animation it names + on_entry / on_exit / variables of every animation controller it names.
READS = every Molang string in every animation it names (channels, anim_time_update, loop, blend_weight, timeline).
A read counts as fine if written by the entity, guarded with `??`, or engine-provided (molang_nwr_lint.ENGINE).
Usage: nwr_entity_lint.py PACK_DIR [PACK_DIR ...]   (lower packs first; later packs override same-id animations)
API: lint(packs, only=None) -> {entity id: [(animation short name, animation id, variable)]}"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML  # noqa: E402
import molang_nwr_lint as NW  # noqa: E402

WRITE, READ, GUARD = NW.WRITE, NW.READ, NW.GUARD


def strings(x):
    """every string inside a JSON value."""
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for v in x.values():
            yield from strings(v)
    elif isinstance(x, list):
        for v in x:
            yield from strings(v)


def load(packs):
    anims, ctrls, ents = {}, {}, {}
    for p in packs:
        p = Path(p)
        for sub, store, key in (("animations", anims, "animations"), ("animation_controllers", ctrls, "animation_controllers")):
            for f in (p / sub).rglob("*.json") if (p / sub).exists() else []:
                try:
                    d = ML._parse_json(f.read_text(encoding="utf-8-sig"))
                except Exception:  # noqa: BLE001
                    continue
                if isinstance(d, dict) and isinstance(d.get(key), dict):
                    store.update(d[key])
        for f in (p / "entity").rglob("*.json") if (p / "entity").exists() else []:
            try:
                d = ML._parse_json(f.read_text(encoding="utf-8-sig"))
            except Exception:  # noqa: BLE001
                continue
            if isinstance(d, dict) and "minecraft:client_entity" in d:
                desc = d["minecraft:client_entity"].get("description") or {}
                if desc.get("identifier"):
                    ents[desc["identifier"]] = (str(f), desc)
    return anims, ctrls, ents


def writes_of(desc, anims, ctrls):
    w = set()
    sc = desc.get("scripts") or {}
    for s in strings(sc):
        w |= {m.lower() for m in WRITE.findall(s)}
    for short, aid in (desc.get("animations") or {}).items():
        src = ctrls.get(aid) if aid.startswith("controller.") else anims.get(aid)
        if src is None:
            continue
        if aid.startswith("controller."):
            for s in strings(src):
                w |= {m.lower() for m in WRITE.findall(s)}
        else:
            for k in ("timeline", "variables"):
                for s in strings(src.get(k) or {}):
                    w |= {m.lower() for m in WRITE.findall(s)}
    return w


def lint(packs, only=None):
    anims, ctrls, ents = load(packs)
    out = {}
    for ident, (f, desc) in ents.items():
        if only and ident not in only:
            continue
        w = writes_of(desc, anims, ctrls)
        bad = []
        for short, aid in (desc.get("animations") or {}).items():
            if aid.startswith("controller.") or aid not in anims:
                continue
            seen = set()
            for s in strings({k: v for k, v in anims[aid].items() if k != "timeline"}):
                guarded = {g.lower() for g in GUARD.findall(s)}
                # 16:5x 10-01: `( v.freq = 2.66; … v.freq … )` — a variable assigned INSIDE the same expression is written
                # before it is read (the SF baby clips do this); not an unknown read (the first lint pass flagged 18 of these)
                guarded |= {w.lower() for w in WRITE.findall(s)}
                for r in READ.findall(s):
                    r = r.lower()
                    if r in w or r in guarded or r in NW.ENGINE or r in seen:
                        continue
                    seen.add(r)
                    bad.append((short, aid, r))
        if bad:
            out[ident] = bad
    return out


if __name__ == "__main__":
    res = lint(sys.argv[1:])
    n_sh = sum(1 for v in res.values() for s, _, _ in v if s.startswith(("shared_", "fam_")))
    n_own = sum(1 for v in res.values() for s, _, _ in v if not s.startswith(("shared_", "fam_")))
    print(f"entities with unknown reads: {len(res)} · reads in shared/fam clips: {n_sh} · in own clips: {n_own}")
    for ident, v in sorted(res.items())[:40]:
        print(" ", ident, v[:4])
