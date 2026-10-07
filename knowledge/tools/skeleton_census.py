#!/usr/bin/env python3
"""skeleton_census.py — PHASE 0 of the standardization program (D-C364, his 02:20 / 02:25 CT 10-01). READ-ONLY.
For every mob the game draws in his stack (RP-07 1.4.38, RP-06 1.4.24, RP-08 1.4.8; vanilla for the rest):
  * source: 'patrix' (our Patrix conversion: geometry or animations named pw_* / pw.), 'ours-naturalist' (sf_nba), 'ported:<pack>'
    (pw:*_<pack>), 'vanilla' (Mojang model + animations)
  * skeleton: bones (name, parent, pivot, rotation, cube count, mirror), depth of the parent chain, total cubes, wing / leg / fin /
    tail / arm / antenna / neck / jaw bone counts (by name)
  * animations (every one the entity's map names, resolved in the stack): length, loop, bones driven, channels, keyframe counts,
    interpolation (linear / catmullrom), Molang-driven channels — and a plain quality figure: keyframed channel-keys + bones driven
    (more joints moving through more poses = richer; it is a sorting aid, his eye decides)
  * body plan (rule table on species + bone vocabulary): quadruped / biped_ape / bird / bat / insect_flying / insect_walking /
    arachnid / snake / lizard_croc / amphibian / fish / cetacean / crustacean / cephalopod / jellyfish / turtle / other
Output: _docs/standard/SKELETON-CENSUS.json (+ a summary on stdout)"""
import glob, json, re, sys
from collections import Counter, defaultdict
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML

ROOT = Path("/home/claude")
RPS = [ROOT / "_build/rp07-1438", ROOT / "_build/rp06-1424", ROOT / "_build/rp08-148", ROOT / "_intake/bedrock-samples/resource_pack"]
SIZES = {r["id"]: r for r in json.loads((ROOT / "_docs/sizes/menagerie_real_sizes.json").read_text())}


def jl(p):
    try: return ML._parse_json(Path(p).read_text(encoding="utf-8-sig"))
    except Exception: return None


def index():
    geo, anim, ctrl = {}, {}, {}
    for rp in RPS:
        for f in glob.glob(str(rp / "models/**/*.json"), recursive=True):
            d = jl(f)
            if not isinstance(d, dict): continue
            for g in d.get("minecraft:geometry", []) or []:
                geo.setdefault(g.get("description", {}).get("identifier"), (g.get("bones", []), f))
            for k, v in d.items():
                if k.startswith("geometry.") and isinstance(v, dict): geo.setdefault(k.split(":")[0], (v.get("bones", []), f))
        for f in glob.glob(str(rp / "animations/**/*.json"), recursive=True):
            d = jl(f)
            if isinstance(d, dict):
                for k, v in (d.get("animations") or {}).items(): anim.setdefault(k, (v, f))
        for f in glob.glob(str(rp / "animation_controllers/**/*.json"), recursive=True):
            d = jl(f)
            if isinstance(d, dict):
                for k, v in (d.get("animation_controllers") or {}).items(): ctrl.setdefault(k, (v, f))
    return geo, anim, ctrl


def clients():
    out = {}
    for rp in RPS:
        for f in glob.glob(str(rp / "entity/**/*.json"), recursive=True):
            d = jl(f)
            if not isinstance(d, dict): continue
            de = (d.get("minecraft:client_entity") or {}).get("description") or {}
            if de.get("identifier") and de["identifier"] not in out: out[de["identifier"]] = (de, f, rp.name)
    return out


ROLE = [("wing", r"wing|feather_?(l|r)|aile|ala\b|asa"), ("leg", r"leg|foot|feet|paw|thigh|shin|knee|perna|pata|hoof|claw_?leg"),
        ("arm", r"arm|hand|elbow|braco"), ("tail", r"tail|cauda|cola"), ("head", r"head|skull|cabeca|cabeza"), ("neck", r"neck|pescoco|cuello"),
        ("jaw", r"jaw|mouth|mandib|beak|bico|bill"), ("fin", r"fin\b|fin_|flipper|barbatana|aleta"), ("antenna", r"antenna|antena"),
        ("body", r"body|torso|chest|belly|corpo|cuerpo|pelvis|hip|spine")]


def roles(bones):
    c = Counter()
    for b in bones:
        n = b.get("name", "").lower()
        for r, rx in ROLE:
            if re.search(rx, n): c[r] += 1; break
    return dict(c)


def depth(bones):
    par = {b.get("name"): b.get("parent") for b in bones}
    best = 0
    for n in par:
        d, seen = 0, set()
        while n in par and par[n] and n not in seen: seen.add(n); n = par[n]; d += 1
        best = max(best, d)
    return best


def anim_stats(a):
    bones = a.get("bones") or {}
    keys, channels, molang, catmull = 0, 0, 0, 0
    for b, ch in bones.items():
        if not isinstance(ch, dict): continue
        for cname, v in ch.items():
            if cname not in ("rotation", "position", "scale"): continue
            channels += 1
            if isinstance(v, dict):
                times = [t for t in v if re.match(r"^-?[0-9.]+$", str(t))]
                keys += len(times)
                catmull += sum(1 for t in times if isinstance(v[t], dict) and v[t].get("lerp_mode") == "catmullrom")
                if not times: molang += 1
            elif isinstance(v, (list, str)):
                if any(isinstance(x, str) and re.search(r"[a-z]", x) for x in (v if isinstance(v, list) else [v])): molang += 1
                keys += 1
    return {"bones_driven": len(bones), "channels": channels, "keyframes": keys, "molang_channels": molang, "catmullrom_keys": catmull,
            "length": a.get("animation_length"), "loop": a.get("loop"), "quality": keys + 2 * molang + len(bones)}


RP_OF = {}


def source(i, de, gid, anim_ids):
    if i.startswith("sf_nba:"): return "ours-naturalist"
    m = re.match(r"pw:.*_(anf|wa|ws|wwa|ysav|ytri|ifs)$", i)
    if m: return f"ported:{m.group(1)}"
    if i.startswith("minecraft:"): return "patrix" if RP_OF.get(i) != "resource_pack" else "vanilla"   # our RPs carry the Patrix ports
    return "other"


PLAN_RULES = [("object", r"arrow|boat|minecart|potion|fireball|skull|bed\b|pot\b|spawner|orb|pearl|snowball|egg\b|trident|bullet|charge|"
                         r"crystal|signal|fang|rocket|hook|knot|stand\b|spit|camera|xp_|agent|npc|cushion|tripod|player"),
              ("humanoid", r"zombie|skeleton|stray|husk|drowned|bogged|parched|villager|pillager|vindicator|evocation|illusioner|witch|"
                           r"piglin|wandering_trader|enderman|iron_golem|snow_golem|copper_golem|giant|wither_skeleton|creaking|warden|allay|vex"),
              ("fantasy", r"blaze|breeze|ghast|slime|magma_cube|creeper|shulker|wither\b|ender_dragon|guardian|phantom|endermite|silverfish|"
                          r"strider|ravager|sulfur_cube|nautilus|hoglin|zoglin|happy_ghast|sniffer"),
              ("cetacean", r"whale|orca|dolphin|beluga|porpoise|boto"), ("cephalopod", r"octopus|squid"), ("jellyfish", r"jelly|agua_viva"),
              ("crustacean", r"crab|lobster|shrimp|krill|isopod|scallop|clam|urchin|starfish|shellfish"),
              ("fish", r"fish|shark|ray\b|stingray|manta|cod|salmon|piranha|bass|catfish|eel|moray|swordfish|toadfish|anglerfish|arraia|tropical"),
              ("snake", r"snake|python|cobra|mamba|viper|boa|anaconda|adder|rattle|naja|garter"),
              ("turtle", r"turtle|tortoise|jabuti|terrapin"),
              ("lizard_croc", r"croc|alligator|caiman|gharial|lizard|iguana|gecko|monitor|komodo|chameleon|gila|newt|salamander|axolotl|tegu"),
              ("amphibian", r"frog|toad|tadpole"),
              ("arachnid", r"spider|scorpion|tarantula|tick"),
              ("insect_flying", r"bee|wasp|hornet|fly\b|fly_|butterfly|moth|dragonfly|firefly|beetle|ladybug|ladybird|mosquito|cicada"),
              ("insect_walking", r"ant\b|ant_|termite|cricket|grasshopper|caterpillar|centipede|millipede|stick|worm|slug|snail|cockroach|mantis"),
              ("bat", r"\bbat\b|_bat|bat_"),
              ("bird", r"bird|parrot|chicken|duck|goose|swan|eagle|hawk|owl|crow|raven|jay|robin|finch|sparrow|canary|cardinal|tit_|gull|tern|"
                       r"heron|egret|stork|crane|flamingo|pelican|penguin|ostrich|emu|cassowary|kiwi|kakapo|toucan|hornbill|pigeon|dove|"
                       r"peafowl|turkey|vulture|budgie|magpie|puffin|roadrunner|hummingbird|shoebill|secretary|coruja|suindara|aguia|bird_of"),
              ("biped_ape", r"gorilla|chimp|orangutan|monkey|baboon|mandrill|gelada|capuchin|lemur|macaque|howler|ape\b"),
              ("quadruped", r".")]


PLAN_TOKENS = [   # exact tokens only (P9 self-check: mammoth != moth, elephant != ant, boar != boa, howler != owl, sparrow != arrow)
    ("object", None), ("humanoid", None), ("fantasy", None),
    ("cetacean", {"whale", "orca", "dolphin", "beluga", "porpoise", "boto", "ballena"}),
    ("cephalopod", {"octopus", "squid"}), ("jellyfish", {"jellyfish", "jelly", "agua", "viva"}),
    ("crustacean", {"crab", "lobster", "shrimp", "krill", "isopod", "scallop", "clam", "urchin", "starfish", "shellfish", "quahog"}),
    ("fish", {"fish", "shark", "hammerhead", "ray", "stingray", "manta", "cod", "salmon", "piranha", "bass", "catfish", "eel", "moray",
              "swordfish", "toadfish", "anglerfish", "arraia", "tropicalfish", "pufferfish", "lanternfish", "flying", "cavefish", "blobfish", "pike", "trout"}),
    ("snake", {"snake", "python", "cobra", "mamba", "viper", "boa", "anaconda", "adder", "rattlesnake", "naja", "garter", "rattle"}),
    ("turtle", {"turtle", "tortoise", "jabuti", "terrapin"}),
    ("lizard_croc", {"croc", "crocodile", "crocodilo", "alligator", "caiman", "gharial", "gavial", "lizard", "iguana", "gecko", "monitor", "komodo",
                     "chameleon", "gila", "newt", "salamander", "axolotl", "tegu", "jacare"}),
    ("amphibian", {"frog", "toad", "tadpole"}),
    ("arachnid", {"spider", "scorpion", "tarantula", "tick"}),
    ("insect_flying", {"bee", "wasp", "hornet", "fly", "butterfly", "moth", "dragonfly", "firefly", "beetle", "ladybug", "ladybird", "mosquito", "cicada"}),
    ("insect_walking", {"ant", "termite", "cricket", "grasshopper", "caterpillar", "centipede", "millipede", "stickinsect", "stick", "worm", "earthworm",
                        "slug", "snail", "cockroach", "mantis", "cupim"}),
    ("bat", {"bat"}),
    ("bird", {"bird", "parrot", "chicken", "duck", "goose", "swan", "eagle", "hawk", "owl", "crow", "raven", "jay", "bluejay", "robin", "finch", "sparrow",
              "canary", "cardinal", "tit", "gull", "tern", "heron", "egret", "stork", "crane", "flamingo", "pelican", "penguin", "ostrich", "emu",
              "cassowary", "casuar", "kiwi", "kakapo", "toucan", "tucano", "tucan", "hornbill", "pigeon", "dove", "peafowl", "turkey", "vulture", "budgie",
              "magpie", "puffin", "roadrunner", "hummingbird", "shoebill", "secretary", "coruja", "suindara", "aguia", "kittiwake", "mallard", "eider",
              "cendrawasih", "paradise", "aracari", "harrier", "sparrowhawk", "avestruz", "chick", "cyanocitta", "cristata", "ave"}),
    ("biped_ape", {"gorilla", "gorila", "chimp", "chimpanzee", "orangutan", "monkey", "monkeys", "baboon", "mandrill", "gelada", "capuchin", "lemur", "lemure",
                   "macaque", "howler", "macaco", "babuino"}),
]
OBJ = {"arrow", "boat", "minecart", "potion", "fireball", "skull", "bed", "pot", "spawner", "orb", "pearl", "snowball", "egg", "trident", "bullet",
       "charge", "crystal", "signal", "fang", "rocket", "hook", "knot", "stand", "spit", "camera", "agent", "npc", "cushion", "tripod", "player", "jar",
       "plushies", "lay"}
HUM = {"zombie", "skeleton", "stray", "husk", "drowned", "bogged", "parched", "villager", "pillager", "vindicator", "evocation", "illusioner", "witch",
       "piglin", "wandering", "enderman", "iron", "snow", "copper", "giant", "wither", "creaking", "warden", "allay", "vex"}
FAN = {"blaze", "breeze", "ghast", "slime", "magma", "creeper", "shulker", "wither", "ender", "dragon", "guardian", "phantom", "endermite", "silverfish",
       "strider", "ravager", "sulfur", "nautilus", "hoglin", "zoglin", "happy", "sniffer"}


def body_plan(i, sp, rl):
    ns, name = i.split(":")
    toks = {x for x in re.split(r"[^a-z0-9]+", (name + " " + (sp or "")).lower()) if x}
    if toks & OBJ and ("egg" in toks or "spit" in toks or "jar" in toks or "plushies" in toks or "lay" in toks or ns == "minecraft"): return "object"
    if ns == "minecraft" and toks & HUM: return "humanoid"
    if toks & {"cage", "trail", "book", "wheel", "balloon", "dagger", "projectile", "beans"} or name == "reptile_tail": return "object"
    if toks & {"seal", "sealion", "walrus"}: return "pinniped"
    if toks & {"kangaroo"}: return "macropod"
    if ns == "minecraft" and toks & FAN: return "fantasy"
    for plan, words in PLAN_TOKENS:
        if words and toks & words: return plan
    return "quadruped"


def main():
    geo, anim, ctrl = index()
    rows = []
    global RP_OF
    RP_OF = {i: rp for i, (de, f, rp) in clients().items()}
    for i, (de, f, rp) in sorted(clients().items()):
        gid = (de.get("geometry") or {}).get("default") or next(iter((de.get("geometry") or {}).values()), None)
        bones = (geo.get(gid) or ([], None))[0]
        amap = de.get("animations") or {}
        an = {}
        for short, aid in amap.items():
            if aid in anim: an[short] = dict(id=aid, kind="animation", **anim_stats(anim[aid][0]))
            elif aid in ctrl: an[short] = {"id": aid, "kind": "controller", "states": list((ctrl[aid][0].get("states") or {}))}
            else: an[short] = {"id": aid, "kind": "missing"}
        sp = SIZES.get(i, {}).get("species")
        rl = roles(bones)
        rows.append({"id": i, "rp": rp, "file": f, "source": source(i, de, gid, list(amap.values())), "species": sp,
                     "body_plan": body_plan(i, sp, rl), "geometry": gid, "bones": len(bones), "cubes": sum(len(b.get("cubes") or []) for b in bones),
                     "depth": depth(bones), "roles": rl, "bone_names": [b.get("name") for b in bones],
                     "animations": an, "anim_quality": sum(v.get("quality", 0) for v in an.values() if v.get("kind") == "animation")})
    out = ROOT / "_docs/standard"; out.mkdir(parents=True, exist_ok=True)
    (out / "SKELETON-CENSUS.json").write_text(json.dumps(rows, indent=1))
    by = Counter((r["body_plan"], r["source"].split(":")[0]) for r in rows if r["bones"])
    print(len(rows), "client entities;", sum(1 for r in rows if r["bones"]), "with a skeleton")
    for (bp, src), n in sorted(by.items()): print(f"  {bp:15s} {src:16s} {n}")


if __name__ == "__main__":
    main()
