#!/usr/bin/env python3
"""spawn_group_audit.py — his 17:47 report: "Wrong spawn group: kiwi and slug were filed as water animals ... I noticed wrong
spawn group as an error across quite a few; please double check this across all."

For every creature in the habitat table (tools/habitat_table.py), read the BODY from its behaviour file (BP-02 1.3.206):
  breathes   minecraft:breathable  (breathes_air / breathes_water; vanilla default = air only)
  moves      the navigation component (walk / swim / fly / hover / climb / generic / float) + movement.* + swim behaviours
  hostile    a minecraft:behavior.nearest_attackable_target in the ALWAYS-ON components that can target the player
and decide the spawn group it SHOULD have:
  water_animal  lives in water: cannot breathe air, OR swims by navigation and its habitat place is underwater (W/Wb/Cw)
  monster       hostile to the player by default
  ambient       small fliers that are scenery (insects with wings, bats)
  animal        everything else (land, shore, air-breathing swimmers that come ashore)
Compared with the group its CURRENT rule uses (SPAWN-VIABILITY-AUDIT rows). Also flags body vs habitat contradictions
(a water-only body given a land place, or the reverse). Writes _docs/mobs/SPAWN-GROUP-AUDIT-2026-10-02.json/.md"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
from habitat_table import HABITAT  # noqa: E402

BP = ROOT / "_build/bp02-206"
AUDIT = ROOT / "_docs/mobs/SPAWN-VIABILITY-AUDIT-2026-10-02.json"
WATER_PLACES = {"W", "Wb", "Cw"}
AMBIENT_WORDS = {"butterfly", "moth", "firefly", "dragonfly", "bee", "wasp", "hornet", "fly", "mosquito", "bat", "ladybug",
                 "ladybird", "cicada", "damselfly", "hummingbird_moth", "locust", "grasshopper"}


def jl(path):
    """lenient JSON: line comments, block comments and trailing commas (several add-on files carry them)."""
    text = path.read_text(encoding="utf-8-sig")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r'("(?:\\.|[^"\\])*")|//[^\n]*', lambda m: m.group(1) or "", text)
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    return json.loads(text)


def entity_files():
    out = {}
    for p in sorted(BP.rglob("entities/**/*.json")):
        try:
            d = jl(p)
        except Exception:  # noqa: BLE001
            continue
        e = d.get("minecraft:entity") if isinstance(d, dict) else None
        if e:
            ident = (e.get("description") or {}).get("identifier")
            if ident:
                out.setdefault(ident, (p, e))
    return out


def _only_player(f):
    """True when a filter block is satisfied by 'the other is a player' alone (no extra condition)."""
    if isinstance(f, list):
        return len(f) == 1 and _only_player(f[0])
    if not isinstance(f, dict):
        return False
    if "test" in f:
        return f.get("test") == "is_family" and f.get("value") == "player" and f.get("operator", "==") in ("==", "equals") \
            and f.get("subject", "other") == "other"
    if "all_of" in f:
        return all(_only_player(x) or _player_family_any(x) for x in f["all_of"]) and len(f["all_of"]) == 1
    if "any_of" in f:
        return any(_only_player(x) for x in f["any_of"])
    return False


def _player_family_any(f):
    return isinstance(f, dict) and "any_of" in f and any(_only_player(x) for x in f["any_of"])


def targets_player(comp):
    """'always' = attacks players on sight with no extra condition; 'conditional' = only when ridden / charged / dark /
    a variant; False = never."""
    t = comp.get("minecraft:behavior.nearest_attackable_target")
    if not t:
        return False
    types = t.get("entity_types", [])
    types = types if isinstance(types, list) else [types]
    kinds = set()
    for e in types:
        f = e.get("filters", e) if isinstance(e, dict) else {}
        if "player" not in json.dumps(f):
            continue
        kinds.add("always" if _only_player(f) else "conditional")
    return "always" if "always" in kinds else ("conditional" if kinds else False)


def body(e):
    comps = e.get("components") or {}
    groups = e.get("component_groups") or {}
    every = [comps] + list(groups.values())
    br = next((c["minecraft:breathable"] for c in [comps] + list(groups.values()) if "minecraft:breathable" in c), {})
    air = br.get("breathes_air", True)
    water = br.get("breathes_water", False)
    navs = sorted({k.split(".", 1)[1] for c in every for k in c if k.startswith("minecraft:navigation.")})
    moves = sorted({k.split(".", 1)[1] for c in every for k in c if k.startswith("minecraft:movement.")})
    swims = any(k in c for c in every for k in ("minecraft:behavior.swim_wander", "minecraft:behavior.random_swim",
                                                    "minecraft:underwater_movement", "minecraft:behavior.swim_idle"))
    flies = any(k in c for c in every for k in ("minecraft:can_fly", "minecraft:behavior.random_fly",
                                                    "minecraft:navigation.fly", "minecraft:navigation.hover",
                                                    "minecraft:flying_speed"))
    families = sorted(set((comps.get("minecraft:type_family") or {}).get("family", [])))
    return {"air": air, "water": water, "navs": navs, "moves": moves, "swims": swims, "flies": flies,
            "hostile": targets_player(comps), "families": families}


def proposed(ident, b, place):
    words = set(re.split(r"[^a-z]+", ident.split(":", 1)[-1].lower()))
    if not b["air"] or (place in WATER_PLACES and (b["swims"] or "swim" in b["navs"] or "generic" in b["navs"])):
        return "water_animal", "lives in water" + (" (cannot breathe air)" if not b["air"] else "") + \
            (" — hostile, but water creatures keep the water cap" if b["hostile"] == "always" else "")
    if b["hostile"] == "always" or "monster" in b["families"]:
        # his M1 ruling: every hostile species becomes neutral (half-heart bite) and gets a larger hostile twin; only the
        # twins ('Giant X', built in #166) take the monster group
        return "animal", "land / shore — hostile today, neutral after M1 (its Giant twin takes the monster group)"
    # insects stay 'animal': Bedrock's ambient cap is the bats' small pool, and his rule is that every mob gets seen
    return "animal", "land / shore / air-breathing"


def main():
    ents = entity_files()
    audit = {r["id"]: r for r in json.loads(AUDIT.read_text())["rows"]}
    rows, issues = [], Counter()
    for ident, spec in sorted(HABITAT.items()):
        if spec.startswith("SKIP"):
            continue
        place = spec.split("|")[1]
        if ident not in ents:
            rows.append({"id": ident, "error": "no behaviour file in BP-02 1.3.206"})
            issues["no_file"] += 1
            continue
        path, e = ents[ident]
        b = body(e)
        want, why = proposed(ident, b, place)
        cur = (audit.get(ident) or {}).get("population")
        flags = []
        if not b["air"] and place not in WATER_PLACES:
            flags.append("BODY-WATER-ONLY but habitat place is " + place)
        if b["air"] and not b["water"] and place in WATER_PLACES and not (b["swims"] or "swim" in b["navs"]):
            flags.append("air-breather with no swim behaviour given an underwater place")
        r = {"id": ident, "place": place, "current": cur, "should": want, "why": why, "body": b,
             "file": str(path.relative_to(BP)), "flags": flags}
        r["wrong"] = cur is not None and cur != want
        rows.append(r)
        issues["wrong" if r["wrong"] else ("no_rule" if cur is None else "right")] += 1
        for f in flags:
            issues["flag"] += 1
    out = ROOT / "_docs/mobs/SPAWN-GROUP-AUDIT-2026-10-02.json"
    out.write_text(json.dumps({"counts": issues, "rows": rows}, indent=1))
    print(dict(issues))
    print(Counter((r.get("current"), r.get("should")) for r in rows if r.get("wrong")).most_common())
    for r in rows:
        if r.get("flags"):
            print("FLAG", r["id"], r["flags"], r["body"]["navs"], r["body"]["moves"])


if __name__ == "__main__":
    main()
