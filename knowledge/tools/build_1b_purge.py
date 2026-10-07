#!/usr/bin/env python3
"""build_1b_purge.py — NAME AUDIT phase 1b (renames + derivations) and the DEAD-WEIGHT PURGE in one version bump per pack
(ruling 17:08 CT, D-C219):  RP-03 v1.3.58 -> .59 · RP-04 v1.3.135 -> .136 · RP-01 v1.3.103 -> .104 · RP-05 v1.3.47 -> .48.

Phase 1b (from _logs/twin_map_1b.json, tools/twin_map_1b.py):
  RENAME  110 CURRENT slots whose Patrix twin already sits in the stack under a Java name -> copied under the Bedrock name
          with its PBR companions (build_phase1.copy_with_companions); same-pack JSON references to the Java name are
          re-pointed to the Bedrock name (RP-04 wool x16, packed_ice) so the Java copy can go.
  PULL    campfire <- RP-04's own pw_hearth_flame strip (= Patrix fire_0, 30 frames — Patrix's campfire model burns fire_0);
          soul_campfire <- Patrix soul_fire_0 (128x3840, pulled); + RP-04 flipbook entries for campfire_fire / soul_campfire_fire.
  DERIVE  shulker_top_<c> x17 = the lid's top face cropped from entity/shulker/shulker_<c> (vanilla shulker_top_white IS that crop, diff 0.00);
          chest / trapped_chest / ender_chest / copper_chest_inventory x4 icons = lid+base front / side / top faces of the E2 entity textures,
          composited 14x15 (+knob) and resized to 16x16 (x8) — inventory icons only;
          chain1/chain2, <state>_copper_chain1/2 = the two 3-px planes of Java's chain.png split into Bedrock's two files;
          dried_ghast_state_N+1_<face> <- dried_ghast_hydration_N_<face'> (front<-north, back<-south, left<-west, right<-east — ASSUMPTION, witness);
          ALIASES (faces vanilla shows only from below / potted twins): honey_top+bottom <- honey_block_side; sculk_{catalyst,sensor,shrieker}_bottom <- sculk;
          enchanting_table_bottom <- obsidian; stonecutter2_bottom <- stone; potted_azalea_bush_{side,top,plant} <- azalea_*;
          potted_flowering_azalea_bush_{side,top} <- flowering_azalea_*; crimson_roots_pot <- crimson_roots; warped_roots_pot <- warped_roots.
Purge (tools/purge_harvest.py re-run on the NEW trees): DUP, CONSUMED, COMPANION-DEAD (of purged/absent stems), dead texture sets,
  BACKUP (*_backup), OURS-DEAD (unreferenced textures/entity/fallingtree/* — an earlier BIGCANOPY iteration).  UNIQUE (+ their companions
  and sets) and every pw_/am_ file are KEPT and listed (_logs/purge_report.json).  textures_list.json regenerated where a pack ships one.
"""
import json, re, shutil, sys, datetime, collections
from pathlib import Path
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
import build_phase1 as bp
import purge_harvest as ph

ROOT = Path("/home/claude"); DATE = "2026-09-22"; LOG = ROOT / "_logs/phase_log.md"
def log(m): LOG.open("a").write(f"[{datetime.datetime.now().strftime('%H:%M')} CT 09-22] BUILD 1B/PURGE — {m}\n")
jload, jdump = bp.jload, bp.jdump
PACKS = {  # tag: (source tree, dest tree, new version, name template)
    "RP-03": (ROOT / "_build/rp03-58", ROOT / "_build/rp03-59", (1, 3, 59), "AbsolutRealism PBR RP v{v}"),
    "RP-04": (ROOT / "_build/rp04-135", ROOT / "_build/rp04-136", (1, 3, 136), "AbsolutRealism Basic RP v{v}"),
    "RP-01": (ROOT / "_build/rp01-103", ROOT / "_build/rp01-104", (1, 3, 104), "AbsolutRealism Tectonic RP v{v}"),
    "RP-05": (ROOT / "_build/rp05-47", ROOT / "_build/rp05-48", (1, 3, 48), "AbsolutRealism Flora RP v{v}"),
}
PULL = ROOT / "_intake/patrix128/pull1b/assets/minecraft/textures/block"
COLOURS = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", "silver", "cyan", "purple", "blue", "brown", "green", "red", "black"]
ALIASES = [  # (pack, bedrock stem, java/source stem)
    ("RP-03", "honey_top", "honey_block_side"), ("RP-03", "honey_bottom", "honey_block_side"),
    ("RP-03", "sculk_catalyst_bottom", "sculk"), ("RP-03", "sculk_sensor_bottom", "sculk"), ("RP-03", "sculk_shrieker_bottom", "sculk"),
    ("RP-03", "enchanting_table_bottom", "obsidian"), ("RP-03", "stonecutter2_bottom", "stone"),
    ("RP-05", "potted_azalea_bush_side", "azalea_side"), ("RP-05", "potted_azalea_bush_top", "azalea_top"), ("RP-05", "potted_azalea_bush_plant", "azalea_plant"),
    ("RP-05", "potted_flowering_azalea_bush_side", "flowering_azalea_side"), ("RP-05", "potted_flowering_azalea_bush_top", "flowering_azalea_top"),
    ("RP-05", "crimson_roots_pot", "crimson_roots"), ("RP-05", "warped_roots_pot", "warped_roots"),
]
GHAST_FACES = {"front": "north", "back": "south", "left": "west", "right": "east", "top": "top", "bottom": "bottom"}
CHEST_ICONS = {  # bedrock icon stem prefix -> entity chest texture
    "chest": "normal", "trapped_chest": "trapped", "ender_chest": "ender", "copper_chest_inventory": "copper_default",
    "exposed_copper_chest_inventory": "copper_exposed", "oxidized_copper_chest_inventory": "copper_oxidized", "weathered_copper_chest_inventory": "copper_weathered"}

def derive(src_png, dst_png, fn, manifest, src_set=None):
    """dst = fn(src) for the colour AND every companion the source texture set references (or bare companions); new set with bare stems."""
    src_png, dst_png = Path(src_png), Path(dst_png); dst_png.parent.mkdir(parents=True, exist_ok=True)
    fn(Image.open(src_png).convert("RGBA")).save(dst_png); manifest.append(dst_png)
    sdir, sstem = src_png.parent, src_png.name[:-4]; dstem = dst_png.name[:-4]
    ts = sdir / f"{sstem}.texture_set.json" if src_set is None else Path(src_set)
    if ts.exists():
        d = jload(ts); t = d["minecraft:texture_set"]
        for k, v in list(t.items()):
            if not isinstance(v, str): continue
            if k == "color": t[k] = dstem; continue
            m = bp.COMP_RE.search(v); suffix = m.group(1) if m else f"_{k[:3]}"
            own = sdir / f"{sstem}{suffix}.png"; ref = sdir / f"{v}.png"
            src_c = own if own.exists() else (ref if ref.exists() else None)
            if src_c is None: del t[k]; continue
            out = dst_png.parent / f"{dstem}{suffix}.png"
            fn(Image.open(src_c).convert("RGBA")).save(out); manifest.append(out); t[k] = f"{dstem}{suffix}"
        jdump(d, dst_png.parent / f"{dstem}.texture_set.json"); manifest.append(dst_png.parent / f"{dstem}.texture_set.json")
    else:
        for suf in bp.COMPANIONS:
            c = sdir / f"{sstem}{suf}.png"
            if c.exists():
                out = dst_png.parent / f"{dstem}{suf}.png"; fn(Image.open(c).convert("RGBA")).save(out); manifest.append(out)

def chest_icon(ent, which):
    """16x16(x s) inventory icon from a Bedrock-layout chest entity texture (64x64 x s): lid 14x5x14 @0,0, base 14x10x14 @0,19, knob 2x4x1 @0,0."""
    s = ent.width // 64
    def R(x0, y0, x1, y1): return ent.crop((x0 * s, y0 * s, x1 * s, y1 * s))
    if which == "top":
        face = R(14, 0, 28, 14)                                     # lid up
    else:
        if which == "front": lid, base = R(14, 14, 28, 19), R(14, 33, 28, 43)     # north regions
        else: lid, base = R(0, 14, 14, 19), R(0, 33, 14, 43)                      # west regions (both sides alike)
        face = Image.new("RGBA", (14 * s, 15 * s), (0, 0, 0, 0)); face.paste(lid, (0, 0)); face.paste(base, (0, 5 * s))
        if which == "front":
            knob = R(1, 1, 3, 5); face.paste(knob, (6 * s, 3 * s), knob)          # latch over the seam
    return face.resize((16 * s, 16 * s), Image.LANCZOS)

def chain_plane(im, plane):
    """Java chain.png: plane 0 = columns 0..3, plane 1 = columns 3..6 (of 16); Bedrock chainN = that plane at columns 0..3."""
    s = im.width // 16; out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(im.crop((plane * 3 * s, 0, (plane + 1) * 3 * s, im.height)), (0, 0)); return out

def repoint(json_path, mapping):
    t = Path(json_path).read_text(encoding="utf-8-sig"); n = 0
    for old, new in mapping.items():
        k = t.count(f'"{old}"'); t = t.replace(f'"{old}"', f'"{new}"'); n += k
    Path(json_path).write_text(t, encoding="utf-8"); return n

def stamp(tag, headline):
    s, d, ver, name = PACKS[tag]; v = ".".join(map(str, ver))
    man = jload(d / "manifest.json"); man["header"]["name"] = name.format(v=v); man["header"]["version"] = list(ver)
    for m in man["modules"]: m["version"] = list(ver)
    man["header"]["description"] = f"v{v} ({DATE}) {headline}"; jdump(man, d / "manifest.json")
    led = d / "PW-DEPENDENCIES.md"
    if led.exists():
        old = ".".join(map(str, jload(s / "manifest.json")["header"]["version"])); t = led.read_text(encoding="utf-8")
        t2 = t.replace(f"v{old} ·", f"v{v} ·", 1)
        if t2 != t: led.write_text(t2, encoding="utf-8")

def main():
    twin = jload(ROOT / "_logs/twin_map_1b.json")
    added = {t: [] for t in PACKS}; manifest = {t: [] for t in PACKS}
    for tag, (s, d, ver, name) in PACKS.items():
        if d.exists(): shutil.rmtree(d)
        shutil.copytree(s, d)
    B = {t: PACKS[t][1] / "textures/blocks" for t in PACKS}
    # ---- 1. RENAMES (CURRENT only; LEGACY slots are never placed in a modern world)
    n_ren = 0; repoint_map = collections.defaultdict(dict)
    for path, r in sorted(twin.items()):
        if r["action"] != "RENAME" or r["tag"] != "CURRENT": continue
        stem = path[len("textures/blocks/"):]; tag = r["source"]
        written = bp.copy_with_companions(B[tag], r["java"], B[tag], stem, "copy", manifest[tag]); manifest[tag] += written
        added[tag].append(f"textures/blocks/{stem}"); n_ren += 1
        repoint_map[tag][f"textures/blocks/{r['java']}"] = path        # same-pack references move to the Bedrock name
    for tag, mp in repoint_map.items():
        for jf in ("textures/terrain_texture.json", "textures/flipbook_textures.json", "textures/item_texture.json"):
            p = PACKS[tag][1] / jf
            if p.exists():
                n = repoint(p, mp)
                if n: log(f"{tag} {jf}: {n} references re-pointed to Bedrock names")
    log(f"1 renames done: {n_ren} CURRENT slots bound under Bedrock names (companions + texture sets ride along)")
    # ---- 2. PULLS + campfire strips + flipbook entries (RP-04)
    fbp = PACKS["RP-04"][1] / "textures/flipbook_textures.json"; fb = jload(fbp)
    shutil.copy(B["RP-04"] / "pw_hearth_flame.png", B["RP-04"] / "campfire.png"); added["RP-04"].append("textures/blocks/campfire")
    shutil.copy(PULL / "soul_fire_0.png", B["RP-04"] / "soul_campfire.png"); added["RP-04"].append("textures/blocks/soul_campfire")
    for tile, tex in (("campfire_fire", "campfire"), ("soul_campfire_fire", "soul_campfire")):
        fb = [e for e in fb if e.get("atlas_tile") != tile]
        nfr = Image.open(B["RP-04"] / f"{tex}.png").height // Image.open(B["RP-04"] / f"{tex}.png").width
        fb.append({"flipbook_texture": f"textures/blocks/{tex}", "atlas_tile": tile, "ticks_per_frame": 2, "blend_frames": False, "frames": list(range(nfr))})
    jdump(fb, fbp)
    for st in ("", "exposed_", "oxidized_", "weathered_"):     # Patrix copper chain states, Java chain layout (colour only — LabPBR _n/_s are not Bedrock companions)
        shutil.copy(PULL / f"{st}copper_chain.png", B["RP-04"] / f"pw_src_{st}copper_chain.png")   # pw_src_: kept authoring source (RP-04's own copper_chain.png is a centred 256 item-style sheet)
    log("2 pulls done: campfire (= pw_hearth_flame strip, 30 f) + soul_campfire (Patrix soul_fire_0, 30 f) with flipbook entries; copper chain states pulled")
    # ---- 3. DERIVES (RP-04 unless noted)
    E = PACKS["RP-04"][1] / "textures/entity"
    for c in COLOURS + ["undyed"]:
        src = E / "shulker" / f"shulker_{c}.png"
        derive(src, B["RP-04"] / f"shulker_top_{c}.png", lambda im: im.crop((im.width // 4, 0, im.width // 2, im.height // 4)), manifest["RP-04"])
        added["RP-04"].append(f"textures/blocks/shulker_top_{c}")
    for pref, ent in CHEST_ICONS.items():
        im = Image.open(E / "chest" / f"{ent}.png").convert("RGBA")
        faces = ["front"] if pref == "trapped_chest" else ["front", "side", "top"]
        for w in faces:
            chest_icon(im, w).save(B["RP-04"] / f"{pref}_{w}.png"); added["RP-04"].append(f"textures/blocks/{pref}_{w}")
    for src, dst in (("chain", "chain"), ("pw_src_copper_chain", "copper_chain"), ("pw_src_exposed_copper_chain", "exposed_copper_chain"), ("pw_src_oxidized_copper_chain", "oxidized_copper_chain"), ("pw_src_weathered_copper_chain", "weathered_copper_chain")):
        for plane in (0, 1):
            derive(B["RP-04"] / f"{src}.png", B["RP-04"] / f"{dst}{plane + 1}.png", lambda im, p=plane: chain_plane(im, p), manifest["RP-04"])
            added["RP-04"].append(f"textures/blocks/{dst}{plane + 1}")
    for n in range(4):
        for bf, jf in GHAST_FACES.items():
            shutil.copy(B["RP-04"] / f"dried_ghast_hydration_{n}_{jf}.png", B["RP-04"] / f"dried_ghast_state_{n + 1}_{bf}.png"); added["RP-04"].append(f"textures/blocks/dried_ghast_state_{n + 1}_{bf}")
        shutil.copy(B["RP-04"] / f"dried_ghast_hydration_{n}_tentacles.png", B["RP-04"] / f"dried_ghast_state_{n + 1}_tentacles.png"); added["RP-04"].append(f"textures/blocks/dried_ghast_state_{n + 1}_tentacles")
    for tag, stem, java in ALIASES:
        bp.copy_with_companions(B[tag], java, B[tag], stem, "copy", manifest[tag]); added[tag].append(f"textures/blocks/{stem}")
    log("3 derives done: shulker tops x17, chest icons x19, chains x10, dried ghast x28, aliases x14")
    # ---- 4. PURGE — harvest on the NEW trees
    ph.TREES = {t: PACKS[t][1] for t in PACKS}
    h = ph.main(out_json=ROOT / "_logs/purge_harvest_new.json")
    report = {}
    for tag in PACKS:
        tree = ph.tree_pack(tag, PACKS[tag][1]); t = h["trees"][tag]; cand = t["candidates"]; live = t["live"]
        kept_unique = {s for s, v in cand.items() if v["class"] == "UNIQUE" and not s.endswith("_backup") and not s.startswith("textures/entity/fallingtree/")}
        decisions = {}
        for s, v in cand.items():
            cls = v["class"]
            b, suf = ph.base_of(s)
            if s.endswith("_backup"): cls = "BACKUP"
            elif s.startswith("textures/entity/fallingtree/"): cls = "OURS-DEAD"
            elif b is not None and b in kept_unique: cls = "UNIQUE-COMPANION"      # a kept UNIQUE stem keeps its companions, whatever their own class
            decisions[s] = cls
        purge = [s for s, c in decisions.items() if c in ("DUP", "CONSUMED", "COMPANION-DEAD", "BACKUP", "OURS-DEAD")]
        keep = [s for s, c in decisions.items() if c in ("UNIQUE", "UNIQUE-COMPANION")]
        dead_sets = [f for f in t["dead_texture_sets"] if f[:-len(".texture_set.json")] not in kept_unique and f[:-len(".texture_set.json")] not in live]
        deleted = []; bytes_ = 0
        for s in purge:
            f = PACKS[tag][1] / tree.tex[s]; bytes_ += f.stat().st_size; f.unlink(); deleted.append(tree.tex[s])
        for f in dead_sets:
            p = PACKS[tag][1] / f
            if p.exists(): bytes_ += p.stat().st_size; p.unlink(); deleted.append(f)
        # companions of purged stems that were 'live' only as companions of a now-deleted base cannot exist (base was live) — nothing more to do
        report[tag] = {"deleted": sorted(deleted), "deleted_bytes": bytes_, "classes": collections.Counter(decisions[s] for s in purge),
                       "kept_unique": sorted(keep), "kept_unique_bytes": sum((PACKS[tag][1] / tree.tex[s]).stat().st_size for s in keep),
                       "ours_unreferenced": t["ours_unreferenced"], "added": added[tag]}
        log(f"4 purge {tag}: {len(deleted)} files / {bytes_/1e6:.1f} MB deleted ({dict(report[tag]['classes'])}); kept UNIQUE {len(keep)} ({report[tag]['kept_unique_bytes']/1e6:.1f} MB)")
    # ---- 5. textures_list.json where the pack ships one
    for tag in PACKS:
        p = PACKS[tag][1] / "textures/textures_list.json"
        if p.exists():
            root = PACKS[tag][1]
            lst = sorted({str(q.relative_to(root)).replace("\\", "/").rsplit(".", 1)[0] for q in root.rglob("*") if q.is_file() and q.suffix.lower() in (".png", ".tga", ".jpg", ".jpeg") and str(q.relative_to(root)).startswith("textures/")})
            p.write_text(json.dumps(lst, indent=1) + "\n", encoding="utf-8"); log(f"5 {tag} textures_list.json regenerated: {len(lst)} entries")
    # ---- 6. stamps
    stamp("RP-03", "NAME AUDIT 1b + PURGE. 84 more vanilla-resolved slots bound under Bedrock's names from Patrix twins already in the pack (stained glass x16 + pane tops x16, "
          "rails x8, anvil x4, quartz pillar/chiseled, crops potatoes/beetroots/cocoa/nether wart/torchflower, huge_fungus/ crimson+warped doors/trapdoors/planks/stems, candles, "
          "cracked deepslate, honeycomb, honey_side, slime, wet sponge, spawner, cobweb, note block, redstone lamp off, stonecutter2, quartz ore, item frame, eyeblossom) "
          "+ bottoms aliased (honey top/bottom, sculk bottoms, enchanting table, stonecutter). Dead weight purged: Java-named duplicates of now-live files and their "
          "orphaned PBR companions/sets. Unreferenced Patrix variants (stone_2/3, granite/andesite/deepslate variants, carved pumpkin 2-4, ...) KEPT as authoring material.")
    stamp("RP-04", "NAME AUDIT 1b + PURGE. Wool x16 rebound under wool_colored_<c> (the new wool slabs/stairs + light gray were vanilla-res), packed_ice; DERIVED: shulker box "
          "tops x17 (lid top face of the entity texture), chest/trapped/ender/copper x4 inventory icons from the E2 chest textures, chain1/2 + copper chain states x4 from "
          "Java's two-plane chain, dried ghast 4 states x6 faces (left/right convention ASSUMED), campfire + soul campfire flames = Patrix 30-frame fire strips with "
          "flipbook entries. PURGED: E2/bed/sign/boat/banner/conduit/pot Java-layout sources and dead entity families, Java-named duplicates, orphaned companions, sun backups. "
          "KEPT: unreferenced Patrix variants + terracotta colours + celestial/ moon art (listed). Pair with BP-02 v1.3.182 + RP-02 v2.0.3.")
    stamp("RP-01", "PURGE. Dead weight removed: Java-named duplicates of live files, orphaned PBR companions/texture sets, and the unreferenced falling-tree leaf sprite "
          "stages s2-s6 of an earlier BIGCANOPY iteration (the live entity references leaves_frame_*_v3-5 + trunk_*_old only). Plant/sapling _v0-2 variants KEPT (authoring material).")
    stamp("RP-05", "NAME AUDIT 1b + PURGE. Potted azalea / flowering azalea and crimson/warped roots pot slots aliased to the Patrix plant textures; Java-named duplicates "
          "(coral wall fans, flowers, dark oak leaves) and their orphaned companions/sets purged; textures_list.json regenerated.")
    jdump({"added": added, "report": {t: {k: (v if k != "classes" else dict(v)) for k, v in r.items()} for t, r in report.items()}}, ROOT / "_logs/purge_report.json")
    log("6 manifests + ledgers stamped; _logs/purge_report.json written")

if __name__ == "__main__":
    main()
