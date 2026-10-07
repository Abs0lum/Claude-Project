#!/usr/bin/env python3
"""entity_schema_lint.py — FMT standing gate (D-C285): client-entity sections the entity's own format_version does not allow.

Why (his R8 first-load log): RP-07 1.4.21/1.4.22 added `scripts.animate` and `scripts.initialize` to the April enderman entity,
whose file is format_version 1.8.0 — the game said
    entity/enderman.entity.json | ... | scripts | animate | child 'animate' not valid here.
    entity/enderman.entity.json | ... | scripts | initialize | child 'initialize' not valid here.
and ignored both, so the ported Patrix jaw never ran. A 1.8.0 client entity plays animations through its `animation_controllers`
list; `scripts.animate` / `scripts.initialize` exist from format 1.10.0.

Rule set (only what the game has told us, extended when a log says more):
  format < 1.10.0  ->  description.scripts.animate / description.scripts.initialize are ERRORS.
Reported as information (no game evidence yet): format >= 1.10.0 with an `animation_controllers` list.

API: lint_pack(pack) -> (n_entities, errors, infos)   error/info = (entity file, message)
CLI: entity_schema_lint.py PACK [PACK ...]"""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML

NOT_BEFORE_1_10 = ("animate", "initialize")


def _ver(s):
    try: return tuple(int(x) for x in str(s).split("."))
    except Exception: return (0,)


def check_entity(d):
    errs, infos = [], []
    fv = _ver(d.get("format_version", "0"))
    desc = (d.get("minecraft:client_entity") or {}).get("description") or {}
    sc = desc.get("scripts") or {}
    if fv < (1, 10, 0):
        for k in NOT_BEFORE_1_10:
            if k in sc: errs.append(f"format {d.get('format_version')}: scripts.{k} is not valid before 1.10.0 (game: \"child '{k}' not valid here\")")
    elif desc.get("animation_controllers"):
        infos.append(f"format {d.get('format_version')}: animation_controllers list (1.8.0 style) in a >= 1.10.0 file")
    return errs, infos


def lint_pack(pack):
    n = 0; errs = []; infos = []
    root = Path(pack) / "entity"
    for p in sorted(root.rglob("*.json")) if root.exists() else []:
        try: d = ML._parse_json(p.read_text(encoding="utf-8-sig"))
        except Exception: continue
        if not isinstance(d, dict) or "minecraft:client_entity" not in d: continue
        n += 1
        e, i = check_entity(d)
        errs += [(p.relative_to(pack).as_posix(), x) for x in e]; infos += [(p.relative_to(pack).as_posix(), x) for x in i]
    return n, errs, infos


def _selftest():
    bad = {"format_version": "1.8.0", "minecraft:client_entity": {"description": {"scripts": {"animate": ["a"], "initialize": ["v.a = 1;"], "pre_animation": []}}}}
    ok = {"format_version": "1.10.0", "minecraft:client_entity": {"description": {"scripts": {"animate": ["a"], "initialize": ["v.a = 1;"]}}}}
    assert len(check_entity(bad)[0]) == 2 and check_entity(ok) == ([], [])
    assert check_entity({"format_version": "1.8.0", "minecraft:client_entity": {"description": {"scripts": {"pre_animation": ["v.x = 1;"]}}}}) == ([], [])
    print("entity_schema_lint self-test OK")


if __name__ == "__main__":
    _selftest()
    bad = 0
    for a in sys.argv[1:]:
        n, e, i = lint_pack(a)
        print(f"{Path(a).name}: {n} client entities; {len(e)} errors; {len(i)} infos")
        for x in e: print("  ERROR", x)
        for x in i[:10]: print("  info ", x)
        bad += len(e)
    sys.exit(1 if bad else 0)
