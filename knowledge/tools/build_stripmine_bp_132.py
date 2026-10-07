#!/usr/bin/env python3
"""build_stripmine_bp_132.py — PW-StripMine-BP v1.3.2 (D-C262, Abs0lum 22:42: "let's make them 10% larger [than the 0.2-block
floor] — so they're still highly interactable"): the HYPER-REALISM SIZE PASS for the sf_nba creatures.

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
SRC, DST, VER, DATE = ROOT / "_build/stripmine-bp-131", ROOT / "_build/stripmine-bp-132", "1.3.2", "2026-09-27"
FLOOR = 0.22
APPLY_BELOW = 0.90
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
    current = max(dims); real = REAL[name]; target = max(real, FLOOR)
    scale = min(1.0, round(target / current, 2))
    action = "shrink" if scale <= APPLY_BELOW else ("keep" if current <= real * 1.15 else "keep (within 10 %)")
    if current < real / 1.5: action = "UNDER-SIZED (not enlarged)"
    table.append({"id": ident, "geometry": geo, "current_blocks": current, "dims": dims, "real_m": real, "target": round(target, 2), "scale": scale, "action": action})
shrink = {t["id"]: t["scale"] for t in table if t["action"] == "shrink"}

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

man = json.loads((DST / "manifest.json").read_text(encoding="utf-8-sig")); v = [1, 3, 2]
man["header"]["name"] = f"PW StripMine BP v{VER}"; man["header"]["version"] = v
for mod in man["modules"]: mod["version"] = v
man["header"]["description"] = (f"v{VER} ({DATE}) HYPER-REALISM SIZES (D-C262): {len(changed)} sf_nba creatures get minecraft:scale so their largest dimension "
                                f"= max(real size, {FLOOR} block) — beetle/ant/termite/snail/slug/caterpillar/butterfly/dragonfly/small birds/rodents shrink toward "
                                "life size with a 22-cm floor for interactability; model and collision box shrink together; baby groups stay proportional. "
                                "Nothing enlarged. Everything else byte-identical to v1.3.1.")
(DST / "manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
dep = DST / "PW-DEPENDENCIES.md"
if dep.exists(): dep.write_text(dep.read_text(encoding="utf-8") + f"\n\n_v{VER} ({DATE}): minecraft:scale on {len(changed)} sf_nba creatures (hyper-realism size pass, D-C262). No dependency change._\n", encoding="utf-8")
report = {"floor": FLOOR, "apply_below": APPLY_BELOW, "table": table, "changed": changed, "skipped": skipped}
json.dump(report, open(ROOT / "_logs/stripmine_bp_132_report.json", "w"), indent=1)
log(f"PW-StripMine-BP v{VER}: {len(changed)} creatures scaled (floor {FLOOR}), {len(skipped)} skipped, manifest stamped -> {DST}")
print(f"{'creature':22s} {'now':>6s} {'real':>6s} {'target':>6s} {'scale':>6s}  action")
for t in sorted(table, key=lambda t: t["scale"]):
    print(f"{t['id'][7:]:22s} {t['current_blocks']:6.2f} {t['real_m']:6.2f} {t['target']:6.2f} {t['scale']:6.2f}  {t['action']}")
print("skipped:", skipped)
