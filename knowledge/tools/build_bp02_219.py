#!/usr/bin/env python3
"""build_bp02_219.py — BP-02 1.3.219 from the frozen 1.3.218 (never rebuilt): THE STREETKIT VILLAGE (D-C529 / D-C530, his
17:00 witness round + 17:27-18:15 rulings). Rebuilt 10-03 evening; the first 219 draft (flush cobble sidewalks) is in
_garbage/bp02-219-draft1-1003 and was never delivered.
  (1) STREETS FROM HIS STREETKIT: structures/pw/road/{v,t}_{straight1,access3,ramp7,dead13,tee13,cross13,elbow13} (tools/
      road_kit.py, snow stripped; village width 5 road + grass verges, town width 7; same tunnels) laid by the clock's
      KIT STREETS (pw_civ_streets.js planner + kit block in pw_civ_clock.js): straight streets, ramps per block of rise,
      dead ends whose sewer runs on to an OUTFALL (stone-brick frame, door-sized space for his grate), plank BRIDGES with
      railing openings, side streets by T junctions, streets that grow, town width at tier town.
  (2) HOUSES FLUSH ON THE STREET at sidewalk height, an access piece in front of each sewer shaft; the shaft's street-side
      opening now reaches down to the gallery floor (local x0, y3-y4 opened) in every template and stage.
  (3) DOUBLE DOORS: every pair of side-by-side doors facing the same way hinges on opposite sides (both leaves had
      door_hinge_bit 0; the +z leaf of each pair -> 1, both halves), in every template AND every stage file.
  (4) KEEPERS + COIN SHOP (pw_civ_shop.js): one named keeper per shop at its station in work hours; talking opens the shop
      window (live town prices, gold coins); the town hall's clerk changes emeralds and coins 1 : 4.
  (5) GOLD COIN (pw_civ_coin.js + items/pw_gold_coin.json + blocks/pw_gold_coin_pile.json): stacks to 64, places as a pile
      (16 coins), coins added by use, every coin back when broken; the mint's ledger (serial ranges per issue).
  (6) The village clears floating leaves daily; a PARK at tier town (young template trees).
Needs RP-04 1.3.157 (the coin's model, textures, icon). Markers BP 0.2.3 hides the zone / station markers."""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402

B = Path("/home/claude/_build")
SRC, DST = B / "bp02-218", B / "bp02-219"
SRC_JS = Path("/home/claude/tools/bp02_src")
KIT = Path("/home/claude/_docs/road_kit")
NEW_SCRIPTS = ["pw_civ_clock.js", "pw_civ_streets.js", "pw_civ_coin.js", "pw_civ_shop.js", "pw_civ_parktrees.js", "pw_civ_economy.js", "pw_civ_people.js", "pw_civ_walk.js", "pw_civ_work.js", "pw_civ_keys.js", "pw_civ_watch.js"]
REFRESH = ["mvv_well_a_r1", "mvv_manor_a_r1"]                      # D-C533: the well's deep shaft


def replace_once(text, old, new, what):
    if text.count(old) != 1:
        raise SystemExit(f"{what}: expected 1 match, found {text.count(old)}")
    return text.replace(old, new)


def shaft_of(path):
    """the sewer shaft's z in a building TEMPLATE: the ladder at x 1, y 3 (None when the building has no cellar)"""
    st = M.Structure.from_bytes(path.read_bytes())
    for z in range(st.size[2]):
        p = st.get(1, 3, z)
        if p and p[0] == "minecraft:ladder":
            return z
    return None


def fix_structure(path, report, shaft_z=None):
    """double doors + the sewer port, in one pass over a building file; returns True when the file changed. The port
    is opened wherever the file holds a solid block at the template's shaft column (x 0, y 3-4): in the stages that is
    the plot stage s0 (the ladder itself arrives with s2; later stages leave those cells void)."""
    st = M.Structure.from_bytes(path.read_bytes())
    sx, sy, sz = st.size
    changed = False
    # (3) doors: z-adjacent, same facing, both hinge 0 -> the +z leaf (both halves) hinge 1
    doors = {}
    for idx, pi in enumerate(st.layer0):
        if pi < 0:
            continue
        n, states, ver = st.palette[pi]
        if n.endswith("_door") and "trap" not in n:
            doors[(idx // (sy * sz), (idx // sz) % sy, idx % sz)] = pi
    for (x, y, z), pi in list(doors.items()):
        n, states, ver = st.palette[pi]
        q = (x, y, z + 1)
        if q not in doors:
            continue
        n2, s2, v2 = st.palette[doors[q]]
        if n2 != n or s2.get("minecraft:cardinal_direction").value != states.get("minecraft:cardinal_direction").value:
            continue
        if states.get("door_hinge_bit").value != 0 or s2.get("door_hinge_bit").value != 0:
            continue
        ns = dict(s2)
        ns["door_hinge_bit"] = M.Tag(M.BYTE, 1)
        st.layer0[st.index(*q)] = st._pal(n2, ns, v2)
        report["door_cells"] += 1
        changed = True
    # (2) sewer port: the shaft is the ladder column at x 1 from y 3; the street face (x 0) at y 3, y 4 opened to air
    for z in ([shaft_z] if shaft_z is not None else []):
        for y in (3, 4):
            q = st.get(0, y, z)
            if q and q[0] in ("minecraft:dirt", "minecraft:smooth_stone", "minecraft:stone_bricks", "minecraft:cobblestone", "minecraft:stone"):
                st.set(0, y, z, "minecraft:air", {})
                report["port_cells"] += 1
                changed = True
    if changed:
        path.write_bytes(st.to_bytes())
    return changed


def coin_defs(dst):
    (dst / "items/pw_gold_coin.json").write_text(json.dumps({
        "format_version": "1.21.30",
        "minecraft:item": {
            # review 19:1x: not in the creative menu — every coin comes from the mint (logged); /scriptevent pw:clock coins give N for tests
            "description": {"identifier": "pw:gold_coin", "menu_category": {"category": "none"}},
            "components": {
                "minecraft:icon": {"textures": {"default": "pw_gold_coin"}},
                "minecraft:max_stack_size": 64,
                "minecraft:display_name": {"value": "item.pw:gold_coin.name"},
                "minecraft:block_placer": {"block": "pw:gold_coin_pile"},
            }}}, indent=1))
    vis = {f"c{k}": f"q.block_state('pw:count') >= {k}" for k in range(1, 17)}
    (dst / "blocks/pw_gold_coin_pile.json").write_text(json.dumps({
        "format_version": "1.21.80",
        "minecraft:block": {
            "description": {"identifier": "pw:gold_coin_pile", "menu_category": {"category": "none"},
                            "states": {"pw:count": list(range(1, 17))}},
            "components": {
                "minecraft:geometry": {"identifier": "geometry.pw_gold_coin_pile", "bone_visibility": vis},
                "minecraft:material_instances": {"*": {"texture": "pw_gold_coin_pile", "render_method": "alpha_test"}},
                "minecraft:collision_box": {"origin": [-7, 0, -7], "size": [14, 4, 14]},
                "minecraft:selection_box": {"origin": [-7, 0, -7], "size": [14, 4, 14]},
                "minecraft:light_dampening": 0,
                "minecraft:destructible_by_mining": {"seconds_to_destroy": 0.3},
                "minecraft:destructible_by_explosion": {"explosion_resistance": 1},
                "minecraft:loot": "loot_tables/blocks/pw_gold_coin_pile.json",
                "minecraft:display_name": "tile.pw:gold_coin_pile.name",
                "minecraft:map_color": "#d4a020",
            }}}, indent=1))
    (dst / "loot_tables/blocks").mkdir(parents=True, exist_ok=True)
    (dst / "loot_tables/blocks/pw_gold_coin_pile.json").write_text(json.dumps({"pools": []}, indent=1))   # the script gives the coins back


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    shutil.copytree(SRC, DST)
    # scripts
    for f in NEW_SCRIPTS:
        shutil.copy(SRC_JS / f, DST / "scripts" / f)
    # D-C534 §4: the building table with every stage's bill of materials (from the staged templates)
    import subprocess
    subprocess.run(["python3", "/home/claude/tools/civ_village_data.py", str(DST / "scripts/pw_civ_buildings.js")], check=True)
    # G (D-C543): the mob scale + damage pass (giants 2.5 x their base; small hostiles hit <= 2, half as often)
    import subprocess as _sp
    _sp.run(["python3", "/home/claude/tools/mob_scale_pass.py", str(DST / "entities"), "/home/claude/_docs/mobs/MOB-PASS-G.json", "/home/claude/_docs/mobs/MOB-PASS-G.md"], check=True)
    # C2.1 (D-C541/542): the vanilla villager with the "follow the lead" group, and the lead entity itself
    C2 = Path("/home/claude/_staging/c2")
    shutil.copy(C2 / "villager_v2.json", DST / "entities/villager_v2.json")
    shutil.copy(C2 / "pw_lead.json", DST / "entities/pw_lead.json")
    # 0.0.26 (run 0.0.24: walkers 16-33 blocks from their own leads — follow_mob took ANY pw_lead within 48): each walker
    # follows only its own lead. The lead carries an int property pw:slot (0..47, default 63 = nobody's); the villager has
    # one follow group per slot (filter: other's pw:slot == k) and pw:lead_on_<k> events; pw:lead_off removes them all.
    import json as _json
    LEAD_SLOTS = 48
    vp = DST / "entities/villager_v2.json"
    vj = _json.loads(vp.read_text())
    ent = vj["minecraft:entity"]
    base = ent["component_groups"]["pw:lead"]
    names = [f"pw:lead_{k}" for k in range(LEAD_SLOTS)]
    for k in range(LEAD_SLOTS):
        g = _json.loads(_json.dumps(base))
        g["minecraft:behavior.follow_mob"]["filters"] = {"all_of": [
            {"test": "is_family", "subject": "other", "value": "pw_lead"},
            {"test": "int_property", "subject": "other", "domain": "pw:slot", "operator": "==", "value": k}]}
        ent["component_groups"][names[k]] = g
        ent["events"][f"pw:lead_on_{k}"] = {"remove": {"component_groups": ["pw:lead"] + [n for j, n in enumerate(names) if j != k]},
                                             "add": {"component_groups": [names[k]]}}
    ent["events"]["pw:lead_off"] = {"remove": {"component_groups": ["pw:lead"] + names}}
    vp.write_text(_json.dumps(vj, indent=1))
    lp = DST / "entities/pw_lead.json"
    lj = _json.loads(lp.read_text())
    lj["minecraft:entity"]["description"]["properties"] = {"pw:slot": {"type": "int", "range": [0, 63], "default": 63, "client_sync": False}}
    lp.write_text(_json.dumps(lj, indent=1))
    print(f"lead slots: {LEAD_SLOTS} follow groups on villager_v2, pw:slot on pw:lead")
    # F4: the sewer key (an item only; no recipe — the register mints it)
    shutil.copy(C2 / "keys/pw_sewer_key.item.json", DST / "items/pw_sewer_key.json")
    # the road kit
    (DST / "structures/pw/road").mkdir(parents=True, exist_ok=True)
    kit = sorted(KIT.glob("*.mcstructure"))
    if len(kit) != 14:
        raise SystemExit(f"road kit: {len(kit)} pieces, expected 14")
    for p in kit:
        shutil.copy(p, DST / "structures/pw/road" / p.name)
    # D-C533: roster buildings regenerated this round (template + 5 stages from _staging) replace the copied ones
    STAGING = Path("/home/claude/_staging/civ")
    for stem in REFRESH:
        shutil.copy(STAGING / "structures/pw" / f"{stem}.mcstructure", DST / "structures/pw" / f"{stem}.mcstructure")
        for k in range(5):
            shutil.copy(STAGING / "stages" / f"{stem}_s{k}.mcstructure", DST / "structures/pw/stages" / f"{stem}_s{k}.mcstructure")
    print("refreshed:", REFRESH)
    # buildings: doors + sewer ports, templates and every stage
    report = {"files": 0, "door_cells": 0, "port_cells": 0}
    files = sorted((DST / "structures/pw").glob("mvv_*.mcstructure")) + sorted((DST / "structures/pw/stages").glob("*.mcstructure"))
    shafts = {p.stem: shaft_of(p) for p in sorted((DST / "structures/pw").glob("mvv_*.mcstructure"))}
    for p in files:
        stem = p.stem.rsplit("_s", 1)[0] if p.parent.name == "stages" else p.stem
        if fix_structure(p, report, shafts.get(stem)):
            report["files"] += 1
    print("buildings:", report)
    if report["door_cells"] < 20:
        raise SystemExit(f"expected the 5 double doors in templates + stages (>= 20 leaf cells), got {report['door_cells']}")
    # the coin
    coin_defs(DST)
    # version markers
    mj = DST / "scripts/main.js"
    mj.write_text(replace_once(mj.read_text(), 'const PW_BUILD = "1.3.218";', 'const PW_BUILD = "1.3.219";', "PW_BUILD"))
    cp = DST / "scripts/pw_companion.js"
    cp.write_text(replace_once(cp.read_text(), "companion v7 LOADED (pack v1.3.218 ", "companion v7 LOADED (pack v1.3.219 ", "C2 label"))
    m = json.loads((DST / "manifest.json").read_text())
    m["header"]["version"] = [1, 3, 219]
    for mod in m["modules"]:
        mod["version"] = [1, 3, 219]
    m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.219"
    desc = m["header"]["description"]
    if not desc.startswith("v1.3.218 (2026-10-03) "):
        raise SystemExit("description prefix")
    m["header"]["description"] = ("v1.3.219 (2026-10-03) STREETKIT VILLAGE: streets from your StreetKit pieces (ramps, sewer outfalls, bridges, "
                                  "side streets, town width at town), flush houses, double doors, shopkeepers + coin shop, gold coins, "
                                  "leaf clearing, park (needs RP-04 1.3.157). Includes all of " + desc)[:1000]
    (DST / "manifest.json").write_text(json.dumps(m, indent=1))
    dep = DST / "PW-DEPENDENCIES.md"
    dep.write_text(replace_once(dep.read_text(), "v1.3.218 (trees re-proportioned,",
                                "v1.3.219 (StreetKit village, gold coin + pile need RP-04 1.3.157; trees re-proportioned,", "deps"))
    print(f"DONE {DST}")


if __name__ == "__main__":
    main()
