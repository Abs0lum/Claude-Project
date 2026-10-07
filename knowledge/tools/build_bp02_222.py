#!/usr/bin/env python3
"""build_bp02_222.py — BP-02 1.3.222 from the frozen 1.3.221: THE GALLERY (D-C571 v2, his 21:39 + 22:01).
  1. One pw:art_<key> entity per catalogued work (entities/pw_art/*.json; static, no collision, property pw:facing).
  2. scripts/pw_gallery.js (tools/bp02_src) + the generated data modules pw_gallery_data.js (works / artists / subjects)
     and pw_gallery_text.js (the book's texts: museum descriptions now, the essay program's texts as they land).
  3. CIV_BUILDINGS: `art` slots for every building (tools/art_slots.py: an offline wall scan of each template; the palace
     pieces by room: chapel religious, great hall + guard rooms history / mythology, council + chancery portraits,
     kitchens + commons still life / genre, garrets landscapes).
  4. The clock hangs the slots at the furnished stage (placeStage hook) and sweeps older finished buildings one per beat.
  5. The Connoisseur's Book item + recipe (book + gold nugget); its icon and name live in RP-08.
Usage: python3 tools/build_bp02_222.py   (bp02-222 must not exist; catalogue.json after art_catalogue.py)"""
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import art_slots as AS  # noqa: E402
import mcstructure as M  # noqa: E402

B = Path("/home/claude/_build")
SRC, DST = B / "bp02-221", B / "bp02-222"
CAT = Path("/home/claude/_intake/art/catalogue.json")
ESSAYS = Path("/home/claude/_intake/art/essays.json")          # the essay program's output {key: {d, i, c}}, bios.json {artist_key: bio}
BIOS = Path("/home/claude/_intake/art/bios.json")
SRCS = Path("/home/claude/tools/bp02_src")
LOG = []
SUBJECTS = ["religious", "portrait", "landscape", "myth_history", "genre", "still_life"]
SOURCES = ["National Gallery of Art, Washington (Open Access, CC0)", "The Metropolitan Museum of Art (Open Access, CC0)", "The Cleveland Museum of Art (Open Access, CC0)"]
SRC_IDX = {"nga": 0, "met": 1, "cma": 2}


def rep(text, old, new, what, count=1):
    n = text.count(old)
    if n != count:
        raise SystemExit(f"PATCH '{what}': expected {count} match(es), found {n}")
    LOG.append(what)
    return text.replace(old, new)


def read(rel):
    return (DST / rel).read_text(encoding="utf-8")


def write(rel, text):
    (DST / rel).parent.mkdir(parents=True, exist_ok=True)
    (DST / rel).write_text(text, encoding="utf-8")


def kid(key):
    return re.sub(r"[^a-z0-9]+", "_", key.lower())


# ------------------------------------------------------------------------------------------------ the palace's rooms
PIECES = {"sw": (0, 0), "se": (0, 64), "nw": (64, 0), "ne": (64, 64)}


def palace_subject(piece):
    ox, oz = PIECES[piece]

    def room_of(cx, y, cz):
        X, Z, feet = cx + ox, cz + oz, y - 15
        if 45 <= X <= 62 and 112 <= Z <= 118 and feet <= 13:
            return "religious"                                     # the chapel
        if 64 <= X <= 81:                                          # the corps de logis
            if feet < 6:
                return "myth_history" if 40 <= Z <= 87 else "portrait"
            if feet < 15:
                return "portrait" if Z < 64 else "myth_history"
            return "landscape"
        if 10 <= X <= 63 and 8 <= Z <= 25:                         # the west wing: guard room, treasury / chancery / judges, archive
            return "myth_history" if feet < 6 else ("portrait" if feet < 15 else "landscape")
        if 10 <= X <= 63 and 102 <= Z <= 119:                      # the east wing: household offices, apartments
            return "genre" if feet < 6 else "any"
        if X >= 86:                                                # the service court
            return "still_life" if feet < 6 else "genre"
        if X <= 9:
            return "myth_history"                                  # the gatehouse
        return "any"
    return room_of


# ------------------------------------------------------------------------------------------------ data modules
def gallery_data(cat):
    works, artists = [], {}
    keys = sorted(cat, key=lambda k: (cat[k].get("artist_key") or "", cat[k].get("year") or 0, k))
    for k in keys:
        r = cat[k]
        if "frame" not in r or not Path(r["file"]).exists():
            continue
        fr = r["frame"]
        dims = f"{fr['cm'][0]:.0f} × {fr['cm'][1]:.0f} cm" if fr.get("cm") else ""
        ak = r.get("artist_key") or "anonymous"
        artists.setdefault(ak, [r.get("artist_display") or r.get("artist") or "Anonymous", r.get("artist_nat") or "", r.get("artist_dates") or ""])
        works.append([k, (r.get("title") or "Untitled").replace("\n", " ")[:120], ak, (r.get("date") or "")[:40], r.get("year") or 0,
                      (r.get("medium") or "")[:60], dims, SRC_IDX[k.split(":")[0]], SUBJECTS.index(r.get("subject", "genre")), fr["w"], fr["h"],
                      1 if r.get("famous") else 0, r.get("url") or "", 1 if r.get("palace_ok") else 0, (r.get("credit") or "")[:90]])
    js = ("// generated by build_bp02_222.py — the GALLERY catalogue (CC0 works: NGA, the Met, Cleveland)\n"
          "// WORKS[i] = [key, title, artistKey, date, year, medium, dims, src, subject, w, h, famous, url, palaceOk, credit]\n"
          f"export const SUBJECTS = {json.dumps(SUBJECTS)};\nexport const SOURCES = {json.dumps(SOURCES)};\n"
          f"export const ARTISTS = {json.dumps(artists, ensure_ascii=False, separators=(',', ':'))};\n"
          f"export const WORKS = {json.dumps(works, ensure_ascii=False, separators=(',', ':'))};\n")
    return js, works, artists


def gallery_text(cat, works):
    essays = json.loads(ESSAYS.read_text()) if ESSAYS.exists() else {}
    bios = json.loads(BIOS.read_text()) if BIOS.exists() else {}
    text = {}
    for row in works:
        k = row[0]
        r = cat[k]
        e = essays.get(k) or {}
        d = e.get("d")
        if not d:
            d = r.get("description") or r.get("alt") or ""
            if r.get("did_you_know"):
                d = (d + "\n\nDid you know? " + r["did_you_know"]).strip()
        t = {}
        if d:
            t["d"] = d.strip()[:2400]
        if e.get("i"):
            t["i"] = e["i"].strip()[:1800]
        if e.get("c"):
            t["c"] = e["c"].strip()[:1800]
        if t:
            text[k] = t
    js = ("// generated by build_bp02_222.py — the Connoisseur's Book texts: museum descriptions (CC0) + the essay program's\n"
          "// readings (interpretation / critique are labelled as readings in the book)\n"
          f"export const TEXT = {json.dumps(text, ensure_ascii=False, separators=(',', ':'))};\n"
          f"export const BIOS = {json.dumps(bios, ensure_ascii=False, separators=(',', ':'))};\n")
    return js, len(text), len(bios)


ENTITY = {"format_version": "1.21.80", "minecraft:entity": {
    "description": {"identifier": "pw:art_KEY", "is_spawnable": False, "is_summonable": True, "is_experimental": False,
                    "properties": {"pw:facing": {"type": "int", "range": [0, 3], "default": 0, "client_sync": True}}},
    "components": {
        "minecraft:type_family": {"family": ["pw_art", "inanimate"]},
        "minecraft:collision_box": {"width": 1.0, "height": 1.0},
        "minecraft:physics": {"has_gravity": False, "has_collision": False},
        "minecraft:pushable": {"is_pushable": False, "is_pushable_by_piston": False},
        "minecraft:knockback_resistance": {"value": 1.0},
        "minecraft:damage_sensor": {"triggers": [{"cause": "all", "deals_damage": "no"}]},
        "minecraft:health": {"value": 1, "max": 1},
        "minecraft:persistent": {},
        "minecraft:fire_immune": {},
        "minecraft:breathable": {"breathes_air": True, "breathes_water": True, "breathes_lava": True, "breathes_solids": True},
        "minecraft:conditional_bandwidth_optimization": {"default_values": {"max_optimized_distance": 80, "max_dropped_ticks": 20, "use_motion_prediction_hints": False}}}}}


def entity_json(key, w, h):
    e = json.loads(json.dumps(ENTITY))
    e["minecraft:entity"]["description"]["identifier"] = f"pw:art_{kid(key)}"
    e["minecraft:entity"]["components"]["minecraft:collision_box"] = {"width": min(6.0, float(w)), "height": float(h)}
    return e


def main():
    if DST.exists():
        raise SystemExit(f"{DST} exists — move it to _garbage first")
    cat = json.loads(CAT.read_text())
    shutil.copytree(SRC, DST)
    m = json.loads(read("manifest.json"))
    m["header"]["version"] = [1, 3, 222]
    m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.222"
    for mod in m["modules"]:
        mod["version"] = [1, 3, 222]
    m["header"]["description"] = ("v1.3.222 (2026-10-05) THE GALLERY: thousands of public-domain paintings (NGA, the Met, Cleveland — CC0) hang as unique "
                                  "works in every CIVITAS building and the palace; the Connoisseur's Book (book + gold nugget) tells the artist's life, "
                                  "the work, a reading and a critique (needs RP-08 Gallery for the pictures). Includes all of " + m["header"]["description"])[:1200]
    write("manifest.json", json.dumps(m, indent=2))
    main_js = read("scripts/main.js")
    main_js = rep(main_js, 'const PW_BUILD = "1.3.221";', 'const PW_BUILD = "1.3.222";', "PW_BUILD")
    main_js = rep(main_js, 'import "./pw_civ_clock.js";', 'import "./pw_civ_clock.js";\nimport "./pw_gallery.js"; // v1.3.222: THE GALLERY — unique public-domain paintings + the Connoisseur\'s Book (D-C571)', "gallery import")
    write("scripts/main.js", main_js)
    comp = read("scripts/pw_companion.js")
    comp = rep(comp, "companion v7 LOADED (pack v1.3.221", "companion v7 LOADED (pack v1.3.222", "companion banner")
    write("scripts/pw_companion.js", comp)
    # 1. the entities
    (DST / "entities/pw_art").mkdir(parents=True)
    n_ent = 0
    for k, r in cat.items():
        if "frame" not in r or not Path(r["file"]).exists():
            continue
        (DST / "entities/pw_art" / f"{kid(k)}.json").write_text(json.dumps(entity_json(k, r["frame"]["w"], r["frame"]["h"]), separators=(",", ":")))
        n_ent += 1
    LOG.append(f"{n_ent} pw:art entities")
    # 2. the scripts
    shutil.copy2(SRCS / "pw_gallery.js", DST / "scripts/pw_gallery.js")
    data_js, works, artists = gallery_data(cat)
    write("scripts/pw_gallery_data.js", data_js)
    text_js, n_text, n_bios = gallery_text(cat, works)
    write("scripts/pw_gallery_text.js", text_js)
    LOG.append(f"pw_gallery.js + data ({len(works)} works, {len(artists)} artists) + text ({n_text} descriptions, {n_bios} lives)")
    # 3. the art slots
    bld = read("scripts/pw_civ_buildings.js")
    MARK = "export const CIV_BUILDINGS = "
    head, body = bld.split(MARK, 1)
    body = body.strip()
    assert body.endswith(";")
    tbl = json.loads(body[:-1])
    n_slots = 0
    for fam, v in tbl.items():
        f = DST / "structures/pw" / f"{v['stem']}.mcstructure"
        if not f.exists():
            v["art"] = []
            continue
        st = M.Structure.from_bytes(f.read_bytes())
        room_of = None
        if "palace" in fam:
            room_of = palace_subject(v["stem"].split("_")[2])
        v["art"] = AS.slots_for(st, v["datum_y"], fam, room_of=room_of)
        n_slots += len(v["art"])
    write("scripts/pw_civ_buildings.js", head + MARK + json.dumps(tbl, separators=(",", ":")) + ";")
    LOG.append(f"CIV_BUILDINGS art slots: {n_slots} across {len(tbl)} buildings")
    # 4. the clock hooks
    clock = read("scripts/pw_civ_clock.js")
    clock = rep(clock, 'import * as COIN from "./pw_civ_coin.js";', 'import * as COIN from "./pw_civ_coin.js";\nimport * as GALLERY from "./pw_gallery.js";                     // 1.3.222: unique paintings hang at the furnished stage (D-C571)', "gallery import (clock)")
    clock = rep(clock, "    if (k === def.stages - 1 && b.settlement !== undefined) { const sst = load().settlements.find((x) => x.id === b.settlement); if (sst) sweepBox(dim, sst, b.x - 10, b.z - 10, b.x + fx + 9, b.z + fz + 9, b.y + def.datum_y - 6, `#${b.id} ${short(b)}`); }   // 1004b: the air above a finished building holds no floating crown",
                "    if (k === def.stages - 1 && b.settlement !== undefined) { const sst = load().settlements.find((x) => x.id === b.settlement); if (sst) sweepBox(dim, sst, b.x - 10, b.z - 10, b.x + fx + 9, b.z + fz + 9, b.y + def.datum_y - 6, `#${b.id} ${short(b)}`); }   // 1004b: the air above a finished building holds no floating crown\n"
                "    if (k === def.stages - 1 && !b.artDone) { try { const nh = GALLERY.hangBuilding(dim, b, def, Math.floor(load().simDays)); if (nh) { const sst2 = load().settlements.find((x) => x.id === b.settlement); if (sst2) sst2.log.push(`day ${load().simDays.toFixed(0)}: ${nh} picture(s) hung in #${b.id} ${short(b)}${b.artDone ? \"\" : \" (more to come)\"}`); } } catch (e) { console.warn(`[GALLERY] #${b.id}: ${e}`); } }   // 1.3.222: the gallery (resumable: the sweep finishes it)",
                "gallery at the furnished stage")
    clock = rep(clock, "system.runInterval(prof(\"clock\", () => {\n  const s = load();\n  const now = worldDays();",
                "system.runInterval(prof(\"clock\", () => {\n  const s = load();\n"
                "  if (system.currentTick % 200 === 0) {                                               // 1.3.222: older finished buildings get their pictures, one per sweep\n"
                "    for (const b of s.buildings) {\n"
                "      const def = BUILDINGS[b.family];\n"
                "      if (!def || b.artDone || b.stage < def.stages - 1 || b.pending.length || !(def.art || []).length) continue;\n"
                "      try { const dim = world.getDimension(b.dim); if (!dim.getBlock({ x: b.x, y: b.y + def.datum_y, z: b.z })) continue; const nh = GALLERY.hangBuilding(dim, b, def, Math.floor(s.simDays)); if (nh || b.artDone) save(); }\n"
                "      catch (e) { console.warn(`[GALLERY] sweep #${b.id}: ${e}`); }\n"
                "      break;\n"
                "    }\n"
                "  }\n"
                "  const now = worldDays();", "gallery sweep")
    write("scripts/pw_civ_clock.js", clock)
    # 5. the book
    write("items/pw_connoisseur_book.json", json.dumps({"format_version": "1.21.30", "minecraft:item": {
        "description": {"identifier": "pw:connoisseur_book", "menu_category": {"category": "items"}},
        "components": {"minecraft:icon": {"textures": {"default": "pw_connoisseur_book"}}, "minecraft:max_stack_size": 1,
                       "minecraft:display_name": {"value": "item.pw:connoisseur_book.name"}}}}, indent=1))
    write("recipes/connoisseur_book.json", json.dumps({"format_version": "1.20.10", "minecraft:recipe_shapeless": {
        "description": {"identifier": "pw:connoisseur_book"}, "tags": ["crafting_table"],
        "ingredients": [{"item": "minecraft:book"}, {"item": "minecraft:gold_nugget"}],
        "result": {"item": "pw:connoisseur_book", "count": 1}, "unlock": [{"item": "minecraft:book"}]}}, indent=1))
    LOG.append("pw:connoisseur_book item + recipe")
    print("\n".join(f"  ok  {w}" for w in LOG))
    print("DONE", DST)


if __name__ == "__main__":
    main()
