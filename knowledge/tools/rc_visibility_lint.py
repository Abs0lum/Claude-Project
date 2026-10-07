#!/usr/bin/env python3
"""rc_visibility_lint.py — RCV standing gate (D-C285): does every client entity's render controller leave its model VISIBLE?

Why (his R8 p4 a17 / p5 b04 "invisible, but I can see his shadow"): RP-06 1.4.15 gave the silverfish the Patrix model but kept
the vanilla render controller `controller.render.silverfish`, whose part_visibility is
    [{"*": "0"}, {"bodypart_0": "1"} ... {"bodypart_6": "1"}, {"bodylayer_0": "1"} ... {"bodylayer_2": "1"}]
— a DEFAULT HIDE with an allow-list of the vanilla bone names. pw_silverfish has 34 bones and none of those names, so every cube
was hidden and only the shadow drew. No gate looked at part_visibility against the geometry the entity actually binds.

Rules (Bedrock): part_visibility entries apply in order, later entries override earlier; keys are bone names or globs with `*`
(case-insensitive, like bone names everywhere); a value is a constant (0 / 1 / true / false / "0" / "1") or a Molang expression
(treated as MAYBE visible). An entry affects that bone's OWN cubes only (L-PARTVIS-OWN), not its children.
Render controllers resolve pack > stack (in order) > vanilla (Mojang bedrock-samples, cached in _ref/bs_sparse).

API:  lint_pack(pack, stack=()) -> (n_entities, findings)   finding = (entity file, geometry id, rc id, n_cube_bones, n_visible, hidden_sample)
      a FINDING = a geometry with cubes of which NO cube-bearing bone can be visible (the silverfish case).
CLI:  rc_visibility_lint.py PACK [STACK ...]"""
import fnmatch, re, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML

VANILLA_RC = Path("/home/claude/_ref/bs_sparse/resource_pack/render_controllers")


def _jl(p):
    try: return ML._parse_json(Path(p).read_text(encoding="utf-8-sig"))
    except Exception: return None


def _files(pack, sub):
    return sorted((Path(pack) / sub).rglob("*.json")) if (Path(pack) / sub).exists() else []


def rc_table(packs):
    """{rc id: definition} — first pack wins (pack order = precedence: the pack itself, then the stack, then vanilla)."""
    out = {}
    for pk in list(packs) + [VANILLA_RC.parent.parent]:
        folder = VANILLA_RC if pk == VANILLA_RC.parent.parent else Path(pk) / "render_controllers"
        for p in (sorted(folder.rglob("*.json")) if folder.exists() else []):
            d = _jl(p)
            if not isinstance(d, dict): continue
            for k, v in (d.get("render_controllers") or {}).items():
                out.setdefault(k, v)
    return out


def geo_table(packs):
    out = {}
    for pk in packs:
        for p in _files(pk, "models"):
            d = _jl(p)
            if not isinstance(d, dict): continue
            for g in d.get("minecraft:geometry", []) or []:
                gid = (g.get("description") or {}).get("identifier")
                if gid: out.setdefault(gid, g.get("bones") or [])
            for k, v in d.items():                                      # legacy 1.8.0 files: "geometry.x": {...}
                if k.startswith("geometry.") and isinstance(v, dict):
                    out.setdefault(k.split(":")[0], v.get("bones") or [])
    return out


def _const(v):
    if isinstance(v, bool): return 1 if v else 0
    if isinstance(v, (int, float)): return 1 if v else 0
    s = str(v).strip().lower()
    if s in ("0", "0.0", "false"): return 0
    if s in ("1", "1.0", "true"): return 1
    return None                                                         # an expression: maybe


def visible_state(pv, bone):
    """final state of `bone` under part_visibility list pv: 1 visible, 0 hidden, None maybe (expression)."""
    state = 1
    b = bone.lower()
    for entry in pv or []:
        if not isinstance(entry, dict): continue
        for key, val in entry.items():
            if fnmatch.fnmatchcase(b, key.lower()):
                state = _const(val)
    return state


def rc_geometry_keys(rc):
    """the entity geometry slots (lower-case keys) a render controller can draw: every `Geometry.<key>` in its geometry
    expression and in its geometry arrays."""
    txt = str(rc.get("geometry", "")) + " " + str((rc.get("arrays") or {}).get("geometries", ""))
    return {m.lower() for m in re.findall(r"geometry\.([A-Za-z_0-9]+)", txt, flags=re.I)}


def lint_pack(pack, stack=()):
    packs = [Path(pack)] + [Path(s) for s in stack]
    rcs = rc_table(packs); geos = geo_table(packs)
    findings = []; n = 0
    for p in _files(pack, "entity"):
        d = _jl(p)
        if not isinstance(d, dict) or "minecraft:client_entity" not in d: continue
        desc = d["minecraft:client_entity"].get("description") or {}
        n += 1
        rc_ids = [r if isinstance(r, str) else next(iter(r)) for r in desc.get("render_controllers") or []]
        for gkey, gid in (desc.get("geometry") or {}).items():
            bones = geos.get(gid)
            if not bones: continue
            cube_bones = [b["name"] for b in bones if b.get("cubes")]
            if not cube_bones: continue
            for rid in rc_ids:
                rc = rcs.get(rid)
                if not isinstance(rc, dict) or not rc.get("part_visibility"): continue
                if gkey.lower() not in rc_geometry_keys(rc): continue          # this RC never draws that geometry slot
                vis = [b for b in cube_bones if visible_state(rc["part_visibility"], b) != 0]
                if not vis:
                    findings.append((p.relative_to(pack).as_posix(), gid, rid, len(cube_bones), 0, cube_bones[:4]))
    return n, findings


def _selftest():
    pv = [{"*": "0"}, {"bodypart_0": "1"}, {"bodyLayer_*": "query.x"}]
    assert visible_state(pv, "head") == 0 and visible_state(pv, "BodyPart_0") == 1 and visible_state(pv, "bodylayer_2") is None
    assert visible_state([{"leftArm": False}], "leftarm") == 0 and visible_state([], "x") == 1
    assert rc_geometry_keys({"geometry": "Array.geos[q.variant]", "arrays": {"geometries": {"Array.geos": ["Geometry.default", "Geometry.baby"]}}}) == {"default", "baby"}
    print("rc_visibility_lint self-test OK")


if __name__ == "__main__":
    _selftest()
    a = sys.argv[1:]
    if a:
        n, f = lint_pack(a[0], a[1:])
        print(f"{Path(a[0]).name}: {n} client entities; {len(f)} with every cube hidden by a render controller")
        for x in f: print("  ", x)
        sys.exit(1 if f else 0)
