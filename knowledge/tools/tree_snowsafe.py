#!/usr/bin/env python3
"""tree_snowsafe.py — trees on SNOW (D-C513, census 0.0.4: 0 of ours in 27 land chunks with >= 75 % snow cover, 0.80 per
chunk on bare ground). The heightmap cell sits ABOVE the snow layer, so a template's root landed on snow and `grounded`
refused it (snow_layer was already in the intersection allowlist). Fix: every heightmap tree rule places a
`minecraft:search_feature` wrapper that tries the heightmap cell first (bare ground: unchanged) and then the cell below
(the snow layer, replaced by the root, which then stands on the ground). Writes pw:snowsafe_<pool>_feature wrappers and
rewrites the rules' places_feature in the given build dir. Rules with a uniform y (emerald jungle canopy, misty dark
canopy) are left alone."""
import json
import sys
from pathlib import Path


def wrapper(ident, target):
    # "+y": the cell BELOW the heightmap first (a snow layer there is replaced by the root, which then stands on the dirt
    # like a vanilla trunk; on bare ground that cell is the grass block, not in the allowlist, so the search moves up),
    # then the heightmap cell itself (bare ground: unchanged; a full snow block: the tree stands on it, like vanilla)
    return {"format_version": "1.21.40", "minecraft:search_feature": {
        "description": {"identifier": ident}, "places_feature": target,
        "search_volume": {"min": [0, -2, 0], "max": [0, 0, 0]}, "search_axis": "+y", "required_successes": 1}}


def retune_templates(B):
    """every template feature: `grounded` -> `leveled` (terrain samples = a solid block with a non-solid block above:
    snow blocks pass, water fails), intersections checked for the template's SOLID blocks only (its empty cells no longer
    collide with a hillside); `unburied` stays. Returns the count."""
    n = 0
    for p in sorted((B / "features").glob("pw_tree_*_feature.json")):
        d = json.loads(p.read_text(encoding="utf-8-sig"))
        f = d.get("minecraft:structure_template_feature")
        if not f:
            continue
        c = f.setdefault("constraints", {})
        c["grounded"] = {}                                   # the anti-float guard stays (v2 without it: 58/115 forest roots on air)
        c.pop("leveled", None)
        c.setdefault("unburied", {})
        bi = c.setdefault("block_intersection", {})
        allow = bi.setdefault("block_allowlist", [])
        for extra in ("minecraft:snow", "minecraft:powder_snow"):          # full snow blocks: the root may replace one (marker probe: the grove's snow is 1 deep over dirt)
            if extra not in allow:
                allow.append(extra)
        bi["only_check_intersection_for_motion_blocking_blocks"] = True
        p.write_text(json.dumps(d, indent=1))
        n += 1
    return n


def apply(build):
    B = Path(build)
    rules = sorted((B / "feature_rules").glob("*.json"))
    changed, wrappers = 0, {}
    for p in rules:
        d = json.loads(p.read_text(encoding="utf-8-sig"))
        fr = d["minecraft:feature_rules"]
        feat = fr["description"]["places_feature"]
        y = fr.get("distribution", {}).get("y")
        if not (isinstance(y, str) and "heightmap" in y):
            continue
        if not ("tree" in feat or "mix_" in feat or "bush" in feat):
            continue
        if feat.startswith("pw:snowsafe_"):
            continue
        stem = feat.split(":")[1].replace("_feature", "")
        wid = f"pw:snowsafe_{stem}_feature"
        wrappers[wid] = feat
        fr["description"]["places_feature"] = wid
        p.write_text(json.dumps(d, indent=1))
        changed += 1
    for wid, target in wrappers.items():
        (B / "features" / f"{wid.split(':')[1]}.json").write_text(json.dumps(wrapper(wid, target), indent=1))
    nt = retune_templates(B)
    print(f"snowsafe: {changed} rules now place {len(wrappers)} search wrappers (y-2, y-1, y); {nt} template features: grounded kept, snow blocks allowed, solid-only intersection")
    return changed, wrappers


if __name__ == "__main__":
    apply(sys.argv[1])
