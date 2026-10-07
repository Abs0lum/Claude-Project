#!/usr/bin/env python3
"""menagerie_census.py — D-C349 (his 20:10 CT 09-30): the TRUE duplicate list for the per-animal comparison + the port list.

addon_catalogue.py grouped by the raw entity key, so the same animal under a Portuguese / Spanish name (elefante, jirafa, leao, gorila …)
or a sub-species key (giraffe_masai, elephant_african) never met its English twin: 53 groups was an undercount (P11 premise audit).
Here every client entity of the 14 add-ons (from _logs/addon_catalogue.json) AND every creature already in our packs (vanilla +
Patrix via RP-06/07, the StripMine sf_nba creatures, from _docs/sizes/roster_size_census.json) is mapped to ONE English animal group.

Output _docs/menagerie/MENAGERIE-CENSUS-2026-09-30.md + _logs/menagerie_census.json:
  COMPARE  groups with 2+ add-on versions, or an add-on version + our own sf_nba version (the comparison test list)
  VANILLA  groups that are a vanilla mob (Patrix covers it): add-on versions listed as variant skins / later decisions
  NEW      groups only one add-on has and we don't — straight to the port list
  PROPS    eggs, vehicles, items, feeders … (travel with their creature, never compared)
"""
import json, re, collections
from pathlib import Path

ROOT = Path("/home/claude")
CAT = json.loads((ROOT / "_logs/addon_catalogue.json").read_text())
OURS = [r["id"] for r in json.loads((ROOT / "_docs/sizes/roster_size_census.json").read_text())["rows"]]
SHORT = {"Animals-and-Fauna.mcaddon": "AnF", "Immersive-Fauna-Savanna-1_5_0.mcaddon": "IFS", "World-Animals-Add-on.mcaddon": "WA",
         "jurassic-project-kingdom-of-the-giants.mcaddon": "JP", "wildlife-sanctuary-mobs-plus.mcaddon": "WS", "wwa-animals-r.mcpack": "WWA",
         "ycreatures-savanna-v1_0_5.mcaddon": "YSav", "ycreaturestrial-rp-v2_0_4.mcpack": "YTri"}

# Portuguese (ycreatures) / Spanish (Immersive Fauna) / odd spellings -> English group
TRANSL = {
    "agua_viva": "jellyfish", "aguia": "eagle", "aguia_africana": "eagle", "aguia_pescadora": "eagle", "alcef": "moose", "alcem": "moose",
    "anta": "tapir", "arraia": "stingray", "avestruz": "ostrich", "babuino": "baboon", "baleia": "whale", "ballena": "whale", "beijaflor": "hummingbird",
    "bisao": "bison", "boto": "river_dolphin", "pink_dolphin": "river_dolphin", "bufalo": "buffalo", "calango": "lizard", "camelo": "camel",
    "canario": "canary", "canguru": "kangaroo", "capivara": "capybara", "caranguejo": "crab", "castor": "beaver", "casuar": "cassowary",
    "cervof": "deer", "cervom": "deer", "chimpanze": "chimpanzee", "cisne": "swan", "coala": "koala", "coiote": "coyote", "coruja": "owl",
    "suindara": "owl", "crocodilo": "crocodile", "elefante": "elephant", "feneco": "fennec", "foca": "seal", "gacela": "gazelle", "gazela": "gazelle",
    "gazelaf": "gazelle", "gamba": "opossum", "girafa": "giraffe", "jirafa": "giraffe", "gorila": "gorilla", "guepardo": "cheetah", "hiena": "hyena",
    "hyenas": "hyena", "hipopotamo": "hippo", "hippopotamus": "hippo", "imperador": "penguin", "impalaf": "impala", "inhala": "nyala",
    "inhalaf": "nyala", "jabali": "boar", "javali": "boar", "jabuti": "tortoise", "land_turtle": "tortoise", "jacare": "caiman",
    "kobo": "kob", "kobof": "kob", "komodo": "komodo_dragon", "leao": "lion", "leao_branco": "lion", "leoa": "lion", "leoa_branca": "lion",
    "leon_f": "lion", "leon_m": "lion", "white_lion": "lion", "baby_lion": "lion", "lemure": "lemur", "leopardo_africano": "leopard",
    "lontra": "otter", "mabeco": "african_wild_dog", "marabu": "stork", "monitor": "monitor_lizard", "naja": "cobra",
    "orangotango": "orangutan", "ornintorrinco": "platypus", "ornitorrinco_original": "platypus", "palanca": "sable_antelope",
    "panda_vermelho": "red_panda", "peixe_boi": "manatee", "polvo": "octopus", "preguica": "sloth", "racoon": "raccoon", "ratel": "honey_badger",
    "rinoceronte": "rhino", "rhinoceros": "rhino", "suricato": "meerkat", "tamandua": "anteater", "tartaruga_alligator": "snapping_turtle",
    "toupeira": "mole", "tubarao": "shark", "tucano": "toucan", "tucan": "toucan", "urso": "bear", "urubu": "vulture", "vibora": "viper",
    "cacu": "catfish", "cupim": "termite", "erizo": "hedgehog", "lucienaga": "firefly", "cyanocitta_cristata": "blue_jay", "bluejay": "blue_jay",
    "jay_blue": "blue_jay", "dik_dik": "dik_dik", "gaint_squid": "giant_squid", "prarie_dog": "prairie_dog", "road_runner": "roadrunner",
    "capuchin_monkeys": "capuchin", "capuchin_monkey": "capuchin", "howler_monkey": "monkey", "monkey": "monkey", "hammer": "hammerhead_shark",
    "hammer_head_shark": "hammerhead_shark", "white_shark": "shark", "great_white_shark": "shark", "tiger_shark": "shark", "thresher_shark": "shark",
    "fennec_fox": "fennec", "peafowl": "peacock", "female_lion": "lion", "male_lion": "lion", "ravenous_hyena": "hyena", "black_bear": "bear",
    "brown_bear": "bear", "grizzly_bear": "bear", "white_tiger": "tiger", "snow_leopard": "snow_leopard", "panther": "leopard",
    "spotted_moray": "moray", "humpback_whale": "whale", "african_elephant": "elephant", "asian_elephant": "elephant", "secretary_bird": "secretary_bird",
    "emperor_penguin": "penguin", "blue_penguin": "penguin", "penguin_african": "penguin", "real_penguin": "penguin", "red_panda": "red_panda",
    "jellyfish_wa": "jellyfish", "small_jellyfish": "jellyfish", "desert_scorpion": "scorpion", "jungle_scorpion": "scorpion",
    "bark_scorpion": "scorpion", "tiger_rattlesnake": "rattlesnake", "rattlesnake": "rattlesnake", "coral_snake": "snake", "snake_coral": "snake",
    "snake_scarlet": "snake", "cave_snake": "snake", "fire_ant": "ant", "sulcata_turtle": "tortoise", "snapping_turtle": "snapping_turtle",
    "giant_isopod": "isopod", "stingray": "stingray", "ray": "stingray", "manta_ray": "stingray", "cendrawasih": "bird_of_paradise",
    "bumblebee_shrimp": "shrimp", "hermit_crab": "crab", "bombardier_beetle": "beetle", "kakapo": "kakapo",
    "bear_polar": "polar_bear", "shellfish_starfish": "starfish", "shellfish_clam": "clam", "shellfish_scallop": "scallop", "shellfish_seaurchin": "sea_urchin",
}
# Animals-and-Fauna (and others) "<family>_<sub>" keys: first word -> group (some families renamed)
FAMILY = {"lioness": "lion", "croc": "crocodile", "chick": "chicken", "rooster": "chicken", "bull": "cow", "hog": "boar", "cow": "cow",
          "dog": "dog", "parakeet": "parrot", "budgie": "parrot", "lovebird": "parrot", "gull": "seagull", "giraffe": "giraffe",
          "elephant": "elephant", "zebra": "zebra", "tiger": "tiger", "lion": "lion", "bear": "bear", "rhino": "rhino", "deer": "deer",
          "moose": "moose", "camel": "camel", "flamingo": "flamingo", "pelican": "pelican", "penguin": "penguin", "eagle": "eagle",
          "hawk": "hawk", "owl": "owl", "alligator": "alligator", "monkey": "monkey", "leopard": "leopard", "wolf": "wolf", "otter": "otter",
          "buffalo": "buffalo", "goat": "goat", "horse": "horse", "pig": "pig", "rabbit": "rabbit", "hare": "hare", "rat": "rat",
          "mouse": "mouse", "hamster": "hamster", "hedgehog": "hedgehog", "stork": "stork", "crane": "crane", "heron": "heron",
          "egret": "egret", "duck": "duck", "goose": "goose", "swan": "swan", "dove": "dove", "pigeon": "pigeon", "crow": "crow",
          "raven": "raven", "tit": "tit", "toucan": "toucan", "tern": "tern", "vulture": "vulture", "parrot": "parrot", "dolphin": "dolphin",
          "octopus": "octopus", "crab": "crab", "turtle": "turtle", "tortoise": "tortoise", "snake": "snake", "frog": "frog", "toad": "toad",
          "newt": "newt", "gecko": "gecko", "lemur": "lemur", "lemming": "lemming", "stoat": "stoat", "ferret": "ferret", "ant": "ant",
          "bee": "bee", "beetle": "beetle", "butterfly": "butterfly", "caterpillar": "caterpillar", "moth": "moth", "dragonfly": "dragonfly",
          "fly": "fly", "ladybug": "ladybug", "spider": "spider", "centipede": "centipede", "cricket": "cricket", "earthworm": "earthworm",
          "wasp": "wasp", "hornet": "hornet", "stickinsect": "stick_insect", "chicken": "chicken", "jay": "jay", "seal": "seal",
          "shark": "shark", "squirrel": "squirrel", "penguin": "penguin", "sloth": "sloth", "fox": "fox", "orca": "orca", "whale": "whale",
          "jellyfish": "jellyfish", "kangaroo": "kangaroo", "iguana": "iguana", "lizard": "lizard", "puffin": "puffin", "magpie": "magpie",
          "robin": "robin", "platypus": "platypus", "gorilla": "gorilla", "hippo": "hippo", "hyena": "hyena", "meerkat": "meerkat",
          "ostrich": "ostrich", "panda": "panda", "termite": "termite", "walrus": "walrus", "mandrill": "mandrill", "mole": "mole",
          "orangutan": "orangutan", "gerbil": "gerbil", "sheep": "sheep", "scorpion": "scorpion", "slug": "slug", "snail": "snail", "bat": "bat", "badger": "badger", "beaver": "beaver", "chameleon": "chameleon", "lobster": "lobster",
          "grasshopper": "grasshopper", "firefly": "firefly", "raccoon": "raccoon", "kiwi": "kiwi", "emu": "emu", "zebu": "cow"}
PROP = re.compile(r"(_egg$|_cracked_egg$|^egg_|_sac$|_spit$|^horn_|boat|safari_car|^bag_items$|^village_|^banner$|^hanging_banner$|^chair$|"
                  r"feeder$|^cage$|^plushies$|^info_book$|^dirt_trail$|^hamster_wheel$|^firefly_jar$|_projectile$|^reptile_tail$|^beekeeper$|^nomad$|^clam$)")
VANILLA = set("""allay armadillo axolotl bat bee blaze bogged breeze camel cat cave_spider chicken cod cow creeper dolphin donkey drowned elder_guardian
ender_dragon enderman endermite evocation_illager fox frog ghast glow_squid goat guardian hoglin horse husk iron_golem llama magma_cube mooshroom mule
ocelot panda parrot phantom pig piglin piglin_brute pillager polar_bear pufferfish rabbit ravager salmon sheep shulker silverfish skeleton
slime sniffer snow_golem spider squid stray strider tadpole trader_llama tropicalfish turtle vex villager vindicator wandering_trader warden witch wither
wolf zoglin zombie zombie_horse zombie_pigman zombie_villager creaking happy_ghast nautilus copper_golem""".split())
FANTASY_JP = {"archel": "archelon", "b_quetz": "quetzalcoatlus", "fb_quetz": "quetzalcoatlus", "leed": "leedsichthys", "meg": "megalodon",
              "mosa": "mosasaurus", "r_mosa": "mosasaurus", "r_rex": "t_rex", "spino": "spinosaurus", "titano": "titanosaurus", "jellyfish": "jellyfish_jp"}


def group_of(key, pack):
    if PROP.search(key): return None
    if pack == "JP": return FANTASY_JP.get(key, key)
    if key in TRANSL: return TRANSL[key]
    if key in VANILLA or key in FAMILY.values(): return FAMILY.get(key, key)
    head = key.split("_")[0]
    if head in FAMILY: return FAMILY[head]
    return key


def main():
    groups = collections.defaultdict(list); props = []
    for pack, rows in CAT.items():
        s = SHORT.get(pack)
        if not s: continue
        for r in rows:
            g = group_of(r["key"], s)
            if g is None: props.append((s, r["key"])); continue
            groups[g].append({"src": s, "key": r["key"], "id": r["id"], "px": r.get("tex_px"), "cubes": r.get("cubes"), "bones": r.get("bones"),
                              "anims": r.get("anims", [])[:6], "file": r.get("file")})
    ours = collections.defaultdict(list)
    for i in OURS:
        ns, k = i.split(":")
        if ns == "sf_nba":
            g = group_of(k, "ours")
            if g: ours[g].append(i)
        else:
            ours[{"polar_bear": "polar_bear", "villager_v2": "villager", "zombie_villager_v2": "zombie_villager", "tropicalfish": "tropical_fish"}.get(k, k)].append(i)
    compare, vanilla, new = {}, {}, {}
    for g, cand in sorted(groups.items()):
        srcs = {c["src"] for c in cand}
        mine = ours.get(g, [])
        van = g in VANILLA or any(m.startswith("minecraft:") for m in mine)
        rec = {"candidates": cand, "ours": mine}
        if van: vanilla[g] = rec
        elif len(srcs) >= 2 or mine: rec["kind"] = "A" if len(srcs) >= 2 else "B"; compare[g] = rec
        else: new[g] = rec
    out = {"compare": compare, "vanilla": vanilla, "new": new, "props": props}
    (ROOT / "_logs/menagerie_census.json").write_text(json.dumps(out, indent=1))
    L = ["# Menagerie census — the true duplicate list + the port list (2026-09-30, D-C349)", "",
         "Every creature in the 14 add-ons mapped to one English animal group (Portuguese / Spanish names translated, sub-species folded into "
         "their animal), then compared with what our packs already have (vanilla + Patrix, StripMine sf_nba). `tools/menagerie_census.py`.", "",
         f"- **COMPARE** (2+ versions to choose from): **{len(compare)} animals** = A {sum(r['kind'] == 'A' for r in compare.values())} with 2+ add-on versions "
         f"+ B {sum(r['kind'] == 'B' for r in compare.values())} with one add-on version vs our current StripMine (sf_nba) one",
         f"- **VANILLA** (a vanilla mob Patrix already covers; add-on versions = possible variant skins): **{len(vanilla)}**",
         f"- **NEW** (only one add-on has it, we don't): **{len(new)} animals**",
         f"- PROPS (eggs, boats, feeders, items — travel with their creature): {len(props)}", "",
         "## COMPARE", "", "| Animal | Versions (source · key · skin px · cubes/bones) | Ours now |", "|---|---|---|"]
    for g, rec in compare.items():
        v = "<br>".join(f"{c['src']} · {c['key']} · {c['px']} px · {c['cubes']}/{c['bones']}" for c in rec["candidates"])
        L.append(f"| **{g}** ({rec['kind']}) | {v} | {', '.join(rec['ours']) or '—'} |")
    L += ["", "## VANILLA (Patrix covers the base mob)", "", "| Animal | Add-on versions |", "|---|---|"]
    for g, rec in vanilla.items():
        L.append(f"| {g} | {len(rec['candidates'])}: " + ", ".join(f"{c['src']}:{c['key']}" for c in rec["candidates"][:12]) + (" …" if len(rec["candidates"]) > 12 else "") + " |")
    L += ["", "## NEW (port list)", "", "| Animal | Source · keys |", "|---|---|"]
    for g, rec in new.items():
        L.append(f"| {g} | {rec['candidates'][0]['src']} · " + ", ".join(c["key"] for c in rec["candidates"]) + " |")
    L += ["", "## PROPS", "", ", ".join(f"{s}:{k}" for s, k in props)]
    (ROOT / "_docs/menagerie/MENAGERIE-CENSUS-2026-09-30.md").write_text("\n".join(L) + "\n")
    n_entities = sum(len(r["candidates"]) for r in new.values())
    print(f"COMPARE {len(compare)} · VANILLA {len(vanilla)} · NEW {len(new)} animals ({n_entities} entities) · PROPS {len(props)}")
    return out


if __name__ == "__main__":
    main()
