#!/usr/bin/env python3
"""tiny_mobs_round.py — task #166, his rulings (D-C462 / D-C465 / D-C467):
  M1  every small mob that can be hostile becomes NEUTRAL: it only fights back when hit.
  M2  its bite is half a heart (damage 1); no venom on the small ones.
  M3  the hostile purpose moves to a LARGER twin: 2.5 hearts (damage 5).
  H1 a  one twin PER SPECIES ("Giant <name>"); H2 target lengths: ant 1.5, scorpion 2.5, beetle 2, centipede 3, hornet 1.2,
        rat 1.5, crab 2, piranha 1.2, snake 4 blocks; H3 a: the twin spawns where its species spawns, 1/5 as often.
  M4  size law v2 lands on the 33 adults that missed it (adult had no minecraft:scale) + the desert centipede.
Source of the in-scope list: _docs/mobs/TINY-MOBS-CENSUS-2026-10-02.md (190 rows, parsed to TINY-MOBS-CENSUS-rows.json).
Out of scope by his H2 list: the optional giants (fly, worm, endermite); vanilla ids (endermite, bee) are not touched.
Writes into the undelivered builds BP-02 1.3.206 and RP-07 1.4.44. Report: _docs/mobs/TINY-MOBS-ROUND-REPORT.json"""
import copy
import json
import re
import sys
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import spawn_gen as G  # noqa: E402  (lenient loader, entity / rule index)

BP = ROOT / "_build/bp02-206"
RP = ROOT / "_build/rp07-1444"
RP_SEARCH = [ROOT / "_build" / d for d in ("rp07-1444", "rp08-1413", "rp06-1428", "rp01-116", "rp04-156")]
ROWS = json.loads((ROOT / "_docs/mobs/TINY-MOBS-CENSUS-rows.json").read_text())
TARGET_LEN = {"pw:giant_ant": 1.5, "pw:giant_scorpion": 2.5, "pw:giant_beetle": 2.0, "pw:giant_centipede": 3.0,
              "pw:giant_hornet": 1.2, "pw:giant_rat": 1.5, "pw:giant_crab": 2.0, "pw:giant_piranha": 1.2,
              "pw:giant_viper": 4.0}
SIZE_FIX = {  # census §E: size law v2 factor for adults that had NO minecraft:scale (current adult 1.0)
    "pw:anteater_ytri": 0.325, "pw:baby_african_black_eagle_ysav": 0.657, "pw:baby_fisher_eagle_ysav": 0.563,
    "pw:beluga_ytri": 0.923, "pw:blue_jay_wa": 0.323, "pw:boar_wa": 0.795, "pw:crab_wa": 0.269, "pw:dove_wa": 0.362,
    "pw:duck_wa": 0.636, "pw:eagle_wa": 0.601, "pw:emu_ytri": 0.735, "pw:hedgehog_wa": 0.619,
    "pw:honey_badger_ysav": 0.54, "pw:hyenas_wa": 0.834, "pw:jerboa_wwa": 0.288, "pw:kakapo_wwa": 0.6,
    "pw:koala_ytri": 0.745, "pw:komodo_dragon_wa": 0.913, "pw:orca_ytri": 1.374, "pw:pangolin_ysav": 0.446,
    "pw:platypus_ytri": 0.452, "pw:prairie_dog_wwa": 0.377, "pw:rat_wa": 0.19, "pw:red_panda_wa": 0.67,
    "pw:serval_ysav": 0.892, "pw:shoebill_wwa": 0.705, "pw:snake_scarlet_wa": 0.158, "pw:swan_wwa": 1.151,
    "pw:toadfish_wwa": 0.267, "pw:tortoise_ysav": 0.229, "pw:toucan_wa": 0.487, "pw:tsessebe_ysav": 1.125,
    "pw:turkey_wa": 0.772,
    "pw:centipede_desert_anf": 0.1113,   # skipped by v2 (parse error); same species size as the Pacific giant (0.2 m)
}
BEFORE = ROOT / "_docs/mobs/before_tiny_round/bp02_entities"     # the entity files as they were before this round
VENOMOUS_SNAKE_WORDS = {"viper", "rattle", "rattlesnake", "cobra", "coral", "mamba", "adder", "krait", "taipan"}
DESERT_CENTIPEDE_MODEL_LEN = 2.483       # model length at scale 1.0 (same model as the other AnF centipedes)
BABY_COMPONENTS = {"minecraft:is_baby", "minecraft:ageable", "minecraft:breedable", "minecraft:behavior.breed",
                   "minecraft:behavior.follow_parent", "minecraft:tameable", "minecraft:behavior.tempt"}
TARGET_KEYS = ("minecraft:behavior.nearest_attackable_target", "minecraft:behavior.nearest_prioritized_attackable_target")


def mentions_player(x):
    return '"player"' in json.dumps(x)


def strip_player(filters):
    """Remove the player from a filter tree. Returns the new tree, or None when the tree only ever matched players."""
    if isinstance(filters, list):
        out = [y for y in (strip_player(x) for x in filters) if y is not None]
        return out or None
    if not isinstance(filters, dict):
        return filters
    if "test" in filters:
        return None if (filters.get("value") == "player" and filters.get("test") in ("is_family", "is_target")) else filters
    for key in ("any_of", "all_of", "none_of"):
        if key in filters:
            if key == "none_of":
                return filters
            inner = [y for y in (strip_player(x) for x in filters[key]) if y is not None]
            if key == "all_of" and len(inner) < len(filters[key]):
                return None          # an AND that required "is a player" can no longer match anyone else
            if not inner:
                return None
            return {key: inner}
    return filters


def containers(ent):
    yield "base", ent.setdefault("components", {})
    for name, g in (ent.get("component_groups") or {}).items():
        yield name, g


def neutralize(ent):
    """M1 + M2: no player target anywhere; bites deal 1 (half a heart) with no venom; fights back when hit."""
    changes = []
    for where, comps in containers(ent):
        for key in TARGET_KEYS:
            comp = comps.get(key)
            if not comp or not mentions_player(comp):
                continue
            types = comp.get("entity_types", [])
            single = not isinstance(types, list)
            types = [types] if single else types
            kept = []
            for t in types:
                f = strip_player(t.get("filters", {})) if mentions_player(t) else t.get("filters")
                if f is None:
                    continue
                t2 = dict(t)
                t2["filters"] = f
                kept.append(t2)
            if kept:
                comp["entity_types"] = kept
                changes.append(f"{where}:{key.split('.')[-1]} player removed ({len(types) - len(kept)} entries dropped)")
            else:
                del comps[key]
                changes.append(f"{where}:{key.split('.')[-1]} removed (player only)")
        atk = comps.get("minecraft:attack")
        if atk:
            before = json.dumps(atk)
            atk["damage"] = 1
            for k in ("effect_name", "effect_duration"):
                atk.pop(k, None)
            if json.dumps(atk) != before:
                changes.append(f"{where}:attack -> 1, no venom")
    base = ent["components"]
    has_melee = any("minecraft:behavior.melee_attack" in c or "minecraft:behavior.melee_box_attack" in c
                    for _, c in containers(ent))
    if has_melee and "minecraft:behavior.hurt_by_target" not in base:
        base["minecraft:behavior.hurt_by_target"] = {"priority": 1}
        changes.append("base:hurt_by_target added (fights back)")
    return changes


def strip_groups_from_events(ent, removed):
    def walk(node):
        if isinstance(node, dict):
            for k in ("add", "remove"):
                if isinstance(node.get(k), dict) and "component_groups" in node[k]:
                    node[k]["component_groups"] = [g for g in node[k]["component_groups"] if g not in removed]
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
    walk(ent.get("events") or {})


def make_twin(src_ent, twin_id, scale, poison):
    ent = copy.deepcopy(src_ent)
    ent["description"]["identifier"] = twin_id
    ent["description"]["is_spawnable"] = True
    ent["description"]["is_summonable"] = True
    ent["description"].pop("runtime_identifier", None)
    groups = ent.get("component_groups") or {}
    removed = {n for n, g in groups.items() if "minecraft:is_baby" in g or re.search(r"baby|tame|breed", n)}
    for n in removed:
        del groups[n]
    strip_groups_from_events(ent, removed)
    for _, comps in containers(ent):
        for k in list(comps):
            if k in BABY_COMPONENTS:
                del comps[k]
            elif k == "minecraft:behavior.avoid_mob_type" and mentions_player(comps[k]):
                del comps[k]                                      # a giant does not flee from players
            elif k in TARGET_KEYS:
                del comps[k]                                      # replaced by one clear hostile target below
        if "minecraft:scale" in comps:
            comps["minecraft:scale"] = {"value": round(scale, 4)}
    base = ent["components"]
    base["minecraft:scale"] = {"value": round(scale, 4)}
    base["minecraft:behavior.nearest_attackable_target"] = {
        "priority": 2, "must_see": True, "reselect_targets": True, "within_radius": 16,
        "entity_types": [{"filters": {"test": "is_family", "subject": "other", "value": "player"}, "max_dist": 16}]}
    base["minecraft:behavior.hurt_by_target"] = {"priority": 1}
    if not any(k in base for k in ("minecraft:behavior.melee_attack", "minecraft:behavior.melee_box_attack")):
        base["minecraft:behavior.melee_attack"] = {"priority": 3, "speed_multiplier": 1.25, "track_target": True}
    atk = {"damage": 5}
    if poison:
        atk.update({"effect_name": "poison", "effect_duration": 5})
    base["minecraft:attack"] = atk
    for _, comps in containers(ent):
        if "minecraft:attack" in comps and comps is not base:
            comps["minecraft:attack"] = dict(atk)
    hp = base.get("minecraft:health", {})
    val = hp.get("value", 10) if isinstance(hp.get("value", 10), (int, float)) else 10
    base["minecraft:health"] = {"value": max(int(val), 20), "max": max(int(val), 20)}
    fam = base.setdefault("minecraft:type_family", {"family": []})["family"]
    for f in ("monster", "pw_giant"):
        if f not in fam:
            fam.append(f)
    base["minecraft:despawn"] = {"despawn_from_distance": {"min_distance": 32, "max_distance": 128}}
    if "minecraft:collision_box" not in base:
        base["minecraft:collision_box"] = {"width": 0.8, "height": 0.4}
    return ent, sorted(removed)


def find_client(ident):
    for pack in RP_SEARCH:
        for p in sorted((pack / "entity").rglob("*.json")):
            try:
                d = G.load(p)
            except Exception:  # noqa: BLE001
                continue
            ce = d.get("minecraft:client_entity") if isinstance(d, dict) else None
            if ce and ce.get("description", {}).get("identifier") == ident:
                return p, d
    return None, None


def lang_name(ident, lang):
    m = re.search(rf"^entity\.{re.escape(ident)}\.name=(.+)$", lang, re.M)
    if m:
        return m.group(1).strip()
    return " ".join(w.capitalize() for w in ident.split(":", 1)[1].split("_"))


def parse_len(row):
    m = re.match(r"([0-9.]+)\s*/", row["size"])
    return float(m.group(1)) if m else None


def parse_scale(row, ident):
    if ident in SIZE_FIX:
        return 1.0                                   # measured at 1.0 (adult had no scale); the twin scale is absolute
    m = re.match(r"([0-9.]+)", row["scale"])
    return float(m.group(1)) if m else 1.0


def main():
    ents = G.index_files("entities", "minecraft:entity")
    rules = G.index_files("spawn_rules", "minecraft:spawn_rules")
    lang_path = RP / "texts/en_US.lang"
    lang = lang_path.read_text(encoding="utf-8")
    sounds_path = RP / "sounds.json"
    sounds = G.load(sounds_path)
    snd = sounds.setdefault("entity_sounds", {}).setdefault("entities", {})
    report = {"size_fix": [], "neutralized": [], "twins": [], "problems": []}
    # ---- A: size law v2 on the adults that missed it
    for ident, factor in SIZE_FIX.items():
        p = ents[ident][0]
        d = G.load(p)
        comps = d["minecraft:entity"]["components"]
        before = comps.get("minecraft:scale")
        comps["minecraft:scale"] = {"value": factor}
        p.write_text(json.dumps(d, indent=2))
        report["size_fix"].append({"id": ident, "before": before, "after": factor})
    # ---- B: neutral small versions
    for row in ROWS:
        ident = row["id"]
        if ident.startswith("minecraft:") or ident == "Identifier":
            continue
        p = ents[ident][0]
        d = G.load(p)
        ch = neutralize(d["minecraft:entity"])
        if ch:
            p.write_text(json.dumps(d, indent=2))
        report["neutralized"].append({"id": ident, "class_before": row["cls"], "changes": ch})
    # ---- C: giant twins
    new_lang = []
    for row in ROWS:
        m = re.search(r"pw:giant_[a-z]+", row["big"])
        arche = m.group(0) if m else None
        extra = [("pw:centipede_desert_anf", "pw:giant_centipede")] if row["id"] == "pw:centipede_brown_anf" else []
        for ident, arche in [(row["id"], arche)] + extra:
            if arche not in TARGET_LEN:
                continue
            src_len = DESERT_CENTIPEDE_MODEL_LEN if ident == "pw:centipede_desert_anf" else parse_len(row)
            src_scale = 1.0 if ident == "pw:centipede_desert_anf" else parse_scale(row, ident)
            if not src_len:
                report["problems"].append((ident, "no measured length"))
                continue
            scale = src_scale * TARGET_LEN[arche] / src_len
            ns, name = ident.split(":", 1)
            twin_id = f"pw:giant_{name}" + ("_nba" if ns == "sf_nba" else "")
            src_doc = G.load(ents[ident][0])
            # venom read from the ORIGINAL file (step B has already taken it off the small version)
            orig = BEFORE / ents[ident][0].relative_to(BP / "entities")
            had_venom = any("effect_name" in (c.get("minecraft:attack") or {}) for _, c in containers(
                G.load(orig)["minecraft:entity"]))
            poison = had_venom or arche in ("pw:giant_scorpion", "pw:giant_centipede", "pw:giant_hornet") or \
                bool(set(re.split(r"[^a-z]+", name)) & VENOMOUS_SNAKE_WORDS)
            twin, removed = make_twin(src_doc["minecraft:entity"], twin_id, scale, poison)
            out = BP / "entities/pw_giants" / f"{twin_id.split(':')[1]}.json"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps({"format_version": src_doc.get("format_version", "1.21.0"),
                                       "minecraft:entity": twin}, indent=2))
            # spawn rule: same places as the species (its generated rule), 1/5 as often, monster group
            src_rule = G.load(rules[ident][0])["minecraft:spawn_rules"]
            conds = []
            for c in src_rule["conditions"]:
                if "minecraft:spawns_on_block_filter" in c:      # the ant-hill condition stays with the small ants
                    continue
                c2 = copy.deepcopy(c)
                c2["minecraft:weight"] = {"default": max(1, round(c["minecraft:weight"]["default"] / 5))}
                c2["minecraft:herd"] = {"min_size": 1, "max_size": 2}
                c2.pop("minecraft:permute_type", None)
                c2.pop("minecraft:spawn_event", None)
                conds.append(c2)
            rule_out = BP / "spawn_rules/pw_giants" / f"{twin_id.split(':')[1]}.json"
            rule_out.parent.mkdir(parents=True, exist_ok=True)
            rule_out.write_text(json.dumps({"format_version": "1.8.0", "minecraft:spawn_rules": {
                "description": {"identifier": twin_id, "population_control": "monster"}, "conditions": conds}}, indent=2))
            # client entity clone (RP-07): same model, pictures, animations; spawn egg darker
            cp, cd = find_client(ident)
            if cd is None:
                report["problems"].append((ident, "no client entity"))
                continue
            cd = copy.deepcopy(cd)
            cd["minecraft:client_entity"]["description"]["identifier"] = twin_id
            egg = cd["minecraft:client_entity"]["description"].get("spawn_egg")
            if isinstance(egg, dict) and "base_color" in egg:
                egg["overlay_color"] = "#8B0000"
            cout = RP / "entity/pw_giants" / f"{twin_id.split(':')[1]}.entity.json"
            cout.parent.mkdir(parents=True, exist_ok=True)
            cout.write_text(json.dumps(cd, indent=2))
            if ident in snd and twin_id not in snd:
                snd[twin_id] = copy.deepcopy(snd[ident])
            nm = "Giant " + lang_name(ident, lang)
            new_lang += [f"entity.{twin_id}.name={nm}", f"item.spawn_egg.entity.{twin_id}.name=Spawn {nm}"]
            report["twins"].append({"id": twin_id, "name": nm, "from": ident, "archetype": arche,
                                    "scale": round(scale, 4), "length_blocks": TARGET_LEN[arche], "poison": poison,
                                    "groups_removed": removed, "client_from": str(cp), "sound": ident in snd,
                                    "weights": [c["minecraft:weight"]["default"] for c in conds]})
    lang_path.write_text(lang.rstrip("\n") + "\n## Giant twins (tiny-mobs round, 2026-10-02)\n" + "\n".join(new_lang) + "\n",
                         encoding="utf-8")
    sounds_path.write_text(json.dumps(sounds, indent=1))
    (ROOT / "_docs/mobs/TINY-MOBS-ROUND-REPORT.json").write_text(json.dumps(report, indent=1))
    print("size fixes", len(report["size_fix"]), "neutralized files", sum(1 for r in report["neutralized"] if r["changes"]),
          "of", len(report["neutralized"]), "twins", len(report["twins"]), "problems", report["problems"])


if __name__ == "__main__":
    main()
