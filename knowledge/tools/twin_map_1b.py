#!/usr/bin/env python3
"""twin_map_1b.py — phase 1b: the curated Java->Bedrock name map for every vanilla-resolved block texture slot.

Input : _logs/block_census_e2.json (slots resolving to VANILLA), the four build trees (every texture file, referenced or
        not — the v1 scan wrongly skipped referenced twins such as white_wool / quartz_pillar), the Patrix 128x listing.
Rules : hand-curated Bedrock -> Java name table (colour families, silver->light_gray, rails, anvil, quartz, stems, crops,
        huge_fungus/, deepslate/, candles/, campfire, misc) + DERIVE families handled by build code (shulker tops, chest
        inventory icons, dried ghast faces) + LEGACY/TECHNICAL block tagging (deprecated flattened ids never placed in a
        modern world — wool/concrete/stained_glass/... legacy entries, command blocks, border/allow/deny, ...).
Output: _logs/twin_map_1b.json  — per slot: action RENAME (source pack + Java stem) / PULL (Patrix zip path) / DERIVE /
        LEGACY / NO-ART (-> the sourcing list), plus the blocks using it.
"""
import json, re, collections
from pathlib import Path
ROOT = Path("/home/claude")
TREES = {"RP-03": ROOT / "_build/rp03-58", "RP-04": ROOT / "_build/rp04-135", "RP-01": ROOT / "_build/rp01-103", "RP-05": ROOT / "_build/rp05-47"}
PREF = ["RP-03", "RP-04", "RP-01", "RP-05"]          # source preference: the PBR pack first (texture sets ride along)
COLOURS = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", "silver", "cyan", "purple", "blue", "brown", "green", "red", "black"]
JCOL = {c: ("light_gray" if c == "silver" else c) for c in COLOURS}
CORAL = {"blue": "tube", "pink": "brain", "purple": "bubble", "red": "fire", "yellow": "horn"}

LEGACY_BLOCKS = {  # deprecated ids kept in blocks.json for old worlds / never placeable now (flattened successors are censused separately)
    "wool", "carpet", "concrete", "concretePowder", "stained_glass", "stained_glass_pane", "stained_hardened_clay", "shulker_box",
    "coral_block", "coral", "coral_fan", "coral_fan_dead", "coral_fan_hang", "coral_fan_hang2", "coral_fan_hang3", "sapling", "stonecutter",
    "deprecated_anvil", "log", "log2", "leaves", "leaves2", "planks", "wood", "stone", "stonebrick", "double_plant", "tallgrass", "red_flower",
    "yellow_flower", "monster_egg", "hard_stained_glass", "hard_stained_glass_pane", "colored_torch_bp", "colored_torch_rg"}
TECHNICAL_BLOCKS = {"allow", "deny", "border_block", "camera", "movingBlock", "reserved6", "info_update", "info_update2", "netherreactor",
                    "glowingobsidian", "structure_void", "barrier", "command_block", "chain_command_block", "repeating_command_block",
                    "end_gateway", "end_portal", "bubble_column", "invisible_bedrock", "unknown", "client_request_placeholder_block",
                    "structure_block", "jigsaw", "light_block"}

def java_names(stem):
    """Bedrock block stem -> list of Java stems to try (most specific first)."""
    s = stem; out = []
    m = re.fullmatch(r"glass_(\w+)", s)
    if m and m.group(1) in COLOURS: out.append(f"{JCOL[m.group(1)]}_stained_glass")
    m = re.fullmatch(r"glass_pane_top_(\w+)", s)
    if m and m.group(1) in COLOURS: out.append(f"{JCOL[m.group(1)]}_stained_glass_pane_top")
    m = re.fullmatch(r"hardened_clay_stained_(\w+)", s)
    if m and m.group(1) in COLOURS: out.append(f"{JCOL[m.group(1)]}_terracotta")
    m = re.fullmatch(r"glazed_terracotta_(\w+)", s)
    if m and m.group(1) in COLOURS: out.append(f"{JCOL[m.group(1)]}_glazed_terracotta")
    m = re.fullmatch(r"concrete_powder_(\w+)", s)
    if m and m.group(1) in COLOURS: out.append(f"{JCOL[m.group(1)]}_concrete_powder")
    m = re.fullmatch(r"concrete_(\w+)", s)
    if m and m.group(1) in COLOURS: out.append(f"{JCOL[m.group(1)]}_concrete")
    m = re.fullmatch(r"wool_colored_(\w+)", s)
    if m and m.group(1) in COLOURS: out.append(f"{JCOL[m.group(1)]}_wool")
    m = re.fullmatch(r"huge_fungus/(crimson|warped)_(.+)", s)
    if m:
        w, part = m.groups()
        part = {"door_lower": "door_bottom", "log_side": "stem", "log_top": "stem_top"}.get(part, part)
        if part.startswith("stripped_"): part = part  # stripped_log_side handled below
        out.append(f"{w}_{part}")
    m = re.fullmatch(r"huge_fungus/stripped_(crimson|warped)_log_(side|top)", s)
    if m: out.append(f"stripped_{m.group(1)}_stem" + ("_top" if m.group(2) == "top" else ""))
    m = re.fullmatch(r"(deepslate|candles)/(.+)", s)
    if m: out.append(m.group(2))
    m = re.fullmatch(r"(\w+)_stage_(\d+)", s)
    if m: out.append(f"{m.group(1)}_stage{m.group(2)}")
    table = {"rail_normal": "rail", "rail_normal_turned": "rail_corner", "rail_golden": "powered_rail", "rail_golden_powered": "powered_rail_on",
             "rail_detector": "detector_rail", "rail_detector_powered": "detector_rail_on", "rail_activator": "activator_rail", "rail_activator_powered": "activator_rail_on",
             "anvil_base": "anvil", "anvil_top_damaged_0": "anvil_top", "anvil_top_damaged_1": "chipped_anvil_top", "anvil_top_damaged_2": "damaged_anvil_top",
             "quartz_block_chiseled": "chiseled_quartz_block", "quartz_block_chiseled_top": "chiseled_quartz_block_top", "quartz_block_lines": "quartz_pillar",
             "quartz_block_lines_top": "quartz_pillar_top", "quartz_ore": "nether_quartz_ore",
             "honey_side": "honey_block_side", "honey_top": "honey_block_top", "honey_bottom": "honey_block_bottom", "honeycomb": "honeycomb_block",
             "slime": "slime_block", "sponge_wet": "wet_sponge", "noteblock": "note_block", "web": "cobweb", "ice_packed": "packed_ice",
             "mob_spawner": "spawner", "redstone_lamp_off": "redstone_lamp", "compost": "composter_compost", "compost_ready": "composter_ready",
             "pumpkin_stem_connected": "attached_pumpkin_stem", "pumpkin_stem_disconnected": "pumpkin_stem",
             "melon_stem_connected": "attached_melon_stem", "melon_stem_disconnected": "melon_stem",
             "campfire": "campfire_fire", "soul_campfire": "soul_campfire_fire",
             "sapling_roofed_oak": "dark_oak_sapling", "eyeblossom_dormant": "closed_eyeblossom", "eyeblossom_open": "open_eyeblossom",
             "stonecutter2_bottom": "stonecutter_bottom", "stonecutter2_saw": "stonecutter_saw", "stonecutter2_side": "stonecutter_side", "stonecutter2_top": "stonecutter_top",
             "itemframe_background": "item_frame", "resin_clump": "resin_clump", "bamboo_singleleaf": "bamboo_singleleaf"}
    if s in table: out.append(table[s])
    m = re.fullmatch(r"sapling_(\w+)", s)
    if m and m.group(1) != "roofed_oak": out.append(f"{m.group(1)}_sapling")
    m = re.fullmatch(r"coral_(fan_|plant_)?(blue|pink|purple|red|yellow)(_dead)?", s)
    if m:
        kind, col, dead = m.groups(); jn = CORAL[col]
        base = {"fan_": f"{jn}_coral_fan", "plant_": f"{jn}_coral", None: f"{jn}_coral_block"}[kind]
        out.append(("dead_" if dead else "") + base)
    out.append(s)                                             # exact same name (absent from the stack, maybe in the Patrix zip)
    return list(dict.fromkeys(out))

DERIVE = {re.compile(r"^shulker_top_(\w+)$"): "SHULKER-TOP", re.compile(r"^(chest|trapped_chest|ender_chest)_(front|side|top)$"): "CHEST-ICON",
          re.compile(r"^(copper|exposed_copper|oxidized_copper|weathered_copper)_chest_inventory_(front|side|top)$"): "CHEST-ICON",
          re.compile(r"^dried_ghast_state_(\d)_(\w+)$"): "DRIED-GHAST"}

def main(census=ROOT / "_logs/block_census_e2.json", out=ROOT / "_logs/twin_map_1b.json"):
    c = json.loads(Path(census).read_text()); blocks = c["blocks"]
    slots = collections.defaultdict(set)
    for blk, v in blocks.items():
        for s in v["slots"]:
            if s["provider"] == "VANILLA": slots[s["path"]].add(blk)
    # every texture stem in the trees (referenced or not)
    have = {}
    for tag in PREF:
        root = TREES[tag]
        for p in root.rglob("*"):
            if p.is_file() and p.suffix.lower() in (".png", ".tga", ".jpg"):
                rel = str(p.relative_to(root)).rsplit(".", 1)[0]
                if rel.startswith("textures/blocks/"): have.setdefault(rel[len("textures/blocks/"):], []).append(tag)
    patrix = set()
    for l in (ROOT / "_intake/patrix128/listing.txt").read_text().split("\n"):
        if l.strip() and not l.startswith("#"):
            q = l.split(None, 1)[1].strip()
            if q.startswith("assets/minecraft/textures/block/") and q.endswith(".png"): patrix.add(q[len("assets/minecraft/textures/block/"):-4])
    table = {}
    for path, blks in sorted(slots.items()):
        stem = path[len("textures/blocks/"):] if path.startswith("textures/blocks/") else path
        live_blocks = sorted(b for b in blks if b not in LEGACY_BLOCKS and b not in TECHNICAL_BLOCKS)
        tag = "LEGACY" if not live_blocks and all(b in LEGACY_BLOCKS for b in blks) else ("TECHNICAL" if not live_blocks else "CURRENT")
        row = {"blocks": sorted(blks), "live_blocks": live_blocks, "tag": tag, "action": None}
        for rx, fam in DERIVE.items():
            if rx.match(stem): row["action"] = "DERIVE"; row["family"] = fam
        if row["action"] is None:
            for jn in java_names(stem):
                if jn in have:
                    src = sorted(have[jn], key=PREF.index)[0]
                    row.update(action="RENAME", java=jn, source=src, also_in=sorted(have[jn])); break
                if jn in patrix:
                    row.update(action="PULL", java=jn, patrix=f"assets/minecraft/textures/block/{jn}.png"); break
        if row["action"] is None: row["action"] = "NO-ART"; row["tried"] = java_names(stem)
        table[path] = row
    Path(out).write_text(json.dumps(table, indent=1))
    cnt = collections.Counter((r["tag"], r["action"]) for r in table.values())
    print("slots:", len(table)); [print(f"  {k[0]:9s} {k[1]:8s} {v}") for k, v in sorted(cnt.items())]
    return table

if __name__ == "__main__":
    t = main()
    for path, r in sorted(t.items(), key=lambda kv: (kv[1]["tag"], kv[1]["action"], kv[0])):
        if r["tag"] == "CURRENT" or r["action"] in ("RENAME", "PULL"):
            extra = r.get("java", r.get("family", "")); src = r.get("source", r.get("patrix", ""))
            print(f"{r['tag']:9s} {r['action']:7s} {path[16:]:40s} <- {extra:36s} {src:10s} blocks: {', '.join(r['live_blocks'] or r['blocks'])[:70]}")
