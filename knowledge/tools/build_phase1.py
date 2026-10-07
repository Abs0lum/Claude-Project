#!/usr/bin/env python3
"""build_phase1.py — PHASE 1 of the texture-name audit (rulings 2026-09-22 14:37: go; keep dead weight; chest single -> E2).

Every fix here is a NAME fix: the HD art already exists in the stack (or in the Patrix zip) under Java's file name,
and the engine looks for Bedrock's name (L-ICON-1, the classic-door lesson, generalised).  The Java-named originals
are KEPT (ruling b: purge only after witness).

Packs:  RP-03 v1.3.56 -> .57 (52 block twins + companions, 6 Patrix-zip pulls)
        RP-01 v1.3.102 -> .103 (7 twins)      RP-05 v1.3.46 -> .47 (2 twins, one derived opaque)
        RP-04 v1.3.132 -> .133 (signs 12 + hanging 12, boats 10, chest boats 10, shulker silver + undyed, chest copper_default)
Companions: <stem>.texture_set.json (references rewritten), <stem>_mer.png, <stem>_n.png / _normal.png / _heightmap.png.
Transforms: copy · mirror (stonecutter_other_side: colour+mer flipped, normal flipped with R inverted) · opaque_fill
(leaves_big_oak_opaque: transparent texels filled with the mean opaque colour, per 16-px-grid frame).
"""
import json, re, shutil, sys, datetime
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path("/home/claude"); SRC = ROOT / "_build/src"; DATE = "2026-09-22"
LOG = ROOT / "_logs/phase_log.md"
def log(m): LOG.open("a").write(f"[{datetime.datetime.now().strftime('%H:%M')} CT 09-22] BUILD PHASE1 — {m}\n")
def jload(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def jdump(o, p): Path(p).write_text(json.dumps(o, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

PACKS = {  # tag: (source tree, dest tree, new version, name template)
    "RP-03": (SRC / "RP-03-v1_3_56", ROOT / "_build/rp03-57", (1, 3, 57), "AbsolutRealism PBR RP v{v}"),
    "RP-01": (SRC / "RP-01-v1_3_102", ROOT / "_build/rp01-103", (1, 3, 103), "AbsolutRealism Tectonic RP v{v}"),
    "RP-05": (SRC / "RP-05-v1_3_46", ROOT / "_build/rp05-47", (1, 3, 47), "AbsolutRealism Flora RP v{v}"),
    "RP-04": (ROOT / "_build/rp04-132", ROOT / "_build/rp04-133", (1, 3, 133), "AbsolutRealism Basic RP v{v}"),
}
# ---- block twins: (dest pack, bedrock stem, source pack, java stem, transform)
B = "textures/blocks/"
BLOCK_MAP = [
    ("RP-03", "furnace_front_off", "RP-03", "furnace_front", "copy"), ("RP-03", "blast_furnace_front_off", "RP-03", "blast_furnace_front", "copy"), ("RP-03", "smoker_front_off", "RP-03", "smoker_front", "copy"),
    ("RP-03", "dispenser_front_horizontal", "RP-03", "dispenser_front", "copy"), ("RP-03", "dropper_front_horizontal", "RP-03", "dropper_front", "copy"),
    ("RP-03", "repeater_off", "RP-03", "repeater", "copy"), ("RP-03", "comparator_off", "RP-03", "comparator", "copy"), ("RP-03", "observer_back_lit", "RP-03", "observer_back_on", "copy"),
    ("RP-03", "pumpkin_face_on", "RP-03", "jack_o_lantern", "copy"), ("RP-03", "door_iron_lower", "RP-03", "iron_door_bottom", "copy"), ("RP-03", "door_iron_upper", "RP-03", "iron_door_top", "copy"),
    ("RP-03", "sandstone_normal", "RP-03", "sandstone", "copy"), ("RP-03", "sandstone_smooth", "RP-03", "cut_sandstone", "copy"),
    ("RP-03", "red_sandstone_normal", "RP-03", "red_sandstone", "copy"), ("RP-03", "red_sandstone_smooth", "RP-03", "cut_red_sandstone", "copy"), ("RP-03", "red_sandstone_carved", "RP-03", "chiseled_red_sandstone", "copy"),
    ("RP-03", "stone_slab_top", "RP-03", "smooth_stone", "copy"), ("RP-03", "stone_slab_side", "RP-03", "smooth_stone_slab_side", "copy"),
    ("RP-03", "stone_andesite", "RP-03", "andesite", "copy"), ("RP-03", "stone_andesite_smooth", "RP-03", "polished_andesite", "copy"),
    ("RP-03", "stone_granite", "RP-03", "granite", "copy"), ("RP-03", "stone_granite_smooth", "RP-03", "polished_granite", "copy"), ("RP-03", "stone_diorite_smooth", "RP-03", "polished_diorite", "copy"),
    ("RP-03", "stonebrick_carved", "RP-03", "chiseled_stone_bricks", "copy"), ("RP-03", "stonebrick_cracked", "RP-03", "cracked_stone_bricks", "copy"), ("RP-03", "stonebrick_mossy", "RP-03", "mossy_stone_bricks", "copy"),
    ("RP-03", "brick", "RP-03", "bricks", "copy"), ("RP-03", "nether_brick", "RP-03", "nether_bricks", "copy"), ("RP-03", "red_nether_brick", "RP-03", "red_nether_bricks", "copy"), ("RP-03", "end_bricks", "RP-03", "end_stone_bricks", "copy"),
    ("RP-03", "prismarine_dark", "RP-03", "dark_prismarine", "copy"), ("RP-03", "prismarine_rough", "RP-03", "prismarine", "copy"),
    ("RP-03", "trip_wire", "RP-03", "tripwire", "copy"), ("RP-03", "trip_wire_source", "RP-03", "tripwire_hook", "copy"),
    ("RP-03", "fletcher_table_side1", "RP-03", "fletching_table_front", "copy"), ("RP-03", "fletcher_table_side2", "RP-03", "fletching_table_side", "copy"), ("RP-03", "fletcher_table_top", "RP-03", "fletching_table_top", "copy"),
    ("RP-03", "stonecutter_other_side", "RP-03", "stonecutter_side", "mirror"),
    ("RP-03", "endframe_side", "RP-03", "end_portal_frame_side", "copy"), ("RP-03", "endframe_top", "RP-03", "end_portal_frame_top", "copy"),
    ("RP-03", "lightning_rod_powered", "RP-03", "lightning_rod_on", "copy"), ("RP-03", "beehive_top", "RP-03", "beehive_end", "copy"), ("RP-03", "turtle_egg_not_cracked", "RP-03", "turtle_egg", "copy"),
    ("RP-03", "dried_kelp_side_a", "RP-03", "dried_kelp_side", "copy"), ("RP-03", "dried_kelp_side_b", "RP-03", "dried_kelp_side", "copy"),
    ("RP-03", "stripped_cherry_log_side", "RP-03", "stripped_cherry_log", "copy"), ("RP-03", "stripped_mangrove_log_side", "RP-03", "stripped_mangrove_log", "copy"), ("RP-03", "stripped_pale_oak_log_side", "RP-03", "stripped_pale_oak_log", "copy"),
    ("RP-03", "huge_fungus/stripped_crimson_stem_side", "RP-03", "stripped_crimson_stem", "copy"), ("RP-03", "huge_fungus/stripped_warped_stem_side", "RP-03", "stripped_warped_stem", "copy"), ("RP-03", "huge_fungus/warped_stem_side", "RP-03", "warped_stem", "copy"),
    ("RP-01", "bamboo_stem", "RP-01", "bamboo_stalk", "copy"), ("RP-01", "big_dripleaf_side1", "RP-01", "big_dripleaf_side", "copy"), ("RP-01", "big_dripleaf_side2", "RP-01", "big_dripleaf_side", "copy"),
    ("RP-01", "mushroom_block_skin_brown", "RP-01", "brown_mushroom_block", "copy"), ("RP-01", "mushroom_block_skin_red", "RP-01", "red_mushroom_block", "copy"), ("RP-01", "pale_oak_log_side", "RP-01", "pale_oak_log", "copy"),
    ("RP-01", "twisting_vines_base", "RP-01", "twisting_vines_plant", "copy"), ("RP-01", "weeping_vines_base", "RP-01", "weeping_vines_plant", "copy"),
    ("RP-05", "bamboo_small_leaf", "RP-05", "bamboo_small_leaves", "copy"), ("RP-05", "leaves_big_oak_opaque", "RP-05", "leaves_big_oak", "opaque_fill"),
]
# Patrix-zip pulls (colour only; LabPBR _n/_s not converted here) and RP-02's animated water as the cauldron water
ZIP = ROOT / "_intake/patrix128/assets/minecraft/textures/block"
PULLS = [("creaking_heart_side_dormant", "creaking_heart"), ("jigsaw_front", "jigsaw_top"), ("jigsaw_back", "jigsaw_bottom"), ("scaffolding_bottom", "scaffolding_bottom"), ("structure_block_export", "structure_block_save"), ("sculk_catalyst_top", "sculk_catalyst_top")]
# ---- entity renames in RP-04 (source path -> dest path, both under textures/entity/)
SIGNS = {"oak": "sign", "spruce": "sign_spruce", "birch": "sign_birch", "jungle": "sign_jungle", "acacia": "sign_acacia", "dark_oak": "sign_darkoak", "crimson": "sign_crimson", "warped": "sign_warped",
         "bamboo": "bamboo_sign", "cherry": "cherry_sign", "mangrove": "mangrove_sign", "pale_oak": "pale_oak_sign"}
BOATS = {"oak": "boat_oak", "spruce": "boat_spruce", "birch": "boat_birch", "jungle": "boat_jungle", "acacia": "boat_acacia", "dark_oak": "boat_darkoak", "cherry": "cherry_boat", "mangrove": "mangrove_boat", "pale_oak": "pale_oak_boat", "bamboo": "bamboo_raft"}
CHEST_BOATS = {w: f"chest_boat_{'darkoak' if w == 'dark_oak' else w}" for w in ("oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "cherry", "mangrove", "pale_oak", "bamboo")}
ENTITY_MAP = [(f"signs/{w}.png", f"{b}.png") for w, b in SIGNS.items()] + [(f"signs/hanging/{w}.png", f"{w}_hanging_sign.png") for w in SIGNS] \
    + [(f"boat/{w}.png", f"boat/{b}.png") for w, b in BOATS.items()] + [(f"chest_boat/{w}.png", f"boat/{b}.png") for w, b in CHEST_BOATS.items()] \
    + [("shulker/shulker_light_gray.png", "shulker/shulker_silver.png"), ("chest/copper.png", "chest/copper_default.png")]
ENTITY_PULLS = [(ROOT / "_intake/patrix128/assets/minecraft/textures/entity/shulker/shulker.png", "shulker/shulker_undyed.png")]

COMPANIONS = ("_mer", "_n", "_normal", "_heightmap")
COMP_RE = re.compile(r"(_mer|_n|_normal|_heightmap)$")

def mirror_png(src, dst, is_normal=False):
    im = Image.open(src).convert("RGBA"); im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if is_normal:
        a = np.array(im); a[..., 0] = 255 - a[..., 0]; im = Image.fromarray(a)
    im.save(dst)

def opaque_fill(src, dst):
    im = Image.open(src).convert("RGBA"); a = np.array(im)
    fr = a.shape[1]                                     # square frames stacked vertically (strip-safe)
    for y0 in range(0, a.shape[0], fr):
        f = a[y0:y0 + fr]; m = f[..., 3] > 0
        fill = f[..., :3][m].mean(axis=0) if m.any() else np.array([40, 60, 20])
        f[..., :3][~m] = fill.astype(np.uint8); f[..., 3] = 255
    Image.fromarray(a).save(dst)

def copy_with_companions(src_dir, java, dst_dir, bedrock, transform, manifest):
    """copy <java>.png -> <bedrock>.png (+ transform) and its PBR companions; texture-set references are written as
    bare stems relative to the destination folder (bedrock may carry a sub-folder, e.g. huge_fungus/...)."""
    sp = src_dir / f"{java}.png"; dp = dst_dir / f"{bedrock}.png"; dp.parent.mkdir(parents=True, exist_ok=True)
    assert sp.exists(), sp
    if transform == "copy": shutil.copy(sp, dp)
    elif transform == "mirror": mirror_png(sp, dp)
    elif transform == "opaque_fill": opaque_fill(sp, dp)
    bname = Path(bedrock).name; written = [dp]
    def put(csrc, suffix):
        cdst = dp.parent / f"{bname}{suffix}.png"
        if transform == "mirror": mirror_png(csrc, cdst, is_normal=(suffix in ("_n", "_normal")))
        else: shutil.copy(csrc, cdst)
        written.append(cdst); return f"{bname}{suffix}"
    ts = src_dir / f"{java}.texture_set.json"
    if ts.exists():
        d = jload(ts); t = d["minecraft:texture_set"]
        for k, v in list(t.items()):
            if not isinstance(v, str): continue                      # inline colour arrays etc.
            if k == "color": t[k] = bname; continue
            m = COMP_RE.search(v); suffix = m.group(1) if m else ""
            own = src_dir / f"{java}{suffix}.png"; ref = src_dir / f"{v}.png"
            if suffix and own.exists(): t[k] = put(own, suffix)          # the twin's own companion (fixes cross-references)
            elif ref.exists(): t[k] = put(ref, suffix or f"_{k[:3]}")
            else: del t[k]
        jdump(d, dp.parent / f"{bname}.texture_set.json"); written.append(dp.parent / f"{bname}.texture_set.json")
    else:
        for suf in COMPANIONS:                                        # companions without a texture set (RP-01/05 style)
            csrc = src_dir / f"{java}{suf}.png"
            if csrc.exists(): put(csrc, suf)
    return written

def stamp(tag, dst, headline):
    s, d, ver, name = PACKS[tag]; v = ".".join(map(str, ver))
    man = jload(dst / "manifest.json")
    man["header"]["name"] = name.format(v=v); man["header"]["version"] = list(ver)
    for m in man["modules"]: m["version"] = list(ver)
    man["header"]["description"] = f"v{v} ({DATE}) {headline}"
    jdump(man, dst / "manifest.json")
    led = dst / "PW-DEPENDENCIES.md"
    if led.exists():
        t = led.read_text(encoding="utf-8"); old = ".".join(map(str, jload(s / "manifest.json")["header"]["version"]))
        t2 = t.replace(f"v{old} ·", f"v{v} ·", 1)
        if t2 != t: led.write_text(t2, encoding="utf-8")

def main():
    added = {tag: [] for tag in PACKS}
    for tag, (s, d, ver, name) in PACKS.items():
        if d.exists(): shutil.rmtree(d)
        shutil.copytree(s, d)
    for tag, bstem, stag, jstem, tr in BLOCK_MAP:
        d = PACKS[tag][1] / "textures/blocks"; sdir = PACKS[stag][0] / "textures/blocks"
        added[tag] += [str(p.relative_to(PACKS[tag][1])) for p in copy_with_companions(sdir, jstem, d, bstem, tr, [])]
    d3 = PACKS["RP-03"][1] / "textures/blocks"
    for bstem, jstem in PULLS:
        shutil.copy(ZIP / f"{jstem}.png", d3 / f"{bstem}.png"); added["RP-03"].append(f"textures/blocks/{bstem}.png")
    # cauldron_water: RP-02's water is vanilla-res (16x512), so an alias would gain nothing — left to vanilla (noted).
    # entities
    d4 = PACKS["RP-04"][1] / "textures/entity"; s4 = PACKS["RP-04"][0] / "textures/entity"
    for src, dst in ENTITY_MAP:
        (d4 / dst).parent.mkdir(parents=True, exist_ok=True); shutil.copy(s4 / src, d4 / dst); added["RP-04"].append(f"textures/entity/{dst}")
    for src, dst in ENTITY_PULLS:
        shutil.copy(src, d4 / dst); added["RP-04"].append(f"textures/entity/{dst}")
    stamp("RP-03", PACKS["RP-03"][1], "NAME AUDIT phase 1 — 52 block textures that existed only under Java's file name now also carry Bedrock's (furnace/blast/smoker OFF fronts, repeater/comparator off, dispenser/dropper fronts, observer back lit, jack-o-lantern, iron door, sandstone/red sandstone/smooth stone/andesite/granite/diorite faces, chiseled/cracked/mossy stone bricks, bricks/nether/red nether/end bricks, prismarine, tripwire, fletching table, stonecutter, end frame, lightning rod, beehive end, turtle egg, kelp, stripped log sides, fungus stems) with their texture sets + MER + normals; 6 Patrix pulls (creaking heart, jigsaw, scaffolding bottom, structure block, sculk catalyst top). Java-named originals kept until witnessed. Vanilla 1.26.50 file list is the name oracle.")
    stamp("RP-01", PACKS["RP-01"][1], "NAME AUDIT phase 1 — 8 block textures re-bound under Bedrock's names (bamboo_stem, big_dripleaf_side1/2, mushroom_block_skin_brown/red, pale_oak_log_side, twisting/weeping_vines_base). Originals kept.")
    stamp("RP-05", PACKS["RP-05"][1], "NAME AUDIT phase 1 — bamboo_small_leaf (from bamboo_small_leaves) + leaves_big_oak_opaque (fancy-leaves-off variant derived from leaves_big_oak, transparent texels filled). Originals kept.")
    stamp("RP-04", PACKS["RP-04"][1], "NAME AUDIT phase 1 — the Patrix sign (12), hanging sign (12), boat (10) and chest-boat (10) textures were dead Java paths; now bound under Bedrock's names (sign.png/sign_<wood>/<wood>_sign, <wood>_hanging_sign, boat/boat_<wood>|<wood>_boat|bamboo_raft, boat/chest_boat_<wood>); shulker_silver + shulker_undyed; chest/copper_default. Same-layout families only (screened against vanilla); the re-layout families (armor stand, minecart, book, banner base, end crystal, bell, XP orb, lead knot, conduit, pot, chest single) are phase E2. Java-named originals kept until witnessed. Pair with BP-02 v1.3.182 + RP-02 v2.0.3.")
    jdump(added, ROOT / "_logs/phase1_added.json")
    log("trees built: rp03-57 (+%d files), rp01-103 (+%d), rp05-47 (+%d), rp04-133 (+%d); manifests stamped" % tuple(len(added[t]) for t in ("RP-03", "RP-01", "RP-05", "RP-04")))

if __name__ == "__main__":
    main()
