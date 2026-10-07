#!/usr/bin/env python3
"""build_stripmine_bp_133.py — PW-StripMine-BP v1.3.3 (D-C263, Abs0lum 23:28: "create scalability/creature based on real-life size
RELATIONSHIPS ... a general relationship needs to be apparent"): the HYPER-REALISM SIZE CURVE for the sf_nba creatures.

v1.3.2 flattened every small creature onto the 0.22-block floor (ant = beetle = termite = butterfly); v1.3.3 replaces the floor
with a MONOTONIC curve, so bigger-in-life is bigger-in-game all the way down:
  real >= 0.60 m : game = real                                   (1 block = 1 m, true scale)
  real <  0.60 m : game = 0.22 + (0.60 - 0.22) * ln(real / 0.01) / ln(0.60 / 0.01)   (a log ramp from 0.22 block at 1 cm to 0.60 at 60 cm)
anchors: termite 1.5 cm -> 0.26 · ant 1 cm -> 0.22 · snail 5 cm -> 0.37 · beetle 6 cm -> 0.39 · butterfly 10 cm -> 0.43 · dragonfly 12 cm -> 0.45 ·
         sparrow 15 cm -> 0.47 · crab 20 cm -> 0.50 · hedgehog 25 cm -> 0.52 · rat 45 cm -> 0.58 · duck 60 cm -> 0.60 · deer 2.0 m -> 2.0
scale = game / current largest dimension, clamped to [0.05, 1.20] (under-sized giants grow at most 20 %), applied where it moves the
creature by 8 % or more.  Everything else as v1.3.2 (minecraft:scale = model + hitbox; baby groups x the same factor).

Rule (his ruling on the floored scheme): target = max(real_size, FLOOR) with FLOOR = 0.22 block (0.2 x 1.10);
scale = min(1.0, target / current_largest_dimension); applied only where scale <= 0.90 (never enlarged — under-sized giants are
listed, not touched).  The scale goes in as the BEHAVIOUR component minecraft:scale (model AND collision box shrink together —
the baby-mob mechanism), so a 22-cm beetle has a 22-cm hitbox; any component-group scale (sf_nba:baby 0.5 ...) is multiplied by
the same factor so babies stay proportional.  Current sizes come from RP-07 1.4.13's sf_nba geometries (largest of width/height/
length in blocks); real sizes are typical adult largest dimensions in metres (my figures — corrections welcome).
Realm-only pack (his ruling: StripMine is never production).  Source: _intake/stack-bps/PW-StripMine-BP-v1_3_1.mcpack."""
import json, os, re, shutil, time
from pathlib import Path

ROOT = Path("/home/claude")
SRC, DST, VER, DATE = ROOT / "_build/stripmine-bp-131", ROOT / "_build/stripmine-bp-133", "1.3.3", "2026-09-27"
FLOOR, R0, RMIN = 0.22, 0.60, 0.01
MAX_UP, MIN_SCALE, DEADBAND = 1.20, 0.05, 0.08
import math
def game_size(real):
    """the size relationship: true scale from 60 cm up, a log ramp below it that keeps the order of the small creatures visible."""
    if real >= R0: return real
    return FLOOR + (R0 - FLOOR) * math.log(max(real, RMIN) / RMIN) / math.log(R0 / RMIN)
# typical adult LARGEST dimension in metres (length incl. tail where the model carries the tail; height for the tall birds/giraffe;
# wingspan where the model's widest axis is spread wings)
REAL = {
    "alligator": 3.5, "anglerfish": 0.5, "ant": 0.01, "badger": 0.8, "bass": 0.45, "beaver": 1.0, "beetle": 0.06, "black_bear": 1.6,
    "bluejay": 0.28, "boar": 1.6, "budgie": 0.18, "butterfly": 0.10, "canary": 0.13, "capybara": 1.25, "cardinal": 0.22, "caterpillar": 0.06,
    "catfish": 0.8, "cavefish": 0.10, "clam": 1.2, "coyote": 1.1, "crab": 0.20, "crow": 0.50, "deer": 2.0, "dragonfly": 0.12, "duck": 0.6,
    "eagle": 0.9, "elephant": 6.5, "emperor_penguin": 1.2, "fennec_fox": 0.7, "finch": 0.14, "firefly": 0.02, "flamingo": 1.4,
    "giant_isopod": 0.4, "giant_salamander": 1.5, "giraffe": 5.5, "goose": 1.0, "gorilla": 1.7, "grizzly_bear": 2.2, "hamster": 0.15,
    "hedgehog": 0.25, "hippo": 3.8, "hyena": 1.5, "iguana": 1.6, "jellyfish": 0.6, "kakapo": 0.6, "kangaroo": 2.3, "kiwi": 0.5,
    "komodo_dragon": 2.8, "lion": 2.1, "female_lion": 1.9, "male_lion": 2.1, "lizard": 0.30, "mammoth": 7.0, "mole": 0.16, "monkey": 0.9,
    "moose": 3.0, "octopus": 1.5, "orca": 7.5, "ostrich": 2.6, "otter": 1.2, "owl": 0.5, "peafowl": 1.5, "platypus": 0.5, "raccoon": 0.9,
    "rat": 0.45, "raven": 0.65, "ray": 2.0, "red_panda": 1.0, "rhino": 3.8, "robin": 0.14, "seal": 1.8, "secretary_bird": 1.3,
    "skunk": 0.7, "sloth": 0.6, "slug": 0.10, "small_jellyfish": 0.10, "snail": 0.05, "snake": 1.5, "sparrow": 0.15, "squirrel": 0.45,
    "starfish": 0.25, "termite": 0.015, "tiger": 2.5, "tortoise": 1.2, "toucan": 0.6, "tree_frog": 0.07, "turkey": 1.1, "vulture": 2.6,
    "walrus": 3.3, "whale": 15.0, "zebra": 2.4,
}

def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT 09-27] BUILD {m}\n")

sizes = json.load(open(ROOT / "_logs/sf_nba_sizes.json"))     # "sf_nba:name" -> [geometry, [w,h,l], rp_scale]
table = []
for ident, (geo, dims, rpscale) in sizes.items():
    name = ident.split(":")[1]
    if not dims or name not in REAL: continue
    current = max(dims); real = REAL[name]; target = round(game_size(real), 3)
    raw = target / current
    scale = round(min(MAX_UP, max(MIN_SCALE, raw)), 2)
    if abs(scale - 1.0) < DEADBAND: action = "keep (within 8 %)"
    elif scale < 1.0: action = "shrink"
    else: action = "grow" + (" (capped at x1.20)" if raw > MAX_UP else "")
    table.append({"id": ident, "geometry": geo, "current_blocks": current, "dims": dims, "real_m": real, "target": target, "after": round(current * scale, 2), "scale": scale, "action": action})
shrink = {t["id"]: t["scale"] for t in table if t["action"] != "keep (within 8 %)"}

if DST.exists(): shutil.rmtree(DST)
shutil.copytree(SRC, DST)
changed, skipped = [], []
for p in sorted((DST / "entities").rglob("*.json")):
    txt = p.read_text(encoding="utf-8-sig")
    m = re.search(r'"identifier"\s*:\s*"(sf_nba:[a-z_]+)"', txt)
    if not m or m.group(1) not in shrink: continue
    ident, s = m.group(1), shrink[m.group(1)]
    try:
        j = json.loads(re.sub(r"^\s*//.*$", "", txt, flags=re.M))
    except Exception as e:
        skipped.append(f"{ident}: not strict JSON ({str(e)[:40]}) — left as is"); continue
    ent = j["minecraft:entity"]
    comps = ent.setdefault("components", {})
    base = comps.get("minecraft:scale", {}).get("value", 1.0)
    comps["minecraft:scale"] = {"value": round(base * s, 3)}
    groups_touched = []
    for g, gc in ent.get("component_groups", {}).items():
        if "minecraft:scale" in gc:
            gc["minecraft:scale"]["value"] = round(gc["minecraft:scale"]["value"] * s, 3); groups_touched.append(g)
    p.write_text(json.dumps(j, indent=2), encoding="utf-8")
    changed.append({"id": ident, "file": str(p.relative_to(DST)), "scale": round(base * s, 3), "groups": groups_touched})

man = json.loads((DST / "manifest.json").read_text(encoding="utf-8-sig")); v = [1, 3, 3]
man["header"]["name"] = f"PW StripMine BP v{VER}"; man["header"]["version"] = v
for mod in man["modules"]: mod["version"] = v
man["header"]["description"] = (f"v{VER} ({DATE}) HYPER-REALISM SIZE CURVE (D-C263): {len(changed)} sf_nba creatures get minecraft:scale from one monotonic real-size "
                                "relationship — true scale (1 block = 1 m) from 60 cm up, a log ramp below it (1 cm -> 0.22 block, 6 cm beetle -> 0.39, 10 cm butterfly -> 0.43, "
                                "20 cm crab -> 0.50, 45 cm rat -> 0.58) so bigger-in-life stays bigger-in-game all the way down; under-sized giants grow by at most 20 %. "
                                "Model and collision box scale together; baby groups stay proportional. Supersedes v1.3.2 (flat 0.22 floor). Everything else byte-identical to v1.3.1.")
(DST / "manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
dep = DST / "PW-DEPENDENCIES.md"
if dep.exists(): dep.write_text(dep.read_text(encoding="utf-8") + f"\n\n_v{VER} ({DATE}): minecraft:scale on {len(changed)} sf_nba creatures (hyper-realism size pass, D-C262). No dependency change._\n", encoding="utf-8")
report = {"floor": FLOOR, "r0": R0, "rmin": RMIN, "max_up": MAX_UP, "deadband": DEADBAND, "table": table, "changed": changed, "skipped": skipped}
json.dump(report, open(ROOT / "_logs/stripmine_bp_133_report.json", "w"), indent=1)
log(f"PW-StripMine-BP v{VER}: {len(changed)} creatures scaled (floor {FLOOR}), {len(skipped)} skipped, manifest stamped -> {DST}")
print(f"{'creature':22s} {'now':>6s} {'real':>6s} {'game':>6s} {'scale':>6s}  action")
for t in sorted(table, key=lambda t: t["real_m"]):
    print(f"{t['id'][7:]:22s} {t['current_blocks']:6.2f} {t['real_m']:6.2f} {t['after']:6.2f} {t['scale']:6.2f}  {t['action']}")
print("skipped:", skipped)
