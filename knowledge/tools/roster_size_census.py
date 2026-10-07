#!/usr/bin/env python3
"""roster_size_census.py — D-C290 (his 19:30 CT 09-29: "make sure we're checking all mobs for appropriate size ratios; I think our
sizes look great for having a recognizable sprite without being cartoonishly large or imperceptible").

READ-ONLY census of EVERY mob the game draws in his stack. It finds outliers; it changes nothing (resizing is his call).

Size of a mob = what the game DRAWS: visible_size.measure (only texels that pass the alpha cut, render-controller parts
evaluated in the EVERYDAY state (D-C291: awake, not angry / sheared / tamed / eating, adult) — the old rule dropped every conditional part,
which lost the grizzly's and armadillo's whole bodies,
x the client entity's adult scripts.scale) x the adult minecraft:scale of the BEHAVIOUR entity that runs it (vanilla BP from
Mojang/bedrock-samples 1.26.50; sf_nba creatures from PW-StripMine BP 1.3.3, the size-curve build).

Classes and the check each gets:
  SMALL  real animal under 0.60 m      -> the size_rule curve (K = 1.0546 blk/m from his 5'10" character; log ramp below 60 cm,
                                          0.22-block floor).  ratio = drawn / target.
  LARGE  real animal from 0.60 m up    -> true-scale fraction f = drawn / (K x real).  Vanilla-size hitboxes keep big mobs
                                          compressed on purpose (size_rule option (a)), so the check is CONSISTENCY: f against the
                                          class median, plus ORDER (bigger in life must not be drawn clearly smaller).
  HUMAN  people-shaped mobs            -> standing height against the player (1.875 blocks).
  FANTASY no real-world size           -> our drawn size against Mojang's own drawn size for the same mob (vanilla geometry).
  NBA    Naturalist creatures           -> the StripMine curve they were built on (largest dimension, 1 block = 1 m, log ramp).
Flags: >= 15 % off its check = LOOK (goes to him); 8-15 % = minor (listed, not pushed); ORDER = inverted pair (> 10 %).
Real sizes are typical adult figures (head-body for mammals, total length for fish / squid, standing height for chicken /
people). Figures in size_rule.REAL (his witnessed calibrations) take precedence over the ones below.
Output: _docs/sizes/roster_size_census.json + .md.  API: census() -> rows"""
import glob, json, math, re, statistics, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML
import visible_size as V
import size_rule as SR

ROOT = Path("/home/claude")
PACKS = [ROOT / "_build/rp07-1425", ROOT / "_build/rp06-1418", ROOT / "_build/rp08-148"]
VAN_RP = ROOT / "_intake/bedrock-samples/resource_pack"
VAN_BP = ROOT / "_intake/bedrock-samples/behavior_pack/entities"
SM_BP = ROOT / "_build/stripmine-bp-133/entities"
OUT = ROOT / "_docs/sizes"
PLAYER_H = 1.875
LOOK, MINOR, ORDER_TOL = 0.15, 0.08, 0.10

# id: (class, real metres or None, measured: "l" head-body w/o tail | "total" max dimension | "h" height, basis)
TABLE = {
    # large real animals (head-body)
    "cow": ("LARGE", 2.1, "l", "cattle head-body 1.8-2.4 m"), "mooshroom": ("LARGE", 2.1, "l", "= cow"),
    "pig": ("LARGE", 1.3, "l", "domestic pig 0.9-1.8 m"), "sheep": ("LARGE", None, "l", "size_rule"),
    "goat": ("LARGE", 1.2, "l", "domestic goat 1.0-1.5 m"), "horse": ("LARGE", 2.4, "l", "horse body 2.2-2.5 m"),
    "donkey": ("LARGE", 1.8, "l", "donkey 1.5-2.0 m"), "mule": ("LARGE", 2.1, "l", "mule 1.9-2.3 m"),
    "skeleton_horse": ("LARGE", 2.4, "l", "= horse"), "zombie_horse": ("LARGE", 2.4, "l", "= horse"),
    "llama": ("LARGE", 1.9, "l", "llama 1.2-2.25 m"), "trader_llama": ("LARGE", 1.9, "l", "= llama"),
    "camel": ("LARGE", 3.0, "l", "dromedary 2.2-3.4 m"), "camel_husk": ("LARGE", 3.0, "l", "= camel"),
    "polar_bear": ("LARGE", 2.1, "l", "polar bear 1.8-2.4 m"), "panda": ("LARGE", 1.5, "l", "giant panda 1.2-1.9 m"),
    "wolf": ("LARGE", None, "l", "size_rule"), "fox": ("LARGE", None, "l", "size_rule"), "ocelot": ("LARGE", None, "l", "size_rule"),
    "dolphin": ("LARGE", 2.5, "total", "bottlenose dolphin 2-4 m"), "turtle": ("LARGE", 1.1, "total", "green sea turtle 0.8-1.2 m shell + head"),
    "cod": ("LARGE", 0.8, "total", "Atlantic cod 0.6-1.0 m"), "salmon": ("LARGE", 0.75, "total", "Atlantic salmon 0.7-0.8 m"),
    "squid": ("LARGE", 0.6, "total", "common squid ~0.3 m mantle, ~0.6 m with arms"),
    # small real animals
    "cat": ("SMALL", None, "l", "size_rule"), "rabbit": ("SMALL", None, "l", "size_rule"), "chicken": ("SMALL", None, "h", "size_rule"),
    "bee": ("SMALL", None, "total", "size_rule"), "axolotl": ("SMALL", None, "total", "size_rule"), "tadpole": ("SMALL", None, "total", "size_rule"),
    "frog": ("SMALL", None, "total", "size_rule"), "pufferfish": ("SMALL", None, "total", "size_rule"),
    "tropicalfish": ("SMALL", None, "total", "size_rule"), "parrot": ("SMALL", 0.50, "total", "macaw 0.8 m incl. tail / African grey 0.33 m -> 0.50"),
    "bat": ("SMALL", 0.25, "total", "wingspan 0.2-0.3 m (drawn spread)"), "armadillo": ("SMALL", 0.40, "l", "nine-banded armadillo 0.35-0.57 m"),
    # people-shaped
    **{k: ("HUMAN", None, "h", "player height 1.875 blk") for k in (
        "villager_v2", "wandering_trader", "witch", "evocation_illager", "vindicator", "pillager", "illusioner", "zombie", "husk",
        "drowned", "zombie_villager_v2", "skeleton", "stray", "bogged", "piglin", "piglin_brute", "zombie_pigman")},
    # fantasy: against Mojang's drawn size
    **{k: ("FANTASY", None, "total", "vanilla Bedrock drawn size") for k in (
        "creeper", "enderman", "spider", "cave_spider", "silverfish", "endermite", "guardian", "elder_guardian", "hoglin", "zoglin",
        "ravager", "iron_golem", "snow_golem", "giant", "sniffer", "strider", "allay", "vex", "ghast", "happy_ghast", "blaze", "breeze",
        "wither", "wither_skeleton", "phantom", "slime", "magma_cube", "warden", "shulker", "glow_squid", "nautilus", "zombie_nautilus",
        "creaking", "copper_golem", "ender_dragon")},
}


def jl(p): return ML._parse_json(Path(p).read_text(encoding="utf-8-sig"))


def client_desc(p):
    try: d = jl(p)
    except Exception: return None
    return (d.get("minecraft:client_entity") or {}).get("description") if isinstance(d, dict) else None


def vanilla_entity_files():
    """identifier -> the vanilla client-entity file the current game uses (highest min_engine_version, then newest name)."""
    best = {}
    for p in sorted(glob.glob(str(VAN_RP / "entity/*.json"))):
        de = client_desc(p)
        if not de or "identifier" not in de: continue
        mev = tuple(int(x) for x in re.findall(r"\d+", str(de.get("min_engine_version", "0")))) or (0,)
        key = (mev, "v1.0" not in p, p)
        if de["identifier"] not in best or key > best[de["identifier"]][0]: best[de["identifier"]] = (key, p)
    return {k: v[1] for k, v in best.items()}


def bp_scale(ident):
    """adult minecraft:scale of the behaviour entity (base components)."""
    ns, name = ident.split(":")
    cands = glob.glob(str(SM_BP / f"{name}*.json")) if ns == "sf_nba" else glob.glob(str(VAN_BP / f"{name}.json"))
    for p in cands:
        try: d = jl(p)
        except Exception: continue
        ent = d.get("minecraft:entity") or {}
        if ent.get("description", {}).get("identifier") != ident: continue
        return float((ent.get("components") or {}).get("minecraft:scale", {}).get("value", 1.0))
    return 1.0


def measure_file(entity_file, pack_root, stack, exclude=None):
    """everyday state first; when that hides every part (a render controller whose allow-list is all state queries), the old
    conditional-dropping rule, then every part (D-C291)."""
    for mode in ("everyday", "old", "all"):
        m = _measure_file(entity_file, pack_root, stack, exclude, mode)
        if m: m["visibility_rule"] = mode; return m
    return None


def _measure_file(entity_file, pack_root, stack, exclude, mode):
    kw = {"everyday": mode == "everyday", "keep_conditional": mode == "all"}
    """visible_size.measure for an entity file whose name is not <stem>.entity.json."""
    stem = Path(entity_file).name.replace(".entity.json", "").replace(".json", "")
    if Path(pack_root, "entity", f"{stem}.entity.json").exists():
        return V.measure(pack_root, stem, stack, exclude=exclude, **kw)
    # vanilla files like horse_v3.entity.json / guardian.entity.v1.0.json: measure through a scratch copy
    scratch = Path("/tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad/vs_pack")
    (scratch / "entity").mkdir(parents=True, exist_ok=True)
    (scratch / "entity" / "probe.entity.json").write_bytes(Path(entity_file).read_bytes())
    return V.measure(scratch, "probe", list(stack) + [pack_root], exclude=exclude, **kw)


def vanilla_size(ident, what, van, ours_stack=()):
    """Mojang's drawn size for the same mob: vanilla client entity + vanilla geometry + vanilla texture (bedrock-samples 1.26.50,
    textures sparse-checked-out 09-29) x vanilla BP adult scale. ours_stack: our packs FIRST when the game draws the vanilla
    entity with our texture (vanilla-drawn mobs)."""
    if ident not in van: return None
    m = measure_file(van[ident], VAN_RP, list(ours_stack), exclude=SR.TAIL if what == "l" else None)
    if not m: return None
    return round(pick(m, what) * bp_scale(ident), 3), m


def pick(m, what):
    if what == "l": return m["l"]
    if what == "h": return m["h"]
    return m["max"]


def census():
    ours = {}
    for i, pack in enumerate(PACKS):
        for p in sorted(glob.glob(str(pack / "entity/*.json"))):
            de = client_desc(p)
            if de and "identifier" in de and de["identifier"] not in ours:
                ours[de["identifier"]] = (p, pack, [q for q in PACKS if q != pack])
    van = vanilla_entity_files()
    rows = []
    idents = sorted(set(ours) | {f"minecraft:{k}" for k in TABLE})
    for ident in idents:
        ns, name = ident.split(":")
        who = "ours" if ident in ours else "vanilla-drawn"
        if ident in ours: f, pack, stack = ours[ident]
        elif ident in van: f, pack, stack = van[ident], VAN_RP, list(PACKS)
        else:
            rows.append({"id": ident, "class": TABLE.get(name, ("?",))[0], "drawn_by": "not in this game version", "flag": "n/a"}); continue
        if ns == "sf_nba": cls, real, what, basis = "NBA", None, "total", "StripMine curve (largest dimension)"
        elif name in TABLE: cls, real, what, basis = TABLE[name]
        else: cls, real, what, basis = "UNCLASSIFIED", None, "total", "not in the table (listed, P11)"
        if name in SR.REAL:
            real, sr_what, basis = SR.REAL[name]; what = {"head-body": "l", "total": "total", "height": "h"}[sr_what]
        excl = SR.TAIL if what == "l" else None
        try: m = measure_file(f, pack, stack, exclude=excl)
        except Exception as e: m = None; err = str(e)[:80]
        if not m:
            rows.append({"id": ident, "class": cls, "drawn_by": who, "flag": "unmeasured", "note": locals().get("err", "no visible texels / geometry")}); continue
        bs = bp_scale(ident)
        drawn = round(pick(m, what) * bs, 3)
        row = {"id": ident, "class": cls, "drawn_by": who, "measured": what, "drawn_blocks": drawn, "h": round(m["h"] * bs, 3),
               "l": round(m["l"] * bs, 3), "w": round(m["w"] * bs, 3), "client_scale": m["client_scale"], "bp_scale": bs, "basis": basis, "real_m": real}
        if cls == "SMALL" or (cls == "LARGE" and real is not None and real < SR.R0):
            row["target"] = round(SR.game_blocks(real), 3); row["ratio"] = round(drawn / row["target"], 3)
        elif cls == "LARGE":
            row["target"] = round(SR.K * real, 3); row["true_scale_fraction"] = round(drawn / row["target"], 3)
        elif cls == "HUMAN":
            row["target"] = PLAYER_H; row["ratio"] = round(row["h"] / PLAYER_H, 3)
        elif cls == "NBA":
            realn = _SM_REAL.get(name)
            if realn: row["real_m"] = realn; row["target"] = round(_sm_game(realn), 3); row["ratio"] = round(max(row["h"], row["l"], row["w"]) / row["target"], 3)
        elif cls == "FANTASY":
            if who == "ours" and ident in van:
                vv = vanilla_size(ident, "total", van)
                if vv: row["vanilla_blocks"] = vv[0]; row["ratio"] = round(drawn / vv[0], 3)
            elif who != "ours": row["ratio"] = 1.0; row["vs"] = "drawn by vanilla (our texture if we ship one)"
        if who == "ours" and ident in van:
            vv = vanilla_size(ident, what, van)
            if vv: row["vanilla_same_measure"] = vv[0]; row["vs_vanilla"] = round(drawn / vv[0], 3) if vv[0] else None
        rows.append(row)
    # consistency of the LARGE class (true-scale fraction against the class median)
    fr = [r["true_scale_fraction"] for r in rows if "true_scale_fraction" in r]
    med = statistics.median(fr) if fr else 1.0
    for r in rows:
        if "true_scale_fraction" in r: r["ratio"] = round(r["true_scale_fraction"] / med, 3); r["vs"] = f"class median f={med:.2f}"
        if "ratio" in r:
            off = abs(r["ratio"] - 1.0)
            r["flag"] = "LOOK" if off >= LOOK else "minor" if off >= MINOR else "ok"
        elif "flag" not in r: r["flag"] = "no check"
    # ORDER: real animals (SMALL + LARGE, both measured) — bigger in life must not be drawn clearly smaller
    real_rows = [r for r in rows if r.get("real_m") and r["class"] in ("SMALL", "LARGE") and "drawn_blocks" in r]
    order = []
    for a in real_rows:
        for b in real_rows:
            if a["real_m"] > b["real_m"] * 1.15 and a["drawn_blocks"] < b["drawn_blocks"] * (1 - ORDER_TOL):
                order.append((a["id"], a["real_m"], a["drawn_blocks"], b["id"], b["real_m"], b["drawn_blocks"]))
    return rows, order, med


_SM_REAL = {}
def _load_sm():
    src = (ROOT / "tools/build_stripmine_bp_133.py").read_text()
    m = re.search(r"REAL = \{(.*?)\n\}", src, re.S)
    _SM_REAL.update(eval("{" + m.group(1) + "}"))
_load_sm()
def _sm_game(real):
    if real >= 0.60: return real
    return 0.22 + (0.60 - 0.22) * math.log(max(real, 0.01) / 0.01) / math.log(0.60 / 0.01)


if __name__ == "__main__":
    rows, order, med = census()
    OUT.mkdir(parents=True, exist_ok=True)
    json.dump({"rows": rows, "order_inversions": order, "large_median_true_scale": med}, open(OUT / "roster_size_census.json", "w"), indent=1)
    from collections import Counter
    print("classes", Counter(r["class"] for r in rows)); print("flags", Counter(r["flag"] for r in rows))
    print(f"LARGE median true-scale fraction {med:.3f}")
    for r in rows:
        if r["flag"] in ("LOOK", "minor", "unmeasured", "n/a") or r["class"] == "UNCLASSIFIED":
            print(f"{r['flag']:10} {r['class']:12} {r['id']:30} drawn {r.get('drawn_blocks')} target {r.get('target', r.get('vanilla_blocks'))} ratio {r.get('ratio')} ({r.get('drawn_by')}) {r.get('note', '')}")
    print("ORDER inversions:", len(order))
    for o in order[:40]: print("  ", o)
