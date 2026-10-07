#!/usr/bin/env python3
"""size_law.py — L-SIZE-REAL (D-C291, his 19:52 CT 09-29): "the scale I want is compared to REAL LIFE - so whales should be very
large. Same with many of the predators. We're not scaling against vanilla ... Things like the squid, guardians (or other fantasy
creatures like the warden) can remain fantastically large".  SUPERSEDES size_rule "option (a) / big mobs wait" and the x1.20
growth cap (size_rule + StripMine 1.3.3).

ONE CURVE for every real animal (his 5'10" character = 1.875 blocks -> K = 1.0546 blocks per metre):
    real >= 0.60 m : blocks = K x real                       (true scale — whales, elephants, big cats at their real size)
    real <  0.60 m : log ramp 0.22 block at 1 cm -> 0.633 at 60 cm (the tiny stay visible, bigger-in-life stays bigger)
LIKE WITH LIKE — each row says what is compared, measured on the model the same way (visible texels, rest pose):
    hb  = head-body length, tail left out on both sides (vanilla mammals: the calibration his wolf / sheep rulings used)
    max = the model's largest dimension vs the animal's largest real dimension: nose-to-tail-tip for tailed animals, height for
          upright birds / apes / giraffe, wingspan for models posed with spread wings, total length for fish / snakes / reptiles
    h   = standing height
FANTASY creatures (squid counted here by his words, guardians, warden, spiders, ghasts ...) are NOT on the curve.
Rows within 8 % of target are left alone (measurement noise). Real figures: typical adult sizes, source ranges in the basis
column — corrections welcome, his eye in game decides.
API: plan(census_rows) -> rows ; K ; target(real)"""
import json, math
from pathlib import Path

K = 1.875 / 1.778
R0, RMIN, FLOOR, DEADBAND = 0.60, 0.01, 0.22, 0.08


def target(real):
    if real >= R0: return K * real
    return FLOOR + (R0 * K - FLOOR) * math.log(max(real, RMIN) / RMIN) / math.log(R0 / RMIN)


# id (without namespace): (real metres, mode, basis)
REAL = {
    # ---- vanilla real animals (RP-06 / RP-07) ----
    "cow": (2.1, "hb", "cattle head-body 1.8-2.4 m"), "mooshroom": (2.1, "hb", "= cow"),
    "pig": (1.3, "hb", "domestic pig 0.9-1.8 m"), "sheep": (1.20, "hb", "his R8 calibration (Merino-type 1.2-1.5)"),
    "goat": (1.2, "hb", "domestic goat 1.0-1.5 m"), "horse": (2.4, "hb", "horse 2.2-2.5 m"), "donkey": (1.8, "hb", "donkey 1.5-2.0 m"),
    "mule": (2.1, "hb", "mule 1.9-2.3 m"), "skeleton_horse": (2.4, "hb", "= horse"), "zombie_horse": (2.4, "hb", "= horse"),
    "llama": (1.9, "hb", "llama 1.2-2.25 m"), "trader_llama": (1.9, "hb", "= llama"), "camel": (3.0, "hb", "dromedary 2.2-3.4 m"),
    "polar_bear": (2.1, "hb", "polar bear 1.8-2.4 m"), "panda": (1.5, "hb", "giant panda 1.2-1.9 m"),
    "wolf": (1.43, "hb", "his R8 calibration (grey wolf 1.05-1.6)"), "fox": (0.65, "hb", "red fox 0.46-0.9 m"),
    "ocelot": (0.75, "hb", "ocelot 0.55-1.0 m"), "cat": (0.46, "hb", "house cat 0.4-0.5 m"), "rabbit": (0.40, "hb", "European rabbit 0.34-0.5 m"),
    "armadillo": (0.40, "hb", "nine-banded 0.35-0.57 m"), "chicken": (0.45, "h", "hen standing 0.4-0.5 m"),
    "parrot": (0.84, "max", "scarlet macaw 0.81-0.96 m bill to tail tip (the red-blue Patrix parrot)"),
    "bat": (0.28, "max", "cave bat wingspan 0.22-0.33 m (posed with spread wings)"),
    "bee": (0.015, "max", "honey bee 12-15 mm"), "axolotl": (0.23, "max", "axolotl 15-45 cm"), "frog": (0.10, "max", "frogs 6-12 cm"),
    "tadpole": (0.05, "max", "tadpole 2.5-7 cm"), "pufferfish": (0.35, "max", "pufferfish 0.2-0.5 m"),
    "tropicalfish": (0.15, "max", "reef fish 0.1-0.2 m"), "cod": (0.8, "max", "Atlantic cod 0.6-1.0 m"),
    "salmon": (0.75, "max", "Atlantic / sockeye salmon 0.6-0.8 m (the NORMAL size variant)"), "dolphin": (2.5, "max", "bottlenose 2-4 m"),
    "turtle": (1.4, "max", "green sea turtle: 1.0 m shell, ~1.4 m flipper tip to flipper tip"),
    # ---- Naturalist creatures (sf_nba, StripMine BP scale) — largest dimension ----
    "alligator": (3.5, "max", "American alligator 3.4-4.6 m"), "anglerfish": (0.5, "max", "anglerfish 0.2-1 m"), "ant": (0.01, "max", "ant ~1 cm"),
    "anteater": (2.0, "max", "giant anteater 1.8-2.2 m with tail"), "badger": (0.9, "max", "European badger 0.75-1.05 m with tail"),
    "bass": (0.45, "max", "largemouth bass 0.3-0.6 m"), "beaver": (1.1, "max", "beaver 1.0-1.3 m with tail"), "beetle": (0.06, "max", "beetle ~6 cm"),
    "black_bear": (1.7, "max", "American black bear 1.5-1.9 m"), "bluejay": (0.28, "max", "blue jay 0.25-0.30 m"),
    "boar": (1.6, "max", "wild boar 1.3-2.0 m"), "budgie": (0.18, "max", "budgerigar 18 cm"), "butterfly": (0.10, "max", "wingspan ~10 cm"),
    "canary": (0.13, "max", "canary 12-14 cm"), "capybara": (1.25, "max", "capybara 1.1-1.3 m"), "cardinal": (0.22, "max", "cardinal 21-23 cm"),
    "caterpillar": (0.06, "max", "caterpillar ~6 cm"), "catfish": (0.8, "max", "channel catfish 0.4-1.3 m"), "cave_snake": (0.8, "max", "cave-dwelling snake ~0.8 m"),
    "cavefish": (0.10, "max", "blind cavefish ~10 cm"), "clam": (1.2, "max", "giant clam 1.2 m"), "coral_snake": (0.8, "max", "coral snake 0.5-0.9 m"),
    "coyote": (1.3, "max", "coyote 1.0-1.35 m with tail"), "crab": (0.20, "max", "crab ~20 cm"), "crow": (0.45, "max", "crow 0.4-0.53 m"),
    "deer": (1.9, "max", "white-tailed deer ~1.9 m long / antler height"), "desert_scorpion": (0.14, "max", "desert hairy scorpion 14 cm"),
    "dragonfly": (0.12, "max", "dragonfly ~12 cm"), "duck": (0.6, "max", "mallard 0.5-0.65 m"), "eagle": (0.9, "max", "bald eagle 0.7-1.0 m"),
    "electric_eel": (2.0, "max", "electric eel up to 2.5 m"), "elephant": (6.5, "max", "African elephant 6-7.5 m"),
    "emperor_penguin": (1.2, "max", "emperor penguin 1.0-1.3 m tall"), "female_lion": (2.6, "max", "lioness 2.4-2.8 m nose to tail tip"),
    "fennec_fox": (0.65, "max", "fennec 0.55-0.7 m with tail"), "finch": (0.14, "max", "finch ~14 cm"), "firefly": (0.02, "max", "firefly ~2 cm"),
    "flamingo": (1.4, "max", "flamingo 1.2-1.5 m tall"), "flying_fish": (0.30, "max", "flying fish ~30 cm"), "giant_isopod": (0.4, "max", "giant isopod 0.19-0.5 m"),
    "giant_salamander": (1.5, "max", "Chinese giant salamander up to 1.8 m"), "giraffe": (5.5, "max", "giraffe 4.3-5.7 m tall"),
    "goose": (0.9, "max", "Canada goose 0.75-1.1 m"), "gorilla": (1.7, "max", "gorilla 1.6-1.8 m standing"),
    "great_white_shark": (4.6, "max", "great white 3.4-4.9 m typical"), "grizzly_bear": (2.2, "max", "grizzly 1.8-2.5 m"),
    "hammer_head_shark": (4.0, "max", "hammerheads 2.5-6 m"), "hamster": (0.15, "max", "Syrian hamster 13-18 cm"), "hedgehog": (0.25, "max", "hedgehog 20-30 cm"),
    "hippo": (3.8, "max", "hippo 2.9-5.0 m"), "hyena": (1.7, "max", "spotted hyena ~1.7 m with tail"), "ravenous_hyena": (1.7, "max", "= hyena"),
    "iguana": (1.6, "max", "green iguana 1.5-1.8 m"), "jellyfish": (0.6, "max", "jellyfish ~0.6 m with tentacles"),
    "jungle_scorpion": (0.20, "max", "emperor scorpion ~20 cm"), "kakapo": (0.6, "max", "kakapo 0.58-0.64 m"),
    "kangaroo": (2.4, "max", "red kangaroo 2.2-2.6 m with tail"), "kiwi": (0.45, "max", "kiwi 0.35-0.55 m"), "komodo_dragon": (2.8, "max", "Komodo 2.6-3.0 m"),
    "lion": (2.8, "max", "lion 2.4-3.3 m nose to tail tip"), "lizard": (0.30, "max", "lizard ~30 cm"), "male_lion": (3.0, "max", "male lion 2.7-3.3 m nose to tail tip"),
    "mammoth": (5.5, "max", "woolly mammoth ~5-5.5 m incl. tusks"), "mole": (0.16, "max", "mole ~16 cm"), "monkey": (0.9, "max", "capuchin ~0.9 m with tail"),
    "moose": (3.0, "max", "moose 2.4-3.1 m"), "moray": (1.5, "max", "green moray ~1.5 m"), "spotted_moray": (1.0, "max", "spotted moray ~1 m"),
    "octopus": (1.5, "max", "common octopus arm span 1-1.5 m"), "orca": (7.5, "max", "orca 6-8 m"), "ostrich": (2.6, "max", "ostrich 2.1-2.8 m tall"),
    "otter": (1.2, "max", "river otter 1.0-1.3 m with tail"), "owl": (0.5, "max", "owl ~0.5 m"), "peafowl": (1.5, "max", "peacock display ~1.5 m"),
    "piranha": (0.30, "max", "red-bellied piranha ~30 cm"), "platypus": (0.5, "max", "platypus 0.4-0.6 m"), "raccoon": (0.85, "max", "raccoon 0.6-1.05 m with tail"),
    "rat": (0.40, "max", "brown rat ~0.4 m with tail"), "rattlesnake": (1.2, "max", "western diamondback ~1.2 m"), "raven": (0.65, "max", "raven 0.56-0.69 m"),
    "ray": (2.0, "max", "stingray disc ~2 m"), "red_panda": (1.0, "max", "red panda ~1 m with tail"), "rhino": (3.8, "max", "white rhino 3.4-4.2 m"),
    "robin": (0.14, "max", "European robin 12.5-14 cm"), "seal": (1.8, "max", "harbour seal 1.5-1.9 m"), "secretary_bird": (1.3, "max", "secretary bird 1.2-1.5 m tall"),
    "skunk": (0.7, "max", "striped skunk ~0.7 m with tail"), "sloth": (0.7, "max", "three-toed sloth ~0.6-0.75 m"), "slug": (0.10, "max", "slug ~10 cm"),
    "small_jellyfish": (0.10, "max", "~10 cm"), "snail": (0.05, "max", "snail ~5 cm"), "snake": (1.5, "max", "rat snake ~1.5 m"),
    "sparrow": (0.15, "max", "sparrow 14-16 cm"), "squirrel": (0.45, "max", "grey squirrel ~0.45 m with tail"), "starfish": (0.25, "max", "starfish ~25 cm"),
    "termite": (0.015, "max", "termite ~1.5 cm"), "tiger": (3.3, "max", "tiger 2.7-3.9 m nose to tail tip"), "tortoise": (1.2, "max", "giant tortoise 1.0-1.5 m"),
    "toucan": (0.6, "max", "toco toucan 0.55-0.65 m"), "tree_frog": (0.07, "max", "tree frog ~7 cm"), "turkey": (1.1, "max", "wild turkey 1.0-1.25 m"),
    "vulture": (2.6, "max", "vulture wingspan ~2.6 m (spread)"), "walrus": (3.3, "max", "walrus 2.2-3.6 m"), "whale": (15.0, "max", "humpback 14-16 m"),
    "zebra": (2.4, "max", "zebra 2.2-2.5 m"),
}
FANTASY = {"squid", "glow_squid", "guardian", "elder_guardian", "warden", "creeper", "enderman", "spider", "cave_spider", "silverfish",
           "endermite", "hoglin", "zoglin", "ravager", "iron_golem", "snow_golem", "giant", "sniffer", "strider", "allay", "vex", "ghast",
           "happy_ghast", "blaze", "breeze", "wither", "wither_skeleton", "phantom", "slime", "magma_cube", "shulker", "nautilus",
           "zombie_nautilus", "creaking", "copper_golem", "ender_dragon", "camel_husk"}


# D-C291: mobs whose everyday body is drawn by render-controller-conditional parts (state variants) — measured with those parts
# included (visible_size keep_conditional=True); every other real animal differs by < 8 % between the two measurements
CURRENT_OVERRIDE = {}   # superseded 20:0x by the everyday-state measurement in visible_size (black bear / deer / armadillo / grizzly)


def current(row, mode):
    if row["id"] in CURRENT_OVERRIDE: return CURRENT_OVERRIDE[row["id"]]
    if mode == "hb": return row["l"]          # the census measured hb rows with the tail left out
    if mode == "h": return row["h"]
    return max(row["h"], row["l"], row["w"])


def plan(rows):
    out = []
    for r in rows:
        name = r["id"].split(":")[1]
        if name in FANTASY or r.get("drawn_blocks") is None: continue
        if name not in REAL: continue
        real, mode, basis = REAL[name]
        cur = current(r, mode)
        if not cur:
            out.append({"id": r["id"], "real_m": real, "mode": mode, "basis": basis, "current": 0, "target": round(target(real), 3),
                        "factor": None, "action": "MEASURE FAILED (flat / alpha) — box measurement needed"}); continue
        t = target(real); f = t / cur
        act = "keep (within 8 %)" if abs(f - 1) < DEADBAND else ("grow" if f > 1 else "shrink")
        out.append({"id": r["id"], "real_m": real, "mode": mode, "basis": basis, "current": round(cur, 3), "target": round(t, 3),
                    "factor": round(f, 3), "action": act, "client_scale": r.get("client_scale"), "bp_scale": r.get("bp_scale")})
    return out


if __name__ == "__main__":
    rows = json.load(open("/home/claude/_docs/sizes/roster_size_census.json"))["rows"]
    p = plan(rows)
    json.dump(p, open("/home/claude/_docs/sizes/size_law_plan.json", "w"), indent=1)
    from collections import Counter
    print(Counter(x["action"].split(" ")[0] for x in p))
    for x in sorted(p, key=lambda x: (x["action"], x["id"])):
        if not x["action"].startswith("keep"):
            print(f"{x['action'][:8]:8} {x['id']:28} {x['mode']:3} real {x['real_m']:6} m  now {x['current']:6} -> {x['target']:6} blk  x{x['factor']}")
