#!/usr/bin/env python3
"""tree_wire_t2.py — tree program T2: every worldgen tree is now one of our 544 templates (D-C477 P-1/P-3: a
structure_template_feature keeps custom states and rotates all four ways). BP-02 1.3.206 (undelivered, in place):
  structures/pw/trees/<name>.mcstructure        544 templates from _staging/trees (void outside the tree: no carving)
  features/pw_tree_<name>_feature.json           one structure_template_feature per template (facing random,
                                                 may intersect air / plants / any leaves, never ground or logs)
  the 12 pw:<sp>_<age>_tree_feature + 5 pw:<sp>_elder_tree_feature_v2 files (tree_feature) -> weighted pools of their
  templates (same identifiers, so the vanilla override chain and the *_with_vines aggregates keep working);
  minecraft:acacia / cherry / mangrove_tree_feature (vanilla-log tree_features) -> pools of their 32 templates.
  scripts/main.js: PW_SCANNER_ON = false (T5: no leaf scanner once every tree is a template; event decay stays).
Backups: _docs/trees/before_t2/. Report: _docs/trees/T2-WIRE-REPORT.json."""
import json
import re
import shutil
from pathlib import Path

B = Path("/home/claude/_build/bp02-206")
STG = Path("/home/claude/_staging/trees")
BK = Path("/home/claude/_docs/trees/before_t2")
ALLOW = ["minecraft:air", "minecraft:short_grass", "minecraft:tall_grass", "minecraft:fern", "minecraft:large_fern",
         "minecraft:vine", "minecraft:snow_layer", "minecraft:dandelion", "minecraft:poppy", "minecraft:pink_petals",
         "minecraft:azalea", "minecraft:flowering_azalea", "minecraft:sweet_berry_bush", "minecraft:bush",
         "minecraft:moss_carpet", "minecraft:big_dripleaf", "minecraft:small_dripleaf_block", "minecraft:leaves",
         "minecraft:leaves2", "minecraft:cherry_leaves", "minecraft:mangrove_leaves", "minecraft:azalea_leaves",
         "minecraft:azalea_leaves_flowered", "minecraft:pale_oak_leaves", "minecraft:mangrove_propagule",
         "minecraft:water", "minecraft:mangrove_roots"] + \
        [f"pw:{s}_leaves" for s in ("oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "pale_oak", "cherry", "mangrove",
                                    "azalea", "flowering_azalea")]
# which existing feature identifier each staged family replaces
TARGET = {}
for sp in ("oak", "birch", "spruce", "jungle"):
    for age in ("young", "mature", "old"):
        TARGET[(sp, age)] = (f"pw_{sp}_{age}_tree_feature.json", f"pw:{sp}_{age}_tree_feature")
for sp in ("oak", "spruce", "jungle", "dark_oak", "pale_oak"):
    TARGET[(f"{sp}_elder", "elder")] = (f"pw_{sp}_elder_tree_feature_v2.json", f"pw:{sp}_elder_tree_feature_v2")
for sp in ("acacia", "cherry", "mangrove"):
    TARGET[(sp, "elder")] = (f"{sp}_tree_feature.json", f"minecraft:{sp}_tree_feature")


def backup(p):
    dst = BK / p.relative_to(B)
    if not dst.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)


def main():
    (B / "structures/pw/trees").mkdir(parents=True, exist_ok=True)
    report = {"templates": 0, "features": 0, "pools": {}}
    for (fam, age), (fname, ident) in TARGET.items():
        src = STG / fam
        files = sorted(src.glob(f"{fam}_{age}_*.mcstructure"))
        assert files, (fam, age)
        members = []
        for f in files:
            m = re.match(rf"{fam}_{age}_(\d+)\.mcstructure", f.name)
            short = f"{fam}_{m.group(1)}" if age == "elder" else f"{fam}_{age}_{m.group(1)}"
            shutil.copy2(f, B / "structures/pw/trees" / f"{short}.mcstructure")
            feat_id = f"pw:tree_{short}_feature"
            (B / "features" / f"pw_tree_{short}_feature.json").write_text(json.dumps({
                "format_version": "1.21.40",
                "minecraft:structure_template_feature": {
                    "description": {"identifier": feat_id},
                    "structure_name": f"pw:trees/{short}",
                    "adjustment_radius": 0,
                    "facing_direction": "random",
                    "constraints": {"block_intersection": {"block_allowlist": ALLOW}}}}, indent=1))
            members.append([feat_id, 1])
            report["templates"] += 1
            report["features"] += 1
        pool = B / "features" / fname
        backup(pool)
        pool.write_text(json.dumps({"format_version": "1.13.0", "minecraft:weighted_random_feature": {
            "description": {"identifier": ident}, "features": members}}, indent=1))
        report["pools"][ident] = len(members)
    mj = B / "scripts/main.js"
    backup(mj)
    s = mj.read_text()
    s = s.replace("const PW_SCANNER_ON = true;", "const PW_SCANNER_ON = false;   // T2 wired every species to templates (tools/tree_wire_t2.py)")
    mj.write_text(s)
    report["scanner"] = "off"
    Path("/home/claude/_docs/trees/T2-WIRE-REPORT.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
