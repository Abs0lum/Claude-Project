#!/usr/bin/env python3
"""build_e2.py — E2: the re-layout / move families (ruling D-C216, 16:29 CT).

RP-04 v1.3.133 -> v1.3.134 (textures/entity):
  chests  — Java 1.15+ layout -> Bedrock classic layout (tools/chest_e2.py, render-verified): singles normal, trapped,
            ender, copper_default (<- copper.png), copper_exposed/oxidized/weathered converted IN PLACE (they were live
            Java-layout files); doubles double_normal, trapped_double (REGENERATED — supersedes the 07-03 composition:
            same front/back, corrected top/underside/ends), copper_default_double + copper_exposed/oxidized/weathered_double
            (new) from the Patrix _left/_right halves.
  armor_stand.png <- armorstand/wood.png (identical box/uv layout: vanilla armor_stand.geo.json vs Java ArmorStandModel)
  bell/bell.png <- bell/bell_body.png (identical: body 6x7x6 @ 0,0 + base 8x2x8 @ 0,13)
  banner/banner_base.png <- banner_base.png ; banner/banner_<p>.png <- banner/<p>.png (42 patterns; the four diagonals swap names between editions; Java 'base' has no
            Bedrock file; Bedrock's illager patterns and the 512x512 UI atlas banner.tga stay vanilla)
  endercrystal/endercrystal.png <- end_crystal/end_crystal.png ; endercrystal_beam likewise (identical 128x64 layout:
            vanilla ender_crystal.geo.json = Java EndCrystalModel)
  already live and same layout, nothing to do: minecart, enchanting_table_book, experience_orb, lead_knot, beacon_beam, shulker.
RP-03 v1.3.57 -> v1.3.58 (textures/blocks):
  conduit_base <- conduit/base.png cropped to the 6x6x6 unwrap (24x12 of the 32x16 canvas) ; conduit_cage <- cage ;
  conduit_closed <- closed_eye ; conduit_open <- open_eye ; conduit_wind_horizontal <- wind ; conduit_wind_vertical <- wind_vertical
  decorated_pot_base <- decorated_pot/decorated_pot_base (same packed layout: neck squares + sides band + body top/bottom squares) ;
  decorated_pot_side ; 23 <p>_pottery_pattern ; cauldron_water (+ texture set, mer, normal) <- RP-02 v2.0.3 water_still (16x512, VV PBR)
Java-named originals kept (ruling b).
"""
import json, shutil, datetime, sys
from pathlib import Path
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
import chest_e2 as ce

ROOT = Path("/home/claude"); DATE = "2026-09-22"; LOG = ROOT / "_logs/phase_log.md"
def log(m): LOG.open("a").write(f"[{datetime.datetime.now().strftime('%H:%M')} CT 09-22] BUILD E2 — {m}\n")
def jload(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def jdump(o, p): Path(p).write_text(json.dumps(o, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
SRC4, DST4 = ROOT / "_build/rp04-133", ROOT / "_build/rp04-134"
SRC3, DST3 = ROOT / "_build/rp03-57", ROOT / "_build/rp03-58"
PATTERNS = ["border", "bricks", "circle", "creeper", "cross", "curly_border", "diagonal_left", "diagonal_right", "diagonal_up_left", "diagonal_up_right", "flow", "flower", "globe", "gradient", "gradient_up", "guster",
            "half_horizontal", "half_horizontal_bottom", "half_vertical", "half_vertical_right", "mojang", "piglin", "rhombus", "skull", "small_stripes", "square_bottom_left", "square_bottom_right", "square_top_left",
            "square_top_right", "straight_cross", "stripe_bottom", "stripe_center", "stripe_downleft", "stripe_downright", "stripe_left", "stripe_middle", "stripe_right", "stripe_top", "triangle_bottom", "triangle_top", "triangles_bottom", "triangles_top"]
# Bedrock and Java name the diagonal patterns the other way round (vanilla banner_diagonal_left == Patrix diagonal_up_left, IoU 0.96 vs 0.38)
DIAG = {"diagonal_left": "diagonal_up_left", "diagonal_up_left": "diagonal_left", "diagonal_right": "diagonal_up_right", "diagonal_up_right": "diagonal_right"}
POTTERY = ["angler", "archer", "arms_up", "blade", "brewer", "burn", "danger", "explorer", "flow", "friend", "guster", "heart", "heartbreak", "howl", "miner", "mourner", "plenty", "prize", "scrape", "sheaf", "shelter", "skull", "snort"]

def stamp(src, dst, ver, name, headline, ledger_old=None):
    v = ".".join(map(str, ver)); man = jload(dst / "manifest.json")
    man["header"]["name"] = name.format(v=v); man["header"]["version"] = list(ver)
    for m in man["modules"]: m["version"] = list(ver)
    man["header"]["description"] = f"v{v} ({DATE}) {headline}"; jdump(man, dst / "manifest.json")
    led = dst / "PW-DEPENDENCIES.md"
    if led.exists() and ledger_old:
        t = led.read_text(encoding="utf-8"); t2 = t.replace(f"v{ledger_old} ·", f"v{v} ·", 1)
        if t2 != t: led.write_text(t2, encoding="utf-8")

def main():
    added = {"RP-04": [], "RP-03": []}
    for s, d in ((SRC4, DST4), (SRC3, DST3)):
        if d.exists(): shutil.rmtree(d)
        shutil.copytree(s, d)
    E = DST4 / "textures/entity"; SE = SRC4 / "textures/entity"
    def put4(rel): added["RP-04"].append(f"textures/entity/{rel}")
    # ---- chests
    C = E / "chest"
    for single, out in (("normal", "normal"), ("trapped", "trapped"), ("ender", "ender"), ("copper", "copper_default"), ("copper_exposed", "copper_exposed"), ("copper_oxidized", "copper_oxidized"), ("copper_weathered", "copper_weathered")):
        ce.convert_single(Image.open(SE / f"chest/{single}.png")).save(C / f"{out}.png"); put4(f"chest/{out}.png")
    for base, out in (("normal", "double_normal"), ("trapped", "trapped_double"), ("copper", "copper_default_double"), ("copper_exposed", "copper_exposed_double"), ("copper_oxidized", "copper_oxidized_double"), ("copper_weathered", "copper_weathered_double")):
        ce.convert_double(Image.open(SE / f"chest/{base}_left.png"), Image.open(SE / f"chest/{base}_right.png"), Image.open(SE / f"chest/{base}.png")).save(C / f"{out}.png"); put4(f"chest/{out}.png")
    # ---- straight renames (same layout as the engine's model)
    for src, dst in [("armorstand/wood.png", "armor_stand.png"), ("bell/bell_body.png", "bell/bell.png"), ("banner_base.png", "banner/banner_base.png"),
                     ("end_crystal/end_crystal.png", "endercrystal/endercrystal.png"), ("end_crystal/end_crystal_beam.png", "endercrystal/endercrystal_beam.png")] + [(f"banner/{p}.png", f"banner/banner_{DIAG.get(p, p)}.png") for p in PATTERNS]:
        (E / dst).parent.mkdir(parents=True, exist_ok=True); shutil.copy(SE / src, E / dst); put4(dst)
    # ---- RP-03 blocks
    B = DST3 / "textures/blocks"
    def put3(rel): added["RP-03"].append(f"textures/blocks/{rel}")
    base = Image.open(SE / "conduit/base.png").convert("RGBA"); s = base.width // 32
    base.crop((0, 0, 24 * s, 12 * s)).save(B / "conduit_base.png"); put3("conduit_base.png")
    for src, dst in (("conduit/cage.png", "conduit_cage.png"), ("conduit/closed_eye.png", "conduit_closed.png"), ("conduit/open_eye.png", "conduit_open.png"), ("conduit/wind.png", "conduit_wind_horizontal.png"), ("conduit/wind_vertical.png", "conduit_wind_vertical.png"),
                     ("decorated_pot/decorated_pot_base.png", "decorated_pot_base.png"), ("decorated_pot/decorated_pot_side.png", "decorated_pot_side.png")) + tuple((f"decorated_pot/{p}_pottery_pattern.png", f"{p}_pottery_pattern.png") for p in POTTERY):
        shutil.copy(SE / src, B / dst); put3(dst)
    W = ROOT / "_intake/rp02-water"
    for suf in ("", "_mer", "_normal"):
        shutil.copy(W / f"water_still{suf}.png", B / f"cauldron_water{suf}.png"); put3(f"cauldron_water{suf}.png")
    ts = jload(W / "water_still.texture_set.json"); t = ts["minecraft:texture_set"]
    for k, v in list(t.items()):
        if isinstance(v, str) and v.startswith("water_still"): t[k] = "cauldron_water" + v[len("water_still"):]
    jdump(ts, B / "cauldron_water.texture_set.json"); put3("cauldron_water.texture_set.json")
    stamp(SRC4, DST4, (1, 3, 134), "AbsolutRealism Basic RP v{v}",
          "E2 RE-LAYOUTS. Chests: the Patrix Java-1.15 chest textures were on Bedrock's classic layout as-is (dark lid top, scrambled latch); every "
          "single (normal/trapped/ender/copper x4) is now converted face by face (front<-Java south flipV, back<-north flipV, top<-up flipV, ends rot180) "
          "and every double regenerated from the Patrix halves (normal, trapped, copper x4 — the copper doubles are new). Renames to Bedrock names: "
          "armor_stand, bell/bell, banner/banner_base + 42 banner patterns, endercrystal + beam. Java-named originals kept. Pair with BP-02 v1.3.182 + RP-02 v2.0.3.", ledger_old="1.3.133")
    stamp(SRC3, DST3, (1, 3, 58), "AbsolutRealism PBR RP v{v}",
          "E2 MOVES. Conduit (Bedrock keeps it in textures/blocks): conduit_base (the 6x6x6 unwrap cropped from Patrix's canvas), cage, closed/open eye, "
          "wind horizontal/vertical (static frames). Decorated pot: base, side, 23 pottery patterns. cauldron_water = RP-02's Vibrant Visuals water "
          "(strip + texture set + MER + normal) under Bedrock's cauldron name. Java-named originals kept.")
    jdump(added, ROOT / "_logs/e2_added.json")
    log(f"trees built: rp04-134 (+{len(added['RP-04'])} files), rp03-58 (+{len(added['RP-03'])} files); manifests stamped")

if __name__ == "__main__":
    main()
