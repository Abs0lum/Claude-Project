#!/usr/bin/env python3
"""tree_rule_coverage.py — D-C517 (Q6 reframed): which biomes does at least one of OUR tree rules target? Evaluates every feature
rule of a BP-02 build that places trees (the 17 legacy overrides + our sparse rules + any rule whose feature chain names a tree)
against the tags of every biome: vanilla 1.26.50 definitions (_ref/bs_sparse/behavior_pack/biomes) + the build's own biomes/.
Usage: tree_rule_coverage.py BUILD_DIR  -> prints covered / uncovered biomes; writes _docs/recheck/W2-TREE-RULE-COVERAGE.json"""
import json, sys
from pathlib import Path
build = Path(sys.argv[1])
def tags_of(f):
    b = json.loads(f.read_text()).get("minecraft:biome", {})
    return b.get("description", {}).get("identifier", f.stem), set(b.get("components", {}).get("minecraft:tags", {}).get("tags", []))
biomes = {}
for f in sorted(Path("/home/claude/_ref/bs_sparse/behavior_pack/biomes").glob("*.json")):
    i, t = tags_of(f); biomes[i] = t
for f in sorted((build / "biomes").glob("*.json")):
    i, t = tags_of(f); biomes[i] = t                       # ours (and any vanilla override) win
def ev(node, tags):
    if isinstance(node, list): return all(ev(n, tags) for n in node)
    if "any_of" in node: return any(ev(n, tags) for n in (node["any_of"] if isinstance(node["any_of"], list) else [node["any_of"]]))
    if "all_of" in node: return all(ev(n, tags) for n in (node["all_of"] if isinstance(node["all_of"], list) else [node["all_of"]]))
    if node.get("test") == "has_biome_tag":
        r = node.get("value") in tags
        return r if node.get("operator", "==") in ("==", "equals") else not r
    return True                                             # other tests (e.g. is_temperature_type) not modelled: treated as pass
TREEY = ("tree", "mix_", "spruce", "oak", "birch", "jungle", "acacia", "savanna", "dark_oak", "taiga", "forest")
rules = []
for f in sorted((build / "feature_rules").glob("*.json")):
    r = json.loads(f.read_text()).get("minecraft:feature_rules", {})
    pf = r.get("description", {}).get("places_feature", "")
    if not any(k in pf for k in TREEY) and "trees" not in f.name: continue
    rules.append((f.name, pf, r.get("conditions", {}).get("minecraft:biome_filter", [])))
# vanilla rules whose feature BP-02 OVERRIDES (an identical "minecraft:" identifier in the build's features/) also place OUR trees
ours = set()
for f in (build / "features").glob("*.json"):
    try:
        d = json.loads(f.read_text())
        for k, v in d.items():
            if isinstance(v, dict) and "description" in v: ours.add(v["description"].get("identifier", ""))
    except Exception:
        pass
own_rule_ids = {json.loads((build / "feature_rules" / n).read_text())["minecraft:feature_rules"]["description"]["identifier"] for n, _, _ in rules}
for f in sorted(Path("/home/claude/_bds/srv/definitions/feature_rules").glob("*.json")):
    try:
        r = json.loads(f.read_text()).get("minecraft:feature_rules", {})
    except Exception:
        continue
    rid, pf = r.get("description", {}).get("identifier", ""), r.get("description", {}).get("places_feature", "")
    if rid in own_rule_ids or pf not in ours or not any(k in pf for k in TREEY):
        continue
    rules.append(("vanilla:" + f.name, pf, r.get("conditions", {}).get("minecraft:biome_filter", [])))
cov = {b: [n for n, pf, bf in rules if ev(bf, t)] for b, t in biomes.items()}
skip = ("ocean", "river", "beach", "the_end", "end_", "nether", "hell", "crimson", "warped", "soulsand", "basalt", "deep_dark", "dripstone", "lush_caves", "stony_shore", "mushroom")
land = {b: r for b, r in cov.items() if not any(s in b for s in skip)}
covered = sorted(b for b, r in land.items() if r); uncovered = sorted(b for b, r in land.items() if not r)
print(f"tree rules: {len(rules)} · land biomes: {len(land)} · covered {len(covered)} · NOT covered {len(uncovered)}")
print("NOT covered:", ", ".join(x.replace("minecraft:", "") for x in uncovered))
print("covered:", ", ".join(f"{x.replace('minecraft:', '')}({len(land[x])})" for x in covered))
Path("/home/claude/_docs/recheck/W2-TREE-RULE-COVERAGE.json").write_text(json.dumps({"rules": [n for n, _, _ in rules], "coverage": cov}, indent=1))
