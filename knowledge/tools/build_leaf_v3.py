#!/usr/bin/env python3
"""build_leaf_v3.py — BP-02 1.3.198 + RP-01 1.3.107 (D-C350, his p16 results 20:52 CT 09-30, 22/25 PASS).

Layered on the v2 builds (_build/bp02-197, _build/rp01-106), every change from his p16 notes / FAILs:
  RP-01 1.3.107
    - leaf colour tiles 256 px (Patrix 26.2 256x basic, the same CTM tile picks), normal 128 (unchanged), MERS 64 (2x2 mean of the
      128 MERS) — his m01-m10 pick "256x with 64x MERS", all species
    - falling-canopy / particle tiles keep the leaf's see-through pixels (n07 FAIL: 1.3.106 made them alpha 255, so the canopy entity
      (material entity_alphatest) drew solid green slabs and its cards as thick rods)
  BP-02 1.3.198
    - shears drop OUR leaf block pw:<species>_leaves (n09 FAIL: the loot gave minecraft:<species>_leaves, which draws the old look)
    - relook sweep removed (his m08 note: "relook will be unnecessary - all new trees from now on")
    - random picture turns off (isotropic removed; his n10: "can't tell difference - accept whatever is cheaper")
Not here (waits for the p17 culling probe): the z-clipping fix.
"""
import json, re, shutil, sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML
import build_leaf_pilot_rp as B
import build_leaf_rollout as R

ROOT = Path("/home/claude")
BP_SRC, BP, BP_VER = ROOT / "_build/bp02-197", ROOT / "_build/bp02-198", [1, 3, 198]
RP_SRC, RP, RP_VER = ROOT / "_build/rp01-106", ROOT / "_build/rp01-107", [1, 3, 107]
DATE = "2026-09-30"
ALL = R.ALL


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT {time.strftime('%m-%d')}] BUILD leaf-v3: {m}\n")


def to256(p): return Path(str(p).replace("patrix262_basic", "patrix262_256"))


def half(a):
    h, w = a.shape[:2]
    return a.reshape(h // 2, 2, w // 2, 2, 4).astype(float).mean((1, 3)).round().astype(np.uint8)


def build_rp():
    if RP.exists(): shutil.rmtree(RP)
    shutil.copytree(RP_SRC, RP)
    d = RP / "textures/blocks/pw_leaves2"; n = 0; sizes = set()
    for s in ALL:
        faces, cards = B.tile_lists(s)
        nf = 6 if s == "spruce" else 5
        for kind, lst, cnt in (("f", faces, nf), ("c", cards, 4)):
            for i in range(cnt):
                src = lst[i]; name = f"{s}_{kind}{i}"
                col = B.painted(B.rgba(to256(src)))
                mers = half(B.mers_156(B.rgba(B.sibling(src, "_s"))))
                assert (d / f"{name}_n.png").exists() and (d / f"{name}.texture_set.json").exists(), name
                B.save(col, d / f"{name}.png"); B.save(mers, d / f"{name}_mers.png")
                sizes.add((col.shape[0], B.rgba(d / f"{name}_n.png").shape[0], mers.shape[0])); n += 1
        # falling canopy + particle: pre-coloured where Java tints, see-through pixels KEPT (alpha test cuts them like the block)
        fall = R.P.colour(to256(faces[0]), s) if s in R.TINT else B.rgba(to256(faces[0]))
        B.save(B.painted(np.asarray(fall).astype(np.uint8)), d / f"{s}_fall.png")
    man = RP / "manifest.json"; m = json.loads(man.read_text(encoding="utf-8-sig"))
    m["header"]["version"] = RP_VER; m["header"]["name"] = "AbsolutRealism Tectonic RP v1.3.107"
    for mod in m["modules"]: mod["version"] = RP_VER
    m["header"]["description"] = (f"v1.3.107 ({DATE}) LEAVES 256: every leaf tile at 256 px (Patrix 26.2 256x), normal maps 128, MERS 64 "
        "(his p16 pick); the falling canopy keeps the leaves' see-through pixels again (no solid green slabs). Pairs with BP-02 v1.3.198. "
        "Includes all of v1.3.106.")
    man.write_text(json.dumps(m, indent=1))
    log(f"RP-01 1.3.107: {n} leaf tiles -> colour/normal/MERS sizes {sorted(sizes)}; 11 fall tiles see-through again")
    return n, sizes


NUDGE = "--nudge" in sys.argv          # Z1 option B (his GO pending): a 3-way position nudge so touching leaves never share a plane
NUDGE_S = 0.006                         # block per step; offsets k*(1,2,3)*S, k = -3..3: the (1,2,3) direction has a non-zero part along every face / card normal
NUDGE_T = {o: [round((o - 3) * NUDGE_S * a, 4) for a in (1, 2, 3)] for o in range(7)}
NUDGE_JS = r'''// v1.3.198 LEAF NUDGE (D-C350, Z1 option B): neighbouring leaves never share a plane (z-clipping, his p16 note). pw:off =
// (x + 2y + 4z) mod 7 picks one of seven tiny shifts (k-3)*(1,2,3)*0.006 block: two leaves that touch on a face OR on an edge (the
// diagonal card twins) always get different shifts, so their cube faces and cards are never coplanar. Set with the look (onPlace +
// the scanner's assign-once); unscanned leaves keep 0, like their look.
function pwNudge(loc) { return (((Math.floor(loc.x) + 2 * Math.floor(loc.y) + 4 * Math.floor(loc.z)) % 7) + 7) % 7; }
'''


def nudge_perms(perms):
    out = []
    for pm in perms:
        for o in range(7):
            comp = json.loads(json.dumps(pm["components"]))
            tr = comp.get("minecraft:transformation", {})
            rot = tr.get("rotation", [0, 0, 0])
            if o != 3 or rot != [0, 0, 0]:
                comp["minecraft:transformation"] = {"rotation": rot, "translation": NUDGE_T[o]} if o != 3 else {"rotation": rot}
            out.append({"condition": f"{pm['condition']} && q.block_state('pw:off') == {o}", "components": comp})
    return out


def build_bp():
    if BP.exists(): shutil.rmtree(BP)
    shutil.copytree(BP_SRC, BP)
    iso = 0
    for s in ALL:
        p = BP / f"blocks/{s}_leaves.json"; d = ML._parse_json(p.read_text(encoding="utf-8"))
        for pm in d["minecraft:block"]["permutations"]:
            for mi in pm["components"]["minecraft:material_instances"].values():
                if mi.pop("isotropic", None) is not None: iso += 1
        if NUDGE:
            blk = d["minecraft:block"]; blk["description"]["states"]["pw:off"] = list(range(7))
            blk["permutations"] = nudge_perms(blk["permutations"])
        p.write_text(json.dumps(d, indent=2), encoding="utf-8")
        lp = BP / f"loot_tables/blocks/{s}_leaves.json"; L = json.loads(lp.read_text(encoding="utf-8"))
        shears = [pl for pl in L["pools"] if any(c.get("condition") == "match_tool" and c.get("item") == "minecraft:shears" for c in pl.get("conditions", []))]
        assert len(shears) == 1 and shears[0]["entries"][0]["name"] == f"minecraft:{s}_leaves", (s, shears)
        shears[0]["entries"][0]["name"] = f"pw:{s}_leaves"
        lp.write_text(json.dumps(L, indent=2), encoding="utf-8")
    mp = BP / "scripts/main.js"; t = mp.read_text(encoding="utf-8")
    a = t.index("// v1.3.197 RELOOK SWEEP (D-C347)"); a = t.rindex("// =====", 0, a)
    b = t.index("}, PW_RELOOK_INTERVAL);\n", a) + len("}, PW_RELOOK_INTERVAL);\n")
    t = t[:a] + "// v1.3.198: the relook sweep (v1.3.197) is removed — his p16 ruling: every tree from now on is a new tree.\n" + t[b:]
    assert "_relookJob" not in t and "PW_RELOOK" not in t
    if NUDGE:
        a1 = '    let newPerm = block.permutation.withState("pw:variant", choice);\n'
        assert t.count(a1) == 1
        t = t.replace(a1, a1 + '    try { if (PW_LEAF_TYPES_DECAY.has(block.typeId)) newPerm = newPerm.withState("pw:off", pwNudge(block.location)); } catch { /* no pw:off */ }\n')
        a2 = 'block.setPermutation(block.permutation.withState("pw:variant", target).withState("pw:rseed", true));'
        assert t.count(a2) == 1
        t = t.replace(a2, 'block.setPermutation(block.permutation.withState("pw:variant", target).withState("pw:rseed", true).withState("pw:off", pwNudge(block.location)));')
        a3 = "function pickVariantForBlock(block) {"
        assert t.count(a3) == 1
        t = t.replace(a3, NUDGE_JS + "\n" + a3)
    assert t.count('const PW_BUILD = "1.3.197";') == 1
    t = t.replace('const PW_BUILD = "1.3.197";', 'const PW_BUILD = "1.3.198";')
    mp.write_text(t, encoding="utf-8")
    man = BP / "manifest.json"; m = json.loads(man.read_text(encoding="utf-8-sig"))
    m["header"]["version"] = BP_VER; m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.198"
    for mod in m["modules"]: mod["version"] = BP_VER
    m["header"]["description"] = (f"v1.3.198 ({DATE}) LEAF FIXES from p16: shears drop our pw: leaf block (it picks its look when placed); "
        "the relook sweep is gone (all trees are new); random picture turns off (cheaper, no visible difference). Pairs with RP-01 v1.3.107. "
        "Includes all of v1.3.197.")
    man.write_text(json.dumps(m, indent=1))
    log(f"BP-02 1.3.198: 11 leaf loot tables -> shears drop pw:<species>_leaves; isotropic removed from {iso} material instances; relook sweep removed")
    return iso


if __name__ == "__main__":
    build_bp(); build_rp()
