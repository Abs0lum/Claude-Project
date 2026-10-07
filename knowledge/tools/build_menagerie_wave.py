#!/usr/bin/env python3
"""build_menagerie_wave.py — merge a staged menagerie wave into the packs (D-C351, wave P1 = the new animals).

  RP-07 1.4.31 -> 1.4.32 (his 15:11 ruling: other animals go into RP-07 Neutral while it stays under 250 MB): every staged RP file
     (entity/, models/, animations/, animation_controllers/, render_controllers/, textures/, sounds/ under pw_menagerie/<src>/) +
     the pack-level fragments merged: texts/en_US.lang (+ languages.json), sounds.json (entity_sounds), sounds/sound_definitions.json,
     textures/item_texture.json.
  PW-StripMine BP 1.3.6 -> 1.3.7 (his Q4): every staged BP file (entities, loot tables, spawn rules, items under pw_menagerie/<src>/).
  Ledgers (§9): one RESTRICTED-ASSETS line per ported creature / item group (source pack, licence as shown), one provenance line.
Never edits an existing file except the manifests and the four merged pack-level files (the gate proves it)."""
import json, shutil, sys, time
from pathlib import Path

ROOT = Path("/home/claude"); STAGE = ROOT / "_build/menagerie-stage"
WAVES = {"P1": dict(rp=("rp07-1431", "rp07-1432", [1, 4, 32]), bp=("stripmine-bp-136", "stripmine-bp-137", [1, 3, 7]), name="P1 (the new animals)",
                   jobs="_logs/menagerie_jobs_P1.json", m0=0),
         "P3": dict(rp=("rp07-1432", "rp07-1433", [1, 4, 33]), bp=("stripmine-bp-137", "stripmine-bp-138", [1, 3, 8]), name="P3 (his picks)",
                   jobs="_logs/menagerie_jobs_P3.json", m0=150),
         "R2": dict(rp=("rp07-1433", "rp07-1434", [1, 4, 34]), bp=("stripmine-bp-138", "stripmine-bp-139", [1, 3, 9]),
                   name="R2 (WWA seal lives, AnF spawn weights to vanilla scale, our spawn rules on today's grass)",
                   jobs="_logs/menagerie_jobs_R2.json", m0=471)}
W = WAVES[sys.argv[1] if len(sys.argv) > 1 else "P1"]
RP_SRC, RP, RP_VER = ROOT / "_build" / W["rp"][0], ROOT / "_build" / W["rp"][1], W["rp"][2]
BP_SRC, BP, BP_VER = ROOT / "_build" / W["bp"][0], ROOT / "_build" / W["bp"][1], W["bp"][2]
RPV, BPV = ".".join(map(str, RP_VER)), ".".join(map(str, BP_VER))
DATE = "2026-09-30"; WAVE = W["name"]
SRC_INFO = {"AnF": ("Animals and Fauna (Wildlife Overworld Add-On), his Drive 'Packs'", "no licence text in the pack"),
            "WA": ("World Animals Add-on (ArathNido), his Drive 'Packs'", "no licence text; 'Created by ArathNido'"),
            "WS": ("Wildlife Sanctuary Mobs Plus (Neq Gamerz), his Drive 'Packs'", "no licence text; 'Made by Neq Gamerz'"),
            "WWA": ("World Wild Animals (enduringcell642), his Drive 'Packs'", "no licence text; 'made by enduringcell642'"),
            "YSav": ("yCreatures Savanna 1.0.5 (yBrothers / Gabriel Castro), his Drive 'Packs'", "README of yCreatures: 'Copyright … All Rights Reserved', no copying / modifying"),
            "YTri": ("yCreatures 2.0.4 (yBrothers / Gabriel Castro), his Drive 'Packs'", "README: 'Copyright 2019 @GabrielCas29007 … All Rights Reserved', no copying / modifying"),
            "IFS": ("Immersive Fauna Savanna 1.5.0, his Drive 'Packs'", "no licence text in the pack")}


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT {time.strftime('%m-%d')}] BUILD menagerie {WAVE}: {m}\n")


def jl(p, default):
    try: return json.loads(Path(p).read_text(encoding="utf-8-sig"))
    except FileNotFoundError: return default


UPDATED = []
NEW_GROUND = ["minecraft:grass_block", "pw:grass_block"]        # what BP-02's own cow / sheep / ... rules spawn on


def fix_our_grass(bp):
    """D-C354 (his S2): our StripMine spawn rules (outside pw_menagerie) whose block filters name only the old 'minecraft:grass'
    (renamed minecraft:grass_block) get today's name + our pw:grass_block, the ground our worlds are made of. Nothing else changes."""
    changed = []
    for f in sorted((bp / "spawn_rules").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8-sig")); hit = False
        for c in d["minecraft:spawn_rules"].get("conditions", []):
            for key in ("minecraft:spawns_on_block_filter", "minecraft:spawns_above_block_filter"):
                v = c.get(key)
                if v is None: continue
                holder, lk = (v, "blocks") if isinstance(v, dict) and "blocks" in v else (c, key)
                lst = holder[lk] if isinstance(holder[lk], list) else [holder[lk]]
                names = [b if isinstance(b, str) else (b.get("name") if isinstance(b, dict) else b) for b in lst]
                if "minecraft:grass" in names:
                    out = []
                    for b, nm in zip(lst, names): out += NEW_GROUND if nm == "minecraft:grass" else [b]
                    holder[lk] = list(dict.fromkeys(json.dumps(x) for x in out)); holder[lk] = [json.loads(x) for x in holder[lk]]; hit = True
        if hit:
            f.write_text(json.dumps(d, indent=1)); changed.append(str(f.relative_to(bp)))
    return changed


def copy_tree(src, dst, skip=()):
    n = 0
    for p in src.rglob("*"):
        if not p.is_file() or any(part in skip for part in p.relative_to(src).parts): continue
        o = dst / p.relative_to(src)
        if o.exists():                                            # a file an earlier wave already shipped: byte-identical, or (P3) an
            if o.read_bytes() == p.read_bytes(): continue         # earlier port file the D-C353 fixes improved (particles, egg / event ids)
            assert W is not WAVES["P1"] and "pw_menagerie" in str(o), f"would change {o}"
            UPDATED.append(str(o.relative_to(dst)))
        o.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(p, o); n += 1
    return n


def build():
    rep = json.loads((STAGE / "PORT-REPORT.json").read_text())
    for d, s in ((RP, RP_SRC), (BP, BP_SRC)):
        if d.exists(): shutil.rmtree(d)
        shutil.copytree(s, d)
    moved = 0
    if sys.argv[1:2] == ["R2"] and (RP / "models/pw_menagerie").exists():   # D-C355: the models now live under models/entity/pw_menagerie
        moved = sum(1 for p in (RP / "models/pw_menagerie").rglob("*") if p.is_file()); shutil.rmtree(RP / "models/pw_menagerie")
    nr = copy_tree(STAGE / "RP", RP, skip=("_fragments",)); nb = copy_tree(STAGE / "BP", BP)
    F = STAGE / "RP/_fragments"
    # lang
    lang = RP / "texts/en_US.lang"; lang.parent.mkdir(exist_ok=True)
    old = lang.read_text(encoding="utf-8") if lang.exists() else ""
    new_lines = [l for l in (F / "en_US.lang").read_text(encoding="utf-8").splitlines() if l and l.split("=")[0] + "=" not in old]
    lang.write_text((old.rstrip("\n") + "\n" if old else "") + "\n".join(new_lines) + "\n", encoding="utf-8")
    lj = RP / "texts/languages.json"
    if not lj.exists(): lj.write_text('["en_US"]\n')
    # sounds.json (entity_sounds) + sound_definitions
    sj = jl(RP / "sounds.json", {}); fr = jl(F / "sounds.json", {})
    ents = sj.setdefault("entity_sounds", {}).setdefault("entities", {})
    for k, v in fr.get("entity_sounds", {}).get("entities", {}).items():
        assert ents.get(k, v) == v, k; ents[k] = v
    (RP / "sounds.json").write_text(json.dumps(sj, indent=1))
    sd = jl(RP / "sounds/sound_definitions.json", {"format_version": "1.20.20", "sound_definitions": {}})
    defs = sd.setdefault("sound_definitions", {})
    for k, v in jl(F / "sound_definitions.json", {}).get("sound_definitions", {}).items():
        assert defs.get(k, v) == v, k; defs[k] = v
    (RP / "sounds").mkdir(exist_ok=True); (RP / "sounds/sound_definitions.json").write_text(json.dumps(sd, indent=1))
    mf = jl(F / "entity.material", {}).get("materials", {})
    if len(mf) > 1:                                               # our custom entity materials (an add-on's 'name:base' with a body)
        (RP / "materials").mkdir(exist_ok=True); (RP / "materials/entity.material").write_text(json.dumps({"materials": mf}, indent=1))
    it = jl(RP / "textures/item_texture.json", {"resource_pack_name": "rp07", "texture_name": "atlas.items", "texture_data": {}})
    for k, v in jl(F / "item_texture.json", {}).get("texture_data", {}).items():
        assert it["texture_data"].get(k, v) == v, k; it["texture_data"][k] = v
    (RP / "textures/item_texture.json").write_text(json.dumps(it, indent=1))
    # manifests
    J = json.loads((ROOT / W["jobs"]).read_text()); wave_ids = {e[2] for e in J["entities"]}; wave_items = {i[2] for i in J["items"]}
    creatures = [c for c in rep["creatures"] if c["new"] in wave_ids]
    prv, pbv = ".".join(map(str, RP_VER[:2] + [RP_VER[2] - 1])), ".".join(map(str, BP_VER[:2] + [BP_VER[2] - 1]))
    # his M9 (P3): our own creatures' spawn rules carry the shared weight too (the only existing BP files a wave edits)
    ours_spawn = {}
    if sys.argv[1:2] in (["P3"], ["R2"]):
        ours_spawn = json.loads((ROOT / "_logs/menagerie_p3_ours_spawn.json").read_text())
        for rel, row in ours_spawn.items(): (BP / rel).write_text(json.dumps(row["json"], indent=1))
    grass = []
    if sys.argv[1:2] == ["R2"]:                                    # his S2: our own spawn rules named the old 'minecraft:grass' only
        grass = fix_our_grass(BP)
        (ROOT / "_logs/menagerie_R2_grass.json").write_text(json.dumps(grass, indent=1))
    for d, ver, name, desc in ((RP, RP_VER, f"AbsolutRealism Neutral Mobs RP v{RPV}",
                                f"v{RPV} ({DATE}) MENAGERIE {WAVE}: {len(creatures)} creatures from his add-on collection (looks, animations, sounds, "
                                f"names; ids pw:<animal>_<pack>), pairs with PW-StripMine BP v{BPV}. Includes all of v{prv}"
                                + (" — FIX: every ported model moved to models/entity/pw_menagerie/ (the game loads entity geometry only under models/entity; "
                                   "1.4.32 / 1.4.33 ported animals were invisible)" if moved else "") + "."),
                               (BP, BP_VER, f"PW StripMine BP v{BPV}",
                                f"v{BPV} ({DATE}) MENAGERIE {WAVE}: behaviours, spawn rules, loot and {len(wave_items)} drop / use items of "
                                f"{len(creatures)} creatures (ids pw:<animal>_<pack>)"
                                + (f"; {len(ours_spawn)} of our own spawn rules share their weight with the kept versions" if ours_spawn else "")
                                + (f"; {len(grass)} of our own spawn rules now spawn on minecraft:grass_block + pw:grass_block (was the old 'minecraft:grass')" if grass else "")
                                + ("; AnF spawn weights scaled to the vanilla level (x0.1)" if sys.argv[1:2] == ["R2"] else "")
                                + f". Pairs with RP-07 v{RPV}. Includes all of v{pbv}.")):
        m = json.loads((d / "manifest.json").read_text(encoding="utf-8-sig"))
        m["header"]["version"] = ver; m["header"]["name"] = name; m["header"]["description"] = desc
        for mod in m["modules"]: mod["version"] = ver
        (d / "manifest.json").write_text(json.dumps(m, indent=1))
    # ledgers
    ra = ROOT / "_docs/licensing/RESTRICTED-ASSETS.md"; t = ra.read_text(encoding="utf-8")
    rows = []; k = 0
    by = {}
    k = W["m0"]
    for c in creatures: by.setdefault(c["src"], []).append(c["new"])
    for src, ids in sorted(by.items()):
        site, lic = SRC_INFO[src]
        for i in ids:
            k += 1
            rows.append(f"| M{k} | RP-07 {RPV} + StripMine BP {BPV}: entity/pw_menagerie/{src.lower()}/… | {i} | {site} | the add-on's model, textures, animations, sounds, behaviour | {lic} | {DATE} | the add-on author | ask the author / commission / replace | in use |")
    items = sorted(wave_items)
    if items:
        rows.append(f"| M{k + 1} | StripMine BP {BPV} items/pw_menagerie/… + RP-07 textures/items/pw_menagerie/… | {len(items)} items: {', '.join(items)} | (the same add-ons) | item icons | as their pack | {DATE} | the add-on authors | as above | in use |")
    t = t.replace("| — | (none yet) | | | | | | | | |\n", "", 1) if "| — | (none yet) | | | | | | | | |" in t.split("## Swapped")[0] else t
    t = "\n".join(l for l in t.split("\n") if not (l.startswith("| M") and (f"RP-07 {RPV} " in l or f"StripMine BP {BPV} " in l)))   # idempotent re-run
    head, tail = t.split("## Swapped", 1)
    t = head.rstrip("\n") + "\n" + "\n".join(rows) + "\n\n## Swapped" + tail
    ra.write_text(t, encoding="utf-8")
    pv = ROOT / "_docs/texture_pilot/PROVENANCE.md"
    pv.write_text("\n".join(l for l in pv.read_text().split("\n") if not (f"menagerie {WAVE}" in l and f"RP-07 {RPV}" in l)).rstrip("\n") + "\n")
    with open(pv, "a") as f:
        f.write(f"- {DATE} · menagerie {WAVE}: {len(creatures)} creatures + {len(items)} items from his add-on collection "
                f"({', '.join(f'{s} {len(v)}' for s, v in sorted(by.items()))}) · licences as shown in RESTRICTED-ASSETS M{W['m0'] + 1}-M{k + 1} · RP-07 {RPV} + StripMine BP {BPV}\n")
    log(f"RP-07 {RPV} (+{nr} files, {moved} old-place models removed, merged lang / sounds / sound_definitions / item_texture), StripMine BP {BPV} (+{nb} files, "
        f"{len(ours_spawn)} own spawn rules re-weighted, {len(UPDATED)} earlier port files improved); RESTRICTED-ASSETS +{len(rows)} lines")
    (ROOT / f"_logs/menagerie_{sys.argv[1] if len(sys.argv) > 1 else 'P1'}_updated.json").write_text(json.dumps(UPDATED, indent=1))
    return nr, nb


if __name__ == "__main__":
    build()
