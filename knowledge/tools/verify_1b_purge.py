#!/usr/bin/env python3
"""verify_1b_purge.py — gate for the 1b renames + purge trees (rp03-59 / rp04-136 / rp01-104 / rp05-48); packages on GATE OPEN."""
import json, re, sys, hashlib, zipfile, subprocess, collections
from pathlib import Path
from PIL import Image
import numpy as np
sys.path.insert(0, "/home/claude/tools")
import purge_harvest as ph, block_census as BC
ROOT = Path("/home/claude"); OUT = Path("/mnt/user-data/outputs"); DATE = "2026-09-22"
PACKS = {"RP-03": (ROOT / "_build/rp03-58", ROOT / "_build/rp03-59", [1, 3, 59], "RP-03-AbsolutRealism-PBR-RP-v1_3_59.mcpack"),
         "RP-04": (ROOT / "_build/rp04-135", ROOT / "_build/rp04-136", [1, 3, 136], "RP-04-AbsolutRealism-Basic-RP-v1_3_136.mcpack"),
         "RP-01": (ROOT / "_build/rp01-103", ROOT / "_build/rp01-104", [1, 3, 104], "RP-01-AbsolutRealism-Tectonic-RP-v1_3_104.mcpack"),
         "RP-05": (ROOT / "_build/rp05-47", ROOT / "_build/rp05-48", [1, 3, 48], "RP-05-AbsolutRealism-Flora-RP-v1_3_48.mcpack")}
def load(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
results = []
def check(name, ok, detail=""):
    results.append((name, bool(ok), detail)); print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  -> {str(detail)[:300]}"))

rep = load(ROOT / "_logs/purge_report.json"); added = rep["added"]; report = rep["report"]; twin = load(ROOT / "_logs/twin_map_1b.json")
van = ph.vanilla_stems()
# A manifests
for tag, (src, dst, ver, outname) in PACKS.items():
    m = load(dst / "manifest.json"); v = ".".join(map(str, ver))
    check(f"A {tag} manifest v{v} + description stamp", m["header"]["version"] == ver and all(x["version"] == ver for x in m["modules"]) and m["header"]["description"].startswith(f"v{v} ({DATE})") and f"v{v}" in m["header"]["name"], m["header"]["name"])
# B added files exist; renames pixel-identical to their Java source (from the OLD tree)
missing = []; mism = []
for tag, lst in added.items():
    for stem in lst:
        p = PACKS[tag][1] / f"{stem}.png"
        if not p.exists(): missing.append(f"{tag}:{stem}")
check(f"B every added texture exists ({sum(len(v) for v in added.values())} files)", not missing, missing[:10])
for path, r in twin.items():
    if r["action"] == "RENAME" and r["tag"] == "CURRENT":
        a = PACKS[r["source"]][1] / f"{path}.png"; b = PACKS[r["source"]][0] / f"textures/blocks/{r['java']}.png"
        if hashlib.md5(a.read_bytes()).hexdigest() != hashlib.md5(b.read_bytes()).hexdigest(): mism.append(path)
check("B 110 renames are byte-identical copies of their Java-named sources", not mism, mism[:10])
# C texture sets resolve inside their tree
dangling = []; nsets = 0
for tag, (src, dst, ver, outname) in PACKS.items():
    for ts in dst.rglob("*.texture_set.json"):
        nsets += 1
        try: d = load(ts)["minecraft:texture_set"]
        except Exception as e: dangling.append((str(ts), "unparsable")); continue
        for k, v in d.items():
            if not isinstance(v, str): continue
            q = (dst / v) if v.startswith("textures/") else (ts.parent / v)
            if not any(q.with_suffix(ext).exists() for ext in (".png", ".tga", ".jpg")): dangling.append((tag, ts.name, k, v))
check(f"C every texture set resolves ({nsets} sets, 4 trees)", not dangling, dangling[:8])
# D nothing deleted is vanilla-named or pw/am-named; nothing deleted is referenced by any JSON in the stack (harvest on the new trees)
bad = []
for tag, r in report.items():
    for f in r["deleted"]:
        stem = f.rsplit(".", 1)[0] if not f.endswith(".texture_set.json") else None
        if stem and (stem in van or ph.OURS_RE.search(stem)): bad.append(f"{tag}:{f}")
check("D no vanilla-named or pw/am-named file was deleted", not bad, bad[:10])
ph.TREES = {t: PACKS[t][1] for t in PACKS}
h = ph.main(out_json=ROOT / "_logs/purge_harvest_verify.json")
refd = []
for tag, r in report.items():
    for f in r["deleted"]:
        stem = f.rsplit(".", 1)[0] if not f.endswith(".texture_set.json") else None
        if stem and stem in h["refs"]: refd.append((tag, f, list(h["refs"][stem])[:3]))
check("D no deleted texture is referenced by any JSON in any stack pack", not refd, refd[:8])
left = collections.Counter()
for tag in PACKS:
    for s, v in h["trees"][tag]["candidates"].items():
        b, suf = ph.base_of(s)
        kept_unique = {x for x, y in h["trees"][tag]["candidates"].items() if y["class"] == "UNIQUE"}
        cls = v["class"]
        if s.endswith("_backup") or s.startswith("textures/entity/fallingtree/"): left[f"{tag}:{cls}"] += 1
        elif cls in ("DUP", "CONSUMED", "COMPANION-DEAD") and not (b in kept_unique): left[f"{tag}:{cls}"] += 1
check("D post-purge harvest: no DUP / CONSUMED / COMPANION-DEAD / BACKUP / fallingtree-dead file remains", not left, dict(left))
# E every JSON texture reference of the rebuilt packs resolves somewhere in the stack or vanilla
zips = ph.stack_zip_packs(); others = {k: ph.tree_pack(k, v) for k, v in ph.OTHER_TREES.items()}
allstems = set(van)
for p in list(zips) + list(others.values()): allstems |= set(p.tex)
trees = {t: ph.tree_pack(t, PACKS[t][1]) for t in PACKS}
for p in trees.values(): allstems |= set(p.tex)
unres = []
for tag, p in trees.items():
    for stem, js in p.refs.items():
        if stem.startswith("textures/") and stem not in allstems and not stem.endswith("/"): unres.append((tag, stem, sorted(js)[0]))
before_unres = set()
oldtrees = {t: ph.tree_pack(t, PACKS[t][0]) for t in PACKS}
oldall = set(van) | {s for p in list(zips) + list(others.values()) for s in p.tex} | {s for p in oldtrees.values() for s in p.tex}
for tag, p in oldtrees.items():
    for stem in p.refs:
        if stem.startswith("textures/") and stem not in oldall: before_unres.add((tag, stem))
new_unres = [u for u in unres if (u[0], u[1]) not in before_unres]
check(f"E no NEW unresolved texture reference in the rebuilt packs ({len(before_unres)} pre-existing unresolved refs unchanged)", not new_unres, new_unres[:8])
for c in ["white", "silver", "black"]:
    check(f"E RP-04 JSON no longer references the Java wool name ({c})", f"textures/blocks/{'light_gray' if c == 'silver' else c}_wool" not in trees["RP-04"].refs)
# F textures_list.json exact
for tag in ("RP-04", "RP-05"):
    dst = PACKS[tag][1]; lst = load(dst / "textures/textures_list.json")
    actual = sorted({str(q.relative_to(dst)).replace("\\", "/").rsplit(".", 1)[0] for q in dst.rglob("*") if q.is_file() and q.suffix.lower() in (".png", ".tga", ".jpg", ".jpeg") and str(q.relative_to(dst)).startswith("textures/")})
    check(f"F {tag} textures_list.json == tree ({len(actual)} entries, no duplicates)", lst == actual and len(lst) == len(set(lst)), (len(lst), len(actual)))
# G derived images
E = PACKS["RP-04"][1] / "textures/entity"; B4 = PACKS["RP-04"][1] / "textures/blocks"
bad = []
for c in ["white", "silver", "undyed", "black"]:
    ent = Image.open(E / "shulker" / f"shulker_{c}.png").convert("RGBA"); top = Image.open(B4 / f"shulker_top_{c}.png").convert("RGBA")
    crop = ent.crop((ent.width // 4, 0, ent.width // 2, ent.height // 4))
    if crop.tobytes() != top.tobytes(): bad.append(c)
check("G shulker tops == lid-top crops of the entity textures (vanilla's own construction)", not bad, bad)
for n in ("chain1", "chain2", "copper_chain1", "weathered_copper_chain2"):
    a = np.array(Image.open(B4 / f"{n}.png").convert("RGBA")); s = a.shape[1] // 16
    cols = [c for c in range(a.shape[1]) if (a[:, c, 3] > 0).any()]
    check(f"G {n}: art only in the first 3 texels (cols {min(cols)}..{max(cols)} of {a.shape[1]})", max(cols) < 3 * s and a.shape[1] == 128)
for n in ("chest_front", "chest_side", "chest_top", "trapped_chest_front", "ender_chest_front", "copper_chest_inventory_top", "weathered_copper_chest_inventory_side"):
    a = np.array(Image.open(B4 / f"{n}.png").convert("RGBA"))
    check(f"G {n} 128x128 opaque icon", a.shape[:2] == (128, 128) and (a[..., 3] == 255).mean() > 0.99, (a.shape, float((a[..., 3] == 255).mean())))
cf = Image.open(B4 / "campfire.png"); sf = Image.open(B4 / "soul_campfire.png")
fb = load(PACKS["RP-04"][1] / "textures/flipbook_textures.json"); ent = {e["atlas_tile"]: e for e in fb if "atlas_tile" in e}
check("G campfire / soul_campfire strips 128x3840 with 30-frame flipbook entries", cf.size == (128, 3840) and sf.size == (128, 3840) and ent["campfire_fire"]["frames"] == list(range(30)) and ent["soul_campfire_fire"]["frames"] == list(range(30)))
check("G dried ghast 4 states x 7 textures present", all((B4 / f"dried_ghast_state_{n}_{f}.png").exists() for n in (1, 2, 3, 4) for f in ("front", "back", "left", "right", "top", "bottom", "tentacles")))
# H census on the new trees
new = BC.main(str(ROOT / "_packs/STACK-LIST-2026-09-21.txt"), str(ROOT / "_logs/block_census_1b.json"), str(ROOT / "_docs/BLOCK-CENSUS-2026-09-22-1b.md"),
              overrides={t: str(PACKS[t][1]) for t in PACKS})
old = load(ROOT / "_logs/block_census_e2.json")["blocks"]
regressed = [b for b, v in old.items() if v["class"] == "ALL-OURS" and new.get(b, {}).get("class") != "ALL-OURS"]
check("H census: no block that was ALL-OURS regressed", not regressed, regressed[:10])
check("H census: no BROKEN block", not [b for b, v in new.items() if v["class"] == "BROKEN"], [b for b, v in new.items() if v["class"] == "BROKEN"][:10])
co, cn = collections.Counter(v["class"] for v in old.values()), collections.Counter(v["class"] for v in new.values())
check(f"H census: ALL-OURS {co['ALL-OURS']} -> {cn['ALL-OURS']}, MIXED {co['MIXED']} -> {cn['MIXED']}, ALL-VANILLA {co['ALL-VANILLA']} -> {cn['ALL-VANILLA']}", cn["ALL-OURS"] > co["ALL-OURS"] and cn["ALL-VANILLA"] < co["ALL-VANILLA"])
stillvan = []
for path, r in twin.items():
    if r["tag"] == "CURRENT" and r["action"] in ("RENAME", "PULL", "DERIVE"):
        for blk in r["live_blocks"]:
            for s in new[blk]["slots"]:
                if s["path"] == path and s["provider"] == "VANILLA": stillvan.append(path)
check("H every CURRENT rename/pull/derive slot now resolves to one of our packs", not stillvan, sorted(set(stillvan))[:10])
exp_all_ours = ["white_stained_glass", "light_gray_stained_glass_pane", "white_wool_slab", "light_gray_wool", "light_gray_carpet", "golden_rail", "anvil", "chipped_anvil", "quartz_pillar", "chiseled_quartz_block", "crimson_door", "warped_trapdoor", "crimson_stem", "candle", "potatoes", "cocoa", "nether_wart", "honey_block", "honeycomb_block", "slime", "wet_sponge", "mob_spawner", "web", "noteblock", "packed_ice", "redstone_lamp", "stonecutter_block", "white_shulker_box", "undyed_shulker_box", "chest", "trapped_chest", "ender_chest", "copper_chest", "chain", "copper_chain", "frame", "closed_eyeblossom", "quartz_ore", "silver_glazed_terracotta", "enchanting_table", "sculk_sensor", "sculk_shrieker", "azalea", "crimson_roots", "warped_roots"]
notours = [b for b in exp_all_ours if new.get(b, {}).get("class") != "ALL-OURS"]
check(f"H {len(exp_all_ours)} named blocks are ALL-OURS now", not notours, [(b, new.get(b, {}).get("class")) for b in notours])
cfv = sorted({s["path"].split("/")[-1] for b in ("campfire", "soul_campfire") for s in new[b]["slots"] if s["provider"] == "VANILLA"})
check(f"H campfire / soul_campfire: flame slots ours, only the log textures still vanilla ({cfv})", cfv == ["campfire_log", "campfire_log_lit", "soul_campfire_log_lit"])
failed = [n for n, ok, _ in results if not ok]
if failed: print(f"\nGATE CLOSED — {failed}"); sys.exit(1)
outs = []
for tag, (src, dst, ver, outname) in PACKS.items():
    out = OUT / outname
    if out.exists(): out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(dst.rglob("*")):
            if p.is_file(): z.write(p, str(p.relative_to(dst)).replace("\\", "/"))
    with zipfile.ZipFile(out) as z: zh = {n: hashlib.md5(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith("/")}
    th = {str(p.relative_to(dst)).replace("\\", "/"): hashlib.md5(p.read_bytes()).hexdigest() for p in dst.rglob("*") if p.is_file()}
    assert zh == th, "zip content mismatch"
    outs.append((tag, outname, out.stat().st_size, hashlib.md5(out.read_bytes()).hexdigest()))
print(f"\nGATE OPEN — {len(results)} checks passed")
for tag, n, sz, md in outs: print(f"  {n} {sz:,} B md5 {md}")
json.dump({"checks": len(results), "outputs": outs, "census": {k: cn[k] for k in cn}}, open(ROOT / "_logs/v1_1b_purge_gate.json", "w"), indent=1)
