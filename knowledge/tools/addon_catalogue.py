#!/usr/bin/env python3
"""addon_catalogue.py — read-only census of third-party creature add-ons in _intake/addons-0930 (his Drive "Packs", 09-29/30).
For every client entity: identifier, geometry (cubes / bones / texture size declared), skin PNG sizes, animation names; then groups
the same species across packs so the best source per species can be picked (his 14:06 ask: "grab the best versions ... geometry,
bones, skeleton, textures, animations"). Output: _docs/menagerie/ADDON-CATALOGUE-2026-09-30.md + _logs/addon_catalogue.json."""
import io, json, re, sys, zipfile, collections
from pathlib import Path
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML

D = Path("/home/claude/_intake/addons-0930")
OUT = Path("/home/claude/_docs/menagerie")
VANILLA = set("""allay armadillo axolotl bat bee blaze bogged breeze camel cat cave_spider chicken cod cow creeper dolphin donkey drowned elder_guardian
ender_dragon enderman endermite evocation_illager fox frog ghast glow_squid goat guardian hoglin horse husk iron_golem llama magma_cube mooshroom mule
ocelot panda parrot phantom pig piglin piglin_brute pillager polar_bear pufferfish rabbit ravager salmon sheep shulker silverfish skeleton skeleton_horse
slime sniffer snow_golem spider squid stray strider tadpole trader_llama tropicalfish turtle vex villager vindicator wandering_trader warden witch wither
wolf zoglin zombie zombie_horse zombie_pigman zombie_villager creaking happy_ghast""".split())
PREFIX = re.compile(r"^(skinscraft_|trial_|savanna_|ycreatures_|wwa_|ulta_|cyd_|jp_|jurassic_|zoo_|wild_)+")


def members(data, prefix=""):
    try: z = zipfile.ZipFile(io.BytesIO(data))
    except Exception: return
    for i in z.infolist():
        if i.filename.lower().endswith((".mcpack", ".zip", ".mcaddon")): yield from members(z.read(i), prefix + i.filename + "!")
        elif not i.is_dir(): yield prefix + i.filename, z.read(i)


def parse(b):
    try: return ML._parse_json(b.decode("utf-8-sig", "replace"))
    except Exception: return None


def species_key(ident):
    s = ident.split(":")[-1].lower()
    s = PREFIX.sub("", s)
    s = re.sub(r"_(black|silverback|male|female|baby|adult|brown|grey|gray|white|red|v\d+|variant\d*|\d+)$", "", s)
    return s


def pack_scan(path):
    files = dict(members(path.read_bytes()))
    geos, anims, ents = {}, {}, []
    for n, b in files.items():
        if not n.endswith(".json"): continue
        d = parse(b)
        if not isinstance(d, dict): continue
        if "minecraft:geometry" in d:
            for g in d["minecraft:geometry"]:
                desc = g.get("description", {}); bones = g.get("bones", []) or []
                geos[desc.get("identifier")] = (sum(len(x.get("cubes", []) or []) for x in bones), len(bones), f'{desc.get("texture_width")}x{desc.get("texture_height")}')
        for k, v in d.items():
            if k.startswith("geometry.") and isinstance(v, dict):
                bones = v.get("bones", []) or []
                geos[k.split(":")[0]] = (sum(len(x.get("cubes", []) or []) for x in bones), len(bones), f'{v.get("texturewidth")}x{v.get("textureheight")}')
        if "animations" in d and isinstance(d["animations"], dict) and "minecraft:client_entity" not in d:
            for k in d["animations"]: anims[k] = n
        if "minecraft:client_entity" in d:
            ents.append((n, d["minecraft:client_entity"].get("description", {})))
    pngs = {re.sub(r"\.(png|tga)$", "", n.split("!")[-1].split("/", 1)[-1] if "/" in n else n): n for n in files if n.lower().endswith((".png", ".tga"))}
    rows = []
    for n, desc in ents:
        ident = desc.get("identifier", "?")
        tex = list((desc.get("textures") or {}).values())
        sizes = []
        for t in tex:
            hit = next((files[p] for q, p in pngs.items() if q.endswith(t) or p.endswith(t + ".png") or p.endswith(t + ".tga")), None)
            if hit:
                try: sizes.append(Image.open(io.BytesIO(hit)).size[0])
                except Exception: pass
        g = list((desc.get("geometry") or {}).values())
        gi = [geos.get(x) for x in g if geos.get(x)]
        an = list((desc.get("animations") or {}).keys())
        rows.append({"id": ident, "key": species_key(ident), "tex_px": max(sizes) if sizes else None, "skins": len(tex),
                     "cubes": max((x[0] for x in gi), default=None), "bones": max((x[1] for x in gi), default=None),
                     "anims": [a for a in an if not a.startswith(("look_at", "controller"))][:8], "file": n})
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    catalog = {}
    for f in sorted(D.iterdir()):
        if f.is_file(): catalog[f.name] = pack_scan(f)
    json.dump(catalog, open("/home/claude/_logs/addon_catalogue.json", "w"), indent=1)
    by = collections.defaultdict(list)
    for pk, rows in catalog.items():
        for r in rows: by[r["key"]].append((pk, r))
    L = ["# Creature add-on catalogue — his Drive 'Packs' (pulled 2026-09-30)", "",
         "Read-only census (`tools/addon_catalogue.py`). Per client entity: the skin's width in pixels, cube and bone counts of its model, and its animations.",
         "Patrix mobs, for scale, are 128x-class skins (1024 px wide on a 128-unit sheet) with 20-80+ cubes.", "",
         "## Packs", "", "| Pack | Client entities | Largest skin (px) |", "|---|---|---|"]
    for pk, rows in catalog.items():
        L.append(f"| {pk} | {len(rows)} | {max((r['tex_px'] or 0) for r in rows) if rows else '-'} |")
    L += ["", "## Species found in 2+ packs (pick the best source)", "", "| Species | Pack · skin px · cubes/bones · animations |", "|---|---|"]
    for k in sorted(by):
        src = by[k]
        if len({p for p, _ in src}) < 2: continue
        cells = "<br>".join(f"{p.split('.')[0]} · {r['tex_px']} px · {r['cubes']}/{r['bones']} · {', '.join(r['anims'][:5])}" for p, r in src)
        L.append(f"| **{k}**{' (vanilla mob)' if k in VANILLA else ''} | {cells} |")
    L += ["", "## Every species by pack", ""]
    for pk, rows in catalog.items():
        L.append(f"### {pk} ({len(rows)})"); L.append("")
        L.append(", ".join(sorted({r['key'] + ('*' if r['key'] in VANILLA else '') for r in rows})) or "(no creatures)"); L.append("")
    L.append("`*` = a vanilla Minecraft mob (these packs would override or duplicate it).")
    (OUT / "ADDON-CATALOGUE-2026-09-30.md").write_text("\n".join(L))
    print(len(by), "species keys;", sum(1 for k in by if len({p for p, _ in by[k]}) >= 2), "in 2+ packs")
    for pk, rows in catalog.items(): print(f"{pk}: {len(rows)} client entities")


if __name__ == "__main__":
    main()
