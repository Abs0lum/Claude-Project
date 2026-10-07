#!/usr/bin/env python3
"""build_rp06_149.py — RP-06 Hostile Mobs RP v1.4.9: the four wiring faults the 09-28 round-2 witness read found (D-C266/D-C267).

  CREEPER  (h09 "weirdly transparent"): the entity listed controller.render.creeper_armor UNGATED, so every creeper wore the
           charged-creeper shell (inflated geometry, lightning texture 87 % alpha-0, ignore_lighting). Vanilla gates it on
           query.is_powered -> the same gate here.
  HUSK     (h04 "missing pieces of his arms"): the 8 limb cubes of geometry.pw_husk had NO uv at all, so they sampled the empty
           top-left of the 64x64 layout and alpha-test dropped them. The Patrix husk.jem carries per-face UVs for each 12-tall
           limb; each is split into the upper (v +0..6) and lower (v +6..12) halves the articulated template uses.
  PILLAGER (h05) + VINDICATOR (h07 "clipping on chest and back"): the pw_ templates had no rightItem/leftItem bones, so the held
           crossbow / axe drew at a default point (the axe handle through the chest). Added under the forearms at the vanilla
           pivots. VINDICATOR also: its three crossed-arm cubes sat in `body` (the conversion dropped the JEM's arms_rotation), so
           the animation set could never hide them when the arms go up. They move to a new `arms` bone (pivot = the JEM's
           arms_rotation point), UNROTATED — the RP-07 animation set this entity uses poses `arms` itself (calm: -60 deg X, the
           crossed pose; attack: scale 0) and hides rightArm/leftArm/rightItem while calm (scale 0).
  WITCH    (h08 "no arms?"): the JEM `arms` part (3 boxes under arms2: translate [0, 23.2233, 0.85129], rotate 43) was dropped
           by the conversion. Added by CONV-1 (tools/jem_convert.py): bone `arms` (pivot [0, 23, 1]) + child `arms2` (rest
           rotation -43 deg X) — the witch's c_* animations add small `arms` motions on top of the rest pose.
Not touched: drowned / stray (their cause is in RP-07: two vanilla .tga files above RP-06's .png skins -> RP-07 1.4.14).
Everything else byte-identical to v1.4.8 (verify_rp06_149.py asserts the diff)."""
import copy, json, re, shutil, sys, time
from pathlib import Path

ROOT = Path("/home/claude")
SRC, DST, VER, DATE = ROOT / "_build/rp06-148", ROOT / "_build/rp06-149", "1.4.9", "2026-09-28"
CEM = ROOT / "_intake/patrix-mobs/assets/minecraft/optifine/cem"
sys.path.insert(0, str(ROOT / "tools"))
from jem_convert import load_json as jem_load, jem_tree, to_bedrock  # noqa: E402

FACES = ("north", "east", "south", "west", "up", "down")


def jl(p):
    return json.loads(re.sub(r"^\s*//.*$", "", Path(p).read_text(encoding="utf-8-sig"), flags=re.M))


def jw(p, obj):
    Path(p).write_text(json.dumps(obj, indent=1), encoding="utf-8")


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f:
        f.write(f"[{time.strftime('%H:%M')} CT 09-28] BUILD {m}\n")


def geo(path):
    doc = jl(path)
    return doc, doc["minecraft:geometry"][0]


def bone(g, name):
    return next(b for b in g["bones"] if b["name"] == name)


# ---------------------------------------------------------------------------------------------------------------------------------
def fix_creeper(report):
    p = DST / "entity/creeper.entity.json"; e = jl(p); d = e["minecraft:client_entity"]["description"]
    before = copy.deepcopy(d["render_controllers"])
    d["render_controllers"] = ["controller.render.creeper", {"controller.render.creeper_armor": "query.is_powered"}]
    jw(p, e)
    report["creeper"] = {"before": before, "after": d["render_controllers"]}


def split_face_uv(face_uv, half):
    """A 12-tall limb's per-face uv -> the upper (half=0) or lower (half=1) 6-tall cube. Side faces take their v range's
    top or bottom half (v grows downward on the model); up/down stay whole (the joint faces are hidden)."""
    out = {}
    for f, r in face_uv.items():
        (u, v), (us, vs) = r["uv"], r["uv_size"]
        if f in ("up", "down"):
            out[f] = {"uv": [u, v], "uv_size": [us, vs]}
        else:
            step = vs / 2.0
            out[f] = {"uv": [u, v + step * half], "uv_size": [us, step]}
    return out


def fix_husk(report):
    jem = jem_load(CEM / "husk.jem")
    limbs = {}
    for b in to_bedrock(jem_tree(jem)):
        for c in b["cubes"]:
            if c["size"] == [4, 12, 4] and isinstance(c.get("uv"), dict):
                # which template limb: by the Bedrock origin (x, y)
                x, y = c["origin"][0], c["origin"][1]
                key = {(-8, 12): "rightArm", (4, 12): "leftArm", (-4, 0): "rightLeg", (0, 0): "leftLeg"}.get((round(x), round(y)))
                if key: limbs[key] = c["uv"]
    assert set(limbs) == {"rightArm", "leftArm", "rightLeg", "leftLeg"}, f"husk.jem limbs found: {sorted(limbs)}"
    p = DST / "models/entity/pw_husk.geo.json"; doc, g = geo(p)
    pairs = {"rightArm": ("rightArm", "rightForearm"), "leftArm": ("leftArm", "leftForearm"),
             "rightLeg": ("rightLeg", "rightShin"), "leftLeg": ("leftLeg", "leftShin")}
    filled = []
    for limb, (upper, lower) in pairs.items():
        for half, bn in enumerate((upper, lower)):
            b = bone(g, bn)
            assert len(b["cubes"]) == 1 and "uv" not in b["cubes"][0], f"pw_husk {bn}: expected one cube without uv"
            b["cubes"][0]["uv"] = split_face_uv(limbs[limb], half)
            filled.append(bn)
    jw(p, doc)
    report["husk"] = {"filled": filled, "source": "husk.jem per-face uv, split 6/6"}


def add_item_bones(path, right_parent, right_pivot, left_parent=None, left_pivot=None):
    doc, g = geo(path)
    names = {b["name"] for b in g["bones"]}
    added = []
    if "rightItem" not in names:
        g["bones"].append({"name": "rightItem", "parent": right_parent, "pivot": right_pivot}); added.append("rightItem")
    if left_parent and "leftItem" not in names:
        g["bones"].append({"name": "leftItem", "parent": left_parent, "pivot": left_pivot}); added.append("leftItem")
    jw(path, doc)
    return added


def fix_pillager(report):
    # vanilla pillager: rightItem under rightArm at [-6, 15, 1], leftItem under leftArm at [6, 15, 1] — here under the forearms
    added = add_item_bones(DST / "models/entity/pw_pillager.geo.json", "rightForearm", [-6, 15, 1], "leftForearm", [6, 15, 1])
    report["pillager"] = {"added": added}


def fix_vindicator(report):
    p = DST / "models/entity/pw_vindicator.geo.json"; doc, g = geo(p)
    body = bone(g, "body")
    crossed = [c for c in body["cubes"] if abs(c["origin"][1] - 14.4719) < 1e-3]
    assert len(crossed) == 3, f"expected the 3 crossed-arm cubes at y 14.4719, found {len(crossed)}"
    body["cubes"] = [c for c in body["cubes"] if c not in crossed]
    # the JEM's arms_rotation point: translate [0, 22.5, 0.35] (depth-1 submodel, absolute) -> Bedrock pivot [0, 22.5, 0.35]
    g["bones"].append({"name": "arms", "pivot": [0, 22.5, 0.35], "cubes": crossed})
    doc2 = doc
    jw(p, doc2)
    added = add_item_bones(p, "rightForearm", [-5.5, 16, 0.5])   # vanilla vindicator rightItem pivot
    report["vindicator"] = {"moved_to_arms": [c["origin"] + c["size"] for c in crossed], "added": ["arms"] + added}


def fix_witch(report):
    jem = jem_load(CEM / "witch.jem")
    conv = {b["name"]: b for b in to_bedrock(jem_tree(jem))}
    arms, arms2 = copy.deepcopy(conv["arms"]), copy.deepcopy(conv["arms2"])
    assert arms["parent"] is None and not arms["cubes"] and arms2["parent"] == "arms" and len(arms2["cubes"]) == 3
    arms.pop("cubes"); arms.pop("parent")
    if not any(arms["rotation"]): arms.pop("rotation")
    p = DST / "models/entity/pw_witch.geo.json"; doc, g = geo(p)
    names = {b["name"] for b in g["bones"]}
    assert "arms" not in names and "arms2" not in names
    g["bones"] += [arms, arms2]
    jw(p, doc)
    report["witch"] = {"arms": arms, "arms2": {k: v for k, v in arms2.items() if k != "cubes"}, "cubes": len(arms2["cubes"])}


def stamp_manifest():
    man = jl(DST / "manifest.json"); v = [int(x) for x in VER.split(".")]
    man["header"]["version"] = v
    for m in man["modules"]: m["version"] = v
    man["header"]["name"] = f"AbsolutRealism Hostile Mobs RP v{VER}"
    man["header"]["description"] = (
        f"v{VER} ({DATE}) FOUR WIRING FIXES from the 09-28 witness read (D-C267): the creeper's charged shell now shows only on charged "
        "creepers (render controller gated on query.is_powered, as vanilla); the husk's arms and legs get their texture maps (the limb cubes "
        "had none); the pillager and vindicator get hand bones so the crossbow and axe sit in their hands; the vindicator's crossed arms move to "
        "their own bone so they hide when it attacks; the witch gets her crossed arms (converted from the Patrix model). Everything else "
        "byte-identical to v1.4.8.")
    jw(DST / "manifest.json", man)


def main():
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    report = {}
    fix_creeper(report); fix_husk(report); fix_pillager(report); fix_vindicator(report); fix_witch(report)
    stamp_manifest()
    json.dump(report, open(ROOT / "_logs/rp06_149_build_report.json", "w"), indent=1)
    log(f"RP-06 v{VER}: creeper RC gated · husk 8 limb UVs · pillager rightItem/leftItem · vindicator arms bone + rightItem · witch arms (CONV-1) -> {DST}")


if __name__ == "__main__":
    main()
