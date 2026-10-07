#!/usr/bin/env python3
"""build_size_round2.py — SIZE ROUND 2 (FA-1; D-C298 his "Big adult male (top of range)" for predators + D-C294 parrot per colour
and bat at real size). Text-level edits on the shipped files, exactly like size round 1 (verify_size_round2.py proves the parsed
difference is the scale values only):
  * BP-02 v1.3.192 from v1.3.191:
      - polar bear x (target(2.5 m hb) / 2.215) on BP-02's own polar_bear.json (round 1 already scaled it);
      - NEW Mojang copies with one inserted base scale: fox, ocelot, dolphin is round-1 (x again), parrot (base = macaw size; the
        minecraft:parrot_silver group gets its own scale = the African grey), bat.
  * PW-StripMine BP v1.3.5 from v1.3.4: the Naturalist predators at the top of their sourced adult-male range (never below the
    shipped basis — his "predators come out large"); female-larger species at the top of the ADULT range.
Sources per figure: _docs/sizes/predator_male_sizes.json (subagent research, 33 species, URL + quote each).
Usage: build_size_round2.py -> _build/bp02-192, _build/stripmine-bp-135 + _docs/sizes/size_round2_report.json"""
import json, re, shutil, sys, time
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML
import size_law as S
import build_size_round as R1
import visible_size as V

ROOT = Path("/home/claude")
PLAN = {r["id"]: r for r in json.load(open(ROOT / "_docs/sizes/size_law_plan.json"))}
DATE = "2026-09-29"
# the new predator figures (metres, the SAME basis/mode as size_law.REAL) — top of the sourced adult-male range;
# `None` = keep the shipped basis (the male figure would shrink it, or no male range exists)
PREDATOR = {
    "polar_bear": (2.5, "males 2.0-2.5 m (DeMaster & Stirling 1981, via Wikipedia)"),
    "grizzly_bear": (2.4, "total 1.98-2.40 m (Mammals of Texas; sexes pooled, top)"),
    "black_bear": (1.83, "adult males 5-6 ft nose to tail (Maine IFW)"),
    "lion": (3.02, "males HB 1.84-2.08 + tail 0.825-0.935 m (West & Packer 2013)"),
    "male_lion": (3.02, "males HB 1.84-2.08 + tail 0.825-0.935 m (West & Packer 2013)"),
    "tiger": (None, "male Bengal 2.83-3.11 m < shipped 3.3 m"),
    "hyena": (1.735, "southern males to 1.735 m (Mammalian Species 2021); females larger"),
    "ravenous_hyena": (1.735, "= hyena"),
    "coyote": (1.35, "species 1.0-1.35 m, male mean 1.22 (Montana Field Guide)"),
    "fox": (0.72, "UK adult males HB 0.67-0.72 m (Wildlife Online)"),
    "fennec_fox": (None, "males 0.62-0.645 m < shipped 0.65 m"),
    "ocelot": (1.0, "HB 0.55-1.00 m (Mammals of Texas: male mean 0.745)"),
    "badger": (1.10, "HB 0.56-0.90 + tail 0.115-0.202 m, sexes alike (ADW)"),
    "otter": (1.40, "mature males 30-40 in + 12-15 in tail (PA Game Commission)"),
    "seal": (1.90, "adult males 1.60-1.90 m (ADW)"),
    "walrus": (3.6, "Pacific males 2.7-3.6 m (SeaWorld)"),
    "orca": (8.0, "males 6-8 m (Wikipedia)"),
    "dolphin": (3.81, "adult males 2.44-3.81 m (ADW)"),
    "alligator": (4.8, "adult males 3.4-4.8 m (Wikipedia; Smithsonian male mean 3.4)"),
    "komodo_dragon": (3.0, "male mean 2.59 m, to ~3 m (Guinness via Wikipedia)"),
    "rattlesnake": (1.5, "adults ~1.2 m, >1.5 infrequent, males larger (Wikipedia)"),
    "snake": (2.07, "adult males SVL 0.91-1.71 m + 17.5 % tail (Virginia Herpetological Society)"),
    "coral_snake": (None, "females larger; male ~0.62 m < shipped 0.8"),
    "moray": (None, "common length 1.5 m (FishBase), no male range"),
    "spotted_moray": (None, "common length 0.6 m (FishBase) < shipped 1.0"),
    "electric_eel": (None, "species max ~2.0 m = shipped"),
    "piranha": (0.41, "commonly 12 in, reported to 16 in (CDFW)"),
    "catfish": (0.81, "adults commonly 12-32 in (Missouri DoC)"),
    "bass": (0.56, "typically 0.30-0.40 m, females to 0.56 m (ADW)"),
    "giant_salamander": (None, "mean 1.0-1.3 m < shipped 1.5"),
    "octopus": (None, "no arm-span source; shipped 1.5 kept"),
    "eagle": (1.02, "adults 0.70-1.02 m, females larger (Wikipedia/ADW)"),
    "owl": (0.64, "adults 0.43-0.64 m, females larger (Wikipedia)"),
    "secretary_bird": (None, "to ~1.3 m = shipped"),
}
KEEP_TOL = 0.03          # a change under 3 % is not worth a file edit
PARROT_M, GREY_M, BAT_M = 0.84, 0.33, 0.28
BAT_BLOCKS = 0.42   # D-C303 his ruling "Go in between - 0.42": between true-to-life (0.28 m -> 0.29 block) and the small-animal curve (0.56)


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT {time.strftime('%m-%d')}] BUILD size-round-2: {m}\n")


def rows():
    out = []
    for key, (m, why) in PREDATOR.items():
        for ident, r in PLAN.items():
            if ident.split(":")[1] != key: continue
            base = r["current"] if r["action"].startswith("keep") else r["target"]      # what the shipped file draws today
            if m is None: out.append({"id": ident, "key": key, "action": "keep", "why": why, "blocks": base}); continue
            new_m = max(m, r["real_m"]); tgt = S.target(new_m); f = tgt / base
            # his ruling "predators come out LARGE": never smaller than what the shipped file draws today (hyena: kept at 1.89)
            act = "keep" if (f < 1 + KEEP_TOL) else "grow"
            if act == "keep": why = why + f"; shipped draws {base:.2f} blocks >= {tgt:.2f}"
            out.append({"id": ident, "key": key, "real_m_old": r["real_m"], "real_m": new_m, "mode": r["mode"], "why": why, "from_blocks": round(base, 3),
                        "to_blocks": round(tgt, 3), "factor": round(f, 4), "action": act, "file_had_round1": not r["action"].startswith("keep")})
    return out


def measure_new(stem, exclude=None, texture_key=None):
    m = V.measure(ROOT / "_build/rp07-1426", stem, [ROOT / "_build/rp06-1420"], exclude=exclude, texture_key=texture_key, everyday=True)
    return m


def insert_group_scale(raw, group, value):
    """insert "minecraft:scale": {"value": x} as the first line of component group `group` (text level)"""
    ms = list(re.finditer(r'^([ \t]*)"' + re.escape(group) + r'"\s*:\s*\{[ \t]*\r?\n', raw, re.M))
    assert len(ms) == 1, (group, len(ms))
    m = ms[0]; nxt = re.match(r"[ \t]*", raw[m.end():]).group(0)
    nl = "\r\n" if raw[m.end() - 2:m.end()] == "\r\n" else "\n"
    return raw[:m.end()] + f'{nxt}"minecraft:scale": {{ "value": {R1.fmt(value)} }},{nl}' + raw[m.end():]


def build_bp02(rs):
    src, dst = ROOT / "_build/bp02-191", ROOT / "_build/bp02-192"
    if dst.exists(): shutil.rmtree(dst)
    shutil.copytree(src, dst)
    done = []
    for r in rs:
        if not r["id"].startswith("minecraft:") or r["action"] == "keep": continue
        fn = {"minecraft:polar_bear": "polar_bear.json", "minecraft:dolphin": "dolphin.json", "minecraft:fox": "fox.json", "minecraft:ocelot": "ocelot.json"}[r["id"]]
        p = dst / "entities" / fn
        raw = p.read_text(encoding="utf-8") if p.exists() else (R1.VAN_BP / fn).read_text(encoding="utf-8")
        assert r["file_had_round1"] == p.exists(), (r["id"], "round-1 file state disagrees with the plan")
        out, n, ins = R1.rescale_text(raw, r["factor"])
        p.write_text(out, encoding="utf-8"); done.append({**r, "file": f"entities/{fn}", "scales_changed": n, "base_inserted": ins, "new_file": not r["file_had_round1"]})
    # parrot (per colour) + bat: sizes measured on the NEW RP-07 1.4.26 models (visible texels; the parrot's hidden flight wings /
    # dance legs left out)
    pm = measure_new("parrot", exclude=r"wing_fly|^left_leg$|^right_leg$|^left_foot$|^right_foot$", texture_key="red_blue")
    gm = measure_new("parrot", exclude=r"wing_fly|^left_leg$|^right_leg$|^left_foot$|^right_foot$", texture_key="grey")
    bm = measure_new("bat")
    s_mac = S.target(PARROT_M) / pm["max"]; s_grey = S.target(GREY_M) / gm["max"]; s_bat = BAT_BLOCKS / bm["max"]
    raw = (R1.VAN_BP / "parrot.json").read_text(encoding="utf-8")
    out, n, ins = R1.rescale_text(raw, s_mac); assert n == 0 and ins, (n, ins)
    out = insert_group_scale(out, "minecraft:parrot_silver", s_grey)
    (dst / "entities/parrot.json").write_text(out, encoding="utf-8")
    done.append({"id": "minecraft:parrot", "file": "entities/parrot.json", "new_file": True, "measured_max": pm["max"], "grey_measured_max": gm["max"],
                 "factor": round(s_mac, 4), "grey_factor": round(s_grey, 4), "to_blocks": S.target(PARROT_M), "grey_to_blocks": S.target(GREY_M),
                 "why": "macaw 0.84 m bill to tail (4 colours); African grey 0.33 m (minecraft:parrot_silver group)"})
    raw = (R1.VAN_BP / "bat.json").read_text(encoding="utf-8")
    out, n, ins = R1.rescale_text(raw, s_bat)
    (dst / "entities/bat.json").write_text(out, encoding="utf-8")
    done.append({"id": "minecraft:bat", "file": "entities/bat.json", "new_file": True, "measured_max": bm["max"], "factor": round(s_bat, 4),
                 "to_blocks": BAT_BLOCKS, "scales_changed": n, "base_inserted": ins, "why": "cave bat wingspan 0.28 m; 0.42 block by his ruling (D-C303)"})
    mp = dst / "manifest.json"; m = json.loads(mp.read_text(encoding="utf-8-sig")); v = [1, 3, 192]
    m["header"]["version"] = v; m["header"]["name"] = "AbsolutRealism Tectonic BP v1.3.192"
    for mod in m["modules"]: mod["version"] = v
    m["header"]["description"] = (f"v1.3.192 ({DATE}) SIZE ROUND 2 (FA-1): predators at the top of their adult-male range (his ruling) - "
        "polar bear 2.5 m, fox, ocelot, dolphin 3.8 m; the parrot per colour (macaws 0.84 m; the grey parrot 0.33 m, on the size law's "
        "small-animal curve: under 60 cm a little bigger than life so it stays visible) and the bat at 0.42 block wingspan (your pick, between "
        "life-size 0.29 and the curve's 0.56), model AND hitbox. Each file = Mojang's 1.26.50 behaviour file with only its scale values changed. "
        "Everything else byte-identical to v1.3.191.")
    mp.write_text(json.dumps(m, indent=1), encoding="utf-8")
    log(f"bp02-192: {len(done)} behaviour entities resized; manifest 1.3.192")
    return done


def build_stripmine(rs):
    src, dst = ROOT / "_build/stripmine-bp-134", ROOT / "_build/stripmine-bp-135"
    if dst.exists(): shutil.rmtree(dst)
    shutil.copytree(src, dst)
    targets = {r["id"]: r for r in rs if r["id"].startswith("sf_nba:") and r["action"] != "keep"}
    done, found = [], set()
    for p in sorted((dst / "entities").rglob("*.json")):
        raw = p.read_text(encoding="utf-8-sig")
        m = re.search(r'"identifier"\s*:\s*"(sf_nba:[a-z_]+)"', raw)
        if not m or m.group(1) not in targets: continue
        r = targets[m.group(1)]
        out, n, ins = R1.rescale_text(raw, r["factor"])
        p.write_text(out, encoding="utf-8"); found.add(r["id"])
        done.append({**r, "file": str(p.relative_to(dst)), "scales_changed": n, "base_inserted": ins})
    missing = sorted(set(targets) - found)
    mp = dst / "manifest.json"; mf = json.loads(mp.read_text(encoding="utf-8-sig")); v = [1, 3, 5]
    mf["header"]["version"] = v; mf["header"]["name"] = "PW StripMine BP v1.3.5"
    for mod in mf["modules"]: mod["version"] = v
    mf["header"]["description"] = (f"v1.3.5 ({DATE}) SIZE ROUND 2 (FA-1): {len(found)} Naturalist predators at the top of their sourced "
        "adult-male range (his ruling: predators come out large; never below v1.3.4) - grizzly 2.4 m, black bear, lions 3.0 m, alligator "
        "4.8 m, orca 8 m, walrus 3.6 m, snakes, badger, otter, eagle, owl ... Realm-only pack. Everything else byte-identical to v1.3.4.")
    mp.write_text(json.dumps(mf, indent=1), encoding="utf-8")
    log(f"stripmine-bp-135: {len(found)} predators rescaled; not found in the pack: {missing}")
    return done, missing


if __name__ == "__main__":
    rs = rows()
    rep = {"rows": rs, "bp02": build_bp02(rs)}
    rep["stripmine"], rep["stripmine_missing"] = build_stripmine(rs)
    json.dump(rep, open(ROOT / "_docs/sizes/size_round2_report.json", "w"), indent=1)
    for r in rs: print(f"{r['id']:26s} {r['action']:6s} " + (f"{r.get('from_blocks')} -> {r.get('to_blocks')} x{r.get('factor')}" if r["action"] != "keep" else r["why"]))
    for d in rep["bp02"]: print("BP-02", d["id"], d.get("factor"), d.get("grey_factor", ""))
