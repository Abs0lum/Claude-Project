#!/usr/bin/env python3
"""spiral_pack.py — the SPIRAL STAIRS TEST PACK (his 14:36 "Yes, to all": build the in-game test; materials by abundance
and class/station, my choice). A separate small RP + BP so nothing touches the 1.3.228 gate.

Blocks (block format 1.26.0 — his ruling: the spiral blocks ONLY may leave 1.21.80; 1.26.0 is the first version whose
minecraft:collision_box takes an ARRAY of boxes, up to y 24, released; geometry may still vary per permutation there):
  pw:spiral_stairs_<design>_<palette>     design A_turret | B_tower | C_grand ; palette stone | oak | spruce_plaster
  states  pw:cell  (int: which block of the quarter turn; A 1, B 4, C 8)
          pw:part  start | mid | end           (the foot with its newel post / the flight / the head with its exit)
          pw:hand  ccw | cw                    (WORLD chirality seen from above while climbing)
          minecraft:cardinal_direction         (the quarter: south 0, east 90, north 180, west 270 — the transformation)
  The id keeps "stairs" (pw_civ_walk.js treats it as a half floor).

ENGINE LAWS USED (measured, D-C487 + L-ROT-DIR): geometry and collision boxes are drawn with file x MIRRORED into the
world; minecraft:transformation rotates right-handed in WORLD coords (y: (x, z) -> (x cos b + z sin b, -x sin b + z cos b))
about the block centre. The design frame of spiral_gen is the FILE frame, so a world point = Rw(90 k) . M . design point:
quadrant k uses rotation b = 90 k and its cells land at Rw(90 k) M (cell centre). Design hand "r" (theta +x -> +z in the
file) becomes west -> south in the world = counter-clockwise from above: r = ccw, l = cw.

Test pad (structure pw:spiral_pad; /structure load pw:spiral_pad ~ ~ ~): a smooth-stone floor and six 2-turn stairs in a
row (A stone ccw + cw, B oak ccw + cw, C stone ccw, C spruce_plaster cw), each with its landing BESIDE the well at the
head (his 14:28 headroom law). Placement by structure = no companion needed.

Outputs: _build/spiraltest-0.0.3-bp, _build/spiraltest-0.0.3-rp, _docs/program228/spiral/PALETTE-RULES.md (in the doc).
"""
import json, math, shutil, sys, uuid
from pathlib import Path
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
import spiral_gen as SG  # noqa: E402
import mcstructure as M  # noqa: E402

VER = [0, 0, 3]
BP = Path("/home/claude/_build/spiraltest-0.0.3-bp")
RP = Path("/home/claude/_build/spiraltest-0.0.3-rp")
RP04 = Path("/home/claude/_build/rp04-159/textures/blocks")
UU = {"bp_h": "1ebc0f4c-05d2-4470-b1b4-7f17fb86e33a", "bp_m": "b8f8c647-107f-4dea-b5a5-a00e06dda6b2",
      "rp_h": "cfe82005-7bf3-43a2-89d8-72e837beaffa", "rp_m": "0d3de496-ff6d-4fee-9fda-f655beb1668b"}
FORMAT = "1.26.0"
DIRS = {"south": 0, "east": 90, "north": 180, "west": 270}
DIR_OF_B = {0: "south", 90: "east", 180: "north", 270: "west"}
PARTS = ["start", "mid", "end", "door"]          # door (16:30): a mid-floor exit beside the step
HANDS = {"ccw": "r", "cw": "l"}

# palettes: material instance -> source texture in RP-04 (Patrix-derived); "@r90" = the tile turned 90 deg (boards run
# round the curve on a wooden underside). Choice (his 14:36 delegation: abundance + class/station) is written up in the doc.
PALETTE = {
    "stone": {"tread": "polished_andesite_v0", "soffit": "stone_bricks", "string": "stone_bricks_v1",
              "rail": "stripped_oak_log", "baluster": "stripped_dark_oak_log", "post": "stone_bricks_v2"},
    "oak": {"tread": "oak_planks_v0", "soffit": "oak_planks_v2@r90", "string": "stripped_oak_log",
            "rail": "stripped_dark_oak_log", "baluster": "stripped_oak_log", "post": "stripped_oak_log"},
    "spruce_plaster": {"tread": "spruce_planks_v0", "soffit": "smooth_stone_v1", "string": "stripped_spruce_log",
                       "rail": "stripped_dark_oak_log", "baluster": "stripped_spruce_log", "post": "stripped_spruce_log"},
}
BLOCKS = [("A_turret", "stone"), ("A_turret", "oak"), ("B_tower", "oak"), ("B_tower", "spruce_plaster"), ("B_tower", "stone"),
          ("C_grand", "stone"), ("C_grand", "spruce_plaster"), ("C_grand", "oak")]
PAD = [("A_turret", "stone", "ccw"), ("A_turret", "stone", "cw"), ("B_tower", "oak", "ccw"), ("B_tower", "oak", "cw"),
       ("C_grand", "stone", "ccw"), ("C_grand", "spruce_plaster", "cw")]


def tex_key(pal, inst):
    return f"pw_sp_{pal}_{inst}"


def mer_normal_of(stem):
    """the MER / normal companions RP-04 pairs with a colour texture (from its texture_set), or None."""
    ts = RP04 / f"{stem}.texture_set.json"
    if ts.exists():
        d = json.loads(ts.read_text())["minecraft:texture_set"]
        return d.get("metalness_emissive_roughness_subsurface"), d.get("normal")
    base = stem.split("_v")[0]
    mer, nrm = RP04 / f"{base}_mer.png", RP04 / f"{base}_n.png"
    return (f"{base}_mer" if mer.exists() else None), (f"{base}_n" if nrm.exists() else None)


def write_textures():
    out = RP / "textures/blocks/pw_spiral"
    out.mkdir(parents=True, exist_ok=True)
    data = {}
    for pal, mats in PALETTE.items():
        for inst, src in mats.items():
            rot = 0
            if "@r" in src: src, rot = src.split("@r")[0], int(src.split("@r")[1])
            key = tex_key(pal, inst)
            im = Image.open(RP04 / f"{src}.png").convert("RGBA")
            if im.width != im.height: raise SystemExit(f"{src}: not square (L-ATLAS-SQUARE)")
            if rot: im = im.rotate(-rot, expand=True)
            im.save(out / f"{key}.png")
            mer, nrm = mer_normal_of(src)
            ts = {"color": key}
            if mer and (RP04 / f"{mer}.png").exists():
                m = Image.open(RP04 / f"{mer}.png")
                if rot: m = m.rotate(-rot, expand=True)
                m.save(out / f"{key}_mer.png"); ts["metalness_emissive_roughness_subsurface"] = f"{key}_mer"
            if nrm and (RP04 / f"{nrm}.png").exists() and not rot:   # a turned normal map needs its vectors turned too: left out
                shutil.copy2(RP04 / f"{nrm}.png", out / f"{key}_n.png"); ts["normal"] = f"{key}_n"
            (out / f"{key}.texture_set.json").write_text(json.dumps({"format_version": "1.21.30", "minecraft:texture_set": ts}, indent=1))
            data[key] = {"textures": f"textures/blocks/pw_spiral/{key}"}
    (RP / "textures/terrain_texture.json").write_text(json.dumps({"resource_pack_name": "pw_spiraltest", "texture_name": "atlas.terrain",
                                                                   "padding": 8, "num_mip_levels": 4, "texture_data": data}, indent=1))
    return data


def design_parts(design):
    """geometry docs + per (hand, part, cell) collision for one design."""
    P = SG.DESIGNS[design]
    base = SG.carry_back(SG.carry(SG.build_quadrant(P["r0"], P["r1"])), P["n"])
    geos, col = [], {}
    te = SG.rail_end_theta(base)
    for dh in ("r", "l"):
        for part in PARTS:
            els = SG.variant(base, P["r1"], part)
            if dh == "l": els = SG.mirror(els)
            geos += SG.emit(f"{design}_{dh}_{part}", els, P["n"])["minecraft:geometry"]
            c = SG.collision(P["r0"], P["r1"], P["n"], rail_to=te if part == "end" else (SG.exit_theta(P["r1"]) if part == "door" else None))
            if dh == "l": c = SG.mirror_collision(c)
            col[(dh, part)] = c
    cells = sorted({g["description"]["identifier"][-2:] for g in geos})
    return geos, col, cells


def block_id(design, pal, main=False):
    """the block id; the MAIN packs use lowercase ids (BDS probe 16:22: ids come back lowercased at runtime)"""
    return f"pw:spiral_stairs_{design.lower()}_{pal}" if main else f"pw:spiral_stairs_{design}_{pal}"


def block_json(design, pal, cells, col, geo_ids, main=False):
    ident = block_id(design, pal, main)
    mats = {inst: {"texture": tex_key(pal, inst), "render_method": "opaque"} for inst in PALETTE[pal]}
    mats["*"] = dict(mats["tread"])
    perms = []
    for ci, cell in enumerate(cells):
        for part in PARTS:
            for hand, dh in HANDS.items():
                gid = f"geometry.pw_spiral_{design}_{dh}_{part}_c{cell}".lower()   # 1.3.229: lowercase ids (his first-load log)
                if gid not in geo_ids: raise SystemExit(f"missing geometry {gid}")
                boxes = col[(dh, part)].get(f"c{cell}") or [{"origin": [-8, 0, -8], "size": [16, 1, 16]}]
                for d, rot in DIRS.items():
                    cc = f"q.block_state('pw:cell') == {ci} && " if len(cells) > 1 else ""   # a 1-value enum is refused (BDS)
                    perms.append({"condition": f"{cc}q.block_state('pw:part') == '{part}' && "
                                               f"q.block_state('pw:hand') == '{hand}' && q.block_state('minecraft:cardinal_direction') == '{d}'",
                                  "components": {"minecraft:geometry": {"identifier": gid},
                                                 "minecraft:collision_box": boxes,
                                                 "minecraft:transformation": {"rotation": [0, rot, 0]}}})
    return {"format_version": FORMAT, "minecraft:block": {
        "description": {"identifier": ident, "menu_category": {"category": "construction"},
                        "traits": {"minecraft:placement_direction": {"enabled_states": ["minecraft:cardinal_direction"], "y_rotation_offset": 0}},
                        "states": ({"pw:cell": list(range(len(cells)))} if len(cells) > 1 else {}) | {"pw:part": PARTS, "pw:hand": list(HANDS)}},
        "components": {"minecraft:geometry": {"identifier": f"geometry.pw_spiral_{design}_r_mid_c{cells[0]}".lower()},
                       "minecraft:material_instances": mats,
                       "minecraft:collision_box": [{"origin": [-8, 0, -8], "size": [16, 16, 16]}],
                       "minecraft:selection_box": {"origin": [-8, 0, -8], "size": [16, 16, 16]},
                       "minecraft:destructible_by_mining": {"seconds_to_destroy": 1.5},
                       "minecraft:destructible_by_explosion": {"explosion_resistance": 6},
                       "minecraft:light_dampening": 0,
                       "minecraft:display_name": f"Spiral stairs {design.split('_')[1]} ({pal.replace('_', ' + ')})"},
        "permutations": perms}}


def rw(x, z, b):
    a = math.radians(b)
    return x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)


def pad_structure(cells_of, main=False):
    """the test pad: floor + the six stairs + their landings (world x east, z south, y up)."""
    gap = 4
    spans = [2 * SG.DESIGNS[d]["n"] + 3 + 2 for d, _, _ in PAD]           # well + landing depth + margin
    W = sum(spans) + gap * (len(PAD) + 1)
    D = max(2 * SG.DESIGNS[d]["n"] for d, _, _ in PAD) + 2 * 3 + 4
    H = 1 + 8 + 2
    st = M.Structure((W, H, D))
    for x in range(W):
        for z in range(D):
            st.set(x, 0, z, "minecraft:smooth_stone", {})
    x_at = gap
    for (design, pal, hand), span in zip(PAD, spans):
        n = SG.DESIGNS[design]["n"]
        cx, cz = x_at + n + 3, D // 2                                    # the helix corner (a grid corner), in blocks
        dh = HANDS[hand]
        name = block_id(design, pal, main)
        for k in range(8):
            part = "start" if k == 0 else ("end" if k == 7 else "mid")
            sgn = 1 if hand == "ccw" else -1                              # the mirrored (cw) design ascends by -90 per quarter
            b = (sgn * 90 * k) % 360
            for ci, cell in enumerate(cells_of[design]):
                i, j = int(cell[0]), int(cell[1])
                wx, wz = rw(-(16 * i + 8), 16 * j + 8, b)                  # M then Rw(90k)
                bx, bz = cx + math.floor(wx / 16), cz + math.floor(wz / 16)
                sts = {"pw:part": M.s(part), "pw:hand": M.s(hand), "minecraft:cardinal_direction": M.s(DIR_OF_B[b])}
                if len(cells_of[design]) > 1: sts["pw:cell"] = M.i(ci)
                st.set(bx, 1 + k, bz, name, sts)
        x0, x1, z0, z1 = SG.landing_local(n, dh)
        for lx in range(int(x0) + 8, int(x1), 16):
            for lz in range(int(z0) + 8, int(z1), 16):
                wx, wz = rw(-lx, lz, (90 * 7 * (1 if hand == "ccw" else -1)) % 360)
                lx_, lz_ = cx + math.floor(wx / 16), cz + math.floor(wz / 16)
                if not (0 <= lx_ < W and 0 <= lz_ < D): raise SystemExit(f"floor in front leaves the pad: {design} {hand} ({lx_}, {lz_})")
                if st.get(lx_, 8, lz_): raise SystemExit(f"floor in front hits a stair block: {design} {hand} ({lx_}, 8, {lz_})")
                st.set(lx_, 8, lz_, "minecraft:spruce_planks", {})
        # his 14:44 check: the foot stands on the floor, the head tread is flush with the landing (0 px bridge)
        q, yfoot, bridge = SG.fit_floors(1, 9)
        assert q == 8 and yfoot == 1 and bridge == 0, (q, yfoot, bridge)
        x_at += span + gap
    return st


def main_packs():
    """program 228 (his 15:23 'test all at once'): the spiral blocks INTO the main packs — BP-02 overlay (blocks with
    lowercase ids + the pad structure) and an RP-04 staging dir (geometry, textures, terrain keys) for build_rp04_159.py"""
    global RP
    OV = Path("/home/claude/tools/bp02_overlay_228")
    ST = Path("/home/claude/_staging/spiral228/rp")
    if ST.exists(): shutil.rmtree(ST)
    RP = ST
    (ST / "models/blocks").mkdir(parents=True)
    data = write_textures()
    (ST / "textures/terrain_texture.json").unlink()
    (ST / "terrain_texture_add.json").write_text(json.dumps(data, indent=1))
    all_geos, cells_of, cols = [], {}, {}
    for design in SG.DESIGNS:
        geos, col, cells = design_parts(design)
        all_geos += geos; cells_of[design] = cells; cols[design] = col
    # 1.3.229 (his first-load content log, 22:46 CT 10-06: "cannot find geometry.pw_spiral_C_grand_..." for EVERY spiral
    # piece): the client registered none of them. All 4,618 working geometries in our packs are lowercase and format 1.16.0;
    # these were mixed case and 1.21.0 -> both normalised.
    for g in all_geos: g["description"]["identifier"] = g["description"]["identifier"].lower()
    (ST / "models/blocks/pw_spiral_stairs.geo.json").write_text(json.dumps({"format_version": "1.16.0", "minecraft:geometry": all_geos}))
    geo_ids = {g["description"]["identifier"] for g in all_geos}
    (OV / "blocks").mkdir(parents=True, exist_ok=True)
    for f in (OV / "blocks").glob("pw_spiral_stairs_*.json"): f.unlink()
    for design, pal in BLOCKS:
        bj = block_json(design, pal, cells_of[design], cols[design], geo_ids, main=True)
        (OV / f"blocks/pw_spiral_stairs_{design.lower()}_{pal}.json").write_text(json.dumps(bj, indent=1))
    (OV / "structures/pw").mkdir(parents=True, exist_ok=True)
    (OV / "structures/pw/spiral_pad.mcstructure").write_bytes(pad_structure(cells_of, main=True).to_bytes())
    json.dump({d: c for d, c in cells_of.items()}, open(ST / "cells_of.json", "w"))
    print(f"main packs: {len(BLOCKS)} blocks -> {OV / 'blocks'}, geometry {len(all_geos)} + {len(data)} textures -> {ST}")


def main():
    if "--main" in sys.argv:
        return main_packs()
    for p in (BP, RP):
        if p.exists(): shutil.rmtree(p)
    (RP / "models/blocks").mkdir(parents=True)
    (BP / "blocks").mkdir(parents=True)
    (BP / "structures/pw").mkdir(parents=True)
    write_textures()
    all_geos, cells_of, report = [], {}, {}
    cols = {}
    for design in SG.DESIGNS:
        geos, col, cells = design_parts(design)
        all_geos += geos; cells_of[design] = cells; cols[design] = col
        report[design] = {"geometries": len(geos), "cells": cells,
                          "max_boxes": max(len(v) for c in col.values() for v in c.values())}
    (RP / "models/blocks/pw_spiral_stairs.geo.json").write_text(json.dumps({"format_version": "1.21.0", "minecraft:geometry": all_geos}))
    geo_ids = {g["description"]["identifier"] for g in all_geos}
    for design, pal in BLOCKS:
        bj = block_json(design, pal, cells_of[design], cols[design], geo_ids)
        (BP / f"blocks/pw_spiral_stairs_{design}_{pal}.json").write_text(json.dumps(bj, indent=1))
        report[f"{design}_{pal}"] = len(bj["minecraft:block"]["permutations"])
    st = pad_structure(cells_of)
    (BP / "structures/pw/spiral_pad.mcstructure").write_bytes(st.to_bytes())
    report["pad_size"] = list(st.size)
    desc = ("v0.0.3 (2026-10-06) SPIRAL STAIRS TEST (0.0.3: the stair exits FORWARD onto the floor in front of its last step, his 15:06): three sizes (A turret / B tower / C grand), both hands, foot + flight + head "
            "pieces with multi-box collision (block format 1.26.0, his ruling for these blocks only). /structure load pw:spiral_pad ~ ~ ~ . "
            "Personal use.")
    (RP / "manifest.json").write_text(json.dumps({"format_version": 2, "header": {"name": "AR Spiral Stairs Test RP v0.0.3", "description": desc,
        "uuid": UU["rp_h"], "version": VER, "min_engine_version": [1, 26, 0]}, "modules": [{"type": "resources", "uuid": UU["rp_m"], "version": VER}]}, indent=1))
    (BP / "manifest.json").write_text(json.dumps({"format_version": 2, "header": {"name": "AR Spiral Stairs Test BP v0.0.3", "description": desc,
        "uuid": UU["bp_h"], "version": VER, "min_engine_version": [1, 26, 0]}, "modules": [{"type": "data", "uuid": UU["bp_m"], "version": VER}],
        "dependencies": [{"uuid": UU["rp_h"], "version": VER}]}, indent=1))
    for p in (BP / "pack_icon.png", RP / "pack_icon.png"):
        Image.open(RP / f"textures/blocks/pw_spiral/{tex_key('oak', 'tread')}.png").convert("RGB").resize((128, 128)).save(p)
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
