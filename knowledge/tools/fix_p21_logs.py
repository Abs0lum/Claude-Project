#!/usr/bin/env python3
"""fix_p21_logs.py — the three error classes of his content log 1 (15:04 CT 10-01), fixed in the STAGED base for ALL mobs
(his 15:06: "check for these same errors across all other mobs as well").

A  EMPTY `bones {}` clips (48; the game: "bones | Required child … not found"). The std conversion dropped channels whose bone
   is absent from the model (dead in the original too) or that flight / flutter took over, and left the block empty. Mojang's
   bone-less animations always carry other content, so an empty clip is not proven valid -> one ZERO rotation on a real bone
   (rotations add: + 0 changes nothing; none of the 48 carries override_previous_animation — checked).
B  format 1.8.0 entities with scripts.animate / scripts.initialize (8; the game: "child 'animate' / 'initialize' not valid
   here" = L-FMT-SCRIPTS). The enderman precedent (D-C285, witnessed): an ANIMATION CONTROLLER plays the clips; the initialize
   values move to the front of pre_animation as `v.x = v.x ?? (value);` (set once, then kept; direct variable left of ??).
C  `armor_offset.default_neck` locator mismatch between the models of one entity (engine-generated; 43 entities whose adult +
   baby models both got a bone named `head` from the std naming). Probable fix (his next log confirms): the locator defined
   EXPLICITLY and IDENTICALLY (same bone name, same offset = the default model's head pivot) in every model of the entity.
Report: _docs/standard/FIX-P21-LOGS.json. Prints a summary."""
import copy
import json
import sys
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import std_convert as S  # noqa: E402

LOC = "armor_offset.default_neck"


def jl(p):
    return S.jload(p)


def wj(p, d):
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text(json.dumps(d, indent=1))


def first_bone(geo_file):
    g = jl(geo_file)["minecraft:geometry"][0]
    tops = [b["name"] for b in g["bones"] if not b.get("parent")]
    return tops[0] if tops else g["bones"][0]["name"]


def fix_a(stage):
    n = []
    for af in sorted(stage.glob("*/animations/std/*.animation.json")):
        d = jl(af)
        slug = af.name.split(".animation.json")[0]
        changed = False
        for aid, a in d["animations"].items():
            if isinstance(a, dict) and "bones" in a and not a["bones"]:
                gf = af.parent.parent.parent / "models/entity/std" / f"{slug}.geo.json"
                bone = first_bone(gf)
                a["bones"] = {bone: {"rotation": [0, 0, 0]}}
                changed = True
                n.append({"clip": aid, "bone": bone})
        if changed:
            wj(af, d)
    return n


def _ver(s):
    try:
        return tuple(int(x) for x in str(s).split("."))
    except ValueError:
        return (0,)


def fix_b(stage):
    out = []
    for ef in sorted(stage.glob("*/entity/std/*.entity.json")):
        d = jl(ef)
        if _ver(d.get("format_version")) >= (1, 10, 0):
            continue
        desc = d["minecraft:client_entity"]["description"]
        sc = desc.get("scripts") or {}
        if not (sc.get("animate") or sc.get("initialize")):
            continue
        slug = ef.name.split(".entity.json")[0]
        init = [s for s in (sc.pop("initialize", None) or []) if isinstance(s, str)]
        anim = sc.pop("animate", None) or []
        pre_init = []
        for s in init:
            for st in [x.strip() for x in s.split(";") if x.strip()]:
                lhs, rhs = st.split("=", 1)
                v = lhs.strip()
                pre_init.append(f"{v} = {v} ?? ({rhs.strip()});")
        if pre_init:
            sc["pre_animation"] = [" ".join(pre_init)] + list(sc.get("pre_animation") or [])
        shorts = [a if isinstance(a, str) else list(a)[0] for a in anim]
        conds = [a for a in anim if not isinstance(a, str)]
        assert not conds, f"{slug}: conditional animate entries need a state per condition"
        cid = f"controller.animation.std.{slug}.play"
        cf = ef.parent.parent.parent / "animation_controllers/std" / f"{slug}.animation_controllers.json"
        wj(cf, {"format_version": "1.10.0", "animation_controllers": {cid: {"initial_state": "default", "states": {
            "default": {"animations": shorts}}}}})
        ctrls = desc.setdefault("animation_controllers", [])
        if not any(cid in c.values() for c in ctrls if isinstance(c, dict)):
            ctrls.append({"std_play": cid})
        desc["scripts"] = sc
        wj(ef, d)
        out.append({"entity": desc["identifier"], "format": d.get("format_version"), "plays": shorts, "init_moved": pre_init,
                    "controller": cid})
    return out


def fix_c(stage):
    out = []
    for ef in sorted(stage.glob("*/entity/std/*.entity.json")):
        d = jl(ef)
        desc = d["minecraft:client_entity"]["description"]
        geos = desc.get("geometry") or {}
        if len(set(geos.values())) < 2:
            continue
        slug = ef.name.split(".entity.json")[0]
        gf = ef.parent.parent.parent / "models/entity/std" / f"{slug}.geo.json"
        if not gf.exists():
            continue
        G = jl(gf)
        by_id = {g["description"]["identifier"]: g for g in G["minecraft:geometry"]}
        models = [by_id[g] for g in dict.fromkeys(geos.values()) if g in by_id]
        with_head = [m for m in models if any(b["name"].lower() == "head" for b in m["bones"])]
        if len(with_head) < 2:
            continue
        default = by_id.get(geos.get("default")) or models[0]
        head = next((b for b in default["bones"] if b["name"].lower() == "head"), None) or \
            next(b for b in with_head[0]["bones"] if b["name"].lower() == "head")
        off = [round(float(x), 4) for x in head.get("pivot", [0, 0, 0])]
        names = [set(b["name"] for b in m["bones"]) for m in models]
        common = set.intersection(*names)
        bone = "body" if "body" in common else ("root" if "root" in common else ("head" if "head" in common else None))
        if bone is None:
            out.append({"entity": desc["identifier"], "skipped": "no bone common to all its models"})
            continue
        for m in models:
            b = next(x for x in m["bones"] if x["name"] == bone)
            b.setdefault("locators", {})[LOC] = list(off)
        wj(gf, G)
        out.append({"entity": desc["identifier"], "models": [m["description"]["identifier"] for m in models], "bone": bone,
                    "offset": off})
    return out


def lint_c(geos_of_entity):
    """standing gate: an entity whose models (2+) carry a `head` bone must carry LOC identically in all of them."""
    with_head = [m for m in geos_of_entity if any(b["name"].lower() == "head" for b in m["bones"])]
    if len(with_head) < 2:
        return None
    vals = set()
    for m in geos_of_entity:
        v = [(b["name"], json.dumps((b.get("locators") or {}).get(LOC))) for b in m["bones"] if LOC in (b.get("locators") or {})]
        vals.add(json.dumps(v))
    return None if len(vals) == 1 and json.loads(next(iter(vals))) else "armor_offset.default_neck missing or different"


if __name__ == "__main__":
    stage = S.STAGE
    rep = {"A_empty_bones": fix_a(stage), "B_fmt_1_8_0": fix_b(stage), "C_locator": fix_c(stage)}
    (ROOT / "_docs/standard/FIX-P21-LOGS.json").write_text(json.dumps(rep, indent=1))
    print(f"A {len(rep['A_empty_bones'])} clips · B {len(rep['B_fmt_1_8_0'])} entities · C {len(rep['C_locator'])} entities "
          f"({sum(1 for x in rep['C_locator'] if 'skipped' in x)} skipped)")
    for x in rep["B_fmt_1_8_0"]:
        print("  B", x["entity"], x["plays"], x["init_moved"])
    for x in rep["C_locator"]:
        if "skipped" in x:
            print("  C SKIPPED", x)
