#!/usr/bin/env python3
"""civ_variants.py — CIVITAS V2 diversification (his 20:04 ruling: my call, research-based; the economy draft §4 "each
villager's house is different", his 13:31 ruling). Every dwelling / shop of the roster gets SKIN variants b, c, d beside the
authored a: the same plan, markers and zones (nothing moves), different materials — and for the plain rectangles a
different roof FORM (gable <-> hip). The farms, lumberyard, quarry and well keep their one skin (their character is the yard).

  skin  walls                 posts                 roof form / material    hearth + flue          furniture   door
  a     oak planks            spruce log            as authored / spruce    as authored            oak         wooden
  b     spruce planks         oak log               form swapped / oak      stone bricks           spruce      spruce
  c     dark oak planks       spruce log            as authored / thatch*   brick                  dark oak    spruce
  d     oak planks            dark oak log          form swapped / spruce   cobblestone            spruce      wooden
  * thatch has no hip / ridge-end / pyramidion pieces -> skin c keeps the gable form; a hip-authored building gets oak in c.

Materials are swapped on the finished structure's PALETTE (the states of every swapped block are identical across woods —
checked by the roster census), so stations, zones, lids and the stage cutter's classes (planks floors, log frames, pw:roof*,
pw:hearth*, pw:flue*) are untouched. The roof form is swapped by routing gable_roof <-> hip_roof while the building is
generated (both return the top feet level the flues use). Names: pw:mvv_<building>_<skin>_r1 (the "a" slot was reserved
for this). Output beside the roster in _staging/civ; the marker audit and the stage cutter run on every variant."""
import json
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import civ_roster as R  # noqa: E402

SKINNED = ["cottage_s", "cottage_m", "cottage_l", "bakery", "butcher", "smithy", "inn", "town_hall"]
FORM_SWAP = {"cottage_s", "cottage_m", "bakery", "butcher", "smithy"}        # plain rectangles: gable <-> hip is safe
SKINS = {
    "b": {"walls": "minecraft:spruce_planks", "posts": "minecraft:oak_log", "roof": "oak", "hearth": "stone_bricks",
          "furn": "spruce", "door": "minecraft:spruce_door", "swap_form": True},
    "c": {"walls": "minecraft:dark_oak_planks", "posts": "minecraft:spruce_log", "roof": "thatch", "hearth": "brick",
          "furn": "dark_oak", "door": "minecraft:spruce_door", "swap_form": False},
    "d": {"walls": "minecraft:oak_planks", "posts": "minecraft:dark_oak_log", "roof": "spruce", "hearth": "cobblestone",
          "furn": "spruce", "door": "minecraft:wooden_door", "swap_form": True},
}
ROOF_PIECES = ("roof45", "roof45_ridge", "roof_hip", "roof_pyramidion", "roof_ridge_end", "roof63_lower", "roof63_upper",
               "roof_gusset_lower", "roof_gusset_upper")
HIP_ONLY = ("roof_hip", "roof_pyramidion", "roof_ridge_end")                 # no thatch pieces of these exist


def rename(name, skin, form_hipped):
    """the palette substitution for one block name under a skin."""
    s = SKINS[skin]
    if name == "minecraft:oak_planks":
        return s["walls"]
    if name == "minecraft:spruce_log":
        return s["posts"]
    if name in ("minecraft:wooden_door", "minecraft:spruce_door"):
        return s["door"]
    for piece in ROOF_PIECES:
        for mat in ("oak", "spruce", "thatch"):
            if name == f"pw:{piece}_{mat}":
                want = s["roof"]
                if want == "thatch" and (piece in HIP_ONLY or form_hipped or piece.startswith("roof63") or piece.startswith("roof_gusset")):
                    want = "oak"                                     # thatch only exists as roof45 + ridge
                return f"pw:{piece}_{want}"
    for base in ("oak_planks", "spruce_planks", "stone_bricks", "brick", "cobblestone"):
        if name == f"pw:hearth_{base}":
            return f"pw:hearth_{s['hearth']}"
        if name == f"pw:flue_{base}":
            return f"pw:flue_{s['hearth']}"
    if name.startswith("pw:furn_"):
        for wood in ("_dark_oak", "_oak", "_spruce"):
            if name.endswith(wood):
                return name[: -len(wood)] + "_" + s["furn"]
    return name


def build_variant(key, skin):
    """generate the building with the skin's roof form, then swap the palette."""
    s = SKINS[skin]
    orig_gable, orig_hip = R.gable_roof, R.hip_roof
    hipped = {"v": None}
    if s["swap_form"] and key in FORM_SWAP:
        def gable_as_hip(b, X, W, eave, roof="pw:roof45_spruce", gable="minecraft:oak_planks", x0=0, x1=None, z0=1, z1=None):
            hipped["v"] = True
            return orig_hip(b, X, W, eave, mat=roof.split("_")[-1], x0=x0, x1=x1, z0=z0, z1=z1)

        def hip_as_gable(b, X, W, eave, mat="spruce", x0=0, x1=None, z0=1, z1=None):
            hipped["v"] = False
            return orig_gable(b, X, W, eave, roof=f"pw:roof45_{mat}", x0=x0, x1=x1, z0=z0, z1=z1)
        R.gable_roof, R.hip_roof = gable_as_hip, hip_as_gable
    try:
        b = R.ROSTER[key]()
    finally:
        R.gable_roof, R.hip_roof = orig_gable, orig_hip
    form_hipped = hipped["v"] if hipped["v"] is not None else any(n.startswith("pw:roof_hip") for n, *_ in b.st.palette)
    b.name = b.name.replace("_a_r1", f"_{skin}_r1")
    b.st.palette = [(rename(n, skin, form_hipped), st, ver) for n, st, ver in b.st.palette]
    return b


def main():
    keys = sys.argv[1:] or SKINNED
    report = {}
    for key in keys:
        for skin in SKINS:
            b = build_variant(key, skin)
            stem = b.name.split(":")[1]
            b.write(R.OUT / "structures/pw" / f"{stem}.mcstructure", R.OUT / "manifests" / f"{stem}.json")
            m = b.manifest()
            names = sorted({x[3] for x in m["blocks"]})
            report[b.name] = {"size": m["size"], "blocks": len(m["blocks"]), "entities": len(b.st.entities),
                              "roof": sorted(n for n in names if n.startswith("pw:roof")), "walls": [n for n in names if n.endswith("_planks")]}
            print(b.name, m["size"], "blocks", len(m["blocks"]), "ents", len(b.st.entities), report[b.name]["roof"][:3])
    (R.OUT / "VARIANTS-REPORT.json").write_text(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
