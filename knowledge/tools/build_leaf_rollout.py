#!/usr/bin/env python3
"""build_leaf_rollout.py — v2 (D-C347, the independent check of the 1.3.196 / 1.3.105 build — packaged, never delivered, numbers retired):
  BP-02 1.3.197: + RELOOK SWEEP (saved worlds: every leaf of a chunk gets the new look once, chunk marks kept in world dynamic
  properties), exposure resets off (looks do not depend on exposure; ended a re-write loop), a broken LOG re-looks the leaves beside
  it, jungle / acacia probe to 4. RP-01 1.3.106: falling-canopy / particle tiles OPAQUE (painted, alpha 255).
THE LEAF ROLLOUT (D-C343 plan, his GO 18:44 CT 09-30): the C-WH80 pilot leaves (p15 27/27 PASS) replace
today's leaves in the main packs.
  BP-02 1.3.196 (from 1.3.195)
    blocks   the 9 pw:<species>_leaves keep their id, their 5 states and every base component (loot, flammable, tag:plant, destroy
             time, map colour, pw:randomize_variant); only the 7 pw:variant permutations change: v0-v4 = five FULL shapes (v0 is what
             worldgen places — a real leaf now, not the far cube), v5-v6 = CARDS ONLY (beside the wood); spruce = seven full shapes.
             Every variant: alpha_test_to_opaque (the game itself turns it solid far away — L-FAR-1), no AO, no face dimming,
             per-variant quarter turn, isotropic face tiles (his 18:14 "leave it on"), biome colour for the 7 tinted species (his Q1).
             NEW pw:azalea_leaves + pw:flowering_azalea_leaves (Patrix 26.2 art; oak family in the scripts; his Q2).
    main.js  a leaf's look is picked ONCE from its position + its distance to the wood (probed around it, Manhattan <= 3);
             pw:rseed = 'look set'; the phase-1 far branch and the applied-registry (far reverter / re-applicator) are no longer fed;
             azalea ids join the leaf sets; PW_BUILD 1.3.196.
  RP-01 1.3.105 (from 1.3.104)
    adds     models/blocks/pw_leaves2.geo.json (full / cards / spruce), textures/blocks/pw_leaves2/* (Patrix 26.2 128 px tiles with
             see-through pixels painted leaf colour for the far swap, + normal + MERS texture sets by Lesson #156), terrain keys
             pw_leaves2_*, pre-coloured 'fall' tiles for the falling-tree canopy + the leaf-fall particle, blocks.json + names for the
             2 azalea blocks.
    removes  the old leaf geometry (pw_leaves_variants / pw_leaves_jungle_variants), the 180 old leaf terrain keys, their PNGs +
             texture sets and their 156 flipbook entries (wind animation returns with the wind work, his Q4).
Rollback = BP-02 1.3.195 + RP-01 1.3.104 together. Test in a COPY of the test world (p16). verify: verify_leaf_rollout.py"""
import json, re, shutil, sys, time
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML
import build_leaf_pilot_rp as B
import leaf_pilot_render as P

ROOT = Path("/home/claude")
BP_SRC, BP, BP_VER = ROOT / "_build/bp02-195", ROOT / "_build/bp02-197", [1, 3, 197]
RP_SRC, RP, RP_VER = ROOT / "_build/rp01-104", ROOT / "_build/rp01-106", [1, 3, 106]
DATE = "2026-09-30"
WOODS = ("oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "mangrove", "cherry", "pale_oak")
AZ = ("azalea", "flowering_azalea")
ALL = WOODS + AZ
TINT = B.TINT_METHOD                                    # 7 tinted species -> biome colour (his Q1)
# variant -> (shape, quarter turn, face tile, card tile); pilot pv1..pv5 -> v0..v4 (full), pv6/pv7 -> v5/v6 (cards only)
FULL_V = {0: (0, 0, 0), 1: (1, 1, 2), 2: (2, 2, 0), 3: (3, 3, 2), 4: (1, 4, 1)}
CARD_V = {5: (0, 2), 6: (2, 3)}
SPRUCE_V = {0: (0, 0, 0), 1: (1, 1, 2), 2: (2, 2, 0), 3: (3, 3, 2), 4: (1, 4, 1), 5: (3, 5, 3), 6: (0, 1, 1)}   # pilot pv 1-5, 8, 6
AZ_COLOUR = {"azalea": "#5a7a2e", "flowering_azalea": "#7a6a52"}
GEO = {"full": "geometry.pw_leaves2_full", "cards": "geometry.pw_leaves2_cards", "spruce": "geometry.pw_leaves2_spruce"}


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT {time.strftime('%m-%d')}] BUILD leaf-rollout: {m}\n")


def key(s, kind, i): return f"pw_leaves2_{s}_{kind}{i}"


# ---------------------------------------------------------------- RP-01
def rp_textures(tt):
    """writes the tiles each species uses; returns {species: (face tile count, card tile count)}"""
    used = {}
    for s in ALL:
        faces, cards = B.tile_lists(s)
        nf = 6 if s == "spruce" else 5
        for kind, lst, n in (("f", faces, nf), ("c", cards, 4)):
            assert len(lst) >= n, (s, kind, len(lst))
            for i in range(n):
                src = lst[i]; name = f"{s}_{kind}{i}"; d = RP / "textures/blocks/pw_leaves2"
                col = B.rgba(src)                                     # tinted species: Patrix grey art (the game adds the biome colour)
                B.save(B.painted(col), d / f"{name}.png")            # see-through pixels painted: the far opaque look is leafy
                ts = {"color": name}
                n_src, s_src = B.sibling(src, "_n"), B.sibling(src, "_s")
                if n_src is not None: B.save(B.normal_156(B.rgba(n_src)), d / f"{name}_n.png"); ts["normal"] = f"{name}_n"
                if s_src is not None: B.save(B.mers_156(B.rgba(s_src)), d / f"{name}_mers.png"); ts["metalness_emissive_roughness_subsurface"] = f"{name}_mers"
                (d / f"{name}.texture_set.json").write_text(json.dumps({"format_version": "1.21.30", "minecraft:texture_set": ts}, indent=1))
                tt[key(s, kind, i)] = {"textures": f"textures/blocks/pw_leaves2/{name}"}
        fall = P.colour(faces[0], s) if s in TINT else B.rgba(faces[0])      # falling canopy + particle: pre-coloured
        fa = B.painted(B.np.asarray(fall).astype(B.np.uint8)); fa[..., 3] = 255                # opaque: the canopy entity + particle show it whole
        B.save(fa, RP / f"textures/blocks/pw_leaves2/{s}_fall.png")
        used[s] = (nf, 4)
    return used


def build_rp():
    if RP.exists(): shutil.rmtree(RP)
    shutil.copytree(RP_SRC, RP)
    # geometry: the pilot shapes under our names (the far cube is not needed any more)
    geos, checks = B.geometries()
    assert all(ok for _, ok in checks), checks
    ren = {"geometry.pw_pilot_full": GEO["full"], "geometry.pw_pilot_cards": GEO["cards"], "geometry.pw_pilot_spruce": GEO["spruce"]}
    gdoc = {"format_version": "1.21.0", "minecraft:geometry": [
        {"description": {"identifier": ren[g], "texture_width": 16, "texture_height": 16, "visible_bounds_width": 3, "visible_bounds_height": 3,
                         "visible_bounds_offset": [0, 0.5, 0]}, "bones": b} for g, b in geos.items() if g in ren]}
    (RP / "models/blocks/pw_leaves2.geo.json").write_text(json.dumps(gdoc, indent=1))
    old_geo = [RP / "models/blocks/pw_leaves_variants.geo.json", RP / "models/blocks/pw_leaves_jungle_variants.geo.json"]
    for p in old_geo: p.unlink()
    # terrain keys: old leaf keys out, new in
    ttp = RP / "textures/terrain_texture.json"; tdoc = json.loads(ttp.read_text(encoding="utf-8-sig")); tt = tdoc["texture_data"]
    old_keys = [k for k in tt if re.match(r"pw_(oak|spruce|birch|jungle|acacia|dark_oak|mangrove|cherry|pale_oak)_leaves", k)]
    assert len(old_keys) == 180, len(old_keys)
    old_paths = set()
    for k in old_keys:
        t = tt.pop(k)["textures"]
        for v in (t if isinstance(t, list) else [t]): old_paths.add(v if isinstance(v, str) else v.get("path"))
    used = rp_textures(tt)
    ttp.write_text(json.dumps(tdoc, indent=1))
    # flipbooks: the old leaf tiles' animation entries out
    fbp = RP / "textures/flipbook_textures.json"; fb = json.loads(fbp.read_text(encoding="utf-8-sig"))
    keep = [e for e in fb if not re.match(r"pw_(oak|spruce|birch|jungle|acacia|dark_oak|mangrove|cherry|pale_oak)_leaves", e.get("atlas_tile", ""))]
    assert len(fb) - len(keep) == 156, len(fb) - len(keep)
    fbp.write_text(json.dumps(keep, indent=1))
    # old leaf PNGs + texture sets (only files no remaining JSON references)
    entity = RP / "entity/falling_tree.json"; e = entity.read_text(encoding="utf-8")
    e2, n = re.subn(r"textures/blocks/pw_([a-z_]+?)_leaves_v\d", lambda m: f"textures/blocks/pw_leaves2/{m.group(1)}_fall", e)
    assert n == 60, n
    entity.write_text(e2, encoding="utf-8")
    part = RP / "particles/pw_leaf_fall.json"; ptxt = part.read_text(encoding="utf-8")
    assert ptxt.count("textures/blocks/pw_oak_leaves_v0") == 1
    part.write_text(ptxt.replace("textures/blocks/pw_oak_leaves_v0", "textures/blocks/pw_leaves2/oak_fall"), encoding="utf-8")
    texts = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in RP.rglob("*.json") if "pw_leaves2" not in p.name)
    removed = 0
    for p in sorted((RP / "textures/blocks").glob("pw_*_leaves_*")):
        stem = "textures/blocks/" + p.name.split(".")[0]
        if p.name.endswith(".texture_set.json") or stem not in texts:
            p.unlink(); removed += 1
    leftover = [p.name for p in (RP / "textures/blocks").glob("pw_*_leaves_*")]
    # blocks.json + names for the 2 azalea blocks (the 9 keep their entries)
    bj = RP / "blocks.json"; bjd = json.loads(bj.read_text(encoding="utf-8-sig"))
    for s in AZ: bjd[f"pw:{s}_leaves"] = {"sound": "grass"}
    bj.write_text(json.dumps(bjd, indent=1))
    lang = RP / "texts/en_US.lang"; lt = lang.read_text(encoding="utf-8").rstrip("\n")
    names = {**{w: w.replace("_", " ").title() + " Leaves" for w in WOODS}, "azalea": "Azalea Leaves", "flowering_azalea": "Flowering Azalea Leaves"}
    add = [f"tile.pw:{s}_leaves.name={n}" for s, n in names.items() if f"tile.pw:{s}_leaves.name=" not in lt]
    lang.write_text(lt + "\n" + "\n".join(add) + "\n", encoding="utf-8")
    man = RP / "manifest.json"; m = json.loads(man.read_text(encoding="utf-8-sig"))
    m["header"]["version"] = RP_VER; m["header"]["name"] = "AbsolutRealism Tectonic RP v1.3.106"
    for mod in m["modules"]: mod["version"] = RP_VER
    m["header"]["description"] = (f"v1.3.106 ({DATE}) THE LEAF ROLLOUT: every pw leaf (9 species + new azalea and flowering azalea) uses the "
        "C-WH80 design that passed p15 27/27 — Patrix 26.2 128 px tiles, biome-coloured where Java tints them, cube + cards, cards only "
        "beside the wood, normal + MERS maps; the game turns them solid far away. Old leaf shapes / tiles / animation removed. Pairs with "
        "BP-02 v1.3.197. Includes all of v1.3.104.")
    man.write_text(json.dumps(m, indent=1))
    log(f"RP-01 1.3.106: geometry pw_leaves2 (3 shapes) in, 2 old geometry files out; 180 old keys out, "
        f"{sum(a + b for a, b in used.values())} new tile keys in; 156 flipbook entries out; falling tree 60 refs + particle repointed; "
        f"{removed} old leaf files removed, leftover {leftover[:4]}")
    return used


# ---------------------------------------------------------------- BP-02
def mat(tex, tint, iso=False):
    m = {"texture": tex, "render_method": "alpha_test_to_opaque", "ambient_occlusion": False, "face_dimming": False}
    if tint: m["tint_method"] = tint
    if iso: m["isotropic"] = True
    return m


def perms(s):
    tint = TINT.get(s); spruce = s == "spruce"; out = []
    for v in range(7):
        if spruce:
            q, fi, ci = SPRUCE_V[v]; geo = GEO["spruce"]
            mi = {"*": mat(key(s, "f", fi % 4), tint, True), "extra": mat(key(s, "c", ci), tint), "top": mat(key(s, "f", 4 + fi % 2), tint, True)}
        elif v in FULL_V:
            q, fi, ci = FULL_V[v]; geo = GEO["full"]
            mi = {"*": mat(key(s, "f", fi), tint, True), "extra": mat(key(s, "c", ci), tint)}
        else:
            q, ci = CARD_V[v]; geo = GEO["cards"]
            mi = {"*": mat(key(s, "f", 0), tint, True), "extra": mat(key(s, "c", ci), tint)}
        comp = {"minecraft:geometry": geo, "minecraft:material_instances": mi}
        if q: comp["minecraft:transformation"] = {"rotation": [0, 90 * q, 0]}
        out.append({"condition": f"q.block_state('pw:variant') == {v}", "components": comp})
    return out


def build_bp():
    if BP.exists(): shutil.rmtree(BP)
    shutil.copytree(BP_SRC, BP)
    for w in WOODS:
        p = BP / f"blocks/{w}_leaves.json"; d = ML._parse_json(p.read_text(encoding="utf-8")); blk = d["minecraft:block"]
        assert list(blk["description"]["states"]) == ["pw:variant", "pw:rseed", "pw:section", "pw:exposure", "pw:section_rolled"], w
        assert len(blk["permutations"]) == 7 and "minecraft:geometry" not in blk["components"], w
        blk["permutations"] = perms(w)
        p.write_text(json.dumps(d, indent=2), encoding="utf-8")
    tmpl = ML._parse_json((BP / "blocks/oak_leaves.json").read_text(encoding="utf-8"))
    loot = json.loads((BP / "loot_tables/blocks/oak_leaves.json").read_text(encoding="utf-8"))
    for s in AZ:
        d = json.loads(json.dumps(tmpl)); blk = d["minecraft:block"]
        blk["description"]["identifier"] = f"pw:{s}_leaves"
        blk["components"]["minecraft:map_color"] = AZ_COLOUR[s]
        blk["components"]["minecraft:loot"] = f"loot_tables/blocks/{s}_leaves.json"
        blk["permutations"] = perms(s)
        (BP / f"blocks/{s}_leaves.json").write_text(json.dumps(d, indent=2), encoding="utf-8")
        L = json.loads(json.dumps(loot))
        L["pools"][0]["entries"][0]["name"] = f"minecraft:{s}_leaves"                  # shears -> the vanilla leaf item
        L["pools"][1]["entries"][0]["name"] = f"minecraft:{s}"                          # 5 % -> azalea / flowering azalea bush
        L["pools"] = L["pools"][:3]                                                     # no apple
        (BP / f"loot_tables/blocks/{s}_leaves.json").write_text(json.dumps(L, indent=2), encoding="utf-8")
    mp = BP / "scripts/main.js"; s = mp.read_text(encoding="utf-8")
    def rep(a, b, n=1):
        nonlocal s
        assert s.count(a) == n, (a[:80], s.count(a)); s = s.replace(a, b)
    rep('const PW_BUILD = "1.3.195";', 'const PW_BUILD = "1.3.197";')
    # --- azalea ids in every leaf set (oak family: azalea trees grow oak logs)
    rep('                                            "pw:oak_leaves_e", "pw:oak_leaves_f"] },',
        '                                            "pw:oak_leaves_e", "pw:oak_leaves_f",\n'
        '                                            "pw:azalea_leaves", "pw:flowering_azalea_leaves"] },')
    rep('  "pw:acacia_leaves": 7, "pw:mangrove_leaves": 7, "pw:cherry_leaves": 7,\n  // Log tiers',
        '  "pw:acacia_leaves": 7, "pw:mangrove_leaves": 7, "pw:cherry_leaves": 7,\n  "pw:azalea_leaves": 7, "pw:flowering_azalea_leaves": 7,\n  // Log tiers')
    rep('  "pw:acacia_leaves", "pw:mangrove_leaves", "pw:cherry_leaves",\n  // Log tier blocks',
        '  "pw:acacia_leaves", "pw:mangrove_leaves", "pw:cherry_leaves",\n  "pw:azalea_leaves", "pw:flowering_azalea_leaves",\n  // Log tier blocks')
    rep('  "pw:acacia_leaves", "pw:mangrove_leaves", "pw:cherry_leaves",\n]);',
        '  "pw:acacia_leaves", "pw:mangrove_leaves", "pw:cherry_leaves",\n  "pw:azalea_leaves", "pw:flowering_azalea_leaves",\n]);')
    rep('  "pw:mangrove_leaves": 8,\n};', '  "pw:mangrove_leaves": 8,\n  "pw:azalea_leaves": 0,\n  "pw:flowering_azalea_leaves": 0,\n};')
    # --- the look: position + distance to the wood, picked once
    old_pick = s[s.index("  if (isLeaf) {\n    let sectionRolled, section, exposure;"):s.index("  const N = PW_VARIANT_COUNT[typeId] || 5;")]
    assert "PW_LEAF_VARIANT_POOLS[key]" in old_pick
    s = s.replace(old_pick, "  if (isLeaf) return pwLeafLook(block);   // v1.3.196: position + distance to the wood, no Math.random\n", 1)
    rep("function pickVariantForBlock(block) {", LOOK_JS + "\nfunction pickVariantForBlock(block) {")
    old_on = s[s.index("    let setRseed = true;\n    if (isLeaf) {"):s.index("    let newPerm = block.permutation.withState(\"pw:variant\", choice);")]
    s = s.replace(old_on, "    const setRseed = true;   // v1.3.196: a leaf's look needs no classification first (position + wood), so it is final\n", 1)
    a = s.index("        // --- 2. DISTANCE TOGGLE (hysteresis) ---"); b = s.index("        // Band [INNER,OUTER]: intentionally no change (hysteresis -> no strobe)\n")
    b += len("        // Band [INNER,OUTER]: intentionally no change (hysteresis -> no strobe)\n")
    assert "PW_FAR_OUTER_SQ" in s[a:b] and "_appliedRegistry.set" in s[a:b]
    s = s[:a] + ASSIGN_JS + s[b:]
    # v1.3.197 (independent check): exposure no longer drives the look -> the decay sweep's exposure resets are switched off
    rep("  if (shouldReset) {\n    try {\n      block.setPermutation(block.permutation\n        .withState(\"pw:section_rolled\", false)",
        "  if (shouldReset && PW_EXPOSURE_RESETS) {   // v1.3.197: off — the look depends on position + wood only\n    try {\n      block.setPermutation(block.permutation\n        .withState(\"pw:section_rolled\", false)")
    rep("function reValidateExposure(block) {", "const PW_EXPOSURE_RESETS = false;\nfunction reValidateExposure(block) {")
    # a broken log re-looks the leaves beside it (cascade on its 6 neighbours)
    rep("    if (!id || !id.endsWith(\"_leaves\")) return;\n    if (!PW_LEAF_TYPES.has(id)) return;\n    // Enqueue cascade for re-flagging of inner-neighbor leaves",
        "    if (!id) return;\n    const isLeafB = id.endsWith(\"_leaves\") && PW_LEAF_TYPES.has(id);\n    if (!isLeafB && !pwIsWood(id)) return;   // v1.3.197: a broken LOG re-looks the leaves beside it\n    // Enqueue cascade for re-flagging of inner-neighbor leaves")
    rep("// =========================================================================\n// v1.2.51: REVERSE-RANDOMIZER", RELOOK_JS + "\n// =========================================================================\n// v1.2.51: REVERSE-RANDOMIZER")
    mp.write_text(s, encoding="utf-8")
    man = BP / "manifest.json"; m = json.loads(man.read_text(encoding="utf-8-sig"))
    m["header"]["version"] = BP_VER; m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.197"
    for mod in m["modules"]: mod["version"] = BP_VER
    m["header"]["description"] = (f"v1.3.197 ({DATE}) THE LEAF ROLLOUT: the 9 pw leaf blocks (same ids, same states) now use the C-WH80 "
        "shapes that passed p15 (v0, the worldgen default, is a real leaf; the game turns leaves solid far away); each leaf's look is "
        "picked once from its position and its distance to the wood (no re-roll); leaves saved by older versions get the new look once as "
        "you come near (relook sweep); new pw:azalea_leaves + pw:flowering_azalea_leaves. Pairs with RP-01 v1.3.106. Includes all of v1.3.195.")
    man.write_text(json.dumps(m, indent=1))
    log("BP-02 1.3.197: 9 leaf blocks re-skinned (7 variants each), 2 azalea blocks + loot added; main.js look picker, onPlace, phase-1 assign-once, azalea sets")


LOOK_JS = r'''// =========================================================================
// v1.3.196 LEAF LOOK (D-C343 / D-C345, the C-WH80 pilot rule; his GO 18:44 CT 09-30)
//   A leaf's look is picked ONCE from its position (a fixed hash, never Math.random) and its distance to the wood:
//   touching wood -> cards only (v5 / v6); 2..band blocks -> a coin flip by position between cards and full; farther -> one of five
//   full shapes (v0-v4). Spruce: seven full shapes (no cards, as in Java). Band: jungle / acacia 4, spruce 0, others 3.
//   Distance is probed in Manhattan shells around the leaf (<= band, max 4), not walked through the leaves (the pilot's BFS).
// =========================================================================
const PW_LEAF_BAND = { "pw:jungle_leaves": 4, "pw:acacia_leaves": 4, "pw:spruce_leaves": 0 };
function pwCellHash(x, y, z) {
  let h = (Math.imul(x | 0, 73856093) ^ Math.imul(y | 0, 19349663) ^ Math.imul(z | 0, 83492791)) >>> 0;
  h ^= h >>> 16; h = Math.imul(h, 2246822507) >>> 0; h ^= h >>> 13; h = Math.imul(h, 3266489909) >>> 0; h ^= h >>> 16;
  return h >>> 0;
}
const PW_WOOD_SHELLS = (() => {
  const sh = [[], [], [], [], []];
  for (let dx = -4; dx <= 4; dx++) for (let dy = -4; dy <= 4; dy++) for (let dz = -4; dz <= 4; dz++) {
    const d = Math.abs(dx) + Math.abs(dy) + Math.abs(dz);
    if (d >= 1 && d <= 4) sh[d].push([dx, dy, dz]);
  }
  return sh;
})();
function pwIsWood(id) { return PW_TA_LOG_TYPES.has(id) || /(_log|_wood|_stem|hyphae)$/.test(id); }
function pwWoodDistance(dim, x, y, z, maxD) {
  for (let d = 1; d <= maxD; d++) {
    for (const [a, b, c] of PW_WOOD_SHELLS[d]) {
      let n; try { n = dim.getBlock({ x: x + a, y: y + b, z: z + c }); } catch { continue; }
      if (n && pwIsWood(n.typeId)) return d;
    }
  }
  return 99;
}
function pwLeafLook(block) {
  const id = block.typeId; const loc = block.location; const h = pwCellHash(loc.x, loc.y, loc.z);
  if (id === "pw:spruce_leaves") return (h >>> 12) % 7;
  const band = PW_LEAF_BAND[id] ?? 3;
  let d = 99; try { d = pwWoodDistance(block.dimension, loc.x, loc.y, loc.z, Math.min(band, 4)); } catch { /* unloaded neighbour */ }
  if (d === 1) return 5 + (h % 2);
  if (d >= 2 && d <= band && ((h >>> 8) & 1) === 1) return 5 + ((h >>> 9) % 2);
  return (h >>> 12) % 5;
}
'''

RELOOK_JS = r'''// =========================================================================
// v1.3.197 RELOOK SWEEP (D-C347): leaves saved by 1.3.195 or older keep their old picks (rseed true; v0 left by the old far reverter,
// v5/v6 that are now cards-only). Once per chunk, the sweep walks the leaves near each player (5 x 5 chunks, player y +-32) and gives
// every leaf its 1.3.197 look (position + wood). Chunk marks live in world dynamic properties (one 1024-char string per 32 x 32-chunk
// region), so each chunk is swept once per world, ever.
// =========================================================================
const PW_RELOOK_INTERVAL = 47;            // ticks; coprime with 22 / 30 / 39
const PW_RELOOK_CHUNK_R = 2;
const PW_RELOOK_DY = 32;
let _relookBusy = false;
const _relookCache = new Map();
const _relookStats = { chunks: 0, leaves: 0, changed: 0 };
function _relookKey(dimId, rx, rz) { return `pw:relook:${String(dimId).replace("minecraft:", "")}:${rx}:${rz}`; }
function _relookRegion(dimId, cx, cz) {
  const rx = Math.floor(cx / 32), rz = Math.floor(cz / 32); const k = _relookKey(dimId, rx, rz);
  let s = _relookCache.get(k);
  if (s === undefined) { let v; try { v = world.getDynamicProperty(k); } catch { v = undefined; } s = typeof v === "string" ? v : ""; _relookCache.set(k, s); }
  return { k, s, i: (cx - rx * 32) * 32 + (cz - rz * 32) };
}
function _relookDone(dimId, cx, cz) { const r = _relookRegion(dimId, cx, cz); return r.s.charAt(r.i) === "1"; }
function _relookMark(dimId, cx, cz) {
  const r = _relookRegion(dimId, cx, cz); const s = r.s.padEnd(1024, "0");
  const n = s.slice(0, r.i) + "1" + s.slice(r.i + 1); _relookCache.set(r.k, n);
  try { world.setDynamicProperty(r.k, n); } catch { /* storage refused: the chunk is swept again next session */ }
}
function* _relookJob() {
  let _slice = Date.now(), _cells = 0;
  try {
    for (const player of world.getPlayers()) {
      const dim = player.dimension; const pcx = Math.floor(player.location.x / 16), pcz = Math.floor(player.location.z / 16);
      const py = Math.floor(player.location.y);
      const order = [];
      for (let a = -PW_RELOOK_CHUNK_R; a <= PW_RELOOK_CHUNK_R; a++) for (let b = -PW_RELOOK_CHUNK_R; b <= PW_RELOOK_CHUNK_R; b++) order.push([a, b]);
      order.sort((p, q) => (p[0] * p[0] + p[1] * p[1]) - (q[0] * q[0] + q[1] * q[1]));
      for (const [a, b] of order) {
        const cx = pcx + a, cz = pcz + b;
        if (_relookDone(dim.id, cx, cz)) continue;
        let loaded = true;
        try { if (!dim.getBlock({ x: cx * 16, y: py, z: cz * 16 })) loaded = false; } catch { loaded = false; }
        if (!loaded) continue;
        for (let x = cx * 16; x < cx * 16 + 16; x++) for (let z = cz * 16; z < cz * 16 + 16; z++) for (let y = py - PW_RELOOK_DY; y <= py + PW_RELOOK_DY; y++) {
          if (++_cells >= 400 || (Date.now() - _slice) >= 8) { _cells = 0; yield; _slice = Date.now(); }
          let blk; try { blk = dim.getBlock({ x, y, z }); } catch { continue; }
          if (!blk || !PW_LEAF_TYPES_DECAY.has(blk.typeId)) continue;
          _relookStats.leaves++;
          try {
            const look = pwLeafLook(blk); const p = blk.permutation;
            if (p.getState("pw:variant") !== look || p.getState("pw:rseed") !== true) {
              blk.setPermutation(p.withState("pw:variant", look).withState("pw:rseed", true)); _relookStats.changed++;
            }
          } catch { /* chunk unloaded mid-sweep */ }
        }
        _relookMark(dim.id, cx, cz); _relookStats.chunks++;
      }
    }
  } finally { _relookBusy = false; }
}
system.runInterval(() => {
  if (_relookBusy) return;
  _relookBusy = true;
  try { system.runJob(_relookJob()); } catch (e) { _relookBusy = false; try { logErr(`[pw_relook] job-kick err: ${e}`); } catch {} }
}, PW_RELOOK_INTERVAL);
'''

ASSIGN_JS = r'''        // --- 2. THE LOOK, ONCE (v1.3.196) ---
        // pw:rseed = 'look set'. The look comes from the position + the wood (pwLeafLook), so a re-pick gives the same answer;
        // the far swap is the game's own (alpha_test_to_opaque, L-FAR-1): no distance branch, no applied-registry.
        let rseed;
        try { rseed = block.permutation.getState("pw:rseed"); } catch { continue; }
        if (rseed !== true) {
          let target = 0;
          try { target = pickVariantForBlock(block); } catch { target = 0; }
          try {
            block.setPermutation(block.permutation.withState("pw:variant", target).withState("pw:rseed", true));
            _scanStats.totalRandomized++;
            _scanStats.lastRandomTick = system.currentTick;
            if (!_scanStats.perVariant[target]) _scanStats.perVariant[target] = 0;
            _scanStats.perVariant[target]++;
            if (!_scanStats._markerEFired) {
              _scanStats._markerEFired = true;
              try { console.warn(`[BIGCANOPY-DIAG] MARKER-E v${PW_BUILD} ${PW_BOOT_ID} first leaf look -> variant=${target} at (${x},${y},${z})`); } catch {}
            }
          } catch {}
        }
'''


if __name__ == "__main__":
    build_bp()
    build_rp()
