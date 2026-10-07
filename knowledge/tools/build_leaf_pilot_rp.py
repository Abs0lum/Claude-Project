#!/usr/bin/env python3
"""build_leaf_pilot_rp.py — LEAF PILOT step 2a (his 15:27 + 15:41 CT 09-30 GO): the pilot leaf blocks for all 11 Patrix 26.2 species.
Writes into NEW build dirs (never the live packs — LEAF PROTOCOL; pilot blocks live in the TestRunner until each species PASSES):
  RP  _build/testrunner-rp-0.4.0  (from 0.3.0): models/blocks/pw_pilot_leaves.geo.json, textures/blocks/pw_pilot/* (+ texture sets),
      terrain_texture keys, block names; manifest 0.4.0 WITH capabilities ["pbr"] + min_engine [1,21,120] (0.3.0 had neither — L-SKY-3 /
      L-VV-2: a non-declaring RP can drop the whole world out of Vibrant Visuals, and the pilot must be judged under VV)
  BP  blocks only -> _build/leaf-pilot-blocks/ (build_testrunner.py copies them into BP 0.4.6)
Design C-WH80 (his picks): Patrix model (oak family: bottomless cube + 3 cards / cards-only beside the wood; spruce: open-sided cube +
4 cards) + a second card set at 80 %, turned 90 deg, on every full leaf. pw:pv 0..8 (his OK 14:39): 0 far cube (opaque) · 1-5 + 8 full
(each its own quarter-turn + face tile + card tile) · 6-7 cards-only (spruce: full). Materials: "*" face tile, "extra" card tile,
"top" spruce up face; alpha_test, no AO, no face dimming (Java shade:false). Blocks: pre-coloured (pw:pilot_<s>_leaves) for all 11,
biome-tinted (…_bt) for the 7 Java-tinted species, isotropic A/B (oak, spruce: …_iso), far swap (oak, spruce: …_far raw, …_farp
see-through pixels painted leaf colour) with alpha_test_to_opaque. Normals + MERS from Patrix _n / _s by Lesson #156."""
import copy, json, math, shutil, sys, time
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
import java_leaf_study as J
import leaf_pilot_render as P
import leaf_fullness_iter as LF
from bb_truth import truth_posed_faces
from equine_compare import bone_affines

ROOT = Path("/home/claude")
SRC_RP, RP = ROOT / "_build/testrunner-rp-0.3.0", ROOT / "_build/testrunner-rp-0.4.0"
BLK = ROOT / "_build/leaf-pilot-blocks"
DATE = "2026-09-30"
SPECIES = P.SPECIES
TINT_METHOD = {"oak": "default_foliage", "dark_oak": "default_foliage", "jungle": "default_foliage", "acacia": "default_foliage",
               "mangrove": "default_foliage", "birch": "birch_foliage", "spruce": "evergreen_foliage"}
TINTED = set(TINT_METHOD)
# variant table: pv -> (shape, quarter-turn, face tile index, card tile index); birch's card weights 2 1 2 1 -> cards 0 and 2 twice
FULL = {1: (0, 0, 0), 2: (1, 1, 2), 3: (2, 2, 0), 4: (3, 3, 2), 5: (1, 4, 1), 8: (3, 5, 3)}
CARDS = {6: (0, 2), 7: (2, 3)}


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT {time.strftime('%m-%d')}] BUILD leaf-pilot RP: {m}\n")


def mers_156(spec):
    """Lesson #156 LabPBR _s -> Bedrock MERS (same code as build_strips_1.py, witnessed on the nether portal)."""
    R, G, B, A = (spec[..., i].astype(int) for i in range(4))
    out = np.zeros_like(spec)
    out[..., 0] = np.where(G >= 230, 255, 0); out[..., 1] = np.where(A < 255, A, 0)
    out[..., 2] = 255 - R; out[..., 3] = np.where(B >= 65, np.round((B - 64) * 255 / 191), 0)
    return out


def normal_156(n):
    x = n[..., 0].astype(float) / 255 * 2 - 1; y = n[..., 1].astype(float) / 255 * 2 - 1
    z = np.sqrt(np.clip(1 - x * x - y * y, 0, 1))
    out = np.zeros_like(n); out[..., 0] = n[..., 0]; out[..., 1] = n[..., 1]; out[..., 2] = np.round(z * 255); out[..., 3] = 255
    return out


def rgba(p): return np.asarray(Image.open(p).convert("RGBA")).astype(np.uint8)
def save(a, p): p.parent.mkdir(parents=True, exist_ok=True); Image.fromarray(a.astype(np.uint8), "RGBA").save(p)


def sibling(p, suffix):
    q = p.with_name(p.stem + suffix + ".png")
    return q if q.exists() else None


def painted(a):
    """far-swap test: see-through pixels get the mean colour of the drawn pixels (alpha kept, so near alpha_test still cuts)."""
    a = a.copy(); m = a[..., 3] >= 128
    mean = a[..., :3][m].mean(0) if m.any() else np.array([80, 110, 60])
    a[..., :3][~m] = mean.round().astype(np.uint8); return a


# ---------- geometry
def turn90(cube):
    """the same cube turned 90 deg about the block's vertical centre line (file frame: (x,y,z) -> (z,y,-x)); faces renamed by their
    new side (file frame: east=-x, west=+x, north=-z, south=+z); single-axis cube rotations only (all Patrix cards)."""
    o, s = cube["origin"], cube["size"]
    c = copy.deepcopy(cube)
    c["origin"] = [round(o[2], 4), o[1], round(-(o[0] + s[0]), 4)]
    c["size"] = [s[2], s[1], s[0]]
    if "pivot" in cube:
        p = cube["pivot"]; c["pivot"] = [round(p[2], 4), p[1], round(-p[0], 4)]
    if "rotation" in cube:
        rx, ry, rz = cube["rotation"]; c["rotation"] = [rz, ry, -rx]
    ren = {"east": "south", "south": "west", "west": "north", "north": "east", "up": "up", "down": "down"}
    c["uv"] = {ren[k]: v for k, v in cube["uv"].items()}
    return c


def pointset(bones):
    fs = truth_posed_faces(bones, 16, 16, bone_affines(bones))
    return sorted(tuple(round(v, 2) for v in p) for f in fs for p in f.pts)


def geometries():
    """returns {gid: bones} + a self-check that turn90 == the renderer's own quarter-turn (point sets equal)."""
    full = J.load_java("leaves_extra1"); cards = J.load_java("leaves_extra3"); spr = J.load_java("leaves_extra2")
    out, checks = {}, []
    for gid, model, second in (("geometry.pw_pilot_full", full, True), ("geometry.pw_pilot_cards", cards, False),
                               ("geometry.pw_pilot_spruce", spr, True)):
        bones = J.java_to_bedrock(model, {"#all": 0, "#extra": 0}, mat_names={"#extra": "extra"})
        cubes = bones[0]["cubes"]
        if gid == "geometry.pw_pilot_spruce":
            for c in cubes:
                if 0 not in c["size"] and "up" in c["uv"]: c["uv"]["up"]["material_instance"] = "top"
        if second:
            sec = [LF.scaled(c, 0.8) for c in cubes if 0 in c["size"]]
            turned = [turn90(c) for c in sec]
            def quarter_points(q):
                fs = J.block_faces([{"name": "l", "pivot": [0, 0, 0], "cubes": sec}], 16, 16, (0, 0, 0), quarter=q, dimmed=False)
                return sorted(tuple(round(v, 2) for v in p) for f in fs for p in f.pts)
            ref, ref3 = quarter_points(1), quarter_points(3)
            got = pointset([{"name": "l", "pivot": [0, 0, 0], "cubes": turned}])
            checks.append((gid, got == ref or got == ref3))
            cubes = cubes + turned
        out[gid] = [{"name": "leaves", "pivot": [0, 0, 0], "cubes": cubes}]
    out["geometry.pw_pilot_far"] = [{"name": "leaves", "pivot": [0, 0, 0], "cubes": [{"origin": [-8, 0, -8], "size": [16, 16, 16],
                                    "uv": {n: {"uv": [0, 0], "uv_size": [16, 16]} for n in ("north", "south", "east", "west", "up", "down")}}]}]
    return out, checks


# ---------- textures
def tile_lists(s):
    sides, tops, cards, cw = P.tiles(s)
    faces = sides + tops                                  # spruce: 4 sides + 2 tops; others: 6
    return faces, cards


def write_textures(s, keys, report):
    faces, cards = tile_lists(s)
    names = {"f": [], "c": []}
    for kind, lst in (("f", faces), ("c", cards)):
        for i, src in enumerate(lst):
            base = f"{s}_{kind}{i}"
            col = rgba(src)
            n_src, s_src = sibling(src, "_n"), sibling(src, "_s")
            pbr = {}
            if n_src is not None: save(normal_156(rgba(n_src)), RP / f"textures/blocks/pw_pilot/{base}_n.png"); pbr["normal"] = f"{base}_n"
            if s_src is not None: save(mers_156(rgba(s_src)), RP / f"textures/blocks/pw_pilot/{base}_mers.png"); pbr["metalness_emissive_roughness_subsurface"] = f"{base}_mers"
            report["pbr_missing"] += [] if pbr.keys() >= {"normal", "metalness_emissive_roughness_subsurface"} else [base]
            variants = [("", col)]
            if s in TINTED:
                variants = [("", col), ("_pc", np.asarray(P.colour(src, s)).astype(np.uint8))]
            if s in ("oak", "spruce"):
                pc = variants[-1][1]; variants.append(("_farp", painted(pc)))
            for suf, arr in variants:
                name = base + suf
                save(arr, RP / f"textures/blocks/pw_pilot/{name}.png")
                ts = {"format_version": "1.21.30", "minecraft:texture_set": {"color": name, **pbr}}
                (RP / f"textures/blocks/pw_pilot/{name}.texture_set.json").write_text(json.dumps(ts, indent=1))
                keys[f"pw_pilot_{name}"] = {"textures": f"textures/blocks/pw_pilot/{name}"}
            names[kind].append(base)
    return names


# ---------- blocks
def material(tex, method, tint=None, iso=False):
    m = {"texture": tex, "render_method": method, "ambient_occlusion": False, "face_dimming": False}
    if tint: m["tint_method"] = tint
    if iso: m["isotropic"] = True
    return m


def block_json(ident, s, names, suffix, tint, iso=False, far=False):
    method = "alpha_test_to_opaque" if far else "alpha_test"
    F, C = names["f"], names["c"]
    spruce = s == "spruce"
    def mats(fi, ci):
        m = {"*": material(f"pw_pilot_{F[fi]}{suffix}", method, tint, iso), "extra": material(f"pw_pilot_{C[ci]}{suffix}", method, tint)}
        if spruce: m["top"] = material(f"pw_pilot_{F[4 + fi % 2]}{suffix}", method, tint, iso)
        return m
    perms = [{"condition": "q.block_state('pw:pv') == 0", "components": {
        "minecraft:geometry": "geometry.pw_pilot_far",
        "minecraft:material_instances": {"*": material(f"pw_pilot_{F[0]}{suffix}", "opaque", tint)}}}]
    for pv in range(1, 9):
        if pv in FULL or spruce:
            q, fi, ci = FULL.get(pv) or {6: (0, 1, 1), 7: (2, 3, 3)}[pv]
            geo = "geometry.pw_pilot_spruce" if spruce else "geometry.pw_pilot_full"
            if spruce: fi = fi % 4
        else:
            q, ci = CARDS[pv]; fi = 0; geo = "geometry.pw_pilot_cards"
        comp = {"minecraft:geometry": geo, "minecraft:material_instances": mats(fi, ci)}
        if q: comp["minecraft:transformation"] = {"rotation": [0, 90 * q, 0]}
        perms.append({"condition": f"q.block_state('pw:pv') == {pv}", "components": comp})
    return {"format_version": "1.21.80", "minecraft:block": {
        "description": {"identifier": ident, "menu_category": {"category": "nature"}, "states": {"pw:pv": list(range(9))}},
        "components": {"minecraft:geometry": "geometry.pw_pilot_far",
                       "minecraft:material_instances": {"*": material(f"pw_pilot_{F[0]}{suffix}", "opaque", tint)},
                       "minecraft:light_dampening": 1, "minecraft:destructible_by_mining": {"seconds_to_destroy": 0.2},
                       "minecraft:destructible_by_explosion": {"explosion_resistance": 0.2}, "minecraft:map_color": "#3f6b2a"},
        "permutations": perms}}


def main():
    if RP.exists(): shutil.rmtree(RP)
    shutil.copytree(SRC_RP, RP)
    if BLK.exists(): shutil.rmtree(BLK)
    BLK.mkdir(parents=True)
    geos, checks = geometries()
    assert all(ok for _, ok in checks), checks
    gdoc = {"format_version": "1.21.0", "minecraft:geometry": [
        {"description": {"identifier": gid, "texture_width": 16, "texture_height": 16, "visible_bounds_width": 3, "visible_bounds_height": 3,
                         "visible_bounds_offset": [0, 0.5, 0]}, "bones": b} for gid, b in geos.items()]}
    (RP / "models/blocks").mkdir(parents=True, exist_ok=True)
    (RP / "models/blocks/pw_pilot_leaves.geo.json").write_text(json.dumps(gdoc, indent=1))
    log(f"geometry: {len(geos)} shapes; turn90 == renderer quarter-turn: {checks}")
    tt_path = RP / "textures/terrain_texture.json"; tt = json.loads(tt_path.read_text(encoding="utf-8-sig"))
    keys = tt.setdefault("texture_data", {}); report = {"pbr_missing": []}; blocks = []; lang = []
    for s in SPECIES:
        names = write_textures(s, keys, report)
        nice = s.replace("_", " ").title()
        pc = "_pc" if s in TINTED else ""
        blocks.append((f"pw:pilot_{s}_leaves", block_json(f"pw:pilot_{s}_leaves", s, names, pc, None)))
        lang.append(f"tile.pw:pilot_{s}_leaves.name=Pilot {nice} Leaves")
        if s in TINTED:
            blocks.append((f"pw:pilot_{s}_leaves_bt", block_json(f"pw:pilot_{s}_leaves_bt", s, names, "", TINT_METHOD[s])))
            lang.append(f"tile.pw:pilot_{s}_leaves_bt.name=Pilot {nice} Leaves (biome colour)")
        if s in ("oak", "spruce"):
            blocks.append((f"pw:pilot_{s}_leaves_iso", block_json(f"pw:pilot_{s}_leaves_iso", s, names, pc, None, iso=True)))
            blocks.append((f"pw:pilot_{s}_leaves_far", block_json(f"pw:pilot_{s}_leaves_far", s, names, pc, None, far=True)))
            blocks.append((f"pw:pilot_{s}_leaves_farp", block_json(f"pw:pilot_{s}_leaves_farp", s, names, "_farp", None, far=True)))
            lang += [f"tile.pw:pilot_{s}_leaves_iso.name=Pilot {nice} Leaves (random turns)", f"tile.pw:pilot_{s}_leaves_far.name=Pilot {nice} Leaves (far swap)",
                     f"tile.pw:pilot_{s}_leaves_farp.name=Pilot {nice} Leaves (far swap, painted)"]
    tt_path.write_text(json.dumps(tt, indent=1))
    for ident, doc in blocks:
        (BLK / (ident.split(":")[1] + ".json")).write_text(json.dumps(doc, indent=1))
    lp = RP / "texts/en_US.lang"; lp.write_text(lp.read_text(encoding="utf-8").rstrip("\n") + "\n" + "\n".join(lang) + "\n", encoding="utf-8")
    man = RP / "manifest.json"; m = json.loads(man.read_text(encoding="utf-8-sig"))
    m["header"]["version"] = [0, 4, 0]; m["header"]["min_engine_version"] = [1, 21, 120]; m["header"]["name"] = "PW Test Runner RP v0.4.0"
    for mod in m["modules"]: mod["version"] = [0, 4, 0]
    m["capabilities"] = ["pbr"]
    m["header"]["description"] = (f"v0.4.0 ({DATE}) TEST RUNNER RP — the LEAF PILOT: pw:pilot_<species>_leaves for all 11 Patrix 26.2 leaf species "
        "(cube + cards, cards only beside the wood, a second card set at 80 %), pre-coloured and biome-coloured, random-turn and far-swap "
        "test blocks, 128 px Patrix art with normal + MERS maps; now declares Vibrant Visuals (pbr) support. Plus everything of v0.3.0 "
        "(the pw:probe entity, the XPACK keys). Job-only: attach at the TOP of the Resource Packs list while testing.")
    man.write_text(json.dumps(m, indent=1))
    log(f"{len(blocks)} pilot blocks -> {BLK}; {len([k for k in keys if k.startswith('pw_pilot_')])} texture keys; PBR missing for {len(report['pbr_missing'])} tiles {report['pbr_missing'][:6]}; RP manifest 0.4.0 + pbr + 1.21.120")
    (ROOT / "_logs/leaf_pilot_build.json").write_text(json.dumps({"blocks": [b for b, _ in blocks], "pbr_missing": report["pbr_missing"]}, indent=1))


if __name__ == "__main__":
    main()
