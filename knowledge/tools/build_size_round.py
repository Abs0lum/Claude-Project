#!/usr/bin/env python3
"""build_size_round.py — the SIZE ROUND (D-C291/D-C292, his 19:52 law + 20:0x answers):
  * BP-02 v1.3.190 — the vanilla real animals at REAL-LIFE size, model AND hitbox ("Visual + hitbox"): Mojang's own behaviour
    entity file (bedrock-samples 1.26.50, 15-09-2026) copied BYTE FOR BYTE except every minecraft:scale value (x the size_law
    factor; babies and the salmon size variants x the same factor so their proportions hold) and, where the adult had no scale,
    one inserted "minecraft:scale" line. Parrot and bat wait for FA-1 (their models change there).
  * PW-StripMine BP v1.3.4 — the Naturalist creatures on the same real-life curve (x1.20 cap gone), sharks KEPT imposing (his
    "Sharks imposing, rest change to real").
  * RP-06 v1.4.19 — minecraft:warden drawn x1.20 (his "+20% and keep his hitbox original size"): Mojang's warden client entity
    copied with scripts.scale "1.2" (resource pack only, hitbox untouched).
Every edit is TEXT-LEVEL on the original file (comments, order and formatting preserved); the gate (verify_size_round.py)
proves the parsed difference is exactly the scale values.
Usage: build_size_round.py            -> _build/bp02-190, _build/stripmine-bp-134, _build/rp06-1419 + _docs/sizes/size_round_report.json"""
import json, re, shutil, sys, time
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML

ROOT = Path("/home/claude")
VAN_BP = ROOT / "_intake/bedrock-samples/behavior_pack/entities"
VAN_RP = ROOT / "_intake/bedrock-samples/resource_pack/entity"
PLAN = {r["id"]: r for r in json.load(open(ROOT / "_docs/sizes/size_law_plan.json"))}
DATE = "2026-09-29"

VANILLA_FILES = {"cow": "cow.json", "mooshroom": "mooshroom.json", "llama": "llama.json", "trader_llama": "trader_llama.json",
                 "horse": "horse.json", "mule": "mule.json", "skeleton_horse": "skeleton_horse.json", "zombie_horse": "zombie_horse.json",
                 "camel": "camel.json", "dolphin": "dolphin.json", "goat": "goat.json", "panda": "panda.json", "polar_bear": "polar_bear.json",
                 "turtle": "turtle.json", "salmon": "salmon.json", "cod": "fish.json", "tropicalfish": "tropicalfish.json", "armadillo": "armadillo.json"}
DEFER = {"minecraft:parrot", "minecraft:bat"}                        # FA-1 decides their size with the new models
KEEP_IMPOSING = {"sf_nba:great_white_shark", "sf_nba:hammer_head_shark"}   # his answer
WARDEN_SCALE = 1.2
SCALE_RE = re.compile(r'("minecraft:scale"\s*:\s*\{\s*"value"\s*:\s*)(-?[\d.]+)')


def fmt(x):
    s = f"{x:.3f}".rstrip("0").rstrip(".")
    return s if s else "0"


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT {time.strftime('%m-%d')}] BUILD size-round: {m}\n")


def rescale_text(raw, factor):
    """x factor on every minecraft:scale value; if the entity's base components carry none, insert one (value = factor)."""
    ent = ML._parse_json(raw)["minecraft:entity"]
    has_base = "minecraft:scale" in (ent.get("components") or {})
    n = [0]
    def sub(m):
        n[0] += 1; return m.group(1) + fmt(float(m.group(2)) * factor)
    out = SCALE_RE.sub(sub, raw)
    inserted = False
    if not has_base:
        ms = list(re.finditer(r'^([ \t]*)"components"\s*:\s*\{[ \t]*\r?\n', out, re.M))
        assert len(ms) == 1, f"'components' key found {len(ms)} times"
        m = ms[0]
        nxt = re.match(r"[ \t]*", out[m.end():]).group(0)
        nl = "\r\n" if out[m.end() - 2:m.end()] == "\r\n" else "\n"
        line = f'{nxt}"minecraft:scale": {{ "value": {fmt(factor)} }},{nl}'
        out = out[:m.end()] + line + out[m.end():]; inserted = True
    return out, n[0], inserted


def build_bp02():
    src, dst = ROOT / "_build/bp02-189", ROOT / "_build/bp02-190"
    if dst.exists(): shutil.rmtree(dst)
    shutil.copytree(src, dst)
    rows = []
    for name, fn in VANILLA_FILES.items():
        ident = f"minecraft:{name}"; pl = PLAN[ident]
        assert not pl["action"].startswith("keep"), (ident, pl["action"])
        raw = (VAN_BP / fn).read_text(encoding="utf-8")
        assert ML._parse_json(raw)["minecraft:entity"]["description"]["identifier"] == ident
        assert not (dst / "entities" / fn).exists(), f"BP-02 already has entities/{fn}"
        out, n, ins = rescale_text(raw, pl["factor"])
        (dst / "entities" / fn).write_text(out, encoding="utf-8")
        rows.append({"id": ident, "file": f"entities/{fn}", "factor": pl["factor"], "scales_changed": n, "base_inserted": ins,
                     "from_blocks": pl["current"], "to_blocks": pl["target"]})
    mp = dst / "manifest.json"; m = json.loads(mp.read_text(encoding="utf-8-sig")); v = [1, 3, 190]
    m["header"]["version"] = v; m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.190"
    for mod in m["modules"]: mod["version"] = v
    m["header"]["description"] = (f"v1.3.190 ({DATE}) REAL-LIFE SIZES (D-C292, his size law): 18 vanilla animals drawn AND collided at their "
        "real-world size (1 m = 1.05 blocks on his 5'10\" character) - cow/mooshroom x1.28, llama x1.21, horses x1.10-1.21, camel x1.15, dolphin x1.11; "
        "goat x0.70, panda x0.68, turtle x0.63, salmon x0.52, armadillo x0.60, polar bear x0.88, cod x0.91, tropical fish x0.77. Each file = Mojang's "
        "1.26.50 behaviour file with only its scale values changed (babies and salmon sizes keep their proportions). Everything else byte-identical to v1.3.189.")
    mp.write_text(json.dumps(m, indent=1), encoding="utf-8")
    log(f"bp02-190: {len(rows)} vanilla behaviour entities at real size; manifest 1.3.190")
    return rows


def build_stripmine():
    src, dst = ROOT / "_build/stripmine-bp-133", ROOT / "_build/stripmine-bp-134"
    if dst.exists(): shutil.rmtree(dst)
    shutil.copytree(src, dst)
    targets = {i: r for i, r in PLAN.items() if i.startswith("sf_nba:") and not r["action"].startswith("keep") and i not in KEEP_IMPOSING}
    rows, found = [], set()
    for p in sorted((dst / "entities").rglob("*.json")):
        raw = p.read_text(encoding="utf-8-sig")
        m = re.search(r'"identifier"\s*:\s*"(sf_nba:[a-z_]+)"', raw)
        if not m or m.group(1) not in targets: continue
        ident = m.group(1); pl = targets[ident]
        try: ML._parse_json(raw)["minecraft:entity"]
        except Exception as e: rows.append({"id": ident, "file": str(p.relative_to(dst)), "skipped": f"unparseable: {str(e)[:60]}"}); continue
        out, n, ins = rescale_text(raw, pl["factor"])
        p.write_text(out, encoding="utf-8"); found.add(ident)
        rows.append({"id": ident, "file": str(p.relative_to(dst)), "factor": pl["factor"], "scales_changed": n, "base_inserted": ins,
                     "from_blocks": pl["current"], "to_blocks": pl["target"]})
    missing = sorted(set(targets) - found)
    mp = dst / "manifest.json"; mf = json.loads(mp.read_text(encoding="utf-8-sig")); v = [1, 3, 4]
    mf["header"]["version"] = v; mf["header"]["name"] = "PW StripMine BP v1.3.4"
    for mod in mf["modules"]: mod["version"] = v
    mf["header"]["description"] = (f"v1.3.4 ({DATE}) REAL-LIFE SIZES (D-C292, his size law): {len(found)} sf_nba creatures moved onto the one "
        "real-life curve (1 m = 1.05 blocks on his 5'10\" character; a log ramp keeps the tiny visible; the x1.20 growth cap is gone) - "
        "whale 15.8 blocks, elephant x1.19, grizzly x1.24, boar x1.67, tortoise x1.48; scorpions, morays, eel, snakes shrink to true size; "
        "sharks keep their imposing size (his ruling). Realm-only pack. Everything else byte-identical to v1.3.3.")
    mp.write_text(json.dumps(mf, indent=1), encoding="utf-8")
    log(f"stripmine-bp-134: {len(found)} creatures rescaled; not found in the pack: {missing}")
    return rows, missing


def build_rp06():
    src, dst = ROOT / "_build/rp06-1418", ROOT / "_build/rp06-1419"
    if dst.exists(): shutil.rmtree(dst)
    shutil.copytree(src, dst)
    assert not (dst / "entity/warden.entity.json").exists()
    raw = (VAN_RP / "warden.entity.json").read_text(encoding="utf-8")
    d = ML._parse_json(raw)["minecraft:client_entity"]["description"]
    assert d["identifier"] == "minecraft:warden"
    sc = (d.get("scripts") or {}).get("scale")
    if sc is None:
        ms = list(re.finditer(r'^([ \t]*)"scripts"\s*:\s*\{[ \t]*\r?\n', raw, re.M))
        if ms:
            m = ms[0]; nxt = re.match(r"[ \t]*", raw[m.end():]).group(0)
            out = raw[:m.end()] + f'{nxt}"scale": "{fmt(WARDEN_SCALE)}",\n' + raw[m.end():]
        else:
            ms = list(re.finditer(r'^([ \t]*)"identifier"\s*:\s*"minecraft:warden"\s*,[ \t]*\r?\n', raw, re.M)); assert len(ms) == 1
            m = ms[0]; ind = m.group(1)
            out = raw[:m.end()] + f'{ind}"scripts": {{ "scale": "{fmt(WARDEN_SCALE)}" }},\n' + raw[m.end():]
    else:
        raise SystemExit(f"vanilla warden already has scripts.scale {sc!r} - multiply instead (not expected)")
    (dst / "entity/warden.entity.json").write_text(out, encoding="utf-8")
    mp = dst / "manifest.json"; mf = json.loads(mp.read_text(encoding="utf-8-sig")); v = [1, 4, 19]
    old_desc = mf["header"]["description"]
    mf["header"]["version"] = v
    for mod in mf["modules"]: mod["version"] = v
    mf["header"]["name"] = re.sub(r"v1\.4\.\d+", "v1.4.19", mf["header"]["name"])
    mf["header"]["description"] = (f"v1.4.19 ({DATE}) WARDEN x1.20 (D-C292, his 'scarier' ruling): Mojang's warden client entity with "
        "scripts.scale 1.2 - drawn 20 % bigger, hitbox unchanged. Everything else byte-identical to v1.4.18.")
    mp.write_text(json.dumps(mf, indent=1), encoding="utf-8")
    log("rp06-1419: minecraft:warden client entity (Mojang 1.26.50 copy) scripts.scale 1.2; manifest 1.4.19")
    return {"file": "entity/warden.entity.json", "scale": WARDEN_SCALE, "old_desc": old_desc[:80]}


if __name__ == "__main__":
    rep = {"bp02": build_bp02()}
    rep["stripmine"], rep["stripmine_missing"] = build_stripmine()
    rep["rp06"] = build_rp06()
    json.dump(rep, open(ROOT / "_docs/sizes/size_round_report.json", "w"), indent=1)
    print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in rep.items()}, indent=1))
