#!/usr/bin/env python3
"""spawn_gen.py — writes a natural spawn rule for EVERY creature in tools/habitat_table.py into BP-02 1.3.206
(his 16:47: "assign mobs to approximate biomes; all of them ... I want all of the mobs to be seen eventually";
SP1 fix set + SP2 water classes; 17:47: wrong spawn groups fixed across all).

Per creature:
  biome filter  built from its habitat PROFILES (tools/habitat_profiles.py). Each biome of a new world is picked by the
                smallest set of its tags that NO other present biome carries in full; the filter is any_of those picks.
                PROVEN after writing: the filter is evaluated against every present biome's tags and must hit exactly
                the intended set (intended ∩ present) — the run fails otherwise.
  group         tools/spawn_group_audit.py's body reading (water_animal / animal; monster only for the Giant twins, #166)
  placement     L, A, S -> spawns_on_surface + daylight-level brightness (as vanilla animals) · W, Wb -> spawns_underwater
                · C -> spawns_underground, dark · Cw -> spawns_underwater below y 40
  weight        abundance c / u / r / v -> 40 / 20 / 8 / 3 (land) or 30 / 15 / 6 / 2 (water); herd from the table;
                density limit 6 / 4 / 2 / 2
  ants          + a second condition: ants come out ON ant hill blocks (the hill's own release script never ran, D-C471)
Also adds minecraft:despawn (distance despawn; never tamed, leashed or name-tagged) to every rule creature that has none
— Naturalist's own despawn was a script (DespawnRule.js) that never ran, so 'never leave' covered them too.
Existing rule files are rewritten in place (same path); a second rule file for the same creature is moved to _garbage;
the pre-run spawn_rules folder is copied to _docs/mobs/spawn_rules_before_gen/ first.
Report: _docs/mobs/SPAWN-GEN-REPORT-2026-10-02.json"""
import itertools
import json
import os
import re
import shutil
import sys
from collections import Counter
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
from habitat_profiles import PROFILES  # noqa: E402
from habitat_table import HABITAT  # noqa: E402

BP = ROOT / "_build/bp02-206"
AUDIT = ROOT / "_docs/mobs/SPAWN-VIABILITY-AUDIT-2026-10-02.json"
GROUPS = ROOT / "_docs/mobs/SPAWN-GROUP-AUDIT-2026-10-02.json"
BACKUP = ROOT / "_docs/mobs/spawn_rules_before_gen"
GARBAGE = ROOT / "_garbage/spawn_rules_duplicates_206"
REPORT = ROOT / "_docs/mobs/SPAWN-GEN-REPORT-2026-10-02.json"
WEIGHT_LAND = {"c": 40, "u": 20, "r": 8, "v": 3}
WEIGHT_WATER = {"c": 30, "u": 15, "r": 6, "v": 2}
DENSITY = {"c": 6, "u": 4, "r": 2, "v": 2}
WATER_PLACES = {"W", "Wb", "Cw"}
MENAGERIE_SUFFIX = {"anf", "wa", "wwa", "ysav", "ytri", "ws", "ifs"}
DESPAWN = {"despawn_from_distance": {"min_distance": 32, "max_distance": 128},
           "filters": {"all_of": [{"test": "is_tamed", "value": False}, {"test": "is_leashed", "value": False},
                                  {"test": "has_nametag", "value": False}]}}


def lenient(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r'("(?:\\.|[^"\\])*")|//[^\n]*', lambda m: m.group(1) or "", text)
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    return json.loads(text)


def load(path):
    return lenient(path.read_text(encoding="utf-8-sig"))


# ---------------------------------------------------------------- biome tag table (new world, after biome fixes)
def biome_table():
    meta = json.loads(AUDIT.read_text())["meta"]["biomes"]
    table = {}
    for b in meta:
        table[b["id"]] = {"tags": set(b["tags"]), "present": b["present"], "dim": b["dim"]}
    for f in sorted((BP / "biomes").glob("*.biome.json")):       # our biomes: tags as they are NOW (206 + 206b fixes)
        doc = load(f)["minecraft:biome"]
        ident = doc["description"]["identifier"]
        table.setdefault(ident, {"present": True, "dim": "overworld"})
        table[ident]["tags"] = set(doc["components"]["minecraft:tags"]["tags"])
    table["pw:taiga_sparse"]["present"] = True                   # retargeted to Windswept Forest (biome_fixes_206)
    return table


FRAGILE = ("has_structure_", "spawns_", "no_legacy", "overworld_generation", "fast_fishing", "surface_mineshaft",
           "swamp_water_huge_mushroom", "rare")


def tag_cost(t):
    return 4.0 if t.startswith(FRAGILE) else 1.0


def selectors(table):
    """biome -> (positive tags, negated tags): all positives present AND none of the negated -> only this biome among
    the present biomes. Cheapest by cost (fragile structure / spawn-flag tags cost 3, a plain tag 1, a negation 1.5).
    Negations are needed where one of our biomes carries every tag of the vanilla biome it replaces (desert_dunes vs
    desert). None if no such pick exists."""
    present = {k: v["tags"] for k, v in table.items() if v["present"]}
    out = {}
    for b, tags in present.items():
        others = {k: t for k, t in present.items() if k != b}
        best = None
        for n in (1, 2, 3):
            for combo in itertools.combinations(sorted(tags), n):
                rest = [t for t in others.values() if set(combo) <= t]
                negs = []
                ok = True
                for t in rest:
                    diff = sorted(t - tags, key=lambda x: (tag_cost(x), x))
                    if not diff:
                        ok = False
                        break
                    if not any(n_ in t for n_ in negs):
                        negs.append(diff[0])
                if not ok:
                    continue
                cost = sum(tag_cost(x) for x in combo) + 1.5 * len(negs)
                if best is None or cost < best[0]:
                    best = (cost, combo, tuple(negs))
        out[b] = (best[1], best[2]) if best else None
    return out


def filter_for(biomes, sel):
    tests = []
    for b in sorted(biomes):
        pos, neg = sel[b]
        parts = [{"test": "has_biome_tag", "operator": "==", "value": t} for t in pos] + \
                [{"test": "has_biome_tag", "operator": "!=", "value": t} for t in neg]
        tests.append(parts[0] if len(parts) == 1 else {"all_of": parts})
    return tests[0] if len(tests) == 1 else {"any_of": tests}


def evaluate(f, tags):
    if "any_of" in f:
        return any(evaluate(x, tags) for x in f["any_of"])
    if "all_of" in f:
        return all(evaluate(x, tags) for x in f["all_of"])
    if f.get("test") == "has_biome_tag":
        return (f["value"] in tags) == (f.get("operator", "==") in ("==", "equals"))  # '!=' / 'not' -> absent
    raise ValueError(f)


# ---------------------------------------------------------------- existing files
def index_files(folder, root_key):
    idx = {}
    for p in sorted((BP / folder).rglob("*.json")):
        try:
            d = load(p)
        except Exception:  # noqa: BLE001
            continue
        node = d.get(root_key) if isinstance(d, dict) else None
        ident = ((node or {}).get("description") or {}).get("identifier")
        if ident:
            idx.setdefault(ident, []).append(p)
    return idx


def new_rule_path(ident):
    ns, name = ident.split(":", 1)
    if ns == "sf_nba":
        return BP / "spawn_rules/sf_nba" / f"{name}.spawn_rule.json"
    suffix = name.rsplit("_", 1)[-1]
    if ns == "pw" and suffix in MENAGERIE_SUFFIX:
        return BP / "spawn_rules/pw_menagerie" / suffix / f"{name}.json"
    return BP / "spawn_rules" / ns / f"{name}.json"


def condition(place, abundance, herd, bfilter):
    hmin, hmax = (int(x) for x in herd.split("-"))
    water = place in WATER_PLACES
    c = {}
    if place in ("L", "A", "S"):
        c["minecraft:spawns_on_surface"] = {}
        c["minecraft:brightness_filter"] = {"min": 7, "max": 15, "adjust_for_weather": False}
    elif place in ("W", "Wb"):
        c["minecraft:spawns_underwater"] = {}
    elif place == "C":
        c["minecraft:spawns_underground"] = {}
        c["minecraft:brightness_filter"] = {"min": 0, "max": 7, "adjust_for_weather": False}
        c["minecraft:height_filter"] = {"min": -60, "max": 50}
    elif place == "Cw":
        c["minecraft:spawns_underwater"] = {}
        c["minecraft:height_filter"] = {"min": -60, "max": 40}
    else:
        raise ValueError(place)
    c["minecraft:weight"] = {"default": (WEIGHT_WATER if water else WEIGHT_LAND)[abundance]}
    c["minecraft:herd"] = {"min_size": hmin, "max_size": hmax}
    c["minecraft:density_limit"] = {"underground" if place == "C" else "surface": DENSITY[abundance]}
    c["minecraft:biome_filter"] = bfilter
    return c


CARRY = ("minecraft:spawn_event", "minecraft:disallow_spawns_in_bubble")


def carry_over(path):
    """Keep what the ORIGINAL rule did beyond placement: its spawn event (e.g. lion -> lionesses), its bubble rule, and
    the permute entries that turn a spawn into the creature's own variants (gazelle -> female gazelle). Naturalist's
    permutes into VANILLA animals (25 % of 'deer' spawns become a fox) are dropped: each animal has its own rule now.
    Dropped on purpose: grass-only 'spawns_above_block_filter' (bear, turkey), distance / difficulty filters."""
    backup = BACKUP / path.relative_to(BP / "spawn_rules")
    if not backup.exists():
        return {}
    out = {}
    for c in load(backup)["minecraft:spawn_rules"].get("conditions", []):
        for k in CARRY:
            if k in c and k not in out:
                out[k] = c[k]
        if "minecraft:permute_type" in c and "minecraft:permute_type" not in out:
            own = [e for e in c["minecraft:permute_type"] if not str(e.get("entity_type", "")).startswith("minecraft:")]
            if any("entity_type" in e for e in own):
                out["minecraft:permute_type"] = own
    return out


def main():
    table = biome_table()
    sel = selectors(table)
    unpickable = sorted(b for b, s in sel.items() if s is None)
    present = {b for b, v in table.items() if v["present"]}
    groups = {r["id"]: r for r in json.loads(GROUPS.read_text())["rows"] if "should" in r}
    rules_idx = index_files("spawn_rules", "minecraft:spawn_rules")
    ent_idx = index_files("entities", "minecraft:entity")
    if not BACKUP.exists():
        shutil.copytree(BP / "spawn_rules", BACKUP)
    report, counts, problems = [], Counter(), []
    for ident, spec in sorted(HABITAT.items()):
        if spec.startswith("SKIP"):
            continue
        profs, place, abundance, herd = spec.split("|")
        intended = set().union(*(PROFILES[p] for p in profs.split(",")))
        target = intended & present
        missing_sel = sorted(b for b in target if sel.get(b) is None)
        if missing_sel:
            problems.append((ident, "no unique tag pick for " + ", ".join(missing_sel)))
            continue
        bfilter = filter_for(target, sel)
        hit = {b for b in present if evaluate(bfilter, table[b]["tags"])}
        if hit != target:
            problems.append((ident, f"filter hits {sorted(hit ^ target)} wrongly"))
            continue
        group = groups.get(ident, {}).get("should") or ("water_animal" if place in WATER_PLACES else "animal")
        conds = [condition(place, abundance, herd, bfilter)]
        if ident == "sf_nba:ant":
            hill = condition("L", "c", "2-4", {"test": "has_biome_tag", "operator": "==", "value": "overworld"})
            hill["minecraft:spawns_on_block_filter"] = ["sf_nba:ant_hill"]
            hill["minecraft:weight"] = {"default": 80}
            conds.append(hill)
        doc = {"format_version": "1.8.0", "minecraft:spawn_rules": {
            "description": {"identifier": ident, "population_control": group}, "conditions": conds}}
        existing = rules_idx.get(ident, [])
        path = existing[0] if existing else new_rule_path(ident)
        carried = carry_over(path)
        conds[0].update(carried)
        for extra in existing[1:]:
            dest = GARBAGE / extra.relative_to(BP)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(extra), str(dest))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc, indent=2))
        # despawn
        despawn_added = False
        for ep in ent_idx.get(ident, [])[:1]:
            d = load(ep)
            comps = d["minecraft:entity"].setdefault("components", {})
            if "minecraft:despawn" not in comps:
                comps["minecraft:despawn"] = DESPAWN
                ep.write_text(json.dumps(d, indent=2))
                despawn_added = True
        counts["rewritten" if existing else "new"] += 1
        counts["duplicates_moved"] += len(existing) - 1 if existing else 0
        counts["despawn_added"] += despawn_added
        counts[group] += 1
        report.append({"id": ident, "file": str(path.relative_to(BP)), "group": group, "place": place,
                       "abundance": abundance, "herd": herd, "biomes": sorted(target),
                       "not_in_new_world": sorted(intended - present), "despawn_added": despawn_added,
                       "replaced": [str(p.relative_to(BP)) for p in existing], "carried": sorted(carried)})
    REPORT.write_text(json.dumps({"counts": counts, "unpickable_biomes": unpickable, "problems": problems,
                                  "selectors": {b: {"all": list(s[0]), "none": list(s[1])} if s else None for b, s in sorted(sel.items())},
                                  "rules": report}, indent=1))
    print(dict(counts))
    print("biomes without a unique tag pick:", unpickable)
    for p in problems:
        print("PROBLEM", p)


if __name__ == "__main__":
    main()
