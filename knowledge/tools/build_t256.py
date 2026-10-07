#!/usr/bin/env python3
"""build_t256.py — the 128 vs 256 leaf comparison (his 19:33 / 19:41 CT 09-30, D-C348).

PW-TestRunner RP v0.5.0 = RP v0.4.0 (the pilot) + two test tile sets for all 11 leaf species:
  textures/blocks/pw_t256/   colour 256 px (Patrix 26.2 256x basic, same CTM tile picks as RP-01 1.3.106) + normal 128 + MERS 128
  textures/blocks/pw_t256m/  colour 256 px + normal 128 + MERS  64 (MERS halved: his 19:41 pick "MERS or normal to 64x, only 1")
  terrain keys pw_t256_<s>_f<i>/c<i> and pw_t256m_<s>_f<i>/c<i>; colour gets the same 'painted' see-through fill as RP-01 1.3.106.
_build/t256-blocks/: 22 test blocks pw:t256_<s>_leaves + pw:t256m_<s>_leaves = BP-02 1.3.197's own leaf block, identifier + texture
  keys swapped, custom component + loot removed (the runner sets each leaf's look itself). Geometry stays RP-01 1.3.106's pw_leaves2.
"""
import json, shutil, sys, time
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
import build_leaf_pilot_rp as B

ROOT = Path("/home/claude")
SRC_RP, RP, RP_VER = ROOT / "_build/testrunner-rp-0.4.0", ROOT / "_build/testrunner-rp-0.5.0", [0, 5, 0]
BP02 = ROOT / "_build/bp02-197"
BLK = ROOT / "_build/t256-blocks"
DATE = "2026-09-30"
ALL = ("oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "mangrove", "cherry", "pale_oak", "azalea", "flowering_azalea")
SETS = {"t256": 128, "t256m": 64}            # set -> MERS size (normal stays 128 in both)


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT {time.strftime('%m-%d')}] BUILD t256: {m}\n")


def to256(p): return Path(str(p).replace("patrix262_basic", "patrix262_256"))


def half(a):
    """2x2 box average, channel by channel (no alpha premultiply: MERS alpha is subsurface, not coverage)"""
    h, w = a.shape[:2]
    return a.reshape(h // 2, 2, w // 2, 2, 4).astype(float).mean((1, 3)).round().astype(np.uint8)


def build_rp():
    if RP.exists(): shutil.rmtree(RP)
    shutil.copytree(SRC_RP, RP)
    ttp = RP / "textures/terrain_texture.json"; tdoc = json.loads(ttp.read_text(encoding="utf-8-sig")); tt = tdoc["texture_data"]
    sizes = {}; n = 0
    for s in ALL:
        faces, cards = B.tile_lists(s)
        nf = 6 if s == "spruce" else 5
        for kind, lst, cnt in (("f", faces, nf), ("c", cards, 4)):
            for i in range(cnt):
                src = lst[i]; big = to256(src); name = f"{s}_{kind}{i}"
                col = B.painted(B.rgba(big))
                nrm = B.normal_156(B.rgba(B.sibling(src, "_n")))
                mers = B.mers_156(B.rgba(B.sibling(src, "_s")))
                assert col.shape[0] == 2 * nrm.shape[0] == 2 * mers.shape[0], (s, name, col.shape, nrm.shape)
                for st, msize in SETS.items():
                    d = RP / f"textures/blocks/pw_{st}"
                    m = mers if msize == mers.shape[0] else half(mers)
                    assert m.shape[0] == msize, (name, m.shape)
                    B.save(col, d / f"{name}.png"); B.save(nrm, d / f"{name}_n.png"); B.save(m, d / f"{name}_mers.png")
                    ts = {"color": name, "normal": f"{name}_n", "metalness_emissive_roughness_subsurface": f"{name}_mers"}
                    (d / f"{name}.texture_set.json").write_text(json.dumps({"format_version": "1.21.30", "minecraft:texture_set": ts}, indent=1))
                    tt[f"pw_{st}_{s}_{kind}{i}"] = {"textures": f"textures/blocks/pw_{st}/{name}"}
                    sizes[st] = (col.shape[0], nrm.shape[0], m.shape[0])
                n += 1
    ttp.write_text(json.dumps(tdoc, indent=1))
    bj = RP / "blocks.json"; bjd = json.loads(bj.read_text(encoding="utf-8-sig")) if bj.exists() else {"format_version": [1, 1, 0]}
    lang = RP / "texts/en_US.lang"; lt = lang.read_text(encoding="utf-8").rstrip("\n"); add = []
    for s in ALL:
        nice = s.replace("_", " ").title()
        for st, label in (("t256", "256 test"), ("t256m", "256 test, MERS 64")):
            bjd[f"pw:{st}_{s}_leaves"] = {"sound": "grass"}
            add.append(f"tile.pw:{st}_{s}_leaves.name={nice} Leaves ({label})")
    bj.write_text(json.dumps(bjd, indent=1))
    lang.write_text(lt + "\n" + "\n".join(add) + "\n", encoding="utf-8")
    man = RP / "manifest.json"; m = json.loads(man.read_text(encoding="utf-8-sig"))
    m["header"]["version"] = RP_VER; m["header"]["name"] = "PW Test Runner RP v0.5.0"
    for mod in m["modules"]: mod["version"] = RP_VER
    m["header"]["description"] = (f"v0.5.0 ({DATE}) TEST RUNNER RP — the 128 vs 256 LEAF COMPARISON: pw:t256_<species>_leaves (Patrix 26.2 "
        "256 px colour + 128 normal + 128 MERS) and pw:t256m_<species>_leaves (256 colour + 128 normal + 64 MERS) for all 11 leaf species, "
        "using RP-01 v1.3.106's leaf shapes. Plus everything of v0.4.0 (the pilot leaves, pw:probe, the XPACK keys). Declares Vibrant Visuals "
        "(pbr). Job-only: attach at the TOP of the Resource Packs list while testing.")
    man.write_text(json.dumps(m, indent=1))
    log(f"RP v0.5.0: {n} tiles x 2 sets = {2 * n} texture sets; sizes colour/normal/MERS {sizes}; 22 blocks.json entries + names")
    return n


def build_blocks():
    if BLK.exists(): shutil.rmtree(BLK)
    BLK.mkdir(parents=True)
    out = []
    for s in ALL:
        src = json.loads((BP02 / f"blocks/{s}_leaves.json").read_text(encoding="utf-8"))
        for st in SETS:
            d = json.loads(json.dumps(src)); blk = d["minecraft:block"]
            ident = f"pw:{st}_{s}_leaves"; blk["description"]["identifier"] = ident
            c = blk["components"]; c.pop("minecraft:custom_components", None); c.pop("minecraft:loot", None)
            txt = json.dumps(d)
            assert txt.count("pw_leaves2_") > 0
            txt = txt.replace(f'"pw_leaves2_{s}_', f'"pw_{st}_{s}_')
            assert f'"pw_leaves2_{s}_' not in txt and txt.count(f'"pw_{st}_{s}_') >= 9 and "custom_components" not in txt, (ident, txt[:200])
            (BLK / f"{st}_{s}_leaves.json").write_text(json.dumps(json.loads(txt), indent=1))
            out.append(ident)
    log(f"{len(out)} test blocks -> {BLK} (BP-02 1.3.197 leaf blocks, keys -> pw_t256*/pw_t256m*, no custom component, no loot)")
    return out


if __name__ == "__main__":
    build_rp(); build_blocks()
