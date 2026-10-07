#!/usr/bin/env python3
"""std_families.py — MOTION FAMILIES for p22 sharing (his 12:51 rule, 10-01: "species correct animations stay with species
correct animations … I only want it applied to species that would use it in real life. I don't want any species to inherit
animations that don't fit the species or animal").

A family = animals that move with the same anatomy (skeleton + gait): a clip may be offered from one member to another ONLY
inside a family, and ONLY for a kind the family really does in life (KINDS). Everything offered is an EXTRA candidate
`fam_<kind>` he keeps or drops in p22; nothing replaces an animal's own clips.

Rules are ordered regexes on the entity id (first match wins). Real-world notes say why the grouping holds. Creatures that
match nothing are ALONE (no cross-species offers) — listed in the report, never guessed.
API: family_of(entity_id) -> (family, kinds) or (None, ()); FAMILIES (ordered)."""
import re

ALL = ("walk", "run", "idle", "attack", "sleep", "sit", "swim", "fly", "eat", "jump", "call")
Q_BASE = ("walk", "run", "idle", "attack", "sleep", "eat", "call")

# HEAD NOUN of the animal decides (10-01 15:0x rewrite after a substring pass mis-filed 12 animals: leopard GECKO as a cat,
# JERBOA as a snake ("jer-boa_"), mouse LEMURS as mice, lanTERN fish / easTERN newt as terns, HEDGEhogs as pigs, horse FLY as a
# horse, peafOWL as an owl, seaLION as a cat, elephant BEETLE as an elephant, hammerHEAD shark as a ratite).
# AnF ids name the group FIRST ("gecko_leopard", "fly_horse", "crab_spider"); every other creator uses English order
# ("snow_leopard", "hammerhead_shark") -> the head is the LAST token. Compound names that end in another animal's noun are
# resolved first (COMPOUND).
CREATOR = {"anf", "wa", "ws", "wwa", "ysav", "ytri", "ifs"}
DROP = {"female", "male", "baby"}
COMPOUND = {"red_panda": "red_panda", "prairie_dog": "prairie_dog", "komodo_dragon": "komodo", "gila_monster": "gila",
            "bird_of_paradise": "songbird_bop", "secretary_bird": "secretary_bird", "sea_lion": "sealion", "dik_dik": "dikdik",
            "honey_badger": "badger", "monitor_lizard": "lizard", "lemur_mouse": "lemur", "emperor_penguin": "penguin",
            "trader_llama": "llama", "glow_squid": "squid", "cave_spider": "spider", "polar_bear": "bear"}

# family -> (head nouns, kinds, real-world basis)
FAMILY_TABLE = {
    "raptor": ({"eagle", "hawk", "vulture", "falcon", "kite", "osprey"}, ("walk", "idle", "attack", "fly", "eat", "sleep", "call"),
               "accipitrids: perch-and-stride walk, talon strike, soaring flight"),
    "owl": ({"owl"}, ("walk", "idle", "attack", "fly", "eat", "sleep", "call"), "owls: upright perch, silent flight"),
    "wader": ({"flamingo", "heron", "egret", "stork", "crane", "shoebill", "ibis", "spoonbill"},
              ("walk", "idle", "attack", "fly", "eat", "sleep", "call"),
              "long-legged waders: high-stepping walk on the backward-bending ankle (his example), spear feeding, one-leg rest"),
    "waterfowl": ({"duck", "goose", "swan"}, ("walk", "run", "idle", "attack", "swim", "fly", "eat", "sleep", "call"),
                  "ducks / geese / swans: waddle, paddle swim"),
    "larid": ({"gull", "tern"}, ("walk", "idle", "attack", "swim", "fly", "eat", "sleep", "call"), "gulls / terns"),
    "pelican": ({"pelican"}, ("walk", "idle", "swim", "fly", "eat", "sleep", "call"), "pelicans"),
    "galliform": ({"chicken", "turkey", "peafowl", "pheasant", "quail"}, ("walk", "run", "idle", "attack", "fly", "eat", "sleep", "call"),
                  "ground fowl: strut, peck, short flutter"),
    "ratite": ({"ostrich", "emu", "cassowary", "rhea"}, ("walk", "run", "idle", "attack", "eat", "sleep", "call"),
               "flightless runners: long stride, kick"),
    "corvid": ({"crow", "raven", "magpie", "jay", "bluejay"}, ("walk", "run", "idle", "attack", "fly", "eat", "sleep", "call"),
               "crows / jays: walk + hop"),
    "columbid": ({"dove", "pigeon"}, ("walk", "idle", "fly", "eat", "sleep", "call"), "pigeons: head-bob walk"),
    "songbird": ({"robin", "tit", "sparrow", "finch", "canary", "cardinal", "songbird_bop"},
                 ("walk", "idle", "fly", "eat", "sleep", "call", "jump"), "small perching birds: hop, flit"),
    "parrot": ({"parrot", "budgie", "kakapo", "macaw", "cockatoo"}, ("walk", "idle", "fly", "eat", "sleep", "call"), "parrots"),
    "bigbill": ({"toucan", "hornbill", "aracari"}, ("walk", "idle", "fly", "eat", "sleep", "call", "jump"), "toucans / hornbills"),
    "canid": ({"wolf", "dog", "fox", "coyote", "jackal"}, ("walk", "run", "idle", "attack", "sleep", "sit", "swim", "eat", "jump", "call"),
              "dogs / wolves / foxes: digitigrade trot + gallop, sit on haunches"),
    "hyaenid": ({"hyena", "hyenas"}, ("walk", "run", "idle", "attack", "sleep", "sit", "eat", "call"), "hyenas: sloped back"),
    "felid": ({"lion", "lioness", "tiger", "leopard", "cheetah", "cougar", "puma", "caracal", "lynx", "serval", "ocelot", "jaguar", "cat"},
              ("walk", "run", "idle", "attack", "sleep", "sit", "eat", "jump", "call"), "cats: stalk, pounce, sit, curl"),
    "ursid": ({"bear", "panda"}, ("walk", "run", "idle", "attack", "sleep", "sit", "swim", "eat", "call"), "bears: amble, rear, sit"),
    "procyonid": ({"raccoon", "red_panda", "coati"}, ("walk", "run", "idle", "attack", "sleep", "sit", "eat", "jump"),
                  "raccoons / red pandas: plantigrade, hand-like paws"),
    "mustelid": ({"badger", "ferret", "stoat", "weasel", "wolverine", "skunk", "mink"},
                 ("walk", "run", "idle", "attack", "sleep", "sit", "eat", "jump"), "weasels + skunks: low bounding gait"),
    "otter": ({"otter"}, ("walk", "run", "idle", "attack", "sleep", "swim", "eat"), "otters"),
    "herpestid": ({"meerkat", "mongoose"}, ("walk", "run", "idle", "attack", "sleep", "sit", "eat"), "meerkats: sentinel sit"),
    "equid": ({"horse", "donkey", "mule", "zebra"}, ("walk", "run", "idle", "attack", "sleep", "eat", "jump", "call"),
              "horses: walk / trot / gallop, kick — NO dog-like sit"),
    "bovine": ({"cow", "mooshroom", "bison", "buffalo", "yak", "gnu"}, ("walk", "run", "idle", "attack", "sleep", "eat", "call"),
               "cattle: heavy walk, lie down"),
    "caprine": ({"sheep", "goat"}, ("walk", "run", "idle", "attack", "sleep", "eat", "jump", "call"), "sheep / goats"),
    "cervid_antelope": ({"deer", "moose", "reindeer", "bongo", "kudu", "impala", "kob", "gazelle", "oryx", "antelope", "tsessebe",
                         "saiga", "dikdik"}, ("walk", "run", "idle", "attack", "sleep", "eat", "jump", "call"), "deer / antelope: bound"),
    "pacer": ({"camel", "llama", "alpaca", "giraffe", "okapi"}, ("walk", "run", "idle", "attack", "sleep", "eat", "call"),
              "camels / llamas / giraffes: PACING gait, kneel to rest"),
    "suid": ({"pig", "boar", "warthog"}, ("walk", "run", "idle", "attack", "sleep", "eat", "call"), "pigs / boars"),
    "proboscid": ({"elephant", "mammoth"}, ("walk", "run", "idle", "attack", "sleep", "swim", "eat", "call"), "elephants"),
    "rhino": ({"rhino"}, ("walk", "run", "idle", "attack", "sleep", "eat", "call"), "rhinos"),
    "murid": ({"mouse", "rat", "hamster", "gerbil", "lemming"}, ("walk", "run", "idle", "attack", "sleep", "sit", "eat", "jump"),
              "mice / rats / hamsters: scurry, sit up"),
    "sciurid": ({"squirrel", "prairie_dog", "chipmunk", "marmot"}, ("walk", "run", "idle", "sleep", "sit", "eat", "jump", "call"),
                "squirrels / prairie dogs"),
    "lagomorph": ({"rabbit", "hare"}, ("walk", "run", "idle", "sleep", "sit", "eat", "jump"), "rabbits / hares: hop"),
    "hedgehog": ({"hedgehog"}, ("walk", "run", "idle", "sleep", "eat"), "hedgehogs: shuffle, curl"),
    "myrmecophage": ({"anteater", "aardvark", "pangolin"}, ("walk", "run", "idle", "attack", "sleep", "eat"), "ant-eaters"),
    "great_ape": ({"gorilla", "chimpanzee", "chimp", "orangutan", "bonobo"},
                  ("walk", "run", "idle", "attack", "sleep", "sit", "eat", "jump", "call"), "great apes: knuckle-walk, sit"),
    "monkey": ({"baboon", "gelada", "mandrill", "capuchin", "monkey", "macaque"},
               ("walk", "run", "idle", "attack", "sleep", "sit", "eat", "jump", "call"), "monkeys"),
    "lemur": ({"lemur"}, ("walk", "run", "idle", "sleep", "sit", "eat", "jump", "call"), "lemurs: leap, sit"),
    "pinniped": ({"seal", "sealion"}, ("walk", "idle", "attack", "sleep", "swim", "eat", "call"), "seals: galumph, swim"),
    "walrus": ({"walrus"}, ("walk", "idle", "attack", "sleep", "swim", "eat", "call"), "walruses"),
    "dolphin": ({"dolphin", "orca", "beluga", "porpoise"}, ("idle", "attack", "swim", "jump", "call"), "toothed whales"),
    "whale": ({"whale"}, ("idle", "swim", "jump", "call"), "baleen whales"),
    "crocodilian": ({"alligator", "croc", "crocodile", "gavial", "caiman"}, ("walk", "run", "idle", "attack", "sleep", "swim", "eat"),
                    "crocodilians: high walk, tail swim"),
    "lizard": ({"gecko", "iguana", "lizard", "komodo", "gila", "chameleon"}, ("walk", "run", "idle", "attack", "sleep", "eat"),
               "lizards: sprawling S-gait"),
    "salamander": ({"newt", "salamander", "axolotl"}, ("walk", "idle", "swim", "eat", "sleep"), "salamanders"),
    "snake": ({"snake", "cobra", "viper", "python", "boa", "mamba", "anaconda", "rattlesnake"},
              ("walk", "run", "idle", "attack", "sleep", "swim"), "snakes: undulation, strike"),
    "turtle": ({"turtle", "tortoise"}, ("walk", "idle", "sleep", "swim", "eat", "attack"), "turtles / tortoises"),
    "anuran": ({"frog", "toad"}, ("walk", "idle", "jump", "swim", "eat", "sleep", "call"), "frogs / toads: hop"),
    "shark": ({"shark"}, ("idle", "attack", "swim"), "sharks"),
    "ray": ({"ray", "stingray"}, ("idle", "attack", "swim"), "rays: wing-flap swim"),
    "eel": ({"eel", "moray"}, ("idle", "attack", "swim"), "eels"),
    "fish": ({"cod", "salmon", "bass", "catfish", "cavefish", "piranha", "tropicalfish", "pufferfish", "fish", "swordfish", "toadfish",
              "anglerfish", "blobfish"}, ("idle", "attack", "swim", "jump"), "bony fish"),
    "cephalopod": ({"squid", "octopus"}, ("idle", "attack", "swim"), "squid / octopus"),
    "jellyfish": ({"jellyfish"}, ("idle", "swim"), "jellyfish"),
    "crab": ({"crab"}, ("walk", "run", "idle", "attack", "eat", "sleep"), "crabs: sideways walk"),
    "lobster": ({"lobster", "shrimp", "isopod"}, ("walk", "idle", "attack", "swim", "eat"), "lobsters / shrimp"),
    "spider": ({"spider"}, ("walk", "run", "idle", "attack", "jump"), "spiders"),
    "scorpion": ({"scorpion"}, ("walk", "run", "idle", "attack"), "scorpions"),
    "beetle": ({"beetle", "ladybug", "firefly"}, ("walk", "idle", "fly", "attack", "eat"), "beetles (fireflies are beetles)"),
    "lepidoptera": ({"butterfly", "moth"}, ("idle", "fly", "eat"), "butterflies / moths"),
    "fly_insect": ({"fly"}, ("walk", "idle", "fly", "eat"), "flies"),
    "hymenoptera": ({"bee", "wasp", "hornet"}, ("walk", "idle", "attack", "fly", "eat"), "bees / wasps"),
    "ant": ({"ant", "termite"}, ("walk", "run", "idle", "attack", "eat"), "ants / termites"),
    "caterpillar": ({"caterpillar"}, ("walk", "idle", "eat"), "caterpillars"),
    "centipede": ({"centipede"}, ("walk", "run", "idle", "attack"), "centipedes"),
    "orthoptera": ({"cricket", "grasshopper"}, ("walk", "idle", "jump", "call"), "crickets / grasshoppers"),
    "worm": ({"earthworm"}, ("walk", "idle"), "earthworms"),
    "gastropod": ({"snail", "slug"}, ("walk", "idle", "eat"), "snails / slugs"),
    "sessile": ({"shellfish", "clam", "scallop", "urchin", "starfish"}, ("idle",), "barely-moving shellfish"),
}
NOUN = {n: f for f, (nouns, _, _) in FAMILY_TABLE.items() for n in nouns}
FAMILIES = [(f, sorted(nouns), kinds, why) for f, (nouns, kinds, why) in FAMILY_TABLE.items()]
EXCLUDE = re.compile(r"xp_bottle|_egg|minecraft:phantom|minecraft:bat$")   # objects / one-off rigs: never in a family


def head_noun(entity_id):
    name = entity_id.split(":", 1)[-1]
    for comp, noun in COMPOUND.items():
        if comp in name:
            return noun
    toks = [t for t in name.split("_") if t and t not in CREATOR and t not in DROP]
    if not toks:
        return None
    first = toks[0] if name.endswith("_anf") else toks[-1]
    if first in NOUN:
        return first
    for t in ([toks[-1], toks[0]] if name.endswith("_anf") else [toks[0], toks[-1]]) + toks:   # group-first names outside AnF
        if t in NOUN:
            return t
    return first


def family_of(entity_id):
    if EXCLUDE.search(entity_id):
        return None, ()
    f = NOUN.get(head_noun(entity_id))
    return (f, FAMILY_TABLE[f][1]) if f else (None, ())


if __name__ == "__main__":
    import json
    import sys
    from collections import defaultdict
    sys.path.insert(0, "/home/claude/tools")
    import std_convert as S
    census = json.load(open("/home/claude/_docs/standard/SKELETON-CENSUS.json"))
    staged = {f.name.split(".entity.json")[0] for f in S.STAGE.glob("*/entity/std/*.entity.json")}
    fam, alone = defaultdict(list), []
    for c in census:
        if S.slug_of(c["id"]) not in staged:
            continue
        f, _ = family_of(c["id"])
        (fam[f].append(c["id"]) if f else alone.append(c["id"]))
    for f, ids in sorted(fam.items(), key=lambda t: -len(t[1])):
        print(f"{f:16s} {len(ids):3d}  {' '.join(i.split(':')[1] for i in ids[:9])}{' …' if len(ids) > 9 else ''}")
    print(f"ALONE ({len(alone)}):", " ".join(alone))
